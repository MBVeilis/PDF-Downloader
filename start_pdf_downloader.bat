@echo off
setlocal

cd /d "%~dp0"

title PDF Downloader

echo ========================================
echo          PDF Downloader
echo ========================================
echo.

if not exist ".venv\Scripts\python.exe" (
    echo ERROR: Python virtual environment was not found.
    echo.
    echo Expected location:
    echo %~dp0.venv\Scripts\python.exe
    echo.
    pause
    exit /b 1
)

if not exist "gui.py" (
    echo ERROR: gui.py was not found in:
    echo %~dp0
    echo.
    pause
    exit /b 1
)

echo Starting PDF Downloader...
echo.

".venv\Scripts\python.exe" "gui.py"

if errorlevel 1 (
    echo.
    echo The application exited with an error.
    pause
)

endlocal