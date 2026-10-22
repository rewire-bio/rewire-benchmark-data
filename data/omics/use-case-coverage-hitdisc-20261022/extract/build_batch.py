#!/usr/bin/env python3
"""Build the hit-discovery-virtual-screening evidence batch (rewire-benchmark-data #177).

Re-downloads every pinned artifact, asserts its SHA-256, parses the chosen tables with
asserted row and column labels, and writes batch.jsonl, claims.csv and coverage.json next
to this script's parent directory.

Usage: python3 extract/build_batch.py [cache_dir]

Nothing here reads a figure. Values printed only in a figure are recorded as gaps in
coverage.json instead.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import os
import sys
import urllib.request
import xml.etree.ElementTree as ET
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
BATCH_DIR = os.path.dirname(HERE)
PREFIX = "hitdisc-20261022"
DATE = "2026-10-22"
AREAS = ["molecular-interactions"]
FACETS = {"areas": AREAS, "contexts": ["research"]}
UA = "rewire-benchmark-data extraction (https://github.com/rewire-bio/rewire-benchmark-data)"

REVIEWER_NOTE = (
    "Claude extraction agent; no human review claimed. Extraction for rewire-benchmark-data #177. "
    "Transcription, not reproduction. Pending an independent review-evidence pass."
)
EXTRACT_NOTE = "Extracted, not reviewed. The review-evidence pass must re-check this against the pinned artifact."

# --------------------------------------------------------------------------------------
# Pinned artifacts
# --------------------------------------------------------------------------------------

ARTIFACTS = {
    "shen2025": {
        "url": "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12704515/fullTextXML",
        "sha256": "11a4cee97057d9e72f9393024d22fdd169e3134f493367eee2f7869facf9ccf8",
        "file": "PMC12704515.xml",
    },
    "kim2026": {
        "url": "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13657626/fullTextXML",
        "sha256": "9be510b7b0cc152ff56a03c96877bf06b6a6bdeffdb4baecf8e999a6bf155aa6",
        "file": "PMC13657626.xml",
    },
    "cache3": {
        "url": "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12892310/fullTextXML",
        "sha256": "43b920ac9f67fac3560bcf7d24a79f76b9a0d0d962088dfe4081742ec7b9b071",
        "file": "PMC12892310.xml",
    },
    "cache3_si002": {
        # The Europe PMC supplementaryFiles endpoint builds a zip per request, so the zip's own
        # hash is not stable; the pinned hash is of the member file.
        "url": "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12892310/supplementaryFiles",
        "zip_member": "ci5c02441_si_002.xlsx",
        "sha256": "5e655da5728da46c6a57882c5fef0643c057536d7897d16b9c98f6d55c12f5fe",
        "file": "ci5c02441_si_002.xlsx",
    },
    "litpcba_audit": {
        "url": "https://arxiv.org/abs/2507.21404v2",
        "sha256": "e766c8aa4f94287672b2b1bacab2480a41ec7c806ecbaf5e2d1bf8773781310f",
        "file": "arxiv-2507.21404v2.html",
        "mutable": True,
    },
    "litpcba_page": {
        "url": "https://drugdesign.unistra.fr/LIT-PCBA/",
        "sha256": "a2203612b553236d7f01da5573389d439d2f7aa0436080412f27da882e086e5e",
        "file": "litpcba-page.html",
        "mutable": True,
    },
    "dude2012": {
        "url": "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC3405771/fullTextXML",
        "sha256": "8f20c3adec704671ea668742622567a7c6aec9b38f6d804f977c175209fa500d",
        "file": "PMC3405771.xml",
    },
    "mfpcba2023": {
        "url": "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10170507/fullTextXML",
        "sha256": "628c94a973118410ec616f9342237c141a139ca4f56c34c698c6d9dcb6d82241",
        "file": "PMC10170507.xml",
    },
    "chen2019": {
        "url": "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC6701836/fullTextXML",
        "sha256": "b845c78815bb0c4eabb3e05e65212b343269c91292fedf00fae9ac00c7840f09",
        "file": "PMC6701836.xml",
    },
}

RETRIEVED_AT = {
    "shen2025": "2026-10-22T11:52:32Z",
    "kim2026": "2026-10-22T11:52:32Z",
    "cache3": "2026-10-22T11:52:32Z",
    "cache3_si002": "2026-10-22T11:55:00Z",
    "litpcba_audit": "2026-10-22T11:59:20Z",
    "litpcba_page": "2026-10-22T12:01:54Z",
    "dude2012": "2026-10-22T12:01:54Z",
    "mfpcba2023": "2026-10-22T12:01:54Z",
    "chen2019": "2026-10-22T12:01:54Z",
}


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def fetch(key: str, cache_dir: str) -> bytes:
    spec = ARTIFACTS[key]
    path = os.path.join(cache_dir, spec["file"])
    if os.path.exists(path):
        with open(path, "rb") as fh:
            data = fh.read()
    else:
        req = urllib.request.Request(spec["url"], headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=120) as resp:
            raw = resp.read()
        if "zip_member" in spec:
            with zipfile.ZipFile(io.BytesIO(raw)) as zf:
                data = zf.read(spec["zip_member"])
        else:
            data = raw
        os.makedirs(cache_dir, exist_ok=True)
        with open(path, "wb") as fh:
            fh.write(data)
    got = sha256_bytes(data)
    if got != spec["sha256"]:
        raise SystemExit(f"{key}: SHA-256 {got} does not match the pinned {spec['sha256']}")
    return data


# --------------------------------------------------------------------------------------
# Record helpers
# --------------------------------------------------------------------------------------

RECORDS: list[dict] = []
CLAIM_ROWS: list[dict] = []


def src_id(key: str) -> str:
    return f"{PREFIX}-source-{key.replace('_', '-')}"


def review(methods: list[str], note: str, artifact: str | None = None, method_note: str | None = None) -> dict:
    out = {
        "method": methods,
        "reviewer": ["claude"],
        "reviewer_note": REVIEWER_NOTE,
        "date": DATE,
        "note": note,
    }
    if method_note:
        out["method_note"] = method_note
    if artifact:
        out["artifact_sha256"] = ARTIFACTS[artifact]["sha256"]
        out["retrieval_url"] = ARTIFACTS[artifact]["url"]
    return out


def add(record: dict) -> str:
    RECORDS.append(record)
    return record["id"]


def rec(
    rid: str,
    kind: str,
    name: str,
    description: str,
    status: str,
    sources: list[str],
    attributes: dict,
    links: list[dict] | None = None,
    facets: dict | None = None,
) -> str:
    return add(
        {
            "id": rid,
            "kind": kind,
            "name": name,
            "description": description,
            "status": status,
            "facets": facets if facets is not None else dict(FACETS),
            "source_ids": sources,
            "links": links or [],
            "attributes": attributes,
        }
    )


def claim_row(rid: str, source: str, locator: str, printed: str, scope: str) -> None:
    CLAIM_ROWS.append(
        {
            "record_id": rid,
            "source_id": source,
            "locator": locator,
            "printed_value": printed,
            "review_scope": scope,
        }
    )


def decimal_or_none(text: str) -> str | None:
    t = text.strip().replace("−", "-").replace("–", "-")
    try:
        float(t)
    except ValueError:
        return None
    return t


# --------------------------------------------------------------------------------------
# Table parsing
# --------------------------------------------------------------------------------------


def cell_text(el: ET.Element) -> str:
    return " ".join("".join(el.itertext()).split())


def pmc_tables(xml: bytes) -> dict[str, dict]:
    """Return {label: {"caption":..., "rows": [[(text, colspan, rowspan), ...]], "foot": ...}}."""
    root = ET.fromstring(xml)
    out: dict[str, dict] = {}
    for tw in root.iter("table-wrap"):
        label_el = tw.find("label")
        if label_el is None:
            continue
        label = cell_text(label_el)
        cap = tw.find("caption")
        foot = tw.find(".//table-wrap-foot")
        rows = []
        for tr in tw.iter("tr"):
            row = []
            for c in tr:
                if c.tag in ("td", "th"):
                    row.append((cell_text(c), int(c.get("colspan") or 1), int(c.get("rowspan") or 1)))
            rows.append(row)
        out[label] = {
            "caption": cell_text(cap) if cap is not None else "",
            "rows": rows,
            "foot": cell_text(foot) if foot is not None else "",
        }
    return out


def body_text(xml: bytes) -> str:
    root = ET.fromstring(xml)
    body = root.find(".//body")
    return " ".join("".join(body.itertext()).split())


XL = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
XLR = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"


def xlsx_sheet(data: bytes, sheet_name: str) -> list[dict[str, str]]:
    """Rows of one sheet as {column letter: cell value}, values as stored in the file."""
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        wb = ET.fromstring(zf.read("xl/workbook.xml"))
        rels = ET.fromstring(zf.read("xl/_rels/workbook.xml.rels"))
        relmap = {r.get("Id"): r.get("Target") for r in rels}
        target = None
        for s in wb.iter(XL + "sheet"):
            if s.get("name") == sheet_name:
                target = relmap[s.get(XLR + "id")]
        if target is None:
            raise SystemExit(f"sheet {sheet_name!r} not found")
        if not target.startswith("xl/"):
            target = "xl/" + target.lstrip("/")
        shared = []
        if "xl/sharedStrings.xml" in zf.namelist():
            ss = ET.fromstring(zf.read("xl/sharedStrings.xml"))
            for si in ss.iter(XL + "si"):
                shared.append("".join(t.text or "" for t in si.iter(XL + "t")))
        sheet = ET.fromstring(zf.read(target))
    rows = []
    for row in sheet.iter(XL + "row"):
        cells: dict[str, str] = {}
        for c in row.iter(XL + "c"):
            ref = c.get("r") or ""
            col = "".join(ch for ch in ref if ch.isalpha())
            t = c.get("t")
            v = c.find(XL + "v")
            inline = c.find(XL + "is")
            if t == "s" and v is not None:
                val = shared[int(v.text)]
            elif t == "inlineStr" and inline is not None:
                val = "".join(x.text or "" for x in inline.iter(XL + "t"))
            elif v is not None:
                val = v.text or ""
            else:
                val = ""
            cells[col] = val.strip()
        rows.append(cells)
    return rows


def shortest_decimal(raw: str) -> str:
    """Shortest decimal that round-trips to the stored double, as a spreadsheet displays it."""
    f = float(raw)
    s = repr(f)
    if s.endswith(".0"):
        s = s[:-2]
    return s


# --------------------------------------------------------------------------------------
# Sources
# --------------------------------------------------------------------------------------

SOURCE_META = {
    "shen2025": dict(
        name="Shen et al. 2025, Chemical Science (Europe PMC full text)",
        description="Primary source for the DEKOIS 2.0, GPCRrecent and LIT-PCBA screening comparison of co-folding confidence scores against docking (rewire-benchmark-data #177).",
        version="PMC12704515 (Chem Sci, published 2025-12-11)",
        doi="10.1039/d5sc06481c",
        publication_status="peer_reviewed",
        licence="Creative Commons Attribution-Non Commercial 3.0 Unported Licence (permissions statement in the retrieved XML)",
        locator="Tables 1-5 and their footnotes; Methods 'Datasets', 'Complex structure prediction', 'Scoring schemes', 'Baseline docking results', 'Evaluation metrics'; Data availability",
    ),
    "kim2026": dict(
        name="Kim, Correy, Hall et al. 2026, eLife 15:RP110475 (Europe PMC full text)",
        description="Primary source for the re-ranking of three tested ultra-large docking hit lists by AlphaFold3 and Boltz-2 against DOCK3.7 (rewire-benchmark-data #177).",
        version="PMC13657626 (eLife 2026;15:RP110475, version of record published 2026-10-12)",
        doi="10.7554/eLife.110475",
        publication_status="peer_reviewed",
        licence="Creative Commons Attribution License (permissions statement in the retrieved XML)",
        locator="Results 'Co-folding struggles to reliably re-rank docking hit lists'; Methods 'Benchmarking co-folding on experimentally validated compounds', 'Molecular docking of Mac1 compounds', 'Co-folding', 'Hit rate curves for different scoring methods'",
    ),
    "cache3": dict(
        name="Herasymenko et al. 2026, J Chem Inf Model (CACHE Challenge #3, Europe PMC full text)",
        description="Primary source for the blinded prospective CACHE #3 hit-discovery challenge on the SARS-CoV-2 Nsp3 macrodomain (rewire-benchmark-data #177).",
        version="PMC12892310 (J Chem Inf Model, published 2026-01-21)",
        doi="10.1021/acs.jcim.5c02441",
        publication_status="peer_reviewed",
        licence="CC-BY 4.0 (https://creativecommons.org/licenses/by/4.0/, permissions statement in the retrieved XML)",
        locator="Results 'Discovering Chemically Novel Ligands Was Challenging' and 'Trends and Strategies from the Best Performing Computational Workflows'; Figure 6 caption; Table 2",
    ),
    "cache3_si002": dict(
        name="Herasymenko et al. 2026, CACHE Challenge #3, Supporting Information workbook ci5c02441_si_002.xlsx",
        description="Supporting workbook holding the per-workflow CACHE #3 scoring table S8 behind Figure 6 (rewire-benchmark-data #177).",
        version="ci5c02441_si_002.xlsx, member of the Europe PMC supplementary archive of PMC12892310",
        doi="10.1021/acs.jcim.5c02441",
        publication_status="peer_reviewed",
        licence="CC-BY 4.0 (the article's licence; the workbook carries no separate statement)",
        locator="Sheet 'S8' (per-workflow scoring); sheets S1-S7 and the Title Page were not extracted",
    ),
    "litpcba_audit": dict(
        name="Huang, Knight and Naprienko 2025, arXiv:2507.21404v2 (abstract page)",
        description="Primary source for the data-leakage audit of the LIT-PCBA virtual-screening benchmark (rewire-benchmark-data #177).",
        version="arXiv:2507.21404v2, submitted 2025-07-29, this version 2025-08-07",
        doi=None,
        publication_status="preprint",
        licence="http://creativecommons.org/licenses/by/4.0/ (stated on the retrieved abstract page)",
        locator="Abstract; title; submission history",
    ),
    "litpcba_page": dict(
        name="LIT-PCBA official project page, drugdesign.unistra.fr",
        description="Official project page for the LIT-PCBA virtual-screening dataset, with its per-target active and inactive counts.",
        version="Page as retrieved 2026-10-22; no version is printed on the page",
        doi=None,
        publication_status="official_project_source",
        licence="Not stated on the retrieved page",
        locator="Data content table (AID, Set, Target, Ligands, Actives, Inactives, PDB templates)",
    ),
    "dude2012": dict(
        name="Mysinger et al. 2012, J Med Chem 55:6582 (DUD-E, Europe PMC full text)",
        description="Primary source for the DUD-E property-matched decoy benchmark (rewire-benchmark-data #177).",
        version="PMC3405771 (J Med Chem 2012)",
        doi="10.1021/jm300687e",
        publication_status="peer_reviewed",
        licence="ACS AuthorChoice open-access terms (permissions statement in the retrieved XML)",
        locator="Abstract",
    ),
    "mfpcba2023": dict(
        name="Buterez et al. 2023, J Chem Inf Model (MF-PCBA, Europe PMC full text)",
        description="Primary source for the MF-PCBA multifidelity high-throughput screening benchmark (rewire-benchmark-data #177).",
        version="PMC10170507 (J Chem Inf Model 2023)",
        doi="10.1021/acs.jcim.2c01569",
        publication_status="peer_reviewed",
        licence="CC-BY 4.0 (https://creativecommons.org/licenses/by/4.0/, permissions statement in the retrieved XML)",
        locator="Abstract",
    ),
    "chen2019": dict(
        name="Chen et al. 2019, PLoS ONE 14:e0220113 (hidden bias in DUD-E, Europe PMC full text)",
        description="Primary source for the finding that deep-learning virtual-screening performance on DUD-E is driven by decoy artefacts (rewire-benchmark-data #177).",
        version="PMC6701836 (PLoS ONE 2019)",
        doi="10.1371/journal.pone.0220113",
        publication_status="peer_reviewed",
        licence="Creative Commons Attribution License (permissions statement in the retrieved XML)",
        locator="Abstract",
    ),
}


def build_sources() -> None:
    for key, meta in SOURCE_META.items():
        spec = ARTIFACTS[key]
        attrs = {
            "url": spec["url"],
            "version": meta["version"],
            "retrieved_at": RETRIEVED_AT[key],
            "artifact_sha256": spec["sha256"],
            "publication_status": meta["publication_status"],
            "licence": meta["licence"],
            "source_locator": meta["locator"],
            "retrieval_method": "HTTP GET with urllib, no authentication",
            "review": review(
                ["source-hash-verification"],
                "Retrieved and hashed by extract/build_batch.py on 2026-10-22. Not re-checked by a reviewer.",
                key,
            ),
        }
        if meta["doi"]:
            attrs["doi"] = meta["doi"]
        else:
            attrs["missing_metadata"] = {"doi": {"reason": "unreported", "note": "No DOI is printed for this artifact"}}
        if key == "cache3_si002":
            attrs["artifact_member"] = ARTIFACTS[key]["zip_member"]
            attrs["hash_scope"] = (
                "artifact_sha256 is the SHA-256 of the member file ci5c02441_si_002.xlsx. The Europe PMC "
                "supplementaryFiles endpoint assembles a zip per request, so the archive's own hash is not "
                "stable; the member file's bytes are. The publisher's direct supplement URL "
                "(https://pubs.acs.org/doi/suppl/10.1021/acs.jcim.5c02441/suppl_file/ci5c02441_si_002.xlsx) "
                "returned HTTP 403 on 2026-10-22."
            )
            attrs["media_type"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        elif spec.get("mutable"):
            attrs["hash_scope"] = (
                "This is a mutable web page: artifact_sha256 describes the single retrieval of "
                f"{RETRIEVED_AT[key]} and a later change to the page would change it."
            )
            attrs["media_type"] = "text/html"
        else:
            attrs["media_type"] = "application/xml"
        if key == "litpcba_page":
            attrs["evidence_concerns"] = [
                {
                    "source_id": src_id(key),
                    "message": (
                        "The official page gives 7761 actives and 382674 unique inactives for the 15 LIT-PCBA "
                        "target sets, while Shen et al. 2025 state 10030 confirmed actives and 2798737 confirmed "
                        "inactives for the full set. The two counts are not reconciled by either source; the "
                        "difference is most likely unique against per-target inactives, but neither source says so."
                    ),
                    "source_locator": "Data content table (page) against Shen et al. 2025 Methods 'Datasets'",
                    "artifact_sha256": spec["sha256"],
                    "review_date": DATE,
                }
            ]
        if key == "litpcba_audit":
            attrs["evidence_concerns"] = [
                {
                    "source_id": src_id(key),
                    "message": (
                        "This preprint audits LIT-PCBA itself and concludes that extensive analogue and "
                        "2D-identical-compound leakage between its splits means a parameter-free memorisation "
                        "baseline matches or exceeds published deep-learning and 3D-similarity results, so nearly "
                        "all published LIT-PCBA results are undermined and zero-shot evaluations are also affected. "
                        "It bears on every LIT-PCBA result in this store. It is a preprint and its tables were not "
                        "retrieved: only the abstract was read."
                    ),
                    "source_locator": "Abstract",
                    "artifact_sha256": spec["sha256"],
                    "review_date": DATE,
                }
            ]
        rec(
            src_id(key),
            "source",
            meta["name"],
            meta["description"],
            "needs_review",
            [],
            attrs,
        )


# --------------------------------------------------------------------------------------
# Reused store IDs
# --------------------------------------------------------------------------------------

REUSED = {
    "af3": "discovery-model-alphafold-3",
    "boltz2": "catalog-model-boltz-2",
    "boltz_family": "discovery-model-boltz",
    "protenix": "ucc-research-model-protenix",
    "vina_method": "discovery-model-autodock-vina",
    "task": "reported-task-a7803ecf7708cc",
}


# --------------------------------------------------------------------------------------
# Methods and datasets
# --------------------------------------------------------------------------------------


def build_methods() -> None:
    rec(
        f"{PREFIX}-method-glide",
        "method",
        "Glide",
        "Physics-based molecular docking program that generates and scores protein-ligand poses at standard precision (SP) and extra precision (XP).",
        "needs_review",
        [src_id("shen2025")],
        {
            "entity_level": "method",
            "reported_name": "Glide",
            "version": "Implemented in Schrodinger version 2020-4 as used by Shen et al. 2025",
            "access": "Commercial (Schrodinger); no access terms are stated in the source",
            "source_locator": "Methods 'Glide'; Results 'Evaluation of AF3's built-in confidence scores on DEKOIS2.0 dataset'",
            "provenance_note": "Created from the comparator description in Shen et al. 2025; the Glide primary papers (refs 27 and 65 of that source) were not retrieved.",
            "review": review(["transcription"], EXTRACT_NOTE, "shen2025"),
        },
        facets={"areas": AREAS, "contexts": ["research"], "method_types": ["conventional_pipeline"]},
    )
    rec(
        f"{PREFIX}-method-gnina",
        "method",
        "Gnina",
        "Molecular docking program that scores protein-ligand poses with the classical AD4, Vina and Vinardo functions and with the CNNscore and CNNaffinity convolutional neural network functions.",
        "needs_review",
        [src_id("shen2025")],
        {
            "entity_level": "method",
            "reported_name": "Gnina",
            "version": "1.3 (as used by Shen et al. 2025)",
            "access": "No access terms are stated in the source",
            "source_locator": "Methods 'Gnina'; Methods 'Baseline docking results'",
            "provenance_note": "Created from the comparator description in Shen et al. 2025; the Gnina primary paper (ref 32 of that source) was not retrieved.",
            "review": review(["transcription"], EXTRACT_NOTE, "shen2025"),
        },
        facets={"areas": AREAS, "contexts": ["research"], "method_types": ["supervised_machine_learning"]},
    )
    rec(
        f"{PREFIX}-method-dock37",
        "method",
        "DOCK3.7",
        "Physics-based docking program that pre-samples ligand conformations onto matching spheres in a binding site and scores them by summed receptor-ligand electrostatic and van der Waals energies corrected for context-dependent ligand desolvation.",
        "needs_review",
        [src_id("kim2026")],
        {
            "entity_level": "method",
            "reported_name": "DOCK3.7",
            "access": "Hit lists available from https://lsd.docking.org/ (Data availability); no licence is stated for the program",
            "source_locator": "Methods 'Molecular docking of Mac1 compounds'; Results 'Co-folding struggles to reliably re-rank docking hit lists'",
            "provenance_note": "Created from the method description in Kim, Correy, Hall et al. 2026; the DOCK3.7 primary papers were not retrieved.",
            "missing_metadata": {"version": {"reason": "unreported", "note": "The source names the program as DOCK3.7 but no build or release"}},
            "review": review(["transcription"], EXTRACT_NOTE, "kim2026"),
        },
        facets={"areas": AREAS, "contexts": ["research"], "method_types": ["conventional_pipeline"]},
    )
    rec(
        f"{PREFIX}-method-tocodecoy",
        "method",
        "TocoDecoy",
        "Generates property-matched decoy molecules for virtual-screening benchmarks with a conditional recurrent neural network instead of selecting them from an existing compound library.",
        "discovered",
        [src_id("shen2025")],
        {
            "entity_level": "method",
            "reported_name": "TocoDecoy",
            "access": "No access terms are stated in the retrieved source",
            "source_locator": "Methods 'Datasets'",
            "provenance_note": "Created from the description in Shen et al. 2025, which used a streamlined implementation of it. The TocoDecoy primary paper (doi 10.1021/acs.jmedchem.2c00460) is closed access and was not retrieved.",
            "missing_metadata": {"version": {"reason": "unreported", "note": "Shen et al. 2025 describe a 'streamlined implementation' without a version"}},
            "review": review(["transcription"], EXTRACT_NOTE, "shen2025"),
        },
        facets={"areas": AREAS, "contexts": ["research"], "method_types": ["supervised_machine_learning"]},
    )


def build_benchmarks_and_data() -> None:
    # ---- DEKOIS 2.0
    rec(
        f"{PREFIX}-benchmark-dekois2",
        "benchmark",
        "DEKOIS 2.0",
        "Virtual-screening benchmark that scores a method on how well it ranks experimentally validated actives above property-matched decoys for each of its targets.",
        "needs_review",
        [src_id("shen2025")],
        {
            "entity_level": "suite",
            "task": "Protein-ligand virtual screening (library ranking)",
            "scope_note": (
                "As described by Shen et al. 2025: 81 structurally diverse targets, each with 40 experimentally "
                "validated actives from BindingDB and 1200 property-matched decoys selected from ZINC, an "
                "actives-to-decoys ratio of 1:30. Data at http://www.dekois.com."
            ),
            "source_locator": "Methods 'Datasets'; Data availability",
            "limitations": [
                "The decoys are synthetic property-matched molecules, not measured inactives, so enrichment factors on this benchmark are not comparable with benchmarks whose negatives were assayed.",
                "The set was released over ten years before Shen et al. 2025 and its template protein structures may overlap substantially with the training data of the co-folding models scored on it (Results 'Performance on GPCRrecent dataset').",
            ],
            "missing_metadata": {
                "version": {
                    "reason": "unavailable",
                    "note": "The DEKOIS 2.0 primary paper (doi 10.1021/ci400115b) is closed access and was not retrieved; the composition recorded here is as Shen et al. 2025 describe it",
                }
            },
            "review": review(["transcription"], EXTRACT_NOTE, "shen2025"),
        },
    )
    rec(
        f"{PREFIX}-dataset-dekois2-79",
        "dataset",
        "DEKOIS 2.0, 79 targets as scored by Shen et al. 2025",
        "The 79 DEKOIS 2.0 targets Shen et al. 2025 screened, each with 40 BindingDB actives and 1200 property-matched ZINC decoys.",
        "needs_review",
        [src_id("shen2025")],
        {
            "version": "DEKOIS 2.0 as distributed at http://www.dekois.com; no release identifier is printed",
            "split": "Whole benchmark, 79 of the 81 targets; pygl-in and pygl-out were excluded because their protein-protein interface binding makes structural modelling computationally expensive",
            "population": "79 targets, 40 experimentally validated actives and 1200 property-matched decoys per target (1:30)",
            "label_semantics": "Positive: experimentally validated active from BindingDB. Negative: property-matched decoy selected from ZINC, not an assayed inactive.",
            "total_targets": 79,
            "access": "http://www.dekois.com (Data availability)",
            "source_locator": "Methods 'Datasets'; Data availability",
            "review": review(["transcription"], EXTRACT_NOTE, "shen2025"),
        },
    )
    rec(
        f"{PREFIX}-dataset-dekois2-speed5",
        "dataset",
        "DEKOIS 2.0 speed subset, five targets with 400 decoys each",
        "Five DEKOIS 2.0 targets, each with 400 randomly selected decoys, used to time the co-folding methods per compound.",
        "needs_review",
        [src_id("shen2025")],
        {
            "version": "DEKOIS 2.0 as distributed at http://www.dekois.com; no release identifier is printed",
            "split": "Five representative targets (a2a, ar, cdk2, ctsk, hdac2), each with 400 randomly selected decoys",
            "population": "Five targets; 400 randomly selected decoys per target",
            "total_targets": 5,
            "source_locator": "Results 'Assessment of computational efficiency'; Table 5 caption",
            "missing_metadata": {"split_seeds": {"reason": "unreported", "note": "The source does not state the seed for the random decoy selection"}},
            "review": review(["transcription"], EXTRACT_NOTE, "shen2025"),
        },
    )
    # ---- GPCRrecent
    rec(
        f"{PREFIX}-benchmark-gpcrrecent",
        "benchmark",
        "GPCRrecent",
        "Virtual-screening benchmark of G protein-coupled receptor targets whose first crystal structures were determined after 2022, scoring how well a method ranks BindingDB actives above generated property-matched decoys.",
        "needs_review",
        [src_id("shen2025")],
        {
            "entity_level": "suite",
            "task": "Protein-ligand virtual screening (library ranking)",
            "version": "Curated by Shen et al. 2025; data at https://zenodo.org/records/16826965",
            "scope_note": (
                "Built so that the targets are temporally separated from AlphaFold3's training data: targets whose "
                "first crystal structure was released after 2022, with BindingDB actives below 10 uM activity, "
                "peptide-like inhibitors and natural products above 600 Da excluded, actives clustered on Murcko "
                "scaffolds with the most potent representative per cluster kept, at most 300 diverse scaffolds per "
                "target and targets with fewer than 200 actives removed; 16 GPCRs result. Decoys are generated by a "
                "streamlined TocoDecoy implementation at a 1:50 actives-to-decoys ratio."
            ),
            "source_locator": "Methods 'Datasets'; Results 'Performance on GPCRrecent dataset'; Data availability",
            "limitations": [
                "The decoys are generated by a conditional recurrent neural network, not assayed inactives, so enrichment factors are not comparable with benchmarks whose negatives were measured.",
                "Temporal separation holds for crystal structures, not for binding data: the authors exclude the Boltz-2 affinity module from this analysis because its training sources (for example BindingDB) overlap the benchmark's composition.",
                "The per-target composition is in Table S1, which was not retrieved.",
            ],
            "review": review(["transcription"], EXTRACT_NOTE, "shen2025"),
        },
    )
    rec(
        f"{PREFIX}-dataset-gpcrrecent-16",
        "dataset",
        "GPCRrecent, 16 GPCR targets",
        "Sixteen G protein-coupled receptor targets with BindingDB actives and TocoDecoy-generated property-matched decoys at a 1:50 ratio.",
        "needs_review",
        [src_id("shen2025")],
        {
            "version": "https://zenodo.org/records/16826965 (Data availability); no version string is printed",
            "split": "Whole curated set, 16 targets",
            "population": "16 GPCR targets; actives from BindingDB with IC50, EC50, Ki or Kd below 10 uM, at most 300 diverse Murcko scaffolds per target and at least 200 actives per target; decoys generated by TocoDecoy at 1:50",
            "label_semantics": "Positive: BindingDB active below 10 uM. Negative: decoy generated by a conditional recurrent neural network, not an assayed inactive.",
            "total_targets": 16,
            "access": "https://zenodo.org/records/16826965",
            "source_locator": "Methods 'Datasets'; Data availability",
            "missing_metadata": {"positives": {"reason": "unextracted", "note": "Per-target active and decoy counts are in Table S1, which was not retrieved"}},
            "review": review(["transcription"], EXTRACT_NOTE, "shen2025"),
        },
    )
    rec(
        f"{PREFIX}-dataset-gpcrrecent-6",
        "dataset",
        "GPCRrecent, six targets after the Boltz-2 training cutoff",
        "The six GPCRrecent targets whose first crystal structures were released after Boltz-2's June 2023 training cutoff.",
        "needs_review",
        [src_id("shen2025")],
        {
            "version": "https://zenodo.org/records/16826965 (Data availability); no version string is printed",
            "split": "Six of the 16 GPCRrecent targets: UniProt O15552, P0DMS8, P13945, P35348, P46098, Q96RJ0",
            "population": "Six GPCR targets whose first crystal structures were released after 2023-06, the temporal cutoff of Boltz-2's training data",
            "total_targets": 6,
            "source_locator": "Table 3 footnote a; Results 'Performance on GPCRrecent dataset'",
            "review": review(["transcription"], EXTRACT_NOTE, "shen2025"),
        },
    )
    # ---- LIT-PCBA
    rec(
        f"{PREFIX}-benchmark-litpcba",
        "benchmark",
        "LIT-PCBA",
        "Virtual-screening benchmark whose actives and inactives are both experimentally measured, taken from high-confidence PubChem BioAssay dose-response data.",
        "needs_review",
        [src_id("litpcba_page"), src_id("shen2025"), src_id("litpcba_audit")],
        {
            "entity_level": "suite",
            "task": "Protein-ligand virtual screening (library ranking)",
            "version": "Full data and AVE-unbiased data as published on the official page; no version string is printed",
            "scope_note": (
                "15 target sets. The official page states 7761 actives and 382674 unique inactives from "
                "high-confidence PubChem BioAssay data, with per-target counts and an AVE-unbiased split published "
                "alongside the full data; Shen et al. 2025 state 10030 confirmed actives and 2798737 confirmed "
                "inactives for the full set. Because the inactives are measured rather than synthetic, and because "
                "the actives-to-inactives ratio reaches about 1:18000 for ADRB2, enrichment factors on LIT-PCBA sit "
                "far below those on property-matched decoy benchmarks."
            ),
            "source_locator": "Official page data content table; Shen et al. 2025 Methods 'Datasets'",
            "limitations": [
                "Huang, Knight and Naprienko 2025 audit the benchmark and report extensive leakage between its splits: 323 active training-validation analogue pairs at ECFP4 Tanimoto at or above 0.6 in ALDH1 alone, and 2491 2D-identical inactives shared between training and validation across targets. They conclude that a parameter-free memorisation baseline matches or exceeds published deep-learning and 3D-similarity results, that nearly all published LIT-PCBA results are undermined, that zero-shot evaluations are also affected by analogue leakage into the query set, and that the benchmark in its current form does not measure recovery of novel chemotypes.",
                "The official page and Shen et al. 2025 give different active and inactive totals and neither reconciles them.",
                "The LIT-PCBA primary paper (doi 10.1021/acs.jcim.0c00155) is closed access and was not retrieved.",
            ],
            "review": review(["transcription"], EXTRACT_NOTE, "litpcba_page"),
        },
    )
    rec(
        f"{PREFIX}-dataset-litpcba-full",
        "dataset",
        "LIT-PCBA full dataset, 15 target sets",
        "All 15 LIT-PCBA target sets with their experimentally measured actives and inactives from PubChem BioAssay dose-response data.",
        "needs_review",
        [src_id("litpcba_page")],
        {
            "version": "Full data as linked from the official page on 2026-10-22; no version string is printed",
            "split": "Full data; an AVE-unbiased split is published separately",
            "population": "15 target sets; 7761 actives and 382674 unique inactives on the official page",
            "label_semantics": "Positive and negative labels both come from high-confidence PubChem BioAssay dose-response measurements; the inactives are assayed, not synthetic decoys.",
            "positives": 7761,
            "negatives": 382674,
            "total_targets": 15,
            "access": "Open download from https://drugdesign.unistra.fr/LIT-PCBA/",
            "source_locator": "Data content table",
            "review": review(["deterministic-table-parse"], EXTRACT_NOTE, "litpcba_page"),
        },
    )
    rec(
        f"{PREFIX}-dataset-litpcba-5",
        "dataset",
        "LIT-PCBA five-target subset as scored by Shen et al. 2025",
        "The five LIT-PCBA target sets with fewer than 100000 compounds each that Shen et al. 2025 screened.",
        "needs_review",
        [src_id("shen2025"), src_id("litpcba_page")],
        {
            "version": "LIT-PCBA full data as distributed at https://drugdesign.unistra.fr/LIT-PCBA; no version string is printed",
            "split": "Five of the 15 target sets: ESR_ago, ESR_antago, PPARG, TP53 and MAPK1. MTORC1 meets the size criterion but was excluded because the binding sites in its recommended PDB structures are ambiguous.",
            "population": "Five target sets, each with fewer than 100000 compounds; actives and inactives both experimentally measured",
            "total_targets": 5,
            "source_locator": "Methods 'Datasets'; Results 'Performance on a subset of LIT-PCBA dataset'; Table 4",
            "review": review(["transcription"], EXTRACT_NOTE, "shen2025"),
        },
    )
    for key, (label, target, actives, inactives) in LITPCBA_TARGETS.items():
        rec(
            f"{PREFIX}-subset-litpcba-{key.lower().replace('_', '-')}",
            "dataset_subset",
            f"LIT-PCBA {label}",
            f"The LIT-PCBA {label} target set: {target}, with {actives} measured actives and {inactives} measured inactives.",
            "needs_review",
            [src_id("litpcba_page")],
            {
                "positive_count": actives,
                "population_count": f"{actives} actives and {inactives} inactives, a ratio of about 1:{round(inactives / actives)}",
                "source_dataset": f"{PREFIX}-dataset-litpcba-full",
                "source_locator": f"Data content table, row '{label}'",
                "review": review(["deterministic-table-parse"], EXTRACT_NOTE, "litpcba_page"),
            },
            links=[{"relation": "used_in", "target_id": f"{PREFIX}-dataset-litpcba-5"}],
        )
    # ---- Kim et al. docking hit lists
    for key, meta in KIM_SETS.items():
        rec(
            f"{PREFIX}-dataset-kim-{key}",
            "dataset",
            meta["name"],
            meta["description"],
            "needs_review",
            [src_id("kim2026")],
            {
                "version": "Compounds and measured potencies as provided in Supplementary file 5; the hit lists are available from https://lsd.docking.org/",
                "split": "Whole tested set; no training or test split applies",
                "population": meta["population"],
                "label_semantics": meta["labels"],
                "positives": meta["positives"],
                "negatives": meta["negatives"],
                "total": meta["positives"] + meta["negatives"],
                "assay": meta["assay"],
                "access": "Supplementary file 5; hit lists from https://lsd.docking.org/",
                "source_locator": meta["locator"],
                "review": review(["transcription"], EXTRACT_NOTE, "kim2026"),
            },
        )
    # ---- CACHE #3
    rec(
        f"{PREFIX}-benchmark-cache3",
        "benchmark",
        "CACHE Challenge #3",
        "Blinded prospective community challenge in which computational teams select commercially available compounds for a named target, the organisers synthesise and assay them, and confirmed hits are scored by an independent Hit Evaluation Committee.",
        "needs_review",
        [src_id("cache3")],
        {
            "entity_level": "challenge",
            "task": "Prospective hit identification for the SARS-CoV-2 Nsp3 macrodomain (Mac1)",
            "scope_note": (
                "Round 1 (hit identification): each of 23 workflows selected up to 100 commercially available "
                "compounds; 1739 were synthesised by Enamine and tested. All 1739 were screened at 100 uM by "
                "homogeneous time-resolved fluorescence (HTRF); 302 reduced the binding signal by 30% or more in at "
                "least one of two duplicates or gave ambiguous data and went to a limited three-point dose response, "
                "then to surface plasmon resonance; 28 advanced to Round 2. In parallel all 1739 were soaked with "
                "crystallised Nsp3-Mac1, giving complex structures for 44. Round 2 (hit expansion): up to 50 close "
                "analogues per team, 296 compounds tested, 84 confirmed. Teams were also asked to predict actives "
                "from the merged library of all 1739 Round 1 compounds, so that every workflow ran on the same "
                "library; confirmed hits with a score above 15 were clustered into four chemically novel Tier 1 "
                "compounds and 25 Tier 2 compounds."
            ),
            "source_locator": "Results 'Compounds Were Drug-like and Chemically Diverse', 'Discovering Chemically Novel Ligands Was Challenging', 'Selection and Experimental Testing of Round 2 Compounds'; Figure 6 caption",
            "limitations": [
                "The challenge scores confirmed hits with an activity score set by a Hit Evaluation Committee and a novelty score voted by three chemists. It does not publish a per-workflow hit rate.",
                "Targets and libraries were chosen by the organisers and predictions were submitted before testing, so there is no training-overlap control in the usual sense; the Nsp3-Mac1 binding features were already well documented, and 61 Mac1 ligands had been published.",
                "Only the published CACHE #3 round is extracted here. The CACHE #1 and #2 results papers (doi 10.1021/acs.jcim.4c01267 and 10.1021/acs.jcim.5c00535) are not open access and were not retrieved.",
            ],
            "review": review(["transcription"], EXTRACT_NOTE, "cache3"),
        },
    )
    rec(
        f"{PREFIX}-dataset-cache3-round1",
        "dataset",
        "CACHE #3 Round 1 compound library",
        "The 1739 commercially available compounds selected by the 23 CACHE #3 workflows, synthesised by Enamine and assayed against the SARS-CoV-2 Nsp3 macrodomain.",
        "needs_review",
        [src_id("cache3")],
        {
            "version": "CACHE #3 Round 1 as published 2026-01-21",
            "split": "Whole Round 1 library; no training or test split applies",
            "population": "1739 compounds selected by 23 workflows, 41 to 99 per workflow; 1592 had a Tanimoto distance greater than 0.6 from the 61 previously published Nsp3-Mac1 ligands and only six had a distance below 0.35",
            "label_semantics": "Positive: experimentally confirmed hit by HTRF and surface plasmon resonance, scored by the Hit Evaluation Committee. 28 of the 1739 advanced to Round 2; 29 confirmed hits scored above 15 and were clustered into four Tier 1 (chemically novel) and 25 Tier 2 compounds.",
            "total": 1739,
            "assay": "HTRF at 100 uM measuring displacement of an ADPr peptide, then a three-point dose response at 25, 50 and 100 uM, then surface plasmon resonance; crystal soaking in parallel",
            "access": "Per-compound data in Tables S2 and S3 of the Supporting Information",
            "source_locator": "Results 'Compounds Were Drug-like and Chemically Diverse' and 'Discovering Chemically Novel Ligands Was Challenging'; Figure 4",
            "review": review(["transcription"], EXTRACT_NOTE, "cache3"),
        },
    )
    # ---- benchmark primaries registered as discovered
    rec(
        f"{PREFIX}-benchmark-dude",
        "benchmark",
        "DUD-E (Directory of Useful Decoys, Enhanced)",
        "Virtual-screening benchmark that scores ligand enrichment against property-matched decoys for each target.",
        "discovered",
        [src_id("dude2012"), src_id("chen2019")],
        {
            "entity_level": "suite",
            "task": "Protein-ligand virtual screening (library ranking)",
            "version": "DUD-E as published in 2012; no release identifier is printed in the abstract",
            "scope_note": "102 proteins with 22886 clustered ligands drawn from ChEMBL, each ligand with 50 property-matched decoys drawn to be topologically dissimilar to the ligands. Targets include GPCRs and ion channels.",
            "source_locator": "Abstract",
            "limitations": [
                "Chen et al. 2019 report that convolutional neural network models trained on DUD-E can distinguish actives from decoys using artefacts of how the decoys were constructed rather than protein-ligand binding, so DUD-E performance of such models is misleading.",
                "Registered without results: no evaluation on DUD-E is extracted in this batch.",
            ],
            "review": review(["transcription"], EXTRACT_NOTE, "dude2012"),
        },
    )
    rec(
        f"{PREFIX}-benchmark-mfpcba",
        "benchmark",
        "MF-PCBA",
        "Multifidelity high-throughput screening benchmark that pairs primary single-concentration screening data with dose-response confirmation for the same compounds.",
        "discovered",
        [src_id("mfpcba2023")],
        {
            "entity_level": "suite",
            "task": "Molecular property and activity prediction from high-throughput screening data",
            "version": "MF-PCBA as published in 2023; no release identifier is printed in the abstract",
            "scope_note": "Built from PubChem high-throughput screening campaigns, pairing large primary-screen measurements with the smaller confirmatory dose-response data for the same compounds.",
            "source_locator": "Abstract",
            "limitations": ["Registered without results: no evaluation on MF-PCBA is extracted in this batch."],
            "review": review(["transcription"], EXTRACT_NOTE, "mfpcba2023"),
        },
    )


LITPCBA_TARGETS = {
    "ESR_ago": ("ESR_ago", "estrogen receptor alpha agonists", 13, 4378),
    "ESR_antago": ("ESR_antago", "estrogen receptor alpha antagonists", 88, 3820),
    "PPARG": ("PPARG", "peroxisome proliferator-activated receptor gamma inhibitors", 24, 4071),
    "TP53": ("TP53", "cellular tumor antigen p53 inhibitors", 64, 3345),
    "MAPK1": ("MAPK1", "mitogen-activated protein kinase 1 inhibitors", 308, 61567),
}

KIM_SETS = {
    "sigma2": dict(
        name="Sigma-2 receptor docking hit list, 506 tested compounds",
        description="The 506 compounds from a 490-million molecule DOCK3.7 screen against the sigma-2 receptor that were synthesised and assayed, split into measured binders and high-ranking docking false positives.",
        population="506 tested compounds from a 490-million molecule screen: 201 true hits and 305 non-binders",
        labels="True hit: apparent Ki below 2.0 uM, from 25% displacement of [3H]ditolylguanidine measured at 1 uM and converted with the Cheng-Prusoff equation. The rest are non-binders, which are high-ranking docking false positives rather than property-matched decoys.",
        positives=201,
        negatives=305,
        assay="Radioligand displacement of [3H]ditolylguanidine, single concentration at 1 uM",
        locator="Results 'Co-folding struggles to reliably re-rank docking hit lists'; Methods 'Benchmarking co-folding on experimentally validated compounds'",
    ),
    "d4": dict(
        name="Dopamine D4 receptor docking hit list, 541 tested compounds",
        description="The 541 compounds from a 138-million molecule DOCK3.7 screen against the dopamine D4 receptor that were synthesised and assayed, split into measured binders and high-ranking docking false positives.",
        population="541 tested compounds from a 138-million molecule screen: 205 true hits and 336 non-binders",
        labels="True hit: apparent Ki below 7.8 uM, from 25% displacement of [3H]N-methylspiperone measured at 10 uM and converted with the Cheng-Prusoff equation. The rest are non-binders, which are high-ranking docking false positives rather than property-matched decoys.",
        positives=205,
        negatives=336,
        assay="Radioligand displacement of [3H]N-methylspiperone, single concentration at 10 uM",
        locator="Results 'Co-folding struggles to reliably re-rank docking hit lists'; Methods 'Benchmarking co-folding on experimentally validated compounds'",
    ),
    "ampc": dict(
        name="AmpC beta-lactamase docking hit list, 1293 tested compounds",
        description="The 1293 compounds from a 1.7-billion molecule DOCK3.7 screen against AmpC beta-lactamase that were synthesised and assayed, split into measured inhibitors and high-ranking docking false positives.",
        population="1293 tested compounds sampled from scoring bins within the top-scoring 1% of 1.7 billion docked molecules: 247 true hits and 1046 non-binders",
        labels="True hit: apparent Ki below 400 uM. The rest are non-binders, which are high-ranking docking false positives rather than property-matched decoys.",
        positives=247,
        negatives=1046,
        assay="Enzyme inhibition, apparent Ki",
        locator="Results 'Co-folding struggles to reliably re-rank docking hit lists'; Methods 'Benchmarking co-folding on experimentally validated compounds'",
    ),
}


# --------------------------------------------------------------------------------------
# Configurations
# --------------------------------------------------------------------------------------

AF3_VER = "AlphaFold3 version 3.0.0, five predictions with random seed 1, Jackhmmer MSAs (HMMER 3.4.0)"
PTX_VER = "Protenix version 0.4.4, five predictions with random seed 1, MMseqs2 web-service MSAs"
BZ2_VER = "Boltz-2 version 2.0.0, the recommended single model with random seed 1, MMseqs2 web-service MSAs"
SCHRO = "Schrodinger version 2020-4"
GNINA_VER = "Gnina version 1.3"

COFOLD_SCORES = [
    ("af3-ranking", "AF3 (ranking score)", "af3", "ranking score", AF3_VER),
    ("af3-ptm", "AF3 (pTM)", "af3", "pTM", AF3_VER),
    ("af3-iptm", "AF3 (ipTM)", "af3", "ipTM", AF3_VER),
    ("af3-minipae", "AF3 (min-iPAE)", "af3", "min-iPAE", AF3_VER),
    ("boltz2-ranking", "Boltz-2 (ranking score)", "boltz2", "ranking score", BZ2_VER),
    ("boltz2-ptm", "Boltz-2 (pTM)", "boltz2", "pTM", BZ2_VER),
    ("boltz2-iptm", "Boltz-2 (ipTM)", "boltz2", "ipTM", BZ2_VER),
    ("boltz2-minipae", "Boltz-2 (min-iPAE)", "boltz2", "min-iPAE", BZ2_VER),
    ("boltz2-affinity", "Boltz-2 (Affinity)", "boltz2", "affinity value from the affinity module", BZ2_VER),
    ("boltz2-probability", "Boltz-2 (Probability)", "boltz2", "binary binding probability from the affinity module", BZ2_VER),
    ("protenix-ranking", "Protenix (ranking score)", "protenix", "ranking score", PTX_VER),
    ("protenix-ptm", "Protenix (pTM)", "protenix", "pTM", PTX_VER),
    ("protenix-iptm", "Protenix (ipTM)", "protenix", "ipTM", PTX_VER),
]

SCORE_DEFS = {
    "pTM": "predicted template modeling score, estimating global structural accuracy",
    "ipTM": "interface predicted template modeling score, covering only inter-chain interactions",
    "ranking score": "a weighted sum of pTM, ipTM and further terms for clashes and disorder",
    "min-iPAE": "the minimum of all pairwise predicted aligned errors between protein tokens aligned by ligand tokens, computed from the output PAE matrix",
    "affinity value from the affinity module": "the regression output of Boltz-2's affinity prediction module",
    "binary binding probability from the affinity module": "the classification output of Boltz-2's affinity prediction module",
}

RESCORERS = [
    ("glide-sp", "Glide_SP", "Glide standard-precision score", f"{PREFIX}-method-glide", SCHRO, "conventional_pipeline"),
    ("glide-xp", "Glide_XP", "Glide extra-precision score", f"{PREFIX}-method-glide", SCHRO, "conventional_pipeline"),
    ("gnina-ad4", "Gnina (AD4)", "Gnina's classical AD4 scoring function with the minimize option", f"{PREFIX}-method-gnina", GNINA_VER, "conventional_pipeline"),
    ("gnina-vina", "Gnina (Vina)", "Gnina's classical Vina scoring function with the minimize option", f"{PREFIX}-method-gnina", GNINA_VER, "conventional_pipeline"),
    ("gnina-vinardo", "Gnina (Vinardo)", "Gnina's classical Vinardo scoring function with the minimize option", f"{PREFIX}-method-gnina", GNINA_VER, "conventional_pipeline"),
    ("gnina-cnnscore", "Gnina (CNNscore)", "Gnina's CNNscore convolutional neural network pose score", f"{PREFIX}-method-gnina", GNINA_VER, "supervised_machine_learning"),
    ("gnina-cnnaffinity", "Gnina (CNNaffinity)", "Gnina's CNNaffinity convolutional neural network affinity score", f"{PREFIX}-method-gnina", GNINA_VER, "supervised_machine_learning"),
    ("rtmscore", "RTMScore", "the RTMScore deep-learning score, which prioritises the structural reliability of the pose", None, None, "supervised_machine_learning"),
    ("planet", "PLANET", "the PLANET deep-learning score", None, None, "supervised_machine_learning"),
    ("pignet2", "PIGNet2", "the PIGNet2 deep-learning score", None, None, "supervised_machine_learning"),
    ("igmodel-pkd", "IGModel (pkd)", "IGModel's predicted binding affinity (pKd) output", None, None, "supervised_machine_learning"),
    ("igmodel-rmsd", "IGModel (rmsd)", "IGModel's predicted pose deviation (RMSD) output", None, None, "supervised_machine_learning"),
]

QUOTED_DEKOIS = [
    ("glide-sp", "Glide_SP", "ref. 38", "conventional_pipeline", f"{PREFIX}-method-glide"),
    ("gold-chemplp", "GOLD_CHEMPLP", "ref. 39", "conventional_pipeline", None),
    ("ledock", "LeDock", "ref. 39", "conventional_pipeline", None),
    ("surflex-dock", "Surflex-Dock", "ref. 38", "conventional_pipeline", None),
    ("tankbind", "TankBind", "ref. 34", "supervised_machine_learning", None),
    ("karmadock-aligned", "KarmaDock (Aligned)", "ref. 34", "supervised_machine_learning", None),
    ("carsidock", "CarsiDock", "ref. 35", "supervised_machine_learning", None),
    ("surfdock", "SurfDock", "ref. 36", "supervised_machine_learning", None),
]

SPEED_CONFIGS = [
    ("af3-5", "AF3", "af3", 5, AF3_VER),
    ("af3-1", "AF3", "af3", 1, AF3_VER.replace("five predictions", "one prediction")),
    ("protenix-5", "Protenix", "protenix", 5, PTX_VER),
    ("protenix-1", "Protenix", "protenix", 1, PTX_VER.replace("five predictions", "one prediction")),
    ("boltz2-default", "Boltz-2", "boltz2", 1, BZ2_VER),
    ("boltz2-no-affinity", "Boltz-2 (without affinity module)", "boltz2", 1, BZ2_VER + ", affinity module disabled"),
]


def cfg(
    key: str,
    name: str,
    description: str,
    reported_name: str,
    method_types: list[str],
    source: str,
    attrs: dict,
    parent: str | None = None,
) -> str:
    a = {
        "reported_name": reported_name,
        "configuration_type": "paper_evaluation",
        "foundation_model_eligible": False,
        "review": review(["transcription"], EXTRACT_NOTE, source),
    }
    a.update(attrs)
    links = [{"relation": "configuration_of", "target_id": parent}] if parent else []
    return rec(
        f"{PREFIX}-config-{key}",
        "configuration",
        name,
        description,
        "needs_review",
        [src_id(source)],
        a,
        links=links,
        facets={"areas": AREAS, "contexts": ["research"], "method_types": method_types},
    )


def build_configurations() -> None:
    for key, label, model, score, version in COFOLD_SCORES:
        parent = REUSED[model]
        is_affinity = "affinity module" in score
        cfg(
            key,
            f"{label} as a screening score",
            f"Ranks a compound library by {SCORE_DEFS[score]} taken from the predicted protein-ligand complex.",
            label,
            ["foundation_model"],
            "shen2025",
            {
                "version": version,
                "access_reuse": "Source code at https://github.com/google-deepmind/alphafold3, https://github.com/bytedance/Protenix and https://github.com/jwohlwend/boltz (Data availability); no licence is stated in the source",
                "parameters": "All parameters other than the sample count and seed left at default or recommended values",
                "foundation_model_eligible": True,
                "score_training_overlap": (
                    "The authors state that the Boltz-2 affinity module's training data, drawn from public binding "
                    "databases including PubChem, ChEMBL and BindingDB, may overlap substantially with the test "
                    "samples, so these results are reported for completeness and excluded from the authors' primary "
                    "comparison."
                )
                if is_affinity
                else "Not assessed for this score by the source beyond the ligand-similarity analysis of Figure 5 and Fig. S10",
                "source_locator": "Methods 'Complex structure prediction' and 'Scoring schemes'",
            },
            parent=parent,
        )
    for pose in ("af3", "protenix"):
        pose_label = "AF3" if pose == "af3" else "Protenix"
        for key, label, what, parent, version, mt in RESCORERS:
            attrs = {
                "parameters": "Implementation set to default or recommended values; binding pockets defined from the predicted ligand pose",
                "source_locator": "Methods 'Scoring schemes', 'Glide', 'Gnina', 'RTMScore, PIGNet2, PLANET and IGModel'",
                "selection": f"Applied to the top-ranked of the five predicted poses, selected by the {pose_label} ranking score",
            }
            if version:
                attrs["version"] = version
            else:
                attrs["missing_metadata"] = {"version": {"reason": "unreported", "note": "The source states only that the official repository's inference script was used"}}
                attrs["provenance_note"] = (
                    "No entity-level record was created for this scoring function: its primary paper was not "
                    "retrieved in this pass, so there is no source from which to describe it."
                )
            cfg(
                f"rescore-{key}-on-{pose}-poses",
                f"{label} rescoring of {pose_label} top-ranked poses",
                f"Ranks a compound library by {what} computed on the top-ranked {pose_label}-predicted protein-ligand complex.",
                label,
                [mt],
                "shen2025",
                attrs,
                parent=parent,
            )
    docking = [
        ("glide-sp", "Glide_SP", "Glide standard-precision docking score", f"{PREFIX}-method-glide", SCHRO, "conventional_pipeline"),
        ("gnina-vina", "Gnina (Vina)", "the Vina score of a Gnina docking pose", f"{PREFIX}-method-gnina", GNINA_VER, "conventional_pipeline"),
        ("gnina-cnnscore", "Gnina (CNNscore)", "the CNNscore of a Gnina docking pose", f"{PREFIX}-method-gnina", GNINA_VER, "supervised_machine_learning"),
        ("gnina-cnnaffinity", "Gnina (CNNaffinity)", "the CNNaffinity score of a Gnina docking pose", f"{PREFIX}-method-gnina", GNINA_VER, "supervised_machine_learning"),
    ]
    for key, label, what, parent, version, mt in docking:
        cfg(
            f"dock-{key}",
            f"{label} docking baseline",
            f"Docks a compound into the prepared receptor and ranks the library by {what}.",
            label,
            [mt],
            "shen2025",
            {
                "version": version,
                "parameters": "Binding box defined from the crystallised ligand; remaining parameters at default settings",
                "source_locator": "Methods 'Baseline docking results'",
            },
            parent=parent,
        )
    for key, label, ref, mt, parent in QUOTED_DEKOIS:
        cfg(
            f"quoted-{key}-dekois",
            f"{label} on DEKOIS 2.0, values quoted by Shen et al. 2025",
            f"Docks a compound into the receptor and ranks the library by the {label} score.",
            label,
            [mt],
            "shen2025",
            {
                "missing_metadata": {"version": {"reason": "unreported", "note": f"Shen et al. 2025 quote these values from {ref} without stating the tool version"}},
                "provenance_note": (
                    f"Shen et al. 2025 quote this row's DEKOIS 2.0 values from {ref} rather than running the tool; "
                    "that reference was not resolved to a primary artifact in this pass, so no entity-level record "
                    "was created for the tool and no evaluation of it is independent of this compilation."
                ),
                "source_locator": f"Table 1, row '{label}' and its footnote",
            },
            parent=parent,
        )
    for key, label, model, samples, version in SPEED_CONFIGS:
        cfg(
            f"speed-{key}",
            f"{label}, {samples} sample{'s' if samples > 1 else ''}, timed per compound",
            f"Predicts a protein-ligand complex from sequence and SMILES, producing {samples} sample{'s' if samples > 1 else ''} per pair.",
            label,
            ["foundation_model"],
            "shen2025",
            {
                "version": version,
                "samples": samples,
                "foundation_model_eligible": True,
                "hardware": {"accelerator": "NVIDIA H100", "memory": "80 GB", "count": 1},
                "parameters": "Pre-computed MSAs and ligand SMILES as input; all other parameters at default or recommended values",
                "source_locator": "Table 5 caption; Results 'Assessment of computational efficiency'",
            },
            parent=REUSED[model],
        )
    kim_cfgs = [
        ("kim-dock37", "DOCK3.7", "DOCK3.7 energy", f"{PREFIX}-method-dock37", "conventional_pipeline",
         "Ranks a compound library by the DOCK3.7 energy of the docked pose, the sum of receptor-ligand electrostatic and van der Waals energies corrected for context-dependent ligand desolvation."),
        ("kim-af3-lplddt", "AF3 L-pLDDT", REUSED["af3"], REUSED["af3"], "foundation_model",
         "Ranks a compound library by a ligand-centric pLDDT, the arithmetic mean of AlphaFold3 pLDDT over the ligand atoms of the predicted complex."),
        ("kim-boltz2-pic50", "Boltz-2 pIC50", REUSED["boltz2"], REUSED["boltz2"], "foundation_model",
         "Ranks a compound library by the pIC50 that Boltz-2's affinity module predicts for the protein-ligand pair."),
    ]
    for key, label, _unused, parent, mt, description in kim_cfgs:
        cfg(
            key,
            f"{label} (Kim, Correy, Hall et al. 2026 hit-list re-ranking)",
            description,
            label,
            [mt],
            "kim2026",
            {
                "missing_metadata": {"version": {"reason": "unreported", "note": "The source cites the tool's repository but states no version or release for it"}},
                "access_reuse": "Repositories named in Methods 'Co-folding'; input and analysis scripts at https://github.com/jongbin99/cofold-em",
                "hardware": {"accelerator": "NVIDIA A40 GPUs"} if mt == "foundation_model" else {},
                "score_training_overlap": (
                    "Training cutoffs stated for the Mac1 arm: Chai-1 entries deposited before 2021-12-01, "
                    "AlphaFold3 before 2021-09-30, Boltz-2 2023-06-01. No training-overlap control is stated for the "
                    "three docking hit lists."
                ),
                "source_locator": "Methods 'Co-folding'; Methods 'Molecular docking of Mac1 compounds'",
                "foundation_model_eligible": mt == "foundation_model",
            },
            parent=parent,
        )


# --------------------------------------------------------------------------------------
# Protocols
# --------------------------------------------------------------------------------------

RATIO_LIMIT = (
    "Enrichment factors depend on the actives-to-inactives ratio and on how the negatives were built, which differ "
    "by more than an order of magnitude between the benchmarks in this store (1:30 for DEKOIS 2.0, 1:50 for "
    "GPCRrecent, and from about 1:43 to about 1:200 across the five LIT-PCBA targets scored here, reaching about "
    "1:18000 for LIT-PCBA ADRB2). Values from different protocols are not comparable."
)
SHEN_METRICS = (
    "AUROC, BEDROC with alpha = 80.5 (the top 2% of the ranked list contributes 80% of the score), and enrichment "
    "factors at 0.5%, 1% and 5%, each reported as the mean and the median over targets. EFx% is the ratio of true "
    "positives found in the top x% of the ranked compounds relative to random selection."
)


def protocol(pid: str, name: str, description: str, source: str, attrs: dict, links: list[dict]) -> str:
    a = {
        "task": "Protein-ligand virtual screening (library ranking)",
        "publication_status": "peer_reviewed",
        "review": review(["transcription"], EXTRACT_NOTE, source),
    }
    a.update(attrs)
    return rec(f"{PREFIX}-protocol-{pid}", "protocol", name, description, "needs_review", [src_id(source)], a, links=links)


def build_protocols() -> None:
    task_link = {"relation": "evaluates_task", "target_id": REUSED["task"]}
    protocol(
        "shen-dekois-builtin",
        "DEKOIS 2.0 screening with co-folding confidence scores against docking tools (Shen et al. 2025 Table 1)",
        "Rank each DEKOIS 2.0 target's 40 actives and 1200 property-matched decoys with a co-folding model's built-in confidence score or with a docking tool, and report AUROC, BEDROC and enrichment factors averaged over targets.",
        "shen2025",
        {
            "metric": "enrichment-factor",
            "metric_direction": "higher",
            "unit": "unitless",
            "metric_qualifier": "mean and median over the DEKOIS 2.0 targets",
            "metric_definition": SHEN_METRICS,
            "protocol": "Co-folding from protein sequence and ligand SMILES with pre-computed MSAs, then ranking by the model's own confidence score; docking tools rank the same compounds for the same targets.",
            "denominator": 79,
            "version": "Shen et al. 2025, Table 1",
            "source_locator": "Table 1 and its footnotes a to f",
            "selection_bias": "The quoted baseline rows were produced by other groups under their own protocols; only the co-folding rows and the three Gnina rows were run by these authors.",
            "limitations": [
                RATIO_LIMIT,
                "The decoys are property-matched synthetic molecules, not assayed inactives.",
                "Eight of the 24 rows are quoted from other papers (footnotes b to f: refs 34, 35, 36, 38 and 39), so they were not run under one common pipeline; none of those references was retrieved in this pass.",
                "The SurfDock row's indicators were calculated on all 81 targets rather than the 79 used elsewhere in the table, because the per-target labels were unavailable (footnote f).",
                "The authors warn that the Boltz-2 Affinity and Probability rows are likely to be significantly over-estimated because Boltz-2 fetched affinity data from the public databases that also source DEKOIS 2.0, and they exclude those two rows from their own primary comparison (footnote a and Methods 'Affinity score and probability').",
                "DEKOIS 2.0 was released over ten years before this evaluation and its template protein structures may overlap the co-folding models' training data; the ligand-similarity analysis of Figure 5 is the authors' partial control and was not extracted.",
            ],
            "scope_note": "Retrospective: the method ranks a curated set of actives and negatives that were assembled before the evaluation, not compounds selected and then tested.",
        },
        [task_link, {"relation": "uses_data", "target_id": f"{PREFIX}-dataset-dekois2-79"},
         {"relation": "part_of", "target_id": f"{PREFIX}-benchmark-dekois2"}],
    )
    for pose, pose_label, n in (("protenix", "Protenix", 13), ("af3", "AF3", 10)):
        protocol(
            f"shen-dekois-rescore-{pose}",
            f"DEKOIS 2.0 screening by rescoring {pose_label}-predicted complexes (Shen et al. 2025 Table 2, {pose_label} block)",
            f"Rank each DEKOIS 2.0 target's 40 actives and 1200 property-matched decoys by rescoring the top-ranked of five {pose_label}-predicted complexes, and report AUROC, BEDROC and enrichment factors averaged over targets.",
            "shen2025",
            {
                "metric": "enrichment-factor",
                "metric_direction": "higher",
                "unit": "unitless",
                "metric_qualifier": "mean and median over the DEKOIS 2.0 targets",
                "metric_definition": SHEN_METRICS,
                "protocol": (
                    f"Five complexes predicted per protein-ligand pair with {pose_label}; the pose ranked first by the "
                    f"{pose_label} ranking score is kept, prepared with the Protein Preparation Wizard, and rescored. "
                    "A structure that remained unrecognisable was given an extremely low score."
                ),
                "denominator": 79,
                "version": f"Shen et al. 2025, Table 2, {pose_label} block",
                "source_locator": f"Table 2, {pose_label} block",
                "limitations": [
                    RATIO_LIMIT,
                    "The decoys are property-matched synthetic molecules, not assayed inactives.",
                    f"The {pose_label} ipTM row (and, for AF3, Min-iPAE) repeats the value printed in Table 1 for the same configuration; it is the co-folding score rather than a rescoring arm, and is kept here because it is a printed cell of this table.",
                    "Structures that could not be processed were assigned an extremely low score rather than excluded, which affects every rescoring row.",
                ],
                "scope_note": "Retrospective: the method ranks a curated set of actives and negatives that were assembled before the evaluation, not compounds selected and then tested.",
            },
            [task_link, {"relation": "uses_data", "target_id": f"{PREFIX}-dataset-dekois2-79"},
             {"relation": "part_of", "target_id": f"{PREFIX}-benchmark-dekois2"}],
        )
    for pid, label, data, denom, extra in (
        ("shen-gpcrrecent-16", "16 GPCR targets", f"{PREFIX}-dataset-gpcrrecent-16", 16, []),
        ("shen-gpcrrecent-6", "the six targets whose first structures postdate the Boltz-2 training cutoff",
         f"{PREFIX}-dataset-gpcrrecent-6", 6,
         ["Only the two Boltz-2 rows marked 'subset' in Table 3 were computed on these six targets; the other rows in the table cover all 16."]),
    ):
        protocol(
            pid,
            f"GPCRrecent screening ({label}) (Shen et al. 2025 Table 3)",
            f"Rank the actives and TocoDecoy-generated decoys of {label} in the GPCRrecent set with a co-folding confidence score, a rescoring function or a docking baseline, and report AUROC, BEDROC and enrichment factors averaged over targets.",
            "shen2025",
            {
                "metric": "enrichment-factor",
                "metric_direction": "higher",
                "unit": "unitless",
                "metric_qualifier": "mean and median over the GPCRrecent targets",
                "metric_definition": SHEN_METRICS,
                "protocol": "Receptor structures retrieved from the PDB and prepared with the Protein Preparation Wizard; ligands prepared with LigPrep; co-folding, rescoring and docking all applied to the same compounds.",
                "denominator": denom,
                "version": "Shen et al. 2025, Table 3",
                "source_locator": "Table 3" + (" (rows marked 'subset' and footnote a)" if denom == 6 else ""),
                "control": "Targets whose first crystal structure was released after 2022, chosen so that the structural inputs postdate the co-folding models' training data.",
                "limitations": [
                    RATIO_LIMIT,
                    "The decoys are generated by a conditional recurrent neural network (TocoDecoy) at 1:50, not assayed inactives.",
                    "The temporal control covers crystal structures only. The authors exclude Boltz-2's affinity module from this analysis because its binding-data training sources overlap the benchmark, and say the set cannot reflect the generalisation of affinity predictors.",
                    "AF3 was not run on this set; Protenix and Boltz-2 were used as representatives because of their lower memory requirements.",
                ]
                + extra,
                "scope_note": "Retrospective: the method ranks a curated set of actives and negatives that were assembled before the evaluation, not compounds selected and then tested.",
            },
            [task_link, {"relation": "uses_data", "target_id": data},
             {"relation": "part_of", "target_id": f"{PREFIX}-benchmark-gpcrrecent"}],
        )
    protocol(
        "shen-litpcba5",
        "LIT-PCBA five-target screening (Shen et al. 2025 Table 4)",
        "Rank the experimentally measured actives and inactives of five LIT-PCBA targets with a co-folding confidence score or a docking baseline, and report the enrichment factor and the normalised enrichment factor at 1% per target and averaged.",
        "shen2025",
        {
            "metric": "enrichment-factor",
            "metric_direction": "higher",
            "unit": "unitless",
            "metric_qualifier": "EF at the top 1% of the ranked library, per target and averaged over the five targets",
            "metric_definition": (
                "EF1% is the ratio of true positives found in the top 1% of the ranked compounds relative to random "
                "selection. NEF1% is the observed EF1% divided by its theoretical maximum at that threshold, which "
                "confines it to [0, 1] and corrects for the different actives-to-inactives ratios between targets "
                "(Table 4 footnote a)."
            ),
            "protocol": "One structure selected from the recommended PDB entries per target for docking; ligands prepared with LigPrep; co-folding, Glide and Gnina applied to the same compounds.",
            "denominator": 5,
            "version": "Shen et al. 2025, Table 4",
            "source_locator": "Table 4 and footnote a",
            "control": "The actives and inactives are both experimentally measured, so the negatives are assayed rather than synthetic.",
            "limitations": [
                RATIO_LIMIT,
                "Huang, Knight and Naprienko 2025 audit LIT-PCBA and conclude that analogue and 2D-identical-compound leakage between its splits lets a parameter-free memorisation baseline match or exceed published results, that nearly all published LIT-PCBA results are undermined, and that the benchmark does not measure recovery of novel chemotypes. That bears on every value from this protocol.",
                "Five of the 15 LIT-PCBA targets were screened, chosen for size; MTORC1 meets the size criterion but was excluded for ambiguous binding sites, which is a selection the authors made rather than a property of the benchmark.",
                "Only EF1% and NEF1% are printed for this table; no AUROC or BEDROC column is given.",
                "AF3 was not run on this set.",
            ],
            "scope_note": "Retrospective: the method ranks a curated set of actives and negatives that were assembled before the evaluation, not compounds selected and then tested.",
        },
        [task_link, {"relation": "uses_data", "target_id": f"{PREFIX}-dataset-litpcba-5"},
         {"relation": "part_of", "target_id": f"{PREFIX}-benchmark-litpcba"}],
    )
    protocol(
        "shen-speed",
        "Co-folding time per compound on five DEKOIS 2.0 targets (Shen et al. 2025 Table 5)",
        "Measure the average wall-clock time per compound to co-fold a protein-ligand pair on one NVIDIA H100, for five DEKOIS 2.0 targets with 400 decoys each.",
        "shen2025",
        {
            "metric": "runtime",
            "metric_direction": "lower",
            "unit": "second",
            "unit_detail": "seconds per compound, the total time for a target averaged over its compounds",
            "metric_definition": "The overall computational efficiency calculated by averaging the total time per compound, with pre-computed MSAs and ligand SMILES as input.",
            "protocol": "Five representative DEKOIS 2.0 targets, each with 400 randomly selected decoys, run on a single NVIDIA H100 with 80 GB of memory.",
            "denominator": 5,
            "version": "Shen et al. 2025, Table 5",
            "source_locator": "Table 5 and its caption",
            "limitations": [
                "MSA construction is excluded: pre-computed MSAs were fed as input, so the figures are inference time only.",
                "The authors note that runtimes vary substantially across targets with token length and other factors, so the average over five targets is not a per-compound cost for an arbitrary target.",
                "No docking tool was timed, so this table does not compare co-folding cost with docking cost.",
                "Timings are single measurements; no repeats or uncertainty are reported.",
            ],
            "scope_note": "Retrospective: the method ranks a curated set of actives and negatives that were assembled before the evaluation, not compounds selected and then tested.",
        },
        [task_link, {"relation": "uses_data", "target_id": f"{PREFIX}-dataset-dekois2-speed5"}],
    )
    for key, meta in KIM_SETS.items():
        protocol(
            f"kim-{key}",
            f"Re-ranking the {meta['name'].split(',')[0]} by co-folding and docking scores (Kim, Correy, Hall et al. 2026)",
            f"Rank the compounds of a tested ultra-large docking hit list by DOCK3.7 energy, AlphaFold3 L-pLDDT or Boltz-2 pIC50, and report the area under the ROC curve for separating measured binders from high-ranking docking false positives.",
            "kim2026",
            {
                "metric": "auroc",
                "metric_direction": "higher",
                "unit": "unitless",
                "unit_detail": "printed as a percentage on a 0-100 scale",
                "metric_qualifier": "discrimination of measured binders from high-ranking docking false positives in a tested hit list",
                "metric_definition": "Area under the receiver operating characteristic curve for separating true hits from non-binders, printed in the body text as a percentage.",
                "protocol": (
                    "Every compound in the list was synthesised and assayed in the original screening campaign. The "
                    "three scores are then computed for those same compounds and their ranking compared; the "
                    "comparison itself is a retrospective re-ranking of a prospectively tested set."
                ),
                "denominator": meta["positives"] + meta["negatives"],
                "version": "Kim, Correy, Hall et al. 2026, Results 'Co-folding struggles to reliably re-rank docking hit lists'",
                "source_locator": meta["locator"],
                "control": "DOCK3.7, the engine that produced the hit list, is scored on the same compounds.",
                "limitations": [
                    "The negatives are compounds a docking screen already ranked highly, which is a far harder and more realistic negative set than property-matched decoys; these AUC values are not comparable with enrichment on decoy benchmarks.",
                    "The list is a biased sample of the library: only high-ranking docked molecules were synthesised, so neither the AUC nor any hit rate derived from it estimates performance over a whole library.",
                    "No training-overlap control is stated for this arm. Training cutoffs are given for the separate Mac1 pose benchmark, and Supplementary file 2 reports pairwise similarity between the datasets, but neither was extracted here.",
                    "The hit-rate curves, the semi-logarithmic ROC curves and the early-enrichment values for these sets are published only as figures (Figure 5 and its supplements 3 and 4) and were not read.",
                    "Only three scores were compared on these sets: DOCK3.7 energy, AF3 L-pLDDT and Boltz-2 pIC50. Chai-1 was used on the Mac1 pose arm only.",
                ],
                "scope_note": "Retrospective: the method ranks a curated set of actives and negatives that were assembled before the evaluation, not compounds selected and then tested.",
            },
            [task_link, {"relation": "uses_data", "target_id": f"{PREFIX}-dataset-kim-{key}"}],
        )
    protocol(
        "cache3-own-selection",
        "CACHE #3 Round 1 own-selection outcome per workflow (Herasymenko et al. 2026 Table S8)",
        "Count the compounds each CACHE #3 workflow selected for synthesis and the confirmed hits among them, and score those hits for activity and chemical novelty.",
        "cache3_si002",
        {
            "metric": "count",
            "metric_direction": "higher",
            "unit": "count",
            "unit_detail": "compounds",
            "metric_qualifier": "compounds selected by one workflow and the confirmed hits among them",
            "metric_definition": (
                "Compounds tested is the number a workflow selected that Enamine synthesised and the organisers "
                "assayed. Hits are the experimentally confirmed actives among them. Chemically Novel Hits are those "
                "the Hit Evaluation Committee judged novel. The activity score reflects the quality and consistency "
                "of the binding signals and the chemical soundness of the molecule, including absence of undesirable "
                "groups; the novelty score runs from 0 (not novel) to 3 (unanimously voted as novel) across three "
                "independent chemists."
            ),
            "protocol": (
                "Blinded and prospective: each team selected up to 100 commercially available compounds before any "
                "testing. All 1739 selected compounds were screened by HTRF at 100 uM, then by a three-point dose "
                "response, then by surface plasmon resonance, and in parallel by crystal soaking."
            ),
            "denominator": 1739,
            "version": "Herasymenko et al. 2026, Supporting Information table S8",
            "source_locator": "Sheet 'S8' of ci5c02441_si_002.xlsx; scoring described in the article's Results and Figure 6 caption",
            "limitations": [
                "Each workflow selected its own compounds, so the workflows are not compared on a common library in this arm. The merged-library arm is the comparison on one library.",
                "The source prints no per-workflow hit rate. Compounds tested and Hits are printed separately; this batch records both counts and does not divide them, because the article defines its hit rate as confirmed actives divided by compounds predicted active, which is the merged-library denominator rather than this one.",
                "Workflow numbers of compounds tested range from 41 to 99, so the counts rest on small and unequal denominators.",
                "The activity and novelty scores are committee judgements, not measurements, and the per-compound scoring matrix (sheet S7) was not extracted.",
                "Participants are named for only 10 of the 23 workflows in this sheet; the rest are anonymous.",
            ],
            "scope_note": "Prospective: predictions were submitted before any compound was synthesised or assayed.",
        },
        [task_link, {"relation": "uses_data", "target_id": f"{PREFIX}-dataset-cache3-round1"},
         {"relation": "part_of", "target_id": f"{PREFIX}-benchmark-cache3"}],
    )
    protocol(
        "cache3-merged-library",
        "CACHE #3 merged Round 1 library prediction per workflow (Herasymenko et al. 2026 Table S8)",
        "Have every CACHE #3 workflow predict which of the same 1739 Round 1 compounds are active, and count the confirmed Tier 1 and Tier 2 hits among each workflow's predicted actives.",
        "cache3_si002",
        {
            "metric": "count",
            "metric_direction": "higher",
            "unit": "count",
            "unit_detail": "compounds",
            "metric_qualifier": "confirmed hits among one workflow's predicted actives on the merged 1739-compound library",
            "metric_definition": (
                "Every workflow was applied to the merged library of all 1739 Round 1 compounds. Confirmed hits with "
                "a score above 15 were clustered into four chemically novel Tier 1 compounds and 25 Tier 2 "
                "compounds. The normalised columns are, in the article's words, 'the aggregated score of all "
                "compounds predicted active divided by the number of compounds predicted to be actives'."
            ),
            "protocol": "Complementary evaluation scheme in which all computational workflows are applied to the same chemical library, so that selection of the library does not differ between them.",
            "denominator": 1739,
            "version": "Herasymenko et al. 2026, Supporting Information table S8",
            "source_locator": "Sheet 'S8' of ci5c02441_si_002.xlsx, merged-library columns; Figure 6 caption",
            "limitations": [
                "The library is the union of what the 23 workflows themselves selected, so it is not an independent library and each workflow's own picks are in it.",
                "Four of the 23 workflows (1694, 1695, 1716, 1717) have no values printed in these columns; they are recorded as absent, not as zero.",
                "Only 29 confirmed hits scored above 15, four of them chemically novel, so the Tier 1 counts rest on four compounds in total.",
                "The two normalised columns are labelled as counts of hits but the Figure 6 caption defines them as an aggregated score divided by the number of compounds predicted active; the label and the definition do not agree, and the sheet's final column has no printed header at all.",
                "Predicting the merged library is not the same task as selecting compounds to synthesise, and the counts here are not hit rates.",
            ],
            "scope_note": "Prospective: predictions were submitted before any compound was synthesised or assayed.",
        },
        [task_link, {"relation": "uses_data", "target_id": f"{PREFIX}-dataset-cache3-round1"},
         {"relation": "part_of", "target_id": f"{PREFIX}-benchmark-cache3"}],
    )



# --------------------------------------------------------------------------------------
# Shen et al. 2025: evaluations and results
# --------------------------------------------------------------------------------------

COLS_10 = [
    ("auroc", "AUROC", "Mean"),
    ("auroc", "AUROC", "Med"),
    ("bedroc", "BEDROC (α = 80.5)", "Mean"),
    ("bedroc", "BEDROC (α = 80.5)", "Med"),
    ("enrichment-factor", "EF0.5%", "Mean"),
    ("enrichment-factor", "EF0.5%", "Med"),
    ("enrichment-factor", "EF1%", "Mean"),
    ("enrichment-factor", "EF1%", "Med"),
    ("enrichment-factor", "EF5%", "Mean"),
    ("enrichment-factor", "EF5%", "Med"),
]

T1_ROWS = [
    ("AF3 (ranking score)", "af3-ranking", "author_reported", None),
    ("AF3 (pTM)", "af3-ptm", "author_reported", None),
    ("AF3 (ipTM)", "af3-iptm", "author_reported", None),
    ("AF3 (min-iPAE)", "af3-minipae", "author_reported", None),
    ("Boltz-2 (ranking score)", "boltz2-ranking", "author_reported", None),
    ("Boltz-2 (pTM)", "boltz2-ptm", "author_reported", None),
    ("Boltz-2 (ipTM)", "boltz2-iptm", "author_reported", None),
    ("Boltz-2 (min-iPAE)", "boltz2-minipae", "author_reported", None),
    ("Boltz-2 (Affinity)a", "boltz2-affinity", "author_reported", "footnote a"),
    ("Boltz-2 (Probability)a", "boltz2-probability", "author_reported", "footnote a"),
    ("Protenix (ranking score)", "protenix-ranking", "author_reported", None),
    ("Protenix (pTM)", "protenix-ptm", "author_reported", None),
    ("Protenix (ipTM)", "protenix-iptm", "author_reported", None),
    ("Glide_SPb", "quoted-glide-sp-dekois", "paper_compilation", "footnote b (ref. 38)"),
    ("GOLD_CHEMPLPc", "quoted-gold-chemplp-dekois", "paper_compilation", "footnote c (ref. 39)"),
    ("LeDockc", "quoted-ledock-dekois", "paper_compilation", "footnote c (ref. 39)"),
    ("Surflex-Dockb", "quoted-surflex-dock-dekois", "paper_compilation", "footnote b (ref. 38)"),
    ("Gnina (Vina)", "dock-gnina-vina", "author_reported", None),
    ("Gnina (CNNscore)", "dock-gnina-cnnscore", "author_reported", None),
    ("Gnina (CNNaffinity)", "dock-gnina-cnnaffinity", "author_reported", None),
    ("TankBindd", "quoted-tankbind-dekois", "paper_compilation", "footnote d (ref. 34)"),
    ("KarmaDock (Aligned)d", "quoted-karmadock-aligned-dekois", "paper_compilation", "footnote d (ref. 34)"),
    ("CarsiDocke", "quoted-carsidock-dekois", "paper_compilation", "footnote e (ref. 35)"),
    ("SurfDockf", "quoted-surfdock-dekois", "paper_compilation", "footnote f (ref. 36), 81 targets"),
]

T2_PROTENIX_ROWS = [
    ("ipTM", "protenix-iptm"),
    ("Glide_SP", "rescore-glide-sp-on-protenix-poses"),
    ("Glide_XP", "rescore-glide-xp-on-protenix-poses"),
    ("Gnina (AD4)", "rescore-gnina-ad4-on-protenix-poses"),
    ("Gnina (Vina)", "rescore-gnina-vina-on-protenix-poses"),
    ("Gnina (Vinardo)", "rescore-gnina-vinardo-on-protenix-poses"),
    ("Gnina (CNNscore)", "rescore-gnina-cnnscore-on-protenix-poses"),
    ("Gnina (CNNaffinity)", "rescore-gnina-cnnaffinity-on-protenix-poses"),
    ("RTMScore", "rescore-rtmscore-on-protenix-poses"),
    ("PLANET", "rescore-planet-on-protenix-poses"),
    ("PIGNet2", "rescore-pignet2-on-protenix-poses"),
    ("IGModel (pkd)", "rescore-igmodel-pkd-on-protenix-poses"),
    ("IGModel (rmsd)", "rescore-igmodel-rmsd-on-protenix-poses"),
]

T2_AF3_ROWS = [
    ("ipTM", "af3-iptm"),
    ("Min-iPAE", "af3-minipae"),
    ("Glide_SP", "rescore-glide-sp-on-af3-poses"),
    ("Glide_XP", "rescore-glide-xp-on-af3-poses"),
    ("Gnina (AD4)", "rescore-gnina-ad4-on-af3-poses"),
    ("Gnina (Vina)", "rescore-gnina-vina-on-af3-poses"),
    ("Gnina (Vinardo)", "rescore-gnina-vinardo-on-af3-poses"),
    ("Gnina (CNNscore)", "rescore-gnina-cnnscore-on-af3-poses"),
    ("Gnina (CNNaffinity)", "rescore-gnina-cnnaffinity-on-af3-poses"),
    ("RTMScore", "rescore-rtmscore-on-af3-poses"),
]

T3_ROWS = [
    ("Boltz-2 (ipTM)", "boltz2-iptm", 16),
    ("Boltz-2 (min-iPAE)", "boltz2-minipae", 16),
    ("Boltz-2 (ipTM) subseta", "boltz2-iptm", 6),
    ("Boltz-2 (min-iPAE) subseta", "boltz2-minipae", 6),
    ("Protenix (ipTM)", "protenix-iptm", 16),
    ("Protenix (Glide_SP)", "rescore-glide-sp-on-protenix-poses", 16),
    ("Protenix (Glide_XP)", "rescore-glide-xp-on-protenix-poses", 16),
    ("Protenix (AD4)", "rescore-gnina-ad4-on-protenix-poses", 16),
    ("Protenix (Vina)", "rescore-gnina-vina-on-protenix-poses", 16),
    ("Protenix (CNNscore)", "rescore-gnina-cnnscore-on-protenix-poses", 16),
    ("Protenix (CNNaffinity)", "rescore-gnina-cnnaffinity-on-protenix-poses", 16),
    ("Protenix (RTMScore)", "rescore-rtmscore-on-protenix-poses", 16),
    ("Glide_SP", "dock-glide-sp", 16),
    ("Gnina (Vina)", "dock-gnina-vina", 16),
    ("Gnina (CNNscore)", "dock-gnina-cnnscore", 16),
    ("Gnina (CNNaffinity)", "dock-gnina-cnnaffinity", 16),
]

T4_ROWS = [
    ("Boltz-2 (ipTM)", "boltz2-iptm"),
    ("Boltz-2 (min-iPAE)", "boltz2-minipae"),
    ("Protenix (ipTM)", "protenix-iptm"),
    ("Glide_SP", "dock-glide-sp"),
    ("Gnina (Vina)", "dock-gnina-vina"),
    ("Gnina (CNNscore)", "dock-gnina-cnnscore"),
    ("Gnina (CNNaffinity)", "dock-gnina-cnnaffinity"),
]

T4_COLS = [
    ("ESR_ago", "EF1%"),
    ("ESR_ago", "NEF1%a"),
    ("ESR_antago", "EF1%"),
    ("ESR_antago", "NEF1%"),
    ("PPARG", "EF1%"),
    ("PPARG", "NEF1%"),
    ("TP53", "EF1%"),
    ("TP53", "NEF1%"),
    ("MAPK1", "EF1%"),
    ("MAPK1", "NEF1%"),
    ("Average", "EF1%"),
    ("Average", "NEF1%"),
]

T5_ROWS = [
    ("AF3", "5", "speed-af3-5"),
    (None, "1", "speed-af3-1"),
    ("Protenix", "5", "speed-protenix-5"),
    (None, "1", "speed-protenix-1"),
    ("Boltz-2", "1", "speed-boltz2-default"),
    ("Boltz-2 (without affinity module)", "1", "speed-boltz2-no-affinity"),
]
T5_COLS = ["a2a", "ar", "cdk2", "ctsk", "hdac2", "Average"]


def agg_word(short: str) -> str:
    return {"Mean": "mean", "Med": "median"}[short]


def qualifier_10(metric: str, column: str, agg: str, scope: str) -> str:
    over = f"{agg_word(agg)} over {scope}"
    if metric == "auroc":
        return f"AUROC, {over}"
    if metric == "bedroc":
        return f"BEDROC with alpha = 80.5, {over}"
    frac = column.replace("EF", "")
    return f"EF at the top {frac} of the ranked library, {over}"


def eval_record(
    eid: str,
    name: str,
    config: str,
    protocol_id: str,
    data: str,
    origin: str,
    source: str,
    comparison: dict,
    locator: str,
    extra: dict | None = None,
) -> str:
    attrs = {
        "origin": origin,
        "protocol": protocol_id,
        "comparison": comparison,
        "source_locator": locator,
        "review": review(["deterministic-table-parse"], EXTRACT_NOTE, source),
    }
    if extra:
        attrs.update(extra)
    return rec(
        eid,
        "evaluation",
        name,
        "Published result; transcribed, not reproduced.",
        "needs_review",
        [src_id(source)],
        attrs,
        links=[
            {"relation": "system", "target_id": config},
            {"relation": "assessment", "target_id": protocol_id},
            {"relation": "data", "target_id": data},
        ],
    )


def result_record(
    rid: str,
    name: str,
    evaluation: str,
    metric: str,
    direction: str,
    unit: str,
    printed: str,
    numeric: str | None,
    qualifier: str,
    locator: str,
    source: str,
    extra: dict | None = None,
) -> str:
    attrs = {
        "metric": metric,
        "metric_direction": direction,
        "unit": unit,
        "metric_qualifier": qualifier,
        "printed_value": printed,
        "numeric_value": numeric,
        "source_locator": locator,
        "missing_metadata": {"uncertainty": {"reason": "unreported", "note": "The source prints no interval or spread for this value"}},
        "review": review(["deterministic-table-parse"], EXTRACT_NOTE, source),
    }
    if extra:
        attrs.update(extra)
        if "uncertainty" in extra:
            attrs.pop("missing_metadata", None)
    out = rec(rid, "result", name, "Reported value transcribed from the pinned source. Not independently reproduced.", "needs_review", [src_id(source)], attrs, links=[{"relation": "evaluation", "target_id": evaluation}], facets={})
    claim_row(out, src_id(source), locator, printed, "value, numeric value, locator, metric, qualifier, unit, direction")
    return out


def numeric_rows(table: dict, expect_header: list[str]) -> list[list[str]]:
    rows = [[c[0] for c in r] for r in table["rows"]]
    header_hits = [r for r in rows if r and r[0] == expect_header[0]]
    if not header_hits:
        raise SystemExit(f"header row starting {expect_header[0]!r} not found")
    return rows


def build_shen(xml: bytes) -> None:
    tables = pmc_tables(xml)
    for want in ("Table 1", "Table 2", "Table 3", "Table 4", "Table 5"):
        if want not in tables:
            raise SystemExit(f"Shen et al.: {want} not found in the pinned XML")

    def cells(table_label: str) -> list[list[str]]:
        return [[c[0] for c in r] for r in tables[table_label]["rows"]]

    # --- assert the shared column header of Tables 1-3
    for label in ("Table 1", "Table 2", "Table 3"):
        rows = cells(label)
        if rows[0][0] != "Method" or [c for c in rows[0][1:]] != [c[1] for c in COLS_10[::2]]:
            raise SystemExit(f"{label}: unexpected column header {rows[0]!r}")
        if rows[1] != ["Mean", "Med"] * 5:
            raise SystemExit(f"{label}: unexpected sub-header {rows[1]!r}")

    base_comparison = {
        "dataset_version": "DEKOIS 2.0 as distributed at http://www.dekois.com",
        "split": "All 79 evaluated targets; no training or test split applies",
        "population": "79 targets, 40 actives and 1200 property-matched decoys each (1:30)",
        "inputs": "Protein sequence and ligand SMILES with pre-computed MSAs",
        "adaptation": "None; pretrained models and default or recommended settings",
        "metric_implementation": SHEN_METRICS,
        "aggregation": "Mean and median of the per-target metric over the targets",
        "budget": None,
    }

    # ---- Table 1
    rows = cells("Table 1")[2:]
    if len(rows) != len(T1_ROWS):
        raise SystemExit(f"Table 1: {len(rows)} data rows, expected {len(T1_ROWS)}")
    pid = f"{PREFIX}-protocol-shen-dekois-builtin"
    for row, (label, ckey, origin, note) in zip(rows, T1_ROWS):
        if row[0] != label:
            raise SystemExit(f"Table 1: row label {row[0]!r}, expected {label!r}")
        if len(row) != 11:
            raise SystemExit(f"Table 1 row {label!r}: {len(row)} cells, expected 11")
        comparison = dict(base_comparison)
        comparison["protocol_id"] = pid
        if ckey == "quoted-surfdock-dekois":
            comparison["population"] = "81 targets: the indicators were calculated on all 81 targets because the per-target labels were unavailable (footnote f)"
            comparison["split"] = "All 81 DEKOIS 2.0 targets"
        eid = f"{PREFIX}-eval-dekois-builtin-{ckey}"
        extra = {"missing_metadata": {"comparison.budget": {"reason": "unreported", "note": "No compute budget is stated for this table"}}, "retrospective": True}
        if origin == "paper_compilation":
            extra["reference"] = f"Values quoted by Shen et al. 2025 from {note}; the original paper was not retrieved in this pass."
        eval_record(
            eid,
            f"{label.rstrip('abcdef')} on DEKOIS 2.0 (Shen et al. 2025 Table 1)",
            f"{PREFIX}-config-{ckey}",
            pid,
            f"{PREFIX}-dataset-dekois2-79",
            origin,
            "shen2025",
            comparison,
            f"Table 1, row '{label}'",
            extra,
        )
        for (metric, column, agg), value in zip(COLS_10, row[1:]):
            scope = "the 81 DEKOIS 2.0 targets" if ckey == "quoted-surfdock-dekois" else "the 79 DEKOIS 2.0 targets"
            extra_r = {"source_table": "Table 1"}
            if note:
                extra_r["source_warnings"] = [f"Printed with {note}."]
            if ckey == "quoted-surfdock-dekois":
                extra_r["scope_note"] = "Calculated on all 81 targets, not the 79 used by the other rows (footnote f)."
            result_record(
                f"{PREFIX}-result-dekois-builtin-{ckey}-{metric}-{column.lower().replace('%', 'pct').replace(' ', '').replace('(', '').replace(')', '').replace('α', 'alpha').replace('=', '').replace('.', 'p')}-{agg.lower()}",
                f"{label.rstrip('abcdef')} on DEKOIS 2.0: {column} ({agg})",
                f"{PREFIX}-eval-dekois-builtin-{ckey}",
                metric,
                "higher",
                "unitless",
                value,
                decimal_or_none(value),
                qualifier_10(metric, column, agg, scope),
                f"Table 1, row '{label}', column '{column}' ({agg})",
                "shen2025",
                extra_r,
            )

    # ---- Table 2
    rows = cells("Table 2")[2:]
    blocks = {"Protenix": T2_PROTENIX_ROWS, "AF3": T2_AF3_ROWS}
    current = None
    seen = {"Protenix": [], "AF3": []}
    for row in rows:
        if len(row) == 1:
            if row[0] in blocks:
                current = row[0]
            elif row[0] == "":
                continue
            else:
                raise SystemExit(f"Table 2: unexpected single-cell row {row!r}")
            continue
        if current is None:
            raise SystemExit("Table 2: data row before any block header")
        seen[current].append(row)
    for block, got in seen.items():
        if len(got) != len(blocks[block]):
            raise SystemExit(f"Table 2 {block}: {len(got)} rows, expected {len(blocks[block])}")
    for block, pose in (("Protenix", "protenix"), ("AF3", "af3")):
        pid = f"{PREFIX}-protocol-shen-dekois-rescore-{pose}"
        for row, (label, ckey) in zip(seen[block], blocks[block]):
            if row[0] != label:
                raise SystemExit(f"Table 2 {block}: row label {row[0]!r}, expected {label!r}")
            comparison = dict(base_comparison)
            comparison["protocol_id"] = pid
            comparison["inputs"] = f"Protein sequence and ligand SMILES with pre-computed MSAs; the top-ranked of five {block}-predicted poses is then rescored"
            eid = f"{PREFIX}-eval-dekois-rescore-{pose}-{ckey}"
            eval_record(
                eid,
                f"{label} on {block}-predicted DEKOIS 2.0 complexes (Shen et al. 2025 Table 2)",
                f"{PREFIX}-config-{ckey}",
                pid,
                f"{PREFIX}-dataset-dekois2-79",
                "author_reported",
                "shen2025",
                comparison,
                f"Table 2, {block} block, row '{label}'",
                {"missing_metadata": {"comparison.budget": {"reason": "unreported", "note": "No compute budget is stated for this table"}}, "retrospective": True},
            )
            for (metric, column, agg), value in zip(COLS_10, row[1:]):
                extra_r = {"source_table": "Table 2"}
                if (block, label) in (("Protenix", "ipTM"), ("AF3", "ipTM"), ("AF3", "Min-iPAE")):
                    extra_r["source_warnings"] = ["The same value is printed in Table 1 for this configuration; it is the co-folding confidence score, not a rescoring arm."]
                result_record(
                    f"{PREFIX}-result-dekois-rescore-{pose}-{ckey}-{metric}-{column.lower().replace('%', 'pct').replace(' ', '').replace('(', '').replace(')', '').replace('α', 'alpha').replace('=', '').replace('.', 'p')}-{agg.lower()}",
                    f"{label} on {block}-predicted DEKOIS 2.0 complexes: {column} ({agg})",
                    eid,
                    metric,
                    "higher",
                    "unitless",
                    value,
                    decimal_or_none(value),
                    qualifier_10(metric, column, agg, "the 79 DEKOIS 2.0 targets"),
                    f"Table 2, {block} block, row '{label}', column '{column}' ({agg})",
                    "shen2025",
                    extra_r,
                )

    # ---- Table 3
    rows = cells("Table 3")[2:]
    if len(rows) != len(T3_ROWS):
        raise SystemExit(f"Table 3: {len(rows)} data rows, expected {len(T3_ROWS)}")
    for row, (label, ckey, ntargets) in zip(rows, T3_ROWS):
        if row[0] != label:
            raise SystemExit(f"Table 3: row label {row[0]!r}, expected {label!r}")
        pid = f"{PREFIX}-protocol-shen-gpcrrecent-{ntargets}"
        data = f"{PREFIX}-dataset-gpcrrecent-{ntargets}"
        comparison = {
            "protocol_id": pid,
            "dataset_version": "GPCRrecent as distributed at https://zenodo.org/records/16826965",
            "split": f"All {ntargets} evaluated targets; no training or test split applies",
            "population": f"{ntargets} GPCR targets, BindingDB actives and TocoDecoy-generated decoys at 1:50",
            "inputs": "Protein sequence and ligand SMILES with pre-computed MSAs; docking and rescoring arms use a PDB structure prepared with the Protein Preparation Wizard",
            "adaptation": "None; pretrained models and default or recommended settings",
            "metric_implementation": SHEN_METRICS,
            "aggregation": "Mean and median of the per-target metric over the targets",
            "budget": None,
        }
        suffix = f"{ckey}-{ntargets}t"
        eid = f"{PREFIX}-eval-gpcrrecent-{suffix}"
        eval_record(
            eid,
            f"{label.rstrip('a')} on GPCRrecent (Shen et al. 2025 Table 3)",
            f"{PREFIX}-config-{ckey}",
            pid,
            data,
            "author_reported",
            "shen2025",
            comparison,
            f"Table 3, row '{label}'",
            {"missing_metadata": {"comparison.budget": {"reason": "unreported", "note": "No compute budget is stated for this table"}}, "retrospective": True},
        )
        for (metric, column, agg), value in zip(COLS_10, row[1:]):
            result_record(
                f"{PREFIX}-result-gpcrrecent-{suffix}-{metric}-{column.lower().replace('%', 'pct').replace(' ', '').replace('(', '').replace(')', '').replace('α', 'alpha').replace('=', '').replace('.', 'p')}-{agg.lower()}",
                f"{label.rstrip('a')} on GPCRrecent ({ntargets} targets): {column} ({agg})",
                eid,
                metric,
                "higher",
                "unitless",
                value,
                decimal_or_none(value),
                qualifier_10(metric, column, agg, f"the {ntargets} GPCRrecent targets"),
                f"Table 3, row '{label}', column '{column}' ({agg})",
                "shen2025",
                {"source_table": "Table 3"},
            )

    # ---- Table 4
    rows = cells("Table 4")
    if rows[0][0] != "Method" or rows[0][1:] != ["ESR_ago", "ESR_antago", "PPARG", "TP53", "MAPK1", "Average"]:
        raise SystemExit(f"Table 4: unexpected column header {rows[0]!r}")
    if rows[1] != [c[1] for c in T4_COLS]:
        raise SystemExit(f"Table 4: unexpected sub-header {rows[1]!r}")
    pid = f"{PREFIX}-protocol-shen-litpcba5"
    for row, (label, ckey) in zip(rows[2:], T4_ROWS):
        if row[0] != label:
            raise SystemExit(f"Table 4: row label {row[0]!r}, expected {label!r}")
        comparison = {
            "protocol_id": pid,
            "dataset_version": "LIT-PCBA full data as distributed at https://drugdesign.unistra.fr/LIT-PCBA",
            "split": "Five target sets, each with fewer than 100000 compounds; no training or test split applies",
            "population": "ESR_ago 13/4378, ESR_antago 88/3820, PPARG 24/4071, TP53 64/3345 and MAPK1 308/61567 measured actives and inactives (counts from the official LIT-PCBA page)",
            "inputs": "Protein sequence and ligand SMILES with pre-computed MSAs; docking arms use one selected PDB structure per target and LigPrep-prepared ligands",
            "adaptation": "None; pretrained models and default or recommended settings",
            "metric_implementation": "EF1% and NEF1%, where NEF1% is EF1% divided by its theoretical maximum at the 1% threshold",
            "aggregation": "Per target, and the arithmetic average over the five targets",
            "budget": None,
        }
        eid = f"{PREFIX}-eval-litpcba5-{ckey}"
        eval_record(
            eid,
            f"{label} on the LIT-PCBA five-target subset (Shen et al. 2025 Table 4)",
            f"{PREFIX}-config-{ckey}",
            pid,
            f"{PREFIX}-dataset-litpcba-5",
            "author_reported",
            "shen2025",
            comparison,
            f"Table 4, row '{label}'",
            {"missing_metadata": {"comparison.budget": {"reason": "unreported", "note": "No compute budget is stated for this table"}}, "retrospective": True},
        )
        for (target, column), value in zip(T4_COLS, row[1:]):
            is_nef = column.startswith("NEF")
            metric = "normalized-enrichment-factor" if is_nef else "enrichment-factor"
            scope = "averaged over the five targets" if target == "Average" else f"LIT-PCBA target {target}"
            qual = ("NEF at the top 1% of the ranked library, " if is_nef else "EF at the top 1% of the ranked library, ") + scope
            result_record(
                f"{PREFIX}-result-litpcba5-{ckey}-{target.lower().replace('_', '-')}-{'nef1' if is_nef else 'ef1'}",
                f"{label} on LIT-PCBA {target}: {column.rstrip('a')}",
                eid,
                metric,
                "higher",
                "unitless",
                value,
                decimal_or_none(value),
                qual,
                f"Table 4, row '{label}', column '{target}' ({column.rstrip('a')})",
                "shen2025",
                {"source_table": "Table 4"},
            )

    # ---- Table 5
    rows = cells("Table 5")
    if rows[0] != ["Method", "Number of samples"] + T5_COLS:
        raise SystemExit(f"Table 5: unexpected column header {rows[0]!r}")
    data_rows = rows[1:]
    if len(data_rows) != len(T5_ROWS):
        raise SystemExit(f"Table 5: {len(data_rows)} data rows, expected {len(T5_ROWS)}")
    pid = f"{PREFIX}-protocol-shen-speed"
    for row, (label, samples, ckey) in zip(data_rows, T5_ROWS):
        if label is None:
            if len(row) != 7 or row[0] != samples:
                raise SystemExit(f"Table 5: continuation row {row!r} does not start with sample count {samples!r}")
            values = row[1:]
            printed_label = "(row continued, sample count " + samples + ")"
        else:
            if len(row) != 8 or row[0] != label or row[1] != samples:
                raise SystemExit(f"Table 5: row {row!r} does not match {label!r}/{samples!r}")
            values = row[2:]
            printed_label = label
        comparison = {
            "protocol_id": pid,
            "dataset_version": "DEKOIS 2.0 as distributed at http://www.dekois.com",
            "split": "Five representative targets with 400 randomly selected decoys each",
            "population": "Five DEKOIS 2.0 targets (a2a, ar, cdk2, ctsk, hdac2), 400 decoys per target",
            "inputs": "Pre-computed MSAs and ligand SMILES",
            "adaptation": "None; default or recommended settings",
            "metric_implementation": "Total time for a target divided by its number of compounds",
            "aggregation": "Per target, and the average over the five targets",
            "budget": "One NVIDIA H100 with 80 GB of memory",
        }
        eid = f"{PREFIX}-eval-speed-{ckey}"
        eval_record(
            eid,
            f"{label or 'Continued row'} with {samples} sample(s): time per compound (Shen et al. 2025 Table 5)",
            f"{PREFIX}-config-{ckey}",
            pid,
            f"{PREFIX}-dataset-dekois2-speed5",
            "author_reported",
            "shen2025",
            comparison,
            f"Table 5, row '{printed_label}', column 'Number of samples' = {samples}",
            {"inference_hardware": "A single NVIDIA H100 with 80 GB of memory", "retrospective": True},
        )
        for column, value in zip(T5_COLS, values):
            scope = "averaged over the five targets" if column == "Average" else f"DEKOIS 2.0 target {column}"
            result_record(
                f"{PREFIX}-result-speed-{ckey}-{column.lower()}",
                f"{label or 'Continued row'} ({samples} sample(s)): seconds per compound, {column}",
                eid,
                "runtime",
                "lower",
                "second",
                value,
                decimal_or_none(value),
                f"Average total time per compound on one NVIDIA H100 80 GB, {scope}",
                f"Table 5, row '{printed_label}' (Number of samples = {samples}), column '{column}'",
                "shen2025",
                {"source_table": "Table 5", "unit_detail": "seconds per compound", "hardware": "One NVIDIA H100 with 80 GB of memory"},
            )


# --------------------------------------------------------------------------------------
# Kim, Correy, Hall et al. 2026: evaluations and results
# --------------------------------------------------------------------------------------

KIM_RESULTS = [
    ("sigma2", "kim-dock37", "AUC = 78.8", "78.8"),
    ("sigma2", "kim-af3-lplddt", "AUC = 56.1", "56.1"),
    ("sigma2", "kim-boltz2-pic50", "AUC = 83.8", "83.8"),
    ("d4", "kim-dock37", "AUC ~ 71", None),
    ("d4", "kim-boltz2-pic50", "AUC ~ 71", None),
    ("d4", "kim-af3-lplddt", "AUC = 46.4", "46.4"),
    ("ampc", "kim-dock37", "AUC = 76.5", "76.5"),
    ("ampc", "kim-boltz2-pic50", "AUC = 68.1", "68.1"),
    ("ampc", "kim-af3-lplddt", "AUC = 60.5", "60.5"),
]

KIM_LABEL = {"kim-dock37": "DOCK3.7 energy", "kim-af3-lplddt": "AF3 L-pLDDT", "kim-boltz2-pic50": "Boltz-2 pIC50"}
KIM_SET_LABEL = {"sigma2": "sigma-2 receptor", "d4": "dopamine D4 receptor", "ampc": "AmpC beta-lactamase"}
KIM_DENOM_NOTE = {
    "sigma2": "201 true hits (apparent Ki below 2.0 uM) and 305 non-binders, which are high-ranking docking false positives",
    "d4": "205 true hits (apparent Ki below 7.8 uM) and 336 non-binders, which are high-ranking docking false positives",
    "ampc": "247 true hits (apparent Ki below 400 uM) and 1046 non-binders, which are high-ranking docking false positives",
}

KIM_SENTENCE = {
    "sigma2": "Results 'Co-folding struggles to reliably re-rank docking hit lists', paragraph on the sigma-2 dataset",
    "d4": "Results 'Co-folding struggles to reliably re-rank docking hit lists', paragraph on the dopamine D4 receptor",
    "ampc": "Results 'Co-folding struggles to reliably re-rank docking hit lists', paragraph on AmpC",
}


def build_kim(xml: bytes) -> None:
    text = body_text(xml)
    for _set, _cfg, printed, _num in KIM_RESULTS:
        if printed not in text:
            raise SystemExit(f"Kim et al.: printed value {printed!r} not found in the pinned body text")
    done = set()
    for set_key, ckey, printed, numeric in KIM_RESULTS:
        meta = KIM_SETS[set_key]
        pid = f"{PREFIX}-protocol-kim-{set_key}"
        eid = f"{PREFIX}-eval-kim-{set_key}-{ckey}"
        if eid not in done:
            done.add(eid)
            eval_record(
                eid,
                f"{KIM_LABEL[ckey]} re-ranking the {KIM_SET_LABEL[set_key]} docking hit list (Kim, Correy, Hall et al. 2026)",
                f"{PREFIX}-config-{ckey}",
                pid,
                f"{PREFIX}-dataset-kim-{set_key}",
                "author_reported",
                "kim2026",
                {
                    "protocol_id": pid,
                    "dataset_version": "Tested compounds and measured potencies as provided in Supplementary file 5",
                    "split": "Whole tested list; no training or test split applies",
                    "population": meta["population"],
                    "inputs": "Ligand SMILES and the protein sequence for the co-folding scores; the ligand SMILES and the receptor structure for DOCK3.7",
                    "adaptation": "None; pretrained models and the published docking receptor",
                    "metric_implementation": "Area under the receiver operating characteristic curve for separating true hits from non-binders, printed as a percentage",
                    "aggregation": "Pooled over the compounds of one target's tested list",
                    "budget": None,
                },
                f"{KIM_SENTENCE[set_key]}",
                {
                    "missing_metadata": {"comparison.budget": {"reason": "unreported", "note": "No compute budget is stated for this arm"}},
                    "retrospective": True,
                    "interpretation": "The compounds were all synthesised and assayed, but the score comparison is a retrospective re-ranking of that tested set rather than a new prospective screen.",
                },
            )
        extra = {
            "unit_detail": "printed as a percentage on a 0-100 scale",
            "denominator": meta["positives"] + meta["negatives"],
            "numerator": meta["positives"],
            "denominator_note": KIM_DENOM_NOTE[set_key],
        }
        if numeric is None:
            extra["approximate"] = True
            extra["source_warnings"] = [
                "The source prints this value as an approximation shared by two scores: 'both with AUC ~ 71'. "
                "No separate value is printed for DOCK3.7 and for Boltz-2 pIC50, so numeric_value is null."
            ]
        result_record(
            f"{PREFIX}-result-kim-{set_key}-{ckey}-auc",
            f"{KIM_LABEL[ckey]} on the {KIM_SET_LABEL[set_key]} docking hit list: AUC",
            eid,
            "auroc",
            "higher",
            "unitless",
            printed,
            numeric,
            f"Discrimination of measured binders from high-ranking docking false positives in the tested {KIM_SET_LABEL[set_key]} hit list",
            f"{KIM_SENTENCE[set_key]}; printed in the body text as '{printed}'",
            "kim2026",
            extra,
        )


# --------------------------------------------------------------------------------------
# CACHE #3 table S8
# --------------------------------------------------------------------------------------

S8_HEADER = {
    "B": "Workflow",
    "C": "Participant",
    "D": "Compounds tested",
    "E": "Hits",
    "F": "Chemically Novel Hits",
    "G": "Score of best hit",
    "H": "Aggregated score",
    "I": "Top novelty score",
    "J": "Top score of novel hits",
    "K": "Carboxylic acid penalty",
    "L": "predicted active",
    "M": "predicted weak",
    "N": "tier 1 hits predicted active",
    "O": "tier 2 hits predicted active",
    "P": "tier 1 hits predicted weak",
    "Q": "tier 2 hits predicted weak",
    "R": "Normalized tier 1 hits predicted active",
    "S": "Normalized tier 2 hits predicted active",
}

OWN_COLS = [
    ("D", "Compounds tested", "count", "count", "compounds", "Compounds the workflow selected that were synthesised and experimentally tested"),
    ("E", "Hits", "count", "count", "compounds", "Experimentally confirmed hits among the compounds the workflow selected"),
    ("F", "Chemically Novel Hits", "count", "count", "compounds", "Confirmed hits the Hit Evaluation Committee judged chemically novel, among the compounds the workflow selected"),
    ("G", "Score of best hit", "cache-challenge-activity-score", "unitless", None, "Activity score of the workflow's best confirmed Round 1 hit"),
    ("H", "Aggregated score", "cache-challenge-activity-score", "unitless", None, "Sum of the activity scores of all the workflow's confirmed Round 1 hits"),
    ("I", "Top novelty score", "cache-challenge-novelty-score", "unitless", None, "Highest chemical novelty score among the workflow's confirmed Round 1 hits"),
    ("J", "Top score of novel hits", "cache-challenge-activity-score", "unitless", None, "Activity score of the workflow's best confirmed Round 1 hit that was judged chemically novel"),
]

MERGED_COLS = [
    ("L", "predicted active", "count", "count", "compounds", "Compounds of the merged 1739-compound Round 1 library the workflow predicted to be active"),
    ("M", "predicted weak", "count", "count", "compounds", "Compounds of the merged 1739-compound Round 1 library the workflow predicted to be weakly active"),
    ("N", "tier 1 hits predicted active", "count", "count", "compounds", "Confirmed Tier 1 (chemically novel) hits among the workflow's predicted-active compounds on the merged library"),
    ("O", "tier 2 hits predicted active", "count", "count", "compounds", "Confirmed Tier 2 (not novel) hits among the workflow's predicted-active compounds on the merged library"),
    ("P", "tier 1 hits predicted weak", "count", "count", "compounds", "Confirmed Tier 1 (chemically novel) hits among the workflow's predicted-weak compounds on the merged library"),
    ("Q", "tier 2 hits predicted weak", "count", "count", "compounds", "Confirmed Tier 2 (not novel) hits among the workflow's predicted-weak compounds on the merged library"),
    ("R", "Normalized tier 1 hits predicted active", "cache-challenge-normalized-hit-score", "unitless", None, "Normalised Tier 1 value for the workflow's predicted-active compounds on the merged library"),
    ("S", "Normalized tier 2 hits predicted active", "cache-challenge-normalized-hit-score", "unitless", None, "Normalised Tier 2 value for the workflow's predicted-active compounds on the merged library"),
    ("T", "(unnamed final column)", "cache-challenge-normalized-hit-score", "unitless", None, "Sum of the normalised Tier 1 and Tier 2 values for the workflow's predicted-active compounds on the merged library"),
]


def build_cache3(xlsx: bytes) -> None:
    rows = xlsx_sheet(xlsx, "S8")
    header, data = rows[0], rows[1:]
    for col, want in S8_HEADER.items():
        if header.get(col, "") != want:
            raise SystemExit(f"Table S8: column {col} header {header.get(col)!r}, expected {want!r}")
    if header.get("T", "") != "":
        raise SystemExit("Table S8: column T was expected to have no printed header")
    if len(data) != 23:
        raise SystemExit(f"Table S8: {len(data)} workflow rows, expected 23")
    ranks = []
    penalties = []
    for row in data:
        wf = row.get("B", "")
        if not wf:
            raise SystemExit(f"Table S8: a row has no workflow id: {row!r}")
        participant = row.get("C", "").strip()
        ranks.append(f"{wf}={row.get('A', '')}")
        if row.get("K", "").strip():
            penalties.append(f"{wf}={row['K'].strip()}")
        attrs = {
            "missing_metadata": {"version": {"reason": "unreported", "note": "Workflow components are shown only in Figures 2, 7 and 8 of the article; no version or software list is printed in text"}},
            "source_locator": f"Sheet 'S8', row with Workflow = {wf}",
            "provenance_note": (
                f"Blinded CACHE #3 Round 1 submission WF{wf}."
                + (f" Participant as printed: {participant}." if participant else " No participant is named in this sheet.")
                + " No entity-level record was created for the workflow: its computational steps appear only in"
                " figures, which this batch does not read."
            ),
        }
        cfg(
            f"cache3-wf{wf}",
            f"CACHE #3 workflow WF{wf}",
            "Selects commercially available compounds predicted to bind the SARS-CoV-2 Nsp3 macrodomain, and ranks the merged Round 1 library for predicted activity.",
            f"WF{wf}",
            ["conventional_pipeline"],
            "cache3_si002",
            attrs,
        )
        for pid_short, cols in (("own-selection", OWN_COLS), ("merged-library", MERGED_COLS)):
            present = [c for c, *_ in cols if row.get(c, "") != ""]
            if not present:
                continue
            if len(present) != len(cols):
                raise SystemExit(f"Table S8 WF{wf}: {pid_short} columns partly blank ({present})")
            pid = f"{PREFIX}-protocol-cache3-{pid_short}"
            eid = f"{PREFIX}-eval-cache3-{pid_short}-wf{wf}"
            eval_record(
                eid,
                f"CACHE #3 workflow WF{wf}: {pid_short.replace('-', ' ')} outcome",
                f"{PREFIX}-config-cache3-wf{wf}",
                pid,
                f"{PREFIX}-dataset-cache3-round1",
                "author_reported",
                "cache3_si002",
                {
                    "protocol_id": pid,
                    "dataset_version": "CACHE #3 Round 1, published 2026-01-21",
                    "split": "Whole Round 1 library; no training or test split applies",
                    "population": (
                        "The up-to-100 compounds this workflow selected, which Enamine synthesised and the organisers assayed"
                        if pid_short == "own-selection"
                        else "All 1739 merged Round 1 compounds, the same library for every workflow"
                    ),
                    "inputs": "The target and the commercial libraries for Round 1 selection; the merged list of all Round 1 compounds for the merged-library arm",
                    "adaptation": "Each team's own workflow, submitted before any experimental result was known",
                    "metric_implementation": "Counts of tested compounds and confirmed hits, and the challenge's activity, novelty and normalised scores",
                    "aggregation": "One value per workflow",
                    "budget": None,
                },
                f"Sheet 'S8', row with Workflow = {wf}",
                {
                    "interpretation": "Blinded prospective challenge: predictions were submitted before any compound was synthesised or assayed.",
                    "missing_metadata": {"comparison.budget": {"reason": "unreported", "note": "No compute budget is printed for any workflow"}},
                    "retrospective": False,
                },
            )
            for col, label, metric, unit, unit_detail, qual in cols:
                raw = row[col]
                printed = shortest_decimal(raw)
                extra = {
                    "source_table": "Table S8",
                    "raw_xml_value": raw,
                    "printed_value_basis": (
                        "The workbook stores this cell as a double. printed_value is the shortest decimal that "
                        "round-trips to that double, which is what a spreadsheet shows; raw_xml_value keeps the "
                        "stored string."
                    ),
                    "workbook_number_format": "Not applied: the cell's number format was not read, so printed_value is the round-tripped decimal rather than the displayed string.",
                }
                if unit_detail:
                    extra["unit_detail"] = unit_detail
                if col == "T":
                    extra["source_warnings"] = ["This column has no printed header in sheet S8. Its values equal the sum of the two preceding normalised columns."]
                if col in ("R", "S"):
                    extra["source_warnings"] = [
                        "The column is labelled as a count of hits, but the article's Figure 6 caption defines the "
                        "normalised quantity as the aggregated score of all compounds predicted active divided by the "
                        "number of compounds predicted to be actives. The label and the definition do not agree."
                    ]
                result_record(
                    f"{PREFIX}-result-cache3-{pid_short}-wf{wf}-{col.lower()}",
                    f"CACHE #3 WF{wf}: {label}",
                    eid,
                    metric,
                    "higher",
                    unit,
                    printed,
                    decimal_or_none(printed),
                    qual,
                    f"Sheet 'S8', row with Workflow = {wf}, column {col} ('{label}')",
                    "cache3_si002",
                    extra,
                )
    rec(
        f"{PREFIX}-claim-cache3-s8-unlabelled-column",
        "claim",
        "CACHE #3 table S8 has an unlabelled first column",
        "Record of the unlabelled first column of CACHE #3 table S8, which this batch did not interpret as a metric.",
        "needs_review",
        [src_id("cache3_si002")],
        {
            "field": "tables_not_extracted",
            "value": (
                "Sheet 'S8' column A has no printed header. Its 23 values are a permutation of 1 to 23, so the "
                "column is most likely a rank, but the sheet and the article do not say what it ranks. Values as "
                "Workflow=value: " + ", ".join(ranks) + "."
            ),
            "source_locator": "Sheet 'S8', column A, rows 2 to 24",
            "review": review(["deterministic-table-parse"], EXTRACT_NOTE, "cache3_si002"),
        },
        links=[{"relation": "subject", "target_id": f"{PREFIX}-benchmark-cache3"}],
    )
    rec(
        f"{PREFIX}-claim-cache3-carboxylic-acid-penalty",
        "claim",
        "CACHE #3 carboxylic acid penalty in table S8",
        "Record of the carboxylic acid penalty column of CACHE #3 table S8.",
        "needs_review",
        [src_id("cache3_si002")],
        {
            "field": "reported_finding",
            "value": (
                "Sheet 'S8' column K, 'Carboxylic acid penalty', carries a value for "
                + (", ".join(penalties) if penalties else "no workflow")
                + " and is blank for every other workflow. Neither the sheet nor the article says whether a blank "
                "cell means no penalty or no entry, so the blanks are not recorded as a value. The article states "
                "that 15% of the Round 1 compounds still featured carboxylates despite this being an explicit "
                "condition of the challenge."
            ),
            "source_locator": "Sheet 'S8', column K; article Results 'Trends and Strategies from the Best Performing Computational Workflows'",
            "review": review(["deterministic-table-parse"], EXTRACT_NOTE, "cache3_si002"),
        },
        links=[{"relation": "subject", "target_id": f"{PREFIX}-benchmark-cache3"}],
    )
    rec(
        f"{PREFIX}-claim-cache3-sheets-not-extracted",
        "claim",
        "CACHE #3 supporting sheets not extracted",
        "Record of the CACHE #3 supporting sheets this batch did not extract.",
        "needs_review",
        [src_id("cache3_si002")],
        {
            "field": "tables_not_extracted",
            "value": (
                "Of ci5c02441_si_002.xlsx only sheet 'S8' was extracted. Sheets 'S1' to 'S7' and the title page were "
                "not: S7 is a per-compound scoring matrix with two judges' scores per topic and would need its own "
                "pass, and S2, S3, S5 and S6 hold the per-compound HTRF and SPR assay data, which is wet-lab "
                "measurement rather than library ranking. The second workbook ci5c02441_si_003.xlsx "
                "(crystallography and ligand modelling) and the Supporting Information PDF ci5c02441_si_001.pdf "
                "(chemical series figures) were retrieved but not extracted. Figures 6a, 6b and 6c of the article "
                "were not read; their values are in sheet S8, which was."
            ),
            "source_locator": "Workbook sheet list; sheets S1-S7",
            "review": review(["deterministic-table-parse"], EXTRACT_NOTE, "cache3_si002"),
        },
        links=[{"relation": "subject", "target_id": f"{PREFIX}-benchmark-cache3"}],
    )


# --------------------------------------------------------------------------------------
# Descriptive claims
# --------------------------------------------------------------------------------------


def build_claims() -> None:
    rec(
        f"{PREFIX}-claim-litpcba-leakage-audit",
        "claim",
        "LIT-PCBA leakage audit: a parameter-free memorisation baseline matches the state of the art",
        "The headline finding of the LIT-PCBA data-leakage audit, which bears on every LIT-PCBA result.",
        "needs_review",
        [src_id("litpcba_audit")],
        {
            "field": "reported_finding",
            "value": (
                "Huang, Knight and Naprienko report extensive data leakage and molecular redundancy across the "
                "LIT-PCBA splits: 2D-identical ligands within and across partitions, pervasive analogue overlap and "
                "low-diversity query sets. In ALDH1 alone 323 active training-validation analogue pairs occur at "
                "ECFP4 Tanimoto at or above 0.6; across all targets 2,491 2D-identical inactives appear in both "
                "training and validation, with very few corresponding actives. They state that these overlaps let "
                "models succeed through scaffold memorisation rather than generalisation, inflating enrichment "
                "factors and AUROC scores, and that the flaws are severe enough that a trivial memorisation-based "
                "baseline with no learnable parameters can match or exceed the reported performance of "
                "state-of-the-art deep-learning and 3D-similarity models. They conclude that nearly all published "
                "results on LIT-PCBA are undermined, that even models evaluated in zero-shot mode are affected by "
                "analogue leakage into the query set, and that the benchmark in its current form does not measure "
                "a model's ability to recover novel chemotypes."
            ),
            "source_locator": "Abstract",
            "review": review(["transcription"], EXTRACT_NOTE + " Only the abstract page was retrieved; the preprint's tables were not read.", "litpcba_audit"),
        },
        links=[{"relation": "subject", "target_id": f"{PREFIX}-benchmark-litpcba"}],
    )
    rec(
        f"{PREFIX}-claim-dude-hidden-bias",
        "claim",
        "Hidden bias in DUD-E misleads deep-learning virtual screening",
        "The finding that convolutional neural network performance on DUD-E reflects decoy construction rather than binding.",
        "needs_review",
        [src_id("chen2019")],
        {
            "field": "reported_finding",
            "value": (
                "Chen et al. 2019 report that convolutional neural network models trained on 3D structural images of "
                "protein-ligand complexes from DUD-E are subject to a hidden bias in that dataset, so their apparent "
                "ability to distinguish binding from non-binding ligands in structure-based virtual screening is "
                "misleading rather than a measure of molecular recognition."
            ),
            "source_locator": "Title; Abstract",
            "review": review(["transcription"], EXTRACT_NOTE + " Only the abstract was read; no table or figure of this paper was extracted.", "chen2019"),
        },
        links=[{"relation": "subject", "target_id": f"{PREFIX}-benchmark-dude"}],
    )
    rec(
        f"{PREFIX}-claim-dude-composition",
        "claim",
        "DUD-E composition and decoy construction",
        "The composition DUD-E's own paper reports, which sets the scale of any enrichment factor measured on it.",
        "needs_review",
        [src_id("dude2012")],
        {
            "field": "reported_finding",
            "value": (
                "Mysinger et al. 2012 describe DUD-E as 102 proteins with 22,886 clustered ligands drawn from ChEMBL, "
                "each ligand accompanied by 50 property-matched decoys, with more diverse targets than the original "
                "DUD including GPCRs and ion channels. The decoys are selected to match the ligands on physical "
                "properties while being topologically dissimilar to them, so they are synthetic negatives rather "
                "than assayed inactives."
            ),
            "source_locator": "Abstract",
            "review": review(["transcription"], EXTRACT_NOTE + " Only the abstract was read.", "dude2012"),
        },
        links=[{"relation": "subject", "target_id": f"{PREFIX}-benchmark-dude"}],
    )
    rec(
        f"{PREFIX}-claim-shen-decoy-ratios",
        "claim",
        "Actives-to-decoys ratio and decoy construction differ by orders of magnitude between the screening benchmarks",
        "The composition facts that make raw enrichment factors incomparable between these benchmarks.",
        "needs_review",
        [src_id("shen2025"), src_id("litpcba_page")],
        {
            "field": "reported_finding",
            "value": (
                "DEKOIS 2.0 holds 40 experimentally validated actives and 1200 property-matched decoys selected from "
                "ZINC per target, a ratio of 1:30. GPCRrecent holds BindingDB actives with decoys generated by a "
                "conditional recurrent neural network (TocoDecoy) at 1:50. LIT-PCBA's negatives are experimentally "
                "measured inactives, and its official per-target counts give ratios from 13 actives to 4,378 "
                "inactives (ESR_ago, about 1:337) and 88 to 3,820 (ESR_antago, about 1:43) up to 17 to 311,748 "
                "(ADRB2, about 1:18,000). DUD-E pairs each of 22,886 clustered ligands with 50 property-matched "
                "decoys. An enrichment factor is a ratio against random selection at a fixed fraction of the list, "
                "so it moves with both the ratio and the realism of the negatives; values from these benchmarks are "
                "not comparable with one another."
            ),
            "source_locator": "Shen et al. 2025 Methods 'Datasets' and 'Evaluation metrics'; LIT-PCBA official page data content table",
            "review": review(["transcription"], EXTRACT_NOTE, "shen2025"),
        },
        links=[{"relation": "subject", "target_id": f"{PREFIX}-benchmark-dekois2"}],
    )


# --------------------------------------------------------------------------------------
# Use case, relevance judgements and summary
# --------------------------------------------------------------------------------------

JUDGEMENTS = [
    dict(
        pid="shen-dekois-builtin",
        relevance="proxy",
        group="screening-enrichment-synthetic-decoys",
        title="Retrospective enrichment on synthetic property-matched decoys",
        stratum="DEKOIS 2.0, built-in co-folding scores against docking tools (24 arms)",
        order=1,
        endpoint="AUROC, BEDROC (alpha = 80.5) and enrichment factors at 0.5%, 1% and 5%, mean and median over 79 DEKOIS 2.0 targets",
        rationale=(
            "Proxy: the endpoint is exactly the one the use case asks about, ranking a library so that real binders "
            "come out on top, and docking baselines are scored on the same targets and compounds. But the negatives "
            "are property-matched decoys selected from ZINC rather than compounds anyone assayed, so the enrichment "
            "figures measure separation from synthetic molecules, not from the false positives a real screen throws "
            "up. The best co-folding score here reaches EF1% 23.15 (AF3 min-iPAE, mean) against 12.01 for the quoted "
            "Glide SP row, a margin that does not survive the move to measured inactives in this same paper."
        ),
        extra_limits=[
            "Eight of the 24 arms are values quoted from five other papers, so they were not produced under one common pipeline.",
            "The two Boltz-2 affinity arms are flagged by the authors themselves as likely over-estimates from training-data overlap with the databases that source DEKOIS 2.0.",
        ],
    ),
    dict(
        pid="shen-dekois-rescore-protenix",
        relevance="proxy",
        group="screening-enrichment-synthetic-decoys",
        title="Retrospective enrichment on synthetic property-matched decoys",
        stratum="DEKOIS 2.0, rescoring of Protenix-predicted complexes (13 arms)",
        order=2,
        endpoint="AUROC, BEDROC (alpha = 80.5) and enrichment factors at 0.5%, 1% and 5%, mean and median over 79 DEKOIS 2.0 targets",
        rationale=(
            "Proxy, for the same reason as the built-in-score arm: right endpoint, synthetic negatives. This arm "
            "answers a narrower question that still bears on the decision, namely whether a classical or "
            "deep-learning scoring function applied to a co-folded pose beats the model's own confidence score. On "
            "Protenix poses only Gnina CNNscore (EF1% 16.69, mean) and RTMScore (20.37) approach the co-folding ipTM "
            "value (16.81), while Glide SP reaches 12.65."
        ),
        extra_limits=["Structures the Protein Preparation Wizard could not process were given an extremely low score rather than excluded."],
    ),
    dict(
        pid="shen-dekois-rescore-af3",
        relevance="proxy",
        group="screening-enrichment-synthetic-decoys",
        title="Retrospective enrichment on synthetic property-matched decoys",
        stratum="DEKOIS 2.0, rescoring of AF3-predicted complexes (10 arms)",
        order=3,
        endpoint="AUROC, BEDROC (alpha = 80.5) and enrichment factors at 0.5%, 1% and 5%, mean and median over 79 DEKOIS 2.0 targets",
        rationale=(
            "Proxy, for the same reason: right endpoint, synthetic negatives. On AF3 poses the rescoring functions "
            "again fail to beat the co-folding confidence scores: AF3 min-iPAE gives EF1% 23.15 (mean) against 21.34 "
            "for RTMScore, 16.51 for Gnina CNNscore and 12.65 for Glide SP."
        ),
        extra_limits=["Structures the Protein Preparation Wizard could not process were given an extremely low score rather than excluded."],
    ),
    dict(
        pid="shen-gpcrrecent-16",
        relevance="proxy",
        group="screening-enrichment-synthetic-decoys",
        title="Retrospective enrichment on synthetic property-matched decoys",
        stratum="GPCRrecent, 16 targets with post-2022 structures (16 arms)",
        order=4,
        endpoint="AUROC, BEDROC (alpha = 80.5) and enrichment factors at 0.5%, 1% and 5%, mean and median over 16 GPCR targets",
        rationale=(
            "Proxy with a stronger control than the DEKOIS 2.0 arms: the targets' first crystal structures were "
            "released after 2022, so the structural inputs postdate the co-folding models' training data. The "
            "negatives are still generated decoys, now from a conditional recurrent neural network at 1:50. The "
            "margin over docking narrows here: Boltz-2 min-iPAE gives EF1% 13.96 (mean) against 5.02 for Glide SP "
            "and 3.65 for Gnina Vina, but every value is far below the same scores' DEKOIS 2.0 figures."
        ),
        extra_limits=[
            "The temporal control covers crystal structures only; the authors exclude Boltz-2's affinity module from this analysis because its binding-data training sources overlap the benchmark.",
            "AF3 was not run on this set.",
        ],
    ),
    dict(
        pid="shen-gpcrrecent-6",
        relevance="proxy",
        group="screening-enrichment-synthetic-decoys",
        title="Retrospective enrichment on synthetic property-matched decoys",
        stratum="GPCRrecent, six targets after the Boltz-2 training cutoff (2 arms)",
        order=5,
        endpoint="AUROC, BEDROC (alpha = 80.5) and enrichment factors at 0.5%, 1% and 5%, mean and median over six GPCR targets",
        rationale=(
            "Proxy, and the tightest leakage control in the batch for a decoy benchmark: six targets whose first "
            "crystal structures were released after Boltz-2's June 2023 training cutoff. Only two arms were run on "
            "it, both Boltz-2 confidence scores, with no docking arm on the same six targets, so it constrains "
            "Boltz-2's own numbers rather than comparing it with docking."
        ),
        extra_limits=["No docking or rescoring arm was run on these six targets, so there is no baseline to compare against within this protocol."],
    ),
    dict(
        pid="shen-litpcba5",
        relevance="proxy",
        group="screening-enrichment-measured-inactives",
        title="Retrospective enrichment where the inactives were measured",
        stratum="LIT-PCBA, five targets under 100,000 compounds (7 arms)",
        order=1,
        endpoint="Enrichment factor and normalised enrichment factor at the top 1% of the ranked library, per target and averaged over five targets",
        rationale=(
            "Proxy, and the most informative retrospective arm in the batch, because the inactives were "
            "experimentally measured rather than constructed. It is still proxy evidence: the compounds were chosen "
            "by past screening campaigns, the benchmark is retrospective, and its splits are compromised by the "
            "leakage the audit documents. The co-folding advantage over docking that the decoy benchmarks show "
            "largely disappears here: averaged over the five targets Boltz-2 min-iPAE gives EF1% 9.30 and NEF1% "
            "0.100 against Glide SP's 6.79 and 0.079, and on TP53 both Boltz-2 scores give EF1% 0.00 while Protenix "
            "ipTM gives 5.00 and Glide SP 3.75."
        ),
        extra_limits=[
            "The LIT-PCBA leakage audit concludes that a parameter-free memorisation baseline matches or exceeds published deep-learning results on this benchmark and that nearly all published results on it are undermined. Every value from this protocol must be read with that finding.",
            "Five of 15 targets were screened, selected for size, and MTORC1 was dropped for ambiguous binding sites.",
            "No AUROC or BEDROC column is printed for this table, so early-recognition behaviour cannot be compared with the decoy benchmarks.",
        ],
    ),
    dict(
        pid="kim-sigma2",
        relevance="direct",
        group="prospective-tested-hit-lists",
        title="Re-ranking compounds that were synthesised and assayed",
        stratum="Sigma-2 receptor: 201 binders and 305 docking false positives",
        order=1,
        endpoint="Area under the ROC curve for separating measured binders from high-ranking docking false positives, printed on a 0-100 scale",
        rationale=(
            "Direct: every compound in the list was synthesised and assayed, the labels are measured potencies with "
            "a stated threshold, the negatives are the false positives a real ultra-large docking screen produced, "
            "and DOCK3.7, the engine that produced the list, is scored on the same compounds. This is the use case's "
            "question asked on the hardest realistic negatives. Boltz-2 pIC50 separates binders best here (AUC "
            "83.8), ahead of DOCK3.7 (78.8), while AF3 L-pLDDT is close to uninformative (56.1)."
        ),
        extra_limits=[
            "Only high-ranking docked molecules were synthesised, so the list is a biased sample of the 490-million library and no value from it estimates performance over a whole library.",
            "The comparison is a retrospective re-ranking of a prospectively tested set, not a new prospective screen.",
            "No training-overlap control is stated for this arm.",
        ],
    ),
    dict(
        pid="kim-d4",
        relevance="direct",
        group="prospective-tested-hit-lists",
        title="Re-ranking compounds that were synthesised and assayed",
        stratum="Dopamine D4 receptor: 205 binders and 336 docking false positives",
        order=2,
        endpoint="Area under the ROC curve for separating measured binders from high-ranking docking false positives, printed on a 0-100 scale",
        rationale=(
            "Direct, on the same grounds as the sigma-2 arm. Here docking and Boltz-2 are indistinguishable at the "
            "precision the source prints (both AUC about 71) and AF3 L-pLDDT is worse than random (46.4), so the "
            "co-folding scores give no advantage over the docking engine that generated the list."
        ),
        extra_limits=[
            "The source prints a single approximate value, 'both with AUC ~ 71', for DOCK3.7 and Boltz-2 pIC50; no separate figure is given, so neither result carries a numeric value.",
            "Only high-ranking docked molecules were synthesised, so the list is a biased sample of the 138-million library.",
            "No training-overlap control is stated for this arm.",
        ],
    ),
    dict(
        pid="kim-ampc",
        relevance="direct",
        group="prospective-tested-hit-lists",
        title="Re-ranking compounds that were synthesised and assayed",
        stratum="AmpC beta-lactamase: 247 inhibitors and 1,046 docking false positives",
        order=3,
        endpoint="Area under the ROC curve for separating measured binders from high-ranking docking false positives, printed on a 0-100 scale",
        rationale=(
            "Direct, on the same grounds, and the largest of the three lists. Docking is clearly the strongest arm "
            "here (AUC 76.5) ahead of Boltz-2 pIC50 (68.1) and AF3 L-pLDDT (60.5), which is the opposite ordering "
            "to the decoy benchmarks."
        ),
        extra_limits=[
            "The 1,293 tested compounds were sampled from scoring bins within the top 1% of 1.7 billion docked molecules, so the list is a biased sample of the library.",
            "The activity threshold for a true hit on this target is an apparent Ki below 400 uM, far weaker than the thresholds used for the two receptors.",
            "No training-overlap control is stated for this arm.",
        ],
    ),
    dict(
        pid="cache3-own-selection",
        relevance="direct",
        group="cache3-prospective-challenge",
        title="Blinded prospective community challenge on the Nsp3 macrodomain",
        stratum="Round 1: each workflow's own selection, synthesised and assayed",
        order=1,
        endpoint="Compounds selected and experimentally tested per workflow, confirmed hits and chemically novel hits among them, and the challenge's activity and novelty scores",
        rationale=(
            "Direct: the predictions were submitted before any compound was made, every selected compound was "
            "synthesised by Enamine and assayed by HTRF, dose response and surface plasmon resonance, and the "
            "counts are of confirmed binders. It answers the second half of the use case's question, how many "
            "compounds must be tested to find one, for each workflow: the denominators are 41 to 99 compounds per "
            "workflow, and 12 of the 23 workflows returned no confirmed hit at all."
        ),
        extra_limits=[
            "Each workflow selected its own compounds, so differences between workflows mix the ranking method with the library and chemistry each team chose. The merged-library arm is the comparison on one library.",
            "The source prints no per-workflow hit rate; this batch records the numerator and the denominator as separate printed counts and does not divide them.",
            "The denominators are small and unequal, so a one-hit difference moves a workflow's apparent rate by several percentage points.",
            "The activity and novelty scores are committee judgements, not measurements.",
        ],
    ),
    dict(
        pid="cache3-merged-library",
        relevance="direct",
        group="cache3-prospective-challenge",
        title="Blinded prospective community challenge on the Nsp3 macrodomain",
        stratum="Round 1: every workflow applied to the same merged 1,739-compound library",
        order=2,
        endpoint="Compounds predicted active and predicted weak on the merged library per workflow, confirmed Tier 1 and Tier 2 hits among them, and the challenge's normalised values",
        rationale=(
            "Direct, and the closest thing in this batch to the use case's question asked cleanly: every workflow "
            "ranked the same 1,739 compounds, all of which had been assayed, so the library is held constant and "
            "only the ranking differs. The article's own reading is that WF1696, a purely physics-based workflow, "
            "retrieved significantly more hits than any other; in table S8 it predicted 99 compounds active and "
            "captured 2 of the 4 Tier 1 and 9 of the 25 Tier 2 confirmed hits."
        ),
        extra_limits=[
            "The merged library is the union of what the workflows themselves selected, so it is not an independent library and each workflow's own picks are in it.",
            "Four of the 23 workflows (1694, 1695, 1716, 1717) have no values printed in these columns; they are absent, not zero.",
            "Only 29 confirmed hits scored above 15, four of them chemically novel, so the Tier 1 counts rest on four compounds in total.",
            "The two normalised columns are labelled as hit counts but defined in the article's figure caption as an aggregated score divided by the number of compounds predicted active, and the final column has no printed header.",
            "One target, one round and one organiser's library: nothing here shows how the ordering would hold on another target.",
        ],
    ),
    dict(
        pid="shen-speed",
        relevance="proxy",
        group="co-folding-screening-cost",
        title="Compute cost per compound of co-folding",
        stratum="Five DEKOIS 2.0 targets, one NVIDIA H100",
        order=1,
        endpoint="Average wall-clock seconds per compound to co-fold a protein-ligand pair, per target and averaged over five targets",
        rationale=(
            "Proxy: it measures cost rather than ranking, but issue #177 lists compute per compound as a limit to "
            "record for every result because it decides whether a method can be run on a library at all. At 7.79 to "
            "34.58 seconds per compound on one H100, a million-compound library would take between about 90 and "
            "400 GPU-days. That multiplication is this agent's arithmetic on the printed per-compound times, not "
            "a figure the source prints, and it is the constraint behind the authors' own decision to screen only "
            "five of the 15 LIT-PCBA targets."
        ),
        extra_limits=[
            "MSA construction is excluded: pre-computed MSAs were fed as input, so these are inference times only.",
            "No docking tool was timed, so the table does not compare co-folding cost with docking cost.",
            "Single measurements on five targets with no repeats or uncertainty; the authors note that runtime varies substantially with token length and other factors.",
        ],
    ),
]

UC_ID = "use-case-hit-discovery-virtual-screening"

COMMON_CONSTRAINTS = [
    "Inspect every linked evaluation's source locator before citing a result.",
    "Compare rows only within this protocol. Enrichment factors from different protocols are not comparable, because the actives-to-inactives ratio and the construction of the negatives differ.",
    "Do not read a result from this protocol together with the Mac1 pose results or the CASF-2016 scoring, ranking and docking protocols already in this store: those measure pose and scoring accuracy, not the ranking of a library.",
]

COMMON_LIMITS = [
    "Transcribed from the source; no reproduction by Rewire and no human scientific review.",
    "No ligand-similarity or pharmacophore baseline is scored on any protocol in this batch, although issue #177 asks for one as the pre-machine-learning comparator alongside docking.",
]


def build_use_case() -> None:
    links = [{"relation": "assessed_by", "target_id": f"{PREFIX}-protocol-{j['pid']}"} for j in JUDGEMENTS]
    rec(
        UC_ID,
        "use_case",
        "Find hits for a target by virtual screening",
        "Which computational screening workflow puts real binders at the top of a large compound library, and how many compounds must be tested to find one?",
        "needs_review",
        [src_id("shen2025"), src_id("kim2026"), src_id("cache3"), src_id("cache3_si002"), src_id("litpcba_audit")],
        {
            "slug": "hit-discovery-virtual-screening",
            "question": "Which computational screening workflow puts real binders at the top of a large compound library, and how many compounds must be tested to find one?",
            "intended_users": [
                "Computational chemists choosing a scoring method before committing a library screen to synthesis and assay",
                "Project teams deciding how many top-ranked compounds to buy or make, and what hit rate to expect",
                "Method developers who need to know which screening benchmarks can still distinguish methods",
            ],
            "decision": "Choose the method that will rank a compound library for one protein target, and decide how many top-ranked compounds to synthesise and test.",
            "inputs": [
                "One protein target, with a sequence and, for docking and rescoring methods, a prepared receptor structure",
                "A compound library to rank, with the actives-to-inactives ratio and how any negatives were constructed",
                "A compute budget, since cost per compound decides whether a method can run on the library at all",
                "A synthesis and assay budget, which sets how many top-ranked compounds can be tested",
            ],
            "output": "Enrichment of true actives at a stated fraction of the library for each method on each protocol, with the decoy construction and actives-to-inactives ratio of that protocol; measured counts of confirmed hits and compounds tested where a paper synthesised and assayed compounds; and compute per compound. No recommendation of a method and no prediction of a hit rate for an untested library.",
            "setting": (
                "Early hit discovery for a single protein target with a known or predictable structure. The endpoint "
                "is the ranking of a library, not the accuracy of one complex: an enrichment factor at a stated "
                "fraction of the list, or a measured count of confirmed hits with its denominator. Retrospective "
                "benchmarks score a method against a curated set of actives and negatives; prospective campaigns "
                "measure what was found when compounds were actually synthesised and assayed. The two answer "
                "different questions and are kept apart."
            ),
            "exclusions": [
                "Pose accuracy and binding-mode reproduction, including the Mac1 co-folding pose benchmark and the CASF-2016 docking power protocols already in this store",
                "Affinity prediction and scoring-power correlation, including CASF-2016 scoring and ranking power",
                "Lead optimisation and hit-to-lead potency improvement, which is a separate use case",
                "De novo molecule generation and library design",
                "Target identification and target validation",
                "Any recommendation for clinical or therapeutic use",
            ],
            "clinical_scope": "Research use only. Nothing here supports a clinical decision, and no compound named in the cited sources is a medicine.",
            "evidence_gaps": [
                "No protocol in this store scores a ligand-similarity or pharmacophore search as a pre-machine-learning baseline, although issue #177 asks for one alongside docking. Lam et al. 2024 print IFP and GRIM rows on LIT-PCBA but quote them from third parties.",
                "No DUD-E evaluation is extracted. DUD-E is registered with its composition and the Chen et al. 2019 bias finding, but no result on it is recorded.",
                "No MF-PCBA evaluation is extracted, so the Boltzina and Boltz-2 affinity-head fine-tuning results on measured PubChem dose-response data (arXiv:2508.17555 and arXiv:2609.24302) remain outside the store; only their abstracts were seen in the search pass.",
                "The hit-rate curves, semi-logarithmic ROC curves and early-enrichment values for the three Kim et al. docking hit lists are published only as figures and were not read.",
                "Kawano et al. 2026 report a measured 70% hit rate (28 of 40) at 10 uM for Boltz-2 on an Enamine diversity set, with no docking arm and after score and diversity filtering from a pre-curated library; the authors state it is not an unbiased estimate. It was not extracted in this pass.",
                "DockM8 (Hamza et al. 2026) reports median relative enrichment across DEKOIS 2.0, DUD-E and LIT-PCBA with an AVE-split generalisation check, and Lam et al. 2024 report a sequence-only screening model with a homology-removed zero-shot arm. Neither was extracted; both carry docking baselines on the same data.",
                "CACHE #1 and #2 are not open access and were not retrieved, so two of the three rounds of the best prospective benchmark are missing and nothing here shows whether the CACHE #3 ordering holds across targets.",
                "The paper relating library size and number tested to hit rate (doi 10.1038/s41589-024-01797-w) is not open access and was not retrieved, so the second half of the question, how many compounds must be tested, rests only on the tested denominators recorded here.",
                "No compute-per-compound figure is recorded for any docking tool, so the cost comparison between co-folding and docking is one-sided.",
                "The DEKOIS 2.0, LIT-PCBA and TocoDecoy primary papers are closed access and were not retrieved; their composition is recorded as Shen et al. 2025 and the official LIT-PCBA page describe it.",
                "Qualified human scientific review is outstanding; automated transcription does not establish replication.",
            ],
            "search_terms": [
                "virtual screening",
                "enrichment factor",
                "hit rate",
                "decoy",
                "DEKOIS",
                "LIT-PCBA",
                "DUD-E",
                "docking",
                "co-folding",
                "Boltz-2",
                "AlphaFold3",
                "CACHE challenge",
                "ultra-large library",
            ],
            "citation_locators": [
                {"source_id": src_id("shen2025"), "locator": "Tables 1-5; Methods 'Datasets' and 'Evaluation metrics'"},
                {"source_id": src_id("kim2026"), "locator": "Results 'Co-folding struggles to reliably re-rank docking hit lists'; Methods 'Benchmarking co-folding on experimentally validated compounds'"},
                {"source_id": src_id("cache3"), "locator": "Results; Figure 6 caption; Table 2"},
                {"source_id": src_id("cache3_si002"), "locator": "Sheet 'S8'"},
                {"source_id": src_id("litpcba_audit"), "locator": "Abstract"},
            ],
            "collection_plan": {
                "status": "planned",
                "comparison_question": "On one library whose negatives were all assayed, and on targets whose structures and ligands postdate every method's training data, does any machine-learning score rank true actives above the compounds a docking screen already ranked highly?",
                "baselines": [
                    "AutoDock Vina and Glide SP on the same library and target",
                    "A ligand-similarity search (ECFP4 nearest neighbour to known actives) on the same library",
                ],
                "outcomes": [
                    "Enrichment factor at 0.5%, 1% and 5% with the actives-to-inactives ratio recorded",
                    "Confirmed hits among a fixed number of top-ranked compounds, with the denominator",
                    "Compute seconds per compound on named hardware",
                ],
                "validation_requirements": [
                    "Negatives that were assayed, not generated",
                    "Targets and ligands dated after every scored model's training cutoff",
                    "The same library, target and receptor preparation for every arm",
                    "A ligand-similarity baseline alongside docking",
                ],
                "next_step": "Extract the DockM8 relative-enrichment tables and the Lam et al. 2024 zero-shot rows, which already carry docking baselines on DEKOIS 2.0, DUD-E and LIT-PCBA, before considering a Rewire run.",
            },
            "evidence_checked": {
                "date": DATE,
                "cutoff_date": DATE,
                "records": [
                    "data/omics/lit-search-20261022-uc-hitdisc/report.md",
                    "data/omics/use-case-coverage-hitdisc-20261022/research.md",
                    "data/omics/search-ledger.jsonl",
                ],
            },
            "review": review(
                ["scope-review"],
                "Drafted by the extraction agent. Not reviewed: a separate review-evidence pass must check the question, decision, inputs, output, exclusions and gaps against the cited sources and the linked protocols.",
            ),
        },
        links=links,
        facets={"areas": AREAS, "contexts": ["research"]},
    )
    for j in JUDGEMENTS:
        pid = f"{PREFIX}-protocol-{j['pid']}"
        sources = [src_id("shen2025")] if j["pid"].startswith("shen") else []
        if j["pid"].startswith("kim"):
            sources = [src_id("kim2026")]
        if j["pid"].startswith("cache3"):
            sources = [src_id("cache3_si002"), src_id("cache3")]
        if j["pid"] == "shen-litpcba5":
            sources = [src_id("shen2025"), src_id("litpcba_audit"), src_id("litpcba_page")]
        rec(
            f"{PREFIX}-use-case-mapping-{j['pid']}",
            "claim",
            f"Relevance of {pid} to {UC_ID}",
            "Relevance judgement drafted by the extraction agent. Not reviewed.",
            "needs_review",
            sources,
            {
                "field": f"links:assessed_by:{pid}",
                "value": pid,
                "relevance": j["relevance"],
                "endpoint": j["endpoint"],
                "rationale": j["rationale"],
                "constraints": COMMON_CONSTRAINTS,
                "limitations": j["extra_limits"] + COMMON_LIMITS,
                "citation_locators": [{"source_id": s, "locator": "See the protocol record's source_locator"} for s in sources],
                "source_locator": f"{pid}: see its source_locator",
                "headline_metric": "runtime" if j["pid"] == "shen-speed" else ("count" if j["pid"].startswith("cache3") else ("auroc" if j["pid"].startswith("kim") else "enrichment-factor")),
                "comparison_group": j["group"],
                "comparison_title": j["title"],
                "stratum_label": j["stratum"],
                "stratum_order": j["order"],
                "reason": "Hit-discovery use-case pass 2026-10-22: relevance of a protocol to a new use case (rewire-benchmark-data #177).",
                "review": review(
                    ["scope-review"],
                    "Judgement drafted by the extraction agent, not reviewed. A separate review-evidence pass must check the endpoint against the use case's question and list the evaluations it checked in reviewed_evaluations.",
                ),
            },
            links=[{"relation": "subject", "target_id": UC_ID}],
            facets={},
        )
    rec(
        f"{PREFIX}-use-case-summary",
        "claim",
        f"Summary of the evidence for {UC_ID}",
        "Draft summary of what the extracted evidence shows. Descriptive only, not reviewed.",
        "needs_review",
        [src_id("shen2025"), src_id("kim2026"), src_id("cache3"), src_id("cache3_si002"), src_id("litpcba_audit")],
        {
            "field": "summary",
            "value": (
                "Three sources in this store score machine-learning and co-folding methods against docking on the "
                "same screening data, and what the numbers say depends on how the negatives were built.\n\n"
                "On DEKOIS 2.0, whose 79 targets each pair 40 validated actives with 1,200 property-matched decoys "
                "selected from ZINC (1:30), the co-folding confidence scores enrich strongly and beat the docking "
                "arms. AF3 min-iPAE gives a mean EF1% of 23.15 and Boltz-2 min-iPAE 22.73, against 12.01 for the "
                "Glide SP row quoted from another paper, 5.16 for Gnina Vina and 2.94 for TankBind; the best "
                "rescoring of a co-folded pose, RTMScore on AF3 poses, reaches 21.34. The authors flag their own "
                "Boltz-2 affinity arms (mean EF1% 23.54 and 25.84) as likely over-estimates because Boltz-2 drew "
                "affinity data from the same public databases that source DEKOIS 2.0.\n\n"
                "On GPCRrecent, 16 targets whose first crystal structures were released after 2022 with decoys "
                "generated by a conditional recurrent neural network at 1:50, every value falls and the margin "
                "narrows: Boltz-2 min-iPAE gives a mean EF1% of 13.96 against 5.02 for Glide SP and 3.65 for Gnina "
                "Vina. On the five LIT-PCBA targets where the inactives were experimentally measured, the margin "
                "largely disappears: averaged over the five targets Boltz-2 min-iPAE gives EF1% 9.30 and NEF1% "
                "0.100 against Glide SP's 6.79 and 0.079, and on TP53 both Boltz-2 scores give EF1% 0.00 while "
                "Protenix ipTM gives 5.00 and Glide SP 3.75. A separate audit of LIT-PCBA reports 323 active "
                "training-validation analogue pairs at ECFP4 Tanimoto at or above 0.6 in ALDH1 alone and 2,491 "
                "2D-identical inactives shared between training and validation across targets, and concludes that a "
                "parameter-free memorisation baseline matches or exceeds published deep-learning results there, so "
                "every LIT-PCBA value above carries that limit.\n\n"
                "Where the negatives are compounds a docking screen already ranked highly and every compound was "
                "synthesised and assayed, the ordering changes. On the AmpC list (247 inhibitors among 1,293 tested "
                "compounds from a 1.7-billion molecule screen) DOCK3.7 separates binders best, AUC 76.5, against "
                "68.1 for Boltz-2 pIC50 and 60.5 for AF3 L-pLDDT. On the dopamine D4 list (205 binders among 541) "
                "docking and Boltz-2 are indistinguishable at the precision printed (both about 71) and AF3 "
                "L-pLDDT is worse than random at 46.4. Only on the sigma-2 list (201 binders among 506) does a "
                "co-folding score lead, Boltz-2 pIC50 at 83.8 against DOCK3.7's 78.8, with AF3 L-pLDDT at 56.1.\n\n"
                "In the one blinded prospective challenge, CACHE #3 on the SARS-CoV-2 Nsp3 macrodomain, 23 "
                "workflows selected 1,739 compounds that were synthesised and assayed; 28 advanced to hit "
                "expansion and 29 confirmed hits scored above 15, four of them judged chemically novel. Twelve of "
                "the 23 workflows returned no confirmed hit from their own selection of 41 to 99 compounds. When "
                "every workflow was applied to the same merged 1,739-compound library, WF1696, which the article "
                "describes as a purely physics-based method, captured 2 of the 4 Tier 1 and 9 of the 25 Tier 2 "
                "confirmed hits from 99 predicted actives, which the authors report as significantly more hits than "
                "any other workflow.\n\n"
                "Cost bounds all of this: co-folding one protein-ligand pair takes 7.79 to 34.58 seconds per "
                "compound on one NVIDIA H100 with pre-computed MSAs, which is why the LIT-PCBA arm covers five "
                "targets rather than fifteen. No docking tool was timed on the same hardware, no "
                "ligand-similarity or pharmacophore baseline is scored anywhere in this batch, and no result here "
                "estimates the hit rate of an untested library."
            ),
            "source_locator": "Shen et al. 2025 Tables 1-5; Kim, Correy, Hall et al. 2026 Results; Herasymenko et al. 2026 Results and sheet S8; arXiv:2507.21404v2 Abstract",
            "citation_locators": [
                {"source_id": src_id("shen2025"), "locator": "Tables 1, 2, 3, 4 and 5"},
                {"source_id": src_id("kim2026"), "locator": "Results 'Co-folding struggles to reliably re-rank docking hit lists'"},
                {"source_id": src_id("cache3"), "locator": "Results 'Discovering Chemically Novel Ligands Was Challenging' and 'Trends and Strategies from the Best Performing Computational Workflows'"},
                {"source_id": src_id("cache3_si002"), "locator": "Sheet 'S8'"},
                {"source_id": src_id("litpcba_audit"), "locator": "Abstract"},
            ],
            "reason": "Hit-discovery use-case pass 2026-10-22 (rewire-benchmark-data #177).",
            "review": review(
                ["scope-review"],
                "Drafted by the extraction agent, not reviewed. A separate review-evidence pass must check every number against a result record in this batch before this summary can be published.",
            ),
        },
        links=[{"relation": "subject", "target_id": UC_ID}],
        facets={},
    )


# --------------------------------------------------------------------------------------
# Driver
# --------------------------------------------------------------------------------------

GAPS = [
    "Shen et al. 2025 Table 6 (pose analysis) was not extracted: pose plausibility is outside this use case's endpoint.",
    "Shen et al. 2025 Figures 1 to 5 and S1 to S17, including the ligand-similarity leakage analysis (Figure 5 and Fig. S10) and the per-target composition tables S1 and S2, were not extracted. The similarity analysis is the authors' leakage control for DEKOIS 2.0 and is published as figures.",
    "Eight of the 24 arms in Shen et al. Table 1 are values quoted from refs 34, 35, 36, 38 and 39. None of those papers was retrieved, so no evaluation of those tools is independent of this compilation.",
    "Kim et al. 2026: the hit-rate curves (Figure 5-figure supplement 4), the semi-logarithmic ROC curves and early enrichment (Figure 5-figure supplement 3) and the per-target score distributions (Figure 5a-c) are figures and were not read. Supplementary file 5 (tested compound lists) was not downloaded.",
    "Kim et al. 2026: the Mac1 pose arm (551 complexes, Figures 2 and 3) is deliberately excluded on endpoint grounds, as are the per-group score medians and the Pearson correlations of score against pKi.",
    "CACHE #3: per-workflow hit rates are not printed anywhere in the article or table S8. The article's own hit-rate definition (confirmed actives divided by compounds predicted active) applies to the merged-library arm, and Figure 6b is an aggregated activity score, not a hit rate. The literature-search report described Figure 5b as a per-workflow hit rate; in the published version the relevant figure is Figure 6 and panel b is the aggregated score.",
    "CACHE #3: sheets S1 to S7 of ci5c02441_si_002.xlsx, the second workbook ci5c02441_si_003.xlsx and the Supporting Information PDF were retrieved but not extracted.",
    "CACHE #1 and #2 results papers (doi 10.1021/acs.jcim.4c01267 and 10.1021/acs.jcim.5c00535) are not open access and were not retrieved.",
    "The LIT-PCBA leakage audit's own tables were not retrieved: only the arXiv abstract page was read, so the memorisation baseline's per-target enrichment values are not recorded.",
    "TocoDecoy (doi 10.1021/acs.jmedchem.2c00460), DEKOIS 2.0 (doi 10.1021/ci400115b), DEKOIS 1.0 (doi 10.1021/ci2001549) and the LIT-PCBA primary paper (doi 10.1021/acs.jcim.0c00155) are closed access and were not retrieved. DEKOIS 2.0 and TocoDecoy are registered from Shen et al. 2025's description of them.",
    "No evaluation on DUD-E or MF-PCBA is recorded; both are registered as discovered benchmarks only.",
    "Kawano et al. 2026 (Boltz-2 prospective 70% hit rate), Hamza et al. 2026 (DockM8 relative enrichment), Lam et al. 2024 (BIND sequence-only screening), Agha et al. 2026 (MolDockLab), Furui and Ohue (Boltzina and Boltz-2 affinity-head fine-tuning), Luttens et al. 2025 and Wang and Kireev 2026 were identified in the search pass and not extracted in this pass.",
    "No ligand-similarity or pharmacophore baseline is scored on any protocol here, so issue #177's pre-machine-learning comparator is only half met: docking is present, ligand similarity is not.",
    "relative-enrichment-factor and forward-screening-success-rate were not added to data/vocab/metric.ttl: no cell extracted here uses them. DockM8's REF formula was not read, so it must not be merged with normalized-enrichment-factor.",
    "hit-rate was not added to data/vocab/metric.ttl: no source extracted here prints a hit rate, so there was no cell that needed the concept.",
]


def write_outputs() -> None:
    by_id: dict[str, dict] = {}
    for r in RECORDS:
        if r["id"] in by_id:
            raise SystemExit(f"duplicate record id {r['id']}")
        by_id[r["id"]] = r
    ordered = [by_id[k] for k in sorted(by_id)]
    with open(os.path.join(BATCH_DIR, "batch.jsonl"), "w", encoding="utf-8") as fh:
        for r in ordered:
            fh.write(json.dumps(r, ensure_ascii=False, sort_keys=False) + "\n")
    with open(os.path.join(BATCH_DIR, "claims.csv"), "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["record_id", "source_id", "locator", "printed_value", "review_scope"])
        w.writeheader()
        for row in sorted(CLAIM_ROWS, key=lambda r: r["record_id"]):
            w.writerow(row)
    counts: dict[str, int] = {}
    for r in ordered:
        counts[r["kind"]] = counts.get(r["kind"], 0) + 1
    coverage = {
        "batch": "use-case-coverage-hitdisc-20261022",
        "issue": "rewire-benchmark-data#177",
        "use_case": UC_ID,
        "built_at": DATE,
        "built_by": "Claude extraction agent; no human review claimed",
        "record_counts": counts,
        "total_records": len(ordered),
        "reused_ids": sorted(set(REUSED.values())),
        "reused_id_roles": {
            "discovery-model-alphafold-3": "parent model of the AF3 screening-score configurations",
            "catalog-model-boltz-2": "parent model of the Boltz-2 screening-score configurations",
            "ucc-research-model-protenix": "parent model of the Protenix screening-score configurations",
            "discovery-model-boltz": "Boltz model family; recorded as reused context, not linked by this batch",
            "discovery-model-autodock-vina": "AutoDock Vina method; the Vina scoring function is reached here through Gnina, so no configuration links to it",
            "reported-task-a7803ecf7708cc": "protein-ligand virtual screening task, linked by evaluates_task from every protocol in this batch",
        },
        "ids_considered_and_not_used": {
            "reported-model-1e51ccbfd2de61": "Vina configuration from the CASF-2016 screening work; its protocol and data differ from every protocol here, so it is not reused",
            "reported-model-6c0bc8d297cc7a": "DiffDock-NMDN pipeline; no source in this batch scores it",
            "reported-dataset-065b9fcc8da573": "CASF-2016 blind docked poses; a pose dataset, outside this use case's endpoint",
        },
        "vocabulary_added": {
            "enrichment-factor": "Shen et al. 2025 Tables 1-4",
            "normalized-enrichment-factor": "Shen et al. 2025 Table 4 and its footnote a",
            "bedroc": "Shen et al. 2025 Tables 1-3",
            "cache-challenge-activity-score": "Herasymenko et al. 2026 table S8 columns G, H and J",
            "cache-challenge-novelty-score": "Herasymenko et al. 2026 table S8 column I",
            "cache-challenge-normalized-hit-score": "Herasymenko et al. 2026 table S8 columns R, S and the unnamed final column",
        },
        "vocabulary_not_added": {
            "hit-rate": "No source extracted here prints a hit rate with a denominator and threshold",
            "relative-enrichment-factor": "DockM8 was not extracted and its formula was not read; it must not be merged with normalized-enrichment-factor",
            "forward-screening-success-rate": "Lam et al. 2024 Table 1 was not extracted; casf-screening-success-rate already covers the CASF-2016 form of this measure",
            "normalized-log-auc": "The Kim et al. normalised logAUC values belong to the Mac1 pose arm, which is outside this use case",
        },
        "tables_extracted": [
            {"source": src_id("shen2025"), "locator": "Table 1", "cells": 240, "note": "24 arms x 10 columns"},
            {"source": src_id("shen2025"), "locator": "Table 2", "cells": 230, "note": "13 Protenix and 10 AF3 arms x 10 columns"},
            {"source": src_id("shen2025"), "locator": "Table 3", "cells": 160, "note": "16 arms x 10 columns"},
            {"source": src_id("shen2025"), "locator": "Table 4", "cells": 84, "note": "7 arms x 12 columns"},
            {"source": src_id("shen2025"), "locator": "Table 5", "cells": 36, "note": "6 rows x 6 columns"},
            {"source": src_id("kim2026"), "locator": "Results, body text AUC values for the sigma-2, D4 and AmpC hit lists", "cells": 9, "note": "no table carries these values; they are printed in the text"},
            {"source": src_id("cache3_si002"), "locator": "Sheet 'S8'", "cells": 332, "note": "23 workflows; 7 own-selection columns for all 23 and 9 merged-library columns for 19"},
        ],
        "gaps": GAPS,
        "reviewer_must_judge": [
            "Whether the ipTM and Min-iPAE rows reprinted in Shen et al. Table 2 should be kept as separate results from their Table 1 twins. This batch keeps them, because they are printed cells of a table it extracted in full, and marks them with a source warning.",
            "Whether a per-target column should become its own evaluation with a dataset subset. This batch keeps one evaluation per configuration and protocol and distinguishes per-target cells by metric_qualifier and source_locator, for Shen et al. Tables 4 and 5.",
            "Whether the CACHE #3 workflows should be configuration records with no parent entity. This batch does that, because their computational steps appear only in figures and no primary source describes each workflow.",
            "Whether the three cache-challenge-* metric concepts are the right granularity, or whether the activity score and the normalised score should be split further.",
            "printed_value for every cell taken from the CACHE workbook is the shortest decimal that round-trips to the stored double, not the string the spreadsheet displays through its number format. raw_xml_value keeps the stored string for each.",
            "The relevance of the CACHE #3 own-selection arm: it is prospective and wet-lab confirmed, but each workflow chose its own compounds, so it is recorded as direct with that confound as its first limitation.",
            "Whether the GPCRrecent six-target protocol earns a judgement at all, given that only two Boltz-2 arms ran on it and there is no baseline within the protocol.",
        ],
    }
    with open(os.path.join(BATCH_DIR, "coverage.json"), "w", encoding="utf-8") as fh:
        json.dump(coverage, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    print(f"{len(ordered)} records")
    for kind in sorted(counts):
        print(f"  {kind}: {counts[kind]}")
    print(f"claims.csv rows: {len(CLAIM_ROWS)}")


def main() -> None:
    cache_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "artifacts-cache")
    data = {key: fetch(key, cache_dir) for key in ARTIFACTS}
    build_sources()
    build_methods()
    build_benchmarks_and_data()
    build_configurations()
    build_protocols()
    build_shen(data["shen2025"])
    build_kim(data["kim2026"])
    build_cache3(data["cache3_si002"])
    build_claims()
    build_use_case()
    write_outputs()


if __name__ == "__main__":
    main()
