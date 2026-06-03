@echo off
echo ==========================================
echo Starting AI Resume Analyzer...
echo ==========================================

REM Check if Python is installed
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Error: Python is not installed or not in PATH. Please install Python.
    pause
    exit /b
)

REM Check if venv exists, if not create it
if not exist "venv\Scripts\activate.bat" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate venv
echo Activating virtual environment...
call venv\Scripts\activate

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Run the app
echo Starting the server...
echo Please open http://127.0.0.1:5000 in your browser!
python app.py

pause
