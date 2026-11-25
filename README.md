<img width="2172" height="724" alt="Plataforma Pluxee de beneficios laborales" src="https://github.com/user-attachments/assets/fcad27ef-6ff8-46df-88c8-d176b007d153" />




# Pluxee Employee Benefits

Monorepo con el frontend y el backend de la aplicación de beneficios para empleados.

## Estructura

```
pluxee-employee-benefits/
├── frontend/          ← React 19 + Vite (JavaScript)
│   └── src/
│       ├── components/    ← Atomic Design (atoms, molecules, organisms, templates)
│       ├── pages/         ← páginas de la app
│       ├── hooks/         ← hooks personalizados
│       ├── services/      ← cliente de la API
│       ├── styles/        ← estilos globales
│       └── assets/        ← imágenes y estáticos
├── backend/           ← Python + FastAPI (API REST)
│   └── app/
│       ├── main.py          ← instancia FastAPI + middlewares + handlers
│       ├── server.py        ← arranque del servidor (uvicorn)
│       ├── core/            ← infraestructura transversal
│       │   ├── config.py        ← variables de entorno (pydantic-settings)
│       │   ├── database.py      ← engine + sesión PostgreSQL (SQLAlchemy 2.0)
│       │   └── errors.py        ← AppError y errores centralizados
│       ├── routes/          ← endpoints (capa API)
│       ├── schemas/         ← validación de entrada/salida (Pydantic)
│       ├── services/        ← lógica de negocio
│       └── models/          ← queries SQL / acceso a datos
│   └── alembic/           ← migraciones de BD (Alembic)
├── package.json       ← scripts de conveniencia
└── README.md
```

Flujo de una petición:

```
routes → schema (Pydantic) → service → model (SQL) → PostgreSQL
```

## Requisitos

- Python 3.11+ (probado con 3.14)
- npm (solo para el frontend)
- Cuenta Neon (la BD compartida vive en la nube; ver [Base de datos compartida](#base-de-datos-compartida-neon))

## Puesta en marcha

```bash
# 1. Frontend
npm install --prefix frontend

# 2. Backend: entorno virtual + dependencias
cd backend
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt   # Linux/macOS: .venv/bin/pip install -r requirements.txt
copy .env.example .env                          # Linux/macOS: cp .env.example .env
cd ..

# 3. Arrancar (cada servicio en su terminal)
npm run dev        # frontend → http://localhost:5173
npm run dev:api    # backend  → http://localhost:4000  (docs en /docs)
```

El frontend tiene configurado un **proxy** en `vite.config.js`: las llamadas a `/api/*` se redirigen al backend en el puerto `4000`.

## Base de datos compartida (Neon)

La BD es **Postgres 18 en la nube (Neon)**: todos los compañeros trabajan
contra los mismos datos desde su máquina local. La CLI de Neon escribe las
credenciales en `.env.local` (raíz del repo) y `backend/app/core/config.py` la
detecta automáticamente — no hay que copiar nada a mano.

**Proyecto**: `pluxee` (`fancy-glitter-51900277`) · **rama**: `production` ·
**región**: `aws-us-east-2` (Ohio, EE. UU.)

### Puesta en marcha de un compañero

```bash
# 1. CLI de Neon (solo la primera vez; sin npm global usa `npx neon@latest`)
npm i -g neon@latest

# 2. Login en el navegador (sesión propia: nunca compartas la cuenta)
neon login

# 3. Desde la raíz del repo: baja DATABASE_URL a .env.local
neon env pull --project-id fancy-glitter-51900277 --branch production

# 4. Arrancar como siempre
npm run dev        # frontend → http://localhost:5173
npm run dev:api    # backend  → http://localhost:4000 (contra Neon)
```

Comprobación: abre `http://localhost:4000/api/health` →
`{"status":"ok","database":"up"}`.

### Seguridad de las claves

- `.env.local` (raíz) y `backend/.env` están en `.gitignore`: **nunca se suben**
  al repo. No pegues credenciales en código, commits ni chats.
- Cada persona usa su propia sesión (`neon login`). Si prefieres una API key:
  `neon profile create work --api-key <KEY>` — guárdala fuera del repo.
- Para dar de alta a alguien, invítalo desde Neon Console → **Members** en vez
  de enviar la connection string.

### Comportamiento

- Sin `.env.local`, el backend cae a la Postgres local (`DB_*` en
  `backend/.env`) como fallback.
- Las migraciones de **Alembic** usan la conexión directa
  (`DATABASE_URL_UNPOOLED`) automáticamente:
  `cd backend && .venv\Scripts\python -m alembic upgrade head`.
- `neon.ts` define la política de ramas (las ramas no-default expiran a los
  7 días); se aplica con `neon deploy`.

## Datos de prueba (seed)

`backend/seed.sql` contiene datos inventados (3 departamentos, 7 usuarios,
presupuestos de noviembre de 2026, gastos y justificantes de ejemplo) para
desarrollo, pruebas y demo — **nunca** para producción. Contraseña de prueba
de todos los usuarios: `Prueba123!`.

```bash
npm run seed              # si la BD está vacía
npm run seed -- --reset   # borra los datos (TRUNCATE) y vuelve a sembrar
```

El runner (`backend/scripts/seed.py`) usa la misma conexión que la app, así
que sirve igual para **Neon** que para la **Postgres local**. Al terminar
comprueba los recuentos de las 13 tablas y el saldo de Lucía: debe dar
**Comida = 70,00** y **Transporte = 10,00** (`SEED RESULT: PASS`).

También se puede ejecutar a mano en **pgAdmin** (F5) sobre una BD local ya
migrada con `alembic upgrade head`: pega el contenido de `backend/seed.sql`.

## Checklist del nuevo colaborador

Copia y pega en orden (los pasos 4 y 8 son los que suelen olvidarse):

```bash
# 1. Clonar
git clone https://github.com/simonlopez25/pluxee-employee-benefits.git
cd pluxee-employee-benefits

# 2. Frontend
npm install --prefix frontend

# 3. Backend (Linux/macOS: .venv/bin/pip y "cp" en lugar de "copy")
cd backend
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
copy .env.example .env
cd ..

# 4. BD compartida en Neon — pide acceso antes por Neon Console → Members
npm i -g neon@latest
neon login
neon env pull --project-id fancy-glitter-51900277 --branch production   # en la raíz

# 5. Arrancar (cada servicio en su terminal)
npm run dev        # frontend → http://localhost:5173
npm run dev:api    # backend  → http://localhost:4000

# 6. Verificar: abre http://localhost:4000/api/health
#    → {"status":"ok","database":"up"}

# 7. Tests (Linux/macOS: .venv/bin/python)
cd backend
.venv\Scripts\python -m pytest
cd ..

# 8. Guardian de commits — ANTES de tu primer commit (no viaja con el repo)
pip install pre-commit
pre-commit install

# 9. Commit y push (el guardian exige inglés: feat(scope): minúsculas, sin punto)
git add <archivos>
git commit -m "feat(scope): describe your change"
git push
```

> ⚠️ **Nunca subas** `.env.local` ni `backend/.env` (ya están en `.gitignore`)
> ni pegues claves en el código, los commits ni los chats.
> **¿Tocas `app/models/`?** Aplica y verifica migraciones desde `backend/`:
> `.venv\Scripts\python -m alembic upgrade head` y después
> `.venv\Scripts\python -m alembic check` (debe quedar sin cambios).
> **¿Mantenedor que usa `neon deploy`?** Ejecuta también `npm install` en la
> raíz (dependencias con las que se evalúa `neon.ts`).

## Scripts disponibles

| Script | Descripción |
|--------|-------------|
| `npm run dev` | Arranca el frontend (Vite) |
| `npm run dev:api` | Arranca el backend (uvicorn con reload) |
| `npm run build` | Build de producción del frontend |
| `npm run lint` | Lint del frontend (ESLint) |
| `npm run start:api` | Arranca el backend en producción |

Tests del backend:

```bash
cd backend
.venv\Scripts\python -m pytest   # Linux/macOS: .venv/bin/python -m pytest
```

Al agregar una dependencia nueva al backend:

```bash
cd backend
.venv\Scripts\pip install <paquete>
.venv\Scripts\pip freeze > requirements.txt
```

Migraciones de base de datos con **Alembic**: ver [backend/README.md](backend/README.md).

## Metodología UI y Frontend

El frontend sigue **Atomic Design** organizado en carpetas modulares por componente (cada componente agrupa su `.jsx`, su `.css` y su `index.js`).

Ver detalle en [frontend/src/components/README.md](frontend/src/components/README.md).

### Catálogo de Beneficios (HU-09 / PEB-48)

La pantalla principal de administración de beneficios incluye:

1. **Barra de navegación lateral (`AdminSidebar`):**
   * Estilo corporativo (Índigo `#221C46` y verde activo `#00EB5E`).
   * Enlaces directos vía `react-router-dom`: `/dashboard`, `/groups`, `/budgets`, `/catalog`, `/assignments`, `/expenses`.
   * Botón para alternar rol ("Ver como empleado") y tarjeta de perfil de usuario.

2. **Catálogo de beneficios (`BenefitsCatalogSection`):**
   * Encabezado con título descriptivo y botón de acción principal `+ Nuevo beneficio`.
   * Filtros rápidos por estado con contadores dinámicos: *Todos*, *Activos*, *Inactivos*, *Básicos*.
   * Cuadrícula responsiva de tarjetas (`BenefitCard`) con badges de estado, atenuación visual para inactivos, acción rápida de activación/desactivación sin borrado físico y botón de edición.
   * Modal de formulario (`BenefitFormModal`) para crear y editar beneficios con validación en cliente y captura de errores del backend (especialmente `409 Conflict` cuando el nombre ya existe).
   * Contenedor inferior preparado para la integración de paquetes (**HU-10**).

### Gestión de Presupuestos (HU-11 / PEB-19)

La vista de control presupuestario (`/budgets`) permite gestionar techos de gasto y reparto por departamento:

1. **Selector de Período y Resumen Global (`GlobalBudgetSummary`):**
   * Navegación por mes (`YYYY-MM-01`) que carga por defecto en el mes actual.
   * Aviso explicativo sobre la naturaleza no acumulativa del saldo mensual.
   * Cuatro métricas consolidadas: Presupuesto Global, Repartido a Grupos, Sin Repartir (Disponible) y Porcentaje Consolidado Repartido.
   * Modal (`GlobalBudgetModal`) para ajustar el techo global, impidiendo reducciones por debajo de lo ya asignado (`409 Conflict`).

2. **Tabla Comparativa de Departamentos (`DepartmentBudgetsTable`):**
   * Fusión reactiva de todos los departamentos activos con las asignaciones del mes.
   * Columnas: Grupo, Asignado, Disponible, Consumido, Barra de progreso de Uso del asignado (%) y Acciones.
   * Badges de estado (*"Sin asignar"*) para departamentos aún no dotados de presupuesto en el mes seleccionado.
   * Modal (`DepartmentBudgetModal`) para asignar o reajustar presupuesto departamental (limitado por el remanente global) y definir referencias orientativas por beneficio con validación informativa.

### Gestión de Empleados (HU-08 / PEB-16)

La vista de administración de plantilla (`/employees`) permite la gestión de usuarios y su ciclo de vida:

1. **Listado de Plantilla (`EmployeesPage`):**
   * Tabla con nombre completo, correo, rol (badge Administrador / Empleado), departamento asignado, estado (Activo / Inactivo) y fecha de baja lógica.
   * Carga paralela de usuarios y departamentos mediante `userService` y `departmentService`.

2. **Edición de Empleados (`EmployeeFormModal`):**
   * Actualización parcial (`PATCH /api/users/{id}`) con validaciones en cliente y backend.
   * Cumplimiento de integridad: los administradores no tienen departamento asociado y los empleados requieren departamento obligatorio.
   * Seguridad: un administrador no puede rebajar su propio rol para evitar el bloqueo del sistema.

3. **Baja Lógica (`DeactivateConfirmModal`):**
   * Desactivación segura (`PATCH /api/users/{id}/deactivate`): marca `is_active = False` y registra la fecha de baja en UTC sin borrar el registro ni perder históricos.
   * Protección contra auto-baja: el administrador actual no puede darse de baja a sí mismo.
   * Revocación de sesión en caliente: si un usuario dado de baja realiza una petición, `http.js` captura el error 403 `account_inactive`, borra el token de sesión y lo redirige a login.

### Flujo de comunicación completa

```text
Frontend (localhost:5173) 
  ──(Peticiones fetch /api/benefits, /api/budgets, /api/users)──> Vite Proxy 
  ──(Reenvío puerto 4000)──────────────────────────────────────> FastAPI (app.routes.benefit, budget, users) 
  ──(SQLAlchemy 2.0)───────────────────────────────────────────> PostgreSQL (Neon en aws-us-east-2)
```

------------------
## 👩‍💻 Equipo de desarrollo

<table align="center">
  <tr>
    <td align="center" width="20%">
      <a href="https://github.com/simonlopez25">
        <img src="https://github.com/simonlopez25.png" width="90" height="90" alt="Simón López" />
      </a>
      <br />
      <sub><b>Simón López</b></sub>
      <br />
      <a href="https://github.com/simonlopez25">GitHub</a>
    </td>
    <td align="center" width="20%">
      <a href="https://github.com/apariciodiazpatricia-cell">
        <img src="https://github.com/apariciodiazpatricia-cell.png" width="90" height="90" alt="Patricia Aparicio" />
      </a>
      <br />
      <sub><b>Patricia Aparicio</b></sub>
      <br />
      <a href="https://github.com/apariciodiazpatricia-cell">GitHub</a>
    </td>
    <td align="center" width="20%">
      <a href="https://github.com/oscarperezGR">
        <img src="https://github.com/oscarperezGR.png" width="90" height="90" alt="Óscar Pérez" />
      </a>
      <br />
      <sub><b>Óscar Pérez</b></sub>
      <br />
      <a href="https://github.com/oscarperezGR">GitHub</a>
    </td>
    <td align="center" width="20%">
      <a href="https://github.com/Marisa-Ruiz">
        <img src="https://github.com/Marisa-Ruiz.png" width="90" height="90" alt="Marisa Ruiz Torres" />
      </a>
      <br />
      <sub><b>Marisa Ruiz Torres</b></sub>
      <br />
      <a href="https://github.com/Marisa-Ruiz">GitHub</a>
    </td>
    <td align="center" width="20%">
      <a href="https://github.com/margaritabellidoroig">
        <img src="https://github.com/margaritabellidoroig.png" width="90" height="90" alt="Margarita Bellido" />
      </a>
      <br />
      <sub><b>Margarita Bellido</b></sub>
      <br />
      <a href="https://github.com/margaritabellidoroig">GitHub</a>
    </td>
  </tr>
</table>
