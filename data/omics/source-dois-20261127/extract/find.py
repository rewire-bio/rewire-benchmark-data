import json, re, urllib.parse, collections, sys
DOI = re.compile(r"10\.\d{4,9}/[^\s\"'<>|)\]]+", re.I)
rows = []
for line in open("data/entities/sources.jsonl"):
    d = json.loads(line); a = d["attributes"]
    if a.get("doi"):
        continue
    found = []
    for field in ("url", "artifact_url", "original_url", "retrieval_url", "original_artifact_url"):
        v = urllib.parse.unquote(a.get(field) or "")
        for m in DOI.findall(v):
            found.append((field, m, v))
    for m in DOI.findall(d["name"] or ""):
        found.append(("name", m, d["name"]))
    if not found:
        continue
    def clean(m):
        m = m.rstrip(".,;:")
        m = re.sub(r"(/mediaobjects/.*|/MediaObjects/.*|_esm.*|\.full(\.pdf)?|\.pdf|\.csv|\.xlsx?|\.zip|v\d+$|/suppl.*|/supplementary.*|/full$|/abstract$)", "", m, flags=re.I)
        return m.lower()
    dois = sorted({clean(m) for _, m, _ in found})
    host = urllib.parse.urlparse(a.get("url") or a.get("artifact_url") or "").netloc
    rows.append({"id": d["id"], "name": d["name"], "status": d["status"], "host": host, "dois": dois,
                 "where": sorted({f for f, _, _ in found}), "url": a.get("url") or a.get("artifact_url")})
json.dump(rows, open(sys.argv[1], "w"), indent=0, ensure_ascii=False)
print(len(rows), "sources hold a DOI only in a URL or name")
print("by host:", collections.Counter(r["host"] for r in rows).most_common(20))
print("more than one DOI:", sum(len(r["dois"]) > 1 for r in rows))
