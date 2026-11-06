#!/usr/bin/env python3
"""Reviewer's manual check of the 25 prose results: each expected sentence is written
out here from reading the report, then matched against the pinned text layer, and the
result records are checked against the role each number plays in that sentence."""
import json
import re
import sys

layout = open(sys.argv[1], encoding="utf-8").read()
flat = re.sub(r"\s+", " ", layout)
batch = [json.loads(l) for l in open(sys.argv[2], encoding="utf-8")]
ev = {r["id"]: r for r in batch if r["kind"] == "evaluation"}

# (locator substring, expected printed value, sentence that must be in the report,
#  expected system configuration)
EXPECT = [
    ("HyCell batch correction", "0.54",
     "Batch correction rises from 0.36 to 0.54", "config-hycell"),
    ("PCA batch correction", "0.36",
     "Batch correction rises from 0.36 to 0.54", "config-pca"),
    ("PCA biological conservation", "0.49",
     "and biological conservation from 0.49 to 0.63.", "config-pca"),
    ("sentence giving HyCell's split (ARI)", "0.64",
     "the two groups are 85% naive and 96% effector cells (ARI 0.64)", "config-hycell"),
    ("'NMI with chemistry'", "0.012",
     "nearly independent of sequencing chemistry (NMI with chemistry 0.012)", "config-hycell"),
    ("'Within single donors', value for HyCell", "0.66",
     "HyCell gives the highest agreement as well (mean ARI 0.66 over 12 donors;", "config-hycell"),
    ("'Within single donors', value for UCE", "0.60",
     "mean ARI 0.66 over 12 donors; UCE 0.60, Tahoe-x1 0.58)", "config-uce"),
    ("'Within single donors', value for Tahoe-x1", "0.58",
     "mean ARI 0.66 over 12 donors; UCE 0.60, Tahoe-x1 0.58)", "config-tahoe-x1-70m"),
    ("gamma-delta T against tissue-resident CD8 T, value for HyCell", "0.37",
     "T cells against tissue-resident CD8 T cells (ARI 0.37 for HyCell, 0.30 for PCA,",
     "config-hycell"),
    ("gamma-delta T against tissue-resident CD8 T, value for PCA", "0.30",
     "(ARI 0.37 for HyCell, 0.30 for PCA, at most 0.06 for the published models)",
     "config-pca"),
    ("all cells, HyCell", "0.937",
     "the Spearman correlation between pseudotime and stage, 0.937, is the highest of all embeddings",
     "config-hycell"),
    ("averaged over donors, HyCell", "0.894",
     "Averaged over donors it is 0.894, again the highest, ahead of Stack (0.918 and 0.879)",
     "config-hycell"),
    ("all cells, Stack", "0.918",
     "ahead of Stack (0.918 and 0.879)", "config-stack"),
    ("averaged over donors, Stack", "0.879",
     "ahead of Stack (0.918 and 0.879)", "config-stack"),
    ("all cells, SCimilarity", "0.908",
     "SCimilarity (0.908 and 0.868)", "config-scimilarity"),
    ("averaged over donors, SCimilarity", "0.868",
     "SCimilarity (0.908 and 0.868)", "config-scimilarity"),
    ("all cells, PCA", "0.888", "PCA (0.888 and 0.849)", "config-pca"),
    ("averaged over donors, PCA", "0.849", "PCA (0.888 and 0.849)", "config-pca"),
    ("decoded against counted fold changes", "0.81",
     "decoded and counted fold changes have a Spearman correlation of 0.81", "config-hycell"),
    ("plasma-cell axis, decoder", "0.965",
     "For the plasma-cell axis the mean Spearman correlation is 0.965 for the decoder and 0.772 for pseudobulk counts",
     "config-hycell"),
    ("plasma-cell axis, pseudobulk counts", "0.772",
     "is 0.965 for the decoder and 0.772 for pseudobulk counts", "config-pseudobulk-counts"),
    ("monocytes, decoder", "0.940",
     "for classical against nonclassical monocytes it is 0.940 against 0.476", "config-hycell"),
    ("monocytes, pseudobulk counts", "0.476",
     "for classical against nonclassical monocytes it is 0.940 against 0.476",
     "config-pseudobulk-counts"),
    ("CD4 T cells, decoder", "0.957",
     "and for naive against effector CD4 T cells 0.957 against 0.376", "config-hycell"),
    ("CD4 T cells, pseudobulk counts", "0.376",
     "and for naive against effector CD4 T cells 0.957 against 0.376", "config-pseudobulk-counts"),
]

results = [r for r in batch if r["kind"] == "result"
           and not r["attributes"]["source_locator"].startswith(("Table", "Figure 1b"))]
assert len(results) == 25, len(results)

ok, bad = 0, []
used = set()
for frag, value, sentence, cfg in EXPECT:
    hits = [r for r in results if frag in r["attributes"]["source_locator"]]
    if len(hits) != 1:
        bad.append((frag, "matched %d results" % len(hits)))
        continue
    r = hits[0]
    used.add(r["id"])
    flatsent = re.sub(r"\s+", " ", sentence)
    if flatsent not in flat:
        bad.append((frag, "sentence not in the report text layer"))
        continue
    if r["attributes"]["printed_value"] != value:
        bad.append((frag, "printed_value %s, expected %s"
                    % (r["attributes"]["printed_value"], value)))
        continue
    e = ev[[l["target_id"] for l in r["links"] if l["relation"] == "evaluation"][0]]
    sysid = [l["target_id"] for l in e["links"] if l["relation"] == "system"][0]
    if not sysid.endswith(cfg):
        bad.append((frag, "system %s, expected %s" % (sysid, cfg)))
        continue
    ok += 1

print("prose results checked: %d of %d, %d failed" % (ok, len(results), len(bad)))
for b in bad:
    print("  FAIL", b)
missed = [r["id"] for r in results if r["id"] not in used]
print("prose results not covered by an expectation:", missed)

# numbers printed in the report that the batch does not store as a result
print()
print("printed prose numbers deliberately not stored as results:")
for s, why in [
    ("and biological conservation from 0.49 to 0.63.",
     "0.63 = HyCell cross-tissue Bio, already stored from Figure 1b at 0.633"),
    ("(Spearman rho = 0.94)", "intro bullet rounds Section 4.2's 0.937"),
    ("reach at most 0.03 for every other embedding", "abstract bound, stored as a claim at 0.031"),
]:
    print("   ", why)
