# Retrieval log

All times UTC, 2026-10-14. Extraction by a Claude (Opus 5.5) agent; no review yet.

1. 11:53 to 11:57. Europe PMC `fullTextXML` for PMC12652071 (Hegde), PMC11810778 (Nucleotide Transformer) and PMC12851941 (AlphaGenome). The MDPI PDF for Hegde returned a 408-byte error page, so the XML is the source. arXiv PDF 2306.15794v2. HyenaDNA model card and GitHub README (HazyResearch/hyena-dna at d553021, used only to find the card). AlphaGenome supplement and README, whose hashes match the stored source records.
2. 11:54 to 11:55. OpenReview PDF for NUleWh1GFx (Saadat and Fellay). Two attempts returned 12,692 and 11,910 bytes that are not a PDF. Recorded as a gap.
3. 11:58. Aspidova et al. 2026 bioRxiv v1 PDF (hash matches the stored `model-execution-20261011-source-aspidova2026-moderngena`), read to look for the throughput measurement code.
4. 12:02:25. EVEE bioRxiv v4 PDF (first attempt). EVEE manuscript repository files at e5e4a43 fetched raw from GitHub.
5. 12:03:27 HTTP 429, then 12:05:27 HTTP 200. NTv3 bioRxiv v1 PDF.
6. 12:06. bioRxiv details API for EVEE (versions 1 to 4) and Evo 2 (author list).
7. 12:41 to 12:48. Pinned HyenaDNA card revision via the Hugging Face API (eed1f67) and the GitHub commit (d553021b483b82980aa4b868b37ec2d4332e198a). Re-downloaded the Europe PMC XMLs, the arXiv PDF, the Evo 2 metadata and the four EVEE repository files. Every hash matched the first download, and these times are the `retrieved_at` values. The two bioRxiv PDFs were not re-fetched because of rate limiting.
8. AIRI-Institute/GENA_LM at ed71502f71538ea1e28485381ac94fcae7211818: listed the tree and read README.md, examples/modernGENA/README.md and the moderngena-base model card. No throughput benchmarking script was found.

## How values were read

- Hegde Table A1: parsed from the XML table `genes-16-01358-t0A1`.
- NTv3 Table 5 (page 34) and HyenaDNA Table A.2 (page 17): parsed from `pdftotext -layout` with headers and row labels asserted.
- EVEE Figure 1c and 1d: in the paper the heatmaps are raster images. The Overall rows were read from a 300 dpi render of page 3. The repository's vector PDFs print the same cells in their text layer, and the script asserts that the two match. Column identities come from the pinned plotting code.
- Prose values (EVEE compute, Hegde convergence times, NT fine-tuning times, NTv3 and AlphaGenome statements): each sentence is asserted as an exact substring of the artifact text.

The script is `extract/extract_gfm_guide.py`. It takes a directory holding the artifacts under the file names in its `ARTIFACTS` table, and checks every hash before reading.
