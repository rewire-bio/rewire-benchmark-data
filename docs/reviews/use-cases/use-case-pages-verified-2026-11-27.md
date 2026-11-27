# Verification fixes to the new use cases, 2026-11-27

Reviewer: `claude`, applying the independent verification by agent `verify-mappings` of batches
`use-case-mapping-gaps-20261127` and `use-case-pages-20261127` (verdicts in its `verdicts.jsonl`). The verifier re-checks what changed here. No
human scientific review.

A second verification pass untied two of the viral page's ties and corrected five sentences; see
[use-case-mapping-second-pass-2026-11-27.md](use-case-mapping-second-pass-2026-11-27.md). The table
below is as of this batch.

Batch: `data/omics/use-case-pages-verified-20261127/`. `extract/remove.py` removes the two held use
cases, `extract/ties.json` and `ties.py` name every tie change test by test, and `extract/texts.json`
and `texts.py` hold the corrected page text.

## What the verification found

82 of 266 judgements were not agreed (30.8 percent): none of the 12 in the first batch and 82 of the 254 in
the second (32.3 percent): 48 should have had a different grade, 19 should not have been tied, 15 could
not be judged from the records. It also listed false sentences on the pages, in this review's
predecessor and in the commit message.

## How the pattern ties happened

The links of batch `use-case-pages-20261127` were chosen by rules in `extract/links.json`: each rule
was a regular expression over protocol ids, usually a benchmark's prefix (for example every
`lit-genomics-20261011-genbench-protocol-*`), with one reason written per rule. I read a sample of the
names each rule matched, not every record, and the evaluation gates in the builder check whether a
test can carry a judgement, not whether it answers the question. So a benchmark's off-question tasks
(GenBench's expression, Hi-C and species tasks), its aggregate rows (means of rows also tied) and
GENEB's mixed-category scores came in with the rest, and a reason that held for most of a rule's
tests was copied onto all of them. One reason was not checked at all: "the splicing use cases hold
the same tasks" was untrue when written.

What would prevent it, for the brief of future mapping work:

1. Choose each tie by reading that test's record (name, description, data, metric, limitations); never
   select tests by pattern or by benchmark.
2. Write the reason for that test, from its own record, and quote the passage relied on.
3. Before tying, look for aggregate rows (a mean, macro, composite or "all" row of tests that are also
   tied) and for one evaluation that mixes categories; tie the parts or the whole, never both.
4. Check every factual sentence in a reason or a page by query against the store before writing it,
   including claims about other use cases, and recount every number after the ties are final.
5. Have a second reader before anything is committed as reviewed.

## Changes

| Change | Tests | Detail |
| --- | --- | --- |
| Use cases removed | 2 | `rna-sequence-property-prediction` and `gene-regulatory-network-inference`, with their 33 judgements, taken out of the store with their provenance (`removed.jsonl`). Never released, so there is nothing to withdraw |
| Ties withdrawn | 12 | Seven GenBench means of tied rows; GENEB full, 1-shot and 10-shot (categories mixed in one evaluation); the HyCell composite score; HyPLM's ten-split regression average. Status `excluded` with the reason, link removed |
| Regraded to direct | 13 | Splice-site tasks of GenBench, the Nucleotide Transformer benchmark and SegmentNT: the question names splice sites |
| Regraded to proxy | 13 | The 12 RhoFold+ CASP15 tests (one developer-chosen target each, best of five picked against the true structure); HyPLM HumanPPI (a pair of proteins, not a property of one) |
| Reason corrected | 1 | HyCell CD4 split against chemistry: measures batch leakage |
| Tie added | 1 | The Rewire FLIP2 rhodopsin run on protein representation, proxy |

The six off-question GenBench ties and the Drosophila enhancer-activity regrade were already made in
batch `use-case-pages-fixes-20261127`, before the verdicts arrived. Every verdict
was accepted. One note on the splice-site verdict: after Part A2 (batch `use-case-mapping-proxy-20261127`) the splicing
follow-up use case does link six Nucleotide Transformer splice-site tasks, as proxy; that does not
change this use case's grade, since the question here names splice sites.

### Why the two use cases are held, and what would make them publishable

- **RNA sequence properties.** 29 of its 32 judgements needed a different grade or could not be
  judged: Wang et al.'s family and type "classification" is cosine similarity of homologous against
  non-homologous pairs, not label prediction; its fitness Spearman is absolute, so a model ranking
  mutants backwards scores well; how fitness was binarised for MCC and AUC is not described; the
  RNAGym macro averages tied categories; and both studies score the same 31 RNAGym assays, so they
  are not independent. Publishable once a second fitness study on other assays (or mRNA properties
  from reviewed mRNABench or MIMIC evaluations) can be linked, with signed metrics.
- **Gene regulatory network inference.** One test with no comparison (every comparator copied from
  another paper), an assay the dataset record does not state (single-cell, pseudobulk or bulk), and a
  method the protocol says does not produce a curated network. Publishable once BEELINE's 54 protocols
  pass review (counted as one study) or geneRNIB's own leaderboard is recorded.

## Sentences corrected on the pages

Every reader-facing gap was rewritten without store vocabulary. In particular:

- Genomic: "DNA sequence model" for "DNA language model" (Enformer, BPNet and DeepSTARR are in the
  evidence); the baseline sentence now names GUANinE's 5-mer and GC-content baselines, GenBench's CNN
  and the raw-sequence probe; the BEND, DART-Eval and Gene-MTEB sentence states what holds each back;
  the GENEB housekeeping sentence is gone.
- RNA structure: the ordering rests on the RhoFold+ developers' table; per-target confidence is a gap;
  the two interface tests pool easy and hard.
- Single-cell integration: SCMBench is held by a source under review, not unreviewed; Kedzierska et al.
  include Harmony, scVI and highly variable gene selection.
- Protein function: the question no longer claims proteins "with no close annotated relative"; the
  splits state no identity cut, which is now a gap; the DGEB enzyme-class test set is 128 proteins.
- Protein representation: the output no longer promises throughput; the HyPLM sentence says 28 public
  checkpoints from 13 families with 12 systems compared here; the FLIP, PFMBench, TAPE and DeepProtein
  sentence is corrected; the Rewire FLIP2 run is described, with why the board does not compare it.
- Protein design: Scaffold-Lab is held by a source under review; 11 of Genie 3's 13 rows are versions
  with no model, so two models can be compared.
- Glycan: five systems, not four; most results carry a standard deviation over three seeds; the
  unsupported imbalance claim is gone; it is the GlycanGT developers' table, and GlycanAA beats
  GlycanGT on class accuracy (0.746 against 0.694).
- Viral and microbial classification (added in batch `use-case-pages-fixes-20261127`, not yet verified): the BLAST comparison reuses
  the best embedding result of the 33-class test, and plain wording for ViroBench and CAMI.

## Ties and boards, per use case

Counts by query on the store and `kb/board.py`. "At verification" is the state the verifier checked;
"before" is the state just before this batch, after the fixes batch. Boards use the grouping and
grades of `kb/board.py` on main.

| Use case | Ties at verification | Ties before | Ties now | Ranked at verification | Ranked now | Board now |
| --- | --- | --- | --- | --- | --- | --- |
| genomic-sequence-element-annotation | 121 | 115 | 105 (101 direct, 4 proxy) | 6 | 6 | 105 groups, 4 studies; Enformer 1 to 4, GENA-LM 1 to 3, Nucleotide Transformer 1 to 3 |
| rna-structure-prediction | 42 | 42 | 42 (30 direct, 12 proxy) | 2 | 2 | 42 groups, 2 studies; AlphaFold 3 and RhoFold+ 1 to 2, resting on the RhoFold+ table |
| single-cell-data-integration | 9 | 11 | 10 (3 direct, 7 proxy) | 0 | 2 | 111 groups, 2 studies; scGPT and Geneformer 1 to 2 |
| protein-representation-property-prediction | 17 | 17 | 17 (11 direct, 6 proxy) | 0 | 0 | 16 groups, 1 study |
| glycan-property-prediction | 21 | 21 | 21 direct | 0 | 0 | 21 groups, 1 study |
| protein-function-annotation | 6 | 6 | 6 direct | 0 | 0 | 6 groups, 1 study |
| protein-design-quality | 5 | 5 | 5 direct | 0 | 0 | 5 groups, 1 study |
| viral-microbial-sequence-classification | none | 6 | 6 (5 direct, 1 proxy) | none | 2 | 24 groups, 2 studies |
| rna-sequence-property-prediction | 32 | 32 | removed | 6 | removed | |
| gene-regulatory-network-inference | 1 | 1 | removed | 0 | removed | |

The store now holds 39 use cases, 25 of them with an ordering.

## Findings for the store

- **Rewire's local runs are recorded one system per source.** In the FLIP2 rhodopsin run each system's
  results cite its own audit source, so the board treats each system as a separate study and compares
  none of them. The same affects the rhodopsin use case.
- **MSAlign v1 and v2 count as two studies** on mass spectrum shortlisting (the verifier's finding), the
  same fault as BEELINE: one paper's two versions are two source records with no shared DOI.
- **Cell-type annotation's ranking** now rests on Wu et al. 2025 and the HyCell developer report; its
  page does not yet say so. Mass spectrum's output and setting text predate its newer ties; both are
  pinned, so changing them needs a re-review of its judgements.
