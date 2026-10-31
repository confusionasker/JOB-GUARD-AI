@echo off
title JobGuard AI - Backend Server
echo ========================================================
echo Starting JobGuard AI Backend (FastAPI + MySQL)...
echo ========================================================
cd /d "%~dp0backend"
if exist venv\Scripts\activate (
    call venv\Scripts\activate
) else (
    echo [ERROR] Virtual environment not found in backend\venv!
    pause
    exit /b 1
)
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
pause

