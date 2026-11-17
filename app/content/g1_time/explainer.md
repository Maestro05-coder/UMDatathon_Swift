## The columns g1 uses

| column | what it is | how g1 uses it |
| :--- | :--------- | :------------- |
| `EPOCH_SECONDS` | when the payment happened, in UTC seconds | the thing being explained — its hour of the day |
| `BIC8_PATH` (first bank) | the sender's bank; characters 5–6 of it give the sender's country | which country's clock the payment should follow |
| `ANOMALY_TYPE` | anomaly label or empty | only clean rows are used
| `half` | a built-in 50/50 row split | check: recover every clock twice, independently |

That's it. No currency, no amounts, no party text — those belong to g2, g3 and g7.

## The rules, and how each is squeezed out

**Rule 1 — Every country runs on its own whole-hour clock, cut from one shared template.**
You have a timestamp and a sender country. The trick: plot payments by UTC hour and
countries' curves don't line up at all (correlation **−0.02**, i.e. noise — the raw
file "has no daily rhythm"). But shift each country by *its own* whole-hour offset
and all 113 country curves collapse onto one shared shape: correlation **+0.99**.
The offsets aren't fitted curves — they are **18 distinct integer hours**
(+6 h for 28 countries, +7 h for 15, +1 h for 10 …). One template, 18 clocks.

**Rule 2 — The two busy windows are the same payments, just at different hours.**
The shared template has a main window (5 hours holding **32.9%** of payments) and a
second window (4 hours holding **20.1%**). The story "the second window is a
cut-off batch of different payments" predicts the windows should *differ* in what
they carry. Test, holding the country fixed across 113 countries: median amount
ratio second-vs-main **+0.006 dex (~zero)**, cross-border share **±0.000**,
business-sender share **+0.003**. Only **1 of 113** countries moves its amount by
more than 0.1 dex. Pooled over all rows: median duration 55 s vs 54 s, median
amount $3,875 vs $4,108, cross-border 92.57% vs 92.08%. Same mix, different hour —
a second hump, not a second process.

**Rule 3 — The clock is exact, not fitted.**
Recover every country's offset independently from two disjoint halves of the rows:
**90 of 113** countries get the identical hour, and the other 23 are off by
**exactly one hour** (two adjacent hours of the same flat-topped peak — their
curves still match ≥ 0.86). A fitted or random clock disagrees by fractions and
scatter. Exact ±1-hour ties are the fingerprint of an integer lookup table.

**Rule 4 — Weekends are nearly closed.**
Weekdays each carry 17.05–18.34% of payments; Saturday + Sunday together **11.18%**
vs 28.6% if all days were equal. It's a working-day template.

## We tried to break it, and it held

- "The second window is a batch job" — killed by the 1-of-113 test above.
- "Maybe the clocks are smooth curves" — killed by Rule 3's exactly-one-hour ties.

<div class="verdict">The proof in one line: −0.02 (UTC) → +0.99 (own country
clock) is the whole argument.</div>

## The one pattern behind all four

Take the column that should cause the rhythm (the sender's country), group by it,
and compare two ways of reading time. If the rhythm is real and local, the country
clock must beat the UTC clock by a mile — and the excess must be made of whole
hours, not fitted mush. It is.

## Words I use

- **clock / offset** — how many whole hours a country's working day is shifted from
  the reference country. Not real-world time zones: the +6 h group isn't "the +6
  time zone", it's the value the generator assigned.
- **aligned day** — every country rolled so its own busiest hour becomes hour 0.
  The shape that all 113 countries share after rolling.
- **main / second window** — the two humps of the aligned day: hours 22–02 and
  13–16 from the peak.
