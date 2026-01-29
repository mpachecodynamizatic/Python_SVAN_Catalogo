#!/usr/bin/env bash
# exit on error
set -o errexit

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
# En Render, instance ya debe estar montado del disco persistente
# Solo crear static/uploads
mkdir -p static/uploads

echo "================================================"
echo "Verificando configuración de disco persistente"
echo "================================================"

# Verificar si el disco persistente está montado
if [ -n "$RENDER_INSTANCE_PATH" ]; then
    echo "✅ RENDER_INSTANCE_PATH configurado: $RENDER_INSTANCE_PATH"
    
    if [ -d "$RENDER_INSTANCE_PATH" ]; then
        echo "✅ Directorio del disco persistente existe"
        ls -lah "$RENDER_INSTANCE_PATH" || echo "⚠️  No se puede listar el contenido"
        
        DB_FILE="$RENDER_INSTANCE_PATH/catalogos_nuevo.db"
        if [ -f "$DB_FILE" ]; then
            DB_SIZE=$(stat -f%z "$DB_FILE" 2>/dev/null || stat -c%s "$DB_FILE" 2>/dev/null || echo "unknown")
            echo "✅ Base de datos existente encontrada: $DB_FILE"
            echo "   Tamaño: $DB_SIZE bytes"
            echo "   Esta base de datos se PRESERVARÁ"
        else
            echo "ℹ️  No hay base de datos existente en el disco persistente"
            echo "   Se creará una nueva base de datos"
        fi
    else
        echo "❌ ERROR: El directorio $RENDER_INSTANCE_PATH no existe"
        echo "   El disco persistente puede no estar montado correctamente"
    fi
else
    echo "ℹ️  RENDER_INSTANCE_PATH no configurado (modo local)"
    mkdir -p instance
fi

echo "================================================"

# Initialize database tables if they don't exist
# db.create_all() ONLY creates tables that don't exist
# It DOES NOT drop or delete existing data
echo "Inicializando tablas de base de datos..."
python << END
import os
import sys
try:
    from app import app, db
    
    # Obtener la ruta de instance configurada
    instance_path = os.environ.get('RENDER_INSTANCE_PATH', 
                                    os.path.join(os.path.dirname(os.path.abspath('app.py')), 'instance'))
    db_file = os.path.join(instance_path, 'catalogos_nuevo.db')
    
    print(f'📂 Ruta de instance: {instance_path}')
    print(f'🗄️  Ruta de BD: {db_file}')
    
    # Verificar permisos de escritura
    if os.path.exists(instance_path):
        if os.access(instance_path, os.W_OK):
            print(f'✅ Permisos de escritura OK en {instance_path}')
        else:
            print(f'❌ ERROR: No hay permisos de escritura en {instance_path}')
            sys.exit(1)
    
    if os.path.exists(db_file):
        file_size = os.path.getsize(db_file)
        print(f'✅ Base de datos existente encontrada ({file_size:,} bytes)')
        print(f'   Los datos se PRESERVARÁN')
    else:
        print('ℹ️  Base de datos no existe - se creará nueva')
    
    with app.app_context():
        db.create_all()
        print('✅ Tablas de base de datos inicializadas (datos existentes preservados)')
        
    # Verificar de nuevo el tamaño después de create_all
    if os.path.exists(db_file):
        file_size = os.path.getsize(db_file)
        print(f'✅ Tamaño final de BD: {file_size:,} bytes')
        
except Exception as e:
    print(f'❌ ERROR en inicialización: {e}')
    import traceback
    traceback.print_exc()
    print('⚠️  La app intentará inicializar en el primer arranque')
END

echo "================================================"
echo "Build completado"
echo "================================================"
