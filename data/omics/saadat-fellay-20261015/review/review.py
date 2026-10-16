"""Independent review of saadat-fellay-20261015 (2026-10-15).

Usage: python3 -I review/review.py <paper.pdf>

Checks every result and claim against the pinned PDF with its own text parse, applies the
corrections listed in docs/reviews/saadat-fellay-2026-10-15-review.md, sets every record to
source_checked, writes the review objects, and writes batch.jsonl and the matching store lines.
Refuses to run unless batch.jsonl is the extractor output that was checked (commit fc3881f).
Run `npm run records -- change` on every batch ID afterwards.
"""
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

BATCH_DIR = Path(__file__).resolve().parent.parent
ROOT = BATCH_DIR.parents[2]
BATCH = BATCH_DIR / "batch.jsonl"
BATCH_SHA_BEFORE = "e3702fd5d1fab507a375797133158722a15131ac982144e5153342a319e812d0"
PDF_SHA = "4bc2452110f280a7ba8baa4c7c28beac89769511019666bc77fc33af9b3bcd60"
PDF_URL = "https://openreview.net/pdf?id=NUleWh1GFx"
REVIEWED_AT = "2026-10-15T22:00:00Z"
REVIEW_DOC = "docs/reviews/saadat-fellay-2026-10-15-review.md"
P = "saadat-fellay-20261015-"
REVIEWER_NOTE = ("Claude review agent; no human review claimed. Independent Claude (Opus 5.5) review agent, separate from "
                 "the extraction agent that built this batch. Automated review only. Transcription, not reproduction.")

pdf = Path(sys.argv[1])
assert hashlib.sha256(pdf.read_bytes()).hexdigest() == PDF_SHA, "PDF hash mismatch"
assert hashlib.sha256(BATCH.read_bytes()).hexdigest() == BATCH_SHA_BEFORE, "batch.jsonl is not the reviewed extractor output"
text = subprocess.run(["pdftotext", str(pdf), "-"], capture_output=True, text=True, check=True).stdout
flat = re.sub(r"\s+", " ", text)
records = [json.loads(line) for line in BATCH.read_text().splitlines()]
by_id = {r["id"]: r for r in records}
assert len(records) == 38 and all(r["status"] == "needs_review" for r in records)

# ---- Independent value check ---------------------------------------------------------------------
# (result suffix, printed value, unit, direction, sentence the value must appear in, model label)
TEXT_RESULTS = [
    ("gena-lm-110m-training-peak-memory-flashattention-checkpointing", "1.18", "gigabyte", "lower",
     "(e.g., GENA-LM 110M increases from 1.18 to 2.49 GB)", "GENA-LM 110M"),
    ("gena-lm-110m-training-peak-memory-flashattention-checkpointing-zero2", "2.49", "gigabyte", "lower",
     "(e.g., GENA-LM 110M increases from 1.18 to 2.49 GB)", "GENA-LM 110M"),
    ("nt-2-5b-training-peak-memory-flashattention-checkpointing", "33.88", "gigabyte", "lower",
     "ZeRO Stage-2 CPU offload provides the largest incremental benefit for the NT 2.5B checkpoint (33.88 → 11.49 GB)", "NT 2.5B"),
    ("nt-2-5b-training-peak-memory-flashattention-checkpointing-zero2", "11.49", "gigabyte", "lower",
     "ZeRO Stage-2 CPU offload provides the largest incremental benefit for the NT 2.5B checkpoint (33.88 → 11.49 GB)", "NT 2.5B"),
    ("nt-2-5b-quantization-memory-bf16", "6.7", "gigabyte", "lower",
     "For NT 2.5B, memory decreases from 6.7 GB (BF16) to 5.6 GB (4-bit).", "NT 2.5B"),
    ("nt-2-5b-quantization-memory-4bit", "5.6", "gigabyte", "lower",
     "For NT 2.5B, memory decreases from 6.7 GB (BF16) to 5.6 GB (4-bit).", "NT 2.5B"),
]
# Figure 1 has no text layer. Read by this reviewer from the embedded image (pdfimages object 6,
# 3566 x 2970 px, downscaled to 1800 px wide): panel title, then the legend in its lower-right corner.
FIGURE1 = [("gena-lm-110m", "GENA-LM 110M", "r = 1.00"), ("gena-lm-336m", "GENA-LM 336M", "r = 1.00"),
           ("nt-500m", "NT 500M", "r = 1.00"), ("nt-2-5b", "NT 2.5B", "r = 0.98")]


def link(r, relation):
    return [l["target_id"] for l in r["links"] if l["relation"] == relation]


def chain(result):
    ev = by_id[link(result, "evaluation")[0]]
    return ev, by_id[link(ev, "system")[0]], by_id[link(ev, "assessment")[0]], by_id[link(ev, "data")[0]]


checked = []
for suffix, value, unit, direction, sentence, model in TEXT_RESULTS:
    r = by_id[P + "result-" + suffix]
    a = r["attributes"]
    assert sentence in flat, sentence
    assert a["printed_value"] == a["numeric_value"] == value and value in sentence
    assert a["unit"] == unit and a["metric_direction"] == direction and a["metric"] == "peak-memory"
    ev, cfg, proto, data = chain(r)
    assert cfg["attributes"]["reported_name"] == model and data["id"] == P + "data-synthetic-dna"
    assert ("training" in suffix) == (proto["id"] == P + "protocol-training-peak-memory")
    assert ("zero2" in suffix) == ("+ DeepSpeed" in a["metric_qualifier"])
    checked.append(r["id"])
for slug, title, legend in FIGURE1:
    r = by_id[P + f"result-{slug}-pseudo-perplexity-pearson-r"]
    a = r["attributes"]
    assert a["printed_value"] == legend and a["numeric_value"] == legend.split(" = ")[1]
    assert a["metric"] == "pearson-correlation" and a["unit"] == "unitless" and a["metric_direction"] == "higher"
    assert f"panel '{title}'" in a["source_locator"]
    ev, cfg, proto, data = chain(r)
    assert cfg["attributes"]["reported_name"] == title and proto["id"] == P + "protocol-pseudo-perplexity-agreement"
    checked.append(r["id"])
assert sorted(checked) == sorted(r["id"] for r in records if r["kind"] == "result")
for phrase in ("All models except NT 2.5B maintain embedding similarity above 0.98. NT 2.5B is more sensitive: quantization lowers similarity to roughly 0.9.",
               "We fine-tune all checkpoints on promoter and enhancer binary classification using LoRA",
               "Speedups generally increase with model size",
               "the efficient and baseline implementations achieve broadly comparable classification accuracy",
               "promoter prediction (300 bp) and enhancer prediction (400 bp) from the Nucleotide Transformer benchmark suite",
               "uniformly sampled from {A,C,G,T} with fixed random seed (42)",
               "we evaluate 50 sequences of length 1000",
               "we measure peak GPU memory at sequence length 1000 and batch size 16 under progressive optimization stages",
               "All experiments run on NVIDIA H100 GPU.", "benchmarks were run on H100 94GB GPUs",
               "5. Quantization trade-offs: parameter memory and embedding cosine similarity relative to BF16."):
    assert phrase in flat, phrase
assert "github" not in flat.lower() and "huggingface" not in flat.lower()  # no code or checkpoint link printed

# ---- Corrections and additions --------------------------------------------------------------------
FIG5 = (" Independent review 2026-10-15: the Figure 5 right-panel bars for NT 2.5B also do not match the printed sentence. "
        "Against the panel's gridlines they stand at about 6.6 GB (BF16) and about 5.45 GB (4-bit), against 6.7 and 5.6 in the "
        "text (reviewer's reading of bar heights, not a printed value). The direction and size of the drop agree, so the "
        "printed values are kept with this note and no source-level concern is raised.")
for suffix in ("bf16", "4bit"):
    a = by_id[P + f"result-nt-2-5b-quantization-memory-{suffix}"]["attributes"]
    a["source_discrepancy"] += FIG5

q = by_id[P + "protocol-quantization-peak-memory"]["attributes"]["limitations"]
old = "Section 2.4 calls the measure parameter memory; Figure 5 labels it peak memory (see the source's evidence concern)."
q[q.index(old)] = ("Section 2.4 calls the measure parameter memory; Figure 5 labels it peak memory. The printed NT 2.5B values "
                   "(6.7 and 5.6 GB) also sit slightly above the plotted bars (about 6.6 and 5.45 GB). See source_discrepancy "
                   "on the two NT 2.5B results.")

t = by_id[P + "protocol-training-peak-memory"]["attributes"]["limitations"]
i = t.index("Whether the ablation trains with LoRA (the stated default for fine-tuning) or updates all weights is not stated.")
t[i] = ("Whether the ablation trains with LoRA (the stated default for fine-tuning) or updates all weights is not stated. "
        "Section 3.3 attributes the NT 2.5B ZeRO saving to optimizer state dominating, which fits a full-weight update better "
        "than LoRA rank 16 on query, key and value projections, but the paper does not say.")
t.insert(i + 1, "Whether 'sequence length 1000' counts nucleotides or tokens is not stated; NT uses 6-mer tokens and GENA-LM "
                "uses BPE tokens, so the two families see different token counts for 1000 nucleotides.")

f = by_id[P + "protocol-pseudo-perplexity-agreement"]["attributes"]["limitations"]
f += [
    "Figure 1 axes (labelled 'Perplexity') run from about 15,000 to 30,000 for the NT models, above the size of the NT 6-mer "
    "vocabulary (about 4,100 tokens; Dalla-Torre et al., not stated in this paper), so the NT models score uniform random DNA "
    "worse than a uniform guess. The paper does not comment on this.",
    "Section 2.3 says attention stays exact when quantization is off, yet NT 2.5B prints r = 0.98 with visibly scattered points. "
    "The paper does not explain the difference; numeric precision may contribute.",
]

c = by_id[P + "claim-fine-tuning-efficiency"]["attributes"]["limitations"]
c += [
    "'Broadly comparable' is the authors' wording. Figure 4 plots lower accuracy for the efficient than the baseline "
    "implementation in seven of the eight model-task pairs (all but GENA-LM 336M promoter), and GENA-LM 110M promoter "
    "accuracy close to 50% for both implementations on a binary task; no values are printed.",
    "Figure 4 reports one run per bar with no spread.",
]

# ---- Review objects --------------------------------------------------------------------------------
TEXT_NOTE = ("Matched the pinned PDF SHA-256 (archived copy of the hand download; OpenReview blocks scripted retrieval). "
             "review/review.py re-parsed the PDF with pdftotext and asserted the source sentence, printed and numeric value, unit, "
             "direction, model label, protocol, data link and Figure 3 stage. The stage was also checked by eye against Figure 3, "
             "whose plotted points agree with the printed pairs.")
FIG1_NOTE = ("Matched the pinned PDF SHA-256. Figure 1 has no text layer; the reviewer extracted the embedded image (pdfimages "
             "object 6) and read the panel title and the legend in its lower-right corner. review/review.py asserts the reading "
             "against printed value, numeric value, locator, model label and protocol.")
for r in records:
    a = r["attributes"]
    old = a.get("review") or {}
    r["status"] = "source_checked"
    review = {"reviewer": ["claude"], "reviewer_note": REVIEWER_NOTE, "reviewed_at": REVIEWED_AT,
              "artifact_sha256": PDF_SHA, "retrieval_url": PDF_URL}
    if r["kind"] == "result":
        fig1 = "pseudo-perplexity" in r["id"]
        review.update(method=["source-hash-verification", "pdf-text-parse", "independent-cell-check", "rendered-source-visual-check"]
                      if not fig1 else ["source-hash-verification", "rendered-source-visual-check", "independent-cell-check"],
                      method_note=FIG1_NOTE if fig1 else TEXT_NOTE)
        if "quantization" in r["id"]:
            review["note"] = ("Value matches the printed sentence. Plotted bar differs slightly and the quantity is ambiguous "
                              "(parameter or peak memory); see source_discrepancy. Kept as a result-level note.")
        elif r["id"] == P + "result-nt-2-5b-pseudo-perplexity-pearson-r":
            review["note"] = "Value, metric and identity match the source. See the protocol's limitations on the NT 2.5B scatter."
        else:
            review["note"] = "Value, metric and identity match the source."
    elif r["kind"] == "claim":
        review.update(method=["source-hash-verification", "pdf-text-parse", "rendered-source-visual-check", "ai-assisted-source-review"],
                      method_note="Source sentences asserted in the pdftotext output by review/review.py; Figures 2-5 viewed to check the claim's scope.",
                      note=("Correct. Limitations added in review on what Figure 4 plots." if r["id"].endswith("fine-tuning-efficiency")
                            else "Correct; Figure 5 left panel is consistent with the bounds."))
    elif r["kind"] == "evaluation":
        review.update(method=["source-hash-verification", "pdf-text-parse", "scope-review"],
                      method_note="Links, origin, comparison fields and missing-metadata reasons checked against the PDF and the linked protocol.",
                      note=("Origin independent_paper checked: the authors (EPFL) are not among the GENA-LM (Fishman et al.) or "
                            "Nucleotide Transformer (Dalla-Torre et al.) authors and cite both as other work."))
    elif r["kind"] == "source":
        review.update(method=["source-hash-verification", "ai-assisted-source-review"],
                      method_note=("Checked the archived copy of the 2026-10-15 hand download against the pinned SHA-256; no fresh "
                                   "download (OpenReview answers scripted requests with a bot challenge). URL, version, venue and "
                                   "missing-metadata reasons checked against the PDF."),
                      note="Hash matches. No source-level evidence concern; the quantization memory conflict is recorded on the two affected results.")
    else:
        review.update(method=["source-hash-verification", "pdf-text-parse", "ai-assisted-source-review", "scope-review"],
                      method_note="Descriptive fields, identity links and missing-metadata reasons checked against the PDF.",
                      note={P + "protocol-quantization-peak-memory": "Limitation on the evidence concern corrected in review (no such concern exists); synthetic-data link kept as an inference the protocol discloses.",
                            P + "protocol-training-peak-memory": "Limitations added in review: sequence-length unit and the LoRA-or-full-update question.",
                            P + "protocol-pseudo-perplexity-agreement": "Limitations added in review on NT pseudo-perplexity range and the NT 2.5B scatter.",
                            }.get(r["id"], "Checked; see the dated review."))
    a["review"] = review

records.sort(key=lambda r: r["id"])
BATCH.write_text("".join(json.dumps(r, separators=(",", ":"), ensure_ascii=False) + "\n" for r in records))

# Mirror into the canonical store; `records -- change` then rewrites the files in store order.
by_id = {r["id"]: r for r in records}
replaced = 0
for shard in sorted((ROOT / "data").glob("e*/**/*.jsonl")):
    lines = shard.read_text().splitlines()
    out = []
    for line in lines:
        rid = json.loads(line)["id"]
        if rid in by_id:
            line = json.dumps(by_id[rid], separators=(",", ":"), ensure_ascii=False)
            replaced += 1
        out.append(line)
    if out != lines:
        shard.write_text("".join(l + "\n" for l in out))
assert replaced == len(records), replaced

cov_path = BATCH_DIR / "coverage.json"
cov = json.loads(cov_path.read_text())
cov["status"] = f"reviewed ({REVIEW_DOC})"
cov_path.write_text(json.dumps(cov, indent=2, ensure_ascii=False) + "\n")
print(len(records), hashlib.sha256(BATCH.read_bytes()).hexdigest())
