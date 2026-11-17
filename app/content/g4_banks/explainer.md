## The columns g4 uses

| column | what it is | how g4 uses it |
| :--- | :--------- | :------------- |
| `BIC8_PATH` (every bank id in it) | the `;`-separated route | the raw material: 25.8M appearances of 8,727 banks, taken apart character by character |
| `ORDERING_TYPE` / `BENEFICIARY_TYPE` | B or C on each side | the second dial — does the party type move the amount? |
| `USD_AMOUNT` | the amount | what the dials move |
| `ANOMALY_TYPE` | label or empty | clean rows only |

That's it. Currency choice is g2's finding, route structure is g5's; g4 owns the
banks themselves.

## The rules, and how each is squeezed out

**Rule 1 — A bank id is a fixed 8-slot layout, with zero exceptions.**
Take all 25,815,715 bank appearances apart:

```
 0 3 0 9 | C H | Z | 0
 └─┬──┘   └┬┘   │   │
 4-digit  country│   always '0'
 bank no.  code  house letter
```

- digits 1–4: **1,075 distinct values** across all 8,727 banks — numeric only,
  0 exceptions.
- characters 5–6: 229 country codes (the same codes used everywhere in the file).
- character 7: 25 possible letters, **constant within each country** (0 of 229
  countries vary), reused across countries — so it identifies the *country*, not
  the bank.
- character 8: always `'0'` — padding, not a check digit (a constant can't encode
  anything).

The kicker: 8,727 banks share only 1,075 four-digit prefixes (range 0…1136), so a
bank is really identified by **(prefix, country)** — the numbers are drawn from a
small shared pool, not a global sequence.

**Rule 2 — Business vs retail is its own dial: +0.865 dex (7.3×) at every income
level.** Types are only ever B or C. Hold the country fixed and compare business
senders to retail senders within it (167 countries with ≥300 of each): median
offset **+0.865 dex = 7.3×**, with sd only 0.100 dex across countries. The trick
that proves it's one fixed knob and not "rich businesses": plot each country's
retail median against its business median — the points sit on a **slope-1 line**
displaced by a constant. And the country dial survives with the type removed
(2.889 dex span inside retail, 2.856 inside business). Two independent knobs; they
even stack innocently:

| pair | rows | median amount | vs C→C |
| :--- | ---: | ---: | ---: |
| C→C | 1,512,382 | $464 | 1.0× |
| B→C | 5,600,965 | $3,118 | 6.7× |
| C→B | 609,762 | $3,236 | 7.0× |
| B→B | 2,269,885 | $22,900 | 49.4× |

**Rule 3 — Individual banks add a stable tilt of their own.** Among 2,221
(bank, country) cells: a bank's median deviates from its country's median with
σ = **0.274 dex**, and that deviation correlates **−0.58** with the bank's retail
share (retail-heavy banks pay less). Split-half check: the tilt correlates
**0.93** across independent halves — a real property, not noise; the part left
after client mix, σ ≈ 0.22 dex, is the bank's own character.

**Supporting censuses (facts, not rules).** 8,727 banks over 229 codes; median 12
banks per country but **max 1,016 (US)**; Isle of Man runs 545k rows on just 12
banks. 45 banks are pure intermediaries (never an endpoint); top middle-hop banks:
`0309CHZ0` 492,743 hops, `0004IMD0` 460,652. **24,017** corridors, top = domestic
US→US (395,503). Corridor reciprocity is *not* balanced (median |n_AB−n_BA| share
0.114) — the generator does not balance flows. These describe *how much*; the
two dials above describe *how*.

**Dead ends (checked, no rule).** Char 7 as a bank identity — no: 25 letters for
8,727 banks. Char 8 — constant. Price-tilt caused by route type — no. Pool size
as a pure function of traffic — no: the residual is country-specific (IM 12, FI
33 banks).

<div class="verdict">The proof in one line: a fixed 8-slot layout with 0
exceptions in 25.8M appearances, and a +0.865 dex business premium that sits still across 167
countries — one layout, two dials.</div>

## The one pattern behind all three

The move is *unpack then hold fixed*: first decompose the id into slots (does each
slot vary? where?) and count exceptions — zero exceptions means a rule; then for
the amount question, hold the country fixed to isolate the type dial, and hold the
type fixed to keep the country ladder. Each dial is only believed once the other
is held still.

## Words I use

- **BIC8** — the 8-character bank id (see Rule 1).
- **house letter** — character 7 of the id, one of 25 letters; constant per
  country, meaningless for identifying a bank.
- **dial** — a generator knob that shifts a payment's amount level (log-space),
  independent of other dials.
- **(bank, country) cell** — a bank in one country; several ids can share a prefix.
