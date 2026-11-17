# Rule content for the g3 · Amounts page.

COLUMNS = """
| column | what it is | how g3 uses it |
| :--- | :--------- | :------------- |
| `USD_AMOUNT` | the amount, in USD terms | the thing being explained |
| `CURRENCY_CODE` | the currency label | is roundness attached to a currency? (USD vs everyone else) |
| `BIC8_PATH` (first bank) | sender's bank → sender country | the suspected dial behind the amount level |
| `BIC8_PATH` (last bank) | beneficiary's bank | the corridor control: hold *who you pay to* fixed |
| `CURRENCY_CONVERSION_COUNT` | currency changes along the route | tested — found to matter not at all |
| `ANOMALY_TYPE` | label or empty | clean rows only |
| `half` | a built-in 50/50 split | check: does the ladder reproduce on independent halves? |

No timestamps, party text, or labels — g1, g7 and g8's territory.
"""

RULES = [
    dict(
        name="Amounts are lognormal: one shared shape, a free per-country centre",
        quick=(
            "Every country draws amounts from the same bell curve on a log scale; the "
            "countries differ only in where their curve is centred — the 'wealth ladder' "
            "from $48 (Guinea-Bissau) to $31,219 (Monaco)."
        ),
        analogy=(
            "everyone's salary curve has the same shape, but Monaco's whole bell sits far "
            "to the right of Guinea-Bissau's."
        ),
        tech="""
In log10 space the global distribution is essentially a perfect normal: mean 3.543,
sigma 1.122, skewness −0.085, kurtosis +0.048 on 10M clean rows. Per sender country
(158 with n≥2,000) the width never changes — sigma 0.97–1.19, median **1.050**
everywhere — only the centre moves: mu from 1.678 (Guinea-Bissau, median **$48**)
through Ukraine $223 and US $7,156 to 4.494 (Monaco, **$31,219**). The full ladder
is in `agg/_g3_country_mu.pkl`. Validation of the two-level model: E[sigma²] +
var(mu) = 1.1168 + 0.1498 = 1.2665 vs the global sigma² 1.2587 — explained to
within **0.6%**.
""",
    ),
    dict(
        name="The country centre is a fixed dial, not a side effect",
        quick=(
            "The wealth ladder is a setting the generator fixed in advance and reproduces "
            "exactly — not an accident of traffic, currency mix, or who pays whom."
        ),
        analogy=(
            "a leaderboard settled before the season starts: re-run the season on fresh "
            "rows and the same countries sit in the same places."
        ),
        tech="""
Four squeezes, each with the control that would break the rule:

- **Reproducible** — split each country's rows into two independent halves
  (`half` column; 181 countries with ≥500 in each): corr(centre half 0, half 1) =
  **0.9977**, mean |difference| 0.0247 dex, while the *between-country* spread is
  sd 0.572 dex — 23× the noise. A centre that emerged from a row sample dies here.
- **Nothing recorded predicts it** — traffic, EUR share, cross-border share … all
  eight attributes together reach only **R² = 0.46**; the correlations are
  cross-country confounds (busy countries happen to be rich), not causes.
- **Not the corridor** — restricting to payments whose beneficiary bank is in the
  US (133 countries, ≥500 rows each), each sender's centre still matches its
  all-rows centre: **r = 0.986**, spread 0.567 vs 0.568 dex. The dial belongs to
  the *sender*, not to whom it pays.
- **Not the party mix** — inside business-only senders the ladder still spans
  **3.188 dex**; inside retail-only, 2.889 dex. Removing the B/C effect (g4's
  dial) doesn't shrink the spread — country and type are separate knobs.
""",
    ),
    dict(
        name="USD amounts come from a nice-number pool: {1, 2, 5} × 10^k",
        quick=(
            "Flip the currency label to USD and amounts suddenly become whole numbers "
            "(38.65% vs 0.99% elsewhere), over-representing values built from 1, 2 and "
            "5 — $200, $5,000, $1,500."
        ),
        analogy=(
            "the tips drawer of a restaurant where people only ever leave $1, $2 and $5 "
            "bills."
        ),
        tech="""
USD rows: whole dollars **38.65%**; multiples of 10/100/1,000 at 19.1%/15.6%/11.4%;
every other currency **0.99%**/0.10%/0.01% (chance). Structure of USD integers:
**10.7% are exactly {1,2,5}×10^k** (non-USD 0.02%); 46.4% have ≤2 significant
figures (59.2% ≤3); leading digits spike on 1 (35.0% vs Benford 30.1%) and 5
(14.1% vs 7.9%). The mode is uniform over the whole window (38.6–38.8% per
15-day bucket — not a storm event) and country-independent (g2 chart: DE-EUR
0.94% vs DE-USD 37.5%). Holding the sender country fixed, switching the currency
label to USD turns on the nice-number mode.
""",
    ),
    dict(
        name="2.83% of rows are 'storm' rows: one amount, stamped across a day",
        quick=(
            "On certain days, one base amount and its ×2 ×3 ×5 ×10 clones flood a single "
            "currency — hundreds of unrelated parties paying the exact same figure."
        ),
        analogy=(
            "a voucher amount stamped onto a whole print run: thousands of vouchers, same "
            "number, one day, back to normal the next morning."
        ),
        tech="""
Census: 1,145 (currency, amount, day) cells with ≥100 rows AND ≥50% of that
amount's rows — **282,771 rows** (2.83%). Structure, proven on the 2023-06-09 EUR
storm: base 1,159.42 stamped into 727 payments, integer multiples into more —
×10: 598 rows, ×5: 433, ×100: 244, ×50: 188, ×3: 108, ×2: 105, down to ×160
(3,135 rows in that one family). Bases drift per currency (EUR ~1,100–1,220,
CHF ~1,250–1,320, GBP ~1,200–1,325), each independently. Storm rows are otherwise
ordinary: 42 sender countries in one storm, type mix = the currency's mix, 332
rows → 324 distinct beneficiaries, anomaly labels at the normal rate (69/282,771
vs 0.07% base — slightly below). This also explains the exotic repeated integers
of non-USD currencies: 5,667.00 = 1,133.40×5; 57,971.00 and 115,942.00 = ×50/×100
of 1,159.42.
""",
    ),
    dict(
        name="Amounts follow Benford's law — except where the generator decorates",
        quick=(
            "Leading digits behave exactly as natural log-scale numbers should (digit 1 "
            "at 30.1%…) — and the only bumps sit at 1 and 5, from the USD pool."
        ),
        analogy=(
            "a crowd of random heights follows a known bell; the one stage-managed group "
            "in the room sticks out at exactly the heights the organiser likes."
        ),
        tech="""
Leading digit of all clean amounts: 1: **31.44%** (Benford 30.10%), 2: 16.84%
(17.61%), 5: **8.84%** (7.92%), 9: 4.38% (4.58%) — the residual deviations are
exactly the USD {1,2,5} pool of Rule 3. The world is honest except where the
generator says "make it pretty".
""",
    ),
]

FACTS = """
| fact | value |
| :--- | :---- |
| clean amounts | median $3,678 · p75 $19,921 · p90 $94,879 · p99 $1.27M · min $0.01 · max $1.395B |
| storm census | 1,145 (currency, amount, day) cells → 282,771 rows = 2.83%: EUR 6.76% of its rows, CHF 3.61%, GBP 3.35%, SGD 1.42%, CNY 0.94%, USD 0.00% |
"""

DECODERS = """
- `USD_AMOUNT` — the amount drawn in USD terms; all currencies carry exactly 2
  decimals. No FX conversion exists (g2 Rule 4).
- `CURRENCY_CODE` — its only feedback into amounts: switching the label to USD
  turns on the nice-number mode (country control: DE-EUR 0.94% vs DE-USD 37.5%).
- sender country — characters 5–6 of the path's first bank; owns the centre dial.
- `half` — the built-in 50/50 split behind the split-half checks (centre
  r = 0.9977; the width never moves).
- **corridor control** — restricting to payments whose beneficiary bank is in the
  US (133 countries, ≥500 rows each) to prove the ladder is sender-side
  (r = 0.986).
"""

DEAD_ENDS = """
- **"Something about the payment moves the amount."** Every candidate is flat:
  median log10 amount by visible bank count 3.563 / 3.564 / 3.565 / 3.566 / 3.566
  (2–6 banks); Direct 3.563 vs Indirect 3.557 vs Covered 3.628; hidden banks
  3.564 vs 3.564; weekend 3.563 vs weekday 3.564. The one tempter — 0 conversions
  3.72 vs 3.54 (+0.18 dex) — is corridor composition: same-country 0-conv 3.746
  vs same-country 2-conv 3.738 (no gap); the cross-country gap (3.704 vs 3.540)
  is the wealth of EUR-zone/US neighbours.
- **"Repeating amounts mean recurring relationships."** Same (sender, beneficiary,
  amount) repeats are rare — 5,560 rows, max 13 repeats; storms, not
  relationships, explain the repeats.
- **Storm census threshold.** ≥100 rows/day AND ≥50% of the value's rows is
  conservative; smaller families exist, so 2.83% is a lower bound on storm mass.
- **Daily base dynamics.** Whether a storm's base is redrawn per day or evolves
  continuously cannot be separated; the observed drift fits either.
"""

PATTERN = (
    "The common thread: hold something fixed and see what survives. Hold "
    "the two halves fixed — the centre survives (r = 0.9977). Hold the corridor fixed — "
    "the centre survives (r = 0.986). Hold the corridor fixed on the conversion effect — "
    "it dies. Hold the country fixed on roundness — the currency label wins. Rules that "
    "survive fixed comparisons are real; effects that dissolve under one were "
    "composition all along."
)

GLOSSARY = """
- **dex** — one power of ten in log space: +1 dex = ×10, +0.1 dex ≈ ×1.26.
- **centre (mu)** — the middle of a country's log-amount curve; the "wealth dial".
- **sigma** — the width of that curve; shared by all countries here.
- **two-level model** — one shared shape + a per-country offset for the centre.
- **storm** — a day where a base amount and its integer multiples flood one
  currency (injected; near-invisible without the census trick).
- **clean row** — no anomaly label.
"""
