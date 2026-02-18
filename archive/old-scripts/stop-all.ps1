# ==========================================
# 康复科助手 - 停止所有服务脚本
# ==========================================

Write-Host ""
Write-Host "╔═══════════════════════════════════════╗" -ForegroundColor Red
Write-Host "║      康复科助手 - 停止所有服务        ║" -ForegroundColor Red
Write-Host "╚═══════════════════════════════════════╝" -ForegroundColor Red
Write-Host ""

# 获取脚本所在目录
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

$BackendStopped = $false
$FrontendStopped = $false

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
Write-Host "🛑 停止所有服务" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
Write-Host ""

# ==================== 停止前端 ====================
Write-Host "📱 [1/2] 停止前端应用..." -ForegroundColor Cyan

$FrontendPidFile = Join-Path $ScriptDir ".frontend.pid"
if (Test-Path $FrontendPidFile) {
    try {
        $ProcessId = Get-Content $FrontendPidFile -Raw
        $ProcessId = $ProcessId.Trim()
        if ($ProcessId -match "^\d+$") {
            $Process = Get-Process -Id $ProcessId -ErrorAction SilentlyContinue
            if ($Process) {
                Stop-Process -Id $ProcessId -Force -ErrorAction Stop
                Write-Host "   ✅ 前端应用已停止 (PID: $ProcessId)" -ForegroundColor Green
                $FrontendStopped = $true
            }
        }
        Remove-Item $FrontendPidFile -Force
    } catch { }
}

if (-not $FrontendStopped) {
    # 查找 Electron 和 Node 进程
    $ElectronProcesses = Get-Process electron -ErrorAction SilentlyContinue
    $NodeProcesses = Get-Process node -ErrorAction SilentlyContinue | Where-Object {
        $_.CommandLine -like "*vite*" -or $_.CommandLine -like "*rehab-assistant*"
    }

    $AllProcesses = @()
    if ($ElectronProcesses) { $AllProcesses += $ElectronProcesses }
    if ($NodeProcesses) { $AllProcesses += $NodeProcesses }

    if ($AllProcesses) {
        foreach ($Process in $AllProcesses) {
            Stop-Process -Id $Process.Id -Force
            $FrontendStopped = $true
        }
        if ($FrontendStopped) {
            Write-Host "   ✅ 前端应用已停止" -ForegroundColor Green
        }
    } else {
        Write-Host "   ⚠️  未找到运行中的前端应用" -ForegroundColor Yellow
    }
}

Write-Host ""

# ==================== 停止后端 ====================
Write-Host "🔧 [2/2] 停止后端服务..." -ForegroundColor Cyan

$BackendPidFile = Join-Path $ScriptDir ".backend.pid"
if (Test-Path $BackendPidFile) {
    try {
        $ProcessId = Get-Content $BackendPidFile -Raw
        $ProcessId = $ProcessId.Trim()
        if ($ProcessId -match "^\d+$") {
            $Process = Get-Process -Id $ProcessId -ErrorAction SilentlyContinue
            if ($Process) {
                Stop-Process -Id $ProcessId -Force -ErrorAction Stop
                Write-Host "   ✅ 后端服务已停止 (PID: $ProcessId)" -ForegroundColor Green
                $BackendStopped = $true
            }
        }
        Remove-Item $BackendPidFile -Force
    } catch { }
}

if (-not $BackendStopped) {
    # 查找 Python uvicorn 进程
    $PythonProcesses = Get-Process python -ErrorAction SilentlyContinue | Where-Object {
        $_.CommandLine -like "*uvicorn*" -or $_.CommandLine -like "*api_main*"
    }

    if ($PythonProcesses) {
        foreach ($Process in $PythonProcesses) {
            Stop-Process -Id $Process.Id -Force
            $BackendStopped = $true
        }
        if ($BackendStopped) {
            Write-Host "   ✅ 后端服务已停止" -ForegroundColor Green
        }
    } else {
        Write-Host "   ⚠️  未找到运行中的后端服务" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray

if ($BackendStopped -or $FrontendStopped) {
    Write-Host "✅ 所有服务已停止!" -ForegroundColor Green
} else {
    Write-Host "ℹ️  没有运行中的服务" -ForegroundColor Gray
}

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
Write-Host ""
Write-Host "按任意键关闭..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

