@echo off
REM ===============================================================
REM  Batik Fusion - Quick Launcher
REM  Double-click file ini untuk membuka showcase di browser.
REM ===============================================================

setlocal

REM Cari lokasi script ini sendiri
set "SCRIPT_DIR=%~dp0"
set "SHOWCASE=%SCRIPT_DIR%showcase\index.html"

echo.
echo Membuka Batik Fusion Showcase di browser...
echo Path: %SHOWCASE%
echo.

if not exist "%SHOWCASE%" (
    echo [ERROR] File showcase\index.html tidak ditemukan!
    echo Pastikan folder showcase/ ada di folder yang sama dengan script ini.
    echo.
    pause
    exit /b 1
)

REM Buka dengan browser default
start "" "%SHOWCASE%"

echo Showcase sudah terbuka di browser!
echo.
echo Untuk menutup: tutup tab browser atau tekan Ctrl+C di sini.
echo.
timeout /t 5 >nul