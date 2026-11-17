# Rule content for the g2 · Currency page.

COLUMNS = """
| column | what it is | how g2 uses it |
| :--- | :--------- | :------------- |
| `CURRENCY_CODE` | the currency label on the payment (GBP, EUR…) | the thing being explained |
| `USD_AMOUNT` | the amount | used for the "round numbers" rule |
| `BIC8_PATH` | the bank route, `;`-separated | first bank = sender, last bank = receiver |
| `ORDERING_BIC8` / `BENEFICIARY_BIC8` | the sender/receiver bank columns | used as a check (they're ~5% wrong — g5 Rule 5) |

That's it. No time, no parties, no anomaly labels — those belong to g1, g7, g8.
"""

RULES = [
    dict(
        name="The currency is decided by the sender",
        quick=(
            "Whose bank you send *from* decides the currency label — the receiving bank's "
            "country matches the label at chance level."
        ),
        analogy=(
            "paying from a German account in euros even though the shop on the other side "
            "would prefer dollars — the wallet you pay from picks the note."
        ),
        tech="""
Each bank's country implies a typical currency (Germany → EUR, US → USD). So ask:
does each side's usual currency match `CURRENCY_CODE`?

| reference | match |
| :-------- | ---: |
| first bank of the path (sender side) | **93.42%** |
| last bank of the path (beneficiary side) | 19.09% — chance for 155 currencies |
| `ORDERING_BIC8` column | 89.45% (lower because that column is ~5% wrong, g5 Rule 5) |

93 vs 19 is the whole proof: the label follows the sender, not the receiver.
""",
    ),
    dict(
        name="Every country has a home currency, and uses it ~92–97% of the time",
        quick=(
            "For each sender country, the most common currency among its payments is that "
            "country's home currency — and almost all of its payments use it. Russia is "
            "the loud exception (72.9%, paying EUR 23% of the time)."
        ),
        analogy=(
            "every shop having a 'local currency' by default — you get the local note "
            "unless something unusual is going on."
        ),
        tech="""
Line payments up by sender country; the modal currency defines the home currency
(recovered exactly for all 228 countries: US→USD, DE→EUR, GT→GTQ …). Home-currency
share, rows-weighted over 182 countries with ≥1,000 rows: median **91.9%**, max
98.3% (MQ), min **72.9% — Russia** (EUR 23.2%; CU 76.1%, SE 81.3%, GT 82.2% follow).

Control that confirms it's a sender-side property, not corridor-driven: payments
*within* one country use the home currency **96.78%** vs **93.15%** for
cross-country payments.
""",
    ),
    dict(
        name="When it's NOT the home currency, it leans to the receiver",
        quick=(
            "The rare foreign payments (~6.6%) mostly become EUR or USD, and they tilt "
            "toward the receiver's home currency — a pull, not a rule."
        ),
        analogy=(
            "a tourist paying in the local currency when the shop accepts it — it happens "
            "far more often than chance, but plenty still pay 'wrong'."
        ),
        tech="""
657,004 foreign rows, composition EUR 56.0%, USD 25.6%, GBP 6.1%, CHF 3.4%. Does
the currency track the beneficiary? Actual match vs the baseline "share of foreign
rows whose beneficiary lives in that currency land":

| foreign currency | n | matches beneficiary home | baseline |
| :--- | ---: | ---: | ---: |
| EUR | 368,002 | 62.1% | 41.8% |
| USD | 168,219 | 54.1% | 21.8% |
| GBP | 40,149 | **62.2%** | **8.5%** |
| CHF | 22,532 | 58.6% | 6.7% |
| CNY | 15,065 | 51.9% | 3.1% |

Every currency beats its own baseline (GBP +54 pp, CHF +52 pp) — the pull is real,
but not deterministic: 42% of foreign rows don't match the beneficiary either.
""",
    ),
    dict(
        name="USD amounts are round; every other currency isn't",
        quick=(
            "Flip the currency label to USD and amounts suddenly become whole numbers "
            "(38.65% vs 0.99% elsewhere) — the label itself switches on a "
            "rounding-to-nice-numbers mode."
        ),
        analogy=(
            "people quote '$3,000', never '$2,981.47' — but only when the sign says USD."
        ),
        tech="""
Share of clean amounts (≥1) that are whole numbers / multiples of 100:
USD **38.65%** / **15.55%**; every other currency **0.99%** / 0.01% (chance).

The country control proves it's the *currency*, not the sender: DE-EUR 0.94% vs
DE-USD **37.5%**; GB-GBP 0.97% vs GB-USD **39.2%**; JP-JPY 0.92% vs JP-USD
**39.2%**; and US senders paying in EUR drop to 0.90%. Holding the country fixed,
switching the currency label to USD turns on the nice-number mode. All amounts in
every currency have exactly 2 decimals.
""",
    ),
    dict(
        name="There is no FX-rate table (the negative rule)",
        quick=(
            "Amounts are drawn directly in USD terms; the currency label is a sticker, "
            "never a conversion."
        ),
        analogy=(
            "price tags repainted shop by shop, not converted from one master price list — "
            "that's why the tag and the label can confidently disagree."
        ),
        tech="""
If real conversion happened, a currency's ratio to USD would be stable and
foreign-currency payments would sit at a shifted level versus home-currency ones,
by exactly the rate. Neither holds: holding the country fixed, the median
log10(`USD_AMOUNT`) delta between foreign- and home-currency payments is
**−0.001 dex** (median |Δ| 0.017) across 63 country×currency cells and 457,972
rows — a real rate table would force ±0.03–1.9 dex. Ukraine pays EUR 4.7% of the
time at median 2.341 log-$ — *identical* to its home-currency median (a
"0.0 dex conversion"). The earlier-looking "implied rates" (USD/INR ≈ 82) were
fake: the amount distribution is a property of the sender country's wealth, and
the currency rides along (see g3's ladder).
""",
    ),
]

PATTERN = (
    "The one pattern behind all five — the same three-step move every time: pick the "
    "column that should cause the effect (sender bank / currency / amount); group all "
    "10M rows by it and count; compare against the baseline that would appear if "
    "nothing were going on (19% = chance mixing, 0.99% = round numbers by chance). If "
    "the real number is far from the chance number, it's a rule; if it's close, it's a "
    "documented dead end. That's how raw columns become 'business rules'."
)

GLOSSARY = """
- **home currency** — the most common currency a sender country uses (a proxy for
  the generator's per-country table).
- **foreign payment** — one whose currency is not the sender country's home currency.
- **beneficiary** — the receiving side of the payment; its bank's country defines
  "the receiver's currency".
- **chance baseline** — the match rate you'd expect from blind mixing; each
  currency's own baseline is its share of foreign-payment destinations.
- **dex** — one power of ten in log space (+1 dex = ×10).
"""
