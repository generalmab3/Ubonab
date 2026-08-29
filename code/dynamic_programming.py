"""Grid dynamic programming reference on signed battery power."""

from __future__ import annotations

import numpy as np

from params import E_MAX, N_ACTIONS, P_MAX, S_MAX, S_MIN, SOC_GRID_STEP
from physics import hard_layer, step_cost


def soc_grid():
    n = int(round((S_MAX - S_MIN) / SOC_GRID_STEP)) + 1
    return np.linspace(S_MIN, S_MAX, n)


def action_grid():
    return np.linspace(-P_MAX, P_MAX, N_ACTIONS)


def _interp_value(v_next, s_next, grid):
    s_clip = np.clip(s_next, grid[0], grid[-1])
    pos = (s_clip - grid[0]) / (grid[1] - grid[0])
    i0 = np.floor(pos).astype(int)
    i1 = np.minimum(i0 + 1, grid.size - 1)
    w = pos - i0
    return (1.0 - w) * v_next[i0] + w * v_next[i1]


def solve_reference(p_l, p_pv, c_b, c_s, s0):
    grid = soc_grid()
    actions = action_grid()
    t_horizon = p_l.size
    n_s = grid.size
    n_u = actions.size
    v = np.zeros((t_horizon + 1, n_s))
    policy = np.zeros((t_horizon, n_s), dtype=int)

    s_mesh = np.repeat(grid[:, None], n_u, axis=1)
    u_mesh = np.repeat(actions[None, :], n_s, axis=0)

    for t in range(t_horizon - 1, -1, -1):
        p_c, p_d, s_next, p_g = hard_layer(s_mesh, u_mesh, p_l[t], p_pv[t])
        g = step_cost(p_g, p_c, p_d, c_b[t], c_s[t])
        cont = _interp_value(v[t + 1], s_next, grid)
        total = g + cont
        policy[t] = np.argmin(total, axis=1)
        v[t] = total[np.arange(n_s), policy[t]]

    s = float(np.clip(s0, S_MIN, S_MAX))
    u_path = np.zeros(t_horizon)
    p_c_path = np.zeros(t_horizon)
    p_d_path = np.zeros(t_horizon)
    s_path = np.zeros(t_horizon)
    p_g_path = np.zeros(t_horizon)
    for t in range(t_horizon):
        pos = (s - grid[0]) / (grid[1] - grid[0])
        i = int(np.clip(round(pos), 0, n_s - 1))
        u = actions[policy[t, i]]
        p_c, p_d, s_next, p_g = hard_layer(s, u, p_l[t], p_pv[t])
        u_path[t] = float(p_c - p_d)
        p_c_path[t] = float(p_c)
        p_d_path[t] = float(p_d)
        p_g_path[t] = float(p_g)
        s_path[t] = s
        s = float(s_next)
    s_next_path = np.concatenate([s_path[1:], np.array([s])])
    return {
        "u": u_path,
        "p_c": p_c_path,
        "p_d": p_d_path,
        "p_g": p_g_path,
        "s": s_path,
        "s_next": s_next_path,
        "value0": float(v[0, int(np.clip(round((s0 - grid[0]) / (grid[1] - grid[0])), 0, n_s - 1))]),
    }
