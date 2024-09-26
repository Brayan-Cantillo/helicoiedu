from flask import jsonify, request
from database import db, Diametro


def buscar_diametro_por_id(diametro_id):
    diametro = Diametro.query.get(diametro_id)

    if not diametro:
        return jsonify({"error": "Diámetro no encontrado."}), 404

    resultado = {
        'id': diametro.id,
        'nombre': diametro.nombre,
        'valor': diametro.valor,
        'material_id': diametro.material_id
    }

    return jsonify(resultado)
