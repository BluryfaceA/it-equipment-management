# Sistema de Gestión de Equipos de TI - Universidad

Sistema completo de gestión de equipos de TI para universidades públicas, desarrollado con arquitectura de microservicios.

## Tabla de Contenidos

- [Características](#características)
- [Arquitectura](#arquitectura)
- [Stack Tecnológico](#stack-tecnológico)
- [Requisitos Previos](#requisitos-previos)
- [Instalación y Despliegue](#instalación-y-despliegue)
- [Uso de la Aplicación](#uso-de-la-aplicación)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [API Documentation](#api-documentation)
- [Configuración](#configuración)
- [Mantenimiento](#mantenimiento)

## Características

### Gestión de Proveedores
- Registro y actualización de información de proveedores
- Gestión de contratos
- Historial de compras
- Seguimiento de proveedores activos/inactivos

### Gestión de Equipos
- Inventario completo de equipos de TI
- Registro con código de activo único
- Categorización de equipos
- Historial de ubicaciones
- Seguimiento de garantías
- Estado operativo

### Gestión de Mantenimiento
- Mantenimientos preventivos y correctivos
- Calendario de mantenimientos programados
- Historial de reparaciones
- Seguimiento de costos
- Alertas de mantenimientos próximos y vencidos
- Registro de partes y repuestos utilizados

### Análisis y Reportes
- Dashboard con estadísticas en tiempo real
- Gráficos de barras, líneas y torta
- Métricas clave: equipos por ubicación, estado, antigüedad
- Costos de mantenimiento por mes
- Exportación de reportes en PDF y Excel

### Autenticación y Seguridad
- Sistema de login con JWT
- Control de acceso basado en roles:
  - **Admin**: Acceso completo al sistema
  - **Technician**: Gestión de equipos y mantenimientos
  - **Viewer**: Solo lectura

## Arquitectura

El sistema está diseñado con arquitectura de microservicios:

```
┌─────────────────┐
│   Frontend      │
│   (Streamlit)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   API Gateway   │
│   (FastAPI)     │
└────────┬────────┘
         │
    ┌────┴────┬────────┬────────┬────────┐
    ▼         ▼        ▼        ▼        ▼
┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
│  Auth  │ │Equipos │ │Provee- │ │Manten- │ │Reportes│
│Service │ │Service │ │dores   │ │imiento │ │Service │
└───┬────┘ └───┬────┘ └───┬────┘ └───┬────┘ └───┬────┘
    │          │          │          │          │
    └──────────┴──────────┴──────────┴──────────┘
                         │
                    ┌────▼────┐
                    │  MySQL  │
                    └─────────┘
```

### Microservicios

1. **Auth Service** (Puerto 8001)
   - Autenticación de usuarios
   - Gestión de tokens JWT
   - Control de acceso por roles

2. **Equipment Service** (Puerto 8002)
   - Gestión de equipos
   - Categorías y ubicaciones
   - Historial de movimientos

3. **Provider Service** (Puerto 8003)
   - Gestión de proveedores
   - Contratos
   - Historial de compras

4. **Maintenance Service** (Puerto 8004)
   - Gestión de mantenimientos
   - Programación
   - Alertas y notificaciones

5. **Reports Service** (Puerto 8005)
   - Generación de reportes
   - Estadísticas
   - Exportación PDF/Excel

6. **API Gateway** (Puerto 8000)
   - Punto único de entrada
   - Enrutamiento de peticiones
   - Health checks

7. **Frontend** (Puerto 8501)
   - Interfaz de usuario Streamlit
   - Dashboard interactivo
   - Formularios de gestión

## Stack Tecnológico

### Backend
- **Python 3.11**
- **FastAPI**: Framework para APIs REST
- **SQLAlchemy**: ORM para base de datos
- **PyMySQL**: Conector MySQL
- **JWT**: Autenticación y autorización
- **Pandas**: Procesamiento de datos para reportes
- **ReportLab**: Generación de PDFs
- **OpenPyXL**: Generación de Excel

### Frontend
- **Streamlit**: Framework de aplicaciones web
- **Plotly**: Visualización de datos
- **Pandas**: Manipulación de datos

### Base de Datos
- **MySQL 8.0**: Sistema de gestión de base de datos

### Infraestructura
- **Docker**: Contenedorización
- **Docker Compose**: Orquestación de contenedores

## Requisitos Previos

- Docker (versión 20.10 o superior)
- Docker Compose (versión 2.0 o superior)
- 4GB RAM mínimo
- 10GB espacio en disco

## Instalación y Despliegue

### 1. Clonar o descargar el proyecto

```bash
cd it-equipment-management
```

### 2. Configurar variables de entorno (Opcional)

Puedes modificar las credenciales de la base de datos en `docker-compose.yml`:

```yaml
environment:
  MYSQL_ROOT_PASSWORD: admin
  MYSQL_DATABASE: it_management
  MYSQL_USER: ituser
  MYSQL_PASSWORD: itpassword
```

### 3. Construir e iniciar los contenedores

```bash
docker-compose up --build -d
```

Este comando:
- Construirá las imágenes Docker para todos los servicios
- Creará la red de comunicación entre contenedores
- Iniciará todos los servicios en modo detached
- Inicializará la base de datos con el esquema

### 4. Verificar que todos los servicios estén corriendo

```bash
docker-compose ps
```

Deberías ver todos los servicios en estado "Up":

```
NAME                  STATUS
auth-service          Up
equipment-service     Up
provider-service      Up
maintenance-service   Up
reports-service       Up
api-gateway           Up
frontend-streamlit    Up
it-management-mysql   Up (healthy)
```

### 5. Verificar la salud de los servicios

Visita http://localhost:8000/health para ver el estado de todos los microservicios.

### 6. Acceder a la aplicación

Abre tu navegador y visita: **http://localhost:8501**

## Uso de la Aplicación

### Credenciales de Acceso Iniciales

| Usuario | Contraseña | Rol |
|---------|-----------|-----|
| admin | admin123 | Administrador |
| tecnico1 | admin123 | Técnico |
| viewer1 | admin123 | Viewer |

### Navegación

1. **Dashboard** 📊
   - Vista general del sistema
   - Estadísticas en tiempo real
   - Gráficos interactivos
   - Alertas de mantenimiento

2. **Equipos** 💻
   - Lista de inventario
   - Búsqueda y filtros
   - Registro de nuevos equipos
   - Actualización de información

3. **Proveedores** 🏢
   - Lista de proveedores
   - Registro de nuevos proveedores
   - Gestión de contratos
   - Historial de compras

4. **Mantenimiento** 🔧
   - Historial de mantenimientos
   - Mantenimientos próximos
   - Mantenimientos vencidos
   - Programación de nuevos mantenimientos

5. **Reportes** 📄
   - Exportar inventario de equipos (Excel/PDF)
   - Exportar historial de mantenimientos (Excel/PDF)
   - Reportes personalizados

### Flujo de Trabajo Típico

#### Registrar un Nuevo Equipo

1. Ir a **Equipos** → **Agregar Equipo**
2. Completar información:
   - Código de Activo (único)
   - Nombre del equipo
   - Marca y Modelo
   - Categoría
   - Fecha de compra
   - Precio
3. Guardar

#### Programar un Mantenimiento

1. Ir a **Mantenimiento**
2. Hacer clic en **Agregar Mantenimiento**
3. Seleccionar equipo
4. Tipo: Preventivo o Correctivo
5. Fecha programada
6. Técnico responsable
7. Guardar

#### Generar Reporte

1. Ir a **Reportes**
2. Seleccionar tipo de reporte
3. Aplicar filtros (opcional)
4. Hacer clic en **Descargar Excel** o **Descargar PDF**
5. Guardar archivo

## Estructura del Proyecto

```
it-equipment-management/
├── api-gateway/                 # API Gateway
│   ├── app/
│   │   ├── __init__.py
│   │   └── main.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── services/
│   ├── auth-service/           # Servicio de Autenticación
│   │   ├── app/
│   │   │   ├── __init__.py
│   │   │   ├── main.py
│   │   │   ├── models.py
│   │   │   ├── auth.py
│   │   │   └── database.py
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   │
│   ├── equipment-service/      # Servicio de Equipos
│   │   ├── app/
│   │   │   ├── __init__.py
│   │   │   ├── main.py
│   │   │   ├── models.py
│   │   │   └── database.py
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   │
│   ├── provider-service/       # Servicio de Proveedores
│   │   ├── app/
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   │
│   ├── maintenance-service/    # Servicio de Mantenimiento
│   │   ├── app/
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   │
│   └── reports-service/        # Servicio de Reportes
│       ├── app/
│       ├── Dockerfile
│       └── requirements.txt
│
├── frontend/                    # Frontend Streamlit
│   ├── pages/
│   ├── utils/
│   │   └── api_client.py
│   ├── components/
│   ├── app.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── init-db/                     # Scripts de inicialización DB
│   └── init.sql
│
├── docker-compose.yml          # Orquestación de servicios
└── README.md                   # Esta documentación
```

## API Documentation

Cada microservicio expone su documentación interactiva de API:

- **Auth Service**: http://localhost:8001/docs
- **Equipment Service**: http://localhost:8002/docs
- **Provider Service**: http://localhost:8003/docs
- **Maintenance Service**: http://localhost:8004/docs
- **Reports Service**: http://localhost:8005/docs
- **API Gateway**: http://localhost:8000/docs

## Configuración

### Cambiar Puerto de un Servicio

Editar `docker-compose.yml`:

```yaml
services:
  frontend:
    ports:
      - "9000:8501"  # Cambia el puerto externo
```

### Cambiar Credenciales de Base de Datos

1. Editar `docker-compose.yml`:
```yaml
mysql:
  environment:
    MYSQL_ROOT_PASSWORD: nueva_contraseña
```

2. Actualizar la configuración en cada servicio que use la BD

### Habilitar Modo Debug

En cada Dockerfile, cambiar:
```dockerfile
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]
```

## Mantenimiento

### Ver Logs de un Servicio

```bash
docker-compose logs -f [nombre-servicio]

# Ejemplo:
docker-compose logs -f auth-service
```

### Reiniciar un Servicio

```bash
docker-compose restart [nombre-servicio]

# Ejemplo:
docker-compose restart equipment-service
```

### Detener Todos los Servicios

```bash
docker-compose down
```

### Detener y Eliminar Volúmenes (CUIDADO: Elimina la BD)

```bash
docker-compose down -v
```

### Backup de Base de Datos

```bash
docker exec it-management-mysql mysqldump -u root -prootpassword it_management > backup.sql
```

### Restaurar Base de Datos

```bash
docker exec -i it-management-mysql mysql -u root -prootpassword it_management < backup.sql
```

### Actualizar un Servicio

```bash
docker-compose up -d --no-deps --build [nombre-servicio]

# Ejemplo:
docker-compose up -d --no-deps --build frontend
```

## Solución de Problemas

### El Frontend no se conecta a la API

1. Verificar que el API Gateway esté corriendo:
```bash
docker-compose ps api-gateway
```

2. Verificar la variable de entorno:
```bash
docker-compose exec frontend env | grep API_GATEWAY_URL
```

### Error de conexión a MySQL

1. Esperar a que MySQL esté completamente iniciado:
```bash
docker-compose logs mysql | grep "ready for connections"
```

2. Verificar health check:
```bash
docker-compose ps mysql
```

### Servicio no inicia correctamente

1. Ver logs detallados:
```bash
docker-compose logs [nombre-servicio]
```

2. Reconstruir imagen:
```bash
docker-compose build --no-cache [nombre-servicio]
docker-compose up -d [nombre-servicio]
```

## Seguridad

### Recomendaciones para Producción

1. **Cambiar Contraseñas**: Modificar todas las contraseñas por defecto
2. **JWT Secret Key**: Usar una clave secreta fuerte y única
3. **HTTPS**: Implementar certificados SSL/TLS
4. **Firewall**: Configurar reglas de firewall apropiadas
5. **Backups**: Implementar backups automáticos de la base de datos
6. **Logs**: Configurar sistema de logging centralizado
7. **Monitoreo**: Implementar monitoreo de servicios (Prometheus/Grafana)

## Contribución

Para contribuir al proyecto:

1. Fork del repositorio
2. Crear una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit de cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir un Pull Request

## Licencia

Este proyecto es de código abierto y está disponible bajo la licencia MIT.

## Soporte

Para soporte técnico o preguntas:
- Email: soporte@universidad.edu
- Issues: GitHub Issues del proyecto

## Autores

Desarrollado para la gestión eficiente de equipos de TI en universidades públicas.

---

**Versión:** 1.0.0
**Última Actualización:** 2024
