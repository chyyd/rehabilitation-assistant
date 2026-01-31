@echo off
echo ========================================
echo   Cleaning up all processes...
echo ========================================
echo.

taskkill /F /IM python.exe 2>nul
taskkill /F /IM node.exe 2>nul
taskkill /F /IM electron.exe 2>nul

echo Waiting for processes to terminate...
timeout /t 2 /nobreak >nul

echo.
echo ========================================
echo   All processes stopped. Ready to restart.
echo ========================================
echo.
echo Please run:
echo   1. Backend:  python main.py
echo   2. Frontend: cd electron-app ^&^& npm run dev
echo.
pause
