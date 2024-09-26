# functions/material_functions.py
from flask import jsonify, request
from database import db, Material, Diametro


def obtener_materiales_por_diametro(valor):
    diametros = Diametro.query.filter_by(valor=valor).all()
    materiales = []

    for diametro in diametros:
        materiales.append({
            'id': diametro.material.id,
            'nombre': diametro.material.nombre,
            'A': diametro.material.A,
            'B': diametro.material.B
        })

    return jsonify(materiales)


def buscar_material(nombre):
    material = Material.query.filter_by(nombre=nombre).first()

    if not material:
        return jsonify({"error": "Material no encontrado."}), 404

    resultado = {
        'id': material.id,
        'nombre': material.nombre,
        'A': material.A,
        'B': material.B,
        'diametros': [{'id': d.id, 'nombre': d.nombre, 'valor': d.valor} for d in material.diametros]
    }

    return jsonify(resultado)


def buscar_material_por_id(material_id):
    material = Material.query.get(material_id)

    if not material:
        return jsonify({"error": "Material no encontrado."}), 404

    resultado = {
        'id': material.id,
        'nombre': material.nombre,
        'A': material.A,
        'B': material.B,
        'diametros': [{'id': d.id, 'nombre': d.nombre, 'valor': d.valor} for d in material.diametros]
    }

    return jsonify(resultado)
