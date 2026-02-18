# 快速重启后端脚本
Write-Host "停止所有Python进程..." -ForegroundColor Yellow
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force

Write-Host "等待进程完全终止..." -ForegroundColor Yellow
Start-Sleep -Seconds 2

Write-Host "启动后端服务..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'C:\Users\youda\Desktop\new'; python main.py"

Write-Host "后端服务已在新窗口中启动！" -ForegroundColor Cyan
Write-Host "等待服务初始化..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

Write-Host "测试API端点..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/openapi.json" -TimeoutSec 5
    $json = $response.Content | ConvertFrom-Json
    $testEndpoints = $json.paths.PSObject.Properties.Name | Where-Object { $_ -like "*test*" }
    Write-Host "找到的测试端点:" -ForegroundColor Green
    $testEndpoints | ForEach-Object { Write-Host "  - $_" -ForegroundColor White }

    $templateEndpoints = $json.paths.PSObject.Properties.Name | Where-Object { $_ -like "*template*" }
    Write-Host "`n找到的模板端点:" -ForegroundColor Green
    $templateEndpoints | ForEach-Object { Write-Host "  - $_" -ForegroundColor White }

    Write-Host "`n✅ 后端服务启动成功！" -ForegroundColor Green
} catch {
    Write-Host "`n❌ 后端服务启动失败或未响应" -ForegroundColor Red
    Write-Host "请检查后端窗口的错误信息" -ForegroundColor Yellow
}
