# Review: lit-genomics-20261011-geneb, 2026-10-11

Reviewer: Claude review agent `reviewer-gen-1`, independent of the extractor `lit-genomics`. No human review claimed. Source transcription is not reproduction.

## Reviewer's report (verbatim)

GENEB (lit-genomics-20261011-geneb): approved with corrections. All values are correct; the corrections are to descriptive fields and one family link.

Checks:
- Source: I re-fetched leaderboard.json at commit 9642d481. Its SHA-256 7c8a9d98...f738 matches the source record and the archived gzip.
- Values: an automated comparison of all 1,845 results against the JSON (data.<regime>[model].micro_MCC, macro_MCC and cat_MCC.<category>) found 0 mismatches in printed_value, numeric_value, locator, configuration or regime protocol. No cell was missed (41 models x 3 regimes x 15 keys). A separate jq check of a stratified sample of 66 values (22 per regime, 33 models, all key types) also found 0 mismatches. The scientific-notation value (gpt2_gene_multi_v2_ft, 1-shot, Virus/Phage, 2.1089155370300136e-05) is expanded correctly.
- Metric and direction: MCC, higher is better, unitless. Correct.
- Origin: the repo README at the same commit says "none of the 40 evaluated models was developed by the authors or their funders", so independent_paper is correct for the 120 official evaluations. SpliceBERT is the only official=false entry (submitted "self-reported"), so origin unreported is right for its 3 evaluations.
- Scope: everything is a genomic or nucleotide foundation model except Enformer. Enformer is correctly marked supervised with foundation_model_eligible false.
- Duplicates with the store's 22 GENEB v1 Table 8 results: none. Those values differ from the leaderboard (for example GROVER Table 8 linear/MLP 0.466/0.477 against leaderboard full macro 0.492), so they are a different paper version and not double entries.

Corrections:
1. metric_qualifier on the 123 macro_MCC results (`*-<regime>-macro` ids) says "macro average over 100 tasks". That is wrong. The README defines Macro as the mean of the 13 category scores, and the JSON confirms it (mean(cat_MCC) equals macro_MCC to 1e-16). Change it to "<regime>; macro average: unweighted mean of the 13 category MCCs". The micro qualifier ("mean over all 100 tasks") is correct. Fix the same wording in the benchmark scope_note and in the text of the 3 protocols.
2. The 3 protocols (lit-genomics-20261011-geneb-protocol-full, -10shot, -1shot) do not name the probe. The README (Evaluation table) states "logistic-regression probe on frozen embeddings (max_iter=1000)". Add this to the protocol text, set comparison.adaptation on all 123 evaluations to "Logistic-regression probe on frozen embeddings", and drop the limitation "Probe type ... documented in the GENEB paper, not in the JSON".
3. Duplicate family: lit-genomics-20261011-geneb-model-metagene-1 duplicates catalog-model-metagene-1, which is already in data/entities/models.jsonl. Point lit-genomics-20261011-geneb-config-metagene-1 configuration_of to catalog-model-metagene-1 and remove the new model record.

Family links to discovery-model-dnabert-2, discovery-model-agro-nucleotide-transformer, discovery-model-nucleotide-transformer and catalog-model-nt-v2 follow existing store usage. The catalog/discovery duplication was already there and is not caused by this batch. No other new family in the batch exists elsewhere in the store or in the sibling lit-genomics batches.

## Corrections applied

Applied by the extractor in the extraction scripts (`extract/`), as the reviewer specified, before the batch was added to the store.

1. macro_MCC qualifiers, the benchmark scope note and the protocol text say the macro average is the unweighted mean of the 13 category MCCs.
2. Protocols name the logistic-regression probe on frozen embeddings (max_iter=1000); comparison.adaptation set accordingly; the 'probe type not in the JSON' limitation removed.
3. Configuration metagene-1 points to catalog-model-metagene-1; the duplicate new family record was removed.

## Records after correction

- benchmark: 1
- configuration: 41
- dataset: 1
- evaluation: 123
- model: 19
- protocol: 3
- result: 1845
- source: 1
