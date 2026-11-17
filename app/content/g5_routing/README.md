# Group 5 — Routing (which banks a payment travels through)

All numbers below come from the full 10,000,000-row CSV. No outside data was used.
Script: `analysis/g5_routing.py` (analysis). Charts: `analysis/g5_charts.py` → this folder (`routing_*.png`).

## The rules we found

**Rule 1 — The type matches the number of banks, every single time.** (checked on all 10m rows, 0 exceptions)
- Direct = exactly 2 banks in `BIC8_PATH` (6,323,280 rows, all matched)
- Indirect or Covered = 3 or more banks
- `PARTICIPANT_COUNT` simply counts the banks shown in the path.

**Rule 2 — `...` in the path = `CONTINUITY_QFLAG` "N".** (767,204 rows, 0 exceptions)
The three dots mean "a bank we are not shown". Every row with dots says N; every row without dots says Y.

**Rule 3 — Each hidden bank is a small roll of the dice: about 5% chance per link.**
A route's chance of having `...` fits `1 − (1 − 0.04986)^links`. 2 links → 9.7%, 3 links → 14.2%, and so on. Every route length fits within 0.4 percentage points.

**Rule 4 — `CURRENCY_CONVERSION_COUNT` = number of neighbouring bank pairs that use different currencies.**
We learned each bank's currency from payments with 0 conversions, then predicted the conversion count on a held-out half of the data: **99.91% correct** on both halves (about 4 million rows each).

**Rule 5 — The country columns `ORDERING_BIC8` / `BENEFICIARY_BIC8` are wrong about 5% of the time at each end.**
The first and last bank in `BIC8_PATH` disagree with them in 4.98% / 5.00% of rows, and the two errors are independent. So: **use the path's first and last bank for country work, not those two columns.**

**Rule 6 — Fraud payments are rarely Covered; accidents are not.**
Covered share on normal multi-bank payments: 11.3%. Romance scam: 0.3%. CEO fraud: 2.0%. Account replacement: 1.5%. But fat-finger mistakes (13.2%), duplicates (11.4%), recalls (11.5%) sit right at the normal rate — mistakes look like ordinary payments, fraud looks different.

**Rule 7 — Some countries appear in the middle of routes far more than their traffic explains.**
Middle-hop share ÷ endpoint share: Belgium 1.34, Switzerland 1.30 (solid). Ukraine 1.61, Isle of Man 1.56 (small sample). We tested "it's just currency" — it failed (Belgium is 36% conversion routes vs 32% baseline). Real reason unknown, medium confidence.

## What each chart shows

| chart                              | what it proves                                                               |
| :--------------------------------- | :--------------------------------------------------------------------------- |
| `routing_1_type_vs_pathlen.png`    | Rule 1 — the clean split: 2 banks = Direct, 3+ = Indirect/Covered            |
| `routing_2_gap_per_hop.png`        | Rule 3 — gap chance grows step by step, matching the 5%-per-link curve       |
| `routing_3_conversion_holdout.png` | Rule 4 — predicted vs actual conversion count on data the model never saw    |
| `routing_5_mismatch.png`           | Rule 5 — the two columns disagree with the path ~5% of the time, at each end |
| `routing_7_hub_tilt.png`           | Rule 7 — which countries punch above their weight as middlemen               |

(Older charts `routing_4` and `routing_6` are in `_archive/` — `routing_6` showed Covered looking 3× slower, which group 6 later explained as the banks those routes use, not the label.)

## Real rows from the file (proof of rules 1 and 2)

**Direct, 2 banks, no conversions, QFLAG Y:**
```
BIC8_PATH: 0621US30;0219US30        TRANSACTION_TYPE_CODE: Direct
PARTICIPANT_COUNT: 2   CURRENCY_CONVERSION_COUNT: 0   CONTINUITY_QFLAG: Y
```

**Indirect, 3 banks, 2 conversions (SG→US→DE, two currency changes):**
```
BIC8_PATH: 0203SGS0;0405US30;0037DEF0   TRANSACTION_TYPE_CODE: Indirect
PARTICIPANT_COUNT: 3   CURRENCY_CONVERSION_COUNT: 2   CONTINUITY_QFLAG: Y
```

**Covered, 3 banks, 2 conversions:**
```
BIC8_PATH: 0001RUM0;0143SGS0;0127IT20   TRANSACTION_TYPE_CODE: Covered
PARTICIPANT_COUNT: 3   CURRENCY_CONVERSION_COUNT: 2   CONTINUITY_QFLAG: Y
```

**A route with a hidden bank — and exactly as Rule 2 says, QFLAG is N:**
```
BIC8_PATH: 0044RUM0;...;0068IT20;0010US30   CONTINUITY_QFLAG: N
```

## Things we still don't know
- What decides whether a payment is Covered vs Indirect — no clean rule found yet (same-country corridors go Covered 20.7% vs 10.6% for cross-country, but that's a tendency, not a rule).
- Why Belgium/Switzerland are over-used as middle hops.
