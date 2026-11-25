"""Tests del saldo del empleado (HU-13 / PEB-55)."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete, func, select

from app.core.database import SessionLocal
from app.core.security import create_access_token, hash_password
from app.main import app
from app.models import (
    Benefit,
    Department,
    DepartmentBudget,
    EmployeeAssignment,
    Expense,
    ExpenseAllocation,
    GlobalBudget,
    Package,
    PackageBenefit,
    User,
)

client = TestClient(app)
pytestmark = pytest.mark.usefixtures("real_auth")

TEST_NAME_PREFIX = "Test Balance HU13"
TEST_PERIOD = date.today().replace(day=1)


def _delete_test_data() -> None:
    """Borra solo lo que crea este módulo, respetando el orden de las FKs.

    No toca `global_budgets` ni el resto del seed: reutiliza el del mes en
    curso y solo borra el `department_budget` de los departamentos de test.
    """
    with SessionLocal() as db:
        test_deps = select(Department.id).where(
            func.lower(Department.name).startswith(TEST_NAME_PREFIX.lower())
        )
        test_users = select(User.id).where(
            func.lower(User.email).startswith("test-balance-hu13")
        )
        test_pkgs = select(Package.id).where(
            func.lower(Package.name).startswith(TEST_NAME_PREFIX.lower())
        )
        test_benefits = select(Benefit.id).where(
            func.lower(Benefit.name).startswith(TEST_NAME_PREFIX.lower())
        )

        db.execute(
            delete(ExpenseAllocation).where(
                ExpenseAllocation.expense_id.in_(
                    select(Expense.id).where(Expense.user_id.in_(test_users))
                )
            )
        )
        db.execute(delete(Expense).where(Expense.user_id.in_(test_users)))
        db.execute(
            delete(EmployeeAssignment).where(
                EmployeeAssignment.user_id.in_(test_users)
            )
        )
        db.execute(
            delete(DepartmentBudget).where(
                DepartmentBudget.department_id.in_(test_deps)
            )
        )
        db.execute(
            delete(PackageBenefit).where(PackageBenefit.package_id.in_(test_pkgs))
        )
        db.execute(delete(Package).where(Package.id.in_(test_pkgs)))
        db.execute(delete(Benefit).where(Benefit.id.in_(test_benefits)))
        db.execute(delete(User).where(User.id.in_(test_users)))
        db.execute(delete(Department).where(Department.id.in_(test_deps)))
        db.commit()


@pytest.fixture(autouse=True)
def clean_test_data():
    _delete_test_data()
    yield
    _delete_test_data()


def _auth_header(user_id: int) -> dict[str, str]:
    return {"Authorization": f"Bearer {create_access_token(user_id, 'EMPLOYEE')}"}


def _ensure_period(db) -> GlobalBudget:
    """Reutiliza el GlobalBudget del mes en curso; lo crea si no existe."""
    gb = db.scalar(select(GlobalBudget).where(GlobalBudget.period == TEST_PERIOD))
    if gb is None:
        gb = GlobalBudget(period=TEST_PERIOD, amount=Decimal("10000.00"))
        db.add(gb)
        db.flush()
    return gb


def _create_department(db, suffix: str) -> Department:
    dep = Department(name=f"{TEST_NAME_PREFIX} {suffix}")
    db.add(dep)
    db.flush()
    return dep


def _create_employee(db, dep: Department, suffix: str) -> User:
    user = User(
        full_name=f"{TEST_NAME_PREFIX} {suffix}",
        email=f"test-balance-hu13-{suffix.lower().replace(' ', '-')}@pluxee.test",
        password_hash=hash_password("Prueba123!"),
        role="EMPLOYEE",
        department_id=dep.id,
        must_change_password=False,
        is_active=True,
    )
    db.add(user)
    db.flush()
    return user


def _create_benefit(db, suffix: str) -> Benefit:
    benefit = Benefit(
        name=f"{TEST_NAME_PREFIX} {suffix}",
        description=suffix,
        is_basic=True,
        is_active=True,
    )
    db.add(benefit)
    db.flush()
    return benefit


def _create_package(db, dep: Department, suffix: str, amount: str) -> Package:
    pkg = Package(
        name=f"{TEST_NAME_PREFIX} {suffix}",
        default_amount=Decimal(amount),
        department_id=dep.id,
        is_active=True,
    )
    db.add(pkg)
    db.flush()
    return pkg


def _assign(db, user: User, package: Package, amount: str) -> EmployeeAssignment:
    assignment = EmployeeAssignment(
        package_id=package.id,
        user_id=user.id,
        assigned_amount=Decimal(amount),
        is_active=True,
    )
    db.add(assignment)
    db.flush()
    return assignment


def _expense(
    db,
    user: User,
    benefit: Benefit,
    assignment: EmployeeAssignment,
    amount: str,
    status: str,
    expense_date: date,
) -> None:
    rejection_reason = "Motivo de prueba" if status == "REJECTED" else None
    expense = Expense(
        user_id=user.id,
        benefit_id=benefit.id,
        amount=Decimal(amount),
        expense_date=expense_date,
        description="test",
        status=status,
        rejection_reason=rejection_reason,
    )
    db.add(expense)
    db.flush()
    db.add(
        ExpenseAllocation(
            expense_id=expense.id,
            employee_assignment_id=assignment.id,
            package_id=assignment.package_id,
            benefit_id=benefit.id,
            amount=Decimal(amount),
        )
    )


# ---------------------------------------------------------------------
# 1. Autenticación
# ---------------------------------------------------------------------
def test_balance_requires_auth() -> None:
    response = client.get("/api/balance/me")
    assert response.status_code == 401


# ---------------------------------------------------------------------
# 2. Sin GlobalBudget del mes: todo a 0, period null
# ---------------------------------------------------------------------
def test_balance_without_current_period_returns_empty() -> None:
    with SessionLocal() as db:
        # Nos aseguramos de que no hay GlobalBudget del mes en curso.
        existing = db.scalar(
            select(GlobalBudget).where(GlobalBudget.period == TEST_PERIOD)
        )
        if existing is not None:
            pytest.skip("El mes en curso tiene GlobalBudget (seed); no aplica")

        dep = _create_department(db, "SinMes")
        user = _create_employee(db, dep, "SinMes")
        db.commit()
        user_id = user.id

    response = client.get("/api/balance/me", headers=_auth_header(user_id))
    assert response.status_code == 200
    body = response.json()
    assert body["period"] is None
    assert body["assigned_total"] == "0.00"
    assert body["available_total"] == "0.00"
    assert body["by_benefit"] == []
    assert body["packages"] == []


# ---------------------------------------------------------------------
# 3. Multibeneficio compartido: el gasto reduce el disponible de todos
#    Ejemplo del cliente: 100 combo + 50 mono comida, 30 gastados en transporte
# ---------------------------------------------------------------------
def test_balance_shared_package_reduces_all_benefits() -> None:
    with SessionLocal() as db:
        dep = _create_department(db, "Compartido")
        user = _create_employee(db, dep, "Compartido")

        food = _create_benefit(db, "Comida compartida")
        transport = _create_benefit(db, "Transporte compartido")

        combo = _create_package(db, dep, "Combo compartido", "100.00")
        mono = _create_package(db, dep, "Mono comida compartido", "50.00")
        db.add_all(
            [
                PackageBenefit(package_id=combo.id, benefit_id=food.id),
                PackageBenefit(package_id=combo.id, benefit_id=transport.id),
                PackageBenefit(package_id=mono.id, benefit_id=food.id),
            ]
        )
        db.flush()

        gb = _ensure_period(db)
        db.add(
            DepartmentBudget(
                global_budget_id=gb.id,
                department_id=dep.id,
                amount=Decimal("3000.00"),
            )
        )
        db.flush()

        assign_combo = _assign(db, user, combo, "100.00")
        _assign(db, user, mono, "50.00")

        _expense(
            db, user, transport, assign_combo, "30.00", "APPROVED", TEST_PERIOD
        )
        db.commit()
        user_id = user.id

    response = client.get("/api/balance/me", headers=_auth_header(user_id))
    assert response.status_code == 200
    body = response.json()

    # Total asignado = 100 + 50 (suma de paquetes, no de beneficios)
    assert body["assigned_total"] == "150.00"
    assert body["consumed_total"] == "30.00"
    assert body["available_total"] == "120.00"

    by_benefit = {item["benefit_name"]: item for item in body["by_benefit"]}
    # Comida: (100 − 30) + (50 − 0) = 120
    assert by_benefit[f"{TEST_NAME_PREFIX} Comida compartida"]["available"] == "120.00"
    # Transporte: 100 − 30 = 70
    assert by_benefit[f"{TEST_NAME_PREFIX} Transporte compartido"]["available"] == "70.00"


# ---------------------------------------------------------------------
# 4. Gasto de un mes anterior no resta
# ---------------------------------------------------------------------
def test_balance_ignores_expenses_from_previous_month() -> None:
    with SessionLocal() as db:
        dep = _create_department(db, "MesAnterior")
        user = _create_employee(db, dep, "MesAnterior")
        food = _create_benefit(db, "Comida mes anterior")

        pkg = _create_package(db, dep, "Comida mes anterior", "80.00")
        db.add(PackageBenefit(package_id=pkg.id, benefit_id=food.id))
        db.flush()

        gb = _ensure_period(db)
        db.add(
            DepartmentBudget(
                global_budget_id=gb.id,
                department_id=dep.id,
                amount=Decimal("1000.00"),
            )
        )
        db.flush()

        assignment = _assign(db, user, pkg, "80.00")

        previous_month = (
            date(TEST_PERIOD.year - 1, 12, 15)
            if TEST_PERIOD.month == 1
            else date(TEST_PERIOD.year, TEST_PERIOD.month - 1, 15)
        )
        _expense(
            db, user, food, assignment, "40.00", "APPROVED", previous_month
        )
        db.commit()
        user_id = user.id

    response = client.get("/api/balance/me", headers=_auth_header(user_id))
    body = response.json()
    assert body["consumed_total"] == "0.00"
    assert body["available_total"] == "80.00"


# ---------------------------------------------------------------------
# 5. Gasto rechazado no resta
# ---------------------------------------------------------------------
def test_balance_ignores_rejected_expenses() -> None:
    with SessionLocal() as db:
        dep = _create_department(db, "Rechazado")
        user = _create_employee(db, dep, "Rechazado")
        food = _create_benefit(db, "Comida rechazada")

        pkg = _create_package(db, dep, "Comida rechazada", "50.00")
        db.add(PackageBenefit(package_id=pkg.id, benefit_id=food.id))
        db.flush()

        gb = _ensure_period(db)
        db.add(
            DepartmentBudget(
                global_budget_id=gb.id,
                department_id=dep.id,
                amount=Decimal("1000.00"),
            )
        )
        db.flush()

        assignment = _assign(db, user, pkg, "50.00")
        _expense(db, user, food, assignment, "20.00", "REJECTED", TEST_PERIOD)
        db.commit()
        user_id = user.id

    response = client.get("/api/balance/me", headers=_auth_header(user_id))
    body = response.json()
    assert body["consumed_total"] == "0.00"
    assert body["available_total"] == "50.00"


# ---------------------------------------------------------------------
# 6. Ejemplo del seed: Comida 70 € y Transporte 10 €
# ---------------------------------------------------------------------
def test_balance_seed_example() -> None:
    """100 combo + 60 mono, 90 gastados en transporte → Comida 70, Transporte 10."""
    with SessionLocal() as db:
        dep = _create_department(db, "Seed")
        user = _create_employee(db, dep, "Seed")
        food = _create_benefit(db, "Comida seed")
        transport = _create_benefit(db, "Transporte seed")

        combo = _create_package(db, dep, "Combo seed", "100.00")
        mono = _create_package(db, dep, "Mono comida seed", "60.00")
        db.add_all(
            [
                PackageBenefit(package_id=combo.id, benefit_id=food.id),
                PackageBenefit(package_id=combo.id, benefit_id=transport.id),
                PackageBenefit(package_id=mono.id, benefit_id=food.id),
            ]
        )
        db.flush()

        gb = _ensure_period(db)
        db.add(
            DepartmentBudget(
                global_budget_id=gb.id,
                department_id=dep.id,
                amount=Decimal("3000.00"),
            )
        )
        db.flush()

        assign_combo = _assign(db, user, combo, "100.00")
        _assign(db, user, mono, "60.00")

        _expense(
            db, user, transport, assign_combo, "90.00", "APPROVED", TEST_PERIOD
        )
        db.commit()
        user_id = user.id

    response = client.get("/api/balance/me", headers=_auth_header(user_id))
    assert response.status_code == 200
    body = response.json()

    assert body["assigned_total"] == "160.00"
    assert body["consumed_total"] == "90.00"
    assert body["available_total"] == "70.00"

    by_benefit = {item["benefit_name"]: item for item in body["by_benefit"]}
    assert by_benefit[f"{TEST_NAME_PREFIX} Comida seed"]["available"] == "70.00"
    assert by_benefit[f"{TEST_NAME_PREFIX} Transporte seed"]["available"] == "10.00"

# ---------------------------------------------------------------------
# 7. Gastos pendientes: descuentan saldo igual que los aprobados
#    Restante = Asignado - Aprobado - Pendiente
# ---------------------------------------------------------------------
def test_balance_pending_expenses_reduce_available() -> None:
    with SessionLocal() as db:
        dep = _create_department(db, "Pendiente")
        user = _create_employee(db, dep, "Pendiente")
        food = _create_benefit(db, "Comida pendiente")

        pkg = _create_package(db, dep, "Comida pendiente", "100.00")
        db.add(PackageBenefit(package_id=pkg.id, benefit_id=food.id))
        db.flush()

        gb = _ensure_period(db)
        db.add(
            DepartmentBudget(
                global_budget_id=gb.id,
                department_id=dep.id,
                amount=Decimal("1000.00"),
            )
        )
        db.flush()

        assignment = _assign(db, user, pkg, "100.00")
        _expense(db, user, food, assignment, "20.00", "APPROVED", TEST_PERIOD)
        _expense(db, user, food, assignment, "30.00", "PENDING", TEST_PERIOD)
        db.commit()
        user_id = user.id

    response = client.get("/api/balance/me", headers=_auth_header(user_id))
    assert response.status_code == 200
    body = response.json()

    # 100 - 20 aprobado - 30 pendiente = 50
    assert body["assigned_total"] == "100.00"
    assert body["approved_total"] == "20.00"
    assert body["pending_total"] == "30.00"
    assert body["consumed_total"] == "50.00"
    assert body["available_total"] == "50.00"

    package = body["packages"][0]
    assert package["approved"] == "20.00"
    assert package["pending"] == "30.00"
    assert package["available"] == "50.00"

    by_benefit = {item["benefit_name"]: item for item in body["by_benefit"]}
    assert by_benefit[f"{TEST_NAME_PREFIX} Comida pendiente"]["available"] == "50.00"


# ---------------------------------------------------------------------
# 8. Un gasto pendiente en un paquete multibeneficio reduce todos sus
#    beneficios (saldo compartido)
# ---------------------------------------------------------------------
def test_balance_pending_in_shared_package_reduces_all_benefits() -> None:
    with SessionLocal() as db:
        dep = _create_department(db, "PendienteCompartido")
        user = _create_employee(db, dep, "PendienteCompartido")
        food = _create_benefit(db, "Comida pendiente compartida")
        transport = _create_benefit(db, "Transporte pendiente compartido")

        combo = _create_package(db, dep, "Combo pendiente", "100.00")
        db.add_all(
            [
                PackageBenefit(package_id=combo.id, benefit_id=food.id),
                PackageBenefit(package_id=combo.id, benefit_id=transport.id),
            ]
        )
        db.flush()

        gb = _ensure_period(db)
        db.add(
            DepartmentBudget(
                global_budget_id=gb.id,
                department_id=dep.id,
                amount=Decimal("1000.00"),
            )
        )
        db.flush()

        assignment = _assign(db, user, combo, "100.00")
        _expense(
            db, user, transport, assignment, "40.00", "PENDING", TEST_PERIOD
        )
        db.commit()
        user_id = user.id

    response = client.get("/api/balance/me", headers=_auth_header(user_id))
    body = response.json()

    by_benefit = {item["benefit_name"]: item for item in body["by_benefit"]}
    assert by_benefit[f"{TEST_NAME_PREFIX} Comida pendiente compartida"]["available"] == "60.00"
    assert by_benefit[f"{TEST_NAME_PREFIX} Transporte pendiente compartido"]["available"] == "60.00"
    assert body["available_total"] == "60.00"


# ---------------------------------------------------------------------
# 9. Una asignación inactiva no cuenta en el saldo
# ---------------------------------------------------------------------
def test_balance_ignores_inactive_assignments() -> None:
    with SessionLocal() as db:
        dep = _create_department(db, "Inactiva")
        user = _create_employee(db, dep, "Inactiva")
        food = _create_benefit(db, "Comida inactiva")

        active_pkg = _create_package(db, dep, "Comida activa", "50.00")
        inactive_pkg = _create_package(db, dep, "Comida inactiva", "80.00")
        db.add_all(
            [
                PackageBenefit(package_id=active_pkg.id, benefit_id=food.id),
                PackageBenefit(package_id=inactive_pkg.id, benefit_id=food.id),
            ]
        )
        db.flush()

        gb = _ensure_period(db)
        db.add(
            DepartmentBudget(
                global_budget_id=gb.id,
                department_id=dep.id,
                amount=Decimal("1000.00"),
            )
        )
        db.flush()

        _assign(db, user, active_pkg, "50.00")
        inactive_assignment = _assign(db, user, inactive_pkg, "80.00")
        inactive_assignment.is_active = False
        db.commit()
        user_id = user.id

    response = client.get("/api/balance/me", headers=_auth_header(user_id))
    body = response.json()

    assert body["assigned_total"] == "50.00"
    assert body["available_total"] == "50.00"
    assert len(body["packages"]) == 1
    assert body["packages"][0]["package_name"] == f"{TEST_NAME_PREFIX} Comida activa"




# ---------------------------------------------------------------------
# 10. Un paquete no se muestra si su departamento no tiene presupuesto
#     en el mes (regla pendiente de confirmar con el PO; este test fija
#     el comportamiento actual)
# ---------------------------------------------------------------------
def test_balance_hides_packages_when_department_has_no_budget() -> None:
    with SessionLocal() as db:
        dep = _create_department(db, "SinPresupuesto")
        user = _create_employee(db, dep, "SinPresupuesto")
        food = _create_benefit(db, "Comida sin presupuesto")

        pkg = _create_package(db, dep, "Comida sin presupuesto", "60.00")
        db.add(PackageBenefit(package_id=pkg.id, benefit_id=food.id))
        db.flush()

        # Hay presupuesto global del mes, pero NO se crea el del departamento
        gb = _ensure_period(db)
        _assign(db, user, pkg, "60.00")
        db.commit()
        user_id = user.id
        department_id = dep.id
        global_budget_id = gb.id

    response = client.get("/api/balance/me", headers=_auth_header(user_id))
    assert response.status_code == 200
    body = response.json()
    assert body["period"] == TEST_PERIOD.isoformat()
    assert body["assigned_total"] == "0.00"
    assert body["available_total"] == "0.00"
    assert body["by_benefit"] == []
    assert body["packages"] == []

    # Al fijar el presupuesto del departamento, el paquete aparece
    with SessionLocal() as db:
        db.add(
            DepartmentBudget(
                global_budget_id=global_budget_id,
                department_id=department_id,
                amount=Decimal("1000.00"),
            )
        )
        db.commit()

    response = client.get("/api/balance/me", headers=_auth_header(user_id))
    body = response.json()
    assert body["assigned_total"] == "60.00"
    assert [p["package_name"] for p in body["packages"]] == [
        f"{TEST_NAME_PREFIX} Comida sin presupuesto"
    ]