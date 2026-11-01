# Architecture decision records

An ADR records one decision about how the data or its checks work: the problem, the options that were weighed, and what was chosen and why. It is written before the work and kept after it, so a later reader can see why things are the way they are. Each record is a self-contained HTML page with its diagrams drawn inline; open it in a browser.

An ADR is not edited after it is accepted, except to correct a figure (say so in the page). A later decision that changes it gets a new ADR that names the one it supersedes.

Designs that implement a decision are in [`docs/design/`](../design/).

| ADR | Decision | Status | Design |
| --- | --- | --- | --- |
| [0001](0001-comparable-evidence.html) | Make contested results compare like with like: define system, study, evidence and task scope in the data and the discrepancy rules (#201, #204 to #208) | Accepted 2026-10-23, option B | [Discrepancy rules version 4](../design/discrepancy-rules-v4.html) |
