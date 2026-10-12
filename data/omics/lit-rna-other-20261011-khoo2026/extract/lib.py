"""Shared record builders for the 2026-10-11 rna and other-omics literature batches.

Each extractor parses a pinned artifact, asserts the printed row and column labels, and calls
these helpers. Every record is written with status needs_review; review is a separate pass.
"""
import csv, json, os, re

DATE = "2026-10-11"
PENDING = "Pending independent review."
DECLARED_EVAL = {"dataset_version", "split", "adaptation", "aggregation", "budget", "metric_implementation"}


def fmt(x):
    """Shortest decimal string for a stored spreadsheet number (round-trips to the stored double)."""
    if isinstance(x, str):
        return x
    s = repr(float(x))
    if s.endswith(".0"):
        s = s[:-2]
    if "e" in s or "E" in s:
        s = format(float(x), "f").rstrip("0").rstrip(".")
    return s


def numeric(printed):
    """Decimal string from a printed cell, or None when the cell is not a plain number."""
    p = printed.strip().replace("−", "-").replace("%", "").strip()
    m = re.fullmatch(r"[+-]?(\d+(\.\d*)?|\.\d+)", p)
    return p.lstrip("+") if m else None


class Batch:
    def __init__(self, folder, prefix, areas, contexts=("research",)):
        self.folder, self.p = folder, prefix
        self.areas, self.contexts = list(areas), list(contexts)
        self.records, self.rows, self.ids = [], [], set()

    def _facets(self, method_types=None, areas=True):
        f = {}
        if areas:
            f["areas"] = self.areas
            f["contexts"] = self.contexts
        if method_types:
            f["method_types"] = list(method_types)
        return f

    def add(self, rec):
        assert rec["id"] not in self.ids, rec["id"]
        assert re.fullmatch(r"[a-z0-9][a-z0-9-]{0,254}", rec["id"]), rec["id"]
        self.ids.add(rec["id"])
        self.records.append(rec)
        return rec["id"]

    def rid(self, kind, key):
        key = re.sub(r"[^a-z0-9]+", "-", key.lower()).strip("-")
        return f"{self.p}-{kind}-{key}"

    def source(self, key, name, attrs, description):
        return self.add({"id": self.rid("source", key), "kind": "source", "name": name,
                         "description": description, "status": "needs_review",
                         "facets": self._facets(), "source_ids": [], "links": [], "attributes": attrs})

    def system(self, kind, key, name, description, src, method_types, attrs):
        """A new family-level model or method record."""
        a = {"reported_name": name, "entity_level": "family" if kind == "model" else "method"}
        a.update(attrs)
        a.setdefault("missing_metadata", {"version": {"reason": "inapplicable",
                                                      "note": "Family record; versions are on configurations"}})
        return self.add({"id": self.rid(kind, key), "kind": kind, "name": name, "description": description,
                         "status": "needs_review", "facets": self._facets(method_types), "source_ids": [src],
                         "links": [], "attributes": a})

    def configuration(self, key, name, of_id, src, method_types, attrs, fm_eligible):
        a = {"reported_name": name, "foundation_model_eligible": fm_eligible}
        a.update(attrs)
        links = [{"relation": "configuration_of", "target_id": of_id}] if of_id else []
        return self.add({"id": self.rid("config", key), "kind": "configuration", "name": name,
                         "description": f"{name} as run in the cited comparison.", "status": "needs_review",
                         "facets": self._facets(method_types), "source_ids": src if isinstance(src, list) else [src],
                         "links": links, "attributes": a})

    def dataset(self, key, name, description, src, attrs):
        return self.add({"id": self.rid("data", key), "kind": "dataset", "name": name, "description": description,
                         "status": "needs_review", "facets": self._facets(), "source_ids": [src], "links": [],
                         "attributes": attrs})

    def protocol(self, key, name, description, src, data_id, attrs):
        return self.add({"id": self.rid("protocol", key), "kind": "protocol", "name": name,
                         "description": description, "status": "needs_review", "facets": self._facets(),
                         "source_ids": [src], "links": [{"relation": "uses_data", "target_id": data_id}],
                         "attributes": attrs})

    def evaluation(self, key, name, config_id, protocol_id, data_id, src, origin, comparison, locator,
                   missing=None, extra=None):
        comp = {k: comparison.get(k) for k in ("protocol_id", "dataset_version", "split", "population", "inputs",
                                               "adaptation", "metric_implementation", "aggregation", "budget")}
        comp["protocol_id"] = protocol_id
        # Only declared evaluation keys can carry a missing reason; other null comparison fields stay null.
        miss = {k: {"reason": "unreported"} for k, v in comp.items() if v is None and k in DECLARED_EVAL}
        miss.update(missing or {})
        a = {"origin": origin, "protocol": protocol_id, "version": f"Primary source as retrieved {DATE}",
             "comparison": comp, "source_locator": locator}
        if miss:
            a["missing_metadata"] = miss
        a.update(extra or {})
        return self.add({"id": self.rid("eval", key), "kind": "evaluation", "name": name,
                         "description": "Published comparison; transcribed, not reproduced.", "status": "needs_review",
                         "facets": self._facets(), "source_ids": [src],
                         "links": [{"relation": "system", "target_id": config_id},
                                   {"relation": "assessment", "target_id": protocol_id},
                                   {"relation": "data", "target_id": data_id}], "attributes": a})

    def result(self, key, eval_id, src, metric, direction, unit, printed, locator, review, qualifier=None,
               uncertainty=None, num="auto", name=None, extra=None):
        a = {"metric": metric, "metric_direction": direction, "unit": unit, "printed_value": printed}
        n = numeric(printed) if num == "auto" else num
        a["numeric_value"] = n
        if n is None:
            del a["numeric_value"]
        if qualifier:
            a["metric_qualifier"] = qualifier
        a["source_locator"] = locator
        miss = {}
        if uncertainty:
            a["uncertainty"] = uncertainty
        else:
            miss["uncertainty"] = {"reason": "unreported"}
        if n is None:
            miss["numeric_value"] = {"reason": "inapplicable", "note": "Printed cell is not a plain number"}
        if miss:
            a["missing_metadata"] = miss
        a["review"] = review
        a.update(extra or {})
        rid = self.add({"id": self.rid("result", key), "kind": "result", "name": name or f"{key} {metric}",
                        "description": "Reported measurement transcribed from the pinned source. Not independently reproduced.",
                        "status": "needs_review", "facets": {}, "source_ids": [src],
                        "links": [{"relation": "evaluation", "target_id": eval_id}], "attributes": a})
        self.rows.append([rid, src, locator, printed, "result"])
        return rid

    def claim(self, key, subject_id, field, value, locator, src, review, extra=None):
        a = {"field": field, "value": value, "source_locator": locator, "review": review}
        a.update(extra or {})
        rid = self.add({"id": self.rid("claim", key), "kind": "claim", "name": f"{field}: {subject_id}",
                        "description": "Descriptive fact transcribed from the pinned source.", "status": "needs_review",
                        "facets": {}, "source_ids": [src], "links": [{"relation": "subject", "target_id": subject_id}],
                        "attributes": a})
        self.rows.append([rid, src, locator, value, "claim"])
        return rid

    def write(self):
        os.makedirs(self.folder, exist_ok=True)
        recs = sorted(self.records, key=lambda r: r["id"])
        with open(os.path.join(self.folder, "batch.jsonl"), "w") as f:
            for r in recs:
                f.write(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n")
        with open(os.path.join(self.folder, "claims.csv"), "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["record_id", "source_id", "locator", "printed_value", "review_scope"])
            for row in sorted(self.rows):
                w.writerow(row)
        kinds = {}
        for r in recs:
            kinds[r["kind"]] = kinds.get(r["kind"], 0) + 1
        return kinds


def review(method, sha, url, note):
    return {"method": method, "date": DATE, "artifact_sha256": sha, "retrieval_url": url,
            "note": f"{note.strip()} {PENDING}"}


REVIEW_DATE = "2026-10-12"
REVIEWED_AT = "2026-10-12T07:44:06Z"  # reviewer-ro-2 report time; the only judgement claims are in its batches
REVIEW_METHODS = ["source-hash-verification", "deterministic-table-parse", "independent-cell-check"]


def finalise(records, reviewer_id, method_note, disputed=None, methods=None, judgement_note=None, judgement_reason=None,
             extractor="lit-rna-otheromics"):
    """Apply the independent review to every record, after the reviewer's corrections have been
    applied in the extractor: status source_checked (or disputed, with the reviewer's
    source_warnings), and the reviewer's review block on each result and relevance judgement.
    The reviewer's text is in review.md."""
    disputed = dict(disputed or {})
    reviewer_note = f"Claude review agent {reviewer_id}, independent of the extractor {extractor}; no human review claimed"
    for r in records:
        a = r["attributes"]
        if r["kind"] == "claim" and str(a.get("field", "")).startswith("links:assessed_by:"):
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
