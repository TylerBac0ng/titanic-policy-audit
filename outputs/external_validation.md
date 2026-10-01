# External Validation

What the Kaggle sample cannot see, and what changes when you bring in the inquiry record and the boats themselves.

## The sample is 40% of the problem

| | People |
|---|---|
| Aboard (British Inquiry) | 2,206 |
| Saved | 702 (32%) |
| Crew aboard — absent from the Kaggle data | 898 (41%) |
| Passengers in the Kaggle training split | 891 |

The modelling scripts see 891 of 2,206 people. Every one of the 898 crew is missing, and crew were both the largest single group aboard and the group doing the evacuating. Any claim about 'who was prioritised' from the sample alone is a claim about passengers only.

## The finding that needs no model

| Class | Children aboard | Saved | Survived |
|---|---|---|---|
| First class | 5 | 4 | **80%** |
| Second class | 24 | 24 | **100%** |
| Third class | 76 | 23 | **30%** |

**Every second-class child survived. 53 of 76 third-class children did not.**

This is the whole argument in one line, and it needs no statistics. 'Women and children first' was not a policy that failed for want of capacity — in second class it was executed perfectly. The same doctrine, on the same night, on the same ship, produced a 100% survival rate one deck up and 30% below. That gap is the revealed policy, visible without a single coefficient.

## Capacity was not the binding constraint — measured, not inferred

| | Seats |
|---|---|
| Rated lifeboat capacity | 1,178 |
| People actually carried away in them | 729 |
| **Seats that went to sea empty** | **449** |

The boats were filled to 62% of their rating. **449 seats left the ship unused** while roughly 1,500 people remained on board. Filling the boats that were already in the water — no extra davits, no design change, no capital spend — was worth more lives than any other single lever available that night.

*(Occupancy counts are reconstructions and are disputed; the inquiries' own totals exceed the confirmed survivor count. Read the gap as large and real, not as exactly 449.)*

## Why the class coefficient exists: the first boats left empty

| Launched | Boats | Mean fill |
|---|---|---|
| First 90 minutes | 6 | 43% |
| After 90 minutes | 12 | 72% |

Fill rises with launch time (r = 0.46). The earliest boats went away barely a third full; the last ones went away over capacity. The failure was concentrated in the opening hour, before passengers and crew believed the ship was sinking.

That timing supplies the **mechanism** behind the 7.6x first-class odds multiplier estimated in `06_revealed_policy.py`. Those early, half-empty boats were loaded from the boat deck, which the first-class accommodation opened onto. Nobody had to be turned away for a class gradient to appear — it is enough that the seats left early, and that proximity decided who was standing there. **Access plus disbelief, not malice.**

## The group the dataset omits entirely

| Department | Survived |
|---|---|
| Deck | 45.5% |
| Engineering | 21.8% |
| Victualling | 22.2% |

Engineering and victualling crew — the people who kept power and lights on, and who were berthed lowest in the ship — died at roughly four-fifths. Deck crew, who were topside and who crewed the boats, survived at more than double that rate. Position in the ship predicted survival for the workforce exactly as it did for the passengers.

## What this means on a modern ship

SOLAS now requires survival craft for everyone aboard, so the 1912 capacity gap is closed. **The constraint moved from seats to minutes.** IMO MSC.1/Circ.1533 sets the standard: complete evacuation — alarm, muster, embarkation, launch — within **60 minutes** for ships of three main vertical zones or fewer, and **80 minutes** for larger ships. On the Titanic's timeline the ship was gone 160 minutes after impact, and the boats were still leaving half-empty at the 90-minute mark.

The modern failure mode is the same one the launch-time data exposes. **Costa Concordia, 2012:** 32 dead; passengers who had boarded at Civitavecchia that day had not yet completed a muster drill, and the alarm and abandon-ship order were delayed more than an hour. Same shape — the opening minutes decide it, and whoever does not know where to go, or does not believe it yet, is the one left aboard.

At the industry's current scale — **37.2 million passengers in 2025**, average age 46.5 — the question is not whether enough seats exist. It is whether the muster plan resolves who moves first, or whether, as in 1912, it quietly defaults to whoever is nearest the stairs when the alarm sounds. **That is measurable from drill records, without waiting for an incident.**
