# Rule content for the g5 · Routing page.

COLUMNS = """
| column | what it is | how g5 uses it |
| :--- | :--------- | :------------- |
| `BIC8_PATH` | the full route of bank ids, `;`-separated; `...` = a bank we're not shown | the subject itself — the rule book of the route |
| `TRANSACTION_TYPE_CODE` | Direct / Indirect / Covered | it is just the bank count — decoded below (Decoders) |
| `PARTICIPANT_COUNT` | number of banks shown in the path | literally counts the path (Decoders) |
| `CONTINUITY_QFLAG` | Y / N flag | matched against the path (Rule 1) |
| `CURRENCY_CONVERSION_COUNT` | number of conversions | predicted from the banks alone (Rule 3) |
| `ORDERING_BIC8` / `BENEFICIARY_BIC8` | stated sender/receiver banks | tested against the path — wrong ~5% of the time (Rule 4) |
| `ANOMALY_TYPE` | label or empty | used in Rule 5: do fraud labels avoid a route type? |

Amounts (g3), timing (g6) and bank identities (g4) live elsewhere.
"""

RULES = [
    dict(
        name="`...` in the path ⇔ QFLAG 'N': two columns, one message",
        quick=(
            "The three dots mean 'a bank we are not shown', and the QFLAG column says "
            "exactly the same thing in letter form."
        ),
        analogy=(
            "a form where one field says 'some pages missing' and another just says "
            "'incomplete' — they'll always agree."
        ),
        tech="""
767,204 rows with dots, **0 exceptions** in either direction: every dotted row
says N, every undotted row says Y. A hidden bank is guaranteed to be flagged.
""",
    ),
    dict(
        name="A hidden bank is a ~5% roll of the dice per link",
        quick=(
            "Each bank-to-bank link flips its own 5% coin for 'hide the next bank'; the "
            "more links, the likelier the route looks dotted."
        ),
        analogy=(
            "posting a letter through five hands, each drop-off having a 5% chance of a "
            "redacted stamp — two hands, ~10%; five hands, ~23%."
        ),
        tech="""
A route of k links hides ≥1 bank with probability 1 − (1 − 0.04986)^k:
2 links → 9.7%, 3 links → 14.2%, and so on — every route length fits within
**0.4 percentage points**. Hiding is uncorrelated with everything else: it is an
independent coin per hop. (Side effect: `...` is a *guaranteed hint* that the
visible route is not the whole route.)
""",
    ),
    dict(
        name="Conversion count = number of neighbouring banks with different currencies",
        quick=(
            "You can predict the conversion column from the route's banks alone, at "
            "99.91% accuracy — the column is fully explained, nothing else feeds it."
        ),
        analogy=(
            "toll booths: count the times the currency changes as you pass each border "
            "along the route — that number is 'conversions', nothing more."
        ),
        tech="""
Learn each bank's currency from payments with 0 conversions, then predict the
conversion count on a held-out half of the data: **99.91% correct** on both
halves (~4M rows each).
""",
    ),
    dict(
        name="The endpoint country columns are ~5% wrong at each end",
        quick=(
            "ORDERING_BIC8 and BENEFICIARY_BIC8 disagree with the actual path ends "
            "about 5% of the time — so trust the path, not the columns."
        ),
        analogy=(
            "the 'from' and 'to' written on the envelope are occasionally mislabelled, "
            "but the postmark route is always honest."
        ),
        tech="""
The path's first bank disagrees with `ORDERING_BIC8` in **4.98%** of rows; the
last bank disagrees with `BENEFICIARY_BIC8` in **5.00%** — and the two errors are
independent. Practical rule every group follows: use the path's first and last
bank for country work; treat the endpoint columns as a noisy copy.
""",
    ),
    dict(
        name="Fraud avoids the Covered route shape; mistakes don't",
        quick=(
            "Scam labels almost never ride a Covered route (0.3–2% vs 11.3% normal), "
            "while mistake labels sit right at the normal rate."
        ),
        analogy=(
            "professional thieves avoid the route with the police escort; clumsy "
            "tourists don't know the difference."
        ),
        tech="""
Covered share on normal multi-bank payments: **11.3%**. Romance scam **0.3%**,
CEO fraud **2.0%**, account replacement **1.5%** — all far below. Fat-finger
**13.2%**, duplicates **11.4%**, recalls **11.5%** — all at the normal rate.
Mistakes look like ordinary payments; fraud looks different.
""",
    ),
    dict(
        name="Belgium and Switzerland punch above their weight as middlemen (open)",
        quick=(
            "Some countries appear in the middle of routes far more than their traffic "
            "explains — the obvious 'it's just currency' check fails."
        ),
        analogy=(
            "a small airport that keeps showing up as everyone's layover — more than its "
            "size predicts, and nobody has caught why yet."
        ),
        tech="""
Middle-hop share ÷ endpoint share: BE **1.34**, CH **1.30** (solid sample); UA
1.61, IM 1.56 (small n). The currency-geography test fails (Belgium's
conversion-route share is 36% vs 32% baseline). Real reason unknown, medium
confidence — an honest open question.
""",
    ),
]

FACTS = """
| fact | value |
| :--- | :---- |
| hidden-bank rows | 767,204 carry `...` — 0 exceptions against QFLAG in either direction |
| hold-out halves | ≈4M rows each; the conversion rule scores 99.91% on both |
| fit quality | every route length fits the 5%-per-link curve within 0.4 percentage points |
"""

DECODERS = """
- **`TRANSACTION_TYPE_CODE` is the bank count, every single time** — Direct =
  exactly 2 banks in `BIC8_PATH` (6,323,280 rows, 0 exceptions); Indirect/Covered
  = 3 or more. The type carries no information beyond the count.
- `PARTICIPANT_COUNT` — literally counts the banks shown in the path.
- `CONTINUITY_QFLAG` — Y = path fully shown; N = contains `...` (Rule 1 makes
  them equivalent).
- **hop / link** — one bank-to-bank leg; a path with n banks has n−1 links.
- **endpoint / middle bank** — first or last bank of the path / anything between.
- **Covered** — one of the type labels; per the decoder above it just means
  "3+ banks".
"""

DEAD_ENDS = """
- **"Same-country corridors are Covered more" is a tendency, not a rule** — 20.7%
  vs 10.6% cross-country; no clean rule separates Covered from Indirect (open).
- **Why Belgium/Switzerland are over-used as middle hops** — the
  currency-geography explanation fails (BE conversion-route share 36% vs 32%
  baseline); real cause unknown, medium confidence (Rule 6).
"""

PATTERN = (
    "The common thread: g5's specialty is *identity* rules. Compare two "
    "columns that should be redundant (dots vs flag) and check all 10M "
    "rows for a single exception — zero exceptions = a rule. The same comparing-habits "
    "move then grades the harder cases: prediction with a hold-out set (99.91%), a "
    "column's own error rate (5%), and whether labels change behaviour — where the "
    "clean baseline (11.3% Covered) is what makes 0.3% meaningful."
)

GLOSSARY = """
- **hop / link** — one bank-to-bank leg of a route; a path with n banks has n−1 links.
- **hidden bank (`...`)** — a bank that exists in the route but is not shown; always
  flagged by `CONTINUITY_QFLAG = N`.
- **endpoint** — the first or last bank of the path (sender's / beneficiary's).
- **middle bank** — any bank between the two endpoints.
- **Covered** — one of the type labels; with the decoder above it just means "3+ banks".
"""
