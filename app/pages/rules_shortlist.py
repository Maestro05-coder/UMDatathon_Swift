# Content for the Shortlist page ("Actual rules"): the 13 findings we'd defend.
#
# Each entry: group + folder (chart location), title, why (why it made the list),
# simple (one-look summary, mirrors the group page's quick take) and deep (the
# squeezes with exact numbers, mirrors the group page's technical expander).
# Every number is a full-data result — identical to the group pages and READMEs.

GROUP_META = {
    "g1": ("g1_time", "g1 · Time"),
    "g2": ("g2_currency", "g2 · Currency"),
    "g3": ("g3_amount", "g3 · Amounts"),
    "g4": ("g4_banks", "g4 · Banks & countries"),
    "g5": ("g5_routing", "g5 · Routing"),
    "g6": ("g6_fx_duration", "g6 · Duration & FX"),
    "g7": ("g7_parties", "g7 · Parties & text"),
    "g8": ("g8_anomalies", "g8 · Anomalies"),
}

RULES = [
    dict(
        group="g1",
        title="g1 · R1 — every country is a whole-hour offset of one shared template",
        why=(
            "Hidden integer-lookup table; −0.02 → +0.99; survives split-half. The benchmark."
        ),
        simple=(
            "All 10M payments follow one busy-working-day rhythm, and each country plays it "
            "shifted by a whole number of hours. On the file's own UTC clock the country "
            "curves look like noise (−0.024); shifted by each country's offset they collapse "
            "onto one shape (+0.990). It's a working-day template: weekends are nearly closed "
            "(Saturday + Sunday carry 11.18% vs 28.6% if all seven days were equal)."
        ),
        deep="""
On one UTC clock, countries don't line up at all — average curve similarity **−0.024**
(noise). Shift each country by *its own* whole-hour offset and all 113 country curves
collapse onto the shared shape: **+0.990**.

| clock | avg curve similarity (113 countries) |
| :---- | ---: |
| file's own UTC clock | −0.024 — looks like noise |
| shifted by each country's own hour offset | **+0.990** — near-perfect |

The offsets are not fitted curves: they are **18 distinct integer hours** covering all
113 countries — `+6 h` for 28 countries, `+7 h` for 15, `+1 h` for 10, `+8 h` for 9,
`+5 h` for 9, `0 h` for 8, `−11 h` for 8, and eleven more values — a generator lookup
from country to clock. Recovering each offset independently from two disjoint halves
of the rows reproduces the identical hour for **90 of 113** countries; the other 23
differ by **exactly one hour** (adjacent high hours of the same flat-topped peak) —
the signature of an integer table, not a fitted curve.
""",
        charts=[
            ("g1_2_aligned_day.png",
             "Lined up by each country's busiest hour, all 113 country curves collapse onto one band — the shared template made visible."),
            ("g1_6_offset_table.png",
             "The lookup itself: 18 whole-hour offsets cover all 113 countries — 28 countries share +6 h. A generator table, not real-world time zones."),
        ],
    ),
    dict(
        group="g1",
        title="g1 · R2 — the two busy windows are one process, not two",
        why=(
            "Refutes a tempting story with per-country controls (1 of 113 shifts)."
        ),
        simple=(
            "The day has two humps, but the payments in the second hump are the same kind as "
            "in the main one — holding the country fixed, amounts, cross-border share and "
            "business-sender share all sit at zero difference. A second hump, not a special "
            "batch cut off at some deadline."
        ),
        deep="""
The shared template has a main window (hours 22, 23, 0, 1, 2 from the peak — **32.9%**
of payments) and a second window (hours 13–16 — **20.1%**). The \"cut-off batch\" story
predicts the two windows carry *different* payments. Holding the country fixed across
113 countries (≥5,000 clean rows each), second window minus main window:

| measured per country | median | p10 | p90 |
| :--- | ---: | ---: | ---: |
| log10 amount ratio | +0.0058 | −0.0319 | +0.0357 |
| cross-border share | +0.0000 | −0.0012 | +0.0013 |
| business-sender share | +0.0025 | −0.0089 | +0.0179 |

Only **1 of 113** countries shifts its amount by more than 0.1 dex between the
windows. Pooled over all rows: median duration 55 s vs 54 s, median amount $3,875 vs
$4,108, cross-border 92.57% vs 92.08%. Same mix, different hour.
""",
        charts=[
            ("g1_5_two_windows.png",
             "Per-country second-window minus main-window differences all sit at zero: same payments, different hour."),
        ],
    ),
    dict(
        group="g3",
        title="g3 · R1 + R2 — lognormal, one shape, a free per-country centre",
        why=(
            "Mechanism + four fixed controls (r = 0.9977; corridor r = 0.986)."
        ),
        simple=(
            "Every country draws amounts from the same bell curve on a log scale; the "
            "countries differ only in where their curve is centred — the wealth ladder from "
            "$48 (Guinea-Bissau) to $31,219 (Monaco). The centre is a fixed dial, not a side "
            "effect: it repeats across independent halves (r = 0.9977) and survives holding "
            "the corridor fixed (r = 0.986)."
        ),
        deep="""
In log10 space the global distribution is essentially a perfect normal: mean 3.543,
sigma 1.122, skewness −0.085, kurtosis +0.048 on 10M clean rows. Per sender country
(158 with n≥2,000) the width never changes — sigma 0.97–1.19, median **1.050**
everywhere — only the centre moves: mu from 1.678 (Guinea-Bissau, median **$48**)
through Ukraine $223 and US $7,156 to 4.494 (Monaco, **$31,219**). Two-level model
check: E[sigma²] + var(mu) = 1.2665 vs global sigma² 1.2587 — explained to within
**0.6%**.

The centre is a fixed dial — four squeezes, each with the control that would break it:

- **Reproducible** — corr(centre half 0, half 1) = **0.9977** (181 countries with ≥500
  rows in each half), mean |difference| 0.0247 dex, while the between-country spread is
  sd 0.572 dex — 23× the noise.
- **Nothing recorded predicts it** — all eight traffic/currency/corridor attributes
  together reach only **R² = 0.46**; the correlations are cross-country confounds.
- **Not the corridor** — restricting to payments whose beneficiary bank is in the US
  (133 countries, ≥500 rows each), each sender's centre still matches its all-rows
  centre: **r = 0.986**, spread 0.567 vs 0.568 dex.
- **Not the party mix** — inside business-only senders the ladder still spans
  **3.188 dex**; inside retail-only, 2.889 dex. Country and type are separate knobs.
""",
        charts=[
            ("g3_2_wealth_ladder.png",
             "Same shape in every country — only the centre moves: $48 median in Guinea-Bissau to $31,219 in Monaco."),
            ("g3_5_country_centre.png",
             "The centre is a real dial: it repeats across independent halves (r = 0.9977), its width never moves, and fixing the corridor to the US keeps the ladder (r = 0.986)."),
        ],
    ),
    dict(
        group="g3",
        title="g3 · R4 — storms: 2.83% injected amount-families",
        why=(
            "A genuinely hidden structure, invisible without the census trick."
        ),
        simple=(
            "On certain days, one base amount and its ×2 ×3 ×5 ×10 clones flood a single "
            "currency — hundreds of unrelated parties paying the exact same figure. 1,145 "
            "(currency, amount, day) cells totalling 282,771 rows (2.83%). Without the "
            "census trick they are invisible; otherwise the rows are ordinary."
        ),
        deep="""
Census: 1,145 (currency, amount, day) cells with ≥100 rows AND ≥50% of that amount's
rows — **282,771 rows** (2.83%). Structure, proven on the 2023-06-09 EUR storm: base
1,159.42 stamped into 727 payments, integer multiples into more — ×10: 598 rows,
×5: 433, ×100: 244, ×50: 188, ×3: 108, ×2: 105, down to ×160 (3,135 rows in that one
family). Bases drift per currency (EUR ~1,100–1,220, CHF ~1,250–1,320,
GBP ~1,200–1,325), each independently. Storm rows are otherwise ordinary: 42 sender
countries in one storm, type mix = the currency's mix, 332 rows → 324 distinct
beneficiaries, anomaly labels at the normal rate. This also explains the exotic
repeated integers of non-USD currencies: 5,667.00 = 1,133.40×5; 57,971.00 and
115,942.00 = ×50/×100 of 1,159.42.
""",
        charts=[
            ("g3_4_storms.png",
             "One storm day (9 Jun 2023, EUR): base 1,159.42 repeated in integer multiples — 3,135 payments in the family."),
        ],
    ),
    dict(
        group="g4",
        title="g4 · R2 — B/C is a +0.865 dex dial at every income level",
        why=(
            "Separate knob; slope-1 offset; holds across 167 countries."
        ),
        simple=(
            "Business payments run ~7.3× retail (a constant +0.865 dex), with the same boost "
            "in rich and poor countries alike — and it stacks on top of the country dial: "
            "B→B median $22,900 vs C→C $464 (49.4×)."
        ),
        deep="""
Types are only ever B or C (0 A/D rows in all 10M). Holding the **country** fixed and
comparing business senders to retail senders within it (167 countries with ≥300 of
each): median offset **+0.865 dex = 7.3×**, sd 0.100, p25–p75 +0.807…+0.917,
min +0.517 (ME) … max +1.179 (XK); 101 of 167 countries inside 0.80–0.95 dex. Because
the effect is additive in log space, each country's retail median plotted against its
business median sits on a **slope-1 line** displaced by a constant — the offset doesn't
grow with wealth. Both endpoints count and they stack:

| pair | rows | median amount | vs C→C |
| :--- | ---: | ---: | ---: |
| C→C | 1,512,382 | $464 | 1.0× |
| B→C | 5,600,965 | $3,118 | 6.7× |
| C→B | 609,762 | $3,236 | 7.0× |
| B→B | 2,269,885 | $22,900 | 49.4× |
""",
        charts=[
            ("g4_8_bc_offset.png",
             "167 countries on a slope-1 line displaced by +0.86 dex: the type effect is a separate dial from the country dial."),
            ("g4_5_party_types.png",
             "Each business endpoint multiplies the median by ~7 — B→B $22,900 vs C→C $464."),
        ],
    ),
    dict(
        group="g4",
        title="g4 · R3 — banks carry their own stable tilt",
        why=(
            "Split-half r = 0.93; not explained by country or type."
        ),
        simple=(
            "On top of the country dial and the type dial, each bank has its own character — "
            "a stable σ ≈ 0.274 dex tilt: retail-heavy banks run smaller, and the tilt "
            "repeats across independent halves of the data (r = 0.931)."
        ),
        deep="""
Among 2,221 (bank, country) cells with n≥500, a bank's median deviates from its
country's median with σ = **0.274 dex**; the deviation correlates **−0.584** with the
bank's retail (C) share. Split-half check (2,200 banks with ≥250 rows each): the tilt
correlates **0.931** across halves, and every bank in the top decile of half 0 stays
above median in half 1. Client mix explains part of it (corr 0.62 with the predicted
type-cell median); the residual σ ≈ **0.22 dex** is the bank's own property, not noise.
""",
        charts=[
            ("g4_6_bank_tilt.png",
             "Banks add their own tilt beyond the country (r = −0.58 vs retail share); tilts are stable across halves (r = 0.93)."),
        ],
    ),
    dict(
        group="g5",
        title="g5 · R2 — a hidden bank is a ~5% coin per link",
        why=(
            "A real generative mechanism — fits 1 − (1−p)^k."
        ),
        simple=(
            "Each bank-to-bank link flips its own ~5% coin for 'hide the next bank': 2 links "
            "hide something 9.7% of the time, 3 links 14.2% — and every route length fits "
            "the 1−(1−p)^k curve within 0.4 percentage points."
        ),
        deep="""
A route of k links hides ≥1 bank with probability 1 − (1 − 0.04986)^k: 2 links → 9.7%,
3 links → 14.2%, and so on — every route length fits within **0.4 percentage points**.
Hiding is uncorrelated with everything else: it is an independent coin per hop.
(Side effect: `...` is a *guaranteed hint* that the visible route is not the whole
route — every dotted row says QFLAG N, 0 exceptions in 767,204 rows.)
""",
        charts=[
            ("routing_2_gap_per_hop.png",
             "Hidden-bank chance grows link by link, matching the ~5%-per-link curve (red line) at every route length."),
        ],
    ),
    dict(
        group="g5",
        title="g5 · R5 — fraud avoids the Covered route; mistakes don't",
        why=(
            "Non-obvious behavioural split."
        ),
        simple=(
            "Scam labels almost never ride a Covered route (0.3–2.0% vs 11.3% clean), while "
            "mistake labels sit right at the clean rate. Professional thieves avoid the "
            "route with the police escort; clumsy tourists don't know the difference."
        ),
        deep="""
Covered share on normal multi-bank payments: **11.3%**. Romance scam **0.3%**, CEO
fraud **2.0%**, account replacement **1.5%** — all far below. Fat-finger **13.2%**,
duplicates **11.4%**, recalls **11.5%** — all at the normal rate. Mistakes look like
ordinary payments; fraud looks different.
""",
        charts=[
            ("routing_8_fraud_covered.png",
             "Covered share per anomaly label: the three mistake labels sit at the clean 11.3% rate; the three fraud labels collapse to 0.3–2.0%."),
        ],
    ),
    dict(
        group="g6",
        title="g6 · R1 (+R4, R5) — duration = sum of per-bank step delays",
        why=(
            "Mechanism; conversions and hidden banks cost nothing."
        ),
        simple=(
            "A route's total time is the sum of its legs — knowing each leg's typical "
            "duration predicts the whole journey (actual ≈ −13 s + 0.99 × predicted). A "
            "step's delay is a bank property, and nothing else charges: conversions and "
            "hidden banks cost zero."
        ),
        deep="""
Take each step's own typical duration (measured from the millions of simple 2-bank
payments containing that exact leg), add them up, and land next to the real total:

| route | actual | steps added |
| :---- | -----: | ----------: |
| `0004IMD0;0077CHZ0;0086KRS0` | 322s | 322 + 17 = **339s** |
| `0026FIH0;0074SGS0;0007IMD0` | 93s | 72 + 31 = **103s** |
| `0412FRP0;0300CHZ0;0292CHZ0` | 503s | 360 + 157 = **517s** |
| `0068IT20;0309CHZ0;0216CHZ0` | 85s | 22 + 80 = **102s** |

Fitted over all measurable 3-bank routes: actual ≈ **−13 + 0.99 × predicted** — a
near-perfect identity line. Why the sum works: a step's delay belongs to the bank,
not the pair (same bank pair → spread ~4% of the median; a bank's sending delay
matches its receiving delay, corr **0.87**). And nothing else charges: currency
conversions are flat (44 s vs 38 s at 2 banks; 126/80/81 s for 0/1/2 conversions at
3 banks) and hidden banks cost nothing (44 s with, 44 s without).
""",
        charts=[
            ("g6_step_additivity.png",
             "Adding the per-step delays predicts the total duration; step delays themselves are heavy-tailed."),
            ("g6_duration_vs_length.png",
             "Duration climbs with route length; conversion count doesn't shift the curve."),
        ],
    ),
    dict(
        group="g7",
        title="g7 · R4 — sender address real (100%), beneficiary address decoy (0.98%)",
        why=(
            "Non-obvious, actionable, mechanism-backed."
        ),
        simple=(
            "The sender's written address always matches the sender's bank country (100%); "
            "the beneficiary's address matches only 0.98% — it comes from a different, "
            "random world. The bank columns carry the truth; beneficiary address text is "
            "a decoy, never a geographic feature."
        ),
        deep="""
Country written in the details (from the `country_code:`/`country_name:` tokens) vs
the party's bank country:

| side | rows with a country token | match |
| :--- | ---: | ---: |
| ORDERING | 8,453,693 | **100.00%** |
| BENEFICIARY | 8,487,531 | **0.98%** |

The beneficiary address pool is population-weighted *somewhere else*: CN 14.5%,
BR 9.0%, UA 7.2%, ET 5.8% — nothing like the beneficiary *bank* world (US 19.2%,
CH 8.3%, GB 6.6%). Proof row: a GB-bank beneficiary whose address says Bangladesh
(`<post_code:BD:4> <city:BD:6> <country_name:BD:en-gb>`).
""",
        charts=[
            ("g7_3_country_decoy.png",
             "Address country vs bank country: sender matches 100%, beneficiary matches 0.98% — the decoy rule."),
        ],
    ),
    dict(
        group="g8",
        title="g8 · R1 — FAT_FINGER: honest amount × 10^k, k varying per row",
        why=(
            "The best anomaly rule: refutes fixed-shift and real-repeat."
        ),
        simple=(
            "The recorded amount is the sender's ordinary amount multiplied by a power of "
            "ten, with the shift varying per row: ÷10–÷1,000 rescue 56.0% of labelled rows "
            "into the sender's own normal range (clean chance 34.7%), and the whole-dollar "
            "rate rises with size exactly as a decimal shift predicts."
        ),
        deep="""
**Test 1 — far from home.** Distance from the sender's own median amount (1,843
fat-finger rows whose sender has ≥5 clean payments): fat finger median **2.283 dex
(~190×)** vs clean 0.640 dex (~4.4×); 59.31% of fat-finger rows are ≥100× off the
sender's habits (clean 3.77%).

**Test 2 — the decisive decimal-shift.** Divide by 10, 100, 1,000 and ask whether the
row lands back inside the sender's own middle 50% of amounts (q25–q75):

| divide by | 1 (as recorded) | 10 | 100 | 1,000 | 10,000 | any of 10–1,000 |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| **fat finger** | 9.28% | 18.72% | **24.15%** | 23.06% | 16.71% | **56.00%** |
| clean (control) | **49.67%** | 30.35% | 7.76% | 0.79% | 0.03% | 34.72% |

Fat-finger rows are *least* at home unshifted and are rescued by ÷10–1,000 far more
often than chance; the rescue only makes sense if the amount was shifted by a power of
ten. It survives a tighter control (same sender→beneficiary pairs: rescue 51.2% vs
23.25% clean). Confirming fingerprint: a ×10^k with k ≥ 2 turns any 2-decimal amount
into a whole number, so the whole-dollar rate rises with size — and it does, only for
USD: 78.0% ($100k–$1M) and 98.8% ($10M+) vs clean ~38%; non-USD fat-finger rows show
no trace. The intended amount is a fresh draw, not a real earlier payment (exact
10^k matches to same-sender payments: 0.67% vs 1.40% clean), and the shift is a wide
mixture (mean 1.576 dex, sd 2.230), not one fixed comma position.
""",
        charts=[
            ("g8_fatfinger_shift.png",
             "The decimal-shift test: share landing back inside the sender's normal range after ÷1, ÷10, ÷100, ÷1,000, ÷10,000 — fat finger vs clean."),
            ("g8_fatfinger_dev.png",
             "How far a payment sits from the same sender's median: fat-finger rows are ~190× off typical, clean rows ~4×."),
        ],
    ),
    dict(
        group="g8",
        title="g8 · R2 — the other label mechanisms (ROMANCE burst, CEO first-contact, ACCOUNT_REPLACEMENT one-off)",
        why=(
            "Each label is a distinct injected pattern."
        ),
        simple=(
            "Duplicates resend within minutes, romance escalates within an hour, CEO strikes "
            "on first contact with a huge tail, replacement pays a normal amount to a "
            "one-off account — four fingerprints, none overlapping."
        ),
        deep="""
| label | mechanism | exact signature |
| :---- | :-------- | :-------------- |
| DUPLICATE | same payment re-sent within minutes | median gap **1,099s (~18 min)**, p75 2,189s, max 6,940s — vs **~14.7 days** for clean repeats of the same trio; a repeat-pair within 2h flags a labelled duplicate at **74% precision** (494 vs 164 clean vs 12 other) |
| ROMANCE | 2–8 escalating payments to one beneficiary inside ~1 hour | median span 18 min (max 70 min); amount climbs **$33 → $54 → $88 → $144 → $206 → $350 → $544 → $1,925**; median $109 vs clean $3,663; senders always C |
| CEO | first-ever contact, huge tail (B senders) | **100%** are the first payment ever between the pair (clean baseline 82%); p90 **$4.2M** vs $0.4M clean; median *lower* than clean — the signal is the tail |
| ACCOUNT_REPLACEMENT | normal amount to a never-before-paid account | **649/649** go to an account the sender never paid before and never pays after; median $4.0k ~ clean $3.7k — differentiator vs CEO: no tail |
""",
        charts=[
            ("g8_repeat_gaps.png",
             "Time between two identical payments: labelled duplicates cluster at minutes; normal repeats at days."),
            ("g8_romance_escalation.png",
             "Median amount by position in a romance burst: $33 → $54 → $88 → $144 → $206 → $350 → $544 → $1,925."),
            ("g8_label_amounts.png",
             "Median and 90th-percentile amount per label on a log axis — CEO's tail and fat-finger's level stand out."),
        ],
    ),
    dict(
        group="g2",
        title="g2 · R4 — there is no FX-rate table",
        why=(
            "A strong negative result that is itself a real, non-obvious finding."
        ),
        simple=(
            "Amounts are drawn directly in USD terms; the currency label is a sticker, never "
            "a conversion. Holding the country fixed, foreign-currency payments sit at the "
            "home-currency level (median gap −0.001 dex) — where a real FX table would "
            "force ±0.03–1.9 dex."
        ),
        deep="""
If real conversion happened, a currency's ratio to USD would be stable and
foreign-currency payments would sit at a shifted level versus home-currency ones, by
exactly the rate. Neither holds: holding the country fixed, the median log10
(`USD_AMOUNT`) delta between foreign- and home-currency payments is **−0.001 dex**
(median |Δ| 0.017) across 63 country×currency cells and 457,972 rows — a real rate
table would force ±0.03–1.9 dex. Ukraine pays EUR 4.7% of the time at median 2.341
log-$ — *identical* to its home-currency median (a \"0.0 dex conversion\"). The
earlier-looking \"implied rates\" (USD/INR ≈ 82) were fake: the amount distribution is
a property of the sender country's wealth, and the currency rides along (g3's ladder).
""",
        charts=[
            ("g2_5_no_fx.png",
             "Held-country amount gaps, one dot per (sender country, currency) cell: everything hugs zero inside the shaded chance zone — a real FX table would push dots to ±0.03–1.9 dex."),
        ],
    ),
]
