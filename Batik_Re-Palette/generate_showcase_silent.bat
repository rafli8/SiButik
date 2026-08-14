@echo off
REM ===============================================================
REM  Batik Fusion - Showcase Generator (Windows, tanpa terminal)
REM  File ini men-generate showcase HTML statis yang siap dibuka
REM  di browser, tanpa perlu install library ML apapun.
REM
REM  Cara pakai: double-click file ini.
REM  Hasil: buka folder showcase/ lalu double-click index.html
REM ===============================================================

setlocal enabledelayedexpansion
chcp 65001 >nul

echo.
echo ========================================================
echo   BATIK FUSION - GENERATE SHOWCASE STATIS
echo ========================================================
echo.

REM Cari Python
where python >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python tidak ditemukan!
    echo.
    echo Silakan install Python terlebih dahulu:
    echo   1. Buka https://www.python.org/downloads/
    echo   2. Download Python 3.10 atau lebih baru
    echo   3. JALANKAN INSTALLER DAN CENTANG "Add Python to PATH"!
    echo   4. Setelah install, JALANKAN FILE INI LAGI
    echo.
    pause
    exit /b 1
)

echo [1/4] Python ditemukan:
python --version
echo.

REM Install Pillow + numpy (minimum)
echo [2/4] Install Pillow + numpy (abaikan jika sudah terinstall)...
python -m pip install --quiet Pillow numpy 2>nul
echo       selesai.
echo.

REM Generate showcase (mode sintetis, tanpa GPU)
echo [3/4] Generate gambar fusion + narasi...
echo.
python generate_showcase.py
if errorlevel 1 (
    echo.
    echo [ERROR] Gagal generate showcase!
    pause
    exit /b 1
)
echo.

REM Generate HTML gallery
echo [4/4] Generate HTML gallery...
python generate_index_html.py
if errorlevel 1 (
    echo.
    echo [ERROR] Gagal generate HTML gallery!
    pause
    exit /b 1
)
echo.

echo ========================================================
echo   SELESAI!
echo ========================================================
echo.
echo Showcase sudah siap di folder:
echo   %CD%\showcase\
echo.
echo CARA BUKA:
echo   1. Buka File Explorer
echo   2. Masuk folder showcase/
echo   3. Double-click file "index.html"
echo   4. Browser akan otomatis terbuka menampilkan gallery
echo.
echo Atau buka langsung dari terminal:
echo   explorer "%CD%\showcase\index.html"
echo.
echo Untuk share ke internet, lihat PANDUAN_STATIC.md
echo atau PANDUAN_LOKAL.md di folder ini.
echo.
pause
