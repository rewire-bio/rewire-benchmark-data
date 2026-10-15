# Research notes

Batch for rewire-benchmark-data issue #129 (genomic foundation model guide fixes): add a model record for GPN-MSA, which had configurations in the store but no model, and extract any coding-variant evaluation the GPN-MSA paper prints as numbers.

## Decisions

- Source: bioRxiv v2 (2024-04-06) of the GPN-MSA paper. The Nature Biotechnology version (2025) is paywalled and its ablation table (Extended Data Table 1) is an image, so the preprint PDF text layer was used. Values may differ from the journal version; the reviewer cannot check that without journal access.
- The DOI in the issue, 10.1101/2023.10.10.562811, does not resolve. The preprint's DOI is 10.1101/2023.10.10.561776.
- Model: `gfm-guides-20261014-gpnmsa-model-gpn-msa`, entity level family, from the preprint and the official repository at commit dc5fd287. No `variant_of` link to the GPN model (`regulatory-variant-20261009-model-gpn`) was added: GPN-MSA uses a different input (a multispecies alignment) and the sources do not call it a variant of GPN. The store owner may decide otherwise.
- Coding-variant evaluation: the paper's ClinVar, COSMIC and DMS comparisons with CADD, phyloP, ESM-1b, Nucleotide Transformer and HyenaDNA are figure-only (Figure 2c-d, Supplementary Figures 3-5). The only printed numbers are Supplementary Table 4 (ablation study) and two DMS AUROCs quoted in the Results text. Both were extracted.
- Supplementary Table 4: the ClinVar, COSMIC and OMIM column groups (mean and max over three seeds) for all 17 rows. The gnomAD column group (odds ratio) was not extracted because `data/vocab/metric.ttl` has no odds-ratio concept and this batch may not add vocabulary.
- Ablation rows are configurations of the new GPN-MSA model, except 'MSA frequency (no neural net)' and 'Combined phyloP and phastCons', which are new method records (they are scores, not GPN-MSA models). Origin is author_reported for GPN-MSA rows and MSA frequency (the authors' own baseline) and independent_paper for the phyloP and phastCons combination and for ESM-1b.
- The ESM-1b DMS TADBP value (0.75) uses the GPN-MSA paper as its source, so it is in this batch; `gfm-guides-20261014-esm1b` does not repeat the source.

## Existing configurations that should get `configuration_of` to the new model

These GPN-MSA configurations currently have `configuration_of` to `regulatory-variant-20261009-model-gpn` (the GPN family). The store owner should repoint them to `gfm-guides-20261014-gpnmsa-model-gpn-msa` through a reviewed `records -- change`:

- `lit-genomics-20261011-guanine-config-gpn-msa-mode-unprinted`
- `lit-genomics-20261011-guanine-config-gpn-msa-position-zs`
- `lit-genomics-20261011-guanine-config-gpn-msa-zs`
- `lit-genomics-20261011-traitgym-config-gpn-msa-absllr-plus-score`
- `lit-genomics-20261011-traitgym-config-gpn-msa-embeddings-minus-inner-product`
- `lit-genomics-20261011-traitgym-config-gpn-msa-embeddings-plus-cosine-distance`
- `lit-genomics-20261011-traitgym-config-gpn-msa-embeddings-plus-euclidean-distance`
- `lit-genomics-20261011-traitgym-config-gpn-msa-innerproduct-minus-score`
- `lit-genomics-20261011-traitgym-config-gpn-msa-llr-minus-score`
- `lit-genomics-20261011-traitgym-config-gpn-msa-logisticregression-chrom`

Not included: the TraitGym `GPN_final_*` configurations (GPN-Promoter, correctly on the GPN family) and the ensemble configurations that are `configuration_of` their own method records (`...-cadd-plus-gpn-msa-logisticregression-chrom`, `...-cadd-plus-gpn-msa-plus-borzoi-logisticregression-chrom`, `...-gpn-msa-plus-borzoi-logisticregression-chrom`). Their methods (`lit-genomics-20261011-traitgym-method-*gpn-msa*`) could take a `uses_model` link to the new model if the owner wants the dependency visible.

Possibly the same data: the official doc lists `songlab/clinvar` (missense variants with pathogenic or benign labels) as a GPN-MSA evaluation set. The store's `lit-genomics-20261011-gfmbench-data-songlab-clinvar` may be built from it. Not linked, because neither source states the versions match.

## Record counts

- benchmark: 1
- claim: 1
- configuration: 17 (15 ablation settings, GPN-MSA main results model, ESM-1b precomputed scores)
- dataset: 4
- evaluation: 53
- method: 2
- model: 1
- protocol: 4
- result: 104
- source: 3

Reused IDs: `uc20260930-model-esm-1b` (target of the ESM-1b configuration). Every record has status `needs_review`.

## Extraction note for the reviewer

Tables and passages extracted:

1. Supplementary Table 4 (PDF page 23), "Ablation study": 17 rows by the ClinVar (AUROC), COSMIC (AUPRC) and OMIM (AUPRC) column groups, each with 'mean' and 'max' over three seeds: 102 results. Method: deterministic parse of the `pdftotext -layout` text of the pinned PDF (`extract/build_gpnmsa.py`), with column groups, the mean/max header, the 17 row labels and the page asserted. Printed values are the strings in the text layer (three decimals).
2. Results, DMS paragraph (PDF page 6): "TADBP, for which GPN-MSA AUROC is 0.83, while ESM-1b AUROC is 0.75": 2 results. Method: transcription, sentence asserted verbatim by the script.
3. Repository README and docs/models/gpn-msa.md: model metadata and one claim (deprecated in favour of GPN-Star; inference only). Method: transcription.

Gaps:

- Figure 2c-f, Supplementary Figures 3, 4 and 5 (ClinVar, COSMIC, OMIM, gnomAD and DMS comparisons with CADD, phyloP, phastCons, ESM-1b, NT, HyenaDNA, Enformer, SpliceAI): figure-only, not read.
- Supplementary Table 4 gnomAD column group (odds ratio, mean and max): no metric concept for odds ratio. 34 cells not extracted. Adding an `odds-ratio` concept to `data/vocab/metric.ttl`, with its STATO match, would allow it.
- Supplementary Tables 1 and 2 (held-out accuracy): language-model metrics, out of scope for this task.
- Nature Biotechnology version: paywalled text; Extended Data Table 1 is an image. Not compared with the preprint.
- Variant counts for the ClinVar, COSMIC and OMIM sets are not printed; dataset sizes are unreported.
- The labelled datasets on Hugging Face (songlab/clinvar, cosmic, omim, gnomad) were not retrieved.

Needs reviewer judgement:

- Supplementary Table 4's caption says ClinVar, COSMIC, OMIM and gnomAD use "same setting as Figure 2a/2b/2c/2d", but in v2 those settings are Figure 2c-2f (the same off-by-two appears in Supplementary Figure 3's caption). The protocols follow the Methods "Main VEP metrics" definitions. Recorded in the source's limitations rather than as an evidence concern, since the values themselves are not in doubt.
- Whether the 'Default' ablation row and the main-results model are the same model as the released checkpoint `songlab/gpn-msa-sapiens`. The preprint does not say; they are separate configurations here and neither is tied to the checkpoint.
- For the two non-neural rows (MSA frequency, combined phyloP and phastCons), seeds do not apply; mean and max are printed and equal. Both are kept as printed.
- The training-data statement on the model ("89 non-human species in the default model") comes from the Figure 2a caption and Methods; check that it describes the released checkpoint.
