# 🚀 Guía Rápida de Inicio

## ✅ Tu sistema ya está configurado para GitHub Codespaces!

### 📁 Archivos Creados

1. **`.devcontainer/devcontainer.json`** - Configuración de Codespaces
2. **`.devcontainer/docker-compose.yml`** - Docker Compose para Codespaces
3. **`.env`** - Variables de entorno
4. **`CODESPACES_SETUP.md`** - Documentación detallada
5. **`DEPLOY_INSTRUCTIONS.md`** - Instrucciones de despliegue
6. **`README_CODESPACES.md`** - README con badge de Codespaces
7. **`setup-codespaces.sh`** - Script de inicialización automática
8. **`.github/workflows/codespaces-prebuild.yml`** - CI/CD opcional

---

## 🎯 Próximos Pasos

### Paso 1: Inicializar Git (si no está inicializado)

```bash
git init
git add .
git commit -m "Initial commit: IT Equipment Management System"
```

### Paso 2: Crear Repositorio en GitHub

1. Ve a https://github.com/new
2. Nombra tu repositorio: `it-equipment-management`
3. **NO** marques ninguna opción de inicialización
4. Haz clic en "Create repository"

### Paso 3: Conectar y Subir

```bash
# Reemplaza TU_USUARIO con tu nombre de usuario de GitHub
git remote add origin https://github.com/TU_USUARIO/it-equipment-management.git
git branch -M main
git push -u origin main
```

**Nota**: Si te pide autenticación, usa un Personal Access Token:
- Ve a GitHub → Settings → Developer settings → Personal access tokens
- Genera un token con permisos `repo`
- Úsalo como contraseña

### Paso 4: Abrir en Codespaces

**Opción A**: Desde GitHub
1. Ve a tu repositorio
2. Clic en **"Code"** (botón verde)
3. Pestaña **"Codespaces"**
4. Clic en **"Create codespace on main"**

**Opción B**: URL Directa
```
https://github.com/codespaces/new?hide_repo_select=true&ref=main&repo=TU_USUARIO/it-equipment-management
```

### Paso 5: ¡Espera y Disfruta! ☕

- Codespaces construirá todo automáticamente (5-10 min)
- El frontend se abrirá en el puerto 8501
- **Usuario**: `admin`
- **Contraseña**: `admin123`

---

## 🌟 Opcional: Agregar Badge al README

Reemplaza tu `README.md` con `README_CODESPACES.md`:

```bash
mv README_CODESPACES.md README.md
git add README.md
git commit -m "Add Codespaces badge to README"
git push
```

Ahora tu README tendrá un botón para abrir directamente en Codespaces!

---

## 🔥 Testing Local (Opcional)

Si quieres probar localmente primero:

```bash
# Iniciar servicios
docker-compose up -d

# Verificar estado
docker-compose ps

# Acceder
# Frontend: http://localhost:8501
# API: http://localhost:8000
```

---

## 🐛 Troubleshooting

### Error: "Permission denied" al subir a GitHub
```bash
# Usa HTTPS con token en vez de SSH
git remote set-url origin https://github.com/TU_USUARIO/it-equipment-management.git
```

### Codespace tarda mucho
- Normal en la primera vez (10-15 min)
- Las siguientes veces serán más rápidas (2-3 min)

### Los servicios no inician en Codespaces
```bash
# Dentro de Codespaces, ejecuta:
./setup-codespaces.sh
```

### Puerto 8501 no se abre automáticamente
1. Ve a la pestaña "PORTS"
2. Busca el puerto 8501
3. Haz clic en el ícono de navegador 🌐

---

## 📚 Documentación Completa

- **CODESPACES_SETUP.md** - Guía detallada de uso de Codespaces
- **DEPLOY_INSTRUCTIONS.md** - Cómo desplegar en producción
- **ESTRUCTURA_PROYECTO.md** - Arquitectura del sistema

---

## 🎉 ¡Listo!

Tu sistema está 100% configurado para la nube. Solo sigue los pasos de arriba y en minutos tendrás tu aplicación corriendo en GitHub Codespaces.

**¿Preguntas?** Revisa la documentación o abre un issue en GitHub.

---

**Desarrollado con ❤️ usando Claude Code**
