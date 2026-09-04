# MLP دو لایه با آدام، فقط نام‌پای

import numpy as np


def _init_tanh(rng, n_in, n_out):
    bound = np.sqrt(6.0 / (n_in + n_out))
    w = rng.uniform(-bound, bound, size=(n_in, n_out))
    b = np.zeros(n_out)
    return w, b


class MLP:
    def __init__(self, n_in, n_hidden, n_out, seed):
        rng = np.random.default_rng(seed)
        self.w1, self.b1 = _init_tanh(rng, n_in, n_hidden)
        self.w2, self.b2 = _init_tanh(rng, n_hidden, n_hidden)
        self.w3, self.b3 = _init_tanh(rng, n_hidden, n_out)
        self.m = [np.zeros_like(p) for p in self.params()]
        self.v = [np.zeros_like(p) for p in self.params()]
        self.t = 0

    def params(self):
        return [self.w1, self.b1, self.w2, self.b2, self.w3, self.b3]

    def forward(self, x):
        h1 = np.tanh(x @ self.w1 + self.b1)
        h2 = np.tanh(h1 @ self.w2 + self.b2)
        y = h2 @ self.w3 + self.b3
        return y, (x, h1, h2)

    def predict(self, x):
        y, _ = self.forward(x)
        return y

    def _backward(self, cache, dy):
        x, h1, h2 = cache
        dw3 = h2.T @ dy
        db3 = dy.sum(axis=0)
        dh2 = (dy @ self.w3.T) * (1.0 - h2**2)
        dw2 = h1.T @ dh2
        db2 = dh2.sum(axis=0)
        dh1 = (dh2 @ self.w2.T) * (1.0 - h1**2)
        dw1 = x.T @ dh1
        db1 = dh1.sum(axis=0)
        return [dw1, db1, dw2, db2, dw3, db3]

    def adam_step(self, grads, lr, beta1=0.9, beta2=0.999, eps=1e-8):
        self.t += 1
        params = self.params()
        for i, g in enumerate(grads):
            self.m[i] = beta1 * self.m[i] + (1.0 - beta1) * g
            self.v[i] = beta2 * self.v[i] + (1.0 - beta2) * (g * g)
            m_hat = self.m[i] / (1.0 - beta1**self.t)
            v_hat = self.v[i] / (1.0 - beta2**self.t)
            params[i] -= lr * m_hat / (np.sqrt(v_hat) + eps)
        self.w1, self.b1, self.w2, self.b2, self.w3, self.b3 = params


def iterate_minibatches(x, y, batch, rng):
    n = x.shape[0]
    idx = rng.permutation(n)
    for start in range(0, n, batch):
        sl = idx[start : start + batch]
        yield x[sl], y[sl]


def train_mlp(x_train, y_train, x_val, y_val, n_hidden, n_out, seed, lr, batch, epochs, patience, tanh_output=False):
    model = MLP(x_train.shape[1], n_hidden, n_out, seed)
    rng = np.random.default_rng(seed + 101)
    best_val = np.inf
    best_params = [p.copy() for p in model.params()]
    wait = 0
    for _ in range(epochs):
        for xb, yb in iterate_minibatches(x_train, y_train, batch, rng):
            pred, cache = model.forward(xb)
            if tanh_output:
                yhat = np.tanh(pred)
                diff = yhat - yb
                dy = (2.0 / xb.shape[0]) * diff * (1.0 - yhat ** 2)
            else:
                diff = pred - yb
                dy = (2.0 / xb.shape[0]) * diff
            grads = model._backward(cache, dy)
            model.adam_step(grads, lr)
        pred_val = model.predict(x_val)
        if tanh_output:
            pred_val = np.tanh(pred_val)
        val = float(np.mean((pred_val - y_val) ** 2))
        if val < best_val - 1e-12:
            best_val = val
            best_params = [p.copy() for p in model.params()]
            wait = 0
        else:
            wait += 1
            if wait >= patience:
                break
    model.w1, model.b1, model.w2, model.b2, model.w3, model.b3 = best_params
    return model, best_val
