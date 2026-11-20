"""packages ligado a un departamento; se elimina department_assignments

Derivado del feedback del cliente:

- Un paquete va dirigido a UN grupo de empleados (departamento) y un
  grupo puede tener varios paquetes: `packages.department_id NOT NULL`.
- `department_assignments` resultaba redundante con `packages`, así que
  desaparece. El presupuesto se deriva: department_id →
  department_budgets(department_id) → global_budgets(period).
- `employee_assignments` pasa a apuntar directamente al paquete
  (UNIQUE (package_id, user_id): como mucho una asignación por paquete
  y empleado).

Migración de datos: los paquetes asignados a más de un departamento se
duplican (una copia por departamento extra, con sufijo " (departamento)")
y las asignaciones/gastos de esos departamentos se re-apuntan a la copia.

Revision ID: 5f2c8a91e4d7
Revises: 4957b7117a5c
Create Date: 2026-11-20 10:15:00.000000
"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '5f2c8a91e4d7'
down_revision: Union[str, Sequence[str], None] = '4957b7117a5c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ---------------------------------------------------------------
    # 1. Columna nueva (todavía anulable: se rellena en el paso 3)
    # ---------------------------------------------------------------
    op.execute("ALTER TABLE packages ADD COLUMN department_id INT;")

    # ---------------------------------------------------------------
    # 2. Reparto actual: pares (paquete, departamento) distintos, con el
    #    departamento "principal" del paquete (rn = 1) y el resto como
    #    copias (rn > 1).
    # ---------------------------------------------------------------
    op.execute("""
        CREATE TEMP TABLE package_split AS
        WITH pairs AS (
            SELECT DISTINCT da.package_id, db.department_id
            FROM department_assignments da
            JOIN department_budgets db ON db.id = da.department_budget_id
        )
        SELECT pairs.package_id                          AS old_id,
               pairs.department_id,
               ROW_NUMBER() OVER (
                   PARTITION BY pairs.package_id
                   ORDER BY pairs.department_id
               ) AS rn
        FROM pairs
    """)

    # ---------------------------------------------------------------
    # 3. Backfill: el paquete se queda con su primer departamento.
    #    (Un paquete sin ninguna asignación toma el departamento de
    #     menor id; si no hubiera departamentos, el paso 9 falla y es
    #     correcto: no puede existir un paquete sin grupo.)
    # ---------------------------------------------------------------
    op.execute("""
        UPDATE packages pkg
        SET department_id = split.department_id
        FROM package_split split
        WHERE split.old_id = pkg.id AND split.rn = 1
    """)
    op.execute("""
        UPDATE packages
        SET department_id = (SELECT MIN(id) FROM departments)
        WHERE department_id IS NULL
    """)

    # ---------------------------------------------------------------
    # 4. Copia por cada departamento extra (packages.name es UNIQUE).
    # ---------------------------------------------------------------
    op.execute("""
        INSERT INTO packages
            (name, description, default_amount, is_active, department_id)
        SELECT pkg.name || ' (' || dep.name || ')',
               pkg.description,
               pkg.default_amount,
               pkg.is_active,
               split.department_id
        FROM package_split split
        JOIN packages    pkg ON pkg.id = split.old_id
        JOIN departments dep ON dep.id = split.department_id
        WHERE split.rn > 1
    """)

    # ---------------------------------------------------------------
    # 5. Mapa old_id/department_id → new_id. El match es por nombre,
    #    determinista porque packages.name es UNIQUE.
    # ---------------------------------------------------------------
    op.execute("""
        CREATE TEMP TABLE package_split_map AS
        SELECT split.old_id, split.department_id, np.id AS new_id
        FROM package_split split
        JOIN packages    pkg ON pkg.id = split.old_id
        JOIN departments dep ON dep.id = split.department_id
        JOIN packages     np ON np.name = pkg.name || ' (' || dep.name || ')'
        WHERE split.rn > 1
    """)

    # ---------------------------------------------------------------
    # 6. package_benefits de las copias (require las copias, paso 4).
    # ---------------------------------------------------------------
    op.execute("""
        INSERT INTO package_benefits (package_id, benefit_id)
        SELECT map.new_id, pb.benefit_id
        FROM package_split_map map
        JOIN package_benefits pb ON pb.package_id = map.old_id
    """)

    # ---------------------------------------------------------------
    # 7. Restricciones que impiden re-apuntar filas existentes.
    # ---------------------------------------------------------------
    op.execute(
        "ALTER TABLE expense_allocations "
        "DROP CONSTRAINT fk_expense_allocations_assignment_package;"
    )
    op.execute(
        "ALTER TABLE employee_assignments "
        "DROP CONSTRAINT fk_employee_assignments_assignment_package;"
    )
    op.execute(
        "ALTER TABLE employee_assignments "
        "DROP CONSTRAINT fk_employee_assignments_department_assignment;"
    )
    op.execute(
        "ALTER TABLE employee_assignments "
        "DROP CONSTRAINT uq_employee_assignments_assignment_user;"
    )

    # ---------------------------------------------------------------
    # 8. Re-apuntar los gastos de los empleados del departamento copiado
    #    (antes de mover employee_assignments: la FK compuesta necesita
    #    que los dos campos sigan casados).
    # ---------------------------------------------------------------
    op.execute("""
        UPDATE expense_allocations al
        SET package_id = map.new_id
        FROM employee_assignments ea
        JOIN users u
          ON u.id = ea.user_id
        JOIN package_split_map map
          ON map.department_id = u.department_id
        WHERE al.employee_assignment_id = ea.id
          AND ea.package_id = map.old_id
    """)

    # ---------------------------------------------------------------
    # 9. Igual para las asignaciones de empleado.
    # ---------------------------------------------------------------
    op.execute("""
        UPDATE employee_assignments ea
        SET package_id = map.new_id
        FROM users u
        JOIN package_split_map map
          ON map.department_id = u.department_id
        WHERE ea.user_id = u.id
          AND ea.package_id = map.old_id
    """)

    # ---------------------------------------------------------------
    # 10. packages.department_id pasa a ser obligatorio + FK.
    # ---------------------------------------------------------------
    op.execute("ALTER TABLE packages ALTER COLUMN department_id SET NOT NULL;")
    op.execute("""
        ALTER TABLE packages
            ADD CONSTRAINT fk_packages_department
            FOREIGN KEY (department_id) REFERENCES departments (id)
            ON DELETE RESTRICT
    """)

    # ---------------------------------------------------------------
    # 11. employee_assignments deja de colgar de department_assignments.
    # ---------------------------------------------------------------
    op.execute(
        "ALTER TABLE employee_assignments DROP COLUMN department_assignment_id;"
    )
    op.execute("""
        ALTER TABLE employee_assignments
            ADD CONSTRAINT uq_employee_assignments_package_user
            UNIQUE (package_id, user_id)
    """)

    # ---------------------------------------------------------------
    # 12. Restaurar la FK compuesta de expense_allocations: los datos ya
    #     están corregidos, así que la validación al recrearla pasa.
    # ---------------------------------------------------------------
    op.execute("""
        ALTER TABLE expense_allocations
            ADD CONSTRAINT fk_expense_allocations_assignment_package
            FOREIGN KEY (employee_assignment_id, package_id)
            REFERENCES employee_assignments (id, package_id)
            ON DELETE RESTRICT
    """)

    # ---------------------------------------------------------------
    # 13. Adiós a la tabla puente y a las temporales.
    # ---------------------------------------------------------------
    op.execute("DROP TABLE department_assignments;")
    op.execute("DROP TABLE package_split_map;")
    op.execute("DROP TABLE package_split;")


def downgrade() -> None:
    """Restaura el modelo anterior (mejor esfuerzo).

    Reconstruye department_assignments desde packages → department_budgets:
    un paquete cuyo departamento no tenga presupuesto no puede
    re-representarse y haría fallar el paso 3.
    """
    # 1. Tabla puente con el DDL del baseline
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
            CONSTRAINT ck_department_assignments_amount
                CHECK (amount_per_employee >= 0)
        );
    """)

    # 2. Cada paquete vuelve a su presupuesto de departamento
    op.execute("""
        INSERT INTO department_assignments
            (department_budget_id, package_id, amount_per_employee)
        SELECT DISTINCT ON (pkg.id)
               db.id, pkg.id, pkg.default_amount
        FROM packages pkg
        JOIN department_budgets db ON db.department_id = pkg.department_id
        ORDER BY pkg.id, db.id
    """)

    # 3. employee_assignments recupera su columna y constraints
    op.execute(
        "ALTER TABLE employee_assignments "
        "ADD COLUMN department_assignment_id INT;"
    )
    op.execute("""
        UPDATE employee_assignments ea
        SET department_assignment_id = da.id
        FROM packages pkg
        JOIN department_budgets db
          ON db.department_id = pkg.department_id
        JOIN department_assignments da
          ON da.department_budget_id = db.id AND da.package_id = pkg.id
        WHERE ea.package_id = pkg.id
    """)
    op.execute(
        "ALTER TABLE employee_assignments "
        "ALTER COLUMN department_assignment_id SET NOT NULL;"
    )
    op.execute("""
        ALTER TABLE employee_assignments
            ADD CONSTRAINT fk_employee_assignments_department_assignment
            FOREIGN KEY (department_assignment_id)
            REFERENCES department_assignments (id) ON DELETE RESTRICT
    """)
    op.execute("""
        ALTER TABLE employee_assignments
            ADD CONSTRAINT fk_employee_assignments_assignment_package
            FOREIGN KEY (department_assignment_id, package_id)
            REFERENCES department_assignments (id, package_id)
            ON DELETE RESTRICT
    """)
    op.execute("""
        ALTER TABLE employee_assignments
            ADD CONSTRAINT uq_employee_assignments_assignment_user
            UNIQUE (department_assignment_id, user_id)
    """)
    op.execute(
        "ALTER TABLE employee_assignments "
        "DROP CONSTRAINT uq_employee_assignments_package_user;"
    )

    # 4. packages vuelve a no conocer departamentos
    op.execute("ALTER TABLE packages DROP COLUMN department_id;")
