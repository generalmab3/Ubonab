# لایه سخت باتری و هزینه گام

import numpy as np

from params import DELTA_T, E_MAX, ETA_C, ETA_D, KAPPA, P_MAX, S_MAX, S_MIN


def hard_layer(s, u, p_l, p_pv):
    s = np.asarray(s, dtype=float)
    u = np.asarray(u, dtype=float)
    p_l = np.asarray(p_l, dtype=float)
    p_pv = np.asarray(p_pv, dtype=float)

    charge_cap = np.maximum(0.0, np.minimum(P_MAX, (S_MAX - s) * E_MAX / (ETA_C * DELTA_T)))
    discharge_cap = np.maximum(0.0, np.minimum(P_MAX, (s - S_MIN) * E_MAX * ETA_D / DELTA_T))
    p_c = np.minimum(np.maximum(u, 0.0), charge_cap)
    p_d = np.minimum(np.maximum(-u, 0.0), discharge_cap)
    s_next = s + ETA_C * p_c * DELTA_T / E_MAX - p_d * DELTA_T / (ETA_D * E_MAX)
    p_g = p_l + p_c - p_pv - p_d
    return p_c, p_d, s_next, p_g


def step_cost(p_g, p_c, p_d, c_b, c_s):
    p_g = np.asarray(p_g, dtype=float)
    buy = np.maximum(p_g, 0.0) * np.asarray(c_b, dtype=float) * DELTA_T
    sell = np.maximum(-p_g, 0.0) * np.asarray(c_s, dtype=float) * DELTA_T
    wear = KAPPA * (np.asarray(p_c, dtype=float) + np.asarray(p_d, dtype=float)) * DELTA_T
    return buy - sell + wear


def power_residual(p_g, p_pv, p_d, p_c, p_l):
    return (
        np.asarray(p_g, dtype=float)
        + np.asarray(p_pv, dtype=float)
        + np.asarray(p_d, dtype=float)
        - np.asarray(p_c, dtype=float)
        - np.asarray(p_l, dtype=float)
    )


def clip_signed_command(p_c_hat, p_d_hat):
    return np.clip(np.asarray(p_c_hat, dtype=float) - np.asarray(p_d_hat, dtype=float), -P_MAX, P_MAX)


def no_battery_program(p_l, p_pv, s0, n):
    zeros = np.zeros(n)
    s = np.full(n, s0)
    p_g = np.asarray(p_l, dtype=float)[:n] - np.asarray(p_pv, dtype=float)[:n]
    return zeros, zeros, s, p_g
