# Store form: source_label removed

`batch.jsonl` is the reviewed batch and is unchanged, so the receipt in `review.json` still binds the reviewed bytes.

`source_label` is reserved for records renamed through a reviewed `source_identity` (`shared/omics/source-identity.ts`). The store copies of the records below had a label and no identity. In each, `source_label` equalled `reported_name`, which keeps the printed name, so the label was removed (rule 1). No other field and no value changed.

| Record | Rule |
| --- | --- |
| `structural-20261009-config-fromm2026-af3-aeitm-oracle` | 1: source_label equals reported_name, removed |
| `structural-20261009-config-fromm2026-af3-aerankconf-oracle` | 1: source_label equals reported_name, removed |
| `structural-20261009-config-fromm2026-af3-aetm-oracle` | 1: source_label equals reported_name, removed |
| `structural-20261009-config-fromm2026-af3-dockq-oracle` | 1: source_label equals reported_name, removed |
| `structural-20261009-config-fromm2026-af3-ipsae` | 1: source_label equals reported_name, removed |
| `structural-20261009-config-fromm2026-af3-iptm` | 1: source_label equals reported_name, removed |
| `structural-20261009-config-fromm2026-af3-pdockq2` | 1: source_label equals reported_name, removed |
| `structural-20261009-config-fromm2026-af3-ptm` | 1: source_label equals reported_name, removed |
| `structural-20261009-config-fromm2026-af3-ranking-confidence` | 1: source_label equals reported_name, removed |
| `structural-20261009-config-smorodina2026-af3` | 1: source_label equals reported_name, removed |
| `structural-20261009-config-smorodina2026-boltz1` | 1: source_label equals reported_name, removed |
| `structural-20261009-config-smorodina2026-boltz2` | 1: source_label equals reported_name, removed |
| `structural-20261009-config-smorodina2026-chai1` | 1: source_label equals reported_name, removed |
