#!/usr/bin/env python3
"""Controlled two-manifest PL+DE import for Summit Passport."""
from __future__ import annotations
import argparse, copy, datetime as dt, json, math, os, pathlib, re, shutil, tempfile, unicodedata
from collections import Counter, defaultdict

ROOT=pathlib.Path(__file__).resolve().parents[1]
CATALOG=ROOT/"app/src/main/assets/ui/catalog.json"
PL=ROOT/"data/import/poland_candidates.json"
DE=ROOT/"data/import/germany_candidates.json"
DRY_JSON=ROOT/"reports/PL_DE_IMPORT_DRY_RUN.json"
DRY_MD=ROOT/"reports/PL_DE_IMPORT_DRY_RUN.md"
FINAL_MD=ROOT/"reports/PL_DE_IMPORT_FINAL.md"
BACKUPS=ROOT/"backups/import"
COUNTRIES={"PL","DE"}
TYPES={"PEAK","PASS_SADDLE","WATER","WATERFALL","CAVE","ROCK_GEOLOGY","NATURE_VIEWPOINT","CASTLE_FORTRESS","HERITAGE_OBJECT","TRAIL_EXPERIENCE"}
TYPE_TO_RUNTIME={"PEAK":"peak","PASS_SADDLE":"pass","WATER":"water","WATERFALL":"waterfall","CAVE":"cave","ROCK_GEOLOGY":"rock","NATURE_VIEWPOINT":"nature","CASTLE_FORTRESS":"castle","HERITAGE_OBJECT":"heritage","TRAIL_EXPERIENCE":"trail"}
RUNTIME={"peak","pass","water","waterfall","cave","rock","nature","viewpoint","castle","heritage","trail","industrial","lighthouse"}
TYPE_WORDS=("punkt widokowy","wieza widokowa","platforma widokowa","aussichtspunkt","aussichtsplattform","viewpoint","wasserfall","waterfall","wodospad","hoehle","hohle","höhle","cave","jaskinia","gipfel","peak","szczyt","berg","mount","przelecz","sattel","pass","jezioro","lake","see","fels","felsen","rock","skala","skała","burg","schloss","castle","fortress","zamek","ruine","ruins","ruiny","trail","szlak","weg")
NEAR_M=80.0

def txt(v): return str(v or "").strip()
def num(v):
    try:
        if v is None or isinstance(v,bool) or txt(v)=="": return None
        return float(txt(v).replace(",","."))
    except (TypeError,ValueError): return None
def norm(v):
    s=txt(v).replace("ß","ss").replace("ł","l").replace("Ł","L")
    s=unicodedata.normalize("NFKD",s).casefold()
    s="".join(c for c in s if not unicodedata.combining(c))
    return " ".join(re.findall(r"[a-z0-9]+",s))
def base_norm(v):
    s=norm(v); words=sorted({norm(x) for x in TYPE_WORDS},key=len,reverse=True)
    changed=True
    while s and changed:
        changed=False
        for w in words:
            if s==w: return ""
            if s.startswith(w+" "): s=s[len(w):].strip(); changed=True; break
            if s.endswith(" "+w): s=s[:-len(w)].strip(); changed=True; break
    return s
def aliases(r):
    a=r.get("aliases") or []
    return [txt(x) for x in a if txt(x)] if isinstance(a,list) else []
def terms(r):
    out={norm(r.get("name")),base_norm(r.get("name"))}
    for a in aliases(r): out|={norm(a),base_norm(a)}
    return {x for x in out if x}
def rid(r): return txt(r.get("id") or r.get("stable_id") or r.get("place_id"))
def cid(r): return txt(r.get("stable_id") or r.get("place_id") or r.get("id"))
def hav(a,b):
    R=6371000.0;p1=math.radians(a[0]);p2=math.radians(b[0]);dp=math.radians(b[0]-a[0]);dl=math.radians(b[1]-a[1])
    x=math.sin(dp/2)**2+math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2*R*math.atan2(math.sqrt(x),math.sqrt(max(0,1-x)))
def read(path): return json.loads(path.read_text(encoding="utf-8-sig"))
def write(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def load_manifest(path,country):
    d=read(path)
    if isinstance(d,list): return {"country":country,"manifest_complete":None,"approval_status":"UNSPECIFIED"},d
    if not isinstance(d,dict): raise ValueError("manifest must be a JSON object or array: "+str(path))
    rows=d.get("candidates") or d.get("places") or d.get("records") or []
    if not isinstance(rows,list): raise ValueError("manifest candidates must be a list: "+str(path))
    return {k:v for k,v in d.items() if k not in {"candidates","places","records"}},rows
def validate(r,country):
    z=[];name=txt(r.get("name"));c=txt(r.get("country")).upper();t=txt(r.get("type")).upper();lat=num(r.get("lat"));lon=num(r.get("lon"))
    if not cid(r): z.append("MISSING_ID")
    if not name: z.append("MISSING_NAME")
    elif len(norm(name))<2 or norm(name) in {"unknown","tbd","todo","brak","n a","none","null"}: z.append("SUSPICIOUS_NAME")
    if c not in COUNTRIES or c!=country: z.append("INVALID_COUNTRY")
    if t not in TYPES: z.append("INVALID_TYPE")
    if not txt(r.get("region")): z.append("MISSING_REGION")
    if lat is None or lon is None: z.append("MISSING_COORDINATES")
    else:
        if not math.isfinite(lat) or not -90<=lat<=90: z.append("INVALID_LATITUDE")
        if not math.isfinite(lon) or not -180<=lon<=180: z.append("INVALID_LONGITUDE")
    if "must_see" not in r or not isinstance(r.get("must_see"),bool): z.append("INVALID_MUST_SEE")
    if "collections" not in r or not isinstance(r.get("collections"),list): z.append("INVALID_COLLECTIONS")
    if "aliases" not in r or not isinstance(r.get("aliases"),list): z.append("INVALID_ALIASES")
    if not txt(r.get("source_name")): z.append("MISSING_SOURCE_NAME")
    if not txt(r.get("source_url")) and not txt(r.get("source_note")): z.append("MISSING_SOURCE")
    rc=txt(r.get("runtime_category"))
    if rc and rc not in RUNTIME: z.append("INVALID_RUNTIME_CATEGORY")
    return z
def result(country,index,r): return {"index":index,"country":country,"stable_id":cid(r),"name":txt(r.get("name")),"status":None,"reasons":[],"match":None,"distance_m":None,"decision":r.get("decision") or r.get("status")}
def material_same(p,r):
    if txt(p.get("country")).upper()!=txt(r.get("country")).upper(): return False
    if not (terms(p)&terms(r)): return False
    a,b=num(p.get("lat")),num(p.get("lon"));c,d=num(r.get("lat")),num(r.get("lon"))
    if None in (a,b,c,d) or hav((c,d),(a,b))>1.0: return False
    rc=txt(r.get("runtime_category")) or TYPE_TO_RUNTIME.get(txt(r.get("type")).upper(),"")
    return not rc or rc==txt(p.get("category"))
def analyze(catalog,packages):
    places=catalog.get("places")
    if not isinstance(places,list): raise ValueError("MASTER has no places array")
    ids=[rid(p) for p in places]
    if len(ids)!=len(set(ids)): raise ValueError("MASTER contains duplicate IDs")
    byid={rid(p):p for p in places}; bycountry=defaultdict(list)
    for p in places: bycountry[txt(p.get("country")).upper()].append(p)
    rows=[];meta={};blockers=[]
    for country,path,m,items in packages:
        meta[country]={**m,"path":str(path),"candidate_count":len(items)}
        if m.get("manifest_complete") is not True or txt(m.get("approval_status")).upper()!="APPROVED_COMPLETE":
            blockers.append({"country":country,"reason":"MANIFEST_NOT_APPROVED_COMPLETE","approval_status":m.get("approval_status"),"manifest_complete":m.get("manifest_complete")})
        for i,r in enumerate(items,1): rows.append((country,i,r,result(country,i,r)))
    idcounts=Counter(cid(r) for _,_,r,_ in rows if cid(r))
    seen=[]
    for country,i,r,out in rows:
        bad=validate(r,country)
        if cid(r) and idcounts[cid(r)]>1: bad.append("DUPLICATE_ID_IN_MANIFEST")
        if bad:
            out["status"]="INVALID";out["reasons"]=sorted(set(bad));continue
        lat,lon=num(r.get("lat")),num(r.get("lon"))
        p=byid.get(cid(r))
        if p:
            same=material_same(p,r);out["status"]="DUPLICATE" if same else "CONFLICT";out["reasons"]=["DUPLICATE_ID" if same else "ID_CONFLICT"];out["match"]={"stable_id":rid(p),"name":p.get("name"),"scope":"MASTER"}
            a,b=num(p.get("lat")),num(p.get("lon"))
            if a is not None and b is not None: out["distance_m"]=round(hav((lat,lon),(a,b)),1)
            continue
        identity=terms(r);namehit=None
        for q in bycountry[country]:
            if identity&terms(q): namehit=q;break
        if namehit:
            a,b=num(namehit.get("lat")),num(namehit.get("lon"))
            dm=hav((lat,lon),(a,b)) if a is not None and b is not None else None
            if dm is not None and dm>5000:
                out["status"]="CONFLICT";out["reasons"]=["NAME_CONFLICT"]
            else:
                out["status"]="DUPLICATE";out["reasons"]=["DUPLICATE_NAME"]
            out["match"]={"stable_id":rid(namehit),"name":namehit.get("name"),"scope":"MASTER"}
            if dm is not None: out["distance_m"]=round(dm,1)
            continue
        internal=None
        for q in seen:
            if q["country"]==country and identity&q["_terms"]:
                internal=q;break
        if internal:
            dm=hav((lat,lon),(internal["lat"],internal["lon"]))
            out["status"]="DUPLICATE" if dm<=5000 else "CONFLICT";out["reasons"]=["DUPLICATE_ALIAS" if out["status"]=="DUPLICATE" else "NAME_CONFLICT"];out["match"]={"stable_id":internal["stable_id"],"name":internal["name"],"scope":"manifest"};out["distance_m"]=round(dm,1);continue
        near=[]
        for q in bycountry[country]:
            a,b=num(q.get("lat")),num(q.get("lon"))
            if a is None or b is None: continue
            dm=hav((lat,lon),(a,b))
            if dm<=NEAR_M: near.append((dm,q,"MASTER"))
        for q in seen:
            if q["country"]!=country: continue
            dm=hav((lat,lon),(q["lat"],q["lon"]))
            if dm<=NEAR_M: near.append((dm,q,"manifest"))
        if near:
            dm,q,scope=min(near,key=lambda x:x[0]);out["status"]="CONFLICT";out["reasons"]=["NEAR_COORDINATE_MATCH"];out["match"]={"stable_id":rid(q) if scope=="MASTER" else q["stable_id"],"name":q.get("name"),"scope":scope};out["distance_m"]=round(dm,1);continue
        out["status"]="ADD";seen.append({"stable_id":cid(r),"country":country,"name":txt(r.get("name")),"lat":lat,"lon":lon,"_terms":identity})
    res=[x[3] for x in rows];counts=Counter(x["status"] for x in res)
    cc={c:Counter(x["status"] for x in res if x["country"]==c) for c in ("PL","DE")}
    summary={"master_before":len(places),"candidates_PL":sum(x["country"]=="PL" for x in res),"candidates_DE":sum(x["country"]=="DE" for x in res),"ADD_PL":cc["PL"]["ADD"],"ADD_DE":cc["DE"]["ADD"],"DUPLICATE_PL":cc["PL"]["DUPLICATE"],"DUPLICATE_DE":cc["DE"]["DUPLICATE"],"CONFLICT":counts["CONFLICT"],"INVALID":counts["INVALID"],"global_blockers":len(blockers)}
    summary["apply_allowed"]=summary["CONFLICT"]==0 and summary["INVALID"]==0 and not blockers
    return {"summary":summary,"manifest_meta":meta,"blockers":blockers,"results":res}
def render(report):
    s=report["summary"];L=["# PL + DE mass import — dry run","",f"Generated: {dt.datetime.now(dt.timezone.utc).isoformat()}","","## Summary","","| Metric | Count |","|---|---:|",f"| MASTER before | {s['master_before']} |",f"| Candidates PL | {s['candidates_PL']} |",f"| Candidates DE | {s['candidates_DE']} |",f"| ADD PL | {s['ADD_PL']} |",f"| ADD DE | {s['ADD_DE']} |",f"| DUPLICATE PL | {s['DUPLICATE_PL']} |",f"| DUPLICATE DE | {s['DUPLICATE_DE']} |",f"| CONFLICT | {s['CONFLICT']} |",f"| INVALID | {s['INVALID']} |",f"| Global blockers | {s['global_blockers']} |","",f"Apply allowed: {'YES' if s['apply_allowed'] else 'NO'}","","## Global blockers",""]
    L += [f"- {b['country']}: {b['reason']} (approval_status={b.get('approval_status')!r}, manifest_complete={b.get('manifest_complete')!r})" for b in report["blockers"]] or ["- none"]
    L+=["","## Conflicts and invalid candidates",""]
    bad=[x for x in report["results"] if x["status"] in {"CONFLICT","INVALID"}]
    if not bad:L.append("- none")
    for x in bad:
        m=x.get("match") or {};extra=f"; match={m.get('stable_id')} {m.get('name')}" if m else "";dm=f"; distance={x['distance_m']} m" if x.get("distance_m") is not None else ""
        L.append(f"- {x['status']} {x['country']} {x['stable_id']} — {x['name']}: {', '.join(x['reasons'])}{extra}{dm}")
    return "\n".join(L)+"\n"
def runtime_record(r):
    return {"id":cid(r),"country":txt(r.get("country")).upper(),"name":txt(r.get("name")),"category":txt(r.get("runtime_category")) or TYPE_TO_RUNTIME[txt(r.get("type")).upper()],"lat":num(r.get("lat")),"lon":num(r.get("lon")),"mapReady":True,"region":txt(r.get("region")),"area":txt(r.get("area") or r.get("region")),"source":txt(r.get("source_url")) or None,"coordinateRole":txt(r.get("coordinate_role")) or "exact_point","mustSee":bool(r.get("must_see")),"aliases":aliases(r)}
def atomic(path,data):
    path.parent.mkdir(parents=True,exist_ok=True);payload=json.dumps(data,ensure_ascii=False,separators=(",",":"))+"\n";fd,tmp=tempfile.mkstemp(prefix=path.name+".",suffix=".tmp",dir=str(path.parent))
    try:
        with os.fdopen(fd,"w",encoding="utf-8") as h: h.write(payload);h.flush();os.fsync(h.fileno())
        os.replace(tmp,path)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)
def final_check(before,after,adds):
    b={rid(x):x for x in before["places"]};a={rid(x):x for x in after["places"]}
    if len(a)!=len(after["places"]): raise ValueError("final duplicate IDs")
    if not set(b)<=set(a): raise ValueError("existing record removed")
    for k,v in b.items():
        if a[k]!=v: raise ValueError("existing record changed: "+k)
    if not adds<=set(a): raise ValueError("added ID missing")
def main():
    p=argparse.ArgumentParser();p.add_argument("--poland",type=pathlib.Path,default=PL);p.add_argument("--germany",type=pathlib.Path,default=DE);p.add_argument("--catalog",type=pathlib.Path,default=CATALOG)
    g=p.add_mutually_exclusive_group(required=True);g.add_argument("--dry-run",action="store_true");g.add_argument("--apply",action="store_true")
    p.add_argument("--dry-report-json",type=pathlib.Path,default=DRY_JSON);p.add_argument("--dry-report-md",type=pathlib.Path,default=DRY_MD);p.add_argument("--final-report-md",type=pathlib.Path,default=FINAL_MD);p.add_argument("--backup-dir",type=pathlib.Path,default=BACKUPS);a=p.parse_args()
    master=read(a.catalog);pm,pr=load_manifest(a.poland,"PL");dm,dr=load_manifest(a.germany,"DE");packs=[("PL",a.poland,pm,pr),("DE",a.germany,dm,dr)]
    rep=analyze(master,packs);write(a.dry_report_json,rep);a.dry_report_md.parent.mkdir(parents=True,exist_ok=True);a.dry_report_md.write_text(render(rep),encoding="utf-8");print(json.dumps(rep["summary"],ensure_ascii=False))
    if a.dry_run:return 0 if rep["summary"]["apply_allowed"] else 2
    if not rep["summary"]["apply_allowed"]: print("APPLY BLOCKED: dry-run is not clean");return 3
    before=read(a.catalog);again=analyze(before,packs)
    if again["summary"]!=rep["summary"] or not again["summary"]["apply_allowed"]: print("APPLY BLOCKED: MASTER changed after validation");return 4
    rows={cid(x):x for x in pr+dr};adds={x["stable_id"] for x in rep["results"] if x["status"]=="ADD"};after=copy.deepcopy(before);after["places"] += [runtime_record(rows[k]) for k in sorted(adds)];final_check(before,after,adds)
    stamp=dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ");a.backup_dir.mkdir(parents=True,exist_ok=True);backup=a.backup_dir/("catalog."+stamp+".json");shutil.copy2(a.catalog,backup);atomic(a.catalog,after);final_check(before,read(a.catalog),adds)
    added=[rows[k] for k in sorted(adds)];must=[cid(x) for x in added if x.get("must_see")];s=rep["summary"];L=["# PL + DE mass import — final","",f"Generated: {dt.datetime.now(dt.timezone.utc).isoformat()}","",f"- MASTER before: {len(before['places'])}",f"- Added PL: {s['ADD_PL']}",f"- Added DE: {s['ADD_DE']}",f"- Skipped duplicates: {s['DUPLICATE_PL']+s['DUPLICATE_DE']}","- Resolved conflicts in apply run: 0",f"- MASTER after: {len(after['places'])}",f"- Backup: {backup}","- Final validation: PASS","","## New stable IDs",""]+[f"- {x}" for x in sorted(adds) or ["none"]]+["","## Must See among new records",""]+[f"- {x}" for x in must or ["none"]]
    a.final_report_md.parent.mkdir(parents=True,exist_ok=True);a.final_report_md.write_text("\n".join(L)+"\n",encoding="utf-8");print("APPLIED",len(adds));return 0
if __name__=="__main__": raise SystemExit(main())
