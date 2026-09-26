@echo off
chcp 65001 >nul
title NAP SKILL VAO ANTIGRAVITY

echo.
echo ==============================================================
echo        TỰ ĐỘNG NẠP SKILL VÀO GOOGLE ANTIGRAVITY
echo ==============================================================
echo.

set "TARGET_DIR=%USERPROFILE%\.gemini\config\skills\tao-de-toan-tuong-tu"

echo [*] Dang tao thu muc skills tren may tinh...
if not exist "%TARGET_DIR%" mkdir "%TARGET_DIR%"

echo [*] Dang sao chep toan bo file skill vao Antigravity...
xcopy "%~dp0*" "%TARGET_DIR%\" /E /I /Y /Q >nul

echo.
echo ==============================================================
echo   ✅ [HOÀN TẤT] ĐÃ NẠP SKILL VÀO ANTIGRAVITY THÀNH CÔNG!
echo.
echo   Bây giờ bạn chỉ cần mở phần mềm Google Antigravity lên
echo   và nhắn tin để tạo đề thi ngay!
echo ==============================================================
echo.
pause
