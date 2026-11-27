import json, re, collections, urllib.parse, sys
rows = json.load(open("../../gaps/fix/dois.json"))
def norm(d):
    d = d.split("&")[0]
    d = re.sub(r"/(fulltext|pdf)$", "", d)
    d = re.sub(r"(v\d+)(\.full)?$", "", d) if d.startswith(("10.1101/", "10.64898/")) else d
    d = re.sub(r"\.s\d{3}$", "", d)          # PLOS supplementary item -> its article
    return d.rstrip(".,;:/")
out, odd = [], []
for r in rows:
    ds = sorted({norm(d) for d in r["dois"]})
    url = urllib.parse.unquote(r["url"] or "").lower()
    in_url = [d for d in ds if d in url]
    if len(ds) != 1:
        odd.append((r["id"], ds, r["url"], r["name"][:60])); continue
    d = ds[0]
    host = r["host"]
    if host == "doi.org": origin = "the source's URL is the doi.org resolver address for this DOI"
    elif host in ("www.biorxiv.org", "api.biorxiv.org"): origin = "the source's URL is the bioRxiv page or API record of this preprint DOI"
    elif host == "europepmc.org": origin = "the source is the Europe PMC record of this preprint, and its name states the DOI"
    elif host in ("media.springernature.com", "static-content.springer.com"): origin = "the source is a supplementary file whose Springer Nature address names the article DOI"
    elif host == "journals.plos.org": origin = "the source is a PLOS supplementary item (item DOI with a .sNNN suffix); it is recorded under its article's DOI, as the store records other supplements"
    elif host == "zenodo.org": origin = None   # concept DOI of all versions, not this record's version DOI
    elif host in ("www.pnas.org", "harvest.aps.org"): origin = "the source's URL is the publisher's article address containing this DOI"
    elif host == "www.nature.com": origin = "the source is a Nature article page whose name states the article DOI"
    else: origin = None
    if origin is None or (not in_url and host not in ("europepmc.org", "www.nature.com", "journals.plos.org")):
        odd.append((r["id"], ds, r["url"], r["name"][:60])); continue
    out.append({"id": r["id"], "doi": d, "origin": origin, "host": host})
json.dump({"fill": out, "odd": odd}, open(sys.argv[1], "w"), indent=0, ensure_ascii=False)
print(len(out), "to fill;", len(odd), "need a look")
for o in odd: print("  ", o)
