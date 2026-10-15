"""Build the claim that Mahtha et al. 2026 print ESMFold monomer accuracy as 76% in the Abstract
and 77% in the Discussion.

Usage: python3 -I build_claim.py <PMC12809598 fullTextXML> <batch-folder>

Asserts the SHA-256 of the Europe PMC JATS XML (the hash on the existing source record), each quoted
sentence in its section, and the two Table 1 ESMFold cells used.
"""
import csv, hashlib, json, os, re, sys

XML_SHA = "aae321d05839186a7595987d05af6e95aec5ac32b93b35c5cf1126902fe798b8"
XML_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12809598/fullTextXML"
SRC = "lit-structure-20261011-afesmfold-source-mahtha2026"
DATE = "2026-10-14"
NOTE = ("Extraction agent for rewire-benchmark-data issue #163; extraction only, not a review. "
        "Pending an independent review-evidence pass.")

xml_path, out = sys.argv[1], sys.argv[2]
raw = open(xml_path, "rb").read()
assert hashlib.sha256(raw).hexdigest() == XML_SHA, "XML hash mismatch"
x = raw.decode("utf-8")


def plain(fragment):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", fragment)).strip()


abstract = plain(re.search(r"<abstract[^>]*>(.*?)</abstract>", x, re.S).group(1))
ABS = "On the other hand, ESMFold accurately predicted 76% of the monomeric proteins and 41% of the dimeric proteins."
assert ABS in abstract, "Abstract sentence"
assert abstract.split(". ").index(ABS.rstrip(".").split(". ")[0]) == 3, "Abstract sentence 4"

disc = x[x.index("<title>Discussion</title>"):]
disc_p1 = plain(re.findall(r"<p[ >].*?</p>", disc, re.S)[0])
DIS = ("For monomeric proteins, AlphaFold2 and AlphaFold3 exhibited comparable performance, each accurately predicting "
       "87%–88% of the structures, while ESMFold achieved 77% accuracy.")
assert DIS in disc_p1, "Discussion paragraph 1 sentence"

res = x[x.index("<title>Performance of ESMFold for monomer structure prediction</title>"):]
res_p1 = plain(re.findall(r"<p[ >].*?</p>", res, re.S)[0])
RES = ("Out of 1666 monomeric structures predicted by ESMFold, 832 (50%) were classified as accurate with high LDDT and low "
       "RMSD, while 430 (26%) showed domain-level movements despite acceptable local accuracy.")
assert RES in res_p1, "Results sentence"

t1 = re.search(r"<table-wrap[ >].*?</table-wrap>", x, re.S).group(0)
assert "Evaluation summary of AlphaFold2, AlphaFold3, and ESMFold predicted monomer structures" in plain(t1)
rows = [[plain(c) for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", r, re.S)] for r in re.findall(r"<tr[ >].*?</tr>", t1, re.S)]
assert rows[0][:3] == ["Tool", "Predictive class", "No."], rows[0]
assert rows[9][:3] == ["ESMFold", "Accurate prediction", "832"], rows[9]
assert rows[10][:2] == ["Domain movement", "430"], rows[10]

cid = "gfm-guides-20261014-mahtha2026-claim-esmfold-monomer-accuracy-abstract-vs-discussion"
loc = ("Abstract sentence 4; Discussion paragraph 1, sentence 6; Results section 'Performance of ESMFold for monomer "
       "structure prediction' paragraph 1, sentence 1; Table 1, ESMFold rows 'Accurate prediction' and 'Domain movement', "
       "column 'No.'")
value = ("The Abstract prints ESMFold monomer accuracy as 76%: 'On the other hand, ESMFold accurately predicted 76% of the "
         "monomeric proteins and 41% of the dimeric proteins.' The Discussion prints 77%: 'For monomeric proteins, AlphaFold2 "
         "and AlphaFold3 exhibited comparable performance, each accurately predicting 87%–88% of the structures, while ESMFold "
         "achieved 77% accuracy.' Table 1 and the Results give ESMFold 832 accurate predictions (50%) and 430 with domain "
         "movement (26%) out of 1,666 monomers. The paper does not print the sum; 832 + 430 = 1,262 of 1,666 is 75.75% "
         "(computed here, not printed), which rounds to the Abstract's 76%, not to the Discussion's 77%.")
rec = {"id": cid, "kind": "claim", "name": f"printed_value_conflict: {SRC}",
       "description": "Descriptive fact transcribed from the pinned source.", "status": "needs_review", "facets": {},
       "source_ids": [SRC], "links": [{"relation": "subject", "target_id": SRC}],
       "attributes": {
           "field": "printed_value_conflict", "value": value, "source_locator": loc,
           "review": {"method": ["source-hash-verification", "transcription"],
                      "method_note": ("Europe PMC JATS re-downloaded on 2026-10-14 (SHA-256 matches the source record); "
                                      "extract/build_claim.py asserts the Abstract, Discussion and Results sentences and the two "
                                      "Table 1 cells."),
                      "reviewer": ["claude"], "reviewer_note": NOTE, "date": DATE,
                      "artifact_sha256": XML_SHA, "retrieval_url": XML_URL,
                      "note": ("Extracted, not reviewed. Follows the dimer claim "
                               "gfm-guides-20261014-mahtha2026-claim-dimer-accuracy-abstract-vs-table2. Reading the paper's "
                               "monomer accuracy as accurate plus domain movement is an inference from the AlphaFold figures "
                               "(1,069 + 386 and 1,076 + 388 of 1,666 give 87.3% and 87.9%, matching '87%–88%'); the paper "
                               "does not define it.")}}}
with open(os.path.join(out, "batch.jsonl"), "w", encoding="utf-8") as f:
    f.write(json.dumps(rec, ensure_ascii=False, separators=(",", ":")) + "\n")
with open(os.path.join(out, "claims.csv"), "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f)
    w.writerow(["record_id", "source_id", "locator", "printed_value", "review_scope"])
    w.writerow([cid, SRC, loc, "76% (Abstract); 77% (Discussion)", "claim"])
print("1 claim")
