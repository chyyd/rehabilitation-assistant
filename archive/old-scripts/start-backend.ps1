# ==========================================
# 康复科助手 - 后端服务启动脚本 (生产环境)
# ==========================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  康复科助手 - 后端服务" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 获取脚本所在目录
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

# 检查是否已有后端服务在运行
$existingProcess = Get-Process python -ErrorAction SilentlyContinue | Where-Object {
    $_.MainWindowTitle -like "*uvicorn*" -or $_.MainWindowTitle -like "*api_main*"
}

if ($existingProcess) {
    Write-Host "⚠️  检测到后端服务已在运行" -ForegroundColor Yellow
    $confirm = Read-Host "是否重启? (Y/N)"
    if ($confirm -eq "Y" -or $confirm -eq "y") {
        Write-Host "正在停止现有服务..." -ForegroundColor Yellow
        Stop-Process -Id $existingProcess.Id -Force
        Start-Sleep -Seconds 2
    } else {
        Write-Host "取消启动" -ForegroundColor Gray
        exit
    }
}

Write-Host "🚀 正在启动后端服务..." -ForegroundColor Green
Write-Host ""
Write-Host "服务信息:" -ForegroundColor White
Write-Host "  - 地址: http://127.0.0.1:8000" -ForegroundColor Gray
Write-Host "  - API文档: http://127.0.0.1:8000/docs" -ForegroundColor Gray
Write-Host ""

# 创建日志目录
$LogDir = Join-Path $ScriptDir "logs"
if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir | Out-Null
}

# 生成日志文件名（带日期时间）
$LogFile = Join-Path $LogDir "backend_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"

# 启动后端服务（隐藏窗口，后台运行）
$ProcessInfo = New-Object System.Diagnostics.ProcessStartInfo
$ProcessInfo.FileName = "python"
$ProcessInfo.Arguments = "-m uvicorn backend.api_main:app --host 127.0.0.1 --port 8000"
$ProcessInfo.WorkingDirectory = $ScriptDir
$ProcessInfo.UseShellExecute = $false
$ProcessInfo.RedirectStandardOutput = $true
$ProcessInfo.RedirectStandardError = $true
$ProcessInfo.CreateNoWindow = $true
$ProcessInfo.WindowStyle = [System.Diagnostics.ProcessWindowStyle]::Hidden

$Process = New-Object System.Diagnostics.Process
$Process.StartInfo = $ProcessInfo

# 启动进程并记录输出
$OutputHandle = $Process.Start()
$StreamReader = $Process.StandardOutput
$ErrorReader = $Process.StandardError

# 等待进程启动
Start-Sleep -Seconds 2

if ($Process.HasExited) {
    Write-Host "❌ 后端服务启动失败!" -ForegroundColor Red
    Write-Host ""
    Write-Host "错误信息:" -ForegroundColor Yellow
    $ErrorText = $ErrorReader.ReadToEnd()
    Write-Host $ErrorText -ForegroundColor DarkRed
    Write-Host ""
    Write-Host "请检查:" -ForegroundColor Yellow
    Write-Host "  1. Python 是否已安装" -ForegroundColor Gray
    Write-Host "  2. 依赖包是否已安装 (pip install -r requirements.txt)" -ForegroundColor Gray
    Write-Host "  3. config.json 配置是否正确" -ForegroundColor Gray
    pause
    exit 1
} else {
    Write-Host "✅ 后端服务启动成功!" -ForegroundColor Green
    Write-Host ""
    Write-Host "进程信息:" -ForegroundColor White
    Write-Host "  - PID: $($Process.Id)" -ForegroundColor Gray
    Write-Host "  - 日志: $LogFile" -ForegroundColor Gray
    Write-Host ""
    Write-Host "💡 提示:" -ForegroundColor Yellow
    Write-Host "  - 后端服务在后台运行" -ForegroundColor Gray
    Write-Host "  - 运行 .\stop-backend.ps1 停止服务" -ForegroundColor Gray
    Write-Host ""
    Write-Host "按任意键关闭此窗口..." -ForegroundColor Gray
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

    # 将进程ID保存到文件，方便停止
    $Process.Id | Out-File -FilePath (Join-Path $ScriptDir ".backend.pid") -Encoding UTF8
}

# 清理
if ($null -ne $Process) {
    if (-not $Process.HasExited) {
        $Process.Dispose()
    }
}

