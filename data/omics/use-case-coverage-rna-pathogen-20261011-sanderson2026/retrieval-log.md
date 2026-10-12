# Retrieval log: Sanderson et al. 2026, nanopore RNA metagenomics on nasopharyngeal swabs (preprint)

Worker: Claude (Opus 5.5) research agent (uc-pathogens) in Claude Code. No human review claimed. Each download went into its own folder in a session scratch directory and was opened only as data (XML, DOCX or XLSX parsed as text). No classifier, pipeline or model was executed.

Times are UTC on 2026-10-11.

| Time | Request | Result |
| --- | --- | --- |
| 21:38:13 | api.biorxiv.org (medrxiv) details; medRxiv JATS v2 `2026.02.06.26345651.source.xml` | HTTP 200, 101,014 bytes. Pinned. Tables 1 to 3 are images (`graphic` elements) |
| 21:42:00 | ScienceDirect and journalofinfection.com pages for 10.1016/j.jinf.2026.106839 | HTTP 403. Published version not retrieved |

## How the values were read

`extract/extract_sanderson2026.py` locates each Results section by its title, takes the paragraph by position, asserts that the quoted sentence fragment occurs in it and that the printed value occurs in the fragment, then writes the result with the quote in `source_locator`. Table images were not read.

