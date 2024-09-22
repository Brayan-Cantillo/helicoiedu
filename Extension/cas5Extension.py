from flask import jsonify
from spring_module import *
from fatigue_calc import *


def case5Extension(data):
    global G

    # Módulo de Corte (G)
    G = 11.5e6

    required_fields = ['material', 'A', 'b', 'C1', 'C2',
                       'd', 'Do_def', 'Lf_def', 'ymax', 'ymin', 'k', 'Fatiga']

    # Validaciones de campos requeridos
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"El campo '{field}' es requerido para el caso seleccionado."}), 400

    try:
        material = data['material']
        A = float(data['A'])
        b = float(data['b'])
        C1 = float(data['C1'])
        C2 = float(data['C2'])
        d = float(data['d'])
        Do_def = float(data['Do_def'])
        Lf_def = float(data['Lf_def'])
        ymax = float(data['ymax'])
        ymin = float(data['ymin'])
        k_value = float(data['k'])
        Fatiga = data['Fatiga']

    except ValueError as e:
        return jsonify({"error": f"Error en los datos proporcionados: {str(e)}"}), 400

    # Validación de materiales

    valid_materials = [1, 2, 3, 4, 5]

    if material not in valid_materials:
        return jsonify({"error": f"El 'Material' seleccionado debe ser uno de los siguientes: {valid_materials}."}), 400

    # Validación opciones de fatiga.
    valid_fatigue = [True, False]
    if Fatiga not in valid_fatigue:
        return jsonify({"error": f"La opción de fatiga seleccionada debe ser una de los siguientes: {valid_fatigue}."}), 400

    # Cálculos caso 1 extensión.
    try:
        exten_F_max_calc = Fmax(k_value, ymax)
        exten_F_min_calc = Fmin(k_value, ymin)
        exten_D_new = D(Do_def, d)
        exten_D = coil_diam(C1, d)
        exten_Na = Na(exten_D, d, G, k_value)
        exten_k_new = k(exten_D, d, exten_Na, G)
        exten_y_calc = y_cal(exten_F_max_calc, exten_F_min_calc, exten_k_new)
        exten_taui_1 = tau_i1(C1)
        exten_taui_2 = tau_i2(C1)
        exten_taui = tau_i_ex(exten_taui_1, exten_taui_2)
        exten_Ks = Ks(C1)
        exten_Kw = Kw(C1)
        exten_Kw2 = Kw_2(C2)
        exten_Kb = Kb(C1)
        exten_Fi = Fi(d, exten_D, exten_taui, exten_Ks)
        exten_tau_min = tau_min_ex(d, exten_D, exten_F_min_calc, exten_Ks)
        exten_tau_max = tau(d, exten_D, exten_F_max_calc, exten_Ks)
        exten_Sut = Sut(d, float(A), float(b))
        exten_Sus = Sus(exten_Sut)
        exten_Sys_cuerpo = Sys_ex_cuerpo(exten_Sut, material)
        exten_Sys_gancho = Sys_ex_gancho(exten_Sut)
        exten_Sy_gancho = Sy_ex_gancho(exten_Sut)
        exten_sigma_A = sigma_A(exten_Kb, exten_D, d, exten_F_max_calc)
        exten_tau_B = tau_B(exten_Kw2, exten_D, d, exten_F_max_calc)
        exten_Ns = Ns(exten_tau_max, exten_Sys_cuerpo)
        exten_NA = NA(exten_Sy_gancho, exten_sigma_A)
        exten_NB = NB(exten_Sys_gancho, exten_tau_B)
        exten_Nt = Nt_ext(exten_Na)
        exten_Do = Do(exten_D, d)
        exten_Di = Di(exten_D, d)
        exten_Lb = Lb(exten_Nt, d)
        exten_long_ganchos = L_ganchos(exten_D, d)
        exten_Lf = Lf_ex(exten_Lb, exten_D, d)

        result = {
            'Fmax': exten_F_max_calc,
            'Fmin': exten_F_min_calc,
            'D': exten_D_new,
            'coil_diam': exten_D,
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
            'Na': exten_Na,
            'k': exten_k_new,
            'y_cal': exten_y_calc,
            'Nt': exten_Nt,
            'Do': exten_Do,
            'Di': exten_Di,
            'Lb': exten_Lb,
            'long_ganchos': exten_long_ganchos,
            'Lf': exten_Lf,
            'Kb': exten_Kb

        }

        # Validación de resultados.

        if exten_Ns < 1:
            return jsonify({"error": f"Diseño no favorable. El Factor de seguridad Ns ({exten_Ns}) es menor que uno. Fallo por carga estática"}), 400

        if exten_NA < 1:
            return jsonify({"error": f"Diseño no favorable. El Factor de seguridad Ns ({exten_NA}) es menor que uno. Fallo por carga estática del gancho por flexion"}), 400

        if exten_NB < 1:
            return jsonify({"error": f"Diseño no favorable. El Factor de seguridad Ns ({exten_NB}) es menor que uno. Fallo por carga estática del gancho por torsion"}), 400

        # Cálculos de fatiga, compresión caso 1.
        if Fatiga:
            fatiga_result = calcular_fatiga_extension(
                exten_F_max_calc, exten_F_min_calc, exten_Ks, exten_Kw, exten_D, d, exten_Sus, exten_Kb, exten_tau_min, exten_Sut, C2)
            result.update(fatiga_result)

            # Cálculos de fatiga, extension caso 5.
        if Fatiga:
            fatiga_result = calcular_fatiga_extension(
                exten_F_max_calc, exten_F_min_calc, exten_Ks, exten_Kw, exten_D, d, exten_Sus, exten_Kb, exten_tau_min, exten_Sut, C2)
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
