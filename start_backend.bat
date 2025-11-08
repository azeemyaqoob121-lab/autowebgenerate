@echo off
echo Starting AutoWeb Backend Server...
echo.

cd backend
..\venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

pause
