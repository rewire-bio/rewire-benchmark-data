"""Shared record builders for the 2026-10-11 use-case literature batches (patient-RNA splicing and CNV).

Every record is built with status needs_review, and result review objects record how the value was extracted.
finalize_review then records the independent review (reviewer-scnv) on the records it approved.
"""
import csv, hashlib, json, os, re, unicodedata

TODAY = "2026-10-11"
EXTRACTOR_NOTE = ("Collector agent uc-splicing-cnv for the 2026-10-11 use-case literature pass; extraction only, "
                  "not a review. Pending an independent review-evidence pass.")
SOURCE_DESCRIPTION = "Primary source retrieved and hashed for the 2026-10-11 use-case literature pass."


def slug(s):
    s = s.lower().replace("+", " plus ").replace("%", " pct ").replace("δ", "delta").replace("ρ", "rho")
    s = "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return re.sub(r"-+", "-", s)


def num(printed):
    """Decimal string for a printed number, or None. Accepts a trailing % and a Unicode minus."""
    t = printed.strip().replace("−", "-").rstrip("%").strip()
    return t if re.fullmatch(r"-?\d+(\.\d+)?", t) else None


def shortest(raw):
    """Shortest round-trip decimal of a stored spreadsheet double, as used in earlier batches."""
    if re.fullmatch(r"-?\d+", raw):
        return raw
    return repr(float(raw)) if "e" not in repr(float(raw)).lower() else format(float(raw), "f").rstrip("0").rstrip(".")


class Batch:
    def __init__(self, folder, prefix, areas, contexts=("clinical_research",)):
        self.folder, self.prefix, self.areas, self.contexts = folder, prefix, list(areas), list(contexts)
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

    def source(self, id, name, attrs):
        return self.add({"id": id, "kind": "source", "name": name, "description": SOURCE_DESCRIPTION, "status": "needs_review",
                         "facets": self.facets(), "source_ids": [], "links": [], "attributes": attrs})

    def entity(self, kind, id, name, description, source_ids, attrs, method_types=None, links=()):
        return self.add({"id": id, "kind": kind, "name": name, "description": description, "status": "needs_review",
                         "facets": self.facets(method_types), "source_ids": list(source_ids), "links": list(links), "attributes": attrs})

    def evaluation(self, id, name, source_ids, system, assessment, data, origin, comparison, locator, missing=None, extra=None):
        attrs = {"origin": origin, "protocol": assessment, "version": "Primary source as retrieved " + TODAY,
                 "comparison": dict(comparison, protocol_id=assessment), "source_locator": locator}
        miss = dict(missing or {})
        for k, v in attrs["comparison"].items():
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
               qualifier=None, unit_detail=None, uncertainty=None, numeric=None, extra=None, value_missing=None,
               uncertainty_missing=None):
        attrs = {"metric": metric, "metric_direction": direction, "unit": unit, "printed_value": printed,
                 "source_locator": locator, "review": review}
        n = numeric if numeric is not None else num(printed)
        attrs["numeric_value"] = n
        miss = {}
        if qualifier:
            attrs["metric_qualifier"] = qualifier
        if unit_detail:
            attrs["unit_detail"] = unit_detail
        if uncertainty:
            attrs["uncertainty"] = uncertainty
        else:
            miss["uncertainty"] = uncertainty_missing or {"reason": "unreported"}
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
        return dict(sorted(counts.items()))


def extraction_review(method, method_note, sha, url):
    return {"method": method, "method_note": method_note, "reviewer": ["claude"], "reviewer_note": EXTRACTOR_NOTE,
            "date": TODAY, "artifact_sha256": sha, "retrieval_url": url,
            "note": "Extracted, not reviewed. The review-evidence pass must re-check this cell against the pinned artifact."}


def sha256(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def judgement(batch, use_case_id, use_case_name, protocol_id, protocol_name, source_ids, citation_locators, relevance,
              endpoint, rationale, constraints, limitations, headline_metric, comparison_group, comparison_title,
              stratum_label, stratum_order, reason):
    """A use-case relevance judgement claim, status needs_review (docs/use-cases.md)."""
    slug_uc = use_case_id.replace("use-case-", "")
    cid = "use-case-mapping-" + batch.prefix + "-" + protocol_id[len(batch.prefix) + 1:].replace("protocol-", "")
    loc = "; ".join(f"{c['source_id']}: {c['locator']}" for c in citation_locators)
    attrs = {"field": "links:assessed_by:" + protocol_id, "value": protocol_id, "relevance": relevance,
             "endpoint": endpoint, "rationale": rationale, "constraints": constraints, "limitations": limitations,
             "citation_locators": citation_locators, "source_locator": loc, "headline_metric": headline_metric,
             "comparison_group": comparison_group, "comparison_title": comparison_title,
             "stratum_label": stratum_label, "stratum_order": stratum_order, "reason": reason}
    return batch.claim(cid, f"Relevance of {protocol_name} to \"{use_case_name}\"", rationale, use_case_id,
                       source_ids, attrs), slug_uc


# Independent review (reviewer-scnv, 2026-10-12; docs/reviews/use-cases/splicing-cnv-use-cases-2026-10-12.md).
# The reviewer's corrections are applied in each extraction script; finalize_review then records the review.
REVIEW_DATE = "2026-10-12"
DATED_REVIEW = "docs/reviews/use-cases/splicing-cnv-use-cases-2026-10-12.md"
REVIEWER_NOTE = "Independent Claude review agent reviewer-scnv; did not extract this batch; no human review claimed"
REVIEW_METHOD = ["source-hash-verification", "independent-cell-check", "automated-source-review"]


def finalize_review(batch, reviewed_evaluations, method=REVIEW_METHOD, held=(), held_reason=""):
    """Set reviewed records to source_checked with the reviewer's review block. Records in `held` stay needs_review.

    reviewed_evaluations maps each reviewed judgement claim to the evaluation IDs the reviewer listed; it must match
    the evaluations on the judged protocol."""
    held = set(held)
    by_id = {r["id"]: r for r in batch.records}
    evals = {}
    for r in batch.records:
        if r["kind"] == "evaluation":
            pid = [l["target_id"] for l in r["links"] if l["relation"] == "assessment"][0]
            evals.setdefault(pid, []).append(r["id"])
    note = (f"Checked by reviewer-scnv against the pinned source; verdict in {DATED_REVIEW} and in this batch's review.md.")
    for r in batch.records:
        a = r["attributes"]
        if r["id"] in held:
            if "review" in a:
                a["review"]["note"] += " Held at review: " + held_reason
            if a.get("field", "").startswith("links:assessed_by:"):
                a["reason"] = "Not shown: " + held_reason + " Kept at needs_review by the independent review (" + DATED_REVIEW + ")."
            continue
        r["status"] = "source_checked"
        if r["kind"] not in ("result", "claim"):
            continue
        old = a.get("review")
        if old is None:  # claims carry no extraction review; bind to the cited source
            src = by_id[r["source_ids"][0]]["attributes"]
            old = {"artifact_sha256": src["artifact_sha256"], "retrieval_url": src["artifact_url"],
                   "method_note": "Drafted by the collector agent uc-splicing-cnv from the pinned source."}
        extra = re.search(r"Formula in the cell: .*?\.(?= The review-evidence pass)", old.get("note", ""))
        is_judgement = a.get("field", "").startswith("links:assessed_by:")
        a["review"] = {"method": list(method) + (["scope-review"] if r["kind"] == "claim" else []), "reviewer": ["claude"],
                       "reviewer_note": REVIEWER_NOTE, "date": REVIEW_DATE, "artifact_sha256": old["artifact_sha256"],
                       "retrieval_url": old["retrieval_url"], "method_note": old["method_note"],
                       "note": note + (" " + extra.group(0) if extra else "")}
        if is_judgement:
            got = sorted(evals[a["value"]])
            assert got == sorted(reviewed_evaluations[r["id"]]), (r["id"], got)
            a["reviewed_evaluations"] = got
            a["reason"] = a["reason"].replace("; pending independent review.", ". Independently reviewed in " + DATED_REVIEW + ".")
    assert set(reviewed_evaluations) <= set(by_id) and not set(reviewed_evaluations) & held


def refresh_coverage(folder):
    """Recompute the record counts, reused IDs and judgement list in coverage.json from batch.jsonl."""
    path = os.path.join(folder, "coverage.json")
    cov = json.load(open(path))
    recs = [json.loads(l) for l in open(os.path.join(folder, "batch.jsonl"))]
    ids = {r["id"] for r in recs}
    targets = {l["target_id"] for r in recs for l in r["links"]}
    cov["existing_reused"] = sorted(t for t in targets if t not in ids)
    counts = {}
    for r in recs:
        counts[r["kind"]] = counts.get(r["kind"], 0) + 1
    cov["new_record_counts"] = dict(sorted(counts.items()))
    evals = {}
    for r in recs:
        if r["kind"] == "evaluation":
            pid = [l["target_id"] for l in r["links"] if l["relation"] == "assessment"][0]
            evals.setdefault(pid, []).append(r["id"])
    old = {j["claim_id"]: j for j in cov["judgements"]}
    cov["judgements"] = []
    for r in recs:
        a = r["attributes"]
        if r["kind"] == "claim" and a.get("field", "").startswith("links:assessed_by:"):
            j = dict(old[r["id"]])
            j.update(relevance=a["relevance"], status=r["status"], evaluation_ids=sorted(evals[a["value"]]))
            cov["judgements"].append(j)
    with open(path, "w") as f:
        f.write(json.dumps(cov, indent=1, ensure_ascii=False) + "\n")
