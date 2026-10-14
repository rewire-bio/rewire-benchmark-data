"""Extract the remaining Feng et al. 2025 tables (issue rewire-benchmark-data#142).

Usage:
  python3 -I extract/extract_feng.py <epmc.xml> <MOESM3_ESM.xlsm> <MOESM1_ESM.pdf> <repo-root> <batch-folder>

Reads the pinned Europe PMC article XML (main Tables 2, 3, 5 and 6, Methods) and the pinned
Supplementary Data workbook (Supplementary Data 1, 2, 4 and 6). The Supplementary Information PDF is
hash-checked only; its Supplementary Notes 1 and 2 are cited by locator. <repo-root> is read, never
written: the script checks that every existing record it links to is in the canonical store.

Asserts every artifact hash, table caption, column header and row label, and the expected record
counts, before writing. All new records are written with status needs_review; an independent
review-evidence pass signs them off. Existing Feng records are reused and never changed.
"""
import csv, glob, hashlib, json, os, re, sys, zipfile
import xml.etree.ElementTree as ET
from decimal import Decimal, ROUND_HALF_UP

TODAY = "2026-10-14"
P = "feng-dna-fm-20261014"
PREV = "feng-dna-fm-20261013"
AMP = "amp-feng-20261007"
SRC = "evidence-expansion-dna-foundation-models-2025-5d8ca9bc"
SRC_SD = PREV + "-source-supplementary-data"
SRC_SI = PREV + "-source-supplementary-information"

XML_SHA = "5d8ca9bcf88cc1b38ad667906a2e4699b1aefa6d31c6f49259784930353f3202"
SD_SHA = "4804c801e0e054eca5f776617c18a6a0cb31d6ce3d2a7a52f70e4dda5b3abd7a"
SI_SHA = "373f59b825c9e2bc51a0f122a9e2653f427c492727fbf73768cc9af02d094a15"
XML_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12663285/fullTextXML"
SD_URL = "https://static-content.springer.com/esm/art%3A10.1038%2Fs41467-025-65823-8/MediaObjects/41467_2025_65823_MOESM3_ESM.xlsm"

EXTRACTOR_NOTE = ("Claude (Opus 5.5) extraction agent for rewire-benchmark-data#142; extraction only, not a review. "
                  "Pending an independent review-evidence pass.")
AREAS = ["dna-genomes"]
MODELS = ["DNABERT-2", "NT-v2", "HyenaDNA", "Caduceus-Ph", "GROVER"]

# Checkpoints named in Methods, "Model configuration selection": Hyena-160K is the "default choice of benchmarks".
CHECKPOINT = {"NT-v2": "NT-v2-500M", "HyenaDNA": "Hyena-160K", "Caduceus-Ph": "Caduceus-Ph-131K",
              "DNABERT-2": "DNABERT-2, its only published checkpoint", "GROVER": "GROVER, its only published checkpoint"}
CHECKPOINT_LOCATOR = "Methods, 'Model configuration selection' paragraph"

FOOTNOTE_BOLD = "Bolded: higher than at least two other AUCs, p < 0.01."

# Rows already in the store; not re-extracted.
T2_EXISTING = {"Promoter Arabidopsis NonTATA", "Promoter Arabidopsis TATA"}
T3_EXISTING = {("Human 5mC", "Caduceus-Ph"): "lit-001", ("Human 5mC", "NT-v2"): "lit-002"}
# Human 5mC already has a task and dataset record (discovery-era, needs_review); reuse both.
H5MC_TASK = "reported-task-988ff78f86471e"
H5MC_DATASET = "reported-dataset-463197d6a98b99"

T2_ROWS = ["Promoter Arabidopsis NonTATA", "Promoter Arabidopsis TATA", "Promoter B.Amyloliquefaciens", "Promoter R.Capsulatus",
           "Human vs worm", "Mouse TFBS 1", "Mouse TFBS 2", "Mouse TFBS 3", "Mouse TFBS 4", "Mouse TFBS 5"]
T3_ROWS = ["Human 5mC", "Human 6 mA", "Yeast H3", "Yeast H3K14ac", "Yeast H3K36me3", "Yeast H3K4me1", "Yeast H3K4me2", "Yeast H3K4me3",
           "Yeast H3K79me3", "Yeast H3K9ac", "Yeast H4", "Yeast H4ac", "A.Thaliana 4mC", "C.Elegans 4mC", "D.Melanogaster 4mC",
           "E.Coli 4mC", "G.Pickeringii 4mC", "G.Subterraneus 4mC"]

# Table label -> Supplementary Data 1/2/6 row label (the workbook spells some names differently).
SD_LABEL = {
    "Promoter B.Amyloliquefaciens": "Promoter B_amyloliquefaciens", "Promoter R.Capsulatus": "Promoter R_capsulatus",
    "Human vs worm": "Human vs Worm", "Human 5mC": "5mC", "Human 6 mA": "6mA",
    "A.Thaliana 4mC": "A.thaliana 4mC", "C.Elegans 4mC": "C.elegans 4mC", "D.Melanogaster 4mC": "D.melanogaster 4mC",
    "E.Coli 4mC": "E.coli_4mC", "G.Pickeringii 4mC": "G.pickeringii 4mC", "G.Subterraneus 4mC": "G.subterraneus 4mC",
}
for _l in T2_ROWS + T3_ROWS:
    SD_LABEL.setdefault(_l, _l)

SN1 = "Supplementary Note 1 (Supplementary Information pages 1-2)"
ORIGIN = {
    "Promoter B.Amyloliquefaciens": ("Multispecies promoter identification benchmark, B. amyloliquefaciens set (Methods, 'Sequence classification datasets', promoter identification in multiple species; " + SN1 + ")", "B. amyloliquefaciens (as printed)"),
    "Promoter R.Capsulatus": ("Multispecies promoter identification benchmark, R. capsulatus set (Methods, 'Sequence classification datasets', promoter identification in multiple species; " + SN1 + ")", "R. capsulatus (as printed)"),
    "Human vs worm": ("Genomic Benchmarks demo_human_or_worm (" + SN1 + "); human versus Caenorhabditis elegans genome sequences", "Homo sapiens and Caenorhabditis elegans"),
    "Human 5mC": ("Human 5-methylcytosine (5mC) detection benchmark dataset (Methods, 'Sequence classification datasets', 5mC and 6 mA modifications detection in human; " + SN1 + ")", "Homo sapiens"),
    "Human 6 mA": ("Human N6-methyladenosine (6mA) detection benchmark dataset (Methods, 'Sequence classification datasets', 5mC and 6 mA modifications detection in human; " + SN1 + ")", "Homo sapiens"),
}
for _i in range(1, 6):
    ORIGIN[f"Mouse TFBS {_i}"] = ("DNABERT-2 benchmark mouse transcription factor binding site prediction set (" + SN1 + ", datasets adopted from DNABERT-2)", "mouse")
for _l in T3_ROWS:
    if _l.startswith("Yeast"):
        ORIGIN[_l] = ("DNABERT-2 benchmark yeast epigenetic marks prediction set (" + SN1 + ", datasets adopted from DNABERT-2)", None)
FOURMC_SPECIES = {"A.Thaliana 4mC": "A. thaliana", "C.Elegans 4mC": "C. elegans", "D.Melanogaster 4mC": "D. melanogaster",
                  "E.Coli 4mC": "E. coli", "G.Pickeringii 4mC": "G. pickeringii", "G.Subterraneus 4mC": "G. subterraneus"}
for _l, _sp in FOURMC_SPECIES.items():
    ORIGIN[_l] = (f"N4-methylcytosine (4mC) site detection benchmark, {_sp} set of six species datasets; 41 bp sequences centred on potential 4mC sites "
                  "(Methods, 'Sequence classification datasets', 4mC site detection in multiple species; " + SN1 + ")", _sp + " (as printed)")

# Supplementary Note 2 (Supplementary Information pages 1-2): reliance on experimental or gold-standard evidence.
SN2 = "Supplementary Note 2 (Supplementary Information pages 3-4)"
NOT_EXPERIMENTAL = {f"Mouse TFBS {i}" for i in range(1, 6)}
EUKARYOTIC_4MC = {"A.Thaliana 4mC", "C.Elegans 4mC", "D.Melanogaster 4mC"}

SPLIT_RULE = ("Original predefined split retained where clearly defined; otherwise a random 70:30 train/test split. "
              "DNABERT-2/NT-v2 benchmark datasets are re-split 70:30 keeping class proportions. "
              "Random forest hyperparameters tuned by fivefold cross-validation. No whole-chromosome holdout (Methods, 'Sequence classification benchmark').")
SCOPE = ("Frozen last-layer mean token embeddings from each pretrained model, scored by a supervised random forest classifier "
         "fitted for this exact task (not label-free prediction). " + SPLIT_RULE)

# Supplementary Data 4: three outer test groups, defined in Methods, 'Variant effect quantification benchmark'.
GROUPS = {1: "chromosomes 3, 6, 9, 12, 16, 18, 19, 21", 2: "chromosomes 2, 5, 11, 14, 17, 20, 22, X", 3: "chromosomes 1, 4, 7, 8, 10, 13, 15"}
SD4_BLOCKS = [("Pathogenic variants vs common", "variant", "Table 5", None, 11),
              ("eQTL", "qtl-eqtl", "Table 6", "eQTL", 12), ("sQTL", "qtl-sqtl", "Table 6", "sQTL", 12),
              ("paQTL", "qtl-paqtl", "Table 6", "paQTL", 12), ("ipaQTL", "qtl-ipaqtl", "Table 6", "ipaQTL", 12)]
# Supplementary Data 4 model label -> (existing evaluation suffix, Table 5/6 row label).
SD4_MODEL = {
    "AlphaGenome, output tracks": ("alphagenome-output-tracks", "AlphaGenome, output tracks*"),
    "Caduceus-Ph": ("caduceus-ph", "Caduceus-Ph"),
    "Caduceus-Ph, long sequence": ("caduceus-ph-long-sequence", "Caduceus-Ph, long sequence"),
    "DNABERT-2": ("dnabert-2", "DNABERT-2"),
    "Enformer, hidden states": ("enformer-hidden-states", "Enformer, hidden states*"),
    "Enformer, output tracks": ("enformer-output-tracks", "Enformer, output tracks*"),
    "GROVER": ("grover", "GROVER"),
    "HyenaDNA-160K": ("hyenadna", "HyenaDNA"),
    "HyenaDNA-450K, long sequence": ("hyenadna-450k-long-sequence", "HyenaDNA-450K, long sequence"),
    "NT-v2": ("nt-v2", "NT-v2"),
    "Sei, hidden states": ("sei-hidden-states", "Sei, hidden states*"),
    "Sei, output tracks": ("sei-output-tracks", "Sei, output tracks*"),
}


def slug(s):
    s = s.lower().replace("+", " plus ").replace("’", "").replace("'", "")
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return re.sub(r"-+", "-", s)


def sha256(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def num(printed):
    t = printed.strip().replace("−", "-")
    return t if re.fullmatch(r"-?\d+(\.\d+)?", t) else None


# ---------------------------------------------------------------- source readers
def read_xml_tables(path):
    t = open(path, encoding="utf-8").read()
    t = re.sub(r'xmlns(:\w+)?="[^"]*"', "", t)
    t = re.sub(r"<(/?)\w+:", r"<\1", t)
    t = re.sub(r'\s\w+:\w+="[^"]*"', "", t)
    root = ET.fromstring(t)
    txt = lambda e: " ".join("".join(e.itertext()).split())
    tables = {}
    for tw in root.iter("table-wrap"):
        rows = []
        for tr in tw.iter("tr"):
            rows.append([{"text": txt(c), "bold": c.find("bold") is not None} for c in tr if c.tag in ("td", "th")])
        foot = tw.find("table-wrap-foot")
        tables[tw.get("id")] = {"caption": txt(tw.find("caption")), "rows": rows, "foot": txt(foot) if foot is not None else ""}
    return tables


def read_workbook(path):
    """Sheet name -> list of rows; each row maps column letter to (value, cell reference, is_number)."""
    z = zipfile.ZipFile(path)
    ns = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    ss = ["".join(t.text or "" for t in si.iter("{%s}t" % ns["m"]))
          for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall("m:si", ns)]
    wb = ET.fromstring(z.read("xl/workbook.xml"))
    rels = {r.get("Id"): r.get("Target") for r in ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))}
    styles = ET.fromstring(z.read("xl/styles.xml"))
    xfs = [xf.get("numFmtId") for xf in styles.find("m:cellXfs", ns)]
    sheets = {}
    for s in wb.find("m:sheets", ns):
        rid = s.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id")
        sh = ET.fromstring(z.read("xl/" + rels[rid].replace("/xl/", "")))
        rows = []
        for row in sh.iter("{%s}row" % ns["m"]):
            vals = {}
            for c in row.findall("m:c", ns):
                v = c.find("m:v", ns)
                if v is None:
                    continue
                col = re.match(r"[A-Z]+", c.get("r")).group(0)
                is_str = c.get("t") == "s"
                if not is_str:
                    # Numbers must use the General format (numFmtId 0) so the displayed value is the shortest decimal.
                    assert xfs[int(c.get("s", "0"))] == "0", (s.get("name"), c.get("r"))
                vals[col] = (ss[int(v.text)] if is_str else v.text, c.get("r"), not is_str)
            rows.append(vals)
        sheets[s.get("name")] = rows
    return sheets


def general(raw):
    """Value as Excel's General format displays a stored double with at most 4 decimals."""
    shown = repr(float(raw))
    assert re.fullmatch(r"0\.\d{1,4}", shown), raw
    return shown


def read_store(root):
    recs = {}
    for f in sorted(glob.glob(os.path.join(root, "data", "entities", "**", "*.jsonl"), recursive=True)
                    + glob.glob(os.path.join(root, "data", "evidence", "**", "*.jsonl"), recursive=True)):
        for line in open(f, encoding="utf-8"):
            if line.strip():
                r = json.loads(line)
                recs[r["id"]] = r
    return recs


# ---------------------------------------------------------------- record builders
class Batch:
    def __init__(self):
        self.records, self.ids, self.rows = [], set(), []

    def add(self, rec):
        assert rec["id"] not in self.ids, rec["id"]
        self.ids.add(rec["id"])
        mm = rec["attributes"].get("missing_metadata")
        if mm:
            rec["attributes"]["missing_metadata"] = dict(sorted(mm.items()))
        self.records.append(rec)
        return rec["id"]

    def entity(self, kind, id, name, description, attrs, source_ids=(SRC,), method_types=None, links=()):
        facets = {"areas": AREAS, "contexts": ["research"]}
        if method_types:
            facets["method_types"] = method_types
        return self.add({"id": id, "kind": kind, "name": name, "description": description, "status": "needs_review",
                         "facets": facets, "source_ids": list(source_ids), "links": list(links), "attributes": attrs})

    def claim(self, id, name, subject, attrs, source_ids, links=()):
        self.rows.append([id, source_ids[0], attrs.get("source_locator", ""), str(attrs.get("value", ""))[:200], "claim"])
        return self.add({"id": id, "kind": "claim", "name": name, "description": "Descriptive fact transcribed from the pinned source.",
                         "status": "needs_review", "facets": {}, "source_ids": list(source_ids),
                         "links": [{"relation": "subject", "target_id": subject}] + list(links), "attributes": attrs})

    def result(self, rid, name, ev, attrs, source_id):
        self.rows.append([rid, source_id, attrs["source_locator"], attrs["printed_value"], "result"])
        return self.add({"id": rid, "kind": "result", "name": name,
                         "description": "Reported measurement transcribed from the pinned source. Not independently reproduced.",
                         "status": "needs_review", "facets": {}, "source_ids": [source_id],
                         "links": [{"relation": "evaluation", "target_id": ev}], "attributes": attrs})


def extraction_review(method_note, sha, url, note=""):
    return {"method": ["deterministic-table-parse"], "method_note": method_note, "reviewer": ["claude"],
            "reviewer_note": EXTRACTOR_NOTE, "date": TODAY, "artifact_sha256": sha, "retrieval_url": url,
            "note": ("Extracted, not reviewed. The review-evidence pass must re-check this cell against the pinned artifact. " + note).strip()}


def main(xml_path, sd_path, si_path, root, out):
    for path, want in ((xml_path, XML_SHA), (sd_path, SD_SHA), (si_path, SI_SHA)):
        got = sha256(path)
        assert got == want, f"{path}: {got} != {want}"
    tables = read_xml_tables(xml_path)
    wb = read_workbook(sd_path)
    store = read_store(root)
    for rid in (SRC, SRC_SD, SRC_SI, H5MC_TASK, H5MC_DATASET, *T3_EXISTING.values(), PREV + "-claim-not-extracted"):
        assert rid in store, rid
    b = Batch()
    coverage = {"sd4_mean_check": [], "counts": {}}

    def sheet_map(name):
        return {r["A"][0].strip(): {k: v[0] for k, v in r.items()} for r in wb[name][1:] if "A" in r}

    sd1, sd2, sd6 = sheet_map("Data 1"), sheet_map("Data 2"), sheet_map("Data 6")
    assert wb["Data 1"][0]["B"][0] == "Baseline CNN Performs Better Than"
    assert wb["Data 2"][0]["B"][0] == "Models that Outperform Baseline CNN"
    assert wb["Data 6"][0]["E"][0] == "Training Size" and wb["Data 6"][0]["F"][0] == "Testing Size"
    assert wb["Data 6"][0]["G"][0] == "Label Distribution (Positive/Negative)"

    # ------------------------------------------------------------ Tables 2 and 3
    def seq_table(tid, table_label, caption_start, row_labels, existing_rows, existing_cells):
        t = tables[tid]
        assert t["caption"].startswith(caption_start), t["caption"]
        assert FOOTNOTE_BOLD in t["foot"], t["foot"]
        assert [c["text"] for c in t["rows"][0]] == ["Data"] + MODELS
        body = t["rows"][1:]
        assert [r[0]["text"] for r in body] == row_labels, [r[0]["text"] for r in body]
        n_results, protocols = 0, {}
        tl = "t" + table_label[-1]
        for row in body:
            label = row[0]["text"]
            if label in existing_rows:
                continue
            cells = row[1:]
            assert len(cells) == 5
            s = slug(label)
            sdl = SD_LABEL[label]
            sd = sd6[sdl]
            train, test = int(sd["E"]), int(sd["F"])
            origin, species = ORIGIN[label]
            population = origin + f"; sequence length median {sd['B']} bp (range {sd['C']}-{sd['D']} bp) per Supplementary Data 6."
            split = SPLIT_RULE + f" Supplementary Data 6: {train} training and {test} test sequences."
            pos, neg = (int(x) for x in sd["G"].split("/"))
            notes = []
            if pos + neg != train + test:
                notes.append(f"Supplementary Data 6 label counts ({pos}/{neg}) do not sum to training plus test size ({train + test}).")
            if label in NOT_EXPERIMENTAL:
                notes.append(SN2 + " marks this dataset as not fully relying on experimental evidence or gold-standard sources.")
            if label.startswith("Yeast"):
                notes.append(SN2 + " lists 'All Yeast Datasets' as 'Unknown' for reliance on experimental evidence or gold-standard sources. The yeast species is not named in the article.")
            if label in EUKARYOTIC_4MC:
                notes.append("Methods ('Sequence classification datasets') state that for eukaryotic species 4mC site annotations often rely on computational predictions rather than direct genome-wide chemical mapping; Results treat these tasks as exploratory.")
            if label in existing_cells_rows(existing_cells):
                ds = H5MC_DATASET
                links = [{"relation": "evaluates_task", "target_id": H5MC_TASK}, {"relation": "uses_data", "target_id": H5MC_DATASET}]
            else:
                ds_attrs = {"population": population, "split": split,
                            "test_denominator": f"{test} test sequences (Supplementary Data 6, row '{sdl}', column 'Testing Size')",
                            "positives": pos, "negatives": neg, "total": pos + neg,
                            "source_locator": f"Supplementary Data 6, row '{sdl}'; {SN1}",
                            "missing_metadata": {"version": {"reason": "unextracted", "note": "Upstream dataset release not stated in the article."}}}
                if species:
                    ds_attrs["species"] = species
                else:
                    ds_attrs["missing_metadata"]["species"] = {"reason": "unreported", "note": "The article says 'yeast' only."}
                if notes:
                    ds_attrs["scope_note"] = " ".join(notes)
                ds = b.entity("dataset", f"{P}-dataset-{tl}-{s}", f"Feng {label} dataset",
                              f"{origin}; as used in Feng et al. 2025 {table_label}.", ds_attrs, source_ids=(SRC, SRC_SD, SRC_SI))
                links = []
            pattrs = {"scope_note": SCOPE + (" " + " ".join(notes) if notes and ds == H5MC_DATASET else ""),
                      "task": f"{label} sequence classification (AUC)", "version": table_label,
                      "metric": "auroc", "metric_direction": "higher",
                      "comparison_limit": "Within-row comparison only: rows differ in source dataset, species, sequence length and split."}
            if ds == H5MC_DATASET:
                pattrs["scope_note"] += (" The Caduceus-Ph and NT-v2 cells of this row were extracted earlier (results lit-001 and lit-002, evaluations "
                                         "evaluation-lit-001 and evaluation-lit-002 on task " + H5MC_TASK + "); this protocol carries the other three cells. "
                                         f"Supplementary Data 6: {train} training and {test} test sequences, {pos}/{neg} positive/negative.")
            proto = b.entity("protocol", f"{P}-protocol-{tl}-{s}", f"Feng {label} sequence classification",
                             f"{table_label} sequence classification; Feng et al. 2025 source-reported protocol.",
                             pattrs, source_ids=(SRC, SRC_SD), links=links)
            protocols[label] = proto
            for model, cell in zip(MODELS, cells):
                if (label, model) in existing_cells:
                    assert existing_cells[(label, model)] in store
                    assert store[existing_cells[(label, model)]]["attributes"]["printed_value"] == cell["text"], (label, model)
                    continue
                ms = slug(model)
                cattrs = {"foundation_model_eligible": True, "head": "Supervised random forest fitted separately for this task",
                          "reported_name": model, "representation": "Frozen last-layer mean token embeddings", "task": f"{label} classification",
                          "checkpoint": CHECKPOINT[model] + " (" + CHECKPOINT_LOCATOR + ")",
                          "missing_metadata": {"head_revision": {"reason": "unextracted"},
                                               "version": {"reason": "unreported", "note": "Immutable checkpoint revision is not stated in the article."}}}
                cfg = b.entity("configuration", f"{P}-config-{tl}-{s}-{ms}", f"{model} ({label} classification)",
                               f"{model} ({label} classification); Feng et al. 2025 source-reported, task-scoped configuration.",
                               cattrs, method_types=["foundation_model"])
                ev = b.entity("evaluation", f"{P}-eval-{tl}-{s}-{ms}", f"{model} {label} evaluation",
                              f"{model} {label} sequence-classification evaluation; Feng et al. 2025. Transcribed, not reproduced.",
                              {"origin": "independent_paper", "protocol": f"{table_label}, frozen embeddings + task-specific random forest classifier",
                               "comparison": {"adaptation": "Frozen pretrained representation plus a supervised random-forest classifier head fitted for this exact task",
                                              "aggregation": None, "budget": None, "dataset_version": None,
                                              "inputs": f"DNA sequence windows for {label} classification", "metric_implementation": None,
                                              "population": population, "protocol_id": proto, "split": split},
                               "missing_metadata": {"budget": {"reason": "unextracted", "note": "Not extracted; no execution"},
                                                    "metric_implementation": {"reason": "unreported", "note": "Exact scoring implementation beyond AUC is unreported."},
                                                    "version": {"reason": "unextracted"}}},
                              links=[{"relation": "assessment", "target_id": proto}, {"relation": "system", "target_id": cfg},
                                     {"relation": "data", "target_id": ds}])
                printed = cell["text"]
                n = num(printed)
                assert n is not None, (label, model, printed)
                bold = f" Printed in bold (table footnote: '{FOOTNOTE_BOLD}')." if cell["bold"] else ""
                loc = f"{table_label}, row '{label}', column '{model}'.{bold}"
                b.result(f"{P}-result-{tl}-{s}-{ms}-auc", f"{model} {label} AUC", ev,
                         {"metric": "auroc", "metric_direction": "higher", "unit": "unitless", "printed_value": printed,
                          "numeric_value": n, "metric_qualifier": f"task: {label.lower()}", "source_locator": loc,
                          "missing_metadata": {"uncertainty": {"reason": "unreported", "note": f"{table_label} prints point AUCs only."}},
                          "review": extraction_review(f"Deterministic parse of the pinned Europe PMC XML table cells (table id {tid}), header and row labels asserted.", XML_SHA, XML_URL)},
                         SRC)
                n_results += 1
        return n_results, protocols

    def existing_cells_rows(cells):
        return {label for label, _ in cells}

    n2, t2_protocols = seq_table("Tab2", "Table 2", "The AUC results for binary sequence classification tasks which have multiple species involved",
                                 T2_ROWS, T2_EXISTING, {})
    assert n2 == 40, n2
    n3, t3_protocols = seq_table("Tab3", "Table 3", "The AUC results for each model on 5mC, 6 mA detection in human",
                                 T3_ROWS, set(), T3_EXISTING)
    assert n3 == 88, n3
    coverage["counts"]["table_2_results"], coverage["counts"]["table_3_results"] = n2, n3

    # ------------------------------------------------------------ CNN comparator claims (Supplementary Data 1 and 2)
    n_cnn = 0
    for table, protos in (("Table 2", t2_protocols), ("Table 3", t3_protocols)):
        for label, proto in sorted(protos.items()):
            key = SD_LABEL[label]
            beaten, better = sd1[key]["B"].strip(), sd2[key]["B"].strip()
            value = (f"Baseline CNN trained from scratch on {label}: Supplementary Data 1 lists the DNA foundation models the CNN significantly outperformed "
                     f"(one-sided DeLong p<0.01): {beaten}. Supplementary Data 2 lists the models that significantly outperformed the CNN: {better}. "
                     f"The CNN's AUC is not printed, so it has no result record; the foundation-model AUCs are in {table}.")
            b.claim(f"{P}-claim-cnn-{slug(label)}", f"reported_finding: {proto}", proto,
                    {"field": "reported_finding", "value": value,
                     "source_locator": f"Supplementary Data 1 and Supplementary Data 2, row '{key}'",
                     "review": extraction_review("Deterministic parse of the pinned Supplementary Data workbook sheets 'Data 1' and 'Data 2'; row label asserted.", SD_SHA, SD_URL)},
                    [SRC_SD, SRC])
            n_cnn += 1
    assert n_cnn == 26, n_cnn
    coverage["counts"]["cnn_claims"] = n_cnn

    # ------------------------------------------------------------ Supplementary Data 4 (per-chromosome-group AUCs)
    t5, t6 = tables["Tab5"], tables["Tab6"]
    assert [c["text"] for c in t5["rows"][0]] == ["Model", "AUC", "Cohen’s d"]
    t5_auc = {r[0]["text"]: r[1]["text"] for r in t5["rows"][1:]}
    assert [c["text"] for c in t6["rows"][0]] == ["", "Model", "eQTL", "sQTL", "paQTL", "ipaQTL"]
    t6_rows = t6["rows"][1:]
    assert t6_rows[0][0]["text"] == "AUC" and t6_rows[12][0]["text"] == "Cohen’s d"
    t6_auc = {}
    for i, r in enumerate(t6_rows[:12]):
        cells = r[1:] if i == 0 else r
        t6_auc[cells[0]["text"]] = {q: c["text"] for q, c in zip(["eQTL", "sQTL", "paQTL", "ipaQTL"], cells[1:])}

    rows = wb["Data 4"]
    i, n_sd4 = 0, 0
    for title, key, table_label, column, n_models in SD4_BLOCKS:
        while not rows[i] or rows[i].get("A", ("",))[0] != title:
            i += 1
        header = rows[i + 1]
        assert [header[c][0] for c in "ABCD"] == ["Model name", "Test Group 1 AUC", "Test Group  2 AUC", "Test Group 3 AUC"], header
        block = rows[i + 2:i + 2 + n_models]
        want = sorted(SD4_MODEL) if n_models == 12 else [m for m in sorted(SD4_MODEL) if not m.startswith("AlphaGenome")]
        assert [r["A"][0] for r in block] == want, [r["A"][0] for r in block]
        assert len(rows) == i + 2 + n_models or not rows[i + 2 + n_models], rows[i + 2 + n_models]
        for r in block:
            label = r["A"][0]
            ev_suffix, table_row = SD4_MODEL[label]
            ev = f"{AMP}-eval-{key}-{ev_suffix}"
            assert ev in store and store[ev]["kind"] == "evaluation", ev
            auc_results = [x for x in store.values() if x["kind"] == "result" and x["attributes"].get("metric") == "auroc"
                           and any(l["relation"] == "evaluation" and l["target_id"] == ev for l in x["links"])]
            assert len(auc_results) == 1, (ev, len(auc_results))
            base_qual = auc_results[0]["attributes"]["metric_qualifier"]
            printed_mean = t5_auc[table_row] if column is None else t6_auc[table_row][column]
            assert auc_results[0]["attributes"]["printed_value"] == printed_mean, (ev, printed_mean)
            values = []
            for g, col in ((1, "B"), (2, "C"), (3, "D")):
                raw, ref, is_num = r[col]
                assert is_num, ref
                printed = general(raw)
                values.append(Decimal(printed))
                hdr = header[col][0]
                loc = (f"Supplementary Data 4 (workbook sheet 'Data 4'), block '{title}', row '{label}', column '{hdr}' (cell {ref}). "
                       f"Test group {g} is {GROUPS[g]} (Methods, 'Variant effect quantification benchmark').")
                note = ("The workbook stores the cell as a binary double in General number format; printed_value is the value as displayed. "
                        f"This per-group AUC is one of the three test-set values whose mean is the {table_label} cell already stored as {auc_results[0]['id']}.")
                if label == "HyenaDNA-160K":
                    note += (" Supplementary Data 4 labels this row 'HyenaDNA-160K'; Table " + table_label[-1] + " prints 'HyenaDNA', and Methods ('Model configuration selection') "
                             "say Hyena-450K was used for variant effect quantification. The row is linked by its matching mean; the checkpoint conflict is left for review.")
                block_slug = "pathogenic-common" if key == "variant" else key
                b.result(f"{P}-result-sd4-{block_slug}-{ev_suffix}-group-{g}-auc",
                         f"{label} {title} AUC, test group {g}", ev,
                         {"metric": "auroc", "metric_direction": "higher", "unit": "unitless", "printed_value": printed, "numeric_value": printed,
                          "metric_qualifier": f"{base_qual}; outer test group {g} only ({GROUPS[g]}), not averaged",
                          "source_locator": loc,
                          "missing_metadata": {"uncertainty": {"reason": "unreported", "note": "Supplementary Data 4 prints one AUC per test group, with no interval."}},
                          "review": extraction_review("Deterministic parse of the pinned Supplementary Data workbook sheet 'Data 4'; block titles, column headers and model labels asserted; number format asserted as General.", SD_SHA, SD_URL, note)},
                         SRC_SD)
                n_sd4 += 1
            # Linkage check: the mean of the three displayed group AUCs must be within 0.0001 of the stored Table 5/6
            # mean (the paper averaged unrounded values, so the last digit can differ by one).
            mean = (sum(values) / 3).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
            diff = abs(Decimal(num(printed_mean)) - mean)
            assert diff <= Decimal("0.0001"), (ev, values, printed_mean)
            coverage["sd4_mean_check"].append({"evaluation": ev, "block": title, "sd4_row": label,
                                               "groups": [str(v) for v in values], "mean_4dp": str(mean),
                                               "table_value": printed_mean, "matches": diff == 0, "abs_diff": str(diff)})
        i += 2 + n_models
    assert n_sd4 == 177, n_sd4
    coverage["counts"]["sd4_results"] = n_sd4

    # ------------------------------------------------------------ coverage claim on the article source (supersedes the 2026-10-13 one)
    b.claim(f"{P}-claim-not-extracted", f"tables_not_extracted: {SRC}", SRC,
            {"field": "tables_not_extracted",
             "value": ("Not extracted as results: Cohen's d per test group (Supplementary Data 4 prints AUC only); Supplementary Tables 1-4 "
                       "(pooling counts, multi-class accuracy, random forest vs XGBoost, short vs long input); Supplementary Data 3 (top genes) and 5 "
                       "(HyenaDNA re-pretraining); Supplementary Tables 5-8 (hyperparameter grids, embedding dimensions) and Supplementary Fig. 1 "
                       "(classifier comparison); Figures 2-4 including runtime. Tables 1-6 and Supplementary Data 4 are now fully extracted. "
                       "The remaining parts are outside the use cases or repeat main-table values at another aggregation."),
             "source_locator": "Supplementary Tables 1-8 and Supplementary Fig. 1; Supplementary Data 3-5; Figures 2-4",
             "review": extraction_review("Inventory of the pinned article XML, Supplementary Information PDF and Supplementary Data workbook.", XML_SHA, XML_URL)},
            [SRC, SRC_SI, SRC_SD], links=[{"relation": "supersedes", "target_id": PREV + "-claim-not-extracted"}])

    # ------------------------------------------------------------ write
    for r in b.records:
        assert r["id"] not in store, f"{r['id']} already in the store"
    os.makedirs(out, exist_ok=True)
    recs = sorted(b.records, key=lambda r: r["id"])
    with open(os.path.join(out, "batch.jsonl"), "w") as f:
        for r in recs:
            f.write(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n")
    with open(os.path.join(out, "claims.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["record_id", "source_id", "locator", "printed_value", "review_scope"])
        for row in sorted(b.rows):
            w.writerow(row)
    counts = {}
    for r in recs:
        counts[r["kind"]] = counts.get(r["kind"], 0) + 1
    coverage["counts"]["by_kind"] = dict(sorted(counts.items()))
    with open(os.path.join(out, "extract", "sd4-mean-check.json"), "w") as f:
        json.dump(coverage, f, indent=1, ensure_ascii=False)
        f.write("\n")
    print(json.dumps(coverage["counts"], sort_keys=True))
    bad = [c for c in coverage["sd4_mean_check"] if not c["matches"]]
    print(f"Supplementary Data 4 means that differ from the Table 5/6 value in the last digit (all within 0.0001): {len(bad)}")
    for c in bad:
        print(" ", c["evaluation"], c["groups"], c["mean_4dp"], "printed", c["table_value"])


if __name__ == "__main__":
    main(*sys.argv[1:6])
