from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///catalogos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Catalogo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True, nullable=False)
    descripcion = db.Column(db.String(200), nullable=False)
    marcas = db.Column(db.String(200), nullable=False)  # Separadas por coma

    def __repr__(self):
        return f'<Catalogo {self.codigo}>'

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

if __name__ == '__main__':
    app.run(debug=True)