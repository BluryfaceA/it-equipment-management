@echo off
echo ============================================
echo   Sistema de Gestion de Equipos de TI
echo   Universidad - Inicio de Servicios
echo ============================================
echo.

REM Verificar que Docker esta instalado
docker --version >nul 2>&1
if errorlevel 1 (
    echo Error: Docker no esta instalado
    echo Por favor, instala Docker desde https://www.docker.com/get-started
    pause
    exit /b 1
)

REM Verificar que Docker Compose esta instalado
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo Error: Docker Compose no esta instalado
    echo Por favor, instala Docker Compose
    pause
    exit /b 1
)

echo Docker y Docker Compose detectados
echo.

REM Detener contenedores existentes
echo Deteniendo contenedores existentes...
docker-compose down

REM Construir e iniciar servicios
echo.
echo Construyendo imagenes Docker...
docker-compose build

echo.
echo Iniciando servicios...
docker-compose up -d

echo.
echo Esperando a que los servicios esten listos...
timeout /t 10 /nobreak >nul

REM Verificar estado de servicios
echo.
echo Estado de los servicios:
docker-compose ps

echo.
echo ============================================
echo Sistema iniciado exitosamente
echo ============================================
echo.
echo Accede a la aplicacion en:
echo    Frontend: http://localhost:8501
echo    API Gateway: http://localhost:8000
echo    API Docs: http://localhost:8000/docs
echo.
echo Credenciales por defecto:
echo    Usuario: admin
echo    Password: admin123
echo.
echo Ver logs: docker-compose logs -f [servicio]
echo Detener: docker-compose down
echo.
echo ============================================
pause
