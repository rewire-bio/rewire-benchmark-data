# Draft relevance judgements: genomic foundation model compute protocols, 2026-10-14

Author: Claude (Opus 5.5) agent working on issue #162. No human review is claimed. Nothing was executed or reproduced. The judgements are drafts (`needs_review`) for a different worker to review with `review-evidence`.

Batch: `data/omics/gfm-guide-execution-judgements-20261014/` (six judgement claims). Use case changed: `use-case-diagnostic-genomics-model-execution` (six `assessed_by` links, nothing else).

## Scope

Issue #162 asks for the execution protocols added by `data/omics/gfm-guide-sources-20261014/` (issue #138, PR #167) to be judged against `use-case-diagnostic-genomics-model-execution`. That batch has eight protocols. Six measure compute and are judged here. The two EVEE AUROC protocols (`gfm-guide-20261014-protocol-evee-deconfounded-snv-auroc`, `gfm-guide-20261014-protocol-evee-clinvar-indel-auroc`) measure pathogenicity classification, not execution, and were not considered for this use case.

AlphaGenome has no protocol in the batch. Its compute statements are three claims (`gfm-guide-20261014-claim-alphagenome-recommended-hardware`, `-training-compute`, `-variant-scoring-time`), and a relevance judgement needs a protocol, so no AlphaGenome judgement is recorded. The variant scoring time ("less than 1 s on an NVIDIA H100 GPU" per variant) is a bound, not a value, which is why #138 kept it as a claim.

## Judgements

The use case asks which model configuration and execution workflow can meet a diagnostic genomics team's resource, throughput and reproducibility constraints. The existing linked foundation-model studies (Yu et al. 2026, Aspidova et al. 2026) are graded proxy: they time a model's forward passes on stated hardware but not inside a diagnostic workflow. The same standard is applied here. Training cost spent once by a model's developers is judged outside scope, because a team running a model uses the trained checkpoint. Adaptation cost (fine-tuning) that a team might itself incur is graded proxy.

| Claim | Protocol | Relevance | Reason in one line |
| --- | --- | --- | --- |
| `use-case-mapping-gfm-guide-20261014-evee-embedding-extraction` | EVEE Evo 2 embedding extraction compute | proxy | Inference of a genomic foundation model over 4,252,870 human ClinVar variants; one approximate H100-hours total, research harvest not a diagnostic workflow |
| `use-case-mapping-gfm-guide-20261014-hegde2025-eqtl-5-epochs` | Hegde et al. 2025 Table A1 | proxy | Fine-tuning and test-set scoring time of NT 500M on 8,862 human eQTL variants, three seeds, independent of the model developers; hardware only in Methods |
| `use-case-mapping-gfm-guide-20261014-hegde2025-eqtl-convergence` | Hegde et al. 2025 Methods | proxy | Approximate time to convergence for NT 500M and pruned DNABERT-2, on different GPUs |
| `use-case-mapping-gfm-guide-20261014-nt-ia3-finetune` | Nucleotide Transformer IA3 fine-tuning | proxy | Developer-reported mean fine-tuning time on one 8 × A100 node, conflicting with the Discussion |
| `use-case-mapping-gfm-guide-20261014-ntv3-training-gpu-hours` | NTv3 Table 5 | outside_scope | Training compute per stage, spent once by the developers |
| `use-case-mapping-gfm-guide-20261014-hyenadna-pretraining-compute` | HyenaDNA Table A.2 | outside_scope | Pretraining compute from scratch; the table also carries a source concern |

Each claim records endpoint, rationale, constraints, limitations, `source_ids` and `citation_locators`. Locators come from the reviewed #138 records. For Hegde et al. 2025 the split sizes (89,060 training and 8,862 test variants, Table 1) and the GPUs in Methods paragraph 3 were checked against the Europe PMC XML, whose SHA-256 (`9ea68b68...6ef47`) matches `gfm-guide-20261014-source-hegde2025`.

## Effect on the use case

- Only `links` changed. No pinned field changed, so no reviewed judgement or summary is withheld.
- The new sources were not added to the use case's `source_ids`. Two of them (`gfm-guide-20261014-source-evee-v4`, `gfm-guide-20261014-source-nt-nature-methods`) carry evidence concerns, and a source the use case cites with a concern withholds every positive judgement on the use case. The reviewer should add the clean sources (Hegde) when activating those judgements.
- Three of the four proxy judgements rest on a source with an evidence concern (EVEE, Nucleotide Transformer; HyenaDNA is outside scope). Even after review they stay withheld until those concerns are resolved. Only the two Hegde judgements can become active on review alone.
- `evidence_gaps`, `summary`, `decision`, `setting` and `collection_plan` are unchanged. The gaps describe active evidence, and draft judgements are not evidence, so nothing in them is out of date. If the Hegde judgements become active, the reviewer should revisit the gap "The one active foundation-model execution benchmark uses microbial genomes", since Hegde times a genomic foundation model on human variant data (though not in a diagnostic workflow), and the `setting` text, which lists the linked studies.

## For the reviewer

- Check each relevance grade against the use case question, in particular whether fine-tuning time (Hegde, NT IA3) is proxy or outside scope for an execution workflow.
- List `reviewed_evaluations` for each positive judgement and pin with `npm run use-cases:repin -- <review.md> <claim-id>...`.
- The other items in #162 (Saadat and Fellay download, the Aspidova throughput unit, the HyenaDNA Table A.2 GPU-hours question) are not part of this change.
