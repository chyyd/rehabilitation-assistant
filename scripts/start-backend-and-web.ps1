# Start Backend + Web Frontend Script
$ErrorActionPreference = "Stop"

# 获取项目根目录和脚本目录（脚本在 scripts/ 下）
$ScriptsDir = $PSScriptRoot
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Rehab Assistant - Backend + Web" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Start backend
Write-Host "[1/2] Starting backend..." -ForegroundColor Yellow
$BackendScript = Join-Path $ScriptsDir "start-backend.ps1"

$BackendResult = & powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -File $BackendScript

if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Backend started" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Backend failed" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""

# Start web frontend
Write-Host "[2/2] Starting web frontend..." -ForegroundColor Yellow
$WebScript = Join-Path $ScriptsDir "start-web-frontend.ps1"

& powershell.exe -ExecutionPolicy Bypass -File $WebScript

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Services Started!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Services:" -ForegroundColor White
Write-Host "  - Backend API: http://127.0.0.1:8000" -ForegroundColor Gray
Write-Host "  - API Docs:   http://127.0.0.1:8000/docs" -ForegroundColor Gray
Write-Host "  - Web Frontend: http://localhost:5173/" -ForegroundColor Gray
Write-Host ""
Write-Host "Stop services: Run 启动.bat and select [5]" -ForegroundColor Yellow
Write-Host ""
