"""Check batch.jsonl against the repository's own schema sources before review.

Reads the declared attribute keys from shared/omics/attribute-registry.ts, the link rules from
shared/omics/relations.ts, the record kinds from shared/omics/entity-kinds.ts and the concept
keys from data/vocab/*.ttl, then checks every record in the batch. Reports problems and exits
non-zero if any are found. This is an extractor self-check, not a review.

Run from the repository root:
    python3 -I data/omics/bioemu2-20261115/extract/check_batch.py
"""

import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[4]
BATCH = pathlib.Path(__file__).resolve().parent.parent
BATCH_FILE = BATCH / "batch.jsonl"

REVIEW_KEYS = {
    "method", "reviewer", "date", "reviewed_at", "scope", "note", "method_note",
    "reviewer_note", "evidence", "source_id", "receipt", "artifact_sha256", "retrieval_url",
}
BANNED_CHARS = {"\u2014": "em dash", "\u2013": "en dash", "\u00b5": "micro sign", "\u00d7": "multiplication sign"}


def registry() -> dict[str, dict[str, str]]:
    text = (ROOT / "shared" / "omics" / "attribute-registry.ts").read_text(encoding="utf-8")
    out: dict[str, dict[str, str]] = {}
    for match in re.finditer(r"^  ([a-z_]+): \{$(.*?)^  \},$", text, re.S | re.M):
        kind, body = match.group(1), match.group(2)
        out[kind] = dict(re.findall(r'^\s{4}([a-z_0-9]+): "([a-z0-9:\-]+)"', body, re.M))
    return out


def concepts(scheme: str) -> set[str]:
    text = (ROOT / "data" / "vocab" / f"{scheme}.ttl").read_text(encoding="utf-8")
    return set(re.findall(r"^:([A-Za-z0-9_-]+)", text, re.M))


def relation_rules() -> dict[str, tuple[set[str], set[str]]]:
    text = (ROOT / "shared" / "omics" / "relations.ts").read_text(encoding="utf-8")
    kinds_text = (ROOT / "shared" / "omics" / "entity-kinds.ts").read_text(encoding="utf-8")

    def group(name: str) -> set[str]:
        block = re.search(rf"export const {name} = \[(.*?)\] as const;", kinds_text, re.S)
        return set(re.findall(r'"([a-z_]+)"', block.group(1)))

    groups = {
        "systems": group("modelSubjectKinds"),
        "assessments": group("benchmarkSubjectKinds"),
        "data": group("datasetSubjectKinds"),
        "any": group("entityKinds"),
    }

    def resolve(expression: str) -> set[str]:
        expression = expression.strip()
        if expression in groups:
            return groups[expression]
        if expression.startswith("["):
            out: set[str] = set()
            for part in re.findall(r'\.\.\.([a-z]+)|"([a-z_]+)"', expression):
                spread, literal = part
                if spread:
                    out |= groups.get(spread, set())
                if literal:
                    out.add(literal)
            return out
        if expression.startswith("systems.filter"):
            return groups["systems"] - {"configuration"}
        raise AssertionError(f"unparsed kind expression {expression!r}")

    rules: dict[str, tuple[set[str], set[str]]] = {}
    for match in re.finditer(
        r"^  ([a-z_]+): \{ from: (.+?), to: (.+?), meaning:", text, re.M
    ):
        rules[match.group(1)] = (resolve(match.group(2)), resolve(match.group(3)))
    return rules


def store_ids() -> set[str]:
    ids: set[str] = set()
    for path in list((ROOT / "data" / "entities").glob("*.jsonl")) + list(
        (ROOT / "data" / "evidence").glob("*/*.jsonl")
    ):
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                ids.add(json.loads(line)["id"])
    return ids


def walk_strings(value, path="") :
    if isinstance(value, str):
        yield path, value
    elif isinstance(value, dict):
        for key, item in value.items():
            yield from walk_strings(item, f"{path}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from walk_strings(item, f"{path}[{index}]")


def type_ok(declared: str, value) -> bool:
    if declared in {"text", "url", "git-sha", "doi", "date", "datetime"} or declared.startswith("concept:"):
        return isinstance(value, str)
    if declared == "texts":
        return isinstance(value, list) and all(isinstance(item, str) for item in value)
    if declared in {"json", "review", "missing-metadata"}:
        return isinstance(value, dict)
    if declared == "boolean":
        return isinstance(value, bool)
    if declared == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if declared in {"record-ids", "entity-kinds"}:
        return isinstance(value, list)
    if declared == "record-id":
        return isinstance(value, str)
    return True


def main() -> int:
    reg = registry()
    rules = relation_rules()
    vocab = {
        "status": concepts("status"),
        "area": concepts("area"),
        "method-type": concepts("method-type"),
        "context": concepts("context"),
        "missingness": concepts("missingness"),
        "review-method": concepts("review-method"),
        "agent": concepts("agent"),
        "publication-status": concepts("publication-status"),
        "entity-level": concepts("entity-level"),
        "configuration-type": concepts("configuration-type"),
    }
    records = [json.loads(line) for line in BATCH_FILE.read_text(encoding="utf-8").splitlines() if line.strip()]
    batch_ids = {record["id"] for record in records}
    known = batch_ids | store_ids()
    kinds = {record["id"]: record["kind"] for record in records}
    problems: list[str] = []

    def bad(record_id: str, message: str) -> None:
        problems.append(f"{record_id}: {message}")

    if len(batch_ids) != len(records):
        problems.append("duplicate record IDs in the batch")
    if [r["id"] for r in records] != sorted(r["id"] for r in records):
        problems.append("records are not sorted by ID")

    descriptions: dict[str, list[str]] = {}
    for record in records:
        rid = record["id"]
        if not re.fullmatch(r"[a-z0-9][a-z0-9:._-]*", rid):
            bad(rid, "ID is not a lowercase slug")
        if record["kind"] not in reg:
            bad(rid, f"unknown kind {record['kind']}")
            continue
        if record["status"] not in vocab["status"]:
            bad(rid, f"status {record['status']} is not in status.ttl")
        if not record.get("name") or not record.get("description"):
            bad(rid, "missing name or description")
        for facet, scheme in (("areas", "area"), ("method_types", "method-type"), ("contexts", "context")):
            for key in record.get("facets", {}).get(facet, []):
                if key not in vocab[scheme]:
                    bad(rid, f"facet {facet} value {key} is not in {scheme}.ttl")
        if record["kind"] in {"model", "method", "pipeline", "service", "configuration"}:
            descriptions.setdefault(record["description"].strip().lower(), []).append(rid)
            text = record["description"]
            if re.search(r"\b(as run|as reported|quoted in|source-reported)\b", text, re.I):
                bad(rid, "description carries provenance wording")
            if re.search(r"\([^()]*\b(Table|Figure|Section|Appendix)\b[^()]*\)", text):
                bad(rid, "description carries a source locator in parentheses")

        for link in record.get("links", []):
            relation, target = link["relation"], link["target_id"]
            if relation not in rules:
                bad(rid, f"unknown relation {relation}")
                continue
            allowed_from, allowed_to = rules[relation]
            if record["kind"] not in allowed_from:
                bad(rid, f"relation {relation} is not allowed from kind {record['kind']}")
            if target not in known:
                bad(rid, f"link target {target} does not exist")
            elif target in kinds and kinds[target] not in allowed_to:
                bad(rid, f"relation {relation} is not allowed to kind {kinds[target]}")
        for source_id in record.get("source_ids", []):
            if source_id not in known:
                bad(rid, f"source_ids entry {source_id} does not exist")

        declared = reg[record["kind"]]
        attributes = record.get("attributes", {})
        for key, value in attributes.items():
            if key not in declared:
                bad(rid, f"attribute {key} is not declared for {record['kind']}")
                continue
            if value is None:
                bad(rid, f"attribute {key} is null; a value that is not known is absent")
            elif not type_ok(declared[key], value):
                bad(rid, f"attribute {key} should be {declared[key]}")
        for key, entry in attributes.get("missing_metadata", {}).items():
            if key not in declared:
                bad(rid, f"missing_metadata names {key}, which is not declared for {record['kind']}")
            if key in attributes:
                bad(rid, f"{key} has both a value and a missing reason")
            if entry.get("reason") not in vocab["missingness"]:
                bad(rid, f"missing_metadata {key} reason {entry.get('reason')} is not in missingness.ttl")
            if set(entry) - {"reason", "note"}:
                bad(rid, f"missing_metadata {key} has unexpected keys {sorted(set(entry) - {'reason', 'note'})}")
        review = attributes.get("review")
        if review is not None:
            if set(review) - REVIEW_KEYS:
                bad(rid, f"review has unexpected keys {sorted(set(review) - REVIEW_KEYS)}")
            for method in review.get("method", []):
                if method not in vocab["review-method"]:
                    bad(rid, f"review method {method} is not in review-method.ttl")
            for reviewer in review.get("reviewer", []):
                if reviewer not in vocab["agent"]:
                    bad(rid, f"review reviewer {reviewer} is not in agent.ttl")
            if "artifact_sha256" in review and not re.fullmatch(r"[a-f0-9]{64}", review["artifact_sha256"]):
                bad(rid, "review artifact_sha256 is not a 64 character hex digest")
        if record["kind"] == "source":
            status = attributes.get("publication_status")
            if status not in vocab["publication-status"]:
                bad(rid, f"publication_status {status} is not in publication-status.ttl")
        if record["kind"] == "model" and attributes.get("entity_level") not in vocab["entity-level"]:
            bad(rid, "entity_level is not in entity-level.ttl")
        if record["kind"] == "configuration":
            if attributes.get("configuration_type") not in vocab["configuration-type"]:
                bad(rid, "configuration_type is not in configuration-type.ttl")
        if record["kind"] == "claim":
            relations = [link["relation"] for link in record.get("links", [])]
            if relations.count("subject") != 1:
                bad(rid, "a claim needs exactly one subject link")
            for required in ("field", "value", "source_locator"):
                if required not in attributes:
                    bad(rid, f"claim is missing {required}")

        for path, text in walk_strings(record):
            for char, label in BANNED_CHARS.items():
                if char in text:
                    bad(rid, f"{label} in {path}")

    for text, ids in descriptions.items():
        if len(ids) > 1:
            kinds_here = {kinds[i] for i in ids}
            if kinds_here - {"configuration"}:
                problems.append(f"shared description between {ids}")

    for problem in problems:
        print("PROBLEM", problem)
    print(f"checked {len(records)} records, {len(problems)} problems")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
