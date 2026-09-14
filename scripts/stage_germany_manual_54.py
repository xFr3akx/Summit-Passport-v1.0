#!/usr/bin/env python3
import json,math,pathlib,re,unicodedata,urllib.parse,urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
ROOT=pathlib.Path(__file__).resolve().parents[1]
MAN=ROOT/'data/germany_review_manual_resolution.json'
CAT=ROOT/'app/src/main/assets/ui/catalog.json'
OUT=ROOT/'data/germany_manual_54_staging.json'
OUTCAT=ROOT/'data/catalog_germany_manual_54_candidate.json'

def norm(s):
    s=unicodedata.normalize('NFKD',str(s or '')).encode('ascii','ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+',' ',s).strip()
def toks(s): return {x for x in norm(s).split() if len(x)>=4}
def dist(a,b):
    la1,lo1=a;la2,lo2=b
    x=math.radians(lo2-lo1)*math.cos(math.radians((la1+la2)/2));y=math.radians(la2-la1)
    return 6371000*math.hypot(x,y)
def photon(q):
    url='https://photon.komoot.io/api/?'+urllib.parse.urlencode({'q':q,'limit':10,'lang':'de'})
    req=urllib.request.Request(url,headers={'User-Agent':'SummitPassportManual54/1.1'})
    with urllib.request.urlopen(req,timeout=6) as r:return json.load(r).get('features',[])
def cand(f):
    p=f.get('properties',{});c=f.get('geometry',{}).get('coordinates') or [None,None]
    return {'lat':c[1],'lon':c[0],'osm_type':p.get('osm_type'),'osm_id':p.get('osm_id'),'name':p.get('name') or '',
            'countrycode':(p.get('countrycode') or '').upper(),'state':p.get('state') or '','county':p.get('county') or '',
            'city':p.get('city') or p.get('town') or p.get('village') or '','district':p.get('district') or '',
            'type':p.get('type') or '','key':p.get('osm_key') or p.get('key'),'value':p.get('osm_value') or p.get('value')}
def score(r,c):
    if c['countrycode']!='DE' or c['lat'] is None:return -99
    n=norm(r['name']);cn=norm(c['name']);parts=[norm(x) for x in re.split(r'[/—-]',r['name']) if norm(x)];s=0
    if cn==n:s+=8
    elif any(cn==p for p in parts):s+=7
    elif cn and (cn in n or n in cn):s+=5
    elif any(p and (p in cn or cn in p) for p in parts):s+=4
    else:s+=min(3,len(toks(r['name'])&toks(c['name'])))
    context=' '.join([c['state'],c['county'],c['city'],c['district']]);s+=min(5,len(toks(r.get('area',''))&toks(context))*2)
    if str(c['type']).lower() in {'street','house','postcode'}:s-=4
    if c['key'] in ('highway','addr'):s-=4
    return s
def osm_url(c):
    t={'N':'node','W':'way','R':'relation','node':'node','way':'way','relation':'relation'}.get(str(c['osm_type']))
    return f"https://www.openstreetmap.org/{t}/{c['osm_id']}" if t and c.get('osm_id') else None

def resolve_rep(r):
    queries=[r['name']+', Deutschland',r['name']+', '+r['area'].replace('/',' ')+', Deutschland']
    pool={};errs=[]
    with ThreadPoolExecutor(max_workers=2) as ex:
        fut={ex.submit(photon,q):q for q in queries}
        for f in as_completed(fut):
            try:
                for feat in f.result():
                    c=cand(feat);key=(c['osm_type'],str(c['osm_id']),round(c['lat'] or 0,6),round(c['lon'] or 0,6));pool[key]=c
            except Exception as e:errs.append(type(e).__name__)
    ranked=sorted(((score(r,c),c) for c in pool.values()),key=lambda x:x[0],reverse=True)
    if not ranked or ranked[0][0]<5:return None,'no strong representative candidate',errs,ranked[:3]
    top=ranked[0];second=ranked[1][0] if len(ranked)>1 else -99
    if second>=top[0]-1 and (ranked[1][1]['osm_id']!=top[1]['osm_id'] or ranked[1][1]['osm_type']!=top[1]['osm_type']):
        return None,f'ambiguous representative candidates {top[0]} vs {second}',errs,ranked[:3]
    if not osm_url(top[1]):return None,'candidate has no OSM identity',errs,ranked[:3]
    return top[1],None,errs,ranked[:3]

manual=json.loads(MAN.read_text(encoding='utf-8'));cat=json.loads(CAT.read_text(encoding='utf-8'));places=cat['places']
existing=[p for p in places if p.get('country')=='DE' and p.get('mapReady') and p.get('lat') is not None]
rows=[r for r in manual['results'] if r['finalStatus'] in ('READY','REPRESENTATIVE')]
resolved={}
with ThreadPoolExecutor(max_workers=8) as ex:
    fut={ex.submit(resolve_rep,r):r for r in rows if not (r.get('chosen') and r['chosen'].get('lat') is not None)}
    for f in as_completed(fut):resolved[fut[f]['id']]=f.result()
results=[]
for r in rows:
    out={'id':r['id'],'name':r['name'],'category':r['category'],'area':r['area'],'requestedStatus':r['finalStatus']};chosen=r.get('chosen')
    if chosen and chosen.get('lat') is not None:
        c={'lat':chosen['lat'],'lon':chosen['lon'],'osm_type':None,'osm_id':None,'name':r['name'],'countrycode':'DE','state':'','county':'','city':'','district':'','type':'','key':None,'value':None}
        source=chosen.get('source');role=chosen.get('role') or ('osm_point' if r['finalStatus']=='READY' else 'representative_point_not_entrance')
        if chosen.get('osmKey'):
            m=re.match(r'([NWR])(\d+)',chosen['osmKey'])
            if m:c['osm_type'],c['osm_id']=m.group(1),int(m.group(2));source=source or osm_url(c)
        conf='manual_exact'
    else:
        c,reason,errs,ranked=resolved.get(r['id'],(None,'lookup missing',[],[]))
        if not c:
            out.update(status='REVIEW',reason=reason,errors=errs,candidates=[x[1] for x in ranked]);results.append(out);continue
        source=osm_url(c);role='representative_point_not_entrance';conf='photon_unique_representative'
    near=[]
    for p in existing:
        if p['id']==r['id']:continue
        d=dist((float(c['lat']),float(c['lon'])),(float(p['lat']),float(p['lon'])))
        if d<80:near.append((round(d,1),p['id'],p['name']))
    if near:
        out.update(status='DUPLICATE',reason='within 80m of existing DE map point',chosen=c,near=sorted(near)[:5]);results.append(out);continue
    out.update(status='STAGE',lat=c['lat'],lon=c['lon'],source=source,coordinateRole=role,confidence=conf,chosen=c);results.append(out)

stage=[x for x in results if x['status']=='STAGE'];newcat=json.loads(json.dumps(cat));newby={p['id']:p for p in newcat['places']};missing_runtime=[]
for x in stage:
    p=newby.get(x['id'])
    if not p:
        missing_runtime.append({
            'id':x['id'],'country':'DE','name':x['name'],'category':x['category'],'lat':x['lat'],'lon':x['lon'],
            'mapReady':True,'region':'','area':x['area'],'source':x['source'],'coordinateRole':x['coordinateRole'],
            'note':'staging_only_missing_from_runtime; complete region/collection metadata before production import'
        })
        continue
    if p.get('mapReady'):
        raise SystemExit('already mapReady '+x['id'])
    p.update(lat=x['lat'],lon=x['lon'],mapReady=True,source=x['source'],coordinateRole=x['coordinateRole'])
summary={'inputResolved':54,'stage':len(stage),'duplicate':sum(x['status']=='DUPLICATE' for x in results),'review':sum(x['status']=='REVIEW' for x in results),'missingRuntime':len(missing_runtime),'productionOverwritten':False}
OUT.write_text(json.dumps({'summary':summary,'results':results,'newRuntimeRecords':missing_runtime},ensure_ascii=False,indent=2)+'\n',encoding='utf-8');OUTCAT.write_text(json.dumps(newcat,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
print('SUMMARY',json.dumps(summary,ensure_ascii=False))
for x in results:print(x['status'],x['name'],x.get('reason',''),x.get('lat',''),x.get('lon',''))
if missing_runtime:
    print('MISSING_RUNTIME',len(missing_runtime),','.join(x['id'] for x in missing_runtime))
