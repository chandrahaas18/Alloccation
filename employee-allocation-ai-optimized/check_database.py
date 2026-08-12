from pathlib import Path
import sqlite3,pandas as pd
p=Path(__file__).resolve().parent/'output/employees.db'
if not p.exists(): raise FileNotFoundError('Run employee_ai_pipeline.py first.')
with sqlite3.connect(p) as c: df=pd.read_sql('SELECT * FROM employees',c)
print('Rows:',len(df)); print('\n'.join(' - '+x for x in df.columns))
