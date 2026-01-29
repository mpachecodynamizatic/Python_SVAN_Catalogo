#!/bin/bash

echo "=========================================="
echo "Azure App Service - Iniciando aplicación"
echo "=========================================="

# Crear carpeta persistente en /home (persiste entre deployments en Azure)
mkdir -p /home/instance
mkdir -p /home/site/wwwroot/static/uploads

echo "📂 Carpeta persistente creada: /home/instance"

# Verificar si hay base de datos existente
if [ -f /home/instance/catalogos_nuevo.db ]; then
    DB_SIZE=$(stat -c%s /home/instance/catalogos_nuevo.db)
    echo "✅ Base de datos existente encontrada: ${DB_SIZE} bytes"
else
    echo "ℹ️  No hay base de datos existente. Se creará una nueva."
fi

# Iniciar Gunicorn
echo "🚀 Iniciando Gunicorn..."
gunicorn --bind=0.0.0.0:8000 --timeout 600 --workers=4 app:app
