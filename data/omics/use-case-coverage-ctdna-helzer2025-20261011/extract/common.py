"""Shared record builders for the 2026-10-11 plasma ctDNA literature batches (one copy per batch folder)."""
import csv, hashlib, json, os
from decimal import Decimal

FACETS = {"areas": ["dna-genomes"], "contexts": ["clinical_research"]}
UC_METH, UC_FRAG = "use-case-plasma-ctdna-methylation", "use-case-plasma-ctdna-fragmentomics"
Q_METH = "Which measured methylation workflow detects tumour-derived plasma DNA and, where separately supported, identifies tissue of origin?"
Q_FRAG = "Which fragmentomics workflow detects tumour-derived plasma DNA under realistic low tumour fractions and fixed false-positive constraints?"
EXTRACTOR = "Claude (Opus 5.5) extraction agent uc-ctdna; extraction record, not an independent review"
# Independent review (reviewer-ctdna, 2026-10-12; docs/reviews/use-cases/plasma-ctdna-use-cases-2026-10-12.md).
REVIEWER = "Separate Claude review agent (reviewer-ctdna), independent of the extractor uc-ctdna; no human review claimed"
REVIEW_DATE = "2026-10-12"
REVIEW_DOC = "docs/reviews/use-cases/plasma-ctdna-use-cases-2026-10-12.md"


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def expect(got, value, where):
    if got != value:
        raise SystemExit(f"{where}: expected {value!r}, found {got!r}")


def shortest(raw):
    """Shortest round-trip decimal of a stored General-format XLSX number."""
    s = repr(float(raw))
    if s.endswith(".0"):
        s = s[:-2]
    if "e" in s or "E" in s:
        s = format(Decimal(s), "f")
    return s


class Batch:
    def __init__(self, prefix, date):
        self.P, self.DATE = prefix, date
        self.records, self.claim_rows = [], []

    def rec(self, id_, kind, name, description, source_ids, links=None, attributes=None, facets=None, status="needs_review"):
        r = {"id": id_, "kind": kind, "name": name, "description": description, "status": status,
             "facets": FACETS if facets is None else facets, "source_ids": source_ids,
             "links": links or [], "attributes": attributes or {}}
        self.records.append(r)
        return r

    def review(self, method, path, url, note):
        return {"method": method, "reviewer": ["claude"], "date": self.DATE, "reviewer_note": EXTRACTOR,
                "artifact_sha256": sha(path), "retrieval_url": url, "note": note + " Pending independent review."}

    def source(self, id_, name, description, attrs):
        self.rec(id_, "source", name, description, [], attributes=attrs)

    def method(self, id_, name, description, source_ids, mtypes, locator, reported=None):
        self.rec(id_, "method", name, description, source_ids,
                 attributes={"reported_name": reported or name, "entity_level": "method", "source_locator": locator,
                             "missing_metadata": {"version": {"reason": "inapplicable", "note": "Family record; settings are on configurations"}}},
                 facets={**FACETS, "method_types": list(mtypes)})

    def configuration(self, id_, name, of, source_ids, reported, locator, mtypes, access, parameters,
                      version=None, version_note=None, fm=False, extra=None):
        attrs = {"reported_name": reported, "foundation_model_eligible": fm, "source_locator": locator,
                 "parameters": parameters, "access_reuse": access}
        if version:
            attrs["version"] = version
        else:
            attrs["missing_metadata"] = {"version": {"reason": "unreported", "note": version_note or "No version or release of this configuration is printed"}}
        attrs.update(extra or {})
        self.rec(id_, "configuration", name, "Configuration as run in the cited comparison.", source_ids,
                 [{"relation": "configuration_of", "target_id": of}], attrs, facets={**FACETS, "method_types": list(mtypes)})

    def evaluation(self, id_, name, config, protocol, dataset, source_ids, origin, comparison, locator, limitations=None, missing=None):
        attrs = {"origin": origin, "protocol": protocol, "version": f"Primary source as retrieved {self.DATE}",
                 "comparison": {"protocol_id": protocol, **comparison}, "source_locator": locator}
        if limitations:
            attrs["limitations"] = limitations
        miss = dict(missing or {})
        for k, v in comparison.items():
            if v is None and f"comparison.{k}" not in miss:
                miss[f"comparison.{k}"] = {"reason": "unreported"}
        if miss:
            attrs["missing_metadata"] = miss
        self.rec(id_, "evaluation", name, "Published comparison; transcribed, not reproduced.", source_ids,
                 [{"relation": "system", "target_id": config}, {"relation": "assessment", "target_id": protocol},
                  {"relation": "data", "target_id": dataset}], attrs)

    def result(self, id_, eval_id, source_ids, locator, pv, metric, qualifier, unit, review, uncertainty=None,
               extra=None, direction="higher", numeric=None):
        attrs = {"metric": metric, "metric_qualifier": qualifier, "metric_direction": direction, "unit": unit,
                 "printed_value": pv, "numeric_value": numeric if numeric is not None else format(Decimal(pv), "f"),
                 "source_locator": locator, "review": review}
        if uncertainty:
            attrs["uncertainty"] = uncertainty
        else:
            attrs["missing_metadata"] = {"uncertainty": {"reason": "unreported"}}
        attrs.update(extra or {})
        self.rec(id_, "result", f"{eval_id.replace(self.P + '-eval-', '')} {metric} ({qualifier})",
                 "Reported measurement transcribed from the pinned source. Not independently reproduced.",
                 source_ids, [{"relation": "evaluation", "target_id": eval_id}], attrs, facets={})
        self.claim_rows.append([id_, source_ids[-1], locator, pv, "result"])

    def claim(self, id_, subject, field, value, source_ids, locator, review):
        self.rec(id_, "claim", f"{field}: {subject}", "Descriptive fact transcribed from the pinned source.", source_ids,
                 [{"relation": "subject", "target_id": subject}],
                 {"field": field, "value": value, "source_locator": locator, "review": review}, facets={})
        self.claim_rows.append([id_, source_ids[-1], locator, value, "claim"])

    def judgement(self, id_, uc, question, protocol, relevance, endpoint, rationale, constraints, limitations, cites,
                  reason, group, title, metric, label=None, order=None):
        self.rec(id_, "claim", f"Relevance of {protocol} to \"{question}\"", rationale, sorted({s for s, _ in cites}),
                 [{"relation": "subject", "target_id": uc}],
                 {"field": f"links:assessed_by:{protocol}", "value": protocol, "relevance": relevance, "endpoint": endpoint,
                  "rationale": rationale, "constraints": constraints, "limitations": limitations,
                  "citation_locators": [{"source_id": s, "locator": loc} for s, loc in cites],
                  "source_locator": "; ".join(f"{s}: {loc}" for s, loc in cites), "revision": 1, "reason": reason,
                  "comparison_group": group, "comparison_title": title, "headline_metric": metric,
                  **({"stratum_label": label, "stratum_order": order} if label else {})}, facets={})

    def finalize(self, note, result_method, reviewed, notes=None, claim_method=None, artifact=None):
        """Apply the independent review: every record becomes source_checked (a record set to another status, such as
        disputed, keeps it), and results, claims and judgements carry the reviewer's review block. With no `result_method`
        a result keeps its extraction method between the reviewer's hash and cell checks. `reviewed` maps each judgement to
        the evaluations the reviewer checked; `artifact` overrides the reviewed artifact hash and URL."""
        notes = notes or {}
        claim_method = claim_method or ["source-hash-verification", "independent-cell-check", "scope-review"]
        for r in self.records:
            if r["status"] == "needs_review":
                r["status"] = "source_checked"
            a = r["attributes"]
            if r["kind"] not in ("result", "claim"):
                continue
            old = a.get("review")
            judgement = a.get("field", "").startswith("links:assessed_by:")
            if r["kind"] == "result":
                method = result_method or ["source-hash-verification"] + old["method"] + ["independent-cell-check"]
            else:
                method = claim_method
            rev = {"method": method, "reviewer": ["claude"],
                   "reviewer_note": REVIEWER, "date": REVIEW_DATE}
            if old:
                rev.update({"artifact_sha256": old["artifact_sha256"], "retrieval_url": old["retrieval_url"]})
            if artifact and (old or judgement):
                rev.update(artifact)
            if old:
                rev["method_note"] = old["note"].replace(" Pending independent review.", "")
            rev["note"] = note + (" " + notes[r["id"]] if r["id"] in notes else "")
            a["review"] = rev
            if judgement:
                a["reviewed_evaluations"] = sorted(reviewed[r["id"]])
                a["reason"] = a["reason"] + f" Independently reviewed in {REVIEW_DOC}."
        missing = set(reviewed) - {r["id"] for r in self.records}
        if missing:
            raise SystemExit(f"Reviewed judgements not in batch: {sorted(missing)}")

    def write(self, batch_dir, links):
        self.records.sort(key=lambda r: r["id"])
        # The store keeps missing_metadata keys sorted (shared/omics/attributes.ts normalizeAttributes).
        for r in self.records:
            if "missing_metadata" in r["attributes"]:
                r["attributes"]["missing_metadata"] = dict(sorted(r["attributes"]["missing_metadata"].items()))
        ids = [r["id"] for r in self.records]
        if len(ids) != len(set(ids)):
            from collections import Counter
            raise SystemExit(f"Duplicate IDs: {[k for k, v in Counter(ids).items() if v > 1][:5]}")
        with open(os.path.join(batch_dir, "batch.jsonl"), "w") as f:
            for r in self.records:
                f.write(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n")
        with open(os.path.join(batch_dir, "claims.csv"), "w", newline="") as f:
            w = csv.writer(f, lineterminator="\n")
            w.writerow(["record_id", "source_id", "locator", "printed_value", "review_scope"])
            for row in sorted(self.claim_rows):
                w.writerow(row)
        with open(os.path.join(batch_dir, "use-case-links.json"), "w") as f:
            json.dump({"note": f"assessed_by links on the use_case records for the judgement claims; added after the independent review ({REVIEW_DOC}).",
                       "links": links}, f, indent=1)
            f.write("\n")
        from collections import Counter
        print(dict(Counter(r["kind"] for r in self.records)), len(self.records))
