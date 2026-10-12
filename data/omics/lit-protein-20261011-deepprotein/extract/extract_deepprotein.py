"""DeepProtein (Shen et al. 2025, Bioinformatics): Tables 2 to 8, the benchmark of sequence
models, graph models, protein language models and chemistry LLMs across nine task groups.

Usage: python3 -I extract_deepprotein.py <PMC12553333.xml> <batch-folder>
Every printed cell of Tables 2 to 8 is extracted. Cells printed as '/' (the footnote says
structure-based and pretrained language models were disregarded for residue-level and secondary
structure prediction) are not results and are left out; OOM, 'Length Exceeded' and NaN cells are
kept with a missing value reason.
"""
import sys, os, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import Batch, extraction_review, sha256, sd, finalise

# Review decisions pending the team lead (see review.md): KEEP_CONCERN keeps the reworded evidence
# concern of correction C1; JUDGEMENT_STATUS serves (source_checked) or holds (needs_review) the judgement.
KEEP_CONCERN = os.environ.get("DP_KEEP_CONCERN", "1") == "1"
JUDGEMENT_STATUS = os.environ.get("DP_JUDGEMENT_STATUS", "needs_review")
from jats import tables

path, folder = sys.argv[1:3]
SHA = sha256(path)
assert SHA == "b586921363170806d9f332afb37762ea61f464da6067a3ef0ab8853281964b7f", SHA
URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12553333/fullTextXML"
PREFIX = "lit-protein-20261011-deepprotein"

b = Batch(folder, PREFIX, ["protein-function"])
SRC = b.source(f"{PREFIX}-source-shen2025", "DeepProtein: deep learning library and benchmark for protein sequence learning", {
    "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC12553333/",
    "artifact_url": URL,
    "doi": "10.1093/bioinformatics/btaf165",
    "version": "Version of record, Bioinformatics 2025 (PMC12553333 JATS full text)",
    "retrieved_at": "2026-10-11T21:30:00Z",
    "artifact_sha256": SHA,
    "publication_status": "peer_reviewed",
    "licence": "CC BY 4.0",
    "media_type": "application/xml",
    "venue": "Bioinformatics",
    "year": 2025,
    "limitations": [
        "Tables 2 to 8. Table 1 (a feature comparison with earlier benchmark libraries), Table 9 (default hyperparameters) and the task-instruction table hold no measurements and were not extracted.",
        "The regression correlation columns are printed as rho. The Evaluation metrics section defines rho as Spearman rank correlation; Figure 3's caption calls it 'Spearman (Pearson) Coefficient'. The section's definition is used.",
        "Cells printed as '/' are not measurements: the Table 7 footnote says structure-based and pretrained protein language models were disregarded for residue-level and secondary structure prediction. They are left out, not recorded as zero.",
        "Bold, underline and the '**' significance marks are kept in printed_value where they are part of the printed cell; the article's own statistical tests were not re-run.",
    ]} | ({"evidence_concerns": [{
        "source_id": f"{PREFIX}-source-shen2025",
        "message": "Figure 3's caption calls the regression metric 'Spearman (Pearson) Coefficient' while the Evaluation metrics section defines rho as Spearman rank correlation and R2 separately. The section's definition is taken as authoritative and the rho columns are recorded as Spearman; the caption wording is noted so a reader of the figure is not surprised.",
        "source_locator": "Tables 2, 4 and 6 column headings 'rho' and 'R2'; Figure 3 caption",
        "artifact_sha256": SHA,
        "review_date": "2026-10-11",
    }]} if KEEP_CONCERN else {}))
SIDS = [SRC]

REV = lambda loc: extraction_review(
    ["deterministic-table-parse"],
    "Parsed the pinned Europe PMC JATS XML with extract_deepprotein.py (table-wrap grid with rowspan and colspan expanded, two header rows and the split-size row asserted); row and column labels asserted. " + loc,
    SHA, URL)

BENCH = b.entity("benchmark", b.rid("benchmark", "deepprotein"), "DeepProtein benchmark",
    "Benchmark of sequence-based, graph-based and pretrained protein models, plus two chemistry LLMs, over protein function, localization, interaction, epitope and paratope, developability, CRISPR repair and structure prediction tasks, with datasets taken from TAPE, PEER and TDC.",
    SIDS, {"entity_level": "suite", "version": "As published 2025 (DeepProtein library)",
           "task": "Protein sequence learning across nine task groups",
           "scope_note": "Each task keeps the split of its original benchmark; every method is trained with five random seeds and the mean and standard deviation are reported.",
           "source_locator": "Results, 'Each individual split is reported from Tables 2-7'; Tables 2 to 8",
           "limitations": ["Author-reported: the DeepProtein authors both run the baselines and introduce DeepProt-T5.",
                           "Residue-level and secondary structure tasks were not run for structure-based and language models (Table 7 footnote)."]})

# dataset key: (name, description, areas override, train/valid/test row position)
DATASETS = {
    "Fluorescence": ("Fluorescence (TAPE)", "Green fluorescent protein brightness regression, as distributed with TAPE.", None),
    "Stability": ("Stability (TAPE)", "Protein stability regression, as distributed with TAPE.", None),
    "β-lactamase": ("beta-lactamase (PEER)", "beta-lactamase activity regression, as distributed with PEER.", None),
    "Solubility": ("Solubility (PEER)", "Protein solubility classification, as distributed with PEER.", None),
    "Subcellular": ("Subcellular localization (PEER)", "Ten-class subcellular localization classification.", None),
    "Binary": ("Binary localization (PEER)", "Membrane-bound against soluble localization classification.", None),
    "PPI Affinity": ("PPI affinity (PEER)", "Protein-protein binding affinity regression.", None),
    "Yeast PPI": ("Yeast PPI (PEER)", "Yeast protein-protein interaction classification.", None),
    "Human PPI": ("Human PPI (PEER)", "Human protein-protein interaction classification.", None),
    "IEDB": ("IEDB epitope prediction", "Residue-level B-cell epitope prediction on the IEDB dataset.", None),
    "PDB-Jespersen": ("PDB-Jespersen epitope prediction", "Residue-level epitope prediction on the Jespersen PDB dataset.", None),
    "SAbDab-Liberis": ("SAbDab-Liberis paratope prediction", "Residue-level paratope prediction on the Liberis SAbDab dataset.", None),
    "TAP": ("TAP antibody developability", "Therapeutic antibody profiler developability regression.", None),
    "SAbDab-Chen": ("SAbDab-Chen antibody developability", "Antibody developability regression on the Chen SAbDab dataset.", None),
    "CRISPR-Leenay": ("CRISPR-Leenay repair outcome", "CRISPR repair outcome regression on the Leenay dataset.", ["dna-genomes"]),
    "Fold": ("Fold classification (TAPE)", "Protein fold class prediction.", ["protein-structure"]),
    "Secondary Structure": ("Secondary structure prediction (TAPE)", "Per-residue secondary structure prediction.", ["protein-structure"]),
}

# metric column heading: (key, concept, direction, unit, unit_detail, qualifier note)
METRICS = {
    "ρ ↑": ("rho", "spearman-correlation", "higher", "unitless", None,
        "Spearman rank correlation, as defined in the article's Evaluation metrics section; supervised split"),
    "MAE ↓": ("mae", "mean-absolute-error", "lower", "unit-unreported", "error in the task's own measurement units", "mean absolute error"),
    "PR-AUC ↑": ("pr-auc", "auprc", "higher", "percent", None, "area under the precision-recall curve, printed on a 0 to 100 scale"),
    "Averaged F1 ↑": ("avg-f1", "macro-f1", "higher", "percent", None,
        "averaged macro F1 (Figure 3 caption: 'averaged macro F1'), printed on a 0 to 100 scale"),
    "Acc ↑": ("acc", "accuracy", "higher", "percent", None, "accuracy, printed on a 0 to 100 scale"),
    "ROC-AUC ↑": ("roc-auc", "auroc", "higher", "percent", "printed x100", "area under the ROC curve, printed on a 0 to 100 scale"),
    "R2 ↑": ("r2", "coefficient-of-determination", "higher", "unitless", None, "coefficient of determination"),
    "Time (hour)": ("time", "runtime", "lower", "hour", "training time for the task", "training wall-clock time"),
    "GPU Memory (GB)": ("memory", "peak-memory", "lower", "gigabyte", "GPU memory", "peak GPU memory"),
}

# model label: (key, family id or None, method types, group)
MODELS = {
    "CNN": ("cnn", None, ["specialist"], "sequence model"),
    "CNN-RNN": ("cnn-rnn", None, ["specialist"], "sequence model"),
    "Transformer": ("transformer", None, ["specialist"], "sequence model"),
    "GCN": ("gcn", None, ["specialist"], "graph model"),
    "GAT": ("gat", None, ["specialist"], "graph model"),
    "NeuralFP": ("neuralfp", None, ["specialist"], "graph model"),
    "AttentiveFP": ("attentivefp", None, ["specialist"], "graph model"),
    "MPNN": ("mpnn", None, ["specialist"], "graph model"),
    "PAGTN": ("pagtn", None, ["specialist"], "graph model"),
    "Graphormer": ("graphormer", None, ["specialist"], "graph model"),
    "ESM-1b": ("esm-1b", "uc20260930-model-esm-1b", ["foundation_model"], "protein language model"),
    "ESM-2-650M": ("esm-2-650m", "catalog-model-esm-2", ["foundation_model"], "protein language model"),
    "Prot-T5-XL": ("prot-t5-xl", None, ["foundation_model"], "protein language model"),
    "ProtBert": ("protbert", None, ["foundation_model"], "protein language model"),
    "Deep Prot-T5": ("deep-prot-t5", None, ["foundation_model"], "fine-tuned protein language model introduced by this paper"),
    "Prot-T5": ("prot-t5", None, ["foundation_model"], "protein language model"),
    "ChemLLM-7B": ("chemllm-7b", None, ["foundation_model"], "chemistry large language model prompted for the task"),
    "LlaSMol-Mistral-7B": ("llasmol-mistral-7b", None, ["foundation_model"], "chemistry large language model prompted for the task"),
}
FAMILY_DESC = {
    "cnn": "Convolutional neural network over the one-hot encoded sequence.",
    "cnn-rnn": "Convolutional network followed by a recurrent layer over the sequence.",
    "transformer": "Transformer encoder trained from scratch on the task's sequences.",
    "gcn": "Graph convolutional network over the protein graph.",
    "gat": "Graph attention network over the protein graph.",
    "neuralfp": "Neural fingerprint graph network.",
    "attentivefp": "Attentive fingerprint graph network.",
    "mpnn": "Message passing neural network over the protein graph.",
    "pagtn": "Path-augmented graph transformer network.",
    "graphormer": "Graph transformer (Graphormer) over the protein graph.",
    "prot-t5-xl": "ProtT5-XL protein language model.",
    "prot-t5": "ProtT5 protein language model, as named in the resource-usage table.",
    "protbert": "ProtBert protein language model.",
    "deep-prot-t5": "DeepProt-T5: Prot-T5-XL fine-tuned per task, introduced by the DeepProtein authors.",
    "chemllm-7b": "ChemLLM-7B chemistry large language model, prompted for protein property questions.",
    "llasmol-mistral-7b": "LlaSMol-Mistral-7B chemistry large language model, prompted for protein property questions.",
}

TABLES = {
    "Table 2.": ("protein function prediction", [("Fluorescence", "ρ ↑"), ("Fluorescence", "MAE ↓"),
        ("Stability", "ρ ↑"), ("Stability", "MAE ↓"), ("β-lactamase", "ρ ↑"),
        ("β-lactamase", "MAE ↓"), ("Solubility", "PR-AUC ↑"), ("Solubility", "Averaged F1 ↑")]),
    "Table 3.": ("protein localization prediction", [("Subcellular", "Acc ↑"), ("Subcellular", "Averaged F1 ↑"),
        ("Binary", "PR-AUC ↑"), ("Binary", "Averaged F1 ↑")]),
    "Table 4.": ("protein-protein interaction prediction", [("PPI Affinity", "R2 ↑"), ("PPI Affinity", "MAE ↓"),
        ("Yeast PPI", "PR-AUC ↑"), ("Yeast PPI", "Averaged F1 ↑"), ("Human PPI", "PR-AUC ↑"),
        ("Human PPI", "Averaged F1 ↑")]),
    "Table 5.": ("epitope and paratope prediction", [("IEDB", "ROC-AUC ↑"), ("IEDB", "Averaged F1 ↑"),
        ("PDB-Jespersen", "ROC-AUC ↑"), ("PDB-Jespersen", "Averaged F1 ↑"),
        ("SAbDab-Liberis", "ROC-AUC ↑"), ("SAbDab-Liberis", "Averaged F1 ↑")]),
    "Table 6.": ("antibody developability and CRISPR repair outcome prediction", [("TAP", "R2 ↑"), ("TAP", "MAE ↓"),
        ("SAbDab-Chen", "R2 ↑"), ("SAbDab-Chen", "MAE ↓"), ("CRISPR-Leenay", "R2 ↑"), ("CRISPR-Leenay", "MAE ↓")]),
    "Table 7.": ("protein folding prediction", [("Fold", "Acc ↑"), ("Fold", "Averaged F1 ↑"),
        ("Secondary Structure", "Acc ↑"), ("Secondary Structure", "Averaged F1 ↑")]),
}
# Table 8 maps its own dataset names to the dataset records above.
TABLE8_DATASETS = {"Fluorescence": "Fluorescence", "Stability": "Stability", "Beta": "β-lactamase",
                   "Solubility": "Solubility", "SubCellular": "Subcellular", "SubCellular-Bin": "Binary",
                   "PPI_Affinity": "PPI Affinity", "Yeast-PPI": "Yeast PPI", "Human-PPI": "Human PPI",
                   "TAP": "TAP", "SAbDab-Chen": "SAbDab-Chen", "CRISPR": "CRISPR-Leenay", "Fold": "Fold",
                   "Secondary Structure": "Secondary Structure", "SS": "Secondary Structure"}

SEEDS = "Five random seeds (table footnote a: 'we used five different random seeds to perform independent runs, reporting the average results along with their standard deviations')"
UNRUN = {"OOM": ("unavailable", "Printed OOM: the run ran out of memory"),
         "Length Exceeded": ("unavailable", "Printed 'Length Exceeded': the sequences exceed the model's context"),
         "NaN": ("unavailable", "Printed NaN: the model produced no usable prediction")}
CELL = re.compile(r"^(−?-?[\d.]+)(?:\s*±\s*([\d.]+))?(\*\*)?$")

grids = {lab.strip(): (cap, g) for lab, cap, g in tables(open(path, "rb").read())}

data_ids, split_sizes = {}, {}
models, protos = {}, {}


def dataset(key):
    if key not in data_ids:
        name, desc, areas = DATASETS[key]
        rec = {"id": b.rid("data", key), "kind": "dataset", "name": name, "description": desc,
               "status": "needs_review", "facets": {"areas": areas or b.areas, "contexts": b.contexts},
               "source_ids": SIDS, "links": [], "attributes": {
                   "split": split_sizes.get(key, "As distributed by the original benchmark"),
                   "source_locator": f"Tables 2 to 7, column group '{key}'; the train/valid/test row of its table",
                   "missing_metadata": {"version": {"reason": "unreported", "note": "The article names the source benchmark without a dataset version"}}}}
        if key in split_sizes:
            rec["attributes"]["population"] = f"train/valid/test {split_sizes[key]}"
        data_ids[key] = b.add(rec)
    return data_ids[key]


# Review correction C5 (the reviewer's attribute name identity_note is not declared for configurations;
# the declared key model_identity_note carries the reviewer's exact text).
PROT_T5_NOTE = "Table 8 prints 'Prot-T5' and Tables 2 to 7 print 'Prot-T5-XL'. They are kept as separate configurations because the article does not state that they are the same checkpoint; their values must not be pooled."


def model_cfg(label):
    key, family, mtypes, group = MODELS[label]
    if key in models:
        return models[key]
    if family is None:
        family = b.entity("model" if "LLM" not in group else "model", b.rid("model", key), label,
            FAMILY_DESC[key], SIDS,
            {"entity_level": "family", "reported_name": label,
             "source_locator": f"Tables 2 to 8, row '{label}'",
             "missing_metadata": {"version": {"reason": "unreported", "note": "The tables name the model without a release version"}}},
            method_types=mtypes)
    cfg = b.entity("configuration", b.rid("config", key), f"{label} (DeepProtein benchmark)",
        f"{label} as trained and evaluated in the DeepProtein benchmark ({group}).", SIDS,
        {"reported_name": label, "reported_configuration": f"{group}; default DeepProtein configuration (Table 9)",
         **({"model_identity_note": PROT_T5_NOTE} if key in ("prot-t5", "prot-t5-xl") else {}),
         "foundation_model_eligible": "foundation_model" in mtypes,
         "source_locator": f"Tables 2 to 8, row '{label}'; Table 9 for the default configuration",
         "missing_metadata": {"version": {"reason": "unreported", "note": "The tables name the model without a release version"}}},
        method_types=mtypes, links=[{"relation": "configuration_of", "target_id": family}])
    models[key] = cfg
    return cfg


# Review correction C3: exact descriptions for the three Spearman protocols.
RHO_DESCRIPTIONS = {
    "Fluorescence": "Fluorescence regression, as distributed with TAPE. Scored by Spearman rank correlation on the task's test split.",
    "Stability": "Protein stability regression, as distributed with TAPE. Scored by Spearman rank correlation on the task's test split.",
    "β-lactamase": "Beta-lactamase activity regression, as distributed with PEER. Scored by Spearman rank correlation on the task's test split.",
}


def protocol(dkey, mcol):
    key = (dkey, mcol)
    if key in protos:
        return protos[key]
    mkey, concept, direction, unit, unit_detail, note = METRICS[mcol]
    name, desc, areas = DATASETS[dkey]
    attrs = {"protocol": f"Train on the task's training split and score {name} on its test split; five random seeds per method, mean and standard deviation reported.",
             "metric": concept, "metric_direction": direction, "unit": unit,
             "metric_qualifier": note,
             "version": "As published 2025",
             "source_locator": f"{name}: column '{mcol.strip()}' of its table in Tables 2 to 8",
             "replicates": SEEDS,
             "limitations": ["Author-reported results: the DeepProtein authors ran every method."]}
    if unit_detail:
        attrs["unit_detail"] = unit_detail
    if dkey in split_sizes:
        attrs["dataset"] = f"{name}; train/valid/test {split_sizes[dkey]}"
    rec = {"id": b.rid("protocol", dkey, mkey), "kind": "protocol",
           "name": f"DeepProtein {name}: {mcol.strip()}",
           "description": RHO_DESCRIPTIONS.get(dkey) if mkey == "rho" else f"{desc} Scored by {note}.", "status": "needs_review",
           "facets": {"areas": areas or b.areas, "contexts": b.contexts},
           "source_ids": SIDS,
           "links": [{"relation": "part_of", "target_id": BENCH}, {"relation": "uses_data", "target_id": dataset(dkey)}],
           "attributes": attrs}
    protos[key] = b.add(rec)
    return protos[key]


n_results, skipped = 0, 0
for table, (topic, columns) in TABLES.items():
    cap, grid = grids[table]
    assert grid[0][0] == "Model", grid[0]
    headers = [(g, m) for g, m in zip(grid[0][1:], grid[1][1:])]
    assert headers == columns, (table, headers)
    size_row = grid[2]
    assert size_row[0].startswith("#") or size_row[0].startswith("No."), size_row
    for (dkey, _m), cell in zip(columns, size_row[1:]):
        if cell.strip():
            split_sizes.setdefault(dkey, cell.strip())
    for row in grid[3:]:
        label = row[0].strip()
        if not label and not any(c.strip() for c in row[1:]):
            continue  # blank separator row between model groups
        assert label in MODELS, (table, label)
        cfg = model_cfg(label)
        for (dkey, mcol), cell in zip(columns, row[1:]):
            cell = cell.strip()
            if cell == "/":
                skipped += 1
                continue
            assert cell, (table, label, dkey, mcol)
            proto = protocol(dkey, mcol)
            mkey = METRICS[mcol][0]
            ev_id = b.rid("eval", dkey, mkey, MODELS[label][0])
            locator = f"{table} row '{label}', column group '{dkey}', column '{mcol.strip()}'"
            if ev_id not in b.ids:
                b.evaluation(ev_id, f"{label} on DeepProtein {DATASETS[dkey][0]} ({mcol.strip()})", SIDS,
                    cfg, proto, dataset(dkey), "author_reported",
                    {"protocol_id": proto, "dataset_version": None,
                     "split": split_sizes.get(dkey, "As distributed by the original benchmark"),
                     "population": f"train/valid/test {split_sizes[dkey]}" if dkey in split_sizes else None,
                     "inputs": "Amino-acid sequence (graph models also take the protein graph)",
                     "adaptation": "Trained on the task's training split with the DeepProtein default configuration",
                     "metric_implementation": METRICS[mcol][5],
                     "aggregation": "Mean over five random seeds", "budget": None},
                    locator, extra={"n_runs": 5, "seeds": SEEDS})
            unc, numeric, missing = None, None, None
            m = CELL.match(cell.replace("−", "-"))
            if cell in UNRUN:
                reason, note = UNRUN[cell]
                missing = {"reason": reason, "note": note}
            else:
                assert m, (table, label, dkey, mcol, cell)
                numeric = m.group(1)
                if m.group(2):
                    unc = sd(m.group(2), cell, n=5, scope=SEEDS)
            b.result(b.rid("result", dkey, mkey, MODELS[label][0]),
                f"{label} {DATASETS[dkey][0]} {mcol.strip()}", SRC, SIDS, ev_id, cell,
                METRICS[mcol][1], METRICS[mcol][2], METRICS[mcol][3], locator, REV(locator),
                qualifier=METRICS[mcol][5], unit_detail=METRICS[mcol][4], uncertainty=unc, numeric=numeric,
                value_missing=missing,
                extra={"printed_value_basis": "Mean plus or minus standard deviation over five random seeds as printed"
                       if unc else "Value as printed"} | ({"limitations": ["The printed cell carries the article's '**' mark for a statistically better result than all other methods."]} if cell.endswith("**") else {}))
            n_results += 1

# Table 8: resource usage, one row per dataset and model.
cap, grid = grids["Table 8."]
assert grid[0] == ["Dataset", "Model", "Time (hour)", "GPU Memory (GB)"], grid[0]
for row in grid[1:]:
    dname, label = row[0].strip(), row[1].strip()
    dkey = TABLE8_DATASETS[dname]
    assert label in MODELS, label
    cfg = model_cfg(label)
    for mcol, cell in zip(("Time (hour)", "GPU Memory (GB)"), row[2:]):
        cell = cell.strip()
        assert cell, (dname, label, mcol)
        proto = protocol(dkey, mcol)
        mkey = METRICS[mcol][0]
        ev_id = b.rid("eval", dkey, mkey, MODELS[label][0])
        locator = f"Table 8 row '{dname}' / '{label}', column '{mcol}'"
        if ev_id not in b.ids:
            b.evaluation(ev_id, f"{label} resource usage on DeepProtein {DATASETS[dkey][0]} ({mcol})", SIDS,
                cfg, proto, dataset(dkey), "author_reported",
                {"protocol_id": proto, "dataset_version": None,
                 "split": split_sizes.get(dkey, "As distributed by the original benchmark"),
                 "population": f"train/valid/test {split_sizes[dkey]}" if dkey in split_sizes else None,
                 "inputs": "Amino-acid sequence (graph models also take the protein graph)",
                 "adaptation": "Trained on the task's training split with the DeepProtein default configuration",
                 "metric_implementation": METRICS[mcol][5],
                 "aggregation": "Single reported figure per dataset and model", "budget": None},
                locator, extra={"limitations": ["Table 8 does not say which hardware or how many runs the figure covers."]})
        b.result(b.rid("result", dkey, mkey, MODELS[label][0]), f"{label} {DATASETS[dkey][0]} {mcol}", SRC, SIDS, ev_id,
            cell, METRICS[mcol][1], METRICS[mcol][2], METRICS[mcol][3], locator, REV(locator),
            qualifier=METRICS[mcol][5], unit_detail=METRICS[mcol][4],
            extra={"printed_value_basis": "Value as printed in Table 8"})
        n_results += 1


# Relevance judgement for the protein-stability use case (status needs_review; the assessed_by
# link on the use_case record is proposed in use-case-links.json, not applied here).
UC = "use-case-protein-stability"
links = []
proto = b.rid("protocol", "Stability", "rho")
claim_id = f"use-case-mapping-{PREFIX}-stability-rho"
b.claim(claim_id,
    "Relevance of DeepProtein Stability (rho) to \"Assess methods for protein stability experiments\"",
    "Correlation of predicted with measured stability on the TAPE stability split, for protein language models and conventional sequence and graph baselines.",
    UC, SIDS,
    {"field": f"links:assessed_by:{proto}", "value": proto, "relevance": "proxy",
     "endpoint": "Rank correlation between predicted and measured stability on the TAPE stability test split (53571/2512/12851 train/valid/test), mean over five seeds",
     "rationale": "Proxy, not direct: the use case needs per-method correlation and error on held-out or dissimilar proteins with a stated construct and endpoint, and this protocol gives correlation on one supervised split of designed mini-protein stability measurements. It says nothing about antisymmetry on reverse variants, about transfer to larger proteins, or about ddG in kcal/mol.",
     "constraints": ["Supervised split: every model is trained on the task's training set, so these values are not comparable with zero-shot stability rankings.",
                     "Spearman rank correlation on one supervised split; not comparable with zero-shot stability rankings or with ddG values in kcal/mol.",
                     "Compare only within this protocol and this split.",
                     "Inspect every linked evaluation's source locator before citing a result."],
     "limitations": ["Author-reported: the DeepProtein authors ran every baseline and also introduce DeepProt-T5, which tops several tasks.",
                     "Graphormer ran out of memory on this task, so its cell is recorded with a missing value reason rather than a score.",
                     "One dataset and one split; no held-out-protein or homology-split stability evaluation.",
                     "The TAPE stability truth set is proteolysis-derived stability of designed mini-proteins, so it is biased towards small designed domains and away from the larger natural proteins the use case asks about."],
     "citation_locators": [{"source_id": SRC, "locator": "Table 2, column group 'Stability', column 'rho'"}],
     "source_locator": "Table 2, column group 'Stability', column 'rho'",
     "headline_metric": "spearman-correlation",
     "reviewed_evaluations": sorted(r["id"] for r in b.records if r["id"].startswith(f"{PREFIX}-eval-stability-rho-"))},
    source_id=SRC)
links.append({"use_case": UC, "relation": "assessed_by", "target_id": proto, "judgement_claim": claim_id})

assert len([r for r in b.records if r["id"].startswith(f"{PREFIX}-eval-stability-rho-")]) == 17
finalise(b, "reviewer-ps-1",
         "Reviewer re-retrieved the Europe PMC JATS XML and matched its SHA-256; an independent JATS table-grid parse compared all 436 results (printed and numeric values and spreads) with 0 mismatches; a hand sample of 49 values across Tables 2 to 8 matched.",
         SHA, URL, judgement_status=JUDGEMENT_STATUS,
         judgement_reason=None if JUDGEMENT_STATUS == "source_checked" else "Not shown: the source carries an evidence concern noting that Figure 3's caption calls the regression metric 'Spearman (Pearson) Coefficient' while the Evaluation metrics section defines it as Spearman. A source with evidence concerns withholds every judgement that cites it, so this judgement and the use-case summary edit that would describe it are held until the concern is cleared.")
counts = b.write({"use-case-links.json": json.dumps({
    "note": "Proposed assessed_by links to add to the use_case records after the judgement claims are reviewed. Not applied by the extractor.",
    "links": links}, indent=1) + "\n"})
print(counts, "results", n_results, "cells printed '/' and left out:", skipped)
