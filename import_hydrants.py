#!/usr/bin/env python3
"""Turn the consolidated hydrant sheet into data/hydrants.seed.json.

    python3 tools/import_hydrants.py "RTFD hydrants.csv"
    python3 tools/import_hydrants.py hydrants.xlsx --sheet "Consolidated"

Handles the two things that keep biting these exports:
  * ragged rows — layer exports where some rows carry title/notes columns and
    some don't. Rows are read by header name, not position, and short rows are
    padded instead of raising.
  * cp1252 mojibake — text that came through as Â , â€™, â€œ and friends.

Column names are matched loosely, so "Unit #", "unit_no" and "UNIT" all land in
the same field. Anything it can't map is reported, not silently dropped.
"""

import argparse, csv, json, re, sys, unicodedata
from pathlib import Path

FIELDS = {
    "id":     ["id", "hydrant_id", "hyd_id", "objectid", "fid", "key"],
    "unit":   ["unit", "unit_no", "unit_num", "unit_number", "hydrant_no", "number", "unit_#"],
    "street": ["street", "address", "location", "street_name", "addr"],
    "cross":  ["cross", "cross_street", "nearest_cross", "intersection", "notes_location"],
    "lat":    ["lat", "latitude", "y", "lat_dd"],
    "lon":    ["lon", "lng", "long", "longitude", "x", "lon_dd"],
    "box":    ["box", "dispatch_box", "box_no", "fire_box", "zone"],
    "size":   ["size", "main", "main_size", "diameter", "main_in"],
    "cls":    ["cls", "class", "flow_class", "nfpa", "nfpa_class", "color",
               "flow", "gpm", "flow_gpm", "test_gpm", "bonnet"],
    "status": ["status", "in_service", "condition", "state"],
    "notes":  ["notes", "note", "comment", "comments", "remarks"],
}

MOJIBAKE = {
    "\u00e2\u20ac\u2122": "'", "\u00e2\u20ac\u0153": '"', "\u00e2\u20ac\u009d": '"',
    "\u00e2\u20ac\u201c": "-", "\u00e2\u20ac\u201d": "-", "\u00c2\u00a0": " ",
    "\u00c2": "", "\u00e2\u20ac\u00a6": "...",
}

CLASS_BY_COLOR = {"blue": "AA", "green": "A", "orange": "B", "red": "C"}


def clean(s):
    if s is None:
        return ""
    s = str(s)
    for bad, good in MOJIBAKE.items():
        s = s.replace(bad, good)
    # last resort for text double-encoded on the way out of Sheets
    if any(ch in s for ch in ("Ã", "â", "Â")):
        try:
            s = s.encode("cp1252", "ignore").decode("utf-8", "ignore") or s
        except Exception:
            pass
    s = unicodedata.normalize("NFKC", s)
    return re.sub(r"\s+", " ", s).strip()


def norm_key(k):
    return re.sub(r"[^a-z0-9]+", "_", clean(k).lower()).strip("_")


def build_map(headers):
    lookup, unmapped = {}, []
    normed = {norm_key(h): h for h in headers if h}
    for field, aliases in FIELDS.items():
        for a in aliases:
            if a in normed:
                lookup[field] = normed[a]
                break
    for h in headers:
        if h and norm_key(h) not in {norm_key(v) for v in lookup.values()}:
            unmapped.append(h)
    return lookup, unmapped


def to_float(v):
    try:
        return float(str(v).strip().replace(",", ""))
    except Exception:
        return None


def flow_class(raw, gpm=None):
    v = clean(raw).lower()
    if v in ("aa", "a", "b", "c"):
        return v.upper()
    if v in CLASS_BY_COLOR:
        return CLASS_BY_COLOR[v]
    g = to_float(gpm if gpm is not None else raw)
    if g is None:
        return "X"
    if g >= 1500: return "AA"
    if g >= 1000: return "A"
    if g >= 500:  return "B"
    if g > 0:     return "C"
    return "X"


def read_rows(path, sheet):
    if path.suffix.lower() in (".xlsx", ".xlsm"):
        try:
            from openpyxl import load_workbook
        except ImportError:
            sys.exit("openpyxl needed for Excel input:  pip install openpyxl")
        wb = load_workbook(path, data_only=True)
        ws = wb[sheet] if sheet else wb.worksheets[0]
        data = list(ws.values)
        headers = [clean(h) for h in data[0]]
        width = len(headers)
        for r in data[1:]:
            r = list(r) + [None] * (width - len(r))      # pad ragged rows
            yield dict(zip(headers, r[:width]))
    else:
        with open(path, newline="", encoding="utf-8-sig", errors="replace") as f:
            rd = csv.DictReader(f)
            for r in rd:
                r.pop(None, None)                        # drop overflow columns
                yield r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source")
    ap.add_argument("--sheet", default=None)
    ap.add_argument("--out", default="data/hydrants.seed.json")
    ap.add_argument("--version", default="rtfd-572")
    args = ap.parse_args()

    src = Path(args.source)
    raw = list(read_rows(src, args.sheet))
    if not raw:
        sys.exit("No rows found.")

    colmap, unmapped = build_map(list(raw[0].keys()))
    for need in ("lat", "lon"):
        if need not in colmap:
            sys.exit(f"Could not find a '{need}' column. Columns seen: {list(raw[0].keys())}")

    out, skipped, n = [], 0, 0
    for row in raw:
        get = lambda f: row.get(colmap[f]) if f in colmap else None
        lat, lon = to_float(get("lat")), to_float(get("lon"))
        if lat is None or lon is None or not (-90 < lat < 90) or not (-180 < lon < 180):
            skipped += 1
            continue
        n += 1
        status = clean(get("status")).lower()
        out.append({
            "id":     clean(get("id")) or f"H-{n:04d}",
            "unit":   clean(get("unit")),
            "street": clean(get("street")),
            "cross":  clean(get("cross")),
            "lat":    round(lat, 6),
            "lon":    round(lon, 6),
            "box":    clean(get("box")),
            "size":   to_float(get("size")) or "",
            "cls":    flow_class(get("cls")),
            "status": "oos" if status in ("oos", "out of service", "no", "false", "0") else "ok",
            "notes":  clean(get("notes")),
            "updated": "",
        })

    dest = Path(args.out)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(
        {"version": args.version, "rows": out}, ensure_ascii=False, indent=1), encoding="utf-8")

    print(f"wrote {len(out)} hydrants to {dest}")
    if skipped:
        print(f"  {skipped} rows skipped for missing or bad coordinates")
    if unmapped:
        print(f"  columns not imported: {', '.join(unmapped)}")
    missing_unit = sum(1 for r in out if not r["unit"])
    if missing_unit:
        print(f"  {missing_unit} hydrants still have no unit number")


if __name__ == "__main__":
    main()
