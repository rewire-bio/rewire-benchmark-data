#!/usr/bin/env python3
"""Deterministically build data/omics/use-case-coverage-amp-20261007/ from the
three research groups' candidate dossiers (data/omics/amp-coverage-20261007/
{oncology-rna,pathogens-fragmentomics,methylation-cnv-operations,feng}) and
reuse of the existing Feng source record.

Read-only against the research groups' directories: this script never writes
inside data/omics/amp-coverage-20261007/. All output lands under
data/omics/use-case-coverage-amp-20261007/, owned exclusively by this
integration pass.

Each declared artifact_sha256 identifies the uncompressed PUBLIC evidence
copy. The script verifies that digest before producing receipts. When the
public copy is a curator extract, original_artifact_sha256 separately retains
the retrieved full-source identity. Exact archive bytes have a separate hash.
Checking an extract does not establish fresh access to the original source.
"""
import gzip
import csv
import io
import hashlib
import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GROUPS = ROOT / "data/omics/amp-coverage-20261007"
OUT = ROOT / "data/omics/use-case-coverage-amp-20261007"
# Fixed, explicit review completion time -- NOT datetime.now(): regenerating
# this deterministic script (e.g. after a scope fix) must not silently imply
# a fresh independent review each run. Override only via AMP_REVIEW_AT when a
# new review genuinely occurred; see scripts/omics/build-amp-use-cases.py for
# the matching constant.
REVIEWED_AT = os.environ.get("AMP_REVIEW_AT", "2026-10-07T13:38:59Z")
REVIEWER = "Claude Sonnet AMP-integration worker, bounded transcription of Codex-checked primary values (workbench/amp-supervision/primary-review.md, integration-review-corrections.md); pending qualified human scientific review"


def slug(text):
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    s = re.sub(r"-+", "-", s)
    return s


def sha256_file(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


ARTIFACT_BINDINGS = {}  # repo-relative path -> {artifact_sha256, archive_sha256, matches_original_artifact_sha256}

_ARCHIVE_TRANSFORM_PATH = GROUPS / "archive-transformation.json"
_ARCHIVE_TRANSFORM_EXPECTED_SHA256 = "3aaf1f811e1963c44679d8e8f3c2aedeb0be26d10c5a09c187e45bb1ea3cc05d"


def _load_archive_transform_registry():
    """workbench/amp-supervision/archive-reuse-review.json's 24 planned
    substitutions landed as data/omics/amp-coverage-20261007/
    archive-transformation.json. Pin its own hash so a later, unreviewed
    edit to that registry cannot silently change what this script trusts as
    'the original full-source hash' for a transformed artifact."""
    if not _ARCHIVE_TRANSFORM_PATH.exists():
        raise FileNotFoundError("Required reviewed archive-transformation.json is missing")
    text = _ARCHIVE_TRANSFORM_PATH.read_text()
    actual = hashlib.sha256(text.encode("utf8")).hexdigest()
    if actual != _ARCHIVE_TRANSFORM_EXPECTED_SHA256:
        raise ValueError(f"archive-transformation.json changed since last reviewed: expected {_ARCHIVE_TRANSFORM_EXPECTED_SHA256}, got {actual}")
    registry = json.loads(text)
    return {c["review_artifact"]: c for c in registry["changes"]}


ARCHIVE_TRANSFORM_REGISTRY = _load_archive_transform_registry()


def bind_artifact(relpath, expected_artifact_sha256, known_original_sha256=None):
    """Verify the bytes CURRENTLY committed at relpath (read-only, under
    GROUPS) against the EXPECTED public receipt hash -- raise on any
    mismatch; never silently accept arbitrary current bytes as if they were
    pre-approved. expected_artifact_sha256 must come from the frozen
    research-group candidates.json (already updated by the archive worker
    when a substitution happened) or an explicit reviewed-input registry
    (ARCHIVE_TRANSFORM_REGISTRY, _bind_feng_inputs), never from re-hashing
    the file itself.

    Returns (artifact_sha256, archive_sha256, matches_original_artifact_sha256):
      - artifact_sha256: sha256 of the decompressed bytes at relpath; always
        equal to expected_artifact_sha256 (the function raises otherwise).
      - archive_sha256: sha256 of the committed .gz (or plain) bytes.
      - matches_original_artifact_sha256: whether this receipt's bytes equal
        the historically verified ORIGINAL full-source bytes. True when no
        substitution has happened for this path; false (not an error) once
        the archive-transformation registry confirms a receipt replaced the
        original (its original_artifact_sha256 then differs from
        artifact_sha256 by design)."""
    path = ROOT / relpath
    if not path.exists():
        raise FileNotFoundError(f"Referenced artifact does not exist: {relpath}")
    on_disk = path.read_bytes()
    # Receipts are not always gzipped (e.g. *.facts.json with no .gz suffix);
    # only decompress when the file actually is gzip.
    if relpath.endswith(".gz"):
        compressed, raw = on_disk, gzip.decompress(on_disk)
    else:
        compressed, raw = on_disk, on_disk
    artifact_sha256 = hashlib.sha256(raw).hexdigest()
    archive_sha256 = hashlib.sha256(compressed).hexdigest()
    if artifact_sha256 != expected_artifact_sha256:
        raise ValueError(
            f"Public artifact_sha256 does not match the expected reviewed value: {relpath} "
            f"(expected={expected_artifact_sha256}, actual={artifact_sha256})"
        )
    if known_original_sha256 is not None:
        original_artifact_sha256 = known_original_sha256
    else:
        transform = ARCHIVE_TRANSFORM_REGISTRY.get(relpath)
        original_artifact_sha256 = transform["original_artifact_sha256"] if transform else expected_artifact_sha256
    matches_original = artifact_sha256 == original_artifact_sha256
    ARTIFACT_BINDINGS[relpath] = {
        "artifact_sha256": artifact_sha256,
        "archive_sha256": archive_sha256,
        "matches_original_artifact_sha256": matches_original,
    }
    return artifact_sha256, archive_sha256, matches_original, original_artifact_sha256


def artifact_format_fields(relpath, is_receipt):
    """Describe what the currently-committed review_artifact bytes actually
    are, so a fresh clone never silently assumes it received the full
    original source just because an artifact_sha256 field is present.
    is_receipt must come from a real fact (artifact_sha256 != the known
    original full-source hash), not from filename pattern-matching alone --
    a compact excerpt is still a receipt even without a ".facts.json" name
    (e.g. the DNA pathogens Table 2 excerpt)."""
    if is_receipt:
        ext = Path(relpath.removesuffix(".gz")).suffix.lstrip(".")
        media = {"json": "application/json", "txt": "text/plain"}.get(ext, "application/json")
        return {"review_artifact_format": "curator_factual_receipt", "media_type": media}
    ext = Path(relpath).stem.rsplit(".", 1)[-1] if relpath.endswith(".gz") else Path(relpath).suffix.lstrip(".")
    media = {"xml": "application/xml", "html": "text/html", "txt": "text/plain", "json": "application/json", "csv": "text/csv", "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"}.get(ext, "application/octet-stream")
    return {"review_artifact_format": "original_source_artifact", "media_type": media}


def result_record(rid, name, source_id, evaluation_id, metric, printed_value, numeric_value,
                   unit, metric_direction, uncertainty, locator, notes=None, extra_attrs=None):
    attrs = {
        "printed_value": printed_value,
        "numeric_value": numeric_value,
        "metric": metric,
        "metric_direction": metric_direction,
        "unit": unit,
        "uncertainty": uncertainty,
        "source_locator": locator,
        "review": {
            "method": "automated_source_review",
            "reviewer": REVIEWER,
            "reviewed_at": REVIEWED_AT,
            "notes": notes or "Bounded transcription of a Codex-checked primary-source cell. No independent experimental reproduction or qualified human scientific review.",
        },
        "missing_metadata": {},
    }
    if extra_attrs:
        attrs.update(extra_attrs)
    return {
        "id": rid, "kind": "result", "name": name,
        "description": f"{name}; bounded additive AMP intake, Codex-checked primary value.",
        "status": "source_checked",
        "facets": {},
        "source_ids": [source_id],
        "links": [{"relation": "evaluation", "target_id": evaluation_id}],
        "attributes": attrs,
    }


# ---------------------------------------------------------------------------
# 1. Oncology-RNA group (issues 10, 11, 12): synthesize canonical records from
#    the nested cases[].entities shape.
# ---------------------------------------------------------------------------
def build_oncology_rna(records):
    path = GROUPS / "oncology-rna/candidates.json"
    d = json.loads(path.read_text())
    sources_by_id = {s["id"]: s for s in d["sources"]}
    mappings = []

    # Promote and hash-fix the three source records, unchanged otherwise.
    for src in d["sources"]:
        attrs = dict(src["attributes"])
        artifact_path = f"data/omics/amp-coverage-20261007/oncology-rna/artifacts/{Path(attrs['artifact_path']).name}"
        expected_sha256 = attrs["artifact_sha256"]
        artifact_sha256, archive_sha256, matches_original, original_artifact_sha256 = bind_artifact(artifact_path, expected_sha256)
        attrs["original_artifact_sha256"] = original_artifact_sha256
        attrs["artifact_sha256"] = artifact_sha256
        attrs["archive_sha256"] = archive_sha256
        attrs["review_artifact"] = artifact_path
        attrs["review_artifact_matches_original_artifact_sha256"] = matches_original
        attrs.update(artifact_format_fields(artifact_path, not matches_original))
        del attrs["artifact_path"]
        records.append({
            "id": src["id"], "kind": "source", "name": src["name"],
            "description": "Primary source for the AMP oncology-RNA bounded intake. Automated review, not independent reproduction.",
            "status": "source_checked",
            "facets": {}, "source_ids": [], "links": [],
            "attributes": attrs,
        })

    def add_protocol(pid, name, version, task_desc, scope_note):
        records.append({
            "id": pid, "kind": "protocol", "name": name,
            "description": f"{name}; bounded primary-source AMP candidate.",
            "status": "source_checked",
            "facets": {"areas": ["dna-genomes"], "method_types": ["conventional_pipeline"]},
            "source_ids": [case_source_id], "links": [],
            "attributes": {
                "version": version, "task": task_desc, "scope_note": scope_note,
                "missing_metadata": {},
            },
        })

    def add_dataset(did, name, entity):
        records.append({
            "id": did, "kind": "dataset", "name": name,
            "description": f"{name}; bounded primary-source AMP candidate.",
            "status": "source_checked",
            "facets": {"areas": ["dna-genomes"]},
            "source_ids": [case_source_id], "links": [],
            "attributes": {
                "version": entity.get("version"),
                "split": entity.get("split"),
                "population": entity.get("population"),
                "assay": entity.get("assay"),
                "accession": entity.get("accession"),
                "missing_metadata": {},
            },
        })

    def add_configuration(cid, name, version):
        records.append({
            "id": cid, "kind": "configuration", "name": name,
            "description": f"{name}; bounded primary-source AMP candidate.",
            "status": "source_checked",
            "facets": {"method_types": ["conventional_pipeline"]},
            "source_ids": [case_source_id], "links": [],
            "attributes": {
                "version": version, "reported_name": name,
                "foundation_model_eligible": False,
                "missing_metadata": {} if version else {
                    "version": "Exact caller release not extracted from the primary article; retain paper-era method identity, not a concrete current checkpoint.",
                },
            },
        })

    def add_evaluation(eid, name, protocol_id, dataset_id, config_id, evaluation_src, origin):
        records.append({
            "id": eid, "kind": "evaluation", "name": name,
            "description": f"{name}; bounded primary-source AMP candidate.",
            "status": "source_checked",
            "facets": {},
            "source_ids": [case_source_id],
            "links": [
                {"relation": "assessment", "target_id": protocol_id},
                {"relation": "system", "target_id": config_id},
                {"relation": "data", "target_id": dataset_id},
            ],
            "attributes": {
                "origin": origin,
                "protocol": evaluation_src.get("protocol"),
                "version": None,
                "comparison": evaluation_src.get("comparison", {}),
                "missing_metadata": evaluation_src.get("missing_metadata", {}),
            },
        })

    def add_results(prefix, config_name, eid, results, allowed_metrics=None):
        for r in results:
            if allowed_metrics is not None and r["metric"] not in allowed_metrics:
                continue
            rid = f"{prefix}-result-{slug(config_name)}-{slug(r['metric'])}"
            records.append(result_record(
                rid, f"{config_name} {r['metric']}", case_source_id, eid,
                r["metric"], r["printed_value"], r["numeric_value"], r["unit"],
                r["metric_direction"], r["uncertainty"], r["source_locator"],
                notes=r.get("notes"),
            ))

    # Origin convention (integration-review-corrections.md #6): a paper's own
    # introduced workflow is author_reported; a comparator model/caller that
    # paper merely evaluated is independent_paper. Never "reproduced".
    ORIGIN_BY_CONFIG = {
        "Lancet": "author_reported", "Strelka2": "independent_paper",
        "Arriba": "independent_paper", "STAR-Fusion": "independent_paper",
        "EnFusion 3 callers": "author_reported",
        "EnFusion 3 callers + filter + known fusion list": "author_reported",
        "FRASER (2021 article implementation)": "author_reported",
    }
    # issue 12's FRASER configuration only reports the known-event recovery
    # metrics in this bounded intake; full-cohort workload counts (12/7/10
    # outlier genes per sample) describe a different population and are
    # dropped here rather than attached to the 30-sample recovery evaluation.
    ALLOWED_METRICS_BY_ISSUE = {
        12: {"mean known pathogenic splicing-event recovery at 30 samples",
             "mean recovered known pathogenic events at 30 samples"},
    }

    for case in d["cases"]:
        case_source_id = case["source_id"]
        prefix = case["suggested_id_prefix"]
        ent = case["entities"]
        protocol_id = ent["protocol"]["proposed_id"]
        dataset_id = ent["dataset"]["proposed_id"]
        add_protocol(protocol_id, ent["protocol"]["name"], ent["protocol"].get("version"),
                     case["evaluation"].get("protocol"),
                     " ".join(case.get("limitations", [])))
        add_dataset(dataset_id, ent["dataset"]["name"], ent["dataset"])
        eval_ids = []
        for cfg in ent["configurations"]:
            cid = f"{prefix}-config-{slug(cfg['name'])}"
            eid = f"{prefix}-eval-{slug(cfg['name'])}"
            add_configuration(cid, cfg["name"], cfg.get("version"))
            origin = ORIGIN_BY_CONFIG.get(cfg["name"], "independent_paper")
            add_evaluation(eid, f"{cfg['name']} evaluation", protocol_id, dataset_id, cid, case["evaluation"], origin)
            add_results(prefix, cfg["name"], eid, cfg["results"], ALLOWED_METRICS_BY_ISSUE.get(case["issue"]))
            eval_ids.append(eid)
        case_limitations = case.get("limitations", [])
        if case["issue"] == 10:
            mappings.append(dict(
                id="use-case-mapping-amp-20261007-issue10-lancet-virtual-tumor",
                use_case_id="use-case-tumour-dna-somatic-variant-detection",
                protocol_id=protocol_id, evaluation_ids=eval_ids,
                endpoint="Virtual-tumour SNV and indel precision/recall/F1, true/false positive and false negative counts for Lancet and Strelka2 on a real-read synthetic tumour/normal pair",
                relevance="direct",
                rationale="Real-read virtual-tumour spike-in directly measures somatic SNV/indel calling precision and recall, the declared benchmark endpoint, under one sequencing/normal regime.",
                case_limitations=case_limitations,
            ))
        if case["issue"] == 11:
            mappings.append(dict(
                id="use-case-mapping-amp-20261007-issue11-enfusion-seraseq",
                use_case_id="use-case-tumour-rna-fusion-detection",
                protocol_id=protocol_id, evaluation_ids=eval_ids,
                endpoint="Synthetic 14-fusion Seraseq reference-standard sensitivity, precision and total/true fusion counts for Arriba, STAR-Fusion and EnFusion ensemble configurations (undiluted duplicate libraries)",
                relevance="direct",
                rationale="A synthetic reference standard with a known fusion set directly measures fusion-calling sensitivity and precision, the declared benchmark endpoint.",
                case_limitations=case_limitations,
            ))
        # Nested additional_evaluations (issue 11 NCH clinical ascertainment).
        for extra in (case.get("additional_evaluations") or []):
            aprefix = extra["protocol"]["proposed_id"].rsplit("-protocol-", 1)[0] + "-nch"
            eprotocol_id = extra["protocol"]["proposed_id"]
            edataset_id = extra["dataset"]["proposed_id"]
            add_protocol(eprotocol_id, extra["protocol"]["name"], extra["protocol"].get("version"),
                         extra.get("comparison", {}).get("population"),
                         " ".join(extra.get("limitations", [])))
            add_dataset(edataset_id, extra["dataset"]["name"], extra["dataset"])
            extra_eval_ids = []
            for cfg in extra["configurations"]:
                cid = f"{aprefix}-config-{slug(cfg['name'])}"
                eid = f"{aprefix}-eval-{slug(cfg['name'])}"
                add_configuration(cid, cfg["name"], cfg.get("version"))
                add_evaluation(eid, f"{cfg['name']} NCH clinical-ascertainment evaluation",
                                eprotocol_id, edataset_id, cid, extra, "independent_paper")
                add_results(aprefix, cfg["name"], eid, cfg["results"])
                extra_eval_ids.append(eid)
            mappings.append(dict(
                id="use-case-mapping-amp-20261007-issue11-enfusion-nch-clinical",
                use_case_id="use-case-tumour-rna-fusion-detection",
                protocol_id=eprotocol_id, evaluation_ids=extra_eval_ids,
                endpoint="Retrospective sensitivity among 67 ensemble-ascertained clinically relevant fusions in a 229-sample paediatric cancer/haematologic cohort, for STAR-Fusion and Arriba",
                relevance="direct",
                rationale="A real clinical cohort with ensemble-ascertained clinically relevant fusions directly measures fusion-detection sensitivity in a clinical population, the declared endpoint; the ascertainment denominator is not an independent exhaustive truth set.",
                case_limitations=extra.get("limitations", []),
            ))
        if case["issue"] == 12:
            mappings.append(dict(
                id="use-case-mapping-amp-20261007-issue12-fraser-kremer",
                use_case_id="use-case-patient-rna-splicing-validation",
                protocol_id=protocol_id, evaluation_ids=eval_ids,
                endpoint="Mean recovery of 13 known pathogenic splicing events at reduced cohort size (30 of 119 patient RNA samples) using FRASER on patient skin-fibroblast RNA",
                relevance="direct",
                rationale="Direct patient-RNA evidence measuring recovery of known pathogenic splicing events bears on the declared decision, scoped narrowly to known-event recovery rather than diagnostic yield in unknown cases.",
                case_limitations=case_limitations,
            ))
    return mappings


# ---------------------------------------------------------------------------
# 2 & 3. pathogens-fragmentomics (issues 13,14,15) and
#         methylation-cnv-operations (issues 16,17,18): their candidates.json
#         already hold canonical RecordEntry-shaped records; promote status,
#         fix hashes/paths, and reuse the records almost verbatim.
# ---------------------------------------------------------------------------
GROUP_ARTIFACT_DIRS = {
    "pathogens-fragmentomics": "",          # artifacts live at the group root
    "methylation-cnv-operations": "artifacts/",
}


def fix_canonical_text(rec, group):
    """Correct wording errors identified by independent review in the
    canonical copy only; the frozen research-group candidates.json is never
    mutated. Per integration-review-corrections.md #1: DELFI's classifier
    inputs are GC-corrected TOTAL and SHORT fragment coverage (not a
    short/long ratio)."""
    if group == "pathogens-fragmentomics" and rec["id"].startswith("amp-20261007-ctdna-fragmentomics-"):
        rec = json.loads(json.dumps(rec))  # deep copy
        for key in ("workflow", "reported_name"):
            if key in rec["attributes"] and rec["attributes"][key]:
                rec["attributes"][key] = rec["attributes"][key].replace(
                    "GC-corrected short/long fragment coverage",
                    "GC-corrected total and short fragment coverage",
                )
    return rec


def fix_source_record(rec, group):
    attrs = dict(rec["attributes"])
    review_artifact = attrs.get("review_artifact")
    if review_artifact:
        name = Path(review_artifact).name
        relpath = f"data/omics/amp-coverage-20261007/{group}/{GROUP_ARTIFACT_DIRS[group]}{name}"
        # dna-pathogens-source already distinguishes artifact_sha256 (a compact
        # excerpt) from a pre-existing original_artifact_sha256 (the full PDF,
        # not locally retrievable); never clobber that distinct field. For
        # everything else, prefer the explicit archive-transformation.json
        # registry entry over a same-as-declared assumption.
        known_original = attrs.get("original_artifact_sha256")
        artifact_sha256, archive_sha256, matches_original, original_artifact_sha256 = bind_artifact(
            relpath, attrs["artifact_sha256"], known_original_sha256=known_original)
        attrs["original_artifact_sha256"] = original_artifact_sha256
        attrs["artifact_sha256"] = artifact_sha256
        attrs["archive_sha256"] = archive_sha256
        attrs["review_artifact"] = relpath
        attrs["review_artifact_matches_original_artifact_sha256"] = matches_original
        # The research/archive worker may already have recorded the exact
        # format/media type on the frozen record; never override an
        # authoritative value with our own heuristic.
        for key, value in artifact_format_fields(relpath, not matches_original).items():
            attrs.setdefault(key, value)
    rec = dict(rec)
    rec["status"] = "source_checked"
    rec["attributes"] = attrs
    return rec


def build_canonical_group(records, group, case_relevance, mapping_prefix, rationale_by_issue, endpoint_by_issue):
    path = GROUPS / group / "candidates.json"
    d = json.loads(path.read_text())
    recs = d["records"]
    cases = d["cases"]
    mappings = []
    for rec in recs:
        rec = dict(rec)
        if rec["kind"] == "source":
            rec = fix_source_record(rec, group)
        else:
            rec["status"] = "source_checked"
        rec = fix_canonical_text(rec, group)
        records.append(rec)
    for case in cases:
        issue = case["issue"]
        eval_ids = case.get("evaluation_ids") or [case.get("key") and f"amp-20261007-{case['key']}-evaluation"]
        eval_ids = [e for e in eval_ids if e]
        # Resolve the protocol each evaluation belongs to.
        proto_lookup = {r["id"]: r for r in recs if r["kind"] == "evaluation"}
        protocol_id = None
        for eid in eval_ids:
            ev = proto_lookup.get(eid)
            if ev:
                for link in ev["links"]:
                    if link["relation"] == "protocol":
                        protocol_id = link["target_id"]
        if not protocol_id:
            # pathogens-fragmentomics shape: one record set per case, protocol
            # is the sibling id for this case's key.
            key = case["key"]
            protocol_id = f"amp-20261007-{key}-protocol"
        mappings.append(dict(
            id=f"{mapping_prefix}-issue{issue}",
            use_case_id=NEW_USE_CASE_BY_ISSUE[issue],
            protocol_id=protocol_id,
            evaluation_ids=eval_ids,
            endpoint=endpoint_by_issue[issue],
            relevance=case_relevance[issue],
            rationale=rationale_by_issue[issue],
            case_limitations=case.get("limits") or case.get("gaps") or [],
        ))
    return mappings


NEW_USE_CASE_BY_ISSUE = {
    10: "use-case-tumour-dna-somatic-variant-detection",
    11: "use-case-tumour-rna-fusion-detection",
    12: "use-case-patient-rna-splicing-validation",
    13: "use-case-diagnostic-dna-pathogen-identification",
    14: "use-case-diagnostic-rna-pathogen-detection",
    15: "use-case-plasma-ctdna-fragmentomics",
    16: "use-case-plasma-ctdna-methylation",
    17: "use-case-cnv-detection-characterisation",
    18: "use-case-diagnostic-genomics-model-execution",
}


def build_pathogens_fragmentomics(records):
    return build_canonical_group(
        records, "pathogens-fragmentomics",
        case_relevance={13: "proxy", 14: "proxy", 15: "proxy"},
        mapping_prefix="use-case-mapping-amp-20261007",
        rationale_by_issue={
            13: "Positive percent agreement against initial blood culture is a proxy for sensitivity against all true infections, since initial blood culture does not identify every infection.",
            14: "Sensitivity against original clinical RVP testing (RNA extraction, DNase treatment, cDNA synthesis; mixed respiratory-virus target panel including transcriptionally detected adenovirus) is a proxy for the declared RNA-pathogen diagnostic-accuracy decision: the specimen prep is an RNA workflow, not a mixed DNA/RNA sample-prep comparison, and this is not an RNA-virus-only subgroup score. The conflicting composite PPA figure (98.7%, 110.5/113) is excluded.",
            15: "A repeated 10-fold cross-validation (10 repeats) on one assembled cohort is a proxy for the broader plasma ctDNA fragmentomics detection decision and for this explicitly assessed assay endpoint; it is internal cross-validation, not a separately held-out validation cohort and not prospective screening validation.",
        },
        endpoint_by_issue={
            13: "Positive percent agreement with initial blood culture for plasma microbial cfDNA sequencing in a prospective sepsis-alert cohort (59/63 initial-blood-culture-positive subset)",
            14: "Sensitivity against original clinical respiratory-virus-panel testing (103/110, 93.6%) for RNA mNGS on a residual-sample pre-DTCA mixed respiratory-target cohort, adenovirus transcripts included",
            15: "Sensitivity (73%, 152/208) at a reported 98% specificity for plasma cfDNA fragmentomics-based cancer detection, repeated 10-fold cross-validation (10 repeats)",
        },
    )


def build_methylation_cnv(records):
    return build_canonical_group(
        records, "methylation-cnv-operations",
        case_relevance={16: "direct", 17: "direct", 18: "proxy"},
        mapping_prefix="use-case-mapping-amp-20261007",
        rationale_by_issue={
            16: "A repeated-split cross-validated sensitivity/specificity figure at a declared specificity directly measures plasma cfDNA methylation cancer-detection performance, the declared endpoint.",
            17: "F-score for 1-5 kb deletion detection against a GIAB truth set directly measures the declared CNV-detection endpoint; it does not cover visualisation usability.",
            18: "A conventional variant-calling pipeline's measured single-sample runtime is a proxy baseline for the throughput/resource constraints a foundation-model execution workflow would need to meet; it is not itself a model-execution benchmark.",
        },
        endpoint_by_issue={
            16: "All-stage cancer-detection sensitivity (95% CI) at a declared specificity for cfMethyl-Seq on a repeated random 25% test split",
            17: "F-score for 1-5 kb deletion detection (DRAGEN 4.2 CNV/SV benchmarking, HG002) against the GIAB SV truth set",
            18: "Total single-sample wall-clock runtime (seconds) for DRAGEN 4.2 Phase 4 processing of HG002, by hardware configuration",
        },
    )


# ---------------------------------------------------------------------------
# 4. Feng expansion (issue #19): reuse the existing checked source unchanged;
#    add Table1 Acceptor/Donor, Table2 Arabidopsis TATA/NonTATA, Table5
#    AUC+Cohen's d and Table6 AUC+Cohen's d as new source-reported records.
# ---------------------------------------------------------------------------
FENG_SOURCE_ID = "evidence-expansion-dna-foundation-models-2025-5d8ca9bc"

# Per-model metadata for the Table5/Table6 (variant/QTL) alternate-minus-
# reference task family. foundation=False marks Sei/Enformer/AlphaGenome,
# which the source itself prints with an asterisk as non-DNA-foundation
# specialised genomic comparators (integration-review-corrections.md and
# feng-integration-review.json, issue "Source comparator role is not
# preserved"). window is the GENERATED/scored population a model is drawn
# from: "short" (6,000 bp generated window, 22,239 pathogenic/17,398 common
# SNPs) or "long" (196,608 bp generated window, 22,222/17,374; the chromosome-
# boundary-filtered population, per feng-followup-review.json). A model's
# actual_input_bp is the literal DNA crop it consumes from that generated
# window (may be smaller than the window itself -- e.g. AlphaGenome crops
# the central 131,072 bp from the long window); output_aggregation_bp is a
# separate, distinct concept (only AlphaGenome: output tracks are averaged
# over the central 2,048 bp of its OUTPUT, not a smaller DNA input crop).
VARIANT_MODELS = {
    "Sei, hidden states*": {"foundation": False, "window": "short", "actual_input_bp": 4096},
    "Sei, output tracks*": {"foundation": False, "window": "short", "actual_input_bp": 4096},
    "Enformer, hidden states*": {"foundation": False, "window": "long", "actual_input_bp": None},
    "Enformer, output tracks*": {"foundation": False, "window": "long", "actual_input_bp": None},
    "DNABERT-2": {"foundation": True, "window": "short", "actual_input_bp": None},
    "NT-v2": {"foundation": True, "window": "short", "actual_input_bp": None},
    "HyenaDNA": {"foundation": True, "window": "short", "actual_input_bp": None},
    "HyenaDNA-450K, long sequence": {"foundation": True, "window": "long", "actual_input_bp": None},
    "Caduceus-Ph": {"foundation": True, "window": "short", "actual_input_bp": None},
    "Caduceus-Ph, long sequence": {"foundation": True, "window": "long", "actual_input_bp": 131072},
    "GROVER": {"foundation": True, "window": "short", "actual_input_bp": 2048},
}
# AlphaGenome is QTL-only (not in Table 5) but is drawn from the same long
# (196,608 bp) generated/chromosome-boundary-filtered population as Enformer
# and the long-sequence HyenaDNA-450K/Caduceus-Ph rows (Sec25: "providing it
# the central 131072 nucleotides" is an input crop of that same long window,
# not a third separate population).
QTL_ONLY_MODELS = {
    "AlphaGenome, output tracks*": {"foundation": False, "window": "long", "actual_input_bp": 131072, "output_aggregation_bp": 2048},
}
SEQ_MODELS = ["DNABERT-2", "NT-v2", "HyenaDNA", "Caduceus-Ph", "GROVER"]  # Tables 1-2 only

GENERATED_WINDOW_BP = {"short": 6000, "long": 196608}
WINDOW_LENGTH_NOTE = {
    "short": f"Short generated/chromosome-boundary-filtered window: {GENERATED_WINDOW_BP['short']:,} bp.",
    "long": (f"Long generated/chromosome-boundary-filtered window: {GENERATED_WINDOW_BP['long']:,} bp. "
             "A model's actual_input_bp may crop a smaller region from this generated window (e.g. AlphaGenome "
             "and long-sequence Caduceus-Ph each crop the central 131,072 bp); exact realised per-model scored "
             "counts after that crop are unextracted, not asserted as zero."),
}
# SNP counts are specific to the Table 5 pathogenic/common SNP task and must
# never be copied into a QTL (Table 6) dataset's population text.
WINDOW_POPULATION = {
    "short": f"{WINDOW_LENGTH_NOTE['short']} 22,239 pathogenic/17,398 common SNPs.",
    "long": f"{WINDOW_LENGTH_NOTE['long']} 22,222/17,374 pathogenic/common SNPs.",
}
OUTER_SPLIT = ("Three disjoint outer chromosome test groups (3/6/9/12/16/18/19/21; 2/5/11/14/17/20/22/X; "
               "1/4/7/8/10/13/15), each held out in turn with fourfold inner-chromosome cross-validation "
               "for hyperparameter tuning.")
QTL_PRE_FILTER_COUNTS = {"eQTL": 1896, "sQTL": 540, "paQTL": 142, "ipaQTL": 116}
QTL_DATASET_SOURCE_NOTE = ("Borzoi-derived GTEx v8 whole-blood putative causal variants paired with matched "
                            "noncausal variants by distance to functional site/gene expression.")


def _window_dataset_id(namespace, window):
    return f"amp-feng-20261007-dataset-{namespace}-{window}"


def _add_window_dataset_once(records, seen, namespace, window, task_label, qtl_type=None):
    """namespace is "variant" for the Table 5 pathogenic/common SNP task, or
    "qtl-<type>" for one Table 6 QTL task. QTL datasets must never inherit
    the SNP task's 22,239/17,398 (short) or 22,222/17,374 (long) counts --
    they carry only that QTL type's own pre-window-filter positive count."""
    did = _window_dataset_id(namespace, window)
    if did in seen:
        return did
    seen.add(did)
    is_qtl = namespace.startswith("qtl")
    if is_qtl:
        qtl_note = (f"{QTL_DATASET_SOURCE_NOTE} {qtl_type} pre-window-filter positive count: "
                    f"{QTL_PRE_FILTER_COUNTS[qtl_type]} (not an established per-model scored denominator; "
                    "post-filter counts are unreported, recorded as null, not zero; this is a different "
                    "population from the Table 5 pathogenic/common SNP short/long counts, never copied here).")
        population = qtl_note + " " + WINDOW_LENGTH_NOTE[window]
    else:
        population = WINDOW_POPULATION[window]
    records.append({
        "id": did, "kind": "dataset", "name": f"Feng {task_label} {window}-window dataset",
        "description": f"Feng {task_label} {window}-window scored population; Feng et al. 2025.",
        "status": "source_checked", "facets": {"areas": ["dna-genomes"]},
        "source_ids": [FENG_SOURCE_ID], "links": [],
        "attributes": {
            "version": None, "split": OUTER_SPLIT, "population": population,
            "missing_metadata": {"split": "Exact per-fold scored counts and post-window-filter denominators are unreported; not asserted as zero."},
        },
    })
    return did


def feng_add_configuration(records, cid, label, task_label, foundation_eligible, actual_input_bp=None, output_aggregation_bp=None):
    scope = f"{label} ({task_label}); Feng et al. 2025 source-reported, task-scoped configuration."
    if not foundation_eligible:
        scope += (" Printed in the source with an asterisk as a non-DNA-foundation specialised genomic "
                   "comparator, not one of the paper's own DNA foundation models.")
    if actual_input_bp:
        scope += f" Actual DNA input consumed by the model: {actual_input_bp} bp (a crop of the dataset's generated window where smaller)."
    if output_aggregation_bp:
        scope += f" Output tracks averaged over the central {output_aggregation_bp} bp of the model's OUTPUT (not a smaller DNA input crop)."
    records.append({
        "id": cid, "kind": "configuration", "name": f"{label} ({task_label})",
        "description": scope,
        "status": "source_checked",
        "facets": {"method_types": ["foundation_model"] if foundation_eligible else ["conventional_pipeline"]},
        "source_ids": [FENG_SOURCE_ID], "links": [],
        "attributes": {
            "version": None, "reported_name": label,
            "foundation_model_eligible": foundation_eligible,
            "task": task_label,
            "head": "Supervised random forest fitted separately for this task",
            "head_revision": None,
            "representation": ("Alternate-minus-reference frozen representation" if "discrimination" in task_label or "SNP" in task_label else "Frozen last-layer mean token embeddings"),
            "actual_input_bp": actual_input_bp,
            "output_aggregation_bp": output_aggregation_bp,
            "missing_metadata": {
                "version": "Printed model name and input representation only; immutable checkpoint/head revision is unreported in the inspected primary text.",
            },
        },
    })


def _seq_task(records, mappings, table_rows, task_key, task_label, locator_label, use_case_id, mapping_id, rationale,
              limitations, dataset_population, dataset_split_note):
    """Shared builder for Table 1 (Acceptor/Donor) and Table 2 (TATA/NonTATA):
    each row is its own task with its own dataset/protocol and task-scoped
    per-model configurations/evaluations (not shared across tasks). Splice
    (Table 1) is the DNABERT-2/NT benchmark; Arabidopsis promoter (Table 2)
    is the separate ref34 multispecies promoter benchmark (Sec16) -- the two
    must not share one dataset provenance string."""
    protocol_id = f"amp-feng-20261007-protocol-{task_key}"
    dataset_id = f"amp-feng-20261007-dataset-{task_key}"
    records.append({
        "id": protocol_id, "kind": "protocol", "name": f"Feng {task_label} sequence classification",
        "description": f"{locator_label} sequence classification; Feng et al. 2025 source-reported protocol.",
        "status": "source_checked", "facets": {"areas": ["dna-genomes"]},
        "source_ids": [FENG_SOURCE_ID], "links": [],
        "attributes": {"version": locator_label, "task": f"{task_label} sequence classification (AUC)",
                       "scope_note": "Frozen last-layer mean token embeddings from each pretrained model, scored by a supervised random forest classifier fitted for this exact task (not label-free prediction). " + dataset_split_note + " Exact per-task split sizes/counts (identified in Supplementary Data 6, not inspected by this intake) and immutable checkpoint/head revisions are unextracted from the inspected main text; not asserted absent from the article.",
                       "missing_metadata": {}},
    })
    records.append({
        "id": dataset_id, "kind": "dataset", "name": f"Feng {task_label} dataset",
        "description": f"{dataset_population}; Feng et al. 2025.",
        "status": "source_checked", "facets": {"areas": ["dna-genomes"]},
        "source_ids": [FENG_SOURCE_ID], "links": [],
        "attributes": {"version": None, "split": dataset_split_note,
                       "population": dataset_population,
                       "missing_metadata": {"split": "Exact per-task split sizes/counts are unextracted from the inspected main text (Supplementary Data 6 is identified but not inspected by this intake); not asserted absent from the article."}},
    })
    eval_ids = []
    for m in SEQ_MODELS:
        cid = f"amp-feng-20261007-config-{task_key}-{slug(m)}"
        eid = f"amp-feng-20261007-eval-{task_key}-{slug(m)}"
        feng_add_configuration(records, cid, m, f"{task_label} classification", True)
        records.append({
            "id": eid, "kind": "evaluation", "name": f"{m} {task_label} evaluation",
            "description": f"{m} {task_label} sequence-classification evaluation; Feng et al. 2025.",
            "status": "source_checked", "facets": {},
            "source_ids": [FENG_SOURCE_ID],
            "links": [
                {"relation": "assessment", "target_id": protocol_id},
                {"relation": "system", "target_id": cid},
                {"relation": "data", "target_id": dataset_id},
            ],
            "attributes": {"origin": "independent_paper",
                           "protocol": f"{locator_label}, frozen embeddings + task-specific random forest classifier",
                           "version": None,
                           "comparison": {"protocol_id": protocol_id, "dataset_version": None,
                                          "split": dataset_split_note,
                                          "population": dataset_population,
                                          "inputs": f"DNA sequence windows for {task_label} classification",
                                          "adaptation": "Frozen pretrained representation plus a supervised random-forest classifier head fitted for this exact task",
                                          "metric_implementation": None,
                                          "aggregation": None, "budget": None},
                           "missing_metadata": {"metric_implementation": "Exact scoring implementation beyond AUC is unreported.", "budget": "Not extracted; no execution"}},
        })
        row = next(r for r in table_rows if r["cells"][0] == task_label)
        idx = row["headers"].index(m)
        val = row["cells"][idx]
        rid = f"amp-feng-20261007-result-{task_key}-{slug(m)}-auc"
        records.append(result_record(rid, f"{m} {task_label} AUC", FENG_SOURCE_ID, eid,
                                      f"{task_label} AUC", val, val.replace("−", "-"), "AUC", "higher", None,
                                      f"{locator_label}, {task_label} row, {m} column (deterministic XML extraction; see data/omics/amp-coverage-20261007/feng/selected-rows.json)"))
        eval_ids.append(eid)
    mappings.append(dict(
        id=mapping_id, use_case_id=use_case_id, protocol_id=protocol_id, evaluation_ids=eval_ids,
        endpoint=f"{task_label} sequence-classification AUC for five DNA foundation-model embeddings",
        relevance="proxy", rationale=rationale, case_limitations=limitations,
    ))


# Pinned against an explicit reviewed-input registry, not computed by
# self-hashing the file at build time (that would silently bless any later
# edit to the deterministic extraction/review-notes inputs this generator
# depends on). fulltext.xml.gz's hash matches the reused source record's own
# artifact_sha256 (feng-integration-review.json); the other two were
# reviewed in this pass (feng-followup-review.json) and pinned here.
FENG_REVIEWED_INPUT_SHA256 = {
    "data/omics/amp-coverage-20261007/feng/fulltext.xml.gz": "5d8ca9bcf88cc1b38ad667906a2e4699b1aefa6d31c6f49259784930353f3202",
    "data/omics/amp-coverage-20261007/feng/selected-rows.json": "681c64b15120f459b7f35dbfa92f4cebc7f00af722cdec912b2c55c406069737",
    "data/omics/amp-coverage-20261007/feng/review-notes.md": "d33c8ce35effc91fea5fff6d4670420032294ccb541479c2d947ef11e5b37753",
}


def _bind_feng_inputs():
    """Reuse of evidence-expansion-dna-foundation-models-2025-5d8ca9bc is
    unchanged (no new source record), but the fresh XML, the deterministic
    selected-rows extraction and the review notes this generator reads are
    still bound into this lane's artifact maps for loader verification,
    against the pinned reviewed hashes above (raises if any has drifted)."""
    for relpath, expected in FENG_REVIEWED_INPUT_SHA256.items():
        bind_artifact(relpath, expected)


def build_feng_expansion(records):
    _bind_feng_inputs()
    sel = json.loads((GROUPS / "feng/selected-rows.json").read_text())
    tab1 = [r for r in sel if r["table_id"] == "Tab1"]
    tab2 = [r for r in sel if r["table_id"] == "Tab2"]
    tab5 = [r for r in sel if r["table_id"] == "Tab5"]
    tab6 = [r for r in sel if r["table_id"] == "Tab6"]
    mappings = []

    splice_split_note = "Original predefined split retained where clearly defined; otherwise a random 70:30 train/test split, tuned by fivefold cross-validation. DNABERT-2/NT benchmark datasets are reshuffled unless an explicit source exception applies."
    promoter_split_note = "Original predefined split retained where clearly defined; otherwise a random 70:30 train/test split, tuned by fivefold cross-validation. This ref34 multispecies promoter benchmark's own partitioning is not asserted to follow the DNABERT-2/NT reshuffle rule absent explicit confirmation."

    # --- Table 1: Acceptor and Donor are two separate classification tasks --
    # Splice acceptor/donor is the DNABERT-2/NT benchmark (Sec16/Sec22).
    _seq_task(records, mappings, tab1, "splice-acceptor", "Acceptor", "Table 1",
              "use-case-splicing-follow-up", "use-case-mapping-amp-20261007-feng-splice-acceptor",
              "Sequence-label splice-acceptor classification AUC is a proxy for splicing-effect prioritisation; it is a different endpoint from MFASS exon-recognition reporter-assay ranking and must not be pooled with it or with the donor task.",
              ["Sequence-label acceptor classification is not a minigene reporter exon-inclusion endpoint and is not patient-RNA splicing validation.", "Exact per-task split sizes/counts are unextracted from the inspected main text (Supplementary Data 6 is identified but not inspected).", "No independent reproduction or qualified human scientific review."],
              "DNABERT-2/NT-v2 benchmark Acceptor splice-site sequence set", splice_split_note)
    _seq_task(records, mappings, tab1, "splice-donor", "Donor", "Table 1",
              "use-case-splicing-follow-up", "use-case-mapping-amp-20261007-feng-splice-donor",
              "Sequence-label splice-donor classification AUC is a proxy for splicing-effect prioritisation; it is a separate task from acceptor classification and from MFASS exon-recognition reporter-assay ranking, and must not be pooled with either.",
              ["Sequence-label donor classification is not a minigene reporter exon-inclusion endpoint and is not patient-RNA splicing validation.", "Exact per-task split sizes/counts are unextracted from the inspected main text (Supplementary Data 6 is identified but not inspected).", "No independent reproduction or qualified human scientific review."],
              "DNABERT-2/NT-v2 benchmark Donor splice-site sequence set", splice_split_note)

    # --- Table 2: Arabidopsis promoter TATA and NonTATA are two separate
    #     tasks, drawn from the SEPARATE ref34 multispecies promoter
    #     benchmark (Sec16), not the DNABERT-2/NT benchmark used by Table 1.
    _seq_task(records, mappings, tab2, "promoter-tata", "Promoter Arabidopsis TATA", "Table 2",
              "use-case-plant-promoter-reporters", "use-case-mapping-amp-20261007-feng-promoter-tata",
              "Sequence-label TATA promoter classification AUC is a proxy for reporter-measured promoter strength; it is a separate task from NonTATA classification and does not itself measure reporter expression.",
              ["Sequence classification accuracy is not a reporter expression measurement.", "Exact per-task split sizes/counts are unextracted from the inspected main text (Supplementary Data 6 is identified but not inspected).", "No independent reproduction or qualified human scientific review."],
              "Arabidopsis TATA promoter sequences from the ref34 multispecies promoter benchmark (Sec16): positives are experimentally established plant promoters; negatives are computationally derived non-promoter regions matched for high sequence similarity.",
              promoter_split_note)
    _seq_task(records, mappings, tab2, "promoter-nontata", "Promoter Arabidopsis NonTATA", "Table 2",
              "use-case-plant-promoter-reporters", "use-case-mapping-amp-20261007-feng-promoter-nontata",
              "Sequence-label NonTATA promoter classification AUC is a proxy for reporter-measured promoter strength; it is a separate task from TATA classification and does not itself measure reporter expression.",
              ["Sequence classification accuracy is not a reporter expression measurement.", "Exact per-task split sizes/counts are unextracted from the inspected main text (Supplementary Data 6 is identified but not inspected).", "No independent reproduction or qualified human scientific review."],
              "Arabidopsis NonTATA promoter sequences from the ref34 multispecies promoter benchmark (Sec16): positives are experimentally established plant promoters; negatives are computationally derived non-promoter regions matched for high sequence similarity.",
              promoter_split_note)

    # --- Table 5: pathogenic vs common SNP classification (single task; short
    #     and long are separate scored populations, assigned per model) ------
    protocol_variant = "amp-feng-20261007-protocol-pathogenic-common-variant-classification"
    records.append({
        "id": protocol_variant, "kind": "protocol", "name": "Feng pathogenic-versus-common SNP classification",
        "description": "Table 5 pathogenic-versus-common SNP classification; Feng et al. 2025 source-reported protocol.",
        "status": "source_checked", "facets": {"areas": ["dna-genomes"]},
        "source_ids": [FENG_SOURCE_ID], "links": [],
        "attributes": {"version": "Table 5", "task": "Pathogenic-versus-common SNP discrimination (AUC, Cohen's d)",
                       "scope_note": "Alternate-minus-reference embedding representations scored by a supervised random forest classifier. " + OUTER_SPLIT + " Short and long are separate scored populations by window-size boundary exclusion, never pooled; see each configuration/dataset for its exact window assignment. Exact immutable checkpoints are unreported; configurations retain the printed model name and input representation only.",
                       "missing_metadata": {}},
    })
    seen_datasets = set()
    eval_ids = []
    for row in tab5:
        m = row["cells"][0]
        meta = VARIANT_MODELS[m]
        did = _add_window_dataset_once(records, seen_datasets, "variant", meta["window"], "pathogenic/common SNP")
        cid = f"amp-feng-20261007-config-variant-{slug(m)}"
        eid = f"amp-feng-20261007-eval-variant-{slug(m)}"
        feng_add_configuration(records, cid, m, "pathogenic/common SNP classification", meta["foundation"],
                                actual_input_bp=meta["actual_input_bp"])
        auc, cohend = row["cells"][1], row["cells"][2]
        records.append({
            "id": eid, "kind": "evaluation", "name": f"{m} pathogenic/common SNP evaluation",
            "description": f"{m} pathogenic/common SNP classification evaluation ({meta['window']} window); Feng et al. 2025.",
            "status": "source_checked", "facets": {},
            "source_ids": [FENG_SOURCE_ID],
            "links": [
                {"relation": "assessment", "target_id": protocol_variant},
                {"relation": "system", "target_id": cid},
                {"relation": "data", "target_id": did},
            ],
            "attributes": {"origin": "independent_paper", "protocol": "Table 5, frozen embeddings + random forest classifier",
                           "version": None,
                           "comparison": {"protocol_id": protocol_variant, "dataset_version": None,
                                          "split": OUTER_SPLIT,
                                          "population": WINDOW_POPULATION[meta["window"]],
                                          "inputs": f"Alternate-minus-reference embedding representation around each SNP ({meta['window']} window)",
                                          "adaptation": "Frozen pretrained representation plus a supervised random-forest classifier head fitted for this task",
                                          "metric_implementation": None,
                                          "aggregation": "Mean of AUC/Cohen's d across the three outer chromosome test folds",
                                          "budget": None},
                           "missing_metadata": {"budget": "Not extracted; no execution"}},
        })
        records.append(result_record(f"amp-feng-20261007-result-variant-{slug(m)}-auc", f"{m} pathogenic/common SNP AUC", FENG_SOURCE_ID, eid,
                                      "pathogenic/common SNP AUC", auc, auc.replace("−", "-"), "AUC", "higher", None,
                                      f"Table 5, {m} row, AUC column (deterministic XML extraction)"))
        records.append(result_record(f"amp-feng-20261007-result-variant-{slug(m)}-cohend", f"{m} pathogenic/common SNP Cohen's d", FENG_SOURCE_ID, eid,
                                      "pathogenic/common SNP Cohen's d", cohend, cohend.replace("−", "-"), "Cohen's d", "unknown", None,
                                      f"Table 5, {m} row, Cohen's d column (deterministic XML extraction). Signed effect size; the source does not state a universal desirable sign/direction, so direction is recorded as unknown rather than assumed higher-is-better."))
        eval_ids.append(eid)
    mappings.append(dict(
        id="use-case-mapping-amp-20261007-feng-pathogenic-common-variant",
        use_case_id="use-case-rare-disease-candidate-ranking",
        protocol_id=protocol_variant, evaluation_ids=eval_ids,
        endpoint="Pathogenic-versus-common SNP discrimination (AUC, Cohen's d) for eleven DNA foundation-model/genomic-comparator configurations, across separate short- and long-window scored populations",
        relevance="proxy",
        rationale="Genome-wide pathogenic-versus-common SNP discrimination is a proxy for rare-disease candidate variant ranking; it is not disease-specific (no BRCA subgroup claim) and is not a complete clinical classification.",
        case_limitations=["No disease-specific (e.g. BRCA) subgroup claim is supported by this table.", "Short-window and long-window populations are separate and must not be pooled; each configuration/dataset records its exact assignment.", "Sei, Enformer (hidden/output tracks) are non-DNA-foundation specialised genomic comparators per the source's own asterisk notation, not DNA foundation models.", "No independent reproduction or qualified human scientific review."],
    ))

    # --- Table 6: four separate QTL discrimination tasks (eQTL/sQTL/paQTL/
    #     ipaQTL), each with its own protocol and per-model evaluations -------
    qtl_types = ["eQTL", "sQTL", "paQTL", "ipaQTL"]
    rows_by_model_metric = {}
    current_metric = None
    for row in tab6:
        cells = row["cells"]
        if len(cells) == 6:
            current_metric, model = cells[0], cells[1]
            values = cells[2:]
        else:
            model = cells[0]
            values = cells[1:]
        rows_by_model_metric.setdefault(model, {})[current_metric] = dict(zip(qtl_types, values))
    all_qtl_models = list(VARIANT_MODELS.keys()) + list(QTL_ONLY_MODELS.keys())
    qtl_eval_ids_by_type = {t: [] for t in qtl_types}
    for qtl_type in qtl_types:
        protocol_qtl = f"amp-feng-20261007-protocol-qtl-{slug(qtl_type)}"
        records.append({
            "id": protocol_qtl, "kind": "protocol", "name": f"Feng {qtl_type} discrimination",
            "description": f"Table 6 {qtl_type} causal-versus-noncausal variant discrimination; Feng et al. 2025 source-reported protocol.",
            "status": "source_checked", "facets": {"areas": ["dna-genomes"]},
            "source_ids": [FENG_SOURCE_ID], "links": [],
            "attributes": {"version": "Table 6", "task": f"{qtl_type} causal-vs-noncausal variant discrimination (AUC, Cohen's d)",
                           "scope_note": ("Alternate-minus-reference embedding representations scored by a supervised random forest classifier. " + OUTER_SPLIT +
                                          f" {QTL_DATASET_SOURCE_NOTE} Pre-window-filter positive count for {qtl_type}: {QTL_PRE_FILTER_COUNTS[qtl_type]} "
                                          "(not an established per-model scored denominator; post-filter counts are unreported and recorded as null, not zero). "
                                          "Short and long generated-window datasets are separate scored populations, never pooled. AlphaGenome uses the long dataset with a central input crop and separate output averaging."),
                           "missing_metadata": {}},
        })
        seen_qtl_datasets = set()
        for m in all_qtl_models:
            meta = VARIANT_MODELS.get(m) or QTL_ONLY_MODELS[m]
            did = _add_window_dataset_once(records, seen_qtl_datasets, f"qtl-{slug(qtl_type)}", meta["window"], f"{qtl_type} discrimination", qtl_type=qtl_type)
            cid = f"amp-feng-20261007-config-qtl-{slug(qtl_type)}-{slug(m)}"
            eid = f"amp-feng-20261007-eval-qtl-{slug(qtl_type)}-{slug(m)}"
            feng_add_configuration(records, cid, m, f"{qtl_type} discrimination", meta["foundation"],
                                    actual_input_bp=meta["actual_input_bp"], output_aggregation_bp=meta.get("output_aggregation_bp"))
            records.append({
                "id": eid, "kind": "evaluation", "name": f"{m} {qtl_type} discrimination evaluation",
                "description": f"{m} {qtl_type} discrimination evaluation ({meta['window']} window); Feng et al. 2025.",
                "status": "source_checked", "facets": {},
                "source_ids": [FENG_SOURCE_ID],
                "links": [
                    {"relation": "assessment", "target_id": protocol_qtl},
                    {"relation": "system", "target_id": cid},
                    {"relation": "data", "target_id": did},
                ],
                "attributes": {"origin": "independent_paper",
                               "protocol": f"Table 6, {qtl_type} column, frozen embeddings + random forest classifier",
                               "version": None,
                               "comparison": {"protocol_id": protocol_qtl, "dataset_version": None,
                                              "split": OUTER_SPLIT,
                                              "population": f"{QTL_DATASET_SOURCE_NOTE} {qtl_type} pre-window-filter positives: {QTL_PRE_FILTER_COUNTS[qtl_type]}.",
                                              "inputs": f"Alternate-minus-reference embedding representation around each {qtl_type} variant ({meta['window']} window)",
                                              "adaptation": "Frozen pretrained representation plus a supervised random-forest classifier head fitted for this exact QTL task",
                                              "metric_implementation": None,
                                              "aggregation": "Mean of AUC/Cohen's d across the three outer chromosome test folds",
                                              "budget": None},
                               "missing_metadata": {"budget": "Not extracted; no execution"}},
            })
            metrics = rows_by_model_metric.get(m, {})
            for metric_name, by_qtl in metrics.items():
                if qtl_type not in by_qtl:
                    continue
                val = by_qtl[qtl_type]
                is_auc = metric_name == "AUC"
                direction = "higher" if is_auc else "unknown"
                note = f"Table 6, {metric_name} block, {m} row, {qtl_type} column (deterministic XML extraction; rowspans resolved per data/omics/amp-coverage-20261007/feng/review-notes.md)."
                if not is_auc:
                    note += (" Signed effect size; no universal desirable sign/direction is stated by the source.")
                elif is_auc and m == "AlphaGenome, output tracks*" and qtl_type in ("eQTL", "sQTL"):
                    note += (" Source Results prose (Sec8) states AlphaGenome's QTL AUC as approximately 0.80, which "
                             "differs from this exact Table 6 AUC cell (eQTL 0.8029, sQTL 0.7147); the table value is "
                             "retained and the prose discrepancy is not silently resolved or transposed onto Cohen's d.")
                rid = f"amp-feng-20261007-result-qtl-{slug(qtl_type)}-{slug(m)}-{slug(metric_name)}"
                records.append(result_record(rid, f"{m} {qtl_type} {metric_name}", FENG_SOURCE_ID, eid,
                                              f"{qtl_type} {metric_name}", val, val.replace("−", "-"),
                                              "AUC" if is_auc else "Cohen's d", direction, None, note))
            qtl_eval_ids_by_type[qtl_type].append(eid)
        mappings.append(dict(
            id=f"use-case-mapping-amp-20261007-feng-qtl-{slug(qtl_type)}",
            use_case_id="use-case-regulatory-variant-gene-follow-up",
            protocol_id=protocol_qtl, evaluation_ids=qtl_eval_ids_by_type[qtl_type],
            endpoint=f"{qtl_type} causal-versus-noncausal variant discrimination (AUC, Cohen's d) for twelve DNA foundation-model/genomic-comparator configurations",
            relevance="proxy",
            rationale=f"{qtl_type} causal-variant discrimination is a proxy for regulatory-variant gene follow-up prioritisation; it is not an experimentally validated follow-up choice and is a separate task from the other three QTL types.",
            case_limitations=[f"Post-window-filter per-model scored denominators are unreported for {qtl_type}; the pre-filter positive count ({QTL_PRE_FILTER_COUNTS[qtl_type]}) is not a confirmed denominator.",
                               "AlphaGenome appears only in this QTL comparison, not the pathogenic/common SNP comparison. It uses the long-window QTL dataset, consuming central 131,072 bp and averaging output tracks over central 2,048 bp.",
                               "Sei, Enformer (hidden/output tracks) and AlphaGenome (output tracks) are non-DNA-foundation specialised genomic comparators per the source's own asterisk notation, not DNA foundation models.",
                               "No independent reproduction or qualified human scientific review."],
        ))
    return mappings
def sha256_text(text):
    return hashlib.sha256(text.encode("utf8")).hexdigest()


def build_all():
    records = []
    mappings = []
    mappings += build_oncology_rna(records)
    mappings += build_pathogens_fragmentomics(records)
    mappings += build_methylation_cnv(records)
    mappings += build_feng_expansion(records)
    ids = [r["id"] for r in records]
    if len(ids) != len(set(ids)):
        dupes = {i for i in ids if ids.count(i) > 1}
        raise ValueError(f"Duplicate canonical record IDs: {dupes}")
    return records, mappings


def write_lane(records, mappings):
    clinical = OUT / "clinical"
    research = OUT / "research"
    experimental = OUT / "experimental"
    for lane in (clinical, research, experimental):
        lane.mkdir(parents=True, exist_ok=True)

    records_jsonl = "\n".join(json.dumps(r, sort_keys=True) for r in records) + "\n"
    (clinical / "records.jsonl").write_text(records_jsonl)
    (research / "records.jsonl").write_text("")
    (experimental / "records.jsonl").write_text("")

    by_issue = {}
    for m in mappings:
        issue_tag = m["id"].split("-issue")[-1] if "-issue" in m["id"] else m["id"].split("-feng-")[-1]
        by_issue.setdefault(issue_tag, []).append(m)

    coverage = [{
        "use_case_id": m["use_case_id"],
        "mapping_id": m["id"],
        "protocol_id": m["protocol_id"],
        "evaluation_ids": m["evaluation_ids"],
        "relevance": m["relevance"],
        "endpoint": m["endpoint"],
        "limitations": m["case_limitations"],
    } for m in mappings]
    (clinical / "coverage.json").write_text(json.dumps(coverage, indent=2, sort_keys=True) + "\n")
    (research / "coverage.json").write_text("[]\n")
    (experimental / "coverage.json").write_text("[]\n")

    claims_buffer = io.StringIO(newline="")
    claims_writer = csv.writer(claims_buffer, lineterminator="\n")
    claims_writer.writerow(["record_id", "source_id", "locator", "printed_value", "review_scope"])
    for r in records:
        if r["kind"] != "result":
            continue
        a = r["attributes"]
        source_id = r["source_ids"][0] if r["source_ids"] else ""
        locator = a.get("source_locator", "")
        claims_writer.writerow([r["id"], source_id, locator, a.get("printed_value", ""), "automated_source_review"])
    (clinical / "claims.csv").write_text(claims_buffer.getvalue())
    (research / "claims.csv").write_text("record_id,source_id,locator,printed_value,review_scope\n")
    (experimental / "claims.csv").write_text("record_id,source_id,locator,printed_value,review_scope\n")

    research_md = f"""# AMP bounded evidence intake, 2026-10-07 (clinical lane)

Additive intake for rewire.it#365 (benchmark-data issues #10-19). Covers nine
new AMP use-case decisions (tumour DNA somatic variant detection, tumour RNA
fusion detection, patient-RNA splicing validation, diagnostic DNA/RNA
pathogen identification, plasma ctDNA fragmentomics/methylation detection,
CNV detection/characterisation, diagnostic genomics model execution) plus a
bounded Feng/Peng Wei DNA-foundation-model table expansion (issue #19).

Scope: {len(records)} new catalogue records ({sum(1 for r in records if r['kind'] == 'source')} source,
{sum(1 for r in records if r['kind'] == 'protocol')} protocol,
{sum(1 for r in records if r['kind'] == 'dataset')} dataset,
{sum(1 for r in records if r['kind'] == 'configuration')} configuration,
{sum(1 for r in records if r['kind'] == 'evaluation')} evaluation,
{sum(1 for r in records if r['kind'] == 'result')} result) and {len(mappings)} new
use-case mapping objects (nine against the new AMP use cases, four against
existing use cases from the Feng expansion).

All status_checked promotions are bounded transcription of primary-source
table cells: automated review per workbench/amp-supervision/primary-review.md
and integration-review-corrections.md, independently checked by a Codex root
reviewer, not qualified human scientific review or independent experimental
reproduction. See workbench/amp-supervision/sonnet-integration-report.md for
exact counts, diff and remaining blockers.

Research and experimental lanes are empty scaffolding only; no record in
this intake is an experimental/research-only lane entry.

## Explicit preserved conflicts and scope limits

- Lancet (PMC6123722): virtual-tumour SNV/indel precision/recall only; no
  tumour clinical utility inference. Strelka2 indel TP 3,647 + FN 1,298 =
  4,945, consistent with the declared 4,945 truth indels. Unselected LoFreq
  (TP 3,210 + FN 1,744 = 4,954; call count 4,853 vs TP 3,210 + FP 1,652 =
  4,862) and MuTect2 (call count 4,873 vs TP 2,712 + FP 2,071 = 4,783) rows
  are internally inconsistent in the source and are excluded from this
  intake, not silently reconciled.
- EnFusion (PMC8642973): synthetic Seraseq known-fusion rescue (optimised,
  100% precision/sensitivity configuration) does not measure novel-fusion
  discovery. NCH clinical-cohort sensitivity (94.0% STAR-Fusion, 88.1%
  Arriba) is ascertained against the optimised EnFusion ensemble's own calls,
  not an independent exhaustive truth set. Table 2 caption (v3) vs
  optimisation narrative (v2) and STAR-Fusion 43.6% (Table 2) vs 43.8%
  (paragraph) precision conflicts are preserved unresolved.
- FRASER (PMC7822922): 85% / mean 11-of-13 known pathogenic splicing-event
  recovery at 30 of 119 patient RNA samples is recovery of known events, not
  diagnostic yield in unknown cases. Full-cohort outlier-gene workload counts
  (12/7/10 genes/sample) are a different population and are not attached to
  this 30-sample recovery evaluation.
- Karius/Blauwkamp 2019: 93.7% (59/63) positive percent agreement with
  initial blood culture is a bounded Table 2 transcription, not sensitivity
  against all 350 sepsis-alert patients; initial blood culture does not
  identify every true infection.
- UCSF respiratory mNGS (PMC11558004): 93.6% (103/110) is sensitivity against
  original clinical RVP testing on a residual pre-DTCA mixed respiratory
  target cohort (RNA extraction, DNase, cDNA synthesis; adenovirus
  transcripts included via transcription). The conflicting composite PPA
  figure (98.7%, 110.5/113) is excluded. This is not a mixed DNA/RNA
  sample-prep comparison and not an RNA-virus-only subgroup score.
- DELFI (PMC6774252): 73% (152/208) sensitivity at a reported 98% specificity
  is from repeated 10-fold cross-validation (10 repeats), not a separately
  held-out validation cohort and not prospective screening validation.
  Classifier inputs are GC-corrected TOTAL and SHORT fragment coverage across
  504 genomic bins, 39 arm Z-scores and mitochondrial representation (not a
  short/long fragment-length ratio).
- cfMethyl-Seq: 80.7% sensitivity (95% CI 68.6-90.7) at 97.9% specificity,
  repeated random 25% test split, cohort 217 cancers/191 non-cancers, test
  n=102. No per-run denominator is inferred beyond what is printed.
- DRAGEN 4.2: CNV/SV 1-5 kb deletion F-score (H6=.926, L6=.391 selected) is a
  bounded Table S4 transcription; the .391 vs 39.20% comparator-table/prose
  conflict is preserved, not promoted. Phase 4 total single-sample runtime
  (AE20=1838.5s HG002; AE7=5521.21s AWS HG002) is a conventional-pipeline
  operational baseline, a proxy for foundation-model execution workload, not
  a model-execution benchmark; stage times cannot be summed due to
  concurrency, and host RAM capacity in the hardware comparator is not
  measured peak usage.
- Feng et al. 2025 (PMC12663285): source `evidence-expansion-dna-foundation-models-2025-5d8ca9bc`
  is reused unchanged; retrieval SHA-256 independently reconfirmed by Codex.
  Table 1 (Acceptor/Donor), Table 2 (Arabidopsis TATA/NonTATA), Table 5
  (pathogenic/common SNP AUC + Cohen's d) and Table 6 (eQTL/sQTL/paQTL/ipaQTL
  AUC + Cohen's d) are added as source-reported ({{"origin": "independent_paper"}})
  evaluations: Feng et al. benchmark third-party pretrained models and
  introduce none of them. Cohen's d is a signed effect size with no stated
  universal desirable direction and is recorded with metric_direction
  "unknown"; Table 6's AlphaGenome eQTL=0.8029/sQTL=0.7147 table cells are
  retained exactly even though source prose elsewhere states AlphaGenome's
  QTL AUC as approximately 0.80, a prose/table discrepancy that is not
  silently resolved. Short-window and long-window variant populations are
  distinct and are never pooled. Gene expression (Table 4), TAD analysis,
  CNN comparators, runtime figures and supplements remain outstanding for
  issue #19. No mapping is made to pathogen detection, tumour variant
  calling, ctDNA cancer detection, Human-5mC-to-ctDNA, or any BRCA-specific
  subgroup.

No new model execution. No qualified human scientific review. No broad
clinical validation is claimed for any mapping in this intake.
"""
    (clinical / "research.md").write_text(research_md)
    (research / "research.md").write_text("# AMP bounded evidence intake, 2026-10-07 (research lane)\n\nEmpty scaffolding; no research-lane record is added by this pass.\n")
    (experimental / "research.md").write_text("# AMP bounded evidence intake, 2026-10-07 (experimental lane)\n\nEmpty scaffolding; no experimental-lane record is added by this pass.\n")

    sources = [r for r in records if r["kind"] == "source"]
    sources_md_lines = ["# AMP bounded evidence intake sources, 2026-10-07\n"]
    for s in sources:
        a = s["attributes"]
        sources_md_lines.append(f"- `{s['id']}`: {s['name']} ({a.get('url', '')}); retrieved {a.get('retrieved_at', 'n/a')}; "
                                  f"artifact_sha256={a.get('artifact_sha256', 'n/a')}; licence={a.get('licence', a.get('license', 'unreported'))}.")
    (clinical / "sources.md").write_text("\n".join(sources_md_lines) + "\n")
    (research / "sources.md").write_text("# AMP bounded evidence intake sources, 2026-10-07 (research lane)\n\nEmpty scaffolding.\n")
    (experimental / "sources.md").write_text("# AMP bounded evidence intake sources, 2026-10-07 (experimental lane)\n\nEmpty scaffolding.\n")

    retrieval_log = """# AMP bounded evidence intake retrieval log, 2026-10-07

All retrieval timestamps below are the research groups' own dated receipts
(unchanged, read from data/omics/amp-coverage-20261007/*/retrieval*.json and
*/*.retrieval.json); this integration pass performed no new retrievals.
Independent primary-value checks were performed by a Codex root reviewer on
2026-10-07 (workbench/amp-supervision/primary-review.md), followed by a
second-cycle correction pass (workbench/amp-supervision/integration-review-corrections.md)
applied before this lane was built. See each source's retrieved_at attribute
in clinical/sources.md for exact per-source times; none is fabricated or
estimated.
"""
    (clinical / "retrieval-log.md").write_text(retrieval_log)
    (research / "retrieval-log.md").write_text("# AMP bounded evidence intake retrieval log, 2026-10-07 (research lane)\n\nEmpty scaffolding.\n")
    (experimental / "retrieval-log.md").write_text("# AMP bounded evidence intake retrieval log, 2026-10-07 (experimental lane)\n\nEmpty scaffolding.\n")

    before = {
        "scope": "Bounded additive AMP intake (rewire.it#365; rewire-benchmark-data issues #10-19). Not a full 26-case audit; before.json here records only what this pass must preserve.",
        "existing_active_mapping_count": 72,
        "existing_use_case_count": 17,
        "note": "All 72 existing mapping objects and 17 existing use-case definitions in data/omics/use-cases/inputs.json remain byte-identical after this intake. This pass adds nine new use-case definitions, nineteen new mapping objects (ten for the new use cases, nine proxy mappings onto existing use cases from the task-scoped Feng expansion), and this coverage lane's canonical records. No release is frozen by writing this receipt.",
    }
    (OUT / "before.json").write_text(json.dumps(before, indent=2, sort_keys=True) + "\n")

    bound_artifacts = {path: info["artifact_sha256"] for path, info in ARTIFACT_BINDINGS.items()}
    bound_archives = {path: info["archive_sha256"] for path, info in ARTIFACT_BINDINGS.items()}
    bound_matches_original = {path: info["matches_original_artifact_sha256"] for path, info in ARTIFACT_BINDINGS.items()}

    for lane, name, n_records, n_results in (
        ("clinical", "clinical", len(records), sum(1 for r in records if r["kind"] == "result")),
        ("research", "research", 0, 0),
        ("experimental", "experimental", 0, 0),
    ):
        review_lane = {
            "status": "passed_with_explicit_scope_limits" if lane == "clinical" else "not_applicable_empty_lane",
            "reviewer": REVIEWER,
            "method": "automated_source_review",
            "reviewed_at": REVIEWED_AT,
            "record_count": n_records,
            "result_count": n_results,
            "scope": research_md if lane == "clinical" else f"Empty {lane}-lane scaffolding; no record added.",
            "checked": {
                "bound_artifacts_raw_sha256": bound_artifacts if lane == "clinical" else {},
                "bound_artifacts_archive_sha256": bound_archives if lane == "clinical" else {},
                "bound_artifacts_match_original": bound_matches_original if lane == "clinical" else {},
            },
            "limitations": [
                "Automated source review is not qualified human scientific review or experimental reproduction.",
                "artifact_sha256 is hashed fresh from whatever bytes are currently committed under data/omics/amp-coverage-20261007/ (read-only); original_artifact_sha256 preserves the historically Codex-verified full-source digest. If a research group's archive worker later substitutes a compact factual receipt for a full-text artifact, artifact_sha256 and bound_artifacts_match_original will change on the next regeneration; this is expected, not an error, and does not retroactively claim the original full bytes were independently verified if they are no longer distributed.",
                "No new model execution anywhere in this intake.",
            ] if lane == "clinical" else ["Empty lane; nothing to review."],
        }
        (OUT / f"review-{name}.json").write_text(json.dumps(review_lane, indent=2, sort_keys=True) + "\n")

    lane_files = ["records.jsonl", "coverage.json", "research.md", "sources.md", "claims.csv", "retrieval-log.md"]
    file_list = ["before.json", "review-clinical.json", "review-research.json", "review-experimental.json"] + \
        [f"{lane}/{f}" for lane in ("clinical", "research", "experimental") for f in lane_files]
    files_hash = {f: sha256_text((OUT / f).read_text()) for f in file_list}

    review = {
        "schema_version": "1.0",
        "method": "automated_source_review",
        "reviewer": REVIEWER,
        "reviewed_at": REVIEWED_AT,
        "scope": ("Bounded additive AMP intake for rewire.it#365 (rewire-benchmark-data issues #10-19): "
                  f"{len(records)} new clinical-lane catalogue records and {len(mappings)} new use-case "
                  "mapping objects, transcribed from the three research groups' candidate dossiers plus a "
                  "bounded Feng/Peng Wei table expansion. Independent Codex source check per "
                  "workbench/amp-supervision/primary-review.md; corrected after a second independent review "
                  "pass per workbench/amp-supervision/integration-review-corrections.md (artifact-hash "
                  "verification method, review timestamp, issue 14/15 endpoint wording, FRASER workload-metric "
                  "scope, DELFI classifier-input wording, and author_reported vs independent_paper origin "
                  "convention). No qualified human scientific review or independent experimental reproduction."),
        "limitations": [
            "Automated source review (Sol collection, Sonnet integration, Codex source check) is not qualified human scientific review or independent experimental reproduction.",
            "Research and experimental lanes are empty scaffolding; all new records are in the clinical lane.",
            "Nine new use-case definitions are additive; the 17 existing use-case definitions and all 72 existing mapping objects are unchanged.",
            "artifact_sha256 is hashed fresh from the bytes currently committed under data/omics/amp-coverage-20261007/; original_artifact_sha256 separately preserves the historically Codex-verified full-source digest and is never overwritten by a later receipt substitution (workbench/amp-supervision/archive-reuse-review.json). No claim is made that undistributed primary bytes are independently re-verified in a fresh clone.",
            "A second independent review pass (Feng task/population scoping, artifact-hash semantics, issue 14/15 endpoint wording, FRASER workload-metric scope, DELFI classifier-input wording, author_reported vs independent_paper origin) is reflected in these records; see integration-review-corrections.md and feng-integration-review.json.",
        ],
        "errors": [],
        "files": files_hash,
    }
    (OUT / "review.json").write_text(json.dumps(review, indent=2, sort_keys=True) + "\n")
    return mappings


if __name__ == "__main__":
    records, mappings = build_all()
    mappings = write_lane(records, mappings)
    print(f"Wrote {len(records)} canonical records and {len(mappings)} mapping drafts to {OUT}")
    (OUT / "mappings-draft.json").write_text(json.dumps(mappings, indent=2, sort_keys=True) + "\n")
