"""Apply the independent review to batch gfm-guide-sources-20261014 (issue #138, PR #150).

Sets every record to source_checked, writes the reviewer's review block on each result and
claim, applies the review corrections listed in docs/reviews/2026-10-14-gfm-guide-sources.md,
and writes review/corrections.jsonl (the metadata-correction claim for the use case setting)
and review/use-case.json (the corrected use case record, for the store).
Usage, from the repository root: python3 -I <this file> <use-cases.jsonl>
"""
import json
import sys
from pathlib import Path

BATCH_DIR = Path(__file__).resolve().parents[1]
BATCH = BATCH_DIR / "batch.jsonl"
P = "gfm-guide-20261014-"
DATE = "2026-10-14"
REVIEWED_AT = "2026-10-14T15:00:00Z"
REVIEWER_NOTE = "Independent Claude (Opus 5.5) review agent for PR #150; did not extract this batch; no human review claimed"
DOC = "docs/reviews/2026-10-14-gfm-guide-sources.md"

FRESH = {  # reviewer's own retrievals on 2026-10-14
    "evee": "9e2176440dfae6740b9e799796297cdd70b9bd59edb5c0a1e7fcdb5d6978710a",
    "ntv3": "082ea9b096d634cad3fc568465ef887d2529060909777685261cfc0bb43fcbee",
}

records = [json.loads(line) for line in BATCH.read_text().splitlines()]
by_id = {r["id"]: r for r in records}


def review(old, method, method_note, note):
    return {
        "method": method,
        "method_note": method_note,
        "reviewer": ["claude"],
        "reviewer_note": REVIEWER_NOTE,
        "date": DATE,
        "artifact_sha256": old["artifact_sha256"],
        "retrieval_url": old["retrieval_url"],
        "note": note,
    }


CHECK = "review/check_gfm_guide.py"
NOT_REPRO = "Transcribed, not reproduced."
for r in records:
    r["status"] = "source_checked"
    a = r["attributes"]
    if r["kind"] not in ("result", "claim") or r["id"].startswith("metadata-correction-"):
        continue
    old = a["review"]
    rid = r["id"].removeprefix(P)
    if rid.startswith("result-evee-") and "embedding" not in rid:
        fig = "1c" if "deconfounded" in rid else "1d"
        a["review"] = review(old, ["source-hash-verification", "pdf-text-parse", "rendered-source-visual-check", "independent-cell-check"],
            f"Overall row parsed by the reviewer's own script ({CHECK}) from the repository vector PDF of Figure {fig} (SHA-256 matches the pinned record), "
            f"column order taken from the pinned plotting code and checked against a 300 dpi render of page 3 of a fresh copy of the paper (SHA-256 {FRESH['evee']}; "
            "bioRxiv stamps each download, see the source's hash_scope).",
            f"Value matches. {NOT_REPRO} " + (
                "AlphaMissense's Overall cell is its missense-only AUROC (source concern confirmed in the plotting code)." if "alphamissense" in rid else
                "The Figure 1b/1c 'NTv3' column is a zero-shot cosine distance, not the Methods' probe (source concern confirmed: fig1c_deconf_heatmap.py calls prepare() in _heatmap_common.py)." if "ntv3-cosine" in rid else
                "The EVEE authors developed this method; author_reported origin confirmed." if "evo2-covariance" in rid else
                "Comparator built by the EVEE authors on Evo 2; author_reported accepted (three EVEE authors match Evo 2 authors by name)." if "evo2" in rid else
                "Baseline run by the EVEE authors, who did not develop it; independent_paper accepted."))
    elif rid == "result-evee-embedding-extraction-h100-hours":
        a["review"] = review(old, ["pdf-text-parse", "independent-cell-check"],
            f"Sentence 'Extraction used ∼20,000 H100-hours' located in the reviewer's text extraction of a fresh copy of the paper (SHA-256 {FRESH['evee']}; per-download stamp, see hash_scope).",
            f"Value matches. Approximate figure; GPU count and wall clock not stated. {NOT_REPRO}")
    elif rid.startswith("result-hegde-nt-5-epochs"):
        a["review"] = review(old, ["source-hash-verification", "deterministic-table-parse", "independent-cell-check"],
            f"Table A1 (table-wrap genes-16-01358-t0A1) parsed with ElementTree by the reviewer's script ({CHECK}); header and seed row asserted; XML SHA-256 matches.",
            f"Value matches. Hardware is from the Methods (2 × TITAN Xp for the Nucleotide Transformer); Table A1 names none. Review corrected the configuration's fine-tuning description from full fine-tuning to LoRA (Appendix A.3). {NOT_REPRO}")
    elif rid.startswith("result-hegde-"):
        a["review"] = review(old, ["source-hash-verification", "independent-cell-check"],
            f"Methods paragraph 3 sentence asserted verbatim in the reviewer's ElementTree text of the XML ({CHECK}); XML SHA-256 matches.",
            f"Value matches, including the printed hedge word. {NOT_REPRO}")
    elif rid.startswith("result-ntv3-"):
        a["review"] = review(old, ["pdf-text-parse", "independent-cell-check"],
            f"Table 5 (page 34) parsed by the reviewer's script ({CHECK}) from pdftotext -layout of a fresh copy (SHA-256 {FRESH['ntv3']}, 107 pages; bioRxiv stamps each download, see hash_scope); caption, row labels and five columns asserted.",
            f"Value matches. {NOT_REPRO}")
    elif rid.startswith("result-nt-"):
        a["review"] = review(old, ["source-hash-verification", "independent-cell-check"],
            f"Methods 'Data preparation > Hardware' paragraph 1 sentence asserted verbatim in the reviewer's ElementTree text of the XML ({CHECK}); XML SHA-256 matches.",
            f"Value matches. Conflicts with the Discussion's 'under 15 min on a single GPU' (source concern confirmed). {NOT_REPRO}")
    elif rid.startswith("result-hyenadna-"):
        compiled = "dnabert" in rid or "nt-2-5b" in rid
        a["review"] = review(old, ["source-hash-verification", "pdf-text-parse", "independent-cell-check"],
            f"Table A.2 (page 17) parsed by the reviewer's script ({CHECK}) from pdftotext -layout; caption, Params, GPUs, Wall clock and GPU-hrs rows asserted; PDF SHA-256 matches.",
            "Value matches. " + ("paper_compilation accepted: the table gives no source for this row. " if compiled else "author_reported accepted. ")
            + ("GPU-hours are about 2.5 times GPUs × wall clock in the same table; see the source concern added by the review. " if compiled and "gpu-hours" in rid else "")
            + NOT_REPRO)
        if compiled and "gpu-hours" in rid:
            a["limitations"] = ["Printed GPU-hours are about 2.5 times the GPUs × wall clock printed in the same column; see the source concern. Do not compare without resolving it."]
    elif r["kind"] == "claim":
        a["review"] = review(old, ["source-hash-verification", "ai-assisted-source-review"],
            f"Each source sentence the claim rests on asserted verbatim in the reviewer's own text extraction ({CHECK}); the claim text was then read against them.",
            "Claim matches the source.")
    else:
        raise SystemExit(f"no review rule for {r['id']}")

# Review corrections (numbered as in the dated review).
# 1. Hegde NT fine-tuning was LoRA through peft, not full fine-tuning (Appendix A.3).
cfg = by_id[P + "config-hegde-nt-500m-human-ref-5-epochs"]["attributes"]
assert cfg["fine_tuning"]["description"].startswith("Full fine-tuning")
cfg["fine_tuning"]["description"] = ("LoRA parameter-efficient fine-tuning with the peft package (r=1, lora_alpha=32, lora_dropout=0.1) "
    "through the Hugging Face Trainer, 5 epochs (Appendix A.3)")

# 2. EVEE authorship: 11 of 23 authors are Goodfire employees, not most.
c = by_id[P + "claim-evee-developer-overlap"]["attributes"]
old = "EVEE is reported by its developers, mostly Goodfire employees (Competing interests)."
assert c["value"].startswith(old)
c["value"] = c["value"].replace(old, "EVEE is reported by its developers: 11 of its 23 authors, including the first and last authors, are Goodfire employees (Competing interests); 11 are at Mayo Clinic.")
c["review"]["note"] = "Review corrected 'mostly Goodfire employees' to the count on the title page and in Competing interests (11 of 23)."

# 3. The NT 'under 15 min' sentence is in Discussion paragraph 3.
c = by_id[P + "claim-nt-fine-tuning-single-gpu"]["attributes"]
assert c["source_locator"].startswith("Discussion, paragraph 2:")
c["source_locator"] = c["source_locator"].replace("Discussion, paragraph 2:", "Discussion, paragraph 3:")
c["review"]["note"] = "Claim matches the source. Review corrected the locator from Discussion paragraph 2 to paragraph 3."
src = by_id[P + "source-nt-nature-methods"]["attributes"]
assert src["evidence_concerns"][0]["source_locator"].endswith("Discussion, paragraph 2")
src["evidence_concerns"][0]["source_locator"] = src["evidence_concerns"][0]["source_locator"].replace("paragraph 2", "paragraph 3")

# 4. bioRxiv per-download stamps: the pinned bytes cannot be reproduced.
stamp = ("bioRxiv stamps the PDF on each download (XMP ModifyDate, MetadataDate, DocumentID and InstanceID, the Info ModDate and the trailer /ID), "
         "so later retrievals differ. The extractor's copy was not retained, so the pinned bytes could not be re-verified.")
by_id[P + "source-evee-v4"]["attributes"]["hash_scope"] = (
    "SHA-256 of one retrieval of the bioRxiv PDF (2026-10-14T12:02:25Z). " + stamp + " The independent reviewer's retrieval on 2026-10-14 "
    f"(5,466,701 bytes, 26 pages, ModDate D:20261014063735-07'00') had SHA-256 {FRESH['evee']}; its Figure 1c and 1d match the repository "
    "vector PDFs cell for cell in the Overall rows, and the quoted Methods and Competing interests sentences are present.")
by_id[P + "source-ntv3-v1"]["attributes"]["hash_scope"] = (
    "SHA-256 of one retrieval of the bioRxiv PDF (2026-10-14T12:05:27Z). " + stamp + " The independent reviewer's retrieval on 2026-10-14 "
    f"(15,535,038 bytes, 107 pages, ModDate D:20261014041002-07'00') had SHA-256 {FRESH['ntv3']}; all 13 Table 5 cells and the quoted "
    "section 4.4.4 and Results sentences match in that copy.")

# 5. HyenaDNA Table A.2: compiled GPU-hours are inconsistent with GPUs × wall clock.
hy = by_id[P + "source-hyenadna-arxiv-v2"]["attributes"]
hy.setdefault("evidence_concerns", []).append({
    "source_id": P + "source-hyenadna-arxiv-v2",
    "message": ("Table A.2 GPU-hours for the DNABERT and Nucleotide Transformer columns do not equal the GPUs × wall clock printed in the same table: "
                "8 GPUs × 25 days is 4,800 GPU-hours against 12,000 printed, and 128 GPUs × 28 days is 86,016 GPU-hours against 215,000 printed, both about "
                "2.5 times higher. The HyenaDNA columns agree (1 GPU × 80 min, about 1.3 GPU-hours). The Nucleotide Transformer article (Methods 'Hardware') "
                "also gives 128 A100 GPUs for 28 days. The table cites no source for these columns. Values are kept as printed and should not be compared "
                "until the discrepancy is resolved."),
    "source_locator": "Table A.2 (page 17), rows 'GPUs', 'Wall clock' and 'GPU-hrs', columns 'DNABERT' and 'Nucleotide Transformer'",
    "artifact_sha256": hy["artifact_sha256"],
    "reviewed_at": REVIEWED_AT,
    "review_method": "automated-source-review",
})

# 6. Use case text: the extractor's evidence_gaps[2] said no DNA foundation-model result is linked,
# but Alavi et al. 2026 Evo 2 40B, Genos 10B and NTv3 650M evaluations are.
GAP = ("Feng et al. 2025 Table 1 splice-site classification is not linked to this use case: it measures AUC on benchmark splice-site sequences "
       "(DNABERT-2/NT datasets), not patient RNA, and is linked to 'Prioritise variants for splicing experiments'. The DNA foundation-model results "
       "linked here (Alavi et al. 2026: Evo 2 40B, Genos 10B and NTv3 650M) are threshold classifications of variants with established splicing "
       "defects, also proxies; none recovers events from patient RNA-seq.")
OLD_SETTING_TAIL = ("A separate, proxy sequence-classification AUC for DNA foundation-model embeddings (Feng et al. 2025, Table 1 Acceptor/Donor) "
                    "is also linked, scoped as a different endpoint.")
NEW_SETTING_TAIL = ("Separate, proxy sequence-classification results for DNA foundation models (Alavi et al. 2026: Evo 2 40B, Genos 10B and NTv3 650M "
                    "classifying variants with established splicing defects against benign variants) are also linked, scoped as a different endpoint. "
                    "Feng et al. 2025 Table 1 splice acceptor and donor classification is linked to 'Prioritise variants for splicing experiments', not here.")
ALAVI = "rna-splicing-20261011-alavi2026-source-article"
FENG = "evidence-expansion-dna-foundation-models-2025-5d8ca9bc"
LINKS_LOCATOR = ("Store links: use-case-splicing-follow-up assessed_by amp-feng-20261007-protocol-splice-acceptor and -splice-donor, none from this use case; "
                 "this use case assessed_by rna-splicing-20261011-alavi2026-protocol-opa1-evaluation and -multigene, whose evaluations include the "
                 "Evo 2 40B, Genos 10B and NTv3 650M configurations")

gap = by_id["metadata-correction-gfm-guide-20261014-patient-rna-splicing-evidence-gaps-2"]
gap["description"] = ("The text said Feng et al. 2025 Table 1 is linked to this use case. Its acceptor and donor protocols are linked to "
                      "use-case-splicing-follow-up only. Historical releases retain the previous value.")
gap["source_ids"] = [FENG, ALAVI]
ga = gap["attributes"]
extractor_gap = ga["value"]
ga["value"] = GAP
ga["source_locator"] = LINKS_LOCATOR
ga["review"] = {
    "method": ["scope-review"],
    "method_note": "Use case assessed_by links, judgement claim subjects and the configurations of every evaluation on the linked protocols read from the store on the PR branch.",
    "reviewer": ["claude"], "reviewer_note": REVIEWER_NOTE, "date": DATE,
    "note": ("The extractor's replacement text said no DNA foundation-model result is linked to this use case; Alavi et al. 2026 foundation-model "
             f"evaluations are linked, so the review replaced it. Extractor's text: {extractor_gap}"),
}

uc = next(json.loads(l) for l in open(sys.argv[1]) if '"id":"use-case-patient-rna-splicing-validation"' in l)
ua = uc["attributes"]
assert ua["evidence_gaps"][2] == extractor_gap
ua["evidence_gaps"][2] = GAP
old_setting = ua["setting"]
assert old_setting.endswith(OLD_SETTING_TAIL)
ua["setting"] = old_setting[: -len(OLD_SETTING_TAIL)] + NEW_SETTING_TAIL

setting_claim = {
    "id": "metadata-correction-gfm-guide-20261014-patient-rna-splicing-setting",
    "kind": "claim",
    "name": "Select a patient-RNA splicing-variant validation workflow: attributes.setting",
    "description": ("The setting said Feng et al. 2025 Table 1 is the proxy sequence-classification evidence linked to this use case. The Feng "
                    "protocols are linked to use-case-splicing-follow-up; the linked foundation-model proxy is Alavi et al. 2026. Change of "
                    "citation, not of meaning; historical releases retain the previous value."),
    "status": "source_checked",
    "facets": {},
    "source_ids": [FENG, ALAVI],
    "links": [{"relation": "subject", "target_id": "use-case-patient-rna-splicing-validation"}],
    "attributes": {
        "field": "attributes.setting",
        "previous_value": old_setting,
        "value": ua["setting"],
        "source_locator": LINKS_LOCATOR,
        "review": {
            "method": ["scope-review"],
            "method_note": ("Use case links and the 18 assessed_by judgements read on the PR branch; each judgement's rationale treats proxies as "
                            "sequence-classification evidence kept separate from patient-RNA recovery, which the new text keeps."),
            "reviewer": ["claude"], "reviewer_note": REVIEWER_NOTE, "date": DATE,
            "note": f"Applied by the independent reviewer; the 18 judgements, the baseline and the summary were re-pinned. See {DOC}.",
        },
    },
}

dump = lambda r: json.dumps(r, ensure_ascii=False, separators=(",", ":"))
BATCH.write_text("".join(dump(r) + "\n" for r in records))
(BATCH_DIR / "review" / "corrections.jsonl").write_text(dump(setting_claim) + "\n")
(BATCH_DIR / "review" / "use-case.json").write_text(dump(uc) + "\n")
print(f"{len(records)} batch records reviewed; corrections.jsonl and use-case.json written")
