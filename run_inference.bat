@echo off
echo Starting Vision AI Quality System...
echo (Batch ID is managed by Dashboard sidebar)

echo [1/2] Starting API Model Server...
start /b .venv\Scripts\python.exe api/fastapi_server.py

echo Waiting for API server (5s)...
timeout /t 5

echo [2/2] Starting Camera Simulator...
.venv\Scripts\python.exe camera_simulator/camera_stream.py

pause
