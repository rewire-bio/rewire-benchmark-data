"""Deterministic extraction of target-prioritisation comparisons into a records batch.

Usage: python3 -I extract_target_validation.py <download-dir> <batch-dir>

Reads three pinned PDFs through their text layers (pdftotext -layout output beside each PDF)
and asserts every row and column label it depends on:
  - Roohani et al. 2025 (ICLR, BioDiscoveryAgent) Table 1: 20 methods x 6 CRISPR screens x
    {all genes, non-essential genes}, hit ratio at round 5
  - Gupta et al. 2025 (EMNLP Findings) Tables 1 and 2: the same agent replicated, the agent given
    randomly permuted feedback, and classical designs, on 5 of the same screens, cumulative hits
  - De Brouwer et al. 2026 (arXiv, AssayBench) Table 3: 15 systems x 3 cohorts x 3 ranking metrics
Writes batch.jsonl and claims.csv in the store form.
"""
import csv, hashlib, json, os, re, sys
from decimal import Decimal

DL, BATCH = sys.argv[1], sys.argv[2]
P = "tgtval-20261009"
UC = "use-case-therapeutic-target-validation"
DATE = "2026-10-09"
FACETS = {"areas": ["cells-tissues"], "contexts": ["research"]}
records, claim_rows = [], []


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def expect(got, value, where):
    if got != value:
        raise SystemExit(f"{where}: expected {value!r}, found {got!r}")


def split_tail(line, n, pattern):
    """Label plus the last n whitespace-separated tokens of a text-layer row, each matching pattern.

    The PDF text layer sometimes leaves a single space between a label and its first value, so the
    row is split from the end rather than on runs of whitespace."""
    tokens = line.split()
    if len(tokens) < n + 1:
        return None
    values = tokens[-n:]
    if not all(re.fullmatch(pattern, v) for v in values):
        return None
    return " ".join(tokens[:-n]), values


def rec(id_, kind, name, description, source_ids, links=None, attributes=None, facets=None, status="needs_review"):
    records.append({"id": id_, "kind": kind, "name": name, "description": description, "status": status,
                    "facets": FACETS if facets is None else facets, "source_ids": source_ids,
                    "links": links or [], "attributes": attributes or {}})


def shortest(raw):
    s = repr(float(raw))
    if s.endswith(".0"):
        s = s[:-2]
    return s


# ---------------------------------------------------------------- sources
def source(id_, name, url, artifact_url, version, retrieved_at, path, status, doi, licence, archive):
    size = os.path.getsize(path)
    attrs = {"url": url, "artifact_url": artifact_url, "version": version, "retrieved_at": retrieved_at,
             "artifact_sha256": sha(path), "publication_status": status, "licence": licence,
             "media_type": "application/pdf", "doi": doi,
             "source_locator": "Full artifact bytes; per-record locators on each record",
             "access_and_reuse": f"{licence} permits redistribution of the article bytes.",
             "archive_note": (f"Not archived in the batch although the licence permits it: the PDF is {size:,} bytes and the "
                              "repository keeps releases small. The artifact_sha256 pins the bytes that were read."),
             "extraction_method": "pdftotext -layout text layer, parsed by extract/extract_target_validation.py"}
    rec(id_, "source", name, "Primary source retrieved and hashed for the therapeutic target validation use-case pass.",
        [], attributes=attrs)


S_ROO = f"{P}-source-roohani2025"
S_GUP = f"{P}-source-gupta2025"
S_ASB = f"{P}-source-debrouwer2026"
ROO_PDF, ROO_TXT = f"{DL}/roohani2025/2405.17631v3.pdf", f"{DL}/roohani2025/b.txt"
GUP_PDF, GUP_TXT = f"{DL}/gupta2025/2025.findings-emnlp.838.pdf", f"{DL}/gupta2025/g.txt"
ASB_PDF, ASB_TXT = f"{DL}/assaybench/2605.10876v1.pdf", f"{DL}/assaybench/a.txt"
ROO_URL = "https://arxiv.org/pdf/2405.17631v3"
GUP_URL = "https://aclanthology.org/2025.findings-emnlp.838.pdf"
ASB_URL = "https://arxiv.org/pdf/2605.10876v1"

source(S_ROO, "BioDiscoveryAgent: An AI Agent for Designing Genetic Perturbation Experiments",
       "https://arxiv.org/abs/2405.17631v3", ROO_URL,
       "arXiv:2405.17631 version 3, updated 2025-03-09; published as a conference paper at ICLR 2025",
       "2026-10-09T20:51:27Z", ROO_PDF, "peer_reviewed", "10.48550/arXiv.2405.17631", "CC-BY-4.0",
       "roohani2025-arxiv-2405-17631v3.pdf.gz")
source(S_GUP, "LLMs for Bayesian Optimization in Scientific Domains: Are We There Yet?",
       "https://aclanthology.org/2025.findings-emnlp.838/", GUP_URL,
       "Findings of the Association for Computational Linguistics: EMNLP 2025, pages 15482-15510",
       "2026-10-09T20:55:36Z", GUP_PDF, "peer_reviewed", "10.48550/arXiv.2509.21403", "CC-BY-4.0",
       "gupta2025-findings-emnlp-838.pdf.gz")
source(S_ASB, "AssayBench: An Assay-Level Virtual Cell Benchmark for LLMs and Agents",
       "https://arxiv.org/abs/2605.10876v1", ASB_URL, "arXiv:2605.10876 version 1, posted 2026-05-11; not peer reviewed",
       "2026-10-09T20:56:07Z", ASB_PDF, "preprint", "10.48550/arXiv.2605.10876", "CC-BY-4.0",
       "debrouwer2026-arxiv-2605-10876v1.pdf.gz")

# the Gupta DOI is the arXiv preprint of the same work; record that rather than implying an ACL DOI
records[1]["attributes"]["version_note"] = ("The DOI recorded is the arXiv preprint (arXiv:2509.21403) of the same work; "
                                            "the bytes read are the ACL Anthology version of record.")


def review_note(path, url, how):
    return {"method": ["pdf-text-parse"], "reviewer": ["claude"], "date": DATE,
            "reviewer_note": "Claude (Opus 5.5) extraction agent; extraction record, not an independent review",
            "artifact_sha256": sha(path), "retrieval_url": url, "note": how + " Pending independent review."}


def result(id_, eval_id, source_ids, locator, pv, metric, qualifier, unit, direction, review, extra=None, missing=None):
    attrs = {"metric": metric, "metric_qualifier": qualifier, "metric_direction": direction, "unit": unit,
             "printed_value": pv, "numeric_value": None if pv in ("N/A", "NA") else format(Decimal(pv), "f"),
             "source_locator": locator, "review": review}
    miss = {"uncertainty": {"reason": "unreported"}}
    if pv in ("N/A", "NA"):
        miss["value"] = {"reason": "inapplicable", "note": f"Printed {pv}"}
    miss.update(missing or {})
    attrs["missing_metadata"] = miss
    attrs.update(extra or {})
    rec(id_, "result", f"{eval_id.replace(P + '-eval-', '')} {metric}".strip(),
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


METHODS = {}


def method(key, name, description, source_ids, mtypes, locator, level="method"):
    if key in METHODS:
        return METHODS[key]
    METHODS[key] = f"{P}-method-{key}"
    rec(METHODS[key], "method", name, description, source_ids,
        attributes={"reported_name": name, "entity_level": level, "source_locator": locator,
                    "missing_metadata": {"version": {"reason": "inapplicable", "note": "Family record; settings are on configurations"}}},
        facets={**FACETS, "method_types": list(mtypes)})
    return METHODS[key]


MODELS = {}


def model(key, name, source_ids, locator, level="checkpoint"):
    if key in MODELS:
        return MODELS[key]
    MODELS[key] = f"{P}-model-{key}"
    rec(MODELS[key], "model", name, "Language model identity as reported in this source. Unspecified versions are not assumed equal to other papers.",
        source_ids, attributes={"entity_level": level, "reported_name": name, "source_locator": locator,
                                "missing_metadata": {"checkpoint_revision": {"reason": "unreported"},
                                                     "training_data": {"reason": "unreported"},
                                                     "version": {"reason": "unreported"}}},
        facets={**FACETS})
    return MODELS[key]


def configuration(id_, name, method_id, source_ids, reported, locator, mtypes, model_id=None, extra=None, limitations=None):
    links = [{"relation": "configuration_of", "target_id": method_id}]
    if model_id:
        links.append({"relation": "uses_model", "target_id": model_id})
    attrs = {"reported_name": reported, "foundation_model_eligible": bool(model_id), "source_locator": locator,
             "missing_metadata": {"version": {"reason": "unreported", "note": "No release or commit is printed for this configuration"}}}
    attrs.update(extra or {})
    if limitations:
        attrs["limitations"] = limitations
    rec(id_, "configuration", name, "Configuration as run in the cited comparison.", source_ids, links, attrs,
        facets={**FACETS, "method_types": list(mtypes)})


# ================================================================ shared screen datasets
SCREENS = {
    "schmidt2022-ifng": ("Schmidt et al. 2022 CRISPRa screen, interferon-gamma production in primary human T cells",
                         "Genome-wide perturbation screen measuring change in interferon-gamma (IFNG) production.",
                         "Over 18,000 genes, each knocked down in a distinct cell (Roohani et al. 2025 section 4.1)"),
    "schmidt2022-il2": ("Schmidt et al. 2022 CRISPRa screen, interleukin-2 production in primary human T cells",
                        "Genome-wide perturbation screen measuring change in interleukin-2 (IL-2) production.",
                        "Over 18,000 genes, each knocked down in a distinct cell (Roohani et al. 2025 section 4.1)"),
    "cart-proliferation": ("CAR-T proliferation screen (unpublished dataset used by Roohani et al. 2025)",
                           "Genome-wide perturbation screen measuring CAR-T cell proliferation.",
                           "Over 18,000 genes; the source states this dataset is unpublished"),
    "scharenberg2023-choline": ("Scharenberg et al. 2023 screen, lysosomal choline recycling in pancreatic cells",
                                "Perturbation screen measuring mediation of lysosomal choline recycling.",
                                "1,061 perturbations (Roohani et al. 2025 Table 1 footnote and section 4.1)"),
    "carnevale2022-tcell": ("Carnevale et al. 2022 screen, T-cell resistance to tumour-microenvironment inhibitory signals",
                            "Perturbation screen identifying genes that render T cells resistant to inhibitory signals.",
                            "Over 18,000 genes (Roohani et al. 2025 section 4.1)"),
    "sanchez2021-tau": ("Sanchez et al. 2021 screen, endogenous tau protein level in neurons",
                        "Perturbation screen measuring change in endogenous tau protein expression, in either direction.",
                        "Over 18,000 genes (Roohani et al. 2025 section 4.1)"),
    "sanchez2021-tau-down": ("Sanchez et al. 2021 screen, decreased endogenous tau protein level in neurons",
                             "The Sanchez et al. 2021 screen restricted to decreased tau expression (Gupta et al. 2025 appendix B.1.1).",
                             "Over 18,000 genes; same measurements as the Sanchez screen, hits restricted to decreases"),
}
DATA = {}
for key, (name, desc, pop) in SCREENS.items():
    DATA[key] = f"{P}-data-{key}"
    src = [S_GUP] if key == "sanchez2021-tau-down" else ([S_ROO, S_GUP] if key in
           ("schmidt2022-ifng", "schmidt2022-il2", "carnevale2022-tcell", "sanchez2021-tau") else [S_ROO])
    rec(DATA[key], "dataset", name, desc, src,
        attributes={"version": "As replayed by the cited benchmark from the original screen",
                    "population": pop, "assay": "Pooled CRISPR perturbation screen with a phenotypic readout",
                    "scope_note": ("Replayed offline: the benchmark looks up the measured phenotypic response of each selected gene "
                                   "instead of running a new experiment. Genes the screen did not assay are absent from the "
                                   "candidate pool, so they are neither hits nor non-hits."),
                    "source_locator": "Roohani et al. 2025 section 4.1; Gupta et al. 2025 appendix B.1.1",
                    "missing_metadata": {"positives": {"reason": "unreported", "note": "Roohani et al. do not print the hit count or the threshold tau per screen; Gupta et al. print their own ground-truth hit counts, recorded as a claim on their protocol"},
                                         "total": {"reason": "unreported", "note": "Stated as 'over 18,000 genes' rather than an exact count"}}})

# ================================================================ Roohani et al. 2025, Table 1
roo = open(ROO_TXT, encoding="utf-8").read().splitlines()
cap1 = [i for i, l in enumerate(roo) if l.startswith("Table 1: Performance comparison to machine learning baselines")]
expect(len(cap1), 1, "Roohani Table 1 caption")
hdr = [i for i in range(cap1[0] - 40, cap1[0]) if roo[i].strip().startswith("Model") and "Schmidt1" in roo[i]]
expect(len(hdr), 1, "Roohani Table 1 header above its caption")
h = hdr[0]
expect(roo[h].split(), ["Model", "Schmidt1", "Schmidt2", "CAR-T†", "Scharen.∗", "Carnev.", "Sanchez"], "Roohani Table 1 dataset header")
expect(roo[h + 1].split(), ["All", "N/E"] * 6, "Roohani Table 1 column header")
cap = cap1
roo_rows, section = [], None
for l in roo[h + 2:cap[0]]:
    if not l.strip():
        continue
    split = split_tail(l, 12, r"0\.\d{3}")
    if split is None:
        section = l.strip()
        expect(section in ("Baseline Models", "BioDiscoveryAgent (No-Tools)"), True, f"Roohani section {section!r}")
        continue
    roo_rows.append((section, split[0], split[1]))
expect([r[1] for r in roo_rows], ["Random", "Human", "Soft Uncertain", "Top Uncertain", "Margin Sample", "Coreset",
                                  "Badge", "K-Means (E)", "K-Means (D)", "DiscoBax", "Claude 3 Haiku", "GPT-3.5-Turbo",
                                  "Claude v1", "o1-mini", "Claude 3 Sonnet", "Claude 3.5 Sonnet", "GPT-4o",
                                  "o1-preview", "Claude 3 Opus", "Sonnet + Coreset"], "Roohani Table 1 row labels")

ROO_SCREENS = ["schmidt2022-ifng", "schmidt2022-il2", "cart-proliferation", "scharenberg2023-choline",
               "carnevale2022-tcell", "sanchez2021-tau"]
ROO_PRINTED = {"schmidt2022-ifng": "Schmidt1", "schmidt2022-il2": "Schmidt2", "cart-proliferation": "CAR-T",
               "scharenberg2023-choline": "Scharen.", "carnevale2022-tcell": "Carnev.", "sanchez2021-tau": "Sanchez"}
M_BDA = method("biodiscoveryagent", "BioDiscoveryAgent", "LLM agent that proposes the next batch of genes to perturb from the experimental history and its own prior knowledge.",
               [S_ROO, S_GUP], ["foundation_model"], "Roohani et al. 2025 section 3; Gupta et al. 2025 section 5")
M_RANDOM = method("random-selection", "Random selection", "Genes for each round drawn at random from the candidate pool.",
                  [S_ROO, S_GUP], ["conventional_pipeline"], "Roohani et al. 2025 section 4.1; Gupta et al. 2025 Table 3")
M_HUMAN = method("human-pathway-selection", "Human pathway-based selection", "Human baseline: the first batch is sampled from named Reactome and KEGG pathways, later batches from enrichment analysis of the hits so far.",
                 [S_ROO], ["conventional_pipeline"], "Roohani et al. 2025 appendix E and Table 6")
ACQ = {"Soft Uncertain": "soft-uncertain", "Top Uncertain": "top-uncertain", "Margin Sample": "margin-sample",
       "Coreset": "coreset", "Badge": "badge", "K-Means (E)": "kmeans-embedding", "K-Means (D)": "kmeans-data"}
for printed, key in ACQ.items():
    method(key, f"{printed} acquisition function (MLP surrogate)",
           "Bayesian optimisation acquisition function over a multi-layer perceptron surrogate, as implemented by the GeneDisco benchmark.",
           [S_ROO], ["supervised_machine_learning"], "Roohani et al. 2025 section 4.1 (baselines)")
method("discobax", "DiscoBAX", "Bayesian algorithm execution method for selecting diverse, high-value genetic interventions.",
       [S_ROO], ["supervised_machine_learning"], "Roohani et al. 2025 section 4.1 (baselines)")
ROO_LLMS = {"Claude 3 Haiku": "claude-3-haiku", "GPT-3.5-Turbo": "gpt-3-5-turbo", "Claude v1": "claude-v1",
            "o1-mini": "o1-mini", "Claude 3 Sonnet": "claude-3-sonnet", "Claude 3.5 Sonnet": "claude-3-5-sonnet",
            "GPT-4o": "gpt-4o", "o1-preview": "o1-preview", "Claude 3 Opus": "claude-3-opus"}
for printed, key in ROO_LLMS.items():
    model(key, printed, [S_ROO], "Roohani et al. 2025 Table 1 row labels and Table 4", level="service")

PR_ROO = f"{P}-protocol-roohani2025-hitratio-round5"
ROO_LIM = ["Offline replay of six existing screens: the candidate pool is the genes each screen assayed, so untested genes are absent rather than negative.",
           "Hit ratio measures recovery of that screen's own hits, not whether a target is useful.",
           "Hits are defined by a threshold tau on the screen's phenotypic response; the source does not print tau or the hit count per screen.",
           "All rows, including the baselines and the human baseline, were run by the agent's developers.",
           "Gupta et al. 2025 report that the same agent scores the same when its experimental feedback is replaced by randomly permuted outcomes, so these numbers should not be read as evidence that the agent learns from the results of each round."]
rec(PR_ROO, "protocol", "BioDiscoveryAgent 1-gene perturbation design: hit ratio after 5 rounds of 128 genes",
    "Offline replay of six CRISPR screens: each method selects 128 genes per round for 5 rounds and is scored on the fraction of that screen's hits it recovered.",
    [S_ROO], [{"relation": "uses_data", "target_id": DATA[k]} for k in ROO_SCREENS],
    {"protocol": ("At each of 5 rounds a method selects 128 genes (32 for Scharenberg et al. 2023, whose pool is 1,061 "
                  "perturbations); the measured phenotypic response of each selected gene is then revealed from the screen. "
                  "Score: hit ratio after round 5, the fraction of the screen's true hits that were selected in any round, "
                  "averaged over 10 runs. Reported twice per screen: over all genes, and over non-essential genes only."),
     "version": "Roohani et al. 2025 (ICLR 2025) sections 2 and 4; Table 1",
     "metric": "recall", "metric_direction": "higher", "unit": "fraction",
     "metric_definition": ("Hit ratio = |genes selected in rounds 1..5 whose response exceeds the threshold tau| / |all genes in the "
                           "screen whose response exceeds tau|. This is recall over the screen's hit set. Non-hits are genes the "
                           "screen assayed whose response did not exceed tau; genes the screen did not assay are not in the pool."),
     "selection": "Candidate pool is the genes assayed by each screen (over 18,000 per screen; 1,061 for Scharenberg et al. 2023)",
     "limitations": ROO_LIM,
     "source_locator": "Sections 2 and 4.1; Table 1 and its caption; appendix Table 7 (error intervals)"})
claim(f"{P}-claim-roohani2025-hit-definition", PR_ROO, "metric_definition",
      "A hit is a gene whose perturbation produces a phenotypic response above a threshold tau, f(g) > tau. The hit ratio after T rounds is the fraction of all such genes that the method selected, which the source describes as similar to recall.",
      [S_ROO], "Section 2 (problem setting), equations for hit ratio", ROO_PDF, ROO_URL)
claim(f"{P}-claim-roohani2025-nonessential", PR_ROO, "scoring_population",
      "The 'N/E' columns count only non-essential genes among the hits. The source argues essential genes are likely to be detected as hits under many phenotypes, so the non-essential subset is the harder and more biologically useful task. The source does not print which gene list defines essentiality.",
      [S_ROO], "Section 5 (results, non-essential genes) and Table 1 caption", ROO_PDF, ROO_URL)

roo_review = review_note(ROO_PDF, ROO_URL, "Extracted by deterministic parse of the PDF text layer (pdftotext -layout) of Table 1, "
                         "asserting the two header rows, the two section headers, the 20 row labels and 12 values per row.")
ROO_CFG = {}
for section, label, nums in roo_rows:
    key = re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-")
    cid = f"{P}-config-roohani2025-{key}"
    ROO_CFG[label] = cid
    if label in ROO_LLMS:
        configuration(cid, f"BioDiscoveryAgent (No-Tools), {label} (Roohani et al. 2025)", M_BDA, [S_ROO], label,
                      "Table 1, BioDiscoveryAgent (No-Tools) block", ["foundation_model"], MODELS[ROO_LLMS[label]],
                      extra={"parameters": "No-Tools variant: no literature search, gene search or critic tool", "source_label": label})
    elif label == "Sonnet + Coreset":
        configuration(cid, "BioDiscoveryAgent (Claude 3.5 Sonnet) combined with the Coreset acquisition function (Roohani et al. 2025)",
                      M_BDA, [S_ROO], label, "Table 1, BioDiscoveryAgent (No-Tools) block, last row", ["foundation_model"],
                      MODELS["claude-3-5-sonnet"],
                      extra={"parameters": "Hybrid of the agent and the Coreset baseline; the source does not describe how the two are combined",
                             "source_label": label},
                      limitations=["The source prints this row without describing the combination rule."])
    elif label == "Random":
        configuration(cid, "Random selection (Roohani et al. 2025)", M_RANDOM, [S_ROO], label, "Table 1, first row",
                      ["conventional_pipeline"], extra={"source_label": label})
    elif label == "Human":
        configuration(cid, "Human pathway-based selection (Roohani et al. 2025)", M_HUMAN, [S_ROO], label, "Table 1, second row; appendix E",
                      ["conventional_pipeline"], extra={"source_label": label})
    elif label == "DiscoBax":
        configuration(cid, "DiscoBAX (Roohani et al. 2025)", METHODS["discobax"], [S_ROO], label, "Table 1, Baseline Models block",
                      ["supervised_machine_learning"], extra={"source_label": label})
    else:
        configuration(cid, f"{label} acquisition function on an MLP surrogate (Roohani et al. 2025)", METHODS[ACQ[label]],
                      [S_ROO], label, "Table 1, Baseline Models block", ["supervised_machine_learning"],
                      extra={"source_label": label})

for section, label, nums in roo_rows:
    for i, skey in enumerate(ROO_SCREENS):
        ev = f"{P}-eval-roohani2025-{re.sub(r'[^a-z0-9]+', '-', label.lower()).strip('-')}-{skey}"
        batch = 32 if skey == "scharenberg2023-choline" else 128
        evaluation(ev, f"{label} on {ROO_PRINTED[skey]} (Roohani et al. 2025)", ROO_CFG[label], PR_ROO, DATA[skey], [S_ROO],
                   "author_reported",
                   {"dataset_version": "Offline replay of the screen", "split": "No training split; 5 sequential selection rounds",
                    "population": f"Genes assayed by the {ROO_PRINTED[skey]} screen",
                    "inputs": "Phenotype description and the responses revealed in previous rounds",
                    "adaptation": "Selection only; no model fitting for the agent rows", "metric_implementation": None,
                    "aggregation": "Mean over 10 runs", "budget": f"5 rounds x {batch} genes"},
                   f"Table 1, row '{label}', columns for '{ROO_PRINTED[skey]}'",
                   limitations=["Run by the authors of the agent."],
                   missing={"comparison.metric_implementation": {"reason": "unreported"}})
        for j, scope in enumerate(("all genes", "non-essential genes only")):
            raw = nums[i * 2 + j]
            result(f"{ev.replace('-eval-', '-result-')}-{'all' if j == 0 else 'nonessential'}", ev, [S_ROO],
                   f"Table 1, row '{label}', column '{'All' if j == 0 else 'N/E'}' under '{ROO_PRINTED[skey]}'",
                   raw, "recall", f"hit ratio after round 5, {scope}; mean of 10 runs", "fraction", "higher", roo_review,
                   extra={"scope_note": f"Scoring population: {scope}."})

# ================================================================ Gupta et al. 2025, Tables 1 and 2
gup = open(GUP_TXT, encoding="utf-8").read().splitlines()
GHDR = re.compile(r"^\s*Method\s+IL2\s+IFNG\s+Carnevale\s+Sanchez\s+Sanchez Down\s*$")
ghdr = [i for i, l in enumerate(gup) if GHDR.match(l)]
expect(len(ghdr), 4, "Gupta method-header rows")  # Tables 1, 2, 3 and the Table 5 ablation
GUP_SCREENS = ["schmidt2022-il2", "schmidt2022-ifng", "carnevale2022-tcell", "sanchez2021-tau", "sanchez2021-tau-down"]
GUP_PRINTED = {"schmidt2022-il2": "IL2", "schmidt2022-ifng": "IFNG", "carnevale2022-tcell": "Carnevale",
               "sanchez2021-tau": "Sanchez", "sanchez2021-tau-down": "Sanchez Down"}


def gupta_table(start, number):
    cap = [i for i in range(start, start + 40) if gup[i].lstrip().startswith(f"Table {number}:")]
    expect(len(cap), 1, f"Gupta Table {number} caption")
    rows, backbone = [], None
    for l in gup[start + 1:cap[0]]:
        if not l.strip():
            continue
        split = split_tail(l, 5, r"\d+(?:\.\d+)?|N/A")
        if split is None:
            backbone = l.strip()
            expect(backbone.endswith("backbone"), True, f"Gupta Table {number} section {backbone!r}")
            continue
        rows.append((backbone, split[0], split[1]))
    return rows


t1 = gupta_table(ghdr[0], 1)
t2 = gupta_table(ghdr[1], 2)
expect([(b, l) for b, l, _ in t1], [(None, "Ground truth (| Cgt |)"), ("Llama-3.1-8B backbone", "BDA"),
                                    ("Llama-3.1-8B backbone", "BDA-Rand"), ("Qwen-2-7B backbone", "BDA"),
                                    ("Qwen-2-7B backbone", "BDA-Rand"), ("Claude 3.5 Sonnet backbone", "BDA (Reported Numbers)"),
                                    ("Claude 3.5 Sonnet backbone", "BDA (Replicated)"), ("Claude 3.5 Sonnet backbone", "BDA-Rand")],
       "Gupta Table 1 rows")
expect([(b, l) for b, l, _ in t2], [(None, "Ground truth (| Cgt |)"), ("Llama-3.1-8B backbone", "Linear UCB"),
                                    ("Llama-3.1-8B backbone", "GP"), ("Llama-3.1-8B backbone", "BDA"),
                                    ("Qwen-2-7B backbone", "Linear UCB"), ("Qwen-2-7B backbone", "GP"),
                                    ("Qwen-2-7B backbone", "BDA")], "Gupta Table 2 rows")
gt1 = dict(zip(GUP_SCREENS, t1[0][2]))
expect(gt1, dict(zip(GUP_SCREENS, t2[0][2])), "Gupta ground-truth row differs between Tables 1 and 2")

M_LUCB = method("linear-ucb", "Linear upper confidence bound", "Linear bandit acquisition over candidate embeddings.",
                [S_GUP], ["supervised_machine_learning"], "Gupta et al. 2025 section 6 and Table 2")
M_GP = method("gaussian-process", "Gaussian process optimisation", "Gaussian process surrogate with an acquisition function over candidate embeddings.",
              [S_GUP], ["supervised_machine_learning"], "Gupta et al. 2025 section 6 and Table 2")
for printed, key in (("Llama-3.1-8B", "llama-3-1-8b"), ("Qwen-2-7B", "qwen-2-7b")):
    model(key, printed, [S_GUP], "Gupta et al. 2025 Tables 1-2 backbone headings")
model("claude-3-5-sonnet", "Claude 3.5 Sonnet", [S_ROO], "Roohani et al. 2025 Table 1")

PR_GUP = f"{P}-protocol-gupta2025-cumulative-hits-round5"
GUP_LIM = ["Offline replay of five of the same screens; untested genes are absent from the candidate pool rather than negative.",
           "Cumulative hits is a count, so values are comparable only within a screen.",
           "The Claude 3.5 Sonnet 'Reported Numbers' row is copied from Roohani et al. 2025, not re-run here, and the source's replication of the same setting gives lower counts on four of five screens.",
           "The source does not print the hit threshold; it prints its own ground-truth hit counts per screen."]
rec(PR_GUP, "protocol", "Independent replication of 1-gene perturbation design: cumulative hits after 5 rounds of 128 genes",
    "Replay of five CRISPR screens by authors independent of the agent, comparing the agent, the agent given randomly permuted feedback, and classical sequential designs.",
    [S_GUP], [{"relation": "uses_data", "target_id": DATA[k]} for k in GUP_SCREENS],
    {"protocol": ("At each of 5 rounds a method selects 128 genes; the measured response of each is revealed. Score: cumulative "
                  "number of the screen's hits selected by the end of round 5, averaged over 5 runs. The agent is also run with "
                  "randomly permuted outcomes (BDA-Rand) to test whether it uses the feedback at all; classical designs use the "
                  "embeddings of the same language model as the agent's backbone."),
     "version": "Gupta et al. 2025 (Findings of EMNLP 2025) sections 4-6; Tables 1 and 2",
     "metric": "true-positive-count", "metric_direction": "higher", "unit": "count",
     "unit_detail": "Genes that are hits in the screen",
     "metric_definition": "Cumulative count of the screen's hits selected across 5 rounds of 128 genes, averaged over 5 runs. Non-hits are genes the screen assayed that are not in its hit set.",
     "control": "BDA-Rand is the same agent with the mapping between genes and outcomes randomly permuted, at two levels: random measurement values, and random hit or not-hit feedback.",
     "limitations": GUP_LIM,
     "source_locator": "Sections 4.1, 5 and 6; Tables 1 and 2; appendix B.1.1"})
claim(f"{P}-claim-gupta2025-ground-truth-hits", PR_GUP, "denominator",
      "Printed ground-truth hit counts |C_gt| per screen: IL2 654, IFNG 920, Carnevale 943, Sanchez 924, Sanchez Down 924. The same five values are printed in Tables 1, 2 and 3.",
      [S_GUP], "Tables 1, 2 and 3, row 'Ground truth (| Cgt |)'", GUP_PDF, GUP_URL)
claim(f"{P}-claim-gupta2025-permuted-feedback", PR_GUP, "control_result",
      "The source states that replacing true outcomes with randomly permuted labels has no impact on performance, and concludes that the language models tested fail to perform in-context experimental design. It performs two levels of randomisation: random measurement values, and random hit or not-hit feedback.",
      [S_GUP], "Abstract; section 5 and Table 1 caption", GUP_PDF, GUP_URL)

claim(f"{P}-claim-gupta2025-reported-numbers-conversion", PR_GUP, "cross_source_consistency",
      "The 'BDA (Reported Numbers)' row divided by the printed ground-truth hit counts reproduces the all-gene hit ratios of "
      "Roohani et al. 2025 Table 1 for Claude 3.5 Sonnet to the printed rounding: IL2 68.01/654 = 0.104 against 0.104, "
      "IFNG 87.4/920 = 0.095 against 0.095, Carnevale 39.6/943 = 0.042 against 0.042 and Sanchez 60.72/924 = 0.0657 against 0.066. "
      "This indicates that both sources score against the same screens and the same hit sets, and that the row is a unit "
      "conversion of the original table rather than a new run. Checked during extraction; no value was altered.",
      [S_GUP, S_ROO], "Gupta et al. 2025 Tables 1 and 2 against Roohani et al. 2025 Table 1", GUP_PDF, GUP_URL)

gup_review = review_note(GUP_PDF, GUP_URL, "Extracted by deterministic parse of the PDF text layer (pdftotext -layout) of Tables 1 "
                         "and 2, asserting the column header, the backbone section headings, the row labels and five values per row.")
GUP_CFG = {}


def gupta_cfg(backbone, label, table):
    bkey = {"Llama-3.1-8B backbone": "llama-3-1-8b", "Qwen-2-7B backbone": "qwen-2-7b",
            "Claude 3.5 Sonnet backbone": "claude-3-5-sonnet"}[backbone]
    key = f"{re.sub(r'[^a-z0-9]+', '-', label.lower()).strip('-')}-{bkey}"
    if key in GUP_CFG:
        return GUP_CFG[key]
    cid = f"{P}-config-gupta2025-{key}"
    GUP_CFG[key] = cid
    mid = MODELS[bkey]
    if label.startswith("BDA"):
        rand = "Rand" in label
        extra = {"source_label": label, "parameters": "No-Tool variant of BioDiscoveryAgent" +
                 ("; experimental feedback replaced by randomly permuted outcomes" if rand else "")}
        lim = ["Receives randomly permuted outcomes instead of true feedback; a control, not a method anyone would deploy."] if rand else None
        if label == "BDA (Reported Numbers)":
            extra["parameters"] = "No-Tool variant; values copied from Roohani et al. 2025 rather than re-run"
            lim = ["Copied from the original paper, not re-run by this source."]
        configuration(cid, f"{label}, {bkey} backbone (Gupta et al. 2025)", M_BDA, [S_GUP], label,
                      f"Table {table}, '{backbone}' block", ["foundation_model"], mid, extra=extra, limitations=lim)
    else:
        mth = M_LUCB if label == "Linear UCB" else M_GP
        configuration(cid, f"{label} over {bkey} embeddings (Gupta et al. 2025)", mth, [S_GUP], label,
                      f"Table {table}, '{backbone}' block", ["supervised_machine_learning"], mid,
                      extra={"source_label": label,
                             "parameters": f"Acquisition over the embeddings of {bkey}, the same model used as the agent's backbone"})
    return cid


GUP_EV = {}
for table, rows in ((1, t1), (2, t2)):
    for backbone, label, nums in rows:
        if label.startswith("Ground truth"):
            continue
        cid = gupta_cfg(backbone, label, table)
        key = cid.split("-config-gupta2025-")[1]
        for i, skey in enumerate(GUP_SCREENS):
            raw = nums[i]
            ev = f"{P}-eval-gupta2025-{key}-{skey}"
            loc = f"Table {table}, '{backbone}' block, row '{label}', column '{GUP_PRINTED[skey]}'"
            if ev in GUP_EV:
                expect(raw, GUP_EV[ev], f"{loc} repeats an earlier row with a different value")
                claim_rows.append([f"{ev.replace('-eval-', '-result-')}-hits", S_GUP, loc + " (same value as Table 1; not recorded twice)", raw, "result-duplicate"])
                continue
            GUP_EV[ev] = raw
            origin = "paper_compilation" if label == "BDA (Reported Numbers)" else "independent_paper"
            evaluation(ev, f"{label} ({backbone}) on {GUP_PRINTED[skey]} (Gupta et al. 2025)", cid, PR_GUP, DATA[skey], [S_GUP],
                       origin,
                       {"dataset_version": "Offline replay of the screen", "split": "No training split; 5 sequential selection rounds",
                        "population": f"Genes assayed by the {GUP_PRINTED[skey]} screen",
                        "inputs": "Phenotype description and the outcomes revealed in previous rounds, true or permuted",
                        "adaptation": "Selection only", "metric_implementation": None,
                        "aggregation": "Mean over 5 runs", "budget": "5 rounds x 128 genes"},
                       loc, missing={"comparison.metric_implementation": {"reason": "unreported"}})
            extra = {"denominator": int(gt1[skey]), "denominator_note": f"Printed ground-truth hit count for this screen: {gt1[skey]}"}
            if label == "GP":
                extra["source_anomaly"] = ("Table 2 prints identical GP values for the Llama-3.1-8B and Qwen-2-7B blocks "
                                           "(147.8, 23, 22.2, 27.6, 30), although the embeddings differ between backbones.")
            result(f"{ev.replace('-eval-', '-result-')}-hits", ev, [S_GUP], loc, raw, "true-positive-count",
                   "cumulative hits after round 5; mean of 5 runs", "count", "higher", gup_review, extra=extra)

# ================================================================ De Brouwer et al. 2026, Table 3
asb = open(ASB_TXT, encoding="utf-8").read().splitlines()
ahdr = [i for i, l in enumerate(asb) if re.match(r"^\s*Method\s+Cohort\s+AnDCG@100\s+Precision@100\s+dFDR@100\s*$", l)]
expect(len(ahdr), 1, "AssayBench Table 3 header")
acap = [i for i in range(ahdr[0], min(len(asb), ahdr[0] + 80)) if asb[i].lstrip().startswith("Table 3:")]
expect(len(acap), 1, "AssayBench Table 3 caption")
arows = []
for l in asb[ahdr[0] + 1:acap[0]]:
    if not l.strip():
        continue
    split = split_tail(l, 4, r"val|test|LaTest|[0-9.]+|NA")
    if split is None:
        raise SystemExit(f"AssayBench Table 3 line not understood: {l!r}")
    label, (cohort, a, p, d) = split
    expect(cohort in ("val", "test", "LaTest"), True, f"AssayBench cohort token {cohort!r}")
    arows.append((label, cohort, a, p, d))
expect(len(arows), 48, "AssayBench Table 3 row count")
ASB_SYS = sorted({r[0] for r in arows})
expect(len(ASB_SYS), 16, "AssayBench system count")
for s in ASB_SYS:
    expect(sorted(r[1] for r in arows if r[0] == s), ["LaTest", "test", "val"], f"AssayBench cohorts for {s!r}")
for label, cohort, a, p, d in arows:
    expect(d == "NA", cohort == "LaTest", f"AssayBench dFDR for {label!r} {cohort}")

ASB_COHORT = {"val": ("validation", "218 benchmark entries from screens published in 2021"),
              "test": ("test", "334 benchmark entries from screens published after 2021"),
              "LaTest": ("post-cutoff", "19 benchmark entries from publications after September 2025, absent from BioGRID")}
ASB_DATA = {}
for ck, (name, pop) in ASB_COHORT.items():
    ASB_DATA[ck] = f"{P}-data-assaybench-{name}"
    rec(ASB_DATA[ck], "dataset", f"AssayBench {name} cohort of human CRISPR screens",
        f"The {name} cohort of the AssayBench temporal split.", [S_ASB],
        attributes={"version": "AssayBench, arXiv:2605.10876v1; built from the 2025 BioGRID ORCS release and 19 recent publications",
                    "population": pop, "assay": "Pooled human CRISPR screens with the screen's own significance criterion",
                    "scope_note": ("Each entry is one screen cast as a gene-ranking task. Hits are the genes meeting that screen's "
                                   "significance criterion; non-hits are assayed genes that do not meet it and are given relevance 0; "
                                   "genes the screen did not assay are removed from the ranking rather than counted as false positives. "
                                   "In screens with a bidirectional criterion, genes significant in the opposite direction get negative relevance."),
                    "source_locator": "Sections 2.1 to 2.3; Table 1 (split statistics)",
                    "missing_metadata": {"positives": {"reason": "unreported", "note": "Hit counts per entry are not printed; relevance is a per-screen percentile construction"}}})
claim(f"{P}-claim-debrouwer2026-curation", ASB_DATA["test"], "label_semantics",
      "A hit is a gene that satisfies the significance criterion of its own screen. Screens where all tested genes are significant, or with missing criteria, were removed. Relevance scores are percentile ranks of the screen's own metrics combined by geometric mean, with non-hit genes set to zero; screens whose relevance ranking disagreed with the original hit labels at ROC-AUC below 0.95 were excluded. Phenotype descriptions and effect directions were extracted by an LLM-assisted curation step.",
      [S_ASB], "Sections 2.1 and 2.2", ASB_PDF, ASB_URL)

PR_ASB = f"{P}-protocol-debrouwer2026-screen-gene-ranking"
ASB_LIM = ["Ranking is scored only over genes the screen assayed; unassayed genes are removed rather than penalised, so untested genes are not negatives.",
           "Hits follow each screen's own significance criterion, so the phenotype and threshold vary between entries.",
           "Retrospective replay of published screens; no new experiment was run.",
           "Phenotype descriptions and effect directions come from an LLM-assisted curation step over BioGRID metadata.",
           "The source notes that frontier language models may have seen much of the underlying literature during pretraining, and reports a performance drop on the post-cutoff cohort.",
           "Precision@100 divides by min(100, number of positive-relevance genes), so it is not precision over a fixed 100 predictions when a screen has fewer than 100 hits."]
rec(PR_ASB, "protocol", "AssayBench: rank 100 candidate genes for a described CRISPR screen",
    "Given a screen description and its significance criterion, a system returns a ranked list of 100 genes, scored against the screen's own hit labels.",
    [S_ASB], [{"relation": "uses_data", "target_id": ASB_DATA[c]} for c in ("val", "test", "LaTest")],
    {"protocol": ("For each benchmark entry the system is given the phenotype, cell line, cell type, library and perturbation "
                  "modality, treatment and duration, plus the ranking objective, and returns 100 ranked gene symbols. Metrics: "
                  "AnDCG@100 (condensed NDCG adjusted so 0 is a random ranking for that screen), Precision@100, and dFDR@100."),
     "version": "AssayBench, arXiv:2605.10876v1, sections 2 to 4",
     "metric": "adjusted-ndcg-at-100", "metric_direction": "higher", "unit": "unitless",
     "metric_definition": ("AnDCG@100 removes unassayed genes from the ranked list, computes NDCG@100 against percentile-rank "
                           "relevance, and rescales by the screen's analytic random baseline. Precision@100 is the share of the "
                           "top-ranked scored genes that are hits, with denominator min(100, positive-relevance genes). dFDR@100 "
                           "is the share of the top 100 scored genes that are significant in the opposite direction."),
     "limitations": ASB_LIM,
     "source_locator": "Sections 2.4, 3 and 4; Tables 1 to 3"})

ASB_KIND = {
    "Gemini 3 Pro": ("model", "gemini-3-pro", "independent_paper", "zero-shot", ["foundation_model"]),
    "Gemini 3 Pro (Few-shot)": ("model", "gemini-3-pro", "independent_paper", "10 nearest-neighbour training examples in context", ["foundation_model"]),
    "Gemini 3 Flash": ("model", "gemini-3-flash", "independent_paper", "zero-shot", ["foundation_model"]),
    "Gemini 3 Flash (GEPA)": ("model", "gemini-3-flash", "author_reported", "prompts optimised with GEPA on the training split", ["foundation_model"]),
    "GPT-5.4": ("model", "gpt-5-4", "independent_paper", "zero-shot", ["foundation_model"]),
    "Qwen3.5-2B": ("model", "qwen3-5-2b", "independent_paper", "zero-shot", ["foundation_model"]),
    "GPT-OSS-120B": ("model", "gpt-oss-120b", "independent_paper", "zero-shot", ["foundation_model"]),
    "GPT-OSS-120B (SFT)": ("model", "gpt-oss-120b", "author_reported", "supervised fine-tuning on the temporal training split", ["foundation_model"]),
    "GPT-OSS-120B (SFT + GRPO)": ("model", "gpt-oss-120b", "author_reported", "supervised fine-tuning then GRPO reinforcement learning", ["foundation_model"]),
    "LLM Ensemble": ("method", "llm-ensemble", "author_reported", "ensemble over several model outputs, discovered with AlphaEvolve on the training split", ["foundation_model"]),
    "Biomni A1 (Claude 4)": ("method", "biomni", "independent_paper", "biomedical agent with tool access, Claude 4 backbone", ["foundation_model"]),
    "C2S (Gemma-2B)": ("method", "c2s-scale", "independent_paper", "single-cell language model, Gemma-2B backbone", ["foundation_model"]),
    "Gene-relevance predictor": ("method", "gene-relevance-predictor", "author_reported", "neural predictor trained on the AssayBench training split from screen-text and gene embeddings", ["supervised_machine_learning"]),
    "Embedding kNN": ("method", "embedding-knn", "author_reported", "top genes of the most similar training screen by description embedding", ["conventional_pipeline"]),
    "Oracle kNN": ("method", "oracle-knn", "author_reported", "training screen chosen to maximise AnDCG@100 against the target screen; an upper bound, not a usable method", ["conventional_pipeline"]),
    "Gene-frequency (by phenotype)": ("method", "gene-frequency", "author_reported", "genes ranked by how often they are hits in training screens of the same phenotype category", ["conventional_pipeline"]),
}
expect(sorted(ASB_KIND), ASB_SYS, "AssayBench system labels")
ASB_DESC = {"gemini-3-pro": "Proprietary frontier language model.", "gemini-3-flash": "Proprietary frontier language model.",
            "gpt-5-4": "Proprietary frontier language model.", "qwen3-5-2b": "Open-weight language model.",
            "gpt-oss-120b": "Open-weight language model.",
            "llm-ensemble": "Algorithmic ensemble over several language-model rankings.",
            "biomni": "Biomedical agent with access to biology tools.",
            "c2s-scale": "Language model fine-tuned on single-cell tasks.",
            "gene-relevance-predictor": "Neural predictor of per-gene relevance from screen text and gene embeddings.",
            "embedding-knn": "Retrieval baseline over screen-description embeddings.",
            "oracle-knn": "Retrieval upper bound that selects the best-matching training screen using the answer.",
            "gene-frequency": "Frequency baseline over training screens of the same phenotype category."}
for label, (kind, key, origin, setting, mt) in ASB_KIND.items():
    if kind == "model":
        model(key, label.split(" (")[0], [S_ASB], "AssayBench Tables 2-3 row labels; section 4.1", level="service")
    else:
        method(key, label.split(" (")[0], ASB_DESC[key], [S_ASB], mt, "AssayBench section 4; Tables 2-3 row labels")

asb_review = review_note(ASB_PDF, ASB_URL, "Extracted by deterministic parse of the PDF text layer (pdftotext -layout) of Table 3, "
                         "asserting the column header, 45 rows, 15 systems, the three cohorts per system and that dFDR is NA only "
                         "for the post-cutoff cohort.")
AMET = {"a": ("adjusted-ndcg-at-100", "unitless", "higher", "AnDCG@100"),
        "p": ("precision-at-100", "fraction", "higher", "Precision@100"),
        "d": ("directional-false-discovery-rate-at-100", "fraction", "lower", "dFDR@100")}
for label, (kind, key, origin, setting, mt) in ASB_KIND.items():
    ckey = re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-")
    cid = f"{P}-config-debrouwer2026-{ckey}"
    target = MODELS[key] if kind == "model" else METHODS[key]
    configuration(cid, f"{label} (AssayBench)", target, [S_ASB], label, "Tables 2-3 row labels; section 4",
                  mt, MODELS[key] if kind == "model" else None, extra={"source_label": label, "parameters": setting})
    if kind == "model":
        # a model-backed row configures the model itself; drop the duplicate uses_model link
        records[-1]["links"] = [{"relation": "configuration_of", "target_id": MODELS[key]}]
    for cohort in ("val", "test", "LaTest"):
        row = [r for r in arows if r[0] == label and r[1] == cohort][0]
        ev = f"{P}-eval-debrouwer2026-{ckey}-{ASB_COHORT[cohort][0]}"
        evaluation(ev, f"{label} on the AssayBench {ASB_COHORT[cohort][0]} cohort", cid, PR_ASB, ASB_DATA[cohort], [S_ASB],
                   origin,
                   {"dataset_version": "AssayBench v1", "split": f"Temporal split, {ASB_COHORT[cohort][0]} cohort",
                    "population": ASB_COHORT[cohort][1], "inputs": "Screen description, significance criterion and ranking objective",
                    "adaptation": setting, "metric_implementation": "AnDCG@100, Precision@100 and dFDR@100 as defined in section 3",
                    "aggregation": "Mean over benchmark entries in the cohort", "budget": "One ranked list of 100 genes per entry"},
                   f"Table 3, rows for '{label}', cohort '{cohort}'",
                   limitations=["Reported by the benchmark's authors for a system they did not build."] if origin == "independent_paper"
                   else ["Reported by the benchmark's authors for their own system."])
        for col, raw in (("a", row[2]), ("p", row[3]), ("d", row[4])):
            metric, unit, direction, printed = AMET[col]
            result(f"{ev.replace('-eval-', '-result-')}-{metric}", ev, [S_ASB], f"Table 3, row '{label}' cohort '{cohort}', column '{printed}'",
                   raw, metric, f"{ASB_COHORT[cohort][0]} cohort; mean over benchmark entries", unit, direction, asb_review,
                   extra={"scope_note": "Precision@100 denominator is min(100, positive-relevance genes) (section 3.2)."} if col == "p" else None,
                   missing={"value": {"reason": "inapplicable", "note": "Printed NA: no screen in this cohort has negative relevance scores (Table 3 caption)"}} if raw == "NA" else None)

# cross-check Table 2 (test split) against Table 3
t2hdr = [i for i, l in enumerate(asb) if re.match(r"^\s*Method\s+AnDCG@100\(.\)\s+Precision@100\(.\)\s+dFDR@100\(.\)\s*$", l)]
expect(len(t2hdr), 1, "AssayBench Table 2 header")
t2cap = [i for i in range(t2hdr[0], min(len(asb), t2hdr[0] + 30)) if asb[i].lstrip().startswith("Table 2:")]
n_checked = 0
for l in asb[t2hdr[0] + 1:t2cap[0]]:
    split = split_tail(l, 3, r"[0-9.]+")
    if split is None:
        continue
    printed, values = split
    label = {"+SFT": "GPT-OSS-120B (SFT)", "+SFT+GRPO": "GPT-OSS-120B (SFT + GRPO)"}.get(printed, printed)
    row = [r for r in arows if r[0] == label and r[1] == "test"]
    expect(len(row), 1, f"AssayBench Table 2 row {label!r} not in Table 3")
    expect(tuple(values), row[0][2:], f"AssayBench Table 2 vs Table 3 for {label!r}")
    claim_rows.append([f"{P}-config-debrouwer2026-{re.sub(r'[^a-z0-9]+', '-', label.lower()).strip('-')}", S_ASB,
                       f"Table 2, row '{printed}' (test split; same values as Table 3)", values[0], "result-duplicate"])
    n_checked += 1
expect(n_checked, 16, "AssayBench Table 2 rows checked")

# ================================================================ judgements
J = "use-case-mapping-target-validation-20261009"
CONSTRAINTS = ["Inspect every linked evaluation's source locator and preserved limitations before citing a result.",
               "Do not combine this mapping's evaluations with any other protocol's results; screens, hit definitions, candidate pools and metrics differ.",
               "Genes absent from a screen's candidate pool are untested, not negative, and no result here says otherwise."]
NEG = ("Negatives are genes the screen assayed whose measured response did not meet its significance criterion. Genes the screen "
       "did not assay are excluded from the candidate pool, so the benchmark never treats an untested gene as a negative; it also "
       "never tests whether a method would have found a target outside that pool.")


def judgement(short, protocol, endpoint, rationale, limitations, sources, cites, group, title, metric, label, order):
    rec(f"{J}-{short}", "claim", f"Relevance of {protocol} to \"Which targets should I test to change a defined disease-relevant phenotype?\"",
        rationale, sources, [{"relation": "subject", "target_id": UC}],
        {"field": f"links:assessed_by:{protocol}", "value": protocol, "relevance": "proxy", "endpoint": endpoint,
         "rationale": rationale + " " + NEG, "constraints": CONSTRAINTS, "limitations": limitations,
         "citation_locators": [{"source_id": s, "locator": loc} for s, loc in cites],
         "source_locator": "; ".join(f"{s}: {loc}" for s, loc in cites), "revision": 1,
         "reason": "Add primary-source target-prioritisation comparisons from the therapeutic target validation use-case pass 2026-10-09.",
         "comparison_group": group, "comparison_title": title, "headline_metric": metric,
         "stratum_label": label, "stratum_order": order}, facets={})


GROUP = "target-nomination-vs-screen-hits"
TITLE = "Target nomination methods scored against measured CRISPR screen hits"
judgement("roohani2025-hitratio", PR_ROO,
          "Hit ratio after 5 rounds of 128 selected genes, over all genes and over non-essential genes only, for 20 selection methods on six CRISPR screens: random selection, a human pathway baseline, seven acquisition functions, DiscoBAX, nine LLM agents and one hybrid",
          "Compares many target-selection methods on the same measured screens for a defined phenotypic readout, which is the use case's question in retrospective form. It is proxy evidence: the screens are replayed offline rather than tested prospectively, the candidate pool is limited to genes each screen assayed, and recovering a screen's hits is not the same as a target being worth pursuing.",
          ROO_LIM, [S_ROO], [(S_ROO, "Sections 2 and 4.1; Table 1; appendix Table 7")],
          GROUP, TITLE, "recall", "Hit ratio, 6 screens (developer-run)", 1)
judgement("gupta2025-cumulative-hits", PR_GUP,
          "Cumulative hits after 5 rounds of 128 selected genes on five of the same screens, for the agent, the agent given randomly permuted feedback, linear bandits and Gaussian process optimisation, alongside the originally reported numbers",
          "An independent replication of the same selection task, which adds the control the original lacks: the same agent given permuted feedback. It is proxy evidence for the same reasons as the original, and it bears on how the original numbers should be read rather than on target usefulness.",
          GUP_LIM, [S_GUP], [(S_GUP, "Sections 4.1, 5 and 6; Tables 1 and 2; appendix B.1.1")],
          GROUP, TITLE, "true-positive-count", "Cumulative hits, 5 screens (independent replication)", 2)
judgement("debrouwer2026-assaybench", PR_ASB,
          "AnDCG@100, Precision@100 and dFDR@100 for 16 systems on 571 screen-ranking entries across a validation, test and post-cutoff cohort: frontier and open-weight language models, fine-tuned and prompt-optimised variants, an agent, a single-cell language model, a trained relevance predictor and retrieval and frequency baselines",
          "The broadest multi-system comparison of ranking genes for a described screen, with a post-cutoff cohort that probes whether apparent skill is prior exposure to the literature. It is proxy evidence: screens are replayed retrospectively, hits follow each screen's own criterion, and ranking quality is not target usefulness.",
          ASB_LIM, [S_ASB], [(S_ASB, "Sections 2 to 4; Tables 1 to 3")],
          GROUP, TITLE, "adjusted-ndcg-at-100", "Screen-ranking quality, 571 entries (preprint)", 3)

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
