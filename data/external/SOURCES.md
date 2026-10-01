# External data sources

The Kaggle training split (891 rows) is a sample of passengers only. These
files bring in the population figures and the physical constraint data it
cannot contain. Every figure here is transcribed from a cited source, not
derived from the modelling.

## `bot_inquiry_1912.csv`

British Wreck Commissioner's Inquiry (1912), Appendix — "Passenger and Crew
numbers and percentages."
Source: https://www.titanicinquiry.org/BOTApp/BOTApp01.php

Covers all **2,206** people aboard, of whom **898 were crew** — crew are
entirely absent from the Kaggle dataset, so 41% of the population aboard is
invisible to the modelling scripts.

Correction applied: the inquiry table records 5 of 5 first-class children
saved (100%). Its own footnote states that one first-class child, Lorraine
Allison, was lost. This file records `saved = 4` and flags it in
`note`. All other figures are transcribed unchanged.

## `lifeboats.csv`

Per-boat rated capacity, people aboard at launch, and launch time.
Source: https://en.wikipedia.org/wiki/Lifeboats_of_the_Titanic

**Occupancy figures are disputed.** The contemporary inquiries recorded 854
(US) and 795 (British) people in the boats, both well above the confirmed
712 survivors — occupants were transferred between boats and counts were
reconstructed after the fact. The per-boat numbers here are the commonly
cited reconstruction and should be read as approximate: the analysis uses
them for the *shape* of the pattern (fill against launch time), not for
precise counts. Collapsibles A and B floated off as the ship went down
rather than being launched, so they carry no launch time.

## `crew_departments.csv`

Crew survival by department. Derived from reported death counts and
survival rates; department totals are back-calculated from those two
figures and are therefore approximate (they sum to 899 against the
inquiry's 898, and to 214 saved against its 210).
Source: https://grokipedia.com/page/Crew_of_the_Titanic and the British
Inquiry report at https://www.titanicinquiry.org/

## Modern-context figures (cited in reports, not stored as data)

- Evacuation performance standard: total evacuation within **60 minutes**
  (ro-ro passenger ships, or ships of three main vertical zones or fewer)
  or **80 minutes** (more than three zones) — IMO MSC.1/Circ.1533, Revised
  Guidelines on Evacuation Analysis for New and Existing Passenger Ships
  (2016), made mandatory via SOLAS Reg. II-2/13.3.2.7.
- Costa Concordia (13 January 2012): 32 deaths. Passengers who had boarded
  that day at Civitavecchia had **not yet completed a muster drill**;
  alarm and abandon-ship were delayed over an hour. Italian Marine
  Casualties Investigative Body report.
- Scale: **37.2 million** cruise passengers in 2025; average passenger age
  **46.5**, with roughly a quarter baby boomers — CLIA State of the Cruise
  Industry.
