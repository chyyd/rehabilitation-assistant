# Start Backend Script
$ErrorActionPreference = "Continue"

# 获取项目根目录（脚本在 scripts/ 下，需要向上一级）
$ProjectRoot = $PSScriptRoot
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
    $Process = Start-Process -FilePath "python" `
        -ArgumentList "-m uvicorn backend.api_main:app --host 127.0.0.1 --port 8000" `
        -WorkingDirectory $ProjectRoot `
        -WindowStyle Hidden `
        -PassThru

    $ProcessId = $Process.Id
    Start-Sleep -Seconds 3

    # Check if backend is running
    $Response = Test-NetConnection -ComputerName 127.0.0.1 -Port 8000 -InformationLevel Quiet

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
