# Python SVAN Catálogo

Aplicación web Flask para gestión de catálogos de productos.

## Características

- Gestión de catálogos y productos
- Importación de datos desde CSV
- Generación de PDFs con información de productos
- Sistema de categorías y subcategorías
- Gestión de atributos de productos
- Gestión de imágenes de productos

## Requisitos

- Python 3.11+
- Flask 2.3.3
- SQLAlchemy
- Reportlab (para generación de PDFs)
- Pillow (para procesamiento de imágenes)

## Instalación Local

1. Clonar el repositorio:
```bash
git clone <tu-repositorio>
cd Python_SVAN_Catalogo
```

2. Crear un entorno virtual:
```bash
python -m venv .venv
.venv\Scripts\activate  # En Windows
# o
source .venv/bin/activate  # En Linux/Mac
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Ejecutar la aplicación:
```bash
python app.py
```

La aplicación estará disponible en `http://localhost:5000`

## Despliegue en Render.com

Este proyecto está configurado para desplegarse automáticamente en Render.com.

### Pasos para el despliegue:

1. Crear una cuenta en [Render.com](https://render.com)

2. Conectar tu repositorio de GitHub:
   - Ve a Dashboard → New → Web Service
   - Conecta tu cuenta de GitHub
   - Selecciona este repositorio

3. Render detectará automáticamente el archivo `render.yaml` y configurará el servicio

4. Configurar variables de entorno (opcional):
   - `SECRET_KEY`: Se genera automáticamente
   - `FLASK_ENV`: production (por defecto)

5. Hacer clic en "Create Web Service"

El despliegue se realizará automáticamente. Render ejecutará:
- `build.sh` para instalar dependencias e inicializar la base de datos
- `gunicorn app:app` para iniciar el servidor

### Actualizaciones

Cada vez que hagas push a la rama `main`, Render desplegará automáticamente los cambios.

## Estructura del Proyecto

```
Python_SVAN_Catalogo/
├── app.py                          # Aplicación Flask principal
├── requirements.txt                # Dependencias Python
├── gunicorn_config.py             # Configuración de Gunicorn
├── build.sh                        # Script de build para Render
├── render.yaml                     # Configuración de Render
├── templates/                      # Plantillas HTML
├── static/                         # Archivos estáticos
│   └── uploads/                    # Carpeta para subidas
├── instance/                       # Base de datos SQLite
└── *.py                           # Scripts auxiliares
```

## Scripts Auxiliares

- `actualizar_atributos_sku.py`: Actualización de atributos de SKUs
- `actualizar_imagenes.py`: Gestión de imágenes
- `check_db.py`: Verificación de base de datos
- `verificar_atributos.py`: Verificación de atributos

## Base de Datos

La aplicación utiliza SQLite para desarrollo local. En producción (Render), se utiliza un disco persistente para mantener la base de datos.

## Licencia

[Especifica tu licencia aquí]

## Contacto

[Tu información de contacto]
