import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PANEL_PATH = os.path.join(BASE_DIR, "data", "nyc_911_panel.parquet")
META_PATH = os.path.join(BASE_DIR, "data", "h3_cell_meta.csv")
OUTPUT_PATH = os.path.join(BASE_DIR, "data", "nyc_911_panel_enriched.parquet")

def main():
    # Load aggregated panel
    print("Loading panel:", PANEL_PATH)
    panel = pd.read_parquet(PANEL_PATH)

    # Load H3 metadata
    print("Loading metadata:", META_PATH)
    meta = pd.read_csv(META_PATH)

    # Join on h3_cell
    enriched = panel.merge(meta, on="h3_cell", how="left")

    # Quick sanity check
    print("Sample rows after join:")
    print(enriched.head())

    # Save enriched panel
    enriched.to_parquet(OUTPUT_PATH, index=False)
    print("Saved enriched panel:", OUTPUT_PATH)

if __name__ == "__main__":
    main()
