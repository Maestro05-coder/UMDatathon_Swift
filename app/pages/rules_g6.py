# Rule content for the g6 · Duration & FX page.

COLUMNS = """
| column | what it is | how g6 uses it |
| :--- | :--------- | :------------- |
| `TOTAL_DURATION` | how long the payment took, in seconds | the thing being explained |
| `BIC8_PATH` | the route, `;`-separated | the route is the sum of its steps — this defines the steps |
| `CURRENCY_CONVERSION_COUNT` | currency changes on the route | suspect #1: does FX cost time? (it doesn't) |
| `BIC8_PATH` contains `...` | one or more hidden banks | suspect #2: does hiding cost time? (it doesn't) |
| `TRANSACTION_TYPE_CODE` | Direct / Indirect / Covered | suspect #3: is "Covered" slow? (it isn't — Rule 6) |

No amounts, no parties — those can't move time anyway (g3 Rule 2).
"""

RULES = [
    dict(
        name="Duration is the sum of the per-step delays",
        quick=(
            "A route's total time is just the time of each leg added together; knowing "
            "each leg's typical duration predicts the whole journey within 6–14%."
        ),
        analogy=(
            "a flight with a stopover: total travel time = flight 1 + layover + flight "
            "2 — no mystery bonus for changing planes."
        ),
        tech="""
Take each step's own typical duration (measured from the millions of simple
2-bank payments containing that exact leg), add them up, and land next to the
real total:

| route | actual | steps added |
| :---- | -----: | ----------: |
| `0004IMD0;0077CHZ0;0086KRS0` | 322s | 322 + 17 = **339s** |
| `0026FIH0;0074SGS0;0007IMD0` | 93s | 72 + 31 = **103s** |
| `0412FRP0;0300CHZ0;0292CHZ0` | 503s | 360 + 157 = **517s** |
| `0068IT20;0309CHZ0;0216CHZ0` | 85s | 22 + 80 = **102s** |

Fitted over all measurable 3-bank routes: actual ≈ **−13 + 0.99 × predicted** —
a near-perfect identity line.
""",
    ),
    dict(
        name="A step's delay belongs to the bank, not the pair",
        quick=(
            "The same two banks always take about the same time, and a bank that is "
            "slow sending is also slow receiving — slowness is a bank property, drawn "
            "once."
        ),
        analogy=(
            "a slow mechanic is a slow mechanic, whether you drop the car off or they "
            "come to you."
        ),
        tech="""
Same bank pair → durations barely move (typical spread 4% of the median). And a
bank's typical delay when *sending* matches its delay when *receiving*:
correlation **0.87**.
""",
    ),
    dict(
        name="Steps come in two speeds — and one slow step ruins the payment",
        quick=(
            "Two-thirds of steps finish in under a minute, but if the route happens to "
            "include one slow bank, you wait hours."
        ),
        analogy=(
            "a road trip of nine fast highways and one toll booth that opens at 5pm — "
            "the booth defines the trip."
        ),
        tech="""
66% of steps take under a minute; 17% take over 15 minutes; the slowest seen is
11,237s (~3 hours). That's why durations are so lopsided: a 3-bank payment has a
**median of 80 seconds but a 75th percentile of 1,180 seconds** — most settle
fast, a route with one slow bank takes half a day.
""",
    ),
    dict(
        name="Currency conversions cost no time",
        quick=(
            "Payments that change currency along the way take exactly as long as those "
            "that don't — FX is priced in, not queued."
        ),
        analogy=(
            "the currency exchange desk at the airport is already on your path — it "
            "doesn't add an extra queue to the trip."
        ),
        tech="""
At 2 banks: 44s (0 conv) vs 38s (1 conv). At 3 banks: 126 / 80 / 81 s for 0 / 1 /
2 conversions. At 4 banks: 422 / 404 / 425 / 408. Flat everywhere.
""",
    ),
    dict(
        name="Hidden banks cost no time",
        quick=(
            "Routes that hide a bank (`...`) take the same time as routes that show "
            "everything — hiding is bookkeeping, not waiting."
        ),
        analogy=(
            "a redacted name on the document doesn't make the meeting run longer."
        ),
        tech="""
2-bank payments with a hidden bank: **44s**. Without: **44s**. A visibility
effect (g5's coin), not a delay.
""",
    ),
    dict(
        name="'Covered is 3–4× slower' was never about the label",
        quick=(
            "Covered payments only *look* slow; hold the countries and then the middle "
            "bank fixed and the 'slowness' melts from 3.27× to 1.14×."
        ),
        analogy=(
            "blaming the restaurant label for a long meal, when the real cause is which "
            "kitchen the order landed in."
        ),
        tech="""
| comparison | Covered ÷ Indirect |
| :--------- | ---: |
| raw, any 3-bank route | 3.27× |
| same corridor (same 3 countries) | 1.99× |
| same corridor + same middle bank | **1.14×** |

Covered payments aren't slow because they're Covered — those routes just happen
to use slower banks. And the label isn't tied to particular banks either: Covered
share varies only 8.6–13.9% across middle banks (base 11.3%).
""",
    ),
]

PATTERN = (
    "The common thread: regress toward the fair comparison. Whenever a "
    "group looks different (Covered looks slow), don't accept the raw number — re-run "
    "the comparison with everything else held fixed (corridor, then corridor + middle "
    "bank) and watch the gap walk down to nothing. And when a mechanism is absent "
    "(conversions, hidden banks), show it with the flat table: identical medians at "
    "every level of the suspect."
)

GLOSSARY = """
- **step** — one bank-to-bank leg of a route (a 3-bank payment has 2 steps).
- **2-bank payment** — a Direct payment; the laboratory where each step's typical
  delay is measured, because it has exactly one step.
- **corridor** — the sender country → beneficiary country pair, held fixed to make
  comparisons fair.
- **middle bank** — the bank(s) between sender and receiver.
- **dex** — not used on this page, but everywhere else: +1 dex = ×10.
"""
