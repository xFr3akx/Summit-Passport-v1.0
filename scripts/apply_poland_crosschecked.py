#!/usr/bin/env python3
"""Apply cross-checked PL coordinates to staging copies of working/runtime catalogs.

This script NEVER overwrites production inputs. It preserves stable IDs and record counts,
and fails if a target is already map-ready, missing, or has a category/name mismatch.
"""
import argparse,csv,datetime,json,pathlib,re,unicodedata
ROOT=pathlib.Path(__file__).resolve().parents[1]

def norm(v):
    s=unicodedata.normalize('NFKD',str(v or '')).encode('ascii','ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+','',s)

def write(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

p=argparse.ArgumentParser()
p.add_argument('crosschecked',type=pathlib.Path)
p.add_argument('--working-output',type=pathlib.Path,required=True)
p.add_argument('--runtime-output',type=pathlib.Path,required=True)
p.add_argument('--summary-output',type=pathlib.Path,required=True)
a=p.parse_args()
rows=list(csv.DictReader(a.crosschecked.open(encoding='utf-8-sig')))
assert rows, 'No cross-checked rows to apply'
ids=[r['stable_id'] for r in rows];assert len(ids)==len(set(ids)), 'Duplicate stable_id in cross-checked input'
working=json.loads((ROOT/'data/catalog_working.json').read_text(encoding='utf-8'))
runtime=json.loads((ROOT/'app/src/main/assets/ui/catalog.json').read_text(encoding='utf-8'))
wrecords=working['records'];rplaces=runtime['places']
widx={r['stable_id']:r for r in wrecords};ridx={r['id']:r for r in rplaces}
assert len(widx)==len(wrecords);assert len(ridx)==len(rplaces)
missing_working=[i for i in ids if i not in widx];missing_runtime=[i for i in ids if i not in ridx]
assert not missing_working, f'Missing working IDs: {missing_working}'
assert not missing_runtime, f'Missing runtime IDs: {missing_runtime}'
old_working_ready=sum(bool(r.get('map_ready')) for r in wrecords)
old_runtime_pl=sum(1 for r in rplaces if r.get('country')=='PL' and r.get('mapReady'))
changes=[];today=datetime.date.today().isoformat()
for row in rows:
    sid=row['stable_id'];w=widx[sid];r=ridx[sid]
    assert w.get('country')=='PL' and r.get('country')=='PL'
    assert w.get('record_kind')=='place'
    assert not w.get('map_ready'), f'Working record already map-ready: {sid}'
    assert not r.get('mapReady'), f'Runtime record already map-ready: {sid}'
    assert norm(w.get('name'))==norm(row['name'])==norm(r.get('name')), f'Name mismatch: {sid}'
    assert r.get('category')==row['category'], f'Runtime category mismatch {sid}: {r.get("category")} != {row["category"]}'
    url=row['osm_url'];assert url.startswith('https://www.openstreetmap.org/')
    lat=float(row['osm_latitude']);lon=float(row['osm_longitude'])
    assert 45<=lat<=56 and 5<=lon<=25
    radius=int(float(row.get('search_radius_m') or 500));assert radius<=500
    basis=row.get('proximity_basis') or 'legacy_centre_distance'
    centre_distance=float(row['centre_distance_m']) if row.get('centre_distance_m') not in (None,'') else None
    if row['osm_type']=='node':
        assert centre_distance is not None and centre_distance<=radius, f'Node outside search radius: {sid}'
    else:
        assert basis=='candidate_specific_overpass_around_geometry', f'Large feature lacks geometry-based proximity proof: {sid}'
    role='osm_point' if row['osm_type']=='node' else 'representative_point_not_entrance'
    w['latitude']=lat;w['longitude']=lon;w['map_ready']=True
    w['verification_status']='cross_checked_osm_geonames';w['coordinate_role']=role
    w['coordinate_source']={
        'url':url,
        'provider':'Overpass / OpenStreetMap',
        'retrieved_on':today,
        'method':f'Exact/alias normalized name and compatible OSM category; candidate-specific Overpass around query with radius {radius} m from an existing GeoNames coordinate candidate; not field surveyed.'
    }
    detail=f'centre distance {centre_distance:.1f} m' if centre_distance is not None else 'centre distance unavailable'
    w['coordinate_review']=f'Automated OSM/GeoNames cross-check; geometry returned inside {radius} m candidate search radius; {detail}; source {row.get("source_id") or "GeoNames candidate"}.'
    if not w.get('category'):w['category']=row['category']
    r['lat']=lat;r['lon']=lon;r['mapReady']=True;r['source']=url;r['coordinateRole']=role
    changes.append({'stable_id':sid,'name':r['name'],'category':r['category'],'lat':lat,'lon':lon,'source':url,'osm_type':row['osm_type'],'centre_distance_m':centre_distance,'search_radius_m':radius})
assert len(wrecords)==len(widx) and len(rplaces)==len(ridx)
new_working_ready=sum(bool(r.get('map_ready')) for r in wrecords)
new_runtime_pl=sum(1 for r in rplaces if r.get('country')=='PL' and r.get('mapReady'))
assert new_working_ready==old_working_ready+len(rows)
assert new_runtime_pl==old_runtime_pl+len(rows)
assert {r['stable_id'] for r in wrecords}==set(widx);assert {r['id'] for r in rplaces}==set(ridx)
summary={'applied':len(rows),'stable_ids_preserved':True,'record_counts_preserved':True,'working_map_ready_before':old_working_ready,'working_map_ready_after':new_working_ready,'runtime_pl_map_ready_before':old_runtime_pl,'runtime_pl_map_ready_after':new_runtime_pl,'changes':changes}
write(a.working_output,working);write(a.runtime_output,runtime);write(a.summary_output,summary)
print(json.dumps({k:v for k,v in summary.items() if k!='changes'},ensure_ascii=False))
for x in changes:print('APPLY',x['stable_id'],x['name'],x['category'],x['source'])
