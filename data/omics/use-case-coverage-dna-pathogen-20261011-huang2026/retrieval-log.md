# Retrieval log: Huang et al. 2026, blood targeted and untargeted sequencing in pneumonia-associated sepsis

Worker: Claude (Opus 5.5) research agent (uc-pathogens) in Claude Code. No human review claimed. Each download went into its own folder in a session scratch directory and was opened only as data (XML, DOCX or XLSX parsed as text). No classifier, pipeline or model was executed.

Times are UTC on 2026-10-11.

| Time | Request | Result |
| --- | --- | --- |
| 22:07:38 | Europe PMC `PMC13584460/fullTextXML` | HTTP 200, 132,579 bytes. Pinned |

## How the values were read

`extract/extract_huang2026.py` parses Table 2 from the XML, asserts the header, the four stratum labels (first row of each group) and the four method labels, and splits each cell into the printed value and the printed interval (U+2212 separator). The p value column is attached to the accuracy result as `reported_p_value`, because the Results tie those p values to accuracy.

