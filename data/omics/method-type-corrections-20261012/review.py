"""Independent review of the method-type corrections, 2026-10-12.
Run after prepare.py, from the repository root: python3 -I data/omics/method-type-corrections-20261012/review.py

Fills the review block of every claim and new source in batch.jsonl and sets them source_checked.
Each claim records which source the reviewer re-read for it, or that it was checked only against
other records in the store. The dated review is docs/reviews/2026-10-12-method-type-corrections.md.
"""
import json, os

HERE = "data/omics/method-type-corrections-20261012"
DATE = "2026-10-12"
REVIEW = "docs/reviews/2026-10-12-method-type-corrections.md"
REVIEWER_NOTE = "Separate Claude review agent, independent of the agent that prepared the corrections; no human review claimed"
EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest/{}/fullTextXML"

# Sources the reviewer re-retrieved: (retrieval URL, SHA-256 of the bytes read, hash note).
SRC = {
    "sctab": (EPMC.format("PMC11298532"), "e61b11cd873f3d13e891e9c33bac0847070826200f8fbe0b3969d994f1c52290", "matches the source record"),
    "abdelaal": (EPMC.format("PMC6734286"), "6df0937c5a2d8ba06465ba356c2321fb9f52d9ecf23456876acd82f828b41d4c", "matches the source record"),
    "msalign2": ("https://arxiv.org/pdf/2605.19752v2", "a31d1167b0ded72f64717881dd6cba0946a56b495d76f169d8e44115c3266fda", "matches the source record"),
    "msalign1": ("https://arxiv.org/pdf/2605.19752v1", "7395a55141ee7916741b7d9e6d4f42a1d3a03217a36ce6824ac3ff48afd4f26f", "matches the source record"),
    "massspecgym": ("https://arxiv.org/pdf/2410.23326v1", "82176d50e8947c8b9baa2a0d91493f5680c0e4c7e25a2266ff7879f48a58c40c", "matches the source record"),
    "jores": ("https://queitschlab.gs.washington.edu/pdf/Jores_et_al_2021.pdf", "31f9157ae1ad52c2f405348cf20f87ab4fb17f26a0b1a91032a9563bfadbd47a", "matches the source record"),
    "rhomax": (EPMC.format("PMC11200256"), "93814dd95c40cb109d592c2917728dc568c0445571e08180b188e726a4bd8f19", "matches the source record"),
    "framepool": (EPMC.format("PMC8136849"), "689af3ecab7b5a928eacc5a76d965960708cbb253fc7cdeae463b16d30ffd2e3", "matches the source record"),
    "benelli": ("https://academic.oup.com/bioinformatics/article/28/24/3232/247436", "6f5f3d171c30b89fc4889a15790bb3af1dc7a038e38ee289d062a394bf4ad61b",
                "innerText of .article-body rendered in Chrome; matches the source record"),
    "ramadane": (EPMC.format("PMC12120176"), "cd089e7c621818f457f54f93c37cc1b9d535e531212b1aaf431fcbdd733bbda1", "matches the source record"),
    "oncovi": ("https://pmc.ncbi.nlm.nih.gov/articles/PMC13269341/", "69ac0b1ef3902b1cb6461c87117db1af4b2035e6a84ab602b0c1d02fc898d28d",
               "live PMC HTML; differs from the source record, as expected for a dynamic page"),
    "chen2020": (EPMC.format("PMC7033911"), "fef52f70c3a0ff3f82902f87080933c220e12274787de6309b41ee283daf8b8e", "matches the source record"),
    "sun2024": (EPMC.format("PMC11660681"), "ce2ac8671cfddf088b33efb150ca50354181de81ca6bfb181dd5bf387c6714e8", "matches the source record"),
    "wang2026": (EPMC.format("PMC13353424"), "61464a274501bb9529b2250eb4c112071b8768fa640e87cf13f14d7df9f6fb23", "matches the source record"),
    "dnalongbench": (EPMC.format("PMC12627797"), "0d7db21f2a843dda3ba703c53cd0abad12c9c795cfbcf4fd1bdc6c4a863fe41b", "matches the source record"),
    "lipp": (EPMC.format("PMC13292216"), "6ff34f2f709a14858a3753abf9f8f6efa1e7e3c351f15c70cf64264193a9414e", "matches the source record"),
    "mprabc": (EPMC.format("PMC13232518"), "7717b5605e01c9346bd04e9510f4d99dff8a05c7af0feb956a82184b4dd7ce46", "matches the source record"),
    "cluspro": ("https://pmc.ncbi.nlm.nih.gov/articles/PMC7484347/", "575577ca8bf96f3cb9c9042f883c9b888d3bdeb90567c0f8fb9128f1203d6a86",
                "live PMC HTML; differs from the source record, as expected for a dynamic page"),
    "hector": ("https://www.medrxiv.org/content/10.64898/2026.07.06.26357220v1.full", "354b3613dc0bf56e078c8e032c49fca663e58e0e04cf5b0223858d3551d596ee",
               "live medRxiv HTML; differs from the source record, as expected for a dynamic page"),
    "lshvec": ("https://www.biorxiv.org/content/10.1101/726729v1.full.pdf", "adb61dd196d8468efa8ca043981c1fc99e5bac59b80a7649485ceda0e0413c33",
               "bioRxiv stamps each download, so the hash differs from the source record; the cited text is the same"),
    "cppc": ("https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13228547/supplementaryFiles", "80ee7ad255296a5650247f06bb1915af12adf6644c2b619417d6940e77368e9b",
             "member media-1.pdf (Note S1); Table S2 member media-3.xlsx and the article XML also match their source records"),
}


def source_for(rid):
    """The source the reviewer re-read for a subject record, or None when only the store was checked."""
    if "houseman" in rid or "epidish" in rid:
        return None  # Giuili 2025 configurations of methods Sun et al. 2024 does not describe
    for prefix, key in [
        ("ucc-research-config-sctab-", "sctab"), ("ucc-research-config-abdelaal-", "abdelaal"),
        ("uc20260930-msalign-v2-config-msalign", "msalign2"), ("msalign-2026-table3-method-msalign", "msalign1"),
        ("uc20260930-msalign-v2-config-", "msalign2"), ("msalign-2026-table3-method-", "msalign1"),
        ("uc20260930-jores-config-", "jores"), ("uc20260930-rhomax-config-", "rhomax"), ("uc20260930-framepool-config-", "framepool"),
        ("rna-fusion-20261009-", "benelli"), ("uc-clinical-20260930-method-bayesdel", "ramadane"), ("uc-clinical-20260930-bayesdel-", "ramadane"),
        ("uc-clinical-20260930-method-oncovi", "oncovi"), ("uc-clinical-20260930-oncovi-", "oncovi"),
        ("somatic-oncogenicity-20261009-", "chen2020"), ("ctdnameth-20261009-", "sun2024"), ("ctdnafrag-20261009-", "wang2026"),
        ("lit-genomics-20261011-dnalongbench-", "dnalongbench"), ("lit-structure-20261011-lipp-", "lipp"), ("catalog-model-diffdock-l", "lipp"),
        ("ucc-research-config-mprabc-", "mprabc"), ("ucc-docking-cluspro-bm5-2020-", "cluspro"), ("uc-clinical-20261005-hector-", "hector"),
        ("rna-pathogen-20261009-", "lshvec"), ("ucc-research-config-cppc-", "cppc")]:
        if rid.startswith(prefix):
            return key
    return None


# What the reviewer found, for subjects where it adds to the claim's own note.
NOTES = {
    "msalign2": "MSAlign aligns frozen DreaMS and MolDeBERTa encoders through trained MLP adapters (abstract; Section 3); the baselines paragraph and Table 1 describe JESTR and Emb-Cos as trained contrastive models and DeepSets as a fingerprint predictor.",
    "msalign1": "MSAlign v1 Section 5.1 \"Baselines\" and Table 1: FFN and DeepSets are fingerprint predictors from MassSpecGym; JESTR, Emb-Cos and SAIL are trained with InfoNCE losses; MSAlign aligns two frozen foundation models.",
    "benelli": "Section 2.6: \"we trained an AdaBoost classifier\" on the GJS, ES and US scores; Section 2.6.4: trained with synthetic data, it gives the EricScore. EricScript remains an alignment-based caller whose candidates are ranked by this learned score.",
    "hector": "Materials and Methods, \"Engine Design and ENIGMA V1.2 Implementation\": criteria applied against VCEP thresholds and decision trees, combined by ACMG/AMP rules and Tavtigian points; BayesDel and SpliceAI are inputs. No trained component.",
    "lshvec": "Section 3.3: \"taxonomy classification is supervised learning\", a one-layer softmax network over k-mer embeddings learned without labels (Section 3.2).",
    "cppc": "Checked against Note S1 and Table S2 columns A to D and G to K only. Note S1 describes the authors' reimplementation; the original write-ups were not read.",
    "abdelaal": "Table 1 lists scmapcell with classifier \"kNN\"; the locator was corrected from a description not in the source.",
    "dnalongbench": "DNALongBench does not say ABC has no training step; the locator was corrected to what the source prints, with MPRAbc for the form of the ABC score.",
}


def review_block(rid, base_note):
    key = source_for(rid)
    block = {"method": ["automated-source-review"], "reviewer": ["claude"], "reviewer_note": REVIEWER_NOTE, "date": DATE}
    if key:
        url, sha, hash_note = SRC[key]
        block["method"] = ["source-hash-verification", "automated-source-review"]
        block["method_note"] = (f"Compared previous_value with origin/main and the store; re-retrieved the source ({hash_note}) and read the passage in source_locator; "
                                "checked the new value against the method-type definitions in data/vocab/method-type.ttl.")
        block["artifact_sha256"] = sha
        block["retrieval_url"] = url
        extra = NOTES.get(key, "")
    else:
        block["method_note"] = ("Compared previous_value with origin/main and the store, and checked the new value against the method-type definitions and the "
                                "tags of the records named in source_locator. The cited publication was not re-read for this record.")
        extra = ""
    block["note"] = base_note.replace(" Pending independent review.", "") + " Independent review 2026-10-12: approved." + (f" {extra}" if extra else "") + f" See {REVIEW}."
    return block


SOURCE_NOTES = {
    "method-type-corrections-20261012-source-benelli2012": "Rendered the article page in Chrome and hashed the innerText of .article-body: 44,359 bytes, same SHA-256. Checked DOI, volume, issue, pages and dates against Crossref, the \"All rights reserved\" notice on the page, and that no text is archived.",
    "method-type-corrections-20261012-source-shi2019-lshvec": "Re-downloaded the bioRxiv v1 PDF; its bytes differ because bioRxiv sets the PDF modification date at download, so hash_scope was extended to say so. Checked DOI, posting date and authors against Crossref and the CC-BY-NC-ND 4.0 notice on every page.",
    "method-type-corrections-20261012-source-cppc-note-s1": "Added by this review: the corrections cite Note S1, which no source record pinned. Extracted media-1.pdf from the Europe PMC supplementary archive, hashed it, and took the licence from the article XML.",
}

path = os.path.join(HERE, "batch.jsonl")
records = [json.loads(line) for line in open(path)]
for r in records:
    r["status"] = "source_checked"
    if r["kind"] == "claim":
        rid = r["links"][0]["target_id"]
        r["attributes"]["review"] = review_block(rid, r["attributes"]["review"]["note"])
    else:
        r["attributes"]["review"] = {
            "method": ["source-hash-verification", "automated-source-review"], "reviewer": ["claude"], "reviewer_note": REVIEWER_NOTE, "date": DATE,
            "method_note": SOURCE_NOTES[r["id"]],
            "note": f"Independent review 2026-10-12: approved. See {REVIEW}."}
with open(path, "w") as out:
    for r in records:
        out.write(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n")
print(f"Reviewed {len(records)} records; {sum(1 for r in records if r['kind'] == 'claim' and source_for(r['links'][0]['target_id']))} claims source-checked.")
