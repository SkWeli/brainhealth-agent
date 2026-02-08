import pandas as pd

def load_csv(path):
    df = pd.read_csv(path)

    papers = []
    for i, row in df.iterrows():
        papers.append({
            "uid": f"P{i}",
            "title": str(row.get("title", "")),
            "abstract": str(row.get("abstract", "")),
            "year": row.get("year", None),
            "doi": row.get("doi", "")
        })
    return papers
