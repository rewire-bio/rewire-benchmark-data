# Batch provenance

Records are not stored here. They live in the canonical store (`data/entities/`, `data/evidence/`), with one provenance line per record in `data/provenance/records.jsonl`.

The batch folders here keep the evidence behind each extraction: review receipts, retrieval logs, source tables, claims sheets, coverage notes and archived source bytes. A record's provenance `added_in` names the batch file it came from. Until 8 October 2026 each batch also held its own record files, and the build assembled the catalogue from them in 30 steps. Those files were folded into the store in one migration and remain in git history. Their receipts still describe the bytes that were reviewed.

The other files here are build inputs or working data:

| Path | Purpose |
| --- | --- |
| `use-cases/` | use-case definitions, mappings and their receipt |
| `audits/` | append-only audit runs, checks and resolutions |
| `releases/` | the current frozen release, plus a receipt for every release |
| `release-config.json` | `released_at` for the current release |
| `search-ledger.jsonl`, `scope-audit.jsonl` | searches run and scope decisions |
| `pending-review/` | extractions not yet ready for the store |
| `baseline-coverage/` | baseline coverage outputs for earlier releases |

See [docs/collection.md](../../docs/collection.md) for how to add a batch.
