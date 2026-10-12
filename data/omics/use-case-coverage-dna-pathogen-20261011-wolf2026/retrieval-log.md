# Retrieval log: Wolf et al. 2026, prospective plasma mcfDNA sequencing in high-risk paediatric leukaemia

Worker: Claude (Opus 5.5) research agent (uc-pathogens) in Claude Code. No human review claimed. Each download went into its own folder in a session scratch directory and was opened only as data (XML, DOCX or XLSX parsed as text). No classifier, pipeline or model was executed.

Times are UTC on 2026-10-11.

| Time | Request | Result |
| --- | --- | --- |
| 22:07:34 | Europe PMC `PMC13154368/fullTextXML` | HTTP 200, 95,734 bytes. Pinned |

## How the values were read

`extract/extract_wolf2026.py` parses Tables 2 and 3, asserts the two header rows, group labels, period labels and the blank separator rows, and converts the U+00B7 decimal point for `numeric_value` while keeping it in `printed_value`. Each sensitivity equals positive/evaluable to one decimal (checked by hand for all 12).

