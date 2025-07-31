@echo off
echo Starting Legal Document Analysis API...
cd backend
poetry run uvicorn main:app --reload --host 0.0.0.0 --port 8000
pause 