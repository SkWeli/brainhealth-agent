import pandas as pd

def load_csv(path):
    df = pd.read_csv(path)

    papers = []
    for i, row in df.iterrows():
        doi = str(row.get("DOI", "")).strip()
        uid = doi if doi else f"P{i}"

        papers.append({
            "uid": uid,
            "title": str(row.get("Title", "")),
            "abstract": str(row.get("Abstract Note", "")),
            "year": row.get("Publication Year", None),
            "doi": doi,
            "source": "zotero"
        })

    return papers
