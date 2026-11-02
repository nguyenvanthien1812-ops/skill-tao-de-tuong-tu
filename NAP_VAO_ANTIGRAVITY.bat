@echo off
chcp 65001 >nul
title NAP SKILL VAO ANTIGRAVITY

echo.
echo ==============================================================
echo        TỰ ĐỘNG NẠP SKILL VÀO GOOGLE ANTIGRAVITY
echo ==============================================================
echo.

REM Kiem tra ban quyen truoc khi nap
if exist "%~dp0scripts\license_manager.py" (
    python "%~dp0scripts\license_manager.py" --silent-check >nul 2>nul
    if errorlevel 1 (
        echo.
        echo ====================================================================
        echo   [!] MAY CHUA DUOC KICH HOAT BAN QUYEN!
        echo   Vui long chay LAY_MA_MAY.bat gui cho Tac gia, sau do chay
        echo   KICH_HOAT_BAN_QUYEN.bat truoc khi nap vao Antigravity.
        echo ====================================================================
        echo.
        pause
        exit /b 1
    )
)

set "TARGET_DIR=%USERPROFILE%\.gemini\config\skills\tao-de-toan-tuong-tu"

echo [*] Dang tao thu muc skills tren may tinh...
if not exist "%TARGET_DIR%" mkdir "%TARGET_DIR%"

echo [*] Dang sao chep toan bo file skill vao Antigravity (ho tro 100% Unicode tieng Viet)...
powershell -NoProfile -ExecutionPolicy Bypass -Command "$src = (Get-Item -LiteralPath '%~dp0').FullName; $dst = '%TARGET_DIR%'; if (!(Test-Path $dst)) { New-Item -ItemType Directory -Path $dst -Force | Out-Null }; $items = Get-ChildItem -LiteralPath $src | Where-Object { $_.Name -notin @('__pycache__', '.git') } | Select-Object -ExpandProperty FullName; Copy-Item -LiteralPath $items -Destination $dst -Recurse -Force" >nul 2>&1
if %errorlevel% neq 0 (
    python -c "import sys, shutil; from pathlib import Path; src = Path(r'%~dp0'); dst = Path(r'%TARGET_DIR%'); dst.mkdir(parents=True, exist_ok=True); [shutil.copytree(p, dst / p.name, dirs_exist_ok=True) if p.is_dir() else shutil.copy2(p, dst / p.name) for p in src.iterdir() if p.name not in ('__pycache__', '.git')]" >nul 2>&1
    if %errorlevel% neq 0 (
        xcopy "%~dp0*" "%TARGET_DIR%" /E /I /Y /Q >nul 2>&1
    )
)

:: Dong bo license.key hai chieu (ho tro tieng Viet co dau)
powershell -NoProfile -ExecutionPolicy Bypass -Command "$srcLic = Join-Path '%~dp0' 'license.key'; $dstLic = Join-Path '%TARGET_DIR%' 'license.key'; $usrLic = Join-Path $env:USERPROFILE '.gemini\license.key'; if (Test-Path -LiteralPath $srcLic) { Copy-Item -LiteralPath $srcLic -Destination $dstLic -Force -ErrorAction SilentlyContinue; Copy-Item -LiteralPath $srcLic -Destination $usrLic -Force -ErrorAction SilentlyContinue } elseif (Test-Path -LiteralPath $dstLic) { Copy-Item -LiteralPath $dstLic -Destination $srcLic -Force -ErrorAction SilentlyContinue; Copy-Item -LiteralPath $dstLic -Destination $usrLic -Force -ErrorAction SilentlyContinue } elseif (Test-Path -LiteralPath $usrLic) { Copy-Item -LiteralPath $usrLic -Destination $srcLic -Force -ErrorAction SilentlyContinue; Copy-Item -LiteralPath $usrLic -Destination $dstLic -Force -ErrorAction SilentlyContinue }" >nul 2>&1

echo.
echo ==============================================================
echo   ✅ [HOÀN TẤT] ĐÃ NẠP SKILL VÀO ANTIGRAVITY THÀNH CÔNG!
echo.
echo   Bản quyền và thư viện đã được đồng bộ 100%%.
echo   Bây giờ bạn chỉ cần mở phần mềm Google Antigravity lên
echo   và nhắn tin để tạo đề thi ngay!
echo ==============================================================
echo.
pause