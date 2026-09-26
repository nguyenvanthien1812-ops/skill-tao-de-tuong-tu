@echo off
chcp 65001 >nul
title KICH HOAT BAN QUYEN - SKILL TAO DE TOAN

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
    echo [!] Chua tim thay Python! Vui long cai Python va tich Add python.exe to PATH.
    pause
    exit /b 1
)

:: Đảm bảo đã có cryptography
%PYTHON_EXE% -c "import cryptography" >nul 2>nul
if %errorlevel% neq 0 (
    echo [*] Dang cai dat thu vien bao mat cryptography...
    %PYTHON_EXE% -m pip install cryptography -q
)

%PYTHON_EXE% "%~dp0scripts\license_manager.py" --activate
echo.
pause
