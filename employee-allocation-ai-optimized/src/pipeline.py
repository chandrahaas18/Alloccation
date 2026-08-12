from pathlib import Path
import json, sqlite3
import numpy as np, pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"data/employee_dataset.xlsx"; REQ=ROOT/"config/project_requirement.json"; OUT=ROOT/"output"
MODEL="sentence-transformers/all-MiniLM-L6-v2"

def band(x):
    return "0-2 Years" if x<=2 else "2-5 Years" if x<=5 else "5-8 Years" if x<=8 else "8+ Years"

def profile(r):
    return f"Role {r.primary_skill}; secondary {r.secondary_skill}; group {r.skill_group}; location {r.location}; domain {r.domain}; experience {r.experience}; certification {r.certification}; preferred domain {r.preferred_domain}; work mode {r.preferred_work_mode}"

def req_text(q):
    return f"Role {q['role']}; primary {q['primary_skill']}; secondary {', '.join(q['secondary_skills'])}; group {q['skill_group']}; location {q['location']}; domain {q['domain']}; experience {q['min_experience']}-{q['max_experience']}; status {q['allocation_status']}"

def rules(r,q):
    s=0; reasons=[]
    if str(r.primary_skill).lower()==q["primary_skill"].lower(): s+=30; reasons.append("Primary skill matches")
    elif any(x.lower() in str(r.secondary_skill).lower() for x in q["secondary_skills"]): s+=12; reasons.append("Secondary skill is relevant")
    if q["min_experience"]<=r.experience<=q["max_experience"]: s+=20; reasons.append("Experience is in required range")
    elif r.experience>=q["min_experience"]-1: s+=8; reasons.append("Experience is close to required range")
    if str(r.skill_group).lower()==q["skill_group"].lower(): s+=15; reasons.append("Skill group matches")
    if str(r.location).lower()==q["location"].lower(): s+=10; reasons.append("Location matches")
    if str(r.domain).lower()==q["domain"].lower(): s+=10; reasons.append("Domain matches")
    if str(r.allocation_status).lower()==q["allocation_status"].lower(): s+=10; reasons.append("Currently unallocated")
    if r.communication_rating>=4: s+=2.5; reasons.append("Strong communication rating")
    if r.last_project_rating>=4: s+=2.5; reasons.append("Strong previous project rating")
    return min(s,100),", ".join(reasons) or "General profile relevance"

def run_pipeline():
    if not DATA.exists(): raise FileNotFoundError("data/employee_dataset.xlsx not found. Run create_sample_data.py first.")
    df=pd.read_excel(DATA); q=json.loads(REQ.read_text())
    df["experience_band"]=df.experience.apply(band); df["employee_profile"]=df.apply(profile,axis=1)
    print("Generating Sentence-BERT embeddings...")
    model=SentenceTransformer(MODEL)
    rv=model.encode([req_text(q)],normalize_embeddings=True,show_progress_bar=False)[0]
    ev=model.encode(df.employee_profile.tolist(),normalize_embeddings=True,batch_size=32,show_progress_bar=True)
    df["semantic_match_score"]=np.round(np.clip((ev@rv+1)*50,0,100),2)
    print("Calculating business-rule scores...")
    rs=df.apply(lambda r:rules(r,q),axis=1)
    df["rule_fit_score"]=rs.apply(lambda x:round(x[0],2))
    df["recommendation_reason"]=rs.apply(lambda x:x[1])
    df["final_fit_score"]=np.round(.6*df.rule_fit_score+.4*df.semantic_match_score,2)
    df["bench_risk"]=df.apply(lambda r:"Needs Attention" if r.allocation_status=="Unallocated" and r.bench_age>=60 else "Monitor" if r.allocation_status=="Unallocated" and r.bench_age>=30 else "Normal",axis=1)
    x=StandardScaler().fit_transform(df[["experience","bench_age","communication_rating","last_project_rating","semantic_match_score","rule_fit_score","final_fit_score"]].fillna(0))
    df["employee_cluster"]=KMeans(n_clusters=5,random_state=42,n_init=10).fit_predict(x)
    df=df.sort_values(["final_fit_score","semantic_match_score"],ascending=False).reset_index(drop=True)
    df["recommendation_rank"]=np.arange(1,len(df)+1)
    OUT.mkdir(exist_ok=True); csv=OUT/"enhanced_employee_dataset.csv"; db=OUT/"employees.db"
    df.to_csv(csv,index=False)
    with sqlite3.connect(db) as c:
        df.to_sql("employees",c,if_exists="replace",index=False)
        for i,col in enumerate(["final_fit_score","primary_skill","location","allocation_status","bench_risk"]):
            c.execute(f"CREATE INDEX IF NOT EXISTS idx_{i} ON employees({col})")
        c.commit()
    print("Pipeline completed."); print(f"Enhanced CSV: {csv}"); print(f"SQLite DB: {db}")
    print(df[["recommendation_rank","employee_name","primary_skill","location","final_fit_score","bench_risk"]].head(10).to_string(index=False))

if __name__=="__main__": run_pipeline()
