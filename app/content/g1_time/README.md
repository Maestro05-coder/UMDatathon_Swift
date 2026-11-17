# Group 1 — Time (when payments happen)

All numbers come from the full 10,000,000-row CSV.
Script: `analysis/g1_time.py`. Charts: this folder (`g1_*.png`).

## The one-line rule

> **The generator draws the hour of a payment from one fixed, two-humped 24-hour
> template, and gives each country an integer clock offset, because 18 whole-hour
> offsets turn a −0.02 curve correlation into +0.99, and because the two busy
> windows hold payments that are indistinguishable in every other field.**

Everything below is the evidence for that sentence, one clause at a time.

## Rules

**Rule 1 — Each country's clock is a whole-hour offset of one shared template.**
(strongest result in this group)

| clock                                     | avg curve similarity (113 countries) |
| :---------------------------------------- | -----------------------------------: |
| file's own UTC clock                      |   −0.024 — no match, looks like noise |
| shifted by each country's own hour offset |       **+0.990** — near-perfect match |

The offset is not fitted per country as a free curve: it is an **integer hour**.
**18 distinct values** cover all 113 countries — `+6 h` 28 countries, `+7 h` 15,
`+1 h` 10, `+8 h` 9, `+5 h` 9, `0 h` 8, `−11 h` 8, `+12 h` 5, `+2 h` 5, `+11 h` 3,
`+9 h` 3, `−1 h` 2, `+10 h` 2, `−10 h` 2, and one country each at `−9`, `−8`, `−6`,
`−5 h`. `g1_6_offset_table.png` is that table as a chart; it is a generator rule
(an integer lookup from country to clock), not a measurement of time zones.

**Rule 2 — The two busy windows are one template, not two kinds of payment.**

The aligned shape (each country rolled so its busiest hour is hour 0) has a sharp
peak of **7.99%** of payments and a quiet floor of **1.57%** in hours 6–12:

| window              | hours (from own peak) | share of payments | share if every hour were equal |
| :------------------ | :-------------------: | ----------------: | -----------------------------: |
| main window         |       22, 23, 0, 1, 2 |        **32.9%** |                          20.8% |
| dead zone           |          6 … 12       |  1.6% per hour    |                           4.2% |
| second window       |       13, 14, 15, 16  |        **20.1%** |                          16.7% |

The "second window is a cut-off batch" story predicts that the two windows carry
different payments. They do not — holding the country fixed (113 countries with
≥5,000 clean rows each):

| measured per country, second window minus main window | median |      p10 |      p90 |
| :--------------------------------------------------- | -----: | -------: | -------: |
| log10(amount ratio)                                  | +0.0058 |  −0.0319 |  +0.0357 |
| cross-border share                                   | +0.0000 |  −0.0012 |  +0.0013 |
| business-sender share                                | +0.0025 |  −0.0089 |  +0.0179 |

Only **1 of 113** countries shifts its amount by more than 0.1 dex between the
windows. Pooled over all rows the same null appears: median duration 55 s (main)
vs 54 s (second), median amount $3,875 vs $4,108, cross-border 92.57% vs 92.08%.
So the second window is the same payment mix at a different hour: it is a second
hump in the hour distribution, not a second process.

**Rule 3 — The clock is exact, not a fitted curve.**
Recovering each country's offset independently from two disjoint halves of the
rows (`half` column): **90 of 113** countries get the identical hour. The other
23 differ by **exactly one hour** — always two adjacent high hours of the same
flat-topped template — while their 24-hour curves still correlate at ≥0.858
(median 0.991). A fitted/random clock would give fractional or scattered
disagreements; an integer lookup gives exactly ±1 h ties.

**Rule 4 — The template is a working day, and weekends are nearly closed.**
Weekdays each carry 17.05–18.34%; Saturday **4.35%** and Sunday **6.84%** →
weekend **11.18%** of payments, vs 28.6% if all days were equal. The 3 hours
around the peak hold 21.43% of payments; 10 of 24 hours are below half the peak.

## What each chart shows

| chart                    | the one question it answers                       | what it shows                                                                                                                                 |
| :----------------------- | :------------------------------------------------ | :-------------------------------------------------------------------------------------------------------------------------------------------- |
| `g1_1_hours_utc.png`     | What does the raw file look like on one clock?     | Payments by UTC hour are lumpy with several peaks — several countries' working days overlap.                                                  |
| `g1_2_aligned_day.png`   | What happens if each country uses its own clock?   | Lined up by each country's busiest hour, all 113 curves collapse onto one band (10th–90th pct) around one average: same rhythm, different clock. |
| `g1_3_country_peaks.png` | Do countries peak at the same UTC hour?            | No — their busiest hours are spread across all 24 hours of the UTC day.                                                                        |
| `g1_4_weekday.png`       | Does the day of the week matter?                   | Working days carry 17.1–18.3% each; Saturday and Sunday together only 11.2%.                                                                   |
| `g1_5_two_windows.png`   | Is the second window a different kind of payment?  | No. Top: the aligned template with the two windows coloured. Bottom: per-country differences between the windows are all centred on zero.       |
| `g1_6_offset_table.png`  | How many different clocks are there really?        | 18 whole-hour offsets (not 113 free curves); 28 countries share `+6 h`.                                                                         |

## Real rows from the file (proof of Rule 1)

Same rows, converted with each country's own recovered clock:

```
Row:  CURRENCY_CODE: SGD   BIC8_PATH starts 0203SGS0 (Singapore)
      EPOCH_SECONDS: 1684465569  = 03:06 UTC
      Singapore's clock (+8)  -> 11:06 local.  Working hours. ✓
```
```
Row:  CURRENCY_CODE: EUR   BIC8_PATH starts 0001RUM0 (Russia)
      EPOCH_SECONDS: 1690259496  = 07:11 UTC
      Russia's clock (+3)     -> 10:11 local.  Working hours. ✓
```
```
Row:  CURRENCY_CODE: USD   ORDERING_BIC8: 0621US30 (US)
      EPOCH_SECONDS: 1685363344  = Monday, 12:29 UTC — a weekday. ✓
```

Each payment was made during *its own country's* working day, not on one shared clock.

## What we can't test (and why)
The brief's example "richer countries pay more at 3–5pm" needs GDP numbers, which
are not in the file, and we're strictly using the file. What the file *can* prove —
and does — is that the daily rhythm is local, not global, and that the local rhythm
is one template with an integer offset.

## Limitations
- Offsets are only whole hours, so half-hour zones (like India, +5:30) land 30 minutes off.
- Offsets are relative to the busiest country, not named as UTC offsets — no outside
  data needed, but we can't say "the peak is 15:00 local time" in absolute terms.
- The busiest country (US) mixes several of its own time zones, so its curve is
  smeared; single-zone countries show the two-window template more sharply.
- The template's two humps are *described* (hours 22–02 and 13–16 after the peak),
  not explained: the file contains no field that says why a payment lands in one
  hump rather than the other — which is itself the finding of Rule 2.
