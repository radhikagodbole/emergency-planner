# scripts/model_xgboost.py

import os
import pandas as pd
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from xgboost import XGBRegressor
import joblib

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(BASE_DIR, "data", "nyc_911_model_ready.parquet")
MODEL_FILE = os.path.join(BASE_DIR, "models", "xgb_model.pkl")
PRED_FILE = os.path.join(BASE_DIR, "data", "xgb_predictions.csv")

def load_data():
    if not os.path.exists(DATA_FILE):
        raise FileNotFoundError(f"Dataset not found at {DATA_FILE}")
    return pd.read_parquet(DATA_FILE)

def train_test_split_time(df, split_date="2021-06-01"):
    train = df[df["ts_hour"] < split_date]
    test = df[df["ts_hour"] >= split_date]
    return train, test

def evaluate(y_true, y_pred, label="XGBoost"):
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    r2 = r2_score(y_true, y_pred)
    print(f"\n{label} Performance:")
    print(f"MAE  : {mae:.4f}")
    print(f"RMSE : {rmse:.4f}")
    print(f"R²   : {r2:.4f}")

def main():
    print("Loading dataset...")
    df = load_data()
    df = df.dropna()  # drop lag/rolling NaNs

    # Feature set (exclude identifiers + target)
    feature_cols = [c for c in df.columns if c not in ["ts_hour", "calls", "h3_cell"]]

    print("Splitting into train/test...")
    train, test = train_test_split_time(df)

    X_train, y_train = train[feature_cols], train["calls"]
    X_test, y_test = test[feature_cols], test["calls"]

    print("Training XGBoost model...")
    model = XGBRegressor(
        n_estimators=300,
        learning_rate=0.1,
        max_depth=6,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train, y_train)

    print("Evaluating on test set...")
    y_pred = model.predict(X_test)
    evaluate(y_test, y_pred, "XGBoost")

    # Save model
    os.makedirs(os.path.join(BASE_DIR, "models"), exist_ok=True)
    joblib.dump(model, MODEL_FILE)
    print(f"Model saved to {MODEL_FILE}")

    # Save predictions
    test_out = test[["ts_hour", "h3_cell", "calls"]].copy()
    test_out["pred_xgb"] = y_pred
    test_out.to_csv(PRED_FILE, index=False)
    print(f"Predictions saved to {PRED_FILE}")

if __name__ == "__main__":
    main()
