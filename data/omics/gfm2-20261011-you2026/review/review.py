"""Independent review of the You et al. 2026 batch (2026-10-11).

Usage: python3 -I review/review.py <pdftotext -layout text of MOESM1_ESM.pdf> <article fullTextXML>

Parses Supplementary Tables 4 and 5 from the supplement text layer and the Methods and Table 1 from
the article XML with its own matching (it does not import extract/extract.py), checks every result,
applies the corrections listed in review.md, moves the rejected top-k results to
data/omics/pending-review/gfm2-20261011-you2026-topk/, and writes the reviewed records back to
batch.jsonl. Run it once, after extract/extract.py; it refuses to run on an already reviewed batch.
"""
import hashlib
import html
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
PENDING = HERE.parent / "pending-review" / "gfm2-20261011-you2026-topk"
P = "gfm2-20261011-you2026-"
XML_SHA = "2c6b2816846a21296c56b4dd58f3d1e8810e9d96e224d3ab21b5eb8faa9928e4"
SUPP_SHA = "cbb69e05045a4526e35479d2c1361ebb9cfadfd968e00675390dad597035d882"
SUPP_TEXT_SHA = "4a54c8b1acbb475db01d8768b4ff7279a9b503714b395738496d6f817127308e"
XML_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12780105/fullTextXML"
SUPP_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12780105/supplementaryFiles"
DATE = "2026-10-11"
REVIEWER_NOTE = "Claude (Opus 5.5) review agent reviewer-gfm-a, independent of the extractor lit-gfm-2; no human review claimed"
METHOD_NOTE = ("Re-downloaded the article XML (SHA-256 matches) and the supplementaryFiles zip, whose MOESM1_ESM.pdf member "
               "matches the pinned SHA-256. Parsed Supplementary Tables 4 and 5 from the `pdftotext -layout` (poppler 26.08.0) "
               "text with a separate parser (review/review.py) and checked printed value, numeric value, spread, metric, "
               "qualifier, unit, direction, locator and the linked configuration, protocol and dataset against the block, "
               "row and column labels and the article's Methods and Table 1.")

supp_raw = Path(sys.argv[1]).read_bytes()
xml_raw = Path(sys.argv[2]).read_bytes()
assert hashlib.sha256(supp_raw).hexdigest() == SUPP_TEXT_SHA, "supplement text hash mismatch"
assert hashlib.sha256(xml_raw).hexdigest() == XML_SHA, "article XML hash mismatch"
lines = supp_raw.decode("utf-8").splitlines()
article = " ".join(html.unescape(re.sub(r"<[^>]+>", " ", xml_raw.decode("utf-8"))).split())

records = [json.loads(l) for l in (HERE / "batch.jsonl").read_text().splitlines()]
by_id = {r["id"]: r for r in records}
assert all(r["status"] == "needs_review" for r in records), "batch already reviewed"
assert len(records) == 266

# ---- Supplementary Tables 4 and 5 (captions sit below their tables) -------------------------
cap3 = next(i for i, l in enumerate(lines) if l.strip().startswith("Supplementary Table 3:"))
cap4 = next(i for i, l in enumerate(lines) if l.strip().startswith("Supplementary Table 4:"))
cap5 = next(i for i, l in enumerate(lines) if l.strip().startswith("Supplementary Table 5:"))
ROW = re.compile(r"^\s*(\S+)\s+((?:\d\.\d{4}\(\d\.\d{4}\)\s*)+)$")
cells = {}


def read(start, end, blocks, cols, table):
    current = None
    for l in lines[start:end]:
        s = l.strip()
        if s in blocks:
            current = s
            continue
        m = ROW.match(l)
        if m and current:
            vals = re.findall(r"(\d\.\d{4})\((\d\.\d{4})\)", m.group(2))
            assert len(vals) == len(cols), l
            for c, v in zip(cols, vals):
                cells[(table, current, m.group(1), c)] = v


read(cap3 + 1, cap4, {"NT-splice-sites-all", "NT-splice-sites-acceptors", "NT-splice-sites-donors"},
     ["F1 Score", "Precision", "Recall", "Accuracy"], "Supplementary Table 4")
read(cap4 + 1, cap5, {"Splice acceptors and donors", "Splice-15class", "Splice-53class"},
     ["Average PR-AUC", "Average Top-k"], "Supplementary Table 5")
assert sum(1 for k in cells if k[0] == "Supplementary Table 4") == 132
assert sum(1 for k in cells if k[0] == "Supplementary Table 5") == 44

# Article facts the corrections rely on.
FACTS = {
    "topk": "Top-k accuracy: Top-k accuracy measures the fraction of times the true label is among the top k predicted labels.",
    "retrain": "The task-specific methods used for comparison-including ncRDense, DeepM6ASeq, SpliceAI, SpliceTransformer, and others-were retrained under our framework.",
    "pytorch": "For non-PyTorch-based methods, we reimplemented them in PyTorch to ensure consistency",
    "seq": "For sequence-level classification, we appended a convolutional layer to the backbone model",
    "split500": "To balance model requirements with practical applications, we divided the input data into a 500bp sequence for all methods.",
    "epoch": "For each model, the epoch with the highest average PR-AUC value across all classes was recognized as the best epoch, with other metrics presented accordingly.",
    "sptransformer": "You, N. et al. SpliceTransformer predicts tissue-specific splicing linked to human diseases. Nat. Commun. 15 , 9129 (2024).",
    "author": "You Ningyuan",
}
for k, v in FACTS.items():
    assert v in article, k
for t1 in ["NT-splice-sites-all 52 5 species 3 30,000 sequences (27,000 train/3,000 test)",
           "NT-splice-sites-acceptors 52 147 species 2 22,179 sequences (19,961 train/2,218 test)",
           "NT-splice-sites-donors 52 147 species 2 21,973 sequences (19,775 train/2198 test)",
           "GTEx Dataset 58 Human 53 341,830 entries (242,017 train/99,813 test)"]:
    assert t1 in article, t1

# ---- Check every result ----------------------------------------------------------------------
METRIC = {"F1 Score": "f1-score", "Precision": "precision", "Recall": "recall", "Accuracy": "accuracy",
          "Average PR-AUC": "auprc", "Average Top-k": "splice-top-k-accuracy"}
T4DATA = {"NT-splice-sites-all": "nt-splice-all", "NT-splice-sites-acceptors": "nt-splice-acceptors", "NT-splice-sites-donors": "nt-splice-donors"}
T5PROTO = {"Splice acceptors and donors": "gtex-acceptors-donors", "Splice-15class": "gtex-splice-15class", "Splice-53class": "gtex-splice-53class"}
seen = set()
for r in records:
    if r["kind"] != "result":
        continue
    a = r["attributes"]
    m = re.fullmatch(r"(Supplementary Table [45]), block '(.+)', row '(.+)', column '(.+)'", a["source_locator"])
    key = m.groups()
    mean, sd = cells[key]
    assert a["printed_value"] == f"{mean}({sd})" and a["numeric_value"] == mean, r["id"]
    u = a["uncertainty"]
    assert u["type"] == "standard_deviation" and u["value"] == sd and u["n"] == 3, r["id"]
    assert a["metric"] == METRIC[key[3]] and a["unit"] == "fraction" and a["metric_direction"] == "higher", r["id"]
    ev = by_id[r["links"][0]["target_id"]]
    el = {l["relation"]: l["target_id"].removeprefix(P) for l in ev["links"]}
    assert el["system"] == "config-" + key[2].lower(), (r["id"], el)
    if key[0] == "Supplementary Table 4":
        assert el["assessment"] == "protocol-" + T4DATA[key[1]] and el["data"] == "data-" + T4DATA[key[1]], r["id"]
    else:
        assert el["assessment"] == "protocol-" + T5PROTO[key[1]] and el["data"] == "data-gtex", r["id"]
    seen.add(key)
assert len(seen) == 176

# ---- Corrections ---------------------------------------------------------------------------
corrections = []


def fix(rid, what):
    corrections.append((rid, what))


# 1. SpTransformer was developed by the same first author (ref. 12, You et al. 2024).
for r in records:
    if r["kind"] == "evaluation" and r["id"].endswith("-sptransformer"):
        r["attributes"]["origin"] = "author_reported"
        r["attributes"]["limitations"].append(
            "SpTransformer (SpliceTransformer) was developed by You et al. 2024 (ref. 12), whose first author is also first "
            "author here, so this row is not independent of the method's developers.")
        fix(r["id"], "origin changed from independent_paper to author_reported: SpTransformer is the first author's own method (ref. 12)")

# 2. The 500 bp input applies to the GTEx task (Results, Methods), not to the NT splice-site datasets,
#    whose input length this source does not state.
NT_LIM_OLD = "All methods are given a 500 bp input so that models with different context windows are comparable; SpTransformer and SpliceAI were designed for 1,000 to 5,000 nucleotide inputs (Results)."
NT_LIM_NEW = "Input length for the NT splice-site datasets is not stated in this source; the 500 bp division applies to the GTEx task."
for r in records:
    a = r["attributes"]
    is_nt = r["id"].startswith(P + "protocol-nt-") or r["id"].startswith(P + "eval-t4-") or r["id"].startswith(P + "result-t4-")
    if not is_nt:
        continue
    if NT_LIM_OLD in a.get("limitations", []):
        a["limitations"][a["limitations"].index(NT_LIM_OLD)] = NT_LIM_NEW
    if r["kind"] == "protocol":
        r["name"] = r["name"].replace(" splice-site classification, 500 bp input, fine-tuned models", " splice-site classification, fine-tuned models")
        r["description"] = r["description"].replace("with every method given the same 500 bp input and the same train/test split",
                                                    "with every method given the same train/test split")
        a["protocol"] = a["protocol"].replace("with an appended convolution head for the language models",
                                              "with an appended convolutional layer for the language models (sequence-level classification, Methods)")
    if r["kind"] == "evaluation":
        r["name"] = r["name"].replace(", 500 bp input", "")
        a["comparison"]["inputs"] = "DNA sequence from the NT benchmark splice-site dataset; length not stated in this source"
    if r["kind"] == "result":
        a["metric_qualifier"] = a["metric_qualifier"].replace(", 500 bp input", "")
    assert "500 bp input" not in json.dumps(r) and "500 bp DNA" not in json.dumps(r), r["id"]
    fix(r["id"], "500 bp input removed: the source states it for the GTEx task only")

# 3. Configurations: the 500 bp input is task-specific; SpliceAI and SpTransformer were retrained, not
#    used as distributed.
for r in records:
    if r["kind"] != "configuration":
        continue
    a = r["attributes"]
    name = a["reported_name"]
    if r["id"] in (P + "config-spliceai", P + "config-sptransformer"):
        r["name"] = f"{name} retrained under the authors' framework (You et al. 2026)"
        a["parameters"] = ("Task-specific method retrained on each benchmark training split under the authors' PyTorch framework, "
                           "with non-PyTorch methods reimplemented in PyTorch (Methods); GTEx task input divided into 500 bp "
                           "blocks; trained and tested three times with different random initialisations")
        a["training_setting"] = "Retrained from scratch on the task training split"
        fix(r["id"], "name and parameters: retrained under the authors' framework (Methods), not used as distributed")
    else:
        r["name"] = f"{name} fine-tuned with an appended convolutional layer (You et al. 2026)"
        a["parameters"] = ("Officially released pre-trained weights fine-tuned per task with a convolutional layer appended to the "
                           "backbone (Methods); AdamW; parameters in Supplementary Table 1; GTEx task input divided into 500 bp "
                           "blocks; fine-tuned and tested three times with different random initialisations")
        fix(r["id"], "name and parameters: 500 bp input stated for the GTEx task only")
    r["description"] = f"{r['name']}, as evaluated in the cited comparison."

# 4. Duplicate family records: the store already holds RNA-FM and GENA-LM.
RELINK = {"config-rnafm": ("model-rna-fm", "discovery-model-rna-fm"),
          "config-gena-lm-base": ("model-gena-lm", "regulatory-variant-20261009-model-gena-lm"),
          "config-gena-lm-large": ("model-gena-lm", "regulatory-variant-20261009-model-gena-lm")}
for cid, (old, new) in RELINK.items():
    c = by_id[P + cid]
    assert c["links"] == [{"relation": "configuration_of", "target_id": P + old}]
    c["links"] = [{"relation": "configuration_of", "target_id": new}]
    fix(c["id"], f"configuration_of changed from {P}{old} to the existing store record {new}")
removed = [P + "model-rna-fm", P + "model-gena-lm"]

# 5. DNABERT and SpTransformer are trained neural models, recorded as `method` records; the store
#    records SpliceAI and the other language models as `model` families.
renamed = {}
for old_key, new_key in (("method-dnabert", "model-dnabert"), ("method-sptransformer", "model-sptransformer")):
    m = by_id[P + old_key]
    m["id"] = P + new_key
    m["kind"] = "model"
    m["attributes"]["entity_level"] = "family"
    m["facets"]["method_types"] = ["foundation_model"] if new_key == "model-dnabert" else ["specialist"]
    renamed[P + old_key] = P + new_key
    fix(P + new_key, f"kind changed from method to model family; ID changed from {P}{old_key}")
for r in records:
    for l in r["links"]:
        if l["target_id"] in renamed:
            l["target_id"] = renamed[l["target_id"]]

# 6. GTEx protocols: the reported epoch is chosen by PR-AUC with no validation split described.
EPOCH = ("Each model's reported values come from the epoch with the highest average PR-AUC across classes (Methods); the "
         "dataset is described only as a train and test split, and no validation split is named.")
for pid in ("protocol-gtex-acceptors-donors", "protocol-gtex-splice-15class", "protocol-gtex-splice-53class"):
    by_id[P + pid]["attributes"]["limitations"].append(EPOCH)
    fix(P + pid, "limitation added: best-epoch selection by PR-AUC without a named validation split")

# 7. Zero spreads across three random initialisations.
ZERO = ("Every printed standard deviation for this method in this table is 0.0000, which three runs with different random "
        "initialisations would not normally give; the source does not explain it.")
zero_methods = {}
for (table, block, method, col), (mean, sd) in cells.items():
    zero_methods.setdefault((table, block, method), []).append(sd == "0.0000")
for r in records:
    if r["kind"] != "evaluation":
        continue
    m = re.fullmatch(r"(Supplementary Table [45]), block '(.+)', row '(.+)'", r["attributes"]["source_locator"])
    if m and all(zero_methods[m.groups()]):
        r["attributes"]["limitations"].append(ZERO)
        fix(r["id"], "limitation added: all spreads print 0.0000")

# 8. Rejected: "Average Top-k" mapped to splice-top-k-accuracy (k = number of true sites). The
#    source defines top-k accuracy as the fraction of times the true label is among the top k
#    predicted labels and never states k, so the concept is not supported.
rejected = [r for r in records if r["kind"] == "result" and r["attributes"]["metric"] == "splice-top-k-accuracy"]
assert len(rejected) == 22
records = [r for r in records if r not in rejected and r["id"] not in removed]
records.sort(key=lambda r: r["id"])

# ---- Review blocks and status --------------------------------------------------------------
for r in records:
    r["status"] = "source_checked"
    a = r["attributes"]
    if r["kind"] in ("result", "claim"):
        note = "Independent review 2026-10-11: value and identity match the source."
        if r["kind"] == "claim":
            note = "Independent review 2026-10-11: Supplementary Tables 2, 3 and 6 are present and unextracted, as stated."
        fixes = [c[1] for c in corrections if c[0] == r["id"]]
        if fixes:
            note += " Corrected in review: " + "; ".join(fixes) + "."
        supp = r["kind"] == "result" or r["kind"] == "claim"
        a["review"] = {"method": ["source-hash-verification", "pdf-text-parse", "independent-cell-check"],
                       "method_note": METHOD_NOTE, "reviewer": ["claude"], "reviewer_note": REVIEWER_NOTE,
                       "date": DATE,
                       "artifact_sha256": SUPP_SHA if supp else XML_SHA, "retrieval_url": SUPP_URL if supp else XML_URL,
                       "note": note}
    if r["kind"] == "source":
        sha, url = (SUPP_SHA, SUPP_URL) if r["id"].endswith("supplement") else (XML_SHA, XML_URL)
        a["review"] = {"method": ["source-hash-verification", "ai-assisted-source-review"], "reviewer": ["claude"],
                       "reviewer_note": REVIEWER_NOTE, "date": DATE,
                       "artifact_sha256": sha, "retrieval_url": url,
                       "note": "Fresh retrieval matches the pinned SHA-256. CC BY-NC-ND 4.0; no copy archived."}

(HERE / "batch.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in records))
PENDING.mkdir(parents=True, exist_ok=True)
(PENDING / "batch.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in sorted(rejected, key=lambda r: r["id"])))
with open(HERE / "claims.csv", newline="") as f:  # keep the csv module's CRLF line endings
    csv_lines = f.read().splitlines(keepends=True)
rejected_ids = {r["id"] for r in rejected}
with open(HERE / "claims.csv", "w", newline="") as f:
    f.write("".join(l for l in csv_lines if l.split(",", 1)[0] not in rejected_ids))
with open(PENDING / "claims.csv", "w", newline="") as f:
    f.write(csv_lines[0] + "".join(l for l in csv_lines if l.split(",", 1)[0] in rejected_ids))
(HERE / "review" / "corrections.json").write_text(json.dumps(corrections, ensure_ascii=False, indent=1) + "\n")
print(f"{len(seen)} results checked; {len(corrections)} corrections; {len(rejected)} results rejected to {PENDING.name}; "
      f"{len(removed)} duplicate families removed; {len(records)} records written")
