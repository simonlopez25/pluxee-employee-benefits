import pytest
from fastapi.testclient import TestClient

from app.main import app

pytestmark = pytest.mark.usefixtures("real_auth")

client = TestClient(app)


def test_budgets_requires_token():
    response = client.get("/api/budgets")
    assert response.status_code == 401, response.text
    assert response.json()["error"]["code"] == "missing_token"


def test_budgets_forbidden_for_employee(employee_headers):
    response = client.get("/api/budgets", headers=employee_headers)
    assert response.status_code == 403, response.text
    assert response.json()["error"]["code"] == "forbidden_role"


def test_budgets_allowed_for_admin(admin_headers):
    response = client.get("/api/budgets", headers=admin_headers)
    assert response.status_code == 200, response.text


def test_global_budget_write_forbidden_for_employee(employee_headers):
    response = client.put("/api/budgets/global", headers=employee_headers)
    assert response.status_code == 403, response.text
    assert response.json()["error"]["code"] == "forbidden_role"


def test_benefits_require_auth():
    response = client.get("/api/benefits")
    assert response.status_code == 401, response.text


def test_benefits_readable_by_employee(employee_headers):
    response = client.get("/api/benefits", headers=employee_headers)
    assert response.status_code == 200, response.text


def test_departments_readable_by_employee(employee_headers):
    response = client.get("/api/departments", headers=employee_headers)
    assert response.status_code == 200, response.text


def test_benefit_write_forbidden_for_employee(employee_headers):
    response = client.post("/api/benefits", headers=employee_headers)
    assert response.status_code == 403, response.text
    assert response.json()["error"]["code"] == "forbidden_role"