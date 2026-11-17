# g4 — Banks & countries

**Question:** what is the bank universe, and — more important — which parts of it
are *generator rules* rather than descriptions of this one sample?

All numbers are exact, from full-data DuckDB over `cache_full/` (all 10,000,000
rows). Script: `analysis/g4_banks.py` (runs ~4 min). Charts: this folder (`g4_*.png`).

The answer splits cleanly in two. Two things are rules (they have "because"
clauses and a mechanism); the censuses below are facts about the draw — true,
exact, and quoted, but they describe *how much* rather than *how*.

---

## A. The rules

**Rule 1 — A bank id is a fixed 8-slot layout, and never anything else.**

```
 0 3 0 9 | C H | Z | 0
 └─┬──┘   └┬┘   │   │
 4-digit  country│   always '0'
 bank no.  code  house letter (per country)
```

Census over all **25,815,715** visible bank appearances, **8,727** distinct banks:

| slot       | distinct values | what it can be                    |
| :--------- | --------------: | :-------------------------------- |
| digits 1–4 |          1,075  | numeric only — **0 exceptions**   |
| chars 5–6  |            229  | the country code used everywhere  |
| char 7     |             25  | one letter, constant per country — **0 of 229 countries vary** |
| char 8     |              1  | always `'0'` — **0 exceptions**   |

*The generator does this because the bank number is drawn per country from a
small shared pool, not from a global sequence:* 8,727 banks share only **1,075**
distinct 4-digit prefixes (range 0…1136), so the prefix alone is not an identity —
a bank is `(prefix, country)`. The house letter is likewise drawn from 25 values and
reused across countries (`'2'` in 30 countries, `M` 22, `B` 20, `S` 18, `P` 17), so
it identifies the country, not the bank. Char 8 being a constant `'0'` means the
field is padded to 8 characters, not a check digit.

Chart: `g4_7_bic8_structure.png`.

**Rule 2 — The business/retail split is a second, independent dial worth
+0.865 dex (7.3×), applied the same way at every income level.**

Types are only ever `B` or `C` (0 `A`/`D` rows in all 10M, anomalous included).
Holding the **country** fixed and measuring the business-sender vs retail-sender
median in each country (167 countries with ≥300 of each):

| statistic | value |
| :-------- | ----: |
| median offset B − C | **+0.865 dex = 7.3×** |
| p25 … p75 | +0.807 … +0.917 |
| min … max | +0.517 (ME) … +1.179 (XK) |
| standard deviation | 0.100 dex |
| countries inside 0.80–0.95 dex | **101 / 167** |

*The generator does this because it is additive in log space:* if you plot each
country's retail median against its business median, the points sit on a line of
slope 1 displaced by a constant (chart `g4_8_bc_offset.png`) — the offset does not
grow with the country's wealth. And the country dial survives after the type effect
is removed: the ladder spans **2.889 dex** within retail senders and **2.856 dex**
within business senders, i.e. the same 2.8–2.9 dex as the mixed ladder. Country and
type are two separate knobs.

Both endpoints count, and they stack:

| pair | rows     | median amount | vs C→C |
| :--- | -------: | ------------: | -----: |
| C→C  | 1,512,382 | $464         |   1.0× |
| B→C  | 5,600,965 | $3,118       |   6.7× |
| C→B  |   609,762 | $3,236       |   7.0× |
| B→B  | 2,269,885 | $22,900      |  49.4× |

**Rule 3 — Individual banks carry their own stable amount tilt on top of both
dials.**

Among 2,221 (bank, country) cells with n≥500, a bank's median deviates from its
country's median with σ = **0.274 dex**. That deviation correlates **−0.584** with
the share of the bank's senders that are retail (C). Split-half check (`half`
column; 2,200 banks with ≥250 rows in each half): the deviation correlates **0.931**
across halves, and every bank in the top decile of half 0 is still above median in
half 1. The client mix explains part of it (corr 0.62 with the predicted type-cell
median); the residual σ ≈ **0.22 dex** is a genuine per-bank property, not noise.

Chart: `g4_6_bank_tilt.png`.

---

## B. Supporting facts (exact censuses — descriptions, not rules)

These are true of this file and are worth quoting, but they have no "because": they
are consequences of how much traffic each country got, not mechanisms.

| fact | value |
| :--- | :---- |
| banks / country codes | 8,727 banks over 229 codes; 25,815,715 appearances |
| banks per country | median 12, max **1,016 (US)**, min 1 |
| pool size vs traffic | Pearson r = 0.94 raw, 0.83 on logs |
| small-pool outliers | Isle of Man: 545k rows on **12** banks; Finland 466k on 33 |
| roles | every bank is an endpoint ≥ once; **45** banks are pure intermediaries (never an endpoint); middle share 56.3% |
| top intermediaries | `0309CHZ0` 492,743 hops, `0004IMD0` 460,652, `0085BEB0` 329,656 |
| dominant bank | median top-bank share of first positions **52.2%**; US most fragmented (4.4% of 979 banks), one-bank countries 100% |
| corridors | **24,017** sender→beneficiary country pairs; top is domestic `US→US` (395,503), then `CH→US` 134,797, `GB→US` 130,410 |
| reciprocity | among 322 pairs with ≥5,000 rows, \|n_AB−n_BA\|/(n_AB+n_BA) median **0.114**, p90 0.326 |

Charts: `g4_1_bank_census.png`, `g4_2_intermediaries.png`, `g4_3_top_corridors.png`,
`g4_4_reciprocity.png`. g5 Rule 7 explains the hub tilt; it is routing behaviour,
not a bank rule.

## C. Dead ends (checked, no rule)

- **char 7 as a unique bank identifier** — no: 25 letters for 8,727 banks, constant
  within each country, reused across countries.
- **char 8** — constant `'0'`; carries nothing (tested as a check digit: a constant
  cannot encode anything).
- **corridor reciprocity** — the generator does not balance A→B against B→A
  (median asymmetry 0.114).
- **bank pool size as a function of traffic alone** — no: r = 0.94 is carried by
  size, but the residual is country-specific (IM 12 banks, FI 33), so the pool is a
  per-country draw, not a rule of traffic.

## D. What each chart shows

One idea per chart, the unit written on each axis, legend below the plot area.

| chart                       | the one question it answers                            | what it shows                                                                                   |
| :-------------------------- | :----------------------------------------------------- | :---------------------------------------------------------------------------------------------- |
| `g4_7_bic8_structure.png`   | How is a bank id built?                                | The 8-slot layout: 1,075 numeric prefixes, 229 country codes, 25 house letters, one constant '0'.|
| `g4_8_bc_offset.png`        | Is the business premium the same everywhere?           | 167 countries on a slope-1 line displaced by +0.86 dex: type is a separate dial from country.    |
| `g4_6_bank_tilt.png`        | Do banks add anything beyond their country?            | Yes: retail-heavy banks pay less (r = −0.58), and the tilts are stable (split-half r = 0.93).     |
| `g4_5_party_types.png`      | Does each business endpoint change the amount?         | Yes — each one multiplies the median by ~7 (B→B $22,900 vs C→C $464).                            |
| `g4_1_bank_census.png`      | How many banks does each country have?                 | Pool size grows with traffic (r = 0.94), but Isle of Man runs 12 banks and Finland 33 for huge traffic. |
| `g4_2_intermediaries.png`   | Which banks carry the most hops?                       | The top 10 middle-hop banks; 45 of 8,727 banks are never an endpoint.                            |
| `g4_3_top_corridors.png`    | Where do payments flow between countries?              | Top 12 country pairs: US→US alone is 395,503 payments of 24,017 pairs.                            |
| `g4_4_reciprocity.png`      | Are A→B and B→A balanced?                              | No: the median pair differs by 11% between directions; balanced flows would pile up at 0.         |

## E. Real rows from the file (proof)

Rule 1 (the layout, and a hidden middle hop inside it):
```
BIC8_PATH: 0004IMD0;0077CHZ0;0086KRS0     USD_AMOUNT: 251.15    ot=B bt=C   Indirect
BIC8_PATH: 0004IMD0;0005CHZ0;0041NOK0;...;0087AEA0   USD_AMOUNT: 151,138.29  ot=B bt=C  Covered
```
Rule 2 (same countries, B vs C changes the scale; the two dials stack):
```
BIC8_PATH: 0004IMD0;0366FRP0   USD_AMOUNT:   2,362.15   ot=B bt=B   Direct
BIC8_PATH: 0007IMD0;0099AU20   USD_AMOUNT: 248,882.70   ot=C bt=C   Direct
```
Rule 3 (a big intermediary hop, retail beneficiary, modest amount):
```
BIC8_PATH: 0309CHZ0;...;0087AEA0   USD_AMOUNT: 5,699.13   ot=C bt=C   Covered
```

## F. Cross-references

- g5 Rule 4/7: bank currencies and the hub-tilt mechanism behind the intermediary table.
- g6 Rule 2: per-bank delays (fixed per bank, sending = receiving).
- g3 Rule 1 + Rule 1b: the country amount dial that Rule 2 here is stacked on top of.
- g2 Rule 1: the bank currency table (`agg/_g2_bank_cur.pkl`).
- g7: ORDERING_TYPE semantics and the account-level view of the same parties.

## G. Limitations

- "Middle share" uses visible hops only; hidden banks (`...`) are unattributable.
- Bank tilts are measured per (bank, country) cell; a bank operating in several
  countries was not cross-checked country by country.
- The 25 house letters have no inferable semantic meaning; only the mapping
  (letter ↔ country) is proven, not its origin.
- Rule 2's offset is a sender-type offset; the 4-cell table shows the beneficiary
  side behaves symmetrically, but the per-country scatter is sender-side only.
