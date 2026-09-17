@echo off
chcp 65001 >nul
title TORTINMANG.UZ v2.0 - ORNATISH
color 0A
rem MUHIM: qayerdan ishga tushirilganidan qat'iy o'z papkasiga o'tish
cd /d "%~dp0"
echo.
echo  ================================================
echo     TORTINMANG.UZ v2.0 - ORNATISH (avtomatik)
echo  ================================================
echo.

where python >nul 2>nul
if errorlevel 1 (
    echo  [XATO] Python topilmadi!
    echo         https://python.org dan yuklab oling.
    echo         O'rnatishda "Add Python to PATH" ni BELGILANG!
    echo.
    pause
    exit /b 1
)

echo  [1/5] Python tekshirildi:
python --version
echo.

echo  [2/5] Virtual muhit yaratilmoqda...
if not exist .venv (
    python -m venv .venv
)
echo         OK
echo.

echo  [3/5] Kutubxonalar o'rnatilmoqda (bir necha daqiqa kuting)...
if not exist requirements.txt (
    echo  [XATO] requirements.txt topilmadi - papka to'liq ko'chirilmagan!
    echo         git pull qiling va ORNATISH.bat ni qayta ishga tushiring.
    pause
    exit /b 1
)
call .venv\Scripts\python.exe -m pip install --upgrade pip -q
call .venv\Scripts\python.exe -m pip install -r requirements.txt -q
if errorlevel 1 (
    echo  [XATO] Kutubxonalar o'rnatilmadi - internetni tekshiring,
    echo         so'ng ORNATISH.bat ni QAYTA ishga tushiring.
    pause
    exit /b 1
)
echo         Asosiy kutubxonalar OK
call .venv\Scripts\python.exe -m pip install MetaTrader5 -q
if errorlevel 1 (
    echo         [!] MetaTrader5 o'rnatilmadi - bot paper rejimda ishlaydi
) else (
    echo         MetaTrader5 OK
)
echo.

echo  [4/5] .env fayli tekshirilmoqda...
if not exist .env (
    copy .env.example .env >nul
    echo         .env YARATILDI.
    echo         !! MUHIM: notepad .env bilan ochib, DeepSeek va Telegram
    echo            kalitlarini kiriting, so'ng qayta saqlang.
) else (
    echo         .env mavjud - OK
)
echo.

echo  [5/5] Self-test ishga tushirilmoqda...
call .venv\Scripts\python.exe run_v2.py --test
echo.

echo  ================================================
echo   ORNATISH TUGADI!
echo.
echo   Keyingi qadam:  START_BOT.bat  (botni ishga tushirish)
echo   Tekshirish:     TEST_BOT.bat
echo   Backtest:       BACKTEST.bat
echo  ================================================
echo.
pause
