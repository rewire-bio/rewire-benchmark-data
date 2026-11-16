#!/usr/bin/env python3
"""Write the review pass's own review object onto every result and claim in the batch, and
apply the two locator corrections this review found.

Follows the convention of the reviewed batches already in the store (for example
data/omics/benchbench-cloning-20261106): the reviewer replaces `attributes.review` on the
result and claim records and leaves the extractor's review object on the other kinds, which
records who made each record rather than who checked its value.

Usage: python3 -I review/apply_review.py   (run from the batch folder)
Rewrites batch.jsonl in place, keeping line order and key order.
"""

import json
import os
import sys

BATCH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATE = "2026-11-16"
REVIEWED_AT = "2026-11-16T01:30:00Z"
REVIEWER = ["claude"]
REVIEWER_NOTE = ("Claude review agent, independent of the extractor; no human review claimed. "
                 "Transcription was checked against the pinned artifacts; nothing was "
                 "reproduced and no value was recomputed.")

XML_SHA = "8ff2184c07f5e6807af0b9d5103d669e1920e735ab5a4b1ea856c070077ae1e0"
XML_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10622914/fullTextXML"
SI_SHA = "e9ea2399b54c66f17b6088f205e17242521bd31fcb6b608841cdaf69cf363b16"
SI_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10622914/supplementaryFiles"
API_SHA = "f9072577d1af56d94f5a9696d50d623b1e8fa8ab7934ced515689971cc642414"
API_URL = "https://api.biorxiv.org/details/biorxiv/10.1101/2022.08.22.504706"

COMMON = ("Independent review pass by a different agent from the extractor, with its own script "
          "(review/recheck_values.py), which does not import extract/parse_values.py and does not "
          "read extract/values.json. The published article XML and the bioRxiv details API "
          "response were re-downloaded and matched their pinned hashes; the SI Appendix PDF was "
          "re-downloaded as the member of a freshly built Europe PMC zip (a third distinct zip "
          "hash, c7a1b20e8796c4bd384ba6f0308134e32a66e40dc881b0c1e3d0201da26e8498) and the PDF "
          "member matched. Every archived gz in artifacts/ decompresses to the hash its source "
          "record pins, and the text layer in extract/ regenerates byte for byte from the "
          "archived PDF with pdftotext -layout, poppler 26.08.0. "
          "npm run batch -- check-values reproduced the extractor's figures: 6 in_cell, "
          "17 locator_not_parsed, no overclaimed_in_row.")

TABLE_NOTE = (COMMON + " The six Table S2 cells were re-read by column position: the character "
              "span of each column's header label was taken from the printed header line, and a "
              "cell is the one number right of the row label whose span overlaps that column's "
              "span, so a value from the neighbouring column cannot match. The locator's row and "
              "column names were checked against the ones read. A mutation test "
              "(review/mutation_test.py) confirmed the check fails on a swapped printed value and "
              "on a swapped locator column.")

PROSE_NOTE = (COMMON + " The article was parsed with xml.etree, the section tree read from its "
              "own <sec><title> elements, and each value checked inside the section its locator "
              "names: the value together with the label the locator names must occur exactly once "
              "in that section and exactly once in the whole body, and a negative control with the "
              "value moved to a neighbouring label must be absent. Whitespace is dropped before "
              "comparison, because the JATS marks up italics, maths and superscripts inside these "
              "sentences, so the spacing is an artefact of the markup and not of the page. A "
              "mutation test (review/mutation_test.py) confirmed the check fails on a changed "
              "value, including the one value the bioRxiv v3 prints differently.")

CLAIM_NOTE = (COMMON + " Each claim was read against its own source_locator in the re-retrieved "
              "artifacts. Two locators did not cover the whole claim and were corrected in this "
              "pass: the comparator bound claim now also names Materials and Methods, 'Variant "
              "Effect Prediction', where phyloP x LD, abs(phyloP) x LD, phastCons x LD and the "
              "baseline LD Score are defined, and the motif claim now also names Materials and "
              "Methods, 'Motif Analysis', where the 1,000 bp promoter window and the repeat and "
              "coding exon filter are printed. The central finding was confirmed independently: "
              "the whole JATS document holds zero table-wrap and zero table elements, and the SI "
              "Appendix figure pages print no comparator value in their text layer, only axis "
              "ticks, GPN score bin edges, threshold quantiles, method legends and the per-class "
              "variant counts of the Figure S9 subplot titles.")

TABLE_S2_RESULTS = {
    "gpn-paper-20261116-result-perplexity-chromosome-wide-repeat-weight-0",
    "gpn-paper-20261116-result-perplexity-chromosome-wide-repeat-weight-0-1",
    "gpn-paper-20261116-result-perplexity-chromosome-wide-repeat-weight-1",
    "gpn-paper-20261116-result-perplexity-non-repeat-repeat-weight-0",
    "gpn-paper-20261116-result-perplexity-non-repeat-repeat-weight-0-1",
    "gpn-paper-20261116-result-perplexity-non-repeat-repeat-weight-1",
}

# Claims whose value quotes a printed number or string that was checked character by character.
CLAIMS_WITH_PRINTED_VALUES = {
    "gpn-paper-20261116-claim-alignment-coverage",
    "gpn-paper-20261116-claim-comparator-bound-gwas",
    "gpn-paper-20261116-claim-kmer-baseline",
    "gpn-paper-20261116-claim-motif-count",
    "gpn-paper-20261116-claim-preprint-value-difference",
    "gpn-paper-20261116-claim-score-correlation-phastcons",
    "gpn-paper-20261116-claim-score-correlation-phylop",
    "gpn-paper-20261116-claim-training-compute",
    "gpn-paper-20261116-claim-training-data",
    "gpn-paper-20261116-claim-version-history",
}

# Claims checked against an artifact other than the published article XML.
CLAIM_ARTIFACT = {
    "gpn-paper-20261116-claim-version-history": (API_SHA, API_URL),
    "gpn-paper-20261116-claim-training-data": (SI_SHA, SI_URL),
}

RESULT_NOTES = {
    "gpn-paper-20261116-result-perplexity-chromosome-wide-single-species":
        "Materials and Methods prints 'a higher test perplexity of 3.13 (3.17 on nonrepeat "
        "regions)' without naming Table S2's column headings. The review upheld the extractor's "
        "mapping of the unqualified figure to the chromosome-wide protocol: Table S2's caption "
        "calls the same quantity 'genome-wide perplexity' against 'perplexity for non-repetitive "
        "regions', and 3.13 is higher than all three chromosome-wide cells while 3.17 is higher "
        "than all three non-repeat cells, which is what 'higher' in that sentence refers to.",
    "gpn-paper-20261116-result-perplexity-non-repeat-single-species":
        "The non-repeat half of 'a higher test perplexity of 3.13 (3.17 on nonrepeat regions)'. "
        "See the chromosome-wide result for why the review upheld the mapping.",
    "gpn-paper-20261116-result-rare-vs-common-odds-ratio-gpn":
        "Metric and printed value upheld. The body text calls the quantity a fold enrichment, but "
        "Materials and Methods, 'Variant Effect Prediction' states 'We calculated the odds ratio "
        "and P -value with Fisher's exact test' and the Figure 5 C caption the sentence cites "
        "reads 'Contingency table and odds ratio showing enrichment of putative functional GPN "
        "scores in rare (AC = 1 ) vs. common (AF >= 5 % ) variants', so the number is an odds "
        "ratio from a two by two table. printed_value keeps the '-fold' the page prints, as a "
        "percent sign would be kept. Materials and Methods defines common as 'allele frequency "
        "above 5%' while the caption prints 'AF >= 5%'; the qualifier follows the caption, which "
        "is the panel the sentence cites.",
    "gpn-paper-20261116-result-gwas-hit-odds-ratio-gpn-x-ld":
        "Metric and printed value upheld on the same evidence as the rare against common result: "
        "the sentence itself opens 'by analyzing odds ratios ( Fig. 6 C )', the Figure 6 C caption "
        "reads 'Contingency table and odds ratio', and Materials and Methods names Fisher's exact "
        "test. denominator stays unreported: the sentence names neither variant set, and although "
        "'GPN x LD achieves much higher odds ratios when considering the full variant set ( Fig. 6 "
        "E )' implies the 10.3-fold is the 453,281 aligned variants of Figure 6 D, the paper does "
        "not say so and the review did not infer it.",
    "gpn-paper-20261116-result-gene-region-accuracy-cds":
        "'achieving the highest accuracy on CDS (96%)' upheld as metric accuracy with the class in "
        "metric_qualifier. The paper gives no per-class definition and Figure 2 B, the confusion "
        "matrix the figure would settle it from, prints no values, so the review did not infer "
        "recall. The ambiguity stays in the result's scope note.",
    "gpn-paper-20261116-result-gene-region-accuracy-ncrna":
        "'the lowest on ncRNA (51%), the least frequent class' upheld on the same reading as the "
        "CDS result.",
}

CLAIM_NOTES = {
    "gpn-paper-20261116-claim-comparator-bound-gwas":
        "source_locator extended in this review pass. The bound itself is printed in the Results "
        "sentence, but the four comparator methods the claim names are defined in Materials and "
        "Methods, 'Variant Effect Prediction' ('We similarly defined phyloP x LD ..., abs(phyloP) "
        "x LD and phastCons x LD. We considered the baseline LD Score'), which the locator did not "
        "name. The Figure 6 D caption names no method.",
    "gpn-paper-20261116-claim-motif-count":
        "source_locator extended in this review pass. 'approximately a hundred and sixty motifs' "
        "and the four examples are in the Results section the locator names, but the 1,000 bp "
        "promoter window and the repeat and coding exon filter are printed in Materials and "
        "Methods, 'Motif Analysis', which the locator did not name.",
    "gpn-paper-20261116-claim-score-correlation-phylop":
        "Upheld as a claim rather than a result: it measures agreement between two scores, not a "
        "model's performance on a protocol. The paper prints 'r = 0.22' with no statement of "
        "whether r is Pearson or Spearman, and the review did not infer one.",
    "gpn-paper-20261116-claim-score-correlation-phastcons":
        "Upheld as a claim rather than a result, on the same reading as the phyloP correlation.",
    "gpn-paper-20261116-claim-preprint-value-difference":
        "Checked against both pinned artifacts. The review confirmed with its own script that "
        "'median = 1.10', 'median = 2.81', 'median = 3.14' and 'p -values < 10 -239' occur in the "
        "bioRxiv v3 body and not in the published body, that '264 genes', '471 transcripts', "
        "'CDS1', 'CDS2' and 'CDS3' occur in the published body and not in v3, and that the twelve "
        "other printed strings this batch records occur verbatim in v3 as well. A measurement over "
        "a different region, so a version difference and not a correction.",
    "gpn-paper-20261116-claim-version-history":
        "Checked field by field against the re-downloaded bioRxiv details API response, which gave "
        "identical bytes: versions 1, 2 and 3 dated 2022-08-23, 2023-04-12 and 2023-08-04, the "
        "three titles as quoted, licence cc_by_nc_nd on all three and published DOI "
        "10.1073/pnas.2311219120.",
    "gpn-paper-20261116-claim-training-data":
        "The eight assemblies were checked against the SI Appendix Table S1 text layer. The "
        "accessions print with a space where the accession carries an underscore (GCF 000001735.4) "
        "because the PDF typesets them that way; the underscore in the record is the only change "
        "made to a printed string in this batch and the review accepts it as a typesetting "
        "artefact, not a transcription error.",
    "gpn-paper-20261116-claim-figure-only-comparisons":
        "Confirmed independently. The whole JATS document, parsed with xml.etree, holds zero "
        "table-wrap and zero table elements, and the SI Appendix figure pages print no comparator "
        "value in their text layer. The only values there are axis ticks, the GPN score bin edges "
        "of the Figure S7 legend, threshold quantiles, the method legends of Figures S11 and S12 "
        "and the per-class rare and common counts in the Figure S9 subplot titles. No comparator "
        "value the extractor missed was found.",
    "gpn-paper-20261116-claim-species-scope":
        "Confirmed by reading the whole article body: every evaluation is in Arabidopsis thaliana "
        "and no human variant is scored anywhere in it. Worth keeping, because the stored GPN "
        "family record carries human results from other groups.",
}

LOCATOR_FIXES = {
    "gpn-paper-20261116-claim-comparator-bound-gwas": (
        "Results, 'Enrichment of GWAS hits in regions with low GPN scores', sentence beginning "
        "\"In particular, by analyzing odds ratios\"; Figure 6 D caption",
        "Results, 'Enrichment of GWAS hits in regions with low GPN scores', sentence beginning "
        "\"In particular, by analyzing odds ratios\"; Figure 6 D caption; Materials and Methods, "
        "'Variant Effect Prediction', sentences beginning \"We similarly defined phyloP x LD\" and "
        "\"We considered the baseline LD Score\", where the four comparator methods are defined",
    ),
    "gpn-paper-20261116-claim-motif-count": (
        "Results, 'DNA Motifs Revealed by High-Confidence Model Predictions'; Figure 3 B caption; "
        "SI Appendix Figure S5",
        "Results, 'DNA Motifs Revealed by High-Confidence Model Predictions'; Figure 3 B caption; "
        "SI Appendix Figure S5; Materials and Methods, 'Motif Analysis', sentence beginning \"An "
        "adaptation of TF-MoDISco was run\", for the 1,000 bp promoter window and the repeat and "
        "coding exon filter",
    ),
}


def review_for(rec):
    rid = rec["id"]
    if rec["kind"] == "result":
        if rid in TABLE_S2_RESULTS:
            method = ["independent-cell-check", "pdf-text-parse", "source-hash-verification"]
            note_base, sha, url = TABLE_NOTE, SI_SHA, SI_URL
        else:
            method = ["independent-cell-check", "automated-source-review",
                      "source-hash-verification"]
            note_base, sha, url = PROSE_NOTE, XML_SHA, XML_URL
        note = RESULT_NOTES.get(rid, "Printed value, numeric value, metric concept, qualifier, "
                                     "direction, unit and the configuration and protocol it hangs "
                                     "on all match the source. No field is null that the source "
                                     "states.")
    else:
        method = ["automated-source-review", "source-hash-verification"]
        if rid in CLAIMS_WITH_PRINTED_VALUES:
            method.insert(0, "independent-cell-check")
        note_base = CLAIM_NOTE
        sha, url = CLAIM_ARTIFACT.get(rid, (XML_SHA, XML_URL))
        note = CLAIM_NOTES.get(rid, "The claim's value was read against its own source_locator in "
                                    "the re-retrieved artifact and matches it. Nothing in the "
                                    "value goes beyond what the locator prints.")
    return {
        "method": method,
        "method_note": note_base,
        "reviewer": REVIEWER,
        "reviewer_note": REVIEWER_NOTE,
        "date": DATE,
        "reviewed_at": REVIEWED_AT,
        "artifact_sha256": sha,
        "retrieval_url": url,
        "note": note,
    }


def main():
    path = os.path.join(BATCH, "batch.jsonl")
    lines = open(path).read().splitlines()
    out = []
    touched = {"result": 0, "claim": 0, "locator": 0}
    for line in lines:
        rec = json.loads(line)
        if rec["kind"] in ("result", "claim"):
            rec["attributes"]["review"] = review_for(rec)
            touched[rec["kind"]] += 1
        if rec["id"] in LOCATOR_FIXES:
            old, new = LOCATOR_FIXES[rec["id"]]
            got = rec["attributes"]["source_locator"]
            if got != old:
                print(f"locator for {rec['id']} is not what this script expects:\n  {got}")
                return 1
            rec["attributes"]["source_locator"] = new
            touched["locator"] += 1
        out.append(json.dumps(rec, ensure_ascii=False, sort_keys=True))
    with open(path, "w") as fh:
        fh.write("\n".join(out) + "\n")
    print(f"reviewed {touched['result']} results and {touched['claim']} claims; "
          f"{touched['locator']} locators corrected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
