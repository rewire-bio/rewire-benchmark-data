"""Deterministic extraction for the rare-disease candidate ranking use-case pass, 2026-10-09.

Usage: python3 -I extract_rare_ranking.py <download-dir> <batch-dir>

<download-dir> layout:
  PMC8921623/fulltext.xml, PMC8921623/supp.zip, PMC8921623/supp/sm_table_3_r1_bbac019.docx  (Yuan et al. 2022)
  PMC10838329/fulltext.xml                                                                   (Yuan et al. 2024)
  PMC12041562/fulltext.xml                                                                   (Kafkas et al. 2025)

Writes batch.jsonl and claims.csv. Extracts every cell of Yuan 2022 Supplementary Table 3,
Yuan 2024 Table 1 and Kafkas 2025 Table 3, with labels asserted.
"""
import csv, hashlib, json, os, re, sys, zipfile, xml.etree.ElementTree as ET
from collections import Counter

DL, OUT = sys.argv[1], sys.argv[2]
P = "rare-ranking-20261009"
UC = "use-case-rare-disease-candidate-ranking"
UC_NAME = "Rank rare-disease variants for review"
DATE = "2026-10-09"
EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest/"
FAC = {"areas": ["dna-genomes"], "contexts": ["clinical_research"]}
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def txt(e):
    return " ".join("".join(e.itertext()).split())


records, claims_rows = [], []


def rec(kind, id_, name, description, attributes, source_ids, links=(), facets=None):
    records.append({"id": id_, "kind": kind, "name": name, "description": description, "status": "needs_review",
                    "facets": facets if facets is not None else {}, "source_ids": list(source_ids),
                    "links": [dict(relation=a, target_id=b) for a, b in links], "attributes": attributes})
    return id_


art = {"y22": os.path.join(DL, "PMC8921623", "fulltext.xml"), "y22_s3": os.path.join(DL, "PMC8921623", "supp", "sm_table_3_r1_bbac019.docx"),
       "y22_zip": os.path.join(DL, "PMC8921623", "supp.zip"), "y24": os.path.join(DL, "PMC10838329", "fulltext.xml"),
       "kf": os.path.join(DL, "PMC12041562", "fulltext.xml")}
H = {k: sha(v) for k, v in art.items()}
S_Y22, S_Y22S, S_Y24, S_KF = f"{P}-source-yuan2022", f"{P}-source-yuan2022-sm-table-3", f"{P}-source-yuan2024", f"{P}-source-kafkas2025"
URL = {S_Y22: EPMC + "PMC8921623/fullTextXML", S_Y22S: EPMC + "PMC8921623/supplementaryFiles", S_Y24: EPMC + "PMC10838329/fullTextXML", S_KF: EPMC + "PMC12041562/fullTextXML"}
SHA = {S_Y22: H["y22"], S_Y22S: H["y22_s3"], S_Y24: H["y24"], S_KF: H["kf"]}


def source(sid, name, desc, a):
    rec("source", sid, name, desc, dict({"artifact_url": URL[sid], "artifact_sha256": SHA[sid], "publication_status": "peer_reviewed"}, **a), [], facets=FAC)


source(S_Y22, "Evaluation of phenotype-driven gene prioritization methods for Mendelian diseases", "Primary source retrieved and hashed for the rare-disease ranking pass.",
       {"url": "https://doi.org/10.1093/bib/bbac019", "doi": "10.1093/bib/bbac019", "retrieved_at": "2026-10-09T21:18:05Z",
        "version": "Briefings in Bioinformatics 23(2):bbac019, published 2022-02-04; PMC8921623 full-text XML", "licence": "CC-BY-NC-4.0", "media_type": "application/xml"})
source(S_Y22S, "Yuan et al. 2022, SM Table 3 (accuracy in each top level experiment)", "Supplementary table of top-k accuracy per method and dataset.",
       {"url": "https://doi.org/10.1093/bib/bbac019", "doi": "10.1093/bib/bbac019", "retrieved_at": "2026-10-09T21:18:19Z",
        "version": "sm_table_3_r1_bbac019.docx inside the Europe PMC supplementaryFiles zip for PMC8921623", "licence": "CC-BY-NC-4.0",
        "media_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "hash_scope": f"SHA-256 of the docx member (zip SHA-256 {H['y22_zip']}; assembled per request)."})
source(S_Y24, "Refined preferences of prioritizers improve intelligent diagnosis for Mendelian diseases", "Primary source retrieved and hashed for the rare-disease ranking pass.",
       {"url": "https://doi.org/10.1038/s41598-024-53461-x", "doi": "10.1038/s41598-024-53461-x", "retrieved_at": "2026-10-09T21:20:19Z",
        "version": "Scientific Reports 14:2845, published 2024-02-03; PMC10838329 full-text XML", "licence": "CC-BY-4.0", "media_type": "application/xml"})
source(S_KF, "The application of Large Language Models to the phenotype-based prioritization of causative genes in rare disease patients", "Primary source retrieved and hashed for the rare-disease ranking pass.",
       {"url": "https://doi.org/10.1038/s41598-025-99539-y", "doi": "10.1038/s41598-025-99539-y", "retrieved_at": "2026-10-09T21:20:27Z",
        "version": "Scientific Reports 15, published 2025-04-29; PMC12041562 full-text XML", "licence": "CC-BY-4.0", "media_type": "application/xml"})

# ---------------------------------------------------------------- methods and models
M = {"exomiser": "uc-clinical-20260930-method-exomiser"}
SML, CP, FM = "supervised_machine_learning", "conventional_pipeline", "foundation_model"


def method(key, name, desc, srcs, locator, mtype):
    M[key] = rec("method", f"{P}-method-{key}", name, desc,
                 {"reported_name": name, "entity_level": "method", "source_locator": locator,
                  "missing_metadata": {"version": {"reason": "inapplicable", "note": "Family record; versions are on configurations"}}},
                 srcs, facets=dict(FAC, method_types=[mtype]))


YL = "Yuan et al. 2022 Table 2"
method("phenix", "PhenIX", "Phenotype-driven exome prioritisation using human disease phenotypes.", [S_Y22, S_Y24], YL, CP)
method("deeppvp", "DeepPVP", "Deep learning phenotype-based variant prioritisation.", [S_Y22], YL, SML)
method("xrare", "Xrare", "Machine-learning variant and gene prioritisation.", [S_Y22], YL, SML)
method("amelie", "AMELIE", "Literature-mining gene prioritisation from phenotype and variants.", [S_Y22, S_Y24], YL, SML)
method("lirical", "LIRICAL", "Likelihood-ratio phenotype and genotype interpretation.", [S_Y22, S_Y24], YL, CP)
method("phenolyzer", "Phenolyzer", "Phenotype-only gene prioritisation.", [S_Y22], YL, SML)
method("hanrd", "HANRD", "Heterogeneous network and graph convolution gene prioritisation.", [S_Y22], YL, SML)
method("gado", "GADO", "Gene network prioritisation from transcriptome co-regulation.", [S_Y22], YL, SML)
method("phen2gene", "Phen2Gene", "Probabilistic phenotype-only gene prioritisation.", [S_Y22], YL, CP)
M["gpt4"] = rec("model", f"{P}-model-gpt-4", "GPT-4", "OpenAI general-purpose large language model, accessed through the API.",
                {"reported_name": "GPT-4", "entity_level": "checkpoint", "version": "gpt-4-1106-preview", "access": "Commercial API (OpenAI), per Kafkas et al. Methods",
                 "source_locator": "Kafkas et al. Introduction and Methods 'Large Language Models used'"}, [S_KF], facets=dict(FAC, method_types=[FM]))

# ---------------------------------------------------------------- configurations
C = {}


def config(key, name, of, srcs, mtype, version=None, vnote="Version not printed", params=None, locator=None, limitations=None):
    a = {"reported_name": name, "foundation_model_eligible": mtype == FM}
    if version:
        a["version"] = version
    else:
        a["missing_metadata"] = {"version": {"reason": "unreported", "note": vnote}}
    for k, v in (("parameters", params), ("source_locator", locator), ("limitations", limitations)):
        if v:
            a[k] = v
    C[key] = rec("configuration", f"{P}-config-{key}", name, f"{name} as evaluated in the cited comparison.", a, srcs,
                 links=[("configuration_of", of)], facets=dict(FAC, method_types=[mtype]))


Y22_ROWS = ["PhenIX", "Exomiser", "DeepPVP", "Xrare", "AMELIE", "LIRICAL", "Phenolyzer", "HANRD", "GADO", "Phen2Gene", "AMELIE-HPO"]
Y22_CFG = {"PhenIX": ("phenix", "1.16", "HPO + VCF", CP), "Exomiser": ("exomiser", "12.1.0", "HPO + VCF", CP), "DeepPVP": ("deeppvp", "2.1", "HPO + VCF", SML),
           "Xrare": ("xrare", "pub:2015 (as printed)", "HPO + VCF", SML), "AMELIE": ("amelie", "Oct 5, 2020 (as printed)", "HPO + VCF", SML),
           "LIRICAL": ("lirical", "1.3.0", "HPO + VCF", CP), "Phenolyzer": ("phenolyzer", "0.4.0", "HPO only", SML), "HANRD": ("hanrd", None, "HPO only", SML),
           "GADO": ("gado", "1.0.1", "HPO only", SML), "Phen2Gene": ("phen2gene", "1.2.3", "HPO only", CP), "AMELIE-HPO": ("amelie", "Oct 5, 2020 (as printed)", "HPO only", SML)}
for row, (mk, ver, inp, mt) in Y22_CFG.items():
    config(f"yuan2022-{row.lower()}", f"{row} default, singleton (Yuan et al. 2022)", M[mk], [S_Y22, S_Y22S], mt, version=ver,
           vnote="Table 2 prints a dash for the HANRD version", params=f"Default parameters; input {inp}; singleton proband analysis",
           locator=f"Table 2 row '{row if row != 'AMELIE-HPO' else 'AMELIE'}'; SM Table 3 row '{row}'")

Y24_PROT = {
    ("Exomiser", "A"): "Old default pathogenicity sources (PolyPhen, MutationTaster, SIFT); singleton",
    ("Exomiser", "B"): "REVEL and MVP pathogenicity sources; singleton",
    ("Exomiser", "C"): "Trio mode (parents' genotypes and disease status)",
    ("Exomiser", "D"): "Trio mode; chosen as optimal by the authors",
    ("PhenIX", "A"): "Old default pathogenicity sources; singleton", ("PhenIX", "B"): "REVEL and MVP pathogenicity sources; singleton",
    ("PhenIX", "C"): "Trio mode", ("PhenIX", "D"): "Trio mode; chosen as optimal by the authors",
    ("AMELIE", "A"): "Default (alfqCutoff 0.5%, filterByCount off)", ("AMELIE", "B"): "alfqCutoff 2.0%, filterByCount off; chosen as optimal by the authors",
    ("AMELIE", "C"): "filterByCount on, alfqCutoff 0.5%", ("AMELIE", "D"): "filterByCount on, alfqCutoff 2.0%",
    ("LIRICAL", "–"): "Few parameter options; no protocol variants"}
Y24_VER = {"Exomiser": "13.1.0", "PhenIX": "1.16", "AMELIE": "3.1.0", "LIRICAL": "1.3.4"}
Y24_MK = {"Exomiser": "exomiser", "PhenIX": "phenix", "AMELIE": "amelie", "LIRICAL": "lirical"}
FIG2 = "Protocol option tables are in Figure 2 (image, not read); descriptions are from the Results text, and the exact pathogenicity source in Protocols C and D is not stated in the text."
for (tool, prot), desc in Y24_PROT.items():
    key = f"yuan2024-{tool.lower()}" + (f"-protocol-{prot.lower()}" if prot != "–" else "")
    config(key, f"{tool} {Y24_VER[tool]}" + (f", Protocol {prot}" if prot != "–" else "") + " (Yuan et al. 2024)", M[Y24_MK[tool]], [S_Y24], CP if tool != "AMELIE" else SML,
           version=Y24_VER[tool], params=desc, locator=f"Table 1 rows '{tool}'" + (f", PROT '{prot}'" if prot != "–" else "") + "; Results 'Performance improvement assessment'",
           limitations=([FIG2] if tool in ("Exomiser", "PhenIX") else None))

KF_COLS = [("GP-Cards", "GPT-4", "Zero shot"), ("GP-Cards", "GPT-4", "One shot"), ("ClinVar", "GPT-4", "Zero shot"), ("ClinVar", "GPT-4", "One shot"),
           ("ClinVar", "Exomiser", None), ("PAVS", "GPT-4", "Zero shot"), ("PAVS", "GPT-4", "One shot"), ("PAVS", "Exomiser", None)]
config("kafkas2025-gpt-4-zero-shot", "GPT-4 (gpt-4-1106-preview), zero-shot prompt (Kafkas et al. 2025)", M["gpt4"], [S_KF], FM, version="gpt-4-1106-preview",
       params="Zero-shot gene-ranking prompt; the specific zero-shot prompt (Q1-Q3 or Q2Q3) used in Table 3 is not stated", locator="Table 1; Table 3; Methods 'Prompt engineering'")
config("kafkas2025-gpt-4-one-shot", "GPT-4 (gpt-4-1106-preview), one-shot chain-of-thought prompt Q4 (Kafkas et al. 2025)", M["gpt4"], [S_KF], FM, version="gpt-4-1106-preview",
       params="One-shot chain-of-thought prompt (Q4)", locator="Table 1; Table 3; Methods 'Prompt engineering'")
config("kafkas2025-exomiser-12-1-0", "Exomiser 12.1.0 'Exomiser score' gene ranking (Kafkas et al. 2025)", M["exomiser"], [S_KF], CP, version="12.1.0",
       params="Weighted combination of ExomeWalker, PHIVE and PhenIX gene scores; a random variant generated in each candidate gene; variant scores ignored; default settings",
       locator="Methods 'Baseline methods'")

# ---------------------------------------------------------------- datasets and protocols
D, PR = {}, {}
D["ddd"] = rec("dataset", f"{P}-data-ddd-305-solved", "DDD 305 solved probands (Yuan et al. selection)",
               "305 Deciphering Developmental Disorders probands with one 'definitely pathogenic' causal SNV or indel, HPO terms and exome VCF; parents' VCFs and disease status added in Yuan et al. 2024.",
               {"version": "EGAD00001001355 (VCF) and EGAD00001001413 (HPO), as selected by Yuan et al.", "patient_count": 305, "accession": "EGAD00001001355; EGAD00001001413",
                "population": "Neurodevelopmental disorders and congenital anomalies; mean 7.5 HPO terms and 100,033 variants per proband; 156 cases are in HGMD (published)",
                "split": "No split; whole set is the benchmark", "access": "Controlled access through the European Genome-phenome Archive",
                "source_locator": "Yuan 2022 Materials 'Datasets curation' and Results paragraph 1; Yuan 2024 Methods 'DDD and KGD trio dataset'"},
               [S_Y22, S_Y24], facets=FAC)
D["kmcgd"] = rec("dataset", f"{P}-data-kmcgd-209", "KingMed Changsha in-house cohort, 209 solved cases (Yuan et al. 2022)",
                 "In-house exome cohort with a wide range of syndromes, each with a single causal gene interpreted under ACMG/AMP.",
                 {"version": "As published", "patient_count": 209, "population": "209 solved patients, mixed phenotypic abnormalities", "split": "No split",
                  "access": "In-house; not public", "source_locator": "Results 'Overview of curated datasets'; Table 1"}, [S_Y22], facets=FAC)
D["kgd"] = rec("dataset", f"{P}-data-kgd-152-trios", "KingMed in-house trio cohort, 152 families (Yuan et al. 2024)",
               "Trio exomes: 58 probands kept from the earlier in-house cohort plus 94 added in 2021-2022, each with one causal gene under ACMG/AMP.",
               {"version": "As published", "patient_count": 152, "population": "152 three-member families; mean 3.1 HPO terms and 108,035 variants per proband", "split": "No split",
                "access": "In-house; not public", "source_locator": "Methods 'DDD and KGD trio dataset'; Results paragraph 1"}, [S_Y24], facets=FAC)
for key, name in (("gpcards", "GPCards gene-phenotype cases (free-text phenotypes)"), ("clinvar", "ClinVar variants added 2 July to 7 October 2023, 100 genes"),
                  ("pavs", "PAVS Saudi phenotype-associated variants, 500 genes")):
    D[key] = rec("dataset", f"{P}-data-kafkas2025-{key}", f"{name} (Kafkas et al. 2025)",
                 "Genotype-phenotype pairs combined with randomly chosen genes into candidate gene sets of 5 to 100 genes.",
                 {"version": "As published", "population": name + "; candidate sets built by adding random genes to the causative gene", "split": "No split",
                  "source_locator": "Methods 'Datasets used'"}, [S_KF], facets=FAC)

Y_LIM_COMMON = ["Ranking of the known causal gene in solved cases; does not establish pathogenicity or a diagnosis.",
                "Each case has a single causal gene; cases with no or several causal genes are not represented."]
Y22_LIM = Y_LIM_COMMON + ["Default parameters and singleton mode for every tool; versions from 2014 to 2020.",
                          "AMELIE draws on the literature, and 156 of 305 DDD cases are published (HGMD); the authors report an almost unchanged trend on the 149 unpublished cases.",
                          "Same group later optimised parameters (Yuan et al. 2024); the two studies use different tool versions."]
PR["y22_ddd"] = rec("protocol", f"{P}-protocol-yuan2022-ddd-singleton-default", "Causal-gene rank in 305 DDD exomes, default singleton runs (Yuan et al. 2022 SM Table 3)",
                    "Proportion of solved cases whose causal gene each tool ranks within the top k.",
                    {"protocol": "Run each tool with default parameters on proband HPO terms (and VCF where accepted); record the rank of the known causal gene; report the percentage of cases ranked top 1 and within top 5, 10, 20, 30, 40 and 50.",
                     "version": "SM Table 3 rows 'DDD'", "source_locator": "SM Table 3; Materials 'Performance evaluation'", "limitations": Y22_LIM},
                    [S_Y22, S_Y22S], links=[("uses_data", D["ddd"])], facets=FAC)
PR["y22_kmcgd"] = rec("protocol", f"{P}-protocol-yuan2022-kmcgd-singleton-default", "Causal-gene rank in 209 in-house exomes, default singleton runs (Yuan et al. 2022 SM Table 3)",
                      "Proportion of solved cases whose causal gene each tool ranks within the top k.",
                      {"protocol": "As for the DDD protocol, on the KMCGD in-house cohort.", "version": "SM Table 3 rows 'KMCGD'", "source_locator": "SM Table 3; Materials 'Performance evaluation'",
                       "limitations": Y22_LIM[:2] + ["Default parameters and singleton mode for every tool.", "In-house cohort from the authors' laboratory; not public."]},
                      [S_Y22, S_Y22S], links=[("uses_data", D["kmcgd"])], facets=FAC)
Y24_LIM = Y_LIM_COMMON + ["Rows mix singleton (Protocols A and B of Exomiser and PhenIX) and trio-mode (C and D) runs; compare within mode only.",
                          "Parameter protocols were optimised on the same cohorts, so the best protocol's values are in-sample.",
                          "Same authors as Yuan et al. 2022; none developed the tools compared."]
for key, dk, n, label in (("y24_ddd", "ddd", 305, "DDD"), ("y24_kgd", "kgd", 152, "KGD")):
    PR[key] = rec("protocol", f"{P}-protocol-yuan2024-{label.lower()}-parameter-protocols", f"Causal-gene rank in {n} {label} trio-family exomes across parameter protocols (Yuan et al. 2024 Table 1)",
                  "Proportion of solved cases whose causal gene each tool and parameter protocol ranks within the top k.",
                  {"protocol": "Run Exomiser and PhenIX under Protocols A-D (pathogenicity source and trio mode), AMELIE under Protocols A-D (allele-frequency cutoff and filterByCount) and LIRICAL once; record the rank of the causal gene; report the percentage of cases in the top 1 and within top 5, 10, 20, 30, 40 and 50.",
                   "version": f"Table 1 rows '{label}'", "source_locator": f"Table 1 rows '{label}'; Methods 'Visualization and statistical analysis'", "limitations": Y24_LIM},
                  [S_Y24], links=[("uses_data", D[dk])], facets=FAC)
KF_LIM = ["Synthetic candidate sets: the causative gene plus randomly chosen genes, not the filtered variant list of a real exome.",
          "ClinVar phenotypes are OMIM disease annotations from the HPO database, which Exomiser also uses, so the comparison may favour Exomiser (authors' note).",
          "Phenotypes are database annotations, not observed in a patient workup (PAVS is closer to clinical reports).",
          "Exomiser was given one random variant per gene and its variant scores were ignored; only gene scores were compared.",
          "Neither GPT-4 nor Exomiser was developed by the authors."]
for key, name in (("gpcards", "GPCards"), ("clinvar", "ClinVar"), ("pavs", "PAVS")):
    PR[f"kf_{key}"] = rec("protocol", f"{P}-protocol-kafkas2025-{key}-gene-sets", f"Ranking the causative gene within synthetic candidate sets of 5 to 100 genes, {name} (Kafkas et al. 2025 Table 3)",
                          "Position of the causative gene when a fixed candidate set is ranked from phenotypes.",
                          {"protocol": "For each genotype-phenotype pair, build candidate sets of 5, 25, 50, 75 or 100 genes containing the causative gene; rank with each method; report Hits@1, Hits@10, ROC AUC and AUPR per set size.",
                           "version": f"Table 3 column '{name}'", "source_locator": f"Table 3 column '{name}'; Methods 'Datasets used' and 'Baseline methods'",
                           "limitations": KF_LIM + (["No comparator: Exomiser is not applicable because phenotypes are free text (table footnote)."] if key == "gpcards" else [])},
                          [S_KF], links=[("uses_data", D[key])], facets=FAC)

# ---------------------------------------------------------------- evaluations and results
def evaluation(short, name, cfg, proto, data, srcs, origin, comparison, locator, limitations=None):
    a = {"origin": origin, "protocol": proto, "version": "Primary source as retrieved 2026-10-09", "comparison": dict(comparison, protocol_id=proto), "source_locator": locator}
    if limitations:
        a["limitations"] = limitations
    return rec("evaluation", f"{P}-eval-{short}", name, "Published comparison; transcribed, not reproduced.", a, srcs,
               links=[("system", cfg), ("assessment", proto), ("data", data)], facets=FAC)


def result(short, ev, srcs, src, metric, printed, qualifier, locator, how, unit):
    float(printed)
    a = {"metric": metric, "metric_direction": "higher", "unit": unit, "printed_value": printed, "numeric_value": printed, "source_locator": locator,
         "missing_metadata": {"uncertainty": {"reason": "unreported"}}, "metric_qualifier": qualifier,
         "review": {"method": ["deterministic-table-parse"], "reviewer": ["claude"], "reviewer_note": "Claude (Opus 5.5) extraction agent; not an independent review",
                    "date": DATE, "artifact_sha256": SHA[src], "retrieval_url": URL[src], "note": how + " Pending independent review."}}
    rid = f"{P}-result-{short}"
    rec("result", rid, f"{short} {metric}", "Reported measurement transcribed from the pinned source. Not independently reproduced.", a, srcs, links=[("evaluation", ev)])
    claims_rows.append([rid, src, locator, printed, "result"])


TOPK = [("TOP 1(%)", "top-1-accuracy", "top1"), ("TOP 5(%)", "top-5-accuracy", "top5"), ("TOP 10(%)", "top-10-accuracy", "top10"), ("TOP 20(%)", "top-20-accuracy", "top20"),
        ("TOP 30(%)", "top-30-accuracy", "top30"), ("TOP 40(%)", "top-40-accuracy", "top40"), ("TOP 50(%)", "top-50-accuracy", "top50")]
QK = "proportion of solved cases with the causal gene within the tool's top-ranked genes"

# Yuan 2022 SM Table 3 (docx)
body = ET.fromstring(zipfile.ZipFile(art["y22_s3"]).read("word/document.xml")).find(W + "body")
tbls = body.findall(W + "tbl")
assert len(tbls) == 1
paras = ["".join(t.text or "" for t in p.iter(W + "t")) for p in body.findall(W + "p")]
assert "SM Table 3 Accuracy in each top level experiments of each method" in paras
rows = [[" ".join("".join(t.text or "" for t in p.iter(W + "t")) for p in tc.iter(W + "p")).strip() for tc in tr.findall(W + "tc")] for tr in tbls[0].iter(W + "tr")]
assert rows[0] == ["", "Method"] + [h for h, _, _ in TOPK]
assert [r[1] for r in rows[1:]] == Y22_ROWS * 2 and rows[1][0] == "DDD" and rows[12][0] == "KMCGD"
HOW_D = "Deterministic parse of the pinned docx table XML (extract/extract_rare_ranking.py) with the caption paragraph, header row, dataset labels and method labels asserted."
for i, r in enumerate(rows[1:]):
    cohort = "ddd" if i < 11 else "kmcgd"
    tool = r[1]
    ev = evaluation(f"yuan2022-{cohort}-{tool.lower()}", f"{tool} default singleton on {'DDD 305' if cohort == 'ddd' else 'KMCGD 209'}", C[f"yuan2022-{tool.lower()}"],
                    PR[f"y22_{cohort}"], D[cohort], [S_Y22, S_Y22S], "independent_paper",
                    {"dataset_version": "As selected by Yuan et al.", "split": "No split", "population": "305 solved DDD probands" if cohort == "ddd" else "209 solved in-house cases",
                     "inputs": f"Proband HPO terms{' and exome VCF' if Y22_CFG[tool][2] == 'HPO + VCF' else ' only'}; singleton", "adaptation": "Default parameters",
                     "metric_implementation": "Rank of the causal gene per case", "aggregation": "Percentage of cases", "budget": "Top 1 to top 50 genes"},
                    f"SM Table 3 rows '{cohort.upper()}', method '{tool}'")
    for j, (h, metric, short) in enumerate(TOPK):
        result(f"yuan2022-{cohort}-{tool.lower()}-{short}", ev, [S_Y22, S_Y22S], S_Y22S, metric, r[2 + j], QK, f"SM Table 3 row {i + 1} ({cohort.upper()}, {tool}), column '{h}'", HOW_D, "percent")

# Yuan 2024 Table 1
t = ET.parse(art["y24"]).getroot()
tw = [x for x in t.iter("table-wrap") if x.get("id") == "Tab1"][0]
assert txt(tw.find("caption")) == "Sensitivity of each prioritizer under different protocols in each top-level experiment."
trs = list(tw.iter("tr"))
assert [txt(c) for c in trs[0]] == ["", "Prioritizer", "PROT", "Top1 (%)", "Top5 (%)", "Top10 (%)", "Top20 (%)", "Top30 (%)", "Top40 (%)", "Top50 (%)"]
cohort = tool = None
seen = []
HOW_T = "Deterministic parse of the pinned article XML table (extract/extract_rare_ranking.py) with caption, column headers, cohort, prioritizer and protocol labels asserted; row-spanning cells resolved by position."
for r in trs[1:]:
    cells = [txt(c) for c in r]
    if len(cells) == 10:
        cohort, tool, cells = cells[0], cells[1], cells[2:]
    elif len(cells) == 9:
        tool, cells = cells[0], cells[1:]
    assert len(cells) == 8
    prot = cells[0]
    seen.append((cohort, tool, prot))
    key = f"yuan2024-{tool.lower()}" + (f"-protocol-{prot.lower()}" if prot != "–" else "")
    ck = "ddd" if cohort == "DDD" else "kgd"
    trio = tool in ("Exomiser", "PhenIX") and prot in ("C", "D")
    ev = evaluation(f"yuan2024-{ck}-{key.split('yuan2024-')[1]}", f"{tool}" + (f" Protocol {prot}" if prot != "–" else "") + f" on {cohort}", C[key], PR[f"y24_{ck}"], D[ck], [S_Y24],
                    "independent_paper",
                    {"dataset_version": "As published", "split": "No split", "population": "305 DDD trios" if ck == "ddd" else "152 KGD trios",
                     "inputs": "Proband HPO terms and exome VCF" + ("; parents' genotypes and disease status (trio mode)" if trio else "; trio mode not stated for this row" if tool in ("AMELIE", "LIRICAL") else "; singleton"),
                     "adaptation": Y24_PROT[(tool, prot)], "metric_implementation": "Rank of the causal gene per case", "aggregation": "Percentage of cases", "budget": "Top 1 to top 50 genes"},
                    f"Table 1 rows '{cohort}', '{tool}', PROT " + (f"'{prot}'" if prot != "–" else "printed as a dash"))
    for j, (h, metric, short) in enumerate(TOPK):
        result(f"yuan2024-{ck}-{key.split('yuan2024-')[1]}-{short}", ev, [S_Y24], S_Y24, metric, cells[1 + j], QK,
               f"Table 1 row ({cohort}, {tool}, PROT {prot if prot != '–' else 'printed as a dash'}), column '{h.replace('TOP ', 'Top').replace('(%)', ' (%)')}'", HOW_T, "percent")
EXP = [(c, t_, p) for c in ("DDD", "KGD") for t_, ps in (("Exomiser", "ABCD"), ("PhenIX", "ABCD"), ("AMELIE", "ABCD"), ("LIRICAL", "–")) for p in ps]
assert seen == EXP, seen

# Kafkas Table 3
t = ET.parse(art["kf"]).getroot()
tw = [x for x in t.iter("table-wrap") if x.get("id") == "Tab3"][0]
assert txt(tw.find("caption")) == "Performance comparison across different Gene Set Sizes and Cohorts."
trs = list(tw.iter("tr"))
assert [txt(c) for c in trs[0]] == ["Size", "Metric", "GP-Cards", "ClinVar", "PAVS"]
assert [txt(c) for c in trs[1]] == ["GPT-4", "GPT-4", "Exomiser", "GPT-4", "Exomiser"]
assert [txt(c) for c in trs[2]] == ["Zero shot", "One shot"] * 3
KM = {"Hits@1 (%)": ("top-1-accuracy", "percent", "hits1"), "Hits@10 (%)": ("top-10-accuracy", "percent", "hits10"), "ROC AUC": ("auroc", "fraction", "auroc"), "AUPR": ("auprc", "fraction", "auprc")}
KF_EV = {}
size = None
seen = []
for r in trs[3:]:
    cells = [txt(c) for c in r]
    if len(cells) == 10:
        size, cells = cells[0], cells[1:]
    metric_label, vals = cells[0], cells[1:]
    assert metric_label in KM and len(vals) == 8, cells
    seen.append((size, metric_label))
    metric, unit, ms = KM[metric_label]
    for (ds, model, shot), v in zip(KF_COLS, vals):
        cfg = "kafkas2025-exomiser-12-1-0" if model == "Exomiser" else f"kafkas2025-gpt-4-{'zero' if shot == 'Zero shot' else 'one'}-shot"
        dk = {"GP-Cards": "gpcards", "ClinVar": "clinvar", "PAVS": "pavs"}[ds]
        if (dk, cfg) not in KF_EV:
            KF_EV[(dk, cfg)] = evaluation(f"kafkas2025-{dk}-{cfg.split('kafkas2025-')[1]}", f"{model}{' ' + shot if shot else ''} on {ds} candidate gene sets", C[cfg], PR[f"kf_{dk}"], D[dk], [S_KF],
                                          "independent_paper",
                                          {"dataset_version": "As published", "split": "No split", "population": f"{ds} genotype-phenotype pairs",
                                           "inputs": "Free-text phenotypes" if dk == "gpcards" else "HPO-coded phenotypes and a candidate gene list", "adaptation": shot or "Default settings",
                                           "metric_implementation": "Hits@k, ROC AUC and AUPR over candidate sets", "aggregation": "Per candidate-set size", "budget": "Candidate sets of 5, 25, 50, 75 and 100 genes"},
                                          f"Table 3 column '{ds}', '{model}'" + (f" '{shot}'" if shot else ""))
        result(f"kafkas2025-{dk}-{cfg.split('kafkas2025-')[1]}-size{size}-{ms}", KF_EV[(dk, cfg)], [S_KF], S_KF, metric, v,
               f"candidate gene set of {size} genes including the causative gene",
               f"Table 3 row Size {size}, '{metric_label}', column '{ds}' '{model}'" + (f" '{shot}'" if shot else ""), HOW_T.replace("cohort, prioritizer and protocol", "size, metric and column"), unit)
assert seen == [(s, m) for s in ("5", "25", "50", "75", "100") for m in KM]

# ---------------------------------------------------------------- descriptive claims
def claim(short, subject, field, value, srcs, src, locator):
    cid = f"{P}-claim-{short}"
    rec("claim", cid, f"{field}: {subject}", "Descriptive fact transcribed from the pinned source.",
        {"field": field, "value": value, "source_locator": locator,
         "review": {"method": ["transcription"], "reviewer": ["claude"], "reviewer_note": "Claude (Opus 5.5) extraction agent; not an independent review",
                    "date": DATE, "artifact_sha256": SHA[src], "retrieval_url": URL[src], "note": "Hand transcription from the article text. Pending independent review."}},
        srcs, links=[("subject", subject)])
    claims_rows.append([cid, src, locator, value, "claim"])


claim("yuan2022-amelie-published-cases", PR["y22_ddd"], "selection_bias",
      "AMELIE tends to have an upper hand in identifying targets for published cases (DDD dataset); after removing 156 HGMD-included cases, the remaining 149 unpublished DDD cases showed an almost-unchanged overall trend.",
      [S_Y22], S_Y22, "Discussion paragraph 1")
claim("yuan2024-optimal-protocols", PR["y24_ddd"], "reported_finding",
      "Exomiser under Protocol D, PhenIX under Protocol D, AMELIE under Protocol B and LIRICAL were compared as optimised settings; in DDD, Exomiser ranked the causal gene first in 61.6% and within the top 5 in 86.6% of 305 trio cases.",
      [S_Y24], S_Y24, "Results 'Performance benchmarking for optimized prioritizers across different experiments' paragraph 1")
claim("kafkas2025-clinvar-bias", PR["kf_clinvar"], "comparison_caveat",
      "In the case of ClinVar, we used the HPO phenotypes as input for ranking; these phenotypes are identical to the phenotypes associated with the causative gene in the database used by Exomiser, and this may bias the results.",
      [S_KF], S_KF, "Results 'LLMs improve on ontology-based ranking methods' paragraph 4")

# ---------------------------------------------------------------- judgements
CONSTR = ["Inspect every linked evaluation's source locator and preserved conflicts before citing a result.",
          "Do not combine this mapping's evaluations with any other protocol's results, including the existing Talos and Exomiser mappings."]
J = []


def judgement(short, proto, relevance, endpoint, rationale, limitations, cites, group, title, headline, stratum=None, order=None):
    a = {"field": f"links:assessed_by:{proto}", "value": proto, "relevance": relevance, "endpoint": endpoint, "rationale": rationale, "constraints": CONSTR,
         "limitations": limitations, "citation_locators": [{"source_id": s, "locator": l} for s, l in cites],
         "source_locator": "; ".join(f"{s}: {l}" for s, l in cites), "revision": 1,
         "reason": "Recorded from the rare-disease ranking use-case pass 2026-10-09 (data/omics/use-case-coverage-rare-ranking-20261009/).",
         "comparison_group": group, "comparison_title": title, "headline_metric": headline}
    if stratum:
        a["stratum_label"], a["stratum_order"] = stratum, order
    pname = next(r["name"] for r in records if r["id"] == proto)
    rec("claim", f"use-case-mapping-rare-ranking-20261009-{short}", f'Relevance of {pname} to "{UC_NAME}"', rationale, a, sorted({s for s, _ in cites}), links=[("subject", UC)])
    J.append(proto)


DIRECT = ("Case-level recovery of the known causal gene within the top 1 to top 50 ranked genes, for several tools on the same solved exome cohort, directly measures how much review "
          "each tool needs to reach the causal gene. Ranking does not establish pathogenicity or a diagnosis.")
judgement("yuan2022-ddd", PR["y22_ddd"], "direct", "Top-1 to top-50 causal-gene recovery for 11 tool configurations (6 using HPO and VCF, 5 HPO-only) on 305 solved DDD exomes, default singleton runs",
          DIRECT, Y22_LIM, [(S_Y22S, "SM Table 3 rows 'DDD'"), (S_Y22, "Table 2; Materials 'Performance evaluation'")], "yuan2022-default", "Default singleton runs of 10 prioritisers (Yuan et al. 2022)", "top-10-accuracy", "DDD (305)", 1)
judgement("yuan2022-kmcgd", PR["y22_kmcgd"], "direct", "The same metrics on 209 solved in-house exomes", DIRECT + " The in-house cohort is not limited to developmental disorders.",
          Y22_LIM[:2] + ["In-house cohort; not public.", "Default singleton runs."], [(S_Y22S, "SM Table 3 rows 'KMCGD'")], "yuan2022-default",
          "Default singleton runs of 10 prioritisers (Yuan et al. 2022)", "top-10-accuracy", "KMCGD (209)", 2)
judgement("yuan2024-ddd", PR["y24_ddd"], "direct", "Top-1 to top-50 causal-gene recovery for Exomiser 13.1.0, PhenIX 1.16 and AMELIE 3.1.0 under four parameter protocols each and LIRICAL 1.3.4, on 305 DDD trio families",
          DIRECT + " It adds trio-mode runs, which the use case treats as a separate comparison from singleton runs.", Y24_LIM,
          [(S_Y24, "Table 1 rows 'DDD'; Results")], "yuan2024-protocols", "Parameter and trio-mode protocols (Yuan et al. 2024)", "top-10-accuracy", "DDD trios (305)", 1)
judgement("yuan2024-kgd", PR["y24_kgd"], "direct", "The same metrics on 152 in-house trio families", DIRECT, Y24_LIM + ["In-house cohort; not public."],
          [(S_Y24, "Table 1 rows 'KGD'")], "yuan2024-protocols", "Parameter and trio-mode protocols (Yuan et al. 2024)", "top-10-accuracy", "KGD trios (152)", 2)
PROXY = ("Ranking a causative gene within a fixed candidate set from phenotypes compares an LLM with Exomiser's gene scores at set sizes like a review budget, but the sets are "
         "synthetic and phenotypes come from databases, so it is not case-level performance on real exomes.")
for i, (key, name) in enumerate((("gpcards", "GPCards"), ("clinvar", "ClinVar"), ("pavs", "PAVS"))):
    judgement(f"kafkas2025-{key}", PR[f"kf_{key}"], "proxy",
              f"Hits@1, Hits@10, ROC AUC and AUPR for GPT-4 (zero-shot and one-shot)" + ("" if key == "gpcards" else " and Exomiser 12.1.0 gene scores") + f" in {name} candidate sets of 5 to 100 genes",
              PROXY, KF_LIM, [(S_KF, f"Table 3 column '{name}'; Methods")], "kafkas2025-gene-sets", "GPT-4 versus Exomiser on synthetic candidate gene sets (Kafkas et al. 2025)",
              "top-1-accuracy", name, i + 1)

records.sort(key=lambda r: r["id"])
ids = [r["id"] for r in records]
assert len(ids) == len(set(ids)), [i for i, c in Counter(ids).items() if c > 1]
with open(os.path.join(OUT, "batch.jsonl"), "w") as f:
    for r in records:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")
claims_rows.sort()
with open(os.path.join(OUT, "claims.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["record_id", "source_id", "locator", "printed_value", "review_scope"])
    w.writerows(claims_rows)
print(json.dumps(Counter(r["kind"] for r in records), sort_keys=True))
print("judged protocols:", J)
