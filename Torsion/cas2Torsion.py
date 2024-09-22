from flask import jsonify
from spring_module import *
from fatigue_calc import *


def case2Torsion(data):
    global E

    # Módulo de Corte (G)
    E = 30e6

    required_fields = ['material', 'A', 'b', 'C', 'd', 'Mmax',
                       'Mmin', 'k', 'L1', 'L2', 'Tratamiento', 'Asentamiento', 'Fatiga']

    # Validaciones de campos requeridos
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"El campo '{field}' es requerido para el caso seleccionado."}), 400

    try:
        material = data['material']
        A = float(data['A'])
        b = float(data['b'])
        C = float(data['C'])
        d = float(data['d'])
        Mmax = float(data['Mmax'])
        Mmin = float(data['Mmin'])
        k = float(data['k'])
        L1 = float(data['L1'])
        L2 = float(data['L2'])
        Tratamiento = int(data['Tratamiento'])  # Asegurar que es entero
        asentamiento = data['Asentamiento']
        Fatiga = data['Fatiga']  # Dejar como booleano
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
        tors_D = coil_diam(C, d)
        tors_Kbi = Kbi(C)
        tors_Kbo = Kbo(C)
        tors_sigma_max_int = sigma_max_int(tors_Kbi, Mmax, d)
        tors_sigma_max_ext = sigma_max_ext(tors_Kbo, Mmax, d)
        tors_sigma_min_ext = sigma_min_ext(tors_Kbo, Mmin, d)
        tors_Sut = Sut(d, A, b)
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

        result = {

            'D': tors_D,
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
            'theta_min': tors_theta_min,
            'theta_max': tors_theta_max,
            'Nyb': tors_Nyb

        }
        # Validación de resultados.
        if tors_Nyb < 1:
            return jsonify({"error": f"Diseño no favorable. El Factor de seguridad Ns ({tors_Nyb}) es menor que uno. Fallo por carga estática"}), 400

        # Cálculos de fatiga, torsion caso 2.
        if Fatiga:
            fatiga_result = calcular_fatiga_torsion(
                Mmax, Mmin, C, tors_sigma_max_int, tors_sigma_max_ext, tors_sigma_min_ext, tors_Sut, tors_Sy, Tratamiento)
            result.update(fatiga_result)

        # Validación de resoltados de fatiga.

        tors_Nfb = fatiga_result.get('Nfb', None)

        if tors_Nfb is not None and tors_Nfb < 1:
            return jsonify({"error": f"Diseño no favorable. El Factor de seguridad Nf ({tors_Nfb}) es menor que uno. Fallo por fatiga"}), 400

    except Exception as e:
        return jsonify({"error": f"Error en el cálculo: {str(e)}"}), 500

    return jsonify(result)
