"""Mahtha et al. 2026 (NAR Genomics and Bioinformatics): AlphaFold2, AlphaFold3 and ESMFold on
1666 monomeric and 994 dimeric PDB structures released 2022-2024. Tables 1 and 2.

Usage: python3 -I extract_afesmfold.py <PMC12809598.xml> <batch-folder>
Every cell of Tables 1 and 2 is a count of predicted structures in a predictive class, broken
down by the column's subset (all, pLDDT >= 70, experimental method, template quality band).
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import Batch, extraction_review, sha256, finalise

# Review decisions pending the team lead (see review.md): KEEP_CONCERNS applies correction A2 as
# evidence concerns; JUDGEMENT_STATUS serves (source_checked) or holds (needs_review) the judgements.
KEEP_CONCERNS = os.environ.get("AF_KEEP_CONCERNS", "1") == "1"
JUDGEMENT_STATUS = os.environ.get("AF_JUDGEMENT_STATUS", "needs_review")
SHA_PIN = "aae321d05839186a7595987d05af6e95aec5ac32b93b35c5cf1126902fe798b8"
CONCERNS = [  # review correction A2, messages and locators verbatim
    ("Table 1, ESMFold rows, columns 'EM' and 'NMR'; Results paragraph 17; Discussion",
     "The ESMFold rows give 244 EM and 107 NMR monomers, while the AlphaFold2 and AlphaFold3 rows over the same 1666 targets give 161 and 190, and the text gives 160 and 190. The Discussion says ESMFold mispredicted 139 of 190 NMR monomers, against 56 incorrect and 9 special cases in the table. The EM and NMR cells of the ESMFold incorrect row appear transposed."),
    ("Table 1, 'Special cases' rows, columns 'XRD', 'EM', 'NMR'; Results paragraphs 24 and 27",
     "The text says all 11 AlphaFold2 and all 11 AlphaFold3 special cases are NMR structures; the table gives 1 XRD and 10 NMR for AlphaFold2, and 2 XRD, 1 EM and 8 NMR for AlphaFold3."),
    ("Table 2, AlphaFold3 'Acceptable quality' row, columns 'EM' and 'NMR'",
     "The row prints EM 3 and NMR 37, so AlphaFold3 totals 184 EM and 49 NMR against 218 and 15 for the other tools over the same 994 targets (text: 219 and 15). The two cells appear transposed."),
    ("Table 2, columns 'TQ 0', 'TQ 1–40', 'TQ > 40'; Results paragraph 38",
     "Template quality is a property of the target, yet the column totals differ by tool (TQ 0: 557, 319 and 391). For AlphaFold3 the text gives 414, 326 and 5 accurate and 153, 88 and 8 incorrect dimers by TQ band, against 228, 512 and 4, and 91, 158 and 0, in the table."),
    ("Tables 1 and 2, row totals",
     "Several rows do not sum to the 'No.' column: Table 1 AlphaFold2 and AlphaFold3 accurate (method columns 1068 and 1075), ESMFold domain movement (429); Table 2 AlphaFold2 incorrect (method 230), AlphaFold3 medium (TQ 305), ESMFold acceptable (TQ 122) and incorrect (method and TQ 584)."),
]
from jats import tables

path, folder = sys.argv[1:3]
SHA = sha256(path)
assert SHA == "aae321d05839186a7595987d05af6e95aec5ac32b93b35c5cf1126902fe798b8", SHA
URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12809598/fullTextXML"
PREFIX = "lit-structure-20261011-afesmfold"

b = Batch(folder, PREFIX, ["protein-structure", "proteins-complexes"])
SRC = b.source(f"{PREFIX}-source-mahtha2026", "Comparative evaluation of the prediction accuracy of AlphaFold and ESMFold for monomeric and dimeric proteins", {
    "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC12809598/",
    "artifact_url": URL,
    "doi": "10.1093/nargab/lqag002",
    "version": "Version of record, NAR Genomics and Bioinformatics 2026 (PMC12809598 JATS full text)",
    "retrieved_at": "2026-10-11T21:30:00Z",
    "artifact_sha256": SHA,
    "publication_status": "peer_reviewed",
    "licence": "CC BY-NC 4.0",
    "media_type": "application/xml",
    "venue": "NAR Genomics and Bioinformatics",
    "year": 2026,
    "limitations": [
        "Tables 1 and 2 only: counts of predicted structures per predictive class. The RMSD, LDDT, TM-score, pLDDT and DockQ distributions are figures and supplementary figures and were not extracted.",
        "The counts are class memberships, not a single accuracy figure; direction is recorded as unknown because a high count is good for the accurate classes and bad for the incorrect class.",
        "The ProModEv web portal the paper describes was not retrieved.",
    ]} | ({"evidence_concerns": [{"source_id": f"{PREFIX}-source-mahtha2026", "message": msg, "source_locator": loc,
                                  "artifact_sha256": SHA_PIN, "review_date": "2026-10-11"} for loc, msg in CONCERNS]} if KEEP_CONCERNS else {}))
SIDS = [SRC]

REV = lambda loc: extraction_review(
    ["deterministic-table-parse"],
    "Parsed the pinned Europe PMC JATS XML with extract_afesmfold.py (table-wrap grid with rowspan and colspan expanded, tool column forward-filled); row and column labels asserted. " + loc,
    SHA, URL)

BENCH = b.entity("benchmark", b.rid("benchmark", "promodev-2022-2024"),
    "AlphaFold and ESMFold benchmark on PDB structures released 2022 to 2024",
    "Independent benchmark of AlphaFold2, AlphaFold3 and ESMFold on non-redundant PDB entries released between 2022 and 2024 whose sequences have no close homologue among pre-2022 structures.",
    SIDS, {"entity_level": "suite", "version": "As published 2026",
           "task": "Predict monomeric and dimeric protein structures from sequence",
           "scope_note": "Targets are PDB entries from 2022 to 2024 with sequence identity below 40% or query coverage below 70% against structures released up to 31 December 2021; CD-HIT at 90% identity removed redundancy and chains shorter than 20 or longer than 2700 residues were excluded.",
           "source_locator": "Materials and methods, 'Collection of benchmarking datasets and structure selection criteria'; Tables 1 and 2",
           "limitations": ["Classification thresholds are the authors' own (RMSD and LDDT for monomers, DockQ for dimers)."]})

DATA = {
    "1": b.entity("dataset", b.rid("data", "monomers-1666"), "1666 non-redundant monomeric PDB structures (2022-2024)",
        "The 1666 monomeric target structures selected from PDB entries released between 2022 and 2024.", SIDS,
        {"population": "1666 monomeric protein structures", "split": "Held-out by release date (2022-2024) and homology filtering",
         "total": 1666, "source_locator": "Materials and methods: 'the final benchmarking set of 1666 monomeric and 994 dimeric structures'",
         "missing_metadata": {"version": {"reason": "unreported", "note": "No accession list version is printed; the per-target list is on the ProModEv portal"}}}),
    "2": b.entity("dataset", b.rid("data", "dimers-994"), "994 non-redundant dimeric PDB structures (2022-2024)",
        "The 994 dimeric target structures selected from PDB entries released between 2022 and 2024.", SIDS,
        {"population": "994 dimeric protein structures", "split": "Held-out by release date (2022-2024) and homology filtering",
         "total": 994, "source_locator": "Materials and methods: 'the final benchmarking set of 1666 monomeric and 994 dimeric structures'",
         "missing_metadata": {"version": {"reason": "unreported", "note": "No accession list version is printed; the per-target list is on the ProModEv portal"}}}),
}

TOOLS = {
    "AlphaFold2": ("alphafold2", None, "AlphaFold2 v2.2.3 installed locally; five models per sequence",
                   "Five structures per sequence were generated with AlphaFold2 (v2.2.3) on a local HPC cluster.", "v2.2.3"),
    "AlphaFold3": ("alphafold3", "discovery-model-alphafold-3", "AlphaFold3 accessed as a web service",
                   "AlphaFold3 was accessed as a web service for structure prediction.", None),
    "ESMFold": ("esmfold", "catalog-model-esmfold", "ESMFold installed locally from its GitHub repository",
                "ESMFold was installed locally following its repository instructions and run on a local HPC cluster.", "v1.0.3"),
}
AF2 = b.entity("model", b.rid("model", "alphafold2"), "AlphaFold 2",
    "Deep-learning protein structure prediction model evaluated in this comparison.", SIDS,
    {"entity_level": "family", "reported_name": "AlphaFold2",
     "source_locator": "Materials and methods, 'Tertiary structure predictions using AlphaFold and ESMFold'",
     "missing_metadata": {"version": {"reason": "inapplicable", "note": "Family record; the evaluated release is on the configuration"}}},
    method_types=["foundation_model"])
TOOLS["AlphaFold2"] = (TOOLS["AlphaFold2"][0], AF2) + TOOLS["AlphaFold2"][2:]

cfg = {}
for tool, (key, family, short, detail, version) in TOOLS.items():
    attrs = {"reported_name": tool, "reported_configuration": detail,
             "foundation_model_eligible": True,
             "source_locator": "Materials and methods, 'Tertiary structure predictions using AlphaFold and ESMFold'; Tables 1 and 2 row labels"}
    if version:
        attrs["version"] = version
    else:
        attrs["missing_metadata"] = {"version": {"reason": "unreported", "note": "The paper names the tool without a release version"}}
    cfg[tool] = b.entity("configuration", b.rid("config", key), f"{tool} ({short})", detail, SIDS, attrs,
                         method_types=["foundation_model"],
                         links=[{"relation": "configuration_of", "target_id": family}])

# Review correction A1: DockQ bands from the Table 2 footnote and Methods paragraph 14.
DIMER_CLASS_NOTES = {
    "High quality": "DockQ >= 0.80",
    "Medium quality": "0.49 <= DockQ < 0.80",
    "Acceptable quality": "0.23 <= DockQ < 0.49",
    "Incorrect prediction": "DockQ < 0.23",
}
CLASS_NOTES = {
    "Accurate prediction": "RMSD <= 3.0 Angstrom and LDDT >= 0.7",
    "Domain movement": "RMSD > 3.0 Angstrom and LDDT >= 0.7 (correct folds, different domain arrangement)",
    "Incorrect prediction": "RMSD > 3.0 Angstrom and LDDT < 0.7",
    "Special cases": "LDDT < 0.7 and RMSD < 3.0 Angstrom",
    "High quality": "DockQ band for high-quality interfaces, as the paper defines it",
    "Medium quality": "DockQ band for medium-quality interfaces, as the paper defines it",
    "Acceptable quality": "DockQ band for acceptable interfaces, as the paper defines it",
}
COLUMN_NOTES = {
    "No.": "all structures in the class",
    "pLDDT ≥ 70": "structures in the class whose pLDDT is at least 70",
    "XRD": "structures in the class whose experimental reference is X-ray diffraction",
    "EM": "structures in the class whose experimental reference is electron microscopy",
    "NMR": "structures in the class whose experimental reference is NMR",
    "Homodimer": "homodimeric structures in the class",
    "Heterodimer": "heterodimeric structures in the class",
    "TQ 0": "structures in the class with template quality 0 (no homologous pre-2022 structure)",
    "TQ 1–40": "structures in the class with template quality between 1 and 40",
    "TQ > 40": "structures in the class with template quality above 40",
}
PROTO_TEXT = {
    "1": ("Monomer predictions were compared with the experimental structure by RMSD and LDDT and assigned to one of four predictive classes: accurate prediction (RMSD <= 3.0 Angstrom and LDDT >= 0.7), correct with domain movement (RMSD > 3.0 Angstrom and LDDT >= 0.7), incorrect prediction (RMSD > 3.0 Angstrom and LDDT < 0.7) and special cases (LDDT < 0.7 and RMSD < 3.0 Angstrom).",
            "monomeric"),
    "2": ("Dimer predictions were scored with DockQ and assigned to high, medium or acceptable quality or incorrect prediction. Ligands were removed from the experimental files before scoring.",
            "dimeric"),
}

grids = {lab.strip().rstrip("."): (cap, g) for lab, cap, g in tables(open(path, "rb").read())}
n_results = 0
for table_no in ("1", "2"):
    cap, grid = grids[f"Table {table_no}"]
    header = grid[0]
    assert header[0] == "Tool" and header[1] == "Predictive class", header
    cols = header[2:]
    assert all(c in COLUMN_NOTES for c in cols), cols
    proto_text, kind = PROTO_TEXT[table_no]
    protos = {}
    for col in cols:
        protos[col] = b.entity("protocol", b.rid("protocol", table_no, col),
            f"Predictive-class counts for {kind} predictions, {COLUMN_NOTES[col]} (Table {table_no}, column '{col}')",
            f"{proto_text.replace('or incorrect prediction.', 'or incorrect prediction (high DockQ >= 0.80, medium 0.49 <= DockQ < 0.80, acceptable 0.23 <= DockQ < 0.49, incorrect DockQ < 0.23).') if table_no == '2' else proto_text} This protocol counts, for each class, {COLUMN_NOTES[col]}.", SIDS,
            {"protocol": proto_text, "metric": "count", "metric_direction": "unknown", "unit": "count",
             "unit_detail": "predicted structures",
             "metric_qualifier": COLUMN_NOTES[col],
             "version": "As published 2026",
             "source_locator": f"Table {table_no}, column '{col}'; Materials and methods (classification thresholds)",
             "limitations": ["Counts per class, not a single accuracy score.",
                             "Template quality is defined in the text as sequence identity multiplied by query coverage."]},
            links=[{"relation": "part_of", "target_id": BENCH}, {"relation": "uses_data", "target_id": DATA[table_no]}])
    tool = None
    rows = 0
    for row in grid[1:]:
        tool = row[0].strip() or tool
        assert tool in TOOLS, (tool, row)
        klass = row[1].strip()
        assert klass in CLASS_NOTES, klass
        rows += 1
        for col, cell in zip(cols, row[2:]):
            cell = cell.strip()
            assert cell.isdigit(), (table_no, tool, klass, col, cell)
            ev_id = b.rid("eval", table_no, TOOLS[tool][0], col)
            if ev_id not in b.ids:
                b.evaluation(ev_id, f"{tool} {kind} predictive-class counts, {COLUMN_NOTES[col]} (Table {table_no})", SIDS,
                    cfg[tool], protos[col], DATA[table_no], "independent_paper",
                    {"protocol_id": protos[col], "dataset_version": None,
                     "split": f"PDB {kind} structures released 2022-2024 without close pre-2022 homologues",
                     "population": "1666 monomers" if table_no == "1" else "994 dimers",
                     "inputs": "Amino-acid sequence only",
                     "adaptation": "None; tools run as released",
                     "metric_implementation": "Counts of predicted structures per predictive class",
                     "aggregation": COLUMN_NOTES[col], "budget": None},
                    f"Table {table_no}, rows for '{tool}', column '{col}'")
            b.result(b.rid("result", table_no, TOOLS[tool][0], col, klass),
                f"{tool} {kind} {klass}: {COLUMN_NOTES[col]}", SRC, SIDS, ev_id, cell, "count", "unknown", "count",
                f"Table {table_no}, row '{tool}' / '{klass}', column '{col}'",
                REV(f"Table {table_no}, row '{tool}' / '{klass}', column '{col}'"),
                qualifier=f"{klass} ({(DIMER_CLASS_NOTES if table_no == '2' else CLASS_NOTES)[klass]}); {COLUMN_NOTES[col]}",
                unit_detail="predicted structures",
                extra={"score_category": klass, "printed_value_basis": "Integer count as printed"})
            n_results += 1
    assert rows == (12 if table_no == "1" else 12), rows


# Relevance judgements for the structural-hypotheses use case (status needs_review; the
# assessed_by links on the use_case record are proposed in use-case-links.json, not applied here).
UC = "use-case-structural-hypotheses-experiments"
links = []
MONO_RATIONALE = "Proxy: the protocol counts how often each tool reproduces the deposited monomer within the authors' RMSD and LDDT thresholds on targets with no close pre-2022 homologue. That is structural accuracy against an experimental structure, which the use case treats as intermediate evidence; it does not test whether a prediction improved an experimental choice, and the use case's exclusions state that structural accuracy alone does not establish that an experiment will succeed."
DIMER_RATIONALE = "Proxy: the dimer classes are DockQ bands over homodimers and heterodimers together, so they bear on whether a predicted interface is worth testing but do not separate the antibody, peptide or ligand complex classes the use case treats separately."
COMMON_LIMITATIONS = ["Automated transcription of the printed counts; no independent reproduction of the predictions or the classification.",
                      "AlphaFold3 was run through its web service while AlphaFold2 and ESMFold were run locally, so compute settings differ between tools.",
                      "The per-target lists are on the authors' portal and were not retrieved.",
                      "The table's experimental-method and template-quality columns conflict with the text in places (see the source's evidence concerns); the linked 'No.' column agrees with the text."]
for table_no, kind in (("1", "monomeric"), ("2", "dimeric")):
    proto = b.rid("protocol", table_no, "No.")
    claim_id = f"use-case-mapping-{PREFIX}-{kind}"
    constraints = ["Counts, not rates: divide by 1666 (monomers) or 994 (dimers) before comparing tools.",
                   "The classification thresholds are the authors' own; compare only within this protocol."]
    if table_no == "1":
        constraints.append("NMR reference structures make up most AlphaFold2 and AlphaFold3 incorrect monomers (128 of 200 and 135 of 191); the ESMFold experimental-method cells conflict with the text, so do not filter ESMFold results by method.")
    constraints.append("Inspect every linked evaluation's source locator before citing a result.")
    limitations = list(COMMON_LIMITATIONS)
    if table_no == "1":
        limitations.append("AlphaFold2 and AlphaFold3 were scored on their top-ranked model (ranked_0); ESMFold gives one model.")
        group = ("monomer-structures", "Monomer structure predictions", "Predictive classes on 1666 post-2021 monomers (Mahtha et al. 2026)")
    else:
        limitations += ["For dimers, the AlphaFold2 and AlphaFold3 model scored is the best of five by DockQ against the experimental structure (Methods paragraph 14), a selection a user cannot make; ESMFold gives one model, so the comparison favours AlphaFold.",
                        "Dimers were kept when only one chain lacked a close pre-2022 homologue (Methods paragraph 6)."]
        group = ("protein-protein-interfaces", "Protein-protein interface predictions", "DockQ classes on 994 post-2021 dimers (Mahtha et al. 2026)")
    b.claim(claim_id,
        f"Relevance of {kind} predictive-class counts to \"Choose structural hypotheses to guide experiments\"",
        f"How often AlphaFold2, AlphaFold3 and ESMFold get {kind} structures right on targets released after their training data, as evidence for trusting a predicted structure.",
        UC, SIDS,
        {"field": f"links:assessed_by:{proto}", "value": proto, "relevance": "proxy",
         "endpoint": f"Number of {kind} targets each tool places in each predictive class, out of {'1666 monomers' if table_no == '1' else '994 dimers'}",
         "rationale": MONO_RATIONALE if table_no == "1" else DIMER_RATIONALE,
         "constraints": constraints,
         "limitations": limitations,
         "citation_locators": [{"source_id": SRC, "locator": f"Table {table_no}, column 'No.'"}],
         "source_locator": f"Table {table_no}, column 'No.'",
         "headline_metric": "count",
         "comparison_group": group[0], "comparison_title": group[1], "stratum_label": group[2],
         "reviewed_evaluations": [b.rid("eval", table_no, t, "No.") for t in ("alphafold2", "alphafold3", "esmfold")]},
        source_id=SRC)
    links.append({"use_case": UC, "relation": "assessed_by", "target_id": proto, "judgement_claim": claim_id})

ids = {r["id"] for r in b.records}
for c in [r for r in b.records if r["kind"] == "claim"]:
    assert all(e in ids for e in c["attributes"]["reviewed_evaluations"]), c["attributes"]["reviewed_evaluations"]
finalise(b, "reviewer-ps-2",
         "Reviewer re-retrieved the Europe PMC JATS XML and matched its SHA-256; an independent table-grid parse matched all 216 results; a hand sample of 48 values against the rendered PMC HTML matched; row and column totals cross-checked against the text.",
         SHA, URL, judgement_status=JUDGEMENT_STATUS,
         judgement_reason=None if JUDGEMENT_STATUS == "source_checked" else "Not shown: the source's experimental-method, template-quality and row-total cells conflict with its own text in places, recorded as evidence concerns on the source. This judgement uses only the 'No.' column, which agrees with the text, but a source with evidence concerns withholds every judgement that cites it until the concerns are resolved.")
counts = b.write({"use-case-links.json": json.dumps({
    "note": "Proposed assessed_by links to add to the use_case records after the judgement claims are reviewed. Not applied by the extractor.",
    "links": links}, indent=1) + "\n"})
print(counts, "results", n_results)
