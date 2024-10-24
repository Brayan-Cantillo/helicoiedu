from flask import Flask, jsonify, request
from spring_module import *
from fatigue_calc import *
from database import db, Material, Diametro
from faker import Faker
from flask_cors import CORS
import random

# Compresión
from Compresion.cas1Compresion import *
from Compresion.cas2Compresion import *
from Compresion.cas3Compresion import *
from Compresion.cas4Compresion import *
from Compresion.cas5Compresion import *

# Extensión

from Extension.cas1Extension import *
from Extension.cas2Extension import *
from Extension.cas3Extension import *
from Extension.cas4Extension import *
from Extension.cas5Extension import *

# Torsión

from Torsion.cas1Torsion import *
from Torsion.cas2Torsion import *
from Torsion.cas3Torsion import *
from Torsion.cas4Torsion import *
from Torsion.cas5Torsion import *

app = Flask(__name__)

CORS(app)  # permite cors para todas las rutas
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://heliedu:V29Wb4ULWsYczhywwNQYaeAeZPmTWwf2@dpg-crqbi9aj1k6c738e54d0-a:5432/heli'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializa la extensión SQLAlchemy
db.init_app(app)

# Inicializa Faker
fake = Faker()


@app.route('/calculate', methods=['POST'])
def calculate():
    global G

    # Módulo de Corte (G)
    G = 11.5e6

    # Obtener datos del request
    data = request.json

    # Verificar el tipo de cálculo seleccionado
    if 'type' not in data:
        return jsonify({"error": "El campo 'type' es requerido."}), 400

    calculation_type = data['type']

    # Verificar el caso seleccionado.
    if 'case' not in data:
        return jsonify({"error": "El campo 'case' es requerido."}), 400

    # Realizar cálculos según el type seleccionado.
    if calculation_type == 1:
        # Lógica para compresión.
        try:
            if data['case'] == 1:
                result = case1Compresion(data)
            elif data['case'] == 2:
                result = case2Compresion(data)
            elif data['case'] == 3:
                result = case3Compresion(data)
            elif data['case'] == 4:
                result = case4Compresion(data)
            elif data['case'] == 5:
                result = case5Compresion(data)
            else:
                return jsonify({"error": "El tipo de caso seleccionado debe ser: 1, 2, 3, 4, 5"}), 400

        except Exception as e:
            return jsonify({"error": f"Error en el cálculo: {str(e)}"}), 500

        return result

    elif calculation_type == 2:
        # Lógica para extensión.
        try:
            if data['case'] == 1:
                result = case1Extension(data)
            elif data['case'] == 2:
                result = case2Extension(data)
            elif data['case'] == 3:
                result = case3Extension(data)
            elif data['case'] == 4:
                result = case4Extension(data)
            elif data['case'] == 5:
                result = case5Extension(data)
            else:
                return jsonify({"error": "El tipo de caso seleccionado debe ser: 1, 2, 3, 4, 5"}), 400

        except Exception as e:
            return jsonify({"error": f"Error en el cálculo: {str(e)}"}), 500

        return result

    elif calculation_type == 3:
        # Lógica para Torsión.
        try:
            if data['case'] == 1:
                result = case1Torsion(data)
            elif data['case'] == 2:
                result = case2Torsion(data)
            elif data['case'] == 3:
                result = case3Torsion(data)
            elif data['case'] == 4:
                result = case4Torsion(data)
            elif data['case'] == 5:
                result = case5Torsion(data)

            else:
                return jsonify({"error": "Tipo de cálculo no válido. Debe ser '1', '2' o '3'."}), 400

        except Exception as e:
            return jsonify({"error": f"Error en el cálculo: {str(e)}"}), 500

        return result


@app.route('/insertar_datos', methods=['POST'])
def insertar_datos():
    data = request.json  # Obtener el JSON del request

    # Validar campos requeridos en el material
    if not all(key in data for key in ('nombre', 'A', 'B', 'diametros')):
        return jsonify({"error": "Faltan campos requeridos en el material."}), 400

    # Validar que el material no exista
    if Material.query.filter_by(nombre=data['nombre']).first():
        return jsonify({"error": "El nombre del material ya existe."}), 400

    # Crear nuevo material
    nuevo_material = Material(nombre=data['nombre'], A=data['A'], B=data['B'])
    db.session.add(nuevo_material)
    db.session.commit()  # Guardar el material para obtener su ID

    # Validar diámetros
    diametro_nombres = set()  # Usar un conjunto para verificar duplicados
    diametros_insertados = []  # Lista para almacenar los diámetros insertados
    for diametro_data in data['diametros']:
        # Validar campos requeridos en diámetros
        if not all(key in diametro_data for key in ('nombre', 'valor')):
            return jsonify({"error": "Faltan campos requeridos en un diámetro."}), 400

        # Validar que el diámetro no exista
        if diametro_data['nombre'] in diametro_nombres:
            return jsonify({"error": f"El diámetro con nombre '{diametro_data['nombre']}' ya existe."}), 400
        diametro_nombres.add(diametro_data['nombre'])

        nuevo_diametro = Diametro(
            nombre=diametro_data['nombre'], valor=diametro_data['valor'], material_id=nuevo_material.id)
        db.session.add(nuevo_diametro)
        diametros_insertados.append({
            'nombre': nuevo_diametro.nombre,
            'valor': nuevo_diametro.valor
        })

    db.session.commit()  # Guardar los diámetros

    # Retornar los datos insertados
    response_data = {
        "message": "Datos insertados correctamente.",
        "material": {
            "id": nuevo_material.id,
            "nombre": nuevo_material.nombre,
            "A": nuevo_material.A,
            "B": nuevo_material.B
        },
        "diametros": diametros_insertados
    }

    return jsonify(response_data), 201


@app.route('/materiales', methods=['GET'])
def obtener_materiales():
    sistema = request.args.get('sistema', default='true')  # Obtén el sistema de unidades desde los parámetros de la URL
    materiales = Material.query.all()  # Filtrar los materiales por sistema de unidades

    if sistema==True:
            seleccionados = materiales([1, 2, 3, 4, 5])  # Toma los primeros 5 materiales
    else:
            seleccionados = materiales([6, 7, 8, 9, 10])  # Toma los últimos 5 materiales

    resultado = []
    for material in seleccionados:
        resultado.append({
            'id': material.id,
            'nombre': material.nombre,
            'A': material.A,
            'B': material.B
            
        })
    return jsonify(resultado)  # Retorna los materiales en formato JSON



# Ruta para obtener diámetros según el material
@app.route('/diametros/<int:material_id>', methods=['GET'])
def obtener_diametros(material_id):
    # Obtener diámetros por material_id
    diametros = Diametro.query.filter_by(material_id=material_id).all()
    resultado = []
    for diametro in diametros:
        resultado.append({
            'id': diametro.id,
            'nombre': diametro.nombre,
            'valor': diametro.valor
        })
    return jsonify(resultado)  # Retorna los diámetros en formato JSON


@app.route('/update_material/<int:id>', methods=['PUT'])
def update_material(id):
    data = request.get_json()

    # Verificar si el material existe
    material = Material.query.get(id)
    if not material:
        return jsonify({'error': 'ID de material no encontrado'}), 404

    # Actualizar campos opcionales
    if 'nombre' in data:
        material.nombre = data['nombre']
    if 'A' in data:
        material.A = data['A']
    if 'B' in data:
        material.B = data['B']

    # Actualizar o crear diámetros
    if 'diametros' in data:
        diametros_data = data['diametros']
        if not isinstance(diametros_data, list):
            return jsonify({'error': 'El campo diametros debe ser una lista'}), 400

        for diametro_data in diametros_data:
            if 'id' not in diametro_data:
                return jsonify({'error': 'Cada diámetro debe contener un id'}), 400

            diametro = Diametro.query.get(diametro_data['id'])
            if diametro:
                if 'nombre' in diametro_data:
                    diametro.nombre = diametro_data['nombre']
                if 'valor' in diametro_data:
                    diametro.valor = diametro_data['valor']
            else:
                # Si no existe, puedes decidir si crear uno nuevo o ignorar
                if 'nombre' in diametro_data and 'valor' in diametro_data:
                    nuevo_diametro = Diametro(
                        nombre=diametro_data['nombre'],
                        valor=diametro_data['valor'],
                        material_id=id
                    )
                    db.session.add(nuevo_diametro)

    try:
        db.session.commit()
        return jsonify({'mensaje': 'Material y diámetros actualizados exitosamente'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al actualizar: {str(e)}'}), 500


@app.route('/crear_tablas', methods=['POST'])
def crear_tablas():
    db.create_all()
    return "Tablas creadas correctamente."


@app.route('/eliminar_tablas', methods=['DELETE'])
def eliminar_tablas():
    db.drop_all()  # Esto eliminará todas las tablas
    return "Todas las tablas han sido eliminadas."


if __name__ == '__main__':
    app.run(debug=True)
