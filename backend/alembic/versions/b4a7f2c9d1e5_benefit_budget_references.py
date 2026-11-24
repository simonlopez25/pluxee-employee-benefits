"""budget references by benefit

Añade la tabla benefit_budget_references (referencias informativas por
beneficio sobre un presupuesto departamental) y la columna updated_at
en global_budgets.

Revision ID: b4a7f2c9d1e5
Revises: 929f9e4a2a20
Create Date: 2026-11-20 13:00:00.000000
"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'b4a7f2c9d1e5'
down_revision: Union[str, Sequence[str], None] = '929f9e4a2a20'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Crea benefit_budget_references y añade updated_at a global_budgets."""
    op.execute(
        "ALTER TABLE global_budgets "
        "ADD COLUMN updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()"
    )

    op.execute("""
        CREATE TABLE benefit_budget_references (
            id                    SERIAL        PRIMARY KEY,
            department_budget_id  INT           NOT NULL,
            benefit_id            INT           NOT NULL,
            indicative_amount     NUMERIC(12,2) NOT NULL,

            CONSTRAINT fk_benefit_budget_references_department_budget
                FOREIGN KEY (department_budget_id) REFERENCES department_budgets (id)
                ON DELETE RESTRICT,
            CONSTRAINT fk_benefit_budget_references_benefit
                FOREIGN KEY (benefit_id) REFERENCES benefits (id)
                ON DELETE RESTRICT,
            CONSTRAINT uq_benefit_budget_references_department_benefit
                UNIQUE (department_budget_id, benefit_id),
            CONSTRAINT ck_benefit_budget_references_indicative_amount
                CHECK (indicative_amount >= 0)
        );
    """)


def downgrade() -> None:
    """Elimina benefit_budget_references y updated_at de global_budgets."""
    op.execute("DROP TABLE benefit_budget_references;")
    op.execute("ALTER TABLE global_budgets DROP COLUMN updated_at;")
