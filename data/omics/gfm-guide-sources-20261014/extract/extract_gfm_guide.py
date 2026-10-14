"""Extract the 2026 genomic foundation model guide sources listed in rewire-benchmark-data#138.

Usage:
  python3 -I extract/extract_gfm_guide.py <artifact-dir> <batch-folder>

<artifact-dir> holds the pinned artifacts under the file names in ARTIFACTS below. Every artifact hash is
asserted before anything is read. Table cells are parsed from the XML table markup (Hegde et al.) or from
`pdftotext -layout` of the pinned PDFs (NTv3 Table 5, HyenaDNA Table A.2, EVEE manuscript-repository
Figure 1c and 1d), with row and column labels asserted. Prose values are asserted as exact substrings of
the artifact text. All records are written with status needs_review; the review-evidence pass signs them off.
Existing records (models, methods, datasets and AlphaGenome sources) are reused, never changed.
"""
import csv, hashlib, json, os, re, subprocess, sys
import xml.etree.ElementTree as ET

TODAY = "2026-10-14"
EXTRACTED_AT = "2026-10-14T12:58:25Z"  # when the concerns were written by the extractor
P = "gfm-guide-20261014"
EXTRACTOR_NOTE = ("Claude (Opus 5.5) extraction agent for rewire-benchmark-data#138; extraction only, not a review. "
                  "Pending an independent review-evidence pass.")
AREAS = ["dna-genomes"]

EVEE_COMMIT = "e5e4a43d60bb217819144c09ab509ed44f49cd5f"
EVEE_RAW = f"https://raw.githubusercontent.com/goodfire-ai/evee-manuscript/{EVEE_COMMIT}/"
HF_REV = "eed1f6737819a3f79b415a42fb1911fa61ef33e9"

# file name -> (sha256, retrieval url, retrieved_at)
ARTIFACTS = {
    "evee-v4.full.pdf": ("1d65b07059c50e8e3f88b8fde950f011630886097bf2784a6653282c6424eef8",
                         "https://www.biorxiv.org/content/biorxiv/early/2026/07/11/2026.04.10.717844.full.pdf", "2026-10-14T12:02:25Z"),
    "fig1c_deconf_heatmap.pdf": ("3dd79f2055d965fa486ae6c33193c646bb21db51f1491694111b9c96d148eec6",
                                 EVEE_RAW + "figures/figure1/fig1c_deconf_heatmap.pdf", "2026-10-14T12:48:26Z"),
    "fig1d_indel_heatmap.pdf": ("b1ec938f98392f1b169798f0d9232337d0635ee909e103745151c0c572578136",
                                EVEE_RAW + "figures/figure1/fig1d_indel_heatmap.pdf", "2026-10-14T12:48:26Z"),
    "_heatmap_common.py": ("1d477d2e1eb4213591015b26baca654e5ca1ca19ee9a1fd39e5f106fc8e56e2e",
                           EVEE_RAW + "scripts/figure1/_heatmap_common.py", "2026-10-14T12:48:26Z"),
    "fig1d_indel_heatmap.py": ("5c03755c6807fef579e234676d86b9e6a20d675e0d520e656e8a60615331e34d",
                               EVEE_RAW + "scripts/figure1/fig1d_indel_heatmap.py", "2026-10-14T12:48:26Z"),
    "evo2-details.json": ("8b50005d8a5e8f37d9e504dec246994bf21a326cfb17dcdd086683db616d2254",
                          "https://api.biorxiv.org/details/biorxiv/10.1101/2025.02.18.638918", "2026-10-14T12:48:26Z"),
    "PMC12652071.xml": ("9ea68b688637b40f0aeced7c905822f6b14c352a3a935c61c407945f3d66ef47",
                        "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12652071/fullTextXML", "2026-10-14T12:48:26Z"),
    "ntv3-v1.full.pdf": ("374a7177ebf75bf9ce6398624a74e4d588581d54a13ba12263d146b194b961ea",
                         "https://www.biorxiv.org/content/biorxiv/early/2025/12/25/2025.12.22.695963.full.pdf", "2026-10-14T12:05:27Z"),
    "PMC11810778.xml": ("7c3b78a4f38ef053a08e466222e5662dd9711d91c535512d0b35d459d1fc7249",
                        "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11810778/fullTextXML", "2026-10-14T12:48:26Z"),
    "hyena.pdf": ("2f471549352ff571ac55faa80c8da453f9bf1ff5b01b6b87fa893457828e798c",
                  "https://arxiv.org/pdf/2306.15794v2", "2026-10-14T12:48:26Z"),
    "hf-readme.md": ("273893718e3d9ec1adcd462b52127f5a201217d6c39d1bfd13fd963caa2598f1",
                     f"https://huggingface.co/LongSafari/hyenadna-tiny-1k-seqlen/resolve/{HF_REV}/README.md", "2026-10-14T12:41:27Z"),
    "PMC12851941.xml": ("50d10530afd474d85702813bc9c9e5431406515e44f3425d64603fdb647fee13",
                        "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12851941/fullTextXML", "2026-10-14T12:48:26Z"),
    "MOESM1.pdf": ("86b2e6a07543e3c201e2e157a3e9c6eb5235ff13eb8a5224f6fcb6fe1808d4c0",
                   "https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fs41586-025-10014-0/MediaObjects/41586_2025_10014_MOESM1_ESM.pdf", None),
    "README-0db53bd.md": ("c715b22c31bd4f69e9b76236de0ab6a26c96fa0f384ad56a2f9d2cb65e262681",
                          "https://raw.githubusercontent.com/google-deepmind/alphagenome_research/0db53bd4352c66d1e00a049a81da373a066e6670/README.md", None),
}

# Existing records reused (never changed).
M_EVO2 = "discovery-model-evo-2"
M_CADD = "somatic-oncogenicity-20261009-method-cadd"
M_AM = "somatic-oncogenicity-20261009-method-alphamissense"
M_GPN = "regulatory-variant-20261009-model-gpn"
M_NTV3 = "lit-genomics-20261011-guanine-model-nucleotide-transformer-v3"
M_AG = "catalog-model-alphagenome"
M_NT = "discovery-model-nucleotide-transformer"
M_DNABERT2 = "discovery-model-dnabert-2"
M_DNABERT = "lit-genomics-20261011-gfmbench-model-dnabert"
M_HYENA = "regulatory-variant-20261009-model-hyenadna"
D_NT18 = "lit-genomics-20261011-ntbench-data-all-18-tasks"
S_AG_SUPP = "source-alphagenome-nature2026-supplementary-methods"
S_AG_README = "evidence-official-578439da3f3a3a476b7f"

# Source IDs created here.
S_EVEE = P + "-source-evee-v4"
S_EVEE_FIG1C = P + "-source-evee-repo-fig1c-pdf"
S_EVEE_FIG1D = P + "-source-evee-repo-fig1d-pdf"
S_EVEE_COMMON = P + "-source-evee-repo-heatmap-common"
S_EVEE_FIG1D_PY = P + "-source-evee-repo-fig1d-script"
S_EVO2_META = P + "-source-evo2-biorxiv-metadata"
S_HEGDE = P + "-source-hegde2025"
S_NTV3 = P + "-source-ntv3-v1"
S_NT = P + "-source-nt-nature-methods"
S_HYENA = P + "-source-hyenadna-arxiv-v2"
S_HYENA_CARD = P + "-source-hyenadna-tiny-1k-card"
S_AG = P + "-source-alphagenome-article"

FILE_OF = {S_EVEE: "evee-v4.full.pdf", S_EVEE_FIG1C: "fig1c_deconf_heatmap.pdf", S_EVEE_FIG1D: "fig1d_indel_heatmap.pdf",
           S_EVEE_COMMON: "_heatmap_common.py", S_EVEE_FIG1D_PY: "fig1d_indel_heatmap.py", S_EVO2_META: "evo2-details.json",
           S_HEGDE: "PMC12652071.xml", S_NTV3: "ntv3-v1.full.pdf", S_NT: "PMC11810778.xml", S_HYENA: "hyena.pdf",
           S_HYENA_CARD: "hf-readme.md", S_AG: "PMC12851941.xml", S_AG_SUPP: "MOESM1.pdf", S_AG_README: "README-0db53bd.md"}


def sha256(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def flat(s):
    return " ".join(s.split())


def pdf_text(path, first, last, layout=False):
    args = ["pdftotext"] + (["-layout"] if layout else []) + ["-f", str(first), "-l", str(last), path, "-"]
    return subprocess.run(args, check=True, capture_output=True, text=True).stdout


def xml_root(path):
    t = open(path, encoding="utf-8").read()
    t = re.sub(r'xmlns(:\w+)?="[^"]*"', "", t)
    t = re.sub(r"<(/?)\w+:", r"<\1", t)
    t = re.sub(r'\s\w+:\w+="[^"]*"', "", t)
    t = re.sub(r"<!DOCTYPE[^>]*>", "", t)
    return ET.fromstring(t)


def xml_text(path):
    return flat("".join(xml_root(path).itertext()))


def xml_table(path, table_id):
    for tw in xml_root(path).iter("table-wrap"):
        if tw.get("id") == table_id:
            return [[flat("".join(c.itertext())) for c in tr if c.tag in ("td", "th")] for tr in tw.iter("tr")]
    raise AssertionError(f"table {table_id} not found in {path}")


def need(text, phrase):
    assert flat(phrase) in text, f"phrase not found: {phrase[:80]}"
    return phrase


def num(printed):
    t = re.sub(r"^(approximately|around)\s+", "", printed.strip())
    t = t.replace(",", "").replace("∼", "").replace("~", "").strip()
    return t if re.fullmatch(r"-?\d+(\.\d+)?", t) else None


class Batch:
    def __init__(self, art):
        self.art, self.records, self.ids, self.rows = art, [], set(), []

    def add(self, rec):
        assert rec["id"] not in self.ids, rec["id"]
        self.ids.add(rec["id"])
        mm = rec["attributes"].get("missing_metadata")
        if mm:
            rec["attributes"]["missing_metadata"] = dict(sorted(mm.items()))
        self.records.append(rec)
        return rec["id"]

    def entity(self, kind, id, name, description, attrs, source_ids, links=(), method_types=None):
        facets = {"areas": AREAS, "contexts": ["research"]}
        if method_types:
            facets["method_types"] = method_types
        return self.add({"id": id, "kind": kind, "name": name, "description": description, "status": "needs_review",
                         "facets": facets, "source_ids": list(source_ids), "links": list(links), "attributes": attrs})

    def review(self, source_id, methods, note):
        f = FILE_OF[source_id]
        sha, url, _ = ARTIFACTS[f]
        return {"method": methods, "method_note": note, "reviewer": ["claude"], "reviewer_note": EXTRACTOR_NOTE,
                "date": TODAY, "artifact_sha256": sha, "retrieval_url": url,
                "note": "Extracted, not reviewed. The review-evidence pass must re-check this value against the pinned artifact."}

    def claim(self, id, name, subject, field, value, locator, source_ids, methods, note, limitations=None):
        attrs = {"field": field, "value": value, "source_locator": locator,
                 "review": self.review(source_ids[0], methods, note)}
        if limitations:
            attrs["limitations"] = limitations
        self.rows.append([id, source_ids[0], locator, value[:200], "claim"])
        return self.add({"id": id, "kind": "claim", "name": name, "description": "Descriptive fact transcribed from the pinned source.",
                         "status": "needs_review", "facets": {}, "source_ids": list(source_ids),
                         "links": [{"relation": "subject", "target_id": subject}], "attributes": attrs})

    def result(self, id, name, evaluation, source_ids, printed, metric, direction, unit, locator, methods, note,
               qualifier=None, unit_detail=None, approximate=False, extra=None):
        attrs = {"metric": metric, "metric_direction": direction, "unit": unit, "printed_value": printed,
                 "numeric_value": num(printed), "source_locator": locator,
                 "missing_metadata": {"uncertainty": {"reason": "unreported"}},
                 "review": self.review(source_ids[0], methods, note)}
        assert attrs["numeric_value"] is not None, printed
        if qualifier:
            attrs["metric_qualifier"] = qualifier
        if unit_detail:
            attrs["unit_detail"] = unit_detail
        if approximate:
            attrs["approximate"] = True
        attrs.update(extra or {})
        self.rows.append([id, source_ids[0], locator, printed, "result"])
        return self.add({"id": id, "kind": "result", "name": name,
                         "description": "Reported value transcribed from the pinned source. Not independently reproduced.",
                         "status": "needs_review", "facets": {}, "source_ids": list(source_ids),
                         "links": [{"relation": "evaluation", "target_id": evaluation}], "attributes": attrs})

    def evaluation(self, id, name, system, protocol, data, source_ids, origin, comparison, locator, extra=None, missing=None):
        attrs = {"origin": origin, "protocol": protocol, "version": "Primary source as retrieved " + TODAY,
                 "comparison": dict(comparison, protocol_id=protocol), "source_locator": locator}
        mm = {f"comparison.{k}": {"reason": "unreported"} for k, v in comparison.items() if v is None}
        mm.update(missing or {})
        if mm:
            attrs["missing_metadata"] = mm
        attrs.update(extra or {})
        return self.entity("evaluation", id, name, "Published result; transcribed, not reproduced.", attrs, source_ids,
                           links=[{"relation": "system", "target_id": system}, {"relation": "assessment", "target_id": protocol},
                                  {"relation": "data", "target_id": data}])

    def source(self, id, name, description, attrs):
        f = FILE_OF[id]
        sha, url, retrieved = ARTIFACTS[f]
        a = {"artifact_url": url, "retrieved_at": retrieved, "artifact_sha256": sha}
        a.update(attrs)
        return self.add({"id": id, "kind": "source", "name": name, "description": description, "status": "needs_review",
                         "facets": {"areas": AREAS, "contexts": ["research"]}, "source_ids": [], "links": [], "attributes": a})


PDF_PARSE = ["pdf-text-parse", "deterministic-table-parse"]
XML_PARSE = ["deterministic-table-parse"]
PROSE = ["transcription"]


# ======================================================================== EVEE (Pearce et al. 2026)
EVEE_METHODS = ["Evo2 Covariance", "Evo2 Mean", "Evo2 Loss", "CADD v1.7", "AlphaMissense", "GPN-MSA", "NTv3", "AlphaGenome"]
# Overall rows read from the paper's raster Figure 1c and 1d (page 3, rendered at 300 dpi). The deterministic
# parse of the manuscript repository's vector PDFs must reproduce them exactly.
EVEE_DECONF_PAPER = ["0.977", "0.967", "0.929", "0.963", "0.972", "0.952", "0.710", "0.574"]
EVEE_INDEL_METHODS = ["Evo2 Covariance", "Evo2 Mean", "CADD v1.7", "NTv3"]
EVEE_INDEL_PAPER = ["0.991", "0.984", "0.980", "0.828"]


def overall_row(pdf_path, label, n_label, ncols):
    lines = pdf_text(pdf_path, 1, 1, layout=True).splitlines()
    for i, line in enumerate(lines):
        if line.split()[:1] == ["Overall"]:
            assert n_label in lines[i + 1], (n_label, lines[i + 1])
            vals = line.split()[1:]
            assert len(vals) == ncols, vals
            return vals
    raise AssertionError(f"{label}: Overall row not found")


def evee(b, d):
    pdf = os.path.join(d, "evee-v4.full.pdf")
    p8 = flat(pdf_text(pdf, 8, 8))
    p9 = flat(pdf_text(pdf, 9, 9))
    p3 = flat(pdf_text(pdf, 3, 3))
    p15 = flat(pdf_text(pdf, 15, 15))
    need(p8, "∼20,000 H100-hours")
    need(p8, "All benchmarks use ClinVar release 2026-03-21.")
    need(p8, "Nucleotide Transformer v3 (650M parameters) embeddings were extracted from layer 11 (1,536-D)")
    need(p9, "Deconfounded benchmark. 158,616 variants with pathogenic and benign labels balanced within each")
    need(p9, "Indel benchmark. 73,961 indels from 3,570 genes ≤100 kb with ≥1 star review status.")
    need(p3, "(c) AUROC on a deconfounded benchmark (158,616 variants)")
    need(p3, "(d) Zero-shot AUROC on 73,961 ClinVar indels")
    need(p15, "are employees of Goodfire")

    common = open(os.path.join(d, "_heatmap_common.py"), encoding="utf-8").read()
    for s in ['("Evo2 Covariance", "Evo2 Mean", "Evo2 Loss")', '("CADD v1.7",)', '("AlphaMissense", "EVE")',
              '("GPN-MSA", "NTv3", "AlphaGenome")', '"NTv3 cosine dist": "NTv3"', '"NTv3 subref probe"',
              '"Covpool probe": "Evo2 Covariance"', "am_ov_mask"]:
        assert s in common, s
    fig1d_py = open(os.path.join(d, "fig1d_indel_heatmap.py"), encoding="utf-8").read()
    for s in ['("evo2_cov_probe_zeroshot",       "Evo2 Covariance")', '("evo2_mean_probe_supervised",    "Evo2 Mean")',
              '("cadd_v17_indel",                "CADD v1.7")', '("ntv3_subref_probe_supervised",  "NTv3")']:
        assert s in fig1d_py, s
    deconf = overall_row(os.path.join(d, "fig1c_deconf_heatmap.pdf"), "fig1c", "(n=158,616, 27.8%P)", 8)
    indel = overall_row(os.path.join(d, "fig1d_indel_heatmap.pdf"), "fig1d", "(n=73,961, 65.1%P)", 4)
    assert deconf == EVEE_DECONF_PAPER, deconf
    assert indel == EVEE_INDEL_PAPER, indel

    evee_common = {"doi": "10.64898/2026.04.10.717844", "publication_status": "preprint", "licence": "CC-BY-4.0"}
    concerns = [
        {"source_id": S_EVEE,
         "message": "The column labelled 'NTv3' in Figure 1b and 1c is not the method the Methods describe. The manuscript repository's plotting code (scripts/figure1/_heatmap_common.py at e5e4a43) renames 'NTv3 cosine dist' to 'NTv3' and drops 'NTv3 subref probe', whereas Methods 'Baseline methods' describe NTv3 650M layer-11 embeddings with L2-regularised logistic regression under 5-fold gene-holdout cross-validation. Figure 1d's NTv3 column is the supervised subref probe. The SNV and deconfounded NTv3 values are recorded as a zero-shot embedding distance.",
         "source_locator": "Figure 1b and 1c, column 'NTv3' (page 3); Methods 'Baseline methods', NTv3 (page 8); repository scripts/figure1/_heatmap_common.py RENAME_MAP and DROP_METHODS",
         "artifact_sha256": ARTIFACTS["evee-v4.full.pdf"][0], "reviewed_at": EXTRACTED_AT, "review_method": "automated-source-review"},
        {"source_id": S_EVEE,
         "message": "AlphaMissense's 'Overall' cell in Figure 1b and 1c is its missense AUROC. The plotting code blanks AlphaMissense outside missense and copies the Missense value into the Overall row (scripts/figure1/_heatmap_common.py, am_ov_mask), so it is computed on a different, missense-only population from the other methods' Overall cells.",
         "source_locator": "Figure 1b and 1c, row 'Overall', column 'AlphaMissense' (page 3); repository scripts/figure1/_heatmap_common.py prepare()",
         "artifact_sha256": ARTIFACTS["evee-v4.full.pdf"][0], "reviewed_at": EXTRACTED_AT, "review_method": "automated-source-review"},
    ]
    b.source(S_EVEE, "Interpretable variant effect prediction from genomic foundation model representations (EVEE), bioRxiv v4",
             "Preprint PDF retrieved and hashed for the genomic foundation model guide sources pass (issue #138).",
             dict(evee_common, url="https://doi.org/10.64898/2026.04.10.717844", version="bioRxiv v4, posted 2026-07-11 (v1 posted 2026-04-11)",
                  media_type="application/pdf", evidence_concerns=concerns,
                  retrieval_note="Figure 1 heatmaps are raster images in the PDF; their printed cell values were read from a 300 dpi render of page 3 and matched against the manuscript repository's vector figure PDFs."))
    repo = {"publication_status": "official_project_source", "url": "https://github.com/goodfire-ai/evee-manuscript/tree/" + EVEE_COMMIT,
            "version": "goodfire-ai/evee-manuscript commit " + EVEE_COMMIT}
    b.source(S_EVEE_FIG1C, "EVEE manuscript repository: figures/figure1/fig1c_deconf_heatmap.pdf",
             "Vector PDF of Figure 1c from the authors' manuscript repository, pinned to a commit; its text layer prints every cell value.",
             dict(repo, media_type="application/pdf", missing_metadata={"licence": {"reason": "unreported", "note": "No licence file checked in this pass"}}))
    b.source(S_EVEE_FIG1D, "EVEE manuscript repository: figures/figure1/fig1d_indel_heatmap.pdf",
             "Vector PDF of Figure 1d from the authors' manuscript repository, pinned to a commit; its text layer prints every cell value.",
             dict(repo, media_type="application/pdf", missing_metadata={"licence": {"reason": "unreported", "note": "No licence file checked in this pass"}}))
    b.source(S_EVEE_COMMON, "EVEE manuscript repository: scripts/figure1/_heatmap_common.py",
             "Plotting code for Figure 1b and 1c: column order, method renaming, dropped methods and the AlphaMissense Overall cell.",
             dict(repo, media_type="text/x-python", missing_metadata={"licence": {"reason": "unreported", "note": "No licence file checked in this pass"}}))
    b.source(S_EVEE_FIG1D_PY, "EVEE manuscript repository: scripts/figure1/fig1d_indel_heatmap.py",
             "Plotting code for Figure 1d: the four method columns and which are zero-shot or supervised.",
             dict(repo, media_type="text/x-python", missing_metadata={"licence": {"reason": "unreported", "note": "No licence file checked in this pass"}}))
    b.source(S_EVO2_META, "bioRxiv API metadata for the Evo 2 preprint (10.1101/2025.02.18.638918)",
             "Author list of the Evo 2 preprint, used only to check author overlap with EVEE.",
             {"url": "https://doi.org/10.1101/2025.02.18.638918", "doi": "10.1101/2025.02.18.638918", "publication_status": "preprint",
              "version": "bioRxiv API details record, version 1 posted 2025-02-21", "media_type": "application/json",
              "missing_metadata": {"licence": {"reason": "inapplicable", "note": "Metadata record; only the author list is used"}}})

    # system records
    m_evee = b.entity("method", P + "-method-evee", "EVEE",
                      "Variant effect predictor from Goodfire and collaborators: a compressed covariance probe on the difference between Evo 2 7B embeddings of variant and reference sequences, plus annotation probes and an LLM explanation layer.",
                      {"entity_level": "method", "reported_name": "EVEE (Evo 2 covariance probe)",
                       "source_locator": "Abstract; Figure 1a; Methods 'Covariance probe' (page 8)",
                       "missing_metadata": {"version": {"reason": "unreported", "note": "No release version is named; the deployed probe is described in Methods"}}},
                      [S_EVEE], links=[{"relation": "uses_model", "target_id": M_EVO2}], method_types=["foundation_model", "supervised_machine_learning"])
    cfg = {}

    def config(key, target, name, desc, attrs, mtypes, sources=(S_EVEE,), extra_links=()):
        cfg[key] = b.entity("configuration", f"{P}-config-evee-{key}", name, desc,
                            dict({"source_locator": "Methods 'Baseline methods' and 'Covariance probe' (page 8); Figure 1 column labels"}, **attrs),
                            list(sources), links=[{"relation": "configuration_of", "target_id": target}, *extra_links], method_types=mtypes)

    config("evo2-covariance", m_evee, "EVEE covariance probe on Evo 2 7B layer 27 (Pearce et al. 2026)",
           "Covariance probe on alternate-minus-reference Evo 2 7B layer-27 embeddings, 65 kb window, top 256 most divergent positions per strand, trained on ClinVar SNVs with an 80/20 gene-level split.",
           {"reported_name": "Evo2 Covariance", "version": "Deployed probe as described in bioRxiv v4", "checkpoint": "Evo 2 7B, layer 27"},
           ["foundation_model", "supervised_machine_learning"], extra_links=[{"relation": "uses_model", "target_id": M_EVO2}])
    config("evo2-mean", M_EVO2, "Evo 2 7B mean-pooled embedding probe (Pearce et al. 2026)",
           "Supervised probe on mean-pooled alternate-minus-reference Evo 2 7B embeddings; the first-order comparator to the covariance probe.",
           {"reported_name": "Evo2 Mean", "checkpoint": "Evo 2 7B, layer 27",
            "missing_metadata": {"version": {"reason": "unreported"}}},
           ["foundation_model", "supervised_machine_learning"])
    config("evo2-loss", M_EVO2, "Evo 2 7B loss-based zero-shot score (Pearce et al. 2026)",
           "Zero-shot pathogenicity score from Evo 2 7B sequence likelihood (loss).",
           {"reported_name": "Evo2 Loss", "checkpoint": "Evo 2 7B",
            "missing_metadata": {"version": {"reason": "unreported"}}}, ["foundation_model"])
    config("cadd-v1-7", M_CADD, "CADD v1.7 PHRED, pre-computed (Pearce et al. 2026)",
           "CADD v1.7 PHRED-scaled scores from pre-computed whole-genome SNV files; for indels, CADD v1.7 InDel scores, indels under 50 bp only.",
           {"reported_name": "CADD v1.7", "version": "v1.7"}, ["supervised_machine_learning"])
    config("alphamissense", M_AM, "AlphaMissense hg38, pre-computed (Pearce et al. 2026)",
           "Pre-computed AlphaMissense hg38 genome-wide scores, missense variants on MANE Select canonical transcripts only.",
           {"reported_name": "AlphaMissense", "missing_metadata": {"version": {"reason": "unreported", "note": "Database file version not named"}}},
           ["foundation_model", "supervised_machine_learning"])
    config("gpn-msa", M_GPN, "GPN-MSA hg38 scores, pre-computed (Pearce et al. 2026)",
           "Pre-computed GPN-MSA scores downloaded from Hugging Face (songlab/gpn-msa-hg38-scores).",
           {"reported_name": "GPN-MSA", "checkpoint": "songlab/gpn-msa-hg38-scores",
            "missing_metadata": {"version": {"reason": "unreported", "note": "No dataset revision named"}}}, ["foundation_model"])
    config("ntv3-cosine", M_NTV3, "NTv3 cosine distance (Pearce et al. 2026 Figure 1b and 1c)",
           "Zero-shot cosine distance between NTv3 embeddings of variant and reference sequences; the method behind the 'NTv3' column of Figure 1b and 1c according to the manuscript repository's plotting code.",
           {"reported_name": "NTv3 (repository label 'NTv3 cosine dist')",
            "limitations": ["Methods describe only a supervised NTv3 650M layer-11 logistic-regression probe; the cosine-distance variant, its model size and layer are named only in the plotting code. See the source's evidence concern."],
            "missing_metadata": {"version": {"reason": "unreported", "note": "Model size and layer for the cosine-distance score are not stated"}}},
           ["foundation_model"], sources=(S_EVEE, S_EVEE_COMMON))
    config("ntv3-subref-probe", M_NTV3, "NTv3 650M layer-11 embedding probe (Pearce et al. 2026 Figure 1d)",
           "L2-regularised logistic regression on alternate-minus-reference NTv3 650M layer-11 embeddings (1,536-D) over 8,192 bp windows, 5-fold gene-holdout cross-validation.",
           {"reported_name": "NTv3 (repository label 'NTv3 subref probe')", "checkpoint": "NTv3 650M, layer 11"},
           ["foundation_model", "supervised_machine_learning"], sources=(S_EVEE, S_EVEE_FIG1D_PY))
    config("alphagenome", M_AG, "AlphaGenome all-folds composite score (Pearce et al. 2026)",
           "AlphaGenome (google/alphagenome-all-folds) variant scores over 9 modalities, CenterMask and GeneMask aggregation, maximum across modality scores.",
           {"reported_name": "AlphaGenome", "checkpoint": "google/alphagenome-all-folds"}, ["foundation_model"])

    # data and protocols
    clinvar = "ClinVar release 2026-03-21"
    d_deconf = b.entity("dataset", P + "-data-evee-clinvar-deconfounded", "EVEE deconfounded ClinVar SNV benchmark (158,616 variants)",
                        "ClinVar SNVs with pathogenic and benign labels balanced within each consequence type (framework of Lu et al.), sampled round-robin over genes.",
                        {"version": clinvar, "population": "158,616 SNVs, 27.8% pathogenic (Figure 1c row label)",
                         "split": "Gene-level holdout cross-validation for supervised probes (Methods); exact folds not published in the paper",
                         "source_locator": "Methods 'Clinical variant datasets', 'Deconfounded benchmark' (page 9); Figure 1c caption"}, [S_EVEE])
    d_indel = b.entity("dataset", P + "-data-evee-clinvar-indels", "EVEE ClinVar indel benchmark (73,961 indels)",
                       "ClinVar indels from 3,570 genes of at most 100 kb with at least one-star review status.",
                       {"version": clinvar, "population": "73,961 indels, 65.1% pathogenic (Figure 1d row label); 37,558 insertions and 36,403 deletions",
                        "split": "Covariance probe trained on SNVs only and applied zero-shot; the Evo2 Mean and NTv3 columns are supervised (repository column names)",
                        "source_locator": "Methods 'Indel benchmark' (page 9); Figure 1d caption"}, [S_EVEE, S_EVEE_FIG1D_PY])
    p_deconf = b.entity("protocol", P + "-protocol-evee-deconfounded-snv-auroc", "EVEE deconfounded ClinVar SNV pathogenicity AUROC (Pearce et al. 2026 Figure 1c)",
                        "AUROC for pathogenic versus benign on the deconfounded ClinVar SNV benchmark, all consequence types pooled (Overall row).",
                        {"protocol": "Each method's score on the 158,616 deconfounded ClinVar SNVs, AUROC for P/LP versus B/LB. Supervised probes use gene-holdout cross-validation; CADD, AlphaMissense, GPN-MSA and AlphaGenome use pre-computed or zero-shot scores.",
                         "version": "bioRxiv v4 Figure 1c", "metric": "auroc",
                         "limitations": ["Developer-reported: the authors built EVEE and three of them co-authored Evo 2.",
                                         "One value per method; no confidence interval is printed in Figure 1c.",
                                         "AlphaMissense's Overall cell is its missense-only AUROC (see the source concern).",
                                         "The NTv3 column is a zero-shot cosine distance, not the probe described in Methods (see the source concern)."],
                         "source_locator": "Figure 1c (page 3); Methods 'Deconfounded benchmark' (page 9)"},
                        [S_EVEE, S_EVEE_FIG1C, S_EVEE_COMMON], links=[{"relation": "uses_data", "target_id": d_deconf}])
    p_indel = b.entity("protocol", P + "-protocol-evee-clinvar-indel-auroc", "EVEE ClinVar indel pathogenicity AUROC (Pearce et al. 2026 Figure 1d)",
                       "AUROC for pathogenic versus benign on 73,961 ClinVar indels, all strata pooled (Overall row).",
                       {"protocol": "Each method's score on the 73,961 ClinVar indels, AUROC for P/LP versus B/LB. The covariance probe was trained on SNVs only; Evo2 Mean and NTv3 are supervised on indels; CADD v1.7 InDel scores indels under 50 bp.",
                        "version": "bioRxiv v4 Figure 1d", "metric": "auroc",
                        "limitations": ["Developer-reported: the authors built EVEE and three of them co-authored Evo 2.",
                                        "Mixes zero-shot and supervised methods in one comparison (repository column names).",
                                        "One value per method; no confidence interval is printed in Figure 1d."],
                        "source_locator": "Figure 1d (page 3); Methods 'Indel benchmark' (page 9); main text lines 141-143 (page 2)"},
                       [S_EVEE, S_EVEE_FIG1D, S_EVEE_FIG1D_PY], links=[{"relation": "uses_data", "target_id": d_indel}])

    deconf_locator = "Figure 1c (page 3, raster; matched to repository figures/figure1/fig1c_deconf_heatmap.pdf text layer), row 'Overall (n=158,616, 27.8%P)', column '{}'"
    indel_locator = "Figure 1d (page 3, raster; matched to repository figures/figure1/fig1d_indel_heatmap.pdf text layer), row 'Overall (n=73,961, 65.1%P)', column '{}'"
    keys = {"Evo2 Covariance": "evo2-covariance", "Evo2 Mean": "evo2-mean", "Evo2 Loss": "evo2-loss", "CADD v1.7": "cadd-v1-7",
            "AlphaMissense": "alphamissense", "GPN-MSA": "gpn-msa", "NTv3": "ntv3-cosine", "AlphaGenome": "alphagenome"}
    origin = {"evo2-covariance": "author_reported", "evo2-mean": "author_reported", "evo2-loss": "author_reported"}
    parse_note = ("Overall row parsed from the text layer of the pinned repository vector PDF (pdftotext -layout), n label asserted, column order "
                  "asserted from the pinned plotting code, and asserted equal to the values read from a 300 dpi render of the paper's Figure 1.")
    for label, printed in zip(EVEE_METHODS, deconf):
        k = keys[label]
        ev = b.evaluation(f"{P}-eval-evee-deconfounded-{k}", f"{label} on the EVEE deconfounded ClinVar SNV benchmark (Pearce et al. 2026)",
                          cfg[k], p_deconf, d_deconf, [S_EVEE, S_EVEE_FIG1C, S_EVEE_COMMON], origin.get(k, "independent_paper"),
                          {"dataset_version": clinvar, "split": "Deconfounded subset; gene-holdout cross-validation for supervised probes",
                           "population": "158,616 ClinVar SNVs, 27.8% pathogenic", "inputs": "Variant and reference sequence or pre-computed score",
                           "adaptation": None, "metric_implementation": None, "aggregation": "One AUROC over all consequence types", "budget": None},
                          deconf_locator.format(label))
        qual = "Deconfounded ClinVar SNVs, all consequence types (Overall row)"
        lims = None
        if k == "alphamissense":
            qual = "Deconfounded ClinVar SNVs, missense only (value plotted in the Overall row)"
            lims = ["The plotting code copies AlphaMissense's missense AUROC into the Overall row; not comparable with the other methods' Overall values."]
        if k == "ntv3-cosine":
            lims = ["Zero-shot cosine distance according to the plotting code; Methods describe a supervised probe instead."]
        b.result(f"{P}-result-evee-deconfounded-{k}", f"{label} AUROC, EVEE deconfounded ClinVar SNVs", ev,
                 [S_EVEE, S_EVEE_FIG1C, S_EVEE_COMMON], printed, "auroc", "higher", "unitless", deconf_locator.format(label),
                 ["pdf-text-parse", "rendered-source-visual-check"], parse_note, qualifier=qual,
                 extra={"limitations": lims} if lims else None)
    ikeys = {"Evo2 Covariance": "evo2-covariance", "Evo2 Mean": "evo2-mean", "CADD v1.7": "cadd-v1-7", "NTv3": "ntv3-subref-probe"}
    isetting = {"evo2-covariance": "zero-shot transfer from SNV training", "evo2-mean": "supervised on indels",
                "cadd-v1-7": "pre-computed CADD v1.7 InDel scores", "ntv3-subref-probe": "supervised on indels"}
    for label, printed in zip(EVEE_INDEL_METHODS, indel):
        k = ikeys[label]
        ev = b.evaluation(f"{P}-eval-evee-indel-{k}", f"{label} on the EVEE ClinVar indel benchmark (Pearce et al. 2026)",
                          cfg[k], p_indel, d_indel, [S_EVEE, S_EVEE_FIG1D, S_EVEE_FIG1D_PY], origin.get(k, "independent_paper"),
                          {"dataset_version": clinvar, "split": None, "population": "73,961 ClinVar indels, 65.1% pathogenic",
                           "inputs": "Variant and reference sequence or pre-computed score", "adaptation": isetting[k],
                           "metric_implementation": None, "aggregation": "One AUROC over all indels", "budget": None},
                          indel_locator.format(label))
        b.result(f"{P}-result-evee-indel-{k}", f"{label} AUROC, EVEE ClinVar indels", ev,
                 [S_EVEE, S_EVEE_FIG1D, S_EVEE_FIG1D_PY], printed, "auroc", "higher", "unitless", indel_locator.format(label),
                 ["pdf-text-parse", "rendered-source-visual-check"], parse_note,
                 qualifier=f"ClinVar indels, all strata (Overall row); {isetting[k]}")

    # embedding extraction compute
    d_full = b.entity("dataset", P + "-data-evee-full-clinvar", "EVEE full ClinVar variant set (4,252,870 variants)",
                      "All ClinVar variants after removing multi-allelic, MNV and unannotated entries and GENCODE v49 validation.",
                      {"version": clinvar, "population": "4,252,870 variants: 1,539,596 labelled and 2,716,001 unlabelled (as printed)",
                       "split": "Not applicable: embedding extraction covers every variant",
                       "source_locator": "Methods 'Full dataset' (page 8)"}, [S_EVEE])
    p_comp = b.entity("protocol", P + "-protocol-evee-embedding-extraction-compute", "EVEE Evo 2 embedding extraction compute (Pearce et al. 2026)",
                      "Accelerator time to extract Evo 2 7B layer-27 embeddings for every variant in the full ClinVar set.",
                      {"protocol": "One-off extraction of per-position Evo 2 7B embeddings (reference and variant, both strands, 256 retained positions, 4,096 dimensions) for 4,252,870 variants, stored as bf16 (about 34 TB).",
                       "version": "bioRxiv v4 Methods", "metric": "accelerator-time",
                       "limitations": ["Approximate figure stated once in Methods; GPU count, batch size and wall-clock time are not given."],
                       "source_locator": "Methods 'Harvesting' (page 8)"}, [S_EVEE], links=[{"relation": "uses_data", "target_id": d_full}])
    ev = b.evaluation(f"{P}-eval-evee-embedding-extraction-compute", "EVEE Evo 2 7B embedding extraction compute (Pearce et al. 2026)",
                      cfg["evo2-covariance"], p_comp, d_full, [S_EVEE], "author_reported",
                      {"dataset_version": clinvar, "split": "All variants", "population": "4,252,870 ClinVar variants",
                       "inputs": "65 kb windows around each variant, reference and variant sequences", "adaptation": "Inference only",
                       "metric_implementation": None, "aggregation": "Total over the extraction", "budget": None},
                      "Methods 'Harvesting' (page 8)", extra={"inference_hardware": "NVIDIA H100 (count not stated)"})
    b.result(f"{P}-result-evee-embedding-extraction-h100-hours", "EVEE embedding extraction, H100-hours", ev, [S_EVEE],
             "∼20,000", "accelerator-time", "lower", "hour", "Methods 'Harvesting', page 8, line 461: 'Extraction used ∼20,000 H100-hours'",
             PROSE, "Exact phrase asserted in the text layer of the pinned PDF (page 8).",
             qualifier="Evo 2 7B embedding extraction for 4,252,870 ClinVar variants", unit_detail="H100 GPU-hours", approximate=True)

    # developer overlap
    meta = json.load(open(os.path.join(d, "evo2-details.json")))["collection"]
    evo2_authors = meta[-1]["authors"]
    overlap = [n for n in ("Nguyen, N.", "Balsam, D.", "Wang, N. K.") if n in evo2_authors]
    assert len(overlap) == 3, overlap
    b.claim(P + "-claim-evee-developer-overlap", "Developer overlap: EVEE authors and Evo 2", m_evee, "developer_overlap",
            "EVEE is reported by its developers, mostly Goodfire employees (Competing interests). Three EVEE authors, N. Nguyen, D. Balsam and N. K. Wang, also appear by name and initials in the author list of the Evo 2 preprint (bioRxiv 10.1101/2025.02.18.638918), so the Evo 2 based configurations are treated as author_reported. The match is by name only; affiliations were not compared.",
            "EVEE v4 title page author list and 'Competing interests' (page 15); bioRxiv API details for 10.1101/2025.02.18.638918, field 'authors'",
            [S_EVEE, S_EVO2_META], PROSE, "Author lists compared by exact name-and-initials string match in the pinned bioRxiv metadata JSON; competing-interests sentence asserted in the PDF text layer.")


# ======================================================================== Hegde, Nebel and Rahman 2025
def hegde(b, d):
    xml = os.path.join(d, "PMC12652071.xml")
    text = xml_text(xml)
    need(text, "The training was performed on 2 × Quadro RTX 8000 GPUs, taking around 1 h per pruned model on average.")
    need(text, "training to convergence on 2 × NVIDIA TITAN Xp GPUs took approximately 19 h.")
    need(text, "“InstaDeepAI/ nucleotide-transformer-500m-human-ref”")
    need(text, "“zhihan1996/DNABERT-2-117M”")
    t = xml_table(xml, "genes-16-01358-t0A1")
    assert t[0] == ["Seed", "Training Time (Hours)", "Evaluation Time (Minutes)", "Accuracy (%)", "AUROC (%)", "F1 (%)"], t[0]
    rows = {r[0]: r for r in t[1:]}
    assert sorted(rows) == ["41", "42", "43"], rows

    b.source(S_HEGDE, "Reaping the Fruits of LLM Pruning: Towards Small Language Models for Efficient Non-Coding Variant Effect Prediction",
             "Primary article (Europe PMC full-text XML) retrieved and hashed for the genomic foundation model guide sources pass (issue #138).",
             {"url": "https://doi.org/10.3390/genes16111358", "doi": "10.3390/genes16111358", "publication_status": "peer_reviewed",
              "licence": "CC-BY-4.0", "version": "Genes 16(11):1358, 2025; PMC12652071 full-text XML", "media_type": "application/xml",
              "retrieval_note": "The publisher PDF request returned a 408-byte error page; the Europe PMC XML was used."})
    d_eqtl = b.entity("dataset", P + "-data-hegde-enformer-eqtl", "Enformer eQTL causal-variant dataset, Genomics Long-Range Benchmark version (Hegde et al. 2025)",
                      "Variant-centred sequences from the Enformer eQTL causal-variant dataset as distributed in InstaDeepAI/genomics-long-range-benchmark.",
                      {"accession": "https://huggingface.co/datasets/InstaDeepAI/genomics-long-range-benchmark (accessed 29 September 2025)",
                       "population": "Train split 44,655 benign and 44,405 pathogenic; test split 4,306 benign and 4,556 pathogenic (Table 1)",
                       "split": "Benchmark train and test splits",
                       "source_locator": "Table 1; Methods paragraph 2; Data Availability Statement",
                       "missing_metadata": {"version": {"reason": "unreported", "note": "No dataset revision; Methods give 88,717 training and 8,846 evaluation sequences, which differ from the Table 1 totals (89,060 and 8,862)"}}},
                      [S_HEGDE])
    c_nt = b.entity("configuration", P + "-config-hegde-nt-500m-human-ref-5-epochs", "NT 500M human reference, fine-tuned 5 epochs, unpruned (Hegde et al. 2025)",
                    "InstaDeepAI/nucleotide-transformer-500m-human-ref fine-tuned for binary eQTL variant classification for 5 epochs with all 24 layers.",
                    {"reported_name": "Nucleotide Transformer (original, non-pruned)", "checkpoint": "InstaDeepAI/nucleotide-transformer-500m-human-ref",
                     "hardware": {"description": "2 × NVIDIA TITAN Xp GPUs (Methods, for the Nucleotide Transformer); Table A1 itself names no hardware"},
                     "fine_tuning": {"description": "Full fine-tuning with Hugging Face Trainer for 5 epochs (Appendix A.3 TrainingArguments)"},
                     "source_locator": "Appendix A.1; Appendix A.3; Methods paragraph 3",
                     "missing_metadata": {"version": {"reason": "unreported", "note": "Hugging Face repository named without a revision"}}},
                    [S_HEGDE], links=[{"relation": "configuration_of", "target_id": M_NT}], method_types=["foundation_model"])
    c_nt_conv = b.entity("configuration", P + "-config-hegde-nt-500m-human-ref-convergence", "NT 500M human reference, fine-tuned to convergence (Hegde et al. 2025)",
                         "InstaDeepAI/nucleotide-transformer-500m-human-ref fine-tuned to convergence of the validation loss on 2 × NVIDIA TITAN Xp.",
                         {"reported_name": "Nucleotide Transformer", "checkpoint": "InstaDeepAI/nucleotide-transformer-500m-human-ref",
                          "hardware": {"description": "2 × NVIDIA TITAN Xp GPUs"}, "source_locator": "Methods paragraph 3; Appendix A.1",
                          "missing_metadata": {"version": {"reason": "unreported", "note": "Hugging Face repository named without a revision"}}},
                         [S_HEGDE], links=[{"relation": "configuration_of", "target_id": M_NT}], method_types=["foundation_model"])
    c_db2 = b.entity("configuration", P + "-config-hegde-dnabert-2-pruned-convergence", "DNABERT-2 117M, one layer pruned, fine-tuned to convergence (Hegde et al. 2025)",
                     "zhihan1996/DNABERT-2-117M with one encoder layer removed, fine-tuned to convergence of the validation loss on 2 × Quadro RTX 8000.",
                     {"reported_name": "DNABERT-2 (pruned model)", "checkpoint": "zhihan1996/DNABERT-2-117M",
                      "hardware": {"description": "2 × Quadro RTX 8000 GPUs"}, "source_locator": "Methods paragraph 3; Appendix A.1",
                      "missing_metadata": {"version": {"reason": "unreported", "note": "Hugging Face repository named without a revision"}}},
                     [S_HEGDE], links=[{"relation": "configuration_of", "target_id": M_DNABERT2}], method_types=["foundation_model"])
    p_5ep = b.entity("protocol", P + "-protocol-hegde-eqtl-finetune-5-epochs-time", "Fine-tuning and evaluation wall time, 5 epochs on the Enformer eQTL dataset (Hegde et al. 2025 Table A1)",
                     "Wall time to fine-tune for 5 epochs on the eQTL training split and to evaluate on its test split, one row per random seed.",
                     {"protocol": "Fine-tune for 5 epochs on the training split (Hugging Face Trainer), then evaluate binary non-coding variant classification on the evaluation split; record training time in hours and evaluation time in minutes per seed.",
                      "version": "Genes 2025 Appendix A.3, Table A1", "metric": "runtime",
                      "limitations": ["Hardware is stated in Methods, not in the table.", "Three seeds on one machine; no spread is printed."],
                      "source_locator": "Table A1; Methods paragraph 3"}, [S_HEGDE], links=[{"relation": "uses_data", "target_id": d_eqtl}])
    p_conv = b.entity("protocol", P + "-protocol-hegde-eqtl-finetune-convergence-time", "Fine-tuning wall time to convergence on the Enformer eQTL dataset (Hegde et al. 2025 Methods)",
                      "Approximate wall time to fine-tune until the validation loss converges.",
                      {"protocol": "Fine-tune until convergence of the validation loss on the eQTL training split; approximate wall time as stated in the Methods.",
                       "version": "Genes 2025 Methods", "metric": "runtime",
                       "limitations": ["Approximate prose values, not measured per run in a table.", "Different GPUs for the two models."],
                       "source_locator": "Methods paragraph 3"}, [S_HEGDE], links=[{"relation": "uses_data", "target_id": d_eqtl}])
    comp = {"dataset_version": None, "split": "Benchmark train split for fine-tuning; evaluation split for evaluation",
            "population": "Enformer eQTL causal-variant sequences", "inputs": "Variant-centred DNA sequences",
            "adaptation": "Full fine-tuning", "metric_implementation": None, "aggregation": "One value per seed", "budget": "5 epochs"}
    ev = b.evaluation(P + "-eval-hegde-nt-500m-human-ref-5-epochs", "NT 500M human reference, 5-epoch fine-tuning time (Hegde et al. 2025 Table A1)",
                      c_nt, p_5ep, d_eqtl, [S_HEGDE], "independent_paper", comp, "Table A1",
                      extra={"training_hardware": "2 × NVIDIA TITAN Xp (Methods)", "n_runs": 3})
    note = "Deterministic parse of the pinned Europe PMC XML table genes-16-01358-t0A1; header and seed labels asserted."
    for seed in ("41", "42", "43"):
        r = rows[seed]
        b.result(f"{P}-result-hegde-nt-5-epochs-training-time-seed-{seed}", f"NT 500M human ref 5-epoch training time, seed {seed}", ev, [S_HEGDE],
                 r[1], "runtime", "lower", "hour", f"Table A1, row seed {seed}, column 'Training Time (Hours)'", XML_PARSE, note,
                 qualifier="Fine-tuning, 5 epochs, unpruned model", extra={"seed": seed, "hardware": "2 × NVIDIA TITAN Xp (Methods)"})
        b.result(f"{P}-result-hegde-nt-5-epochs-evaluation-time-seed-{seed}", f"NT 500M human ref evaluation time, seed {seed}", ev, [S_HEGDE],
                 r[2], "runtime", "lower", "minute", f"Table A1, row seed {seed}, column 'Evaluation Time (Minutes)'", XML_PARSE, note,
                 qualifier="Evaluation on the eQTL test split after 5-epoch fine-tuning", extra={"seed": seed, "hardware": "2 × NVIDIA TITAN Xp (Methods)"})
    comp_c = dict(comp, aggregation="Approximate wall time as stated", budget="Until validation-loss convergence")
    ev = b.evaluation(P + "-eval-hegde-nt-500m-human-ref-convergence", "NT 500M human reference, fine-tuning time to convergence (Hegde et al. 2025)",
                      c_nt_conv, p_conv, d_eqtl, [S_HEGDE], "independent_paper", comp_c, "Methods paragraph 3",
                      extra={"training_hardware": "2 × NVIDIA TITAN Xp"})
    b.result(f"{P}-result-hegde-nt-convergence-time", "NT 500M human ref fine-tuning to convergence, wall time", ev, [S_HEGDE], "approximately 19",
             "runtime", "lower", "hour", "Methods paragraph 3: 'training to convergence on 2 × NVIDIA TITAN Xp GPUs took approximately 19 h'",
             PROSE, "Exact sentence asserted in the pinned XML text.", qualifier="Fine-tuning to convergence, unpruned model",
             unit_detail="Printed as 'approximately 19 h'", approximate=True, extra={"hardware": "2 × NVIDIA TITAN Xp"})
    ev = b.evaluation(P + "-eval-hegde-dnabert-2-pruned-convergence", "DNABERT-2 pruned models, fine-tuning time to convergence (Hegde et al. 2025)",
                      c_db2, p_conv, d_eqtl, [S_HEGDE], "independent_paper", dict(comp_c, aggregation="Average over pruned models, approximate"),
                      "Methods paragraph 3", extra={"training_hardware": "2 × Quadro RTX 8000"})
    b.result(f"{P}-result-hegde-dnabert-2-pruned-convergence-time", "DNABERT-2 pruned model fine-tuning to convergence, wall time", ev, [S_HEGDE], "around 1",
             "runtime", "lower", "hour", "Methods paragraph 3: 'taking around 1 h per pruned model on average'",
             PROSE, "Exact sentence asserted in the pinned XML text.", qualifier="Fine-tuning to convergence, average per pruned model",
             unit_detail="Printed as 'around 1 h'", approximate=True, extra={"hardware": "2 × Quadro RTX 8000"})


# ======================================================================== NTv3 (Boshar et al. 2025)
NTV3_COLS = ["Pre-training 8 kb", "Length ext. 1-4", "Length ext. 5-7", "Post-training 1", "Post-training 2"]
NTV3_TOKENS = ["10.5T tokens", "200B tokens", "150B tokens", "1.2T tokens", "54B tokens"]


def ntv3(b, d):
    pdf = os.path.join(d, "ntv3-v1.full.pdf")
    page = pdf_text(pdf, 34, 34, layout=True)
    lines = page.splitlines()
    hdr = next(i for i, l in enumerate(lines) if "Pre-training 8 kb" in l)
    assert re.split(r"\s{2,}", lines[hdr].strip()) == NTV3_COLS, lines[hdr]
    assert re.split(r"\s{2,}", lines[hdr + 2].strip()) == NTV3_TOKENS, lines[hdr + 2]
    table = {}
    for l in lines[hdr + 3: hdr + 6]:
        parts = l.split()
        table[parts[0]] = parts[1:]
    assert sorted(table) == ["100M", "650M", "8M"] and all(len(v) == 5 for v in table.values()), table
    assert table["8M"][3:] == ["NA", "NA"], table["8M"]
    flatp = flat(page)
    need(flatp, "Table 5 | H100 GPU-hours required for all training stages of each model size.")
    need(flatp, "By leveraging a 4-node (32 GPU) setup, the end-to-end wall-clock time was reduced to just under nine days (Table 5).")
    need(flatp, "For the largest NTv3 650M (pre) model, processing the full 10.5 trillion tokens required over nine months of H100 GPU-hours.")
    p4_6 = flat(pdf_text(pdf, 4, 6))
    need(p4_6, "even the largest NTv3 model is designed to run")
    need(p4_6, "inference for full megabase windows on a single A100/H100 GPU.")
    need(p4_6, "NTv3 8M can run inference for sequences of several tens of kilobases on a laptop CPU within seconds")

    b.source(S_NTV3, "A foundational model for joint sequence-function multi-species modeling at scale for long-range genomic prediction (NTv3), bioRxiv v1",
             "Preprint PDF retrieved and hashed for the genomic foundation model guide sources pass (issue #138).",
             {"url": "https://doi.org/10.64898/2025.12.22.695963", "doi": "10.64898/2025.12.22.695963", "publication_status": "preprint",
              "licence": "CC-BY-NC-ND-4.0", "version": "bioRxiv v1, posted 2025-12-25 (dated 2025-12-22 on the title page)", "media_type": "application/pdf",
              "retrieval_note": "First request returned HTTP 429; the retry two minutes later returned the PDF (107 pages)."})
    d_corpus = b.entity("dataset", P + "-data-ntv3-training-corpus", "NTv3 training data, all stages (Boshar et al. 2025)",
                        "Multi-species genomes for pre-training (8 kb sequences, 10.5T tokens), length extension and functional-track post-training.",
                        {"population": "Tokens per stage: pre-training 10.5T, length extension 1-4 200B, length extension 5-7 150B, post-training 1 1.2T, post-training 2 54B (Table 5 header)",
                         "split": "Not applicable: training compute", "source_locator": "Table 5 column headers (page 34)",
                         "missing_metadata": {"version": {"reason": "unextracted", "note": "Corpus composition is described elsewhere in the preprint and not extracted here"}}},
                        [S_NTV3])
    p = b.entity("protocol", P + "-protocol-ntv3-training-gpu-hours", "NTv3 H100 GPU-hours per training stage (Boshar et al. 2025 Table 5)",
                 "H100 GPU-hours used by each training stage of each NTv3 model size.",
                 {"protocol": "Accelerator time per training stage on the authors' infrastructure (8 × H100 80GB nodes, NVLink, RoCE), as printed in Table 5.",
                  "version": "bioRxiv v1 Table 5", "metric": "accelerator-time",
                  "limitations": ["Developer-reported.", "The text says models were trained on either Cloud TPU v6 or on-premise H100s; Table 5 gives H100 GPU-hours for every stage without saying whether TPU runs were converted.",
                                  "Post-training stages are not applicable to the 8M model (printed NA)."],
                  "source_locator": "Table 5 and section 4.4.4 'Training Infrastructure' (page 34)"}, [S_NTV3],
                 links=[{"relation": "uses_data", "target_id": d_corpus}])
    note = "Deterministic parse of pdftotext -layout output of page 34; column headers, token row and model labels asserted."
    for size in ("8M", "100M", "650M"):
        c = b.entity("configuration", f"{P}-config-ntv3-{size.lower()}-training", f"NTv3 {size} training run (Boshar et al. 2025)",
                     f"Training of NTv3 {size} through all stages reported in Table 5.",
                     {"reported_name": f"NTv3 {size}", "hardware": {"description": "Machines with 8 NVIDIA H100 80GB GPUs connected via NVLink, nodes connected with RoCE; some runs on Cloud TPU v6 (section 4.4.4)"},
                      "source_locator": "Table 5; section 4.4.4", "missing_metadata": {"version": {"reason": "unreported", "note": "No checkpoint revision named in the table"}}},
                     [S_NTV3], links=[{"relation": "configuration_of", "target_id": M_NTV3}], method_types=["foundation_model"])
        ev = b.evaluation(f"{P}-eval-ntv3-{size.lower()}-training-gpu-hours", f"NTv3 {size} training GPU-hours (Boshar et al. 2025 Table 5)",
                          c, p, d_corpus, [S_NTV3], "author_reported",
                          {"dataset_version": None, "split": "Not applicable", "population": "Training tokens as in the Table 5 header",
                           "inputs": "Genomic sequence", "adaptation": "Training from scratch through each stage", "metric_implementation": None,
                           "aggregation": "Total per stage", "budget": None},
                          "Table 5 (page 34)", extra={"training_hardware": "NVIDIA H100 80GB (8 per node)"})
        if size == "650M":
            wall = b.claim(f"{P}-claim-ntv3-650m-pretraining-wall-clock", "NTv3 650M pre-training wall-clock time", c, "training_compute",
                           "Pre-training NTv3 650M on the full 10.5 trillion tokens took over nine months of H100 GPU-hours; on 4 nodes (32 GPUs) the wall-clock time was just under nine days. Throughput was about 3.5M tokens/s for 650M, 7.8M for 100M and 14.5M for 8M.",
                           "Section 4.4.4 'Pre-training Compute' (page 34)", [S_NTV3], PROSE, "Exact sentences asserted in the pinned PDF text (page 34).")
        for col, printed, tokens in zip(NTV3_COLS, table[size], NTV3_TOKENS):
            if printed == "NA":
                continue
            slug = re.sub(r"[^a-z0-9]+", "-", col.lower()).strip("-")
            b.result(f"{P}-result-ntv3-{size.lower()}-{slug}-gpu-hours", f"NTv3 {size} {col} H100 GPU-hours", ev, [S_NTV3], printed,
                     "accelerator-time", "lower", "hour", f"Table 5 (page 34), row '{size}', column '{col}'", PDF_PARSE, note,
                     qualifier=f"Training stage '{col}' ({tokens})", unit_detail="H100 GPU-hours")
    b.claim(P + "-claim-ntv3-inference-hardware", "NTv3 inference hardware", M_NTV3, "hardware_requirement",
            "The authors state that even the largest NTv3 model is designed to run inference for full megabase windows on a single A100 or H100 GPU, and that NTv3 8M can run inference for sequences of several tens of kilobases on a laptop CPU within seconds in mixed precision.",
            "Results paragraph spanning pages 4 and 6 (page 5 is a figure)", [S_NTV3], PROSE,
            "Exact phrases asserted in the pinned PDF text (pages 4 to 6).", limitations=["Authors' design statement; no per-sequence time or memory is printed with it. Figure 2H plots single-GPU inference time without printed values."])


# ======================================================================== Nucleotide Transformer (Dalla-Torre et al. 2025)
def nt(b, d):
    xml = os.path.join(d, "PMC11810778.xml")
    text = xml_text(xml)
    s_hw = need(text, "On average, a fine-tuning run lasted 20 min for the 500M-parameter models and 50 min for the 2.5B-parameter models.")
    need(text, "All fine-tuning runs were performed on a single node with eight A100 GPUs.")
    s_disc = need(text, "allowing even our largest models to be fine-tuned in under 15 min on a single GPU.")
    s_train = need(text, "The 500M-parameter models were trained on a single node for a day, whereas the 2.5B-parameter models required the whole cluster for 28 days to be trained.")
    need(text, "All models were trained on the Cambridge-1 Nvidia supercomputer system, using 16 nodes, each equipped with eight A100 GPUs, leading to a total of 128 A100 GPUs used.")
    need(text, "The NT-v2 models with varying number of parameters ranging from 50 million to 500 million were similarly trained on a single node for a single day.")
    need(text, "were computed and stored on a single node with eight A100 GPUs, requiring 2 days to compute. Then, 760,000 downstream models were fit on a cluster of 3,000 CPUs, requiring 2.5 days.")

    concern = {"source_id": S_NT,
               "message": "Fine-tuning time conflicts within the article. Methods 'Hardware' say all fine-tuning runs used one node of eight A100 GPUs and averaged 20 min (500M-parameter models) and 50 min (2.5B-parameter models); the Discussion says the IA3 technique allows even the largest models to be fine-tuned in under 15 min on a single GPU. Both are recorded; neither is preferred.",
               "source_locator": "Methods, 'Data preparation > Hardware', paragraph 1; Discussion, paragraph 2",
               "artifact_sha256": ARTIFACTS["PMC11810778.xml"][0], "reviewed_at": EXTRACTED_AT, "review_method": "automated-source-review"}
    b.source(S_NT, "Nucleotide Transformer: building and evaluating robust foundation models for human genomics (Nature Methods)",
             "Primary article (Europe PMC full-text XML) retrieved and hashed for the genomic foundation model guide sources pass (issue #138).",
             {"url": "https://doi.org/10.1038/s41592-024-02523-z", "doi": "10.1038/s41592-024-02523-z", "publication_status": "peer_reviewed",
              "licence": "CC-BY-NC-ND-4.0", "version": "Nature Methods 22, 287-297 (published online 2024-11-28); PMC11810778 full-text XML",
              "media_type": "application/xml", "evidence_concerns": [concern]})
    p = b.entity("protocol", P + "-protocol-nt-ia3-finetune-runtime", "Nucleotide Transformer IA3 fine-tuning run time (Dalla-Torre et al. 2025 Methods 'Hardware')",
                 "Average wall time of one parameter-efficient (IA3) fine-tuning run on the downstream tasks.",
                 {"protocol": "IA3 fine-tuning on one node of eight A100 GPUs, weights replicated, batch size eight (one sample per GPU); average duration of a fine-tuning run.",
                  "version": "Nature Methods 2025 Methods", "metric": "runtime",
                  "limitations": ["Developer-reported average; the number of runs and the tasks averaged over are not stated.",
                                  "The Discussion's 'under 15 min on a single GPU' conflicts with these values (see the source concern)."],
                  "source_locator": "Methods, 'Data preparation > Hardware', paragraph 1"}, [S_NT], links=[{"relation": "uses_data", "target_id": D_NT18}])
    for size, printed, label in (("500m", "20", "500M-parameter models"), ("2-5b", "50", "2.5B-parameter models")):
        c = b.entity("configuration", f"{P}-config-nt-{size}-ia3-fine-tuning", f"Nucleotide Transformer {label}, IA3 fine-tuning (Dalla-Torre et al. 2025)",
                     f"IA3 parameter-efficient fine-tuning of the Nucleotide Transformer {label} on one node of eight A100 GPUs.",
                     {"reported_name": f"NT {label}", "hardware": {"description": "One node with eight NVIDIA A100 GPUs"},
                      "fine_tuning": {"description": "IA3 parameter-efficient fine-tuning, about 0.1% of parameters trainable, batch size eight"},
                      "source_locator": "Methods 'Hardware'; Results paragraph on fine-tuning",
                      "missing_metadata": {"version": {"reason": "unreported", "note": f"The article groups all {label} (several pretraining datasets) together"}}},
                     [S_NT], links=[{"relation": "configuration_of", "target_id": M_NT}], method_types=["foundation_model"])
        ev = b.evaluation(f"{P}-eval-nt-{size}-ia3-fine-tuning-runtime", f"NT {label} IA3 fine-tuning run time (Dalla-Torre et al. 2025)",
                          c, p, D_NT18, [S_NT], "author_reported",
                          {"dataset_version": None, "split": None, "population": "Downstream fine-tuning tasks (not enumerated for this average)",
                           "inputs": "DNA sequence", "adaptation": "IA3 fine-tuning", "metric_implementation": None,
                           "aggregation": "Average over fine-tuning runs", "budget": None},
                          "Methods, 'Data preparation > Hardware', paragraph 1", extra={"training_hardware": "One node of eight NVIDIA A100 GPUs"})
        b.result(f"{P}-result-nt-{size}-ia3-fine-tuning-runtime", f"NT {label} average IA3 fine-tuning run time", ev, [S_NT], printed,
                 "runtime", "lower", "minute", "Methods, 'Data preparation > Hardware', paragraph 1: '" + s_hw + "'",
                 PROSE, "Exact sentence asserted in the pinned XML text.", qualifier="Mean wall time per IA3 fine-tuning run",
                 unit_detail=f"Printed as '{printed} min'", extra={"hardware": "One node of eight NVIDIA A100 GPUs"})
    b.claim(P + "-claim-nt-fine-tuning-single-gpu", "Nucleotide Transformer fine-tuning time on a single GPU (Discussion)", M_NT, "fine_tuning_time",
            "The Discussion states that IA3 fine-tuning, which trains about 0.1% of parameters, allows even the largest models to be fine-tuned in under 15 min on a single GPU. This conflicts with Methods 'Hardware' (one node of eight A100 GPUs, 20 min average for 500M and 50 min for 2.5B models).",
            "Discussion, paragraph 2: '" + s_disc + "'", [S_NT], PROSE, "Exact sentence asserted in the pinned XML text.",
            limitations=["Conflicts with the Methods; see the source concern."])
    b.claim(P + "-claim-nt-training-compute", "Nucleotide Transformer pre-training and probing compute", M_NT, "training_compute",
            "All models were trained on Cambridge-1 (16 nodes of eight A100 GPUs, 128 GPUs). The 500M-parameter models trained on one node for a day; the 2.5B-parameter models used the whole cluster for 28 days; NT-v2 models (50M to 500M) trained on one node for a day. Probing embeddings took 2 days on one 8-A100 node, and fitting 760,000 downstream models took 2.5 days on 3,000 CPUs.",
            "Methods, 'Data preparation > Hardware', paragraphs 1 and 2: '" + s_train + "'", [S_NT], PROSE,
            "Exact sentences asserted in the pinned XML text.")


# ======================================================================== HyenaDNA (Nguyen et al. 2023)
HYENA_COLS = ["DNABERT", "Nucleotide Transformer", "HyenaDNA", "HyenaDNA"]


def hyena(b, d):
    pdf = os.path.join(d, "hyena.pdf")
    page = pdf_text(pdf, 17, 17, layout=True)
    lines = page.splitlines()
    i = next(k for k, l in enumerate(lines) if "Table A.2: Pretraining GPU & runtime comparison for short-range models." in l)
    assert flat(lines[i + 1]) == " ".join(HYENA_COLS), lines[i + 1]
    rows = {}
    for l in lines[i + 2: i + 6]:
        parts = re.split(r"\s{2,}", l.strip())
        rows[parts[0]] = parts[1:]
    assert rows["Params"] == ["110M", "2.5B", "436K", "1.6M"], rows
    assert rows["GPUs"] == ["8-2080 TI", "128-A100-80GB", "1-A100-40GB", "1-A100-40GB"], rows
    assert rows["Wall clock"] == ["25 days", "28 days", "80 mins", "80 mins"], rows
    assert rows["GPU-hrs"] == ["12,000", "215,000", "1.3", "1.3"], rows
    card = open(os.path.join(d, "hf-readme.md"), encoding="utf-8").read()
    for s in ["- [tiny-1k](https://huggingface.co/LongSafari/hyenadna-tiny-1k-seqlen/tree/main): (T4, T4, T4)",
              "- [small-32k](https://huggingface.co/LongSafari/hyenadna-small-32k-seqlen/tree/main): (A100-40, T4, T4)",
              "- [medium-160k](https://huggingface.co/LongSafari/hyenadna-medium-160k-seqlen/tree/main): (A100-40, A100-40, T4)",
              "- [medium-450k](https://huggingface.co/LongSafari/hyenadna-medium-450k-seqlen/tree/main): (A100-40, A100-40, T4)",
              "- [large-1m](https://huggingface.co/LongSafari/hyenadna-large-1m-seqlen/tree/main): (A100-80, A100-80, A100-40)",
              "### GPU requirements (suggested)", "GPU during: Pretrain, fine-tune, inference"]:
        assert s in card, s

    b.source(S_HYENA, "HyenaDNA: Long-Range Genomic Sequence Modeling at Single Nucleotide Resolution, arXiv v2",
             "Preprint PDF (arXiv v2, 25 pages) retrieved and hashed for the genomic foundation model guide sources pass (issue #138).",
             {"url": "https://arxiv.org/abs/2306.15794v2", "doi": "10.48550/arXiv.2306.15794", "publication_status": "preprint",
              "licence": "arXiv non-exclusive distribution licence 1.0", "version": "arXiv 2306.15794v2", "media_type": "application/pdf"})
    b.source(S_HYENA_CARD, "LongSafari/hyenadna-tiny-1k-seqlen model card (README.md)",
             "Official Hugging Face model card, pinned to a revision; lists suggested GPUs for each HyenaDNA checkpoint.",
             {"url": f"https://huggingface.co/LongSafari/hyenadna-tiny-1k-seqlen/blob/{HF_REV}/README.md", "publication_status": "official_project_source",
              "licence": "BSD-3-Clause", "version": "Hugging Face revision " + HF_REV + " (last modified 2023-08-13)", "media_type": "text/markdown"})
    d_pre = b.entity("dataset", P + "-data-hyenadna-table-a2-pretraining-data", "Pretraining corpora of the models in HyenaDNA Table A.2",
                     "Each model's own pretraining data; Table A.2 does not name the corpora.",
                     {"population": "Not stated in Table A.2", "split": "Not applicable: pretraining compute", "source_locator": "Table A.2 (page 17)",
                      "missing_metadata": {"version": {"reason": "unreported", "note": "Table A.2 compares pretraining runs on different corpora"}}},
                     [S_HYENA])
    p = b.entity("protocol", P + "-protocol-hyenadna-pretraining-compute", "Pretraining GPUs and runtime for short-range models (HyenaDNA Table A.2)",
                 "GPUs, wall-clock time and GPU-hours of pretraining for DNABERT, Nucleotide Transformer 2.5B and two small HyenaDNA models.",
                 {"protocol": "Pretraining cost as printed: GPUs used, wall-clock time and GPU-hours per model. HyenaDNA rows are the authors' own runs; the DNABERT and Nucleotide Transformer rows are stated without a cited source in the table.",
                  "version": "arXiv v2 Table A.2", "metric": "accelerator-time",
                  "limitations": ["Mixes GPU types (RTX 2080 Ti, A100 80GB, A100 40GB), so GPU-hours are not comparable in cost.",
                                  "The two HyenaDNA models are tiny (436K and 1.6M parameters) next to 110M and 2.5B, and pretrain on different data and sequence lengths."],
                  "source_locator": "Table A.2 (page 17)"}, [S_HYENA], links=[{"relation": "uses_data", "target_id": d_pre}])
    specs = [("dnabert-110m", 0, M_DNABERT, "DNABERT 110M", "8 × NVIDIA RTX 2080 Ti", "paper_compilation"),
             ("nt-2-5b", 1, M_NT, "Nucleotide Transformer 2.5B", "128 × NVIDIA A100 80GB", "paper_compilation"),
             ("hyenadna-436k", 2, M_HYENA, "HyenaDNA 436K", "1 × NVIDIA A100 40GB", "author_reported"),
             ("hyenadna-1-6m", 3, M_HYENA, "HyenaDNA 1.6M", "1 × NVIDIA A100 40GB", "author_reported")]
    note = "Deterministic parse of pdftotext -layout output of page 17; table title, column labels and all four row labels asserted."
    loc = "Table A.2 (page 17), row '{}', column {} ('{}', {})"
    for key, j, target, label, gpus, origin in specs:
        c = b.entity("configuration", f"{P}-config-hyenadna-table-a2-{key}-pretraining", f"{label} pretraining (HyenaDNA Table A.2)",
                     f"Pretraining run of {label} as listed in HyenaDNA Table A.2.",
                     {"reported_name": f"{HYENA_COLS[j]} ({rows['Params'][j]})", "parameters": rows["Params"][j],
                      "hardware": {"description": gpus + " (printed '" + rows["GPUs"][j] + "')"}, "source_locator": "Table A.2 (page 17)",
                      "missing_metadata": {"version": {"reason": "unreported"}}},
                     [S_HYENA], links=[{"relation": "configuration_of", "target_id": target}], method_types=["foundation_model"])
        ev = b.evaluation(f"{P}-eval-hyenadna-table-a2-{key}-pretraining", f"{label} pretraining compute (HyenaDNA Table A.2)", c, p, d_pre,
                          [S_HYENA], origin, {"dataset_version": None, "split": "Not applicable", "population": None, "inputs": "DNA sequence",
                                              "adaptation": "Pretraining from scratch", "metric_implementation": None, "aggregation": "Total per run", "budget": None},
                          "Table A.2 (page 17)", extra={"training_hardware": gpus})
        colref = f"{j + 1} of 4"
        b.result(f"{P}-result-hyenadna-table-a2-{key}-gpu-hours", f"{label} pretraining GPU-hours (HyenaDNA Table A.2)", ev, [S_HYENA],
                 rows["GPU-hrs"][j], "accelerator-time", "lower", "hour", loc.format("GPU-hrs", colref, HYENA_COLS[j], rows["Params"][j]),
                 PDF_PARSE, note, qualifier="Pretraining, total", unit_detail="GPU-hours on " + gpus)
        wc = rows["Wall clock"][j]
        val, unit = wc.split()
        b.result(f"{P}-result-hyenadna-table-a2-{key}-wall-clock", f"{label} pretraining wall-clock time (HyenaDNA Table A.2)", ev, [S_HYENA],
                 val, "runtime", "lower", {"days": "day", "mins": "minute"}[unit], loc.format("Wall clock", colref, HYENA_COLS[j], rows["Params"][j]),
                 PDF_PARSE, note, qualifier="Pretraining, wall clock", unit_detail=f"Printed as '{wc}'")
    b.claim(P + "-claim-hyenadna-suggested-gpus", "HyenaDNA suggested GPUs per checkpoint (model card)", M_HYENA, "hardware_requirement",
            "Suggested GPUs for pretraining, fine-tuning and inference: tiny-1k (T4, T4, T4); small-32k (A100-40, T4, T4); medium-160k (A100-40, A100-40, T4); medium-450k (A100-40, A100-40, T4); large-1m (A100-80, A100-80, A100-40). T4 has 16 GB, A100-40 40 GB and A100-80 80 GB. The card adds that the Colab notebook can run inference on sequences up to 450k on the free tier (T4) and up to 1 million on the paid tier (A100).",
            "Model card section 'GPU requirements (suggested)' and the Colab paragraph", [S_HYENA_CARD], PROSE,
            "Exact list lines asserted in the pinned model card.", limitations=["Suggestions from the developers, not measured requirements; no batch size or sequence length is attached to them."])


# ======================================================================== AlphaGenome (Avsec et al. 2026)
def alphagenome(b, d):
    xml = os.path.join(d, "PMC12851941.xml")
    text = xml_text(xml)
    s_inf = need(text, "Taking less than 1 s on an NVIDIA H100 GPU, the student model is highly efficient for large-scale variant effect prediction relative to the alternative approach of ensembling several independently trained models.")
    supp = flat(pdf_text(os.path.join(d, "MOESM1.pdf"), 20, 22))
    need(supp, "Each gradient step processed a batch size of 64 samples using 8-way sequence parallelism, requiring 512 TPUv3 cores, with pre-training runs typically completing in approximately 4 hours.")
    need(supp, "Training proceeded for a fixed duration of 15,000 steps without early stopping.")
    need(supp, "distribute the computation for each 1 Mb input interval across 8 TPU cores.")
    need(supp, "Distillation training was performed without sequence parallelism across 64 NVIDIA H100 GPUs, with a batch size of 64 (effectively one sample per GPU).")
    need(supp, "The distillation process ran for 250,000 steps, taking approximately 3 days.")
    readme = flat(open(os.path.join(d, "README-0db53bd.md"), encoding="utf-8").read())
    need(readme, "In order to run the model, we recommend running with at least an [NVIDIA H100 GPU](https://docs.cloud.google.com/compute/docs/gpus#h100-gpus).")
    need(readme, "For training, we recommend running on [Tensor Processing Units (TPUs) v3](https://docs.cloud.google.com/tpu/docs/v3) or higher.")
    need(readme, "We strongly recommend using our [AlphaGenome API](https://deepmind.google.com/science/alphagenome) to interact with the model without needing specialized hardware.")

    b.source(S_AG, "Advancing regulatory variant effect prediction with AlphaGenome (Nature), Europe PMC full-text XML",
             "Primary article retrieved and hashed for the genomic foundation model guide sources pass (issue #138). The stored retrieval of the same URL (evidence-official-56e5abfb5f12f1cd3b20, 2026-09-16) has different bytes, so this retrieval is pinned separately.",
             {"url": "https://doi.org/10.1038/s41586-025-10014-0", "doi": "10.1038/s41586-025-10014-0", "publication_status": "peer_reviewed",
              "licence": "CC-BY-4.0", "version": "Nature, version of record 28 January 2026; PMC12851941 full-text XML", "media_type": "application/xml"})
    b.claim(P + "-claim-alphagenome-variant-scoring-time", "AlphaGenome distilled model time per variant", M_AG, "inference_hardware",
            "The distilled student model makes predictions for all modalities and cell types with a single device call per variant, taking less than 1 s on an NVIDIA H100 GPU.",
            "Results, 'Unifying DNA sequence-to-function model', paragraph 2: '" + s_inf + "'", [S_AG], PROSE,
            "Exact sentence asserted in the pinned XML text.", limitations=["Upper bound stated in prose; batch size, sequence length and whether model loading is included are not stated."])
    b.claim(P + "-claim-alphagenome-training-compute", "AlphaGenome pre-training and distillation compute", M_AG, "training_compute",
            "Pre-training used TPU v3 with 8-way sequence parallelism (each 1 Mb interval split across 8 TPU cores); each gradient step of 64 samples required 512 TPUv3 cores, and a pre-training run of 15,000 steps typically completed in about 4 hours. Distillation ran without sequence parallelism on 64 NVIDIA H100 GPUs (batch size 64, one sample per GPU) for 250,000 steps, taking about 3 days.",
            "Supplementary Methods, 'Sequence Parallelism' (page 20), 'Pre-training' (page 21) and 'Distillation' / 'Model Training Parameters' (pages 21-22)",
            [S_AG_SUPP], PROSE, "Exact sentences asserted in pdftotext output of pages 20-22 of the pinned supplement (SHA-256 matches the stored source record).",
            limitations=["Per-run figures; the number of pre-training runs (fold-specific and all-folds teachers, 64 all-folds models used in distillation) is described elsewhere and not totalled here."])
    b.claim(P + "-claim-alphagenome-recommended-hardware", "AlphaGenome recommended hardware (repository README)", M_AG, "hardware_requirement",
            "The official repository recommends running the model on at least an NVIDIA H100 GPU, training on TPU v3 or higher, and strongly recommends the AlphaGenome API for use without specialised hardware.",
            "README.md 'Model requirements' and introduction, commit 0db53bd", [S_AG_README], PROSE,
            "Exact sentences asserted in the pinned README (SHA-256 matches the stored source record).")


# ======================================================================== use-case text correction (issue #138, Fix)
UC_RNA = "use-case-patient-rna-splicing-validation"
S_FENG = "evidence-expansion-dna-foundation-models-2025-5d8ca9bc"
FRASER = ("FRASER, applied to a retrospective Kremer rare-mitochondrial-disorder skin-fibroblast RNA cohort (119 samples/105 individuals, "
          "13 known pathogenic splicing events), recovers a mean 85% (11 of 13) of known events at a reduced 30-sample subsample.")
# The setting text is pinned by 18 reviewed judgements, so its correction is left to the reviewer (see the dated review).
UC_SETTING_PROPOSAL = [
    ("setting", "attributes.setting",
     FRASER + " A separate, proxy sequence-classification AUC for DNA foundation-model embeddings (Feng et al. 2025, Table 1 Acceptor/Donor) is also linked, scoped as a different endpoint.",
     FRASER + " Feng et al. 2025 Table 1 splice acceptor and donor classification by DNA foundation-model embeddings is not linked here; it is linked to 'Prioritise variants for splicing experiments'."),
]
UC_FIXES = [
    ("evidence-gaps-2", "attributes.evidence_gaps[2]",
     "The sequence-classification proxy mapping (Feng Table 1) measures AUC on a different population (DNABERT-2/NT benchmark splice-site datasets), not minigene reporter exon inclusion or patient RNA, and must not be pooled with the FRASER recovery figure.",
     "No DNA foundation-model result is linked to this use case. Feng et al. 2025 Table 1 splice-site classification is linked to 'Prioritise variants for splicing experiments' instead, because it measures AUC on benchmark splice-site sequences (DNABERT-2/NT datasets), not on patient RNA."),
]


def usecase_fix(b):
    for slug, field, old, new in UC_FIXES:
        rid = f"metadata-correction-{P}-patient-rna-splicing-{slug}"
        b.rows.append([rid, S_FENG, "use-case-splicing-follow-up assessed_by links", new[:200], "claim"])
        b.add({"id": rid, "kind": "claim", "name": f"Select a patient-RNA splicing-variant validation workflow: {field}",
               "description": "The text said Feng et al. 2025 Table 1 is linked to this use case. Its acceptor and donor protocols are linked to use-case-splicing-follow-up only. Historical releases retain the previous value.",
               "status": "needs_review", "facets": {}, "source_ids": [S_FENG],
               "links": [{"relation": "subject", "target_id": UC_RNA}],
               "attributes": {"field": field, "previous_value": old, "value": new,
                              "source_locator": "Store links: use-case-splicing-follow-up assessed_by amp-feng-20261007-protocol-splice-acceptor and -splice-donor; no assessed_by link from use-case-patient-rna-splicing-validation to any Feng protocol (origin/main 7999572)",
                              "review": {"method": ["transcription"], "method_note": "Compared the use case's links and the Feng judgement claims' subjects in the store at origin/main 7999572.",
                                         "reviewer": ["claude"], "reviewer_note": EXTRACTOR_NOTE, "date": TODAY,
                                         "note": "Proposed correction, not reviewed."}}})


def main(art, out):
    for f, (want, _, _) in ARTIFACTS.items():
        got = sha256(os.path.join(art, f))
        assert got == want, f"{f}: {got} != {want}"
    b = Batch(art)
    evee(b, art)
    hegde(b, art)
    ntv3(b, art)
    nt(b, art)
    hyena(b, art)
    alphagenome(b, art)
    usecase_fix(b)
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
    print(json.dumps(counts, sort_keys=True))


if __name__ == "__main__":
    main(*sys.argv[1:3])
