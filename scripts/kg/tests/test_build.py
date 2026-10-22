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
import contradictions  # noqa: E402
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

    def test_shacl_ignores_violations_only_on_context_records(self) -> None:
        broken = fixture()
        broken.add((ID.result1, RB.evaluation, ID.eval2))
        conforms, _ = build.validate(broken, set(), asserted_only=True, context={str(ID.result1)})
        self.assertTrue(conforms)
        conforms, report = build.validate(broken, set(), asserted_only=True, context={str(ID.eval2)})
        self.assertFalse(conforms)
        self.assertIn(str(ID.result1), report)

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

    def test_shape_groups_cover_every_targeted_shape_once(self) -> None:
        def targeted(shapes: rdflib.Graph) -> set:
            return {shape for target in build.TARGETS for shape in shapes.subjects(target, None)}

        load = lambda: rdflib.Graph().parse(build.SHAPES, format="turtle").parse(build.ATTRIBUTE_SHAPES, format="turtle")
        everything = targeted(load())
        groups = [targeted(build.shard_shapes(load(), index, 4)) for index in range(1, 5)]
        self.assertEqual(set().union(*groups), everything)
        self.assertEqual(sum(len(group) for group in groups), len(everything))

    def test_shape_groups_find_what_one_run_finds(self) -> None:
        full, _ = build.validate(fixture(), set())
        self.assertFalse(full)
        groups = [build.validate(fixture(), set(), shard=(index, 3))[0] for index in range(1, 4)]
        self.assertFalse(all(groups))
        conforms, report = build.validate(fixture(), set(), asserted_only=True)
        self.assertTrue(conforms, report)
        for index in range(1, 4):
            conforms, report = build.validate(fixture(), set(), asserted_only=True, shard=(index, 3))
            self.assertTrue(conforms, report)

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


def scored(g: rdflib.Graph, name: str, system: URIRef, source: URIRef, value: str, qualifier: str,
           protocol: URIRef = ID.protocol, metric: str = "auroc", direction: str = "higher") -> URIRef:
    """One evaluation and its result: `system` scored `value` on `protocol` in `source`."""
    evaluation, result = ID[f"eval-{name}"], ID[f"result-{name}"]
    record(g, evaluation, RB.Evaluation, testedSystem=system, testedOn=protocol, dataset=ID.data)
    record(g, result, RB.Result, evaluation=evaluation, source=source)
    g.add((result, RB.metric, V("metric", metric)))
    g.add((result, RB.unit, V("unit", "unitless")))
    g.add((result, RB.metricDirection, V("direction", direction)))
    g.add((result, RB.metricQualifier, Literal(qualifier)))
    g.add((result, RB.printedValue, Literal(value)))
    g.add((result, MLS.hasValue, Literal(value, datatype=rdflib.XSD.decimal)))
    return result


def disagreement(outlier_system: URIRef = ID.modelB, outlier_values: tuple[str, str] = ("0.70", "0.80")) -> rdflib.Graph:
    """Studies 1 and 2 put model A above model B on 6 and 3 subsets; study 3 puts B above A on 4.
    `outlier_system` is what study 3 tested for B (a configuration in some tests)."""
    g = rdflib.Graph()
    for node in (ID.study1, ID.study2, ID.study3):
        record(g, node, RB.Source)
    record(g, ID.modelA, RB.Model)
    record(g, ID.modelB, RB.Model)
    record(g, ID.protocol, RB.Protocol)
    record(g, ID.data, RB.Dataset)
    for study, count in ((ID.study1, 6), (ID.study2, 3)):
        for i in range(count):
            name = f"{str(study)[-1]}-{i}"
            scored(g, f"{name}-a", ID.modelA, study, "0.90", f"subset {i}")
            scored(g, f"{name}-b", ID.modelB, study, "0.80", f"subset {i}")
    for i in range(4):
        scored(g, f"3-{i}-a", ID.modelA, ID.study3, outlier_values[0], f"subset {i}")
        scored(g, f"3-{i}-b", outlier_system, ID.study3, outlier_values[1], f"subset {i}")
    return g


class DiscrepancyTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.ontology = build.load_ontology()
        cls.rules = contradictions.load_rules()

    def derive(self, graph: rdflib.Graph) -> tuple[set, list[dict]]:
        return contradictions.derive(graph, build.infer(graph, self.ontology), self.ontology, self.rules)

    def reversals(self, report: list[dict]) -> list[dict]:
        return [d for d in report if d["rule"] == "ordering-reversal"]

    def test_flags_the_study_that_reverses_the_consensus(self) -> None:
        triples, report = self.derive(disagreement())
        [found] = self.reversals(report)
        self.assertEqual(found["outlier_sources"], ["study3"])
        self.assertEqual(found["consensus_sources"], ["study1", "study2"])
        self.assertEqual(found["consensus_higher"], "modelA")
        self.assertEqual(found["numbers"], {"outlier_comparisons": 4, "outlier_reversals": 4,
                                            "consensus_comparisons": 9, "consensus_agreements": 9})
        self.assertEqual((found["scope"], found["identity_basis"], found["severity"], found["review_state"]),
                         ("same-protocol", "reviewed", "high", "open"))
        self.assertEqual(len(found["outlier_results"]), 8)
        node = URIRef(build.ID + found["id"])
        self.assertIn((node, RDF.type, RB.OrderingReversal), triples)
        self.assertIn((node, RB.assertionMethod, contradictions.AUTOMATIC), triples)
        self.assertIn((node, RB.outlierSource, ID.study3), triples)
        self.assertEqual(contradictions.check_derived(triples), [])

    def test_does_not_flag_the_consensus_studies(self) -> None:
        _, report = self.derive(disagreement())
        self.assertEqual({tuple(d["outlier_sources"]) for d in report}, {("study3",)})

    def test_gap_outlier_needs_three_studies_on_one_protocol(self) -> None:
        _, report = self.derive(disagreement())
        [gap] = [d for d in report if d["rule"] == "gap-outlier"]
        self.assertEqual(gap["outlier_sources"], ["study3"])
        self.assertEqual(gap["reference_system"], "modelB")
        self.assertLess(gap["numbers"]["outlier_gap"], gap["numbers"]["consensus_gap_min"])

    def test_identifiers_and_output_are_deterministic(self) -> None:
        first, report = self.derive(disagreement())
        second, again = self.derive(disagreement())
        self.assertEqual(build.nquads(first, build.GRAPHS["derived"]), build.nquads(second, build.GRAPHS["derived"]))
        self.assertEqual(report, again)

    def test_ties_are_not_reversals(self) -> None:
        _, report = self.derive(disagreement(outlier_values=("0.800", "0.805")))
        self.assertEqual(self.reversals(report), [])

    def test_copied_results_do_not_count(self) -> None:
        graph = disagreement()
        for evaluation in [e for e in graph.subjects(RDF.type, RB.Evaluation) if str(e).startswith(str(ID["eval-3-"]))]:
            graph.add((evaluation, RB.origin, V("origin", "paper_compilation")))
        self.assertEqual(self.derive(graph)[1], [])

    def test_results_without_a_direction_do_not_count(self) -> None:
        graph = disagreement()
        for result in graph.subjects(RB.evaluation, None):
            if str(result).startswith(str(ID["result-3-"])):
                graph.set((result, RB.metricDirection, V("direction", "unknown")))
                graph.set((result, RB.metric, V("metric", "not-a-metric")))
        self.assertEqual(self.reversals(self.derive(graph)[1]), [])

    def test_unreviewed_configuration_links_are_used_and_marked(self) -> None:
        graph = disagreement(outlier_system=ID.configB)
        record(graph, ID.configB, RB.Configuration, configurationOf=ID.modelB)
        [found] = self.reversals(self.derive(graph)[1])
        self.assertEqual((found["identity_basis"], found["severity"]), ("unreviewed", "medium"))
        record(graph, ID.linkClaim, RB.Claim, subject=ID.configB, source=ID.study3)
        graph.add((ID.linkClaim, RB.claimField, Literal("links:configuration_of:modelB")))
        [found] = self.reversals(self.derive(graph)[1])
        self.assertEqual((found["identity_basis"], found["severity"]), ("reviewed", "high"))

    def test_a_review_claim_sets_the_state_and_method(self) -> None:
        graph = disagreement()
        [found] = self.reversals(self.derive(graph)[1])
        record(graph, ID.review, RB.Claim, subject=ID["result-3-0-a"], source=ID.study3)
        graph.add((ID.review, RB.claimField, Literal(contradictions.REVIEW_FIELD)))
        graph.add((ID.review, RB.discrepancyId, Literal(found["id"])))
        graph.add((ID.review, RB.value, Literal("confirmed-error")))
        triples, report = self.derive(graph)
        [found] = self.reversals(report)
        node = URIRef(build.ID + found["id"])
        self.assertEqual((found["review_state"], found["review_claim"]), ("confirmed-error", "review"))
        self.assertIn((node, RB.assertionMethod, contradictions.MANUAL), triples)
        self.assertIn((node, RB.reviewState, V("discrepancy-state", "confirmed-error")), triples)

    def test_check_refuses_statements_about_records(self) -> None:
        problems = contradictions.check_derived({(ID.result1, RB.status, V("status", "disputed"))})
        self.assertEqual(len(problems), 2)

    def test_derived_terms_are_declared_and_rules_are_concepts(self) -> None:
        vocab = rdflib.Graph().parse(build.VOCABULARY, format="turtle")
        for predicate in contradictions.DERIVED_PREDICATES - {RDF.type, RDFS.label}:
            self.assertIn((predicate, RDFS.label, None), vocab, predicate)
        for scheme, keys in (("discrepancy-rule", {"ordering-reversal", "gap-outlier"}),
                             ("discrepancy-state", contradictions.STATES)):
            for key in keys:
                self.assertIn((V(scheme, key), RDF.type, URIRef("http://www.w3.org/2004/02/skos/core#Concept")),
                              self.ontology, key)

    def test_no_record_property_specialises_a_derived_term(self) -> None:
        for predicate in contradictions.DERIVED_PREDICATES - {RDF.type, RDFS.label}:
            self.assertEqual(list(self.ontology.subjects(RDFS.subPropertyOf, predicate)), [], predicate)


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
