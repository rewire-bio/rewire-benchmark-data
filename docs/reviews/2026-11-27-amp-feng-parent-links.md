# Parent links for the amp-feng-20261007 configurations, 2026-11-27

Reviewer: `claude`, the agent that made the change. No human review. An independent verification pass
is needed before merge.

All 79 configurations of batch `amp-feng-20261007` (Feng et al., the DNA foundation model comparison)
record the model they ran in `reported_name` and have no `configuration_of` link, so every board fits
them as systems with no model and ranks none of them
(`docs/reviews/2026-11-27-use-case-mapping-gaps.md`, section 4). This change adds the link to 36 of
them, in `data/omics/amp-feng-parent-links-20261127/` with `evidence.jsonl` giving, for each link, the
configuration, its reported name, the parent chosen and why.

| Reported name | Configurations | Parent | Basis |
| --- | --- | --- | --- |
| GROVER | 9 | `lit-genomics-20261011-geneb-model-grover` | The only record of that name |
| HyenaDNA | 9 | `regulatory-variant-20261009-model-hyenadna` | The only model record of that name; 30 other configurations link to it |
| DNABERT-2 | 9 | `discovery-model-dnabert-2` | Two model records carry the name; 33 other configurations link to this one and 1 to `catalog-model-dnabert-2` |
| NT-v2 | 9 | `catalog-model-nt-v2` (Nucleotide Transformer v2) | An alias, not an exact name: 27 of the 28 other NT-v2 configurations link here |

Every other record matching one of these names exactly is a study-local `pipeline` record (MIMIC
mRNABench, Gene-MTEB, mRNABench variants, a paper's dagger-marked rows), not a parent.

Left alone, 43 configurations whose reported names are qualified ("Enformer, output tracks\*",
"Caduceus-Ph, long sequence", "HyenaDNA-450K, long sequence", "Sei, hidden states\*") or have no model
record ("Caduceus-Ph"). Each needs a judgement about which checkpoint or output head was run; the
parent model exists for Enformer, Sei, AlphaGenome, Caduceus and HyenaDNA.

Two findings for the store: DNABERT-2 has two model records (`discovery-model-dnabert-2` and
`catalog-model-dnabert-2`), and the configuration links in this batch, like 1,803 others, have no
reviewed association claim (rewire-benchmark-data#163).
