# Review: lit-rna-other-20261011-khoo2026, 2026-10-12

Reviewer: Claude review agent `reviewer-ro-2`, independent of the extractor `lit-rna-other`. No human review claimed. Source transcription is not reproduction.

## Reviewer's report (verbatim)

Excerpts of `reviewer-ro-2`'s report that concern this batch, unedited.

Reviewer: Claude (Opus 5.5) research agent, reviewer-ro-2. No human review claimed. I did not extract any of these batches.

Every printed value in all four batches matches the source. All corrections are to metadata, origin notes, duplicates and judgement text. No numerical result needs a superseding record.

## lit-rna-other-20261011-khoo2026: approved with corrections

K1. DreaMS checkpoint. All 16 configurations carry `missing_metadata.checkpoint` with the note "Retrieval method; DreaMS embeddings checkpoint not stated". Supplementary Note S2 says DreaMS uses the "pre-trained checkpoint, without contrastive fine-tuning".
- For `lit20261011-khoo2026-config-a1-cosine-similarity-dreams`, `...-a2-cosine-similarity-dreams` and `...-a3-cosine-similarity-dreams-sub-formula`: append "; DreaMS pre-trained checkpoint without contrastive fine-tuning (Supplementary Note S2)" to `parameters`, and set `missing_metadata.checkpoint` to `{"reason": "unreported", "note": "Pre-trained DreaMS checkpoint without contrastive fine-tuning (Note S2); the exact checkpoint file is not stated"}`.
- For the other 13 configurations, set the note to "Retrieval method; no learned checkpoint" and keep the reason `inapplicable`.

K2. Leakage caveat. Table 3 of the source reports structure leakage of test spectra into training of 62.9% (NPLIB1 random) and 95.3% (MassSpecGym random). Append a limitation to the six random-split protocols.
- `lit20261011-khoo2026-protocol-nplib1-random-a1`, `-a2` and `-a3`: "Random split: 62.9% of test spectra have their structure (first InChIKey block) in the training split (Supplementary Table 3); scores largely reflect retrieval of seen structures."
- `lit20261011-khoo2026-protocol-massspecgym-random-a1`, `-a2` and `-a3`: the same sentence with "95.3%".

Origin `author_reported` is right: the sole author ran her own nearest-neighbour baselines. Not adding a relevance judgement is also right, because fingerprint prediction is not candidate retrieval. The metric `fingerprint-tanimoto-similarity` is approved: it is distinct from `top-1-tanimoto`, which scores a retrieved candidate, and it respells no existing concept. Note that msgwild's "Nearest Neighbor† [40]" cites this author's MIT thesis. msgwild does not describe the method enough to say it is the same configuration, so do not link the two method records.

## Corrections applied

Applied by the extractor in the extraction scripts (`extract/`), as the reviewer specified, before the batch was added to the store. The review fields were set by `finalise` in `extract/lib.py`.

1. K1: the three DreaMS configurations append the reviewer's sentence to `parameters` and carry the reviewer's `missing_metadata.checkpoint`; the other 13 have the note "Retrieval method; no learned checkpoint" with reason inapplicable.
2. K2: the six random-split protocols carry the reviewer's leakage limitation (62.9% NPLIB1, 95.3% MassSpecGym).
3. Review fields: every record is `source_checked`; each result carries a review block naming reviewer-ro-2 (methods source-hash-verification, pdf-text-parse, independent-cell-check), with the extraction note kept in `note`.

## Records after correction

- configuration: 16
- dataset: 4
- evaluation: 64
- method: 1
- protocol: 12
- result: 128
- source: 1

Status: source_checked 226.
