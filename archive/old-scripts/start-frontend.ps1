# ==========================================
# 康复科助手 - 前端服务启动脚本 (生产环境)
# ==========================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  康复科助手 - 前端应用" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 获取脚本所在目录
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$FrontendDir = Join-Path $ScriptDir "electron-app"

# 检查后端服务是否运行
Write-Host "🔍 检查后端服务..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/docs" -Method HEAD -TimeoutSec 3 -UseBasicParsing
    Write-Host "✅ 后端服务正常" -ForegroundColor Green
} catch {
    Write-Host "⚠️  后端服务未检测到" -ForegroundColor Yellow
    $confirm = Read-Host "是否启动后端服务? (Y/N)"
    if ($confirm -eq "Y" -or $confirm -eq "y") {
        $BackendScript = Join-Path $ScriptDir "start-backend.ps1"
        if (Test-Path $BackendScript) {
            Start-Process powershell -ArgumentList "-ExecutionPolicy Bypass -File `"$BackendScript`""
            Start-Sleep -Seconds 3
        } else {
            Write-Host "❌ 找不到 start-backend.ps1" -ForegroundColor Red
            Write-Host "请先手动启动后端服务" -ForegroundColor Yellow
        }
    } else {
        Write-Host "⚠️  警告: 前端功能可能受限" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "🚀 正在启动前端应用..." -ForegroundColor Green
Write-Host ""

Set-Location $FrontendDir

# 检查 node_modules
if (-not (Test-Path "node_modules")) {
    Write-Host "⚠️  未检测到 node_modules，正在安装依赖..." -ForegroundColor Yellow
    npm install
    Write-Host ""
}

# 创建日志目录
$LogDir = Join-Path $ScriptDir "logs"
if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir | Out-Null
}

# 启动前端（隐藏此命令行窗口，显示 Electron 应用窗口）
$ProcessInfo = New-Object System.Diagnostics.ProcessStartInfo
$ProcessInfo.FileName = "npm"
$ProcessInfo.Arguments = "run dev"
$ProcessInfo.WorkingDirectory = $FrontendDir
$ProcessInfo.UseShellExecute = $false
$ProcessInfo.RedirectStandardOutput = $true
$ProcessInfo.RedirectStandardError = $true
$ProcessInfo.CreateNoWindow = $true

$Process = New-Object System.Diagnostics.Process
$Process.StartInfo = $ProcessInfo

try {
    $Process.Start() | Out-Null
    Start-Sleep -Seconds 3

    if ($Process.HasExited) {
        Write-Host "❌ 前端启动失败!" -ForegroundColor Red
        Write-Host ""
        Write-Host "请检查:" -ForegroundColor Yellow
        Write-Host "  1. Node.js 是否已安装" -ForegroundColor Gray
        Write-Host "  2. 依赖是否已安装 (cd electron-app && npm install)" -ForegroundColor Gray
        pause
        exit 1
    } else {
        Write-Host "✅ 前端应用启动成功!" -ForegroundColor Green
        Write-Host ""
        Write-Host "进程信息:" -ForegroundColor White
        Write-Host "  - PID: $($Process.Id)" -ForegroundColor Gray
        Write-Host ""
        Write-Host "💡 提示:" -ForegroundColor Yellow
        Write-Host "  - Electron 应用窗口应该已经打开" -ForegroundColor Gray
        Write-Host "  - 此窗口可以关闭，不影响应用运行" -ForegroundColor Gray
        Write-Host "  - 运行 .\stop-frontend.ps1 停止应用" -ForegroundColor Gray
        Write-Host ""
        Write-Host "按任意键关闭此启动窗口..." -ForegroundColor Gray
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

        # 将进程ID保存到文件
        $Process.Id | Out-File -FilePath (Join-Path $ScriptDir ".frontend.pid") -Encoding UTF8
    }
} finally {
    if ($null -ne $Process) {
        if (-not $Process.HasExited) {
            $Process.Dispose()
        }
    }
}

