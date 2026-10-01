# Resource Allocation Analysis

Three allocation policies compared at **identical capacity (341 seats)** — the number who actually survived in this 891-passenger sample. No survival model is used here; see the script docstring for why.

## The capacity question

355 passengers in this sample were women or children, against 341 seats. The stated policy of the day was very nearly affordable with the boats that launched — the shortfall was in *execution*, not capacity.

## Who each policy seats

| Policy | Seats | % female | Children | Mean age |
|---|---|---|---|---|
| Actual (1912) | 341 | 68% | 42 | 28.1 |
| Women & children first | 341 | 88% | 72 | 24.7 |
| Need-based (class/sex-blind) | 341 | 33% | 73 | 26.8 |

## Seats by passenger class

Share of each class that receives a seat:

| Policy | 1st | 2nd | 3rd |
|---|---|---|---|
| Actual (1912) | 63% | 47% | 24% |
| Women & children first | 43% | 44% | 34% |
| Need-based (class/sex-blind) | 30% | 40% | 41% |

## How far the realized policy drifted

- **Women & children first**: 245 of 341 seats (72%) go to the same people who actually survived. **96 seats (28%) change hands.**
- **Need-based (class/sex-blind)**: 135 of 341 seats (40%) go to the same people who actually survived. **206 seats (60%) change hands.**

96 passengers would have been seated under a perfectly executed 'women and children first' but did not survive — 87 of them (91%) were 3rd class. This is the core audit finding: the realized policy tracked class, and the stated policy was applied to upper decks first.


## Does each rule actually sort people?

A priority rule is only operational if it discriminates *within* the population competing for the last seats. Where a rule ties, the allocation falls through to whoever arrives first — which in practice means proximity and status, the very bias the rule was meant to remove. Seats decided at a tied score:

| Policy | Outright | Contested tier | Seats left | Contention |
|---|---|---|---|---|
| Women & children first | 32 | 323 | 309 | 1.05x |
| Need-based (class/sex-blind) | 99 | 549 | 242 | 2.27x |

*Contention* is how many people are tied at the cutoff per seat still available. It, not the raw tiebreak count, says whether the tiebreak changes the **character** of who sails.

- **Women & children first** looks poorly determined (most seats sit at a tied score) but is contended only 1.05x: everyone in the tied tier is a woman or child, and nearly all of them are seated. The tiebreak picks *which* 309 of 323 — it cannot violate the policy's intent.
- **Need-based** is contended 2.27x across a tier of 549 heterogeneous passengers, so the tiebreak decides most of the boat and can pick any composition at all. **Read its class and sex columns above as largely an artifact of the tiebreak, not a result.**

That is the finding, not a bug to tune away: a triage rule with too few levels silently hands the decision back to circumstance — proximity, status, whoever reached the deck first. Resolution has to be designed to the population you will actually face (graded mobility, distance to muster, dependants), and it should be stress-tested by contention at capacity before anyone relies on it.

## What this translates to today

The transferable deliverable is not a survival score — it is the **policy-drift audit**: state your priority rule, simulate it at real capacity, then measure the distance between it and what your operation actually does. Cruise, aviation, stadium, and hospital-surge planners all hold a stated priority doctrine; few measure realized allocation against it. The gap is usually where an unstated variable (proximity, status, tier) has quietly become the sort order.

Operationally, the class gap here is a **staffing and access** problem, not a scoring one: it points at crew placement, stairwell and corridor capacity, and muster assignment for the berths furthest from the boat deck — the levers that decide who physically reaches a seat within the evacuation window.
