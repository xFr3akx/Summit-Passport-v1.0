#!/usr/bin/env python3
import json,pathlib,re,unicodedata,urllib.parse,urllib.request,difflib,collections,concurrent.futures
ROOT=pathlib.Path(__file__).resolve().parents[1]
SRC=json.loads((ROOT/'data/germany_completion_12.json').read_text(encoding='utf-8'))
CAT=json.loads((ROOT/'app/src/main/assets/ui/catalog.json').read_text(encoding='utf-8'))['places']
OUT=ROOT/'data/germany_remaining_fast_review.json'
SUM=ROOT/'data/germany_remaining_fast_summary.json'
AREA_HINTS=('tal','schlucht','klamm','wald','moor','heide','seenland','altstadt','naturpark','gebiet','plateau','buchenwalder','buchenwälder','hohenweg','höhenweg','panoramastrasse','panoramastraße','seen','rummel')

def norm(s):
 s=unicodedata.normalize('NFKD',str(s or '')).casefold();s=''.join(c for c in s if not unicodedata.combining(c));s=s.replace('ß','ss');return ' '.join(re.findall(r'[a-z0-9]+',s))
def score(a,b):
 a,b=norm(a),norm(b)
 if not a or not b:return 0
 if a==b:return 1
 parts=[norm(x) for x in re.split(r'[/()]',a) if norm(x)]
 return max([difflib.SequenceMatcher(None,a,b).ratio()]+[difflib.SequenceMatcher(None,x,b).ratio() for x in parts])
def broad(n,a):
 x=norm(n+' '+a);return any(h in x for h in AREA_HINTS)
def osmkey(p):
 typ=str(p.get('osm_type') or '').upper()[:1];oid=p.get('osm_id');return typ+str(oid) if typ in {'N','W','R'} and oid is not None else None
def keyfromsrc(s):
 m=re.search(r'openstreetmap\.org/(node|way|relation)/(\d+)',str(s or ''))
 return ({'node':'N','way':'W','relation':'R'}[m.group(1)]+m.group(2)) if m else None
def existing_keys():
 d={}
 for x in CAT:
  if x.get('country')=='DE' and x.get('mapReady'):
   k=keyfromsrc(x.get('source'))
   if k:d[k]=x.get('id')
 return d
EX=existing_keys()

def prior_candidates(r):
 out=[]
 for c in r.get('candidates') or []:
  if not isinstance(c,dict):continue
  k=c.get('osmKey') or c.get('osm_key')
  nm=c.get('name') or c.get('label') or ''
  lat=c.get('lat') or c.get('latitude');lon=c.get('lon') or c.get('longitude')
  try:lat=float(lat);lon=float(lon)
  except:lat=lon=None
  out.append({'osmKey':k,'name':nm,'lat':lat,'lon':lon,'source':'prior_candidate','nameScore':score(r.get('name'),nm)})
 return out

def photon_one(r):
 q=' '.join(x for x in [r.get('name',''),r.get('area',''),'Deutschland'] if x)
 url='https://photon.komoot.io/api/?'+urllib.parse.urlencode({'q':q,'limit':12,'lang':'de'})
 req=urllib.request.Request(url,headers={'User-Agent':'SummitPassport/1.1.2 fast-audit'})
 try:
  with urllib.request.urlopen(req,timeout=8) as h:data=json.load(h)
 except Exception as e:return [],type(e).__name__+': '+str(e)
 out=[];seen=set()
 for f in data.get('features',[]):
  p=f.get('properties') or {};cc=str(p.get('countrycode') or '').lower()
  if cc and cc!='de':continue
  nm=str(p.get('name') or p.get('street') or p.get('city') or '')
  sc=score(r.get('name'),nm)
  if sc<0.82:continue
  k=osmkey(p)
  if k in seen:continue
  seen.add(k)
  try:lon,lat=f.get('geometry',{}).get('coordinates',[])[:2];lat=float(lat);lon=float(lon)
  except:lat=lon=None
  out.append({'osmKey':k,'name':nm,'lat':lat,'lon':lon,'osm_type':p.get('osm_type'),'osm_id':p.get('osm_id'),'source':'photon','nameScore':round(sc,4),'city':p.get('city'),'state':p.get('state'),'district':p.get('district'),'type':p.get('type')})
 return out,None

rows=SRC.get('unresolved') or []
network={}
need=[r for r in rows if not prior_candidates(r) and not r.get('queryChecked')]
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
 fut={ex.submit(photon_one,r):r.get('id') for r in need}
 for f in concurrent.futures.as_completed(fut):network[fut[f]]=f.result()

results=[]
for i,r in enumerate(rows,1):
 cs=prior_candidates(r);err=None
 if not cs and not r.get('queryChecked'):cs,err=network.get(r.get('id'),([],None))
 # retain only reasonably matching stored candidates
 cs=[c for c in cs if c.get('nameScore',0)>=0.82]
 cs.sort(key=lambda c:c.get('nameScore',0),reverse=True)
 # collapse same osm identity
 uniq=[];seen=set()
 for c in cs:
  k=c.get('osmKey') or (c.get('lat'),c.get('lon'),norm(c.get('name')))
  if k in seen:continue
  seen.add(k);uniq.append(c)
 cs=uniq
 status='UNRESOLVED';reason='no reliable candidate';chosen=None;dup=None
 strong=[c for c in cs if c.get('nameScore',0)>=0.94]
 if len(strong)==1 and (len(cs)==1 or strong[0].get('nameScore',0)-(cs[1].get('nameScore',0) if len(cs)>1 else 0)>=0.08):
  chosen=strong[0];k=chosen.get('osmKey')
  if k and k in EX:status='DUPLICATE';dup=EX[k];reason='same OSM identity already exists in current catalog'
  else:
   rep=broad(r.get('name',''),r.get('area','')) or (k and k.startswith(('W','R')))
   status='REPRESENTATIVE' if rep else 'READY';reason='single strong identity from existing evidence/Photon'
 elif cs:
  status='REVIEW';reason=f'{len(cs)} plausible candidates; identity not unique'
 elif err:
  status='REVIEW';reason='lookup failed; do not treat as not-found'
 elif r.get('queryChecked'):
  status='UNRESOLVED';reason='previous search completed without supported identity'
 result={'index':i,'id':r.get('id'),'name':r.get('name'),'category':r.get('category'),'area':r.get('area'),'status':status,'reason':reason,'chosen':chosen,'duplicateOf':dup,'candidates':cs[:5],'queryCheckedBefore':r.get('queryChecked'),'lookupError':err}
 results.append(result);print(f'{i:03d} {status:14s} {r.get("name")} :: {reason}')
counts=collections.Counter(r['status'] for r in results)
summary={'source_unresolved_count':len(rows),'network_queries':len(need),'counts':dict(counts),'safe_to_stage':counts['READY']+counts['REPRESENTATIVE'],'duplicates':counts['DUPLICATE'],'manual_review':counts['REVIEW'],'unresolved':counts['UNRESOLVED'],'production_overwritten':False}
OUT.write_text(json.dumps({'summary':summary,'results':results},ensure_ascii=False,indent=2)+'\n',encoding='utf-8');SUM.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print('SUMMARY '+json.dumps(summary,ensure_ascii=False))
