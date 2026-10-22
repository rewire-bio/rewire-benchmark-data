"""Apply the independent review of use-case-coverage-hitdisc-20261022 to batch.jsonl.

Rewrites every record's review block, sets statuses, applies the eight descriptive corrections the
review found, adds the metadata-correction claims that keep the previous values, and adds the
source warnings. Deterministic: running it twice on the original batch gives the same bytes.
"""

import os

# Paths are configurable so the review can be rerun anywhere.
SOURCES_ROOT = os.environ.get("HITDISC_SOURCES", "sources")
BATCH_DIR = os.environ.get("HITDISC_BATCH_DIR", "data/omics/use-case-coverage-hitdisc-20261022")
import hashlib
import json
import re

BATCH = os.path.join(BATCH_DIR, "batch.jsonl")
REVIEW_DOC = "docs/reviews/use-cases/hitdisc-2026-10-22.md"
RECEIPT = "data/omics/use-case-coverage-hitdisc-20261022/review.json"
DATE = "2026-10-22"
REVIEWER_NOTE = ("Claude review agent, independent of the extraction agent; "
                 "no human review claimed")

SHA = {
    "shen": "11a4cee97057d9e72f9393024d22fdd169e3134f493367eee2f7869facf9ccf8",
    "kim": "9be510b7b0cc152ff56a03c96877bf06b6a6bdeffdb4baecf8e999a6bf155aa6",
    "cache3": "43b920ac9f67fac3560bcf7d24a79f76b9a0d0d962088dfe4081742ec7b9b071",
    "si002": "5e655da5728da46c6a57882c5fef0643c057536d7897d16b9c98f6d55c12f5fe",
    "audit": "e766c8aa4f94287672b2b1bacab2480a41ec7c806ecbaf5e2d1bf8773781310f",
    "page": "a2203612b553236d7f01da5573389d439d2f7aa0436080412f27da882e086e5e",
    "dude": "8f20c3adec704671ea668742622567a7c6aec9b38f6d804f977c175209fa500d",
    "mfpcba": "628c94a973118410ec616f9342237c141a139ca4f56c34c698c6d9dcb6d82241",
    "chen": "b845c78815bb0c4eabb3e05e65212b343269c91292fedf00fae9ac00c7840f09",
}

# ---------------------------------------------------------------- review blocks
HOW_CHECKED = {
    "shen-table": ("Re-downloaded the pinned Europe PMC XML, matched its SHA-256, and re-parsed "
                   "Tables 1 to 5 with a parser written for this review (myparse_shen.py), "
                   "independent of the extractor's build_batch.py. Every printed value, row label "
                   "and column header compared; the parser was proved on six seeded errors."),
    "kim-text": ("Re-downloaded the pinned Europe PMC XML, matched its SHA-256, confirmed it holds "
                 "no table-wrap element, and checked that each printed AUC string occurs verbatim "
                 "in the Results section 'Co-folding struggles to reliably re-rank docking hit "
                 "lists'. No figure was read."),
    "s8": ("Re-downloaded the Europe PMC supplementary archive, matched the SHA-256 of the member "
           "file ci5c02441_si_002.xlsx, and re-parsed sheet S8 from xl/worksheets/sheet9.xml and "
           "xl/sharedStrings.xml with a parser written for this review (myparse_xlsx.py), "
           "independent of the extractor's. Compared every cell's round-tripped decimal, stored "
           "string and column header, and read the stored cell formulas."),
    "hash": "Re-downloaded the artifact and matched its SHA-256 against the source record.",
    "scope": ("Read the record against the pinned sources and against docs/use-cases.md and "
              "docs/record-contract.md."),
}

METHODS = {
    "shen-table": ["independent-cell-check", "deterministic-table-parse"],
    "kim-text": ["independent-cell-check", "pdf-text-parse"],
    "s8": ["independent-cell-check", "deterministic-table-parse"],
    "hash": ["source-hash-verification"],
    "scope": ["scope-review", "automated-source-review"],
}


def review_block(kind_key, sha, url, note):
    return {
        "method": METHODS[kind_key],
        "reviewer": ["claude"],
        "reviewer_note": REVIEWER_NOTE,
        "date": DATE,
        "method_note": HOW_CHECKED[kind_key],
        "note": note,
        "artifact_sha256": sha,
        "retrieval_url": url,
        "receipt": RECEIPT,
    }


URL = {
    SHA["shen"]: "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12704515/fullTextXML",
    SHA["kim"]: "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13657626/fullTextXML",
    SHA["cache3"]: "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12892310/fullTextXML",
    SHA["si002"]: "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12892310/supplementaryFiles",
    SHA["audit"]: "https://arxiv.org/abs/2507.21404v2",
    SHA["page"]: "https://drugdesign.unistra.fr/LIT-PCBA/",
    SHA["dude"]: "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC3405771/fullTextXML",
    SHA["mfpcba"]: "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10170507/fullTextXML",
    SHA["chen"]: "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC6701836/fullTextXML",
}

TRANSCRIPTION_NOTE = ("Checked against the pinned source by an automated independent re-parse. "
                      "Transcription checked; not reproduced and not reviewed by a human scientist.")

# ---------------------------------------------------------------- corrections
NEW_NEF_QUALIFIER = {
    "R": ("Confirmed Tier 1 (chemically novel) hits among the workflow's predicted actives on the "
          "merged 1739-compound library, per 1000 compounds predicted active. The cell is stored "
          "as the formula 1000*N/L, that is 1000 times the Tier 1 count in column N divided by the "
          "predicted-active count in column L."),
    "S": ("Confirmed Tier 2 (not novel) hits among the workflow's predicted actives on the merged "
          "1739-compound library, per 1000 compounds predicted active. The cell is stored as the "
          "formula 1000*O/L, that is 1000 times the Tier 2 count in column O divided by the "
          "predicted-active count in column L."),
    "T": ("Confirmed Tier 1 and Tier 2 hits combined among the workflow's predicted actives on the "
          "merged 1739-compound library, per 1000 compounds predicted active. The cell is stored "
          "as the formula R+S, the sum of the two preceding columns."),
}

NEF_WARNING = (
    "The stored cell is a formula, not a transcribed number: column R is 1000*N/L, column S is "
    "1000*O/L and column T is R+S, so the value is confirmed Tier 1 or Tier 2 hits per 1000 "
    "compounds predicted active. That is the article's own hit-rate form scaled by 1000. The "
    "Figure 6c caption instead defines the normalised number as 'the aggregated score of all "
    "compounds predicted active divided by the number of compounds predicted to be actives', which "
    "does not describe this formula: the numerator is a count of confirmed tier hits, not an "
    "aggregated score, and the caption omits the factor of 1000. Read the formula, not the caption, "
    "and do not compare this value with a hit rate that has a different denominator or no scaling."
)

LITPCBA_WARNING = [
    ("Huang, Knight and Naprienko 2025 (arXiv:2507.21404v2, artifact "
     "e766c8aa4f94287672b2b1bacab2480a41ec7c806ecbaf5e2d1bf8773781310f, Abstract) audit LIT-PCBA "
     "and report extensive analogue and 2D-identical-compound leakage between its splits: 323 "
     "active training-validation analogue pairs at ECFP4 Tanimoto at or above 0.6 in ALDH1 alone "
     "and 2491 2D-identical inactives shared between training and validation across targets. They "
     "conclude that a parameter-free memorisation baseline matches or exceeds published "
     "deep-learning and 3D-similarity results, that nearly all published LIT-PCBA results are "
     "undermined, that zero-shot evaluations are also affected, and that the benchmark does not "
     "measure recovery of novel chemotypes. That bears on this value."),
    ("The actives-to-inactives ratio of LIT-PCBA is in dispute between the sources: the official "
     "page (artifact a2203612b553236d7f01da5573389d439d2f7aa0436080412f27da882e086e5e, data "
     "content table) gives 7761 actives and 382674 unique inactives for the 15 target sets, while "
     "Shen et al. 2025 (artifact "
     "11a4cee97057d9e72f9393024d22fdd169e3134f493367eee2f7869facf9ccf8, Methods 'Datasets') give "
     "10030 confirmed actives and 2798737 confirmed inactives. Neither source reconciles the "
     "other. NEF1% is defined as a correction for that ratio, so the normalised values rest on a "
     "count the sources disagree about."),
]

ZERO_SCORE_WARNING = (
    "This workflow has no experimentally confirmed hit (column E is 0), so the workbook's 0 in this "
    "column means there was no hit to score, not a hit the committee scored at zero. Do not average "
    "or rank these columns across workflows without excluding the workflows that returned no hit."
)

NO_NOVEL_WARNING = (
    "This workflow has no confirmed hit the committee judged chemically novel (column F is 0), so "
    "the workbook's 0 in this column means there was no novel hit to score, not a novel hit scored "
    "at zero."
)

WF1696_WRONG = "significantly more hits than any other workflow"
WF1696_RIGHT = ("did better than any other method in retrieving hits from the collection of all "
                "molecules selected in Round 1")
WF1696_WRONG_J = "significantly more hits than any other"
WF1696_RIGHT_J = ("did better than any other method in retrieving hits from the collection of all "
                  "molecules selected in Round 1")

CACHE_FIG6_LIMITATION = (
    "The article is internally inconsistent about Figure 6. The Results section 'Trends and "
    "Strategies from the Best Performing Computational Workflows' calls panels a, b and c 'top "
    "scoring compounds, top hit rates, and top selections from the merged Round 1 library', while "
    "the Figure 6 caption calls panel b 'the aggregated score of all Round 1 hits' and panel c the "
    "normalised Tier 1 and Tier 2 counts. The body text therefore calls an aggregated score a hit "
    "rate. No value in this batch is taken from Figure 6; every value is from sheet S8."
)

OWN_SELECTION_HITRATE_FIX = (
    "No hit rate is printed for this arm. Compounds tested (column D) and Hits (column E) are "
    "printed as separate counts and this batch records both without dividing them, because a "
    "derived rate would be a computation rather than a printed value. The article does publish a "
    "per-workflow rate, but for the merged-library arm: columns R, S and T of sheet S8 are stored "
    "as the formulas 1000*N/L, 1000*O/L and R+S, that is confirmed Tier 1 or Tier 2 hits per 1000 "
    "compounds predicted active."
)

OWN_SELECTION_ZERO_LIMITATION = (
    "Twelve of the 23 workflows returned no confirmed hit, and the workbook stores 0 for their "
    "score of best hit, aggregated score, top novelty score and top score of novel hits. A 0 in "
    "those columns means there was no hit to score, not a hit scored at zero; each affected result "
    "carries that warning."
)

MERGED_NOT_RATES_FIX = (
    "Columns L to Q are counts of compounds, not rates. Columns R, S and T are rates: the workbook "
    "stores them as 1000*N/L, 1000*O/L and R+S, so each is confirmed Tier 1 or Tier 2 hits per 1000 "
    "compounds predicted active. Predicting the merged library is also not the same task as "
    "selecting compounds to synthesise."
)

MERGED_LABEL_FIX = (
    "The two normalised columns are labelled as counts of hits while the Figure 6c caption defines "
    "the normalised quantity as an aggregated score divided by the number of compounds predicted "
    "active. The stored cell formulas (1000*N/L and 1000*O/L) agree with the column labels and not "
    "with the caption. The sheet's final column has no printed header at all; its formula is R+S."
)

MERGED_METRIC_DEFINITION = (
    "Every workflow was applied to the merged library of all 1739 Round 1 compounds. Confirmed hits "
    "with a score above 15 were clustered into four chemically novel Tier 1 compounds and 25 Tier 2 "
    "compounds. Columns L to Q are counts. Columns R, S and T are stored as the formulas 1000*N/L, "
    "1000*O/L and R+S, so they are confirmed Tier 1 or Tier 2 hits per 1000 compounds predicted "
    "active; the Figure 6c caption's wording, 'the aggregated score of all compounds predicted "
    "active divided by the number of compounds predicted to be actives', does not describe that "
    "formula."
)

AUDIT_CONCERN_REMOVED_NOTE = (
    "The extraction pass recorded the LIT-PCBA leakage audit as an evidence_concerns entry on the "
    "audit's own source record. The audit is not itself an unreliable source: it is the source that "
    "reports the problem. Because the use case and its summary cite this source, that entry "
    "withheld every judgement on the use case (shared/omics/use-cases.ts, cleanSource and the "
    "'a source the use case cites' blocker). The entry is removed by this review and the audit's "
    "finding is kept as the claim hitdisc-20261022-claim-litpcba-leakage-audit, as limitations on "
    "the LIT-PCBA benchmark and the five-target protocol, and as a source warning on each of the 84 "
    "LIT-PCBA results."
)

PAGE_CONCERN_MESSAGE = (
    "The official page (data content table, artifact "
    "a2203612b553236d7f01da5573389d439d2f7aa0436080412f27da882e086e5e) gives 7761 actives and "
    "382674 unique inactives for the 15 LIT-PCBA target sets, while Shen et al. 2025 (Methods "
    "'Datasets', artifact 11a4cee97057d9e72f9393024d22fdd169e3134f493367eee2f7869facf9ccf8) state "
    "10030 confirmed actives and 2798737 confirmed inactives for the full set. The two counts are "
    "not reconciled by either source; the difference is most likely unique against per-target "
    "inactives, but neither source says so. EF and NEF both depend on this ratio, so the conflict "
    "is left unresolved and marked rather than reconciled."
)


def cid(seed):
    return "metadata-correction-" + hashlib.sha1(seed.encode()).hexdigest()[:20]


def correction_claim(seed, name, description, subject, field, previous, value, locator,
                     source_ids, method_note):
    return {
        "id": cid(seed),
        "kind": "claim",
        "name": name,
        "description": description,
        "status": "source_checked",
        "facets": {"areas": ["molecular-interactions"], "contexts": ["research"]},
        "source_ids": source_ids,
        "links": [{"relation": "subject", "target_id": subject}],
        "attributes": {
            "field": field,
            "previous_value": previous,
            "value": value,
            "source_locator": locator,
            "review": {
                "method": ["scope-review", "independent-cell-check"],
                "reviewer": ["claude"],
                "reviewer_note": REVIEWER_NOTE,
                "date": DATE,
                "method_note": method_note,
                "note": ("Correction found by the independent review pass of batch "
                         "use-case-coverage-hitdisc-20261022. The previous value is kept here."),
                "receipt": RECEIPT,
            },
        },
    }


# ---------------------------------------------------------------- run
recs = [json.loads(l) for l in open(BATCH)]
by_id = {r["id"]: r for r in recs}
new_claims = []
changes = []


def note_change(what):
    changes.append(what)


# --- which CACHE workflows had no hit / no novel hit (read from the pinned sheet)
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import myparse_xlsx
s8 = myparse_xlsx.read_sheet(
    SOURCES_ROOT + "/supp/ci5c02441_si_002.xlsx", "S8")
rows = {}
for ref, d in s8.items():
    m = re.match(r"([A-Z]+)(\d+)$", ref)
    rows.setdefault(int(m.group(2)), {})[m.group(1)] = d
NO_HIT, NO_NOVEL = set(), set()
for rn, cells in rows.items():
    if rn == 1 or "B" not in cells:
        continue
    wf = str(int(float(cells["B"]["raw"])))
    if float(cells["E"]["raw"]) == 0:
        NO_HIT.add(wf)
    if float(cells["F"]["raw"]) == 0:
        NO_NOVEL.add(wf)
assert len(NO_HIT) == 12, NO_HIT

# =============================== F1: remove the audit's evidence_concerns
src = by_id["hitdisc-20261022-source-litpcba-audit"]
prev = json.dumps(src["attributes"].pop("evidence_concerns"), ensure_ascii=False)
new_claims.append(correction_claim(
    "hitdisc-litpcba-audit-evidence-concerns",
    "LIT-PCBA leakage audit source: evidence_concerns removed",
    ("The audit is the source that reports the LIT-PCBA problem, not a source with a problem. "
     "Keeping the entry withheld every judgement on the use case."),
    "hitdisc-20261022-source-litpcba-audit", "attributes.evidence_concerns", prev,
    ("Removed. The source record now carries no evidence_concerns entry. The audit's finding is kept "
     "as the claim hitdisc-20261022-claim-litpcba-leakage-audit, as limitations on the LIT-PCBA "
     "benchmark record and the five-target protocol, and as a source warning on each of the 84 "
     "LIT-PCBA results."),
    "arXiv:2507.21404v2 abstract page; shared/omics/use-cases.ts cleanSource",
    ["hitdisc-20261022-source-litpcba-audit"],
    ("Read the abstract of the pinned page against the entry, and traced the effect of a concerned "
     "source through shared/omics/use-cases.ts.")))
note_change("F1 removed evidence_concerns from hitdisc-20261022-source-litpcba-audit")

# =============================== F2: both hashes in the page's concern
page = by_id["hitdisc-20261022-source-litpcba-page"]
ec = page["attributes"]["evidence_concerns"]
assert len(ec) == 1
prev = ec[0]["message"]
ec[0]["message"] = PAGE_CONCERN_MESSAGE
ec[0]["source_locator"] = ("Official page data content table (artifact "
                           "a2203612b553236d7f01da5573389d439d2f7aa0436080412f27da882e086e5e) "
                           "against Shen et al. 2025 Methods 'Datasets' (artifact "
                           "11a4cee97057d9e72f9393024d22fdd169e3134f493367eee2f7869facf9ccf8)")
ec[0]["review_date"] = DATE
new_claims.append(correction_claim(
    "hitdisc-litpcba-page-concern-hashes",
    "LIT-PCBA page source: totals-conflict concern now names both artifact hashes",
    "The entry named both figures and both locators but only the page's artifact hash.",
    "hitdisc-20261022-source-litpcba-page", "attributes.evidence_concerns[0].message",
    prev, PAGE_CONCERN_MESSAGE,
    "LIT-PCBA official page data content table; Shen et al. 2025 Methods 'Datasets'",
    ["hitdisc-20261022-source-litpcba-page", "hitdisc-20261022-source-shen2025"],
    ("Read both totals from the two pinned artifacts: the page gives 7761 and 382674, Shen et al. "
     "give 10030 and 2798737.")))
note_change("F2 both artifact hashes now named in the LIT-PCBA totals-conflict concern")

# =============================== F4/F6/F3: result-level corrections
nef_fixed = litpcba_warned = zero_warned = 0
for r in recs:
    if r["kind"] != "result":
        continue
    a = r["attributes"]
    loc = a["source_locator"]
    # F4: the three normalised merged-library columns
    m = re.match(r"Sheet 'S8', row with Workflow = (\d+), column ([RST])\b", loc)
    if m:
        col = m.group(2)
        a["metric_qualifier"] = NEW_NEF_QUALIFIER[col]
        a["source_warnings"] = [NEF_WARNING]
        nef_fixed += 1
        continue
    # F6: own-selection score columns for workflows with no hit / no novel hit
    m = re.match(r"Sheet 'S8', row with Workflow = (\d+), column ([GHIJ])\b", loc)
    if m:
        wf, col = m.group(1), m.group(2)
        warn = list(a.get("source_warnings") or [])
        if col in "GHI" and wf in NO_HIT:
            warn.append(ZERO_SCORE_WARNING)
        if col == "J" and wf in NO_NOVEL:
            warn.append(NO_NOVEL_WARNING)
        if warn:
            a["source_warnings"] = warn
            zero_warned += 1
        continue
    # F3: the 84 LIT-PCBA results
    if a.get("source_table") == "Table 4":
        a["source_warnings"] = list(a.get("source_warnings") or []) + LITPCBA_WARNING
        litpcba_warned += 1

assert nef_fixed == 57, nef_fixed
assert litpcba_warned == 84, litpcba_warned
note_change(f"F4 corrected metric_qualifier and source_warnings on {nef_fixed} normalised "
            "merged-library results")
note_change(f"F3 added the leakage-audit and ratio-conflict warnings to {litpcba_warned} "
            "LIT-PCBA results")
note_change(f"F6 added the no-hit warning to {zero_warned} CACHE own-selection score results")

new_claims.append(correction_claim(
    "hitdisc-cache-nef-qualifier",
    "CACHE #3 normalised merged-library results: metric_qualifier corrected to the stored formula",
    ("The workbook stores these cells as 1000*N/L, 1000*O/L and R+S, so each is confirmed Tier 1 or "
     "Tier 2 hits per 1000 compounds predicted active. The previous qualifiers said only "
     "'normalised value' and hid the per-1000 scaling. Affects the 57 results on columns R, S and "
     "T of sheet S8."),
    "hitdisc-20261022-protocol-cache3-merged-library", "attributes.metric_qualifier",
    ("Normalised Tier 1 value / Normalised Tier 2 value / Sum of the normalised Tier 1 and Tier 2 "
     "values for the workflow's predicted-active compounds on the merged library"),
    " | ".join(NEW_NEF_QUALIFIER[c] for c in "RST"),
    "Sheet 'S8', columns R, S and T; the stored cell formulas in xl/worksheets/sheet9.xml",
    ["hitdisc-20261022-source-cache3-si002", "hitdisc-20261022-source-cache3"],
    ("Read the stored formulas from xl/worksheets/sheet9.xml of the pinned workbook: R is "
     "1000*N/L, S is 1000*O/L and T is R+S.")))

# =============================== F4: protocol corrections
p = by_id["hitdisc-20261022-protocol-cache3-merged-library"]
pa = p["attributes"]
prev_lims = list(pa["limitations"])
lims = []
for lim in prev_lims:
    if lim.startswith("The two normalised columns are labelled as counts of hits"):
        lims.append(MERGED_LABEL_FIX)
    elif lim.startswith("Predicting the merged library is not the same task"):
        lims.append(MERGED_NOT_RATES_FIX)
    else:
        lims.append(lim)
lims.append(CACHE_FIG6_LIMITATION)
pa["limitations"] = lims
prev_md = pa["metric_definition"]
pa["metric_definition"] = MERGED_METRIC_DEFINITION
new_claims.append(correction_claim(
    "hitdisc-cache-merged-protocol",
    "CACHE #3 merged-library protocol: normalised columns described by their stored formula",
    ("The protocol said the counts 'are not hit rates' and left the label-versus-caption "
     "disagreement unresolved. The stored formulas resolve it: columns R, S and T are rates."),
    "hitdisc-20261022-protocol-cache3-merged-library",
    "attributes.metric_definition and attributes.limitations",
    prev_md + " || " + json.dumps(prev_lims, ensure_ascii=False),
    MERGED_METRIC_DEFINITION + " || " + json.dumps(lims, ensure_ascii=False),
    ("Sheet 'S8' columns R, S and T and their stored formulas; article Figure 6 caption and Results "
     "'Trends and Strategies from the Best Performing Computational Workflows'"),
    ["hitdisc-20261022-source-cache3-si002", "hitdisc-20261022-source-cache3"],
    ("Read the stored cell formulas and compared them with the Figure 6 caption and with the "
     "Results section's own description of the three panels.")))
note_change("F4 corrected the merged-library protocol's metric_definition and two limitations, "
            "and added the Figure 6 inconsistency")

p = by_id["hitdisc-20261022-protocol-cache3-own-selection"]
pa = p["attributes"]
prev_lims = list(pa["limitations"])
lims = []
for lim in prev_lims:
    if lim.startswith("The source prints no per-workflow hit rate"):
        lims.append(OWN_SELECTION_HITRATE_FIX)
    else:
        lims.append(lim)
lims.append(OWN_SELECTION_ZERO_LIMITATION)
lims.append(CACHE_FIG6_LIMITATION)
pa["limitations"] = lims
new_claims.append(correction_claim(
    "hitdisc-cache-own-protocol",
    "CACHE #3 own-selection protocol: hit-rate limitation corrected",
    ("The protocol said the source prints no per-workflow hit rate. It prints none for this arm, "
     "but columns R, S and T of sheet S8 are per-workflow rates for the merged-library arm."),
    "hitdisc-20261022-protocol-cache3-own-selection", "attributes.limitations",
    json.dumps(prev_lims, ensure_ascii=False), json.dumps(lims, ensure_ascii=False),
    "Sheet 'S8' columns D, E, R, S and T and their stored formulas",
    ["hitdisc-20261022-source-cache3-si002", "hitdisc-20261022-source-cache3"],
    "Read columns D and E and the stored formulas of columns R, S and T."))
note_change("F6 added the no-hit-to-score limitation to the own-selection protocol")

# =============================== F7: the WF1696 wording
for rid, field in (("hitdisc-20261022-use-case-summary", "value"),
                   ("hitdisc-20261022-use-case-mapping-cache3-merged-library", "rationale")):
    r = by_id[rid]
    a = r["attributes"]
    target = "value" if field == "value" else "rationale"
    before = a[target]
    after = before.replace(WF1696_WRONG, WF1696_RIGHT).replace(WF1696_WRONG_J, WF1696_RIGHT_J)
    assert after != before, rid
    a[target] = after
    new_claims.append(correction_claim(
        "hitdisc-wf1696-wording-" + rid,
        f"{rid}: WF1696 wording corrected to the source's own",
        ("'Significantly more hits than any other' is what the article says of WF1715's "
         "own-selection aggregated score. Of WF1696 it says it 'did better than any other method "
         "in retrieving hits from the collection of all molecules selected in Round 1'."),
        rid, "attributes." + target, before, after,
        ("Herasymenko et al. 2026, Results 'Trends and Strategies from the Best Performing "
         "Computational Workflows'"),
        ["hitdisc-20261022-source-cache3"],
        ("Read both sentences in the pinned article: 'significantly more hits' belongs to WF1715 "
         "and Figure 6b, not to WF1696.")))
note_change("F7 corrected the WF1696 wording in the summary claim and the merged-library judgement")

# =============================== F9: evidence_checked points at this review
uc = next(r for r in recs if r["kind"] == "use_case")
prev = json.dumps(uc["attributes"]["evidence_checked"], ensure_ascii=False)
uc["attributes"]["evidence_checked"]["records"] = (
    uc["attributes"]["evidence_checked"]["records"] + [REVIEW_DOC])
new_claims.append(correction_claim(
    "hitdisc-evidence-checked",
    "Hit-discovery use case: evidence_checked names this review",
    "The pass's dated review is added to evidence_checked.records, as docs/use-cases.md requires.",
    uc["id"], "attributes.evidence_checked", prev,
    json.dumps(uc["attributes"]["evidence_checked"], ensure_ascii=False),
    REVIEW_DOC, ["hitdisc-20261022-source-shen2025"],
    "Checked the field against the requirement in docs/use-cases.md."))
note_change("F9 added the dated review to the use case's evidence_checked.records")

# =============================== review blocks and statuses
RESULT_KEY = {}
for r in recs:
    if r["kind"] != "result":
        continue
    a = r["attributes"]
    if a.get("source_table") in ("Table 1", "Table 2", "Table 3", "Table 4", "Table 5"):
        RESULT_KEY[r["id"]] = ("shen-table", SHA["shen"])
    elif a.get("source_table") == "Table S8":
        RESULT_KEY[r["id"]] = ("s8", SHA["si002"])
    else:
        RESULT_KEY[r["id"]] = ("kim-text", SHA["kim"])

SOURCE_OF = {
    "hitdisc-20261022-source-shen2025": SHA["shen"],
    "hitdisc-20261022-source-kim2026": SHA["kim"],
    "hitdisc-20261022-source-cache3": SHA["cache3"],
    "hitdisc-20261022-source-cache3-si002": SHA["si002"],
    "hitdisc-20261022-source-litpcba-audit": SHA["audit"],
    "hitdisc-20261022-source-litpcba-page": SHA["page"],
    "hitdisc-20261022-source-dude2012": SHA["dude"],
    "hitdisc-20261022-source-mfpcba2023": SHA["mfpcba"],
    "hitdisc-20261022-source-chen2019": SHA["chen"],
}

JUDGEMENTS = {}
for r in recs:
    if r["kind"] == "claim" and str(r["attributes"].get("field", "")).startswith("links:assessed_by:"):
        pid = r["attributes"]["value"]
        JUDGEMENTS[r["id"]] = pid
evals_by_protocol = {}
for r in recs:
    if r["kind"] == "evaluation":
        pid = r["attributes"]["protocol"]
        evals_by_protocol.setdefault(pid, []).append(r["id"])

for r in recs:
    kind, a = r["kind"], r["attributes"]
    if kind == "result":
        key, sha = RESULT_KEY[r["id"]]
        a["review"] = review_block(key, sha, URL[sha], TRANSCRIPTION_NOTE)
        r["status"] = "source_checked"
    elif kind == "source":
        sha = SOURCE_OF[r["id"]]
        a["review"] = review_block("hash", sha, URL[sha],
                                   "Artifact re-downloaded on 2026-10-22 and its SHA-256 matched "
                                   "the pinned value. Content not re-published.")
        r["status"] = "source_checked"
    elif kind in ("evaluation", "configuration", "protocol", "dataset", "dataset_subset",
                  "benchmark", "method", "use_case"):
        sha = SOURCE_OF.get((r["source_ids"] or [None])[0], SHA["shen"])
        key = "scope"
        a["review"] = review_block(key, sha, URL[sha],
                                   "Record checked against the pinned source and the record "
                                   "contract. Transcription checked; not reproduced and not "
                                   "reviewed by a human scientist.")
        if r["status"] != "discovered":
            r["status"] = "source_checked"
    elif kind == "claim":
        sha = SOURCE_OF.get((r["source_ids"] or [None])[0], SHA["shen"])
        a["review"] = review_block("scope", sha, URL[sha],
                                   "Claim checked against the pinned source. Every figure it "
                                   "states was matched to a result record in this batch.")
        if r["id"] in JUDGEMENTS:
            pid = JUDGEMENTS[r["id"]]
            a["reviewed_evaluations"] = sorted(evals_by_protocol.get(pid, []))
        r["status"] = "source_checked"

for c in new_claims:
    recs.append(c)

by_id2 = {}
for r in recs:
    assert r["id"] not in by_id2, r["id"]
    by_id2[r["id"]] = r

with open(BATCH, "w") as f:
    for r in recs:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")

print(f"records: {len(recs)} (added {len(new_claims)} metadata-correction claims)")
for c in changes:
    print(" -", c)
print()
for c in new_claims:
    print("   new claim:", c["id"], "|", c["name"])
print()
import collections
print(collections.Counter(r["status"] for r in recs))
print(collections.Counter(r["kind"] for r in recs))
