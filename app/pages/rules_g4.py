# Rule content for the g4 · Banks & countries page.

COLUMNS = """
| column | what it is | how g4 uses it |
| :--- | :--------- | :------------- |
| `BIC8_PATH` (every bank id in it) | the `;`-separated route | the raw material: 25.8M appearances of 8,727 banks (layout decoded below) |
| `ORDERING_TYPE` / `BENEFICIARY_TYPE` | B or C on each side | the second dial — does the party type move the amount? |
| `USD_AMOUNT` | the amount | what the dials move |
| `ANOMALY_TYPE` | label or empty | clean rows only |

Currency choice is g2's finding, route structure is g5's; g4 owns the banks
themselves.
"""

RULES = [
    dict(
        name="Bank numbers are drawn from a small shared pool — a bank is (prefix, country)",
        quick=(
            "8,727 banks share only 1,075 four-digit numbers, so the number alone doesn't "
            "identify a bank — the pair (prefix, country) does. The values are drawn per "
            "country from a pool, not counted up in a global sequence."
        ),
        analogy=(
            "licence plate numbers: two states can both issue '4402', so the plate is "
            "the number *and* the state together."
        ),
        tech=r"""
Zero exceptions across **25,815,715** appearances of **8,727** banks:

- digits 1–4: **1,075 distinct values** for 8,727 banks (range 0…1136), numeric
  only — the prefix alone is not an identity.
- char 7 (house letter): **25 possible values, constant within each country**
  (0 of 229 countries vary) and reused across countries ('2' in 30 countries,
  M 22, B 20, S 18, P 17) — it identifies the *country*, not the bank.
- char 8: always `'0'` — the field is padded to 8 characters, not a check digit
  (a constant cannot encode anything).
""",
    ),
    dict(
        name="Business vs retail is its own dial: +0.865 dex (7.3×) at every income level",
        quick=(
            "Business payments run ~7.3× retail, with the same boost in rich and poor "
            "countries alike — and it stacks on top of the country dial."
        ),
        analogy=(
            "wholesale versus counter price: the multiplier is the same whether the shop "
            "is in Monaco or Guinea-Bissau."
        ),
        tech="""
Types are only ever B or C (0 A/D rows in all 10M). Holding the **country** fixed
and comparing business senders to retail senders within it (167 countries with
≥300 of each): median offset **+0.865 dex = 7.3×**, sd 0.100, p25–p75 +0.807…+0.917,
min +0.517 (ME) … max +1.179 (XK); 101 of 167 countries inside 0.80–0.95 dex.
Because the effect is additive in log space, each country's retail median plotted
against its business median sits on a **slope-1 line** displaced by a constant —
the offset doesn't grow with wealth. Removing the type effect leaves the country
ladder intact (2.889 dex inside retail, 2.856 inside business — same 2.8–2.9 as
mixed). Both endpoints count and they stack:

| pair | rows | median amount | vs C→C |
| :--- | ---: | ---: | ---: |
| C→C | 1,512,382 | $464 | 1.0× |
| B→C | 5,600,965 | $3,118 | 6.7× |
| C→B | 609,762 | $3,236 | 7.0× |
| B→B | 2,269,885 | $22,900 | 49.4× |
""",
    ),
    dict(
        name="Individual banks add a stable tilt of their own",
        quick=(
            "On top of the country dial and the type dial, each bank has its own "
            "character — retail-heavy banks run smaller, and the tilt is stable across "
            "independent halves of the data."
        ),
        analogy=(
            "branches of the same bank chain in the same town still develop their own "
            "clientele — and that character shows up again next quarter."
        ),
        tech="""
Among 2,221 (bank, country) cells with n≥500, a bank's median deviates from its
country's median with σ = **0.274 dex**; the deviation correlates **−0.584** with
the bank's retail (C) share. Split-half check (`half` column; 2,200 banks with
≥250 rows each): the tilt correlates **0.931** across halves, and every bank in
the top decile of half 0 stays above median in half 1. Client mix explains part
of it (corr 0.62 with the predicted type-cell median); the residual σ ≈ **0.22
dex** is the bank's own property, not noise.
""",
    ),
]

FACTS = r"""
| fact | value |
| :--- | :---- |
| bank census | 8,727 banks over 229 country codes; 25,815,715 visible appearances |
| banks per country | median 12 · max 1,016 (US) · min 1 |
| pool vs traffic | r = 0.94 raw, 0.83 on logs — with country-specific residuals (Isle of Man: 545k rows on 12 banks; Finland: 466k on 33) |
| roles | every bank is an endpoint ≥ once; 45 banks are pure intermediaries; middle share 56.3% |
| top intermediaries | `0309CHZ0` 492,743 hops · `0004IMD0` 460,652 · `0085BEB0` 329,656 |
| corridors | 24,017 sender→beneficiary pairs; top = domestic US→US (395,503) |
| reciprocity | \|n_AB − n_BA\| / (n_AB + n_BA) median 0.114, p90 0.326 — flows are not balanced |
"""

DECODERS = r"""
**The 8-slot BIC8 layout** — a fixed format (0 exceptions in 25,815,715
appearances); the *drawing* of its values is Rule 1:

```
 0 3 0 9 | C H | Z | 0
 └─┬──┘   └┬┘   │   │
 4-digit  country│   always '0'
 bank no.  code  house letter
```

| slot | distinct values | meaning |
| :--- | ---: | :--- |
| digits 1–4 | 1,075 | the shared numeric pool (range 0…1136) |
| chars 5–6 | 229 | country code, used file-wide |
| char 7 | 25 | house letter — constant within a country, identifies the country, not the bank |
| char 8 | 1 | always `'0'` — padding to 8 characters |

- `ORDERING_TYPE` / `BENEFICIARY_TYPE` — B or C; the amount dial is Rule 2, the
  wording-level meaning is decoded in g7.
- chars 5–6 of any bank in the path give that bank's country — the convention
  every group uses for country work.
"""

DEAD_ENDS = """
- **Char 7 as a bank identity** — no: 25 letters for 8,727 banks, constant within
  each country, reused across countries.
- **Char 8 as a check digit** — a constant `'0'` cannot encode anything.
- **Corridor reciprocity balancing** — the generator does not balance A→B against
  B→A (median asymmetry 0.114, p90 0.326).
- **Bank pool size as a pure function of traffic** — r = 0.94 is carried by size,
  but the residual is country-specific (IM 12 banks, FI 33): the pool is a
  per-country draw, not a rule of traffic.
"""

PATTERN = (
    "The common thread: unpack, then hold fixed. First decompose the id "
    "into slots and count exceptions — zero exceptions in 25.8M appearances means a "
    "rule, not a habit. Then, for the amount question, hold the country fixed to "
    "isolate the type dial, and hold the type fixed to keep the country ladder. A dial "
    "is only believed once the other dial is held still."
)

GLOSSARY = """
- **BIC8** — the 8-character bank id (layout in Decoders); its chars 5–6 are the
  country.
- **house letter** — char 7 of the id; constant per country, meaningless for
  identifying a bank.
- **dial** — a generator knob that shifts amount levels in log space,
  independent of other dials.
- **(bank, country) cell** — a bank in one country; several ids can share a
  prefix, so identity = (prefix, country).
- **endpoint** — the first or last bank of the path; **middle bank** — anything
  between them.
"""
