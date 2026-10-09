"""Deterministic extraction of precision-oncology evidence comparisons into a records batch.

Usage: python3 -I extract_egfr_nsclc.py <download-dir> <batch-dir>

Reads the pinned sources and asserts every row and column label it depends on:
  - Lin et al. 2025 (npj Precision Oncology) Tables 1 and 2, from the article JATS XML
  - Roberts et al. 2020, Overview of the TREC 2020 Precision Medicine Track, Tables 5 and 6,
    from the PDF text layer (pdftotext -layout output passed as <download-dir>/trec2020-overview/ov.txt)
  - TREC 2020 PM topics file, and run descriptions from the NIST trec-browser repository at a pinned commit
Writes batch.jsonl and claims.csv in the store form.
"""
import csv, hashlib, json, os, re, sys
import xml.etree.ElementTree as ET
from decimal import Decimal

DL, BATCH = sys.argv[1], sys.argv[2]
P = "egfrnsclc-20261009"
UC = "use-case-egfr-nsclc-actionability-resistance-evidence"
DATE = "2026-10-09"
FACETS = {"areas": ["dna-genomes"], "contexts": ["clinical_research"]}
TB_COMMIT = "75ec9339eac60126b1045e5858a5ac874ea54a51"
records, claim_rows = [], []


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def expect(got, value, where):
    if got != value:
        raise SystemExit(f"{where}: expected {value!r}, found {got!r}")


def rec(id_, kind, name, description, source_ids, links=None, attributes=None, facets=None, status="needs_review"):
    r = {"id": id_, "kind": kind, "name": name, "description": description, "status": status,
         "facets": FACETS if facets is None else facets, "source_ids": source_ids,
         "links": links or [], "attributes": attributes or {}}
    records.append(r)
    return r


def source(id_, name, url, artifact_url, version, retrieved_at, path, status, media_type, doi=None, licence=None, extra=None):
    attrs = {"url": url, "artifact_url": artifact_url, "version": version, "retrieved_at": retrieved_at,
             "artifact_sha256": sha(path), "publication_status": status, "media_type": media_type,
             "source_locator": "Full artifact bytes; per-record locators on each record"}
    if doi:
        attrs["doi"] = doi
    if licence:
        attrs["licence"] = licence
    else:
        attrs["missing_metadata"] = {"licence": {"reason": "unreported", "note": "No licence statement in the retrieved artifact"}}
    attrs.update(extra or {})
    rec(id_, "source", name, "Primary source retrieved and hashed for the EGFR NSCLC evidence-retrieval use-case pass.", [], attributes=attrs)


LIN_XML = f"{DL}/lin2025/PMC12078457.xml"
OV_PDF = f"{DL}/trec2020-overview/OVERVIEW.PM.pdf"
OV_TXT = f"{DL}/trec2020-overview/ov.txt"
TOPICS = f"{DL}/trec29/topics2020.xml"
RUNS = f"{DL}/trecbrowser/runs.md"
S_LIN = f"{P}-source-lin2025"
S_OV = f"{P}-source-trec2020-pm-overview"
S_TOP = f"{P}-source-trec2020-pm-topics"
S_RUNS = f"{P}-source-trec-browser-pm2020-runs"
LIN_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12078457/fullTextXML"
OV_URL = "https://trec.nist.gov/pubs/trec29/papers/OVERVIEW.PM.pdf"

source(S_LIN, "Benchmarking large language models GPT-4o, llama 3.1, and qwen 2.5 for cancer genetic variant classification",
       "https://doi.org/10.1038/s41698-025-00935-4", LIN_URL,
       "npj Precision Oncology 9:141, published 2025-05-15; PMC12078457 full-text XML", "2026-10-09T20:43:36Z", LIN_XML,
       "peer_reviewed", "application/xml", doi="10.1038/s41698-025-00935-4", licence="CC-BY-NC-ND-4.0",
       extra={"archive_note": "Not archived: CC BY-NC-ND 4.0; the hash pins the bytes read."})
source(S_OV, "Overview of the TREC 2020 Precision Medicine Track",
       OV_URL, OV_URL, "Proceedings of the Twenty-Ninth Text REtrieval Conference (TREC 2020), NIST Special Publication 1266; 10-page PDF",
       "2026-10-09T20:41:38Z", OV_PDF, "official_project_source", "application/pdf",
       extra={"archive_note": "Not archived: no licence statement in the PDF; the hash pins the bytes read."})
source(S_TOP, "TREC 2020 Precision Medicine topics", "https://trec.nist.gov/data/precmed2020.html",
       "https://trec.nist.gov/data/precmed/topics2020.xml", "topics2020.xml as served on 2026-10-09 (40 topics)",
       "2026-10-09T20:40:57Z", TOPICS, "official_project_source", "application/xml",
       extra={"scope_note": "Mutable web resource; the hash describes one retrieval."})
source(S_RUNS, "NIST TREC Browser, Precision Medicine 2020 runs page",
       f"https://github.com/usnistgov/trec-browser/blob/{TB_COMMIT}/browser/src/docs/trec29/pm/runs.md",
       f"https://api.github.com/repos/usnistgov/trec-browser/contents/browser/src/docs/trec29/pm/runs.md?ref={TB_COMMIT}",
       f"usnistgov/trec-browser commit {TB_COMMIT}", "2026-10-09T20:41:00Z", RUNS, "official_project_source", "text/markdown",
       extra={"retrieval_method": "GitHub contents API at the pinned commit, base64-decoded",
              "scope_note": "Run metadata (participant, type, submission date, run description) for each TREC 2020 PM run. The repository README says 'The database will be available under an academic, non-commercial license'; no licence file was found for runs.md."})


def review_note(path, url, how):
    return {"method": ["deterministic-table-parse"], "reviewer": ["claude"], "date": DATE,
            "reviewer_note": "Claude (Opus 5.5) extraction agent; extraction record, not an independent review",
            "artifact_sha256": sha(path), "retrieval_url": url, "note": how + " Pending independent review."}


def result(id_, eval_id, source_ids, locator, pv, metric, qualifier, unit, review, uncertainty=None, extra=None):
    attrs = {"metric": metric, "metric_qualifier": qualifier, "metric_direction": "higher", "unit": unit,
             "printed_value": pv, "numeric_value": format(Decimal(pv), "f"), "source_locator": locator, "review": review}
    if uncertainty:
        attrs["uncertainty"] = uncertainty
    else:
        attrs["missing_metadata"] = {"uncertainty": {"reason": "unreported"}}
    attrs.update(extra or {})
    rec(id_, "result", f"{eval_id.replace(P + '-eval-', '')} {metric} ({qualifier})",
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


# ================================================================ Lin et al. 2025
txt = lambda e: " ".join("".join(e.itertext()).split())
lin = ET.parse(LIN_XML).getroot()
tabs = {tw.get("id"): [[txt(c) for c in tr] for tr in tw.iter("tr")] for tw in lin.iter("table-wrap")}
t1, t2 = tabs["Tab1"], tabs["Tab2"]
expect(t1[0], ["", "GPT-4o", "Llama 3", "Qwen 2.5", ""], "Lin Table 1 header row 1")
expect(t1[1], ["", "Mean accuracy", "95% CI", "Mean accuracy", "95% CI", "Mean accuracy", "95% CI", "p value"], "Lin Table 1 header row 2")
expect([r[0] for r in t1[2:]], ["Foundationone", "OncoKB", "CIViC"], "Lin Table 1 rows")
expect(t2[0], ["Model", "Model conditions", "Dataset", "Accuracy", "Best-in- group"], "Lin Table 2 header")
expect(len(t2), 12, "Lin Table 2 rows")

LIN_LOC = "Lin et al. 2025 Methods 'Dataset' (P35-P38), 'Model selection' (P39-P40), 'System prompts' (P41-P43), 'Testing framework design' (P44-P47)"
D = {"foundationone": f"{P}-data-lin2025-foundationone-variants", "oncokb": f"{P}-data-lin2025-oncokb-associations",
     "civic": f"{P}-data-lin2025-civic-associations"}
rec(D["foundationone"], "dataset", "FoundationOne CDx report variants, 612 patients (Lin et al. 2025)",
    "Real-world variants labelled clinically relevant or VUS by the FoundationOne CDx report section they appear in.", [S_LIN],
    attributes={"version": "Single-hospital FoundationOne CDx reports as used by Lin et al. 2025", "total": 10506, "positives": 5240,
                "negatives": 5266, "population": "10,506 genetic alterations from 612 patients: 5,240 clinically relevant (Genomic Findings) and 5,266 VUS (appendix)",
                "access": "Hospital data; not published", "private_data_not_included": True, "source_locator": LIN_LOC})
rec(D["oncokb"], "dataset", "OncoKB actionable-genes table, 625 variant-cancer-drug associations (accessed 2024-11-20)",
    "OncoKB levels of evidence used as the reference labels by Lin et al. 2025.", [S_LIN],
    attributes={"version": "OncoKB actionable genes table, last accessed 2024-11-20", "total": 625,
                "population": "625 associations: Level 1 182, Level 2 154, Level 3 114, Level 4 80, R1 34, R2 61",
                "access": "Downloaded by the authors from https://www.oncokb.org/actionable-genes (Methods P36); the table itself is not copied into this batch", "source_locator": "Lin et al. 2025 Methods P36"})
rec(D["civic"], "dataset", "CIViC clinical evidence summary, 4,426 variant-disease associations (accessed 2024-11-20)",
    "CIViC evidence levels used as the reference labels by Lin et al. 2025.", [S_LIN],
    attributes={"version": "CIViC Clinical Evidence Summary download, last accessed 2024-11-20", "total": 4426,
                "population": "4,426 associations: level A 166, B 1,465, C 1,547, D 1,216, E 32",
                "source_locator": "Lin et al. 2025 Methods P37"})
PR = {"foundationone": f"{P}-protocol-lin2025-foundationone-relevant-vs-vus", "oncokb": f"{P}-protocol-lin2025-oncokb-level-assignment",
      "civic": f"{P}-protocol-lin2025-civic-level-assignment"}
LIN_LIM = ["Pan-cancer variant set; no EGFR- or NSCLC-specific score is reported.",
           "The model assigns an evidence level from gene, alteration and tumour type alone; no prior therapy, line or evidence date is given and no source is cited.",
           "Public OncoKB and CIViC tables may be in the models' training data (Discussion P33)."]
for key, name, task, ref in (
        ("foundationone", "Lin et al. 2025 FoundationOne variants: clinically relevant vs VUS",
         "Ask each LLM to classify a gene, alteration and tumour type with the CIViC level-of-evidence system (A-E or VUS); levels A-E count as clinically relevant. Score against the report section.",
         "FoundationOne CDx report section"),
        ("oncokb", "Lin et al. 2025 OncoKB level-of-evidence assignment",
         "Ask each LLM to assign the OncoKB level (1, 2, 3, 4, R1, R2 or VUS) for each gene, alteration and cancer type of the OncoKB actionable-genes table.",
         "OncoKB level in the actionable-genes table"),
        ("civic", "Lin et al. 2025 CIViC evidence-level assignment",
         "Ask each LLM to assign the CIViC evidence level (A-E or VUS) for each molecular profile and disease of the CIViC clinical evidence summary.",
         "CIViC evidence level")):
    rec(PR[key], "protocol", name, "LLM evidence-level classification task from Lin et al. 2025.", [S_LIN],
        [{"relation": "uses_data", "target_id": D[key]}],
        {"protocol": task + f" Reference: {ref}. Score the top-1 answer (up to three levels may be returned); repeat each query 100 times for basic prompts and 10 times for other settings; report mean accuracy.",
         "version": "Lin et al. 2025 Methods", "metric": "top-1-accuracy", "metric_direction": "higher",
         "limitations": LIN_LIM, "source_locator": LIN_LOC + "; Tables 1-2"})

MODELS = {"gpt-4o": ("GPT-4o", "service", "Proprietary model used through the Azure OpenAI API, version 2024-05-13"),
          "llama-3-1-70b": ("Llama 3.1 70B", "checkpoint", "Open-weight model served with Ollama"),
          "qwen-2-5-72b": ("Qwen 2.5 72B", "checkpoint", "Open-weight model served with Ollama")}
MID = {}
for k, (name, level, desc) in MODELS.items():
    MID[k] = f"{P}-model-{k}"
    rec(MID[k], "model", name, desc + " (as used by Lin et al. 2025).", [S_LIN],
        attributes={"entity_level": level, "reported_name": name, "source_locator": "Lin et al. 2025 Methods P39-P40, P46, P48",
                    "missing_metadata": {"checkpoint_revision": {"reason": "unreported"}, "training_data": {"reason": "unreported"}}},
        facets={**FACETS})
CFG = {}
def lin_cfg(key, model, label, prompt, temp, extra_note=None):
    CFG[key] = f"{P}-config-lin2025-{key}"
    attrs = {"reported_name": label, "foundation_model_eligible": True, "source_locator": "Lin et al. 2025 Methods P39-P43; Table 2 'Model conditions'",
             "parameters": f"{prompt}; temperature {temp}" + (f"; {extra_note}" if extra_note else "")}
    if model == "gpt-4o":
        attrs["version"] = "2024-05-13 (Azure OpenAI)"
    else:
        attrs["missing_metadata"] = {"version": {"reason": "unreported", "note": "Model size is printed (70B or 72B); no checkpoint tag or quantisation is printed"}}
    rec(CFG[key], "configuration", f"{MODELS[model][0]}, {prompt}, temperature {temp} (Lin et al. 2025)",
        "Configuration as run in the cited comparison.", [S_LIN], [{"relation": "configuration_of", "target_id": MID[model]}], attrs,
        facets={**FACETS, "method_types": ["foundation_model"]})
lin_cfg("gpt-4o-basic", "gpt-4o", "GPT-4o", "basic prompt", "1.0 (default)")
lin_cfg("llama-basic-t0-8", "llama-3-1-70b", "Llama 3.1", "basic prompt", "0.8 (default)",
        "Table 1 header prints 'Llama 3'; Methods and Table 2 print 'Llama 3.1 (70B)'")
lin_cfg("llama-basic-t0-4", "llama-3-1-70b", "Llama 3.1", "basic prompt", "0.4")
lin_cfg("llama-basic-t0", "llama-3-1-70b", "Llama 3.1", "basic prompt", "0")
lin_cfg("qwen-basic", "qwen-2-5-72b", "Qwen2.5", "basic prompt", "0.8 (default)")
lin_cfg("qwen-refined", "qwen-2-5-72b", "Qwen2.5", "refined prompt", "0.8 (default)")
lin_cfg("qwen-binary", "qwen-2-5-72b", "Qwen2.5", "binary class prompt", "0.8 (default)")
lin_cfg("qwen-rag", "qwen-2-5-72b", "Qwen2.5", "RAG with basic prompt", "0.8 (default)",
        "retrieval corpus and retriever are described in Methods P49-P50 without a version")

lin_review = review_note(LIN_XML, LIN_URL, "Extracted by deterministic parse of the article JATS XML tables Tab1 and Tab2 "
                         "(extract/extract_egfr_nsclc.py) with header and row labels asserted.")
DSNAME = {"Foundationone": "foundationone", "FoundationOne": "foundationone", "OncoKB": "oncokb", "CIViC": "civic"}
QUAL = {"foundationone": "clinically relevant vs VUS via CIViC levels; mean over iterations",
        "oncokb": "OncoKB level of evidence; mean over iterations", "civic": "CIViC evidence level; mean over iterations"}
EVS = {}
def lin_eval(cfg, ds, iters, loc):
    key = (cfg, ds)
    if key not in EVS:
        EVS[key] = f"{P}-eval-lin2025-{cfg}-{ds}"
        evaluation(EVS[key], f"{cfg} on {ds} (Lin et al. 2025)", CFG[cfg], PR[ds], D[ds], [S_LIN], "independent_paper",
                   {"dataset_version": D[ds], "split": "Whole table; no training split (prompted models)", "population": QUAL[ds].split(";")[0],
                    "inputs": "Gene, alteration and tumour type as a natural-language query", "adaptation": "Prompting only" if "rag" not in cfg else "Retrieval-augmented prompting",
                    "metric_implementation": "Top-1 answer compared with the reference level", "aggregation": f"Mean over {iters} iterations", "budget": None},
                   loc)
    return EVS[key]

cols = {"gpt-4o-basic": (1, 2), "llama-basic-t0-8": (3, 4), "qwen-basic": (5, 6)}
for row in t1[2:]:
    ds = DSNAME[row[0]]
    for cfg, (vc, cc) in cols.items():
        ev = lin_eval(cfg, ds, 100, f"Table 1 row '{row[0]}', columns for {t1[0][[1, 2, 3][list(cols).index(cfg)]]}")
        lo, hi = row[cc].split("–")
        result(f"{P}-result-lin2025-{cfg}-{ds}-top1", ev, [S_LIN],
               f"Table 1 (Tab1), row '{row[0]}', column '{t1[0][[1, 2, 3][list(cols).index(cfg)]]}' Mean accuracy; 95% CI in the next column",
               row[vc], "top-1-accuracy", QUAL[ds], "fraction", lin_review,
               {"type": "confidence_interval", "lower": lo, "upper": hi, "level": 0.95, "printed": row[cc]},
               extra={"reported_p_value": f"{row[7]} (test across the three models, as printed in the row's 'p value' column)"})
COND = {"Basic prompt + Default temperature (0.8)": {"Qwen2.5": "qwen-basic", "Llama 3.1": "llama-basic-t0-8"},
        "Refined prompt + Default temperature (0.8)": {"Qwen2.5": "qwen-refined"},
        "Binary class prompt + Default temperature (0.8)": {"Qwen2.5": "qwen-binary"},
        "RAG + Default temperature (0.8)": {"Qwen2.5": "qwen-rag"},
        "Basic prompt + temperature (0.4)": {"Llama 3.1": "llama-basic-t0-4"},
        "Basic prompt + temperature (0)": {"Llama 3.1": "llama-basic-t0"}}
t1_values = {(DSNAME[r[0]], cfg): r[vc] for r in t1[2:] for cfg, (vc, _) in cols.items()}
for i, row in enumerate(t2[1:], start=1):
    model, cond, dsl, acc, best = row
    cfg = COND[cond][model]
    ds = DSNAME[dsl]
    loc = f"Table 2 (Tab2), row {i} ('{model}', '{cond}', '{dsl}'), column 'Accuracy'"
    if (ds, cfg) in t1_values:
        expect(acc, t1_values[(ds, cfg)], f"Table 2 row {i} repeats Table 1")
        claim_rows.append([f"{P}-result-lin2025-{cfg}-{ds}-top1", S_LIN, loc + " (same value as Table 1; not recorded twice)", acc, "result-duplicate"])
        continue
    ev = lin_eval(cfg, ds, 10, loc)
    result(f"{P}-result-lin2025-{cfg}-{ds}-top1", ev, [S_LIN], loc, acc, "top-1-accuracy", QUAL[ds].replace("over iterations", "over 10 iterations"),
           "fraction", lin_review, extra={"scope_note": "Marked best in its model and dataset group in Table 2." if best else "Not marked best in its model and dataset group in Table 2."})

claim(f"{P}-claim-lin2025-query-example", PR["oncokb"], "query_format",
      "Queries were generated from gene, alteration and tumour type, for example: 'Given the gene EGFR, with alteration L858R in the context of non-small cell lung cancer, what is the appropriate classification?'",
      [S_LIN], "Methods 'Testing framework design' (P44-P45)", LIN_XML, LIN_URL)

# ================================================================ TREC 2020 PM overview
ov = open(OV_TXT, encoding="utf-8").read()
lines = ov.splitlines()
def find(text):
    idx = [i for i, l in enumerate(lines) if l.strip() == text]
    if len(idx) != 1:
        raise SystemExit(f"Overview: {text!r} found {len(idx)} times")
    return idx[0]
i5 = find("Table 5: Top overall systems in Phase 1 (best run per team).")
i6 = find("Table 6: Top overall systems in Phase 2 (best run per team).")
ROW = re.compile(r"^\s{2,}(?P<team>\S.*?)\s{2,}(?P<run>\S.*?)\s{2,}(?P<v>0\.\d{4})$")
def block(start, end):
    out, metric = [], None
    for l in lines[start:end]:
        s = l.strip()
        if not s:
            continue
        m = ROW.match(l)
        if m:
            out.append((metric, m.group("team"), m.group("run"), m.group("v")))
        elif s in ("Team Run infNDCG",) or re.fullmatch(r"Team\s+Run\s+infNDCG", s):
            metric = "infNDCG"
        elif s in ("R-prec", "P@10", "std-gains", "exp-gains", "NDCG@30"):
            metric = {"NDCG@30": metric}.get(s, s)
        elif re.fullmatch(r"Team\s+Run\s+std-gains", s):
            metric = "std-gains"
        else:
            raise SystemExit(f"Overview table line not understood: {l!r}")
    return out
hdr5 = [i for i in range(i5 - 25, i5) if re.fullmatch(r"\s*Team\s+Run\s+infNDCG\s*", lines[i])]
hdr6 = [i for i in range(i5 + 1, i6) if lines[i].strip() == "NDCG@30"]
if len(hdr5) != 1 or len(hdr6) != 2:
    raise SystemExit("Overview table headers not found as expected")
PAGE = {"Table 5": ov[:ov.index(lines[i5])].count("\f") + 1, "Table 6": ov[:ov.index(lines[i6])].count("\f") + 1}
rows5 = block(hdr5[0], i5)
rows6 = block(hdr6[0], i6)
expect([m for m, *_ in rows5], ["infNDCG"] * 5 + ["R-prec"] * 5 + ["P@10"] * 5, "Table 5 metric blocks")
expect([m for m, *_ in rows6], ["std-gains"] * 5 + ["exp-gains"] * 5, "Table 6 metric blocks")

runs_md = open(RUNS, encoding="utf-8").read()
RUN = {}
for b in re.split(r"\n#### ", runs_md)[1:]:
    name = b.split("\n")[0].strip()
    RUN[name] = {"participant": re.search(r"\*\*Participant:\*\* (.*?) \n", b).group(1),
                 "type": re.search(r"\*\*Type:\*\* (.*?) \n", b).group(1),
                 "md5": re.search(r"MD5:\*\* `(.*?)`", b).group(1),
                 "desc": re.search(r"\*\*Run description:\*\* (.*?)\n", b).group(1).strip()}
expect(len(RUN), 66, "TREC browser run count")

topics = ET.parse(TOPICS).getroot()
expect(len(topics), 40, "TREC 2020 PM topic count")
egfr = [(t.get("number"), t.findtext("disease"), t.findtext("gene"), t.findtext("treatment")) for t in topics if t.findtext("gene") == "EGFR"]
expect(egfr, [("15", "non-small cell lung cancer", "EGFR", "Afatinib"), ("16", "non-small cell lung cancer", "EGFR", "Osimertinib")], "EGFR topics")

D_TREC = f"{P}-data-trec2020-pm-topics-medline"
rec(D_TREC, "dataset", "TREC 2020 Precision Medicine: 40 cancer-gene-treatment topics over a 2019 MEDLINE baseline snapshot",
    "Topics and pooled relevance and evidence judgements of the TREC 2020 Precision Medicine track.", [S_OV, S_TOP],
    attributes={"version": "TREC 2020 PM (MEDLINE baseline snapshot of the 2019 track)", "total": 40,
                "population": ("40 topics, each a cancer, a gene and a treatment; topics 15 and 16 are EGFR-mutant non-small cell lung cancer with "
                               "afatinib and osimertinib. 22,806 Phase 1 relevance judgements and 2,691 Phase 2 evidence judgements; runs were "
                               "scored on 31 topics."),
                "scope_note": "Topics give no prior therapy, line of treatment or resistance context.",
                "source_locator": "Overview sections 3-6 and Table 3; topics2020.xml topics 15-16; run appendix PDFs list 31 topics"})
claim(f"{P}-claim-trec2020-egfr-topic-judgements", D_TREC, "egfr_topic_judgements",
      "Topic 15 (non-small cell lung cancer, EGFR, afatinib): 226 Definitely Relevant, 94 Partially Relevant, 252 Not Relevant. Topic 16 (non-small cell lung cancer, EGFR, osimertinib): 182, 44 and 302.",
      [S_OV, S_TOP], "Overview Table 3, rows for topics 15 and 16; topics2020.xml", OV_PDF, OV_URL)

PRT = {1: f"{P}-protocol-trec2020-pm-phase1-relevance", 2: f"{P}-protocol-trec2020-pm-phase2-evidence"}
TREC_LIM = ["Pan-cancer topics; per-topic scores (including the two EGFR topics) are shown only as figures in the run appendices.",
            "The overview prints only the best run per team for the top five teams per metric.",
            "Topics carry no prior therapy, line or resistance context; the 2019 MEDLINE snapshot is not current evidence.",
            "Each document was judged once; no inter-rater agreement is available (Overview section 6)."]
rec(PRT[1], "protocol", "TREC 2020 PM Phase 1: topical relevance of retrieved MEDLINE abstracts",
    "Rank MEDLINE abstracts for each cancer-gene-treatment topic; score against Phase 1 relevance judgements.", [S_OV, S_TOP],
    [{"relation": "uses_data", "target_id": D_TREC}],
    {"protocol": ("Systems return ranked MEDLINE abstracts for each topic. Judges map disease, gene and treatment matches to Definitely "
                  "Relevant (gain 2), Partially Relevant (1) or Not Relevant (0). Metrics: infNDCG (sample-eval), R-precision and P@10, "
                  "averaged over topics."),
     "version": "TREC 2020 PM overview sections 5.1-5.2", "metric": "ndcg", "metric_direction": "higher",
     "limitations": TREC_LIM, "source_locator": "Overview sections 5.1-5.2 and Table 5"})
rec(PRT[2], "protocol", "TREC 2020 PM Phase 2: evidence-tier-weighted ranking of retrieved abstracts",
    "Score rankings by topic-specific evidence tiers (strong positive or negative evidence ranked above weak evidence).", [S_OV, S_TOP],
    [{"relation": "uses_data", "target_id": D_TREC}],
    {"protocol": ("Judges re-grade up to 100 relevant abstracts per topic on a topic-specific 4-tier evidence scale; conclusive positive and "
                  "negative results are weighted equally. Metric: NDCG@30 with standard gains {0,1,2,3,4} or exponential gains {0,1,2,4,8}."),
     "version": "TREC 2020 PM overview section 5.3", "metric": "ndcg", "metric_direction": "higher",
     "limitations": TREC_LIM, "source_locator": "Overview section 5.3, Table 2 and Table 6"})

TEAMS = {}
def team_method(team):
    k = re.sub(r"[^a-z0-9]+", "-", team.lower()).strip("-")
    if k not in TEAMS:
        TEAMS[k] = f"{P}-method-trec2020-pm-{k}"
        rec(TEAMS[k], "method", f"TREC 2020 PM system of team {team}", f"Retrieval system family submitted by {team} to the TREC 2020 Precision Medicine track.",
            [S_OV, S_RUNS], attributes={"reported_name": team, "entity_level": "method", "source_locator": "Overview Table 4; TREC browser runs page",
                                        "missing_metadata": {"version": {"reason": "inapplicable", "note": "Team-level family; runs are configurations"}}},
            facets={**FACETS, "method_types": ["conventional_pipeline"]})
    return TEAMS[k]
TCFG = {}
def run_cfg(team, printed):
    run = printed.replace(" ", "_")
    key = re.sub(r"[^a-z0-9]+", "-", run.lower()).strip("-")
    if key in TCFG:
        return TCFG[key], run
    TCFG[key] = f"{P}-config-trec2020-pm-{key}"
    extra = {"source_label": printed}
    if run in RUN:
        r = RUN[run]
        expect(r["participant"].replace("_", " "), team, f"participant of {run}")
        extra.update({"parameters": f"Run type: {r['type']}. Run description as submitted: {r['desc']}",
                      "source_identity": {"run_id": run, "run_file_md5": r["md5"], "listed_in": "TREC browser runs page"}})
        locator = f"Overview Tables 5-6; TREC browser runs page, run {run}"
        mt = ["supervised_machine_learning"] if re.search(r"BERT|T5|learning|biobert", r["desc"], re.I) else ["conventional_pipeline"]
    else:
        extra["model_identity_note"] = (f"Printed as '{printed}' in Overview Table 5. No run of that name is listed among the 66 runs of the TREC browser; "
                                        "its printed P@10 (0.5484) equals the P_10 listed for run uog_ufmg_sb_df5 of the same team. Not merged with that run.")
        locator = "Overview Table 5"
        mt = ["supervised_machine_learning"]
    rec(TCFG[key], "configuration", f"TREC 2020 PM run {run} ({team})", "Submitted run as evaluated by the track.", [S_OV, S_RUNS],
        [{"relation": "configuration_of", "target_id": team_method(team)}],
        {"reported_name": run, "foundation_model_eligible": False, "source_locator": locator,
         "missing_metadata": {"version": {"reason": "inapplicable", "note": "A submitted run is a fixed artifact; its MD5 is recorded where listed"}}, **extra},
        facets={**FACETS, "method_types": mt})
    if run in RUN and RUN[run]["type"] == "manual":
        records[-1]["attributes"]["limitations"] = ["Manual run: human input in query formulation or relevance feedback (TREC browser run type)."]
    return TCFG[key], run

ov_review = review_note(OV_PDF, OV_URL, "Extracted by deterministic parse of the PDF text layer (pdftotext -layout) of Tables 5 and 6, "
                        "with table captions, metric sub-headers and five rows per block asserted; run names printed with spaces were "
                        "matched to TREC browser run IDs with underscores.")
METRIC = {"infNDCG": ("ndcg", "inferred NDCG (sample-eval), Phase 1 relevance gains, mean over topics"),
          "R-prec": ("r-precision", "Phase 1 relevance, mean over topics"),
          "P@10": ("precision-at-10", "Phase 1 relevance, mean over topics"),
          "std-gains": ("ndcg", "NDCG@30, Phase 2 evidence tiers, standard gains {0,1,2,3,4}, mean over topics"),
          "exp-gains": ("ndcg", "NDCG@30, Phase 2 evidence tiers, exponential gains {0,1,2,4,8}, mean over topics")}
TEV = {}
for phase, rows, tab in ((1, rows5, "Table 5"), (2, rows6, "Table 6")):
    for rank, (m, team, printed, v) in enumerate(rows):
        cfg, run = run_cfg(team, printed)
        ek = (cfg, phase)
        if ek not in TEV:
            TEV[ek] = f"{P}-eval-trec2020-pm-phase{phase}-{cfg.split('-config-trec2020-pm-')[1]}"
            lim = ["Scores computed by the track organisers on runs submitted by the participating team; the overview authors did not build the system."]
            evaluation(TEV[ek], f"{run} ({team}), TREC 2020 PM Phase {phase}", cfg, PRT[phase], D_TREC, [S_OV, S_RUNS], "independent_paper",
                       {"dataset_version": "TREC 2020 PM qrels", "split": "Single evaluation round (no training split)",
                        "population": "Topics with judged documents (31 of 40)", "inputs": "Topic disease, gene and treatment fields",
                        "adaptation": None, "metric_implementation": "trec_eval and sample_eval (Phase 1); NDCG@30 (Phase 2)",
                        "aggregation": "Mean over topics", "budget": None},
                       f"Overview {tab}", limitations=lim)
        metric, qual = METRIC[m]
        result(f"{P}-result-trec2020-pm-{cfg.split('-config-trec2020-pm-')[1]}-{m.lower().replace('@', '').replace('-', '')}",
               TEV[ek], [S_OV, S_RUNS], f"Overview {tab} (PDF page {PAGE[tab]}), block '{m}', row {rank % 5 + 1}: team '{team}', run '{printed}'",
               v, metric, qual, "unitless", ov_review,
               extra={"scope_note": "Listed as one of the top five teams (best run per team) for this metric."})

# ================================================================ judgements
J = "use-case-mapping-egfr-nsclc-20261009"
CONSTRAINTS = ["Inspect every linked evaluation's source locator and preserved conflicts before citing a result.",
               "Do not combine this mapping's evaluations with any other protocol's results; tasks, reference standards and corpora differ."]
def judgement(short, protocol, endpoint, rationale, limitations, sources, cites, group, title, metric, label, order):
    rec(f"{J}-{short}", "claim", f"Relevance of {protocol} to \"EGFR NSCLC actionability and resistance evidence retrieval\"",
        rationale, sources, [{"relation": "subject", "target_id": UC}],
        {"field": f"links:assessed_by:{protocol}", "value": protocol, "relevance": "proxy", "endpoint": endpoint,
         "rationale": rationale, "constraints": CONSTRAINTS, "limitations": limitations,
         "citation_locators": [{"source_id": s, "locator": loc} for s, loc in cites],
         "source_locator": "; ".join(f"{s}: {loc}" for s, loc in cites), "revision": 1,
         "reason": "Add primary-source precision-oncology evidence comparisons from the EGFR NSCLC use-case pass 2026-10-09.",
         "comparison_group": group, "comparison_title": title, "headline_metric": metric,
         "stratum_label": label, "stratum_order": order}, facets={})

LIN_T = "LLMs assigning knowledge-base evidence levels (Lin et al. 2025)"
for order, (key, label, endpoint) in enumerate((
        ("foundationone", "FoundationOne variants: relevant vs VUS", "Top-1 accuracy of GPT-4o, Llama 3.1 and Qwen 2.5 (and Qwen prompt and RAG variants) in separating clinically relevant variants from VUS in 10,506 real-world report variants"),
        ("oncokb", "OncoKB levels 1-4, R1, R2", "Top-1 accuracy of GPT-4o, Llama 3.1 and Qwen 2.5 (and temperature and prompt variants) in assigning OncoKB levels, including resistance levels R1 and R2, to 625 OncoKB associations"),
        ("civic", "CIViC levels A-E", "Top-1 accuracy of GPT-4o, Llama 3.1 and Qwen 2.5 (and a refined Qwen prompt) in assigning CIViC evidence levels to 4,426 CIViC associations")), start=1):
    judgement(f"lin2025-{key}", PR[key], endpoint,
              "Measures whether systems return the knowledge base's native evidence level, including OncoKB resistance levels, for a variant in a tumour type, which is one element of correctly scoped evidence; it does not test source-linked retrieval, treatment history or contradictions, and it is pan-cancer.",
              LIN_LIM, [S_LIN], [(S_LIN, "Tables 1-2; Methods P35-P49; Discussion P33")], "lin2025-llm-evidence-levels", LIN_T,
              "top-1-accuracy", label, order)
TREC_T = "Precision-oncology literature retrieval systems (TREC 2020 Precision Medicine)"
judgement("trec2020-phase1", PRT[1], "infNDCG, R-precision and P@10 of the best run per team for the top five teams, ranking MEDLINE abstracts for 40 cancer-gene-treatment topics (two EGFR NSCLC topics)",
          "A multi-system evaluation of retrieving literature for a cancer, gene and treatment, the retrieval step of the use case, but pan-cancer, without treatment history or resistance context, and scored for topical relevance rather than evidence direction.",
          TREC_LIM, [S_OV, S_TOP], [(S_OV, "Sections 4-6, Tables 3-5"), (S_TOP, "Topics 15 and 16")], "trec2020-pm", TREC_T, "ndcg",
          "Phase 1: topical relevance", 1)
judgement("trec2020-phase2", PRT[2], "NDCG@30 with standard and exponential evidence-tier gains of the best run per team for the top five teams",
          "Scores whether systems rank the strongest positive or negative treatment evidence first, which bears on correctly scoped sensitivity and resistance evidence, but tiers are topic-specific, topics lack prior-therapy context and only top runs are printed.",
          TREC_LIM, [S_OV, S_TOP], [(S_OV, "Section 5.3, Tables 2 and 6"), (S_TOP, "Topics 15 and 16")], "trec2020-pm", TREC_T, "ndcg",
          "Phase 2: evidence tiers", 2)

records.sort(key=lambda r: r["id"])
ids = [r["id"] for r in records]
if len(ids) != len(set(ids)):
    raise SystemExit("Duplicate IDs")
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
