"""Evaluations and results for HyCell: one evaluation per (configuration, protocol,
dataset), one result per printed cell. All author_reported."""

from assess import ATLAS, SUITE
from parse import PRINTED

MARK = {"b": "batch-grouped inference", "l": "trained with cell-type labels"}


def row_label(model):
    """The row label as the text layer prints it, with its superscript explained."""
    shown = PRINTED.get(model)
    if not shown:
        return f"'{model}'"
    return f"'{shown}' (printed '{model}' with superscript {shown[-1]}, {MARK[shown[-1]]})"
from models import ADAPT, SYSTEMS, adapt
from protocols import protocols
from sources import AREAS, B, SRC_REPORT, record

PAGES = {}
PROTO = {p["id"].replace(f"{B}-protocol-", ""): p["attributes"] for p in protocols()}
REVIEW = {"method": ["pdf-text-parse", "deterministic-table-parse", "source-hash-verification"],
          "method_note": "pdftotext -layout text layer of the pinned PDF, parsed by "
                         "data/omics/hycell-20261106/extract/parse.py with every row label and cell "
                         "count asserted, S checked against its stated weights, Table 3 against the "
                         "mean of Table 4, and Figure 1b's mean row against Table 3.",
          "reviewer": ["claude"],
          "reviewer_note": "Extracted by a Claude agent for issue #234. Extraction record only: no "
                           "independent or human review is claimed; review-evidence has not run.",
          "date": "2026-11-06"}
TIE = ("Not a win for either model. HyCell's S of 0.735 and Stack's 0.736 differ by 0.001 with no "
       "uncertainty printed anywhere in the report, which calls them level; Stack ran with batch "
       "labels at inference and HyCell without, so the two are not under equal conditions.")
DATA = {label: f"{B}-data-{v[0]}" for label, v in ATLAS.items()}
DATA["Cross-tissue"] = DATA["Cross-tissue immune"]


def page(key):
    return f"page {PAGES[key]} of {PAGES['count']}"


class Out:
    def __init__(self):
        self.records, self.evals = [], set()

    def add(self, slug, label, data, printed, locator, scope=None, limits=None):
        if label == "Fine-tuned":
            cfg, cslug, condition = f"{B}-config-hycell-finetuned", "hycell-finetuned", \
                "Fine-tuned on the labelled cells of the other batches"
        elif label == "pseudobulk counts":
            cfg, cslug, condition = f"{B}-config-pseudobulk-counts", "pseudobulk-counts", \
                "Counted programs from pseudobulk raw counts; no embedding"
        else:
            cslug = SYSTEMS[label][0]
            cfg, condition = f"{B}-config-{cslug}", adapt(label)
        dslug = data.replace(f"{B}-data-", "")
        eval_id = f"{B}-eval-{slug}-{cslug}-{dslug}"
        if eval_id not in self.evals:
            self.evals.add(eval_id)
            comp = {"protocol_id": f"{B}-protocol-{slug}",
                    "dataset_version": "As assembled for the HyCell report (2026-11-01)",
                    "split": "Whole atlas; batches held out in turn for annotation transfer",
                    "population": "As printed in Table 2 for this dataset",
                    "inputs": "Raw integer counts with all measured human genes",
                    "adaptation": condition,
                    "metric_implementation": PROTO[slug]["metric_implementation"],
                    "aggregation": PROTO[slug]["aggregation"],
                    "budget": "Released weights at default inference settings"}
            self.records.append(record(
                eval_id, "evaluation", f"{label} on {slug}, {dslug} (HyCell report)",
                "Author-reported evaluation transcribed from the pinned report; run by the developer "
                "of HyCell and not reproduced by Rewire.",
                {"origin": "author_reported", "protocol": f"{B}-protocol-{slug}",
                 "version": "HyCell technical report, 2026-11-01, retrieved at commit 0dcc533c",
                 "comparison": comp, "source_locator": locator},
                links=[{"relation": "system", "target_id": cfg},
                       {"relation": "assessment", "target_id": f"{B}-protocol-{slug}"},
                       {"relation": "data", "target_id": data}],
                facets={"areas": AREAS, "contexts": ["research"]}))
        p = PROTO[slug]
        attrs = {"metric": p["metric"], "metric_direction": p["metric_direction"], "unit": p["unit"],
                 "metric_qualifier": p["metric_qualifier"], "printed_value": printed,
                 "numeric_value": printed, "source_locator": locator, "review": dict(REVIEW),
                 "missing_metadata": {"uncertainty": {
                     "reason": "unreported", "note": "No uncertainty is printed anywhere in the report."}}}
        if scope:
            attrs["claim_scope"] = scope
        if limits:
            attrs["limitations"] = limits
        self.records.append(record(
            f"{B}-result-{slug}-{cslug}-{dslug}", "result", f"{label}: {slug} on {dslug} (HyCell report)",
            "Value transcribed exactly as printed in the pinned report. Author-reported; not "
            "reproduced by Rewire.", attrs, links=[{"relation": "evaluation", "target_id": eval_id}],
            facets={}))


def build(parsed):
    PAGES.clear()
    PAGES.update(parsed["pages"])
    o = Out()
    cols = {"S": "composite-score", "Bio": "bio-conservation", "Batch": "batch-correction",
            "LR": "annotation-transfer-lr", "kNN": "annotation-transfer-knn"}
    for model, row in parsed["table3"].items():
        for col, slug in cols.items():
            scope = TIE if col == "S" and model in ("HyCell", "Stack") else None
            o.add(slug, model, SUITE, row[col],
                  f"Table 3, row {row_label(model)}, column '{col}' ({page('table3')})", scope)
    for model, row in parsed["table4"].items():
        for atlas, value in row.items():
            o.add("composite-score", model, DATA[atlas], value,
                  f"Table 4, row {row_label(model)}, column '{atlas}' ({page('table4')})",
                  limits=["Table 4 prints S per atlas without its four components, so this "
                          "composite cannot be decomposed from the report."])
    for (atlas, model), value in parsed["figure1b"].items():
        if atlas == "Mean":
            continue
        o.add("bio-conservation", model, DATA[atlas], value,
              f"Figure 1b, row '{atlas}', column '{model}', printed value ({page('figure1')})")
    for atlas, row in parsed["table5"].items():
        loc = f"Table 5, row '{atlas}', column '{{}}' ({page('table5')})"
        o.add("annotation-finetuned", "Fine-tuned", DATA[atlas], row["Fine-tuned"],
              loc.format("Fine-tuned"))
        o.add("annotation-transfer-lr", "HyCell", DATA[atlas], row["Frozen + LR"],
              loc.format("Frozen + LR"))
        o.add("annotation-transfer-knn", "HyCell", DATA[atlas], row["Frozen + kNN"],
              loc.format("Frozen + kNN"))
    return o
