"""Shared record builders for the 2026-10-11 cells-spatial and networks-mechanistic literature batches.

Every record is built with status needs_review. Result review objects record how the value
was extracted; they are not a review sign-off. finalise() applies the independent review after the
reviewer's corrections have been applied in the extractor.
"""
import csv, hashlib, json, os, re, unicodedata

TODAY = "2026-10-11"
AREAS = ["single-cell"]
EXTRACTOR_NOTE = "Collector agent lit-cells-networks for the 2026-10-11 cells-spatial and networks-mechanistic literature pass; extraction only, not a review. Pending an independent review-evidence pass."


def slug(s):
    s = s.lower().replace("+", " plus ").replace("%", " pct ").replace("δ", "delta").replace("ρ", "rho")
    s = "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return re.sub(r"-+", "-", s)


def num(printed):
    """Decimal string for a printed number, or None. Accepts a trailing % and a Unicode minus."""
    t = printed.strip().replace("−", "-").rstrip("%").strip()
    return t if re.fullmatch(r"-?\d+(\.\d+)?", t) else None


class Batch:
    def __init__(self, folder, prefix, contexts=("research",), areas=None):
        self.folder, self.prefix, self.contexts = folder, prefix, list(contexts)
        self.areas = list(areas or AREAS)
        self.records, self.ids, self.claim_rows = [], set(), []

    def rid(self, *parts):
        return self.prefix + "-" + "-".join(slug(p) for p in parts if p)

    def facets(self, method_types=None):
        f = {"areas": self.areas, "contexts": self.contexts}
        if method_types:
            f["method_types"] = method_types
        return f

    def add(self, rec):
        if rec["id"] in self.ids:
            raise ValueError("duplicate id " + rec["id"])
        self.ids.add(rec["id"])
        self.records.append(rec)
        return rec["id"]

    def source(self, id, name, attrs, description="Primary source retrieved and hashed for the 2026-10-11 cells-spatial and networks-mechanistic literature pass."):
        return self.add({"id": id, "kind": "source", "name": name, "description": description, "status": "needs_review",
                         "facets": self.facets(), "source_ids": [], "links": [], "attributes": attrs})

    def entity(self, kind, id, name, description, source_ids, attrs, method_types=None, links=()):
        return self.add({"id": id, "kind": kind, "name": name, "description": description, "status": "needs_review",
                         "facets": self.facets(method_types), "source_ids": list(source_ids), "links": list(links), "attributes": attrs})

    def evaluation(self, id, name, source_ids, system, assessment, data, origin, comparison, locator, missing=None, extra=None):
        attrs = {"origin": origin, "protocol": assessment, "version": "Primary source as retrieved " + TODAY,
                 "comparison": comparison, "source_locator": locator}
        miss = dict(missing or {})
        for k, v in comparison.items():
            if v is None and "comparison." + k not in miss:
                miss["comparison." + k] = {"reason": "unreported"}
        if miss:
            attrs["missing_metadata"] = miss
        if extra:
            attrs.update(extra)
        return self.add({"id": id, "kind": "evaluation", "name": name, "description": "Published comparison transcribed from the pinned source; not reproduced.",
                         "status": "needs_review", "facets": self.facets(), "source_ids": list(source_ids),
                         "links": [{"relation": "system", "target_id": system}, {"relation": "assessment", "target_id": assessment},
                                   {"relation": "data", "target_id": data}], "attributes": attrs})

    def result(self, id, name, source_id, source_ids, evaluation, printed, metric, direction, unit, locator, review,
               qualifier=None, unit_detail=None, uncertainty=None, numeric=None, extra=None, value_missing=None):
        attrs = {"metric": metric, "metric_direction": direction, "unit": unit, "printed_value": printed,
                 "source_locator": locator, "review": review}
        n = numeric if numeric is not None else num(printed)
        attrs["numeric_value"] = n
        miss = {}
        if n is None:
            miss["value"] = value_missing or {"reason": "unreported", "note": "Printed cell is not a number"}
        if qualifier:
            attrs["metric_qualifier"] = qualifier
        if unit_detail:
            attrs["unit_detail"] = unit_detail
        if uncertainty:
            attrs["uncertainty"] = uncertainty
        else:
            miss["uncertainty"] = {"reason": "unreported"}
        if miss:
            attrs["missing_metadata"] = miss
        if extra:
            attrs.update(extra)
        self.claim_rows.append([id, source_id, locator, printed, "result"])
        return self.add({"id": id, "kind": "result", "name": name, "description": "Reported measurement transcribed from the pinned source. Not independently reproduced.",
                         "status": "needs_review", "facets": {}, "source_ids": list(source_ids),
                         "links": [{"relation": "evaluation", "target_id": evaluation}], "attributes": attrs})

    def claim(self, id, name, description, subject, source_ids, attrs, source_id=None):
        self.claim_rows.append([id, source_id or source_ids[0], attrs.get("source_locator", ""), str(attrs.get("value", ""))[:200], "claim"])
        return self.add({"id": id, "kind": "claim", "name": name, "description": description, "status": "needs_review",
                         "facets": {}, "source_ids": list(source_ids), "links": [{"relation": "subject", "target_id": subject}], "attributes": attrs})

    def write(self, extra_files=None):
        os.makedirs(self.folder, exist_ok=True)
        for r in self.records:  # the store keeps missing_metadata keys sorted
            mm = r["attributes"].get("missing_metadata")
            if mm:
                r["attributes"]["missing_metadata"] = dict(sorted(mm.items()))
        with open(os.path.join(self.folder, "batch.jsonl"), "w") as f:
            for r in sorted(self.records, key=lambda r: r["id"]):
                f.write(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n")
        with open(os.path.join(self.folder, "claims.csv"), "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["record_id", "source_id", "locator", "printed_value", "review_scope"])
            for row in sorted(self.claim_rows):
                w.writerow(row)
        for name, text in (extra_files or {}).items():
            with open(os.path.join(self.folder, name), "w") as f:
                f.write(text)
        counts = {}
        for r in self.records:
            counts[r["kind"]] = counts.get(r["kind"], 0) + 1
        return counts


def extraction_review(method, method_note, sha, url):
    return {"method": method, "method_note": method_note, "reviewer": ["claude"], "reviewer_note": EXTRACTOR_NOTE,
            "date": TODAY, "artifact_sha256": sha, "retrieval_url": url,
            "note": "Extracted, not reviewed. The review-evidence pass must re-check this cell against the pinned artifact."}


def sha256(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def judgement(batch, use_case, protocol, short, source_ids, relevance, endpoint, rationale, constraints, limitations, citation_locators,
              headline_metric, comparison_group, comparison_title, stratum_label, stratum_order, evaluations, use_case_name):
    """Relevance judgement claim for one protocol, status needs_review; the assessed_by link is proposed in use-case-links.json, not applied."""
    cid = "use-case-mapping-" + batch.prefix + "-" + short
    batch.claim_rows.append([cid, source_ids[0], "; ".join(c["locator"] for c in citation_locators), relevance, "judgement"])
    batch.add({"id": cid, "kind": "claim", "name": f"Relevance of {stratum_label} to \"{use_case_name}\"", "description": rationale,
               "status": "needs_review", "facets": {}, "source_ids": list(source_ids), "links": [{"relation": "subject", "target_id": use_case}],
               "attributes": {"field": "links:assessed_by:" + protocol, "value": protocol, "relevance": relevance, "endpoint": endpoint,
                              "rationale": rationale, "constraints": constraints, "limitations": limitations, "citation_locators": citation_locators,
                              "source_locator": "; ".join(f"{c['source_id']}: {c['locator']}" for c in citation_locators),
                              "headline_metric": headline_metric, "comparison_group": comparison_group, "comparison_title": comparison_title,
                              "stratum_label": stratum_label, "stratum_order": stratum_order, "reviewed_evaluations": sorted(evaluations),
                              "reason": "Proposed relevance judgement from the 2026-10-11 cells-spatial and networks-mechanistic literature pass; extracted, not reviewed."}})
    return {"use_case": use_case, "relation": "assessed_by", "target_id": protocol, "judgement_claim": cid}


def write_links(folder, links):
    with open(os.path.join(folder, "use-case-links.json"), "w") as f:
        json.dump({"note": "Proposed assessed_by links to add to the use_case records after the judgement claims are reviewed. Not applied by the extractor.",
                   "links": links}, f, indent=1)
        f.write("\n")


REVIEW_DATE = "2026-10-12"
REVIEW_DOC = "docs/reviews/2026-10-12-cells-networks-batches.md"


def finalise(batch, reviewer_id, reviewed_at, review_note, source_note, result_notes=None):
    """Apply the independent review to every record: status source_checked, and the reviewer's review block on
    results, descriptive claims, sources and relevance judgements. The reviewer's text is in review.md.
    result_notes maps a result ID to a sentence the reviewer asked to add to its review note."""
    reviewer_note = f"Claude review agent {reviewer_id}, independent of the extractor lit-cells-networks; no human review claimed"
    result_notes = dict(result_notes or {})
    sources = {r["id"]: r for r in batch.records if r["kind"] == "source"}
    for r in batch.records:
        a = r["attributes"]
        r["status"] = "source_checked"
        if r["kind"] == "claim" and str(a.get("field", "")).startswith("links:assessed_by:"):
            a["reason"] = ("Add a relevance judgement for a protocol from the 2026-10-11 cells-spatial and networks-mechanistic "
                           f"literature pass, reviewed in {REVIEW_DOC}.")
            a["review"] = {"method": ["ai-assisted-source-review", "scope-review"],
                           "method_note": "Reviewer checked the endpoint against the use case's inputs, output and exclusions, the relevance rating and the limitations; every evaluation on the protocol had its values checked in the batch review. Corrections listed in review.md were applied by the extractor.",
                           "reviewer": ["claude"], "reviewer_note": reviewer_note, "reviewed_at": reviewed_at,
                           "note": "Automated review; not human scientific review."}
        elif r["kind"] == "result":
            old = a["review"]
            note = ("Extraction: " + old["method_note"].rstrip(".") + ". Independent review " + REVIEW_DATE + ": " + review_note
                    + " Corrections from the review applied by the extractor as listed in review.md.")
            if r["id"] in result_notes:
                note += " " + result_notes.pop(r["id"])
            a["review"] = {"method": ["source-hash-verification", "deterministic-table-parse", "independent-cell-check"],
                           "method_note": old["method_note"], "reviewer": ["claude"], "reviewer_note": reviewer_note,
                           "date": REVIEW_DATE, "artifact_sha256": old["artifact_sha256"], "retrieval_url": old["retrieval_url"], "note": note}
        elif r["kind"] == "claim":
            src = sources[r["source_ids"][0]]["attributes"]
            a["review"] = {"method": ["source-hash-verification", "deterministic-table-parse", "independent-cell-check"],
                           "method_note": "Transcribed from the pinned source by the extraction script.", "reviewer": ["claude"],
                           "reviewer_note": reviewer_note, "date": REVIEW_DATE, "artifact_sha256": src["artifact_sha256"],
                           "retrieval_url": src.get("artifact_url", src["url"]), "note": "Independent review " + REVIEW_DATE + ": " + review_note}
        elif r["kind"] == "source":
            a["review"] = {"method": ["source-hash-verification"], "method_note": source_note, "reviewer": ["claude"],
                           "reviewer_note": reviewer_note, "date": REVIEW_DATE}
    assert not result_notes, sorted(result_notes)
