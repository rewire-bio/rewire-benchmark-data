# Experimental-lane use-case evidence audit — genetic-perturbation-response bounded intake, 2026-10-07

Scope: `use-case-genetic-perturbation-response` (B334/BL334, rewire-benchmarks #25; programme rewire-benchmark-data #3; article plan rewire.it #334). Focused execution gap: rewire-benchmarks [#29](https://github.com/rewire-bio/rewire-benchmarks/issues/29) ("Freeze Norman controls and metric-sensitivity protocol before model comparison"), opened after an open/closed title-and-body dedup check; this intake does not close that gap and is reconciled to it, not duplicative of it.

## What is added

PertEval-scFM (Wenteler et al., ICML 2025, PMLR v267 pp. 66633–66677), Table 1, Norman single-gene section, 2,000 highly-variable-gene preprocessing: exactly three printed AUSPC (Area Under the SPECTRA Performance Curve) values — GEARS (trained from scratch, no pretrained weights, official implementation with only the train-test split modified) 0.815 ± 0.039; MLP baseline (input Xc ⊕ Gc, Eq. 3: raw control expression concatenated with perturbed-gene co-expression features, not raw expression alone) 4.484 ± 0.299; Mean baseline (predicted effect = mean expression of "all cells in the same context" minus the cell's own expression, per the paper's own Section 2.2 text — population not restricted to controls or training cells in that text) 4.612 ± 0.317 — all ×10⁻² as printed.

The scored quantity is the perturbation-effect delta := P − Xc (Eq. 5), described by the source as a "log fold change perturbation effect" — not raw post-perturbation expression, and a different metric construction from GEARS Supplementary Table 6's own Pearson-ΔExpression metric. This is a second, independent, from-scratch GEARS evaluation on a differently-preprocessed Norman2019 subset (2,000 HVGs, SPECTRA-sparsification splits, AUSPC metric), distinct from the existing GEARS Supplementary Table 6 catalogue entries (different gene universe, split mechanism, and metric); the eight existing Table 6 results and their two mappings remain byte-identical.

## Uncertainty

AUSPC's printed `±` is the source's own propagated uncertainty: derived from each split's MSE uncertainty via the trapezoidal integral's partial derivatives (Appendix F.2, Eqs. F3–F5), and separately described in the main-text Figure 2 caption as "standard error bars" — two compatible descriptions of the same author-reported quantity, not a conflict. The underlying per-split uncertainty is attributed to triplicate experiments per model (Appendix I, Figure I1 caption), not to the Figure 2 region. Figure I1's own caption states "8 train-test splits," while Table 1 prints seven S-columns (S0.1–S0.7) and Appendix F.2 describes the grid as 0.1–0.7; this discrepancy is preserved as printed, not resolved, and no eighth Table 1 column or confirmed `n_runs=7` is inferred. The F3–F5 derivation is the authors' own formula; its mathematical correctness is not independently validated here, and this uncertainty is not read as an independently resampled model-seed SD or confidence interval.

## What is explicitly not added

- The same table's five scFM-embedding configurations (Geneformer, scBERT, scFoundation, scGPT, UCE).
- The same table's double-gene section (printed GEARS AUSPC 0.808, Mean-baseline AUSPC 4.255, printed Δ 4.254 — not reproducible from simple subtraction, 4.255−0.808=3.447 ≠ 4.254; preserved as an unresolved printed inconsistency, out of scope here).
- Table 2 (Replogle RPE1), which separately shows a running-text-vs-table-row conflict (text attributes AUSPC 0.1251 to "the Mean baseline"; the table assigns 0.1251 to Geneformer and 0.1341 to Mean baseline) — preserved, not resolved, out of scope here.
- The paper's own ΔAUSPC column and per-split MSE sub-values.

## Input-budget and scope caveats

GEARS, the MLP baseline, and the Mean baseline receive different input representations (graph-based architecture over raw expression plus prior knowledge; a fixed concatenated raw-expression-and-co-expression vector; no learned input at all, respectively) — not an identical input budget. This protocol concerns generalisation to unseen perturbations under SPECTRA's distribution-shift splits; it does not test or establish forecasting for unseen cells, donors, or cell-line/context transfer, and does not establish prospective experiment-selection hit rate (case 6's separate endpoint, tracked at rewire-benchmarks #348).

## Review

Automated source review only (Claude Sonnet, local extraction and coding; no skills or subagents invoked), independently reviewed by Codex, which verified the PertEval-scFM full-text Methods sections (2.1–2.3, Appendix F.2, Appendix I), the pinned GitHub code (LICENSE blob and `predictors.py` at commit `ce48c8b998901c8f8b6275114caac3a4d8543c0b`), and the PMLR general publication agreement, before this corrected version of the intake was finalized. No model execution, no paid access, no access bypass, no outreach. `use-case-genetic-perturbation-response` remains an open, incomplete evidence-collection case: a confirmed, directly relevant 27-method/29-dataset benchmark (scPerturBench, Wei et al., *Nat. Methods*) remains genuinely paywalled and unread; the focused execution gap tracked at rewire-benchmarks #29 (a frozen, matched Norman control panel with a metric-sensitivity check and a separately registered context-transfer protocol) is not addressed by this source-transcription intake.
