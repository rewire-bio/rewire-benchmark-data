import sys, zipfile, re
import xml.etree.ElementTree as ET
NS={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
def sheet_cells(path, name):
    z=zipfile.ZipFile(path)
    wb=ET.fromstring(z.read('xl/workbook.xml'))
    rels=ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
    rmap={r.get('Id'):r.get('Target') for r in rels}
    sid=[s for s in wb.find('m:sheets',NS) if s.get('name')==name][0].get('{%s}id'%NS['r'])
    target=rmap[sid].lstrip('/'); target=target if target.startswith('xl/') else 'xl/'+target
    ss=[]
    if 'xl/sharedStrings.xml' in z.namelist():
        for si in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('m:si',NS):
            ss.append(''.join(t.text or '' for t in si.iter('{%s}t'%NS['m'])))
    styles=ET.fromstring(z.read('xl/styles.xml'))
    numfmts={int(n.get('numFmtId')):n.get('formatCode') for n in styles.iter('{%s}numFmt'%NS['m'])}
    xfs=[int(x.get('numFmtId',0)) for x in styles.find('m:cellXfs',NS)]
    out={}
    for c in ET.fromstring(z.read(target)).iter('{%s}c'%NS['m']):
        v=c.find('m:v',NS); f=c.find('m:f',NS)
        if v is None: continue
        t=c.get('t'); val=v.text
        if t=='s': val=ss[int(val)]
        fid=xfs[int(c.get('s',0))]; fmt=numfmts.get(fid, 'General' if fid==0 else f'builtin:{fid}')
        out[c.get('r')]=(val,t,fmt, f is not None)
    return out
if __name__=='__main__':
    cells=sheet_cells(sys.argv[1],sys.argv[2])
    for k,v in list(cells.items())[:int(sys.argv[3]) if len(sys.argv)>3 else 10**6]: print(k,v)
