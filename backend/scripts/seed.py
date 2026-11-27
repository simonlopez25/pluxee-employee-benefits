from __future__ import annotations

import argparse
import sys
from decimal import Decimal
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

import psycopg  # noqa: E402

from app.core.config import settings  # noqa: E402

SEED_FILE = BACKEND_ROOT / "seed.sql"
RESET_BEGIN = "-- SEED_RESET_BEGIN"
RESET_END = "-- SEED_RESET_END"

EXPECTED_COUNTS: dict[str, int] = {
    "departments": 3,
    "users": 7,
    "benefits": 4,
    "packages": 6,
    "package_benefits": 8,
    "global_budgets": 1,
    "department_budgets": 3,
    "employee_assignments": 10,
    "expenses": 6,
    "expense_allocations": 6,
    "attachments": 6,
    "expense_history": 4,
    "audit_logs": 4,
    "benefit_budget_references": 0,
}

LUCIA_SQL = """
WITH restante_paquete AS (
    SELECT ea.id, ea.user_id, ea.package_id,
           ea.assigned_amount - COALESCE(SUM(al.amount)
              FILTER (WHERE e.status IN ('APPROVED', 'PENDING')), 0) AS remaining
    FROM employee_assignments ea
    LEFT JOIN expense_allocations al ON al.employee_assignment_id = ea.id
    LEFT JOIN expenses e             ON e.id = al.expense_id
    WHERE ea.is_active
    GROUP BY ea.id
)
SELECT b.name AS benefit, SUM(rp.remaining) AS balance
FROM restante_paquete rp
JOIN package_benefits pb ON pb.package_id = rp.package_id
JOIN benefits b          ON b.id = pb.benefit_id
WHERE rp.user_id = (SELECT id FROM users WHERE email = 'lucia.garcia@pluxee.test')
GROUP BY b.name
ORDER BY b.name
"""

EXPECTED_LUCIA = {"Meal": Decimal("70"), "Transport": Decimal("10")}


def split_seed(sql_text: str) -> tuple[str, str]:
    reset_lines: list[str] = []
    main_lines: list[str] = []
    inside = False
    for line in sql_text.splitlines():
        stripped = line.strip()
        if stripped == RESET_BEGIN:
            inside = True
            continue
        if stripped == RESET_END:
            inside = False
            continue
        if inside:
            if line.startswith("-- "):
                reset_lines.append(line[3:])
            elif stripped:
                reset_lines.append(line)
        else:
            main_lines.append(line)
    if inside:
        raise SystemExit(f"seed.sql: falta el marcador {RESET_END}")
    return "\n".join(reset_lines), "\n".join(main_lines)


def connect() -> psycopg.Connection:
    url = settings.app_database_url.render_as_string(hide_password=False)
    url = url.replace("postgresql+psycopg://", "postgresql://", 1)
    return psycopg.connect(url, autocommit=True)


def check_counts(conn: psycopg.Connection) -> bool:
    print("\n[2/3] Table row counts (14 tables)")
    print(f"      {'table':<24}{'actual':>6}{'expected':>10}   ok")
    all_ok = True
    for table, expected in EXPECTED_COUNTS.items():
        real = conn.execute(f"SELECT count(*) FROM {table}").fetchone()[0]
        ok = real == expected
        all_ok = all_ok and ok
        print(f"      {table:<24}{real:>6}{expected:>10}   {'yes' if ok else 'NO'}")
    return all_ok


def check_lucia(conn: psycopg.Connection) -> bool:
    print("\n[3/3] Lucia's balance (query B)")
    real = {row[0]: Decimal(str(row[1])) for row in conn.execute(LUCIA_SQL)}
    all_ok = True
    for benefit, expected in EXPECTED_LUCIA.items():
        got = real.get(benefit)
        ok = got is not None and got == expected
        all_ok = all_ok and ok
        got_str = f"{got:.2f}" if got is not None else "missing"
        print(
            f"      {benefit:<14}actual={got_str:>8}  "
            f"expected={expected:.2f}   {'yes' if ok else 'NO'}"
        )
    extra = set(real) - set(EXPECTED_LUCIA)
    if extra:
        print(f"      unexpected benefits: {sorted(extra)}")
        all_ok = False
    return all_ok


def main() -> int:
    parser = argparse.ArgumentParser(description="Runs seed.sql (test data)")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="TRUNCATE 14 tables before seeding (start over)",
    )
    args = parser.parse_args()

    sql_text = SEED_FILE.read_text(encoding="utf-8")
    reset_sql, main_sql = split_seed(sql_text)

    url = settings.app_database_url
    mode = "reset + insert" if args.reset else "insert"
    print("Seed · Pluxee test data")
    print(f"Target: {url.host}/{url.database}  ·  mode: {mode}")

    try:
        with connect() as conn:
            print("\n[1/3] Running seed.sql")
            if args.reset:
                if not reset_sql.strip():
                    raise SystemExit("seed.sql: empty reset block")
                conn.execute(reset_sql)
                print("      reset: TRUNCATE 14 tables + RESTART IDENTITY")
            try:
                conn.execute(main_sql)
            except psycopg.errors.UniqueViolation as exc:
                detail = str(exc).splitlines()[0]
                print(f"      DUPLICATE KEY ERROR: {detail}")
                print(
                    "      Database already has data. Start over with:\n"
                    "        npm run seed -- --reset"
                )
                return 1
            print("      OK: INSERTs + setval counters + queries A and B")

            counts_ok = check_counts(conn)
            lucia_ok = check_lucia(conn)
    except psycopg.Error as exc:
        detail = str(exc).splitlines()[0]
        print(f"\nPOSTGRESQL ERROR: {detail}")
        return 1

    ok = counts_ok and lucia_ok
    print(f"\nSEED RESULT: {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
