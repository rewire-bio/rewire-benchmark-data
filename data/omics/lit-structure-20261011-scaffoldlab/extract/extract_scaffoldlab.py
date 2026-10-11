"""Scaffold-Lab (Zheng et al. 2026, PLoS Computational Biology): Table 3, the ranking of protein
backbone generation methods for unconditional generation.

Usage: python3 -I extract_scaffoldlab.py <PMC13225634.xml> <batch-folder>
Every cell of Table 3 is extracted: designability, novelty, diversity, efficiency, the TOPSIS
relative closeness per length, its mean per method and the resulting rank.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import Batch, extraction_review, sha256, finalise
from jats import tables

path, folder = sys.argv[1:3]
SHA = sha256(path)
assert SHA == "9ff68ef80dc57d6ef85920d4d2104e86d071215ac9c74367a72b2a85669840d0", SHA
URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13225634/fullTextXML"
PREFIX = "lit-structure-20261011-scaffoldlab"

b = Batch(folder, PREFIX, ["protein-structure"])
SRC = b.source(f"{PREFIX}-source-zheng2026", "Scaffold-Lab: Critical evaluation and ranking of protein backbone generation methods in a unified framework", {
    "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC13225634/",
    "artifact_url": URL,
    "doi": "10.1371/journal.pcbi.1014290",
    "version": "Version of record, PLoS Computational Biology 2026 (PMC13225634 JATS full text)",
    "retrieved_at": "2026-10-11T21:30:00Z",
    "artifact_sha256": SHA,
    "publication_status": "peer_reviewed",
    "licence": "CC BY 4.0",
    "media_type": "application/xml",
    "venue": "PLoS Computational Biology",
    "year": 2026,
    "limitations": [
        "Table 3 only: the unconditional-generation summary. The motif-scaffolding results, the secondary-structure composition, the structural-validity checks and the dynamic-threshold analyses are figures and were not extracted.",
        "Table 3 prints no unit for the efficiency column; the text says it is the average time to generate each backbone and that current methods take several minutes, so the unit is recorded as unreported.",
        "The table prints group means without data preprocessing; the per-backbone values behind them are not published in the article.",
        "The acknowledgements thank Brian L. Trippe, an author of FrameDiff, for contributing to the Scaffold-Lab codebase; he is not an author of this paper.",
    ],
    "evidence_concerns": [{
        "source_id": f"{PREFIX}-source-zheng2026",
        "message": "Table 3 Designability column: equation (1) defines a per-backbone success over 100 backbones per length, which gives two-decimal fractions, but the column prints three-decimal group means; the aggregation behind the column is not stated, and the criterion is sc-TM above 0.5, not the 2 Angstrom sc-RMSD in the store's designability concept. Do not compare these values with other designability results.",
        "source_locator": "Table 3, column 'Designability(↑)'; Metrics, equation (1)",
        "artifact_sha256": SHA,
        "review_date": "2026-10-11",
    }]})
SIDS = [SRC]

REV = lambda loc: extraction_review(
    ["deterministic-table-parse"],
    "Parsed the pinned Europe PMC JATS XML with extract_scaffoldlab.py (table-wrap grid with rowspan and colspan expanded, type and method columns forward-filled); row and column labels asserted. " + loc,
    SHA, URL)

BENCH = b.entity("benchmark", b.rid("benchmark", "scaffold-lab"), "Scaffold-Lab unconditional generation",
    "Unified evaluation of protein backbone generation methods: 100 backbones per length group are refolded with ProteinMPNN and ESMFold and scored for designability, novelty, diversity and runtime.",
    SIDS, {"entity_level": "suite", "version": "As published 2026",
           "task": "Generate protein backbones unconditionally and evaluate them in a shared refolding pipeline",
           "scope_note": "Per group, 100 backbones with 10 ProteinMPNN sequences each are refolded; a backbone is designable if the refolded structure shares a TM-score above 0.5 with it. Short covers lengths 50 and 100, medium 200 to 500 and long 600 to 1000.",
           "source_locator": "Table 2 (length grouping), Table 3, and the Metrics section (designability, novelty, diversity, efficiency, ranking)",
           "limitations": ["Methods are evaluated only at the lengths the authors could run them at, so the groups hold different method sets."]})

DATA = b.entity("dataset", b.rid("data", "generated-backbones"), "Scaffold-Lab generated backbones (100 per length group)",
    "The backbones each method generated for evaluation: 100 per length, with 10 designed sequences per backbone.",
    SIDS, {"population": "100 generated backbones per method and length, each with 10 ProteinMPNN sequences",
           "split": "Generated de novo; no held-out split",
           "source_locator": "Results, 'The overall workflow of Scaffold-Lab': 'We generated 100 backbones with 10 sequences for each backbone to be evaluated.'",
           "missing_metadata": {"version": {"reason": "inapplicable", "note": "Backbones are generated per run rather than released as a fixed dataset"}}})

METHODS = {
    "Chroma": ("chroma", None, "Diffusion-based", "2023-11"),
    "FrameDiff": ("framediff", None, "Diffusion-based", "2023-03"),
    "FrameFlow": ("frameflow", None, "Flow-based", "2023-10"),
    "Genie": ("genie", None, "Diffusion-based", "2023-01"),
    "RFdiffusion": ("rfdiffusion", "discovery-model-rfdiffusion", "Diffusion-based", "2023-04"),
}
for name, (key, family, category, released) in list(METHODS.items()):
    if family is None:
        family = b.entity("model", b.rid("model", key), name,
            f"{category} protein backbone generation method evaluated in Scaffold-Lab (released {released}).", SIDS,
            {"entity_level": "family", "reported_name": name,
             "source_locator": f"Table 1, row '{name}'",
             "missing_metadata": {"version": {"reason": "unreported", "note": "Table 1 gives a release date and repository, not a version"}}},
            method_types=["specialist"])
        METHODS[name] = (key, family, category, released)

cfg = {}
for name, (key, family, category, released) in METHODS.items():
    cfg[name] = b.entity("configuration", b.rid("config", key), f"{name} (Scaffold-Lab unconditional generation)",
        f"{name} as run in the Scaffold-Lab unconditional generation benchmark, with ProteinMPNN sequence design and ESMFold refolding.",
        SIDS, {"reported_name": name, "reported_configuration": f"{category} method, released {released}; run inside the Scaffold-Lab pipeline on shared hardware",
               "source_locator": f"Table 1, row '{name}'; Table 3 row labels",
               "missing_metadata": {"version": {"reason": "unreported", "note": "Table 1 gives the repository and release date, not a version"}}},
        method_types=["specialist"], links=[{"relation": "configuration_of", "target_id": family}])

METRICS = {
    "Designability(↑)": ("designability", "designability", "higher", "fraction", None,
        "Table 3 'Designability' column, printed as a group mean without data preprocessing; the Metrics section counts a backbone as designable when the mean sc-TM of its top 3 ProteinMPNN sequences refolded with ESMFold exceeds 0.5 (equation 1); the table does not state whether the value is the share of designable backbones or a mean sc-TM; not comparable with the 2 Angstrom sc-RMSD criterion in the concept definition",
        "Share of generated backbones that are designable."),
    "Novelty(↓)": ("novelty", "tm-score", "lower", "unitless", None,
        "novelty as the pdb-TM of designable backbones against the PDB (lower is more novel); group mean without data preprocessing",
        "Structural similarity of the designable backbones to the closest known PDB structure."),
    "Diversity (↑)": ("diversity", "proportion", "higher", "fraction", "unique Foldseek clusters per generated backbone",
        "unique Foldseek-Cluster clusters divided by the number of backbones in the group, clustering TM-score threshold 0.5; group mean without data preprocessing",
        "Share of distinct structural clusters among the generated backbones."),
    "Efficiency (↓)": ("efficiency", "runtime", "lower", "unit-unreported", "average time to generate one backbone; Table 3 prints no unit",
        "average time taken to generate each backbone over 100 backbones per group, on identical hardware",
        "Average generation time per backbone."),
    "Ci": ("ci", "topsis-relative-closeness", "higher", "unitless", None,
        "TOPSIS relative closeness with CRITIC weights, per length",
        "TOPSIS relative closeness of the method at this length."),
    "Mean Ci": ("mean-ci", "topsis-relative-closeness", "higher", "unitless", None,
        "TOPSIS relative closeness with CRITIC weights, mean over the lengths in the group",
        "Mean TOPSIS relative closeness of the method within the length group."),
    "Rank": ("rank", "rank", "lower", "unitless", "ordinal position within the length group",
        "rank within the length group by mean TOPSIS relative closeness",
        "Rank of the method within the length group."),
}

grids = {lab.strip(): (cap, g) for lab, cap, g in tables(open(path, "rb").read())}
cap, grid = grids["Table 3"]
header = grid[0]
assert header[:3] == ["Type", "Method", "Length"], header
cols = header[3:]
assert list(cols) == list(METRICS), cols

protos = {}
for col in cols:
    key, metric, direction, unit, unit_detail, qualifier, desc = METRICS[col]
    protos[col] = b.entity("protocol", b.rid("protocol", key),
        f"Scaffold-Lab unconditional generation: {col.strip()}",
        f"{desc} Measured in the Scaffold-Lab unconditional generation pipeline: 100 backbones per length, 10 ProteinMPNN sequences each, refolded with ESMFold.",
        SIDS, {"protocol": "Per method and length, 100 backbones are generated, 10 sequences are designed for each with ProteinMPNN and refolded with ESMFold; the metrics are group means without data preprocessing. Ranking uses TOPSIS with CRITIC weighting.",
               "metric": metric, "metric_direction": direction, "unit": unit,
               "metric_qualifier": qualifier,
               "version": "As published 2026",
               "source_locator": f"Table 3, column '{col.strip()}'; Metrics section",
               "aggregation": "Mean within each length group without data preprocessing",
               "limitations": ["Group means only; the per-backbone values are not published in the article."] +
                              (["Table 3 prints no unit for this column."] if unit == "unit-unreported" else [])}
        | ({"unit_detail": unit_detail} if unit_detail else {}),
        links=[{"relation": "part_of", "target_id": BENCH}, {"relation": "uses_data", "target_id": DATA}])

n_results = 0
group = method = None
for row in grid[1:]:
    group = row[0].strip() or group
    method = row[1].strip() or method
    length = row[2].strip()
    assert group in ("Short", "Medium", "Long"), group
    assert method in METHODS, method
    assert length.isdigit(), length
    for col, cell in zip(cols, row[3:]):
        cell = cell.strip()
        assert cell, (group, method, length, col)
        key, metric, direction, unit, unit_detail, qualifier, desc = METRICS[col]
        per_length = key not in ("mean-ci", "rank")
        scope = f"length {length}" if per_length else f"{group} group"
        ev_id = b.rid("eval", key, METHODS[method][0], group, (length if per_length else ""))
        if ev_id not in b.ids:
            b.evaluation(ev_id, f"{method} {col.strip()} on Scaffold-Lab unconditional generation, {scope}", SIDS,
                cfg[method], protos[col], DATA, "independent_paper",
                {"protocol_id": protos[col], "dataset_version": None,
                 "split": f"{group} group, {'length ' + length if per_length else 'lengths ' + group.lower()}",
                 "population": "100 generated backbones per length",
                 "inputs": "Target backbone length only (unconditional generation)",
                 "adaptation": "None; methods run with their released weights inside the Scaffold-Lab pipeline",
                 "metric_implementation": qualifier,
                 "aggregation": "Mean within the length" if per_length else "Mean over the lengths in the group",
                 "budget": "100 backbones per length, 10 designed sequences per backbone"},
                f"Table 3, row '{group}' / '{method}'" + (f" / length {length}" if per_length else "") + f", column '{col.strip()}'")
        rid = b.rid("result", key, METHODS[method][0], group, (length if per_length else ""))
        if rid in b.ids:  # Mean Ci and Rank are printed once per method and repeat down the group's rows
            prior = next(r for r in b.records if r["id"] == rid)
            assert prior["attributes"]["printed_value"] == cell, (rid, cell, prior["attributes"]["printed_value"])
            continue
        b.result(rid,
            f"{method} {col.strip()}, {group} group, {scope}", SRC, SIDS, ev_id, cell, metric, direction, unit,
            f"Table 3, row '{group}' / '{method}'" + (f" / length {length}" if per_length else "") + f", column '{col.strip()}'",
            REV(f"Table 3, row '{group}' / '{method}'" + (f" / length {length}" if per_length else "") + f", column '{col.strip()}'"),
            qualifier=f"{qualifier}; {scope}", unit_detail=unit_detail,
            extra={"printed_value_basis": "Value as printed in Table 3",
                   "scope_note": f"Length group {group}; {'length ' + length if per_length else 'mean over the group'}"})
        n_results += 1

finalise(b, "reviewer-ps-2",
         "Reviewer re-retrieved the Europe PMC JATS XML and matched its SHA-256; an independent table-grid parse matched all 140 per-length cells and all 20 mean Ci and rank records (mean Ci recomputed for all 10 groups); a hand sample of 45 values against the rendered PMC HTML matched.",
         SHA, URL)
counts = b.write()
print(counts, "results", n_results)
