"""Deterministic extraction of structure-prediction reliability comparisons into a records batch.

Usage: python3 -I extract_structural.py <download-dir> <batch-dir>

Reads two pinned JATS XML files and asserts every label and sentence it depends on:
  - Fromm et al. 2026 (Bioinformatics 42(4):btag136) Table 1: nine ways to pick the top AlphaFold3
    model per antibody-antigen target, scored by mean DockQ of the pick and Spearman correlation
  - Smorodina et al. 2026 (bioRxiv 10.64898/2026.03.02.709004 v1, via Europe PMC PPR1221387),
    printed values in Results paragraphs P11, P19, P21 and P36: cognate versus shuffled
    nanobody-antigen discrimination by ipTM, ipTM against DockQ calibration, and DockQ against sampling
Also writes judgements for two existing FoldBench protocols (antibody-antigen, protein-ligand),
which reuse stored records and add none. Writes batch.jsonl and claims.csv in the store form.
"""
import csv, hashlib, json, os, re, sys
import xml.etree.ElementTree as ET
from decimal import Decimal

DL, BATCH = sys.argv[1], sys.argv[2]
P = "structural-20261009"
UC = "use-case-structural-hypotheses-experiments"
DATE = "2026-10-09"
FACETS = {"areas": ["proteins-complexes"], "contexts": ["research"]}
records, claim_rows = [], []


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def expect(got, value, where):
    if got != value:
        raise SystemExit(f"{where}: expected {value!r}, found {got!r}")


def text(el):
    return " ".join("".join(el.itertext()).split()) if el is not None else ""


def rec(id_, kind, name, description, source_ids, links=None, attributes=None, facets=None, status="needs_review"):
    records.append({"id": id_, "kind": kind, "name": name, "description": description, "status": status,
                    "facets": FACETS if facets is None else facets, "source_ids": source_ids,
                    "links": links or [], "attributes": attributes or {}})


# ---------------------------------------------------------------- sources
FRO_XML = f"{DL}/PMC13061134/PMC13061134.xml"
SMO_XML = f"{DL}/smorodina2026/epmc.xml"
FRO_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13061134/fullTextXML"
SMO_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PPR1221387/fullTextXML"
S_FRO = f"{P}-source-fromm2026"
S_SMO = f"{P}-source-smorodina2026"


def source(id_, name, url, version, retrieved_at, path, status, doi, archive, extra):
    attrs = {"url": url, "artifact_url": {S_FRO: FRO_URL, S_SMO: SMO_URL}[id_], "version": version,
             "retrieved_at": retrieved_at, "artifact_sha256": sha(path), "publication_status": status,
             "licence": "CC-BY-4.0", "media_type": "application/xml", "doi": doi,
             "source_locator": "Full artifact bytes; per-record locators on each record",
             "access_and_reuse": "CC BY 4.0 permits redistribution of the article bytes.",
             "archive_note": f"Gzip copy (gzip -n -9) archived in the batch as artifacts/{archive}.",
             "extraction_method": "JATS XML parse (xml.etree), by extract/extract_structural.py"}
    attrs.update(extra)
    rec(id_, "source", name, "Primary source retrieved and hashed for the structural hypotheses use-case pass.",
        [], attributes=attrs)


source(S_FRO, "Evaluating deep learning based structure prediction methods on antibody-antigen complexes",
       "https://doi.org/10.1093/bioinformatics/btag136",
       "Bioinformatics 42(4):btag136, 2026; PMC13061134 full-text XML", "2026-10-09T21:21:58Z", FRO_XML,
       "peer_reviewed", "10.1093/bioinformatics/btag136", "fromm2026-article.xml.gz",
       {"scope_note": ("Authors: Fromm, Ludaic and Elofsson (Stockholm University); conflicts of interest: none declared. "
                       "The authors did not develop AlphaFold3, Boltz-1 or Chai-1. pDockQ2, one of the ranking scores "
                       "compared, comes from the same group (Zhu et al. 2023).")})
source(S_SMO, "Structural Plausibility Without Binding Specificity: Limits of AI-Based Antibody-Antigen Structure Prediction Confidence Scores",
       "https://doi.org/10.64898/2026.03.02.709004",
       "bioRxiv version 1, posted 2026-03-03; Europe PMC preprint full text PPR1221387 (manuscript EMS215481); not peer reviewed",
       "2026-10-09T21:25:48Z", SMO_XML, "preprint", "10.64898/2026.03.02.709004", "smorodina2026-article.xml.gz",
       {"scope_note": ("Authors: Smorodina, Ali, Kropivšek Brumat, Salicari, Miklavc, Kappassov, Fu, Sormanni, de Marco and "
                       "Greiff. None developed AlphaFold3, Boltz-2 or Chai-1. Competing interests printed: V.G. declares "
                       "advisory, consulting and employment roles with antibody-discovery and biotechnology companies, "
                       "none of them a developer of the three tools compared."),
        "retrieval_note": ("bioRxiv returned HTTP 429 (Cloudflare 1015) for the source XML, and the Europe PMC supplementary "
                           "files returned a browser challenge, so only the Europe PMC full text was read. "
                           "Supplementary Tables 1, 3 and 4 were not read.")})


def review_note(path, url, how):
    return {"method": ["deterministic-table-parse" if "Table" in how else "transcription"], "reviewer": ["claude"],
            "date": DATE, "reviewer_note": "Claude (Opus 5.5) extraction agent; extraction record, not an independent review",
            "artifact_sha256": sha(path), "retrieval_url": url, "note": how + " Pending independent review."}


def result(id_, eval_id, source_ids, locator, pv, numeric, metric, qualifier, unit, direction, review, extra=None):
    attrs = {"metric": metric, "metric_qualifier": qualifier, "metric_direction": direction, "unit": unit,
             "printed_value": pv, "numeric_value": format(Decimal(numeric), "f"), "source_locator": locator,
             "review": review, "missing_metadata": {"uncertainty": {"reason": "unreported"}}}
    attrs.update(extra or {})
    rec(id_, "result", f"{eval_id.replace(P + '-eval-', '')} {metric}",
        "Reported measurement transcribed from the pinned source. Not independently reproduced.",
        source_ids, [{"relation": "evaluation", "target_id": eval_id}], attrs, facets={})
    claim_rows.append([id_, source_ids[-1], locator, pv, "result"])


def evaluation(id_, name, config, protocol, dataset, source_ids, origin, comparison, locator, limitations=None, missing=None):
    attrs = {"origin": origin, "protocol": protocol, "version": "Primary source as retrieved 2026-10-09",
             "comparison": {"protocol_id": protocol, **comparison}, "source_locator": locator}
    if limitations:
        attrs["limitations"] = limitations
    if missing:
        attrs["missing_metadata"] = missing
    rec(id_, "evaluation", name, "Published comparison; transcribed, not reproduced.", source_ids,
        [{"relation": "system", "target_id": config}, {"relation": "assessment", "target_id": protocol},
         {"relation": "data", "target_id": dataset}], attrs)


def claim(id_, subject, field, value, source_ids, locator, path, url):
    rec(id_, "claim", f"{field}: {subject}", "Descriptive fact transcribed from the pinned source.", source_ids,
        [{"relation": "subject", "target_id": subject}],
        {"field": field, "value": value, "source_locator": locator,
         "review": {"method": ["transcription"], "reviewer": ["claude"], "date": DATE,
                    "reviewer_note": "Claude (Opus 5.5) extraction agent; extraction record, not an independent review",
                    "artifact_sha256": sha(path), "retrieval_url": url,
                    "note": "Hand transcription from the source text. Pending independent review."}}, facets={})
    claim_rows.append([id_, source_ids[-1], locator, value, "claim"])


def configuration(id_, name, model_id, source_ids, reported, locator, version=None, extra=None, limitations=None):
    attrs = {"reported_name": reported, "foundation_model_eligible": True, "source_locator": locator}
    if version:
        attrs["version"] = version
    else:
        attrs["missing_metadata"] = {"version": {"reason": "unreported", "note": "No release or commit is printed for this run"}}
    attrs.update(extra or {})
    if limitations:
        attrs["limitations"] = limitations
    rec(id_, "configuration", name, "Configuration as run in the cited comparison.", source_ids,
        [{"relation": "configuration_of", "target_id": model_id}], attrs,
        facets={**FACETS, "method_types": ["foundation_model"]})


# existing model records, reused by link only
AF3, BOLTZ2, BOLTZ, CHAI1 = "discovery-model-alphafold-3", "catalog-model-boltz-2", "discovery-model-boltz", "catalog-model-chai-1"

# ================================================================ Fromm et al. 2026, Table 1
fro = ET.parse(FRO_XML).getroot()
fro_paras = [text(p) for p in fro.find(".//body").iter("p")]


def fro_para(start):
    hits = [p for p in fro_paras if p.startswith(start)]
    expect(len(hits), 1, f"Fromm paragraph starting {start!r}")
    return hits[0]


tw = [t for t in fro.iter("table-wrap") if t.get("id") == "btag136-T1"]
expect(len(tw), 1, "Fromm Table 1")
expect(text(tw[0].find("caption")), "Summary for different methods to rank AlphaFold3 models, average DockQ (<DockQ>) and "
       "Spearman correlation for all targets (R) or average per target <R>.", "Fromm Table 1 caption")
rows = [[text(c) for c in tr] for tr in tw[0].iter("tr")]
expect(rows[0], ["Method", "<DockQ>", "R", "<R>"], "Fromm Table 1 header")
body = rows[1:]
expect([r[0] for r in body], ["DockQ", "aeTM", "aeiTM", "aeRankConf", "pTM", "ipTM", "RankConf", "pDockQ2", "ipSAE"],
       "Fromm Table 1 row labels")
for r in body:
    expect(all(re.fullmatch(r"[01]\.\d{3}", v) for v in r[1:]), True, f"Fromm Table 1 values for {r[0]}")
# the paragraphs that fix the set, the sampling and the reading of the table
p_set = fro_para("The dataset consists of 110 antibody–antigen structures with <80% sequence identity")
expect("30 September 2021, serves as the cut-off for the training data used by all benchmarked methods" in p_set, True, "Fromm cutoff sentence")
p_samp = fro_para("For each complex in the dataset, 40 random seeds (1–40) were used to generate five models each")
p_tab = fro_para("To better understand the impact of feature quality versus function accuracy")
expect("(DockQ = 0.35, versus 0.54)" in p_tab and "(<R><0.30)" in p_tab, True, "Fromm Table 1 discussion")

D_FRO = f"{P}-data-fromm2026-abag-110"
rec(D_FRO, "dataset", "Fromm et al. 2026 antibody-antigen benchmark: 110 complexes released after 30 September 2021",
    "Antibody-antigen structures from SAbDab deposited after the AlphaFold3 training cutoff, filtered against earlier entries.",
    [S_FRO],
    attributes={"version": "SAbDab entries as of 23 October 2024, built with a modified AADaM; Zenodo 10.5281/zenodo.17978681",
                "population": ("110 antibody-antigen complexes deposited after 30 September 2021, X-ray or electron microscopy at "
                               "3.5 Å or better, under 80% sequence identity per chain to any entry before that date, then "
                               "clustered at 80%; antibody-peptide complexes excluded"),
                "total": 110,
                "scope_note": ("No two antibodies are identical; one antigen appears twice with two antibodies. 15 antigen "
                               "sequences occur in the training set. Concatenated CDR identity to the training set is at most 72%."),
                "source_locator": "Section 2.1 (Dataset), paragraphs 1 to 3"})

PR_FRO = f"{P}-protocol-fromm2026-abag-model-selection"
FRO_LIM = ["Antibody-antigen complexes only; results do not transfer to other complex classes.",
           "Structural accuracy against the deposited complex, not binding, affinity or the outcome of an experiment.",
           "Only AlphaFold3 models are ranked in Table 1; the source does not print the same table for AlphaFold2.3, Boltz-1 or Chai-1.",
           "Table 1 does not state the number of models ranked per target. Its DockQ row (0.544) matches the best-of-200 value "
           "given in the text (0.54), so the table is read as selection among all 200 models; this is an inference.",
           "The DockQ, aeTM, aeiTM and aeRankConf rows use the experimental structure, so they are upper bounds, not usable selection rules.",
           "Figure 6 and the text give a per-target ranking-confidence correlation of 0.28, while Table 1 prints 0.214 for "
           "RankConf under a Spearman caption; the figure's correlation type is not stated.",
           "No uncertainty is printed."]
rec(PR_FRO, "protocol", "Picking the top AlphaFold3 model per antibody-antigen target with a confidence score",
    "200 AlphaFold3 models per target; each score picks one model, which is scored by DockQ against the deposited complex.",
    [S_FRO], [{"relation": "uses_data", "target_id": D_FRO}],
    {"protocol": ("AlphaFold3 is run with 40 seeds and 5 diffusion samples per seed, giving 200 models per target. Each "
                  "ranking score selects the model it rates highest; the score is the mean DockQ of the selected models "
                  "over 110 targets. Two correlations with DockQ are also printed: across all models of all targets (R) and "
                  "the mean of per-target correlations (<R>). DockQ is computed for the antibody-antigen interface with "
                  "multi-chain antigens merged into one chain."),
     "version": "Fromm et al. 2026, sections 2.2 to 2.7 and 3.5 to 3.6; Table 1",
     "metric": "dockq", "metric_direction": "higher", "unit": "unitless",
     "metric_definition": ("<DockQ>: mean over targets of the DockQ of the model each score ranks first. R: Spearman "
                           "correlation between the score and DockQ over all models. <R>: mean over targets of the per-target "
                           "Spearman correlation."),
     "selection": "Highest value of the named score among the 200 models of each target",
     "limitations": FRO_LIM,
     "source_locator": "Sections 2.2.2, 2.4, 2.7, 3.5 and 3.6; Table 1"})
claim(f"{P}-claim-fromm2026-top-vs-best", PR_FRO, "headline_finding",
      "For AlphaFold3 the mean DockQ of the top-ranked model rises only from 0.29 to 0.37 as sampling grows, while the best "
      "generated model reaches 0.52. For Boltz-1 and Chai-1 the top-ranked model barely improves with more samples (from 0.12 "
      "to 0.14). Scores computed from predicted aligned errors give a mean DockQ of about 0.35 for the selected model against "
      "0.54 for the best model; the same scores computed from the true aligned errors close most of that gap.",
      [S_FRO], "Section 3.3 paragraph 1; section 3.6 paragraph 4", FRO_XML, FRO_URL)

FRO_ROWS = {
    "DockQ": ("dockq-oracle", "DockQ against the experimental structure (oracle upper bound)", "author_reported",
              ["Uses the experimental structure; the best achievable pick, not a selection rule."]),
    "aeTM": ("aetm-oracle", "aeTM: pTM recomputed from true aligned errors (oracle)", "author_reported",
             ["Defined by the source; uses the experimental structure, so not usable before an experiment."]),
    "aeiTM": ("aeitm-oracle", "aeiTM: ipTM recomputed from true aligned errors (oracle)", "author_reported",
              ["Defined by the source; uses the experimental structure, so not usable before an experiment."]),
    "aeRankConf": ("aerankconf-oracle", "aeRankConf: 0.2 aeTM + 0.8 aeiTM (oracle)", "author_reported",
                   ["Defined by the source; uses the experimental structure, so not usable before an experiment."]),
    "pTM": ("ptm", "AlphaFold3 pTM", "independent_paper", None),
    "ipTM": ("iptm", "AlphaFold3 ipTM", "independent_paper", None),
    "RankConf": ("ranking-confidence", "AlphaFold3 ranking confidence (0.2 pTM + 0.8 ipTM)", "independent_paper", None),
    "pDockQ2": ("pdockq2", "pDockQ2 (Zhu et al. 2023)", "author_reported",
                ["pDockQ2 was developed by the same group as this source."]),
    "ipSAE": ("ipsae", "ipSAE (Dunbrack 2025), PAE and distance cut-off 10 Å", "independent_paper", None),
}
fro_review = review_note(FRO_XML, FRO_URL, "Extracted by deterministic parse of JATS Table 1 (table-wrap btag136-T1), asserting "
                         "the caption, the header, the nine row labels and three values of the form d.ddd per row.")
for label, mean_dockq, r_all, r_target in body:
    key, desc, origin, lim = FRO_ROWS[label]
    cid = f"{P}-config-fromm2026-af3-{key}"
    configuration(cid, f"AlphaFold3, 200 models per target, top model picked by {desc} (Fromm et al. 2026)", AF3, [S_FRO],
                  label, f"Table 1, row '{label}'; sections 2.2.2 and 2.7",
                  extra={"source_label": label, "samples": 200,
                         "parameters": "40 seeds (1 to 40) x 5 diffusion samples; MSAs from the AlphaFold 2.3.2 pipeline (commit f251de6), bfd_uniref_hits.a3m",
                         "selection": f"Model with the highest {label} among the 200"},
                  limitations=lim)
    ev = f"{P}-eval-fromm2026-af3-{key}"
    evaluation(ev, f"AlphaFold3 top model by {label} on 110 post-cutoff antibody-antigen complexes (Fromm et al. 2026)", cid,
               PR_FRO, D_FRO, [S_FRO], origin,
               {"dataset_version": "110 complexes deposited after 30 September 2021", "split": "Temporal split at the AlphaFold3 training cutoff",
                "population": "110 antibody-antigen complexes", "inputs": "Sequences and MSAs; no templates of the complex",
                "adaptation": "None; selection among sampled models", "metric_implementation": "DockQ (Basu and Wallner 2016; Mirabello and Wallner 2024)",
                "aggregation": "Mean over targets", "budget": "200 models per target"},
               f"Table 1, row '{label}'", limitations=(lim or []) + ["Run by authors who did not develop AlphaFold3."])
    for col, raw, metric, qual in (("<DockQ>", mean_dockq, "dockq", "mean over targets of the DockQ of the model picked by this score"),
                                   ("R", r_all, "spearman-correlation", "score against DockQ over all models of all targets"),
                                   ("<R>", r_target, "spearman-correlation", "mean over targets of the per-target correlation of score against DockQ")):
        suffix = {"<DockQ>": "mean-dockq", "R": "spearman-all", "<R>": "spearman-per-target"}[col]
        result(f"{ev.replace('-eval-', '-result-')}-{suffix}", ev, [S_FRO], f"Table 1, row '{label}', column '{col}'",
               raw, raw, metric, qual, "unitless", "higher", fro_review,
               extra={"scored_count": 110})

# ================================================================ Smorodina et al. 2026, Results text
smo = ET.parse(SMO_XML).getroot()
SP = {p.get("id"): text(p) for p in smo.iter("p") if p.get("id")}


def smo_find(pid, pattern, n):
    m = re.search(pattern, SP[pid])
    if not m:
        raise SystemExit(f"Smorodina {pid}: pattern {pattern!r} not found")
    expect(len(m.groups()), n, f"Smorodina {pid} group count")
    return m.groups()


ap = smo_find("P11", r"AF3 achieved the highest PR-AUC \(AP = (0\.\d+)\), followed by Chai-1 \(AP = (0\.\d+)\) and Boltz-2 \(AP = (0\.\d+)\)", 3)
base = smo_find("P11", r"\(baseline precision ≈ (0\.\d+); ~(\d+)-(\d+) positives out of ~([\d,]+)-([\d,]+) evaluated pairs", 5)
cal = smo_find("P19", r"pearson correlation of r=(0\.\d+) for best-DockQ structures and relatively few overconfident failures "
               r"\(Q2 - (\d+)%, Q4 - (\d+)%\)\. AF3 maintained high correlation even at the single-sample level \(r=(0\.\d+) for sample0\)", 4)
calb = smo_find("P19", r"best-DockQ calibration remained moderate \(pearson r=(0\.\d+)\), a substantial fraction of predictions fell into "
                r"the overconfident failure regime \(Q2 - (\d+)%\).*?correlation dropped sharply \(pearson r=(0\.\d+)\)", 3)
calc = smo_find("P19", r"underconfident successes \(Q4; (\d+)%\).*?\(best-DockQ vs\. ipTM, r=(0\.\d+)\)", 2)
delta = smo_find("P21", r"correlations between changes in DockQ and changes in ipTM were near zero across all models "
                 r"\(r=(-0\.\d+), (-0\.\d+), and (-0\.\d+) for AF3, Boltz-2, and Chai-1, respectively", 3)
samp = smo_find("P36", r"by Δ=\+(0\.\d+) for AF3 \((0\.\d+) to (0\.\d+)\), Δ=\+(0\.\d+) for Boltz-2 \((0\.\d+) to (0\.\d+)\), "
                r"Δ=\+(0\.\d+) for Boltz-1 \((0\.\d+) to (0\.\d+)\), and Δ=\+(0\.\d+) for Chai-1 \((0\.\d+) to (0\.\d+)\)", 12)
# the discussion repeats the change correlations at two decimals; they must agree with P21 to rounding
disc = [v for v in SP.values() if "pearson’s r=-0.03, -0.04, and -0.02 for AF3, Boltz-2 and Chai-1" in v]
expect(len(disc), 1, "Smorodina discussion repeat of the change correlations")
expect([round(float(x), 2) for x in delta], [-0.03, -0.04, -0.02], "Smorodina P21 against the discussion")
# printed deltas against the printed medians; AF3 differs by 0.01, consistent with rounding of the medians
rounding = {}
for i, tool in enumerate(("AF3", "Boltz-2", "Boltz-1", "Chai-1")):
    d, lo, hi = (Decimal(x) for x in samp[i * 3:i * 3 + 3])
    if hi - lo != d:
        expect(abs(hi - lo - d) <= Decimal("0.01"), True, f"Smorodina P36 delta for {tool}")
        rounding[tool] = f"Printed Δ=+{d} while the printed medians differ by {hi - lo}; consistent with rounding of the medians to two decimals."
expect(sorted(rounding), ["AF3"], "Smorodina P36 rounding differences")
hits = [k for k, v in SP.items() if "Chai-1- 25 train and 81 test systems" in v]
expect(len(hits), 1, "Smorodina train/test split sentence")
SPLIT_PID = hits[0]
splits = smo_find(SPLIT_PID, r"Chai-1- (\d+) train and (\d+) test systems; Boltz-2-(\d+) train and (\d+) test systems; AF3 - (\d+) train and (\d+) test systems", 6)
expect(splits, ("25", "81", "64", "42", "30", "76"), "Smorodina train/test counts")
cut = [k for k, v in SP.items() if "AF3: ~30 September 2021, ii) Chai-1: ~12 January 2021, iii) Boltz-2: ~1 June 2023" in v]
expect(len(cut), 1, "Smorodina training cutoff sentence")
cur = [k for k, v in SP.items() if "only post-October 2021depositions were retained from SAbDab-nano, corresponding to the earliest training cutoff among the evaluated tools (Boltz-2)" in v]
expect(len(cur), 1, "Smorodina curation sentence")
shuf = [k for k, v in SP.items() if "we assume that VHHs and antigens of “shuffled complexes” are non-binders" in v]
expect(len(shuf), 1, "Smorodina negative-definition sentence")
vers = {"AF3": [k for k, v in SP.items() if "alphafold3-3.0.1 via Singularity container" in v],
        "Boltz": [k for k, v in SP.items() if "Boltz CLI v2.2.0" in v],
        "Chai-1": [k for k, v in SP.items() if "Chai-1 predictions were performed using version 0.6.1" in v]}
for k, v in vers.items():
    expect(len(v), 1, f"Smorodina version sentence for {k}")
CUT_PID, CUR_PID, SHUF_PID = cut[0], cur[0], shuf[0]

D_SMO_REAL = f"{P}-data-smorodina2026-vhh-antigen-106"
D_SMO_PAIRS = f"{P}-data-smorodina2026-vhh-antigen-91x91"
SMO_SCOPE = ("Curated from SAbDab-nano (downloaded March 2025; post-October 2021 depositions) and from AACDB, whose pre-cutoff "
             "structures were kept on purpose to probe memorisation. Resolution 3.0 Å or better, VHH 110 to 150 residues, antigen "
             "100 to 400 residues. Per-tool training overlap printed by the source: AF3 30 train and 76 test systems, Chai-1 25 "
             "and 81, Boltz-2 64 and 42.")
rec(D_SMO_REAL, "dataset", "Smorodina et al. 2026 nanobody-antigen benchmark: 106 cognate VHH-antigen complexes",
    "Experimentally determined nanobody-antigen complexes, used as the real (cognate) systems.", [S_SMO],
    attributes={"version": "bioRxiv v1 benchmark; Zenodo 10.5281/zenodo.18390239",
                "population": "106 VHH-antigen systems from 91 PDB entries; 15 entries hold two VHHs bound to different epitopes",
                "total": 106, "scope_note": SMO_SCOPE,
                "source_locator": f"Methods, VHH-antigen dataset curation ({CUR_PID} and following); Results {SPLIT_PID}; Methods {CUT_PID}"})
rec(D_SMO_PAIRS, "dataset", "Smorodina et al. 2026 all-against-all VHH-antigen pairing matrix (91 unique PDB entries)",
    "Every VHH paired with every antigen; the observed pairing is the positive and all other pairings are treated as non-binders.",
    [S_SMO],
    attributes={"version": "bioRxiv v1 benchmark; Zenodo 10.5281/zenodo.18390239",
                "population": f"All VHH-antigen pairings over 91 unique PDB entries; about {base[1]} to {base[2]} positives among about {base[3]} to {base[4]} scored pairs, depending on the tool",
                "label_semantics": ("Positive: the cognate pairing of each VHH, observed in a deposited structure. Negative: a shuffled "
                                    "pairing of a VHH with a non-cognate antigen, which the source assumes does not bind; none was "
                                    "tested experimentally."),
                "missing_metadata": {"positives": {"reason": "unreported", "note": f"Printed only as about {base[1]} to {base[2]}, depending on the tool"},
                                     "negatives": {"reason": "unreported", "note": f"Printed only as part of about {base[3]} to {base[4]} scored pairs"}},
                "scope_note": SMO_SCOPE,
                "source_locator": f"Results {SHUF_PID} to P11; Methods P66 and P67"})

SMO_COMMON_LIM = [
    "Nanobody (VHH)-antigen complexes only; results do not transfer to conventional antibodies or other complex classes.",
    "The set mixes systems inside and outside each tool's training data (AF3 30 of 106 in training, Chai-1 25, Boltz-2 64); "
    "the printed values are over all systems, so they are not post-cutoff results, and Boltz-2's are the most exposed.",
    "The curation text calls Boltz-2's cutoff the earliest among the tools, while the methods give Chai-1 about 12 January 2021, "
    "AF3 about 30 September 2021 and Boltz-2 about 1 June 2023. The per-tool counts follow the later statement.",
    "Preprint, not peer reviewed. Supplementary tables were not read.",
    "No uncertainty is printed for these values."]

PR_SPEC = f"{P}-protocol-smorodina2026-vhh-cognate-vs-shuffled"
SPEC_LIM = ["Negatives are shuffled pairings assumed to be non-binders; none was tested, and some may bind.",
            "Ranks pairings by ipTM; it measures whether confidence separates observed from assumed-absent interactions, not structural accuracy."] + SMO_COMMON_LIM
rec(PR_SPEC, "protocol", "Telling cognate from shuffled nanobody-antigen pairs by ipTM",
    "All-against-all VHH-antigen pairings are predicted; the best ipTM of 50 samples ranks each pairing, scored by average precision for the cognate pairs.",
    [S_SMO], [{"relation": "uses_data", "target_id": D_SMO_PAIRS}],
    {"protocol": ("Each VHH is paired with each antigen over 91 unique PDB entries and predicted with 50 samples per pairing. "
                  "Each pairing is scored by its interface confidence (ipTM). Precision-recall over all pairings, with the "
                  "cognate pairing as the positive, summarised as average precision."),
     "version": "Smorodina et al. 2026 bioRxiv v1, Results P8 to P11, Figure 2B",
     "metric": "average-precision", "metric_direction": "higher", "unit": "unitless",
     "metric_definition": ("Area under the precision-recall curve (average precision) for ranking cognate pairs above shuffled "
                           f"pairs by ipTM. The random baseline equals the positive prevalence, printed as about {base[0]}."),
     "limitations": SPEC_LIM, "source_locator": "Results P8 to P11; Figure 2"})
claim(f"{P}-claim-smorodina2026-shuffled-negatives", PR_SPEC, "negative_definition",
      "The source states: 'we assume that VHHs and antigens of “shuffled complexes” are non-binders'. Negatives are therefore "
      "pairings assumed not to bind, not pairings shown not to bind.", [S_SMO], f"Results {SHUF_PID}", SMO_XML, SMO_URL)
claim(f"{P}-claim-smorodina2026-random-baseline", PR_SPEC, "baseline",
      f"Random baseline precision is about {base[0]}: about {base[1]} to {base[2]} positives out of about {base[3]} to {base[4]} "
      "evaluated pairs, depending on the tool after excluding missing values.", [S_SMO], "Results P11", SMO_XML, SMO_URL)

PR_CAL = f"{P}-protocol-smorodina2026-vhh-iptm-dockq-calibration"
CAL_LIM = ["Calibration is computed on cognate complexes only; it says nothing about whether ipTM separates binders from non-binders.",
           "Quadrant thresholds (DockQ 0.23, ipTM 0.5) are the source's choice, and the text does not say which sample (best, first or worst) the quadrant shares refer to.",
           "Not every tool has every value printed in the text."] + SMO_COMMON_LIM
rec(PR_CAL, "protocol", "How well ipTM tracks DockQ on cognate nanobody-antigen complexes",
    "On the 106 cognate complexes, 50 samples per complex; correlation of ipTM with DockQ, the share of confident failures and unconfident successes, and whether ipTM follows DockQ gains from sampling.",
    [S_SMO], [{"relation": "uses_data", "target_id": D_SMO_REAL}],
    {"protocol": ("For each cognate complex, 50 samples are predicted and scored by DockQ against the deposited structure. "
                  "Pearson correlation of ipTM with DockQ is printed for the best-DockQ sample and for the first sample "
                  "(sample0). Quadrants at DockQ 0.23 and ipTM 0.5: Q2 is ipTM at least 0.5 with DockQ below 0.23 (confident "
                  "failure), Q4 is ipTM below 0.5 with DockQ at least 0.23 (unconfident success). Change correlation: Pearson "
                  "correlation between the change in DockQ and the change in ipTM under saturation sampling."),
     "version": "Smorodina et al. 2026 bioRxiv v1, Results P18 to P22, Figure 3",
     "metric": "pearson-correlation", "metric_direction": "higher", "unit": "unitless",
     "metric_definition": ("Pearson correlation between ipTM and DockQ across the cognate complexes. Quadrant shares use DockQ "
                           "0.23 (CAPRI acceptable) and ipTM 0.5 (confident) as thresholds."),
     "limitations": CAL_LIM, "source_locator": "Results P18 to P22; Figure 3; Supplementary Table 3 (not read)"})

PR_SAMP = f"{P}-protocol-smorodina2026-vhh-dockq-vs-sampling"
SAMP_LIM = ["Best-of-N DockQ needs the experimental structure to pick the best sample, so it is an upper bound on what a user could select.",
            "Each sampling depth is a separate run with its own seed (seeds 1 to 5 for N = 1, 10, 25, 50 and 100), unlike the single 50-sample runs of the other protocols.",
            "For Chai-1 the smallest depth is 5 samples (5 trunk samples x 1 diffusion sample), so its N = 1 value is the best of 5.",
            "Boltz-1 appears only in this analysis."] + SMO_COMMON_LIM
rec(PR_SAMP, "protocol", "Best DockQ against sampling depth on cognate nanobody-antigen complexes",
    "For each of 106 cognate complexes, the best DockQ among N samples, summarised as the median over complexes, at N = 1 and N = 100.",
    [S_SMO], [{"relation": "uses_data", "target_id": D_SMO_REAL}],
    {"protocol": ("Each complex is predicted with five independent seeds at sampling depths N = 1, 10, 25, 50 and 100. For each "
                  "complex the maximum DockQ at each depth is taken and the median over complexes is printed for N = 1 and N = 100."),
     "version": "Smorodina et al. 2026 bioRxiv v1, Results P33 to P36, Methods P83 and P91, Figure 5B",
     "metric": "dockq", "metric_direction": "higher", "unit": "unitless",
     "metric_definition": "Median over complexes of the per-complex maximum DockQ among N samples.",
     "limitations": SAMP_LIM, "source_locator": "Results P33 to P36; Methods P83 and P91; Figure 5B"})

smo_review = review_note(SMO_XML, SMO_URL, "Extracted by regular expressions over the Results paragraphs of the JATS XML, each "
                         "asserted to match exactly once, with the discussion's rounded repeat checked against the Results values.")
SMO_CFG = {
    "af3": ("AlphaFold3 3.0.1, 50 diffusion samples, seed 1, built-in data pipeline", AF3, "alphafold3-3.0.1",
            "num_diffusion_samples = 50; run_data_pipeline = true; seed = 1; MSAs from the built-in pipeline", "AF3",
            "30 of 106 cognate systems in the training set; 76 not (AF3 cutoff about 30 September 2021)", vers["AF3"][0]),
    "boltz2": ("Boltz-2 via Boltz CLI v2.2.0, 50 diffusion samples, seed 42, MSA server", BOLTZ2, "Boltz CLI v2.2.0, --model boltz2",
               "--use_msa_server; recycling_steps = 3; sampling_steps = 200; diffusion_samples = 50; seed 42", "Boltz-2",
               "64 of 106 cognate systems in the training set; 42 not (Boltz-2 cutoff about 1 June 2023)", vers["Boltz"][0]),
    "boltz1": ("Boltz-1 via Boltz CLI v2.2.0, MSA server", BOLTZ, "Boltz CLI v2.2.0, --model boltz1",
               "--use_msa_server; recycling_steps = 3; sampling_steps = 200; sampling depth set per analysis", "Boltz-1",
               "Training overlap not printed for Boltz-1", vers["Boltz"][0]),
    "chai1": ("Chai-1 0.6.1, 5 trunk x 10 diffusion samples, seed 42, ESM embeddings without MSAs", CHAI1, "0.6.1",
              "num_trunk_samples = 5; num_diffn_samples = 10; num_trunk_recycles = 3; num_diffn_timesteps = 200; seed = 42; no MSAs",
              "Chai-1", "25 of 106 cognate systems in the training set; 81 not (Chai-1 cutoff about 12 January 2021)", vers["Chai-1"][0]),
}
for key, (name, model_id, version, params, label, overlap, pid) in SMO_CFG.items():
    configuration(f"{P}-config-smorodina2026-{key}", f"{name} (Smorodina et al. 2026)", model_id, [S_SMO], label,
                  f"Methods, structure prediction ({pid})", version=version,
                  extra={"source_label": label, "parameters": params, "training_overlap": overlap})


def smo_eval(protocol, key, data, locator, comparison, extra_lim=None):
    ev = f"{P}-eval-smorodina2026-{protocol.split('-smorodina2026-')[1]}-{key}"
    evaluation(ev, f"{SMO_CFG[key][4]} on {next(r['name'] for r in records if r['id'] == protocol)} (Smorodina et al. 2026)",
               f"{P}-config-smorodina2026-{key}", protocol, data, [S_SMO], "independent_paper",
               {"dataset_version": "bioRxiv v1 benchmark", "split": "Mixed: systems inside and outside the tool's training data",
                "inputs": "VHH and antigen sequences", "adaptation": "None", **comparison},
               locator, limitations=["Run by authors who did not develop the tool."] + (extra_lim or []))
    return ev


T3 = {"af3": "AF3", "chai1": "Chai-1", "boltz2": "Boltz-2"}
for key, pv in zip(("af3", "chai1", "boltz2"), ap):
    ev = smo_eval(PR_SPEC, key, D_SMO_PAIRS, f"Results P11, '{T3[key]}' AP",
                  {"population": "All pairings over 91 unique PDB entries", "metric_implementation": "Average precision of the precision-recall curve",
                   "aggregation": "One curve over all pairings", "budget": "50 samples per pairing; best ipTM per pairing"})
    result(f"{ev.replace('-eval-', '-result-')}-average-precision", ev, [S_SMO], f"Results P11, 'AP = {pv}' for {T3[key]}",
           pv, pv, "average-precision", "cognate against shuffled pairs ranked by ipTM", "unitless", "higher", smo_review,
           extra={"scope_note": f"Random baseline precision about {base[0]} (positive prevalence)."})

CAL_VALUES = {
    "af3": [("pearson-correlation", "best", cal[0]), ("pearson-correlation", "sample0", cal[3]),
            ("proportion", "q2", cal[1]), ("proportion", "q4", cal[2]), ("pearson-correlation", "change", delta[0])],
    "boltz2": [("pearson-correlation", "best", calb[0]), ("pearson-correlation", "sample0", calb[2]),
               ("proportion", "q2", calb[1]), ("pearson-correlation", "change", delta[1])],
    "chai1": [("pearson-correlation", "best", calc[1]), ("proportion", "q4", calc[0]), ("pearson-correlation", "change", delta[2])],
}
CAL_DESC = {"best": ("ipTM against DockQ for the best-DockQ sample of each complex", "higher", "unitless", "P19"),
            "sample0": ("ipTM against DockQ for the first sample (sample0) of each complex", "higher", "unitless", "P19"),
            "q2": ("share of predictions with ipTM at least 0.5 and DockQ below 0.23 (confident failures, Q2)", "lower", "percent", "P19"),
            "q4": ("share of predictions with ipTM below 0.5 and DockQ at least 0.23 (unconfident successes, Q4)", "lower", "percent", "P19"),
            "change": ("change in ipTM against change in DockQ under saturation sampling", "higher", "unitless", "P21")}
for key, vals in CAL_VALUES.items():
    printed = {k for _, k, _ in vals}
    missing = [CAL_DESC[k][0] for k in ("best", "sample0", "q2", "q4", "change") if k not in printed]
    ev = smo_eval(PR_CAL, key, D_SMO_REAL, f"Results P19 and P21, values for '{T3[key]}'",
                  {"population": "106 cognate complexes", "metric_implementation": "Pearson correlation; DockQ v2.1.3",
                   "aggregation": "Across complexes", "budget": "50 samples per complex"},
                  extra_lim=[f"Not printed in the text for this tool: {'; '.join(missing)}."] if missing else None)
    for metric, k, raw in vals:
        qual, direction, unit, pid = CAL_DESC[k]
        pv = f"{raw}%" if unit == "percent" else raw
        result(f"{ev.replace('-eval-', '-result-')}-{k}", ev, [S_SMO], f"Results {pid}, {T3[key]}: {qual}",
               pv, raw, metric, qual, unit, direction, smo_review)

S4 = {"af3": "AF3", "boltz2": "Boltz-2", "boltz1": "Boltz-1", "chai1": "Chai-1"}
for i, key in enumerate(("af3", "boltz2", "boltz1", "chai1")):
    d, lo, hi = samp[i * 3:i * 3 + 3]
    ev = smo_eval(PR_SAMP, key, D_SMO_REAL, f"Results P36, '{S4[key]}'",
                  {"population": "106 cognate complexes", "metric_implementation": "DockQ v2.1.3",
                   "aggregation": "Median over complexes of the per-complex maximum", "budget": "5 seeds; N = 1 and N = 100 samples"},
                  extra_lim={"boltz1": ["Boltz-1 is not in the other analyses of this source."],
                             "chai1": ["The N = 1 level is 5 samples for Chai-1 (Methods P91)."]}.get(key))
    for n, raw in (("1", lo), ("100", hi)):
        extra = {"rounding_note": rounding[S4[key]]} if S4[key] in rounding and n == "100" else None
        result(f"{ev.replace('-eval-', '-result-')}-n{n}", ev, [S_SMO], f"Results P36, {S4[key]} ({lo} to {hi}), N = {n}",
               raw, raw, "dockq", f"median over complexes of the best DockQ among N = {n} samples", "unitless", "higher",
               smo_review, extra=extra)

# ================================================================ judgements
J = "use-case-mapping-structural-20261009"
CONSTRAINTS = ["Inspect every linked evaluation's source locator and preserved limitations before citing a result.",
               "Do not combine this mapping's evaluations with any other protocol's results; complex sets, sampling and metrics differ.",
               "Results for one complex class do not establish performance in another.",
               "Structural accuracy and confidence are not evidence that an interaction exists, how strong it is or that an experiment will work."]


def judgement(short, protocol, endpoint, rationale, limitations, sources, cites, group, title, metric, label, order):
    rec(f"{J}-{short}", "claim", f"Relevance of {protocol} to \"Which predicted interfaces or structures are reliable enough to guide my next experiment?\"",
        rationale, sources, [{"relation": "subject", "target_id": UC}],
        {"field": f"links:assessed_by:{protocol}", "value": protocol, "relevance": "proxy", "endpoint": endpoint,
         "rationale": rationale, "constraints": CONSTRAINTS, "limitations": limitations,
         "citation_locators": [{"source_id": s, "locator": loc} for s, loc in cites],
         "source_locator": "; ".join(f"{s}: {loc}" for s, loc in cites), "revision": 1,
         "reason": "Add comparisons of structure-prediction reliability by complex class from the structural hypotheses use-case pass 2026-10-09.",
         "comparison_group": group, "comparison_title": title, "headline_metric": metric,
         "stratum_label": label, "stratum_order": order}, facets={})


G_AB, T_AB = "antibody-antigen-interfaces", "Antibody and nanobody-antigen interface predictions"
G_LIG, T_LIG = "protein-ligand-poses", "Protein-ligand pose predictions"
FB_PAPER, FB_SUPP = "ucc-research-source-foldbench-paper", "ucc-research-source-foldbench-supp"
FB_LIM = ["Benchmark authors ran all five tools; per-tool assessable counts differ, so the scored populations are not matched.",
          "Structural success against the deposited complex, not binding, affinity or the outcome of an experiment.",
          "No uncertainty is printed."]
judgement("foldbench-antibody-antigen", "ucc-research-protocol-foldbench-antibody-antigen",
          "FoldBench success rate, LDDT, interface RMSD and ligand RMSD for AlphaFold 3, Boltz-1, Chai-1, HelixFold 3 and Protenix on antibody-antigen targets with low homology to earlier PDB entries",
          "The only multi-tool comparison stored for antibody-antigen complexes on a held-out set with five current cofolding tools under one protocol. It is proxy evidence: success means structural agreement with the deposited complex, and confidence is not assessed.",
          FB_LIM + ["Antibody-antigen targets only."], [FB_PAPER, FB_SUPP],
          [(FB_SUPP, "Supplementary Table 3, antibody-antigen block"), (FB_PAPER, "Table 1 assessable counts")],
          G_AB, T_AB, "foldbench-success-rate", "Accuracy of five tools (FoldBench)", 1)
judgement("fromm2026-model-selection", PR_FRO,
          "Mean DockQ of the AlphaFold3 model picked by each of nine scores (ipTM, pTM, ranking confidence, pDockQ2, ipSAE and four oracle references) among 200 models per target, and Spearman correlation with DockQ over all models and per target, on 110 antibody-antigen complexes released after the training cutoff",
          "Answers whether the confidence a user sees can pick the right antibody-antigen model: every score based on predicted errors picks models with mean DockQ near 0.35 when the best available is 0.54, and the per-target correlation stays below 0.25. Proxy evidence: structural accuracy only, one tool, one complex class.",
          FRO_LIM, [S_FRO], [(S_FRO, "Section 2.1; sections 3.3 and 3.6; Table 1")],
          G_AB, T_AB, "dockq", "Picking AlphaFold3 models by confidence (independent)", 2)
judgement("smorodina2026-sampling", PR_SAMP,
          "Median best DockQ among 1 and among 100 samples for AlphaFold3, Boltz-2, Boltz-1 and Chai-1 on 106 nanobody-antigen complexes",
          "Shows how much sampling raises the best available nanobody-antigen model for four tools. Proxy evidence: the best sample is picked with the experimental structure, the set mixes training and held-out systems, and the source is a preprint.",
          SAMP_LIM, [S_SMO], [(S_SMO, "Results P33 to P36; Methods P83 and P91; Figure 5B")],
          G_AB, T_AB, "dockq", "Best of N samples, nanobodies (preprint)", 3)
judgement("smorodina2026-calibration", PR_CAL,
          "Pearson correlation of ipTM with DockQ, share of confident failures and unconfident successes, and correlation of ipTM change with DockQ change under sampling, for AlphaFold3, Boltz-2 and Chai-1 on 106 nanobody-antigen complexes",
          "Measures whether each tool's confidence tracks its structural accuracy on nanobody complexes, which decides whether a confident model can be trusted. Proxy evidence: cognate complexes only, mixed training exposure, preprint.",
          CAL_LIM, [S_SMO], [(S_SMO, "Results P18 to P22; Figure 3")],
          G_AB, T_AB, "pearson-correlation", "Confidence against accuracy, nanobodies (preprint)", 4)
judgement("smorodina2026-cognate-vs-shuffled", PR_SPEC,
          "Average precision for ranking cognate above shuffled nanobody-antigen pairings by ipTM, for AlphaFold3, Chai-1 and Boltz-2, against a random baseline of about 0.011",
          "Tests the use case's second exclusion directly: whether high confidence indicates that an interaction exists. Proxy evidence: the negatives are pairings assumed not to bind, never tested, and the set mixes training and held-out systems.",
          SPEC_LIM, [S_SMO], [(S_SMO, f"Results {SHUF_PID} to P11; Figure 2")],
          G_AB, T_AB, "average-precision", "Confidence as evidence of binding, nanobodies (preprint)", 5)
judgement("foldbench-protein-ligand", "ucc-research-protocol-foldbench-protein-ligand",
          "FoldBench success rate, LDDT-LP and LDDT-PLI for AlphaFold 3, Boltz-1, Chai-1, HelixFold 3 and Protenix on protein-ligand targets with low homology to earlier PDB entries",
          "The stored multi-tool comparison for protein-ligand poses on a held-out set, kept apart from protein and antibody complexes because results do not transfer between classes. Proxy evidence: pose accuracy against the deposited complex, not affinity or activity.",
          FB_LIM + ["Protein-ligand targets only."], [FB_PAPER, FB_SUPP],
          [(FB_SUPP, "Supplementary Table 3, protein-ligand block"), (FB_PAPER, "Table 1 assessable counts")],
          G_LIG, T_LIG, "foldbench-success-rate", "Pose accuracy of five tools (FoldBench)", 1)

records.sort(key=lambda r: r["id"])
ids = [r["id"] for r in records]
if len(ids) != len(set(ids)):
    from collections import Counter as C
    raise SystemExit(f"Duplicate IDs: {[k for k, v in C(ids).items() if v > 1][:5]}")
with open(os.path.join(BATCH, "batch.jsonl"), "w") as f:
    for r in records:
        f.write(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n")
with open(os.path.join(BATCH, "claims.csv"), "w", newline="") as f:
    w = csv.writer(f, lineterminator="\n")
    w.writerow(["record_id", "source_id", "locator", "printed_value", "review_scope"])
    for row in sorted(claim_rows):
        w.writerow(row)
from collections import Counter
print(Counter(r["kind"] for r in records), len(records))
