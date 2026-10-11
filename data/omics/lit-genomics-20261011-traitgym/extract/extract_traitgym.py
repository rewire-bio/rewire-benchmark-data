"""TraitGym official metrics (songlab/TraitGym Hugging Face dataset at a pinned revision):
AUPRC_by_chrom_weighted_average/all for mendelian_traits_matched_9 and complex_traits_matched_9.

Usage: python3 -I extract_traitgym.py <hf-folder> <batch-folder> <bundle-out.json>
The bundle (every CSV's path, SHA-256 and bytes) is the hashed artifact.
"""
import sys, os, json, csv, io, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import Batch, extraction_review

hf, folder, bundle_out = sys.argv[1:4]
REV = "1fde19555fe8c0a55b1382bdf4c6f7082209f566"
DSETS = ["mendelian_traits_matched_9", "complex_traits_matched_9"]
bundle = {"repository": "https://huggingface.co/datasets/songlab/TraitGym", "revision": REV, "files": []}
for ds in DSETS:
    for name in sorted(os.listdir(os.path.join(hf, ds))):
        raw = open(os.path.join(hf, ds, name), "rb").read()
        bundle["files"].append({"path": f"{ds}/AUPRC_by_chrom_weighted_average/all/{name}", "sha256": hashlib.sha256(raw).hexdigest(), "content": raw.decode()})
blob = json.dumps(bundle, indent=1, sort_keys=True).encode() + b"\n"
open(bundle_out, "wb").write(blob)
SHA = hashlib.sha256(blob).hexdigest()
assert len(bundle["files"]) == 156, len(bundle["files"])
URL = f"https://huggingface.co/datasets/songlab/TraitGym/tree/{REV}"

b = Batch(folder, "lit-genomics-20261011-traitgym")
SRC = b.source("lit-genomics-20261011-traitgym-source-hf-metrics", "TraitGym official metrics: AUPRC by chromosome, weighted average (Hugging Face dataset songlab/TraitGym)", {
    "url": "https://huggingface.co/datasets/songlab/TraitGym", "artifact_url": URL,
    "version": f"Hugging Face dataset revision {REV} (last modified 2025-03-25); 156 metric CSVs under {{dataset}}/AUPRC_by_chrom_weighted_average/all/",
    "retrieved_at": "2026-10-11T01:40:33Z", "retrieval_note": "156 CSVs downloaded 01:39-01:40 UTC from the resolve endpoint at the pinned revision; time is the last download", "artifact_sha256": SHA, "publication_status": "official_project_source", "licence": "MIT",
    "hash_scope": "SHA-256 of a JSON bundle listing every retrieved CSV with its path, its own SHA-256 and its bytes (artifacts/traitgym-metrics-bundle.json.gz)",
    "media_type": "application/json",
    "limitations": ["Official benchmark repository by the TraitGym authors, who also developed GPN-MSA and GPN-Promoter; those rows are author_reported.",
                    "Benchmark paper: Benegas, Eraslan and Song, bioRxiv 10.1101/2025.02.11.637758 v2 (2025-03-04, CC BY-NC-ND), outside the search window; its Figure 2 plots these metrics. The paper's Table S8 prints rounded zero-shot AUPRCs on a related but unweighted basis and was not extracted.",
                    "Hugging Face datasets are mutable; the revision hash pins this retrieval."]})
SIDS = [SRC]
REVIEW = lambda loc: extraction_review(["deterministic-table-parse"], "Read the single data row (model, metric, score, se) of each pinned CSV with tools/extract_traitgym.py; the metric column is asserted to be AUPRC and the model column to match the file name. " + loc,
                                       SHA, URL)

BENCH = b.entity("benchmark", b.rid("benchmark", "traitgym"), "TraitGym",
    "Causal versus matched non-causal noncoding variants for 113 Mendelian and 83 complex traits, scored by AUPRC computed per chromosome and averaged with sample-size weights.",
    SIDS, {"entity_level": "suite", "version": f"Hugging Face revision {REV[:12]}", "task": "Causal regulatory variant prediction",
           "scope_note": "Datasets mendelian_traits_matched_9 and complex_traits_matched_9 (nine matched controls per causal variant), subset 'all'. Zero-shot scores and chromosome-held-out logistic regression (linear probing).",
           "source_locator": "README 'Resources' and 'Running'; dataset paths in this batch"})
DATA = {}
PROTO = {}
for ds, label in (("mendelian_traits_matched_9", "Mendelian traits"), ("complex_traits_matched_9", "Complex traits")):
    DATA[ds] = b.entity("dataset", b.rid("data", ds), f"TraitGym {label}, matched 9 controls", f"TraitGym {ds}: causal variants with nine matched negative controls each.", SIDS,
                        {"version": f"Hugging Face revision {REV[:12]}", "split": "Leave-one-chromosome-out for linear probing; all variants scored for zero-shot",
                         "population": f"{label}; nine matched controls per causal variant (baseline AUPRC 0.1)", "source_locator": f"{ds}/test.parquet (not downloaded); README"})
    for mode, desc in (("zero-shot", "zero-shot score"), ("linear-probing", "ridge logistic regression on extracted features, trained on the other chromosomes")):
        PROTO[(ds, mode)] = b.entity("protocol", b.rid("protocol", ds, mode), f"TraitGym {label}, {mode}, AUPRC by chromosome weighted average",
            f"TraitGym {label} with {desc}.", SIDS,
            {"protocol": f"{desc}; AUPRC computed per chromosome and averaged with weights by sample size; standard error by bootstrap (paper Appendix B.4).",
             "version": f"Hugging Face revision {REV[:12]}", "metric": "auprc", "metric_direction": "higher", "unit": "unitless",
             "limitations": ["Baseline AUPRC is 0.1.", "Labels come from fine-mapping (complex traits) and curated pathogenic variants (Mendelian), not experiments.", "Benchmark authors developed GPN-MSA and GPN-Promoter."],
             "source_locator": "File names under AUPRC_by_chrom_weighted_average/all/; paper Section 2 'evaluation metric'"},
            links=[{"relation": "part_of", "target_id": BENCH}, {"relation": "uses_data", "target_id": DATA[ds]}])

# model token -> (family id or new family spec, reported checkpoint, foundation model?)
FAM = {
    "AIDO.DNA": ("lit-genomics-20261011-guanine-model-aido-dna", "genbio-ai/AIDO.DNA-7B", True),
    "Borzoi": ("regulatory-variant-20261009-model-borzoi", "gReLU model zoo", False),
    "Enformer": ("regulatory-variant-20261009-model-enformer", "gReLU model zoo", False),
    "CADD": ("somatic-oncogenicity-20261009-method-cadd", "CADD v1.7", False),
    "Caduceus": ("regulatory-variant-20261009-model-caduceus", "kuleshov-group/caduceus-ps_seqlen-131k_d_model-256_n_layer-16", True),
    "GPN-MSA": ("regulatory-variant-20261009-model-gpn", "songlab/gpn-msa-sapiens", True),
    "GPN_final": ("regulatory-variant-20261009-model-gpn", "GPN-Promoter (the authors' model; 'GPN_final' in file names, named GPN-Promoter in config/models.csv)", True),
    "HyenaDNA": ("regulatory-variant-20261009-model-hyenadna", "LongSafari/hyenadna-medium-160k-seqlen-hf", True),
    "NucleotideTransformer": ("discovery-model-nucleotide-transformer", "InstaDeepAI/nucleotide-transformer-2.5b-multi-species", True),
    "Sei": ("regulatory-variant-20261009-model-sei", "Sei web server", False),
    "SpeciesLM": (None, "johahi/specieslm-metazoa-upstream-k6", True),
    "evo2_1b_base": ("discovery-model-evo-2", "Evo2 1B base", True),
    "evo2_7b": ("discovery-model-evo-2", "Evo2 7B", True),
    "evo2_40b": ("discovery-model-evo-2", "Evo2 40B", True),
    "phyloP-100v": ("somatic-oncogenicity-20261009-method-phylop", "hg38.phyloP100way", False),
    "phyloP-241m": ("somatic-oncogenicity-20261009-method-phylop", "cactus241way phyloP", False),
    "phastCons-43p": (None, "Zoonomia primate phastCons (43 primates)", False),
}
new = {}
def family(tok):
    f = FAM[tok][0]
    if f:
        return f
    if tok not in new:
        name, kind, desc, mt = {"SpeciesLM": ("SpeciesLM", "model", "Species-aware DNA language model (SpeciesLM).", ["foundation_model"]),
                                "phastCons-43p": ("phastCons", "method", "phastCons conservation score.", ["conventional_pipeline"])}[tok]
        new[tok] = b.entity(kind, b.rid(kind, name), name, desc, SIDS, {"reported_name": name, "entity_level": "family" if kind == "model" else "method",
                            "source_locator": "config/models.csv; paper Table S5", "missing_metadata": {"version": {"reason": "inapplicable", "note": "Family record"}}}, method_types=mt)
    return new[tok]

def ensemble_family(name):
    if name not in new:
        new[name] = b.entity("method", b.rid("method", name, "logistic-regression"), f"{name} logistic regression ensemble",
                             f"Logistic regression on the combined features of {name.replace('+', ', ')}, trained on the other chromosomes (TraitGym).", SIDS,
                             {"reported_name": name, "entity_level": "method", "source_locator": "File names '<features>.LogisticRegression.chrom.csv'; config/models.csv",
                              "missing_metadata": {"version": {"reason": "inapplicable", "note": "Ensemble defined by its feature sets"}}}, method_types=["supervised_machine_learning"])
    return new[name]

SCORE = {"LLR.minus.score": "negative log-likelihood ratio", "absLLR.plus.score": "absolute log-likelihood ratio",
         "Embeddings.minus.inner_product": "negative inner product of embeddings", "Embeddings.plus.cosine_distance": "cosine distance of embeddings",
         "Embeddings.plus.euclidean_distance": "Euclidean distance of embeddings", "InnerProduct.minus.score": "negative inner product score",
         "EuclideanDistance.plus.score": "Euclidean distance score", "L2_L2.plus.all": "L2 norm of predicted track differences",
         "plus.seqclass_max_absdiff": "maximum absolute sequence-class score difference", "plus.RawScore": "raw score", "plus.score": "score"}
cfgs = {}
n = 0
for f in bundle["files"]:
    ds = f["path"].split("/")[0]
    fname = f["path"].split("/")[-1][:-4]
    rows = list(csv.DictReader(io.StringIO(f["content"])))
    assert len(rows) == 1 and rows[0]["metric"] == "AUPRC" and rows[0]["model"] == fname, (f["path"], rows)
    if fname.endswith(".LogisticRegression.chrom"):
        tok, mode, scoring = fname[:-len(".LogisticRegression.chrom")], "linear-probing", "ridge logistic regression on extracted features (chromosome folds)"
    else:
        tok = max((k for k in FAM if fname.startswith(k + "_") or fname.startswith(k + ".")), key=len)
        rest = fname[len(tok) + 1:]
        mode, scoring = "zero-shot", SCORE[rest]
    if "+" in tok:
        fam, ckpt, fm = ensemble_family(tok), "Ensemble of " + tok.replace("+", ", "), False
    else:
        fam, ckpt, fm = family(tok), FAM[tok][1], FAM[tok][2]
    key = fname
    if key not in cfgs:
        cfgs[key] = b.entity("configuration", b.rid("config", fname), f"{fname} (TraitGym)", f"{tok} scored as '{scoring}' in TraitGym.", SIDS,
            {"reported_name": fname, "foundation_model_eligible": fm, "parameters": f"{ckpt}; {scoring}",
             "access_reuse": "Public weights or score files (paper Appendix B.1)" if tok != "GPN_final" else "GPN-Promoter weights: see the GPN repository",
             "source_locator": f"File name '{fname}.csv'; config/models.csv; paper Table S5",
             **({"version": ckpt} if tok in ("CADD", "AIDO.DNA", "Caduceus", "GPN-MSA", "HyenaDNA", "NucleotideTransformer", "SpeciesLM") else
                {"missing_metadata": {"version": {"reason": "unreported", "note": "Only the label in the file name identifies the model"}}})},
            method_types=["foundation_model"] if fm else (["supervised_machine_learning"] if tok in ("Borzoi", "Enformer", "Sei", "CADD") or "+" in tok else ["conventional_pipeline"]),
            links=[{"relation": "configuration_of", "target_id": fam}])
    p, d = PROTO[(ds, mode)], DATA[ds]
    origin = "author_reported" if tok in ("GPN-MSA", "GPN_final") or "GPN-MSA" in tok else "independent_paper"
    ev = b.evaluation(b.rid("eval", fname, ds), f"{fname} on TraitGym {ds}", SIDS, cfgs[key], p, d, origin,
        {"protocol_id": p, "dataset_version": f"Hugging Face revision {REV[:12]}", "split": "Leave-one-chromosome-out" if mode == "linear-probing" else "All variants",
         "population": None, "inputs": "Reference and alternate allele with DNA sequence context", "adaptation": mode,
         "metric_implementation": "AUPRC per chromosome, weighted average by sample size", "aggregation": "Weighted average over chromosomes", "budget": None},
        f"{f['path']}")
    loc = f"{f['path']}, column 'score' (standard error in column 'se')"
    b.result(b.rid("result", fname, ds), f"{fname} TraitGym {ds} AUPRC", SRC, SIDS, ev, rows[0]["score"], "auprc", "higher", "unitless", loc,
             REVIEW(f"File SHA-256 {f['sha256']}."), qualifier="weighted average over chromosomes of per-chromosome AUPRC; subset 'all'",
             uncertainty={"type": "standard_error", "value": rows[0]["se"], "method": "bootstrap", "printed": rows[0]["se"], "source_column": "se"},
             extra={"printed_value_basis": "Full-precision number as stored in the official CSV"})
    n += 1
assert n == 156
print(SHA, json.dumps(b.write()))
