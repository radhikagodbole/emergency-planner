# scripts/base_model.py

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(BASE_DIR, "data", "nyc_911_model_ready.parquet")
PLOT_DIR = os.path.join(BASE_DIR, "plots")
os.makedirs(PLOT_DIR, exist_ok=True)

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

def evaluate(y_true, y_pred, label="Model"):
    """Print regression evaluation metrics."""
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    r2 = r2_score(y_true, y_pred)
    print(f"\n{label} Performance:")
    print(f"MAE  : {mae:.4f}")
    print(f"RMSE : {rmse:.4f}")
    print(f"R²   : {r2:.4f}")

def run_naive_baseline(test):
    """Naive baseline: predict calls using lag_1h."""
    if "calls_lag_1h" not in test.columns:
        raise KeyError("calls_lag_1h feature missing. Ensure panel_feature_engineering.py created it.")

    y_test = test["calls"]
    y_pred = test["calls_lag_1h"]

    evaluate(y_test, y_pred, label="Naive Baseline")
    return y_pred

def run_linear_regression(train, test, feature_cols):
    """Linear Regression baseline."""
    X_train, y_train = train[feature_cols], train["calls"]
    X_test, y_test = test[feature_cols], test["calls"]

    model = LinearRegression()
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    evaluate(y_test, y_pred, label="Linear Regression")
    return y_pred

def plot_predictions(test, pred_col, title, filename, sample_cells=3):
    """Plot actual vs predicted for a few sample H3 cells."""
    plt.figure(figsize=(12, 6))
    for i, cell in enumerate(test["h3_cell"].unique()[:sample_cells]):
        subset = test[test["h3_cell"] == cell].sort_values("ts_hour")
        plt.plot(subset["ts_hour"], subset["calls"], label=f"Actual {cell}", alpha=0.7)
        plt.plot(subset["ts_hour"], subset[pred_col], "--", label=f"Predicted {cell}", alpha=0.7)

    plt.title(title)
    plt.xlabel("Time")
    plt.ylabel("Calls")
    plt.legend()
    plt.tight_layout()
    filepath = os.path.join(PLOT_DIR, filename)
    plt.savefig(filepath)
    plt.close()
    print(f"Saved plot: {filepath}")

def main():
    print("Loading dataset...")
    df = load_data()

    # Drop rows with missing values (from lag/rolling features)
    df = df.dropna()

    # Feature set (exclude identifiers + target)
    feature_cols = [col for col in df.columns if col not in ["ts_hour", "calls", "h3_cell"]]

    # Train/test split
    print("Splitting into train/test...")
    train, test = train_test_split_time(df)

    # 1. Run naive baseline
    print("Running Naive Baseline...")
    test["pred_naive"] = run_naive_baseline(test)

    # 2. Run linear regression
    print("Running Linear Regression...")
    test["pred_lr"] = run_linear_regression(train, test, feature_cols)

    # Save predictions
    output_file = os.path.join(BASE_DIR, "data", "baseline_predictions.csv")
    test[["ts_hour", "h3_cell", "calls", "pred_naive", "pred_lr"]].to_csv(output_file, index=False)
    print(f"\nPredictions saved to {output_file}")

    # Generate plots
    print("Generating plots...")
    plot_predictions(test, "pred_naive", "Naive Baseline Predictions vs Actual", "naive_baseline.png")
    plot_predictions(test, "pred_lr", "Linear Regression Predictions vs Actual", "linear_regression.png")

if __name__ == "__main__":
    main()
