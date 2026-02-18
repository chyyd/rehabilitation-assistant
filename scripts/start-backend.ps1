# Start Backend Script
$ErrorActionPreference = "Continue"

# 获取项目根目录（脚本在 scripts/ 下，需要向上一级）
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

# Stop old process
$OldProcess = Get-Process python -ErrorAction SilentlyContinue | Where-Object {
    $_.CommandLine -like "*uvicorn*"
}
if ($OldProcess) {
    Stop-Process -Id $OldProcess.Id -Force
    Start-Sleep -Seconds 2
}

# Start backend
try {
    $Args = @("-m", "uvicorn", "backend.api_main:app", "--host", "127.0.0.1", "--port", "8000")
    Write-Host "Starting: python $Args" -ForegroundColor Gray
    Write-Host "WorkingDir: $ProjectRoot" -ForegroundColor Gray

    $Process = Start-Process -FilePath "python" `
        -ArgumentList $Args `
        -WorkingDirectory $ProjectRoot `
        -WindowStyle Hidden `
        -PassThru

    $ProcessId = $Process.Id
    Write-Host "Process started with PID: $ProcessId" -ForegroundColor Yellow
    Write-Host "Waiting 5 seconds for startup..." -ForegroundColor Yellow
    Start-Sleep -Seconds 5

    # Check if process is still running
    $RunningProcess = Get-Process -Id $ProcessId -ErrorAction SilentlyContinue
    if (-not $RunningProcess) {
        Write-Host "[ERROR] Process exited unexpectedly!" -ForegroundColor Red
        Write-Host "       Check if Python and dependencies are installed correctly" -ForegroundColor Yellow
        exit 1
    }

    # Check if backend is running
    $Response = Test-NetConnection -ComputerName 127.0.0.1 -Port 8000 -InformationLevel Quiet -ErrorAction SilentlyContinue

    if ($Response) {
        $PidFile = Join-Path $ProjectRoot ".backend.pid"
        $ProcessId | Out-File -FilePath $PidFile -Encoding UTF8

        Write-Host "[OK] Backend started successfully!" -ForegroundColor Green
        Write-Host "     PID: $ProcessId" -ForegroundColor Cyan
        Write-Host "     URL: http://127.0.0.1:8000" -ForegroundColor Gray
        Write-Host "     Docs: http://127.0.0.1:8000/docs" -ForegroundColor Gray

        exit 0
    } else {
        Write-Host "[ERROR] Backend failed to start!" -ForegroundColor Red
        Write-Host "        Cannot connect to port 8000" -ForegroundColor Yellow
        exit 1
    }
} catch {
    Write-Host "[ERROR] Backend failed to start!" -ForegroundColor Red
    Write-Host "        Error: $($_.Exception.Message)" -ForegroundColor Yellow
    exit 1
}
