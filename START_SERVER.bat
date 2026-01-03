@echo off
echo Starting Multi-Agent Intelligence System Backend...
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8002
pause






