@echo off
set /p BATCH_ID="Enter Batch ID (or press Enter for Auto-ID): "

echo [1/2] Starting API Model Server...
REM 환경변수로 입력받은 BATCH_ID를 전달합니다.
start /b .venv\Scripts\python.exe api/fastapi_server.py --batch_id "%BATCH_ID%"

echo Waiting for API server to warm up...
timeout /t 5

echo [2/2] Starting Camera Simulator...
.venv\Scripts\python.exe camera_simulator/camera_stream.py

pause
