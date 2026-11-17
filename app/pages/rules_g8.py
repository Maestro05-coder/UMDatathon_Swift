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
"""

RULES = [
    dict(
        name="FAT_FINGER: an honest amount with the decimal point moved — and the shift varies per row",
        quick=(
            "The recorded amount is the sender's ordinary amount multiplied by a power "
            "of ten; dividing it back down lands inside the sender's normal range far "
            "more often than chance would allow."
        ),
        analogy=(
            "entering '1,159' as '115,900' because one zero was one too many — the "
            "intended payment is still sitting behind the extra zeros."
        ),
        tech="""
**Test 1 — far from home.** Distance from the sender's own median amount
(1,843 fat-finger rows whose sender has ≥5 clean payments; clean control on all
9,561,031 comparable rows): fat finger median **2.283 dex (~190×)** vs clean
0.640 dex (~4.4×); p25/p75 1.352/3.295 vs 0.290/1.099; 59.31% of fat-finger rows
are ≥100× off the sender's habits (clean 3.77%).

**Test 2 — the decisive decimal-shift.** Divide by 10, 100, 1,000 and ask whether
the row lands back inside the sender's own middle 50% of amounts (q25–q75):

| divide by | 1 (as recorded) | 10 | 100 | 1,000 | 10,000 | any of 10–1,000 |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| **fat finger** | 9.28% | 18.72% | **24.15%** | 23.06% | 16.71% | **56.00%** |
| clean (control) | **49.67%** | 30.35% | 7.76% | 0.79% | 0.03% | 34.72% |

Fat-finger rows are *least* at home unshifted and are rescued by ÷10–1,000 far
more often than chance; the rescue only makes sense if the amount was shifted by
a power of ten. It survives a tighter control (same sender→beneficiary pairs,
≥3 clean payments: 250 fat-finger rows vs 1,603,808 clean — rescue 51.2% vs
23.25%).

**Confirming fingerprint.** A ×10^k with k ≥ 2 turns any 2-decimal amount into a
whole number, so the whole-dollar rate should rise with size — and it does, only
for USD (the one currency with whole-number amounts, g3): USD fat finger 78.0%
($100k–$1M) and 98.8% ($10M+) vs clean ~38%; non-USD fat-finger rows show no
trace (0.35–1.8%, indistinguishable from clean). Resulting sizes: median
**$260,241**, p75 $6,442,821, p90 $77,029,306 (clean median $3,663).
""",
    ),
    dict(
        name="Every other label is a distinct mechanism",
        quick=(
            "Duplicates resend within minutes, romance escalates within an hour, CEO "
            "strikes on first contact with a huge tail, replacement pays a normal "
            "amount to a one-off account — four fingerprints, none overlapping."
        ),
        analogy=(
            "four different crimes, four different signatures: the double-clicked "
            "'pay now', the grooming ladder, the cold-call wire, the ghost account."
        ),
        tech="""
| label | mechanism | exact signature |
| :---- | :-------- | :-------------- |
| DUPLICATE | same payment re-sent within minutes | median gap **1,099s (~18 min)**, p75 2,189s, max 6,940s — vs **~14.7 days** for clean repeats of the same trio; all 494 repeat-pairs same-currency; a repeat-pair within 2h flags a labelled duplicate at **74% precision** (494 vs 164 clean vs 12 other) |
| ROMANCE | 2–8 escalating payments to one beneficiary inside ~1 hour | median span 18 min (max 70 min); amount climbs **$33 → $54 → $88 → $144 → $206 → $350 → $544 → $1,925**; median $109 vs clean $3,663; senders always C (1,811 C→C, 665 C→B); INR 429 + CNY 426 of 2,476 rows — the generator picks small-scale-retail currencies |
| CEO | first-ever contact, huge tail (B senders) | **100%** are the first payment ever between the pair (clean baseline 82%); p90 **$4.2M** vs $0.4M clean; median *lower* than clean ($15.2k vs $22.9k) — the signal is the tail |
| ACCOUNT_REPLACEMENT | normal amount to a never-before-paid account | **649/649** go to an account the sender never paid before and never pays after; median $4.0k ~ clean $3.7k, p90 $94k; differentiator vs CEO: no tail |

Sampling note: the labelled rows are a *sample* of each romance burst — only 364
of 500 bursts sit fully in C→C (136 bursts have B beneficiaries, 665 rows), so
burst tests must ignore type.
""",
    ),
    dict(
        name="CUSTOMER_RECALL: no payment-level signature (the honest negative)",
        quick=(
            "Nothing in the payment distinguishes a recall from a clean row — every "
            "hypothesis was tested and matched the clean baseline."
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

FACTS = """
**Label census (exact, all 10M rows):**

| label | rows | per 10k | who → whom |
| :---- | ---: | ---: | :--- |
| ROMANCE_SCAM | 2,476 | 247.6 | senders always C (1,811 C>C, 665 C>B) |
| FAT_FINGER_MISTAKE | 1,940 | 194.0 | spread over all four pairs |
| CEO_SCAM | 945 | 94.5 | senders always B (683 B>C, 262 B>B) |
| DUPLICATE_PAYMENT | 679 | 67.9 | spread |
| ACCOUNT_REPLACEMENT_SCAM | 649 | 64.9 | mostly B→C (370) |
| CUSTOMER_RECALL | 317 | 31.7 | spread |

Total 7,006 rows = **0.07%** of the file.
"""

DECODERS = """
- **clean baseline** — the same measurement over 9.56M clean rows with comparable
  senders; every label is judged against it.
- **sender's own middle 50% (q25–q75)** — the range holding half of that sender's
  ordinary amounts; the "at home" zone for the decimal-shift test.
- **×10^k / shift k** — moving the decimal point k places (×10, ×100, ×1,000…).
- **burst** — a romance sequence of 2–8 escalating payments to one beneficiary,
  all inside about an hour.
- **first-ever contact** — the sender↔beneficiary pair has never transacted
  before in the whole 90-day window.
"""

DEAD_ENDS = """
- **"The intended amount was a real earlier payment with the comma moved"**
  (fat finger) — exact integer-cent 10^k matches to same-sender payments: 13/1,940
  (**0.67%**) vs 139,604/9,992,994 (**1.40%**) clean for ×10; 0.46% vs 0.80% for
  ×100; 0.15% vs 0.33% for ×1,000; and **0/0/0** for the same sender→beneficiary
  pair. The intended amount is a fresh draw, then shifted.
- **"One fixed comma position for all fat-finger rows"** — refuted: against the
  clean median of the same (country, type) cell the shift is a wide mixture
  (mean 1.576 dex, sd 2.230, skew −0.479, n = 1,939), not a spike.
- **The classic replacement stories** — same beneficiary NAME paid at a different
  account before: 11/649 (1.7%), *below* the 3.9% clean baseline; "account fresh
  anywhere in the window": 34% vs 26% clean (weak); "same sender + same amount
  (±1%) previously paid to a *different* account": 259/649 (40%) vs clean 39% —
  no signal.
- **Recall mechanisms** — all null: 0/317 on every prior-payment pattern; fresh
  account 23.7% ~ clean 26.3% (Rule 3 keeps the conclusion).
"""

PATTERN = (
    "The common thread: compute one candidate statistic per label (gap, "
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
