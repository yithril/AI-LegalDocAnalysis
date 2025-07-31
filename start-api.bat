@echo off
echo Starting Legal Document Analysis Application...
echo.

echo Starting Backend API...
start "Backend API" powershell -Command "cd backend && poetry run uvicorn main:app --reload --host 0.0.0.0 --port 8000"

echo Starting Frontend Development Server...
start "Frontend Dev Server" powershell -Command "cd frontend && npm run dev"

echo.
echo Both servers are starting...
echo Backend will be available at: http://localhost:8000
echo Frontend will be available at: http://localhost:3000
echo.
echo Press any key to close this window (servers will continue running)
pause > nul 