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
    echo [!] Chua tim thay Python! Vui long chay cai_dat_tu_dong.bat truoc.
    pause
    exit /b 1
)

set "LM_SCRIPT="
if exist "%~dp0scripts\license_manager.py" (
    set "LM_SCRIPT=%~dp0scripts\license_manager.py"
) else if exist "%~dp0.agents\skills\tao-de-toan-tuong-tu\scripts\license_manager.py" (
    set "LM_SCRIPT=%~dp0.agents\skills\tao-de-toan-tuong-tu\scripts\license_manager.py"
)

if "%LM_SCRIPT%"=="" (
    echo [X] Khong tim thay script license_manager.py!
    pause
    exit /b 1
)

:: Đảm bảo đã có cryptography
%PYTHON_EXE% -c "import cryptography" >nul 2>nul
if %errorlevel% neq 0 (
    echo [*] Dang cai dat thu vien bao mat cryptography...
    %PYTHON_EXE% -m pip install cryptography --quiet
)

%PYTHON_EXE% "%LM_SCRIPT%" --activate
echo.
pause
