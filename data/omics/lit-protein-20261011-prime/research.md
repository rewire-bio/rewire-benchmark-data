# Research notes

Part of the 2026-10-11 protein-fitness and structure-design literature pass (window 2025-10-01 to
2026-10-11). The search log is in `data/omics/lit-search-20261011-protein-structure/ledger.jsonl`.

## Why this source

A model-scale and representation study with a printed table: ESM-2 at 8M, 150M and 650M parameters and
ESM-C at 300M and 600M, each with CLS against mean pooling and frozen against fine-tuned, on SARS-CoV-2
RBD binding and expression, under a random split and a position-stratified split, with a one-hot mean
baseline. The two splits are the point: R-squared falls from about 0.8 to about 0.2 or below when whole
mutated positions are held out, and several configurations go negative.

## Extraction notes (written before review; `review.md` takes precedence where they differ)

- 21 configurations (5 model sizes x 2 pooling choices x 2 fine-tuning settings, plus the one-hot
  baseline), 8 protocols (2 splits x 2 targets x 2 metrics), 168 results: 370 records.
- Every cell is printed as mean plus or minus standard deviation. The article does not say how many runs
  the standard deviation covers, so the uncertainty object carries no sample count.
- RMSE has no printed unit; the unit concept is `unit-unreported` with the assay scale noted.
- The One-Hot Mean row repeats its label across the three leading cells in the XML; it is recorded as one
  baseline configuration with a `conventional_pipeline` method type.

## For the reviewer

- Check the fine-tuned column mapping (a tick means fine-tuned, a cross means frozen).
- Check the negative R-squared values are transcribed with their signs.
- No use-case judgement is proposed: the use cases in the store do not cover viral RBD binding and
  expression prediction.
