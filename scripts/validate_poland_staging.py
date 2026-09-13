#!/usr/bin/env python3
"""Validate staged PL catalog updates without touching production files."""
import argparse,csv,json,math,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]

def load(p): return json.loads(pathlib.Path(p).read_text(encoding='utf-8'))

p=argparse.ArgumentParser()
p.add_argument('crosschecked',type=pathlib.Path)
p.add_argument('--working-next',type=pathlib.Path,required=True)
p.add_argument('--runtime-next',type=pathlib.Path,required=True)
a=p.parse_args()
rows=list(csv.DictReader(a.crosschecked.open(encoding='utf-8-sig')))
assert rows, 'No CROSS_CHECKED rows'
target={r['stable_id']:r for r in rows};assert len(target)==len(rows)
oldw=load(ROOT/'data/catalog_working.json');neww=load(a.working_next)
oldr=load(ROOT/'app/src/main/assets/ui/catalog.json');newr=load(a.runtime_next)
ow=oldw['records'];nw=neww['records'];orr=oldr['places'];nrr=newr['places']
assert len(ow)==len(nw) and len(orr)==len(nrr), 'Record count changed'
owi={r['stable_id']:r for r in ow};nwi={r['stable_id']:r for r in nw}
ori={r['id']:r for r in orr};nri={r['id']:r for r in nrr}
assert set(owi)==set(nwi) and set(ori)==set(nri), 'Stable ID set changed'
assert set(target)<=set(owi) and set(target)<=set(ori), 'Target missing from catalogs'
# Non-target records must be byte-for-byte equivalent as parsed JSON objects.
for sid in set(owi)-set(target): assert owi[sid]==nwi[sid], f'Unexpected working change: {sid}'
for sid in set(ori)-set(target): assert ori[sid]==nri[sid], f'Unexpected runtime change: {sid}'
for sid,row in target.items():
    w=nwi[sid];r=nri[sid]
    assert w['country']=='PL' and r['country']=='PL'
    assert w['record_kind']=='place' and w['map_ready'] is True and r['mapReady'] is True
    assert w['verification_status']=='cross_checked_osm_geonames'
    assert w.get('coordinate_review')
    assert w['coordinate_source']['url']==row['osm_url']==r['source']
    assert row['osm_url'].startswith('https://www.openstreetmap.org/')
    assert w['coordinate_source']['provider']=='Overpass / OpenStreetMap'
    lat=float(row['osm_latitude']);lon=float(row['osm_longitude'])
    assert math.isclose(w['latitude'],lat,abs_tol=1e-9) and math.isclose(w['longitude'],lon,abs_tol=1e-9)
    assert math.isclose(r['lat'],lat,abs_tol=1e-9) and math.isclose(r['lon'],lon,abs_tol=1e-9)
    assert 45<=lat<=56 and 5<=lon<=25
    assert r['category']==row['category']
    expected_role='osm_point' if row['osm_type']=='node' else 'representative_point_not_entrance'
    assert w['coordinate_role']==expected_role==r['coordinateRole']
old_working_ready=sum(bool(x.get('map_ready')) for x in ow);new_working_ready=sum(bool(x.get('map_ready')) for x in nw)
old_pl=sum(1 for x in orr if x.get('country')=='PL' and x.get('mapReady'));new_pl=sum(1 for x in nrr if x.get('country')=='PL' and x.get('mapReady'))
assert new_working_ready-old_working_ready==len(rows)
assert new_pl-old_pl==len(rows)
assert old_working_ready==1065, f'Unexpected working baseline {old_working_ready}'
assert old_pl==451, f'Unexpected PL runtime baseline {old_pl}'
print(json.dumps({'PASS':True,'applied':len(rows),'working_map_ready':f'{old_working_ready}->{new_working_ready}','runtime_pl_map_ready':f'{old_pl}->{new_pl}','ids_preserved':True,'non_targets_unchanged':True},ensure_ascii=False))
