# Sensitivity Analysis

Every rule re-run **1,000 times at 341 seats**, breaking ties at random instead of by PassengerId. A rule that really decides the outcome barely moves between runs. A rule that defers to circumstance swings — and that swing is the honest error bar on any claim made about it.

## Rule resolution

| Rule | Distinct score levels | Contention at cutoff |
|---|---|---|
| Women & children first | 3 | 1.05x |
| Need-based (coarse) | 5 | 2.27x |
| Need-based (graded) | 62 | 2.25x |

## What the tiebreak alone can change

3rd-class coverage across random tiebreaks:

| Rule | Min | Median | Max | Swing |
|---|---|---|---|---|
| Women & children first | 33% | 34% | 35% | **2.0 pts** |
| Need-based (coarse) | 39% | 42% | 46% | **7.3 pts** |
| Need-based (graded) | 40% | 43% | 47% | **7.5 pts** |

**The coarse need rule's 3rd-class coverage swings 7.3 points on the tiebreak alone** — across those runs the rule is not choosing, the coin is.

'Women and children first' swings only 2.0 points despite leaving most seats tied, because its tied tier is homogeneous and almost fully seated. Low contention, not high resolution, is what makes a coarse rule safe — a rule needs one or the other.

## Why adding resolution did not help

The graded rule has 62 score levels against the coarse rule's 5, and it changed nothing: contention 2.27x to 2.25x, swing 7.3 to 7.5 points. The tied tier explains it:

| Contested tier at the cutoff | Value |
|---|---|
| Passengers tied | 516 |
| Children | 0 |
| Elderly | 0 |
| Large families | 0 |
| Travelling alone | 516 |
| Mean age | 29.8 |

Every graded term — the age curves, the family-size burden — evaluates to **zero for all 516** of them. They are healthy adults travelling alone, and they all score identically because none of the criteria describe them. The extra levels were added where there was never a contest.

## Takeaway

**Resolution only helps where the contention is.** Adding precision to a rule feels like progress and can be measured as progress (12x the score levels) while changing nothing about the decision that is actually being made.

The harder conclusion: *this dataset cannot support a class-blind triage rule for the contested seats.* The population competing for them is homogeneous on every class-blind variable available — age, family structure, accompaniment. Separating them needs a variable nobody recorded: mobility or assistance need, distance from berth to muster station, language. **The fix is not a better rule or a better model, it is instrumenting the right field at boarding** — which is a capital-cheap operational change, and the most transferable recommendation this project produces.

Corollary for reporting: publish a triage rule with the spread its tiebreak can produce. A single-run allocation table looks equally authoritative whether the rule decided it or a coin did.
