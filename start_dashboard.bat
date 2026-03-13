@echo off
echo Starting Quality Dashboard...
.venv\Scripts\python.exe -m streamlit run dashboard/streamlit_app.py --server.port 8501
pause
