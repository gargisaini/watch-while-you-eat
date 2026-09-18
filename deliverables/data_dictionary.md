# Data Dictionary — Watch While You Eat Pre/Post Survey

Source file: `pre and post final.xlsx` (sheets `pre`, `post`). Cleaned outputs: `analysis/clean_pre.csv`
(eligible respondents only, n=61), `analysis/clean_post.csv` (n=37), `analysis/matched.csv` (inner join on
`session_id`, n=37). Column renames applied in `analysis/analysis.py`.

## Pre-survey (`clean_pre.csv`)

| Clean name | Raw column | Type | Values observed | Spec question | Notes |
|---|---|---|---|---|---|
| `session_id` | session_id | string (UUID) | unique per row | — | join key |
| `screened_out` | screened_out | boolean | True/False | — | provided in source; independently reproduced from S1–S3/Q1 logic |
| `eligible` | *(derived)* | boolean | `not screened_out` | — | added in pipeline |
| `age_band` | How old are you? | categorical | Under 18, 18–22, 23–26, 27–30, 31 or older | S1 | Under 18 / 31+ screen out |
| `stream_freq` | How often do you watch shows or movies on a streaming app? | categorical | Every day, A few times a week, About once a week, Rarely | S2 | Rarely screens out |
| `eat_while_watch` | Do you watch something while eating a meal? | categorical | Most meals, Sometimes, Rarely, Never | S3 | Never screens out |
| `devices` | Where do you usually watch during meals? | multi-select, `;`-joined | Phone, Laptop, TV, Tablet (combinations) | (context) | not itself a screener item |
| `meal_sessions_per_week` | In a typical week, how many times... | categorical (ordinal) | 0, 1–2, 3–5, 6–10, 10+ | Q1 (C1) | 0 screens out |
| `decision_time` | Think about the last time... how long did you spend deciding | categorical (ordinal) | Under 1 minute, 1–3, 3–5, 5–10, Over 10 minutes, I never started | Q2 (C2) | "I never started" excluded from time-threshold %s |
| `meal_pct_over` | By the time you settled on something, how much of your meal was already over? | numeric (0–10 slider) | 0–10, observed 0–10 | Q3 (C2) | 0 = none of it, 10 = most of it |
| `giveup_freq` | In the last month, how often did you open a streaming app at a meal but give up... | categorical (ordinal) | Never, Once or twice, A few times, Often | Q4 (C3) | spec lists a 5th option "Almost every time" — 0 responses in this export |
| `know_what_want` | When you sit down to watch at a meal, do you usually already know... | categorical | I usually already know, I usually have to figure it out, Depends | Q5 (C3 falsifier) | — |
| `action_when_dragged` | The last time deciding dragged at a meal, what did you actually do? | categorical | Switched to YouTube, Put on an old favourite, Scrolled social media instead, Watched something on it anyway, Switched to another app | Q6 (C4) | spec lists 6th option "Gave up and just ate" — 0 responses |
| `annoyance` | How annoying is the 'what do I put on' part at mealtime, for you? | numeric (0–10 slider) | 0–10 | Q7 (C5) | — |
| `open_giveup_story` | Describe the last time you gave up... | free text | 18 of 61 gave a substantive answer | Q8 (open) | optional; 42 of 61 left it blank, 1 more wrote only "Na" |

## Post-survey (`clean_post.csv`)

| Clean name | Raw column | Type | Values observed | Spec question | Notes |
|---|---|---|---|---|---|
| `session_id` | session_id | string (UUID) | unique per row | — | join key; all 37 trace to an eligible pre respondent |
| `noticed_row` | Did you notice a row meant to help you quickly pick something to watch? | categorical | Yes, Not sure, No | (awareness) | — |
| `perceived_speed` / `perceived_speed_num` | Compared to how you normally decide... | categorical + numeric (-1..2) | Much faster, Faster, About the same, Slower | Q1 (C2) | numeric column consistent 1:1 with categorical |
| `taste_match` | How well did the episodes it showed you match your taste? | numeric (scale, observed 3–5) | mean 4.14, std 0.89 | **not in spec's Q1–Q9 list** | supplementary item; prior PDF report flagged an item like this as a degenerate default — not the case in this export |
| `start_intention` / `start_intention_num` | If that had been a real meal... started watching or given up? | categorical + numeric (0..2) | Started easily, Started eventually, Probably given up | Q2 (C3) | — |
| `reduced_struggle` / `reduced_struggle_num` | Did it reduce the 'what do I put on' struggle...? | categorical + numeric (0..2) | Yes, clearly; Somewhat; No | Q3 | — |
| `stay_on_netflix` / `stay_on_netflix_num` | Would this keep you on Netflix instead of switching...? | categorical + numeric (0..2) | Yes, Maybe, No, I'd still switch | Q4 (C4) | spec's single option "No, I'd still switch" appears split into "No" and "I'd still switch" in this export |
| `guardrail_already_seen` | Of the episodes it suggested, did they feel like things you'd want or already skip? | categorical | Mostly things I'd want, A mix | Q5 (guardrail) | spec's 3rd option "Mostly already-seen/would-skip" — 0 responses; 0 missing |
| `useful_components` | Which parts felt useful? | multi-select, `;`-joined | mood filters, best-episode pick, shows already watched, jump-to-best-moment | Q6 | spec's "None" option — 0 responses |
| `likelihood_use_next` | How likely are you to use this at your next meal? | numeric (0–10) | mean 6.14, median 6 | (mapped to spec's top-box likelihood KPI; spec's own question numbering for this item is internally inconsistent — see Section 12/spec_crosscheck) | — |
| `open_one_thing` | What is the ONE thing that would make you actually use it? | free text | 35 of 37 answered | Q8 (open) | — |
| `open_confusion` | Anything that confused you or got in the way? | free text | 4 of 37 gave a substantive answer | Q9 (open) | optional; 29 of 37 left it blank, 4 more wrote only "No"/"IDK"/"Nothing" |

## Derived / analysis fields (matched.csv and results.json only)

| Field | Definition |
|---|---|
| `decision_time_over3` | pre `decision_time` in {3–5, 5–10, Over 10 minutes} |
| `speed_faster` | post `perceived_speed` in {Faster, Much faster} |
| `gave_up_often` / `gave_up_ever` | pre `giveup_freq` == Often / in {Once or twice, A few times, Often} |
| `would_start` | post `start_intention` in {Started easily, Started eventually} |
| `off_platform_pre` | pre `action_when_dragged` in {Switched to YouTube, Scrolled social media instead, Switched to another app} |
| `stay_post` | post `stay_on_netflix` in {Yes, Maybe} |
| `primary_device` | first device listed in pre `devices` (order as entered, not frequency-ranked) |

## Files produced by the pipeline

| File | Produced by | Contents |
|---|---|---|
| `analysis/clean_pre.csv` | analysis.py | 61 eligible pre respondents, renamed columns |
| `analysis/clean_post.csv` | analysis.py | 37 post respondents, renamed columns |
| `analysis/matched.csv` | analysis.py | inner join of the two on session_id, n=37 |
| `analysis/results.json` | analysis.py → kpi_framework.py → qualitative_themes.py → spec_crosscheck.py | every number used anywhere in the dashboard/report |
| `analysis/kpi_table.csv` | export_kpi_table.py | flat KPI table (deliverable) |
