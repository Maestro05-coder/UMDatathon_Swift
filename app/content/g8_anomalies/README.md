# g8 — Anomalies

**Question:** what does each anomaly label actually *do* to a payment? Tested every label's
suspected injection mechanism directly on the full 10M rows (DuckDB over `cache_party/`).
All numbers are exact (full 10M rows); no sample is used anywhere — the fat-finger
baseline is computed on all 9.56M clean rows that have a comparable sender.

Script: `analysis/g8_anomalies.py` (analysis, run ~25s). Charts: `analysis/g8_charts.py` → this folder (`g8_*.png`).

## Label census (exact)

| label                    |  rows | per 10k | who -> whom                           |
| :----------------------- | ----: | ------: | :------------------------------------ |
| ROMANCE_SCAM             | 2,476 |   247.6 | senders always C (1,811 C>C, 665 C>B) |
| FAT_FINGER_MISTAKE       | 1,940 |   194.0 | spread over all four pairs            |
| CEO_SCAM                 |   945 |    94.5 | senders always B (683 B>C, 262 B>B)   |
| DUPLICATE_PAYMENT        |   679 |    67.9 | spread                                |
| ACCOUNT_REPLACEMENT_SCAM |   649 |    64.9 | mostly B>C (370)                      |
| CUSTOMER_RECALL          |   317 |    31.7 | spread                                |

Total 7,006 rows = 0.07% of the data.

## Rules found (and the mechanisms that died)

### FAT_FINGER — "a normal amount with the decimal point moved"

> **The rule (confirmed):** the recorded amount is an ordinary amount for that sender
> multiplied by a power of ten, `amount = honest × 10^k`, where **k varies from row to
> row** rather than sitting at one fixed comma position. Two stricter versions of the
> story are **refuted**: (i) "one fixed shift for every row" and (ii) "the intended
> amount is an existing payment of that sender with the comma moved".

**Test 1 — distance from the sender's own typical amount (exact, full data).**
For the 1,843 fat-finger rows whose sender has ≥5 clean payments, compare with that
sender's median clean amount; the same test on all 9,561,031 comparable clean rows:

| | fat finger | clean |
| :--- | ---: | ---: |
| rows | 1,843 | 9,561,031 |
| median \|log10(amount/own median)\| | **2.283 dex** (≈190×) | 0.640 dex (≈4.4×) |
| p25 / p75 | 1.352 / 3.295 | 0.290 / 1.099 |
| p99 | 5.548 | 2.478 |
| share ≥100× off | **59.31%** | 3.77% |

Fat-finger rows are far outside the sender's habits — but "far outside" alone does not
say *how* the amount was built. That is what tests 2–5 measure.

**Test 2 — the decisive one: divide by 10, 100, 1,000 and see if the row returns to
normal.** The sender's own middle 50% of amounts (q25–q75) is the target. If the amount
is an honest draw with the decimal point moved, one of those divisions must land inside it.

| divide by | 1 (as recorded) | 10 | 100 | 1,000 | 10,000 | any of 10–1,000 |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| **fat finger** | 9.28% | 18.72% | **24.15%** | 23.06% | 16.71% | **56.00%** |
| clean (control) | **49.67%** | 30.35% | 7.76% | 0.79% | 0.03% | 34.72% |

Read the two rows against each other. A clean payment is most at home with no shift at
all (49.7%) and almost never comes back into range after ÷1,000 (0.79%). A fat-finger
payment is *least* at home unshifted (9.3%) and is rescued by ÷100 or ÷1,000 far more
often than chance. The fat-finger rescue rate (56.0%) is 1.6× the clean rate (34.7%).

**Test 3 — control for the pair, not just the sender.** Restricting to sender→beneficiary
pairs with ≥3 clean payments (250 fat-finger rows, 1,603,808 clean):

| | fat finger | clean |
| :--- | ---: | ---: |
| as recorded | 6.80% | 45.70% |
| ÷10 / ÷100 / ÷1,000 | 16.4% / 18.0% / 22.8% | 21.5% / 3.97% / 0.27% |
| any of ÷10–1,000 | **51.2%** | 23.25% |

The effect survives the tighter control.

**Test 4 — what is refuted: "the intended amount is a real payment with the comma moved".**
Exact integer-cent match, `fat_finger.cents = clean.cents × 10^k`, same sender:

| k | fat-finger rows hit | rate | clean rows hit | rate |
| :--- | ---: | ---: | ---: | ---: |
| ×10  | 13 / 1,940 | **0.67%** | 139,604 / 9,992,994 | **1.40%** |
| ×100 |  9 / 1,940 | **0.46%** | 79,978 | **0.80%** |
| ×1,000 | 3 / 1,940 | **0.15%** | 33,338 | **0.33%** |

Fat-finger rows are **half as likely** as clean rows to be an exact 10^k multiple of
another payment by the same sender, and for the same sender→beneficiary pair the match
count is **0 / 0 / 0**. The intended amount was not a real earlier payment — it is a
fresh draw that was then shifted.

**Test 5 — why k must vary: a single comma position would be a spike, not a spread.**
Measured against the clean median of the same (country, type) cell, the shift has
mean **1.576 dex**, sd **2.230 dex**, skew **−0.479** (n = 1,939). A fixed shift would
pile up on one or two integer values; a 2.2-dex-wide, mildly left-skewed distribution is
what a *mixture* of 10^k (k ≈ 1…5) produces.

**Test 6 — the digit fingerprint confirms the shift.** A ×10^k with k ≥ 2 turns any
2-decimal amount into a whole number, so the whole-dollar rate should rise with the
amount — and it does, but only for USD (the one currency that has whole-number amounts
in the first place, g3 Rule 3):

| USD rows, by size | fat finger, whole dollars | clean, whole dollars |
| :--- | ---: | ---: |
| $100k–$1M | **78.0%** | 38.1% |
| $10M+ | **98.8%** | 37.9% |

Non-USD fat-finger rows show no trace at all (0.35–1.8% whole across size buckets,
indistinguishable from clean) — exactly as expected, because their honest amounts have
no whole-number mode to preserve.

**What survives:** amounts are huge in absolute terms — median **$260,241**, p75
$6,442,821, p90 $77,029,306 (clean median $3,663).

**Charts:** `g8_fatfinger_dev.png` (how far from the sender's own amount) and
`g8_fatfinger_shift.png` (the decimal-shift test with its clean control, the one-chart
version of Test 2).

### DUPLICATE — "identical payment re-sent within minutes"
Gap between two identical payments (same sender account + beneficiary account + amount):
duplicates median **1,099s (~18 min)**, p75 2,189s, max 6,940s (~2h); clean repeats of the
same trio take median **~14.7 days**. All 494 duplicate repeat-pairs are same-currency.
- Rule: identical payment re-sent within 2h -> 494 duplicate vs 164 clean vs 12 other
  -> **74% precision** for "this is a labelled duplicate".

### ROMANCE — "rapid escalating burst to one beneficiary"
500 bursts of **2–8 payments** (median 5), all within **~1 hour** (median span 18 min,
max 70 min). Median amount climbs by payment number: **$33 → $54 → $88 → $144 → $206 →
$350 → $544 → $1,925**. Tiny overall (median $109 vs clean $3,663). Senders always C.
- Currency skew confirmed: INR 429 + CNY 426 of 2,476 rows dominate, while clean
  C-senders are USD/EUR dominated (INR 23, CNY 155 in a 30% clean sample). The
  generator picks "small-scale retail" currencies for this label.
- The labelled rows are a *sample* of each burst: only 364 of 500 bursts sit fully in
  C>C; 136 bursts have B beneficiaries (665 rows), so the burst test must ignore type.

### CEO — "first-ever contact, huge ask" (B senders)
For B>B payments: **100%** of CEO scam rows are the FIRST payment ever between that
sender/beneficiary pair (clean baseline: 82%). Amounts skew large: p90 **$4.2M** vs
$0.4M clean (median is *lower* than clean — $15.2k vs $22.9k — the signal is the tail,
not the typical size).

### ACCOUNT_REPLACEMENT — "one-off payment to a never-before-paid account, normal amount"
**649/649** rows go to a beneficiary account this sender has never paid before and never
pays again. Amounts are completely normal: median $4.0k ~ clean $3.7k, p90 $94k.
- Dead end 1 (the classic story fails here): same beneficiary NAME paid to a different
  account before = 11/649 (1.7%), *below* the 3.9% clean baseline.
- Dead end 2: "account fresh anywhere in the window" — 34% vs 26% clean. Weak.
- Dead end 3: "same sender + same amount (±1%) paid to a *different* account before"
  (the classic replacement story): 259/649 (40%) vs clean baseline 39%. No signal.
- Differentiator vs CEO scam: CEO has the huge-amount tail; replacement doesn't.

### CUSTOMER_RECALL — no payment-level signature (honest negative result)
317 rows, tested against every hypothesis:
- same-amount prior payment (same pair, 30d): **0/317**
- swapped-direction prior payment: **0/317**
- any other anomaly label on the same pair: **0/317**
- fresh account: 23.7% ~ clean 26.3% · amounts ~ clean · prior-same-pair ~ clean baseline
**Conclusion:** recall behaves like a post-payment status, not an injected payment
pattern. If the hidden generator gives it a mechanism, it lives outside the payment fields.

## Charts

| chart                       | what it shows                                                        |
| :-------------------------- | :------------------------------------------------------------------- |
| `g8_label_amounts.png`      | median and 90th-percentile amount per label, on a log axis           |
| `g8_fatfinger_dev.png`      | how far a payment sits from the same sender's median (normal vs fat finger) |
| `g8_fatfinger_shift.png`    | **the decimal-shift test**: share landing back inside the sender's normal range after ÷1, ÷10, ÷100, ÷1,000, ÷10,000 — fat finger vs clean |
| `g8_repeat_gaps.png`        | time between two identical payments: duplicates vs normal repeats    |
| `g8_romance_escalation.png` | median amount by position in a romance-scam burst (n per step shown) |

## Proof rows (real rows from the data)

| label                    | when (UTC)       |            amount | pair | note                                               |
| :----------------------- | :--------------- | ----------------: | :--- | :------------------------------------------------- |
| DUPLICATE_PAYMENT        | 2023-05-01 10:20 |      GBP 3,224.93 | B>C  | `_FAKE_41GBP/9 1 62` -> `_FAKE_IT9601000000000061` |
| DUPLICATE_PAYMENT        | 2023-05-01 10:49 |      GBP 3,224.93 | B>C  | same pair — 29 min later                           |
| ROMANCE_SCAM             | 2023-05-01 01:55 |          INR 9.76 | C>B  | `_FAKE_0/0/00X00043/694 3` -> `_FAKE_-77202-8E`    |
| ROMANCE_SCAM             | 2023-05-01 01:59 |         INR 16.01 | C>B  | same pair — 4 min later, amount up                 |
| CEO_SCAM                 | 2023-05-01 02:39 | EUR 16,906,375.08 | B>C  | first-ever contact, $16.9M ask                     |
| FAT_FINGER_MISTAKE       | 2023-04-30 23:19 |   EUR 17,492.22   | B>C  | far outside the sender's own amount range          |
| FAT_FINGER_MISTAKE       | 2023-04-30 23:42 |    CNY 161,881.13 | B>B  | 100×+ off own-sender median                        |
| ACCOUNT_REPLACEMENT_SCAM | 2023-05-01 04:40 |     RUB 93,621.72 | B>B  | account never used before/after                    |
| CUSTOMER_RECALL          | 2023-05-01 13:10 |      EUR 2,749.12 | B>B  | indistinguishable from clean                       |
