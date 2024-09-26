from flask import Flask, jsonify, request
from spring_module import *
from fatigue_calc import *
from database import db

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

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://heliedu:V29Wb4ULWsYczhywwNQYaeAeZPmTWwf2@dpg-crqbi9aj1k6c738e54d0-a:5432/heli'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


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


def create_tables():
    db.create_all()


if __name__ == '__main__':
    app.run(debug=True)
