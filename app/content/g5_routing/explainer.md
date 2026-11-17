## The columns g5 uses

| column | what it is | how g5 uses it |
| :--- | :--------- | :------------- |
| `BIC8_PATH` | the full route of bank ids, `;`-separated; `...` = a bank we're not shown | the subject itself — the rule book of the route |
| `TRANSACTION_TYPE_CODE` | Direct / Indirect / Covered | what does the type actually mean? (Rule 1) |
| `PARTICIPANT_COUNT` | number of banks shown in the path | checked — it literally counts the path |
| `CONTINUITY_QFLAG` | Y / N flag | matched against the path, char by char (Rule 2) |
| `CURRENCY_CONVERSION_COUNT` | number of conversions | can we predict it from the banks alone? (Rule 4) |
| `ORDERING_BIC8` / `BENEFICIARY_BIC8` | stated sender/receiver banks | tested against the path — found wrong ~5% of the time (Rule 5) |
| `ANOMALY_TYPE` | label or empty | used in Rule 6: do fraud labels avoid a route type? |

That's it. Amounts (g3), timing (g6) and bank identities (g4) live elsewhere.

## The rules, and how each is squeezed out

**Rule 1 — The type is just the bank count, every single time.**
Direct = exactly 2 banks in the path — 6,323,280 rows, **0 exceptions**.
Indirect/Covered = 3 or more banks. `PARTICIPANT_COUNT` simply counts the banks
shown. The scary-sounding "type" column has no independent information.

**Rule 2 — `...` ⇔ QFLAG "N", with 0 exceptions on 767,204 rows.**
The three dots mean "a bank we are not shown" — a hidden bank. Every dotted row
says N; every undotted row says Y. Two columns, one message.

**Rule 3 — A hidden bank is a ~5% roll of the dice per link.**
A route of k links hides ≥1 bank with probability `1 − (1 − 0.04986)^k`:
2 links → 9.7%, 3 links → 14.2%, and so on — every route length fits within
**0.4 percentage points**. Hiding isn't correlated with anything else; it's an
independent coin per hop. (Useful side effect: `...` is a *guaranteed hint* that
the visible route is not the whole route.)

**Rule 4 — Conversion count = number of neighbouring banks with different
currencies.** Learn each bank's currency from payments with 0 conversions, then
predict the conversion count on a held-out half of the data: **99.91% correct** on
both halves (~4M rows each). The column is fully explained by the route's bank
currencies — nothing else feeds it.

**Rule 5 — The endpoint country columns are ~5% wrong at each end.**
The path's first bank disagrees with `ORDERING_BIC8` in 4.98% of rows; the last
bank disagrees with `BENEFICIARY_BIC8` 5.00% of the time — and the two errors are
independent. Practical rule the other groups follow: **use the path's first and
last bank for country work**, treat the endpoint columns as noise.

**Rule 6 — Fraud avoids Covered; mistakes don't.**
Normal multi-bank payments are Covered 11.3% of the time. Romance scam **0.3%**,
CEO fraud 2.0%, account replacement 1.5%. But fat-finger 13.2%, duplicates 11.4%,
recalls 11.5% — sitting right at the normal rate. So the *label* changes the
route shape: fraud looks like an unusual route; accidents look like ordinary
payments.

**Rule 7 — Belgium and Switzerland punch above their weight as middlemen.**
Middle-hop share ÷ endpoint share: BE 1.34, CH 1.30 (solid sample); UA 1.61, IM
1.56 (small n). The obvious test — "it's just currency geography" — fails
(Belgium's conversion-route share is 36% vs 32% baseline). Real reason unknown,
medium confidence: an honest open question.

<div class="verdict">The proof in one line: two zero-exception identities
(type = count, dots = N), one 5%-per-link coin, one 99.91% hold-out prediction,
a measured 5% column error rate — the route story, fully priced.</div>

## The one pattern behind all seven

g5's specialty is *identity* rules: compare two columns that should be
redundant (type vs count, dots vs flag) and check all 10M rows for a single
exception. Zero exceptions = a rule. Then the same comparing-habits move is
applied to harder cases: prediction with a hold-out set (Rule 4), a column's own
error rate (Rule 5), and whether labels change behaviour (Rule 6) — where the
clean baseline (11.3% Covered) is what makes 0.3% meaningful.

## Words I use

- **hop / link** — one bank-to-bank leg of a route; a path with n banks has
  n−1 links.
- **hidden bank (`...`)** — a bank that exists in the route but is not shown; its
  presence is flagged by `CONTINUITY_QFLAG = N`.
- **endpoint** — the first or last bank of the path (sender's / beneficiary's).
- **middle bank** — any bank between the two endpoints.
- **Covered** — one of the type labels; with Rule 1 it just means "3+ banks".
