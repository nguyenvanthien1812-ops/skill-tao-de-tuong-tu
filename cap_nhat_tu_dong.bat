@echo off
chcp 65001 >nul
title Cap Nhat Tu Dong - Skill Tao De Toan ^& Vat Ly

echo.
echo ====================================================================
echo        CẬP NHẬT TỰ ĐỘNG - SKILL TẠO ĐỀ TOÁN ^& VẬT LÝ
echo ====================================================================
echo.

set "PYTHON_EXE="

:: Tìm kiếm Python trên máy
py -c "import sys" >nul 2>nul && set "PYTHON_EXE=py"
if "%PYTHON_EXE%"=="" python -c "import sys" >nul 2>nul && set "PYTHON_EXE=python"
if "%PYTHON_EXE%"=="" (
    for /d %%D in ("%LOCALAPPDATA%\Programs\Python\Python3*") do if exist "%%D\python.exe" set "PYTHON_EXE=%%D\python.exe"
)
if "%PYTHON_EXE%"=="" (
    for /d %%D in ("C:\Program Files\Python3*") do if exist "%%D\python.exe" set "PYTHON_EXE=%%D\python.exe"
)
if "%PYTHON_EXE%"=="" (
    for /d %%D in ("C:\Python3*") do if exist "%%D\python.exe" set "PYTHON_EXE=%%D\python.exe"
)

if "%PYTHON_EXE%"=="" (
    echo [!] Khong tim thay Python tren may!
    echo     Vui long chay file "cai_dat_tu_dong.bat" truoc de cai dat.
    echo.
    pause
    exit /b 1
)

echo [*] Dang kiem tra ban cap nhat moi nhat...
"%PYTHON_EXE%" "%~dp0scripts\updater.py"

echo.
pause
