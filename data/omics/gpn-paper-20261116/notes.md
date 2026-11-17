# GPN paper extraction (issue #226)

Scope: the GPN model's own paper, "DNA language models are powerful predictors of genome-wide
variant effects". Lane `genomics`. Search cutoff 2026-11-16. Extraction only; a different agent
reviews this batch.

Frozen extraction hash: `batch.jsonl` sha256
`6d4b99a755d9bb72f6ecdd8b469ea4717d1a04e492761689581ae6fc2d7d48b0`.

## The finding that shapes the whole batch

**The paper prints no comparison table.** The published article has no `table-wrap` element at all,
asserted by `extract/parse_values.py`. The SI Appendix has three tables: S1 is the list of genome
assemblies, S2 is test perplexity for the authors' three models, S3 is the training
hyperparameters. Every comparison of GPN against phyloP, phastCons, abs(phyloP), LD Score and their
LD-weighted forms is a bar chart: Figures 5D, 6D and 6E of the article, and SI Appendix Figures S6,
S8, S9, S10, S11 and S12. The `pdftotext -layout` text layer of those figures carries axis ticks,
legends and the per-class variant counts in the Figure S9 subplot titles, and nothing else. No
comparator value is readable without reading pixels, so none is recorded. The same holds for the
contingency tables drawn in Figures 5C and 6C and for the confusion matrix in Figure 2B.

What that leaves is 23 printed values: the 6 cells of Table S2, and 17 values the body text prints
in prose. That is the whole of the paper's numeric content.

## Which version was pinned

**Checked first: the store holds no source record for this paper, and nothing here is a stale pin.**
Prompted by what the GPN-Star extractor found, `data/entities/sources.jsonl` (1,467 records) was
grepped for the DOI 10.1073/pnas.2311219120, the bioRxiv ID 2022.08.22.504706, PMC10622914, PMID
37883436, both the published and the preprint titles, and the author name. No hit. The only Benegas
sources in the store are the GPN-MSA preprint and the TraitGym Hugging Face metrics, and the only
songlab-cal/gpn sources are the repository README and the GPN-MSA model doc at two pinned commits.
So no existing record is being duplicated or contradicted here.

The publication was not taken from the bioRxiv API's `published` field. It was found by searching
Europe PMC on the title, which returned PMID 37883436 / PMC10622914 / DOI 10.1073/pnas.2311219120
as a separate indexed record from the preprint PPR534879; the API happened to agree. PubMed and
Europe PMC were then checked directly for a later version or an erratum: the article has one
version, no `commentCorrection` entry other than the "Preprint in" link to PPR534879, and no
erratum, so the pinned bytes are the version of record and have been since 2023-10-26.

Re-download reproducibility was confirmed for every hashed artifact: the PNAS JATS XML, the bioRxiv
v3 JATS XML and the SI Appendix PDF member each came back byte-identical on a second fetch. The one
unstable artifact is the Europe PMC `supplementaryFiles` zip, which is generated per request; that
is why the SI source pins the PDF member and records the zip as `artifact_retrieval_endpoint` with
both observed zip hashes in its `retrieval_note`. No `hash_scope` caveat is needed on any source in
this batch.

The published version exists: PNAS 120(44) e2311219120, 26 October 2023, DOI
10.1073/pnas.2311219120, PMC10622914. It is the primary source and every result is taken from it
(`gpn-paper-20261116-source-pnas-2023`, Europe PMC full text JATS XML, sha256 `8ff2184c...`), with
the SI Appendix PDF for Table S2 (`...-source-pnas-2023-si-appendix`, sha256 `e9ea2399...`).

bioRxiv 10.1101/2022.08.22.504706 has three versions. v1 (2022-08-23) is titled "DNA language
models are powerful **zero-shot** predictors of **non-coding** variant effects", v2 (2023-04-12)
"... zero-shot predictors of genome-wide variant effects", v3 (2023-08-04) carries the published
title. v3 is recorded as a companion source (`...-source-biorxiv-v3`, sha256 `4faeb24f...`) for
version history; no result is taken from it. The version list itself comes from the bioRxiv details
API (`...-source-biorxiv-version-list`).

**Values that differ between v3 and the published article.** One measurement, the positional
perplexity sentence:

| | bioRxiv v3 | published |
| --- | --- | --- |
| region | the whole test chromosome | a 1 Mb region of the test chromosome, 264 genes, 471 transcripts |
| splice acceptor | 1.03 | 1.03 |
| splice donor | 1.02 | 1.02 |
| start codon | 1.10 | 1.08 |
| CDS1 / CDS2 / CDS3 | not reported | 2.44 / 2.24 / 2.79 |
| stop codon | 2.81 | 2.8 |
| intergenic and intronic | 3.14 | 3.24 |
| significance | all Mann-Whitney p < 10^-239 | all Mann-Whitney P < 10^-17 |

This is a different measurement region, not a corrected value, so it is recorded as a claim
(`...-claim-preprint-value-difference`) on the positional perplexity protocol rather than as a
correction. Every other printed value in this batch appears verbatim in v3 as well; the parse
script asserts that for 5.5-fold, 10.3-fold, "less than 7.5-fold", 96%, 51%, 14.2%, r = 0.22,
r = 0.13, 3.13, 3.17, "8% and 9%" and 27%. The preprint's own SI Appendix was not retrieved, so its
Table S2 was not compared.

## Species and task scope: the paper is plant-only

The brief asked whether the pinned version covers human variant effects as well as a plant genome
model. It does not. Every evaluation in the paper, in all three preprint versions and in the
published article, is in *Arabidopsis thaliana*: held-out sequence modelling, gene region
classification from embeddings, in silico mutagenesis, 1001 Genomes rare against common enrichment
and AraGWAS hit enrichment. No human model is trained and no human variant is scored. This is
recorded as `...-claim-species-scope`, because the stored GPN family record carries 17 human results
from other groups and a reader could otherwise take the training description here as applying to
them.

The two benchmark records keep the species and task scopes apart:
`...-benchmark-athaliana-model-quality` for held-out sequence modelling and the embedding probe, and
`...-benchmark-athaliana-variant-effect` for the variant work. Nothing is pooled across them, and
the four perplexity protocols, the classification protocol and the three variant protocols are
separate records.

## Reused IDs

- `regulatory-variant-20261009-model-gpn`, the existing GPN family record. No second GPN model was
  created. All five configurations in this batch link to it with `configuration_of` and `family`.
- Nothing else in the store matched. There is no Arabidopsis variant effect dataset, benchmark or
  protocol, no 1001 Genomes record and no AraGWAS record. The only Arabidopsis records are the Feng
  promoter classification datasets and protocols (`amp-feng-20261007-*`), which are a different task
  on different data.

## Duplicate check against the stored GPN results

The 17 results already on the GPN family are all human: TraitGym complex and Mendelian traits
(13 results), Tang et al. 2025 CAGI5 HepG2 and K562 (2), and EVEE deconfounded SNV AUROC (1, and see
below). None of them uses a protocol this paper uses, and this paper evaluates nothing the stored
results evaluate. **No duplicate protocol was found.**

One thing the reviewer should look at while here, which this batch does not touch: the configuration
`gfm-guide-20261014-config-evee-gpn-msa` ("GPN-MSA hg38 scores, pre-computed (Pearce et al. 2026)")
is linked `configuration_of` to `regulatory-variant-20261009-model-gpn`, so a GPN-MSA result is
counted as a GPN result. GPN-MSA has its own model record,
`gfm-guides-20261014-gpnmsa-model-gpn-msa`. That looks like a pre-existing identity error. It is not
changed here because this batch may not edit stored records, and it is relevant to whoever is
extracting the published GPN-MSA paper.

## Configurations and how results were assigned to them

The paper trains four models and defines one derived score. None is tied to a released checkpoint:
the paper offers only training code at https://github.com/songlab-cal/gpn and names no checkpoint,
revision or hash, so `checkpoint` is missing with reason `unreported` on every configuration.

| Configuration | What it is |
| --- | --- |
| `...-config-gpn-brassicales-repeat-weight-0-1` | the main model, 8 Brassicales genomes, repeat loss weight 0.1 |
| `...-config-gpn-brassicales-repeat-weight-1` | same, repeat loss weight 1 |
| `...-config-gpn-brassicales-repeat-weight-0` | same, repeat loss weight 0 |
| `...-config-gpn-athaliana-single-species` | trained on *A. thaliana* alone, 12,000 steps |
| `...-config-gpn-x-ld` | GPN scores of the main model weighted by LD; `uses_model` the GPN family |

Results whose source text says only "GPN" are assigned to the repeat weight 0.1 configuration on the
strength of one sentence: "Consequently, we focus on this model throughout the remainder of the
paper unless otherwise specified" (Results, Training a Multispecies DNA Language Model). That
sentence is quoted in the configuration's `provenance_note`. This is the single most load-bearing
inference in the batch and the reviewer should rule on it.

GPN x LD is recorded as a configuration of the GPN model, not as a separate model, because the paper
defines it as a weighted sum over the same model's scores:
`GPNxLD_i = -sum_j |GPN_j| * r_ij^2` within a 100 kb radius. The formula is in `hyperparameters`,
not in `combination_rule`: the `rbs:CombinedConfiguration` shape targets subjects of
`combination_rule` and requires at least two `uses_model` links, which is for a configuration that
combines two systems' outputs, and this combines one model's scores with an LD matrix. For the same
reason it carries no `uses_model` link, which under the record contract would say its result does
not belong to GPN; `configuration_of` says it does, which is the intended reading.

## What was extracted, and how each value was checked

| Protocol | Results | Where the value is printed |
| --- | --- | --- |
| test perplexity, chromosome-wide | 4 | SI Appendix Table S2 (3) and Materials and Methods (1) |
| test perplexity, non-repeat regions | 4 | SI Appendix Table S2 (3) and Materials and Methods (1) |
| positional perplexity, Chr5:3.5-4.5 Mb | 8 | Results prose |
| gene region classification accuracy | 2 | Results prose |
| rare versus common odds ratio | 1 | Results prose |
| GWAS hit odds ratio | 1 | Results prose |
| repeat variants below the missense decile | 3 | Results prose |

`extract/validate_batch.ts` runs the repository's own validators over the batch, including the
attribute registry and concept keys, the description rules, the relation rules and link resolution
against the store, and reports no problems. `npm run -s batch -- check-values` over the batch gives
`in_cell` for all 6 Table S2 results and
`locator_not_parsed` for the 17 prose results, which the tool does not parse by design. The text
layer for the check is `data/omics/gpn-paper-20261116/extract/si-appendix.layout.txt`
(`pdftotext -layout`, poppler 26.08.0, sha256 `6ee1d0c9...`). The published-article artifact for the
check is the pinned JATS XML.

`review.method` says which route produced each record. `deterministic-table-parse` appears only on
the 6 Table S2 results and their 6 evaluations, which `extract/parse_values.py` parsed. Everything
else read off the SI text layer (the Table S1 assembly list, the two chromosome 5 subsets, the two
perplexity protocols, the model-quality benchmark) carries `transcription`, because it was read by
hand. One detail there: the text layer prints the assembly accessions with a space where the
accession has an underscore (`GCF 000001735.4`), and the underscore is restored in the dataset
record. That is the only change made to a printed string anywhere in this batch, and it is recorded
in the dataset's review note.

The prose values are not left unchecked. `extract/parse_values.py` asserts the **whole printed
sentence** for each of them against the pinned article, and asserts that each recorded value occurs
in its own sentence, so a changed sentence fails the parse instead of a number moving silently. It
also asserts Table S2's header and all three row labels, re-checks the SHA-256 of all three pinned
artifacts before reading them, and asserts that the article has no tables.

## Reviewer questions

1. **Main-model assignment.** Is "we focus on this model throughout the remainder of the paper unless
   otherwise specified" enough to put the 5.5-fold odds ratio, the 8 positional perplexities, the two
   classification accuracies and the GPN x LD score on the repeat weight 0.1 configuration? If not,
   they belong at family level.
2. **Single-species perplexity.** Materials and Methods prints "test perplexity of 3.13 (3.17 on
   nonrepeat regions)" without naming Table S2's columns. This batch puts those two values on the
   same two protocols as the Table S2 cells. That mapping is the extractor's reading, recorded in the
   evaluation's `limitations`.
3. **Which variant set the 10.3-fold covers.** Figure 6D is labelled n = 453,281 variants with
   whole-genome alignment and Figure 6E n = 510,462 for the full set. The sentence that prints
   10.3-fold, which points at Figure 6C, names neither. `denominator` is missing with reason
   `unreported` on both the protocol and the result.
4. **"Accuracy on CDS (96%)".** Whether the printed per-class quantity is recall or something else is
   not stated. Recorded as `accuracy` with the class in `metric_qualifier` and the ambiguity in the
   result's `scope_note`.
5. **"5.5-fold" and "10.3-fold" as odds ratios.** The body text calls them fold enrichments; the
   figure captions call the same quantities odds ratios computed with Fisher's exact test. They are
   recorded with metric `odds-ratio` and `printed_value` exactly as the text prints it, including the
   "-fold". Confirm that is the right reading.
6. **Correlation type.** "r = 0.22" and "r = 0.13" are recorded as claims, not results, because they
   measure agreement between two scores rather than a model's performance. The paper does not say
   whether r is Pearson or Spearman, and nothing was inferred.
7. **Direction on the repeat-variant share.** `metric_direction` is `lower` for the share of repeat
   variants scored below the missense first decile. That is only right on the authors' reading that
   repeat variants should not outrank missense variants; it is stated in the protocol's
   `limitations`.
8. **Licence.** The article and its SI are CC BY-NC-ND 4.0. The SI PDF is archived verbatim under
   `artifacts/`; the `pdftotext` text layer in `extract/` is a mechanical derivative kept so the parse
   can be rerun. Confirm that is acceptable, or drop the text layer and have the reviewer regenerate
   it from the archived PDF with the command recorded on the source.

## Gaps

1. Every per-method comparison value in the paper (Figures 5D, 6D, 6E; SI Appendix Figures S6, S8,
   S9, S10, S11, S12). Bar charts with no values in the text layer. This is the paper's whole
   model-versus-baseline story, and none of it is in the store. The only comparator figure the paper
   prints anywhere is the bound "less than 7.5-fold enrichment was observed for other methods",
   recorded as `...-claim-comparator-bound-gwas`.
2. The contingency table counts of Figures 5C and 6C, drawn as images.
3. The gene region confusion matrix of Figure 2B: 4 of the 6 per-class accuracies are only there.
4. The k-mer baseline for gene region classification is printed only as ranges over classes (k = 3:
   8% to 70%; k = 6: 15% to 67%), not per class, so it is a claim and not results.
5. The odds ratios of SI Appendix Figure S6C and S6D (repeat weight ablation on both variant
   protocols) and Figure S10 (single-species ablation on both variant protocols). The text says only
   that the intermediate repeat weight does slightly better and that the single-species model does
   worse.
6. The preprint's own SI Appendix was not retrieved; its Table S2 was not compared with the published
   one.
7. The typeset PNAS PDF was not retrievable (pnas.org 403, PMC proof-of-work page). If a later pass
   obtains it, its figures may be vector text and some of gap 1 may become extractable. That is the
   one route worth trying. Re-running the authors' code would be a `rewire_run`, not source data, and
   is out of scope for this batch.

## Not done

No use-case work. The pinned source is plant-only, so none of the variant interpretation use cases
in #222, #223 and #224 is in scope, and `use-case-plant-promoter-reporters` is a promoter design
decision, not variant effect prediction. No `coverage.json`, no relevance judgements and no summary
claim were written. Skipped step 9 of the skill (`test:fast`, `typecheck`, `build`) as the brief
directs; the coordinator runs those.
