# Retrieval log

All requests were made from the collector's scratch area with curl. No personal identifier was sent.

1. Europe PMC search by DOI gave PMC13444443, open access, licence CC BY-NC-ND.
2. `curl -s https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13444443/fullTextXML` returned 200,
   134,124 bytes, SHA-256 `0f57b9b1...`.
3. Table 2 parsed from the XML `<td>` cells: four antigens x four systems, every cell.
4. Table 1 is a feature matrix of prior studies with ticks and crosses, not performance values, and
   was not extracted. Supplementary Document S1 (Figure S1, Tables S1 and S2) was not retrieved, so
   the McNemar chi-squared statistics and the Graphinity before-and-after-fine-tuning accuracies are
   a gap.
5. Retrieval results (Precision@K and retrieval accuracy) are figures only and were not read.

Re-run the extraction with:

```sh
curl -s -o pmc.xml https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13444443/fullTextXML
python3 -I extract/extract_mochibind.py pmc.xml <batch-folder>
```
