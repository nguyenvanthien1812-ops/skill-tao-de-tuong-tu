@echo off
chcp 65001 >nul
title Cai Dat Tu Dong 1-Click - Skill Tao De Toan, Ly, Hoa

echo.
echo ====================================================================
echo      HỆ THỐNG CÀI ĐẶT TỰ ĐỘNG 1-CLICK - SKILL TẠO ĐỀ TOÁN, LÝ, HÓA
echo ====================================================================
echo.

set "PYTHON_EXE="

:: ─── BƯỚC 1: KIỂM TRA PYTHON CÓ SẴN KHÔNG ───────────────────────────
echo [*] Buoc 1/3: Kiem tra moi truong Python...

:: 1.1 Thử lệnh 'py'
py -c "import sys" >nul 2>nul
if not errorlevel 1 (
    set "PYTHON_EXE=py"
    goto :PYTHON_READY
)

:: 1.2 Thử lệnh 'python' trực tiếp
python -c "import sys" >nul 2>nul
if not errorlevel 1 (
    set "PYTHON_EXE=python"
    goto :PYTHON_READY
)

:: 1.3 Quét tìm trong các thư mục cài đặt phổ biến
for /d %%D in ("%LOCALAPPDATA%\Programs\Python\Python3*") do (
    if exist "%%D\python.exe" (
        "%%D\python.exe" -c "import sys" >nul 2>nul
        if not errorlevel 1 (
            set "PYTHON_EXE=%%D\python.exe"
            set "PATH=%%D;%%D\Scripts;%PATH%"
            goto :PYTHON_READY
        )
    )
)

for /d %%D in ("C:\Program Files\Python3*") do (
    if exist "%%D\python.exe" (
        "%%D\python.exe" -c "import sys" >nul 2>nul
        if not errorlevel 1 (
            set "PYTHON_EXE=%%D\python.exe"
            set "PATH=%%D;%%D\Scripts;%PATH%"
            goto :PYTHON_READY
        )
    )
)

for /d %%D in ("C:\Python3*") do (
    if exist "%%D\python.exe" (
        "%%D\python.exe" -c "import sys" >nul 2>nul
        if not errorlevel 1 (
            set "PYTHON_EXE=%%D\python.exe"
            set "PATH=%%D;%%D\Scripts;%PATH%"
            goto :PYTHON_READY
        )
    )
)

:: ─── BƯỚC 2: NẾU CHƯA CÓ PYTHON -> TỰ ĐỘNG TẢI VÀ CÀI ĐẶT NGẦM ───────
echo.
echo [!] May tinh chua co Python. He thong dang TU DONG TAI VA CAI DAT PYTHON...
echo     (Qua trinh nay dien ra hoan toan tu dong trong khoang 30 - 60 giay)
echo.

set "PY_INSTALLER=%TEMP%\python_installer_auto.exe"
set "PY_URL=https://www.python.org/ftp/python/3.12.6/python-3.12.6-amd64.exe"

echo [*] Dang tai bo cai Python tu trang chu python.org...
if exist "%SystemRoot%\System32\curl.exe" (
    curl.exe -L -o "%PY_INSTALLER%" "%PY_URL%"
) else (
    powershell -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; (New-Object System.Net.WebClient).DownloadFile('%PY_URL%', '%PY_INSTALLER%')"
)

if not exist "%PY_INSTALLER%" (
    echo [X] Khong the tai Python tu dong! Vui long kiem tra ket noi Internet.
    pause
    exit /b 1
)

echo [*] Dang cai dat Python ngam vao may tinh (khong can thao tac gi)...
start /wait "" "%PY_INSTALLER%" /quiet InstallAllUsers=0 PrependPath=1 Include_test=0 Include_pip=1 SimpleInstall=1

del "%PY_INSTALLER%" >nul 2>nul

for /d %%D in ("%LOCALAPPDATA%\Programs\Python\Python3*") do (
    if exist "%%D\python.exe" (
        set "PYTHON_EXE=%%D\python.exe"
        set "PATH=%%D;%%D\Scripts;%PATH%"
        goto :PYTHON_READY
    )
)

py -c "import sys" >nul 2>nul && set "PYTHON_EXE=py"
if "%PYTHON_EXE%"=="" (
    python -c "import sys" >nul 2>nul && set "PYTHON_EXE=python"
)

if "%PYTHON_EXE%"=="" (
    echo [!] Da cai xong nhung can khoi dong lai CMD. Vui long dong va mo lai file nay!
    pause
    exit /b 1
)

:PYTHON_READY
echo [OK] Python da san sang: %PYTHON_EXE%
%PYTHON_EXE% -c "import sys; print(f'     Phien ban: Python {sys.version.split()[0]}')"
echo.

:: ─── BƯỚC 3: TỰ ĐỘNG CÀI ĐẶT CÁC THƯ VIỆN TOÁN, LÝ, HÓA & HÌNH VẼ ────
echo [*] Buoc 2/3: Kiem tra va cai dat day du cac thu vien qua pip...
echo     (matplotlib, scipy, python-docx, lxml, latex2mathml, requests, pillow, openpyxl, cryptography, pymupdf)
echo.

%PYTHON_EXE% -m pip install --upgrade pip --quiet --no-warn-script-location
%PYTHON_EXE% -m pip install matplotlib scipy python-docx lxml latex2mathml requests pillow openpyxl cryptography pymupdf --no-warn-script-location

echo.
echo [OK] Tat ca thu vien da duoc cai dat thanh cong 100%!
echo.

:: ─── BƯỚC 4: TÌM ĐƯỜNG DẪN SCRIPT LICENSE_MANAGER.PY ─────────────────
set "LM_SCRIPT="
if exist "%~dp0scripts\license_manager.py" (
    set "LM_SCRIPT=%~dp0scripts\license_manager.py"
) else if exist "%~dp0.agents\skills\tao-de-toan-tuong-tu\scripts\license_manager.py" (
    set "LM_SCRIPT=%~dp0.agents\skills\tao-de-toan-tuong-tu\scripts\license_manager.py"
)

if "%LM_SCRIPT%"=="" (
    echo [i] Hoan tat cai dat thu vien he thong!
    echo.
    pause
    exit /b 0
)

:: ─── BƯỚC 5: KIỂM TRA BẢN QUYỀN / LICENSE ────────────────────────────
echo [*] Buoc 3/3: Kiem tra ban quyen su dung...
echo.

%PYTHON_EXE% "%LM_SCRIPT%" --check >nul 2>nul
if %errorlevel% equ 0 (
    echo [OK] MAY TINH DA DUOC KICH HOAT BAN QUYEN HOP LE!
    goto :DEPLOY_ANTIGRAVITY
)

:: Nếu chưa kích hoạt bản quyền
echo --------------------------------------------------------------------
echo  CAN KICH HOAT BAN QUYEN DE SU DUNG SKILL
echo --------------------------------------------------------------------
echo.

%PYTHON_EXE% "%LM_SCRIPT%" --machine-id

echo.
echo ====================================================================
echo  HUONG DAN KICH HOAT:
echo   1. Ma may o tren da duoc TU DONG COPY vao Clipboard cua ban.
echo   2. Mo Zalo gui tin nhan cho Tac gia va bam Ctrl + V de gui ma may.
echo   3. Khi nhan duoc ma License Key tu Tac gia:
echo ====================================================================
echo.

set /p "USER_KEY=👉 Dan ma License Key vao day roi bam Enter (hoac Enter de bo qua): "
if not "%USER_KEY%"=="" (
    echo.
    %PYTHON_EXE% "%LM_SCRIPT%" --activate "%USER_KEY%"
    if %errorlevel% equ 0 (
        goto :DEPLOY_ANTIGRAVITY
    )
)

echo.
echo [i] Sau khi co ma License Key tu tac gia, ban chi can:
echo     Nhap dup vao file "KICH_HOAT_BAN_QUYEN.bat" de kich hoat bat cu luc nao.
echo.
pause
exit /b 0

:DEPLOY_ANTIGRAVITY
echo.
echo [*] Dang tu dong nap va dong bo skill vao Google Antigravity...
set "AG_TARGET=%USERPROFILE%\.gemini\config\skills\tao-de-toan-tuong-tu"
if not exist "%AG_TARGET%" mkdir "%AG_TARGET%"
xcopy "%~dp0*" "%AG_TARGET%\" /E /I /Y /Q >nul 2>nul
if exist "%~dp0license.key" copy /Y "%~dp0license.key" "%AG_TARGET%\license.key" >nul 2>nul
if exist "%~dp0license.key" copy /Y "%~dp0license.key" "%USERPROFILE%\.gemini\license.key" >nul 2>nul
if exist "%AG_TARGET%\license.key" copy /Y "%AG_TARGET%\license.key" "%USERPROFILE%\.gemini\license.key" >nul 2>nul

echo.
echo ====================================================================
echo   🎉 [HOAN TAT 100%%] CAI DAT VA DONG BO THANH CONG!
echo.
echo   Moi thu da san sang! Ban chi can mo phan mem Google Antigravity
echo   va nhan tin de tao de thi ngay lap tuc!
echo ====================================================================
echo.
pause
exit /b 0
