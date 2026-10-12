# Research notes

Part of the 2026-10-11 microbial and interactions literature pass (window 2025-10-01 to 2026-10-11).
The search log is in `data/omics/lit-search-20261011-microbial-interactions/ledger.jsonl`.

## Why this source

ViroBench is the largest independent evaluation of nucleotide foundation models on viral and phage
genomics found in the window: 66 foundation models plus four conventional baselines (BLAST, Kraken2,
a BiLSTM and a CNN) under one frozen-embedding protocol, with two split strategies that separate
phylogenetic from temporal generalisation. Nothing in the store covered the microbial lane at this
breadth; the store's only comparable microbial benchmark is LAMBDA (prophage detection).

It also puts conventional similarity search and foundation models on the same protocol, which is what
the lane is missing: BLAST beats every foundation model on host classification for the ALL-virus
genus-disjoint split (92.50 against LucaVirus 84.56).

## Record counts

- benchmark: 1
- configuration: 76
- dataset: 6
- evaluation: 912
- method: 2
- model: 10
- protocol: 12
- result: 912
- source: 1

## Extraction notes (written before review)

- Twelve protocols: three virus sets (ALL, DNA, RNA) x two tasks (taxonomy, host) x two splits
  (genus-disjoint, temporal). Every one of the 76 configurations has a value in all twelve, so the
  result count is 76 x 12.
- Each printed cell is a mean with a standard deviation in parentheses. The standard deviation is
  recorded as `uncertainty` with scope "across hyperparameter settings", because Section 4.1.2 says
  the spread is over window configurations and learning rates, not over seeds. A reviewer should
  confirm that reading.
- Values carry no unit in Tables 4 and 25. The ablation tables (17 to 20) say Macro-F1 in %, so
  percent is recorded with `unit_detail` "Macro-F1 x100 as printed".
- The taxonomy columns print one Macro-F1 per model although the source predicts five ranks. The
  source does not state how the ranks are combined. For the rows spot-checked the value equals the
  mean of the five per-rank values in Table 26; that is recorded as an observation in the protocol
  limitations, not as a stated aggregation, and no value was computed from it.
- Origin: `author_reported` for the authors' own in-house models (ViroHyena, ViroDNABERT2,
  ViroCaduceus) and their from-scratch BiLSTM and CNN baselines; `independent_paper` for everything
  else. The authors ran every model either way, which the protocol limitations say.
- Model families reuse existing store records where one exists (Evo, Evo 2, DNABERT, DNABERT-2,
  DNABERT-S, GenomeOcean, LucaOne, GENA-LM, GROVER, GENERator, Caduceus, HyenaDNA, NT v1/v2/v3,
  AIDO.DNA, RNA-FM, RNABERT, BLAST, Kraken2). New families: LucaVirus, Genos, OmniReg-GPT, AIDO.RNA,
  RiNALMo, BiRNA-BERT, MP-RNA and the three in-house Viro* models.
- Table 3 lists NT v3 under phage-specific pretraining coverage and Table 9 lists it as non-viral.
  Table 25 groups the NTv3 rows under phage-specific coverage, which is what the configurations
  record. Flagged in the source limitations for a reviewer.
