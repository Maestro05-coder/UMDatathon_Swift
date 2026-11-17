"""Shortlist page: the 13 rules that genuinely carry the file.

One block per rule: title + why-it-made-the-list, a one-look summary card (the
same quick take as the group page), an in-depth expander with the exact numbers,
a link to the group's full analysis, and the chart(s) that carry the rule.

Content lives in rules_shortlist.py next to this file.
"""
import sys
from pathlib import Path

import streamlit as st

HERE = Path(__file__).parent
for p in (str(HERE), str(HERE.parent)):
    if p not in sys.path:
        sys.path.insert(0, p)

from ui import apply_theme  # noqa: E402
from rules_shortlist import GROUP_META, RULES  # noqa: E402

CONTENT = HERE.parent / "content"

apply_theme()

st.markdown("<p class='kicker'>The shortlist</p>", unsafe_allow_html=True)
st.title("Actual rules — the ones that carry the file")
st.markdown(
    "<p class='tagline'>Thirteen findings survived every control we could throw at "
    "them. Each one below: a one-look summary, the exact numbers behind it, and the "
    "chart that carries it.</p>",
    unsafe_allow_html=True,
)
st.markdown(
    "Rule numbers refer to the group pages (g1–g8), where every squeeze is documented "
    "with its controls, its chance baselines, and the dead ends that were ruled out. "
    "Nothing on this page survived by luck — each rule was re-checked on independent "
    "halves of the data, against a held-fixed comparison, or against a clean baseline."
)
st.divider()

for i, r in enumerate(RULES, 1):
    folder, group_name = GROUP_META[r["group"]]
    st.markdown(
        f"<div class='shortlist-head'><span class='sl-num'>{i:02d}</span>"
        f"<span class='sl-title'>{r['title']}</span></div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<div class='sl-why'><b>Why it made the list ·</b> {r['why']}</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<div class='rulecard'><div class='rulenum'>In one look</div>"
        f"<p>{r['simple']}</p></div>",
        unsafe_allow_html=True,
    )
    with st.expander("🔬 In depth — the squeezes and the exact numbers"):
        st.markdown(r["deep"])
    st.markdown(f"[Full analysis in {group_name} →](/{r['group']})")
    for png, note in r["charts"]:
        st.image(CONTENT / folder / png, width="stretch")
        st.markdown(
            f"<div class='chartnote'><b>What this chart shows</b>{note}</div>",
            unsafe_allow_html=True,
        )
    st.divider()
