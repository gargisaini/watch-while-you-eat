"""Exports the KPI framework in results.json to a flat CSV table (deliverable #2)."""
import json
from pathlib import Path

import pandas as pd

OUT = Path(__file__).resolve().parent
r = json.loads((OUT / "results.json").read_text(encoding="utf-8"))
kf = r["kpi_framework"]

rows = []
for k in kf["core_kpis"] + [kf["guardrail_kpi"]]:
    rows.append({
        "ID": k["id"], "Category": k["category"], "KPI Name": k["name"],
        "Definition": k["definition"], "Formula": k["formula"],
        "Numerator": k["numerator"], "Denominator": k["denominator"],
        "Value (%)": k["value_pct"], "Sample size (n)": k["sample_size"],
        "Source question": k["source_question"], "Interpretation": k["interpretation"],
        "Limitation": k["limitation"],
    })
df = pd.DataFrame(rows)
df.to_csv(OUT / "kpi_table.csv", index=False)
print(df[["ID", "KPI Name", "Numerator", "Denominator", "Value (%)"]].to_string(index=False))
