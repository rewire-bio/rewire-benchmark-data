"""Shared record builders for the 2026-10-11 oncology use-case literature batches.

Every record is written with status needs_review. Result review objects record how the value
was extracted; they are not a review sign-off.
"""
import csv, hashlib, json, os, re, unicodedata

TODAY = "2026-10-11"
EXTRACTOR_NOTE = "Collector agent for the 2026-10-11 oncology use-case literature pass (uc-oncology); extraction only, not a review. Pending an independent review-evidence pass."
SOMATIC_UC = "use-case-tumour-dna-somatic-variant-detection"
FUSION_UC = "use-case-tumour-rna-fusion-detection"


def slug(s):
    s = s.lower().replace("+", " plus ").replace("%", " pct ")
    s = "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return re.sub(r"-+", "-", s)


def num(printed):
    """Decimal string for a printed number, or None. Accepts a trailing %, thousands commas and a Unicode minus."""
    t = printed.strip().replace("−", "-").rstrip("%").strip().replace(",", "")
    return t if re.fullmatch(r"-?\d+(\.\d+)?", t) else None


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

    def source(self, id, name, attrs, description):
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
        n = None if numeric is False else (numeric if numeric is not None else num(printed))
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

    def judgement(self, use_case, use_case_name, protocol, protocol_name, source_ids, relevance, endpoint, rationale, limitations,
                  citation_locators, group, title, stratum, order, headline, constraints=None, reason=None):
        """Relevance judgement claim (needs_review) for one protocol and one use case."""
        short = protocol[len(self.prefix) + len("-protocol-"):] if protocol.startswith(self.prefix + "-protocol-") else protocol
        cid = "use-case-mapping-" + self.prefix + "-" + short
        attrs = {"field": "links:assessed_by:" + protocol, "value": protocol, "relevance": relevance, "endpoint": endpoint,
                 "rationale": rationale,
                 "constraints": constraints or ["Inspect every linked evaluation's source locator before citing a result.",
                                                "Do not combine this mapping's evaluations with any other protocol's results; truth sets, specimens, sequencing and caller versions differ between sources."],
                 "limitations": limitations, "citation_locators": citation_locators,
                 "source_locator": "; ".join(f"{c['source_id']}: {c['locator']}" for c in citation_locators),
                 "headline_metric": headline, "reason": reason or "Add a relevance judgement from the 2026-10-11 oncology use-case literature pass.",
                 "comparison_group": group, "comparison_title": title, "stratum_label": stratum, "stratum_order": order}
        self.claim_rows.append([cid, source_ids[0], attrs["source_locator"], protocol, "judgement"])
        self.add({"id": cid, "kind": "claim", "name": f"Relevance of {protocol_name} to \"{use_case_name}\"", "description": rationale,
                  "status": "needs_review", "facets": {}, "source_ids": list(source_ids),
                  "links": [{"relation": "subject", "target_id": use_case}], "attributes": attrs})
        return cid

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


def read_tsv(path):
    import io
    raw = open(path, "rb").read()
    text = (__import__("gzip").decompress(raw) if path.endswith(".gz") else raw).decode()
    return list(csv.DictReader(io.StringIO(text), delimiter="\t"))
