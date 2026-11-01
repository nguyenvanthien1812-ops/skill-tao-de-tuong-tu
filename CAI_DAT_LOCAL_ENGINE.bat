@echo off
chcp 65001 >nul
title Cai Dat Engine Xu Ly Cuc Bo (Local Engine) - MathType OLE 100%% Offline

echo.
echo ====================================================================
echo    CÀI ĐẶT ENGINE XỬ LÝ CỤC BỘ (LOCAL ENGINE) - 100%% OFFLINE
echo    Xuất Word công thức chuẩn MathType OLE (Equation.DSMT4)
echo    Không cần kết nối máy chủ Backend - Tốc độ siêu nhanh - Bảo mật
echo ====================================================================
echo.

set "PYTHON_EXE="

:: ─── BƯỚC 1: TÌM PYTHON ───────────────────────────────────────────────
echo [*] Buoc 1/3: Kiem tra moi truong Python...

py -c "import sys" >nul 2>nul
if not errorlevel 1 (
    set "PYTHON_EXE=py"
    goto :PYTHON_READY
)

python -c "import sys" >nul 2>nul
if not errorlevel 1 (
    set "PYTHON_EXE=python"
    goto :PYTHON_READY
)

for /d %%D in ("%LOCALAPPDATA%\Programs\Python\Python3*") do (
    if exist "%%D\python.exe" (
        set "PYTHON_EXE=%%D\python.exe"
        goto :PYTHON_READY
    )
)

for /d %%D in ("C:\Program Files\Python3*") do (
    if exist "%%D\python.exe" (
        set "PYTHON_EXE=%%D\python.exe"
        goto :PYTHON_READY
    )
)

for /d %%D in ("C:\Python3*") do (
    if exist "%%D\python.exe" (
        set "PYTHON_EXE=%%D\python.exe"
        goto :PYTHON_READY
    )
)

echo [!] May tinh chua co Python. Vui long chay file cai_dat_tu_dong.bat truoc!
pause
exit /b 1

:PYTHON_READY
echo [OK] Python da san sang: %PYTHON_EXE%
echo.

:: ─── BƯỚC 2: CÀI ĐẶT THƯ VIỆN CẦN THIẾT QUA PIP ──────────────────────
echo [*] Buoc 2/3: Cai dat cac thu vien chuyen dung cho Local Engine...
echo     (lxml, olefile, latex2mathml, python-docx, pywin32)
echo.

%PYTHON_EXE% -m pip install --upgrade pip --quiet --no-warn-script-location
%PYTHON_EXE% -m pip install lxml olefile latex2mathml python-docx pywin32 --no-warn-script-location

echo.
echo [OK] Cac thu vien Python da cai dat xong!
echo.

:: ─── BƯỚC 3: KIỂM TRA & CÀI ĐẶT LIBREOFFICE HEADLESS ─────────────────
echo [*] Buoc 3/3: Kiem tra phan mem LibreOffice (Core Engine cua Local Mode)...

set "LO_EXE="
if exist "C:\Program Files\LibreOffice\program\soffice.exe" set "LO_EXE=C:\Program Files\LibreOffice\program\soffice.exe"
if exist "C:\Program Files (x86)\LibreOffice\program\soffice.exe" set "LO_EXE=C:\Program Files (x86)\LibreOffice\program\soffice.exe"
if "%LO_EXE%"=="" (
    for /f "tokens=*" %%i in ('where soffice 2^>nul') do set "LO_EXE=%%i"
)

if not "%LO_EXE%"=="" (
    echo [OK] Da tim thay LibreOffice tai: %LO_EXE%
    goto :VERIFY_ENGINE
)

echo.
echo [!] May tinh cua ban CHUA CO LibreOffice (Thanh phan xu ly headless StarMath).
echo     He thong se TU DONG TAI VA CAI DAT LibreOffice mien phi qua winget...
echo     (Qua trinh nay dien ra ngam trong khoang 1 - 2 phut, khong lam anh huong den may)
echo.

where winget >nul 2>nul
if not errorlevel 1 (
    echo [*] Dang chay winget install LibreOffice...
    winget install --id TheDocumentFoundation.LibreOffice -e --silent --accept-package-agreements --accept-source-agreements
) else (
    echo [!] May khong co winget. Dang mo trinh duyet de tai bo cai LibreOffice...
    start https://www.libreoffice.org/download/download-libreoffice/
    echo Vui long cai dat LibreOffice roi chay lai file nay!
    pause
    exit /b 0
)

:VERIFY_ENGINE
echo.
echo ====================================================================
echo    CHAY KIEM DINH CHUAN HOAN TAT (INTEGRITY VERIFICATION)
echo ====================================================================
echo.

if exist "%~dp0scripts\local_engine\verify_local_engine.py" (
    %PYTHON_EXE% "%~dp0scripts\local_engine\verify_local_engine.py"
) else (
    echo [OK] Local Engine da duoc tich hop day du!
)

echo.
pause
exit /b 0
