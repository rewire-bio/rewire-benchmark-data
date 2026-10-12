"""LiPP lipid-protein benchmark (Raza et al. 2026, J Chem Inf Model): Tables 2 and 3.

Usage: python3 -I extract_lipp.py <PMC13292216.xml> <batch-folder>
Extracts every printed success-rate cell of Tables 2 and 3 for the five docking and co-folding
tools, on the LiPP set, the LiPP test set and the two PoseBusters sets.
"""
import sys, os, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import Batch, extraction_review, sha256, finalise
from jats import tables

path, folder = sys.argv[1:3]
SHA = sha256(path)
assert SHA == "6ff34f2f709a14858a3753abf9f8f6efa1e7e3c351f15c70cf64264193a9414e", SHA
URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13292216/fullTextXML"
PREFIX = "lit-structure-20261011-lipp"

b = Batch(folder, PREFIX, ["protein-structure", "molecular-interactions"])
# Review correction L1: the store already holds this artifact as evidence-expansion-p2-lipp-2026-6ff34f2f709a
# (same SHA-256), so the batch cites it and adds no source record. The limitations below are moved
# onto that record through `records change` (see apply_store_changes.py).
SRC = "evidence-expansion-p2-lipp-2026-6ff34f2f709a"
SOURCE_LIMITATIONS = [
    "Tables 2 and 3 only. The confidence-score analyses, the per-lipid-class breakdowns and the PoseBusters validity checks in the figures were not extracted.",
    "The PoseBusters v1 and v2 columns are values the authors took from other publications, not runs of their own; they are recorded as paper_compilation.",
    "Cells printed as '-' (not yet evaluated on that set) are left out: 4 cells in Table 2 and 9 in Table 3.",
]
SIDS = [SRC]

REV = lambda loc: extraction_review(
    ["deterministic-table-parse"],
    "Parsed the pinned Europe PMC JATS XML with extract_lipp.py (table-wrap grid with rowspan and colspan expanded); row and column labels asserted. " + loc,
    SHA, URL)

BENCH = b.entity("benchmark", b.rid("benchmark", "lipp"), "LiPP benchmark set",
    "Benchmark of lipid-protein complex structure prediction: 331 experimental lipid-protein complexes curated from BioDolphin v1.1, with a 36-complex test subset released after every tool's training cutoff.",
    SIDS, {"entity_level": "suite", "version": "LiPP as published 2026 (BioDolphin v1.1)",
           "task": "Predict the pose of a lipid bound to a protein",
           "scope_note": "Success is a lipid pose with all-atom RMSD below 2 Angstrom; a second criterion also requires the pose to be PoseBusters valid.",
           "source_locator": "Results and Discussion, 'LiPP Benchmark Set'; Tables 2 and 3",
           "limitations": ["Lipid poses only; the protein fold accuracy is assessed elsewhere in the paper."]})

DATASETS = {
    "LiPP (N = 331) % Success Rate": ("lipp-331", "LiPP benchmark set (331 lipid-protein complexes)",
        "The full LiPP set of 331 experimental lipid-protein complexes curated from BioDolphin v1.1.", "331", "Full LiPP set", "independent_paper"),
    "LiPP test set (N = 36) % Success Rate": ("lipp-test-36", "LiPP test set (36 complexes released after every tool's cutoff)",
        "The 36 LiPP complexes released after the training or calibration cutoff of every tool evaluated.", "36", "LiPP test set", "independent_paper"),
    "PoseBusters v1 (N = 428) % Success Rate": ("posebusters-v1-428", "PoseBusters v1 (428 protein-small molecule complexes)",
        "PoseBusters version 1, 428 protein-small molecule complexes; success rates taken from the literature by the LiPP authors.", "428", "PoseBusters v1", "paper_compilation"),
    "PoseBusters v2 (N = 308) % Success Rate": ("posebusters-v2-308", "PoseBusters v2 (308 protein-small molecule complexes)",
        "PoseBusters version 2, 308 protein-small molecule complexes; success rates taken from the literature by the LiPP authors.", "308", "PoseBusters v2", "paper_compilation"),
}
# Table 3 prints the PoseBusters columns with slightly different spacing.
ALIASES = {"PoseBusters v1(N = 428) % Success Rate": "PoseBusters v1 (N = 428) % Success Rate"}

data_ids = {}
for col, (key, name, desc, n, pop, _origin) in DATASETS.items():
    data_ids[col] = b.entity("dataset", b.rid("data", key), name, desc, SIDS,
        {"population": f"{n} complexes ({pop})", "split": pop, "total": int(n),
         "source_locator": "Tables 2 and 3 column headings; Table 3 footnote a ('N denotes the total number of complexes in each dataset')" if "PoseBusters" in name else "Tables 2 and 3 column headings; table footnote a ('N denotes the total number of lipid-protein complexes in each dataset')",
         "missing_metadata": {"version": {"reason": "unreported", "note": "PoseBusters set versions are named v1 and v2 without a release identifier"}} if "PoseBusters" in name else {"version": {"reason": "unreported"}}})

TOOLS = {
    "AlphaFold 3": ("alphafold-3", "discovery-model-alphafold-3", "Trained on PDB structures with a training cutoff date 2021-09-30", ["foundation_model"], "co-folding"),
    "Chai-1": ("chai-1", "catalog-model-chai-1", "Trained on PDB structures with a training cutoff date of 2021-01-21", ["foundation_model"], "co-folding"),
    "RoseTTAFold AA": ("rosettafold-aa", None, "Trained on PDB structures with a training cutoff date of 2020-04-30", ["foundation_model"], "co-folding"),
    "DiffDock-L": ("diffdock-l", "catalog-model-diffdock-l", "Trained on complexes in PDBbind before 2019", ["specialist"], "AI-based docking"),
    "AutoDock Vina": ("autodock-vina", "catalog-model-vina", "Scoring function was weighted using PDBbind before 2019", ["conventional_pipeline"], "physics-based docking"),
}
RFAA = b.entity("model", b.rid("model", "rosettafold-aa"), "RoseTTAFold All-Atom",
    "All-atom co-folding model evaluated on the LiPP benchmark set.", SIDS,
    {"entity_level": "family", "reported_name": "RoseTTAFold AA",
     "training_data": "PDB structures with a training cutoff date of 2020-04-30 (Table 1)",
     "source_locator": "Table 1, row 'RoseTTAFold AA'",
     "missing_metadata": {"version": {"reason": "unreported", "note": "The paper names the tool without a release version"}}},
    method_types=["foundation_model"])
TOOLS["RoseTTAFold AA"] = ("rosettafold-aa", RFAA) + TOOLS["RoseTTAFold AA"][2:]

cfg = {}
for tool, (key, family, training, mtypes, kind) in TOOLS.items():
    cfg[tool] = b.entity("configuration", b.rid("config", key), f"{tool} (LiPP evaluation)",
        f"{tool} as run on the LiPP benchmark set by the LiPP authors.", SIDS,
        {"reported_name": tool, "method_role": kind, "training_setting": training,
         "foundation_model_eligible": "foundation_model" in mtypes,
         "source_locator": f"Table 1, row '{tool}'; Tables 2 and 3 row labels",
         "missing_metadata": {"version": {"reason": "unreported", "note": "Tool versions are not printed in Tables 1 to 3"}}},
        method_types=mtypes, links=[{"relation": "configuration_of", "target_id": family}])

CRITERIA = {
    "2": ("rmsd", "lipid pose all-atom RMSD below 2 Angstrom",
          "Success is a predicted lipid pose whose all-atom RMSD to the experimental pose is less than 2 Angstrom.",
          "ligand-rmsd-under-2a-rate"),
    "3": ("pb-valid", "RMSD below 2 Angstrom and PoseBusters valid",
          "Success requires both an all-atom lipid pose RMSD below 2 Angstrom and a PoseBusters-valid pose.",
          "success-rate"),
}

PB_TEXT = {
    "rmsd": "Success is a predicted small-molecule ligand pose with RMSD below 2 Angstrom to the experimental pose, as reported in the publication the LiPP authors cite. Pose selection and the RMSD atom set follow that publication and are not stated in this source.",
    "pb-valid": "Success is a predicted small-molecule ligand pose with RMSD below 2 Angstrom and a PoseBusters-valid pose to the experimental pose, as reported in the publication the LiPP authors cite. Pose selection and the RMSD atom set follow that publication and are not stated in this source.",
}

CI = re.compile(r"^†?\s*(-?[\d.]+)\s*\{([\d.]+)–([\d.]+)\}$")
PLAIN = re.compile(r"^†?\s*(-?[\d.]+)$")

grids = {lab.strip().rstrip("."): (cap, g) for lab, cap, g in tables(open(path, "rb").read())}
n_results = 0
for table_no, (ckey, cshort, cdesc, metric) in CRITERIA.items():
    cap, grid = grids[table_no]
    header = grid[0]
    assert header[0] == "Method", header
    cols = [ALIASES.get(h, h) for h in header[1:]]
    assert set(cols) == set(DATASETS), cols
    protos = {}
    for col in cols:
        key = DATASETS[col][0]
        if ckey == "pb-valid" and key == "posebusters-v1-428":
            continue  # review correction L4: every cell is a dash, so no protocol
        if "PoseBusters" in col:  # review correction L4: literature values on protein-small molecule sets
            pdesc = PB_TEXT[ckey]
            ptext = pdesc
        else:
            pdesc = cdesc
            ptext = cdesc + " One pose per complex as the tool ranks it; the paper gives no re-ranking step."
        protos[col] = b.entity("protocol", b.rid("protocol", ckey, key), f"LiPP Table {table_no}: {cshort}, {DATASETS[col][4]}",
            f"{pdesc} Evaluated on {DATASETS[col][4]}.", SIDS,
            {"protocol": ptext,
             "metric": metric, "metric_direction": "higher", "unit": "percent",
             "success_threshold": {"criterion": pdesc},
             "version": "LiPP as published 2026",
             "source_locator": f"Table {table_no}, column '{col}'",
             "limitations": (["The PoseBusters columns are literature values compiled by the LiPP authors, not their own runs."] if "PoseBusters" in col else []) +
                            ["Per-complex identifiers are in the supplementary data and were not extracted."]},
            links=[{"relation": "part_of", "target_id": BENCH}, {"relation": "uses_data", "target_id": data_ids[col]}])
    for row in grid[1:]:
        tool = row[0]
        assert tool in TOOLS, tool
        for col, cell in zip(cols, row[1:]):
            cell = cell.strip()
            if cell in ("-", "–", ""):
                continue
            dagger = cell.startswith("†")
            m = CI.match(cell) or PLAIN.match(cell)
            assert m, (table_no, tool, col, cell)
            value = m.group(1)
            unc = None
            if m.re is CI:
                unc = {"type": "confidence_interval", "printed": cell, "lower": m.group(2), "upper": m.group(3),
                       "level": 0.95, "method": "analytic",
                       "note": "Exact binomial interval (table footnote a: 'lower and upper bounds of the 95% confidence intervals calculated with exact binomial distribution')"}
            origin = DATASETS[col][5]
            key = DATASETS[col][0]
            ev = b.evaluation(b.rid("eval", ckey, key, tool), f"{tool} on {DATASETS[col][4]} ({cshort})", SIDS,
                cfg[tool], protos[col], data_ids[col], origin,
                {"protocol_id": protos[col], "dataset_version": None, "split": DATASETS[col][4],
                 "population": f"{DATASETS[col][3]} complexes", "inputs": "Protein sequence or structure and the bound lipid or small molecule",
                 "adaptation": "None; tools run as released", "metric_implementation": cshort,
                 "aggregation": "Share of complexes counted as successful", "budget": None},
                f"Table {table_no}, row '{tool}', column '{col}'",
                extra={"limitations": ["Value reported by the AlphaFold 3 authors, who used a training cutoff of 2019-09-30 (table footnote a, dagger)."] if dagger else
                                      (["Value compiled from the literature by the LiPP authors."] if origin == "paper_compilation" else [])} if (dagger or origin == "paper_compilation") else None)
            b.result(b.rid("result", ckey, key, tool), f"{tool} {DATASETS[col][4]} {cshort}", SRC, SIDS, ev,
                cell, metric, "higher", "percent",
                f"Table {table_no}, row '{tool}', column '{col}'", REV(f"Table {table_no}, row '{tool}', column '{col}'"),
                qualifier=(f"ligand pose RMSD below 2 Angstrom, as reported in the cited literature; {DATASETS[col][4]}" if ckey == "rmsd" and "PoseBusters" in col else f"{cshort}; {DATASETS[col][4]}"), uncertainty=unc, numeric=value,
                extra={"printed_value_basis": "Percentage as printed, with the 95% confidence interval in braces" if unc else "Percentage as printed"})
            n_results += 1


# Relevance judgements for the structural-hypotheses use case (status needs_review; the
# assessed_by links on the use_case record are proposed in use-case-links.json, not applied here).
UC = "use-case-structural-hypotheses-experiments"
links = []
for ckey, cshort, metric, order in (("rmsd", "lipid pose all-atom RMSD below 2 Angstrom", "ligand-rmsd-under-2a-rate", 1),
                                    ("pb-valid", "RMSD below 2 Angstrom and PoseBusters valid", "success-rate", 2)):
    proto = b.rid("protocol", ckey, "lipp-test-36")
    claim_id = f"use-case-mapping-{PREFIX}-{ckey}-lipp-test-36"
    b.claim(claim_id,
        f"Relevance of LiPP test set ({cshort}) to \"Choose structural hypotheses to guide experiments\"",
        "Lipid-protein pose accuracy on complexes released after every tool's training cutoff, as evidence for trusting a predicted ligand complex.",
        UC, SIDS,
        {"field": f"links:assessed_by:{proto}", "value": proto, "relevance": "proxy",
         "endpoint": f"Share of 36 post-cutoff lipid-protein complexes whose predicted lipid pose counts as a success ({cshort})",
         "rationale": "Proxy, not direct: the use case asks whether a predicted interface or complex is reliable enough to guide an experiment, and this protocol answers it for lipid ligands on complexes no tool could have memorised. It does not cover protein-protein interfaces, protein-peptide complexes or drug-like small molecules, and a correct pose does not establish that the interaction matters in the experiment being planned.",
         "constraints": ["Lipid ligands only; the LiPP authors note that drug-likeness filters exclude most lipids from PDBbind-derived sets.",
                         "Compare only within the same criterion and the same dataset column: the full LiPP set includes complexes inside some tools' training windows.",
                         "The 36-complex test set is small, so the printed 95% confidence intervals are wide.",
                         "Inspect every linked evaluation's source locator before citing a result."],
         "limitations": ["Author-run predictions, not an independent reproduction by Rewire.",
                         "The PoseBusters columns in the same tables are literature values compiled by the LiPP authors and are recorded as paper_compilation.",
                         "Pose accuracy only; the paper's confidence-score analysis is in figures and was not extracted.",
                         "Several printed test-set percentages are truncated rather than rounded (for example 11 of 36 printed as 30.5); the values are kept as printed.",
                         "The full LiPP set and the PoseBusters columns are not linked to the use case: the full set includes complexes inside some tools' training windows, and the PoseBusters values are literature compilations on drug-like ligands."],
         "citation_locators": [{"source_id": SRC, "locator": f"Table {'2' if ckey == 'rmsd' else '3'}, column 'LiPP test set (N = 36) % Success Rate'"}],
         "source_locator": f"Table {'2' if ckey == 'rmsd' else '3'}, column 'LiPP test set (N = 36) % Success Rate'",
         "headline_metric": metric,
         "comparison_group": "lipid-protein-poses", "comparison_title": "Lipid-protein pose predictions",
         "stratum_label": "Lipid poses on 36 post-cutoff complexes (LiPP)", "stratum_order": order,
         "reviewed_evaluations": [b.rid("eval", ckey, "lipp-test-36", t) for t in ("AlphaFold 3", "AutoDock Vina", "Chai-1", "DiffDock-L", "RoseTTAFold AA")]},
        source_id=SRC)
    links.append({"use_case": UC, "relation": "assessed_by", "target_id": proto, "judgement_claim": claim_id})

# Review correction L2: the two full-set cells already in the store as lit-041 and lit-042.
recs = {r["id"]: r for r in b.records}
for rid, old in ((f"{PREFIX}-result-rmsd-lipp-331-chai-1", "lit-041"), (f"{PREFIX}-result-rmsd-lipp-331-diffdock-l", "lit-042")):
    recs[rid]["links"].append({"relation": "supersedes", "target_id": old})
assert recs[f"{PREFIX}-result-rmsd-lipp-331-chai-1"]["attributes"]["numeric_value"] == "60.7"
assert recs[f"{PREFIX}-result-rmsd-lipp-331-diffdock-l"]["attributes"]["numeric_value"] == "46.8"
for c in [r for r in b.records if r["kind"] == "claim"]:
    for e in c["attributes"]["reviewed_evaluations"]:
        assert e in recs, e

finalise(b, "reviewer-ps-2",
         "Reviewer re-retrieved the Europe PMC JATS XML and matched its SHA-256; an independent table-grid parse matched all 27 results and all 22 confidence intervals; a hand sample of all 27 values against the rendered PMC HTML matched.",
         SHA, URL)
json.dump({"source_id": SRC, "limitations": SOURCE_LIMITATIONS}, open(os.path.join(folder, "extract", "source-limitations.json"), "w"), indent=1)
counts = b.write({"use-case-links.json": json.dumps({
    "note": "Proposed assessed_by links to add to the use_case records after the judgement claims are reviewed. Not applied by the extractor.",
    "links": links}, indent=1) + "\n"})
print(counts, "results", n_results)
