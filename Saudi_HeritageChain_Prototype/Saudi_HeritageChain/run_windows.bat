@echo off
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel% equ 0 (set "PYTHON=py -3") else (set "PYTHON=python")
if not exist ".venv\Scripts\python.exe" %PYTHON% -m venv .venv
if not exist ".venv\Scripts\python.exe" goto fail
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto fail
".venv\Scripts\python.exe" -m streamlit run app.py
pause
exit /b
:fail
echo Setup failed. Install Python 3.11 or newer and select Add Python to PATH.
pause
