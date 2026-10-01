"""
Titanic dataset cleaning.

Decisions (confirmed with project owner before running):
- Age (20% missing): impute with median grouped by Pclass + Sex, keep an
  Age_was_missing flag so imputed rows stay identifiable for analysis.
- Cabin (77% missing): extract Deck (first letter of cabin code, else
  "Unknown"), then drop the raw Cabin column.
- Name (free text, not directly analyzable): extract Title (Mr/Mrs/Miss/
  Master/Rare), then drop the raw Name column.
- Embarked (2 missing): fill with the column mode.
- Ticket: left as-is (no missing values); not used as an analysis feature.
"""

import pandas as pd

RAW_PATH = "../data/raw/Titanic-Dataset.csv"
CLEAN_PATH = "../data/clean/titanic_clean.csv"
REPORT_PATH = "../outputs/cleaning_report.txt"

TITLE_MAP = {
    "Mlle": "Miss", "Ms": "Miss", "Mme": "Mrs",
    "Lady": "Rare", "Countess": "Rare", "Sir": "Rare", "Jonkheer": "Rare",
    "Don": "Rare", "Dona": "Rare", "Major": "Rare", "Col": "Rare",
    "Capt": "Rare", "Rev": "Rare", "Dr": "Rare",
}


def main():
    df = pd.read_csv(RAW_PATH)
    report = []

    report.append(f"Raw shape: {df.shape}")
    report.append(f"Duplicate rows: {df.duplicated().sum()}")
    report.append(f"Duplicate PassengerId: {df['PassengerId'].duplicated().sum()}")
    report.append("\nMissing values per column (raw):")
    report.append(df.isna().sum().to_string())

    # --- Title from Name ---
    df["Title"] = df["Name"].str.extract(r",\s*([^.]*)\.")[0].str.strip()
    df["Title"] = df["Title"].replace(TITLE_MAP)
    title_counts = df["Title"].value_counts()
    rare_titles = title_counts[title_counts < 5].index
    df["Title"] = df["Title"].where(~df["Title"].isin(rare_titles), "Rare")
    report.append("\nTitle value counts (after grouping rare titles):")
    report.append(df["Title"].value_counts().to_string())
    df = df.drop(columns=["Name"])

    # --- Deck from Cabin ---
    df["Deck"] = df["Cabin"].str[0]
    df["Deck"] = df["Deck"].fillna("Unknown")
    report.append("\nDeck value counts (Unknown = missing Cabin):")
    report.append(df["Deck"].value_counts().to_string())
    df = df.drop(columns=["Cabin"])

    # --- Embarked: fill 2 missing with mode ---
    n_missing_embarked = df["Embarked"].isna().sum()
    embarked_mode = df["Embarked"].mode()[0]
    df["Embarked"] = df["Embarked"].fillna(embarked_mode)
    report.append(
        f"\nEmbarked: filled {n_missing_embarked} missing value(s) with mode '{embarked_mode}'"
    )

    # --- Age: median imputed by Pclass + Sex, with a missing flag ---
    df["Age_was_missing"] = df["Age"].isna()
    n_missing_age = df["Age_was_missing"].sum()
    df["Age"] = df.groupby(["Pclass", "Sex"])["Age"].transform(
        lambda s: s.fillna(s.median())
    )
    report.append(
        f"\nAge: imputed {n_missing_age} missing value(s) using the median Age "
        "within each Pclass+Sex group; flagged in Age_was_missing"
    )
    report.append("Median age by Pclass + Sex (used for imputation):")
    report.append(df.groupby(["Pclass", "Sex"])["Age"].median().to_string())

    # --- Fare: check for anomalies, no changes made ---
    zero_fare = (df["Fare"] == 0).sum()
    report.append(
        f"\nFare: {zero_fare} rows have Fare == 0 (likely crew/employee/"
        "comp tickets, e.g. ticket 'LINE'). Left as-is; noted for analysis."
    )
    report.append(df["Fare"].describe().to_string())

    # --- Data types ---
    df["Survived"] = df["Survived"].astype(bool)
    df["Pclass"] = df["Pclass"].astype("category")
    df["Sex"] = df["Sex"].astype("category")
    df["Embarked"] = df["Embarked"].astype("category")
    df["Title"] = df["Title"].astype("category")
    df["Deck"] = df["Deck"].astype("category")

    report.append(f"\nFinal shape: {df.shape}")
    report.append("\nFinal missing values per column:")
    report.append(df.isna().sum().to_string())

    df.to_csv(CLEAN_PATH, index=False)
    with open(REPORT_PATH, "w") as f:
        f.write("\n".join(str(r) for r in report))

    print("\n".join(str(r) for r in report))
    print(f"\nSaved cleaned data to {CLEAN_PATH}")
    print(f"Saved cleaning report to {REPORT_PATH}")


if __name__ == "__main__":
    main()
