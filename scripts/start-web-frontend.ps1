# Start Web Frontend Only (No Electron)
# Independent Vite server for browser access

# 获取项目根目录（从脚本位置向上两级）
$ProjectRoot = $PSScriptRoot
$FrontendDir = Join-Path $ProjectRoot "electron-app"

Write-Host "Starting Web Frontend Server..." -ForegroundColor Cyan
Write-Host "Project Root: $ProjectRoot" -ForegroundColor Gray
Write-Host "Frontend Dir: $FrontendDir" -ForegroundColor Gray
Write-Host "Access URL: http://localhost:5173/" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

# 检查前端目录是否存在
if (-not (Test-Path $FrontendDir)) {
    Write-Host "[ERROR] Frontend directory not found: $FrontendDir" -ForegroundColor Red
    Write-Host "Please run this script from the project root directory" -ForegroundColor Yellow
    exit 1
}

Set-Location $FrontendDir
npm run web
