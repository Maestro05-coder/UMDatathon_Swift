"""Shared look & feel for the findings app.

Aesthetic: "night ledger, squared". Same light-ish darkness as before (dark
navy #0E1420, never pitch black), JetBrains Mono throughout, sharp rectangles
everywhere (no rounded corners), navy panels with a single orange accent.
Injected once on every page via apply_theme().
"""
import streamlit as st

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:ital,wght@0,400;0,500;0,600;0,700;0,800;1,400;1,500&display=swap');

:root {
  --bg:#0E1420; --bg2:#151C2A; --panel:#121927; --line:#232E44;
  --ink:#E7ECF5; --ink2:#9AA8BF; --lead:#C6D2E4;
  --navy:#3D5A8C; --steel:#7FA6D9; --accent:#F0785F;
  --font:'JetBrains Mono','Cascadia Mono','Consolas',monospace;
}

* { border-radius: 0 !important; }

.stApp {
  background-color: var(--bg);
  background-image:
    radial-gradient(1100px 520px at 82% -10%, rgba(61,90,140,.38), transparent 62%);
  background-repeat: no-repeat;
  background-attachment: fixed;
  color: var(--ink);
  font-family: var(--font);
}

h1, h2, h3, h4 {
  font-family: var(--font) !important;
  color: #EDF2FA !important;
  letter-spacing: -0.02em;
  font-weight: 700;
}
h1 { font-size: 2.05rem; font-weight: 800; line-height: 1.2; }
h2 { font-size: 1.3rem; font-weight: 700; margin-top: 2.4rem !important; }
h3 { font-size: 1.02rem; font-weight: 700; }
h3::before { content: "▪ "; color: var(--accent); font-size: .8em; }

p, li, td, th { font-family: var(--font); }
p { margin: .6em 0; line-height: 1.65; }

.kicker {
  text-transform: uppercase; letter-spacing: .22em;
  font-size: .72rem; color: var(--accent); font-weight: 600;
}
.tagline {
  font-style: italic;
  color: var(--ink2); font-size: 1.02rem; margin-top: -2px; line-height: 1.6;
}
.verdict {
  border-left: 3px solid var(--accent);
  background: rgba(240,120,95,.08);
  padding: .9em 1.1em;
  margin: 2rem 0; color: var(--lead);
  font-size: .93em; line-height: 1.6;
}

.rulecard {
  background: linear-gradient(180deg, rgba(21,28,42,.92), rgba(17,24,38,.92));
  border: 1px solid var(--line);
  border-left: 3px solid var(--accent);
  padding: 1.05rem 1.3rem .95rem;
  margin: 1.7rem 0;
}
.rulenum {
  text-transform: uppercase; letter-spacing: .2em;
  font-size: .7rem; color: var(--accent); font-weight: 600;
  margin-bottom: .3rem;
}
.rulecard h3 { margin: .1rem 0 .45rem !important; }
.rulecard h3::before { content: none; }
.rulecard p { color: var(--lead); margin: .35em 0; line-height: 1.6; }
.analogy { color: var(--steel) !important; font-style: italic; }
.analogy b { color: var(--accent); font-style: normal; }

.chartnote {
  font-size: 1.03rem; color: var(--ink); line-height: 1.7;
  background: rgba(61,90,140,.20);
  border: 1px solid #2E3D5C; border-left: 4px solid var(--accent);
  padding: 1.15em 1.5em; margin: .9em 0 3em;
}
.chartnote b {
  color: var(--accent); font-weight: 600; font-size: .8em;
  text-transform: uppercase; letter-spacing: .09em;
  display: block; margin-bottom: .35em;
}

table { border-collapse: collapse; width: auto !important; }
th {
  background: #1D2A42 !important; color: #CFE0F5 !important;
  font-size: .70rem !important; letter-spacing: .07em;
  text-transform: uppercase; padding: .5em .85em !important;
  font-weight: 600;
}
td {
  font-size: .93rem; padding: .45em .85em !important;
  border-bottom: 1px solid #1E2739 !important;
  vertical-align: top !important; color: var(--lead);
}
tr:nth-child(even) td { background: rgba(255,255,255,.025); }

pre, .stCodeBlock {
  background: #0A0E16 !important; border: none !important;
  border-left: 3px solid var(--accent) !important;
  padding: 14px 18px !important;
}
pre code { color: #DCE6F5 !important; font-family: var(--font) !important; font-size: .85rem !important; }

div[data-testid="stExpander"] {
  background: var(--panel) !important;
  border: 1px solid var(--line) !important;
  margin: 1rem 0 1.6rem;
}
div[data-testid="stExpander"] summary { font-size: .95rem; }
div[data-testid="stExpanderDetails"] { border-top: 1px solid var(--line); }

[data-testid="stSidebar"] { background: #0A0F17; border-right: 1px solid #1C2437; }
[data-testid="stSidebar"] * { color: #DCE4F2 !important; font-family: var(--font) !important; }
[data-testid="stSidebarNavLink"]:hover { background: rgba(240,120,95,.14); }
[data-testid="stSidebarNavLink"][aria-current="page"] { background: rgba(240,120,95,.24); }

.block-container { max-width: 1160px; padding-top: 3.2rem; padding-bottom: 6rem; }
hr { border-color: var(--line) !important; margin: 2.4rem 0 !important; }
img { box-shadow: 0 2px 18px rgba(0,0,0,.45); }
a { color: var(--accent) !important; }
"""


def apply_theme() -> None:
    st.markdown(CSS, unsafe_allow_html=True)
