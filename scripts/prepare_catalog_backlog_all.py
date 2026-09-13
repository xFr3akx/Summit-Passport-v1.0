#!/usr/bin/env python3
"""
Prepare a full PL+DE backlog package for Summit Passport.

The script never overwrites production catalog files. It audits every unresolved
place in Poland and Germany, uses existing GeoNames candidates when available,
falls back to live Photon/OSM lookup, performs strict country/category/name and
duplicate checks, and writes a staging catalog that can be reviewed/replaced
quickly.

Statuses:
  READY             safe staging update with OSM source
  POSSIBLE_DUPLICATE candidate resolves to an already mapped or batch identity
  REVIEW            no unambiguous safe identity
"""
import argparse
import collections
import csv
import datetime
import difflib
import json
import math
import pathlib
import re
import time
import unicodedata
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
PHOTON = "https://photon.komoot.io/api/"
OVERPASS_ENDPOINTS = (
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass.nchc.org.tw/api/interpreter",
)
COUNTRY = {
    "PL": {"query": "Polska", "lang": "pl"},
    "DE": {"query": "Deutschland", "lang": "de"},
}
ALLOWED_CATEGORIES = {
    "peak", "pass", "water", "waterfall", "cave", "rock", "nature",
    "viewpoint", "heritage", "lighthouse", "castle", "industrial",
}

def norm(value):
    s = str(value or "").replace("ß", "ss").replace("ł", "l")
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "", s)

def words(value):
    s = str(value or "")
    s = re.sub(r"\bUNESCO\b", " ", s, flags=re.I)
    raw = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    toks = re.findall(r"[a-z0-9]+", raw)
    stop = {"w","we","na","nad","pod","i","im","der","die","das","am","an","im","in","zu","zum","zur"}
    return [x for x in toks if x not in stop]

def name_score(a, b):
    na, nb = norm(a), norm(b)
    if not na or not nb:
        return 0.0
    if na == nb:
        return 1.0
    if min(len(na), len(nb)) >= 7 and (na in nb or nb in na):
        return 0.92
    wa, wb = set(words(a)), set(words(b))
    jac = len(wa & wb) / max(1, len(wa | wb))
    seq = difflib.SequenceMatcher(None, " ".join(words(a)), " ".join(words(b))).ratio()
    return max(jac, seq)

def distance_m(a, b):
    lat1, lon1 = a
    lat2, lon2 = b
    x = math.radians(lon2-lon1) * math.cos(math.radians((lat1+lat2)/2))
    y = math.radians(lat2-lat1)
    return 6371000 * math.hypot(x, y)

def ring_contains(x, y, ring):
    inside = False
    for aa, bb in zip(ring, ring[1:] + ring[:1]):
        if (aa[1] > y) != (bb[1] > y):
            cross = (bb[0]-aa[0]) * (y-aa[1]) / (bb[1]-aa[1]) + aa[0]
            if x < cross:
                inside = not inside
    return inside

def make_inside(boundaries, code):
    geom = boundaries[code]
    polys = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
    return lambda lat, lon: any(
        ring_contains(lon, lat, p[0]) and not any(ring_contains(lon, lat, h) for h in p[1:])
        for p in polys
    )

def fits_kv(category, key, value, tags=None):
    tags = tags or {}
    key = str(key or "")
    value = str(value or "")
    natural = tags.get("natural") or (value if key == "natural" else "")
    historic = tags.get("historic") or (value if key == "historic" else "")
    tourism = tags.get("tourism") or (value if key == "tourism" else "")
    if category == "peak":
        return (key == "natural" and value == "peak") or natural == "peak"
    if category == "pass":
        return (key == "natural" and value == "saddle") or natural == "saddle" or tags.get("mountain_pass") == "yes"
    if category == "water":
        return (
            (key == "natural" and value == "water") or natural == "water"
            or (key == "water" and value in {"lake","reservoir","pond"})
            or tags.get("water") in {"lake","reservoir","pond"}
            or (key == "landuse" and value == "reservoir") or tags.get("landuse") == "reservoir"
        )
    if category == "waterfall":
        return natural == "waterfall" or (key == "waterway" and value == "waterfall") or tags.get("waterway") == "waterfall"
    if category == "cave":
        return natural == "cave_entrance"
    if category == "rock":
        return natural in {"rock","stone","cliff"} or (key == "geological" and value == "geological_site") or tags.get("geological") == "geological_site"
    if category == "nature":
        return (
            (key == "boundary" and value in {"protected_area","national_park"})
            or tags.get("boundary") in {"protected_area","national_park"}
            or (key == "leisure" and value in {"nature_reserve","park"})
            or tags.get("leisure") in {"nature_reserve","park"}
            or natural in {"wood","heath","wetland","valley","scrub"}
        )
    if category == "viewpoint":
        return tourism == "viewpoint"
    if category == "heritage":
        return tourism in {"museum","attraction"} or bool(historic) or key == "heritage" or bool(tags.get("heritage"))
    if category == "lighthouse":
        return (key == "man_made" and value == "lighthouse") or tags.get("man_made") == "lighthouse" or historic == "lighthouse"
    if category == "castle":
        return historic in {"castle","fort","ruins","manor"} or key == "castle_type" or bool(tags.get("castle_type"))
    if category == "industrial":
        return (
            (key == "man_made" and value in {"works","mine","adit","mineshaft","chimney","kiln"})
            or tags.get("man_made") in {"works","mine","adit","mineshaft","chimney","kiln"}
            or (key == "industrial") or tags.get("industrial") is not None
            or (tourism == "museum" and tags.get("museum") in {"technology","industrial"})
        )
    return False

def osm_url(osm_type, osm_id):
    kind = {"N":"node","W":"way","R":"relation","node":"node","way":"way","relation":"relation"}.get(str(osm_type))
    return f"https://www.openstreetmap.org/{kind}/{osm_id}" if kind and str(osm_id or "") else None

def request_json(url, data=None, timeout=35, attempts=3):
    last = None
    for n in range(attempts):
        try:
            req = urllib.request.Request(
                url,
                data=data,
                headers={"User-Agent":"SummitPassportCatalogAudit/2.0 (GitHub Actions; catalog preparation)"},
            )
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.load(resp)
        except Exception as e:
            last = e
            time.sleep(min(4.0, 0.8 * (2**n)))
    raise last

def photon_query(name, country, limit=12):
    cfg = COUNTRY[country]
    params = {"q": f"{name}, {cfg['query']}", "limit": limit, "lang": cfg["lang"]}
    return request_json(PHOTON + "?" + urllib.parse.urlencode(params), timeout=30, attempts=3)

def photon_candidates(name, country, category):
    raw = photon_query(name, country)
    out = []
    for feature in raw.get("features", []):
        prop = feature.get("properties") or {}
        coords = (feature.get("geometry") or {}).get("coordinates") or []
        if len(coords) < 2 or str(prop.get("countrycode") or "").upper() != country:
            continue
        pname = prop.get("name") or ""
        score = name_score(name, pname)
        if score < 0.78:
            continue
        if not fits_kv(category, prop.get("osm_key"), prop.get("osm_value"), prop):
            continue
        otype, oid = prop.get("osm_type"), prop.get("osm_id")
        url = osm_url(otype, oid)
        if not url:
            continue
        out.append({
            "name": pname,
            "lat": float(coords[1]),
            "lon": float(coords[0]),
            "osm_type": {"N":"node","W":"way","R":"relation"}.get(str(otype), str(otype)),
            "osm_id": oid,
            "osm_key": prop.get("osm_key"),
            "osm_value": prop.get("osm_value"),
            "state": prop.get("state"),
            "county": prop.get("county"),
            "city": prop.get("city"),
            "name_score": round(score, 3),
            "source": url,
        })
    uniq = {}
    for x in out:
        uniq[(x["osm_type"], str(x["osm_id"]))] = x
    return list(uniq.values())

def overpass_geonames(name, category, lat, lon, radius=500):
    q = f'[out:json][timeout:35];nwr(around:{radius},{lat:.7f},{lon:.7f})["name"];out center tags;'
    payload = urllib.parse.urlencode({"data": q}).encode()
    raw = None
    used = None
    last = None
    for endpoint in OVERPASS_ENDPOINTS:
        try:
            raw = request_json(endpoint, data=payload, timeout=50, attempts=2)
            used = endpoint
            break
        except Exception as e:
            last = e
    if raw is None:
        raise last
    matches = []
    for e in raw.get("elements", []):
        tags = e.get("tags") or {}
        names = []
        for key in ("name","name:pl","name:de","official_name","alt_name","short_name"):
            if tags.get(key):
                names.extend(str(tags[key]).split(";"))
        if not names or max(name_score(name, x) for x in names) < 0.86:
            continue
        if not fits_kv(category, None, None, tags):
            continue
        kind = e.get("type")
        oid = e.get("id")
        url = osm_url(kind, oid)
        centre = e.get("center") or {}
        pt = None
        if "lat" in e and "lon" in e:
            pt = (float(e["lat"]), float(e["lon"]))
        elif "lat" in centre and "lon" in centre:
            pt = (float(centre["lat"]), float(centre["lon"]))
        matches.append({
            "name": tags.get("name") or names[0],
            "lat": pt[0] if pt else lat,
            "lon": pt[1] if pt else lon,
            "osm_type": kind,
            "osm_id": oid,
            "osm_key": None,
            "osm_value": None,
            "state": None,
            "county": None,
            "city": None,
            "name_score": round(max(name_score(name, x) for x in names), 3),
            "source": url,
            "overpass_endpoint": used,
            "search_radius_m": radius,
            "proximity_basis": "candidate_specific_overpass_around_geometry",
        })
    uniq = {}
    for x in matches:
        uniq[(x["osm_type"], str(x["osm_id"]))] = x
    return list(uniq.values())

def write_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def safe_float(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None

parser = argparse.ArgumentParser()
parser.add_argument("--output-dir", type=pathlib.Path, default=ROOT/"data/full_backlog")
parser.add_argument("--photon-delay", type=float, default=0.45)
parser.add_argument("--overpass-delay", type=float, default=0.20)
parser.add_argument("--no-live", action="store_true")
args = parser.parse_args()

working = json.loads((ROOT/"data/catalog_working.json").read_text(encoding="utf-8"))
runtime = json.loads((ROOT/"app/src/main/assets/ui/catalog.json").read_text(encoding="utf-8"))
boundaries = json.loads((ROOT/"app/src/main/assets/ui/boundaries.json").read_text(encoding="utf-8"))
wrecords = working["records"]
rplaces = runtime["places"]
widx = {r["stable_id"]: r for r in wrecords if r.get("stable_id")}
ridx = {r["id"]: r for r in rplaces if r.get("id")}
assert len(ridx) == len(rplaces), "Runtime IDs are not unique"

inside = {code: make_inside(boundaries, code) for code in COUNTRY}

backlog = [
    r for r in wrecords
    if r.get("country") in COUNTRY and r.get("record_kind") == "place" and not r.get("map_ready")
]
missing_runtime = [r.get("stable_id") for r in backlog if r.get("stable_id") not in ridx]
assert not missing_runtime, f"Backlog IDs missing from runtime: {missing_runtime[:10]}"
backlog.sort(key=lambda r: (r.get("country",""), str((r.get("source_regions") or [""])[0]), r.get("name",""), r.get("stable_id","")))

existing = {code: [] for code in COUNTRY}
existing_osm = {}
for r in wrecords:
    code = r.get("country")
    if code not in COUNTRY or r.get("record_kind") != "place" or not r.get("map_ready"):
        continue
    lat, lon = safe_float(r.get("latitude")), safe_float(r.get("longitude"))
    if lat is None or lon is None:
        continue
    sid = r.get("stable_id")
    rp = ridx.get(sid) or {}
    rec = {
        "stable_id": sid, "name": r.get("name",""), "category": rp.get("category") or r.get("category") or "",
        "lat": lat, "lon": lon, "source": rp.get("source") or ((r.get("coordinate_source") or {}).get("url")),
    }
    existing[code].append(rec)
    source = str(rec["source"] or "")
    if source.startswith("https://www.openstreetmap.org/"):
        existing_osm[source] = rec

results = []
for n, r in enumerate(backlog, 1):
    sid = r["stable_id"]
    rp = ridx[sid]
    country = r["country"]
    name = r.get("name") or rp.get("name") or ""
    category = rp.get("category") or r.get("category") or ""
    source_region = str((r.get("source_regions") or [""])[0])
    source_ids = list(r.get("source_ids") or [])
    reasons = []
    candidates = []
    candidate_origin = None
    query_error = None

    if category not in ALLOWED_CATEGORIES:
        reasons.append("unsupported_runtime_category:" + str(category))

    cc = r.get("coordinate_candidate") or {}
    cc_lat, cc_lon = safe_float(cc.get("latitude")), safe_float(cc.get("longitude"))
    cc_country = str(cc.get("country") or country)
    if not reasons and cc_lat is not None and cc_lon is not None and cc_country == country:
        candidate_origin = "geonames"
        try:
            candidates = overpass_geonames(name, category, cc_lat, cc_lon, radius=500)
        except Exception as e:
            query_error = "overpass:" + type(e).__name__
        time.sleep(args.overpass_delay)

    if not reasons and not candidates and not args.no_live:
        candidate_origin = "photon_osm"
        try:
            candidates = photon_candidates(name, country, category)
        except Exception as e:
            query_error = "photon:" + type(e).__name__
        time.sleep(args.photon_delay)

    identities = {(c["osm_type"], str(c["osm_id"])) for c in candidates}
    chosen = candidates[0] if len(identities) == 1 else None
    status = "REVIEW"
    duplicate_of = None

    if reasons:
        pass
    elif len(identities) == 0:
        reasons.append(query_error or "no_unambiguous_osm_identity")
    elif len(identities) > 1:
        reasons.append(f"multiple_osm_identities:{len(identities)}")
    else:
        lat, lon = chosen["lat"], chosen["lon"]
        if not inside[country](lat, lon):
            reasons.append("outside_country_boundary")
        if chosen.get("name_score", 0) < (0.86 if candidate_origin == "geonames" else 0.78):
            reasons.append("weak_name_match")
        source = chosen["source"]
        if source in existing_osm:
            status = "POSSIBLE_DUPLICATE"
            duplicate_of = existing_osm[source]["stable_id"]
            reasons.append("same_osm_identity_as_existing")
        else:
            same_name = [
                e for e in existing[country]
                if norm(e["name"]) == norm(name) and distance_m((lat,lon),(e["lat"],e["lon"])) < 15000
            ]
            if same_name:
                status = "POSSIBLE_DUPLICATE"
                duplicate_of = same_name[0]["stable_id"]
                reasons.append("same_name_near_existing")
            else:
                near = [
                    e for e in existing[country]
                    if e["category"] == category and distance_m((lat,lon),(e["lat"],e["lon"])) < 75
                ]
                if near:
                    status = "POSSIBLE_DUPLICATE"
                    duplicate_of = near[0]["stable_id"]
                    reasons.append("same_category_within_75m_existing")
                elif not reasons:
                    status = "READY"

    results.append({
        "stable_id": sid,
        "country": country,
        "name": name,
        "category": category,
        "source_region": source_region,
        "source_ids": source_ids,
        "status": status,
        "reasons": reasons,
        "duplicate_of": duplicate_of,
        "candidate_origin": candidate_origin,
        "coordinate_candidate": {
            "latitude": cc_lat, "longitude": cc_lon,
            "geonames_id": cc.get("geonames_id"),
            "feature_code": cc.get("feature_code"),
        } if cc_lat is not None and cc_lon is not None else None,
        "candidates": candidates,
        "chosen": chosen,
    })
    print(f"{n:03d}/{len(backlog)} {country} {status} {name} :: {', '.join(reasons) if reasons else candidate_origin}")

by_osm = collections.defaultdict(list)
by_name = collections.defaultdict(list)
for x in results:
    c = x.get("chosen")
    if c and x["status"] == "READY":
        by_osm[(x["country"], c["osm_type"], str(c["osm_id"]))].append(x)
        by_name[(x["country"], norm(x["name"]))].append(x)

def rank_primary(x):
    return (-len(x.get("source_ids") or []), x["stable_id"])

for group in list(by_osm.values()) + [g for g in by_name.values() if len(g) > 1]:
    if len(group) < 2:
        continue
    primary = sorted(group, key=rank_primary)[0]
    for x in group:
        if x is primary or x["status"] != "READY":
            continue
        x["status"] = "POSSIBLE_DUPLICATE"
        x["duplicate_of"] = primary["stable_id"]
        x["reasons"] = sorted(set(x["reasons"] + ["batch_duplicate_identity_or_name"]))

ready_now = [x for x in results if x["status"] == "READY" and x.get("chosen")]
for i, x in enumerate(ready_now):
    if x["status"] != "READY":
        continue
    cx = x["chosen"]
    for y in ready_now[i+1:]:
        if y["status"] != "READY" or x["country"] != y["country"] or x["category"] != y["category"]:
            continue
        cy = y["chosen"]
        if distance_m((cx["lat"],cx["lon"]),(cy["lat"],cy["lon"])) < 50:
            primary, other = sorted([x,y], key=rank_primary)
            other["status"] = "POSSIBLE_DUPLICATE"
            other["duplicate_of"] = primary["stable_id"]
            other["reasons"] = sorted(set(other["reasons"] + ["batch_same_category_within_50m"]))

today = datetime.date.today().isoformat()
changes = []
ready_rows = []
review_rows = []
for x in results:
    sid = x["stable_id"]
    if x["status"] == "READY":
        c = x["chosen"]
        w = widx[sid]
        rp = ridx[sid]
        assert not w.get("map_ready") and not rp.get("mapReady"), f"Target already ready: {sid}"
        assert norm(w.get("name")) == norm(rp.get("name")) == norm(x["name"]), f"Name mismatch: {sid}"
        assert rp.get("category") == x["category"], f"Category mismatch: {sid}"
        lat, lon = float(c["lat"]), float(c["lon"])
        source = c["source"]
        role = "osm_point" if c["osm_type"] == "node" else "representative_point_not_entrance"
        verification = "cross_checked_osm_geonames" if x["candidate_origin"] == "geonames" else "verified_osm_photon"
        w["latitude"] = lat
        w["longitude"] = lon
        w["map_ready"] = True
        w["verification_status"] = verification
        w["coordinate_role"] = role
        w["coordinate_source"] = {
            "url": source,
            "provider": "OpenStreetMap" if x["candidate_origin"] == "photon_osm" else "Overpass / OpenStreetMap + GeoNames candidate",
            "retrieved_on": today,
            "method": (
                "Unique country/category/name-compatible OSM identity returned by Photon."
                if x["candidate_origin"] == "photon_osm"
                else "Unique country/category/name-compatible OSM identity within 500 m of existing GeoNames coordinate candidate."
            ),
        }
        w["coordinate_review"] = "Automated full PL+DE backlog audit; not field surveyed."
        rp["lat"] = lat
        rp["lon"] = lon
        rp["mapReady"] = True
        rp["source"] = source
        rp["coordinateRole"] = role
        row = {
            "stable_id": sid, "country": x["country"], "name": x["name"], "category": x["category"],
            "latitude": lat, "longitude": lon, "osm_url": source, "osm_type": c["osm_type"], "osm_id": c["osm_id"],
            "verification_status": verification, "candidate_origin": x["candidate_origin"],
        }
        ready_rows.append(row)
        changes.append(row)
    else:
        review_rows.append({
            "stable_id": sid, "country": x["country"], "name": x["name"], "category": x["category"],
            "status": x["status"], "duplicate_of": x.get("duplicate_of") or "",
            "reasons": " | ".join(x.get("reasons") or []),
        })

out = args.output_dir
out.mkdir(parents=True, exist_ok=True)
write_json(out/"all_results.json", results)
write_json(out/"catalog_working_next.json", working)
write_json(out/"catalog_main_candidate.json", runtime)
write_json(out/"ready_patch.json", changes)

ready_fields = ["stable_id","country","name","category","latitude","longitude","osm_url","osm_type","osm_id","verification_status","candidate_origin"]
with (out/"ready_to_import.csv").open("w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=ready_fields)
    w.writeheader()
    w.writerows(ready_rows)
review_fields = ["stable_id","country","name","category","status","duplicate_of","reasons"]
with (out/"needs_review.csv").open("w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=review_fields)
    w.writeheader()
    w.writerows(review_rows)

status_counts = collections.Counter(x["status"] for x in results)
country_status = {
    code: dict(collections.Counter(x["status"] for x in results if x["country"] == code))
    for code in COUNTRY
}
after = {
    code: sum(1 for p in rplaces if p.get("country") == code and p.get("mapReady"))
    for code in COUNTRY
}
before = {code: after[code] - sum(1 for x in ready_rows if x["country"] == code) for code in COUNTRY}
summary = {
    "generated_on": today,
    "backlog_total": len(backlog),
    "backlog_by_country": dict(collections.Counter(r["country"] for r in backlog)),
    "status_counts": dict(status_counts),
    "country_status": country_status,
    "map_ready_before": before,
    "map_ready_after_staging": after,
    "ready_to_import": len(ready_rows),
    "possible_duplicates": status_counts.get("POSSIBLE_DUPLICATE", 0),
    "needs_review": status_counts.get("REVIEW", 0),
    "stable_ids_preserved": True,
    "production_catalog_overwritten": False,
}
write_json(out/"summary.json", summary)
print("FINAL_SUMMARY " + json.dumps(summary, ensure_ascii=False))
