"""Shared look & feel for the findings app.

Aesthetic: "forensic ledger". Warm paper background with faint ruled lines,
engraved-serif headings (Fraunces), IBM Plex Sans/Plex Mono for body and
numbers, dark proof-row blocks, ledger-green tables, stamp-red accents.
Injected once on every page via apply_theme().
"""
import streamlit as st

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,500;0,9..144,650;1,9..144,500&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;600&display=swap');

:root {
  --paper:#FAF7F0; --paper2:#F1EADC; --ink:#23231F; --ink2:#5A5A50;
  --ledger:#1F5F4E; --stamp:#B2382B; --line:#E3DACA;
}

.stApp {
  background-color: var(--paper);
  background-image:
    repeating-linear-gradient(0deg, transparent 0 34px, rgba(31,95,78,.045) 34px 35px),
    radial-gradient(1100px 480px at 85% -8%, rgba(31,95,78,.07), transparent 60%);
  color: var(--ink);
}

/* --- typography ------------------------------------------------------- */
h1, h2, h3, h4 {
  font-family: 'Fraunces', Georgia, serif !important;
  color: #1E1F1C !important;
  letter-spacing: -0.01em;
}
h1 { font-size: 2.25rem; font-weight: 650; line-height: 1.15; }
h2 { font-size: 1.45rem; font-weight: 650; margin-top: 1.7rem; }
h3 { font-size: 1.08rem; font-weight: 650; margin-top: 1.25rem; }
h3::before { content: "▪"; color: var(--stamp); margin-right: .5em; font-size: .8em; }

.kicker {
  font-family: 'IBM Plex Mono', monospace;
  text-transform: uppercase; letter-spacing: .22em;
  font-size: .72rem; color: var(--stamp); font-weight: 600;
}
.tagline {
  font-family: 'Fraunces', Georgia, serif; font-style: italic;
  color: var(--ink2); font-size: 1.12rem; margin-top: -4px;
}
.verdict {
  border-left: 3px solid var(--ledger);
  background: rgba(31,95,78,.07);
  padding: .75em 1em; border-radius: 0 8px 8px 0; margin: .9em 0;
  font-family: 'IBM Plex Mono', monospace; font-size: .92em;
}

/* --- tables ----------------------------------------------------------- */
table { border-collapse: collapse; width: auto !important; }
th {
  font-family: 'IBM Plex Mono', monospace !important;
  background: var(--ledger) !important; color: #F5F1E6 !important;
  font-size: .70rem !important; letter-spacing: .07em;
  text-transform: uppercase; padding: .45em .8em !important;
}
td {
  font-size: .92rem; padding: .42em .8em !important;
  border-bottom: 1px solid var(--line) !important;
  vertical-align: top !important;
}
tr:nth-child(even) td { background: rgba(31,95,78,.05); }

/* --- code blocks (proof rows) ------------------------------------------ */
pre, .stCodeBlock {
  background: #211E19 !important; border: none !important;
  border-left: 3px solid var(--stamp) !important;
  border-radius: 6px !important; padding: 14px 18px !important;
}
pre code { color: #EFE6D4 !important; font-family: 'IBM Plex Mono', monospace !important; font-size: .85rem !important; }

/* --- sidebar ------------------------------------------------------------ */
[data-testid="stSidebar"] { background: #211E19; border-right: 1px solid #3A352C; }
[data-testid="stSidebar"] * { color: #EDE4D3 !important; }
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2 { font-size: 1rem; }
[data-testid="stSidebarNavLink"] { border-radius: 6px; }
[data-testid="stSidebarNavLink"]:hover { background: rgba(178,56,43,.22); }
[data-testid="stSidebarNavLink"][aria-current="page"] { background: rgba(178,56,43,.32); }

/* --- layout polish ------------------------------------------------------ */
.block-container { max-width: 1150px; padding-top: 3.4rem; padding-bottom: 5rem; }
div[data-testid="stExpander"] { border: 1px solid var(--line) !important; border-radius: 8px; }
hr { border-color: var(--line) !important; }
img { border-radius: 6px; box-shadow: 0 1px 10px rgba(35,35,31,.09); }
a { color: var(--stamp) !important; }
"""


def apply_theme() -> None:
    st.markdown(CSS, unsafe_allow_html=True)
