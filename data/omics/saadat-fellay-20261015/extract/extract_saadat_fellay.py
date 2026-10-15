"""Extract Saadat and Fellay, "Optimizing genomic language models for efficient training, fine-tuning, and
inference" (ICLR 2026 workshop paper, OpenReview NUleWh1GFx), for rewire-benchmark-data#162.

Usage:
  python3 -I extract/extract_saadat_fellay.py <paper.pdf> <batch-folder>

The PDF hash is asserted before anything is read. Prose values (sections 3.3 and 3.5) are asserted as exact
substrings of the whitespace-normalised `pdftotext` text. The four Pearson r values of Figure 1 are printed
inside the raster figure (embedded image object 6 on page 4), so they have no text layer; they are transcribed
from the image at its native resolution and listed in FIGURE1_LEGEND below. Every other figure plots values
without printing them, so nothing else is read from figures.

All records are written with status needs_review; the review-evidence pass signs them off. Existing model
records are reused, never changed.
"""
import csv, hashlib, json, os, re, subprocess, sys

TODAY = "2026-10-15"
P = "saadat-fellay-20261015"
SHA = "4bc2452110f280a7ba8baa4c7c28beac89769511019666bc77fc33af9b3bcd60"
PDF_URL = "https://openreview.net/pdf?id=NUleWh1GFx"
FORUM_URL = "https://openreview.net/forum?id=NUleWh1GFx"
RETRIEVED_AT = "2026-10-15T10:56:26Z"
EXTRACTOR_NOTE = ("Claude (Opus 5.5) extraction agent for rewire-benchmark-data#162; extraction only, not a review. "
                  "Pending an independent review-evidence pass.")
AREAS = ["dna-genomes"]
HARDWARE = "NVIDIA H100 (section 2.4); 'H100 94GB GPUs' (section 4)"

# Existing records reused (never changed).
M_GENA = "regulatory-variant-20261009-model-gena-lm"
M_NT = "discovery-model-nucleotide-transformer"

S = P + "-source-paper"
D_SYN = P + "-data-synthetic-dna"
PR_FID = P + "-protocol-pseudo-perplexity-agreement"
PR_TRAIN = P + "-protocol-training-peak-memory"
PR_QUANT = P + "-protocol-quantization-peak-memory"

FIGURE1_LEGEND = [  # (panel title, printed legend text)
    ("GENA-LM 110M", "r = 1.00"),
    ("GENA-LM 336M", "r = 1.00"),
    ("NT 500M", "r = 1.00"),
    ("NT 2.5B", "r = 0.98"),
]

MODELS = {
    "gena-lm-110m": ("GENA-LM 110M", M_GENA, "GENA-LM"),
    "gena-lm-336m": ("GENA-LM 336M", M_GENA, "GENA-LM"),
    "nt-500m": ("NT 500M", M_NT, "Nucleotide Transformer"),
    "nt-2-5b": ("NT 2.5B", M_NT, "Nucleotide Transformer"),
}

CHECKPOINT_MISSING = {"reason": "unreported", "note": (
    "The paper names the family and parameter count only. No Hugging Face repository, revision or pretraining "
    "dataset is given (several GENA-LM and Nucleotide Transformer checkpoints share these sizes).")}

QUANT_DISCREPANCY = (
    "Section 2.4 says the quantization experiment measures parameter memory, and Section 3.5 opens 'Quantization reduces parameter "
    "memory' before giving these values, but the Figure 5 right panel is labelled 'Peak Memory (GB)'. A 1.1 GB drop is small for "
    "parameters alone (2.5 billion weights are about 5 GB in BF16 and about 1.25 GB at 4 bits; an extractor's estimate, not printed), "
    "so the values look like peak memory of a run whose input length, batch size and quantised layers ('a conservative strategy for "
    "NT models') are not stated. Recorded as peak memory.")

EFFICIENT = ("FlashAttention exact attention, padding-free sequence packing through the variable-length "
             "FlashAttention interface, and token-budget batching")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def text_of(pdf):
    out = subprocess.run(["pdftotext", pdf, "-"], check=True, capture_output=True).stdout.decode("utf-8")
    return re.sub(r"\s+", " ", out)


def review(note):
    return {
        "method": ["transcription"],
        "method_note": note,
        "reviewer": ["claude"],
        "reviewer_note": EXTRACTOR_NOTE,
        "date": TODAY,
        "artifact_sha256": SHA,
        "retrieval_url": PDF_URL,
        "note": "Extracted, not reviewed. The review-evidence pass must re-check this value against the pinned artifact.",
    }


def base(id_, kind, name, description, facets=None, links=None, attributes=None):
    return {
        "id": id_, "kind": kind, "name": name, "description": description, "status": "needs_review",
        "facets": facets if facets is not None else {"areas": AREAS, "contexts": ["research"]},
        "source_ids": [S], "links": links or [], "attributes": attributes or {},
    }


def main(pdf, batch):
    assert sha256(pdf) == SHA, "PDF hash does not match the pinned SHA-256"
    text = text_of(pdf)

    def assert_text(*phrases):
        for p in phrases:
            assert p in text, f"not found in PDF text: {p!r}"

    # Page header and setup sentences that the records rest on.
    assert_text(
        "Published as a workshop paper at ICLR 2026",
        "Ali Saadat, Jacques Fellay",
        "GENA-LM (Fishman et al., 2025) (110M, 336M) and Nucleotide Transformer (NT) (Dalla-Torre et al., 2025) (500M, 2.5B)",
        "Synthetic sequences: uniformly sampled from {A,C,G,T} with fixed random seed (42) to isolate implementation and hardware effects. For pseudo-perplexity, we evaluate 50 sequences of length 1000.",
        "Fidelity: agreement between baseline and efficient implementations, measured by Pearson correlation (r) between pseudo-perplexity values.",
        "Each point corresponds to one sequence (50 total). Pearson correlations are shown in the legend.",
        "All experiments run on NVIDIA H100 GPU.",
        "benchmarks were run on H100 94GB GPUs",
        "Unless stated otherwise, we fine-tune with LoRA rank 16, dropout = 0.1, weight decay = 0.01, and batch size 16 for 5 epochs using AdamW with learning rate 10",
        "we measure peak GPU memory at sequence length 1000 and batch size 16 under progressive optimization stages (Figure 3)",
        "ZeRO Stage-2 CPU offload provides the largest incremental benefit for the NT 2.5B checkpoint (33.88 → 11.49 GB)",
        "(e.g., GENA-LM 110M increases from 1.18 to 2.49 GB)",
        "We evaluate 4-bit and 8-bit quantization using a conservative strategy for NT models and quantify drift relative to BF16 via embedding cosine similarity (Figure 5).",
        "For NT 2.5B, memory decreases from 6.7 GB (BF16) to 5.6 GB (4-bit).",
        "Quantization trade-offs: parameter memory and embedding cosine similarity relative to BF16.",
        "All models except NT 2.5B maintain embedding similarity above 0.98. NT 2.5B is more sensitive: quantization lowers similarity to roughly 0.9.",
        "The efficient implementation substantially improves end-to-end fine-tuning efficiency. Speedups generally increase with model size",
        "Across models and tasks, the efficient and baseline implementations achieve broadly comparable classification accuracy.",
        "promoter prediction (300 bp) and enhancer prediction (400 bp) from the Nucleotide Transformer benchmark suite",
        "Peak GPU memory. We report peak allocated GPU memory during the measured region using the framework allocator statistics",
    )

    records, claims_rows = [], []

    # Source.
    records.append(base(S, "source",
        "Optimizing genomic language models for efficient training, fine-tuning, and inference (Saadat and Fellay, ICLR 2026 workshop)",
        "Workshop paper PDF retrieved from OpenReview and hashed for the issue #162 extraction.",
        links=[], attributes={
            "artifact_url": PDF_URL,
            "url": FORUM_URL,
            "retrieved_at": RETRIEVED_AT,
            "artifact_sha256": SHA,
            "publication_status": "peer_reviewed",
            "version": "OpenReview PDF headed 'Published as a workshop paper at ICLR 2026' (11 pages; PDF CreationDate 2026-03-09)",
            "venue": "ICLR 2026 workshop (the workshop is not named in the PDF)",
            "year": 2026,
            "media_type": "application/pdf",
            "retrieval_note": ("OpenReview answers scripted requests with a bot challenge, so the PDF was downloaded by hand in a browser "
                               "by the repository owner on 2026-10-15 (file 49_Optimizing_Genomic_Language.pdf; the browser recorded the "
                               "download URL as https://openreview.net/pdf?id=NUleWh1GFx). retrieved_at is the file's creation time. "
                               "The OpenReview API also returned a challenge, so the forum metadata (workshop name, licence, code link) was not read."),
            "missing_metadata": {
                "licence": {"reason": "unavailable", "note": "No licence is printed in the PDF and the OpenReview forum page could not be read by script."},
                "doi": {"reason": "inapplicable", "note": "OpenReview workshop paper without a DOI"},
            },
        }))
    records[-1]["source_ids"] = []

    # Dataset.
    records.append(base(D_SYN, "dataset", "Synthetic uniform random DNA sequences, seed 42 (Saadat and Fellay 2026)",
        "DNA sequences sampled uniformly from A, C, G and T with random seed 42, used to measure implementation and hardware effects.",
        attributes={
            "population": "50 sequences of length 1000 for the pseudo-perplexity comparison; counts for the other synthetic-input measurements are not stated",
            "split": "Not applicable: synthetic inputs for implementation measurements",
            "species": "None (synthetic)",
            "source_locator": "Section 2.4 'Data' (page 3)",
            "missing_metadata": {"version": {"reason": "unreported", "note": "Generated by the authors' code; no code or data release is cited in the PDF"}},
        }))

    # Protocols.
    records.append(base(PR_FID, "protocol",
        "Pseudo-perplexity agreement between reference and efficient implementations (Saadat and Fellay 2026 Figure 1)",
        "Per-sequence pseudo-perplexity from the reference implementation and the efficient implementation on 50 synthetic 1000-length sequences, compared by Pearson correlation.",
        links=[{"relation": "uses_data", "target_id": D_SYN}],
        attributes={
            "protocol": ("Compute masked-LM pseudo-perplexity (one position masked at a time, padding and special tokens excluded) for each of 50 "
                         "uniform random sequences of length 1000 with the reference and the efficient implementation; report the Pearson "
                         "correlation across sequences."),
            "metric": "pearson-correlation",
            "metric_definition": "Pearson r between per-sequence pseudo-perplexity of the reference and the efficient implementation (Appendix A.2, Eq. 2)",
            "version": "ICLR 2026 workshop paper, Section 3.1 and Appendix A.2",
            "limitations": [
                "Synthetic sequences at one length; the authors note it does not cover longer contexts or real genomic sequence.",
                "r is printed to two decimals inside the figure; per-sequence values are plotted, not printed.",
                "Numeric precision of each run (BF16 or FP32) is not stated.",
            ],
            "source_locator": "Section 2.4 'Evaluation axes and metrics' item 1 and 'Data'; Section 3.1; Figure 1 (page 4); Appendix A.2",
        }))
    records.append(base(PR_TRAIN, "protocol",
        "Training peak GPU memory under progressive optimizations, sequence length 1000, batch size 16 (Saadat and Fellay 2026 Figure 3)",
        "Peak GPU memory of a training step at sequence length 1000 and batch size 16, adding FlashAttention, activation checkpointing and ZeRO Stage-2 CPU offload in turn.",
        links=[{"relation": "uses_data", "target_id": D_SYN}],
        attributes={
            "protocol": ("Measure peak allocated GPU memory (PyTorch allocator statistics) during training at sequence length 1000 and batch size 16, "
                         "for the baseline and after cumulatively adding FlashAttention, activation checkpointing and ZeRO Stage-2 CPU offload "
                         "(DeepSpeed), on an NVIDIA H100."),
            "metric": "peak-memory",
            "unit": "gigabyte",
            "memory_measurement": "Peak allocated GPU memory from the framework allocator statistics during the measured region (Appendix A.3)",
            "version": "ICLR 2026 workshop paper, Section 3.3",
            "limitations": [
                "Only the stage values quoted in Section 3.3 are printed; the other Figure 3 points are plotted without values.",
                "The training input is not named. The paper lists synthetic sequences as its input for implementation measurements and the "
                "promoter and enhancer tasks as its only real data; the training ablation is linked to the synthetic data on that basis.",
                "Whether the ablation trains with LoRA (the stated default for fine-tuning) or updates all weights is not stated.",
                "Single hardware type (H100 94GB); offload benefit depends on CPU-GPU bandwidth, as the authors note.",
            ],
            "source_locator": "Section 3.3 and Figure 3 (pages 5-6); Appendix A.3 'Peak GPU memory'",
            "missing_metadata": {"replicates": {"reason": "unreported"}},
        }))
    records.append(base(PR_QUANT, "protocol",
        "Peak memory under 8-bit and 4-bit quantization relative to BF16 (Saadat and Fellay 2026 Figure 5)",
        "GPU memory of each model at BF16, 8-bit and 4-bit weights (bitsandbytes), alongside embedding cosine similarity to BF16.",
        links=[{"relation": "uses_data", "target_id": D_SYN}],
        attributes={
            "protocol": ("Load each model in BF16, 8-bit and 4-bit (bitsandbytes; a 'conservative strategy' for NT models), compute embeddings and "
                         "report memory and cosine similarity of the embeddings to BF16."),
            "metric": "peak-memory",
            "unit": "gigabyte",
            "version": "ICLR 2026 workshop paper, Section 3.5",
            "limitations": [
                "Section 2.4 calls the measure parameter memory; Figure 5 labels it peak memory (see the source's evidence concern).",
                "Input length, batch size and input sequences are not stated; the link to the synthetic data follows the paper's two input categories and is not stated for this experiment.",
                "The 'conservative strategy' for NT models is not defined.",
                "Only the NT 2.5B BF16 and 4-bit values are printed; the other bars are plotted without values.",
            ],
            "source_locator": "Section 2.4 item 5; Section 3.5 and Figure 5 (page 7)",
            "missing_metadata": {"replicates": {"reason": "unreported"}},
        }))

    # Configurations, evaluations and results.
    def config(key, slug, name_suffix, description, fine_tuning, extra=None):
        label, model, family = MODELS[key]
        cid = f"{P}-config-{key}-{slug}"
        attrs = {
            "reported_name": label,
            "model_family": family,
            "hardware": {"description": HARDWARE},
            "source_locator": "Section 2.2 'Models'; Section 2.3; Section 2.4",
            "provenance_note": ("Implementation and measurements by Saadat and Fellay (EPFL), who did not develop the model. "
                                "Checkpoint identity is not stated, so the configuration stays at family level."),
            "missing_metadata": {"checkpoint": CHECKPOINT_MISSING, "version": {"reason": "unreported", "note": "No code release or software versions are given in the PDF"}},
        }
        if fine_tuning:
            attrs["fine_tuning"] = {"description": fine_tuning}
        attrs.update(extra or {})
        records.append(base(cid, "configuration", f"{label}, {name_suffix} (Saadat and Fellay 2026)", description,
            facets={"areas": AREAS, "contexts": ["research"], "method_types": ["foundation_model"]},
            links=[{"relation": "configuration_of", "target_id": model}], attributes=attrs))
        return cid

    def evaluation(cid, slug, name, protocol, comparison, locator, extra=None):
        eid = f"{P}-eval-{slug}"
        attrs = {
            "origin": "independent_paper",
            "protocol": protocol,
            "version": "Primary source as retrieved 2026-10-15",
            "comparison": dict(comparison, protocol_id=protocol, dataset_version=None, metric_implementation=None),
            "source_locator": locator,
            "inference_hardware" if protocol != PR_TRAIN else "training_hardware": HARDWARE,
            "missing_metadata": {"comparison.dataset_version": {"reason": "inapplicable", "note": "Synthetic sequences generated by the authors"},
                                 "comparison.metric_implementation": {"reason": "unreported", "note": "No code release is cited"}},
        }
        attrs.update(extra or {})
        records.append(base(eid, "evaluation", name, "Published result; transcribed, not reproduced.",
            links=[{"relation": "system", "target_id": cid}, {"relation": "assessment", "target_id": protocol},
                   {"relation": "data", "target_id": D_SYN}], attributes=attrs))
        return eid

    def result(eid, slug, name, metric, unit, printed, numeric, locator, qualifier, note, extra=None):
        rid = f"{P}-result-{slug}"
        attrs = {
            "metric": metric, "metric_direction": "higher" if metric == "pearson-correlation" else "lower", "unit": unit,
            "printed_value": printed, "numeric_value": numeric, "source_locator": locator, "metric_qualifier": qualifier,
            "missing_metadata": {"uncertainty": {"reason": "unreported"}},
            "review": review(note), "hardware": HARDWARE,
        }
        attrs.update(extra or {})
        records.append(base(rid, "result", name, "Reported value transcribed from the pinned source. Not independently reproduced.",
            facets={}, links=[{"relation": "evaluation", "target_id": eid}], attributes=attrs))
        claims_rows.append([rid, S, locator, printed, "result"])

    # Figure 1: fidelity, efficient implementation of each checkpoint.
    for (panel, legend), key in zip(FIGURE1_LEGEND, MODELS):
        label = MODELS[key][0]
        assert panel == label
        m = re.fullmatch(r"r = (\d\.\d\d)", legend)
        assert m
        cid = config(key, "efficient-inference", "efficient inference implementation",
            f"{label} forward pass run with {EFFICIENT}; attention stays exact and weights are unchanged.",
            None)
        eid = evaluation(cid, f"{key}-pseudo-perplexity-agreement", f"{label} efficient implementation, pseudo-perplexity agreement with the reference",
            PR_FID, {"split": "Not applicable", "population": "50 uniform random DNA sequences of length 1000, seed 42",
                     "inputs": "DNA sequence", "adaptation": "None (pretrained weights, masked-LM head)",
                     "aggregation": "Pearson correlation across 50 per-sequence pseudo-perplexities", "budget": "Single pass per masked position"},
            f"Figure 1, panel '{panel}' (page 4)")
        result(eid, f"{key}-pseudo-perplexity-pearson-r", f"{label} pseudo-perplexity agreement, Pearson r",
            "pearson-correlation", "unitless", legend, m.group(1),
            f"Figure 1 (page 4, raster), panel '{panel}', legend text '{legend}'",
            "Agreement of per-sequence pseudo-perplexity between the reference and the efficient implementation, 50 synthetic sequences of length 1000",
            "Legend text read from the embedded raster of Figure 1 (image object 6, 3566 x 2970 px) at native resolution; the PDF has no text layer for it. Panel title asserted against the extraction table.",
            {"unit_detail": "Printed as 'r = ' with two decimals"})

    # Section 3.3: training peak memory.
    TRAIN = [
        ("gena-lm-110m", "flashattention-checkpointing", "1.18", "+ Checkpointing (FlashAttention and activation checkpointing)",
         "(e.g., GENA-LM 110M increases from 1.18 to 2.49 GB)"),
        ("gena-lm-110m", "flashattention-checkpointing-zero2", "2.49", "+ DeepSpeed (FlashAttention, checkpointing and ZeRO Stage-2 CPU offload)",
         "(e.g., GENA-LM 110M increases from 1.18 to 2.49 GB)"),
        ("nt-2-5b", "flashattention-checkpointing", "33.88", "+ Checkpointing (FlashAttention and activation checkpointing)",
         "the NT 2.5B checkpoint (33.88 → 11.49 GB)"),
        ("nt-2-5b", "flashattention-checkpointing-zero2", "11.49", "+ DeepSpeed (FlashAttention, checkpointing and ZeRO Stage-2 CPU offload)",
         "the NT 2.5B checkpoint (33.88 → 11.49 GB)"),
    ]
    for key, slug, printed, stage, quote in TRAIN:
        label = MODELS[key][0]
        assert quote in text and printed in quote
        zero = slug.endswith("zero2")
        tech = ("FlashAttention, layer-wise activation checkpointing and ZeRO Stage-2 optimizer-state and gradient offload to CPU (DeepSpeed)"
                if zero else "FlashAttention and layer-wise activation checkpointing, without ZeRO offload")
        cid = config(key, f"training-{slug}", "training with " + ("FlashAttention, checkpointing and ZeRO-2 offload" if zero else "FlashAttention and checkpointing"),
            f"Training of {label} with {tech}, at sequence length 1000 and batch size 16.",
            f"{tech}; whether LoRA (the paper's fine-tuning default: rank 16 on query, key and value) was active in this ablation is not stated",
            {"training_setting": f"Figure 3 stage '{stage.split(' (')[0]}', cumulative over the previous stages"})
        eid = evaluation(cid, f"{key}-training-peak-memory-{slug}", f"{label} training peak memory, stage {stage.split(' (')[0]}",
            PR_TRAIN, {"split": "Not applicable", "population": "Training batches of 16 sequences of length 1000",
                       "inputs": "DNA sequence", "adaptation": "Training step; LoRA or full update not stated",
                       "aggregation": "Peak over the measured region", "budget": "Sequence length 1000, batch size 16"},
            "Section 3.3 'ZeRO offload' paragraph (page 6); Figure 3")
        result(eid, f"{key}-training-peak-memory-{slug}", f"{label} training peak GPU memory, {stage.split(' (')[0]}",
            "peak-memory", "gigabyte", printed, printed,
            f"Section 3.3 'ZeRO offload' paragraph (page 6): '{quote}'; stage {stage} of Figure 3",
            f"Training, sequence length 1000, batch size 16, stage {stage}",
            "Exact phrase asserted in the pinned PDF text; the stage follows from the sentence (ZeRO offload changes memory from the previous stage) and the Figure 3 stage order.",
            {"unit_detail": "Printed as GB", "scope_note": "Peak allocated GPU memory (Appendix A.3)"})

    # Section 3.5: quantization memory.
    for slug, printed, setting in [("bf16", "6.7", "BF16"), ("4bit", "5.6", "4-bit")]:
        cid = config("nt-2-5b", f"{slug}-inference", f"{setting} weights for embedding inference",
            f"NT 2.5B embedding inference with {'BF16 weights, the reference for quantization drift' if slug == 'bf16' else '4-bit bitsandbytes weight quantization, using what the authors call a conservative strategy for NT models'}.",
            None, {"configuration": {"weights": setting, "library": "bitsandbytes"} if slug == "4bit" else {"weights": setting}})
        eid = evaluation(cid, f"nt-2-5b-quantization-memory-{slug}", f"NT 2.5B {setting} inference memory",
            PR_QUANT, {"split": "Not applicable", "population": None, "inputs": "DNA sequence", "adaptation": "None (pretrained weights)",
                       "aggregation": None, "budget": None},
            "Section 3.5 'Memory' paragraph (page 7); Figure 5 right panel",
            {"missing_metadata": {
                "comparison.dataset_version": {"reason": "unreported"},
                "comparison.metric_implementation": {"reason": "unreported", "note": "No code release is cited"},
                "comparison.population": {"reason": "unreported", "note": "Input sequences, length and batch size are not stated for Figure 5"},
                "comparison.aggregation": {"reason": "unreported"},
                "comparison.budget": {"reason": "unreported"}}})
        result(eid, f"nt-2-5b-quantization-memory-{slug}", f"NT 2.5B {setting} memory",
            "peak-memory", "gigabyte", printed, printed,
            "Section 3.5 'Memory' paragraph (page 7): 'For NT 2.5B, memory decreases from 6.7 GB (BF16) to 5.6 GB (4-bit).'",
            f"Embedding inference with {setting} weights; the paper calls it parameter memory in Section 2.4 and peak memory in Figure 5",
            "Exact sentence asserted in the pinned PDF text.",
            {"unit_detail": "Printed as GB", "source_discrepancy": QUANT_DISCREPANCY})

    # Claims about the paper's findings that carry no printed values.
    def claim(slug, field, value, locator, extra=None):
        cid = f"{P}-claim-{slug}"
        attrs = {"field": field, "value": value, "source_locator": locator,
                 "review": review("Each source sentence the claim rests on asserted verbatim in the pinned PDF text.")}
        attrs.update(extra or {})
        records.append(base(cid, "claim", f"{field}: Saadat and Fellay 2026", "Descriptive fact transcribed from the pinned source.",
            facets={}, links=[{"relation": "subject", "target_id": S}], attributes=attrs))
        claims_rows.append([cid, S, locator, value, "claim"])

    claim("quantization-embedding-similarity", "reported_finding",
        ("Under 8-bit and 4-bit quantization, embedding cosine similarity to BF16 stays above 0.98 for GENA-LM 110M, GENA-LM 336M and NT 500M; "
         "for NT 2.5B quantization lowers it to roughly 0.9."),
        "Section 3.5 'Fidelity' paragraph (page 6): 'All models except NT 2.5B maintain embedding similarity above 0.98. NT 2.5B is more sensitive: quantization lowers similarity to roughly 0.9.'",
        {"limitations": ["Bounds and an approximate value, not per-model results; Figure 5 left panel plots the bars without values.",
                         "The paper does not say which of 8-bit and 4-bit gives 'roughly 0.9' for NT 2.5B."]})
    claim("fine-tuning-efficiency", "reported_finding",
        ("With LoRA fine-tuning on the Nucleotide Transformer benchmark promoter (300 bp) and enhancer (400 bp) tasks, the authors report that "
         "the efficient implementation substantially reduces training time and peak GPU memory, with speedups generally increasing with model "
         "size, and achieves broadly comparable accuracy to the baseline implementation."),
        "Abstract; Section 3.4 'Efficiency' and 'Task performance' paragraphs (page 6); Figure 4 (page 7)",
        {"limitations": ["Figure 4 plots accuracy, peak memory and total training time per model and implementation without printed values, so no speedup, memory or accuracy figure is recorded."]})
    claim("figures-not-extracted", "tables_not_extracted",
        ("Not extracted as results: Figure 2 (inference peak memory and throughput against sequence length 256-4096 and batch size 1-32), "
         "the Figure 3 points not quoted in Section 3.3 (baseline and FlashAttention stages for all models; every stage for GENA-LM 336M and NT 500M), "
         "Figure 4 (fine-tuning accuracy, peak memory and training time for promoter and enhancer prediction) and Figure 5 apart from the "
         "NT 2.5B BF16 and 4-bit memory. These figures plot values without printing them, and the repository does not read numbers from plotted marks."),
        "Figures 2-5 (pages 5-7)")

    os.makedirs(batch, exist_ok=True)
    records.sort(key=lambda r: r["id"])
    for r in records:  # the store keeps missing_metadata keys sorted
        if "missing_metadata" in r["attributes"]:
            r["attributes"]["missing_metadata"] = dict(sorted(r["attributes"]["missing_metadata"].items()))
    ids = [r["id"] for r in records]
    assert len(ids) == len(set(ids))
    with open(os.path.join(batch, "batch.jsonl"), "w") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False, sort_keys=False) + "\n")
    with open(os.path.join(batch, "claims.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["record_id", "source_id", "locator", "printed_value", "review_scope"])
        for row in sorted(claims_rows):
            w.writerow(row)
    counts = {}
    for r in records:
        counts[r["kind"]] = counts.get(r["kind"], 0) + 1
    print(json.dumps(counts, sort_keys=True))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
