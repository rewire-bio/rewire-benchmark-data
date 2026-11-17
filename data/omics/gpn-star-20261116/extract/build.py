"""Build data/omics/gpn-star-20261116/batch.jsonl from the pinned GPN-Star artifacts.

Usage:
    python3 extract/build.py <nature-article.pdf> <nature-supplementary.pdf> <biorxiv-v1.pdf> <hf-collection.json>

The script hashes each artifact and refuses to run if a hash differs from the pinned value.
It then renders the two Nature PDFs with `pdftotext -layout` (poppler 26.08.0) and parses:

  * Supplementary Information, Supplementary Table 3 (ablation studies): 8 rows x 7 benchmark
    columns, each cell printed as "mean (max)" over three random initializations. Row labels,
    column headers and cell counts are asserted.
  * Article Fig. 4b: the printed odds-ratio labels for 12 scores. Panel b labels end before
    column 105 and their value labels sit between columns 106 and 160, which separates them
    from the panel c axis ticks and the panel d legend; the label set and count are asserted.
  * Article Results, the RVAT paragraph: the four printed gene counts, asserted by matching the
    sentences that carry them.
  * Supplementary Information, Supplementary Table 1 (training setups): the 19 rows are
    transcribed here by hand because the printed table merges cells down each group; every
    transcribed per-row value is asserted to appear on that row's line in the text layer, and
    every group-shared value to appear in the table block.

Nothing is read from a figure without printed numbers. Figs. 2, 3, 4a, 4c, 4d, Extended Data
Figs. 1-10 and Supplementary Figs. 1-27 carry no printed values and are recorded as gaps in
notes.md instead.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

BATCH = "gpn-star-20261116"
P = BATCH  # id prefix

SHA_ARTICLE = "d7dfe801bad2a0a23478753147af2320bc31c8b37ee50d66f1a1af8385e9005d"
SHA_SI = "3f7e8f71710bb63ec5ff032e697b6ef85f0d6d74411a31865fed73a757c7fc9e"
SHA_PREPRINT = "ec829bce7b9192a6a396f29d4ab90ac5de6c4903232bdf9328eb1c53e626af7a"
SHA_HF = "4e8141d673c18e6ab131eba8e1cbef7f29aa4403d5a4864218b06b90d07b275d"

URL_ARTICLE = "https://www.nature.com/articles/s41586-026-11005-5.pdf"
URL_SI = (
    "https://static-content.springer.com/esm/art%3A10.1038%2Fs41586-026-11005-5/"
    "MediaObjects/41586_2026_11005_MOESM1_ESM.pdf"
)
URL_PREPRINT = "https://www.biorxiv.org/content/biorxiv/early/2025/09/21/2025.09.21.677619.full.pdf"
URL_HF = "https://huggingface.co/api/collections/songlab/gpn-star-68c0c055acc2ee51d5c4f129"

SRC_ARTICLE = f"{P}-source-nature-2026"
SRC_SI = f"{P}-source-nature-si"
SRC_PREPRINT = f"{P}-source-biorxiv-v1"
SRC_HF = f"{P}-source-hf-collection"

MODEL_GPN_STAR = "vep-uc-20261014-model-gpn-star"  # existing discovered record, reused
MODEL_GPN_MSA = "gfm-guides-20261014-gpnmsa-model-gpn-msa"
METHOD_PHYLOP = "somatic-oncogenicity-20261009-method-phylop"
METHOD_PHASTCONS = "somatic-oncogenicity-20261009-method-phastcons"
METHOD_CADD = "somatic-oncogenicity-20261009-method-cadd"
DATA_COSMIC = "gfm-guides-20261014-gpnmsa-data-cosmic-frequent-vs-gnomad-common-missense"
DATA_OMIM = "lit-genomics-20261011-traitgym-data-mendelian-traits-matched-9"
DATA_COMPLEX = "lit-genomics-20261011-traitgym-data-complex-traits-matched-9"

DATE = "2026-11-16"
AREAS = ["dna-genomes"]
# clinical_research is kept for the records about human disease variants: the paper itself, the
# benchmark suite, and the ClinVar, OMIM, HGMD and fine-mapped datasets and protocols. Everything
# else in this batch (ablation models, conservation tracks, gnomAD frequency data, the non-human
# training setups) is research context only.
CONTEXTS = ["research"]
CONTEXTS_CLINICAL = ["research", "clinical_research"]
CLINICAL_DATASETS = {"clinvar", "hgmd", "finemapped-coding"}
CLINICAL_PROTOCOLS = {"clinvar-auprc", "hgmd-auprc", "omim-auprc", "finemapped-coding-auprc",
                      "finemapped-noncoding-auprc"}
EXTRACTOR = "Claude extraction agent; no human review claimed"

PARSE_NOTE = (
    "Extraction: pdftotext 26.08.0 -layout text layer of the pinned PDF, parsed by "
    f"data/omics/{BATCH}/extract/build.py, which asserts the artifact hash, the table row "
    "labels, the column headers and the cell count. Review sign-off is left to review-evidence."
)
TRANSCRIBE_NOTE = (
    "Extraction: transcribed by hand from the pdftotext 26.08.0 -layout text layer of the "
    f"pinned PDF; data/omics/{BATCH}/extract/build.py asserts that each transcribed string "
    "appears at the stated location. Review sign-off is left to review-evidence."
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pages(pdf: Path, expected: str) -> list[str]:
    got = sha256(pdf)
    assert got == expected, f"{pdf}: sha256 {got} != pinned {expected}"
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "text.txt"
        subprocess.run(["pdftotext", "-layout", str(pdf), str(out)], check=True)
        return out.read_text(encoding="utf-8").split("\f")


# --------------------------------------------------------------------------------------
# Supplementary Table 3: ablation studies
# --------------------------------------------------------------------------------------

ABLATION_ROWS = [
    ("gpn-star-default", "GPN-Star default"),
    ("one-target-species-human", "only use one target species (human)"),
    ("no-evol-distance-encoding", "no evol. distance encoding"),
    ("no-pooling-into-clades", "no pooling into clades"),
    ("no-species-tree", "no species tree (no evol. distances, no clades)"),
    ("msa-transformer-like", "MSA Transformer-like architecture"),
    ("gpn-msa-exclude-10-closest-species", "GPN-MSA (exclude 10 closest species)"),
    ("gpn-msa-no-species-curation", "GPN-MSA (no species curation)"),
]

# column key, printed header, protocol slug
ABLATION_COLUMNS = [
    ("clinvar", "ClinVar", "clinvar-auprc"),
    ("cosmic", "COSMIC", "cosmic-auprc"),
    ("proteingym", "ProteinGym", "proteingym-spearman"),
    ("finemapped-coding", "Finemapped coding", "finemapped-coding-auprc"),
    ("omim", "OMIM", "omim-auprc"),
    ("finemapped-noncoding", "Finemapped non-coding", "finemapped-noncoding-auprc"),
    ("hgmd", "HGMD", "hgmd-auprc"),
]

CELL = re.compile(r"(\d\.\d{3}) \((\d\.\d{3})\)")


def parse_supp_table_3(si: list[str]) -> dict[str, dict[str, tuple[str, str, str]]]:
    page_index = next(i for i, p in enumerate(si) if "Supplementary Table 3: Ablation studies" in p)
    assert page_index + 1 == 23, f"Supplementary Table 3 moved to PDF page {page_index + 1}"
    page = si[page_index]
    lines = page.splitlines()

    header = next(l for l in lines if "ClinVar" in l and "COSMIC" in l and "ProteinGym" in l)
    above = lines[lines.index(header) - 1]
    below = lines[lines.index(header) + 1]
    assert above.count("Finemapped") == 2, above
    assert "coding" in below and "non-coding" in below, below
    order = [m.group(0) for m in re.finditer(r"ClinVar|COSMIC|ProteinGym|OMIM|HGMD", header)]
    assert order == ["ClinVar", "COSMIC", "ProteinGym", "OMIM", "HGMD"], order

    # Body lines are the lines that print seven "mean (max)" cells. The caption also mentions
    # the MSA Transformer-like architecture, so a row label alone does not identify a row.
    body = [l for l in lines if len(CELL.findall(l)) == 7]
    assert len(body) == 8, f"{len(body)} body lines"

    out: dict[str, dict[str, tuple[str, str, str]]] = {}
    for index, (slug, label) in enumerate(ABLATION_ROWS):
        row = [l for l in body if label in l]
        assert len(row) == 1, f"{label}: {len(row)} matching body lines"
        assert row[0] == body[index], f"{label}: printed in row {body.index(row[0]) + 1}"
        cells = list(CELL.finditer(row[0]))
        starts = [c.start() for c in cells]
        assert starts == sorted(starts)
        out[slug] = {
            key: (m.group(1), m.group(2), m.group(0))
            for (key, _, _), m in zip(ABLATION_COLUMNS, cells)
        }
    assert len(out) == 8
    return out


# --------------------------------------------------------------------------------------
# Fig. 4b: printed odds ratios
# --------------------------------------------------------------------------------------

FIG4B_SCORES = [
    ("gpn-star-v", "GPN-Star (V)"),
    ("gpn-star-m", "GPN-Star (M)"),
    ("gpn-star-p", "GPN-Star (P)"),
    ("gpn-msa", "GPN-MSA"),
    ("phylop-v", "PhyloP (V)"),
    ("phylop-m", "PhyloP (M)"),
    ("phylop-p", "PhyloP (P)"),
    ("phastcons-v", "PhastCons (V)"),
    ("phastcons-m", "PhastCons (M)"),
    ("phastcons-p", "PhastCons (P)"),
    ("cadd", "CADD"),
    ("roulette", "Roulette mutation rate"),
]


def parse_fig_4b(article: list[str]) -> dict[str, str]:
    page_index = next(
        i for i, p in enumerate(article) if "Fig. 4 | GPN-Star scores reflect evolutionary" in p
    )
    assert page_index + 1 == 7, f"Fig. 4 moved to PDF page {page_index + 1}"
    page = article[page_index]
    assert "n = 5.5M versus 5.6M" in page
    out: dict[str, str] = {}
    for line in page.splitlines():
        for slug, label in FIG4B_SCORES:
            hit = re.search(re.escape(label), line)
            if not hit or hit.end() > 105:
                continue
            values = [
                m.group(1) for m in re.finditer(r"(\d+\.\d+)", line[106:161])
            ]
            assert len(values) == 1, f"{label}: value labels {values} on {line!r}"
            assert slug not in out, f"{label} twice"
            out[slug] = values[0]
    assert len(out) == 12, sorted(out)
    assert out["gpn-star-v"] == "58.4" and out["roulette"] == "1.1", out
    return out


# --------------------------------------------------------------------------------------
# RVAT gene counts printed in the Results
# --------------------------------------------------------------------------------------

def parse_rvat(article: list[str]) -> dict[str, str]:
    """Read the four printed RVAT gene counts.

    The page is set in two columns, so a sentence is split across one text-layer line. Each
    phrase below is asserted within a single line, after collapsing runs of spaces.
    """
    page = article[4]
    assert "RVAT experiments using DeepRVAT" in page
    lines = [re.sub(r"\s+", " ", l).strip() for l in page.splitlines()]
    phrases = [
        "average across runs, 402 genes compared with 383 from the original",
        "age 353 compared with 338), indicating high robustness",
        "the number of discovered genes at a family-wise error rate <0.05",
        "experiments using DeepRVAT on 34 quantitative traits in UK Biobank",
        "ancestry, retaining variants with minor allele frequency (MAF) <0.1%",
    ]
    for phrase in phrases:
        assert any(phrase in l for l in lines), f"{phrase!r} not on one line of PDF page 5"
    assert any("161,822 unrelated individuals of European" in l for l in lines)
    return {"discovered-gpn-star": "402", "discovered-original": "383",
            "replicated-gpn-star": "353", "replicated-original": "338"}


# --------------------------------------------------------------------------------------
# Supplementary Table 1: training setups (hand transcription, asserted)
# --------------------------------------------------------------------------------------

# group key -> fields printed once for the whole group
GROUPS = {
    "hg38-vertebrate": dict(
        assembly="hg38", assembly_size="3.1Gbp", train_chr="1-20, X, Y", val_chr="21",
        test_chr="22", wga="multiz100way", species="100 vertebrates", phi_clade="0.2",
        clades="45", context="128bp", organism="Homo sapiens", timescale="vertebrate",
    ),
    "hg38-mammal": dict(
        assembly="hg38", assembly_size="3.1Gbp", train_chr="1-20, X, Y", val_chr="21",
        test_chr="22", wga="cactus447way", species="447 mammals", phi_clade="0.05",
        clades="145", context="256bp", organism="Homo sapiens", timescale="mammal",
    ),
    "hg38-primate": dict(
        assembly="hg38", assembly_size="3.1Gbp", train_chr="1-20, X, Y", val_chr="21",
        test_chr="22", wga="cactus447way", species="243 primates", phi_clade="0.05",
        clades="21", context="256bp", organism="Homo sapiens", timescale="primate",
    ),
    "mm39": dict(
        assembly="mm39", assembly_size="2.7Gbp", train_chr="1-17, X, Y", val_chr="18",
        test_chr="19", wga="multiz35way", species="35 vertebrates", phi_clade="0.2",
        clades="26", context="128bp", organism="Mus musculus", timescale=None,
    ),
    "galGal6": dict(
        assembly="galGal6", assembly_size="1.1Gbp", train_chr="1-24, Z, W", val_chr="25-28",
        test_chr="30-33", wga="multiz77way", species="77 vertebrates", phi_clade="0.2",
        clades="29", context="128bp", organism="Gallus gallus", timescale=None,
    ),
    "dm6": dict(
        assembly="dm6", assembly_size="144Mbp", train_chr="2L, 3L, 3R, X, Y", val_chr="2R",
        test_chr="4", wga="multiz124way", species="124 insects", phi_clade="0.2",
        clades="93", context="128bp", organism="Drosophila melanogaster", timescale=None,
    ),
    "ce11": dict(
        assembly="ce11", assembly_size="100Mbp", train_chr="II, IV, V, X", val_chr="I",
        test_chr="III", wga="multiz135way", species="135 nematodes", phi_clade="0.2",
        clades="92", context="128bp", organism="Caenorhabditis elegans", timescale=None,
    ),
    "tair10": dict(
        assembly="tair10", assembly_size="120Mbp", train_chr="1-3", val_chr="4",
        test_chr="5", wga="multiz18way", species="18 Brassicaceae", phi_clade="0.05",
        clades="18", context="256bp", organism="Arabidopsis thaliana", timescale=None,
    ),
}

# checkpoint name -> (group, model size, learning rate, training steps, training time)
CHECKPOINTS = [
    ("hg38-vertebrate-200m", "hg38-vertebrate", "200 M", "5e-5", "200 k", "4.5 d"),
    ("hg38-vertebrate-85m", "hg38-vertebrate", "85 M", "1e-4", "150 k", "1.8 d"),
    ("hg38-vertebrate-25m", "hg38-vertebrate", "25 M", "1e-4", "150 k", "0.9 d"),
    ("hg38-mammal-200m", "hg38-mammal", "200 M", "5e-5", "200 k", "6.6 d"),
    ("hg38-mammal-85m", "hg38-mammal", "85 M", "1e-4", "150 k", "2.9 d"),
    ("hg38-mammal-25m", "hg38-mammal", "25 M", "1e-4", "150 k", "1.2 d"),
    ("hg38-primate-200m", "hg38-primate", "200 M", "5e-5", "200 k", "4.2 d"),
    ("hg38-primate-85m", "hg38-primate", "85 M", "1e-4", "150 k", "1.6 d"),
    ("hg38-primate-25m", "hg38-primate", "25 M", "1e-4", "150 k", "0.8 d"),
    ("mm39-85m", "mm39", "85 M", "1e-4", "150 k", "1.6 d"),
    ("mm39-25m", "mm39", "25 M", "1e-4", "150 k", "0.7 d"),
    ("galGal6-85m", "galGal6", "85 M", "1e-4", "150 k", "1.7 d"),
    ("galGal6-25m", "galGal6", "25 M", "1e-4", "150 k", "0.7 d"),
    ("dm6-85m", "dm6", "85 M", "1e-4", "50 k", "0.8 d"),
    ("dm6-25m", "dm6", "25 M", "1e-4", "50 k", "0.3 d"),
    ("ce11-85m", "ce11", "85 M", "1e-4", "50 k", "0.8 d"),
    ("ce11-25m", "ce11", "25 M", "1e-4", "50 k", "0.3 d"),
    ("tair10-85m", "tair10", "85 M", "1e-4", "50 k", "0.5 d"),
    ("tair10-25m", "tair10", "25 M", "1e-4", "50 k", "0.2 d"),
]

ARCHITECTURE = [
    ("Num encoder blocks (K)", "8", "12", "16"),
    ("Hidden dim (H)", "512", "768", "1024"),
    ("Intermediate size (F)", "2048", "3072", "4096"),
    ("Num self-attn heads (A)", "4", "6", "8"),
    ("Num cross-attn heads (A)", "4", "6", "8"),
    ("Attn head dim (D)", "64", "64", "64"),
    ("Dropout rate", "0.1", "0.1", "0.1"),
]


def check_supp_table_1(si: list[str]) -> None:
    page_index = next(
        i for i, p in enumerate(si) if "Supplementary Table 1: A summary of the training setups" in p
    )
    assert page_index + 1 == 21, f"Supplementary Table 1 moved to PDF page {page_index + 1}"
    block = si[page_index]
    lines = block.splitlines()
    for name, group, size, lr, steps, time in CHECKPOINTS:
        row = [l for l in lines if re.search(rf"\b{re.escape(name)}\b", l)]
        assert len(row) == 1, f"{name}: {len(row)} matching lines"
        for value in (size, lr, steps, time):
            assert value in row[0], f"{name}: {value!r} not on its row"
    for group, fields in GROUPS.items():
        for key in ("assembly", "assembly_size", "train_chr", "val_chr", "test_chr", "wga",
                    "species", "phi_clade", "clades", "context"):
            value = fields[key]
            if key == "train_chr":
                # printed over two lines inside the merged cell
                for part in [p.strip() for p in value.split(",")]:
                    assert part in block, f"{group}: {part!r} not in the table block"
                continue
            assert value in block, f"{group}: {value!r} ({key}) not in the table block"
    # Supplementary Table 10, architecture hyperparameters
    arch_index = next(
        i for i, p in enumerate(si) if "Supplementary Table 10: Hyperparameters of the GPN-Star" in p
    )
    assert arch_index + 1 == 27, f"Supplementary Table 10 moved to PDF page {arch_index + 1}"
    arch = si[arch_index]
    for label, a, b, c in ARCHITECTURE:
        row = [l for l in arch.splitlines() if label in l]
        assert len(row) == 1, f"{label}: {len(row)} matching lines"
        assert a in row[0] and b in row[0] and c in row[0], f"{label}: values not on its row"


def check_fig_5a(article: list[str]) -> None:
    """Assert the Fig. 5a bar labels that notes.md lists as an unextracted gap.

    Fig. 5a prints 15 odds ratios, three scores in each of five species panels, but the labels do
    not sit beside a row label: assigning one to a species and a score means grouping the labels
    by horizontal position and taking the bar order from the legend. That is an inference about
    the figure, so the panel is recorded as a gap rather than extracted. The values are asserted
    here so the gap note stays true to the artifact.
    """
    page_index = next(
        i for i, p in enumerate(article) if "Fig. 5 | Application of GPN-Star to non-human" in p
    )
    assert page_index + 1 == 8, f"Fig. 5 moved to PDF page {page_index + 1}"
    page = article[page_index]
    printed = re.findall(r"\d+\.\d+", page)
    expected = ["38.7", "186.3", "440.8", "37.0", "29.1", "43.4", "88.9", "7.0", "5.5", "5.3",
                "4.0", "1.8", "3.1", "3.8", "2.7"]
    for value in expected:
        assert value in printed, f"Fig. 5a label {value} not printed"
    for label in ("GPN-Star", "PhyloP", "PhastCons"):
        assert label in page, f"Fig. 5a legend entry {label} not printed"


def check_prose(article: list[str], si: list[str]) -> None:
    """Assert every number quoted in a claim, each within one text-layer line."""
    def lines(pages_: list[str]) -> list[str]:
        return [re.sub(r"\s+", " ", l).strip() for p in pages_ for l in p.splitlines()]

    article_lines = lines(article)
    for phrase in (
        "large proportions of missense variants (33%, 170-fold enriched)",
        "distal enhancer elements (26%,",
        "2.4-fold enriched) and their flanks (8%, 0.35-fold depleted)",
        "(v0.8), archived at Zenodo",
        "available under the MIT license",
        "DeepRVAT 1.1 (https://github.com/PMBio/deeprvat)",
        "(https://doi.org/10.5281/zenodo.21501177)",
        "(https://doi.org/10.57967/hf/9849)",
    ):
        assert any(phrase in l for l in article_lines), f"{phrase!r} not in the article"
    si_lines = lines(si)
    for phrase in (
        "fold in missense variants (Supplementary Table 7)",
        "such as missense (1.52-fold) and even synonymous (3.89-fold)",
        "multiz100way with training interval curation",
    ):
        assert any(phrase in l for l in si_lines), f"{phrase!r} not in the Supplementary "
    assert any("the former enriched 1.14-" in l for l in si_lines)


# --------------------------------------------------------------------------------------
# record helpers
# --------------------------------------------------------------------------------------

def review(sources: list[str], note: str, method: list[str]) -> dict:
    sha = {SRC_ARTICLE: SHA_ARTICLE, SRC_SI: SHA_SI, SRC_PREPRINT: SHA_PREPRINT,
           SRC_HF: SHA_HF}[sources[0]]
    url = {SRC_ARTICLE: URL_ARTICLE, SRC_SI: URL_SI, SRC_PREPRINT: URL_PREPRINT,
           SRC_HF: URL_HF}[sources[0]]
    return {
        "method": method,
        "method_note": "Source artifact hashed on retrieval; values read from its pdftotext "
                       "-layout text layer." if method != ["transcription"] else
                       "Source artifact hashed on retrieval; value transcribed by hand from its "
                       "pdftotext -layout text layer.",
        "reviewer": ["claude"],
        "reviewer_note": EXTRACTOR,
        "date": DATE,
        "artifact_sha256": sha,
        "retrieval_url": url,
        "note": note,
    }


records: list[dict] = []


def add(record: dict) -> dict:
    records.append(record)
    return record


def entity(kind: str, rid: str, name: str, description: str, sources: list[str],
           attributes: dict, links: list[dict] | None = None, facets: dict | None = None,
           status: str = "source_checked") -> dict:
    return add({
        "id": rid,
        "kind": kind,
        "name": name,
        "description": description,
        "status": status,
        "facets": facets if facets is not None else {"areas": AREAS, "contexts": CONTEXTS},
        "source_ids": sources,
        "links": links or [],
        "attributes": attributes,
    })


# --------------------------------------------------------------------------------------
# sources
# --------------------------------------------------------------------------------------

def build_sources() -> None:
    entity(
        "source", SRC_ARTICLE,
        "Ye et al. 2026, Predicting genome-wide functional constraints with GPN-Star (Nature)",
        "Peer-reviewed version of record of the GPN-Star paper, retrieved as the publisher PDF.",
        [],
        {
            "url": "https://www.nature.com/articles/s41586-026-11005-5",
            "artifact_url": URL_ARTICLE,
            "doi": "10.1038/s41586-026-11005-5",
            "version": "Version of record: Nature 659, 141-150 (5 November 2026); received "
                       "2025-09-10, accepted 2026-08-07, published online 2026-09-09",
            "retrieved_at": "2026-11-16T00:11:46Z",
            "artifact_sha256": SHA_ARTICLE,
            "publication_status": "peer_reviewed",
            "licence": "CC BY 4.0 (Open Access)",
            "media_type": "application/pdf",
            "venue": "Nature",
            "year": 2026,
            "hash_scope": "SHA-256 of the 26-page publisher PDF as downloaded. A second download "
                          "in the same session reproduced the hash byte for byte.",
            "source_locator": "Results (PDF pages 3-6); Fig. 4 (PDF page 7); Data availability "
                              "and Code availability (PDF page 10); Reporting Summary "
                              "(PDF page 23)",
            "limitations": [
                "Figs. 2 and 3, Fig. 4a,c,d, Fig. 5b-d and Extended Data Figs. 1-10 print no "
                "numerical values. Fig. 4b and Fig. 5a carry printed value labels; only Fig. 4b "
                "is extracted here, because Fig. 5a's labels can be assigned to a species and a "
                "score only by grouping them by position and taking the bar order from the "
                "legend.",
                "The store already holds vep-uc-20261014-source-gpn-star for the same article "
                "URL, pinned to the accelerated article preview PDF "
                "(97f61ec05d4ace41692549290db3faf019ce869459459d2c5694bf54e16d0996). That URL "
                "now serves this final version of record, whose bytes differ.",
            ],
            "review": review([SRC_ARTICLE], "Retrieved and hashed 2026-11-16; re-downloaded in "
                                            "the same session with an identical hash.",
                             ["source-hash-verification"]),
        },
        links=[{"relation": "supersedes", "target_id": "vep-uc-20261014-source-gpn-star"}],
        facets={"areas": AREAS, "contexts": CONTEXTS_CLINICAL},
    )
    entity(
        "source", SRC_SI,
        "Ye et al. 2026 GPN-Star, Nature Supplementary Information",
        "Supplementary Information of the GPN-Star paper: supplementary methods, 27 "
        "supplementary figures and 11 supplementary tables.",
        [],
        {
            "url": "https://doi.org/10.1038/s41586-026-11005-5",
            "artifact_url": URL_SI,
            "doi": "10.1038/s41586-026-11005-5",
            "version": "Supplementary Information PDF (MOESM1) of the version of record, 57 pages",
            "retrieved_at": "2026-11-16T00:12:33Z",
            "artifact_sha256": SHA_SI,
            "publication_status": "peer_reviewed",
            "licence": "CC BY 4.0 (Open Access)",
            "media_type": "application/pdf",
            "venue": "Nature",
            "year": 2026,
            "hash_scope": "SHA-256 of the supplementary PDF as downloaded; a second download in "
                          "the same session reproduced the hash.",
            "source_locator": "Supplementary Table 1 (PDF page 21); Supplementary Table 3 "
                              "(PDF page 23); Supplementary Tables 5-8 (PDF pages 24-26); "
                              "Supplementary Table 10 (PDF page 27); Evaluation Benchmarks "
                              "(PDF pages 11-14)",
            "limitations": [
                "Supplementary Figs. 1-27 print no numerical values.",
                "Supplementary Tables 5-8 (variant consequence distributions) were not extracted "
                "as results; see notes.md.",
            ],
            "review": review([SRC_SI], "Retrieved and hashed 2026-11-16; re-downloaded in the "
                                       "same session with an identical hash.",
                             ["source-hash-verification"]),
        },
        links=[{"relation": "companion_of", "target_id": SRC_ARTICLE}],
        facets={"areas": AREAS, "contexts": CONTEXTS_CLINICAL},
    )
    entity(
        "source", SRC_PREPRINT,
        "Ye et al. 2025, Predicting functional constraints across evolutionary timescales with "
        "phylogeny-informed genomic language models (bioRxiv v1)",
        "Preprint version of the GPN-Star paper, under its earlier title, retrieved as PDF.",
        [],
        {
            "url": "https://www.biorxiv.org/content/10.1101/2025.09.21.677619v1",
            "artifact_url": URL_PREPRINT,
            "doi": "10.1101/2025.09.21.677619",
            "version": "bioRxiv v1, posted 2025-09-21; the only version the bioRxiv API lists "
                       "(details endpoint, 2026-11-16), with published 'NA'",
            "retrieved_at": "2026-11-16T00:05:27Z",
            "artifact_sha256": SHA_PREPRINT,
            "publication_status": "preprint",
            "licence": "CC BY-NC-ND 4.0",
            "media_type": "application/pdf",
            "venue": "bioRxiv",
            "year": 2025,
            "source_locator": "Methods 'Evaluation Benchmarks' (PDF page 34); Supplementary "
                              "Tables 1-10 (PDF pages 42-48)",
            "limitations": [
                "No value in this batch is taken from the preprint; it is pinned only to record "
                "the version the discovery lead named and the differences from the version of "
                "record.",
                "The preprint has no equivalent of the version of record's Supplementary Table 3 "
                "(ablation studies), the one table of printed performance values.",
                "The preprint's Methods say the ClinVar metric is AUROC; the version of record "
                "says AUPRC, consistent with its own figure captions.",
                "The preprint's Fig. 2 caption says 66 and 84 UK Biobank traits where its "
                "Results say 65 and 83; the version of record says 65 and 83 throughout.",
            ],
            "review": review([SRC_PREPRINT], "Retrieved and hashed 2026-11-16. bioRxiv rewrites "
                                             "per-download stamps, so a re-download may not "
                                             "reproduce the hash.",
                             ["source-hash-verification"]),
        },
        links=[{"relation": "companion_of", "target_id": SRC_ARTICLE}],
        facets={"areas": AREAS, "contexts": CONTEXTS_CLINICAL},
    )
    entity(
        "source", SRC_HF,
        "songlab/gpn-star Hugging Face collection (API response)",
        "The authors' Hugging Face collection of GPN-Star models, training alignments, benchmark "
        "datasets and precomputed scores, retrieved as the collection API JSON.",
        [],
        {
            "url": "https://huggingface.co/collections/songlab/gpn-star-68c0c055acc2ee51d5c4f129",
            "artifact_url": URL_HF,
            "version": "Collection as served 2026-11-16; the collection is mutable and carries "
                       "no revision",
            "retrieved_at": "2026-11-16T00:15:43Z",
            "artifact_sha256": SHA_HF,
            "publication_status": "official_project_source",
            "media_type": "application/json",
            "hash_scope": "SHA-256 of one retrieval of the collection API JSON. The collection is "
                          "a mutable web resource; the hash describes that retrieval only.",
            "source_locator": "items[] of the collection API response",
            "licence": "Not stated in the collection response",
            "review": review([SRC_HF], "Retrieved and hashed 2026-11-16.",
                             ["source-hash-verification"]),
        },
        links=[{"relation": "companion_of", "target_id": SRC_ARTICLE}],
    )


# --------------------------------------------------------------------------------------
# benchmark, datasets, protocols
# --------------------------------------------------------------------------------------

BENCHMARK = f"{P}-benchmark-gpn-star-vep"

DATASETS = {
    "clinvar": dict(
        rid=f"{P}-data-clinvar-pathogenic-vs-benign-missense",
        name="ClinVar pathogenic vs benign missense variants (GPN-Star paper)",
        description="ClinVar missense variants labelled Pathogenic as positives and missense "
                    "variants labelled Benign as negatives.",
        version="ClinVar release 20220924",
        population="ClinVar 'Pathogenic' versus 'Benign' missense variants",
        locator="Supplementary Information, Evaluation Benchmarks, Homo sapiens, Datasets, "
                "bullet 'ClinVar' (PDF page 11)",
    ),
    "proteingym": dict(
        rid=f"{P}-data-proteingym-human-31-genomic",
        name="ProteinGym v0.1 human deep mutational scanning assays in genomic coordinates "
             "(GPN-Star paper)",
        description="The 31 human protein deep mutational scanning datasets of ProteinGym v0.1 "
                    "mapped to genomic coordinates, keeping amino acid substitutions reachable by "
                    "a single nucleotide change and taking the most deleterious such change by "
                    "CADD.",
        version="ProteinGym v0.1, 31 human proteins, processed as in the GPN-MSA paper",
        population="31 human deep mutational scanning assays",
        locator="Supplementary Information, Evaluation Benchmarks, Homo sapiens, Datasets, "
                "bullet 'ProteinGym' (PDF page 11)",
    ),
    "finemapped-coding": dict(
        rid=f"{P}-data-finemapped-coding-matched-maf",
        name="UK Biobank fine-mapped coding variants, MAF-matched controls (GPN-Star paper)",
        description="Missense variants fine-mapped in UK Biobank GWAS with high posterior "
                    "inclusion probability as positives and low-probability variants matched on "
                    "minor allele frequency as controls.",
        version="UK Biobank fine-mapping of 65 traits; controls matched on minor allele "
                "frequency only, similar to GeneticsGym",
        population="Coding variants with PIP > 0.9 versus PIP < 0.01 across 65 UK Biobank traits",
        locator="Supplementary Information, Evaluation Benchmarks, Homo sapiens, Datasets, "
                "bullet 'GWAS fine-mapping' (PDF pages 11-12); Fig. 2c caption",
    ),
    "hgmd": dict(
        rid=f"{P}-data-hgmd-pathogenic-vs-gnomad-common-regulatory",
        name="HGMD pathogenic vs gnomAD common regulatory variants, nine matched controls "
             "(GPN-Star paper)",
        description="Curated HGMD pathogenic regulatory variants as positives, each with nine "
                    "gnomAD common control variants matched on chromosome, molecular consequence "
                    "and distance to the transcription start site.",
        version="HGMD curated data from the cited source, processed as the TraitGym Mendelian "
                "traits dataset; Ensembl VEP release 107 consequences",
        population="HGMD pathogenic versus gnomAD common regulatory variants, nine controls per "
                   "positive",
        locator="Supplementary Information, Evaluation Benchmarks, Homo sapiens, Datasets, "
                "bullet 'HGMD' (PDF page 11)",
    ),
    "gnomad": dict(
        rid=f"{P}-data-gnomad-rare-vs-common-balanced",
        name="gnomAD rare versus common variants, consequence-balanced (GPN-Star paper)",
        description="gnomAD singletons as rare variants and variants with minor allele frequency "
                    "above 5% as common variants, with the rare variants in each molecular "
                    "consequence category subsampled to the number of common variants.",
        version="gnomAD v3.1.2 allele frequencies; Ensembl VEP release 107 consequences",
        population="5.5 million rare versus 5.6 million common variants genome-wide (Fig. 4b "
                   "panel heading)",
        locator="Supplementary Information, Evaluation Benchmarks, Homo sapiens, Datasets, "
                "bullet 'gnomAD' (PDF page 12); Fig. 4b panel heading",
        denominator=None,
    ),
    "ukb-wes": dict(
        rid=f"{P}-data-ukb-wes-34-quantitative-traits",
        name="UK Biobank whole-exome sequencing, 34 quantitative traits (GPN-Star paper)",
        description="UK Biobank whole-exome sequencing data for 161,822 unrelated individuals of "
                    "European ancestry and 34 quantitative traits, keeping variants with minor "
                    "allele frequency below 0.1%.",
        version="UK Biobank WES as used by the published DeepRVAT benchmark; 34 quantitative "
                "traits; MAF < 0.1%",
        population="161,822 unrelated individuals of European ancestry",
        locator="Results, rare variant association testing paragraph (PDF page 5); Fig. 2j "
                "caption",
    ),
}

# protocol slug -> definition
PROTOCOLS = {
    "clinvar-auprc": dict(
        name="ClinVar pathogenic vs benign missense, AUPRC (GPN-Star Supplementary Table 3)",
        description="Area under the precision-recall curve of zero-shot variant scores "
                    "separating ClinVar pathogenic from ClinVar benign missense variants.",
        metric="auprc", direction="higher", unit="unitless",
        data=DATASETS["clinvar"]["rid"],
        locator="Supplementary Information, Evaluation Benchmarks bullet 'ClinVar' (PDF page 11); "
                "Supplementary Table 3 column 'ClinVar' (PDF page 23)",
    ),
    "cosmic-auprc": dict(
        name="COSMIC frequent vs gnomAD common missense, AUPRC (GPN-Star Supplementary Table 3)",
        description="Area under the precision-recall curve of zero-shot variant scores separating "
                    "frequent COSMIC somatic missense mutations from gnomAD common missense "
                    "variants.",
        metric="auprc", direction="higher", unit="unitless",
        data=DATA_COSMIC,
        locator="Supplementary Information, Evaluation Benchmarks bullet 'COSMIC' (PDF page 11); "
                "Supplementary Table 3 column 'COSMIC' (PDF page 23)",
    ),
    "proteingym-spearman": dict(
        name="ProteinGym human deep mutational scanning, mean Spearman (GPN-Star Supplementary "
             "Table 3)",
        description="Mean Spearman rank correlation between zero-shot variant scores and deep "
                    "mutational scanning fitness scores across the 31 human ProteinGym assays.",
        metric="spearman-correlation", direction="higher", unit="unitless",
        data=DATASETS["proteingym"]["rid"],
        locator="Fig. 1c caption ('For ProteinGym, the metric was the mean Spearman's rho across "
                "assays', PDF page 3); Supplementary Table 3 column 'ProteinGym' (PDF page 23)",
    ),
    "finemapped-coding-auprc": dict(
        name="UK Biobank fine-mapped coding variants, AUPRC (GPN-Star Supplementary Table 3)",
        description="Area under the precision-recall curve of zero-shot variant scores separating "
                    "fine-mapped putatively causal coding variants from non-causal ones.",
        metric="auprc", direction="higher", unit="unitless",
        data=DATASETS["finemapped-coding"]["rid"],
        locator="Supplementary Information, Evaluation Benchmarks bullet 'GWAS fine-mapping' "
                "(PDF pages 11-12); Supplementary Table 3 column 'Finemapped coding' "
                "(PDF page 23)",
    ),
    "omim-auprc": dict(
        name="OMIM pathogenic vs gnomAD common regulatory variants, AUPRC (GPN-Star "
             "Supplementary Table 3)",
        description="Area under the precision-recall curve of zero-shot variant scores separating "
                    "OMIM pathogenic regulatory variants from their nine matched gnomAD common "
                    "controls.",
        metric="auprc", direction="higher", unit="unitless",
        data=DATA_OMIM,
        locator="Supplementary Information, Evaluation Benchmarks bullet 'OMIM' (PDF page 11); "
                "Supplementary Table 3 column 'OMIM' (PDF page 23)",
    ),
    "finemapped-noncoding-auprc": dict(
        name="UK Biobank fine-mapped non-coding variants, AUPRC (GPN-Star Supplementary Table 3)",
        description="Area under the precision-recall curve of zero-shot variant scores separating "
                    "fine-mapped putatively causal non-coding variants from their nine matched "
                    "controls.",
        metric="auprc", direction="higher", unit="unitless",
        data=DATA_COMPLEX,
        locator="Supplementary Information, Evaluation Benchmarks bullet 'GWAS fine-mapping' "
                "(PDF pages 11-12); Supplementary Table 3 column 'Finemapped non-coding' "
                "(PDF page 23)",
    ),
    "hgmd-auprc": dict(
        name="HGMD pathogenic vs gnomAD common regulatory variants, AUPRC (GPN-Star "
             "Supplementary Table 3)",
        description="Area under the precision-recall curve of zero-shot variant scores separating "
                    "HGMD pathogenic regulatory variants from their nine matched gnomAD common "
                    "controls.",
        metric="auprc", direction="higher", unit="unitless",
        data=DATASETS["hgmd"]["rid"],
        locator="Supplementary Information, Evaluation Benchmarks bullet 'HGMD' (PDF page 11); "
                "Supplementary Table 3 column 'HGMD' (PDF page 23)",
    ),
}

ABLATION_PROTOCOL_NOTE = (
    "All compared models in Supplementary Table 3 were trained on the same dataset "
    "(multiz100way with training interval curation) and with the same hyperparameters: 25 "
    "million parameters, learning rate 1e-4, batch size 512 and 150k steps. Each setting was "
    "trained with three random initializations; the table prints the mean outside the "
    "parentheses and the maximum inside them. For every benchmark in the paper, only variants "
    "for which all compared models have predictions are scored."
)

GNOMAD_PROTOCOL = f"{P}-protocol-gnomad-rare-vs-common-odds-ratio"
RVAT_PROTOCOLS = {
    "discovered": dict(
        rid=f"{P}-protocol-rvat-significant-genes",
        name="DeepRVAT rare variant association testing, significant genes (GPN-Star Fig. 2j)",
        description="Number of gene-trait associations discovered at a family-wise error rate "
                    "below 0.05 by DeepRVAT rare variant association testing over 34 UK Biobank "
                    "quantitative traits.",
        metric="count", unit="count",
    ),
    "replicated": dict(
        rid=f"{P}-protocol-rvat-replicated-genes",
        name="DeepRVAT rare variant association testing, replicated genes (GPN-Star Fig. 2j)",
        description="Number of discovered gene-phenotype associations that replicate findings of "
                    "conventional UK Biobank rare variant association studies with larger sample "
                    "sizes.",
        metric="count", unit="count",
    ),
}


def build_assessments() -> None:
    entity(
        "benchmark", BENCHMARK,
        "GPN-Star variant effect prediction benchmarks (Ye et al. 2026)",
        "The authors' variant effect benchmarks for GPN-Star: ClinVar, COSMIC and ProteinGym "
        "missense tasks, OMIM, HGMD and fine-mapped UK Biobank coding and non-coding variant "
        "tasks, gnomAD rare versus common enrichment, complex trait heritability and rare "
        "variant association testing.",
        [SRC_ARTICLE, SRC_SI],
        {
            "entity_level": "suite",
            "version": "Nature version of record (2026-09-09)",
            "task": "Genome-wide variant effect (functional constraint) prediction",
            "scope_note": "Supplementary Table 3 (ablation studies), the printed value labels "
                          "of Fig. 4b and the rare variant association gene counts in the Results "
                          "are extracted. Fig. 5a also prints value labels, for five non-human "
                          "species, and is not extracted. Figs. 2 and 3, Fig. 4a,c,d, Fig. 5b-d, "
                          "Extended Data Figs. 1-10 and Supplementary Figs. 1-27 are plots "
                          "without printed values and were not read.",
            "source_locator": "Supplementary Information, Evaluation Benchmarks (PDF pages "
                              "11-14); Figs. 2-5; Results",
            "limitations": [
                "Built and run by the GPN-Star authors (author-reported).",
                "The headline model comparisons (Figs. 2 and 3) print no values, so the only "
                "stored cross-model comparison from this paper is Fig. 4b.",
            ],
            "review": review([SRC_SI], TRANSCRIBE_NOTE, ["transcription"]),
        },
        facets={"areas": AREAS, "contexts": CONTEXTS_CLINICAL},
    )

    for key, spec in DATASETS.items():
        attrs = {
            "version": spec["version"],
            "split": "Whole labelled set; scores are zero-shot, with no training on these labels"
                     if key != "ukb-wes" else
                     "DeepRVAT training and association testing on the same cohort, following the "
                     "published DeepRVAT procedure",
            "population": spec["population"],
            "source_locator": spec["locator"],
            "missing_metadata": {
                "denominator": {
                    "reason": "unreported",
                    "note": "Variant counts are not printed for this dataset",
                },
            },
            "review": review([SRC_SI if key != "ukb-wes" else SRC_ARTICLE], TRANSCRIBE_NOTE,
                             ["transcription"]),
        }
        if key == "gnomad":
            attrs["missing_metadata"]["denominator"]["note"] = (
                "Fig. 4b prints the class sizes as rounded millions (n = 5.5M versus 5.6M), not "
                "as exact counts"
            )
        entity("dataset", spec["rid"], spec["name"], spec["description"],
               [SRC_SI, SRC_ARTICLE] if key in ("gnomad", "ukb-wes") else [SRC_SI], attrs,
               facets={"areas": AREAS,
                       "contexts": CONTEXTS_CLINICAL if key in CLINICAL_DATASETS else CONTEXTS})

    for slug, spec in PROTOCOLS.items():
        entity(
            "protocol", f"{P}-protocol-ablation-{slug}", spec["name"], spec["description"],
            [SRC_SI],
            {
                "procedure": ABLATION_PROTOCOL_NOTE,
                "version": "Nature version of record, Supplementary Table 3",
                "metric": spec["metric"],
                "metric_direction": spec["direction"],
                "unit": spec["unit"],
                "replicates": "Three random initializations per setting; mean and maximum printed",
                "limitations": [
                    "Author-reported: the ablation models were trained and scored by the authors.",
                    "The ablation models are 25-million-parameter models trained on the "
                    "vertebrate alignment; they are not the released checkpoints used in the "
                    "paper's headline figures.",
                    "Scored variant counts are not printed.",
                ],
                "source_locator": spec["locator"],
                "review": review([SRC_SI], PARSE_NOTE, ["pdf-text-parse"]),
            },
            links=[
                {"relation": "part_of", "target_id": BENCHMARK},
                {"relation": "uses_data", "target_id": spec["data"]},
            ],
            facets={"areas": AREAS,
                    "contexts": CONTEXTS_CLINICAL if slug in CLINICAL_PROTOCOLS else CONTEXTS},
        )

    entity(
        "protocol", GNOMAD_PROTOCOL,
        "gnomAD rare versus common enrichment in the deleterious tail, odds ratio (GPN-Star "
        "Fig. 4b)",
        "Odds ratio for the enrichment of gnomAD singletons over common variants in the most "
        "deleterious tail of each score, with the tail threshold set so that each score yields 30 "
        "false discoveries.",
        [SRC_ARTICLE, SRC_SI],
        {
            "procedure": "Each score is applied to gnomAD v3.1.2 variants; rare variants are "
                         "singletons and common variants have minor allele frequency above 5%. "
                         "The deleterious tail threshold is chosen so that each score yields 30 "
                         "false discoveries, and the rare variants in each molecular consequence "
                         "category are subsampled to the number of common variants. The panel "
                         "reports the genome-wide enrichment.",
            "version": "Nature version of record, Fig. 4b",
            "metric": "odds-ratio",
            "metric_direction": "higher",
            "unit": "unitless",
            "limitations": [
                "Author-reported.",
                "The values are the printed labels of a bar chart; no uncertainty is printed for "
                "them.",
                "The figure does not name the GPN-Star checkpoints behind GPN-Star (V), (M) and "
                "(P), nor state whether the scores are the mutation-rate-calibrated ones.",
            ],
            "source_locator": "Fig. 4b and its caption (PDF page 7); Supplementary Information, "
                              "Evaluation Benchmarks bullet 'gnomAD' (PDF page 12)",
            "review": review([SRC_ARTICLE], PARSE_NOTE, ["pdf-text-parse"]),
        },
        links=[
            {"relation": "part_of", "target_id": BENCHMARK},
            {"relation": "uses_data", "target_id": DATASETS["gnomad"]["rid"]},
        ],
    )

    for spec in RVAT_PROTOCOLS.values():
        entity(
            "protocol", spec["rid"], spec["name"], spec["description"],
            [SRC_ARTICLE],
            {
                "procedure": "Rare variant association testing with DeepRVAT on 34 UK Biobank "
                             "quantitative traits, following the published DeepRVAT benchmarking "
                             "procedure, on whole-exome sequencing data from 161,822 unrelated "
                             "individuals of European ancestry, keeping variants with minor "
                             "allele frequency below 0.1%. The procedure was run three times "
                             "with different random seeds and the paper reports averages across "
                             "runs.",
                "version": "Nature version of record, Fig. 2j and Results",
                "metric": spec["metric"],
                "metric_direction": "higher",
                "unit": spec["unit"],
                "unit_detail": "Genes (gene-trait associations)",
                "replicates": "Three runs with different random seeds; averages reported",
                "limitations": [
                    "Author-reported.",
                    "The counts are printed in the Results text; Fig. 2j itself prints no values.",
                    "The paper states 'on average across runs' for the comparison and does not "
                    "separately say whether the original DeepRVAT counts are also means over "
                    "three runs.",
                ],
                "source_locator": "Results, rare variant association testing paragraph "
                                  "(PDF page 5); Fig. 2j caption",
                "review": review([SRC_ARTICLE], PARSE_NOTE, ["pdf-text-parse"]),
            },
            links=[
                {"relation": "part_of", "target_id": BENCHMARK},
                {"relation": "uses_data", "target_id": DATASETS["ukb-wes"]["rid"]},
            ],
        )


# --------------------------------------------------------------------------------------
# configurations
# --------------------------------------------------------------------------------------

ACCESS_COLLECTION = (
    "Pretrained models, training datasets and benchmark datasets are released on the Hugging "
    "Face collection songlab/gpn-star-68c0c055acc2ee51d5c4f129 (Data availability); the paper "
    "does not map checkpoint names to repository ids."
)

ABLATION_DESCRIPTIONS = {
    "gpn-star-default": "GPN-Star in the reference setting of the architecture ablation: 25 "
                        "million parameters trained on the curated multiz100way vertebrate "
                        "alignment with the species tree, clade pooling and 20 target species.",
    "one-target-species-human": "GPN-Star trained with the human genome as its only target "
                                "species instead of 20 target species sampled across clades.",
    "no-evol-distance-encoding": "GPN-Star with the evolutionary distance encoding removed from "
                                 "the phylogeny-informed cross-attention.",
    "no-pooling-into-clades": "GPN-Star without attention pooling of source species into clade "
                              "embeddings.",
    "no-species-tree": "GPN-Star with the species tree removed, so it uses neither evolutionary "
                       "distances nor clade pooling.",
    "msa-transformer-like": "An MSA Transformer style alignment model that uses no species tree "
                            "and no target or source distinction, applying row-wise then "
                            "column-wise self-attention over the full alignment in each encoder "
                            "block.",
    "gpn-msa-exclude-10-closest-species": "The GPN-MSA architecture trained on the same "
                                          "alignment with the ten closest species excluded.",
    "gpn-msa-no-species-curation": "The GPN-MSA architecture trained on the same alignment "
                                   "without species curation.",
}

FIG4B_DESCRIPTIONS = {
    "gpn-star-v": ("GPN-Star (V)", MODEL_GPN_STAR,
                   "GPN-Star at the vertebrate timescale, scoring human variants from a "
                   "whole-genome alignment of 100 vertebrates."),
    "gpn-star-m": ("GPN-Star (M)", MODEL_GPN_STAR,
                   "GPN-Star at the mammal timescale, scoring human variants from a whole-genome "
                   "alignment of 447 mammals."),
    "gpn-star-p": ("GPN-Star (P)", MODEL_GPN_STAR,
                   "GPN-Star at the primate timescale, scoring human variants from a whole-genome "
                   "alignment of 243 primates."),
    "gpn-msa": ("GPN-MSA", MODEL_GPN_MSA,
                "GPN-MSA log-likelihood ratios taken from the authors' precomputed hg38 score "
                "set on Hugging Face."),
    "phylop-v": ("PhyloP (V)", METHOD_PHYLOP,
                 "phyloP conservation scores from the 100-vertebrate hg38 alignment, downloaded "
                 "as the UCSC phyloP100way track."),
    "phylop-m": ("PhyloP (M)", METHOD_PHYLOP,
                 "phyloP conservation scores from the 447-mammal hg38 alignment, downloaded as "
                 "the UCSC phyloP447way track."),
    "phylop-p": ("PhyloP (P)", METHOD_PHYLOP,
                 "phyloP conservation scores for 243 primates, downloaded as the UCSC "
                 "phyloP447wayPrimates track."),
    "phastcons-v": ("PhastCons (V)", METHOD_PHASTCONS,
                    "phastCons conservation scores from the 100-vertebrate hg38 alignment, "
                    "downloaded as the UCSC phastCons100way track."),
    "phastcons-m": ("PhastCons (M)", METHOD_PHASTCONS,
                    "phastCons conservation scores from the 470-mammal hg38 alignment, "
                    "downloaded as the UCSC phastCons470way track."),
    "phastcons-p": ("PhastCons (P)", METHOD_PHASTCONS,
                    "Primate conservation scores for 43 primates, downloaded from the Zoonomia "
                    "cactus track hub."),
    "cadd": ("CADD", METHOD_CADD,
             "CADD v1.7 precomputed raw scores."),
    "roulette": ("Roulette mutation rate", f"{P}-method-roulette",
                 "Roulette precomputed genome-wide mutation rate estimates."),
}

FIG4B_SOURCE_DETAIL = {
    "gpn-msa": "Precomputed log-likelihood ratios from "
               "https://huggingface.co/datasets/songlab/gpn-msa-hg38-scores",
    "phylop-v": "https://hgdownload.soe.ucsc.edu/goldenPath/hg38/phyloP100way/"
                "hg38.phyloP100way.bw",
    "phylop-m": "https://hgdownload.soe.ucsc.edu/goldenPath/hg38/phyloP447way/"
                "hg38.phyloP447way.bw",
    "phylop-p": "https://hgdownload.soe.ucsc.edu/goldenPath/hg38/phyloP447way/"
                "hg38.phyloP447wayPrimates.bw",
    "phastcons-v": "https://hgdownload.soe.ucsc.edu/goldenPath/hg38/phastCons100way/"
                   "hg38.phastCons100way.bw",
    "phastcons-m": "https://hgdownload.soe.ucsc.edu/goldenPath/hg38/phastCons470way/"
                   "hg38.phastCons470way.bw",
    "phastcons-p": "https://cgl.gi.ucsc.edu/data/cactus/zoonomia-2021-track-hub/hg38/"
                   "phyloPPrimates.bigWig",
    "cadd": "CADD v1.7 raw scores from https://cadd.gs.washington.edu",
    "roulette": "https://github.com/vseplyarskiy/Roulette",
}


def build_configurations() -> None:
    # released and unreleased training setups, Supplementary Table 1
    for name, group, size, lr, steps, time in CHECKPOINTS:
        fields = GROUPS[group]
        timescale = fields["timescale"]
        description = (
            f"GPN-Star trained for {fields['organism']} on the {fields['wga']} whole-genome "
            f"alignment of {fields['species']} with {size.replace(' ', '')} parameters and a "
            f"{fields['context']} context."
        )
        entity(
            "configuration", f"{P}-config-ckpt-{name.lower()}",
            f"GPN-Star {name}", description,
            [SRC_SI],
            {
                "reported_name": name,
                "version": name,
                "parameters": size,
                "hyperparameters": f"learning rate {lr}; {steps} training steps; context size "
                                   f"{fields['context']}; clade distance threshold "
                                   f"phi_clade = {fields['phi_clade']}; {fields['clades']} clades",
                "training_setting": (
                    f"Genome assembly {fields['assembly']} ({fields['assembly_size']}); training "
                    f"chromosomes {fields['train_chr']}; validation chromosome {fields['val_chr']}; "
                    f"held-out test chromosome {fields['test_chr']}; whole-genome alignment "
                    f"{fields['wga']} of {fields['species']}"
                ),
                "runtime": f"{time} on 8 NVIDIA A100 GPUs",
                "access_reuse": ACCESS_COLLECTION,
                "foundation_model_eligible": True,
                "model_identity_note": (
                    "Training setup named in Supplementary Table 1. The three human 200 "
                    "million-parameter models are the ones the paper calls GPN-Star (V), (M) and "
                    "(P)." if size == "200 M" and timescale else
                    "Training setup named in Supplementary Table 1."
                ),
                "source_locator": f"Supplementary Information, Supplementary Table 1, row "
                                  f"'{name}' (PDF page 21)",
                "review": review([SRC_SI], TRANSCRIBE_NOTE, ["transcription"]),
            },
            links=[{"relation": "configuration_of", "target_id": MODEL_GPN_STAR}],
            facets={"areas": AREAS, "contexts": CONTEXTS, "method_types": ["foundation_model"]},
        )

    # ablation settings, Supplementary Table 3
    for slug, label in ABLATION_ROWS:
        target = MODEL_GPN_MSA if slug.startswith("gpn-msa") else MODEL_GPN_STAR
        attrs = {
            "reported_name": label,
            "version": "Ablation model trained by the authors for Supplementary Table 3; not a "
                       "released checkpoint",
            "parameters": "25 M",
            "hyperparameters": "learning rate 1e-4; batch size 512; 150k training steps",
            "training_setting": "multiz100way vertebrate alignment with training interval "
                                "curation; same dataset and hyperparameters for every row of "
                                "Supplementary Table 3",
            "access_reuse": "Ablation models are not among the checkpoints released on the "
                            "authors' Hugging Face collection.",
            "foundation_model_eligible": True,
            "source_locator": f"Supplementary Information, Supplementary Table 3, row "
                              f"'{label}' (PDF page 23)",
            "review": review([SRC_SI], PARSE_NOTE, ["pdf-text-parse"]),
        }
        if slug.startswith("gpn-msa"):
            attrs["model_identity_note"] = (
                "The GPN-MSA architecture retrained by the GPN-Star authors on their own dataset "
                "and hyperparameters for this ablation; it is not the released GPN-MSA "
                "checkpoint, and it is not one of the ablations in the GPN-MSA paper."
            )
            attrs["model_identity_note"] += (
                " The paper describes the setting itself only by its Supplementary Table 3 row "
                "label."
            )
        if slug == "msa-transformer-like":
            attrs["model_identity_note"] = (
                "An architecture ablation trained in the GPN-Star framework, not the published "
                "MSA Transformer."
            )
        entity(
            "configuration", f"{P}-config-ablation-{slug}",
            f"GPN-Star ablation '{label}' (Supplementary Table 3)" if not slug.startswith("gpn-msa")
            else f"GPN-Star ablation '{label}' (Supplementary Table 3)",
            ABLATION_DESCRIPTIONS[slug],
            [SRC_SI], attrs,
            links=[{"relation": "configuration_of", "target_id": target}],
            facets={"areas": AREAS, "contexts": CONTEXTS, "method_types": ["foundation_model"]},
        )

    # Fig. 4b systems
    entity(
        "method", f"{P}-method-roulette",
        "Roulette",
        "Roulette estimates the local mutation rate of each possible single nucleotide variant in "
        "the human genome from sequence context and local covariates.",
        [SRC_SI],
        {
            "reported_name": "Roulette mutation rate",
            "source_locator": "Supplementary Information, Evaluation Benchmarks, Compared models, "
                              "bullet 'Roulette' (PDF page 13)",
            "missing_metadata": {
                "version": {
                    "reason": "unreported",
                    "note": "The paper cites the Roulette repository without naming a version",
                },
            },
            "review": review([SRC_SI], TRANSCRIBE_NOTE, ["transcription"]),
        },
        facets={"areas": AREAS, "contexts": ["research"], "method_types": ["conventional_pipeline"]},
    )
    for slug, (label, target, description) in FIG4B_DESCRIPTIONS.items():
        attrs = {
            "reported_name": label,
            "access_reuse": FIG4B_SOURCE_DETAIL.get(slug, ACCESS_COLLECTION),
            "source_locator": f"Fig. 4b, row '{label}' (PDF page 7); Supplementary Information, "
                              f"Evaluation Benchmarks, Compared models (PDF pages 12-14)",
            "review": review([SRC_ARTICLE], PARSE_NOTE, ["pdf-text-parse"]),
        }
        if slug.startswith("gpn-star"):
            attrs["version"] = (
                "Timescale model as scored in the paper's main figures; the paper says it focuses "
                "on the largest (200 million-parameter) models but Fig. 4b does not name a "
                "checkpoint"
            )
            attrs["foundation_model_eligible"] = True
            attrs["model_identity_note"] = (
                "Kept separate from the Supplementary Table 1 training setups because the figure "
                "does not name the checkpoint."
            )
            attrs["provenance_note"] = (
                "Identity as the figure labels it. Fig. 4b names the model only as GPN-Star (V), "
                "(M) or (P); the paper says it focuses on the 200 million-parameter models but "
                "the figure does not name a checkpoint, so no checkpoint is assigned."
            )
            attrs["missing_metadata"] = {
                "checkpoint": {
                    "reason": "unreported",
                    "note": "Fig. 4b names the model only as GPN-Star (V), (M) or (P)",
                },
            }
            types = ["foundation_model"]
        elif slug == "gpn-msa":
            attrs["version"] = "Precomputed hg38 log-likelihood ratios released by the GPN-MSA " \
                               "authors"
            attrs["foundation_model_eligible"] = True
            types = ["foundation_model"]
        elif slug == "cadd":
            attrs["version"] = "CADD v1.7, raw scores"
            types = ["supervised_machine_learning"]
        elif slug == "roulette":
            attrs["version"] = "Precomputed genome-wide mutation rate estimates from the Roulette " \
                               "repository"
            types = ["conventional_pipeline"]
        else:
            attrs["version"] = FIG4B_SOURCE_DETAIL[slug].rsplit("/", 1)[-1]
            types = ["conventional_pipeline"]
        entity(
            "configuration", f"{P}-config-fig4b-{slug}",
            f"{label} (GPN-Star Fig. 4b)", description,
            [SRC_ARTICLE, SRC_SI], attrs,
            links=[{"relation": "configuration_of", "target_id": target}],
            facets={"areas": AREAS, "contexts": CONTEXTS, "method_types": types},
        )

    # RVAT systems
    entity(
        "method", f"{P}-method-deeprvat",
        "DeepRVAT",
        "DeepRVAT aggregates rare variants within a gene with a deep set network over variant "
        "annotations to test the gene for association with a trait.",
        [SRC_ARTICLE],
        {
            "reported_name": "DeepRVAT",
            "version": "DeepRVAT 1.1",
            "source_locator": "Results, rare variant association testing paragraph (PDF page 5); "
                              "Reporting Summary, Data analysis (PDF page 23)",
            "review": review([SRC_ARTICLE], TRANSCRIBE_NOTE, ["transcription"]),
        },
        facets={"areas": AREAS, "contexts": CONTEXTS,
                "method_types": ["supervised_machine_learning"]},
    )
    entity(
        "method", f"{P}-method-deeprvat-plus-gpn-star",
        "DeepRVAT with GPN-Star annotations",
        "DeepRVAT rare variant association testing with the three GPN-Star timescale predictions "
        "added to its variant annotations during training and association testing.",
        [SRC_ARTICLE],
        {
            "reported_name": "DeepRVAT + GPN-Star (V, M, P)",
            "version": "DeepRVAT 1.1 with the three GPN-Star predictions added as annotations",
            "source_locator": "Results, rare variant association testing paragraph (PDF page 5); "
                              "Fig. 2j caption",
            "missing_metadata": {
                "checkpoint_revision": {
                    "reason": "unreported",
                    "note": "The paper does not name which GPN-Star checkpoints produced the "
                            "annotations",
                },
            },
            "review": review([SRC_ARTICLE], TRANSCRIBE_NOTE, ["transcription"]),
        },
        links=[{"relation": "uses_model", "target_id": MODEL_GPN_STAR}],
        facets={"areas": AREAS, "contexts": CONTEXTS,
                "method_types": ["supervised_machine_learning"]},
    )


# --------------------------------------------------------------------------------------
# evaluations and results
# --------------------------------------------------------------------------------------

def evaluation(rid: str, name: str, system: str, assessment: str, data: str, sources: list[str],
               comparison: dict, locator: str, missing: dict, limitations: list[str]) -> None:
    entity(
        "evaluation", rid, name,
        "Published comparison transcribed from the pinned source; not reproduced.",
        sources,
        {
            "origin": "author_reported",
            "protocol": assessment,
            "version": "Nature version of record (2026-09-09)",
            "comparison": comparison,
            "source_locator": locator,
            "limitations": limitations,
            "missing_metadata": missing,
            "review": review([sources[0]], PARSE_NOTE, ["pdf-text-parse"]),
        },
        links=[
            {"relation": "system", "target_id": system},
            {"relation": "assessment", "target_id": assessment},
            {"relation": "data", "target_id": data},
        ],
        facets={"areas": AREAS, "contexts": CONTEXTS},
    )


def result(rid: str, name: str, eval_id: str, printed: str, numeric: str, metric: str,
           unit: str, qualifier: str, locator: str, sources: list[str], extra: dict | None = None,
           note: str = PARSE_NOTE, method: list[str] | None = None) -> None:
    attrs = {
        "printed_value": printed,
        "numeric_value": numeric,
        "metric": metric,
        "metric_direction": "higher",
        "unit": unit,
        "metric_qualifier": qualifier,
        "source_locator": locator,
        "review": review([sources[0]], note, method or ["pdf-text-parse"]),
    }
    if extra:
        attrs.update(extra)
    entity("result", rid, name,
           "Reported measurement transcribed from the pinned source. Not independently reproduced.",
           sources, attrs,
           links=[{"relation": "evaluation", "target_id": eval_id}],
           facets={})


ABLATION_MISSING = {
    "comparison.budget": {"reason": "unreported"},
    "comparison.dataset_version": {
        "reason": "unreported",
        "note": "Dataset releases are named in the Supplementary Information but the scored "
                "variant set and its size are not",
    },
    "comparison.metric_implementation": {"reason": "unreported"},
    "comparison.population": {
        "reason": "unreported",
        "note": "Only variants predicted by every compared model are scored; the resulting "
                "counts are not printed",
    },
}


def build_ablation(table: dict[str, dict[str, tuple[str, str, str]]]) -> None:
    for slug, label in ABLATION_ROWS:
        config = f"{P}-config-ablation-{slug}"
        for key, header, proto_slug in ABLATION_COLUMNS:
            mean, maximum, cell = table[slug][key]
            protocol = f"{P}-protocol-ablation-{proto_slug}"
            spec = PROTOCOLS[proto_slug]
            eval_id = f"{P}-eval-ablation-{slug}-{key}"
            evaluation(
                eval_id, f"{label} on {header} (GPN-Star Supplementary Table 3)",
                config, protocol, spec["data"], [SRC_SI],
                {
                    "protocol_id": protocol,
                    "dataset_version": None,
                    "split": "Whole labelled set",
                    "population": None,
                    "inputs": "Reference genome and whole-genome alignment window around each "
                              "variant",
                    "adaptation": "zero-shot",
                    "metric_implementation": None,
                    "aggregation": "Mean over three random initializations; the maximum over the "
                                   "same three is printed in parentheses",
                    "budget": None,
                },
                f"Supplementary Table 3, row '{label}', column '{header}' (PDF page 23)",
                ABLATION_MISSING,
                [
                    "Author-reported ablation: models trained and scored by the authors.",
                    "25-million-parameter ablation models, not the released checkpoints.",
                ],
            )
            metric_name = ("mean Spearman" if spec["metric"] == "spearman-correlation"
                           else "AUPRC")
            # One result per printed cell. Emitting the parenthesised maximum as a second result
            # was tried and reverted: `batch.py check-values` matches whole cells, so the maxima
            # came back as 51 not_in_row and 8 overclaimed_in_row, which would bury a real
            # mismatch. The maximum is kept in printed_source_cell and source_statistic.
            result(
                f"{P}-result-ablation-{slug}-{key}",
                f"{label} {header} {metric_name} (mean over three initializations)",
                eval_id, mean, mean, spec["metric"], spec["unit"],
                "mean over three random initializations; zero-shot",
                f"Supplementary Table 3, row '{label}', column '{header}' (PDF page 23)",
                [SRC_SI],
                {
                    "printed_source_cell": cell,
                    "source_statistic": f"The cell prints '{cell}': the mean over three random "
                                        f"initializations outside the parentheses and the "
                                        f"maximum over the same three ({maximum}) inside them.",
                    "missing_metadata": {
                        "uncertainty": {
                            "reason": "unreported",
                            "note": "The table prints a mean and a maximum over three "
                                    "initializations, not a spread",
                        },
                    },
                },
            )


def build_fig4b(values: dict[str, str]) -> None:
    data = DATASETS["gnomad"]["rid"]
    for slug, (label, _, _) in FIG4B_DESCRIPTIONS.items():
        config = f"{P}-config-fig4b-{slug}"
        eval_id = f"{P}-eval-fig4b-{slug}"
        evaluation(
            eval_id, f"{label} on gnomAD rare versus common enrichment (GPN-Star Fig. 4b)",
            config, GNOMAD_PROTOCOL, data, [SRC_ARTICLE, SRC_SI],
            {
                "protocol_id": GNOMAD_PROTOCOL,
                "dataset_version": "gnomAD v3.1.2",
                "split": "Genome-wide; GPN-Star's held-out test chromosome is chromosome 22",
                "population": "5.5 million rare versus 5.6 million common variants",
                "inputs": "Per-variant deleteriousness or constraint score",
                "adaptation": "zero-shot",
                "metric_implementation": None,
                "aggregation": "Genome-wide odds ratio at the threshold giving 30 false "
                               "discoveries",
                "budget": None,
            },
            f"Fig. 4b, row '{label}' (PDF page 7)",
            {
                "comparison.budget": {"reason": "unreported"},
                "comparison.metric_implementation": {"reason": "unreported"},
            },
            [
                "Author-reported.",
                "Value read from a printed bar label; no uncertainty is printed.",
            ],
        )
        result(
            f"{P}-result-fig4b-{slug}", f"{label} gnomAD rare versus common odds ratio",
            eval_id, values[slug], values[slug], "odds-ratio", "unitless",
            "genome-wide enrichment of singletons over common variants in the deleterious tail at "
            "the threshold giving 30 false discoveries",
            f"Fig. 4b, row '{label}', printed bar label (PDF page 7)",
            [SRC_ARTICLE],
            {
                "scope_note": "Panel heading 'n = 5.5M versus 5.6M'; the class sizes are printed "
                              "as rounded millions, so no exact scored count is recorded.",
                "missing_metadata": {
                    "uncertainty": {
                        "reason": "unreported",
                        "note": "No error bar or interval is printed for the panel b labels",
                    },
                },
            },
        )


def build_rvat(values: dict[str, str]) -> None:
    data = DATASETS["ukb-wes"]["rid"]
    systems = {
        "gpn-star": (f"{P}-method-deeprvat-plus-gpn-star", "DeepRVAT with GPN-Star annotations"),
        "original": (f"{P}-method-deeprvat", "DeepRVAT"),
    }
    for endpoint, spec in RVAT_PROTOCOLS.items():
        for who, (system, label) in systems.items():
            key = f"{endpoint}-{who}"
            eval_id = f"{P}-eval-rvat-{endpoint}-{who}"
            evaluation(
                eval_id, f"{label}, {endpoint} genes (GPN-Star Fig. 2j)",
                system, spec["rid"], data, [SRC_ARTICLE],
                {
                    "protocol_id": spec["rid"],
                    "dataset_version": "UK Biobank whole-exome sequencing, 161,822 unrelated "
                                       "individuals of European ancestry",
                    "split": "34 quantitative traits; variants with minor allele frequency below "
                             "0.1%",
                    "population": "161,822 unrelated individuals of European ancestry",
                    "inputs": "Variant annotations aggregated per gene",
                    "adaptation": "trained on the cohort following the published DeepRVAT "
                                  "procedure",
                    "metric_implementation": "Family-wise error rate below 0.05"
                                             if endpoint == "discovered" else
                                             "Replication against conventional UK Biobank rare "
                                             "variant association studies with larger sample sizes",
                    "aggregation": "Average over three runs with different random seeds",
                    "budget": None,
                },
                "Results, rare variant association testing paragraph (PDF page 5)",
                {"comparison.budget": {"reason": "unreported"}},
                [
                    "Author-reported.",
                    "The paper's 'on average across runs' is stated for the comparison; it does "
                    "not separately say whether the original DeepRVAT counts are means over "
                    "three runs.",
                ],
            )
            result(
                f"{P}-result-rvat-{endpoint}-{who}",
                f"{label}, {endpoint} genes",
                eval_id, values[f"{endpoint}-{who}"], values[f"{endpoint}-{who}"],
                "count", "count",
                "mean over three runs with different random seeds; family-wise error rate below "
                "0.05" if endpoint == "discovered" else
                "mean over three runs with different random seeds; replicated in earlier UK "
                "Biobank rare variant studies",
                "Results, rare variant association testing paragraph (PDF page 5)",
                [SRC_ARTICLE],
                {
                    "unit_detail": "Genes (gene-trait associations)",
                    "scope_note": "Printed in the Results text, not in Fig. 2j." if who == "gpn-star"
                                  else "Printed in the Results text, not in Fig. 2j. The paper "
                                       "states 'on average across runs' for the comparison and "
                                       "does not separately say whether the original DeepRVAT "
                                       "count is a mean over the three runs.",
                    "missing_metadata": {
                        "uncertainty": {
                            "reason": "unreported",
                            "note": "Only the average over the three runs is printed",
                        },
                    },
                },
            )


# --------------------------------------------------------------------------------------
# claims
# --------------------------------------------------------------------------------------

def claim(slug: str, field: str, value: str, locator: str, sources: list[str],
          subject: str = MODEL_GPN_STAR, method: list[str] | None = None) -> None:
    entity(
        "claim", f"{P}-claim-{slug}", f"{field}: GPN-Star" if subject == MODEL_GPN_STAR
        else f"{field}: {subject}",
        "Descriptive fact transcribed from the pinned source.",
        sources,
        {
            "field": field,
            "value": value,
            "source_locator": locator,
            "review": review([sources[0]], TRANSCRIBE_NOTE, method or ["transcription"]),
        },
        links=[{"relation": "subject", "target_id": subject}],
        facets={},
    )


def build_claims() -> None:
    claim(
        "software-version", "version",
        "The paper names no model release version. Its code is the gpn package at v0.8 "
        "(github.com/songlab-cal/gpn), archived at doi:10.5281/zenodo.21501177 and available "
        "under the MIT licence. Model checkpoints are named by assembly, alignment and parameter "
        "count (Supplementary Table 1); the three human models are called GPN-Star (V), (M) and "
        "(P) for the vertebrate, mammal and primate timescales.",
        "Reporting Summary, Software and code, 'Data analysis' (PDF page 23); Code availability "
        "(PDF page 10); Results (PDF page 3); Supplementary Information, Supplementary Table 1 "
        "(PDF page 21)",
        [SRC_ARTICLE, SRC_SI],
    )
    claim(
        "access", "access",
        "Pretrained models, training datasets and benchmark datasets are on the Hugging Face "
        "collection songlab/gpn-star-68c0c055acc2ee51d5c4f129. Precomputed GPN-Star predictions "
        "for all possible single nucleotide variants in the human genome and in the five model "
        "organisms are on Hugging Face at doi:10.57967/hf/9849.",
        "Data availability (PDF page 10)",
        [SRC_ARTICLE],
    )
    claim(
        "released-checkpoints", "released_checkpoints",
        "The authors' Hugging Face collection listed eight model repositories on 2026-11-16: "
        "songlab/gpn-star-hg38-v100-200m, songlab/gpn-star-hg38-m447-200m, "
        "songlab/gpn-star-hg38-p243-200m, songlab/gpn-star-mm39-v35-85m, "
        "songlab/gpn-star-galGal6-v77-85m, songlab/gpn-star-dm6-i124-85m, "
        "songlab/gpn-star-ce11-n135-25m and songlab/gpn-star-tair10-b18-25m, alongside the "
        "training alignments, the benchmark datasets and the precomputed score set "
        "songlab/gpn-star-scores. None of the repositories was gated or private. Supplementary "
        "Table 1 describes 19 training setups, so not every trained model is released, and the "
        "paper does not map checkpoint names to repository ids.",
        "items[] of the collection API response; Supplementary Information, Supplementary Table 1 "
        "(PDF page 21)",
        [SRC_HF, SRC_SI],
    )
    claim(
        "licence", "licence",
        "The paper states a licence for the code (MIT) but none for the released model weights. "
        "The article itself is open access under CC BY 4.0.",
        "Reporting Summary, Software and code, 'Data analysis' (PDF page 23); Open Access "
        "statement (PDF page 10)",
        [SRC_ARTICLE],
    )
    claim(
        "training-data", "training_data",
        "The three human models are trained on whole-genome alignments at three timescales: "
        "multiz100way (100 vertebrates), cactus447way restricted to 447 mammals, and "
        "cactus447way restricted to 243 primates, all on hg38. Chromosomes 1-20, X and Y are "
        "training data, chromosome 21 is validation and chromosome 22 is a held-out test "
        "chromosome. Five further models are trained for Mus musculus (mm39, multiz35way), "
        "Gallus gallus (galGal6, multiz77way), Drosophila melanogaster (dm6, multiz124way), "
        "Caenorhabditis elegans (ce11, multiz135way) and Arabidopsis thaliana (tair10, "
        "multiz18way).",
        "Supplementary Information, Supplementary Table 1 (PDF page 21) and Training Data "
        "(PDF pages 7-8)",
        [SRC_SI],
    )
    claim(
        "architecture", "architecture_hyperparameters",
        "GPN-Star is an encoder-only masked language model whose encoder blocks apply sequence-"
        "wise self-attention, phylogeny-informed cross-attention and a feed-forward network. "
        "Supplementary Table 10 gives the three sizes as 25M, 85M and 200M parameters with 8, 12 "
        "and 16 encoder blocks, hidden dimension 512, 768 and 1024, intermediate size 2048, 3072 "
        "and 4096, 4, 6 and 8 self-attention heads, the same number of cross-attention heads, "
        "attention head dimension 64 and dropout rate 0.1 throughout.",
        "Supplementary Information, Model Architecture (PDF pages 4-7) and Supplementary Table 10 "
        "(PDF page 27)",
        [SRC_SI],
    )
    claim(
        "mutation-rate-calibration", "mutation_rate_calibration",
        "GPN-Star raw scores are calibrated to remove the effect of local mutation rate "
        "variation. The paper reports that the calibration substantially reduced correlations "
        "with Roulette mutation rate estimates while improving performance on most downstream "
        "benchmarks, and that the uncalibrated raw scores were used only for the head-to-head "
        "comparison with GPN-MSA in Supplementary Fig. 20.",
        "Results, genome-wide evolutionary constraints (PDF page 7); Supplementary Information, "
        "Mutation Rate Calibration (PDF page 10) and Supplementary Fig. 20 caption",
        [SRC_ARTICLE, SRC_SI],
    )
    claim(
        "differences-from-gpn-msa", "differences_from_gpn_msa",
        "GPN-Star differs from GPN-MSA in three ways the authors name: it masks and predicts "
        "nucleotides across many species rather than the human genome alone; it encodes "
        "phylogenetic relationships explicitly through its attention modules; and it accepts "
        "alignments of any composition and size, so it does not need the manual species curation "
        "that GPN-MSA required, such as excluding species closely related to human.",
        "Supplementary Information, 'Key differences between GPN-MSA and GPN-Star' (PDF page 2)",
        [SRC_SI],
    )
    claim(
        "prioritized-consequences", "prioritized_variant_consequences",
        "Among the top 0.1% most constrained common variants by GPN-Star (P), missense variants "
        "are the largest class at 33% and 170-fold enriched, followed by variants in distal "
        "enhancer-like regions at 26% and 2.4-fold enriched and their flanks at 8% and 0.35-fold "
        "depleted. Compared with GPN-Star (M), GPN-Star (P) is enriched 1.14-fold in missense "
        "variants; compared with GPN-Star (V) it is enriched 1.52-fold in missense and 3.89-fold "
        "in synonymous variants and depleted in non-exonic classes such as intergenic.",
        "Results, relevant evolutionary timescales (PDF page 5); Supplementary Information, "
        "relevant evolutionary timescales (PDF page 3) with Supplementary Tables 5-8 "
        "(PDF pages 24-26)",
        [SRC_ARTICLE, SRC_SI],
    )
    claim(
        "timescale-guidance", "timescale_guidance",
        "The authors report that coding variants and lower-frequency variants with larger effect "
        "sizes are better predicted by models trained on deeper evolutionary timescales, while "
        "non-coding variants and higher-frequency variants with smaller effect sizes are better "
        "predicted by models trained on shallower timescales, and that GPN-Star predictions "
        "quantify evolutionary constraint at a timescale rather than general variant "
        "pathogenicity.",
        "Results, relevant evolutionary timescales (PDF page 5); Discussion (PDF pages 9-10)",
        [SRC_ARTICLE],
    )
    claim(
        "printed-values-scope", "printed_values_scope",
        "Of this paper's evaluations, four print numbers: Supplementary Table 3 (ablation "
        "studies), the bar labels of Fig. 4b, the bar labels of Fig. 5a for five non-human "
        "species, and the rare variant association gene counts in the Results. The model "
        "comparisons in Figs. 2 and 3, Fig. 4a,c,d, Fig. 5b-d, Extended Data Figs. 1-10 and "
        "Supplementary Figs. 1-27 are plots whose values are not printed, so the paper's headline "
        "comparisons against CADD, GPN-MSA, Evo 2, Nucleotide Transformer, ESM-1b, Enformer, "
        "Borzoi, AlphaGenome, AlphaMissense, PrimateAI-3D, PromoterAI, SpeciesLM, GPN-Promoter, "
        "PhyloP and PhastCons cannot be extracted as values from this source.",
        "Figs. 2-5 and their captions; Extended Data Figs. 1-10; Supplementary Information, "
        "Supplementary Figs. 1-27",
        [SRC_ARTICLE, SRC_SI],
        subject=BENCHMARK,
    )
    claim(
        "benchmark-dataset-provenance", "benchmark_dataset_provenance",
        "The OMIM benchmark uses the processed Mendelian traits dataset from TraitGym and the "
        "non-coding fine-mapping benchmark uses the processed complex traits dataset from "
        "TraitGym, both with nine controls matched per positive on chromosome, molecular "
        "consequence and distance to the transcription start site, and for complex traits also "
        "on LD score and minor allele frequency. HGMD was processed in the same way as the "
        "TraitGym Mendelian traits dataset. Coding fine-mapped variants come from the same "
        "fine-mapping source but are matched on minor allele frequency only. The paper does not "
        "name a TraitGym revision.",
        "Supplementary Information, Evaluation Benchmarks, Homo sapiens, Datasets "
        "(PDF pages 11-12)",
        [SRC_SI],
        subject=BENCHMARK,
    )


# --------------------------------------------------------------------------------------

def main() -> None:
    if len(sys.argv) != 5:
        raise SystemExit(__doc__)
    article_pdf, si_pdf, preprint_pdf, hf_json = (Path(a) for a in sys.argv[1:])
    article = pages(article_pdf, SHA_ARTICLE)
    si = pages(si_pdf, SHA_SI)
    got = sha256(preprint_pdf)
    assert got == SHA_PREPRINT, f"{preprint_pdf}: sha256 {got} != pinned {SHA_PREPRINT}"
    got = sha256(hf_json)
    assert got == SHA_HF, f"{hf_json}: sha256 {got} != pinned {SHA_HF}"
    collection = json.loads(hf_json.read_text())
    released = [i["id"] for i in collection["items"] if i["type"] == "model"]
    assert len(released) == 8, released
    assert released[0] == "songlab/gpn-star-hg38-v100-200m", released

    table3 = parse_supp_table_3(si)
    fig4b = parse_fig_4b(article)
    rvat = parse_rvat(article)
    check_supp_table_1(si)
    check_fig_5a(article)
    check_prose(article, si)

    build_sources()
    build_assessments()
    build_configurations()
    build_ablation(table3)
    build_fig4b(fig4b)
    build_rvat(rvat)
    build_claims()

    ids = [r["id"] for r in records]
    assert len(ids) == len(set(ids)), "duplicate record id"
    out = Path(__file__).resolve().parent.parent / "batch.jsonl"
    out.write_text(
        "".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n"
                for r in sorted(records, key=lambda r: r["id"])),
        encoding="utf-8",
    )
    counts: dict[str, int] = {}
    for r in records:
        counts[r["kind"]] = counts.get(r["kind"], 0) + 1
    print(f"wrote {out} with {len(records)} records")
    for kind in sorted(counts):
        print(f"  {kind:14} {counts[kind]}")


if __name__ == "__main__":
    main()
