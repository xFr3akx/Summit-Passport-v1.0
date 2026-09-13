#!/usr/bin/env python3
import argparse,csv,json,math,pathlib,re,unicodedata,uuid
from collections import Counter

ROOT=pathlib.Path(__file__).resolve().parents[1]
CATALOG=ROOT/'app/src/main/assets/ui/catalog.json'
QUEUE=ROOT/'data/new_places_queue.csv'
REPORT=ROOT/'data/new_places_report.json'
NEXT=ROOT/'data/catalog_next.json'
NS=uuid.UUID('6e65b31a-e889-4d19-a5e1-6642d28a6f6c')
VALID={'peak','pass','castle','waterfall','cave','rock','water','nature','viewpoint','heritage','lighthouse','industrial','underground','memory','trail'}
ALIASES={'pass_saddle':'pass','rock_geology':'rock','nature_viewpoint':'viewpoint','castle_fortress':'castle','heritage_object':'heritage','trail_experience':'trail','nature_reserve':'nature'}

def norm(s):
    s=unicodedata.normalize('NFKD',str(s or '')).casefold()
    s=''.join(c for c in s if not unicodedata.combining(c))
    return ' '.join(re.findall(r'[a-z0-9]+',s))

def f(v):
    try:return float(str(v).replace(',','.')) if str(v).strip() else None
    except:return None

def dist(a,b,c,d):
    r=6371000;p1=math.radians(a);p2=math.radians(c);dp=math.radians(c-a);dl=math.radians(d-b)
    x=math.sin(dp/2)**2+math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2*r*math.atan2(math.sqrt(x),math.sqrt(1-x))

def category(v):
    k=norm(v).replace(' ','_');k=ALIASES.get(k,k)
    return k if k in VALID else None

def load_queue(path):
    if path.suffix.lower()=='.json':
        d=json.loads(path.read_text(encoding='utf-8'))
        return d if isinstance(d,list) else d.get('places') or d.get('candidates') or d.get('records') or []
    with path.open(encoding='utf-8-sig',newline='') as h:return list(csv.DictReader(h))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('queue',nargs='?',type=pathlib.Path,default=QUEUE);ap.add_argument('--catalog',type=pathlib.Path,default=CATALOG);ap.add_argument('--report',type=pathlib.Path,default=REPORT);ap.add_argument('--output',type=pathlib.Path,default=NEXT);a=ap.parse_args()
    cat=json.loads(a.catalog.read_text(encoding='utf-8'));places=cat['places'];results=[];new=[]
    known_ids={p.get('id') for p in places};index={}
    for p in places:index.setdefault((p.get('country'),norm(p.get('name'))),[]).append(p)
    for i,row in enumerate(load_queue(a.queue),1):
        country=str(row.get('country','')).strip().upper();name=str(row.get('name','')).strip();catg=category(row.get('category'));lat=f(row.get('lat'));lon=f(row.get('lon'));source=str(row.get('source','')).strip();role=norm(row.get('coordinate_role') or row.get('coord_status') or 'exact').replace(' ','_')
        errors=[]
        if country not in {'PL','DE'}:errors.append('country')
        if not name:errors.append('name')
        if catg is None:errors.append('category')
        if lat is None or lon is None:errors.append('coordinates')
        if lat is not None and not (45<=lat<=56 and 5<=lon<=25):errors.append('coordinate_range')
        if not source.startswith(('https://','http://')):errors.append('source')
        status='INVALID' if errors else None;match=None;reason=None;dm=None
        if not status:
            same=index.get((country,norm(name)),[])
            if same:
                ranked=[]
                for p in same:
                    plat=f(p.get('lat'));plon=f(p.get('lon'))
                    if plat is not None:ranked.append((dist(lat,lon,plat,plon),p))
                if ranked:
                    dm,match=min(ranked,key=lambda x:x[0]);status='EXISTS' if dm<=350 else 'POSSIBLE_DUPLICATE';reason='same_name'
                else:status='POSSIBLE_DUPLICATE';match=same[0];reason='same_name_no_coords'
        if not status:
            near=[]
            for p in places:
                if p.get('country')!=country:continue
                plat=f(p.get('lat'));plon=f(p.get('lon'))
                if plat is None:continue
                d=dist(lat,lon,plat,plon)
                if d<=80:near.append((d,p))
            if near:
                dm,match=min(near,key=lambda x:x[0]);status='POSSIBLE_DUPLICATE';reason='within_80m'
        sid=None
        if not status:
            sid='SP-'+str(uuid.uuid5(NS,f'{country}|{norm(name)}|{lat:.6f}|{lon:.6f}'))
            if sid in known_ids:status='POSSIBLE_DUPLICATE';reason='id_collision'
            elif role=='review':status='REVIEW';reason='coordinate_role_review'
            else:
                status='NEW';rec={'id':sid,'country':country,'name':name,'category':catg,'lat':lat,'lon':lon,'mapReady':True,'region':row.get('region',''),'area':row.get('area',''),'source':source,'coordinateRole':'representative_point_not_entrance' if role=='representative' else ('start_or_entrance' if role=='start' else ('osm_point' if source.startswith('https://www.openstreetmap.org/') else 'exact_point'))};new.append(rec);known_ids.add(sid);index.setdefault((country,norm(name)),[]).append(rec)
        results.append({'row':i,'status':status,'country':country,'name':name,'category':catg,'lat':lat,'lon':lon,'stable_id':sid,'errors':errors,'reason':reason,'distance_m':round(dm,1) if dm is not None else None,'match':{'id':match.get('id'),'name':match.get('name')} if match else None})
    out=dict(cat);out['places']=places+new;a.output.write_text(json.dumps(out,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
    counts=Counter(r['status'] for r in results);report={'summary':{'input':len(results),'existing':len(places),'new':len(new),'next_total':len(out['places']),'status_counts':dict(counts)},'results':results};a.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(' '.join(f'{k}={counts.get(k,0)}' for k in ['NEW','EXISTS','POSSIBLE_DUPLICATE','REVIEW','INVALID']))
    print(f'prepared={a.output} report={a.report}')
if __name__=='__main__':main()
