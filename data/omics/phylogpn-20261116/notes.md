# PhyloGPN, its own paper

Requested in issue #226 (rewire-bio/rewire-benchmark-data), fourth part: "PhyloGPN: the paper the
README cites". This batch extracts every printed cell of the two headline tables of that paper and
registers the configurations, protocol, data and descriptive facts behind them.

Extraction only. A different agent reviews it. No record is marked reproduced, and no review
sign-off is claimed.

## What the issue got wrong

Both claims in the issue's table row for PhyloGPN are wrong, and both were checked against the
store and the publisher rather than assumed:

1. "Own paper in the database: No (README and licence only)". The paper is in the store twice
   already: `phylogpn-2025` (status `discovered`) and `evidence-expansion-p2-phylogpn-2025-807f3a26cbfa`
   (status `source_checked`), both pointing at the same Europe PMC full text XML with the same hash.
   One result from its Table 1 is already stored as `b2-phylogpn-2025` (see "The legacy duplicate").
   No third source record was created for those bytes; every result in this batch cites
   `phylogpn-2025`.
2. The paper is published. The songlab-cal/gpn README cites it as a Springer chapter, and Crossref
   and the publisher page agree: Albors C., Li J.C., Benegas G., Ye C., Song Y.S., *A Phylogenetic
   Approach to Genomic Language Modeling*, Research in Computational Molecular Biology (RECOMB
   2025), Lecture Notes in Computer Science (LNBI) volume 15647, pages 99-117, first online
   25 April 2025, doi 10.1007/978-3-031-90252-9_7. The text of the version of record is paywalled,
   so nothing was extracted from it; a source record pins the publisher page and a claim records the
   version of record against `phylogpn-2025`.

Note for the coordinator: this is the mirror image of the GPN-Star case. There the stored record
said preprint and the work had been published with a changed title; here the issue said the paper
was missing and unpublished, and it is neither.

## Sources

| Record | Artifact | SHA-256 | Reproduced today |
| --- | --- | --- | --- |
| `phylogpn-2025` (reused) | Europe PMC full text XML of PMC11908359, the arXiv:2503.03773v1 preprint | `807f3a26cbfa9b5ce238d92164bd523302c67d1c5794b08273c51cca1acd4224` | Yes, byte for byte |
| `evidence-reported-phylogpn-2025-readme-md` (reused) | songlab-cal/gpn README at commit 6f28c81 | `0312fb9646aef630a30cd3039337b31a48f4345f4dd1cdd71edcc483afd8b9d0` | Yes, byte for byte |
| `phylogpn-20261116-source-supplement` (new) | Supplement 1 PDF, `NIHPP2503.03773v1-supplement-1.pdf` | `b4885d288e03ae976acafb2b6b1c3837572dce224c8803715f4d329966ba65f4` | Yes, in two retrievals |
| `phylogpn-20261116-source-springer-chapter` (new) | Springer chapter page for the version of record | `31d3954fe7909256c70099ca0153500b1ab4c72314208e825dbd298276d4f0e7` | No, see below |

Hash findings, which the brief asked to be explicit about:

- The stored hash of `phylogpn-2025` reproduces exactly. The warning about an October pin no longer
  matching its live URL does not apply to this source. Nothing stored was edited.
- The supplement is only served as a zip (`.../PMC11908359/supplementaryFiles`). The zip is **not**
  byte-stable: two retrievals on 2026-11-16 gave different bytes, because the archive carries
  per-download timestamps. The member PDF was byte-identical in both, so the source record pins the
  PDF's hash and `hash_scope` says why.
- The direct PMC path for the supplement (`.../articles/instance/11908359/bin/NIHPP2503.03773v1-supplement-1.pdf`)
  returns an HTML error page, not the PDF.
- The Springer page is mutable: two retrievals on 2026-11-16 differed in bytes. Its hash describes
  one retrieval and is recorded as such. No value comes from it.
- Both primary artifacts are archived gzipped in `artifacts/` (the preprint licence, CC BY-NC-ND
  4.0, allows unadapted noncommercial copying). The Springer page is not archived.

Europe PMC search is a trap here and cost a few minutes: `"A Phylogenetic Approach to Genomic
Language Modeling"`, `TITLE:"..."` and `DOI:"10.1007/978-3-031-90252-9_7"` each return
`hitCount: 0`, although PMC11908359 exists and its full text XML serves from the same API. Resolve
this paper by PMC ID or Crossref, not by an Europe PMC search.

## What was extracted

| Table | Cells | Records |
| --- | --- | --- |
| Table 1, ClinVar classification from log likelihood ratios, AUROC | 12 classes x 5 models = 60 | 60 evaluations, 60 results |
| Table 2, BEND tasks from embeddings | 10 rows x 7 tasks = 70, of which 6 print `N/A` | 64 evaluations, 64 results |

The six `N/A` cells (GPN-MSA on Chromatin Accessibility, and GPN-MSA (LLR) on the five
classification tasks) are not recorded. `extract/parse_tables.py` asserts their count, so a changed
table stops the parse.

Record counts: 2 sources, 13 configurations, 1 dataset, 12 dataset subsets, 1 protocol,
124 evaluations, 124 results, 10 claims. 287 records.

## Existing IDs reused

- Model: `lit-genomics-20261011-guanine-model-phylogpn`. No second PhyloGPN model record was
  created. Both new PhyloGPN configurations link to it with `configuration_of`.
- Comparator families: `discovery-model-nucleotide-transformer`,
  `regulatory-variant-20261009-model-hyenadna`, `regulatory-variant-20261009-model-caduceus`,
  `regulatory-variant-20261009-model-gena-lm`, `gfm-guides-20261014-gpnmsa-model-gpn-msa`.
- BEND tasks as the `assessment` of every Table 2 evaluation: `bend-task-gene-finding`,
  `bend-task-enhancer`, `bend-task-chromatin`, `bend-task-histone`, `bend-task-cpg`,
  `bend-task-variant-expression`, `bend-task-variant-disease`. Their printed metrics match the
  Table 2 column headers (MCC, AUPRC, AUROC) exactly.
- BEND data subsets as the `data` of every Table 2 evaluation: `bend-dataset-gencode`,
  `bend-dataset-fulco-2019-gasperini-2019-and-enformer-enhancer-set`,
  `bend-dataset-encode-chromatin-accessibility`, `bend-dataset-encode-histone-modification`,
  `bend-dataset-encode-cpg-methylation`, `bend-dataset-deepsea-expression-variants`,
  `bend-dataset-clinvar-disease-variants`.
- Expert methods of the Table 2 "Expert Method" row, as the `system` of those seven evaluations:
  `bend-method-augustus` (Gene Finding), `bend-method-enformer` (Enhancer Annotation),
  `bend-method-basset` (Chromatin Accessibility, Histone Modification, CpG Methylation),
  `bend-method-deepsea` (Expression VEP, Disease VEP). These are the same records the BEND paper's
  own evaluations use, and the printed values match the stored BEND values cell for cell.

New configurations were created rather than reusing other papers' configurations for the same
checkpoints (for example `lit-genomics-20261011-geneb-config-hyenadna-medium-160k-seqlen-hf`),
because the store's practice is one configuration per paper per evaluated setup: the same checkpoint
scored by a different rule is a different setup. `lu-hetero-20261019-config-gpn-msa-precomputed`
beside `gfm-guide-20261014-config-evee-gpn-msa` is the precedent.

## Decisions a reader should be able to check

**Checkpoints.** Appendix A.2, in the supplement and not in the body, is the only place that names
the comparator checkpoints: `nucleotide-transformer-v2-500m-multi-species` (the 2.5B multi-species
model was also evaluated and did slightly worse on likelihood tasks), `hyenadna-medium-160k-seqlen-hf`,
`caduceus-ps_seqlen-131k_d_model-256_n_layer-16`, and GPN-MSA from the published precomputed hg38
score set. Each has its own configuration record citing the supplement. PhyloGPN's own weights are
published at `songlab/phylogpn` with no revision stated, so `version` and `checkpoint_revision` are
`missing_metadata`, not a guess. Results stay with these paper-scoped configurations; nothing is
attached to a named released checkpoint revision.

**PhyloGPN-X is not a model.** It is the same weights with embeddings pooled over 5,521 positions
through a fixed random map (l = 2,760, 6,001 bp effective receptive field). It is a second
configuration of the same family record, not a new model.

**Caduceus appears twice.** Table 1 uses the checkpoint A.2 names. Section 4.2 says the Table 2
Caduceus row is "the largest RCE Caduceus model" and does not say it is that same checkpoint, so
there are two configuration records and the second carries a `model_identity_note` saying exactly
that. Merging them is a reviewer ruling, not an extractor's.

**Origin differs by Table 2 row.** Section 4.2: the authors reproduce Marin et al.'s numbers and add
"our own evaluation of PhyloGPN, PhyloGPN-X, and the largest RCE Caduceus model", plus GPN-MSA by
Appendix A.3. So PhyloGPN, PhyloGPN-X, Caduceus, GPN-MSA and GPN-MSA (LLR) are `author_reported`;
DNABERT, GENA-LM, HyenaDNA, Nucleotide Transformer and the Expert Method row are
`paper_compilation`, and those evaluations carry a limitation saying the measurement is not this
paper's.

**Table 1 GPN-MSA is author_reported, not unreported.** The body lists only Nucleotide Transformer,
HyenaDNA and Caduceus as benchmarked, which reads as if the GPN-MSA column came from elsewhere, but
Appendix A.2 states plainly: "we evaluated GPN-MSA using pre-computed LLR values". The authors ran
it; the scores they fed in were published ones.

**Family-best rows.** The Table 2 caption says "We report the best result among models in each
family", so the DNABERT, GENA-LM, HyenaDNA and Nucleotide Transformer rows are not single-model
results. Each has a `*-family-best` configuration, each evaluation's `comparison.aggregation` is
"Best result among the models of this family", and each result's `metric_qualifier` ends with the
same phrase, so these cannot compare automatically against single-model results. The member that
produced each value is not printed and was not inferred.

The DNABERT family-best configuration is deliberately left with no `configuration_of` link. BEND
scored DNABERT and DNABERT-2, the printed row mixes them (Gene Finding 0.43 is DNABERT-2's stored
value, Chromatin Accessibility 0.85 and Expression VEP 0.60 are DNABERT v1's), and the store holds
DNABERT and DNABERT-2 as separate family records, so attaching the row to either would misstate it.
The GENA-LM, HyenaDNA and Nucleotide Transformer rows do link to their family records, whose
members BEND evaluated under one family.

**GPN-MSA (LLR) is kept apart from the embedding rows.** It scores the two VEP tasks by allele
likelihood ratio, so its `comparison.inputs` and `adaptation` and its `metric_qualifier` say so. It
shares the task and the data subset with the embedding rows, which is correct, but it will not
compare as though the inputs were identical.

**Asterisks.** `0.50*` (PhyloGPN Gene Finding and Expression VEP) and `0.01*` (PhyloGPN-X Enhancer
Annotation) keep the asterisk in `printed_value`; `numeric_value` drops it. Those three results
carry the caption's own wording in `source_warnings`.

**A misprint worth a ruling.** Appendix A.3 says the GPN-MSA alignment "was constructed using the
hg39 human reference genome". No assembly called hg39 exists and GPN-MSA is built on hg38, so this
reads as a typo. It is quoted in the GPN-MSA BEND configuration's limitations and nothing was
inferred from it.

## GUANinE: no comparison is possible

The paper does not mention GUANinE. The string appears zero times in the full text XML. The nine
stored GUANinE results for PhyloGPN
(`lit-genomics-20261011-guanine-result-phylogpn-*`: cons30, cons100, ccre-propensity,
dnase-propensity, gpra-c, gpra-d, cadd-snv zero-shot, cadd-snv 1% eval, clinvar-snv) come from the
GUANinE benchmark paper, a different source, and there is no cell to compare against and no
protocol to compare. They stand untouched. No correction claim was written, because there is no
disagreement to record.

One consistency check worth noting: the stored GUANinE configuration
`lit-genomics-20261011-guanine-config-phylogpn-1pct` records a context column of "= 481", which
matches the 481 bp receptive field this paper states in Methods. The GUANinE extraction and the
paper agree on the one model property both report.

The issue's count of stored PhyloGPN results is also low. Besides the nine GUANinE results the store
holds 14 PhyloGPN per-class ClinVar AUROCs from `lu-hetero-20261019` and the one legacy Table 1
value, 24 in total.

## Cross-source checks against the store, for the reviewer to rule on

These are leads, not corrections. Every printed value in this batch stands as printed.

1. **Two Table 2 family-best cells are not the maximum of the BEND values we store.** The other 26
   compiled cells are. Recorded in `source_discrepancy` on the two results:
   - GENA-LM, Chromatin Accessibility: printed 0.84; stored BEND values are GENA-LM BERT 0.76 and
     GENA-LM BigBird 0.82.
   - Nucleotide Transformer, Expression VEP: printed 0.54, which is the stored NT-MS value, while
     the stored NT-H value is 0.55.

   Either the authors read a different BEND release, or our BEND extraction differs, or the
   family-best rule was applied loosely. Our BEND source is the ICLR 2024 proceedings PDF
   (`evidence-expansion-bend-final-f709b6be`).
2. **Table 1 disagrees with `lu-hetero-20261019` on overlapping ClinVar classes**, in the same
   direction every time (this paper higher):

   | Class | This paper (Table 1) | Lu et al. 2025 (stored) |
   | --- | --- | --- |
   | 5' UTR | 0.94 | 0.601 |
   | 3' UTR | 0.94 | 0.765 |
   | Start codon / start loss | 0.77 | 0.583 |
   | Stop lost | 0.81 | 0.695 |
   | Intronic / intron non-splice | 0.95 | 0.846 |
   | Splice acceptor, splice donor / splice | 0.82, 0.83 | 0.722 |
   | Synonymous | 0.85 | 0.806 |
   | Missense | 0.84 | 0.799 |
   | Noncoding | 0.94 | 0.951 |

   The protocols are not the same: Lu et al. used ClinVar `variant_summary` 2025-03-31 with MANE
   RefSeq v1.4, restricted to variants every compared model scored, and ran PhyloGPN from its
   official example code; this paper used an unnamed ClinVar release filtered to at least one review
   star and scored from the stationary distribution of the predicted substitution model. Class
   definitions also differ (this paper's "Noncoding" is not Lu's "Noncoding"). The knowledge-graph
   discrepancy build will probably flag these; the reviewer should check its `outlier_results` for
   this batch.

## The legacy duplicate

`b2-phylogpn-2025` already holds Table 1, 3' UTR, PhyloGPN = 0.94, the same cell and the same value
as the new `phylogpn-20261116-result-t1-utr3-phylogpn`. The legacy record hangs off
`reported-model-cbbe04b826ceff` (a configuration named PhyloGPN with no link to the family record),
`reported-task-ed3dd3b83c4505` (whose own attributes say "structured extraction pending") and
`reported-dataset-a28180d33f7a23`, all `needs_review`. Its `metric_direction` is `unknown`, which is
wrong for AUROC; the new records use `higher`.

Nothing was linked to those legacy records and no `supersedes` link was added: retiring the legacy
silo is a ruling about four existing records, which belongs to review. Recommendation, for the
reviewer to take or reject in one step: add `supersedes` from
`phylogpn-20261116-result-t1-utr3-phylogpn` to `b2-phylogpn-2025`, set the legacy result's status to
`superseded`, and leave the legacy task, dataset and configuration alone or fold them into an
identity candidate. The alternative is to keep both results and record the duplication; they do not
disagree, so nothing is blocked either way.

The duplicate source records (`phylogpn-2025` and
`evidence-expansion-p2-phylogpn-2025-807f3a26cbfa`, same URL and same hash) are a second, smaller
case of the same thing. Not acted on.

## Gaps

- **Version of record not read.** The Springer chapter text is paywalled; only the abstract and the
  metadata are public. The preprint and the chapter were therefore not compared, so a table that
  changed between them would not be visible here. Anyone with institutional access can settle it in
  one read.
- **Table S1, deep mutational scanning Spearman correlations, 31 experiments over 25 proteins x 5
  models = 155 printed cells.** Not extracted, to keep this batch to the headline tables. It is in
  the pinned supplement (`phylogpn-20261116-source-supplement`), locator "Appendix A.4, Table S1",
  with asterisks marking data from Giacomelli et al. 2018 and negative values present. Extracting it
  would turn Figure 4 from a gap into data and is one follow-up batch.
- **Table S2, ablation study, 12 ClinVar classes x 2 models = 24 printed cells.** Not extracted. The
  two systems are an epoch-one PhyloGPN checkpoint and a model trained from scratch for two epochs
  on odd-numbered chromosomes and X, evaluated on the complement. Neither is a released checkpoint,
  so extracting it means two more configurations and a second protocol (evaluated on Subset 2 only,
  not comparable with Table 1). Locator "Appendix A.4, Table S2".
- **Figures with no printed numbers**, recorded as gaps and not read by eye: Figure 3a (ClinVar ROC
  curves), Figure 3b (AUPRC against MAF threshold for the OMIM regulatory test set, 409
  disease-causing variants against gnomAD negative sets), Figure 4 (DMS, summarised by Table S1),
  Figure 5 and Figure S1 (gene-finding confusion matrices), Figure 6 (ablation, summarised by
  Table S2). The OMIM comparison in Figure 3b has no printed values anywhere in the paper, so it is
  a true gap rather than a deferred table.
- **Printed values in prose, not extracted** (they are off-table and each needs its own protocol, so
  they are listed rather than recorded): PhyloGPN LLRs on the BEND Expression VEP variants reach
  AUROC 0.55 and Nucleotide Transformer 0.36 (Results, Embedding Evaluation, paragraph 6); PhyloGPN-X
  reaches AUPRC 0.03 on Enhancer Annotation when the BEND classifier's hidden size is raised from 2
  to 32 (paragraph 5). Both are quotable with the locators given.
- **No use-case judgements and no `coverage.json`.** The brief scoped this batch to steps 1 to 8 of
  the extraction skill and did not ask for use-case work. The Table 1 ClinVar protocol is a
  candidate for the variant interpretation use cases named in issue #226 (#222, #223, #224) and
  would need one judgement claim per protocol.
- **No vocabulary proposal.** Every metric, unit, origin, method type, area, context, review method,
  agent and missingness value used here already exists: `auroc`, `auprc`,
  `matthews-correlation-coefficient`, `unitless`, `author_reported`, `paper_compilation`,
  `foundation_model`.

## Questions for the reviewer

1. The legacy duplicate: supersede `b2-phylogpn-2025` with the new result, or keep both? The
   recommendation above is a single ruling.
2. Two claims are `needs_review` because they propose filling fields on the stored source record
   `phylogpn-2025`, which this batch must not edit:
   `phylogpn-20261116-claim-preprint-licence` (`attributes.licence` = CC BY-NC-ND 4.0, printed in the
   PMC permissions statement) and `phylogpn-20261116-claim-version-of-record`
   (`attributes.version_note`, the RECOMB 2025 chapter). Apply them with `records -- change` or
   leave them as claims?
3. Should `phylogpn-2025` keep `publication_status: preprint`? The artifact is the preprint, so the
   field is right for what it describes, and a reader looking for the published version now finds it
   through the new Springer source record and the claim. A reviewer may prefer the stored record to
   point at the chapter instead.
4. Caduceus: one configuration or two? The paper names a checkpoint for the likelihood-ratio
   evaluation and describes the BEND one only as the largest reverse-complement-equivariant model.
5. The DNABERT family-best configuration has no `configuration_of` link, for the reason above. If
   the reviewer prefers a link, which DNABERT family record should carry a row that mixes DNABERT
   and DNABERT-2?
6. The two BEND family-best cells that exceed our stored BEND maxima, and the Table 1 against
   Lu et al. disagreements: worth an upstream question, a discrepancy review, or neither?
7. Is Table S1 worth a follow-up batch? It is the only numeric record of the DMS comparison, and
   155 cells is a batch of its own.

## How to check this batch

```sh
python3 -I data/omics/phylogpn-20261116/extract/parse_tables.py \
  data/omics/phylogpn-20261116/artifacts/pmc11908359-fulltext.xml.gz \
  data/omics/phylogpn-20261116/extract/tables.json
python3 -I data/omics/phylogpn-20261116/extract/build_batch.py \
  data/omics/phylogpn-20261116/extract/tables.json data/omics/phylogpn-20261116/batch.jsonl
npx tsx data/omics/phylogpn-20261116/extract/validate_batch.ts
gunzip -c data/omics/phylogpn-20261116/artifacts/pmc11908359-fulltext.xml.gz > /tmp/phylogpn.xml
npm run -s batch -- check-values data/omics/phylogpn-20261116 phylogpn-2025=/tmp/phylogpn.xml
```

`parse_tables.py` asserts the artifact hash before parsing, so it fails rather than extracting from
a different retrieval. `build_batch.py` asserts 60 Table 1 results, 64 Table 2 results and one
system, assessment and data link per evaluation. The validator reported no problems over all 287
records. `check-values` reports `in_cell` for all 124 results, meaning every `source_locator`
resolved to the named row **and** the named column in the pinned XML; `value-check.tsv` holds the
per-result rows.

Extraction and the whole-batch value check were both run; what has not been done is an independent
re-reading of the cells by a second party, which is the reviewer's step.

## Frozen extraction hash

`batch.jsonl`, 287 records, SHA-256:

```
fbf8f6410ec0063a5e7beea4b0c8842052cafe5d26be31d70cbe9e341dce4903
```
