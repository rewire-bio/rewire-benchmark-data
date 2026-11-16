#!/usr/bin/env python3
"""Build batch.jsonl for the GPN paper batch (issue #226).

Reads extract/values.json, written by extract/parse_values.py from the pinned sources, and
emits one JSONL record per line, sorted by ID.

Usage: python3 build.py    (run from the batch folder)
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
VALUES = os.path.join(HERE, "extract", "values.json")
OUT = os.path.join(HERE, "batch.jsonl")

P = "gpn-paper-20261116-"
GPN = "regulatory-variant-20261009-model-gpn"  # existing family record, reused

DATE = "2026-11-16"
RETRIEVED = "2026-11-16T00:29:00Z"
RETRIEVED_SI = "2026-11-16T00:30:00Z"
RETRIEVED_BX = "2026-11-16T00:37:00Z"

SRC_PNAS = P + "source-pnas-2023"
SRC_SI = P + "source-pnas-2023-si-appendix"
SRC_BIORXIV = P + "source-biorxiv-v3"
SRC_VERSIONS = P + "source-biorxiv-version-list"

XML_SHA = "8ff2184c07f5e6807af0b9d5103d669e1920e735ab5a4b1ea856c070077ae1e0"
SI_SHA = "e9ea2399b54c66f17b6088f205e17242521bd31fcb6b608841cdaf69cf363b16"
BX_SHA = "4faeb24f27e8db7fd57f65f10e2885e9bea82f539b6acf37b356d2bd5864ef15"
VERSIONS_SHA = "f9072577d1af56d94f5a9696d50d623b1e8fa8ab7934ced515689971cc642414"

XML_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10622914/fullTextXML"
SI_ZIP_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10622914/supplementaryFiles"
BX_URL = "https://www.biorxiv.org/content/early/2023/08/04/2022.08.22.504706.source.xml"
VERSIONS_URL = "https://api.biorxiv.org/details/biorxiv/10.1101/2022.08.22.504706"

REVIEWER_NOTE = ("Claude (Opus 5) extraction agent. Extraction only: no independent review is "
                 "claimed, and a different agent reviews this batch.")
PARSE_NOTE = (
    "Extraction: the published article prints no tables in its main text, so Table S2 was parsed "
    "from the pdftotext -layout text layer of the pinned SI Appendix PDF (extract/si-appendix.layout.txt) "
    "by extract/parse_values.py with all three row labels and the header asserted, and every other "
    "value was taken from the article body by matching its whole printed sentence in the pinned "
    "Europe PMC JATS XML, so a changed sentence fails the parse."
)

FACETS = {"areas": ["dna-genomes"], "contexts": ["research"]}
FACETS_MODEL = {"areas": ["dna-genomes"], "contexts": ["research"], "method_types": ["foundation_model"]}


def review(sha, url, method, note=None):
    out = {
        "method": method,
        "method_note": PARSE_NOTE,
        "reviewer": ["claude"],
        "reviewer_note": REVIEWER_NOTE,
        "date": DATE,
        "artifact_sha256": sha,
        "retrieval_url": url,
    }
    if note:
        out["note"] = note
    return out


def rev_xml(note=None):
    return review(XML_SHA, XML_URL, ["transcription", "source-hash-verification"], note)


def rev_si(note=None):
    """For the six Table S2 cells and their evaluations, which extract/parse_values.py parsed."""
    return review(SI_SHA, SI_ZIP_URL,
                  ["deterministic-table-parse", "pdf-text-parse", "source-hash-verification"], note)


def rev_si_transcribed(note=None):
    """For records read off the SI text layer by hand, which no parser produced."""
    return review(SI_SHA, SI_ZIP_URL,
                  ["transcription", "pdf-text-parse", "source-hash-verification"], note)


def rec(kind, rid, name, description, attributes, links=(), sources=(SRC_PNAS,),
        status="source_checked", facets=None):
    return {
        "id": rid,
        "kind": kind,
        "name": name,
        "description": description,
        "status": status,
        "facets": facets or FACETS,
        "source_ids": list(sources),
        "links": [{"relation": r, "target_id": t} for r, t in links],
        "attributes": attributes,
    }


def main():
    v = json.load(open(VALUES))
    prose = v["prose"]
    out = []

    # ---------------------------------------------------------------- sources
    out.append(rec(
        "source", SRC_PNAS,
        "DNA language models are powerful predictors of genome-wide variant effects (PNAS 2023)",
        "Peer-reviewed article introducing GPN, a masked DNA language model trained on eight "
        "Brassicales genomes and evaluated on Arabidopsis thaliana variants.",
        {
            "url": XML_URL,
            "version": "PNAS 120(44) e2311219120, published 26 October 2023; Europe PMC full text JATS XML of PMC10622914",
            "retrieved_at": RETRIEVED,
            "artifact_sha256": XML_SHA,
            "doi": "10.1073/pnas.2311219120",
            "publication_status": "peer_reviewed",
            "licence": "CC BY-NC-ND 4.0",
            "article_licence": "CC BY-NC-ND 4.0 (https://creativecommons.org/licenses/by-nc-nd/4.0/), stated in the article permissions",
            "media_type": "application/xml",
            "artifact_format": "JATS XML",
            "original_url": "https://www.pnas.org/doi/10.1073/pnas.2311219120",
            "venue": "Proceedings of the National Academy of Sciences of the United States of America",
            "year": 2023,
            "retrieval_note": (
                "www.pnas.org returned HTTP 403 to a direct request for the article PDF and for the "
                "supplementary PDF, and the PMC PDF endpoint returned a proof-of-work interstitial "
                "rather than the file, so the Europe PMC full text XML is the pinned artifact. It was "
                "fetched twice on 2026-11-16 with identical bytes."
            ),
            "limitations": [
                "The published article prints no tables in its main text. Every comparison of GPN "
                "against phyloP, phastCons, abs(phyloP) and LD Score (Figures 5D, 6D, 6E and SI "
                "Appendix Figures S6, S8 to S12) is a bar chart with no values in the text layer, so "
                "those numbers are not in this batch.",
                "The Europe PMC rendering of the publisher's XML, not the publisher's own file; it "
                "carries the article text, figure captions and metadata but not the typeset page.",
            ],
            "review": review(XML_SHA, XML_URL, ["source-hash-verification", "automated-source-review"],
                             "Fetched twice on 2026-11-16 with identical bytes. The DOI, PMID 37883436, "
                             "PMC10622914, volume 120 issue 44 and the 2023-10-26 publication date were "
                             "read from the article metadata in the same file."),
        },
        status="source_checked",
    ))

    out.append(rec(
        "source", SRC_SI,
        "SI Appendix for PNAS 2023 GPN paper (Tables S1 to S3, Figures S1 to S12)",
        "The published supporting information, which holds the genome assembly list, the test "
        "perplexity table, the training hyperparameters and twelve supplementary figures.",
        {
            "url": SI_ZIP_URL,
            "version": "pnas.2311219120.sapp.pdf as served for PMC10622914, 18 pages, created 2023-09-22",
            "retrieved_at": RETRIEVED_SI,
            "artifact_sha256": SI_SHA,
            "doi": "10.1073/pnas.2311219120",
            "publication_status": "peer_reviewed",
            "licence": "CC BY-NC-ND 4.0",
            "media_type": "application/pdf",
            "artifact_format": "PDF",
            "artifact_member": "pnas.2311219120.sapp.pdf",
            "artifact_retrieval_endpoint": SI_ZIP_URL,
            "original_url": "https://www.pnas.org/doi/suppl/10.1073/pnas.2311219120/suppl_file/pnas.2311219120.sapp.pdf",
            "retrieval_note": (
                "The Europe PMC supplementaryFiles endpoint serves a zip built per request, so the zip "
                "hash is not stable: two downloads on 2026-11-16 gave "
                "c20ffb3f6f12bfd7b1dd96b7735dd52eb2c2f3c0298a745a03241ee0a09085cf and "
                "4b92429593be1cbd31983738ab46d6276151bd19858ef7b7151073395c0c8984. The pinned hash is "
                "that of the PDF member, which was identical in both. Direct requests to pnas.org and "
                "to the PMC /bin/ path returned HTTP 403 and 404."
            ),
            "extraction_method": (
                "pdftotext -layout (poppler 26.08.0) on the pinned PDF; the text layer is kept at "
                "extract/si-appendix.layout.txt, sha256 "
                "6ee1d0c99cc16aa2f5781755204665f0ee08a8f966a9a52c4e1e804ba3bf335a."
            ),
            "limitations": [
                "Figures S1 to S12 carry no values in their text layer beyond axis ticks and the "
                "per-class variant counts printed in the Figure S9 subplot titles, so the odds ratios "
                "they show are not extractable.",
                "Licensed CC BY-NC-ND 4.0. The PDF is archived here verbatim; the text layer in "
                "extract/ is a mechanical derivative kept so the parse can be rerun.",
            ],
            "review": review(SI_SHA, SI_ZIP_URL,
                             ["source-hash-verification", "pdf-text-parse", "automated-source-review"],
                             "The PDF member hash was confirmed identical across two downloads of the "
                             "generated zip on 2026-11-16, and the text layer was regenerated from the "
                             "pinned PDF with pdftotext -layout (poppler 26.08.0)."),
        },
        links=[("companion_of", SRC_PNAS)],
        sources=(SRC_PNAS,),
    ))

    out.append(rec(
        "source", SRC_BIORXIV,
        "DNA language models are powerful predictors of genome-wide variant effects (bioRxiv v3)",
        "The third and final preprint version of the GPN paper, kept for version history against "
        "the published article.",
        {
            "url": BX_URL,
            "version": "bioRxiv v3, posted 2023-08-04; publisher JATS source XML",
            "retrieved_at": RETRIEVED_BX,
            "artifact_sha256": BX_SHA,
            "doi": "10.1101/2022.08.22.504706",
            "publication_status": "preprint",
            "licence": "CC BY-NC-ND 4.0",
            "media_type": "application/xml",
            "artifact_format": "JATS XML",
            "original_url": "https://www.biorxiv.org/content/10.1101/2022.08.22.504706v3",
            "retrieval_note": (
                "The bioRxiv web pages block plain requests; the JATS source XML named by the bioRxiv "
                "details API was retrievable and was fetched twice on 2026-11-16 with identical bytes."
            ),
            "limitations": [
                "Used only for version history. No result in this batch is taken from it.",
                "The preprint's own supplementary PDF was not retrieved, so its Table S2 was not "
                "compared with the published one.",
            ],
            "review": review(BX_SHA, BX_URL, ["source-hash-verification", "transcription"],
                             "The positional perplexity sentence differs from the published one; see "
                             "notes.md. Every other printed value this batch records appears verbatim "
                             "in v3 as well, asserted by extract/parse_values.py."),
        },
        links=[("companion_of", SRC_PNAS)],
        sources=(SRC_PNAS,),
    ))

    out.append(rec(
        "source", SRC_VERSIONS,
        "bioRxiv details API record for 10.1101/2022.08.22.504706",
        "The bioRxiv version list for the GPN preprint, giving the posting date, title and licence "
        "of each of its three versions and the DOI of the published article.",
        {
            "url": VERSIONS_URL,
            "version": "API response of 2026-11-16, listing versions 1 to 3",
            "retrieved_at": RETRIEVED_BX,
            "artifact_sha256": VERSIONS_SHA,
            "publication_status": "official_project_source",
            "media_type": "application/json",
            "artifact_format": "JSON",
            "limitations": [
                "A mutable API; the hash describes one retrieval on 2026-11-16.",
                "Used only for the version history claim.",
            ],
            "missing_metadata": {
                "licence": {"reason": "unreported",
                            "note": "The API response states each preprint version's licence but not the terms of the API response itself."},
            },
            "review": review(VERSIONS_SHA, VERSIONS_URL, ["source-hash-verification", "automated-source-review"],
                             "Read for the three version dates and titles only."),
        },
        links=[("companion_of", SRC_PNAS)],
        sources=(SRC_PNAS,),
    ))

    # --------------------------------------------------------- configurations
    train_common = (
        "Masked language model over single-nucleotide tokens in 512 bp windows, 25 dilated "
        "convolutional blocks of embedding dimension 512, trained for 150,000 steps"
    )

    def config(suffix, name, description, attrs, extra_links=()):
        attrs = dict(attrs)
        attrs.setdefault("configuration_type", "paper_evaluation")
        attrs.setdefault("reported_name", "GPN")
        attrs.setdefault("version", "As trained for PNAS 120(44) e2311219120; no released checkpoint is named")
        attrs.setdefault("access_reuse", "Training code at https://github.com/songlab-cal/gpn (Data, "
                                         "Materials, and Software Availability). No checkpoint, revision "
                                         "or hash is named in the paper.")
        attrs.setdefault("review", rev_xml())
        attrs.setdefault("missing_metadata", {})
        attrs["missing_metadata"].setdefault("checkpoint", {
            "reason": "unreported",
            "note": "The paper names no released checkpoint for any of its models; it offers only the "
                    "training code at https://github.com/songlab-cal/gpn. The configuration is kept at "
                    "the training description the paper prints and is not tied to a published checkpoint.",
        })
        return rec("configuration", P + suffix, name, description, attrs,
                   links=[("configuration_of", GPN), ("family", GPN), *extra_links],
                   facets=FACETS_MODEL)

    out.append(config(
        "config-gpn-brassicales-repeat-weight-0-1",
        "GPN trained on eight Brassicales genomes, repeat loss weight 0.1 (PNAS 2023)",
        "Masked DNA language model trained on eight unaligned Brassicales reference genomes with "
        "the prediction loss on repetitive elements down-weighted to 0.1, which scores a variant by "
        "the log-likelihood ratio between its alternate and reference allele.",
        {
            "hyperparameters": train_common + ", convolutional kernel size 9, cycling dilation "
                               "1, 2, 4, 8, 16, 32, AdamW with weight decay 0.01, batch size 2048, "
                               "learning rate 1e-3 for 120,000 steps then cosine decay for 30,000 "
                               "steps after a 1,000 step warmup, 15% of positions masked, repeat "
                               "loss weight 0.1 (SI Appendix Table S3).",
            "training_setting": "Pretrained on the reference sequence of eight Brassicales genomes, one per "
                                "genus, with Arabidopsis thaliana chromosome 4 held out for validation and "
                                "chromosome 5 for testing. Windows were sampled from exons with a small "
                                "intronic flank, promoters 1,000 bp upstream of transcription start sites, "
                                "and an equivalent amount of random windows.",
            "hardware": {"accelerators": "4 x NVIDIA A100 80 GB", "wall_clock": "approximately 4 days"},
            "access_reuse": "Training code at https://github.com/songlab-cal/gpn (Data, Materials, and Software Availability). No checkpoint is named in the paper.",
            "provenance_note": "The paper's main model: \"Consequently, we focus on this model throughout "
                               "the remainder of the paper unless otherwise specified\" (Results, Training a "
                               "Multispecies DNA Language Model). Every result in this batch whose source "
                               "text says only \"GPN\" is assigned to it on the strength of that sentence.",
            "source_locator": "Results, 'Training a Multispecies DNA Language Model'; Materials and Methods, 'Pretraining'; SI Appendix Tables S1 to S3",
            "missing_metadata": {"parameters": {"reason": "unreported", "note": "No parameter count is printed; the paper gives 25 convolutional blocks at embedding dimension 512 and says the model is about 200 times smaller than the largest published protein language model."}},
        },
    ))

    out.append(config(
        "config-gpn-brassicales-repeat-weight-1",
        "GPN trained on eight Brassicales genomes, repeat loss weight 1 (PNAS 2023)",
        "Masked DNA language model trained on eight Brassicales reference genomes with no "
        "down-weighting of the prediction loss on repetitive elements.",
        {
            "hyperparameters": train_common + ", repeat loss weight 1; otherwise the hyperparameters of SI Appendix Table S3.",
            "training_setting": "As the main model, with the loss weight on repetitive elements left at 1.",
            "provenance_note": "One of the three models of SI Appendix Table S2, which differ only in the loss weight on repeats.",
            "source_locator": "SI Appendix Table S2, row 'Repeat weight 1'; Materials and Methods, 'Pretraining'",
        },
    ))

    out.append(config(
        "config-gpn-brassicales-repeat-weight-0",
        "GPN trained on eight Brassicales genomes, repeat loss weight 0 (PNAS 2023)",
        "Masked DNA language model trained on eight Brassicales reference genomes with the "
        "prediction loss on repetitive elements removed entirely.",
        {
            "hyperparameters": train_common + ", repeat loss weight 0; otherwise the hyperparameters of SI Appendix Table S3.",
            "training_setting": "As the main model, with the loss weight on repetitive elements set to 0.",
            "provenance_note": "One of the three models of SI Appendix Table S2, which differ only in the loss weight on repeats.",
            "source_locator": "SI Appendix Table S2, row 'Repeat weight 0'; Materials and Methods, 'Pretraining'",
        },
    ))

    out.append(config(
        "config-gpn-athaliana-single-species",
        "GPN trained on the Arabidopsis thaliana genome alone (PNAS 2023)",
        "Masked DNA language model trained on the single Arabidopsis thaliana reference genome, "
        "used to show what the seven related Brassicales genomes contribute.",
        {
            "hyperparameters": "Repeat loss weight 0.1 and the hyperparameters of SI Appendix Table S3, "
                               "except that it was trained for 12,000 steps with decaying learning rate "
                               "because the authors saw it would soon start overfitting.",
            "training_setting": "Pretrained on the Arabidopsis thaliana reference genome alone.",
            "provenance_note": "The paper's single-species ablation, described only in Materials and Methods, 'Pretraining'.",
            "source_locator": "Materials and Methods, 'Pretraining', sentence beginning 'We also trained a separate model on the single genome'",
        },
    ))

    out.append(config(
        "config-gpn-x-ld",
        "GPN x LD, GPN scores weighted by linkage disequilibrium (PNAS 2023)",
        "Variant score that sums the absolute GPN scores of nearby variants weighted by their "
        "squared correlation with the variant, so that two variants in strong linkage "
        "disequilibrium can still be scored differently.",
        {
            "reported_name": "GPN x LD",
            "hyperparameters": "GPNxLD_i = -sum_j |GPN_j| * r_ij^2, a stratified LD Score over the "
                               "absolute GPN scores. The LD matrix of squared Pearson correlations was "
                               "computed within a radius of 100 kb around each variant with sgkit. The "
                               "absolute value is taken because the association P-value does not depend "
                               "on which allele is called reference.",
            "provenance_note": "A scoring scheme the paper defines on top of the GPN scores of its main "
                               "model, the one trained with repeat loss weight 0.1, not a separately "
                               "trained model. It is a configuration of GPN, so its result belongs to "
                               "GPN; no uses_model link is added, which would say the opposite.",
            "source_locator": "Results, 'Enrichment of GWAS hits in regions with low GPN scores'; Materials and Methods, 'Variant Effect Prediction'",
        },
    ))

    # -------------------------------------------------------------- datasets
    out.append(rec(
        "dataset", P + "dataset-brassicales-genomes",
        "Eight Brassicales reference genome assemblies used to train GPN",
        "RefSeq-annotated reference genome assemblies of Arabidopsis thaliana and seven related "
        "Brassicales species, one per genus, used as the pretraining corpus and as the held-out "
        "validation and test sequence.",
        {
            "species": "Arabidopsis thaliana, Brassica rapa, Camelina sativa, Capsella rubella, Carica "
                       "papaya, Eutrema salsugineum, Raphanus sativus, Tarenaya hassleriana",
            "accession": "GCF_000001735.4, GCF_000309985.2, GCF_000633955.1, GCF_000375325.1, "
                         "GCF_000150535.2, GCF_000478725.1, GCF_000801105.1, GCF_000463585.1",
            "split": "Arabidopsis thaliana chromosome 4 for validation and chromosome 5 for testing; "
                     "all remaining sequence for training",
            "repository": "https://www.ncbi.nlm.nih.gov/data-hub/genome/",
            "version": "As listed in SI Appendix Table S1 of PNAS 120(44) e2311219120",
            "assay": "Reference genome sequence; no assay",
            "source_locator": "SI Appendix Table S1; Materials and Methods, 'Pretraining'",
            "review": rev_si_transcribed(
                "The eight assembly accessions, names and organism names were read from Table S1 by hand, "
                "not by a parser. The text layer prints a space where the accession has an underscore "
                "(GCF 000001735.4); the underscore is restored here, which is the only change made to the "
                "printed strings."),
        },
        sources=(SRC_PNAS, SRC_SI),
    ))

    out.append(rec(
        "dataset", P + "dataset-1001genomes-snps",
        "1001 Genomes Arabidopsis thaliana SNPs with allele frequencies",
        "Over 10 million single-nucleotide polymorphisms from naturally occurring Arabidopsis "
        "thaliana accessions, with the allele counts and frequencies used to separate rare from "
        "common variants.",
        {
            "species": "Arabidopsis thaliana",
            "repository": "https://aragwas.1001genomes.org/api/genotypes/download",
            "version": "1001 Genomes genotype matrix downloaded from the AraGWAS API, combined with "
                       "metadata from 1001genomes_snp-short-indel_only_ACGTN.vcf.gz release v3.1",
            "assay": "Whole-genome resequencing of natural accessions",
            "label_semantics": "Rare variants are those with allele count 1, which for these homozygous "
                               "selfing accessions means two alleles in one accession; common variants are "
                               "those with allele frequency above 5%. For variants with alternate allele "
                               "frequency above 50% the sign of the GPN score was flipped, so all analyses "
                               "are in terms of the minor allele.",
            "scope_note": "The paper says over 10 million variants were scored; it prints no exact total.",
            "source_locator": "Results, 'Benchmarking using allele frequencies in 1001 genomes'; Materials and Methods, 'Variant Effect Prediction'",
            "missing_metadata": {
                "variant_count": {"reason": "unreported",
                                  "note": "Only 'over 10 million variants' is printed; SI Appendix Figure S9 "
                                          "prints per-class rare and common counts in its subplot titles but no total."},
                "accession": {"reason": "unreported", "note": "No accession or archive DOI is given for the downloaded matrix."},
            },
            "review": rev_xml(),
        },
    ))

    out.append(rec(
        "dataset", P + "dataset-aragwas",
        "AraGWAS Catalog summary statistics for 462 Arabidopsis thaliana phenotypes",
        "Genome-wide association summary statistics for 462 Arabidopsis thaliana phenotypes, with "
        "each association marked significant or not under a permutation-based threshold and under a "
        "Bonferroni threshold.",
        {
            "species": "Arabidopsis thaliana",
            "repository": "https://aragwas.1001genomes.org/",
            "version": "Downloaded through the AraGWAS API with the default minimum allele count of 6",
            "assay": "Genome-wide association summary statistics",
            "population": "462 phenotypes",
            "label_semantics": "A variant is a GWAS hit for any trait when it reaches the permutation-based "
                               "significance threshold AraGWAS recommends; a Bonferroni threshold is also supplied.",
            "variants": 510462,
            "scope_note": "510,462 variants were tested in total; 453,281 of them have a whole-genome "
                          "alignment and so can also be scored by phyloP and phastCons.",
            "source_locator": "Results, 'Enrichment of GWAS hits in regions with low GPN scores'; Figure 6 D and E captions; Materials and Methods, 'Variant Effect Prediction'",
            "review": rev_xml(),
        },
    ))

    out.append(rec(
        "dataset", P + "dataset-ism-chr5-1mb",
        "All possible SNPs in Arabidopsis thaliana Chr5:3,500,000-4,500,000, annotated by consequence",
        "Every single-nucleotide polymorphism that can be made in a 1 Mb window of the held-out test "
        "chromosome, with its consequence called by the Ensembl Variant Effect Predictor.",
        {
            "species": "Arabidopsis thaliana",
            "split": "Held-out test chromosome 5, region 3,500,000 to 4,500,000",
            "assay": "In silico mutagenesis; no assay",
            "version": "Generated by the authors and annotated with the Ensembl Plants Variant Effect "
                       "Predictor web interface, upstream/downstream argument 500",
            "label_semantics": "Variant consequence classes from the Ensembl Variant Effect Predictor. Only "
                               "classes with at least 1,000 variants were compared, and variants with "
                               "different consequences in different transcripts were excluded.",
            "source_locator": "Results, 'In silico mutagenesis'; Materials and Methods, 'Variant Effect Prediction'",
            "missing_metadata": {
                "variant_count": {"reason": "unreported", "note": "The number of generated SNPs is not printed."},
            },
            "review": rev_xml(),
        },
    ))

    # -------------------------------------------------------- dataset subsets
    out.append(rec(
        "dataset_subset", P + "data-athaliana-chr5-test",
        "Arabidopsis thaliana chromosome 5, held out for testing",
        "The whole of Arabidopsis thaliana chromosome 5, held out of training and used to measure "
        "test perplexity chromosome-wide.",
        {
            "source_dataset": P + "dataset-brassicales-genomes",
            "split": "Test",
            "subset_scope": "All positions of Arabidopsis thaliana chromosome 5",
            "version": "TAIR10.1 (GCF_000001735.4) chromosome 5",
            "source_locator": "Materials and Methods, 'Pretraining'; SI Appendix Table S2 caption",
            "review": rev_si_transcribed(),
        },
        links=[("same_data_as", P + "dataset-brassicales-genomes")],
        sources=(SRC_PNAS, SRC_SI),
    ))

    out.append(rec(
        "dataset_subset", P + "data-athaliana-chr5-test-nonrepeat",
        "Non-repeat regions of Arabidopsis thaliana chromosome 5",
        "The positions of the held-out test chromosome that lie outside repetitive elements, the "
        "regions the authors say are often of greater interest.",
        {
            "source_dataset": P + "dataset-brassicales-genomes",
            "split": "Test",
            "subset_scope": "Positions of Arabidopsis thaliana chromosome 5 outside repetitive elements, "
                            "which are marked lowercase in the FASTA file",
            "version": "TAIR10.1 (GCF_000001735.4) chromosome 5, non-repeat positions",
            "source_locator": "SI Appendix Table S2, column 'Non-repeat regions'; Materials and Methods, 'Pretraining'",
            "review": rev_si_transcribed(),
        },
        links=[("same_data_as", P + "data-athaliana-chr5-test")],
        sources=(SRC_PNAS, SRC_SI),
    ))

    out.append(rec(
        "dataset_subset", P + "data-chr5-1mb-positions",
        "Positions of Arabidopsis thaliana Chr5:3,500,000-4,500,000 outside repeats, by class",
        "The positions of a 1 Mb window of the held-out test chromosome, excluding repeats, grouped "
        "into splice acceptors, splice donors, start codons, stop codons, the three coding frames, "
        "and intergenic and intronic positions.",
        {
            "source_dataset": P + "dataset-brassicales-genomes",
            "split": "Test",
            "subset_scope": "Chr5:3,500,000-4,500,000 after excluding repeats; the window contains 264 "
                            "genes and 471 transcripts",
            "version": "TAIR10.1 (GCF_000001735.4) Chr5:3,500,000-4,500,000",
            "source_locator": "Results, 'DNA Motifs Revealed by High-Confidence Model Predictions'; Materials and Methods, 'Motif Analysis'",
            "review": rev_xml(),
        },
        links=[("same_data_as", P + "data-athaliana-chr5-test")],
    ))

    out.append(rec(
        "dataset_subset", P + "data-genome-windows-100bp",
        "Non-overlapping 100 bp windows of the Arabidopsis thaliana genome, labelled by gene region",
        "Windows of the Arabidopsis thaliana reference genome labelled intergenic, intron, CDS, UTR, "
        "ncRNA or repeat, used to test whether the model's averaged embeddings separate gene regions.",
        {
            "source_dataset": P + "dataset-brassicales-genomes",
            "split": "All chromosomes; each chromosome is predicted by a model trained on the remaining chromosomes",
            "subset_scope": "Non-overlapping 100 bp windows across the Arabidopsis thaliana genome. Gene "
                            "annotation from EnsemblPlants; intergenic windows overlapping repeats "
                            "completely form a separate Repeat class; windows with ambiguous annotation "
                            "were excluded.",
            "version": "TAIR10.1 (GCF_000001735.4), EnsemblPlants annotation",
            "source_locator": "Results, 'Unsupervised Clustering of Genomic Regions'; Materials and Methods, 'Analysis of Model Embeddings'",
            "missing_metadata": {
                "test_count": {"reason": "unreported", "note": "The number of windows per class is not printed."},
            },
            "review": rev_xml(),
        },
        links=[("same_data_as", P + "dataset-brassicales-genomes")],
    ))

    # ------------------------------------------------------------- benchmarks
    bench_lm = P + "benchmark-athaliana-model-quality"
    bench_vep = P + "benchmark-athaliana-variant-effect"

    out.append(rec(
        "benchmark", bench_lm,
        "GPN paper: Arabidopsis thaliana held-out sequence modelling and embedding evaluation",
        "The paper's own evaluation of how well a GPN model predicts held-out Arabidopsis thaliana "
        "sequence and how far its embeddings separate gene regions.",
        {
            "entity_level": "suite",
            "executable_suite": False,
            "task": "Masked nucleotide prediction on held-out sequence, and gene region classification from averaged embeddings",
            "version": "As published in PNAS 120(44) e2311219120",
            "scope_note": "Defined by the authors for this paper. It is not a shared benchmark: no "
                          "leaderboard, no released split manifest and no other model is scored on it in "
                          "the paper.",
            "split": "Arabidopsis thaliana chromosome 4 validation, chromosome 5 test; gene region "
                     "classification holds out one chromosome at a time",
            "source_locator": "Results, 'Training a Multispecies DNA Language Model' and 'Unsupervised Clustering of Genomic Regions'; SI Appendix Table S2",
            "limitations": [
                "Author-defined and author-run; only the authors' own models are scored.",
                "The gene region confusion matrix (Figure 2B) prints no values, so only the two accuracies quoted in the text are recorded.",
            ],
            "review": rev_si_transcribed(),
        },
        sources=(SRC_PNAS, SRC_SI),
    ))

    out.append(rec(
        "benchmark", bench_vep,
        "GPN paper: unsupervised variant effect prediction in Arabidopsis thaliana",
        "The paper's own evaluation of a genome-wide variant score in Arabidopsis thaliana, by "
        "enrichment of rare variants and of GWAS hits in the tail of the score distribution.",
        {
            "entity_level": "suite",
            "executable_suite": False,
            "task": "Unsupervised genome-wide variant effect prediction, scored by enrichment rather than against a labelled truth set",
            "version": "As published in PNAS 120(44) e2311219120",
            "scope_note": "Arabidopsis thaliana only. There is no human variant evaluation anywhere in this "
                          "paper. Enrichment is measured with Fisher's exact test on a two by two table of "
                          "score class against variant class, so the endpoint is population genetic "
                          "signal, not a curated pathogenic or benign label.",
            "split": "No train or test split: every variant in the set is scored by an unsupervised model",
            "source_locator": "Results, 'Unsupervised Variant Effect Prediction'; Materials and Methods, 'Variant Effect Prediction'",
            "limitations": [
                "Author-defined and author-run.",
                "The comparison against phyloP, phastCons, abs(phyloP) and LD Score is printed only as "
                "bar charts (Figures 5D, 6D, 6E and SI Appendix Figures S6, S8 to S12), so no comparator "
                "value is in this batch.",
                "Rare versus common enrichment is a proxy for deleteriousness, not a measured functional effect.",
            ],
            "review": rev_xml(),
        },
    ))

    # -------------------------------------------------------------- protocols
    def protocol(suffix, name, description, attrs, bench, data_ids):
        attrs = dict(attrs)
        attrs.setdefault("review", rev_xml())
        links = [("part_of", bench)] + [("uses_data", d) for d in data_ids]
        return rec("protocol", P + suffix, name, description, attrs, links=links,
                   sources=attrs.pop("_sources", (SRC_PNAS,)))

    pp_chrom = P + "protocol-test-perplexity-chromosome-wide"
    pp_nonrep = P + "protocol-test-perplexity-non-repeat"
    pp_pos = P + "protocol-positional-perplexity-chr5-1mb"
    pp_class = P + "protocol-gene-region-classification"
    pp_rare = P + "protocol-rare-vs-common-odds-ratio"
    pp_gwas = P + "protocol-gwas-hit-odds-ratio"
    pp_ism = P + "protocol-repeat-variants-below-missense-decile"

    out.append(protocol(
        "protocol-test-perplexity-chromosome-wide",
        "Test perplexity on Arabidopsis thaliana chromosome 5, chromosome-wide",
        "Masked nucleotide prediction perplexity over the whole held-out test chromosome.",
        {
            "metric": "perplexity",
            "metric_direction": "lower",
            "unit": "unitless",
            "metric_qualifier": "masked nucleotide prediction, chromosome-wide over the held-out test chromosome",
            "metric_definition": "\"Perplexity, defined as the exponentiation of the cross-entropy loss, is "
                                 "equivalent to 1 over the probability given to the correct nucleotide\" (SI "
                                 "Appendix Table S2 caption, quoted).",
            "procedure": "Each model is scored on Arabidopsis thaliana chromosome 5, which was held out of "
                         "training; chromosome 4 was used for validation.",
            "dataset": "Arabidopsis thaliana chromosome 5 (TAIR10.1)",
            "version": "As published in SI Appendix Table S2 of PNAS 120(44) e2311219120",
            "source_locator": "SI Appendix Table S2, column 'Chromosome-wide'",
            "limitations": [
                "Measured by the authors on their own models only; no other model is scored.",
                "The single-species model's value is printed in Materials and Methods rather than in Table "
                "S2, and the text calls it 'test perplexity' without naming the column.",
            ],
            "review": rev_si_transcribed(),
            "_sources": (SRC_PNAS, SRC_SI),
        },
        bench_lm, [P + "data-athaliana-chr5-test"],
    ))

    out.append(protocol(
        "protocol-test-perplexity-non-repeat",
        "Test perplexity on Arabidopsis thaliana chromosome 5, non-repeat regions",
        "Masked nucleotide prediction perplexity over the positions of the held-out test chromosome "
        "that lie outside repetitive elements.",
        {
            "metric": "perplexity",
            "metric_direction": "lower",
            "unit": "unitless",
            "metric_qualifier": "masked nucleotide prediction, non-repeat regions of the held-out test chromosome",
            "metric_definition": "\"Perplexity, defined as the exponentiation of the cross-entropy loss, is "
                                 "equivalent to 1 over the probability given to the correct nucleotide\" (SI "
                                 "Appendix Table S2 caption, quoted).",
            "procedure": "As the chromosome-wide protocol, restricted to positions outside repetitive "
                         "elements, which are marked lowercase in the FASTA file.",
            "dataset": "Non-repeat positions of Arabidopsis thaliana chromosome 5 (TAIR10.1)",
            "version": "As published in SI Appendix Table S2 of PNAS 120(44) e2311219120",
            "source_locator": "SI Appendix Table S2, column 'Non-repeat regions'",
            "limitations": [
                "Measured by the authors on their own models only; no other model is scored.",
                "A different population from the chromosome-wide protocol, so the two are not comparable with each other.",
            ],
            "review": rev_si_transcribed(),
            "_sources": (SRC_PNAS, SRC_SI),
        },
        bench_lm, [P + "data-athaliana-chr5-test-nonrepeat"],
    ))

    out.append(protocol(
        "protocol-positional-perplexity-chr5-1mb",
        "Median held-out perplexity by position class in Chr5:3,500,000-4,500,000",
        "Median masked prediction perplexity at each class of genomic position in a 1 Mb window of "
        "the held-out test chromosome, after excluding repeats.",
        {
            "metric": "perplexity",
            "metric_direction": "lower",
            "unit": "unitless",
            "metric_qualifier": "median over positions of one class in Chr5:3,500,000-4,500,000, repeats excluded",
            "aggregation": "Median over the positions of each class",
            "procedure": "Each position was independently masked and the model distribution over nucleotides "
                         "extracted, averaged between the forward and reverse strands. Perplexity was then "
                         "computed for splice acceptors, splice donors, start codons, stop codons, the three "
                         "coding frames, and intergenic and intronic positions in Chr5:3,500,000-4,500,000 "
                         "after excluding repeats.",
            "dataset": "Chr5:3,500,000-4,500,000 of Arabidopsis thaliana (TAIR10.1), repeats excluded",
            "version": "As published in PNAS 120(44) e2311219120",
            "source_locator": "Results, 'DNA Motifs Revealed by High-Confidence Model Predictions'; Materials and Methods, 'Motif Analysis'",
            "limitations": [
                "The medians are printed in prose; SI Appendix Figure S4, which shows the distributions, prints no values.",
                "The classes are not disjoint from the chromosome-wide perplexity protocol and the numbers are not comparable with it: this is a median over one 1 Mb window by position class, not a perplexity over a chromosome.",
                "bioRxiv v3 prints different values for this measurement over a different region; see notes.md.",
            ],
        },
        bench_lm, [P + "data-chr5-1mb-positions"],
    ))

    out.append(protocol(
        "protocol-gene-region-classification",
        "Gene region classification from averaged GPN embeddings, leave-one-chromosome-out",
        "Accuracy of a logistic regression classifier that labels 100 bp genomic windows by gene "
        "region from the model's averaged embeddings, with each chromosome predicted by a model "
        "trained on the others.",
        {
            "metric": "accuracy",
            "metric_direction": "higher",
            "unit": "percent",
            "metric_qualifier": "per gene region class, leave-one-chromosome-out logistic regression on averaged 100 bp embeddings",
            "procedure": "Embeddings were averaged over non-overlapping 100 bp windows, averaged between the "
                         "forward and reverse strands and standardised. A logistic regression with class "
                         "weight inversely proportional to frequency and L2 strength chosen by "
                         "cross-validation was fitted in scikit-learn, and the windows of each chromosome "
                         "were predicted by a model trained on the remaining chromosomes.",
            "dataset": "Non-overlapping 100 bp windows of the Arabidopsis thaliana genome labelled by gene region",
            "version": "As published in PNAS 120(44) e2311219120",
            "source_locator": "Results, 'Unsupervised Clustering of Genomic Regions'; Materials and Methods, 'Analysis of Model Embeddings'",
            "limitations": [
                "Only the highest and lowest per-class accuracies are printed in the text. Figure 2B, the "
                "confusion matrix that holds the rest, prints no values, so the other classes are a gap.",
                "The text calls these accuracies on a class; whether the quantity is per-class recall or "
                "something else is not stated.",
                "A supervised probe over the model's embeddings, not a property of the model alone.",
            ],
        },
        bench_lm, [P + "data-genome-windows-100bp"],
    ))

    out.append(protocol(
        "protocol-rare-vs-common-odds-ratio",
        "Rare versus common variant enrichment in the lowest 0.1% of scores, 1001 Genomes",
        "Odds ratio for rare against common Arabidopsis thaliana variants falling in the lowest 0.1% "
        "of a genome-wide variant score.",
        {
            "metric": "odds-ratio",
            "metric_direction": "higher",
            "unit": "unitless",
            "metric_qualifier": "rare (allele count 1) against common (allele frequency at least 5%) variants, putative functional score threshold at the lowest 0.1% quantile",
            "metric_definition": "The odds ratio of the two by two table of score class against variant class, "
                                 "with the P-value from Fisher's exact test.",
            "procedure": "GPN scores were computed for over 10 million 1001 Genomes SNPs by masking each "
                         "variant position and taking the log-likelihood ratio between alternate and "
                         "reference allele, averaged over both strands. Scores were called putative "
                         "functional or benign at a quantile threshold, here 0.1%. Rare means allele count "
                         "1, common means allele frequency above 5%.",
            "dataset": "1001 Genomes Arabidopsis thaliana SNPs",
            "version": "As published in PNAS 120(44) e2311219120",
            "source_locator": "Results, 'Benchmarking using allele frequencies in 1001 genomes'; Figure 5 C; Materials and Methods, 'Variant Effect Prediction'",
            "limitations": [
                "Enrichment of rare variants is a population genetic proxy for deleteriousness, not a measured functional effect.",
                "Only the GPN value is printed in prose. The comparison with phyloP, phastCons and "
                "abs(phyloP) is Figure 5D, a bar chart with no values in its text layer.",
                "The contingency table itself is drawn in Figure 5C as an image, so its counts were not read.",
            ],
        },
        bench_vep, [P + "dataset-1001genomes-snps"],
    ))

    out.append(protocol(
        "protocol-gwas-hit-odds-ratio",
        "GWAS hit enrichment in the lowest 1% of scores, AraGWAS permutation threshold",
        "Odds ratio for AraGWAS hits for any trait falling in the lowest 1% of a genome-wide variant "
        "score, against the upper 99%.",
        {
            "metric": "odds-ratio",
            "metric_direction": "higher",
            "unit": "unitless",
            "metric_qualifier": "AraGWAS hits for any trait, permutation-based significance threshold, lowest 1% of scores against the upper 99%",
            "metric_definition": "The odds ratio of the two by two table of score class against GWAS hit "
                                 "status, with the P-value from Fisher's exact test.",
            "procedure": "Variants tested in AraGWAS for any of 462 phenotypes were scored, and the lowest 1% "
                         "of scores compared with the upper 99% for enrichment of variants significant under "
                         "the permutation-based threshold AraGWAS recommends.",
            "dataset": "AraGWAS Catalog summary statistics for 462 Arabidopsis thaliana phenotypes",
            "version": "As published in PNAS 120(44) e2311219120",
            "source_locator": "Results, 'Enrichment of GWAS hits in regions with low GPN scores'; Figure 6 C; Materials and Methods, 'Variant Effect Prediction'",
            "limitations": [
                "Which variant set the printed 10.3-fold odds ratio was computed on is not stated: Figure 6D "
                "is labelled n = 453,281 variants with whole-genome alignment and Figure 6E n = 510,462 for "
                "the full set, and the Figure 6C sentence names neither.",
                "Only the GPN x LD value is printed. The comparison with phyloP x LD, phastCons x LD, "
                "abs(phyloP) x LD and LD Score is Figure 6D, a bar chart with no values in its text layer; "
                "the text gives only the bound 'less than 7.5-fold ... for other methods'.",
                "A GWAS hit is an association, not a causal variant, so enrichment here is a proxy endpoint.",
            ],
            "missing_metadata": {
                "denominator": {"reason": "unreported",
                                "note": "The sentence that prints 10.3-fold does not say whether it is over the "
                                        "453,281 aligned variants of Figure 6D or the 510,462 of Figure 6E."},
            },
        },
        bench_vep, [P + "dataset-aragwas"],
    ))

    out.append(protocol(
        "protocol-repeat-variants-below-missense-decile",
        "Share of simulated repeat variants scored below the first decile of missense variants",
        "Percentage of simulated repeat variants that a model ranks ahead of the first decile of "
        "simulated missense variants, in a 1 Mb window of the held-out test chromosome.",
        {
            "metric": "proportion",
            "metric_direction": "lower",
            "unit": "percent",
            "unit_detail": "Percentage of the simulated repeat variants in the window",
            "metric_qualifier": "simulated repeat variants ranked before the first decile of simulated missense variants, in silico mutagenesis of Chr5:3,500,000-4,500,000",
            "procedure": "All possible SNPs in Chr5:3,500,000-4,500,000 were generated, their consequences "
                         "annotated with the Ensembl Variant Effect Predictor, and GPN scores computed for "
                         "each. The share of repeat variants scored below the first decile of missense "
                         "variants measures how far repetitive sequence is mistaken for constrained sequence.",
            "dataset": "All possible SNPs in Arabidopsis thaliana Chr5:3,500,000-4,500,000",
            "version": "As published in PNAS 120(44) e2311219120",
            "source_locator": "Results, 'In silico mutagenesis'; SI Appendix Figure S6 B",
            "limitations": [
                "A diagnostic of the training scheme, not a measure of accuracy: lower is better only on the "
                "authors' reading that these repeat variants should not outrank missense variants.",
                "The three percentages are printed in prose; SI Appendix Figure S6B itself prints no values.",
                "The Fisher's exact test P-value is given only as P < 10^-300 and the comparison it tests is not stated precisely.",
            ],
        },
        bench_vep, [P + "dataset-ism-chr5-1mb"],
    ))

    # ---------------------------------------------------- evaluations, results
    CFG = {
        "rw1": P + "config-gpn-brassicales-repeat-weight-1",
        "rw01": P + "config-gpn-brassicales-repeat-weight-0-1",
        "rw0": P + "config-gpn-brassicales-repeat-weight-0",
        "single": P + "config-gpn-athaliana-single-species",
        "ld": P + "config-gpn-x-ld",
    }

    def evaluation(eid, name, description, config_id, protocol_id, data_id, comparison,
                   attrs=None, sources=(SRC_PNAS,), rv=None):
        a = {
            "origin": "author_reported",
            "protocol": protocol_id,
            "comparison": comparison,
            "review": rv or rev_xml(),
            "limitations": ["Reported by the authors of the model, on an evaluation they designed and ran."],
        }
        a.update(attrs or {})
        return rec("evaluation", eid, name, description, a,
                   links=[("system", config_id), ("assessment", protocol_id), ("data", data_id)],
                   sources=sources)

    def result(rid, eval_id, printed, numeric, metric, direction, unit, qualifier, locator,
               attrs=None, sources=(SRC_PNAS,), rv=None, name=None, description=None):
        a = {
            "printed_value": printed,
            "numeric_value": numeric,
            "metric": metric,
            "metric_direction": direction,
            "unit": unit,
            "metric_qualifier": qualifier,
            "source_locator": locator,
            "review": rv or rev_xml(),
            "missing_metadata": {
                "uncertainty": {"reason": "unreported", "note": "The source prints no interval or spread for this value."},
            },
        }
        a.update(attrs or {})
        return rec("result", rid, name or printed, description or f"Printed value {printed}.", a,
                   links=[("evaluation", eval_id)], sources=sources)

    perp_comparison_base = {
        "protocol_id": None,
        "dataset_version": "TAIR10.1 (GCF_000001735.4) chromosome 5",
        "split": "Held-out test chromosome; chromosome 4 was the validation chromosome",
        "population": None,
        "inputs": "Reference DNA sequence in 512 bp windows; 15% of positions masked during training, the scored position masked at inference",
        "adaptation": "None; the pretrained model is scored directly",
        "metric_implementation": "Exponentiation of the cross-entropy loss, as stated in the SI Appendix Table S2 caption",
        "aggregation": None,
        "budget": None,
    }

    s2 = {row["row"]: row for row in v["table_s2"]}
    perp_rows = [
        ("rw1", "Repeat weight 1"),
        ("rw01", "Repeat weight 0.1"),
        ("rw0", "Repeat weight 0"),
    ]
    for key, label in perp_rows:
        for scope, phrase, column, protocol_id, data_id in [
            ("chromosome-wide", "chromosome-wide", "Chromosome-wide", pp_chrom,
             P + "data-athaliana-chr5-test"),
            ("non-repeat", "over non-repeat regions", "Non-repeat regions", pp_nonrep,
             P + "data-athaliana-chr5-test-nonrepeat"),
        ]:
            value = s2[label]["chromosome_wide" if scope == "chromosome-wide" else "non_repeat"]
            slug = {"rw1": "repeat-weight-1", "rw01": "repeat-weight-0-1", "rw0": "repeat-weight-0"}[key]
            eid = f"{P}eval-perplexity-{scope}-{slug}"
            comparison = dict(perp_comparison_base)
            comparison["protocol_id"] = protocol_id
            comparison["population"] = ("All positions of chromosome 5" if scope == "chromosome-wide"
                                        else "Positions of chromosome 5 outside repetitive elements")
            out.append(evaluation(
                eid,
                f"Test perplexity, {scope}, GPN with {label.lower()} (PNAS 2023 Table S2)",
                f"The authors' measurement of test perplexity {phrase} on Arabidopsis thaliana "
                f"chromosome 5 for the GPN model trained with {label.lower()}.",
                CFG[key], protocol_id, data_id, comparison,
                attrs={"review": rev_si()},
                sources=(SRC_PNAS, SRC_SI), rv=rev_si(),
            ))
            out.append(result(
                f"{P}result-perplexity-{scope}-{slug}", eid, value, value,
                "perplexity", "lower", "unitless",
                f"masked nucleotide prediction, {phrase} on the held-out test chromosome",
                f"Table S2 (SI Appendix), row \"{label}\", column \"{column}\"",
                attrs={"source_table": "SI Appendix Table S2"},
                # The SI source comes first so the value check reads the Table S2 text layer.
                sources=(SRC_SI, SRC_PNAS), rv=rev_si(),
                name=f"{value} perplexity, {scope}, {label.lower()}",
                description=f"Test perplexity {value} for the GPN model trained with {label.lower()}, "
                            f"measured {phrase} on Arabidopsis thaliana chromosome 5.",
            ))

    single = prose["single_species_perplexity"]["values"]
    for scope, phrase, value, protocol_id, data_id in [
        ("chromosome-wide", "chromosome-wide", single["chromosome_wide"], pp_chrom,
         P + "data-athaliana-chr5-test"),
        ("non-repeat", "over non-repeat regions", single["non_repeat"], pp_nonrep,
         P + "data-athaliana-chr5-test-nonrepeat"),
    ]:
        eid = f"{P}eval-perplexity-{scope}-single-species"
        comparison = dict(perp_comparison_base)
        comparison["protocol_id"] = protocol_id
        comparison["population"] = ("All positions of chromosome 5" if scope == "chromosome-wide"
                                    else "Positions of chromosome 5 outside repetitive elements")
        out.append(evaluation(
            eid,
            f"Test perplexity, {scope}, GPN trained on Arabidopsis thaliana alone (PNAS 2023)",
            f"The authors' measurement of test perplexity {phrase} for the model trained on the single "
            f"Arabidopsis thaliana genome, printed in Materials and Methods rather than in Table S2.",
            CFG["single"], protocol_id, data_id, comparison,
            attrs={"limitations": [
                "Reported by the authors of the model, on an evaluation they designed and ran.",
                "Printed in Materials and Methods, not in SI Appendix Table S2. The text says 'test "
                "perplexity of 3.13 (3.17 on nonrepeat regions)' without naming the Table S2 columns, so "
                "that these two values sit in the same two protocols as the Table S2 cells is the "
                "extractor's reading of the text, not something the paper states.",
            ]},
        ))
        out.append(result(
            f"{P}result-perplexity-{scope}-single-species", eid, value, value,
            "perplexity", "lower", "unitless",
            f"masked nucleotide prediction, {phrase} on the held-out test chromosome",
            "Materials and Methods, 'Pretraining', sentence \"This model obtained a higher test "
            "perplexity of 3.13 (3.17 on nonrepeat regions).\"",
            name=f"{value} perplexity, {scope}, single-species model",
            description=f"Test perplexity {value} for the GPN model trained on the Arabidopsis thaliana "
                        f"genome alone, measured {phrase} on chromosome 5.",
        ))

    # Positional perplexity, 8 classes, main model.
    pos = prose["positional_perplexity"]["values"]
    eid = P + "eval-positional-perplexity-chr5-1mb"
    out.append(evaluation(
        eid,
        "Median held-out perplexity by position class, Chr5:3,500,000-4,500,000 (PNAS 2023)",
        "The authors' measurement of median masked prediction perplexity at each class of genomic "
        "position in a 1 Mb window of the held-out test chromosome.",
        CFG["rw01"], pp_pos, P + "data-chr5-1mb-positions",
        {
            "protocol_id": pp_pos,
            "dataset_version": "TAIR10.1 (GCF_000001735.4) Chr5:3,500,000-4,500,000",
            "split": "Held-out test chromosome, 1 Mb window, repeats excluded",
            "population": "Positions of each class in a window containing 264 genes and 471 transcripts",
            "inputs": "Reference DNA sequence; each position independently masked, the distribution averaged between forward and reverse strands",
            "adaptation": "None; the pretrained model is scored directly",
            "metric_implementation": "Perplexity per position, then the median over the positions of each class",
            "aggregation": "Median over positions of the class",
            "budget": None,
        },
        attrs={"limitations": [
            "Reported by the authors of the model, on an evaluation they designed and ran.",
            "bioRxiv v3 prints this measurement over the whole test chromosome with different values and "
            "without the three coding frames; see notes.md.",
        ]},
    ))
    pos_slugs = {
        "splice donor": "splice-donor", "splice acceptor": "splice-acceptor",
        "start codon": "start-codon", "CDS2": "cds2", "CDS1": "cds1", "CDS3": "cds3",
        "stop codon": "stop-codon", "intergenic and intronic": "intergenic-and-intronic",
    }
    for label, value in pos.items():
        out.append(result(
            f"{P}result-positional-perplexity-{pos_slugs[label]}", eid, value, value,
            "perplexity", "lower", "unitless",
            f"median over {label} positions in Chr5:3,500,000-4,500,000, repeats excluded",
            "Results, 'DNA Motifs Revealed by High-Confidence Model Predictions', sentence beginning "
            "\"Across a 1-Mb region in the test chromosome\", term \"" + label + " (median = " + value + ")\"",
            attrs={"aggregation": "Median over positions of the class",
                   "reported_p_value": "All Mann-Whitney P-values < 10^-17 for the comparison with intergenic and intronic positions"}
            if label != "intergenic and intronic" else {"aggregation": "Median over positions of the class"},
            name=f"Median perplexity {value} at {label} positions",
            description=f"Median masked prediction perplexity {value} at {label} positions of "
                        f"Chr5:3,500,000-4,500,000.",
        ))

    # Gene region classification, two printed classes.
    cls = prose["region_classification"]["values"]
    eid = P + "eval-gene-region-classification"
    out.append(evaluation(
        eid,
        "Gene region classification from averaged GPN embeddings (PNAS 2023)",
        "The authors' measurement of how well a logistic regression on averaged GPN embeddings "
        "labels 100 bp genomic windows by gene region.",
        CFG["rw01"], pp_class, P + "data-genome-windows-100bp",
        {
            "protocol_id": pp_class,
            "dataset_version": "TAIR10.1 (GCF_000001735.4), EnsemblPlants gene annotation",
            "split": "Leave one chromosome out: each chromosome predicted by a model trained on the remaining chromosomes",
            "population": "Non-overlapping 100 bp windows with unambiguous gene region annotation",
            "inputs": "GPN embeddings averaged over each 100 bp window, averaged between strands and standardised",
            "adaptation": "Supervised logistic regression probe, class weight inversely proportional to frequency, L2 strength chosen by cross-validation (scikit-learn)",
            "metric_implementation": None,
            "aggregation": "Per class; the paper quotes only the highest and the lowest",
            "budget": None,
        },
        attrs={"limitations": [
            "Reported by the authors of the model, on an evaluation they designed and ran.",
            "Only two of the per-class accuracies are printed. The confusion matrix of Figure 2B holds the rest and prints no values.",
        ]},
    ))
    for label, value in cls.items():
        slug = label.lower()
        out.append(result(
            f"{P}result-gene-region-accuracy-{slug}", eid, value, value.rstrip("%"),
            "accuracy", "higher", "percent",
            f"gene region class {label}, leave-one-chromosome-out logistic regression on averaged 100 bp GPN embeddings",
            "Results, 'Unsupervised Clustering of Genomic Regions', sentence beginning \"To quantify "
            "GPN's ability to distinguish genomic regions\", term \"" + label + " (" + value + ")\"",
            attrs={"scope_note": "The text calls this the accuracy on this class. Whether the printed "
                                 "quantity is per-class recall is not stated."},
            name=f"{value} accuracy on {label} windows",
            description=f"Accuracy {value} for the {label} class in the leave-one-chromosome-out gene "
                        f"region classification from averaged GPN embeddings.",
        ))

    # Rare vs common odds ratio.
    eid = P + "eval-rare-vs-common-odds-ratio-gpn"
    out.append(evaluation(
        eid,
        "Rare versus common variant enrichment for GPN, 1001 Genomes (PNAS 2023)",
        "The authors' measurement of how far rare Arabidopsis thaliana variants are enriched in the "
        "lowest 0.1% of GPN scores.",
        CFG["rw01"], pp_rare, P + "dataset-1001genomes-snps",
        {
            "protocol_id": pp_rare,
            "dataset_version": "1001 Genomes genotype matrix from the AraGWAS API with metadata from release v3.1",
            "split": "No split; every variant is scored by an unsupervised model",
            "population": "Over 10 million 1001 Genomes SNPs; rare means allele count 1, common means allele frequency above 5%",
            "inputs": "Reference DNA sequence context with the variant position masked; log-likelihood ratio of alternate against reference allele, averaged over both strands",
            "adaptation": "None; zero-shot scoring by the pretrained model",
            "metric_implementation": "Odds ratio of the two by two table of score class against variant class, with Fisher's exact test",
            "aggregation": "Single odds ratio over the whole variant set",
            "budget": None,
        },
        attrs={"limitations": [
            "Reported by the authors of the model, on an evaluation they designed and ran.",
            "The paper prints the GPN value only. Its comparison with phyloP, phastCons and abs(phyloP) is Figure 5D, a bar chart with no values in its text layer.",
        ]},
    ))
    out.append(result(
        P + "result-rare-vs-common-odds-ratio-gpn", eid,
        prose["rare_vs_common_odds_ratio"]["values"]["GPN"], "5.5",
        "odds-ratio", "higher", "unitless",
        "rare (allele count 1) against common (allele frequency at least 5%) 1001 Genomes variants, putative functional score threshold at the lowest 0.1% quantile",
        "Results, 'Benchmarking using allele frequencies in 1001 genomes', sentence beginning "
        "\"Putative functional SNPs, defined as the lowest 0.1% of GPN scores\"; the same value is drawn in Figure 5 C",
        attrs={"scope_note": "Printed as a fold enrichment in the text; the figure caption calls it an odds ratio."},
        name="5.5-fold rare variant enrichment for GPN",
        description="Odds ratio 5.5 for rare against common 1001 Genomes variants in the lowest 0.1% of GPN scores.",
    ))

    # GWAS hit odds ratio.
    eid = P + "eval-gwas-hit-odds-ratio-gpn-x-ld"
    out.append(evaluation(
        eid,
        "GWAS hit enrichment for GPN x LD, AraGWAS (PNAS 2023)",
        "The authors' measurement of how far AraGWAS hits for any trait are enriched in the lowest "
        "1% of GPN x LD scores.",
        CFG["ld"], pp_gwas, P + "dataset-aragwas",
        {
            "protocol_id": pp_gwas,
            "dataset_version": "AraGWAS Catalog summary statistics for 462 phenotypes, minimum allele count 6",
            "split": "No split; every variant is scored",
            "population": None,
            "inputs": "GPN scores of the main model, weighted by the squared Pearson correlation with every variant within 100 kb",
            "adaptation": "None; zero-shot scoring, then the LD weighting the paper defines",
            "metric_implementation": "Odds ratio of the two by two table of score class against GWAS hit status, with Fisher's exact test",
            "aggregation": "Single odds ratio over the variant set, pooled across all traits",
            "budget": None,
        },
        attrs={
            "limitations": [
                "Reported by the authors of the model, on an evaluation they designed and ran.",
                "The variant set behind the printed value is not stated: Figure 6D is labelled n = 453,281 "
                "aligned variants and Figure 6E n = 510,462 for the full set, and the sentence that prints "
                "10.3-fold names neither.",
                "The paper prints the GPN x LD value only; the comparators are a bar chart.",
            ],
            "missing_metadata": {
                "denominator": {"reason": "unreported",
                                "note": "The sentence printing 10.3-fold does not say whether it covers the 453,281 aligned variants or the 510,462 of the full set."},
            },
        },
    ))
    out.append(result(
        P + "result-gwas-hit-odds-ratio-gpn-x-ld", eid,
        prose["gwas_odds_ratio"]["values"]["GPN x LD"], "10.3",
        "odds-ratio", "higher", "unitless",
        "AraGWAS hits for any trait, permutation-based significance threshold, lowest 1% of GPN x LD scores against the upper 99%",
        "Results, 'Enrichment of GWAS hits in regions with low GPN scores', sentence beginning \"In "
        "particular, by analyzing odds ratios\"; the same value is drawn in Figure 6 C",
        attrs={
            "scope_note": "Printed as a fold enrichment in the text; the figure caption calls it an odds ratio.",
            "missing_metadata": {
                "uncertainty": {"reason": "unreported", "note": "The source prints no interval or spread for this value."},
                "denominator": {"reason": "unreported",
                                "note": "Whether the value covers the 453,281 aligned variants of Figure 6D or the 510,462 of Figure 6E is not stated."},
            },
        },
        name="10.3-fold GWAS hit enrichment for GPN x LD",
        description="Odds ratio 10.3 for AraGWAS hits in the lowest 1% of GPN x LD scores against the upper 99%.",
    ))

    # Repeat variants below the missense decile, three models.
    ism = dict(prose["repeat_below_missense_decile"]["values"])
    ism.update(prose["repeat_below_missense_decile_baseline"]["values"])
    ism_locator = {
        "repeat weight 0": "Results, 'In silico mutagenesis', sentence beginning \"More precisely, in "
                           "models with 0.0 and 0.1 down-weighting\", the 8% of the 0.0 down-weighting model",
        "repeat weight 0.1": "Results, 'In silico mutagenesis', sentence beginning \"More precisely, in "
                             "models with 0.0 and 0.1 down-weighting\", the 9% of the 0.1 down-weighting model",
        "repeat weight 1": "Results, 'In silico mutagenesis', sentence beginning \"These represent a "
                           "substantial decrease compared to the 27% observed in the model without any down-weighting\"",
    }
    ism_cfg = {"repeat weight 0": "rw0", "repeat weight 0.1": "rw01", "repeat weight 1": "rw1"}
    for label, value in ism.items():
        slug = label.replace(" ", "-").replace(".", "-")
        eid = f"{P}eval-repeat-below-missense-decile-{slug}"
        out.append(evaluation(
            eid,
            f"Repeat variants below the missense first decile, GPN with {label} (PNAS 2023)",
            f"The authors' measurement of how many simulated repeat variants the GPN model trained "
            f"with {label} ranks ahead of the first decile of simulated missense variants.",
            CFG[ism_cfg[label]], pp_ism, P + "dataset-ism-chr5-1mb",
            {
                "protocol_id": pp_ism,
                "dataset_version": "All possible SNPs in TAIR10.1 Chr5:3,500,000-4,500,000, consequences from the Ensembl Plants VEP",
                "split": "Held-out test chromosome, 1 Mb window",
                "population": "Simulated repeat variants of the window, against the first decile of simulated missense variants",
                "inputs": "Reference DNA sequence context with the variant position masked; log-likelihood ratio of alternate against reference allele, averaged over both strands",
                "adaptation": "None; zero-shot scoring by the pretrained model",
                "metric_implementation": "Share of repeat variants scored below the tenth percentile of missense variant scores",
                "aggregation": "Single percentage over the window",
                "budget": None,
            },
            attrs={"limitations": [
                "Reported by the authors of the model, on an evaluation they designed and ran.",
                "Lower is better only on the authors' reading that repeat variants should not outrank missense variants.",
            ]},
        ))
        out.append(result(
            f"{P}result-repeat-below-missense-decile-{slug}", eid, value, value.rstrip("%"),
            "proportion", "lower", "percent",
            f"simulated repeat variants ranked before the first decile of simulated missense variants, GPN trained with {label}",
            ism_locator[label],
            attrs={"unit_detail": "Percentage of the simulated repeat variants in Chr5:3,500,000-4,500,000"},
            name=f"{value} of repeat variants below the missense first decile, {label}",
            description=f"{value} of simulated repeat variants in Chr5:3,500,000-4,500,000 scored below "
                        f"the first decile of simulated missense variants by the model trained with {label}.",
        ))

    # ----------------------------------------------------------------- claims
    def claim(suffix, name, description, subject, field, value, locator, attrs=None,
              sources=(SRC_PNAS,), rv=None):
        a = {
            "field": field,
            "value": value,
            "source_locator": locator,
            "review": rv or rev_xml(),
        }
        a.update(attrs or {})
        return rec("claim", P + suffix, name, description, a,
                   links=[("subject", subject)], sources=sources, status="source_checked")

    out.append(claim(
        "claim-architecture", "GPN architecture as published in the PNAS paper",
        "What the GPN paper states about the model's architecture and input.",
        GPN, "architecture",
        "Masked language model over single-nucleotide tokens, not k-mers or byte-pair encoding. A "
        "512 bp window is one-hot encoded and processed by 25 convolutional blocks, each a dilated "
        "convolution followed by a feed-forward layer with residual connections and layer "
        "normalisation, at a fixed embedding dimension of 512 and kernel size 9, with the dilation "
        "increased exponentially and then cycled. A final layer outputs four nucleotide "
        "probabilities at each masked position. Implemented with the Hugging Face library.",
        "Figure 1 caption; Materials and Methods, 'Pretraining'; SI Appendix Table S3",
        sources=(SRC_PNAS, SRC_SI),
    ))

    out.append(claim(
        "claim-variant-score-definition", "How GPN scores a variant",
        "What the GPN paper states about how a variant effect score is computed.",
        GPN, "scoring_definition",
        "The variant position is masked and the score is the log-likelihood ratio between the "
        "alternate and the reference allele, averaged between the forward and reverse strands. "
        "During training 15% of positions are masked; at variant effect prediction only the variant "
        "position is masked.",
        "Figure 1 caption; Materials and Methods, 'Variant Effect Prediction'",
    ))

    out.append(claim(
        "claim-species-scope", "The GPN paper evaluates Arabidopsis thaliana only",
        "What the GPN paper covers, recorded because the model family also carries results on human "
        "variants from other groups' benchmarks.",
        GPN, "evaluation_scope",
        "Every evaluation in this paper is in Arabidopsis thaliana: held-out sequence modelling, gene "
        "region classification from embeddings, in silico mutagenesis, 1001 Genomes rare against "
        "common enrichment and AraGWAS hit enrichment. The paper reports no human variant effect "
        "results, and no human model is trained or scored in it. Its stated motivation is that a "
        "model trained on DNA sequence alone can be applied to understudied non-model organisms.",
        "Abstract; Results; Discussion, paragraph beginning \"Here, we present an unsupervised genome-wide variant effect predictor\"",
    ))

    out.append(claim(
        "claim-training-data", "GPN pretraining corpus and held-out chromosomes",
        "What the GPN paper states about the data its main model was trained on.",
        P + "config-gpn-brassicales-repeat-weight-0-1", "training_data",
        "Eight RefSeq-annotated Brassicales reference genomes, one per genus, filtered from NCBI "
        "Genome: Arabidopsis thaliana, Brassica rapa, Camelina sativa, Capsella rubella, Carica "
        "papaya, Eutrema salsugineum, Raphanus sativus and Tarenaya hassleriana. Arabidopsis thaliana "
        "chromosomes 4 and 5 were held out for validation and testing. Windows of 512 bp at a step of "
        "256 bp were sampled with the reverse complement, drawn from exons with a small intronic "
        "flank, promoters 1,000 bp upstream of transcription start sites and an equivalent amount of "
        "random windows, with each genome subset to the number of windows from Arabidopsis.",
        "SI Appendix Table S1; Materials and Methods, 'Pretraining'",
        sources=(SRC_PNAS, SRC_SI),
    ))

    out.append(claim(
        "claim-training-compute", "GPN training compute as published",
        "What the GPN paper states about the cost of training each model.",
        P + "config-gpn-brassicales-repeat-weight-0-1", "training_compute",
        "Each of the three models was trained for 150,000 steps, taking approximately 4 days with 4 "
        "NVIDIA A100 80 GB GPUs.",
        "Materials and Methods, 'Pretraining', sentence \"We trained each model for 150,000 steps, taking approximately 4 d with 4 NVIDIA A100 80 GB GPUs.\"",
    ))

    out.append(claim(
        "claim-single-species-training", "Training of the single-species GPN model",
        "What the GPN paper states about the model trained on Arabidopsis thaliana alone.",
        P + "config-gpn-athaliana-single-species", "training_setting",
        "Trained on the single Arabidopsis thaliana genome with a repeat weight of 0.1 and the same "
        "hyperparameters as the main model, except for only 12,000 steps with decaying learning rate, "
        "because the authors saw it would soon start overfitting.",
        "Materials and Methods, 'Pretraining', sentence beginning \"We also trained a separate model on the single genome of A. thaliana\"",
    ))

    out.append(claim(
        "claim-score-correlation-phylop", "Correlation between GPN scores and phyloP",
        "The correlation the GPN paper reports between its variant scores and phyloP.",
        P + "config-gpn-brassicales-repeat-weight-0-1", "score_correlation_phylop",
        "r = 0.22, P < 10^-300, over the 1001 Genomes variants both methods score. The paper does not "
        "say whether r is a Pearson or a Spearman correlation.",
        "Results, 'Benchmarking using allele frequencies in 1001 genomes', sentence \"In fact, GPN scores are only weakly correlated with phyloP (r = 0.22, P < 10-300) and phastCons (r = 0.13, P < 10-300).\"",
    ))

    out.append(claim(
        "claim-score-correlation-phastcons", "Correlation between GPN scores and phastCons",
        "The correlation the GPN paper reports between its variant scores and phastCons.",
        P + "config-gpn-brassicales-repeat-weight-0-1", "score_correlation_phastcons",
        "r = 0.13, P < 10^-300, over the 1001 Genomes variants both methods score. The paper does not "
        "say whether r is a Pearson or a Spearman correlation.",
        "Results, 'Benchmarking using allele frequencies in 1001 genomes', sentence \"In fact, GPN scores are only weakly correlated with phyloP (r = 0.22, P < 10-300) and phastCons (r = 0.13, P < 10-300).\"",
    ))

    out.append(claim(
        "claim-alignment-coverage", "Share of variants that alignment-based scores cannot reach",
        "The coverage advantage the GPN paper claims over phyloP and phastCons.",
        P + "config-gpn-brassicales-repeat-weight-0-1", "coverage_advantage",
        "14.2% of all 1001 Genomes variants could not be scored by phyloP or phastCons because the "
        "whole-genome alignment failed there; GPN scores them because it needs no alignment. Where "
        "the paper compares with phyloP and phastCons, those variants were excluded.",
        "Results, 'Benchmarking using allele frequencies in 1001 genomes', sentence beginning \"A notable advantage of GPN\"; Materials and Methods, 'Variant Effect Prediction'",
    ))

    out.append(claim(
        "claim-comparator-bound-gwas", "The only comparator figure the GPN paper prints for Figure 6D",
        "The bound the paper states for the other methods in its GWAS enrichment comparison, "
        "recorded because the per-method values are only in the bar chart.",
        pp_gwas, "comparator_bound",
        "\"while less than 7.5-fold enrichment was observed for other methods (Fig. 6D)\". The other "
        "methods are phyloP x LD, phastCons x LD, abs(phyloP) x LD and LD Score. Figure 6D prints no "
        "per-method value in its text layer, so none is recorded.",
        "Results, 'Enrichment of GWAS hits in regions with low GPN scores', sentence beginning \"In particular, by analyzing odds ratios\"; Figure 6 D caption",
    ))

    out.append(claim(
        "claim-kmer-baseline", "k-mer frequency baseline for gene region classification",
        "The baseline range the GPN paper quotes against its embedding classification accuracies.",
        pp_class, "baseline_range",
        "Classification from k-mer frequencies alone spans 8% to 70% per class at k = 3 and 15% to 67% "
        "at k = 6. The paper prints these only as ranges over classes, not per class.",
        "Results, 'Unsupervised Clustering of Genomic Regions', sentence beginning \"This level of classification accuracy cannot be achieved merely through k-mer frequencies\"; SI Appendix Figure S1",
    ))

    out.append(claim(
        "claim-motif-count", "Promoter motifs recovered by TF-MoDISco on GPN predictions",
        "What the GPN paper reports from running an adapted TF-MoDISco over its promoter predictions.",
        GPN, "motif_analysis",
        "Approximately a hundred and sixty motifs were identified in regions 1,000 bp either side of "
        "transcription start sites, after filtering repeats and coding exons. Four are shown in Figure "
        "3B, the first two with a significant match in PlantTFDB at a Tomtom q-value below 0.05.",
        "Results, 'DNA Motifs Revealed by High-Confidence Model Predictions'; Figure 3 B caption; SI Appendix Figure S5",
        sources=(SRC_PNAS, SRC_SI),
    ))

    out.append(claim(
        "claim-code-availability", "Code availability for the GPN paper",
        "Where the GPN paper says its code can be found.",
        GPN, "code_availability",
        "\"Code to reproduce all results, including instructions to load the pretrained model, is "
        "available at https://github.com/songlab-cal/gpn\". No checkpoint name, revision or hash is "
        "given in the paper, and sequence logo predictions for Arabidopsis thaliana are offered as a "
        "UCSC Genome Browser session at https://genome.ucsc.edu/s/gbenegas/gpn-arabidopsis.",
        "Data, Materials, and Software Availability; Abstract",
    ))

    out.append(claim(
        "claim-version-history", "Version history of the GPN paper",
        "The three preprint versions behind the published GPN article and how they are titled.",
        SRC_PNAS, "version_history",
        "bioRxiv 10.1101/2022.08.22.504706 has three versions: v1 posted 2022-08-23 and v2 posted "
        "2023-04-12, both titled \"DNA language models are powerful zero-shot predictors of "
        "non-coding variant effects\" (v1) and \"... of genome-wide variant effects\" (v2), and v3 "
        "posted 2023-08-04 under the published title \"DNA language models are powerful predictors of "
        "genome-wide variant effects\". All three are licensed CC BY-NC-ND and all name 10.1073/pnas.2311219120 "
        "as the published article.",
        "bioRxiv details API response for 10.1101/2022.08.22.504706, fields title, date, version, license and published",
        sources=(SRC_PNAS, SRC_VERSIONS),
        rv=review(VERSIONS_SHA, VERSIONS_URL, ["source-hash-verification", "transcription"]),
    ))

    out.append(claim(
        "claim-preprint-value-difference", "Where bioRxiv v3 and the published article print different numbers",
        "The one measurement whose printed values changed between the final preprint and the "
        "published article, recorded so the stored values are not read as a correction of the preprint.",
        pp_pos, "version_difference",
        "The positional perplexity sentence differs. bioRxiv v3 reports medians over the whole test "
        "chromosome for four classes: splice acceptors 1.03, splice donors 1.02, start codons 1.10, "
        "stop codons 2.81, against intergenic and intronic 3.14, all Mann-Whitney p-values < 10^-239. "
        "The published article reports medians over a 1 Mb region of the test chromosome containing "
        "264 genes and 471 transcripts, and adds the three coding frames: splice donors 1.02, splice "
        "acceptors 1.03, start codons 1.08, CDS2 2.24, CDS1 2.44, CDS3 2.79, stop codons 2.8, against "
        "intergenic and intronic 3.24, all Mann-Whitney P-values < 10^-17. This is a different "
        "measurement region, not a corrected value. Every other printed value this batch records "
        "appears verbatim in both versions, asserted by extract/parse_values.py.",
        "bioRxiv v3 Results, sentence beginning \"Across the test chromosome, model perplexities in splice acceptors\"; published article Results, sentence beginning \"Across a 1-Mb region in the test chromosome\"",
        sources=(SRC_PNAS, SRC_BIORXIV),
        rv=review(BX_SHA, BX_URL, ["source-hash-verification", "transcription"]),
    ))

    out.append(claim(
        "claim-figure-only-comparisons", "The GPN paper's model comparisons are printed only as figures",
        "Why this batch holds no comparator value from the paper, recorded as a scope limit on the "
        "benchmark rather than as an absence of evidence.",
        bench_vep, "extraction_gap",
        "Every comparison of GPN against phyloP, phastCons, abs(phyloP), LD Score and their LD-weighted "
        "forms is printed as a bar chart with no values in the text layer: Figures 5D, 6D and 6E of the "
        "article and Figures S6, S8, S9, S10, S11 and S12 of the SI Appendix. The same is true of the "
        "contingency tables drawn in Figures 5C and 6C and of the confusion matrix in Figure 2B. The "
        "published article contains no table at all; the SI Appendix contains three, of which only "
        "Table S2 holds results. The comparator values are therefore a gap, not a finding.",
        "Figures 5 C, 5 D, 6 C, 6 D, 6 E and 2 B of the article; SI Appendix Figures S6, S8, S9, S10, S11 and S12",
        sources=(SRC_PNAS, SRC_SI),
    ))

    # ----------------------------------------------------------------- output
    ids = [r["id"] for r in out]
    assert len(ids) == len(set(ids)), "duplicate IDs: " + str(sorted({i for i in ids if ids.count(i) > 1}))
    out.sort(key=lambda r: r["id"])
    with open(OUT, "w") as fh:
        for r in out:
            fh.write(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n")
    counts = {}
    for r in out:
        counts[r["kind"]] = counts.get(r["kind"], 0) + 1
    print(f"wrote {OUT}: {len(out)} records")
    for kind in sorted(counts):
        print(f"  {kind}: {counts[kind]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
