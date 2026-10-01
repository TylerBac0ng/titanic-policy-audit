"""
Revealed-policy estimation: recover the priority rule that was actually run.

03_model.py asked "who survived?" and was deliberately not used to assign
seats, because a model fitted to historical outcomes reproduces the
historical decision rule. This script inverts the purpose rather than the
method: the same fit, read as a *measuring instrument*. Its coefficients
are an estimate of the implicit priority function the evacuation actually
applied, and the finding is the gap between that and the stated doctrine.

Two nested models:
  STATED  — the doctrine of the day: sex and child status only.
  REVEALED — adds the access variables the doctrine never mentions:
             class, fare, and whether you were travelling alone.

The improvement from STATED to REVEALED is the part of the realized
policy the written policy does not account for: the drift.

Estimation, not prediction, so: all 891 rows (no holdout), no
regularisation (it would shrink the very coefficients being measured),
and bootstrap confidence intervals.

What this CANNOT support: intent, or a causal claim. Deck is near-perfectly
confounded with class in this data (decks A/B/C are 100% first class), so
"distance from berth to boat deck" is not separable from "class" here. The
honest reading is class-correlated access, never a claim about who decided
what.
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression

CLEAN_PATH = "../data/clean/titanic_clean.csv"
CHART_DIR = "../outputs/charts"
REPORT_PATH = "../outputs/revealed_policy.md"

import os
os.makedirs(CHART_DIR, exist_ok=True)

INK = "#0b0b0b"
INK_SECONDARY = "#52514e"
GRID = "#e1e0d9"
SURFACE = "#fcfcfb"
BLUE = "#2a78d6"
ORANGE = "#eb6834"
RED = "#d03b3b"
MUTED = "#898781"

plt.rcParams.update({
    "figure.facecolor": SURFACE,
    "axes.facecolor": SURFACE,
    "savefig.facecolor": SURFACE,
    "text.color": INK,
    "axes.edgecolor": "#c3c2b7",
    "axes.labelcolor": INK_SECONDARY,
    "xtick.color": INK_SECONDARY,
    "ytick.color": INK_SECONDARY,
    "font.family": "sans-serif",
    "font.size": 11,
    "axes.titlesize": 14,
    "axes.titleweight": "bold",
    "axes.titlecolor": INK,
})

CHILD_AGE = 12
N_BOOT = 1000
SEED = 42

# Which variables the stated doctrine actually names.
STATED_VARS = ["Female", "Child"]
ACCESS_VARS = ["1st class", "2nd class", "Fare (log, sd)"]
OTHER_VARS = ["Travelling alone"]


def build(df):
    df["FamilySize"] = df["SibSp"] + df["Parch"] + 1
    X = pd.DataFrame({
        "Female": (df["Sex"] == "female").astype(float),
        "Child": ((df["Age"] <= CHILD_AGE) | (df["Title"] == "Master")).astype(float),
        "1st class": (df["Pclass"] == 1).astype(float),
        "2nd class": (df["Pclass"] == 2).astype(float),
        "Fare (log, sd)": np.log1p(df["Fare"]),
        "Travelling alone": (df["FamilySize"] == 1).astype(float),
    })
    X["Fare (log, sd)"] = ((X["Fare (log, sd)"] - X["Fare (log, sd)"].mean())
                            / X["Fare (log, sd)"].std())
    return X, df["Survived"].astype(int)


def fit(X, y):
    """Unregularised logistic fit — coefficients are the estimate here."""
    m = LogisticRegression(penalty=None, max_iter=5000)
    m.fit(X, y)
    return m


def log_likelihood(y, p):
    p = np.clip(p, 1e-12, 1 - 1e-12)
    return float(np.sum(y * np.log(p) + (1 - y) * np.log(1 - p)))


def mcfadden(X, y):
    m = fit(X, y)
    ll_model = log_likelihood(y, m.predict_proba(X)[:, 1])
    base = np.full(len(y), y.mean())
    ll_null = log_likelihood(y, base)
    return 1 - ll_model / ll_null, ll_model


def bootstrap_ci(X, y, n_boot=N_BOOT, seed=SEED):
    rng = np.random.default_rng(seed)
    n = len(X)
    coefs = []
    Xv, yv = X.to_numpy(), y.to_numpy()
    for _ in range(n_boot):
        idx = rng.integers(0, n, n)
        if yv[idx].std() == 0:
            continue
        m = LogisticRegression(penalty=None, max_iter=5000)
        m.fit(Xv[idx], yv[idx])
        coefs.append(m.coef_[0])
    arr = np.array(coefs)
    return (np.percentile(arr, 2.5, axis=0), np.percentile(arr, 97.5, axis=0))


def main():
    df = pd.read_csv(CLEAN_PATH)
    X, y = build(df)

    stated_cols = STATED_VARS
    full_cols = list(X.columns)

    r2_stated, _ = mcfadden(X[stated_cols], y)
    r2_full, _ = mcfadden(X[full_cols], y)
    drift_share = (r2_full - r2_stated) / r2_full

    model = fit(X[full_cols], y)
    coefs = pd.Series(model.coef_[0], index=full_cols)
    lo, hi = bootstrap_ci(X[full_cols], y)
    ci = pd.DataFrame({"lo": lo, "hi": hi}, index=full_cols)

    lines = [
        "# The Revealed Policy\n",
        "The evacuation ran on some priority rule. Nobody wrote it down, but "
        "the outcomes encode it. Fitting an unregularised logistic model to "
        "all 891 passengers — as a measuring instrument, not a predictor — "
        "estimates that implicit rule. Coefficients are reported as **odds "
        "multipliers**: how much a factor multiplied the odds of getting off "
        "the ship, holding the others fixed.\n",
        "## The rule that was actually run\n",
        "| Factor | Named by the stated doctrine? | Odds multiplier | 95% CI |",
        "|---|---|---|---|",
    ]
    for name in full_cols:
        named = "**Yes**" if name in STATED_VARS else "No"
        lines.append(f"| {name} | {named} | {np.exp(coefs[name]):.2f}× | "
                     f"{np.exp(ci.loc[name, 'lo']):.2f}–{np.exp(ci.loc[name, 'hi']):.2f} |")

    first = np.exp(coefs["1st class"])
    child = np.exp(coefs["Child"])
    female = np.exp(coefs["Female"])
    lines.append(
        f"\n'Women and children first' names two factors. Being female "
        f"multiplied the odds by {female:.1f}× and being a child by "
        f"{child:.1f}× — the doctrine was real and it was strong.\n"
    )
    lines.append(
        f"But **first class multiplied the odds by {first:.1f}×**, and the "
        "stated doctrine does not mention class at all. That coefficient is "
        "the policy nobody wrote down.\n"
    )

    lines.append("## How much of the real policy the written one explains\n")
    lines.append("| Model | Factors | McFadden pseudo-R² |")
    lines.append("|---|---|---|")
    lines.append(f"| Stated doctrine | sex, child | {r2_stated:.3f} |")
    lines.append(f"| Revealed policy | + class, fare, alone | {r2_full:.3f} |")
    lines.append(
        f"\n**{drift_share:.0%} of the explained priority rule comes from "
        "factors the stated policy never names.** That fraction is the drift, "
        "measured rather than asserted.\n"
    )

    lines.append("## What this cannot tell you\n")
    lines.append(
        "Decks A, B and C in this dataset are 100% first class; only 204 of "
        "891 passengers have any cabin recorded at all. **Distance from berth "
        "to the boat deck is therefore not separable from class here** — the "
        "two are the same variable in 1912. So the honest statement is "
        "class-correlated *access*, not a claim that anyone was turned away, "
        "and certainly not intent.\n"
    )
    lines.append(
        "That confound is itself the bridge to the modern case. On a modern "
        "ship, cabins at different price points sit on the same deck and "
        "share the same stairwells, so deck distance and fare class finally "
        "*are* separable. The audit that could not be run in 1912 is "
        "identified today.\n"
    )

    lines.append("## Reading this on a modern ship\n")
    lines.append(
        "Capacity is no longer the constraint: SOLAS requires survival craft "
        "for everyone aboard. The scarce resource has moved from **seats to "
        "time** — the evacuation window, and who can physically reach an "
        "assigned muster station inside it. The allocation question is the "
        "same shape, and so is the failure mode.\n"
    )
    lines.append(
        "The fields this analysis said were missing in 1912 are already "
        "collected at booking today:\n"
    )
    lines.append("| 1912 gap | Modern equivalent already on file |")
    lines.append("|---|---|")
    lines.append("| Distance from berth to boat deck | Cabin number → deck, stairwell, muster station |")
    lines.append("| Mobility or assistance need | Accessibility requests at booking |")
    lines.append("| Who is travelling with whom | Booking party / linked reservations |")
    lines.append("| Whether instructions are understood | Language preference on the reservation |")
    lines.append(
        "\n**And the audit does not need a disaster to run.** Muster drill "
        "records — who reached which station, and how long it took, by cabin, "
        "by deck, by mobility flag — are a live record of the realized "
        "policy. Fit the same instrument to drill timings and it returns the "
        "priority rule the ship actually operates, which can then be compared "
        "against the written muster plan.\n"
    )
    lines.append(
        "The 1912 question, restated for a modern operator: *does your "
        "realized evacuation order track assistance need and distance — or "
        "does it still track deck and fare, with a written policy that says "
        "otherwise?* That is measurable this quarter, from data already held, "
        "and the contention check in 05_sensitivity.py says whether the "
        "muster plan is resolving the decision at all or leaving it to "
        "whoever is nearest the stairwell.\n"
    )

    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    # ---- chart: the revealed priority function ----
    order = ["Female", "Child", "1st class", "2nd class", "Fare (log, sd)",
             "Travelling alone"]
    fig, ax = plt.subplots(figsize=(8.5, 5))
    for i, name in enumerate(order):
        if name in STATED_VARS:
            color, label = BLUE, "Named by the stated doctrine"
        elif name in ACCESS_VARS:
            color, label = RED, "Never mentioned by it"
        else:
            color, label = MUTED, "Other"
        yv = len(order) - 1 - i
        ax.plot([np.exp(ci.loc[name, "lo"]), np.exp(ci.loc[name, "hi"])],
                [yv, yv], color=color, linewidth=2.5, solid_capstyle="round",
                zorder=3)
        ax.scatter([np.exp(coefs[name])], [yv], color=color, s=110, zorder=4,
                   edgecolor=SURFACE, linewidth=1.5)

    ax.axvline(1.0, color=INK_SECONDARY, linestyle="--", linewidth=1, zorder=2)
    ax.set_xscale("log")
    ax.set_yticks(range(len(order)))
    ax.set_yticklabels(order[::-1], fontsize=11)
    ax.set_xlabel("Odds multiplier on getting off the ship (log scale)")
    ax.set_title("The priority rule that was actually run")
    ax.set_xticks([0.5, 1, 2, 5, 10])
    ax.set_xticklabels(["0.5×", "1×", "2×", "5×", "10×"])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="x", color=GRID, linewidth=1, zorder=0)
    ax.set_axisbelow(True)

    handles = [plt.Line2D([], [], color=BLUE, linewidth=3,
                           label="Named by the stated doctrine"),
               plt.Line2D([], [], color=RED, linewidth=3,
                           label="Never mentioned by it"),
               plt.Line2D([], [], color=MUTED, linewidth=3, label="Other")]
    ax.legend(handles=handles, frameon=False, fontsize=9.5, loc="lower right")

    fig.text(0.02, -0.02,
             f"Insight: the doctrine's own factors are strong, but first class still "
             f"multiplied the odds {first:.1f}x — and the written policy never mentions "
             f"class. {drift_share:.0%} of the explained rule comes from factors it does not "
             "name. Bars are bootstrap 95% intervals.",
             ha="left", va="top", fontsize=10, color=INK_SECONDARY, wrap=True)
    fig.savefig(f"{CHART_DIR}/15_revealed_policy.png", dpi=150, bbox_inches="tight")
    plt.close(fig)

    print(f"Saved revealed-policy report to {REPORT_PATH}")
    print(f"Saved coefficient chart to {CHART_DIR}/15_revealed_policy.png")
    print(f"\nDrift share: {drift_share:.1%} | 1st class odds: {first:.2f}x")


if __name__ == "__main__":
    main()
