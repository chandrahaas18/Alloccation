from pathlib import Path
import pandas as pd
p=Path(__file__).resolve().parent/'data/employee_dataset.xlsx'
if not p.exists(): raise FileNotFoundError(p)
df=pd.read_excel(p); print(f'Dataset ready: {len(df)} rows x {len(df.columns)} columns')
