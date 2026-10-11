# Review: use-case-coverage-rna-fusion-longread-20261011, 2026-10-11

Reviewer: Claude research agent `reviewer-onc-2`, independent of the extractor `uc-oncology`. No human review claimed. Source transcription is not reproduction. Full review: `docs/reviews/use-cases/tumour-rna-fusion-detection-2026-10-11.md`.

## Reviewer's verdict for this batch (verbatim)

### use-case-coverage-rna-fusion-longread-20261011 (Dorney et al. 2026): approved with corrections

All 597 values are correct. The corrections are one duplicate method, one relevance change and some wording.

D1. Duplicate method. `rna-fusion-longread-20261011-method-jaffal` duplicates the stored `rna-fusion-20261009-method-jaffa`; Lin 2026's JAFFAL configuration `rna-fusion-20261009-config-lin2026-jaffal` already links to it.
- Delete the record `rna-fusion-longread-20261011-method-jaffal`.
- In `rna-fusion-longread-20261011-config-jaffal`, change the `configuration_of` target to `rna-fusion-20261009-method-jaffa`.
- In `coverage.json`: add `rna-fusion-20261009-method-jaffa` to `existing_reused`, remove the jaffal ID from `new_ids_by_kind.method`, and set `new_record_counts.method` to 4.

D2. Huh7 judgement `use-case-mapping-rna-fusion-longread-20261011-huh7-known-fusions`: change `relevance` from `direct` to `proxy`. Each value pools six long-read callers, or three short-read callers for Illumina, so it scores no workflow a user would run. Platform and the number of pooled callers are confounded, and there are only three counts. Replace both `description` and `attributes.rationale` with:
> Proxy, not direct: the same Huh7 RNA sequenced on PacBio Kinnex, ONT PCR-cDNA and Illumina gives the first linked short- versus long-read comparison on identical samples, but each value pools several callers (six long-read callers, three short-read callers for Illumina), so it compares platforms with unequal caller pools, not workflows a user would run.

Update the matching entry in `coverage.json` `judgements` to `proxy`.

D3. Configuration locators. Each `attributes.source_locator` currently cites `Run_GFSLGF.sh header and RunJAFFAL.sh` for every caller. Set them to:
- `rna-fusion-longread-20261011-config-ctat-lr-fusion`: `Methods 'Reference genomes', 'Fusion caller configuration'; repository Fusions/runtools/RunCTAT-LR-fusion.sh header`
- `rna-fusion-longread-20261011-config-gfseeker`: `Methods 'Reference genomes', 'Fusion caller configuration'; repository Fusions/runtools/RunGFSeeker.sh`
- `rna-fusion-longread-20261011-config-fusionseeker`, `-config-genion`, `-config-longgf`: `Methods 'Reference genomes', 'Fusion caller configuration'; repository Fusions/runtools/Run_GFSLGF.sh header (caller versions, min_read_supp=2)`
- `rna-fusion-longread-20261011-config-jaffal`: `Methods 'Reference genomes', 'Fusion caller configuration'; repository Fusions/runtools/RunJAFFAL.sh`

D4. Add this limitation to the `limitations` of protocol `rna-fusion-longread-20261011-protocol-sgnex-k562` and of claim `use-case-mapping-rna-fusion-longread-20261011-sgnex-k562`:
> CTAT-LR-Fusion has no K562 PCR-cDNA rows at 7.5 or 10 Gb, and no caller has K562 direct-RNA rows above 2.5 Gb or direct-cDNA rows above 5 Gb; the source does not say why.

D5. Add this limitation to protocols `rna-fusion-longread-20261011-protocol-sgnex-k562` and `-protocol-sgnex-mcf7`, and to claims `use-case-mapping-rna-fusion-longread-20261011-sgnex-k562` and `-sgnex-mcf7`:
> knownnumber is the number of distinct call records the authors' script labels known (grouped by gene pair, chromosomes and fusion type); the script does not deduplicate them to listed fusions, so it is an upper bound on the number of listed fusions recovered.

No numeric value changes.

## Corrections applied

Applied by the extractor in the extraction scripts (`extract/`), as the reviewer specified, before the batch was added to the store; then `extract/apply_review.py` recorded the review on every record.

1. D1: duplicate JAFFAL method removed; the JAFFAL configuration links to rna-fusion-20261009-method-jaffa.
2. D2: Huh7 judgement set to proxy with the reviewer's rationale and description.
3. D3: configuration source locators set per caller.
4. D4: K562 missing-rows limitation added to the K562 protocol and judgement.
5. D5: knownnumber upper-bound limitation added to the K562 and MCF7 protocols and judgements.

## Records after correction

- claim: 4
- configuration: 9
- dataset: 3
- evaluation: 21
- method: 4
- protocol: 4
- result: 597
- source: 2
