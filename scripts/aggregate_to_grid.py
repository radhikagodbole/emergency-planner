import os
import pandas as pd
import h3
import pytz

# --- Compatibility layer for different h3 packages ---
if hasattr(h3, "geo_to_h3"):
    # Old API (h3-py <= 3.x)
    h3_cell_fn = h3.geo_to_h3
    h3_to_geo_fn = h3.h3_to_geo
    h3_to_boundary_fn = lambda h: h3.h3_to_geo_boundary(h, geo_json=True)
elif hasattr(h3, "latlng_to_cell"):
    # New API (h3 >= 4.x)
    h3_cell_fn = h3.latlng_to_cell
    h3_to_geo_fn = h3.cell_to_latlng
    h3_to_boundary_fn = lambda h: h3.cell_to_boundary(h)
else:
    raise RuntimeError("Unsupported H3 package version")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_CSV = os.path.join(BASE_DIR, "data", "nyc_911_features.csv")
OUT_PANEL = os.path.join(BASE_DIR, "data", "nyc_911_panel.parquet")
OUT_CELLS = os.path.join(BASE_DIR, "data", "h3_cell_meta.csv")
OUT_GEOJSON = os.path.join(BASE_DIR, "data", "h3_cells.geojson")

# choose H3 resolution
H3_RES = 8  # change to 7 or 9 if you want coarser/finer


def main():
    print("Loading:", INPUT_CSV)
    df = pd.read_csv(INPUT_CSV)

    # ensure datetime is parsed and convert to local time (NYC)
    if "Creation Date" not in df.columns:
        raise RuntimeError("Expected 'Creation Date' column in features CSV.")
    df["Creation Date"] = pd.to_datetime(df["Creation Date"], utc=True, errors="coerce")
    df = df.dropna(subset=["Creation Date"])

    # FLOOR in UTC first (no DST ambiguity), then convert to America/New_York
    df["ts_hour"] = df["Creation Date"].dt.floor("h").dt.tz_convert("America/New_York")

    # compute H3 cell for each event
    if not {"Latitude", "Longitude"}.issubset(df.columns):
        raise RuntimeError("Expected Latitude/Longitude columns in features CSV.")
    df["h3_cell"] = df.apply(
        lambda r: h3_cell_fn(r["Latitude"], r["Longitude"], H3_RES), axis=1
    )

    # aggregate: count calls per (h3_cell, ts_hour)
    panel = (
        df.groupby(["h3_cell", "ts_hour"], as_index=False)
        .size()
        .rename(columns={"size": "calls"})
    )

    # create cell metadata (centroid)
    unique_cells = panel["h3_cell"].unique()
    cell_rows = []
    for c in unique_cells:
        lat, lng = h3_to_geo_fn(c)  # works for both APIs
        cell_rows.append({"h3_cell": c, "center_lat": lat, "center_lng": lng})
    cells_df = pd.DataFrame(cell_rows)

    # sanity checks
    total_events = len(df)
    total_agg = panel["calls"].sum()
    print(f"Total raw events used: {total_events}")
    print(f"Total events after aggregation (sum of calls): {total_agg}")
    assert total_events == total_agg, "Event count mismatch after aggregation!"

    # Save outputs
    panel.to_parquet(OUT_PANEL, index=False)
    cells_df.to_csv(OUT_CELLS, index=False)
    print("Saved panel:", OUT_PANEL)
    print("Saved cell metadata:", OUT_CELLS)

    # Optional: create a lightweight GeoJSON (polygons) for mapping
    try:
        import json

        features = []
        for _, row in cells_df.iterrows():
            h = row["h3_cell"]
            boundary = h3_to_boundary_fn(h)
            # convert to (lng, lat) for GeoJSON and close polygon
            coords = [[lng, lat] for lat, lng in boundary]
            coords.append(coords[0])
            features.append(
                {
                    "type": "Feature",
                    "properties": {"h3_cell": h},
                    "geometry": {"type": "Polygon", "coordinates": [coords]},
                }
            )
        geo = {"type": "FeatureCollection", "features": features}
        with open(OUT_GEOJSON, "w") as f:
            json.dump(geo, f)
        print("Saved GeoJSON for mapping:", OUT_GEOJSON)
    except Exception as e:
        print("Skipping GeoJSON export (optional). Reason:", e)


if __name__ == "__main__":
    main()
