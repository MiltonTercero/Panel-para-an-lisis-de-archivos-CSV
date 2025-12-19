@echo off
REM EDA Panel - Windows Launcher
REM Double-click this file to run the application

cd /d "%~dp0"

REM Check if venv exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    
    echo Installing dependencies...
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
    
    echo Setup complete!
) else (
    call venv\Scripts\activate.bat
)

echo Starting EDA Panel...
python main.py
pause
