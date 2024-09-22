import sqlite3
from math import inf
import spring_module as sp

# Extraemos los diámetros disponibles de la base de datos.
conexion = sqlite3.connect("MechPropES")
cursor = conexion.cursor()
cursor.execute("SELECT DISTINCT diametro FROM PROPIEDADES_ES")
diametros_ES = [row[0] for row in cursor.fetchall()]

# DATOS DE ENTRADA

Do_5 = 2
Lf_5 = 4.26
ymin_5 = 1.48
ymax_5 = 2.22
C_5 = 8
k5 = 67.4
A_5 = 141040
b_5 = -0.1822
G_5 = 11.5e6

# Función para calcular los parámetros con un diámetro dado


def calcular_parametros(d, k5):
    # Actualizar D_5 con el diámetro dado
    D_5 = sp.D(Do_5, d)

    # Cálculos iniciales
    Fmin_5 = sp.Fmin(k5, ymin_5)
    Fmax_5 = sp.Fmax(k5, ymax_5)

    # Cálculos adicionales
    D_5 = sp.D(Do_5, d)
    Ks_5 = sp.Ks(C_5)
    tau_5 = sp.tau(d, D_5, Fmax_5, Ks_5)
    Sut_5 = sp.Sut(d, A_5, b_5)
    Sys_5 = sp.Sys(Sut_5)
    Ns_5 = sp.Ns(tau_5, Sys_5)
    y_5 = sp.y(Fmax_5, Fmin_5, k5)
    Na_5 = sp.Na(D_5, d, G_5, k5)

    if Na_5 == 0:
        # Devolver un error infinito y demás valores nulos
        return inf, None, None, None, None, None, None, None

    k5_new = sp.k(D_5, d, Na_5, G_5)
    y5_new = sp.y(Fmax_5, Fmin_5, k5_new)

    # CALCULOS RESTANTES
    Nt_5 = sp.Nt_cuad_esm(Na_5)
    Ls_5 = sp.Ls(d, Nt_5)
    yinicial_5 = sp.yinicial(Fmin_5, k5_new)
    ychoque_5 = sp.ychoque(y5_new)
    Lf_5_new = sp.Lf(Ls_5, y5_new, ychoque_5, yinicial_5)
    ysolida_5 = sp.ysolida(Lf_5_new, Ls_5)
    Fsolida_5 = sp.Fsolida(k5_new, ysolida_5)
    tau_cierre_5 = sp.tau_cierre(d, D_5, Fsolida_5, Ks_5)
    Ns_cierre_5 = sp.Ns_cierre(tau_cierre_5, Sys_5)
    pandeo_5 = sp.pandeo(Lf_5, D_5)
    Di_5 = sp.Di(D_5, d)

    # Cálculo de error relativo porcentual.
    error = abs(Lf_5_new - Lf_5) / Lf_5 * 100

    return error, Ns_5, Lf_5_new, Ns_cierre_5, Fmin_5, Fmax_5, D_5, k5_new


# Tolerancia de la iteración
error_max = 5  # Error relativo máximo permitido (5%)

# Encontrar el diámetro válido


def encontrar_diametro_valido(k5):
    for d in diametros_ES:
        error, Ns_5, Lf_5_new, Ns_cierre_5, Fmin_5, Fmax_5, D_5, k5_new = calcular_parametros(
            d, k5)
        if (error <= error_max and
            Ns_5 >= 1 and
            Ns_cierre_5 >= 1 and
            D_5 <= Do_5 and
                Lf_5_new <= Lf_5):
            return d, error, Ns_5, Lf_5_new, Ns_cierre_5, Fmin_5, Fmax_5, D_5, k5_new
    return None


# Buscar el diámetro válido
diametro_valido = encontrar_diametro_valido(k5)
if diametro_valido:
    d, e, ns, lf_new, ns_cierre, fmin, fmax, d_coil, k5_new = diametro_valido
    print(f"Diámetro válido encontrado:")
    print(f"Diámetro: {d}, Error relativo: {e:.2f}%, Ns: {ns:.2f}, Lf_5_new: {lf_new:.2f}, "
          f"Ns_cierre: {ns_cierre:.2f}, Fmin_5: {fmin:.2f}, Fmax_5: {fmax:.2f}, D_5: {d_coil:.2f}, k5_new: {k5_new:.2f}")
else:
    print("No se encontraron diámetros válidos que cumplan con los requisitos.")

# Cierre de la conexión a la base de datos
conexion.close()
