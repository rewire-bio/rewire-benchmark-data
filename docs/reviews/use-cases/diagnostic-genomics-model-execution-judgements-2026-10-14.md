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

## Independent review

Reviewer: Claude (Opus 5.5) review agent `review-169`, independent of the agent that drafted the judgements. No human review is claimed. Nothing was executed or reproduced.

### Sources

| Source | Artifact checked | SHA-256 | Outcome |
| --- | --- | --- | --- |
| `gfm-guide-20261014-source-hegde2025` | Europe PMC XML, PMC12652071 | `9ea68b688637b40f0aeced7c905822f6b14c352a3a935c61c407945f3d66ef47` | Matches the pinned hash |
| `gfm-guide-20261014-source-nt-nature-methods` | Europe PMC XML, PMC11810778 | `7c3b78a4f38ef053a08e466222e5662dd9711d91c535512d0b35d459d1fc7249` | Matches |
| `gfm-guide-20261014-source-hyenadna-arxiv-v2` | arXiv PDF 2306.15794v2 | `2f471549352ff571ac55faa80c8da453f9bf1ff5b01b6b87fa893457828e798c` | Matches |
| `gfm-guide-20261014-source-evee-v4` | bioRxiv v4 PDF from the DOI `v4.full.pdf` route | `85d368ee7959fe7f98fdbaf72db4367b3cd773b826a0bb3b3e0b636a033eb500` | Differs from the pinned bytes; bioRxiv stamps each download (the source's `hash_scope`). Text checked in this copy |
| `gfm-guide-20261014-source-ntv3-v1` | bioRxiv v1 PDF | not obtained | bioRxiv returned rate-limit errors (error 1015) on every attempt; Table 5 not re-read |

### Values checked

| Judgement | Values checked against the source | Outcome |
| --- | --- | --- |
| EVEE embedding extraction | "Extraction used ∼20,000 H100-hours"; 4,252,870 variants; 65k bp window; both strands; 4,252,870 × 2 × 512 × 4,096 bf16, about 34 TB; competing interests (11 Goodfire employees) | Match. The sentence is in the 'Dataset' paragraph after 'Harvesting' (page 8, line 461); locator made precise |
| Hegde 5 epochs | Table A1: training 7.53, 7.50, 7.48 h; evaluation 8.49, 8.51, 8.49 min for seeds 41 to 43. Table 1: 44,655 + 44,405 = 89,060 train, 4,306 + 4,556 = 8,862 test. Methods: 2 × TITAN Xp. Appendix A.3: LoRA through peft, r = 1. Affiliations: Kingston University | Values match. Three findings, below |
| Hegde convergence | "approximately 19 h" on 2 × TITAN Xp; "around 1 h per pruned model on average" on 2 × Quadro RTX 8000; NT not trained to convergence three times per version; Table 2 model sizes; Appendix A.2 LoRA for DNABERT-2 | Match. LoRA and model size added |
| NT IA3 | Methods 'Hardware': one node of eight A100, batch size eight, "20 min for the 500M-parameter models and 50 min for the 2.5B-parameter models". Discussion: "under 15 min on a single GPU" | Match. The average spans several 500M models; limitation reworded |
| NTv3 Table 5 | Not re-read (source unavailable today). Grade and limitations checked against the protocol and the 13 results reviewed in PR #150 | Grade accepted |
| HyenaDNA Table A.2 | 8 × 2080 Ti, 25 days, 12,000; 128 × A100-80GB, 28 days, 215,000; 1 × A100-40GB, 80 min, 1.3 (twice) | Match; the 2.5-fold discrepancy (4,800 and 86,016 GPU-hours from GPUs × wall clock) is confirmed |

### Findings and fixes

1. **Hegde fine-tuning was LoRA, not full fine-tuning.** Appendices A.2 and A.3 list "Parameter-efficient fine-tuning using the peft package: r = 1; lora_alpha = 32; lora_dropout = 0.1" for both models. The three Hegde evaluations from #138 recorded `comparison.adaptation` "Full fine-tuning" (the PR #150 review corrected the 5-epoch configuration but not the evaluations). Corrected on the three evaluations, with `metadata-correction-gfm-guide-20261014-hegde-*-adaptation` claims in `corrections.jsonl`; the judgement endpoints and limitations now say LoRA.
2. **Hegde training-split size conflicts within the article.** Table 1 gives 89,060 training variants; the Methods text says "the 88,717 variant-centred DNA sequences in the training split". The endpoint gives both and a limitation records the conflict. Not raised as an evidence concern: no stored result depends on the split size.
3. **Hegde hardware for Table A1 is implied, not stated.** The Methods tie 2 × TITAN Xp to training the Nucleotide Transformer to convergence and say the two models ran on different machines. The constraint and limitation now say so instead of attributing the GPUs to Table A1.
4. **Meaning of the three Hegde seeds.** The draft constraint said the seeds "repeat timings only". They repeat the whole fine-tuning and evaluation, and Table A1 prints identical aggregate accuracy, AUROC and F1. That is not per-variant concordance, so the reproducibility gap stands; the constraint was reworded.
5. EVEE locator made precise, and the NT IA3 limitation now notes that the average covers several 500M-parameter models.

### Verdicts

| Judgement | Grade | Verdict | Lifecycle after review |
| --- | --- | --- | --- |
| `use-case-mapping-gfm-guide-20261014-evee-embedding-extraction` | proxy | Accepted with locator fix | Withheld: the source carries an evidence concern (EVEE Figure 1b and 1c NTv3 column) |
| `use-case-mapping-gfm-guide-20261014-hegde2025-eqtl-5-epochs` | proxy | Accepted with fixes 1 to 4 | Active |
| `use-case-mapping-gfm-guide-20261014-hegde2025-eqtl-convergence` | proxy | Accepted with fix 1 | Active |
| `use-case-mapping-gfm-guide-20261014-nt-ia3-finetune` | proxy | Accepted | Withheld: source concern on the Methods and Discussion conflict |
| `use-case-mapping-gfm-guide-20261014-ntv3-training-gpu-hours` | outside_scope | Accepted | Active as outside scope; no evidence shown |
| `use-case-mapping-gfm-guide-20261014-hyenadna-pretraining-compute` | outside_scope | Accepted | Withheld: the source carries the Table A.2 GPU-hours concern. As an outside-scope judgement it would show no evidence either way |

Fine-tuning time is graded proxy, not outside scope: a diagnostic team adapting a foundation model to its own variant task pays this cost on its own hardware, unlike pretraining. Hegde's evaluation time is inference over 8,862 human variants and is the closer proxy.

`reviewed_evaluations`: EVEE `gfm-guide-20261014-eval-evee-embedding-extraction-compute`; Hegde 5 epochs `gfm-guide-20261014-eval-hegde-nt-500m-human-ref-5-epochs`; Hegde convergence `gfm-guide-20261014-eval-hegde-dnabert-2-pruned-convergence` and `-nt-500m-human-ref-convergence`; NT IA3 `gfm-guide-20261014-eval-nt-2-5b-ia3-fine-tuning-runtime` and `-nt-500m-ia3-fine-tuning-runtime`. Every result on these evaluations was checked (one, six, two and two results).

### Use-case text

With the Hegde judgements active the use case has a second active foundation-model study, on human variants. Text that said there was one had to change:

- `evidence_gaps`: the gap "The one active foundation-model execution benchmark uses microbial genomes" is rewritten to name both active studies (Yu, microbial inference; Hegde, human eQTL fine-tuning and scoring on older GPUs), keep "none measures a genomic foundation model inside a diagnostic workflow on human data", and list the withheld Aspidova, EVEE and NT IA3 studies. The reproducibility gap now notes that Hegde's three seeds print identical aggregate metrics but no per-variant concordance.
- `setting`: adds Hegde et al. 2025, lists the four withheld studies (Zheng, Aspidova, Pearce, Dalla-Torre) and says the NTv3 and HyenaDNA pretraining compute is linked as outside scope.
- `decision` and `clinical_scope` said "the one active foundation-model inference benchmark" and "one foundation-model inference benchmark on microbial genomes"; both now describe two foundation-model benchmarks outside any diagnostic workflow. `output` and `exclusions` stay true and are unchanged.
- `source_ids` and `citation_locators` add `gfm-guide-20261014-source-hegde2025` (clean). The EVEE and NT sources are not cited, because their concerns would withhold every positive judgement.
- Metadata-correction claims keep the previous `setting`, `decision` and `clinical_scope`.

`setting`, `decision` and `clinical_scope` are pinned by every reviewed claim on the use case, so all 32 were re-reviewed for this change of wording and re-pinned: the 24 existing judgements, the baseline, the summary and the six new judgements. Before re-pinning, each existing claim's pins differed only in the use-case record (the summary also in the newly reviewed evaluations). The rewording changes no judgement's endpoint or grade.

The summary also had to change: it said six active benchmarks with one foundation-model study, and its pins include the reviewed evaluations of every reviewed judgement. It now says eleven linked benchmarks, seven active, four withheld, adds a sentence with the Hegde values (7.53, 7.50, 7.48 h; 8.49, 8.51, 8.49 min; approximately 19 h; around 1 h), each traced to a stored result, and names the EVEE and NT studies as withheld without values. `collection_plan` is unchanged: its comparison (Rewire executing a foundation model inside a workflow) is not answered.

### Remaining gaps

- NTv3 Table 5 was not re-read by this reviewer because bioRxiv refused the download.
- The EVEE and NT IA3 judgements stay withheld until their source concerns are resolved.
- Still open in #162: Saadat and Fellay, the Aspidova throughput unit, the HyenaDNA Table A.2 question.

### Effect on the store

Active judgements across all use cases went from 395 to 398 (the two Hegde judgements and the NTv3 outside-scope judgement). No previously active judgement, summary or baseline is withheld. The draft `reason` on the six judgements, which said they awaited review, was replaced.
