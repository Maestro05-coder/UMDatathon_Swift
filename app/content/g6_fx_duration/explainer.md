## The columns g6 uses

| column | what it is | how g6 uses it |
| :--- | :--------- | :------------- |
| `TOTAL_DURATION` | how long the payment took, in seconds | the thing being explained |
| `BIC8_PATH` | the route, `;`-separated | the route is the sum of its steps — this defines the steps |
| `CURRENCY_CONVERSION_COUNT` | how many currency changes on the route | suspect #1: does FX cost time? (it doesn't) |
| `BIC8_PATH` contains `...` | one or more hidden banks | suspect #2: does hiding cost time? (it doesn't) |
| `TRANSACTION_TYPE_CODE` | Direct / Indirect / Covered | suspect #3: is "Covered" slow? (it isn't — Rule 6) |

That's it. No amounts, no parties — those can't move time anyway (g3 Rule 2).

## The rules, and how each is squeezed out

**Rule 1 — Duration is the sum of the per-step delays.**
A route with 3 banks has 2 steps: sender→middle, middle→receiver. Measure each
step's own typical time from the millions of simple 2-bank payments that contain
that exact leg, add the two, and you land next to the real durations:

| route | actual | steps added |
| :---- | -----: | ----------: |
| `0004IMD0;0077CHZ0;0086KRS0` | 322s | 322 + 17 = **339s** |
| `0026FIH0;0074SGS0;0007IMD0` | 93s | 72 + 31 = **103s** |
| `0412FRP0;0300CHZ0;0292CHZ0` | 503s | 360 + 157 = **517s** |
| `0068IT20;0309CHZ0;0216CHZ0` | 85s | 22 + 80 = **102s** |

Fitted over all measurable 3-bank routes: actual ≈ −13 + **0.99** × predicted —
a near-perfect identity line.

**Rule 2 — A step's delay belongs to the bank, not the pair.**
The same bank pair's durations barely move (typical spread 4% around the median).
And a bank's typical delay when *sending* matches its delay when *receiving*:
correlation **0.87**. Slow banks are slow in both directions — the delay is a
per-bank property the generator drew once.

**Rule 3 — Steps come in two speeds, and one slow step ruins the payment.**
66% of steps finish in under a minute; 17% take over 15 minutes; the slowest seen
is 11,237s (~3 hours). That's why durations are lopsided: a 3-bank payment has a
**median of 80 seconds but a 75th percentile of 1,180 seconds**. Most payments
settle fast; a route that includes one slow bank makes you wait half a day.

**Rule 4 — Currency conversions cost no time.**
At 2 banks: 44s with no conversion vs 38s with one. At 3 banks: 126 / 80 / 81 s
for 0 / 1 / 2 conversions. At 4 banks: 422 / 404 / 425 / 408. Flat everywhere —
in this world FX is priced in, not queued.

**Rule 5 — Hidden banks cost no time.**
2-bank payments with a hidden bank: 44s. Without: 44s. Hiding is a *visibility*
effect (g5's coin), not a delay.

**Rule 6 — "Covered is 3–4× slower" is not caused by the label.** (the detective
story) The raw gap is huge: Covered ÷ Indirect = **3.27×**. But the gap shrinks
as the comparison gets fairer:

| comparison | Covered ÷ Indirect |
| :--------- | -----------------: |
| raw, any 3-bank route | 3.27× |
| same corridor (same 3 countries) | 1.99× |
| same corridor **+ same middle bank** | **1.14×** |

Covered payments aren't slow *because* they're Covered — those routes just happen
to use slower banks. And the label isn't tied to particular banks either (Covered
share varies only 8.6–13.9% across middle banks, base 11.3%).

<div class="verdict">The proof in one line: 0.99× the sum of its steps, and three
suspects (FX, hidden banks, the Covered label) all walk free — the same corridor
and the same middle bank reduce "Covered slowness" from 3.27× to 1.14×.</div>

## The one pattern behind all six

The move is *regression toward the fair comparison*: whenever a group looks
different (Covered looks slow), don't accept the raw number — re-run the
comparison with everything else held fixed (corridor, then corridor + middle
bank) and watch the gap walk down to nothing. And when a mechanism is absent
(conversions, hidden banks), show it with the flat table: identical medians
across every level of the suspect.

## Words I use

- **step** — one bank-to-bank leg of a route (a 3-bank payment has 2 steps).
- **2-bank payment** — a Direct payment; the laboratory where each step's typical
  delay is measured, because it has exactly one step.
- **corridor** — the sender country → beneficiary country pair (held fixed to
  make comparisons fair).
- **middle bank** — the bank(s) between sender and receiver.
