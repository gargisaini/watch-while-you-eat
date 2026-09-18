# Qualitative Theme Analysis

Manually coded from the actual response text in `analysis/clean_pre.csv` / `clean_post.csv` (open_* columns). No quotes are invented; each theme's illustration is a paraphrase of what respondents actually wrote, not a verbatim quote. Themes are ranked by frequency within the respondents who gave a substantive answer to that field — these fields were optional, so the base is the answering subsample, not all eligible/post respondents (noted per field).

## Pre-survey — 'Describe the last time you gave up trying to find something at a meal'

Base: respondents who volunteered a free-text answer describing their last give-up (18 of 61 eligible respondents; this field was optional so the other 43 left it blank — themes below describe this self-selected subsample of 18, not all eligible respondents).

| Theme | Freq (n) | % of answered | Paraphrased insight | Product implication |
|---|---|---|---|---|
| Switched off-platform (YouTube / Instagram / another app) | 7 | 38.9% | Several respondents said that when deciding dragged they left the app entirely — opening YouTube or Instagram instead of continuing to browse Netflix. | Corroborates the C4 off-platform leak measured quantitatively; the leak destination named unprompted is consistently YouTube or social video. |
| Defaulted to a familiar rewatch | 3 | 16.7% | Some respondents said they gave up searching and put on something they'd already seen rather than picking something new. | A 'quick rewatch' shortcut already exists informally; the prototype's 'shows already watched' component maps directly onto this coping behaviour. |
| Time pressure from the meal itself | 3 | 16.7% | A few respondents described the meal finishing, or food going cold, before they had settled on something to watch. | The meal is a hard deadline, not just a mood — supports treating 'meal-window cost' as a real cost, not only an annoyance rating. |
| No problem — decides in advance | 2 | 11.1% | A couple of respondents said they never face this because they choose what to watch before sitting down. | Direct qualitative echo of the C3 falsifier segment; this behaviour is a real substitute, not just a survey artifact. |
| Browsed without resolving (decision paralysis) | 2 | 11.1% | A couple of respondents described browsing around — food content, or simply not having a next show queued — without landing on anything. | Supports a queueing/continuation feature, not just faster search, for the post-finale moment. |
| Co-viewing / social constraint | 1 | 5.6% | One respondent noted difficulty finding something suitable to watch with parents. | A minority but distinct segment (shared viewing) whose friction is about suitability, not volume of choice; too small a signal to size here. |

## Post-survey — 'What is the ONE thing that would make you actually use it?'

Base: of 37 post respondents, 35 gave a substantive answer to 'what is the ONE thing that would make you actually use it'.

| Theme | Freq (n) | % of answered | Paraphrased insight | Product implication |
|---|---|---|---|---|
| Better / more personalised recommendations | 13 | 37.1% | The largest single group asked for recommendations more closely matched to their own taste and watch history, several explicitly contrasting this with the prototype's current suggestions. | Recommendation relevance is the single biggest lever on stated adoption — consistent with the weak 32.4% top-box headline desirability; this is the primary 'improve' target, not a new component. |
| Mood-based filtering valued / requested | 7 | 20.0% | A number of respondents pointed to the mood filter as the thing they want more of or that already works for them. | Corroborates the quantitative component-usefulness ranking, where mood filters is the second most-cited useful part. |
| Adapting to meal context (episode length / time of day) | 3 | 8.6% | A few respondents wanted the row to account for how long they actually have — for example shorter episodes so the show can finish with the meal. | A concrete, buildable refinement: surface episode runtime and bias toward meal-length content. |
| Less cognitive effort / fewer choices to weigh | 3 | 8.6% | Some respondents said the appeal is simply not having to think — clicking something already picked for them. | Validates the core mechanic (pre-narrowing choice) independent of recommendation quality. |
| Short-form / snackable content style | 2 | 5.7% | A couple of respondents compared the desired experience to short-form video feeds such as YouTube Shorts. | A different product shape (bite-sized clips) than the current best-episode-pick mechanic; worth flagging as a distinct idea to test, not folding into the current feature. |
| Interface / discoverability friction (unlabeled thumbnails) | 1 | 2.9% | One respondent found it hard to identify shows from cover art alone and wanted titles shown. | Minor UI fix, low cost, plausibly affects the 'about the same' speed-perception segment. |
| Already decides in advance — feature doesn't apply | 1 | 2.9% | One respondent restated that they plan ahead regardless of platform, so the feature has little to add for them. | Same falsifier segment reappearing in the post survey — this group is unlikely to adopt regardless of iteration. |
| Off-topic or non-committal answers | 5 | 14.3% | A handful of answers were non-answers or unrelated one-word replies (e.g. uncertainty about the question, or unrelated words). | Signals response-quality noise in this open field; treat single-word answers as low-confidence evidence. |

## Post-survey — 'Anything that confused you or got in the way?'

Base: only 4 of 37 post respondents reported anything confusing or in the way; 33 left this blank or wrote 'no' / 'nothing'.

| Theme | Freq (n) | % of answered | Paraphrased insight | Product implication |
|---|---|---|---|---|
| Prototype fidelity blurred the test (felt too much like real Netflix) | 2 | 50.0% | Two respondents said the prototype resembled the real Netflix UI closely enough that it was unclear what they were meant to be evaluating, and one wanted a brief orientation before starting. | A study-design note more than a product finding: low reported confusion may partly reflect respondents not clearly distinguishing the feature from the baseline UI, which argues for treating the strongly positive reaction numbers with some caution. |
| Wants a persistently visible, dedicated section | 1 | 25.0% | One respondent suggested a clearly dedicated 'Watch While You Eat' section would reduce anxiety about finding it again. | Supports a persistent placement/entry point rather than a one-off row, as a low-cost iteration. |
| Non-functional prototype elements | 1 | 25.0% | One respondent noted that some interactive elements (play buttons) weren't functional in the prototype. | Expected fake-door/prototype limitation, not a product signal. |
