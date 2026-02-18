$files = @(
    "start-backend.ps1",
    "start-frontend.ps1",
    "stop-backend.ps1",
    "stop-frontend.ps1",
    "stop-all.ps1",
    "start-all.ps1"
)

foreach ($file in $files) {
    if (Test-Path $file) {
        $content = Get-Content $file -Raw -Encoding UTF8
        $newContent = $content -replace '\$Pid', '$ProcessId'
        Set-Content $file -Value $newContent -Encoding UTF8
        Write-Host "Fixed: $file"
    }
}
