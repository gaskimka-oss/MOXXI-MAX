@echo off
chcp 65001 > nul
title MOXXI 3.0 — Max Messenger Bot (moxximax)
echo ===================================================
echo   Запуск автономного бота MOXXI для Max...
echo   Авто-перезапуск при сбоях ВКЛЮЧЕН!
echo ===================================================

set PYTHON_EXE=..\бот2.0\venv\Scripts\python.exe
if not exist "%PYTHON_EXE%" (
    set PYTHON_EXE=C:\Users\eiema\OneDrive\Desktop\бот2.0\venv\Scripts\python.exe
)

:loop
echo [%date% %time%] Запуск процесса MOXXI Max...
"%PYTHON_EXE%" main.py
echo.
echo [!] MOXXI Max завершился или произошел сетевой сбой (%date% %time%).
echo [!] Автоматический перезапуск через 5 секунд... (Ctrl+C для остановки)
timeout /t 5 > nul
goto loop
