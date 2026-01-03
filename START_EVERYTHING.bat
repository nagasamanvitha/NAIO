@echo off
echo ========================================
echo Starting Complete Naio Application
echo ========================================
echo.
echo This will start:
echo   1. Backend (FastAPI) on http://localhost:8002
echo   2. Frontend (Next.js) on http://localhost:3000
echo   3. n8n is already running on http://localhost:5678
echo.
echo ========================================
echo.

echo [1/2] Starting Backend...
start cmd /k "cd backend && uvicorn main:app --reload --host 127.0.0.1 --port 8002"
timeout /t 5 /nobreak >nul

echo [2/2] Starting Frontend...
start cmd /k "cd frontend && npm run dev"

echo.
echo ========================================
echo All Services Starting!
echo ========================================
echo.
echo Backend:  http://localhost:8002
echo Frontend: http://localhost:3000
echo n8n:      http://localhost:5678
echo.
echo Wait 30 seconds for services to start...
echo.
echo Then:
echo   1. Open http://localhost:3000 in your browser
echo   2. Execute n8n workflow to send data
echo   3. See data appear in your dashboard!
echo.
echo ========================================
echo.
pause






