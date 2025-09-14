# scripts/plot_demand_trends.py

import pandas as pd
import matplotlib.pyplot as plt
import os
import random

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(BASE_DIR, "data", "nyc_911_model_ready.parquet")

def main():
    print("Loading model-ready dataset...")
    df = pd.read_parquet(DATA_FILE)

    # Pick a few random H3 cells
    unique_cells = df["h3_cell"].unique()
    sample_cells = random.sample(list(unique_cells), 3)  # plot 3 cells

    print(f"Plotting demand trends for cells: {sample_cells}")

    plt.figure(figsize=(12, 6))

    for cell in sample_cells:
        cell_df = df[df["h3_cell"] == cell].sort_values("ts_hour")
        plt.plot(cell_df["ts_hour"], cell_df["calls"], label=f"Cell {cell}")

    plt.title("911 Calls Over Time for Sample H3 Cells")
    plt.xlabel("Time (Hourly)")
    plt.ylabel("Number of Calls")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(BASE_DIR, "data", "demand_trends.png"))
    print("Saved plot to data/demand_trends.png")

if __name__ == "__main__":
    main()
