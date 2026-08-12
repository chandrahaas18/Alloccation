cd employee-allocation-ai-optimized

python -m venv venv
.\venv\Scripts\Activate.ps1

pip install -r requirements.txt



Powershell:
python create_sample_data.py
python employee_ai_pipeline.py
python check_database.py


streamlit run app.py
