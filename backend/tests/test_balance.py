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

# Solo los datos con este prefijo son datos de prueba:
# se borran antes y después de cada test para que las corridas sean repetibles.
TEST_NAME_PREFIX = "Test Balance HU13"
# Mes en curso: el mismo que usa el endpoint por defecto.
TEST_PERIOD = date.today().replace(day=1)


def _delete_test_data() -> None:
    """Borra los datos de prueba respetando el orden de las FKs.

    No toca `global_budgets` ni el resto de datos del seed: solo elimina
    lo que crea este módulo (departamento, usuario, paquetes, beneficios,
    asignaciones, gastos y el department_budget del departamento de test).
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
    """Limpia los datos de prueba antes y después de cada test."""
    _delete_test_data()
    yield
    _delete_test_data()


def _auth_header(user_id: int) -> dict[str, str]:
    return {"Authorization": f"Bearer {create_access_token(user_id, 'EMPLOYEE')}"}


# ---------------------------------------------------------------------
# 1. Autenticación
# ---------------------------------------------------------------------
def test_balance_requires_auth() -> None:
    response = client.get("/api/balance/me")

    assert response.status_code == 401


# ---------------------------------------------------------------------
# 2. Cálculo: Restante = Asignado − Aprobado − Pendiente
# ---------------------------------------------------------------------
def test_balance_returns_assigned_minus_approved_minus_pending() -> None:
    """160 € asignados, 90 € aprobados, 10 € pendientes → 60 € disponibles."""
    with SessionLocal() as db:
        dep = Department(name=f"{TEST_NAME_PREFIX} Ventas")
        db.add(dep)
        db.flush()

        user = User(
            full_name=f"{TEST_NAME_PREFIX} Lucía",
            email="test-balance-hu13-lucia@pluxee.test",
            password_hash=hash_password("Prueba123!"),
            role="EMPLOYEE",
            department_id=dep.id,
            must_change_password=False,
            is_active=True,
        )
        food = Benefit(
            name=f"{TEST_NAME_PREFIX} Comida",
            description="Comida",
            is_basic=True,
            is_active=True,
        )
        transport = Benefit(
            name=f"{TEST_NAME_PREFIX} Transporte",
            description="Transporte",
            is_basic=True,
            is_active=True,
        )
        db.add_all([user, food, transport])
        db.flush()

        pkg_combo = Package(
            name=f"{TEST_NAME_PREFIX} Comida y transporte",
            default_amount=Decimal("100.00"),
            department_id=dep.id,
            is_active=True,
        )
        pkg_food = Package(
            name=f"{TEST_NAME_PREFIX} Comida",
            default_amount=Decimal("60.00"),
            department_id=dep.id,
            is_active=True,
        )
        db.add_all([pkg_combo, pkg_food])
        db.flush()
        db.add_all(
            [
                PackageBenefit(package_id=pkg_combo.id, benefit_id=food.id),
                PackageBenefit(package_id=pkg_combo.id, benefit_id=transport.id),
                PackageBenefit(package_id=pkg_food.id, benefit_id=food.id),
            ]
        )
        db.flush()

        # Reutiliza el GlobalBudget del mes en curso (el del seed en noviembre);
        # solo lo crea si no existe.
        gb = db.scalar(
            select(GlobalBudget).where(GlobalBudget.period == TEST_PERIOD)
        )
        if gb is None:
            gb = GlobalBudget(period=TEST_PERIOD, amount=Decimal("10000.00"))
            db.add(gb)
            db.flush()

        db.add(
            DepartmentBudget(
                global_budget_id=gb.id, department_id=dep.id, amount=Decimal("3000.00")
            )
        )
        db.flush()

        assign_combo = EmployeeAssignment(
            package_id=pkg_combo.id,
            user_id=user.id,
            assigned_amount=Decimal("100.00"),
            is_active=True,
        )
        assign_food = EmployeeAssignment(
            package_id=pkg_food.id,
            user_id=user.id,
            assigned_amount=Decimal("60.00"),
            is_active=True,
        )
        db.add_all([assign_combo, assign_food])
        db.flush()

        for status, amount, assignment, benefit, description in (
            ("APPROVED", "90.00", assign_combo, transport, "Tren"),
            ("PENDING", "10.00", assign_food, food, "Menú"),
        ):
            expense = Expense(
                user_id=user.id,
                benefit_id=benefit.id,
                amount=Decimal(amount),
                expense_date=TEST_PERIOD,
                description=description,
                status=status,
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

        db.commit()
        user_id = user.id

    response = client.get("/api/balance/me", headers=_auth_header(user_id))

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["period"] == TEST_PERIOD.isoformat()
    assert body["assigned_total"] == "160.00"
    assert body["approved_total"] == "90.00"
    assert body["pending_total"] == "10.00"
    assert body["consumed_total"] == "100.00"
    assert body["available_total"] == "60.00"

    by_benefit = {item["benefit_name"]: item for item in body["by_benefit"]}
    assert by_benefit[f"{TEST_NAME_PREFIX} Comida"]["available"] == "150.00"
    assert by_benefit[f"{TEST_NAME_PREFIX} Transporte"]["available"] == "10.00"