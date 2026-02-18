# Stop All Script
$ErrorActionPreference = "SilentlyContinue"

Write-Host ""
Write-Host "========================================" -ForegroundColor Red
Write-Host "  Stop All Services" -ForegroundColor Red
Write-Host "========================================" -ForegroundColor Red
Write-Host ""

# 获取项目根目录（脚本在 scripts/ 下）
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$Stopped = $false

# Stop from PID files
Write-Host "[1/2] Stopping from PID files..." -ForegroundColor Yellow

$BackendPidFile = Join-Path $ProjectRoot ".backend.pid"
if (Test-Path $BackendPidFile) {
    try {
        $ProcessId = Get-Content $BackendPidFile -Raw
        $ProcessId = $ProcessId.Trim()
        $Process = Get-Process -Id $ProcessId -ErrorAction SilentlyContinue
        if ($Process) {
            Stop-Process -Id $ProcessId -Force
            Write-Host "  [OK] Backend stopped (PID: $ProcessId)" -ForegroundColor Green
            $Stopped = $true
        }
        Remove-Item $BackendPidFile -Force
    } catch {}
}

$FrontendPidFile = Join-Path $ProjectRoot ".frontend.pid"
if (Test-Path $FrontendPidFile) {
    try {
        $ProcessId = Get-Content $FrontendPidFile -Raw
        $ProcessId = $ProcessId.Trim()
        $Process = Get-Process -Id $ProcessId -ErrorAction SilentlyContinue
        if ($Process) {
            Stop-Process -Id $ProcessId -Force
            Write-Host "  [OK] Frontend stopped (PID: $ProcessId)" -ForegroundColor Green
            $Stopped = $true
        }
        Remove-Item $FrontendPidFile -Force
    } catch {}
}

Write-Host ""
Write-Host "[2/2] Finding remaining processes..." -ForegroundColor Yellow

# Stop remaining Python processes
$PythonProcesses = Get-Process python -ErrorAction SilentlyContinue | Where-Object {
    $_.CommandLine -like "*uvicorn*"
}
if ($PythonProcesses) {
    foreach ($p in $PythonProcesses) {
        Stop-Process -Id $p.Id -Force
        $Stopped = $true
    }
    Write-Host "  [OK] Python uvicorn stopped" -ForegroundColor Green
}

# Stop Electron processes
$ElectronProcesses = Get-Process electron -ErrorAction SilentlyContinue
if ($ElectronProcesses) {
    foreach ($p in $ElectronProcesses) {
        Stop-Process -Id $p.Id -Force
        $Stopped = $true
    }
    Write-Host "  [OK] Electron stopped" -ForegroundColor Green
}

# Stop Node vite processes
$NodeProcesses = Get-Process node -ErrorAction SilentlyContinue | Where-Object {
    $_.CommandLine -like "*vite*" -or $_.CommandLine -like "*rehab-assistant*"
}
if ($NodeProcesses) {
    foreach ($p in $NodeProcesses) {
        Stop-Process -Id $p.Id -Force
        $Stopped = $true
    }
    Write-Host "  [OK] Node vite stopped" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Red

if ($Stopped) {
    Write-Host "[OK] All services stopped!" -ForegroundColor Green
} else {
    Write-Host "[INFO] No services were running" -ForegroundColor Gray
}

Write-Host "========================================" -ForegroundColor Red
Write-Host ""
Write-Host "Press any key to close..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
