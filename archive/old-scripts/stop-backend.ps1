# ==========================================
# 康复科助手 - 后端服务停止脚本
# ==========================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  停止后端服务" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 获取脚本所在目录
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

$ProcessIdFile = Join-Path $ScriptDir ".backend.pid"
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
                Write-Host "✅ 后端服务已停止" -ForegroundColor Green
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

# 方法2: 通过进程名查找
if (-not $Stopped) {
    Write-Host "🔍 搜索正在运行的后端进程..." -ForegroundColor Yellow

    $PythonProcesses = Get-Process python -ErrorAction SilentlyContinue | Where-Object {
        $_.CommandLine -like "*uvicorn*" -or $_.CommandLine -like "*api_main*"
    }

    if ($PythonProcesses) {
        foreach ($Process in $PythonProcesses) {
            Write-Host "🛑 停止进程 (PID: $($Process.Id))" -ForegroundColor Yellow
            Stop-Process -Id $Process.Id -Force
            $Stopped = $true
        }

        if ($Stopped) {
            Write-Host "✅ 后端服务已停止" -ForegroundColor Green
        }
    } else {
        Write-Host "⚠️  未找到运行中的后端服务" -ForegroundColor Yellow
    }
}

Write-Host ""

# 清理可能存在的 PID 文件
if (Test-Path $ProcessIdFile) {
    Remove-Item $ProcessIdFile -Force
}

# 额外检查: 杀死所有相关的 Python 进程（谨慎）
if (-not $Stopped) {
    Write-Host "💡 提示: 如果服务仍在运行，可以手动检查任务管理器" -ForegroundColor Gray
}

Write-Host ""
if ($Stopped) {
    Write-Host "✅ 完成!" -ForegroundColor Green
} else {
    Write-Host "ℹ️  没有需要停止的服务" -ForegroundColor Gray
}
Write-Host ""
Write-Host "按任意键关闭..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

