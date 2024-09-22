# ---------- MÓDULO CÁLCULOS RESORTES ---------------
""" Este módulo contiene las funciones requeridas para realizar los cálculos en resortes helicoidales de compresión,
extensión y torsión. 
"""

# Función diámetro medio de resorte.


def coil_diam(C, d):
    """Calcula el diámetro medio del resorte (D) a partir del índice del resorte (C)
    y el diámetro del alambre (d).  
    """
    D = C*d
    return D

# Función Sut


def Sut(d, A, b):
    """Calcula el esfuerzo último a la tensión a partir de d, A y b.
    """
    Sut = A*(d**b)
    return Sut

# Función Sys


def Sys(Sut, material, asentamiento):
    """
    Calcula la resistencia a la fluencia por torsión a partir del Sut, el material y si se considera o no asentamiento.

    Materiales disponibles:

    1. ASTM A227.
    2. ASTM A228.
    3. ASTM A229.
    4. ASTM A232.
    5. ASTM A401.

    """

    if asentamiento == True:

        if material == 1 or material == 2:

            Sys = 0.60*Sut

        elif material == 3 or material == 4 or material == 5:

            Sys = 0.65*Sut

    else:

        if material == 1 or material == 2:

            Sys = 0.45*Sut

        elif material == 3 or material == 4 or material == 5:

            Sys = 0.50*Sut

    return Sys

# Factor de cortante directo


def Ks(C):
    """Calcula el factor de cortante directo a partir del indice de resorte C.
    """
    Ks = 1 + (0.5/C)
    return Ks

# Esfuerzo cortante máximo.


def tau(d, D, Fmax, Ks):
    """Calcula el esfuerzo cortante máximo para un resorte helicoidal de compresión sometido a carga estática.
    """
    from math import pi, pow
    tau = (Ks*((8*Fmax*D)/(pi*pow(d, 3))))
    return tau

# Factor de seguridad contra fluencia


def Ns(tau, Sys):
    """Calcula el factor de seguridad contra fluencia para un resorte helicoidal de compresión sometido a carga estática.
    """
    Ns = Sys/tau

    if Ns < 0:
        Ns = 0.0

    return Ns

# Función Deflexión


def y(F, D, d, Na, G):
    """ Calcula de deflexión del resorte.
    """
    y = ((8*F*(D**3)*Na)/((d**4)*G))
    return y

# Función constante del resorte.


def k(D, d, Na, G):
    """Calcula la constante k para resortes a compresión y extensión.
    """
    k = (((d**4)*(G))/(8*(D**3)*Na))
    return k

# Función k def


def k_def(Fmax, Fmin, y):
    k_def = ((Fmax-Fmin)/(y))
    return k_def


# ------- FUNCIONES NÚMERO DE ESPIRAS -------

# Función Na


def Na(D, d, G, k):
    from math import ceil, floor

    Na = ((d**4)*(G))/(8*(D**3)*k)

    lower_value = (floor(Na*4)/4)

    upper_value = (ceil(Na*4)/4)

    if abs(Na-lower_value) < abs(Na-upper_value):
        return lower_value
    else:
        return upper_value

# Extremos planos


def Nt_planos(Na):
    Nt = Na
    return Nt

# Planos esmerilados


def Nt_plan_esm(Na):
    Nt = Na+1
    return Nt

# Cuadrados


def Nt_cuad(Na):
    Nt = Na+2
    return Nt

# Cuadrados esmerilados


def Nt_cuad_esm(Na):
    Nt = Na+2
    return Nt


# -------- FACTORES GEOMÉTRICOS ---------------

# Función diámetro exterior


def Do(D, d):
    Do = D+d
    return Do

# Función diámetro interior


def Di(D, d):
    Di = D-d
    return Di

# Función altura de cierre


def Ls(d, Nt):
    Ls = d*Nt
    return Ls

# Función yinicial


def yinicial(Fmin, k):
    yinicial = Fmin/k
    return yinicial

# Función ychoque


def ychoque(y):
    ychoque = 0.15*y
    return ychoque


# Función Lf


def Lf(Ls, y, ychoque, yinicial):
    """ Calcula la longitud libre del resorte.
    """
    Lf = Ls+ychoque+yinicial+y
    return Lf


# Función Ls
def ysolida(Lf, Ls):
    ysolida = Lf-Ls
    return ysolida


# Función peso total del resorte


def Wt(D, d, NT, gamma):
    from math import pi
    Wt = ((pi*(d**2)*D*NT*gamma)/(4))
    return Wt


# -------------- FUNCIONES FATIGA COMPRESIÓN  ---------------

# Función fuerza alternante.
def Fa(Fmax, Fmin):
    """Devuelve la fuerza alternante a partir de Fmax y Fmin.
    """
    Fa = (Fmax-Fmin)/2
    return Fa

# Función fuerza media.


def Fm(Fmax, Fmin):
    """Devuelve la fuerza media a partir de Fmax y Fmin.
    """
    Fm = (Fmax+Fmin)/2
    return Fm

# Función Esfuerzo cortante inicial.


def tau_i(Ks, Fmin, D, d):
    from math import pi
    """Calcula es esfuerzo cortante debido a la carga mínima. A partir de Ks, Fmin, D, d.
  """
    tau_i = (Ks*((8*Fmin*D)/(pi*(d**3))))
    return tau_i

# Función Esfuerzo cortante medio.


def tau_m(Ks, Fm, D, d):
    from math import pi
    """Calcula es esfuerzo cortante debido a la carga media a partir de Ks, Fm, D, d.
  """
    tau_m = (Ks*((8*Fm*D)/(pi*(d**3))))
    return tau_m

# Función Factor de Wahl.


def Kw(C):
    """ Calcula el factor de Wahl a partir de el indice de resorte.
    """
    Kw = (((4*C-1)/(4*C-4))+(0.615/C))
    return Kw

# Función Esfuerzo cortante alternante.


def tau_a(Kw, Fa, D, d):
    from math import pi
    """Calcula es esfuerzo cortante debido a la carga alterna.
  """
    tau_a = (Kw*((8*Fa*D)/(pi*(d**3))))
    return tau_a

# Función Sus.


def Sus(Sut):
    """Calcula la resistencia última a cortante a partir de Sut.
    """
    Sus = 0.67*Sut
    return Sus

# Función Ses.


def Ses(Sew, Sus):
    """ Calcula el límite de resistencia a la fatiga por torsión a partir de Sew y Sus. 
    """
    Ses = (0.5*((Sew*Sus)/(Sus-(0.5*Sew))))
    return Ses

# Función factor de seguridad contra fatiga.


def Nfs_comp(Ses, Sus, tau_i, tau_m, tau_a):
    """Calcula el factor de seguridad contra fatiga.
    """
    Nfs = ((Ses*(Sus-tau_i))/((Ses*(tau_m-tau_i)+(Sus*tau_a))))

    if Nfs < 0:
        Nfs = 0.0

    return Nfs

#          ---------- FUNCIONES PANDEO ------------

# Función Fsol


def Fsolida(k, ysolida):
    Fsolida = k*ysolida
    return Fsolida

# Esfuerzo cortante de cierre


def tau_cierre(d, D, Fsolida, Ks):
    """Calcula el esfuerzo cortante máximo para un resorte helicoidal de compresión sometido a carga en su altura de cierre.
    """
    from math import pi

    tau_cierre = ((round(Ks, 2)) *
                  ((8*(round(Fsolida))*(round(D, 2)))/(pi*(d**3))))

    # tau_cierre = (((Ks)) *
    #               ((8*((Fsolida))*((D)))/(pi*(d**3))))

    return tau_cierre


def Ns_cierre(tau_cierre, Sys):
    """Calcula el factor de seguridad de cierre.
    """
    Ns_cierre = (Sys/tau_cierre)

    if Ns_cierre < 0:

        Ns_cierre = 0.0

    return Ns_cierre

# Pandeo


def pandeo(Lf, D):
    """ Verifica si el resorte se pandea o no a partir del criterio Lf/D.

    Si Lf/D > 4 --->  El resorte se pandea.

    """
    pandeo = Lf/D
    return pandeo


# ------------- EXTENSION --------------

# Esfuerzo inicial Fi

def tau_i1(C):
    """ Calcula el esfuerzo inicial Fi en las espiras a partir del índice de resorte (C).
    """
    tau_i1 = ((-4.231*(C**3))+(181.5*(C**2))-(3387*C)+(28640))
    return tau_i1


def tau_i2(C):
    """ Calcula el esfuerzo inicial Fi en las espiras a partir del índice de resorte (C).
    """
    tau_i2 = ((-2.987*(C**3))+(139.7*(C**2))-(3427*C)+(38404))
    return tau_i2

# Esfuerzo inicial tau_i_ex.


def tau_i_ex(tau_i1, tau_i2):
    """" Calcula el Esfuerzo inicial adecuado Fi en las espiras a partir los esfuerzos taui_1 y taui_2.
    """
    tau_i_ex = ((tau_i1+tau_i2)/2)
    return tau_i_ex


# Esfuerzo cortante minimo.


def tau_min_ex(d, D, Fmin, Ks):
    """Calcula el esfuerzo cortante minimo para un resorte helicoidal de extension sometido a carga estática.
    """
    from math import pi, pow
    tau_min_ex = (Ks*((8*Fmin*D)/(pi*pow(d, 3))))
    return tau_min_ex


def Fi(d, D, tau_i_ex, Ks):
    """Calcula la fuerza de tensión inicial (Precarga) en la espira a partir de d, D, tau_i_ex y Ks.
    """
    from math import pi, pow
    Fi = ((pi*(d**3)*tau_i_ex)/(8*Ks*D))
    return Fi


def Sus_ex(Sut):
    """Calcula la resistencia última a cortante a partir de Sut.
    """
    Sus_ex = 0.667*Sut
    return Sus_ex


def Sys_ex_cuerpo(Sut, material):
    """ Calcula la resitencia a la fluencia por torsión en el cuerpo del resorte heloidal de tensión a partir del Sut y el material.

    Materiales disponibles:

    1. ASTM A227.
    2. ASTM A228.
    3. ASTM A229.
    4. ASTM A232.
    5. ASTM A401.

    """

    if material == 1 or material == 2:

        Sys_ex_cuerpo = 0.45*Sut

    elif material == 3 or material == 4 or material == 5:

        Sys_ex_cuerpo = 0.50*Sut

    return Sys_ex_cuerpo


def Sys_ex_gancho(Sut):
    """ Calcula la resitencia a la fluencia por torsión en el gancho del resorte a partir de Sut.
    """

    Sys_ex_gancho = 0.4*Sut

    return Sys_ex_gancho


def Sy_ex_gancho(Sut):
    """ Calcula la resitencia a la fluencia en el gancho del resorte a partir de Sut.
    """

    Sy_ex_gancho = 0.75*Sut

    return Sy_ex_gancho


def Kb(C):
    """Calcula el factor Kb para resortes de extensión.
    """
    Kb = (((4*(C**2))-C-1)/(4*C*(C-1)))
    return Kb

# Esfuerzos en extremos del resorte.


def sigma_A(Kb, D, d, F):

    from math import pi

    sigma_A = (Kb*((16*D*F)/(pi*(d**3)))+((4*F)/(pi*(d**2))))

    return sigma_A


def tau_B(Kw2, D, d, F):

    from math import pi

    tau_B = (Kw2*((8*D*F)/(pi*(d**3))))

    return tau_B


# Funcion para calcular Sigma_a.


def sigma_a_ex(D, Fa, d, Kb):
    from math import pi
    """ Calcula el facor Sigma_a.
    """
    sigma_a_ex = (Kb*((16*Fa*D)/(pi*(d**3))))+((4*Fa)/(pi*d**2))
    return sigma_a_ex


# Funcion para calcular Sigma_m.

def sigma_m_ex(D, Fm, d, Kb):
    from math import pi
    """ Calcula el factor Sigma_m.
    """
    sigma_m_ex = (Kb*((16*Fm*D)/(pi*(d**3))))+((4*Fm)/(pi*d**2))
    return sigma_m_ex


# Funcion para calcular Sigma_min.

def sigma_min_ex(D, Fmin, d, Kb):
    from math import pi
    """ Calcula el factor Sigma_min. 
    """
    sigma_min_ex = (Kb*((16*Fmin*D)/(pi*(d**3))))+((4*Fmin)/(pi*d**2))
    return sigma_min_ex

# Funcion resistencia a la fatica por tension.


def Se_ex(Ses):
    """ Calcula la resistecia a la fatiga por tension 
    """
    Se_ex = ((Ses)/(0.67))
    return Se_ex


# Funcion para el factor de seguridad.
def Nfb_ex(Se, Sut, sigma_min_ex, sigma_m_ex, sigma_a_ex):
    """ Calcula el factor de seguridad
    """
    Nfb_ex = ((Se*(Sut-sigma_min_ex)) /
              (Se*(sigma_m_ex-sigma_min_ex)+(Sut*sigma_a_ex)))

    if Nfb_ex < 0:

        Nfb_ex = 0.0

    return Nfb_ex


# Funcion para R2.
def R2(C2, d):
    """ Calcula el valor de radio de doblez con C supuesta mayor que 4. 
    """
    R2 = ((C2*d)/2)
    return R2


# Funcion para Kw_2.
def Kw_2(C2):
    """Calcula el valor de Kw_2
    """
    Kw_2 = (((4*C2)-1)/((4*C2)-4))
    return Kw_2

# Funcion calculo de esfuerzos para ganchos extremos alternante.


def tau_a_g(Kw_2, d, D, Fa):
    """ Calcula esfuerzo alternante en gancho extremo  
    """
    from math import pi
    tau_a_g = (Kw_2*((8*Fa*D)/(pi*(d**3))))
    return tau_a_g

# Funcion calculo de esfuerzos para ganchos extremos medio.


def tau_m_g(Kw_2, d, D, Fm):
    """ Calcula esfuerzo alternante en gancho extremo  
    """
    from math import pi
    tau_m_g = (Kw_2*((8*Fm*D)/(pi*(d**3))))
    return tau_m_g

# Funcion calculo de esfuerzos para ganchos extremos minimo.


def tau_min_g(Kw_2, d, D, Fmin):
    """ Calcula esfuerzo alternante en gancho extremo  
    """
    from math import pi
    tau_min_g = (Kw_2*((8*Fmin*D)/(pi*(d**3))))
    return tau_min_g


def tau_max_g(Kw_2, d, D, Fmax):
    """ Calcula esfuerzo alternante en gancho extremo  
    """
    from math import pi
    tau_max_g = (Kw_2*((8*Fmax*D)/(pi*(d**3))))
    return tau_max_g

# Funcion factor de seguridad contra fatiga por torsion en ganchos extremos.


def Nfs(Ses, Sus, tau_min_g, tau_m_g, tau_a_g):
    """ Calcula el factor de seguridad en ganchos extremos 
    """
    Nfs = ((Ses*(Sus-tau_min_g))/(Ses*(tau_m_g-tau_min_g)+(Sus*tau_a_g)))

    if Nfs < 0:

        Nfs = 0.0

    return Nfs

# Factor de Seguridad Estático Ganchos Por Flexión


def NA(Sy, Sigma_a):

    NA = Sy/Sigma_a

    if NA < 0:

        NA = 0.0

    return NA

# Factor de Seguridad Estático Ganchos Por Torsión


def NB(Ssy, tau_max):

    NB = Ssy/tau_max

    if NB < 0:

        NB = 0.0

    return NB


# Número total de espiras extensión


def Nt_ext(Na):
    Nt_ext = Na + 1
    return Nt_ext


def Lb(Nt, d):
    """ Calcula la longitud de la espiral a partir de Nt y d.
    """
    Lb = Nt*d
    return Lb


def Lf_ex(Lb, D, d):
    """ Calcula la longitud libre para un resorte a extensión.
    """
    Lf_ex = Lb + 2*(D-d)
    return Lf_ex


def ymax(Fmax, k):
    ymax = (Fmax)/k
    return ymax


def L_ganchos(D, d):
    """ Calcula la longitud de un gancho estándar, equivalente al diámetro interno de la espira.
    """
    L_ganchos = (D-d)
    return L_ganchos

# ------------- TORSION --------------


def Mm(Mmax, Mmin):
    """ Calcula el momento medio a partir de Mmax, Mmin.
    """
    Mm = (Mmax+Mmin)/2
    return Mm


def Ma(Mmax, Mmin):
    """ Calcula el momento alternante a partir de Mmax, Mmin.
    """
    Ma = (Mmax-Mmin)/2
    return Ma


def Kbi(C):
    """Calcula el factor de flexión Wahl para superficie interior.
    """
    Kbi = (((4*(C**2))-C-1)/(4*C*(C-1)))
    return Kbi


def sigma_max_int(Kbi, Mmax, d):
    """Calcula el esfuerzo de compresión máximo en la superficie interior de la espira.
    """
    from math import pi
    sigma_max_int = Kbi*((32*Mmax)/(pi*(d**3)))
    return sigma_max_int


def Kbo(C):
    """Calcula el factor de flexión Wahl para superficie exterior.
    """
    Kbo = (((4*(C**2))+C-1)/(4*C*(C+1)))
    return Kbo


def sigma_max_ext(Kbo, Mmax, d):
    """Calcula el esfuerzo de compresión máximo en la superficie exterior de la espira.
    """
    from math import pi
    sigma_max_ext = Kbo*((32*Mmax)/(pi*(d**3)))
    return sigma_max_ext


def sigma_min_ext(Kbo, Mmin, d):
    """Calcula el esfuerzo de compresión mínimo en la superficie exterior de la espira.
    """
    from math import pi
    sigma_min_ext = Kbo*((32*Mmin)/(pi*(d**3)))
    return sigma_min_ext


def sigma_medio_ext(sigma_max_ext, sigma_min_ext):
    """ Calcula el esfuerzo de compresión medio en la superficie exterior de la espira.
    """
    sigma_medio_ext = ((sigma_max_ext+sigma_min_ext)/2)
    return sigma_medio_ext


def sigma_alt_ext(sigma_max_ext, sigma_min_ext):
    """ Calcula el esfuerzo de compresión alternante en la superficie exterior de la espira.
    """
    sigma_alt_ext = ((sigma_max_ext-sigma_min_ext)/2)
    return sigma_alt_ext


def Sy_torsion(Sut, material, asentamiento):
    """Calcula la resistencia a la fluencia en función de Sut, material y si se considera o no remoción del asentamiento.

    Materiales disponibles:

    1. ASTM A227.
    2. ASTM A228.
    3. ASTM A229.
    4. ASTM A232.
    5. ASTM A401.

    """

    if asentamiento == True:

        Sy = 1.0*Sut

    else:

        if material == 1 or material == 2:

            Sy = 0.80*Sut

        elif material == 3 or material == 4 or material == 5:

            Sy = 0.85*Sut

    return Sy


def Se_tor(Sewb, Sut):
    """Calcula la resistencia  a la fatiga a partir de una resistencia física de ciclo totalmente invertido.
    """
    Se_tor = (0.5*((Sewb*Sut)/(Sut-(0.5*Sewb))))
    return Se_tor


def Nfb_tor(Se_tor, Sut, sigma_min_ext, sigma_medio_ext, sigma_alt_ext):
    """ Calcula el factor de seguridad para las espiras en flexión.
    """
    Nfb_tor = ((Se_tor*(Sut-sigma_min_ext)) /
               (Se_tor*(sigma_medio_ext-sigma_min_ext)+Sut*sigma_alt_ext))

    if Nfb_tor < 0:

        Nfb_tor = 0.0

    return Nfb_tor


def Nyb(Sy, sigma_max_int):
    """Calcula el factor de seguridad estático contra fluencia.
    """
    Nyb = Sy/sigma_max_int

    if Nyb < 0:

        Nyb = 0.0

    return Nyb


def k_torsion(Mmax, Mmin, theta):
    """Calcula la constante de resortes a partir de dos momentos especificados para su flexión relativa.
    """
    k_torsion = (Mmax-Mmin)/(theta/360)
    return k_torsion


def k_def_tor(E, d, D, Na):
    """Calcula la constante de resorte definida para torsión.
    """
    k_def_tor = (((d**4)*E)/(10.8*D*Na))
    return k_def_tor


def Na_tor(d, E, D, k):
    Na_tor = (((d**4)*E)/(10.8*D*k))
    return Na_tor


def Ne(L1, L2, D):
    """Calcula las espiras activas del resorte.
    """
    from math import pi
    Ne = ((L1+L2)/(3*pi*D))
    return Ne


def Nb(Na, Ne):
    """Calcula el número de espiras en el cuerpo del resorte.
    """
    Nb = Na - Ne
    return Nb


def theta_min(Mmin, D, Na, d, E):
    """ Calcula la deflexión mínima del resorte. 
    """
    theta_min = 360*(10.8*((Mmin*D*Na)/((d**4)*E)))
    return theta_min


def theta_max(Mmax, D, Na, d, E):
    """ Calcula la deflexión máxima del resorte. 
    """
    theta_max = 360*(10.8*((Mmax*D*Na)/((d**4)*E)))
    return theta_max


def theta(Mmax, Mmin, k):
    theta = (Mmax-Mmin)/(k/360)
    return theta


def def_Mmax(k, thetamax):
    def_Mmax = (k*thetamax)/360
    return def_Mmax


def def_Mmin(k, thetamin):
    def_Mmin = (k*thetamin)/360
    return def_Mmin


def def_Di_min(D, Nb, theta, d):
    def_Di_min = (((D*Nb)/(Nb+(theta/360)))-d)
    return def_Di_min


# calcula las fuerzas maximas y minimas


def Fmax(k, ymax):
    Fmax = k*ymax
    return Fmax


def Fmin(k, ymin):
    Fmin = k*ymin
    return Fmin


def y_cal(Fmax, Fmin, k):
    y_cal = (Fmax-Fmin)/k
    return y_cal


def D(Do_def, d):
    """ Calcula el diámetro medio del resorte conociendo el diámetro externo y asumiendo un diámetro de espira.
    """
    D = Do_def - d

    return D
