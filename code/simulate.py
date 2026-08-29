"""Run the archived experiment: DP reference, two networks, metrics and figures."""

from __future__ import annotations

import csv
import json
from datetime import datetime
from pathlib import Path

import numpy as np

from dynamic_programming import solve_reference
from mlp import train_mlp
from params import (
    ASSETS_DIR,
    BATCH,
    CASE_CSV,
    DATA_DIR,
    EPOCHS,
    HIDDEN,
    LR,
    METRICS_JSON,
    P_MAX,
    PATIENCE,
    S0,
    SEEDS,
    TRAIN_FRAC,
    VAL_FRAC,
)
from physics import clip_signed_command, hard_layer, no_battery_program, power_residual, step_cost


def load_case(path: Path):
    stamps, p_l, p_pv, c_b, c_s, hour, work = [], [], [], [], [], [], []
    with path.open(encoding="utf-8") as fh:
        for rec in csv.DictReader(fh):
            stamps.append(datetime.strptime(rec["timestamp"], "%Y-%m-%d %H:%M"))
            p_l.append(float(rec["P_L_kW"]))
            p_pv.append(float(rec["P_PV_kW"]))
            c_b.append(float(rec["c_b"]))
            c_s.append(float(rec["c_s"]))
            hour.append(int(rec["hour"]))
            work.append(int(rec["is_workday"]))
    return {
        "stamp": stamps,
        "p_l": np.asarray(p_l, dtype=float),
        "p_pv": np.asarray(p_pv, dtype=float),
        "c_b": np.asarray(c_b, dtype=float),
        "c_s": np.asarray(c_s, dtype=float),
        "hour": np.asarray(hour, dtype=float),
        "work": np.asarray(work, dtype=float),
    }


def split_sizes(n: int):
    n_train = int(n * TRAIN_FRAC)
    n_val = int(n * VAL_FRAC)
    n_test = n - n_train - n_val
    return n_train, n_val, n_test


def lookahead(arr, shift):
    idx = np.minimum(np.arange(arr.size) + shift, arr.size - 1)
    return arr[idx]


def make_features(case, s_now):
    h = case["hour"]
    x = np.column_stack(
        [
            np.sin(2 * np.pi * h / 24.0),
            np.cos(2 * np.pi * h / 24.0),
            case["work"],
            case["p_l"],
            case["p_pv"],
            case["c_b"],
            case["c_s"],
            s_now,
            lookahead(case["p_l"], 1),
            lookahead(case["p_pv"], 1),
            lookahead(case["p_l"], 3),
            lookahead(case["p_pv"], 3),
        ]
    )
    return x


def standardize_fit(x):
    mean = x.mean(axis=0)
    std = x.std(axis=0)
    std = np.where(std < 1e-8, 1.0, std)
    return mean, std


def apply_standard(x, mean, std):
    return (x - mean) / std


def rollout_raw_dd(model, x_mean, x_std, y_mean, y_std, case, s0, start, stop):
    n = stop - start
    p_g = np.zeros(n)
    p_c = np.zeros(n)
    p_d = np.zeros(n)
    s = np.zeros(n)
    s_now = s0
    for i, t in enumerate(range(start, stop)):
        feat = make_features(case, np.zeros(case["p_l"].size))[t]
        feat[7] = s_now
        z = apply_standard(feat[None, :], x_mean, x_std)
        y = model.predict(z)[0] * y_std + y_mean
        p_g[i], p_c[i], p_d[i], s_next = y
        s[i] = s_now
        s_now = float(s_next)
    return p_g, p_c, p_d, s


def rollout_hard(command_fn, case, s0, start, stop):
    n = stop - start
    p_g = np.zeros(n)
    p_c = np.zeros(n)
    p_d = np.zeros(n)
    u = np.zeros(n)
    s = np.zeros(n)
    s_now = s0
    for i, t in enumerate(range(start, stop)):
        u_t = float(command_fn(t, s_now))
        pc, pd, s_next, pg = hard_layer(s_now, u_t, case["p_l"][t], case["p_pv"][t])
        p_c[i], p_d[i], p_g[i], u[i], s[i] = float(pc), float(pd), float(pg), float(pc - pd), s_now
        s_now = float(s_next)
    s_next_path = np.concatenate([s[1:], np.array([s_now])])
    return p_g, p_c, p_d, u, s, s_next_path


def feasibility(p_g, p_c, p_d, s, p_l, p_pv):
    r = np.abs(power_residual(p_g, p_pv, p_d, p_c, p_l))
    soc_v = np.mean((s < 0.20 - 1e-9) | (s > 0.90 + 1e-9)) * 100.0
    return {
        "abs_r": float(np.mean(r)),
        "soc_pct": float(soc_v),
        "pc_neg_pct": float(np.mean(p_c < -1e-12) * 100.0),
        "pd_neg_pct": float(np.mean(p_d < -1e-12) * 100.0),
        "simul_pct": float(np.mean((p_c > 1e-12) & (p_d > 1e-12)) * 100.0),
    }


def mae(a, b):
    return float(np.mean(np.abs(a - b)))


def mse_comp(pg, pc, pd, sn, pg_t, pc_t, pd_t, sn_t):
    err = np.stack([pg - pg_t, pc - pc_t, pd - pd_t, sn - sn_t], axis=1)
    return float(np.mean(err**2))


def plot_figures(case, ref, pe, dd_rep, dd_raw, start, n_test):
    import matplotlib.pyplot as plt

    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    hours = np.arange(24)
    sl = slice(0, 24)
    fig, axes = plt.subplots(2, 1, figsize=(8.2, 5.6), sharex=True)
    axes[0].plot(hours, case["p_l"][start : start + 24], color="#2c5f8a", label="Public-demand signal")
    axes[0].plot(hours, case["p_pv"][start : start + 24], color="#d08a2b", label="PV proxy")
    axes[0].set_ylabel("Power (kW)")
    axes[0].legend(loc="upper right", frameon=False)
    axes[0].set_title("First test day: public-data hybrid case study")
    axes[1].axhline(0.90, color="0.75", ls=":", lw=0.8)
    axes[1].axhline(0.20, color="0.75", ls=":", lw=0.8)
    axes[1].plot(hours, ref["s"][start : start + 24], color="#2aa198", label="DP reference")
    axes[1].plot(hours, dd_rep["s"][sl], color="#d62728", ls="--", label="Data-driven (repaired)")
    axes[1].plot(hours, pe["s"][sl], color="#4b3f91", label="Physics-embedded")
    axes[1].set_ylabel("SOC")
    axes[1].set_xlabel("Test hour")
    axes[1].set_ylim(0.15, 0.95)
    axes[1].legend(loc="upper right", frameon=False)
    fig.tight_layout()
    fig.savefig(ASSETS_DIR / "fig-first-test-day.png", dpi=140)
    plt.close(fig)

    week = min(168, n_test)
    fig, ax = plt.subplots(figsize=(8.4, 3.8))
    r_dd = np.abs(
        power_residual(
            dd_raw["p_g"][:week],
            case["p_pv"][start : start + week],
            dd_raw["p_d"][:week],
            dd_raw["p_c"][:week],
            case["p_l"][start : start + week],
        )
    )
    r_pe = np.abs(
        power_residual(
            pe["p_g"][:week],
            case["p_pv"][start : start + week],
            pe["p_d"][:week],
            pe["p_c"][:week],
            case["p_l"][start : start + week],
        )
    )
    ax.plot(np.arange(week), r_dd, color="#d62728", lw=1.1, label="Raw data-driven")
    ax.plot(np.arange(week), r_pe, color="#4b3f91", lw=1.4, label="Physics-embedded")
    ax.set_xlabel("Test hour")
    ax.set_ylabel("Absolute power residual (kW)")
    ax.set_title("Power-balance residual on the first test week")
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(ASSETS_DIR / "fig-power-residual.png", dpi=140)
    plt.close(fig)

    n_days = n_test / 24.0
    costs = [
        float(np.sum(step_cost(ref["p_g"][start : start + n_test], ref["p_c"][start : start + n_test], ref["p_d"][start : start + n_test], case["c_b"][start : start + n_test], case["c_s"][start : start + n_test])))
        / n_days,
        float(np.sum(step_cost(case["p_l"][start : start + n_test] - case["p_pv"][start : start + n_test], np.zeros(n_test), np.zeros(n_test), case["c_b"][start : start + n_test], case["c_s"][start : start + n_test])))
        / n_days,
        float(np.sum(step_cost(dd_rep["p_g"], dd_rep["p_c"], dd_rep["p_d"], case["c_b"][start : start + n_test], case["c_s"][start : start + n_test])))
        / n_days,
        float(np.sum(step_cost(pe["p_g"], pe["p_c"], pe["p_d"], case["c_b"][start : start + n_test], case["c_s"][start : start + n_test])))
        / n_days,
    ]
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    colors = ["#2aa198", "#8a8a8a", "#d62728", "#4b3f91"]
    labels = ["DP\nreference", "Grid-only", "Data-driven\n+ repair", "Physics-\nembedded"]
    bars = ax.bar(labels, costs, color=colors)
    ax.set_ylabel("Mean daily operating cost")
    ax.set_title("Executable cost on the held-out test horizon")
    ax.set_ylim(0, max(costs) * 1.18)
    for bar, val in zip(bars, costs):
        ax.text(bar.get_x() + bar.get_width() / 2, val + max(costs) * 0.02, f"{val:.3f}", ha="center", va="bottom")
    fig.tight_layout()
    fig.savefig(ASSETS_DIR / "fig-daily-cost.png", dpi=140)
    plt.close(fig)


def main():
    if not CASE_CSV.exists():
        raise SystemExit("run prepare_public_data.py first")
    case = load_case(CASE_CSV)
    n = case["p_l"].size
    n_train, n_val, n_test = split_sizes(n)
    print(f"hours={n} split={n_train}/{n_val}/{n_test}")
    print("solving DP reference...")
    ref = solve_reference(case["p_l"], case["p_pv"], case["c_b"], case["c_s"], S0)

    x_ref = make_features(case, ref["s"])
    y_ref = np.column_stack([ref["p_g"], ref["p_c"], ref["p_d"], ref["s_next"]])
    u_ref = ref["u"]

    sl_tr = slice(0, n_train)
    sl_va = slice(n_train, n_train + n_val)
    sl_te = slice(n_train + n_val, n)
    start = n_train + n_val

    x_mean, x_std = standardize_fit(x_ref[sl_tr])
    y_mean, y_std = standardize_fit(y_ref[sl_tr])
    x_tr = apply_standard(x_ref[sl_tr], x_mean, x_std)
    x_va = apply_standard(x_ref[sl_va], x_mean, x_std)
    y_tr = apply_standard(y_ref[sl_tr], y_mean, y_std)
    y_va = apply_standard(y_ref[sl_va], y_mean, y_std)
    u_tr = (u_ref[sl_tr] / P_MAX).reshape(-1, 1)
    u_va = (u_ref[sl_va] / P_MAX).reshape(-1, 1)

    dd_acc, pe_acc, dd_feas, pe_feas, dd_cost, pe_cost = [], [], [], [], [], []
    last_pe = last_dd_rep = last_dd_raw = None

    for seed in SEEDS:
        print(f"seed {seed}: training data-driven...")
        dd, _ = train_mlp(x_tr, y_tr, x_va, y_va, HIDDEN, 4, seed, LR, BATCH, EPOCHS, PATIENCE)
        print(f"seed {seed}: training physics-embedded...")
        pe_net, _ = train_mlp(x_tr, u_tr, x_va, u_va, HIDDEN, 1, seed + 17, LR, BATCH, EPOCHS, PATIENCE, tanh_output=True)

        pg, pc, pd, s_raw = rollout_raw_dd(dd, x_mean, x_std, y_mean, y_std, case, ref["s"][start], start, n)
        last_dd_raw = {"p_g": pg, "p_c": pc, "p_d": pd, "s": s_raw}

        def dd_cmd(t, s_now, model=dd):
            feat = make_features(case, np.zeros(n))[t]
            feat[7] = s_now
            y = model.predict(apply_standard(feat[None, :], x_mean, x_std))[0] * y_std + y_mean
            return clip_signed_command(y[1], y[2])

        def pe_cmd(t, s_now, model=pe_net):
            feat = make_features(case, np.zeros(n))[t]
            feat[7] = s_now
            z = model.predict(apply_standard(feat[None, :], x_mean, x_std))[0, 0]
            return P_MAX * np.tanh(z)

        pg_r, pc_r, pd_r, u_r, s_r, sn_r = rollout_hard(dd_cmd, case, ref["s"][start], start, n)
        pg_p, pc_p, pd_p, u_p, s_p, sn_p = rollout_hard(pe_cmd, case, ref["s"][start], start, n)
        last_dd_rep = {"p_g": pg_r, "p_c": pc_r, "p_d": pd_r, "u": u_r, "s": s_r, "s_next": sn_r}
        last_pe = {"p_g": pg_p, "p_c": pc_p, "p_d": pd_p, "u": u_p, "s": s_p, "s_next": sn_p}

        tgt_g, tgt_c, tgt_d, tgt_sn = y_ref[sl_te].T
        tgt_u = u_ref[sl_te]
        tgt_s = ref["s"][sl_te]
        dd_acc.append(
            {
                "mse": mse_comp(pg, pc, pd, np.concatenate([s_raw[1:], s_raw[-1:]]), tgt_g, tgt_c, tgt_d, tgt_sn),
                "mae_g": mae(pg, tgt_g),
                "mae_u": mae(pc - pd, tgt_u),
                "mae_s": mae(s_raw, tgt_s),
            }
        )
        pe_acc.append(
            {
                "mse": mse_comp(pg_p, pc_p, pd_p, sn_p, tgt_g, tgt_c, tgt_d, tgt_sn),
                "mae_g": mae(pg_p, tgt_g),
                "mae_u": mae(u_p, tgt_u),
                "mae_s": mae(s_p, tgt_s),
            }
        )
        dd_feas.append(feasibility(pg, pc, pd, s_raw, case["p_l"][sl_te], case["p_pv"][sl_te]))
        pe_feas.append(feasibility(pg_p, pc_p, pd_p, s_p, case["p_l"][sl_te], case["p_pv"][sl_te]))
        dd_cost.append(
            float(np.sum(step_cost(pg_r, pc_r, pd_r, case["c_b"][sl_te], case["c_s"][sl_te])))
        )
        pe_cost.append(
            float(np.sum(step_cost(pg_p, pc_p, pd_p, case["c_b"][sl_te], case["c_s"][sl_te])))
        )

    def mean_std(values):
        a = np.asarray(values, dtype=float)
        return float(a.mean()), float(a.std(ddof=0))

    nb_pc, nb_pd, nb_s, nb_pg = no_battery_program(case["p_l"][sl_te], case["p_pv"][sl_te], S0, n_test)
    ref_cost = float(np.sum(step_cost(ref["p_g"][sl_te], ref["p_c"][sl_te], ref["p_d"][sl_te], case["c_b"][sl_te], case["c_s"][sl_te])))
    nb_cost = float(np.sum(step_cost(nb_pg, nb_pc, nb_pd, case["c_b"][sl_te], case["c_s"][sl_te])))

    metrics = {
        "n": n,
        "split": [n_train, n_val, n_test],
        "dp_cost": ref_cost,
        "no_battery_cost": nb_cost,
        "dd_cost_mean": mean_std(dd_cost)[0],
        "dd_cost_std": mean_std(dd_cost)[1],
        "pe_cost_mean": mean_std(pe_cost)[0],
        "pe_cost_std": mean_std(pe_cost)[1],
        "dd_mse": mean_std([d["mse"] for d in dd_acc]),
        "pe_mse": mean_std([d["mse"] for d in pe_acc]),
        "dd_mae_g": mean_std([d["mae_g"] for d in dd_acc]),
        "pe_mae_g": mean_std([d["mae_g"] for d in pe_acc]),
        "dd_mae_u": mean_std([d["mae_u"] for d in dd_acc]),
        "pe_mae_u": mean_std([d["mae_u"] for d in pe_acc]),
        "dd_mae_s": mean_std([d["mae_s"] for d in dd_acc]),
        "pe_mae_s": mean_std([d["mae_s"] for d in pe_acc]),
        "dd_feas": {k: mean_std([d[k] for d in dd_feas]) for k in dd_feas[0]},
        "pe_feas": {k: mean_std([d[k] for d in pe_feas]) for k in pe_feas[0]},
        "nb_mae_g": mae(nb_pg, ref["p_g"][sl_te]),
        "nb_mae_u": mae(np.zeros(n_test), ref["u"][sl_te]),
        "nb_mae_s": mae(nb_s, ref["s"][sl_te]),
        "nb_mse": mse_comp(nb_pg, nb_pc, nb_pd, nb_s, ref["p_g"][sl_te], ref["p_c"][sl_te], ref["p_d"][sl_te], ref["s"][sl_te]),
    }
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    METRICS_JSON.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(json.dumps(metrics, indent=2))
    plot_figures(case, ref, last_pe, last_dd_rep, last_dd_raw, start, n_test)
    print("wrote figures to", ASSETS_DIR)


if __name__ == "__main__":
    main()
