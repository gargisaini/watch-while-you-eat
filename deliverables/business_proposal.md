# Watch While You Eat — Business Proposal

## Business problem

Young Netflix viewers aged 18–30 are hypothesised to spend so much time deciding what to watch during a meal
that they sometimes give up before pressing play, losing a recurring engagement window and, at the margin,
leaking to a competing app. "Watch While You Eat" is a fake-door prototype — a dedicated row combining a
single best-episode pick per show, mood-based filters, previously-watched shows, and a jump-to-best-moment
marker — designed to cut that decision cost. This proposal treats the problem statement as a hypothesis and
reports what a 61-respondent pre-survey and a 37-respondent matched post-survey actually show, including
where the evidence is partial or weak.

## Research evidence: is the problem real?

The occasion is genuinely frequent: 85.2% of eligible respondents (52/61) watch something at a meal three or
more times a week. Decision friction is real but not universal — 59.0% (36/61) spend more than three minutes
deciding, and by the time they settle, a third of the meal is on average already over (mean 3.23/10 on the
"meal already over" scale). Abandonment is broad but shallow: 78.7% (48/61) gave up at least once in the
last month, yet only 13.1% (8/61) do so "often." The problem statement's falsifier — do respondents already
know what they want? — returns a non-trivial 37.7% (23/61) who say yes; the friction problem simply does not
apply to over a third of this audience, and this is reported rather than minimised. The clearest commercial
signal is the off-platform leak: 54.1% (33/61) say that the last time deciding dragged, they left Netflix
entirely, most often to YouTube (23 of those 33 instances). Severity is moderate-to-high but has a heavy
tail: mean annoyance 5.7/10, with 45.9% rating it 7 or above.

Read together, the data **partially validates** the problem statement: frequent occasion and a real
off-platform leak are strongly supported; chronic, severe abandonment is a minority behaviour, not the
median experience.

## Solution evidence

Among the 37 respondents who tried the prototype, reaction measures are strongly positive on every stated
dimension: 94.6% (35/37) say they would have started watching rather than given up, 94.6% (35/37) say it
reduced the decision struggle (though only 21.6% chose the strongest option, "clearly"), 86.5% (32/37) say it
would keep them on Netflix instead of switching away, and 59.5% (22/37) perceived it as faster than their
normal routine. The one measure that asks for actual commitment — top-box (8–10) likelihood to use it at the
next meal — is materially weaker at 32.4% (12/37), with a mean of 6.14/10. This gap between soft reaction
measures and the one measure requiring commitment is the single most important nuance in the solution data,
and the decision should weight the latter more heavily than the former.

Matching respondents across the two surveys strengthens the case where it counts most: among the 19 matched
respondents who had reported an off-platform leak pre-survey, 89.5% (17/19) now say they'd stay on Netflix —
the strongest single piece of evidence in the dataset, because it targets exactly the segment the business
case depends on. Demand also concentrates correctly: respondents who pre-survey said they "have to figure it
out" report the highest mean likelihood to use (7.11) versus "already know" (6.12) and "depends" (5.42), and
annoyance correlates with likelihood to use at r=0.375 — the pattern a genuine signal produces, not a novelty
effect spread evenly across everyone.

## Guardrail

The prototype's central risk is repeating Netflix's own "Play Something" failure — recommending content
users have already seen and would skip. In this dataset, 0 of 37 respondents chose the "would already skip"
option; responses split between "mostly things I'd want" (24/37) and "a mix" (13/37), with zero missing
values. No kill-switch signal is present. This directly contradicts a prior report on this same project,
which described a related item as an unusable default value; the current Excel export shows real variance
instead. Given that direct contradiction, this guardrail result should be re-verified against the live survey
tool before being treated as settled — see Data Limitations.

## Product and business implications

The component data says what to build on: the best-episode pick (19/37) and mood filters (19/37) are the
most-cited useful parts and should be kept; the jump-to-best-moment graph is the least-cited (3/37) and does
not clearly earn its build cost on this sample. The single largest open-text theme in the post survey (13 of
35 substantive answers) asks for better-matched recommendations — the most direct lever on the weak top-box
desirability number, and the clearest "improve" priority. Commercially, this study can name feature awareness
(81.1%), stated retention intent (86.5%), and the addressable off-platform leak (54.1% pre-survey) as
relevant indicators. It **cannot** produce market share, value/volume share, CAC, CRC, or EBITDA — those
require external market and cost data this survey was never designed to collect — and it cannot measure
actual retention, which by the course formula sheet's own definition requires a tracked cohort over time, not
a single session.

## Limitations

Sample sizes are small (n=61 pre, n=37 post, several segment cells under 5); there is no control cohort, so
before/after comparisons cannot rule out novelty effects; every figure is self-report, not logged behaviour;
completer bias likely skews reaction measures favourably, since 24 of 61 eligible respondents did not finish;
and the recomputed sample sizes materially differ from a prior report on this project, a discrepancy that is
flagged, not resolved, here.

## Next experiment and instrumentation required

The decisive test is behavioural, not another survey: instrument the real feature with an event log (row
impression, row click, feature dwell, play-start) and run it against this project's own pre-registered
thresholds — relative CTR uplift ≥1.5× against a baseline row, feature adoption ≥30% of qualified sessions,
and median feature dwell ≥20 seconds — with a no-feature holdout arm if cannibalisation needs to be ruled out.
Until that exists, this survey establishes that the problem is real for a majority (not all) of this audience
and that the prototype's stated reaction is positive but not yet a committed "I will use this," which is the
appropriately cautious basis for a go/no-go call.
