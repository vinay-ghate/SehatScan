@echo off
echo Starting SehatScan...
echo.

REM Check if .env file exists
if not exist .env (
    echo Warning: .env file not found!
    echo Please copy .env.example to .env and add your API keys.
    echo See README.md for setup instructions.
    echo.
)

echo Ensuring dependencies are installed...
uv sync --no-install-project

echo Starting SehatScan application...
uv run streamlit run app.py

pause