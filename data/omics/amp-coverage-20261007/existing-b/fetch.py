import json,pathlib,urllib.request,gzip,hashlib,datetime,concurrent.futures
r=pathlib.Path(__file__).parent;r.joinpath('artifacts').mkdir(exist_ok=True);xs=json.loads((r/'inspection-input.json').read_text()); selects=['agront-2024-fig3e-source','uc20260930-source-proteingym-amfr-spearman','uc-clinical-20260930-source-talos-table1','ucc-research-source-mprabc','uc20260930-source-rhomax-2024','uc-clinical-20260930-source-oncovi']
def fetch(pair):
 o,sid=pair;s=next(x for x in o['referenced'] if x['id']==sid);a=s['attributes'];url=a.get('artifact_retrieval_endpoint') or a.get('artifact_url') or a['url'];ext='xml' if 'XML' in url else 'csv' if url.endswith('.csv') else 'txt' if url.endswith('.txt') else 'html';t=datetime.datetime.now(datetime.timezone.utc).isoformat();z={'case_id':o['case']['id'],'source_id':sid,'url':url,'request_started_at':t,'baseline_sha256':a.get('artifact_sha256'),'pinned_version':a.get('version')}
 try:
  response=urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=30);raw=response.read();f=r/'artifacts'/f'{sid}.{ext}.gz';f.write_bytes(gzip.compress(raw,9,mtime=0));z.update(retrieved_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),final_url=response.url,http_status=response.status,content_type=response.headers.get('Content-Type'),sha256=hashlib.sha256(raw).hexdigest(),artifact=str(f),bytes=len(raw));z['byte_identical_to_baseline']=z['sha256']==z['baseline_sha256']
 except Exception as e:z.update(error=str(e),checked_at=datetime.datetime.now(datetime.timezone.utc).isoformat())
 return z
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as p:out=list(p.map(fetch,zip(xs,selects)))
(r/'retrieval.json').write_text(json.dumps(out,indent=2)+'\n')
for x in out:print(x['case_id'],x.get('bytes'),x.get('byte_identical_to_baseline'),x.get('error'))
