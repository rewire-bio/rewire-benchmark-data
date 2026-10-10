"""Follow-up to issue #88(b), 2026-10-10: remove author-year citations from 18 more method and
model descriptions listed in review.md. Run from the worktree root:
python3 -I apply_fixes_18.py <notes-dir> <scratch-dir>

Each record has an explicit old and new text. The old text must equal the current working-tree
description. Only the description string (and, for DELFI, one source ID appended to source_ids)
changes. One metadata-correction claim per record is appended to <notes-dir>/batch.jsonl.
"""
import hashlib, json, sys

NOTES, SCRATCH = sys.argv[1], sys.argv[2]
DATE = "2026-10-10"
WHY = ("Remove the author-year citation from the description (issue #88 follow-up) and reword the sentence where the citation sat mid-sentence, "
       "keeping every functional fact.")

# id: (new description, cited works, source to add or None, note)
EDITS = {
    "ctdnafrag-20261009-method-delfi": (
        "Short-to-long fragment ratios in 5 Mb bins. The method record names the feature definition, not an implementation.",
        ["Cristiano et al. 2019", "Hou et al. reference 45"], "amp-20261007-ctdna-fragmentomics-source",
        "Cristiano et al. 2019 matches existing source amp-20261007-ctdna-fragmentomics-source, which was added to source_ids. Hou et al. 2024 was already present."),
    "ctdnafrag-20261009-method-ichorcna": (
        "Copy-number-based tumour fraction estimation from ultra-low-pass WGS.",
        ["Adalsteinsson et al. 2017"], None, "No source record for Adalsteinsson et al. 2017 exists in the store; source_ids unchanged."),
    "ctdnameth-20261009-method-houseman-cp": (
        "Constrained projection least-squares deconvolution, run through the EpiDISH R package.",
        ["Houseman 2012"], None, "No source record for Houseman 2012 exists in the store; source_ids unchanged."),
    "regulatory-variant-20261009-method-epimap": (
        "Enhancer-gene links from the EpiMap integrative epigenomics resource.",
        ["Boix et al. 2021", "Gschwind et al. reference 8"], None,
        "No source record for Boix et al. 2021 exists in the store; Gschwind et al. 2026 was already present."),
    "regulatory-variant-20261009-method-epiraction": (
        "Atlas of candidate enhancer-gene interactions, released as a 2025 preprint.",
        ["Nurtdinov and Guigó, bioRxiv 2025", "Gschwind et al. reference 27"], None,
        "No source record for Nurtdinov and Guigó 2025 exists in the store; Gschwind et al. 2026 was already present."),
    "rna-fusion-20261009-method-fusilli": (
        "Long-read fusion caller that keeps reads spanning two genes from a B-ALL gene list and fusions on a B-ALL fusion list, with distance, overlap, breakpoint and two-read filters; developed by the authors of the comparison that evaluated it.",
        ["Lin et al. 2026"], None, "Lin et al. 2026 already present."),
    "rna-fusion-20261009-method-fusioncatcher": (
        "Short-read fusion caller using several aligners (STAR, Bowtie and BLAT).",
        ["Tamura et al. 2026"], None, "Tamura et al. 2026 already present."),
    "rna-fusion-20261009-method-fusionseeker": (
        "Long-read fusion caller that clusters candidate fusions from BAM alignments and filters them by supporting reads.",
        ["Lin et al. 2026"], None, "Lin et al. 2026 already present."),
    "rna-fusion-20261009-method-jaffa": (
        "Fusion caller using alignment to a transcriptomic reference: JAFFA-direct for short reads (BLAT, Bowtie2 and BLAST+) and JAFFAL for long reads, which filters candidates by alignment to the genome.",
        ["Tamura et al. 2026", "Lin et al. 2026"], None, "Both already present."),
    "rna-fusion-20261009-method-longgf": (
        "Long-read fusion caller that compares reads mapped to a reference against a GTF and filters supporting reads.",
        ["Lin et al. 2026"], None, "Lin et al. 2026 already present."),
    "somatic-20261009-method-neusomatic": (
        "Neural-network somatic SNV and indel caller; in one linked comparison it was run in ensemble mode over other callers' output.",
        ["Guille et al. 2025", "Wang et al. 2020"], None, "Both already present."),
    "somatic-20261009-method-strelka": (
        "Somatic SNV and indel caller using allele-frequency analysis; versions 2.7.1 and 2.9.2 were evaluated in the linked comparisons.",
        ["Guille et al. 2025", "Wang et al. 2020"], None, "Both already present. Which version each comparison used is on the configuration records."),
    "somatic-oncogenicity-20261009-method-cadd": (
        "Combined Annotation-Dependent Depletion: a genome-wide variant deleteriousness score that integrates more than 60 genomic features in a machine learning model trained to separate simulated de novo variants from variants fixed in human populations since the human-chimpanzee split. It scores single nucleotide variants and short insertions and deletions anywhere in the reference assembly, not only missense variants.",
        ["Rentzsch et al. 2019, Nucleic Acids Research 47:D886"], None, "No source record for Rentzsch et al. 2019 exists in the store; source_ids unchanged."),
    "egfrnsclc-20261009-model-gpt-4o": (
        "Proprietary model; the evaluated version, 2024-05-13, was used through the Azure OpenAI API.",
        ["Lin et al. 2025"], None, "Lin et al. 2025 already present."),
    "egfrnsclc-20261009-model-llama-3-1-70b": (
        "Open-weight model; in the evaluated runs it was served with Ollama.",
        ["Lin et al. 2025"], None, "Lin et al. 2025 already present."),
    "egfrnsclc-20261009-model-qwen-2-5-72b": (
        "Open-weight model; in the evaluated runs it was served with Ollama.",
        ["Lin et al. 2025"], None, "Lin et al. 2025 already present."),
    "regulatory-variant-20261009-model-gpn": (
        "Masked DNA language model; variant effects scored by single-nucleotide masking.",
        ["Tang et al. 2025"], None, "Tang et al. 2025 already present."),
    "regulatory-variant-20261009-model-trednet": (
        "Two-phase CNN for enhancer prediction and variant prioritisation, developed by the group of the senior author of the comparison that evaluated it.",
        ["Manzo et al. 2025"], None, "Manzo et al. 2025 already present."),
}
assert len(EDITS) == 18

sources = {json.loads(l)["id"] for l in open("data/entities/sources.jsonl")}


def enc(s):
    return json.dumps(s, ensure_ascii=False)


changes, corrections, seen = [], [], set()
for path in ("data/entities/methods.jsonl", "data/entities/models.jsonl"):
    lines = open(path).read().split("\n")
    for i, line in enumerate(lines):
        if not line:
            continue
        r = json.loads(line)
        if r["id"] not in EDITS:
            continue
        new, cited, add, note = EDITS[r["id"]]
        old = r["description"]
        assert line.count(enc(old)) == 1
        out = line.replace(enc(old), enc(new))
        if add:
            assert add in sources and add not in r["source_ids"]
            old_ids = enc(r["source_ids"]).replace(", ", ",")
            new_ids = enc(r["source_ids"] + [add]).replace(", ", ",")
            assert out.count(old_ids) == 1
            out = out.replace(old_ids, new_ids)
        after = json.loads(out)
        assert after["description"] == new
        check = dict(after, description=old, source_ids=r["source_ids"])
        assert check == r, r["id"]
        lines[i] = out
        seen.add(r["id"])
        changes.append({"id": r["id"], "kind": r["kind"], "old": old, "new": new, "cited": cited, "source_added": add, "note": note})
        h = hashlib.sha256(f"{r['id']}|description|followup".encode()).hexdigest()[:20]
        corrections.append({
            "id": f"metadata-correction-qa-20261010-{h}", "kind": "claim", "name": f"{r['name']}: description", "description": WHY,
            "status": "needs_review", "facets": {}, "source_ids": after["source_ids"], "links": [{"relation": "subject", "target_id": r["id"]}],
            "attributes": {"field": "description", "previous_value": old, "value": new, "source_locator": f"Record description; cited {'; '.join(cited)}",
                           "review": {"method": ["automated-source-review"], "reviewer": ["claude"],
                                      "reviewer_note": "Claude (Opus 5.5) QA agent; not an independent review",
                                      "date": DATE, "note": WHY + " " + note + " Pending independent review."}}})
    open(path, "w").write("\n".join(lines))
assert seen == set(EDITS), set(EDITS) - seen

batch = f"{NOTES}/batch.jsonl"
existing = [json.loads(l) for l in open(batch) if l.strip()]
ids = {c["id"] for c in existing}
assert not ids & {c["id"] for c in corrections}
with open(batch, "a") as f:
    for c in sorted(corrections, key=lambda c: c["id"]):
        f.write(json.dumps(c, ensure_ascii=False) + "\n")
json.dump(changes, open(f"{SCRATCH}/changes_18.json", "w"), indent=1, ensure_ascii=False)
print("changed:", len(changes), "sources added:", sum(1 for c in changes if c["source_added"]),
      "cited works with no store source:", sum(1 for c in changes if c["note"].startswith("No source")), "batch lines:", len(existing) + len(corrections))
