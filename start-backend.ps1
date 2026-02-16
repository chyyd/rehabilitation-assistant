# Start Backend Script
$ErrorActionPreference = "Continue"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

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
        -WorkingDirectory $ScriptDir `
        -WindowStyle Hidden `
        -PassThru

    $ProcessId = $Process.Id
    Start-Sleep -Seconds 3

    # Check if backend is running
    $Response = Test-NetConnection -ComputerName 127.0.0.1 -Port 8000 -InformationLevel Quiet

    if ($Response) {
        $ProcessId | Out-File -FilePath ".backend.pid" -Encoding UTF8

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
