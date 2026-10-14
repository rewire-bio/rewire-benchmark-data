"""Write sources.md from the source records in batch.jsonl."""
import hashlib
import json
import os

BATCH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
recs = [json.loads(l) for l in open(os.path.join(BATCH, "batch.jsonl"))]
src = [r for r in recs if r["kind"] == "source"]
gz = hashlib.sha256(open(os.path.join(BATCH, "artifacts", "PMC9748256.xml.gz"), "rb").read()).hexdigest()
out = ["# Sources", "",
       "All retrievals ran on 2026-10-14 (UTC) with curl or `gh api`. Hashes are of the downloaded bytes, except PMC article pages (`pmc.ncbi.nlm.nih.gov/articles/...`), "
       "whose `artifact_sha256` is taken after blanking two per-request tokens (`extract/pmc_html.py`); the raw hash of the retrieval is in each record's `hash_scope`. "
       f"Only the CC BY Pejaver et al. 2022 XML is archived (`artifacts/PMC9748256.xml.gz`, `gzip -9 -n`, gzip SHA-256 `{gz}`); the other artifacts are not archived, "
       "because their licences do not allow it or because they are not needed to re-run the extraction.", ""]
CAL = ("pejaver2022", "bergquist2025", "stenton2024", "tejura2024")


def section(title, rs):
    out.extend([f"## {title}", ""])
    for r in sorted(rs, key=lambda r: r["id"]):
        a = r["attributes"]
        out.extend([f"### {r['name']}", "", f"- Record: `{r['id']}`", f"- Artifact: {a['url']}", f"- Version: {a['version']}"]
                   + ([f"- DOI: {a['doi']}"] if a.get("doi") else [])
                   + [f"- Retrieved: {a['retrieved_at']}", f"- SHA-256: `{a['artifact_sha256']}`", f"- Licence: {a['licence']}", ""])


section("Calibration sources for use case #151", [r for r in src if r["id"].rsplit("-", 1)[-1] in CAL])
section("Primary sources for the #153-#155 predictors", [r for r in src if r["id"].rsplit("-", 1)[-1] not in CAL])
open(os.path.join(BATCH, "sources.md"), "w").write("\n".join(out))
