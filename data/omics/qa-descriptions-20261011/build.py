"""Issue #88 follow-up: functional descriptions for dilated-resnet and the seven
borderline method records named in qa-suffix-reasons-20261010/review.md.

Reads the original lines from origin/main, applies the changes below, writes
the store files in place and regenerates batch.jsonl (one new source and one
metadata-correction claim per changed description, source_checked after the
independent review).
  python3 -I data/omics/qa-descriptions-20261011/build.py           write
  python3 -I data/omics/qa-descriptions-20261011/build.py --check   check only
Run from the repository root.
"""
import hashlib
import json
import subprocess
import sys

BASE = "origin/main"
HERE = "data/omics/qa-descriptions-20261011"
NOTE = "Replace a placeholder or provenance description with a sourced functional description (issue #88 follow-up). Historical releases retain the original value."
KRAKEN_SOURCE = "qa-descriptions-20261011-source-kraken"

# id -> (store file, new description, sources added, text appended to attributes.source_locator, claim source_locator)
CHANGES = {
    "mimic-2026-mrnabench-method-dilated-resnet": (
        "data/entities/pipelines.jsonl",
        "Supervised dilated convolutional network baseline, built from three or four DilatedResNet blocks and trained from scratch on each task's training split.",
        ["expansion-p3-mrnabench-2025"],
        "Prior mRNABench evaluated pipeline, quoted in MIMIC Table S11; not a new execution",
        "expansion-p3-mrnabench-2025: Appendix A, Overview of Evaluated Models (baselines paragraph); coverage-source-mimic-2026-v1-html: Table S11 and Appendix D.3",
    ),
    "dna-pathogen-20261009-method-kraken": (
        "data/entities/methods.jsonl",
        "Classifier that assigns taxonomic labels to metagenomic DNA sequences by exact alignment of k-mers.",
        [KRAKEN_SOURCE],
        None,
        f"{KRAKEN_SOURCE}: abstractText; dna-pathogen-20261009-source-song2025: Methods 'Data Analysis' paragraph 1 (cites Wood and Salzberg 2014)",
    ),
    "regulatory-variant-20261009-method-distance-to-tss": (
        "data/entities/methods.jsonl",
        "Baseline that ranks element-gene pairs by the distance from the element to the gene's transcription start site.",
        [],
        "baseline computed by Gschwind et al. 2026, Methods 'Collection of published predictions and baseline predictors'",
        "regulatory-variant-20261009-source-gschwind2026: Methods 'Collection of published predictions and baseline predictors'; Results 'Systematic benchmarking of ENCODE-rE2G'",
    ),
    "regulatory-variant-20261009-method-ep-dnase-correlation": (
        "data/entities/methods.jsonl",
        "Baseline that links elements to genes by correlating DNase-seq accessibility at the element and at the gene's promoter across cell types.",
        [],
        "baseline computed by Gschwind et al. 2026, Supplementary Table 3 row label",
        "regulatory-variant-20261009-source-gschwind2026: Results 'Systematic benchmarking of ENCODE-rE2G' ('correlating element and promoter accessibility across cell types'); Methods 'Correlation of enhancer–promoter activity across cell types'",
    ),
    "regulatory-variant-20261009-method-residualbind": (
        "data/entities/methods.jsonl",
        "Convolutional network for lentiMPRA activity that adds a dilated residual block after the first convolutional layer of a baseline CNN and is trained on one-hot sequences.",
        [],
        "defined and trained on lentiMPRA by Tang et al. 2025, Methods 'ResidualBind for lentiMPRA'",
        "regulatory-variant-20261009-source-tang2025: Methods 'ResidualBind for lentiMPRA'; Results 'Task 1: predicting cell-type specific regulatory activity from lentiMPRA data'",
    ),
    "ucc-research-method-abdelaal-scmapcell": (
        "data/entities/methods.jsonl",
        "Cell-type classifier for single-cell RNA-seq data that labels each cell with a k-nearest-neighbour classifier and can leave cells unlabelled.",
        [],
        None,
        "ucc-research-source-abdelaal-2019-paper: Table 1, row 'scmapcell' (underlying classifier kNN; rejection option yes)",
    ),
    "ucc-research-method-abdelaal-scpred": (
        "data/entities/methods.jsonl",
        "Cell-type classifier for single-cell RNA-seq data built on a support vector machine with a radial kernel, which can leave cells unlabelled.",
        [],
        None,
        "ucc-research-source-abdelaal-2019-paper: Table 1, row 'scPred' (underlying classifier SVM with radial kernel; rejection option yes)",
    ),
    "ucc-research-method-abdelaal-svm-linear": (
        "data/entities/methods.jsonl",
        "General-purpose support vector machine classifier with a linear kernel from scikit-learn, used with and without a rejection option that leaves low-confidence cells unlabelled.",
        [],
        None,
        "ucc-research-source-abdelaal-2019-paper: Table 1, rows 'SVM' and 'SVM rejection'; Methods 'Classification methods'",
    ),
}

KRAKEN = {
    "id": KRAKEN_SOURCE,
    "kind": "source",
    "name": "Abstract: Kraken: ultrafast metagenomic sequence classification using exact alignments",
    "description": "Source text retrieved and hashed for the issue #88 follow-up functional-description fix.",
    "status": "needs_review",
    "facets": {},
    "source_ids": [],
    "links": [],
    "attributes": {
        "url": "https://doi.org/10.1186/gb-2014-15-3-r46",
        "artifact_url": "https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI%3A%2210.1186%2Fgb-2014-15-3-r46%22&format=json&resultType=core",
        "version": "Europe PMC core record MED/24580807 (title and abstract), Genome biology 2014",
        "retrieved_at": "2026-10-11T00:29:23Z",
        "artifact_sha256": "5209b274d6ff9f32c554eced5ccb1cd810194fe587a7649b4ca5990e870fd07d",
        "publication_status": "peer_reviewed",
        "media_type": "application/json",
        "source_locator": "abstractText",
        "doi": "10.1186/gb-2014-15-3-r46",
        "licence": "CC-BY-2.0",
        "hash_scope": "SHA-256 of one retrieval of a Europe PMC REST search response. These responses are not byte-stable (a later retrieval can differ in JSON key order); the title and abstractText fields are the evidence.",
    },
}


# Added by the independent review (review.md): status and review block for each batch record.
REVIEW_DATE = "2026-10-11"
REVIEWER = {
    "reviewer": ["claude"],
    "reviewer_note": "Extractor: Claude research agent for the issue #88 follow-up. Reviewer: separate Claude review agent, independent of the extractor; no human review claimed",
    "date": REVIEW_DATE,
}
KRAKEN_REVIEW = {
    "method": ["source-hash-verification", "ai-assisted-source-review"],
    **REVIEWER,
    "artifact_sha256": "c40f09ae30a945394aef0aac37d331982df0e89fa00f2f290505124dfc4f7bdb",
    "retrieval_url": KRAKEN["attributes"]["artifact_url"],
    "method_note": "Re-downloaded the artifact three times, compared its SHA-256 with the pin, read the title, DOI, authors, abstractText and licence field, and read the licence statement in the article full text (Europe PMC PMC4053813 fullTextXML).",
    "note": "Re-downloaded on 2026-10-11: three retrievals gave the same bytes (c40f09ae...), which do not match artifact_sha256 (5209b274...). No saved copy of the pinned retrieval exists, so the difference cannot be inspected; hash_scope says these responses are not byte-stable. The fresh record is MED/24580807, PMC4053813, DOI 10.1186/gb-2014-15-3-r46, Wood DE and Salzberg SL, Genome Biology 15(3), 2014, and its abstractText contains both passages quoted in changes.md. Licence corrected from CC-BY-4.0 to CC-BY-2.0: the search record says only 'cc by', and the article's permissions block gives http://creativecommons.org/licenses/by/2.0.",
}
CLAIM_METHOD = {
    "method": ["automated-source-review", "ai-assisted-source-review"],
    **REVIEWER,
    "method_note": "Re-downloaded the cited artifact and checked its SHA-256 against the pin, read the new description against the cited passage, compared previous_value with origin/main, and ran build.py --check.",
}
CLAIM_NOTES = {
    "mimic-2026-mrnabench-method-dilated-resnet": "Supported by mRNABench Appendix A 'Overview of Evaluated Models' (PMC12265608, matches pin): ab-initio supervised dilated CNN, trained from scratch on the train split, three or four DilatedResNetBlocks. MIMIC (matches pin) cites the row as Dilated ResNet [71], and [71] is mRNABench. The old text is kept in source_locator.",
    "dna-pathogen-20261009-method-kraken": "Supported by the Kraken abstractText ('assigning taxonomic labels to metagenomic DNA sequences'; 'Using exact alignment of k-mers'). Agree with dropping 'lowest common ancestor assignment': it is not in the pinned abstract. The citation formerly in the text is now the added source.",
    "regulatory-variant-20261009-method-distance-to-tss": "Supported by Gschwind et al. Methods 'Collection of published predictions and baseline predictors' ('based on distance to TSS') and the Supplementary Table 3 predictor 'Distance to TSS'; the Results sentence supports the expansion of TSS. Same meaning as the old text, which is kept in source_locator.",
    "regulatory-variant-20261009-method-ep-dnase-correlation": "Supported by Results ('correlating element and promoter accessibility across cell types') and by Methods 'Correlation of enhancer–promoter activity across cell types' (DNase-seq reads at cCREs and TSSs across 89 biosamples, correlated per pair). Review added the Methods section to source_locator. 'Across cell types' is the source's own wording.",
    "regulatory-variant-20261009-method-residualbind": "Supported by Tang et al. Methods 'ResidualBind for lentiMPRA' (dilated residual block after the first convolutional layer of the baseline CNN) and Results Task 1 (trained using one-hot sequences); matches the linked configuration 'LentiMPRA-one-hot'. The old provenance is kept in source_locator.",
    "ucc-research-method-abdelaal-scmapcell": "Supported by Abdelaal et al. Table 1 row scmapcell (kNN; rejection option Yes), the Results definition of rejection ('unlabeled' if not confident enough), and Methods (16 methods developed specifically for scRNA-seq data).",
    "ucc-research-method-abdelaal-scpred": "Supported by Abdelaal et al. Table 1 row scPred (SVM with radial kernel; rejection option Yes) and the Results definition of rejection.",
    "ucc-research-method-abdelaal-svm-linear": "Supported by Abdelaal et al. Table 1 rows SVM and SVMrejection (SVM (linear kernel), Python 0.19.2, rejection No and Yes) and Methods 'Classification methods' (general-purpose classifiers from scikit-learn; LinearSVC(), with CalibratedClassifierCV() for the rejection variant).",
}


def reviewed_source(record):
    record = json.loads(dumps(record))
    record["status"] = "source_checked"
    record["attributes"]["review"] = KRAKEN_REVIEW
    return record


def reviewed_claim(claim, subject):
    claim["status"] = "source_checked"
    claim["attributes"]["review"] = {**CLAIM_METHOD, "note": f"{NOTE} Independent review {REVIEW_DATE}: {CLAIM_NOTES[subject]}"}
    return claim


def git_lines(path):
    text = subprocess.run(["git", "show", f"{BASE}:{path}"], check=True, capture_output=True, text=True).stdout
    return text.split("\n")


def dumps(record):
    return json.dumps(record, separators=(",", ":"), ensure_ascii=False)


def main(check):
    claims = []
    rows = []
    for path in sorted({c[0] for c in CHANGES.values()}):
        base = git_lines(path)
        out = list(base)
        seen = 0
        for i, line in enumerate(base):
            if not line:
                continue
            record = json.loads(line)
            change = CHANGES.get(record["id"])
            if not change:
                continue
            assert dumps(record) == line, record["id"]
            _, description, added, locator_tail, claim_locator = change
            old = record["description"]
            new = json.loads(line)
            new["description"] = description
            for source in added:
                assert source not in new["source_ids"], (record["id"], source)
                new["source_ids"].append(source)
            if locator_tail:
                new["attributes"]["source_locator"] = f"{record['attributes']['source_locator']}; {locator_tail}"
            changed = {k for k in record if record[k] != new[k]}
            assert changed <= {"description", "source_ids", "attributes"}, changed
            changed_attrs = {k for k in record["attributes"] if record["attributes"][k] != new["attributes"].get(k)}
            assert changed_attrs <= {"source_locator"}, changed_attrs
            out[i] = dumps(new)
            seen += 1
            digest = hashlib.sha256(f"{record['id']}:description:2026-10-11".encode()).hexdigest()[:20]
            claims.append({
                "id": f"metadata-correction-{digest}",
                "kind": "claim",
                "name": f"{record['name']}: description",
                "description": NOTE,
                "status": "needs_review",
                "facets": record["facets"],
                "source_ids": new["source_ids"],
                "links": [{"relation": "subject", "target_id": record["id"]}],
                "attributes": {
                    "field": "description",
                    "previous_value": old,
                    "value": description,
                    "source_locator": claim_locator,
                },
            })
            rows.append((record["id"], record["kind"], old, description, claim_locator))
        assert seen == sum(1 for c in CHANGES.values() if c[0] == path), path
        current = open(path, encoding="utf8").read().split("\n")
        if check:
            assert current == out, f"{path} differs from the build"
        else:
            open(path, "w", encoding="utf8").write("\n".join(out))
    claims = [reviewed_claim(c, c["links"][0]["target_id"]) for c in claims]
    batch = [dumps(reviewed_source(KRAKEN))] + [dumps(c) for c in sorted(claims, key=lambda c: c["id"])]
    text = "\n".join(batch) + "\n"
    if check:
        assert open(f"{HERE}/batch.jsonl", encoding="utf8").read() == text, "batch.jsonl differs from the build"
    else:
        open(f"{HERE}/batch.jsonl", "w", encoding="utf8").write(text)
    print(f"{len(rows)} descriptions changed; batch has {len(batch)} records ({len(claims)} correction claims, 1 source)")
    return rows


if __name__ == "__main__":
    main("--check" in sys.argv)
