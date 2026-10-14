# Genomic foundation model guide sources (issue #138)

Batch: `data/omics/gfm-guide-sources-20261014` (127 records, all `needs_review`), plus a text correction to `use-case-patient-rna-splicing-validation`.

Status: extracted by a Claude (Opus 5.5) agent. **Independent review pending.** No human review is claimed, and nothing here is a reproduction.

## Use-case correction

`use-case-patient-rna-splicing-validation` says Feng et al. 2025 Table 1 (splice acceptor and donor AUC) is linked to it. At origin/main 7999572 that is not true. The Feng protocols `amp-feng-20261007-protocol-splice-acceptor` and `-splice-donor` are `assessed_by` targets of `use-case-splicing-follow-up` only, and the judgement claims `use-case-mapping-amp-20261007-feng-splice-acceptor` and `-donor` have that use case as subject.

Changed in this PR:

- `attributes.evidence_gaps[2]` now says no DNA foundation-model result is linked to this use case, and why the Feng result sits elsewhere. The old text is kept in `metadata-correction-gfm-guide-20261014-patient-rna-splicing-evidence-gaps-2`.

Not changed, for the reviewer:

- `attributes.setting` is pinned by the use case's 18 reviewed judgements, so editing it withholds all of them until they are re-pinned (`tests/use-case-records.test.ts` fails until then). The extractor cannot attest that review. Proposed replacement for its last sentence, "A separate, proxy sequence-classification AUC for DNA foundation-model embeddings (Feng et al. 2025, Table 1 Acceptor/Donor) is also linked, scoped as a different endpoint.":

  > Feng et al. 2025 Table 1 splice acceptor and donor classification by DNA foundation-model embeddings is not linked here; it is linked to 'Prioritise variants for splicing experiments'.

  To apply it: edit the record, add a `metadata-correction-` claim with the old text, run `npm run records -- change` with this review, then `npm run use-cases:repin -- <review.md> <claim-id>...` for the 18 judgements (`use-case-mapping-amp-20261007-issue12-fraser-kremer`, the `use-case-mapping-rna-splicing-*` claims on this use case). The proposed text is also in `extract/extract_gfm_guide.py` as `UC_SETTING_PROPOSAL`.

## For the reviewer

Check every result in `claims.csv` against the pinned artifacts listed in `sources.md`. Points that need judgement:

1. The EVEE v4 values differ from those in issue #138 (see `research.md`). Confirm v4 is the version to record.
2. The two EVEE source concerns, which are read from the plotting code at e5e4a43: the NTv3 column is a cosine distance, and AlphaMissense's Overall cell is its missense value.
3. The origins: EVEE's Evo 2 configurations as `author_reported` because of a name-only author overlap, and HyenaDNA Table A.2's DNABERT and NT rows as `paper_compilation`.
4. The NT fine-tuning time conflict (Methods 20 and 50 min on 8 A100s against the Discussion's "under 15 min on a single GPU").
5. The use-case correction text above.

Then fill each record's `review`, write `review.json`, set statuses with `records -- change`, and complete this document with the table of values checked.
