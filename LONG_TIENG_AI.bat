@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
title Long Tieng AI Cho Slide PowerPoint - Thay Thien

echo.
echo ====================================================================
echo   🎙️ TỰ ĐỘNG LỒNG TIẾNG AI CHO SLIDE POWERPOINT TỪ LỜI BÌNH (NOTES)
echo      Tác giả: Thầy Nguyễn Văn Thiện - THCS Ứng Hòe
echo ====================================================================
echo.

set "PPTX_FILE=%~1"

if "%PPTX_FILE%"=="" (
    echo [HƯỚNG DẪN SỬ DỤNG]:
    echo   1. KÉO THẢ file PowerPoint (.pptx đã có lời bình Notes) vào file .bat này.
    echo   2. Hoặc dán đường dẫn file PowerPoint vào bên dưới:
    echo.
    set /p "PPTX_FILE=[*] Nhập đường dẫn file .pptx: "
)

if "%PPTX_FILE%"=="" (
    echo [!] Chưa có file PowerPoint để lồng tiếng.
    pause
    exit /b 1
)

set "PPTX_FILE=%PPTX_FILE:"=%"

echo.
echo [CHỌN GIỌNG ĐỌC PHÁT THANH VIÊN AI]:
echo   [1] Cô Hoài My   (Giọng nữ miền Bắc - Nhẹ nhàng, truyền cảm, chuẩn cô giáo)
echo   [2] Thầy Nam Minh (Giọng nam miền Bắc - Dõng dạc, trầm ấm, chuẩn thầy giáo)
echo.
set "VOICE_OPT=1"
set /p "VOICE_OPT=[*] Thầy/Cô chọn [1 hoặc 2, Nhấn Enter mặc định chọn 1]: "

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

set "SCRIPT_FILE="
if exist "%~dp0scripts\long_tieng_pptx.py" (
    set "SCRIPT_FILE=%~dp0scripts\long_tieng_pptx.py"
) else if exist "%USERPROFILE%\.gemini\config\skills\tao-slide-va-video-khoi-dong\scripts\long_tieng_pptx.py" (
    set "SCRIPT_FILE=%USERPROFILE%\.gemini\config\skills\tao-slide-va-video-khoi-dong\scripts\long_tieng_pptx.py"
) else if exist "%USERPROFILE%\.gemini\antigravity\skills\tao-slide-va-video-khoi-dong\scripts\long_tieng_pptx.py" (
    set "SCRIPT_FILE=%USERPROFILE%\.gemini\antigravity\skills\tao-slide-va-video-khoi-dong\scripts\long_tieng_pptx.py"
)

if "%SCRIPT_FILE%"=="" (
    echo [X] Không tìm thấy script long_tieng_pptx.py!
    pause
    exit /b 1
)

echo.
echo [*] Đang tiến hành đọc lời giảng và lồng tiếng AI vào từng slide...
echo.

"%PYTHON_EXE%" "%SCRIPT_FILE%" "%PPTX_FILE%" --voice "%VOICE_OPT%"

echo.
pause
