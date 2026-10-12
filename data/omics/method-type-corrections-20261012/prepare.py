"""Method-type tag corrections from docs/reviews/use-cases/baselines-2026-10-12.md, 2026-10-12.
Run from the repository root: python3 -I data/omics/method-type-corrections-20261012/prepare.py

Writes, in this folder:
- corrections.csv: the staged store edits, in the format of `npm run records:correct`
  (record_id, field, old_value, new_value, evidence). Not applied to the store.
- batch.jsonl: one needs_review metadata-correction claim per changed record, keeping the previous
  value, and two new source records (Benelli et al. 2012 for EricScript, Shi and Chen 2019 for LSHVec).
The store is read, never written. Every row is checked against the current value first.
"""
import csv, hashlib, json, os

HERE = "data/omics/method-type-corrections-20261012"
DATE = "2026-10-12"
REVIEW = "docs/reviews/use-cases/baselines-2026-10-12.md"
FM, SML, CP = "foundation_model", "supervised_machine_learning", "conventional_pipeline"
BENELLI = "method-type-corrections-20261012-source-benelli2012"

recs = {}
for f in ["configurations", "methods", "models", "pipelines", "services"]:
    for line in open(f"data/entities/{f}.jsonl"):
        r = json.loads(line)
        recs[r["id"]] = r

# Each group: record IDs, new value, the review's evidence locator, extra sources that hold that
# evidence, and which review table the row is from (1: changes a same-data answer, 2: does not).
groups = []


def group(ids, new, locator, extra=(), table=2, note=""):
    groups.append({"ids": ids, "new": new, "locator": locator, "extra": list(extra), "table": table, "note": note})


def ex(prefix, *suffixes):
    return [prefix + s for s in suffixes]


# Table 1: records that change a same-data answer.
group(ex("ucc-research-config-sctab-", "scgpt-ft", "scgpt-zero"), [FM],
      "scTab Methods: fine-tuned scGPT and frozen scGPT embeddings; catalog-model-scgpt configurations are foundation_model",
      ["ucc-research-source-sctab-paper"], 1)
group(["ucc-research-config-sctab-uce"], [FM],
      "scTab Methods: UCE embeddings with a linear probe; cell-type-20261009-config-wu2025-uce-onclass is foundation_model",
      ["ucc-research-source-sctab-paper"], 1)
group(ex("ucc-research-config-sctab-", "celltypist", "ciform", "mlp", "sctab", "xgboost", "linear"), [SML],
      "scTab Methods: each classifier is trained on labelled cells", ["ucc-research-source-sctab-paper"], 1)
group(ex("ucc-research-config-abdelaal-", "svm-no-rejection", "svm-rejection", "scpred"), [SML],
      "Abdelaal et al. 2019: supervised classifiers trained on a labelled reference", ["ucc-research-source-abdelaal-2019-paper"], 1)
group(["ucc-research-config-abdelaal-scmapcell"], [CP],
      "Abdelaal et al. 2019 Table 1: scmapcell is listed with classifier \"kNN\"; it labels each query cell from its nearest reference cells, with no fitted model parameters",
      ["ucc-research-source-abdelaal-2019-paper"], 1,
      "A nearest-neighbour vote over a labelled reference; supervised_machine_learning is also defensible. Either way it is a baseline row.")
group(ex("uc20260930-msalign-v2-config-", "deepset", "emb-cos", "jestr") + ex("msalign-2026-table3-method-", "deepsets", "emb-cos", "ffn", "jestr", "sail"),
      [SML], "MassSpecGym Section 4.1: Fingerprint FFN \"employs a feedforward neural network to predict the Morgan fingerprint\", and DeepSets; MSAlign arXiv 2605.19752 Table 1 and \"Baselines\" (v1 and v2): JESTR \"pretrains with batch InfoNCE\", Emb-Cos \"uses candidates InfoNCE to learn a shared space\", SAIL is trained with the batch loss",
      ["part2-massspecgym-arxiv-v1", "uc20260930-source-msalign-v2", "evidence-official-760ab2fa8c396aeb796c"], 1)
# MSAlign: foundation_model only once its source is checked (filled in below from the check).
MSALIGN_IDS = ["uc20260930-msalign-v2-config-msalign", "uc20260930-msalign-v2-config-msalign-score-fusion-overbar", "msalign-2026-table3-method-msalign"]
group(ex("uc20260930-jores-config-", "maize-protoplasts-cnn", "tobacco-leaves-cnn"), [SML],
      "Jores et al. 2021 p849: convolutional neural network", ["uc20260930-source-jores-2021"], 1)
group(ex("uc20260930-jores-config-", "maize-protoplasts-gc-motif-linear", "tobacco-leaves-gc-motif-linear"), [CP],
      "Jores et al. 2021 p849: linear regression on GC content and the maximum PWM match score", ["uc20260930-source-jores-2021"], 1,
      "The review says supervised_machine_learning is also defensible; either way it is a baseline row.")
group(ex("uc20260930-rhomax-config-", "rhomax", "rhomax-retinal"), [SML],
      "RhoMax Methods: a graph neural network trained on structures", ["uc20260930-source-rhomax-2024"], 1)
group(["uc20260930-rhomax-config-blasso"], [SML],
      "RhoMax: BLASSO is \"a first attempt to utilize machine learning\" (Bayesian LASSO)", ["uc20260930-source-rhomax-2024"], 1)
group(ex("uc20260930-framepool-config-", "framepool-50", "framepool-100", "framepool-combined", "optimus-50", "optimus-100"), [SML],
      "FramePool Methods: convolutional networks trained on the MPRA library", ["uc20260930-source-framepool-2021"], 1)
group(ex("uc20260930-framepool-config-", "3mer-random-forest", "4mer-random-forest", "5mer-frame-forest", "frame-forest-4mer", "frame-forest-hyperopt"), [SML],
      "FramePool Methods: \"we also trained random forest models which use k-mer counts as input features\"", ["uc20260930-source-framepool-2021"], 1)
group(["rna-fusion-20261009-method-ericscript", "rna-fusion-20261009-config-tamura2026-ericscript"], [SML],
      "Benelli et al. 2012 section 2.6: \"we trained an AdaBoost classifier\"; section 2.6.4: the classifier, trained with synthetic data, gives the EricScore that ranks candidate fusions",
      [BENELLI], 1, "Issue #121's locator (Tamura 2026 supplement) is wrong: it does not mention AdaBoost.")

# Table 2: records that do not change an answer.
group(["uc-clinical-20260930-method-bayesdel", "uc-clinical-20260930-bayesdel-enigma", "uc-clinical-20260930-bayesdel-pejaver-generic"], [SML],
      "Matches the other 7 BayesDel configurations; Ramadane 2025 calls BayesDel a meta-predictor", ["brca-20261009-source-ramadane2025"])
group(["uc-clinical-20260930-enigma-v10-manual"], [CP], "Manual criteria-based curation (record description)")
# HECTOR: conventional_pipeline only after checking its source (filled in below).
HECTOR_IDS = ["uc-clinical-20261005-hector-v1-2-config"]
group(["uc-clinical-20260930-method-oncovi", "uc-clinical-20260930-oncovi-study", "uc-clinical-20260930-oncovi-prior-mtb"], [CP],
      "OncoVI Methods: \"an IF-ELSE implementation\" of the points-based SOP", ["uc-clinical-20260930-source-oncovi"])
group(["somatic-oncogenicity-20261009-method-sift"] + ex("somatic-oncogenicity-20261009-config-", "chen2020-sift", "chen2020-sift4g", "lee2026-sift", "lee2026-sift4g"),
      [CP], "Chen et al. 2020 Table 1: SIFT uses a position-specific scoring matrix", ["somatic-oncogenicity-20261009-source-chen2020"])
group(["somatic-oncogenicity-20261009-method-provean"] + ex("somatic-oncogenicity-20261009-config-", "chen2020-provean", "lee2026-provean"),
      [CP], "Chen et al. 2020 Table 1: PROVEAN uses a delta alignment score", ["somatic-oncogenicity-20261009-source-chen2020"],
      note="Named in the SIFT row's evidence (\"The same applies to PROVEAN\") rather than in its record IDs.")
group(["uc-clinical-20260930-method-exomiser", "uc-clinical-20260930-exomiser-v14"], [CP],
      "Other Exomiser configurations; Yuan et al. 2022 Table 2 classes Exomiser by phenotype comparison", ["rare-ranking-20261009-source-yuan2022"])
group(ex("uc-clinical-20260930-talos-", "default", "strict", "monthly"), [CP],
      "Other Talos configurations; Kaschta 2026", ["reanalysis-kaschta-20261010-source-kaschta2026"])
group(["amp-config-dragen42-cnv-sv", "amp-config-dragen42-phase4-runtime"], [CP], "Other DRAGEN configurations (cnv-20261009-method-dragen) are conventional_pipeline",
      note="The review also proposes a configuration_of link to cnv-20261009-method-dragen; not added here.")
group(["model-execution-20261009-config-samarakoon2025-parabricks-4-3-0-1-8xh100"], [SML],
      "Samarakoon et al. 2025 Supplementary Table S4: Parabricks DeepVariant only; model-execution-20261011-model-deepvariant is supervised_machine_learning")
group(["uc-clinical-20260930-civic-gpt5-alone", "uc-clinical-20260930-civic-gpt5-mcp", "uc-clinical-20260930-civic-agent-mode", "ucc-clinical-egfr-config-qwen3-reranker-8b"],
      [FM], "Record names and descriptions: GPT-5, ChatGPT Agent Mode and Qwen3-Reranker-8B are large pretrained language models used without task training",
      note="The review marks these as the proposer's, not source-checked.")
group(["ucc-clinical-egfr-config-medcpt-ft"], [SML], "Record description: MedCPT cross-encoder fine-tuned on the CIViC-Fact training data",
      note="The review marks this as the proposer's, not source-checked.")
# LSHVec: supervised_machine_learning only after reading its method paper (filled in below).
LSHVEC_IDS = ["rna-pathogen-20261009-method-lshvec", "rna-pathogen-20261009-config-meyer2022-lshvec"]
group(["catalog-model-kraken2"], [CP], "Its configurations are conventional_pipeline; minimizer database lookup (record description)")
group(["ctdnameth-20261009-method-methatlas", "ctdnameth-20261009-method-celfie"]
      + ex("ctdnameth-20261009-config-", "sun2024-methatlas", "sun2024-celfie", "sun2024-celfeer", "sun2024-uxm",
           "giuili2025-methatlas", "giuili2025-celfie", "giuili2025-uxm", "giuili2025-houseman-eq", "giuili2025-houseman-ineq", "giuili2025-epidish-rpc"),
      [CP], "Sun et al. 2024 Background: deconvolution by non-negative least squares (MethAtlas) and expectation-maximisation (CelFiE) fitting",
      ["ctdnameth-20261009-source-sun2024"])
group(["ctdnafrag-20261009-config-wang2026-ichorcna-tf-logistic-regression"], [SML],
      "Wang et al. 2026 Results: ichorCNA tumour fraction fed to a one-feature logistic regression (ichorCNA-TF)", ["ctdnafrag-20261009-source-wang2026"],
      note="Optional in the review; it is a baseline row either way.")
group(["lit-genomics-20261011-dnalongbench-config-abc"], [CP],
      "DNALongBench Results: the expert model is ABC, \"which incorporates DNase-seq, H3K27ac ChIP-seq data, and a Hi-C matrix\"; MPRAbc Introduction: ABC is \"a mathematical framework\" combining activity and contact",
      ["lit-genomics-20261011-dnalongbench-source-cheng2025", "ucc-research-source-mprabc"])
group([f"amp-feng-20261007-config-qtl-{q}-{m}" for q in ["eqtl", "ipaqtl", "paqtl", "sqtl"]
       for m in ["enformer-hidden-states", "enformer-output-tracks", "sei-hidden-states", "sei-output-tracks", "alphagenome-output-tracks"]]
      + [f"amp-feng-20261007-config-variant-{m}" for m in ["enformer-hidden-states", "enformer-output-tracks", "sei-hidden-states", "sei-output-tracks"]],
      [SML], "The store's Enformer and Sei model records (regulatory-variant-20261009-model-enformer, regulatory-variant-20261009-model-sei) are supervised_machine_learning",
      note="The review did not read the Feng source. These configurations have no method link. catalog-model-alphagenome is tagged foundation_model; Feng prints AlphaGenome with an asterisk as a non-DNA-foundation comparator.")
group(["lit-structure-20261011-lipp-config-diffdock-l", "catalog-model-diffdock-l"], [SML],
      "LiPP: \"AI-based docking tool\", \"Trained on complexes in PDBbind before 2019\"", ["evidence-expansion-p2-lipp-2026-6ff34f2f709a"])
group(["ucc-research-config-mprabc-abc"], [CP], "MPRAbc Introduction: ABC is \"a mathematical framework\"", ["ucc-research-source-mprabc"])
group(ex("ucc-research-config-mprabc-", "re2g", "full", "megamap", "mpralegnet", "sei"), [SML],
      "MPRAbc: \"trained within the ENCODE-rE2G framework\"", ["ucc-research-source-mprabc"])
group(ex("ucc-docking-cluspro-bm5-2020-config-", "others", "enzyme-balanced"), [CP], "ClusPro BM5: FFT rigid-body docking", ["ucc-docking-cluspro-bm5-2020-source"])
group(ex("ucc-research-config-foldbench-", "af3", "boltz1", "chai1", "helixfold3", "protenix"), [FM],
      "Matches other AlphaFold 3 and Chai-1 configurations", note="The review did not read FoldBench.")
group(ex("agront-2024-fig3e-method-agront-promoter-strength-", "maize-protoplasts", "tobacco-leaves"), [FM],
      "AgroNT is a pretrained genomic language model", ["agront-2024-paper-methods"])
group(ex("agront-2024-fig3e-method-cnn-jores-et-al-promoter-strength-", "maize-protoplasts", "tobacco-leaves"), [SML],
      "The Jores et al. 2021 CNN", ["uc20260930-source-jores-2021"],
      note="The review also proposes a configuration_of link to uc20260930-model-jores-plant-promoter-cnn; not added here.")
group(["rna-splicing-20261009-method-splice-predictor-consensus"] + [f"rna-splicing-20261009-config-drost2025-at-least-{n}" for n in range(1, 5)],
      [SML], "A vote over four trained predictors (SpliceAI, Pangolin, SPiP and SQUIRLS)", note="Optional in the review.")
group([f"rewire-mfass-matched-v1-configuration-{c}" for c in ["s0", "s1", "p0", "p1"]], [SML], "SpliceAI and Pangolin (configuration_of links)")
group(["rewire-local-20260920-configuration-flip2-train-mean", "rewire-local-20260920-configuration-flip2-composition", "rewire-local-20260921-configuration-composition22"],
      [CP], "Fixed training-mean and composition-ridge probes (record descriptions)")
group(["rewire-local-20260921-configuration-esm2-35m", "rewire-local-20260921-configuration-esm2-8m"], [FM], "Frozen ESM-2 embeddings with a ridge probe")

# ProteinGym AMFR: per method, following the proposer's report (data/omics/use-case-baselines-20261012/report.md).
AMFR = "uc20260930-proteingym-amfr-config-"
AMFR_FM = ["uc20260930-model-esm-1b", "discovery-model-esm-1v", "discovery-model-esm-2", "discovery-model-esmc", "discovery-model-esm3",
           "discovery-model-esm-if1", "uc20260930-model-progen2", "uc20260930-model-progen3", "uc20260930-model-rita", "uc20260930-model-protgpt2",
           "uc20260930-model-tranception", "uc20260930-model-carp", "uc20260930-model-xtrimopglm", "uc20260930-model-saprot", "uc20260930-model-prosst",
           "uc20260930-model-protssn", "uc20260930-model-poet", "uc20260930-model-msa-transformer", "uc20260930-model-mif", "uc20260930-model-mif-st",
           "uc20260930-model-mulan", "uc20260930-model-unirep", "uc20260930-model-unirep-evotuned", "uc20260930-model-s2f", "uc20260930-model-s2f-msa",
           "uc20260930-model-s3f", "uc20260930-model-s3f-msa", "uc20260930-model-aido-protein-rag", "uc20260930-model-protriever",
           "uc20260930-model-venusrem", "discovery-model-proteinmpnn"]
AMFR_SML = ["uc20260930-model-vespa", "uc20260930-model-vespal", "uc20260930-model-vespag"]


def amfr(models):
    return sorted(r["id"] for r in recs.values() if r["id"].startswith(AMFR)
                  and any(l["relation"] == "configuration_of" and l["target_id"] in models for l in r["links"]))


group(amfr(AMFR_FM), [FM], "Proposer's report, ProteinGym AMFR: protein language and structure-conditioned models fit foundation_model",
      note="Not source-checked in the review; this comparison has no baseline row.")
group(amfr(AMFR_SML), [SML], "Proposer's report, ProteinGym AMFR: VESPA, VESPAl and VespaG are supervised on embeddings",
      note="Not source-checked in the review; this comparison has no baseline row.")

# Conditional and per-method rows, decided by the source checks recorded in report.md.
exec(open(os.path.join(HERE, "decisions.py")).read())

csv_rows, claims, seen = [], [], set()
for g in groups:
    for rid in g["ids"]:
        assert rid not in seen, f"{rid} listed twice"
        seen.add(rid)
        r = recs[rid]
        old = r["facets"].get("method_types")
        if old == g["new"]:
            continue
        # records:correct replaces one facet value per row; a record has at most one method type here.
        assert old is None or len(old) == 1, rid
        csv_rows.append({"record_id": rid, "field": "facets.method_types", "old_value": old[0] if old else "",
                         "new_value": g["new"][0], "evidence": g["locator"]})
        why = (f"Correct the method type from {old[0] if old else 'none'} to {g['new'][0]} "
               f"(use-case baseline review 2026-10-12, table {g['table']}).") + (f" {g['note']}" if g["note"] else "")
        h = hashlib.sha256(f"{rid}|facets.method_types".encode()).hexdigest()[:20]
        claims.append({
            "id": f"metadata-correction-tags-20261012-{h}", "kind": "claim", "name": f"{r['name']}: facets.method_types",
            "description": why, "status": "needs_review", "facets": {},
            "source_ids": list(dict.fromkeys(r["source_ids"] + g["extra"])),
            "links": [{"relation": "subject", "target_id": rid}],
            "attributes": {"field": "facets.method_types", "previous_value": json.dumps(old) if old else "absent",
                           "value": json.dumps(g["new"]), "source_locator": g["locator"],
                           "review": {"method": ["automated-source-review"], "reviewer": ["claude"],
                                      "reviewer_note": "Claude (Opus 5.5) correction agent applying the independent use-case baseline review; not an independent review of this change",
                                      "date": DATE, "note": why + f" Evidence from {REVIEW}. Pending independent review."}}})

sources = [json.load(open(os.path.join(HERE, f))) for f in ["benelli-source.json", "shi2019-lshvec-source.json", "cppc-note-s1-source.json"]]
with open(os.path.join(HERE, "batch.jsonl"), "w") as out:
    for rec in sorted(claims + sources, key=lambda x: x["id"]):
        out.write(json.dumps(rec, ensure_ascii=False, separators=(",", ":")) + "\n")
with open(os.path.join(HERE, "corrections.csv"), "w", newline="") as out:
    w = csv.DictWriter(out, fieldnames=["record_id", "field", "old_value", "new_value", "evidence"])
    w.writeheader()
    w.writerows(csv_rows)
print(f"{len(csv_rows)} store edits, {len(claims)} correction claims")
