# Watch While You Eat — Research Analysis & Dashboard

Reproducible analysis of the pre/post survey for the "Watch While You Eat" Netflix prototype: problem
validation (C1–C5), solution validation, matched pre/post analysis, guardrail check, KPI framework, and a
Streamlit dashboard. Every number in the dashboard and the written deliverables is generated from
`pre and post final.xlsx` by the scripts in `analysis/` — nothing is hand-typed into the dashboard.

## Requirements

Python 3.10+ and:

```
pip install pandas openpyxl streamlit plotly python-docx
```

(`python-docx` is only needed to re-run `analysis/spec_crosscheck.py`'s source dump; the core pipeline needs
only `pandas`, `openpyxl`, `streamlit`, `plotly`.)

## Reproduce the analysis

Run from the project root, in this order (each step reads/writes `analysis/results.json`):

```
python analysis/analysis.py            # loads the Excel file, applies the screener, matches pre/post,
                                         # computes C1-C5 / solution-validation / matched-pair numbers,
                                         # writes clean_pre.csv, clean_post.csv, matched.csv, results.json
python analysis/qualitative_themes.py   # appends hand-coded open-text theme counts
python analysis/kpi_framework.py        # appends the 9 core KPIs + 1 guardrail KPI
python analysis/spec_crosscheck.py      # appends the cross-check against the survey spec docx
python analysis/export_kpi_table.py     # writes analysis/kpi_table.csv (flat KPI export)
```

All five are idempotent and can be re-run any time the source Excel file changes — the dashboard will pick up
new numbers automatically on its next run since it reads only `analysis/results.json` and the three CSVs.

## Run the dashboard

```
streamlit run dashboard/app.py
```

Opens at `http://localhost:8501` (or the next free port). Eleven sections, navigable from the sidebar:
Business Problem, Sample/Recruitment Funnel, Problem Validation, Solution Validation, Before vs After,
Guardrail, Feature Component Analysis, Segment Analysis, KPI Scorecard, Key Insights, Recommendations.

## Project structure

```
pre and post final.xlsx                 raw survey export (source of truth)
Pre-Post Survey — Problem Validation.docx   screener + question spec + measurement plan
analysis/
  analysis.py                            main pipeline: QA, screener, matching, C1-C5, solution validation,
                                          matched pre/post, guardrail, qualitative raw text extraction
  qualitative_themes.py                  hand-coded open-text theme counts
  kpi_framework.py                       9 core KPIs + 1 guardrail KPI, built only from already-computed values
  spec_crosscheck.py                     cross-checks results against the survey spec docx
  export_kpi_table.py                    flat KPI CSV export
  clean_pre.csv / clean_post.csv / matched.csv   cleaned, renamed datasets
  results.json                           every number used anywhere downstream
  kpi_table.csv                          KPI table deliverable
dashboard/
  app.py                                 Streamlit dashboard (reads only results.json + the three CSVs)
deliverables/
  data_dictionary.md                     column-by-column dictionary, raw name -> clean name -> notes
  qa_report.md                           data quality report (screener, matching, spec cross-check)
  business_proposal.md                   ~1000-word business proposal
README.md                                this file
```

## Key numbers (see dashboard for full detail with denominators)

- 75 pre-survey submissions -> 61 eligible after the screener -> 37 completed the post survey (60.7%
  completion).
- Problem validation is partial: the occasion is frequent (85.2% watch at a meal 3+/week) and the off-platform
  leak is real (54.1%), but chronic abandonment is a minority (13.1% "often") and 37.7% of respondents already
  know what they want before sitting down (the falsifier).
- Solution reaction measures are strongly positive (94.6% would have started, 86.5% would stay on Netflix) but
  the measure requiring actual commitment is weaker (32.4% top-box likelihood to use).
- The guardrail (already-seen/would-skip) shows no failure signal in the current data (0/37) — see Section 6
  of the dashboard.
- No business metrics (market share, CAC, CRC, EBITDA, actual retention) are measurable from this dataset;
  see Section 9 of the dashboard for what would be required.
