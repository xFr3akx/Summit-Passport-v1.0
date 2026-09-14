#!/usr/bin/env python3
import json, pathlib, re, unicodedata, urllib.parse, urllib.request, time, difflib, math, collections

ROOT=pathlib.Path(__file__).resolve().parents[1]
SRC=ROOT/'data/germany_completion_12.json'
CAT=ROOT/'app/src/main/assets/ui/catalog.json'
OUT=ROOT/'data/germany_remaining_review.json'
SUMMARY=ROOT/'data/germany_remaining_review_summary.json'

AREA_HINTS=('tal','schlucht','klamm','wald','moor','heide','seenland','altstadt','naturpark','gebiet','plateau','buchenwalder','buchenwälder','hohenweg','höhenweg','panoramastrasse','panoramastraße','seen','rummel')
GENERIC_WORDS={'der','die','das','bei','am','an','im','in','und','von','vom','zum','zur','de','germany','deutschland'}

def norm(v):
    s=unicodedata.normalize('NFKD',str(v or '')).casefold()
    s=''.join(c for c in s if not unicodedata.combining(c))
    s=s.replace('ß','ss')
    return ' '.join(re.findall(r'[a-z0-9]+',s))

def toks(v): return {x for x in norm(v).split() if len(x)>2 and x not in GENERIC_WORDS}

def osm_key_from_source(src):
    m=re.search(r'openstreetmap\.org/(node|way|relation)/(\d+)',str(src or ''))
    if not m:return None
    return {'node':'N','way':'W','relation':'R'}[m.group(1)]+m.group(2)

def candidate_osm_key(p):
    typ=str(p.get('osm_type') or '').upper()[:1]
    oid=p.get('osm_id')
    return typ+str(oid) if typ in {'N','W','R'} and oid is not None else None

def candidate_name(p):
    return str(p.get('name') or p.get('street') or p.get('city') or p.get('locality') or '').strip()

def country_de(p):
    cc=str(p.get('countrycode') or '').lower()
    country=norm(p.get('country'))
    return cc=='de' or country in {'deutschland','germany'}

def hav(a,b):
    lat1,lon1=a;lat2,lon2=b;R=6371000
    p1,p2=math.radians(lat1),math.radians(lat2);dp=math.radians(lat2-lat1);dl=math.radians(lon2-lon1)
    q=math.sin(dp/2)**2+math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2*R*math.asin(min(1,math.sqrt(q)))

def photon(q):
    url='https://photon.komoot.io/api/?'+urllib.parse.urlencode({'q':q,'limit':15,'lang':'de'})
    req=urllib.request.Request(url,headers={'User-Agent':'SummitPassport/1.1.2 database-audit'})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req,timeout=12) as r:
                data=json.load(r)
            return data.get('features',[]),None
        except Exception as e:
            err=type(e).__name__+': '+str(e)
            if attempt<2: time.sleep(1.0*(attempt+1))
    return [],err

def props(feature):
    p=dict(feature.get('properties') or {})
    try:
        lon,lat=feature['geometry']['coordinates'][:2];p['_lat']=float(lat);p['_lon']=float(lon)
    except Exception: p['_lat']=p['_lon']=None
    return p

def name_score(target,cand):
    a,b=norm(target),norm(cand)
    if not a or not b:return 0.0
    if a==b:return 1.0
    # slash/parenthesis source names often contain a precise alias plus context.
    parts=[norm(x) for x in re.split(r'[/()]',target) if norm(x)]
    best=max([difflib.SequenceMatcher(None,a,b).ratio()]+[difflib.SequenceMatcher(None,x,b).ratio() for x in parts])
    at,bt=toks(a),toks(b)
    if at and bt:
        overlap=len(at&bt)/max(1,len(at|bt))
        best=max(best,0.65*best+0.35*overlap)
    return best

def context_score(area,p):
    at=toks(area)
    if not at:return 0.0
    vals=' '.join(str(p.get(k) or '') for k in ('city','district','county','state','locality','name'))
    pt=toks(vals)
    return len(at&pt)/max(1,min(len(at),4))

def broad_name(name,area):
    n=norm(name+' '+area)
    return any(h in n for h in AREA_HINTS)

def role_for(p,broad):
    typ=str(p.get('osm_type') or '').upper()[:1]
    return 'representative_point_not_entrance' if broad or typ in {'W','R'} else 'osm_point'

src=json.loads(SRC.read_text(encoding='utf-8'))
unresolved=src.get('unresolved') or []
catalog=json.loads(CAT.read_text(encoding='utf-8'))['places']
existing=[];existing_osm={};by_name=collections.defaultdict(list)
for x in catalog:
    if x.get('country')!='DE' or not x.get('mapReady'): continue
    lat=x.get('lat');lon=x.get('lon')
    try: lat=float(lat);lon=float(lon)
    except Exception: lat=lon=None
    rec={'id':x.get('id'),'name':x.get('name'),'category':x.get('category'),'lat':lat,'lon':lon,'source':x.get('source')}
    existing.append(rec);by_name[norm(x.get('name'))].append(rec)
    ok=osm_key_from_source(x.get('source'))
    if ok:existing_osm.setdefault(ok,[]).append(rec)

results=[]
for i,r in enumerate(unresolved,1):
    name=r.get('name','');area=r.get('area','');broad=broad_name(name,area)
    queries=[]
    if area: queries.append(f'{name} {area} Deutschland')
    queries += [f'{name} Deutschland',name]
    feats=[];errs=[];seen=set()
    for q in queries:
        fs,e=photon(q)
        if e:errs.append({'query':q,'error':e})
        for f in fs:
            p=props(f);key=candidate_osm_key(p) or json.dumps(f.get('geometry',{}),sort_keys=True)
            if key in seen:continue
            seen.add(key);feats.append(p)
        if len(feats)>=12:break
        time.sleep(0.12)
    cand=[]
    for p in feats:
        if not country_de(p):continue
        nm=candidate_name(p);ns=name_score(name,nm);cs=context_score(area,p)
        # Keep exact/high-name matches, or slightly weaker ones with strong regional context.
        if ns>=0.86 or (ns>=0.74 and cs>=0.5):
            cand.append({'osmKey':candidate_osm_key(p),'name':nm,'nameScore':round(ns,4),'contextScore':round(cs,4),'lat':p.get('_lat'),'lon':p.get('_lon'),'osm_type':p.get('osm_type'),'osm_id':p.get('osm_id'),'city':p.get('city'),'district':p.get('district'),'county':p.get('county'),'state':p.get('state'),'type':p.get('type'),'key':p.get('key'),'value':p.get('value')})
    cand.sort(key=lambda x:(x['nameScore']+0.18*x['contextScore']),reverse=True)
    status='UNRESOLVED';reason='no plausible Germany OSM/Photon identity';chosen=None;duplicate_of=None
    if cand:
        # collapse exact same OSM identity
        uniq=[];keys=set()
        for c in cand:
            k=c['osmKey'] or (round(c['lat'] or 0,6),round(c['lon'] or 0,6),norm(c['name']))
            if k in keys:continue
            keys.add(k);uniq.append(c)
        cand=uniq
        top=cand[0];second=cand[1] if len(cand)>1 else None
        top_total=top['nameScore']+0.18*top['contextScore'];second_total=(second['nameScore']+0.18*second['contextScore']) if second else -1
        decisive=(top['nameScore']>=0.98 and (not second or top_total-second_total>=0.08)) or (top['nameScore']>=0.90 and top['contextScore']>=0.5 and (not second or top_total-second_total>=0.10))
        if decisive:
            chosen=top
            if top['osmKey'] and top['osmKey'] in existing_osm:
                status='DUPLICATE';duplicate_of=existing_osm[top['osmKey']][0]['id'];reason='same OSM identity already published'
            else:
                # secondary proximity/name duplicate protection
                near=[]
                if top['lat'] is not None:
                    for ex in existing:
                        if ex['lat'] is None:continue
                        d=hav((top['lat'],top['lon']),(ex['lat'],ex['lon']))
                        if d<120 and name_score(name,ex['name'])>=0.82:near.append((d,ex))
                if near:
                    near.sort(key=lambda x:x[0]);status='DUPLICATE';duplicate_of=near[0][1]['id'];reason=f'near-identical published place within {near[0][0]:.0f} m'
                else:
                    status='REPRESENTATIVE' if role_for(top,broad).startswith('representative') else 'READY'
                    reason='single decisive Germany OSM identity with name/context match'
        else:
            status='REVIEW';reason=f'ambiguous plausible candidates: {len(cand)}'
    elif errs and len(errs)==len(queries):
        status='REVIEW';reason='geocoder/network failed for all queries'
    result={'index':i,'id':r.get('id'),'name':name,'category':r.get('category'),'area':area,'previousReason':r.get('reason'),'status':status,'reason':reason,'chosen':chosen,'duplicateOf':duplicate_of,'coordinateRole':role_for(chosen,broad) if chosen and status in {'READY','REPRESENTATIVE'} else None,'candidates':cand[:6],'errors':errs}
    results.append(result)
    print(f'{i:03d} {status:14s} {name} :: {reason}')

counts=collections.Counter(x['status'] for x in results)
summary={'source_unresolved_count':len(unresolved),'counts':dict(counts),'safe_to_stage':counts.get('READY',0)+counts.get('REPRESENTATIVE',0),'duplicates':counts.get('DUPLICATE',0),'manual_review':counts.get('REVIEW',0),'unresolved':counts.get('UNRESOLVED',0),'production_overwritten':False,'policy':{'READY':'one decisive point-like OSM identity','REPRESENTATIVE':'one decisive area/way/relation identity; representative point','DUPLICATE':'same OSM identity or near-identical existing map place','REVIEW':'multiple plausible identities or failed lookup','UNRESOLVED':'no plausible Germany identity found'}}
OUT.write_text(json.dumps({'summary':summary,'results':results},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
SUMMARY.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('SUMMARY '+json.dumps(summary,ensure_ascii=False))
