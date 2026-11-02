@echo off
chcp 65001 >nul
setlocal EnableExtensions
title Cai Dat Local Engine - MathType OLE 100%% Offline

echo.
echo ====================================================================
echo    CAI DAT ENGINE XU LY CUC BO (LOCAL ENGINE) - 100%% OFFLINE
echo    Xuat Word cong thuc chuan MathType OLE (Equation.DSMT4)
echo    Khong can may chu Backend - Nhanh - Bao mat
echo ====================================================================
echo.

set "PYTHON_EXE="

:: ---------------- BUOC 1: TIM PYTHON ----------------
echo [*] Buoc 1/4: Kiem tra Python...
py -c "import sys" >nul 2>nul
if not errorlevel 1 set "PYTHON_EXE=py"
if defined PYTHON_EXE goto :PYTHON_READY

python -c "import sys" >nul 2>nul
if not errorlevel 1 set "PYTHON_EXE=python"
if defined PYTHON_EXE goto :PYTHON_READY

for /d %%D in ("%LOCALAPPDATA%\Programs\Python\Python3*") do if exist "%%~D\python.exe" set "PYTHON_EXE=%%~D\python.exe"
if defined PYTHON_EXE goto :PYTHON_READY
for /d %%D in ("%ProgramFiles%\Python3*") do if exist "%%~D\python.exe" set "PYTHON_EXE=%%~D\python.exe"
if defined PYTHON_EXE goto :PYTHON_READY
for /d %%D in ("C:\Python3*") do if exist "%%~D\python.exe" set "PYTHON_EXE=%%~D\python.exe"
if defined PYTHON_EXE goto :PYTHON_READY

echo [!] May tinh chua co Python.
echo     Vui long chay file cai_dat_tu_dong.bat truoc, sau do chay lai file nay.
echo.
pause
exit /b 1

:PYTHON_READY
echo [OK] Python: "%PYTHON_EXE%"
echo.

:: ---------------- BUOC 1.5: KIEM TRA BAN QUYEN ----------------
echo [*] Kiem tra ban quyen hop le...
"%PYTHON_EXE%" "%~dp0scripts\license_manager.py" --silent-check >nul 2>nul
if errorlevel 1 (
    echo.
    echo ====================================================================
    echo   [!] MAY TINH CHUA KICH HOAT BAN QUYEN HOAC LICENSE DANG DUNG CHO MAY KHAC!
    echo ====================================================================
    echo   Quy Thay/Co vui long chay file LAY_MA_MAY.bat de lay ma may gui cho Tac gia,
    echo   sau do chay KICH_HOAT_BAN_QUYEN.bat de dan ma kich hoat.
    echo ====================================================================
    echo.
    pause
    exit /b 1
)
echo [OK] Ban quyen hop le!
echo.

:: ---------------- BUOC 2: THU VIEN PYTHON ----------------
echo [*] Buoc 2/4: Cai thu vien cho Local Engine (lxml, olefile, latex2mathml, python-docx, pywin32)...
"%PYTHON_EXE%" -m pip install --upgrade pip --quiet --no-warn-script-location
"%PYTHON_EXE%" -m pip install lxml olefile latex2mathml python-docx pywin32 --no-warn-script-location
if errorlevel 1 goto :PIP_FAILED
echo [OK] Thu vien Python da san sang.
echo.
goto :CHECK_LO

:PIP_FAILED
echo.
echo [!] Cai thu vien qua pip chua thanh cong. Vui long kiem tra mang Internet
echo     roi chay lai file nay.
echo.
pause
exit /b 1

:: ---------------- BUOC 3: LIBREOFFICE ----------------
:CHECK_LO
echo [*] Buoc 3/4: Kiem tra LibreOffice (loi xu ly cua Local Engine)...
call :FIND_LO
if defined LO_EXE goto :LO_FOUND

echo.
echo [!] May chua co LibreOffice (mien phi). He thong se tu dong tai va cai dat.
echo     Neu Windows hoi quyen quan tri, Thay/Co bam "Yes" de cho phep.
echo     Qua trinh mat khoang 2 - 5 phut tuy toc do mang.
echo.

where winget >nul 2>nul
if errorlevel 1 goto :NO_WINGET

winget install --id TheDocumentFoundation.LibreOffice -e --silent --accept-package-agreements --accept-source-agreements
call :FIND_LO
if defined LO_EXE goto :LO_FOUND

echo.
echo [!] Chua cai duoc LibreOffice tu dong.
goto :NO_WINGET

:NO_WINGET
echo.
echo [!] Vui long tai LibreOffice tai trang: https://www.libreoffice.org/download/
echo     Cai dat binh thuong (Next - Next - Install), sau do chay lai file nay.
start "" "https://www.libreoffice.org/download/download-libreoffice/"
echo.
echo [i] Trong luc chua co LibreOffice, Skill van xuat MathType OLE qua may chu
echo     Cloud du phong (can mang Internet).
echo.
pause
exit /b 0

:LO_FOUND
echo [OK] LibreOffice: "%LO_EXE%"
echo.

:: ---------------- BUOC 4: KIEM DINH ----------------
echo [*] Buoc 4/4: Chay thu chuyen doi cong thuc mau sang MathType OLE...
echo.
if not exist "%~dp0scripts\local_engine\verify_local_engine.py" goto :NO_ENGINE_FILES
"%PYTHON_EXE%" "%~dp0scripts\local_engine\verify_local_engine.py"
if errorlevel 1 goto :VERIFY_FAILED

echo.
echo ====================================================================
echo   [HOAN TAT] LOCAL ENGINE DA SAN SANG 100%%!
echo   Tu nay Skill se uu tien xuat MathType OLE ngay tren may (Offline).
echo ====================================================================
echo.
pause
exit /b 0

:VERIFY_FAILED
echo.
echo [!] Kiem dinh chua dat. Skill van hoat dong qua may chu Cloud du phong.
echo     Thay/Co hay chup man hinh nay gui tac gia de duoc ho tro.
echo.
pause
exit /b 1

:NO_ENGINE_FILES
echo [!] Khong tim thay thu muc scripts\local_engine trong Skill.
echo     Vui long chay cap_nhat_tu_dong.bat de tai ban moi nhat.
echo.
pause
exit /b 1

:: ---------------- HAM TIM LIBREOFFICE ----------------
:FIND_LO
set "LO_EXE="
if exist "%ProgramFiles%\LibreOffice\program\soffice.exe" set "LO_EXE=%ProgramFiles%\LibreOffice\program\soffice.exe"
if defined LO_EXE exit /b 0
if exist "%ProgramFiles(x86)%\LibreOffice\program\soffice.exe" set "LO_EXE=%ProgramFiles(x86)%\LibreOffice\program\soffice.exe"
if defined LO_EXE exit /b 0
for /f "delims=" %%i in ('where soffice 2^>nul') do if not defined LO_EXE set "LO_EXE=%%i"
exit /b 0
