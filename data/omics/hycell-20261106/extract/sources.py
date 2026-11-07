"""Source records for the HyCell batch."""

B = "hycell-20261106"
COMMIT = "0dcc533cc9f8f76c90ecbfe944df816b6672328a"
RAW = f"https://raw.githubusercontent.com/Tencent-Hunyuan/Hyra-results/{COMMIT}"
BLOB = f"https://github.com/Tencent-Hunyuan/Hyra-results/blob/{COMMIT}"
PDF_SHA = "dc2cacf87ffae8525e81fede1b01f261d3a49cece9061465c36ad1fac6680a28"

SRC_REPO = "hyra-results-20261106-source-repository-readme"  # reused
SRC_LICENSE = "hyra-results-20261106-source-repository-licence"  # shared, neutral ID
SRC_REPORT = f"{B}-source-report"
SRC_README = f"{B}-source-model-readme"
SRC_NOTICE = f"{B}-source-notice"
SRC_CITATION = f"{B}-source-citation"
SRC_PYPROJECT = f"{B}-source-pyproject"
SRC_SIDECAR = f"{B}-source-weights-sidecar"
SRC_WEIGHTS = f"{B}-source-weights"
AREAS = ["single-cell", "cells-tissues"]


def record(rid, kind, name, description, attributes, links=None, sources=None, facets=None):
    return {"id": rid, "kind": kind, "name": name, "description": description,
            "status": "needs_review",
            "facets": facets if facets is not None else {"areas": AREAS, "contexts": ["research"]},
            "source_ids": sources if sources is not None else [SRC_REPORT],
            "links": links or [], "attributes": attributes}


def text_source(rid, name, description, path, sha, retrieved, licence, media, kind, extra):
    attrs = {"url": f"{BLOB}/{path}", "artifact_url": f"{RAW}/{path}",
             "version": f"GitHub repository Tencent-Hunyuan/Hyra-results at commit {COMMIT}",
             "retrieved_at": retrieved, "artifact_sha256": sha,
             "publication_status": "official_project_source", "licence": licence,
             "media_type": media, "source_type": kind}
    attrs.update(extra)
    links = [{"relation": "companion_of", "target_id": SRC_REPORT}]
    return record(rid, "source", name, description, attrs, links=links, sources=[])


def concern(message, locator, applies_to):
    return {"source_id": SRC_REPORT, "message": message, "source_locator": locator,
            "artifact_sha256": PDF_SHA, "reviewed_at": "2026-11-06T11:42:12Z",
            "review_method": "ai-assisted-source-review", "applies_to": applies_to}


REPORT_LIMITS = [
    "Author-released report, not peer reviewed. The developer of HyCell ran every model, so no "
    "result is independent of the developer.",
    "No uncertainty is printed anywhere in the report: no interval, standard deviation or test for "
    "any score, including the 0.735 against 0.736 comparison with Stack.",
    "The comparators do not run under equal conditions. Stack encodes sets of 256 cells with the "
    "cells of each batch together, so it uses batch labels at inference; SCimilarity and scPRINT are "
    "trained with cell-type labels; PCA is fitted to each evaluation atlas on 2,000 highly variable "
    "genes. HyCell embeds each cell from its own counts with no batch or donor information.",
    "The benchmark measures cell-level tasks only. Stack draws on the other cells of a sample at "
    "inference, which the report says helps sample-level tasks such as predicting a donor's disease "
    "state; such tasks are not in the benchmark.",
    "The composite S = 0.3 Bio + 0.2 Batch + 0.25 LR + 0.25 kNN is the authors' chosen weighting. "
    "Table 4 prints only S per atlas, not its four components per atlas, so the per-atlas weighting "
    "cannot be checked.",
]
CONCERNS = []  # see notes.md: no finding here makes a printed value unreliable


def sources():
    t0, t1, t2 = "2026-11-06T11:42:11Z", "2026-11-06T11:45:18Z", "2026-11-06T11:45:37Z"
    return [
        record(SRC_REPORT, "source",
               "HyCell: a Compact Embedding Model for Single-Cell Transcriptomes (Hyra Team, 2026-11-01)",
               "Technical report for HyCell, with its architecture and training, a benchmark of frozen "
               "embeddings of eleven models on seven held-out atlases, downstream analyses and "
               "fine-tuning.",
               {"url": f"{BLOB}/AI4Science/hycell/paper/HyCell_Technical_Report.pdf",
                "artifact_url": f"{RAW}/AI4Science/hycell/paper/HyCell_Technical_Report.pdf",
                "version": f"Dated 2026-11-01 on page 1; retrieved at commit {COMMIT} (9 pages)",
                "version_note": "The report is dated 2026-11-01 on page 1. The PDF's CreationDate and "
                                "ModDate are both 2026-11-02T00:14:59+08 (pdfTeX-1.40.29), which is "
                                "2026-11-01T16:14:59Z, the same day in UTC. The printed date is what "
                                "version records. No earlier PDF exists at the pinned commit, so "
                                "whether a rebuild changed any content was not checked.",
                "retrieved_at": t0, "artifact_sha256": PDF_SHA,
                "publication_status": "official_project_source",
                "licence": "Apache-2.0 (repository LICENSE)", "media_type": "application/pdf",
                "source_type": "vendor technical report",
                "extraction_method": "pdftotext -layout text layer, parsed by extract/parse.py with "
                                     "every row label and cell count asserted.",
                "archive_note": "The PDF is not committed: it is refetchable at the pinned commit and "
                                "extract/parse.py refuses other bytes. Its gzipped text layer is "
                                "artifacts/HyCell_Technical_Report.txt.gz.",
                "archive_sha256": "465ce7e05942e9fee63a647d9351ff535b97add2da26bcd38df0590757105c23",
                "limitations": REPORT_LIMITS},
               sources=[]),
    ]
