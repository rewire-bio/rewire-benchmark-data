"""Complete the knowledge-graph bundle: OWL 2 RL inference, checks and SHACL validation.

Reads the asserted graph written by `npm run kg -- export` (public/kg/asserted.nq), the
vocabulary (data/ontology/rb.ttl) and the pinned external vocabularies
(data/ontology/imports/), then writes into public/kg/:

  inferred.nq      new facts about records, sorted, in the inferred named graph
  derived.nq       discrepancies between studies' results (scripts/kg/contradictions.py),
                   in the derived named graph
  discrepancies.json  the same discrepancies as JSON, for the website; not part of the bundle
  ontology/        the vocabulary files the server loads into the ontology graph
  manifest.json    bundle format 1.0 (see rewire-bio/rdf-kg-mcp docs/bundle-format.md)

The build fails if the reasoner finds an inconsistency, if a protected link is inferred,
if a result's inferred system differs from what its evaluation tested, if SHACL
validation fails (data/ontology/shapes.ttl and attribute-shapes.ttl for the records,
derived-shapes.ttl for the derived graph), or if an accepted discrepancy_review claim names
a discrepancy that is not derived and not settled.

Usage: npm run kg:build   (or: python scripts/kg/build.py [--kg-dir public/kg])
       python scripts/kg/build.py --shapes-only [--kg-dir public/kg] [--context FILE] [--shard I/N]
         SHACL over the asserted graph and the vocabulary only, without inference: the
         check pull requests run on the whole exported store. `npm run records -- add`
         and `change` run it on a subset (`npm run kg -- subset`): the records they wrote,
         the records that link to them, and the records those link to. FILE lists the
         last group, one IRI per line; they are there only as link targets.
         --shard I/N checks only the I-th of N groups of targeted shapes, so CI can run
         the groups in parallel; together the N groups check every shape once.
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
import rdflib.collection
from rdflib import OWL, RDF, RDFS, BNode, URIRef

import contradictions

ROOT = Path(__file__).resolve().parents[2]
ONTOLOGY_DIR = ROOT / "data" / "ontology"
VOCABULARY = ONTOLOGY_DIR / "rb.ttl"
IMPORTS = ONTOLOGY_DIR / "imports"
SHAPES = ONTOLOGY_DIR / "shapes.ttl"
ATTRIBUTE_SHAPES = ONTOLOGY_DIR / "attribute-shapes.ttl"
ATTRIBUTE_DECLARATIONS = ONTOLOGY_DIR / "rb-attributes.ttl"
DERIVED_SHAPES = ONTOLOGY_DIR / "derived-shapes.ttl"
VOCAB_DIR = ROOT / "data" / "vocab"
MAPPING = ONTOLOGY_DIR / "mapping.json"

RB = rdflib.Namespace("https://benchmarks.rewire.it/vocab#")
SH = rdflib.Namespace("http://www.w3.org/ns/shacl#")
ID = "https://benchmarks.rewire.it/id/"
GRAPHS = {
    "asserted": "https://benchmarks.rewire.it/graph/asserted",
    "inferred": "https://benchmarks.rewire.it/graph/inferred",
    "derived": "https://benchmarks.rewire.it/graph/derived",
    "ontology": "https://benchmarks.rewire.it/graph/ontology",
}
MLS_HAS_VALUE = URIRef("http://www.w3.org/ns/mls#hasValue")

# Links that must only ever be asserted. Inferring any of them would let results move between
# records (families, aliases, models used by pipelines) without review.
PROTECTED = {
    RB.evaluation,
    RB.testedSystem,
    RB.testedOn,
    RB.dataset,
    RB.family,
    RB.variantOf,
    RB.configurationOf,
    RB.aliasOf,
    RB.usesModel,
    RB.assessedBy,
    RB.status,
    MLS_HAS_VALUE,
    OWL.sameAs,
}
# The asserted link whose target is what an evaluation tested.
SUBJECT_LINKS = [RB.testedSystem]

def in_vocabulary(predicate: URIRef, obj: object) -> bool:
    """Keep only facts stated in the rewire vocabulary: rb: links and rb: types.

    Superclasses and superproperties from the imported vocabularies (mls:InformationEntity,
    schema:Thing, obo:IAO_0000030, ...) follow from the ontology graph for any
    consumer that wants them; materialising them would restate every record in vaguer terms.
    """
    if predicate == RDF.type:
        return isinstance(obj, URIRef) and str(obj).startswith(str(RB))
    return str(predicate).startswith(str(RB))


class BuildError(Exception):
    pass


def ontology_files() -> list[Path]:
    """The vocabulary, pinned imports and controlled vocabularies (SKOS schemes)."""
    return [
        VOCABULARY,
        ATTRIBUTE_DECLARATIONS,
        *sorted(p for p in IMPORTS.iterdir() if p.suffix in (".ttl", ".nt")),
        *sorted(VOCAB_DIR.glob("*.ttl")),
    ]


def bundle_path(path: Path) -> str:
    """Where an ontology file sits in the bundle: ontology/rb.ttl, ontology/imports/..., ontology/vocab/..."""
    if path.is_relative_to(VOCAB_DIR):
        return f"ontology/vocab/{path.relative_to(VOCAB_DIR).as_posix()}"
    return f"ontology/{path.relative_to(ONTOLOGY_DIR).as_posix()}"


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


PROPERTY_AXIOMS = [RDFS.subPropertyOf, OWL.equivalentProperty, OWL.inverseOf, OWL.propertyDisjointWith,
                   RDFS.domain, RDFS.range]
PROPERTY_TYPES = [OWL.TransitiveProperty, OWL.SymmetricProperty, OWL.AsymmetricProperty, OWL.IrreflexiveProperty,
                  OWL.FunctionalProperty, OWL.InverseFunctionalProperty]


def axiom_properties(ontology: rdflib.Graph) -> set:
    """Every property that appears in a property axiom, as either side, or in a chain."""
    found = set()
    for predicate in PROPERTY_AXIOMS:
        for s, o in ontology.subject_objects(predicate):
            found.update(t for t in (s, o) if isinstance(t, URIRef))
    for kind in PROPERTY_TYPES:
        found.update(ontology.subjects(RDF.type, kind))
    for prop, head in ontology.subject_objects(OWL.propertyChainAxiom):
        found.add(prop)
        found.update(rdflib.collection.Collection(ontology, head))
    return found


def infer(asserted: rdflib.Graph, ontology: rdflib.Graph) -> set[tuple]:
    """Run the OWL 2 RL closure and return the new statements about records.

    The reasoner only sees statements an axiom can act on: types, and links whose property
    some axiom mentions. Text values and links such as dcterms:source or rb:area have no
    axioms, cannot produce a new fact, and made up about two thirds of the input."""
    closure = rdflib.Graph()
    active = axiom_properties(ontology)
    for triple in asserted:
        if triple[1] == RDF.type or triple[1] in active:
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
        if not in_vocabulary(p, o):
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


def without_inferred_paths(shapes: rdflib.Graph) -> rdflib.Graph:
    """Drop property shapes on links only the reasoner creates (property chains and inverses),
    for validating the asserted graph alone."""
    vocabulary = rdflib.Graph().parse(VOCABULARY, format="turtle")
    derived = set(vocabulary.subjects(OWL.propertyChainAxiom, None)) | set(vocabulary.subjects(OWL.inverseOf, None))
    for shape, prop in list(shapes.subject_objects(SH.property)):
        if shapes.value(prop, SH.path) in derived:
            shapes.remove((shape, SH.property, prop))
    return shapes


TARGETS = (SH.targetClass, SH.targetNode, SH.targetObjectsOf, SH.targetSubjectsOf)


def shard_shapes(shapes: rdflib.Graph, index: int, count: int) -> rdflib.Graph:
    """Keep the targets of the index-th (1-based) of count groups of targeted shapes and drop
    the others' targets. Untargeted shapes stay, so sh:node references still resolve."""
    targeted = sorted({shape for target in TARGETS for shape in shapes.subjects(target, None)}, key=str)
    for position, shape in enumerate(targeted):
        if position % count != index - 1:
            for target in TARGETS:
                shapes.remove((shape, target, None))
    return shapes


def validate(asserted: rdflib.Graph, inferred: set[tuple], asserted_only: bool = False,
             context: set[str] | None = None, shard: tuple[int, int] | None = None) -> tuple[bool, str]:
    """SHACL over the asserted and inferred statements, with the concept schemes mixed in so
    shapes can check that each controlled value is a concept of the right scheme, and the
    vocabulary mixed in so sh:class sees subclasses without running the reasoner.

    `context` names records (IRIs) that are in the graph only so that the checked records'
    links resolve. Violations on them or their nodes are ignored, since their own links
    lead to records outside the graph."""
    data = rdflib.Graph()
    for triple in asserted:
        data.add(triple)
    for triple in inferred:
        data.add(triple)
    shapes = rdflib.Graph().parse(SHAPES, format="turtle").parse(ATTRIBUTE_SHAPES, format="turtle")
    if asserted_only:
        shapes = without_inferred_paths(shapes)
    if shard:
        shapes = shard_shapes(shapes, *shard)
    data.parse(VOCABULARY, format="turtle")
    for path in sorted(VOCAB_DIR.glob("*.ttl")):
        data.parse(path, format="turtle")
    conforms, results, report = pyshacl.validate(data, shacl_graph=shapes, inference="none", advanced=False)
    if conforms or not context:
        return bool(conforms), str(report)
    kept = [result for result in results.subjects(RDF.type, SH.ValidationResult)
            if record_of(str(results.value(result, SH.focusNode))) not in context]
    if not kept:
        return True, "Conforms (violations only on context records)"
    lines = [f"Constraint violations on checked records: {len(kept)}"]
    for result in kept:
        path = results.value(result, SH.resultPath)
        lines.append(f"- {results.value(result, SH.focusNode)}{f' {path}' if path else ''}: "
                     f"{results.value(result, SH.resultMessage)}")
    return False, "\n".join(lines)


def validate_derived(triples: set[tuple]) -> tuple[bool, str]:
    """SHACL over the derived graph, with the vocabulary and concept schemes mixed in so the shapes
    can check rule, state and action concepts. Record IRIs the discrepancies point at are not
    loaded, so the shapes check only that they are IRIs."""
    data = rdflib.Graph()
    for triple in triples:
        data.add(triple)
    data.parse(VOCABULARY, format="turtle")
    for path in sorted(VOCAB_DIR.glob("*.ttl")):
        data.parse(path, format="turtle")
    shapes = rdflib.Graph().parse(DERIVED_SHAPES, format="turtle")
    conforms, _, report = pyshacl.validate(data, shacl_graph=shapes, inference="none", advanced=False)
    return bool(conforms), str(report)


def record_of(node: str) -> str:
    """The record IRI a node belongs to: the record itself, or <record>/<path> for its nodes."""
    return ID + node[len(ID):].split("/", 1)[0] if node.startswith(ID) else node


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
        "  ?result a rb:Result ; dcterms:source ?source ; rb:sourceLocator ?locator .\n"
        "  OPTIONAL { ?source schema:url ?url }\n"
        "} LIMIT 20",
    },
    {
        "title": "Open discrepancies between studies",
        "description": "Results from one study that disagree with other studies' results for the same systems. "
        "Each is a lead to investigate, found by a rule; the review state says whether anyone has decided it.",
        "query": "SELECT ?discrepancy ?summary ?severity ?scope ?state WHERE {\n"
        "  GRAPH <https://benchmarks.rewire.it/graph/derived> {\n"
        "    ?discrepancy a rb:Discrepancy ; rb:discrepancySummary ?summary ; rb:severity ?severity ;\n"
        "                 rb:discrepancyScope ?scope ; rb:reviewState ?state .\n"
        "  }\n"
        "} ORDER BY ?severity LIMIT 50",
    },
    {
        "title": "Discrepancies involving a system",
        "query": "SELECT ?discrepancy ?summary ?outlier WHERE {\n"
        "  ?discrepancy rb:comparedSystem ?system ; rb:discrepancySummary ?summary ; rb:outlierSource ?outlier .\n"
        '  ?system rdfs:label ?name FILTER(CONTAINS(?name, "AlphaGenome"))\n'
        "}",
    },
    {
        "title": "Asserted facts only",
        "description": "Restrict to the asserted graph to see exactly what the records say.",
        "query": "SELECT ?p (COUNT(*) AS ?n) WHERE { GRAPH <https://benchmarks.rewire.it/graph/asserted> "
        "{ ?s ?p ?o } } GROUP BY ?p ORDER BY DESC(?n)",
    },
]


DERIVED_GRAPH = "<https://benchmarks.rewire.it/graph/derived>"
STATE = "https://benchmarks.rewire.it/vocab/discrepancy-state/"
UNSETTLED = (f"FILTER(?state NOT IN (<{STATE}explained>, <{STATE}confirmed-error>, <{STATE}false-positive>))")
SEVERITY_RANK = 'BIND(IF(?severity = "high", 0, IF(?severity = "medium", 1, 2)) AS ?rank)'

# Parameterised queries for rdf-kg-mcp's list_queries and run_query (bundle format, rdf-kg-mcp
# v0.2.0). A parameter appears as $name; the server puts in the validated value. An optional
# parameter left unset stays an unbound variable, so it is only used in FILTER(COALESCE(?x = $p, true)),
# and never in the SELECT list or BOUND().
NAMED_QUERIES = [
    {
        "name": "open_discrepancies",
        "title": "Open discrepancies between studies",
        "description": "Discrepancies not yet settled as explained, a confirmed error or a false positive, most "
        "severe first. Each is a lead found by a rule, not a finding that a result is wrong.",
        "sparql": "SELECT ?discrepancy ?severity ?state ?rule ?scope ?summary WHERE {\n"
        f"  GRAPH {DERIVED_GRAPH} {{\n"
        "    ?discrepancy a rb:Discrepancy ; rb:severity ?severity ; rb:reviewState ?state ;\n"
        "                 rb:discrepancyRule ?rule ; rb:discrepancyScope ?scope ; rb:discrepancySummary ?summary .\n"
        "  }\n"
        "  FILTER(COALESCE(?severity = $severity, true))\n"
        f"  {UNSETTLED}\n"
        f"  {SEVERITY_RANK}\n"
        "} ORDER BY ?rank ?discrepancy",
        "params": [
            {"name": "severity", "type": "string", "required": False,
             "description": "Only discrepancies of this severity: high, medium or low. Leave unset for all."},
        ],
    },
    {
        "name": "discrepancies_for_system",
        "title": "Discrepancies involving a model or method",
        "description": "Every discrepancy, settled or not, that compares the given model or method. Configurations "
        "are compared as the model or method they configure, so pass the model or method IRI.",
        "sparql": "SELECT ?discrepancy ?other ?otherName ?severity ?state ?summary WHERE {\n"
        f"  GRAPH {DERIVED_GRAPH} {{\n"
        "    ?discrepancy rb:comparedSystem $system , ?other ; rb:severity ?severity ; rb:reviewState ?state ;\n"
        "                 rb:discrepancySummary ?summary .\n"
        "    FILTER(?other != $system)\n"
        "  }\n"
        "  OPTIONAL { ?other rdfs:label ?otherName }\n"
        f"  {SEVERITY_RANK}\n"
        "} ORDER BY ?rank ?discrepancy",
        "params": [
            {"name": "system", "type": "iri", "required": True,
             "description": "The model or method, e.g. id:catalog-model-alphagenome."},
        ],
    },
    {
        "name": "discrepancy_history",
        "title": "Follow-up history of a discrepancy",
        "description": "What was done about one discrepancy, in revision order: each accepted discrepancy_review "
        "claim is one action, with the state it left, its date, a link and when to check again.",
        "sparql": "SELECT ?revision ?actionType ?state ?date ?url ?nextCheck ?claim WHERE {\n"
        f"  GRAPH {DERIVED_GRAPH} {{\n"
        "    $discrepancy rb:hasAction ?action .\n"
        "    ?action rb:actionRevision ?revision ; rb:resultingState ?state ; rb:reviewClaim ?claim .\n"
        "    OPTIONAL { ?action rb:actionType ?actionType }\n"
        "    OPTIONAL { ?action rb:actionDate ?date }\n"
        "    OPTIONAL { ?action rb:actionUrl ?url }\n"
        "    OPTIONAL { ?action rb:nextCheck ?nextCheck }\n"
        "  }\n"
        "} ORDER BY ?revision",
        "params": [
            {"name": "discrepancy", "type": "iri", "required": True,
             "description": "The discrepancy, e.g. id:discrepancy-0123456789abcdef."},
        ],
    },
    {
        "name": "contested_results_for_use_case",
        "title": "Contested results for a use case",
        "description": "Results on the protocols a use case is assessed by that an unsettled discrepancy rests on, "
        "as the outlier study's result or as part of the consensus. Contested results are flagged, not withheld.",
        "sparql": "SELECT DISTINCT ?result ?role ?discrepancy ?severity ?state ?summary WHERE {\n"
        "  $use_case rb:assessedBy ?protocol .\n"
        "  ?result rb:resultOn ?protocol .\n"
        f"  GRAPH {DERIVED_GRAPH} {{\n"
        '    { ?discrepancy rb:outlierResult ?result . BIND("outlier" AS ?role) }\n'
        '    UNION { ?discrepancy rb:consensusResult ?result . BIND("consensus" AS ?role) }\n'
        "    ?discrepancy rb:severity ?severity ; rb:reviewState ?state ; rb:discrepancySummary ?summary .\n"
        "  }\n"
        f"  {UNSETTLED}\n"
        f"  {SEVERITY_RANK}\n"
        "} ORDER BY ?rank ?discrepancy ?role ?result",
        "params": [
            {"name": "use_case", "type": "iri", "required": True,
             "description": "The use case record, e.g. id:use-case-splicing-follow-up."},
        ],
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
    rules = contradictions.load_rules()
    result = contradictions.derive(asserted, inferred, ontology, rules)
    derived, discrepancies = result.triples, result.report
    problems = contradictions.check_derived(derived)
    if problems:
        raise BuildError("The discrepancy rules wrote statements they may not:\n  " + "\n  ".join(problems))
    if result.problems:
        raise BuildError("Discrepancy review claims do not match the derived discrepancies:\n  "
                         + "\n  ".join(result.problems[:20]))
    conforms, report = validate_derived(derived)
    if not conforms:
        raise BuildError("SHACL validation of the derived graph failed:\n" + report[:5000])
    print(f"Derived {len(discrepancies)} discrepancies; left out {result.excluded['disputed']} disputed results "
          f"and {result.excluded['concern']} under an evidence concern", file=sys.stderr)

    (kg_dir / "inferred.nq").write_text(nquads(inferred, GRAPHS["inferred"]), "utf-8")
    (kg_dir / "derived.nq").write_text(nquads(derived, GRAPHS["derived"]), "utf-8")
    (kg_dir / "discrepancies.json").write_text(json.dumps(
        {"schema_version": 3, "release_id": exported["release_id"], "rules": rules, "excluded": result.excluded,
         "discrepancies": discrepancies}, indent=2, ensure_ascii=False) + "\n", "utf-8")
    target = kg_dir / "ontology"
    if target.exists():
        shutil.rmtree(target)
    files: dict[str, dict] = {"asserted.nq": exported["files"]["asserted.nq"]}
    files["inferred.nq"] = {"sha256": sha256(kg_dir / "inferred.nq"), "quads": len(inferred)}
    files["derived.nq"] = {"sha256": sha256(kg_dir / "derived.nq"), "quads": len(derived)}
    for path in ontology_files():
        relative = bundle_path(path)
        dest = kg_dir / relative
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, dest)
        entry: dict = {"graph": GRAPHS["ontology"], "sha256": sha256(dest)}
        if path.suffix == ".nt":
            entry["triples"] = count_lines(dest)
        files[relative] = entry

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
        "inferences in a separate graph, and discrepancies between studies' results in a derived graph.",
        "homepage": "https://github.com/rewire-bio/rewire-benchmark-data",
        "graphs": GRAPHS,
        "graph_descriptions": {
            "derived": "Discrepancies between studies' results found by the rules in scripts/kg/contradictions.py, "
            "with their review state and follow-up actions. Each is a lead for review, not a finding that a "
            "result is wrong.",
        },
        "files": dict(sorted(files.items())),
        "prefixes": {
            **mapping["prefixes"],
            "id": ID,
            "skos": "http://www.w3.org/2004/02/skos/core#",
            **{p.stem: f"https://benchmarks.rewire.it/vocab/{p.stem}/" for p in sorted(VOCAB_DIR.glob("*.ttl"))},
        },
        "label_predicates": ["rdfs:label", "skos:prefLabel", "skos:altLabel"],
        "mapping_sha256": exported["mapping_sha256"],
        "inferred": {
            "reasoner": {"name": "owlrl", "version": importlib.metadata.version("owlrl"), "profile": "OWL 2 RL"},
            "rdflib": importlib.metadata.version("rdflib"),
            "vocabulary_sha256": sha256(VOCABULARY),
            "kept": "New statements about records in the rewire vocabulary: rb: links and rb: types. "
            "Superclasses and superproperties from imported vocabularies are left to the ontology graph. "
            "Protected links are never inferred.",
            "by_predicate": dict(sorted(by_predicate.items())),
        },
        "derived": {
            "generator": "scripts/kg/contradictions.py",
            "generator_sha256": sha256(Path(contradictions.__file__)),
            "rules": "data/ontology/discrepancy-rules.json",
            "rules_sha256": sha256(contradictions.RULES),
            "kept": "Discrepancies only: SEPIO assertions that one study's results disagree with other "
            "studies' results for the same systems. No record's status, value or links are derived.",
            "discrepancies": len(discrepancies),
            "by_rule": dict(sorted(Counter(d["rule"] for d in discrepancies).items())),
            "by_severity": dict(sorted(Counter(d["severity"] for d in discrepancies).items())),
            "by_review_state": dict(sorted(Counter(d["review_state"] for d in discrepancies).items())),
            "excluded": result.excluded,
            "retired_reviews": result.retired,
            "shapes": "data/ontology/derived-shapes.ttl",
            "shapes_sha256": sha256(DERIVED_SHAPES),
            "discrepancies_json_sha256": sha256(kg_dir / "discrepancies.json"),
        },
        "shacl": {
            "conforms": True,
            "engine": f"pyshacl {importlib.metadata.version('pyshacl')}",
            "shapes": "data/ontology/shapes.ttl",
            "shapes_sha256": sha256(SHAPES),
            "attribute_shapes": "data/ontology/attribute-shapes.ttl",
            "attribute_shapes_sha256": sha256(ATTRIBUTE_SHAPES),
        },
        "example_queries": EXAMPLE_QUERIES,
        "queries": NAMED_QUERIES,
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
    parser.add_argument("--shapes-only", action="store_true", help="SHACL on the asserted graph, no inference")
    parser.add_argument("--context", help="with --shapes-only: file of record IRIs present only as link targets")
    parser.add_argument("--shard", help="with --shapes-only, check only group I of N targeted shapes (I/N)")
    args = parser.parse_args()
    try:
        if args.shapes_only:
            shard = tuple(int(part) for part in args.shard.split("/")) if args.shard else None
            if shard and not (len(shard) == 2 and 1 <= shard[0] <= shard[1]):
                raise BuildError(f"--shard must be I/N with 1 <= I <= N, not {args.shard}")
            started = time.monotonic()
            context = set(Path(args.context).read_text("utf-8").split()) if args.context else None
            asserted = load_asserted(Path(args.kg_dir) / "asserted.nq")
            loaded = time.monotonic()
            conforms, report = validate(asserted, set(), asserted_only=True, context=context, shard=shard)
            if not conforms:
                raise BuildError("SHACL validation failed:\n" + report[:5000])
            group = f", shape group {args.shard}" if shard else ""
            print(
                f"Records conform to the shapes ({loaded - started:.0f}s load, {time.monotonic() - loaded:.0f}s validate{group})",
                file=sys.stderr,
            )
            return
        build(Path(args.kg_dir))
    except BuildError as error:
        print(f"Knowledge-graph build failed: {error}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
