from flask import jsonify
from spring_module import *
from fatigue_calc import *
from material_functions import *
from diameter_functions import *


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


def case5Torsion(data):
    global E

    # Módulo de Corte (G)
    E = 30e6

    required_fields = ['material', 'C', 'd', 'Do_def', 'thetamax',
                       'thetamin', 'k', 'L1', 'L2', 'Tratamiento', 'Asentamiento', 'Fatiga']

    # Validaciones de campos requeridos
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"El campo '{field}' es requerido para el caso seleccionado."}), 400

    try:
        # Obtener material desde la base de datos por ID
        material = int(data['material'])
        material_response = buscar_material_por_id(material)

        if material_response.status_code != 200:
            return material_response

        material_data = material_response.json

        # Obtener diámetro desde la base de datos por ID
        diametro_id = int(data['d'])
        diametro_response = buscar_diametro_por_id(diametro_id)

        if diametro_response.status_code != 200:
            return diametro_response

        diametro_data = diametro_response.json

        A = material_data['A']
        B = material_data['B']
        C = float(data['C'])
        d = diametro_data['valor']  # Usar el valor de d desde la base de datos
        Do_def = float(data['Do_def'])
        thetamax = float(data['thetamax'])
        thetamin = float(data['thetamin'])
        k = float(data['k'])
        L1 = float(data['L1'])
        L2 = float(data['L2'])
        Tratamiento = int(data['Tratamiento'])  # Asegurar que es entero
        asentamiento = data['Asentamiento']
        Fatiga = data['Fatiga']           # Dejar como booleano

    except ValueError as e:
        return jsonify({"error": f"Error en los datos proporcionados: {str(e)}"}), 400

    # Validación de materiales
    valid_materials = [1, 2, 3, 4, 5]
    if material not in valid_materials:
        return jsonify({"error": f"El 'Material' seleccionado debe ser uno de los siguientes: {valid_materials}."}), 400

    # Validación de tratamientos para compresión.
    valid_treatments = [1, 2]
    if Tratamiento not in valid_treatments:
        return jsonify({"error": f"El 'Tratamiento' seleccionado debe ser uno de los siguientes: {valid_treatments}."}), 400

    # Validación opciones de fatiga.
    valid_fatigue = [True, False]
    if Fatiga not in valid_fatigue:
        return jsonify({"error": f"La opción de fatiga seleccionada debe ser una de los siguientes: {valid_fatigue}."}), 400

    # Validación opciones de asentamiento
    valid_setting = [True, False]
    if asentamiento not in valid_setting:
        return jsonify({"error": f"La opción de fatiga seleccionada debe ser una de los siguientes: {valid_fatigue}."}), 400

    # Cálculos caso 1 torsion.
    try:
        tors_D_new = D(Do_def, d)
        tors_D = coil_diam(C, d)
        tors_def_Mmax = def_Mmax(k, thetamax)
        tors_def_Mmin = def_Mmin(k, thetamin)
        tors_Kbi = Kbi(C)
        tors_Kbo = Kbo(C)
        tors_sigma_max_int = sigma_max_int(tors_Kbi, tors_def_Mmax, d)
        tors_sigma_max_ext = sigma_max_ext(tors_Kbo, tors_def_Mmax, d)
        tors_sigma_min_ext = sigma_min_ext(tors_Kbo, tors_def_Mmin, d)
        tors_Sut = Sut(d, A, B)
        tors_Sy = Sy_torsion(tors_Sut, material, asentamiento)
        tors_theta = theta(tors_def_Mmax, tors_def_Mmin, k)
        tors_k = k_torsion(tors_def_Mmax, tors_def_Mmin, tors_theta)
        tors_Na = Na_tor(d, E, tors_D, tors_k)
        tors_k_def = k_def_tor(E, d, tors_D, tors_Na)
        tors_Ne = Ne(L1, L2, tors_D)
        tors_Nb = Nb(tors_Na, tors_Ne)
        tors_Nyb = Nyb(tors_Sy, tors_sigma_max_int)
        tors_Do = Do(tors_D, d)
        tors_Di_min = def_Di_min(tors_D, tors_Nb, tors_theta, d)

        result = {

            'D': tors_D_new,
            'coil_diam': tors_D,
            'def_Mmax': tors_def_Mmax,
            'def_Mmin': tors_def_Mmin,
            'Kbi': tors_Kbi,
            'Kbo': tors_Kbo,
            'sigma_max_int': tors_sigma_max_int,
            'sigma_max_ext': tors_sigma_max_ext,
            'sigma_min_ext': tors_sigma_min_ext,
            'Sut': tors_Sut,
            'Sy': tors_Sy,
            'theta': tors_theta,
            'k_torsion': tors_k,
            'k_def_tor': tors_k_def,
            'Na_tor': tors_Na,
            'Ne': tors_Ne,
            'Nb': tors_Nb,
            'Nyb': tors_Nyb,
            'Do': tors_Do,
            'def_Di_min': tors_Di_min

        }

        # Validación de resultados.

        if tors_Nyb < 1:
            return jsonify({"error": f"Diseño no favorable. El Factor de seguridad Ns ({tors_Nyb}) es menor que uno. Fallo por carga estática"}), 400

        fatiga_result = {}
        # Cálculos de fatiga, torsion caso 5.
        if Fatiga:
            fatiga_result = calcular_fatiga_torsion(
                tors_def_Mmax, tors_def_Mmin, C, tors_sigma_max_int, tors_sigma_max_ext, tors_sigma_min_ext, tors_Sut, tors_Sy, Tratamiento)
            result.update(fatiga_result)

        # Validación de resoltados de fatiga.

        tors_Nfb = fatiga_result.get('Nfb', None)

        if tors_Nfb is not None and tors_Nfb < 1:
            return jsonify({"error": f"Diseño no favorable. El Factor de seguridad Nf ({tors_Nfb}) es menor que uno. Fallo por fatiga"}), 400

    except Exception as e:
        return jsonify({"error": f"Error en el cálculo: {str(e)}"}), 500

    return jsonify(result)
