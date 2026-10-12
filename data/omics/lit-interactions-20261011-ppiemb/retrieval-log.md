# Retrieval log

All requests were made from the collector's scratch area with curl. No personal identifier was sent.

1. Europe PMC search by DOI gave PMC13280947, open access, licence CC BY-NC.
2. `curl -s https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13280947/fullTextXML` returned 200,
   302,811 bytes, SHA-256 `360d4f17...`.
3. Tables 5 (Hits@100) and 6 (Accuracy) parsed from the XML `<td>` cells, every cell: seven GNN or
   MLP rows x eleven feature columns x two datasets x two metrics.
4. Supplementary Tables S1 to S7 (datasets, the original OGBl-ppa leaderboard values, and the
   embedding and GNN hyperparameters) were not retrieved, so no model version or checkpoint is
   recorded.
5. One HuRI row in Table 5 is laid out without the leading empty cell and with a trailing empty one;
   the parser normalises that and still asserts eleven values per row.

Re-run the extraction with:

```sh
curl -s -o pmc.xml https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13280947/fullTextXML
python3 -I extract/extract_ppiemb.py pmc.xml <batch-folder>
```
