@echo off
REM ============================================================
REM  run.bat  —  Quick Launch Script for Amulya AI
REM ============================================================

title Amulya AI - Voice Assistant

REM Get the directory where this script is located
setlocal enabledelayedexpansion
set "SCRIPT_DIR=%~dp0"

REM Run Python with the virtual environment
echo Starting Amulya AI...
"%SCRIPT_DIR%.venv_new\Scripts\python.exe" "%SCRIPT_DIR%main.py"

REM Keep window open if there's an error
if errorlevel 1 (
    echo.
    echo Error occurred. Press any key to close...
    pause
)
