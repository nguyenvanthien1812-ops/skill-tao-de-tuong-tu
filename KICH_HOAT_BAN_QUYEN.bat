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
if %errorlevel% equ 0 (
    echo.
    echo [*] Dang tu dong dong bo ban quyen vao Google Antigravity (ho tro 100% Unicode tieng Viet)...
    set "AG_TARGET=%USERPROFILE%\.gemini\config\skills\tao-de-toan-tuong-tu"
    if not exist "%AG_TARGET%" mkdir "%AG_TARGET%"
    powershell -NoProfile -ExecutionPolicy Bypass -Command "$src = (Get-Item -LiteralPath '%~dp0').FullName; $dst = '%AG_TARGET%'; if (!(Test-Path $dst)) { New-Item -ItemType Directory -Path $dst -Force | Out-Null }; $items = Get-ChildItem -LiteralPath $src | Where-Object { $_.Name -notin @('__pycache__', '.git') } | Select-Object -ExpandProperty FullName; Copy-Item -LiteralPath $items -Destination $dst -Recurse -Force" >nul 2>&1
    powershell -NoProfile -ExecutionPolicy Bypass -Command "$srcLic = Join-Path '%~dp0' 'license.key'; $dstLic = Join-Path '%AG_TARGET%' 'license.key'; $usrLic = Join-Path $env:USERPROFILE '.gemini\license.key'; if (Test-Path -LiteralPath $srcLic) { Copy-Item -LiteralPath $srcLic -Destination $dstLic -Force -ErrorAction SilentlyContinue; Copy-Item -LiteralPath $srcLic -Destination $usrLic -Force -ErrorAction SilentlyContinue } elseif (Test-Path -LiteralPath $dstLic) { Copy-Item -LiteralPath $dstLic -Destination $srcLic -Force -ErrorAction SilentlyContinue; Copy-Item -LiteralPath $dstLic -Destination $usrLic -Force -ErrorAction SilentlyContinue }" >nul 2>&1
    echo [OK] Da dong bo vao Antigravity! Ban co the bat dau dung ngay.
)
echo.
pause