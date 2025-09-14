# scripts/feature_engineering.py

import pandas as pd
import os

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
INPUT_FILE = os.path.join(DATA_DIR, "nyc_911_clean.csv")
OUTPUT_FILE = os.path.join(DATA_DIR, "nyc_911_features.csv")

def load_data():
    """Load cleaned 911 data."""
    if not os.path.exists(INPUT_FILE):
        raise FileNotFoundError(f"Input file not found at {INPUT_FILE}")
    return pd.read_csv(INPUT_FILE)

def extract_time_features(df):
    """Extract useful time-based features."""
    # Match the actual column name from cleaned CSV
    if "Creation Date" not in df.columns:
        raise KeyError("Expected column 'Creation Date' not found in dataset.")
    
    df["Creation Date"] = pd.to_datetime(df["Creation Date"])
    df["year"] = df["Creation Date"].dt.year
    df["month"] = df["Creation Date"].dt.month
    df["day"] = df["Creation Date"].dt.day
    df["hour"] = df["Creation Date"].dt.hour
    df["day_of_week"] = df["Creation Date"].dt.dayofweek  # Monday=0
    df["is_weekend"] = df["day_of_week"].isin([5, 6]).astype(int)
    return df

def engineer_location_features(df):
    """Extract features based on location data."""
    # Match column names from your cleaned CSV
    if "Latitude" in df.columns and "Longitude" in df.columns:
        df["lat_round"] = df["Latitude"].round(3)
        df["lon_round"] = df["Longitude"].round(3)
    return df

def encode_categoricals(df):
    """Encode categorical features."""
    if "Incident Type" in df.columns:
        df = pd.get_dummies(df, columns=["Incident Type"], prefix="incident")
    if "Borough" in df.columns:
        df = pd.get_dummies(df, columns=["Borough"], prefix="borough")
    return df

def main():
    print("Loading cleaned data...")
    df = load_data()

    print("Engineering features...")
    df = extract_time_features(df)
    df = engineer_location_features(df)
    df = encode_categoricals(df)

    print(f"Saving feature file to {OUTPUT_FILE}...")
    df.to_csv(OUTPUT_FILE, index=False)
    print("Feature engineering completed successfully.")

if __name__ == "__main__":
    main()
