@echo off
title Push FinSight AI to GitHub
echo ===================================================
echo          Push FinSight AI to GitHub
echo ===================================================

set "GIT_DIR=%LOCALAPPDATA%\Programs\git\cmd"
set "PATH=%GIT_DIR%;%PATH%"

set SCRIPT_DIR=%~dp0
if exist "%SCRIPT_DIR%finsight-ai" (
    set "PROJECT_DIR=%SCRIPT_DIR%finsight-ai"
) else (
    set "PROJECT_DIR=%SCRIPT_DIR%"
)

cd /d "%PROJECT_DIR%"

echo.
echo Current Git Status:
git status --short
echo.

set /p REPO_URL="Paste your GitHub Repository URL (e.g. https://github.com/username/finsight-ai.git): "

if "%REPO_URL%"=="" (
    echo No URL entered. Exiting.
    pause
    exit /b
)

echo.
echo Linking remote origin to: %REPO_URL%
git remote remove origin 2>nul
git remote add origin %REPO_URL%
git branch -M main

echo.
echo Pushing to GitHub (a browser login window may pop up to authenticate)...
git push -u origin main

echo.
echo ===================================================
if %ERRORLEVEL% EQU 0 (
    echo SUCCESS! Your project is now live on GitHub!
) else (
    echo Push failed. Please check your GitHub repository URL and permissions.
)
echo ===================================================
pause
