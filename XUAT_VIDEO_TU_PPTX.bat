@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
title Xuat Video Bai Giang MP4 Tu Slide PowerPoint - Thay Thien

echo.
echo ====================================================================
echo   🎬 XUẤT VIDEO BÀI GIẢNG MP4 FULL HD TỪ FILE POWERPOINT (.PPTX)
echo      Tác giả: Thầy Nguyễn Văn Thiện - THCS Ứng Hòe
echo ====================================================================
echo.

set "PPTX_FILE=%~1"

if "%PPTX_FILE%"=="" (
    echo [HƯỚNG DẪN SỬ DỤNG]:
    echo   1. Thầy/Cô KÉO THẢ file PowerPoint (.pptx) vào file .bat này.
    echo   2. Hoặc dán đường dẫn file PowerPoint vào bên dưới:
    echo.
    set /p "PPTX_FILE=[*] Nhập đường dẫn file .pptx: "
)

if "%PPTX_FILE%"=="" (
    echo [!] Chưa có file PowerPoint để xuất video.
    pause
    exit /b 1
)

set "PPTX_FILE=%PPTX_FILE:"=%"

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
    echo [!] Không tìm thấy Python trên máy tính!
    echo     Vui lòng chạy file 1_CAI_DAT_MOI_TRUONG.bat trước để cài đặt.
    pause
    exit /b 1
)

set "SCRIPT_FILE="
if exist "%~dp0scripts\xuat_video_pptx.py" (
    set "SCRIPT_FILE=%~dp0scripts\xuat_video_pptx.py"
) else if exist "%USERPROFILE%\.gemini\config\skills\tao-slide-va-video-khoi-dong\scripts\xuat_video_pptx.py" (
    set "SCRIPT_FILE=%USERPROFILE%\.gemini\config\skills\tao-slide-va-video-khoi-dong\scripts\xuat_video_pptx.py"
) else if exist "%USERPROFILE%\.gemini\antigravity\skills\tao-slide-va-video-khoi-dong\scripts\xuat_video_pptx.py" (
    set "SCRIPT_FILE=%USERPROFILE%\.gemini\antigravity\skills\tao-slide-va-video-khoi-dong\scripts\xuat_video_pptx.py"
)

if "%SCRIPT_FILE%"=="" (
    echo [X] Không tìm thấy script xuat_video_pptx.py!
    pause
    exit /b 1
)

echo.
"%PYTHON_EXE%" "%SCRIPT_FILE%" "%PPTX_FILE%"

echo.
pause
