# Test Start Script
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

Write-Host "Starting backend..." -ForegroundColor Green

# Start backend in hidden window
$ProcessInfo = New-Object System.Diagnostics.ProcessStartInfo
$ProcessInfo.FileName = "python"
$ProcessInfo.Arguments = "-m uvicorn backend.api_main:app --host 127.0.0.1 --port 8000"
$ProcessInfo.WorkingDirectory = $ScriptDir
$ProcessInfo.UseShellExecute = $false
$ProcessInfo.RedirectStandardOutput = $true
$ProcessInfo.RedirectStandardError = $true
$ProcessInfo.CreateNoWindow = $true

$Process = New-Object System.Diagnostics.Process
$Process.StartInfo = $ProcessInfo

try {
    $Process.Start() | Out-Null
    $ProcessId = $Process.Id

    Start-Sleep -Seconds 3

    if ($Process.HasExited) {
        Write-Host "Failed to start" -ForegroundColor Red
        $ErrorText = $Process.StandardError.ReadToEnd()
        Write-Host $ErrorText
    } else {
        Write-Host "Backend started successfully!" -ForegroundColor Green
        Write-Host "PID: $ProcessId"
        $ProcessId | Out-File -FilePath ".backend.pid" -Encoding UTF8
    }
} finally {
    if ($null -ne $Process -and -not $Process.HasExited) {
        $Process.Dispose()
    }
}

Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
