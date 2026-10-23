"""Tests for the vocabulary rules, the inference step and SHACL validation.

Run with: npm run test:kg
"""

from __future__ import annotations

import json
import re
import sys
import unittest
from functools import reduce
from unittest import mock
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
SCHEMA = rdflib.Namespace("https://schema.org/")
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

    def derived(self, graph: rdflib.Graph) -> contradictions.Derived:
        return contradictions.derive(graph, build.infer(graph, self.ontology), self.ontology, self.rules)

    def derive(self, graph: rdflib.Graph) -> tuple[set, list[dict]]:
        result = self.derived(graph)
        return result.triples, result.report

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

    def gaps(self, report: list[dict]) -> list[dict]:
        return [d for d in report if d["rule"] == "gap-outlier"]

    def test_gap_outlier_needs_three_studies_on_one_protocol(self) -> None:
        _, report = self.derive(disagreement())
        [gap] = self.gaps(report)
        self.assertEqual(gap["outlier_sources"], ["study3"])
        # Every study measured both models and neither is a baseline, so the first is the reference.
        self.assertEqual((gap["reference_system"], gap["systems"]), ("modelA", ["modelB", "modelA"]))
        self.assertGreater(gap["numbers"]["outlier_gap"], gap["numbers"]["consensus_gap_max"])
        self.assertEqual((gap["key"]["anchor"], gap["key"]["metric"]), ("protocol", "auroc"))

    def test_gap_reference_prefers_a_named_baseline(self) -> None:
        graph = disagreement()
        record(graph, ID.baselineB, RB.Baseline, implementedBy=ID.modelB)
        [gap] = self.gaps(self.derive(graph)[1])
        self.assertEqual(gap["reference_system"], "modelB")
        self.assertLess(gap["numbers"]["outlier_gap"], gap["numbers"]["consensus_gap_min"])

    def test_gap_rule_skips_a_group_without_a_shared_reference(self) -> None:
        graph = disagreement()
        # Study 2 compares model A with model C instead: no system is measured by every study.
        for subject in [r for r in graph.subjects(RB.testedSystem, ID.modelB) if str(r).startswith(str(ID["eval-2-"]))]:
            graph.set((subject, RB.testedSystem, ID.modelC))
        record(graph, ID.modelC, RB.Model)
        self.assertEqual(self.gaps(self.derive(graph)[1]), [])

    def test_lists_each_study_with_its_comparisons(self) -> None:
        [found] = self.reversals(self.derive(disagreement())[1])
        studies = found["studies"]
        self.assertEqual([(s["key"], s["role"], s["source_ids"]) for s in studies],
                         [("source:study3", "outlier", ["study3"]), ("source:study1", "consensus", ["study1"]),
                          ("source:study2", "consensus", ["study2"])])
        self.assertEqual([(s["higher"], s["ties"], s["gap"]) for s in studies],
                         [({"modelA": 0, "modelB": 4}, 0, None), ({"modelA": 6, "modelB": 0}, 0, None),
                          ({"modelA": 3, "modelB": 0}, 0, None)])
        for s in studies:
            self.assertEqual(sum(s["higher"].values()) + s["ties"], s["comparisons_total"])
            self.assertEqual(len(s["comparisons"]), s["comparisons_total"])
        first = studies[0]["comparisons"][0]
        self.assertEqual(first, {
            "protocol": "protocol", "dataset": "data", "metric": "auroc", "unit": "unitless", "qualifier": "subset 0",
            "split": None, "values": {"modelA": 0.7, "modelB": 0.8},
            "results": {"modelA": "result-3-0-a", "modelB": "result-3-0-b"}, "higher": "modelB"})
        self.assertEqual(sorted(r for s in studies[:1] for c in s["comparisons"] for r in c["results"].values()),
                         found["outlier_results"])

    def test_a_study_of_only_ties_is_listed_but_not_a_consensus_source(self) -> None:
        graph = disagreement()
        record(graph, ID.study4, RB.Source)
        for i in range(2):
            scored(graph, f"4-{i}-a", ID.modelA, ID.study4, "0.80", f"subset {i}")
            scored(graph, f"4-{i}-b", ID.modelB, ID.study4, "0.80", f"subset {i}")
        [found] = self.reversals(self.derive(graph)[1])
        self.assertEqual(found["consensus_sources"], ["study1", "study2"])
        tied = next(s for s in found["studies"] if s["key"] == "source:study4")
        self.assertEqual((tied["role"], tied["higher"], tied["ties"], tied["comparisons_total"]),
                         ("consensus", {"modelA": 0, "modelB": 0}, 2, 2))
        self.assertEqual({c["higher"] for c in tied["comparisons"]}, {None})

    def test_caps_the_comparisons_listed_per_study(self) -> None:
        with mock.patch.object(contradictions, "MAX_STUDY_COMPARISONS", 2):
            [found] = self.reversals(self.derive(disagreement())[1])
        outlier = found["studies"][0]
        self.assertEqual((len(outlier["comparisons"]), outlier["comparisons_total"]), (2, 4))
        self.assertEqual(sum(outlier["higher"].values()) + outlier["ties"], 4)

    def test_gap_outlier_studies_carry_their_median_gap(self) -> None:
        [gap] = self.gaps(self.derive(disagreement())[1])
        studies = gap["studies"]
        self.assertEqual([(s["key"], s["role"]) for s in studies],
                         [("source:study3", "outlier"), ("source:study1", "consensus"), ("source:study2", "consensus")])
        self.assertEqual(studies[0]["gap"], gap["numbers"]["outlier_gap"])
        self.assertEqual({s["gap"] for s in studies[1:]},
                         {gap["numbers"]["consensus_gap_min"], gap["numbers"]["consensus_gap_max"]})
        self.assertEqual(list(studies[0]["higher"]), gap["systems"])

    def test_identifier_hashes_the_canonical_key(self) -> None:
        [found] = self.reversals(self.derive(disagreement())[1])
        self.assertEqual(found["key"], {"rule": "ordering-reversal", "systems": ["modelA", "modelB"], "anchor": None,
                                        "metric": None, "outlier_study": "source:study3"})
        self.assertEqual(found["id"], contradictions.identifier(found["key"]))

    def test_adding_a_source_to_a_study_keeps_its_identifier(self) -> None:
        for doi in (None, "10.1000/Outlier"):
            graph = disagreement()
            graph.add((ID.study3, RB.retrievedAt, Literal("2026-01-01T00:00:00Z", datatype=rdflib.XSD.dateTime)))
            if doi:
                graph.add((ID.study3, RB.doi, Literal(doi)))
            before = {d["rule"]: d["id"] for d in self.derive(graph)[1]}
            # A later source that shares a result with study 3, with an IRI that sorts first, so it
            # now names the merged study.
            record(graph, ID.aSupplement, RB.Source)
            graph.add((ID.aSupplement, RB.retrievedAt, Literal("2026-05-01T00:00:00Z", datatype=rdflib.XSD.dateTime)))
            graph.add((ID["result-3-0-a"], DCT.source, ID.aSupplement))
            _, report = self.derive(graph)
            self.assertEqual({d["rule"]: d["id"] for d in report}, before, doi)
            self.assertIn("aSupplement", self.reversals(report)[0]["outlier_sources"])
            self.assertEqual(self.reversals(report)[0]["key"]["outlier_study"],
                             "doi:10.1000/outlier" if doi else "source:study3")

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

    def test_files_from_one_repository_are_one_study(self) -> None:
        graph = disagreement()
        for study, path in ((ID.study2, "blob/abc/summary.csv"), (ID.study3, "abc/assay_level.csv")):
            host = "github.com" if study == ID.study2 else "raw.githubusercontent.com"
            graph.add((study, SCHEMA.url, Literal(f"https://{host}/Lab/Bench/{path}")))
        # Studies 2 and 3 are now one study, whose own comparisons are split 3 to 4, so nothing
        # is a reversal of the others.
        self.assertEqual(self.reversals(self.derive(graph)[1]), [])
        self.assertEqual(len(self.reversals(self.derive(disagreement())[1])), 1)

    def test_a_paper_and_its_supplement_are_one_study(self) -> None:
        graph = disagreement()
        for study in (ID.study2, ID.study3):
            graph.add((study, RB.doi, Literal("10.1000/Example")))
        self.assertEqual(self.reversals(self.derive(graph)[1]), [])

    def test_reversing_a_near_unanimous_consensus_raises_severity(self) -> None:
        graph = disagreement(outlier_system=ID.configB)
        record(graph, ID.configB, RB.Configuration, configurationOf=ID.modelB)
        self.assertEqual(self.reversals(self.derive(graph)[1])[0]["severity"], "medium")
        for i in range(6, 20):
            scored(graph, f"1-{i}-a", ID.modelA, ID.study1, "0.90", f"subset {i}")
            scored(graph, f"1-{i}-b", ID.modelB, ID.study1, "0.80", f"subset {i}")
        [found] = self.reversals(self.derive(graph)[1])
        self.assertEqual((found["numbers"]["consensus_comparisons"], found["severity"]), (23, "high"))

    def test_a_configuration_of_an_alias_compares_as_the_aliased_model(self) -> None:
        graph = disagreement(outlier_system=ID.configB)
        record(graph, ID.modelBAlias, RB.Model, aliasOf=ID.modelB)
        record(graph, ID.configB, RB.Configuration, configurationOf=ID.modelBAlias)
        [found] = self.reversals(self.derive(graph)[1])
        self.assertEqual(found["systems"], ["modelA", "modelB"])

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

    def review(self, graph: rdflib.Graph, discrepancy: str, state: str, **fields: str) -> None:
        """A discrepancy_review claim: where it stands, and the work behind it."""
        claim = ID[f"review-{state}"]
        record(graph, claim, RB.Claim, subject=ID["result-3-0-a"], source=ID.study3)
        graph.add((claim, RB.claimField, Literal(contradictions.REVIEW_FIELD)))
        graph.add((claim, RB.discrepancyId, Literal(discrepancy)))
        graph.add((claim, RB.value, Literal(state)))
        for name, value in fields.items():
            prop, kind = contradictions.RESOLUTION[name]
            graph.add((claim, prop, URIRef(value) if kind == "iri" else
                       Literal(value, datatype=rdflib.XSD.date) if kind == "date" else Literal(value)))

    def test_resolution_records_the_work_and_what_is_awaited(self) -> None:
        graph = disagreement()
        [found] = self.reversals(self.derive(graph)[1])
        self.assertEqual((found["resolution"], found["settled"]), ({}, False))
        self.review(graph, found["id"], "awaiting-correction",
                    investigation_url="https://github.com/rewire-bio/rewire-benchmark-data/issues/174",
                    report_url="https://github.com/example/repo/issues/2",
                    reported_on="2026-10-19", upstream_response="The author confirmed the bug on 2026-10-20.",
                    awaiting="A corrected preprint and rerun scripts.", expected_by="2026-11-07",
                    next_check="2026-11-10")
        triples, report = self.derive(graph)
        [found] = self.reversals(report)
        self.assertEqual(found["review_state"], "awaiting-correction")
        self.assertFalse(found["settled"])
        self.assertEqual(found["resolution"]["next_check"], "2026-11-10")
        self.assertEqual(found["resolution"]["awaiting"], "A corrected preprint and rerun scripts.")
        node = URIRef(build.ID + found["id"])
        self.assertIn((node, RB.reportedOn, Literal("2026-10-19", datatype=rdflib.XSD.date)), triples)
        self.assertIn((node, RB.reportUrl, URIRef("https://github.com/example/repo/issues/2")), triples)
        self.assertIn((node, RB.assertionMethod, contradictions.MANUAL), triples)
        self.assertEqual(contradictions.check_derived(triples), [])

    def test_terminal_states_settle_a_discrepancy_and_working_states_do_not(self) -> None:
        for state in contradictions.WORKING_STATES + contradictions.TERMINAL_STATES:
            graph = disagreement()
            [found] = self.reversals(self.derive(graph)[1])
            self.review(graph, found["id"], state)
            [found] = self.reversals(self.derive(graph)[1])
            self.assertEqual(found["review_state"], state)
            self.assertEqual(found["settled"], state in contradictions.TERMINAL_STATES, state)

    def test_the_latest_revision_wins(self) -> None:
        graph = disagreement()
        [found] = self.reversals(self.derive(graph)[1])
        self.review(graph, found["id"], "reported-upstream", reported_on="2026-10-19")
        self.review(graph, found["id"], "confirmed-error")
        graph.add((ID["review-confirmed-error"], RB.revision, Literal(2)))
        [found] = self.reversals(self.derive(graph)[1])
        self.assertEqual(found["review_state"], "confirmed-error")

    def test_check_refuses_statements_about_records(self) -> None:
        problems = contradictions.check_derived({(ID.result1, RB.status, V("status", "disputed"))})
        self.assertEqual(len(problems), 2)

    def claim(self, graph: rdflib.Graph, name: str, discrepancy: str, state: str, revision: int | None = None,
              action: str | None = None, date: str | None = None, previous: tuple[str, ...] = (), **fields: str) -> URIRef:
        node = ID[name]
        record(graph, node, RB.Claim, subject=ID["result-3-0-a"], source=ID.study3)
        graph.add((node, RB.claimField, Literal(contradictions.REVIEW_FIELD)))
        graph.add((node, RB.discrepancyId, Literal(discrepancy)))
        graph.add((node, RB.value, Literal(state)))
        if revision is not None:
            graph.add((node, RB.revision, Literal(revision)))
        if action:
            graph.add((node, RB.action, V("discrepancy-action", action)))
        if date:
            graph.add((node, RB.date, Literal(date, datatype=rdflib.XSD.date)))
        for old in previous:
            graph.add((node, RB.previousIds, Literal(old)))
        for name_, value in fields.items():
            prop, kind = contradictions.RESOLUTION[name_]
            graph.add((node, prop, URIRef(value) if kind == "iri" else
                       Literal(value, datatype=rdflib.XSD.date) if kind == "date" else Literal(value)))
        return node

    def test_every_revision_is_kept_as_an_action(self) -> None:
        graph = disagreement()
        [found] = self.reversals(self.derive(graph)[1])
        self.claim(graph, "r2", found["id"], "awaiting-correction", 2, "awaiting-correction", "2026-10-20",
                   next_check="2026-11-10", upstream_response="Accepted.")
        self.claim(graph, "r1", found["id"], "reported-upstream", 1, "reported-upstream", "2026-10-19",
                   report_url="https://github.com/example/repo/issues/2")
        self.claim(graph, "r0", found["id"], "investigating")
        triples, report = self.derive(graph)
        [found] = self.reversals(report)
        self.assertEqual([(a["revision"], a["claim_id"], a["action"], a["state"], a["date"]) for a in found["actions"]],
                         [(0, "r0", None, "investigating", None),
                          (1, "r1", "reported-upstream", "reported-upstream", "2026-10-19"),
                          (2, "r2", "awaiting-correction", "awaiting-correction", "2026-10-20")])
        self.assertEqual(list(found["actions"][0]), list(contradictions.ACTION_FIELDS))
        self.assertEqual((found["review_state"], found["review_claim"]), ("awaiting-correction", "r2"))
        self.assertEqual(found["actions"][2]["next_check"], "2026-11-10")
        node = URIRef(build.ID + found["id"])
        action = URIRef(f"{node}/action/1")
        self.assertIn((node, RB.hasAction, action), triples)
        self.assertIn((action, RB.actionType, V("discrepancy-action", "reported-upstream")), triples)
        self.assertIn((action, RB.actionUrl, URIRef("https://github.com/example/repo/issues/2")), triples)
        self.assertIn((URIRef(f"{node}/action/2"), RB.nextCheck, Literal("2026-11-10", datatype=rdflib.XSD.date)), triples)
        self.assertFalse(any(p == RB.actionType for s, p, _ in triples if s == URIRef(f"{node}/action/0")))
        self.assertEqual(contradictions.check_derived(triples), [])
        conforms, shacl_report = build.validate_derived(triples)
        self.assertTrue(conforms, shacl_report)

    def test_an_action_without_a_date_takes_the_reported_date(self) -> None:
        graph = disagreement()
        [found] = self.reversals(self.derive(graph)[1])
        self.claim(graph, "r1", found["id"], "reported-upstream", 1, "reported-upstream", reported_on="2026-10-19")
        self.claim(graph, "r2", found["id"], "awaiting-correction", 2, "awaiting-correction", "2026-10-21",
                   reported_on="2026-10-19")
        [found] = self.reversals(self.derive(graph)[1])
        self.assertEqual([a["date"] for a in found["actions"]], ["2026-10-19", "2026-10-21"])
        self.assertEqual([a["resolved_by"] for a in found["actions"]], [[], []])

    def test_two_claims_with_one_revision_fail(self) -> None:
        graph = disagreement()
        [found] = self.reversals(self.derive(graph)[1])
        self.claim(graph, "r1", found["id"], "investigating", 1)
        self.claim(graph, "r1b", found["id"], "reported-upstream", 1)
        self.assertEqual(len(self.derived(graph).problems), 1)

    def test_previous_ids_map_claims_forward(self) -> None:
        graph = disagreement()
        [found] = self.reversals(self.derive(graph)[1])
        old = "discrepancy-0000000000000000"
        self.claim(graph, "old", old, "investigating", 1)
        self.claim(graph, "new", found["id"], "reported-upstream", 2, previous=(old,))
        result = self.derived(graph)
        self.assertEqual(result.problems, [])
        [found] = self.reversals(result.report)
        self.assertEqual(found["previous_ids"], [old])
        self.assertEqual([a["claim_id"] for a in found["actions"]], ["old", "new"])
        self.assertIn((URIRef(build.ID + found["id"]), RB.previousIds, Literal(old)), result.triples)

    def test_a_claim_naming_no_derived_discrepancy_fails(self) -> None:
        graph = disagreement()
        self.claim(graph, "lost", "discrepancy-0000000000000000", "awaiting-correction")
        result = self.derived(graph)
        self.assertEqual(len(result.problems), 1)
        self.assertIn("discrepancy-0000000000000000", result.problems[0])
        # Unchecked claims are not accepted, so they cannot fail the build.
        graph.set((ID.lost, RB.status, V("status", "needs_review")))
        self.assertEqual(self.derived(graph).problems, [])

    def test_a_settled_claim_retires_when_its_discrepancy_stops_firing(self) -> None:
        graph = disagreement()
        [found] = self.reversals(self.derive(graph)[1])
        self.claim(graph, "settled", found["id"], "confirmed-error", action="corrected-records")
        for result in [r for r in graph.subjects(RDF.type, RB.Result) if str(r).startswith(str(ID["result-3-"]))]:
            graph.set((result, RB.status, V("status", "disputed")))
        result = self.derived(graph)
        self.assertEqual(self.reversals(result.report), [])
        self.assertEqual((result.problems, result.retired), ([], [found["id"]]))

    def resolved_graph(self) -> tuple[rdflib.Graph, dict]:
        """A reversal reviewed in two steps, settled as a confirmed error, whose outlier results are
        then disputed so that the rule stops firing."""
        graph = disagreement()
        [found] = self.reversals(self.derive(graph)[1])
        self.claim(graph, "r1", found["id"], "reported-upstream", 1, "reported-upstream", "2026-10-19",
                   previous=("discrepancy-00000000000000aa",))
        graph.add((ID.r1, RB.subject, ID["result-3-0-b"]))
        self.claim(graph, "r2", found["id"], "confirmed-error", 2, "corrected-records", "2026-11-12",
                   rationale="The authors corrected an off-by-one error.")
        for result in [r for r in graph.subjects(RDF.type, RB.Result) if str(r).startswith(str(ID["result-3-"]))]:
            graph.set((result, RB.status, V("status", "disputed")))
        return graph, found

    def test_a_settled_finding_that_stops_firing_is_kept_as_resolved(self) -> None:
        graph, found = self.resolved_graph()
        result = self.derived(graph)
        [resolved] = [d for d in result.report if d["resolved"]]
        self.assertEqual(result.report[-1], resolved)
        self.assertEqual(
            {k: resolved[k] for k in ("id", "rule", "label", "summary", "severity", "review_state", "review_claim",
                                      "settled", "systems", "previous_ids", "studies", "numbers", "key")},
            {"id": found["id"], "rule": None, "label": "modelA and modelB: resolved",
             "summary": "The authors corrected an off-by-one error.", "severity": "low", "review_state": "confirmed-error",
             "review_claim": "r2", "settled": True, "systems": ["modelA", "modelB"],
             "previous_ids": ["discrepancy-00000000000000aa"], "studies": [], "numbers": {}, "key": None})
        self.assertEqual([(a["revision"], a["action"], a["state"]) for a in resolved["actions"]],
                         [(1, "reported-upstream", "reported-upstream"), (2, "corrected-records", "confirmed-error")])
        self.assertEqual(resolved["resolution"]["rationale"], "The authors corrected an off-by-one error.")
        self.assertEqual(result.problems, [])
        self.assertTrue(all(not d["resolved"] for d in result.report[:-1]))
        node = URIRef(build.ID + found["id"])
        self.assertIn((node, RDF.type, RB.ResolvedDiscrepancy), result.triples)
        self.assertIn((node, RB.reviewState, V("discrepancy-state", "confirmed-error")), result.triples)
        self.assertEqual(len({o for s, p, o in result.triples if s == node and p == RB.hasAction}), 2)
        self.assertEqual(contradictions.check_derived(result.triples), [])
        conforms, report = build.validate_derived(result.triples)
        self.assertTrue(conforms, report)

    def test_derived_shapes_reject_a_resolved_finding_with_live_links_or_an_open_state(self) -> None:
        graph, found = self.resolved_graph()
        triples = self.derived(graph).triples
        node = URIRef(build.ID + found["id"])
        with_result = triples | {(node, RB.outlierResult, ID["result-3-0-a"])}
        self.assertFalse(build.validate_derived(with_result)[0])
        reopened = {t for t in triples if not (t[0] == node and t[1] == RB.reviewState)} | {
            (node, RB.reviewState, V("discrepancy-state", "investigating"))}
        self.assertFalse(build.validate_derived(reopened)[0])

    def test_named_queries_show_a_resolved_finding_only_where_settled_ones_belong(self) -> None:
        graph, found = self.resolved_graph()
        inferred = build.infer(graph, self.ontology)
        derived = contradictions.derive(graph, inferred, self.ontology, self.rules).triples
        dataset = rdflib.Dataset()
        for triple in derived:
            dataset.graph(URIRef(build.GRAPHS["derived"])).add(triple)
        for triple in graph:
            dataset.graph(URIRef(build.GRAPHS["asserted"])).add(triple)
        dataset.default_union = True
        node = URIRef(build.ID + found["id"])
        queries = {q["name"]: q["sparql"] for q in build.NAMED_QUERIES}
        run = lambda name, **values: list(dataset.query(
            reduce(lambda q, kv: q.replace(f"${kv[0]}", kv[1].n3()), values.items(), queries[name]),
            initNs={"rb": RB, "rdfs": RDFS}))
        self.assertNotIn(node, {row[0] for row in run("open_discrepancies", severity=Literal("low"))})
        self.assertEqual([(int(r[0]), str(r[2]).rsplit("/", 1)[-1]) for r in run("discrepancy_history", discrepancy=node)],
                         [(1, "reported-upstream"), (2, "confirmed-error")])
        self.assertIn(node, {row[0] for row in run("discrepancies_for_system", system=ID.modelA)})

    def test_disputed_results_are_left_out(self) -> None:
        graph = disagreement()
        for result in [r for r in graph.subjects(RDF.type, RB.Result) if str(r).startswith(str(ID["result-3-"]))]:
            graph.set((result, RB.status, V("status", "disputed")))
        result = self.derived(graph)
        self.assertEqual(result.report, [])
        self.assertEqual(result.excluded, {"disputed": 8, "concern": 0})

    def concern(self, graph: rdflib.Graph, source: URIRef, applies_to: list[str] | None = None) -> None:
        entry = {"source_id": str(source).rsplit("/", 1)[-1], "message": "Tables disagree."}
        if applies_to is not None:
            entry["applies_to"] = applies_to
        graph.add((source, RB.evidenceConcerns, Literal(json.dumps([entry]), datatype=RDF.JSON)))

    def test_a_source_wide_concern_leaves_out_its_results(self) -> None:
        graph = disagreement()
        self.concern(graph, ID.study3)
        result = self.derived(graph)
        self.assertEqual(self.reversals(result.report), [])
        self.assertEqual(result.excluded, {"disputed": 0, "concern": 8})

    def test_a_source_wide_concern_covers_results_whose_evaluation_cites_it(self) -> None:
        graph = disagreement()
        concerned = URIRef(ID + "evaluation-paper")
        for evaluation in [e for e in graph.subjects(RDF.type, RB.Evaluation) if str(e).startswith(str(ID["eval-3-"]))]:
            graph.add((evaluation, DCT.source, concerned))
        self.concern(graph, concerned)
        self.assertEqual(self.derived(graph).excluded, {"disputed": 0, "concern": 8})

    def test_a_scoped_concern_leaves_out_only_what_rests_on_its_targets(self) -> None:
        graph = disagreement()
        # A paper cited for context reports a problem in two of study 3's evaluations.
        self.concern(graph, ID.study1, ["eval-3-0-a", "result-3-1-b"])
        result = self.derived(graph)
        self.assertEqual(result.excluded, {"disputed": 0, "concern": 2})
        [found] = self.reversals(result.report)
        self.assertEqual(found["numbers"]["outlier_comparisons"], 2)
        # A named protocol covers every result on it, from any source.
        self.concern(graph, ID.study2, ["protocol"])
        self.assertEqual(self.derived(graph).excluded["concern"], 26)

    def test_derived_shapes_reject_a_malformed_discrepancy(self) -> None:
        triples, report = self.derive(disagreement())
        self.assertTrue(build.validate_derived(triples)[0])
        node = URIRef(build.ID + self.reversals(report)[0]["id"])
        broken = {t for t in triples if not (t[0] == node and t[1] == RB.severity)} | {(node, RB.severity, Literal("urgent"))}
        self.assertFalse(build.validate_derived(broken)[0])
        dangling = triples | {(URIRef(f"{node}/action/1"), RB.actionType, V("discrepancy-action", "closed"))}
        self.assertFalse(build.validate_derived(dangling)[0])

    def test_named_queries_run_over_the_derived_graph(self) -> None:
        graph = disagreement()
        [found] = self.reversals(self.derive(graph)[1])
        self.claim(graph, "r1", found["id"], "reported-upstream", 1, "reported-upstream", "2026-10-19")
        record(graph, ID.useCase, RB.UseCase, assessedBy=ID.protocol)
        inferred = build.infer(graph, self.ontology)
        derived = contradictions.derive(graph, inferred, self.ontology, self.rules).triples
        dataset = rdflib.Dataset()
        for triple in graph:
            dataset.graph(URIRef(build.GRAPHS["asserted"])).add(triple)
        for triple in inferred:
            dataset.graph(URIRef(build.GRAPHS["inferred"])).add(triple)
        for triple in derived:
            dataset.graph(URIRef(build.GRAPHS["derived"])).add(triple)
        dataset.default_union = True
        node = URIRef(build.ID + found["id"])
        given = {"severity": Literal("high"), "system": ID.modelA, "discrepancy": node,
                 "use_case": ID.useCase}
        rows = {}
        for query in build.NAMED_QUERIES:
            names = {p["name"] for p in query["params"]}
            self.assertEqual(names, {n for n in names if f"${n}" in query["sparql"]}, query["name"])
            sparql = query["sparql"]
            for name in names:
                sparql = sparql.replace(f"${name}", given[name].n3())
            rows[query["name"]] = list(dataset.query(sparql, initNs={"rb": RB, "rdfs": RDFS}))
        self.assertIn(node, {row[0] for row in rows["open_discrepancies"]})
        # An optional parameter left unset stays a variable and matches every value.
        [query] = [q for q in build.NAMED_QUERIES if q["name"] == "open_discrepancies"]
        unset = list(dataset.query(query["sparql"].replace("$severity", "?unset"), initNs={"rb": RB, "rdfs": RDFS}))
        self.assertEqual(len(unset), len(contradictions.derive(graph, inferred, self.ontology, self.rules).report))
        for query in build.NAMED_QUERIES:
            select = query["sparql"].split("WHERE", 1)[0]
            self.assertNotIn("$", select, query["name"])
            self.assertNotIn("BOUND(", query["sparql"], query["name"])
        # Both findings, the reversal and the gap outlier, compare model A with model B.
        self.assertEqual({row[0] for row in rows["discrepancies_for_system"]},
                         {URIRef(build.ID + d["id"]) for d in contradictions.derive(graph, inferred, self.ontology, self.rules).report})
        self.assertEqual([(int(r[0]), str(r[1]).rsplit("/", 1)[-1]) for r in rows["discrepancy_history"]],
                         [(1, "reported-upstream")])
        self.assertEqual({str(r[1]) for r in rows["contested_results_for_use_case"]}, {"outlier", "consensus"})

    def test_named_queries_follow_the_bundle_format(self) -> None:
        names = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
        self.assertEqual({q["name"] for q in build.NAMED_QUERIES},
                         {"open_discrepancies", "discrepancies_for_system", "discrepancy_history",
                          "contested_results_for_use_case"})
        for query in build.NAMED_QUERIES:
            self.assertLessEqual(set(query), {"name", "title", "sparql", "description", "params"}, query["name"])
            self.assertRegex(query["name"], names)
            self.assertTrue(query["sparql"].lstrip().startswith("SELECT"), query["name"])
            for param in query.get("params", []):
                self.assertLessEqual(set(param), {"name", "type", "description", "required", "default"})
                self.assertRegex(param["name"], names)
                self.assertIn(param["type"], {"iri", "string", "integer"})
                self.assertIn(f"${param['name']}", query["sparql"])
        self.assertIn("derived", build.GRAPHS)

    def test_derived_terms_are_declared_and_rules_are_concepts(self) -> None:
        vocab = (rdflib.Graph().parse(build.VOCABULARY, format="turtle")
                 .parse(build.ATTRIBUTE_DECLARATIONS, format="turtle"))
        for predicate in contradictions.DERIVED_PREDICATES - {RDF.type, RDFS.label}:
            self.assertIn((predicate, RDFS.label, None), vocab, predicate)
        for scheme, keys in (("discrepancy-rule", {"ordering-reversal", "gap-outlier"}),
                             ("discrepancy-state", contradictions.STATES),
                             ("discrepancy-action", contradictions.ACTIONS)):
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
