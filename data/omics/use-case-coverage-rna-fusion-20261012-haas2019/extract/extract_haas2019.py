"""Record the Haas et al. 2019 (Genome Biology) source and its descriptive claims about the use case's tools.

Haas et al. print no per-method accuracy value in a table or in the text (see research.md), so this batch
holds no results. Table 1 rows and quoted sentences are asserted against the pinned Europe PMC XML
(sha256 9828428800fb119b30742d6f6f0b1aabf4b8cd34bd889768c462ca440cd65108). Run with python3 -I.
"""
import csv
import hashlib
import html
import json
import re
import sys
from collections import Counter

xml_path, out_dir = sys.argv[1:3]
raw = open(xml_path, "rb").read()
SHA = "9828428800fb119b30742d6f6f0b1aabf4b8cd34bd889768c462ca440cd65108"
assert hashlib.sha256(raw).hexdigest() == SHA
xml = raw.decode("utf-8")
P = "rna-fusion-20261012-haas2019"
SRC = f"{P}-source"
URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC6802306/fullTextXML"
FACETS = {"areas": ["rna-transcriptomes"], "contexts": ["research"]}


def text(fragment):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", fragment))).strip()


tw = re.search(r"<table-wrap .*?</table-wrap>", xml, re.S).group(0)
rows = {}
for tr in re.findall(r"<tr>.*?</tr>", tw, re.S):
    cells = [text(c) for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", tr, re.S)]
    rows[re.sub(r"\s*\[.*", "", cells[0])] = cells
assert rows["Method"] == ["Method", "Class*", "Brief overview of methodology"]
body = re.sub(r"\s+", " ", text(re.search(r"<body>.*</body>", xml, re.S).group(0)))


def sentence(s):
    assert s in body, s
    return s


records = [{"id": SRC, "kind": "source",
            "name": "Accuracy assessment of fusion transcript detection via read-mapping and de novo fusion transcript assembly-based methods",
            "description": "Primary source retrieved and hashed for the 2026-10-12 ML-versus-baseline pass.",
            "status": "needs_review", "facets": FACETS, "source_ids": [], "links": [],
            "attributes": {"url": "https://doi.org/10.1186/s13059-019-1842-9", "artifact_url": URL,
                           "version": "Genome Biology 20:213, published 2019-10-21; PMC6802306 full-text XML",
                           "retrieved_at": "2026-10-12T20:53:32Z", "artifact_sha256": SHA,
                           "doi": "10.1186/s13059-019-1842-9", "publication_status": "peer_reviewed", "licence": "CC-BY-4.0",
                           "media_type": "application/xml", "venue": "Genome Biology", "year": 2019,
                           "source_locator": "Licence statement in the article XML <license> element: Creative Commons Attribution 4.0",
                           "scope_decision": "No results extracted: per-method accuracy (P-R AUC, TPR and PPV at maximum F1, leaderboard rankings) is shown only in Figures 1b, 2a, 4a, 4c, 4d and Additional file 2 Figures S3, S5, S8 and S9. Additional file 1 holds per-fusion predictions, not accuracy values, and the FusionBenchmarking repository holds code, not result tables."}}]
claims_rows = []
REVIEW = {"method": ["transcription"], "method_note": "Transcribed from the pinned article XML; extract/extract_haas2019.py asserts each Table 1 row or sentence.",
          "reviewer": ["claude"],
          "reviewer_note": "Extracting Claude agent for the 2026-10-12 ML-versus-baseline pass (issue #121); extraction only, not a review. Pending an independent review-evidence pass.",
          "date": "2026-10-12", "artifact_sha256": SHA, "retrieval_url": URL,
          "note": "Extracted, not reviewed."}
for cid, subject, field, value, loc in [
        ("claim-ericscript-classifier", "rna-fusion-20261009-method-ericscript", "method_description", rows["EricScript"][2],
         "Table 1, row 'EricScript', column 'Brief overview of methodology'"),
        ("claim-arriba-filters", "rna-fusion-20261009-method-arriba", "method_description", rows["Arriba"][2],
         "Table 1, row 'Arriba', column 'Brief overview of methodology'"),
        ("claim-star-fusion-filters", "rna-fusion-20261009-method-star-fusion", "method_description", rows["STAR-Fusion"][2],
         "Table 1, row 'STAR-Fusion', column 'Brief overview of methodology'"),
        ("claim-top-performers", "rna-fusion-20261009-method-star-fusion", "reported_ranking",
         sentence("In particular, STAR-Fusion, Arriba, and STAR-SEQR had the best combination of speed and accuracy compared to 19 other methods evaluated on cancer transcriptome data."),
         "Discussion paragraph 2, sentence 1"),
        ("claim-ericscript-least-accurate", "rna-fusion-20261009-method-ericscript", "reported_ranking",
         sentence("In contrast to an earlier assessment of fusion prediction accuracy that found EricScript to be top-ranking [ 16 ], in our assessment, EricScript was the least accurate method on cancer cell line RNA-seq, suffering mostly from a high rate of false positives."),
         "Discussion paragraph 2, sentence 4")]:
    records.append({"id": f"{P}-{cid}", "kind": "claim", "name": f"{field}: {subject}",
                    "description": "Descriptive fact transcribed from the pinned source.", "status": "needs_review", "facets": {},
                    "source_ids": [SRC], "links": [{"relation": "subject", "target_id": subject}],
                    "attributes": {"field": field, "value": value, "source_locator": loc, "review": REVIEW}})
    claims_rows.append([f"{P}-{cid}", SRC, loc, value, "claim"])
assert "AdaBoost classifier" in rows["EricScript"][2] and "AdaBoost classifier" in rows["deFuse"][2]

with open(f"{out_dir}/batch.jsonl", "w", encoding="utf-8") as f:
    for r in sorted(records, key=lambda r: r["id"]):
        f.write(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n")
with open(f"{out_dir}/claims.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["record_id", "source_id", "locator", "printed_value", "review_scope"])
    w.writerows(claims_rows)
print(Counter(r["kind"] for r in records))
