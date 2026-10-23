"""Parse Tables 1, 2 and 8 of Song et al. 2025 (Virtual CRISPR, BioNLP 2025) from the
pdftotext -layout text layer of the pinned PDF and write the part file of records.

Usage:
  pdftotext -layout song2025.pdf song2025.txt
  python3 -I song2025virtualcrispr.py song2025.txt <artifact_sha256> <retrieved_at> <out.jsonl>

Row labels and counts are asserted; the script fails if the text layer does not match.
Tables 3, 4 and 7 (benchmark composition and model versions) are transcribed by hand below
and checked against the text layer by substring assertions.
"""
import json
import re
import sys

TXT, SHA, RETRIEVED_AT, OUT = sys.argv[1:5]
text = open(TXT, encoding="utf-8").read()
lines = text.splitlines()

T = "pheno-20261022"
SRC = f"{T}-source-song2025"
DATE = RETRIEVED_AT[:10]
PDF_URL = "https://aclanthology.org/2025.bionlp-1.30.pdf"
FACETS = {"areas": ["cells-tissues"], "contexts": ["research"]}
REVIEW = {
    "method": ["pdf-text-parse"],
    "reviewer": ["claude"],
    "reviewer_note": "Claude (Opus 5.5) extraction agent; no human review claimed. Extraction only; independent review is pending.",
    "date": DATE,
    "artifact_sha256": SHA,
    "retrieval_url": PDF_URL,
}


def review(note):
    return {**REVIEW, "note": note}


def region(start_pat, end_pat):
    s = next(i for i, l in enumerate(lines) if re.search(start_pat, l))
    e = next(i for i, l in enumerate(lines) if i > s and re.search(end_pat, l))
    return lines[s + 1 : e]


# ---------------------------------------------------------------- Table 1
T1_ROWS = ["Llama-2-7B", "Llama-2-13B", "Llama-2-70B", "Llama-3-8B", "Llama-3-70B", "Llama-3.1-8B",
           "Llama-3.1-70B", "Llama-3.2-1B", "Llama-3.2-3B", "Llama-3.3-70B", "o1", "o1-mini", "GPT-4o",
           "GPT-4o-mini", "GPT-4-turbo", "GPT-4", "GPT-3.5-turbo", "Random Baseline"]
cell = r"(\d\.\d\d(?: ± \d\.\d\d)?)"
t1 = {}
for l in region(r"Model\s+F1 Score\s+FPR", r"^\s*.*Table 1: Performance on the Simple"):
    m = re.search(r"(Llama-[\d.]+-\d+B|o1-mini|o1|GPT-4o-mini|GPT-4o|GPT-4-turbo|GPT-4|GPT-3\.5-turbo|Random Baseline)\s+"
                  + cell + r"\s+" + cell + r"\s*$", l)
    if m:
        assert m.group(1) not in t1, m.group(1)
        t1[m.group(1)] = (m.group(2), m.group(3))
assert list(t1) == T1_ROWS, list(t1)

# ---------------------------------------------------------------- Table 2
T2_COLS = ["AUROC", "AUPRC", "F1", "FPR", "PPV", "NPV", "Sens.", "Spec."]
reg2 = region(r"Model\s+AUROC\s+AUPRC\s+F1\s+FPR\s+PPV\s+NPV\s+Sens\.\s+Spec\.", r"^Table 2: Performance on the Difficult")
hdr = next(l for l in lines if re.search(r"Model\s+AUROC\s+AUPRC", l))
assert re.findall(r"AUROC|AUPRC|F1|FPR|PPV|NPV|Sens\.|Spec\.", hdr) == T2_COLS
t2 = {}
rows2 = [l for l in reg2 if l.strip()]
assert len(rows2) == 4, rows2
for l in rows2[:3]:
    m = re.match(r"\s*(Raw Emb\.|Summ\. Emb\.|GPT-4o \(prompting\))\s+(.*)$", l)
    assert m, l
    vals = m.group(2).split()
    assert len(vals) == 8, vals
    t2[m.group(1)] = vals
spread = rows2[3].split()
assert len(spread) == 6 and all(s.startswith("±") for s in spread), spread
assert list(t2) == ["Raw Emb.", "Summ. Emb.", "GPT-4o (prompting)"]
assert t2["GPT-4o (prompting)"][:2] == ["N/A", "N/A"]

# ---------------------------------------------------------------- Table 8
T8_COLS = ["F1", "FPR", "PPV", "NPV", "Sensitivity", "Specificity"]
reg8 = region(r"Model\s+Few-shot\s+CoT\s+F1\s+FPR\s+PPV\s+NPV\s+Sensitivity\s+Specificity", r"^Table 8: Detailed performance")
t8 = []
for l in reg8:
    if not l.strip():
        continue
    m = re.match(r"\s*(GPT-4o|Random)\s+(0-shot|1-shot \([+-]\)|2-shot \([+-]/[+-]\)|N/A)\s+(Y|N|N/A)\s+(.*)$", l)
    assert m, l
    vals = m.group(4).split()
    assert len(vals) == 6, vals
    t8.append((m.group(1), m.group(2), m.group(3), vals))
assert len(t8) == 11 and t8[-1][0] == "Random" and all(r[0] == "GPT-4o" for r in t8[:10])
assert [(r[1], r[2]) for r in t8[:10]] == [(s, c) for c in ("N", "Y") for s in
        ("0-shot", "1-shot (+)", "1-shot (-)", "2-shot (+/-)", "2-shot (-/+)")]
# Random row is printed in both Table 1 and Table 8
assert t8[-1][3][:2] == [t1["Random Baseline"][0], t1["Random Baseline"][1]]

# ---------------------------------------------------------------- hand-transcribed facts, asserted
for s in ["BioGRID-ORCS (v1.1.16)", "1175 gene-", "41.3% of these are hits", "taling 907 positive and 907 negative instances",
          "benchmark is comprised of 1814 gene-phenotype", "Our final training dataset consists of 1,678",
          "7.74% of the gene-phenotype pairs are", "contains no data from BioGRID-ORCS",
          "github.com/czbiohub-chi/immune-llm-acl", "binarized using Youden’s J statistic",
          "1837          activation", "1885          activation", "1835          activation", "1733          knockout",
          "39567689 knockout", "39385035 knockout", "temper-", "ature parameter for LLM generation was set to 0."]:
    assert s in text, s

VERSIONS = {  # Table 7
    "o1": "o1-2024-12-17", "o1-mini": "o1-mini-2024-09-12", "GPT-4o": "gpt-4o-2024-11-20",
    "GPT-4o-mini": "gpt-4o-mini-2024-07-18", "GPT-4-turbo": "gpt-4-turbo-2024-04-09", "GPT-4": "gpt-4-0125-preview",
    "GPT-3.5-turbo": "gpt-3.5-turbo-0125", "Llama-2-7B": "meta-llama/Llama-2-7b-chat-hf",
    "Llama-2-13B": "meta-llama/Llama-2-13b-chat-hf", "Llama-2-70B": "meta-llama/Llama-2-70b-chat-hf",
    "Llama-3-8B": "meta-llama/Llama-3-8B-Instruct", "Llama-3-70B": "meta-llama/Llama-3-70B-Instruct",
    "Llama-3.1-8B": "meta-llama/Llama-3.1-8B-Instruct", "Llama-3.1-70B": "meta-llama/Llama-3.1-70B-Instruct",
    "Llama-3.2-1B": "meta-llama/Llama-3.2-1B-Instruct", "Llama-3.2-3B": "meta-llama/Llama-3.2-3B-Instruct",
    "Llama-3.3-70B": "meta-llama/Llama-3.3-70B-Instruct",
}
T7_ALIAS = {"GPT-3.5-turbo": "GPT-3.5"}  # Table 1 prints GPT-3.5-turbo; Table 7 prints the alias GPT-3.5
for alias, ver in VERSIONS.items():
    assert re.search(r"\s" + re.escape(T7_ALIAS.get(alias, alias)) + r"\s+" + re.escape(ver) + r"\s*$", text, re.M), alias

records = []
add = records.append


def slug(s):
    s = s.replace("(+/-)", "pos-neg").replace("(-/+)", "neg-pos").replace("(+)", "pos").replace("(-)", "neg")
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


# ---------------------------------------------------------------- source
add({"id": SRC, "kind": "source", "name": "Virtual CRISPR: Can LLMs Predict CRISPR Screen Results?",
     "description": "Primary source retrieved and hashed for the phenotype perturbation selection use-case refresh.",
     "status": "needs_review", "facets": FACETS, "source_ids": [], "links": [],
     "attributes": {
         "url": "https://doi.org/10.18653/v1/2025.bionlp-1.30", "artifact_url": PDF_URL,
         "version": "Proceedings of the 24th Workshop on Biomedical Language Processing (BioNLP 2025), pages 354-364, 1 August 2025; ACL Anthology 2025.bionlp-1.30",
         "retrieved_at": RETRIEVED_AT, "artifact_sha256": SHA, "doi": "10.18653/v1/2025.bionlp-1.30",
         "publication_status": "peer_reviewed", "licence": "CC-BY-4.0", "media_type": "application/pdf",
         "venue": "BioNLP 2025 workshop (ACL)", "year": 2025,
         "access_and_reuse": "The ACL Anthology landing page states that material published in or after 2016 is licensed under CC BY 4.0.",
         "source_locator": "Full artifact bytes; per-record locators on each record",
         "archive_note": "Not archived in the batch; the artifact_sha256 pins the bytes that were read. Text layer kept in the extractor's scratchpad only.",
         "extraction_method": "pdftotext -layout text layer, parsed by data/omics/use-case-refresh-phenotype-20261022/extract/song2025virtualcrispr.py with row labels asserted",
         "code_url": "https://github.com/czbiohub-chi/immune-llm-acl",
     }})

# ---------------------------------------------------------------- datasets
D_SIMPLE = f"{T}-data-song2025-simple"
D_DIFF = f"{T}-data-song2025-difficult"
D_TRAIN = f"{T}-data-song2025-orcs-training"
add({"id": D_SIMPLE, "kind": "dataset", "name": "Virtual CRISPR Simple Benchmark",
     "description": "1,175 gene-phenotype queries from four BioGRID-ORCS screens, each labelled hit or no-hit.",
     "status": "needs_review", "facets": FACETS, "source_ids": [SRC], "links": [],
     "attributes": {
         "version": "BioGRID-ORCS v1.1.16; screens 1837, 1885, 1835 and 1733",
         "total": 1175, "species": "human and mouse cell models",
         "population": "1,175 gene-phenotype queries from four manually selected BioGRID-ORCS screens; 41.3% are hits",
         "assay": "Pooled CRISPR activation and knockout screens harmonised by BioGRID-ORCS",
         "label_semantics": "A hit is a statistically significant effect in the hypothesised direction; a no-hit is a statistically significant effect in the opposite direction. Genes with no significant effect are not queried.",
         "scope_note": "Table 3 per screen (Genes, Hits): 1837 activation, primary CD4+ human T cells, increased TNF-alpha secretion (423, 140); 1885 activation, J774 macrophages, phagocytic inhibition (343, 139); 1835 activation, primary CD4+ human T cells, increased IL2 secretion (243, 76); 1733 knockout, HeLa cervical adenocarcinoma cells, increased RelA nuclear translocation (166, 130). Genes counts are after filtering to genes with a significant effect.",
         "source_locator": "Sections 2.1 to 2.3; Appendix Table 3",
         "missing_metadata": {"positives": {"reason": "unreported", "note": "Only the 41.3% hit fraction and per-screen hit counts are printed, not a benchmark total"}},
     }})
add({"id": D_DIFF, "kind": "dataset", "name": "Virtual CRISPR Difficult Benchmark",
     "description": "1,814 balanced gene-phenotype queries curated from two late-2024 CRISPR screen publications.",
     "status": "needs_review", "facets": FACETS, "source_ids": [SRC], "links": [],
     "attributes": {
         "version": "Manually curated from PMID 39567689 (Chen et al. 2024, gliocidin) and PMID 39385035 (Skoulidis et al. 2024, PD1 blockade)",
         "total": 1814, "positives": 907, "negatives": 907, "species": "mouse cell models",
         "population": "1,814 gene-phenotype queries from two knockout screens in NG2-3112 mouse glioblastoma cells and 3LL Lewis lung carcinoma cells; 907 positive and 907 negative",
         "assay": "Pooled CRISPR knockout screens",
         "label_semantics": "Same high-confidence hit definition as the Simple Benchmark. To balance labels, each significant effect opposite to the hypothesised phenotype was also posed as an inverted query and labelled a hit.",
         "scope_note": "Table 4 per screen (Genes, Hits): 39567689 increased sensitivity to gliocidin (881, 73); 39385035 increased resistance to PD1 blockade (26, 23); 39567689 decreased sensitivity to gliocidin (881, 808); 39385035 decreased resistance to PD1 blockade (26, 3). The 808 and 23 rows are the inverted phenotypes. Each screen appears once per phenotype direction with the same gene count, so 2 x (881 + 26) = 1,814 queries.",
         "source_locator": "Section 2.3 'Difficult Benchmark'; Appendix Table 4",
     }})
add({"id": D_TRAIN, "kind": "dataset", "name": "Virtual CRISPR BioGRID-ORCS training set",
     "description": "Training set for the Virtual CRISPR embedding classifier: 1,678 BioGRID-ORCS screens in human or mouse cells.",
     "status": "needs_review", "facets": FACETS, "source_ids": [SRC], "links": [],
     "attributes": {
         "version": "BioGRID-ORCS v1.1.16",
         "population": "1,678 screens (from 1,924) performed in human or mouse cells; about 22.6 million gene-level results across 3 perturbation methods, 40,461 genes, 133 cell lines and 613 phenotype descriptions; 7.74% of gene-phenotype pairs are hits",
         "split": "5 randomly selected screens held out as a validation set for early stopping and hyperparameter tuning",
         "label_semantics": "High-confidence hit definition; screens reporting both significant positive and negative effects for the same gene-phenotype query were excluded. The full BioGRID-ORCS phenotype note is embedded rather than a parsed phenotype.",
         "source_locator": "Section 3",
         "missing_metadata": {"scope_note": {"reason": "unreported", "note": "The paper does not say whether the four Simple Benchmark screens were removed from the training set; the classifier is evaluated only on the Difficult Benchmark"}},
     }})

# ---------------------------------------------------------------- protocols
P_SIMPLE = f"{T}-protocol-song2025-simple-hit-classification"
P_DIFF = f"{T}-protocol-song2025-difficult-hit-classification"
common_lim = [
    "Binary classification of pre-selected gene-phenotype queries; there is no candidate pool, ranking step or test budget, so it measures hit prediction rather than which perturbations to test.",
    "Only genes with a statistically significant effect in either direction are queried; genes with no effect, which make up most of a screen, are not negatives.",
    "Retrospective: labels come from published screens and no new experiment was run.",
]
add({"id": P_SIMPLE, "kind": "protocol", "name": "Virtual CRISPR Simple Benchmark: yes/no prediction of a screen hit",
     "description": "A system answers whether a stated CRISPR perturbation of a gene in a cell line causally produces a stated phenotype, scored against high-confidence hit labels from four BioGRID-ORCS screens.",
     "status": "needs_review", "facets": FACETS, "source_ids": [SRC], "links": [{"relation": "uses_data", "target_id": D_SIMPLE}],
     "attributes": {
         "protocol": "Each query is posed as 'Does {perturbation method} of {gene} in {cell line} causally result in {phenotype}?' and the system answers Yes (hit) or No (no-hit). Prompted language models are run with zero-shot, one- or two-shot and chain-of-thought prompts at temperature 0 with a fixed seed; the binary answer is extracted from the generated text. Metrics: F1 and false positive rate, with PPV, NPV, sensitivity and specificity for GPT-4o and the random baseline in Appendix Table 8.",
         "task": "Binary hit/no-hit prediction for gene-phenotype queries from CRISPR screens",
         "version": "Song et al., BioNLP 2025, Sections 2.2, 2.3, 4.1 and Appendix A.1-A.2",
         "metric": "f1-score", "metric_direction": "higher", "unit": "fraction",
         "metric_definition": "F1 is the harmonic mean of precision and recall for the hit class; FPR is the proportion of actual negatives predicted positive. Under the high-confidence definition a false positive asserts an effect opposite to the observed significant effect.",
         "control": "Random baseline predicting hit with probability equal to the benchmark's overall hit proportion (Appendix A.2)",
         "limitations": common_lim + [
             "The four screens were selected by the authors from BioGRID-ORCS on domain knowledge, and are public, so prompted models may have seen them or their source papers in pre-training.",
             "Table 1 values are means across up to 10 prompting-strategy combinations; the o1 family was run without explicit chain-of-thought prompts, so its n is smaller and not printed.",
         ],
         "source_locator": "Sections 2.2, 2.3 and 4.1; Table 1; Appendix A.1, A.2, Tables 3 and 8",
     }})
add({"id": P_DIFF, "kind": "protocol", "name": "Virtual CRISPR Difficult Benchmark: hit prediction for complex phenotypes",
     "description": "A system predicts whether a CRISPR knockout of a gene produces a complex phenotype, on balanced queries curated from two late-2024 screen publications.",
     "status": "needs_review", "facets": FACETS, "source_ids": [SRC], "links": [{"relation": "uses_data", "target_id": D_DIFF}],
     "attributes": {
         "protocol": "Same query form as the Simple Benchmark. The embedding classifier outputs a probability, binarised with Youden's J statistic, and is scored with AUROC, AUPRC, F1, FPR, PPV, NPV, sensitivity and specificity. GPT-4o is scored from its binary answers, averaged across prompting strategies; AUROC and AUPRC are undefined for it.",
         "task": "Binary hit/no-hit prediction for gene-phenotype queries from CRISPR screens",
         "version": "Song et al., BioNLP 2025, Sections 2.3, 3 and 4.2",
         "metric": "f1-score", "metric_direction": "higher", "unit": "fraction",
         "metric_definition": "As for the Simple Benchmark; AUROC and AUPRC are computed from the classifier's predicted probabilities.",
         "limitations": common_lim + [
             "Labels are balanced by construction: every gene appears once per phenotype direction with opposite labels, so the benchmark tests whether the direction of effect is predicted.",
             "Two screens from two publications, both in mouse cells; the authors call the test set constrained by the availability of suitable post-cutoff screens.",
             "No random-baseline row is printed for this benchmark.",
             "The Youden's J threshold is chosen on predicted probabilities; the paper does not say whether it was set on the validation set or on the test set.",
         ],
         "source_locator": "Sections 2.3, 3 and 4.2; Table 2; Appendix A.3 and Table 4; Limitations",
     }})

# ---------------------------------------------------------------- models
REUSE = {"GPT-4o": "tgtval-20261009-model-gpt-4o", "o1-mini": "tgtval-20261009-model-o1-mini",
         "GPT-3.5-turbo": "tgtval-20261009-model-gpt-3-5-turbo", "Llama-3.1-8B": "tgtval-20261009-model-llama-3-1-8b",
         "Llama-3.1-70B": "egfrnsclc-20261009-model-llama-3-1-70b"}
NEW = {
    "Llama-2-7B": ("Llama 2 7B Chat", "Chat-tuned 7-billion-parameter model in Meta's Llama 2 family of open-weight language models.", "checkpoint"),
    "Llama-2-13B": ("Llama 2 13B Chat", "Chat-tuned 13-billion-parameter model in Meta's Llama 2 family of open-weight language models.", "checkpoint"),
    "Llama-2-70B": ("Llama 2 70B Chat", "Chat-tuned 70-billion-parameter model in Meta's Llama 2 family of open-weight language models.", "checkpoint"),
    "Llama-3-8B": ("Llama 3 8B Instruct", "Instruction-tuned 8-billion-parameter model in Meta's Llama 3 family of open-weight language models.", "checkpoint"),
    "Llama-3-70B": ("Llama 3 70B Instruct", "Instruction-tuned 70-billion-parameter model in Meta's Llama 3 family of open-weight language models.", "checkpoint"),
    "Llama-3.2-1B": ("Llama 3.2 1B Instruct", "Instruction-tuned 1-billion-parameter text model in Meta's Llama 3.2 collection of open-weight language models.", "checkpoint"),
    "Llama-3.2-3B": ("Llama 3.2 3B Instruct", "Instruction-tuned 3-billion-parameter text model in Meta's Llama 3.2 collection of open-weight language models.", "checkpoint"),
    "Llama-3.3-70B": ("Llama 3.3 70B Instruct", "Instruction-tuned 70-billion-parameter text model in Meta's Llama 3.3 release of open-weight language models.", "checkpoint"),
    "o1": ("o1", "OpenAI reasoning language model that generates an internal chain of thought before giving its answer.", "service"),
    "GPT-4o-mini": ("GPT-4o mini", "Smaller, lower-cost OpenAI language model in the GPT-4o line, served through the OpenAI API.", "service"),
    "GPT-4-turbo": ("GPT-4 Turbo", "OpenAI GPT-4 Turbo large language model with a longer context window than the original GPT-4, served through the OpenAI API.", "service"),
    "GPT-4": ("GPT-4 (gpt-4-0125-preview)", "OpenAI GPT-4 large language model at the gpt-4-0125-preview API snapshot.", "service"),
}
M = dict(REUSE)
for alias, (name, desc, level) in NEW.items():
    mid = f"{T}-model-song2025-{slug(alias)}"
    M[alias] = mid
    open_w = alias.startswith("Llama")
    add({"id": mid, "kind": "model", "name": name, "description": desc, "status": "needs_review",
         "facets": {**FACETS, "method_types": ["foundation_model"]}, "source_ids": [SRC], "links": [],
         "attributes": {"entity_level": level, "reported_name": alias, "version": VERSIONS[alias],
                        "access": "Open weights from Hugging Face, served with vLLM" if open_w else "Commercial API (OpenAI)",
                        "source_locator": "Appendix Table 7; Appendix A.1",
                        "provenance_note": "Version string as printed in Appendix Table 7 of Song et al. 2025. The description is general knowledge of the model line, not taken from the source.",
                        "missing_metadata": {"training_data": {"reason": "unreported"}}}})
M_EMB = f"{T}-model-song2025-text-embedding-3-large"
add({"id": M_EMB, "kind": "model", "name": "text-embedding-3-large",
     "description": "OpenAI text embedding model that maps a text string to a 3,072-dimensional vector.",
     "status": "needs_review", "facets": {**FACETS, "method_types": ["foundation_model"]}, "source_ids": [SRC], "links": [],
     "attributes": {"entity_level": "service", "reported_name": "text-embedding-3-large", "access": "Commercial API (OpenAI)",
                    "source_locator": "Section 4.2; Appendix A.3",
                    "missing_metadata": {"version": {"reason": "unreported", "note": "No snapshot date is printed"},
                                         "training_data": {"reason": "unreported"}}}})

# ---------------------------------------------------------------- methods
METH_EMB = f"{T}-method-song2025-virtual-crispr-embedding-classifier"
METH_RAND = f"{T}-method-song2025-random-hit-classifier"
add({"id": METH_EMB, "kind": "method", "name": "Virtual CRISPR embedding classifier",
     "description": "Multilayer perceptron that predicts whether perturbing a gene in a cell line produces a phenotype, from concatenated LLM text embeddings of the perturbation method, gene, cell line and phenotype.",
     "status": "needs_review", "facets": {**FACETS, "method_types": ["supervised_machine_learning"]}, "source_ids": [SRC], "links": [],
     "attributes": {"reported_name": "Embedding-Based Classifier", "entity_level": "method",
                    "access": "Code and benchmark data at https://github.com/czbiohub-chi/immune-llm-acl (not pinned to a commit in this pass)",
                    "source_locator": "Section 4.2; Figure 2; Appendix A.3; Ethics Statement",
                    "missing_metadata": {"version": {"reason": "inapplicable", "note": "Method record; settings are on configurations"}}}})
add({"id": METH_RAND, "kind": "method", "name": "Hit-frequency-weighted random classifier",
     "description": "Predicts hit or no-hit at random, with the probability of predicting a hit set to the proportion of hits in the benchmark being evaluated.",
     "status": "needs_review", "facets": {**FACETS, "method_types": ["conventional_pipeline"]}, "source_ids": [SRC], "links": [],
     "attributes": {"reported_name": "Random Baseline", "entity_level": "method", "source_locator": "Appendix A.2",
                    "missing_metadata": {"version": {"reason": "inapplicable", "note": "Method record; settings are on configurations"}}}})

# ---------------------------------------------------------------- configurations
C = {}


def config(cid, name, desc, links, attrs, method_types):
    add({"id": cid, "kind": "configuration", "name": name, "description": desc, "status": "needs_review",
         "facets": {**FACETS, "method_types": method_types}, "source_ids": [SRC], "links": links, "attributes": attrs})
    return cid


for alias in T1_ROWS[:-1]:
    open_w = alias.startswith("Llama")
    C[alias] = config(
        f"{T}-config-song2025-{slug(alias)}-prompting-mean",
        f"{alias}, direct prompting, mean over prompting strategies (Song et al. 2025)",
        f"{alias} answering yes/no CRISPR screen questions by direct prompting, summarised over zero-shot, few-shot and chain-of-thought prompt variants.",
        [{"relation": "configuration_of", "target_id": M[alias]}],
        {"reported_name": alias, "configuration_type": "paper_evaluation", "foundation_model_eligible": True,
         "version": VERSIONS[alias], "model_version": VERSIONS[alias],
         "parameters": "Direct prompting; up to 10 combinations of chain-of-thought and 0-, 1- or 2-shot examples" + (
             "; explicit chain-of-thought prompts omitted for the o1 family" if alias.startswith("o1") else ""),
         "temperature_note": "Temperature 0 with a fixed random seed",
         "access_reuse": "Hugging Face weights served with vLLM's OpenAI-compatible server on 2x A100 80GB" if open_w else "OpenAI API",
         "source_locator": f"Table 1, row '{alias}'; Appendix A.1 and Table 7",
         "provenance_note": "Prompted by Song et al. 2025; the model is third-party."},
        ["foundation_model"])

for (_, shot, cot, _vals) in t8[:10]:
    key = f"GPT-4o {shot} CoT={cot}"
    C[key] = config(
        f"{T}-config-song2025-gpt-4o-{slug(shot)}-cot-{cot.lower()}",
        f"GPT-4o, {shot}, {'with' if cot == 'Y' else 'without'} chain-of-thought (Song et al. 2025)",
        f"GPT-4o answering yes/no CRISPR screen questions with a {shot} prompt {'and' if cot == 'Y' else 'and no'} chain-of-thought instruction.",
        [{"relation": "configuration_of", "target_id": M["GPT-4o"]}],
        {"reported_name": "GPT-4o", "configuration_type": "paper_evaluation", "foundation_model_eligible": True,
         "version": VERSIONS["GPT-4o"], "model_version": VERSIONS["GPT-4o"],
         "parameters": f"Few-shot: {shot}; CoT: {cot}. (+)/(-) mark positive/negative examples; for 2-shot the order is given",
         "temperature_note": "Temperature 0 with a fixed random seed", "access_reuse": "OpenAI API",
         "source_locator": f"Appendix Table 8, row 'GPT-4o', Few-shot '{shot}', CoT '{cot}'",
         "provenance_note": "Prompted by Song et al. 2025; the model is third-party."},
        ["foundation_model"])

C["Random"] = config(
    f"{T}-config-song2025-random-simple",
    "Random baseline, Simple Benchmark hit rate (Song et al. 2025)",
    "Random hit/no-hit predictions with the hit probability set to the Simple Benchmark's hit proportion.",
    [{"relation": "configuration_of", "target_id": METH_RAND}],
    {"reported_name": "Random Baseline", "configuration_type": "paper_evaluation", "foundation_model_eligible": False,
     "parameters": "Hit probability weighted by the overall hit proportion of the benchmark (41.3% for the Simple Benchmark)",
     "source_locator": "Table 1, row 'Random Baseline'; Appendix Table 8, row 'Random'; Appendix A.2",
     "missing_metadata": {"version": {"reason": "inapplicable", "note": "No software release involved"}}},
    ["conventional_pipeline"])

emb_common = ("text-embedding-3-large embeddings (3,072 dimensions) of perturbation method, gene symbol, cell line and phenotype, "
              "concatenated to 12,288 dimensions; 5-layer MLP with hidden layers [6144, 3072, 1536, 768]; binary cross-entropy; "
              "AdamW lr 0.001, weight decay 0.01, batch 8192; LR reduced after 5 epochs without validation improvement; early stopping after 15; "
              "probabilities binarised with Youden's J statistic")
C["Raw Emb."] = config(
    f"{T}-config-song2025-embedding-classifier-raw",
    "Virtual CRISPR embedding classifier, raw-text embeddings (Song et al. 2025)",
    "Embedding classifier whose inputs are embeddings of the raw text of each screen component.",
    [{"relation": "configuration_of", "target_id": METH_EMB}, {"relation": "uses_model", "target_id": M_EMB}],
    {"reported_name": "Raw Emb.", "configuration_type": "paper_evaluation", "foundation_model_eligible": False,
     "parameters": emb_common + "; converged after 4 epochs",
     "training_setting": "Trained on 1,678 BioGRID-ORCS v1.1.16 screens, 5 screens held out for validation",
     "score_training_overlap": "Evaluated only on the Difficult Benchmark, which the authors state contains no BioGRID-ORCS data",
     "access_reuse": "Code at https://github.com/czbiohub-chi/immune-llm-acl (not pinned)",
     "source_locator": "Table 2, row 'Raw Emb.'; Section 4.2; Appendix A.3",
     "missing_metadata": {"version": {"reason": "unreported", "note": "No release, commit or weights checksum printed"}}},
    ["supervised_machine_learning"])
C["Summ. Emb."] = config(
    f"{T}-config-song2025-embedding-classifier-summary",
    "Virtual CRISPR embedding classifier, GPT-4o summary embeddings (Song et al. 2025)",
    "Embedding classifier whose inputs are embeddings of GPT-4o-generated summaries of each screen component.",
    [{"relation": "configuration_of", "target_id": METH_EMB}, {"relation": "uses_model", "target_id": M_EMB},
     {"relation": "uses_model", "target_id": M["GPT-4o"]}],
    {"reported_name": "Summ. Emb.", "configuration_type": "paper_evaluation", "foundation_model_eligible": False,
     "parameters": emb_common + "; component texts first summarised by GPT-4o (Appendix Table 6 prompt); trained for 3 epochs",
     "training_setting": "Trained on 1,678 BioGRID-ORCS v1.1.16 screens, 5 screens held out for validation",
     "score_training_overlap": "Evaluated only on the Difficult Benchmark, which the authors state contains no BioGRID-ORCS data",
     "access_reuse": "Code at https://github.com/czbiohub-chi/immune-llm-acl (not pinned)",
     "source_locator": "Table 2, row 'Summ. Emb.'; Section 4.2; Appendix A.3 and Table 6",
     "missing_metadata": {"version": {"reason": "unreported", "note": "No release, commit or weights checksum printed"},
                          "model_version": {"reason": "unreported", "note": "The GPT-4o snapshot used for summaries is not stated"}}},
    ["supervised_machine_learning"])

# ---------------------------------------------------------------- evaluations and results
METRIC = {"F1": ("f1-score", "higher", "fraction"), "FPR": ("false-positive-rate", "lower", "fraction"),
          "PPV": ("precision", "higher", "fraction"), "NPV": ("negative-predictive-value", "higher", "fraction"),
          "Sens.": ("recall", "higher", "fraction"), "Sensitivity": ("recall", "higher", "fraction"),
          "Spec.": ("specificity", "higher", "fraction"), "Specificity": ("specificity", "higher", "fraction"),
          "AUROC": ("auroc", "higher", "unitless"), "AUPRC": ("auprc", "higher", "unitless")}

SIMPLE_CMP = {"protocol_id": P_SIMPLE, "dataset_version": "BioGRID-ORCS v1.1.16, screens 1837, 1885, 1835, 1733",
              "split": "Fixed evaluation set of 1,175 queries; no training on it",
              "population": "1,175 gene-phenotype queries, 41.3% hits",
              "inputs": "Natural-language question naming perturbation method, gene, cell line and phenotype",
              "metric_implementation": "Binary Yes/No answer extracted from generated text; metrics over queries",
              "budget": None}
DIFF_CMP = {**SIMPLE_CMP, "protocol_id": P_DIFF,
            "dataset_version": "Curated from PMID 39567689 and PMID 39385035",
            "split": "Fixed evaluation set of 1,814 queries; no data from BioGRID-ORCS",
            "population": "1,814 gene-phenotype queries, 907 positive and 907 negative"}
TXT_NOTE = "Extracted by deterministic parse of the pdftotext -layout text layer of the pinned PDF (extract/song2025virtualcrispr.py), row labels and counts asserted."

evals_n = results_n = 0


def evaluation(eid, name, system, protocol, data, origin, cmp, locator, limitations=None, missing=None):
    global evals_n
    evals_n += 1
    a = {"origin": origin, "protocol": protocol, "version": f"Primary source as retrieved {DATE}", "comparison": cmp,
         "source_locator": locator, "retrospective": True}
    if limitations:
        a["limitations"] = limitations
    if missing:
        a["missing_metadata"] = missing
    add({"id": eid, "kind": "evaluation", "name": name, "description": "Published comparison; transcribed, not reproduced.",
         "status": "needs_review", "facets": FACETS, "source_ids": [SRC],
         "links": [{"relation": "system", "target_id": system}, {"relation": "assessment", "target_id": protocol},
                   {"relation": "data", "target_id": data}], "attributes": a})
    return eid


def result(eid, col, printed, qualifier, locator, unc=None, extra=None, unc_missing_note=None):
    global results_n
    results_n += 1
    metric, direction, unit = METRIC[col]
    a = {"metric": metric, "metric_qualifier": qualifier, "metric_direction": direction, "unit": unit,
         "printed_value": printed, "numeric_value": printed if re.fullmatch(r"\d+\.\d+", printed) else None,
         "source_locator": locator, "review": review(TXT_NOTE)}
    if unc:
        a["uncertainty"] = unc
    else:
        a["missing_metadata"] = {"uncertainty": {"reason": "unreported", **({"note": unc_missing_note} if unc_missing_note else {})}}
    if extra:
        a.update(extra)
    rid = f"{eid.replace('-eval-', '-result-')}-{metric}"
    add({"id": rid, "kind": "result", "name": f"{eid.split(T + '-eval-')[1]} {metric}",
         "description": "Reported measurement transcribed from the pinned source. Not independently reproduced.",
         "status": "needs_review", "facets": {}, "source_ids": [SRC], "links": [{"relation": "evaluation", "target_id": eid}],
         "attributes": a})


THIRD = ["The language model was built by a third party; Song et al. designed the prompts and ran it."]
# Table 1
for alias in T1_ROWS:
    f1, fpr = t1[alias]
    if alias == "Random Baseline":
        eid = evaluation(f"{T}-eval-song2025-random-simple", "Random baseline on the Virtual CRISPR Simple Benchmark",
                         C["Random"], P_SIMPLE, D_SIMPLE, "author_reported",
                         {**SIMPLE_CMP, "adaptation": "None; random predictions weighted by the benchmark hit proportion", "aggregation": None},
                         "Table 1, row 'Random Baseline'; Appendix Table 8, row 'Random'",
                         missing={"seed": {"reason": "unreported", "note": "Not stated whether the values are one draw or an expectation"}})
        t8r = t8[-1][3]
        occ = lambda col: {"source_occurrences": [{"source_id": SRC, "locator": f"Appendix Table 8, row 'Random', column '{col}'"}]}
        result(eid, "F1", f1, "Simple Benchmark", "Table 1, row 'Random Baseline', column 'F1 Score'", extra=occ("F1"))
        result(eid, "FPR", fpr, "Simple Benchmark", "Table 1, row 'Random Baseline', column 'FPR'", extra=occ("FPR"))
        for col, v in zip(T8_COLS[2:], t8r[2:]):
            result(eid, col, v, "Simple Benchmark", f"Appendix Table 8, row 'Random', column '{col}'")
        continue
    eid = evaluation(f"{T}-eval-song2025-{slug(alias)}-prompting-mean-simple",
                     f"{alias} (direct prompting, mean over strategies) on the Virtual CRISPR Simple Benchmark",
                     C[alias], P_SIMPLE, D_SIMPLE, "independent_paper",
                     {**SIMPLE_CMP, "adaptation": "Direct prompting, no fine-tuning",
                      "aggregation": "Mean and standard deviation across up to 10 combinations of chain-of-thought and few-shot prompting strategies"},
                     f"Table 1, row '{alias}'", limitations=THIRD)
    for col, v in (("F1", f1), ("FPR", fpr)):
        c, s = v.split(" ± ")
        result(eid, col, v, "Simple Benchmark", f"Table 1, row '{alias}', column '{'F1 Score' if col == 'F1' else 'FPR'}'",
               unc={"type": "standard_deviation", "value": s, "printed": f"± {s}",
                    "scope": "across prompting-strategy combinations for this model",
                    "note": "Caption: mean and std. dev. across up to 10 combinations of CoT and few-shot prompting; the number of combinations per model is not printed"})
        # numeric_value is the mean, not the whole printed string
        records[-1]["attributes"]["numeric_value"] = c

# Table 8 (GPT-4o rows)
for (_, shot, cot, vals) in t8[:10]:
    key = f"GPT-4o {shot} CoT={cot}"
    eid = evaluation(f"{T}-eval-song2025-gpt-4o-{slug(shot)}-cot-{cot.lower()}-simple",
                     f"GPT-4o, {shot}, CoT {cot}, on the Virtual CRISPR Simple Benchmark",
                     C[key], P_SIMPLE, D_SIMPLE, "independent_paper",
                     {**SIMPLE_CMP, "adaptation": f"Direct prompting: {shot}, chain-of-thought {cot}",
                      "aggregation": "Single prompting strategy, one run at temperature 0"},
                     f"Appendix Table 8, row 'GPT-4o', Few-shot '{shot}', CoT '{cot}'", limitations=THIRD)
    for col, v in zip(T8_COLS, vals):
        result(eid, col, v, "Simple Benchmark", f"Appendix Table 8, row 'GPT-4o' / '{shot}' / CoT '{cot}', column '{col}'")

# Table 2
t2_spread = dict(zip(T2_COLS[2:], [s.replace("±", "") for s in spread]))
for row, cfg in (("Raw Emb.", C["Raw Emb."]), ("Summ. Emb.", C["Summ. Emb."]), ("GPT-4o (prompting)", C["GPT-4o"])):
    gpt = row.startswith("GPT")
    eid = evaluation(
        f"{T}-eval-song2025-{'gpt-4o-prompting-mean' if gpt else 'embedding-classifier-' + ('raw' if row.startswith('Raw') else 'summary')}-difficult",
        f"{row} on the Virtual CRISPR Difficult Benchmark", cfg, P_DIFF, D_DIFF,
        "independent_paper" if gpt else "author_reported",
        {**DIFF_CMP,
         "adaptation": "Direct prompting, no fine-tuning" if gpt else "Supervised MLP on LLM embeddings, trained on BioGRID-ORCS",
         "metric_implementation": ("Binary Yes/No answer extracted from generated text; metrics over queries" if gpt else
                                   "AUROC and AUPRC from predicted probabilities; other metrics after binarising with Youden's J statistic"),
         "aggregation": "Averaged across prompting strategies; spread statistic not named" if gpt else "Single trained model; one evaluation"},
        f"Table 2, row '{row}'", limitations=THIRD if gpt else ["Authors' own method."])
    for col, v in zip(T2_COLS, t2[row]):
        loc = f"Table 2, row '{row}', column '{col}'"
        if v == "N/A":
            result(eid, col, v, "Difficult Benchmark", loc,
                   extra={"undefined_reason": "Table 2 caption: GPT-4o prompting gives binary outputs and thus AUROC and AUPRC are undefined"},
                   unc_missing_note=None)
            records[-1]["attributes"]["missing_metadata"] = {"uncertainty": {"reason": "inapplicable"}}
        elif gpt:
            result(eid, col, v, "Difficult Benchmark", loc,
                   unc={"type": "unresolved_spread", "value": t2_spread[col], "printed": f"±{t2_spread[col]}",
                        "scope": "across prompting strategies",
                        "note": "Printed on the line below the row; the caption says results are aggregated across prompting strategies but does not name the statistic. Table 1 uses mean and standard deviation for the same kind of aggregation."})
        else:
            result(eid, col, v, "Difficult Benchmark", loc)

# ---------------------------------------------------------------- claims
claims = [
    ("leakage-control", D_DIFF, "leakage_control",
     "The Difficult Benchmark is built from two publications released in late 2024, selected because they post-date the training cutoffs of all evaluated LLMs, and contains no data from BioGRID-ORCS.",
     "Section 2.1 item (2); Section 3 last sentence; Limitations"),
    ("simple-from-orcs", D_SIMPLE, "leakage_control",
     "The Simple Benchmark's four screens come from BioGRID-ORCS v1.1.16, the same database the embedding classifier is trained on; the authors evaluate the classifier only on the Difficult Benchmark to avoid that overlap. Only prompted LLMs are scored on the Simple Benchmark.",
     "Section 2.3 'Simple Benchmark'; Section 3"),
    ("training-data", METH_EMB, "training_data",
     "Trained on 1,678 BioGRID-ORCS v1.1.16 screens in human or mouse cells (about 22.6 million gene-level results; 7.74% hits under the high-confidence definition), with 5 screens held out for validation.",
     "Section 3"),
    ("stated-purpose", METH_EMB, "intended_use",
     "The authors present in silico prediction of CRISPR screen outcomes as a way to prioritise experiments and guide screen design, and propose using failures of LLM prediction on robust hits to flag novel biology. The evaluation itself is binary classification of pre-selected gene-phenotype queries; in vitro validation of predictions is listed as future work.",
     "Abstract; Section 5; Limitations and Future Work"),
]
for suffix, subj, field, value, loc in claims:
    add({"id": f"{T}-claim-song2025-{suffix}", "kind": "claim", "name": f"{field}: {subj}",
         "description": "Descriptive fact transcribed from the pinned source.", "status": "needs_review", "facets": {},
         "source_ids": [SRC], "links": [{"relation": "subject", "target_id": subj}],
         "attributes": {"field": field, "value": value, "source_locator": loc,
                        "review": review("Hand transcription from the PDF text layer.")}})

assert evals_n == 31, evals_n
assert results_n == 124, results_n
ids = [r["id"] for r in records]
assert len(ids) == len(set(ids)), "duplicate ids"
for r in records:
    assert re.fullmatch(r"[a-z0-9][a-z0-9-]{0,254}", r["id"]), r["id"]
records.sort(key=lambda r: r["id"])
with open(OUT, "w", encoding="utf-8") as fh:
    for r in records:
        fh.write(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n")
print(f"{len(records)} records: {evals_n} evaluations, {results_n} results")
