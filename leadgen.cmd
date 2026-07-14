@echo off
REM LeadGen AI — Developed by Gyan Ranjan
REM Global launcher: run "leadgen" from any folder

set "LEADGEN_HOME=%~dp0"
cd /d "%LEADGEN_HOME%"

if not exist "%LEADGEN_HOME%.venv\Scripts\python.exe" (
  echo Creating virtual environment...
  python -m venv "%LEADGEN_HOME%.venv"
  if errorlevel 1 (
    echo Failed to create venv. Is Python installed?
    exit /b 1
  )
  echo Installing dependencies...
  "%LEADGEN_HOME%.venv\Scripts\pip.exe" install -q -r "%LEADGEN_HOME%requirements.txt"
)

REM Load XAI_API_KEY from .env if present and not already set
if not defined XAI_API_KEY if exist "%LEADGEN_HOME%.env" (
  for /f "usebackq tokens=1,* delims==" %%A in ("%LEADGEN_HOME%.env") do (
    if /I "%%A"=="XAI_API_KEY" set "XAI_API_KEY=%%B"
  )
)

REM Pass all args through. No args = interactive chat
if "%~1"=="" (
  "%LEADGEN_HOME%.venv\Scripts\python.exe" "%LEADGEN_HOME%main.py" chat
) else (
  "%LEADGEN_HOME%.venv\Scripts\python.exe" "%LEADGEN_HOME%main.py" %*
)
