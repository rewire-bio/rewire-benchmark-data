# Retrieval log

All requests were made with curl from the collector's scratch area on 2026-10-14. No personal identifier was sent.

1. Europe PMC search for DOI 10.1038/s41587-024-02511-w: found PMID 39747647, not open access, not in PMC.
2. Europe PMC and the bioRxiv API for DOI 10.1101/2023.10.10.562811 (the DOI in the issue): no record. Crossref returned "Resource not found".
3. Crossref title search for "GPN-MSA alignment-based DNA language model": DOI 10.1101/2023.10.10.561776. The bioRxiv API for that DOI lists v1 (2023-10-11) and v2 (2024-04-06), licence cc_by_nc_nd, published as 10.1038/s41587-024-02511-w.
4. Downloaded the v2 JATS XML (12:01:39Z). Its tables are images.
5. Downloaded the v2 full-text PDF (12:02:16Z, 37 pages) and converted it with `pdftotext -layout` (poppler 26.08.0).
6. Fetched the Nature article page and the Extended Data Table 1 page (12:02). The article is paywalled; Extended Data Table 1 is an image. Neither was read for values.
7. GitHub API: songlab-cal/gpn default branch main at commit dc5fd287599f2955a79d010bca0e0f7f8178c67e (2026-09-26), licence MIT. Downloaded README.md (12:05:43Z) and docs/models/gpn-msa.md (12:06:06Z) from raw.githubusercontent.com at that commit; found the doc path from the recursive git tree at the commit.

Re-run the extraction with:

```sh
pdftotext -layout v2.pdf v2.txt
python3 -I extract/build_gpnmsa.py v2.pdf v2.txt README.md gpn-msa.md <batch-folder>
```

The script checks the SHA-256 of the PDF, README and doc, asserts the Supplementary Table 4 header groups, the 'mean max' header, all 17 row labels and the page (23), and asserts the DMS TADBP sentence verbatim on page 6. It writes `batch.jsonl` and `claims.csv`.
