"""Shared record builders for the genomic foundation model literature pass (2026-10-11).

Each batch script under data/omics/gfm2-20261011-*/extract/ imports this module, builds its
records from the pinned source text and writes batch.jsonl and claims.csv. Every record is
written with status needs_review: the extractor never marks its own work reviewed.
"""
import csv
import json
import re
from pathlib import Path

DATE = "2026-10-11"
EXTRACTOR_NOTE = "Extractor: Claude (Opus 5.5) research agent lit-gfm-2; not independent review; no human review claimed"


def num(printed):
    """Decimal string for a printed number, or None if the cell is not numeric."""
    s = printed.replace("⋆", "").replace("*", "").replace(",", "").strip()
    s = s.replace("−", "-")
    if s.endswith("%"):
        s = s[:-1]
    if re.fullmatch(r"-?\d+(\.\d+)?", s):
        return s
    if re.fullmatch(r"-?\.\d+", s):
        return s.replace(".", "0.", 1) if not s.startswith("-") else "-0" + s[1:]
    return None


class Batch:
    def __init__(self, prefix, source_id, areas=("dna-genomes",), contexts=("research",)):
        self.prefix = prefix
        self.source_id = source_id
        self.areas = list(areas)
        self.contexts = list(contexts)
        self.records = {}
        self.claim_rows = []

    def rid(self, *parts):
        slug = "-".join(re.sub(r"[^a-z0-9]+", "-", str(p).lower()).strip("-") for p in parts if p != "")
        return f"{self.prefix}-{slug}"

    def add(self, record):
        if record["id"] in self.records:
            raise ValueError("duplicate id " + record["id"])
        self.records[record["id"]] = record
        return record["id"]

    def _base(self, rid, kind, name, description, facets=None, links=None, attributes=None, sources=None):
        return {
            "id": rid,
            "kind": kind,
            "name": name,
            "description": description,
            "status": "needs_review",
            "facets": facets if facets is not None else {"areas": self.areas, "contexts": self.contexts},
            "source_ids": sources if sources is not None else [self.source_id],
            "links": links or [],
            "attributes": attributes or {},
        }

    def source(self, name, description, attributes):
        return self.add(self._base(self.source_id, "source", name, description, sources=[], attributes=attributes))

    def model(self, key, name, description, locator, reported_name=None, extra=None):
        attrs = {"reported_name": reported_name or name, "entity_level": "family", "source_locator": locator,
                 "missing_metadata": {"version": {"reason": "inapplicable", "note": "Family record; versions are on configurations"}}}
        attrs.update(extra or {})
        facets = {"areas": self.areas, "contexts": self.contexts, "method_types": ["foundation_model"]}
        return self.add(self._base(self.rid("model", key), "model", name, description, facets=facets, attributes=attrs))

    def method(self, key, name, description, locator, method_type="conventional_pipeline"):
        attrs = {"reported_name": name, "entity_level": "method", "source_locator": locator,
                 "missing_metadata": {"version": {"reason": "inapplicable", "note": "Family record; versions are on configurations"}}}
        facets = {"areas": self.areas, "contexts": self.contexts, "method_types": [method_type]}
        return self.add(self._base(self.rid("method", key), "method", name, description, facets=facets, attributes=attrs))

    def config(self, key, name, of, method_type, reported_name, locator, version=None, version_missing=None,
               parameters=None, fm=True, extra=None, description=None):
        attrs = {"reported_name": reported_name, "foundation_model_eligible": fm, "source_locator": locator}
        if parameters:
            attrs["parameters"] = parameters
        if version:
            attrs["version"] = version
        else:
            attrs["missing_metadata"] = {"version": version_missing or {"reason": "unreported", "note": "No checkpoint revision is printed"}}
        attrs.update(extra or {})
        facets = {"areas": self.areas, "contexts": self.contexts, "method_types": [method_type]}
        links = [{"relation": "configuration_of", "target_id": t} for t in ([of] if isinstance(of, str) else of)]
        return self.add(self._base(self.rid("config", key), "configuration", name,
                                   description or f"{name}, as evaluated in the cited comparison.", facets=facets, links=links, attributes=attrs))

    def dataset(self, key, name, description, attributes):
        return self.add(self._base(self.rid("data", key), "dataset", name, description, attributes=attributes))

    def protocol(self, key, name, description, attributes, data_id=None, extra_links=None):
        links = [{"relation": "uses_data", "target_id": data_id}] if data_id else []
        links += extra_links or []
        return self.add(self._base(self.rid("protocol", key), "protocol", name, description, links=links, attributes=attributes))

    def evaluation(self, key, name, config_id, protocol_id, data_id, origin, comparison, locator, limitations=None, extra=None):
        comp = {"protocol_id": protocol_id}
        comp.update(comparison)
        for field in ("dataset_version", "split", "population", "inputs", "adaptation", "metric_implementation", "aggregation", "budget"):
            comp.setdefault(field, None)
        attrs = {"origin": origin, "protocol": protocol_id, "version": f"Primary source as retrieved {DATE}",
                 "comparison": comp, "source_locator": locator}
        if limitations:
            attrs["limitations"] = limitations
        attrs.update(extra or {})
        links = [{"relation": "system", "target_id": config_id}, {"relation": "assessment", "target_id": protocol_id},
                 {"relation": "data", "target_id": data_id}]
        return self.add(self._base(self.rid("eval", key), "evaluation", name, "Published comparison; transcribed, not reproduced.",
                                   links=links, attributes=attrs))

    def result(self, key, eval_id, metric, printed, locator, direction="higher", unit="fraction", qualifier=None,
               unit_detail=None, uncertainty=None, method=("pdf-text-parse",), method_note=None, note=None, extra=None):
        attrs = {"metric": metric, "metric_direction": direction, "unit": unit, "printed_value": printed,
                 "numeric_value": num(printed), "source_locator": locator}
        if qualifier:
            attrs["metric_qualifier"] = qualifier
        if unit_detail:
            attrs["unit_detail"] = unit_detail
        if uncertainty:
            attrs["uncertainty"] = uncertainty
        else:
            attrs["missing_metadata"] = {"uncertainty": {"reason": "unreported"}}
        review = {"method": list(method), "reviewer": ["claude"], "reviewer_note": EXTRACTOR_NOTE, "date": DATE,
                  "note": note or "Extraction only; pending independent review."}
        if method_note:
            review["method_note"] = method_note
        attrs["review"] = review
        attrs.update(extra or {})
        rid = self.rid("result", key)
        self.add(self._base(rid, "result", f"{key} {metric}", "Reported measurement transcribed from the pinned source. Not independently reproduced.",
                            facets={}, links=[{"relation": "evaluation", "target_id": eval_id}], attributes=attrs))
        self.claim_rows.append([rid, self.source_id, locator, printed, "result"])
        return rid

    def claim(self, key, subject_id, field, value, locator):
        attrs = {"field": field, "value": value, "source_locator": locator,
                 "review": {"method": ["transcription"], "reviewer": ["claude"], "reviewer_note": EXTRACTOR_NOTE, "date": DATE,
                            "note": "Extraction only; pending independent review."}}
        rid = self.rid("claim", key)
        self.add(self._base(rid, "claim", f"{field}: {subject_id}", "Descriptive fact transcribed from the pinned source.",
                            facets={}, links=[{"relation": "subject", "target_id": subject_id}], attributes=attrs))
        self.claim_rows.append([rid, self.source_id, locator, value, "claim"])
        return rid

    def write(self, folder):
        folder = Path(folder)
        rows = [self.records[k] for k in sorted(self.records)]
        with open(folder / "batch.jsonl", "w") as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        with open(folder / "claims.csv", "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["record_id", "source_id", "locator", "printed_value", "review_scope"])
            for row in sorted(self.claim_rows):
                w.writerow(row)
        counts = {}
        for r in rows:
            counts[r["kind"]] = counts.get(r["kind"], 0) + 1
        return counts


def table_rows(lines, start_marker, end_marker):
    """Lines between two markers (exclusive), for parsing a table from pdftotext -layout output."""
    start = next(i for i, l in enumerate(lines) if start_marker in l)
    end = next(i for i in range(start + 1, len(lines)) if end_marker in lines[i])
    return lines[start + 1:end]
