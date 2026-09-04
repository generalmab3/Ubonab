# زمان یک گام کنترل‌کننده

import time

import numpy as np

from mlp import MLP
from params import HIDDEN, P_MAX, S0
from physics import hard_layer


def one_step(model, x, s, p_l, p_pv):
    z = model.predict(x)[0, 0]
    u = P_MAX * np.tanh(z)
    return hard_layer(s, u, p_l, p_pv)


def main():
    rng = np.random.default_rng(0)
    model = MLP(12, HIDDEN, 1, seed=7)
    x = rng.normal(size=(1, 12))
    for _ in range(1000):
        one_step(model, x, S0, 0.5, 0.2)
    samples = []
    for _ in range(10):
        t0 = time.perf_counter()
        for _ in range(10000):
            one_step(model, x, S0, 0.5, 0.2)
        samples.append((time.perf_counter() - t0) / 10000 * 1e6)
    arr = np.asarray(samples)
    print("یک گام: {:.3f} ± {:.3f} us".format(arr.mean(), arr.std()))


if __name__ == "__main__":
    main()
