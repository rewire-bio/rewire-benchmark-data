"""Issue #88 category-only descriptions, batch D: the 23 protein stability-change
(ddG) predictors and the 4 conservation or selection scores from
`qa-descriptions-20261011/scan.md`.

Most descriptions come from a benchmark source the record already cites, which
describes each tool in one or two sentences: Pancotti 2022 section 2.2, Chu 2024
and Dieckhaus 2024. Seven records have no such description in a cited source,
so this batch adds their method's own paper as a source: ABYSSAL, PROSTATA,
Stability Oracle, GERP, phastCons, phyloP and the background-selection B value.

Reads the original lines from origin/main, applies the changes below, writes
`methods.jsonl` in place and regenerates batch.jsonl (the new sources and one
metadata-correction claim per changed description, all needs_review).
  python3 -I data/omics/qa-descriptions-20261011-d/build.py           write
  python3 -I data/omics/qa-descriptions-20261011-d/build.py --check   check only
Run from the repository root.
"""
import hashlib
import json
import subprocess
import sys

BASE = "47a06e988e8b7db72b6f4d3404f1d4db7bb0ca88"  # origin/main when batches a to e were integrated
HERE = "data/omics/qa-descriptions-20261011-d"
NOTE = "Replace a category-only description with a sourced functional description (issue #88). Historical releases retain the original value."
METHODS = "data/entities/methods.jsonl"
DDG = "Protein stability-change (ddG) predictor."
CONSERVATION = "Conservation or selection score used as a predictor."
P = "qa-descriptions-20261011-d-source-"

PANCOTTI = "protein-stability-20261009-source-pancotti2022"
DIECKHAUS = "protein-stability-20261009-source-dieckhaus2024"
CHU = "protein-stability-20261009-source-chu2024"
EVALUATED = "2 Materials and methods/2.2 Evaluated methods"


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
SEARCH_SCOPE = "SHA-256 of one retrieval of a Europe PMC REST search response. These responses are not byte-stable (a later retrieval can differ in JSON key order); the title and abstractText fields are the evidence."
XML_SCOPE = "SHA-256 of one retrieval of the Europe PMC full-text XML. These renderings are not always byte-stable; the article text is the evidence."

SOURCES = [
    source(f"{P}abyssal", "Abstract: New mega dataset combined with deep neural network makes a progress in predicting impact of mutation on protein stability (ABYSSAL)",
           "https://doi.org/10.1101/2022.12.31.522396",
           f"{EPMC}DOI%3A%2210.1101/2022.12.31.522396%22&format=json&resultType=core",
           "Europe PMC preprint record PPR/PPR590902 (title and abstract), bioRxiv 2023", "2026-10-11T01:30:45Z",
           "6b8741e12f40c5074150beecba35f0000e6d39a88c270d9327adfbcc57cddabf", None, "preprint",
           "abstractText", SEARCH_SCOPE, "application/json"),
    source(f"{P}prostata", "PROSTATA: a framework for protein stability assessment using transformers",
           "https://doi.org/10.1093/bioinformatics/btad671", FULLTEXT.format("PMC10651431"),
           "Europe PMC full-text XML for PMC10651431, Bioinformatics 2023", "2026-10-11T01:30:46Z",
           "6f94f73ccd2a97c7dd08d0c5396b48df9fea17b464b678364000d27bb98e7e69", "CC-BY-4.0", "peer_reviewed",
           "Abstract; Results", XML_SCOPE, "application/xml"),
    source(f"{P}stability-oracle", "Stability Oracle: a structure-based graph-transformer framework for identifying stabilizing mutations",
           "https://doi.org/10.1038/s41467-024-49780-2", FULLTEXT.format("PMC11266546"),
           "Europe PMC full-text XML for PMC11266546, Nature Communications 2024", "2026-10-11T01:30:46Z",
           "8f33eefa7e621fde0fabb78775bd35ad7cd5c9f21852e91eb30f0c40c87bb657", "CC-BY-4.0", "peer_reviewed",
           "Abstract", XML_SCOPE, "application/xml"),
    source(f"{P}gerp", "Identifying a high fraction of the human genome to be under selective constraint using GERP++",
           "https://doi.org/10.1371/journal.pcbi.1001025", FULLTEXT.format("PMC2996323"),
           "Europe PMC full-text XML for PMC2996323, PLoS Computational Biology 2010", "2026-10-11T01:33:44Z",
           "b843d9b8b2e7ee9323c0236a727bf45a2a910830e8270a760c31cc1384a576a9", "CC-BY-4.0", "peer_reviewed",
           "Abstract", XML_SCOPE, "application/xml"),
    source(f"{P}phastcons", "Abstract: Evolutionarily conserved elements in vertebrate, insect, worm, and yeast genomes (phastCons)",
           "https://doi.org/10.1101/gr.3715005", f"{EPMC}DOI%3A%2210.1101/gr.3715005%22&format=json&resultType=core",
           "Europe PMC core record MED/16024819 (title and abstract), Genome Research 2005", "2026-10-11T01:30:45Z",
           "83aff0f66231f8dcd1e49a1308884a66a800e95e6529ee7d5d3df8b3d9280471", None, "peer_reviewed",
           "abstractText", SEARCH_SCOPE, "application/json"),
    source(f"{P}phylop", "Abstract: Detection of nonneutral substitution rates on mammalian phylogenies (phyloP)",
           "https://doi.org/10.1101/gr.097857.109", f"{EPMC}DOI%3A%2210.1101/gr.097857.109%22&format=json&resultType=core",
           "Europe PMC core record MED/19858363 (title and abstract), Genome Research 2010", "2026-10-11T01:30:46Z",
           "d25b40f27cb6adb2fa570010735d829ba99cd9dceb85e1cc011c390622b200b8", None, "peer_reviewed",
           "abstractText", SEARCH_SCOPE, "application/json"),
    source(f"{P}bstatistic", "Widespread genomic signatures of natural selection in hominid evolution (background selection B value)",
           "https://doi.org/10.1371/journal.pgen.1000471", FULLTEXT.format("PMC2669884"),
           "Europe PMC full-text XML for PMC2669884, PLoS Genetics 2009", "2026-10-11T01:30:47Z",
           "9bee2be2a1ef463dbfbf26bba15456b8a8e33aac1fd9bfff6fe3bf7073b3fcdf", "CC-BY-4.0", "peer_reviewed",
           "Results (definition of the B value)", XML_SCOPE, "application/xml"),
]

# id -> (description, source ids cited by the claim, locator, sources to add to the record)
CHANGES = {
    "protein-stability-20261009-method-acdc-nn": (
        "Neural-network predictor of the stability change on point mutation whose architecture is antisymmetric by construction, taking the amino acids neighbouring the mutation and multiple sequence alignments as input.",
        [PANCOTTI], EVALUATED, []),
    "protein-stability-20261009-method-ddgun": (
        "Untrained predictor that combines evolutionary information with statistical potentials in an antisymmetric linear score; the 3D version adds a structural statistical potential weighted by the accessibility of the mutated residue.",
        [PANCOTTI], EVALUATED, []),
    "protein-stability-20261009-method-mcsm": (
        "Predicts the effect of a point mutation on stability from graph-based structural signatures that encode the distance patterns between atoms in the residue environment.",
        [PANCOTTI], EVALUATED, []),
    "protein-stability-20261009-method-sdm": (
        "Statistical potential energy function that scores a mutation from environment-specific amino-acid substitution frequencies within homologous families, as a proxy for the free-energy difference between wild type and mutant.",
        [PANCOTTI], EVALUATED, []),
    "protein-stability-20261009-method-duet": (
        "Meta-predictor that combines the mCSM and SDM scores with a support vector machine.",
        [PANCOTTI], EVALUATED, []),
    "protein-stability-20261009-method-dynamut": (
        "Consensus machine-learning predictor that combines the effects of a mutation on stability and on dynamics as computed by DUET, Bio3D and ENCoM.",
        [PANCOTTI], EVALUATED, []),
    "protein-stability-20261009-method-foldx": (
        "Empirical force-field method that predicts the effect of a point mutation from a linear combination of free-energy terms, including an entropy contribution, Van der Waals forces, hydrogen bonds and electrostatic interactions.",
        [PANCOTTI], EVALUATED, []),
    "protein-stability-20261009-method-saafec-seq": (
        "Gradient-boosting decision-tree predictor that uses physico-chemical properties, sequence features and evolutionary information.",
        [PANCOTTI], EVALUATED, []),
    "protein-stability-20261009-method-mupro": (
        "Sequence-based support vector machine that encodes the residues in a window centred on the mutated position.",
        [PANCOTTI], EVALUATED, []),
    "protein-stability-20261009-method-rosetta": (
        "Computes the stability change as the difference in Rosetta energy between the simulated wild-type and mutant structures.",
        [PANCOTTI], EVALUATED, []),
    "protein-stability-20261009-method-thermonet": (
        "Deep 3D convolutional network that predicts the stability change from multi-channel voxel grids of biophysical properties derived from atom coordinates.",
        [PANCOTTI], EVALUATED, []),
    "protein-stability-20261009-method-premps": (
        "Random-forest regression predictor that uses evolutionary and structure-based features, trained on a dataset with equal numbers of stabilising and destabilising mutations.",
        [PANCOTTI], EVALUATED, []),
    "protein-stability-20261009-method-popmusic": (
        "Energy-function method that combines 13 statistical potentials with volume-dependent terms for the wild-type and mutant amino acids, weighted by the solvent accessibility of the mutated residue.",
        [PANCOTTI], EVALUATED, []),
    "protein-stability-20261009-method-maestro": (
        "Multi-agent predictor based on statistical scoring functions, combining an ensemble of neural networks, support vector regressors and multiple linear regressors into a consensus model.",
        [PANCOTTI], EVALUATED, []),
    "protein-stability-20261009-method-inps": (
        "Support vector method with a radial-basis-function kernel over BLOSUM62 substitution scores, the alignment-score difference between native and variant sequence, hydrophobicity and evolutionary information; the 3D version adds relative solvent accessibility and a structural statistical potential.",
        [PANCOTTI], EVALUATED, []),
    "protein-stability-20261009-method-i-mutant": (
        "Support vector method with a radial-basis-function kernel over 42 features, including temperature, pH, an encoding of the mutation, and an encoding of the spatial residue environment where a structure is available or of the nearest sequence neighbours otherwise.",
        [PANCOTTI], EVALUATED, []),
    "protein-stability-20261009-method-thermompnn": (
        "Deep neural network that predicts the stability change of a point mutation from an input structure, by transfer learning on features extracted from ProteinMPNN.",
        [DIECKHAUS], "Abstract", []),
    "protein-stability-20261009-method-rasp": (
        "Convolutional-neural-network stability predictor trained on Rosetta-computed stability changes, operating directly on the input protein structure.",
        [CHU], "Introduction", []),
    "protein-stability-20261009-method-esm-therm": (
        "Protein language model fine-tuned on the folding stability of 528,000 natural and de novo sequences from 461 protein domains, which also accommodates deletions, insertions and multiple-point mutations.",
        [CHU], "Abstract; Introduction", []),
    "protein-stability-20261009-method-elaspic-2": (
        "Stability predictor that operates on both an ESM sequence embedding and a graph-neural-network structural embedding.",
        [CHU], "Introduction", []),
    "protein-stability-20261009-method-abyssal": (
        "ESM-2 network with an added light-attention mechanism, trained on the mega-scale stability dataset, which predicts the stability change on single mutation and satisfies the antisymmetry property.",
        [f"{P}abyssal"], f"{P}abyssal: abstractText", [f"{P}abyssal"]),
    "protein-stability-20261009-method-prostata": (
        "Transformer-based model, built by knowledge transfer on a curated stability dataset, that predicts the change in protein stability on point mutation from sequence.",
        [f"{P}prostata"], f"{P}prostata: Abstract", [f"{P}prostata"]),
    "protein-stability-20261009-method-stability-oracle": (
        "Structure-based graph-transformer framework for identifying thermodynamically stabilising mutations, trained with thermodynamic permutations for data augmentation and structural amino-acid embeddings that represent a mutation from a single structure.",
        [f"{P}stability-oracle"], f"{P}stability-oracle: Abstract", [f"{P}stability-oracle"]),
    "somatic-oncogenicity-20261009-method-gerp": (
        "Scores selective constraint position by position in a multiple alignment by maximum-likelihood evolutionary rate estimation, and defines constrained elements from runs of high-scoring positions by dynamic programming.",
        [f"{P}gerp"], f"{P}gerp: Abstract", [f"{P}gerp"]),
    "somatic-oncogenicity-20261009-method-phastcons": (
        "Conservation score from a two-state phylogenetic hidden Markov model fitted to a multiple alignment by maximum likelihood, from which conserved elements are predicted.",
        [f"{P}phastcons"], f"{P}phastcons: abstractText", [f"{P}phastcons"]),
    "somatic-oncogenicity-20261009-method-phylop": (
        "Tests whether the substitution rate at a site departs from the neutral rate, in either direction and optionally within a particular clade of the phylogeny.",
        [f"{P}phylop"], f"{P}phylop: abstractText", [f"{P}phylop"]),
    "somatic-oncogenicity-20261009-method-bstatistic": (
        "The background-selection B value: the expected fraction of neutral diversity remaining at a site, computed from the local recombination rate and the density of conserved segments.",
        [f"{P}bstatistic"], f"{P}bstatistic: Results (definition of the B value)", [f"{P}bstatistic"]),
}


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
    "note": 'Approved. Checked the 16 Pancotti-derived descriptions word for word against PMC8921618 section 2.2, ESM therm, RaSP and ELASPIC-2 against Chu 2024, ThermoMPNN against Dieckhaus 2024, and ABYSSAL and phyloP against their abstracts; all match. Licences on the new sources are supported by Europe PMC, the PMC XML and Crossref.',
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
        assert record["description"] in (DDG, CONSERVATION), record["id"]
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
        digest = hashlib.sha256(f"{record['id']}:description:2026-10-11-d".encode()).hexdigest()[:20]
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
