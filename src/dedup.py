import re
from rapidfuzz import fuzz

def norm_doi(doi: str) -> str:
    if not doi:
        return ""
    doi = doi.strip().lower()
    doi = doi.replace("https://doi.org/", "").replace("http://doi.org/", "")
    doi = doi.replace("doi:", "").strip()
    return doi

def norm_title(title: str) -> str:
    if not title:
        return ""
    t = title.lower().strip()
    t = re.sub(r"\s+", " ", t)
    t = re.sub(r"[^\w\s]", "", t)  # remove punctuation
    return t

def is_probable_duplicate(a, b, title_threshold=95):
    """
    Returns (bool, score) based on title similarity.
    """
    ta = norm_title(a.get("title", ""))
    tb = norm_title(b.get("title", ""))

    if not ta or not tb:
        return False, 0

    score = fuzz.token_set_ratio(ta, tb)

    # optionally require same year if both available
    ya = a.get("year")
    yb = b.get("year")
    same_year = (ya is None or yb is None or str(ya) == str(yb))

    return (score >= title_threshold and same_year), score

def deduplicate(papers, title_threshold=95):
    """
    Dedup strategy:
    1) DOI exact match (strongest)
    2) Title similarity + (optional year)
    Returns: (deduped_list, report_rows)
    """
    report = []
    kept = []
    seen_doi = {}

    # 1) DOI exact
    for p in papers:
        doi = norm_doi(p.get("doi", ""))
        p["doi"] = doi

        if doi:
            if doi in seen_doi:
                report.append({
                    "duplicate_uid": p.get("uid"),
                    "kept_uid": seen_doi[doi].get("uid"),
                    "match_type": "doi",
                    "score": 100,
                    "duplicate_title": p.get("title", ""),
                    "kept_title": seen_doi[doi].get("title", ""),
                })
                continue
            else:
                seen_doi[doi] = p
                kept.append(p)
        else:
            kept.append(p)

    # 2) Title similarity for those without DOI (or still potential dups)
    final = []
    for p in kept:
        found_dup = False
        for k in final:
            dup, score = is_probable_duplicate(p, k, title_threshold=title_threshold)
            if dup:
                report.append({
                    "duplicate_uid": p.get("uid"),
                    "kept_uid": k.get("uid"),
                    "match_type": "title",
                    "score": score,
                    "duplicate_title": p.get("title", ""),
                    "kept_title": k.get("title", ""),
                })
                found_dup = True
                break

        if not found_dup:
            final.append(p)

    return final, report
