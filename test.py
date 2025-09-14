import pandas as pd
df = pd.read_parquet("data/nyc_911_model_ready.parquet")
print(df.head(10))
