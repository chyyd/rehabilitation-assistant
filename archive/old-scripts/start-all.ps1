# ==========================================
# 康复科助手 - 一键启动脚本 (生产环境)
# ==========================================

Write-Host ""
Write-Host "╔═══════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║      康复科助手 - 一键启动            ║" -ForegroundColor Cyan
Write-Host "║      Rehabilitation Assistant         ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# 获取脚本所在目录
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

Write-Host "📋 启动清单:" -ForegroundColor White
Write-Host "  ✓ 后端 API 服务 (隐藏窗口)" -ForegroundColor Gray
Write-Host "  ✓ 前端 Electron 应用" -ForegroundColor Gray
Write-Host ""

# ==================== 启动后端 ====================
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
Write-Host "📦 [1/2] 启动后端服务..." -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray

$BackendScript = Join-Path $ScriptDir "start-backend.ps1"
if (Test-Path $BackendScript) {
    # 使用隐藏窗口启动后端
    $ProcessInfo = New-Object System.Diagnostics.ProcessStartInfo
    $ProcessInfo.FileName = "powershell.exe"
    $ProcessInfo.Arguments = "-ExecutionPolicy Bypass -WindowStyle Hidden -File `"$BackendScript`""
    $ProcessInfo.UseShellExecute = $false
    $ProcessInfo.CreateNoWindow = $true

    $BackendProcess = [System.Diagnostics.Process]::Start($ProcessInfo)
    Write-Host "✅ 后端服务启动中..." -ForegroundColor Green
    Start-Sleep -Seconds 3
} else {
    Write-Host "❌ 找不到 start-backend.ps1" -ForegroundColor Red
    pause
    exit 1
}

# 检查后端是否启动成功
Write-Host ""
Write-Host "🔍 检查后端服务状态..." -ForegroundColor Yellow
$BackendRunning = $false
for ($i = 1; $i -le 5; $i++) {
    try {
        $response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/docs" -Method HEAD -TimeoutSec 2 -UseBasicProgramming
        $BackendRunning = $true
        break
    } catch {
        Write-Host "   等待后端启动... ($i/5)" -ForegroundColor Gray
        Start-Sleep -Seconds 1
    }
}

if ($BackendRunning) {
    Write-Host "✅ 后端服务运行正常" -ForegroundColor Green
    Write-Host "   📍 地址: http://127.0.0.1:8000" -ForegroundColor Gray
} else {
    Write-Host "⚠️  后端服务可能未正常启动，但继续启动前端..." -ForegroundColor Yellow
}

Write-Host ""

# ==================== 启动前端 ====================
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
Write-Host "🖥️  [2/2] 启动前端应用..." -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray

$FrontendScript = Join-Path $ScriptDir "start-frontend.ps1"
if (Test-Path $FrontendScript) {
    Start-Process powershell -ArgumentList "-ExecutionPolicy Bypass -File `"$FrontendScript`""
} else {
    Write-Host "❌ 找不到 start-frontend.ps1" -ForegroundColor Red
    pause
    exit 1
}

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
Write-Host "✅ 启动完成!" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
Write-Host ""

Write-Host "📊 服务状态:" -ForegroundColor White
Write-Host "  • 后端服务: 在后台运行" -ForegroundColor Gray
Write-Host "  • 前端应用: Electron 窗口应该已打开" -ForegroundColor Gray
Write-Host ""

Write-Host "🔧 管理命令:" -ForegroundColor White
Write-Host "  • 停止后端: .\stop-backend.ps1" -ForegroundColor Gray
Write-Host "  • 停止前端: .\stop-frontend.ps1" -ForegroundColor Gray
Write-Host "  • 停止全部: .\stop-all.ps1" -ForegroundColor Gray
Write-Host ""

Write-Host "💡 提示:" -ForegroundColor Yellow
Write-Host "  • 此启动窗口可以关闭，不影响应用运行" -ForegroundColor Gray
Write-Host "  • 后端服务完全隐藏在后台运行" -ForegroundColor Gray
Write-Host ""

Write-Host "按任意键关闭此窗口..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

