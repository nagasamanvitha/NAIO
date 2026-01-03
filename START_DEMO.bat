@echo off
echo ========================================
echo   Multi-Agent Intelligence System
echo   Quick Start Demo
echo ========================================
echo.

echo [1/3] Starting backend server...
start "Backend Server" cmd /k "cd backend && python -m uvicorn main:app --reload"

timeout /t 3 /nobreak >nul

echo [2/3] Generating mock data...
cd backend
python generate_data_instant.py
cd ..

echo.
echo [3/3] Starting frontend...
echo.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo API Docs: http://localhost:8000/docs
echo.
echo Press any key to start frontend...
pause >nul

cd frontend
npm run dev








