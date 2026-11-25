"""The release graph: what a release serves, stated about its records.

The asserted graph holds every public record. Whether a relevance judgement is shown as evidence
is decided when the release is built (shared/omics/use-cases.ts): a judgement is withheld when a
source it rests on is unchecked or carries an evidence concern, when a reviewed evaluation is no
longer eligible, or when pinned evidence changed since review. That decision is not a record
field, so a query over the records alone cannot reproduce it. This module copies it from the
release's use-cases.json into a graph of its own, so that a query and the website read the same
evidence:

  <judgement> rb:servedEvaluation          <evaluation>   an active direct or proxy judgement and each
                                                           evaluation the release serves for it
  <use case>  rb:servedBaseline            <method>       the use case's reviewed baseline methods
  <protocol>  rb:servedNullBaseline        <claim>        the protocol's reviewed null-baseline claim
  <protocol>  rb:servedConventionalBaseline <claim>       the protocol's reviewed conventional-baseline claim
  <protocol>  rb:servedExperimentalCeiling <claim>        the protocol's reviewed experimental-ceiling claim
  <record>    rb:runReceipt                <source>       the source of a run receipt on an executed,
                                                           full-protocol run-recipe instruction of the record

Nothing here is inferred and no record's status, value or links are changed. A bundle built
without a release (release_id "unreleased") has run receipts only.
"""

from __future__ import annotations

import json

import rdflib
from rdflib import RDF, URIRef

RB = rdflib.Namespace("https://benchmarks.rewire.it/vocab#")
ID = "https://benchmarks.rewire.it/id/"
ANCHOR_PREDICATES = {
    "null_baseline": RB.servedNullBaseline,
    "conventional_baseline": RB.servedConventionalBaseline,
    "experimental_ceiling": RB.servedExperimentalCeiling,
}
PREDICATES = {RB.servedEvaluation, RB.servedBaseline, *ANCHOR_PREDICATES.values(), RB.runReceipt}


class ReleaseGraphError(Exception):
    pass


def run_receipts(asserted: rdflib.Graph) -> set[tuple]:
    """Run receipts as the website counts them (rewire-database lib/release-leaderboard.ts): the
    validation receipt of an executed instruction that covers the full protocol, whose source
    record is in the release."""
    triples: set[tuple] = set()
    for record, _, literal in asserted.triples((None, RB.runRecipes, None)):
        for recipe in json.loads(str(literal)):
            for step in recipe.get("instructions", []):
                receipt = step.get("validation_receipt") or {}
                source = URIRef(ID + str(receipt.get("source_id", "")))
                if (step.get("status") == "executed" and receipt.get("scope") == "full_protocol"
                        and (source, RDF.type, RB.Source) in asserted):
                    triples.add((record, RB.runReceipt, source))
    return triples


def served(asserted: rdflib.Graph, artifact: dict, release_id: str) -> set[tuple]:
    """Served evaluations and baselines from the release's use-case artifact. Fails if the
    artifact is for another release or names a record the asserted graph does not have."""
    if artifact.get("release_id") != release_id:
        raise ReleaseGraphError(f"use-cases.json is for release {artifact.get('release_id')}, not {release_id}")
    triples: set[tuple] = set()
    problems: list[str] = []

    def known(node: URIRef, kind: URIRef, what: str) -> bool:
        if (node, RDF.type, kind) in asserted:
            return True
        problems.append(f"{what} {str(node)[len(ID):]} is not in the asserted graph")
        return False

    for mapping in artifact.get("mappings", []):
        if mapping.get("lifecycle") != "active" or mapping.get("relevance") not in ("direct", "proxy"):
            continue
        judgement = URIRef(ID + mapping["id"])
        if not known(judgement, RB.RelevanceJudgement, "judgement"):
            continue
        if (judgement, RB.subject, URIRef(ID + mapping["use_case_id"])) not in asserted:
            problems.append(f"judgement {mapping['id']} is not about use case {mapping['use_case_id']}")
        for evaluation_id in mapping.get("evaluation_ids", []):
            evaluation = URIRef(ID + evaluation_id)
            if known(evaluation, RB.Evaluation, "evaluation"):
                triples.add((judgement, RB.servedEvaluation, evaluation))
        protocol_id = mapping.get("protocol_id")
        for field, predicate in ANCHOR_PREDICATES.items():
            anchor = mapping.get(field)
            if not anchor or not protocol_id:
                continue
            protocol = URIRef(ID + protocol_id)
            claim = URIRef(ID + anchor["claim_id"])
            if not (known(protocol, RB.Protocol, "protocol") and known(claim, RB.Claim, f"{field} claim")):
                continue
            if (claim, RB.subject, protocol) not in asserted:
                problems.append(f"anchor claim {anchor['claim_id']} is not about protocol {protocol_id}")
            for ref_id in [*anchor.get("method_ids", []), *anchor.get("evaluation_ids", []), *anchor.get("result_ids", [])]:
                if (URIRef(ID + ref_id), RDF.type, None) not in asserted:
                    problems.append(f"anchor {anchor['claim_id']} reference {ref_id} is not in the asserted graph")
            triples.add((protocol, predicate, claim))
    for use_case in artifact.get("use_cases", []):
        node = URIRef(ID + use_case["id"])
        method_ids = (use_case.get("baseline") or {}).get("method_ids", [])
        if method_ids and known(node, RB.UseCase, "use case"):
            for method_id in method_ids:
                method = URIRef(ID + method_id)
                if (method, RDF.type, None) in asserted:
                    triples.add((node, RB.servedBaseline, method))
                else:
                    problems.append(f"baseline method {method_id} is not in the asserted graph")
    if problems:
        raise ReleaseGraphError("use-cases.json does not match the asserted graph (run npm run omics:release so that both "
                                "come from the same records):\n  " + "\n  ".join(problems[:20]))
    return triples


def release_triples(asserted: rdflib.Graph, artifact: dict | None, release_id: str) -> tuple[set[tuple], dict]:
    """The release graph and its counts. `artifact` is the release's use-cases.json, or None for a
    bundle built without a release."""
    receipts = run_receipts(asserted)
    use_cases = served(asserted, artifact, release_id) if artifact is not None else set()
    evaluations = {(s, o) for s, p, o in use_cases if p == RB.servedEvaluation}
    anchor_predicates = set(ANCHOR_PREDICATES.values())
    return receipts | use_cases, {
        "use_cases": artifact is not None,
        "served_judgements": len({s for s, _ in evaluations}),
        "served_evaluations": len(evaluations),
        "served_baselines": sum(p == RB.servedBaseline for _, p, _ in use_cases),
        "served_anchors": sum(p in anchor_predicates for _, p, _ in use_cases),
        "run_receipts": len(receipts),
    }
