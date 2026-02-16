@echo off
chcp 65001 >nul
echo.
echo ========================================
echo   Rehab Assistant - Start Menu
echo ========================================
echo.
echo [1] Start All (Backend + Electron)
echo [2] Start Backend Only
echo [3] Start Frontend (Electron App)
echo [4] Start Frontend (Web Browser)
echo [5] Stop All Services
echo [0] Exit
echo.
set /p choice=Select option (0-5):

if "%choice%"=="1" goto startall
if "%choice%"=="2" goto startbackend
if "%choice%"=="3" goto startfrontend
if "%choice%"=="4" goto startweb
if "%choice%"=="5" goto stopall
if "%choice%"=="0" goto end
goto invalid

:startall
cls
echo.
echo Starting all services (Backend + Electron)...
echo.
powershell.exe -ExecutionPolicy Bypass -File "%~dp0start-all.ps1"
goto end

:startbackend
cls
echo.
echo Starting backend service...
echo Backend API: http://127.0.0.1:8000
echo.
powershell.exe -ExecutionPolicy Bypass -File "%~dp0start-backend.ps1"
pause
goto end

:startfrontend
cls
echo.
echo Starting Electron frontend...
echo.
powershell.exe -ExecutionPolicy Bypass -File "%~dp0start-frontend.ps1"
goto end

:startweb
cls
echo.
echo Starting Web Frontend Server...
echo Access URL: http://localhost:5173/
echo.
powershell.exe -ExecutionPolicy Bypass -File "%~dp0start-web-frontend.ps1"
goto end

:stopall
cls
echo.
echo Stopping all services...
echo.
powershell.exe -ExecutionPolicy Bypass -File "%~dp0stop-all.ps1"
goto end

:invalid
cls
echo.
echo Invalid option!
pause
goto end

:end
