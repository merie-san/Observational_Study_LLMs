import pandas as pd
import os

paths=os.listdir("Data")
for path in paths:
    df=pd.read_json(f"Data/{path}")
    df.to_csv(f"Data/{path.replace("json","csv")}")