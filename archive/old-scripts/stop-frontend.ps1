# ==========================================
# 康复科助手 - 前端应用停止脚本
# ==========================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  停止前端应用" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 获取脚本所在目录
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProcessIdFile = Join-Path $ScriptDir ".frontend.pid"

$Stopped = $false

# 方法1: 从 PID 文件读取
if (Test-Path $ProcessIdFile) {
    try {
        $SavedPid = Get-Content $ProcessIdFile -Raw
        $SavedPid = $SavedPid.Trim()

        if ($SavedPid -match "^\d+$") {
            $Process = Get-Process -Id $SavedPid -ErrorAction SilentlyContinue
            if ($Process) {
                Write-Host "🔍 找到保存的进程 (PID: $SavedPid)" -ForegroundColor Yellow
                Stop-Process -Id $SavedPid -Force -ErrorAction Stop
                Write-Host "✅ 前端应用已停止" -ForegroundColor Green
                $Stopped = $true
            } else {
                Write-Host "⚠️  保存的进程不存在 (PID: $SavedPid)" -ForegroundColor Yellow
            }
        }
        Remove-Item $ProcessIdFile -Force
    } catch {
        Write-Host "⚠️  无法停止保存的进程: $_" -ForegroundColor Yellow
    }
}

# 方法2: 查找 Electron 和 Node 进程
if (-not $Stopped) {
    Write-Host "🔍 搜索正在运行的前端进程..." -ForegroundColor Yellow

    # 查找 Electron 进程
    $ElectronProcesses = Get-Process electron -ErrorAction SilentlyContinue
    # 查找 Node 进程（vite 开发服务器）
    $NodeProcesses = Get-Process node -ErrorAction SilentlyContinue | Where-Object {
        $_.CommandLine -like "*vite*" -or $_.CommandLine -like "*rehab-assistant*"
    }

    $AllProcesses = @()
    if ($ElectronProcesses) { $AllProcesses += $ElectronProcesses }
    if ($NodeProcesses) { $AllProcesses += $NodeProcesses }

    if ($AllProcesses) {
        foreach ($Process in $AllProcesses) {
            Write-Host "🛑 停止进程 $($Process.ProcessName) (PID: $($Process.Id))" -ForegroundColor Yellow
            Stop-Process -Id $Process.Id -Force
            $Stopped = $true
        }

        if ($Stopped) {
            Write-Host "✅ 前端应用已停止" -ForegroundColor Green
        }
    } else {
        Write-Host "⚠️  未找到运行中的前端应用" -ForegroundColor Yellow
    }
}

Write-Host ""

# 清理 PID 文件
if (Test-Path $ProcessIdFile) {
    Remove-Item $ProcessIdFile -Force
}

Write-Host ""
if ($Stopped) {
    Write-Host "✅ 完成!" -ForegroundColor Green
} else {
    Write-Host "ℹ️  没有需要停止的应用" -ForegroundColor Gray
}
Write-Host ""
Write-Host "按任意键关闭..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

