"""
Watch While You Eat — reproducible analysis pipeline.
Reads 'pre and post final.xlsx' from the project root, cleans it, applies the
screener, matches pre/post on session_id, computes every KPI in the brief,
and writes:
  analysis/clean_pre.csv
  analysis/clean_post.csv
  analysis/matched.csv
  analysis/results.json   (every number the dashboard and report use)
Run: python analysis/analysis.py
"""
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "pre and post final.xlsx"
OUT = Path(__file__).resolve().parent

# ---------------------------------------------------------------- load ----
pre_raw = pd.read_excel(SRC, sheet_name="pre")
post_raw = pd.read_excel(SRC, sheet_name="post")

PRE_COLS = {
    "session_id": "session_id",
    "screened_out": "screened_out",
    "How old are you?": "age_band",
    "How often do you watch shows or movies on a streaming app?": "stream_freq",
    "Do you watch something while eating a meal?": "eat_while_watch",
    "Where do you usually watch during meals? Pick every one you use.": "devices",
    "In a typical week, how many times do you watch something on a streaming app while eating a meal?": "meal_sessions_per_week",
    "Think about the last time you watched during a meal. How long did you spend deciding before you actually started?": "decision_time",
    "By the time you settled on something, how much of your meal was already over?": "meal_pct_over",
    "In the last month, how often did you open a streaming app at a meal but give up without watching anything on it?": "giveup_freq",
    "When you sit down to watch at a meal, do you usually already know what you want, or do you have to figure it out?": "know_what_want",
    "The last time deciding dragged at a meal, what did you actually do?": "action_when_dragged",
}
# annoyance + open text columns contain a mangled apostrophe char from export; match by prefix
for c in pre_raw.columns:
    if c.startswith("How annoying"):
        PRE_COLS[c] = "annoyance"
    if c.startswith("Describe the last time"):
        PRE_COLS[c] = "open_giveup_story"

pre = pre_raw.rename(columns=PRE_COLS)[list(dict.fromkeys(PRE_COLS.values()))].copy()

POST_COLS = {"session_id": "session_id"}
for c in post_raw.columns:
    if c == "session_id":
        continue
    if c.startswith("Did you notice"):
        POST_COLS[c] = "noticed_row"
    elif "[numeric]" in c and "was" in c:
        POST_COLS[c] = "perceived_speed_num"
    elif c.startswith("Compared to how you normally decide"):
        POST_COLS[c] = "perceived_speed"
    elif c.startswith("How well did the episodes"):
        POST_COLS[c] = "taste_match"
    elif "[numeric]" in c and "started watching" in c:
        POST_COLS[c] = "start_intention_num"
    elif c.startswith("If that had been a real meal"):
        POST_COLS[c] = "start_intention"
    elif "[numeric]" in c and "struggle" in c:
        POST_COLS[c] = "reduced_struggle_num"
    elif c.startswith("Did it reduce"):
        POST_COLS[c] = "reduced_struggle"
    elif "[numeric]" in c and "switching" in c:
        POST_COLS[c] = "stay_on_netflix_num"
    elif c.startswith("Would this keep you on Netflix"):
        POST_COLS[c] = "stay_on_netflix"
    elif c.startswith("Of the episodes it suggested"):
        POST_COLS[c] = "guardrail_already_seen"
    elif c.startswith("Which parts felt useful"):
        POST_COLS[c] = "useful_components"
    elif c.startswith("How likely are you to use"):
        POST_COLS[c] = "likelihood_use_next"
    elif c.startswith("What is the ONE thing"):
        POST_COLS[c] = "open_one_thing"
    elif c.startswith("Anything that confused"):
        POST_COLS[c] = "open_confusion"

post = post_raw.rename(columns=POST_COLS)[list(dict.fromkeys(POST_COLS.values()))].copy()

# ------------------------------------------------------------- data QA ----
qa = {}
qa["pre_rows_total"] = int(len(pre))
qa["pre_duplicate_session_ids"] = int(pre["session_id"].duplicated().sum())
qa["post_rows_total"] = int(len(post))
qa["post_duplicate_session_ids"] = int(post["session_id"].duplicated().sum())
qa["pre_missing_by_col"] = {k: int(v) for k, v in pre.isna().sum().items()}
qa["post_missing_by_col"] = {k: int(v) for k, v in post.isna().sum().items()}

# Screener, applied independently from the 'screened_out' flag already in the sheet,
# using the rule board: age Under 18 / 31+, freq Rarely/Never, eat Never, sessions/wk == 0
screen_age = pre["age_band"].isin(["Under 18", "31 or older"])
screen_freq = pre["stream_freq"].isin(["Rarely", "Never"])
screen_eat = pre["eat_while_watch"].isin(["Never"])
screen_q1 = pre["meal_sessions_per_week"].astype(str).isin(["0"])
computed_screened_out = screen_age | screen_freq | screen_eat | screen_q1
qa["screener_flag_matches_recomputation"] = bool((computed_screened_out == pre["screened_out"]).all())
qa["screener_breakdown"] = {
    "age_out_of_range": int(screen_age.sum()),
    "streaming_freq_too_low": int(screen_freq.sum()),
    "never_eats_while_watching": int(screen_eat.sum()),
    "zero_meal_sessions_per_week": int(screen_q1.sum()),
}

pre["eligible"] = ~pre["screened_out"].astype(bool)
elig = pre[pre["eligible"]].copy()

post_ids = set(post["session_id"])
elig_ids = set(elig["session_id"])
screened_ids = set(pre.loc[pre["screened_out"], "session_id"])

qa["submitted_n"] = int(len(pre))
qa["eligible_n"] = int(len(elig))
qa["screened_out_n"] = int(len(pre) - len(elig))
qa["post_ids_not_in_pre"] = sorted(post_ids - set(pre["session_id"]))
qa["post_ids_from_screened_out_pre"] = sorted(post_ids & screened_ids)
qa["matched_pairs_n"] = int(len(post_ids & elig_ids))
qa["eligible_with_no_post_n"] = int(len(elig_ids - post_ids))
qa["completion_rate_pct"] = round(100 * qa["matched_pairs_n"] / qa["eligible_n"], 1)

# discrepancy vs the prior PDF report (Team04_A6.pdf), kept explicit per instructions
qa["prior_report_claims"] = {
    "submitted_n": 67, "eligible_n": 55, "matched_pairs_n": 34, "completion_rate_pct": 61.8,
}
qa["discrepancy_vs_prior_report"] = (
    qa["submitted_n"] != 67 or qa["eligible_n"] != 55 or qa["matched_pairs_n"] != 34
)

matched = elig.merge(post, on="session_id", how="inner", suffixes=("_pre", "_post"))
qa["matched_rows_after_join"] = int(len(matched))
assert qa["matched_rows_after_join"] == qa["matched_pairs_n"]

elig.to_csv(OUT / "clean_pre.csv", index=False)
post.to_csv(OUT / "clean_post.csv", index=False)
matched.to_csv(OUT / "matched.csv", index=False)

N_PRE = len(elig)
N_POST = len(post)
N_MATCH = len(matched)


def pct(n, d):
    return round(100 * n / d, 1) if d else None


def counts(series):
    vc = series.value_counts(dropna=False)
    return {str(k): int(v) for k, v in vc.items()}


results = {"qa": qa, "n_pre": N_PRE, "n_post": N_POST, "n_matched": N_MATCH}

# ------------------------------------------------------------- C1 occasion
c1_ge3 = elig["meal_sessions_per_week"].isin(["3–5", "6–10", "10+"])
results["C1_occasion"] = {
    "distribution": counts(elig["meal_sessions_per_week"]),
    "n_3_or_more_per_week": int(c1_ge3.sum()),
    "d": N_PRE,
    "pct_3_or_more_per_week": pct(c1_ge3.sum(), N_PRE),
}

# ------------------------------------------------------------- C2 friction
dt_dist = counts(elig["decision_time"])
over3 = elig["decision_time"].isin(["3–5 minutes", "5–10 minutes", "Over 10 minutes"])
over5 = elig["decision_time"].isin(["5–10 minutes", "Over 10 minutes"])
over10 = elig["decision_time"].isin(["Over 10 minutes"])
results["C2_friction"] = {
    "decision_time_distribution": dt_dist,
    "n_over_3min": int(over3.sum()), "d_time": N_PRE, "pct_over_3min": pct(over3.sum(), N_PRE),
    "n_over_5min": int(over5.sum()), "pct_over_5min": pct(over5.sum(), N_PRE),
    "n_over_10min": int(over10.sum()), "pct_over_10min": pct(over10.sum(), N_PRE),
    "meal_pct_over_mean": round(elig["meal_pct_over"].mean(), 2),
    "meal_pct_over_median": float(elig["meal_pct_over"].median()),
}

# ------------------------------------------------------------- C3 abandon
gu_dist = counts(elig["giveup_freq"])
gu_at_least_once = elig["giveup_freq"].isin(["Once or twice", "A few times", "Often"])
gu_chronic = elig["giveup_freq"].isin(["Often"])
know_dist = counts(elig["know_what_want"])
already_know = elig["know_what_want"].isin(["I usually already know"])
results["C3_abandonment"] = {
    "giveup_freq_distribution": gu_dist,
    "n_gave_up_at_least_once": int(gu_at_least_once.sum()), "d": N_PRE,
    "pct_gave_up_at_least_once": pct(gu_at_least_once.sum(), N_PRE),
    "n_chronic_often": int(gu_chronic.sum()), "pct_chronic_often": pct(gu_chronic.sum(), N_PRE),
    "falsifier_distribution": know_dist,
    "n_already_know": int(already_know.sum()), "pct_already_know": pct(already_know.sum(), N_PRE),
}

# ------------------------------------------------------------- C4 leak
action_dist = counts(elig["action_when_dragged"])
off_platform_labels = ["Switched to YouTube", "Scrolled social media instead", "Switched to another app"]
on_platform_labels = ["Put on an old favourite", "Watched something on it anyway"]
off_platform = elig["action_when_dragged"].isin(off_platform_labels)
results["C4_leak"] = {
    "action_distribution": action_dist,
    "n_off_platform": int(off_platform.sum()), "d": N_PRE,
    "pct_off_platform": pct(off_platform.sum(), N_PRE),
    "n_youtube": action_dist.get("Switched to YouTube", 0),
    "off_platform_labels": off_platform_labels, "on_platform_labels": on_platform_labels,
    "note": "Asked to all eligible respondents, framed as 'the last time deciding dragged' — "
            "presupposes a drag event rather than being gated on C3 abandonment.",
}

# ------------------------------------------------------------- C5 severity
ann = elig["annoyance"].astype(float)
top_box = ann >= 7
results["C5_severity"] = {
    "mean": round(ann.mean(), 2), "median": float(ann.median()), "std": round(ann.std(), 2),
    "distribution": counts(elig["annoyance"].astype(int)),
    "n_top_box_7plus": int(top_box.sum()), "d": N_PRE, "pct_top_box_7plus": pct(top_box.sum(), N_PRE),
}

# ------------------------------------------------------- solution validation
noticed = post["noticed_row"].isin(["Yes"])
speed_dist = counts(post["perceived_speed"])
faster = post["perceived_speed"].isin(["Faster", "Much faster"])
start_dist = counts(post["start_intention"])
would_start = post["start_intention"].isin(["Started easily", "Started eventually"])
started_easily = post["start_intention"].isin(["Started easily"])
struggle_dist = counts(post["reduced_struggle"])
reduced = post["reduced_struggle"].isin(["Yes, clearly", "Somewhat"])
reduced_clearly = post["reduced_struggle"].isin(["Yes, clearly"])
stay_dist = counts(post["stay_on_netflix"])
stay = post["stay_on_netflix"].isin(["Yes", "Maybe"])
guardrail_dist = counts(post["guardrail_already_seen"])
lik = post["likelihood_use_next"].astype(float)
top_box_lik = lik >= 8
taste = post["taste_match"].astype(float)

results["solution_validation"] = {
    "noticed_row": {"n": int(noticed.sum()), "d": N_POST, "pct": pct(noticed.sum(), N_POST),
                     "distribution": counts(post["noticed_row"])},
    "perceived_speed": {"distribution": speed_dist, "n_faster": int(faster.sum()), "d": N_POST,
                         "pct_faster": pct(faster.sum(), N_POST)},
    "start_intention": {"distribution": start_dist, "n_would_start": int(would_start.sum()), "d": N_POST,
                         "pct_would_start": pct(would_start.sum(), N_POST),
                         "n_started_easily": int(started_easily.sum()),
                         "pct_started_easily": pct(started_easily.sum(), N_POST)},
    "reduced_struggle": {"distribution": struggle_dist, "n_reduced": int(reduced.sum()), "d": N_POST,
                          "pct_reduced": pct(reduced.sum(), N_POST),
                          "n_reduced_clearly": int(reduced_clearly.sum()),
                          "pct_reduced_clearly": pct(reduced_clearly.sum(), N_POST)},
    "stay_on_netflix": {"distribution": stay_dist, "n_stay": int(stay.sum()), "d": N_POST,
                         "pct_stay": pct(stay.sum(), N_POST)},
    "taste_match": {"mean": round(taste.mean(), 2), "median": float(taste.median()),
                     "std": round(taste.std(), 2), "distribution": counts(post["taste_match"].astype(int)),
                     "note": "Range 3-5 in current export; NOT a degenerate/default-value column here "
                             "(prior PDF report flagged this item as unusable — contradicted by current data)."},
    "guardrail_already_seen": {"distribution": guardrail_dist, "d": N_POST,
                                "n_missing": int(post["guardrail_already_seen"].isna().sum())},
    "likelihood_use_next": {"mean": round(lik.mean(), 2), "median": float(lik.median()),
                             "distribution": counts(post["likelihood_use_next"].astype(int)),
                             "n_top_box_8plus": int(top_box_lik.sum()), "d": N_POST,
                             "pct_top_box_8plus": pct(top_box_lik.sum(), N_POST)},
}

# feature components (multi-select ;-delimited)
comp_counts = {}
for row in post["useful_components"].dropna():
    for part in str(row).split(";"):
        part = part.strip()
        comp_counts[part] = comp_counts.get(part, 0) + 1
results["solution_validation"]["useful_components"] = {"counts": comp_counts, "d": N_POST,
                                                         "pct": {k: pct(v, N_POST) for k, v in comp_counts.items()}}

# devices (multi-select) on pre
dev_counts = {}
for row in elig["devices"].dropna():
    for part in str(row).split(";"):
        part = part.strip()
        dev_counts[part] = dev_counts.get(part, 0) + 1
results["C1_occasion"]["device_counts"] = dev_counts

# ------------------------------------------------------- guardrail deep dive
gr = post["guardrail_already_seen"]
results["guardrail"] = {
    "valid_responses_n": int(gr.notna().sum()),
    "missing_n": int(gr.isna().sum()),
    "d": N_POST,
    "distribution": counts(gr),
    "already_skip_option_present_in_data": bool(gr.isin(["Mostly things I'd already skip",
                                                          "Mostly already-seen"]).any()),
}

# --------------------------------------------------- matched pre-post work
m = matched
m["decision_time_over3"] = m["decision_time"].isin(["3–5 minutes", "5–10 minutes", "Over 10 minutes"])
m["speed_faster"] = m["perceived_speed"].isin(["Faster", "Much faster"])
t1 = pd.crosstab(m["decision_time_over3"], m["speed_faster"])
results["matched_1_friction_vs_speed"] = {
    "n": N_MATCH,
    "transition_matrix": t1.to_dict(orient="index"),  # {row_value: {col_value: count}}
    "note": "Pre 'spent >3 min deciding' (rows) vs post 'perceived row as faster/much faster' (cols). "
            "Proxy comparison: different measurement instruments (behavioural recall vs stated perception) "
            "on the same respondents, not a repeated identical metric.",
}

m["gave_up_often"] = m["giveup_freq"].isin(["Often"])
m["gave_up_ever"] = m["giveup_freq"].isin(["Once or twice", "A few times", "Often"])
m["would_start"] = m["start_intention"].isin(["Started easily", "Started eventually"])
t2a = pd.crosstab(m["gave_up_often"], m["would_start"])
t2b = pd.crosstab(m["gave_up_ever"], m["would_start"])
results["matched_2_abandonment_vs_start"] = {
    "n": N_MATCH,
    "chronic_abandoners_transition": t2a.to_dict(orient="index"),
    "chronic_abandoners_n": int(m["gave_up_often"].sum()),
    "any_abandoners_transition": t2b.to_dict(orient="index"),
    "any_abandoners_n": int(m["gave_up_ever"].sum()),
}

m["off_platform_pre"] = m["action_when_dragged"].isin(off_platform_labels)
m["stay_post"] = m["stay_on_netflix"].isin(["Yes", "Maybe"])
t3 = pd.crosstab(m["off_platform_pre"], m["stay_post"])
leak_n = int(m["off_platform_pre"].sum())
leak_would_stay = int((m["off_platform_pre"] & m["stay_post"]).sum())
results["matched_3_leak_vs_retention"] = {
    "n": N_MATCH,
    "transition_matrix": t3.to_dict(orient="index"),  # {row_value: {col_value: count}}
    "off_platform_pre_n": leak_n,
    "off_platform_pre_would_stay_n": leak_would_stay,
    "off_platform_pre_would_stay_pct": pct(leak_would_stay, leak_n),
}

seg = m.groupby("know_what_want")["likelihood_use_next"].agg(["mean", "median", "count"]).round(2)
results["matched_4_problem_status_vs_likelihood"] = {
    "n": N_MATCH,
    "by_segment": seg.reset_index().to_dict(orient="records"),
}

corr = m[["annoyance", "likelihood_use_next"]].astype(float).corr().iloc[0, 1]
results["matched_4b_annoyance_vs_likelihood_corr"] = round(float(corr), 3)

# device-level (primary device = first listed) where sample allows
m["primary_device"] = m["devices"].astype(str).str.split(";").str[0]
dev_seg = m.groupby("primary_device")["likelihood_use_next"].agg(["mean", "count"]).round(2)
results["matched_5_device_level"] = {
    "by_primary_device": dev_seg.reset_index().to_dict(orient="records"),
    "note": "Descriptive only; several cells n<5, not tested for significance.",
}

# ---------------------------------------------------- reversal cells (n small, report as-is)
results["reversal_C3"] = {
    "definition": "Among matched respondents who reported giving up 'Often' pre-survey, "
                   "share who said they would have started (easily/eventually) post-prototype.",
    "n_denominator": int(m["gave_up_often"].sum()),
    "n_would_start": int((m["gave_up_often"] & m["would_start"]).sum()),
}
results["reversal_C4"] = {
    "definition": "Among matched respondents who reported an off-platform leak pre-survey, "
                   "share who said they'd stay on Netflix (yes/maybe) post-prototype.",
    "n_denominator": leak_n,
    "n_would_stay": leak_would_stay,
    "pct_would_stay": pct(leak_would_stay, leak_n),
}

# ------------------------------------------------------------ qualitative
def clean_text(s):
    if pd.isna(s):
        return None
    s = str(s).strip()
    if s.lower() in {"-", "n/a", "na", "idk", "nothing", "no", ""}:
        return None
    return s

pre_open = [clean_text(x) for x in elig["open_giveup_story"]]
pre_open = [x for x in pre_open if x]
post_thing = [clean_text(x) for x in post["open_one_thing"]]
post_thing = [x for x in post_thing if x]
post_confuse = [clean_text(x) for x in post["open_confusion"]]
post_confuse = [x for x in post_confuse if x]

results["qualitative_raw_counts"] = {
    "pre_giveup_story_answered": len(pre_open), "pre_d": N_PRE,
    "post_one_thing_answered": len(post_thing), "post_d": N_POST,
    "post_confusion_answered": len(post_confuse), "post_confusion_blank_or_none": N_POST - len(post_confuse),
}
results["qualitative_texts"] = {
    "pre_giveup_story": pre_open,
    "post_one_thing": post_thing,
    "post_confusion": post_confuse,
}

OUT.joinpath("results.json").write_text(json.dumps(results, indent=2, default=str), encoding="utf-8")
print(json.dumps({k: v for k, v in results.items() if k not in ("qualitative_texts",)}, indent=2, default=str)[:3000])
print("\n\nWrote results.json, clean_pre.csv, clean_post.csv, matched.csv to", OUT)
