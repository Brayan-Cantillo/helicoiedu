from spring_module import *


def calcular_fatiga_compresion(Fmax, Fmin, C, d, D, comp_Sus, Tratamiento, sistema):

    # Asignar el valor de Sew basado en el tratamiento

    if Tratamiento == 1:
        if sistema == True:
            comp_Sew = 45.0e3
        else:
            comp_Sew = 310  # sistema internacional

    elif Tratamiento == 2:
        if sistema == True:
            comp_Sew = 67.5e3
        else:
            comp_Sew = 465  # sistema internacional

    # Calcular los parámetros de fatiga
    comp_Fa = Fa(Fmax, Fmin)
    comp_Fm = Fm(Fmax, Fmin)
    comp_Ks = Ks(C)
    comp_tau_i = tau_i(comp_Ks, Fmin, D, d)
    comp_tau_m = tau_m(comp_Ks, comp_Fm, D, d)
    comp_Kw = Kw(C)
    comp_tau_a = tau_a(comp_Kw, comp_Fa, D, d)
    comp_Ses = Ses(comp_Sew, comp_Sus)
    comp_Nf = Nfs_comp(comp_Ses, comp_Sus, comp_tau_i, comp_tau_m, comp_tau_a)

    # Resultados
    return {
        "Sew": comp_Sew,
        "Fa": comp_Fa,
        "Fm": comp_Fm,
        "τi": comp_tau_i,
        "τm": comp_tau_m,
        "Kw": comp_Kw,
        "τa": comp_tau_a,
        "Ses": comp_Ses,
        "Nf": comp_Nf
    }


def calcular_fatiga_extension(Fmax, Fmin, Ks, Kw, D, d, Sus, Kb, tau_min, Sut, C2):

    exten_Sew = 45.0e3

    exten_Fa = Fa(Fmax, Fmin)
    exten_Fm = Fm(Fmax, Fmin)
    exten_tau_m = tau_m(Ks, exten_Fm, D, d)
    exten_tau_a = tau_a(Kw, exten_Fa, D, d)
    exten_Ses = Ses(exten_Sew, Sus)
    exten_sigma_a = sigma_a_ex(D, exten_Fa, d, Kb)
    exten_sigma_m = sigma_a_ex(D, exten_Fm, d, Kb)
    exten_sigma_min = sigma_a_ex(D, Fmin, d, Kb)
    exten_Se = Se_ex(exten_Ses)
    exten_Nf = Nfs_comp(exten_Ses, Sus, tau_min, exten_tau_m, exten_tau_a)
    exten_NfgF = Nfb_ex(exten_Se, Sut, exten_sigma_min,
                        exten_sigma_m, exten_sigma_a)
    Kw2 = Kw_2(C2)
    exten_taub_a = tau_a_g(Kw2, d, D, exten_Fa)
    exten_taub_m = tau_m_g(Kw2, d, D, exten_Fm)
    exten_taub_min = tau_min_g(Kw2, d, D, Fmin)
    exten_taub_max = tau_max_g(Kw2, d, D, Fmax)
    exten_NfgT = Nfs(exten_Ses, Sus, exten_taub_min,
                     exten_taub_m, exten_taub_a)

    return {

        'Fa': exten_Fa,
        'Fm': exten_Fm,
        'tau_m': exten_tau_m,
        'tau_a': exten_tau_a,
        'Ses': exten_Ses,
        'sigma_a': exten_sigma_a,
        'sigma_m': exten_sigma_m,
        'sigma_min': exten_sigma_min,
        'Se': exten_Se,
        'Nf': exten_Nf,
        'NfgF': exten_NfgF,
        'Kw2': Kw2,
        'taub_a': exten_taub_a,
        'taub_m': exten_taub_m,
        'taub_min': exten_taub_min,
        'taub_max': exten_taub_max,
        'NfgT': exten_NfgT,
        'Sew': exten_Sew
    }


def calcular_fatiga_torsion(Mmax, Mmin, C, sigma_max_int, sigma_max_ext, sigma_min_ext, Sut, Sy, Tratamiento):

    if Tratamiento == 1:
        tors_Sewb = 78e3
    elif Tratamiento == 2:
        tors_Sewb = 117e3

    tors_Mm = Mm(Mmax, Mmin)
    tors_Ma = Ma(Mmax, Mmin)
    tors_sigma_medio_ext = sigma_medio_ext(sigma_max_ext, sigma_min_ext)
    tors_sigma_alt_ext = sigma_alt_ext(sigma_max_ext, sigma_min_ext)
    tors_Se = Se_tor(tors_Sewb, Sut)
    tors_Nfb = Nfb_tor(tors_Se, Sut, sigma_min_ext,
                       tors_sigma_medio_ext, tors_sigma_alt_ext)
    tors_Nyb = Nyb(Sy, sigma_max_int)

    return {

        'Mm': tors_Mm,
        'Ma': tors_Ma,
        'sigma_medio_ext': tors_sigma_medio_ext,
        'sigma_alt_ext': tors_sigma_alt_ext,
        'Se_tor': tors_Se,
        'Nfb_tor': tors_Nfb,
        'Nyb': tors_Nyb,
        'Sewb': tors_Sewb

    }
