# Employee Allocation AI — Optimized

## Stack
Sentence-BERT semantic matching, business-rule scoring, K-Means segmentation, SQLite, Streamlit, LangChain SQL Agent and Groq.

## Run
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python create_sample_data.py
python employee_ai_pipeline.py
python check_database.py
streamlit run app.py
```

## Groq
Copy `.env.example` to `.env` and add a fresh Groq API key. Never commit `.env`.

## Latency optimizations
1. SQL agent initialized once and reused.
2. 220-token output cap.
3. Maximum 3 agent iterations and 15-second execution limit.
4. Sentence-BERT embeddings are precomputed by the pipeline, never per chatbot question.
5. SQLite indexes support common filters/sorts.
6. Streamlit caches the loaded employee dataset.

For even lower latency later, add a deterministic query router for common questions, while keeping LangChain for complex natural-language questions.
