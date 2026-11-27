# PLABench depth tier, 2026-11-27

`lit-interactions-20261011-leakctl-benchmark-plabench` was stored at depth tier 3. Batch
`use-case-mapping-proxy-20261127` linked two of its protocols (CASP16 L1000 and L3000 affinity) to
`use-case-lead-optimisation-affinity-ranking`, a tier 2 use case, so the rule in
`shared/omics/depth-tier.ts` now places the benchmark at tier 2 and `npm run depth-tier -- check`
reported the difference. Set with `npm run depth-tier -- backfill`. Reviewer: `claude`; no human review.
