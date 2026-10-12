# Review: lit-cells-networks-20261011-scmbench, 2026-10-12

Source: SCMBench, Nature Communications 2026, Supplementary Data 2.

Reviewer: Claude review agent `reviewer-cn-2`, independent of the extractor `lit-cells-networks`. No human review claimed. Source transcription is not reproduction.

## Reviewer's report (verbatim)

The reviewer reported on this batch together with `lit-cells-networks-20261011-perturbench-v4` and `lit-cells-networks-20261011-chen2026`. The common sections and this batch's corrections and answers follow, unchanged.

# Independent review: PerturBench v4, Chen 2026 and SCMBench batches

Reviewer: Claude review agent (reviewer-cn-2), independent of the collector; no human review claimed.
Date: 2026-10-12. Worktree reviewed: /Users/timrichardson/Documents/projects/personal/blog/rewire-benchmark-data-lit-cells-networks
(batch folders treated as the source of truth; no record was edited and nothing was committed).

## Verdicts

- `data/omics/lit-cells-networks-20261011-perturbench-v4` (340 results): approved with corrections P1 to P7.
- `data/omics/lit-cells-networks-20261011-chen2026` (378 results): approved with corrections C1 to C7.
- `data/omics/lit-cells-networks-20261011-scmbench` (241 results): approved with corrections S1 to S5.
- New metric concepts in `data/vocab/metric.ttl`: approved, with one definition change (P7).
- Use-case summaries: no summary text was proposed for either use case these batches touch, so none is approved. No use-case field change is approved; no exclusion or input change is needed (the Jiang24 scope issue is handled as a limitation, P5).

No printed value, numeric value, uncertainty value or cell locator is wrong in any of the three batches. The corrections concern one configuration mapping, metric qualifiers, evidence concerns and judgement wording.

## Corrections

### SCMBench

S1. Source `lit-cells-networks-20261011-scmbench-source-sd2`, first evidence concern: replace `message` with "Sheet 'unpaired_inte_overall' has no header for column H. Each H cell is the formula =AVERAGE(Bn:Gn), the mean of the dataset cells with values. Rows with a blank Yao cell (bindSC, scMoMaT, scGPT_zero, Pamona, scFoundation, Geneformer) average five datasets and the other rows six, so column H values are not comparable across all rows." Set its review_date to 2026-10-12. Keep the locator and hash.

S2. Add to `attributes.evidence_concerns` of source `lit-cells-networks-20261011-scmbench-source-sd2`:
- source_id: `lit-cells-networks-20261011-scmbench-source-sd2`
- message: "In sheet 'paired_inte_overall' the scGPT row is scored on 10x-Multiome-Pbmc10k only; its Overall cell G20 (=AVERAGE(B20:F20)) is that single value, not a five-dataset mean, so it is not comparable with the other Overall values."
- source_locator: "Supplementary Data 2, sheet 'paired_inte_overall', cell G20"
- artifact_sha256: `77582bcc906fed343de12c2b2ed7443e94f5d11bf93b7f3862a37c5099015443`
- review_date: 2026-10-12

S3. Metric qualifiers on the seven partial across-dataset means (currently "mean of MAP, NMI, ASW and ARI; mean across datasets"):
- `lit-cells-networks-20261011-scmbench-result-paired-paired-overall-scgpt`: "mean of MAP, NMI, ASW and ARI; across-dataset mean over 10x-Multiome-Pbmc10k only"
- `lit-cells-networks-20261011-scmbench-result-unpaired-unpaired-overall-bindsc`, `-unpaired-unpaired-overall-scmomat`, `-unpaired-unpaired-overall-scgpt-zero`, `-unpaired-unpaired-overall-pamona`, `-unpaired-unpaired-overall-scfoundation`, `-unpaired-unpaired-overall-geneformer`: "mean of MAP, NMI, ASW and ARI; mean across the five Muto-2021 batches (Yao not scored)"

S4. The Methods tie the 2,500-cell sampling to the batch-effect experiments ("which are used for experiments investigating batch effects"). They do not say the per-batch integration-accuracy sheets use the sampled batches.
- In the descriptions of the eight dataset subsets `lit-cells-networks-20261011-scmbench-data-ma-2020-batch-53`, `-54`, `-55` and `-data-muto-2021-batch-1` to `-5`: replace "2,500 sampled cells)" with "the Methods sample each batch to 2,500 cells for the batch-effect experiments and do not say whether this sheet uses the sampled batches)".
- In all 241 evaluations: replace `comparison.split` "All cells (2,500-cell samples for batch splits)" with "Per dataset or batch as in Supplementary Data 2; whether batch splits use the 2,500-cell samples is not stated".

S5. The collector's report gives 545 records for this batch; `batch.jsonl` has 544 (241 results, 241 evaluations, 25 configurations, 18 methods, 13 dataset subsets, 3 sources, 2 protocols, 1 benchmark). Correct the report.

## Answers to the collector's questions

SCMBench
- Unlabelled column H: resolved. The cells are `=AVERAGE(Bn:Gn)` formulas, so H is the across-dataset mean. The concern stays because the means cover different numbers of datasets (S1 to S3).
- FM-scVI: concern approved as written. The Fig. 2 legend gives scGPT on PBMC-10k and adapted UCE on Ma-2020 for dataset results, and "the best-performing foundation model ... which varies across datasets" for overall results.
- printed_value for General-format cells: approved. It is the shortest 15-significant-digit form of the stored double, with `raw_xml_value` kept, which is the store's existing convention ("Canonical stored-number transcription of a General-format cell", 37 stored results).
- Paired 'scGPT' mode: unstated in the sheet; the configuration correctly says so. Blank cells are correctly skipped: the Yao sheet marks scMoMaT and Pamona as OOM, bindSC is blank, the article says UCE is the only foundation model that handled Yao, and paired scGPT is blank on the three mouse datasets.
- Origin: `independent_paper` approved, FM-scVI `author_reported`. No SCMBench author (Wang, Fan, ..., Gao, King, Li) is an author of the 19 domain-specific methods or the four foundation models, as far as the author lists show.

## Checks run and outcomes

Sources. I re-downloaded every artifact with curl and hashed it with shasum.

| Source | URL | SHA-256 | Match |
| --- | --- | --- | --- |
| perturbench-v4 source-wu2025 | https://arxiv.org/html/2408.10609v4 | b73f2644b129ca209b69812ad467d595e15c283f6cae5c3c9bbc5a4c5870996a | Yes |
| (reference only) PerturBench v4 PDF | https://arxiv.org/pdf/2408.10609v4 | 5922c95d24526b5b078887bdf2181e354ab3ddf05fd943c55041af1bea6caf96 | Yes, matches sources.md |
| chen2026 source-chen2026 | https://arxiv.org/pdf/2607.17227v2 | 8137338c6146f570a6546f30707d4244baca9dab848b32c51539665a5ba539da | Yes; archived .gz 1dd08b0d... decompresses to the same hash |
| scmbench source-article | Europe PMC PMC13342640 fullTextXML | 7aa2dbf1fc26bd602bf26e52c1061f91358a1c6cb389f57edc0ebfb0edc64f57 | Yes; archived .gz matches |
| scmbench source-sd2 | Springer MOESM4 xlsx | 77582bcc906fed343de12c2b2ed7443e94f5d11bf93b7f3862a37c5099015443 | Yes; archived .gz matches |
| scmbench source-sd1 | Springer MOESM3 xlsx | 7287a457b1e856742a90043e96dc57b667210b28a8228d4d9a6de5d7156ecfb9 | Yes; archived .gz matches |

Full automated comparison with my own parsers, not the collector's scripts:
- PerturBench: BeautifulSoup parse of the HTML `ltx_table` grids for Tables 2 to 13 (369 cells, 29 '-'). 340 of 340 results match the printed cell, numeric value and decimal standard deviation (n = 5), and each maps to exactly one cell. No cell missed, no duplicate.
- Chen: my own regex parse of `pdftotext -layout`, with model blocks assigned from the printed order and labels asserted where they share a line. 378 of 378 printed and numeric values match. No cell missed, no duplicate.
- SCMBench: openpyxl cached values plus my own read of the sheet XML. 241 of 241 match on raw XML string, numeric value and 15-significant-digit printed value. Row and column labels in every locator match. 39 Overall or column H cells are formulas (AVERAGE). I spot-checked per-dataset cells against the per-metric sheets (GLUE PBMC-10k, 0.676475 = mean of 0.8364, 0.8039, 0.5997, 0.4659). The article's printed overall scores (GLUE 0.599; Seurat4, scJoint and scMDC on PBMC-10k 0.7952, 0.7671 and 0.7391) agree with the sheet.

Stratified hand checks against the rendered table:
- PerturBench: 48 values, 4 per table from Tables 2 to 13, checked by eye against the v4 PDF rendering (pdftotext -layout of the reference PDF). They cover every model family, including Biolord*, GEARS-adjacent Norman rows, SAMS-VAE* (S), LA, Linear, DecoderOnly and the matrix distances. All match.
- Chen: rendered PDF pages 46 to 48 (Tables 2 to 5 and S2) as images and checked by eye. 45 values cover every table and all six models: all Table 2 Nicheformer and GenePT-w rows, the Table 3 spatial rows across the page break, every Table 4 block including Novae SEAAD, the Table 5 GenePT-w and scELMo rows, and all of S2. All match, including the model block assignment around the Table 3 page break and the Table 4 labels between rows.
- SCMBench: 40 values (20 per sheet, random with a fixed seed) checked against the cell grid. All match, including the column H value for FM-scVI.

Mapping checks:
- Metric, qualifier, direction and unit were checked for every metric column. Wrong: C1, C2, C3 and S3. Units follow the store (PerturBench v1 units; unitless for Chen and SCMBench).
- Uncertainty is on PerturBench only and correct. Chen and SCMBench print no spread; `missing_metadata` says so correctly.
- Dataset, split and protocol links were checked for every result: each table maps to the right protocol and subset. Wrong: S4.
- Configuration mapping: one error (P1).

Duplicates:
- No batch ID exists on origin/main (bba147c, 54,592 IDs). Every external link target exists there.
- No other open branch (`claude/lit-20261011-*`, local and remote) or worktree (`../rewire-benchmark-data-lit-*`) holds these sources or the new model families (Nicheformer, CellPLM, scGPT-spatial, Novae).
- The store has GenePT and scELMo papers (`genept-2024`, `scelmo-2025`) and a GenePT-w configuration, but no GenePT or scELMo model record, so the new model records are not duplicates.
- PerturBench v1 is a separate source in the store; v4 is a new source with new protocols. That is correct, because the runs differ.
- None of the five new metric concepts respells an existing one (`scib-asw-label` is the rescaled ASW; there is no MMD, matrix distance or transposed-rank concept). No other branch or worktree adds them.

Relevance judgements:
- For all 10 judgements (3 PerturBench, 7 Chen), `reviewed_evaluations` equals the set of evaluations on the protocol. No `excluded_evaluations` were needed.
- `proxy` is justified for all 10, given corrections P3 to P6, C5 and C6.
- Not mapping the PerturBench chemical protocols (Srivatsan20, OP3) or the SCMBench integration protocols is correct. `use-case-phenotype-perturbation-selection` excludes transcriptome similarity alone, and no use case covers multi-omics integration.

Use-case summary: none proposed by the collector; nothing to approve. The existing summaries do not cite these batches and remain accurate. Optional evidence-gap wording for the integrator, not required: replace "PerturBench combination-prediction results are in the store as task records and need a protocol before they can be judged for this use case." with "PerturBench v1 combination-prediction results remain task records without a protocol; the PerturBench v4 reruns (arXiv v4, Tables 3 and 6) are judged as a separate protocol and are not combined with v1."

Other: `claims.csv` agrees with `batch.jsonl` (record IDs, printed values and locators) for all three batches. No batch has a `derivation`, so no recomputation was needed.

Not run: `npm test`, `npm run typecheck` and `npm run build`. I edited no records; those runs belong to the apply step after the corrections. No external API received an email or personal identifier.

## Corrections applied

Applied by the extractor in the `extract/` scripts, as the reviewer specified, before the batch was added to the store.

1. S1: the first evidence concern on `lit-cells-networks-20261011-scmbench-source-sd2` has the reviewer's message and review date 2026-10-12; locator and hash unchanged.
2. S2: the reviewer's paired scGPT evidence concern is on the source.
3. S3: the seven partial across-dataset means carry the reviewer's qualifiers.
4. S4: the eight per-batch dataset subsets and all 241 evaluations carry the reviewer's sampling wording.
5. S5: the pass report gives 544 records for this batch.
6. Every record is `source_checked`; each result's and claim's `review` block names the reviewer and keeps the extraction note.

## Records after correction

- benchmark: 1
- configuration: 25
- dataset_subset: 13
- evaluation: 241
- method: 18
- protocol: 2
- result: 241
- source: 3
