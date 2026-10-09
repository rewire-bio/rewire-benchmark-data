"""Deterministic extraction of DNA pathogen-identification workflow comparisons into a records batch.

Usage: python3 -I extract_pathogen.py <portik-xml> <song-xml> <hall-xml> <batch-dir>

Reads three pinned Europe PMC full-text XML files, rebuilds each chosen table as a grid
(row and column spans expanded), asserts every row and column label it depends on, and
writes batch.jsonl (store form) and claims.csv. Every cell of each chosen table becomes a
result, a claim or (for Song et al. Table 1, column "Theoretical") a dataset claim.
printed_value is the cell text exactly as it appears in the XML.
"""
import csv, hashlib, json, re, sys
import xml.etree.ElementTree as ET
from decimal import Decimal

PORTIK_XML, SONG_XML, HALL_XML, BATCH = sys.argv[1:5]
P = "dna-pathogen-20261009"
UC = "use-case-diagnostic-dna-pathogen-identification"
EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest"
DATE = "2026-10-09"
MICRO = {"areas": ["microbes-communities"], "contexts": ["clinical_research"]}
EXTRACT_NOTE = ("Extracted by deterministic parse of the pinned Europe PMC full-text XML (extract/extract_pathogen.py), "
                "with every row and column label asserted. printed_value is the table cell text exactly as in the XML. "
                "Pending independent review.")
records, claims_rows = [], []


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def rec(id_, kind, name, description, source_ids, links=None, attributes=None, facets=None, status="needs_review"):
    r = {"id": id_, "kind": kind, "name": name, "description": description, "status": status,
         "facets": MICRO if facets is None else facets, "source_ids": source_ids,
         "links": links or [], "attributes": attributes or {}}
    records.append(r)
    return r


def review(note=EXTRACT_NOTE, method=("deterministic-table-parse",), artifact=None, url=None):
    r = {"method": list(method), "reviewer": ["claude"],
         "reviewer_note": "Claude (Opus 5.5) research agent, the extractor; no independent or human review claimed",
         "date": DATE, "note": note}
    return r


# ---------------------------------------------------------------- table grid
def txt(e):
    return " ".join("".join(e.itertext()).split())


def table_grid(xml_path, table_id):
    """Rows of cell texts for one table-wrap, with rowspan and colspan expanded."""
    root = ET.parse(xml_path).getroot()
    tw = next(t for t in root.iter("table-wrap") if t.get("id") == table_id)
    grid, pending = [], {}  # pending[col] = (text, rows_left)
    for tr in tw.iter("tr"):
        row, col = [], 0
        cells = [c for c in tr if c.tag in ("td", "th")]
        ci = 0
        while ci < len(cells) or col in pending:
            if col in pending:
                text, left = pending[col]
                row.append(text)
                pending[col] = (text, left - 1)
                if pending[col][1] == 0:
                    del pending[col]
                col += 1
                continue
            c = cells[ci]; ci += 1
            text = txt(c)
            cs, rs = int(c.get("colspan") or 1), int(c.get("rowspan") or 1)
            for k in range(cs):
                row.append(text)
                if rs > 1:
                    pending[col] = (text, rs - 1)
                col += 1
        grid.append(row)
    caption = txt(tw.find("caption")) if tw.find("caption") is not None else ""
    foot = txt(tw.find("table-wrap-foot")) if tw.find("table-wrap-foot") is not None else ""
    return grid, caption, foot


def need(got, expected, where):
    if got != expected:
        raise SystemExit(f"Label check failed at {where}: expected {expected!r}, got {got!r}")


def number(printed):
    """Decimal string for a printed number; None when the cell is not a single number."""
    s = printed.replace("‐", "-").replace("−", "-").replace(",", "")
    if not re.fullmatch(r"-?\d+(\.\d+)?([eE]-?\d+)?", s):
        return None
    d = Decimal(s)
    out = format(d, "f")
    return out


# ---------------------------------------------------------------- records helpers
def result(id_, eval_id, source_id, locator, printed, metric, direction, unit, qualifier=None, unit_detail=None,
           uncertainty=None, extra=None, name=None):
    nv = number(printed)
    attrs = {"metric": metric, "metric_direction": direction, "unit": unit, "printed_value": printed,
             "numeric_value": nv, "source_locator": locator}
    if qualifier:
        attrs["metric_qualifier"] = qualifier
    if unit_detail:
        attrs["unit_detail"] = unit_detail
    if uncertainty:
        attrs["uncertainty"] = uncertainty
    else:
        attrs["missing_metadata"] = {"uncertainty": {"reason": "unreported"}}
    if extra:
        attrs.update(extra)
    attrs["review"] = review()
    rec(id_, "result", name or f"{eval_id.replace(P + '-eval-', '')} {metric}" + (f" ({qualifier})" if qualifier else ""),
        "Reported measurement transcribed from the pinned source. Not independently reproduced.",
        [source_id], [{"relation": "evaluation", "target_id": eval_id}], attrs, facets={})
    claims_rows.append([id_, source_id, locator, printed, "result"])


def claim(id_, subject, field, value, source_id, locator, name=None):
    rec(id_, "claim", name or f"{field}: {subject}", "Descriptive fact transcribed from the pinned source.", [source_id],
        [{"relation": "subject", "target_id": subject}],
        {"field": field, "value": value, "source_locator": locator,
         "review": review("Transcribed from the pinned article XML text. Pending independent review.", ("transcription",))},
        facets={})
    claims_rows.append([id_, source_id, locator, value, "claim"])


def evaluation(id_, name, system, protocol, dataset, source_id, origin, comparison, locator, extra=None, missing=None):
    attrs = {"origin": origin, "protocol": protocol, "version": f"Primary source as retrieved {DATE}",
             "comparison": {"protocol_id": protocol, **comparison}, "source_locator": locator}
    if missing:
        attrs["missing_metadata"] = missing
    if extra:
        attrs.update(extra)
    rec(id_, "evaluation", name, "Published DNA metagenomic classification comparison; transcribed, not reproduced.",
        [source_id], [{"relation": "system", "target_id": system}, {"relation": "assessment", "target_id": protocol},
                      {"relation": "data", "target_id": dataset}], attrs)


def method(id_, name, description, source_id, locator, kind="method", entity_level="method", access=None):
    attrs = {"reported_name": name, "entity_level": entity_level}
    if kind == "method":  # the service kind declares neither key
        attrs["source_locator"] = locator
        attrs["missing_metadata"] = {"version": {"reason": "inapplicable", "note": "Family record; versions are on configurations"}}
    if access:
        attrs["access"] = access
    facets = {**MICRO, "method_types": ["conventional_pipeline"]}
    rec(id_, kind, name, description, [source_id], [], attrs, facets=facets)


def configuration(id_, name, description, of, source_id, reported_name, locator, version=None, version_missing=None,
                  parameters=None, extra=None):
    attrs = {"reported_name": reported_name, "source_locator": locator, "foundation_model_eligible": False}
    if version:
        attrs["version"] = version
    else:
        attrs["missing_metadata"] = {"version": version_missing}
    if parameters:
        attrs["parameters"] = parameters
    if extra:
        attrs.update(extra)
    rec(id_, "configuration", name, description, [source_id], [{"relation": "configuration_of", "target_id": of}], attrs,
        facets={**MICRO, "method_types": ["conventional_pipeline"]})


def source(id_, name, doi, pmcid, path, version, retrieved, venue, year, extra=None):
    attrs = {"url": f"https://doi.org/{doi}", "artifact_url": f"{EPMC}/{pmcid}/fullTextXML", "version": version,
             "retrieved_at": retrieved, "artifact_sha256": sha(path), "doi": doi, "publication_status": "peer_reviewed",
             "licence": "CC-BY-4.0", "media_type": "application/xml", "venue": venue, "year": year,
             "source_locator": "Licence statement in the article XML <license> element: Creative Commons Attribution 4.0"}
    attrs.update(extra or {})
    rec(id_, "source", name, "Primary source retrieved and hashed for the DNA pathogen-identification use-case pass.",
        [], [], attrs)


# ================================================================= sources
SRC_PORTIK, SRC_SONG, SRC_HALL = f"{P}-source-portik2022", f"{P}-source-song2025", f"{P}-source-hall2024"
source(SRC_PORTIK, "Evaluation of taxonomic classification and profiling methods for long-read shotgun metagenomic sequencing datasets",
       "10.1186/s12859-022-05103-0", "PMC9749362", PORTIK_XML,
       "BMC Bioinformatics 23:541, published 2022-12-13; PMC9749362 full-text XML", "2026-10-09T19:45:04Z",
       "BMC Bioinformatics", 2022)
source(SRC_SONG, "Diagnostic Accuracy of Shotgun Metagenomics for Bloodstream Infections Is Influenced by Bioinformatics Workflow Selection",
       "10.1002/mbo3.70158", "PMC12705909", SONG_XML,
       "MicrobiologyOpen 14(6):e70158, published online 2025-12-15; PMC12705909 full-text XML", "2026-10-09T19:48:48Z",
       "MicrobiologyOpen", 2025)
source(SRC_HALL, "Pangenome databases improve host removal and mycobacteria classification from clinical metagenomic data",
       "10.1093/gigascience/giae010", "PMC10993716", HALL_XML,
       "GigaScience 13:giae010, published online 2024-04-04; PMC10993716 full-text XML", "2026-10-09T19:55:15Z",
       "GigaScience", 2024)

# ================================================================= methods (reused and new)
KRAKEN2 = "catalog-model-kraken2"        # existing; discovery-model-kraken-2 is a duplicate family record
METAPHLAN = "catalog-model-metaphlan"    # existing
MMSEQS2 = "discovery-model-mmseqs2"      # existing
M = {}
for key, name, desc, src, loc in [
    ("bracken", "Bracken", "Bayesian re-estimation of species abundance from Kraken2 read assignments.", SRC_PORTIK, "Table 2; Methods 'Bracken'"),
    ("centrifuge", "Centrifuge", "Read classifier using a Burrows-Wheeler transform and FM-index of reference genomes.", SRC_PORTIK, "Table 2; Methods 'Centrifuge'"),
    ("motus2", "mOTUs2", "Marker-gene profiler based on single-copy phylogenetic marker genes.", SRC_PORTIK, "Table 2; Methods 'mOTUs2'"),
    ("sourmash", "sourmash", "FracMinHash k-mer sketching with minimum metagenome cover (gather) and taxonomic aggregation.", SRC_PORTIK, "Table 2; Methods 'Sourmash'"),
    ("metamaps", "MetaMaps", "Long-read classifier using approximate mapping to a reference database.", SRC_PORTIK, "Table 2; Methods 'MetaMaps'"),
    ("megan-lr", "MEGAN-LR", "Long-read lowest-common-ancestor binning in MEGAN6 community edition after protein (DIAMOND) or nucleotide (minimap2) alignment.", SRC_PORTIK, "Table 2; Methods 'MEGAN-LR-prot' and 'MEGAN-LR-nuc'"),
    ("blast", "BLAST (BLASTn)", "Heuristic nucleotide alignment to the NCBI nt database.", SRC_SONG, "Methods 'Data Analysis' paragraph 1; Discussion paragraph 3"),
    ("kraken", "Kraken", "Exact k-mer classifier with lowest common ancestor assignment, cited as Wood and Salzberg 2014.", SRC_SONG, "Methods 'Data Analysis' paragraph 1"),
    ("rtg-core", "RTG Core", "Alignment-based metagenomic species estimation with a dynamic-programming edit-distance model.", SRC_SONG, "Methods 'Data Analysis' paragraph 1; Discussion paragraph 3"),
    ("minimap2", "minimap2", "Sequence aligner used here to classify reads by alignment to a chosen reference database.", SRC_HALL, "Methods 'Mycobacterium read classification' paragraphs 2-3"),
]:
    M[key] = f"{P}-method-{key}"
    method(M[key], name, desc, src, loc)
M["bugseq"] = f"{P}-service-bugseq"
method(M["bugseq"], "BugSeq", "Hosted long-read metagenomic classification platform (bugseq.com).", SRC_PORTIK,
       "Table 2; Methods 'BugSeq'", kind="service", entity_level="service",
       access="Hosted web platform; the source uploaded datasets at https://bugseq.com and selected the NCBI nt reference database option.")

# ================================================================= Portik et al. 2022, Table 4
grid, caption, foot = table_grid(PORTIK_XML, "Tab4")
need(caption, "Species-level detection results based on the minimum 0.001% of total reads threshold", "Portik Table 4 caption")
need(grid[0], ["Dataset", "Method type", "Profiling method", "True positives", "False positives", "False negatives",
               "Precision", "Recall", "F1", "F0.5", "L1"], "Portik Table 4 header")
need(foot.startswith("*Two species were unavailable in several reference databases for HiFi Zymo D6331"), True, "Portik Table 4 footnote")
body = grid[1:]
need(len(body), 70, "Portik Table 4 body row count")
LONG = ["Kraken2", "Bracken", "Centrifuge-h22", "Centrifuge-h500", "MetaPhlAn3", "mOTUs", "Sourmash-k31", "Sourmash-k51",
        "MetaMaps", "MMseqs2", "MEGAN-LR-Prot", "MEGAN-LR-Nuc-HiFi", "MEGAN-LR-Nuc-ONT", "BugSeq-V2"]
ILL_ATCC = ["Kraken2", "Bracken", "Centrifuge-h22", "MetaPhlAn3", "mOTUs", "Sourmash-k31", "Sourmash-k51"]
ILL_ZYMO = ILL_ATCC
BLOCKS = [  # key, dataset label, first row index, expected methods, star (footnote) applies
    ("hifi-atcc-msa1003", "HiFi ATCC MSA1003", 0, LONG),
    ("illumina-atcc-msa1003", "Illumina ATCC MSA1003 (20 species, staggered)", 14, ILL_ATCC),
    ("hifi-zymo-d6331", "HiFi Zymo D6331 (17 species, staggered)", 21, LONG),
    ("ont-r10-zymo-d6300", "ONT R10 Zymo D6300 (10 species, even)", 35, LONG),
    ("ont-q20-zymo-d6300", "ONT Q20 Zymo D6300 (10 species, even)", 49, LONG),
    ("illumina-zymo-d6300", "Illumina Zymo D6300 (10 species, even)", 63, ILL_ZYMO),
]
need([body[0][0], body[1][0]], ["HiFi ATCC MSA1003", "(20 species, staggered)"], "Portik Table 4 first dataset label (split across two cells)")
for key, label, start, methods in BLOCKS:
    if key != "hifi-atcc-msa1003":
        need(body[start][0], label, f"Portik Table 4 dataset label row {start + 2}")
    for i, m in enumerate(methods):
        row = body[start + i]
        need(len(row), 11, f"Portik Table 4 row {start + i + 2} width")
        need(row[2].rstrip("*"), m, f"Portik Table 4 row {start + i + 2} method")
        if key == "hifi-zymo-d6331":
            need(row[2].endswith("*"), m not in ("mOTUs", "Sourmash-k31", "Sourmash-k51"), f"Portik Table 4 row {start + i + 2} asterisk")

# configurations
PC = {}
pcfg = [
    ("Kraken2", "kraken2-2-1-1-pluspf", KRAKEN2, "Kraken2", "2.1.1", "Database 'PlusPF' (pre-built, released 2021-01-27). Command: kraken2 --db PlusPF --threads 24 --report SAMPLE.kreport.txt SAMPLE.fasta", "Table 2 row Kraken2; Methods 'Kraken2' and 'Reference databases' paragraph 2"),
    ("Bracken", "bracken-2-6-0-pluspf", M["bracken"], "Bracken", "2.6.0", "Run on Kraken2 kreport outputs, database 'PlusPF', species level: bracken -d PlusPF -r 50 -l S -t 10", "Table 2 row Bracken; Methods 'Bracken'"),
    ("Centrifuge-h22", "centrifuge-1-0-4-h22-abvf", M["centrifuge"], "Centrifuge-h22", "1.0.4", "RefSeq archaea, bacteria, viruses and fungi database built 2021-04 with centrifuge-build; --min-hitlen 22 -k 20", "Table 2 row Centrifuge (variation h22); Methods 'Centrifuge' paragraphs 1-5"),
    ("Centrifuge-h500", "centrifuge-1-0-4-h500-abvf", M["centrifuge"], "Centrifuge-h500", "1.0.4", "Same database as Centrifuge-h22; --min-hitlen 500 -k 20", "Table 2 row Centrifuge (variation h500); Methods 'Centrifuge' paragraphs 3, 6-7"),
    ("MetaPhlAn3", "metaphlan-3-0-7-mpa-v30-201901", METAPHLAN, "MetaPhlAn3", "3.0.7", "Database mpa_v30_CHOCOPhlAn_201901; alignments made externally with bowtie2 --local, then metaphlan --input_type sam", "Table 2 row MetaPhlAn3; Methods 'MetaPhlAn3'"),
    ("mOTUs", "motus2-3-0-3", M["motus2"], "mOTUs", "mOTUs2 v3.0.3 (database version 3.0.3)", "Long reads converted with motus prep_long, then motus profile -c", "Table 2 row mOTUs2; Methods 'mOTUs2' and 'Reference databases' paragraph 3"),
    ("Sourmash-k31", "sourmash-4-5-1-k31-genbank-2022-03", M["sourmash"], "Sourmash-k31", "4.5.1", "GenBank 2022.03 pre-built databases (bacteria, archaea, viral, protozoa, fungi), scaled 1000, k = 31; sourmash gather then sourmash tax metagenome", "Table 2 row sourmash (variation k31); Methods 'Sourmash' and 'Reference databases' paragraph 5"),
    ("Sourmash-k51", "sourmash-4-5-1-k51-genbank-2022-03", M["sourmash"], "Sourmash-k51", "4.5.1", "As Sourmash-k31 with k = 51", "Table 2 row sourmash (variation k51); Methods 'Sourmash'"),
    ("MetaMaps", "metamaps-0-1-miniseq-h", M["metamaps"], "MetaMaps", "0.1", "Pre-built MiniSeq + H database (12,058 complete RefSeq genomes); metamaps mapDirectly then classify", "Table 2 row MetaMaps; Methods 'MetaMaps' and 'Reference databases' paragraph 4"),
    ("MMseqs2", "mmseqs2-13-45111-nr", MMSEQS2, "MMseqs2", "13.45111", "NCBI nr (downloaded 2021-04); mmseqs easy-taxonomy", "Table 2 row MMseqs2; Methods 'MMseqs2'"),
    ("MEGAN-LR-Prot", "megan-lr-prot-diamond-nr", M["megan-lr"], "MEGAN-LR-Prot", None, "DIAMOND alignment to NCBI nr (downloaded 2021-04), MEGAN6 community edition tools with megan-map-Jan2021.db, run through the PacBio pb-metagenomics-tools Taxonomic-Profiling-Diamond-Megan workflow", "Table 2 row MEGAN-LR-prot; Methods 'MEGAN-LR-prot'"),
    ("MEGAN-LR-Nuc-HiFi", "megan-lr-nuc-hifi-minimap2-nt", M["megan-lr"], "MEGAN-LR-Nuc-HiFi", None, "minimap2 (-k 19 -w 10 index) alignment to NCBI nt, at most 5 secondary alignments, MEGAN6 community edition, PacBio pb-metagenomics-tools Taxonomic-Profiling-Minimap-Megan workflow", "Table 2 row MEGAN-LR-nuc (variation HiFi); Methods 'MEGAN-LR-nuc' paragraphs 1-3"),
    ("MEGAN-LR-Nuc-ONT", "megan-lr-nuc-ont-minimap2-nt", M["megan-lr"], "MEGAN-LR-Nuc-ONT", None, "As MEGAN-LR-Nuc-HiFi but minimap2 index -k 15 -w 10 and -ax map-ont", "Table 2 row MEGAN-LR-nuc (variation ONT); Methods 'MEGAN-LR-nuc' paragraphs 4-7"),
    ("BugSeq-V2", "bugseq-v2-nt", M["bugseq"], "BugSeq-V2", "V2 (as printed in Table 2 and Table 4)", "Hosted BugSeq platform with the NCBI nt reference database option", "Table 2 row BugSeq-V2; Methods 'BugSeq'"),
]
for label, slug, of, rname, version, params, loc in pcfg:
    cid = f"{P}-config-portik2022-{slug}"
    PC[label] = cid
    vm = None if version else {"reason": "unreported", "note": "MEGAN6 community edition is named without a version number; workflow commit not printed in the article"}
    configuration(cid, f"{rname} (Portik et al. 2022)", f"{rname} as run in Portik et al. 2022.", of, SRC_PORTIK, rname, loc,
                  version=version, version_missing=vm, parameters=params)

PORTIK_BENCH = f"{P}-benchmark-portik2022-mock-communities"
DS_INFO = {
    "hifi-atcc-msa1003": ("HiFi ATCC MSA-1003 mock community (PacBio Sequel II HiFi)", "NCBI SRX6095783",
                          "ATCC MSA-1003: 20 bacterial species, staggered abundances (five species each at 18%, 1.8%, 0.18% and 0.02%). 2,419,037 HiFi reads, median length 8,310 bp, 20.54 Gb.",
                          "Table 1 row 'HiFi ATCC MSA-1003'; Methods 'Mock community datasets' paragraph 2", 20),
    "illumina-atcc-msa1003": ("Illumina ATCC MSA-1003 mock community (HiSeq 2500)", "NCBI SRX5169925",
                              "ATCC MSA-1003: 20 bacterial species, staggered abundances. 10,038,314 reads of 125 bp (pre-trimmed from 150 bp paired-end), 1.25 Gb.",
                              "Table 1 row 'Illumina ATCC MSA-1003'; Methods 'Mock community datasets' paragraph 4", 20),
    "hifi-zymo-d6331": ("HiFi ZymoBIOMICS D6331 gut microbiome standard (PacBio Sequel II HiFi)", "NCBI SRX9569057",
                        "ZymoBIOMICS D6331: 17 species (14 bacteria, 1 archaeon, 2 yeasts), staggered from 14% to 0.0001%; five E. coli strains treated as one species. 1,978,852 HiFi reads, median length 8,077 bp, 17.99 Gb.",
                        "Table 1 row 'HiFi Zymo D6331'; Methods 'Mock community datasets' paragraph 2", 15),
    "ont-r10-zymo-d6300": ("ONT R10.3 ZymoBIOMICS D6300 standard, length-filtered (GridION)", "https://lomanlab.github.io/mockcommunity/r10.html (R10.3 release, February 2020)",
                           "ZymoBIOMICS D6300: 10 species (8 bacteria at 12%, 2 yeasts at 2%). Reads under 2 kb and over 50 kb removed: 275,318 of 1.16 million reads kept, median length 6,664 bp, 3.31 Gb.",
                           "Table 1 row 'ONT R10 Zymo D6300'; Methods 'Mock community datasets' paragraph 3", 10),
    "ont-q20-zymo-d6300": ("ONT Q20 ZymoBIOMICS D6300 standard, length-filtered (PromethION)", "ENA ERR5396170",
                           "ZymoBIOMICS D6300: 10 species (8 bacteria at 12%, 2 yeasts at 2%). Reads under 2 kb and over 50 kb removed; 2,000,000 reads used, median length 4,160 bp, 9.61 Gb.",
                           "Table 1 row 'ONT Q20 Zymo D6300'; Methods 'Mock community datasets' paragraph 3", 10),
    "illumina-zymo-d6300": ("Illumina ZymoBIOMICS D6300 standard (NovaSeq 6000), subsampled", "NCBI SRX8824472",
                            "ZymoBIOMICS D6300: 10 species (8 bacteria at 12%, 2 yeasts at 2%). Subsampled to 20,000,000 of about 103 million 150 bp paired-end reads, 2.99 Gb.",
                            "Table 1 row 'Illumina Zymo D6300'; Methods 'Mock community datasets' paragraph 4", 10),
}
THRESH = {"hifi-atcc-msa1003": "24", "illumina-atcc-msa1003": "100", "hifi-zymo-d6331": "19", "ont-r10-zymo-d6300": "2",
          "ont-q20-zymo-d6300": "20", "illumina-zymo-d6300": "200"}
rec(PORTIK_BENCH, "benchmark", "Mock community taxonomic profiling benchmark (Portik et al. 2022)",
    "Eleven profiling methods (14 configurations) on PacBio HiFi, ONT and Illumina reads from ATCC and ZymoBIOMICS mock communities, scored on species detection and abundance.",
    [SRC_PORTIK], [], {"entity_level": "suite", "version": "BMC Bioinformatics 2022, Table 4",
                       "task": "Species-level presence detection and relative abundance estimation in mock microbial communities",
                       "source_locator": "Tables 1-4; Methods 'Detection metrics' and 'Relative abundance estimates'",
                       "scope_note": "Genus-level and higher-threshold results (Additional file 1 Tables S10-S16) and the shorter-read and simulated short-read variants are not extracted.",
                       "limitations": ["Mock communities of cultured organisms without human host DNA; not clinical specimens.",
                                       "Reference databases differ between methods (Table 2), so method and database effects are confounded."]})
P_ORDER = ["hifi-atcc-msa1003", "illumina-atcc-msa1003", "hifi-zymo-d6331", "ont-r10-zymo-d6300", "ont-q20-zymo-d6300", "illumina-zymo-d6300"]
PORTIK_PROTOCOLS = {}
for key, label, start, methods in BLOCKS:
    dname, acc, pop, dloc, nspecies = DS_INFO[key]
    did = f"{P}-data-portik2022-{key}"
    rec(did, "dataset", dname, "Public mock community sequencing run as used in Portik et al. 2022.", [SRC_PORTIK], [],
        {"version": f"As described in Portik et al. 2022 Table 1 ({acc})", "accession": acc, "population": pop,
         "split": "Single sequencing run of one mock community; no split", "source_locator": dloc,
         "scope_note": f"Species metrics are scored against {nspecies} species" + (
             " (17 in the community; Veillonella rogosae and Prevotella corporis excluded because several reference databases lacked them)" if key == "hifi-zymo-d6331" else "") + "."})
    pid = f"{P}-protocol-portik2022-{key}-species"
    PORTIK_PROTOCOLS[key] = pid
    rec(pid, "protocol", f"{dname}: species detection at 0.001% of total reads (Portik et al. 2022 Table 4)",
        "Presence or absence of each mock community species from the method's species-level read counts.", [SRC_PORTIK],
        [{"relation": "uses_data", "target_id": did}, {"relation": "part_of", "target_id": PORTIK_BENCH}],
        {"protocol": (f"A species is detected when its cumulative read count exceeds 0.001% of total reads ({THRESH[key]} reads for this dataset). "
                      "True positive: a mock community species detected; false positive: a detected species not in the community; "
                      "false negative: a community species not detected. Precision, recall, F1 and F0.5 from these counts. "
                      "L1: sum of absolute differences between estimated and theoretical species percent abundances, with all false positives pooled as 'Other' against a theoretical 0."),
         "version": f"Table 4 block '{label}'",
         "source_locator": "Methods 'Detection metrics' paragraphs 1-4; 'Relative abundance estimates' paragraph 4; Table 3 (threshold read counts)",
         "limitations": ["Mock community of cultured organisms; no human host DNA, no clinical specimen matrix.",
                         "Detection threshold is a fixed fraction of total reads, which penalises methods that assign fewer reads (Methods 'Detection metrics' paragraph 1).",
                         "Each method used its own reference database."]
         + (["Two community species were missing from several reference databases and were excluded from species scoring for every method (Table 4 footnote; Methods 'Detection metrics' paragraph 4)."] if key == "hifi-zymo-d6331" else []),
         "missing_metadata": {"uncertainty": {"reason": "unreported", "note": "Single run per dataset; no intervals printed"}}})
    comparison = {"dataset_version": acc, "split": "Single sequencing run", "population": f"{nspecies} scored species",
                  "inputs": dname, "adaptation": "None; reference databases as listed in Table 2",
                  "metric_implementation": "Authors' scoring of species read counts against the community composition",
                  "aggregation": "Single dataset", "budget": None}
    for i, m in enumerate(methods):
        row = body[start + i]
        printed_method = row[2]
        cid = PC[m]
        ev = f"{P}-eval-portik2022-{key}-{cid.split('-config-portik2022-')[1]}"
        origin = "author_reported" if m.startswith("Sourmash") else "independent_paper"
        r_no = start + i + 2
        loc_base = f"Table 4, dataset block '{label}', row '{printed_method}' (table row {r_no})"
        extra = {}
        if m.startswith("Sourmash"):
            extra["limitations"] = ["Co-authors C. Titus Brown and N. Tessa Pierce-Ward are authors of the cited sourmash papers (references 33-35), so these rows are recorded as author_reported."]
        if m.startswith("MEGAN-LR"):
            extra["limitations"] = ["Run through PacBio's pb-metagenomics-tools workflow; the first author is a Pacific Biosciences employee (Competing interests). MEGAN itself is third-party software."]
        if printed_method.endswith("*"):
            extra.setdefault("limitations", []).append("Asterisk in Table 4: two species unavailable in several reference databases; species set adjusted to 15.")
        evaluation(ev, f"{m} on {dname}", cid, pid, did, SRC_PORTIK, origin, comparison, loc_base, extra=extra or None)
        cols = [("True positives", 3, "true-positive-count", "higher", "count", None, "species"),
                ("False positives", 4, "false-positive-count", "lower", "count", None, "species"),
                ("False negatives", 5, "false-negative-count", "lower", "count", None, "species"),
                ("Precision", 6, "precision", "higher", "fraction", None, None),
                ("Recall", 7, "recall", "higher", "fraction", None, None),
                ("F1", 8, "f1-score", "higher", "fraction", None, None),
                ("F0.5", 9, "f-beta-score", "higher", "fraction", "F0.5 (beta = 0.5)", None),
                ("L1", 10, "composition-l1-distance", "lower", "percent", "species-level relative abundance, false positives pooled as 'Other'",
                 "sum of absolute differences in percent abundance (0 to 200)")]
        for col_label, ci, metric, direction, unit, qual, udetail in cols:
            slug = {"true-positive-count": "tp", "false-positive-count": "fp", "false-negative-count": "fn", "precision": "precision",
                    "recall": "recall", "f1-score": "f1", "f-beta-score": "f0-5", "composition-l1-distance": "l1"}[metric]
            result(f"{ev}-{slug}".replace("-eval-", "-result-"), ev, SRC_PORTIK, f"{loc_base}, column '{col_label}'",
                   row[ci], metric, direction, unit, qualifier=qual, unit_detail=udetail)

# ================================================================= Song et al. 2025, Tables 1 and 2
g1, cap1, foot1 = table_grid(SONG_XML, "mbo370158-tbl-0001")
need(cap1, "Relative abundances of the standard microbial control as analyzed by different software, in comparison with the theoretical distribution.", "Song Table 1 caption")
need(g1[0], ["", "Theoretical", "Blast", "Metaphlan", "RTG", "Kraken"], "Song Table 1 header")
SPECIES = ["Listeria monocytogenes", "Pseudomonas aeruginosa", "Bacillus subtilis", "Salmonella enterica", "Escherichia coli",
           "Lactobacillus fermentum", "Enterococcus faecalis", "Staphylococcus aureus"]
need([r[0] for r in g1[1:9]], SPECIES, "Song Table 1 species rows")
need([g1[9][0], g1[10][0]], ["η 2", "p‐value"], "Song Table 1 statistic rows")
need([g1[9][1], g1[10][1]], ["*", "*"], "Song Table 1 theoretical statistic cells")
need(foot1, "*not applicable. Note: η 2 and p‐value of ANOVA are shown.", "Song Table 1 footnote")
g2, cap2, foot2 = table_grid(SONG_XML, "mbo370158-tbl-0002")
need(cap2, "Relative abundances of viridans group Streptococci as detected by different software in blood samples.", "Song Table 2 caption")
need(g2[0], ["", "Blast", "Kraken", "RTG", "Metaphlan"], "Song Table 2 header")
SAMPLES = ["Sample 1", "Sample 2", "Sample 3", "Sample 4", "Sample 5", "Negative blood", "No template control"]
need([r[0] for r in g2[1:]], SAMPLES, "Song Table 2 sample rows")

SC = {}
for label, slug, of, rname, version, vm, params in [
    ("Blast", "blast-nt-galaxy", M["blast"], "BLAST", None, {"reason": "unreported", "note": "BLASTn run through Galaxy; version not printed"}, "NCBI nt database; Galaxy platform; default settings with minimum sequence similarity 90%"),
    ("Kraken", "kraken-native-db-galaxy", M["kraken"], "Kraken", None, {"reason": "unreported", "note": "Cited as Wood and Salzberg 2014 and run through Galaxy; neither the Kraken major version nor the database version is printed"}, "Native database; Galaxy platform; default settings with minimum sequence similarity 90% where not default"),
    ("Metaphlan", "metaphlan-native-db-galaxy", METAPHLAN, "Metaphlan", None, {"reason": "unreported", "note": "Cited as Beghini et al. 2021 and run through Galaxy; version and marker database not printed"}, "Native marker database; Galaxy platform; default settings"),
    ("RTG", "rtg-core-3-12", M["rtg-core"], "RTG Core", "3.12", None, "Native database; default settings with minimum sequence similarity 90% where not default"),
]:
    cid = f"{P}-config-song2025-{slug}"
    SC[label] = cid
    configuration(cid, f"{rname} (Song et al. 2025)", f"{rname} as run in Song et al. 2025 on shotgun reads from blood.", of, SRC_SONG,
                  rname, "Methods 'Data Analysis' paragraph 1", version=version, version_missing=vm, parameters=params)

SONG_ZYMO, SONG_BSI = f"{P}-data-song2025-zymo-standard-ii", f"{P}-data-song2025-bsi-blood"
rec(SONG_ZYMO, "dataset", "ZymoBIOMICS Microbial Community Standard II positive control (Song et al. 2025)",
    "Log-distributed mock community processed through the study's blood shotgun metagenomics workflow as a positive control.", [SRC_SONG], [],
    {"version": "ZymoBIOMICS Microbial Community Standard II (Zymo Research) as sequenced in the study",
     "population": "Eight species with theoretical relative abundances from 8.90E-1 to 8.90E-7 (Table 1, column 'Theoretical'); Results paragraph 1 also mentions yeasts, which Table 1 does not list.",
     "split": "Single positive-control library; no split", "source_locator": "Methods 'Data Analysis' paragraph 1; Results paragraph 1; Table 1",
     "missing_metadata": {"accession": {"reason": "unreported", "note": "The data availability statement gives PRJNA1268383 for sequencing data without saying whether the control is included"}}})
rec(SONG_BSI, "dataset", "Blood shotgun metagenomes from five culture-positive patients with haematological malignancy, plus negative blood and no-template controls (Song et al. 2025)",
    "Shotgun metagenomes from blood of patients with suspected bloodstream infection whose blood cultures grew alpha-haemolytic streptococci, and two negative controls.", [SRC_SONG], [],
    {"version": "Samples from Gyarmati et al. 2016 as reanalysed in Song et al. 2025", "accession": "NCBI PRJNA1268383",
     "population": "Five culture-positive blood samples (all viridans group streptococci, alpha-haemolytic on culture) from 22 sequenced samples; microfiltered sterile human blood (negative blood) and sterile water (no template control).",
     "split": "No split", "denominator": 5,
     "assay": "MolYsis Complete5 extraction, NEBNext microbiome enrichment, GenomiPhi V2 amplification, Nextera XT, HiSeq 2500 2x100 bp; mean 33.5 M reads per sample after QC",
     "source_locator": "Methods 'Sample Collection and Processing'; 'Data Analysis' paragraph 1; Results paragraph 2; Discussion paragraph 4"})
claim(f"{P}-claim-song2025-zymo-theoretical-composition", SONG_ZYMO, "theoretical_relative_abundance",
      "; ".join(f"{sp} {g1[i + 1][1]}" for i, sp in enumerate(SPECIES)) + ". Eta squared and p-value are not applicable to the theoretical column (printed '*').",
      SRC_SONG, "Table 1, column 'Theoretical', rows 1-10")
SP1 = f"{P}-protocol-song2025-zymo-abundance"
rec(SP1, "protocol", "Relative abundance of each species in ZymoBIOMICS Standard II against its theoretical distribution (Song et al. 2025 Table 1)",
    "Each pipeline's relative abundance per species in the log-distributed mock standard, with ANOVA effect size and p-value per pipeline.", [SRC_SONG],
    [{"relation": "uses_data", "target_id": SONG_ZYMO}],
    {"protocol": "Report the relative abundance each pipeline assigns to the eight listed species of the log-distributed standard; compare with the theoretical distribution by ANOVA (eta squared = between-group sum of squares / total sum of squares, and p-value).",
     "version": "Table 1", "source_locator": "Methods 'Data Analysis' paragraphs 1-2; Results paragraph 1; Table 1",
     "limitations": ["One positive-control library; no replicates.", "The ANOVA grouping is not described beyond the eta squared formula."],
     "missing_metadata": {"uncertainty": {"reason": "unreported"}}})
SP2 = f"{P}-protocol-song2025-bsi-vgs-abundance"
rec(SP2, "protocol", "Relative abundance of viridans group streptococci in culture-positive patient blood and negative controls (Song et al. 2025 Table 2)",
    "Each pipeline's relative abundance of viridans group streptococci in five culture-positive blood metagenomes and in negative blood and no-template controls.", [SRC_SONG],
    [{"relation": "uses_data", "target_id": SONG_BSI}],
    {"protocol": "Blood culture is the reference. For each sample, report the relative abundance of viridans group streptococci assigned by each pipeline; the same read-out in negative blood and no-template control shows contamination or false-positive signal. The study counts a detection as valid only if absent from both negative controls.",
     "version": "Table 2 (pipelines at the settings in Methods 'Data Analysis'; before the BLAST e-value optimisation shown in Figure 1)",
     "source_locator": "Methods 'Data Analysis' paragraph 1; Results paragraph 2; Table 2",
     "limitations": ["Five culture-positive samples, all viridans group streptococci; no culture-negative patient samples analysed.",
                     "Table 2 prints relative abundances, not detection calls; the study's validity rule (absent from both controls) is applied in the text.",
                     "BLAST e-value optimisation that removed control signal is reported only in Figure 1, not in a table."],
     "denominator": 5, "missing_metadata": {"uncertainty": {"reason": "unreported"}}})
ZCOMP = {"dataset_version": "ZymoBIOMICS Microbial Community Standard II, one library", "split": "Single positive control",
         "population": "Eight species in Table 1", "inputs": "Merged quality-filtered HiSeq 2500 reads", "adaptation": "Native database per pipeline",
         "metric_implementation": "Relative abundance as output by each pipeline", "aggregation": "Single library", "budget": None}
BCOMP = {"dataset_version": "Gyarmati et al. 2016 blood metagenomes, PRJNA1268383", "split": "No split",
         "population": "5 culture-positive blood samples, negative blood, no-template control", "inputs": "Merged quality-filtered HiSeq 2500 reads (mean 33.5 M per sample)",
         "adaptation": "Native database per pipeline", "metric_implementation": "Relative abundance of viridans group streptococci as output by each pipeline",
         "aggregation": "Per sample", "budget": None}
for label in ["Blast", "Metaphlan", "RTG", "Kraken"]:
    cid = SC[label]; s = cid.split("-config-song2025-")[1]
    ci = g1[0].index(label)
    ev = f"{P}-eval-song2025-zymo-{s}"
    evaluation(ev, f"{label} on ZymoBIOMICS Standard II (Song et al. 2025)", cid, SP1, SONG_ZYMO, SRC_SONG, "independent_paper", ZCOMP,
               f"Table 1, column '{label}'")
    for ri, sp in enumerate(SPECIES):
        sslug = sp.lower().replace(" ", "-")
        result(f"{P}-result-song2025-zymo-{s}-{sslug}", ev, SRC_SONG, f"Table 1, row '{sp}', column '{label}'",
               g1[ri + 1][ci], "proportion", "unknown", "fraction", qualifier=f"relative abundance of {sp}",
               unit_detail="relative abundance printed in E notation (theoretical value in column 'Theoretical')")
    result(f"{P}-result-song2025-zymo-{s}-eta-squared", ev, SRC_SONG, f"Table 1, rows 'η 2' and 'p‐value', column '{label}'",
           g1[9][ci], "eta-squared", "unknown", "unitless", qualifier="ANOVA against the theoretical distribution",
           extra={"reported_p_value": g1[10][ci]})
    claims_rows[-1][3] = f"{g1[9][ci]}; p-value {g1[10][ci]}"
for label in ["Blast", "Kraken", "RTG", "Metaphlan"]:
    cid = SC[label]; s = cid.split("-config-song2025-")[1]
    ci = g2[0].index(label)
    ev = f"{P}-eval-song2025-bsi-{s}"
    evaluation(ev, f"{label} on culture-positive blood and controls (Song et al. 2025)", cid, SP2, SONG_BSI, SRC_SONG, "independent_paper", BCOMP,
               f"Table 2, column '{label}'")
    for ri, smp in enumerate(SAMPLES):
        sslug = smp.lower().replace(" ", "-")
        result(f"{P}-result-song2025-bsi-{s}-{sslug}", ev, SRC_SONG, f"Table 2, row '{smp}', column '{label}'",
               g2[ri + 1][ci], "proportion", "unknown", "fraction", qualifier=f"relative abundance of viridans group streptococci, {smp.lower()}",
               unit_detail="relative abundance printed in E notation")
claim(f"{P}-claim-song2025-blast-controls", SP2, "control_signal_and_optimisation",
      "BLAST was the only software that detected viridans group streptococci in all five culture-positive samples, but it also gave signal in the negative blood and no-template control. Lowering the BLAST e-value to 10E-13 removed reads from both controls while all culture-positive samples stayed positive (Figure 1). Removing human reads first did not change viridans streptococci abundances (p = 0.15).",
      SRC_SONG, "Results paragraph 2; 'Reduction of False-Positive Signals' paragraphs 1-2")

# ================================================================= Hall and Coin 2024, Tables 5-8
HALL_TABLES = [("tbl5", "sim-nanopore", "simulated Nanopore", 1), ("tbl6", "real-nanopore", "real Nanopore", 2),
               ("tbl7", "sim-illumina", "simulated Illumina", 3), ("tbl8", "real-illumina", "real Illumina", 4)]
HALL_METHODS = ["kraken standard", "kraken standard-8", "kraken Myco", "minimap2 Clockwork", "minimap2 MTB", "minimap2 Myco"]
HALL_FOOT = ("Bold text indicates the best performing method for that metric. CI, confidence interval (Wilson score interval).*Average from 10 executions. †Maximum from 10 executions.")
HC = {}
for label, slug, of, version, params, loc in [
    ("kraken standard", "kraken2-standard", KRAKEN2, None, "Kraken standard database (complete RefSeq bacteria, archaea, viruses, human genome and vectors), built 2023-06-05; default options (--paired for Illumina)", "Methods 'Mycobacterium read classification' paragraphs 1 and 3"),
    ("kraken standard-8", "kraken2-standard-8", KRAKEN2, None, "Kraken standard database capped at 8 GB, built 2023-06-05; default options (--paired for Illumina)", "Methods 'Mycobacterium read classification' paragraphs 1 and 3"),
    ("kraken Myco", "kraken2-myco", KRAKEN2, None, "Authors' database: one RefSeq genome per Mycobacteriaceae species plus one per species of nine other genera, downloaded with genome_updater v0.6.3 and built with kraken2-build --build; simulation genomes excluded", "Methods 'Mycobacterium read classification' paragraph 1"),
    ("minimap2 Clockwork", "minimap2-clockwork", M["minimap2"], "2.26", "Clockwork decontamination database (sputum contaminants, NTM genomes, H37Rv, human) plus 17 high-quality M. tuberculosis genomes; -x map-ont or -x sr, -c --secondary=no", "Methods 'Mycobacterium read classification' paragraphs 2-3; minimap2 v2.26 from Methods 'Human read removal' paragraph 1"),
    ("minimap2 MTB", "minimap2-mtb", M["minimap2"], "2.26", "Authors' database: M. tuberculosis H37Rv plus 17 high-quality M. tuberculosis genomes from lineages 1-6; -x map-ont or -x sr, -c --secondary=no", "Methods 'Mycobacterium read classification' paragraphs 2-3"),
    ("minimap2 Myco", "minimap2-myco", M["minimap2"], "2.26", "Authors' database: one RefSeq genome per leaf node of the Mycobacterium genus plus the 17 M. tuberculosis genomes; -x map-ont or -x sr, -c --secondary=no", "Methods 'Mycobacterium read classification' paragraphs 2-3"),
]:
    cid = f"{P}-config-hall2024-{slug}"
    HC[label] = cid
    vm = None if version else {"reason": "unreported", "note": "Methods name kraken v2.1.2 only for the library download used to simulate reads; the version used for classification is not stated separately"}
    configuration(cid, f"{label} (Hall and Coin 2024)", f"{label} as run for M. tuberculosis read classification in Hall and Coin 2024.", of, SRC_HALL,
                  label, loc, version=version, version_missing=vm, parameters=params)
HALL_BENCH = f"{P}-benchmark-hall2024-mtb-read-classification"
rec(HALL_BENCH, "benchmark", "M. tuberculosis read classification with standard and custom databases (Hall and Coin 2024)",
    "Kraken and minimap2 with three databases each, scored per read on simulated and artificial real Nanopore and Illumina sputum-like metagenomes.",
    [SRC_HALL], [], {"entity_level": "suite", "version": "GigaScience 2024, Tables 5-8",
                     "task": "Classify each non-human read as M. tuberculosis or not",
                     "source_locator": "Results 'Classification of Mycobacterium reads'; Methods 'Mycobacterium read classification'",
                     "scope_note": "Human read removal (Tables 1-4) and coverage analyses (Supplementary Tables S9-S12) are not extracted.",
                     "limitations": ["Read-level classification of one pathogen; not sample-level pathogen detection."]})
HALL_DATA = {
    "sim-nanopore": ("Simulated sputum-like Nanopore metagenome, non-human reads (Hall and Coin 2024)", "Badreads v0.4.0 simulation, R10.4.1 error model; 46% bacteria, 46% human, 6% M. tuberculosis complex, 1% virus, 1% NTM by bases; 100,733 non-human reads (460 Mbp) classified", "Methods 'Generating in silico metagenomic reads' paragraphs 1-3, 5; Results 'Classification of Mycobacterium reads' paragraph 1"),
    "real-nanopore": ("Artificial real Nanopore metagenome, non-human reads (Hall and Coin 2024)", "Real reads combined: three 1000 Genomes individuals (R10.4), M. tuberculosis ERR8170871 (R10.3), ZymoBIOMICS D6322 ERR7287988 (R10.4); 915,209 non-human reads (3.47 Gbp) classified", "Methods 'Creation of an artificial real metagenomic dataset'; Results 'Classification of Mycobacterium reads' paragraph 1"),
    "sim-illumina": ("Simulated sputum-like Illumina metagenome, non-human reads (Hall and Coin 2024)", "ART v2016.06.05 MiSeq v3 150 bp paired reads at the same group proportions; 1,417,015 non-human read pairs (424 Mbp) classified", "Methods 'Generating in silico metagenomic reads' paragraphs 1, 4-5; Results 'Classification of Mycobacterium reads' paragraph 1"),
    "real-illumina": ("Artificial real Illumina metagenome, non-human reads (Hall and Coin 2024)", "Real reads combined: three 1000 Genomes individuals (NovaSeq 6000), M. tuberculosis ERR245682 (HiSeq 4000), ZymoBIOMICS D6322 ERR7255689 (MiSeq); 21,172,961 non-human read pairs (4.68 Gbp) classified", "Methods 'Creation of an artificial real metagenomic dataset'; Results 'Classification of Mycobacterium reads' paragraph 1"),
}
HALL_PROTOCOLS = {}
for tid, key, label, order in HALL_TABLES:
    g, cap, ft = table_grid(HALL_XML, tid)
    need(cap, f"Performance of M. tuberculosis read classification—{label}", f"Hall {tid} caption")
    need(g[0], ["Method", "Rate (reads/s)*", "Memory (GB)†", "Specificity (95% CI)", "Sensitivity (95% CI)", "Youden’s index (95% CI)"], f"Hall {tid} header")
    need([r[0] for r in g[1:]], HALL_METHODS, f"Hall {tid} method rows")
    need(ft, HALL_FOOT, f"Hall {tid} footnote")
    tno = tid[3:]
    dname, pop, dloc = HALL_DATA[key]
    did = f"{P}-data-hall2024-{key}"
    rec(did, "dataset", dname, "Sputum-like metagenome with known read origin, used after human read removal.", [SRC_HALL], [],
        {"version": "As described in Hall and Coin 2024", "population": pop, "split": "Single dataset; no split", "source_locator": dloc})
    pid = f"{P}-protocol-hall2024-mtb-reads-{key}"
    HALL_PROTOCOLS[key] = pid
    rec(pid, "protocol", f"M. tuberculosis read classification, {label} (Hall and Coin 2024 Table {tno})",
        "Per-read sensitivity, specificity and Youden's index for classifying non-human reads as M. tuberculosis, with throughput and peak memory.", [SRC_HALL],
        [{"relation": "uses_data", "target_id": did}, {"relation": "part_of", "target_id": HALL_BENCH}],
        {"protocol": "True positive: a read from an M. tuberculosis genome classified as M. tuberculosis; true negative: a non-M. tuberculosis read not so classified; false positive: a non-M. tuberculosis read classified as M. tuberculosis; false negative: an M. tuberculosis read not so classified. Sensitivity, specificity and Youden's index with 95% Wilson score intervals; rate is the mean and memory the maximum of 10 executions on 4 threads.",
         "version": f"Table {tno}", "source_locator": "Methods 'Human read removal' paragraph 4 and 'Mycobacterium read classification' paragraph 4",
         "limitations": ["Read-level metrics; a sample-level detection call is not evaluated.", "One target pathogen (M. tuberculosis); NTM reads are negatives.",
                         "Three of the six configurations use databases built by the authors."]})
    comp = {"dataset_version": pop, "split": "Single dataset", "population": "Non-human reads of the dataset",
            "inputs": "Non-human reads after the human read removal step", "adaptation": "Database as stated per configuration",
            "metric_implementation": "Per-read confusion counts against known read origin", "aggregation": "All reads in the dataset", "budget": "4 threads"}
    for ri, m in enumerate(HALL_METHODS):
        row = g[ri + 1]
        cid = HC[m]; s = cid.split("-config-hall2024-")[1]
        ev = f"{P}-eval-hall2024-{key}-{s}"
        origin = "independent_paper" if m in ("kraken standard", "kraken standard-8") else "author_reported"
        extra = None
        if origin == "author_reported":
            extra = {"limitations": ["The database for this configuration was built or extended by the authors (Methods 'Mycobacterium read classification')."]}
        evaluation(ev, f"{m} on {dname}", cid, pid, did, SRC_HALL, origin, comp, f"Table {tno}, row '{m}'", extra=extra)
        base = f"Table {tno}, row '{m}'"
        result(f"{P}-result-hall2024-{key}-{s}-rate", ev, SRC_HALL, f"{base}, column 'Rate (reads/s)*'", row[1], "inference-throughput", "higher",
               "sample-per-second", unit_detail="reads per second, mean of 10 executions on 4 threads")
        result(f"{P}-result-hall2024-{key}-{s}-memory", ev, SRC_HALL, f"{base}, column 'Memory (GB)†'", row[2], "peak-memory", "lower",
               "gigabyte", unit_detail="GB as printed; maximum of 10 executions")
        for col, ci, metric, slug in [("Specificity (95% CI)", 3, "specificity", "specificity"), ("Sensitivity (95% CI)", 4, "recall", "sensitivity"),
                                      ("Youden’s index (95% CI)", 5, "youden-index", "youden")]:
            mm = re.fullmatch(r"([0-9.]+) \(([0-9.]+) ?– ?([0-9.]+)\)", row[ci])
            if not mm:
                raise SystemExit(f"Unparsed interval cell {tid} {m} {col}: {row[ci]!r}")
            pv, lo, hi = mm.groups()
            unc = {"type": "confidence_interval", "printed": f"({lo}–{hi})", "lower": lo, "upper": hi, "level": 0.95,
                   "method": "analytic", "note": "Wilson score interval (table footnote)"}
            result(f"{P}-result-hall2024-{key}-{s}-{slug}", ev, SRC_HALL, f"{base}, column '{col}'", pv, metric, "higher",
                   "fraction", qualifier="per read, M. tuberculosis" if metric != "youden-index" else None, uncertainty=unc,
                   extra={"printed_source_cell": row[ci]})
            claims_rows[-1][3] = row[ci]
claim(f"{P}-claim-hall2024-kraken-fn-genus", HALL_BENCH, "kraken_false_negative_rank",
      "With the full-size and 8 GB standard databases, kraken's missed M. tuberculosis reads were mostly not placed at species rank; in all cases at least 90% of these false negatives were classified correctly at genus level.",
      SRC_HALL, "Results 'Classification of Mycobacterium reads', subsection 'Real Illumina' paragraph 3")
claim(f"{P}-claim-portik2022-missing-reference-species", f"{P}-data-portik2022-hifi-zymo-d6331", "species_absent_from_reference_databases",
      "Sequences or taxonomy for Veillonella rogosae and Prevotella corporis were lacking from several reference databases (PlusPF, RefSeq ABVF, MiniSeq + H, NCBI nt), so both were excluded from species-level detection metrics for all methods; many of their reads were assigned to other species of the same genera.",
      SRC_PORTIK, "Methods 'Detection metrics' paragraph 4; Table 4 footnote")

# ================================================================= relevance judgements
UC_NAME = "Select a DNA pathogen-identification workflow for diagnostic testing"
JUDGEMENTS = []


def judgement(short, protocol_id, protocol_name, relevance, endpoint, rationale, constraints, limitations, source_id, cite_loc,
              group, title, headline, stratum=None, order=None):
    jid = f"use-case-mapping-dna-pathogen-20261009-{short}"
    attrs = {"field": f"links:assessed_by:{protocol_id}", "value": protocol_id, "relevance": relevance, "endpoint": endpoint,
             "rationale": rationale, "constraints": constraints, "limitations": limitations,
             "citation_locators": [{"source_id": source_id, "locator": cite_loc}],
             "source_locator": f"{source_id}: {cite_loc}", "revision": 1,
             "reason": "Recorded from the DNA pathogen-identification use-case pass 2026-10-09 (data/omics/use-case-coverage-dna-pathogen-20261009). Draft until an independent review.",
             "comparison_group": group, "comparison_title": title, "headline_metric": headline}
    if stratum:
        attrs["stratum_label"], attrs["stratum_order"] = stratum, order
    rec(jid, "claim", f"Relevance of {protocol_name} to \"{UC_NAME}\"", rationale, [source_id],
        [{"relation": "subject", "target_id": UC}], attrs, facets={})
    JUDGEMENTS.append({"judgement_id": jid, "protocol_id": protocol_id, "relevance": relevance, "comparison_group": group,
                       **({"stratum_label": stratum, "stratum_order": order} if stratum else {})})


COMMON_CONSTRAINTS = ["Inspect every linked evaluation's source locator and preserved limitations before citing a result.",
                      "Do not combine these results with another protocol's results; datasets, databases and scoring rules differ between sources."]
P_LABELS = {"hifi-atcc-msa1003": ("PacBio HiFi, ATCC MSA-1003", 1), "illumina-atcc-msa1003": ("Illumina, ATCC MSA-1003", 2),
            "hifi-zymo-d6331": ("PacBio HiFi, Zymo D6331", 3), "ont-r10-zymo-d6300": ("ONT R10.3, Zymo D6300", 4),
            "ont-q20-zymo-d6300": ("ONT Q20, Zymo D6300", 5), "illumina-zymo-d6300": ("Illumina, Zymo D6300", 6)}
for key in P_ORDER:
    pid = PORTIK_PROTOCOLS[key]
    stratum, order = P_LABELS[key]
    lims = ["Mock community of cultured organisms without human host DNA or a clinical specimen matrix.",
            "Each method used its own reference database (Table 2), so method and database effects are confounded.",
            "Single run per dataset; no intervals.",
            "Sourmash rows are reported by sourmash authors (author_reported); the first author is a PacBio employee and MEGAN-LR workflows are PacBio's."]
    if key == "hifi-zymo-d6331":
        lims.append("Two community species were absent from several databases and were dropped from species scoring for all methods.")
    if key.startswith("illumina"):
        lims.append("Only short-read and general methods were run on the Illumina data.")
    judgement(f"portik2022-{key}", pid, f"{DS_INFO[key][0]}: species detection at 0.001% of total reads (Portik et al. 2022 Table 4)", "proxy",
              f"Species-level true and false positives, false negatives, precision, recall, F1, F0.5 and abundance L1 error for {len(BLOCKS[[b[0] for b in BLOCKS].index(key)][3])} classification configurations on {stratum} mock community reads",
              "Counting false-positive species and missed species in a mock community of known composition measures how a classification workflow handles spurious low-abundance calls and detection, which bears on the use case. It is proxy evidence because the samples are mock communities of cultured organisms without host DNA, not clinical specimens.",
              COMMON_CONSTRAINTS, lims, SRC_PORTIK, f"Table 4, dataset block '{dict((b[0], b[1]) for b in BLOCKS)[key]}'; Methods 'Detection metrics'",
              "portik2022-mock-species", "Species detection in mock communities (Portik et al. 2022)", "f1-score", stratum, order)
judgement("song2025-zymo-standard", SP1, "Relative abundance in ZymoBIOMICS Standard II (Song et al. 2025 Table 1)", "proxy",
          "Relative abundance of eight species in a log-distributed mock standard (8.9E-1 to 8.9E-7) for BLAST, MetaPhlAn, RTG Core and Kraken, against the theoretical distribution",
          "The lowest abundance at which each pipeline still reports a species in a standard processed through a blood metagenomics workflow bears on detection of low-abundance pathogens. It is proxy evidence: one mock library, abundance rather than detection calls, and no clinical reference standard.",
          COMMON_CONSTRAINTS, ["One positive-control library; no replicates or intervals.", "Abundances, not detection calls; no threshold applied in the table.",
                               "Kraken and MetaPhlAn versions and databases unreported; Kraken major version unclear."],
          SRC_SONG, "Table 1; Results paragraph 1", "song2025-zymo-standard", "Abundance recovery in a log-distributed mock standard (Song et al. 2025)", "proportion")
judgement("song2025-bsi-blood", SP2, "Viridans streptococci in culture-positive blood and negative controls (Song et al. 2025 Table 2)", "proxy",
          "Relative abundance of viridans group streptococci assigned by BLAST, Kraken, RTG Core and MetaPhlAn in five blood-culture-positive patient blood metagenomes, a negative blood control and a no-template control",
          "Real patient blood with a blood-culture reference and negative controls is the use case's setting, and the control rows show contamination signal. It is held as proxy because the table reports relative abundances rather than detection calls, covers five samples of one organism group, and has no culture-negative patients.",
          COMMON_CONSTRAINTS, ["Five culture-positive samples, all viridans group streptococci; no culture-negative patient samples.",
                               "Relative abundances, not detection calls; the study's control-based validity rule is applied in the text.",
                               "BLAST's later e-value optimisation (Figure 1) is not in the table and was not extracted.",
                               "Kraken and MetaPhlAn versions and databases unreported."],
          SRC_SONG, "Table 2; Results paragraph 2", "song2025-bsi-blood", "Viridans streptococci in culture-positive blood and negative controls (Song et al. 2025)", "proportion")
H_LABELS = {"sim-nanopore": ("Simulated Nanopore", 1), "real-nanopore": ("Artificial real Nanopore", 2),
            "sim-illumina": ("Simulated Illumina", 3), "real-illumina": ("Artificial real Illumina", 4)}
for tid, key, label, order in HALL_TABLES:
    stratum, _ = H_LABELS[key]
    judgement(f"hall2024-mtb-{key}", HALL_PROTOCOLS[key], f"M. tuberculosis read classification, {label} (Hall and Coin 2024 Table {tid[3:]})", "proxy",
              f"Per-read sensitivity, specificity and Youden's index (95% Wilson intervals), throughput and peak memory for kraken and minimap2 with three databases each, classifying M. tuberculosis reads in a {label} sputum-like metagenome",
              "Comparing standard and pathogen-focused databases on reads of known origin measures how reference completeness changes identification of a clinically relevant pathogen, which bears on the use case's question about organisms poorly represented in the reference. It is proxy evidence: read-level classification of one pathogen in constructed metagenomes, not sample-level diagnosis.",
              COMMON_CONSTRAINTS, ["Read-level, not sample-level, metrics; one target pathogen.",
                                   "Constructed metagenomes (simulated or mixed real reads), not patient specimens.",
                                   "Three configurations use databases built by the authors (author_reported)."],
              SRC_HALL, f"Table {tid[3:]}; Results 'Classification of Mycobacterium reads'", "hall2024-mtb-reads",
              "M. tuberculosis read classification by database (Hall and Coin 2024)", "youden-index", stratum, order)

# ================================================================= write
records.sort(key=lambda r: r["id"])
ids = [r["id"] for r in records]
if len(ids) != len(set(ids)):
    raise SystemExit("Duplicate IDs")
with open(f"{BATCH}/batch.jsonl", "w", encoding="utf-8") as f:
    for r in records:
        f.write(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n")
claims_rows.sort(key=lambda r: r[0])
with open(f"{BATCH}/claims.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["record_id", "source_id", "locator", "printed_value", "review_scope"])
    w.writerows(claims_rows)
with open(f"{BATCH}/extract/judgements.json", "w", encoding="utf-8") as f:
    json.dump(JUDGEMENTS, f, indent=2, ensure_ascii=False)
from collections import Counter
print(json.dumps(Counter(r["kind"] for r in records), sort_keys=True))
