# Identity candidates

Generated 8 October 2026 by `npm run identity:candidates`. Not reviewed. No record has been linked or merged.

Records were grouped by kind and normalised name. Groups where every member already links to the same parent model, or where an alias link already exists, are left out. 362 groups remain:

| Finding | Groups | Proposal |
| --- | --- | --- |
| Source records with the same artifact hash | 136 | `alias_of` the shortest ID; the hash is the evidence |
| Configurations or pipelines where some members have no parent model | 198 | `family` link where exactly one sibling parent is known (3), otherwise review |
| Models, methods, tasks and datasets with the same name and no alias link | 18 | review |
| Sources with the same title but different URL or bytes | 10 | review |

Same name does not mean same thing. Configurations are deliberately source-specific: a score belongs to the exact setup that produced it, and configurations of one model share a `family` link rather than one ID. Never move results between records.

## Reviewing

Fill `decision` (`link`, `keep separate` or `unsure`), `reviewer` and `notes` for each row. For each accepted link:

1. Add the link (`alias_of` or `family`) to the record, and a `claim` record backing it (`field: "links:<relation>:<target>"`, `target_id`, `source_locator`, `review`, with a `subject` link). Relationships count in navigation only when a claim backs them.
2. Run `npm run records -- change <dated review> data/omics/pending-review/identity-candidates <ids>` for the edited records, and `npm run records -- add` for the new claims.
3. Rerun `npm run identity:candidates` to refresh this list.
