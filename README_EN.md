# Technical Efficiency and Risk Prediction in Bogotá's District Development Plan 2024–2027

*Spanish version: [README.md](README.md)*

Master's thesis project (Data Science, Universidad Santo Tomás) that aims to evaluate how efficiently Bogotá's District Development Plan *"Bogotá Camina Segura"* turns budget into physical progress, and to flag product goals at risk of under-execution. It combines **Data Envelopment Analysis (DEA)**, **Natural Language Processing (NLP)** on institutional progress reports, and **classification models** with temporal validation.

**Team:** Adrian Grateron · Jhonatan Smith Doncel · Jorge Emmanuel Marín

## Current status

- ✅ Research proposal (October 2026): problem, objectives, methodology and timeline.
- ✅ **Data pipeline (Bronze → Silver)** in four Jupyter notebooks: automated download of official sources from Bogotá's Planning Secretariat, cleaning of plan-progress and investment tables, and extraction of narrative reports (delays, solutions, achievements) from PDF.
- ✅ Offline HTML prototype to prioritize which goals and activities need follow-up.
- ⏳ DEA, NLP and classification phases have not been run yet; no efficiency scores or model metrics are reported.

## First processed snapshot (June 30, 2026)

| Silver table | Rows |
|---|---|
| Product goals | 425 |
| Goal indicators | 443 |
| Investment activities (48 agencies, 16 sectors) | 1,655 |
| Narrative reports per goal | 425 |

At this cut-off the plan reports **71.1 %** physical progress against what was scheduled through 2026 and **53.3 %** against the full four-year target; 17 goals show zero progress.

## Repository structure

`pipeline/` notebooks and Silver data · `docs/` proposal (PDF) · `latex/` source · `prototipo/` HTML prototype.

**Tech:** Python · pandas · requests/BeautifulSoup · PyMuPDF · Jupyter · DEA · NLP · **License:** CC BY 4.0 (source data keeps its original terms)
