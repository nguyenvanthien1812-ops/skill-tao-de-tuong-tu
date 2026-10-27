#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hệ Thống Tự Động Xuất Video Bài Giảng MP4 từ PowerPoint (.pptx)
Tác giả: Thầy Nguyễn Văn Thiện - THCS Ứng Hòe
- Sử dụng trực tiếp bộ giải mã video của Microsoft PowerPoint trên Windows
- Xuất video Full HD (1080p, 30fps), giữ nguyên 100% hiệu ứng chuyển trang và hoạt ảnh
- Không cần cài đặt ffmpeg hay phần mềm dựng video phức tạp
"""

import sys
import os
import subprocess
import argparse

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

def export_pptx_to_video(pptx_path, output_mp4=None, resolution=1080, fps=30, timeout=1800):
    pptx_path = os.path.abspath(pptx_path)
    if not os.path.exists(pptx_path):
        print(f"[X] Lỗi: Không tìm thấy file PowerPoint tại: {pptx_path}")
        return False

    if not output_mp4:
        base_name = os.path.splitext(pptx_path)[0]
        output_mp4 = f"{base_name}_Video.mp4"
    else:
        output_mp4 = os.path.abspath(output_mp4)

    print("=" * 66)
    print("      HỆ THỐNG XUẤT VIDEO BÀI GIẢNG MP4 TỪ POWERPOINT")
    print("        Tác giả: Thầy Nguyễn Văn Thiện - THCS Ứng Hòe")
    print("=" * 66)
    print(f"\n[*] File slide đầu vào : {os.path.basename(pptx_path)}")
    print(f"[*] File video đầu ra  : {os.path.basename(output_mp4)}")
    print(f"[*] Độ phân giải video : {resolution}p (Full HD, {fps} fps)")
    print(f"[*] Đang khởi động Microsoft PowerPoint để kết xuất video...")

    # Mã PowerShell điều khiển PowerPoint COM
    ps_script = f"""
$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

$pptxPath = "{pptx_path.replace('\\', '\\\\')}"
$outputPath = "{output_mp4.replace('\\', '\\\\')}"
$resolution = {resolution}
$fps = {fps}
$timeout = {timeout}

if (Test-Path -LiteralPath $outputPath) {{
    Remove-Item -LiteralPath $outputPath -Force
}}

$powerPoint = $null
$presentation = $null

try {{
    try {{
        $powerPoint = [Runtime.InteropServices.Marshal]::GetActiveObject("PowerPoint.Application")
    }} catch {{
        $powerPoint = New-Object -ComObject PowerPoint.Application
    }}
    $powerPoint.Visible = [Microsoft.Office.Core.MsoTriState]::msoTrue

    $presentation = $powerPoint.Presentations.Open($pptxPath, [Microsoft.Office.Core.MsoTriState]::msoTrue, [Microsoft.Office.Core.MsoTriState]::msoFalse, [Microsoft.Office.Core.MsoTriState]::msoFalse)

    # 1080p, 30fps, quality 85, default slide duration 5s
    $presentation.CreateVideo($outputPath, $true, 5, $resolution, $fps, 85)

    $deadline = (Get-Date).AddSeconds($timeout)
    while ($true) {{
        $status = $presentation.CreateVideoStatus
        if ($status -eq 3) {{ # ppMediaTaskStatusDone
            break
        }}
        if ($status -eq 4) {{ # ppMediaTaskStatusFailed
            throw "PowerPoint bao loi khi render video."
        }}
        if ((Get-Date) -ge $deadline) {{
            throw "Qua thoi gian cho phep render video."
        }}
        Start-Sleep -Seconds 2
    }}

    Write-Host "[OK] Render thanh cong!"
}}
catch {{
    Write-Error $_.Exception.Message
    exit 1
}}
finally {{
    if ($presentation -ne $null) {{
        try {{ $presentation.Close() }} catch {{}}
    }}
}}
"""

    try:
        proc = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_script],
            capture_output=True,
            text=True,
            timeout=timeout + 30
        )
        if proc.returncode == 0 and os.path.exists(output_mp4) and os.path.getsize(output_mp4) > 0:
            print("\n" + "=" * 66)
            print("  🎉 [XUẤT VIDEO THÀNH CÔNG!]")
            print(f"  • Video đã lưu tại: {output_mp4}")
            print("  • Thầy/Cô có thể mở video để trình chiếu hoặc gửi học sinh ôn bài.")
            print("=" * 66)
            return True
        else:
            print(f"\n[!] Lỗi khi xuất video: {proc.stderr.strip() or proc.stdout.strip()}")
            print("💡 Mẹo: Thầy/Cô có thể mở trực tiếp file PowerPoint lên máy,")
            print("       vào File -> Export -> Create a Video để lưu video cực nhanh!")
            return False
    except Exception as e:
        print(f"\n[!] Lỗi tiến trình: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Xuất video bài giảng MP4 từ PowerPoint")
    parser.add_argument("pptx", help="Đường dẫn tới file PowerPoint (.pptx)")
    parser.add_argument("-o", "--output", help="Đường dẫn file video đầu ra (.mp4)")
    parser.add_argument("--res", type=int, default=1080, help="Độ phân giải (mặc định 1080)")
    args = parser.parse_args()

    export_pptx_to_video(args.pptx, args.output, resolution=args.res)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Cách dùng: python xuat_video_pptx.py <duong_dan_file.pptx>")
        sys.exit(1)
    main()
