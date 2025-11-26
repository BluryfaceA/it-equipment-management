# 💻 Sistema de Gestión de Equipos TI

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new?hide_repo_select=true&ref=main)

Sistema completo de gestión de equipos de tecnología con arquitectura de microservicios.

## 🚀 Inicio Rápido en Codespaces

### 1️⃣ Haz clic en el badge de arriba "Open in GitHub Codespaces"

### 2️⃣ Espera a que se configure (5-10 minutos)

### 3️⃣ Accede al sistema
- El frontend se abrirá automáticamente en el puerto 8501
- Usuario: `admin` | Contraseña: `admin123`

## ✨ Características

- 🔐 **Autenticación y autorización** con JWT
- 💻 **Gestión completa de equipos** TI
- 🏢 **Administración de proveedores** y contratos
- 🔧 **Sistema de mantenimiento** preventivo y correctivo
- 📊 **Dashboard** con estadísticas en tiempo real
- 📄 **Generación de reportes** en PDF y Excel
- 🎯 **Arquitectura de microservicios** escalable

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (Streamlit)                  │
│                     Puerto: 8501                         │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│                   API Gateway                            │
│                   Puerto: 8000                           │
└──┬──────┬──────┬───────────┬──────────┬─────────────────┘
   │      │      │           │          │
   ▼      ▼      ▼           ▼          ▼
┌────┐ ┌────┐ ┌────┐    ┌────────┐ ┌────────┐
│Auth│ │Eqp │ │Prv │    │Maint   │ │Reports │
│8001│ │8002│ │8003│    │8004    │ │8005    │
└──┬─┘ └──┬─┘ └──┬─┘    └───┬────┘ └───┬────┘
   │      │      │           │          │
   └──────┴──────┴───────────┴──────────┘
                  │
          ┌───────▼────────┐
          │  MySQL:3306    │
          └────────────────┘
```

## 🛠️ Tecnologías

- **Backend**: FastAPI (Python)
- **Frontend**: Streamlit
- **Base de Datos**: MySQL 8.0
- **Contenedores**: Docker & Docker Compose
- **Reportes**: ReportLab (PDF), OpenPyXL (Excel)

## 📦 Microservicios

| Servicio | Puerto | Descripción |
|----------|--------|-------------|
| **Frontend** | 8501 | Interfaz de usuario con Streamlit |
| **API Gateway** | 8000 | Punto de entrada unificado |
| **Auth Service** | 8001 | Autenticación y autorización |
| **Equipment Service** | 8002 | Gestión de equipos |
| **Provider Service** | 8003 | Gestión de proveedores |
| **Maintenance Service** | 8004 | Gestión de mantenimientos |
| **Reports Service** | 8005 | Generación de reportes |
| **MySQL** | 3306 | Base de datos |

## 🎯 Funcionalidades Principales

### Dashboard
- Estadísticas en tiempo real
- Gráficos interactivos con Plotly
- KPIs principales del sistema
- Alertas de mantenimientos vencidos

### Gestión de Equipos
- ✅ CRUD completo de equipos
- ✅ Categorización y ubicación
- ✅ Historial de mantenimientos
- ✅ Control de garantías
- ✅ Búsqueda y filtros avanzados

### Gestión de Mantenimientos
- ✅ CRUD completo de mantenimientos
- ✅ Mantenimientos preventivos y correctivos
- ✅ Programación de tareas
- ✅ Alertas de vencimiento
- ✅ Registro de técnicos y costos
- ✅ Historial detallado

### Gestión de Proveedores
- ✅ CRUD completo de proveedores
- ✅ Información de contacto
- ✅ Contratos y servicios
- ✅ Estadísticas por proveedor

### Reportes
- 📊 Reportes de inventario (PDF/Excel)
- 📊 Reportes de mantenimiento (PDF/Excel)
- 📊 Estadísticas personalizables
- 📊 Exportación de datos

## 🔐 Seguridad

- Autenticación JWT
- Validación de datos con Pydantic
- Gestión de sesiones
- Protección CORS configurada
- Variables de entorno para credenciales

## 📖 Documentación Adicional

- [`CODESPACES_SETUP.md`](CODESPACES_SETUP.md) - Guía detallada de Codespaces
- [`DEPLOY_INSTRUCTIONS.md`](DEPLOY_INSTRUCTIONS.md) - Instrucciones de despliegue
- [`ESTRUCTURA_PROYECTO.md`](ESTRUCTURA_PROYECTO.md) - Estructura del proyecto

## 🚀 Despliegue Local

```bash
# Clonar repositorio
git clone https://github.com/TU_USUARIO/it-equipment-management.git
cd it-equipment-management

# Iniciar servicios
docker-compose up -d

# Acceder al sistema
# Frontend: http://localhost:8501
# API Docs: http://localhost:8000/docs
```

## 🌐 Despliegue en la Nube

Soporta despliegue en:
- ✅ GitHub Codespaces (Recomendado para desarrollo)
- ✅ Railway.app
- ✅ Render.com
- ✅ DigitalOcean App Platform
- ✅ AWS ECS
- ✅ Google Cloud Run
- ✅ Azure Container Instances

Ver [`DEPLOY_INSTRUCTIONS.md`](DEPLOY_INSTRUCTIONS.md) para detalles.

## 🔧 Comandos Útiles

```bash
# Ver estado de servicios
docker-compose ps

# Ver logs
docker-compose logs -f

# Reiniciar un servicio
docker-compose restart frontend

# Reconstruir después de cambios
docker-compose up -d --build

# Detener todo
docker-compose down
```

## 📊 Base de Datos

### Tablas Principales
- `users` - Usuarios del sistema
- `equipment` - Inventario de equipos
- `equipment_categories` - Categorías de equipos
- `locations` - Ubicaciones
- `maintenance` - Registros de mantenimiento
- `providers` - Proveedores
- `contracts` - Contratos con proveedores

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT.

## 👨‍💻 Autor

Desarrollado con ❤️ usando Claude Code

## 🆘 Soporte

¿Problemas? Abre un [issue](https://github.com/TU_USUARIO/it-equipment-management/issues)

---

**⭐ Si te gusta este proyecto, dale una estrella en GitHub!**
