"""Shared look & feel for the findings app.

Aesthetic: "night ledger". Dark slate-navy background (not pitch black) with
faint ruled lines, engraved-serif headings (Fraunces), IBM Plex Sans/Mono for
body and numbers, stamp-red accents, ledger-green highlights. Injected once on
every page via apply_theme().
"""
import streamlit as st

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,500;0,9..144,650;1,9..144,500&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;600&display=swap');

:root {
  --bg:#0E1420; --bg2:#151C2A; --panel:#121927; --line:#232E44;
  --ink:#E7ECF5; --ink2:#9AA8BF; --lead:#C6D2E4;
  --ledger:#57C7A3; --navy:#3D5A8C; --stamp:#F0785F;
}

.stApp {
  background-color: var(--bg);
  background-image:
    repeating-linear-gradient(0deg, transparent 0 37px, rgba(93,140,220,.05) 37px 38px),
    radial-gradient(1100px 520px at 82% -10%, rgba(61,90,140,.38), transparent 62%);
  color: var(--ink);
}

/* --- typography ------------------------------------------------------- */
h1, h2, h3, h4 {
  font-family: 'Fraunces', Georgia, serif !important;
  color: #EDF2FA !important;
  letter-spacing: -0.01em;
}
h1 { font-size: 2.25rem; font-weight: 650; line-height: 1.16; }
h2 { font-size: 1.5rem; font-weight: 650; margin-top: 2.4rem !important; }
h3 { font-size: 1.12rem; font-weight: 650; }
h3::before { content: "▪ "; color: var(--stamp); font-size: .8em; }

p { margin: .6em 0; }

.kicker {
  font-family: 'IBM Plex Mono', monospace;
  text-transform: uppercase; letter-spacing: .22em;
  font-size: .72rem; color: var(--stamp); font-weight: 600;
}
.tagline {
  font-family: 'Fraunces', Georgia, serif; font-style: italic;
  color: var(--ink2); font-size: 1.14rem; margin-top: -2px; line-height: 1.5;
}
.verdict {
  border-left: 3px solid var(--ledger);
  background: rgba(87,199,163,.09);
  padding: .9em 1.1em; border-radius: 0 10px 10px 0;
  margin: 2rem 0; color: var(--lead);
  font-family: 'IBM Plex Mono', monospace; font-size: .93em; line-height: 1.55;
}

/* --- rule cards -------------------------------------------------------- */
.rulecard {
  background: linear-gradient(180deg, rgba(21,28,42,.92), rgba(17,24,38,.92));
  border: 1px solid var(--line);
  border-left: 3px solid var(--stamp);
  border-radius: 10px;
  padding: 1.05rem 1.3rem .95rem;
  margin: 1.7rem 0;
}
.rulenum {
  font-family: 'IBM Plex Mono', monospace;
  text-transform: uppercase; letter-spacing: .2em;
  font-size: .7rem; color: var(--stamp); font-weight: 600;
  margin-bottom: .3rem;
}
.rulecard h3 { margin: .1rem 0 .45rem !important; }
.rulecard h3::before { content: none; }
.rulecard p { color: var(--lead); margin: .35em 0; line-height: 1.6; }
.analogy { color: #A9BBDD !important; font-style: italic; }
.analogy b { color: var(--ledger); font-style: normal; }

.chartnote {
  font-size: .92rem; color: var(--lead); line-height: 1.55;
  background: rgba(61,90,140,.14);
  border: 1px solid var(--line); border-radius: 8px;
  padding: .65em 1em; margin: .55em 0 2.6em;
}
.chartnote b { color: var(--ledger); font-weight: 600; }

/* --- tables ----------------------------------------------------------- */
table { border-collapse: collapse; width: auto !important; }
th {
  font-family: 'IBM Plex Mono', monospace !important;
  background: #1D2A42 !important; color: #CFE0F5 !important;
  font-size: .70rem !important; letter-spacing: .07em;
  text-transform: uppercase; padding: .5em .85em !important;
}
td {
  font-size: .93rem; padding: .45em .85em !important;
  border-bottom: 1px solid #1E2739 !important;
  vertical-align: top !important; color: var(--lead);
}
tr:nth-child(even) td { background: rgba(255,255,255,.025); }

/* --- code blocks (proof rows) ------------------------------------------ */
pre, .stCodeBlock {
  background: #0A0E16 !important; border: none !important;
  border-left: 3px solid var(--stamp) !important;
  border-radius: 6px !important; padding: 14px 18px !important;
}
pre code { color: #DCE6F5 !important; font-family: 'IBM Plex Mono', monospace !important; font-size: .85rem !important; }

/* --- expanders ---------------------------------------------------------- */
div[data-testid="stExpander"] {
  background: var(--panel) !important;
  border: 1px solid var(--line) !important;
  border-radius: 10px !important;
  margin: 1rem 0 1.6rem;
}
div[data-testid="stExpander"] summary { font-size: .95rem; }
div[data-testid="stExpanderDetails"] { border-top: 1px solid var(--line); }

/* --- sidebar ------------------------------------------------------------ */
[data-testid="stSidebar"] { background: #0A0F17; border-right: 1px solid #1C2437; }
[data-testid="stSidebar"] * { color: #DCE4F2 !important; }
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2 { font-size: 1rem; }
[data-testid="stSidebarNavLink"] { border-radius: 6px; }
[data-testid="stSidebarNavLink"]:hover { background: rgba(240,120,95,.14); }
[data-testid="stSidebarNavLink"][aria-current="page"] { background: rgba(240,120,95,.24); }

/* --- layout polish ------------------------------------------------------ */
.block-container { max-width: 1160px; padding-top: 3.2rem; padding-bottom: 6rem; }
hr { border-color: var(--line) !important; margin: 2.4rem 0 !important; }
img { border-radius: 8px; box-shadow: 0 2px 18px rgba(0,0,0,.45); }
a { color: var(--stamp) !important; }
"""


def apply_theme() -> None:
    st.markdown(CSS, unsafe_allow_html=True)
