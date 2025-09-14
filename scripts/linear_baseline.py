# scripts/base_model.py

import os
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(BASE_DIR, "data", "nyc_911_model_ready.parquet")

def load_data():
    """Load model-ready dataset."""
    if not os.path.exists(DATA_FILE):
        raise FileNotFoundError(f"Model-ready file not found at {DATA_FILE}")
    return pd.read_parquet(DATA_FILE)

def train_test_split_time(df, split_date="2021-06-01"):
    """Split into train and test sets based on time."""
    train = df[df["ts_hour"] < split_date]
    test = df[df["ts_hour"] >= split_date]
    return train, test

def evaluate(y_true, y_pred):
    """Print regression evaluation metrics."""
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    r2 = r2_score(y_true, y_pred)
    print("\nEvaluation Metrics:")
    print(f"MAE  : {mae:.4f}")
    print(f"RMSE : {rmse:.4f}")
    print(f"R²   : {r2:.4f}")

def main():
    print("Loading dataset...")
    df = load_data()

    # Drop rows with missing values (from lag/rolling features)
    df = df.dropna()

    # Select features
    feature_cols = [col for col in df.columns if col not in ["ts_hour", "calls", "h3_cell"]]
    X = df[feature_cols]
    y = df["calls"]

    # Split into train/test
    print("Splitting into train/test...")
    train, test = train_test_split_time(df)

    X_train, y_train = train[feature_cols], train["calls"]
    X_test, y_test = test[feature_cols], test["calls"]

    # Train baseline model
    print("Training Linear Regression model...")
    model = LinearRegression()
    model.fit(X_train, y_train)

    # Predict
    y_pred = model.predict(X_test)

    # Evaluate
    evaluate(y_test, y_pred)

    # Save predictions
    test["pred_calls"] = y_pred
    output_file = os.path.join(BASE_DIR, "data", "linear_predictions.csv")
    test[["ts_hour", "h3_cell", "calls", "pred_calls"]].to_csv(output_file, index=False)
    print(f"\nPredictions saved to {output_file}")

if __name__ == "__main__":
    main()
