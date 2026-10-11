# Review: lit-genomics-20261011-ntbench, 2026-10-11

Reviewer: Claude review agent `reviewer-gen-2`, independent of the extractor `lit-genomics`. No human review claimed. Source transcription is not reproduction.

## Reviewer's report (verbatim)

ntbench (lit-genomics-20261011-ntbench @ ce56c11): APPROVED WITH CORRECTIONS. All values are correct.

Checks:
- Source: SHA-256 ef0f357a… matches the re-downloaded SI PDF.
- Values: I wrote my own parser over the pdftotext layer and compared all 491 results (printed value, numeric value and SD; 144 in ST6, 324 in ST7, 23 in ST9). 0 mismatches and no missing cells.
- I also checked a seeded stratified sample of 62 cells against the rendered pages 7 and 8 (20 from ST6, 30 from ST7, 12 from ST9). All matched.
- Dataset sizes and lengths match Supplementary Table 5 (an image, checked visually). claims.csv agrees with the batch.
- Metric (MCC, higher), uncertainty (SD over 10 folds) and the 10-fold CV split are right.
- Scope fits.

Corrections:
1. Duplicates inside the batch. ST7 reprints the Raw Probe and three BPNet rows unchanged from ST6. Its caption says BPNet is fully trained and Raw Probe uses probing, so these are the same measurements. Fix: remove the 72 ST7 copies (results and evals `lit-genomics-20261011-ntbench-{result,eval}-{raw-probe,bpnet-original,bpnet-large,bpnet-x-large}-fine-tuning-<task>`), and add "printed identically in Supplementary Table 7" to the matching ST6 locators. Those copies currently also carry the wrong adaptation, "parameter-efficient fine-tuning".
2. Adaptation on the 54 ST6 BPNet evals (`...-eval-bpnet-*-probing-<task>`): change "probing" to "trained from scratch". The ST6 caption says the BPNet models are fully trained CNNs.
3. Origin of all BPNet evaluations (54 ST6, plus 3 ST9 `...-eval-bpnet-*-control-summary`): change author_reported to independent_paper. The vocabulary defines author_reported as "authors of the evaluated method", and BPNet is Avsec et al.'s, not InstaDeep's. Keep author_reported for the NT models, the NT random-init controls and the Raw Probe.
4. Link to PR #107: add `same_data_as` from `lit-genomics-20261011-ntbench-data-all-18-tasks` to `gfm2-20261011-datta2026-data-nt-benchmark`. The link is informational only and the values must not merge: Datta uses the train/test split, while this batch reports 10-fold CV medians.
5. Minor, `lit-genomics-20261011-ntbench-config-dnabert-1-parameter-efficient-fine-tuning`: the SI only says "Finetuning" for DNABERT-1, and DNABERT-1 is not in ST7. Either rename it to `...-dnabert-1-fine-tuning` or add a note that PEFT is not stated. Also normalise the ST9 eval adaptation strings ("Finetuning", "Probing", "control", "Training from scratch") to the per-task wording.

Duplicates against the store: none. `qa-descriptions-20261010-source-nt-v2` is the abstract of the same DOI, a different artifact with no results attached, so keeping a separate SI source is fine. No NT-benchmark results exist on main or in PR #107.

Optional source note: ST5 prints Promoter TATA as 30000/1372 and non-TATA as 5062/212. That looks swapped compared with the public dataset, where the TATA set is the small one. The records follow the print correctly; a limitation line on the two datasets would help.

## Corrections applied

Applied by the extractor in the extraction scripts (`extract/`), as the reviewer specified, before the batch was added to the store.

1. The 72 Supplementary Table 7 copies of the Raw Probe and three BPNet rows were removed (identical to Table 6); the Table 6 locators now say 'printed identically in Supplementary Table 7'.
2. Adaptation of the BPNet evaluations is 'trained from scratch'.
3. Origin of all BPNet evaluations (Table 6 and Table 9) is independent_paper; NT models, NT random-init controls and the Raw Probe stay author_reported.
4. same_data_as link from lit-genomics-20261011-ntbench-data-all-18-tasks to gfm2-20261011-datta2026-data-nt-benchmark (informational; values are not merged).
5. DNABERT-1 configuration renamed to -fine-tuning with a limitation that PEFT is not stated; Table 9 evaluation adaptations use the per-task wording.
6. Scope note on the Promoter TATA and non-TATA datasets that Supplementary Table 5 may print their sizes swapped.

## Records after correction

- benchmark: 1
- configuration: 23
- dataset: 19
- evaluation: 419
- method: 1
- model: 1
- protocol: 37
- result: 419
- source: 1
