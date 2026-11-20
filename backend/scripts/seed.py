"""Ejecuta seed.sql (datos de prueba) contra la BD que tenga configurada la app.

Uso (desde la raíz del repo):

    npm run seed              # si la BD está vacía
    npm run seed -- --reset   # borra los datos (TRUNCATE) y vuelve a sembrar

Funciona igual contra Neon (BD compartida) o contra la Postgres local: usa la
misma resolución de URL que el backend (app.core.config). Al terminar comprueba
los recuentos de las 14 tablas y el saldo de Lucía (Comida=70, Transporte=10).

El bloque de reset vive DENTRO de seed.sql entre los marcadores
SEED_RESET_BEGIN / SEED_RESET_END (comentado). El runner lo extrae de ahí:
sin --reset NUNCA se ejecuta (aunque lo descomentes a mano en el archivo);
con --reset se descomenta y se ejecuta antes de sembrar.
"""

from __future__ import annotations

import argparse
import sys
from decimal import Decimal
from pathlib import Path

# backend/ en el sys.path para poder importar "app.*" (igual que alembic/env.py)
BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

import psycopg  # noqa: E402

from app.core.config import settings  # noqa: E402

SEED_FILE = BACKEND_ROOT / "seed.sql"
RESET_BEGIN = "-- SEED_RESET_BEGIN"
RESET_END = "-- SEED_RESET_END"

# Recuentos esperados tras sembrar (14 tablas)
EXPECTED_COUNTS: dict[str, int] = {
    "departments": 3,
    "users": 7,
    "benefits": 4,
    "packages": 5,
    "package_benefits": 6,
    "global_budgets": 1,
    "department_budgets": 3,
    "department_assignments": 6,
    "employee_assignments": 10,
    "expenses": 6,
    "expense_allocations": 6,
    "attachments": 6,
    "expense_history": 4,
    "audit_logs": 4,
}

# Consulta B del seed: saldo por beneficio de Lucía
LUCIA_SQL = """
WITH restante_paquete AS (
    SELECT ea.id, ea.user_id, ea.package_id,
           ea.assigned_amount - COALESCE(SUM(al.amount)
               FILTER (WHERE e.status IN ('APPROVED', 'PENDING')), 0) AS restante
    FROM employee_assignments ea
    LEFT JOIN expense_allocations al ON al.employee_assignment_id = ea.id
    LEFT JOIN expenses e             ON e.id = al.expense_id
    WHERE ea.is_active
    GROUP BY ea.id
)
SELECT b.name AS beneficio, SUM(rp.restante) AS saldo
FROM restante_paquete rp
JOIN package_benefits pb ON pb.package_id = rp.package_id
JOIN benefits b          ON b.id = pb.benefit_id
WHERE rp.user_id = (SELECT id FROM users WHERE email = 'lucia.garcia@pluxee.test')
GROUP BY b.name
ORDER BY b.name
"""

EXPECTED_LUCIA = {"Comida": Decimal("70"), "Transporte": Decimal("10")}


def split_seed(sql_text: str) -> tuple[str, str]:
    """Divide seed.sql en (bloque_reset_descomentado, script_principal)."""
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
            # El bloque va comentado: quitamos el prefijo "-- " para poder
            # ejecutarlo; ignoramos líneas en blanco.
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
    """Conexión autocommit con la URL que usa la app (pooled de Neon o local)."""
    url = settings.app_database_url.render_as_string(hide_password=False)
    url = url.replace("postgresql+psycopg://", "postgresql://", 1)
    return psycopg.connect(url, autocommit=True)


def check_counts(conn: psycopg.Connection) -> bool:
    """Comprueba que cada tabla tiene las filas esperadas."""
    print("\n[2/3] Recuentos de las 14 tablas")
    print(f"      {'tabla':<24}{'real':>6}{'esperado':>10}   ok")
    all_ok = True
    for table, expected in EXPECTED_COUNTS.items():
        real = conn.execute(f"SELECT count(*) FROM {table}").fetchone()[0]
        ok = real == expected
        all_ok = all_ok and ok
        print(f"      {table:<24}{real:>6}{expected:>10}   {'si' if ok else 'NO'}")
    return all_ok


def check_lucia(conn: psycopg.Connection) -> bool:
    """Comprueba el saldo de Lucía (ejemplo de Pablo: 70 / 10)."""
    print("\n[3/3] Saldo de Lucía (consulta B)")
    real = {row[0]: Decimal(str(row[1])) for row in conn.execute(LUCIA_SQL)}
    all_ok = True
    for benefit, expected in EXPECTED_LUCIA.items():
        got = real.get(benefit)
        ok = got is not None and got == expected
        all_ok = all_ok and ok
        got_str = f"{got:.2f}" if got is not None else "ausente"
        print(
            f"      {benefit:<14}real={got_str:>8}  "
            f"esperado={expected:.2f}   {'si' if ok else 'NO'}"
        )
    extra = set(real) - set(EXPECTED_LUCIA)
    if extra:
        print(f"      beneficios inesperados: {sorted(extra)}")
        all_ok = False
    return all_ok


def main() -> int:
    parser = argparse.ArgumentParser(description="Siembra seed.sql (datos de prueba)")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="TRUNCATE de las 14 tablas antes de sembrar (volver a empezar)",
    )
    args = parser.parse_args()

    sql_text = SEED_FILE.read_text(encoding="utf-8")
    reset_sql, main_sql = split_seed(sql_text)

    url = settings.app_database_url
    modo = "reset + inserción" if args.reset else "inserción"
    print("Seed · datos de prueba de Pluxee")
    print(f"Destino: {url.host}/{url.database}  ·  modo: {modo}")

    try:
        with connect() as conn:
            # [1/3] reset opcional + seed
            print("\n[1/3] Ejecutando seed.sql")
            if args.reset:
                if not reset_sql.strip():
                    raise SystemExit("seed.sql: bloque de reset vacío")
                conn.execute(reset_sql)
                print("      reset: TRUNCATE de las 14 tablas + RESTART IDENTITY")
            try:
                conn.execute(main_sql)
            except psycopg.errors.UniqueViolation as exc:
                detail = str(exc).splitlines()[0]
                print(f"      ERROR de clave duplicada: {detail}")
                print(
                    "      La BD ya tiene datos. Vuelve a empezar con:\n"
                    "        npm run seed -- --reset"
                )
                return 1
            print("      OK: INSERTs + setval de contadores + consultas A y B")

            counts_ok = check_counts(conn)
            lucia_ok = check_lucia(conn)
    except psycopg.Error as exc:
        detail = str(exc).splitlines()[0]
        print(f"\nERROR de PostgreSQL: {detail}")
        return 1

    ok = counts_ok and lucia_ok
    print(f"\nSEED RESULT: {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
