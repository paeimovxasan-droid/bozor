@echo off
chcp 65001 >nul
title TORTINMANG.UZ v2.0 - BOT ISHLAMOQDA
color 0B
cd /d "%~dp0"

if not exist .venv\Scripts\python.exe (
    echo  [!] Avval ORNATISH.bat ni ishga tushiring!
    pause
    exit /b 1
)

echo  TORTINMANG.UZ v2.0 ishga tushmoqda...
echo  To'xtatish uchun: Ctrl+C
echo.
call .venv\Scripts\python.exe run_v2.py
echo.
pause
