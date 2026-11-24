-- =====================================================================
-- PLUXEE · Datos de prueba (seed)
-- Ejecutar DESPUÉS de crear el esquema con Alembic (alembic upgrade head),
-- sobre la base de datos vacía.
-- =====================================================================
--
-- CÓMO USARLO
--   A) Con el runner del repo (recomendado — funciona contra Neon o local):
--        npm run seed              # si la BD está vacía
--        npm run seed -- --reset   # borra los datos (TRUNCATE) y vuelve a sembrar
--
--   B) En pgAdmin (Postgres local):
--        1. Crea el esquema antes: cd backend && .venv\Scripts\python -m alembic upgrade head
--        2. Abre el Query Tool sobre tu base de datos (local: "pluxee").
--        3. Pega este archivo completo y ejecútalo con F5.
--        4. Al terminar, la consulta B debe dar a Lucía:
--           Comida = 70,00 y Transporte = 10,00. Si sale eso, todo está bien.
--
--   En la BD compartida (Neon) la base se llama "neondb"; en local, "pluxee".
--
-- IMPORTANTE
--   · Son datos inventados, solo para desarrollo, pruebas y la demo.
--     Nunca se usan en producción.
--   · Todos los usuarios tienen la contraseña de prueba:  Prueba123!
--     (en la tabla se guarda su hash bcrypt, nunca el texto).
--   · El mes de prueba es noviembre de 2026 (period = 2026-11-01).
--
-- SI QUIERES VOLVER A EMPEZAR (borra TODOS los datos, no las tablas):
--   Usa `npm run seed -- --reset`, o descomenta y ejecuta SOLO este bloque
--   en pgAdmin (el runner lo detecta solo aunque esté comentado, así que si
--   usas npm run seed con el bloque descomentado NO borra nada: usa --reset):
--
-- SEED_RESET_BEGIN
-- TRUNCATE audit_logs, expense_history, attachments, expense_allocations,
-- expenses, employee_assignments,
-- department_budgets, package_benefits, packages, benefits,
-- users, global_budgets, departments
-- RESTART IDENTITY;
-- SEED_RESET_END
-- =====================================================================

BEGIN;


-- ---------------------------------------------------------------------
-- 1. Departamentos
-- ---------------------------------------------------------------------
INSERT INTO departments (id, name, currency) VALUES
    (1, 'Ventas',     'EUR'),
    (2, 'Ingeniería', 'EUR'),
    (3, 'Marketing',  'EUR');


-- ---------------------------------------------------------------------
-- 2. Usuarios (contraseña de todos: Prueba123!)
-- ---------------------------------------------------------------------
INSERT INTO users (id, department_id, full_name, email, password_hash, role,
                   must_change_password, is_active, deactivated_at) VALUES
    -- Administrador: sin departamento
    (1, NULL, 'Ana Ruiz (RRHH)', 'admin@pluxee.test',
     '$2b$12$786Lgq8876eES2vfb4urfeocuAU7rz4/T1hGl9Q.MmKHatxz.Tf8m', 'ADMIN', FALSE, TRUE, NULL),
    -- Ventas
    (2, 1, 'Lucía García', 'lucia.garcia@pluxee.test',
     '$2b$12$786Lgq8876eES2vfb4urfeocuAU7rz4/T1hGl9Q.MmKHatxz.Tf8m', 'EMPLOYEE', FALSE, TRUE, NULL),
    (3, 1, 'Carlos Martín', 'carlos.martin@pluxee.test',
     '$2b$12$786Lgq8876eES2vfb4urfeocuAU7rz4/T1hGl9Q.MmKHatxz.Tf8m', 'EMPLOYEE', FALSE, TRUE, NULL),
    -- Ingeniería
    (4, 2, 'Javier López', 'javier.lopez@pluxee.test',
     '$2b$12$786Lgq8876eES2vfb4urfeocuAU7rz4/T1hGl9Q.MmKHatxz.Tf8m', 'EMPLOYEE', FALSE, TRUE, NULL),
    -- Empleada nueva: tiene que cambiar la contraseña al entrar
    (5, 2, 'Sara Díaz', 'sara.diaz@pluxee.test',
     '$2b$12$786Lgq8876eES2vfb4urfeocuAU7rz4/T1hGl9Q.MmKHatxz.Tf8m', 'EMPLOYEE', TRUE, TRUE, NULL),
    -- Marketing
    (6, 3, 'Elena Torres', 'elena.torres@pluxee.test',
     '$2b$12$786Lgq8876eES2vfb4urfeocuAU7rz4/T1hGl9Q.MmKHatxz.Tf8m', 'EMPLOYEE', FALSE, TRUE, NULL),
    -- Empleado dado de baja (baja lógica): no puede entrar y no recibe paquetes
    (7, 3, 'Pedro Sánchez', 'pedro.sanchez@pluxee.test',
     '$2b$12$786Lgq8876eES2vfb4urfeocuAU7rz4/T1hGl9Q.MmKHatxz.Tf8m', 'EMPLOYEE', FALSE, FALSE, '2026-10-31 18:00:00+01');


-- ---------------------------------------------------------------------
-- 3. Beneficios (descripciones enviadas por Pablo el 17/11)
-- ---------------------------------------------------------------------
INSERT INTO benefits (id, name, description, is_basic) VALUES
    (1, 'Comida',
     'Gastos en restauración. El empleado pide el reembolso con un ticket o factura y el importe gastado. El administrador lo aprueba o lo deniega con sus propios criterios.',
     TRUE),
    (2, 'Transporte',
     'Reembolso o pago previo de billetes de tren, autobús u otro transporte público terrestre.',
     TRUE),
    (3, 'Formación',
     'El empleado solicita que la empresa compre libros o cursos de formación.',
     TRUE),
    (4, 'Guardería',
     'El empleado solicita cada mes la mensualidad de la guardería de su hijo o hijos.',
     TRUE);


-- ---------------------------------------------------------------------
-- 4. Paquetes y beneficios que cubre cada uno
-- ---------------------------------------------------------------------
INSERT INTO packages (id, name, description, default_amount, department_id) VALUES
    (1, 'Comida y transporte', 'Saldo compartido entre comida y transporte', 100.00, 1),
    (2, 'Comida',              NULL,                                          60.00, 1),
    (3, 'Transporte',          NULL,                                          50.00, 2),
    (4, 'Formación',           NULL,                                         150.00, 2),
    (5, 'Guardería',           NULL,                                         300.00, 3),
    -- Un paquete va dirigido a UN grupo de empleados: si Marketing necesita
    -- lo mismo que Ventas, se crea otro paquete (el nombre es único).
    (6, 'Comida y transporte flexible',
         'Saldo compartido entre comida y transporte',                       100.00, 3);

INSERT INTO package_benefits (package_id, benefit_id) VALUES
    (1, 1), (1, 2),   -- Comida y transporte: multibeneficio
    (2, 1),           -- Comida: monobeneficio
    (3, 2),           -- Transporte: monobeneficio
    (4, 3),           -- Formación: monobeneficio
    (5, 4),           -- Guardería: monobeneficio
    (6, 1), (6, 2);   -- Comida y transporte flexible: multibeneficio


-- ---------------------------------------------------------------------
-- 5. Presupuesto global del mes y reparto por departamento
--    Global 10.000 €; departamentos 8.000 € (quedan 2.000 € sin repartir)
-- ---------------------------------------------------------------------
INSERT INTO global_budgets (id, period, amount) VALUES
    (1, '2026-11-01', 10000.00);

INSERT INTO department_budgets (id, global_budget_id, department_id, amount) VALUES
    (1, 1, 1, 3000.00),   -- Ventas
    (2, 1, 2, 3000.00),   -- Ingeniería
    (3, 1, 3, 2000.00);   -- Marketing


-- ---------------------------------------------------------------------
-- 6. Paquetes de cada empleado activo (Pedro está de baja: no recibe)
--    Un paquete ⇒ un grupo; cada empleado puede tener varios paquetes.
-- ---------------------------------------------------------------------
INSERT INTO employee_assignments (id, package_id, user_id, assigned_amount) VALUES
    -- Ventas: el ejemplo de Pablo (paquete de 100 € de comida y transporte + paquete de 60 € de comida)
    (1, 1, 2, 100.00),   -- Lucía: Comida y transporte
    (2, 2, 2,  60.00),   -- Lucía: Comida
    (3, 1, 3, 100.00),   -- Carlos: Comida y transporte
    (4, 2, 3,  60.00),   -- Carlos: Comida
    -- Ingeniería
    (5, 4, 4, 150.00),   -- Javier: Formación
    (6, 3, 4,  50.00),   -- Javier: Transporte
    (7, 4, 5, 150.00),   -- Sara: Formación
    (8, 3, 5,  50.00),   -- Sara: Transporte
    -- Marketing: Elena tiene el importe de comida y transporte ajustado (caso particular)
    (9,  6, 6,  80.00),  -- Elena: Comida y transporte flexible (ajustado de 100 € a 80 €)
    (10, 5, 6, 300.00);  -- Elena: Guardería


-- ---------------------------------------------------------------------
-- 7. Gastos, con su reparto entre paquetes (expense_allocations)
-- ---------------------------------------------------------------------
INSERT INTO expenses (id, user_id, benefit_id, amount, expense_date, description,
                      status, rejection_reason, reviewed_by_id, reviewed_at, created_at) VALUES
    -- Ejemplo de Pablo: Lucía ha gastado 90 € en transporte del paquete de comida y transporte
    (1, 2, 2,  90.00, '2026-11-03', 'Abono mensual de tren',
     'APPROVED', NULL, 1, '2026-11-04 10:00:00+01', '2026-11-03 09:15:00+01'),
    -- Carlos: comida aprobada (sale primero del paquete monobeneficio)
    (2, 3, 1,  12.50, '2026-11-05', 'Menú del día con cliente',
     'APPROVED', NULL, 1, '2026-11-06 09:30:00+01', '2026-11-05 14:40:00+01'),
    -- Carlos: comida denegada (con motivo obligatorio)
    (3, 3, 1,  20.00, '2026-11-07', 'Cena de fin de semana',
     'REJECTED', 'El ticket es de un sábado y no corresponde a una jornada laboral.', 1, '2026-11-08 11:00:00+01', '2026-11-07 22:10:00+01'),
    -- Javier: formación pendiente de revisar (pago previo con factura proforma)
    (4, 4, 3, 120.00, '2026-11-10', 'Curso online de Python avanzado',
     'PENDING', NULL, NULL, NULL, '2026-11-10 12:00:00+01'),
    -- Elena: guardería aprobada
    (5, 6, 4, 300.00, '2026-11-02', 'Mensualidad de guardería de noviembre',
     'APPROVED', NULL, 1, '2026-11-03 16:00:00+01', '2026-11-02 08:30:00+01'),
    -- Elena: comida pendiente (no tiene paquete solo de comida: sale del multibeneficio)
    (6, 6, 1,  15.00, '2026-11-12', 'Desayuno de trabajo',
     'PENDING', NULL, NULL, NULL, '2026-11-12 10:20:00+01');

-- La suma del reparto de cada gasto es igual a su importe
INSERT INTO expense_allocations (id, expense_id, employee_assignment_id, package_id, benefit_id, amount) VALUES
    (1, 1, 1,  1, 2,  90.00),   -- Lucía: 90 € de transporte del paquete Comida y transporte
    (2, 2, 4,  2, 1,  12.50),   -- Carlos: del paquete Comida (monobeneficio, va primero)
    (3, 3, 4,  2, 1,  20.00),   -- Carlos: gasto denegado; no cuenta en el saldo porque está REJECTED
    (4, 4, 5,  4, 3, 120.00),   -- Javier: del paquete Formación
    (5, 5, 10, 5, 4, 300.00),   -- Elena: del paquete Guardería
    (6, 6, 9,  6, 1,  15.00);   -- Elena: del paquete Comida y transporte flexible


-- ---------------------------------------------------------------------
-- 8. Justificantes (solo la ruta; los archivos no existen en estos datos de prueba)
-- ---------------------------------------------------------------------
INSERT INTO attachments (id, expense_id, storage_path, original_name, mime_type, uploaded_at) VALUES
    (1, 1, 'uploads/2026/11/expense_1_abono_tren.pdf',      'abono_tren_noviembre.pdf', 'application/pdf', '2026-11-03 09:15:00+01'),
    (2, 2, 'uploads/2026/11/expense_2_ticket.jpg',          'ticket_restaurante.jpg',   'image/jpeg',      '2026-11-05 14:40:00+01'),
    (3, 3, 'uploads/2026/11/expense_3_ticket.jpg',          'ticket_cena.jpg',          'image/jpeg',      '2026-11-07 22:10:00+01'),
    (4, 4, 'uploads/2026/11/expense_4_proforma.pdf',        'proforma_curso_python.pdf','application/pdf', '2026-11-10 12:00:00+01'),
    (5, 5, 'uploads/2026/11/expense_5_guarderia.pdf',       'recibo_guarderia.pdf',     'application/pdf', '2026-11-02 08:30:00+01'),
    (6, 6, 'uploads/2026/11/expense_6_ticket.png',          'ticket_desayuno.png',      'image/png',       '2026-11-12 10:20:00+01');


-- ---------------------------------------------------------------------
-- 9. Histórico de cambios de estado (solo de los gastos ya revisados)
-- ---------------------------------------------------------------------
INSERT INTO expense_history (id, expense_id, actor_id, previous_status, new_status, reason, created_at) VALUES
    (1, 1, 1, 'PENDING', 'APPROVED', NULL, '2026-11-04 10:00:00+01'),
    (2, 2, 1, 'PENDING', 'APPROVED', NULL, '2026-11-06 09:30:00+01'),
    (3, 3, 1, 'PENDING', 'REJECTED', 'El ticket es de un sábado y no corresponde a una jornada laboral.', '2026-11-08 11:00:00+01'),
    (4, 5, 1, 'PENDING', 'APPROVED', NULL, '2026-11-03 16:00:00+01');


-- ---------------------------------------------------------------------
-- 10. Auditoría de algunas acciones del administrador
-- ---------------------------------------------------------------------
INSERT INTO audit_logs (id, actor_id, entity_type, entity_id, action, detail, created_at) VALUES
    (1, 1, 'global_budgets',       1, 'create',     '{"period": "2026-11-01", "amount": 10000.00}', '2026-11-01 09:00:00+01'),
    (2, 1, 'department_budgets',   1, 'create',     '{"department": "Ventas", "amount": 3000.00}',  '2026-11-01 09:05:00+01'),
    (3, 1, 'employee_assignments', 9, 'update',     '{"assigned_amount": {"before": 100.00, "after": 80.00}}', '2026-11-01 09:30:00+01'),
    (4, 1, 'users',                7, 'deactivate', '{"is_active": {"before": true, "after": false}}', '2026-10-31 18:00:00+01');


-- ---------------------------------------------------------------------
-- 11. Poner al día los contadores de id
--     Como arriba hemos escrito los id a mano, le decimos a cada contador
--     (SERIAL) por qué número va. Así la app podrá crear filas nuevas
--     sin chocar con un id que ya existe.
-- ---------------------------------------------------------------------
SELECT setval(pg_get_serial_sequence('departments',            'id'), (SELECT MAX(id) FROM departments));
SELECT setval(pg_get_serial_sequence('users',                  'id'), (SELECT MAX(id) FROM users));
SELECT setval(pg_get_serial_sequence('benefits',               'id'), (SELECT MAX(id) FROM benefits));
SELECT setval(pg_get_serial_sequence('packages',               'id'), (SELECT MAX(id) FROM packages));
SELECT setval(pg_get_serial_sequence('global_budgets',         'id'), (SELECT MAX(id) FROM global_budgets));
SELECT setval(pg_get_serial_sequence('department_budgets',     'id'), (SELECT MAX(id) FROM department_budgets));
SELECT setval(pg_get_serial_sequence('employee_assignments',   'id'), (SELECT MAX(id) FROM employee_assignments));
SELECT setval(pg_get_serial_sequence('expenses',               'id'), (SELECT MAX(id) FROM expenses));
SELECT setval(pg_get_serial_sequence('expense_allocations',    'id'), (SELECT MAX(id) FROM expense_allocations));
SELECT setval(pg_get_serial_sequence('attachments',            'id'), (SELECT MAX(id) FROM attachments));
SELECT setval(pg_get_serial_sequence('expense_history',        'id'), (SELECT MAX(id) FROM expense_history));
SELECT setval(pg_get_serial_sequence('audit_logs',             'id'), (SELECT MAX(id) FROM audit_logs));


COMMIT;


-- =====================================================================
-- CONSULTAS DE COMPROBACIÓN. Se ejecutan solas al final del script
-- (no cambian datos, solo consultan). También puedes seleccionar una y ejecutarla.
-- =====================================================================

-- A) Restante de cada paquete de cada empleado
--    Restante = asignado − aprobado − pendiente (los denegados no cuentan)

SELECT u.full_name,
       p.name                                   AS paquete,
       ea.assigned_amount                       AS asignado,
       ea.assigned_amount - COALESCE(SUM(al.amount)
           FILTER (WHERE e.status IN ('APPROVED', 'PENDING')), 0) AS restante
FROM employee_assignments ea
JOIN users u     ON u.id = ea.user_id
JOIN packages p  ON p.id = ea.package_id
LEFT JOIN expense_allocations al ON al.employee_assignment_id = ea.id
LEFT JOIN expenses e             ON e.id = al.expense_id
GROUP BY u.full_name, p.name, ea.id
ORDER BY u.full_name, p.name;


-- B) Saldo por beneficio de Lucía (ejemplo de Pablo). Debe dar Comida = 70 € y Transporte = 10 €

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
SELECT u.full_name, b.name AS beneficio, SUM(rp.restante) AS saldo
FROM restante_paquete rp
JOIN users u             ON u.id = rp.user_id
JOIN package_benefits pb ON pb.package_id = rp.package_id
JOIN benefits b          ON b.id = pb.benefit_id
WHERE u.email = 'lucia.garcia@pluxee.test'
GROUP BY u.full_name, b.name
ORDER BY b.name;
