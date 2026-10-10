# Retrieval log: structural hypotheses use-case pass, 2026-10-09

Worker: Claude (Opus 5.5) research agent in Claude Code. No human review claimed. Downloads went to a session scratch directory, one folder per source, and were read as data (JATS XML parsed with `xml.etree` under `python3 -I`). No structure prediction was run.

Times are UTC; `~` marks times taken from command order rather than recorded.

| Time | Request | HTTP | Bytes | Result |
| --- | --- | --- | --- | --- |
| ~21:15 | web search for Runs N' Poses | | | Lead found; query text reconstructed after a context reset |
| ~21:19 | `GET biorxiv.org/content/early/2025/08/04/2025.02.03.636309.source.xml` | 429 | 17 | Cloudflare 1015; retried twice, same result |
| 21:20:40 | `GET europepmc .../PPR976473/fullTextXML` | 500 | 149 | No preprint full text |
| ~21:21 | `GET api.biorxiv.org/details/biorxiv/10.1101/2025.02.03.636309` | 200 | | Versions 1 to 3, CC BY; published as 10.1038/s41594-026-01797-5 |
| ~21:21 | `GET api.github.com/repos/plinder-org/runs-n-poses` and tree at `197fafc6` | 200 | | Apache-2.0; example inputs and outputs only, no result tables |
| ~21:21 | `GET nature.com/articles/s41594-026-01797-5` | 200 | 422,808 | Subscription article; supplement is figures and one table of clusters |
| 21:21:48 | `GET europepmc .../search` (antibody query, ledger q3) | 200 | | 66 hits |
| 21:21:58 | `GET europepmc .../PMC13061134/fullTextXML` | 200 | 107,528 | Fromm et al. 2026; extracted |
| ~21:22 | `GET europepmc .../PMC12750043`, `PMC13557113`, `PMC12360200` full text | 200 | | Screened |
| 21:22:26 | `GET europepmc .../search` (ligand query, ledger q4) | 200 | | 112 hits |
| ~21:23 | `GET europepmc .../PMC12851923`, `PMC13476267` full text; PoseBench supplement PDF | 200 | ; 1,832,231 | Screened; supplement has no result tables and was deleted |
| ~21:23 | CASP16 Table S1 via `europepmc.org/articles/.../bin/` and `pmc.ncbi.nlm.nih.gov` | 403, 200 | 5,585; 1,816 | HTML challenge pages, not the workbook |
| ~21:24 | `GET europepmc .../PMC12750043/supplementaryFiles` | | | Stalled at 12 MB; stopped and deleted |
| 21:25:41 | `GET europepmc .../search?query=EXT_ID:PPR1221387` and `api.biorxiv.org/details/biorxiv/10.64898/2026.03.02.709004` | 200 | | Smorodina et al.; version 1 only, CC BY |
| 21:25:48 | `GET europepmc .../PPR1221387/fullTextXML` | 200 | 162,618 | Smorodina et al. 2026; extracted |
| ~21:26 | `GET biorxiv.org/content/early/2026/03/03/2026.03.02.709004.source.xml` | 429 | 17 | Cloudflare 1015 |
| 21:26:15 | `GET europepmc.org/articles/PPR1221387/bin/EMS215481-supplement-*` (4 files) | 403 | 5,699 each | Browser challenge; not read |
| ~21:28 | web fetch of the Runs N' Poses v3 full-text HTML | 200 | | Per-method values are figure-only; excluded |
| ~21:29 | web search for independent protein-ligand pose tables (ledger q6) | | | Nothing beyond FoldBench |

## How each value was read

All parsing is in `extract/extract_structural.py`.

- **Fromm et al. Table 1** (`table-wrap` `btag136-T1`): asserts the caption, the header `Method, <DockQ>, R, <R>`, the nine row labels in order and three values of the form `d.ddd` per row. 27 results. The paragraphs that fix the dataset, the sampling (40 seeds x 5 samples) and the table discussion (`DockQ = 0.35, versus 0.54`) are asserted to be present.
- **Smorodina et al. Results text**: each value comes from one regular expression over one paragraph, identified by its JATS `id` (P11, P19, P21, P36), and each pattern must match. 23 results. Checks: the discussion's rounded change correlations (-0.03, -0.04, -0.02) equal the Results values (-0.027, -0.040, -0.019) to two decimals; each printed Δ equals the difference of the printed medians, except AF3, which differs by 0.01 and is recorded as rounding; the train and test counts per tool, the training-cutoff sentence, the curation sentence, the negative-definition sentence and the three version sentences each appear exactly once.
- **FoldBench**: no values read. The two judgements cite the stored protocols and evaluations.
