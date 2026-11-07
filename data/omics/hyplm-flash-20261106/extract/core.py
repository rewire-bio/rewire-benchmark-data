"""Shared helpers for HyPLM-Flash evaluations and results."""

from entities import AREAS, B, BASELINES, CONFIG_BF16, CONFIG_INT8, SRC_REPORT, record

PAGES = {}

REVIEW = {
    "method": ["pdf-text-parse", "deterministic-table-parse", "source-hash-verification"],
    "method_note": "pdftotext -layout text layer of the pinned PDF, parsed by "
                   "data/omics/hyplm-flash-20261106/extract/parse.py, which checks the PDF hash and "
                   "asserts every row label, metric label and cell count, and asserts every value "
                   "printed twice is equal in both places. Printed cell text is kept exactly.",
    "reviewer": ["claude"],
    "reviewer_note": "Extracted by a Claude agent for issue #233. Extraction record only: no "
                     "independent or human review is claimed, and review-evidence has not run.",
    "date": "2026-11-06",
}
NO_INTERVAL = {"uncertainty": {
    "reason": "unreported",
    "note": "Section 4 says intervals are paired bootstrap intervals; none is printed here."}}


def page(key):
    return f"page {PAGES[key]} of {PAGES['count']}"


def clean(token):
    return token.replace(",", "").replace("−", "-")


def config(label):
    label = label.rstrip("†")
    if label == "HyPLM-Flash":
        return CONFIG_BF16, "hyplm-flash"
    if label == "INT8":
        return CONFIG_INT8, "hyplm-flash-int8"
    return f"{B}-config-{BASELINES[label][0]}", BASELINES[label][0]


def evaluation(protocol_slug, data, label, locator, overrides=None):
    config_id, config_slug = config(label)
    comp = {
        "protocol_id": f"{B}-protocol-{protocol_slug}",
        "dataset_version": "As used in the HyPLM technical report (2026-10-12)",
        "split": "Test split as printed in Table 4",
        "population": "The test split of this task as printed in Table 4",
        "inputs": "Protein amino-acid sequence alone; no structure, alignment or retrieved homologs",
        "adaptation": "Frozen BF16 representations; the encoder is not fine-tuned",
        "metric_implementation": "As stated in the protocol",
        "aggregation": "One value per model on the test split",
        "budget": "One forward pass per sequence or masked position; no fine-tuning",
    }
    comp.update(overrides or {})
    attrs = {"origin": "author_reported", "protocol": f"{B}-protocol-{protocol_slug}",
             "version": "HyPLM technical report, 2026-10-12, retrieved at commit 0dcc533c",
             "comparison": comp, "source_locator": locator}
    missing = {f"comparison.{k}": {"reason": "unreported"} for k, v in comp.items() if v is None}
    if missing:
        attrs["missing_metadata"] = missing
    eval_id = f"{B}-eval-{protocol_slug}-{config_slug}"
    rec = record(eval_id, "evaluation", f"{label.rstrip(chr(8224))} on {protocol_slug} (HyPLM report)",
                 "Author-reported evaluation transcribed from the pinned report; run by the "
                 "developer of HyPLM-Flash and not reproduced by Rewire.", attrs,
                 links=[{"relation": "system", "target_id": config_id},
                        {"relation": "assessment", "target_id": f"{B}-protocol-{protocol_slug}"},
                        {"relation": "data", "target_id": data}],
                 facets={"areas": AREAS, "contexts": ["research"]})
    return eval_id, rec


def result(rid, name, eval_id, printed, metric, unit, direction, qualifier, locator,
           uncertainty=None, **extra):
    attrs = {"metric": metric, "metric_direction": direction, "unit": unit,
             "metric_qualifier": qualifier, "printed_value": printed,
             "numeric_value": clean(printed).lstrip("+").rstrip("×"),
             "source_locator": locator, "review": dict(REVIEW)}
    attrs.update({k: v for k, v in extra.items() if v})
    if uncertainty:
        attrs["uncertainty"] = uncertainty
    else:
        attrs["missing_metadata"] = dict(NO_INTERVAL)
    return record(rid, "result", name, "Value transcribed exactly as printed in the pinned report. "
                  "Author-reported; not reproduced by Rewire.", attrs,
                  links=[{"relation": "evaluation", "target_id": eval_id}], facets={})
