from ingest import load_csv
from screen_rules import rule_screen
import pandas as pd
from tqdm import tqdm

INPUT_FILE = "data/raw/papers.csv"
OUTPUT_FILE = "outputs/exports/screened_results.csv"

def run():
    papers = load_csv(INPUT_FILE)
    results = []

    for p in tqdm(papers):
        decision, factors, outcomes, reason, evidence = rule_screen(
            p["title"], p["abstract"]
        )

        results.append({
            "uid": p["uid"],
            "title": p["title"],
            "decision": decision,
            "factors": ";".join(factors),
            "outcomes": ";".join(outcomes),
            "reason": reason,
            "evidence": evidence
        })

    df = pd.DataFrame(results)
    df.to_csv(OUTPUT_FILE, index=False)
    print("Saved:", OUTPUT_FILE)

if __name__ == "__main__":
    run()
