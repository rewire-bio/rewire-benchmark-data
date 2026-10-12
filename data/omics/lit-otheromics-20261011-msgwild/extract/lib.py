"""Shared record builders for the 2026-10-11 RNA and other-omics literature batches.

Every record is written with status needs_review. Result review objects record how the value
was extracted; they are not a review sign-off.
"""
import csv, hashlib, json, os, re, unicodedata

TODAY = "2026-10-11"
AREAS = ["rna-transcriptomes"]
EXTRACTOR_NOTE = "Collector agent lit-rna-otheromics for the 2026-10-11 RNA and other-omics literature pass; extraction only, not a review. Pending an independent review-evidence pass."


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
        self.records, self.ids, self.claim_rows = [], set(), []
        self.areas = list(areas or AREAS)

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

    def source(self, id, name, attrs, description="Primary source retrieved and hashed for the 2026-10-11 RNA and other-omics literature pass."):
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


REVIEW_DATE = "2026-10-12"
REVIEWED_AT = "2026-10-12T07:44:06Z"  # reviewer-ro-2 report time; the only judgement claims are in its batches
REVIEW_METHODS = ["source-hash-verification", "deterministic-table-parse", "independent-cell-check"]


def finalise(records, reviewer_id, method_note, disputed=None, methods=None, judgement_note=None, judgement_reason=None,
             extractor="lit-rna-otheromics", defer_judgements=False):
    """Apply the independent review to every record, after the reviewer's corrections have been
    applied in the extractor: status source_checked (or disputed, with the reviewer's
    source_warnings), and the reviewer's review block on each result and relevance judgement.
    The reviewer's text is in review.md."""
    disputed = dict(disputed or {})
    reviewer_note = f"Claude review agent {reviewer_id}, independent of the extractor {extractor}; no human review claimed"
    for r in records:
        a = r["attributes"]
        if r["kind"] == "claim" and str(a.get("field", "")).startswith("links:assessed_by:"):
            if defer_judgements:
                # The use-case link is deferred, so the judgement stays an unlinked draft with the
                # reviewer's text and no review block until the link is added.
                continue
            r["status"] = "source_checked"
            if judgement_reason:
                a["reason"] = judgement_reason
            a["review"] = {"method": ["ai-assisted-source-review", "scope-review"], "method_note": judgement_note,
                           "reviewer": ["claude"], "reviewer_note": reviewer_note,
                           "reviewed_at": REVIEWED_AT, "note": "Automated review; not human scientific review."}
            continue
        r["status"] = "source_checked"
        if r["kind"] != "result":
            continue
        old = a["review"]
        extraction = old.get("method_note") or old["note"].replace(" Pending independent review.", "")
        note = "Extraction: " + extraction + " Independent review " + REVIEW_DATE + \
               ": value, locator, metric, unit, direction and linked configuration and protocol checked."
        if r["id"] in disputed:
            r["status"] = "disputed"
            a["source_warnings"] = list(disputed.pop(r["id"]))
            note += " Disputed: see source_warnings."
        a["review"] = {"method": list(methods(r) if methods else REVIEW_METHODS), "method_note": method_note,
                       "reviewer": ["claude"], "reviewer_note": reviewer_note, "date": REVIEW_DATE,
                       "artifact_sha256": old["artifact_sha256"], "retrieval_url": old["retrieval_url"], "note": note}
    assert not disputed, sorted(disputed)
