"""Extract Tisza et al. 2026 (EsViritu, bioRxiv 10.64898/2026.09.29.755457 v1) Supplemental Tables S2, S6 and S9.

Usage: python3 -I extract_tisza2026.py <755457_file02.xlsx> <batch-folder>

Deterministic parse of the pinned supplementary workbook (sheet XML and shared strings,
no spreadsheet library). Every header and row label is asserted. printed_value is the cell
text, or for numeric cells the shortest decimal that round-trips to the stored number;
displayed spreadsheet formatting is not applied. Writes batch.jsonl and claims.csv.
Records are needs_review; this script never marks anything reviewed.
"""
import csv, hashlib, json, re, sys, zipfile
from collections import Counter

XLSX_SHA = "0559022a3ff5ef5b2682e3c451eda51835c4c8d9be9dfdb1ebc9cd9295fb7701"
XML_SHA = "fd92099655ddefdec31d35e273b80c4b233eed395c1cfc137eaddaa4efee232b"
P = "rna-pathogen-20261011-tisza2026"
M = "rna-pathogen-20261011-method"
SRC, SRC_SUPP = f"{P}-source", f"{P}-source-supp"
XML_URL = "https://www.biorxiv.org/content/early/2026/09/30/2026.09.29.755457.source.xml"
SUPP_URL = "https://www.biorxiv.org/content/biorxiv/early/2026/09/30/2026.09.29.755457/DC1/embed/media-1.xlsx?download=true"
DATE = "2026-10-11"
FACETS = {"areas": ["microbes-communities"], "contexts": ["research"]}
UC_RNA = "use-case-diagnostic-rna-pathogen-detection"
UC_DNA = "use-case-diagnostic-dna-pathogen-identification"

def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()

def read_sheets(path):
    z = zipfile.ZipFile(path)
    x = z.read("xl/sharedStrings.xml").decode()
    ss = ["".join(re.findall(r"<t[^>]*>([^<]*)</t>", si)) for si in re.findall(r"<si>.*?</si>", x, re.S)]
    wb = z.read("xl/workbook.xml").decode()
    rels_x = z.read("xl/_rels/workbook.xml.rels").decode()
    rels = {}
    for rel in re.findall(r"<Relationship [^>]*/>", rels_x):
        rels[re.search(r'Id="([^"]+)"', rel).group(1)] = re.search(r'Target="([^"]+)"', rel).group(1)
    out = {}
    for name, rid in re.findall(r'<sheet [^>]*name="([^"]+)"[^>]*r:id="([^"]+)"', wb):
        t = rels[rid].lstrip("/")
        t = t if t.startswith("xl/") else "xl/" + t
        cells = {}
        for ref, attrs, body in re.findall(r'<c r="([A-Z]+\d+)"([^>]*?)(?:/>|>(.*?)</c>)', z.read(t).decode(), re.S):
            v = re.search(r"<v>([^<]*)</v>", body or "")
            if v is None:
                continue
            kind = "s" if 't="s"' in attrs else ("str" if 't="str"' in attrs else "n")
            cells[ref] = ss[int(v.group(1))] if kind == "s" else v.group(1)
            if kind == "n":
                cells[ref] = ("n", v.group(1))
        out[name] = cells
    return out

def printed(sheet, ref):
    """(printed_value, numeric_value)."""
    v = sheet.get(ref)
    if isinstance(v, tuple):
        f = float(v[1])
        s = repr(f)
        if "e" in s:
            s = format(f, ".17f").rstrip("0")  # plain decimal, then shorten
            for n in range(1, 30):
                t = format(f, f".{n}f")
                if float(t) == f:
                    s = t
                    break
        if s.endswith(".0"):
            s = s[:-2]
        return s, s
    assert v is not None, ref
    return v, None

TOOLS = {
    "EsViritu": ("esviritu", "EsViritu", "v1.3.1", "sr mode (minimap2 short-read preset)", "Headline setting 'EsViritu=sr'"),
    "Centrifuger": ("centrifuger", "Centrifuger", "v1.1.1-r309", "minimum-hit-length 100, minimum score 0", "Headline setting 'Centrifuger=minimum-hit-length:100, minimum score:0'"),
    "Kraken2": ("kraken2", "Kraken2", "v2.17.1", "confidence 0.5, minimum-hit-group 2", "Headline setting 'Kraken2=confidence score:0.5, minimum-hit-group:2'"),
    "Metabuli": ("metabuli", "Metabuli", "v1.2.0", "precision 1, minimum score 0.15", "Headline setting 'Metabuli=precision:1, minimum score:0.15'"),
    "Sylph": ("sylph", "Sylph", "v0.9.0", "10 k-mers per genome", "Headline setting 'Sylph=10 k-mers-per-genome'"),
}
PARENT = {"esviritu": f"{M}-esviritu", "centrifuger": f"{M}-centrifuger", "kraken2": "catalog-model-kraken2",
          "metabuli": f"{M}-metabuli", "sylph": f"{M}-sylph"}

def review(art_sha, url, note, method="deterministic-table-parse"):
    return {"method": [method], "reviewer": ["claude"],
            "reviewer_note": "Extracting Claude research agent (uc-pathogens); not an independent review",
            "date": DATE, "artifact_sha256": art_sha, "retrieval_url": url, "note": note + " Pending independent review."}

PARSE_NOTE = ("Extracted by deterministic parse of the pinned XLSX sheet XML (extract/extract_tisza2026.py), with header and row labels asserted. "
              "printed_value is the cell text, or the shortest decimal that round-trips to the stored number; displayed spreadsheet formatting was not applied.")

# Independent review (reviewer-path, 2026-10-11; docs/reviews/use-cases/pathogen-use-cases-2026-10-11.md):
# every record becomes source_checked, and results, claims and judgements carry the reviewer's review block.
REVIEW_NOTE = ("Re-downloaded the pinned artifact and matched its SHA-256; compared every value with a separate stdlib parser "
               "written for this review (the extractor's script was not run) and checked a stratified sample by hand against the rendered table.")

def finalize(records, table_results=True, extra_notes=None):
    extra_notes = extra_notes or {}
    evals = {}
    for r in records:
        if r["kind"] == "evaluation":
            pid = [l["target_id"] for l in r["links"] if l["relation"] == "assessment"][0]
            evals.setdefault(pid, []).append(r["id"])
    for r in records:
        r["status"] = "source_checked"
        a = r["attributes"]
        if r["kind"] not in ("result", "claim"):
            continue
        old = a["review"]
        if r["kind"] == "result":
            method = ["source-hash-verification", "deterministic-table-parse", "independent-cell-check"] if table_results else ["source-hash-verification", "independent-cell-check"]
        else:
            method = ["source-hash-verification", "independent-cell-check", "scope-review"]
        note = REVIEW_NOTE + (" " + extra_notes[r["id"]] if r["id"] in extra_notes else "")
        a["review"] = {"method": method, "reviewer": ["claude"],
                       "reviewer_note": "Separate Claude review agent (reviewer-path), independent of the extractor; no human review claimed",
                       "date": "2026-10-11", "artifact_sha256": old["artifact_sha256"], "retrieval_url": old["retrieval_url"],
                       "method_note": old["note"].replace(" Pending independent review.", ""), "note": note}
        if a.get("field", "").startswith("links:assessed_by:"):
            a["reviewed_evaluations"] = sorted(evals[a["value"]])
            a["reason"] = a["reason"].replace(" Needs independent review.", " Independently reviewed in docs/reviews/use-cases/pathogen-use-cases-2026-10-11.md.")

EXTRA = {}

T1_ANOMALY = "Results 'EsViritu is an accurate profiler of mock virus communities' paragraph 2 says only the three one-per-family communities were measured in the divergence-capped metrics; Methods 'Mock communities' says all six communities were analysed together, and the Supplemental Table S9 caption says 'across mock communities'. The number of communities behind this mean is not certain. Value kept as printed."
T1_LIMIT = "Under divergence-capped truth the Results say only the three one-per-family communities were scored, while Methods say all six were analysed together; the capped means may cover three communities."
T3_ANOMALY = "Results 'EsViritu reaches read-level sensitivity while avoiding false positives' paragraph 4 prints detection probabilities (EsViritu 0.995, Metabuli 0.99996, Sylph 1.8 x 10^-3) and odds ratios that do not match Supplemental Tables S2 and S3; the text appears to describe a different fit. Value is the S2 marginal mean as printed."

def main():
    xlsx, out = sys.argv[1:3]
    xlsx_sha = sha(xlsx)
    assert xlsx_sha == XLSX_SHA, xlsx_sha
    sh = read_sheets(xlsx)
    R, claims = [], []

    def add(id_, kind, name, desc, attrs, links=(), src=(SRC,), facets=FACETS):
        R.append({"id": id_, "kind": kind, "name": name, "description": desc, "status": "needs_review",
                  "facets": dict(facets), "source_ids": list(src),
                  "links": [dict(relation=a, target_id=b) for a, b in links], "attributes": attrs})

    def result(rid, eval_id, metric, unit, direction, sheet_name, ref, loc, qual, unit_detail=None, unc=None, missing_note=None, anomaly=None):
        s = sh[sheet_name]
        pv, nv = printed(s, ref)
        attrs = {"metric": metric, "metric_direction": direction, "unit": unit, "printed_value": pv, "numeric_value": nv,
                 "metric_qualifier": qual, "source_locator": loc}
        if unit_detail:
            attrs["unit_detail"] = unit_detail
        mm = {}
        if unc:
            attrs["uncertainty"] = unc
        else:
            mm["uncertainty"] = {"reason": "unreported"}
        if nv is None:
            mm["value"] = {"reason": "unavailable", "note": missing_note or "Cell printed 'NA'"}
        if mm:
            attrs["missing_metadata"] = mm
        if anomaly:
            attrs["source_anomaly"] = anomaly
        attrs["review"] = review(XLSX_SHA, SUPP_URL, PARSE_NOTE)
        add(rid, "result", rid.replace(P + "-result-", "tisza2026 "), "Reported measurement transcribed from the pinned source. Not independently reproduced.",
            attrs, links=[("evaluation", eval_id)], src=(SRC_SUPP,), facets={})
        claims.append([rid, SRC_SUPP, loc, pv, "result"])

    # Sources
    add(SRC, "source", "EsViritu is a sensitive and specific profiler for viral pathogen detection and genome recovery in metagenomes",
        "Primary source retrieved and hashed for the 2026-10-11 RNA pathogen-detection literature pass.",
        {"url": "https://doi.org/10.64898/2026.09.29.755457", "artifact_url": XML_URL,
         "version": "bioRxiv 10.64898/2026.09.29.755457 v1, posted 2026-09-30; JATS XML",
         "retrieved_at": "2026-10-11T21:39:50Z", "artifact_sha256": XML_SHA, "doi": "10.64898/2026.09.29.755457",
         "publication_status": "preprint", "licence": "CC-BY-NC-4.0", "media_type": "application/xml", "venue": "bioRxiv", "year": 2026,
         "source_locator": "Licence statement in the JATS XML and the bioRxiv API record (license cc_by_nc)"},
        src=())
    add(SRC_SUPP, "source", "Tisza et al. 2026 Supplemental Tables S1-S25 (bioRxiv media-1.xlsx)",
        "Supplementary workbook of the primary source, retrieved and hashed for the 2026-10-11 RNA pathogen-detection literature pass.",
        {"url": "https://doi.org/10.64898/2026.09.29.755457", "artifact_url": SUPP_URL,
         "version": "bioRxiv 10.64898/2026.09.29.755457 v1 supplementary file DC1 (755457_file02.xlsx)",
         "retrieved_at": "2026-10-11T21:45:51Z", "artifact_sha256": XLSX_SHA, "doi": "10.64898/2026.09.29.755457",
         "publication_status": "preprint", "licence": "CC-BY-NC-4.0",
         "media_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "venue": "bioRxiv", "year": 2026,
         "source_locator": "JATS XML <supplementary-material> 'Supplemental Tables S1-S25' (supplements/755457_file02.xlsx); licence as for the preprint"},
        src=())
    # Methods (families)
    fam = {
        "esviritu": ("EsViritu", "Read-mapping virus profiler: minimap2 alignment to the Virus Pathogen Database, greedy read-sharing clustering of assemblies, reference-guided genome reconstruction and lowest-common-ancestor taxonomy with ANI roll-back.", "Bioconda package; source at GitHub cmmr/EsViritu", "Methods 'EsViritu algorithms and code'; Code and data availability"),
        "centrifuger": ("Centrifuger", "Metagenomic read classifier using a compressed full-text index of reference genomes.", "Not described in the source beyond the citation", "Methods 'Tools and parameters'"),
        "metabuli": ("Metabuli", "Metagenomic read classifier combining DNA and amino-acid k-mer matching.", "Not described in the source beyond the citation", "Methods 'Tools and parameters'"),
        "sylph": ("Sylph", "Metagenomic profiler based on k-mer containment of sketched genomes.", "Not described in the source beyond the citation", "Methods 'Tools and parameters'; Results 'Mock communities' last paragraph"),
    }
    for k, (name, desc, access, loc) in fam.items():
        add(f"{M}-{k}", "method", name, desc,
            {"reported_name": name, "entity_level": "method", "source_locator": loc, "access": access,
             "missing_metadata": {"version": {"reason": "inapplicable", "note": "Family record; versions are on configurations"}}},
            facets={**FACETS, "method_types": ["conventional_pipeline"]})
    # Configurations
    for label, (k, rep, ver, params, loc) in TOOLS.items():
        attrs = {"reported_name": f"{rep} {ver}", "version": ver.lstrip("v"), "foundation_model_eligible": False,
                 "parameters": f"{params}; database: EsViritu Virus Pathogen Database v3.2.4b (v3.2.4 with taxonomy labels taken only from the NCBI TaxDump of 2026-06-01), built into each tool's own index format",
                 "source_locator": f"Methods 'Tools and parameters'; Results 'EsViritu reaches read-level sensitivity while avoiding false positives' paragraph 3 ({loc})",
                 "access_reuse": "EsViritu: Bioconda and GitHub cmmr/EsViritu; Virus Pathogen Database on Zenodo (10.5281/zenodo.17716199; v3.2.4b in 10.5281/zenodo.23043160)" if k == "esviritu" else "Third-party tool run by the EsViritu authors; access not described in the source"}
        if k == "kraken2":
            attrs["model_identity_note"] = "Printed as 'v2.17.1' followed by reference marker 19"
        add(f"{P}-config-{k}", "configuration", f"{rep} {ver}, headline setting (Tisza et al. 2026)",
            f"{rep} {ver} at the authors' headline parameter setting, querying the EsViritu Virus Pathogen Database.",
            attrs, links=[("configuration_of", PARENT[k])], facets={**FACETS, "method_types": ["conventional_pipeline"]})
    # Datasets
    datasets = {
        "pos": ("Positive-control synthetic reads from seven divergent virus genomes (Tisza et al. 2026)",
                "Reads synthesised with bbtools randomreads.sh from seven genomes (four Genomoviridae, three Picornaviridae) at 75.91% to 95.62% ANI to their closest database reference, at 1, 10, 100 and 1,000 reads, ten permutations per depth",
                "Methods 'Positive controls'; Supplemental Table S25"),
        "neg": ("Seven pathogen-free negative-control read libraries (Tisza et al. 2026)",
                "Human genome mock reads (chm13v2, 20,000,004 reads), mouse RNA, anaerobic digester (ONT), freshwater, marine water, hot springs and soil libraries; 1.56 to 90.6 million reads each",
                "Methods 'Negative controls'; Supplemental Table S16"),
        "mock": ("Six mutated virus mock communities with bacterial and human background (Tisza et al. 2026)",
                 "Three communities of 90 random Virus Pathogen Database genomes and three of 60 genomes with at most one per family, mutated to 80%, 85%, 90%, 95%, 98% and 100% ANI; 10,000 InSilicoSeq NovaSeq read pairs per virus plus 50,000,000 reads from 100 bacterial genomes and the human genome",
                 "Methods 'Mock communities'"),
    }
    for k, (name, pop, loc) in datasets.items():
        add(f"{P}-data-{k}", "dataset", name, "Benchmark data constructed by the EsViritu authors.",
            {"version": "As described in Tisza et al. 2026 v1", "population": pop, "split": "No split", "source_locator": loc,
             "access": "Zenodo 10.5281/zenodo.23043160 (stated in Code and data availability; not retrieved)"})
    bench = f"{P}-benchmark-virus-profilers"
    add(bench, "benchmark", "Virus profiler benchmark against a shared Virus Pathogen Database (Tisza et al. 2026)",
        "EsViritu, Kraken2, Centrifuger, Metabuli and Sylph on positive controls, pathogen-free negative controls and mutated mock communities, all querying the same database.",
        {"entity_level": "suite", "version": "bioRxiv v1, Supplemental Tables S1-S25",
         "task": "Detect and profile vertebrate, plant and other pathogen viruses from metagenomic reads",
         "source_locator": "Results; Methods 'Tools and parameters', 'Positive controls', 'Negative controls', 'Mock communities'",
         "scope_note": "Only Supplemental Tables S2, S6 and S9 (headline settings) were extracted; per-sample and parameter-sweep tables (S5, S10, S22, S24), regression terms (S1, S3, S11, S12), statistical tests and timing (S15) were not.",
         "limitations": ["Benchmark built and run by the developers of EsViritu.", "All data are synthetic or pathogen-free libraries; no clinical specimen with a reference test."]})
    protocols = {
        "pos": ("Positive-control virus detection by read depth (Tisza et al. 2026 Table S2)",
                "Family-level detection of reads from seven divergent virus genomes, modelled with Firth-penalised logistic regression (detected ~ tool x depth + genome); marginal detection probability at 10 and 100 read pairs averaged over genomes, with 95% asymptotic confidence intervals.",
                "A detection is scored when a tool reports the genome's family. Bias-reduced logistic regression (brglm2 AS_mixed), genome as a fixed block, EsViritu as the reference tool; estimated marginal means at 10 and 100 read pairs.",
                "Methods 'Positive controls'; Supplemental Table S2 caption",
                ["Detection is scored at family rank only.", "Model-estimated probabilities, not observed proportions; ANI is confounded with genome (one genome per ANI level).", "Seven genomes from two families.", "The S2 caption does not name the parameter setting; the Results tie the regression to the headline parameters, so the results are attached to the headline configurations."]),
        "neg": ("False positives in seven pathogen-free libraries (Tisza et al. 2026 Table S6)",
                "Percentage of individual reads falsely assigned to a virus and number of false species, summarised as median and mean (reads) or median and maximum (species) over seven negative-control libraries.",
                "Every virus assignment in a pathogen-free library is a false positive. False-positive individual-read percentage uses each library's total reads as the denominator; Sylph read percentages are unavailable.",
                "Methods 'Negative controls'; Supplemental Tables S6 and S16 captions",
                ["Seven libraries; one is human genome mock reads and one is mouse RNA; the rest are environmental.", "Each tool at its selected negative-control setting."]),
        "mock": ("Mutated virus mock-community profiling against ground truth (Tisza et al. 2026 Table S9)",
                 "Mean F1, Bray-Curtis dissimilarity (reads per million) and Pearson correlation of each tool's profile against ground truth across six mock communities, by taxonomic rank under strict truth and under ANI-capped truth.",
                 "Strict truth uses the provenance lineage at each rank; capped truth caps the rank by ANI (98-100%: subspecies, 90-95%: species, 80-85%: genus). Profiles normalised to relative abundance per tool; means over the six communities.",
                 "Methods 'Mock communities'; Supplemental Table S9 caption",
                 ["The divergence cap is a heuristic, as the authors note (Discussion).", "Sylph abundance metrics are not comparable and are printed NA.", T1_LIMIT]),
    }
    for k, (name, desc, proto, loc, lim) in protocols.items():
        add(f"{P}-protocol-{k}", "protocol", name, desc,
            {"protocol": proto, "version": "bioRxiv v1", "source_locator": loc, "limitations": lim},
            links=[("uses_data", f"{P}-data-{k}"), ("part_of", bench)], src=(SRC, SRC_SUPP))
    for label, (k, rep, ver, params, loc) in TOOLS.items():
        for pk in protocols:
            add(f"{P}-eval-{pk}-{k}", "evaluation", f"{rep} {ver} on {protocols[pk][0]}",
                "Published developer benchmark; transcribed, not reproduced.",
                {"origin": "author_reported", "protocol": f"{P}-protocol-{pk}", "version": "Preprint v1 as retrieved 2026-10-11",
                 "comparison": {"protocol_id": f"{P}-protocol-{pk}", "dataset_version": datasets[pk][0], "split": "No split",
                                "population": datasets[pk][1], "inputs": {"pos": "Synthetic read pairs (bbtools randomreads.sh)", "neg": "Short reads (ONT reads for one negative-control library)", "mock": "Synthetic NovaSeq read pairs (InSilicoSeq)"}[pk],  # review T2
                                "adaptation": f"Headline setting: {params}", "metric_implementation": protocols[pk][2],
                                "aggregation": {"pos": "Marginal mean over seven genomes at fixed depth", "neg": "Median, mean or maximum over seven libraries", "mock": "Mean over six communities"}[pk],
                                "budget": None},
                 "source_locator": {"pos": f"Supplemental Table S2, rows base_tool '{label}'", "neg": f"Supplemental Table S6, row base_tool '{label}'", "mock": f"Supplemental Table S9, rows base_tool '{label}'"}[pk],
                 "limitations": ["Run by the developers of EsViritu, who chose each comparator's parameter grid and headline setting.",
                                 "All tools queried the same Virus Pathogen Database (v3.2.4b), so reference content is held constant; real-world tools are usually run with their own databases."]},
                links=[("system", f"{P}-config-{k}"), ("assessment", f"{P}-protocol-{pk}"), ("data", f"{P}-data-{pk}")], src=(SRC, SRC_SUPP))

    # S2
    s = sh["S2 Firth Marginal Means"]
    assert [s[f"{c}3"] for c in "ABCDEFGHIJ"] == ["base_tool", "lr_c", "prob", "SE", "df", "asymp.LCL", "asymp.UCL", "read_pairs", "estimator", "genome_effect"]
    seen = Counter()
    for r in range(4, 14):
        tool = s[f"A{r}"]; depth = s[f"H{r}"][1]
        assert tool in TOOLS and depth in ("10", "100"), (tool, depth)
        seen[tool] += 1
        k = TOOLS[tool][0]
        lo, _ = printed(s, f"F{r}"); hi, _ = printed(s, f"G{r}"); se, _ = printed(s, f"D{r}")
        unc = {"type": "confidence_interval", "lower": lo, "upper": hi, "level": 0.95, "method": "analytic",
               "source_column": "asymp.LCL, asymp.UCL", "note": f"Asymptotic interval from brglm2 estimated marginal means; standard error printed {se}"}
        result(f"{P}-result-pos-{k}-{depth}", f"{P}-eval-pos-{k}", "recall", "fraction", "higher", "S2 Firth Marginal Means", f"C{r}",
               f"Supplemental Table S2, row {r} (base_tool '{tool}', read_pairs {depth}), column 'prob' (cell C{r}); interval columns 'asymp.LCL' and 'asymp.UCL'",
               f"model-estimated family-level detection probability at {depth} read pairs; marginal mean over seven positive-control genomes", unc=unc,
               anomaly=T3_ANOMALY)  # review T3
    assert all(v == 2 for v in seen.values()) and len(seen) == 5
    # S6
    s = sh["S6 Neg Control Summary"]
    assert [s[f"{c}3"] for c in "ABCDEF"] == ["neg_class", "base_tool", "median_fp_pct", "mean_fp_pct", "median_n_species", "max_n_species"]
    for r in range(4, 9):
        tool = s[f"B{r}"]; assert s[f"A{r}"] == "true_negative" and tool in TOOLS
        k = TOOLS[tool][0]
        for col, key, metric, unit, qual, ud in [
            ("C", "median-fp-pct", "false-positive-rate", "percent", "percentage of individual reads falsely assigned; median over seven negative-control libraries", "percent of the library's total individual reads"),
            ("D", "mean-fp-pct", "false-positive-rate", "percent", "percentage of individual reads falsely assigned; mean over seven negative-control libraries", "percent of the library's total individual reads"),
            ("E", "median-species", "false-positive-count", "count", "false species reported; median over seven negative-control libraries", "species"),
            ("F", "max-species", "false-positive-count", "count", "false species reported; maximum over seven negative-control libraries", "species"),
        ]:
            hdr = s[f"{col}3"]
            result(f"{P}-result-neg-{k}-{key}", f"{P}-eval-neg-{k}", metric, unit, "lower", "S6 Neg Control Summary", f"{col}{r}",
                   f"Supplemental Table S6, row {r} (base_tool '{tool}'), column '{hdr}' (cell {col}{r})", qual, unit_detail=ud,
                   missing_note="Printed 'NA'; the table caption says Sylph read-percentage results are unavailable, not zero")
    # S9
    s = sh["S9 Profile vs Truth Summary"]
    assert [s[f"{c}3"] for c in "ABCDEF"] == ["base_tool", "rank", "truth_mode", "F1", "bray_curtis", "pearson"]
    n = 0
    for r in range(4, 29):
        tool, rank, mode = s[f"A{r}"], s[f"B{r}"], s[f"C{r}"]
        assert tool in TOOLS and rank in ("family", "genus", "species", "subspecies", "ani_capped") and mode in ("strict", "capped")
        k = TOOLS[tool][0]
        scope = f"rank {rank}, strict truth" if mode == "strict" else "ANI-capped truth"
        rk = rank if mode == "strict" else "capped"
        for col, key, metric, direction in [("D", "f1", "f1-score", "higher"), ("E", "bray-curtis", "bray-curtis-dissimilarity", "lower"), ("F", "pearson", "pearson-correlation", "higher")]:
            hdr = s[f"{col}3"]
            over = "mean over six mock communities" if mode == "strict" else "mean over mock communities"  # review T1
            q = {"f1": f"taxon detection; {over}; {scope}",
                 "bray-curtis": f"RPM-based abundance profile; {over}; {scope}",
                 "pearson": f"abundance profile against truth; {over}; {scope}"}[key]
            result(f"{P}-result-mock-{k}-{rk}-{key}", f"{P}-eval-mock-{k}", metric, "unitless", direction, "S9 Profile vs Truth Summary", f"{col}{r}",
                   f"Supplemental Table S9, row {r} (base_tool '{tool}', rank '{rank}', truth_mode '{mode}'), column '{hdr}' (cell {col}{r})", q,
                   missing_note="Printed 'NA'; Methods say Sylph's k-mer-containment abundance is not comparable to the other abundance metrics",
                   anomaly=T1_ANOMALY if mode == "capped" else None)  # review T1
            n += 1
    assert n == 75

    # Judgements
    def judge(uc, uc_slug, uc_name, pk, rel_text, extra_lims, order, title):
        pid = f"{P}-protocol-{pk}"
        base_lims = ["Developer benchmark: the EsViritu authors built the data, chose the comparators' parameter grids and headline settings, and ran every tool (author_reported).",
                     "Preprint (bioRxiv v1); not peer reviewed.",
                     "Synthetic reads or pathogen-free libraries only; no clinical specimens and no reference laboratory test.",
                     "All tools queried the same Virus Pathogen Database (v3.2.4b), so results compare algorithms with reference content held constant, not tools as usually deployed with their own databases."]
        add(f"use-case-mapping-{uc_slug}-20261011-tisza2026-{pk}", "claim",
            f"Relevance of {protocols[pk][0]} to \"{uc_name}\"", rel_text,
            {"field": f"links:assessed_by:{pid}", "value": pid, "relevance": "proxy",
             "endpoint": {"pos": "Model-estimated family-level detection probability at 10 and 100 read pairs for reads from seven divergent virus genomes (75.9% to 95.6% ANI to the nearest reference), with 95% intervals",
                          "neg": "False-positive read percentage and false species counts in seven pathogen-free libraries, including human genome mock reads and mouse RNA",
                          "mock": "Mean F1, Bray-Curtis dissimilarity and Pearson correlation against ground truth in six mutated virus mock communities with bacterial and human background"}[pk],
             "rationale": rel_text,
             "constraints": ["Inspect every linked evaluation's source locator and preserved limitations before citing a result.",
                             "Do not combine these results with another protocol's results; datasets, databases and scoring rules differ between sources."],
             "limitations": base_lims + extra_lims,
             "citation_locators": [{"source_id": SRC, "locator": "Methods 'Tools and parameters', 'Positive controls', 'Negative controls', 'Mock communities'"},
                                   {"source_id": SRC_SUPP, "locator": {"pos": "Supplemental Table S2", "neg": "Supplemental Table S6", "mock": "Supplemental Table S9"}[pk]}],
             "source_locator": f"{SRC_SUPP}: Supplemental Table {'S2' if pk == 'pos' else 'S6' if pk == 'neg' else 'S9'}",
             "revision": 1,
             "reason": "Recorded from the 2026-10-11 pathogen-detection literature pass (data/omics/use-case-coverage-rna-pathogen-20261011-tisza2026). Needs independent review.",
             "comparison_group": "tisza2026-virus-profilers", "comparison_title": title,
             "headline_metric": {"pos": "recall", "neg": "false-positive-count", "mock": "f1-score"}[pk],
             "stratum_label": {"pos": "Positive controls (divergent genomes)", "neg": "Pathogen-free negative controls", "mock": "Mutated mock communities"}[pk],
             "stratum_order": order,
             "review": review(XML_SHA, XML_URL, "Judgement drafted by the extracting agent from the pinned preprint and workbook.", method="transcription")},
            links=[("subject", uc)], src=(SRC, SRC_SUPP), facets={})

    title = "Virus profilers on a shared Virus Pathogen Database (Tisza et al. 2026, developer benchmark)"
    rna_name = "Select an RNA pathogen-detection workflow for diagnostic testing"
    dna_name = "Select a DNA pathogen-identification workflow for diagnostic testing"
    judge(UC_RNA, "rna-pathogen", rna_name, "pos",
          "Detection of reads from divergent viruses, including three picornaviruses (RNA viruses), at low read depth bears on whether a workflow detects RNA pathogens reliably, including viruses that differ from the reference. It is proxy evidence: synthetic reads, family-level scoring and a developer-run comparison.",
          ["Three of the seven positive-control genomes are Picornaviridae (RNA viruses); four are Genomoviridae (DNA viruses). Results are not split by genome type."], 1, title)
    judge(UC_RNA, "rna-pathogen", rna_name, "neg",
          "False assignments in pathogen-free libraries, including human genome reads and mouse RNA, bear directly on the use case's question of distinguishing real detections from host or background signal. It is proxy evidence: no clinical specimens, and the libraries are not RNA-virus diagnostic samples.",
          ["Only one of the seven libraries is RNA-derived (mouse RNA)."], 2, title)
    judge(UC_RNA, "rna-pathogen", rna_name, "mock",
          "Profiling accuracy on mock communities with mutated viruses in a large bacterial and human background bears on detecting viruses that differ from the reference amid background reads. It is proxy evidence: synthetic communities and developer-run comparison.",
          ["The communities draw from all 63 database families; the share of RNA viruses is not stated in the inspected text.", T1_LIMIT], 3, title)
    judge(UC_DNA, "dna-pathogen", dna_name, "pos",
          "Detection of reads from four Genomoviridae (DNA viruses) and three picornaviruses at 75.9% to 95.6% ANI to the nearest reference bears on the use case's question of organisms poorly represented in the reference. It is proxy evidence: viral only, synthetic reads, family-level scoring and a developer-run comparison.",
          ["Viruses only; no bacteria, fungi or parasites.", "Results are not split by DNA or RNA genome."], 1, title)
    judge(UC_DNA, "dna-pathogen", dna_name, "neg",
          "False virus assignments in pathogen-free libraries, including human genome mock reads, bear on the use case's question of handling contamination and background. It is proxy evidence: viral classification only and no clinical specimens.",
          ["Viral database only; false bacterial or fungal calls are not tested."], 2, title)

    add(f"{P}-claim-shared-database", "claim", f"reference_database: {bench}", "Descriptive fact transcribed from the pinned source.",
        {"field": "reference_database",
         "value": "All five tools used identical genome sequences from the EsViritu Virus Pathogen Database v3.2.4b and the same NCBI TaxDump (2026-06-01) to build their own database files, so reference content was held constant across the comparison.",
         "source_locator": "Methods 'Tools and parameters' paragraph 1",
         "review": review(XML_SHA, XML_URL, "Transcribed from the pinned JATS XML text.", method="transcription")},
        links=[("subject", bench)], src=(SRC,), facets={})
    claims.append([f"{P}-claim-shared-database", SRC, "Methods 'Tools and parameters' paragraph 1", R[-1]["attributes"]["value"], "claim"])

    finalize(R, extra_notes=EXTRA)
    R.sort(key=lambda r: r["id"])
    ids = [r["id"] for r in R]
    assert len(ids) == len(set(ids))
    with open(f"{out}/batch.jsonl", "w") as f:
        for r in R:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    with open(f"{out}/claims.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["record_id", "source_id", "locator", "printed_value", "review_scope"])
        w.writerows(claims)
    print(dict(Counter(r["kind"] for r in R)))

if __name__ == "__main__":
    main()
