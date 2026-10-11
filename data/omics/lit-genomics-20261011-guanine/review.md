# Review: lit-genomics-20261011-guanine, 2026-10-11

Reviewer: Claude review agent `reviewer-gen-3`, independent of the extractor `lit-genomics`. No human review claimed. Source transcription is not reproduction.

## Reviewer's report (verbatim)

guanine (lit-genomics-20261011-guanine): approved with corrections.
Checked: the archived XML's SHA-256 matches f6cc4294...3ef79. All 225 results compared by an independent <td> parse of Tables 2-4: every printed and numeric value matches. Column mapping is right (dnase-prop, ccre-prop, cons30, cons100, gpra-c, gpra-d). Eval mode (F/X/blank, giving ft/1pct/zs) matches the Eval column on every row, including the two PhyloGPN cadd-snv rows (zs 9.80, 1pct 23.60). No cell is left unrecorded. ENCFF180XQC "–" cells are omitted, which is right. No GUANinE records exist elsewhere in the store, so no duplicates. hgT5 and T5 as author_reported is right.
Recording the metric as Spearman x100 for cadd-snv and clinvar-snv is faithful to the printed "ρ". The values also behave like correlations, not AUROC: GC-content scores 1.47 and 11.53, near 0, where an AUROC would sit near 50.
Corrections:
1. Protocols lit-genomics-20261011-guanine-protocol-cadd-snv and -clinvar-snv: add a limitation. "ρ against a Boolean label is a rank correlation with a binary target; the source does not define it further; not comparable with AUROC or AUPRC on similar ClinVar tasks."
2. Origin: set config-sei-aggr-mode-unprinted and config-sei-aggr-plus-pangolin-mode-unprinted to author_reported. Sei-Aggr. is the authors' own scoring construction (Table 4 footnote; Discussion: "additively combining Pangolin and Sei-Aggr, the latter simplified to the zero-shot regime"). The same text supports changing their mode from "unprinted" to zero-shot. Optional, for consistency with DNALongBench's CNN: the authors' own non-neural baselines (GC-content, 5-mer LinSVR, 5-mer kNN) could also be author_reported.
3. ID slug: config-na-ve-conseq-type-mode-unprinted and config-na-ve-vep-115-conseq-1pct lost the "ï" in "Naïve". Rename to naive-* before release, while the IDs are still unpublished.
4. Locators: the two PhyloGPN cadd-snv results share the locator "Table 3, row 'PhyloGPN', column 'cadd-snv'". Add the Eval value (blank vs 'X') to each so they can be told apart.
Note, no change needed: the two Evo2_7B gpra-c/gpra-d results are null with printed "†" and missing_metadata reason "unavailable". The schema allows this. The "previously reported" (blue) cells cannot be identified from the XML, and the protocol limitations already say so.

## Corrections applied

Applied by the extractor in the extraction scripts (`extract/`), as the reviewer specified, before the batch was added to the store.

1. Protocols cadd-snv and clinvar-snv: limitation added that ρ against a Boolean label is a rank correlation with a binary target, not comparable with AUROC or AUPRC.
2. Origin author_reported for the Sei-Aggr. and Sei-Aggr. + Pangolin configurations (the authors' own scoring construction), now recorded as zero-shot; the authors' own non-neural baselines (GC-content, 5-mer LinSVR, 5-mer kNN) also set to author_reported.
3. IDs with the lost 'ï' renamed to naive-* (config-naive-conseq-type-mode-unprinted, config-naive-vep-115-conseq-1pct and their evaluations and results).
4. The two PhyloGPN cadd-snv locators now carry the Eval value (blank or 'X').

## Records after correction

- benchmark: 1
- configuration: 55
- dataset: 8
- evaluation: 225
- method: 8
- model: 8
- protocol: 8
- result: 225
- source: 1
