"""
Exploratory analysis of what's associated with Titanic survival.

Produces one PNG per question in ../outputs/charts/ and a text summary of the
numbers behind each chart in ../outputs/eda_findings.md.

Color usage follows a fixed palette:
- Status (good/critical) for the Survived/Died outcome itself.
- A fixed categorical pair for Sex wherever it's broken out (female=blue, male=orange).
- A single sequential hue (blue) for plain magnitude-by-category bars.
- Diverging blue<->red for the correlation heatmap (a polarity measure, -1..1).
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd

CLEAN_PATH = "../data/clean/titanic_clean.csv"
CHART_DIR = "../outputs/charts"
FINDINGS_PATH = "../outputs/eda_findings.md"

import os
os.makedirs(CHART_DIR, exist_ok=True)

# ---- palette ----
INK = "#0b0b0b"
INK_SECONDARY = "#52514e"
INK_MUTED = "#898781"
GRID = "#e1e0d9"
SURFACE = "#fcfcfb"
BLUE = "#2a78d6"
ORANGE = "#eb6834"
RED = "#e34948"
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


def style_axes(ax, hide_y=False):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(not hide_y)
    if hide_y:
        ax.set_yticks([])
    ax.grid(axis="y", color=GRID, linewidth=1, zorder=0)
    ax.set_axisbelow(True)


def add_insight(fig, text):
    fig.text(0.02, -0.02, f"Insight: {text}", ha="left", va="top",
              fontsize=10, color=INK_SECONDARY, wrap=True)


def savefig(fig, name):
    fig.savefig(f"{CHART_DIR}/{name}.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def main():
    df = pd.read_csv(CLEAN_PATH)
    df["Survived"] = df["Survived"].astype(bool)
    findings = []

    overall_rate = df["Survived"].mean()
    findings.append(f"## Overall\nOverall survival rate: {overall_rate:.1%} "
                     f"({df['Survived'].sum()} of {len(df)} passengers).\n")

    # 1. Overall outcome ---------------------------------------------------
    counts = df["Survived"].value_counts().reindex([True, False])
    fig, ax = plt.subplots(figsize=(5, 4))
    bars = ax.bar(["Survived", "Did not survive"], counts.values,
                   color=[GOOD, CRITICAL], width=0.6, zorder=3)
    for b, v in zip(bars, counts.values):
        ax.text(b.get_x() + b.get_width() / 2, v + 10, f"{v}\n({v/len(df):.0%})",
                ha="center", va="bottom", color=INK, fontsize=11)
    ax.set_title("Most passengers did not survive")
    ax.set_ylabel("Number of passengers")
    ax.set_ylim(0, counts.max() * 1.25)
    style_axes(ax)
    add_insight(fig, f"{overall_rate:.1%} of the {len(df)} passengers on board survived.")
    savefig(fig, "01_overall_survival")

    # 2. Survival rate by Sex ----------------------------------------------
    by_sex = df.groupby("Sex")["Survived"].mean().reindex(["female", "male"])
    fig, ax = plt.subplots(figsize=(5, 4))
    bars = ax.bar(by_sex.index.str.capitalize(), by_sex.values,
                   color=[BLUE, ORANGE], width=0.5, zorder=3)
    for b, v in zip(bars, by_sex.values):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.02, f"{v:.0%}",
                ha="center", va="bottom", color=INK, fontsize=12, fontweight="bold")
    ax.set_title("Women survived at far higher rates than men")
    ax.set_ylabel("Survival rate")
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(1.0))
    ax.set_ylim(0, 1)
    style_axes(ax)
    add_insight(fig, f"Female survival rate ({by_sex['female']:.0%}) was "
                      f"{by_sex['female']/by_sex['male']:.1f}x the male rate ({by_sex['male']:.0%}) "
                      "— consistent with a 'women first' evacuation priority.")
    savefig(fig, "02_survival_by_sex")
    findings.append(f"## Sex\nFemale survival rate: {by_sex['female']:.1%}. "
                     f"Male survival rate: {by_sex['male']:.1%}.\n")

    # 3. Survival rate by Pclass --------------------------------------------
    by_class = df.groupby("Pclass")["Survived"].mean().sort_index()
    fig, ax = plt.subplots(figsize=(5, 4))
    bars = ax.bar([f"Class {c}" for c in by_class.index], by_class.values,
                   color=BLUE, width=0.5, zorder=3)
    for b, v in zip(bars, by_class.values):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.02, f"{v:.0%}",
                ha="center", va="bottom", color=INK, fontsize=12, fontweight="bold")
    ax.set_title("Survival dropped sharply by passenger class")
    ax.set_ylabel("Survival rate")
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(1.0))
    ax.set_ylim(0, 1)
    style_axes(ax)
    add_insight(fig, f"1st class survival ({by_class[1]:.0%}) was more than double "
                      f"3rd class ({by_class[3]:.0%}), consistent with cabin location "
                      "and boat-deck access favoring upper classes.")
    savefig(fig, "03_survival_by_class")
    findings.append("## Pclass\n" + by_class.apply(lambda v: f"{v:.1%}").to_string() + "\n")

    # 4. Survival rate by Sex within Pclass ---------------------------------
    grp = df.groupby(["Pclass", "Sex"])["Survived"].mean().unstack()
    grp = grp[["female", "male"]].sort_index()
    x = np.arange(len(grp))
    width = 0.35
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    ax.bar(x - width / 2, grp["female"], width, label="Female", color=BLUE, zorder=3)
    ax.bar(x + width / 2, grp["male"], width, label="Male", color=ORANGE, zorder=3)
    for i, cls in enumerate(grp.index):
        ax.text(i - width / 2, grp.loc[cls, "female"] + 0.02, f"{grp.loc[cls, 'female']:.0%}",
                ha="center", fontsize=9, color=INK)
        ax.text(i + width / 2, grp.loc[cls, "male"] + 0.02, f"{grp.loc[cls, 'male']:.0%}",
                ha="center", fontsize=9, color=INK)
    ax.set_xticks(x)
    ax.set_xticklabels([f"Class {c}" for c in grp.index])
    ax.set_ylabel("Survival rate")
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(1.0))
    ax.set_ylim(0, 1.05)
    ax.set_title("Sex matters more than class, but both stack")
    ax.legend(frameon=False, loc="upper right")
    style_axes(ax)
    add_insight(fig, f"3rd-class women ({grp.loc[3,'female']:.0%}) still outsurvived "
                      f"1st-class men ({grp.loc[1,'male']:.0%}) — sex was the stronger factor.")
    savefig(fig, "04_survival_by_sex_and_class")
    findings.append("## Pclass x Sex\n" + grp.applymap(lambda v: f"{v:.1%}").to_string() + "\n")

    # 5. Age distribution by outcome -----------------------------------------
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    bins = np.arange(0, 85, 5)
    ax.hist(df.loc[~df["Survived"], "Age"], bins=bins, color=CRITICAL, alpha=0.55,
             label="Did not survive", zorder=3)
    ax.hist(df.loc[df["Survived"], "Age"], bins=bins, color=GOOD, alpha=0.55,
             label="Survived", zorder=3)
    ax.set_title("Young children survived at high rates; other ages look similar")
    ax.set_xlabel("Age (years) — includes imputed values for the 177 passengers missing Age")
    ax.set_ylabel("Number of passengers")
    ax.legend(frameon=False)
    style_axes(ax)
    child_rate = df.loc[df["Age"] <= 10, "Survived"].mean()
    add_insight(fig, f"Passengers age 10 or under survived at {child_rate:.0%}, "
                      "noticeably above the {:.0%} overall rate.".format(overall_rate))
    savefig(fig, "05_age_distribution_by_outcome")
    findings.append(f"## Age\nSurvival rate for age <= 10: {child_rate:.1%} vs overall {overall_rate:.1%}.\n"
                     f"Age was imputed for {df['Age_was_missing'].sum()} passengers (median by Pclass+Sex); "
                     "interpret age-based patterns with that in mind.\n")

    # 6. Fare by outcome (log scale, capped view noted) ----------------------
    fig, ax = plt.subplots(figsize=(5, 4.5))
    data = [df.loc[~df["Survived"], "Fare"].clip(lower=1),
            df.loc[df["Survived"], "Fare"].clip(lower=1)]
    bp = ax.boxplot(data, labels=["Did not survive", "Survived"], patch_artist=True,
                     showfliers=True, widths=0.5, zorder=3,
                     medianprops=dict(color=INK, linewidth=2))
    for patch, color in zip(bp["boxes"], [CRITICAL, GOOD]):
        patch.set_facecolor(color)
        patch.set_alpha(0.55)
        patch.set_edgecolor(color)
    ax.set_yscale("log")
    ax.set_title("Survivors paid noticeably higher fares")
    ax.set_ylabel("Fare (USD, log scale; $0 fares clipped to $1 to plot on log axis)")
    style_axes(ax)
    add_insight(fig, f"Median fare for survivors (${df.loc[df['Survived'],'Fare'].median():.2f}) was "
                      f"roughly {df.loc[df['Survived'],'Fare'].median()/max(df.loc[~df['Survived'],'Fare'].median(),1):.1f}x "
                      f"the median for non-survivors (${df.loc[~df['Survived'],'Fare'].median():.2f}) — "
                      "likely a proxy for class/cabin location rather than a direct cause.")
    savefig(fig, "06_fare_by_outcome")
    findings.append(f"## Fare\nMedian fare, survived: ${df.loc[df['Survived'],'Fare'].median():.2f}. "
                     f"Median fare, did not survive: ${df.loc[~df['Survived'],'Fare'].median():.2f}. "
                     f"{(df['Fare']==0).sum()} passengers paid $0 (kept as-is, noted as an anomaly).\n")

    # 7. Family size vs survival ---------------------------------------------
    family_size = df["SibSp"] + df["Parch"] + 1
    bucket = pd.cut(family_size, bins=[0, 1, 4, 11], labels=["Alone (1)", "Small (2-4)", "Large (5+)"])
    by_family = df.groupby(bucket, observed=True)["Survived"].mean()
    fig, ax = plt.subplots(figsize=(5, 4))
    bars = ax.bar(by_family.index.astype(str), by_family.values, color=BLUE, width=0.5, zorder=3)
    for b, v in zip(bars, by_family.values):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.02, f"{v:.0%}",
                ha="center", va="bottom", color=INK, fontsize=12, fontweight="bold")
    ax.set_title("Traveling with a small family beat traveling alone or in a large one")
    ax.set_xlabel("Family size aboard (self + SibSp + Parch)")
    ax.set_ylabel("Survival rate")
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(1.0))
    ax.set_ylim(0, 1)
    style_axes(ax)
    add_insight(fig, f"Small families survived at {by_family['Small (2-4)']:.0%}, above both "
                      f"solo travelers ({by_family['Alone (1)']:.0%}) and large families "
                      f"({by_family['Large (5+)']:.0%}), who may have struggled to stay together.")
    savefig(fig, "07_survival_by_family_size")
    findings.append("## Family size\n" + by_family.apply(lambda v: f"{v:.1%}").to_string() + "\n")

    # 8. Title vs survival -----------------------------------------------------
    order = df.groupby("Title")["Survived"].mean().sort_values(ascending=False)
    counts_by_title = df["Title"].value_counts()
    fig, ax = plt.subplots(figsize=(6, 4.5))
    bars = ax.bar(order.index.astype(str), order.values, color=BLUE, width=0.55, zorder=3)
    for b, title in zip(bars, order.index):
        v = order[title]
        ax.text(b.get_x() + b.get_width() / 2, v + 0.02,
                f"{v:.0%}\n(n={counts_by_title[title]})",
                ha="center", va="bottom", color=INK, fontsize=9)
    ax.set_title("Name titles echo the sex and class patterns")
    ax.set_ylabel("Survival rate")
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(1.0))
    ax.set_ylim(0, 1.15)
    style_axes(ax)
    add_insight(fig, "Titles are a proxy for sex/age/status extracted from Name — "
                      "'Mr' (mostly adult men) has the lowest survival, matching the sex breakdown.")
    savefig(fig, "08_survival_by_title")
    findings.append("## Title\n" + order.apply(lambda v: f"{v:.1%}").to_string() + "\n")

    # 9. Deck vs survival (with Unknown, and a caveat) --------------------------
    deck_order = ["A", "B", "C", "D", "E", "F", "G", "Unknown"]
    by_deck = df.groupby("Deck", observed=True)["Survived"].mean().reindex(deck_order).dropna()
    counts_by_deck = df["Deck"].value_counts()
    fig, ax = plt.subplots(figsize=(7, 4.5))
    colors = [INK_MUTED if d == "Unknown" else BLUE for d in by_deck.index]
    bars = ax.bar(by_deck.index.astype(str), by_deck.values, color=colors, width=0.6, zorder=3)
    for b, deck in zip(bars, by_deck.index):
        v = by_deck[deck]
        ax.text(b.get_x() + b.get_width() / 2, v + 0.02,
                f"{v:.0%}\n(n={counts_by_deck[deck]})",
                ha="center", va="bottom", color=INK, fontsize=9)
    ax.set_title("Known cabin decks survived better — but this mostly reflects class")
    ax.set_ylabel("Survival rate")
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(1.0))
    ax.set_ylim(0, 1.15)
    style_axes(ax)
    add_insight(fig, "687 of 891 passengers (77%) have no recorded cabin ('Unknown', gray) — "
                      "mostly 3rd class. Deck is really a proxy for class/fare, not an independent factor.")
    savefig(fig, "09_survival_by_deck")
    findings.append("## Deck\n" + by_deck.apply(lambda v: f"{v:.1%}").to_string() +
                     "\nNote: 'Unknown' deck is 77% of passengers and correlates with lower Pclass.\n")

    # 10. Correlation heatmap ----------------------------------------------------
    corr_df = df.copy()
    corr_df["FamilySize"] = family_size
    corr_df["Pclass_num"] = corr_df["Pclass"].astype(int)
    corr_df["Survived_num"] = corr_df["Survived"].astype(int)
    cols = ["Survived_num", "Pclass_num", "Age", "SibSp", "Parch", "Fare", "FamilySize"]
    labels = ["Survived", "Pclass", "Age", "SibSp", "Parch", "Fare", "FamilySize"]
    corr = corr_df[cols].corr()

    fig, ax = plt.subplots(figsize=(6, 5.5))
    cmap = matplotlib.colors.LinearSegmentedColormap.from_list("div", [RED, "#f0efec", BLUE])
    im = ax.imshow(corr.values, cmap=cmap, vmin=-1, vmax=1)
    ax.set_xticks(range(len(labels)))
    ax.set_yticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=45, ha="right")
    ax.set_yticklabels(labels)
    for i in range(len(labels)):
        for j in range(len(labels)):
            val = corr.values[i, j]
            text_color = "white" if abs(val) > 0.6 else INK
            ax.text(j, i, f"{val:.2f}", ha="center", va="center", color=text_color, fontsize=9)
    ax.set_title("Correlation with survival: class and fare matter most\n(numerically)")
    cbar = fig.colorbar(im, ax=ax, shrink=0.8)
    cbar.set_label("Correlation coefficient")
    for spine in ax.spines.values():
        spine.set_visible(False)
    add_insight(fig, f"Pclass has the strongest linear correlation with survival "
                      f"({corr.loc['Survived_num','Pclass_num']:.2f}, negative because a higher class "
                      f"number is a lower-status cabin), followed by Fare ({corr.loc['Survived_num','Fare']:.2f}). "
                      "Sex isn't in this numeric matrix but its effect (from chart 2) was larger than either.")
    savefig(fig, "10_correlation_heatmap")
    findings.append("## Correlation with Survived (numeric features only; Sex is categorical and excluded here)\n" +
                     corr["Survived_num"].drop("Survived_num").sort_values().apply(lambda v: f"{v:.2f}").to_string() + "\n")

    with open(FINDINGS_PATH, "w") as f:
        f.write("# EDA Findings\n\n" + "\n".join(findings))

    print(f"Saved {10} charts to {CHART_DIR}/")
    print(f"Saved findings summary to {FINDINGS_PATH}")


if __name__ == "__main__":
    main()
