# Estructura Completa del Proyecto

```
it-equipment-management/
│
├── 📄 README.md                        # Documentación principal
├── 📄 docker-compose.yml               # Orquestación de servicios
├── 📄 .gitignore                       # Archivos a ignorar en Git
├── 📄 .env.example                     # Ejemplo de variables de entorno
├── 📄 start.sh                         # Script de inicio (Linux/Mac)
├── 📄 start.bat                        # Script de inicio (Windows)
├── 📄 ESTRUCTURA_PROYECTO.md           # Este archivo
│
├── 📁 init-db/                         # Inicialización de Base de Datos
│   └── 📄 init.sql                     # Schema SQL con datos iniciales
│
├── 📁 api-gateway/                     # API Gateway (Puerto 8000)
│   ├── 📁 app/
│   │   ├── 📄 __init__.py
│   │   └── 📄 main.py                  # Lógica del gateway
│   ├── 📄 Dockerfile
│   └── 📄 requirements.txt
│
├── 📁 services/                        # Microservicios Backend
│   │
│   ├── 📁 auth-service/               # Servicio de Autenticación (Puerto 8001)
│   │   ├── 📁 app/
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 main.py             # API endpoints de auth
│   │   │   ├── 📄 models.py           # Modelos SQLAlchemy
│   │   │   ├── 📄 auth.py             # Utilidades JWT y seguridad
│   │   │   └── 📄 database.py         # Configuración BD
│   │   ├── 📄 Dockerfile
│   │   └── 📄 requirements.txt
│   │
│   ├── 📁 equipment-service/          # Servicio de Equipos (Puerto 8002)
│   │   ├── 📁 app/
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 main.py             # CRUD de equipos
│   │   │   ├── 📄 models.py           # Equipment, Category, Location
│   │   │   └── 📄 database.py
│   │   ├── 📄 Dockerfile
│   │   └── 📄 requirements.txt
│   │
│   ├── 📁 provider-service/           # Servicio de Proveedores (Puerto 8003)
│   │   ├── 📁 app/
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 main.py             # CRUD de proveedores
│   │   │   ├── 📄 models.py           # Provider, Contract
│   │   │   └── 📄 database.py
│   │   ├── 📄 Dockerfile
│   │   └── 📄 requirements.txt
│   │
│   ├── 📁 maintenance-service/        # Servicio de Mantenimiento (Puerto 8004)
│   │   ├── 📁 app/
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 main.py             # CRUD de mantenimientos
│   │   │   ├── 📄 models.py           # Maintenance, MaintenancePart
│   │   │   └── 📄 database.py
│   │   ├── 📄 Dockerfile
│   │   └── 📄 requirements.txt
│   │
│   └── 📁 reports-service/            # Servicio de Reportes (Puerto 8005)
│       ├── 📁 app/
│       │   ├── 📄 __init__.py
│       │   ├── 📄 main.py             # Generación de reportes
│       │   └── 📄 database.py
│       ├── 📄 Dockerfile
│       └── 📄 requirements.txt
│
└── 📁 frontend/                        # Frontend Streamlit (Puerto 8501)
    ├── 📁 utils/
    │   └── 📄 api_client.py           # Cliente para consumir APIs
    ├── 📁 pages/                       # Páginas adicionales (vacío por ahora)
    ├── 📁 components/                  # Componentes reutilizables (vacío)
    ├── 📄 app.py                       # Aplicación principal Streamlit
    ├── 📄 Dockerfile
    └── 📄 requirements.txt

```

## Descripción de Componentes

### Base de Datos (MySQL)
- **Puerto**: 3306
- **Ubicación**: Contenedor Docker `it-management-mysql`
- **Schema**: `init-db/init.sql`
- **Tablas principales**:
  - `users` - Usuarios del sistema
  - `providers` - Proveedores
  - `contracts` - Contratos con proveedores
  - `equipment_categories` - Categorías de equipos
  - `locations` - Ubicaciones físicas
  - `equipment` - Inventario de equipos
  - `equipment_location_history` - Historial de ubicaciones
  - `maintenance_types` - Tipos de mantenimiento
  - `maintenance` - Registros de mantenimiento
  - `maintenance_parts` - Partes usadas en mantenimientos
  - `alerts` - Alertas y notificaciones
  - `audit_logs` - Logs de auditoría

### API Gateway (Puerto 8000)
**Función**: Punto de entrada único para todas las peticiones

**Endpoints**:
- `/health` - Estado de todos los servicios
- `/api/auth/*` - Proxy a auth-service
- `/api/equipment/*` - Proxy a equipment-service
- `/api/providers/*` - Proxy a provider-service
- `/api/maintenance/*` - Proxy a maintenance-service
- `/api/reports/*` - Proxy a reports-service

### Auth Service (Puerto 8001)
**Función**: Autenticación y autorización

**Endpoints principales**:
- `POST /login` - Inicio de sesión
- `POST /register` - Registro de usuarios (admin)
- `GET /me` - Usuario actual
- `PUT /me/password` - Cambiar contraseña
- `GET /users` - Listar usuarios
- `PUT /users/{id}` - Actualizar usuario
- `DELETE /users/{id}` - Eliminar usuario

**Tecnologías**:
- FastAPI
- JWT (python-jose)
- Bcrypt (passlib)
- SQLAlchemy

### Equipment Service (Puerto 8002)
**Función**: Gestión de inventario de equipos

**Endpoints principales**:
- **Categorías**:
  - `GET /categories` - Listar categorías
  - `POST /categories` - Crear categoría

- **Ubicaciones**:
  - `GET /locations` - Listar ubicaciones
  - `POST /locations` - Crear ubicación

- **Equipos**:
  - `GET /equipment` - Listar equipos (con filtros)
  - `POST /equipment` - Crear equipo
  - `GET /equipment/{id}` - Obtener equipo
  - `PUT /equipment/{id}` - Actualizar equipo
  - `DELETE /equipment/{id}` - Eliminar equipo
  - `POST /equipment/{id}/move` - Mover equipo a nueva ubicación
  - `GET /equipment/{id}/history` - Historial de ubicaciones

- **Estadísticas**:
  - `GET /stats/by-status` - Equipos por estado
  - `GET /stats/by-category` - Equipos por categoría
  - `GET /stats/by-location` - Equipos por ubicación

### Provider Service (Puerto 8003)
**Función**: Gestión de proveedores y contratos

**Endpoints principales**:
- **Proveedores**:
  - `GET /providers` - Listar proveedores
  - `POST /providers` - Crear proveedor
  - `GET /providers/{id}` - Obtener proveedor con contratos
  - `PUT /providers/{id}` - Actualizar proveedor
  - `DELETE /providers/{id}` - Eliminar proveedor
  - `GET /providers/{id}/purchase-history` - Historial de compras

- **Contratos**:
  - `GET /contracts` - Listar contratos
  - `POST /contracts` - Crear contrato
  - `GET /contracts/{id}` - Obtener contrato
  - `PUT /contracts/{id}` - Actualizar contrato
  - `DELETE /contracts/{id}` - Eliminar contrato

- **Estadísticas**:
  - `GET /stats/top-providers` - Top proveedores por contratos

### Maintenance Service (Puerto 8004)
**Función**: Gestión de mantenimientos preventivos y correctivos

**Endpoints principales**:
- **Tipos de Mantenimiento**:
  - `GET /types` - Listar tipos
  - `POST /types` - Crear tipo

- **Mantenimientos**:
  - `GET /maintenance` - Listar mantenimientos (con filtros)
  - `POST /maintenance` - Crear mantenimiento
  - `GET /maintenance/{id}` - Obtener mantenimiento
  - `PUT /maintenance/{id}` - Actualizar mantenimiento
  - `DELETE /maintenance/{id}` - Eliminar mantenimiento
  - `GET /equipment/{id}/maintenance-history` - Historial de equipo
  - `GET /equipment/{id}/next-maintenance` - Próximo mantenimiento
  - `GET /upcoming-maintenance` - Mantenimientos próximos
  - `GET /overdue-maintenance` - Mantenimientos vencidos

- **Estadísticas**:
  - `GET /stats/by-type` - Mantenimientos por tipo
  - `GET /stats/by-status` - Mantenimientos por estado
  - `GET /stats/costs-by-month` - Costos mensuales
  - `GET /stats/equipment-maintenance-frequency` - Equipos con más mantenimientos

### Reports Service (Puerto 8005)
**Función**: Generación de reportes y estadísticas para dashboard

**Endpoints principales**:
- **Reportes de Equipos**:
  - `GET /equipment/excel` - Exportar a Excel
  - `GET /equipment/pdf` - Exportar a PDF

- **Reportes de Mantenimiento**:
  - `GET /maintenance/excel` - Exportar a Excel
  - `GET /maintenance/pdf` - Exportar a PDF

- **Dashboard**:
  - `GET /dashboard/statistics` - Todas las estadísticas

**Tecnologías**:
- Pandas - Procesamiento de datos
- ReportLab - Generación de PDFs
- OpenPyXL - Generación de Excel
- Matplotlib/Seaborn - Gráficos

### Frontend (Puerto 8501)
**Función**: Interfaz de usuario web

**Páginas**:
1. **Login** - Autenticación de usuarios
2. **Dashboard** - Vista general con estadísticas y gráficos
3. **Equipos** - Gestión de inventario
4. **Proveedores** - Gestión de proveedores y contratos
5. **Mantenimiento** - Gestión de mantenimientos
6. **Reportes** - Exportación de datos

**Tecnologías**:
- Streamlit - Framework web
- Plotly - Gráficos interactivos
- Pandas - Manipulación de datos
- Requests - Consumo de APIs

## Flujo de Datos

```
Usuario
  │
  ▼
Frontend (Streamlit)
  │
  ▼
API Gateway (Puerto 8000)
  │
  ├──▶ Auth Service (8001) ──┐
  ├──▶ Equipment Service (8002) ──┤
  ├──▶ Provider Service (8003) ──┼──▶ MySQL
  ├──▶ Maintenance Service (8004) ──┤
  └──▶ Reports Service (8005) ──┘
```

## Puertos Utilizados

| Servicio | Puerto | URL |
|----------|--------|-----|
| Frontend | 8501 | http://localhost:8501 |
| API Gateway | 8000 | http://localhost:8000 |
| Auth Service | 8001 | http://localhost:8001 |
| Equipment Service | 8002 | http://localhost:8002 |
| Provider Service | 8003 | http://localhost:8003 |
| Maintenance Service | 8004 | http://localhost:8004 |
| Reports Service | 8005 | http://localhost:8005 |
| MySQL | 3306 | localhost:3306 |

## Volúmenes Docker

- `mysql_data`: Persistencia de datos de MySQL

## Red Docker

- `it-management-network`: Red bridge para comunicación entre servicios

## Variables de Entorno

Ver archivo `.env.example` para la lista completa de variables de entorno configurables.

## Logs

Cada servicio genera logs que pueden ser consultados con:
```bash
docker-compose logs -f [nombre-servicio]
```

## Healthchecks

Todos los servicios implementan healthchecks para monitoreo:
- Backend services: `/health` endpoint
- MySQL: `mysqladmin ping`
- Frontend: `/_stcore/health` endpoint
