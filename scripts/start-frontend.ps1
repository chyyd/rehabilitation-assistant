# Start Frontend Script
$ErrorActionPreference = "Continue"

# 获取项目根目录和前端目录
$ProjectRoot = $PSScriptRoot
$FrontendDir = Join-Path $ProjectRoot "electron-app"

# Wait for backend
Write-Host "Waiting for backend..." -ForegroundColor Yellow
for ($i = 1; $i -le 10; $i++) {
    $Response = Test-NetConnection -ComputerName 127.0.0.1 -Port 8000 -InformationLevel Quiet -ErrorAction SilentlyContinue
    if ($Response) {
        Write-Host "[OK] Backend is ready" -ForegroundColor Green
        break
    }
    Start-Sleep -Seconds 1
}

Set-Location $FrontendDir

# Check node_modules
if (-not (Test-Path "node_modules")) {
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    cmd /c "npm install"
}

# Start frontend using cmd
try {
    Write-Host "Starting frontend..." -ForegroundColor Yellow

    # Use cmd /c to start npm in a new window
    $Command = "cd /d `"$FrontendDir`" && npm run dev"

    $Process = Start-Process -FilePath "cmd.exe" `
        -ArgumentList "/c", $Command `
        -WorkingDirectory $FrontendDir `
        -WindowStyle Normal `
        -PassThru

    $ProcessId = $Process.Id

    # Save PID to project root
    $PidFile = Join-Path $ProjectRoot ".frontend.pid"
    $ProcessId | Out-File -FilePath $PidFile -Encoding UTF8

    Write-Host "[OK] Frontend started!" -ForegroundColor Green
    Write-Host "     PID: $ProcessId" -ForegroundColor Cyan
    Write-Host "     Electron window will open in a few seconds" -ForegroundColor Gray
    Write-Host "" -ForegroundColor Gray
    Write-Host "Note: A command window has been opened for Vite/Electron" -ForegroundColor Gray

    exit 0
} catch {
    Write-Host "[ERROR] Frontend failed to start!" -ForegroundColor Red
    Write-Host "        $($_.Exception.Message)" -ForegroundColor Yellow
    exit 1
}
