# Retrieval log

All requests were made from the collector's scratch area with Python urllib or curl. No personal identifier was sent; the only email used for an API was the placeholder research-agent@example.invalid (Unpaywall).

1. Listed the 156 metric CSVs under {mendelian,complex}_traits_matched_9/AUPRC_by_chrom_weighted_average/all/ with the Hugging Face tree API at revision 1fde1955 and downloaded each from the resolve endpoint (no token).
2. Bundled every CSV (path, SHA-256, bytes) into one JSON file; its SHA-256 is the source hash. Archived as artifacts/traitgym-metrics-bundle.json.gz (MIT licence).
3. README read at GitHub commit 4d80fe88 for the metric definitions; the bioRxiv v2 PDF read for model checkpoints (Table S5) and the evaluation metric.

Re-run the extraction with:

```sh
python3 -I extract/extract_traitgym.py <hf-folder> <batch-folder> <bundle.json>
```

`extract/lib.py` holds the shared record builders. The script asserts the artifact hash before parsing.
