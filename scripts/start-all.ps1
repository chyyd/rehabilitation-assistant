# Launch All Script
$ErrorActionPreference = "Stop"

# 获取项目根目录（脚本在 scripts/ 下）
$ScriptsDir = $PSScriptRoot
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Rehab Assistant - Launch All" -ForegroundColor Cyan
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

# Start frontend
Write-Host "[2/2] Starting frontend..." -ForegroundColor Yellow
$FrontendScript = Join-Path $ScriptsDir "start-frontend.ps1"

$FrontendResult = & powershell.exe -ExecutionPolicy Bypass -File $FrontendScript

if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Frontend started" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Frontend failed" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  All Services Started!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Services:" -ForegroundColor White
Write-Host "  - Backend API: http://127.0.0.1:8000" -ForegroundColor Gray
Write-Host "  - API Docs:   http://127.0.0.1:8000/docs" -ForegroundColor Gray
Write-Host "  - Frontend:    Electron window" -ForegroundColor Gray
Write-Host ""
Write-Host "Stop services: .\stop-all.ps1" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press any key to close this window..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
