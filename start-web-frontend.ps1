# Start Web Frontend Only (No Electron)
# Independent Vite server for browser access

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$FrontendDir = Join-Path $ScriptDir "electron-app"

Write-Host "Starting Web Frontend Server..." -ForegroundColor Cyan
Write-Host "Access URL: http://localhost:5173/" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

Set-Location $FrontendDir
npm run web
