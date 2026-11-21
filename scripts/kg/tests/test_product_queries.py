"""Tests for the release graph and the ranking, gaps, recipe and provenance queries (#261).

Run with: npm run test:kg
"""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

import rdflib
from rdflib import RDF, RDFS, Literal, URIRef, XSD

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import build  # noqa: E402
import product_queries  # noqa: E402
import release_graph  # noqa: E402

RB = build.RB
ID = rdflib.Namespace(build.ID)
DCT = rdflib.Namespace("http://purl.org/dc/terms/")
MLS = rdflib.Namespace("http://www.w3.org/ns/mls#")
SCHEMA = rdflib.Namespace("https://schema.org/")
V = lambda scheme, key: URIRef(f"https://benchmarks.rewire.it/vocab/{scheme}/{key}")
QUERIES = {q["name"]: q for q in product_queries.QUERIES}
local = lambda term: None if term is None else str(term).rsplit("/", 1)[-1]


def record(graph: rdflib.Graph, name: str, kind: URIRef, status: str = "source_checked", **links) -> URIRef:
    node = ID[name]
    graph.add((node, RDF.type, kind))
    graph.add((node, RDFS.label, Literal(name)))
    graph.add((node, RB.status, V("status", status)))
    for key, targets in links.items():
        for target in targets if isinstance(targets, list) else [targets]:
            graph.add((node, DCT.source if key == "source" else RB[key], target))
    return node


class Fixture:
    """One use case with two served comparisons and one withheld judgement.

    study-a is directly relevant and has two strata (protocols p1 and p2); its ranked column is
    p1 and its metric is AUROC. p3 is a proxy comparison with more configurations, ranked on MSE.
    p5 has a reviewed judgement and a high value, but the release does not serve it."""

    def __init__(self) -> None:
        self.asserted = g = rdflib.Graph()
        self.release = rdflib.Graph()
        self.derived = rdflib.Graph()
        self.inferred = rdflib.Graph()
        record(g, "paper", RB.Source)
        g.add((ID.paper, RB.doi, Literal("10.1/a")))
        g.add((ID.paper, SCHEMA.url, URIRef("https://example.org/paper")))
        g.add((ID.paper, RB.retrievedAt, Literal("2026-10-01", datatype=XSD.date)))
        g.add((ID.paper, RB.artifactSha256, Literal("ab" * 32)))
        record(g, "supplement", RB.Source)
        g.add((ID.supplement, RB.doi, Literal("10.1/A")))
        record(g, "repository", RB.Source, companionOf=ID.paper)
        record(g, "other-paper", RB.Source)
        record(g, "receipt", RB.Source)
        g.add((ID.receipt, SCHEMA.url, URIRef("https://example.org/receipt")))
        for name in ("model-a", "model-b", "model-old"):
            record(g, name, RB.Model)
        record(g, "baseline-method", RB.Method)
        record(g, "use-case", RB.UseCase)
        g.add((ID["use-case"], RB.depthTier, Literal(1)))
        record(g, "bench", RB.Benchmark)
        for protocol in ("p1", "p2", "p3", "p5"):
            record(g, protocol, RB.Protocol)
            g.add((ID["use-case"], RB.assessedBy, ID[protocol]))
            self.inferred.add((ID[protocol], RB.within, ID.bench))
        self.judgement("j1", "p1", "direct", group="study-a", order=1, label="Stratum one", headline="auroc")
        self.judgement("j2", "p2", "direct", group="study-a", order=2, label="Stratum two")
        self.judgement("j3", "p3", "proxy")
        self.judgement("j5", "p5", "direct")

        # study-a, first stratum. Configuration d has two evaluations: the later one counts.
        self.config("a", "model-a")
        self.config("b", "model-b")
        self.config("c")
        self.config("d", "model-old", "model-b")
        self.evaluation("j1", "p1", "e1-a", "a", "independent_paper")
        self.evaluation("j1", "p1", "e1-b", "b", "author_reported", source=ID.receipt)
        self.evaluation("j1", "p1", "e1-c", "c", "rewire_run")
        self.evaluation("j1", "p1", "e1-d-1", "d", "independent_paper")
        self.evaluation("j1", "p1", "e1-d-2", "d", None)
        self.result("r1-a-1", "e1-a", "auroc", "0.90", qualifier="all variants")
        self.result("r1-a-2", "e1-a", "auroc", "0.10", qualifier="subset")  # not the first result
        self.result("r1-a-acc", "e1-a", "accuracy", "0.50")  # another metric
        self.result("r1-b", "e1-b", "auroc", "80", unit="percent")
        self.result("r1-b-old", "e1-b", "auroc", "0.99", status="superseded")
        self.result("r1-c", "e1-c", "auroc", "0.80", source=[ID.repository])
        self.result("r1-d-1", "e1-d-1", "auroc", "0.99")
        self.result("r1-d-2", "e1-d-2", "auroc", "0.70")
        # study-a, second stratum: scores configuration a only.
        self.evaluation("j2", "p2", "e2-a", "a", "independent_paper")
        self.result("r2-a", "e2-a", "auroc", "0.95")
        # p3: five configurations, lower is better, two qualifiers. The column is "a set".
        for i, value in enumerate(["0.30", "0.10", "0.20", "0.10", "0.50"], start=1):
            self.config(f"p3-{i}", "model-a" if i == 1 else None)
            self.evaluation("j3", "p3", f"e3-{i}", f"p3-{i}", "author_reported")
            self.result(f"r3-{i}", f"e3-{i}", "mse", value, qualifier="A set", direction="lower", source=[ID["other-paper"]])
            self.result(f"r3-{i}-b", f"e3-{i}", "mse", "0.01", qualifier="b set", direction="lower", source=[ID["other-paper"]])
        # p5: reviewed and never served.
        self.config("withheld")
        record(g, "e5", RB.Evaluation, testedOn=ID.p5, testedSystem=ID["config-withheld"], origin=V("origin", "independent_paper"))
        self.result("r5", "e5", "auroc", "0.999")

        # One open and one settled finding, a run receipt and a served baseline.
        for finding, state, role, result in (("discrepancy-open", "open", RB.outlierResult, "r1-a-1"),
                                             ("discrepancy-settled", "explained", RB.partyResult, "r1-b")):
            self.derived.add((ID[finding], RDF.type, RB.Discrepancy))
            self.derived.add((ID[finding], RB.reviewState, V("discrepancy-state", state)))
            self.derived.add((ID[finding], role, ID[result]))
        g.add((ID.p1, RB.runRecipes, Literal(json.dumps([{"id": "p1-baseline", "instructions": [
            {"status": "executed", "validation_receipt": {"scope": "full_protocol", "source_id": "receipt"}},
            {"status": "smoke_tested", "validation_receipt": {"scope": "synthetic_smoke", "source_id": "paper"}},
            {"status": "executed", "validation_receipt": {"scope": "full_protocol", "source_id": "not-in-the-release"}},
            {"status": "source_reviewed_not_executed"}]}]), datatype=RDF.JSON)))
        self.release.add((ID.p1, RB.runReceipt, ID.receipt))
        record(g, "correction", RB.Claim, subject=ID["r1-a-1"])
        g.add((ID.correction, RB.claimField, Literal("attributes.printed_value")))
        g.add((ID["r1-a-1"], RB.reviewedBy, V("agent", "claude")))
        g.add((ID["r1-a-1"], RB.reviewDate, Literal("2026-10-02", datatype=XSD.date)))

    def judgement(self, name: str, protocol: str, relevance: str, group: str | None = None, order: int | None = None,
                  label: str | None = None, headline: str | None = None) -> None:
        node = record(self.asserted, name, RB.RelevanceJudgement, subject=ID["use-case"], relevance=V("relevance", relevance))
        self.asserted.add((node, RDF.type, RB.Claim))
        self.asserted.add((node, RB.value, Literal(protocol)))
        for predicate, value in ((RB.comparisonGroup, group), (RB.stratumOrder, order), (RB.stratumLabel, label)):
            if value is not None:
                self.asserted.add((node, predicate, Literal(value)))
        if headline:
            self.asserted.add((node, RB.headlineMetric, V("metric", headline)))

    def config(self, name: str, *parents: str | None) -> None:
        node = record(self.asserted, f"config-{name}", RB.Configuration)
        self.asserted.add((node, RB.reportedName, Literal(f"Tool {name}")))
        for parent in parents:
            if parent:
                self.asserted.add((node, RB.configurationOf, ID[parent]))

    def evaluation(self, judgement: str, protocol: str, name: str, config: str, origin: str | None, source: URIRef | None = None) -> None:
        node = record(self.asserted, name, RB.Evaluation, testedOn=ID[protocol], testedSystem=ID[f"config-{config}"])
        if origin:
            self.asserted.add((node, RB.origin, V("origin", origin)))
        if source:
            self.asserted.add((node, DCT.source, source))
        self.release.add((ID[judgement], RB.servedEvaluation, node))

    def result(self, name: str, evaluation: str, metric: str, value: str, qualifier: str | None = None, unit: str = "fraction",
               direction: str = "higher", status: str = "source_checked", source: list[URIRef] | None = None) -> None:
        node = record(self.asserted, name, RB.Result, status, evaluation=ID[evaluation], source=source or [ID.paper, ID.supplement])
        self.asserted.add((node, RB.metric, V("metric", metric)))
        self.asserted.add((node, RB.unit, V("unit", unit)))
        self.asserted.add((node, RB.metricDirection, V("direction", direction)))
        self.asserted.add((node, MLS.hasValue, Literal(value, datatype=XSD.decimal)))
        self.asserted.add((node, RB.sourceLocator, Literal(f"Table 1, row {name}")))
        if qualifier:
            self.asserted.add((node, RB.metricQualifier, Literal(qualifier)))

    def dataset(self) -> rdflib.Dataset:
        dataset = rdflib.Dataset()
        for role, graph in (("asserted", self.asserted), ("release", self.release), ("derived", self.derived), ("inferred", self.inferred)):
            target = dataset.graph(URIRef(build.GRAPHS[role]))
            for triple in graph:
                target.add(triple)
        dataset.default_union = True
        return dataset

    def run(self, name: str, **values) -> list[dict]:
        sparql = QUERIES[name]["sparql"]
        for key, value in values.items():
            sparql = sparql.replace(f"${key}", value.n3())
        result = self.dataset().query(sparql, initNs={"rb": RB, "rdfs": RDFS})
        return [{str(v): row[v] for v in result.vars} for row in result]

    def rank(self) -> list[dict]:
        return self.run("rank_for_use_case", use_case=ID["use-case"])


def self_rank_rows(use_case: URIRef) -> list[dict]:
    return Fixture().run("rank_for_use_case", use_case=use_case)


class RankForUseCaseTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fixture = Fixture()
        cls.rows = cls.fixture.rank()
        cls.by_config = {local(row["configuration"]): row for row in cls.rows}

    def test_ranks_one_comparison_and_prefers_a_direct_one_to_a_larger_proxy(self) -> None:
        # study-a has four valued configurations and p3 has five, but study-a is directly relevant.
        self.assertEqual([local(r["configuration"]) for r in self.rows], ["config-a", "config-b", "config-c", "config-d"])
        self.assertEqual({str(r["comparison"]) for r in self.rows}, {"study-a"})
        self.assertEqual({local(r["relevance"]) for r in self.rows}, {"direct"})
        self.assertEqual({local(r["metric"]) for r in self.rows}, {"auroc"})
        self.assertEqual({local(r["direction"]) for r in self.rows}, {"higher"})
        # Only the first stratum is ranked: the second protocol's result is not a row.
        self.assertEqual({local(r["protocol"]) for r in self.rows}, {"p1"})
        self.assertNotIn("r2-a", {local(r["result"]) for r in self.rows})

    def test_a_withheld_judgement_contributes_nothing(self) -> None:
        self.assertNotIn("config-withheld", self.by_config)
        self.assertEqual({int(r["relevant"]) for r in self.rows}, {2})

    def test_ties_share_a_rank_and_percent_is_compared_as_a_fraction(self) -> None:
        self.assertEqual([int(r["rank"]) for r in self.rows], [1, 2, 2, 4])
        self.assertEqual(local(self.by_config["config-b"]["unit"]), "percent")

    def test_a_cell_is_the_first_result_of_the_last_evaluation(self) -> None:
        self.assertEqual(local(self.by_config["config-a"]["result"]), "r1-a-1")
        self.assertEqual(local(self.by_config["config-d"]["evaluation"]), "e1-d-2")
        self.assertEqual(local(self.by_config["config-d"]["result"]), "r1-d-2")
        # A superseded result is never ranked.
        self.assertEqual(local(self.by_config["config-b"]["result"]), "r1-b")

    def test_origin_and_independence(self) -> None:
        origins = {name: (local(row["origin"]), row["independent"].toPython()) for name, row in self.by_config.items()}
        self.assertEqual(origins, {"config-a": ("independent_paper", True), "config-b": ("author_reported", False),
                                   "config-c": ("rewire_run", False), "config-d": (None, False)})

    def test_review_status_needs_a_cited_run_receipt(self) -> None:
        self.assertEqual({name: str(row["reviewStatus"]) for name, row in self.by_config.items()},
                         {"config-a": "source_checked", "config-b": "reproduced", "config-c": "source_checked", "config-d": "source_checked"})
        self.assertEqual(local(self.by_config["config-b"]["receipt"]), "receipt")
        self.assertIsNone(self.by_config["config-a"]["receipt"])

    def test_coverage_counts_comparisons_by_tool(self) -> None:
        # model-a has a configuration in both served comparisons; configuration c is its own tool.
        self.assertEqual(local(self.by_config["config-a"]["tool"]), "model-a")
        self.assertEqual(int(self.by_config["config-a"]["evaluated"]), 2)
        self.assertEqual(local(self.by_config["config-c"]["tool"]), "config-c")
        self.assertEqual(int(self.by_config["config-c"]["evaluated"]), 1)
        # Two parent links and no link order in RDF: the IRI that sorts last.
        self.assertEqual(local(self.by_config["config-d"]["tool"]), "model-old")

    def test_only_unsettled_findings_are_open(self) -> None:
        self.assertEqual(str(self.by_config["config-a"]["openFindings"]), str(ID["discrepancy-open"]))
        self.assertEqual(str(self.by_config["config-b"]["openFindings"]), "")

    def test_a_proxy_comparison_is_ranked_when_no_direct_one_qualifies(self) -> None:
        fixture = Fixture()
        for judgement in ("j1", "j2"):
            fixture.release.remove((ID[judgement], RB.servedEvaluation, None))
        rows = fixture.rank()
        self.assertEqual({local(r["relevance"]) for r in rows}, {"proxy"})
        self.assertEqual({str(r["comparison"]) for r in rows}, {"j3"})
        # Lower is better, and the column is the qualifier that sorts first ("A set").
        self.assertEqual([(int(r["rank"]), local(r["result"])) for r in rows],
                         [(1, "r3-2"), (1, "r3-4"), (3, "r3-3"), (4, "r3-1"), (5, "r3-5")])
        self.assertEqual({int(r["relevant"]) for r in rows}, {1})

    def test_a_single_judgement_skips_evaluations_without_the_column_and_strata_do_not(self) -> None:
        # Configuration p3-1 gets a later evaluation that reports only the other qualifier.
        fixture = Fixture()
        for judgement in ("j1", "j2"):
            fixture.release.remove((ID[judgement], RB.servedEvaluation, None))
        fixture.evaluation("j3", "p3", "e3-1-later", "p3-1", "author_reported")
        fixture.result("r3-1-later", "e3-1-later", "mse", "0.02", qualifier="b set", direction="lower")
        self.assertIn("r3-1", {local(r["result"]) for r in fixture.rank()})
        # In a strata comparison the last evaluation counts even without the metric: no value.
        strata = Fixture()
        strata.evaluation("j1", "p1", "e1-a-later", "a", "independent_paper")
        strata.result("r1-a-later", "e1-a-later", "accuracy", "0.5")
        self.assertNotIn("config-a", {local(r["configuration"]) for r in strata.rank()})

    def test_a_served_baseline_breaks_a_tie_between_comparisons(self) -> None:
        fixture = Fixture()
        fixture.asserted.add((ID["use-case"], RB.assessedBy, record(fixture.asserted, "p0", RB.Protocol)))
        fixture.judgement("j0", "p0", "direct", group="study-0", order=1, label="Only stratum", headline="auroc")
        for i in range(4):
            fixture.config(f"p0-{i}", "baseline-method" if i == 0 else None)
            fixture.evaluation("j0", "p0", f"e0-{i}", f"p0-{i}", "independent_paper")
            fixture.result(f"r0-{i}", f"e0-{i}", "auroc", f"0.{i + 1}")
        # Same relevance and number of configurations: the comparison ID decides.
        self.assertEqual({str(r["comparison"]) for r in fixture.rank()}, {"study-0"})
        fixture.asserted.remove((ID["config-p0-0"], RB.configurationOf, None))
        fixture.release.add((ID["use-case"], RB.servedBaseline, ID["model-b"]))
        self.assertEqual({str(r["comparison"]) for r in fixture.rank()}, {"study-a"})

    def test_nothing_is_ranked_without_two_values_or_a_direction(self) -> None:
        fixture = Fixture()
        fixture.release.remove((None, RB.servedEvaluation, None))
        self.assertEqual(fixture.rank(), [])
        fixture.evaluation("j1", "p1", "e1-a", "a", "independent_paper")
        self.assertEqual(fixture.rank(), [])
        fixture = Fixture()
        fixture.release.remove((ID.j3, RB.servedEvaluation, None))
        fixture.asserted.remove((None, RB.metricDirection, None))
        self.assertEqual(fixture.rank(), [])


class GapsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fixture = Fixture()
        cls.rows = cls.fixture.run("gaps", use_case=ID["use-case"], tier=Literal(1))

    def gaps(self, rows: list[dict]) -> set[tuple]:
        return {(str(r["level"]), local(r["protocol"]), str(r["gap"])) for r in rows}

    def test_protocol_gaps(self) -> None:
        found = self.gaps(self.rows)
        # The paper and its supplement share a DOI, and the repository is the paper's companion: one study.
        self.assertIn(("protocol", "p1", "single_source"), found)
        self.assertNotIn(("protocol", "p1", "no_independent_result"), found)
        self.assertIn(("protocol", "p3", "no_independent_result"), found)
        self.assertIn(("protocol", "p3", "single_source"), found)
        # The withheld judgement leaves its protocol without served evidence, and nothing else is said of it.
        self.assertEqual({gap for level, protocol, gap in found if protocol == "p5"}, {"no_served_evidence"})

    def test_use_case_gaps(self) -> None:
        # Two studies, one directly relevant judgement and one independent evaluation: no gap.
        self.assertEqual({gap for level, _, gap in self.gaps(self.rows) if level == "use_case"}, set())
        [row] = [r for r in self.rows if local(r["protocol"]) == "p1"]
        self.assertEqual((int(row["evaluations"]), int(row["studies"])), (5, 1))
        fixture = Fixture()
        for judgement in ("j1", "j2"):
            fixture.release.remove((ID[judgement], RB.servedEvaluation, None))
        found = self.gaps(fixture.run("gaps", use_case=ID["use-case"], tier=Literal(1)))
        self.assertEqual({gap for level, _, gap in found if level == "use_case"},
                         {"no_direct_evidence", "single_source", "no_independent_result"})
        fixture.release.remove((None, RB.servedEvaluation, None))
        found = self.gaps(fixture.run("gaps", use_case=ID["use-case"], tier=Literal(1)))
        self.assertEqual({gap for level, _, gap in found if level == "use_case"}, {"no_direct_evidence"})

    def test_optional_parameters(self) -> None:
        # Unset parameters stay variables and match everything; another tier matches nothing.
        self.assertEqual(self.gaps(self.fixture.run("gaps")), self.gaps(self.rows))
        self.assertEqual(self.fixture.run("gaps", tier=Literal(2)), [])
        self.assertEqual(self.fixture.run("gaps", use_case=ID["bench"]), [])

    def test_a_use_case_without_a_tier_matches_no_tier(self) -> None:
        fixture = Fixture()
        fixture.asserted.remove((ID["use-case"], RB.depthTier, None))
        self.assertEqual(self.gaps(fixture.run("gaps")), self.gaps(self.rows))
        self.assertEqual(self.gaps(fixture.run("gaps", use_case=ID["use-case"])), self.gaps(self.rows))
        for tier in (1, 2, 3):
            self.assertEqual(fixture.run("gaps", tier=Literal(tier)), [], tier)

    def test_level_keeps_one_level_and_use_case_rows_come_first(self) -> None:
        fixture = Fixture()
        for judgement in ("j1", "j2"):
            fixture.release.remove((ID[judgement], RB.servedEvaluation, None))
        rows = fixture.run("gaps")
        levels = [str(r["level"]) for r in rows]
        self.assertEqual(levels, sorted(levels, reverse=True))
        self.assertEqual(levels[0], "use_case")
        self.assertIn("protocol", levels)
        for level in ("use_case", "protocol"):
            kept = fixture.run("gaps", level=Literal(level))
            self.assertEqual(self.gaps(kept), {row for row in self.gaps(rows) if row[0] == level}, level)
            self.assertEqual(len(kept), levels.count(level), level)
        self.assertEqual(fixture.run("gaps", level=Literal("use case")), [])
        [level] = [p for p in QUERIES["gaps"]["params"] if p["name"] == "level"]
        self.assertEqual((level["type"], level["required"]), ("string", False))


class RecipeAndProvenanceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fixture = Fixture()

    def test_recipe_for_a_record_and_for_what_contains_it(self) -> None:
        for subject in (ID.p1, ID.bench):
            [row] = self.fixture.run("recipe_for", subject=subject)
            self.assertEqual(local(row["record"]), "p1")
            self.assertEqual(json.loads(str(row["storeRecipes"]))[0]["id"], "p1-baseline")
            self.assertEqual(local(row["fullProtocolReceipt"]), "receipt")
            self.assertEqual(str(row["receiptUrl"]), "https://example.org/receipt")
        self.assertEqual(self.fixture.run("recipe_for", subject=ID.p2), [])
        self.assertEqual(self.fixture.run("recipe_for", subject=ID["model-a"]), [])

    def test_a_record_with_recipes_and_no_receipt_is_still_listed(self) -> None:
        fixture = Fixture()
        fixture.release.remove((None, RB.runReceipt, None))
        [row] = fixture.run("recipe_for", subject=ID.p1)
        self.assertIsNone(row["fullProtocolReceipt"])

    def test_provenance_lists_sources_reviews_and_claims(self) -> None:
        rows = self.fixture.run("provenance", result=ID["r1-a-1"])
        self.assertEqual([(str(r["step"]), local(r["record"])) for r in rows],
                         [("source", "paper"), ("source", "supplement"), ("review", "e1-a"), ("review", "r1-a-1"), ("claim", "correction")])
        source = rows[0]
        self.assertEqual(str(source["locator"]), "Table 1, row r1-a-1")
        self.assertEqual((str(source["url"]), str(source["doi"]), str(source["retrieved"]), str(source["sha256"])),
                         ("https://example.org/paper", "10.1/a", "2026-10-01", "ab" * 32))
        review = rows[3]
        self.assertEqual((local(review["status"]), local(URIRef(str(review["reviewedBy"]))), str(review["date"])),
                         ("source_checked", "claude", "2026-10-02"))
        self.assertEqual(str(rows[4]["field"]), "attributes.printed_value")

    def test_provenance_is_empty_for_a_record_that_is_not_a_result(self) -> None:
        # A use case has claims about it, an evaluation has a review and a source, a source has a review.
        for name in ("use-case", "e1-b", "config-a", "paper", "j1", "no-such-record"):
            self.assertEqual(self.fixture.run("provenance", result=ID[name]), [], name)


class ReleaseGraphTest(unittest.TestCase):
    def artifact(self, **changes) -> dict:
        return {
            "release_id": "2026-01-01-000000000000",
            "use_cases": [{"id": "use-case", "baseline": {"method_ids": ["baseline-method"]}}, {"id": "other-use-case"}],
            "mappings": [
                {"id": "j1", "use_case_id": "use-case", "lifecycle": "active", "relevance": "direct", "evaluation_ids": ["e1-a", "e1-b"]},
                {"id": "j3", "use_case_id": "use-case", "lifecycle": "needs_review", "relevance": "proxy", "evaluation_ids": []},
                {"id": "j5", "use_case_id": "use-case", "lifecycle": "draft", "relevance": "direct", "evaluation_ids": ["e5"]},
                {"id": "j2", "use_case_id": "use-case", "lifecycle": "active", "relevance": "outside_scope", "evaluation_ids": ["e2-a"]},
            ],
            **changes,
        }

    def test_only_active_direct_or_proxy_judgements_are_served(self) -> None:
        asserted = Fixture().asserted
        triples, counts = release_graph.release_triples(asserted, self.artifact(), "2026-01-01-000000000000")
        self.assertEqual(triples, {
            (ID.j1, RB.servedEvaluation, ID["e1-a"]), (ID.j1, RB.servedEvaluation, ID["e1-b"]),
            (ID["use-case"], RB.servedBaseline, ID["baseline-method"]),
            # Executed and full protocol, with its source in the release: the smoke receipt and
            # the receipt whose source is missing are left out.
            (ID.p1, RB.runReceipt, ID.receipt),
        })
        self.assertEqual(counts, {"use_cases": True, "served_judgements": 1, "served_evaluations": 2,
                                  "served_baselines": 1, "run_receipts": 1})
        self.assertLessEqual({p for _, p, _ in triples}, release_graph.PREDICATES)

    def test_a_bundle_without_a_release_has_run_receipts_only(self) -> None:
        triples, counts = release_graph.release_triples(Fixture().asserted, None, "unreleased")
        self.assertEqual(triples, {(ID.p1, RB.runReceipt, ID.receipt)})
        self.assertFalse(counts["use_cases"])

    def test_the_build_fails_when_the_artifact_and_the_graph_disagree(self) -> None:
        asserted = Fixture().asserted
        with self.assertRaisesRegex(release_graph.ReleaseGraphError, "is for release"):
            release_graph.release_triples(asserted, self.artifact(), "2026-01-02-000000000000")
        for mapping, message in (
            ({"id": "j1", "evaluation_ids": ["no-such-evaluation"]}, "evaluation no-such-evaluation is not in the asserted graph"),
            ({"id": "no-such-judgement", "evaluation_ids": ["e1-a"]}, "judgement no-such-judgement is not in the asserted graph"),
            ({"id": "j1", "use_case_id": "other-use-case", "evaluation_ids": ["e1-a"]}, "is not about use case other-use-case"),
        ):
            broken = self.artifact(mappings=[{"use_case_id": "use-case", "lifecycle": "active", "relevance": "direct", **mapping}])
            with self.assertRaisesRegex(release_graph.ReleaseGraphError, message):
                release_graph.release_triples(asserted, broken, "2026-01-01-000000000000")
        broken = self.artifact(use_cases=[{"id": "use-case", "baseline": {"method_ids": ["no-such-method"]}}])
        with self.assertRaisesRegex(release_graph.ReleaseGraphError, "baseline method no-such-method"):
            release_graph.release_triples(asserted, broken, "2026-01-01-000000000000")

    def test_a_release_needs_its_use_case_file(self) -> None:
        self.assertIsNone(build.load_use_cases("unreleased", None))
        with self.assertRaisesRegex(build.BuildError, "use-cases.json not found; run npm run omics:release first") as raised:
            build.load_use_cases("1999-01-01-000000000000", None)
        # release:fetch writes data/omics/releases/<id>/use-cases.json.gz, which the build does not read.
        self.assertNotIn("release:fetch", str(raised.exception))

    def test_release_terms_are_declared_and_stay_out_of_the_reasoner(self) -> None:
        vocab = rdflib.Graph().parse(build.VOCABULARY, format="turtle")
        for predicate in release_graph.PREDICATES:
            self.assertIn((predicate, RDFS.label, None), vocab, predicate)
            self.assertEqual(list(vocab.subjects(RDFS.subPropertyOf, predicate)), [], predicate)
            self.assertEqual(list(vocab.objects(predicate, RDFS.subPropertyOf)), [], predicate)
            self.assertNotIn(predicate, build.axiom_properties(vocab))
        self.assertIn("release", build.GRAPHS)

    def test_the_fixture_release_graph_is_what_the_module_writes(self) -> None:
        # The query tests rest on a hand-built release graph; its receipt is what run_receipts finds.
        fixture = Fixture()
        self.assertEqual(release_graph.run_receipts(fixture.asserted), set(fixture.release.triples((None, RB.runReceipt, None))))


class QueryFormatTest(unittest.TestCase):
    def test_no_composite_score_and_no_parameter_in_a_select_list(self) -> None:
        self.assertEqual(list(QUERIES), ["rank_for_use_case", "gaps", "recipe_for", "provenance"])
        for query in product_queries.QUERIES:
            self.assertIn(query, build.NAMED_QUERIES)
        columns = QUERIES["rank_for_use_case"]["sparql"].split("WHERE", 1)[0]
        self.assertNotIn("score", columns.lower())

    def test_use_case_parameters_say_to_look_the_record_up_by_slug(self) -> None:
        # A record ID is not always use-case-<slug>, and a wrong IRI returns no rows without an error.
        for name in ("rank_for_use_case", "gaps"):
            [param] = [p for p in QUERIES[name]["params"] if p["name"] == "use_case"]
            self.assertIn("rb:slug", param["description"], name)
        self.assertIn("rb:slug", QUERIES["rank_for_use_case"]["description"])
        self.assertEqual(self_rank_rows(ID["no-such-use-case"]), [])
        self.assertEqual(self_rank_rows(ID["bench"]), [])


if __name__ == "__main__":
    unittest.main()
