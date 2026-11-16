# GPN-Star (Ye et al. 2026), batch gpn-star-20261116

Extraction for the first part of rewire-bio/rewire-benchmark-data issue #226. Lane: genomics.
Search cutoff 2026-11-16. Extractor: Claude extraction agent; no human review claimed. Review is
a separate pass and has not been done.

Frozen extraction hash: `batch.jsonl` sha256
`0c92c46582ae5d2f4df77b4fe90669c205998a7b981dba113924943558843836` (219 records, 493,308 bytes).
`extract/build.py` sha256 `9a3e3eae3fa4cb5d502bd61b9b93d5837b6efb503871e710e05192b057dd3fc0`.

Every record has `status` `source_checked`, which is the store's convention for a record
transcribed from a pinned source. It is the extractor's statement that the value came from the
artifact, not a review sign-off; each record's `review` block names the extraction method and says
sign-off is left to review-evidence.

## The version pinned, and why it is not the one the issue names

The issue names bioRxiv 2025.09.21.677619. That preprint has been published:

> Ye, C., Benegas, G., Albors, C., Li, J. C., Prillo, S., Fields, P. D., Clarke, B. and Song, Y. S.
> **Predicting genome-wide functional constraints with GPN-Star.** *Nature* **659**, 141-150
> (5 November 2026). doi:10.1038/s41586-026-11005-5. Received 2025-09-10, accepted 2026-08-07,
> published online 2026-09-09. Open access, CC BY 4.0.

The title changed between the two versions. The bioRxiv API still lists one version (v1, posted
2025-09-21) with `published: "NA"`, so the preprint record does not point at the journal version;
the link was found in the store instead (see below). This batch pins the version of record and its
Supplementary Information, and pins the preprint only so the version history is recorded. No value
in the batch comes from the preprint.

Artifacts (all re-downloaded once in the same session; the two publisher PDFs reproduced their
hashes byte for byte, so they are stable):

| Source record | Artifact | sha256 |
| --- | --- | --- |
| `gpn-star-20261116-source-nature-2026` | Nature article PDF, 26 pages | `d7dfe801bad2a0a23478753147af2320bc31c8b37ee50d66f1a1af8385e9005d` |
| `gpn-star-20261116-source-nature-si` | Supplementary Information PDF (MOESM1), 57 pages | `3f7e8f71710bb63ec5ff032e697b6ef85f0d6d74411a31865fed73a757c7fc9e` |
| `gpn-star-20261116-source-biorxiv-v1` | bioRxiv v1 PDF, 68 pages | `ec829bce7b9192a6a396f29d4ab90ac5de6c4903232bdf9328eb1c53e626af7a` |
| `gpn-star-20261116-source-hf-collection` | Hugging Face collection API JSON | `4e8141d673c18e6ab131eba8e1cbef7f29aa4403d5a4864218b06b90d07b275d` |

The artifacts are not archived in the batch folder: the two publisher PDFs are 16 MB and 8 MB, are
open access at stable URLs and re-download to the same bytes. Copies used for the extraction are at
`/private/tmp/claude-501/-Users-timrichardson-Documents-projects-personal-blog/2b3e629e-c97e-4855-9278-c3793c720747/scratchpad/gpnstar/`
as `nature.pdf`, `moesm1.pdf`, `paper.pdf` (the preprint) and `hf.json`, with the `pdftotext -layout`
text layers beside them as `nature.txt` and `moesm1.txt`. That folder is session scratch, so re-download
rather than rely on it.

## A stored source record points at the same article with a different hash

`vep-uc-20261014-source-gpn-star` (added by the 2026-10-14 VEP use-case pass) is already a record of
this article: same URL and DOI, named "Ye et al. 2026, Nature (publisher PDF)", with
`version` "Nature accelerated article preview PDF ('Published online: xx xx xxxx'; accepted
2026-08-07)" and `artifact_sha256`
`97f61ec05d4ace41692549290db3faf019ce869459459d2c5694bf54e16d0996`. That URL now serves the final
version of record, whose bytes differ. The stored hash is not wrong, it pins the accelerated preview,
but it no longer matches a fresh download.

This batch therefore adds a new source record for the version of record with a `supersedes` link to
the stored one, rather than editing the stored record. Two checks were made before adding the link.
The store already does this for a source: `lit-protein-20261011-prime-source-prime2026` supersedes
`prime-2026` and `evidence-expansion-prime-2026-f6aac4c2`, accepted in the 2026-10-11 protein
structure review with the old records left unedited. And `publicRecords` in
`scripts/omics/schema.ts` withholds a record only for linking to an `excluded` or `disputed`
record, so a `supersedes` edge to a `source_checked` record hides nothing. **Reviewer ruling still
wanted:** is `supersedes` the right edge between an accelerated preview and the version of record
of the same article, or should the two sit side by side with no edge?

## What is extractable, and what is not

The paper's headline comparisons are plots. Figs. 2 and 3, Fig. 4a, c and d, Extended Data Figs.
1-10 and Supplementary Figs. 1-27 print no values; the figure files are raster images, so even the
axis ticks are mostly absent from the PDF text layer. Nature publishes no Source Data files for this
article, so none of those panels can be recomputed from the source's own rows under
docs/collection.md "Values computed from source data". The authors do publish their benchmark
datasets and precomputed scores on Hugging Face, but computing AUPRC from them would be a Rewire
run, not an extraction, and the paper states no aggregation that could be applied to them as a
derivation. All of this is recorded as a gap.

Three places print numbers, and all three are extracted in full:

1. **Supplementary Information, Supplementary Table 3 (ablation studies), PDF page 23.** 8 settings
   x 7 benchmarks = 56 cells, each printed as `mean (max)` over three random initializations. This
   is the paper's only printed table of performance values, and it does not exist in the preprint.
2. **Article Fig. 4b, PDF page 7.** 12 printed bar labels: the genome-wide odds ratio for the
   enrichment of gnomAD singletons over common variants in each score's deleterious tail. These are
   printed numeric labels in the PDF text layer, not values read off a bar.
3. **Article Results, PDF page 5.** The four rare variant association gene counts (402 versus 383
   discovered; 353 versus 338 replicated).

Record counts: 4 source, 1 benchmark, 6 dataset, 10 protocol, 39 configuration, 3 method,
72 evaluation, 72 result, 12 claim. Total 219.

## Reused identities

| Reused record | Used for | Why it is the same thing |
| --- | --- | --- |
| `vep-uc-20261014-model-gpn-star` | the model every GPN-Star configuration and claim attaches to | the discovered record the issue names; no second GPN-Star model record was created |
| `gfm-guides-20261014-gpnmsa-model-gpn-msa` | the two GPN-MSA ablation configurations and the Fig. 4b GPN-MSA configuration | same model |
| `somatic-oncogenicity-20261009-method-phylop` | three Fig. 4b phyloP configurations | same method |
| `somatic-oncogenicity-20261009-method-phastcons` | three Fig. 4b phastCons configurations | same method |
| `somatic-oncogenicity-20261009-method-cadd` | the Fig. 4b CADD v1.7 configuration | same method |
| `gfm-guides-20261014-gpnmsa-data-cosmic-frequent-vs-gnomad-common-missense` | the COSMIC ablation column | the Supplementary Information says the COSMIC data were "processed by ref. [22]", the GPN-MSA paper, with the same MutantCensus v98 >0.1% positives and gnomAD common missense controls the stored record describes |
| `lit-genomics-20261011-traitgym-data-mendelian-traits-matched-9` | the OMIM ablation column | "downloaded processed Mendelian traits dataset from TraitGym", with nine controls per positive matched on chromosome, consequence and distance to the TSS, which is what the stored record describes |
| `lit-genomics-20261011-traitgym-data-complex-traits-matched-9` | the fine-mapped non-coding ablation column | "downloaded processed complex traits dataset from TraitGym", nine matched controls, matching also on LD score and MAF |

Not reused, and why:

- **TraitGym protocols.** The store holds `lit-genomics-20261011-traitgym-protocol-*-zero-shot` and
  `-linear-probing` (AUPRC by chromosome, weighted average, Hugging Face revision 1fde19555fe8),
  `lit-genomics-20261011-gfmbench-protocol-traitgym-*` and `ag-atlas-20261019-protocol-traitgym-*`
  (AUPRC after the AlphaGenome Atlas positional filtering). GPN-Star computes a plain AUPRC over the
  whole set, restricted to variants every compared model scores, so the split and the metric
  implementation differ from all of them. New protocols were created.
- **GPN-MSA ablation protocols.** `gfm-guides-20261014-gpnmsa-protocol-ablation-clinvar-auroc`,
  `-cosmic-auprc`, `-omim-auprc` and `-gnomad-odds-ratio` are the same shape of table from the
  sibling paper, but the ClinVar metric there is AUROC against gnomAD common controls, while
  GPN-Star reports AUPRC against ClinVar benign controls on an earlier ClinVar release. New
  protocols and a new ClinVar dataset were created.
- **GPN-MSA ablation configurations.** The GPN-MSA paper's own ablations
  (`gfm-guides-20261014-gpnmsa-config-ablation-*`) are different models from the two GPN-MSA rows in
  GPN-Star's Supplementary Table 3, which the GPN-Star authors retrained on their own dataset and
  hyperparameters. New configurations were created, each linked `configuration_of` the stored
  GPN-MSA model.
- **Precomputed-score configurations of other papers.** `gfm-guide-20261014-config-evee-gpn-msa` and
  `lu-hetero-20261019-config-gpn-msa-precomputed` are other papers' setups of the same precomputed
  GPN-MSA scores. A new configuration was created for this paper's use of them.

Duplicate identities already in the store, noticed while reusing: phastCons has two method records
(`somatic-oncogenicity-20261009-method-phastcons` and `lit-genomics-20261011-traitgym-method-phastcons`),
Evo 2 has two model records (`catalog-model-evo-2`, `discovery-model-evo-2`) and Nucleotide
Transformer has three (`catalog-model-nt-v2`, `discovery-model-nucleotide-transformer`,
`lit-genomics-20261011-guanine-model-nucleotide-transformer-v3`). This batch uses the
somatic-oncogenicity phastCons record and does not touch Evo 2 or Nucleotide Transformer, which it
has no values for. The duplicates are flagged here, not changed.

## Decisions and their reasons

**Coding and non-coding are separate protocols.** Supplementary Table 3 prints them as separate
columns over separate datasets: "Finemapped coding" (MAF-matched controls) and "Finemapped
non-coding" (TraitGym complex traits, nine matched controls). ClinVar, COSMIC and ProteinGym are
missense; OMIM and HGMD are regulatory. Seven columns, seven protocols, six datasets plus the
reused COSMIC one.

**Checkpoints.** Supplementary Table 1 names 19 training setups: nine human models (vertebrate,
mammal and primate x 25M, 85M and 200M) and ten for the five other species. Each is a configuration
record with its alignment, chromosome split, clade threshold, clade count, context size, learning
rate, step count and training time. The Hugging Face collection listed eight released model
repositories on 2026-11-16, so not every setup is released, and the paper does not map setup names
to repository ids; the collection listing is a claim, and no configuration asserts a repository id.

**No result is attached to a named checkpoint.** The Supplementary Table 3 results belong to
ablation models the authors trained for that table (25M parameters, multiz100way with training
interval curation); they are not the released checkpoints, and the table says so. Fig. 4b and the
RVAT paragraph name their models only as GPN-Star (V), (M) and (P). The paper says elsewhere that it
focuses on the 200M models, but no figure or sentence ties a figure value to a checkpoint, so the
Fig. 4b systems are separate configurations with `missing_metadata.checkpoint` unreported, and the
RVAT method record carries the same gap on `checkpoint_revision`.

**Supplementary Table 3 cells are one result each.** The cell prints `0.896 (0.897)`: the mean over
three random initializations outside the parentheses and the maximum inside. Each result holds
`printed_value` the mean, the whole cell in `printed_source_cell`, and the maximum in
`source_statistic`.

Two results per cell was built and measured, because the GPN-MSA batch stores its mean and its
maximum as separate results. It was reverted: `scripts/omics/batch.py check-values` matches a
result's printed value against whole cells of the text-layer table, so the 56 extra maxima came
back as 51 `not_in_row` and 8 `overclaimed_in_row`, against no failures at all for one result per
cell. That is the checker's error state, not a soft flag, and 59 false failures would bury a real
mismatch. The GPN-MSA table prints its mean and its maximum in separate columns, so the split that
works there does not work here. **Reviewer ruling wanted:** keep one result per cell, or take the
59 flagged rows to make the maxima queryable?

A related wording point: the stored GPN-MSA results say "mean over three random seeds; zero-shot"
and these say "mean over three random initializations; zero-shot", because that is this caption's
wording. Aligning them would not make the two tables automatically comparable, since their
evaluation comparison fields differ, so the source's own wording was kept.

**Supplementary Tables 5-8 are not results.** They give the count, proportion and odds ratio of each
Ensembl consequence class among the top 0.1% most constrained variants by GPN-Star (P), and two
tables of consequences enriched in GPN-Star (P) against GPN-Star (M) and (V). They characterise what
one model prioritises rather than measuring it against a ground truth, and two of them compare the
model to itself. The numbers the main text quotes (missense 33% and 170-fold, dELS 26% and 2.4-fold,
dELS-flank 8% and 0.35-fold, P versus M missense 1.14-fold, P versus V missense 1.52-fold and
synonymous 3.89-fold) are recorded in the claim
`gpn-star-20261116-claim-prioritized-variant-consequences`; the full tables are left unextracted.
**Reviewer ruling needed:** should these four tables become evaluations on a consequence-enrichment
protocol? The parse is cheap to add; the question is whether they belong in the results graph.

**RVAT numbers are results.** 402 versus 383 discovered genes and 353 versus 338 replicated genes
are printed in the Results, with a stated protocol (DeepRVAT 1.1, 34 UK Biobank quantitative traits,
161,822 unrelated individuals of European ancestry, MAF < 0.1%, family-wise error rate < 0.05, three
seeds). The system is not GPN-Star: it is DeepRVAT with GPN-Star annotations, a new method record
linked `uses_model` to the GPN-Star model, against a new DeepRVAT method record. The contract says
`uses_model` does not assign the result to the base model, which is the intended reading here.
One caveat is in the evaluation and result records: the paper says "on average across runs" of the
comparison and does not separately say whether the original DeepRVAT counts are also means over
three runs.

**Facets.** `clinical_research` is kept only on the records about human disease variants: the three
versions of the paper, the benchmark suite, and the ClinVar, HGMD, fine-mapped coding and OMIM
datasets and protocols. The ablation configurations, the conservation tracks, the gnomAD frequency
data, the UK Biobank cohort and the ten non-human training setups carry `research` only. `areas` is
`dna-genomes` throughout.

**Near-duplicates with other groups' stored results.** None of the 72 values duplicates a stored
result. The closest are the GPN-MSA paper's own ablation table (same shape, different metric on
ClinVar, different ClinVar release, different models) and the TraitGym metrics already stored for
GPN and GPN-MSA (same underlying datasets, different protocol: by-chromosome weighted average versus
plain AUPRC over variants all compared models score). The paper's headline figures would have
overlapped more, but they print no values. Nothing was added that is a near-duplicate of a stored
number without a separate protocol.

**Differences between the preprint and the version of record**, found while checking the version:

- The preprint's Methods say the ClinVar metric is AUROC; its own Fig. 2 caption and Results say
  AUPRC. The version of record says AUPRC in all three places. The published reading is used.
- The preprint's Fig. 2 caption says 66 and 84 UK Biobank traits where its Results say 65 and 83.
  The version of record says 65 and 83 throughout.
- The preprint says the hg38 assembly is "3.1Bbp"; the version of record says "3.1Gbp".
- The version of record adds Supplementary Table 3 (ablation studies), the only printed performance
  table, and renumbers the supplementary tables.

These are version differences, not errors in the stored data, so no evidence concern was written.
They are listed in the preprint source record's `limitations`.

## Recommended changes to the stored discovered record

Not made here. For the reviewer to apply with `npm run records -- change` if the new claims are
accepted. Record `vep-uc-20261014-model-gpn-star`:

- `status`: `discovered` to `source_checked`, once the results in this batch are checked.
- `version`: currently absent with `missing_metadata.version` "unreported". The version of record
  still names no model release, but it names the code release (gpn v0.8, Zenodo
  doi:10.5281/zenodo.21501177) and the checkpoint naming scheme. Either leave the missing reason or
  set it from `gpn-star-20261116-claim-software-version`.
- `access`: currently "Code at https://github.com/songlab-cal/gpn; models on Hugging Face (Data and
  code availability)". Could name the collection
  `https://huggingface.co/collections/songlab/gpn-star-68c0c055acc2ee51d5c4f129` and the precomputed
  predictions at doi:10.57967/hf/9849, from `gpn-star-20261116-claim-access`.
- `licence`: currently "Not stated for the model in the captured source". Still true for the
  weights; the code is MIT (`gpn-star-20261116-claim-licence`).
- `training_data`: currently "Whole-genome alignments with species trees at vertebrate, mammal and
  primate timescales (Abstract)". Could name multiz100way, cactus447way restricted to 447 mammals
  and to 243 primates, with chromosomes 1-20, X and Y for training, 21 for validation and 22 held
  out, from `gpn-star-20261116-claim-training-data`.
- `source_ids`: add `gpn-star-20261116-source-nature-2026`, which supersedes the preview PDF the
  record cites.
- links: the record has none. `family` or `variant_of` edges to GPN and GPN-MSA would need a sourced
  association claim; the Supplementary Information's "Key differences between GPN-MSA and GPN-Star"
  section would support one.

## Gaps

1. Figs. 2 and 3, Fig. 4a, c and d, Fig. 5b-d, Extended Data Figs. 1-10 and Supplementary Figs.
   1-27 print no values. The paper's comparisons against CADD, GPN-MSA, Evo 2 (7B and 40B), Nucleotide Transformer
   2.5B, ESM-1b, Enformer, Borzoi, AlphaGenome, AlphaMissense, PrimateAI-3D, PromoterAI, SpeciesLM,
   GPN-Promoter, PhyloP and PhastCons on ClinVar, COSMIC, ProteinGym, OMIM, HGMD, the fine-mapped
   UK Biobank sets and the promoter subsets are therefore not in the store from this source.
2. No Source Data files are published, so no derivation is available for those panels.
3. The S-LDSC heritability analyses (Fig. 3, Extended Data Figs. 2-4) print no values.
4. **Fig. 5a prints 15 bar labels and is still unextracted.** It gives the rare versus common
   enrichment odds ratio for GPN-Star, PhyloP and PhastCons in each of five non-human species
   The fifteen printed values, in text-layer order and deliberately not assigned to a species or a
   score here, are 38.7, 186.3, 440.8, 37.0, 29.1, 43.4, 88.9, 7.0, 5.5, 5.3, 4.0, 1.8, 3.1, 3.8
   and 2.7; the page also prints each panel's sample sizes. It was left out because, unlike
   Fig. 4b,
   the value labels do not sit beside their row label: assigning each of the 15 numbers to a
   species and a score means grouping them by horizontal position into five panels and then taking
   the within-panel bar order from the legend. That is an inference about the figure, not a reading
   of it. Extracting it would need 5 datasets, 5 protocols and 15 configurations for models the
   store has no other evidence for. See the reviewer questions.
5. Fig. 5b, c and d (mouse MMRdb, fly FlyBase lethal and worm lethal variant classification) print
   AUPRC bars with 95% confidence intervals but no values. The ten non-human training setups are
   registered as configurations with no results.
6. Supplementary Tables 5-8 are unextracted (see the ruling above).
7. Supplementary Table 2 (traits to tissues), Supplementary Table 4 (ENCODE SCREEN cCRE class
   definitions), Supplementary Table 9 (UCSC alignments) and Supplementary Table 11 (GTEx tissue
   groups) are reference tables, not results, and were not extracted.
8. Fig. 4c prints per-consequence sample sizes but no enrichment values, so the
   consequence-stratified version of the Fig. 4b protocol is unextracted.
9. Whether the GPN-Star scores behind Fig. 4b are the mutation-rate-calibrated ones is not stated in
   the figure or its caption. The Supplementary Fig. 20 caption says the uncalibrated raw scores
   were used there "for fair comparison", which implies the main figures use calibrated scores, but
   that is an inference and is not asserted in any record. It is noted in the Fig. 4b protocol's
   limitations.
10. The other four papers in issue #226 (GPN, the published GPN-MSA, PhyloGPN, TraitGym) were not
   searched or extracted.

## Questions for the reviewer

1. Is `supersedes` the right link from the version of record to the stored accelerated-preview
   source record, and should anything be noted on the stored record itself? The precedent and the
   `publicRecords` check are in the section above.
2. One result per `mean (max)` cell, as built, or two at the cost of 59 false value-check
   failures?
3. Should Supplementary Tables 5-8 become evaluations on a consequence-enrichment protocol?
4. Are the Fig. 4b printed bar labels acceptable as results? They are printed numbers in the PDF
   text layer, not values read off a bar, but they sit in a figure rather than a table.
5. Three Fig. 4b GPN-Star configurations exist alongside the nine human Supplementary Table 1
   training setups, because the figure names no checkpoint. Is that the right split, or should the
   figure results attach to the 200M setups on the strength of "we focus here on the largest
   models"?
6. The "MSA Transformer-like architecture" ablation row is a configuration of the GPN-Star model
   with a note saying it is an architecture ablation rather than the published MSA Transformer. Is
   that the right parent?
7. Reusing the two TraitGym dataset records pins a Hugging Face revision (1fde19555fe8) that
   GPN-Star does not name. Reuse and note, as done here, or create new dataset records?
8. Should Fig. 5a's 15 printed bar labels be extracted, given that assigning them needs the
   within-panel bar order from the legend rather than a label on the same line?
9. Should the recommended changes to `vep-uc-20261014-model-gpn-star` be applied in this pass?

## Reproducing the extraction

```sh
# the four artifacts, re-downloaded to a scratch folder
curl -sL -o nature.pdf https://www.nature.com/articles/s41586-026-11005-5.pdf
curl -sL -o moesm1.pdf "https://static-content.springer.com/esm/art%3A10.1038%2Fs41586-026-11005-5/MediaObjects/41586_2026_11005_MOESM1_ESM.pdf"
curl -sL -o paper.pdf https://www.biorxiv.org/content/biorxiv/early/2025/09/21/2025.09.21.677619.full.pdf
curl -s -o hf.json https://huggingface.co/api/collections/songlab/gpn-star-68c0c055acc2ee51d5c4f129

cd data/omics/gpn-star-20261116
python3 -I extract/build.py <dir>/nature.pdf <dir>/moesm1.pdf <dir>/paper.pdf <dir>/hf.json
```

`build.py` refuses to run unless every artifact hash matches, and asserts the table row labels, the
column headers, the cell counts, the Fig. 4b label set and every sentence a claim quotes. It
rewrites `batch.jsonl` byte for byte.

For the value check, pass the `pdftotext -layout` text layers (poppler 26.08.0), not the PDFs:

```sh
pdftotext -layout nature.pdf nature.txt && pdftotext -layout moesm1.pdf moesm1.txt
npm run -s batch -- check-values data/omics/gpn-star-20261116 \
  gpn-star-20261116-source-nature-2026=<dir>/nature.txt \
  gpn-star-20261116-source-nature-si=<dir>/moesm1.txt
```

Run by the extractor on 2026-11-16 and deleted again, since writing the receipt is the reviewer's
step: 12 `in_cell`, 44 `in_row`, 16 `locator_not_parsed`, and no `not_in_row`, `wrong_column` or
`overclaimed_in_row`. The 16 unparsed locators are the 12 Fig. 4b labels and the four RVAT prose
values, which name a figure or a paragraph rather than a table. The 44 `in_row` results are
Supplementary Table 3 cells whose column the checker cannot name, because the "Finemapped coding"
and "Finemapped non-coding" headers are printed over two lines; `build.py` asserts the column order
positionally instead, and the column assignment still needs the reviewer's sampled check.

`npm run records -- add` was not run: the batch is frozen for review (extract-evaluations step 7).
The additions were checked against the store with the same validators `records -- add` uses
(`validateVocabularies`, `validateAttributes`, `validateDescriptions`, `validateDerivations`,
`validateConcerns`, `validateRecords`): 219 new records validate against the 91,734 stored ones. The
SHACL subset check runs as part of `records -- add` and has not been run.
