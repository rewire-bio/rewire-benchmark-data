# Retrieval log

All times UTC, 2026-10-13. Extractor: Claude (Opus 5.5) research agent; no human review claimed.

1. 12:37. GitHub API `repos/science-machine/biomlbench`: default branch `main`, MIT licence, `pushed_at` 2025-09-14T17:37:56Z. `commits/main` returned 673f3d8d3462fc6cdcbbd9695fba612b9332ca65.
2. 12:38:10. Downloaded the codeload tar.gz for that commit (1,533,925 bytes), SHA-256 c2397827...ae559. Unpacked into an empty scratch directory. Read README.md (paper link to bioRxiv v2, DOI 10.1101/2025.09.01.673319), experiments/biomlbench_v0.1a.txt (24 task IDs), agents/*/config.yaml, agents/biomni/main.py and the config and description of each in-scope task. A second download later in the session gave the same archive hash.
3. 12:38. bioRxiv API `details/biorxiv/10.1101/2025.09.01.673319`: three versions (2025-09-04, 2025-09-07, 2025-09-28), licence cc_by, `published` NA. `pubs` endpoint: no published version.
4. 12:38:42. Downloaded https://www.biorxiv.org/content/10.1101/2025.09.01.673319v3.full.pdf (HTTP 200, application/pdf, 2,282,513 bytes, 12 pages), SHA-256 875cb351...38b35. Also fetched the v3 JATS XML (82,630 bytes) to check for supplementary files; none are listed, and the supplementary-material page links no media files. The XML was not used for extraction.
5. Converted the PDF with `pdftotext -layout` (poppler, Homebrew). Read the full text. Tables 2 and 4 carry the only printed agent results; Figures 2 to 6 have no printed values.
6. `extract/extract_biomlbench.py` re-checks the PDF and the cited repository file hashes, parses Table 4 from the text layer (header string, 40 rows, block order Penalized then Non-penalized, domain order and agent order asserted), drops the Biomedical Imaging rows, and writes `batch.jsonl` and `claims.csv`. Entity, task and claim records are written by the same script from values transcribed by hand from Sections 3.1 to 3.4, Table 3 and the repository files.
7. `npm run records -- add` was run once to check the batch against the attribute registry, vocabularies and SHACL shapes (passed: 215 records), then the store was restored with `git checkout` so the batch stays out of the store until independent review.
