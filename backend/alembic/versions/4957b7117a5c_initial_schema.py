"""initial schema

Revision ID: 4957b7117a5c
Revises:
Create Date: 2026-11-18 13:50:24.909264

Baseline con el DDL del DER aprobado (14 tablas).
"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '4957b7117a5c'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Crea las 14 tablas en orden de dependencia."""
    op.execute("""
        CREATE TABLE departments (
            id          SERIAL       PRIMARY KEY,
            name        VARCHAR(100) NOT NULL UNIQUE,
            currency    CHAR(3)      NOT NULL DEFAULT 'EUR',
            is_active   BOOLEAN      NOT NULL DEFAULT TRUE,
            created_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW()
        );
    """)

    op.execute("""
        CREATE TABLE global_budgets (
            id          SERIAL        PRIMARY KEY,
            period      DATE          NOT NULL UNIQUE,
            amount      NUMERIC(12,2) NOT NULL,
            created_at  TIMESTAMPTZ   NOT NULL DEFAULT NOW(),

            CONSTRAINT ck_global_budgets_amount CHECK (amount >= 0),
            CONSTRAINT ck_global_budgets_period CHECK (EXTRACT(DAY FROM period) = 1)
        );
    """)

    op.execute("""
        CREATE TABLE users (
            id                    SERIAL       PRIMARY KEY,
            department_id         INT          NULL,
            full_name             VARCHAR(120) NOT NULL,
            email                 VARCHAR(150) NOT NULL UNIQUE,
            password_hash         TEXT         NOT NULL,
            role                  VARCHAR(20)  NOT NULL,
            must_change_password  BOOLEAN      NOT NULL DEFAULT TRUE,
            is_active             BOOLEAN      NOT NULL DEFAULT TRUE,
            deactivated_at        TIMESTAMPTZ  NULL,
            created_at            TIMESTAMPTZ  NOT NULL DEFAULT NOW(),

            CONSTRAINT fk_users_department
                FOREIGN KEY (department_id) REFERENCES departments (id) ON DELETE RESTRICT,
            CONSTRAINT ck_users_role CHECK (role IN ('ADMIN', 'EMPLOYEE')),
            CONSTRAINT ck_users_role_department CHECK (
                (role = 'ADMIN'    AND department_id IS NULL) OR
                (role = 'EMPLOYEE' AND department_id IS NOT NULL)
            )
        );
    """)

    op.execute("""
        CREATE TABLE benefits (
            id           SERIAL      PRIMARY KEY,
            name         VARCHAR(80) NOT NULL UNIQUE,
            description  TEXT        NOT NULL,
            is_basic     BOOLEAN     NOT NULL DEFAULT FALSE,
            is_active    BOOLEAN     NOT NULL DEFAULT TRUE
        );
    """)

    op.execute("""
        CREATE TABLE packages (
            id              SERIAL        PRIMARY KEY,
            name            VARCHAR(100)  NOT NULL UNIQUE,
            description     TEXT          NULL,
            default_amount  NUMERIC(12,2) NOT NULL,
            is_active       BOOLEAN       NOT NULL DEFAULT TRUE,

            CONSTRAINT ck_packages_default_amount CHECK (default_amount >= 0)
        );
    """)

    op.execute("""
        CREATE TABLE package_benefits (
            package_id  INT NOT NULL,
            benefit_id  INT NOT NULL,

            CONSTRAINT pk_package_benefits PRIMARY KEY (package_id, benefit_id),
            CONSTRAINT fk_package_benefits_package
                FOREIGN KEY (package_id) REFERENCES packages (id) ON DELETE RESTRICT,
            CONSTRAINT fk_package_benefits_benefit
                FOREIGN KEY (benefit_id) REFERENCES benefits (id) ON DELETE RESTRICT
        );
    """)

    op.execute("""
        CREATE TABLE department_budgets (
            id                SERIAL        PRIMARY KEY,
            global_budget_id  INT           NOT NULL,
            department_id     INT           NOT NULL,
            amount            NUMERIC(12,2) NOT NULL,

            CONSTRAINT fk_department_budgets_global
                FOREIGN KEY (global_budget_id) REFERENCES global_budgets (id) ON DELETE RESTRICT,
            CONSTRAINT fk_department_budgets_department
                FOREIGN KEY (department_id) REFERENCES departments (id) ON DELETE RESTRICT,
            CONSTRAINT uq_department_budgets_global_department
                UNIQUE (global_budget_id, department_id),
            CONSTRAINT ck_department_budgets_amount CHECK (amount >= 0)
        );
    """)

    op.execute("""
        CREATE TABLE department_assignments (
            id                    SERIAL        PRIMARY KEY,
            department_budget_id  INT           NOT NULL,
            package_id            INT           NOT NULL,
            amount_per_employee   NUMERIC(12,2) NOT NULL,
            assigned_at           TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
            is_active             BOOLEAN       NOT NULL DEFAULT TRUE,

            CONSTRAINT fk_department_assignments_budget
                FOREIGN KEY (department_budget_id) REFERENCES department_budgets (id) ON DELETE RESTRICT,
            CONSTRAINT fk_department_assignments_package
                FOREIGN KEY (package_id) REFERENCES packages (id) ON DELETE RESTRICT,
            CONSTRAINT uq_department_assignments_budget_package
                UNIQUE (department_budget_id, package_id),
            CONSTRAINT uq_department_assignments_id_package
                UNIQUE (id, package_id),
            CONSTRAINT ck_department_assignments_amount CHECK (amount_per_employee >= 0)
        );
    """)

    op.execute("""
        CREATE TABLE employee_assignments (
            id                        SERIAL        PRIMARY KEY,
            department_assignment_id  INT           NOT NULL,
            package_id                INT           NOT NULL,
            user_id                   INT           NOT NULL,
            assigned_amount           NUMERIC(12,2) NOT NULL,
            is_active                 BOOLEAN       NOT NULL DEFAULT TRUE,

            CONSTRAINT fk_employee_assignments_department_assignment
                FOREIGN KEY (department_assignment_id) REFERENCES department_assignments (id) ON DELETE RESTRICT,
            CONSTRAINT fk_employee_assignments_package
                FOREIGN KEY (package_id) REFERENCES packages (id) ON DELETE RESTRICT,
            CONSTRAINT fk_employee_assignments_user
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE RESTRICT,
            CONSTRAINT uq_employee_assignments_assignment_user
                UNIQUE (department_assignment_id, user_id),
            CONSTRAINT uq_employee_assignments_id_package
                UNIQUE (id, package_id),
            CONSTRAINT fk_employee_assignments_assignment_package
                FOREIGN KEY (department_assignment_id, package_id)
                REFERENCES department_assignments (id, package_id) ON DELETE RESTRICT,
            CONSTRAINT ck_employee_assignments_amount CHECK (assigned_amount >= 0)
        );
    """)

    op.execute("""
        CREATE TABLE expenses (
            id                SERIAL        PRIMARY KEY,
            user_id           INT           NOT NULL,
            benefit_id        INT           NOT NULL,
            amount            NUMERIC(12,2) NOT NULL,
            expense_date      DATE          NOT NULL,
            description       VARCHAR(200)  NOT NULL,
            status            VARCHAR(20)   NOT NULL DEFAULT 'PENDING',
            rejection_reason  TEXT          NULL,
            reviewed_by_id    INT           NULL,
            reviewed_at       TIMESTAMPTZ   NULL,
            created_at        TIMESTAMPTZ   NOT NULL DEFAULT NOW(),

            CONSTRAINT fk_expenses_user
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE RESTRICT,
            CONSTRAINT fk_expenses_benefit
                FOREIGN KEY (benefit_id) REFERENCES benefits (id) ON DELETE RESTRICT,
            CONSTRAINT fk_expenses_reviewed_by
                FOREIGN KEY (reviewed_by_id) REFERENCES users (id) ON DELETE RESTRICT,
            CONSTRAINT ck_expenses_amount CHECK (amount > 0),
            CONSTRAINT ck_expenses_status CHECK (status IN ('PENDING', 'APPROVED', 'REJECTED')),
            CONSTRAINT ck_expenses_rejection_reason CHECK (
                status <> 'REJECTED' OR rejection_reason IS NOT NULL
            )
        );
    """)

    op.execute("""
        CREATE TABLE expense_allocations (
            id                      SERIAL        PRIMARY KEY,
            expense_id              INT           NOT NULL,
            employee_assignment_id  INT           NOT NULL,
            package_id              INT           NOT NULL,
            benefit_id              INT           NOT NULL,
            amount                  NUMERIC(12,2) NOT NULL,

            CONSTRAINT fk_expense_allocations_expense
                FOREIGN KEY (expense_id) REFERENCES expenses (id) ON DELETE RESTRICT,
            CONSTRAINT fk_expense_allocations_employee_assignment
                FOREIGN KEY (employee_assignment_id) REFERENCES employee_assignments (id) ON DELETE RESTRICT,
            CONSTRAINT fk_expense_allocations_package
                FOREIGN KEY (package_id) REFERENCES packages (id) ON DELETE RESTRICT,
            CONSTRAINT fk_expense_allocations_benefit
                FOREIGN KEY (benefit_id) REFERENCES benefits (id) ON DELETE RESTRICT,
            CONSTRAINT fk_expense_allocations_assignment_package
                FOREIGN KEY (employee_assignment_id, package_id)
                REFERENCES employee_assignments (id, package_id) ON DELETE RESTRICT,
            CONSTRAINT fk_expense_allocations_package_benefit
                FOREIGN KEY (package_id, benefit_id)
                REFERENCES package_benefits (package_id, benefit_id) ON DELETE RESTRICT,
            CONSTRAINT ck_expense_allocations_amount CHECK (amount > 0)
        );
    """)

    op.execute("""
        CREATE TABLE attachments (
            id             SERIAL       PRIMARY KEY,
            expense_id     INT          NOT NULL,
            storage_path   TEXT         NOT NULL,
            original_name  VARCHAR(255) NOT NULL,
            mime_type      VARCHAR(100) NOT NULL,
            uploaded_at    TIMESTAMPTZ  NOT NULL DEFAULT NOW(),

            CONSTRAINT fk_attachments_expense
                FOREIGN KEY (expense_id) REFERENCES expenses (id) ON DELETE RESTRICT
        );
    """)

    op.execute("""
        CREATE TABLE expense_history (
            id               SERIAL      PRIMARY KEY,
            expense_id       INT         NOT NULL,
            actor_id         INT         NOT NULL,
            previous_status  VARCHAR(20) NOT NULL,
            new_status       VARCHAR(20) NOT NULL,
            reason           TEXT        NULL,
            created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),

            CONSTRAINT fk_expense_history_expense
                FOREIGN KEY (expense_id) REFERENCES expenses (id) ON DELETE RESTRICT,
            CONSTRAINT fk_expense_history_actor
                FOREIGN KEY (actor_id) REFERENCES users (id) ON DELETE RESTRICT,
            CONSTRAINT ck_expense_history_previous_status
                CHECK (previous_status IN ('PENDING', 'APPROVED', 'REJECTED')),
            CONSTRAINT ck_expense_history_new_status
                CHECK (new_status IN ('PENDING', 'APPROVED', 'REJECTED'))
        );
    """)

    op.execute("""
        CREATE TABLE audit_logs (
            id           SERIAL      PRIMARY KEY,
            actor_id     INT         NOT NULL,
            entity_type  VARCHAR(50) NOT NULL,
            entity_id    INT         NOT NULL,
            action       VARCHAR(30) NOT NULL,
            detail       JSONB       NOT NULL,
            created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),

            CONSTRAINT fk_audit_logs_actor
                FOREIGN KEY (actor_id) REFERENCES users (id) ON DELETE RESTRICT
        );
    """)


def downgrade() -> None:
    """Elimina las 14 tablas en orden inverso (RESTRICT lo exige)."""
    op.execute("DROP TABLE audit_logs;")
    op.execute("DROP TABLE expense_history;")
    op.execute("DROP TABLE attachments;")
    op.execute("DROP TABLE expense_allocations;")
    op.execute("DROP TABLE expenses;")
    op.execute("DROP TABLE employee_assignments;")
    op.execute("DROP TABLE department_assignments;")
    op.execute("DROP TABLE department_budgets;")
    op.execute("DROP TABLE package_benefits;")
    op.execute("DROP TABLE packages;")
    op.execute("DROP TABLE benefits;")
    op.execute("DROP TABLE users;")
    op.execute("DROP TABLE global_budgets;")
    op.execute("DROP TABLE departments;")
