## The columns g8 uses

| column | what it is | how g8 uses it |
| :--- | :--------- | :------------- |
| `ANOMALY_TYPE` | the label on 7,006 rows (0.07% of the file) | the thing being explained — one mechanism per label |
| `USD_AMOUNT` | the amount | fat-finger shifts, CEO tails, romance ladders, "normal" replacements |
| `ORDERING_ACCOUNT` / `BENEFICIARY_ACCOUNT` | sender and receiver | defining each sender's *own* normal range; duplicate and recall repeats |
| `EPOCH_SECONDS` | when it happened | "within minutes" mechanics: duplicate gaps, romance bursts |

Everything is compared against the **clean baseline**: the same statistic over
9.56M clean rows with comparable senders. An anomaly is only "found" if it lands
far outside that clean number.

## The label census

| label | rows | per 10k | who → whom |
| :---- | ---: | ---: | :--- |
| ROMANCE_SCAM | 2,476 | 247.6 | senders always C |
| FAT_FINGER_MISTAKE | 1,940 | 194.0 | spread over all pairs |
| CEO_SCAM | 945 | 94.5 | senders always B |
| DUPLICATE_PAYMENT | 679 | 67.9 | spread |
| ACCOUNT_REPLACEMENT_SCAM | 649 | 64.9 | mostly B→C |
| CUSTOMER_RECALL | 317 | 31.7 | spread |

## The rules, and how each is squeezed out

**FAT_FINGER — "a normal amount with the decimal point moved" (confirmed, with
the details corrected).** The recorded amount is the sender's ordinary amount ×
10^k. Three squeezes:

- *It's far from home:* median distance from the sender's own median amount is
  **2.283 dex (~190×)** vs 0.640 dex (~4.4×) for clean rows; 59.31% of fat-finger
  rows are ≥100× off the sender's habits (clean: 3.77%).
- *The decimal-shift test (the decisive one):* divide by 10, 100, 1,000 and ask
  whether the row lands back inside the sender's own middle 50% of amounts.
  Clean rows sit at home unshifted (**49.67%**) and almost never come back after
  ÷1,000 (0.79%). Fat-finger rows are *least* at home unshifted (**9.28%**) and
  are rescued by ÷10–1,000 **56.00%** of the time (clean control 34.72%). The
  rescue exists, and only a decimal-shift mechanism produces it.
- *Two versions are refuted:* (1) "one fixed comma position for all rows" — the
  measured shift is a wide spread (sd 2.23 dex); a fixed k would make a spike.
  (2) "the intended amount was an earlier real payment, comma moved" — exact
  10^k matches to a same-sender payment happen in **0.67%** of fat-finger rows,
  *half the clean baseline* (1.40%), and 0/0/0 on same sender→beneficiary pairs.
  The intended amount is a fresh draw, then shifted. Confirming fingerprint: the
  USD whole-dollar share rises with size (78.0% → 98.8%) because only USD has
  whole-number amounts to begin with.

**DUPLICATE — the same payment re-sent within minutes.** Two identical payments
(same sender, same beneficiary, same amount): labelled duplicates have a median
gap of **1,099s (~18 min)**; the same trio recurs in clean data once every
**~14.7 days**. Bonus usable rule: a repeat-pair within 2 hours flags a duplicate
at **74% precision**. All 494 duplicate repeat-pairs are same-currency.

**ROMANCE — a fast escalating burst.** 500 bursts of 2–8 payments (median 5), all
inside **~1 hour** (median span 18 min), with the amount climbing per payment:
median $33 → $54 → $88 → $144 → $206 → $350 → $544 → $1,925. Senders always
retail (C). The currency choice is narrow too — INR + CNY account for 855 of
2,476 rows while clean C-senders are USD/EUR dominated.

**CEO — first-ever contact, huge ask.** For business senders: **100%** of CEO
scams are the *first* payment ever between that pair (clean baseline 82%). The
signature is in the tail: 90th percentile **$4.2M** vs $0.4M clean — the median
is actually *lower* than clean ($15.2k vs $22.9k).

**ACCOUNT_REPLACEMENT — a normal amount to an account used once and never again.**
649/649 rows go to a beneficiary account this sender never paid before and never
pays after; amounts are ordinary (median $4.0k vs clean $3.7k). The classic
stories all die here: paying the same *name* at a different account before → only
1.7% (below the 3.9% baseline); "prior same-amount payment to a different
account" → 40% vs clean 39% — no signal at all.

**CUSTOMER_RECALL — no payment-level signature (honest negative).** Same-amount
prior payment: 0/317. Swapped-direction prior payment: 0/317. Any other anomaly
on the same pair: 0/317. Fresh account 23.7% ~ clean 26.3%. Recall behaves like a
*post-payment status*, not an injected pattern — if the generator has a mechanism
for it, it lives outside the payment fields.

<div class="verdict">The proof in one line: 56.0% vs 34.7% (decimal rescue),
18 min vs 14.7 days (duplicates), 100% vs 82% first contact (CEO), 649/649
(once-only accounts) — and 0/317 everywhere for recall.</div>

## The one pattern behind all six

Every label gets the same treatment: compute one candidate statistic (gap, rescue
rate, first-contact rate) on the labelled rows **and on the clean rows**, and
hold everything else as fixed as possible (same sender, same pair, same size
band). If the label's number sits far outside the clean number, the mechanism is
real — and its exact shape (decimal shift? burst ladder? fresh account?) pins
the generator down. If it doesn't — as with recall — we say so plainly.

## Words I use

- **clean baseline** — the same measurement over 9.56M clean rows; every label is
  judged against it.
- **sender's own middle 50% (q25–q75)** — the range holding half of that sender's
  ordinary amounts; the "at home" zone for the decimal-shift test.
- **×10^k / shift k** — moving the decimal point k places (×10, ×100, ×1,000…).
- **burst** — a romance-scam sequence of 2–8 escalating payments to one
  beneficiary, all inside about an hour.
- **first-ever contact** — this sender↔beneficiary pair has never transacted
  before in the whole 90-day window.
