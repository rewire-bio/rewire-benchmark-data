"""Write review.json for vep-use-cases-20261014: the receipt fields and the SHA-256 of every other file in the batch folder.

Usage: python3 -I review/receipt.py  (run after review/signoff.py)
"""
import hashlib
import json
from pathlib import Path

BATCH_DIR = Path(__file__).resolve().parent.parent
batch = [json.loads(line) for line in (BATCH_DIR / "batch.jsonl").open()]
sources = {r["id"]: r["attributes"]["artifact_sha256"] for r in batch if r["kind"] == "source"}
sources.update({
    "vep-lit-20261014-source-livesey2025-article": "1735ee461ef192d9de67c914e9ad73d72d8aa255ea0e3479eb68cd8631d99fa2",
    "run-doc-proteingym-readme-md-144fe22b": "321487a8de52c6cfa647a658f61150dd72e0acb0125470524fb94d1f8b23321a",
    "vep-lit-20261014-source-proteingym-clinical-zero-shot-substitutions-auc-summary-144fe22": "fbe453d1aaa6c30a1d0adf610f7fc23c36044a8e2548b178d316777383f8fe93",
    "vep-lit-20261014-source-proteingym-clinical-supervised-substitutions-auc-summary-144fe22": "f2e38aeac2624d87e7a35a5b16bd580de62c24db36973848e1d94ac3ce510359",
    "profile-protocol-proteingym-paper-xml-a58110e0": "a58110e02c3efc8395c534d48630f577c3d45e90d48198b7f9989cf52600b045",
})

RECEIPT = {
    "schema_version": "1.0",
    "method": "automated_source_review",
    "review_methods": ["source-hash-verification", "deterministic-table-parse", "independent-cell-check",
                       "ai-assisted-source-review", "scope-review"],
    "reviewer": "Claude review agent; no human review claimed. Independent Claude (Opus 5.5) review agent, separate from the "
                "extraction agent that built this batch.",
    "reviewed_at": "2026-10-14T16:00:00Z",
    "scope": "Independent review of vep-use-cases-20261014 (extraction head 9a1f0eb): 295 records (173 results, 26 "
             "evaluations, 26 sources, 23 claims, 19 methods, 16 configurations, 4 protocols, 3 models, 2 use cases, 2 "
             "datasets, 1 benchmark). Re-downloaded all 26 sources and matched their SHA-256 (5 PMC pages after blanking two "
             "per-request tokens, checked with an independent normaliser on two downloads each). review/check_values.py, "
             "written independently of the extractor, compared all 173 values with 0 mismatches after proving it on five "
             "seeded errors; 12 values were also checked by hand. The 22 predictor records, the 15 exclusions, the two use "
             "cases, 21 relevance judgements and 2 baseline claims were checked against their sources.",
    "comparison": {"script": "review/check_values.py", "results_checked": 173, "mismatches": 0, "seeded_errors_caught": 5,
                   "by_source": {"pejaver2022-table2": 104, "pejaver2022-table3": 6, "bergquist2025-table1": 63}},
    "manual_sample": {"seed": 20261014, "results": [
        "vep-uc-20261014-result-pejaver2022-polyphen2-pp3-supporting", "vep-uc-20261014-result-bergquist2025-revel-plus4",
        "vep-uc-20261014-result-bergquist2025-revel-minus2", "vep-uc-20261014-result-pejaver2022-mutpred2-pp3-supporting",
        "vep-uc-20261014-result-pejaver2022-revel-bp4-supporting", "vep-uc-20261014-result-pejaver2022-phylop-pp3-strong",
        "vep-uc-20261014-result-pejaver2022-devlr-sift", "vep-uc-20261014-result-pejaver2022-sift-pp3-strong",
        "vep-uc-20261014-result-pejaver2022-ea-pp3-supporting", "vep-uc-20261014-result-pejaver2022-devfraction-sift",
        "vep-uc-20261014-result-pejaver2022-polyphen2-bp4-strong", "vep-uc-20261014-result-pejaver2022-ea-pp3-strong"],
        "mismatches": 0},
    "limitations": [
        "Automated review by a Claude agent; not human scientific review and not reproduction of any result.",
        "Figures and supplements (Pejaver Table S1, Data S1 and S2; Bergquist Supplementary Material) were not read.",
        "Relevance judgements are reviewed decisions, not facts from a source. Values of evaluations already in the store "
        "were not re-checked here.",
        "PMC page hashes describe the 2026-10-14 retrievals of a mutable website.",
    ],
    "corrections": [
        "PMC source hash_scope: records the page as a mutable website instead of saying a re-download hashes the same.",
        "Bergquist BayesDel and VEST4 evaluations: origin author_reported (was independent_paper).",
        "Bergquist protocol and judgement: carried-over rows, 3-point check, shared limitations, Very Strong caption conflict.",
        "Bergquist results with a value: uncertainty missing reason unextracted (was unreported).",
        "gnomAD-fraction protocol and results: metric_direction unknown (was lower).",
        "Judgement limitations revised on 14 judgements; the #152 Livesey DMS-trained VEP limitation corrected.",
        "See docs/reviews/vep-use-cases-2026-10-14-review.md.",
    ],
    "errors": [],
    "review_document": "docs/reviews/vep-use-cases-2026-10-14-review.md",
    "batch_sha256_before_review": "277d103f76bd9956f9d03bb902cb6ac27af99b88315050728d3cedc3c99c8f39",
    "source_artifacts": sources,
    "archived_artifacts": {"artifacts/PMC9748256.xml.gz": {
        "gzip_sha256": "28bb3e751d79727adf066ff165597ee76eb8ff6e03f8ccd9aca6e419ff899d0c",
        "raw_sha256": "a78c7bcaacb0ccb72291264bbe7c1f9a16867b0c6207dcbb45c3c59a14af6b3b"}},
}

files = {}
for p in sorted(BATCH_DIR.rglob("*")):
    if p.is_file() and p.name != "review.json" and "__pycache__" not in p.parts:
        files[str(p.relative_to(BATCH_DIR))] = hashlib.sha256(p.read_bytes()).hexdigest()
RECEIPT["files"] = files
(BATCH_DIR / "review.json").write_text(json.dumps(RECEIPT, indent=2, ensure_ascii=False) + "\n")
print(len(files), files["batch.jsonl"])
