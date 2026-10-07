# Retrieval log — EGFR NSCLC evidence-retrieval bounded ingestion, 2026-10-07

Full dated query log for the underlying research pass is preserved separately in
`docs/omics/evidence-research/egfr-nsclc-evidence-retrieval-2026-10-07.md` (section "Dated query
log (provenance)"). This log records only the retrieval actions specific to this additive intake.

- Fetched `https://www.biorxiv.org/content/10.1101/2025.09.10.675443.full.pdf` at 2026-10-07T09:28:49Z; confirmed v3 (posted 2026-08-29) by in-document header, not by title search alone.
- Attempted `https://www.biorxiv.org/content/10.1101/2025.09.10.675443v3.full.pdf` (explicit versioned URL) at 2026-10-07T09:48Z; received HTTP 429; not retried.
- Queried the bioRxiv API for doi:10.1101/2025.09.10.675443, confirming three versions (v1/v2 2025-09-15, v3 2026-08-29) and `published: NA`.
- Visually inspected Supplementary Figure 2 (printed page 33 / PDF page 34) of the cached v3 PDF to confirm the 150→66→42→40 selection chain and 9/7/24 scored breakdown.
- Confirmed via `gh api repos/creisle/civicfact` that root-level GitHub licence metadata is null and no root LICENSE file exists.
- Confirmed via `gh api "repos/creisle/civicfact/contents/data_builder/LICENSE?ref=1a767d889b015a836f0f4331afcac5cef165ec7f"` that a nested `data_builder/LICENSE` file exists at pinned commit `1a767d889b015a836f0f4331afcac5cef165ec7f` and is GNU GPL version 3 (29 June 2007); confirmed the adjacent `data_builder/pyproject.toml` at the same commit does not declare a licence field. The broad claim that the repository has no LICENSE file is therefore false; only the repository root lacks one.
- Confirmed via existing catalogue records (`data/omics/use-case-coverage-20260930/clinical/records.jsonl`) that CIViC MCP's published article and Zenodo 20938836 archive are already present; no re-fetch performed for this pass.
- Confirmed via `gh issue view 28 --repo rewire-bio/rewire-benchmarks` that the focused execution-gap issue exists and was independently created by Codex after a full title/body dedup check.

Cached bytes (PDF, bioRxiv API JSON, GitHub API responses, Supplementary Figure 2 page renders) remain under the git-ignored `workbench/egfr-20261007/cache/`. Only the compressed v3 PDF is committed, under `clinical/artifacts/civic-fact-v3-biorxiv.pdf.gz`.
