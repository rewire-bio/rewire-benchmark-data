"""Record builders shared by the 2026-10-11 execution use-case extraction scripts.

Every record is written with status needs_review; the extractor never marks its own work reviewed.
"""
import json
import os
import re

USE_CASE = "use-case-diagnostic-genomics-model-execution"
DATE = "2026-10-11"
AREAS = ["dna-genomes"]


def slug(text):
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", text.lower())).strip("-")


def source(id, name, url, artifact_url, version, retrieved_at, sha, doi, status, licence, media, description, note=None):
    attrs = {
        "url": url, "artifact_url": artifact_url, "version": version, "retrieved_at": retrieved_at,
        "artifact_sha256": sha, "doi": doi, "publication_status": status, "licence": licence, "media_type": media,
    }
    if note:
        attrs["source_locator"] = note
    return {"id": id, "kind": "source", "name": name, "description": description, "status": "needs_review",
            "facets": {"areas": AREAS, "contexts": ["research"]}, "source_ids": [], "links": [], "attributes": attrs}


def extraction_review(methods, method_note, note):
    return {
        "method": methods, "method_note": method_note, "reviewer": ["claude"],
        "reviewer_note": "Extractor: Claude (Opus 5.5) research agent uc-execution; not independent review; no human review claimed",
        "date": DATE, "note": note,
    }


def entity(id, kind, name, description, sources, attrs, links=(), facets=None):
    return {"id": id, "kind": kind, "name": name, "description": description, "status": "needs_review",
            "facets": facets if facets is not None else {"areas": AREAS, "contexts": ["research"]},
            "source_ids": list(sources), "links": [dict(relation=r, target_id=t) for r, t in links],
            "attributes": attrs}


def result(id, name, sources, evaluation, metric, direction, unit, printed, numeric, locator, review,
           qualifier=None, unit_detail=None, uncertainty=None, missing=None):
    attrs = {"metric": metric, "metric_direction": direction, "unit": unit}
    if qualifier:
        attrs["metric_qualifier"] = qualifier
    if unit_detail:
        attrs["unit_detail"] = unit_detail
    attrs["printed_value"] = printed
    attrs["numeric_value"] = numeric
    attrs["source_locator"] = locator
    if uncertainty:
        attrs["uncertainty"] = uncertainty
    else:
        attrs["missing_metadata"] = {"uncertainty": missing or {"reason": "unreported"}}
    attrs["review"] = review
    return {"id": id, "kind": "result", "name": name,
            "description": "Reported measurement transcribed from the pinned source. Not independently reproduced.",
            "status": "needs_review", "facets": {}, "source_ids": list(sources),
            "links": [{"relation": "evaluation", "target_id": evaluation}], "attributes": attrs}


def judgement(id, protocol, protocol_name, sources, relevance, endpoint, rationale, constraints, limitations,
              citation_locators, group, title, stratum_label, stratum_order, headline_metric):
    return {
        "id": id, "kind": "claim",
        "name": f'Relevance of {protocol_name} to "Select an execution workflow for large-scale diagnostic genomics"',
        "description": rationale, "status": "needs_review", "facets": {}, "source_ids": list(sources),
        "links": [{"relation": "subject", "target_id": USE_CASE}],
        "attributes": {
            "field": f"links:assessed_by:{protocol}", "value": protocol, "relevance": relevance,
            "endpoint": endpoint, "rationale": rationale, "constraints": constraints, "limitations": limitations,
            "revision": 1,
            "reason": "Add primary-source execution evidence from the diagnostic genomics execution literature pass (2026-10-11).",
            "citation_locators": citation_locators,
            "source_locator": "; ".join(f"{c['source_id']}: {c['locator']}" for c in citation_locators),
            "comparison_group": group, "comparison_title": title, "headline_metric": headline_metric,
            **({"stratum_label": stratum_label, "stratum_order": stratum_order} if stratum_label else {}),
            "review": {
                "method": ["automated-source-review"], "reviewer": ["claude"],
                "reviewer_note": "Claude (Opus 5.5) research agent uc-execution drafted this judgement; independent review pending",
                "date": DATE, "note": "Draft relevance judgement by the extractor; needs independent review.",
            },
        },
    }


def write(batch_dir, records, claims_rows):
    ids = [r["id"] for r in records]
    import collections
    dups = [i for i, c in collections.Counter(ids).items() if c > 1]
    assert not dups, dups[:5]
    with open(os.path.join(batch_dir, "batch.jsonl"), "w") as f:
        for r in sorted(records, key=lambda r: r["id"]):
            f.write(json.dumps(r, ensure_ascii=False, sort_keys=False) + "\n")
    with open(os.path.join(batch_dir, "claims.csv"), "w") as f:
        import csv
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["record_id", "source_id", "locator", "printed_value", "review_scope"])
        for row in sorted(claims_rows):
            w.writerow(row)
    return len(records)
