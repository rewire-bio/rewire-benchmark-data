"""Parse Supplementary Table S9 (TorchCraft runtime) from the pinned arXiv v1 PDF.

The table is the only complete numeric table in the preprint. Every row label, every column
header and the cell count are asserted, so a changed layout fails rather than silently moving a
value into the wrong column.

Usage:
    python3 data/omics/torchcraft-20261115/extract/parse_runtime_table.py [<artifact>]

<artifact> is the PDF (sha256 f8145b5b...) or a `pdftotext -layout` text layer of it (sha256
90f1da5f...). Without an argument the script looks at $TORCHCRAFT_ARTIFACT, then at the path the
extraction used, and finally falls back to the runtime-table.tsv this script wrote at extraction
time, printing a warning. Neither the PDF nor its text layer is committed: the arXiv licence
(http://arxiv.org/licenses/nonexclusive-distrib/1.0/) grants no redistribution right. Refetch the
PDF from https://arxiv.org/pdf/2609.19770v1 and pass it to re-run the parse from the source bytes.

Output: JSON on stdout, {"<Code> <Operator>": {"<length>": "<printed value>"}}, and
extract/runtime-table.tsv beside this script.
"""

import hashlib
import json
import os
import pathlib
import re
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
TSV = HERE / "runtime-table.tsv"

PDF_SHA256 = "f8145b5b95552dd30996eda2940507c0f32d09adfc60f44f28458e7872788f21"
TEXT_SHA256 = "90f1da5f8a936766087beba0ade3f038f5b69504b9f581b42f2391f5640c5e6b"
DEFAULT_PATHS = [
    "/private/tmp/claude-501/-Users-timrichardson-Documents-projects-personal-blog/"
    "2b3e629e-c97e-4855-9278-c3793c720747/scratchpad/tc-dl/arxiv-v1-layout.txt",
    "/private/tmp/claude-501/-Users-timrichardson-Documents-projects-personal-blog/"
    "2b3e629e-c97e-4855-9278-c3793c720747/scratchpad/tc-dl/arxiv-2609.19770v1.pdf",
]

ROWS = ["NPU w/ FA", "NPU w/o FA", "GPU w/ cuequivariance", "GPU w/o cuequivariance"]
MACHINES = {"NPU w/ FA": "910B (64G)", "NPU w/o FA": "910B (64G)",
            "GPU w/ cuequivariance": "A100 (80G)", "GPU w/o cuequivariance": "A100 (80G)"}
LENGTHS = ["100", "200", "300", "400", "500"]
EXPECTED = {
    "NPU w/ FA": ["3.1", "3.75", "6.23", "11.29", "16.56"],
    "NPU w/o FA": ["3.0", "4.13", "8.63", "14.64", "33.47"],
    "GPU w/ cuequivariance": ["3.92", "4.27", "4.54", "5.85", "7.59"],
    "GPU w/o cuequivariance": ["4.76", "7.96", "13.08", "21.65", "33.3"],
}


def sha256(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def text_layer(path):
    """The text layer of `path`, which may be the PDF or an existing text layer."""
    digest = sha256(path)
    if digest == TEXT_SHA256:
        return pathlib.Path(path).read_text(encoding="utf-8", errors="strict")
    if digest != PDF_SHA256:
        sys.exit(
            "unexpected artifact " + str(path) + "\n  sha256 " + digest +
            "\n  expected the PDF (" + PDF_SHA256 + ") or its text layer (" + TEXT_SHA256 + ")"
        )
    with tempfile.TemporaryDirectory() as tmp:
        out = pathlib.Path(tmp) / "layout.txt"
        subprocess.run(["pdftotext", "-layout", str(path), str(out)], check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        produced = sha256(out)
        if produced != TEXT_SHA256:
            sys.exit(
                "pdftotext produced a different text layer (" + produced + " rather than " +
                TEXT_SHA256 + "); a different poppler build changes the layout, so re-check the "
                "parse by hand before trusting it"
            )
        return out.read_text(encoding="utf-8")


def find_artifact():
    if len(sys.argv) > 1:
        return sys.argv[1]
    env = os.environ.get("TORCHCRAFT_ARTIFACT")
    if env:
        return env
    for candidate in DEFAULT_PATHS:
        if pathlib.Path(candidate).exists():
            return candidate
    return None


def parse(text):
    lines = text.splitlines()
    captions = [i for i, line in enumerate(lines) if line.strip().startswith("Table S9 TorchCraft runtime")]
    if len(captions) != 1:
        sys.exit("expected exactly one Table S9 caption, found " + str(len(captions)))
    caption = captions[0]
    header = None
    for i in range(caption, min(len(lines), caption + 20)):
        if re.match(r"\s*Code\s+Operator\s+Machine\s", lines[i]):
            header = i
            break
    if header is None:
        sys.exit("no 'Code Operator Machine' header line within 20 lines of the Table S9 caption")
    headers = re.findall(r"(\d+) aa", lines[header])
    if headers != LENGTHS:
        sys.exit("column headers are " + str(headers) + ", expected " + str(LENGTHS))

    values = {}
    for i in range(header + 1, min(len(lines), header + 12)):
        line = lines[i]
        for label in ROWS:
            pattern = r"^\s*" + label.replace("/", r"/").replace(" ", r"\s+") + r"\s+" + re.escape(MACHINES[label]) + r"\s+(.*)$"
            match = re.match(pattern, line)
            if not match:
                continue
            if label in values:
                sys.exit("row " + label + " appears twice")
            cells = [c for c in re.split(r"\s{2,}", match.group(1).strip()) if c]
            cells = [re.sub(r"[^\d.]", "", c) for c in cells]
            if len(cells) != 5:
                sys.exit("row " + label + " parsed to " + str(len(cells)) + " cells: " + str(cells))
            values[label] = cells
    missing = [label for label in ROWS if label not in values]
    if missing:
        sys.exit("rows not found: " + ", ".join(missing))
    if values != EXPECTED:
        sys.exit("parsed values differ from the values this script was written against:\n  parsed   " +
                 json.dumps(values) + "\n  expected " + json.dumps(EXPECTED))
    return values


def main():
    artifact = find_artifact()
    if artifact:
        values = parse(text_layer(artifact))
        rows = ["\t".join(["code_operator", "machine"] + [length + " aa" for length in LENGTHS])]
        rows += ["\t".join([label, MACHINES[label]] + values[label]) for label in ROWS]
        TSV.write_text("\n".join(rows) + "\n", encoding="utf-8")
    else:
        if not TSV.exists():
            sys.exit(
                "no artifact and no runtime-table.tsv. Refetch https://arxiv.org/pdf/2609.19770v1 "
                "and pass its path, or set TORCHCRAFT_ARTIFACT."
            )
        print("warning: no artifact available; reading the parse output " + str(TSV) +
              ". Pass the PDF to parse from the source bytes.", file=sys.stderr)
        values = {}
        lines = TSV.read_text(encoding="utf-8").strip().splitlines()
        head = lines[0].split("\t")
        if head != ["code_operator", "machine"] + [length + " aa" for length in LENGTHS]:
            sys.exit("runtime-table.tsv header is " + str(head))
        for line in lines[1:]:
            parts = line.split("\t")
            values[parts[0]] = parts[2:]
        if values != EXPECTED:
            sys.exit("runtime-table.tsv does not match the parsed values this script asserts")
    print(json.dumps({label: dict(zip(LENGTHS, values[label])) for label in ROWS}, indent=1))


if __name__ == "__main__":
    main()
