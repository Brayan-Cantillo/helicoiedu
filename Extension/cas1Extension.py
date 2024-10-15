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


def case1Extension(data):

    required_fields = ['sistema', 'material',  'C1', 'C2', 'd',
                       'Fmax', 'Fmin', 'Deflexión', 'Fatiga']

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
        C1 = float(data['C1'])
        C2 = float(data['C2'])
        d = diametro_data['valor']  # Usar el valor de d desde la base de datos
        Fmax = float(data['Fmax'])
        Fmin = float(data['Fmin'])
        y = float(data['Deflexión'])
        Fatiga = data['Fatiga']

    except ValueError as e:
        return jsonify({"error": f"Error en los datos proporcionados: {str(e)}"}), 400

    # Validación de materiales

    valid_materials = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    if material not in valid_materials:
        return jsonify({"error": f"El 'Material' seleccionado debe ser uno de los siguientes: {valid_materials}."}), 400

    # Validación opciones de fatiga.
    valid_fatigue = [True, False]
    if Fatiga not in valid_fatigue:
        return jsonify({"error": f"La opción de fatiga seleccionada debe ser una de los siguientes: {valid_fatigue}."}), 400

    # Validación opciones de sistema de unidades
    valid_system = [True, False]
    if sistema not in valid_system:
        return jsonify({"error": f"El sistema seleccionado debe ser uno de los siguientes: {valid_system}."}), 400

    global G

    # Módulo de Corte (G)

    if sistema == True:
        G = 11.5e6
    else:
        G = 79300  # valor cambia a sistema internacional

    # Cálculos caso 1 extensión.
    try:

        exten_D = coil_diam(C1, d)
        exten_taui_1 = tau_i1(C1)
        exten_taui_2 = tau_i2(C1)
        exten_taui = tau_i_ex(exten_taui_1, exten_taui_2)
        exten_Ks = Ks(C1)
        exten_Kw = Kw(C1)
        exten_Kw2 = Kw_2(C2)
        exten_Kb = Kb(C1)
        exten_Fi = Fi(d, exten_D, exten_taui, exten_Ks)
        exten_tau_min = tau_min_ex(d, exten_D, Fmin, exten_Ks)
        exten_tau_max = tau(d, exten_D, Fmax, exten_Ks)
        exten_Sut = Sut(d, float(A), float(B))
        exten_Sus = Sus(exten_Sut)
        exten_Sys_cuerpo = Sys_ex_cuerpo(exten_Sut, material)
        exten_Sys_gancho = Sys_ex_gancho(exten_Sut)
        exten_Sy_gancho = Sy_ex_gancho(exten_Sut)
        exten_sigma_A = sigma_A(exten_Kb, exten_D, d, Fmax)
        exten_tau_B = tau_B(exten_Kw2, exten_D, d, Fmax)
        exten_Ns = Ns(exten_tau_max, exten_Sys_cuerpo)
        exten_NA = NA(exten_Sy_gancho, exten_sigma_A)
        exten_NB = NB(exten_Sys_gancho, exten_tau_B)
        exten_kdef = k_def(Fmax, Fmin, y)
        exten_Na = Na(exten_D, d, G, exten_kdef)
        exten_k = k(exten_D, d, exten_Na, G)
        exten_Nt = Nt_ext(exten_Na)
        exten_Do = Do(exten_D, d)
        exten_Di = Di(exten_D, d)
        exten_Lb = Lb(exten_Nt, d)
        exten_long_ganchos = L_ganchos(exten_D, d)
        exten_Lf = Lf_ex(exten_Lb, exten_D, d)
        exten_ymax = ymax(Fmax, exten_k)

        result = {
            'D': exten_D,
            'taui_1': exten_taui_1,
            'taui_2': exten_taui_2,
            'taui': exten_taui,
            'Ks': exten_Ks,
            'Kw': exten_Kw,
            'Fi': exten_Fi,
            'tau_min': exten_tau_min,
            'tau_max': exten_tau_max,
            'Sut': exten_Sut,
            'Sus': exten_Sus,
            'Sys': exten_Sys_cuerpo,
            'Sys_ex_gancho': exten_Sys_gancho,
            'Sy_ex_gancho': exten_Sy_gancho,
            'Ns': exten_Ns,
            'NA': exten_NA,
            'NB': exten_NB,
            'k': exten_kdef,
            'Na': exten_Na,
            'k': exten_k,
            'Nt': exten_Nt,
            'Do': exten_Do,
            'Di': exten_Di,
            'Lb': exten_Lb,
            'long_ganchos': exten_long_ganchos,
            'Lf': exten_Lf,
            'ymax': exten_ymax,
            'Kb': exten_Kb,
        }

        # Validación de resultados.

        if exten_Ns < 1:
            return jsonify({"error": f"Diseño no favorable. El Factor de seguridad Ns ({exten_Ns}) es menor que uno. Fallo por carga estática"}), 400

        if exten_NA < 1:
            return jsonify({"error": f"Diseño no favorable. El Factor de seguridad Ns ({exten_NA}) es menor que uno. Fallo por carga estática del gancho por flexion"}), 400

        if exten_NB < 1:
            return jsonify({"error": f"Diseño no favorable. El Factor de seguridad Ns ({exten_NB}) es menor que uno. Fallo por carga estática del gancho por torsion"}), 400

        fatiga_result = {}
        # Cálculos de fatiga, extension caso 1.
        if Fatiga:
            fatiga_result = calcular_fatiga_extension(
                Fmax, Fmin, exten_Ks, exten_Kw, exten_D, d, exten_Sus, exten_Kb, exten_tau_min, exten_Sut, C2, sistema)
            result.update(fatiga_result)

         # Validación de resoltados de fatiga.

        comp_Nf = fatiga_result.get('Nf', None)

        if comp_Nf is not None and comp_Nf < 1:
            return jsonify({"error": f"Diseño no favorable. El Factor de seguridad Nf ({comp_Nf}) es menor que uno. Fallo por fatiga"}), 400

        exten_NfgT = fatiga_result.get('NfgT', None)

        if exten_NfgT is not None and exten_NfgT < 1:
            return jsonify({"error": f"Diseño no favorable. El Factor de seguridad NfgT ({exten_NfgT}) es menor que uno. Fallo por fatiga del gancho por torsion"}), 400

        exten_NfgF = fatiga_result.get('NfgF', None)

        if exten_NfgF is not None and exten_NfgF < 1:
            return jsonify({"error": f"Diseño no favorable. El Factor de seguridad NfgF ({exten_NfgF}) es menor que uno. Fallo por fatiga del gancho por flexion"}), 400

    except Exception as e:
        return jsonify({"error": f"Error en el cálculo: {str(e)}"}), 500

    return jsonify(result)
