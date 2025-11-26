#!/bin/bash

echo "============================================"
echo "  Sistema de Gestión de Equipos de TI"
echo "  Universidad - Inicio de Servicios"
echo "============================================"
echo ""

# Verificar que Docker está instalado
if ! command -v docker &> /dev/null; then
    echo "❌ Error: Docker no está instalado"
    echo "Por favor, instala Docker desde https://www.docker.com/get-started"
    exit 1
fi

# Verificar que Docker Compose está instalado
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Error: Docker Compose no está instalado"
    echo "Por favor, instala Docker Compose"
    exit 1
fi

echo "✅ Docker y Docker Compose detectados"
echo ""

# Detener contenedores existentes si los hay
echo "🔄 Deteniendo contenedores existentes..."
docker-compose down

# Construir e iniciar servicios
echo ""
echo "🏗️  Construyendo imágenes Docker..."
docker-compose build

echo ""
echo "🚀 Iniciando servicios..."
docker-compose up -d

echo ""
echo "⏳ Esperando a que los servicios estén listos..."
sleep 10

# Verificar estado de servicios
echo ""
echo "📊 Estado de los servicios:"
docker-compose ps

echo ""
echo "============================================"
echo "✅ Sistema iniciado exitosamente"
echo "============================================"
echo ""
echo "📱 Accede a la aplicación en:"
echo "   Frontend: http://localhost:8501"
echo "   API Gateway: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "👤 Credenciales por defecto:"
echo "   Usuario: admin"
echo "   Contraseña: admin123"
echo ""
echo "📚 Ver logs: docker-compose logs -f [servicio]"
echo "🛑 Detener: docker-compose down"
echo ""
echo "============================================"
