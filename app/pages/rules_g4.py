# Rule content for the g4 · Banks & countries page.

COLUMNS = """
| column | what it is | how g4 uses it |
| :--- | :--------- | :------------- |
| `BIC8_PATH` (every bank id in it) | the `;`-separated route | the raw material: 25.8M appearances of 8,727 banks, taken apart character by character |
| `ORDERING_TYPE` / `BENEFICIARY_TYPE` | B or C on each side | the second dial — does the party type move the amount? |
| `USD_AMOUNT` | the amount | what the dials move |
| `ANOMALY_TYPE` | label or empty | clean rows only |

Currency choice is g2's finding, route structure is g5's; g4 owns the banks
themselves.
"""

RULES = [
    dict(
        name="A bank id is a fixed 8-slot layout — zero exceptions",
        quick=(
            "Bank ids aren't random codes: every one of the 25.8M appearances is built "
            "as 4 shared digits + country code + one house letter + a fixed '0'."
        ),
        analogy=(
            "licence plates: the format is fixed by law, the numbers come from a small "
            "shared pool per region, and the letter says which region you're from."
        ),
        tech="""
```
 0 3 0 9 | C H | Z | 0
 └─┬──┘   └┬┘   │   │
 4-digit  country│   always '0'
 bank no.  code  house letter
```

Census over **25,815,715** appearances of **8,727** distinct banks:

| slot | distinct values | what it can be |
| :--- | ---: | :--- |
| digits 1–4 | 1,075 | numeric only — **0 exceptions** |
| chars 5–6 | 229 | country codes, used everywhere in the file |
| char 7 | 25 | one letter, constant per country — 0 of 229 countries vary |
| char 8 | 1 | always `'0'` — a constant can't be a check digit |

The kicker: 8,727 banks share only 1,075 four-digit prefixes (range 0…1136), so
the bank number is drawn per country from a small shared pool, not a global
sequence — a bank is really **(prefix, country)**. The house letter ('2' in 30
countries, M 22, B 20, S 18, P 17) identifies the country, not the bank.
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
≥300 of each): median offset **+0.865 dex = 7.3×**, sd 0.100, p25–p75 +0.807…+0.917.
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
    dict(
        name="The rest is census, not rule — and here's what died",
        quick=(
            "How many banks, corridors and intermediaries exist is a fact about this "
            "draw, not a mechanism — and three tempting stories died on inspection."
        ),
        analogy=(
            "a phone book tells you how many plumbers a town has — not why; and some "
            "obvious 'plumber patterns' turn out to be coincidence."
        ),
        tech=r"""
**Exact censuses (descriptions, not rules):**

| fact | value |
| :--- | :---- |
| banks / country codes | 8,727 banks over 229 codes; 25,815,715 appearances |
| banks per country | median 12, max **1,016 (US)**, min 1 |
| pool size vs traffic | r = 0.94 raw — but country-specific residuals (IM: 12 banks, FI: 33) |
| roles | 45 banks are pure intermediaries (never an endpoint); middle share 56.3% |
| top intermediaries | `0309CHZ0` 492,743 hops; `0004IMD0` 460,652; `0085BEB0` 329,656 |
| corridors | **24,017** sender→beneficiary pairs; top = domestic US→US (395,503) |
| reciprocity | \|n_AB − n_BA\| / (n_AB + n_BA) median **0.114** — flows are *not* balanced |

**Dead ends (checked, no rule):** char 7 as a bank identity (25 letters for 8,727
banks); char 8 (constant `'0'`); corridor reciprocity balancing; bank pool size as
a pure function of traffic.
""",
    ),
]

PATTERN = (
    "The one pattern behind all of it: unpack, then hold fixed. First decompose the id "
    "into slots and count exceptions — zero exceptions in 25.8M appearances means a "
    "rule, not a habit. Then, for the amount question, hold the country fixed to "
    "isolate the type dial, and hold the type fixed to keep the country ladder. A dial "
    "is only believed once the other dial is held still."
)

GLOSSARY = """
- **BIC8** — the 8-character bank id (see Rule 1); its chars 5–6 are the country.
- **house letter** — char 7 of the id; constant per country, meaningless for
  identifying a bank.
- **dial** — a generator knob that shifts amount levels in log space,
  independent of other dials.
- **(bank, country) cell** — a bank in one country; several ids can share a
  prefix, so identity = (prefix, country).
- **endpoint** — the first or last bank of the path; **middle bank** — anything
  between them.
"""
