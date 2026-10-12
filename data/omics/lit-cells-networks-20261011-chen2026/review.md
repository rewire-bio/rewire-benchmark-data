# Review: lit-cells-networks-20261011-chen2026, 2026-10-12

Source: Chen et al. 2026, harmonised single-cell and spatial foundation model benchmark (arXiv v2).

Reviewer: Claude review agent `reviewer-cn-2`, independent of the extractor `lit-cells-networks`. No human review claimed. Source transcription is not reproduction.

## Reviewer's report (verbatim)

The reviewer reported on this batch together with `lit-cells-networks-20261011-perturbench-v4` and `lit-cells-networks-20261011-scmbench`. The common sections and this batch's corrections and answers follow, unchanged.

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

### Chen 2026

C1. Metric qualifiers on the DE-gene results. The Methods ('Perturbation prediction', page 28) state "MSE and Pearson correlation restricted to the top 20 differentially expressed genes for each perturbation condition" and "Pearson Delta DE across the top 20 differentially expressed genes".
- The 24 results with qualifier "top differentially expressed genes (number not stated), predicted versus observed post-perturbation expression" (Table 5 'MSE DE' and 'Pearson DE'): new qualifier "top 20 differentially expressed genes per perturbation condition, predicted versus observed post-perturbation expression".
- The 12 results with qualifier "top differentially expressed genes (number not stated)" (Table 5 'Pearson Delta DE'): new qualifier "top 20 differentially expressed genes per perturbation condition".

C2. The 42 Table 4 results with metric `auprc` or `auroc` and qualifier "held-out test set; multiclass averaging not stated": new qualifier "held-out test set; macro-averaged over classes". The Methods ('Cell type annotation', page 25) say "macro-PR-AUC, and macro-ROC-AUC".

C3. The 42 Table 4 results with metric `precision` or `recall` and qualifier "held-out test set; averaging across classes not stated": new qualifier "held-out test set; described as global in the Methods, averaging not further defined". Add to `attributes.evidence_concerns` of source `lit-cells-networks-20261011-chen2026-source-chen2026`:
- source_id: `lit-cells-networks-20261011-chen2026-source-chen2026`
- message: "Table 4 precision and recall equal accuracy in all eight Nicheformer and CellPLM rows, as micro (global) averaging would give, but recall differs from accuracy in every scGPT-spatial, GenePT-w, scELMo and Novae row. The Methods call precision and recall 'global' without defining the averaging, so they may be averaged differently between models and should not be compared across models."
- source_locator: "Table 4, columns 'Accuracy', 'Precision' and 'Recall'; Methods 'Cell type annotation' (page 25)"
- artifact_sha256: `8137338c6146f570a6546f30707d4244baca9dab848b32c51539665a5ba539da`
- review_date: 2026-10-12

C4. Source `lit-cells-networks-20261011-chen2026-source-chen2026`, third `limitations` entry: replace with "Spatial dataset codes BC, MH and ME are not defined in the tables; the Figure 2 legend defines them as BC/HBCA1 (human breast cancer), MH/MHPC (mouse hippocampus) and ME/MOSTA E9.5 (mouse embryo)."

C5. The four annotation judgements (`use-case-mapping-lit-cells-networks-20261011-chen2026-annotation-ataa`, `-annotation-hs`, `-annotation-bmmc`, `-annotation-seaad`):
- Replace the limitation "Precision, recall and AUC averaging across classes is not stated." with "PR-AUC and ROC-AUC are macro-averaged (Methods); precision and recall are called global without a definition and appear to be averaged differently between models (source evidence concern), so do not compare them across models."
- Append: "Reference labels are the datasets' curated marker-gene and expert annotations, not independent ground truth."
- Append: "No rejection of unseen cell types or unassigned output is evaluated."
- In `-annotation-seaad` only, replace "Within-dataset stratified split, not cross-dataset transfer." with "Within-dataset split by tissue section (whole sections held out; train and test from the same study), not cross-dataset transfer."

C6. The three perturbation judgements (`use-case-mapping-lit-cells-networks-20261011-chen2026-perturbation-norman`, `-perturbation-adamson`, `-perturbation-replogle`):
- Replace the limitation "The number of DE genes behind the DE metrics is not stated." with "DE metrics use the top 20 differentially expressed genes per perturbation condition (Methods); the DE gene sets are not printed."
- In `-perturbation-norman` only, append: "Scores average single-gene and two-gene test perturbations under the GEARS simulation split; the number of two-gene combinations in training is not printed."

C7. `research.md`: the bullets "Precision, recall and multiclass AUC averaging are not stated" and "The number of DE genes behind the 'DE' perturbation metrics is not stated" are wrong; update them to match C1 to C3.

## Answers to the collector's questions

Chen 2026
- BC, MH and ME: confirmed. The Figure 2 legend prints "human breast cancer (BC/HBCA1), mouse hippocampus (MH/MHPC) and mouse embryo (ME/MOSTA E9.5)" (C4).
- No conventional baseline: confirmed for Tables 2 to 5 and S2; the limitation is correct.
- Averaging: PR-AUC and ROC-AUC are stated as macro (C2). Precision and recall are "global" and appear inconsistent across models (C3).
- Annotation protocols as proxy for annotation transfer: approved as proxy. A within-dataset 8:2 stratified split (section-wise for SEAAD) is weaker than the use case's transfer setting, which matches the existing proxy judgement on the Abdelaal intra-dataset protocol. Limitations C5 are required.
- Origin: `independent_paper` approved. The authors (Sally Chen, Alinejad-Rokny, Ye and colleagues, UNSW and collaborators) developed none of the six models; competing interests are declared none.

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

1. C1: the 36 Table 5 DE-gene results carry the reviewer's 'top 20' qualifiers.
2. C2: the 42 Table 4 AUPRC and AUROC results are 'macro-averaged over classes'.
3. C3: the 42 Table 4 precision and recall results carry the reviewer's qualifier, and the reviewer's evidence concern is on the source.
4. C4: the source's third limitation is the reviewer's text.
5. C5: the four annotation judgements carry the reviewer's limitations, including the SEAAD split wording.
6. C6: the three perturbation judgements carry the reviewer's DE limitation, and the Norman judgement the appended split limitation.
7. C7: `research.md` states the top-20 DE genes and the macro and 'global' averaging.
8. The seven judgements are `source_checked`, linked from `use-case-cell-type-annotation-transfer` and `use-case-genetic-perturbation-response`, and pinned with `npm run use-cases:repin`.
9. Every record is `source_checked`; each result's and claim's `review` block names the reviewer and keeps the extraction note.

## Records after correction

- benchmark: 1
- claim: 7
- configuration: 21
- dataset_subset: 10
- evaluation: 93
- model: 6
- protocol: 25
- result: 378
- source: 1
