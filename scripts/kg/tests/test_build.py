"""Tests for the vocabulary rules, the inference step and SHACL validation.

Run with: npm run test:kg
"""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

import rdflib
from rdflib import OWL, RDF, RDFS, BNode, Literal, URIRef
from rdflib.collection import Collection

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import build  # noqa: E402
import extract_terms  # noqa: E402

RB = build.RB
ID = rdflib.Namespace(build.ID)
DCT = rdflib.Namespace("http://purl.org/dc/terms/")
MLS = rdflib.Namespace("http://www.w3.org/ns/mls#")
V = lambda scheme, key: URIRef(f"https://benchmarks.rewire.it/vocab/{scheme}/{key}")
LINK_ONLY = [RB.usesModel, RB.family, RB.variantOf, RB.configurationOf, RB.aliasOf, RB.measuredIn, RB.implementedBy, RB.usedIn, RB.usesData]


def expand(curie: str, prefixes: dict[str, str]) -> URIRef:
    prefix, local = curie.split(":", 1)
    return URIRef(prefixes[prefix] + local)


class VocabularyTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.vocab = rdflib.Graph().parse(build.VOCABULARY, format="turtle").parse(build.ATTRIBUTE_DECLARATIONS, format="turtle")
        cls.mapping = json.loads(build.MAPPING.read_text("utf-8"))

    def test_declares_every_rb_term_the_mapping_uses(self) -> None:
        prefixes = self.mapping["prefixes"]
        terms = {t for c in self.mapping["classes"].values() for t in c["types"]}
        for section in ("relations", "fields", "facets", "attributes", "review"):
            for entry in self.mapping[section].values():
                terms.add(entry["property"])
        terms.update({"rb:link", "rb:relation", "rb:target"})  # JSON-LD link objects
        missing = sorted(
            t for t in terms if t.startswith("rb:") and (expand(t, prefixes), RDFS.label, None) not in self.vocab
        )
        self.assertEqual(missing, [])

    def test_never_equates_records(self) -> None:
        self.assertEqual(list(self.vocab.triples((None, OWL.sameAs, None))), [])
        self.assertEqual(list(self.vocab.triples((None, OWL.equivalentProperty, None))), [])

    def test_protected_links_are_not_generalised(self) -> None:
        for prop in [*build.PROTECTED, *LINK_ONLY]:
            for kind in (OWL.TransitiveProperty, OWL.SymmetricProperty):
                self.assertNotIn((prop, RDF.type, kind), self.vocab, prop)
        for prop in LINK_ONLY:
            self.assertEqual(list(self.vocab.objects(prop, RDFS.subPropertyOf)), [], prop)
            self.assertEqual(list(self.vocab.objects(prop, OWL.inverseOf)), [], prop)
            self.assertEqual(list(self.vocab.subjects(OWL.inverseOf, prop)), [], prop)
        # Nothing may become one of the asserted-only links by subproperty reasoning.
        for prop in build.PROTECTED:
            self.assertEqual(list(self.vocab.subjects(RDFS.subPropertyOf, prop)), [], prop)

    def test_property_chains_avoid_family_and_model_links(self) -> None:
        for _, head in self.vocab.subject_objects(OWL.propertyChainAxiom):
            chain = list(Collection(self.vocab, head))
            self.assertTrue(set(chain).isdisjoint(LINK_ONLY), chain)

    def test_no_domains_or_ranges_on_rb_properties(self) -> None:
        for predicate in (RDFS.domain, RDFS.range):
            used = [s for s in self.vocab.subjects(predicate, None) if str(s).startswith(str(RB))]
            self.assertEqual(used, [], predicate)


def record(graph: rdflib.Graph, node: URIRef, kind: URIRef, **links: URIRef | list[URIRef]) -> None:
    graph.add((node, RDF.type, kind))
    graph.add((node, RDFS.label, Literal(str(node).rsplit("/", 1)[-1])))
    graph.add((node, RB.status, V("status", "source_checked")))
    for name, targets in links.items():
        for target in targets if isinstance(targets, list) else [targets]:
            predicate = DCT.source if name == "source" else RB[name]
            graph.add((node, predicate, target))


def fixture() -> rdflib.Graph:
    """A pipeline that uses a model, a configuration in a family, and a baseline, each evaluated."""
    g = rdflib.Graph()
    record(g, ID.paper, RB.Source)
    record(g, ID.model, RB.Model)
    record(g, ID.family, RB.Model)
    record(g, ID.alias, RB.Model, aliasOf=ID.model)
    record(g, ID.pipeline, RB.Pipeline, usesModel=ID.model)
    record(g, ID.config, RB.Configuration, family=ID.family, configurationOf=ID.model)
    record(g, ID.suite, RB.Benchmark)
    record(g, ID.bench, RB.Benchmark, partOf=ID.suite)
    record(g, ID.task, RB.Task, partOf=ID.bench)
    record(g, ID.protocol, RB.Protocol, partOf=ID.bench)
    record(g, ID.data, RB.Dataset)
    record(g, ID.subset, RB.DatasetSubset, usedIn=ID.protocol)
    record(g, ID.eval1, RB.Evaluation, testedSystem=ID.pipeline, testedOn=ID.task, dataset=ID.subset)
    record(g, ID.eval2, RB.Evaluation, testedSystem=ID.config, testedOn=ID.protocol, dataset=ID.data)
    record(g, ID.result1, RB.Result, evaluation=ID.eval1, source=ID.paper)
    record(g, ID.result2, RB.Result, evaluation=ID.eval2, source=ID.paper)
    for result in (ID.result1, ID.result2):
        g.add((result, RB.metric, V("metric", "auroc")))
        g.add((result, RB.unit, V("unit", "unitless")))
        g.add((result, RB.metricDirection, V("direction", "higher")))
        g.add((result, RB.printedValue, Literal("0.91")))
        g.add((result, MLS.hasValue, Literal("0.91", datatype=rdflib.XSD.decimal)))
    record(g, ID.baseline, RB.Baseline, measuredIn=ID.eval2, implementedBy=ID.config)
    record(g, ID.claim, RB.Claim, subject=ID.result1, source=ID.paper)
    return g


class InferenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.ontology = build.load_ontology()
        cls.asserted = fixture()
        cls.inferred = build.infer(cls.asserted, cls.ontology)

    def objects(self, subject: URIRef, predicate: URIRef) -> set:
        return {o for s, p, o in self.inferred if s == subject and p == predicate}

    def test_results_attach_only_to_what_was_tested(self) -> None:
        self.assertEqual(self.objects(ID.result1, RB.resultFor), {ID.pipeline})
        self.assertEqual(self.objects(ID.result2, RB.resultFor), {ID.config})
        targets = {o for _, p, o in self.inferred if p == RB.resultFor}
        self.assertTrue(targets.isdisjoint({ID.model, ID.family, ID.alias}))
        build.check_inferred(self.asserted, self.inferred)

    def test_evaluation_links_are_asserted_not_inferred(self) -> None:
        for prop in (RB.testedSystem, RB.testedOn, RB.dataset):
            self.assertEqual({o for s, p, o in self.inferred if p == prop}, set(), prop)
        self.assertEqual(self.objects(ID.config, RB.testedIn), {ID.eval2})

    def test_suites_are_transitive(self) -> None:
        self.assertEqual(self.objects(ID.task, RB.within), {ID.bench, ID.suite})
        self.assertEqual(self.objects(ID.result2, RB.resultWithin), {ID.bench, ID.suite})
        self.assertEqual(self.objects(ID.suite, RB.contains), {ID.bench, ID.task, ID.protocol})
        self.assertEqual(self.objects(ID.result1, RB.resultOnDataset), {ID.subset})

    def test_types_follow_the_class_hierarchy(self) -> None:
        self.assertIn(RB.Dataset, self.objects(ID.subset, RDF.type))
        self.assertIn(RB.System, self.objects(ID.pipeline, RDF.type))
        self.assertIn(RB.Assessment, self.objects(ID.protocol, RDF.type))
        # Imported superclasses stay in the ontology graph rather than being restated per record.
        self.assertNotIn(URIRef("http://purl.obolibrary.org/obo/OBI_0000272"), self.objects(ID.protocol, RDF.type))
        self.assertNotIn(OWL.Thing, self.objects(ID.pipeline, RDF.type))

    def test_baselines_are_not_results_or_evaluations(self) -> None:
        self.assertEqual({p for s, p, _ in self.inferred if s == ID.baseline}, set())
        self.assertNotIn(ID.baseline, self.objects(ID.eval2, RB.hasResult))
        self.assertEqual(self.objects(ID.config, RB.testedIn), {ID.eval2})

    def test_keeps_only_record_statements_in_the_vocabulary(self) -> None:
        for s, p, o in self.inferred:
            self.assertTrue(str(s).startswith(build.ID), s)
            self.assertTrue(build.in_vocabulary(p, o), (p, o))
            self.assertNotIsInstance(o, BNode)
            self.assertNotIn(p, build.PROTECTED)

    def test_output_is_sorted_and_deterministic(self) -> None:
        text = build.nquads(self.inferred, build.GRAPHS["inferred"])
        again = build.nquads(build.infer(self.asserted, self.ontology), build.GRAPHS["inferred"])
        self.assertEqual(text, again)
        lines = text.splitlines()
        self.assertEqual(lines, sorted(lines))
        self.assertTrue(all(line.endswith(f"<{build.GRAPHS['inferred']}> .") for line in lines))

    def test_shacl_accepts_the_fixture(self) -> None:
        conforms, report = build.validate(self.asserted, self.inferred)
        self.assertTrue(conforms, report)

    def test_shacl_rejects_a_result_with_two_evaluations(self) -> None:
        broken = fixture()
        broken.add((ID.result1, RB.evaluation, ID.eval2))
        conforms, report = build.validate(broken, build.infer(broken, self.ontology))
        self.assertFalse(conforms)
        self.assertIn("evaluation", report)

    def test_shacl_rejects_excluded_records(self) -> None:
        broken = fixture()
        broken.set((ID.claim, RB.status, V("status", "excluded")))
        conforms, _ = build.validate(broken, build.infer(broken, self.ontology))
        self.assertFalse(conforms)

    def test_shacl_rejects_a_typed_subject_link_outside_an_evaluation(self) -> None:
        broken = fixture()
        broken.add((ID.config, RB.testedSystem, ID.model))  # a configuration does not test anything
        conforms, report = build.validate(broken, build.infer(broken, self.ontology))
        self.assertFalse(conforms)
        self.assertIn("Evaluation", report)

    def test_shacl_checks_review_and_retrieval_dates(self) -> None:
        broken = fixture()
        broken.add((ID.result1, RB.reviewDate, Literal("2026-10-09", datatype=rdflib.XSD.date)))
        broken.add((ID.result1, RB.reviewDate, Literal("2026-10-08", datatype=rdflib.XSD.date)))
        broken.add((ID.paper, RB.retrievedAt, Literal("yesterday")))
        conforms, report = build.validate(broken, build.infer(broken, self.ontology))
        self.assertFalse(conforms)
        self.assertIn("reviewDate", report)
        self.assertIn("retrievedAt", report)

    def test_shacl_rejects_values_outside_their_scheme(self) -> None:
        broken = fixture()
        broken.set((ID.result1, RB.metric, V("unit", "unitless")))  # a unit is not a metric
        broken.add((ID.model, RB.area, Literal("genomics")))  # free text, not a concept
        conforms, report = build.validate(broken, build.infer(broken, self.ontology))
        self.assertFalse(conforms)
        self.assertIn("vocab/metric/", report)

    def test_shacl_checks_attribute_datatypes_and_nodes(self) -> None:
        broken = fixture()
        broken.add((ID.result1, RB.denominator, Literal("many")))  # an integer attribute
        node = URIRef(str(ID.result1) + "/uncertainty")
        broken.add((ID.result1, RB.uncertainty, node))
        broken.add((node, RDF.type, RB.Uncertainty))
        broken.add((node, RB.uncertaintyType, V("uncertainty-type", "confidence_interval")))
        broken.add((node, RB.confidenceLevel, Literal("95", datatype=rdflib.XSD.decimal)))  # not a fraction
        missing = URIRef(str(ID.result2) + "/missing/seeds")
        broken.add((ID.result2, RB.missingValue, missing))
        broken.add((missing, RDF.type, RB.MissingValue))
        broken.add((missing, RB.missingField, Literal("seeds")))
        broken.add((missing, RB.missingReason, V("status", "discovered")))  # not a missingness concept
        conforms, report = build.validate(broken, build.infer(broken, self.ontology))
        self.assertFalse(conforms)
        self.assertIn("denominator", report)
        self.assertIn("confidenceLevel", report)
        self.assertIn("vocab/missingness/", report)

    def test_shacl_checks_derivation_nodes(self) -> None:
        graph = fixture()
        node = URIRef(str(ID.result1) + "/derivation")
        source = URIRef(str(ID.result1) + "/derivation/inputs/0")
        graph.add((ID.result1, RB.derivation, node))
        graph.add((node, RDF.type, RB.Derivation))
        graph.add((node, RB.derivationMethod, V("derivation-method", "computed-from-source-data")))
        graph.add((node, RB.derivationInput, source))
        graph.add((source, RDF.type, RB.DerivationInput))
        graph.add((source, RB.rowCount, Literal(310)))
        conforms, report = build.validate(graph, build.infer(graph, self.ontology))
        self.assertTrue(conforms, report)
        graph.set((source, RB.rowCount, Literal("many")))  # an integer field
        graph.set((node, RB.derivationMethod, V("review-method", "transcription")))  # another scheme
        conforms, report = build.validate(graph, build.infer(graph, self.ontology))
        self.assertFalse(conforms)
        self.assertIn("rowCount", report)
        self.assertIn("vocab/derivation-method/", report)
        graph.remove((node, RB.derivationInput, source))  # a derivation needs its inputs
        conforms, report = build.validate(graph, build.infer(graph, self.ontology))
        self.assertIn("derivationInput", report)

    def test_shapes_only_skips_links_only_inference_creates(self) -> None:
        conforms, report = build.validate(fixture(), set(), asserted_only=True)
        self.assertTrue(conforms, report)
        conforms, _ = build.validate(fixture(), set())
        self.assertFalse(conforms)

    def test_check_rejects_a_result_moved_to_another_system(self) -> None:
        moved = set(self.inferred) | {(ID.result1, RB.resultFor, ID.model)}
        with self.assertRaises(build.BuildError):
            build.check_inferred(self.asserted, moved)

    def test_check_rejects_inferred_protected_links(self) -> None:
        with self.assertRaises(build.BuildError):
            build.check_inferred(self.asserted, set(self.inferred) | {(ID.config, RB.family, ID.model)})

    def test_inconsistency_fails_the_build(self) -> None:
        ontology = rdflib.Graph()
        for triple in self.ontology:
            ontology.add(triple)
        ontology.add((RB.Result, OWL.disjointWith, RB.Evaluation))
        broken = fixture()
        broken.add((ID.result1, RDF.type, RB.Evaluation))
        with self.assertRaises(build.BuildError):
            build.infer(broken, ontology)


class ExtractTermsTest(unittest.TestCase):
    def test_keeps_terms_ancestors_and_english_labels(self) -> None:
        ex = rdflib.Namespace("https://example.org/")
        source = rdflib.Graph()
        source.add((ex.Protocol, RDF.type, OWL.Class))
        source.add((ex.Protocol, RDFS.subClassOf, ex.Plan))
        source.add((ex.Plan, RDFS.subClassOf, ex.Thing))
        source.add((ex.Protocol, RDFS.label, Literal("protocol", lang="en")))
        source.add((ex.Protocol, RDFS.label, Literal("protocole", lang="fr")))
        source.add((ex.Protocol, OWL.disjointWith, ex.Process))
        source.add((ex.Unrelated, RDF.type, OWL.Class))
        subset = extract_terms.extract(source, [ex.Protocol])
        self.assertIn((ex.Plan, RDFS.subClassOf, ex.Thing), subset)
        self.assertIn((ex.Protocol, RDFS.label, Literal("protocol", lang="en")), subset)
        self.assertNotIn((ex.Protocol, RDFS.label, Literal("protocole", lang="fr")), subset)
        self.assertNotIn((ex.Protocol, OWL.disjointWith, ex.Process), subset)
        self.assertFalse(any(subset.triples((ex.Unrelated, None, None))))


if __name__ == "__main__":
    unittest.main()
