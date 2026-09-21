@echo off
chcp 65001 >nul
title TORTINMANG.UZ v2.0 - TEST
color 0E
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe (
    echo  [!] Avval ORNATISH.bat ni ishga tushiring!
    pause
    exit /b 1
)
call .venv\Scripts\python.exe run_v2.py --test
echo.
pause
