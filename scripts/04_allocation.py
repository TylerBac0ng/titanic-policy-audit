"""
Resource-allocation analysis (see ../outputs/problem_statement.md).

This deliberately does NOT predict survival. A survival model learns the
1912 allocation policy, structural bias included; reusing it to assign
seats would launder that bias as a recommendation. Instead this compares
three allocation *policies* at identical capacity (341 seats — the number
of passengers who actually survived in this 891-passenger sample), and
asks which people each policy seats:

- ACTUAL:  who actually survived.
- WCF:     "women and children first" — the stated 1912 doctrine, applied
           perfectly and class-blind.
- NEED:    modern SOLAS-style vulnerability triage — class-blind AND
           sex-blind, scoring only assistance need.

The gap between ACTUAL and WCF is the audit finding: the distance between
a stated policy and the realized one. The NEED policy shows what a
contemporary priority rule would produce with the same boats.

Scoring weights are a POLICY CHOICE, not a result discovered in the data.
They are declared below so they can be argued with and re-run.

Age caveat: Age was imputed for 177 passengers using a median by
Pclass+Sex, which can never produce a child. Title == "Master" (a boy)
therefore identifies children the age column alone would miss.
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

CLEAN_PATH = "../data/clean/titanic_clean.csv"
CHART_DIR = "../outputs/charts"
REPORT_PATH = "../outputs/allocation_analysis.md"

import os
os.makedirs(CHART_DIR, exist_ok=True)

# ---- palette (matches 02_eda_visuals.py) ----
INK = "#0b0b0b"
INK_SECONDARY = "#52514e"
INK_MUTED = "#898781"
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

# Policy weights — argue with these, then re-run.
WCF_WEIGHTS = {"female": 2.0, "child": 2.0}
NEED_WEIGHTS = {"child": 3.0, "elderly": 2.0, "alone": 1.0, "large_family": 1.0}


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
    return (WCF_WEIGHTS["female"] * (df["Sex"] == "female")
            + WCF_WEIGHTS["child"] * df["IsChild"])


def need_score(df):
    """Class-blind and sex-blind: scores only need for assistance."""
    return (NEED_WEIGHTS["child"] * df["IsChild"]
            + NEED_WEIGHTS["elderly"] * df["IsElderly"]
            + NEED_WEIGHTS["alone"] * df["IsAlone"]
            + NEED_WEIGHTS["large_family"] * df["LargeFamily"])


def allocate(df, scores, capacity):
    """Seat the top `capacity` passengers by score.

    Ties at the cutoff are broken by PassengerId — arbitrary by design,
    mirroring the fact that within a priority tier real evacuation order
    is effectively first-come.
    """
    order = (pd.DataFrame({"score": scores, "pid": df["PassengerId"]})
             .sort_values(["score", "pid"], ascending=[False, True]))
    mask = pd.Series(False, index=df.index)
    mask.loc[order.head(capacity).index] = True
    return mask


def profile(df, mask):
    seated = df[mask]
    by_class = df[mask].groupby("Pclass", observed=True).size()
    total_by_class = df.groupby("Pclass", observed=True).size()
    return {
        "n": int(mask.sum()),
        "pct_female": (seated["Sex"] == "female").mean(),
        "n_children": int(seated["IsChild"].sum()),
        "mean_age": seated["Age"].mean(),
        "by_class": by_class,
        "class_coverage": (by_class / total_by_class),
    }


def main():
    df = add_features(pd.read_csv(CLEAN_PATH))
    df["Survived"] = df["Survived"].astype(bool)

    capacity = int(df["Survived"].sum())
    policies = {
        "Actual (1912)": df["Survived"].copy(),
        "Women & children first": allocate(df, wcf_score(df), capacity),
        "Need-based (class/sex-blind)": allocate(df, need_score(df), capacity),
    }
    profiles = {name: profile(df, mask) for name, mask in policies.items()}

    actual = policies["Actual (1912)"]
    lines = [
        "# Resource Allocation Analysis\n",
        "Three allocation policies compared at **identical capacity "
        f"({capacity} seats)** — the number who actually survived in this "
        f"{len(df)}-passenger sample. No survival model is used here; see the "
        "script docstring for why.\n",
        "## The capacity question\n",
        f"{((df['Sex'] == 'female') | df['IsChild']).sum()} passengers in this "
        f"sample were women or children, against {capacity} seats. The stated "
        "policy of the day was very nearly affordable with the boats that "
        "launched — the shortfall was in *execution*, not capacity.\n",
        "## Who each policy seats\n",
        "| Policy | Seats | % female | Children | Mean age |",
        "|---|---|---|---|---|",
    ]
    for name, p in profiles.items():
        lines.append(f"| {name} | {p['n']} | {p['pct_female']:.0%} | "
                     f"{p['n_children']} | {p['mean_age']:.1f} |")

    lines.append("\n## Seats by passenger class\n")
    lines.append("Share of each class that receives a seat:\n")
    lines.append("| Policy | 1st | 2nd | 3rd |")
    lines.append("|---|---|---|---|")
    for name, p in profiles.items():
        cov = p["class_coverage"]
        lines.append(f"| {name} | {cov.get(1, 0):.0%} | {cov.get(2, 0):.0%} | "
                     f"{cov.get(3, 0):.0%} |")

    lines.append("\n## How far the realized policy drifted\n")
    for name, mask in policies.items():
        if name == "Actual (1912)":
            continue
        overlap = int((mask & actual).sum())
        changed = capacity - overlap
        lines.append(f"- **{name}**: {overlap} of {capacity} seats "
                     f"({overlap / capacity:.0%}) go to the same people who "
                     f"actually survived. **{changed} seats "
                     f"({changed / capacity:.0%}) change hands.**")

    wcf = policies["Women & children first"]
    missed = df[wcf & ~actual]
    lines.append(
        f"\n{len(missed)} passengers would have been seated under a perfectly "
        "executed 'women and children first' but did not survive — "
        f"{(missed['Pclass'] == 3).sum()} of them "
        f"({(missed['Pclass'] == 3).mean():.0%}) were 3rd class. This is the "
        "core audit finding: the realized policy tracked class, and the stated "
        "policy was applied to upper decks first.\n"
    )

    # ---- resolution check: how much of each policy is decided by tiebreak? ----
    lines.append("\n## Does each rule actually sort people?\n")
    lines.append(
        "A priority rule is only operational if it discriminates *within* the "
        "population competing for the last seats. Where a rule ties, the "
        "allocation falls through to whoever arrives first — which in practice "
        "means proximity and status, the very bias the rule was meant to "
        "remove. Seats decided at a tied score:\n"
    )
    contention = {}
    for name, scores in [("Women & children first", wcf_score(df)),
                          ("Need-based (class/sex-blind)", need_score(df))]:
        ranked = scores.sort_values(ascending=False).reset_index(drop=True)
        cutoff = ranked.iloc[capacity - 1]
        decided = int((scores > cutoff).sum())
        tier = int((scores == cutoff).sum())
        remaining = capacity - decided
        contention[name] = {"decided": decided, "tier": tier,
                             "remaining": remaining, "ratio": tier / remaining}

    lines.append("| Policy | Outright | Contested tier | Seats left | Contention |")
    lines.append("|---|---|---|---|---|")
    for name, c in contention.items():
        lines.append(f"| {name} | {c['decided']} | {c['tier']} | "
                     f"{c['remaining']} | {c['ratio']:.2f}x |")

    wcf_c = contention["Women & children first"]
    need_c = contention["Need-based (class/sex-blind)"]
    lines.append(
        "\n*Contention* is how many people are tied at the cutoff per seat "
        "still available. It, not the raw tiebreak count, says whether the "
        "tiebreak changes the **character** of who sails.\n"
    )
    lines.append(
        f"- **Women & children first** looks poorly determined (most seats sit "
        f"at a tied score) but is contended only {wcf_c['ratio']:.2f}x: "
        "everyone in the tied tier is a woman or child, and nearly all of them "
        f"are seated. The tiebreak picks *which* {wcf_c['remaining']} of "
        f"{wcf_c['tier']} — it cannot violate the policy's intent.\n"
        f"- **Need-based** is contended {need_c['ratio']:.2f}x across a tier of "
        f"{need_c['tier']} heterogeneous passengers, so the tiebreak decides "
        "most of the boat and can pick any composition at all. **Read its "
        "class and sex columns above as largely an artifact of the tiebreak, "
        "not a result.**\n"
    )
    lines.append(
        "That is the finding, not a bug to tune away: a triage rule with too "
        "few levels silently hands the decision back to circumstance — "
        "proximity, status, whoever reached the deck first. Resolution has to "
        "be designed to the population you will actually face (graded "
        "mobility, distance to muster, dependants), and it should be "
        "stress-tested by contention at capacity before anyone relies on it.\n"
    )

    lines.append("## What this translates to today\n")
    lines.append(
        "The transferable deliverable is not a survival score — it is the "
        "**policy-drift audit**: state your priority rule, simulate it at real "
        "capacity, then measure the distance between it and what your "
        "operation actually does. Cruise, aviation, stadium, and hospital-surge "
        "planners all hold a stated priority doctrine; few measure realized "
        "allocation against it. The gap is usually where an unstated variable "
        "(proximity, status, tier) has quietly become the sort order.\n"
    )
    lines.append(
        "Operationally, the class gap here is a **staffing and access** "
        "problem, not a scoring one: it points at crew placement, stairwell "
        "and corridor capacity, and muster assignment for the berths furthest "
        "from the boat deck — the levers that decide who physically reaches a "
        "seat within the evacuation window.\n"
    )

    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    # ---- chart: share of each class seated, by policy ----
    classes = [1, 2, 3]
    x = np.arange(len(classes))
    width = 0.26
    colors = [CRITICAL, BLUE, GOOD]

    fig, ax = plt.subplots(figsize=(7.5, 4.8))
    for i, (name, p) in enumerate(profiles.items()):
        cov = [p["class_coverage"].get(c, 0) for c in classes]
        offset = (i - 1) * width
        # Need-based is hatched: most of its seats fall to the tiebreak, so its
        # composition is not well determined by the rule (see report).
        contested = name.startswith("Need-based")
        bars = ax.bar(x + offset, cov, width,
                      label=name + (" *" if contested else ""),
                      color=colors[i], zorder=3,
                      hatch="//" if contested else None,
                      edgecolor=SURFACE if contested else "none")
        for b, v in zip(bars, cov):
            ax.text(b.get_x() + b.get_width() / 2, v + 0.015, f"{v:.0%}",
                    ha="center", va="bottom", fontsize=8.5, color=INK)

    ax.set_xticks(x)
    ax.set_xticklabels([f"Class {c}" for c in classes])
    ax.set_ylabel("Share of class receiving a seat")
    ax.set_ylim(0, 1.05)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0%}"))
    ax.set_title("Same capacity, three policies: who gets a seat")
    ax.legend(frameon=False, fontsize=9, loc="upper right")
    style_axes(ax)
    fig.text(0.02, -0.02,
             "Insight: at identical capacity, a class-blind policy redistributes "
             "seats toward 3rd class — the boats could have carried a very "
             "different population.\n"
             "* Need-based bars are hatched because most of its seats fall to an "
             "arbitrary tiebreak; treat its composition as indicative, not determined.",
             ha="left", va="top", fontsize=10, color=INK_SECONDARY, wrap=True)
    fig.savefig(f"{CHART_DIR}/13_allocation_by_policy.png", dpi=150, bbox_inches="tight")
    plt.close(fig)

    print(f"Saved allocation report to {REPORT_PATH}")
    print(f"Saved policy comparison chart to {CHART_DIR}/13_allocation_by_policy.png")


if __name__ == "__main__":
    main()
