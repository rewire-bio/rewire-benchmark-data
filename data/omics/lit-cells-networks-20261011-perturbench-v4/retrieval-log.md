# Retrieval log

All requests used curl from the collector's scratch area. No personal identifier was sent to any service.

1. arXiv export API for 2408.10609: v4 posted 2025-10-24 (inside the 2025-10-01 to 2026-10-11 window); v1 is already in the store as evidence-expansion-perturbench-5c480456 with 76 results from Tables 2-3.
2. `curl -sSL -o 2408.10609v4.html https://arxiv.org/html/2408.10609v4` at 2026-10-11T21:29:35Z; SHA-256 above.
3. Parsed with `python3 -I extract/extract_perturbench_v4.py <2408.10609v4.html> <batch-folder>`. The script asserts the file hash, finds the 22 `ltx_table` figures, asserts each result table's header and row count, normalises math-bold digits (the best-in-column marks) to plain digits, converts '± m × 10 − k' to a decimal standard deviation, skips cells printed as '-', and asserts the per-table cell counts (340 in total).
