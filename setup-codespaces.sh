#!/bin/bash

echo "🚀 Configurando IT Equipment Management System en Codespaces..."
echo ""

# Copiar .env.example a .env si no existe
if [ ! -f .env ]; then
    echo "📋 Creando archivo .env desde .env.example..."
    cp .env.example .env
    echo "✅ Archivo .env creado"
else
    echo "✅ Archivo .env ya existe"
fi

echo ""
echo "🐳 Iniciando servicios Docker..."
echo "Esto puede tomar varios minutos la primera vez..."
echo ""

# Iniciar docker-compose
docker-compose up -d

echo ""
echo "⏳ Esperando a que los servicios estén listos..."
sleep 10

# Verificar estado de los servicios
echo ""
echo "📊 Estado de los servicios:"
docker-compose ps

echo ""
echo "🔍 Verificando MySQL..."
until docker exec it-management-mysql mysqladmin ping -h localhost -uroot -padmin --silent; do
    echo "⏳ Esperando a MySQL..."
    sleep 2
done
echo "✅ MySQL está listo"

echo ""
echo "🎉 ¡Sistema configurado exitosamente!"
echo ""
echo "📱 Accede a la aplicación:"
echo "   Frontend (Streamlit): http://localhost:8501"
echo "   API Gateway: http://localhost:8000"
echo ""
echo "🔐 Credenciales por defecto:"
echo "   Usuario: admin"
echo "   Contraseña: admin123"
echo ""
echo "📚 Para más información, consulta CODESPACES_SETUP.md"
echo ""
