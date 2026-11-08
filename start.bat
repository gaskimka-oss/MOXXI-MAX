@echo off
chcp 65001 > nul
title MOXXI 3.0 — Max Messenger Bot (moxximax)
echo ===================================================
echo   Запуск автономного бота MOXXI для Max...
echo ===================================================

if exist "..\бот2.0\venv\Scripts\python.exe" (
    "..\бот2.0\venv\Scripts\python.exe" main.py
) else (
    python main.py
)

pause
