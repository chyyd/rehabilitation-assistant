$ScriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptPath

Write-Host "Starting Rehab Assistant System..." -ForegroundColor Cyan

Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$ScriptPath'; python main.py"

Start-Sleep -Seconds 2

Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$ScriptPath\electron-app'; npm run dev"

Write-Host "Services started!" -ForegroundColor Green
Write-Host "Close the windows to stop services." -ForegroundColor Yellow
