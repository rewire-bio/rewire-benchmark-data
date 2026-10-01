"""Bounded metadata/source checks. Writes only this pilot directory.

Run from the repository root. This never imports scores or renews reviews.
"""
from __future__ import annotations
import datetime
import gzip
import hashlib
import json
from pathlib import Path
import re
import urllib.error
import urllib.request

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
RELEASE = "2026-09-30-e37e3ab1284d"
NOW = lambda: datetime.datetime.now(datetime.timezone.utc).isoformat()
sha = lambda data: hashlib.sha256(data).hexdigest()
retrievals = []


def fetch(url: str, name: str, archive: bool = True):
    receipt = {"requested_url": url, "retrieved_at": NOW(), "method": "Python urllib HTTPS GET", "name": name}
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "rewire-database-maintenance-pilot/1.0", "Accept": "application/vnd.github+json" if "api.github.com" in url else "*/*"})
        with urllib.request.urlopen(req, timeout=30) as response:
            body = response.read(8_000_001)
            if len(body) > 8_000_000:
                raise ValueError("Pilot response size limit exceeded")
            receipt.update(status="retrieved", http_status=response.status, final_url=response.url, sha256=sha(body), bytes=len(body), content_type=response.headers.get("Content-Type"))
        if archive:
            path = OUT / "sources" / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(body)
            receipt["artifact"] = str(path.relative_to(ROOT))
        retrievals.append(receipt)
        return body
    except Exception as error:
        receipt.update(status="blocked", reason=str(error))
        retrievals.append(receipt)
        return None


def main():
    if (OUT / "retrievals.json").exists():
        raise SystemExit("This pilot already has receipts. Preserve them and use a new run directory for another retrieval.")
    snapshot = json.loads(gzip.decompress((ROOT / f"data/omics/releases/{RELEASE}/catalogue.json.gz").read_bytes()))
    records = {r["id"]: r for r in snapshot["records"]}
    updates = []
    for source_id in ["src-discovery-songlab-cal-tape", "evidence-reported-phylogpn-2025-readme-md"]:
        record = records[source_id]
        source = record["attributes"]
        match = re.match(r"https://github.com/([^/]+/[^/]+)/blob/([a-f0-9]{40})/(.+)", source["url"])
        assert match is not None
        repository, pinned, filename = match.groups()
        slug = repository.replace("/", "-")
        head_body = fetch(f"https://api.github.com/repos/{repository}/commits/HEAD", f"{slug}-head.json")
        original = fetch(f"https://raw.githubusercontent.com/{repository}/{pinned}/{filename}", f"{slug}-{pinned}-README.md")
        check = {"source_id": source_id, "repository": repository, "pinned_revision": pinned,
                 "recorded_artifact_sha256": source.get("artifact_sha256"), "recorded_retrieved_at": source.get("retrieved_at"),
                 "pinned_artifact_sha256": sha(original) if original else None,
                 "pinned_artifact_matches_record": sha(original) == source.get("artifact_sha256") if original else None}
        if head_body:
            head = json.loads(head_body)
            current = head["sha"]
            latest = fetch(f"https://raw.githubusercontent.com/{repository}/{current}/{filename}", f"{slug}-{current}-current-README.md")
            check.update(current_revision=current, current_commit_url=head["html_url"],
                         current_commit_date=head["commit"]["committer"]["date"], head_changed=current != pinned,
                         repository_decision="review_required_head_changed" if current != pinned else "head_unchanged",
                         current_artifact_sha256=sha(latest) if latest else None,
                         artifact_changed=original != latest if original is not None and latest is not None else None)
            if original is None or latest is None or check["pinned_artifact_matches_record"] is not True:
                check["decision"] = "blocked_source_integrity_or_access"
            else:
                check["decision"] = "review_required" if original != latest else "checked_document_unchanged"
        else:
            check["decision"] = "blocked_head_lookup"
        updates.append(check)
    # Revisit the explicitly pending glycomics lead at a pinned official version.
    body = fetch("https://api.github.com/repos/BojarLab/GlycoGym/commits/HEAD", "BojarLab-GlycoGym-head.json")
    if body:
        revision = json.loads(body)["sha"]
        fetch(f"https://raw.githubusercontent.com/BojarLab/GlycoGym/{revision}/README.md", f"BojarLab-GlycoGym-{revision}-README.md")
    # Independent HTTP receipt for the primary article. Browser reading is logged
    # separately if the publisher prevents this direct request.
    fetch("https://www.nature.com/articles/s41586-026-11005-5", "gpn-star-article.html", archive=False)
    (OUT / "retrievals.json").write_text(json.dumps({"checked_at": NOW(), "retrievals": retrievals, "existing_source_checks": updates}, indent=2) + "\n")
    print(json.dumps({"retrievals": len(retrievals), "existing_source_checks": updates}, indent=2))


if __name__ == "__main__":
    main()
