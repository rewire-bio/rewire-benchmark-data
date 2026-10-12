# Research notes

Part of the 2026-10-11 RNA and other-omics literature pass. Search log: `data/omics/lit-search-20261011-rna-otheromics/ledger.jsonl`.

## Why this source

Ludaic and Elofsson 2026 (NAR, gkag813, CC BY) is an independent benchmark of ten deep learning RNA structure methods, including AlphaFold3, Boltz-1, Chai-1 and HelixFold3, on RNAs released after every method's training cut-off, split by structural similarity to training data. The authors developed none of the methods. It adds RNA 3D evidence that the store lacked apart from the RhoFold+ CASP15 comparison.

## Record counts

- benchmark: 1
- configuration: 10
- dataset: 5
- evaluation: 216
- model: 5
- protocol: 30
- result: 216
- source: 2

## Extraction notes

- Every cell of Tables 2-5 (means), Supplementary Tables S6-S7 (success rates against CASP16 thresholds) and S15 (mean per-interface DockQ by interface type).
- One protocol per subset and metric; one evaluation and one result per method and protocol. Origin `independent_paper` throughout.
- Table 4-5 iRMSD and LRMSD carry no printed unit; recorded as angstrom with a `unit_detail` saying so.
- Table 2 prints 'Chai' and Table 3 'Chai-1'; both map to the Chai-1 configuration.
- Model families reused: AlphaFold 3, Boltz, Chai-1, HelixFold 3, RhoFold+. New families: NuFold, RoseTTAFoldNA, trRosettaRNA, DRfold, DeepFoldRNA.
- Source concerns (in the source record's limitations, for the reviewer to decide on `evidence_concerns`): identical GDT-TS, INF and lDDT for DRfold and DeepFoldRNA in Tables 2-3 and in the supplementary per-target columns; RF2NA hard-set INF 0.668 versus a supplementary column mean of 0.608.
- Tables mark statistical ties with bold, underline and italic; the XML has no formatting, so ties are not recorded.
