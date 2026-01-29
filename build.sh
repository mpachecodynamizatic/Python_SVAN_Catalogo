#!/usr/bin/env bash
# exit on error
set -o errexit

echo "=========================================="
echo "Instalando dependencias Python"
echo "=========================================="
pip install --upgrade pip
pip install -r requirements.txt

echo "=========================================="
echo "Creando directorios necesarios"
echo "=========================================="
mkdir -p static/uploads

# En Render con disco persistente, la carpeta instance ya debe estar montada
# Solo crearla si no existe (modo local)
if [ -z "$RENDER_INSTANCE_PATH" ]; then
    echo "Modo local - creando carpeta instance"
    mkdir -p instance
else
    echo "Modo Render - usando disco persistente en: $RENDER_INSTANCE_PATH"
fi

echo "=========================================="
echo "Build completado exitosamente"
echo "=========================================="
