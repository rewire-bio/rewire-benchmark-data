# Architecture decision records

An ADR records one decision about how the data or its checks work: the problem, the options that were weighed, and what was chosen and why. It is written before the work and kept after it, so a later reader can see why things are the way they are. Each record is a self-contained HTML page with its diagrams drawn inline; open it in a browser.

An ADR is not edited after it is accepted, except to correct a figure (say so in the page). A later decision that changes it gets a new ADR that names the one it supersedes.

Designs that implement a decision are in [`docs/design/`](../design/).

| ADR | Decision | Status | Design |
| --- | --- | --- | --- |
| [0001](0001-comparable-evidence.html) | Make contested results compare like with like: define system, study, evidence and task scope in the data and the discrepancy rules (#201, #204 to #208) | Accepted 2026-10-23, option B | [Discrepancy rules version 4](../design/discrepancy-rules-v4.html) |
| [0002](0002-claim-extraction.html) | Extract and check claims and values deterministically first, address every claim to a span in a hashed text layer, and run one model stage behind a byte-span check (#228) | Proposed 2026-11-17. Figures corrected 2026-11-18: locator parse coverage, the distinction between a locator that parses and one that resolves to bytes, what the layer registry and the table grids actually built, and the step 5 estimate | |
| [0003](0003-source-preservation.html) | Preserve every source as two identities, publish by licence tier, rescue by citation weight; corrects the no-derivatives storage rule in `docs/collection.md` | Proposed 2026-11-17. Superseded in part 2026-11-17: the store is recollected from the primary sources, so the two-identity scheme, the drift and re-pinning apparatus and the citation-weight waves are dropped, while the receipt, the licence tiers, the text layer and the manifest stand | [Preserving source bytes](../source-preservation.md), the policy in force |
| [0004](0004-storage-substrate.html) | Keep the canonical store as JSONL in git, evict binaries to a content-addressed archive, and add a warehouse only when a named consumer exists | Proposed 2026-11-17 | |
| [0005](0005-run-recipes.html) | Give models and benchmarks an evidenced, executable how-to that promotes into an independent run | Proposed 2026-11-17 | |
