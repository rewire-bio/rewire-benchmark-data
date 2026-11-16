"""Check every transcribed value in batch.jsonl against the pinned artifacts.

`npm run batch -- check-values` cannot place these values: the preprint's table captions carry no
colon or full stop after the label ("Table S9 TorchCraft runtime benchmark ..."), which its caption
pattern requires, so all 20 Table S9 results come back `row_not_found`, and the other 11 values are
printed in figure captions and prose, which it lists as `locator_not_parsed`. This script is the
extraction-side check: it asserts each printed string in the whitespace-normalised text layer, and
cross-checks the runtime table against the copy on the official project site.

Usage, from the repository root:
    python3 data/omics/torchcraft-20261115/extract/check_transcriptions.py \
        <arxiv-v1-layout.txt or arxiv PDF> [<project-site.html>]

Exits non-zero on the first value it cannot place.
"""

import hashlib
import json
import pathlib
import re
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
BATCH = json.loads("[" + ",".join((HERE.parent / "batch.jsonl").read_text(encoding="utf-8").strip().splitlines()) + "]")

PDF_SHA256 = "f8145b5b95552dd30996eda2940507c0f32d09adfc60f44f28458e7872788f21"
TEXT_SHA256 = "90f1da5f8a936766087beba0ade3f038f5b69504b9f581b42f2391f5640c5e6b"
SITE_SHA256 = "fa95060dad51bd3e04278b48c7e3bc62c66f8f909db3871e654f79d5a98dcd3c"

# Printed strings each result must be found in, as printed in the preprint.
FRAGMENTS = {
    "minibinder-kd": "Apparent dissociation constants of the displayed binders were 60.2, 8.55, 2.04, and 23.3 nM, respectively.",
    "minibinder-kd-body": "with representative apparent dissociation constants of 60.2, 8.55, 2.04, and 23.3 nM, respectively",
    "vhh-kd": "Apparent dissociation constants of the displayed binders were 24.3, 122, 268, and 354 nM, respectively.",
    "vhh-kd-body": "with representative apparent dissociation constants of 24.3, 122, 268, and 354 nM, respectively",
    "classifier": "MCC = 0.598; Pearson r = −0.538; Spearman ρ = −0.602",
    "expression-cutoff": "high-expression cutoff of 0.08 mg",
    "threshold-figure": "The selected threshold of 6.309 maximizes the Matthews correlation coefficient",
    "threshold-methods": "ESM2-150M perplexity had to be below 6.31",
    "minibinder-pool": "Candidates were selected from 3,000 generated designs per target",
    "vhh-pool": "For each VHH target, 12,500 TorchCraft candidates were generated",
    "af3-weights": "All designs reported in this study used pretrained AF3 weights",
    "torchscore-weights": "TorchScore used pretrained AF3 weights, the same checkpoint used for design",
    "torchscore-no-refold": "they were not refolded from sequence by TorchScore",
    "oom-footnote": "Batch size 1; batch size 2 exceeded memory (OOM)",
}
# Panel labels that print the same KD values a second time.
PANEL_LABELS = ["KD: 60.2nM", "KD: 8.55nM", "KD: 2.04nM", "KD: 23.3nM",
                "KD: 24.3nM", "KD: 122nM", "KD: 268nM", "KD: 354nM"]


def sha256(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def text_layer(path):
    digest = sha256(path)
    if digest == TEXT_SHA256:
        return pathlib.Path(path).read_text(encoding="utf-8")
    if digest != PDF_SHA256:
        sys.exit("unexpected artifact " + str(path) + " (sha256 " + digest + ")")
    with tempfile.TemporaryDirectory() as tmp:
        out = pathlib.Path(tmp) / "layout.txt"
        subprocess.run(["pdftotext", "-layout", str(path), str(out)], check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if sha256(out) != TEXT_SHA256:
            sys.exit("pdftotext produced a different text layer; re-check the transcription by hand")
        return out.read_text(encoding="utf-8")


def flat(text):
    return re.sub(r"\s+", " ", text)


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    text = flat(text_layer(sys.argv[1]))
    failures = []

    for name, fragment in FRAGMENTS.items():
        count = text.count(flat(fragment))
        if count != 1:
            failures.append("fragment " + name + " occurs " + str(count) + " times, expected 1")
    for label in PANEL_LABELS:
        if text.count(label) != 1:
            failures.append("panel label " + label + " occurs " + str(text.count(label)) + " times, expected 1")

    # Every result's printed value must appear in the fragment its locator names.
    results = [r for r in BATCH if r["kind"] == "result"]
    if len(results) != 31:
        failures.append("expected 31 results, found " + str(len(results)))
    for r in results:
        value = r["attributes"]["printed_value"]
        locator = r["attributes"]["source_locator"]
        if "Table S9" in locator:
            row = re.search(r'row "([^"]+)"', locator).group(1)
            column = re.search(r'column "([^"]+)"', locator).group(1)
            tsv = [line.split("\t") for line in (HERE / "runtime-table.tsv").read_text(encoding="utf-8").strip().splitlines()]
            head, body = tsv[0], tsv[1:]
            cell = next((line[head.index(column)] for line in body if line[0] == row), None)
            if cell != value:
                failures.append(r["id"] + ": parse gives " + str(cell) + ", record says " + value)
            continue
        if "Figure 2a" in locator:
            source = FRAGMENTS["minibinder-kd"]
        elif "Figure 3a" in locator:
            source = FRAGMENTS["vhh-kd"]
        elif "Figure S4" in locator:
            source = FRAGMENTS["classifier"]
        else:
            failures.append(r["id"] + ": locator not covered by this check: " + locator)
            continue
        if value not in source:
            failures.append(r["id"] + ": printed value " + value + " is not in the quoted fragment")

    # The four KD values of each campaign must be in target order in the caption sentence.
    for fmt, order in (("minibinder", ["ifnar2", "il7ra", "pdgfrb", "pdl1"]),
                       ("vhh", ["bhrf1", "efna5", "pdgfrb", "s100a4"])):
        wanted = [next(r["attributes"]["printed_value"] for r in results if r["id"].endswith("kd-" + fmt + "-" + slug)) for slug in order]
        printed = re.search(r"displayed binders were (.+?) nM, respectively\.", FRAGMENTS[fmt + "-kd"]).group(1)
        listed = [v.strip() for v in printed.replace(" and ", ", ").split(",") if v.strip()]
        if listed != wanted:
            failures.append(fmt + " KD order: caption lists " + str(listed) + ", records give " + str(wanted))

    # Cross-check the runtime table against the official project site, if it was passed.
    if len(sys.argv) > 2:
        if sha256(sys.argv[2]) != SITE_SHA256:
            failures.append("project site artifact does not match the pinned hash")
        else:
            site = flat(re.sub(r"<[^>]+>", " ", pathlib.Path(sys.argv[2]).read_text(encoding="utf-8")))
            for line in (HERE / "runtime-table.tsv").read_text(encoding="utf-8").strip().splitlines()[1:]:
                parts = line.split("\t")
                if " ".join(parts[2:]) not in site:
                    failures.append("project site does not print the row " + parts[0] + " as " + " ".join(parts[2:]))

    if failures:
        print("\n".join(failures))
        sys.exit(str(len(failures)) + " transcription checks failed")
    print(json.dumps({"results_checked": len(results), "fragments_checked": len(FRAGMENTS) + len(PANEL_LABELS),
                      "site_cross_check": len(sys.argv) > 2}, indent=1))


if __name__ == "__main__":
    main()
