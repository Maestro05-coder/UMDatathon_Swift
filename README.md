# 10,000,000 payments, reverse-engineered

Streamlit findings app for **UMDatathon 2026 — Swift case study**. A hidden
generator produced a 10M-row SWIFT-like payments file; we reverse-engineered its
rules, one feature area ("group") at a time, and proved every rule against the
full file.

**Every number in this app is exact** — computed on all 10,000,000 rows with
DuckDB, never sampled. Random samples were used only for chart shapes; every rare
bucket was counted exactly. Each rule is shown next to its chance baseline, and
documented dead ends are kept in the write-ups on purpose.

## What's here

| group | headline rule |
| :---- | :------------- |
| g1 · time | one shared two-hump working-day template on 18 integer-hour country clocks (−0.02 → +0.99) |
| g2 · currency | currency = sender side (93% vs 19%); no FX-rate table exists |
| g3 · amounts | lognormal, shared shape, free per-country centre ($48 … $31k); USD nice numbers; 2.83% storm rows |
| g4 · banks | fixed 8-slot BIC8 layout (0 exceptions in 25.8M); business adds +0.865 dex (7.3×) at every income level |
| g5 · routing | type = bank count; `...` = QFLAG N; ~5%-per-link hiding; endpoint columns ~5% wrong |
| g6 · duration | duration = sum of per-bank step delays; conversions and hidden banks cost nothing; "Covered slow" was bank composition |
| g7 · parties | `_FAKE_` accounts; whale senders carry 78.6% of rows; sender address real (100%), beneficiary address decoy (0.98%) |
| g8 · anomalies | FAT_FINGER = honest × 10^k, k varying; five other labels squeezed against clean baselines |

`app/content/overview.md` has the dataset spec, the column dictionary and the
method. Each group page follows the same rhythm:

1. the columns the group uses (compact table),
2. the rules — each as a **quick take with a plain analogy**, with the full
   technical proof (numbers, controls, dead ends) in an expandable block,
3. the one pattern behind the group's rules,
4. the charts, each followed by a "what this shows" note,
5. a glossary of the group's own terms (hop, step, dex, dial, decoy…),
6. the complete write-up with proof rows straight from the file.

## Run it locally

```bash
pip install -r requirements.txt
streamlit run app/app.py
```

## Repo layout

```
app/
  app.py            entry point (multi-page navigation)
  ui.py             shared theme ("forensic ledger")
  pages/            one file per group + overview
  content/          per group: explainer.md (simple), README.md (full), charts
```

## A note on the data

The source CSV (~4.95 GB) and the analysis caches stay out of this repository on
purpose — everything the app shows is a frozen, exact result of the full-data
analysis. The heavy lifting scripts and caches live in the private working
project.
