# Retrieval log

All requests were made from the collector's scratch area with curl or Python urllib. No personal identifier was sent; the only email used for an API was the placeholder research-agent@example.invalid (Europe PMC).

1. Europe PMC REST fullTextXML for PMC12963973 (2026-10-11T21:27:04Z). Main text; all benchmark values are in figures there.
2. Europe PMC supplementaryFiles archive for PMC12963973 (2026-10-11T21:27:04Z, zip SHA-256 `560f481026da87f357bebfb9196019dc38aae7472ba0257577098ed9371f12c5`). Contains `bbag098_supplymentary_information_20260209.docx` (SHA-256 `c8fc78c3d8538c9431fc0448a4068a7643dfb7d74558877fd40b36feba71e214`) and figure images.
3. The .docx was read as a zip; `word/document.xml` paragraphs and tables were walked in order, and each table was keyed by the 'Supplementary Table N.' caption paragraph before it. Supplementary Tables 4-11 were parsed; Table 1 gave download locations and versions; Tables 2-3 are descriptive.
4. Header rows asserted for every table. Group rows (DNA LMs, Class I-III RNA LMs) are skipped after checking they are empty.

Re-run the extraction with:

```sh
python3 -I extract/extract_rnalm_zeroshot.py <PMC12963973 fullTextXML> <bbag098_supplymentary_information_20260209.docx> <batch-folder>
```

The script asserts both hashes before parsing. `extract/lib.py` holds the shared record builders.
