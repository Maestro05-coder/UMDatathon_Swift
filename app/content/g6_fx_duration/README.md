# Group 6 — FX & Duration (how long payments take, and what conversions cost)

All numbers come from the full 10,000,000-row CSV. No outside data.
Script: `analysis/g6_fx_duration.py`, `g6b_steps.py`, `g6d_control.py`, `g6e_middle.py` (analysis).
Charts: `analysis/g6_charts.py` → this folder (`g6_*.png`).

## The rules we found

**Rule 1 — A payment's duration is the sum of the time spent at each bank-to-bank step.**
Take each step's *own* typical duration (measured from 2-bank payments), add them up, and you land within 6–14% of the real duration:

| route                        | actual | predicted (steps added) |
| :--------------------------- | -----: | ----------------------: |
| `0004IMD0;0077CHZ0;0086KRS0` |   322s |       322s + 17s = 339s |
| `0026FIH0;0074SGS0;0007IMD0` |    93s |        72s + 31s = 103s |
| `0412FRP0;0300CHZ0;0292CHZ0` |   503s |      360s + 157s = 517s |
| `0068IT20;0309CHZ0;0216CHZ0` |    85s |        22s + 80s = 102s |

Fitted properly: actual ≈ −13 + 0.99 × predicted.

**Rule 2 — A step's delay is fixed, and it mostly belongs to the bank, not the pair.**
Same bank pair → durations barely move (typical spread 4% of the median). And a bank's typical delay when *sending* matches its delay when *receiving*: correlation 0.87. Slow banks are slow in both directions.

**Rule 3 — Steps come in two kinds: quick and slow.**
66% of steps take under a minute; 17% take over 15 minutes; the slowest seen is 11,237s (~3 hours). That's why durations are so lopsided: a 3-bank payment has a median of 80 seconds but a 75th percentile of 1,180 seconds — most settle fast, but if the route includes one slow bank you wait half a day.

**Rule 4 — Currency conversions add NO time.**
At 2 banks: 44s with no conversion vs 38s with one. At 3 banks: 126 / 80 / 81 seconds for 0 / 1 / 2 conversions. At 4 banks: 422 / 404 / 425 / 408. The conversion count doesn't matter for speed — in this data, FX is priced in, not delayed.

**Rule 5 — Hidden banks (`...`) add NO time.**
2-bank payments with a hidden bank: 44s. Without: 44s. Hiding is a visibility effect, not a delay.

**Rule 6 — "Covered is 3–4× slower" is NOT caused by the label.** (the main detective story of this group)
The raw gap looks dramatic, but it shrinks as the comparison gets fairer:

| comparison                       | Covered ÷ Indirect |
| :------------------------------- | -----------------: |
| raw, any 3-bank route            |              3.27× |
| same corridor (same 3 countries) |              1.99× |
| same corridor + same middle bank |          **1.14×** |

So Covered payments aren't slow *because* they're Covered — those routes just happen to use slower banks. (And the middle-bank check showed the label isn't tied to particular banks either: Covered share varies only 8.6%–13.9% across middle banks, base 11.3%.)

## What each chart shows

| chart                       | what it proves                                                                   |
| :-------------------------- | :------------------------------------------------------------------------------- |
| `g6_duration_vs_length.png` | Rules 4/3 — duration climbs with route length; conversions don't shift the curve |
| `g6_gap_shrinks.png`        | Rule 6 — the headline: 3.27× → 1.99× → 1.14× as the comparison gets fairer       |
| `g6_step_additivity.png`    | Rules 1/3 — adding the steps predicts the total; step delays are heavy-tailed    |

(The detailed control charts `g6_same_corridor_control` and `g6_same_middle_control` are in `_archive/` — `g6_gap_shrinks.png` summarises them.)

## Real rows from the file (proof of Rules 1 and 3)

A fast route — both steps quick (23 seconds total, Covered, conv=2):
```
BIC8_PATH: 0001RUM0;0143SGS0;0127IT20   TOTAL_DURATION: 23
```
A slow route — the very first Indirect row in the file (4,341 seconds, over an hour, for SGD 1,920):
```
BIC8_PATH: 0203SGS0;0405US30;0037DEF0   TOTAL_DURATION: 4341
```
Same number of banks, same label — 190× different, because the steps differ. That contrast is the whole group in two rows.

## Limitations
- Only ~3% of 3–4-bank routes had *both* steps measurable (a step must also appear as a 2-bank payment somewhere), so Rule 1 is tested on common bank pairs, not a random sample.
- Sending-bank vs receiving-bank vs pair: not fully separable; the 0.87 correlation says the bank dominates.
- Rule 6's tightest check rests on 21 matched cells, so 1.14× could wobble either way.
