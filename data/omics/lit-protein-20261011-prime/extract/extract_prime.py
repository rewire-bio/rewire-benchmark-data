"""PRIME (Jiang et al. 2026, BMC Genomics): Table 1, protein language model scales and embedding
choices on SARS-CoV-2 RBD binding and expression, under a random and a position-stratified split.

Usage: python3 -I extract_prime.py <PMC13425921.xml> <batch-folder>
Every cell of Table 1 is extracted.
"""
import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import Batch, extraction_review, sha256, sd, finalise
from jats import tables

path, folder = sys.argv[1:3]
SHA = sha256(path)
assert SHA == "f6aac4c25dd93026f87ce9a2e327c95faf4c3014d7f9ae04bb11f208ce047971", SHA
URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13425921/fullTextXML"
PREFIX = "lit-protein-20261011-prime"

b = Batch(folder, PREFIX, ["protein-function"])
SRC = b.source(f"{PREFIX}-source-prime2026", "PRIME: An evaluation framework for protein representation inference and generalization in viral mutation space", {
    "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC13425921/",
    "artifact_url": URL,
    "doi": "10.1186/s12864-026-12976-5",
    "version": "Version of record, BMC Genomics 2026 (PMC13425921 JATS full text)",
    "retrieved_at": "2026-10-11T21:30:00Z",
    "artifact_sha256": SHA,
    "publication_status": "peer_reviewed",
    "licence": "CC BY 4.0",
    "media_type": "application/xml",
    "venue": "BMC Genomics",
    "year": 2026,
    "limitations": [
        "Table 1 only. The lineage-clustering, temporal-dynamics and attention analyses are figures and were not extracted.",
        "The One-Hot Mean row has no embedding or fine-tuning setting; its three leading cells repeat the row label in the XML and are recorded as a single baseline configuration.",
        "The plus-minus values are the standard deviation across random seeds (Table 1 footnote, pointing at Supplementary Table 6, which was not retrieved). Table 1 uses five folds and the Methods name three seeds, so the sample count behind each spread is not determined by the article.",
    ]})
SIDS = [SRC]

REV = lambda loc: extraction_review(
    ["deterministic-table-parse"],
    "Parsed the pinned Europe PMC JATS XML with extract_prime.py (table-wrap grid with rowspan and colspan expanded, three header rows asserted); row and column labels asserted. " + loc,
    SHA, URL)

BENCH = b.entity("benchmark", b.rid("benchmark", "prime"), "PRIME viral mutation-space evaluation",
    "Evaluation framework for protein representations on SARS-CoV-2 receptor-binding-domain mutants: ACE2 binding and expression regression under a random split and a position-stratified split that holds out mutated positions.",
    SIDS, {"entity_level": "suite", "version": "As published 2026",
           "task": "Predict RBD mutant binding and expression from protein language model representations",
           "scope_note": "The position-stratified split holds out whole mutated positions, so it measures generalisation to unseen positions rather than unseen mutants.",
           "source_locator": "Table 1 and its surrounding Results text",
           "limitations": ["One protein (SARS-CoV-2 RBD) and two phenotypes; results do not transfer to other proteins without further evidence.",
                           "Author-reported: the PRIME authors ran every model and also contribute the fine-tuned ESM-RBD variants, which are the best-scoring rows."]})

DATA = b.entity("dataset", b.rid("data", "rbd-mutants"), "SARS-CoV-2 RBD mutant binding and expression measurements",
    "Deep mutational scanning measurements of SARS-CoV-2 receptor-binding-domain mutants used by PRIME for binding and expression regression.",
    SIDS, {"population": "Mutated SARS-CoV-2 RBD variants with ACE2 binding and expression measurements",
           "split": "Random split and position-stratified split",
           "source_locator": "Table 1 caption: 'Benchmarking PRIME across different model scales and validation regimes for mutated RBD binding and expression'",
           "missing_metadata": {"version": {"reason": "unreported"},
                                "total": {"reason": "unextracted", "note": "The variant count is in the Methods text, not in Table 1"}}})

FAMILIES = {
    "ESM-2": "catalog-model-esm-2",
    "ESM-C": None,
}
ESMC = b.entity("model", b.rid("model", "esm-c"), "ESM-C",
    "ESM Cambrian protein language model family, evaluated at 300M and 600M parameters.", SIDS,
    {"entity_level": "family", "reported_name": "ESM-C",
     "source_locator": "Table 1 rows 'ESM-C 300M' and 'ESM-C 600M'",
     "missing_metadata": {"version": {"reason": "inapplicable", "note": "Family record; the evaluated sizes are on the configurations"}}},
    method_types=["foundation_model"], links=[{"relation": "alias_of", "target_id": "discovery-model-esmc"}])
FAMILIES["ESM-C"] = "discovery-model-esmc"  # review correction P4: the store's existing ESMC family

ONEHOT = b.entity("method", b.rid("method", "one-hot-mean"), "One-hot mean baseline",
    "Baseline representation: the mean of one-hot encoded residues, used in place of a language model embedding.",
    SIDS, {"entity_level": "method", "reported_name": "One-Hot Mean",
           "source_locator": "Table 1, row 'One-Hot Mean'",
           "missing_metadata": {"version": {"reason": "inapplicable", "note": "A fixed encoding, not a released model"}}},
    method_types=["conventional_pipeline"])

EMBED = {"CLS": "the CLS token embedding", "Mean": "the mean over residue embeddings"}
METRICS = {"R²": ("r2", "coefficient-of-determination", "higher", "unitless"),
           "RMSE": ("rmse", "root-mean-squared-error", "lower", "unit-unreported")}
TARGETS = {"Binding": "ACE2 binding", "Expression": "RBD expression"}
SPLITS = {"Random Split": ("random", "Random split over RBD mutants"),
          "Position-Stratified Split": ("position-stratified", "Position-stratified split holding out whole mutated positions")}

grids = {lab.strip(): (cap, g) for lab, cap, g in tables(open(path, "rb").read())}
cap, grid = grids["Table 1"]
h1, h2, h3 = grid[0], grid[1], grid[2]
assert h1[:3] == ["Model", "EmbedMethod", "Fine-tuned"], h1
columns = []
for split, target, metric in zip(h1[3:], h2[3:], h3[3:]):
    assert split in SPLITS and target in TARGETS and metric in METRICS, (split, target, metric)
    columns.append((split, target, metric))

protos = {}
for split, target, metric in columns:
    key = (split, target, metric)
    mkey, concept, direction, unit = METRICS[metric]
    protos[key] = b.entity("protocol", b.rid("protocol", SPLITS[split][0], target, mkey),
        f"PRIME {TARGETS[target]} regression, {SPLITS[split][1]}, {metric}",
        f"Supervised regression of {TARGETS[target]} from protein representations under the {SPLITS[split][1].lower()}, scored by {metric}.",
        SIDS, {"protocol": f"Representations of RBD mutants are fed to a supervised regression head and scored on held-out data under the {SPLITS[split][1].lower()}." + " Binding and expression are predicted jointly by one multi-task fully connected network over the representations (Methods, Input features), so the two targets are not independent runs.",
               "metric": concept, "metric_direction": direction, "unit": unit,
               "metric_qualifier": f"{TARGETS[target]}; {SPLITS[split][1]}",
               "version": "As published 2026",
               "source_locator": f"Table 1, columns '{split}' / '{target}' / '{metric}'",
               "limitations": ["Table 1 prints no unit for RMSE; the measurement scale is the assay's own."] if unit == "unit-unreported" else [],
               "uncertainty_reporting": {"printed": "mean plus or minus standard deviation across random seeds", "runs": "Five folds (Fig. 1C) and three seeds (Methods) are stated; which the printed spread is taken over is not"}},
        links=[{"relation": "part_of", "target_id": BENCH}, {"relation": "uses_data", "target_id": DATA}])

CELL = re.compile(r"^(-?[\d.]+)\s*±\s*([\d.]+)$")
cfg = {}
n_results = 0
for row in grid[3:]:
    model, embed, tuned = row[0].strip(), row[1].strip(), row[2].strip()
    if model == embed == tuned:  # the One-Hot Mean baseline row repeats its label across the three leading cells
        key = "one-hot-mean"
        label = model
        if key not in cfg:
            cfg[key] = b.entity("configuration", b.rid("config", key), "One-hot mean representation (PRIME)",
                "Mean one-hot residue encoding with the PRIME supervised head; the paper's representation baseline.",
                SIDS, {"reported_name": "One-Hot Mean", "reported_configuration": "Mean of one-hot encoded residues; no pretrained language model",
                       "method_role": "baseline representation",
                       "foundation_model_eligible": False,
                       "source_locator": "Table 1, row 'One-Hot Mean'",
                       "missing_metadata": {"version": {"reason": "inapplicable", "note": "A fixed encoding, not a released checkpoint"}}},
                method_types=["conventional_pipeline"], links=[{"relation": "configuration_of", "target_id": ONEHOT}])
        row_locator = "row 'One-Hot Mean'"
        setting = "one-hot mean representation"
    else:
        assert embed in EMBED and tuned in ("×", "✓"), (model, embed, tuned)
        family = next((f for f in FAMILIES if model.startswith(f)), None)
        assert family, model
        fine_tuned = tuned == "✓"
        key = f"{model} {embed} {'finetuned' if fine_tuned else 'frozen'}"
        label = key
        if key not in cfg:
            cfg[key] = b.entity("configuration", b.rid("config", model, embed, "finetuned" if fine_tuned else "frozen"),
                f"{model}, {EMBED[embed]}, {'fine-tuned' if fine_tuned else 'not fine-tuned'} (PRIME)",
                f"{model} representations taken as {EMBED[embed]}, {'fine-tuned on the RBD data' if fine_tuned else 'frozen'}, with the PRIME supervised head.",
                SIDS, {"reported_name": model, "version": model,
                       "representation": EMBED[embed],
                       "training_setting": "Fine-tuned on the RBD measurements" if fine_tuned else "None; frozen representations",
                       "foundation_model_eligible": True,
                       "source_locator": f"Table 1, row '{model}' / '{embed}' / '{tuned}'"},
                method_types=["foundation_model"], links=[{"relation": "configuration_of", "target_id": FAMILIES[family]}])
        row_locator = f"row '{model}' / '{embed}' / '{tuned}'"
        setting = f"{EMBED[embed]}, {'fine-tuned' if fine_tuned else 'frozen'}"
    for (split, target, metric), cell in zip(columns, row[3:]):
        cell = cell.strip()
        m = CELL.match(cell)
        assert m, (label, split, target, metric, cell)
        mkey, concept, direction, unit = METRICS[metric]
        proto = protos[(split, target, metric)]
        ev_id = b.rid("eval", SPLITS[split][0], target, mkey, key)
        if ev_id not in b.ids:
            b.evaluation(ev_id, f"{label}: {TARGETS[target]} {metric}, {SPLITS[split][1]}", SIDS,
                cfg[key], proto, DATA, "author_reported",
                {"protocol_id": proto, "dataset_version": None, "split": SPLITS[split][1],
                 "population": "RBD mutants with measured binding and expression",
                 "inputs": f"RBD mutant sequence; {setting}",
                 "adaptation": "Supervised regression head on the representations" + ("; backbone fine-tuned" if "fine-tuned" in setting else ""),
                 "metric_implementation": metric, "aggregation": "Mean with standard deviation across random seeds, over five cross-validation folds (Table 1 footnote; Fig. 1C)", "budget": None},
                f"Table 1, {row_locator}, columns '{split}' / '{target}' / '{metric}'")
        b.result(b.rid("result", SPLITS[split][0], target, mkey, key),
            f"{label} {TARGETS[target]} {metric} ({SPLITS[split][0]} split)", SRC, SIDS, ev_id,
            cell, concept, direction, unit,
            f"Table 1, {row_locator}, columns '{split}' / '{target}' / '{metric}'",
            REV(f"Table 1, {row_locator}, columns '{split}' / '{target}' / '{metric}'"),
            qualifier=f"{TARGETS[target]}; {SPLITS[split][1]}; {setting}",
            uncertainty=sd(m.group(2), cell, scope="Standard deviation across random seeds (Table 1 footnote: 'with ± values representing the standard deviation across random seeds seen in Supplementary Table 6'). Table 1 uses five folds (Fig. 1C) and the Methods name three seeds, and the article does not say which of the two the spread is taken over, so no sample count is recorded."),
            numeric=m.group(1),
            extra={"printed_value_basis": "Mean plus or minus standard deviation as printed"})
        n_results += 1

# Review corrections P5 and P6: the new source and two re-extracted cells supersede the store's
# earlier records for the same bytes and cells; the old records are not edited.
recs = {r["id"]: r for r in b.records}
recs[SRC]["links"] += [{"relation": "supersedes", "target_id": "prime-2026"},
                       {"relation": "supersedes", "target_id": "evidence-expansion-prime-2026-f6aac4c2"}]
recs[f"{PREFIX}-result-position-stratified-binding-r2-esm-2-8m-mean-frozen"]["links"].append({"relation": "supersedes", "target_id": "lit-021"})
recs[f"{PREFIX}-result-position-stratified-binding-r2-esm-c-300m-mean-frozen"]["links"].append({"relation": "supersedes", "target_id": "lit-022"})
assert recs[f"{PREFIX}-result-position-stratified-binding-r2-esm-2-8m-mean-frozen"]["attributes"]["printed_value"].startswith("0.0248")
assert recs[f"{PREFIX}-result-position-stratified-binding-r2-esm-c-300m-mean-frozen"]["attributes"]["printed_value"].startswith("-0.0162")
assert sum(1 for r in b.records if r["kind"] == "configuration" and {"relation": "configuration_of", "target_id": "discovery-model-esmc"} in r["links"]) == 8

finalise(b, "reviewer-ps-1",
         "Reviewer re-retrieved the Europe PMC JATS XML and matched its SHA-256; an independent JATS table-grid parse compared all 168 results (printed and numeric values and spreads) with 0 mismatches; a hand sample of 40 values covering every column matched.",
         SHA, URL)
counts = b.write()
print(counts, "results", n_results)
