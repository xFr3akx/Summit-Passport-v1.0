#!/usr/bin/env python3
import copy,json,pathlib,subprocess,tempfile
ROOT=pathlib.Path(__file__).resolve().parents[1]
SCRIPT=ROOT/"scripts/import_places.py"
def write(p,o): p.write_text(json.dumps(o,ensure_ascii=False),encoding="utf-8")
def candidate(**kw):
    r={"stable_id":"SP-new","name":"Nowa Skała","country":"PL","region":"Małopolskie","type":"ROCK_GEOLOGY","runtime_category":"rock","lat":50.2,"lon":19.2,"must_see":False,"collections":["PL-rock"],"aliases":[],"source_name":"test","source_url":"https://example.test/place","decision":"APPROVED"}
    r.update(kw);return r
def manifest(c,rows,complete=True): return {"country":c,"manifest_complete":complete,"approval_status":"APPROVED_COMPLETE" if complete else "INCOMPLETE_REVIEW","candidates":rows}
def run(td,*mode):
    cmd=["python3",str(SCRIPT),"--catalog",str(td/"catalog.json"),"--poland",str(td/"pl.json"),"--germany",str(td/"de.json"),"--dry-report-json",str(td/"dry.json"),"--dry-report-md",str(td/"dry.md"),"--final-report-md",str(td/"final.md"),"--backup-dir",str(td/"backup"),*mode]
    return subprocess.run(cmd,text=True,capture_output=True)
def main():
    with tempfile.TemporaryDirectory() as raw:
        td=pathlib.Path(raw)
        old={"id":"SP-old","country":"PL","name":"Testowa Góra","category":"peak","lat":50.0,"lon":19.0,"mapReady":True,"region":"Małopolskie","area":"Test","source":"https://example.test/old","coordinateRole":"exact_point"}
        master={"version":"test","places":[old],"attribution":{}}
        write(td/"catalog.json",master)
        dup=candidate(stable_id="SP-dup",name="Szczyt Testowa Góra",type="PEAK",runtime_category="peak",lat=50.01,lon=19.01,aliases=["Testowa Góra"])
        near=candidate(stable_id="SP-near",name="Inny punkt",lat=50.0002,lon=19.0002)
        bad=candidate(stable_id="SP-bad",name="?",lat=None,lon=None)
        write(td/"pl.json",manifest("PL",[dup,near,bad],False));write(td/"de.json",manifest("DE",[],False))
        before=(td/"catalog.json").read_bytes();p=run(td,"--dry-run");assert p.returncode==2,p.stdout+p.stderr;assert (td/"catalog.json").read_bytes()==before
        rep=json.loads((td/"dry.json").read_text());by={x["stable_id"]:x for x in rep["results"]}
        assert by["SP-dup"]["status"]=="DUPLICATE"
        assert by["SP-near"]["status"]=="CONFLICT" and "NEAR_COORDINATE_MATCH" in by["SP-near"]["reasons"]
        assert by["SP-bad"]["status"]=="INVALID" and rep["summary"]["apply_allowed"] is False
        add=candidate(stable_id="SP-add",name="Nowa Skała")
        exact=candidate(stable_id="SP-old",name="Testowa Góra",type="PEAK",runtime_category="peak",lat=50.0,lon=19.0,region="Małopolskie",source_url="https://example.test/old")
        write(td/"pl.json",manifest("PL",[add,exact]));write(td/"de.json",manifest("DE",[]))
        p=run(td,"--apply");assert p.returncode==0,p.stdout+p.stderr
        after=json.loads((td/"catalog.json").read_text());assert len(after["places"])==2 and after["places"][0]==old
        assert next(x for x in after["places"] if x["id"]=="SP-add")["category"]=="rock"
        backups=list((td/"backup").glob("catalog.*.json"));assert len(backups)==1 and json.loads(backups[0].read_text())==master
        assert "Final validation: PASS" in (td/"final.md").read_text()
        write(td/"catalog.json",master);conf=copy.deepcopy(exact);conf["lat"]=50.1
        write(td/"pl.json",manifest("PL",[conf]));write(td/"de.json",manifest("DE",[]));before=(td/"catalog.json").read_bytes();p=run(td,"--apply");assert p.returncode==3 and (td/"catalog.json").read_bytes()==before
        rr=json.loads((td/"dry.json").read_text());assert rr["results"][0]["status"]=="CONFLICT" and rr["results"][0]["reasons"]==["ID_CONFLICT"]
    print("PASS: controlled PL+DE mass importer")
if __name__=="__main__": main()
