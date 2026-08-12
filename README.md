employee-allocation-ai/
│
├── app.py
├── employee_ai_pipeline.py
├── create_sample_data.py
├── check_database.py
├── requirements.txt
├── .env.example
├── README.md
│
├── config/
│   └── project_requirement.json
│
├── data/
│   └── employee_dataset.xlsx
│
├── src/
│   ├── pipeline.py
│   ├── chatbot.py
│   └── __init__.py
│
├── output/
│
└── .streamlit/
    └── config.toml
    ================================================
    Architecture:
                       employee_dataset.xlsx
                           │
                           ▼
                  employee_ai_pipeline.py
                           │
             ┌─────────────┼──────────────┐
             ▼             ▼              ▼
       Sentence-BERT   Business Rules   K-Means
             │             │              │
             ▼             ▼              ▼
       Semantic Score   Rule Score      Clusters
             │             │
             └──────┬──────┘
                    ▼
             Final Fit Score
                    │
                    ▼
             Bench Risk
                    │
                    ▼
          Recommendation Ranking
                    │
                    ▼
        enhanced_employee_dataset.csv
                    │
                    ▼
              employees.db
                 /      \
                /        \
               ▼          ▼
        Streamlit UI   LangChain
                         │
                         ▼
                       Groq

++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


    
