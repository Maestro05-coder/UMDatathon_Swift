"""Shared renderer for the eight group pages.

Each page calls render("<group>"). Layout: title + tagline, the columns the
group uses (in an expander), then the rules — each as a quick-take card with a
simple analogy, with the full technical squeeze inside an expandable block —
then the one-pattern verdict, the charts each followed by its "what this shows"
note, and finally glossary + full write-up expanders.

Rule content lives in rules_<group>.py modules next to this file.
"""
import importlib
import sys
from pathlib import Path

import streamlit as st

HERE = Path(__file__).parent
for p in (str(HERE), str(HERE.parent)):
    if p not in sys.path:
        sys.path.insert(0, p)

from ui import apply_theme  # noqa: E402

CONTENT = HERE.parent / "content"

GROUPS = {
    "g1": dict(
        folder="g1_time",
        title="Time — when payments happen",
        tagline=(
            "One shared two-hump working-day template, stamped on each country's "
            "own integer-hour clock — 18 offsets turn a −0.02 curve correlation into +0.99."
        ),
        charts=[
            ("g1_1_hours_utc.png",
             "The raw file on one UTC clock: lumpy, several peaks — many working days overlap."),
            ("g1_2_aligned_day.png",
             "Lined up by each country's busiest hour, all 113 country curves collapse onto one band: same rhythm, different clock."),
            ("g1_3_country_peaks.png",
             "Countries peak at all 24 hours of the UTC day — the clocks really differ."),
            ("g1_4_weekday.png",
             "Weekdays carry 17.1–18.3% each; Saturday + Sunday together only 11.2%."),
            ("g1_5_two_windows.png",
             "Per-country second-window minus main-window differences all sit at zero: same payments, different hour."),
            ("g1_6_offset_table.png",
             "18 whole-hour offsets cover all 113 countries — 28 countries share +6 h."),
        ],
    ),
    "g2": dict(
        folder="g2_currency",
        title="Currency — whose money is it?",
        tagline=(
            "The currency is decided by the SENDER side (first bank 93% vs beneficiary 19%). "
            "Countries have home currencies; foreign payments lean to the receiver; "
            "USD gets nice-number amounts; no FX-rate table exists."
        ),
        charts=[
            ("g2_1_currency_census.png",
             "The 15 largest of 155 currencies; EUR+USD+GBP+CHF+SGD carry 69% of all payments."),
            ("g2_2_whose_currency.png",
             "Sender side 93.4% vs beneficiary side 19.1% — the sender decides (Rule 1)."),
            ("g2_3_usd_roundness.png",
             "Holding the sender country fixed, whole-number amounts jump from ~1% to ~38% only when the currency is USD (Rule 4)."),
            ("g2_4_beneficiary_pull.png",
             "When a payment is foreign, actual match to the beneficiary's home currency (blue) vs chance (grey) — every currency beats its baseline (Rule 3)."),
        ],
    ),
    "g3": dict(
        folder="g3_amount",
        title="Amounts — one shape, one ladder, one pool, storms",
        tagline=(
            "Lognormal everywhere with one shared shape (sigma ≈ 1.05) around a free "
            "per-country centre ($48 Guinea-Bissau … $31k Monaco); USD gets a "
            "{1,2,5}×10^k nice-number pool; 2.83% of rows are injected storm rows."
        ),
        charts=[
            ("g3_1_lognormal.png",
             "A 100,000-payment sample hugs a normal curve on a log axis (skew −0.08, kurtosis +0.05)."),
            ("g3_2_wealth_ladder.png",
             "Same shape in every country — only the centre moves: $48 median in Guinea-Bissau to $31,219 in Monaco."),
            ("g3_3_usd_roundness.png",
             "Only USD piles up on whole / 10 / 100 / 1,000 amounts; every other currency sits at chance (~1%)."),
            ("g3_4_storms.png",
             "One storm day (9 Jun 2023, EUR): base 1,159.42 repeated in integer multiples — 3,135 payments in the family."),
            ("g3_5_country_centre.png",
             "The centre is a real dial: it repeats across independent halves (r = 0.9977), its width never moves, and fixing the corridor to the US keeps the ladder (r = 0.986)."),
        ],
    ),
    "g4": dict(
        folder="g4_banks",
        title="Banks & countries — the two dials",
        tagline=(
            "BIC8 ids follow a fixed 8-slot layout (0 exceptions in 25.8M appearances), "
            "and business-vs-retail adds a constant +0.865 dex (7.3×) at every income "
            "level — two separate generator dials."
        ),
        charts=[
            ("g4_7_bic8_structure.png",
             "The 8-slot layout: 1,075 numeric prefixes, 229 country codes, 25 house letters, one constant '0'."),
            ("g4_8_bc_offset.png",
             "167 countries on a slope-1 line displaced by +0.86 dex: the type effect is a separate dial from the country dial."),
            ("g4_6_bank_tilt.png",
             "Banks add their own tilt beyond the country (r = −0.58 vs retail share); tilts are stable across halves (r = 0.93)."),
            ("g4_5_party_types.png",
             "Each business endpoint multiplies the median by ~7 — B→B $22,900 vs C→C $464."),
            ("g4_1_bank_census.png",
             "Bank pool grows with traffic (r = 0.94) — but Isle of Man runs 12 banks and Finland 33."),
            ("g4_2_intermediaries.png",
             "The top middle-hop banks; 45 of 8,727 banks are never an endpoint."),
            ("g4_3_top_corridors.png",
             "Top country pairs: domestic US→US alone is 395,503 payments of 24,017 pairs."),
            ("g4_4_reciprocity.png",
             "A→B and B→A are not balanced: the median pair differs by 11% between directions."),
        ],
    ),
    "g5": dict(
        folder="g5_routing",
        title="Routing — which banks a payment travels through",
        tagline=(
            "Route type = bank count (0 exceptions); `...` = QFLAG N (0 exceptions); "
            "each hidden bank is a ~5% roll per link; conversion count reaches 99.91% "
            "hold-out accuracy; the endpoint country columns are ~5% wrong."
        ),
        charts=[
            ("routing_1_type_vs_pathlen.png",
             "Rule 1 — the clean split: 2 banks = Direct, 3+ = Indirect/Covered."),
            ("routing_2_gap_per_hop.png",
             "Rule 3 — hidden-bank chance grows link by link, matching the ~5%-per-link curve."),
            ("routing_3_conversion_holdout.png",
             "Rule 4 — predicted vs actual conversion count on data the rule never saw (99.91%)."),
            ("routing_5_mismatch.png",
             "Rule 5 — ORDERING/BENEFICIARY columns disagree with the path ~5% of the time, at each end."),
            ("routing_7_hub_tilt.png",
             "Rule 7 — countries that punch above their weight as middlemen: Belgium 1.34×, Switzerland 1.30×."),
        ],
    ),
    "g6": dict(
        folder="g6_fx_duration",
        title="Duration & FX — what a payment costs in time",
        tagline=(
            "Duration = sum of per-bank step delays (slow banks are slow in both "
            "directions); conversions and hidden banks cost nothing; and 'Covered is "
            "3.27× slower' collapses to 1.14× once the banks are held fixed."
        ),
        charts=[
            ("g6_duration_vs_length.png",
             "Duration climbs with route length; conversion count doesn't shift the curve."),
            ("g6_gap_shrinks.png",
             "The headline: Covered ÷ Indirect shrinks 3.27× → 1.99× (same corridor) → 1.14× (same middle bank) as the comparison gets fairer."),
            ("g6_step_additivity.png",
             "Adding the per-step delays predicts the total duration; step delays themselves are heavy-tailed."),
        ],
    ),
    "g7": dict(
        folder="g7_parties",
        title="Parties & text — accounts, DETAILS, TOKENS",
        tagline=(
            "All accounts are `_FAKE_` placeholders (54% IBAN-shaped, prefix = bank "
            "country 100%); a small whale pool of senders vs 2.6M one-off beneficiaries; "
            "and the decoy rule: sender address is real, beneficiary address is a random-world pool."
        ),
        charts=[
            ("g7_1_accounts.png",
             "Most senders pay again, most beneficiaries are one-off; a few big senders carry nearly all payments."),
            ("g7_2_tokens.png",
             "Share of payments containing each recurring text block of the DETAILS profile."),
            ("g7_3_country_decoy.png",
             "Address country vs bank country: sender matches 100%, beneficiary matches 0.98% — the decoy rule."),
            ("g7_4_type_semantics.png",
             "B rows are worded as businesses, C rows as persons — and anomalies keep the same templates."),
        ],
    ),
    "g8": dict(
        folder="g8_anomalies",
        title="Anomalies — what each label actually does",
        tagline=(
            "FAT_FINGER = honest amount × 10^k with k varying per row (decimal-shift "
            "rescue 56.0% vs clean 34.7%); five other labels each squeezed: duplicates "
            "resend within ~18 min, romance escalates in ~1 h, CEO pays a first-ever "
            "contact a huge tail, replacement is normal-but-fresh — recall has no signature."
        ),
        charts=[
            ("g8_label_amounts.png",
             "Median and 90th-percentile amount per label on a log axis — CEO's tail and fat-finger's level stand out."),
            ("g8_fatfinger_dev.png",
             "How far a payment sits from the same sender's median: fat-finger rows are ~190× off typical, clean rows ~4×."),
            ("g8_fatfinger_shift.png",
             "The decimal-shift test: share landing back inside the sender's normal range after ÷1, ÷10, ÷100, ÷1,000, ÷10,000 — fat finger vs clean."),
            ("g8_repeat_gaps.png",
             "Time between two identical payments: labelled duplicates cluster at minutes; normal repeats at days."),
            ("g8_romance_escalation.png",
             "Median amount by position in a romance burst: $33 → $54 → $88 → $144 → $206 → $350 → $544 → $1,925."),
        ],
    ),
}


def _esc(md: str) -> str:
    """Markdown inside HTML block elements isn't parsed by st.markdown, so rule
    cards avoid markup; tech text is rendered as plain markdown separately."""
    return md


def render(group: str) -> None:
    cfg = GROUPS[group]
    mod = importlib.import_module(f"rules_{group}")
    apply_theme()
    d = CONTENT / cfg["folder"]

    st.markdown(f"<p class='kicker'>Group {group} · findings</p>", unsafe_allow_html=True)
    st.title(cfg["title"])
    st.markdown(f"<p class='tagline'>{cfg['tagline']}</p>", unsafe_allow_html=True)
    st.divider()

    with st.expander("🧰 The columns this group uses — and what they mean", icon="🗂️"):
        st.markdown(mod.COLUMNS)

    st.markdown("## The rules — the quick version first")
    for i, r in enumerate(mod.RULES, 1):
        st.markdown(
            f"<div class='rulecard'><div class='rulenum'>Rule {i}</div>"
            f"<h3>{_esc(r['name'])}</h3>"
            f"<p>{_esc(r['quick'])}</p>"
            f"<p class='analogy'><b>Analogy ·</b> {_esc(r['analogy'])}</p></div>",
            unsafe_allow_html=True,
        )
        with st.expander("🔬 The technical squeeze — numbers, controls, how it was proven"):
            st.markdown(r["tech"])

    st.markdown(f"<div class='verdict'>{mod.PATTERN}</div>", unsafe_allow_html=True)

    st.divider()
    st.markdown("## The charts")
    for png, point in cfg["charts"]:
        st.image(d / png, width="stretch")
        st.markdown(
            f"<div class='chartnote'><b>What this shows ·</b> {point}</div>",
            unsafe_allow_html=True,
        )

    with st.expander("🗣️ Words used on this page (hop, step, dex, dial…)", icon="📖"):
        st.markdown(mod.GLOSSARY)

    st.divider()
    with st.expander("📓 Full write-up — rules, dead ends, proof rows from the raw file", icon="🗃️"):
        st.markdown((d / "README.md").read_text(encoding="utf-8"), unsafe_allow_html=True)
