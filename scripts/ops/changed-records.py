"""Print the IDs of records a pull request adds or changes, for the subset shape check.

Usage: python3 scripts/ops/changed-records.py <base-ref> [<head-ref>]

Exits 0 and prints one ID per line when the change touches only record files, batch folders and
documents, so checking the changed records is enough. Exits 1 when anything else changed (code,
the ontology, vocabularies, workflows, the release configuration) or a record was removed: the
caller then runs the full-store checks.
"""
import re
import subprocess
import sys

RECORDS = ("data/entities/", "data/evidence/")
HARMLESS = ("data/provenance/", "data/omics/", "docs/")
FULL = ("data/omics/release-config.json",)
ID = re.compile(r'^[+-]\{"id":"([^"]+)"')


def git(*args: str) -> str:
    return subprocess.run(["git", *args], check=True, capture_output=True, text=True).stdout


def main(base: str, head: str = "HEAD") -> int:
    names = [n for n in git("diff", "--name-only", base, head).splitlines() if n]
    if any(n in FULL or not n.startswith(RECORDS + HARMLESS) for n in names):
        return 1
    added: set[str] = set()
    removed: set[str] = set()
    for name in names:
        if not name.startswith(RECORDS):
            continue
        for line in git("diff", "-U0", base, head, "--", name).splitlines():
            match = ID.match(line)
            if match:
                (added if line[0] == "+" else removed).add(match.group(1))
    if removed - added:
        return 1
    print("\n".join(sorted(added)))
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:3]))
