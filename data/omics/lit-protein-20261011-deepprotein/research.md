# Research notes

Part of the 2026-10-11 protein-fitness and structure-design literature pass (window 2025-10-01 to
2026-10-11). The search log is in `data/omics/lit-search-20261011-protein-structure/ledger.jsonl`.

## Why this source

The broadest in-window table-backed comparison of protein language models against conventional baselines:
18 methods (CNN, CNN-RNN, Transformer, seven graph networks, ESM-1b, ESM-2-650M, Prot-T5-XL, ProtBert,
the authors' fine-tuned DeepProt-T5, and two chemistry LLMs prompted for the task) over 17 datasets in
nine task groups, each with five random seeds, plus a resource-usage table. The datasets come from TAPE,
PEER and TDC, so the comparison sits next to benchmarks already in the store.

## Record counts

- source 1, benchmark 1, model 16, configuration 18, dataset 17, protocol 60, evaluation 436, result 436
  and one claim (the relevance judgement): 986 records.

## Extraction notes (written before review; `review.md` takes precedence where they differ)

- The regression correlation column is printed as rho while Figure 3's caption calls it
  "Spearman (Pearson) Coefficient". Which coefficient it is cannot be settled from the article, so the
  results use the generic `correlation` concept, the ambiguity is in every qualifier, and the source
  carries an `evidence_concerns` entry so these values cannot be compared automatically with results
  recorded as Spearman or as Pearson.
- PR-AUC, averaged F1 and accuracy are printed on a 0 to 100 scale and recorded as `percent`, following
  the store's existing convention; ROC-AUC is recorded as `auroc`, unitless, with `unit_detail`
  "printed x100". MAE has no printed unit.
- Cells printed OOM, "Length Exceeded" and NaN are kept as results with a missing value reason of
  `unavailable` and a note: they are outcomes of the run, not scores.
- Cells printed `/` are not measurements. The Table 7 footnote says structure-based and pretrained
  language models were disregarded for residue-level and secondary structure prediction, so the 12 such
  cells are left out rather than recorded as zero.
- Cells carrying the article's `**` significance mark keep it in `printed_value`; the mark is also noted
  in the result's limitations. The article's statistical tests were not re-run.
- Origin is `author_reported` throughout: the DeepProtein authors ran every baseline and also introduce
  DeepProt-T5, which tops several tasks.
- Table 8's model labels include "Prot-T5" where Tables 2 to 7 use "Prot-T5-XL". They are kept as
  separate configurations because the article does not say they are the same checkpoint.

## Printed spacing

`printed_value` holds the cell's text exactly as the JATS XML gives it, with the cell's own internal
elements concatenated. The XML is not consistent about the space around the plus-minus sign: within one
row it holds both "0.680 ± 0.001" and "0.678±0.001". A self-check that searched the whole stripped XML
text for each stored string found 79 of the 436 values only after normalising that spacing, which is the
same artefact seen from the other side. No digit differs. The rendered PDF spacing cannot be recovered
from the XML, so nothing was invented; a reviewer comparing against the PDF should compare the digits.

## For the reviewer

- The rho ambiguity and the resulting choice of the `correlation` concept is the main judgement call.
- Check the "Prot-T5" against "Prot-T5-XL" split in Table 8, and whether the two should instead be one
  configuration.
- Check the handling of OOM, "Length Exceeded", NaN and `/` cells.
- The relevance judgement for `use-case-protein-stability` is `proxy` on the Stability rho protocol; the
  proposed `assessed_by` link is in `use-case-links.json` and is not applied.
