# Rule content for the g8 · Anomalies page.

COLUMNS = """
| column | what it is | how g8 uses it |
| :--- | :--------- | :------------- |
| `ANOMALY_TYPE` | the label on 7,006 rows (0.07% of the file) | the thing being explained — one mechanism per label |
| `USD_AMOUNT` | the amount | fat-finger shifts, CEO tails, romance ladders, "normal" replacements |
| `ORDERING_ACCOUNT` / `BENEFICIARY_ACCOUNT` | sender and receiver | defining each sender's *own* normal range; duplicate and recall repeats |
| `EPOCH_SECONDS` | when it happened | "within minutes" mechanics: duplicate gaps, romance bursts |

Everything is judged against the **clean baseline**: the same statistic over
9.56M clean rows with comparable senders.

**Label census (exact):**

| label | rows | per 10k | who → whom |
| :---- | ---: | ---: | :--- |
| ROMANCE_SCAM | 2,476 | 247.6 | senders always C |
| FAT_FINGER_MISTAKE | 1,940 | 194.0 | spread over all pairs |
| CEO_SCAM | 945 | 94.5 | senders always B |
| DUPLICATE_PAYMENT | 679 | 67.9 | spread |
| ACCOUNT_REPLACEMENT_SCAM | 649 | 64.9 | mostly B→C |
| CUSTOMER_RECALL | 317 | 31.7 | spread |
"""

RULES = [
    dict(
        name="FAT_FINGER: an honest amount with the decimal point moved — and the shift varies per row",
        quick=(
            "A typo, not a heist: someone's ordinary payment got ×10, ×100 or ×1,000. "
            "Divide back down and it lands inside the sender's normal range far more "
            "often than chance."
        ),
        analogy=(
            "entering '1,159' as '115,900' because one zero was one too many — the "
            "intended payment is still sitting behind the extra zeros."
        ),
        tech="""
**Test 1 — far from home.** Distance from the sender's own median amount:
fat finger median **2.283 dex (~190×)** vs clean 0.640 dex (~4.4×); 59.31% of
fat-finger rows are ≥100× off the sender's habits (clean 3.77%).

**Test 2 — the decisive decimal-shift.** Divide by 10, 100, 1,000 and ask whether
the row lands back inside the sender's own middle 50% of amounts (q25–q75):

| divide by | 1 (as recorded) | 10 | 100 | 1,000 | 10,000 | any of 10–1,000 |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| **fat finger** | 9.28% | 18.72% | **24.15%** | 23.06% | 16.71% | **56.00%** |
| clean (control) | **49.67%** | 30.35% | 7.76% | 0.79% | 0.03% | 34.72% |

Fat-finger rows are *least* at home unshifted and are rescued by ÷10–1,000 far
more often than chance; the rescue only makes sense if the amount was shifted by
a power of ten. It survives an even tighter control (same sender→beneficiary
pairs: 51.2% vs 23.25%).

**Test 3 — what is refuted.** (i) "one fixed comma position": the shift is a wide
mixture (sd 2.230 dex, skew −0.479), not a spike. (ii) "the intended amount is an
earlier real payment with the comma moved": exact 10^k matches to same-sender
payments happen in **0.67%** of fat-finger rows — *half* the clean baseline
(1.40%) — and 0/0/0 for same sender→beneficiary pairs. The intended amount is a
fresh draw, then shifted. Fingerprint check: the USD whole-dollar share rises
with size (78.0% at $100k–$1M, 98.8% at $10M+) — only USD has whole-number
amounts to preserve. Resulting sizes: median **$260,241**, p90 $77.0M.
""",
    ),
    dict(
        name="DUPLICATE: the same payment re-sent within minutes",
        quick=(
            "Someone pressed 'send' twice: an identical payment (same pair, same "
            "amount, same currency) re-appears after about 18 minutes, not weeks."
        ),
        analogy=(
            "the double-click on 'pay now' — the same receipt shows up twice within a "
            "coffee break."
        ),
        tech="""
Gap between two identical payments (same sender account + beneficiary account +
amount): duplicates median **1,099s (~18 min)**, p75 2,189s, max 6,940s (~2h) —
clean repeats of the same trio take median **~14.7 days**. All 494 duplicate
repeat-pairs are same-currency. Usable detector: a repeat-pair within 2 hours
flags a labelled duplicate at **74% precision** (494 vs 164 clean).
""",
    ),
    dict(
        name="ROMANCE: a fast escalating burst to one beneficiary",
        quick=(
            "A string of 2–8 payments within an hour, each asking for a little more "
            "than the last, always from a retail (C) sender."
        ),
        analogy=(
            "'it's just another $50' repeated every ten minutes until it isn't."
        ),
        tech="""
500 bursts of **2–8 payments** (median 5), all within **~1 hour** (median span
18 min, max 70 min). Median amount climbs by payment number: **$33 → $54 → $88 →
$144 → $206 → $350 → $544 → $1,925**. Tiny overall (median $109 vs clean
$3,663). Senders always C. Currency skew confirmed: INR 429 + CNY 426 of 2,476
rows dominate, while clean C-senders are USD/EUR dominated — the generator picks
"small-scale retail" currencies for this label. The labelled rows are a *sample*
of each burst: only 364 of 500 bursts sit fully in C→C, so burst tests must
ignore type.
""",
    ),
    dict(
        name="CEO: first-ever contact, huge ask",
        quick=(
            "The very first payment between two business parties is the scam — and "
            "while the median is normal, the tail reaches millions."
        ),
        analogy=(
            "a stranger emailing the CFO out of the blue with a wire request sized in "
            "the millions."
        ),
        tech="""
For B→B payments: **100%** of CEO scam rows are the FIRST payment ever between
that sender/beneficiary pair (clean baseline 82%). Amounts skew large in the
tail: p90 **$4.2M** vs $0.4M clean — the median is actually *lower* than clean
($15.2k vs $22.9k), so the signal is the tail, not the typical size.
""",
    ),
    dict(
        name="ACCOUNT_REPLACEMENT: a normal amount to an account used once, ever",
        quick=(
            "The amount is completely ordinary; the tell is that the receiving account "
            "had never been paid before and never will be again."
        ),
        analogy=(
            "the invoice is normal, but the bank account it asks you to pay is a ghost "
            "— created once, used once."
        ),
        tech="""
**649/649** rows go to a beneficiary account this sender has never paid before
and never pays after. Amounts normal: median $4.0k ~ clean $3.7k, p90 $94k.
The classic stories die here: paying the same beneficiary NAME at a different
account before = 11/649 (1.7%), *below* the 3.9% clean baseline; "account fresh
anywhere in the window" = 34% vs 26% (weak); "same sender + same amount (±1%)
previously paid to a *different* account" = 40% vs clean 39% — no signal.
Differentiator vs CEO: no huge tail.
""",
    ),
    dict(
        name="CUSTOMER_RECALL: no payment-level signature (honest negative)",
        quick=(
            "Nothing about the payment itself distinguishes recalls — tested against "
            "every hypothesis and matched the clean baseline on all of them."
        ),
        analogy=(
            "the envelope gives nothing away; whatever 'recall' means happened after "
            "the letter left the building."
        ),
        tech="""
317 rows, tested against every hypothesis: same-amount prior payment (same pair,
30d): **0/317**; swapped-direction prior payment: **0/317**; any other anomaly
label on the same pair: **0/317**; fresh account 23.7% ~ clean 26.3%; amounts ~
clean; prior-same-pair ~ clean baseline. Conclusion: recall behaves like a
*post-payment status*, not an injected payment pattern — if the generator gives
it a mechanism, it lives outside the payment fields.
""",
    ),
]

PATTERN = (
    "The one pattern behind all six: compute one candidate statistic per label (gap, "
    "rescue rate, first-contact rate) on the labelled rows AND on the clean rows, "
    "holding everything else as fixed as possible (same sender, same pair, same size "
    "band). If the label's number sits far outside the clean number, the mechanism is "
    "real — and its exact shape (decimal shift? escalation ladder? fresh account?) "
    "pins the generator down. If it doesn't — as with recall — that's the finding, "
    "and it's written down too."
)

GLOSSARY = """
- **clean baseline** — the same measurement over 9.56M clean rows; every label is
  judged against it.
- **sender's own middle 50% (q25–q75)** — the range holding half of that sender's
  ordinary amounts; the "at home" zone for the decimal-shift test.
- **×10^k / shift k** — moving the decimal point k places (×10, ×100, ×1,000…).
- **burst** — a romance-scam sequence of 2–8 escalating payments to one
  beneficiary, all inside about an hour.
- **first-ever contact** — this sender↔beneficiary pair has never transacted
  before in the whole 90-day window.
"""
