# 🚀 Configuración para GitHub Codespaces

Este documento describe cómo ejecutar el Sistema de Gestión de Equipos TI en GitHub Codespaces.

## 📋 Requisitos Previos

- Una cuenta de GitHub
- Acceso a GitHub Codespaces (incluido en GitHub Free, Pro, Team y Enterprise)

## 🎯 Inicio Rápido

### Opción 1: Desde GitHub (Recomendado)

1. **Sube tu repositorio a GitHub**
   ```bash
   cd it-equipment-management
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/TU_USUARIO/it-equipment-management.git
   git push -u origin main
   ```

2. **Abre en Codespaces**
   - Ve a tu repositorio en GitHub
   - Haz clic en el botón verde "Code"
   - Selecciona la pestaña "Codespaces"
   - Haz clic en "Create codespace on main"

3. **Espera a que el entorno se configure**
   - Codespaces construirá automáticamente todos los contenedores Docker
   - Esto puede tomar 5-10 minutos la primera vez

4. **Accede a la aplicación**
   - Frontend (Streamlit): El puerto 8501 se abrirá automáticamente
   - API Gateway: Disponible en el puerto 8000
   - Usuario por defecto: `admin` / `admin123`

### Opción 2: URL Directa

Puedes crear un Codespace directamente usando esta URL:
```
https://github.com/codespaces/new?hide_repo_select=true&ref=main&repo=TU_REPOSITORIO_ID
```

## 🔧 Configuración Manual

Si necesitas iniciar los servicios manualmente:

```bash
# En el terminal de Codespaces
docker-compose up -d

# Ver logs
docker-compose logs -f

# Verificar servicios
docker-compose ps
```

## 🌐 Puertos Expuestos

El sistema expone los siguientes puertos:

| Puerto | Servicio | Descripción | Auto-abrir |
|--------|----------|-------------|------------|
| 8501 | Frontend | Interfaz Streamlit | ✅ Sí |
| 8000 | API Gateway | Gateway principal | ⚠️ Notificar |
| 8001 | Auth Service | Autenticación | ❌ No |
| 8002 | Equipment Service | Gestión de equipos | ❌ No |
| 8003 | Provider Service | Gestión de proveedores | ❌ No |
| 8004 | Maintenance Service | Gestión de mantenimiento | ❌ No |
| 8005 | Reports Service | Reportes y estadísticas | ❌ No |
| 3306 | MySQL | Base de datos | ❌ No |

## 🔐 Credenciales por Defecto

### Base de Datos MySQL
- **Usuario Root**: `root`
- **Contraseña Root**: `admin`
- **Base de Datos**: `it_management`
- **Usuario App**: `ituser`
- **Contraseña App**: `itpassword`

### Aplicación Web
- **Usuario**: `admin`
- **Contraseña**: `admin123`

⚠️ **IMPORTANTE**: Cambia estas credenciales antes de usar en producción.

## 📦 Estructura del Proyecto

```
it-equipment-management/
├── .devcontainer/
│   └── devcontainer.json      # Configuración de Codespaces
├── services/
│   ├── auth-service/          # Servicio de autenticación
│   ├── equipment-service/     # Servicio de equipos
│   ├── provider-service/      # Servicio de proveedores
│   ├── maintenance-service/   # Servicio de mantenimiento
│   └── reports-service/       # Servicio de reportes
├── api-gateway/               # Gateway API
├── frontend/                  # Interfaz Streamlit
├── init-db/                   # Scripts de inicialización DB
├── docker-compose.yml         # Configuración Docker
└── .env                       # Variables de entorno
```

## 🛠️ Comandos Útiles

### Gestión de Contenedores
```bash
# Iniciar todos los servicios
docker-compose up -d

# Detener todos los servicios
docker-compose down

# Reiniciar un servicio específico
docker-compose restart frontend

# Ver logs de un servicio
docker-compose logs -f frontend

# Reconstruir un servicio
docker-compose up -d --build maintenance-service
```

### Debugging
```bash
# Verificar estado de contenedores
docker-compose ps

# Acceder a un contenedor
docker exec -it frontend-streamlit bash

# Ver logs de MySQL
docker-compose logs mysql

# Verificar conectividad de red
docker network inspect it-equipment-management_it-management-network
```

## 🔄 Actualizar la Aplicación

Después de hacer cambios en el código:

```bash
# Si modificaste el código Python
docker-compose restart frontend

# Si modificaste requirements.txt o Dockerfile
docker-compose up -d --build frontend

# Para reconstruir todo
docker-compose down
docker-compose up -d --build
```

## 🌍 Acceso desde Internet

Codespaces hace que tus puertos sean accesibles mediante URLs únicas:

1. **Ver puertos abiertos**:
   - Haz clic en la pestaña "Ports" en la parte inferior de VS Code

2. **Compartir puerto**:
   - Haz clic derecho en el puerto
   - Selecciona "Port Visibility" → "Public"

3. **Copiar URL**:
   - Haz clic en el icono de "copiar" junto al puerto
   - Comparte esta URL con otros usuarios

## ⚡ Optimización de Rendimiento

### Recursos Recomendados
- **Máquina**: 4-core, 8 GB RAM
- **Tiempo de construcción inicial**: ~10 minutos
- **Tiempo de inicio posterior**: ~2 minutos

### Acelerar el Inicio
```bash
# Prebuild: Configura un prebuild en GitHub para que los Codespaces
# se inicien más rápido. Ve a Settings → Codespaces → Prebuilds
```

## 🐛 Solución de Problemas

### El frontend no se carga
```bash
# Verifica que todos los servicios estén corriendo
docker-compose ps

# Reinicia el frontend
docker-compose restart frontend

# Revisa logs
docker-compose logs frontend
```

### Error de conexión a MySQL
```bash
# Espera a que MySQL esté listo
docker-compose logs mysql | grep "ready for connections"

# Reinicia servicios que dependen de MySQL
docker-compose restart auth-service equipment-service
```

### Puerto ya en uso
```bash
# Detén todos los servicios
docker-compose down

# Limpia contenedores
docker system prune -f

# Inicia de nuevo
docker-compose up -d
```

## 📊 Monitoreo

### Ver uso de recursos
```bash
# Uso de CPU y memoria
docker stats

# Espacio en disco
docker system df
```

## 🔒 Seguridad

### Antes de producción:
1. ✅ Cambia todas las contraseñas en `.env`
2. ✅ Genera una nueva `SECRET_KEY`
3. ✅ Configura HTTPS
4. ✅ Habilita autenticación fuerte
5. ✅ Limita acceso a puertos de servicios internos
6. ✅ Configura backups de base de datos

## 📚 Recursos Adicionales

- [Documentación de GitHub Codespaces](https://docs.github.com/es/codespaces)
- [Docker Compose Docs](https://docs.docker.com/compose/)
- [Streamlit Docs](https://docs.streamlit.io/)
- [FastAPI Docs](https://fastapi.tiangolo.com/)

## 🆘 Soporte

Si encuentras problemas:
1. Revisa los logs: `docker-compose logs`
2. Verifica la documentación
3. Abre un issue en GitHub

---

**¡Feliz desarrollo! 🎉**
