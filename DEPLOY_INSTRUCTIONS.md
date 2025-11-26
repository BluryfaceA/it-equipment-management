# 🚀 Instrucciones de Despliegue

## 📝 Pasos para Subir a GitHub Codespaces

### 1. Preparar el Repositorio Local

```bash
cd it-equipment-management

# Inicializar git (si no está inicializado)
git init

# Agregar todos los archivos
git add .

# Hacer commit inicial
git commit -m "Initial commit: IT Equipment Management System"
```

### 2. Crear Repositorio en GitHub

1. Ve a [GitHub](https://github.com)
2. Haz clic en el botón "+" en la esquina superior derecha
3. Selecciona "New repository"
4. Nombra tu repositorio: `it-equipment-management`
5. Déjalo como **público** o **privado** según prefieras
6. **NO** inicialices con README, .gitignore o licencia
7. Haz clic en "Create repository"

### 3. Conectar y Subir tu Código

```bash
# Agregar el remote de GitHub (reemplaza TU_USUARIO con tu usuario de GitHub)
git remote add origin https://github.com/TU_USUARIO/it-equipment-management.git

# Renombrar la rama a main
git branch -M main

# Subir el código
git push -u origin main
```

Si te pide autenticación, usa un **Personal Access Token**:
1. Ve a GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Genera un nuevo token con permisos `repo`
3. Úsalo como contraseña cuando hagas push

### 4. Abrir en Codespaces

**Método 1: Desde GitHub**
1. Ve a tu repositorio en GitHub
2. Haz clic en el botón verde **"Code"**
3. Selecciona la pestaña **"Codespaces"**
4. Haz clic en **"Create codespace on main"**

**Método 2: Badge en README**
Agrega este badge a tu README.md:

```markdown
[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/TU_USUARIO/it-equipment-management?quickstart=1)
```

### 5. Esperar la Construcción

El Codespace:
- ✅ Descargará el código
- ✅ Construirá todas las imágenes Docker (5-10 minutos)
- ✅ Iniciará todos los servicios automáticamente
- ✅ Abrirá el puerto 8501 (Frontend) automáticamente

### 6. Acceder a la Aplicación

Una vez que Codespaces esté listo:
- El frontend se abrirá automáticamente en una nueva pestaña
- Si no se abre, ve a la pestaña "PORTS" y haz clic en el puerto **8501**
- Usuario: `admin`
- Contraseña: `admin123`

---

## 🌐 Alternativa: Desplegar en la Nube (Producción)

### Opción 1: Railway.app

1. Ve a [Railway.app](https://railway.app)
2. Conecta con GitHub
3. Selecciona tu repositorio
4. Railway detectará automáticamente el `docker-compose.yml`
5. Configura las variables de entorno
6. ¡Despliega!

### Opción 2: Render.com

1. Ve a [Render.com](https://render.com)
2. Crea una nueva "Web Service"
3. Conecta tu repositorio de GitHub
4. Render detectará Docker
5. Configura:
   - Environment: Docker
   - Docker Command: `docker-compose up`
6. Despliega

### Opción 3: DigitalOcean App Platform

1. Ve a [DigitalOcean](https://www.digitalocean.com/)
2. Crea una nueva App
3. Conecta con GitHub
4. Selecciona tu repositorio
5. DigitalOcean detectará docker-compose
6. Configura recursos (mínimo: 2GB RAM)
7. Despliega

### Opción 4: AWS (Amazon Web Services)

**Usando ECS (Elastic Container Service):**
```bash
# Instalar AWS CLI
pip install awscli

# Configurar credenciales
aws configure

# Subir imágenes a ECR
aws ecr create-repository --repository-name it-management

# Build y push
docker-compose build
docker tag it-equipment-management-frontend:latest YOUR_ECR_URL/it-management:frontend
docker push YOUR_ECR_URL/it-management:frontend
```

### Opción 5: Google Cloud Run

```bash
# Instalar gcloud CLI
gcloud init

# Configurar proyecto
gcloud config set project YOUR_PROJECT_ID

# Deploy cada servicio
gcloud run deploy frontend --source . --platform managed --region us-central1
```

### Opción 6: Azure Container Instances

```bash
# Instalar Azure CLI
az login

# Crear grupo de recursos
az group create --name it-management-rg --location eastus

# Deploy con Docker Compose
az container create --resource-group it-management-rg --file docker-compose.yml
```

---

## 🔧 Configuración de Variables de Entorno para Producción

Antes de desplegar en producción, actualiza el archivo `.env`:

```bash
# Genera una SECRET_KEY segura
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Actualiza .env con:
SECRET_KEY=tu-nueva-secret-key-super-segura

# Cambia las contraseñas de MySQL
MYSQL_ROOT_PASSWORD=contraseña-segura-aqui
DB_PASSWORD=otra-contraseña-segura
```

---

## 📊 Verificación Post-Despliegue

Después de desplegar, verifica:

```bash
# Verifica que todos los servicios estén corriendo
docker-compose ps

# Prueba el health check del API Gateway
curl http://localhost:8000/health

# Verifica logs
docker-compose logs -f
```

---

## 🛡️ Checklist de Seguridad

Antes de producción:
- [ ] Cambiar todas las contraseñas por defecto
- [ ] Generar nueva SECRET_KEY
- [ ] Configurar HTTPS/SSL
- [ ] Habilitar autenticación fuerte (2FA)
- [ ] Configurar firewall
- [ ] Limitar acceso a base de datos
- [ ] Configurar backups automáticos
- [ ] Configurar monitoreo y alertas
- [ ] Actualizar dependencias a últimas versiones
- [ ] Revisar logs de errores

---

## 📞 Soporte

Si tienes problemas:
1. Revisa `CODESPACES_SETUP.md` para troubleshooting
2. Verifica los logs: `docker-compose logs`
3. Abre un issue en el repositorio

---

**¡Feliz despliegue! 🎉**
