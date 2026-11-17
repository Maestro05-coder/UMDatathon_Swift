## The columns g2 uses

| column | what it is | how g2 uses it |
| :--- | :--------- | :------------- |
| `CURRENCY_CODE` | the currency label on the payment (GBP, EUR…) | the thing being explained |
| `USD_AMOUNT` | the amount | used for the "round numbers" rule |
| `BIC8_PATH` | the bank route, `;`-separated | first bank = sender, last bank = receiver |
| `ORDERING_BIC8` / `BENEFICIARY_BIC8` | the sender/receiver bank columns | used as a check (they're ~5% wrong — g5 Rule 5) |

That's it. No time, no parties, no anomaly labels — those belong to g1, g7, g8.

## The rules, and how each is squeezed out

**Rule 1 — "the currency is decided by the sender."**
You have a currency label and two banks. The trick: each bank's country implies a
typical currency (Germany → EUR, US → USD). So for the first bank, ask "does its
country's usual currency match `CURRENCY_CODE`?" → **93.42%** yes. Do the same for
the last bank → only **19.09%** yes — roughly what random mixing over 155
currencies would produce (the stated sender column scores 89.45%, consistent with
its ~5% error rate). 93 vs 19 is the whole proof: the label follows the sender,
not the receiver.

**Rule 2 — "every country has a home currency."**
Line every payment up by sender country, and for each country ask "what's the most
common currency its payments use?" That majority is the country's **home currency**
(e.g. US→USD, DE→EUR, GT→GTQ) — recovered exactly for all 228 countries. Then
measure how often payments actually use it: most countries sit at **~91–98%**
(weighted median 91.9%). The one loud outlier is Russia: only **72.9%**, because it
pays in EUR 23.2% of the time. A control confirms this is a sender-side property,
not a route story: payments *inside* one country use the home currency **96.78%**
vs 93.15% for cross-country payments.

**Rule 3 — "when it's NOT the home currency, it leans to the receiver."**
Only ~6.6% of payments are foreign. Take those 657,004 rows and ask: was this
currency picked freely, or does it track the beneficiary? If free, matching the
beneficiary's home currency would happen at the baseline rate of however many
foreign payments *could* have matched. Actual wins over baseline for every
currency: EUR 62.1% vs 41.8%, USD 54.1% vs 21.8%, **GBP 62.2% vs 8.5%**, CHF 58.6%
vs 6.7%, CNY 51.9% vs 3.1%. There is a real pull toward the receiver's currency —
but not a rule (42% still don't match; the pull mostly lands on EUR 56.0% and USD
25.6% of foreign rows).

**Rule 4 — "USD amounts are round; others aren't."**
Ignore routing entirely — just look at `USD_AMOUNT` and ask "is this an exact
whole dollar (or a multiple of 100)?" USD → **38.65%** whole / **15.55%** ÷100;
every other currency → **0.99%** / 0.01% (chance). The country control proves it's
the *currency label*, not the sender: DE-EUR 0.94% vs DE-USD **37.5%**; GB 0.97%
vs **39.2%**; JP 0.92% vs **39.2%**; and US senders paying in EUR drop to 0.90%.
Flip the label to USD and a "nice numbers" mode turns on.

**Rule 5 — "there is no FX-rate table" (the negative rule).**
If amounts were converted from a currency into USD using real exchange rates, two
things would hold: a currency's ratio to USD would be stable, and same-country
payments in a foreign currency would sit at a different level than home-currency
payments, by exactly the rate. Both are flat: holding the country fixed, the
median `log10(USD_AMOUNT)` delta between foreign- and home-currency payments is
**−0.001 dex** (median |Δ| 0.017), where a real rate table would force ±0.03–1.9
dex. Ukraine pays EUR 4.7% of the time at median 2.341 log-$ — **identical** to
its home-currency median. So the amount is drawn in USD terms; `CURRENCY_CODE` is
a label attached by Rules 1–3, and no conversion ever happens.

<div class="verdict">The proof in one line: 93% vs 19% (whose label), 96.8% vs
93.2% (home-currency control), 38.65% vs 0.99% (roundness), −0.001 dex (no FX
table).</div>

## The one pattern behind all five

Same three-step move every time:

1. Pick the column that should cause the effect (sender bank / currency / amount).
2. Group the 10M rows by it and count.
3. Compare against the baseline that would appear if nothing were going on
   (19% = chance mixing, 0.99% = round numbers by chance).

If the real number is far from the chance number → it's a rule. If it's close →
it's a documented dead end. That's how raw columns become "business rules".

## Words I use

- **home currency** — the most common currency a sender country uses (a proxy for
  the generator's per-country table).
- **foreign payment** — one whose currency is not the sender country's home currency.
- **beneficiary** — the receiving side of the payment (its bank's country defines
  "the receiver's currency").
- **chance baseline** — the match rate you'd expect from blind mixing; each
  currency's own baseline is its share of foreign payment destinations.
