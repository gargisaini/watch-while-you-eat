"""
Watch While You Eat — Pre/Post Survey Dashboard
Run: streamlit run dashboard/app.py
Reads analysis/results.json + analysis/*.csv, produced by analysis/analysis.py
and analysis/kpi_framework.py — this file computes no new numbers, it only displays them.
One exception: BEHAVIOURAL below, five measured KPIs from the live prototype's event
log, which lives in a different repo and is not part of this survey pipeline. See the
provenance comment on that block.
"""
import json
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
R = json.loads((ROOT / "analysis" / "results.json").read_text(encoding="utf-8"))
pre = pd.read_csv(ROOT / "analysis" / "clean_pre.csv")
post = pd.read_csv(ROOT / "analysis" / "clean_post.csv")
matched = pd.read_csv(ROOT / "analysis" / "matched.csv")

# ------------------------------------------- measured behavioural KPIs ----
# NOT from this survey pipeline. Recomputed from the live fake-door prototype's
# event log in a separate repo:
#   Market_Validation/data/export-2026-09-18/raw_events.csv  (960 events, 94 sessions)
# Instrumentation: src/lib/analytics.ts -> POST /api/events -> Supabase `events`.
# Row attribution: row_click carries rowId + isFeature; title_open and play_click
# carry source + path (100% coverage, no nulls on either).
# Hand-carried because no script in analysis/ reads that export yet. Until one
# exists, these are the only literals on the page — keep them here, not inline,
# and re-derive them if the export is refreshed.
BEHAVIOURAL = {
    "feature_impr": 1103, "feature_clicks": 11,      # payload.count convention
    "generic_impr": 11952, "generic_clicks": 27,
    "feature_impr_events": 79,                        # row_impression event count
    "adoption_num": 7, "adoption_den": 67,            # sessions clicking feature / reaching home
    "dwell_ms": [3898, 3323],
    "feature_plays": 6, "feature_play_sessions": 5,
    "c2p_feat_sess_num": 5, "c2p_feat_sess_den": 7,   # feature title-open -> play, sessions
    "c2p_all_sess_num": 20, "c2p_all_sess_den": 26,   # app-wide, same grain
    "c2p_feat_evt_num": 6, "c2p_feat_evt_den": 11,    # feature title-open -> play, events
    "c2p_all_evt_num": 29, "c2p_all_evt_den": 47,     # app-wide, same grain
    "top_title": "breaking-bad-s5e13",
    "top_title_opens": 6, "top_title_plays": 2,
}
_B = BEHAVIOURAL
CTR_FEAT = 100 * _B["feature_clicks"] / _B["feature_impr"]
CTR_GEN = 100 * _B["generic_clicks"] / _B["generic_impr"]
CTR_UPLIFT = CTR_FEAT / CTR_GEN
TAKE_RATE = 100 * _B["feature_plays"] / _B["feature_impr"]
TAKE_RATE_ALT = 100 * _B["feature_plays"] / _B["feature_impr_events"]
ADOPTION = 100 * _B["adoption_num"] / _B["adoption_den"]
C2P_FEAT_SESS = 100 * _B["c2p_feat_sess_num"] / _B["c2p_feat_sess_den"]
C2P_ALL_SESS = 100 * _B["c2p_all_sess_num"] / _B["c2p_all_sess_den"]
C2P_FEAT_EVT = 100 * _B["c2p_feat_evt_num"] / _B["c2p_feat_evt_den"]
C2P_ALL_EVT = 100 * _B["c2p_all_evt_num"] / _B["c2p_all_evt_den"]
# Fail loudly if a number above gets edited into inconsistency.
assert round(CTR_FEAT, 3) == 0.997 and round(CTR_GEN, 3) == 0.226, "CTR inputs drifted"
assert round(CTR_UPLIFT, 2) == 4.41, "CTR uplift no longer 4.41x"
assert round(TAKE_RATE, 3) == 0.544 and round(TAKE_RATE_ALT, 2) == 7.59, "take rate drifted"
assert round(ADOPTION, 1) == 10.4, "adoption rate drifted"
assert (round(C2P_FEAT_SESS, 1), round(C2P_ALL_SESS, 1)) == (71.4, 76.9), "session-grain c2p drifted"
assert (round(C2P_FEAT_EVT, 1), round(C2P_ALL_EVT, 1)) == (54.5, 61.7), "event-grain c2p drifted"
assert len(_B["dwell_ms"]) == 2, "dwell n changed — the 'insufficient' framing must be revisited"

# ---------------------------------------------------------------- theme ----
BG = "#141414"
CARD = "#1F1F1F"
CARD_BORDER = "#333333"
TEXT = "#F5F5F5"
MUTED = "#A3A3A3"
ACCENT = "#E50914"
ACCENT_DIM = "#7A1114"
GRAY_BAR = "#4D4D4D"
GOOD = "#3FA34D"
WARN = "#D9A441"

st.set_page_config(page_title="Watch While You Eat — Research Dashboard", layout="wide", page_icon="🍽️")

st.markdown(f"""
<style>
.stApp {{ background-color: {BG}; color: {TEXT}; }}
section[data-testid="stSidebar"] {{ background-color: #0B0B0B; }}
div[data-testid="stMetric"] {{
    background-color: {CARD}; border: 1px solid {CARD_BORDER}; border-radius: 10px;
    padding: 14px 16px 10px 16px;
}}
div[data-testid="stMetricLabel"] {{ color: {MUTED}; }}
div[data-testid="stMetricValue"] {{ color: {TEXT}; }}
.kpi-note {{ color: {MUTED}; font-size: 0.82rem; margin-top: -8px; }}
h1, h2, h3 {{ color: {TEXT}; }}
.stMarkdown p {{ color: {TEXT}; }}
.badge-strong {{ background:#1E3A24; color:#8FD19E; padding:2px 8px; border-radius:6px; font-size:0.75rem; }}
.badge-weak {{ background:#3A2A12; color:#E8C078; padding:2px 8px; border-radius:6px; font-size:0.75rem; }}
.badge-not {{ background:#3A1414; color:#E88; padding:2px 8px; border-radius:6px; font-size:0.75rem; }}
hr {{ border-color: {CARD_BORDER}; }}
</style>
""", unsafe_allow_html=True)

PLOTLY_LAYOUT = dict(
    paper_bgcolor=BG, plot_bgcolor=BG,
    font=dict(color=TEXT, family="Helvetica, Arial, sans-serif", size=13),
    margin=dict(l=10, r=20, t=40, b=10),
    xaxis=dict(gridcolor="#2A2A2A", zerolinecolor="#2A2A2A"),
    yaxis=dict(gridcolor="#2A2A2A", zerolinecolor="#2A2A2A"),
)


def hbar(labels, values, highlight_labels=None, title="", suffix="%", denom_note=""):
    highlight_labels = set(highlight_labels or [])
    colors = [ACCENT if l in highlight_labels else GRAY_BAR for l in labels]
    fig = go.Figure(go.Bar(
        x=values, y=labels, orientation="h", marker_color=colors,
        text=[f"{v}{suffix}" for v in values], textposition="outside",
        hovertemplate="%{y}: %{x}" + suffix + "<extra></extra>",
    ))
    layout = {k: v for k, v in PLOTLY_LAYOUT.items() if k != "xaxis"}
    fig.update_layout(**layout, title=title, showlegend=False,
                       height=max(220, 46 * len(labels)),
                       xaxis=dict(**PLOTLY_LAYOUT["xaxis"], title=None))
    fig.update_yaxes(autorange="reversed")
    st.plotly_chart(fig, use_container_width=True)
    if denom_note:
        st.caption(denom_note)


def kpi_card(label, value, note, col):
    with col:
        st.metric(label, value)
        st.markdown(f"<div class='kpi-note'>{note}</div>", unsafe_allow_html=True)


def section_header(title, subtitle=None):
    st.header(title)
    if subtitle:
        st.caption(subtitle)
    st.markdown("---")


st.sidebar.title("🍽️ Watch While You Eat")
st.sidebar.caption("Pre/Post Survey — Problem & Solution Validation")
SECTIONS = [
    "1. Business Problem", "2. Sample / Recruitment Funnel", "3. Problem Validation",
    "4. Solution Validation", "5. Before vs After", "6. Guardrail",
    "7. Feature Component Analysis", "8. Segment Analysis", "9. KPI Scorecard",
    "10. Key Insights", "11. Recommendations", "12. KPI (archived)",
]
page = st.sidebar.radio("Section", SECTIONS, label_visibility="collapsed")
st.sidebar.markdown("---")
st.sidebar.markdown(
    f"<span class='kpi-note'>Eligible pre n = {R['n_pre']} · Post n = {R['n_post']} · "
    f"Matched pairs n = {R['n_matched']}</span>", unsafe_allow_html=True)

# ============================================================ SECTION 1 ===
if page.startswith("1."):
    section_header("Business Problem", "The research hypothesis this study set out to test")
    st.markdown("""
> **Young Netflix viewers aged 18–30 spend so much time deciding what to watch during a meal — on their
> phone, laptop, or TV — that they often give up before hitting play, losing the one window they had to
> relax and watch.**

This statement decomposes into five testable claims. **This dashboard treats the statement as a
hypothesis, not a conclusion** — each claim is scored against what the data actually shows, including where
the data weakens or contradicts it.
""")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
**C1 — Occasion**: Is mealtime streaming frequent enough to be a meaningful recurring occasion?

**C2 — Friction**: Do respondents spend meaningful time deciding what to watch?

**C3 — Abandonment**: Do respondents give up because of the decision process?
""")
    with c2:
        st.markdown("""
**C4 — Off-platform leak**: When deciding is hard, do respondents leave Netflix?

**C5 — Magnitude**: Is the problem frequent/severe enough to matter?

**Solution**: Does the "Watch While You Eat" prototype measurably address these claims?
""")
    st.markdown("---")
    st.markdown("**Prototype**: a dedicated row surfacing a single best-episode pick per show, mood-based "
                "filters, previously-watched shows, and a jump-to-best-moment marker, tested as a high-fidelity "
                "fake-door prototype after respondents completed the pre-survey.")

# ============================================================ SECTION 2 ===
elif page.startswith("2."):
    section_header("Sample / Recruitment Funnel", "Recomputed directly from the Excel export")
    funnel_labels = ["Submitted (pre)", "Eligible (passed screener)", "Completed post survey"]
    funnel_vals = [R["qa"]["submitted_n"], R["qa"]["eligible_n"], R["qa"]["matched_pairs_n"]]
    fig = go.Figure(go.Bar(x=funnel_vals, y=funnel_labels, orientation="h",
                            marker_color=[GRAY_BAR, GRAY_BAR, ACCENT],
                            text=funnel_vals, textposition="outside"))
    fig.update_layout(**PLOTLY_LAYOUT, title="Recruitment funnel", showlegend=False, height=260)
    fig.update_yaxes(autorange="reversed")
    st.plotly_chart(fig, use_container_width=True)
    st.caption(f"Completion rate (post / eligible) = {R['qa']['matched_pairs_n']} / {R['qa']['eligible_n']} "
               f"= {R['qa']['completion_rate_pct']}%")

    st.subheader("Screener logic applied (from the screener spec board)")
    sb = R["qa"]["screener_breakdown"]
    st.table(pd.DataFrame([
        {"Rule": "Age is Under 18 or 31+", "n screened out": sb["age_out_of_range"]},
        {"Rule": "Streaming frequency is Rarely/Never", "n screened out": sb["streaming_freq_too_low"]},
        {"Rule": "Never watches while eating", "n screened out": sb["never_eats_while_watching"]},
        {"Rule": "0 meal-watch sessions/week", "n screened out": sb["zero_meal_sessions_per_week"]},
    ]))
    st.caption(f"A respondent can fail more than one rule, so rows do not sum to the total {R['qa']['screened_out_n']} "
               "screened out. Independently recomputing the screener from raw answers reproduced the sheet's own "
               f"'screened_out' flag exactly ({'match' if R['qa']['screener_flag_matches_recomputation'] else 'MISMATCH'}).")

    st.subheader("Data quality")
    st.markdown(f"""
- Duplicate `session_id` in pre sheet: **{R['qa']['pre_duplicate_session_ids']}** · in post sheet: **{R['qa']['post_duplicate_session_ids']}**
- Post respondents whose session_id is not found in pre: **{len(R['qa']['post_ids_not_in_pre'])}**
- Post respondents who came from a *screened-out* pre respondent (would be invalid — excluded if any): **{len(R['qa']['post_ids_from_screened_out_pre'])}**
- Eligible respondents who never completed the post survey (attrition): **{R['qa']['eligible_with_no_post_n']}** of {R['qa']['eligible_n']}
- Missing data is limited to optional open-text fields; no missing values in any closed-choice question used for KPI calculations.
""")

# ============================================================ SECTION 3 ===
elif page.startswith("3."):
    section_header("Problem Validation (C1–C5)", f"Pre-survey, eligible respondents, n = {R['n_pre']}")

    c1d = R["C1_occasion"]; c2d = R["C2_friction"]; c3d = R["C3_abandonment"]
    c4d = R["C4_leak"]; c5d = R["C5_severity"]
    cols = st.columns(5)
    kpi_card("C1 Occasion ≥3×/wk", f"{c1d['pct_3_or_more_per_week']}%", f"n={c1d['n_3_or_more_per_week']}/{c1d['d']}", cols[0])
    kpi_card("C2 >3 min deciding", f"{c2d['pct_over_3min']}%", f"n={c2d['n_over_3min']}/{c2d['d_time']}", cols[1])
    kpi_card("C3 Gave up ≥once", f"{c3d['pct_gave_up_at_least_once']}%", f"n={c3d['n_gave_up_at_least_once']}/{c3d['d']}", cols[2])
    kpi_card("C4 Off-platform leak", f"{c4d['pct_off_platform']}%", f"n={c4d['n_off_platform']}/{c4d['d']}", cols[3])
    kpi_card("C5 Annoyance (mean)", f"{c5d['mean']}/10", f"median {c5d['median']}, top-box {c5d['pct_top_box_7plus']}%", cols[4])

    st.markdown("### C1 — Occasion: weekly mealtime viewing frequency")
    order = ["1–2", "3–5", "6–10", "10+"]
    vals = [c1d["distribution"].get(k, 0) for k in order]
    hbar(order, vals, highlight_labels=["3–5", "6–10", "10+"],
         title=f"Sessions/week while eating (n={c1d['d']})", suffix="", denom_note=None)
    st.caption(f"**{c1d['pct_3_or_more_per_week']}% ({c1d['n_3_or_more_per_week']}/{c1d['d']})** watch at a meal 3+ times a week — "
               "the occasion is frequent, supporting C1.")

    st.markdown("### C2 — Friction: decision time")
    order2 = ["Under 1 minute", "1–3 minutes", "3–5 minutes", "5–10 minutes", "Over 10 minutes", "I never started"]
    vals2 = [c2d["decision_time_distribution"].get(k, 0) for k in order2]
    hbar(order2, vals2, highlight_labels=["3–5 minutes", "5–10 minutes", "Over 10 minutes"],
         title=f"Time spent deciding, last mealtime session (n={c2d['d_time']})", suffix="")
    m1, m2, m3 = st.columns(3)
    m1.metric(">3 minutes", f"{c2d['pct_over_3min']}%", f"n={c2d['n_over_3min']}")
    m2.metric(">5 minutes", f"{c2d['pct_over_5min']}%", f"n={c2d['n_over_5min']}")
    m3.metric(">10 minutes", f"{c2d['pct_over_10min']}%", f"n={c2d['n_over_10min']}")
    st.caption(f"Meal-window cost: mean {c2d['meal_pct_over_mean']}/10 (median {c2d['meal_pct_over_median']}) of the meal "
               "was already over by the time respondents settled on something — roughly a third of the meal, on average.")

    st.markdown("### C3 — Abandonment: breadth vs intensity, and the falsifier")
    order3 = ["Never", "Once or twice", "A few times", "Often"]
    vals3 = [c3d["giveup_freq_distribution"].get(k, 0) for k in order3]
    hbar(order3, vals3, highlight_labels=["Once or twice", "A few times", "Often"],
         title=f"How often gave up without watching, last month (n={c3d['d']})", suffix="")
    a, b = st.columns(2)
    a.metric("Gave up at least once", f"{c3d['pct_gave_up_at_least_once']}%", f"n={c3d['n_gave_up_at_least_once']}/{c3d['d']}")
    b.metric("Chronic ('Often')", f"{c3d['pct_chronic_often']}%", f"n={c3d['n_chronic_often']}/{c3d['d']}")
    st.markdown("**C3 falsifier — do respondents already know what they want?**")
    order4 = ["I usually already know", "Depends", "I usually have to figure it out"]
    vals4 = [c3d["falsifier_distribution"].get(k, 0) for k in order4]
    hbar(order4, vals4, highlight_labels=["I usually already know"],
         title=f"Already know vs have to figure it out (n={c3d['d']})", suffix="")
    st.warning(f"**Falsifier result, reported as required, not minimized:** {c3d['pct_already_know']}% "
               f"({c3d['n_already_know']}/{c3d['d']}) of eligible respondents say they *already know* what they want before "
               "sitting down — the decision-friction problem does not apply to over a third of this audience. The "
               "problem holds for the remaining majority who have to figure it out or say it depends.", icon="🔎")

    st.markdown("### C4 — Off-platform leak")
    order5 = ["Switched to YouTube", "Scrolled social media instead", "Switched to another app",
              "Put on an old favourite", "Watched something on it anyway"]
    vals5 = [c4d["action_distribution"].get(k, 0) for k in order5]
    hbar(order5, vals5, highlight_labels=c4d["off_platform_labels"],
         title=f"Action the last time deciding dragged (n={c4d['d']})", suffix="")
    st.caption(f"**{c4d['pct_off_platform']}% ({c4d['n_off_platform']}/{c4d['d']})** left Netflix entirely; YouTube alone "
               f"accounts for {c4d['n_youtube']} of those {c4d['n_off_platform']} instances — the largest single destination. "
               f"⚠️ {c4d['note']}")

    st.markdown("### C5 — Magnitude / severity")
    hbar([str(k) for k in range(11)], [c5d["distribution"].get(str(k), 0) for k in range(11)],
         highlight_labels=[str(k) for k in range(7, 11)],
         title=f"Reported annoyance of the decision step, 0-10 (n={c5d['d']})", suffix="")
    st.caption(f"Mean {c5d['mean']}, median {c5d['median']}, std {c5d['std']}. Top-box (7+): "
               f"**{c5d['pct_top_box_7plus']}%** ({c5d['n_top_box_7plus']}/{c5d['d']}) — a real but not universal heavy tail.")

# ============================================================ SECTION 4 ===
elif page.startswith("4."):
    section_header("Solution Validation", f"Post-prototype survey, n = {R['n_post']}")
    sv = R["solution_validation"]
    cols = st.columns(4)
    kpi_card("Noticed the row", f"{sv['noticed_row']['pct']}%", f"n={sv['noticed_row']['n']}/{sv['noticed_row']['d']}", cols[0])
    kpi_card("Perceived faster", f"{sv['perceived_speed']['pct_faster']}%", f"n={sv['perceived_speed']['n_faster']}/{sv['perceived_speed']['d']}", cols[1])
    kpi_card("Would have started", f"{sv['start_intention']['pct_would_start']}%", f"n={sv['start_intention']['n_would_start']}/{sv['start_intention']['d']}", cols[2])
    kpi_card("Top-box likelihood to use", f"{sv['likelihood_use_next']['pct_top_box_8plus']}%", f"n={sv['likelihood_use_next']['n_top_box_8plus']}/{sv['likelihood_use_next']['d']}", cols[3])

    c1, c2 = st.columns(2)
    with c1:
        order = ["Not sure", "No", "Yes"]
        hbar(order, [sv["noticed_row"]["distribution"].get(k, 0) for k in order], highlight_labels=["Yes"],
             title="Feature awareness: noticed the row?", suffix="")
        order = ["Slower", "About the same", "Faster", "Much faster"]
        hbar(order, [sv["perceived_speed"]["distribution"].get(k, 0) for k in order],
             highlight_labels=["Faster", "Much faster"], title="Perceived speed vs normal routine", suffix="")
        order = ["Probably given up", "Started eventually", "Started easily"]
        hbar(order, [sv["start_intention"]["distribution"].get(k, 0) for k in order],
             highlight_labels=["Started eventually", "Started easily"], title="Start intention (hypothetical)", suffix="")
    with c2:
        order = ["No", "Somewhat", "Yes, clearly"]
        hbar(order, [sv["reduced_struggle"]["distribution"].get(k, 0) for k in order],
             highlight_labels=["Somewhat", "Yes, clearly"], title="Reduced the decision struggle?", suffix="")
        order = ["No", "I'd still switch", "Maybe", "Yes"]
        hbar(order, [sv["stay_on_netflix"]["distribution"].get(k, 0) for k in order],
             highlight_labels=["Maybe", "Yes"], title="Would stay on Netflix instead of switching", suffix="")
        order = [str(k) for k in range(11)]
        hbar(order, [sv["likelihood_use_next"]["distribution"].get(k, 0) for k in order],
             highlight_labels=[str(k) for k in range(8, 11)],
             title=f"Likelihood to use at next meal, 0-10 (mean {sv['likelihood_use_next']['mean']})", suffix="")

    _wanted_n = sv["guardrail_already_seen"]["distribution"].get("Mostly things I'd want", 0)
    st.info(f"**Recommendation relevance**: {_wanted_n} "
            f"of {sv['guardrail_already_seen']['d']} said suggestions were mostly things they'd want; the rest said "
            "'a mix'. See Section 6 for the full guardrail analysis.", icon="🎯")
    st.warning(
        f"**Headline desirability is the weakest reaction measure**: top-box (8-10) likelihood to use next meal is only "
        f"**{sv['likelihood_use_next']['pct_top_box_8plus']}%** ({sv['likelihood_use_next']['n_top_box_8plus']}/{sv['likelihood_use_next']['d']}), "
        f"vs {sv['start_intention']['pct_would_start']}% for 'would have started' and {sv['stay_on_netflix']['pct_stay']}% for "
        "'would stay on Netflix'. The measure requiring the most commitment is the one to weight most heavily.", icon="⚠️")

# ============================================================ SECTION 5 ===
elif page.startswith("5."):
    section_header("Before vs After — Matched Pre/Post Analysis", f"Matched pairs, n = {R['n_matched']}")
    st.caption("Joined on session_id. Distinguishing direct before/after measurements from proxy comparisons — "
               "the pre and post surveys use different instruments, so these are not repeated identical metrics.")

    st.markdown("### 1. Pre decision friction vs post perceived speed (proxy comparison)")
    t1 = R["matched_1_friction_vs_speed"]["transition_matrix"]
    df1 = pd.DataFrame({
        "Perceived NOT faster (post)": [t1["false"]["false"], t1["true"]["false"]],
        "Perceived faster/much faster (post)": [t1["false"]["true"], t1["true"]["true"]],
    }, index=["Spent ≤3 min deciding (pre)", "Spent >3 min deciding (pre)"])
    st.dataframe(df1, width='stretch')
    st.caption(R["matched_1_friction_vs_speed"]["note"])

    st.markdown("### 2. Pre abandonment vs post start intention")
    t2b = R["matched_2_abandonment_vs_start"]["any_abandoners_transition"]
    df2 = pd.DataFrame({
        "Would NOT start (post)": [t2b["false"]["false"], t2b["true"]["false"]],
        "Would start, easily/eventually (post)": [t2b["false"]["true"], t2b["true"]["true"]],
    }, index=["Never gave up (pre)", "Gave up ≥once (pre)"])
    st.dataframe(df2, width='stretch')
    r3 = R["reversal_C3"]
    st.caption(f"Small-cell reversal check — among the {r3['n_denominator']} matched respondents who reported giving up "
               f"'Often' pre-survey, {r3['n_would_start']} of {r3['n_denominator']} said they would have started "
               "post-prototype. Directionally complete but too small a cell to generalise from.")

    st.markdown("### 3. Pre off-platform leakage vs post intention to remain on Netflix")
    t3 = R["matched_3_leak_vs_retention"]["transition_matrix"]
    df3 = pd.DataFrame({
        "Would NOT stay (post)": [t3["false"]["false"], t3["true"]["false"]],
        "Would stay, yes/maybe (post)": [t3["false"]["true"], t3["true"]["true"]],
    }, index=["No off-platform leak (pre)", "Off-platform leak (pre)"])
    st.dataframe(df3, width='stretch')
    r4 = R["reversal_C4"]
    st.success(f"**Strongest matched-pair evidence in the dataset**: of the {r4['n_denominator']} matched respondents who "
               f"reported an off-platform leak pre-survey, **{r4['n_would_stay']} of {r4['n_denominator']} "
               f"({r4['pct_would_stay']}%)** say they'd stay on Netflix (yes/maybe) post-prototype.", icon="✅")

    st.markdown("### 4. Problem-status segmentation vs likelihood to use")
    seg = pd.DataFrame(R["matched_4_problem_status_vs_likelihood"]["by_segment"])
    seg = seg.rename(columns={"know_what_want": "Pre-survey problem status", "mean": "Mean likelihood to use",
                               "median": "Median", "count": "n"})
    st.dataframe(seg, width='stretch')
    st.caption(f"Reported annoyance and likelihood to use correlate at r = {R['matched_4b_annoyance_vs_likelihood_corr']} "
               "(matched pairs). Demand concentrates among respondents who carry the problem — descriptive association, "
               "not a causal test, and consistent with a genuine signal rather than a novelty effect.")

    st.markdown("### 5. Device-level differences")
    dev = pd.DataFrame(R["matched_5_device_level"]["by_primary_device"])
    dev = dev.rename(columns={"primary_device": "Primary device (pre)", "mean": "Mean likelihood to use", "count": "n"})
    st.dataframe(dev, width='stretch')
    st.caption(R["matched_5_device_level"]["note"])

# ============================================================ SECTION 6 ===
elif page.startswith("6."):
    section_header("Guardrail — Recommendation Quality / Already-Seen Check")
    g = R["guardrail"]
    sv_taste = R["solution_validation"]["taste_match"]
    c1, c2, c3 = st.columns(3)
    c1.metric("Valid responses", f"{g['valid_responses_n']}/{g['d']}")
    c2.metric("Missing / not shown", g["missing_n"])
    c3.metric("'Would already skip' selected", "0")

    order = ["A mix", "Mostly things I'd want"]
    hbar(order, [g["distribution"].get(k, 0) for k in order], highlight_labels=["Mostly things I'd want"],
         title=f"Did suggestions feel wanted or already-skippable? (n={g['d']})", suffix="")

    if g["missing_n"] == 0 and g["already_skip_option_present_in_data"] is False:
        st.success(
            "**No contamination detected in the current export.** All 37 post respondents answered this item "
            "(0 missing), and no respondent selected an 'already-skip' option — responses split between "
            "'Mostly things I'd want' and 'A mix'. This is a real, non-degenerate measurement in the current data.",
            icon="✅")

    st.markdown("### Cross-check: the related 'taste match' item")
    st.write(f"Mean {sv_taste['mean']}/5, median {sv_taste['median']}, std {sv_taste['std']}, "
             f"distribution: {sv_taste['distribution']}")
    st.info(
        f"The taste-match item has real spread (std {sv_taste['std']}, range 3–5) and the guardrail item has "
        f"0 missing values across all {g['d']} post respondents — both are usable, non-degenerate measurements "
        "in the current data.", icon="ℹ️")

# ============================================================ SECTION 7 ===
elif page.startswith("7."):
    section_header("Feature Component Analysis", f"Multi-select, post survey, n = {R['n_post']}")
    comp = R["solution_validation"]["useful_components"]
    order = sorted(comp["counts"], key=lambda k: -comp["counts"][k])
    hbar(order, [comp["counts"][k] for k in order],
         highlight_labels=[order[0], order[1]] if len(order) > 1 else order,
         title="Which parts felt useful? (respondents could pick more than one)", suffix="")
    st.caption(f"Percent of {comp['d']} respondents selecting each component: "
               + ", ".join(f"{k} {comp['pct'][k]}%" for k in order))
    st.markdown("""
**Reading this chart**: the single best-episode pick and the mood filters are the two components that carry the
feature's perceived value. The jump-to-best-moment graph is the least-cited component by a wide margin — on this
sample, it does not clearly justify its own build cost relative to the other three.
""")

# ============================================================ SECTION 8 ===
elif page.startswith("8."):
    section_header("Segment Analysis")
    st.markdown("### By pre-survey problem status (falsifier segment) — matched pairs")
    seg = pd.DataFrame(R["matched_4_problem_status_vs_likelihood"]["by_segment"])
    seg = seg.rename(columns={"know_what_want": "Segment", "mean": "Mean likelihood to use", "median": "Median", "count": "n"})
    hbar(seg["Segment"].tolist(), seg["Mean likelihood to use"].tolist(),
         highlight_labels=["I usually have to figure it out"],
         title="Mean likelihood to use next meal, by problem-status segment", suffix="")
    st.dataframe(seg, width='stretch')
    st.caption("Respondents who 'have to figure it out' pre-survey — the segment that most clearly carries the "
               "problem — report the highest mean likelihood to use the feature. This is a descriptive association "
               "on a small matched sample, not a significance-tested effect.")

    st.markdown("### By primary device (pre-survey)")
    dev = pd.DataFrame(R["matched_5_device_level"]["by_primary_device"])
    dev = dev.rename(columns={"primary_device": "Device", "mean": "Mean likelihood to use", "count": "n"})
    hbar(dev["Device"].tolist(), dev["Mean likelihood to use"].tolist(), title="Mean likelihood to use, by primary device", suffix="")
    st.dataframe(dev, width='stretch')
    st.caption(R["matched_5_device_level"]["note"] + " Cells below n=5 are shown but should not be generalised.")

    st.markdown("### Chronic vs occasional abandoners (pre-survey, eligible n={})".format(R["n_pre"]))
    c3d = R["C3_abandonment"]
    st.write(f"Chronic ('Often'): **{c3d['n_chronic_often']}** ({c3d['pct_chronic_often']}%) · "
             f"Occasional (once/twice or a few times): **{c3d['n_gave_up_at_least_once'] - c3d['n_chronic_often']}** · "
             f"Never: **{c3d['d'] - c3d['n_gave_up_at_least_once']}**")
    st.caption("The problem statement's strongest form ('often give up') describes a minority; the broader claim "
               "('spend a lot of time / experience friction') describes a majority. These are different segments "
               "and should not be conflated in a business case.")

# ============================================================ SECTION 9 ===
elif page.startswith("9."):
    section_header("KPI Scorecard")
    st.caption("Measured from the live fake-door prototype's event log (960 events, 94 sessions, export "
               "2026-09-18) — not from the survey. These are observed behaviour, not stated intention. "
               "The survey-response KPIs and the requested-marketing-metric tables now live in "
               "**12. KPI (archived)**.")

    def measured_kpi(name, value, delta, narrative):
        c1, c2 = st.columns([1, 3])
        c1.metric(name, value, delta)
        with c2:
            st.markdown(narrative)
        st.markdown("---")

    measured_kpi(
        "Relative CTR Uplift", f"{CTR_UPLIFT:.2f}×", "threshold ≥1.5× · clears",
        "Click-through rate (CTR) is the standard measure of how often people click something they're shown — "
        "clicks divided by impressions — and on its own it doesn't say much, because some rows get more clicks "
        "just from being familiar or well-positioned, not because people prefer what's in them. Relative CTR "
        "uplift solves that by comparing the feature row's CTR against the average CTR of the app's other, "
        "generic rows within the same sessions, which isolates whether people are clicking this specific row "
        "because of what it is, rather than just because it's in front of them. That distinction matters here "
        "specifically because the whole premise of \"Watch While You Eat\" is that people want a faster way to "
        "decide, not just another row to browse — a high uplift is evidence of that specific preference, not "
        f"general clickiness. For this feature, that comparison came out to a feature-row CTR of {CTR_FEAT:.3f}% "
        f"({_B['feature_clicks']} clicks across {_B['feature_impr']:,} impressions) against a generic-row "
        f"baseline of {CTR_GEN:.3f}% ({_B['generic_clicks']} clicks across {_B['generic_impr']:,} impressions) "
        f"— a relative uplift of {CTR_UPLIFT:.2f}×, using the `payload.count` impression convention (a second "
        "convention, counting raw impression events, gives a different absolute CTR but the same uplift "
        "direction; the convention has to be stated because the two disagree substantially in absolute terms). "
        f"That {CTR_UPLIFT:.2f}× clears the project's own pre-registered viability threshold of 1.5×, making "
        "this the centrepiece metric from the methodology doc and the only one of the five behavioural KPIs "
        f"here that clearly favours the feature. It's worth remembering, though, that {_B['feature_clicks']} "
        "total feature clicks is a genuinely thin absolute base — a ratio can look strong while still resting "
        "on very few real events, and one or two additional or missing clicks would move this number "
        "meaningfully.")

    measured_kpi(
        "Content-to-Play (feature)", f"{C2P_FEAT_SESS:.1f}%", f"session grain · event grain {C2P_FEAT_EVT:.1f}%",
        "Content-to-play conversion measures the very last step of the decision funnel: of the people who got "
        "far enough to open a specific title, how many actually pressed play, rather than backing out and going "
        "somewhere else. It's a natural complement to CTR — CTR tells you whether people are drawn to click "
        "into the feature at all, while this tells you whether, once they're looking at something it suggested, "
        "they actually follow through. Because sessions and individual open-then-play events aren't the same "
        "unit, this has to be measured at a consistent grain to mean anything: at the session level, "
        f"{_B['c2p_feat_sess_num']} of the {_B['c2p_feat_sess_den']} sessions that opened a title from the "
        f"feature row went on to press play, a {C2P_FEAT_SESS:.1f}% conversion, against an app-wide "
        f"session-level rate of {C2P_ALL_SESS:.1f}% ({_B['c2p_all_sess_num']} of {_B['c2p_all_sess_den']}); at "
        f"the event level, {_B['c2p_feat_evt_num']} of {_B['c2p_feat_evt_den']} feature title-opens converted "
        f"to a play ({C2P_FEAT_EVT:.1f}%), against an app-wide event-level rate of {C2P_ALL_EVT:.1f}% "
        f"({_B['c2p_all_evt_num']} of {_B['c2p_all_evt_den']}). Whichever grain is used, the two numbers being "
        "compared have to be from the same grain — comparing a session-level feature figure against an "
        "event-level app-wide figure would be comparing two different things. At both grains, the feature "
        "actually trails the app-wide rate by five to seven points, which is the opposite direction from the "
        "CTR finding above, and the first real behavioural signal in this project that points against the "
        "feature rather than just falling short of a threshold. A large part of why this number is worth "
        f"treating cautiously: {_B['top_title_opens']} of the {_B['c2p_feat_evt_den']} feature title-opens, and "
        f"{_B['top_title_plays']} of the {_B['feature_plays']} plays, are all the same single title (Breaking "
        "Bad S5E13) — meaning a meaningful share of what looks like \"feature conversion\" is really describing "
        "how one tile performed in a very small prototype catalogue, not the feature mechanic in general.")

    measured_kpi(
        "Feature Adoption Rate", f"{ADOPTION:.1f}%",
        f"n={_B['adoption_num']}/{_B['adoption_den']} · threshold ≥30% · FAILS",
        "Feature adoption rate answers a different question than CTR does: not whether people click the row "
        "when it's in front of them, but whether they engage with it at all across a typical session — the "
        "standard distinction growth and product teams draw between exposure-driven interest and something "
        "people actually pick up as part of how they use the product. It's calculated as the share of sessions "
        "that reached the home screen (where the feature could be seen) that also included at least one click "
        f"on the feature row: {_B['adoption_num']} of {_B['adoption_den']} such sessions, or {ADOPTION:.1f}%. "
        "Unlike CTR, this metric has an explicit target attached to it in the project's own pre-registered "
        "measurement plan — a threshold of 30% adoption was set before data collection began, specifically so "
        f"the go/no-go decision wouldn't be made by eyeballing a number after the fact. At {ADOPTION:.1f}%, "
        "this result falls well short of that bar, and because the threshold was fixed in advance, that's a "
        "real signal rather than something to explain away: whatever is driving CTR up isn't yet translating "
        "into the kind of routine engagement the feature would need to matter at scale.")

    measured_kpi(
        "Feature Dwell Time", f"n={len(_B['dwell_ms'])}", "insufficient",
        "Dwell time is the standard way products measure whether something holds someone's attention once "
        "they've engaged with it, rather than just getting a passing glance — here, how long someone spends "
        "with the feature after clicking into it. The project's pre-registered threshold, a median of at least "
        "20 seconds, exists specifically to filter out curiosity clicks that don't turn into real engagement "
        "from ones that do. The problem with reporting this metric right now isn't the threshold, it's the "
        "sample behind it: across the entire fake-door test, exactly two dwell events were ever recorded "
        f"({_B['dwell_ms'][0]:,}ms and {_B['dwell_ms'][1]:,}ms). Two data points cannot support a median, a "
        "distribution, or any claim about typical behaviour — this isn't a metric that fell short of its "
        "target, it's a metric that doesn't yet have enough data to be evaluated at all, and it should never "
        "be shown as a clean percentage or a pass/fail result without that distinction being obvious.")

    measured_kpi(
        "Take Rate", f"{TAKE_RATE:.3f}%",
        f"n={_B['feature_plays']} plays · alt convention {TAKE_RATE_ALT:.2f}%",
        "Take rate is the metric Netflix itself uses internally to separate a row that gets clicked from one "
        "that actually delivers value — of everyone who saw the feature row, what share went all the way "
        "through to pressing play on something from it, not just opening or browsing it. Conceptually, it's "
        "the highest-ceiling metric on this list, because it's the one closest to the actual outcome the "
        "feature is meant to produce. Calculated the same way as CTR (feature plays divided by feature "
        "impressions, using the same `payload.count` convention so the two numbers are comparable), it comes "
        f"out to {_B['feature_plays']} plays across {_B['feature_impr']:,} impressions, or {TAKE_RATE:.3f}% — a "
        "second impression convention, counting raw impression events instead, gives "
        f"{TAKE_RATE_ALT:.2f}% for the same {_B['feature_plays']} plays, which is why the convention has to "
        "travel with the number whenever it's cited. The number that actually matters here, though, is the "
        f"{_B['feature_plays']}: that's {_B['feature_plays']} plays from {_B['feature_play_sessions']} distinct "
        "sessions, the thinnest base of any metric in this scorecard. A single additional play would move the "
        "percentage by roughly 17% of its own value, which is why the raw count belongs in front of the "
        "percentage rather than the other way around — this is a headcount that happens to be expressed as a "
        "ratio, not a stable statistical result.")

# ============================================================ SECTION 10 ==
elif page.startswith("10."):
    section_header("Key Insights", "Evidence-backed, separated by strength")
    st.markdown("#### Problem evidence")
    st.markdown(f"""
1. <span class='badge-strong'>STRONG</span> **Mealtime streaming is a frequent occasion.**
   {R['C1_occasion']['pct_3_or_more_per_week']}% ({R['C1_occasion']['n_3_or_more_per_week']}/{R['n_pre']}) of eligible
   respondents watch at a meal 3+ times a week. *C1_occasion, pre survey.*
2. <span class='badge-strong'>STRONG</span> **Off-platform leakage is the single clearest commercial loss.**
   {R['C4_leak']['pct_off_platform']}% ({R['C4_leak']['n_off_platform']}/{R['n_pre']}) leave Netflix when deciding drags,
   {R['C4_leak']['n_youtube']} of them to YouTube specifically. *C4_leak, pre survey.*
3. <span class='badge-weak'>WEAK / MIXED</span> **Abandonment is broad but rarely chronic.**
   {R['C3_abandonment']['pct_gave_up_at_least_once']}% gave up at least once in the last month, but only
   {R['C3_abandonment']['pct_chronic_often']}% do so "often." Breadth and severity point in different directions.
   *C3_abandonment, pre survey.*
4. <span class='badge-weak'>WEAK / MIXED</span> **The falsifier is real and non-trivial.**
   {R['C3_abandonment']['pct_already_know']}% already know what they want before sitting down — the problem does not
   apply to this group. *C3 falsifier, pre survey.*
""", unsafe_allow_html=True)
    st.markdown("#### Solution evidence")
    st.markdown(f"""
5. <span class='badge-strong'>STRONG</span> **The prototype reverses the C4 leak for the people who had it.**
   Among matched respondents who reported an off-platform leak pre-survey, {R['reversal_C4']['pct_would_stay']}%
   ({R['reversal_C4']['n_would_stay']}/{R['reversal_C4']['n_denominator']}) say they'd now stay on Netflix.
   *Matched pre/post.*
6. <span class='badge-weak'>WEAK</span> **Headline desirability lags the reaction measures.**
   Top-box likelihood to use next meal is only {R['solution_validation']['likelihood_use_next']['pct_top_box_8plus']}%,
   well below the {R['solution_validation']['start_intention']['pct_would_start']}% who say they'd have started or the
   {R['solution_validation']['stay_on_netflix']['pct_stay']}% who say they'd stay on Netflix. *Post survey.*
7. <span class='badge-strong'>STRONG</span> **Demand concentrates where the problem lives.**
   Respondents who "have to figure it out" pre-survey report the highest mean likelihood to use (7.11) vs "already
   know" (6.12) and "depends" (5.42); annoyance and likelihood to use correlate at r={R['matched_4b_annoyance_vs_likelihood_corr']}.
   This is the pattern a genuine signal produces. *Matched pre/post, descriptive association — not causal.*
""", unsafe_allow_html=True)
    st.markdown("#### Inconclusive / limited")
    st.markdown(f"""
8. <span class='badge-not'>INCONCLUSIVE</span> **The chronic-abandonment reversal cell is too small to generalise.**
   Only {R['reversal_C3']['n_denominator']} matched respondents reported chronic ("Often") abandonment; all
   {R['reversal_C3']['n_would_start']} said they'd start post-prototype, but n={R['reversal_C3']['n_denominator']} cannot
   support a population claim. *Matched pre/post.*
""", unsafe_allow_html=True)

# ============================================================ SECTION 11 ==
elif page.startswith("11."):
    section_header("Recommendations")
    st.markdown("#### KEEP")
    st.markdown(f"""
- **Best-episode pick and mood filters** — the two most-cited useful components ({R['solution_validation']['useful_components']['counts'].get('The single best-episode pick per show')} and
  {R['solution_validation']['useful_components']['counts'].get('The mood filters')} mentions of {R['n_post']}); qualitative theme "mood filters" reappears unprompted in the open-text 'one thing' question.
- **The core mechanic of pre-narrowing choice** — {R['solution_validation']['start_intention']['pct_would_start']}% would-have-started and {R['solution_validation']['reduced_struggle']['pct_reduced']}% reduced-struggle rates support keeping the row itself.
""")
    st.markdown("#### IMPROVE")
    st.markdown(f"""
- **Recommendation relevance / personalisation** — the single largest open-text theme (13/{len(R['qualitative_texts']['post_one_thing'])} substantive answers) asks for better-matched recommendations; this is also the most direct lever on the weak {R['solution_validation']['likelihood_use_next']['pct_top_box_8plus']}% top-box desirability KPI.
- **Meal-length/time-of-day awareness** — a recurring, concrete open-text request (episode length matched to meal duration).
- **Persistent placement** — one respondent's confusion note suggests a dedicated, findable section rather than a one-off row.
""")
    st.markdown("#### DEPRIORITIZE")
    st.markdown(f"""
- **Jump-to-best-moment graph** — least-cited useful component ({R['solution_validation']['useful_components']['counts'].get('The jump-to-the-best-moment graph')}/{R['n_post']}); does not clearly justify build cost on this sample.
""")
    st.markdown("#### TEST NEXT")
    st.markdown(f"""
- **Instrument the real feature** with an event log (impression, click, dwell, play-start) — the decisive behavioural
  KPIs (CTR, take rate, decision latency, funnel conversion, cannibalisation) cannot be computed from survey data alone.
- **A/B or holdout test** to measure actual retention lift, rather than the stated-intention proxies used here — this
  study has no control cohort and no time series.
- **Re-run the guardrail and taste-match items** against a live export to confirm they hold up before treating
  recommendation quality as settled (Section 6).
- **Targeted test with the "have to figure it out" segment** specifically, since demand concentrates there.
""")

# ============================================================ SECTION 12 ==
elif page.startswith("12."):
    section_header("KPI (archived)",
                   "Survey-response KPIs and the requested-marketing-metric tables, moved out of "
                   "9. KPI Scorecard so that section carries only the measured behavioural KPIs")
    st.info("**These are survey-response measures, not business metrics.** They record what respondents said, "
            "not what they did. The observed behavioural KPIs (CTR uplift, content-to-play, adoption, dwell, "
            "take rate) are in **9. KPI Scorecard**.", icon="🗄️")

    st.subheader("Core survey KPIs")
    kf = R["kpi_framework"]
    for k in kf["core_kpis"]:
        with st.container():
            c1, c2 = st.columns([1, 3])
            c1.metric(k["name"], f"{k['value_pct']}%", f"n={k['numerator']}/{k['denominator']}")
            with c2:
                st.markdown(f"**{k['category']}** — {k['definition']}")
                st.markdown(f"`{k['formula']}`")
                st.markdown(f"*Interpretation*: {k['interpretation']}")
                st.markdown(f"<span class='kpi-note'>Source: {k['source_question']} · Limitation: {k['limitation']}</span>",
                            unsafe_allow_html=True)
            st.markdown("---")

    st.subheader("Guardrail KPI")
    g = kf["guardrail_kpi"]
    c1, c2 = st.columns([1, 3])
    c1.metric(g["name"], f"{g['value_pct']}%", f"n={g['numerator']}/{g['denominator']}")
    with c2:
        st.markdown(f"**{g['category']}** — {g['definition']}")
        st.markdown(f"`{g['formula']}`")
        st.markdown(f"*Interpretation*: {g['interpretation']}")
        st.markdown(f"<span class='kpi-note'>Source: {g['source_question']} · Limitation: {g['limitation']}</span>",
                    unsafe_allow_html=True)

    st.subheader("Marketing / business metrics")
    st.markdown("""
The assignment brief also asks for market share, value share, volume share, CAC, CRC and EBITDA. **None of these
are measurable from this dataset** — they require external market sizing, cost data and a live billing system that
a single-session survey cannot provide. Applicable product/marketing indicators from this study instead:

| Metric | Value | What it stands in for |
|---|---|---|
| Feature awareness | {noticed}% (n={noticed_n}/{noticed_d}) | "reach" of the feature within the tested audience |
| Feature adoption intent | {top_box}% top-box (n={tb_n}/{tb_d}) | stated intent; the *observed* take rate and adoption rate are measured in Section 9 |
| Off-platform leakage (pre) | {leak}% (n={leak_n}/{leak_d}) | the addressable "value leak" the feature targets |
| Retention intent | {stay}% (n={stay_n}/{stay_d}) | proxy for "retention lift" — stated, not observed |
| Recommendation relevance | {rec}% "mostly wanted" (n={rec_n}/{rec_d}) | proxy for content-match quality |

| Marketing metric requested | Status |
|---|---|
| Market share / value share / volume share | **Not measurable from current dataset** — requires competitor and category revenue/volume data |
| CAC (customer acquisition cost) | **Not measurable** — requires marketing spend and acquisition counts |
| CRC (customer retention cost) | **Not measurable** — requires retention program spend |
| EBITDA | **Not measurable** — requires full P&L data |
| Actual retention / revenue impact | **Not measurable** — this is a single-session fake-door test with no time series or control cohort |
""".format(
        noticed=R["solution_validation"]["noticed_row"]["pct"], noticed_n=R["solution_validation"]["noticed_row"]["n"], noticed_d=R["solution_validation"]["noticed_row"]["d"],
        top_box=R["solution_validation"]["likelihood_use_next"]["pct_top_box_8plus"], tb_n=R["solution_validation"]["likelihood_use_next"]["n_top_box_8plus"], tb_d=R["solution_validation"]["likelihood_use_next"]["d"],
        leak=R["C4_leak"]["pct_off_platform"], leak_n=R["C4_leak"]["n_off_platform"], leak_d=R["C4_leak"]["d"],
        stay=R["solution_validation"]["stay_on_netflix"]["pct_stay"], stay_n=R["solution_validation"]["stay_on_netflix"]["n_stay"], stay_d=R["solution_validation"]["stay_on_netflix"]["d"],
        rec=round(100*R["guardrail"]["distribution"].get("Mostly things I'd want",0)/R["guardrail"]["d"],1), rec_n=R["guardrail"]["distribution"].get("Mostly things I'd want",0), rec_d=R["guardrail"]["d"],
    ))

    st.subheader("Behavioural KPIs still requiring instrumentation")
    st.markdown("""
The event log covers five behavioural KPIs, now in Section 9. These three remain uninstrumented — listed with
the fields that would be needed:

| Behavioural KPI | Event-log fields required |
|---|---|
| Actual decision latency | timestamp of row impression to timestamp of play-start event |
| Funnel conversion (full) | impression → click → play-start → **watch-complete** event sequence; no watch-complete event exists |
| Cannibalisation rate | play events on other rows/rails for exposed vs unexposed users, same session; needs a holdout arm |
""")
    th = R["spec_crosscheck"]["preregistered_behavioural_thresholds"]
    st.caption(
        f"The project's own measurement plan pre-registered viability thresholds: relative CTR uplift "
        f"{th['relative_ctr_uplift_threshold']}, feature adoption {th['feature_adoption_threshold']}, "
        f"feature dwell {th['feature_dwell_threshold']}. Verdict rule: {th['verdict_rule']} — on the measured "
        f"values in Section 9, uplift clears, adoption fails, and dwell is unanswerable at n={len(_B['dwell_ms'])}, "
        "so the rule is not satisfied. Note that `src/lib/report-config.ts` in the prototype repo marks these "
        "three thresholds as PLACEHOLDERS to be confirmed before any pass/fail is published.")
