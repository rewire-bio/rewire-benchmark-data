# Retrieval log

All requests were made from the collector's scratch area with curl or Python urllib. No personal identifier was sent; the only email used for an API was the placeholder research-agent@example.invalid (Europe PMC).

1. bioRxiv API details for 10.1101/2025.06.16.660049: RNAGym preprint v1, 2025-06-17, CC BY-NC-ND, out of the search window. Not extracted.
2. GitHub API: repository search 'RNAGym' found MarksLab-DasLab/RNAGym; latest commit on main is 2828cf99316d75daaa8d832a2573cbb25bbd35fe (2026-08-14). Tree listed recursively.
3. raw.githubusercontent.com at that commit (2026-10-11T21:40:04Z): `leaderboard/fitness/README.md` (SHA-256 `c947a7a45a53cc4106323a3bcae1bb3fa84276bc07df89493cb501735711b891`), `leaderboard/fitness/leaderboard_signed_3ncRNA.csv` (`b72459e550a4daac53459b002b7f38246185dc50647656c104a56a98882f3a99`), `leaderboard/fitness/aido_rna_scaling.csv` (`c5b2e3f573a10036c2fb35118be363e5433af0150d00e8447ef534b2d36a7949`), `LICENSE` (MIT, `343d286cf6e50f4737a328eb17093142bed1c09050ea55c4f189ac90f011fb77`) and the root `README.md`.
4. The two Markdown tables of the leaderboard README were parsed; each printed value was asserted equal to the matching CSV value rounded half-even to four decimals. All 64 matched.

Re-run the extraction with:

```sh
python3 -I extract/extract_rnagym.py <README.md> <leaderboard_signed_3ncRNA.csv> <aido_rna_scaling.csv> <batch-folder>
```
