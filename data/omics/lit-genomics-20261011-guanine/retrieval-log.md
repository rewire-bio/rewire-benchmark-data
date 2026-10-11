# Retrieval log

All requests were made from the collector's scratch area with Python urllib or curl. No personal identifier was sent; the only email used for an API was the placeholder research-agent@example.invalid (Unpaywall).

1. Europe PMC REST fullTextXML for PMC13501288 downloaded with urllib (no email or identifier sent).
2. Supplementary files zip from the Europe PMC supplementaryFiles endpoint: contains btag427_supplementary_data.pdf (2,936,070 bytes), a 'Microsoft: Print To PDF' scan with no text layer. Not read; values in it were not extracted.
3. Publisher page (academic.oup.com) returned HTTP 403; Unpaywall (placeholder email research-agent@example.invalid) listed no direct PDF URL. The blue colouring that marks previously reported Table 2 cells could therefore not be checked.
4. Tables 2, 3 and 4 parsed from the XML <td> cells; header rows asserted. Row label, Reg., Eval. and Context columns become configuration parameters.

Re-run the extraction with:

```sh
python3 -I extract/extract_guanine.py <fulltext.xml> <batch-folder>
```

`extract/lib.py` holds the shared record builders. The script asserts the artifact hash before parsing.
