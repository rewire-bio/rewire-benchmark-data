import urllib.request,datetime,gzip,hashlib,json,pathlib,concurrent.futures
p=pathlib.Path(__file__).parent;(p/'artifacts').mkdir(exist_ok=True)
items={'enigma':'https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11393667/fullTextXML','abdelaal':'https://www.ebi.ac.uk/europepmc/webservices/rest/PMC6734286/fullTextXML','cppc':'https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13228547/fullTextXML','civicfact':'https://www.biorxiv.org/content/10.1101/2025.09.10.675443.full.pdf','gears':'https://static-content.springer.com/esm/art%3A10.1038%2Fs41587-023-01905-6/MediaObjects/41587_2023_1905_MOESM1_ESM.pdf','msalign':'https://arxiv.org/pdf/2605.19752v2'}
def fetch(k,u):
 t=datetime.datetime.now(datetime.timezone.utc).isoformat(); r=dict(key=k,url=u,retrieved_at=t)
 try:
  res=urllib.request.urlopen(u,timeout=40);b=res.read();typ='pdf' if b.startswith(b'%PDF') else 'xml' if b'<?xml' in b[:100] else 'html';r.update(status='fetched',type=typ,bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),resolved_url=res.url);a=p/'artifacts'/(k+'.'+typ+'.gz');a.write_bytes(gzip.compress(b,mtime=0));r['artifact']=str(a)
 except Exception as e:r.update(status='blocked',error=str(e))
 (p/(k+'.retrieval.json')).write_text(json.dumps(r,indent=2)+'\n');return r
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
 for r in ex.map(lambda kv:fetch(*kv),items.items()):print(r)
