from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///catalogos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
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

# Crear la base de datos si no existe
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    catalogos = Catalogo.query.all()
    return render_template('index.html', catalogos=catalogos)

@app.route('/add', methods=['POST'])
def add_catalogo():
    codigo = request.form['codigo']
    descripcion = request.form['descripcion']
    marcas = request.form['marcas']
    nuevo_catalogo = Catalogo(codigo=codigo, descripcion=descripcion, marcas=marcas)
    db.session.add(nuevo_catalogo)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/delete/<int:id>')
def delete_catalogo(id):
    catalogo = Catalogo.query.get_or_404(id)
    db.session.delete(catalogo)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/configurar/<int:catalogo_id>')
def configurar_catalogo(catalogo_id):
    catalogo = Catalogo.query.get_or_404(catalogo_id)
    categorias = Categoria.query.filter_by(catalogo_id=catalogo_id).all()
    return render_template('configurar.html', catalogo=catalogo, categorias=categorias)

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
    db.session.delete(categoria)
    db.session.commit()
    return redirect(url_for('configurar_catalogo', catalogo_id=catalogo_id))

@app.route('/categoria/<int:categoria_id>')
def categoria(categoria_id):
    categoria = Categoria.query.get_or_404(categoria_id)
    subcategorias = Subcategoria.query.filter_by(categoria_id=categoria_id).all()
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

if __name__ == '__main__':
    app.run(debug=True)