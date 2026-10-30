#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hệ Thống Tự Động Xuất Video Bài Giảng MP4 từ PowerPoint (.pptx) — Kiến Trúc Dual-Engine
Tác giả: Thầy Nguyễn Văn Thiện - THCS Ứng Hòe
- Engine 1 (Ưu tiên - Siêu tốc & Chống lỗi codec AV1/VP9 100%):
  + Dùng Microsoft PowerPoint COM kết xuất từng trang Slide ra ảnh gốc Full HD (1920x1080 PNG),
    giữ nguyên 100% font chữ, công thức Toán OMML, đồ họa SVG/SmartArt và tự ẩn biểu tượng cái loa ở góc slide.
  + Trích xuất trực tiếp các file âm thanh giọng đọc AI (.mp3) đã nhúng trong từng slide + khớp chính xác 100%
    thời lượng từng slide trong _SlideTimeline.json.
  + Dùng FFmpeg (hoặc imageio-ffmpeg tự động) ghép thành Video bài giảng MP4 Full HD (1080p, 30fps, H.264 + AAC)
    chỉ trong 15-30 giây, không bao giờ bị treo hay lỗi ppMediaTaskStatusFailed!
- Engine 2 (Dự phòng): Gọi trực tiếp PowerPoint CreateVideo nếu máy không có FFmpeg.
"""

import sys
import os
import re
import json
import zipfile
import shutil
import tempfile
import subprocess
import argparse
import xml.etree.ElementTree as ET

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def ps_quote(val: str) -> str:
    """Đặt đường dẫn vào cặp nháy đơn PowerShell an toàn tuyệt đối với tiếng Việt, dấu cách, ký tự $."""
    return "'" + str(val).replace("'", "''") + "'"


def _find_ffmpeg_exe() -> str:
    """Tìm bộ mã hóa FFmpeg trên máy hoặc qua gói imageio-ffmpeg."""
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        pass
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "imageio-ffmpeg", "--quiet"], timeout=60)
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return ""


def _extract_slide_mp3_map(pptx_path: str, out_dir: str) -> dict:
    """
    Trích xuất file âm thanh .mp3 tương ứng với từng slide (1..N) từ cấu trúc OOXML của file .pptx.
    Trả về dict: {slide_index (int): đường_dẫn_mp3}
    """
    slide_mp3s = {}
    with zipfile.ZipFile(pptx_path, "r") as zf:
        namelist = set(zf.namelist())
        idx = 1
        while f"ppt/slides/slide{idx}.xml" in namelist:
            rels_path = f"ppt/slides/_rels/slide{idx}.xml.rels"
            if rels_path in namelist:
                rels_xml = zf.read(rels_path).decode("utf-8", errors="ignore")
                # Tìm tất cả Target="../media/*.mp3"
                matches = re.findall(r'Target="\.\./media/([^"]+\.mp3)"', rels_xml, flags=re.I)
                if matches:
                    media_name = matches[-1]
                    zip_media_path = f"ppt/media/{media_name}"
                    if zip_media_path in namelist:
                        local_mp3 = os.path.join(out_dir, f"slide_{idx:03d}.mp3")
                        with open(local_mp3, "wb") as f:
                            f.write(zf.read(zip_media_path))
                        slide_mp3s[idx] = local_mp3
            idx += 1
    return slide_mp3s


def _load_slide_durations(pptx_path: str, total_slides: int, slide_mp3s: dict) -> dict:
    """Đọc thời lượng chuẩn của từng slide từ _SlideTimeline.json (nếu có) hoặc đo từ file MP3."""
    durations = {}
    base_no_ext = os.path.splitext(pptx_path)[0]
    timeline_path = base_no_ext + "_SlideTimeline.json"
    if os.path.exists(timeline_path):
        try:
            data = json.load(open(timeline_path, "r", encoding="utf-8"))
            for item in data.get("slides", []):
                s_idx = int(item.get("slide", 0))
                dur = float(item.get("duration_sec", 5.0))
                if s_idx > 0 and dur > 0:
                    durations[s_idx] = dur
        except Exception:
            pass

    for idx in range(1, total_slides + 1):
        if idx not in durations:
            mp3_p = slide_mp3s.get(idx)
            if mp3_p and os.path.exists(mp3_p):
                try:
                    from mutagen.mp3 import MP3
                    a = MP3(mp3_p)
                    durations[idx] = round(float(a.info.length) + 1.0, 1)
                except Exception:
                    durations[idx] = 6.0
            else:
                durations[idx] = 5.0
    return durations


def _export_slides_to_png_via_powerpoint(pptx_path: str, png_dir: str, width: int, height: int) -> int:
    """
    Dùng PowerPoint COM xuất toàn bộ các trang slide ra ảnh PNG độ phân giải cao (1920x1080),
    đồng thời tạm ẩn icon cái loa (MediaType=2) để khung hình video bài giảng sạch đẹp 100%.
    """
    temp_pptx = os.path.join(png_dir, "export_slides_source.pptx")
    shutil.copy2(pptx_path, temp_pptx)

    ps_script = f"""
$ErrorActionPreference = "Stop"
$pptxPath = {ps_quote(temp_pptx)}
$pngDir = {ps_quote(png_dir)}
$w = {int(width)}
$h = {int(height)}

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
    $presentation = $powerPoint.Presentations.Open(
        $pptxPath,
        [Microsoft.Office.Core.MsoTriState]::msoTrue,
        [Microsoft.Office.Core.MsoTriState]::msoFalse,
        [Microsoft.Office.Core.MsoTriState]::msoFalse
    )
    $count = $presentation.Slides.Count
    for ($i = 1; $i -le $count; $i++) {{
        $slide = $presentation.Slides.Item($i)
        foreach ($sh in $slide.Shapes) {{
            try {{
                if ($sh.Type -eq 16 -and $sh.MediaType -eq 2) {{
                    $sh.Visible = [Microsoft.Office.Core.MsoTriState]::msoFalse
                }}
            }} catch {{}}
        }}
        $outPng = Join-Path $pngDir ("slide_" + $i.ToString("000") + ".png")
        $slide.Export($outPng, "PNG", $w, $h)
    }}
    Write-Host "EXPORTED_COUNT=$count"
}}
finally {{
    if ($presentation -ne $null) {{ try {{ $presentation.Close() }} catch {{}} }}
    if ($createdNewPP -and $powerPoint -ne $null) {{ try {{ $powerPoint.Quit() }} catch {{}} }}
}}
"""
    ps_file = os.path.join(png_dir, "export_pngs.ps1")
    with open(ps_file, "w", encoding="utf-8-sig") as f:
        f.write(ps_script)

    proc = subprocess.run(
        ["powershell", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-File", ps_file],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=300,
    )
    m = re.search(r"EXPORTED_COUNT=(\d+)", proc.stdout or "")
    if m:
        return int(m.group(1))
    pngs = [p for p in os.listdir(png_dir) if p.startswith("slide_") and p.endswith(".png")]
    return len(pngs)


def _render_video_via_ffmpeg_engine(pptx_path: str, output_mp4: str, resolution: int, fps: int) -> bool:
    ffmpeg_exe = _find_ffmpeg_exe()
    if not ffmpeg_exe:
        return False

    height = int(resolution)
    width = int(round(height * 16.0 / 9.0))
    if width % 2 == 1:
        width += 1
    if height % 2 == 1:
        height += 1

    temp_dir = tempfile.mkdtemp(prefix="pptx_fast_video_")
    try:
        print("    • [Bước 3.1] Đang chụp kết xuất các trang Slide chuẩn Full HD từ PowerPoint...")
        total_slides = _export_slides_to_png_via_powerpoint(pptx_path, temp_dir, width, height)
        if total_slides <= 0:
            return False

        slide_mp3s = _extract_slide_mp3_map(pptx_path, temp_dir)
        durations = _load_slide_durations(pptx_path, total_slides, slide_mp3s)

        print(f"    • [Bước 3.2] Đang ghép âm thanh AI và mã hóa H.264 cho {total_slides} slide...")
        seg_files = []
        for idx in range(1, total_slides + 1):
            png_path = os.path.join(temp_dir, f"slide_{idx:03d}.png")
            if not os.path.exists(png_path):
                return False
            dur = max(1.0, float(durations.get(idx, 5.0)))
            mp3_path = slide_mp3s.get(idx)
            seg_path = os.path.join(temp_dir, f"seg_{idx:03d}.mp4")

            if mp3_path and os.path.exists(mp3_path):
                cmd = [
                    ffmpeg_exe,
                    "-y",
                    "-loop", "1",
                    "-framerate", str(fps),
                    "-t", f"{dur:.2f}",
                    "-i", png_path,
                    "-i", mp3_path,
                    "-filter_complex", f"[1:a]apad=whole_dur={dur:.2f}[aout]",
                    "-map", "0:v:0",
                    "-map", "[aout]",
                    "-c:v", "libx264",
                    "-preset", "ultrafast",
                    "-tune", "stillimage",
                    "-crf", "20",
                    "-pix_fmt", "yuv420p",
                    "-r", str(fps),
                    "-c:a", "aac",
                    "-b:a", "128k",
                    "-ar", "44100",
                    "-ac", "2",
                    "-t", f"{dur:.2f}",
                    seg_path,
                ]
            else:
                cmd = [
                    ffmpeg_exe,
                    "-y",
                    "-loop", "1",
                    "-framerate", str(fps),
                    "-t", f"{dur:.2f}",
                    "-i", png_path,
                    "-f", "lavfi",
                    "-t", f"{dur:.2f}",
                    "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
                    "-map", "0:v:0",
                    "-map", "1:a:0",
                    "-c:v", "libx264",
                    "-preset", "ultrafast",
                    "-tune", "stillimage",
                    "-crf", "20",
                    "-pix_fmt", "yuv420p",
                    "-r", str(fps),
                    "-c:a", "aac",
                    "-b:a", "128k",
                    "-ar", "44100",
                    "-ac", "2",
                    "-t", f"{dur:.2f}",
                    seg_path,
                ]

            res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120)
            if res.returncode != 0 or not os.path.exists(seg_path):
                return False
            seg_files.append(seg_path)
            print(f"      + Slide {idx:02d}/{total_slides:02d} ({dur:.1f}s) -> OK")

        concat_txt = os.path.join(temp_dir, "concat_list.txt")
        with open(concat_txt, "w", encoding="utf-8") as f:
            for sp in seg_files:
                safe_sp = sp.replace("\\", "/").replace("'", "'\\''")
                f.write(f"file '{safe_sp}'\n")

        if os.path.exists(output_mp4):
            os.remove(output_mp4)

        concat_cmd = [
            ffmpeg_exe,
            "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", concat_txt,
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-tune", "stillimage",
            "-crf", "21",
            "-pix_fmt", "yuv420p",
            "-c:a", "copy",
            "-movflags", "+faststart",
            output_mp4,
        ]
        res_c = subprocess.run(concat_cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=300)
        return res_c.returncode == 0 and os.path.exists(output_mp4) and os.path.getsize(output_mp4) > 0
    except Exception as e:
        print(f"    [!] Cảnh báo Engine 1: {e}")
        return False
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


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
    print("[*] Đang kết xuất video bài giảng Full HD...")

    # Ưu tiên Engine 1 (PowerPoint Native PNG Export + FFmpeg Studio Encoder): siêu tốc 15-30s, khớp 100% _SlideTimeline.json, không bao giờ lỗi codec AV1
    if _render_video_via_ffmpeg_engine(pptx_path, output_mp4, resolution=resolution, fps=fps):
        size_mb = os.path.getsize(output_mp4) / (1024.0 * 1024.0)
        print("\n" + "=" * 66)
        print("  🎉 [XUẤT VIDEO BÀI GIẢNG MP4 THÀNH CÔNG!]")
        print(f"  • Video đã lưu tại : {output_mp4}")
        print(f"  • Dung lượng video : {size_mb:.2f} MB (Full HD {resolution}p)")
        print("  • Sẵn sàng tải lên YouTube / gắn vào Trang Web Video Tương Tác!")
        print("=" * 66)
        return True

    # Engine 2 (Dự phòng): PowerPoint CreateVideo trực tiếp
    temp_dir = tempfile.mkdtemp(prefix="pptx_video_")
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

    $presentation.CreateVideo($outputPath, $true, 5, $resolution, $fps, 85)

    $deadline = (Get-Date).AddSeconds($timeout)
    while ($true) {{
        $status = $presentation.CreateVideoStatus
        if ($status -eq 3) {{
            break
        }}
        if ($status -eq 4) {{
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

    ps_file = os.path.join(temp_dir, "export_video.ps1")
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
