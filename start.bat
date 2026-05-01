@echo off
echo ============================================
echo   AI Knowledge Assistant - Starting Up
echo ============================================
echo.

REM Check for .env
if not exist "backend\.env" (
  echo ERROR: backend\.env not found.
  echo Please create it with: HF_TOKEN=hf_your_token_here
  pause
  exit /b 1
)

REM Start backend in a new window
echo [1/2] Starting FastAPI backend on http://localhost:8000 ...
start "AI Backend" cmd /k "conda activate kpitb_ai && cd backend && uvicorn main:app --reload --port 8000"

REM Wait a moment then start frontend
timeout /t 3 /nobreak > nul

echo [2/2] Starting React frontend on http://localhost:3000 ...
start "AI Frontend" cmd /k "cd frontend && npm start"

echo.
echo Both servers are starting.
echo Backend:  http://localhost:8000/docs
echo Frontend: http://localhost:3000
echo.
pause
