@echo off
echo Stopping Rehab Assistant System...
echo.

taskkill /F /IM python.exe >nul 2>&1
if %errorlevel% equ 0 (
    echo Backend services stopped
) else (
    echo No backend services found
)

taskkill /F /IM node.exe >nul 2>&1
if %errorlevel% equ 0 (
    echo Frontend services stopped
) else (
    echo No frontend services found
)

echo.
echo All services stopped
pause
