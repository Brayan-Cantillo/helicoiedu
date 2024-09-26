from flask_sqlalchemy import SQLAlchemy

# Inicializa la extensión SQLAlchemy
db = SQLAlchemy()

# Modelo de la tabla Material


class Material(db.Model):
    __tablename__ = 'material'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)
    A = db.Column(db.Float, nullable=False)
    B = db.Column(db.Float, nullable=False)

    # Relación con la tabla Diametro
    diametros = db.relationship('Diametro', backref='material', lazy=True)

# Modelo de la tabla Diametro


class Diametro(db.Model):
    __tablename__ = 'diametro'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    material_id = db.Column(db.Integer, db.ForeignKey(
        'material.id'), nullable=False)
