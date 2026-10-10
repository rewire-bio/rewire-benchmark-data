# Store form: source_label removed

`batch.jsonl` is the reviewed batch and is unchanged, so the receipt in `review.json` still binds the reviewed bytes.

`source_label` is reserved for records renamed through a reviewed `source_identity` (`shared/omics/source-identity.ts`). The store copies of the records below had a label and no identity. In each, `source_label` equalled `reported_name`, which keeps the printed name, so the label was removed (rule 1). No other field and no value changed.

| Record | Rule |
| --- | --- |
| `tgtval-20261009-config-debrouwer2026-biomni-a1-claude-4` | 1: source_label equals reported_name, removed |
| `tgtval-20261009-config-debrouwer2026-c2s-gemma-2b` | 1: source_label equals reported_name, removed |
| `tgtval-20261009-config-debrouwer2026-embedding-knn` | 1: source_label equals reported_name, removed |
| `tgtval-20261009-config-debrouwer2026-gemini-3-flash` | 1: source_label equals reported_name, removed |
| `tgtval-20261009-config-debrouwer2026-gemini-3-flash-gepa` | 1: source_label equals reported_name, removed |
| `tgtval-20261009-config-debrouwer2026-gemini-3-pro` | 1: source_label equals reported_name, removed |
| `tgtval-20261009-config-debrouwer2026-gemini-3-pro-few-shot` | 1: source_label equals reported_name, removed |
| `tgtval-20261009-config-debrouwer2026-gene-frequency-by-phenotype` | 1: source_label equals reported_name, removed |
| `tgtval-20261009-config-debrouwer2026-gene-relevance-predictor` | 1: source_label equals reported_name, removed |
| `tgtval-20261009-config-debrouwer2026-gpt-5-4` | 1: source_label equals reported_name, removed |
| `tgtval-20261009-config-debrouwer2026-gpt-oss-120b` | 1: source_label equals reported_name, removed |
| `tgtval-20261009-config-debrouwer2026-gpt-oss-120b-sft` | 1: source_label equals reported_name, removed |
| `tgtval-20261009-config-debrouwer2026-gpt-oss-120b-sft-grpo` | 1: source_label equals reported_name, removed |
| `tgtval-20261009-config-debrouwer2026-llm-ensemble` | 1: source_label equals reported_name, removed |
| `tgtval-20261009-config-debrouwer2026-oracle-knn` | 1: source_label equals reported_name, removed |
| `tgtval-20261009-config-debrouwer2026-qwen3-5-2b` | 1: source_label equals reported_name, removed |
| `tgtval-20261009-config-gupta2025-bda-llama-3-1-8b` | 1: source_label equals reported_name, removed |
| `tgtval-20261009-config-gupta2025-bda-qwen-2-7b` | 1: source_label equals reported_name, removed |
| `tgtval-20261009-config-gupta2025-bda-rand-claude-3-5-sonnet` | 1: source_label equals reported_name, removed |
| `tgtval-20261009-config-gupta2025-bda-rand-llama-3-1-8b` | 1: source_label equals reported_name, removed |
| `tgtval-20261009-config-gupta2025-bda-rand-qwen-2-7b` | 1: source_label equals reported_name, removed |
| `tgtval-20261009-config-gupta2025-bda-replicated-claude-3-5-sonnet` | 1: source_label equals reported_name, removed |
| `tgtval-20261009-config-gupta2025-bda-reported-numbers-claude-3-5-sonnet` | 1: source_label equals reported_name, removed |
| `tgtval-20261009-config-gupta2025-gp-llama-3-1-8b` | 1: source_label equals reported_name, removed |
| `tgtval-20261009-config-gupta2025-gp-qwen-2-7b` | 1: source_label equals reported_name, removed |
| `tgtval-20261009-config-gupta2025-linear-ucb-llama-3-1-8b` | 1: source_label equals reported_name, removed |
| `tgtval-20261009-config-gupta2025-linear-ucb-qwen-2-7b` | 1: source_label equals reported_name, removed |
| `tgtval-20261009-config-roohani2025-badge` | 1: source_label equals reported_name, removed |
| `tgtval-20261009-config-roohani2025-claude-3-5-sonnet` | 1: source_label equals reported_name, removed |
| `tgtval-20261009-config-roohani2025-claude-3-haiku` | 1: source_label equals reported_name, removed |
| `tgtval-20261009-config-roohani2025-claude-3-opus` | 1: source_label equals reported_name, removed |
| `tgtval-20261009-config-roohani2025-claude-3-sonnet` | 1: source_label equals reported_name, removed |
| `tgtval-20261009-config-roohani2025-claude-v1` | 1: source_label equals reported_name, removed |
| `tgtval-20261009-config-roohani2025-coreset` | 1: source_label equals reported_name, removed |
| `tgtval-20261009-config-roohani2025-discobax` | 1: source_label equals reported_name, removed |
| `tgtval-20261009-config-roohani2025-gpt-3-5-turbo` | 1: source_label equals reported_name, removed |
| `tgtval-20261009-config-roohani2025-gpt-4o` | 1: source_label equals reported_name, removed |
| `tgtval-20261009-config-roohani2025-human` | 1: source_label equals reported_name, removed |
| `tgtval-20261009-config-roohani2025-k-means-d` | 1: source_label equals reported_name, removed |
| `tgtval-20261009-config-roohani2025-k-means-e` | 1: source_label equals reported_name, removed |
| `tgtval-20261009-config-roohani2025-margin-sample` | 1: source_label equals reported_name, removed |
| `tgtval-20261009-config-roohani2025-o1-mini` | 1: source_label equals reported_name, removed |
| `tgtval-20261009-config-roohani2025-o1-preview` | 1: source_label equals reported_name, removed |
| `tgtval-20261009-config-roohani2025-random` | 1: source_label equals reported_name, removed |
| `tgtval-20261009-config-roohani2025-soft-uncertain` | 1: source_label equals reported_name, removed |
| `tgtval-20261009-config-roohani2025-sonnet-coreset` | 1: source_label equals reported_name, removed |
| `tgtval-20261009-config-roohani2025-top-uncertain` | 1: source_label equals reported_name, removed |
