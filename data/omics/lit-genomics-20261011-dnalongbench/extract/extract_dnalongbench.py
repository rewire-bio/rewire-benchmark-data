"""DNALONGBENCH (Cheng et al., Nature Communications 2025): Tables 3-7 from the PMC XML.

Usage: python3 -I extract_dnalongbench.py <fulltext.xml> <batch-folder>
"""
import sys, os, json
import xml.etree.ElementTree as ET
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import Batch, extraction_review, sha256, num

xml_path, folder = sys.argv[1], sys.argv[2]
SHA = sha256(xml_path)
assert SHA == "0d7db21f2a843dda3ba703c53cd0abad12c9c795cfbcf4fd1bdc6c4a863fe41b", SHA
URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12627797/fullTextXML"

b = Batch(folder, "lit-genomics-20261011-dnalongbench")
SRC = b.source("lit-genomics-20261011-dnalongbench-source-cheng2025", "DNALONGBENCH: a benchmark suite for long-range DNA prediction tasks", {
    "url": "https://doi.org/10.1038/s41467-025-65077-4", "artifact_url": URL,
    "version": "Nature Communications 16, published 2025-11-18; PMC12627797 full-text XML",
    "retrieved_at": "2026-10-11T01:34:19Z", "artifact_sha256": SHA, "doi": "10.1038/s41467-025-65077-4",
    "publication_status": "peer_reviewed", "licence": "CC-BY-NC-ND-4.0", "media_type": "application/xml",
    "limitations": ["Journal version of the bioRxiv preprint already in the store as dnalongbench-2025 (2 results from Table 3). The two overlapping cells (HyenaDNA and Caduceus-Ph ETGP AUROC) agree with this version.",
                    "Supplementary Information (Table S1 and per-task details) was not read."]})
SIDS = [SRC]
REV = lambda loc: extraction_review(["deterministic-table-parse"], "Parsed the <td> cells of the pinned PMC XML table with tools/extract_dnalongbench.py; header rows and model labels asserted. " + loc, SHA, URL)

root = ET.fromstring(open(xml_path, "rb").read())
tables = {}
for tw in root.iter("table-wrap"):
    lab = " ".join("".join(tw.find("label").itertext()).split())
    tables[lab] = [[" ".join("".join(c.itertext()).split()) for c in tr if c.tag in ("td", "th")] for tr in tw.iter("tr")]

BENCH = b.entity("benchmark", b.rid("benchmark", "dnalongbench"), "DNALONGBENCH",
    "Five long-range DNA prediction tasks with inputs up to about 1 Mb: enhancer-target gene, eQTL, 3D contact map, regulatory sequence activity and transcription initiation signal prediction.",
    SIDS, {"entity_level": "suite", "version": "Nature Communications 2025", "task": "Long-range DNA sequence prediction",
           "scope_note": "Each task compares a task-specific expert model, a CNN, and fine-tuned HyenaDNA (medium-450k), Caduceus-Ph and Caduceus-PS.",
           "source_locator": "Abstract; Table 2; Tables 3-7"})

EXPERT = {"ETGP": ("ABC", "ucc-research-method-mprabc-abc", "Activity-by-Contact model using DNase-seq, H3K27ac ChIP-seq and Hi-C inputs, not sequence only"),
          "eQTLP": ("Enformer", "regulatory-variant-20261009-model-enformer", "Enformer"),
          "RSAP": ("Enformer", "regulatory-variant-20261009-model-enformer", "Enformer"),
          "CMP": ("Akita", None, "Akita contact-map model"),
          "TISP": ("Puffin-D", None, "Puffin-D transcription initiation model")}
FAM = {"HyenaDNA": "regulatory-variant-20261009-model-hyenadna", "Caduceus-Ph": "regulatory-variant-20261009-model-caduceus", "Caduceus-PS": "regulatory-variant-20261009-model-caduceus"}
newfam = {}
def family(name, desc, mt):
    if name not in newfam:
        newfam[name] = b.entity("model", b.rid("model", name), name, desc, SIDS,
                                {"reported_name": name, "entity_level": "family", "source_locator": "Methods 'Expert model' and 'CNN' descriptions",
                                 "missing_metadata": {"version": {"reason": "inapplicable", "note": "Family record; versions are on configurations"}}}, method_types=mt)
    return newfam[name]

cfgs = {}
def config(row, task):
    if row == "Expert Model":
        name, fam, note = EXPERT[task]
        fam = fam or family(name, note + ".", ["supervised_machine_learning"])
        key, label, mt, params = (name, task if name == "Enformer" else ""), name, ["supervised_machine_learning"], f"Expert model for {task}: {note}"
    elif row == "CNN":
        fam = family("DNALONGBENCH CNN baseline", "Convolutional neural network baseline trained per task by the DNALONGBENCH authors.", ["supervised_machine_learning"])
        key, label, mt, params = ("CNN", task), "CNN", ["supervised_machine_learning"], f"CNN trained for {task}"
    else:
        fam, key, label, mt = FAM[row], (row, ""), row, ["foundation_model"]
        params = ("HyenaDNA medium-450k; fine-tuned per task" if row == "HyenaDNA" else f"Caduceus {row.split('-')[1]}; fine-tuned per task")
    if key not in cfgs:
        cfgs[key] = b.entity("configuration", b.rid("config", *key), f"{label} (DNALONGBENCH{', ' + key[1] if key[1] else ''})", f"{label} as evaluated in DNALONGBENCH.", SIDS,
                             {"reported_name": row if row != "Expert Model" else f"Expert Model ({label})", "foundation_model_eligible": row in FAM,
                              "parameters": params, "access_reuse": "Public model code and weights" if row in FAM else "Not stated in the main text",
                              "source_locator": "Methods 'Expert model', 'CNN' and 'DNA Foundation Model'",
                              "missing_metadata": {"version": {"reason": "unreported", "note": "Checkpoint or release not printed beyond the model name"}}},
                             method_types=mt, links=[{"relation": "configuration_of", "target_id": fam}])
    return cfgs[key]

SPEC = [  # table, task code, task name, header row index, metric per column fn, unit, data note
    ("Table 3", "ETGP", "Enhancer-target gene prediction", {"AUROC": "auroc", "AUPRC": "auprc"}),
    ("Table 4", "CMP", "Contact map prediction", "scc"),
    ("Table 5", "RSAP", "Regulatory sequence activity prediction", "pearson-correlation"),
    ("Table 6", "TISP", "Transcription initiation signal prediction", "pearson-correlation"),
    ("Table 7", "eQTLP", "Expression quantitative trait loci prediction", "auroc"),
]
ABBR = {"FC": "FANTOM CAGE", "EC": "ENCODE CAGE", "ER": "ENCODE RAMPAGE", "GC": "GRO-cap", "PC": "PRO-cap",
        "CCF": "Cells_Cultured_fibroblasts", "WB": "Whole_Blood", "SNSES": "Skin_Not_Sun_Exposed_Suprapubic", "SSELL": "Skin_Sun_Exposed_Lower_leg",
        "MS": "Muscle Skeletal", "NT": "Nerve Tibial", "AT": "Artery_Tibial", "AS": "Adipose_Subcutaneous"}
# Results already in the store from the bioRxiv preprint (source dnalongbench-2025) for the same cells.
SUPERSEDES = {("HyenaDNA", "ETGP", "AUROC"): "lit-007", ("Caduceus-Ph", "ETGP", "AUROC"): "lit-008"}
for table, code, tname, metric in SPEC:
    rows = tables[table]
    cols = rows[1][1:]
    body = rows[2:]
    assert [r[0] for r in body] == ["Expert Model", "CNN", "HyenaDNA", "Caduceus-Ph", "Caduceus-PS"], body
    data = b.entity("dataset", b.rid("data", code), f"DNALONGBENCH {tname} test set", f"Held-out test data for the DNALONGBENCH {tname} task.", SIDS,
                    {"split": "Held-out test set as defined by DNALONGBENCH", "source_locator": f"Methods 'Benchmark dataset' for {tname}; Table 2",
                     "missing_metadata": {"version": {"reason": "unreported"}}})
    m0 = metric if isinstance(metric, str) else "auroc"
    proto = b.entity("protocol", b.rid("protocol", code), f"DNALONGBENCH {tname} ({table})", f"DNALONGBENCH {code}: {tname}.", SIDS,
                     {"protocol": f"{tname}; models trained or fine-tuned on the task training split and scored on the held-out test set; columns as printed in {table}.",
                      "version": "Nature Communications 2025", "metric": "stratum-adjusted-correlation-coefficient" if m0 == "scc" else m0, "metric_direction": "higher", "unit": "unitless",
                      "limitations": ["Single run per cell; no uncertainty printed.", "Expert models differ by task and may use non-sequence inputs (ABC uses DNase-seq, H3K27ac and Hi-C)."]
                                     + (["For eQTL prediction the foundation models feed last-layer representations to a classification head; Methods do not say whether the backbone was frozen, so 'Fine-tuned' may overstate the adaptation."] if code == "eQTLP" else []),
                      "source_locator": f"{table}; Methods"},
                     links=[{"relation": "part_of", "target_id": BENCH}, {"relation": "uses_data", "target_id": data}])
    for r in body:
        c = config(r[0], code)
        ev = b.evaluation(b.rid("eval", r[0], code), f"{r[0]} on DNALONGBENCH {code}", SIDS, c, proto, data,
                          "author_reported" if r[0] == "CNN" else "independent_paper",
                          {"protocol_id": proto, "dataset_version": None, "split": "Held-out test set", "population": None, "inputs": "DNA sequence" + (" plus DNase-seq, H3K27ac and Hi-C" if r[0] == "Expert Model" and code == "ETGP" else ""),
                           "adaptation": "Fine-tuned" if r[0] in FAM else "Trained for the task", "metric_implementation": None, "aggregation": None, "budget": None},
                          f"{table} row '{r[0]}'")
        for col, v in zip(cols, r[1:]):
            met = metric[col] if isinstance(metric, dict) else metric
            q = None if isinstance(metric, dict) else (f"average over {code} conditions as printed" if col == "Avg" else (f"{col} ({ABBR[col]})" if col in ABBR and code in ("TISP", "eQTLP") else f"{col}"))
            key = "stratum-adjusted-correlation-coefficient" if met == "scc" else met
            loc = f"{table}, row '{r[0]}', column '{col}'"
            assert num(v) is not None, v
            rid = b.result(b.rid("result", r[0], code, col), f"{r[0]} {code} {col}", SRC, SIDS, ev, v, key, "higher", "unitless", loc, REV(loc), qualifier=q)
            old = SUPERSEDES.get((r[0], code, col))
            if old:
                b.records[-1]["links"].append({"relation": "supersedes", "target_id": old})
                evrec = next(x for x in b.records if x["id"] == ev)
                evrec["links"].append({"relation": "supersedes", "target_id": "evaluation-" + old})
print(json.dumps(b.write()))
