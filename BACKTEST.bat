@echo off
chcp 65001 >nul
title TORTINMANG.UZ v2.0 - BACKTEST
color 0D
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe (
    echo  [!] Avval ORNATISH.bat ni ishga tushiring!
    pause
    exit /b 1
)
rem Standart: XAUUSD+ETHUSD, oxirgi 30 kun.
rem O'zgartirish: python run_v2.py --backtest --days 90 --symbols XAUUSD
call .venv\Scripts\python.exe run_v2.py --backtest --days 30
echo.
pause
