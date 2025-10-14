@echo off
echo Installing SehatScan...
echo.

REM Check Python version
python --version 2>nul | findstr /r "3\.1[2-9]\." >nul
if %errorlevel% neq 0 (
    echo Warning: Python 3.12+ is recommended for optimal performance
    echo Current Python version:
    python --version 2>nul || echo Python not found in PATH
    echo.
    echo Please install Python 3.12+ from https://python.org
    echo.
)

REM Check if UV is installed
uv --version >nul 2>&1
if %errorlevel% neq 0 (
    echo UV package manager not found. Installing UV...
    powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
    if %errorlevel% neq 0 (
        echo Failed to install UV. Please install manually from https://docs.astral.sh/uv/
        pause
        exit /b 1
    )
)

echo UV found. Installing dependencies...
uv sync --no-install-project

if %errorlevel% neq 0 (
    echo Failed to install dependencies.
    pause
    exit /b 1
)

echo.
echo SehatScan installation completed successfully!
echo.
echo To run SehatScan:
echo   1. Copy .env.example to .env
echo   2. Add your API keys to .env (see README.md for setup guide)
echo   3. Run: uv run streamlit run app.py
echo.
pause