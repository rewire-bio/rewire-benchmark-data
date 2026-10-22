"""Find results from one study that disagree with results from other studies.

OWL 2 RL cannot compare numbers, so this runs after inference, over the asserted graph and the
inferred links, and writes its facts to the derived graph. Each fact is an rb:Discrepancy, a
SEPIO assertion (made by an ECO automatic assertion until a reviewer decides) that one study's
results disagree with other studies' results for the same systems. A discrepancy is a lead to
investigate. Nothing here changes a record's status or value.

Rules, with thresholds in data/ontology/discrepancy-rules.json:

  ordering reversal  Other studies rank system A above system B in most of their comparisons;
                     this study ranks B above A in most of its own.
  gap outlier        For systems A and B tested on the same protocol or task by at least three
                     studies, this study's median relative difference between A and B lies
                     outside the range of the others by more than a margin.

A comparison is two systems' best values in one group of results from one study: same protocol,
dataset, metric, unit, qualifier, split and direction. Copied results (an rb:originalEvaluation
link, or origin paper_compilation) are left out, so a compilation never counts as a second
study. Sources that share a result are one study.

Configurations are compared as the model or method they configure (rb:configurationOf, then
rb:family). The vocabulary keeps those links out of inference because results roll up only
when a claim backs the link; here an unbacked link is still used, and the discrepancy says so
with rb:identityBasis "unreviewed", because a lead is worth raising before identity review.
"""

from __future__ import annotations

import hashlib
import json
import statistics
from collections import defaultdict
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from pathlib import Path

import rdflib
from rdflib import RDF, RDFS, XSD, Literal, URIRef

ROOT = Path(__file__).resolve().parents[2]
RULES = ROOT / "data" / "ontology" / "discrepancy-rules.json"

RB = rdflib.Namespace("https://benchmarks.rewire.it/vocab#")
DCT = rdflib.Namespace("http://purl.org/dc/terms/")
MLS_HAS_VALUE = URIRef("http://www.w3.org/ns/mls#hasValue")
ID = "https://benchmarks.rewire.it/id/"
VOCAB = "https://benchmarks.rewire.it/vocab/"
concept = lambda scheme, key: URIRef(f"{VOCAB}{scheme}/{key}")

HIGHER, LOWER, UNKNOWN = (concept("direction", k) for k in ("higher", "lower", "unknown"))
COPIED_ORIGIN = concept("origin", "paper_compilation")
CHECKED = {concept("status", "source_checked"), concept("status", "reproduced")}
AUTOMATIC = URIRef("http://purl.obolibrary.org/obo/ECO_0000203")
MANUAL = URIRef("http://purl.obolibrary.org/obo/ECO_0000218")
REVIEW_FIELD = "discrepancy_review"
STATES = {"open", "explained", "confirmed-error", "false-positive"}
SEVERITY = ["low", "medium", "high"]

# Every predicate the derived graph may use. check_derived refuses anything else.
DERIVED_PREDICATES = {
    RDF.type, RDFS.label, RB.discrepancyRule, RB.assertionMethod, RB.reviewState, RB.reviewClaim,
    RB.comparedSystem, RB.consensusHigher, RB.referenceSystem, RB.outlierSource, RB.consensusSource,
    RB.outlierResult, RB.consensusResult, RB.discrepancyScope, RB.identityBasis, RB.severity,
    RB.outlierComparisons, RB.outlierReversals, RB.consensusComparisons, RB.consensusAgreements,
    RB.outlierGap, RB.consensusGapMin, RB.consensusGapMax, RB.discrepancySummary,
}


def load_rules(path: Path = RULES) -> dict:
    return json.loads(path.read_text("utf-8"))


@dataclass(frozen=True)
class Comparison:
    """Two systems' best values in one group of one study's results."""
    study: URIRef
    protocol: URIRef | None
    a: URIRef
    b: URIRef
    value_a: Decimal
    value_b: Decimal
    higher_is_better: bool
    results_a: tuple[URIRef, ...]
    results_b: tuple[URIRef, ...]
    reviewed: bool

    def better(self, tolerance: float) -> URIRef | None:
        """The better system, or None for a tie within tolerance of the larger magnitude."""
        scale = max(abs(self.value_a), abs(self.value_b))
        if scale == 0 or abs(self.value_a - self.value_b) / scale <= Decimal(str(tolerance)):
            return None
        return self.a if (self.value_a > self.value_b) == self.higher_is_better else self.b

    def relative_gap(self) -> float | None:
        """(A - B) / |B|, signed so that positive means A is better."""
        if self.value_b == 0:
            return None
        gap = float((self.value_a - self.value_b) / abs(self.value_b))
        return gap if self.higher_is_better else -gap


@dataclass
class Finding:
    rule: str
    a: URIRef
    b: URIRef
    outlier: URIRef
    comparisons: list[Comparison]
    consensus: list[Comparison]
    numbers: dict = field(default_factory=dict)
    higher: URIRef | None = None
    reference: URIRef | None = None

    @property
    def iri(self) -> URIRef:
        key = "|".join([self.rule, str(self.a), str(self.b), str(self.outlier)])
        return URIRef(f"{ID}discrepancy-{hashlib.sha256(key.encode()).hexdigest()[:16]}")


class Index:
    """Lookups over the asserted graph and inferred links that the rules need."""

    def __init__(self, asserted: rdflib.Graph, inferred: set[tuple], ontology: rdflib.Graph):
        self.g = asserted
        self.ontology = ontology
        self.within: dict[URIRef, set] = defaultdict(set)
        for s, p, o in inferred:
            if p == RB.within:
                self.within[s].add(o)
        for s, o in asserted.subject_objects(RB.within):
            self.within[s].add(o)
        self.backed = self._backed_links()
        self.study = self._studies()

    def label(self, node: URIRef) -> str:
        return str(self.g.value(node, RDFS.label) or str(node).removeprefix(ID))

    def _backed_links(self) -> set[tuple]:
        """(configuration, field) pairs backed by a checked claim, e.g. links:configuration_of:<id>."""
        backed = set()
        for claim, value in self.g.subject_objects(RB.claimField):
            if str(value).startswith("links:") and self.g.value(claim, RB.status) in CHECKED:
                for subject in self.g.objects(claim, RB.subject):
                    backed.add((subject, str(value)))
        return backed

    def _studies(self) -> dict[URIRef, URIRef]:
        """Sources that appear together on a result are one study, named by its first source."""
        parent: dict[URIRef, URIRef] = {}

        def find(node: URIRef) -> URIRef:
            parent.setdefault(node, node)
            while parent[node] != node:
                parent[node] = parent[parent[node]]
                node = parent[node]
            return node

        for result in self.g.subjects(RDF.type, RB.Result):
            sources = sorted(self.g.objects(result, DCT.source))
            for other in sources[1:]:
                first, second = sorted((find(sources[0]), find(other)))
                parent[second] = first
            for source in sources:
                find(source)
        return {source: find(source) for source in parent}

    def identity(self, system: URIRef) -> tuple[URIRef, bool] | None:
        """The model or method a tested system stands for, and whether that link is reviewed."""
        if system is None:
            return None
        if (system, RDF.type, RB.Configuration) not in self.g:
            target = self.g.value(system, RB.aliasOf)
            return (target or system), True
        options = []
        for relation, name in ((RB.configurationOf, "configuration_of"), (RB.family, "family")):
            for target in sorted(self.g.objects(system, relation)):
                reviewed = (system, f"links:{name}:{str(target).removeprefix(ID)}") in self.backed
                options.append((not reviewed, name != "configuration_of", str(target), target, reviewed))
        if not options:
            return None
        *_, target, reviewed = min(options)
        return target, reviewed

    def anchors(self, protocol: URIRef | None) -> set:
        """The protocol, the tasks it evaluates and everything it sits within."""
        if protocol is None:
            return set()
        found = {protocol, *self.within.get(protocol, ())}
        for task in self.g.objects(protocol, RB.evaluatesTask):
            found |= {task, *self.within.get(task, ())}
        return found

    def direction(self, result: URIRef) -> bool | None:
        direction = self.g.value(result, RB.metricDirection)
        if direction in (None, UNKNOWN):
            metric = self.g.value(result, RB.metric)
            direction = self.ontology.value(metric, RB.defaultDirection) if metric is not None else None
        return True if direction == HIGHER else False if direction == LOWER else None


def comparisons(index: Index) -> list[Comparison]:
    g = index.g
    groups: dict[tuple, dict[URIRef, list]] = defaultdict(lambda: defaultdict(list))
    for result in g.subjects(RDF.type, RB.Result):
        evaluation = g.value(result, RB.evaluation)
        value = g.value(result, MLS_HAS_VALUE)
        sources = sorted(g.objects(result, DCT.source))
        higher = index.direction(result)
        if evaluation is None or value is None or not sources or higher is None:
            continue
        if g.value(evaluation, RB.origin) == COPIED_ORIGIN or (evaluation, RB.originalEvaluation, None) in g:
            continue
        resolved = index.identity(g.value(evaluation, RB.testedSystem))
        if resolved is None:
            continue
        try:
            number = Decimal(str(value))
        except InvalidOperation:
            continue
        protocol = g.value(evaluation, RB.testedOn)
        key = (
            index.study[sources[0]], protocol, g.value(evaluation, RB.dataset), g.value(result, RB.metric),
            g.value(result, RB.unit), str(g.value(result, RB.metricQualifier) or ""),
            str(g.value(result, RB.split) or ""), higher,
        )
        groups[key][resolved[0]].append((number, result, resolved[1]))

    found = []
    for key, by_system in groups.items():
        study, protocol, *_, higher = key
        best = {}
        for system, rows in by_system.items():
            value = (max if higher else min)(number for number, _, _ in rows)
            best[system] = (value, tuple(sorted(r for n, r, _ in rows if n == value)), all(rev for _, _, rev in rows))
        for a in sorted(best):
            for b in sorted(best):
                if a < b:
                    (va, ra, rev_a), (vb, rb_, rev_b) = best[a], best[b]
                    found.append(Comparison(study, protocol, a, b, va, vb, higher, ra, rb_, rev_a and rev_b))
    return found


def ordering_reversals(pairs: dict, rules: dict) -> list[Finding]:
    r = rules["ordering_reversal"]
    tolerance = rules["tie_tolerance"]
    findings = []
    for (a, b), items in pairs.items():
        studies = sorted({c.study for c in items})
        for study in studies:
            mine = [c for c in items if c.study == study and c.better(tolerance)]
            others = [c for c in items if c.study != study and c.better(tolerance)]
            if len(others) < r["min_consensus_comparisons"] or not mine:
                continue
            for_a = sum(1 for c in others if c.better(tolerance) == a)
            higher = a if for_a * 2 >= len(others) else b
            agreements = sum(1 for c in others if c.better(tolerance) == higher)
            if agreements / len(others) < r["consensus_consistency"]:
                continue
            reversals = sum(1 for c in mine if c.better(tolerance) != higher)
            if reversals < r["min_outlier_reversals"] or reversals / len(mine) < r["outlier_consistency"]:
                continue
            findings.append(Finding(
                "ordering-reversal", a, b, study, mine, others, higher=higher,
                numbers={"outlier_comparisons": len(mine), "outlier_reversals": reversals,
                         "consensus_comparisons": len(others), "consensus_agreements": agreements},
            ))
    return findings


def gap_outliers(pairs: dict, index: Index, rules: dict) -> list[Finding]:
    """Per anchor (a protocol, or a task or benchmark it sits within), compare each study's
    median relative gap with the other studies'. Keep the widest miss per pair and study."""
    r = rules["gap_outlier"]
    best: dict[tuple, Finding] = {}
    for (a, b), items in pairs.items():
        by_anchor: dict[URIRef, list[Comparison]] = defaultdict(list)
        for c in items:
            for anchor in index.anchors(c.protocol):
                by_anchor[anchor].append(c)
        for anchor in sorted(by_anchor):
            gaps: dict[URIRef, list[float]] = defaultdict(list)
            for c in by_anchor[anchor]:
                gap = c.relative_gap()
                if gap is not None:
                    gaps[c.study].append(gap)
            if len(gaps) < r["min_studies"]:
                continue
            medians = {study: statistics.median(values) for study, values in gaps.items()}
            for study, median in sorted(medians.items()):
                rest = [m for s, m in medians.items() if s != study]
                low, high = min(rest), max(rest)
                miss = max(low - median, median - high)
                if miss <= r["margin"]:
                    continue
                key = (a, b, study)
                if key in best and best[key].numbers["miss"] >= miss:
                    continue
                anchored = by_anchor[anchor]
                best[key] = Finding(
                    "gap-outlier", a, b, study,
                    [c for c in anchored if c.study == study], [c for c in anchored if c.study != study],
                    reference=b, numbers={"outlier_gap": median, "consensus_gap_min": low,
                                          "consensus_gap_max": high, "miss": miss},
                )
    return [best[k] for k in sorted(best)]


def scope(finding: Finding, index: Index) -> str:
    mine = {c.protocol for c in finding.comparisons}
    theirs = {c.protocol for c in finding.consensus}
    if mine & theirs - {None}:
        return "same-protocol"
    near = set().union(*(index.anchors(p) for p in mine)) & set().union(*(index.anchors(p) for p in theirs))
    return "same-task" if near else "cross-task"


def reviews(index: Index) -> dict[str, tuple[URIRef, str]]:
    """discrepancy id -> (claim, state) from checked discrepancy_review claims. The last claim by
    IRI wins when there are several, so a later decision can be added without editing the first."""
    decided = {}
    claims = (c for c, value in index.g.subject_objects(RB.claimField) if str(value) == REVIEW_FIELD)
    for claim in sorted(claims):
        if index.g.value(claim, RB.status) not in CHECKED:
            continue
        target = index.g.value(claim, RB.discrepancyId)
        state = str(index.g.value(claim, RB.value) or "")
        if target is not None and state in STATES:
            decided[str(target)] = (claim, state)
    return decided


def derive(asserted: rdflib.Graph, inferred: set[tuple], ontology: rdflib.Graph,
           rules: dict | None = None) -> tuple[set[tuple], list[dict]]:
    """The derived graph's statements, and the same discrepancies as JSON-ready dicts."""
    rules = rules or load_rules()
    index = Index(asserted, inferred, ontology)
    pairs: dict[tuple, list[Comparison]] = defaultdict(list)
    for c in comparisons(index):
        pairs[(c.a, c.b)].append(c)
    findings = ordering_reversals(pairs, rules) + gap_outliers(pairs, index, rules)
    decided = reviews(index)

    triples: set[tuple] = set()
    report = []
    for f in findings:
        node = f.iri
        identifier = str(node).removeprefix(ID)
        claim, state = decided.get(identifier, (None, "open"))
        where = scope(f, index)
        reviewed = all(c.reviewed for c in f.comparisons + f.consensus)
        # A gap outlier is the weaker signal, so it is never more than medium.
        severity = SEVERITY[max(0, 2 - (where == "cross-task") - (not reviewed) - (f.rule == "gap-outlier"))]
        outlier_sources = sorted(s for s, study in index.study.items() if study == f.outlier)
        consensus_sources = sorted({s for s, study in index.study.items() if study in {c.study for c in f.consensus}})
        outlier_results = sorted({r for c in f.comparisons for r in c.results_a + c.results_b})
        consensus_results = sorted({r for c in f.consensus for r in c.results_a + c.results_b})
        name_a, name_b, study = index.label(f.a), index.label(f.b), index.label(f.outlier)
        n = f.numbers
        if f.rule == "ordering-reversal":
            top, bottom = (name_a, name_b) if f.higher == f.a else (name_b, name_a)
            kind = RB.OrderingReversal
            label = f"{name_a} and {name_b}: {study} reverses the order"
            summary = (f"{study} ranks {bottom} above {top} in {n['outlier_reversals']} of {n['outlier_comparisons']} "
                       f"comparisons; other studies rank {top} above {bottom} in {n['consensus_agreements']} of "
                       f"{n['consensus_comparisons']}.")
        else:
            kind = RB.GapOutlier
            label = f"{name_a} relative to {name_b}: {study} is outside the range of other studies"
            summary = (f"{study} reports {name_a} at a median relative difference of {n['outlier_gap']:+.2f} from {name_b}; "
                       f"other studies report {n['consensus_gap_min']:+.2f} to {n['consensus_gap_max']:+.2f}.")
        triples |= {
            (node, RDF.type, RB.Discrepancy), (node, RDF.type, kind), (node, RDFS.label, Literal(label)),
            (node, RB.discrepancyRule, concept("discrepancy-rule", f.rule)),
            (node, RB.assertionMethod, MANUAL if claim else AUTOMATIC),
            (node, RB.reviewState, concept("discrepancy-state", state)),
            (node, RB.comparedSystem, f.a), (node, RB.comparedSystem, f.b),
            (node, RB.discrepancyScope, Literal(where)),
            (node, RB.identityBasis, Literal("reviewed" if reviewed else "unreviewed")),
            (node, RB.severity, Literal(severity)),
            (node, RB.discrepancySummary, Literal(summary)),
        }
        if claim is not None:
            triples.add((node, RB.reviewClaim, claim))
        triples |= {(node, RB.outlierSource, s) for s in outlier_sources}
        triples |= {(node, RB.consensusSource, s) for s in consensus_sources}
        triples |= {(node, RB.outlierResult, r) for r in outlier_results}
        triples |= {(node, RB.consensusResult, r) for r in consensus_results}
        if f.rule == "ordering-reversal":
            triples.add((node, RB.consensusHigher, f.higher))
            for key, prop in (("outlier_comparisons", RB.outlierComparisons), ("outlier_reversals", RB.outlierReversals),
                              ("consensus_comparisons", RB.consensusComparisons),
                              ("consensus_agreements", RB.consensusAgreements)):
                triples.add((node, prop, Literal(n[key], datatype=XSD.integer)))
        else:
            triples.add((node, RB.referenceSystem, f.reference))
            for key, prop in (("outlier_gap", RB.outlierGap), ("consensus_gap_min", RB.consensusGapMin),
                              ("consensus_gap_max", RB.consensusGapMax)):
                triples.add((node, prop, Literal(Decimal(f"{n[key]:.4f}"), datatype=XSD.decimal)))
        local = lambda nodes: [str(x).removeprefix(ID) for x in nodes]
        report.append({
            "id": identifier, "rule": f.rule, "label": label, "summary": summary, "severity": severity,
            "scope": where, "identity_basis": "reviewed" if reviewed else "unreviewed", "review_state": state,
            "review_claim": str(claim).removeprefix(ID) if claim else None,
            "systems": local([f.a, f.b]),
            "consensus_higher": str(f.higher).removeprefix(ID) if f.higher else None,
            "reference_system": str(f.reference).removeprefix(ID) if f.reference else None,
            "outlier_sources": local(outlier_sources), "consensus_sources": local(consensus_sources),
            "outlier_results": local(outlier_results), "consensus_results": local(consensus_results),
            "numbers": {k: (round(v, 4) if isinstance(v, float) else v) for k, v in n.items() if k != "miss"},
        })
    report.sort(key=lambda d: (-SEVERITY.index(d["severity"]), d["rule"], d["id"]))
    return triples, report


def check_derived(triples: set[tuple]) -> list[str]:
    """Problems with the derived statements: subjects that are not discrepancies, or predicates
    outside the discrepancy terms (so no record status, value or link can be derived here)."""
    problems = []
    for s, p, _ in sorted(triples):
        if not str(s).startswith(f"{ID}discrepancy-"):
            problems.append(f"derived statement about a record: {s}")
        if p not in DERIVED_PREDICATES:
            problems.append(f"derived statement uses {p}")
    return problems[:20]
