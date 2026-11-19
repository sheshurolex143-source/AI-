$ErrorActionPreference = "Continue"

# Resolve project directory whether run from 'project' or 'finsight-ai'
$baseDir = $PSScriptRoot
if (-not $baseDir) { $baseDir = (Get-Location).Path }

if (Test-Path "$baseDir\finsight-ai") {
    $projectDir = "$baseDir\finsight-ai"
} else {
    $projectDir = $baseDir
}

$backendDir = "$projectDir\backend"
$frontendDir = "$projectDir\frontend"

Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "             FinSight AI System Launcher           " -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "Project directory: $projectDir" -ForegroundColor Gray

# Detect Python venv or system Python
if (Test-Path "$baseDir\.venv\Scripts\python.exe") {
    $pythonDir = "$baseDir\.venv\Scripts"
} elseif (Test-Path "$projectDir\..\.venv\Scripts\python.exe") {
    $pythonDir = "$projectDir\..\.venv\Scripts"
} else {
    $pythonDir = "C:\Users\VS Naidu\AppData\Local\Programs\Python\Python311"
}

$nodeDir = "$env:LOCALAPPDATA\Programs\nodejs"
$env:PATH = "$pythonDir;$nodeDir;$env:PATH"

Write-Host "Python environment: $pythonDir" -ForegroundColor Gray

# Clean up previous instances on ports 8000 and 5173
Write-Host "Releasing ports 8000 and 5173..." -ForegroundColor Gray
Get-NetTCPConnection -LocalPort 8000, 5173 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }

Start-Sleep -Seconds 1

# 1. Start Backend in a dedicated visible CMD window
Write-Host "[1/3] Launching FastAPI Backend on Port 8000..." -ForegroundColor Yellow
$backendCmd = "set PATH=$pythonDir;$nodeDir;%PATH% && cd /d `"$backendDir`" && python -m uvicorn app.main:app --host 127.0.0.1 --port 8000"
Start-Process "cmd.exe" -ArgumentList "/k", "`"$backendCmd`""

# Wait for backend
Start-Sleep -Seconds 3

# 2. Start Frontend in a dedicated visible CMD window
Write-Host "[2/3] Launching Vite Frontend on Port 5173..." -ForegroundColor Yellow
$frontendCmd = "set PATH=$pythonDir;$nodeDir;%PATH% && cd /d `"$frontendDir`" && npm run dev -- --host 127.0.0.1 --port 5173"
Start-Process "cmd.exe" -ArgumentList "/k", "`"$frontendCmd`""

# Wait for frontend
Start-Sleep -Seconds 3

# 3. Open browser
Write-Host "[3/3] Opening Web Browser at http://localhost:5173..." -ForegroundColor Green
Start-Process "http://localhost:5173"

Write-Host ""
Write-Host "===================================================" -ForegroundColor Green
Write-Host "  FinSight AI is now running in terminal windows!  " -ForegroundColor Green
Write-Host "===================================================" -ForegroundColor Green
Write-Host "Web App:   http://localhost:5173" -ForegroundColor White
Write-Host "API Docs:  http://localhost:8000/docs" -ForegroundColor White
Write-Host "Demo User: demo@finsight.ai / Demo@123" -ForegroundColor Yellow
Write-Host "===================================================" -ForegroundColor Green
