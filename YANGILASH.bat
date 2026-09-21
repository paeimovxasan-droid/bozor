@echo off
chcp 65001 >nul
title TORTINMANG.UZ - YANGILASH
color 0E
rem O'z papkasiga o'tish (administrator rejimida ham)
cd /d "%~dp0"
echo.
echo  ================================================
echo     TORTINMANG.UZ - ENG YANGI VERSIYAGA O'TISH
echo  ================================================
echo.

where git >nul 2>nul
if errorlevel 1 (
    echo  [XATO] Git topilmadi! https://git-scm.com dan o'rnating,
    echo         yoki quyidagi ikki buyruqni qo'lda yozing:
    echo.
    echo         git fetch origin
    echo         git reset --hard origin/arena/01a09db7-bozor
    pause
    exit /b 1
)

echo  [1/3] GitHub ulanishini tekshirish...
if not exist .git (
    echo         .git yo'q ekan - repository yaratilmoqda...
    git init -q
    git remote add origin https://github.com/paeimovxasan-droid/bozor.git
)
echo  [2/3] Yangi versiya yuklab olinmoqda...
git fetch origin
if errorlevel 1 (
    echo  [XATO] Internet/GitHub muammosi - keyinroq qayta urining.
    pause
    exit /b 1
)

echo  [3/3] Yangilash...
rem .env, state va jurnallar git kuzatmaydi - kalitlaringiz SAQLANADI
git checkout -B arena/01a09db7-bozor origin/arena/01a09db7-bozor
echo.
echo  ================================================
echo   ✅ YANGILANDI!
echo.
echo   Endi START_BOT.bat ni ishga tushiring.
echo   .env kalitlaringiz joyida qoldi - xavotir olmang.
echo  ================================================
echo.
pause
