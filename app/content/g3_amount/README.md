# g3 — Amounts

**Question:** how are amounts generated — what is the distribution, does anything
about a payment move the amount, why do amounts repeat, and why are some "rounder"
than others? And is the per-country centre a real generator dial or a side effect
of what each country does?

All numbers are exact, from full-data DuckDB over `cache_full/` (all 10,000,000 rows;
clean = `ANOMALY_TYPE IS NULL`). Script: `analysis/g3_amount.py` (runs ~4 min).
Charts: this folder (`g3_*.png`).

## The rules we found

**Rule 1 — Amounts are log-normal with one shared shape, shifted by a per-country
wealth ladder.**
Clean amounts: median $3,678, p75 $19,921, p90 $94,879, p99 $1.27M, min $0.01,
max $1.395B. In log10 space the global distribution is essentially a perfect normal:
mean 3.543, sigma 1.122, **skewness −0.085, kurtosis +0.048** on 10M rows.
Per sender country (158 countries with n≥2,000), the shape never changes — sigma
(interquartile/1.349) is 0.97–1.19, median 1.050 everywhere — only the centre moves:
mu runs from 1.678 (Guinea-Bissau, median **$48**) through 2.35 (Ukraine $223) and
3.85 (US $7,156) to 4.494 (Monaco, median **$31,219**). The full ladder is in
`agg/_g3_country_mu.pkl`. Validation: E[sigma_c²] + var(mu_c) = 1.1168 + 0.1498 =
1.2665 vs the global sigma² 1.2587 — the two-level model (one shape + country
offsets) explains the global variance to within 0.6%.

**Rule 1b — The country centre is a free per-country dial, not a by-product of
size, mix or route.**
(The mechanism sentence: *the generator draws each country's centre once from a
per-country table and then draws every payment from the same log-normal shape
around it, because the centre is reproducible to 0.02 dex across independent halves,
its width never moves, and holding the counterparty corridor fixed leaves the
ladder intact.*)

Four tests, each with the control that would break the rule:

**(a) It is fixed, not sampled.** Splitting every country's rows into the two
disjoint halves in the `half` column (181 countries with ≥500 rows in each half):
corr(centre half 0, centre half 1) = **0.9977**, mean |difference| **0.0247 dex**,
max 0.1740. The spread *between* countries is sd **0.572 dex** — 23× the split-half
noise. A centre that emerged from a country's row sample would not survive this.

**(b) Nothing the file records predicts it.** Correlations with the centre
(158 countries, n≥2,000):

| country attribute | corr with centre |
| :---------------- | ---------------: |
| traffic (log10 rows)        | +0.626 |
| EUR share                   | +0.376 |
| conversion share            | −0.383 |
| cross-border share          | −0.312 |
| mean visible banks          | +0.115 |
| business-beneficiary share  | +0.098 |
| business-sender share       | −0.093 |
| USD share                   | −0.009 |

All eight together in one regression: **R² = 0.460**. The correlations are
cross-country confounds (busy countries are rich, EUR-zone countries are rich,
rich countries trade across borders), not causes — see (c) and (d).

**(c) Hold the corridor fixed and the ladder survives.** Restricting to payments
whose beneficiary bank is in the US (133 countries with ≥500 such rows), each
sender's centre still matches its all-rows centre: **r = +0.986**, and the spread
across countries is **0.567 dex** vs **0.568 dex** on all rows. The centre belongs
to the *sender*, not to whom it pays — so corridor mix cannot create the ladder.

**(d) Party mix is additive, not the driver.** Within business senders alone the
country centre spans **3.188 dex** (197 countries, 1.451 … 4.639); within retail
senders **2.889 dex** (168 countries, 0.885 … 3.774); the full mixed ladder is
**2.817 dex**. Removing the type effect does not shrink the ladder — the B/C offset
(g4 Rule 6, +0.865 dex) shifts every country's level, it does not produce the spread.

**Verdict:** the centre is an exogenous per-country dial. The file cannot say *why*
a country sits where it does (there is no GDP in it, deliberately); it can and does
say that the value is fixed, shape-independent, and not produced by composition,
traffic or routing.

**Rule 2 — Nothing about the payment itself moves the amount.** (honest negatives)
Median log10 amount by: visible bank count 3.563 / 3.564 / 3.565 / 3.566 / 3.566 for
2/3/4/5/6 banks; Direct 3.563 vs Indirect 3.557 vs Covered 3.628; hidden banks 3.564
vs 3.564; weekend 3.563 vs weekday 3.564. All flat.
The one apparent effect — payments with 0 conversions have median 3.72 vs 3.54 for
1 conversion (+0.18 dex) — is **corridor composition, not causation**: split by
corridor, same-country 0-conv rows are 3.746 and same-country 2-conv rows are 3.738
(no gap), while cross-country 0-conv (3.704) vs cross-country 1-conv (3.540) is just
the wealth of same-currency neighbours (EUR-zone/US corridors are rich).

**Rule 3 — USD payments have a whole-number mode; no other currency does.**
Among clean amounts ≥1: USD rows are whole dollars **38.65%** of the time and
multiples of 10/100/1000 at 19.1%/15.6%/11.4%; every other currency sits at
**0.99%**/0.10%/0.01% (i.e., chance). The mode is uniform over the whole window
(38.6–38.8% in every 15-day bucket — it is not a storm event, see Rule 4) and
country-independent (g2 chart: DE-EUR 0.94% vs DE-USD 37.5%). Structure of the USD
integers: 46.4% have ≤2 significant figures (59.2% ≤3), and **10.7% are exactly
{1,2,5}×10^k** (non-USD: 0.02%). Leading digits of USD integers spike on 1 (35.0%
vs Benford 30.1%) and 5 (14.1% vs 7.9%) — the {1,2,5}-pool signature.

**Rule 4 — 2.83% of all rows are "storm" rows: hundreds of unrelated payments share one exact injected amount for a single day.** 

(the detective story of this group)
Census: 1,145 (currency, amount, day) cells hold ≥100 rows AND ≥50% of that amount's
rows — 282,771 rows. Shares by currency: **EUR 6.76%** of its rows, CHF 3.61%,
GBP 3.35%, SGD 1.42%, CNY 0.94%, **USD 0.00%** (USD gets the Rule-3 pool instead).
Structure, proven on 2023-06-09 EUR: a base value (1,159.42) is stamped into 727
payments, and **integer multiples** into more — ×10: 598 rows, ×5: 433, ×100: 244,
×50: 188, ×3: 108, ×2: 105, ×20: 72, ×4: 69, ×30: 60 … down to ×160 (3,135 rows in
that one family). The base drifts day by day within ~1,100–1,220 (EUR), ~1,250–1,320
(CHF), ~1,200–1,325 (GBP) — each currency independently, no fixed cross-currency
ratio. Storm rows are otherwise completely ordinary: 42 sender countries in one
storm, transaction-type mix equals the currency's mix, parties are near-unique
(332 rows → 324 distinct beneficiaries), and anomaly labels appear at their normal
rate (69/282,771 vs 0.07% base rate — actually slightly below).
This mechanism also explains the exotic repeated integers of non-USD currencies:
5,667.00 = 1,133.40×5, 57,971.00 and 115,942.00 = ×50/×100 of 1,159.42 — the
multiples whose cents vanish. It does NOT explain recurring trios: same
(sender, beneficiary, amount) repeats are rare (5,560 rows, max 13 repeats).

**Rule 5 — Amounts follow Benford's law.**
Leading digit of all clean amounts: 1: 31.44% (Benford 30.10%), 2: 16.84% (17.61%),
5: 8.84% (7.92%), 9: 4.38% (4.58%) — the residual deviations are exactly the USD
{1,2,5} pool of Rule 3.

## What each chart shows

One idea per chart, the unit written on each axis, legend below the plot area.

| chart                      | the one question it answers                     | what it shows                                                                                      |
| :------------------------- | :---------------------------------------------- | :------------------------------------------------------------------------------------------------- |
| `g3_1_lognormal.png`       | What shape are amounts drawn from?              | A 100,000-payment sample hugs a normal curve on a log axis (skew −0.08, kurtosis +0.05).            |
| `g3_2_wealth_ladder.png`   | Does the shape change by country?               | No — only the centre moves: $48 median in Guinea-Bissau to $31,219 in Monaco.                        |
| `g3_3_usd_roundness.png`   | Why are some amounts "round"?                   | Only USD piles up on whole / 10 / 100 / 1,000 amounts; every other currency is at chance (~1%).     |
| `g3_4_storms.png`          | Why do exact amounts repeat?                     | One storm day (9 Jun 2023, EUR): a base of 1,159.42 repeated in integer multiples, 3,135 payments.  |
| `g3_5_country_centre.png`  | Is the country centre a real dial or a by-product? | Three panels: the centre repeats across halves (r = 0.9977), its width stays at 1.05 dex, and holding the corridor fixed to the US keeps the ladder (r = 0.986). |


## Real rows from the file (proof)

**Wealth ladder** — Monaco rows cluster near $31k:
```
BIC8_PATH: 0004MCM0;0773US30    USD_AMOUNT: 30041.88   (2023-05-01)
BIC8_PATH: 0018MCM0;0669US30    USD_AMOUNT: 31752.71
```
**A storm** — six unrelated parties pay exactly EUR 5,667.00 on 2023-05-26:
```
BIC8_PATH: 0026FIH0;0003ECE0    5667.00   Direct   conv 1
BIC8_PATH: 0073KRS0;0032BEB0    5667.00   Direct   conv 1
BIC8_PATH: 0506US30;0304DEF0;0035AU20;0182CHZ0    5667.00   Indirect  conv 3
...   637 rows that day+2, 558 different senders, 42 countries
```
**The ×10 sibling on the same storm day (Jun 23):** 1,149.08 (n=1,159) and
11,490.81 (n=1,011) = exactly 10×.

## Cross-references
- g2 Rule 4: the USD nice-number rule = this group's Rule 3 pool.
- g4 Rule 6 / g7 Rule 5: ORDERING_TYPE B (business) vs C (retail) adds a binary
  +0.87 dex offset on top of this group's ladder (B→B $22.9k vs C→C $464 at the
  same country); the ladder here mixes the two types.
- g8: FAT_FINGER rows are extreme *deviations from the sender's own median* — built
  on this group's lognormal baseline; ROMANCE bursts ride the small-amount tail.
- g6: amounts don't interact with duration or conversion count (Rule 2 here agrees).

## Limitations
- The storm census threshold (≥100 rows/day and ≥50% of the value's rows) is
  conservative; smaller families exist, so 2.83% is a lower bound on storm mass.
- Whether the daily base is redrawn per day or evolves continuously can't be
  separated; observed drift is consistent with either.
- "Wealth ladder" is descriptive naming of mu_country — the file contains no
  outside data to attach real-world GDP (deliberately).
