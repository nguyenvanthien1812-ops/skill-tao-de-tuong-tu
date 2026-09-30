@echo off
chcp 65001 >nul
title Cap Nhat Tu Dong - Skill Tao De Toan ^& Vat Ly

echo.
echo ====================================================================
echo        CẬP NHẬT TỰ ĐỘNG - SKILL TẠO ĐỀ TOÁN, LÝ, HÓA
echo ====================================================================
echo.

set "PYTHON_EXE="
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

set "UP_SCRIPT="
if exist "%~dp0scripts\updater.py" (
    set "UP_SCRIPT=%~dp0scripts\updater.py"
) else if exist "%~dp0.agents\skills\tao-de-toan-tuong-tu\scripts\updater.py" (
    set "UP_SCRIPT=%~dp0.agents\skills\tao-de-toan-tuong-tu\scripts\updater.py"
)

if "%UP_SCRIPT%"=="" (
    echo [X] Khong tim thay script updater.py!
    pause
    exit /b 1
)

echo [*] Dang kiem tra ban cap nhat moi nhat...
"%PYTHON_EXE%" "%UP_SCRIPT%"

echo.
pause
