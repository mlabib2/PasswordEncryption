#!/usr/bin/env python3
import os
import re
import sys
import math
import warnings
from typing import Dict, Optional, Tuple, List

import pandas as pd

warnings.simplefilter("ignore", UserWarning)

# ============================================================
# >>> SET YOUR FOLDER PATH HERE (absolute or relative) <<<
# Example: BASE_DIR = "/Users/mahirlabib/Desktop/HK (RN)"
# If left as None, you can also provide the path when running:
#    python aggregate_scores.py "HK (RN)"
# ============================================================
BASE_DIR = "/Users/mahirlabib/Desktop/Darwin_Buffet_Stock_Pick_Project-2/Financials_Analyzed/HK_Stock"
# ============================================================

TARGET_LABELS = [
    "5 year net asset growth (20 points)",
    "5 year avg roce (30 points)",
    "5 year avg ebit margin (15 points)",
    "5 year avergae gearing (20 points)",   # kept original spelling
    "5 year op income growth (15 points)",
]

def normalize(s: str) -> str:
    s = s.lower()
    s = re.sub(r"average", "avergae", s)
    s = re.sub(r"[^a-z0-9\s\(\)\.-]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

LABEL_ALIASES = {
    "5 year net asset growth (20 points)": [
        "5 year net asset growth (20 points)",
        "5y net asset growth (20 points)",
        "five year net asset growth (20 points)",
    ],
    "5 year avg roce (30 points)": [
        "5 year avg roce (30 points)",
        "5 year average roce (30 points)",
    ],
    "5 year avg ebit margin (15 points)": [
        "5 year avg ebit margin (15 points)",
        "5 year average ebit margin (15 points)",
    ],
    "5 year avergae gearing (20 points)": [
        "5 year avergae gearing (20 points)",
        "5 year average gearing (20 points)",
    ],
    "5 year op income growth (15 points)": [
        "5 year op income growth (15 points)",
        "5 year operating income growth (15 points)",
    ],
}

def is_number(x) -> bool:
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return False
    try:
        float(str(x).replace(",", ""))
        return True
    except Exception:
        return False

def to_float(x) -> Optional[float]:
    try:
        return float(str(x).replace(",", ""))
    except Exception:
        return None

def load_all_sheets(path: str) -> List[pd.DataFrame]:
    xls = pd.ExcelFile(path)
    out = []
    for sheet in xls.sheet_names:
        try:
            df = pd.read_excel(path, sheet_name=sheet, header=None)
            out.append(df)
        except Exception:
            pass
    return out

def iter_cells(df: pd.DataFrame):
    for r in range(df.shape[0]):
        for c in range(df.shape[1]):
            yield r, c, df.iat[r, c]

def match_label(cell_val: str) -> Optional[str]:
    if not isinstance(cell_val, str):
        return None
    cell_norm = normalize(cell_val)
    for canonical, aliases in LABEL_ALIASES.items():
        for alias in aliases:
            if normalize(alias) == cell_norm:
                return canonical
    for canonical in TARGET_LABELS:
        canon_norm = normalize(canonical)
        if canon_norm in cell_norm or cell_norm in canon_norm:
            return canonical
    return None

def find_value_in_same_row(df: pd.DataFrame, row: int, col: int) -> Optional[float]:
    for c in range(col + 1, df.shape[1]):
        v = df.iat[row, c]
        if is_number(v):
            return to_float(v)
    for c in range(col - 1, -1, -1):
        v = df.iat[row, c]
        if is_number(v):
            return to_float(v)
    return None

def extract_scores_from_file(path: str) -> Dict[str, Optional[float]]:
    dfs = load_all_sheets(path)
    results = {k: None for k in TARGET_LABELS}
    found = set()

    for df in dfs:
        for r, c, v in iter_cells(df):
            if isinstance(v, str) and v.strip():
                canonical = match_label(v)
                if canonical and canonical not in found:
                    num = find_value_in_same_row(df, r, c)
                    if num is None and r + 1 < df.shape[0]:
                        for cc in range(c, df.shape[1]):
                            vv = df.iat[r + 1, cc]
                            if is_number(vv):
                                num = to_float(vv)
                                break
                    results[canonical] = num
                    found.add(canonical)
            if len(found) == len(TARGET_LABELS):
                break
        if len(found) == len(TARGET_LABELS):
            break
    return results

def main():
    base_dir = BASE_DIR or (sys.argv[1] if len(sys.argv) > 1 else ".")
    companies = sorted([d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))])

    rows = []
    for company in companies:
        main_xlsx = os.path.join(base_dir, company, f"{company}.xlsx")
        row = {
            "company": company,
            "5 year net asset growth (20 points)": None,
            "5 year avg ROCE (30 points)": None,
            "5 year avg EBIT margin (15 points)": None,
            "5 year avergae gearing (20 points)": None,
            "5 year Op income growth (15 points)": None,
        }
        if os.path.exists(main_xlsx):
            try:
                scores = extract_scores_from_file(main_xlsx)
                row["5 year net asset growth (20 points)"] = scores.get("5 year net asset growth (20 points)")
                row["5 year avg ROCE (30 points)"] = scores.get("5 year avg roce (30 points)")
                row["5 year avg EBIT margin (15 points)"] = scores.get("5 year avg ebit margin (15 points)")
                row["5 year avergae gearing (20 points)"] = scores.get("5 year avergae gearing (20 points)")
                row["5 year Op income growth (15 points)"] = scores.get("5 year op income growth (15 points)")
            except Exception:
                pass
        rows.append(row)

    df = pd.DataFrame(rows, columns=[
        "company",
        "5 year net asset growth (20 points)",
        "5 year avg ROCE (30 points)",
        "5 year avg EBIT margin (15 points)",
        "5 year avergae gearing (20 points)",
        "5 year Op income growth (15 points)",
    ])
    out_path = os.path.join(base_dir, "scores_summary.csv")
    df.to_csv(out_path, index=False, encoding="utf-8")
    print(f"Wrote {out_path}")
    print(df.head(20).to_string(index=False))

if __name__ == "__main__":
    main()