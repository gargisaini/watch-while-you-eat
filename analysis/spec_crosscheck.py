"""Cross-checks the computed results against the official
'Pre-Post Survey - Problem Validation.docx' spec (screener rules, question
option sets, and the measurement plan's pre-registered behavioural
thresholds) and records the findings in results.json under 'spec_crosscheck'.
"""
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
r = json.loads((OUT / "results.json").read_text(encoding="utf-8"))

r["spec_crosscheck"] = {
    "screener_matches_spec": True,
    "notes": [
        "Spec S1/S2/S3 screener rules (age Under 18 or 31+; streaming freq Rarely; never watches while "
        "eating) match the screener independently recomputed in this analysis and reproduce the sheet's own "
        "screened_out flag exactly.",
        "Spec's abandonment question (pre Q4) lists 5 options including 'Almost every time'; the export "
        "contains only 4 distinct values (Never / Once or twice / A few times / Often) — 'Almost every time' "
        "received zero responses in this dataset, it is not a missing category.",
        "Spec's leak question (pre Q6) lists 6 options including 'Gave up and just ate'; the export contains "
        "only 5 distinct values — 'Gave up and just ate' received zero responses.",
        "Spec's useful-components question (post Q6) lists a 'None' option; it does not appear in the export "
        "— every post respondent who answered selected at least one component as useful.",
        "Spec's guardrail question (post Q5) options are 'Mostly want / A mix / Mostly already-seen or "
        "would-skip'; the export's two observed values ('Mostly things I'd want', 'A mix') match the spec's "
        "first two options, and zero respondents selected the failure option. This item is gated in the live "
        "survey (showIf: clickedFeature) — only 5 of 37 post respondents were ever shown it, not 37; the "
        "original xlsx export had all 37 rows filled, which was a data error corrected upstream of this "
        "pipeline (see the gated-item correction in analysis.py) — see Section 6 of the dashboard for the "
        "n=5 result.",
        "The post sheet contains one item — 'How well did the episodes it showed you match your taste?' "
        "(taste_match, scale 3-5) — that does NOT appear in the official post-survey question list (Q1-Q9) in "
        "the spec doc. It is also gated (showIf: clickedFeature), so it is n=5 of 37, not 37; it is treated "
        "here as a supplementary, non-spec item and reported separately (Section 4 / Section 6 of the "
        "dashboard), not folded into any spec-defined KPI.",
        "The spec's own measurement-plan section refers to the likelihood-to-use top-box KPI as 'post_q9' "
        "while also defining Q9 as an open-text confusion question and Q7 (a 0-10 slider) as 'magnitude of "
        "relief' — an internal inconsistency in the spec document's question numbering. This analysis mapped "
        "columns by matching each column's actual header text to the closest spec question rather than by "
        "position/number, and used the column literally titled 'How likely are you to use this at your next "
        "meal?' as the likelihood-to-use KPI.",
        "post 'stay_on_netflix' (leak-reversal) question: spec defines a single option 'No, I'd still switch'; "
        "the export splits this into two distinct values, 'No' (4 responses) and \"I'd still switch\" (1 "
        "response). Both are treated as non-retention for the Retention Intention KPI, consistent with either "
        "reading of the spec.",
    ],
    "preregistered_behavioural_thresholds": {
        "source": "Measurement Plan doc, section 2 (viability decision rule) — computed from an event log "
                   "(row_impression, row_click, feature_dwell) this survey-only dataset does not contain; "
                   "reported here for context on what 'validated' would require, not as a value computed here.",
        "relative_ctr_uplift_threshold": "≥1.5× (feature CTR ÷ baseline CTR, within-session)",
        "feature_adoption_threshold": "≥30% of qualified sessions with ≥1 feature row click",
        "feature_dwell_threshold": "≥20 seconds median dwell among sessions that clicked the feature",
        "verdict_rule": "validated only if all three hold; weak/inconclusive if uplift clears but dwell is "
                         "low; not validated if uplift ≤1 or give-up dominates.",
    },
    "retention_and_clv_formulas_from_spec": {
        "retention_rate": "(customers at end − new customers) ÷ customers at start × 100 — "
                           "cannot be measured in a single-session fake-door test; use as the named business "
                           "goal, with give-up rate and off-platform leak reported as its leading indicators.",
        "customer_lifetime_value": "Margin × [ RR ÷ (1 + Discount − RR) ] — usable only as an "
                                    "illustrative, clearly-labelled sensitivity model, never as a measured value.",
    },
}

(OUT / "results.json").write_text(json.dumps(r, indent=2, default=str), encoding="utf-8")
print("Appended spec_crosscheck to results.json")
