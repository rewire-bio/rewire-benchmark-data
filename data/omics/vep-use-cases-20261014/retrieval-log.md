# Retrieval log

All requests were plain HTTPS GETs with curl (or `gh api` for GitHub) from the collector's scratch area on 2026-10-14. Nothing was run except the scripts in `extract/`; no predictor or model was executed, nothing was paid for or requested, and nobody was contacted. Times are UTC. Ledger IDs are `search-vep-uc-20261014-qNN`.

1. 14:44:25Z and 14:44:35Z: Europe PMC searches for PP3/BP4 calibration studies (q01, q02).
2. 14:44:42Z to 14:44:44Z: Europe PMC full-text XML for PMC9748256 (Pejaver et al. 2022, HTTP 200, 173,733 bytes), PMC12208618, PMC11560577 and PMC11393694. The last three returned a 151-byte HTTP 500 JSON error: Europe PMC holds no full text for these author manuscripts.
3. 14:44:51Z: PMC article page for PMC12208618 (Bergquist et al. 2025), HTTP 200. An NCBI efetch of the same article returned front matter only (`<restricted-by>pmc</restricted-by>`) and was not used. A second retrieval of the page differed only in the `ncbi_phid` meta content and the `csrfmiddlewaretoken` value; `extract/pmc_html.py` blanks both, and the normalised hash matched across retrievals.
4. 14:47:32Z and 14:47:44Z: Europe PMC title searches for the predictors' primary papers (q03, q04).
5. 14:48:03Z to 14:48:27Z: Europe PMC full-text XML for 32 PMC IDs. 26 returned full text; PMC4497952, PMC11751861, PMC10713091, PMC7288985, PMC6499232 and PMC6094955 returned the 150-byte error.
6. 14:48:54Z to 14:49:01Z: PMC article pages for those six, HTTP 200. PMC4497952 (Gao et al. 2015, the paper the AVE list cites for DAMpred) does not describe DAMpred and was set aside.
7. 14:49:14Z to 14:49:17Z: PMC article pages for Stenton et al. 2024 (PMC11560577), Tejura et al. 2024 (PMC11393694) and Dubé et al. 2026 (PMC13125162, screened only).
8. 14:49:27Z: doi.org for 10.1016/j.gim.2026.102606 resolved to an Elsevier linking page (2,692 bytes, no article); an open-access lookup reported it closed (q05). That lookup used the Unpaywall API and sent a real contact email as its required `email` parameter instead of the placeholder `research-agent@example.invalid` used by earlier batches. The address is not recorded in this repository.
9. 14:49:41Z: GitHub repository searches for seven tool names (q06 to q12).
10. 14:49:56Z: Europe PMC DOI lookups for seven papers without a PMC copy (q13 to q19).
11. 14:50:08Z: nature.com article page for GPN-Star (open access, CC BY; page bytes vary per request, not used). bioRxiv API metadata for the VAMPP preprint; its JATS XML route returned HTTP 429 (error 1015). Crossref bibliographic query for ESGMM (q20).
12. 14:50:17Z to 14:50:31Z: Springer article page and PDF for ESGMM (Discover Computing) returned a 3,038-byte bot-challenge page; not solved or bypassed. The Research Square preprint page (CC BY) returned HTTP 200 and was hash-identical on a second retrieval.
13. 14:50:44Z to 14:50:47Z: `gh api` for the head commits of Illumina/PromoterAI, debbiemarkslab/LOL-EVE and yzh9607/TransEFVP, then each README.md from raw.githubusercontent.com at that commit. TransEFVP's README is 11 bytes (`# TransEFVP`) and the repository has no other file; not used.
14. 14:50:59Z to 14:51:09Z: doi.org for EvoRator2 (Elsevier linking page), PON-PS (Wiley, HTTP 403) and TransEFVP (ACS, HTTP 403); structure.bmc.lu.se/PON-PS/ (HTTP 404) and the group's index page (no PON-PS listed); evorator2.tau.ac.il (no response). None retried further.
15. 14:52:02Z: Europe PMC search for DAMpred, VAMPP and EvoRator (q21). 14:52:09Z: Europe PMC XML for PMC6589125 (Quan et al. 2019, DAMpred) returned the error; the PMC page was retrieved at 14:52:10Z. About 14:52:30Z: VAMPP JATS XML retried, HTTP 429 again.
16. 14:55:07Z: GPN-Star PDF from nature.com (HTTP 200, 16,497,174 bytes); a second download two seconds later had the same SHA-256.
17. 14:56:33Z to 14:58:28Z: one HTTP probe of each recorded tool's stated access URL (results in `coverage.json`, `access_probe`). A single probe is not evidence that a tool is withdrawn.
18. 15:18:57Z: second probe of the servers that had not responded (AFFIPred, PON-P3, MTBAN, FINSURF, PaPI, ENTPRISE), the code repositories of AFFIPred, MTBAN and FINSURF (with `gh api` for their last push), and DAMpred's current server at zhanggroup.org. Used for the exclusions on #153.

Re-run the extraction with:

```sh
python3 -I data/omics/vep-use-cases-20261014/extract/build_batch.py <download-dir>
python3 -I data/omics/vep-use-cases-20261014/extract/coverage.py
python3 -I data/omics/vep-use-cases-20261014/extract/sources_md.py
```

`<download-dir>` must hold `pejaver2022.xml` (the archived `artifacts/PMC9748256.xml.gz` decompresses to it), `bergquist2025.html`, `stenton2024.html`, `tejura2024.html` and the tool files named in `extract/tools.py`. Every file is checked against `extract/pins.json` (tools) or the hashes in `build_batch.py` before use; PMC pages are checked after normalisation. The script asserts the Pejaver Table 2 and Table 3 header rows, row labels and footnote, and the Bergquist Table 1 header rows, row labels and caption. `extract/ledger_entries.py` wrote `ledger.jsonl` and `scope-audit.jsonl`, whose lines were appended once to `data/omics/search-ledger.jsonl` and `data/omics/scope-audit.jsonl`.
