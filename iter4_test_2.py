import sqlite3
from math import inf
import spring_module as sp
from diameters_database import diametros_ES

# Extraemos los diámetros disponibles de la base de datos.
# conexion = sqlite3.connect("MechPropES")
# cursor = conexion.cursor()
# cursor.execute("SELECT DISTINCT diametro FROM PROPIEDADES_ES")
# diametros_ES = [row[0] for row in cursor.fetchall()]
# conexion.close()

# DATOS DE ENTRADA
Do_4 = 1.73
Lf_4 = 4.23
Fmin_4 = 100
Fmax_4 = 150
y_4 = 0.75
C_4 = 8

# Se asume un material.
A_4 = 141040
b_4 = -0.1822
G_4 = 11.5e6

# Tolerancia de la iteración
error_max = 5  # Error relativo máximo permitido (1%)

# Función para calcular los parámetros con un diámetro dado


def calcular_parametros(d, Fmin_4, Fmax_4, y_4, C_4):
    D_4 = sp.D(Do_4, d)
    k4 = sp.k_def(Fmax_4, Fmin_4, y_4)
    Na_4 = sp.Na(D_4, d, G_4, k4)

    if Na_4 == 0:  # Validación para evitar división por cero
        # Devolver un error infinito, Ns_4, Ns_4_cierre y Lf_4_new nulos
        return inf, None, None, None

    k4_new = sp.k(D_4, d, Na_4, G_4)
    Nt_4 = sp.Nt_cuad_esm(Na_4)
    Ls_4 = sp.Ls(d, Nt_4)
    ychoque_4 = sp.ychoque(y_4)
    yinicial_4 = sp.yinicial(Fmin_4, k4_new)
    Lf_4_new = sp.Lf(Ls_4, y_4, ychoque_4, yinicial_4)

    Ks_4 = sp.Ks(C_4)
    tau_4 = sp.tau(d, D_4, Fmax_4, Ks_4)
    Sut_4 = sp.Sut(d, A_4, b_4)
    Sys_4 = sp.Sys(Sut_4)
    Ns_4 = sp.Ns(tau_4, Sys_4)

    ysolida_4 = sp.ysolida(Lf_4, Ls_4)
    Fsolida_4 = sp.Fsolida(k4_new, ysolida_4)
    tau_cierre_4 = sp.tau_cierre(d, D_4, Fsolida_4, Ks_4)
    Ns_4_cierre = sp.Ns_cierre(tau_cierre_4, Sys_4)

    # Cálculo de error relativo porcentual.
    e = abs(Lf_4_new - Lf_4) / Lf_4 * 100

    return e, Ns_4, Lf_4_new, Ns_4_cierre

# Iterar sobre todos los diámetros disponibles y calcular el error y el factor de seguridad


def encontrar_diametros_validos(Fmin_4, Fmax_4, y_4, C_4):
    diametros_validos = []
    for d in diametros_ES:
        error, Ns_4, Lf_4_new, Ns_4_cierre = calcular_parametros(
            d, Fmin_4, Fmax_4, y_4, C_4)
        # Añadir la condición para que Lf_4_new <= Lf_4 y Ns_4_cierre >= 1
        if error <= error_max and Ns_4 is not None and Ns_4 >= 1 and Lf_4_new <= Lf_4 and Ns_4_cierre >= 1:
            diametros_validos.append((d, error, Ns_4, Lf_4_new, Ns_4_cierre))
    return diametros_validos


# Buscar soluciones iniciales
diametros_validos = encontrar_diametros_validos(Fmin_4, Fmax_4, y_4, C_4)

# Si no se encuentran soluciones, variar los parámetros
if not diametros_validos:
    print("No se encontraron diámetros que cumplan con el criterio inicial.")
    print("Buscando soluciones alternativas modificando Fmin_4, Fmax_4, C_4 y y_4...")

    # Definir rangos de variación (porcentajes de cambio)
    variacion_porcentual = 0.1  # 10% de variación

    rangos_Fmin = [Fmin_4 * (1 - variacion_porcentual),
                   Fmin_4, Fmin_4 * (1 + variacion_porcentual)]
    rangos_Fmax = [Fmax_4 * (1 - variacion_porcentual),
                   Fmax_4, Fmax_4 * (1 + variacion_porcentual)]
    rangos_C = [C_4 * (1 - variacion_porcentual), C_4,
                C_4 * (1 + variacion_porcentual)]
    rangos_y = [y_4 * (1 - variacion_porcentual), y_4,
                y_4 * (1 + variacion_porcentual)]

    for Fmin in rangos_Fmin:
        for Fmax in rangos_Fmax:
            for C in rangos_C:
                for y in rangos_y:
                    diametros_validos = encontrar_diametros_validos(
                        Fmin, Fmax, y, C)
                    if diametros_validos:
                        print(f"Solución encontrada con Fmin_4={Fmin:.2f}, Fmax_4={Fmax:.2f}, C_4={C:.2f}, y_4={y:.2f}:")
                        for d, e, ns, lf_new, ns_cierre in diametros_validos:
                            print(f"Diámetro: {d}, Error relativo: {e:.2f}%, Ns: {ns:.2f}, Lf_4_new: {lf_new:.2f}, Ns_4_cierre: {ns_cierre:.2f}")
                        break
                if diametros_validos:
                    break
            if diametros_validos:
                break
        if diametros_validos:
            break

    if not diametros_validos:
        print("No se encontraron soluciones alternativas que cumplan con los requisitos.")
else:
    print("Los siguientes diámetros cumplen con el criterio de error relativo < 1%, Ns >= 1, y Ns_4_cierre >= 1:")
    for d, e, ns, lf_new, ns_cierre in diametros_validos:
        print(f"Diámetro: {d}, Error relativo: {e:.2f}%, Ns: {ns:.2f}, Lf_4_new: {lf_new:.2f}, Ns_4_cierre: {ns_cierre:.2f}")


