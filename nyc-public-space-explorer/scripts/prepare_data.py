"""
prepare_data.py
Clean the raw NYC Parks Properties export into a tidy, point-based GeoJSON
that the web map can load, and write a matching data dictionary.

Input:  data/parks_raw.json        (raw pull from NYC Open Data, dataset enfh-gkve)
Output: data/public_spaces.geojson (cleaned points, one per public space)
        data/data_dictionary.md    (field descriptions + provenance)

Run:    python scripts/prepare_data.py
"""

import json
import os
from collections import Counter
from datetime import date

from shapely.geometry import shape

RAW_PATH = os.path.join("data", "parks_raw.json")
OUT_GEOJSON = os.path.join("data", "public_spaces.geojson")
OUT_DICT = os.path.join("data", "data_dictionary.md")

# NYC Parks codes the borough as a single letter; spell it out for readers.
BOROUGHS = {"M": "Manhattan", "B": "Brooklyn", "X": "Bronx", "Q": "Queens", "R": "Staten Island"}

# Rough bounding box for the five boroughs. Anything outside this is almost
# certainly a bad coordinate, so we drop it during QA.
NYC_BBOX = {"min_lon": -74.30, "max_lon": -73.65, "min_lat": 40.48, "max_lat": 40.95}


def clean_acres(value):
    """Return acres as a non-negative float, or None if it can't be trusted."""
    try:
        acres = round(float(value), 3)
    except (TypeError, ValueError):
        return None
    return acres if acres >= 0 else None


def centroid_of(geometry):
    """Return (lon, lat) for a park's centroid, repairing bad rings if needed."""
    geom = shape(geometry)
    if not geom.is_valid:
        geom = geom.buffer(0)  # standard trick to fix self-intersecting polygons
    if geom.is_empty:
        return None
    point = geom.centroid
    return round(point.x, 6), round(point.y, 6)


def in_nyc(lon, lat):
    return (NYC_BBOX["min_lon"] <= lon <= NYC_BBOX["max_lon"]
            and NYC_BBOX["min_lat"] <= lat <= NYC_BBOX["max_lat"])


def main():
    with open(RAW_PATH) as f:
        raw = json.load(f)

    stats = Counter()
    stats["read"] = len(raw)

    seen = set()          # (name, lon, lat) keys, to drop duplicates
    features = []

    for row in raw:
        name = (row.get("signname") or "").strip()
        geometry = row.get("multipolygon")

        # Drop rows that can't be placed or named.
        if not name:
            stats["dropped_no_name"] += 1
            continue
        if not geometry:
            stats["dropped_no_geometry"] += 1
            continue

        coords = centroid_of(geometry)
        if coords is None:
            stats["dropped_bad_geometry"] += 1
            continue

        lon, lat = coords
        if not in_nyc(lon, lat):
            stats["dropped_out_of_bounds"] += 1
            continue

        key = (name.lower(), lon, lat)
        if key in seen:
            stats["dropped_duplicate"] += 1
            continue
        seen.add(key)

        features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [lon, lat]},
            "properties": {
                "name": name,
                "borough": BOROUGHS.get(row.get("borough"), "Unknown"),
                "category": (row.get("typecategory") or "Uncategorized").strip(),
                "acres": clean_acres(row.get("acres")),
                "address": (row.get("address") or "").strip().title() or None,
                "zipcode": (row.get("zipcode") or "").strip() or None,
                "community_board": (row.get("communityboard") or "").strip() or None,
                "waterfront": str(row.get("waterfront")).strip().lower() == "true",
            },
        })

    stats["kept"] = len(features)

    collection = {
        "type": "FeatureCollection",
        "metadata": {
            "title": "NYC Public Spaces",
            "source": "NYC Open Data, Parks Properties (dataset enfh-gkve)",
            "prepared": date.today().isoformat(),
            "feature_count": len(features),
            "note": "Point coordinates are polygon centroids computed from the source geometry.",
        },
        "features": features,
    }
    with open(OUT_GEOJSON, "w") as f:
        json.dump(collection, f)

    write_data_dictionary(features)
    print_report(stats, features)


def write_data_dictionary(features):
    boroughs = sorted({f["properties"]["borough"] for f in features})
    categories = sorted({f["properties"]["category"] for f in features})
    lines = [
        "# Data Dictionary: NYC Public Spaces",
        "",
        f"- **Source:** NYC Open Data, Parks Properties (dataset `enfh-gkve`)",
        f"- **Prepared:** {date.today().isoformat()} by `scripts/prepare_data.py`",
        f"- **Records:** {len(features)} public spaces",
        "- **Geometry:** one Point per space (centroid of the original park polygon)",
        "",
        "| Field | Type | Description |",
        "| --- | --- | --- |",
        "| `name` | string | Official sign name of the public space |",
        "| `borough` | string | Borough, spelled out (" + ", ".join(boroughs) + ") |",
        "| `category` | string | Park type, e.g. Neighborhood Park, Garden, Triangle/Plaza |",
        "| `acres` | number \\| null | Size in acres; null where the source value was missing or invalid |",
        "| `address` | string \\| null | Nearest street address, title-cased |",
        "| `zipcode` | string \\| null | ZIP code |",
        "| `community_board` | string \\| null | NYC community board |",
        "| `waterfront` | boolean | Whether the space is on the waterfront |",
        "",
        f"### Categories ({len(categories)})",
        "",
        ", ".join(categories),
        "",
        "### Cleaning steps",
        "",
        "1. Dropped records with no sign name or no geometry.",
        "2. Computed a centroid for each park polygon; repaired invalid rings with a zero-width buffer.",
        "3. Dropped centroids that fell outside the NYC bounding box (bad coordinates).",
        "4. Removed duplicates keyed on name plus rounded coordinates.",
        "5. Coerced `acres` to a non-negative number, else null; spelled out borough codes; normalized text fields.",
        "",
    ]
    with open(OUT_DICT, "w") as f:
        f.write("\n".join(lines))


def print_report(stats, features):
    print("=== QA report ===")
    for key in ["read", "dropped_no_name", "dropped_no_geometry", "dropped_bad_geometry",
                "dropped_out_of_bounds", "dropped_duplicate", "kept"]:
        print(f"  {key:22} {stats[key]}")
    by_borough = Counter(f["properties"]["borough"] for f in features)
    print("  by borough:", dict(by_borough.most_common()))
    acres = [f["properties"]["acres"] for f in features if f["properties"]["acres"] is not None]
    if acres:
        print(f"  acres: min={min(acres)} max={max(acres)} "
              f"missing={len(features) - len(acres)}")


if __name__ == "__main__":
    main()
