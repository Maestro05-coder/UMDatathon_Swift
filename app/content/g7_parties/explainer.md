## The columns g7 uses

| column | what it is | how g7 uses it |
| :--- | :--------- | :------------- |
| `ORDERING_ACCOUNT` / `BENEFICIARY_ACCOUNT` | the account strings | the subject: who are these parties, and how are accounts built? |
| `ORDERING_DETAILS` / `BENEFICIARY_DETAILS` | the party's profile text (name/address) | read line by line: is the geography real or decoration? |
| `ORDERING_TOKENS` / `BENEFICIARY_TOKENS` | the generator's template of the same text | compared against DETAILS, token family by token family |
| `BIC8_PATH` (first bank) | sender's bank → its country | the ground truth geography that the address is checked against |
| `ORDERING_TYPE` / `BENEFICIARY_TYPE` | B or C | decoded from the text itself (Rule 5) |

That's it. Amounts (g3), clock (g1) and labels (g8) live elsewhere.

## The rules, and how each is squeezed out

**Rule 1 — Every account in the world is a `_FAKE_` placeholder.**
10M/10M rows on both sides — 0 exceptions. **54.4%** of sender accounts are
IBAN-shaped (`_FAKE_` + 2 letters + 2 digits + more digits). For those, the
2-letter prefix matches the account's bank country **100.00% of the time**
(76 distinct prefixes, 5.4M rows checked) — the IBAN is fake, but its *country is
real*. The other 45.6% are random strings (`_FAKE_8254 52.`, `_FAKE_.62313E9`)
with no country meaning. Stronger still: each sender account belongs to **exactly
one bank** (100% of the 391,132 accounts).

**Rule 2 — A small loyal sender pool, an enormous one-off beneficiary pool.**
391,132 distinct sender accounts (avg 25.6 payments each) vs **2,590,877**
beneficiary accounts (avg 3.9). The mass is at the top: **28,889** sender accounts
with ≥50 payments carry **78.6% of all rows**. The biggest "whale"
(`_FAKE_41GBP/9 1 67`) sends 75,803 payments to 38,415 distinct beneficiaries —
and one single payment of about **$1.95B**. Beneficiaries behave like ordinary
people who get paid once.

**Rule 3 — DETAILS is the profile; TOKENS is its template.**
DETAILS reads like a letter: line 1 echoes the account number (94.4% of rows),
then name / street / city / country, wrapped at 35 characters. TOKENS restates
the exact same layout as placeholders — 18 token families:

```
DETAILS: /LU23003500000000669614    SCHROEDER+CHRETIEN 95-40 ...
TOKENS:  /<iban:22> <line_break:35><first_name:9><separator:+> ...
```

DETAILS and TOKENS agree 96.1% of the time on the account shape — one is the
text, the other is the generator's specification of that text.

**Rule 4 (the decoy rule) — The sender's address is real; the beneficiary's is a
random-world decoration.** Does the country written in the address match the
party's bank country?

| side | rows with a country token | match |
| :--- | ---: | ---: |
| sender | 8,453,693 | **100.00%** |
| beneficiary | 8,487,531 | **0.98%** |

The beneficiary address pool is population-weighted *somewhere else*: CN 14.5%,
BR 9.0%, UA 7.2%, ET 5.8% — nothing like the beneficiary *bank* world (US 19.2%,
CH 8.3%, GB 6.6%). Proof row: a GB-bank beneficiary whose address says
Bangladesh. Practical rule: **never use beneficiary address text as geography**
— the bank column carries the truth.

**Rule 5 — B really is business, C really is a person.**
B rows' TOKENS contain business/company wording **87.6%** and person-name wording
**0%**; C rows contain person names **90.7%** and business **0%**. Control:
anomalous rows keep the same templates (B 88.1% business, C 89.1% person) — the
labels from g8 change amounts and accounts, never the letterhead.

**Dead ends (checked, no rule).** The non-IBAN accounts' prefixes — random. An
anomaly-specific text style — none exists. Beneficiary address as a feature —
decoy, Rule 4.

<div class="verdict">The proof in one line: 100.00% vs 0.98% — sender address
tracks its bank perfectly while the beneficiary's address is drawn from a
different world entirely.</div>

## The one pattern behind all five

Same move as everywhere else: start from a suspiciously uniform column (every
account is `_FAKE_`), split it into sub-kinds (IBAN-shaped vs random), and check
each kind against ground truth (bank country). Sub-kinds that match 100% are
rules; strings that fail to match anything are decoration — and decoration
misleading judges is itself a rule (the decoy).

## Words I use

- **DETAILS / TOKENS** — the profile text a party carries, and the machine
  template of that same text (`<city:BD:6>` = "a 6-char city from Bangladesh").
- **IBAN-shaped** — looks like an IBAN: `_FAKE_` + country letters + digits.
  Fake bank account, real country.
- **whale** — one of the few sender accounts with ≥50 payments; together they
  carry 78.6% of all traffic.
- **decoy** — text that *looks* like a feature (beneficiary's address) but is
  a random-world prop.
