Write-Host "Stopping Rehab Assistant System..." -ForegroundColor Yellow
Write-Host ""

$pythonStopped = $false
$nodeStopped = $false

$pythonProcesses = Get-Process python -ErrorAction SilentlyContinue
if ($pythonProcesses) {
    Write-Host "Stopping backend services..." -ForegroundColor Cyan
    foreach ($process in $pythonProcesses) {
        Stop-Process -Id $process.Id -Force
        $pythonStopped = $true
    }
    if ($pythonStopped) {
        Write-Host "Backend services stopped" -ForegroundColor Green
    }
} else {
    Write-Host "No backend services found" -ForegroundColor Gray
}

Write-Host ""

$nodeProcesses = Get-Process node -ErrorAction SilentlyContinue
if ($nodeProcesses) {
    Write-Host "Stopping frontend services..." -ForegroundColor Cyan
    foreach ($process in $nodeProcesses) {
        Stop-Process -Id $process.Id -Force
        $nodeStopped = $true
    }
    if ($nodeStopped) {
        Write-Host "Frontend services stopped" -ForegroundColor Green
    }
} else {
    Write-Host "No frontend services found" -ForegroundColor Gray
}

Write-Host ""
if ($pythonStopped -or $nodeStopped) {
    Write-Host "All services stopped!" -ForegroundColor Green
} else {
    Write-Host "No services were running" -ForegroundColor Gray
}
Write-Host ""
