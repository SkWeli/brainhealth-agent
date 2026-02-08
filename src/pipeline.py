import os
import glob
import pandas as pd
from tqdm import tqdm

from ingest import load_csv
from dedup import deduplicate
from screen_rules import rule_screen

RAW_DIR = "data/raw"
PROCESSED_OUT = "data/processed/papers_deduped.csv"
DEDUP_REPORT = "outputs/logs/dedup_report.csv"
SCREEN_OUT = "outputs/exports/screened_results.csv"

def run():
    # 1) Load all CSVs inside data/raw (or just papers.csv if that’s all you have)
    csv_files = sorted(glob.glob(os.path.join(RAW_DIR, "*.csv")))
    if not csv_files:
        raise FileNotFoundError("No CSV files found in data/raw/")

    all_papers = []
    for f in csv_files:
        papers = load_csv(f)
        # tag source file name for traceability
        for p in papers:
            p["source_file"] = os.path.basename(f)
        all_papers.extend(papers)

    imported_n = len(all_papers)

    # 2) Deduplicate
    deduped, report = deduplicate(all_papers, title_threshold=95)
    deduped_n = len(deduped)
    removed_n = imported_n - deduped_n

    # 3) Save deduped set + dedup report
    os.makedirs("data/processed", exist_ok=True)
    os.makedirs("outputs/logs", exist_ok=True)
    os.makedirs("outputs/exports", exist_ok=True)

    pd.DataFrame(deduped).to_csv(PROCESSED_OUT, index=False)
    pd.DataFrame(report).to_csv(DEDUP_REPORT, index=False)

    # 4) Screen (rules)
    results = []
    for p in tqdm(deduped, desc="Screening"):
        decision, factors, outcomes, reason, evidence = rule_screen(p["title"], p.get("abstract", ""))

        results.append({
            "uid": p.get("uid", ""),
            "title": p.get("title", ""),
            "year": p.get("year", ""),
            "doi": p.get("doi", ""),
            "source_file": p.get("source_file", ""),
            "decision": decision,
            "factors": ";".join(factors),
            "outcomes": ";".join(outcomes),
            "reason": reason,
            "evidence": evidence
        })

    df = pd.DataFrame(results)
    df.to_csv(SCREEN_OUT, index=False)

    # 5) PRISMA-style counts (baseline)
    counts = df["decision"].value_counts().to_dict()
    print("\n--- PRISMA-style counts (baseline) ---")
    print("Records imported:", imported_n)
    print("Duplicates removed:", removed_n)
    print("Records after dedup:", deduped_n)
    print("Title/Abstract screened:", deduped_n)
    print("Included:", counts.get("include", 0))
    print("Excluded:", counts.get("exclude", 0))
    print("Maybe:", counts.get("maybe", 0))
    print("\nSaved screened results:", SCREEN_OUT)
    print("Saved deduped papers:", PROCESSED_OUT)
    print("Saved dedup report:", DEDUP_REPORT)

if __name__ == "__main__":
    run()
