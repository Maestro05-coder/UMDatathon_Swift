# Rule content for the g1 · Time page: COLUMNS, RULES (quick + analogy + tech), PATTERN, GLOSSARY.

COLUMNS = """
| column | what it is | how g1 uses it |
| :--- | :--------- | :------------- |
| `EPOCH_SECONDS` | when the payment happened, in UTC seconds | the thing being explained — its hour of the day |
| `BIC8_PATH` (first bank) | the sender's bank; characters 5–6 give the sender's country | which country's clock the payment should follow |
| `ANOMALY_TYPE` | anomaly label or empty | only clean rows are used |
| `half` | a built-in 50/50 row split | check: recover every clock twice, independently |

That's it. No currency, no amounts, no party text — those belong to g2, g3 and g7.
"""

RULES = [
    dict(
        name="Every country runs on its own whole-hour clock, cut from one shared template",
        quick=(
            "All 10M payments follow one single busy-day rhythm; each country just plays "
            "that rhythm shifted by a whole number of hours."
        ),
        analogy=(
            "a café chain where every branch opens at '6am local' — same routine everywhere, "
            "and branches differ only by whole-hour clock offsets."
        ),
        tech="""
Plot payments by UTC hour and countries don't line up at all — average curve
similarity **−0.024** (noise). Shift each country by *its own* whole-hour offset
and all 113 country curves collapse onto the shared shape: **+0.990**.

| clock | avg curve similarity (113 countries) |
| :---- | ---: |
| file's own UTC clock | −0.024 — looks like noise |
| shifted by each country's own hour offset | **+0.990** — near-perfect |

The offsets are not fitted curves: they are **18 distinct integer hours** covering
all 113 countries — `+6 h` for 28 countries, `+7 h` for 15, `+1 h` for 10, `+8 h`
for 9, `+5 h` for 9, `0 h` for 8, `−11 h` for 8, and eleven more values. The
offset table itself is charted as `g1_6_offset_table.png` — a generator lookup
from country to clock, not a measurement of real-world time zones.
""",
    ),
    dict(
        name="The two busy windows carry the same payments, just at different hours",
        quick=(
            "The day has two busy humps, but the payments in the second hump are the same "
            "kind as in the main one — it is not a special batch cut off at some deadline."
        ),
        analogy=(
            "morning rush and after-lunch rush at a bank: the same customers come at both, "
            "just at different times of day."
        ),
        tech="""
The shared template has a main window (hours 22, 23, 0, 1, 2 from the peak —
**32.9%** of payments) and a second window (hours 13–16 — **20.1%**), with a dead
zone in between (1.6% per hour).

The "cut-off batch" story predicts the two windows carry *different* payments.
Holding the country fixed across 113 countries (≥5,000 clean rows each), second
window minus main window:

| measured per country | median | p10 | p90 |
| :--- | ---: | ---: | ---: |
| log10 amount ratio | +0.0058 | −0.0319 | +0.0357 |
| cross-border share | +0.0000 | −0.0012 | +0.0013 |
| business-sender share | +0.0025 | −0.0089 | +0.0179 |

Only **1 of 113** countries shifts its amount by more than 0.1 dex between the
windows. Pooled over all rows: median duration 55 s vs 54 s, median amount
$3,875 vs $4,108, cross-border 92.57% vs 92.08%. Same mix, different hour —
a second hump, not a second process.
""",
    ),
    dict(
        name="The clock is exact — an integer lookup, not a fitted curve",
        quick=(
            "Recovering every country's clock twice from independent halves of the data "
            "gives the same hour (90 of 113) or off by exactly one hour (23) — never "
            "something fussy like 'half past'."
        ),
        analogy=(
            "two people reading the same wall clock agree exactly, or land on the "
            "neighbouring hour while the hands move — never '10:37.2'."
        ),
        tech="""
Recovering each country's offset independently from two disjoint halves of the
rows (`half` column): **90 of 113** countries get the identical hour. The other
23 differ by **exactly one hour** — always two adjacent high hours of the same
flat-topped peak — while their 24-hour curves still correlate ≥ 0.858 (median
0.991). A fitted or random clock would disagree by fractional amounts and
scatter; an integer lookup produces exactly ±1 h ties.
""",
    ),
    dict(
        name="It's a working-day template: weekends are nearly closed",
        quick=(
            "Each weekday carries 17–18% of payments; Saturday and Sunday together only "
            "11.2%, versus 28.6% if all seven days were equal."
        ),
        analogy="offices that shut for the weekend.",
        tech="""
Weekdays each carry 17.05–18.34% of payments; Saturday **4.35%** and Sunday
**6.84%** — weekend **11.18%** overall vs 28.6% if all days were equal. The three
hours around the peak hold 21.43% of payments; 10 of 24 hours sit below half the
peak.
""",
    ),
]

PATTERN = (
    "The one pattern behind all four: take the column that should cause the rhythm "
    "(the sender's country), group all 10M rows by it, and read the day twice — once "
    "on the UTC clock, once on the country's own clock. A real local rhythm shows up "
    "as a huge correlation jump (−0.02 → +0.99); and if the generator used a lookup "
    "table, the disagreements come in whole hours, not fractions."
)

GLOSSARY = """
- **clock / offset** — how many whole hours a country's working day is shifted
  from the reference country. Not real-world time zones: the +6 h group isn't
  "the +6 time zone", it's the value the generator assigned.
- **aligned day** — every country rolled so its own busiest hour becomes hour 0.
  The shape all 113 countries share after rolling.
- **main / second window** — the two humps of the aligned day: hours 22–02 and
  13–16 measured from each country's peak.
- **clean row** — a payment with no anomaly label (see g8).
"""
