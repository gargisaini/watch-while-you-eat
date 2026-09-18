"""Manual thematic coding of the open-text responses in results.json.
Coded by hand against the actual response text (see clean_pre.csv /
clean_post.csv open_* columns) — not keyword-matched, not invented.
Appends a 'qualitative_themes' block to analysis/results.json.
"""
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
r = json.loads((OUT / "results.json").read_text(encoding="utf-8"))

pre_n = len(r["qualitative_texts"]["pre_giveup_story"])   # 18, of 61 eligible
post_thing_n = len(r["qualitative_texts"]["post_one_thing"])  # 35, of 37
post_conf_n = len(r["qualitative_texts"]["post_confusion"])   # 4, of 37

themes = {
    "pre_giveup_story": {
        "base": "respondents who volunteered a free-text answer describing their last give-up "
                "(18 of 61 eligible respondents; this field was optional so the other 43 left it blank "
                "— themes below describe this self-selected subsample of 18, not all eligible respondents).",
        "n_answered": pre_n, "d": 61,
        "themes": [
            {"theme": "Switched off-platform (YouTube / Instagram / another app)", "freq": 7,
             "pct_of_answered": round(100*7/pre_n, 1),
             "paraphrase": "Several respondents said that when deciding dragged they left the app entirely — opening YouTube or Instagram instead of continuing to browse Netflix.",
             "implication": "Corroborates the C4 off-platform leak measured quantitatively; the leak destination named unprompted is consistently YouTube or social video."},
            {"theme": "Defaulted to a familiar rewatch", "freq": 3,
             "pct_of_answered": round(100*3/pre_n, 1),
             "paraphrase": "Some respondents said they gave up searching and put on something they'd already seen rather than picking something new.",
             "implication": "A 'quick rewatch' shortcut already exists informally; the prototype's 'shows already watched' component maps directly onto this coping behaviour."},
            {"theme": "Time pressure from the meal itself", "freq": 3,
             "pct_of_answered": round(100*3/pre_n, 1),
             "paraphrase": "A few respondents described the meal finishing, or food going cold, before they had settled on something to watch.",
             "implication": "The meal is a hard deadline, not just a mood — supports treating 'meal-window cost' as a real cost, not only an annoyance rating."},
            {"theme": "No problem — decides in advance", "freq": 2,
             "pct_of_answered": round(100*2/pre_n, 1),
             "paraphrase": "A couple of respondents said they never face this because they choose what to watch before sitting down.",
             "implication": "Direct qualitative echo of the C3 falsifier segment; this behaviour is a real substitute, not just a survey artifact."},
            {"theme": "Browsed without resolving (decision paralysis)", "freq": 2,
             "pct_of_answered": round(100*2/pre_n, 1),
             "paraphrase": "A couple of respondents described browsing around — food content, or simply not having a next show queued — without landing on anything.",
             "implication": "Supports a queueing/continuation feature, not just faster search, for the post-finale moment."},
            {"theme": "Co-viewing / social constraint", "freq": 1,
             "pct_of_answered": round(100*1/pre_n, 1),
             "paraphrase": "One respondent noted difficulty finding something suitable to watch with parents.",
             "implication": "A minority but distinct segment (shared viewing) whose friction is about suitability, not volume of choice; too small a signal to size here."},
        ],
    },
    "post_one_thing": {
        "base": "of 37 post respondents, 35 gave a substantive answer to 'what is the ONE thing that would make you actually use it'.",
        "n_answered": post_thing_n, "d": 37,
        "themes": [
            {"theme": "Better / more personalised recommendations", "freq": 13,
             "pct_of_answered": round(100*13/post_thing_n, 1),
             "paraphrase": "The largest single group asked for recommendations more closely matched to their own taste and watch history, several explicitly contrasting this with the prototype's current suggestions.",
             "implication": "Recommendation relevance is the single biggest lever on stated adoption — consistent with the weak 32.4% top-box headline desirability; this is the primary 'improve' target, not a new component."},
            {"theme": "Mood-based filtering valued / requested", "freq": 7,
             "pct_of_answered": round(100*7/post_thing_n, 1),
             "paraphrase": "A number of respondents pointed to the mood filter as the thing they want more of or that already works for them.",
             "implication": "Corroborates the quantitative component-usefulness ranking, where mood filters is the second most-cited useful part."},
            {"theme": "Adapting to meal context (episode length / time of day)", "freq": 3,
             "pct_of_answered": round(100*3/post_thing_n, 1),
             "paraphrase": "A few respondents wanted the row to account for how long they actually have — for example shorter episodes so the show can finish with the meal.",
             "implication": "A concrete, buildable refinement: surface episode runtime and bias toward meal-length content."},
            {"theme": "Less cognitive effort / fewer choices to weigh", "freq": 3,
             "pct_of_answered": round(100*3/post_thing_n, 1),
             "paraphrase": "Some respondents said the appeal is simply not having to think — clicking something already picked for them.",
             "implication": "Validates the core mechanic (pre-narrowing choice) independent of recommendation quality."},
            {"theme": "Short-form / snackable content style", "freq": 2,
             "pct_of_answered": round(100*2/post_thing_n, 1),
             "paraphrase": "A couple of respondents compared the desired experience to short-form video feeds such as YouTube Shorts.",
             "implication": "A different product shape (bite-sized clips) than the current best-episode-pick mechanic; worth flagging as a distinct idea to test, not folding into the current feature."},
            {"theme": "Interface / discoverability friction (unlabeled thumbnails)", "freq": 1,
             "pct_of_answered": round(100*1/post_thing_n, 1),
             "paraphrase": "One respondent found it hard to identify shows from cover art alone and wanted titles shown.",
             "implication": "Minor UI fix, low cost, plausibly affects the 'about the same' speed-perception segment."},
            {"theme": "Already decides in advance — feature doesn't apply", "freq": 1,
             "pct_of_answered": round(100*1/post_thing_n, 1),
             "paraphrase": "One respondent restated that they plan ahead regardless of platform, so the feature has little to add for them.",
             "implication": "Same falsifier segment reappearing in the post survey — this group is unlikely to adopt regardless of iteration."},
            {"theme": "Off-topic or non-committal answers", "freq": 5,
             "pct_of_answered": round(100*5/post_thing_n, 1),
             "paraphrase": "A handful of answers were non-answers or unrelated one-word replies (e.g. uncertainty about the question, or unrelated words).",
             "implication": "Signals response-quality noise in this open field; treat single-word answers as low-confidence evidence."},
        ],
    },
    "post_confusion": {
        "base": "only 4 of 37 post respondents reported anything confusing or in the way; 33 left this blank or wrote 'no' / 'nothing'.",
        "n_answered": post_conf_n, "d": 37,
        "themes": [
            {"theme": "Prototype fidelity blurred the test (felt too much like real Netflix)", "freq": 2,
             "pct_of_answered": round(100*2/post_conf_n, 1),
             "paraphrase": "Two respondents said the prototype resembled the real Netflix UI closely enough that it was unclear what they were meant to be evaluating, and one wanted a brief orientation before starting.",
             "implication": "A study-design note more than a product finding: low reported confusion may partly reflect respondents not clearly distinguishing the feature from the baseline UI, which argues for treating the strongly positive reaction numbers with some caution."},
            {"theme": "Wants a persistently visible, dedicated section", "freq": 1,
             "pct_of_answered": round(100*1/post_conf_n, 1),
             "paraphrase": "One respondent suggested a clearly dedicated 'Watch While You Eat' section would reduce anxiety about finding it again.",
             "implication": "Supports a persistent placement/entry point rather than a one-off row, as a low-cost iteration."},
            {"theme": "Non-functional prototype elements", "freq": 1,
             "pct_of_answered": round(100*1/post_conf_n, 1),
             "paraphrase": "One respondent noted that some interactive elements (play buttons) weren't functional in the prototype.",
             "implication": "Expected fake-door/prototype limitation, not a product signal."},
        ],
    },
}

r["qualitative_themes"] = themes
(OUT / "results.json").write_text(json.dumps(r, indent=2, default=str), encoding="utf-8")
print("Appended qualitative_themes to results.json")
