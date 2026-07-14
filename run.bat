@echo off
title LeadGen AI - Developed by Gyan Ranjan
cd /d "%~dp0"
echo.
echo   LeadGen AI
echo   Developed by Gyan Ranjan
echo.
powershell -ExecutionPolicy Bypass -File "%~dp0run.ps1" %*
pause
