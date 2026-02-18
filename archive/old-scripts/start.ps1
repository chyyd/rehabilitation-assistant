# 康复科助手系统启动脚本
# 用于启动后端API和前端Electron应用

$ErrorActionPreference = "Stop"

# 获取脚本所在目录
$ScriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptPath

Write-Host "=" * 60
Write-Host "康复科助手系统启动脚本" -ForegroundColor Cyan
Write-Host "=" * 60
Write-Host ""

# 检查Python是否安装
Write-Host "正在检查Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python已安装: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python未安装或未添加到PATH" -ForegroundColor Red
    exit 1
}

# 检查Node.js是否安装
Write-Host "正在检查Node.js..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version 2>&1
    Write-Host "✓ Node.js已安装: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Node.js未安装或未添加到PATH" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "选择启动模式:" -ForegroundColor Cyan
Write-Host "1. 在当前窗口启动（按Ctrl+C停止）" -ForegroundColor White
Write-Host "2. 在新窗口启动后端和前端" -ForegroundColor White
Write-Host ""

$choice = Read-Host "请输入选择 (1 或 2)"

if ($choice -eq "2") {
    Write-Host ""
    Write-Host "正在新窗口启动服务..." -ForegroundColor Yellow
    Write-Host ""

    # 在新窗口启动后端
    Write-Host "启动后端服务..." -ForegroundColor Cyan
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$ScriptPath'; python main.py"

    # 等待2秒让后端先启动
    Start-Sleep -Seconds 2

    # 在新窗口启动前端
    Write-Host "启动前端应用..." -ForegroundColor Cyan
    Set-Location "$ScriptPath\electron-app"
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$ScriptPath\electron-app'; npm run dev"

    Write-Host ""
    Write-Host "✓ 服务已在独立窗口启动" -ForegroundColor Green
    Write-Host "  - 后端: http://127.0.0.1:8000" -ForegroundColor White
    Write-Host "  - 前端: Electron应用窗口" -ForegroundColor White
    Write-Host ""
    Write-Host "关闭对应窗口即可停止服务" -ForegroundColor Yellow

} else {
    Write-Host ""
    Write-Host "在当前窗口启动服务（按Ctrl+C停止）..." -ForegroundColor Yellow
    Write-Host ""

    # 启动后端（后台作业）
    Write-Host "启动后端服务..." -ForegroundColor Cyan
    $backendJob = Start-Job -ScriptBlock {
        cd $using:ScriptPath
        python main.py
    }

    # 等待后端启动
    Start-Sleep -Seconds 3

    # 检查后端是否启动成功
    $backendOutput = Receive-Job -Job $backendJob -ErrorAction SilentlyContinue
    if ($backendOutput -match "Application startup complete") {
        Write-Host "✓ 后端服务启动成功" -ForegroundColor Green
    } else {
        Write-Host "⚠ 后端服务可能未完全启动，继续启动前端..." -ForegroundColor Yellow
    }

    # 启动前端
    Write-Host "启动前端应用..." -ForegroundColor Cyan
    Set-Location "$ScriptPath\electron-app"
    npm run dev

    # 前端停止后，清理后台作业
    Write-Host ""
    Write-Host "正在停止后端服务..." -ForegroundColor Yellow
    Stop-Job -Job $backendJob
    Remove-Job -Job $backendJob
    Write-Host "✓ 后端服务已停止" -ForegroundColor Green
}

Write-Host ""
