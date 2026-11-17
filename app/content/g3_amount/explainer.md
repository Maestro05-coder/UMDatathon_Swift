## The columns g3 uses

| column | what it is | how g3 uses it |
| :--- | :--------- | :------------- |
| `USD_AMOUNT` | the amount, in USD terms | the thing being explained |
| `CURRENCY_CODE` | the currency label | is roundness attached to a currency? (USD vs everyone else) |
| `BIC8_PATH` (first bank) | sender's bank → sender country | the suspected dial behind the amount level |
| `BIC8_PATH` (last bank) | beneficiary's bank | the corridor control: hold who you pay to fixed |
| `CURRENCY_CONVERSION_COUNT` | currency changes along the route | tested — found to matter not at all |
| `ANOMALY_TYPE` | label or empty | clean rows only |
| `half` | a built-in 50/50 split | check: does the ladder reproduce on independent halves? |

That's it. No timestamps, no party text, no labels — g1, g7, g8's business.

## The rules, and how each is squeezed out

**Rule 1 — Amounts are lognormal: one shared shape, a free per-country centre.**
Draw `log10(amount)` for all 10M clean rows: the curve is essentially a perfect
normal (skew −0.085, kurtosis +0.048). Every country shares the *same width*
(sigma 0.97–1.19, median 1.050) — only the **centre** moves: Guinea-Bissau median
**$48**, Ukraine $223, US $7,156, Monaco **$31,219**. A "wealth ladder". The check
that one-shape-plus-offsets is the true structure: expected global variance
1.1168 + 0.1498 = 1.2665 vs observed 1.2587 — explained to within **0.6%**.

**Rule 1b — The centre is a fixed dial, not a side effect.** Four squeezes:
- *Reproducible:* splitting each country's rows into two independent halves, the
  centre correlates **r = 0.9977** (typical drift 0.025 dex; the between-country
  spread is 0.572 dex — 23× bigger). A centre that emerges from noise dies here.
- *Not explained by anything recorded:* traffic, EUR share, cross-border share …
  all eight predictors together reach only **R² = 0.46** (they're confounds: busy
  countries happen to be rich).
- *Not the corridor:* restricting to payments that all land in the US, every
  sender's centre still matches its all-rows value (**r = 0.986**). The dial
  belongs to the sender, not to whom it pays.
- *Not the party mix:* inside business-only senders the ladder still spans
  **3.188 dex**; inside retail-only, 2.889 dex. Removing the B/C effect doesn't
  shrink it — the dials are separate (that's g4's dial).

**Rule 2 — Nothing about the payment itself moves the amount.** Median
log10-amount by visible bank count: 3.563 / 3.564 / 3.565 / 3.566 / 3.566 — flat.
Direct 3.563 vs Indirect 3.557 vs Covered 3.628 — flat. Weekend vs weekday — flat.
The one tempter: 0-conversion payments look +0.18 dex bigger than 1-conversion
ones. Split by corridor and it dissolves — same-country 0-conv 3.746 vs
same-country 2-conv 3.738 (no gap): it was rich neighbours, not conversions.

**Rule 3 — USD amounts come from a nice-number pool.** Whole dollars: USD
**38.65%**, every other currency **0.99%** (= chance). Beyond rounding, USD
integers love {1,2,5}×10^k: **10.7%** of USD whole-dollars vs 0.02% non-USD; the
leading digits of USD integers spike on 1 (35.0% vs Benford's 30.1%) and 5 (14.1%
vs 7.9%) — the {1,2,5} signature. It's stable in time (38.6–38.8% per fortnight)
and, as g2 showed, it's the currency label that switches it on.

**Rule 4 — 2.83% of rows are "storm" rows.** 1,145 (currency, amount, day) cells
hold ≥100 rows *and* that exact amount covers ≥50% of its own rows — 282,771
payments. Structure, shown on one day: a base value EUR 1,159.42 stamped into 727
payments, and **integer multiples** stamped into more (×10: 598 rows, ×5: 433,
×100: 244, ×50: 188 …). Each currency runs its own drifting daily base. Storm rows
are otherwise ordinary people: 332 rows → 324 distinct beneficiaries, normal
type mix, anomaly labels at their normal rate. By currency: EUR 6.76% of its rows,
CHF 3.61%, GBP 3.35%, USD **0.00%** (USD keeps its nice-number pool instead).

**Rule 5 — Amounts follow Benford's law.** Leading digit 1: 31.44% (Benford
30.10%), 2: 16.84% (17.61%), 5: 8.84% (7.92%) — and the leftover bumps are exactly
the USD pool from Rule 3. The world is honest except where the generator says
"make it pretty".

<div class="verdict">The proof in one line: same shape everywhere (sigma 1.05),
level set by a per-country dial that survives every hold-fixed test
(r = 0.9977 halves · r = 0.986 corridor · R² 0.46 predictors), rounded only for
USD (38.65% vs 0.99%), repeated only in storms (×integer of a daily base).</div>

## The one pattern behind all five

For "is X a rule?", g3's move is always *hold something fixed and see what
survives*: hold the two halves fixed → the centre survives; hold the corridor
fixed → the centre survives; hold the corridor fixed on conversions → the effect
dies; hold the country fixed on roundness → the currency wins. Rules that survive
fixed comparisons are real; effects that dissolve under one were composition all
along.

## Words I use

- **dex** — one power of ten in log space (+1 dex = ×10, +0.1 dex ≈ ×1.26).
- **centre (mu)** — the middle of a country's log-amount curve; the "wealth dial".
- **sigma** — the width of that curve; shared by all countries here.
- **storm** — a day where a base amount and its integer multiples flood one
  currency (injected, near-untraceable otherwise).
- **clean row** — no anomaly label.
