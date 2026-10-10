# Retrieval log: Kaschta et al. reanalysis follow-up, 2026-10-10

Worker: Claude (Opus 5.5) research agent in Claude Code. No human review claimed. Downloads went to a session scratch directory and were parsed as XML only.

| Time (UTC) | Request | HTTP | Bytes | Result |
| --- | --- | --- | --- | --- |
| 06:04:29 | `GET https://api.medrxiv.org/details/medrxiv/10.64898/2026.05.16.26352295` | 200 | 2,057 | Metadata: v1, 2026-05-19, licence `cc_no`, JATS URL |
| 06:04:35 | `GET https://www.medrxiv.org/content/early/2026/05/19/2026.05.16.26352295.source.xml` | 200 | 108,323 | JATS XML with three figures, Table 1 as an image, and a supplement reference |

The supplement was not requested.

## How values were read

`extract/jats_paras.py` lists the abstract and body paragraphs with a locator made of the section path and the paragraph number within that section (counting `<p>` elements directly inside the section). `extract/extract_kaschta.py` defines each result as (section, paragraph number, exact quoted phrase, printed value) and asserts that the phrase occurs in that paragraph and the value in the phrase. All 27 values come from prose; Table 1 (image), figures and figure legends were not used for values. The figure 2 legend is quoted only to record its conflicting 9.6%.

Run: `python3 -I extract/extract_kaschta.py <jats-xml> <batch-dir>`.
