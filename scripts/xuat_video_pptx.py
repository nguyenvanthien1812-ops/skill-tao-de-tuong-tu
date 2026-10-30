#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hệ Thống Tự Động Xuất Video Bài Giảng MP4 từ PowerPoint (.pptx)
Tác giả: Thầy Nguyễn Văn Thiện - THCS Ứng Hòe
- Sử dụng trực tiếp bộ kết xuất video của Microsoft PowerPoint trên Windows
- Xuất video Full HD (1080p, 30fps), giữ nguyên 100% giọng đọc AI, hiệu ứng chuyển trang và công thức OMML
- Lưu kịch bản PowerShell bằng chuẩn UTF-8 BOM (utf-8-sig) + chuỗi đơn để hỗ trợ 100% đường dẫn tiếng Việt có dấu
"""

import sys
import os
import shutil
import tempfile
import subprocess
import argparse

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def ps_quote(val: str) -> str:
    """Đặt đường dẫn vào cặp nháy đơn PowerShell an toàn tuyệt đối với tiếng Việt, dấu cách, ký tự $."""
    return "'" + str(val).replace("'", "''") + "'"


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

    os.makedirs(os.path.dirname(output_mp4), exist_ok=True)

    print("=" * 66)
    print("      HỆ THỐNG XUẤT VIDEO BÀI GIẢNG MP4 TỪ POWERPOINT")
    print("        Tác giả: Thầy Nguyễn Văn Thiện - THCS Ứng Hòe")
    print("=" * 66)
    print(f"\n[*] File slide đầu vào : {os.path.basename(pptx_path)}")
    print(f"[*] File video đầu ra  : {os.path.basename(output_mp4)}")
    print(f"[*] Độ phân giải video : {resolution}p (Full HD, {fps} fps)")
    print("[*] Đang khởi động Microsoft PowerPoint để kết xuất video (vui lòng chờ 1-3 phút)...")

    ps_script = f"""
$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

$pptxPath = {ps_quote(pptx_path)}
$outputPath = {ps_quote(output_mp4)}
$resolution = {int(resolution)}
$fps = {int(fps)}
$timeout = {int(timeout)}

if (Test-Path -LiteralPath $outputPath) {{
    Remove-Item -LiteralPath $outputPath -Force
}}

$createdNewPP = $false
$powerPoint = $null
$presentation = $null

try {{
    try {{
        $powerPoint = [Runtime.InteropServices.Marshal]::GetActiveObject("PowerPoint.Application")
    }} catch {{
        $powerPoint = New-Object -ComObject PowerPoint.Application
        $createdNewPP = $true
    }}
    $powerPoint.Visible = [Microsoft.Office.Core.MsoTriState]::msoTrue

    $presentation = $powerPoint.Presentations.Open(
        $pptxPath,
        [Microsoft.Office.Core.MsoTriState]::msoTrue,
        [Microsoft.Office.Core.MsoTriState]::msoFalse,
        [Microsoft.Office.Core.MsoTriState]::msoFalse
    )

    # CreateVideo(FileName, UseTimingsAndNarrations=$true, DefaultSlideDuration=5, VertResolution, FramesPerSecond, Quality=85)
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
    if ($createdNewPP -and $powerPoint -ne $null) {{
        try {{ $powerPoint.Quit() }} catch {{}}
    }}
}}
"""

    temp_dir = tempfile.mkdtemp(prefix="pptx_video_")
    ps_file = os.path.join(temp_dir, "export_video.ps1")
    # CỰC KỲ QUAN TRỌNG: Ghi chuẩn utf-8-sig (có BOM) để Windows PowerShell 5.1 đọc đúng tên file tiếng Việt!
    with open(ps_file, "w", encoding="utf-8-sig") as f:
        f.write(ps_script)

    try:
        proc = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-File", ps_file],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout + 30,
        )
        if proc.returncode == 0 and os.path.exists(output_mp4) and os.path.getsize(output_mp4) > 0:
            size_mb = os.path.getsize(output_mp4) / (1024.0 * 1024.0)
            print("\n" + "=" * 66)
            print("  🎉 [XUẤT VIDEO BÀI GIẢNG MP4 THÀNH CÔNG!]")
            print(f"  • Video đã lưu tại : {output_mp4}")
            print(f"  • Dung lượng video : {size_mb:.2f} MB (Full HD {resolution}p)")
            print("  • Sẵn sàng tải lên YouTube / gắn vào Trang Web Video Tương Tác!")
            print("=" * 66)
            return True
        else:
            print(f"\n[!] Lỗi khi xuất video: {proc.stderr.strip() or proc.stdout.strip()}")
            print("💡 Mẹo dự phòng: Mở file PowerPoint -> File -> Export -> Create a Video -> Create Video.")
            return False
    except Exception as e:
        print(f"\n[!] Lỗi tiến trình: {e}")
        return False
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def main():
    parser = argparse.ArgumentParser(description="Xuất video bài giảng MP4 từ PowerPoint")
    parser.add_argument("pptx", help="Đường dẫn tới file PowerPoint (.pptx)")
    parser.add_argument("-o", "--output", help="Đường dẫn file video đầu ra (.mp4)")
    parser.add_argument("--res", type=int, default=1080, help="Độ phân giải (mặc định 1080)")
    args = parser.parse_args()

    ok = export_pptx_to_video(args.pptx, args.output, resolution=args.res)
    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Cách dùng: python xuat_video_pptx.py <duong_dan_file.pptx>")
        sys.exit(1)
    main()
