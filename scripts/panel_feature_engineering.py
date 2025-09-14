
import pandas as pd
import os

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
INPUT_FILE = os.path.join(DATA_DIR, "nyc_911_panel_enriched.parquet")
OUTPUT_FILE = os.path.join(DATA_DIR, "nyc_911_model_ready.parquet")

def load_data():
    """Load enriched panel with spatio-temporal aggregation."""
    if not os.path.exists(INPUT_FILE):
        raise FileNotFoundError(f"Input file not found at {INPUT_FILE}")
    return pd.read_parquet(INPUT_FILE)

def add_time_features(df):
    """Extract features from ts_hour (already hourly)."""
    df["year"] = df["ts_hour"].dt.year
    df["month"] = df["ts_hour"].dt.month
    df["day"] = df["ts_hour"].dt.day
    df["hour"] = df["ts_hour"].dt.hour
    df["day_of_week"] = df["ts_hour"].dt.dayofweek  # Monday=0
    df["is_weekend"] = df["day_of_week"].isin([5, 6]).astype(int)
    return df

def add_lag_features(df, lags=[1, 2, 3, 6, 12, 24]):
    """Add lag features for past call counts within each H3 cell."""
    df = df.sort_values(["h3_cell", "ts_hour"])
    for lag in lags:
        df[f"calls_lag_{lag}h"] = df.groupby("h3_cell")["calls"].shift(lag)
    return df

def add_rolling_features(df, windows=[3, 6, 12, 24]):
    """Add rolling mean/std of call counts within each H3 cell."""
    df = df.sort_values(["h3_cell", "ts_hour"])
    for w in windows:
        df[f"calls_rollmean_{w}h"] = (
            df.groupby("h3_cell")["calls"]
              .shift(1)  # avoid leakage
              .rolling(window=w, min_periods=1)
              .mean()
              .reset_index(level=0, drop=True)
        )
        df[f"calls_rollstd_{w}h"] = (
            df.groupby("h3_cell")["calls"]
              .shift(1)
              .rolling(window=w, min_periods=1)
              .std()
              .reset_index(level=0, drop=True)
        )
    return df

def main():
    print("Loading enriched panel...")
    df = load_data()

    print("Adding temporal features...")
    df = add_time_features(df)

    print("Adding lag features...")
    df = add_lag_features(df)

    print("Adding rolling features...")
    df = add_rolling_features(df)

    print(f"Saving model-ready dataset to {OUTPUT_FILE}...")
    df.to_parquet(OUTPUT_FILE, index=False)
    print("Feature engineering completed successfully.")

if __name__ == "__main__":
    main()
