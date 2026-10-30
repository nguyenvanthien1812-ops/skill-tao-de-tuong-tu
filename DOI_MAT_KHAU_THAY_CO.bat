@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
title Doi Mat Khau Che Do Thay Co (1-Click) - Video Tuong Tac E-Learning

echo.
echo ====================================================================
echo   🔐 CÔNG CỤ ĐỔI MẬT KHẨU CHẾ ĐỘ THẦY CÔ (1-CLICK)
echo   Dành cho bài giảng Video Tương Tác E-Learning
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
    echo [!] Không tìm thấy Python trên máy tính! Vui lòng chạy 1_CAI_DAT_MOI_TRUONG.bat trước.
    pause
    exit /b 1
)

set "TARGET_PATH=%~1"
if not "%TARGET_PATH%"=="" goto :ASK_PWD

echo 👉 CÁCH DÙNG NHANH:
echo    Thầy/Cô kéo thả trực tiếp THƯ MỤC bài giảng (hoặc file index.html)
echo    vào biểu tượng file DOI_MAT_KHAU_THAY_CO.bat này, hoặc dán đường dẫn ở dưới:
echo.
set /p "TARGET_PATH=📂 Dán đường dẫn thư mục bài giảng (hoặc file index.html): "

:ASK_PWD
if "%TARGET_PATH%"=="" (
    echo [!] Chưa nhập đường dẫn bài giảng.
    pause
    exit /b 1
)
set "TARGET_PATH=%TARGET_PATH:"=%"

echo.
echo [*] Bài giảng được chọn: %TARGET_PATH%
set /p "NEW_PWD=🔑 Nhập MẬT KHẨU MỚI cho Chế độ Thầy Cô (VD: Thien2026): "

if "%NEW_PWD%"=="" (
    echo [!] Mật khẩu mới không được để trống!
    pause
    exit /b 1
)

echo.
"%PYTHON_EXE%" "%~dp0scripts\interactive_video_builder.py" --set-password "%NEW_PWD%" "%TARGET_PATH%"

echo.
pause
