#!/usr/bin/env python3
"""Parse every printed value this batch records from the pinned GPN sources.

Two sources carry values:

  artifacts/pnas-2311219120-si-appendix.pdf.gz  Table S2 (test perplexity), parsed from the
      pdftotext -layout text layer kept at extract/si-appendix.layout.txt.
  artifacts/pnas-2311219120.fulltext.xml.gz     the published article body, where every other
      value is printed in prose, not in a table. The article has no table-wrap element at all.

Prose values are taken by matching the whole printed sentence, so a changed sentence fails the
parse instead of silently moving a number. Every row label and every sentence is asserted.

Usage: python3 extract/parse_values.py    (run from the batch folder)
Writes extract/values.json.
"""

import gzip
import hashlib
import html
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BATCH = os.path.dirname(HERE)
ART = os.path.join(BATCH, "artifacts")

SI_PDF_SHA = "e9ea2399b54c66f17b6088f205e17242521bd31fcb6b608841cdaf69cf363b16"
XML_SHA = "8ff2184c07f5e6807af0b9d5103d669e1920e735ab5a4b1ea856c070077ae1e0"
BIORXIV_SHA = "4faeb24f27e8db7fd57f65f10e2885e9bea82f539b6acf37b356d2bd5864ef15"


def read_gz(name, expect_sha):
    raw = gzip.decompress(open(os.path.join(ART, name), "rb").read())
    got = hashlib.sha256(raw).hexdigest()
    assert got == expect_sha, f"{name}: sha256 {got} != {expect_sha}"
    return raw


def body_text(xml_bytes):
    x = xml_bytes.decode("utf-8")
    b = x[x.index("<body>"):x.index("</body>")]
    t = re.sub(r"<[^>]+>", " ", b)
    t = html.unescape(t)
    return re.sub(r"\s+", " ", t).strip()


def table_s2(layout_text):
    """Table S2: three rows, two value columns. Row labels and the header are asserted."""
    lines = layout_text.splitlines()
    start = next(i for i, l in enumerate(lines) if l.strip().startswith("Table S2: Test perplexity"))
    header = next(l for l in lines[start:start + 20] if "Chromosome-wide" in l)
    assert re.search(r"Model\s+Chromosome-wide\s+Non-repeat regions", header), header
    want = ["Repeat weight 1", "Repeat weight 0.1", "Repeat weight 0"]
    rows = []
    for label in want:
        hits = [l for l in lines[start:start + 20]
                if re.match(r"\s*" + re.escape(label) + r"\s+\d", l)]
        assert len(hits) == 1, f"Table S2 row {label!r}: {len(hits)} matching lines"
        cells = hits[0].strip()[len(label):].split()
        assert len(cells) == 2, f"Table S2 row {label!r} cells {cells}"
        rows.append({"row": label, "chromosome_wide": cells[0], "non_repeat": cells[1]})
    # The three labels must be distinct lines, and "Repeat weight 0" must not have matched 0.1.
    assert [r["row"] for r in rows] == want
    assert rows[1]["chromosome_wide"] != rows[2]["chromosome_wide"] or rows[1]["non_repeat"] != rows[2]["non_repeat"]
    return rows


# Each entry: key, the sentence that must appear verbatim in the article body, and the values
# this batch takes from it with the label each value carries.
SENTENCES = [
    ("single_species_perplexity",
     "This model obtained a higher test perplexity of 3.13 (3.17 on nonrepeat regions).",
     {"chromosome_wide": "3.13", "non_repeat": "3.17"}),
    ("region_classification",
     "To quantify GPN’s ability to distinguish genomic regions, we trained a logistic regression "
     "classifier using the averaged embeddings as features, achieving the highest accuracy on CDS "
     "(96%) and the lowest on ncRNA (51%), the least frequent class.",
     {"CDS": "96%", "ncRNA": "51%"}),
    ("kmer_classification",
     "This level of classification accuracy cannot be achieved merely through k -mer frequencies "
     "( k = 3 : 8% to 70%; k = 6 : 15% to 67%; see SI Appendix , Fig. S1 ).",
     {"k3_range": "8% to 70%", "k6_range": "15% to 67%"}),
    ("positional_perplexity",
     "Across a 1-Mb region in the test chromosome (containing 264 genes and 471 transcripts), model "
     "perplexities in splice donors (median = 1.02 ), splice acceptors (median = 1.03), start codons "
     "(median = 1.08 ), CDS2 (median = 2.24 ), CDS1 (median = 2.44 ), CDS3 (median = 2.79 ), and stop "
     "codons (median = 2.8 ) are significantly smaller than those in intergenic and intronic regions "
     "(median = 3.24 , all Mann–Whitney P -values < 10 − 17 , SI Appendix , Fig. S4 ).",
     {"splice donor": "1.02", "splice acceptor": "1.03", "start codon": "1.08", "CDS2": "2.24",
      "CDS1": "2.44", "CDS3": "2.79", "stop codon": "2.8", "intergenic and intronic": "3.24"}),
    ("repeat_below_missense_decile",
     "More precisely, in models with 0.0 and 0.1 down-weighting, respectively, 8% and 9% of repeat "
     "variants are ranked before the first decile of missense variants.",
     {"repeat weight 0": "8%", "repeat weight 0.1": "9%"}),
    ("repeat_below_missense_decile_baseline",
     "These represent a substantial decrease compared to the 27% observed in the model without any "
     "down-weighting ( SI Appendix , Fig. S6 B , Fisher’s exact test P < 10 − 300 ).",
     {"repeat weight 1": "27%"}),
    ("rare_vs_common_odds_ratio",
     "Putative functional SNPs, defined as the lowest 0.1% of GPN scores, exhibit a 5.5-fold "
     "enrichment in rare variants ( Fig. 5 C ); see SI Appendix , Fig. S8 for different allele "
     "frequency thresholds.",
     {"GPN": "5.5-fold"}),
    ("gwas_odds_ratio",
     "In particular, by analyzing odds ratios ( Fig. 6 C ), we found that SNPs with the lower 1% of "
     "GPN × LD scores are 10.3-fold enriched in GWAS hits compared to the upper 99% of GPN × LD "
     "scores, while less than 7.5-fold enrichment was observed for other methods ( Fig. 6 D ); see SI "
     "Appendix , Fig. S11 for different thresholds.",
     {"GPN x LD": "10.3-fold", "other methods bound": "less than 7.5-fold"}),
    ("score_correlations",
     "In fact, GPN scores are only weakly correlated with phyloP ( r = 0.22 , P < 10 − 300 ) and "
     "phastCons ( r = 0.13 , P < 10 − 300 ).",
     {"phyloP": "0.22", "phastCons": "0.13"}),
    ("alignment_coverage",
     "A notable advantage of GPN is that it is able to score variants that could not be scored by "
     "phyloP and phastCons due to unsuccessful whole-genome alignment (14.2% of all variants).",
     {"unalignable": "14.2%"}),
    ("gwas_variant_counts",
     "( D ) Comparison of odds ratios obtained with different models ( n = 453 , 281 variants with "
     "whole-genome alignment). ( E ) Odds ratios with the full variant set ( n = 510 , 462 ).",
     # The XML marks up the thousands separator, so the extracted text reads "453 , 281" where
     # the page prints "453,281". These counts are recorded as integer denominators, not as
     # printed values, so the spacing does not reach a record.
     {"aligned": "453 , 281", "full": "510 , 462"}),
]

# Sentences whose numbers differ between the published article and bioRxiv v3.
BIORXIV_SENTENCES = [
    ("positional_perplexity",
     "Across the test chromosome, model perplexities in splice acceptors (median = 1.03), splice "
     "donors (median = 1.02), start codons (median = 1.10), and stop codons (median = 2.81) are "
     "significantly smaller than those in intergenic and intronic regions (median = 3.14, all "
     "Mann–Whitney p -values < 10 − 239 , Supplementary Figure S4).",
     {"splice acceptor": "1.03", "splice donor": "1.02", "start codon": "1.10",
      "stop codon": "2.81", "intergenic and intronic": "3.14"}),
]

# Printed values the published article and bioRxiv v3 share verbatim, checked so the batch can
# say which numbers the version change did and did not touch.
SHARED_WITH_BIORXIV = ["5.5-fold", "10.3-fold", "less than 7.5-fold", "96%", "51%", "14.2%",
                       "r = 0.22", "r = 0.13", "3.13", "3.17", "8% and 9%", "27%"]


def take(text, sentences, where):
    out = {}
    for key, sentence, values in sentences:
        assert sentence in text, f"{where}: sentence not found for {key!r}:\n{sentence}"
        assert text.count(sentence) == 1, f"{where}: sentence appears more than once for {key!r}"
        for label, value in values.items():
            assert value in sentence, f"{where}: {value!r} not in the {key!r} sentence"
        out[key] = {"sentence": sentence, "values": values}
    return out


def main():
    layout = open(os.path.join(HERE, "si-appendix.layout.txt")).read()
    read_gz("pnas-2311219120-si-appendix.pdf.gz", SI_PDF_SHA)  # the text layer's source
    article = body_text(read_gz("pnas-2311219120.fulltext.xml.gz", XML_SHA))
    preprint = body_text(read_gz("biorxiv-2022.08.22.504706v3.source.xml.gz", BIORXIV_SHA))

    assert "<table-wrap" not in read_gz("pnas-2311219120.fulltext.xml.gz", XML_SHA).decode("utf-8"), \
        "the published article is expected to print no tables in the main text"

    out = {
        "table_s2": table_s2(layout),
        "prose": take(article, SENTENCES, "published article"),
        "biorxiv_v3_prose": take(preprint, BIORXIV_SENTENCES, "bioRxiv v3"),
        "shared_with_biorxiv_v3": {v: (v in preprint) for v in SHARED_WITH_BIORXIV},
    }
    for value, shared in out["shared_with_biorxiv_v3"].items():
        assert shared, f"{value!r} was expected in bioRxiv v3 as well"

    path = os.path.join(HERE, "values.json")
    with open(path, "w") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    print(f"wrote {path}")
    print(json.dumps(out["table_s2"], indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
