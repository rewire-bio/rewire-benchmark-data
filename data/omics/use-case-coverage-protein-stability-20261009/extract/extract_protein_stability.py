"""Deterministic extraction of protein stability-change predictor comparisons into a records batch.

Usage: python3 -I extract_protein_stability.py <pinned-dir> <batch-dir>

<pinned-dir> holds the pinned article XML files named in ARTIFACTS. The script checks each SHA-256, reads the
tables from the JATS XML, asserts every row and column label it depends on, and writes batch.jsonl and claims.csv
in the current store shape. Nothing is marked reviewed.
"""
import csv, hashlib, json, os, re, sys
import xml.etree.ElementTree as ET
from collections import Counter
from decimal import Decimal

PINNED, BATCH = sys.argv[1], sys.argv[2]
P = "protein-stability-20261009"
UC = "use-case-protein-stability"
UC_NAME = "Assess methods for protein stability experiments"
FACETS = {"areas": ["proteins-complexes"], "contexts": ["research"]}
TODAY = "2026-10-09"
ARTIFACTS = {
    "pancotti2022-article.xml": "132038084a57c060add54f152f68a69ccaf198337f86a5ec03d39496945c0024",
    "dieckhaus2024-article.xml": "ba9a763c388eeea47d70fd0d8e2fbf497f61fc8a88dc93d5dac261572daa8010",
    "chu2024-article.xml": "bb9830cbd6bab1b3e0ddbb52edb2a9afd4b06e427dbfeb19e6a07f843ebd914f",
}
records, claims_rows, judgements = [], [], []
for name, digest in ARTIFACTS.items():
    got = hashlib.sha256(open(os.path.join(PINNED, name), "rb").read()).hexdigest()
    assert got == digest, f"{name}: {got} != pinned {digest}"


def rec(id_, kind, name, description, source_ids, links=None, attributes=None, facets=None, status="needs_review"):
    assert re.fullmatch(r"[a-z0-9][a-z0-9-]{0,254}", id_), id_
    r = {"id": id_, "kind": kind, "name": name[:500], "description": description, "status": status,
         "facets": FACETS if facets is None else facets, "source_ids": source_ids,
         "links": links or [], "attributes": attributes or {}}
    records.append(r)
    return r


def review_note(how):
    return {"method": ["deterministic-table-parse"], "reviewer": ["claude"],
            "reviewer_note": "Extracting Claude (Opus 5.5) research agent; not a review. No human review claimed.",
            "date": TODAY, "note": f"{how} Pending independent review."}


METRIC = {
    "r": dict(metric="pearson-correlation", metric_direction="higher", unit="unitless"),
    "rho": dict(metric="spearman-correlation", metric_direction="higher", unit="unitless"),
    "rmse": dict(metric="root-mean-squared-error", metric_direction="lower", unit="kilocalorie-per-mole"),
    "mae": dict(metric="mean-absolute-error", metric_direction="lower", unit="kilocalorie-per-mole"),
    "r_dr": dict(metric="pearson-correlation", metric_direction="unknown", unit="unitless"),
    "bias": dict(metric="antisymmetry-bias", metric_direction="unknown", unit="kilocalorie-per-mole"),
}


def num(text):
    t = text.replace("–", "-").replace("−", "-")
    assert re.fullmatch(r"-?\d+(\.\d+)?", t), text
    return format(Decimal(t), "f")


def result(id_, eval_id, source_ids, sha, url, locator, printed, metric, qualifier, how, extra=None):
    attrs = {**METRIC[metric], "metric_qualifier": qualifier, "printed_value": printed, "numeric_value": num(printed),
             "source_locator": locator, "missing_metadata": {"uncertainty": {"reason": "unreported"}},
             "review": {**review_note(how), "artifact_sha256": sha, "retrieval_url": url}}
    if extra:
        attrs.update(extra)
    rec(id_, "result", f"{eval_id.removeprefix(P + '-eval-')} {METRIC[metric]['metric']} ({qualifier})",
        "Reported measurement transcribed from the pinned source. Not independently reproduced.",
        source_ids, [{"relation": "evaluation", "target_id": eval_id}], attrs, facets={})
    claims_rows.append([id_, source_ids[-1], locator, printed, "result"])


def evaluation(id_, name, system, protocol, dataset, source_ids, origin, comparison, locator, missing=None, extra=None):
    attrs = {"origin": origin, "protocol": protocol, "version": f"Primary source as retrieved {TODAY}",
             "comparison": {"protocol_id": protocol, **comparison}, "source_locator": locator}
    if missing:
        attrs["missing_metadata"] = missing
    if extra:
        attrs.update(extra)
    rec(id_, "evaluation", name, "Published stability-change predictor comparison; transcribed, not reproduced.", source_ids,
        [{"relation": "system", "target_id": system}, {"relation": "assessment", "target_id": protocol},
         {"relation": "data", "target_id": dataset}], attrs)


def slug(t):
    return re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")


FAMILY = {"acdc-nn-seq": "acdc-nn", "ddgun3d": "ddgun", "inps3d": "inps", "inps-seq": "inps", "i-mutant3-0": "i-mutant",
          "i-mutant3-0-seq": "i-mutant", "dynamut2": "dynamut", "mupro": "mupro", "esm-2-35m": "esm-2", "esm-2-3b": "esm-2"}
FAMILY_NAME = {"acdc-nn": "ACDC-NN", "ddgun": "DDGun", "inps": "INPS", "i-mutant": "I-Mutant", "dynamut": "DynaMut",
               "mupro": "MUpro", "esm-therm": "ESM therm"}
EXISTING = {"esm-2": "discovery-model-esm-2", "proteinmpnn": "discovery-model-proteinmpnn"}  # reused records
PHYSICS = {"rosetta", "foldx"}
STATISTICAL = {"ddgun", "sdm", "popmusic"}
PLM = {"esm-2"}
METHODS = {}


def method(label, source_ids):
    fam = FAMILY.get(slug(label), slug(label))
    if fam in EXISTING:
        return EXISTING[fam], fam
    mid = f"{P}-method-{fam}"
    if mid in METHODS:
        for s in source_ids:
            if s not in METHODS[mid]["source_ids"]:
                METHODS[mid]["source_ids"].append(s)
        return mid, fam
    name = FAMILY_NAME.get(fam, label)
    METHODS[mid] = rec(mid, "method", name, "Protein stability-change (ddG) predictor.", list(source_ids), [],
                       {"reported_name": name, "entity_level": "method", "source_locator": "Method lists and table row labels of the cited sources",
                        "missing_metadata": {"version": {"reason": "inapplicable", "note": "Family record; versions are on configurations"}}},
                       facets={**FACETS, "method_types": mtype(fam)})
    return mid, fam


def mtype(fam):
    if fam in PHYSICS or fam in STATISTICAL:
        return ["conventional_pipeline"]
    if fam in PLM:
        return ["foundation_model"]
    return ["supervised_machine_learning"]


def config(cid, label, study, source_ids, attrs, extra_links=None):
    mid, fam = method(label, source_ids[:1])
    links = [{"relation": "configuration_of", "target_id": mid}] + (extra_links or [])
    rec(cid, "configuration", f"{label} ({study})", f"{label} as evaluated in the cited comparison.", source_ids, links,
        {"reported_name": label, "foundation_model_eligible": fam in PLM, **attrs}, facets={**FACETS, "method_types": mtype(fam)})
    return cid


def judgement(short, protocol, protocol_name, source_ids, relevance, endpoint, rationale, limitations, locators, group, title, headline,
              stratum=None, order=None):
    cid = f"use-case-mapping-{P}-{short}"
    attrs = {"field": f"links:assessed_by:{protocol}", "value": protocol, "relevance": relevance, "endpoint": endpoint,
             "rationale": rationale,
             "constraints": ["Inspect every linked evaluation's source locator before citing a result.",
                             "Do not combine this mapping's evaluations with any other protocol's results; datasets, splits, structures and predictor versions differ between sources."],
             "limitations": limitations, "revision": 1,
             "reason": "Add primary-source stability predictor comparison evidence from the protein stability use-case pass (2026-10-09).",
             "citation_locators": [{"source_id": s, "locator": l} for s, l in locators],
             "source_locator": "; ".join(f"{s}: {l}" for s, l in locators),
             "comparison_group": group, "comparison_title": title, "headline_metric": headline}
    if stratum is not None:
        attrs["stratum_label"] = stratum
        attrs["stratum_order"] = order
    rec(cid, "claim", f"Relevance of {protocol_name} to \"{UC_NAME}\"", rationale, source_ids,
        [{"relation": "subject", "target_id": UC}], attrs, facets={})
    judgements.append(cid)


tx = lambda e: " ".join(" ".join(e.itertext()).split())


def table(path, tid):
    t = ET.parse(path)
    tw = next(x for x in t.iter("table-wrap") if x.get("id") == tid)
    return tw, [[tx(c) for c in tr if c.tag in ("td", "th")] for tr in tw.iter("tr")]


def source(sid, title, doi, pmcid, version, when, sha, licence):
    rec(sid, "source", title, "Primary source retrieved and hashed for the protein stability use-case pass.", [], [],
        {"url": f"https://doi.org/{doi}", "artifact_url": f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/fullTextXML",
         "version": version, "retrieved_at": when, "artifact_sha256": sha, "doi": doi, "publication_status": "peer_reviewed",
         "licence": licence, "media_type": "application/xml"})
    return sid


HOW = ("Extracted by deterministic parse of the table in the pinned JATS XML (extract/extract_protein_stability.py), with the "
       "caption, header rows and row labels asserted. printed_value is the cell text as printed, without footnote markers, which "
       "are kept in printed_source_cell.")

# =============================================================================================
# A. Pancotti et al. 2022, Briefings in Bioinformatics 23(2):bbab555, Table 1 (S669)
# =============================================================================================
A = source(f"{P}-source-pancotti2022", "Predicting protein stability changes upon single-point mutation: a thorough comparison of the available tools on a new dataset",
           "10.1093/bib/bbab555", "PMC8921618", "Briefings in Bioinformatics 23(2):bbab555, published 2022-01-11; PMC8921618 full-text XML",
           "2026-10-09T21:00:42Z", ARTIFACTS["pancotti2022-article.xml"], "CC-BY-NC-4.0")
A_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC8921618/fullTextXML"
tw, rows = table(os.path.join(PINNED, "pancotti2022-article.xml"), "TB1")
assert tx(tw.find("caption")).startswith("Assessment of the protein stability prediction tools on s669.")
assert rows[0] == ["", "Total", "Direct", "Reverse", "Antisimmetry/Bias"], rows[0]
assert rows[1][:10] == ["Method", "r", "RMSE", "MAE", "r", "RMSE", "MAE", "r", "RMSE", "MAE"] and len(rows[1]) == 12, rows[1]
A_STRUCT = ["ACDC-NN", "DDGun3D", "PremPS", "ThermoNet", "Rosetta", "Dynamut", "INPS3D", "SDM", "PoPMuSiC", "MAESTRO", "FoldX",
            "DUET", "I-Mutant3.0", "mCSM", "Dynamut2"]
A_SEQ = ["INPS-Seq", "ACDC-NN-Seq", "DDGun", "I-Mutant3.0-Seq", "MUpro", "SAAFEC-SEQ"]
assert [r[0] for r in rows[2:]] == ["Structure-based"] + A_STRUCT + ["Sequence-based"] + A_SEQ, [r[0] for r in rows[2:]]
A_OWN = {"ACDC-NN", "ACDC-NN-Seq", "DDGun", "DDGun3D"}  # developed by authors of this paper (Fariselli, Capriotti groups)
A_DATA = rec(f"{P}-data-pancotti2022-s669", "dataset", "S669: 669 single-point variants from ThermoMutDB in proteins under 25% identity to S2648 and VariBench, with reverse variants",
             "Benchmark set introduced in Pancotti et al. 2022.", [A], [],
             {"population": "669 direct variants manually cleaned from ThermoMutDB (proteins under 25% sequence identity to S2648 and VariBench) plus 669 reverse variants with Robetta-modelled mutant structures; 1,338 in total",
              "split": "External test set; no training", "denominator": 1338,
              "source_locator": "Section 2.1 'Datasets' paragraphs 1 and 3",
              "missing_metadata": {"version": {"reason": "unreported", "note": "ThermoMutDB release not stated"}}})["id"]
apid = f"{P}-protocol-pancotti2022-s669"
A_LIMS = ["Single benchmark of 669 variants with reverse variants built from modelled structures.",
          "Some methods (ACDC-NN, ACDC-NN-Seq, DDGun, DDGun3D) were developed by authors of this paper.",
          "Predictor versions and servers are listed only in the Supplementary Materials, which were not read; web servers may have changed since.",
          "Proteins are under 25% identity to S2648 and VariBench, but predictors trained on other data (for example ThermoMutDB itself) may still overlap.",
          "No uncertainty is printed."]
rec(apid, "protocol", "S669 direct and reverse ddG prediction (Pancotti et al. 2022 Table 1)",
    "Pearson r, RMSE and MAE on direct, reverse and all variants, plus antisymmetry r and bias, for 21 predictors.", [A],
    [{"relation": "uses_data", "target_id": A_DATA}],
    {"protocol": "Each tool run once on S669 and its reverse variants with default parameters (web server or stand-alone); predicted ddG compared with experimental ddG in kcal/mol.",
     "version": "Table 1", "metric": "pearson-correlation", "limitations": A_LIMS, "denominator": 1338,
     "source_locator": "Table 1; Sections 2.2 and 2.3"})
A_COLS = [(1, "r", "all 1,338 direct and reverse variants"), (2, "rmse", "all 1,338 direct and reverse variants"), (3, "mae", "all 1,338 direct and reverse variants"),
          (4, "r", "669 direct variants"), (5, "rmse", "669 direct variants"), (6, "mae", "669 direct variants"),
          (7, "r", "669 reverse variants"), (8, "rmse", "669 reverse variants"), (9, "mae", "669 reverse variants"),
          (10, "r_dr", "antisymmetry, direct versus reverse predictions"), (11, "bias", "antisymmetry bias")]
A_HEAD = {1: "Total r", 2: "Total RMSE", 3: "Total MAE", 4: "Direct r", 5: "Direct RMSE", 6: "Direct MAE", 7: "Reverse r",
          8: "Reverse RMSE", 9: "Reverse MAE", 10: "Antisimmetry r(d-r)", 11: "Bias"}
for r in rows[2:]:
    label = r[0]
    if label in ("Structure-based", "Sequence-based"):
        assert len(r) == 1
        continue
    assert len(r) == 12, r
    group = "structure-based" if label in A_STRUCT else "sequence-based"
    cid = config(f"{P}-config-pancotti2022-{slug(label)}", label, "Pancotti et al. 2022", [A],
                 {"protocol": f"Default parameters; {group} (Table 1 group)",
                  "source_locator": "Section 2.2 'Evaluated methods'; Table 1",
                  "missing_metadata": {"version": {"reason": "unextracted", "note": "Versions and servers are in the Supplementary Materials, not read in this pass"}}})
    eid = f"{P}-eval-pancotti2022-{slug(label)}-s669"
    evaluation(eid, f"{label} on S669 (Pancotti et al. 2022)", cid, apid, A_DATA, [A], "author_reported" if label in A_OWN else "independent_paper",
               {"dataset_version": None, "split": "External test set", "population": "669 direct and 669 reverse variants",
                "inputs": "Protein sequence or structure and the variant" , "adaptation": None,
                "metric_implementation": "Pearson r, RMSE and MAE between predicted and experimental ddG", "aggregation": "Pooled over variants", "budget": None},
               f"Table 1, row '{label}'", missing={"comparison.dataset_version": {"reason": "unreported"}})
    for col, m, q in A_COLS:
        result(f"{P}-result-pancotti2022-{slug(label)}-s669-{slug(A_HEAD[col])}", eid, [A], ARTIFACTS["pancotti2022-article.xml"], A_URL,
               f"Table 1, row '{label}', column '{A_HEAD[col]}'", r[col], m, f"S669, {q}", HOW)
judgement("pancotti2022-s669", apid, "S669 direct and reverse ddG prediction (Pancotti et al. 2022)", [A], "direct",
          "Pearson r, RMSE and MAE of predicted against experimental ddG for 21 predictors on 669 direct and 669 reverse variants, with antisymmetry",
          ("Experimental ddG for proteins dissimilar to the usual training sets directly tests how well each predictor ranks substitutions by folding "
           "stability on unseen proteins, and the reverse variants test for bias towards destabilising predictions."),
          A_LIMS, [(A, "Table 1; Sections 2.1-2.3")], "pancotti2022-s669", "S669 external ddG benchmark (Pancotti et al. 2022)", "pearson-correlation")

# =============================================================================================
# B. Dieckhaus et al. 2024, PNAS 121(6):e2314853121, Tables 2 and 3
# =============================================================================================
B = source(f"{P}-source-dieckhaus2024", "Transfer learning to leverage larger datasets for improved prediction of protein stability changes",
           "10.1073/pnas.2314853121", "PMC10861915", "PNAS 121(6):e2314853121, published 2024-01-29; PMC10861915 full-text XML",
           "2026-10-09T21:01:06Z", ARTIFACTS["dieckhaus2024-article.xml"], "CC-BY-NC-ND-4.0")
B_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10861915/fullTextXML"
B_SHA = ARTIFACTS["dieckhaus2024-article.xml"]
B_DATA = {
    "megascale": rec(f"{P}-data-dieckhaus2024-megascale-test", "dataset", "Megascale (Tsuboyama 2023) test split, homology-clustered at 25% identity",
                     "Held-out protein clusters from the cDNA display proteolysis set as curated by Dieckhaus et al.", [B], [],
                     {"population": "28,312 single-point mutations in test-split proteins; reliable ddG only; natural and de novo designed domains of 40-72 residues",
                      "split": "MMseqs2 clusters at 25% identity; no test protein has a homologue in the Megascale or Fireprot training sets", "denominator": 28312,
                      "source_locator": "Methods 'Datasets' paragraphs 2 and 4; Results 'Comparison with literature methods'",
                      "missing_metadata": {"version": {"reason": "unreported", "note": "Tsuboyama et al. 2023 release used; exact file version not stated"}}})["id"],
    "fireprot": rec(f"{P}-data-dieckhaus2024-fireprot-hf", "dataset", "FireProtDB homologue-free split with experimental structures",
                    "Low-throughput biophysical ddG measurements matched to PDB structures, homologue-free split.", [B], [],
                    {"population": "2,578 mutations; 85 of 100 Fireprot proteins have fewer than 50 measurements",
                     "split": "Homologue-free split at 25% identity to the training sets", "denominator": 2578,
                     "source_locator": "Methods 'Datasets' paragraphs 3-4; Results",
                     "missing_metadata": {"version": {"reason": "unreported"}}})["id"],
    "ssym": rec(f"{P}-data-dieckhaus2024-ssym", "dataset", "Ssym (342 direct and 342 inverse variants with experimental structures)",
                "Antisymmetry benchmark as used in Dieckhaus et al. Table 3.", [B], [],
                {"population": "Ssym direct and inverse sets (342 each, per the literature definition); counts not printed in Table 3",
                 "split": "External test set", "source_locator": "Table 3",
                 "missing_metadata": {"version": {"reason": "unreported"}, "denominator": {"reason": "unreported", "note": "Variant counts are not printed in this source"}}})["id"],
    "s669": rec(f"{P}-data-dieckhaus2024-s669", "dataset", "S669 as used in Dieckhaus et al. Table 3",
                "Direct S669 variants; ThermoMPNN trained on a homologue-filtered Megascale set; ABYSSAL scored on 420 filtered variants.", [B], [],
                {"population": "669 direct variants (420 for ABYSSAL)", "split": "External test set", "source_locator": "Table 3 and footnotes",
                 "missing_metadata": {"version": {"reason": "unreported"}}})["id"],
}
B_TRAIN = {"ThermoMPNN"}
B_RETRAINED = {"RaSP", "PROSTATA"}
B_CONF = {}


def b_config(label):
    if label in B_CONF:
        return B_CONF[label]
    attrs = {"source_locator": "Tables 2-3; Results 'Comparison with literature methods'"}
    extra = None
    if label == "ThermoMPNN":
        attrs["protocol"] = "ProteinMPNN backbone embeddings with a transfer-learned stability head trained on the Megascale training split"
        attrs["missing_metadata"] = {"version": {"reason": "unreported", "note": "No release number printed"}}
        extra = [{"relation": "uses_model", "target_id": EXISTING["proteinmpnn"]}]
    elif label in B_RETRAINED:
        attrs["protocol"] = "Retrained by the authors on the Megascale dataset (Table 2 footnote †)"
        attrs["missing_metadata"] = {"version": {"reason": "unreported"}}
    elif label == "ProteinMPNN":
        attrs["protocol"] = "Published pretrained ProteinMPNN log-likelihood ratios used to rank mutations"
        attrs["missing_metadata"] = {"version": {"reason": "unreported"}}
    else:
        attrs["protocol"] = "Published model or software with accessible code, run by the authors (Table 2) or values taken from the cited literature (Table 3)"
        attrs["missing_metadata"] = {"version": {"reason": "unreported"}}
    B_CONF[label] = config(f"{P}-config-dieckhaus2024-{slug(label)}", label, "Dieckhaus et al. 2024", [B], attrs, extra)
    return B_CONF[label]


def split_cell(cell):
    m = re.fullmatch(r"(-?\d+(?:\.\d+)?)\s*([*†]?)", cell)
    assert m, cell
    return m.group(1), m.group(2)


# Table 2
tw2, rows2 = table(os.path.join(PINNED, "dieckhaus2024-article.xml"), "t02")
assert tx(tw2.find("caption")) == "Comparison of ThermoMPNN performance with literature methods on Megascale and Fireprot datasets"
assert rows2[0] == ["", "Megascale (test)", "Fireprot (HF)"] and rows2[1] == ["Model", "RMSE (kcal/mol)", "PCC", "SCC", "RMSE (kcal/mol)", "PCC", "SCC"], rows2[:2]
T2 = ["ProteinMPNN", "ThermoMPNN", "Rosetta", "RaSP †", "PROSTATA †", "FoldX", "ACDC-NN", "ACDC-NN-Seq", "ThermoNet", "MAESTRO", "mCSM", "MUPRO"]
assert [r[0] for r in rows2[2:]] == T2, [r[0] for r in rows2[2:]]
FOOT2 = tx(tw2.find("table-wrap-foot"))
assert "* Score may be inflated due to the presence of close homologues" in FOOT2 and "† Retrained using the Megascale dataset" in FOOT2
FOOT2_STAR = "Score may be inflated due to the presence of close homologues (>25% sequence identity) of Fireprot proteins in the training dataset."
B_PROTO = {}
B_LIMS = {
    "megascale": ["Developer comparison: the authors built ThermoMPNN and chose the comparator set (methods with readily accessible code).",
                  "Megascale proteins are 40-72-residue domains, many de novo designed, measured by one proteolysis assay over a narrow ddG range (-3 to 5 kcal/mol).",
                  "RaSP and PROSTATA were retrained on Megascale data for this table; other comparators use their published training.",
                  "No uncertainty is printed in Table 2 (Table 1 ablations give seed SD for ThermoMPNN only)."],
    "fireprot": ["Developer comparison (ThermoMPNN authors).",
                 "Values marked * may be inflated because those methods' training sets contain close homologues of Fireprot proteins (Table 2 footnote).",
                 "85 of 100 Fireprot proteins have fewer than 50 measurements, so pooled metrics are dominated by a few proteins.",
                 "No uncertainty is printed."],
    "ssym": ["Most rows are compiled from earlier publications (references 29 and 30 and the methods' own papers) rather than rerun by the authors.",
             "Variant counts are not printed in Table 3.",
             "No uncertainty is printed."],
    "s669": ["Most rows are compiled from Pancotti et al. 2022 (reference 30); the S669 values here are not an independent rerun.",
             "ThermoMPNN was trained on a homologue-filtered Megascale set for this column (footnote *); ABYSSAL was scored on 420 filtered variants (footnote dagger).",
             "The ACDC-NN RMSE printed here (1.60) differs from Pancotti et al. 2022 Table 1 (1.49 for direct variants), although its PCC matches.",
             "No uncertainty is printed."],
}
B_NAMES = {"megascale": "Megascale held-out test split", "fireprot": "Fireprot homologue-free split",
           "ssym": "Ssym direct and inverse", "s669": "S669 direct"}
for k, name in B_NAMES.items():
    pid = f"{P}-protocol-dieckhaus2024-{k}"
    B_PROTO[k] = pid
    table_no = "2" if k in ("megascale", "fireprot") else "3"
    rec(pid, "protocol", f"{name} ddG prediction (Dieckhaus et al. 2024 Table {table_no})",
        f"RMSE and correlation of predicted against experimental ddG on the {name}.", [B],
        [{"relation": "uses_data", "target_id": B_DATA[k]}],
        {"protocol": "Predicted ddG compared with experimental ddG in kcal/mol; PCC Pearson and SCC Spearman correlation.",
         "version": f"Table {table_no}", "metric": "pearson-correlation", "limitations": B_LIMS[k],
         "source_locator": f"Table {table_no}; Methods 'Datasets'"})

B_ORIGIN_T3 = {"ProteinMPNN": "author_reported", "ThermoMPNN": "author_reported"}
for r in rows2[2:]:
    label = r[0].replace(" †", "")
    cid = b_config(label)
    for k, cols in (("megascale", (1, 2, 3)), ("fireprot", (4, 5, 6))):
        eid = f"{P}-eval-dieckhaus2024-{slug(label)}-{k}"
        evaluation(eid, f"{label} on {B_NAMES[k]} (Dieckhaus et al. 2024)", cid, B_PROTO[k], B_DATA[k], [B],
                   "author_reported" if label in B_TRAIN else "independent_paper",
                   {"dataset_version": None, "split": B_NAMES[k], "population": f"{28312 if k == 'megascale' else 2578} mutations",
                    "inputs": "Protein structure or sequence and the mutation", "adaptation": "Retrained on Megascale" if label in B_RETRAINED else None,
                    "metric_implementation": "RMSE, Pearson and Spearman correlation", "aggregation": "Pooled over mutations", "budget": None},
                   f"Table 2, row '{r[0]}', {B_NAMES[k]} columns", missing={"comparison.dataset_version": {"reason": "unreported"}})
        for c, m, head in zip(cols, ("rmse", "r", "rho"), ("RMSE (kcal/mol)", "PCC", "SCC")):
            v, mark = split_cell(r[c])
            extra = {"printed_source_cell": r[c]}
            if mark == "*":
                extra["source_warnings"] = [FOOT2_STAR]
            result(f"{P}-result-dieckhaus2024-{slug(label)}-{k}-{METRIC[m]['metric']}", eid, [B], B_SHA, B_URL,
                   f"Table 2, row '{r[0]}', column '{B_NAMES[k].split(' ')[0]} {head}'", v, m, f"{B_NAMES[k]}", HOW, extra)

# Table 3
tw3, rows3 = table(os.path.join(PINNED, "dieckhaus2024-article.xml"), "t03")
assert tx(tw3.find("caption")) == "ThermoMPNN comparison with literature methods on Ssym and S669 datasets"
assert rows3[0] == ["", "Ssym (direct)", "Ssym (inverse)", "S669"], rows3[0]
assert rows3[1] == ["Model", "RMSE (kcal/mol)", "PCC", "RMSE (kcal/mol)", "PCC", "RMSE (kcal/mol)", "PCC"], rows3[1]
FOOT3 = tx(tw3.find("table-wrap-foot"))
assert "* Model trained with a filtered homologue-free Megascale training set" in FOOT3 and "420 of original 669 variants" in FOOT3
T3_MARK = {"*": "ThermoMPNN trained on a homologue-free filtered Megascale training set for this column (Table 3 footnote).",
           "†": "Scored on filtered S669 (420 of 669 variants) because of training-set homology (Table 3 footnote)."}
for r in rows3[2:]:
    m_lab = re.fullmatch(r"(.+?)(?: \(\s*([\d ,]+)\s*\))?", r[0])
    label, refs = m_lab.group(1), m_lab.group(2)
    if label == "MUPRO":
        label_key = "MUPRO"
    cid = b_config(label)
    origin = B_ORIGIN_T3.get(label, "paper_compilation")
    for k, cols, qual in (("ssym", (1, 2), "Ssym direct variants"), ("ssym", (3, 4), "Ssym inverse variants"), ("s669", (5, 6), "S669 direct variants")):
        eid = f"{P}-eval-dieckhaus2024-{slug(label)}-{k}"
        if not any(x["id"] == eid for x in records):
            evaluation(eid, f"{label} on {B_NAMES[k]} (Dieckhaus et al. 2024)", cid, B_PROTO[k], B_DATA[k], [B], origin,
                       {"dataset_version": None, "split": B_NAMES[k], "population": B_NAMES[k], "inputs": "Protein structure or sequence and the mutation",
                        "adaptation": None, "metric_implementation": None, "aggregation": "Pooled over variants", "budget": None},
                       f"Table 3, row '{r[0]}'", missing={"comparison.dataset_version": {"reason": "unreported"},
                                                          "comparison.metric_implementation": {"reason": "unreported"}},
                       extra={"limitations": [f"Values cited from references {refs} in Table 3."]} if refs else None)
        for c, m, head in zip(cols, ("rmse", "r"), ("RMSE (kcal/mol)", "PCC")):
            cell = r[c]
            if cell == "":
                continue
            v, mark = split_cell(cell)
            extra = {"printed_source_cell": cell}
            if mark:
                extra["source_warnings"] = [T3_MARK[mark]]
            result(f"{P}-result-dieckhaus2024-{slug(label)}-{slug(qual)}-{METRIC[m]['metric']}", eid, [B], B_SHA, B_URL,
                   f"Table 3, row '{r[0]}', column '{rows3[0][1 + (c - 1) // 2]} {head}'", v, m, qual, HOW, extra)

for k, rel, order in (("megascale", "direct", 1), ("fireprot", "direct", 2), ("ssym", "proxy", 3), ("s669", "proxy", 4)):
    judgement(f"dieckhaus2024-{k}", B_PROTO[k], f"{B_NAMES[k]} ddG prediction (Dieckhaus et al. 2024)", [B], rel,
              f"RMSE and correlation of predicted ddG on the {B_NAMES[k]} for the ThermoMPNN comparison set",
              ("Held-out proteins with no homologue in the training sets directly test generalisation to unseen proteins, the validation step the use case asks about."
               if k in ("megascale", "fireprot") else
               "Mostly values compiled from earlier papers, useful as context but not a fresh matched comparison; S669 duplicates Pancotti et al. 2022."),
              B_LIMS[k], [(B, f"Table {'2' if order < 3 else '3'} and footnotes; Methods 'Datasets'")],
              "dieckhaus2024-thermompnn", "ThermoMPNN comparison sets (Dieckhaus et al. 2024)", "pearson-correlation",
              stratum=B_NAMES[k], order=order)

# =============================================================================================
# C. Chu et al. 2024, PLOS Computational Biology 20(7):e1012248, Table 1 (per-dataset Spearman)
# =============================================================================================
C = source(f"{P}-source-chu2024", "Protein stability prediction by fine-tuning a protein language model on a mega-scale dataset",
           "10.1371/journal.pcbi.1012248", "PMC11293664", "PLOS Computational Biology 20(7):e1012248, published 2024-07-22; PMC11293664 full-text XML",
           "2026-10-09T21:01:08Z", ARTIFACTS["chu2024-article.xml"], "CC-BY-4.0")
C_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11293664/fullTextXML"
C_SHA = ARTIFACTS["chu2024-article.xml"]
twc, rowsc = table(os.path.join(PINNED, "chu2024-article.xml"), "pcbi.1012248.t001")
assert tx(twc.find("caption")).startswith("Comparison of Spearman’s R across methods on individual DMS datasets.")
assert rowsc[0] == ["Dataset", "Length", "Supervised Prediction", "Unsupervised Prediction"], rowsc[0]
assert rowsc[1] == ["Rosetta", "MUPro", "RaSP", "ELASPIC-2", "ESM therm", "ESM-2 (35M)", "ESM-2 (3B)"], rowsc[1]
twc2, rowsc2 = table(os.path.join(PINNED, "chu2024-article.xml"), "pcbi.1012248.t002")
assert rowsc2[0] == ["Dataset name", "Protein name", "Protein length", "Measured quantity", "No. of sequences"], rowsc2[0]
C_META = {r[0].split(" [")[0]: {"protein": r[1], "length": r[2], "quantity": r[3], "n": r[4]} for r in rowsc2[1:]}
C_TOOLS = rowsc[1]
C_SUPERVISED = {"Rosetta", "MUPro", "RaSP", "ELASPIC-2", "ESM therm"}
C_OWN = {"ESM therm"}
C_CONF = {}
for tool in C_TOOLS:
    attrs = {"source_locator": "Table 1 column header; Results 'Benchmarking on larger proteins'",
             "protocol": ("Fine-tuned by the authors on the mega-scale dataset (35M ESM-2 backbone)" if tool == "ESM therm"
                          else "Published model or software, scored by the authors" if tool in C_SUPERVISED
                          else "Pretrained ESM-2 likelihood used without supervision"),
             "missing_metadata": {"version": {"reason": "unreported", "note": "No release number printed"}}}
    extra = [{"relation": "uses_model", "target_id": EXISTING["esm-2"]}] if tool == "ESM therm" else None
    label = tool if not tool.startswith("ESM-2 (") else tool
    C_CONF[tool] = config(f"{P}-config-chu2024-{slug(tool)}", label, "Chu et al. 2024", [C], attrs, extra)
C_LIMS_COMMON = ["ESM therm was fine-tuned by the authors of this paper; the other methods were run by them as comparators.",
                 "Only Spearman correlation is printed; no RMSE, calibration or uncertainty.",
                 "Rosetta was run on only six ProteinGym datasets plus BglB because of compute cost (Methods)."]
c_order = 0
for r in rowsc[2:]:
    name = r[0]
    assert len(r) == 9, r
    meta = C_META[name]
    assert meta["protein"] is not None
    c_order += 1
    key = slug(name.replace(" dataset", ""))
    did = rec(f"{P}-data-chu2024-{key}", "dataset", f"{name}: {meta['protein']}, {meta['quantity']}",
              "Stability-related DMS set benchmarked in Chu et al. 2024.", [C], [],
              {"population": f"{meta['n']} sequences; protein length {meta['length']}",
               "assay": meta["quantity"], "split": "Test-set-only protein domains" if key == "mega-scale" else "Whole dataset",
               "source_locator": "Table 2; Methods",
               "missing_metadata": {"version": {"reason": "unreported"}}})["id"]
    pid = f"{P}-protocol-chu2024-{key}"
    lims = list(C_LIMS_COMMON)
    if key == "mega-scale":
        lims.append("Point mutations only for every method except the authors' own model, which also saw multi-point variants on this set (Table 1 caption).")
        lims.append("Metrics are aggregated over test-set-only domains of 40-72 residues, the same assay the model was trained on.")
    else:
        lims.append(f"Single protein ({meta['protein']}, {meta['length']} residues); the measured quantity is {meta['quantity']}, not ddG of folding.")
        lims.append("ESM therm was fine-tuned on domains of at most 72 residues, so this is an out-of-range test for it.")
    rec(pid, "protocol", f"{name} stability ranking, Spearman correlation (Chu et al. 2024 Table 1)",
        f"Spearman correlation between predicted and measured values for seven methods on {name}.", [C],
        [{"relation": "uses_data", "target_id": did}],
        {"protocol": f"Each method scores the variants and Spearman correlation is computed against the measured {meta['quantity']}.",
         "version": "Table 1", "metric": "spearman-correlation", "limitations": lims,
         "source_locator": f"Table 1, row '{name}'; Table 2"})
    for i, tool in enumerate(C_TOOLS):
        cell = r[2 + i]
        eid = f"{P}-eval-chu2024-{slug(tool)}-{key}"
        evaluation(eid, f"{tool} on {name} (Chu et al. 2024)", C_CONF[tool], pid, did, [C],
                   "author_reported" if tool in C_OWN else "independent_paper",
                   {"dataset_version": None, "split": "Test-set-only domains" if key == "mega-scale" else "Whole dataset",
                    "population": f"{meta['n']} sequences", "inputs": "Protein sequence and the variant", "adaptation": None,
                    "metric_implementation": "Spearman correlation", "aggregation": "Pooled over variants, or mean over domains for the mega-scale set",
                    "budget": None},
                   f"Table 1, row '{name}', column '{tool}'", missing={"comparison.dataset_version": {"reason": "unreported"}})
        result(f"{P}-result-chu2024-{slug(tool)}-{key}-spearman-correlation", eid, [C], C_SHA, C_URL,
               f"Table 1, row '{name}', column '{tool}' ({'supervised' if tool in C_SUPERVISED else 'unsupervised'} group)",
               cell, "rho", f"{name}, {meta['quantity']}", HOW)
    rel = "direct" if key == "mega-scale" else "proxy"
    judgement(f"chu2024-{key}", pid, f"{name} stability ranking (Chu et al. 2024)", [C], rel,
              f"Spearman correlation for Rosetta, MUPro, RaSP, ELASPIC-2, ESM therm and two ESM-2 checkpoints on {name}",
              ("Held-out protein domains from the cDNA display proteolysis set directly measure how well each method ranks substitutions by folding stability."
               if key == "mega-scale" else
               f"Measures ranking against {meta['quantity']} in a single larger protein, which is a proxy for folding stability and shows how methods transfer beyond small domains."),
              lims, [(C, f"Table 1 row '{name}'; Table 2; Results")],
              "chu2024-transfer", "Transfer from mega-scale domains to larger proteins (Chu et al. 2024)", "spearman-correlation",
              stratum=f"{meta['protein']} ({meta['quantity']})" if key != "mega-scale" else "Mega-scale held-out domains", order=c_order)

# ---------------------------------------------------------------------------------------------
ids = [r["id"] for r in records]
assert len(ids) == len(set(ids)), [i for i, c in Counter(ids).items() if c > 1]
os.makedirs(BATCH, exist_ok=True)
records.sort(key=lambda r: r["id"])
with open(os.path.join(BATCH, "batch.jsonl"), "w") as f:
    for r in records:
        f.write(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n")
claims_rows.sort()
with open(os.path.join(BATCH, "claims.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["record_id", "source_id", "locator", "printed_value", "review_scope"])
    w.writerows(claims_rows)
print(Counter(r["kind"] for r in records))
