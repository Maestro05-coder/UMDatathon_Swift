# Rule content for the g7 · Parties & text page.

COLUMNS = """
| column | what it is | how g7 uses it |
| :--- | :--------- | :------------- |
| `ORDERING_ACCOUNT` / `BENEFICIARY_ACCOUNT` | the account strings | the subject: who are these parties, and how are accounts built? |
| `ORDERING_DETAILS` / `BENEFICIARY_DETAILS` | the party's profile text (name/address) | read line by line: is the geography real or decoration? |
| `ORDERING_TOKENS` / `BENEFICIARY_TOKENS` | the generator's template of the same text | compared against DETAILS, token family by token family |
| `BIC8_PATH` (first bank) | sender's bank → its country | the ground-truth geography that the address is checked against |
| `ORDERING_TYPE` / `BENEFICIARY_TYPE` | B or C | decoded from the text itself (Decoders) |

Amounts (g3), clock (g1) and labels (g8) live elsewhere.
"""

RULES = [
    dict(
        name="Every account is a `_FAKE_` placeholder — but the IBAN ones carry a real country",
        quick=(
            "No real accounts exist anywhere in 10M rows. When the fake account is "
            "IBAN-shaped, its 2-letter prefix matches the account's bank country 100% "
            "of the time; the rest are random strings."
        ),
        analogy=(
            "theatre costumes: every costume is fake, but the ones with a country flag "
            "sewn on always match the actor's assigned nationality."
        ),
        tech="""
10M/10M rows on both sides — 0 exceptions. Average length 24.2 chars. **54.4%**
of ordering accounts (54.1% beneficiary) are IBAN-shaped (`_FAKE_` + 2 letters +
2 digits + more digits); for those, the letter prefix matches the bank's country
**100.00%** (76 distinct prefixes, 5.4M rows). The other 45.6% are random strings
(`_FAKE_8254 52.`, `_FAKE_.62313E9`) with no country meaning. Stronger still:
each sender account belongs to **exactly one bank** (100% of the 391,132
accounts); beneficiary accounts 97.6% (max 8 banks).
""",
    ),
    dict(
        name="Few loyal senders, millions of one-off beneficiaries",
        quick=(
            "A small pool of 'whale' senders makes payments over and over and carries "
            "most of the traffic; beneficiaries are almost always strangers paying an "
            "account once."
        ),
        analogy=(
            "the difference between a payroll department paying thousands of people "
            "daily, and you wiring rent to a landlord once."
        ),
        tech="""
391,132 distinct ordering accounts (avg 25.6 rows each, max 75,803) vs
**2,590,877** beneficiary accounts (avg 3.9). The heavy tail: 28,889 senders with
≥50 rows carry **78.6% of all rows**. Top whale `_FAKE_41GBP/9 1 67` (bank
`0004IMD0`): 75,803 payments to 38,415 distinct beneficiaries — and one single
payment of about **$1.95B**, a platform-like hub at the Isle-of-Man bank.
""",
    ),
    dict(
        name="DETAILS is the profile; TOKENS is the generator's template of it",
        quick=(
            "One party's text has an exact machine blueprint: every token like "
            "`<city:BD:6>` marks what fills that slot — and the two agree 96% of the "
            "time."
        ),
        analogy=(
            "a form and its field labels: the filled page (DETAILS) and the blank "
            "template (TOKENS) describing the very same document."
        ),
        tech="""
DETAILS: line 1 echoes the account number (94.4% of rows), then name / street /
city / country, wrapped at 35-char lines, avg 66 chars; 16.6% use the numbered
structure (`1/NAME 2/STREET 3/CC/CITY`). TOKENS restates the same layout as
`<token:length>` placeholders across 18 token families. The account shape and
the `<iban:>` template agree **96.1%** of the time.
""",
    ),
    dict(
        name="The decoy rule: sender address is real, beneficiary address is decoration",
        quick=(
            "The sender's written address always matches the sender's bank country "
            "(100%); the beneficiary's address matches only 0.98% — it comes from a "
            "different, random world."
        ),
        analogy=(
            "the parcel is honestly postmarked, but the gift tag was written by a "
            "random-address generator."
        ),
        tech="""
Country written in the details (from the `country_code:`/`country_name:` tokens)
vs the party's bank country:

| side | rows with a country token | match |
| :--- | ---: | ---: |
| ORDERING | 8,453,693 | **100.00%** |
| BENEFICIARY | 8,487,531 | **0.98%** |

The beneficiary address pool is population-weighted *somewhere else*: CN 14.5%,
BR 9.0%, UA 7.2%, ET 5.8% — nothing like the beneficiary *bank* world (US 19.2%,
CH 8.3%, GB 6.6%). Proof row: a GB-bank beneficiary whose address says
Bangladesh (`<post_code:BD:4> <city:BD:6> <country_name:BD:en-gb>`). Practical
consequence: never use beneficiary address text as a geographic feature.
""",
    ),
]

FACTS = """
| account (top whales) | bank | rows | beneficiaries | median $ |
| :--- | :--- | ---: | ---: | ---: |
| `_FAKE_41GBP/9 1 67` | 0004IMD0 | 75,803 | 38,415 | 5,750 |
| `_FAKE_41GBP/9 1 62` | 0004IMD0 | 49,629 | 25,357 | 5,370 |
| `_FAKE_00E69 0N 873` | 0001MQM0 | 27,737 | 4,687 | 575 |
| `_FAKE_.62313E9` | 0013JEH0 | 19,947 | 11,774 | 600 |
| `_FAKE_LU35012400000000669820` | 0124LUL0 | 18,812 | 7,648 | 9,330 |

Pools: 391,132 ordering accounts (avg 25.6 rows) vs 2,590,877 beneficiary
accounts (avg 3.9); 28,889 senders with ≥50 rows carry 78.6% of all rows.
"""

DECODERS = """
- **B = business, C = person, confirmed in the text.** B rows' TOKENS contain
  business/company wording **87.6%** and person names **0%**; C rows contain
  person names **90.7%** and business **0%** (both sides). Anomalous rows keep
  the same templates (B 88.1% business, C 89.1% person) — labels never touch the
  letterhead (consistent with g8).
- **DETAILS / TOKENS** — the party's profile text, and the generator's template
  of it; `<city:BD:6>` = "a 6-char city from Bangladesh".
- **IBAN-shaped** — `_FAKE_` + 2 letters + 2 digits + digits; a fake account
  whose country prefix is real (100.00% match, 76 prefixes, Rule 1).
- account → bank: each ordering account belongs to exactly one bank (100% of
  391,132); beneficiary accounts 97.6% (max 8 banks).
"""

DEAD_ENDS = """
- **Beneficiary address as geography** — decoy: 0.98% match to the bank country;
  the bank column carries the truth (Rule 4).
- **Non-IBAN account prefixes (45.6%)** — random strings; no country or bank
  signal.
- **Anomaly-specific text styles** — none: anomalous rows keep the same B/C
  templates (Decoders above).
- **Short profiles.** 3.4% of rows lack a country token; mostly truncated details
  (only 21.6% of <40-char details carry one) — a coverage note, not a signal.
"""

PATTERN = (
    "The common thread: start from a suspiciously uniform column (every "
    "account is `_FAKE_`), split it into sub-kinds (IBAN-shaped vs random), and check "
    "each kind against ground truth (the bank country). Kinds that match 100% are "
    "rules; strings that fail to match anything are decoration — and decoration that "
    "looks like a feature is itself a rule (the decoy)."
)

GLOSSARY = """
- **DETAILS / TOKENS** — the profile text a party carries, and the machine
  template of that same text (`<city:BD:6>` = "a 6-char city from Bangladesh").
- **IBAN-shaped** — looks like an IBAN: `_FAKE_` + country letters + digits.
  A fake account with a real country.
- **whale** — one of the sender accounts with ≥50 payments; together they carry
  78.6% of all traffic.
- **decoy** — text that *looks* like a feature (the beneficiary's address) but is
  a random-world prop.
"""
