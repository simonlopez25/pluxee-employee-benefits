"""package name unique per department ignoring case

La regla del servicio compara nombres sin distinguir mayúsculas
(«Comida» = «comida»), pero el UNIQUE anterior sí las distinguía.
Se sustituye por un índice único sobre (department_id, lower(name))
para que la base de datos aplique la misma regla que el servicio.

Revision ID: c7d3e1a9b2f4
Revises: b4a7f2c9d1e5
Create Date: 2026-11-24 12:30:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c7d3e1a9b2f4'
down_revision: Union[str, Sequence[str], None] = 'b4a7f2c9d1e5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Cambia el UNIQUE (name, department_id) por uno que ignora mayúsculas."""
    op.drop_constraint('uq_package_name_department', 'packages', type_='unique')
    op.create_index(
        'uq_package_name_department',
        'packages',
        ['department_id', sa.text('lower(name)')],
        unique=True,
    )


def downgrade() -> None:
    """Vuelve al UNIQUE que distingue mayúsculas."""
    op.drop_index('uq_package_name_department', table_name='packages')
    op.create_unique_constraint(
        'uq_package_name_department', 'packages', ['name', 'department_id']
    )