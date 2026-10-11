"""Write scope-audit.jsonl for the genomic foundation model pass (2026-10-11).

Usage: python3 -I build-scope-audit.py
"""
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent
AT = "2026-10-11T01:10:00Z"
REVIEWER = "Claude (Opus 5.5) research agent lit-gfm-2 scope review; not a scientific validation"

INCLUDED = [
    ("doi:10.64898/2026.09.25.754388", "Buzkova et al. 2026: nine Nucleotide Transformer and DNABERT models compared with BLAST on RVDB-derived viral classification from frozen embeddings, with printed tables for pooling, PCA, BLAST comparison, corruption grids and long sequences. Independent of all models compared. Extracted (Tables 3, 7 and 10)."),
    ("arxiv:2608.05329v1", "Datta et al. 2026: frozen-embedding probing of five genomic language models against fine-tuned references on the Nucleotide Transformer benchmark, Genomic Benchmark and two Genomics Long-Range Benchmark variant-effect tasks. Independent of all models compared. Extracted (Table 1)."),
    ("doi:10.1038/s41467-025-66899-y", "You et al. 2026: eleven pre-trained genomic language models against task-specific methods on four RNA-related processes, with per-method supplementary tables. Independent of all models compared. Extracted (Supplementary Tables 4 and 5, the splicing tables)."),
]

EXCLUDED = [
    ("doi:10.1038/s41467-025-65823-8", "Already in the store (Feng et al. 2025, batch amp-feng-20261007 and dna-foundation-models-2025 source)."),
    ("doi:10.1186/s13059-025-03674-8", "Already in the store (Tang et al. 2025, batch use-case-coverage-regulatory-variant-20261009)."),
    ("doi:10.3390/genes16101223", "Already in the store (Manzo et al. 2025, same batch)."),
    ("doi:10.1186/s13040-026-00553-1", "Already in the store (fusion-breakpoint foundation model benchmark)."),
    ("doi:10.1016/j.csbj.2025.03.007", "Already in the store (quadruplex DNA language model benchmark)."),
    ("doi:10.1093/bioinformatics/btaf456", "Already in the store (tokenizer selection in genomic language models)."),
    ("arxiv:2511.02888", "Already in the store (NABench nucleotide foundation model fitness benchmark)."),
    ("doi:10.1038/s41467-025-65077-4", "DNALONGBENCH is a benchmark suite; the parallel lit-genomics teammate covers suites."),
    ("doi:10.1093/bioinformatics/btag427", "GUANinE v1.1 is a benchmark suite; left to the lit-genomics pass."),
    ("arxiv:2606.04525", "GENEB is a benchmark suite and is already represented in the store by geneb-* configurations; left to the lit-genomics pass."),
    ("doi:10.1101/2025.02.11.637758", "TraitGym is a benchmark suite and the preprint predates the window (2025-02); flagged for the lit-genomics pass."),
    ("doi:10.64898/2026.02.19.706811", "GFMBench-API is a benchmarking interface, not published results for named models on a defined benchmark."),
    ("doi:10.64898/2026.03.10.710786", "Mathur and Sachidanandam 2026, Evo 2 blind spots: in scope but could not be retrieved. bioRxiv returned HTTP 429 (rate limit) on two attempts, so no artifact could be pinned. Carried forward as a candidate."),
    ("arxiv:2604.06549v1", "Mechanistic Invariance Test, five genomic language models with printed tables: in scope, but its headline metrics (compensation sensitivity score, spacing consistency ratio) have no concept in data/vocab/metric.ttl, so extraction needs a reviewed vocabulary addition. Carried forward as a candidate."),
    ("arxiv:2606.06834v2", "Dark regulome: in scope (Caduceus, HyenaDNA, Enformer) but the per-model figures carry the values and its metrics (regulatory importance score variance decomposition) have no concept in the vocabulary. Candidate."),
    ("arxiv:2510.12617v2", "Shuffling artifacts in BEND benchmarking: concerns benchmark implementation rather than published model results, and the per-model deltas are in figures. Candidate for the suite pass."),
    ("doi:10.1021/acssynbio.6c00024", "Nullsettes, 14 genomic language models on synthetic loss-of-function cassettes: in scope, but the per-model success rates are in Figure 1C and the supplementary tables list designs and model specifications, not scores. Figures are not read by eye."),
    ("doi:10.64898/2026.02.22.707219", "He and Florea 2026, foundation models for splice site and exon annotation: in scope, but all per-model values are in Figure 1 panels; the only table lists model features."),
    ("doi:10.64898/2026.08.24.746734", "Bellido Molias and Kudla 2026, eleven splicing predictors on synthetic GFP variants: values are in figures; the single table lists predictor characteristics. Also overlaps the RNA splicing lane."),
    ("doi:10.64898/2026.06.22.730889", "Sun et al. 2026, ancestry-stratified Borzoi and AlphaGenome evaluation: per-model values are in figures and supplementary tables S1-S6 that were not retrieved in this pass. Candidate."),
    ("doi:10.64898/2026.07.10.737654", "Ramarao-Milne et al. 2026, AlphaGenome cross-species transferability: in scope; values are quoted in prose and figures rather than a printed comparison table. Candidate."),
    ("doi:10.64898/2026.02.04.703796", "Sweeney and Kang 2026, sequence-to-omics models for fine-mapping reproducibility: outcome is replication failure rate of fine-mapping, not a model benchmark metric; values in figures and supplementary tables. Candidate."),
    ("doi:10.64898/2026.07.14.738542", "Evo 2 viral-architecture benchmark: in scope; accuracies and R-squared values are quoted in the abstract and figures, with no printed results table in the retrieved text. Candidate."),
    ("doi:10.1093/nar/gkag704", "Ebbert et al. 2026, SegmentNT contextual biases: in scope as an independent evaluation, but the article prints no results table; values are in figures and the supplementary zip."),
    ("doi:10.1093/bib/bbag329", "Sun et al. 2026 splicing review and assessment of ten models including six genomic foundation models: benchmark values are in figures and a supplementary docx; the two printed tables summarise architectures and resources. Candidate, and overlaps the RNA splicing lane."),
    ("doi:10.3390/ijms27156657", "Jin et al. 2026, encoding strategies for non-coding SNPs: the printed tables are feature and interpretability profiles, not scores; results are in figures."),
    ("doi:10.1093/bib/bbag011", "McLaughlin and Lim 2026, probing Nucleotide GPT: developer study of their own model, and Europe PMC holds no full text."),
    ("doi:10.1038/s41598-026-67272-9", "Viral classification benchmark of supervised and retrieval methods: the only language-model representation is DNABERT embeddings among classical encodings, so it is a representation comparison rather than a foundation model evaluation. Low priority candidate."),
    ("doi:10.1093/femsle/fnag112", "Listeria benzalkonium tolerance benchmark: a single DNABERT-2 embedding baseline against k-mer and determinant rules in 197 isolates; the authors call it hypothesis-generating. Low priority candidate."),
    ("doi:10.1093/bib/bbaf724", "Review (comprehensive survey of genome language models): mined for primary evaluations; prints no new benchmark results."),
    ("doi:10.1038/s44320-025-00184-4", "Review (The DNA dialect, a guide to pretrained genomic language models): mined for primary evaluations; prints no new benchmark results."),
    ("doi:10.3389/fgene.2025.1634882", "Review (Gene-LLMs survey): mined; no new benchmark results."),
    ("doi:10.1093/bioadv/vbaf271", "Review (deep learning for regulatory genomics): mined; no new benchmark results."),
    ("doi:10.1093/gigascience/giag004", "Review (AI for genomic variant prediction): mined; no new benchmark results."),
    ("doi:10.1093/bib/bbag229", "Review (AI in genomics survey): mined; no new benchmark results."),
    ("doi:10.3389/fmolb.2026.1761673", "Review (noncoding variant pathogenicity paradigms): mined; no new benchmark results."),
    ("doi:10.1093/bib/bbag439", "Review (foundation models in omics): mined; no new benchmark results."),
    ("doi:10.3390/insects17090928", "Critical review proposing a benchmark agenda for sequence foundation models in insect olfactory gene discovery: proposes, does not report, benchmark results."),
    ("doi:10.1038/s41586-026-10176-5", "Evo 2 primary paper: developer study, and the model and its official sources are already in the store."),
    ("doi:10.1038/s41586-025-10014-0", "AlphaGenome primary paper: developer study, already in the store (alphagenome-2026 batch)."),
    ("doi:10.1038/s41592-026-03124-8", "SAGE-net personal-genome framework: developer study of their own framework; per-model values in figures."),
    ("doi:10.1186/s13059-025-03926-7", "Variformer personal-genome expression model: developer study of their own model."),
]

with open(OUT / "scope-audit.jsonl", "w") as f:
    for paper_id, reason in INCLUDED:
        f.write(json.dumps({"paper_id": paper_id, "decision": "included", "reason": reason,
                            "reviewed_at": AT, "reviewer": REVIEWER}, ensure_ascii=False) + "\n")
    for paper_id, reason in EXCLUDED:
        f.write(json.dumps({"paper_id": paper_id, "decision": "excluded", "reason": reason,
                            "reviewed_at": AT, "reviewer": REVIEWER}, ensure_ascii=False) + "\n")
print(len(INCLUDED) + len(EXCLUDED), "scope entries")
