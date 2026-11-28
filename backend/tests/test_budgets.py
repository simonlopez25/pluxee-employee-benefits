from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete, func, select

from app.core.database import SessionLocal
from app.main import app
from app.models import BenefitBudgetReference, DepartmentBudget, GlobalBudget

client = TestClient(app)

TEST_PERIODS = [
    date(2026, 12, 1),
    date(2027, 1, 1),
    date(2027, 2, 1),
    date(2027, 3, 1),
    date(2027, 4, 1),
    date(2027, 5, 1),
]

DEPT_VENTAS = 1
DEPT_INGENIERIA = 2
DEPT_MARKETING = 3


def _delete_test_budget_rows() -> None:
    with SessionLocal() as db:
        db.execute(
            delete(BenefitBudgetReference).where(
                BenefitBudgetReference.department_budget_id.in_(
                    select(DepartmentBudget.id).join(
                        GlobalBudget,
                        GlobalBudget.id == DepartmentBudget.global_budget_id,
                    ).where(GlobalBudget.period.in_(TEST_PERIODS))
                )
            )
        )
        db.execute(delete(DepartmentBudget).where(
            DepartmentBudget.global_budget_id.in_(
                select(GlobalBudget.id).where(GlobalBudget.period.in_(TEST_PERIODS))
            )
        ))
        db.execute(delete(GlobalBudget).where(GlobalBudget.period.in_(TEST_PERIODS)))
        db.commit()


@pytest.fixture(autouse=True)
def clean_test_budget_rows():
    _delete_test_budget_rows()
    yield
    _delete_test_budget_rows()


def _put_global(period: date, total_amount: str | float):
    return client.put(
        "/api/budgets/global",
        json={"period": period.isoformat(), "total_amount": str(total_amount)},
    )


def _put_department(department_id: int, period: date, allocated_amount: str | float):
    return client.put(
        f"/api/budgets/departments/{department_id}",
        json={"period": period.isoformat(), "allocated_amount": str(allocated_amount)},
    )


def _put_references(department_id: int, period: date, references: list[dict]):
    return client.put(
        f"/api/budgets/departments/{department_id}/references",
        json={"period": period.isoformat(), "references": references},
    )


def test_create_global_budget_normalizes_period_to_first_day():
    response = _put_global(date(2026, 12, 15), "10000.00")
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["period"] == "2026-12-01"
    assert body["total_amount"] == "10000.00"
    assert body["allocated_to_departments"] == "0.00"
    assert body["unallocated_amount"] == "10000.00"

    get_response = client.get("/api/budgets", params={"period": "2026-12-15"})
    assert get_response.status_code == 200
    assert get_response.json()["period"] == "2026-12-01"
    assert get_response.json()["total_amount"] == "10000.00"


def test_update_global_budget():
    _put_global(date(2026, 12, 1), "10000.00")
    response = _put_global(date(2026, 12, 1), "15000.00")
    assert response.status_code == 200
    assert response.json()["total_amount"] == "15000.00"


def test_assign_department_budgets_within_global_limit():
    period = date(2027, 1, 1)
    _put_global(period, "10000.00")

    r1 = _put_department(DEPT_VENTAS, period, "3000.00")
    assert r1.status_code == 200, r1.text
    r2 = _put_department(DEPT_INGENIERIA, period, "4000.00")
    assert r2.status_code == 200, r2.text

    overview = client.get(f"/api/budgets?period={period.isoformat()}")
    assert overview.status_code == 200
    body = overview.json()
    assert body["total_amount"] == "10000.00"
    assert body["allocated_to_departments"] == "7000.00"
    assert body["unallocated_amount"] == "3000.00"
    assert len(body["departments"]) == 2


def test_department_budget_exceeds_global_returns_409():
    period = date(2027, 2, 1)
    _put_global(period, "10000.00")
    _put_department(DEPT_VENTAS, period, "4000.00")
    _put_department(DEPT_INGENIERIA, period, "4000.00")

    response = _put_department(DEPT_MARKETING, period, "3000.00")
    assert response.status_code == 409, response.text
    assert response.json()["error"]["code"] == "conflict"
    message = response.json()["error"]["message"].lower()
    assert "disponible" in message or "superaría" in message


def test_reduce_global_budget_below_allocated_returns_409():
    period = date(2027, 3, 1)
    _put_global(period, "10000.00")
    _put_department(DEPT_VENTAS, period, "8000.00")

    response = _put_global(period, "5000.00")
    assert response.status_code == 409, response.text
    assert response.json()["error"]["code"] == "conflict"
    assert "8000.00" in response.json()["error"]["message"]


def test_benefit_references_are_informative_and_do_not_block():
    period = date(2027, 4, 1)
    _put_global(period, "10000.00")
    _put_department(DEPT_VENTAS, period, "3000.00")

    references = [
        {"benefit_id": 1, "indicative_amount": "9999.99"},
        {"benefit_id": 2, "indicative_amount": "0.00"},
    ]
    response = _put_references(DEPT_VENTAS, period, references)
    assert response.status_code == 200, response.text

    detail = client.get(f"/api/budgets?period={period.isoformat()}")
    assert detail.status_code == 200
    dept = detail.json()["departments"][0]
    assert dept["allocated_amount"] == "3000.00"
    assert dept["available_amount"] == "3000.00"

    refs = dept["benefit_references"]
    by_id = {r["benefit_id"]: r for r in refs}
    assert by_id[1]["indicative_amount"] == "9999.99"
    assert by_id[2]["indicative_amount"] == "0.00"


def test_monthly_independence_no_carryover():
    period_nov = date(2026, 11, 1)
    period_dec = date(2026, 12, 1)

    response = client.get(f"/api/budgets?period={period_dec.isoformat()}")
    assert response.status_code == 200
    body = response.json()
    assert body["period"] == "2026-12-01"
    assert body["total_amount"] == "0.00"
    assert body["allocated_to_departments"] == "0.00"
    assert body["unallocated_amount"] == "0.00"
    assert body["departments"] == []

    _put_global(period_dec, "5000.00")
    _put_department(DEPT_VENTAS, period_dec, "2000.00")

    nov_response = client.get(f"/api/budgets?period={period_nov.isoformat()}")
    assert nov_response.status_code == 200
    assert nov_response.json()["total_amount"] != "5000.00"

    dec_response = client.get(f"/api/budgets?period={period_dec.isoformat()}")
    assert dec_response.status_code == 200
    assert dec_response.json()["total_amount"] == "5000.00"
    assert dec_response.json()["allocated_to_departments"] == "2000.00"
