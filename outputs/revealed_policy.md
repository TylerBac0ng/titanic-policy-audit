# The Revealed Policy

The evacuation ran on some priority rule. Nobody wrote it down, but the outcomes encode it. Fitting an unregularised logistic model to all 891 passengers — as a measuring instrument, not a predictor — estimates that implicit rule. Coefficients are reported as **odds multipliers**: how much a factor multiplied the odds of getting off the ship, holding the others fixed.

## The rule that was actually run

| Factor | Named by the stated doctrine? | Odds multiplier | 95% CI |
|---|---|---|---|
| Female | **Yes** | 14.98× | 10.51–23.06 |
| Child | **Yes** | 4.64× | 2.03–11.35 |
| 1st class | No | 7.56× | 4.09–14.80 |
| 2nd class | No | 3.11× | 2.07–4.71 |
| Fare (log, sd) | No | 1.07× | 0.81–1.43 |
| Travelling alone | No | 1.33× | 0.85–2.05 |

'Women and children first' names two factors. Being female multiplied the odds by 15.0× and being a child by 4.6× — the doctrine was real and it was strong.

But **first class multiplied the odds by 7.6×**, and the stated doctrine does not mention class at all. That coefficient is the policy nobody wrote down.

## How much of the real policy the written one explains

| Model | Factors | McFadden pseudo-R² |
|---|---|---|
| Stated doctrine | sex, child | 0.232 |
| Revealed policy | + class, fare, alone | 0.321 |

**28% of the explained priority rule comes from factors the stated policy never names.** That fraction is the drift, measured rather than asserted.

## What this cannot tell you

Decks A, B and C in this dataset are 100% first class; only 204 of 891 passengers have any cabin recorded at all. **Distance from berth to the boat deck is therefore not separable from class here** — the two are the same variable in 1912. So the honest statement is class-correlated *access*, not a claim that anyone was turned away, and certainly not intent.

That confound is itself the bridge to the modern case. On a modern ship, cabins at different price points sit on the same deck and share the same stairwells, so deck distance and fare class finally *are* separable. The audit that could not be run in 1912 is identified today.

## Reading this on a modern ship

Capacity is no longer the constraint: SOLAS requires survival craft for everyone aboard. The scarce resource has moved from **seats to time** — the evacuation window, and who can physically reach an assigned muster station inside it. The allocation question is the same shape, and so is the failure mode.

The fields this analysis said were missing in 1912 are already collected at booking today:

| 1912 gap | Modern equivalent already on file |
|---|---|
| Distance from berth to boat deck | Cabin number → deck, stairwell, muster station |
| Mobility or assistance need | Accessibility requests at booking |
| Who is travelling with whom | Booking party / linked reservations |
| Whether instructions are understood | Language preference on the reservation |

**And the audit does not need a disaster to run.** Muster drill records — who reached which station, and how long it took, by cabin, by deck, by mobility flag — are a live record of the realized policy. Fit the same instrument to drill timings and it returns the priority rule the ship actually operates, which can then be compared against the written muster plan.

The 1912 question, restated for a modern operator: *does your realized evacuation order track assistance need and distance — or does it still track deck and fare, with a written policy that says otherwise?* That is measurable this quarter, from data already held, and the contention check in 05_sensitivity.py says whether the muster plan is resolving the decision at all or leaving it to whoever is nearest the stairwell.
