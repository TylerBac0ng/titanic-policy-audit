"""
Bring in the sources the Kaggle sample cannot contain.

The 891-row training split is passengers only, and it carries no record of
the physical constraint — how many seats existed, when they left, or how
full they were. Three external datasets close that gap (provenance and
caveats in ../data/external/SOURCES.md):

  bot_inquiry_1912.csv  — the British Inquiry's population figures, all
                          2,206 aboard including the 898 crew the Kaggle
                          data omits entirely.
  lifeboats.csv         — per-boat capacity, occupancy and launch time.
  crew_departments.csv  — crew survival by department.

Together they do three things the modelling alone could not: check whether
the sample is representative, replace an inferred claim about capacity with
a measured one, and supply a mechanism for the class coefficient estimated
in 06_revealed_policy.py.
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

CLEAN_PATH = "../data/clean/titanic_clean.csv"
EXTERNAL_DIR = "../data/external"
CHART_DIR = "../outputs/charts"
REPORT_PATH = "../outputs/external_validation.md"

import os
os.makedirs(CHART_DIR, exist_ok=True)

INK = "#0b0b0b"
INK_SECONDARY = "#52514e"
GRID = "#e1e0d9"
SURFACE = "#fcfcfb"
BLUE = "#2a78d6"
ORANGE = "#eb6834"
RED = "#d03b3b"
GOOD = "#0ca30c"
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

SANK_AT = 160  # minutes after impact


def style_axes(ax, axis="y"):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis=axis, color=GRID, linewidth=1, zorder=0)
    ax.set_axisbelow(True)


def main():
    sample = pd.read_csv(CLEAN_PATH)
    bot = pd.read_csv(f"{EXTERNAL_DIR}/bot_inquiry_1912.csv")
    boats = pd.read_csv(f"{EXTERNAL_DIR}/lifeboats.csv")
    crew = pd.read_csv(f"{EXTERNAL_DIR}/crew_departments.csv")

    lines = ["# External Validation\n",
             "What the Kaggle sample cannot see, and what changes when you "
             "bring in the inquiry record and the boats themselves.\n"]

    # ---- 1. coverage ----
    aboard = int(bot["carried"].sum())
    saved = int(bot["saved"].sum())
    crew_n = int(bot.loc[bot["group"] == "Crew", "carried"].sum())
    lines.append("## The sample is 40% of the problem\n")
    lines.append("| | People |")
    lines.append("|---|---|")
    lines.append(f"| Aboard (British Inquiry) | {aboard:,} |")
    lines.append(f"| Saved | {saved:,} ({saved / aboard:.0%}) |")
    lines.append(f"| Crew aboard — absent from the Kaggle data | {crew_n:,} ({crew_n / aboard:.0%}) |")
    lines.append(f"| Passengers in the Kaggle training split | {len(sample):,} |")
    lines.append(
        f"\nThe modelling scripts see {len(sample):,} of {aboard:,} people. "
        f"Every one of the {crew_n:,} crew is missing, and crew were both the "
        "largest single group aboard and the group doing the evacuating. Any "
        "claim about 'who was prioritised' from the sample alone is a claim "
        "about passengers only.\n"
    )

    # ---- 2. the children comparison ----
    kids = bot[bot["category"] == "Children"].copy()
    kids["rate"] = kids["saved"] / kids["carried"]
    lines.append("## The finding that needs no model\n")
    lines.append("| Class | Children aboard | Saved | Survived |")
    lines.append("|---|---|---|---|")
    for _, r in kids.iterrows():
        lines.append(f"| {r['group']} | {r['carried']} | {r['saved']} | "
                     f"**{r['saved'] / r['carried']:.0%}** |")
    third_kids = kids[kids["group"] == "Third class"].iloc[0]
    lost_kids = int(third_kids["carried"] - third_kids["saved"])
    lines.append(
        f"\n**Every second-class child survived. "
        f"{lost_kids} of {int(third_kids['carried'])} third-class children "
        "did not.**\n"
    )
    lines.append(
        "This is the whole argument in one line, and it needs no statistics. "
        "'Women and children first' was not a policy that failed for want of "
        "capacity — in second class it was executed perfectly. The same "
        "doctrine, on the same night, on the same ship, produced a 100% "
        "survival rate one deck up and 30% below. That gap is the revealed "
        "policy, visible without a single coefficient.\n"
    )

    # ---- 3. the utilisation gap ----
    total_capacity = int(boats["capacity"].sum())
    total_aboard_boats = int(boats["aboard"].sum())
    empty = total_capacity - total_aboard_boats
    lines.append("## Capacity was not the binding constraint — measured, not inferred\n")
    lines.append("| | Seats |")
    lines.append("|---|---|")
    lines.append(f"| Rated lifeboat capacity | {total_capacity:,} |")
    lines.append(f"| People actually carried away in them | {total_aboard_boats:,} |")
    lines.append(f"| **Seats that went to sea empty** | **{empty:,}** |")
    lines.append(
        f"\nThe boats were filled to {total_aboard_boats / total_capacity:.0%} "
        f"of their rating. **{empty} seats left the ship unused** while "
        f"roughly 1,500 people remained on board. Filling the boats that were "
        "already in the water — no extra davits, no design change, no capital "
        "spend — was worth more lives than any other single lever available "
        "that night.\n"
    )
    lines.append(
        "*(Occupancy counts are reconstructions and are disputed; the "
        "inquiries' own totals exceed the confirmed survivor count. Read the "
        "gap as large and real, not as exactly " + f"{empty}.)*\n"
    )

    # ---- 4. fill against launch time: the mechanism ----
    launched = boats.dropna(subset=["launch_minutes_after_impact"]).copy()
    launched["fill"] = launched["aboard"] / launched["capacity"]
    r = float(np.corrcoef(launched["launch_minutes_after_impact"], launched["fill"])[0, 1])
    first_half = launched[launched["launch_minutes_after_impact"] <= 90]
    second_half = launched[launched["launch_minutes_after_impact"] > 90]

    lines.append("## Why the class coefficient exists: the first boats left empty\n")
    lines.append("| Launched | Boats | Mean fill |")
    lines.append("|---|---|---|")
    lines.append(f"| First 90 minutes | {len(first_half)} | {first_half['fill'].mean():.0%} |")
    lines.append(f"| After 90 minutes | {len(second_half)} | {second_half['fill'].mean():.0%} |")
    lines.append(
        f"\nFill rises with launch time (r = {r:.2f}). The earliest boats went "
        f"away barely a third full; the last ones went away over capacity. The "
        "failure was concentrated in the opening hour, before passengers and "
        "crew believed the ship was sinking.\n"
    )
    lines.append(
        "That timing supplies the **mechanism** behind the 7.6x first-class "
        "odds multiplier estimated in `06_revealed_policy.py`. Those early, "
        "half-empty boats were loaded from the boat deck, which the "
        "first-class accommodation opened onto. Nobody had to be turned away "
        "for a class gradient to appear — it is enough that the seats left "
        "early, and that proximity decided who was standing there. **Access "
        "plus disbelief, not malice.**\n"
    )

    # ---- 5. crew ----
    lines.append("## The group the dataset omits entirely\n")
    lines.append("| Department | Survived |")
    lines.append("|---|---|")
    for _, c in crew.iterrows():
        lines.append(f"| {c['department']} | {c['survival_rate']:.1%} |")
    lines.append(
        "\nEngineering and victualling crew — the people who kept power and "
        "lights on, and who were berthed lowest in the ship — died at roughly "
        "four-fifths. Deck crew, who were topside and who crewed the boats, "
        "survived at more than double that rate. Position in the ship "
        "predicted survival for the workforce exactly as it did for the "
        "passengers.\n"
    )

    # ---- 6. modern ----
    lines.append("## What this means on a modern ship\n")
    lines.append(
        "SOLAS now requires survival craft for everyone aboard, so the 1912 "
        "capacity gap is closed. **The constraint moved from seats to "
        "minutes.** IMO MSC.1/Circ.1533 sets the standard: complete "
        "evacuation — alarm, muster, embarkation, launch — within **60 "
        "minutes** for ships of three main vertical zones or fewer, and **80 "
        "minutes** for larger ships. On the Titanic's timeline the ship was "
        "gone 160 minutes after impact, and the boats were still leaving "
        "half-empty at the 90-minute mark.\n"
    )
    lines.append(
        "The modern failure mode is the same one the launch-time data "
        "exposes. **Costa Concordia, 2012:** 32 dead; passengers who had "
        "boarded at Civitavecchia that day had not yet completed a muster "
        "drill, and the alarm and abandon-ship order were delayed more than "
        "an hour. Same shape — the opening minutes decide it, and whoever "
        "does not know where to go, or does not believe it yet, is the one "
        "left aboard.\n"
    )
    lines.append(
        "At the industry's current scale — **37.2 million passengers in "
        "2025**, average age 46.5 — the question is not whether enough seats "
        "exist. It is whether the muster plan resolves who moves first, or "
        "whether, as in 1912, it quietly defaults to whoever is nearest the "
        "stairs when the alarm sounds. **That is measurable from drill "
        "records, without waiting for an incident.**\n"
    )

    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    # ---- chart 16: fill vs launch time ----
    fig, ax = plt.subplots(figsize=(8.5, 5))
    colors = [RED if t <= 90 else BLUE for t in launched["launch_minutes_after_impact"]]
    ax.scatter(launched["launch_minutes_after_impact"], launched["fill"],
               s=150, color=colors, zorder=4, edgecolor=SURFACE, linewidth=1.5)
    for _, b in launched.iterrows():
        ax.annotate(str(b["boat"]),
                    (b["launch_minutes_after_impact"], b["fill"]),
                    textcoords="offset points", xytext=(0, 13),
                    ha="center", fontsize=8.5, color=INK_SECONDARY)

    z = np.polyfit(launched["launch_minutes_after_impact"], launched["fill"], 1)
    xs = np.linspace(55, 150, 50)
    ax.plot(xs, np.poly1d(z)(xs), color=INK_SECONDARY, linestyle="--",
            linewidth=1.5, zorder=3)
    ax.axhline(1.0, color=MUTED, linewidth=1, zorder=2)
    ax.axvline(SANK_AT, color=RED, linewidth=1.5, zorder=2)
    ax.text(SANK_AT - 4, 0.06, "ship sinks", rotation=90, ha="right",
            va="bottom", fontsize=9.5, color=RED)
    ax.text(150, 1.02, "rated capacity", ha="right", va="bottom",
            fontsize=9.5, color=MUTED)

    ax.set_xlabel("Minutes after impact that the boat was launched")
    ax.set_ylabel("Share of rated capacity filled")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0%}"))
    ax.set_xlim(50, 168)
    ax.set_ylim(0, 1.2)
    ax.set_title("The first boats left barely a third full")
    style_axes(ax)
    fig.text(0.02, -0.02,
             f"Insight: fill rises with launch time (r = {r:.2f}). Boats launched in the first "
             f"90 minutes averaged {first_half['fill'].mean():.0%} of capacity; those after, "
             f"{second_half['fill'].mean():.0%}. {empty} seats left the ship empty. The failure was "
             "concentrated before anyone believed the ship was sinking. Occupancy figures are "
             "disputed reconstructions — read the pattern, not the decimals.",
             ha="left", va="top", fontsize=9.5, color=INK_SECONDARY, wrap=True)
    fig.savefig(f"{CHART_DIR}/16_lifeboat_fill_vs_time.png", dpi=150, bbox_inches="tight")
    plt.close(fig)

    # ---- chart 17: survival by class and category, full population ----
    pivot = bot.pivot_table(index="group", columns="category",
                             values=["carried", "saved"], aggfunc="sum")
    groups = ["First class", "Second class", "Third class"]
    cats = ["Men", "Women", "Children"]
    cat_colors = {"Men": ORANGE, "Women": BLUE, "Children": GOOD}

    x = np.arange(len(groups))
    width = 0.26
    fig, ax = plt.subplots(figsize=(8.5, 5))
    for i, cat in enumerate(cats):
        rates = [pivot.loc[g, ("saved", cat)] / pivot.loc[g, ("carried", cat)]
                 for g in groups]
        bars = ax.bar(x + (i - 1) * width, rates, width, label=cat,
                      color=cat_colors[cat], zorder=3)
        for b, v in zip(bars, rates):
            ax.text(b.get_x() + b.get_width() / 2, v + 0.015, f"{v:.0%}",
                    ha="center", va="bottom", fontsize=9, color=INK)

    ax.set_xticks(x)
    ax.set_xticklabels(groups)
    ax.set_ylabel("Share saved")
    ax.set_ylim(0, 1.12)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0%}"))
    ax.set_title("The same doctrine, three different outcomes")
    ax.legend(frameon=False, fontsize=10, loc="upper right")
    style_axes(ax)
    fig.text(0.02, -0.02,
             f"Insight: every second-class child survived; {lost_kids} of "
             f"{int(third_kids['carried'])} third-class children did not. "
             "British Wreck Commissioner's Inquiry, 1912 — all 2,206 aboard, crew included.",
             ha="left", va="top", fontsize=10, color=INK_SECONDARY, wrap=True)
    fig.savefig(f"{CHART_DIR}/17_inquiry_survival.png", dpi=150, bbox_inches="tight")
    plt.close(fig)

    print(f"Saved external validation report to {REPORT_PATH}")
    print(f"Saved charts 16 and 17 to {CHART_DIR}/")
    print(f"\nEmpty seats: {empty} | fill~time r = {r:.2f} | "
          f"3rd-class children lost: {lost_kids}/{int(third_kids['carried'])}")


if __name__ == "__main__":
    main()
