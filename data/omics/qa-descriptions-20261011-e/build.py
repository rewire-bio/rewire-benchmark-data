"""Issue #88 category-only descriptions, batch E: the 38 missense variant-effect
predictors from `qa-descriptions-20261011/scan.md`.

27 of them are described by Chen 2020 Table 1, which the record already cites:
that table gives each algorithm's features and its method. The other 11 are not
described in any cited source, so this batch adds the paper that introduces each
one as a source: AlphaMissense, ClinPred, gMVP, LIST-S2, MetaRNN, MisFit,
MutFormer, MutScore, PHACTboost, popEVE and VARITY.

Reads the original lines from origin/main, applies the changes below, writes
`methods.jsonl` in place and regenerates batch.jsonl (the new sources and one
metadata-correction claim per changed description, all needs_review).
  python3 -I data/omics/qa-descriptions-20261011-e/build.py           write
  python3 -I data/omics/qa-descriptions-20261011-e/build.py --check   check only
Run from the repository root.
"""
import hashlib
import json
import subprocess
import sys

BASE = "47a06e988e8b7db72b6f4d3404f1d4db7bb0ca88"  # origin/main when batches a to e were integrated
HERE = "data/omics/qa-descriptions-20261011-e"
NOTE = "Replace a category-only description with a sourced functional description (issue #88). Historical releases retain the original value."
METHODS = "data/entities/methods.jsonl"
MISSENSE = "Variant effect predictor for missense variants."
P = "qa-descriptions-20261011-e-source-"
CHEN = "somatic-oncogenicity-20261009-source-chen2020"
TABLE1 = "Table 1, Summary of 33 computational algorithms included in this study"


def source(id, name, url, artifact, version, retrieved_at, sha, licence, status, locator, scope, media):
    attrs = {"url": url, "artifact_url": artifact, "version": version, "retrieved_at": retrieved_at, "artifact_sha256": sha,
             "publication_status": status, "media_type": media, "source_locator": locator, "hash_scope": scope}
    if licence:
        attrs["licence"] = licence
    else:
        attrs["missing_metadata"] = {"licence": {"reason": "unreported", "note": "The retrieved record gives no licence"}}
    return {"id": id, "kind": "source", "name": name,
            "description": "Source text retrieved and hashed for the issue #88 category-only description fix.",
            "status": "needs_review", "facets": {}, "source_ids": [], "links": [], "attributes": attrs}


EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest/search?query="
FULLTEXT = "https://www.ebi.ac.uk/europepmc/webservices/rest/{}/fullTextXML"
ARXIV = "https://export.arxiv.org/api/query?id_list="
SEARCH_SCOPE = "SHA-256 of one retrieval of a Europe PMC REST search response. These responses are not byte-stable (a later retrieval can differ in JSON key order); the title and abstractText fields are the evidence."
XML_SCOPE = "SHA-256 of one retrieval of the Europe PMC full-text XML. These renderings are not always byte-stable; the article text is the evidence."
ARXIV_SCOPE = "SHA-256 of one retrieval of an arXiv API Atom response for this identifier. The response is not guaranteed byte-stable; the title and summary fields are the evidence."

SOURCES = [
    source(f"{P}alphamissense", "Abstract: Accurate proteome-wide missense variant effect prediction with AlphaMissense",
           "https://doi.org/10.1126/science.adg7492", f"{EPMC}DOI%3A%2210.1126/science.adg7492%22&format=json&resultType=core",
           "Europe PMC core record MED/37733863 (title and abstract), Science 2023", "2026-10-11T01:38:37Z",
           "ef691586b68410db2fca1d6e1908dc426d243b11fc5444bcfcf94d4fb632ce7a", None, "peer_reviewed",
           "abstractText", SEARCH_SCOPE, "application/json"),
    source(f"{P}clinpred", "Abstract: ClinPred: Prediction Tool to Identify Disease-Relevant Nonsynonymous Single-Nucleotide Variants",
           "https://doi.org/10.1016/j.ajhg.2018.08.005", f"{EPMC}DOI%3A%2210.1016/j.ajhg.2018.08.005%22&format=json&resultType=core",
           "Europe PMC core record MED/30220433 (title and abstract), American Journal of Human Genetics 2018", "2026-10-11T01:38:37Z",
           "63c0292fe97a07565c917ae562ca50bdb52f07a46d7052cfd66963026be63c63", None, "peer_reviewed",
           "abstractText", SEARCH_SCOPE, "application/json"),
    source(f"{P}gmvp", "Abstract: Predicting functional effect of missense variants using graph attention neural networks (gMVP)",
           "https://doi.org/10.1038/s42256-022-00561-w", f"{EPMC}DOI%3A%2210.1038/s42256-022-00561-w%22&format=json&resultType=core",
           "Europe PMC core record MED/37484202 (title and abstract), Nature Machine Intelligence 2022", "2026-10-11T01:38:38Z",
           "27c9af15fc3ab76243b896e115b66f0c2e02f306efce4d35876369f1e3410525", None, "peer_reviewed",
           "abstractText", SEARCH_SCOPE, "application/json"),
    source(f"{P}list-s2", "LIST-S2: taxonomy based sorting of deleterious missense mutations across species",
           "https://doi.org/10.1093/nar/gkaa288", FULLTEXT.format("PMC7319545"),
           "Europe PMC full-text XML for PMC7319545, Nucleic Acids Research 2020", "2026-10-11T01:38:38Z",
           "5867606de985e78a008b910e4a49c91e6f9ef4e3f37dc5bad92f98d7bf935d76", "CC-BY-NC-4.0", "peer_reviewed",
           "Abstract", XML_SCOPE, "application/xml"),
    source(f"{P}metarnn", "MetaRNN: differentiating rare pathogenic and rare benign missense SNVs and InDels using deep learning",
           "https://doi.org/10.1186/s13073-022-01120-z", FULLTEXT.format("PMC9548151"),
           "Europe PMC full-text XML for PMC9548151, Genome Medicine 2022", "2026-10-11T01:38:38Z",
           "cb6e5a519d5aa219681966f3e80b311e9539b280b619cb953515f8c10f09adcd", "CC-BY-4.0", "peer_reviewed",
           "Abstract; Background (flanking \u00b11 codon annotations read by bidirectional GRUs)", XML_SCOPE, "application/xml"),
    source(f"{P}misfit", "A probabilistic graphical model for estimating selection coefficients of nonsynonymous variants (MisFit)",
           "https://doi.org/10.1038/s41467-025-59937-2", FULLTEXT.format("PMC12092651"),
           "Europe PMC full-text XML for PMC12092651, Nature Communications 2025", "2026-10-11T01:38:39Z",
           "71c488bd8a8b8b7fa10f65cfb258c02b2fb93e4d93b1c2284dad7f8b3d8b3b4f", "CC-BY-NC-ND-4.0", "peer_reviewed",
           "Abstract", XML_SCOPE, "application/xml"),
    source(f"{P}mutformer", "Abstract: Deciphering the Language of Nature: A transformer-based language model for deleterious mutations in proteins (MutFormer)",
           "https://arxiv.org/abs/2110.14746", f"{ARXIV}2110.14746",
           "arXiv:2110.14746 (title and abstract)", "2026-10-11T01:38:41Z",
           "9e45051cd7f25c788f15a77569c0e3388d5de3d1037b3c87d5225aa8c1356c06", "CC-BY-4.0", "preprint",
           "summary", ARXIV_SCOPE, "application/atom+xml"),
    source(f"{P}mutscore", "Analysis of missense variants in the human genome reveals widespread gene-specific clustering and improves prediction of pathogenicity (MutScore)",
           "https://doi.org/10.1016/j.ajhg.2022.01.006", FULLTEXT.format("PMC8948164"),
           "Europe PMC full-text XML for PMC8948164, American Journal of Human Genetics 2022", "2026-10-11T01:38:39Z",
           "3c46c27459420339177d0df81f71538f0a45078001e13c8b309c9d7fb6907ee6", "CC-BY-NC-ND-4.0", "peer_reviewed",
           "Summary", XML_SCOPE, "application/xml"),
    source(f"{P}phactboost", "PHACTboost: A Phylogeny-Aware Pathogenicity Predictor for Missense Mutations via Boosting",
           "https://doi.org/10.1093/molbev/msae136", FULLTEXT.format("PMC11251492"),
           "Europe PMC full-text XML for PMC11251492, Molecular Biology and Evolution 2024", "2026-10-11T01:38:40Z",
           "d6fcbbffa7ddf488dfb4da57edb2a5234006b403db37a2ce059d1d3d6beffc93", "CC-BY-NC-4.0", "peer_reviewed",
           "Abstract", XML_SCOPE, "application/xml"),
    source(f"{P}popeve", "Proteome-wide model for human disease genetics (popEVE)",
           "https://doi.org/10.1038/s41588-025-02400-1", FULLTEXT.format("PMC12695638"),
           "Europe PMC full-text XML for PMC12695638, Nature Genetics 2025", "2026-10-11T01:38:40Z",
           "5995c0b15ea643adfbc7123beb9a9017aca518e4052c92088a5b5ae26e7781be", "CC-BY-NC-ND-4.0", "peer_reviewed",
           "Abstract", XML_SCOPE, "application/xml"),
    source(f"{P}varity", "Improved pathogenicity prediction for rare human missense variants (VARITY)",
           "https://doi.org/10.1016/j.ajhg.2021.08.012", FULLTEXT.format("PMC8546039"),
           "Europe PMC full-text XML for PMC8546039, American Journal of Human Genetics 2021", "2026-10-11T01:38:41Z",
           "8f0fc5ae7af02c855733196570c16805a39036fe2aad1119a0b159dd0be1a8f9", "CC-BY-4.0", "peer_reviewed",
           "Abstract", XML_SCOPE, "application/xml"),
]

# id -> (description, source ids cited by the claim, locator, sources to add to the record)
CHEN_ROW = {
    "candra": "Scores missense variants with a support vector machine over structural, evolutionary and genomic features together with the scores of published predictors.",
    "chasm": "Scores missense variants with a random forest over structural, evolutionary and genomic features.",
    "ctat": "Scores missense variants with principal-component ensembles of other predictors: the cancer ensemble combines TransFIC, FATHMM, CHASM and CanDrA, and the population ensemble combines SIFT, PolyPhen-2, MutationAssessor and VEST.",
    "dann": "Scores variants with a deep neural network over conservation, epigenetic signals, the scores of other predictors and genetic context.",
    "deogen2": "Scores missense variants with a random forest over evolutionary, protein, gene and pathway features together with PROVEAN scores.",
    "eigen": "Scores variants by an unsupervised spectral method that combines the scores of other tools, allele frequencies and epigenomic signals; the paper evaluates both the Eigen and the Eigen-PC variant.",
    "fathmm": "Scores missense variants with hidden Markov models over sequence homology; the paper evaluates both the disease-weighted and the cancer-weighted variant.",
    "fathmm-mkl": "Scores variants by multiple kernel learning over conservation and epigenomic signals.",
    "fathmm-xf": "Scores variants by multiple kernel learning over conservation, genomic features and epigenomic signals.",
    "genocanyon": "Scores a position by the posterior probability that it is functional, from unsupervised statistical learning over conservation and biochemical annotation.",
    "integrated-fitcons": "Scores the fitness consequences of a position by applying the INSIGHT evolutionary model to integrated epigenomic signals.",
    "lrt": "Scores a variant by a likelihood ratio test of codon neutrality from sequence homology.",
    "m-cap": "Scores missense variants with a gradient-boosted tree classifier over the scores of published predictors and conservation.",
    "metalr": "Scores missense variants with a logistic regression over nine prediction scores and 1000 Genomes allele frequencies.",
    "metasvm": "Scores missense variants with a radial-kernel support vector machine over nine prediction scores and 1000 Genomes allele frequencies.",
    "mpc": "Scores missense variants with a logistic regression over regional missense constraint, missense badness and PolyPhen-2 scores.",
    "mutationassessor": "Scores a substitution from sequence homology with a combinatorial entropy formalism.",
    "mutationtaster": "Scores variants with a naive Bayes classifier over conservation, genetic context and regulatory features.",
    "mutpred": "Scores missense variants with a random forest over protein structural and functional properties, conservation and SIFT scores.",
    "mvp": "Scores missense variants with a deep neural network over sequence and structural features, the scores of published predictors and conservation.",
    "polyphen2": "Scores missense variants with a naive Bayes classifier over eight sequence-based and three structure-based features; the paper evaluates both the HumDiv and the HumVar trained variant.",
    "primateai": "Scores missense variants with a deep residual neural network over sequence homology.",
    "provean": "Scores a substitution by the change it causes in an alignment score against homologous sequences.",
    "revel": "Scores missense variants with a random forest over the scores of published predictors.",
    "sift": "Position-specific scoring matrix built from sequence homology found by PSI-BLAST.",
    "transfic": "Transforms the functional impact scores of SIFT, PolyPhen-2 and MutationAssessor.",
    "vest4": "Scores missense variants with a random forest over amino-acid-related features, DNA context, conservation and protein structure.",
}
OWN_PAPER = {
    "alphamissense": ("An adaptation of AlphaFold, fine-tuned on human and primate variant population frequencies, that predicts missense variant pathogenicity from structural context and evolutionary conservation.", "abstractText"),
    "clinpred": ("Scores missense variants by combining two machine-learning algorithms over existing pathogenicity scores and gnomAD population allele frequencies, trained on confidently annotated ClinVar variants.", "abstractText"),
    "gmvp": ("Graph attention neural network whose nodes carry amino-acid features and whose edges are weighted by co-evolution strength, pooling information from the local protein context and from correlated distal positions.", "abstractText"),
    "list-s2": ("Quantifies the conservation of a position from local sequence identity and taxonomic distances in a multiple alignment, for sequences from any organism rather than human alone.", "Abstract"),
    "metarnn": ("Recurrent neural network over other predictors' scores, conservation scores and population allele frequencies, with flanking-codon annotations read by bidirectional gated recurrent units, trained to separate rare pathogenic from rare benign nonsynonymous variants; a companion model covers non-frameshift indels.", "Abstract; Background (flanking \u00b11 codon annotations read by bidirectional GRUs)"),
    "misfit": ("Graphical model that estimates the fitness effect of a missense variant, jointly modelling its molecular-level effect and its selection coefficient in humans, rather than predicting pathogenicity.", "Abstract"),
    "mutformer": ("Transformer language model over reference and mutated human protein sequences, combining self-attention and convolutional layers, pretrained on protein sequences and fine-tuned for deleteriousness prediction.", "summary"),
    "mutscore": ("Random forest that combines qualitative features of the DNA substitution with the within-gene positional clustering of pathogenic and benign missense variants.", "Summary"),
    "phactboost": ("Gradient-boosted tree classifier that combines PHACT phylogeny-aware scores with features from multiple sequence alignments and phylogenetic trees.", "Abstract"),
    "popeve": ("Deep generative model that combines evolutionary and human population data to score variant deleteriousness on a scale calibrated across the proteome.", "Abstract"),
    "varity": ("Predicts the pathogenicity of rare missense variants, trained on a larger reservoir of training variants whose accuracy and representativity are uncertain, excluding features informed by variant annotation and protein identity to limit circularity and bias.", "Abstract"),
}

CHANGES = {}
for key, text in CHEN_ROW.items():
    CHANGES[f"somatic-oncogenicity-20261009-method-{key}"] = (text, [CHEN], f"{CHEN}: {TABLE1}", [])
for key, (text, locator) in OWN_PAPER.items():
    CHANGES[f"somatic-oncogenicity-20261009-method-{key}"] = (text, [f"{P}{key}"], f"{P}{key}: {locator}", [f"{P}{key}"])


def git_lines(path):
    return subprocess.run(["git", "show", f"{BASE}:{path}"], check=True, capture_output=True, text=True).stdout.split("\n")


def dumps(record):
    return json.dumps(record, separators=(",", ":"), ensure_ascii=False)


# Added at integration (2026-10-11), after the independent review recorded in
# docs/reviews/2026-10-11-description-batches-a-e.md and this folder's review.json.
REVIEW = {
    "method": ["automated-source-review", "ai-assisted-source-review"],
    "reviewer": ["claude"],
    "reviewer_note": "Extractor: Claude integrator agent for issue #88. Reviewer: a separate Claude review agent, independent of the extractor; no human review claimed.",
    "date": "2026-10-11",
    "method_note": "Compared the store diff with origin/main, read each new description against its cited source passage and checked the licence of each new source record.",
    "note": 'Approved with two corrections, both applied: the MutFormer source licence is CC BY 4.0 per the arXiv abstract page, and the MetaRNN source locator now names the Background passage. Checked the 27 Chen 2020 descriptions row by row against Table 1 (PMC7033911) and spot-checked AlphaMissense, MisFit, popEVE, VARITY, MetaRNN, MutFormer and gMVP against their abstracts; accurate. Licences on the other new sources match Europe PMC.',
    "receipt": f"{HERE}/review.json",
}


def reviewed(record):
    record = json.loads(dumps(record))
    record["status"] = "source_checked"
    review = dict(REVIEW)
    if record["kind"] == "source":
        review["retrieval_url"] = record["attributes"]["artifact_url"]
    record["attributes"]["review"] = review
    return record


def sync(path, base, out, check):
    """Compare or apply only the lines this batch changes, so batches a to e share one store."""
    current = open(path, encoding="utf8").read().split("\n")
    index = {json.loads(line)["id"]: i for i, line in enumerate(current) if line}
    for old, new in zip(base, out):
        if old == new:
            continue
        i = index[json.loads(new)["id"]]
        if check:
            assert current[i] == new, f"{path}: {json.loads(new)['id']} differs from the build"
        current[i] = new
    if not check:
        open(path, "w", encoding="utf8").write("\n".join(current))


def main(check):
    base = git_lines(METHODS)
    out = list(base)
    claims, rows = [], []
    for i, line in enumerate(base):
        if not line:
            continue
        record = json.loads(line)
        change = CHANGES.get(record["id"])
        if not change:
            continue
        assert record["description"] == MISSENSE, record["id"]
        assert dumps(record) == line, record["id"]
        description, cited, locator, added = change
        new = json.loads(line)
        new["description"] = description
        for s in added:
            if s not in new["source_ids"]:
                new["source_ids"].append(s)
        assert set(cited) <= set(new["source_ids"]), record["id"]
        assert {k for k in record if record[k] != new[k]} <= {"description", "source_ids"}
        out[i] = dumps(new)
        digest = hashlib.sha256(f"{record['id']}:description:2026-10-11-e".encode()).hexdigest()[:20]
        claims.append({
            "id": f"metadata-correction-{digest}", "kind": "claim", "name": f"{record['name']}: description",
            "description": NOTE, "status": "needs_review", "facets": record["facets"], "source_ids": cited,
            "links": [{"relation": "subject", "target_id": record["id"]}],
            "attributes": {"field": "description", "previous_value": record["description"], "value": description,
                           "source_locator": locator},
        })
        rows.append(record["id"])
    assert len(rows) == len(CHANGES), sorted(set(CHANGES) - set(rows))
    sync(METHODS, base, out, check)
    batch = [dumps(reviewed(s)) for s in SOURCES] + [dumps(reviewed(c)) for c in sorted(claims, key=lambda c: c["id"])]
    text = "\n".join(batch) + "\n"
    if check:
        assert open(f"{HERE}/batch.jsonl", encoding="utf8").read() == text, "batch.jsonl differs from the build"
    else:
        open(f"{HERE}/batch.jsonl", "w", encoding="utf8").write(text)
    print(f"{len(rows)} descriptions changed; batch has {len(batch)} records ({len(claims)} correction claims, {len(SOURCES)} sources)")


if __name__ == "__main__":
    main("--check" in sys.argv)
