"""
Robustness check for the allocation policies in 04_allocation.py.

04 showed the need-based rule leaves most seats to an arbitrary tiebreak.
This quantifies what that costs and tests a fix.

Experiment A — tiebreak sensitivity. Hold the rule fixed and re-run the
allocation many times with a random tiebreak instead of PassengerId order.
A rule that genuinely determines the outcome barely moves; a rule that
defers to circumstance swings widely. The spread IS the fragility.

Experiment B — does resolution fix it? Tested by replacing the binary
criteria with continuous ones (age vulnerability as a curve, family burden
scaled by size), still strictly class- and sex-blind.

It does not. The graded rule has 12x more score levels and essentially
identical contention, because the added resolution lands where there was
never a contest. The tied tier is solo adults with no child, elderly or
large-family status, so every graded term evaluates to zero across all of
them. Resolution only helps where the contention actually is — which is
the point worth carrying out of this analysis.

Age caveat: 177 ages are imputed at a Pclass+Sex median, so graded age
still ties at those medians. The graded rule's resolution is therefore a
ceiling estimate, not what you would get from fully observed ages.
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

CLEAN_PATH = "../data/clean/titanic_clean.csv"
CHART_DIR = "../outputs/charts"
REPORT_PATH = "../outputs/sensitivity_analysis.md"

import os
os.makedirs(CHART_DIR, exist_ok=True)

INK = "#0b0b0b"
INK_SECONDARY = "#52514e"
GRID = "#e1e0d9"
SURFACE = "#fcfcfb"
BLUE = "#2a78d6"
ORANGE = "#eb6834"
GOOD = "#0ca30c"
CRITICAL = "#d03b3b"

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
ELDERLY_AGE = 60
N_TRIALS = 1000
SEED = 42


def style_axes(ax):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", color=GRID, linewidth=1, zorder=0)
    ax.set_axisbelow(True)


def add_features(df):
    df["FamilySize"] = df["SibSp"] + df["Parch"] + 1
    df["IsChild"] = (df["Age"] <= CHILD_AGE) | (df["Title"] == "Master")
    df["IsElderly"] = df["Age"] >= ELDERLY_AGE
    df["IsAlone"] = df["FamilySize"] == 1
    df["LargeFamily"] = df["FamilySize"] >= 5
    return df


def wcf_score(df):
    return 2.0 * (df["Sex"] == "female") + 2.0 * df["IsChild"]


def need_coarse(df):
    return (3.0 * df["IsChild"] + 2.0 * df["IsElderly"]
            + 1.0 * df["IsAlone"] + 1.0 * df["LargeFamily"])


def need_graded(df):
    """Same intent as need_coarse, but continuous. Class- and sex-blind."""
    age = df["Age"]
    young = np.clip(CHILD_AGE - age, 0, None) * 0.25       # steeper the younger
    old = np.clip(age - ELDERLY_AGE, 0, None) * 0.08       # rises past 60
    child_floor = 3.0 * df["IsChild"]
    elderly_floor = 2.0 * df["IsElderly"]
    alone = 1.0 * df["IsAlone"]
    burden = np.clip(df["FamilySize"] - 4, 0, None) * 0.4   # scales with size
    return child_floor + elderly_floor + young + old + alone + burden


def contention(scores, capacity):
    ranked = scores.sort_values(ascending=False).reset_index(drop=True)
    cutoff = ranked.iloc[capacity - 1]
    decided = int((scores > cutoff).sum())
    tier = int((scores == cutoff).sum())
    remaining = capacity - decided
    return {"levels": int(scores.nunique()), "decided": decided, "tier": tier,
            "remaining": remaining, "ratio": tier / remaining if remaining else 0.0}


def random_tiebreak_trials(df, scores, capacity, n_trials=N_TRIALS, seed=SEED):
    """Re-allocate n_trials times, breaking ties at random each time."""
    rng = np.random.default_rng(seed)
    s = scores.to_numpy(dtype=float)
    is_third = (df["Pclass"] == 3).to_numpy()
    is_female = (df["Sex"] == "female").to_numpy()
    third_total = is_third.sum()

    third_cov, female_share = [], []
    for _ in range(n_trials):
        key = rng.random(len(s))
        chosen = np.lexsort((key, -s))[:capacity]
        third_cov.append(is_third[chosen].sum() / third_total)
        female_share.append(is_female[chosen].mean())
    return np.array(third_cov), np.array(female_share)


def main():
    df = add_features(pd.read_csv(CLEAN_PATH))
    df["Survived"] = df["Survived"].astype(bool)
    capacity = int(df["Survived"].sum())

    rules = {
        "Women & children first": wcf_score(df),
        "Need-based (coarse)": need_coarse(df),
        "Need-based (graded)": need_graded(df),
    }

    lines = [
        "# Sensitivity Analysis\n",
        f"Every rule re-run **{N_TRIALS:,} times at {capacity} seats**, breaking "
        "ties at random instead of by PassengerId. A rule that really decides "
        "the outcome barely moves between runs. A rule that defers to "
        "circumstance swings — and that swing is the honest error bar on any "
        "claim made about it.\n",
        "## Rule resolution\n",
        "| Rule | Distinct score levels | Contention at cutoff |",
        "|---|---|---|",
    ]
    results = {}
    for name, scores in rules.items():
        c = contention(scores, capacity)
        results[name] = {"contention": c}
        lines.append(f"| {name} | {c['levels']} | {c['ratio']:.2f}x |")

    lines.append("\n## What the tiebreak alone can change\n")
    lines.append("3rd-class coverage across random tiebreaks:\n")
    lines.append("| Rule | Min | Median | Max | Swing |")
    lines.append("|---|---|---|---|---|")
    for name, scores in rules.items():
        third, female = random_tiebreak_trials(df, scores, capacity)
        results[name]["third"] = third
        results[name]["female"] = female
        swing = third.max() - third.min()
        lines.append(f"| {name} | {third.min():.0%} | {np.median(third):.0%} | "
                     f"{third.max():.0%} | **{swing * 100:.1f} pts** |")

    coarse_swing = (results["Need-based (coarse)"]["third"].max()
                     - results["Need-based (coarse)"]["third"].min())
    graded_swing = (results["Need-based (graded)"]["third"].max()
                     - results["Need-based (graded)"]["third"].min())
    wcf_swing = (results["Women & children first"]["third"].max()
                  - results["Women & children first"]["third"].min())

    lines.append(
        f"\n**The coarse need rule's 3rd-class coverage swings "
        f"{coarse_swing * 100:.1f} points on the tiebreak alone** — across those "
        "runs the rule is not choosing, the coin is.\n"
    )
    lines.append(
        f"'Women and children first' swings only {wcf_swing * 100:.1f} points "
        "despite leaving most seats tied, because its tied tier is homogeneous "
        "and almost fully seated. Low contention, not high resolution, is what "
        "makes a coarse rule safe — a rule needs one or the other.\n"
    )

    # ---- why grading failed ----
    graded = rules["Need-based (graded)"]
    cutoff = graded.sort_values(ascending=False).reset_index(drop=True).iloc[capacity - 1]
    tied = df[graded == cutoff]
    lines.append("## Why adding resolution did not help\n")
    lines.append(
        f"The graded rule has {results['Need-based (graded)']['contention']['levels']} "
        f"score levels against the coarse rule's "
        f"{results['Need-based (coarse)']['contention']['levels']}, and it changed "
        f"nothing: contention {results['Need-based (coarse)']['contention']['ratio']:.2f}x "
        f"to {results['Need-based (graded)']['contention']['ratio']:.2f}x, swing "
        f"{coarse_swing * 100:.1f} to {graded_swing * 100:.1f} points. The tied "
        "tier explains it:\n"
    )
    lines.append(f"| Contested tier at the cutoff | Value |")
    lines.append("|---|---|")
    lines.append(f"| Passengers tied | {len(tied)} |")
    lines.append(f"| Children | {int(tied['IsChild'].sum())} |")
    lines.append(f"| Elderly | {int(tied['IsElderly'].sum())} |")
    lines.append(f"| Large families | {int(tied['LargeFamily'].sum())} |")
    lines.append(f"| Travelling alone | {int(tied['IsAlone'].sum())} |")
    lines.append(f"| Mean age | {tied['Age'].mean():.1f} |")
    lines.append(
        f"\nEvery graded term — the age curves, the family-size burden — "
        f"evaluates to **zero for all {len(tied)}** of them. They are healthy "
        "adults travelling alone, and they all score identically because none "
        "of the criteria describe them. The extra levels were added where "
        "there was never a contest.\n"
    )
    lines.append("## Takeaway\n")
    lines.append(
        "**Resolution only helps where the contention is.** Adding precision "
        "to a rule feels like progress and can be measured as progress "
        "(12x the score levels) while changing nothing about the decision "
        "that is actually being made.\n"
    )
    lines.append(
        "The harder conclusion: *this dataset cannot support a class-blind "
        "triage rule for the contested seats.* The population competing for "
        "them is homogeneous on every class-blind variable available — age, "
        "family structure, accompaniment. Separating them needs a variable "
        "nobody recorded: mobility or assistance need, distance from berth to "
        "muster station, language. **The fix is not a better rule or a better "
        "model, it is instrumenting the right field at boarding** — which is a "
        "capital-cheap operational change, and the most transferable "
        "recommendation this project produces.\n"
    )
    lines.append(
        "Corollary for reporting: publish a triage rule with the spread its "
        "tiebreak can produce. A single-run allocation table looks equally "
        "authoritative whether the rule decided it or a coin did.\n"
    )

    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    # ---- chart: spread of 3rd-class coverage under random tiebreaks ----
    fig, ax = plt.subplots(figsize=(7.5, 4.8))
    names = list(rules.keys())
    data = [results[n]["third"] for n in names]
    colors = [BLUE, CRITICAL, GOOD]

    bp = ax.boxplot(data, patch_artist=True, widths=0.5, showfliers=False,
                     medianprops=dict(color=INK, linewidth=2), zorder=3)
    for patch, color in zip(bp["boxes"], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.55)
        patch.set_edgecolor(color)
    for whisker in bp["whiskers"]:
        whisker.set_color(INK_SECONDARY)
    for cap in bp["caps"]:
        cap.set_color(INK_SECONDARY)

    ax.set_xticklabels([n.replace(" (", "\n(") for n in names], fontsize=10)
    ax.set_ylabel("Share of 3rd class receiving a seat")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0%}"))
    ax.set_title(f"How much the tiebreak alone moves the outcome\n"
                  f"({N_TRIALS:,} random tiebreaks per rule)")
    style_axes(ax)
    fig.text(0.02, -0.02,
             f"Insight: both need rules swing ~{coarse_swing * 100:.0f} points on the tiebreak "
             f"alone, versus {wcf_swing * 100:.0f} for women-and-children-first. Grading the "
             f"criteria ({results['Need-based (graded)']['contention']['levels']} score levels "
             f"vs {results['Need-based (coarse)']['contention']['levels']}) did not narrow it: "
             "the contested tier is solo adults, whom none of the criteria describe. A wide box "
             "means the rule is not the thing making the decision.",
             ha="left", va="top", fontsize=10, color=INK_SECONDARY, wrap=True)
    fig.savefig(f"{CHART_DIR}/14_tiebreak_sensitivity.png", dpi=150, bbox_inches="tight")
    plt.close(fig)

    print(f"Saved sensitivity report to {REPORT_PATH}")
    print(f"Saved sensitivity chart to {CHART_DIR}/14_tiebreak_sensitivity.png")


if __name__ == "__main__":
    main()
