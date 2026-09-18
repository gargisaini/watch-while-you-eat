"""Renders results.json's qualitative_themes block to a markdown deliverable."""
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
DELIV = OUT.parent / "deliverables"
r = json.loads((OUT / "results.json").read_text(encoding="utf-8"))
qt = r["qualitative_themes"]

TITLES = {
    "pre_giveup_story": "Pre-survey — 'Describe the last time you gave up trying to find something at a meal'",
    "post_one_thing": "Post-survey — 'What is the ONE thing that would make you actually use it?'",
    "post_confusion": "Post-survey — 'Anything that confused you or got in the way?'",
}

lines = ["# Qualitative Theme Analysis", "",
         "Manually coded from the actual response text in `analysis/clean_pre.csv` / `clean_post.csv` "
         "(open_* columns). No quotes are invented; each theme's illustration is a paraphrase of what "
         "respondents actually wrote, not a verbatim quote. Themes are ranked by frequency within the "
         "respondents who gave a substantive answer to that field — these fields were optional, so the base "
         "is the answering subsample, not all eligible/post respondents (noted per field).", ""]

for key, block in qt.items():
    lines.append(f"## {TITLES.get(key, key)}")
    lines.append("")
    lines.append(f"Base: {block['base']}")
    lines.append("")
    lines.append("| Theme | Freq (n) | % of answered | Paraphrased insight | Product implication |")
    lines.append("|---|---|---|---|---|")
    for t in block["themes"]:
        lines.append(f"| {t['theme']} | {t['freq']} | {t['pct_of_answered']}% | {t['paraphrase']} | {t['implication']} |")
    lines.append("")

(DELIV / "qualitative_analysis.md").write_text("\n".join(lines), encoding="utf-8")
print("Wrote deliverables/qualitative_analysis.md")
