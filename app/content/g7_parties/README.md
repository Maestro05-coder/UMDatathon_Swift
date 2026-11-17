# g7 — Parties & text fields (accounts, DETAILS, TOKENS)

**Question:** what are the account strings, how are parties reused, what is inside
the DETAILS/TOKENS text fields, and is any of it real information or decoration?

All numbers are exact, from full-data DuckDB over `cache_party/` (all 10,000,000 rows).
Script: `analysis/g7_parties.py` (analysis, runs ~4 min). Charts: `analysis/g7_charts.py` → this folder (`g7_*.png`).

## The rules we found

**Rule 1 — Every account is a synthetic `_FAKE_...` placeholder.** (10M/10M rows,
both sides — 0 exceptions). Average length 24.2 chars. **54.4%** of ordering accounts
(54.1% beneficiary) are IBAN-shaped: `_FAKE_` + 2 letters + 2 digits + more digits.
For those, the 2-letter country prefix **matches the bank's country 100%** of the
time (76 distinct prefixes, checked on 5.4M rows) — the IBAN is fake but its country
is real. The other 45.6% are random strings (spaces, slashes, letters in random
places — `_FAKE_8254 52.`, `_FAKE_.62313E9`), with no country meaning.
A stricter link: each ordering account belongs to **exactly one bank** (100% of the
391,132 accounts); beneficiary accounts 97.6% (max 8 banks).

**Rule 2 — A small fixed sender pool, a huge one-off beneficiary pool.**
391,132 distinct ordering accounts (average 25.6 rows each, max 75,803) vs
**2,590,877** distinct beneficiary accounts (average 3.9 rows). The heavy tail:
28,889 sender accounts with ≥50 rows carry **78.6% of all rows**. Top "whale" senders:

| account                       | bank      | rows  | distinct beneficiaries | median $ |
| :---------------------------- | :-------- | ----: | ---------------------: | -------: |
| `_FAKE_41GBP/9 1 67`          | 0004IMD0  | 75,803 | 38,415 | 5,750 |
| `_FAKE_41GBP/9 1 62`          | 0004IMD0  | 49,629 | 25,357 | 5,370 |
| `_FAKE_00E69 0N 873`          | 0001MQM0  | 27,737 |  4,687 |   575 |
| `_FAKE_.62313E9`              | 0013JEH0  | 19,947 | 11,774 |   600 |
| `_FAKE_LU35012400000000669820`| 0124LUL0  | 18,812 |  7,648 | 9,330 |

The top whale pays up to **$1.95B** in a single row — a platform-like hub, at the
Isle-of-Man hub bank from g4 Rule 2.

**Rule 3 — DETAILS is the party profile; TOKENS is the generator's template of it.**
DETAILS = line 1 echoing the account number (**94.4%** of rows contain the account's
first 12 chars), then name / street / city / country, wrapped at 35-char lines
(mean line 19.9, max 51), average total length 66 chars. **16.6%** use a numbered
structure (`1/NAME 2/STREET 3/CC/CITY`). TOKENS restates the exact same layout as
`<token:length>` placeholders — 18 token families, e.g.:

```
DETAILS: /LU23003500000000669614    SCHROEDER+CHRETIEN 95-40 FREDI-SCHM ...
TOKENS:  /<iban:22> <line_break:35><first_name:9><separator:+><last_name:8> ...
```
The account shape and the `<iban:>` template agree 96.1% of the time.

**Rule 4 (the decoy rule) — Only the SENDER's address tracks its bank; the
BENEFICIARY's address is decoration.**
Country written in the details (from the `country_code:`/`country_name:` token) vs
the party's bank country:

| side        | rows with a country token | match |
| :---------- | ------------------------: | ----: |
| ORDERING    |               8,453,693   | **100.00%** |
| BENEFICIARY |               8,487,531   | **0.98%** |

The beneficiary address world is a **population-weighted global pool** — top
countries CN 14.5%, BR 9.0%, UA 7.2%, ET 5.8%, IN 4.6%, MX 4.3% — completely
different from the beneficiary bank world (US 19.2%, CH 8.3%, GB 6.6% ...).
Example proof: a GB-bank beneficiary whose address says Bangladesh
(`<post_code:BD:4> <city:BD:6> <country_name:BD:en-gb>`). So: sender geography is
real and consistent; beneficiary address text is a random-world decoy that must not
be used as a feature (the bank column carries the true geography).

**Rule 5 — Type B = business, C = person, confirmed at the text level.**
B rows' TOKENS contain business/company tokens **87.6%** and person-name tokens
**0%**; C rows contain person names **90.7%** and business **0%** (both sides).
Control: anomalous rows use the same mix (B anomalous 88.1% business, C anomalous
89.1% person) — the anomaly labels do not touch the templates (consistent with g8:
labels act on amounts/timing/accounts, not text style).

## Dead ends (checked, no rule)

- **Beneficiary address as geography** — decoy (Rule 4).
- **Account prefix of the 45.6% non-IBAN accounts** — random, no country/bank signal.
- **Anomaly-specific text styles** — none found (Rule 5 control).

## What each chart shows

| chart                     | what it proves                                                                    |
| :------------------------ | :-------------------------------------------------------------------------------- |
| `g7_1_accounts.png`       | Rules 1–2 — most senders pay again, most beneficiaries are one-off; a few big senders carry nearly all payments |
| `g7_2_tokens.png`         | Rule 3 — share of payments containing each of the recurring text blocks in DETAILS |
| `g7_3_country_decoy.png`  | Rule 4 — address countries vs bank countries, and the sender/receiver match rates (100% vs 0.98%) |
| `g7_4_type_semantics.png` | Rule 5 — 100% stacked B/C bars: business vs person wording, normal and anomalous |

## Real rows from the file (proof)

The whale sender (Rule 2, Rule 4 — note the address country IM = its bank's country):
```
ORDERING_ACCOUNT: _FAKE_41GBP/9 1 67      bank: 0004IMD0     75,803 rows
ORDERING_DETAILS: /41GBP/9 1 67
                  1/MASON, COX
                  3/IM/NEW JASMINE
```
An IBAN-shaped retail sender (Rules 1/3):
```
ORDERING_ACCOUNT: _FAKE_LU23003500000000669614   (LU23 == bank 0xxLUxx)
ORDERING_DETAILS: /LU23003500000000669614
                  SCHROEDER+CHRETIEN 95-40 FREDI-SCHM
                  IEDECKE-GASSE KOBLENZ LUXEMBOURG
```
The decoy (Rule 4): beneficiary account `_FAKE_GB30029500000000623158` (GB bank)
with BENEFICIARY_TOKENS `<post_code:BD:4> <city:BD:6> <country_name:BD:en-gb>` —
address says Bangladesh, bank says GB.

## Cross-references

- g4 Rule 6: ORDERING_TYPE/BENEFICIARY_TYPE B vs C and the +0.87 dex amount offset —
  this group proves what the letters mean.
- g8: labels change amounts/accounts but not text templates.
- g1: the sender country clock — the same sender geography that Rule 4 says is real.

## Limitations

- TOKENS→DETAILS reconstruction was verified structurally (same layout, matching
  token families, 96.1% IBAN agreement), not by full round-trip parsing of all rows.
- "Population-weighted" for the beneficiary address pool is a description of the
  observed ranking (CN/BR/UA/ET on top), not a fitted population model.
- The 3.4% of rows whose details lack a country token are mostly the short/truncated
  profiles (only 21.6% of <40-char details carry one).
