"""MochiBind antibody-antigen affinity evaluation (iScience 2026, 116522): Table 2.

Usage: python3 -I extract_mochibind.py <fulltext.xml> <batch-folder>
"""
import sys, os, json
import xml.etree.ElementTree as ET
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import Batch, extraction_review, reviewed_review, source_review, mark_reviewed, sha256, slug, num

xml_path, folder = sys.argv[1], sys.argv[2]
SHA = sha256(xml_path)
URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13444443/fullTextXML"
assert SHA == "0f57b9b13bae7460d3789fdcd7f3aaa062ec8cfe8e8d1ef9242d480ea444368d", SHA

P = "lit-interactions-20261011-mochibind"
b = Batch(folder, P, areas=["molecular-interactions", "proteins-complexes"])
SRC = b.source(P + "-source-isci2026", "A systematic evaluation framework for universal antibody-antigen binding affinity prediction and candidate recommendation", {
    "url": "https://doi.org/10.1016/j.isci.2026.116522", "artifact_url": URL,
    "version": "iScience 2026, 116522; PMC13444443 full-text XML",
    "retrieved_at": "2026-10-11T21:26:34Z", "artifact_sha256": SHA, "doi": "10.1016/j.isci.2026.116522",
    "publication_status": "peer_reviewed", "licence": "CC-BY-NC-ND-4.0", "media_type": "application/xml",
    "limitations": [
        "Retrieval results (Precision@K and retrieval accuracy) are in figures only and were not read.",
        "Supplementary Tables S1 (McNemar statistics) and S2 (Graphinity before and after fine-tuning) were not retrieved.",
        "Licence CC BY-NC-ND: the XML is not archived in the repository.",
    ]})
SIDS = [SRC]
REVIEW = lambda loc: extraction_review(["deterministic-table-parse"],
    "Parsed the <td> cells of the pinned PMC XML with extract/extract_mochibind.py; header row asserted. " + loc, SHA, URL)

root = ET.fromstring(open(xml_path, "rb").read())
tables = {}
for tw in root.iter("table-wrap"):
    lab = tw.find("label")
    if lab is None:
        continue
    rows = [[" ".join("".join(c.itertext()).split()) for c in tr if c.tag in ("td", "th")] for tr in tw.iter("tr")]
    tables[" ".join("".join(lab.itertext()).split())] = rows
t2 = tables["Table 2"]
assert t2[0] == ["Antigen", "Graphinity (%)", "Boltz-2 - iplddt (%)", "GeoDock (%)", "MochiBind (%)"], t2[0]

SYSTEMS = {
    "Graphinity (%)": ("Graphinity", "model", "Graphinity: equivariant graph neural network predicting binding free-energy change from antibody-antigen structures.",
                       ["supervised_machine_learning"], "Fine-tuned Graphinity model (Table 2 note: 'The Graphinity model result is reported using the fine-tuned model')", "independent_paper"),
    "Boltz-2 - iplddt (%)": ("Boltz-2", None, None, ["foundation_model"], "Boltz-2 interface pLDDT (ipLDDT) used as the binding score for each antibody-antigen complex", "independent_paper"),
    "GeoDock (%)": ("GeoDock", "model", "GeoDock: geometric deep-learning protein docking framework.", ["supervised_machine_learning"],
                    "GeoDock interface-stability score derived from ipLDDT features", "independent_paper"),
    "MochiBind (%)": ("MochiBind", "model", "MochiBind: sequence-only pairwise antibody-antigen binding predictor using ESM-2 (esm2_t36_3B_UR50D) embeddings and a pairwise scoring module (this paper).",
                      ["foundation_model"], "Trained on two antigens, validated on a third and tested on the held-out antigen (rotation); ESM-2 esm2_t36_3B_UR50D encoder (Key resources table)", "author_reported"),
}
fam = {}
for col, (name, kind, desc, mt, params, origin) in SYSTEMS.items():
    if name == "Boltz-2":
        fam[col] = "catalog-model-boltz-2"
    else:
        fam[col] = b.entity(kind, b.rid(kind, name), name, desc, SIDS, {"reported_name": name, "entity_level": "family",
                            "source_locator": "Introduction; Results; Table 2 header",
                            "missing_metadata": {"version": {"reason": "unreported", "note": "No version printed"}}}, method_types=mt)
configs = {}
for col, (name, kind, desc, mt, params, origin) in SYSTEMS.items():
    links = [{"relation": "configuration_of", "target_id": fam[col]}]
    if name == "MochiBind":
        links.append({"relation": "uses_model", "target_id": "discovery-model-esm-2"})
    configs[col] = b.entity("configuration", b.rid("config", name, "alphabind-pairwise"), f"{name} (AlphaBind pairwise evaluation)",
        f"{name} as evaluated on AlphaBind pairwise accuracy in the MochiBind study.", SIDS,
        {"reported_name": col.replace(" (%)", ""), "foundation_model_eligible": mt == ["foundation_model"], "parameters": params,
         "source_locator": "Table 2 header and note; STAR Methods", "access_reuse": "Not stated in the source",
         "missing_metadata": {"version": {"reason": "unreported", "note": "No checkpoint version printed"}}},
        method_types=mt, links=links)

BENCH = b.entity("benchmark", b.rid("benchmark", "alphabind-universal-affinity"), "Universal antibody-antigen affinity evaluation on AlphaBind (MochiBind study)",
    "Evaluation framework for antibody-antigen binding affinity on four AlphaBind antigen systems with each antigen held out in turn; pairwise accuracy and retrieval metrics.",
    SIDS, {"entity_level": "suite", "version": "iScience 2026, 116522", "task": "Antibody-antigen relative binding affinity prediction",
           "scope_note": "Pairwise accuracy (Table 2) only; retrieval metrics are in figures.", "source_locator": "Introduction; Figure 1; STAR Methods; Table 2"})
ANTIGENS = ["PEM", "PP489", "TRA", "VHH72"]
datas, protos = {}, {}
for ag in ANTIGENS:
    datas[ag] = b.entity("dataset", b.rid("data", "alphabind", ag), f"AlphaBind {ag} antibody variants (held-out antigen)",
        f"AlphaBind antibody variants against antigen {ag}, sampled to preserve the affinity distribution, used as the held-out test antigen in the rotation.", SIDS,
        {"version": "AlphaBind dataset as sampled in the MochiBind study", "split": "Held-out antigen (rotation: two antigens train, one validation, one test)",
         "population": "10,000 sampled variants" if ag != "TRA" else "5,000 sampled variants",
         "source_locator": "STAR Methods, data sampling and rotation setup"})
    protos[ag] = b.entity("protocol", b.rid("protocol", "alphabind", ag, "pairwise-accuracy"), f"AlphaBind {ag} held-out antigen, pairwise accuracy",
        f"Pairwise accuracy on antibody pairs against the held-out antigen {ag}: the fraction of sampled pairs in which the stronger binder is identified.", SIDS,
        {"protocol": f"AlphaBind {ag} held out; pairwise accuracy (%)", "version": "iScience 2026, 116522", "metric": "accuracy",
         "metric_direction": "higher", "unit": "percent", "metric_qualifier": "pairwise: stronger binder identified within sampled antibody pairs",
         "limitations": ["The authors developed MochiBind and ran all baselines.",
                         "Boltz-2 and GeoDock are scored through interface confidence (ipLDDT) used as an affinity proxy, not an affinity head.",
                         "The p-values printed beside MochiBind are one-sided McNemar tests against the baselines; no uncertainty is printed for the accuracies."],
         "source_locator": f"Table 2, row '{ag}'"},
        links=[{"relation": "part_of", "target_id": BENCH}, {"relation": "uses_data", "target_id": datas[ag]}])

seen = []
for i, row in enumerate(t2[1:], 2):
    ag = row[0]
    seen.append(ag)
    for col, cell in zip(t2[0][1:], row[1:]):
        name, _, _, mt, _, origin = SYSTEMS[col]
        value = cell.split(" (")[0]
        assert value.endswith("%") and num(value) is not None, (ag, col, cell)
        e = b.evaluation(b.rid("eval", name, ag), f"{name} on AlphaBind {ag} (pairwise accuracy)", SIDS, configs[col], protos[ag], datas[ag], origin,
                         {"protocol_id": protos[ag], "dataset_version": "AlphaBind (sampled)", "split": "Held-out antigen", "population": None,
                          "inputs": "Antibody and antigen sequences" if name == "MochiBind" else "Antibody-antigen complex predicted or docked by the method",
                          "adaptation": "Trained on two other antigens" if name in ("MochiBind",) else ("Fine-tuned" if name == "Graphinity" else "Zero-shot confidence score"),
                          "metric_implementation": "Pairwise accuracy (%) as printed", "aggregation": None, "budget": None},
                         f"Table 2 row '{ag}', column '{col}'; STAR Methods, 'Cross-antigen evaluation setup'")
        extra = {"reported_p_value": cell.split(" (", 1)[1].rstrip(")")} if " (" in cell else None
        b.result(b.rid("result", name, ag), f"{name} AlphaBind {ag} pairwise accuracy", SRC, SIDS, e, cell if extra else value, "accuracy", "higher", "percent",
                 f"Table 2, row '{ag}', column '{col}'; STAR Methods, 'Cross-antigen evaluation setup'",
                 REVIEW(f"Table 2 body row {i - 1}."),
                 qualifier="pairwise: stronger binder identified within sampled antibody pairs", numeric=num(value), extra=extra)
assert seen == ANTIGENS, seen
# ---------------------------------------------------------------------------
# Corrections from the independent review (reviewer-mi-1, 2026-10-11), applied
# verbatim. Labels M1 to M4 are the reviewer's.
# ---------------------------------------------------------------------------
REVIEWER_NOTE = ("Claude review agent reviewer-mi-1, independent of the extractor "
                 "lit-microbial-interactions; no human review claimed")
by_id = {r["id"]: r for r in b.records}

# M1 and M2: the source states the test-set denominator and the metric's aggregation follows from it.
POP = "200,000 sampled antibody pairs from the held-out antigen, no affinity-difference threshold applied"
AGG = "Fraction of the 200,000 sampled test pairs in which the stronger binder was identified"
n = 0
for r in b.records:
    if r["kind"] != "evaluation":
        continue
    a = r["attributes"]
    a["comparison"]["population"] = POP
    a["comparison"]["aggregation"] = AGG
    for key in ("comparison.population", "comparison.aggregation"):
        a.get("missing_metadata", {}).pop(key, None)
    if not a.get("missing_metadata"):
        a.pop("missing_metadata", None)
    n += 1
assert n == 16, n

# M3: the Table 2 footnote contradicts the headers, the cells and the body text.
by_id[SRC]["attributes"]["evidence_concerns"] = [{
    "source_id": SRC,
    "message": ('The Table 2 footnote says "Values denote chi-squared statistics, with significance levels in '
                'parentheses", which contradicts the column headers ("Pairwise accuracy (%)", "Graphinity (%)" '
                "and so on), the cell contents (percentages between 47.11 and 74.27) and the body text, which "
                "places the chi-squared statistics in Table S1. The records read the cells as accuracies with a "
                "p-value, which the headers and body support; the footnote is wrong as printed."),
    "source_locator": "Table 2 footnote",
    "artifact_sha256": SHA, "reviewed_at": "2026-10-11T00:00:00Z", "review_method": "ai-assisted-source-review"}]

# M4: the four columns are not matched on adaptation.
M4 = ("The four columns are not matched on adaptation: the Graphinity column is the authors' own fine-tune of a "
      "third-party model, trained on the same rotation, while Boltz-2 and GeoDock are used without any fitting.")
for ag in ANTIGENS:
    lims = by_id[protos[ag]]["attributes"]["limitations"]
    assert not any(l.startswith("The four columns are not matched") for l in lims)
    lims.append(M4)

R_METHODS = ["source-hash-verification", "deterministic-table-parse", "independent-cell-check"]
R_NOTE = ("Re-downloaded the Europe PMC full-text XML and matched its byte count and SHA-256. Parsed every "
          "table-wrap of the pinned XML with an independent parser: all 16 Table 2 cells are extracted and the "
          "printed string, the numeric accuracy and, for MochiBind, the p-value all match. Table 1 is a feature "
          "matrix of prior studies and the key resources table holds no performance values, so neither is "
          "extracted; no other table in the XML carries results. All 16 cells, the header row, the footnote and "
          "the p-value strings were also read directly from the table markup, which is the whole batch rather "
          "than a sample.")
for r in b.records:
    if r["kind"] == "result":
        old = r["attributes"]["review"]
        r["attributes"]["review"] = reviewed_review(R_METHODS, R_NOTE, REVIEWER_NOTE, SHA, URL,
                                                    old["method_note"], R_NOTE)
by_id[SRC]["attributes"]["review"] = source_review(
    REVIEWER_NOTE, "Full-text XML re-downloaded from the recorded Europe PMC URL and its SHA-256 matched.")
mark_reviewed(b)

counts = b.write()
print(json.dumps(counts))
