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


def case4Torsion(data):

    required_fields = ['sistema', 'material', 'C', 'd', 'Do_def', 'Mmax',
                       'Mmin', 'k', 'L1', 'L2', 'Tratamiento', 'Asentamiento', 'Fatiga']

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

        sistema = data['sistema']
        A = material_data['A']
        B = material_data['B']
        C = float(data['C'])
        d = diametro_data['valor']  # Usar el valor de d desde la base de datos
        Do_def = float(data['Do_def'])
        Mmax = float(data['Mmax'])
        Mmin = float(data['Mmin'])
        k = float(data['k'])
        L1 = float(data['L1'])
        L2 = float(data['L2'])
        Tratamiento = int(data['Tratamiento'])  # Asegurar que es entero
        asentamiento = data['Asentamiento']
        Fatiga = data['Fatiga']           # Dejar como booleano

    except ValueError as e:
        return jsonify({"error": f"Error en los datos proporcionados: {str(e)}"}), 400

    # Validación de materiales
    valid_materials = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
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

    # Validación opciones de sistema de unidades
    valid_system = [True, False]
    if sistema not in valid_system:
        return jsonify({"error": f"El sistema seleccionado debe ser uno de los siguientes: {valid_system}."}), 400

    global E

    # Módulo de Corte (E)

    if sistema == True:
        E = 30e6
    else:
        E = 206000  # valor cambia a sistema internacional

    # Cálculos caso 1 torsion.
    try:
        tors_D_new = D(Do_def, d)
        tors_D = coil_diam(C, d)
        tors_Kbi = Kbi(C)
        tors_Kbo = Kbo(C)
        tors_sigma_max_int = sigma_max_int(tors_Kbi, Mmax, d)
        tors_sigma_max_ext = sigma_max_ext(tors_Kbo, Mmax, d)
        tors_sigma_min_ext = sigma_min_ext(tors_Kbo, Mmin, d)
        tors_Sut = Sut(d, A, B)
        tors_Sy = Sy_torsion(tors_Sut, material, asentamiento)
        tors_theta = theta(Mmax, Mmin, k)
        tors_k = k_torsion(Mmax, Mmin, tors_theta)
        tors_Na = Na_tor(d, E, tors_D, tors_k)
        tors_k_def = k_def_tor(E, d, tors_D, tors_Na)
        tors_Ne = Ne(L1, L2, tors_D)
        tors_Nb = Nb(tors_Na, tors_Ne)
        tors_theta_min = theta_min(Mmin, tors_D, tors_Na, d, E)
        tors_theta_max = theta_max(Mmax, tors_D, tors_Na, d, E)
        tors_Nyb = Nyb(tors_Sy, tors_sigma_max_int)
        tors_Do = Do(tors_D, d)
        tors_Di_min = def_Di_min(tors_D, tors_Nb, tors_theta, d)

        result = {

            'D': tors_D_new,
            'coil_diam': tors_D,
            'Kbi': tors_Kbi,
            'Kbo': tors_Kbo,
            'sigma_max_int': tors_sigma_max_int,
            'sigma_max_ext': tors_sigma_max_ext,
            'sigma_min_ext': tors_sigma_min_ext,
            'Sut': tors_Sut,
            'Sy': tors_Sy,
            'theta': tors_theta,
            'k': tors_k,
            'k': tors_k_def,
            'Na': tors_Na,
            'Ne': tors_Ne,
            'Nb': tors_Nb,
            'theta_min': tors_theta_min,
            'theta_max': tors_theta_max,
            'Nyb': tors_Nyb,
            'Do': tors_Do,
            'Di': tors_Di_min


        }

        # Validación de resultados.
        # Inicializamos una lista para acumular los errores.

        errores = []

        if tors_Nyb < 1:
            errores.append(f"Diseño no favorable. El Factor de seguridad Ns ({tors_Nyb}) es menor que uno. Fallo por carga estática")

        fatiga_result = {}
       # Cálculos de fatiga, trosion caso 4.
        if Fatiga:
            fatiga_result = calcular_fatiga_torsion(
                Mmax, Mmin, C, tors_sigma_max_int, tors_sigma_max_ext, tors_sigma_min_ext, tors_Sut, tors_Sy, Tratamiento, sistema)
            result.update(fatiga_result)

        tors_Nfb = fatiga_result.get('Nfb', None)
        if tors_Nfb is not None and tors_Nfb < 1:
            errores.append(f"Diseño no favorable. El Factor de seguridad Nf ({tors_Nfb}) es menor que uno. Fallo por fatiga")
                   
         # Si hay errores, los devolvemos como un JSON con código 400
        if errores:
            return jsonify({"errores": errores}), 400

            # Si no hay errores, se puede proceder con el flujo normal.
            # return jsonify({...}), 200

    except Exception as e:
        return jsonify({"error": f"Error en el cálculo: {str(e)}"}), 500

    return jsonify(result)
