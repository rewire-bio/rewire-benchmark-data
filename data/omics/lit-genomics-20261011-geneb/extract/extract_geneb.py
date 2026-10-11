"""GENEB official leaderboard (darlednik/GENEB, leaderboard/leaderboard.json at a pinned commit): MCC aggregates.

Usage: python3 -I extract_geneb.py <leaderboard.json> <batch-folder>
Extracts micro MCC, macro MCC and the 13 per-category MCCs for every model in the full-data, 10-shot and 1-shot regimes.
"""
import sys, os, json, re
from decimal import Decimal
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import Batch, extraction_review, sha256

path, folder = sys.argv[1:3]
SHA = sha256(path)
assert SHA == "7c8a9d985e7c2df24514f309bf6102e4f81d9da1b9afbb74856d87e78e01f738", SHA
COMMIT = "9642d481e40c0af23995dcd162b779613f789f97"
URL = f"https://raw.githubusercontent.com/darlednik/GENEB/{COMMIT}/leaderboard/leaderboard.json"
d = json.load(open(path))

b = Batch(folder, "lit-genomics-20261011-geneb")
SRC = b.source("lit-genomics-20261011-geneb-source-leaderboard", "GENEB leaderboard (leaderboard.json, 13 task-type aggregates)", {
    "url": f"https://github.com/darlednik/GENEB/blob/{COMMIT}/leaderboard/leaderboard.json", "artifact_url": URL,
    "version": f"Git commit {COMMIT} (repository pushed 2026-08-22)", "retrieved_at": "2026-10-11T01:42:40Z", "artifact_sha256": SHA,
    "publication_status": "official_project_source", "licence": "Apache-2.0", "media_type": "application/json",
    "limitations": ["Mutable leaderboard; the commit pins this retrieval. The README says the JSON is regenerated from reviewed submissions.",
                    "Benchmark paper: GENEB, arXiv 2606.04525 (v4, 2026-06). The store already holds 22 Table 8 results from v1 (source evidence-expansion-p2-evidence-discovery-final-geneb-47975089c0ca).",
                    "Accuracy and F1 aggregates, and the 100 per-task scores in leaderboard_tasks.json, were not extracted."]})
SIDS = [SRC]
REV = lambda loc: extraction_review(["deterministic-table-parse"], "Read the pinned leaderboard.json with tools/extract_geneb.py; keys data.<regime>[i].micro_MCC, macro_MCC and cat_MCC.<category>; model id from the 'model' key. " + loc, SHA, URL)

CATS = ["Histone Mod.", "Promoters", "Enhancers", "DNA Methyl.", "Splice Sites", "lncRNA", "Mouse Enh.", "TF Binding", "Species Clf.", "Regulatory", "Virus/Phage", "Coding/NC", "Chromatin Acc."]
REGIMES = {"full": "full training data", "10shot": "10-shot", "1shot": "1-shot"}
BENCH = b.entity("benchmark", b.rid("benchmark", "geneb"), "GENEB leaderboard",
    "Frozen-embedding probing benchmark of genomic foundation models over 100 tasks in 13 categories, with full-data, 10-shot and 1-shot regimes.",
    SIDS, {"entity_level": "suite", "version": f"Leaderboard at commit {COMMIT[:12]}", "task": "Genomic sequence classification from frozen embeddings",
           "scope_note": "MCC aggregates only: micro average over all 100 tasks, macro average (unweighted mean of the 13 category MCCs), and per category.", "source_locator": "leaderboard/README.md (Evaluation table: logistic-regression probe on frozen embeddings, max_iter=1000; Macro = mean of the 13 category scores); leaderboard.json"})
data = b.entity("dataset", b.rid("data", "geneb-100-tasks"), "GENEB 100 tasks", "The 100 GENEB tasks (Hugging Face dataset darlednik/geneb-tasks).", SIDS,
                {"population": "100 classification tasks in 13 categories (leaderboard_tasks.json)", "split": "Task-defined train and test splits",
                 "source_locator": "leaderboard/README.md 'Task data'", "missing_metadata": {"version": {"reason": "unreported"}}})
protos = {}
for r, rl in REGIMES.items():
    protos[r] = b.entity("protocol", b.rid("protocol", r), f"GENEB leaderboard, {rl}, MCC aggregates", f"GENEB probing of frozen embeddings, {rl} regime.", SIDS,
        {"protocol": f"Logistic-regression probe (max_iter=1000) on frozen embeddings, trained per task in the {rl} regime; MCC aggregated as the micro average over all 100 tasks, the macro average (unweighted mean of the 13 category MCCs) and per category.",
         "version": f"Leaderboard at commit {COMMIT[:12]}", "metric": "matthews-correlation-coefficient", "metric_direction": "higher", "unit": "unitless",
         "limitations": ["Leaderboard aggregates; per-task values not extracted."],
         "source_locator": f"leaderboard.json data.{r}"}, links=[{"relation": "part_of", "target_id": BENCH}, {"relation": "uses_data", "target_id": data}])

EXIST = {"nucleotide-transformer-v2": "catalog-model-nt-v2", "nucleotide-transformer-2.5b": "discovery-model-nucleotide-transformer",
         "agro-nucleotide-transformer": "discovery-model-agro-nucleotide-transformer", "dnabert2": "discovery-model-dnabert-2",
         "caduceus": "regulatory-variant-20261009-model-caduceus", "hyenadna": "regulatory-variant-20261009-model-hyenadna", "gena-lm": "regulatory-variant-20261009-model-gena-lm",
         "enformer": "regulatory-variant-20261009-model-enformer", "evo-1": "discovery-model-evo-2",
         "metagene-1": "catalog-model-metagene-1"}
NEWFAM = [("BioFM", "BioFM"), ("deepgene", "DeepGene"), ("dna_gpt", "DNAGPT"), ("DNABERT-S", "DNABERT-S"), ("eccdnamamba", "eccDNAMamba"),
          ("GENERator", "GENERator"), ("GenomeOcean", "GenomeOcean"), ("genomics-fm", "genomics-fm"), ("gpt2_gene", "GPT-2 gene models"), ("GROVER", "GROVER"),
          ("JanusDNA", "JanusDNA"), ("LucaOne", "LucaOne"), ("MutBERT", "MutBERT"), ("Omni-DNA", "Omni-DNA"), ("OmniNA", "OmniNA"),
          ("PlantCaduceus", "PlantCaduceus"), ("space", "SPACE"), ("splicebert", "SpliceBERT")]
new = {}
def family(model):
    for k, f in EXIST.items():
        if model.lower().startswith(k):
            return f
    for k, name in NEWFAM:
        if model.startswith(k):
            if name not in new:
                new[name] = b.entity("model", b.rid("model", name), name, f"{name} genomic foundation model family as listed on the GENEB leaderboard.", SIDS,
                                     {"reported_name": name, "entity_level": "family", "source_locator": "leaderboard.json 'model' and 'disp' keys",
                                      "missing_metadata": {"version": {"reason": "inapplicable", "note": "Family record; checkpoints are on configurations"}}}, method_types=["foundation_model"])
            return new[name]
    raise KeyError(model)

# Evo 1 is not Evo 2; give it its own family rather than the Evo 2 record.
EXIST.pop("evo-1")
NEWFAM.append(("evo-1", "Evo"))

n = 0
cfgs = {}
for r in REGIMES:
    rows = d["data"][r]
    assert len(rows) == 41
    for x in rows:
        m = x["model"]
        if m not in cfgs:
            cfgs[m] = b.entity("configuration", b.rid("config", m), f"{x['disp']} (GENEB leaderboard)", f"{m} as evaluated on the GENEB leaderboard.", SIDS,
                {"reported_name": m, "foundation_model_eligible": not m.startswith("enformer"), "parameters": f"{x['params']} parameters as listed; frozen embeddings; leaderboard display name '{x['disp']}'",
                 "access_reuse": "Public checkpoint as named on the leaderboard", "version": m, "source_locator": f"leaderboard.json data.full row model '{m}'"},
                method_types=["supervised_machine_learning"] if m.startswith("enformer") else ["foundation_model"], links=[{"relation": "configuration_of", "target_id": family(m)}])
        origin = "independent_paper" if x["official"] else "unreported"
        ev = b.evaluation(b.rid("eval", m, r), f"{x['disp']} on GENEB ({REGIMES[r]})", SIDS, cfgs[m], protos[r], data, origin,
            {"protocol_id": protos[r], "dataset_version": None, "split": REGIMES[r], "population": "100 tasks", "inputs": "DNA sequence; frozen embeddings",
             "adaptation": "Logistic-regression probe on frozen embeddings", "metric_implementation": "MCC", "aggregation": "micro, macro and per-category averages", "budget": REGIMES[r]},
            f"leaderboard.json data.{r}, model '{m}'",
            extra={"limitations": [f"Leaderboard entry status: '{x['submitted']}' (official={x['official']})."]})
        cells = [("micro_MCC", x["micro_MCC"], "micro average: mean over all 100 tasks"), ("macro_MCC", x["macro_MCC"], "macro average: unweighted mean of the 13 category MCCs")] + \
                [(f"cat_MCC.{c}", x["cat_MCC"][c], f"category '{c}'") for c in CATS]
        assert set(x["cat_MCC"]) == set(CATS)
        for key, v, q in cells:
            loc = f"leaderboard.json data.{r}, model '{m}', key '{key}'"
            b.result(b.rid("result", m, r, key.replace("cat_MCC.", "")), f"{x['disp']} GENEB {r} {key}", SRC, SIDS, ev, repr(v) if isinstance(v, float) else str(v),
                     "matthews-correlation-coefficient", "higher", "unitless", loc, REV(loc), qualifier=f"{REGIMES[r]}; {q}",
                     numeric=format(Decimal(repr(v)), "f"), extra={"printed_value_basis": "Full-precision JSON number as stored"})
            n += 1
assert n == 41 * 3 * 15, n
print(json.dumps(b.write()))
