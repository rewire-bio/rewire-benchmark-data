# Retrieval log

All requests were made from the collector's scratch area with Python urllib or curl. No personal identifier was sent; the only email used for an API was the placeholder research-agent@example.invalid (Unpaywall).

1. leaderboard/leaderboard.json, leaderboard_tasks.json and README.md downloaded from raw.githubusercontent.com at commit 9642d481 (Apache-2.0).
2. The arXiv v4 PDF (2606.04525) was downloaded to check the paper's tables; its main results are figures plus probe-stability tables, already partly in the store from v1.

Re-run the extraction with:

```sh
python3 -I extract/extract_geneb.py <leaderboard.json> <batch-folder>
```

`extract/lib.py` holds the shared record builders. The script asserts the artifact hash before parsing.
