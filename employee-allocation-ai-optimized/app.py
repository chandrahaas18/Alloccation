import sqlite3
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv

ROOT=Path(__file__).resolve().parent
DB=ROOT/"output/employees.db"
load_dotenv(ROOT/".env")

st.set_page_config(page_title="Employee Allocation AI",page_icon="◆",layout="wide")
st.markdown("""
<style>
.stApp{background:#f4f4f4;color:#111}
[data-testid="stSidebar"]{background:#090909}
[data-testid="stSidebar"] *{color:#fff!important}
.hero{background:#090909;color:#fff;padding:28px 32px;border-radius:16px;border-left:7px solid #e30613;margin-bottom:18px}
.hero h1{color:#fff;margin:0;font-size:34px}.hero p{color:#ccc;margin:7px 0 0}
.card{background:#fff;border:1px solid #ddd;border-radius:14px;padding:18px;min-height:100px}
.label{font-size:11px;color:#666;text-transform:uppercase;letter-spacing:.08em}
.value{font-size:28px;font-weight:800}.red{color:#e30613}
.stButton>button{border-radius:9px;font-weight:700}
</style>
""",unsafe_allow_html=True)

if not DB.exists():
    st.error("Database not found. Run: python employee_ai_pipeline.py")
    st.stop()

@st.cache_data
def load_data():
    with sqlite3.connect(DB) as c:
        return pd.read_sql("SELECT * FROM employees",c)

df=load_data()

with st.sidebar:
    st.markdown("## EMPLOYEE AI")
    st.caption("Allocation intelligence")
    page=st.radio("Navigate",["Overview","Recommendations","Workforce Intelligence","AI Assistant"])
    st.divider()
    skills=st.multiselect("Primary skill",sorted(df.primary_skill.unique()))
    locations=st.multiselect("Location",sorted(df.location.unique()))
    domains=st.multiselect("Domain",sorted(df.domain.unique()))
    statuses=st.multiselect("Allocation status",sorted(df.allocation_status.unique()))

f=df.copy()
if skills:f=f[f.primary_skill.isin(skills)]
if locations:f=f[f.location.isin(locations)]
if domains:f=f[f.domain.isin(domains)]
if statuses:f=f[f.allocation_status.isin(statuses)]

st.markdown('<div class="hero"><h1>AI-Powered Employee Allocation</h1><p>Sentence-BERT + business rules + K-Means + conversational SQL</p></div>',unsafe_allow_html=True)

if page=="Overview":
    cols=st.columns(4)
    vals=[("Total employees",len(f),""),("Unallocated",int((f.allocation_status=="Unallocated").sum()),"red"),
          ("Avg fit score",f"{f.final_fit_score.mean():.1f}" if len(f) else "0",""),
          ("Needs attention",int((f.bench_risk=="Needs Attention").sum()),"red")]
    for c,(lab,val,cl) in zip(cols,vals):
        c.markdown(f'<div class="card"><div class="label">{lab}</div><div class="value {cl}">{val}</div></div>',unsafe_allow_html=True)
    a,b=st.columns(2)
    with a:
        x=f.groupby("primary_skill").size().reset_index(name="employees").sort_values("employees",ascending=False).head(12)
        st.plotly_chart(px.bar(x,x="employees",y="primary_skill",orientation="h",title="Skill Availability"),use_container_width=True)
    with b:
        x=f.groupby("location").size().reset_index(name="employees")
        st.plotly_chart(px.bar(x,x="location",y="employees",title="Employees by Location"),use_container_width=True)
    a,b=st.columns(2)
    with a:
        x=f.groupby("experience_band").size().reset_index(name="employees")
        st.plotly_chart(px.pie(x,names="experience_band",values="employees",hole=.55,title="Experience Distribution"),use_container_width=True)
    with b:
        x=f.groupby("bench_risk").size().reset_index(name="employees")
        st.plotly_chart(px.bar(x,x="bench_risk",y="employees",title="Bench Risk"),use_container_width=True)

elif page=="Recommendations":
    st.subheader("Top Recommended Employees")
    top=f.sort_values("final_fit_score",ascending=False).head(10)
    cards=st.columns(3)
    for i,(_,r) in enumerate(top.head(3).iterrows()):
        cards[i].markdown(f'<div class="card"><div class="label">Rank #{int(r.recommendation_rank)}</div><b style="font-size:21px">{r.employee_name}</b><br>{r.primary_skill} · {r.skill_group} · {r.location}<div class="value red">{r.final_fit_score:.1f}</div><span style="color:#666">Final fit score</span></div>',unsafe_allow_html=True)
    cols=["recommendation_rank","employee_id","employee_name","experience","primary_skill","secondary_skill","skill_group","location","domain","allocation_status","semantic_match_score","rule_fit_score","final_fit_score","bench_risk","recommendation_reason"]
    st.dataframe(top[cols],use_container_width=True,hide_index=True)

elif page=="Workforce Intelligence":
    st.subheader("Workforce Intelligence")
    a,b=st.columns(2)
    with a:
        x=f.groupby("employee_cluster").size().reset_index(name="employees")
        st.plotly_chart(px.bar(x,x="employee_cluster",y="employees",title="Employee Clusters"),use_container_width=True)
    with b:
        x=f.groupby("skill_group",as_index=False).bench_age.mean()
        st.plotly_chart(px.bar(x,x="skill_group",y="bench_age",title="Average Bench Age by Skill Group"),use_container_width=True)
    st.subheader("Employees Needing Attention")
    x=f[f.bench_risk=="Needs Attention"].sort_values("bench_age",ascending=False)
    st.dataframe(x[["employee_name","experience","primary_skill","location","bench_age","final_fit_score","bench_risk"]].head(20),use_container_width=True,hide_index=True)

else:
    st.subheader("AI Assistant")
    st.caption("Natural-language questions over the enhanced employee database.")
    with st.expander("Example questions"):
        for q in ["Who is the top fit-score employee?","Show top 5 Java employees in Bangalore.","Which employees need bench attention?","Count employees by location.","Show unallocated backend employees."]:
            st.code(q)
    if "messages" not in st.session_state: st.session_state.messages=[]
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.write(m["content"])
    q=st.chat_input("Ask about employee allocation...")
    if q:
        st.session_state.messages.append({"role":"user","content":q})
        with st.chat_message("user"): st.write(q)
        with st.chat_message("assistant"):
            with st.spinner("Querying database..."):
                try:
                    from src.chatbot import ask
                    ans=ask(q)
                except Exception as e:
                    ans=f"Unable to answer: {e}"
            st.write(ans)
            st.session_state.messages.append({"role":"assistant","content":ans})
