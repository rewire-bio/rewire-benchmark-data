# Retrieval log

All requests were made from the collector's scratch area with Python urllib or curl. No personal identifier was sent; the only email used for an API was the placeholder research-agent@example.invalid (Unpaywall).

1. Europe PMC REST fullTextXML for PMC12627797 (Nature Communications version) downloaded; Tables 3-7 parsed from <td> cells; model labels and header rows asserted.
2. Licence CC BY-NC-ND 4.0: hashed, not archived. Supplementary Information not read.

Re-run the extraction with:

```sh
python3 -I extract/extract_dnalongbench.py <fulltext.xml> <batch-folder>
```

`extract/lib.py` holds the shared record builders. The script asserts the artifact hash before parsing.
