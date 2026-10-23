"""Parse Table 1 and Supplementary Table 4 of Edwards et al. 2026 (AssayLoop, arXiv:2609.11877v1)
and write the extraction part for this source.

Usage:
  python3 -I edwards2026assayloop.py <pdftotext -layout text of the pinned PDF> <output part.jsonl>

The text layer is produced with `pdftotext -layout` from the PDF whose SHA-256 is
adcaaa5b7f9bd0e3bc1f91d94d26c8d4924c5c0b3064b6625c01ba92c6eaef28. Row labels are asserted in
order for both tables. Every value printed more than once for the same run (Table 1 against
Supplementary Table 4, and the repeated rows inside Supplementary Table 4) is asserted equal;
each distinct run is stored once (see notes/edwards2026assayloop.md).
"""
import json
import re
import sys

P = "ucpheno-20261022"
SRC = f"{P}-source-edwards2026"
SHA = "adcaaa5b7f9bd0e3bc1f91d94d26c8d4924c5c0b3064b6625c01ba92c6eaef28"
PDF_URL = "https://arxiv.org/pdf/2609.11877v1"
PROTOCOL = f"{P}-protocol-edwards2026-assaybench-loop-test-10x100"
DATA = f"{P}-data-edwards2026-assaybench-loop-test"
BASELINE = f"{P}-baseline-edwards2026-random-policy"
FACETS = {"areas": ["cells-tissues"], "contexts": ["research"]}
TODAY = "2026-10-22"
EXTRACTOR = "Claude (Opus 5.5) extraction agent in the evidence-pass workflow; no human review claimed"

# ---------------------------------------------------------------- table specs
T1_COLS = ["EF (↑)", "nAUC (%)(↑)", "FH (%)(↑)", "SF (%)(↓)", "%ess (%)", "EP-B", "EP-S", "EP-D"]
T1_KEYS = ["ef", "nauc", "fh", "sf", "ess", "epb", "eps", "epd"]
S4_COLS = ["EF", "nAUC (%)", "Frac. hits (%)", "Shortfall (%)", "Ess. (%)", "Vendi (%)", "Path. Ov.",
           "EP-B", "EP-S", "EP-D"]
S4_KEYS = ["ef", "nauc", "fh", "sf", "ess", "vendi", "po", "epb", "eps", "epd"]

# (group, printed label, system slug). Order is asserted.
T1_ROWS = [
    ("Base LLMs", "GLM-5.1", "glm-5-1"),
    ("Base LLMs", "w/o labels", "glm-5-1-no-labels"),
    ("Base LLMs", "Gemini-3.1-Pro", "gemini-3-1-pro"),
    ("Base LLMs", "w/o labels", "gemini-3-1-pro-no-labels"),
    ("Base LLMs", "GPT-5.6 Sol", "gpt-5-6-sol"),
    ("AssayLLM (Ours)", "Qwen3.6-27B (base)", "qwen3-6-27b"),
    ("AssayLLM (Ours)", "+ SFT (GLM-5.1 traces)", "qwen3-6-27b-sft"),
    ("AssayLLM (Ours)", "+ SFT + GRPO (= AssayLLM)", "assayllm"),
    ("Adaptive Experimental Design Methods", "Random", "random"),
    ("Adaptive Experimental Design Methods", "Prior hit baseline", "prior-hit"),
    ("Adaptive Experimental Design Methods", "Screen-kNN", "screen-knn"),
    ("Adaptive Experimental Design Methods", "BPMF [41]", "bpmf-greedy"),
    ("Adaptive Experimental Design Methods", "MAML (w/ BPMF embs.) [12, 41]", "maml-bpmf"),
    ("Adaptive Experimental Design Methods", "BioBO [27]", "biobo"),
    ("Adaptive Experimental Design Methods", "Probability-of-hit [40]", "probability-of-hit"),
    ("Agent Harnesses", "Haiku-4.5 Agent", "haiku-4-5-coding-agent"),
    ("Agent Harnesses", "LLMNN [17]", "llmnn"),
    ("Agent Harnesses", "ICBR-EF [51]", "icbr-ef"),
    ("AssayFormer (Ours)", "AssayFormer (random embs.)", "assayformer-random-emb-sft"),
    ("AssayFormer (Ours)", "+ BPMF Embeddings", "assayformer-bpmf-sft"),
    ("AssayFormer (Ours)", "+ GRPO (= AssayFormer)", "assayformer"),
    ("AssayLoop (Ours)", "GLM-5.1 → AssayFormer", "assayloop-glm-5-1"),
    ("AssayLoop (Ours)", "Gemini-3.1-Pro → AssayFormer", "assayloop-gemini-3-1-pro"),
    ("AssayLoop (Ours)", "GPT-5.6 Sol → AssayFormer", "assayloop-gpt-5-6-sol"),
    ("AssayLoop (Ours)", "AssayLLM → AssayFormer", "assayloop-assayllm"),
    ("AssayLoop (Ours)", "Handoff-trained AssayLLM → AssayFormer", "assayloop-assayllm-handoff"),
]
T1_GROUPS = ["Base LLMs", "AssayLLM (Ours)", "Adaptive Experimental Design Methods", "Agent Harnesses",
             "AssayFormer (Ours)", "AssayLoop (Ours)"]

S4_ROWS = [
    ("Base LLMs", "GLM-5.1", "glm-5-1"),
    ("Base LLMs", "- hit labels", "glm-5-1-no-labels"),
    ("Base LLMs", "GLM-5.2", "glm-5-2"),
    ("Base LLMs", "Kimi-K2.6", "kimi-k2-6"),
    ("Base LLMs", "- hit labels", "kimi-k2-6-no-labels"),
    ("Base LLMs", "Claude Opus-4.8", "claude-opus-4-8"),
    ("Base LLMs", "- hit labels", "claude-opus-4-8-no-labels"),
    ("Base LLMs", "Claude Sonnet-4.6", "claude-sonnet-4-6"),
    ("Base LLMs", "Claude Haiku-4.5", "claude-haiku-4-5"),
    ("Base LLMs", "Qwen3.6-27B", "qwen3-6-27b"),
    ("Base LLMs", "- hit labels", "qwen3-6-27b-no-labels"),
    ("Base LLMs", "Gemini-3.1-pro", "gemini-3-1-pro"),
    ("Base LLMs", "- hit labels", "gemini-3-1-pro-no-labels"),
    ("Base LLMs", "GPT-5.5", "gpt-5-5"),
    ("Base LLMs", "GPT-5.6 Sol", "gpt-5-6-sol"),
    ("AssayLLM (Ours)", "Qwen3.6-27B (base)", "qwen3-6-27b"),
    ("AssayLLM (Ours)", "+ SFT (GLM-5.1 traces)", "qwen3-6-27b-sft"),
    ("AssayLLM (Ours)", "+ SFT + GRPO (= AssayLLM)", "assayllm"),
    ("Adaptive Experimental Design Methods", "Random", "random"),
    ("Adaptive Experimental Design Methods", "Prior hit baseline", "prior-hit"),
    ("Adaptive Experimental Design Methods", "Screen-kNN", "screen-knn"),
    ("Adaptive Experimental Design Methods", "RF (greedy)", "rf-greedy"),
    ("Adaptive Experimental Design Methods", "RF + UCB", "rf-ucb"),
    ("Adaptive Experimental Design Methods", "BPMF [41]", "bpmf-greedy"),
    ("Adaptive Experimental Design Methods", "Transformer + DAgger [39]", "transformer-dagger"),
    ("Adaptive Experimental Design Methods", "MAML (w/ BPMF embs.) [12, 41]", "maml-bpmf"),
    ("Adaptive Experimental Design Methods", "BioBO [27]", "biobo"),
    ("Adaptive Experimental Design Methods", "Probability-of-hit [40]", "probability-of-hit"),
    ("Agent Harnesses", "Haiku-4.5 Agent", "haiku-4-5-coding-agent"),
    ("Agent Harnesses", "LLMNN [17]", "llmnn"),
    ("Agent Harnesses", "ICBR-EF [51]", "icbr-ef"),
    ("AssayFormer (Ours)", "AssayFormer (random embs.)", "assayformer-random-emb-sft"),
    ("AssayFormer (Ours)", "+ BPMF Embeddings", "assayformer-bpmf-sft"),
    ("AssayFormer (Ours)", "+ GRPO (= AssayFormer)", "assayformer"),
    ("AssayLoop (Ours)", "GLM-5.1 → AssayFormer", "assayloop-glm-5-1"),
    ("AssayLoop (Ours)", "Gemini-3.1-Pro → AssayFormer", "assayloop-gemini-3-1-pro"),
    ("AssayLoop (Ours)", "GPT-5.5 → AssayFormer", "assayloop-gpt-5-5"),
    ("AssayLoop (Ours)", "GPT-5.6 Sol → AssayFormer", "assayloop-gpt-5-6-sol"),
    ("AssayLoop (Ours)", "AssayLLM → AssayFormer", "assayloop-assayllm"),
    ("AssayLoop (Ours)", "Handoff-trained AssayLLM →AssayFormer", "assayloop-assayllm-handoff"),
    ("Ablations", "AssayFormer (Random)", "assayformer-random-emb-sft"),
    ("Ablations", "AssayFormer (BPMF)", "assayformer-bpmf-sft"),
    ("Ablations", "- screen desc.", "assayformer-bpmf-sft-no-desc"),
    ("Ablations", "AssayFormer (SVD)", "assayformer-svd-sft"),
    ("Ablations", "AssayFormer (MF)", "assayformer-mf-sft"),
    ("Ablations", "AssayFormer (MF-Sphere)", "assayformer-mf-sphere-sft"),
    ("Ablations", "AssayFormer (GenePT-PCA)", "assayformer-genept-pca-sft"),
    ("Ablations", "AssayFormer (K562-PCA)", "assayformer-k562-pca-sft"),
    ("Ablations", "Random + GRPO", "assayformer-random-emb-grpo"),
    ("Ablations", "BPMF + GRPO", "assayformer"),
    ("Ablations", "BPMF (no desc.) + GRPO", "assayformer-no-desc-grpo"),
    ("Ablations", "BPMF + GRPO (EFterminal )", "assayformer-ef-terminal-grpo"),
    ("Ablations", "SVD + GRPO", "assayformer-svd-grpo"),
    ("Ablations", "MF + GRPO", "assayformer-mf-grpo"),
    ("Ablations", "MF-Sphere + GRPO", "assayformer-mf-sphere-grpo"),
    ("Ablations", "GenePT-PCA + GRPO", "assayformer-genept-pca-grpo"),
    ("Ablations", "K562-PCA + GRPO", "assayformer-k562-pca-grpo"),
]
S4_GROUPS = T1_GROUPS + ["Ablations"]

NUM = re.compile(r"^-?\d+(?:\.\d+)?$")


def parse_table(lines, caption, header_start, end_marker, ncols, groups, expected):
    start = next(i for i, l in enumerate(lines) if l.startswith(caption))
    head = next(i for i in range(start, len(lines)) if lines[i].strip().startswith(header_start))
    rows, group = [], None
    for line in lines[head + 1:]:
        text = line.strip()
        if text.startswith(end_marker):
            break
        if not text or re.fullmatch(r"\d+", text):
            continue
        toks = text.split()
        if len(toks) > ncols and all(NUM.match(t) for t in toks[-ncols:]):
            label = " ".join(toks[:-ncols])
            rows.append((group, label, toks[-ncols:]))
        elif text in groups:
            group = text
        else:
            raise AssertionError(f"unexpected line in {caption!r}: {text!r}")
    got = [(g, l) for g, l, _ in rows]
    want = [(g, l) for g, l, _ in expected]
    assert got == want, f"{caption}: row labels differ\n{got}\n{want}"
    return [(g, l, s, v) for (g, l, v), (_, _, s) in zip(rows, expected)]


# ---------------------------------------------------------------- systems
M = lambda s: f"{P}-model-{s}"  # noqa: E731
METH = lambda s: f"{P}-method-{s}"  # noqa: E731
RANDOM_METHOD = "tgtval-20261009-method-random-selection"

MODELS = {
    # slug: (name, reported names, entity_level, description, locator)
    "glm-5-1": ("GLM-5.1", "GLM-5.1", "family",
                "General-purpose large language model, release 5.1 of the GLM-5 series.",
                "Table 1 and Supplementary Table 4 row labels; Methods 4.9; reference [53]"),
    "glm-5-2": ("GLM-5.2", "GLM-5.2", "family",
                "General-purpose large language model, release 5.2 of the GLM-5 series.",
                "Supplementary Table 4 row label; Methods 4.9; reference [53]"),
    "kimi-k2-6": ("Kimi-K2.6", "Kimi-K2.6", "family",
                  "General-purpose large language model, release K2.6 of the Kimi K2 series.",
                  "Supplementary Table 4 row label; Methods 4.9; reference [47]"),
    "claude-opus-4-8": ("Claude Opus 4.8", "Claude Opus-4.8", "service",
                        "Anthropic's hosted large language model Claude Opus 4.8.",
                        "Supplementary Table 4 row label; Methods 4.9; reference [2]"),
    "claude-sonnet-4-6": ("Claude Sonnet 4.6", "Claude Sonnet-4.6", "service",
                          "Anthropic's hosted large language model Claude Sonnet 4.6.",
                          "Supplementary Table 4 row label; Methods 4.9"),
    "claude-haiku-4-5": ("Claude Haiku 4.5", "Claude Haiku-4.5", "service",
                         "Anthropic's hosted large language model Claude Haiku 4.5.",
                         "Supplementary Table 4 row labels; Section 2.3; Methods 4.9"),
    "qwen3-6-27b": ("Qwen3.6-27B", "Qwen3.6-27B", "checkpoint",
                    "Dense 27-billion-parameter large language model in the Qwen3.6 series.",
                    "Table 1 and Supplementary Table 4 row labels; Section 2.7; reference [36]"),
    "gemini-3-1-pro": ("Gemini 3.1 Pro", "Gemini-3.1-Pro", "service",
                       "Google's hosted large language model Gemini 3.1 Pro.",
                       "Table 1 and Supplementary Table 4 row labels; Methods 4.9"),
    "gpt-5-5": ("GPT-5.5", "GPT-5.5", "service",
                "OpenAI's hosted large language model GPT-5.5.",
                "Supplementary Table 4 row labels; Methods 4.9"),
    "gpt-5-6-sol": ("GPT-5.6 Sol", "GPT-5.6 Sol", "service",
                    "OpenAI's hosted large language model GPT-5.6 Sol.",
                    "Table 1 and Supplementary Table 4 row labels; Methods 4.9"),
}

METHODS = {
    # slug: (name, description, method_types, locator)
    "assayformer": ("AssayFormer",
                    "Transformer encoder that reads a screen description and the genes tested so far with their hit labels and scores every candidate gene for the next batch.",
                    ["specialist"], "Section 2.2; Figure 3B-C; Methods 4.4-4.5"),
    "assayloop": ("AssayLoop",
                  "Acquisition policy in which a large language model chooses the first k batches of genes and AssayFormer chooses the remaining batches from the accumulated results.",
                  ["foundation_model", "specialist"], "Section 2.2; Figure 3D; Methods 4.6"),
    "screen-knn": ("Screen-kNN",
                   "Scores candidate genes by a mixture of their prior hit rate and the hit rates in training screens whose labels most resemble the labels observed so far.",
                   ["conventional_pipeline"], "Methods 4.9; Appendix D.5"),
    "prior-hit-frequency": ("Prior hit baseline",
                            "Ranks genes by their empirical hit frequency across the training screens.",
                            ["conventional_pipeline"], "Section 2.3; Methods 4.9"),
    "random-forest-acquisition": ("Random forest acquisition",
                                  "Random forest surrogate whose predictions rank candidate genes for acquisition.",
                                  ["supervised_machine_learning"], "Supplementary Table 4 row labels 'RF (greedy)' and 'RF + UCB'"),
    "bpmf-greedy": ("BPMF with greedy acquisition",
                    "Bayesian probabilistic matrix factorisation of the screen-by-gene hit matrix, with untested genes acquired greedily by predicted hit probability.",
                    ["supervised_machine_learning"], "Section 2.3; Methods 4.9; Appendix D.1"),
    "transformer-dagger": ("Transformer trained with DAgger",
                           "Transformer acquisition policy trained by the DAgger imitation-learning algorithm.",
                           ["supervised_machine_learning"], "Supplementary Table 4 row label 'Transformer + DAgger [39]'; reference [39]"),
    "maml": ("MAML acquisition model",
             "Model meta-learned across training screens with model-agnostic meta-learning and adapted by gradient steps on the hit labels observed in the current screen.",
             ["supervised_machine_learning"], "Section 2.3; Methods 4.9"),
    "biobo": ("BioBO",
              "Bayesian optimisation for perturbation design that uses an upper-confidence-bound acquisition, an MLP surrogate on gene embeddings and a biological enrichment-analysis prior.",
              ["supervised_machine_learning"], "Introduction; Methods 4.9; reference [27]"),
    "probability-of-hit": ("Probability-of-Hit",
                           "Active-search acquisition over an MLP surrogate fitted to the observations collected in the current screen.",
                           ["supervised_machine_learning"], "Introduction; Methods 4.9; reference [40]"),
    "llmnn": ("LLMNN",
              "Agentic harness that combines large-language-model prior knowledge with nearest-neighbour sampling to choose experiments.",
              ["foundation_model"], "Methods 4.9; reference [17]"),
    "icbr-ef": ("ICBR-EF",
                "Agentic harness that keeps a hypothesis registry to improve a large language model's in-context learning from experimental feedback.",
                ["foundation_model"], "Methods 4.9; reference [51]"),
}

LLM_PROMPT = ("prompted with the screen description and, after each round, the genes acquired so far with "
              "their hit labels (AssayBench prompt adapted to the sequential setting)")
NOLAB = ("prompted with the screen description and the genes acquired so far, with hit labels omitted "
         "from the history")

# slug: dict(name, reported, of, uses, types, fm, params, origin, origin_note)
S = {}


def sysrec(slug, **kw):
    S[slug] = kw


for slug, mslug, reported in [
    ("glm-5-1", "glm-5-1", "GLM-5.1"), ("glm-5-2", "glm-5-2", "GLM-5.2"), ("kimi-k2-6", "kimi-k2-6", "Kimi-K2.6"),
    ("claude-opus-4-8", "claude-opus-4-8", "Claude Opus-4.8"), ("claude-sonnet-4-6", "claude-sonnet-4-6", "Claude Sonnet-4.6"),
    ("claude-haiku-4-5", "claude-haiku-4-5", "Claude Haiku-4.5"), ("qwen3-6-27b", "qwen3-6-27b", "Qwen3.6-27B"),
    ("gemini-3-1-pro", "gemini-3-1-pro", "Gemini-3.1-Pro"), ("gpt-5-5", "gpt-5-5", "GPT-5.5"),
    ("gpt-5-6-sol", "gpt-5-6-sol", "GPT-5.6 Sol"),
]:
    sysrec(slug, name=f"{MODELS[mslug][0]} acquisition policy (AssayBench-Loop)", reported=reported,
           of=M(mslug), uses=[], types=["foundation_model"], fm=True,
           params=f"Standalone policy for all 10 rounds, {LLM_PROMPT}",
           origin="independent_paper", origin_note="Run by the AssayLoop authors on a third-party model with their own prompt.")
for slug, mslug, reported in [
    ("glm-5-1-no-labels", "glm-5-1", "w/o labels (GLM-5.1)"), ("kimi-k2-6-no-labels", "kimi-k2-6", "- hit labels (Kimi-K2.6)"),
    ("claude-opus-4-8-no-labels", "claude-opus-4-8", "- hit labels (Claude Opus-4.8)"),
    ("qwen3-6-27b-no-labels", "qwen3-6-27b", "- hit labels (Qwen3.6-27B)"),
    ("gemini-3-1-pro-no-labels", "gemini-3-1-pro", "w/o labels (Gemini-3.1-Pro)"),
]:
    sysrec(slug, name=f"{MODELS[mslug][0]} acquisition policy without hit labels (AssayBench-Loop)", reported=reported,
           of=M(mslug), uses=[], types=["foundation_model"], fm=True,
           params=f"Standalone policy for all 10 rounds, {NOLAB}",
           origin="independent_paper", origin_note="Run by the AssayLoop authors on a third-party model with their own prompt; label-ablation arm.")
S["qwen3-6-27b"]["reported"] = "Qwen3.6-27B; Qwen3.6-27B (base)"
sysrec("qwen3-6-27b-sft", name="Qwen3.6-27B after SFT on GLM-5.1 traces (AssayLLM stage 1)", reported="+ SFT (GLM-5.1 traces)",
       of=M("qwen3-6-27b"), uses=[], types=["foundation_model"], fm=True,
       params="Qwen3.6-27B supervised fine-tuned on GLM-5.1 acquisition trajectories from the training screens; standalone policy for all 10 rounds",
       origin="author_reported", origin_note="AssayLLM is the authors' own fine-tuned model.")
sysrec("assayllm", name="AssayLLM (Qwen3.6-27B after SFT and GRPO)", reported="+ SFT + GRPO (= AssayLLM)",
       of=M("qwen3-6-27b"), uses=[], types=["foundation_model"], fm=True,
       params="Qwen3.6-27B supervised fine-tuned on GLM-5.1 trajectories, then GRPO reinforcement learning; standalone policy for all 10 rounds",
       origin="author_reported", origin_note="AssayLLM is the authors' own fine-tuned model.")
sysrec("random", name="Random policy (AssayBench-Loop)", reported="Random", of=RANDOM_METHOD, uses=[],
       types=["conventional_pipeline"], fm=False,
       params="One draw of the random policy over the candidate pool, not its expected value",
       origin="author_reported", origin_note="Random comparator run by the AssayLoop authors.")
sysrec("prior-hit", name="Prior hit baseline (AssayBench-Loop)", reported="Prior hit baseline", of=METH("prior-hit-frequency"),
       uses=[], types=["conventional_pipeline"], fm=False, params="Genes ranked by empirical hit frequency across the 1,349 training screens",
       origin="author_reported", origin_note="Baseline built by the AssayLoop authors.")
sysrec("screen-knn", name="Screen-kNN (AssayBench-Loop)", reported="Screen-kNN", of=METH("screen-knn"), uses=[],
       types=["conventional_pipeline"], fm=False, params="Exponential kernel temperature 0.1, prior-mixing constant kappa 100; top-b untested genes per round",
       origin="author_reported", origin_note="Baseline built by the AssayLoop authors (Appendix D.5).")
sysrec("rf-greedy", name="Random forest, greedy acquisition (AssayBench-Loop)", reported="RF (greedy)", of=METH("random-forest-acquisition"),
       uses=[], types=["supervised_machine_learning"], fm=False, params="Greedy acquisition",
       origin="independent_paper", origin_note="Generic baseline run by the AssayLoop authors; not described in the Methods.")
sysrec("rf-ucb", name="Random forest, UCB acquisition (AssayBench-Loop)", reported="RF + UCB", of=METH("random-forest-acquisition"),
       uses=[], types=["supervised_machine_learning"], fm=False, params="Upper-confidence-bound acquisition",
       origin="independent_paper", origin_note="Generic baseline run by the AssayLoop authors; not described in the Methods.")
sysrec("bpmf-greedy", name="BPMF with greedy acquisition (AssayBench-Loop)", reported="BPMF [41]", of=METH("bpmf-greedy"), uses=[],
       types=["supervised_machine_learning"], fm=False, params="BPMF fitted to the training hit matrix; greedy acquisition",
       origin="independent_paper", origin_note="Third-party algorithm (Salakhutdinov and Mnih) run by the AssayLoop authors.")
sysrec("transformer-dagger", name="Transformer trained with DAgger (AssayBench-Loop)", reported="Transformer + DAgger [39]",
       of=METH("transformer-dagger"), uses=[], types=["supervised_machine_learning"], fm=False,
       params="Transformer policy trained with DAgger; architecture and training not described in the Methods",
       origin="independent_paper", origin_note="Third-party training algorithm (Ross et al.) run by the AssayLoop authors.")
sysrec("maml-bpmf", name="MAML with BPMF embeddings (AssayBench-Loop)", reported="MAML (w/ BPMF embs.) [12, 41]", of=METH("maml"),
       uses=[], types=["supervised_machine_learning"], fm=False, params="Meta-learned initialisation across training screens, BPMF gene embeddings",
       origin="independent_paper", origin_note="Third-party algorithm (Finn et al.) run by the AssayLoop authors.")
sysrec("biobo", name="BioBO (AssayBench-Loop)", reported="BioBO [27]", of=METH("biobo"), uses=[],
       types=["supervised_machine_learning"], fm=False, params="Per-screen surrogate; does not use the training screens",
       origin="independent_paper", origin_note="Third-party method (Li et al.) run by the AssayLoop authors.")
sysrec("probability-of-hit", name="Probability-of-Hit (AssayBench-Loop)", reported="Probability-of-hit [40]", of=METH("probability-of-hit"),
       uses=[], types=["supervised_machine_learning"], fm=False, params="Per-screen surrogate; does not use the training screens",
       origin="independent_paper", origin_note="Third-party method (Rubbi et al.) run by the AssayLoop authors.")
sysrec("haiku-4-5-coding-agent", name="Claude Haiku 4.5 coding agent with training screens (AssayBench-Loop)", reported="Haiku-4.5 Agent",
       of=M("claude-haiku-4-5"), uses=[], types=["foundation_model"], fm=True,
       params="General coding agent on Claude Haiku 4.5 with direct access to the training screens; harness not named",
       origin="independent_paper", origin_note="Third-party model in a general coding-agent setup run by the AssayLoop authors.")
sysrec("llmnn", name="LLMNN (AssayBench-Loop)", reported="LLMNN [17]", of=METH("llmnn"), uses=[], types=["foundation_model"], fm=True,
       params="Does not use the training screens; backbone language model not stated",
       origin="independent_paper", origin_note="Third-party harness (Gupta et al.) run by the AssayLoop authors.")
sysrec("icbr-ef", name="ICBR-EF (AssayBench-Loop)", reported="ICBR-EF [51]", of=METH("icbr-ef"), uses=[], types=["foundation_model"], fm=True,
       params="Does not use the training screens; backbone language model not stated",
       origin="independent_paper", origin_note="Third-party harness (Wainrib et al.) run by the AssayLoop authors.")

AF = METH("assayformer")
for slug, name, reported, params in [
    ("assayformer-random-emb-sft", "AssayFormer, random embeddings, supervised only", "AssayFormer (random embs.); AssayFormer (Random)",
     "Randomly initialised gene embeddings; supervised (BCE) training only, no GRPO"),
    ("assayformer-bpmf-sft", "AssayFormer, BPMF embeddings, supervised only", "+ BPMF Embeddings; AssayFormer (BPMF)",
     "BPMF-initialised gene embeddings; supervised (BCE) training only, no GRPO"),
    ("assayformer", "AssayFormer (BPMF embeddings, supervised then GRPO)", "+ GRPO (= AssayFormer); BPMF + GRPO",
     "BPMF-initialised gene embeddings; supervised training then GRPO with the context-delta reward; standalone for all 10 rounds"),
    ("assayformer-bpmf-sft-no-desc", "AssayFormer, BPMF embeddings, supervised only, no screen description", "- screen desc. (under AssayFormer (BPMF))",
     "BPMF embeddings; supervised training only; screen description removed"),
    ("assayformer-svd-sft", "AssayFormer, SVD embeddings, supervised only", "AssayFormer (SVD)", "SVD of the training hit matrix; supervised training only"),
    ("assayformer-mf-sft", "AssayFormer, MF embeddings, supervised only", "AssayFormer (MF)", "Matrix factorisation embeddings; supervised training only"),
    ("assayformer-mf-sphere-sft", "AssayFormer, MF-Sphere embeddings, supervised only", "AssayFormer (MF-Sphere)",
     "Normalised matrix factorisation embeddings; supervised training only"),
    ("assayformer-genept-pca-sft", "AssayFormer, GenePT-PCA embeddings, supervised only", "AssayFormer (GenePT-PCA)",
     "GenePT embeddings reduced by PCA; supervised training only"),
    ("assayformer-k562-pca-sft", "AssayFormer, K562-PCA embeddings, supervised only", "AssayFormer (K562-PCA)",
     "K562 Perturb-seq embeddings reduced by PCA; supervised training only"),
    ("assayformer-random-emb-grpo", "AssayFormer, random embeddings, supervised then GRPO", "Random + GRPO",
     "Randomly initialised gene embeddings; supervised training then GRPO"),
    ("assayformer-no-desc-grpo", "AssayFormer, BPMF embeddings, GRPO, no screen description", "BPMF (no desc.) + GRPO",
     "BPMF embeddings; supervised training then GRPO; screen description removed"),
    ("assayformer-ef-terminal-grpo", "AssayFormer, BPMF embeddings, GRPO with terminal-EF reward", "BPMF + GRPO (EFterminal)",
     "BPMF embeddings; GRPO with terminal EF after 10 rounds as the reward instead of the context-delta reward"),
    ("assayformer-svd-grpo", "AssayFormer, SVD embeddings, supervised then GRPO", "SVD + GRPO", "SVD embeddings; supervised training then GRPO"),
    ("assayformer-mf-grpo", "AssayFormer, MF embeddings, supervised then GRPO", "MF + GRPO", "Matrix factorisation embeddings; supervised training then GRPO"),
    ("assayformer-mf-sphere-grpo", "AssayFormer, MF-Sphere embeddings, supervised then GRPO", "MF-Sphere + GRPO",
     "Normalised matrix factorisation embeddings; supervised training then GRPO"),
    ("assayformer-genept-pca-grpo", "AssayFormer, GenePT-PCA embeddings, supervised then GRPO", "GenePT-PCA + GRPO",
     "GenePT embeddings reduced by PCA; supervised training then GRPO"),
    ("assayformer-k562-pca-grpo", "AssayFormer, K562-PCA embeddings, supervised then GRPO", "K562-PCA + GRPO",
     "K562 Perturb-seq embeddings reduced by PCA; supervised training then GRPO"),
]:
    sysrec(slug, name=f"{name} (AssayBench-Loop)", reported=reported, of=AF, uses=[], types=["specialist"], fm=False,
           params=params, origin="author_reported", origin_note="The authors' own method.")

AL = METH("assayloop")
for slug, llm, reported, params in [
    ("assayloop-glm-5-1", "glm-5-1", "GLM-5.1 → AssayFormer", "GLM-5.1 chooses rounds 1-3, AssayFormer rounds 4-10 (k = 3)"),
    ("assayloop-gemini-3-1-pro", "gemini-3-1-pro", "Gemini-3.1-Pro → AssayFormer", "Gemini 3.1 Pro chooses rounds 1-3, AssayFormer rounds 4-10 (k = 3)"),
    ("assayloop-gpt-5-5", "gpt-5-5", "GPT-5.5 → AssayFormer", "GPT-5.5 chooses rounds 1-3, AssayFormer rounds 4-10 (k = 3)"),
    ("assayloop-gpt-5-6-sol", "gpt-5-6-sol", "GPT-5.6 Sol → AssayFormer", "GPT-5.6 Sol chooses rounds 1-3, AssayFormer rounds 4-10 (k = 3)"),
    ("assayloop-assayllm", "qwen3-6-27b", "AssayLLM → AssayFormer", "AssayLLM (fine-tuned Qwen3.6-27B) chooses rounds 1-3, AssayFormer rounds 4-10 (k = 3)"),
    ("assayloop-assayllm-handoff", "qwen3-6-27b", "Handoff-trained AssayLLM → AssayFormer",
     "AssayLLM post-trained for the warm-start role chooses rounds 1-3, AssayFormer rounds 4-10 (k = 3)"),
]:
    sysrec(slug, name=f"AssayLoop: {reported.replace(' →', ' to').replace('→', ' to ')} (AssayBench-Loop)", reported=reported, of=AL,
           uses=[M(llm), AF], types=["foundation_model", "specialist"], fm=True, params=params,
           origin="author_reported", origin_note="The authors' own method.")

# ---------------------------------------------------------------- metrics
Q_MEAN = "mean over the 20 AssayBench-Loop test screens"
METRICS = {
    "ef": dict(metric="hit-enrichment-factor", direction="higher", unit="unitless",
               qualifier=f"hits found divided by hits expected under random selection, after 10 rounds of 100 genes; hallucinated genes and unfilled slots count in the denominator, valid genes outside the screen library do not; {Q_MEAN}"),
    "nauc": dict(metric="normalized-cumulative-hits-auc", direction="higher", unit="unitless", unit_detail="printed x100 (column 'nAUC (%)')",
                 qualifier=f"area under the fraction-of-hits against fraction-of-library-queried curve over 10 rounds, divided by an oracle's area over the same effective budget; {Q_MEAN}"),
    "fh": dict(metric="recall", direction="higher", unit="percent", unit_detail="hits in the screen library",
               qualifier=f"fraction of the screen's hits acquired within 10 rounds of 100 genes (FH); {Q_MEAN}"),
    "sf": dict(metric="proportion", direction="lower", unit="percent", unit_detail="acquired genes",
               qualifier=f"shortfall: share of acquired genes outside the screen library, including hallucinated gene names; {Q_MEAN}"),
    "ess": dict(metric="proportion", direction="unknown", unit="percent", unit_detail="acquired hits",
                qualifier=f"share of acquired hits that are DepMap common-essential genes (1,827 genes); {Q_MEAN}"),
    "vendi": dict(metric="vendi-ratio", direction="unknown", unit="unitless", unit_detail="printed x100 (column 'Vendi (%)')",
                  qualifier=f"Vendi score of each batch under a cosine kernel on GenePT embeddings, divided by batch size and averaged over batches; {Q_MEAN}"),
    "po": dict(metric="annotation-overlap-ratio", direction="unknown", unit="unitless",
               qualifier=f"mean pairwise Jaccard overlap of GO biological-process annotations within a batch, divided by that of an equal-size random batch from the screen library, averaged over batches; {Q_MEAN}"),
    "epb": dict(metric="effective-number-of-groups", direction="unknown", unit="unitless", unit_detail="effective number of Reactome level-2 pathway groups (186 in the vocabulary)",
                qualifier="EP-B: Hill number of order 1 at batch scope, rarefied to 30 annotated genes per batch, one random group per gene per draw, 400 Monte Carlo draws, averaged within each screen then across the 20 test screens; not comparable with EP-S or EP-D"),
    "eps": dict(metric="effective-number-of-groups", direction="unknown", unit="unitless", unit_detail="effective number of Reactome level-2 pathway groups (186 in the vocabulary)",
                qualifier="EP-S: Hill number of order 1 at screen scope, rarefied to 200 annotated genes per screen, one random group per gene per draw, 400 Monte Carlo draws, averaged across the 20 test screens; not comparable with EP-B or EP-D"),
    "epd": dict(metric="effective-number-of-groups", direction="unknown", unit="unitless", unit_detail="effective number of Reactome level-2 pathway groups (186 in the vocabulary)",
                qualifier="EP-D: Hill number of order 1 at dataset scope, rarefied to 6,000 annotated genes across the complete test set, one random group per gene per draw, 300 Monte Carlo draws; not comparable with EP-B or EP-S"),
}
ORDER = ["ef", "nauc", "fh", "sf", "ess", "vendi", "po", "epb", "eps", "epd"]


def review(note):
    return {
        "method": ["source-hash-verification", "pdf-text-parse", "deterministic-table-parse"],
        "reviewer": ["claude"],
        "reviewer_note": EXTRACTOR + "; extraction only, not yet independently reviewed",
        "date": TODAY,
        "artifact_sha256": SHA,
        "retrieval_url": PDF_URL,
        "note": note,
    }


def main(text_path, out_path):
    lines = open(text_path, encoding="utf-8").read().splitlines()
    t1 = parse_table(lines, "Table 1: Performance comparison", "Method", "warm starts reaching", 8, T1_GROUPS, T1_ROWS)
    s4 = parse_table(lines, "Supplementary Table 4: Full performance", "Method", "D     Implementation details", 10, S4_GROUPS, S4_ROWS)
    assert len(t1) == 26 and len(s4) == 57

    # values per system from S4 (first printing), with duplicate printings asserted equal
    s4_vals, s4_label, s4_dups = {}, {}, {}
    for g, label, slug, vals in s4:
        d = dict(zip(S4_KEYS, vals))
        if slug in s4_vals:
            assert s4_vals[slug] == d, f"S4 duplicate rows disagree for {slug}"
            s4_dups.setdefault(slug, []).append((g, label))
        else:
            s4_vals[slug], s4_label[slug] = d, (g, label)
    t1_vals, t1_label = {}, {}
    for g, label, slug, vals in t1:
        d = dict(zip(T1_KEYS, vals))
        t1_vals[slug], t1_label[slug] = d, (g, label)
        for k in T1_KEYS:
            assert d[k] == s4_vals[slug][k], f"Table 1 and S4 disagree: {slug} {k} {d[k]} {s4_vals[slug][k]}"
    assert set(S) == set(s4_vals), set(S) ^ set(s4_vals)

    recs = []

    def add(r):
        recs.append(r)

    # source
    add({"id": SRC, "kind": "source", "name": "Biology-in-the-loop: Amortized Adaptive Hit Discovery in CRISPR Screens",
         "description": "Preprint introducing the AssayBench-Loop benchmark of 1,389 historical CRISPR screens and the AssayLoop, AssayFormer and AssayLLM acquisition policies.",
         "status": "needs_review", "facets": FACETS, "source_ids": [], "links": [],
         "attributes": {"url": "https://arxiv.org/abs/2609.11877v1", "artifact_url": PDF_URL,
                        "version": "arXiv:2609.11877 version 1, submitted 2026-09-10; not peer reviewed",
                        "retrieved_at": "2026-10-22T13:57:26Z", "artifact_sha256": SHA, "doi": "10.48550/arXiv.2609.11877",
                        "publication_status": "preprint", "licence": "CC-BY-4.0", "media_type": "application/pdf",
                        "source_locator": "Full artifact bytes; per-record locators on each record",
                        "access_and_reuse": "CC-BY-4.0 permits redistribution of the article bytes.",
                        "archive_note": "Not archived in the batch; the artifact_sha256 pins the bytes read. The digest matches the copy hashed for the 2026-10-07 dossier and the 2026-10-22 search pass.",
                        "extraction_method": "pdftotext -layout text layer, parsed by data/omics/use-case-refresh-phenotype-20261022/extract/edwards2026assayloop.py",
                        "scope_note": "Authors are at Genentech. Two of them (De Brouwer, Scalia) are also authors of AssayBench (tgtval-20261009-source-debrouwer2026), on which AssayBench-Loop is built."}})

    # dataset subset
    add({"id": DATA, "kind": "dataset_subset", "name": "AssayBench-Loop test split (20 genome-wide CRISPR screens published after 2021)",
         "description": "The 20 temporally held-out test screens of AssayBench-Loop, each a genome-wide CRISPR screen with binary hit labels.",
         "status": "needs_review", "facets": FACETS, "source_ids": [SRC],
         "links": [{"relation": "used_in", "target_id": PROTOCOL},
                   {"relation": "same_data_as", "target_id": "tgtval-20261009-data-assaybench-test"}],
         "attributes": {"version": "AssayBench-Loop as described in arXiv:2609.11877v1",
                        "split": "Temporal: 1,349 training screens before 2021, 20 validation screens from 2021, 20 test screens after 2021",
                        "test_count": 20,
                        "subset_scope": "Test screens were restricted to genome-wide coverage (18,000-22,000 genes), at least 50 hits with hit rate below 15%, and a best-LLM AnDCG@100 of at least 0.05 (Gemini 3.1 Pro on AssayBench); phenotype categories were allocated from the eligible pool with a soft cap of six per category, and within-category diversity of screen descriptions was maximised.",
                        "source_dataset": "AssayBench (1,920 CRISPR screens); the test pool is AssayBench's post-2021 split",
                        "limitations": ["Screens were selected, not sampled: the criteria include a performance floor for the best LLM on AssayBench, which conditions the test set on LLM-recoverable hits.",
                                        "Hit labels are each screen's own published significance call; the candidate pool G (about 20,000 genes) is larger than each screen library, so genes outside the library cannot be scored.",
                                        "The same_data_as link to the AssayBench test cohort is informational: AssayBench-Loop draws its test screens from that post-2021 pool, but the 20 screen identities are listed only in Supplementary Table 2, which was not extracted."],
                        "source_locator": "Section 2.1; Figure 2B-C caption; Methods 4.2; Supplementary Table 2 (not extracted)"}})

    # protocol
    add({"id": PROTOCOL, "kind": "protocol",
         "name": "AssayBench-Loop adaptive hit discovery: 10 rounds of 100 genes on 20 held-out CRISPR screens",
         "description": "Retrospective replay in which a policy picks 100 genes per round for 10 rounds from a shared pool of about 20,000 genes, sees each screen's historical hit labels for its picks, and is scored on hits found against random selection.",
         "status": "needs_review", "facets": FACETS, "source_ids": [SRC],
         "links": [{"relation": "uses_data", "target_id": DATA}],
         "attributes": {
             "protocol": "For each test screen the policy receives a natural-language description of the screen. At each of T = 10 rounds it nominates b = 100 genes from the candidate pool G, observes their binary hit labels from the historical screen, and conditions the next batch on the accumulated history. Budget 1,000 acquisitions per screen (about 5% of the library). Methods may use the 1,349 training screens. Metrics are computed per screen and averaged equally over the 20 test screens.",
             "version": "arXiv:2609.11877v1, Section 2.1, Methods 4.1-4.3, Appendix H; Table 1 and Supplementary Table 4",
             "metric": "hit-enrichment-factor", "metric_direction": "higher", "unit": "unitless",
             "metric_definition": "EF = |G_T ∩ H| / ((N_L + N_Ḡ + N_miss) · h_rand), where G_T is the set of acquired genes, H the screen's hits, N_L the acquired genes in the screen library, N_Ḡ the hallucinated (invalid) gene names, N_miss the unfilled slots and h_rand = |H|/|L| the screen's hit rate. Valid genes outside the screen library are not counted in the denominator. Secondary: nAUC, fraction of hits found, shortfall, %ess, Vendi ratio, pathway overlap, EP-B/EP-S/EP-D (Appendix H).",
             "aggregation": "Each metric computed per screen, then averaged with equal weight over the 20 test screens (EP-D is computed over the pooled test set).",
             "allowed_information": "Screen description (cell line, perturbation modality, treatment, readout, hit definition); the genes acquired in earlier rounds and their hit labels; the 1,349 training screens. Policies may ignore any of these (the label-ablation arms omit the hit labels).",
             "heldout_test": "20 genome-wide screens published after 2021 (temporal split)",
             "heldout_validation": "20 screens from 2021; used to select the handoff round k = 3",
             "selection": "Test screens filtered for genome-wide coverage, at least 50 hits, hit rate below 15%, and a best-LLM AnDCG@100 of at least 0.05, then chosen for phenotype spread and description diversity.",
             "uncertainty_reporting": "Table 1 and Supplementary Table 4 print means without spread. Supplementary Figure 6D shows ±1 SEM across 20 screens for five methods as a figure only.",
             "limitations": [
                 "Retrospective: labels are historical screen calls, and the authors state the policies remain to be validated prospectively in a live experimental loop.",
                 "The held-out unit is the screen; there are 20 test screens and no per-screen values in the extracted tables.",
                 "Test screens were selected with a performance floor for the best LLM on AssayBench, which favours screens whose hits an LLM can name.",
                 "Recovered hits are often DepMap common-essential genes (the %ess column), so a high EF can partly reflect generic fitness genes.",
                 "Random is one draw of the random policy, not its expectation (Table 1 caption).",
                 "The AssayLoop, AssayFormer and AssayLLM rows are the authors' own methods; all other rows were also run by the same authors."],
             "source_locator": "Section 2.1; Figure 2A and D captions; Methods 4.1-4.3; Appendix H; Table 1 caption"}})

    # models
    for slug, (name, reported, level, desc, loc) in MODELS.items():
        mm = {"checkpoint_revision": {"reason": "unreported"}, "training_data": {"reason": "unreported"},
              "version": {"reason": "unreported", "note": "Only the release name is printed; no snapshot date, API version or weights revision."}}
        add({"id": M(slug), "kind": "model", "name": name, "description": desc, "status": "needs_review",
             "facets": FACETS, "source_ids": [SRC], "links": [],
             "attributes": {"entity_level": level, "reported_name": reported, "source_locator": loc, "missing_metadata": mm,
                            "provenance_note": "Identity as printed in arXiv:2609.11877v1; the access route (hosted API or local weights) is not stated. Not assumed equal to any other release in the store."}})

    # methods
    for slug, (name, desc, types, loc) in METHODS.items():
        attrs = {"reported_name": name, "entity_level": "method", "source_locator": loc,
                 "missing_metadata": {"version": {"reason": "inapplicable", "note": "Family record; settings are on configurations"}}}
        if slug in ("random-forest-acquisition", "transformer-dagger"):
            attrs["provenance_note"] = "Appears only as a row label in Supplementary Table 4; the Methods do not describe it, so the description is limited to what the label states."
        add({"id": METH(slug), "kind": "method", "name": name, "description": desc, "status": "needs_review",
             "facets": {**FACETS, "method_types": types}, "source_ids": [SRC], "links": [], "attributes": attrs})

    # configurations, evaluations, results
    n_results = 0
    for slug in sorted(S):
        s = S[slug]
        cid, eid = f"{P}-config-edwards2026-{slug}", f"{P}-eval-edwards2026-{slug}"
        links = [{"relation": "configuration_of", "target_id": s["of"]}] + [{"relation": "uses_model", "target_id": u} for u in s["uses"]]
        add({"id": cid, "kind": "configuration", "name": s["name"],
             "description": f"Configuration of {s['name'].split(' (AssayBench-Loop)')[0]}: {s['params']}.",
             "status": "needs_review", "facets": {**FACETS, "method_types": s["types"]}, "source_ids": [SRC], "links": links,
             "attributes": {"reported_name": s["reported"], "foundation_model_eligible": s["fm"], "parameters": s["params"],
                            "source_locator": "Table 1 and Supplementary Table 4 row labels; Methods 4.6-4.9",
                            "missing_metadata": {"version": {"reason": "unreported", "note": "No release, commit or checkpoint is printed for this configuration"},
                                                 "access_reuse": {"reason": "unextracted", "note": "Page 1 shows Website, GitHub, PyPI and Models & Data link labels; their URLs were not resolved from the text layer"}},
                            "provenance_note": "Configuration as run in the AssayLoop comparison (arXiv:2609.11877v1)."}})
        in_t1 = slug in t1_vals
        g1, l1 = t1_label.get(slug, (None, None))
        g4, l4 = s4_label[slug]
        if in_t1:
            ev_loc = f"Table 1, row '{l1}' ({g1}); Supplementary Table 4, row '{l4}' ({g4})"
        else:
            ev_loc = f"Supplementary Table 4, row '{l4}' ({g4})"
        lim = [s["origin_note"]]
        if slug == "random":
            lim.append("One instantiation of the random policy, not an expected value (Table 1 caption).")
        add({"id": eid, "kind": "evaluation", "name": f"{s['name'].split(' (AssayBench-Loop)')[0]} on AssayBench-Loop test (Edwards et al. 2026)",
             "description": "Published comparison; transcribed, not reproduced.", "status": "needs_review", "facets": FACETS, "source_ids": [SRC],
             "links": [{"relation": "system", "target_id": cid}, {"relation": "assessment", "target_id": PROTOCOL}, {"relation": "data", "target_id": DATA}],
             "attributes": {"origin": s["origin"], "protocol": PROTOCOL, "version": "arXiv:2609.11877v1 as retrieved 2026-10-22",
                            "comparison": {"protocol_id": PROTOCOL, "dataset_version": "AssayBench-Loop test split, 20 screens (arXiv:2609.11877v1)",
                                           "split": "Temporal: train before 2021 (1,349 screens), validation 2021 (20), test after 2021 (20)",
                                           "population": "20 genome-wide CRISPR test screens; candidate pool of about 20,000 genes",
                                           "inputs": "Screen description, genes acquired in earlier rounds with their hit labels, and the training screens",
                                           "adaptation": "Method-specific; training on the 1,349 training screens permitted",
                                           "metric_implementation": "Methods 4.3 and Appendix H of arXiv:2609.11877v1",
                                           "aggregation": "Per-screen metric averaged equally over the 20 test screens",
                                           "budget": "10 rounds x 100 genes (1,000 acquisitions per screen)"},
                            "source_locator": ev_loc, "limitations": lim,
                            "missing_metadata": {"n_runs": {"reason": "unreported", "note": "The tables do not say how many runs or seeds each row averages; only Random is described as a single instantiation."}}}})
        if slug == "random":
            add({"id": BASELINE, "kind": "baseline", "name": "Random policy on AssayBench-Loop (one draw)",
                 "description": "Source-supported random comparator; measured values belong to the linked evaluation.",
                 "status": "needs_review", "facets": FACETS, "source_ids": [SRC],
                 "links": [{"relation": "implemented_by", "target_id": cid}, {"relation": "measured_in", "target_id": eid},
                           {"relation": "applicable_to", "target_id": PROTOCOL}],
                 "attributes": {"baseline_type": "null_control", "applicability": "source_supported",
                                "requirements": "Same 20 test screens, candidate pool and 10 x 100 budget as the other rows.",
                                "scope_note": "A single draw of the random policy, not its expectation. EF is itself defined against the random expectation, so its expected value under random selection is about 1; the printed 1.04 is one draw.",
                                "source_locator": "Table 1 caption and row 'Random'; Supplementary Table 4 row 'Random'"}})
        for key in ORDER:
            m = METRICS[key]
            use_t1 = in_t1 and key in T1_KEYS
            if use_t1:
                val = t1_vals[slug][key]
                col = T1_COLS[T1_KEYS.index(key)]
                rowlab, grp = l1, g1
                table = "Table 1"
            else:
                val = s4_vals[slug][key]
                col = S4_COLS[S4_KEYS.index(key)]
                rowlab, grp = l4, g4
                table = "Supplementary Table 4"
            dup_label = sum(1 for _, l, _ in (T1_ROWS if use_t1 else S4_ROWS) if l == rowlab) > 1
            where = f" (group '{grp}'"
            if dup_label:
                parent = {"glm-5-1-no-labels": "GLM-5.1", "gemini-3-1-pro-no-labels": "Gemini-3.1-Pro" if use_t1 else "Gemini-3.1-pro",
                          "kimi-k2-6-no-labels": "Kimi-K2.6", "claude-opus-4-8-no-labels": "Claude Opus-4.8",
                          "qwen3-6-27b-no-labels": "Qwen3.6-27B"}[slug]
                where += f", the row directly under '{parent}'"
            where += ")"
            loc = f'{table}, row "{rowlab}"{where}, column "{col}"'
            also = []
            if use_t1:
                also.append(f"printed identically in Supplementary Table 4, row '{l4}' ({g4})")
            for gd, ld in s4_dups.get(slug, []):
                if key in S4_KEYS:
                    also.append(f"printed identically in Supplementary Table 4, row '{ld}' ({gd})")
            note = ("Extracted by deterministic parse of the pdftotext -layout text layer of the pinned PDF "
                    "(extract/edwards2026assayloop.py), asserting the row labels and group headings of Table 1 (26 rows) and "
                    "Supplementary Table 4 (57 rows) in order and that every repeated printing of the same run is identical.")
            if also:
                note += " Same value " + "; ".join(also) + "; stored once."
            attrs = {"metric": m["metric"], "metric_qualifier": m["qualifier"], "metric_direction": m["direction"], "unit": m["unit"],
                     "printed_value": val, "numeric_value": val, "source_locator": loc,
                     "coverage": {"scored": 20, "unit": "test screens"},
                     "review": review(note),
                     "missing_metadata": {"uncertainty": {"reason": "unreported", "note": "Table 1 and Supplementary Table 4 print means without spread."}}}
            if "unit_detail" in m:
                attrs["unit_detail"] = m["unit_detail"]
            add({"id": f"{P}-result-edwards2026-{slug}-{key}", "kind": "result",
                 "name": f"{s['name'].split(' (AssayBench-Loop)')[0]} {key.upper()} on AssayBench-Loop test",
                 "description": "Reported measurement transcribed from the pinned source. Not independently reproduced.",
                 "status": "needs_review", "facets": {}, "source_ids": [SRC],
                 "links": [{"relation": "evaluation", "target_id": eid}], "attributes": attrs})
            n_results += 1

    # claims
    def claim(cid, subject, field, value, loc):
        add({"id": f"{P}-claim-edwards2026-{cid}", "kind": "claim", "name": f"{field} ({cid})",
             "description": "Descriptive fact transcribed from the pinned source.", "status": "needs_review", "facets": FACETS,
             "source_ids": [SRC], "links": [{"relation": "subject", "target_id": subject}],
             "attributes": {"field": field, "value": value, "source_locator": loc,
                            "review": {"method": ["transcription"], "reviewer": ["claude"],
                                       "reviewer_note": EXTRACTOR + "; not yet independently reviewed", "date": TODAY,
                                       "artifact_sha256": SHA, "retrieval_url": PDF_URL,
                                       "note": "Transcribed from the pdftotext -layout text layer."}}})

    claim("assaybench-loop-composition", DATA, "composition",
          "AssayBench-Loop comprises 1,389 CRISPR screens across five phenotype categories, split temporally into 1,349 training (before 2021), 20 validation (2021) and 20 test (after 2021) screens; median test-to-training hit-set Jaccard similarity 0.064.",
          "Section 2.1; Figure 2B caption")
    claim("assayformer-training", METH("assayformer"), "training",
          "Gene embeddings are initialised by BPMF on the training hit matrix; the policy is trained with binary cross-entropy on simulated partial histories, then fine-tuned with GRPO on full 10-round rollouts using a context-delta reward relative to a context-free reference policy.",
          "Section 2.2; Figure 3C caption; Methods 4.5")
    claim("assayloop-handoff", METH("assayloop"), "handoff",
          "A large language model acts as the acquisition policy for the first k rounds and AssayFormer for the remaining T - k rounds; k = 3 was selected on the validation set.",
          "Section 2.2; Methods 4.6")
    claim("assayllm-training", M("qwen3-6-27b"), "post_training",
          "AssayLLM is Qwen3.6-27B supervised fine-tuned on GLM-5.1 acquisition trajectories from the training screens and then trained with GRPO; the authors report EF rising from 2.65 (base) to 3.56 (SFT) and 3.69 (SFT + GRPO).",
          "Section 2.7; Figure 6 caption; Methods 4.7")
    claim("prospective-validation", PROTOCOL, "prospective_validation",
          "The authors state that AssayBench-Loop is a retrospective benchmark and that the policies remain to be validated prospectively in a live experimental loop.",
          "Section 3 (Discussion), limitations paragraph")

    recs.sort(key=lambda r: r["id"])
    ids = [r["id"] for r in recs]
    assert len(ids) == len(set(ids)), "duplicate ids"
    with open(out_path, "w", encoding="utf-8") as f:
        for r in recs:
            f.write(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n")
    kinds = {}
    for r in recs:
        kinds[r["kind"]] = kinds.get(r["kind"], 0) + 1
    print(json.dumps({"records": len(recs), "kinds": kinds, "results": n_results,
                      "systems": len(S), "table1_rows": len(t1), "s4_rows": len(s4)}))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
