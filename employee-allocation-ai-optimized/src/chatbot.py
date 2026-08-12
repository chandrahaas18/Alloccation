import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent

ROOT=Path(__file__).resolve().parents[1]
DB=ROOT/"output/employees.db"
load_dotenv(ROOT/".env")
_agent=None

def get_agent():
    global _agent
    if _agent is None:
        if not DB.exists(): raise FileNotFoundError("output/employees.db not found. Run employee_ai_pipeline.py first.")
        if not os.getenv("GROQ_API_KEY"): raise RuntimeError("GROQ_API_KEY is not configured.")
        db=SQLDatabase.from_uri(f"sqlite:///{DB}")
        llm=ChatGroq(model=os.getenv("GROQ_MODEL","openai/gpt-oss-20b"),temperature=0,max_tokens=220)
        _agent=create_sql_agent(llm=llm,db=db,verbose=False,agent_type="tool-calling",max_iterations=3,max_execution_time=15)
    return _agent

INSTRUCTIONS="Use only the employees table. SELECT only; never modify data. Limit lists to 10 rows unless another limit/count is requested. For top/best/recommended employees sort by final_fit_score DESC. Be concise. Never invent data."

def ask(question):
    return get_agent().invoke({"input":INSTRUCTIONS+"\\n\\nUser question:\\n"+question}).get("output","No answer.")
