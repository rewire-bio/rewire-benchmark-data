"""Issue #88, independent review: write review-corrections.csv, which fixes descriptions written by
corrections.csv. Apply it after corrections.csv:

  python3 -I data/omics/qa-descriptions-20261014/review-fixes.py
  npm run records:correct -- data/omics/qa-descriptions-20261014/review-corrections.csv docs/reviews/2026-10-14-functional-descriptions.md

Configurations (systematic errors in build.py, fixed by rule):
- label-repeat: "Configuration of X: X: ..." repeats the label.
- version: build.py prefixed any version-like value with "version". A ProteinGym snapshot commit
  became the model's version, and sizes ("8M") or settings ("3 recycling rounds") read as
  versions.
- name-only detail: the text after the colon repeats the label ("GAT: GAT.") or stops at an
  abbreviation ("Protein representation: 1D conv."), while the record's own settings say more.
- source commentary: segments about how the source prints or omits something ("Table 2 prints
  the ROC-optimal thresholds ...", "region printed as ...", "parameters in Supplementary Table 1").
- "its settings are not recorded" was also written where the label itself carries the settings,
  or where the record has settings that build.py dropped. The phrase becomes "no settings beyond
  its name are recorded", or the settings are written out.
Models: corrections from checking each researched sentence against its source (REVIEWED below).
"""
import csv
import glob
import importlib.util
import json
import re

HERE = "data/omics/qa-descriptions-20261014"
spec = importlib.util.spec_from_file_location("build", f"{HERE}/build.py")
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)

RULE = ("Review of build.py output ({rule}); rewritten from the record's own name, links and "
        f"attributes by {HERE}/review-fixes.py.")

REVIEWED = {
    "lit-genomics-20261011-geneb-model-generator": (
        "Generative transformer decoder DNA language models with 6-mer tokens, in eukaryote and prokaryote "
        "variants, that generate and embed long sequences (98 kb context in the first release, pretrained on "
        "386 billion nucleotides of eukaryotic DNA).",
        "Family includes GENERator-v2 prokaryote checkpoints (linked configurations), so 'pretrained on "
        "eukaryotic DNA' did not hold for the whole family. https://arxiv.org/abs/2502.07272 Abstract; "
        "https://huggingface.co/GenerTeam (GENERator-v2-prokaryote-1.2b-base, -3b-base model cards)"),
    "gfm2-20261011-datta2026-model-generator-v2": (
        "Generative transformer decoder DNA language model family with 6-mer tokens and long context (98 kb in "
        "the first release, pretrained on eukaryotic DNA; the second version adds prokaryote variants), used for "
        "sequence generation, zero-shot variant effect scoring and as a source of embeddings for fine-tuning.",
        "The linked configurations are GENERATOR-v2-1.2B, and v2 has eukaryote and prokaryote checkpoints. "
        "https://arxiv.org/abs/2502.07272 Abstract; https://huggingface.co/GenerTeam/GENERator-v2-prokaryote-1.2b-base"),
    "lit-genomics-20261011-geneb-model-evo": (
        "StripedHyena DNA language models of 7 billion parameters (Evo 1 and Evo 1.5), trained at "
        "single-nucleotide resolution on prokaryotic and phage genomes with 8 kb or 131 kb contexts, for "
        "zero-shot function prediction and sequence generation.",
        "Family includes Evo1-8K-Base and Evo 1.5 (8k) configurations, so a single 131 kb context did not hold. "
        "https://doi.org/10.1101/2024.02.27.582234 Abstract: \"we scale Evo to 7 billion parameters with a "
        "context length of 131 kilobases (kb) at single-nucleotide, byte resolution\""),
    "lit-genomics-20261011-geneb-model-dnagpt": (
        "GPT-style DNA models pretrained on human genomes (0.1B) or on genomes of many mammals (3B; over 200 "
        "billion base pairs), with extra sequence-order and GC-content tasks so they take both sequence and "
        "numerical inputs.",
        "Linked configurations are dna_gpt0.1b_h and dna_gpt3b_m. https://github.com/TencentAILabHealthcare/DNAGPT "
        "README: \"DNAGPT 0.1B params model pretrained with human genomes\"; \"DNAGPT 3B params model pretrained "
        "with mutli-organism genomes\"; https://arxiv.org/abs/2307.05628 Abstract"),
    "paper-model-984c6b7cbb3e92f1d0": (
        "Scans whole bacterial genomes in half-overlapping windows with an NTv2 phage-versus-bacteria segment "
        "classifier, then normalises, smooths, merges and filters the window scores by score and length to call "
        "prophage regions.",
        "Article fix only ('a NTv2' to 'an NTv2'); content as in corrections.csv."),
}

SEG_COMMENTARY = re.compile(
    r"\b(prints?|printed|do(es)? not restate|is not stated|are not stated)\b"
    r"|^(hyper)?parameters in Supplement|^command line and parameters in", re.I)
SETTINGS_PHRASE = "; its settings are not recorded."
NEW_PHRASE = "; no settings beyond its name are recorded."
SIZE = re.compile(r"^\d+(\.\d+)?[KMB]$")
VERSION = re.compile(r"^(v?\d+\.\d+|v\d+|\d{4}-\d{2})")
SHA = re.compile(r"^[0-9a-f]{40}$")
JUNKISH = re.compile(r"\b(paper-specific|table-specific|evaluated by|paper baseline|checkpoint not|"
                     r"trained by the benchmark authors|reimplemented by)\b", re.I)


def segments(text):
    """Split settings text into segments at semicolons and sentence ends, not at abbreviations."""
    text = build.LOCATOR.sub("", build.CITATION.sub("", str(text))).strip()
    text = re.sub(r"\s+in (Table|Tables|Figure|Fig\.) S?\d+[a-z]?\b", "", text)
    parts = re.split(r";\s+|(?<=[a-z0-9)]{3}\.)\s+(?=[A-Z])", text)
    return [p.strip().rstrip(".;, ") for p in parts if p.strip()]


def real_settings(record):
    """Segments of the record's settings that are settings, not provenance."""
    out = []
    for key in build.SETTING_KEYS + ["version"]:
        value = record["attributes"].get(key)
        if not isinstance(value, str):
            continue
        for seg in segments(value):
            if len(seg) < 3 or build.JUNK.search(seg) or JUNKISH.search(seg) or build.bad(seg) or SEG_COMMENTARY.search(seg):
                continue
            if build.norm(seg) and build.norm(seg) not in [build.norm(s) for s in out]:
                out.append(seg)
    return out


def subject_of(record, records):
    label = build.label_of(record)
    targets = [records[l["target_id"]] for rel in build.TARGET_RELATIONS for l in record["links"]
               if l["relation"] == rel and l["target_id"] in records]
    names = []
    for t in targets:
        if build.clean_label(t["name"]) not in names:
            names.append(build.clean_label(t["name"]))
    if names and not any(build.norm(t) in build.norm(label) or build.norm(label) in build.norm(t) for t in names):
        return label, f"{label}, a configuration of {' and '.join(names[:2])}"
    if names and build.norm(label) == build.norm(names[0]):
        return label, f"Configuration of {names[0]}"
    return label, label


def fix_version(text):
    def repl(m):
        value = m.group(1)
        if VERSION.match(value):
            return m.group(0)
        if SIZE.match(value):
            return f"{value} checkpoint"
        return value
    return re.sub(r"(?<=: |; )version ([^;,]+?)(?=[;,]|\.$|$)", repl, text)


def fix_configuration(record, records, desc):
    rules = []
    label, subject = subject_of(record, records)
    new = desc
    # A ProteinGym snapshot commit is the scores' version, not the model's.
    sha = record["attributes"].get("version")
    if isinstance(sha, str) and SHA.match(sha) and f"version {sha}" in new:
        new = f"{subject}, from the ProteinGym reference scores at commit {sha[:8]}."
        return new, ["snapshot-commit"]
    m = re.match(r"^((?:Configuration of )?)([^:]{2,120}): \2: ", new)
    if m:
        new = f"{m.group(1)}{m.group(2)}: " + new[m.end():]
        rules.append("label-repeat")
    fixed = fix_version(new)
    if fixed != new:
        new, rules = fixed, rules + ["version"]
    if ": " in new and not new.startswith("Entry in "):
        head, tail = new.split(": ", 1)
        kept = [s for s in tail.rstrip(".").split("; ") if not SEG_COMMENTARY.search(s)]
        if kept and len(kept) < len(tail.rstrip(".").split("; ")):
            new, rules = f"{head}: {'; '.join(kept)}.", rules + ["source-commentary"]
        head, tail = new.split(": ", 1)
        thin = build.norm(tail) in build.norm(record["name"]) or build.norm(tail) in build.norm(head)
        cut = re.search(r"\b(conv|approx|vs|e\.g|i\.e)\.$", new)
        if thin or cut:
            settings = real_settings(record)
            if settings:
                new = f"{head}: {'; '.join(settings[:3])}."
            else:
                new = f"{subject}{NEW_PHRASE}"
            rules.append("name-only-detail")
    if new.endswith(SETTINGS_PHRASE) or new.endswith("; its model version and settings are not identified."):
        settings = [s for s in real_settings(record) if build.norm(s) not in build.norm(record["name"])]
        if settings:
            head = new.rsplit("; ", 1)[0]
            new, rules = f"{head}: {'; '.join(settings[:3])}.", rules + ["dropped-settings"]
        elif new.endswith(SETTINGS_PHRASE):
            new, rules = new[: -len(SETTINGS_PHRASE)] + NEW_PHRASE, rules + ["settings-phrase"]
    if len(new) > 320:
        cut_at = new.rfind("; ", 0, 300)
        new = new[:cut_at].rstrip(".;, ") + "."
    return new, rules


def main():
    records = build.read_store()
    build.BENCHMARK_WORDS.update(build.norm(r["name"]) for r in records.values()
                                 if r["kind"] == "benchmark" and len(build.norm(r["name"])) >= 5)
    applied = {r["record_id"]: r["new_value"] for r in csv.DictReader(open(f"{HERE}/corrections.csv"))
               if r["field"] == "description"}
    rows, counts = [], {}
    for rid, written in sorted(applied.items()):
        record = records[rid]
        if record["description"] != written:
            raise SystemExit(f"{rid}: the store no longer holds the corrections.csv description")
        if rid in REVIEWED:
            new, evidence = REVIEWED[rid]
            rules = ["reviewed"]
        elif record["kind"] == "configuration":
            new, rules = fix_configuration(record, records, written)
            evidence = RULE.format(rule=", ".join(rules))
        else:
            continue
        if new == written or not rules:
            continue
        if build.bad(new):
            raise SystemExit(f"{rid}: fixed description still carries provenance: {new}")
        for rule in rules:
            counts[rule] = counts.get(rule, 0) + 1
        rows.append({"record_id": rid, "field": "description", "old_value": written, "new_value": new, "evidence": evidence})
    with open(f"{HERE}/review-corrections.csv", "w", newline="") as out:
        w = csv.DictWriter(out, fieldnames=["record_id", "field", "old_value", "new_value", "evidence"], lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} descriptions fixed", dict(sorted(counts.items())))


if __name__ == "__main__":
    main()
