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


def case4Compresion(data):

    required_fields = ['sistema', 'material', 'C', 'd', 'Do_def', 'Lf_def', 'Fmax', 'Fmin',
                       'k', 'Extremos', 'Tratamiento', 'Asentamiento', 'Fatiga']

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
        Lf_def = float(data['Lf_def'])
        Fmax = float(data['Fmax'])
        Fmin = float(data['Fmin'])
        k_value = float(data['k'])
        extremos = int(data['Extremos'])
        Tratamiento = int(data['Tratamiento'])
        asentamiento = data['Asentamiento']
        Fatiga = data['Fatiga']

    except ValueError as e:
        return jsonify({"error": f"Error en los datos proporcionados: {str(e)}"}), 400

        # Validación de materiales
    valid_materials = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
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

    # Cálculos caso 2 compresión.
    try:
        comp_D_new = D(Do_def, d)
        comp_D = coil_diam(C, d)
        comp_Ks = Ks(C)
        comp_tau = tau(d, comp_D_new, Fmax, comp_Ks)
        comp_Sut = Sut(d, A, B)
        comp_Sys = Sys(comp_Sut, material, asentamiento)
        comp_Sus = Sus(comp_Sut)
        # Renombrado para evitar conflictos
        comp_y_calculado = y_cal(Fmax, Fmin, k_value)
        comp_Na = Na(comp_D_new, d, G, k_value)
        comp_k_new = k(comp_D_new, d, comp_Na, G)

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
        comp_yinicial = yinicial(Fmin, k_value)
        comp_ychoque = ychoque(comp_y_calculado)  # Usa la variable renombrada
        comp_Lf = Lf(round(comp_Ls, 2), round(comp_y_calculado),
                     round(comp_ychoque, 2), round(comp_yinicial, 2))
        comp_ysolida = ysolida(comp_Lf, comp_Ls)
        comp_Do = Do(comp_D_new, d)
        comp_Di = Di(comp_D_new, d)
        comp_Fsolida = Fsolida(k_value, comp_ysolida)
        comp_tau_cierre = tau_cierre(d, comp_D_new, comp_Fsolida, comp_Ks)
        comp_rel_pandeo = pandeo(comp_Lf, comp_D_new)
        comp_Ns = Ns(comp_tau, comp_Sys)
        comp_Ns_cierre = Ns_cierre(comp_tau_cierre, comp_Sys)

        result = {
            'D': comp_D_new,
            'coil_diam': comp_D,
            'Sut': comp_Sut,
            'Sys': comp_Sys,
            'Ks': comp_Ks,
            'y_cal': comp_y_calculado,
            'Nt': comp_Nt,
            'Sus': comp_Sus,
            'Ls': comp_Ls,
            'yinicial': comp_yinicial,
            'ychoque': comp_ychoque,
            'ysolida': comp_ysolida,
            'Lf': comp_Lf,
            'Do': comp_Do,
            'Di': comp_Di,
            'Fsolida': comp_Fsolida,
            'tau': comp_tau,
            'tau cierre': comp_tau_cierre,
            'Ns': comp_Ns,
            'Ns cierre': comp_Ns_cierre,
            'Relación de Pandeo': comp_rel_pandeo,
            'Na': comp_Na,

        }

        # Validación de resultados.

        if comp_Ns < 1:
            return jsonify({"error": f"Diseño no favorable. El Factor de seguridad Ns ({comp_Ns}) es menor que uno. Fallo por carga estática"}), 400

        if comp_Ns_cierre < 1:
            return jsonify({"error": f"Diseño no favorable. El Factor de seguridad Ns ({comp_Ns_cierre}) es menor que uno. Fallo por carga estática en altura de cierre."}), 400

        if comp_rel_pandeo > 4:
            return jsonify({"error": f"Diseño no favorable. El valor de la relación de pandeo ({comp_Ns_cierre}) es mayor que 4. El resorte podría pandearse."}), 400

        fatiga_result = {}
        # Cálculos de fatiga, compresión caso 2.
        if Fatiga:
            fatiga_result = calcular_fatiga_compresion(
                Fmax, Fmin, C, d, comp_D, comp_Sus, Tratamiento, sistema)
            result.update(fatiga_result)

        comp_Nf = fatiga_result.get('Nf', None)

        if comp_Nf is not None and comp_Nf < 1:
            return jsonify({"error": f"Diseño no favorable. El Factor de seguridad Nf ({comp_Nf}) es menor que uno. Fallo por fatiga"}), 400

    except Exception as e:
        return jsonify({"error": f"Error en el cálculo: {str(e)}"}), 500

    return jsonify(result)
