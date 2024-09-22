from flask import jsonify
from spring_module import *
from fatigue_calc import *


def case1Compresion(data):
    global G

    # Módulo de Corte (G)
    G = 11.5e6

    required_fields = ['material', 'A', 'b', 'C', 'd', 'Fmax', 'Fmin',
                       'Deflexión', 'Extremos', 'Tratamiento', 'Asentamiento', 'Fatiga']

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
        Fmax = float(data['Fmax'])
        Fmin = float(data['Fmin'])
        y = float(data['Deflexión'])
        extremos = int(data['Extremos'])
        Tratamiento = int(data['Tratamiento'])
        asentamiento = data['Asentamiento']
        Fatiga = data['Fatiga']

    except ValueError as e:
        return jsonify({"error": f"Error en los datos proporcionados: {str(e)}"}), 400

    # Validación de materiales
    valid_materials = [1, 2, 3, 4, 5]
    if material not in valid_materials:
        return jsonify({"error": f"El 'Material' seleccionado debe ser uno de los siguientes: {valid_materials}."}), 400

    # Validación de extremos para compresión.
    valid_extremos = [1, 2, 3, 4]
    if extremos not in valid_extremos:
        return jsonify({"error": f"El valor de 'Extremos' debe ser uno de: {valid_extremos}."}), 400

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

    # Cálculos caso 1 compresión.
    try:
        comp_D = coil_diam(C, d)
        comp_Ks = Ks(C)
        comp_tau = tau(d, comp_D, Fmax, comp_Ks)
        comp_Sut = Sut(d, A, b)
        comp_Sys = Sys(comp_Sut, material, asentamiento)
        comp_Sus = Sus(comp_Sut)
        comp_k_def = k_def(Fmax, Fmin, y)
        comp_Na = Na(comp_D, d, G, comp_k_def)
        comp_k = k(comp_D, d, comp_Na, G)

        # Casos de extremos
        if extremos == 1:
            comp_Nt = Nt_planos(comp_Na)
        elif extremos == 2:
            comp_Nt = Nt_plan_esm(comp_Na)
        elif extremos == 3:
            comp_Nt = Nt_cuad(comp_Na)
        elif extremos == 4:
            comp_Nt = Nt_cuad_esm(comp_Na)
        else:
            return jsonify({"error": f"El valor de 'Extremos' debe ser uno de: {valid_extremos}."}), 400

        comp_Ls = Ls(d, comp_Nt)
        comp_yinicial = yinicial(Fmin, comp_k)
        comp_ychoque = ychoque(y)
        comp_Lf = Lf(comp_Ls, y, comp_ychoque, comp_yinicial)
        comp_ysolida = ysolida(comp_Lf, comp_Ls)
        comp_Do = Do(comp_D, d)
        comp_Di = Di(comp_D, d)
        comp_Fsolida = Fsolida(comp_k, comp_ysolida)
        comp_tau_cierre = tau_cierre(d, comp_D, comp_Fsolida, comp_Ks)
        comp_rel_pandeo = pandeo(comp_Lf, comp_D)
        comp_Ns = Ns(comp_tau, comp_Sys)
        comp_Ns_cierre = Ns_cierre(comp_tau_cierre, comp_Sys)

        result = {
            'D': comp_D,
            'Sut': comp_Sut,
            'Sys': comp_Sys,
            'Ks': comp_Ks,
            'k': comp_k,
            'Sus': comp_Sus,
            'Ls': comp_Ls,
            'yinicial': comp_yinicial,
            'ychoque': comp_ychoque,
            'Lf': comp_Lf,
            'ysolida': comp_ysolida,
            'Do': comp_Do,
            'Di': comp_Di,
            'Fsolida': comp_Fsolida,
            'tau': comp_tau,
            'tau cierre': comp_tau_cierre,
            'Ns': comp_Ns,
            'Ns cierre': comp_Ns_cierre,
            'Relación de Pandeo': comp_rel_pandeo
        }

        # Validación de resultados.

        if comp_Ns < 1:
            return jsonify({"error": f"Diseño no favorable. El Factor de seguridad Ns ({comp_Ns}) es menor que uno. Fallo por carga estática"}), 400

        if comp_Ns_cierre < 1:
            return jsonify({"error": f"Diseño no favorable. El Factor de seguridad Ns ({comp_Ns_cierre}) es menor que uno. Fallo por carga estática en altura de cierre."}), 400

        if comp_rel_pandeo > 4:
            return jsonify({"error": f"Diseño no favorable. El valor de la relación de pandeo ({comp_Ns_cierre}) es mayor que 4. El resorte podría pandearse."}), 400

        # Cálculos de fatiga, compresión caso 1.
        if Fatiga:
            fatiga_result = calcular_fatiga_compresion(
                Fmax, Fmin, C, d, comp_D, comp_Sus, Tratamiento)
            result.update(fatiga_result)

        # Validación de resoltados de fatiga.

        comp_Nf = fatiga_result.get('Nf', None)

        if comp_Nf is not None and comp_Nf < 1:
            return jsonify({"error": f"Diseño no favorable. El Factor de seguridad Nf ({comp_Nf}) es menor que uno. Fallo por fatiga"}), 400

    except Exception as e:
        return jsonify({"error": f"Error en el cálculo: {str(e)}"}), 500

    return jsonify(result)
