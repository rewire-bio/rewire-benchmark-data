"""Complete the knowledge-graph bundle: OWL 2 RL inference, checks and SHACL validation.

Reads the asserted graph written by `npm run kg -- export` (public/kg/asserted.nq), the
vocabulary (data/ontology/rb.ttl) and the pinned external vocabularies
(data/ontology/imports/), then writes into public/kg/:

  inferred.nq      new facts about records, sorted, in the inferred named graph
  ontology/        the vocabulary files the server loads into the ontology graph
  manifest.json    bundle format 1.0 (see rewire-bio/rdf-kg-mcp docs/bundle-format.md)

The build fails if the reasoner finds an inconsistency, if a protected link is inferred,
if a result's inferred system differs from what its evaluation tested, or if SHACL
validation fails.

Usage: npm run kg:build   (or: python scripts/kg/build.py [--kg-dir public/kg])
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import shutil
import sys
import time
from collections import Counter
from collections.abc import Iterable
from pathlib import Path

import owlrl
import pyshacl
import rdflib
from owlrl.Namespaces import ERRNS
from rdflib import OWL, RDF, RDFS, BNode, URIRef

ROOT = Path(__file__).resolve().parents[2]
ONTOLOGY_DIR = ROOT / "data" / "ontology"
VOCABULARY = ONTOLOGY_DIR / "rb.ttl"
IMPORTS = ONTOLOGY_DIR / "imports"
SHAPES = ONTOLOGY_DIR / "shapes.ttl"
MAPPING = ONTOLOGY_DIR / "mapping.json"

RB = rdflib.Namespace("https://benchmarks.rewire.it/vocab#")
ID = "https://benchmarks.rewire.it/id/"
GRAPHS = {
    "asserted": "https://benchmarks.rewire.it/graph/asserted",
    "inferred": "https://benchmarks.rewire.it/graph/inferred",
    "ontology": "https://benchmarks.rewire.it/graph/ontology",
}
MLS_HAS_VALUE = URIRef("http://www.w3.org/ns/mls#hasValue")

# Links that must only ever be asserted. Inferring any of them would let results move between
# records (families, aliases, models used by pipelines) without review.
PROTECTED = {
    RB.evaluation,
    RB.evaluatedSubject,
    RB.configuration,
    RB.method,
    RB.pipeline,
    RB.service,
    RB.family,
    RB.variantOf,
    RB.aliasOf,
    RB.usesModel,
    RB.status,
    MLS_HAS_VALUE,
    OWL.sameAs,
}
# The asserted links whose targets are what an evaluation tested.
SUBJECT_LINKS = [RB.evaluatedSubject, RB.configuration, RB.method, RB.pipeline, RB.service]
# Generic types every resource gets under OWL 2 RL; they carry no information.
TRIVIAL_TYPES = {OWL.Thing, RDFS.Resource, OWL.NamedIndividual}


class BuildError(Exception):
    pass


def ontology_files() -> list[Path]:
    return [VOCABULARY, *sorted(p for p in IMPORTS.iterdir() if p.suffix in (".ttl", ".nt"))]


def load_ontology() -> rdflib.Graph:
    graph = rdflib.Graph()
    for path in ontology_files():
        graph.parse(path, format="nt" if path.suffix == ".nt" else "turtle")
    return graph


def load_asserted(path: Path) -> rdflib.Graph:
    dataset = rdflib.Dataset()
    dataset.parse(path, format="nquads")
    graph = rdflib.Graph()
    for s, p, o, _ in dataset.quads():
        graph.add((s, p, o))
    return graph


def infer(asserted: rdflib.Graph, ontology: rdflib.Graph) -> set[tuple]:
    """Run the OWL 2 RL closure and return the new statements about records."""
    closure = rdflib.Graph()
    for triple in asserted:
        closure.add(triple)
    for triple in ontology:
        closure.add(triple)
    owlrl.DeductiveClosure(owlrl.OWLRL_Semantics, axiomatic_triples=False, datatype_axioms=False).expand(closure)

    errors = sorted(str(m) for m in closure.objects(None, ERRNS.error))
    if errors:
        raise BuildError("The reasoner found inconsistencies:\n  " + "\n  ".join(errors[:20]))
    unsatisfiable = sorted(str(s) for s in closure.subjects(RDF.type, OWL.Nothing))
    if unsatisfiable:
        raise BuildError("Records typed owl:Nothing: " + ", ".join(unsatisfiable[:20]))

    merged = [
        (str(s), str(o))
        for s, o in closure.subject_objects(OWL.sameAs)
        if s != o and str(s).startswith(ID)
    ]
    if merged:
        raise BuildError(f"owl:sameAs was inferred between records, e.g. {merged[0]}")

    inferred = set()
    for s, p, o in closure:
        if (s, p, o) in asserted or (s, p, o) in ontology:
            continue
        if not isinstance(s, URIRef) or not str(s).startswith(ID):
            continue  # vocabulary-level inferences and literal or blank subjects
        if isinstance(o, BNode):
            continue  # membership of anonymous restriction classes
        if p == OWL.sameAs and s == o:
            continue
        if p == RDF.type and o in TRIVIAL_TYPES:
            continue
        inferred.add((s, p, o))
    return inferred


def check_inferred(asserted: rdflib.Graph, inferred: set[tuple]) -> None:
    protected = Counter(str(p) for _, p, _ in inferred if p in PROTECTED)
    if protected:
        raise BuildError(f"Protected links were inferred: {dict(protected)}")
    tested: dict[URIRef, set] = {}
    for link in SUBJECT_LINKS:
        for evaluation, system in asserted.subject_objects(link):
            tested.setdefault(evaluation, set()).add(system)
    for result, system in ((s, o) for s, p, o in inferred if p == RB.resultFor):
        evaluations = set(asserted.objects(result, RB.evaluation))
        allowed = set().union(*(tested.get(e, set()) for e in evaluations))
        if system not in allowed:
            raise BuildError(f"{result} was inferred to be a result for {system}, which its evaluation did not test")


def validate(asserted: rdflib.Graph, inferred: set[tuple]) -> tuple[bool, str]:
    data = rdflib.Graph()
    for triple in asserted:
        data.add(triple)
    for triple in inferred:
        data.add(triple)
    shapes = rdflib.Graph().parse(SHAPES, format="turtle")
    conforms, _, report = pyshacl.validate(data, shacl_graph=shapes, inference="none", advanced=False)
    return bool(conforms), str(report)


def nquads(triples: Iterable[tuple], graph: str) -> str:
    """Sorted N-Quads in one named graph."""
    nt = rdflib.Graph()
    for triple in triples:
        nt.add(triple)
    suffix = f" <{graph}> ."
    lines = sorted(line[: -len(" .")] + suffix for line in nt.serialize(format="nt").splitlines() if line.strip())
    return "\n".join(lines) + "\n" if lines else ""


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def count_lines(path: Path) -> int:
    return sum(1 for line in path.read_text("utf-8").splitlines() if line.strip() and not line.startswith("#"))


EXAMPLE_QUERIES = [
    {
        "title": "Results for a system, with assessment and dataset",
        "description": "Results reported for systems whose name contains ESM-2. Each result counts only for the "
        "system its evaluation tested: never for other members of its family or for pipelines that use it.",
        "query": "SELECT ?name ?metric ?value ?assessment ?dataset WHERE {\n"
        "  ?result rb:resultFor ?system ; rb:metric ?metric ; rb:printedValue ?value ;\n"
        "          rb:resultOn ?assessment ; rb:resultOnDataset ?dataset .\n"
        '  ?system rdfs:label ?name FILTER(CONTAINS(?name, "ESM-2"))\n'
        "} ORDER BY ?name LIMIT 100",
    },
    {
        "title": "Benchmarks by number of results",
        "query": "SELECT ?benchmark ?name (COUNT(?result) AS ?results) WHERE {\n"
        "  ?result rb:resultWithin ?benchmark . ?benchmark a rb:Benchmark ; rdfs:label ?name .\n"
        "} GROUP BY ?benchmark ?name ORDER BY DESC(?results) LIMIT 25",
    },
    {
        "title": "Systems tested on a benchmark",
        "query": "SELECT DISTINCT ?system ?name WHERE {\n"
        '  ?benchmark a rb:Benchmark ; rdfs:label "ProteinGym" .\n'
        "  ?evaluation rb:testedWithin ?benchmark ; rb:testedSystem ?system .\n"
        "  ?system rdfs:label ?name .\n"
        "} ORDER BY ?name",
    },
    {
        "title": "Sources behind a result",
        "query": "SELECT ?result ?source ?url ?locator WHERE {\n"
        "  ?result a rb:Result ; prov:wasDerivedFrom ?source ; rb:sourceLocator ?locator .\n"
        "  OPTIONAL { ?source schema:url ?url }\n"
        "} LIMIT 20",
    },
    {
        "title": "Asserted facts only",
        "description": "Restrict to the asserted graph to see exactly what the records say.",
        "query": "SELECT ?p (COUNT(*) AS ?n) WHERE { GRAPH <https://benchmarks.rewire.it/graph/asserted> "
        "{ ?s ?p ?o } } GROUP BY ?p ORDER BY DESC(?n)",
    },
]


def build(kg_dir: Path) -> dict:
    started = time.monotonic()
    manifest_path = kg_dir / "manifest.json"
    exported = json.loads(manifest_path.read_text("utf-8"))
    asserted_path = kg_dir / "asserted.nq"
    if sha256(asserted_path) != exported["files"]["asserted.nq"]["sha256"]:
        raise BuildError("asserted.nq does not match the export manifest; run npm run kg -- export first")

    asserted = load_asserted(asserted_path)
    ontology = load_ontology()
    print(f"Loaded {len(asserted)} asserted and {len(ontology)} ontology statements", file=sys.stderr)
    inferred = infer(asserted, ontology)
    check_inferred(asserted, inferred)
    print(f"Inferred {len(inferred)} statements in {time.monotonic() - started:.0f}s", file=sys.stderr)
    conforms, report = validate(asserted, inferred)
    if not conforms:
        raise BuildError("SHACL validation failed:\n" + report[:5000])

    (kg_dir / "inferred.nq").write_text(nquads(inferred, GRAPHS["inferred"]), "utf-8")
    target = kg_dir / "ontology"
    if target.exists():
        shutil.rmtree(target)
    files: dict[str, dict] = {"asserted.nq": exported["files"]["asserted.nq"]}
    files["inferred.nq"] = {"sha256": sha256(kg_dir / "inferred.nq"), "quads": len(inferred)}
    for path in ontology_files():
        relative = path.relative_to(ONTOLOGY_DIR).as_posix()
        dest = target / relative
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, dest)
        entry: dict = {"graph": GRAPHS["ontology"], "sha256": sha256(dest)}
        if path.suffix == ".nt":
            entry["triples"] = count_lines(dest)
        files[f"ontology/{relative}"] = entry

    mapping = json.loads(MAPPING.read_text("utf-8"))
    by_predicate = Counter(str(p) for _, p, _ in inferred)
    manifest = {
        "format_version": "1.0",
        "dataset": exported["dataset"],
        "version": exported["release_id"],
        "release_id": exported["release_id"],
        "title": "Rewire benchmark data",
        "description": "Reviewed biological benchmark records (models, methods, configurations, benchmarks, "
        "tasks, protocols, datasets, evaluations, results, sources and claims) as RDF, with OWL 2 RL "
        "inferences in a separate graph.",
        "homepage": "https://github.com/rewire-bio/rewire-benchmark-data",
        "graphs": GRAPHS,
        "files": dict(sorted(files.items())),
        "prefixes": {**mapping["prefixes"], "id": ID},
        "label_predicates": ["rdfs:label"],
        "mapping_sha256": exported["mapping_sha256"],
        "inferred": {
            "reasoner": {"name": "owlrl", "version": importlib.metadata.version("owlrl"), "profile": "OWL 2 RL"},
            "rdflib": importlib.metadata.version("rdflib"),
            "vocabulary_sha256": sha256(VOCABULARY),
            "kept": "New statements whose subject is a record; excludes blank nodes, owl:Thing typing and "
            "reflexive owl:sameAs. Protected links are never inferred.",
            "by_predicate": dict(sorted(by_predicate.items())),
        },
        "shacl": {
            "conforms": True,
            "engine": f"pyshacl {importlib.metadata.version('pyshacl')}",
            "shapes": "data/ontology/shapes.ttl",
            "shapes_sha256": sha256(SHAPES),
        },
        "example_queries": EXAMPLE_QUERIES,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", "utf-8")
    print(
        f"Wrote {len(inferred)} inferred quads and the bundle manifest for {exported['release_id']} "
        f"in {time.monotonic() - started:.0f}s",
        file=sys.stderr,
    )
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--kg-dir", default=str(ROOT / "public" / "kg"))
    args = parser.parse_args()
    try:
        build(Path(args.kg_dir))
    except BuildError as error:
        print(f"Knowledge-graph build failed: {error}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
