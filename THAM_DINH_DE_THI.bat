@echo off
chcp 65001 > nul
cls
echo.
echo ╔══════════════════════════════════════════════════════════════════╗
echo ║      BỘ CÔNG CỤ THẨM ĐỊNH ĐỀ KIỂM TRA MÔN TOÁN (GDPT 2018)   ║
echo ║      Phiên bản 1.0  ^|  Ưu tiên Toán THCS lớp 6–9              ║
echo ╚══════════════════════════════════════════════════════════════════╝
echo.

REM ── Xác định thư mục gốc của tool ──────────────────────────────────────────
set "TOOL_DIR=%~dp0"
set "SCRIPT_DIR=%TOOL_DIR%.agents\skills\tao-de-toan-tuong-tu\scripts"
set "SCRIPT=%SCRIPT_DIR%\tham_dinh\exam_reviewer_cli.py"

REM ── Kiểm tra Python ─────────────────────────────────────────────────────────
python --version > nul 2>&1
if errorlevel 1 (
    echo [LỖI] Không tìm thấy Python. Vui lòng cài Python 3.9+ và thêm vào PATH.
    pause
    exit /b 1
)

REM ── Kiểm tra thư viện ───────────────────────────────────────────────────────
python -c "import docx, openpyxl, lxml" > nul 2>&1
if errorlevel 1 (
    echo [THÔNG BÁO] Đang cài đặt thư viện cần thiết...
    python -m pip install python-docx openpyxl lxml --quiet
    echo [OK] Cài đặt hoàn tất.
    echo.
)

REM ── Nhập thông tin từ GV ────────────────────────────────────────────────────
echo Thầy/Cô vui lòng nhập đường dẫn 3 file (kéo thả file vào cửa sổ này hoặc gõ tay):
echo.

set /p "MATRIX_FILE=  1. File MA TRẬN / BẢN ĐẶC TẢ (.docx): "
if not exist "%MATRIX_FILE%" (
    echo [LỖI] Không tìm thấy file: %MATRIX_FILE%
    pause & exit /b 1
)

set /p "EXAM_FILE=  2. File ĐỀ THI (dành cho học sinh) (.docx): "
if not exist "%EXAM_FILE%" (
    echo [LỖI] Không tìm thấy file: %EXAM_FILE%
    pause & exit /b 1
)

set /p "RUBRIC_FILE=  3. File HƯỚNG DẪN CHẤM / LỜI GIẢI (.docx): "
if not exist "%RUBRIC_FILE%" (
    echo [LỖI] Không tìm thấy file: %RUBRIC_FILE%
    pause & exit /b 1
)

echo.
set /p "GRADE=  4. Lớp (ví dụ: 8, 9, 10...): "
set /p "SCHOOL=  5. Tên trường (có thể bỏ trống): "
set /p "TEACHER=  6. Tên giáo viên biên soạn (có thể bỏ trống): "

REM ── Thư mục output ──────────────────────────────────────────────────────────
echo.
set "DEFAULT_OUT=%USERPROFILE%\Desktop\BAO_CAO_THAM_DINH"
set /p "OUT_DIR=  7. Thư mục lưu báo cáo [Enter = Desktop\BAO_CAO_THAM_DINH]: "
if "%OUT_DIR%"=="" set "OUT_DIR=%DEFAULT_OUT%"

echo.
echo ══════════════════════════════════════════════════════════════════
echo   Đang thẩm định... Vui lòng chờ.
echo ══════════════════════════════════════════════════════════════════
echo.

REM ── Chạy tool ───────────────────────────────────────────────────────────────
set "CMD=python "%SCRIPT%" --matrix "%MATRIX_FILE%" --exam "%EXAM_FILE%" --rubric "%RUBRIC_FILE%" --output "%OUT_DIR%" --grade %GRADE%"
if not "%SCHOOL%"=="" set "CMD=%CMD% --school "%SCHOOL%""
if not "%TEACHER%"=="" set "CMD=%CMD% --teacher "%TEACHER%""

cd /d "%SCRIPT_DIR%"
%CMD%

echo.
echo ══════════════════════════════════════════════════════════════════
echo   Báo cáo đã được lưu tại: %OUT_DIR%
echo ══════════════════════════════════════════════════════════════════
echo.
echo   Thầy/Cô mở thư mục báo cáo? (Y/N)
set /p "OPEN_DIR="
if /i "%OPEN_DIR%"=="Y" explorer "%OUT_DIR%"

pause
