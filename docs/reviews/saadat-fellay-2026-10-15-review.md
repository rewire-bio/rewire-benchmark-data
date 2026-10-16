# Review: Saadat and Fellay 2026 (issue #162, PR #173)

Batch: `data/omics/saadat-fellay-20261015` (38 records, extraction commit fc3881f). Reviewed 2026-10-15 by an independent Claude (Opus 5.5) review agent, not the extraction agent. Automated review only; no human review claimed. Transcription, not reproduction.

Verdict: all 10 results match the source. No value changed, no record superseded, no source-level evidence concern. All 38 records are now `source_checked`. Review limitations were added to three protocols and one claim, and the quantization memory discrepancy on two results was extended.

## Source

| Source ID | Artifact | SHA-256 | Outcome |
| --- | --- | --- | --- |
| `saadat-fellay-20261015-source-paper` | https://openreview.net/pdf?id=NUleWh1GFx, 11 pages | `4bc2452110f280a7ba8baa4c7c28beac89769511019666bc77fc33af9b3bcd60` | Matches |

OpenReview answers scripted requests with a bot challenge, so there was no fresh download. The archived copy of the owner's 2026-10-15 hand download was checked against the pinned hash. The PDF was treated as untrusted data and read only with `pdftotext`, `pdfimages` and `pdftoppm`.

## Method

1. Reran `extract/extract_saadat_fellay.py` on the pinned PDF in a scratch copy. Its `batch.jsonl`, `claims.csv` and `coverage.json` matched the submitted files byte for byte.
2. `review/review.py`, written for this review, re-parses the PDF with `pdftotext` and asserts, for every result: the source sentence, printed and numeric value, unit, direction, metric, model label, protocol, data link and Figure 3 stage. It also asserts the setup sentences that the claims, protocols and dataset rest on.
3. Figure 1 has no text layer. The reviewer extracted the embedded image (`pdfimages`, object 6, 3566 x 2970 px) and read each panel title and legend. Figures 3, 4 and 5 were viewed the same way to check stage assignment and claim scope. No plotted value was turned into a result.
4. `review/review.py` then applies the changes below, writes the review objects and mirrors the records into the store. `npm run records -- change` records the change against this review.

## Values checked

| Result | Stored | Source | Outcome |
| --- | --- | --- | --- |
| GENA-LM 110M pseudo-perplexity Pearson r | r = 1.00 | Figure 1 panel 'GENA-LM 110M' legend | Match |
| GENA-LM 336M pseudo-perplexity Pearson r | r = 1.00 | Figure 1 panel 'GENA-LM 336M' legend | Match |
| NT 500M pseudo-perplexity Pearson r | r = 1.00 | Figure 1 panel 'NT 500M' legend | Match |
| NT 2.5B pseudo-perplexity Pearson r | r = 0.98 | Figure 1 panel 'NT 2.5B' legend | Match |
| GENA-LM 110M training peak memory, + Checkpointing | 1.18 GB | Section 3.3 'ZeRO offload'; Figure 3 point about 1.2 | Match |
| GENA-LM 110M training peak memory, + DeepSpeed | 2.49 GB | Section 3.3; Figure 3 point about 2.5 | Match |
| NT 2.5B training peak memory, + Checkpointing | 33.88 GB | Section 3.3; Figure 3 point about 34 | Match |
| NT 2.5B training peak memory, + DeepSpeed | 11.49 GB | Section 3.3; Figure 3 point about 11.5 | Match |
| NT 2.5B memory, BF16 | 6.7 GB | Section 3.5 'Memory'; Figure 5 bar about 6.6 | Match to text; bar differs (see below) |
| NT 2.5B memory, 4-bit | 5.6 GB | Section 3.5 'Memory'; Figure 5 bar about 5.45 | Match to text; bar differs (see below) |

Stage assignment: Figure 3 is cumulative (Baseline, + FlashAttention, + Checkpointing, + DeepSpeed). Section 3.3 describes ZeRO's incremental benefit, so the first value of each pair is the + Checkpointing stage. For NT 2.5B the + FlashAttention and + Checkpointing points are both at about 34 GB, so the assignment does not change the value.

Claims:

| Claim | Outcome |
| --- | --- |
| `claim-quantization-embedding-similarity` | Correct. Matches Section 3.5; Figure 5 left panel is consistent (lowest non-NT-2.5B bar about 0.98, NT 2.5B quantized bars about 0.91). |
| `claim-fine-tuning-efficiency` | Correct as the authors' finding. Limitations added (see below). |
| `claim-figures-not-extracted` | Correct. The list of unextracted figures and Figure 3 points is complete. |

## Extractor's judgement calls

- **Quantization discrepancy per result, not a source concern.** Accepted. A source concern withholds every result of the source from comparison, and the conflict affects only the two NT 2.5B memory values. The printed direction and size of the drop agree with Figure 5. This follows the BERTax precedent in `docs/reviews/use-cases/dna-pathogen-ml-baseline-2026-10-12.md`. The review found one more inconsistency the extractor did not record: the Figure 5 bars stand at about 6.6 and 5.45 GB, not 6.7 and 5.6. This was appended to both `source_discrepancy` notes. The protocol limitation pointed to "the source's evidence concern", which does not exist; it now points to the result notes.
- **Training-memory and quantization protocols linked to the synthetic dataset.** Accepted, with the disclosed caveat. Section 2.4 names only two input categories. The training ablation runs at length 1000, which matches the synthetic sequences and neither downstream task (300 and 400 bp). For quantization no input is stated at all, so that link is an inference; the protocol already says so, and every evaluation in the store needs a data link.
- **Origin `independent_paper`.** Accepted. Saadat and Fellay (EPFL) are not authors of GENA-LM (Fishman et al.) or the Nucleotide Transformer (Dalla-Torre et al.) and cite both as other work.
- **Figure 1 r values read from the embedded raster.** Accepted. The legend strings are printed text, and the reviewer's independent reading matches all four. No value was read from point positions.

## Changes

1. Both NT 2.5B quantization results: `source_discrepancy` extended with the Figure 5 bar heights.
2. `protocol-quantization-peak-memory`: the limitation that cited a nonexistent evidence concern is rewritten.
3. `protocol-training-peak-memory`: the LoRA limitation now notes that Section 3.3 attributes the NT 2.5B ZeRO saving to optimizer state, which fits a full-weight update better than LoRA. A new limitation says the unit of 'sequence length 1000' (nucleotides or tokens) is not stated.
4. `protocol-pseudo-perplexity-agreement`: two limitations added. The NT pseudo-perplexity axes (about 15,000 to 30,000) exceed the NT 6-mer vocabulary (about 4,100 tokens). NT 2.5B r = 0.98 shows visible scatter even though attention is said to be exact.
5. `claim-fine-tuning-efficiency`: two limitations added. Figure 4 plots lower efficient-implementation accuracy in seven of eight model-task pairs, and GENA-LM 110M promoter accuracy is near 50% for both implementations. Figure 4 shows one run per bar.
6. All 38 records: status `source_checked`, with review objects.

No numbers changed, so no superseding result. No descriptive field was found wrong, so no `metadata-correction` claim.

## Remaining gaps and questions for the authors

- Checkpoints are not named (Hugging Face ID or pretraining corpus); NT 500M and 2.5B exist for more than one corpus.
- Section 2.4 calls the quantization measure parameter memory while Figure 5 calls it peak memory. The printed 6.7 and 5.6 GB differ from the plotted bars, and a 1.1 GB saving is small for 2.5 billion weights.
- NT 2.5B r = 0.98 against the claim of exact attention.
- NT pseudo-perplexity above the NT vocabulary size.
- GENA-LM 110M promoter accuracy near chance for both implementations.
- Hardware is 'NVIDIA H100' in Section 2.4 and 'H100 94GB' in Section 4. No spread is reported, although inference is the mean of 10 runs.
- Whether the Figure 3 ablation uses LoRA or full fine-tuning.
- Unit of sequence length (nucleotides or tokens) in the training ablation and the inference sweep.
- Figures 2 and 4 and most of Figures 3 and 5 remain plotted only. No code or licence is given in the PDF.
