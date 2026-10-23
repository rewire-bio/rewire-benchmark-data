"""Find results from one study that disagree with results from other studies.

OWL 2 RL cannot compare numbers, so this runs after inference, over the asserted graph and the
inferred links, and writes its facts to the derived graph. Each fact is an rb:Discrepancy, a
SEPIO assertion (made by an ECO automatic assertion until a reviewer decides) that one study's
results disagree with other studies' results for the same systems. A discrepancy is a lead to
investigate. Nothing here changes a record's status or value.

Rules, with thresholds in data/ontology/discrepancy-rules.json:

  ordering reversal  Other studies rank system A above system B in most of their comparisons;
                     this study ranks B above A in most of its own.
  gap outlier        In a group of at least three studies of one metric on one protocol or task,
                     with a reference system that every study in the group measured (a named
                     baseline if there is one), this study's median relative difference between a
                     system and the reference lies outside the range of the others by more than a
                     margin. A group without such a reference is skipped.

A comparison is two systems' best values in one group of results from one study: same protocol,
dataset, metric, unit, qualifier, split and direction. Copied results (an rb:originalEvaluation
link, or origin paper_compilation) are left out, so a compilation never counts as a second
study. Sources that share a result are one study, and so are sources with one DOI (a paper and
its supplement) and files from one GitHub repository (the summaries of one benchmark's
leaderboard are not independent of each other).

Configurations are compared as the model or method they configure (rb:configurationOf, then
rb:family). The vocabulary keeps those links out of inference because results roll up only
when a claim backs the link; here an unbacked link is still used, and the discrepancy says so
with rb:identityBasis "unreviewed", because a lead is worth raising before identity review.

Results a reviewer has marked disputed, and results covered by a source's evidence_concerns
entry, are left out, so a confirmed error stops firing once it is recorded.

A discrepancy's ID hashes a canonical key: rule, compared systems (after configuration, family
and alias resolution), anchor, metric and outlier study key. Only the gap rule has an anchor and a
metric; an ordering reversal pools every comparison of its two systems, so both are null. The
study key is the lowest DOI among the study's sources, else the lowest repository URL, else the
source retrieved first (tie-break: ID). None of these change when a source joins the study.
"""

from __future__ import annotations

import hashlib
import json
import re
import statistics
from collections import Counter, defaultdict
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
SCHEMA_URL = URIRef("https://schema.org/url")
# A GitHub repository, whether a file is linked through github.com or raw.githubusercontent.com.
REPOSITORY = re.compile(r"^https?://(?:github\.com|raw\.githubusercontent\.com)/([^/]+)/([^/#?]+)", re.I)
ID = "https://benchmarks.rewire.it/id/"
VOCAB = "https://benchmarks.rewire.it/vocab/"
concept = lambda scheme, key: URIRef(f"{VOCAB}{scheme}/{key}")

HIGHER, LOWER, UNKNOWN = (concept("direction", k) for k in ("higher", "lower", "unknown"))
COPIED_ORIGIN = concept("origin", "paper_compilation")
CHECKED = {concept("status", "source_checked"), concept("status", "reproduced")}
AUTOMATIC = URIRef("http://purl.obolibrary.org/obo/ECO_0000203")
MANUAL = URIRef("http://purl.obolibrary.org/obo/ECO_0000218")
DISPUTED = concept("status", "disputed")
REVIEW_FIELD = "discrepancy_review"
BASELINE_FIELD = "baseline"
# Working states say what has been done; the terminal three settle the discrepancy.
WORKING_STATES = ("investigating", "reported-upstream", "awaiting-correction")
TERMINAL_STATES = ("explained", "confirmed-error", "false-positive")
STATES = {"open", *WORKING_STATES, *TERMINAL_STATES}
# The resolution a review claim carries: our analysis, what we raised upstream, what we await.
# Property names are the ones the attribute registry generates for the same claim attributes.
RESOLUTION = {
    "investigation_url": (RB.investigationUrl, "iri"),
    "report_url": (RB.reportUrl, "iri"),
    "reported_on": (RB.reportedOn, "date"),
    "upstream_response": (RB.upstreamResponse, "text"),
    "awaiting": (RB.awaiting, "text"),
    "expected_by": (RB.expectedBy, "date"),
    "next_check": (RB.nextCheck, "date"),
    "resolved_by": (RB.resolvedBy, "iris"),
    "rationale": (RB.rationale, "text"),
}
SEVERITY = ["low", "medium", "high"]
# The most comparisons listed per study in discrepancies.json; comparisons_total gives the full count.
MAX_STUDY_COMPARISONS = 200
# Follow-up action types (data/vocab/discrepancy-action.ttl).
ACTIONS = ("investigated", "contacted-authors", "reported-upstream", "awaiting-correction", "reran",
           "corrected-records", "closed")
# The fields of one follow-up action in discrepancies.json, in order.
ACTION_FIELDS = ("revision", "claim_id", "action", "state", "date", "rationale", "investigation_url", "report_url",
                 "upstream_response", "awaiting", "expected_by", "next_check", "resolved_by")
# What a result's value rests on, for scoped evidence concerns (shared/omics/concerns.ts).
EVALUATION_PATH = (RB.testedSystem, RB.testedOn, RB.dataset)

# Every predicate the derived graph may use. check_derived refuses anything else.
DERIVED_PREDICATES = {
    RDF.type, RDFS.label, RB.discrepancyRule, RB.assertionMethod, RB.reviewState, RB.reviewClaim,
    RB.comparedSystem, RB.consensusHigher, RB.referenceSystem, RB.outlierSource, RB.consensusSource,
    RB.outlierResult, RB.consensusResult, RB.discrepancyScope, RB.identityBasis, RB.severity,
    RB.outlierComparisons, RB.outlierReversals, RB.consensusComparisons, RB.consensusAgreements,
    RB.outlierGap, RB.consensusGapMin, RB.consensusGapMax, RB.discrepancySummary,
    RB.discrepancyKey, RB.previousIds, RB.hasAction, RB.actionType, RB.actionDate, RB.actionUrl,
    RB.actionRevision, RB.resultingState,
    *(prop for prop, _ in RESOLUTION.values()),
}


def load_rules(path: Path = RULES) -> dict:
    return json.loads(path.read_text("utf-8"))


@dataclass(frozen=True)
class Comparison:
    """Two systems' best values in one group of one study's results."""
    study: URIRef
    protocol: URIRef | None
    metric: URIRef | None
    a: URIRef
    b: URIRef
    value_a: Decimal
    value_b: Decimal
    higher_is_better: bool
    results_a: tuple[URIRef, ...]
    results_b: tuple[URIRef, ...]
    reviewed: bool
    dataset: URIRef | None = None
    unit: URIRef | None = None
    qualifier: str = ""
    split: str = ""

    def better(self, tolerance: float) -> URIRef | None:
        """The better system, or None for a tie within tolerance of the larger magnitude."""
        scale = max(abs(self.value_a), abs(self.value_b))
        if scale == 0 or abs(self.value_a - self.value_b) / scale <= Decimal(str(tolerance)):
            return None
        return self.a if (self.value_a > self.value_b) == self.higher_is_better else self.b

    def relative_gap(self, reference: URIRef) -> float | None:
        """(system - reference) / |reference|, signed so that positive means the other system is
        better than the reference."""
        mine, theirs = (self.value_b, self.value_a) if reference == self.a else (self.value_a, self.value_b)
        if theirs == 0:
            return None
        gap = float((mine - theirs) / abs(theirs))
        return gap if self.higher_is_better else -gap


def local(node: URIRef | None) -> str | None:
    return None if node is None else str(node).removeprefix(ID)


def finding_key(rule: str, systems: list[URIRef], anchor: URIRef | None, metric: URIRef | None,
                outlier_study: str) -> dict:
    """The canonical key a discrepancy's ID hashes. Systems are resolved model or method IRIs;
    the metric is a concept key."""
    return {"rule": rule, "systems": sorted(local(s) for s in systems), "anchor": local(anchor),
            "metric": str(metric).rsplit("/", 1)[-1] if metric is not None else None,
            "outlier_study": outlier_study}


def identifier(key: dict) -> str:
    canonical = json.dumps(key, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return f"discrepancy-{hashlib.sha256(canonical.encode()).hexdigest()[:16]}"


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
    anchor: URIRef | None = None
    metric: URIRef | None = None
    # Every comparison of the two systems the rule looked at, ties included, and (gap rule) each
    # study's median relative gap to the reference. The per-study breakdown is built from these.
    pool: list[Comparison] = field(default_factory=list)
    gaps: dict[URIRef, float] = field(default_factory=dict)


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
        self.study_keys = self._study_keys()
        self.excluded = self._excluded()
        self.baselines = self._baselines()

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
        """Sources that appear together on a result, share a DOI, or are files in one GitHub
        repository are one study, named by its first source."""
        parent: dict[URIRef, URIRef] = {}

        def find(node: URIRef) -> URIRef:
            parent.setdefault(node, node)
            while parent[node] != node:
                parent[node] = parent[parent[node]]
                node = parent[node]
            return node

        def union(a: URIRef, b: URIRef) -> None:
            first, second = sorted((find(a), find(b)))
            parent[second] = first

        for result in self.g.subjects(RDF.type, RB.Result):
            sources = sorted(self.g.objects(result, DCT.source))
            for other in sources[1:]:
                union(sources[0], other)
            for source in sources:
                find(source)
        publications: dict[str, URIRef] = {}
        for source in sorted(parent):
            keys = []
            if (doi := self.g.value(source, RB.doi)) is not None:
                keys.append(f"doi:{str(doi).lower()}")
            if match := REPOSITORY.match(str(self.g.value(source, SCHEMA_URL) or "")):
                keys.append("github:" + "/".join(match.groups()).lower().removesuffix(".git"))
            for key in keys:
                union(publications.setdefault(key, source), source)
        return {source: find(source) for source in parent}

    def _study_keys(self) -> dict[URIRef, str]:
        """study -> its stable key: lowest DOI, else lowest repository URL, else the source
        retrieved first (tie-break: ID)."""
        members: dict[URIRef, list[URIRef]] = defaultdict(list)
        for source, study in self.study.items():
            members[study].append(source)
        keys = {}
        for study, sources in members.items():
            dois = sorted(re.sub(r"^https?://(dx\.)?doi\.org/", "", str(d).strip(), flags=re.I).lower()
                          for s in sources for d in self.g.objects(s, RB.doi))
            repositories = sorted(
                "https://github.com/" + "/".join(match.groups()).lower().removesuffix(".git")
                for s in sources if (match := REPOSITORY.match(str(self.g.value(s, SCHEMA_URL) or ""))))
            if dois:
                keys[study] = f"doi:{dois[0]}"
            elif repositories:
                keys[study] = f"repository:{repositories[0]}"
            else:
                first = min(sources, key=lambda s: (self.g.value(s, RB.retrievedAt) is None,
                                                    str(self.g.value(s, RB.retrievedAt) or ""), str(s)))
                keys[study] = f"source:{local(first)}"
        return keys

    def _excluded(self) -> dict[URIRef, str]:
        """result -> why it is left out: "disputed" (its status), or "concern" (a source's
        evidence_concerns entry covers it; the logic of shared/omics/concerns.ts)."""
        whole_sources, targets = set(), set()
        for source, value in self.g.subject_objects(RB.evidenceConcerns):
            try:
                entries = json.loads(str(value))
            except ValueError:
                continue
            for entry in entries if isinstance(entries, list) else [entries]:
                # A plain-text entry, the form older records use, covers the whole source.
                if isinstance(entry, str) and entry.strip():
                    whole_sources.add(source)
                    continue
                if not isinstance(entry, dict):
                    continue
                scoped = entry.get("applies_to")
                if isinstance(scoped, list) and scoped:
                    targets |= {URIRef(ID + str(target)) for target in scoped}
                else:
                    whole_sources.add(source)
        excluded = {}
        for result in self.g.subjects(RDF.type, RB.Result):
            if self.g.value(result, RB.status) == DISPUTED:
                excluded[result] = "disputed"
                continue
            evaluations = set(self.g.objects(result, RB.evaluation))
            # A source-wide concern covers results that cite the source or whose evaluation does.
            cited = set(self.g.objects(result, DCT.source))
            for evaluation in evaluations:
                cited |= set(self.g.objects(evaluation, DCT.source))
            if whole_sources & cited:
                excluded[result] = "concern"
                continue
            if not targets:
                continue
            path = {result}
            for evaluation in evaluations:
                path.add(evaluation)
                for prop in EVALUATION_PATH:
                    path |= set(self.g.objects(evaluation, prop))
                for assessment in self.g.objects(evaluation, RB.testedOn):
                    path |= set(self.g.objects(assessment, RB.partOf))
            if path & targets:
                excluded[result] = "concern"
        return excluded

    def _baselines(self) -> set[URIRef]:
        """Systems named as a baseline: what a baseline record is implemented by, and the methods a
        use case's baseline claim names (issue #121)."""
        named = set(self.g.objects(None, RB.implementedBy))
        for claim, value in self.g.subject_objects(RB.claimField):
            if str(value) == BASELINE_FIELD:
                named |= set(self.g.objects(claim, RB.methodIds))
        return {resolved[0] for system in named if (resolved := self.identity(system))}

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
        # Configurations of two records for the same model compare as one system.
        return self.g.value(target, RB.aliasOf) or target, reviewed

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
        if result in index.excluded:
            continue
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
        study, protocol, dataset, metric, unit, qualifier, split, higher = key
        best = {}
        for system, rows in by_system.items():
            value = (max if higher else min)(number for number, _, _ in rows)
            best[system] = (value, tuple(sorted(r for n, r, _ in rows if n == value)), all(rev for _, _, rev in rows))
        for a in sorted(best):
            for b in sorted(best):
                if a < b:
                    (va, ra, rev_a), (vb, rb_, rev_b) = best[a], best[b]
                    found.append(Comparison(study, protocol, metric, a, b, va, vb, higher, ra, rb_, rev_a and rev_b,
                                            dataset, unit, qualifier, split))
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
                "ordering-reversal", a, b, study, mine, others, higher=higher, pool=items,
                numbers={"outlier_comparisons": len(mine), "outlier_reversals": reversals,
                         "consensus_comparisons": len(others), "consensus_agreements": agreements},
            ))
    return findings


def anchor_rank(index: Index, anchor: URIRef) -> tuple:
    """Most specific first: a protocol, then a task, then a benchmark or suite; then by IRI."""
    kind = 0 if (anchor, RDF.type, RB.Protocol) in index.g else 1 if (anchor, RDF.type, RB.Task) in index.g else 2
    return kind, str(anchor)


def gap_outliers(found: list[Comparison], index: Index, rules: dict) -> list[Finding]:
    """Per comparison group (a protocol, or a task or benchmark it sits within, and one metric),
    take a reference system every study in the group measured, preferring a named baseline. For
    each other system, compare each study's median relative gap to the reference with the other
    studies'. A pair and study that fire on several anchors keep the most specific one."""
    r = rules["gap_outlier"]
    groups: dict[tuple, list[Comparison]] = defaultdict(list)
    for c in found:
        for anchor in index.anchors(c.protocol):
            groups[(anchor, c.metric)].append(c)
    best: dict[tuple, Finding] = {}
    for (anchor, metric), items in sorted(groups.items(), key=lambda kv: (str(kv[0][0]), str(kv[0][1]))):
        measured: dict[URIRef, set] = defaultdict(set)
        for c in items:
            measured[c.study] |= {c.a, c.b}
        if len(measured) < r["min_studies"]:
            continue
        shared = set.intersection(*measured.values())
        if not shared:
            continue
        reference = min(shared, key=lambda s: (s not in index.baselines, str(s)))
        for system in sorted(shared - {reference}):
            pair = [c for c in items if {c.a, c.b} == {system, reference}]
            gaps: dict[URIRef, list[float]] = defaultdict(list)
            for c in pair:
                gap = c.relative_gap(reference)
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
                key = (system, reference, metric, study)
                if key in best and anchor_rank(index, best[key].anchor) <= anchor_rank(index, anchor):
                    continue
                best[key] = Finding(
                    "gap-outlier", system, reference, study,
                    [c for c in pair if c.study == study], [c for c in pair if c.study != study],
                    reference=reference, anchor=anchor, metric=metric, pool=pair, gaps=medians,
                    numbers={"outlier_gap": median, "consensus_gap_min": low, "consensus_gap_max": high},
                )
    return [best[k] for k in sorted(best, key=lambda k: tuple(str(x) for x in k))]


def scope(finding: Finding, index: Index) -> str:
    mine = {c.protocol for c in finding.comparisons}
    theirs = {c.protocol for c in finding.consensus}
    if mine & theirs - {None}:
        return "same-protocol"
    near = set().union(*(index.anchors(p) for p in mine)) & set().union(*(index.anchors(p) for p in theirs))
    return "same-task" if near else "cross-task"


def concept_key(node: URIRef | None) -> str | None:
    return None if node is None else str(node).rsplit("/", 1)[-1]


def comparison_json(c: Comparison, tolerance: float) -> dict:
    better = c.better(tolerance)
    return {
        "protocol": local(c.protocol), "dataset": local(c.dataset), "metric": concept_key(c.metric),
        "unit": concept_key(c.unit), "qualifier": c.qualifier or None, "split": c.split or None,
        "values": {local(c.a): float(c.value_a), local(c.b): float(c.value_b)},
        # The first of the results that share a system's best value.
        "results": {local(c.a): local(c.results_a[0]), local(c.b): local(c.results_b[0])},
        "higher": local(better),
    }


def studies_json(f: Finding, index: Index, tolerance: float) -> list[dict]:
    """Every study that compared the finding's two systems: the outlier first, then the others by
    number of comparisons (most first) and key. For an ordering reversal this includes a study whose
    comparisons are all ties, which consensus_sources leaves out."""
    by_study: dict[URIRef, list[Comparison]] = defaultdict(list)
    for c in f.pool:
        by_study[c.study].append(c)
    studies = []
    for study, items in by_study.items():
        items.sort(key=lambda c: tuple(str(x or "") for x in (c.protocol, c.dataset, c.metric, c.unit, c.qualifier, c.split)))
        winners = Counter(c.better(tolerance) for c in items)
        gap = f.gaps.get(study)
        studies.append({
            "key": index.study_keys[study],
            "role": "outlier" if study == f.outlier else "consensus",
            "source_ids": sorted(local(s) for s, member in index.study.items() if member == study),
            "higher": {local(f.a): winners[f.a], local(f.b): winners[f.b]},
            "ties": winners[None],
            "gap": round(gap, 4) if gap is not None else None,
            "comparisons_total": len(items),
            "comparisons": [comparison_json(c, tolerance) for c in items[:MAX_STUDY_COMPARISONS]],
        })
    studies.sort(key=lambda s: (s["role"] != "outlier", -s["comparisons_total"], s["key"]))
    return studies


@dataclass
class Reviews:
    """Accepted discrepancy_review claims, as follow-up actions grouped by the discrepancy they
    decide after previous_ids are mapped forward."""
    actions: dict[str, list[dict]]
    previous: dict[str, list[str]]
    problems: list[str]


def reviews(index: Index) -> Reviews:
    """Checked discrepancy_review claims. Each claim is one action; a later step is a new claim
    with a higher revision, so the actions of one discrepancy ordered by revision are its history
    and the last one is where it stands. A claim's previous_ids map those IDs forward to its
    discrepancy_id, for every claim that names them."""
    g = index.g
    claims = []
    for claim, value in g.subject_objects(RB.claimField):
        if str(value) != REVIEW_FIELD or g.value(claim, RB.status) not in CHECKED:
            continue
        target = g.value(claim, RB.discrepancyId)
        state = str(g.value(claim, RB.value) or "")
        if target is None or state not in STATES:
            continue
        action = g.value(claim, RB.action)
        fields = {name: g.value(claim, prop) for name, (prop, _) in RESOLUTION.items()}
        fields["resolved_by"] = sorted(g.objects(claim, RB.resolvedBy))
        claims.append({
            "claim": claim, "target": str(target), "state": state, "revision": int(g.value(claim, RB.revision) or 0),
            "action": str(action).rsplit("/", 1)[-1] if action is not None else None,
            # The action's date: the claim's date attribute, else the day it was reported upstream.
            "date": g.value(claim, RB.date) or fields["reported_on"], "fields": fields,
            "previous_ids": sorted(str(p) for p in g.objects(claim, RB.previousIds)),
        })
    forward: dict[str, str] = {}
    problems = []
    for c in sorted(claims, key=lambda c: str(c["claim"])):
        for old in c["previous_ids"]:
            if forward.setdefault(old, c["target"]) != c["target"]:
                problems.append(f"{local(c['claim'])}: previous ID {old} is mapped to both {forward[old]} and {c['target']}")

    def resolve(identifier: str) -> str:
        seen = {identifier}
        while identifier in forward:
            identifier = forward[identifier]
            if identifier in seen:
                problems.append(f"previous_ids form a cycle through {identifier}")
                break
            seen.add(identifier)
        return identifier

    actions: dict[str, list[dict]] = defaultdict(list)
    for c in claims:
        actions[resolve(c["target"])].append(c)
    previous: dict[str, list[str]] = defaultdict(list)
    for old in sorted(forward):
        previous[resolve(old)].append(old)
    for target, items in actions.items():
        items.sort(key=lambda c: (c["revision"], str(c["claim"])))
        revisions = [c["revision"] for c in items]
        for revision in sorted({n for n in revisions if revisions.count(n) > 1}):
            problems.append(f"{target}: more than one accepted review claim has revision {revision}")
    return Reviews(dict(actions), dict(previous), problems)


def action_json(c: dict) -> dict:
    fields = c["fields"]
    text = lambda name: str(fields[name]) if fields.get(name) is not None else None
    return {
        "revision": c["revision"], "claim_id": local(c["claim"]), "action": c["action"], "state": c["state"],
        "date": str(c["date"]) if c["date"] is not None else None,
        "rationale": text("rationale"), "investigation_url": text("investigation_url"), "report_url": text("report_url"),
        "upstream_response": text("upstream_response"), "awaiting": text("awaiting"),
        "expected_by": text("expected_by"), "next_check": text("next_check"),
        "resolved_by": [local(t) for t in fields["resolved_by"]],
    }


@dataclass
class Derived:
    triples: set[tuple]
    report: list[dict]
    excluded: dict[str, int]
    # Accepted review claims whose discrepancy is no longer derived, directly or through
    # previous_ids. A settled one is retired: a confirmed error stops firing once its results
    # are disputed. Any other fails the build (check_reviews).
    retired: list[str]
    problems: list[str]


def derive(asserted: rdflib.Graph, inferred: set[tuple], ontology: rdflib.Graph,
           rules: dict | None = None) -> Derived:
    """The derived graph's statements, and the same discrepancies as JSON-ready dicts."""
    rules = rules or load_rules()
    index = Index(asserted, inferred, ontology)
    found = comparisons(index)
    pairs: dict[tuple, list[Comparison]] = defaultdict(list)
    for c in found:
        pairs[(c.a, c.b)].append(c)
    findings = ordering_reversals(pairs, rules) + gap_outliers(found, index, rules)
    decided = reviews(index)

    triples: set[tuple] = set()
    report = []
    for f in findings:
        key = finding_key(f.rule, [f.a, f.b], f.anchor, f.metric, index.study_keys[f.outlier])
        identifier_ = identifier(key)
        node = URIRef(ID + identifier_)
        history = decided.actions.get(identifier_, [])
        review = history[-1] if history else None
        claim = review["claim"] if review else None
        state = review["state"] if review else "open"
        where = scope(f, index)
        reviewed = all(c.reviewed for c in f.comparisons + f.consensus)
        # A step down each for different tasks, unreviewed identity and the gap rule; a step up for
        # a reversal of a near-unanimous consensus. A gap outlier is never more than medium.
        strong = rules["strong_consensus"]
        unanimous = (f.rule == "ordering-reversal"
                     and f.numbers["consensus_comparisons"] >= strong["min_comparisons"]
                     and f.numbers["consensus_agreements"] / f.numbers["consensus_comparisons"] >= strong["min_consistency"])
        steps = 2 - (where == "cross-task") - (not reviewed) - (f.rule == "gap-outlier") + unanimous
        severity = SEVERITY[min(max(0, steps), 1 if f.rule == "gap-outlier" else 2)]
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
            summary = (f"On {index.label(f.anchor)}, {study} reports {name_a} at a median relative difference of "
                       f"{n['outlier_gap']:+.2f} from {name_b}; other studies report {n['consensus_gap_min']:+.2f} to "
                       f"{n['consensus_gap_max']:+.2f}.")
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
            (node, RB.discrepancyKey, Literal(json.dumps(key, sort_keys=True, ensure_ascii=False))),
        }
        previous = decided.previous.get(identifier_, [])
        triples |= {(node, RB.previousIds, Literal(old)) for old in previous}
        resolution: dict = {}
        if claim is not None:
            triples.add((node, RB.reviewClaim, claim))
            for name, (prop, kind) in RESOLUTION.items():
                value = review["fields"].get(name)
                if not value:
                    continue
                if kind == "iris":
                    triples |= {(node, prop, target) for target in value}
                    resolution[name] = [local(t) for t in value]
                    continue
                triples.add((node, prop, value if kind == "iri" else
                             Literal(str(value), datatype=XSD.date) if kind == "date" else Literal(str(value))))
                resolution[name] = str(value)
        for c in history:
            action = URIRef(f"{node}/action/{c['revision']}")
            fields = c["fields"]
            url = fields.get("report_url") or fields.get("investigation_url")
            triples |= {
                (node, RB.hasAction, action), (action, RDF.type, RB.FollowUpAction),
                (action, RB.actionRevision, Literal(c["revision"], datatype=XSD.integer)),
                (action, RB.reviewClaim, c["claim"]),
                (action, RB.resultingState, concept("discrepancy-state", c["state"])),
            }
            if c["action"]:
                triples.add((action, RB.actionType, concept("discrepancy-action", c["action"])))
            if c["date"] is not None:
                triples.add((action, RB.actionDate, Literal(str(c["date"]), datatype=XSD.date)))
            if url is not None:
                triples.add((action, RB.actionUrl, url))
            if fields.get("next_check") is not None:
                triples.add((action, RB.nextCheck, Literal(str(fields["next_check"]), datatype=XSD.date)))
        triples |= {(node, RB.outlierSource, s) for s in outlier_sources}
        triples |= {(node, RB.consensusSource, s) for s in consensus_sources}
        triples |= {(node, RB.outlierResult, r) for r in outlier_results}
        triples |= {(node, RB.consensusResult, r) for r in consensus_results}
        if f.rule == "ordering-reversal":
            triples.add((node, RB.consensusHigher, f.higher))
            for name, prop in (("outlier_comparisons", RB.outlierComparisons), ("outlier_reversals", RB.outlierReversals),
                               ("consensus_comparisons", RB.consensusComparisons),
                               ("consensus_agreements", RB.consensusAgreements)):
                triples.add((node, prop, Literal(n[name], datatype=XSD.integer)))
        else:
            triples.add((node, RB.referenceSystem, f.reference))
            for name, prop in (("outlier_gap", RB.outlierGap), ("consensus_gap_min", RB.consensusGapMin),
                               ("consensus_gap_max", RB.consensusGapMax)):
                triples.add((node, prop, Literal(Decimal(f"{n[name]:.4f}"), datatype=XSD.decimal)))
        locals_ = lambda nodes: [local(x) for x in nodes]
        report.append({
            "id": identifier_, "rule": f.rule, "label": label, "summary": summary, "severity": severity,
            "scope": where, "identity_basis": "reviewed" if reviewed else "unreviewed", "review_state": state,
            "review_claim": local(claim) if claim else None,
            "settled": state in TERMINAL_STATES,
            # next_check is a date, not a flag: a consumer decides what is overdue when it reads
            # this, so the same release always produces the same bytes.
            "resolution": resolution,
            "systems": locals_([f.a, f.b]),
            "consensus_higher": local(f.higher) if f.higher else None,
            "reference_system": local(f.reference) if f.reference else None,
            "outlier_sources": locals_(outlier_sources), "consensus_sources": locals_(consensus_sources),
            "outlier_results": locals_(outlier_results), "consensus_results": locals_(consensus_results),
            "numbers": {k: (round(v, 4) if isinstance(v, float) else v) for k, v in n.items()},
            "previous_ids": previous,
            "key": key,
            "studies": studies_json(f, index, rules["tie_tolerance"]),
            "actions": [action_json(c) for c in history],
        })
    report.sort(key=lambda d: (-SEVERITY.index(d["severity"]), d["rule"], d["id"]))
    derived_ids = {d["id"] for d in report}
    retired, problems = [], list(decided.problems)
    for target, history in sorted(decided.actions.items()):
        if target in derived_ids:
            continue
        names = ", ".join(local(c["claim"]) for c in history)
        if history[-1]["state"] in TERMINAL_STATES:
            retired.append(target)
        else:
            problems.append(f"review claim(s) {names} name {target}, which is not derived and is not settled; "
                            "if its ID changed, list the old ID in a claim's previous_ids")
    excluded = Counter(index.excluded.values())
    return Derived(triples, report, {"disputed": excluded["disputed"], "concern": excluded["concern"]}, retired, problems)


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
