"""Check batch.jsonl against the repository's own rules without loading the store into Node.

  python3 -I validate_batch.py <repo root> <batch.jsonl>

It reads the kind list, the attribute registry, the relation rules, the SKOS vocabularies and
the description rules straight from the repository, so it fails on the same things
`npm run records -- add` fails on: an undeclared attribute key, a concept key that is not in its
scheme, a link relation that is not allowed between two kinds, a link or concern target that does
not exist, an ID the store already holds, a field carrying both a value and a missing reason, and
a placeholder or provenance description. It is not a substitute for `records -- add`, which also
runs the Zod schema and the SHACL shapes.
"""

import glob
import json
import os
import re
import sys


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def registry(root):
    source = read(os.path.join(root, "shared/omics/attribute-registry.ts"))
    out = {}
    for match in re.finditer(r"\n  ([a-z_]+): \{(.*?)\n  \},", source, re.S):
        kind, body = match.group(1), match.group(2)
        out[kind] = dict(re.findall(r'^\s+([a-z_0-9]+): "([^"]+)"', body, re.M))
    return out


def relation_rules(root):
    source = read(os.path.join(root, "shared/omics/relations.ts"))
    kinds = read(os.path.join(root, "shared/omics/entity-kinds.ts"))

    def names(const):
        match = re.search(const + r"\s*=\s*\[(.*?)\]", kinds, re.S)
        return re.findall(r'"([a-z_]+)"', match.group(1)) if match else []

    groups = {
        "any": names("export const entityKinds"),
        "systems": names("export const modelSubjectKinds"),
        "assessments": names("export const benchmarkSubjectKinds"),
        "data": names("export const datasetSubjectKinds"),
    }
    rules = {}
    for match in re.finditer(r"\n  ([a-z_]+): \{ from: (\[[^\]]*\]|systems[^,]*|assessments|data|any|\[\.\.\.[^\]]*\]), to: ([^,]+), meaning", source):
        name, raw_from, raw_to = match.groups()

        def expand(text):
            text = text.strip()
            out = []
            for token in re.findall(r'"([a-z_]+)"|\b(systems|assessments|data|any)\b', text):
                literal, group = token
                if literal:
                    out.append(literal)
                else:
                    out.extend(groups[group])
            if "filter" in text:
                out = [k for k in out if k != "configuration"]
            return out

        rules[name] = (set(expand(raw_from)), set(expand(raw_to)))
    return rules


def schemes(root):
    out = {}
    for path in glob.glob(os.path.join(root, "data/vocab/*.ttl")):
        name = os.path.basename(path)[:-4]
        out[name] = set(re.findall(r"^:([A-Za-z0-9_-]+) a skos:Concept", read(path), re.M))
    return out


def description_rules(root):
    source = read(os.path.join(root, "shared/omics/descriptions.ts"))
    return [(m.group(1), m.group(2)) for m in re.finditer(r'id: "([^"]+)", kind: "(?:placeholder|provenance)",\s*\n?\s*pattern: /(.+?)/[a-z]*,', source)]


def store_ids(root):
    ids = set()
    for pattern in ("data/entities/*.jsonl", "data/evidence/*/*.jsonl"):
        for path in glob.glob(os.path.join(root, pattern)):
            for line in open(path, encoding="utf-8"):
                if line.strip():
                    ids.add(json.loads(line)["id"])
    return ids


CONCEPT_SCHEME = {
    "concept:metric": "metric", "concept:unit": "unit", "concept:direction": "direction",
    "concept:origin": "origin", "concept:entity-level": "entity-level",
    "concept:configuration-type": "configuration-type", "concept:publication-status": "publication-status",
    "concept:baseline-type": "baseline-type", "concept:relevance": "relevance",
    "concept:algorithm": "algorithm", "concept:discrepancy-action": "discrepancy-action",
    "concept:discrepancy-state": "discrepancy-state", "concept:derivation-method": "derivation-method",
}
FACET_SCHEME = {"areas": "area", "method_types": "method-type", "contexts": "context"}


def main(root, batch_path):
    reg = registry(root)
    rules = relation_rules(root)
    vocab = schemes(root)
    rows = [json.loads(line) for line in open(batch_path, encoding="utf-8") if line.strip()]
    existing = store_ids(root)
    batch_ids = {r["id"]: r["kind"] for r in rows}
    problems = []

    def bad(record_id, message):
        problems.append(f"{record_id}: {message}")

    entity_kinds = set(read(os.path.join(root, "shared/omics/entity-kinds.ts")).split())
    for r in rows:
        rid, kind = r["id"], r["kind"]
        if kind not in reg:
            bad(rid, f"unknown kind {kind}")
            continue
        if rid in existing:
            bad(rid, "the store already holds this ID")
        for field in ("name", "description", "status", "facets", "source_ids", "links", "attributes"):
            if field not in r:
                bad(rid, f"missing top-level field {field}")
        if r.get("status") not in vocab["status"]:
            bad(rid, f"status {r.get('status')} is not in the status scheme")
        for facet, scheme in FACET_SCHEME.items():
            for value in r.get("facets", {}).get(facet, []):
                if value not in vocab[scheme]:
                    bad(rid, f"facet {facet} value {value!r} is not in {scheme}.ttl")
        for source_id in r.get("source_ids", []):
            if source_id not in batch_ids and source_id not in existing:
                bad(rid, f"source_ids names {source_id}, which does not exist")
        for link in r.get("links", []):
            relation, target = link["relation"], link["target_id"]
            if relation not in rules:
                bad(rid, f"unknown relation {relation}")
                continue
            allowed_from, allowed_to = rules[relation]
            if kind not in allowed_from:
                bad(rid, f"relation {relation} is not allowed from a {kind}")
            target_kind = batch_ids.get(target)
            if target is not None and target not in batch_ids and target not in existing:
                bad(rid, f"link {relation} names {target}, which does not exist")
            elif target_kind and target_kind not in allowed_to:
                bad(rid, f"relation {relation} is not allowed to a {target_kind} ({target})")
        attributes = r.get("attributes", {})
        declared = reg[kind]
        for key, value in attributes.items():
            if key not in declared:
                bad(rid, f"attribute {key} is not declared for kind {kind}")
                continue
            kind_of = declared[key]
            if kind_of in CONCEPT_SCHEME:
                scheme = CONCEPT_SCHEME[kind_of]
                if value not in vocab.get(scheme, set()):
                    bad(rid, f"attribute {key} value {value!r} is not in {scheme}.ttl")
            if kind_of == "texts" and not isinstance(value, list):
                bad(rid, f"attribute {key} must be a list of strings")
            if kind_of == "text" and not isinstance(value, str):
                bad(rid, f"attribute {key} must be a string, got {type(value).__name__}")
            if kind_of == "integer" and not isinstance(value, int):
                bad(rid, f"attribute {key} must be an integer")
            if kind_of == "boolean" and not isinstance(value, bool):
                bad(rid, f"attribute {key} must be a boolean")
            if value is None:
                bad(rid, f"attribute {key} is null; a value that is not known is absent, with a missing reason")
        missing = attributes.get("missing_metadata", {})
        for field, entry in missing.items():
            if field not in declared:
                bad(rid, f"missing_metadata names {field}, which kind {kind} cannot hold")
            if field in attributes:
                bad(rid, f"{field} has both a value and a missing reason")
            if entry.get("reason") not in vocab["missingness"]:
                bad(rid, f"missing_metadata {field} reason {entry.get('reason')!r} is not in missingness.ttl")
        review = attributes.get("review")
        if isinstance(review, dict):
            for method in review.get("method", []):
                if method not in vocab["review-method"]:
                    bad(rid, f"review method {method!r} is not in review-method.ttl")
            for reviewer in review.get("reviewer", []):
                if reviewer not in vocab["agent"]:
                    bad(rid, f"review reviewer {reviewer!r} is not in agent.ttl")
        for concern in attributes.get("evidence_concerns", []):
            for target in concern.get("applies_to", []):
                if target not in batch_ids and target not in existing:
                    bad(rid, f"evidence concern applies_to names {target}, which does not exist")
        if kind == "evaluation":
            for relation in ("system", "assessment", "data"):
                n = sum(1 for link in r["links"] if link["relation"] == relation)
                if n != 1:
                    bad(rid, f"an evaluation needs exactly one {relation} link, found {n}")
        if kind == "result":
            n = sum(1 for link in r["links"] if link["relation"] == "evaluation")
            if n != 1:
                bad(rid, f"a result needs exactly one evaluation link, found {n}")
            for field in ("printed_value", "metric", "metric_direction", "unit", "source_locator"):
                if field not in attributes:
                    bad(rid, f"result is missing {field}")

    # Descriptions of described kinds.
    described = {"model", "method", "pipeline", "service", "configuration"}
    distinct = {"model", "method", "pipeline", "service"}
    by_text = {}
    for r in rows:
        if r["kind"] not in described:
            continue
        text = " ".join(r["description"].split())
        for name, pattern in description_rules(root):
            try:
                if re.search(pattern, text, re.I):
                    bad(r["id"], f"description trips rule {name}: {text[:90]}")
            except re.error:
                pass
        if r["kind"] in distinct:
            by_text.setdefault(text.lower(), []).append(r)
    for text, group in by_text.items():
        names = {" ".join(r["name"].split()).lower() for r in group}
        if len(group) > 1 and len(names) > 1:
            bad(group[0]["id"], f"shares its description with {[r['id'] for r in group[1:]]}")

    if problems:
        for message in problems:
            print("FAIL", message)
        raise SystemExit(f"{len(problems)} problem(s)")
    print(f"{len(rows)} records pass the local checks")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
