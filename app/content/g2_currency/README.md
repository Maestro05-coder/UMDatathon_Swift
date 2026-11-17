# g2 — Currencies & conversions

  **Question:** which currency does a payment use, is there an FX-rate table behind
  `USD_AMOUNT`, and what (if anything) does the currency label do to the payment?

All numbers are exact, from full-data DuckDB over `cache_full/` (all 10,000,000 rows).
Script: `analysis/g2_currency.py` (runs ~3 min; also caches the recovered tables in
`analysis/agg/_g2_home_cur_all.pkl` and `_g2_bank_cur.pkl` for reuse by g3/g4).
Charts: this folder (`g2_*.png`).

## Census (exact)

- **155 distinct currencies.** EUR 3,198,639 (32.0%) > USD 1,702,991 (17.0%) >
  GBP 873,781 (8.7%) > CHF 803,898 (8.0%) > SGD 367,648 (3.7%). 25 currencies have
  <1,000 rows; 4 have <100 (ER 15, FKP 5, SVC 4 …).
- **228 sender countries** (182 with ≥1,000 rows; country = chars 5–6 of the path's
  first bank, the ~5%-wrong `ORDERING_BIC8` column is NOT used — see g5 Rule 5).

## The rules we found

**Rule 1 — The currency is decided on the SENDER side.**
Compare `CURRENCY_CODE` against each side's modal currency (all 10m rows):

| reference                                | match  |
| :--------------------------------------- | -----: |
| first bank of the path (sender side)     | 93.42% |
| last bank of the path (beneficiary side) | 19.09% |
| `ORDERING_BIC8` column                   | 89.45% |

19% for the beneficiary is roughly what random currency mixing would produce; 93% vs
19% is decisive. The `ORDERING_BIC8` column scores lower than the path's first bank —
consistent with g5 Rule 5 (that column is ~5% wrong on its own).

**Rule 2 — Every country has a home currency; payments use it ~92–97% of the time.**
The recovered home-currency table (modal currency of each sender country) is exact and
saved to `agg/_g2_home_cur_all.pkl` — 228 countries, e.g. US→USD, DE→EUR, GT→GTQ,
SX→ANG, IS→ISK. Home-currency share per country (rows weighted, 182 countries with
n≥1,000): median **91.9%**, max 98.3% (MQ), min **72.9% — Russia**, which pays EUR
23.2% of the time (the strongest deviator; CU 76.1%, SE 81.3%, GT 82.2% follow).
Control that confirms this is a sender-side property, not corridor-driven: payments
*within* one country use the home currency **96.78%** of the time vs 93.15% for
cross-country payments.

**Rule 3 — When a payment is NOT in the sender's home currency (~6.6% of rows),**
it is mostly EUR or USD, and it leans to the beneficiary's currency.
657,004 foreign rows (big countries): EUR **56.0%**, USD **25.6%**, GBP 6.1%,
CHF 3.4%, CNY 2.3%, everything else 6.6%. And the choice tracks the beneficiary:
57.7% of foreign rows use the beneficiary's home currency. Per currency, actual match
vs the baseline "share of foreign rows whose beneficiary lives in that currency land":

| foreign currency | n      | matches beneficiary home | baseline |
| :--------------- | -----: | -----------------------: | -------: |
| EUR              | 368,002 | 62.1%                    |   41.8%  |
| USD              | 168,219 | 54.1%                    |   21.8%  |
| GBP              |  40,149 | 62.2%                    |    8.5%  |
| CHF              |  22,532 | 58.6%                    |    6.7%  |
| CNY              |  15,065 | 51.9%                    |    3.1%  |
| JPY              |   4,770 | 47.5%                    |    1.2%  |

Every currency beats its own baseline (GBP +54 pp, CHF +52 pp) — the pull is real, but
not deterministic (42% of foreign rows don't match the beneficiary either).

**Rule 4 — USD payments get "nice-number" amounts; every other currency doesn't.**
Share of clean amounts (≥1) that are whole numbers / multiples of 100:

| currency | whole-number | ÷100   |
| :------- | -----------: | -----: |
| USD      |      **38.65%** | **15.55%** |
| all non-USD |       0.99% |  0.01% |

The country control proves it is the *currency*, not the sender: DE-EUR 0.94% vs
DE-USD **37.5%**; GB-GBP 0.97% vs GB-USD **39.2%**; JP-JPY 0.92% vs JP-USD **39.2%**;
and US senders paying in EUR drop to 0.90%. Holding the country fixed, switching the
currency label to USD turns on a rounding-to-nice-numbers mode. (The whole-number and
÷100 shares are remarkably stable at 37.5–39.2% / 14.2–16.3% across all five tested
countries.) All amounts in every currency have exactly 2 decimals.

**Rule 5 (dead end) — There is NO FX-rate table converting the currency into`USD_AMOUNT`.**

The naive approach — "median amount per currency ⇒ implied rate" — produces numbers
that look like exchange rates (USD/INR "≈82", CHF/USD "≈1.2"), but they are fake:
the amount distribution is a property of the *sender country's wealth*, and the
currency rides along. The clean test holds the country fixed and compares the median
`log10(USD_AMOUNT)` of its foreign-currency payments to its home-currency payments
(63 country×currency cells, 457,972 rows): deltas are min −0.080, **median −0.001**,
max +0.133 (|Δ| median **0.017** dex). A real rate table would force deltas of
±0.03–1.9 dex (EUR/USD ≈ 0.03, USD/INR ≈ 1.9). Ukraine pays EUR 4.7% of the time at
median 2.341 vs its UAH median 2.341 — a "0.0 dex conversion". So: **the amount is
drawn in USD terms; `CURRENCY_CODE` is a label attached by Rule 1–3, and the only
currency that feeds back into amounts is USD via Rule 4's nice-number rounding.**
The earlier log-shape correlations of 0.93–0.97 across currencies reflect the shared
country-wealth curve, not rates.

## What each chart shows

One idea per chart, the unit written on each axis, and the legend below the plot area
(never on top of the data).

| chart                         | the one question it answers                     | what it shows                                                                                          |
| :---------------------------- | :---------------------------------------------- | :----------------------------------------------------------------------------------------------------- |
| `g2_1_currency_census.png`    | Which currencies are in the file, and how big?  | 15 largest of 155; the top five (EUR, USD, GBP, CHF, SGD) carry 69% of all payments.                   |
| `g2_2_whose_currency.png`     | Whose currency is the label attached to?        | Sender side 93.4% vs beneficiary side 19.1% — the sender decides (Rule 1).                             |
| `g2_3_usd_roundness.png`      | Does the currency itself change the amount?     | Holding the sender country fixed, whole-number amounts jump from ~1% to ~38% only when the currency is USD (Rule 4). |
| `g2_4_beneficiary_pull.png`   | When the sender does pay foreign, whose currency? | Actual match to the beneficiary's home currency (blue) vs what chance alone gives (grey) — every currency beats its baseline (Rule 3). |


## Real rows from the file (proof of Rules 1–4)

Guatemala pays in its home quetzal, even multi-bank (Rule 1/2):
```
BIC8_PATH: 0010GTG0;0202JPJ0        CURRENCY_CODE: GTQ   USD_AMOUNT: 2797.59   conversions: 1
BIC8_PATH: 0010GTG0;0004IMD0;...;0015MCM0;0920US30   CURRENCY_CODE: GTQ   USD_AMOUNT: 452.09   conversions: 3
```
A German sender paying foreign — in USD, with a *nice* amount (Rules 3/4):
```
BIC8_PATH: 0010DEF0;0774US30        CURRENCY_CODE: USD   USD_AMOUNT: 3000.00   conversions: 1
```

## Cross-references

- Which banks have which currency, and why `CURRENCY_CONVERSION_COUNT` = neighbouring
  banks with different currencies (99.91% hold-out accuracy) — g5 Rule 4.
- Why ROMANCE_SCAM rows skew INR/CNY: the generator picks those labels' senders in
  small-scale-retail countries — a sender-country choice, not an FX effect (g8).
- Amount *distributions* themselves (roundness beyond USD, tails, repeats) — g3.

## Limitations
- "Home currency" is the modal currency — a proxy for the generator's intended table;
  for 46 tiny countries (<1,000 rows) it rests on few rows.
- The foreign-currency choice is only partially explained (57.7% beneficiary match);
  the remaining 42% follow the EUR/USD habit but no stronger rule was found.
- Rule 4's mechanism (rounding vs drawing from a nice-number pool) cannot be told
  apart from the data; both produce the same observed shares.
