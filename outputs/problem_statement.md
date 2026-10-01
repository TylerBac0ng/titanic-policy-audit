# Problem Statement

## The question
Every evacuation runs on a priority rule. Most of that rule is never
written down — but the outcomes encode it. **Can we recover the priority
rule an organisation actually ran, and measure its distance from the one
it published?**

Titanic is the worked example because it is the rare case where the stated
doctrine is known ("women and children first"), the outcome is fully
recorded, and an official inquiry counted every person aboard.

## Why not "predict survival"
A classifier fitted to 1912 outcomes recovers the 1912 decision rule,
structural bias included. Deploying it to assign seats would launder that
bias as a recommendation with a validation score attached.

The reframe keeps the method and inverts the purpose: the same fit, read
as a **measuring instrument**. Its coefficients estimate the priority
function the evacuation really applied. The bias stops being a defect to
mitigate and becomes the reading.

## The analysis
| Script | Question it answers |
|---|---|
| `01`–`02` | What does the passenger data show? |
| `03` | Is the historical rule learnable? (Yes — which is the problem.) |
| `04` | How do stated and realized allocation differ at fixed capacity? |
| `05` | Does a priority rule actually decide, or does the tiebreak? |
| `06` | **What rule was actually run?** (revealed-policy estimation) |
| `07` | What do the inquiry record and the boats themselves add? |

## What was found
- **The finding that needs no model:** every second-class child survived;
  53 of 76 third-class children did not. Same doctrine, same night, same
  ship.
- **The revealed rule:** being first class multiplied the odds of getting
  off by **7.6×** — more than being a child (4.6×). The stated doctrine
  never mentions class.
- **The measured drift:** **28%** of the explained priority rule comes
  from factors the written policy does not name.
- **The mechanism:** the first boats left 43% full and 449 seats went to
  sea empty. Those early boats loaded from the boat deck, which first-class
  accommodation opened onto. A class gradient needs no gatekeeper — only
  that the seats left early and proximity decided who was standing there.
- **A kept negative result:** grading a need-based rule gave it 12× the
  score levels and changed nothing, because the precision landed where
  there was never a contest.

## Why it matters on a modern ship
SOLAS now requires survival craft for everyone aboard, so the capacity gap
is closed. **The constraint moved from seats to minutes** — IMO
MSC.1/Circ.1533 sets 60 minutes (≤3 main vertical zones) or 80 minutes to
complete evacuation. Costa Concordia (2012, 32 dead) shows the failure
mode survived: passengers who had boarded that day had not yet mustered,
and the alarm was delayed over an hour.

Two things make the audit stronger today than it could ever have been in
1912:

1. **The confound breaks.** Decks A/B/C were 100% first class, so berth
   distance and fare class were the same variable. Modern ships mix price
   points across decks and share stairwells, so the two are finally
   separable.
2. **The data already exists.** Cabin number gives deck, stairwell and
   muster station; booking gives accessibility requests, linked
   reservations and language preference.

**The deliverable: run the audit on muster drill records.** Who reached
which station and how long they took is a live record of the realized
policy — measurable per sailing, from data already held, with no incident
required.

## Success criteria
Not accuracy. The outputs are a measured drift percentage, a coefficient
on a variable the policy does not name, and a reported spread showing how
much the tiebreak alone could have changed. A rule that does not
discriminate within the contested population is reported as such.

## What this cannot support
Intent, or causality. Deck, boarding position and proximity are
inseparable from class in 1912 data, so the honest claim is
class-correlated *access*. A true allocation tool would need the uplift
from a seat — P(survive | seat) − P(survive | no seat) — which is
unidentifiable here because treatment and outcome are nearly collinear.
