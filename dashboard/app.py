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

# ------------------------------------------ hypothetical business/financial
# Section 3 (Marketing Metrics) only. Two layers: (1) real, sourced Netflix company financials
# (SEC 10-K, Netflix's own investor letter) and this project's own real leading
# indicators (adoption rate, reversal rate); (2) one unverifiable assumption —
# how much of Netflix's baseline churn this specific friction causes — sized
# proportionally to layer 1 rather than guessed independently. Every number
# downstream of that one assumption is a hypothetical projection, not a
# measurement, and is labelled as such everywhere it's shown.
NETFLIX_BIZ = {
    "fy2024_revenue": 39_000_966_000,       # SEC 10-K, real
    "subs_q4_2024": 301_630_000,            # SEC 10-K/earnings release, last disclosed subscriber count
    "net_adds_2024": 41_000_000,            # Netflix's own "record net additions (41M)" (2025 Perspective letter)
    "operating_margin_fy2025": 0.295,       # SEC 10-K, real
    "monthly_churn_baseline": 0.020,        # Antenna (third-party analytics firm), US-market estimate — NOT Netflix-disclosed
    "discount_rate_assumed": 0.10,          # standard illustrative rate — NOT Netflix's actual cost of capital
    "cac_anchor": 126,                      # Q3 2024, derived from Netflix's own disclosed marketing spend ÷ net adds
                                             # (allyourscreens.com calc, not Netflix's own stated CAC). Last computable
                                             # year — Netflix stopped disclosing subscriber counts in 2025. Was
                                             # trending up (+31% 2022→2024), so likely understates current CAC.
}
_NB = NETFLIX_BIZ
avg_subs_2024 = ((_NB["subs_q4_2024"] - _NB["net_adds_2024"]) + _NB["subs_q4_2024"]) / 2
ARPU_MONTHLY = _NB["fy2024_revenue"] / avg_subs_2024 / 12
MARGIN_PER_MEMBER_ANNUAL = ARPU_MONTHLY * 12 * _NB["operating_margin_fy2025"]

RESOLUTION_LOW = ADOPTION / 100                       # 10.4%, real observed adoption rate (§2)
RESOLUTION_HIGH = R["reversal_C4"]["n_would_stay"] / R["reversal_C4"]["n_denominator"]  # 17/19, real reversal rate (Analysis/Proposition)
RESOLUTION_MID = (RESOLUTION_LOW * RESOLUTION_HIGH) ** 0.5

CHURN_ANCHOR = 0.0005
def churn_shift(resolution_rate):
    return CHURN_ANCHOR * (resolution_rate / RESOLUTION_LOW)

def clv(annual_rr, margin=MARGIN_PER_MEMBER_ANNUAL, discount=_NB["discount_rate_assumed"]):
    return margin * (annual_rr / (1 + discount - annual_rr))

BASELINE_MONTHLY_CHURN = _NB["monthly_churn_baseline"]
BASELINE_ANNUAL_RR = (1 - BASELINE_MONTHLY_CHURN) ** 12
BASELINE_CLV = clv(BASELINE_ANNUAL_RR)

SCENARIOS = ["Low", "Mid", "High"]
RESOLUTIONS = {"Low": RESOLUTION_LOW, "Mid": RESOLUTION_MID, "High": RESOLUTION_HIGH}
BIZ_PROJECTIONS = {}
for _name in SCENARIOS:
    _shift = churn_shift(RESOLUTIONS[_name])
    _new_monthly_churn = BASELINE_MONTHLY_CHURN - _shift
    _new_annual_rr = (1 - _new_monthly_churn) ** 12
    _extra_retained_per_month = _shift * _NB["subs_q4_2024"]
    _c = clv(_new_annual_rr)
    BIZ_PROJECTIONS[_name] = {
        "new_monthly_churn": _new_monthly_churn * 100,
        "churn_shift_pp": _shift * 10000 / 100,
        "extra_retained_per_month": _extra_retained_per_month,
        "revenue_retained_annual": _extra_retained_per_month * ARPU_MONTHLY * 12,
        "clv": _c,
        "clv_delta_pct": (_c - BASELINE_CLV) / BASELINE_CLV * 100,
        "acquisition_cost_avoided_annual": _extra_retained_per_month * _NB["cac_anchor"] * 12,
        "ltv_cac_ratio": _c / _NB["cac_anchor"],
    }

# Pinned to this formula's own full-precision output (never rounding mid-calculation) —
# not hand-typed targets, so a future edit to NETFLIX_BIZ or the resolution rates fails
# loudly here instead of silently drifting from the narrative text below.
assert round(ARPU_MONTHLY, 2) == 11.56, "ARPU derivation drifted"
assert round(MARGIN_PER_MEMBER_ANNUAL, 2) == 40.93, "margin/member drifted"
assert round(BASELINE_CLV, 2) == 101.86, "baseline CLV drifted"
assert round(BIZ_PROJECTIONS["Low"]["clv"], 2) == 104.08, "Low CLV drifted"
assert round(BIZ_PROJECTIONS["Mid"]["clv"], 2) == 108.58, "Mid CLV drifted"
assert round(BIZ_PROJECTIONS["High"]["clv"], 2) == 123.89, "High CLV drifted"
assert round(BIZ_PROJECTIONS["Low"]["new_monthly_churn"], 2) == 1.95, "Low churn % drifted"
assert round(BIZ_PROJECTIONS["Mid"]["new_monthly_churn"], 2) == 1.85, "Mid churn % drifted"
assert round(BIZ_PROJECTIONS["High"]["new_monthly_churn"], 2) == 1.57, "High churn % drifted"
assert round(BIZ_PROJECTIONS["Low"]["ltv_cac_ratio"], 2) == 0.83, "Low LTV:CAC drifted"
assert round(BIZ_PROJECTIONS["Mid"]["ltv_cac_ratio"], 2) == 0.86, "Mid LTV:CAC drifted"
assert round(BIZ_PROJECTIONS["High"]["ltv_cac_ratio"], 2) == 0.98, "High LTV:CAC drifted"

# §2 only: summary tile on top, bordered detail card below. badge = (css class, label).
# badge is optional: pass None to render a tile with no verdict label. The KPI
# cards report what was measured and leave the adjudication to the reader, so
# every KPI below passes None. The slot is kept for reuse elsewhere.
def kpi_tile(col, name, value, sub, badge, *_):
    chip = f"<span class='{badge[0]}'>{badge[1]}</span>" if badge else ""
    col.markdown(
        f"<div class='kpi-tile'><div class='kpi-tile-name'>{name}</div>"
        f"<div class='kpi-tile-value'>{value}</div><div class='kpi-tile-sub'>{sub}</div>"
        f"{chip}</div>", unsafe_allow_html=True)


def kpi_detail(name, value, sub, badge, definition, calculation):
    with st.container(border=True):
        chip = f" &nbsp;<span class='{badge[0]}'>{badge[1]}</span>" if badge else ""
        st.markdown(f"#### {name}{chip}", unsafe_allow_html=True)
        a, b, c = st.columns([1, 2, 2], gap="medium")
        a.metric("Result", value)
        a.markdown(f"<div class='kpi-note'>{sub}</div>", unsafe_allow_html=True)
        b.markdown(definition)
        c.markdown(calculation)

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
div[data-testid="stMetricValue"] {{
    color: {TEXT}; font-size: 2rem !important; font-weight: 700 !important; line-height: 1.2 !important;
}}
.kpi-note {{ color: {MUTED}; font-size: 0.82rem; margin-top: -8px; }}
h1, h2, h3 {{ color: {TEXT}; }}
.stMarkdown p {{ color: {TEXT}; }}
.badge-strong {{ background:#1E3A24; color:#8FD19E; padding:2px 8px; border-radius:6px; font-size:0.75rem; }}
.badge-weak {{ background:#3A2A12; color:#E8C078; padding:2px 8px; border-radius:6px; font-size:0.75rem; }}
.badge-not {{ background:#3A1414; color:#E88; padding:2px 8px; border-radius:6px; font-size:0.75rem; }}
.badge-neutral {{ background:#2A2A2A; color:{MUTED}; padding:2px 8px; border-radius:6px; font-size:0.75rem; }}
.kpi-tile {{
    background-color: {CARD}; border: 1px solid {CARD_BORDER}; border-radius: 10px;
    padding: 14px 16px; height: 100%; min-height: 150px;
}}
.kpi-tile-name {{ color: {MUTED}; font-size: 0.85rem; }}
.kpi-tile-value {{ color: {TEXT}; font-size: 1.9rem; font-weight: 700; line-height: 1.3; }}
.kpi-tile-sub {{ color: {MUTED}; font-size: 0.78rem; margin-bottom: 8px; }}
.disclaimer-box {{
    background-color: {WARN}; color: {BG}; font-weight: 700; text-decoration: underline;
    padding: 12px 16px; border-radius: 8px; margin-bottom: 16px;
}}
.problem-statement {{
    font-size: 1.6rem; font-weight: 700; line-height: 1.45; color: {TEXT};
    border-left: 4px solid {ACCENT}; padding: 4px 0 4px 18px; margin: 8px 0 16px 0;
}}
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
    "1. Business Problem", "2. KPI Scorecard", "3. Marketing Metrics",
    "4. Analysis", "5. Proposition",
]
page = st.sidebar.radio("Section", SECTIONS, label_visibility="collapsed")
st.sidebar.markdown("---")
st.sidebar.markdown(
    f"<span class='kpi-note'>Eligible pre n = {R['n_pre']} · Post n = {R['n_post']} · "
    f"Matched pairs n = {R['n_matched']}</span>", unsafe_allow_html=True)

# ============================================================ SECTION 1 ===
if page.startswith("1."):
    section_header("Business Problem", "The research hypothesis this study set out to test")
    st.markdown(
        "<div class='problem-statement'>Young Netflix viewers aged 18–30 spend so much time deciding what "
        "to watch during a meal — on their phone, laptop, or TV — that they often give up before hitting "
        "play, losing the one window they had to relax and watch.</div>", unsafe_allow_html=True)
    st.markdown("""
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
""")
    st.markdown("---")
    st.markdown("**Prototype**: a dedicated row surfacing a single best-episode pick per show, mood-based "
                "filters, previously-watched shows, and a jump-to-best-moment marker, tested as a high-fidelity "
                "fake-door prototype after respondents completed the pre-survey.")
    st.markdown('**Solution**: Does the "Watch While You Eat" prototype measurably address these claims?')


# ============================================================ SECTION 2 ===
elif page.startswith("2."):
    section_header("KPI Scorecard")
    st.caption("What people actually did in the prototype (960 events, 94 sessions) — real behaviour, not "
               "survey answers. What this could be worth to Netflix is in **3. Marketing Metrics**.")

    KPIS = [(
        "Relative CTR Uplift", f"{CTR_UPLIFT:.2f}×",
        f"{_B['feature_clicks']} clicks from {_B['feature_impr']:,} views",
        None,
        f"**What it means:** people clicked our row about {CTR_UPLIFT:.1f}× more often than a normal row. "
        "It clearly grabs attention.",
        f"**How we got it:** our row's click rate ({_B['feature_clicks']} clicks ÷ {_B['feature_impr']:,} views "
        f"= {CTR_FEAT:.3f}%) ÷ a normal row's ({_B['generic_clicks']} ÷ {_B['generic_impr']:,} = {CTR_GEN:.3f}%). "
        f"Only {_B['feature_clicks']} clicks so far, so treat it as an early signal."
    ), (
        "Content-to-Play", f"{C2P_FEAT_SESS:.1f}%", f"vs {C2P_ALL_SESS:.1f}% for the rest of the app",
        None,
        "**What it means:** after opening a show from our row, people pressed play a bit less often than "
        "elsewhere in the app. The row gets the click, but doesn't yet turn it into watching.",
        f"**How we got it:** {_B['c2p_feat_sess_num']} of {_B['c2p_feat_sess_den']} sessions played after "
        f"opening a show from the row, vs {_B['c2p_all_sess_num']} of {_B['c2p_all_sess_den']} app-wide "
        f"(per open: {C2P_FEAT_EVT:.1f}% vs {C2P_ALL_EVT:.1f}%). {_B['top_title_opens']} of the "
        f"{_B['c2p_feat_evt_den']} opens were one show (Breaking Bad), so one tile drives a lot of this."
    ), (
        "Feature Adoption", f"{ADOPTION:.1f}%",
        f"{_B['adoption_num']} of {_B['adoption_den']} sessions",
        None,
        "**What it means:** about 1 in 10 people who reached the home screen used the row at all. Read "
        "alongside the CTR tile, which shows those who did use it clicked far more readily than on any "
        "other row: the limit is how many find it, not how well it lands.",
        f"**How we got it:** {_B['adoption_num']} sessions clicked the row ÷ {_B['adoption_den']} sessions "
        "that reached the home screen."
    ), (
        "Feature Dwell Time", f"n={len(_B['dwell_ms'])}",
        f"{len(_B['dwell_ms'])} readings recorded",
        None,
        "**What it means:** how long people stay once they open the row. The reading count is low for a "
        "structural reason rather than a behavioural one: the timer stops when the show card is closed, "
        "but pressing play leaves the card open and moves on, so the most engaged sessions are the ones "
        "this measure cannot see.",
        f"**How we got it:** recorded visits so far, {_B['dwell_ms'][0]/1000:.1f}s and "
        f"{_B['dwell_ms'][1]/1000:.1f}s. No median is shown on two readings."
    ), (
        "Take Rate", f"{TAKE_RATE:.3f}%",
        f"{_B['feature_plays']} plays from {_B['feature_impr']:,} views",
        None,
        "**What it means:** out of everyone shown the row, very few went on to press play from it.",
        f"**How we got it:** {_B['feature_plays']} plays ÷ {_B['feature_impr']:,} row views. Counting row-view "
        f"events instead gives {TAKE_RATE_ALT:.2f}%. With only {_B['feature_plays']} plays, one more would "
        "change this a lot."),
    ]

    for col, k in zip(st.columns(len(KPIS)), KPIS):
        kpi_tile(col, *k)
    st.markdown("")

    st.subheader("KPI detail")
    for k in KPIS:
        kpi_detail(*k)

    st.subheader("What people said (survey)")
    st.caption("Answers from the pre/post surveys — what people told us, not what they did.")
    st.markdown("""
| Metric | Value | What it means |
|---|---|---|
| Feature awareness | {noticed}% ({noticed_n}/{noticed_d}) | Most people noticed the row |
| Keen to use it again | {top_box}% ({tb_n}/{tb_d}) | Only about 1 in 3 rated it 8–10 out of 10 |
| Left Netflix when stuck (before) | {leak}% ({leak_n}/{leak_d}) | More than half leave Netflix when choosing takes too long |
| Would stay on Netflix | {stay}% ({stay_n}/{stay_d}) | Most say the row would keep them on Netflix |
| Picks felt right | {rec}% ({rec_n}/{rec_d}) | Only 5 people were asked — too few to judge |
""".format(
        noticed=R["solution_validation"]["noticed_row"]["pct"], noticed_n=R["solution_validation"]["noticed_row"]["n"], noticed_d=R["solution_validation"]["noticed_row"]["d"],
        top_box=R["solution_validation"]["likelihood_use_next"]["pct_top_box_8plus"], tb_n=R["solution_validation"]["likelihood_use_next"]["n_top_box_8plus"], tb_d=R["solution_validation"]["likelihood_use_next"]["d"],
        leak=R["C4_leak"]["pct_off_platform"], leak_n=R["C4_leak"]["n_off_platform"], leak_d=R["C4_leak"]["d"],
        stay=R["solution_validation"]["stay_on_netflix"]["pct_stay"], stay_n=R["solution_validation"]["stay_on_netflix"]["n_stay"], stay_d=R["solution_validation"]["stay_on_netflix"]["d"],
        rec=round(100*R["guardrail"]["distribution"].get("Mostly things I'd want",0)/R["guardrail"]["valid_responses_n"],1), rec_n=R["guardrail"]["distribution"].get("Mostly things I'd want",0), rec_d=R["guardrail"]["valid_responses_n"],
    ))


# ============================================================ SECTION 3 ===
elif page.startswith("3."):
    section_header("Marketing Metrics")
    st.markdown(
        "<div class='disclaimer-box'>Estimates only — Netflix has not built this feature. These numbers show "
        "what it could be worth if it launched for all members.</div>", unsafe_allow_html=True)

    L, M, H = (BIZ_PROJECTIONS[k] for k in SCENARIOS)
    MID = ("badge-neutral", "MID ESTIMATE")
    for col, k in zip(st.columns(4), [
        ("Monthly churn", f"{M['new_monthly_churn']:.2f}%",
         f"down from {BASELINE_MONTHLY_CHURN*100:.1f}% · range {L['new_monthly_churn']:.2f}–{H['new_monthly_churn']:.2f}%", MID),
        ("Customer lifetime value", f"${M['clv']:.2f}",
         f"up from ${BASELINE_CLV:.2f} · range ${L['clv']:.0f}–${H['clv']:.0f}", MID),
        ("Acquisition cost avoided", f"${M['acquisition_cost_avoided_annual']/1e6:.0f}M/yr",
         f"range ${L['acquisition_cost_avoided_annual']/1e6:.0f}M–${H['acquisition_cost_avoided_annual']/1e9:.2f}B", MID),
        ("LTV:CAC", f"{M['ltv_cac_ratio']:.2f} : 1",
         f"range {L['ltv_cac_ratio']:.2f}–{H['ltv_cac_ratio']:.2f} · healthy ≈ 3:1", MID),
    ]):
        kpi_tile(col, *k)
    st.markdown("")

    st.subheader("All scenarios at a glance")
    st.markdown(f"""
| | Today | Low | Mid | High |
|---|---|---|---|---|
| **Share of at-risk viewers won back** | — | {RESOLUTION_LOW*100:.1f}% (real adoption) | {RESOLUTION_MID*100:.1f}% (in between) | {RESOLUTION_HIGH*100:.1f}% (said they'd stay) |
| **Monthly churn** | {BASELINE_MONTHLY_CHURN*100:.2f}% | {L['new_monthly_churn']:.2f}% | {M['new_monthly_churn']:.2f}% | {H['new_monthly_churn']:.2f}% |
| **Customer lifetime value** | ${BASELINE_CLV:.2f} | ${L['clv']:.2f} (+{L['clv_delta_pct']:.1f}%) | ${M['clv']:.2f} (+{M['clv_delta_pct']:.1f}%) | ${H['clv']:.2f} (+{H['clv_delta_pct']:.1f}%) |
| **Acquisition cost avoided / yr** | — | ${L['acquisition_cost_avoided_annual']/1e6:.0f}M | ${M['acquisition_cost_avoided_annual']/1e6:.0f}M | ${H['acquisition_cost_avoided_annual']/1e9:.2f}B |
| **LTV:CAC** | {BASELINE_CLV/_NB['cac_anchor']:.2f} : 1 | {L['ltv_cac_ratio']:.2f} : 1 | {M['ltv_cac_ratio']:.2f} : 1 | {H['ltv_cac_ratio']:.2f} : 1 |
""")

    st.subheader("What each metric means")
    BIZ_CARDS = [
        ("Retention (monthly churn)",
         "The share of members who cancel each month. Lower is better — if the row stops people drifting "
         "off to YouTube, fewer of them cancel.",
         f"Today's {BASELINE_MONTHLY_CHURN*100:.1f}% churn minus the share of at-risk viewers the row wins back. "
         "How much churn this problem actually causes is our one big assumption."),
        ("Customer lifetime value (CLV)",
         "How much profit one member brings in over their whole time with Netflix. Keeping members longer "
         "makes each one worth more.",
         f"Profit per member per year (${MARGIN_PER_MEMBER_ANNUAL:.2f}) adjusted for how long members stay, "
         f"using a {_NB['discount_rate_assumed']*100:.0f}% discount rate."),
        ("Acquisition cost avoided",
         "Money Netflix doesn't have to spend on ads to win back members it would otherwise lose.",
         f"Extra members kept each month × ${_NB['cac_anchor']} (Netflix's cost to gain one member, Q3 2024) "
         "× 12. That cost was rising, so this is probably on the low side."),
        ("LTV:CAC",
         "How much a member is worth compared with what it costs to get one. Around 3:1 is seen as healthy.",
         f"Lifetime value ÷ ${_NB['cac_anchor']}. It sits below 1 here because our model is simple (company-wide "
         "margin, US churn), not because Netflix loses money. What matters is that it goes up in every scenario."),
    ]
    for row in (BIZ_CARDS[:2], BIZ_CARDS[2:]):
        for col, (name, means, how) in zip(st.columns(2), row):
            with col.container(border=True):
                st.markdown(f"#### {name}")
                st.markdown(f"**What it means:** {means}")
                st.markdown(f"**How we got it:** {how}")


# ============================================================ SECTION 4 ===
elif page.startswith("4."):
    section_header("Analysis", "Problem validation, solution validation, guardrail, feature components, and segments")

    st.subheader("Problem Validation (C1–C5)")
    st.caption(f"Pre-survey, eligible respondents, n = {R['n_pre']}")

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

    st.markdown("---")

    st.subheader("Solution Validation")
    st.caption(f"Post-prototype survey, n = {R['n_post']}")
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

    st.markdown("---")

    st.subheader("Guardrail — Recommendation Quality / Already-Seen Check")
    g = R["guardrail"]

    order = ["A mix", "Mostly things I'd want"]
    hbar(order, [g["distribution"].get(k, 0) for k in order], highlight_labels=["Mostly things I'd want"],
         title=f"Did suggestions feel wanted or already-skippable? (n={g['valid_responses_n']} of "
               f"{g['d']} asked)", suffix="")

    st.markdown("---")

    st.subheader("Feature Component Analysis")
    st.caption(f"Multi-select, post survey, n = {R['n_post']}")
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

    st.markdown("---")

    st.subheader("Segment Analysis")
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


# ============================================================ SECTION 5 ===
elif page.startswith("5."):
    section_header("Proposition", "Key insights and recommendations")

    st.subheader("Key Insights")
    st.caption("Evidence-backed, separated by strength")
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

    st.markdown("---")

    st.subheader("Recommendations")
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
