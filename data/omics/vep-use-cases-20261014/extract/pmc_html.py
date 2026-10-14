"""Stable hash for a PMC article page (https://pmc.ncbi.nlm.nih.gov/articles/PMC.../).

Each request returns two per-request tokens: the content of <meta name="ncbi_phid"> and the
value of the csrfmiddlewaretoken hidden input. Everything else was byte-identical across two
retrievals on 2026-10-14. normalise() blanks those two values, so a re-download hashes the same.

Usage: python3 -I pmc_html.py <page.html> [...]   prints raw and normalised SHA-256.
"""
import hashlib
import re
import sys

PHID = re.compile(rb'(<meta name="ncbi_phid" content=")[^"]*(")')
CSRF = re.compile(rb'(name="csrfmiddlewaretoken" value=")[^"]*(")')


def normalise(data: bytes) -> bytes:
    data, n1 = PHID.subn(rb"\1\2", data)
    data, n2 = CSRF.subn(rb"\1\2", data)
    if n1 != 1 or n2 != 1:
        raise SystemExit(f"expected one ncbi_phid and one csrf token, found {n1} and {n2}")
    return data


def normalised_sha256(data: bytes) -> str:
    return hashlib.sha256(normalise(data)).hexdigest()


if __name__ == "__main__":
    for path in sys.argv[1:]:
        raw = open(path, "rb").read()
        print(path, hashlib.sha256(raw).hexdigest(), normalised_sha256(raw))
