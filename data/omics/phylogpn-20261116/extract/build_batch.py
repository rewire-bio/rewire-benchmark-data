"""Build batch.jsonl for the PhyloGPN preprint from the parsed tables.

Usage: python3 -I extract/build_batch.py extract/tables.json batch.jsonl

Every printed cell of Table 1 (60) and Table 2 (64) becomes one evaluation and one result. The
six printed N/A cells of Table 2 are never recorded. Entity metadata is written here by hand from
the pinned preprint and its pinned supplement; the numbers come only from extract/tables.json.
"""

import json
import sys

PAPER = "phylogpn-2025"
SUPP = "phylogpn-20261116-source-supplement"
SPRINGER = "phylogpn-20261116-source-springer-chapter"
README = "evidence-reported-phylogpn-2025-readme-md"
MODEL = "lit-genomics-20261011-guanine-model-phylogpn"
PREFIX = "phylogpn-20261116"

PAPER_SHA = "807f3a26cbfa9b5ce238d92164bd523302c67d1c5794b08273c51cca1acd4224"
PAPER_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11908359/fullTextXML"
SUPP_SHA = "b4885d288e03ae976acafb2b6b1c3837572dce224c8803715f4d329966ba65f4"
SUPP_ZIP_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11908359/supplementaryFiles"
SUPP_ARCHIVE_SHA = "29b1855dd6807ce39722f37b7db6bae0aa18b6036bb10be561e6574f5ccc3e71"
PAPER_ARCHIVE_SHA = "2b971a17c520b01a5b564929fa250af0d6da7a1298fb740fe72c1d8b0f1c139c"
SPRINGER_SHA = "31d3954fe7909256c70099ca0153500b1ab4c72314208e825dbd298276d4f0e7"
SPRINGER_URL = "https://link.springer.com/chapter/10.1007/978-3-031-90252-9_7"
DATE = "2026-11-16"

TABLE_PARSE = (
    "Parsed from the pinned Europe PMC JATS XML by extract/parse_tables.py, which asserts the "
    "SHA-256 of the artifact, both table headers, every row label in order, the cell count of "
    "each table and the six printed N/A cells of Table 2."
)
AGENT = (
    "Claude (Opus 5) extraction agent; no human review claimed. A different agent reviews this "
    "batch."
)


def review(note, methods=("deterministic-table-parse", "source-hash-verification"),
           sha=PAPER_SHA, url=PAPER_URL, method_note=TABLE_PARSE):
    return {
        "method": list(methods),
        "method_note": method_note,
        "reviewer": ["claude"],
        "reviewer_note": AGENT,
        "date": DATE,
        "artifact_sha256": sha,
        "retrieval_url": url,
        "note": note,
    }


TEXT_REVIEW_NOTE = (
    "Transcribed from the prose and captions of the pinned JATS XML; no number in this record "
    "comes from a figure."
)
SUPP_REVIEW_NOTE = (
    "Transcribed from the pdftotext -layout text layer of the pinned supplement PDF, whose "
    "SHA-256 was checked against the source record."
)


def text_review(note):
    return review(note, methods=("transcription", "source-hash-verification"),
                  method_note=TEXT_REVIEW_NOTE)


def supp_review(note):
    return review(note, methods=("pdf-text-parse", "source-hash-verification"), sha=SUPP_SHA,
                  url=SUPP_ZIP_URL, method_note=SUPP_REVIEW_NOTE)


def record(rid, kind, name, description, attributes, links=(), sources=(PAPER,),
           status="source_checked", facets=None):
    return {
        "id": rid,
        "kind": kind,
        "name": name,
        "description": description,
        "status": status,
        "facets": facets if facets is not None else {"areas": ["dna-genomes"], "contexts": ["research"]},
        "source_ids": list(sources),
        "links": [{"relation": r, "target_id": t} for r, t in links],
        "attributes": attributes,
    }


# ---------------------------------------------------------------- sources

SOURCES = [
    record(
        SUPP, "source",
        "Supplement 1 of the PhyloGPN preprint (arXiv:2503.03773v1)",
        "The appendix of the PhyloGPN preprint: its mathematical result, the log-likelihood-ratio "
        "evaluation settings, the GPN-MSA evaluation on BEND, Tables S1 and S2 and Figure S1.",
        {
            "url": SUPP_ZIP_URL,
            "artifact_url": SUPP_ZIP_URL,
            "artifact_member": "NIHPP2503.03773v1-supplement-1.pdf",
            "artifact_format": "application/pdf",
            "artifact_sha256": SUPP_SHA,
            "retrieved_at": "2026-11-16T01:07:00Z",
            "version": "Supplement 1 of arXiv:2503.03773v1 as deposited in PMC11908359",
            "publication_status": "preprint",
            "licence": "CC BY-NC-ND 4.0",
            "hash_scope": (
                "SHA-256 of the supplement PDF taken from the Europe PMC supplementaryFiles zip "
                "for PMC11908359. The zip is not byte-stable: two retrievals on 2026-11-16 gave "
                "different bytes because the archive carries per-download timestamps, while the "
                "member PDF was byte-identical in both."
            ),
            "archive_sha256": SUPP_ARCHIVE_SHA,
            "archive_member": "artifacts/NIHPP2503.03773v1-supplement-1.pdf.gz",
            "archive_note": (
                "The member PDF is kept gzipped in the batch folder because it is the only route "
                "to the appendix; the preprint licence allows unadapted noncommercial copying."
            ),
            "source_locator": (
                "Appendix A.2 Computation of Log Likelihood Ratios; A.3 Evaluation of GPN-MSA on "
                "BEND; A.4 Supplementary Tables and Figure (Tables S1 and S2, Figure S1)"
            ),
            "missing_metadata": {
                "doi": {
                    "reason": "inapplicable",
                    "note": "A supplementary file of the preprint; the DOI identifies the article.",
                },
            },
            "review": supp_review(
                "Retrieved twice on 2026-11-16: the zip differed in bytes, the member PDF did not. "
                "The PDF carries the paper title, the appendix sections and Tables S1 and S2."
            ),
        },
        links=(("companion_of", PAPER),),
        sources=(PAPER,),
    ),
    record(
        SPRINGER, "source",
        "Springer chapter page for the RECOMB 2025 version of record",
        "The publisher's page for the peer-reviewed version of this work, carrying its abstract, "
        "proceedings series, volume, page range, first-online date and DOI.",
        {
            "url": SPRINGER_URL,
            "artifact_url": SPRINGER_URL,
            "artifact_format": "text/html",
            "artifact_sha256": SPRINGER_SHA,
            "retrieved_at": "2026-11-16T01:05:00Z",
            "version": (
                "Chapter page as served on 2026-11-16: Research in Computational Molecular Biology "
                "(RECOMB 2025), Lecture Notes in Computer Science (LNBI) volume 15647, pages "
                "99-117, first online 25 April 2025"
            ),
            "doi": "10.1007/978-3-031-90252-9_7",
            "publication_status": "peer_reviewed",
            "venue": "Research in Computational Molecular Biology (RECOMB 2025), Lecture Notes in "
                     "Computer Science (LNBI) volume 15647",
            "year": 2025,
            "hash_scope": (
                "Mutable publisher page; the hash describes one retrieval. A second retrieval on "
                "2026-11-16 differed in bytes, so the hash does not identify the page over time."
            ),
            "limitations": [
                "The text of the version of record is paywalled: the page serves the abstract and "
                "the line 'This is a preview of subscription content'. No value in this batch "
                "comes from it.",
                "Used only for the venue, series volume, page range, first-online date and DOI of "
                "the version of record.",
            ],
            "source_locator": "Chapter header (series, volume, pages, First Online date), Abstract, "
                              "access panel",
            "missing_metadata": {
                "licence": {
                    "reason": "unreported",
                    "note": "The page states no licence for the chapter text.",
                },
            },
            "review": review(
                "Retrieved on 2026-11-16. The page gives the authors, the RECOMB 2025 proceedings, "
                "LNBI volume 15647, pages 99-117 and first online 25 April 2025, and offers only a "
                "preview of the text.",
                methods=("automated-source-review", "source-hash-verification"),
                sha=SPRINGER_SHA, url=SPRINGER_URL,
                method_note="Publisher page retrieved with curl and read as text; no value was "
                            "taken from it.",
            ),
        },
        links=(("companion_of", PAPER),),
        sources=(PAPER,),
    ),
]

# ---------------------------------------------------------------- configurations

FM = {"areas": ["dna-genomes"], "contexts": ["research"], "method_types": ["foundation_model"]}
SPECIALIST = {"areas": ["dna-genomes"], "contexts": ["research"], "method_types": ["specialist"]}

NO_REVISION = {
    "reason": "unreported",
    "note": "No checkpoint revision or weight digest is printed for the evaluated model.",
}

CONFIGS = [
    record(
        f"{PREFIX}-config-phylogpn", "configuration",
        "PhyloGPN (481 bp receptive field, about 83M parameters)",
        "PhyloGPN is a reverse-complement-equivariant dilated convolutional network that outputs "
        "F81 nucleotide substitution parameters for the central position of a 481 bp window.",
        {
            "reported_name": "PhyloGPN",
            "foundation_model_eligible": True,
            "parameters": (
                "40 dilated residual blocks giving a 481 bp receptive field; about 83M stored "
                "parameters, with reverse-complement weight tying leaving about half of them free; "
                "960-dimensional embeddings; trained for 18 epochs on four NVIDIA A100 GPUs with "
                "AdamW, a fixed learning rate of 1e-5 and no weight decay"
            ),
            "access_reuse": (
                "Weights at https://huggingface.co/songlab/phylogpn and evaluation code at "
                "https://github.com/songlab-cal/gpn. Neither is pinned to a revision in the paper."
            ),
            "provenance_note": (
                "The single trained model behind both the log-likelihood-ratio results and the "
                "BEND embedding results of this paper."
            ),
            "source_locator": "Methods, Architecture and Training; Methods, Embeddings; Footnotes, "
                              "Code and model availability",
            "missing_metadata": {
                "version": NO_REVISION,
                "checkpoint_revision": NO_REVISION,
            },
            "review": text_review("Architecture, parameter count, training settings and the "
                                  "release URLs are printed in the Methods and the footnote."),
        },
        links=(("configuration_of", MODEL),), sources=(PAPER,), facets=FM,
    ),
    record(
        f"{PREFIX}-config-phylogpn-x", "configuration",
        "PhyloGPN-X (pooled embeddings, 6,001 bp effective receptive field)",
        "PhyloGPN-X pools PhyloGPN embeddings over 5,521 contiguous positions through a fixed "
        "random linear map, giving an effective receptive field of 6,001 bp.",
        {
            "reported_name": "PhyloGPN-X",
            "foundation_model_eligible": True,
            "parameters": (
                "Embedding transform with l = 2,760, pooling 5,521 positions; fixed d x d matrix "
                "with independent standard normal entries; the underlying weights are PhyloGPN's, "
                "unchanged"
            ),
            "representation": "Pooled 960-dimensional PhyloGPN embeddings",
            "provenance_note": "An embedding transform of PhyloGPN, not a separately trained model.",
            "source_locator": "Methods, Embeddings (Eq. 6 and the following sentence)",
            "missing_metadata": {
                "version": NO_REVISION,
                "checkpoint_revision": NO_REVISION,
            },
            "review": text_review("The pooling width, the random map and the name are printed in "
                                  "Methods, Embeddings."),
        },
        links=(("configuration_of", MODEL),), sources=(PAPER,), facets=FM,
    ),
    record(
        f"{PREFIX}-config-nt-v2-500m-multi-species", "configuration",
        "Nucleotide Transformer v2 500M multi-species, likelihood-ratio scoring",
        "The 500M-parameter multi-species Nucleotide Transformer v2 checkpoint, scored by log "
        "likelihood ratios over 6-mer tokens averaged with the reverse complement.",
        {
            "reported_name": "Nucleotide Transformer",
            "version": "nucleotide-transformer-v2-500m-multi-species",
            "foundation_model_eligible": True,
            "parameters": (
                "At least 9,283 bp of context per position instead of the maximum 12,281 bp, "
                "because the genome was partitioned into disjoint 3 kb segments; the alternate "
                "over reference token ratio is averaged with the ratio for the complementary "
                "substitution on the reverse complement"
            ),
            "selection": (
                "The 2.5B multi-species model was also evaluated and did slightly worse on the "
                "likelihood-based tasks, so the 500M model is the one reported"
            ),
            "provenance_note": "The comparator checkpoint used for the likelihood-ratio tables.",
            "source_locator": "Appendix A.2, Computation of Log Likelihood Ratios (paragraphs 1-2)",
            "missing_metadata": {"checkpoint_revision": NO_REVISION},
            "review": supp_review("The checkpoint name, context length and scoring rule are "
                                  "printed in Appendix A.2."),
        },
        links=(("configuration_of", "discovery-model-nucleotide-transformer"),),
        sources=(PAPER, SUPP), facets=FM,
    ),
    record(
        f"{PREFIX}-config-hyenadna-medium-160k", "configuration",
        "HyenaDNA medium 160k, likelihood-ratio scoring",
        "The medium HyenaDNA checkpoint with a 160 kb sequence length, scored by causal log "
        "likelihood ratios averaged with those of the reverse complement.",
        {
            "reported_name": "HyenaDNA",
            "version": "hyenadna-medium-160k-seqlen-hf",
            "foundation_model_eligible": True,
            "parameters": (
                "At least 314,001 bp of context per position instead of the maximum 320,001 bp; "
                "because the model is causal, the ratio is averaged with the one obtained from the "
                "reverse complement of the following sequence"
            ),
            "selection": "The largest HyenaDNA model the authors could evaluate",
            "provenance_note": "The comparator checkpoint used for the likelihood-ratio tables.",
            "source_locator": "Appendix A.2, Computation of Log Likelihood Ratios (paragraph 3)",
            "missing_metadata": {"checkpoint_revision": NO_REVISION},
            "review": supp_review("The checkpoint name, context length and the reverse-complement "
                                  "averaging are printed in Appendix A.2."),
        },
        links=(("configuration_of", "regulatory-variant-20261009-model-hyenadna"),),
        sources=(PAPER, SUPP), facets=FM,
    ),
    record(
        f"{PREFIX}-config-caduceus-ps-131k", "configuration",
        "Caduceus-PS 131k, 256 model dimensions, 16 layers",
        "The parameter-shared Caduceus checkpoint with a 131 kb sequence length, 256 model "
        "dimensions and 16 layers, scored by its bidirectional likelihoods without transformation.",
        {
            "reported_name": "Caduceus",
            "version": "caduceus-ps_seqlen-131k_d_model-256_n_layer-16",
            "foundation_model_eligible": True,
            "parameters": (
                "At least 128,071 bp of context per position instead of the maximum 131,071 bp; "
                "outputs used untransformed because the model is bidirectional and "
                "reverse-complement equivariant"
            ),
            "provenance_note": "The comparator checkpoint used for the likelihood-ratio tables.",
            "source_locator": "Appendix A.2, Computation of Log Likelihood Ratios (paragraph 4)",
            "missing_metadata": {"checkpoint_revision": NO_REVISION},
            "review": supp_review("The checkpoint name, context length and the untransformed "
                                  "outputs are printed in Appendix A.2."),
        },
        links=(("configuration_of", "regulatory-variant-20261009-model-caduceus"),),
        sources=(PAPER, SUPP), facets=FM,
    ),
    record(
        f"{PREFIX}-config-caduceus-largest-rce", "configuration",
        "Caduceus, largest reverse-complement-equivariant model, frozen embeddings",
        "The largest reverse-complement-equivariant Caduceus model, used as a frozen embedding "
        "extractor for the BEND tasks.",
        {
            "reported_name": "Caduceus",
            "foundation_model_eligible": True,
            "model_identity_note": (
                "Section 4.2 identifies this model only as the largest reverse-complement "
                "equivariant Caduceus model. Appendix A.2 names "
                "caduceus-ps_seqlen-131k_d_model-256_n_layer-16 for the likelihood-ratio "
                "evaluation, but the paper does not say the embedding evaluation used that same "
                "checkpoint, so the two are kept as separate records."
            ),
            "provenance_note": "The Caduceus row of the BEND embedding table.",
            "source_locator": "Results, Embedding Evaluation (paragraph 2); Table 2 row 'Caduceus'",
            "missing_metadata": {
                "version": {
                    "reason": "unreported",
                    "note": "Only described as the largest reverse-complement-equivariant Caduceus "
                            "model; no checkpoint name is printed for this evaluation.",
                },
                "checkpoint_revision": NO_REVISION,
            },
            "review": text_review("The description of the model is printed in Results, Embedding "
                                  "Evaluation; no checkpoint name is given there."),
        },
        links=(("configuration_of", "regulatory-variant-20261009-model-caduceus"),),
        sources=(PAPER,), facets=FM,
    ),
    record(
        f"{PREFIX}-config-gpn-msa-precomputed-llr", "configuration",
        "GPN-MSA, published precomputed hg38 likelihood ratios",
        "GPN-MSA variant scores taken from the published precomputed hg38 log-likelihood-ratio "
        "dataset rather than recomputed.",
        {
            "reported_name": "GPN-MSA",
            "foundation_model_eligible": True,
            "parameters": "Precomputed log likelihood ratios for hg38",
            "access_reuse": "https://huggingface.co/datasets/songlab/gpn-msa-hg38-scores",
            "provenance_note": "The GPN-MSA column of the likelihood-ratio tables.",
            "source_locator": "Appendix A.2, Computation of Log Likelihood Ratios (paragraph 5)",
            "missing_metadata": {
                "version": {
                    "reason": "unreported",
                    "note": "No revision of the precomputed score dataset is named.",
                },
            },
            "review": supp_review("Appendix A.2 states that GPN-MSA was evaluated from "
                                  "precomputed likelihood ratios and gives the dataset URL."),
        },
        links=(("configuration_of", "gfm-guides-20261014-gpnmsa-model-gpn-msa"),),
        sources=(PAPER, SUPP), facets=FM,
    ),
    record(
        f"{PREFIX}-config-gpn-msa-bend-embeddings", "configuration",
        "GPN-MSA, concatenated 128 bp window embeddings",
        "GPN-MSA embeddings computed on non-overlapping 128 bp alignment windows and concatenated "
        "to cover a full-length input sequence.",
        {
            "reported_name": "GPN-MSA",
            "foundation_model_eligible": True,
            "parameters": (
                "Alignments retrieved for each sequence's genome coordinates from the GPN-MSA "
                "multiple sequence alignment, divided into non-overlapping 128 bp windows, "
                "embedded separately and concatenated; default BEND training and evaluation "
                "settings"
            ),
            "limitations": [
                "Chromatin Accessibility could not be evaluated because that task uses hg19 "
                "coordinates while the alignment is on the human reference the appendix names.",
                "Appendix A.3 writes that the alignment was constructed using the 'hg39' human "
                "reference genome. No assembly called hg39 exists, so this reads as a misprint; "
                "nothing in this batch was inferred from it.",
            ],
            "provenance_note": "The GPN-MSA row of the BEND embedding table.",
            "source_locator": "Appendix A.3, Evaluation of GPN-MSA on BEND",
            "missing_metadata": {
                "version": {
                    "reason": "unreported",
                    "note": "No GPN-MSA checkpoint or alignment release is named.",
                },
            },
            "review": supp_review("The windowing, the concatenation, the default BEND settings "
                                  "and the excluded task are printed in Appendix A.3."),
        },
        links=(("configuration_of", "gfm-guides-20261014-gpnmsa-model-gpn-msa"),),
        sources=(PAPER, SUPP), facets=FM,
    ),
    record(
        f"{PREFIX}-config-gpn-msa-bend-llr", "configuration",
        "GPN-MSA, allele likelihood ratios on variant-effect tasks",
        "GPN-MSA scored on variant-effect tasks by the log likelihood ratio between the reference "
        "and alternative alleles instead of a distance between embeddings.",
        {
            "reported_name": "GPN-MSA (LLR)",
            "foundation_model_eligible": True,
            "provenance_note": "The GPN-MSA (LLR) row of the BEND embedding table.",
            "source_locator": "Table 2 caption, final sentence; Table 2 row 'GPN-MSA (LLR)'",
            "missing_metadata": {
                "parameters": {
                    "reason": "unreported",
                    "note": "The caption says only that the row reports GPN-MSA likelihood ratios "
                            "between reference and alternative alleles. Whether they are the "
                            "published precomputed scores is not stated.",
                },
                "version": {
                    "reason": "unreported",
                    "note": "No GPN-MSA checkpoint or score release is named for this row.",
                },
            },
            "review": text_review("The caption states that the row reports likelihood ratios "
                                  "between reference and alternative alleles."),
        },
        links=(("configuration_of", "gfm-guides-20261014-gpnmsa-model-gpn-msa"),),
        sources=(PAPER,), facets=FM,
    ),
]

FAMILY_BEST = [
    ("dnabert", "DNABERT", None,
     "DNABERT-family DNA language models whose frozen embeddings a downstream head scores, taken "
     "at family level because the best score among the family members is reported without naming "
     "the member.",
     "The BEND benchmark scored DNABERT and DNABERT-2, and this row reports the better of the "
     "family on each task without saying which model it was. The store holds DNABERT and "
     "DNABERT-2 as separate family records, so this record is deliberately left unlinked rather "
     "than attached to one of them."),
    ("gena-lm", "GENA-LM", "regulatory-variant-20261009-model-gena-lm",
     "GENA-LM DNA language models whose frozen embeddings a downstream head scores, taken at "
     "family level because the best score among the family members is reported without naming the "
     "member.",
     "The BEND benchmark scored a GENA-LM BERT and a GENA-LM BigBird model, and this row reports "
     "the better of the two on each task without saying which model it was."),
    ("hyenadna", "HyenaDNA", "regulatory-variant-20261009-model-hyenadna",
     "HyenaDNA DNA language models whose frozen embeddings a downstream head scores, taken at "
     "family level because the best score among the family members is reported without naming the "
     "member.",
     "The BEND benchmark scored a large and a tiny HyenaDNA model, and this row reports the better "
     "of the two on each task without saying which model it was."),
    ("nucleotide-transformer", "Nucleotide Transformer", "discovery-model-nucleotide-transformer",
     "Nucleotide Transformer DNA language models whose frozen embeddings a downstream head scores, "
     "taken at family level because the best score among the family members is reported without "
     "naming the member.",
     "The BEND benchmark scored four Nucleotide Transformer models, and this row reports the best "
     "of them on each task without saying which model it was."),
]

for slug, printed, family, description, note in FAMILY_BEST:
    CONFIGS.append(record(
        f"{PREFIX}-config-{slug}-family-best", "configuration",
        f"{printed}, best model of the family on each BEND task",
        description,
        {
            "reported_name": printed,
            "foundation_model_eligible": True,
            "model_identity_note": note,
            "provenance_note": (
                f"The {printed} row of the BEND embedding table, whose values the authors "
                "reproduced from the BEND benchmark paper."
            ),
            "source_locator": f"Table 2 caption, first sentence; Table 2 row '{printed}'",
            "missing_metadata": {
                "version": {
                    "reason": "unreported",
                    "note": "A family-level row: the member that produced each value is not printed.",
                },
                "checkpoint_revision": NO_REVISION,
            },
            "review": text_review("The caption states that each row reports the best result among "
                                  "the models of that family."),
        },
        links=((("configuration_of", family),) if family else ()),
        sources=(PAPER,), facets=FM,
    ))

# ---------------------------------------------------------------- ClinVar protocol and data

CLINVAR_DATA = f"{PREFIX}-data-clinvar-llr"
CLINVAR_PROTOCOL = f"{PREFIX}-protocol-clinvar-llr-auroc"

CLASSES = [
    ("utr3", "3’ UTR"),
    ("utr5", "5’ UTR"),
    ("downstream-of-transcript", "Downstream of Transcript"),
    ("intronic", "Intronic"),
    ("missense", "Missense"),
    ("noncoding", "Noncoding"),
    ("splice-acceptor", "Splice Acceptor"),
    ("splice-donor", "Splice Donor"),
    ("start-codon", "Start Codon"),
    ("stop-lost", "Stop Lost"),
    ("synonymous", "Synonymous"),
    ("upstream-of-transcript", "Upstream of Transcript"),
]

UNREPORTED_COUNTS = {
    "reason": "unreported",
    "note": "The paper prints no variant counts for the ClinVar test set or its classes.",
}

DATA_RECORDS = [
    record(
        CLINVAR_DATA, "dataset",
        "ClinVar pathogenic versus benign variants with at least one review star",
        "Clinically classified ClinVar variants with at least one review star, split into a "
        "pathogenic or likely pathogenic positive class and a benign or likely benign negative "
        "class.",
        {
            "label_semantics": (
                "Positive class: variants labelled pathogenic or likely pathogenic. Negative "
                "class: variants labelled benign or likely benign. Both restricted to variants "
                "with at least one review star."
            ),
            "population": "Human variants in ClinVar",
            "split": "Evaluation only; no training split is used",
            "source_locator": "Results, Classifying ClinVar variants (paragraph 1); Table 1 caption",
            "missing_metadata": {
                "version": {
                    "reason": "unreported",
                    "note": "No ClinVar release or download date is printed.",
                },
                "variant_count": UNREPORTED_COUNTS,
                "accession": {
                    "reason": "unreported",
                    "note": "No accession or file is named for the retrieved ClinVar data.",
                },
            },
            "review": text_review("The review-star filter and the label classes are printed in "
                                  "Results, Classifying ClinVar variants."),
        },
        sources=(PAPER,),
        facets={"areas": ["dna-genomes"], "contexts": ["clinical_research"]},
    ),
    record(
        CLINVAR_PROTOCOL, "protocol",
        "ClinVar pathogenic versus benign classification from likelihood ratios, AUROC by variant class",
        "Scores variants by the log likelihood ratio of the alternate over the reference allele "
        "and reports one AUROC per printed variant class.",
        {
            "metric": "auroc",
            "metric_direction": "higher",
            "unit": "unitless",
            "metric_qualifier": (
                "ClinVar pathogenic or likely pathogenic versus benign or likely benign, zero-shot "
                "allele log likelihood ratio, one AUROC per variant class"
            ),
            "procedure": (
                "Likelihood values are computed for every position of the human reference genome "
                "and the log likelihood ratio of the alternate over the reference allele is taken "
                "as the variant score. No model is fitted on the ClinVar labels."
            ),
            "selection": "Variants with at least one review star",
            "aggregation": "One AUROC per printed variant class",
            "limitations": [
                "The paper does not report any exclusion of ClinVar positions from the pretraining "
                "data of the compared models.",
                "Class membership and class sizes are not printed, so the classes cannot be "
                "rebuilt from the paper alone.",
                "Compared models were given different amounts of sequence context, set by each "
                "model's receptive field.",
            ],
            "source_locator": (
                "Results, Log Likelihood Ratio Evaluation (paragraphs 1-3) and Classifying ClinVar "
                "variants; Table 1 caption; Appendix A.2"
            ),
            "missing_metadata": {
                "denominator": UNREPORTED_COUNTS,
                "uncertainty": {
                    "reason": "unreported",
                    "note": "No interval, resampling or repeat-run spread is printed for any cell "
                            "of Table 1.",
                },
                "version": {
                    "reason": "inapplicable",
                    "note": "A protocol defined by this paper; it carries no version of its own.",
                },
            },
            "review": text_review("The scoring rule, the star filter, the metric and the "
                                  "per-class reporting are printed in the Results and the Table 1 "
                                  "caption."),
        },
        links=(("uses_data", CLINVAR_DATA),),
        sources=(PAPER, SUPP),
        facets={"areas": ["dna-genomes"], "contexts": ["clinical_research"]},
    ),
]

for slug, label in CLASSES:
    DATA_RECORDS.append(record(
        f"{PREFIX}-subset-{slug}", "dataset_subset",
        f"ClinVar {label} variants, at least one review star",
        f"The {label} class of the ClinVar test set, scored on its own in the "
        "likelihood-ratio evaluation.",
        {
            "subset_scope": f"Variants of class {label}",
            "source_locator": f"Table 1, row '{label}'",
            "missing_metadata": {
                "test_count": UNREPORTED_COUNTS,
                "positive_count": UNREPORTED_COUNTS,
            },
            "review": review(f"The class label '{label}' is a printed row of Table 1."),
        },
        links=(("used_in", CLINVAR_PROTOCOL),),
        sources=(PAPER,),
        facets={"areas": ["dna-genomes"], "contexts": ["clinical_research"]},
    ))

# ---------------------------------------------------------------- Table 1 evaluations and results

T1_SYSTEMS = {
    "PhyloGPN": {
        "slug": "phylogpn",
        "config": f"{PREFIX}-config-phylogpn",
        "inputs": "481 bp of sequence context per scored position",
        "adaptation": "None: the allele probability is taken from the stationary distribution of "
                      "the predicted substitution model",
        "origin": "author_reported",
        "sources": (PAPER, SUPP),
    },
    "Caduceus": {
        "slug": "caduceus",
        "config": f"{PREFIX}-config-caduceus-ps-131k",
        "inputs": "At least 128,071 bp of sequence context per scored position",
        "adaptation": "None: bidirectional likelihoods used untransformed",
        "origin": "author_reported",
        "sources": (PAPER, SUPP),
    },
    "Nucleotide Transformer": {
        "slug": "nucleotide-transformer",
        "config": f"{PREFIX}-config-nt-v2-500m-multi-species",
        "inputs": "At least 9,283 bp of sequence context per scored position",
        "adaptation": "None: 6-mer token likelihood ratio averaged with the reverse complement",
        "origin": "author_reported",
        "sources": (PAPER, SUPP),
    },
    "HyenaDNA": {
        "slug": "hyenadna",
        "config": f"{PREFIX}-config-hyenadna-medium-160k",
        "inputs": "At least 314,001 bp of sequence context per scored position",
        "adaptation": "None: causal likelihood ratio averaged with the reverse complement",
        "origin": "author_reported",
        "sources": (PAPER, SUPP),
    },
    "GPN-MSA": {
        "slug": "gpn-msa",
        "config": f"{PREFIX}-config-gpn-msa-precomputed-llr",
        "inputs": "Published precomputed log likelihood ratios for hg38",
        "adaptation": "None: published precomputed scores",
        "origin": "author_reported",
        "sources": (PAPER, SUPP),
    },
}


def table_1_records(tables):
    out = []
    rows = tables["table_1"]["rows"]
    for slug, label in CLASSES:
        for column, system in T1_SYSTEMS.items():
            printed = rows[label][column]
            eid = f"{PREFIX}-eval-t1-{slug}-{system['slug']}"
            rid = f"{PREFIX}-result-t1-{slug}-{system['slug']}"
            locator = f"Table 1, row '{label}', column '{column}'"
            out.append(record(
                eid, "evaluation",
                f"{column} on ClinVar {label} variants, likelihood-ratio scoring",
                "Author-reported comparison transcribed from the pinned preprint; not reproduced.",
                {
                    "origin": system["origin"],
                    "protocol": CLINVAR_PROTOCOL,
                    "comparison": {
                        "protocol_id": CLINVAR_PROTOCOL,
                        "dataset_version": None,
                        "split": "None: zero-shot likelihood-ratio scoring",
                        "population": f"ClinVar variants with at least one review star, class {label}",
                        "inputs": system["inputs"],
                        "adaptation": system["adaptation"],
                        "metric_implementation": "AUROC with pathogenic and likely pathogenic "
                                                 "variants as positives",
                        "aggregation": "One AUROC over the variants of this class",
                        "budget": None,
                    },
                    "source_locator": locator,
                    "missing_metadata": {
                        "comparison.dataset_version": {
                            "reason": "unreported",
                            "note": "No ClinVar release or download date is printed.",
                        },
                        "comparison.budget": {
                            "reason": "inapplicable",
                            "note": "Zero-shot or precomputed scoring; no compute budget applies.",
                        },
                    },
                    "review": review(f"Cell read from the parsed table at {locator}."),
                },
                links=(("system", system["config"]), ("assessment", CLINVAR_PROTOCOL),
                       ("data", f"{PREFIX}-subset-{slug}")),
                sources=system["sources"],
                facets={"areas": ["dna-genomes"], "contexts": ["clinical_research"],
                        "tasks": ["ClinVar variant classification"]},
            ))
            out.append(record(
                rid, "result",
                f"{column} AUROC, ClinVar {label}",
                "Printed value transcribed from the pinned preprint; not reproduced.",
                {
                    "printed_value": printed,
                    "numeric_value": printed,
                    "metric": "auroc",
                    "metric_direction": "higher",
                    "unit": "unitless",
                    "metric_qualifier": (
                        "ClinVar pathogenic or likely pathogenic versus benign or likely benign, "
                        f"zero-shot allele log likelihood ratio, class {label}"
                    ),
                    "source_locator": locator,
                    "missing_metadata": {
                        "uncertainty": {
                            "reason": "unreported",
                            "note": "Table 1 prints no interval or spread.",
                        },
                        "denominator": UNREPORTED_COUNTS,
                    },
                    "review": review(f"Cell read from the parsed table at {locator}."),
                },
                links=(("evaluation", eid),),
                sources=(PAPER,),
                facets={"areas": ["dna-genomes"], "contexts": ["clinical_research"],
                        "tasks": ["ClinVar variant classification"]},
            ))
    return out


# ---------------------------------------------------------------- Table 2 evaluations and results

T2_TASKS = {
    "Gene Finding (MCC)": {
        "slug": "gene-finding", "task": "bend-task-gene-finding", "data": "bend-dataset-gencode",
        "metric": "matthews-correlation-coefficient", "metric_name": "MCC",
        "label": "Gene Finding", "kind": "supervised",
    },
    "Enhancer Annotation (AUPRC)": {
        "slug": "enhancer", "task": "bend-task-enhancer",
        "data": "bend-dataset-fulco-2019-gasperini-2019-and-enformer-enhancer-set",
        "metric": "auprc", "metric_name": "AUPRC", "label": "Enhancer Annotation",
        "kind": "supervised",
    },
    "Chromatin Accessibility (AUROC)": {
        "slug": "chromatin", "task": "bend-task-chromatin",
        "data": "bend-dataset-encode-chromatin-accessibility", "metric": "auroc",
        "metric_name": "AUROC", "label": "Chromatin Accessibility", "kind": "supervised",
    },
    "Histone Modification (AUROC)": {
        "slug": "histone", "task": "bend-task-histone",
        "data": "bend-dataset-encode-histone-modification", "metric": "auroc",
        "metric_name": "AUROC", "label": "Histone Modification", "kind": "supervised",
    },
    "CpG Methylation (AUROC)": {
        "slug": "cpg", "task": "bend-task-cpg", "data": "bend-dataset-encode-cpg-methylation",
        "metric": "auroc", "metric_name": "AUROC", "label": "CpG Methylation",
        "kind": "supervised",
    },
    "Expression VEP (AUROC)": {
        "slug": "expression-vep", "task": "bend-task-variant-expression",
        "data": "bend-dataset-deepsea-expression-variants", "metric": "auroc",
        "metric_name": "AUROC", "label": "Expression VEP", "kind": "vep",
    },
    "Disease VEP (AUROC)": {
        "slug": "disease-vep", "task": "bend-task-variant-disease",
        "data": "bend-dataset-clinvar-disease-variants", "metric": "auroc",
        "metric_name": "AUROC", "label": "Disease VEP", "kind": "vep",
    },
}

EXPERTS = {
    "(Augustus)": ("bend-method-augustus", "AUGUSTUS"),
    "(Enformer)": ("bend-method-enformer", "ENFORMER"),
    "(Basset)": ("bend-method-basset", "BASSET"),
    "(DeepSEA)": ("bend-method-deepsea", "DEEPSEA"),
}

EMBEDDING_ADAPTATION = {
    "supervised": "Two-layer CNN trained on frozen embeddings",
    "vep": "Cosine distance between the embeddings of the reference and alternative sequences",
}

T2_ROWS = {
    "PhyloGPN": {"slug": "phylogpn", "config": f"{PREFIX}-config-phylogpn",
                 "origin": "author_reported", "aggregation": None, "mode": "embedding"},
    "PhyloGPN-X": {"slug": "phylogpn-x", "config": f"{PREFIX}-config-phylogpn-x",
                   "origin": "author_reported", "aggregation": None, "mode": "embedding"},
    "Caduceus": {"slug": "caduceus", "config": f"{PREFIX}-config-caduceus-largest-rce",
                 "origin": "author_reported", "aggregation": None, "mode": "embedding"},
    "DNABERT": {"slug": "dnabert", "config": f"{PREFIX}-config-dnabert-family-best",
                "origin": "paper_compilation",
                "aggregation": "Best result among the models of this family",
                "mode": "embedding"},
    "GENA-LM": {"slug": "gena-lm", "config": f"{PREFIX}-config-gena-lm-family-best",
                "origin": "paper_compilation",
                "aggregation": "Best result among the models of this family",
                "mode": "embedding"},
    "HyenaDNA": {"slug": "hyenadna", "config": f"{PREFIX}-config-hyenadna-family-best",
                 "origin": "paper_compilation",
                 "aggregation": "Best result among the models of this family",
                 "mode": "embedding"},
    "Nucleotide Transformer": {"slug": "nucleotide-transformer",
                               "config": f"{PREFIX}-config-nucleotide-transformer-family-best",
                               "origin": "paper_compilation",
                               "aggregation": "Best result among the models of this family",
                               "mode": "embedding"},
    "GPN-MSA": {"slug": "gpn-msa", "config": f"{PREFIX}-config-gpn-msa-bend-embeddings",
                "origin": "author_reported", "aggregation": None, "mode": "embedding"},
    "GPN-MSA (LLR)": {"slug": "gpn-msa-llr", "config": f"{PREFIX}-config-gpn-msa-bend-llr",
                      "origin": "author_reported", "aggregation": None, "mode": "llr"},
    "Expert Method": {"slug": "expert", "config": None, "origin": "paper_compilation",
                      "aggregation": None, "mode": "expert"},
}

ASTERISK_NOTE = (
    "The Table 2 caption says of asterisked results: \"Asterisked results are discussed further in "
    "the text; we believe they are not fully indicative of the models' capabilities.\""
)

BEND_CROSSCHECK = {
    ("GENA-LM", "Chromatin Accessibility (AUROC)"): (
        "The printed 0.84 is above both GENA-LM values already stored from the BEND paper's own "
        "Table 1 (GENA-LM BERT 0.76, GENA-LM BigBird 0.82), so it is not the maximum of the stored "
        "family values. A lead for the reviewer, not a correction: the printed value stands."
    ),
    ("Nucleotide Transformer", "Expression VEP (AUROC)"): (
        "The printed 0.54 matches the stored NT-MS value from the BEND paper's own Table 1, but "
        "the stored NT-H value is 0.55, so this is not the maximum of the stored family values. A "
        "lead for the reviewer, not a correction: the printed value stands."
    ),
}


def table_2_records(tables):
    out = []
    rows = tables["table_2"]["rows"]
    experts = tables["table_2"]["expert_labels"]
    for column, task in T2_TASKS.items():
        for row_label, row in T2_ROWS.items():
            printed = rows[row_label][column]
            if printed == "N/A":
                continue
            if row["mode"] == "expert":
                config, _ = EXPERTS[experts[column]]
                system_name = experts[column].strip("()")
                adaptation = "Task-specific expert model trained end to end"
                sources = (PAPER,)
            else:
                config = row["config"]
                printed_name = row_label
                system_name = row_label
                adaptation = (
                    "Log likelihood ratio between the reference and alternative alleles"
                    if row["mode"] == "llr" else EMBEDDING_ADAPTATION[task["kind"]]
                )
                sources = (PAPER, SUPP) if row["slug"].startswith("gpn-msa") else (PAPER,)
            eid = f"{PREFIX}-eval-t2-{task['slug']}-{row['slug']}"
            rid = f"{PREFIX}-result-t2-{task['slug']}-{row['slug']}"
            locator = f"Table 2, row '{row_label}', column '{column}'"
            numeric = printed.rstrip("*")
            qualifier = f"BEND {task['label']}, {adaptation[0].lower() + adaptation[1:]}"
            if row["aggregation"]:
                qualifier += "; best result among the models of this family"
            compiled = row["origin"] == "paper_compilation"
            description = (
                "Value reproduced from the BEND benchmark paper by the authors of this preprint; "
                "not reproduced by Rewire."
                if compiled else
                "Author-reported evaluation transcribed from the pinned preprint; not reproduced."
            )
            attrs = {
                "origin": row["origin"],
                "protocol": task["task"],
                "comparison": {
                    "protocol_id": task["task"],
                    "dataset_version": None,
                    "split": "BEND train, validation and test splits",
                    "population": f"BEND {task['label']} test set",
                    "inputs": (
                        "Reference and alternative alleles"
                        if row["mode"] == "llr" else
                        "Task-specific inputs of the expert model"
                        if row["mode"] == "expert" else
                        "Frozen embeddings of the task's input sequences"
                    ),
                    "adaptation": adaptation,
                    "metric_implementation": f"{task['metric_name']} on the BEND test set",
                    "aggregation": row["aggregation"],
                    "budget": None,
                },
                "source_locator": locator,
                "missing_metadata": {
                    "comparison.dataset_version": {
                        "reason": "unreported",
                        "note": "No BEND release or revision is named.",
                    },
                    "comparison.budget": {
                        "reason": "unreported",
                        "note": "No compute budget is printed for the BEND evaluations.",
                    },
                },
                "review": review(f"Cell read from the parsed table at {locator}."),
            }
            if row["aggregation"] is None:
                attrs["missing_metadata"]["comparison.aggregation"] = {
                    "reason": "inapplicable",
                    "note": "A single model's score, not an aggregate over a family.",
                }
            if compiled:
                attrs["limitations"] = [
                    "Reproduced by this paper from the BEND benchmark paper, which ran the "
                    "evaluation; the numbers are not this paper's own measurement."
                ]
            out.append(record(
                eid, "evaluation",
                f"{system_name} on BEND {task['label']}",
                description,
                attrs,
                links=(("system", config), ("assessment", task["task"]), ("data", task["data"])),
                sources=sources,
                facets={"areas": ["dna-genomes"], "contexts": ["research"],
                        "tasks": [f"BEND {task['label']}"]},
            ))
            result_attrs = {
                "printed_value": printed,
                "numeric_value": numeric,
                "metric": task["metric"],
                "metric_direction": "higher",
                "unit": "unitless",
                "metric_qualifier": qualifier,
                "source_locator": locator,
                "missing_metadata": {
                    "uncertainty": {
                        "reason": "unreported",
                        "note": "Table 2 prints no interval or spread.",
                    },
                    "denominator": {
                        "reason": "unreported",
                        "note": "The paper prints no test-set size for the BEND tasks.",
                    },
                },
                "review": review(f"Cell read from the parsed table at {locator}."),
            }
            if printed.endswith("*"):
                result_attrs["source_warnings"] = [ASTERISK_NOTE]
            if (row_label, column) in BEND_CROSSCHECK:
                result_attrs["source_discrepancy"] = BEND_CROSSCHECK[(row_label, column)]
            out.append(record(
                rid, "result",
                f"{system_name} {task['metric_name']}, BEND {task['label']}",
                description,
                result_attrs,
                links=(("evaluation", eid),),
                sources=(PAPER,),
                facets={"areas": ["dna-genomes"], "contexts": ["research"],
                        "tasks": [f"BEND {task['label']}"]},
            ))
    return out


# ---------------------------------------------------------------- descriptive claims

def claim(slug, subject, field, value, locator, sources, rev, description, status="source_checked",
          name=None, extra=None):
    attrs = {"field": field, "value": value, "source_locator": locator, "review": rev}
    if extra:
        attrs.update(extra)
    return record(
        f"{PREFIX}-claim-{slug}", "claim", name or f"PhyloGPN {field.replace('_', ' ')}",
        description, attrs, links=(("subject", subject),), sources=sources, status=status,
        facets={"areas": ["dna-genomes"], "contexts": ["research"]},
    )


CLAIMS = [
    claim("architecture", MODEL, "architecture",
          "Reverse-complement-equivariant dilated convolutional network adapted from CARP, itself "
          "adapted from ByteNet, with 40 residual blocks, a 481 bp receptive field and about 83M "
          "stored parameters. Reverse-complement weight tying leaves about half of the weights and "
          "biases free, plus the layer-normalisation parameters.",
          "Methods, Architecture and Training (paragraph 1)", (PAPER,),
          text_review("Printed in Methods, Architecture and Training."),
          "The network family, depth, receptive field and parameter count of PhyloGPN."),
    claim("training-data", MODEL, "training_data",
          "Length-481 windows of the human reference genome GRCh38, each paired with the "
          "nucleotides aligned to its central position in a whole-genome alignment of 447 placental "
          "mammal genomes from the Zoonomia Consortium, and with the minimum spanning tree of a "
          "species-level phylogeny for the species aligned at that position. Positions outside the "
          "primary assembly were excluded.",
          "Methods, Training Data (paragraphs 1-2); Methods, Architecture and Training (paragraph 2)",
          (PAPER,), text_review("Printed in Methods, Training Data."),
          "The genomes, alignment and phylogeny PhyloGPN was trained on."),
    claim("training-objective", MODEL, "training_objective",
          "A stable upper bound of a phylogenetic F81 likelihood for the aligned column at the "
          "central position, conditioned on the state of the human reference nucleotide so the "
          "model cannot simply copy it.",
          "Methods, Loss Function (Eqs. 3 to 5)", (PAPER,),
          text_review("Printed in Methods, Loss Function."),
          "What PhyloGPN was trained to predict."),
    claim("training-compute", MODEL, "training_compute",
          "Eighteen epochs on four NVIDIA A100 GPUs with AdamW, a fixed learning rate of 1e-5 and "
          "no weight decay; 12 alignment blocks of about 10 kb per batch, with autosomal positions "
          "sampled four times per epoch, X chromosome positions three times and Y chromosome "
          "positions once.",
          "Methods, Architecture and Training (paragraphs 2-3)", (PAPER,),
          text_review("Printed in Methods, Architecture and Training."),
          "The hardware, optimiser and schedule PhyloGPN was trained with."),
    claim("inference-inputs", MODEL, "inference_inputs",
          "A single DNA sequence. The whole-genome alignment and the phylogeny enter the training "
          "loss only and are not required to make a prediction.",
          "Abstract; Discussion and Conclusion (paragraph 1)", (PAPER,),
          text_review("Printed in the Abstract and the Discussion."),
          "What PhyloGPN needs as input at prediction time."),
    claim("embeddings", MODEL, "embeddings",
          "A 960-dimensional embedding of any 481 bp DNA sequence, taken from one named layer. "
          "Embeddings from other layers were not tried.",
          "Methods, Embeddings (paragraph 1)", (PAPER,),
          text_review("Printed in Methods, Embeddings."),
          "The representation PhyloGPN provides for downstream tasks."),
    claim("access", MODEL, "access",
          "Model weights at https://huggingface.co/songlab/phylogpn and the code for the "
          "likelihood-based evaluation at https://github.com/songlab-cal/gpn. Neither is pinned to "
          "a revision in the paper.",
          "Footnotes, Code and model availability", (PAPER,),
          text_review("Printed in the code and model availability footnote."),
          "Where the weights and the evaluation code are published."),
    claim("coding-limit", MODEL, "reported_limitation",
          "The authors attribute PhyloGPN coming up short of GPN-MSA on coding variant "
          "pathogenicity to its training alignment holding many mammals but fewer distantly related "
          "species, and state they did not harmonise the more diverse vertebrate alignment with "
          "their mammalian one.",
          "Discussion and Conclusion (paragraph 4)", (PAPER,),
          text_review("Printed in the Discussion."),
          "The limitation the authors themselves give for coding variants."),
    claim("preprint-licence", PAPER, "attributes.licence",
          "CC BY-NC-ND 4.0",
          "Permissions statement of the PMC deposit of arXiv:2503.03773v1",
          (PAPER,),
          review("The PMC deposit carries a Creative Commons "
                 "Attribution-NonCommercial-NoDerivatives 4.0 International licence. The stored "
                 "source record leaves licence unextracted; this claim records the printed value "
                 "for the reviewer to apply.",
                 methods=("automated-source-review", "source-hash-verification"),
                 method_note="Read from the permissions element of the pinned JATS XML."),
          "The licence the pinned preprint artifact carries, which its source record leaves unset.",
          status="needs_review",
          name="Licence of the pinned PhyloGPN preprint artifact",
          extra={"rationale": "The source record records no licence; the pinned artifact states one."}),
    claim("version-of-record", PAPER, "attributes.version_note",
          "Published as a peer-reviewed conference paper: Albors C., Li J.C., Benegas G., Ye C., "
          "Song Y.S., A Phylogenetic Approach to Genomic Language Modeling, Research in "
          "Computational Molecular Biology (RECOMB 2025), Lecture Notes in Computer Science (LNBI) "
          "volume 15647, pages 99-117, first online 25 April 2025, doi "
          "10.1007/978-3-031-90252-9_7. The pinned artifact remains the preprint, whose "
          "publication_status is correctly 'preprint'; the version of record is paywalled and was "
          "not compared with the preprint.",
          "Springer chapter page header and abstract; songlab-cal/gpn README model-families table "
          "and BibTeX entry albors2025phylogenetic",
          (SPRINGER, README),
          review("The README of the model's own repository cites the Springer chapter, and the "
                 "chapter page gives the venue, volume, pages and first-online date. Recorded as a "
                 "claim rather than an edit: the stored source record describes the preprint "
                 "artifact, so its publication status is not wrong, but it carries no pointer to "
                 "the version of record.",
                 methods=("automated-source-review", "source-hash-verification"),
                 sha=SPRINGER_SHA, url=SPRINGER_URL,
                 method_note="Publisher page and the pinned repository README read as text."),
          "The peer-reviewed version of this work, which the store does not yet point to.",
          status="needs_review",
          name="Version of record of the PhyloGPN paper",
          extra={"rationale": "The discovery issue records the paper as absent and unpublished; it "
                              "is published, and the store already holds the preprint."}),
]

# ---------------------------------------------------------------- assembly


def main():
    tables = json.load(open(sys.argv[1]))
    out_path = sys.argv[2] if len(sys.argv) > 2 else "batch.jsonl"
    records = SOURCES + CONFIGS + DATA_RECORDS + table_1_records(tables) + table_2_records(tables) + CLAIMS

    ids = [r["id"] for r in records]
    assert len(ids) == len(set(ids)), "duplicate record IDs"
    results = [r for r in records if r["kind"] == "result"]
    evaluations = [r for r in records if r["kind"] == "evaluation"]
    assert len(results) == 124, f"{len(results)} results, expected 124"
    assert len(evaluations) == 124, f"{len(evaluations)} evaluations, expected 124"
    assert len([r for r in results if r["id"].startswith(f"{PREFIX}-result-t1-")]) == 60
    assert len([r for r in results if r["id"].startswith(f"{PREFIX}-result-t2-")]) == 64
    for rec in evaluations:
        relations = sorted(link["relation"] for link in rec["links"])
        assert relations == ["assessment", "data", "system"], f"{rec['id']}: {relations}"

    records.sort(key=lambda r: r["id"])
    with open(out_path, "w") as handle:
        for rec in records:
            handle.write(json.dumps(rec, ensure_ascii=False) + "\n")
    counts = {}
    for rec in records:
        counts[rec["kind"]] = counts.get(rec["kind"], 0) + 1
    print(f"{len(records)} records -> {out_path}")
    for kind in sorted(counts):
        print(f"  {kind}: {counts[kind]}")


if __name__ == "__main__":
    main()
