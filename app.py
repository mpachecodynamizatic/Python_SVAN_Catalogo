from flask import Flask, render_template, request, redirect, url_for, flash, send_file, jsonify, Response, render_template_string, session
from flask_sqlalchemy import SQLAlchemy
import os
import requests
import json
import csv
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash
from io import BytesIO
from PIL import Image as PILImage
import tempfile
import time
from functools import wraps

app = Flask(__name__)

# Configuration
# Ensure instance folder exists
# En Render, usar el disco persistente montado; localmente, usar carpeta instance
instance_path = os.environ.get('RENDER_INSTANCE_PATH', 
                                os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance'))

print(f"========================================")
print(f"DIAGNÓSTICO DE DISCO PERSISTENTE")
print(f"========================================")
print(f"📂 Instance path: {instance_path}")
print(f"🔧 RENDER_INSTANCE_PATH: {os.environ.get('RENDER_INSTANCE_PATH', 'NO CONFIGURADO')}")

# Listar contenido de la carpeta instance si existe
if os.path.exists(instance_path):
    print(f"✅ La carpeta existe")
    try:
        contenido = os.listdir(instance_path)
        print(f"📁 Contenido de la carpeta ({len(contenido)} archivos):")
        for item in contenido:
            item_path = os.path.join(instance_path, item)
            if os.path.isfile(item_path):
                size = os.path.getsize(item_path)
                print(f"   - {item} ({size:,} bytes)")
            else:
                print(f"   - {item}/ (directorio)")
        if not contenido:
            print(f"   ⚠️  La carpeta está VACÍA")
    except Exception as e:
        print(f"❌ Error listando contenido: {e}")
    
    # Verificar permisos
    if os.access(instance_path, os.W_OK):
        print(f"✅ Permisos de escritura: OK")
    else:
        print(f"❌ Sin permisos de escritura")
else:
    os.makedirs(instance_path, exist_ok=True)
    print(f"📁 Carpeta creada en: {instance_path}")

db_path = os.environ.get('DATABASE_URL')
if not db_path:
    db_file_path = os.path.join(instance_path, 'catalogos_nuevo.db')
    db_path = f"sqlite:///{db_file_path}"
    print(f"🗄️  Ruta de BD: {db_file_path}")
    if os.path.exists(db_file_path):
        size = os.path.getsize(db_file_path)
        print(f"✅ BD EXISTENTE encontrada. Tamaño: {size:,} bytes")
        print(f"   ✅ LOS DATOS SE PRESERVARÁN")
    else:
        print(f"⚠️  BD no existe. Se creará nueva.")
print(f"========================================\n")

app.config['SQLALCHEMY_DATABASE_URI'] = db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.environ.get('UPLOAD_FOLDER', 'static/uploads')
app.secret_key = os.environ.get('SECRET_KEY', 'clave_secreta_muy_segura_cambiar_en_produccion')

# Usuarios del sistema (en producción usar base de datos con contraseñas hasheadas)
USUARIOS = {
    'admin': generate_password_hash('admin123'),
    'user': generate_password_hash('user123'),
    'producto': generate_password_hash('producto123')
}

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Decorador para reintentos en operaciones de base de datos
def retry_on_db_error(max_retries=5, delay=1, backoff=2):
    """
    Decorador para reintentar operaciones de base de datos en caso de error.
    
    Args:
        max_retries: Número máximo de reintentos
        delay: Tiempo de espera inicial entre reintentos (segundos)
        backoff: Factor de incremento del delay en cada reintento
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            current_delay = delay
            
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    if retries >= max_retries:
                        print(f"Error después de {max_retries} reintentos: {e}")
                        raise
                    
                    print(f"Error en operación DB (reintento {retries}/{max_retries}): {e}")
                    time.sleep(current_delay)
                    current_delay *= backoff
                    
                    # Hacer rollback antes de reintentar
                    try:
                        db.session.rollback()
                    except:
                        pass
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

db = SQLAlchemy(app)

# Diccionario de subcategorías por categoría padre
SUBCATEGORIAS = {
    'AGUA CALIENTE': ['AEROTERMO', 'CALENTADOR ATMOSF', 'CALENTADOR ESTANCO', 'MONOBLOC', 'TERMOS'],
    'CAMPANAS': ['CAMPANA DECORATIVA', 'CAMPANA EXTRAIBLE', 'CAMPANA INT', 'CAMPANA PIRAMIDAL', 'CAMPANA TECHO', 'CAMPANA TIPO T', 'GRUPO FILTRANTE'],
    'CLIMATIZACION': ['CASSETTE INT', 'CONDUCTO', 'CONDUCTO INT', 'EXTERIOR 1X1', 'EXTERIOR MULTI', 'PANEL', 'PORTATILES', 'SPLIT', 'SPLIT INT', 'SUELO TECHO INT', 'VERTICAL INT'],
    'COCCION': ['ENCIMERAS DE GAS', 'HORNILLAS', 'HORNOS', 'INDUCCIONES', 'MINI HORNOS', 'MW', 'MW INT', 'VITROCERAMICAS'],
    'COCINAS': ['COCINA 50 ELECTRICA', 'COCINA 50 GAS', 'COCINA 50 MIXTA', 'COCINA 60 ELECTRICA', 'COCINA 60 GAS', 'COCINA 60 MIXTA', 'COCINA 90 ELECTRICA', 'COCINA 90 GAS', 'COCINA 90 MIXTA'],
    'COMBINADOS': ['COMBI CICLICOS', 'COMBI INTEGRACION', 'COMBI NF', 'COMBI RETRO', 'COMBI SF'],
    'CONGELADORES': ['CONGELAD CICLICO', 'CONGELAD HORIZONTAL', 'CONGELAD NF', 'CONGELAD SF'],
    'FRIGORIFICOS': ['FRIGO 4 PTAS', 'FRIGO AMERICANO', 'FRIGO CICLICO', 'FRIGO FRANCES', 'FRIGO NF', 'FRIGO RETRO', 'FRIGO VENTILADO'],
    'HORECA': ['CONGELAD HORECA', 'REFRIGER HORECA'],
    'LAVADORAS': ['LAVADORA 10KG', 'LAVADORA 11KG', 'LAVADORA 12KG', 'LAVADORA 5KG', 'LAVADORA 6KG', 'LAVADORA 7KG', 'LAVADORA 8KG', 'LAVADORA 9KG', 'LAVADORA CARGA SUP', 'LAVADORA SECADORA'],
    'LAVAVAJILLAS': ['LAVAVAJILLAS 45CM', 'LAVAVAJILLAS 60CM', 'LAVAVAJILLAS INT'],
    'REFRIGERADORES': ['REFRIGER CICLICO', 'REFRIGER NF', 'REFRIGER PELTIER', 'REFRIGER RETRO', 'REFRIGER SF'],
    'SECADORA': ['SECADORA BOMBA CALOR', 'SECADORA CONDENSAC', 'SECADORA EVACUACION'],
    'VINOTECAS': ['VINOTECA CICLICA', 'VINOTECA PELTIER'],
    'CALEFACCION': ['CALEF CONVECTOR', 'CALEF EMISOR TERMICO', 'CALEF ESTUFA', 'CALEF RADIADOR'],
    'PAE': ['PAE AIR FRYER', 'PAE ASPIRADOR', 'PAE BATIDORA', 'PAE CAFETERA', 'PAE EXPRIMIDOR', 'PAE GRANIZADORA', 'PAE GRILL', 'PAE HELADERA', 'PAE HERVIDOR', 'PAE LIMPIADOR VAPOR', 'PAE MINIHORNO', 'PAE PARRILLAS GRILL', 'PAE PIZZA MAKER', 'PAE PLANCHA ASAR', 'PAE PLANCHADO', 'PAE PURIFICADOR', 'PAE SANDWICHERA', 'PAE SECADOR PELO', 'PAE TOSTADOR', 'VENTILACION'],
    'TELEVISION': ['TV 22', 'TV 24', 'TV 24 QLED', 'TV 32', 'TV 32 QLED', 'TV 39', 'TV 40', 'TV 40 QLED', 'TV 42', 'TV 43', 'TV 43 QLED', 'TV 48', 'TV 49', 'TV 50', 'TV 50 QLED', 'TV 55', 'TV 55 QLED', 'TV 58', 'TV 60', 'TV 65', 'TV 75', 'TV 82', 'TV ACCESORIOS']
}

class Catalogo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True, nullable=False)
    descripcion = db.Column(db.String(200), nullable=False)
    marcas = db.Column(db.String(200), nullable=False)  # Separadas por coma

    def __repr__(self):
        return f'<Catalogo {self.codigo}>'

class Categoria(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    catalogo_id = db.Column(db.Integer, db.ForeignKey('catalogo.id'), nullable=False)
    cod_categoria = db.Column(db.String(50), nullable=False)
    descripcion = db.Column(db.String(200), nullable=False)
    catalogo = db.relationship('Catalogo', backref=db.backref('categorias', lazy=True))

    def __repr__(self):
        return f'<Categoria {self.cod_categoria}>'

class Subcategoria(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categoria.id'), nullable=False)
    cod_categoria = db.Column(db.String(50), nullable=False)
    descripcion = db.Column(db.String(200), nullable=False)
    categoria = db.relationship('Categoria', backref=db.backref('subcategorias', lazy=True))

    def __repr__(self):
        return f'<Subcategoria {self.cod_categoria}>'

class Ficha(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subcategoria_id = db.Column(db.Integer, db.ForeignKey('subcategoria.id'), nullable=False)
    fila_numero = db.Column(db.Integer, nullable=False)
    subcategoria = db.relationship('Subcategoria', backref=db.backref('fichas', lazy=True))

    def __repr__(self):
        return f'<Ficha {self.fila_numero}>'

class Tarjeta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ficha_id = db.Column(db.Integer, db.ForeignKey('ficha.id'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('producto.id'))  # Relación con producto
    marca = db.Column(db.String(10), nullable=False)
    imagen = db.Column(db.String(200))
    nombre = db.Column(db.String(200))
    valor_energetico = db.Column(db.String(50))
    peso = db.Column(db.String(50))
    volumen = db.Column(db.String(50))
    ficha = db.relationship('Ficha', backref=db.backref('tarjetas', lazy=True))
    producto = db.relationship('Producto', backref=db.backref('tarjetas', lazy=True))

    def __repr__(self):
        return f'<Tarjeta {self.marca}>'

class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_csv = db.Column(db.Integer, unique=True, nullable=False)  # ID del CSV para relación con atributos
    marca = db.Column(db.String(10), nullable=False)  # AS, WD, SV, HY, NL, FR
    producto_id = db.Column(db.String(50))  # ProductoId del CSV
    sku = db.Column(db.String(50))
    categoria = db.Column(db.String(100), default='', server_default='')  # Categoría del producto (INDUCCIONES, VITROCERAMICAS, etc.)
    ean = db.Column(db.String(50))
    descripcion = db.Column(db.Text)
    titulo = db.Column(db.Text)
    descripcion_larga = db.Column(db.Text)
    estado_referencia = db.Column(db.String(50))
    clasificacion = db.Column(db.String(50))
    color = db.Column(db.String(100))
    dimensiones = db.Column(db.String(100))
    imagen = db.Column(db.String(500))  # URL de la imagen del producto
    
    def __repr__(self):
        return f'<Producto {self.sku}>'

class Atributo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey('producto.id'), nullable=False)
    sku = db.Column(db.String(50))  # SKU del producto (redundante para facilitar búsquedas)
    atributo = db.Column(db.String(100), nullable=False)
    valor = db.Column(db.String(200), nullable=False)
    orden = db.Column(db.Integer, nullable=False, default=0, server_default='0')  # Campo para ordenar atributos
    producto = db.relationship('Producto', backref=db.backref('atributos', lazy=True))

class Imagen(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey('producto.id'), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    producto = db.relationship('Producto', backref=db.backref('imagenes', lazy=True))

class DatosManuales(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(50), unique=True, nullable=False)
    unidades_vendidas = db.Column(db.Integer, default=0)
    pvp = db.Column(db.Float, default=0.0)
    inventario = db.Column(db.Integer, default=0)
    fecha_entrada = db.Column(db.String(20))  # Formato: DD/MM/YYYY
    unidades_entrada = db.Column(db.Integer, default=0)
    fabricante = db.Column(db.String(100))
    
    def __repr__(self):
        return f'<DatosManuales {self.sku}>'

class PlantillaTarjeta(db.Model):
    """
    Configuración de qué información mostrar en las tarjetas de productos.
    Jerarquía: subcategoria_id > categoria_id > catalogo_id > general (todos null)
    """
    id = db.Column(db.Integer, primary_key=True)
    catalogo_id = db.Column(db.Integer, db.ForeignKey('catalogo.id'), nullable=True)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categoria.id'), nullable=True)
    subcategoria_id = db.Column(db.Integer, db.ForeignKey('subcategoria.id'), nullable=True)
    
    # Campos de la ficha del producto a mostrar (JSON array: ['sku', 'titulo', 'ean', 'estado_referencia', 'color', 'marca', 'descripcion', 'dimensiones'])
    campos_ficha = db.Column(db.Text, nullable=False, default='["sku", "titulo", "ean", "estado_referencia", "color"]')
    
    # Atributos a mostrar (JSON array: ['Potencia', 'Capacidad', ...])
    atributos_seleccionados = db.Column(db.Text, nullable=False, default='[]')
    
    # Si es True, esta plantilla se aplica como genérica para la categoría
    es_generica = db.Column(db.Boolean, default=False)
    
    catalogo = db.relationship('Catalogo', backref=db.backref('plantillas', lazy=True))
    categoria = db.relationship('Categoria', backref=db.backref('plantillas', lazy=True))
    subcategoria = db.relationship('Subcategoria', backref=db.backref('plantillas', lazy=True))
    
    def __repr__(self):
        if self.subcategoria_id:
            return f'<PlantillaTarjeta Subcategoria {self.subcategoria_id}>'
        elif self.categoria_id:
            return f'<PlantillaTarjeta Categoria {self.categoria_id}>'
        elif self.catalogo_id:
            return f'<PlantillaTarjeta Catalogo {self.catalogo_id}>'
        else:
            return '<PlantillaTarjeta General>'

# Crear la base de datos si no existe
# db.create_all() solo crea tablas que no existen, NO borra datos
with app.app_context():
    db.create_all()

# Decorador para proteger rutas
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario' not in session:
            flash('Debes iniciar sesión para acceder a esta página', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Rutas de autenticación
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form.get('usuario')
        password = request.form.get('password')
        
        if usuario in USUARIOS and check_password_hash(USUARIOS[usuario], password):
            session['usuario'] = usuario
            flash(f'Bienvenido {usuario}', 'success')
            return redirect(url_for('index'))
        else:
            flash('Usuario o contraseña incorrectos', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('usuario', None)
    flash('Sesión cerrada correctamente', 'info')
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    catalogos = Catalogo.query.all()
    return render_template('index.html', catalogos=catalogos)

@app.route('/productos')
@login_required
def productos():
    from sqlalchemy import func
    buscar = request.args.get('buscar', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = 50  # Productos por página
    
    # Subconsulta para contar atributos
    atributos_count = db.session.query(
        Atributo.producto_id,
        func.count(Atributo.id).label('count')
    ).group_by(Atributo.producto_id).subquery()
    
    if buscar:
        # Buscar en SKU, marca, título, descripción, categoría
        query = db.session.query(Producto, func.coalesce(atributos_count.c.count, 0).label('num_atributos')).outerjoin(
            atributos_count, Producto.id == atributos_count.c.producto_id
        ).filter(
            db.or_(
                Producto.sku.like(f'%{buscar}%'),
                Producto.marca.like(f'%{buscar}%'),
                Producto.titulo.like(f'%{buscar}%'),
                Producto.descripcion.like(f'%{buscar}%'),
                Producto.ean.like(f'%{buscar}%'),
                Producto.categoria.like(f'%{buscar}%')
            )
        )
    else:
        query = db.session.query(Producto, func.coalesce(atributos_count.c.count, 0).label('num_atributos')).outerjoin(
            atributos_count, Producto.id == atributos_count.c.producto_id
        )
    
    # Aplicar paginación
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    # Crear lista de tuplas (producto, num_atributos)
    productos_con_conteo = [(p, int(count)) for p, count in pagination.items]
    
    # Obtener total de productos
    total_productos = Producto.query.count()
    
    return render_template('productos.html', productos=productos_con_conteo, buscar=buscar, pagination=pagination, total_productos=total_productos)

@app.route('/productos_atributos')
@login_required
def productos_atributos():
    from sqlalchemy import func
    buscar = request.args.get('buscar', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = 100  # Atributos por página
    
    # Query con join a Producto para mostrar información completa
    query = db.session.query(Atributo, Producto).join(
        Producto, Atributo.producto_id == Producto.id
    )
    
    if buscar:
        # Buscar en nombre del atributo, valor, SKU del producto, marca, SKU del atributo
        query = query.filter(
            db.or_(
                Atributo.atributo.like(f'%{buscar}%'),
                Atributo.valor.like(f'%{buscar}%'),
                Atributo.sku.like(f'%{buscar}%'),
                Producto.sku.like(f'%{buscar}%'),
                Producto.marca.like(f'%{buscar}%'),
                Producto.titulo.like(f'%{buscar}%')
            )
        )
    
    # Ordenar por producto y orden
    query = query.order_by(Producto.sku, Atributo.orden)
    
    # Aplicar paginación
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    atributos_con_producto = [(atributo, producto) for atributo, producto in pagination.items]
    
    # Contar total de atributos
    total_atributos = Atributo.query.count()
    
    return render_template('productos_atributos.html', 
                         atributos=atributos_con_producto, 
                         buscar=buscar, 
                         pagination=pagination,
                         total_atributos=total_atributos)

@app.route('/datos_manuales')
@login_required
def datos_manuales():
    buscar = request.args.get('buscar', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = 50  # Registros por página
    
    query = DatosManuales.query
    
    if buscar:
        # Buscar por SKU o fabricante
        query = query.filter(
            db.or_(
                DatosManuales.sku.like(f'%{buscar}%'),
                DatosManuales.fabricante.like(f'%{buscar}%')
            )
        )
    
    # Ordenar por SKU
    query = query.order_by(DatosManuales.sku)
    
    # Aplicar paginación
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Contar total
    total_datos = DatosManuales.query.count()
    
    return render_template('datos_manuales.html', 
                         datos=pagination.items, 
                         buscar=buscar, 
                         pagination=pagination,
                         total_datos=total_datos)

@app.route('/ver_producto/<int:id>')
@login_required
def ver_producto(id):
    producto = Producto.query.get_or_404(id)
    atributos = Atributo.query.filter_by(producto_id=id).order_by(Atributo.orden).all()
    datos_manuales = DatosManuales.query.filter_by(sku=producto.sku).first()
    return render_template('ver_producto.html', producto=producto, atributos=atributos, datos_manuales=datos_manuales)

@app.route('/producto/<int:id>/atributos')
def producto_atributos(id):
    producto = Producto.query.get_or_404(id)
    atributos = Atributo.query.filter_by(producto_id=id).order_by(Atributo.orden).all()
    return render_template('atributos.html', producto=producto, atributos=atributos)

@app.route('/eliminar_producto/<int:id>')
def eliminar_producto(id):
    producto = Producto.query.get_or_404(id)
    # Eliminar atributos e imágenes relacionados
    Atributo.query.filter_by(producto_id=id).delete()
    Imagen.query.filter_by(producto_id=id).delete()
    db.session.delete(producto)
    db.session.commit()
    flash('Producto eliminado correctamente.')
    return redirect(url_for('productos'))

@app.route('/eliminar_atributo/<int:id>')
def eliminar_atributo(id):
    atributo = Atributo.query.get_or_404(id)
    producto_id = atributo.producto_id
    db.session.delete(atributo)
    db.session.commit()
    flash('Atributo eliminado correctamente.')
    return redirect(url_for('producto_atributos', id=producto_id))

@app.route('/importar/conteos')
def importar_conteos():
    """Devuelve los conteos de registros existentes en la base de datos"""
    import json
    try:
        conteos = {
            'productos': Producto.query.count(),
            'atributos': Atributo.query.count(),
            'datos_manuales': DatosManuales.query.count()
        }
        return json.dumps(conteos)
    except Exception as e:
        return json.dumps({'error': str(e)}), 500

@app.route('/importar', methods=['GET', 'POST'])
@login_required
def importar():
    if request.method == 'POST':
        tipo = request.form['tipo']
        
        # Para datos manuales no necesitamos archivo
        if tipo == 'datos_manuales':
            from flask import session
            session['import_tipo'] = tipo
            session['import_file'] = None
            session['import_filename'] = 'Generación automática'
            return redirect(url_for('importar_progreso'))
        
        # Para productos y atributos sí necesitamos archivo
        archivo = request.files.get('archivo')
        
        if not archivo or not archivo.filename:
            flash('No se seleccionó ningún archivo.', 'error')
            return render_template('importar.html')
            
        if not archivo.filename.endswith('.csv'):
            flash('Archivo no válido. Debe ser un CSV.', 'error')
            return render_template('importar.html')
            
        try:
            filename = secure_filename(archivo.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            archivo.save(filepath)
            
            # Guardar información en sesión para la página de progreso
            from flask import session
            session['import_tipo'] = tipo
            session['import_file'] = filepath
            session['import_filename'] = filename
            
            return redirect(url_for('importar_progreso'))
        except Exception as e:
            flash(f'Error durante la importación: {str(e)}', 'error')
            return render_template('importar.html')
    
    return render_template('importar.html')

@app.route('/importar_progreso')
def importar_progreso():
    return render_template('importar_progreso.html')

@app.route('/importar_stream')
def importar_stream():
    from flask import session, Response
    import threading
    import time
    
    tipo = session.get('import_tipo')
    filepath = session.get('import_file')
    
    def generar():
        try:
            if tipo == 'productos':
                for mensaje in importar_productos_con_progreso(filepath):
                    yield f"data: {mensaje}\n\n"
            elif tipo == 'atributos':
                for mensaje in importar_atributos_con_progreso(filepath):
                    yield f"data: {mensaje}\n\n"
            elif tipo == 'datos_manuales':
                for mensaje in importar_datos_manuales_con_progreso():
                    yield f"data: {mensaje}\n\n"
            
            # Eliminar archivo temporal después de importar
            try:
                if filepath:
                    os.remove(filepath)
            except:
                pass
        except Exception as e:
            yield f"data: {{\"error\": \"{str(e)}\"}}\n\n"
    
    return Response(generar(), mimetype='text/event-stream')

# Función auxiliar para commits con retry
@retry_on_db_error(max_retries=5, delay=0.5, backoff=2)
def commit_with_retry():
    """Ejecuta commit con reintentos automáticos"""
    db.session.commit()

def importar_productos_con_progreso(filepath):
    import json
    import sys
    csv.field_size_limit(sys.maxsize)  # Aumentar límite para campos grandes
    
    marca_map = {
        'ASPES': 'AS', 'Aspes': 'AS',
        'WONDER': 'WD', 'Wonder': 'WD',
        'SVAN': 'SV', 'Svan': 'SV',
        'HYUNDAI': 'HY', 'Hyundai': 'HY',
        'NILSON': 'NL', 'Nilson': 'NL',
        'FAGOR': 'FR', 'Fagor': 'FR'
    }
    
    importados = 0
    omitidos = 0
    total = 0
    
    try:
        # Contar líneas primero
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            total = sum(1 for _ in f) - 1  # -1 por la cabecera
        
        yield json.dumps({'tipo': 'inicio', 'total': total, 'mensaje': f'Iniciando importación de {total} productos...'})
        
        # Cargar SKUs existentes en memoria para optimizar consultas
        skus_existentes = {p.sku for p in Producto.query.with_entities(Producto.sku).all() if p.sku}
        ids_existentes = {p.id_csv for p in Producto.query.with_entities(Producto.id_csv).all() if p.id_csv}
        
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f, delimiter=';')
            procesados = 0
            
            for row in reader:
                procesados += 1
                marca_original = row.get('Marca', '').strip()
                
                if marca_original in marca_map:
                    try:
                        with db.session.no_autoflush:
                            sku = row.get('Sku', '').strip()
                            
                            # Verificar si ya existe por SKU en memoria (más rápido)
                            if sku and sku in skus_existentes:
                                omitidos += 1
                                continue
                            
                            # Si no existe por SKU, verificar por id_csv en memoria
                            id_csv = int(row.get('id', 0))
                            if id_csv and id_csv in ids_existentes:
                                omitidos += 1
                                continue
                            # Generar URL de imagen
                            imagen_url = f"https://pim.gruposvan.com/multimedia/{sku}/800x600_imagen_principal.png" if sku else ''
                                
                            producto = Producto(
                                id_csv=id_csv,
                                marca=marca_map[marca_original],
                                producto_id=row.get('ProductoId', '').strip(),
                                sku=sku,
                                categoria=row.get('Categoria', '').strip(),
                                ean=row.get('Ean', '').strip(),
                                descripcion=row.get('Descripcion', '').strip(),
                                titulo=row.get('Titulo', '').strip(),
                                descripcion_larga=row.get('DescripcionLarga', '').strip(),
                                estado_referencia=row.get('EstadoReferencia', '').strip(),
                                clasificacion=row.get('Clasificacion', '').strip(),
                                color=row.get('Color', '').strip(),
                                dimensiones=row.get('Dimensiones', '').strip(),
                                imagen=imagen_url
                            )
                            db.session.add(producto)
                            # Agregar a sets en memoria
                            if sku:
                                skus_existentes.add(sku)
                            if id_csv:
                                ids_existentes.add(id_csv)
                            importados += 1
                    except Exception as e:
                        print(f"Error importando producto: {e}")
                        db.session.rollback()
                        omitidos += 1
                        continue
                else:
                    omitidos += 1
                
                # Keep-alive cada 2 productos
                if procesados % 2 == 0:
                    yield json.dumps({'tipo': 'heartbeat'}) + '\n\n'
                
                # Enviar progreso cada 100 registros y hacer commit parcial
                if procesados % 100 == 0:
                    try:
                        commit_with_retry()  # Commit parcial con retry
                    except Exception as e:
                        print(f"Error en commit: {e}")
                        db.session.rollback()
                    porcentaje = int((procesados / total) * 100)
                    yield json.dumps({
                        'tipo': 'progreso',
                        'procesados': procesados,
                        'total': total,
                        'porcentaje': porcentaje,
                        'importados': importados,
                        'omitidos': omitidos
                    })
            
            # Enviar progreso final si quedan registros sin reportar
            if procesados % 100 != 0 or procesados == 0:
                porcentaje = 100 if total > 0 else 0
                yield json.dumps({
                    'tipo': 'progreso',
                    'procesados': procesados,
                    'total': total,
                    'porcentaje': porcentaje,
                    'importados': importados,
                    'omitidos': omitidos
                })
        
        try:
            db.session.commit()
        except Exception as e:
            print(f"Error en commit final: {e}")
            db.session.rollback()
            
        yield json.dumps({
            'tipo': 'completado',
            'importados': importados,
            'omitidos': omitidos,
            'mensaje': f'Importados {importados} productos. Omitidos {omitidos} (duplicados o marcas no incluidas).'
        })
    except Exception as e:
        db.session.rollback()
        yield json.dumps({'tipo': 'error', 'mensaje': str(e)})
        raise

def importar_atributos_con_progreso(filepath):
    import json
    import sys
    csv.field_size_limit(sys.maxsize)  # Aumentar límite para campos grandes
    
    importados = 0
    omitidos = 0
    total = 0
    
    try:
        # Contar líneas primero
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            total = sum(1 for _ in f) - 1  # -1 por la cabecera
        
        yield json.dumps({'tipo': 'inicio', 'total': total, 'mensaje': f'Iniciando importación de {total} atributos...'})
        
        # Cargar atributos existentes en memoria para optimizar consultas
        # Estructura: {(producto_id, atributo, valor): True}
        atributos_existentes = {
            (a.producto_id, a.atributo, a.valor): True 
            for a in Atributo.query.with_entities(
                Atributo.producto_id, Atributo.atributo, Atributo.valor
            ).all()
        }
        
        # También cargar SKUs de productos para búsqueda rápida
        productos_por_sku = {p.sku: p.id for p in Producto.query.with_entities(Producto.sku, Producto.id).all() if p.sku}
        productos_por_id_csv = {p.id_csv: p.id for p in Producto.query.with_entities(Producto.id_csv, Producto.id).all() if p.id_csv}
        
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f, delimiter=';')
            procesados = 0
            
            for row in reader:
                procesados += 1
                try:
                    with db.session.no_autoflush:
                        # Primero intentar buscar por SKU si existe en el CSV
                        sku = row.get('SKU', '').strip()
                        producto_id_db = None
                        sku_producto = None
                        
                        if sku and sku in productos_por_sku:
                            # Buscar por SKU en memoria
                            producto_id_db = productos_por_sku[sku]
                            sku_producto = sku
                        
                        # Si no se encontró por SKU, buscar por ProductoId
                        if not producto_id_db:
                            producto_id_csv = int(row.get('ProductoId', 0))
                            if producto_id_csv in productos_por_id_csv:
                                producto_id_db = productos_por_id_csv[producto_id_csv]
                                # Obtener SKU del producto
                                producto = Producto.query.get(producto_id_db)
                                if producto:
                                    sku_producto = producto.sku
                        
                        if producto_id_db:
                            # Verificar si el atributo ya existe para este producto
                            atributo_nombre = row.get('Nombre', '').strip()
                            atributo_valor = row.get('Valor', '').strip()
                            
                            # Buscar en memoria si ya existe este atributo
                            clave_atributo = (producto_id_db, atributo_nombre, atributo_valor)
                            if clave_atributo in atributos_existentes:
                                # Ya existe, lo saltamos
                                omitidos += 1
                            else:
                                # No existe, lo creamos
                                atributo = Atributo(
                                    producto_id=producto_id_db,
                                    sku=sku_producto,  # Guardar el SKU del producto
                                    atributo=atributo_nombre,
                                    valor=atributo_valor,
                                    orden=int(row.get('OrdenEnGrupo', 0) or 0)  # Campo OrdenEnGrupo del CSV
                                )
                                db.session.add(atributo)
                                # Agregar a memoria
                                atributos_existentes[clave_atributo] = True
                                importados += 1
                        else:
                            omitidos += 1
                except Exception as e:
                    print(f"Error importando atributo: {e}")
                    db.session.rollback()  # Rollback en caso de error
                    omitidos += 1
                    continue
                
                # Keep-alive cada 2 atributos
                if procesados % 2 == 0:
                    yield json.dumps({'tipo': 'heartbeat'}) + '\n\n'
                
                # Enviar progreso cada 100 registros y hacer commit parcial
                if procesados % 100 == 0:
                    try:
                        commit_with_retry()  # Commit parcial con retry
                    except Exception as e:
                        print(f"Error en commit: {e}")
                        db.session.rollback()
                    porcentaje = int((procesados / total) * 100)
                    yield json.dumps({
                        'tipo': 'progreso',
                        'procesados': procesados,
                        'total': total,
                        'porcentaje': porcentaje,
                        'importados': importados,
                        'omitidos': omitidos
                    })
            
            # Enviar progreso final si quedan registros sin reportar
            if procesados % 100 != 0 or procesados == 0:
                porcentaje = 100 if total > 0 else 0
                yield json.dumps({
                    'tipo': 'progreso',
                    'procesados': procesados,
                    'total': total,
                    'porcentaje': porcentaje,
                    'importados': importados,
                    'omitidos': omitidos
                })
        
        try:
            commit_with_retry()  # Commit final con retry
        except Exception as e:
            print(f"Error en commit final: {e}")
            db.session.rollback()
            
        yield json.dumps({
            'tipo': 'completado',
            'importados': importados,
            'omitidos': omitidos,
            'mensaje': f'Importados {importados} atributos. Omitidos {omitidos} (duplicados o productos no encontrados).'
        })
    except Exception as e:
        db.session.rollback()
        yield json.dumps({'tipo': 'error', 'mensaje': str(e)})
        raise

def importar_datos_manuales_con_progreso():
    """Genera datos manuales aleatorios para todos los productos existentes"""
    import json
    import random
    from datetime import datetime, timedelta
    
    # Obtener todos los productos
    productos = Producto.query.all()
    total_productos = len(productos)
    
    if total_productos == 0:
        yield json.dumps({'tipo': 'error', 'mensaje': 'No hay productos para generar datos manuales'})
        return
    
    # Filtrar productos que NO tienen datos manuales
    productos_sin_datos = []
    for producto in productos:
        dato_existente = DatosManuales.query.filter_by(sku=producto.sku).first()
        if not dato_existente:
            productos_sin_datos.append(producto)
    
    total = len(productos_sin_datos)
    saltados = total_productos - total
    
    if total == 0:
        yield json.dumps({
            'tipo': 'completado',
            'mensaje': f'Todos los productos ({total_productos}) ya tienen datos manuales',
            'importados': 0,
            'omitidos': saltados
        })
        return
    
    yield json.dumps({
        'tipo': 'inicio',
        'total': total,
        'mensaje': f'Generando datos para {total} productos (saltando {saltados} que ya tienen datos)...'
    })
    
    fabricantes = ['Samsung', 'LG', 'Bosch', 'Siemens', 'Whirlpool', 'Electrolux', 'AEG', 'Miele', 'Teka', 'Balay']
    creados = 0
    
    for i, producto in enumerate(productos_sin_datos, 1):
        try:
            # Generar datos aleatorios
            unidades_vendidas = random.randint(0, 100)
            pvp = round(random.uniform(50.0, 2000.0), 2)
            inventario = random.randint(0, 50)
            
            # Fecha de entrada aleatoria en los últimos 6 meses
            fecha_aleatoria = datetime.now() - timedelta(days=random.randint(1, 180))
            fecha_entrada = fecha_aleatoria.strftime('%d/%m/%Y')
            
            unidades_entrada = random.randint(5, 30)
            fabricante = random.choice(fabricantes)
            
            # Crear nuevo
            nuevo_dato = DatosManuales(
                sku=producto.sku,
                unidades_vendidas=unidades_vendidas,
                pvp=pvp,
                inventario=inventario,
                fecha_entrada=fecha_entrada,
                unidades_entrada=unidades_entrada,
                fabricante=fabricante
            )
            db.session.add(nuevo_dato)
            creados += 1
            
            commit_with_retry()  # Commit con retry
            
            # Keep-alive cada 2 productos
            if i % 2 == 0:
                yield json.dumps({'tipo': 'heartbeat'}) + '\n\n'
            
            # Enviar progreso cada 5 productos o al final
            if i % 5 == 0 or i == total:
                porcentaje = int((i / total) * 100)
                yield json.dumps({
                    'tipo': 'progreso',
                    'porcentaje': porcentaje,
                    'procesados': i,
                    'total': total,
                    'importados': creados,
                    'omitidos': saltados,
                    'mensaje': f'Creando datos {i}/{total} - SKU: {producto.sku}'
                })
        
        except Exception as e:
            yield json.dumps({
                'tipo': 'error',
                'mensaje': f'Error en producto {producto.sku}: {str(e)}'
            })
            continue
    
    yield json.dumps({
        'tipo': 'completado',
        'mensaje': f'Completado: {creados} nuevos creados, {saltados} saltados (ya existían)',
        'importados': creados,
        'omitidos': saltados
    })

@app.route('/eliminar_datos')
def eliminar_datos():
    tipo = request.args.get('tipo', 'todo')
    
    if tipo == 'productos':
        Producto.query.delete()
        flash('Productos eliminados correctamente.')
    elif tipo == 'atributos':
        Atributo.query.delete()
        flash('Atributos eliminados correctamente.')
    elif tipo == 'datos_manuales':
        DatosManuales.query.delete()
        flash('Datos Manuales eliminados correctamente.')
    elif tipo == 'todo':
        # Eliminar en cascada
        DatosManuales.query.delete()
        Atributo.query.delete()
        Producto.query.delete()
        flash('Todos los datos importados eliminados correctamente.')
    
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/add', methods=['POST'])
def add_catalogo():
    codigo = request.form['codigo']
    descripcion = request.form['descripcion']
    marcas = request.form['marcas']
    nuevo_catalogo = Catalogo(codigo=codigo, descripcion=descripcion, marcas=marcas)
    db.session.add(nuevo_catalogo)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/copiar_catalogo', methods=['POST'])
def copiar_catalogo():
    catalogo_origen_id = request.form['catalogo_origen']
    codigo = request.form['codigo']
    descripcion = request.form['descripcion']
    
    # Obtener catálogo origen
    catalogo_origen = Catalogo.query.get_or_404(catalogo_origen_id)
    
    # Crear nuevo catálogo copiando las marcas del origen
    nuevo_catalogo = Catalogo(codigo=codigo, descripcion=descripcion, marcas=catalogo_origen.marcas)
    db.session.add(nuevo_catalogo)
    db.session.flush()  # Para obtener el ID del nuevo catálogo
    
    # Copiar categorías, subcategorías y fichas
    for categoria in catalogo_origen.categorias:
        nueva_categoria = Categoria(
            catalogo_id=nuevo_catalogo.id,
            cod_categoria=categoria.cod_categoria,
            descripcion=categoria.descripcion
        )
        db.session.add(nueva_categoria)
        db.session.flush()
        
        # Copiar subcategorías
        for subcategoria in categoria.subcategorias:
            nueva_subcategoria = Subcategoria(
                categoria_id=nueva_categoria.id,
                cod_categoria=subcategoria.cod_categoria,
                descripcion=subcategoria.descripcion
            )
            db.session.add(nueva_subcategoria)
            db.session.flush()
            
            # Copiar fichas
            for ficha in subcategoria.fichas:
                nueva_ficha = Ficha(
                    subcategoria_id=nueva_subcategoria.id,
                    fila_numero=ficha.fila_numero
                )
                db.session.add(nueva_ficha)
                db.session.flush()
                
                # Copiar tarjetas de la ficha
                for tarjeta in ficha.tarjetas:
                    nueva_tarjeta = Tarjeta(
                        ficha_id=nueva_ficha.id,
                        marca=tarjeta.marca,
                        producto_id=tarjeta.producto_id
                    )
                    db.session.add(nueva_tarjeta)
    
    db.session.commit()
    flash(f'Catálogo copiado exitosamente: {codigo} (con marcas: {catalogo_origen.marcas})', 'success')
    return redirect(url_for('index'))

@app.route('/delete/<int:id>')
def delete_catalogo(id):
    catalogo = Catalogo.query.get_or_404(id)
    # Eliminar en cascada
    for categoria in catalogo.categorias:
        for subcategoria in categoria.subcategorias:
            for ficha in subcategoria.fichas:
                for tarjeta in ficha.tarjetas:
                    db.session.delete(tarjeta)
                db.session.delete(ficha)
            db.session.delete(subcategoria)
        db.session.delete(categoria)
    db.session.delete(catalogo)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/ver_catalogo_completo/<int:catalogo_id>')
def ver_catalogo_completo(catalogo_id):
    catalogo = Catalogo.query.get_or_404(catalogo_id)
    categorias = Categoria.query.filter_by(catalogo_id=catalogo_id).order_by(Categoria.cod_categoria).all()
    marcas = catalogo.marcas.split(',')
    
    # Cargar datos manuales para todos los SKUs en un diccionario
    datos_manuales_dict = {}
    datos_manuales = DatosManuales.query.all()
    for dm in datos_manuales:
        if dm.sku not in datos_manuales_dict:
            datos_manuales_dict[dm.sku] = []
        datos_manuales_dict[dm.sku].append(dm)
    
    # Para cada categoría, cargar sus subcategorías y fichas
    categorias_data = []
    for cat in categorias:
        subcategorias = Subcategoria.query.filter_by(categoria_id=cat.id).order_by(Subcategoria.cod_categoria).all()
        
        subcategorias_data = []
        for subcat in subcategorias:
            fichas = Ficha.query.filter_by(subcategoria_id=subcat.id).order_by(Ficha.fila_numero).all()
            
            # Calcular totales por marca para esta subcategoría
            totales_marca = {}
            total_general = 0
            for marca in marcas:
                count = sum(1 for f in fichas for t in f.tarjetas if t.marca == marca)
                totales_marca[marca] = count
                total_general += count
            
            # Obtener configuración de plantilla para esta subcategoría
            plantilla_config = obtener_plantilla_activa(subcat.id)
            
            subcategorias_data.append({
                'subcategoria': subcat,
                'fichas': fichas,
                'totales_marca': totales_marca,
                'total_general': total_general,
                'plantilla_config': plantilla_config
            })
        
        categorias_data.append({
            'categoria': cat,
            'subcategorias_data': subcategorias_data
        })
    
    return render_template('ver_catalogo_completo.html',
                         catalogo=catalogo,
                         categorias_data=categorias_data,
                         marcas=marcas,
                         datos_manuales_dict=datos_manuales_dict)

@app.route('/configurar/<int:catalogo_id>')
@login_required
def configurar_catalogo(catalogo_id):
    catalogo = Catalogo.query.get_or_404(catalogo_id)
    categorias = Categoria.query.filter_by(catalogo_id=catalogo_id).order_by(Categoria.cod_categoria).all()
    return render_template('configurar.html', catalogo=catalogo, categorias=categorias)

@app.route('/editar_catalogo/<int:catalogo_id>', methods=['POST'])
def editar_catalogo(catalogo_id):
    catalogo = Catalogo.query.get_or_404(catalogo_id)
    descripcion = request.form['descripcion']
    marcas_nuevas = request.form['marcas']
    
    # Obtener marcas actuales y nuevas como listas
    marcas_actuales = set(catalogo.marcas.split(','))
    marcas_nuevas_set = set(marcas_nuevas.split(','))
    
    # Identificar marcas eliminadas
    marcas_eliminadas = marcas_actuales - marcas_nuevas_set
    
    # Eliminar tarjetas de las marcas eliminadas
    if marcas_eliminadas:
        for categoria in catalogo.categorias:
            for subcategoria in categoria.subcategorias:
                for ficha in subcategoria.fichas:
                    tarjetas_a_eliminar = [t for t in ficha.tarjetas if t.marca in marcas_eliminadas]
                    for tarjeta in tarjetas_a_eliminar:
                        db.session.delete(tarjeta)
    
    # Actualizar catálogo
    catalogo.descripcion = descripcion
    catalogo.marcas = marcas_nuevas
    
    db.session.commit()
    
    if marcas_eliminadas:
        flash(f'Catálogo actualizado. Se eliminaron {len(list(marcas_eliminadas))} marca(s) y sus tarjetas asociadas.', 'success')
    else:
        flash('Catálogo actualizado exitosamente.', 'success')
    
    return redirect(url_for('configurar_catalogo', catalogo_id=catalogo_id))

@app.route('/add_categoria/<int:catalogo_id>', methods=['POST'])
def add_categoria(catalogo_id):
    cod_categoria = request.form['cod_categoria']
    descripcion = request.form['descripcion']
    nueva_categoria = Categoria(catalogo_id=catalogo_id, cod_categoria=cod_categoria, descripcion=descripcion)
    db.session.add(nueva_categoria)
    db.session.commit()
    return redirect(url_for('configurar_catalogo', catalogo_id=catalogo_id))

@app.route('/delete_categoria/<int:id>')
def delete_categoria(id):
    categoria = Categoria.query.get_or_404(id)
    catalogo_id = categoria.catalogo_id
    # Eliminar en cascada
    for subcategoria in categoria.subcategorias:
        for ficha in subcategoria.fichas:
            for tarjeta in ficha.tarjetas:
                db.session.delete(tarjeta)
            db.session.delete(ficha)
        db.session.delete(subcategoria)
    db.session.delete(categoria)
    db.session.commit()
    return redirect(url_for('configurar_catalogo', catalogo_id=catalogo_id))

@app.route('/categoria/<int:categoria_id>')
@login_required
def categoria(categoria_id):
    categoria = Categoria.query.get_or_404(categoria_id)
    subcategorias = Subcategoria.query.filter_by(categoria_id=categoria_id).order_by(Subcategoria.cod_categoria).all()
    subcats_options = SUBCATEGORIAS.get(categoria.cod_categoria, [])
    return render_template('categoria.html', categoria=categoria, subcategorias=subcategorias, subcats_options=subcats_options)

@app.route('/add_subcategoria/<int:categoria_id>', methods=['POST'])
def add_subcategoria(categoria_id):
    cod_categoria = request.form['cod_categoria']
    descripcion = request.form['descripcion']
    nueva_subcategoria = Subcategoria(categoria_id=categoria_id, cod_categoria=cod_categoria, descripcion=descripcion)
    db.session.add(nueva_subcategoria)
    db.session.commit()
    return redirect(url_for('categoria', categoria_id=categoria_id))

@app.route('/delete_subcategoria/<int:id>')
def delete_subcategoria(id):
    subcategoria = Subcategoria.query.get_or_404(id)
    categoria_id = subcategoria.categoria_id
    # Eliminar en cascada
    for ficha in subcategoria.fichas:
        for tarjeta in ficha.tarjetas:
            db.session.delete(tarjeta)
        db.session.delete(ficha)
    db.session.delete(subcategoria)
    db.session.commit()
    return redirect(url_for('categoria', categoria_id=categoria_id))

@app.route('/copy_subcategoria/<int:categoria_id>', methods=['POST'])
def copy_subcategoria(categoria_id):
    from_cod_categoria = request.form['from_cod_categoria']
    to_cod_categoria = request.form['to_cod_categoria']
    descripcion = request.form['descripcion']
    
    # Verificar que no sean iguales
    if from_cod_categoria == to_cod_categoria:
        # Aunque el JS lo previene, por seguridad
        return redirect(url_for('categoria', categoria_id=categoria_id))
    
    # Crear nueva subcategoria
    nueva_subcategoria = Subcategoria(categoria_id=categoria_id, cod_categoria=to_cod_categoria, descripcion=descripcion)
    db.session.add(nueva_subcategoria)
    db.session.commit()
    return redirect(url_for('categoria', categoria_id=categoria_id))

@app.route('/fichas/<int:subcategoria_id>')
@login_required
def fichas(subcategoria_id):
    subcategoria = Subcategoria.query.get_or_404(subcategoria_id)
    fichas = Ficha.query.filter_by(subcategoria_id=subcategoria_id).order_by(Ficha.fila_numero).all()
    marcas = subcategoria.categoria.catalogo.marcas.split(',')
    
    # Obtener las categorías de productos que ya están en esta subcategoría
    categorias_productos = db.session.query(Producto.categoria).distinct()\
        .join(Tarjeta, Producto.id == Tarjeta.producto_id)\
        .join(Ficha, Tarjeta.ficha_id == Ficha.id)\
        .filter(Ficha.subcategoria_id == subcategoria_id)\
        .filter(Producto.categoria != None)\
        .filter(Producto.categoria != '')\
        .all()
    categorias_str = ','.join([c[0] for c in categorias_productos]) if categorias_productos else ''
    
    # Calcular totales por marca
    totales_marca = {}
    total_general = 0
    for marca in marcas:
        count = sum(1 for f in fichas for t in f.tarjetas if t.marca == marca)
        totales_marca[marca] = count
        total_general += count
    
    # Cargar datos manuales para todos los SKUs en un diccionario
    datos_manuales_dict = {}
    datos_manuales = DatosManuales.query.all()
    for dm in datos_manuales:
        if dm.sku not in datos_manuales_dict:
            datos_manuales_dict[dm.sku] = []
        datos_manuales_dict[dm.sku].append(dm)
    
    # Obtener configuración de plantilla activa
    plantilla_config = obtener_plantilla_activa(subcategoria_id)
    
    return render_template('fichas.html', 
                         subcategoria=subcategoria, 
                         fichas=fichas, 
                         marcas=marcas, 
                         totales_marca=totales_marca, 
                         total_general=total_general,
                         datos_manuales_dict=datos_manuales_dict,
                         categorias=categorias_str,
                         plantilla_config=plantilla_config)

@app.route('/ver_categoria_completa/<int:categoria_id>')
def ver_categoria_completa(categoria_id):
    categoria = Categoria.query.get_or_404(categoria_id)
    subcategorias = Subcategoria.query.filter_by(categoria_id=categoria_id).order_by(Subcategoria.cod_categoria).all()
    marcas = categoria.catalogo.marcas.split(',')
    
    # Cargar datos manuales para todos los SKUs en un diccionario
    datos_manuales_dict = {}
    datos_manuales = DatosManuales.query.all()
    for dm in datos_manuales:
        if dm.sku not in datos_manuales_dict:
            datos_manuales_dict[dm.sku] = []
        datos_manuales_dict[dm.sku].append(dm)
    
    # Para cada subcategoría, cargar sus fichas
    subcategorias_data = []
    for subcat in subcategorias:
        fichas = Ficha.query.filter_by(subcategoria_id=subcat.id).order_by(Ficha.fila_numero).all()
        
        # Calcular totales por marca para esta subcategoría
        totales_marca = {}
        total_general = 0
        for marca in marcas:
            count = sum(1 for f in fichas for t in f.tarjetas if t.marca == marca)
            totales_marca[marca] = count
            total_general += count
        
        # Obtener configuración de plantilla para esta subcategoría
        plantilla_config = obtener_plantilla_activa(subcat.id)
        
        subcategorias_data.append({
            'subcategoria': subcat,
            'fichas': fichas,
            'totales_marca': totales_marca,
            'total_general': total_general,
            'plantilla_config': plantilla_config
        })
    
    return render_template('ver_categoria_completa.html',
                         categoria=categoria,
                         subcategorias_data=subcategorias_data,
                         marcas=marcas,
                         datos_manuales_dict=datos_manuales_dict)

@app.route('/ver_fichas/<int:subcategoria_id>')
def ver_fichas(subcategoria_id):
    subcategoria = Subcategoria.query.get_or_404(subcategoria_id)
    fichas = Ficha.query.filter_by(subcategoria_id=subcategoria_id).order_by(Ficha.fila_numero).all()
    marcas = subcategoria.categoria.catalogo.marcas.split(',')
    
    # Calcular totales por marca
    totales_marca = {}
    total_general = 0
    for marca in marcas:
        count = sum(1 for f in fichas for t in f.tarjetas if t.marca == marca)
        totales_marca[marca] = count
        total_general += count
    
    # Cargar datos manuales para todos los SKUs en un diccionario
    datos_manuales_dict = {}
    datos_manuales = DatosManuales.query.all()
    for dm in datos_manuales:
        if dm.sku not in datos_manuales_dict:
            datos_manuales_dict[dm.sku] = []
        datos_manuales_dict[dm.sku].append(dm)
    
    # Obtener configuración de plantilla activa
    plantilla_config = obtener_plantilla_activa(subcategoria_id)
    
    return render_template('ver_fichas.html', 
                         subcategoria=subcategoria, 
                         fichas=fichas, 
                         marcas=marcas, 
                         totales_marca=totales_marca, 
                         total_general=total_general,
                         datos_manuales_dict=datos_manuales_dict,
                         plantilla_config=plantilla_config)

@app.route('/add_fila/<int:subcategoria_id>')
def add_fila(subcategoria_id):
    max_fila = db.session.query(db.func.max(Ficha.fila_numero)).filter_by(subcategoria_id=subcategoria_id).scalar() or 0
    nueva_fila = Ficha(subcategoria_id=subcategoria_id, fila_numero=max_fila + 1)
    db.session.add(nueva_fila)
    db.session.commit()
    return redirect(url_for('fichas', subcategoria_id=subcategoria_id))

@app.route('/delete_fila/<int:id>')
def delete_fila(id):
    ficha = Ficha.query.get_or_404(id)
    subcategoria_id = ficha.subcategoria_id
    # Eliminar en cascada
    for tarjeta in ficha.tarjetas:
        db.session.delete(tarjeta)
    db.session.delete(ficha)
    db.session.commit()
    return redirect(url_for('fichas', subcategoria_id=subcategoria_id))

@app.route('/buscar_productos_ajax')
def buscar_productos_ajax():
    buscar = request.args.get('q', '').strip()
    marca = request.args.get('marca', '').strip()
    categoria = request.args.get('categoria', '').strip()
    
    if not buscar or len(buscar) < 2:
        return {'productos': []}
    
    query = Producto.query.filter(
        db.or_(
            Producto.sku.like(f'%{buscar}%'),
            Producto.titulo.like(f'%{buscar}%'),
            Producto.descripcion.like(f'%{buscar}%')
        )
    )
    
    # Filtrar por marca
    if marca:
        query = query.filter(Producto.marca == marca)
    
    # Filtrar por categoría del producto
    if categoria:
        query = query.filter(Producto.categoria == categoria)
    
    productos = query.limit(10).all()
    
    return {
        'productos': [{
            'id': p.id,
            'sku': p.sku,
            'marca': p.marca,
            'titulo': p.titulo,
            'dimensiones': p.dimensiones,
            'color': p.color,
            'categoria': p.categoria
        } for p in productos]
    }

@app.route('/add_tarjeta/<int:ficha_id>/<marca>', methods=['POST'])
def add_tarjeta(ficha_id, marca):
    ficha = Ficha.query.get_or_404(ficha_id)
    producto_id = request.form.get('producto_id', '').strip()
    
    if not producto_id:
        flash('Debe seleccionar un producto', 'error')
        return redirect(url_for('fichas', subcategoria_id=ficha.subcategoria_id))
    
    # Buscar el producto
    producto = Producto.query.get(int(producto_id))
    
    if not producto:
        flash('Producto no encontrado', 'error')
        return redirect(url_for('fichas', subcategoria_id=ficha.subcategoria_id))
    
    # Crear la tarjeta
    nueva_tarjeta = Tarjeta(
        ficha_id=ficha.id,
        marca=marca,
        producto_id=producto.id
    )
    
    db.session.add(nueva_tarjeta)
    db.session.commit()
    
    flash(f'Tarjeta agregada: {producto.sku} - {producto.descripcion}', 'success')
    return redirect(url_for('fichas', subcategoria_id=ficha.subcategoria_id))

@app.route('/delete_tarjeta/<int:id>')
def delete_tarjeta(id):
    tarjeta = Tarjeta.query.get_or_404(id)
    subcategoria_id = tarjeta.ficha.subcategoria_id
    db.session.delete(tarjeta)
    db.session.commit()
    flash('Tarjeta eliminada correctamente.', 'success')
    return redirect(url_for('fichas', subcategoria_id=subcategoria_id))

# ===================================================================
# GESTIÓN DE PLANTILLAS DE TARJETAS
# ===================================================================

def obtener_plantilla_activa(subcategoria_id):
    """
    Obtiene la plantilla activa para una subcategoría siguiendo la jerarquía:
    subcategoria > categoria > catalogo > general (default)
    Retorna un diccionario con campos_ficha y atributos_seleccionados
    """
    subcategoria = Subcategoria.query.get(subcategoria_id)
    if not subcategoria:
        return {'campos_ficha': ['sku', 'titulo', 'ean', 'estado_referencia', 'color'], 'atributos_seleccionados': []}
    
    # Buscar plantilla específica de subcategoría
    plantilla = PlantillaTarjeta.query.filter_by(subcategoria_id=subcategoria_id).first()
    if plantilla:
        return {
            'campos_ficha': json.loads(plantilla.campos_ficha),
            'atributos_seleccionados': json.loads(plantilla.atributos_seleccionados)
        }
    
    # Buscar plantilla de categoría
    plantilla = PlantillaTarjeta.query.filter_by(categoria_id=subcategoria.categoria_id, subcategoria_id=None).first()
    if plantilla:
        return {
            'campos_ficha': json.loads(plantilla.campos_ficha),
            'atributos_seleccionados': json.loads(plantilla.atributos_seleccionados)
        }
    
    # Buscar plantilla de catálogo
    plantilla = PlantillaTarjeta.query.filter_by(catalogo_id=subcategoria.categoria.catalogo_id, categoria_id=None, subcategoria_id=None).first()
    if plantilla:
        return {
            'campos_ficha': json.loads(plantilla.campos_ficha),
            'atributos_seleccionados': json.loads(plantilla.atributos_seleccionados)
        }
    
    # Buscar plantilla general (todos null)
    plantilla = PlantillaTarjeta.query.filter_by(catalogo_id=None, categoria_id=None, subcategoria_id=None).first()
    if plantilla:
        return {
            'campos_ficha': json.loads(plantilla.campos_ficha),
            'atributos_seleccionados': json.loads(plantilla.atributos_seleccionados)
        }
    
    # Default: configuración general
    return {
        'campos_ficha': ['sku', 'titulo', 'ean', 'estado_referencia', 'color'],
        'atributos_seleccionados': []
    }

@app.route('/obtener_atributos_categoria/<int:categoria_id>')
@login_required
def obtener_atributos_categoria(categoria_id):
    """
    Obtiene todos los atributos únicos disponibles en productos de una categoría
    """
    categoria = Categoria.query.get_or_404(categoria_id)
    
    # Obtener todos los códigos de categoría (categoría del producto) asociados a esta categoría
    # a través de las subcategorías y sus productos
    subcategorias = Subcategoria.query.filter_by(categoria_id=categoria_id).all()
    subcategoria_ids = [s.id for s in subcategorias]
    
    # Obtener productos de estas subcategorías
    productos_ids = db.session.query(Tarjeta.producto_id).distinct()\
        .join(Ficha, Tarjeta.ficha_id == Ficha.id)\
        .filter(Ficha.subcategoria_id.in_(subcategoria_ids))\
        .filter(Tarjeta.producto_id.isnot(None))\
        .all()
    
    productos_ids = [p[0] for p in productos_ids]
    
    # Obtener todos los atributos únicos de estos productos
    atributos = db.session.query(Atributo.atributo).distinct()\
        .filter(Atributo.producto_id.in_(productos_ids))\
        .order_by(Atributo.atributo)\
        .all()
    
    atributos_list = [a[0] for a in atributos]
    
    return jsonify({'atributos': atributos_list})

@app.route('/obtener_plantilla_tarjeta/<int:subcategoria_id>')
@login_required
def obtener_plantilla_tarjeta(subcategoria_id):
    """
    Obtiene la plantilla activa para una subcategoría
    """
    config = obtener_plantilla_activa(subcategoria_id)
    return jsonify(config)

@app.route('/guardar_plantilla_tarjeta', methods=['POST'])
@login_required
def guardar_plantilla_tarjeta():
    """
    Guarda la configuración de plantilla para una subcategoría
    """
    try:
        data = request.get_json()
        subcategoria_id = data.get('subcategoria_id')
        campos_ficha = data.get('campos_ficha', ['sku', 'titulo', 'ean', 'estado_referencia', 'color'])
        atributos_seleccionados = data.get('atributos_seleccionados', [])
        es_generica = data.get('es_generica', False)
        
        subcategoria = Subcategoria.query.get_or_404(subcategoria_id)
        
        if es_generica:
            # Guardar como plantilla genérica de la categoría
            # Eliminar plantilla genérica anterior si existe
            PlantillaTarjeta.query.filter_by(
                categoria_id=subcategoria.categoria_id,
                subcategoria_id=None,
                es_generica=True
            ).delete()
            
            plantilla = PlantillaTarjeta(
                categoria_id=subcategoria.categoria_id,
                subcategoria_id=None,
                campos_ficha=json.dumps(campos_ficha),
                atributos_seleccionados=json.dumps(atributos_seleccionados),
                es_generica=True
            )
        else:
            # Guardar como plantilla específica de la subcategoría
            # Eliminar plantilla anterior si existe
            PlantillaTarjeta.query.filter_by(subcategoria_id=subcategoria_id).delete()
            
            plantilla = PlantillaTarjeta(
                subcategoria_id=subcategoria_id,
                campos_ficha=json.dumps(campos_ficha),
                atributos_seleccionados=json.dumps(atributos_seleccionados),
                es_generica=False
            )
        
        db.session.add(plantilla)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Plantilla guardada correctamente'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# ===================================================================
# FUNCIONALIDAD DE EXPORTACIÓN A PDF ELIMINADA
# Se han eliminado las siguientes rutas:
# - /generar_pdf_fichas/<int:subcategoria_id>
# - /generar_pdf_categoria/<int:categoria_id>
# - /generar_pdf_catalogo/<int:catalogo_id>
# ===================================================================

# Inicializar base de datos al arrancar la aplicación
# Este código solo crea tablas que no existen, NO destruye datos
def init_database():
    """Inicializa la base de datos creando solo las tablas que no existen"""
    try:
        # Crear archivo de prueba para verificar persistencia del disco
        test_file = os.path.join(instance_path, 'DISK_PERSISTENCE_TEST.txt')
        
        if os.path.exists(test_file):
            # Leer contador existente
            with open(test_file, 'r') as f:
                content = f.read()
                try:
                    count = int(content.split(':')[-1].strip())
                    count += 1
                except:
                    count = 1
            print(f"🔄 DISCO PERSISTENTE VERIFICADO - Deploy #{count}")
            with open(test_file, 'w') as f:
                f.write(f"Deploy counter: {count}")
        else:
            print(f"🆕 PRIMER DEPLOY - Creando archivo de prueba")
            with open(test_file, 'w') as f:
                f.write("Deploy counter: 1")
        
        with app.app_context():
            # db.create_all() es SEGURO - solo crea tablas que no existen
            # NO elimina ni modifica datos existentes
            db.create_all()
            
            # Agregar columna categoria si no existe
            try:
                from sqlalchemy import text
                db.session.execute(text("SELECT categoria FROM producto LIMIT 1"))
                print("✅ Columna 'categoria' ya existe en tabla producto")
            except Exception as e:
                print("⚠️  Columna 'categoria' no existe, agregándola...")
                try:
                    db.session.execute(text("ALTER TABLE producto ADD COLUMN categoria VARCHAR(100) DEFAULT ''"))
                    db.session.commit()
                    print("✅ Columna 'categoria' agregada exitosamente")
                except Exception as e2:
                    print(f"❌ Error agregando columna categoria: {e2}")
                    db.session.rollback()
            
            db_file_path = os.path.join(instance_path, 'catalogos_nuevo.db')
            if os.path.exists(db_file_path):
                size = os.path.getsize(db_file_path)
                print(f"✅ Base de datos inicializada. Tamaño: {size:,} bytes")
                
                # Contar registros para verificar que hay datos
                from sqlalchemy import inspect, text
                inspector = inspect(db.engine)
                tables = inspector.get_table_names()
                print(f"📊 Tablas en BD: {', '.join(tables)}")
                
                # Contar catálogos como ejemplo
                try:
                    result = db.session.execute(text("SELECT COUNT(*) FROM catalogo")).scalar()
                    print(f"📚 Total catálogos: {result}")
                except:
                    print(f"ℹ️  No se pudieron contar catálogos (tabla vacía o no existe)")
            else:
                print("✅ Base de datos creada")
    except Exception as e:
        print(f"⚠️  Error inicializando base de datos: {e}")
        import traceback
        traceback.print_exc()
        print("La base de datos se inicializará en la primera petición")

# Ejecutar inicialización solo una vez al arrancar
init_database()

if __name__ == '__main__':
    app.run(debug=True)