"""UMDatathon 2026 — reverse-engineering 10,000,000 SWIFT-like payments.

Findings app. Everything shown is precomputed analysis (charts, READMEs,
simplified explainers) — the 4.7 GB source file itself never leaves the
working machine, so this app needs no data at runtime.
"""
import sys
from pathlib import Path

import streamlit as st

HERE = Path(__file__).parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

st.set_page_config(
    page_title="10M payments, reverse-engineered",
    page_icon="🗃️",
    layout="wide",
    initial_sidebar_state="expanded",
)

from ui import apply_theme  # noqa: E402  (needs sys.path first)

apply_theme()

PAGES = [
    st.Page("pages/00_overview.py", title="Overview", icon="🏦", default=True),
    st.Page("pages/shortlist.py", title="Shortlist · actual rules", icon="⭐", url_path="shortlist"),
    st.Page("pages/g1.py", title="g1 · Time", icon="🕒", url_path="g1"),
    st.Page("pages/g2.py", title="g2 · Currency", icon="💱", url_path="g2"),
    st.Page("pages/g3.py", title="g3 · Amounts", icon="💵", url_path="g3"),
    st.Page("pages/g4.py", title="g4 · Banks & countries", icon="🏛️", url_path="g4"),
    st.Page("pages/g5.py", title="g5 · Routing", icon="🛤️", url_path="g5"),
    st.Page("pages/g6.py", title="g6 · Duration & FX", icon="⏱️", url_path="g6"),
    st.Page("pages/g7.py", title="g7 · Parties & text", icon="📇", url_path="g7"),
    st.Page("pages/g8.py", title="g8 · Anomalies", icon="🚨", url_path="g8"),
]

st.navigation(PAGES, position="sidebar").run()
