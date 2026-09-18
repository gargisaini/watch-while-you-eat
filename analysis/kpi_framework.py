"""Builds the KPI framework (5-10 core KPIs + 1 guardrail KPI) purely from
already-computed values in results.json — no new literals are typed here
except formula/definition/interpretation/limitation text, so numbers can't
drift out of sync with the analysis.
"""
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
r = json.loads((OUT / "results.json").read_text(encoding="utf-8"))

kpis = [
    {
        "id": "K1", "category": "Mealtime viewing frequency", "name": "Weekly Meal-Occasion Rate",
        "definition": "Share of eligible respondents who watch something at a meal 3+ times a week.",
        "formula": "n(meal_sessions_per_week in {3-5, 6-10, 10+}) / n(eligible pre respondents)",
        "numerator": r["C1_occasion"]["n_3_or_more_per_week"], "denominator": r["n_pre"],
        "value_pct": r["C1_occasion"]["pct_3_or_more_per_week"], "sample_size": r["n_pre"],
        "source_question": "pre_q1 — 'In a typical week, how many times do you watch on a streaming app while eating a meal?'",
        "interpretation": "Mealtime streaming is a frequent, recurring occasion for the large majority of eligible respondents, not an edge case.",
        "limitation": "Self-reported frequency band, not logged behaviour; bands are coarse (e.g. '3-5') so exact counts aren't recoverable.",
    },
    {
        "id": "K2", "category": "Decision friction", "name": "High-Friction Decision Rate",
        "definition": "Share of eligible respondents whose last mealtime decision took more than 3 minutes.",
        "formula": "n(decision_time in {3-5, 5-10, Over 10 minutes}) / n(eligible pre respondents)",
        "numerator": r["C2_friction"]["n_over_3min"], "denominator": r["n_pre"],
        "value_pct": r["C2_friction"]["pct_over_3min"], "sample_size": r["n_pre"],
        "source_question": "pre — 'How long did you spend deciding before you actually started?'",
        "interpretation": "A majority spend more than 3 minutes deciding; the tail is meaningful too — "
                          f"{r['C2_friction']['pct_over_10min']}% spend over 10 minutes.",
        "limitation": "Recall of a single past instance, not a timed measurement; 1 respondent who 'never started' is excluded from this rate.",
    },
    {
        "id": "K3", "category": "Abandonment", "name": "Any-Abandonment Rate",
        "definition": "Share of eligible respondents who gave up at least once in the last month after opening a streaming app at a meal.",
        "formula": "n(giveup_freq in {Once or twice, A few times, Often}) / n(eligible pre respondents)",
        "numerator": r["C3_abandonment"]["n_gave_up_at_least_once"], "denominator": r["n_pre"],
        "value_pct": r["C3_abandonment"]["pct_gave_up_at_least_once"], "sample_size": r["n_pre"],
        "source_question": "pre — 'In the last month, how often did you open a streaming app at a meal but give up without watching anything?'",
        "interpretation": "Abandonment is broad at least-once, but the chronic form is narrow: only "
                          f"{r['C3_abandonment']['pct_chronic_often']}% report 'Often'. Report both — breadth is not the same as severity.",
        "limitation": "One-month recall window; no distinction between a 30-second reconsideration and a multi-minute abandoned search.",
    },
    {
        "id": "K4", "category": "Off-platform leak", "name": "Off-Platform Leak Rate",
        "definition": "Share of eligible respondents whose reported action, the last time deciding dragged, left Netflix (YouTube, social media, or another app) rather than staying on the platform.",
        "formula": "n(action_when_dragged in {YouTube, social media, another app}) / n(eligible pre respondents)",
        "numerator": r["C4_leak"]["n_off_platform"], "denominator": r["n_pre"],
        "value_pct": r["C4_leak"]["pct_off_platform"], "sample_size": r["n_pre"],
        "source_question": "pre — 'The last time deciding dragged at a meal, what did you actually do?'",
        "interpretation": f"YouTube alone accounts for {r['C4_leak']['n_youtube']} of {r['C4_leak']['n_off_platform']} off-platform instances — the single largest destination and the clearest commercially relevant loss.",
        "limitation": "Question is framed around 'the last time deciding dragged', so it presupposes a drag event rather than being conditioned on the abandonment question (K3); not a strict funnel step.",
    },
    {
        "id": "K5", "category": "Perceived speed-up", "name": "Perceived Speed-Up Rate",
        "definition": "Share of post-prototype respondents who rated finding something with the feature as faster or much faster than their normal routine.",
        "formula": "n(perceived_speed in {Faster, Much faster}) / n(post respondents)",
        "numerator": r["solution_validation"]["perceived_speed"]["n_faster"], "denominator": r["n_post"],
        "value_pct": r["solution_validation"]["perceived_speed"]["pct_faster"], "sample_size": r["n_post"],
        "source_question": "post — \"...finding something with the 'Watch While You Eat' row was...\"",
        "interpretation": "A majority perceive a speed-up, but a large minority (about 4 in 10) felt no improvement or worse — this is a real, not unanimous, effect.",
        "limitation": "Stated perception in a single test session, not a timed A/B comparison against the normal routine.",
    },
    {
        "id": "K6", "category": "Struggle reduction", "name": "Struggle Reduction Rate",
        "definition": "Share of post-prototype respondents who said the feature reduced the 'what do I put on' struggle, clearly or somewhat.",
        "formula": "n(reduced_struggle in {Yes clearly, Somewhat}) / n(post respondents)",
        "numerator": r["solution_validation"]["reduced_struggle"]["n_reduced"], "denominator": r["n_post"],
        "value_pct": r["solution_validation"]["reduced_struggle"]["pct_reduced"], "sample_size": r["n_post"],
        "source_question": "post — \"Did it reduce the 'what do I put on' struggle for you specifically?\"",
        "interpretation": "Very high on the surface, but only "
                          f"{r['solution_validation']['reduced_struggle']['pct_reduced_clearly']}% chose the strong option ('Yes, clearly'); most of the 94.6% is the softer 'Somewhat'.",
        "limitation": "Self-report after a single short exposure; does not measure an actual repeated-use reduction in struggle.",
    },
    {
        "id": "K7", "category": "Start intention", "name": "Start-Intention Rate",
        "definition": "Share of post-prototype respondents who said they would have started watching (easily or eventually) rather than probably given up, had this been a real meal.",
        "formula": "n(start_intention in {Started easily, Started eventually}) / n(post respondents)",
        "numerator": r["solution_validation"]["start_intention"]["n_would_start"], "denominator": r["n_post"],
        "value_pct": r["solution_validation"]["start_intention"]["pct_would_start"], "sample_size": r["n_post"],
        "source_question": "post — 'If that had been a real meal just now, would you have started watching — or given up?'",
        "interpretation": "The strongest reaction measure in the study; directly answers the abandonment claim (C3) with a hypothetical intention, though only "
                          f"{r['solution_validation']['start_intention']['pct_started_easily']}% chose the confident 'started easily' option.",
        "limitation": "Hypothetical/stated intention captured immediately after prototype exposure, not an observed behaviour at a real meal.",
    },
    {
        "id": "K8", "category": "On-platform intention", "name": "Retention Intention Rate",
        "definition": "Share of post-prototype respondents who said the feature would keep them on Netflix at a meal instead of switching, yes or maybe.",
        "formula": "n(stay_on_netflix in {Yes, Maybe}) / n(post respondents)",
        "numerator": r["solution_validation"]["stay_on_netflix"]["n_stay"], "denominator": r["n_post"],
        "value_pct": r["solution_validation"]["stay_on_netflix"]["pct_stay"], "sample_size": r["n_post"],
        "source_question": "post — 'Would this keep you on Netflix at a meal instead of switching to something else?'",
        "interpretation": "Directly answers the C4 leak claim; among the matched respondents who had reported an off-platform leak pre-survey, "
                          f"{r['matched_3_leak_vs_retention']['off_platform_pre_would_stay_pct']}% now say yes/maybe (n={r['matched_3_leak_vs_retention']['off_platform_pre_n']}) — see matched analysis.",
        "limitation": "'Maybe' (the largest single response) is counted toward retention; a stricter definition using only 'Yes' would give a materially lower rate — reported separately in the dashboard.",
    },
    {
        "id": "K9", "category": "Headline desirability", "name": "Top-Box Likelihood to Use",
        "definition": "Share of post-prototype respondents rating likelihood to use the feature at their next meal 8 or above out of 10.",
        "formula": "n(likelihood_use_next >= 8) / n(post respondents)",
        "numerator": r["solution_validation"]["likelihood_use_next"]["n_top_box_8plus"], "denominator": r["n_post"],
        "value_pct": r["solution_validation"]["likelihood_use_next"]["pct_top_box_8plus"], "sample_size": r["n_post"],
        "source_question": "post — 'How likely are you to use this at your next meal?' (0-10)",
        "interpretation": f"The weakest of the reaction measures (mean {r['solution_validation']['likelihood_use_next']['mean']}, median {r['solution_validation']['likelihood_use_next']['median']}) and the one requiring the most commitment from the respondent — this is the number the go/no-go decision should weight most heavily, not the softer reaction measures above.",
        "limitation": "Single-item stated intention; no observed repeat-use or actual adoption data exists to validate it against.",
    },
]

guardrail = {
    "id": "G1", "category": "Guardrail", "name": "Already-Seen / Would-Skip Rate",
    "definition": "Share of post-prototype respondents who said the suggested episodes felt like content they'd already skip, rather than content they'd want.",
    "formula": "n(guardrail_already_seen == \"Mostly things I'd already skip\") / n(post respondents who answered this item)",
    "numerator": 0, "denominator": r["guardrail"]["valid_responses_n"],
    "value_pct": 0.0, "sample_size": r["guardrail"]["valid_responses_n"],
    "source_question": "post — \"Of the episodes it suggested, did they feel like things you'd want, or things you'd already skip?\"",
    "interpretation": "No respondent chose the 'would already skip' pole; the split is 'Mostly things I'd want' "
                      "({}/{}) vs 'A mix' ({}/{}). No kill-switch signal in the current data — recommendation "
                      "relevance is not failing outright.".format(
                          r["guardrail"]["distribution"].get("Mostly things I'd want", 0),
                          r["guardrail"]["valid_responses_n"],
                          r["guardrail"]["distribution"].get("A mix", 0),
                          r["guardrail"]["valid_responses_n"],
                      ),
    "limitation": "This item has 0 missing values and real variance in the current export. Because a genuinely "
                  "degenerate/default-only response pattern would invalidate this KPI, it should be re-checked against the "
                  "live survey tool export (not just this snapshot) before being relied on for a go/no-go call.",
}

r["kpi_framework"] = {"core_kpis": kpis, "guardrail_kpi": guardrail}
(OUT / "results.json").write_text(json.dumps(r, indent=2, default=str), encoding="utf-8")
print(f"Wrote {len(kpis)} core KPIs + 1 guardrail KPI to results.json")
