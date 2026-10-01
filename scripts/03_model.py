"""
Baseline survival-prediction models, framed as an evacuation-triage
classifier (see ../outputs/problem_statement.md).

Trains two models on the same features:
- Logistic regression: interpretable benchmark.
- Random forest: nonlinear comparison, also yields feature importances.

Reports standard classification metrics (accuracy, recall, ROC-AUC) plus a
fairness breakdown (recall by Pclass and Sex) for the better model, since
this dataset's strongest predictors (Pclass, Deck, Fare) are proxies for
structural access rather than individual risk — the business framing
explicitly asks for that gap to be visible, not folded into one aggregate
score.
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (RocCurveDisplay, classification_report,
                              confusion_matrix, recall_score, roc_auc_score)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

CLEAN_PATH = "../data/clean/titanic_clean.csv"
CHART_DIR = "../outputs/charts"
REPORT_PATH = "../outputs/model_report.md"

import os
os.makedirs(CHART_DIR, exist_ok=True)

# ---- palette (matches 02_eda_visuals.py) ----
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

NUMERIC_FEATURES = ["Age", "Fare", "FamilySize"]
CATEGORICAL_FEATURES = ["Pclass", "Sex", "Title", "Deck", "Embarked"]
RANDOM_STATE = 42


def style_axes(ax):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", color=GRID, linewidth=1, zorder=0)
    ax.set_axisbelow(True)


def build_preprocessor():
    return ColumnTransformer([
        ("num", StandardScaler(), NUMERIC_FEATURES),
        ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL_FEATURES),
    ])


def fairness_table(y_true, y_pred, groups, group_name):
    rows = [f"| {group_name} | n | Recall (TPR) |", "|---|---|---|"]
    df = pd.DataFrame({"y_true": y_true, "y_pred": y_pred, "group": groups})
    for g, sub in df.groupby("group", observed=True):
        n = len(sub)
        actual_pos = sub["y_true"].sum()
        recall = recall_score(sub["y_true"], sub["y_pred"]) if actual_pos > 0 else float("nan")
        rows.append(f"| {g} | {n} | {recall:.1%} |")
    return "\n".join(rows)


def main():
    df = pd.read_csv(CLEAN_PATH)
    df["FamilySize"] = df["SibSp"] + df["Parch"] + 1

    X = df[NUMERIC_FEATURES + CATEGORICAL_FEATURES]
    y = df["Survived"].astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=RANDOM_STATE
    )

    models = {
        "Logistic Regression": Pipeline([
            ("prep", build_preprocessor()),
            ("clf", LogisticRegression(max_iter=1000, random_state=RANDOM_STATE)),
        ]),
        "Random Forest": Pipeline([
            ("prep", build_preprocessor()),
            ("clf", RandomForestClassifier(
                n_estimators=300, max_depth=6, random_state=RANDOM_STATE
            )),
        ]),
    }

    report_lines = ["# Model Report\n",
                     "Framing: evacuation-triage classifier — see problem_statement.md.\n"]
    results = {}

    fig, ax = plt.subplots(figsize=(5.5, 5))
    for name, pipe in models.items():
        pipe.fit(X_train, y_train)
        y_pred = pipe.predict(X_test)
        y_proba = pipe.predict_proba(X_test)[:, 1]

        acc = (y_pred == y_test).mean()
        rec = recall_score(y_test, y_pred)
        auc = roc_auc_score(y_test, y_proba)
        results[name] = {"pipe": pipe, "y_pred": y_pred, "y_proba": y_proba, "auc": auc}

        report_lines.append(f"## {name}")
        report_lines.append(f"- Accuracy: {acc:.1%}")
        report_lines.append(f"- Recall (survived): {rec:.1%}")
        report_lines.append(f"- ROC-AUC: {auc:.3f}")
        report_lines.append("```\n" + classification_report(y_test, y_pred, target_names=["Died", "Survived"]) + "```\n")

        RocCurveDisplay.from_predictions(y_test, y_proba, name=name, ax=ax)

    ax.plot([0, 1], [0, 1], linestyle="--", color=INK_SECONDARY, linewidth=1)
    ax.set_title("ROC curve: Random Forest vs. Logistic Regression")
    style_axes(ax)
    fig.savefig(f"{CHART_DIR}/11_roc_curve.png", dpi=150, bbox_inches="tight")
    plt.close(fig)

    # ---- feature importance (Random Forest) ----
    rf_pipe = results["Random Forest"]["pipe"]
    feature_names = [n.split("__", 1)[1] for n in rf_pipe.named_steps["prep"].get_feature_names_out()]
    importances = rf_pipe.named_steps["clf"].feature_importances_
    imp = pd.Series(importances, index=feature_names).sort_values(ascending=False).head(10)

    fig, ax = plt.subplots(figsize=(7, 5))
    bars = ax.barh(imp.index[::-1], imp.values[::-1], color=BLUE, zorder=3)
    ax.set_title("Random Forest: top 10 feature importances")
    ax.set_xlabel("Importance")
    style_axes(ax)
    fig.savefig(f"{CHART_DIR}/12_feature_importance.png", dpi=150, bbox_inches="tight")
    plt.close(fig)

    # ---- pick the better model by AUC for the fairness audit ----
    best_name = max(results, key=lambda n: results[n]["auc"])
    best = results[best_name]
    report_lines.append(f"## Fairness audit ({best_name}, chosen by ROC-AUC)\n")
    report_lines.append("Recall (true positive rate) by group — a gap here means the model is "
                         "better at correctly flagging survivors in one group than another, "
                         "which for this dataset reflects structural access (class/deck), not "
                         "individual risk. Report this alongside accuracy, don't hide it.\n")
    report_lines.append(fairness_table(y_test, best["y_pred"], X_test["Pclass"], "Pclass") + "\n")
    report_lines.append(fairness_table(y_test, best["y_pred"], X_test["Sex"], "Sex") + "\n")

    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))

    print(f"Saved ROC curve and feature importance charts to {CHART_DIR}/")
    print(f"Saved model report to {REPORT_PATH}")


if __name__ == "__main__":
    main()
