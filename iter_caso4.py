import sqlite3
from math import inf
import spring_module as sp

# Extraemos los diámetros disponibles de la base de datos.
conexion = sqlite3.connect("MechPropES")
cursor = conexion.cursor()
cursor.execute("SELECT DISTINCT diametro FROM PROPIEDADES_ES")
diametros_ES = [row[0] for row in cursor.fetchall()]

# DATOS DE ENTRADA
Do_4 = 1.5
Lf_4 = 4
Fmin_4 = 50
Fmax_4 = 100
y_4 = 0.75
C_4 = 5
d_4 = 0.177

# Se asume un material.
A_4 = 141040
b_4 = -0.1822
G_4 = 11.5e6

# Tolerancia de la iteración
error_max = 5  # Error relativo máximo permitido (5%)

# Función para calcular los parámetros con un diámetro dado


def calcular_parametros(d):
    D_4 = sp.D(Do_4, d)
    k4 = sp.k_def(Fmax_4, Fmin_4, y_4)
    Na_4 = sp.Na(D_4, d, G_4, k4)

    if Na_4 == 0:  # Validación para evitar división por cero
        return inf, None  # Devolver un error infinito si Na_4 es 0 y un valor nulo para Ns_4

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

    e = abs(Lf_4_new - Lf_4) / Lf_4 * 100

    return e, Ns_4


# Iterar sobre todos los diámetros disponibles y calcular el error y el factor de seguridad
diametros_validos = []
for d in diametros_ES:
    error, Ns_4 = calcular_parametros(d)
    if error <= error_max and Ns_4 is not None and Ns_4 >= 1:
        diametros_validos.append((d, error, Ns_4))

# Mostrar los resultados
if diametros_validos:
    print("Los siguientes diámetros cumplen con el criterio de error relativo < 5% y Ns >= 1:")
    for d, e, ns in diametros_validos:
        print(f"Diámetro: {d}, Error relativo: {e:.2f}%, Ns: {ns:.2f}")
else:
    print("No se encontraron diámetros que cumplan con el criterio de error relativo < 5% y Ns >= 1.")

# Cierre de la conexión a la base de datos
conexion.close()
