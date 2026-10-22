"""Shared record helpers for the de novo binder design extraction (#176).

Every record this batch writes is produced here or by one of the per-source
modules. Nothing is marked reviewed: statuses are `needs_review` and the review
blocks name the extraction agent and the method, so a separate review agent can
check each value against the pinned artifact.
"""

PREFIX = "uc-binder-20261022"
DATE = "2026-10-22"
REVIEWED_AT = "2026-10-22T12:00:00Z"
AGENT_NOTE = "Claude extraction agent; no human review claimed"
EXTRACT_NOTE = (
    "Extraction pass only. Review sign-off, review.json and any status change are left to a "
    "separate review agent (docs/collection.md section 5)."
)

AREAS = ["proteins-complexes", "protein-structure"]
CONTEXTS = ["research"]


def rid(*parts: str) -> str:
    return "-".join([PREFIX, *parts])


def review(source, method, how, note=""):
    """Review block for a result or claim.

    `source` is the source record this value was read from, `method` a list of
    review-method concept keys, `how` a plain sentence saying how it was read.
    """
    block = {
        "method": list(method),
        "reviewer": ["claude"],
        "reviewer_note": AGENT_NOTE,
        "date": DATE,
        "reviewed_at": REVIEWED_AT,
        "artifact_sha256": source["attributes"]["artifact_sha256"],
        "retrieval_url": source["attributes"].get("artifact_url") or source["attributes"]["url"],
        "method_note": how,
        "note": " ".join([EXTRACT_NOTE, note]).strip(),
    }
    return block


def record(rec_id, kind, name, description, *, status="needs_review", facets=None,
           source_ids=(), links=(), attributes=None):
    return {
        "id": rec_id,
        "kind": kind,
        "name": name,
        "description": description,
        "status": status,
        "facets": facets if facets is not None else {},
        "source_ids": list(source_ids),
        "links": list(links),
        "attributes": attributes if attributes is not None else {},
    }


def facets(method_types=None, areas=None):
    out = {"areas": list(areas) if areas else list(AREAS), "contexts": list(CONTEXTS)}
    if method_types:
        out["method_types"] = list(method_types)
    return out


def link(relation, target_id):
    return {"relation": relation, "target_id": target_id}


def evaluation(rec_id, name, description, *, source, system, assessment, data,
               origin, version, comparison, locator, missing=None, attrs=None):
    a = {
        "origin": origin,
        "protocol": assessment,
        "version": version,
        "comparison": comparison,
        "source_locator": locator,
    }
    if attrs:
        a.update(attrs)
    if missing:
        a["missing_metadata"] = missing
    return record(
        rec_id, "evaluation", name, description,
        facets={"areas": list(AREAS), "contexts": list(CONTEXTS)},
        source_ids=[source["id"]],
        links=[link("system", system), link("assessment", assessment), link("data", data)],
        attributes=a,
    )


def result(rec_id, name, description, *, source, evaluation_id, printed, numeric, metric,
           direction, unit, locator, review_block, qualifier=None, unit_detail=None,
           numerator=None, denominator=None, denominator_note=None, missing=None,
           extra=None, source_ids=None):
    a = {
        "metric": metric,
        "metric_direction": direction,
        "unit": unit,
        "printed_value": printed,
        "numeric_value": numeric,
        "source_locator": locator,
        "review": review_block,
    }
    if qualifier:
        a["metric_qualifier"] = qualifier
    if unit_detail:
        a["unit_detail"] = unit_detail
    if numerator is not None:
        a["numerator"] = numerator
    if denominator is not None:
        a["denominator"] = denominator
    if denominator_note:
        a["denominator_note"] = denominator_note
    if extra:
        a.update(extra)
    if missing:
        a["missing_metadata"] = missing
    return record(
        rec_id, "result", name, description,
        source_ids=source_ids or [source["id"]],
        links=[link("evaluation", evaluation_id)],
        attributes=a,
    )


def claim(rec_id, name, description, *, source, subject, field, value, locator, review_block,
          source_ids=None, extra=None, status="needs_review"):
    a = {
        "field": field,
        "value": value,
        "source_locator": locator,
        "review": review_block,
    }
    if extra:
        a.update(extra)
    return record(
        rec_id, "claim", name, description, status=status,
        source_ids=source_ids or [source["id"]],
        links=[link("subject", subject)],
        attributes=a,
    )


# Comparison objects. A field the source does not state is null, which blocks
# automatic comparison; that is the intended behaviour (docs/collection.md s4).
def comparison(protocol_id, *, dataset_version=None, split=None, population=None, inputs=None,
               adaptation=None, metric_implementation=None, aggregation=None, budget=None):
    return {
        "protocol_id": protocol_id,
        "dataset_version": dataset_version,
        "split": split,
        "population": population,
        "inputs": inputs,
        "adaptation": adaptation,
        "metric_implementation": metric_implementation,
        "aggregation": aggregation,
        "budget": budget,
    }


def missing(**kwargs):
    """missing_metadata map: field -> {reason, note}."""
    out = {}
    for field, spec in kwargs.items():
        key = field.replace("__", ".")
        if isinstance(spec, str):
            out[key] = {"reason": spec}
        else:
            reason, note = spec
            out[key] = {"reason": reason, "note": note}
    return out
