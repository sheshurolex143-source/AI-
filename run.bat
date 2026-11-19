@echo off
title FinSight AI Launcher
echo ===================================================
echo           FinSight AI System Launcher
echo ===================================================

set SCRIPT_DIR=%~dp0
if exist "%SCRIPT_DIR%finsight-ai" (
    set "PROJECT_DIR=%SCRIPT_DIR%finsight-ai"
) else (
    set "PROJECT_DIR=%SCRIPT_DIR%"
)

if exist "%SCRIPT_DIR%.venv\Scripts\python.exe" (
    set "VENV_DIR=%SCRIPT_DIR%.venv"
) else if exist "%PROJECT_DIR%\..\.venv\Scripts\python.exe" (
    set "VENV_DIR=%PROJECT_DIR%\..\.venv"
) else (
    set "VENV_DIR=C:\Users\VS Naidu\AppData\Local\Programs\Python\Python311"
)

set "NODE_DIR=%LOCALAPPDATA%\Programs\nodejs"
set "PATH=%VENV_DIR%\Scripts;%VENV_DIR%;%NODE_DIR%;%PATH%"

echo Project Directory: %PROJECT_DIR%
echo Python Environment: %VENV_DIR%

echo Cleaning up previous instances on ports 8000 and 5173...
powershell -NoProfile -Command "Get-NetTCPConnection -LocalPort 8000, 5173 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }"

timeout /t 1 /nobreak >nul

echo [1/3] Starting Backend API Server (FastAPI on Port 8000)...
start "FinSight Backend API (Port 8000)" cmd /k "set "PATH=%VENV_DIR%\Scripts;%VENV_DIR%;%NODE_DIR%;%PATH%" && cd /d "%PROJECT_DIR%\backend" && python -m uvicorn app.main:app --host 127.0.0.1 --port 8000"

timeout /t 3 /nobreak >nul

echo [2/3] Starting Frontend Dev Server (Vite on Port 5173)...
start "FinSight Frontend (Port 5173)" cmd /k "set "PATH=%VENV_DIR%\Scripts;%VENV_DIR%;%NODE_DIR%;%PATH%" && cd /d "%PROJECT_DIR%\frontend" && npm run dev -- --host 127.0.0.1 --port 5173"

timeout /t 3 /nobreak >nul

echo [3/3] Opening Web Browser...
start http://localhost:5173

echo ===================================================
echo FinSight AI is running!
echo Frontend: http://localhost:5173
echo Backend:  http://localhost:8000
echo Docs:     http://localhost:8000/docs
echo Demo Credentials: demo@finsight.ai / Demo@123
echo ===================================================
pause
