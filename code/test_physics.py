"""Edge-case checks for the analytical hard-constraint layer."""

from __future__ import annotations

import numpy as np

from physics import hard_layer, power_residual
from params import P_MAX, S_MAX, S_MIN


def _check(s, u, p_l, p_pv):
    p_c, p_d, s_next, p_g = hard_layer(s, u, p_l, p_pv)
    r = power_residual(p_g, p_pv, p_d, p_c, p_l)
    assert np.all(p_c >= -1e-12)
    assert np.all(p_d >= -1e-12)
    assert np.all(p_c <= P_MAX + 1e-12)
    assert np.all(p_d <= P_MAX + 1e-12)
    assert np.all(p_c * p_d <= 1e-12)
    assert np.all(s_next >= S_MIN - 1e-9)
    assert np.all(s_next <= S_MAX + 1e-9)
    assert np.max(np.abs(r)) < 1e-12
    return p_c, p_d, s_next, p_g


def test_limits():
    p_l, p_pv = 0.8, 0.3
    for s in (S_MIN, 0.5, S_MAX):
        for u in (-P_MAX, -0.4, 0.0, 0.4, P_MAX):
            _check(s, u, p_l, p_pv)


def test_empty_battery_cannot_discharge():
    p_c, p_d, s_next, _ = _check(S_MIN, -P_MAX, 1.0, 0.0)
    assert p_d == 0.0
    assert s_next >= S_MIN - 1e-12


def test_full_battery_cannot_charge():
    p_c, p_d, s_next, _ = _check(S_MAX, P_MAX, 0.2, 0.9)
    assert p_c == 0.0
    assert s_next <= S_MAX + 1e-12


def test_vectorized():
    rng = np.random.default_rng(0)
    s = rng.uniform(S_MIN, S_MAX, 200)
    u = rng.uniform(-P_MAX, P_MAX, 200)
    p_l = rng.uniform(0.1, 1.2, 200)
    p_pv = rng.uniform(0.0, 0.8, 200)
    _check(s, u, p_l, p_pv)


if __name__ == "__main__":
    test_limits()
    test_empty_battery_cannot_discharge()
    test_full_battery_cannot_charge()
    test_vectorized()
    print("physics layer tests passed")
