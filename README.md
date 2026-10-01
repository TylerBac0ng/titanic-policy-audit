# The Policy Nobody Wrote Down

Recovering the priority rule the Titanic evacuation **actually ran** — and
measuring its distance from the rule that was written down.

Most Titanic analysis asks *"who survived?"* That is a prediction problem,
and a model fitted to 1912 outcomes simply recovers the 1912 decision rule,
structural bias included. This project asks the inverted question —
*"what rule did we actually run?"* — which turns the same model from a
predictor into a **measuring instrument**.

---

## Headline findings

| | |
|---|---|
| **Every second-class child survived.** 53 of 76 third-class children did not. | Same doctrine, same night, same ship. Needs no model. |
| **Being first class multiplied the odds of survival 7.6×** — more than being a child (4.6×). | The stated doctrine never mentions class. |
| **27.6% of the explained priority rule** comes from factors the written policy does not name. | McFadden pseudo-R² 0.232 → 0.321. |
| **449 lifeboat seats went to sea empty.** The first boats left 43% full, the last 72%. | Capacity was not the binding constraint. |
| **12× the score resolution changed nothing.** | A kept negative result — see below. |

### The mechanism

A class gradient needs no gatekeeper. It is enough that the seats left
**early**, and that proximity decided who was standing on the boat deck
when they did — first-class accommodation opened directly onto it.
Access plus disbelief, not malice.

### The negative result worth keeping

The hypothesis was that a coarse need-based triage rule failed because it
lacked resolution. Grading its criteria gave it **12× more score levels
(5 → 62) and changed nothing**: contention 2.27× → 2.25×, swing 7.3 → 7.5
points.

The reason matters more than a fix would have. The 516 passengers
contested at the cutoff are solo adults with no child, elderly or
large-family status, so every graded term evaluates to zero across all of
them. **Resolution only helps where the contention is.** Adding precision
to a rule feels like progress and can be *measured* as progress while
changing nothing about the decision being made.

---

## Why it matters on a modern ship

SOLAS now requires survival craft for everyone aboard, so the 1912 capacity
gap is closed. **The constraint moved from seats to minutes** — IMO
MSC.1/Circ.1533 requires complete evacuation within 60 minutes (≤3 main
vertical zones) or 80 minutes. Costa Concordia (2012, 32 dead) shows the
failure mode survived: a cohort aboard had not yet completed a muster
drill, and the alarm was delayed over an hour.

Two things make the audit **stronger today than it could ever have been in
1912**:

1. **The confound breaks.** Decks A, B and C were 100% first class, so
   berth distance and fare class were literally the same variable. Modern
   ships sell different price points on the same deck sharing the same
   stairwells — the two are finally separable.
2. **The data already exists.** Cabin number gives deck, stairwell and
   assigned muster station; booking records give accessibility requests,
   linked reservations and language preference.

Which means the audit can run on **muster drill records** — per sailing,
from data already held, with no incident required.

---

## Repository structure

```
data/
  raw/        Kaggle Titanic training split (891 passengers)
  clean/      cleaned output of 01
  external/   1912 inquiry figures, per-lifeboat records, crew departments
              + SOURCES.md with full provenance and caveats
scripts/
  01_clean_data.py          imputation and feature extraction
  02_eda_visuals.py         exploratory charts + findings
  03_model.py               predictive baseline + fairness audit
  04_allocation.py          three policies compared at fixed capacity
  05_sensitivity.py         tiebreak robustness; the negative result
  06_revealed_policy.py     revealed-policy estimation (the core method)
  07_external_validation.py inquiry record, lifeboats, crew
outputs/
  charts/     17 figures
  *.md        a written report per script
```

Run in order from inside `scripts/`:

```bash
cd scripts
python 01_clean_data.py
python 02_eda_visuals.py
python 03_model.py
python 04_allocation.py
python 05_sensitivity.py
python 06_revealed_policy.py
python 07_external_validation.py
```

Requires `pandas`, `numpy`, `matplotlib`, `scikit-learn`.

---

## Method note

`06_revealed_policy.py` is the core of the project, and its three design
choices are each the *opposite* of what prediction would call for:

- **All 891 rows, no holdout** — estimating, not forecasting.
- **No regularisation** — L2 shrinks coefficients toward zero, and those
  coefficients are the measurement.
- **Bootstrap intervals** (1,000 resamples) — a point estimate with no
  uncertainty is not a measurement.

Nested comparison: fit the doctrine's own variables (sex, child), then add
the ones it never names (class, fare, party). The gain in fit is the drift.

---

## What this cannot support

- **Weight, not intent.** Correlational throughout. Deck, boarding position
  and proximity are inseparable from class in 1912 data, so the honest
  claim is class-correlated *access* — never that anyone was turned away.
- **Not an allocation tool.** Allocating seats needs the uplift from a seat,
  P(survive | seat) − P(survive | no seat). Treatment and outcome are
  nearly collinear here, so that quantity is unidentifiable.
- **Disputed sources.** Boat occupancy figures are post-hoc reconstructions
  and the two inquiries disagree — both of their totals exceed the
  confirmed survivor count. 449 is a shape, not a decimal.
- **Partial sample.** 891 of 2,206 people, passengers only, 177 ages imputed
  at a class-and-sex median. Every population-level claim comes from the
  inquiry record rather than the model.

---

## Sources

- [British Wreck Commissioner's Inquiry (1912), passenger and crew numbers](https://www.titanicinquiry.org/BOTApp/BOTApp01.php)
- [Lifeboats of the Titanic — per-boat capacity, occupancy, launch times](https://en.wikipedia.org/wiki/Lifeboats_of_the_Titanic)
- [IMO MSC.1/Circ.1533 — evacuation analysis guidelines](https://safetyatsea.uk/imo-msc-1-circ-1533-guidelines/)
- [Costa Concordia casualty investigation](https://www.seatrade-cruise.com/safety-security/costa-concordia-casualty-probe-pinpoints-series-of-human-failures)
- [CLIA State of the Cruise Industry](https://cruising.org/resources/state-cruise-industry-report-2026)

Full provenance, corrections and caveats: [`data/external/SOURCES.md`](data/external/SOURCES.md).
