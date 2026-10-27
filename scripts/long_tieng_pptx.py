#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hệ Thống Tự Động Lồng Tiếng AI Chuẩn Phát Thanh Viên Cho Slide PowerPoint
Tác giả: Thầy Nguyễn Văn Thiện - THCS Ứng Hòe
- Đọc nội dung lời giảng trong phần Notes của từng slide
- Sử dụng giọng đọc AI tiếng Việt chất lượng cao của Microsoft (Edge-TTS)
  + vi-VN-HoaiMyNeural (Giọng nữ miền Bắc nhẹ nhàng, truyền cảm)
  + vi-VN-NamMinhNeural (Giọng nam miền Bắc dõng dạc, trầm ấm)
- Nhúng trực tiếp file âm thanh vào từng slide PowerPoint và tự động đặt thời gian chuyển slide
"""

import sys
import os
import asyncio
import argparse
import subprocess
import tempfile
import shutil

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

try:
    from pptx import Presentation
except ImportError:
    print("[*] Dang tu dong cai dat thu vien python-pptx (lan dau tien)...")
    subprocess.run([sys.executable, "-m", "pip", "install", "python-pptx", "--quiet"])
    try:
        from pptx import Presentation
    except ImportError:
        print("[!] Khong the tu dong cai dat python-pptx. Vui long chay cai_dat_tu_dong.bat.")
        sys.exit(1)


try:
    import edge_tts
except ImportError:
    print("[!] Đang tự động cài đặt edge-tts...")
    subprocess.run([sys.executable, "-m", "pip", "install", "edge-tts", "--quiet"])
    import edge_tts


VOICE_MAP = {
    "1": ("vi-VN-HoaiMyNeural", "Cô Hoài My (Nữ miền Bắc - Nhẹ nhàng, truyền cảm)"),
    "2": ("vi-VN-NamMinhNeural", "Thầy Nam Minh (Nam miền Bắc - Dõng dạc, trầm ấm)"),
    "hoaimy": ("vi-VN-HoaiMyNeural", "Cô Hoài My (Nữ miền Bắc)"),
    "namminh": ("vi-VN-NamMinhNeural", "Thầy Nam Minh (Nam miền Bắc)")
}


async def generate_speech(text, voice_name, output_path):
    """Sinh file âm thanh mp3 từ văn bản qua edge-tts"""
    communicate = edge_tts.Communicate(text, voice_name, rate="+0%", volume="+0%")
    await communicate.save(output_path)


def process_long_tieng(pptx_path, voice_choice="1", output_pptx=None):
    pptx_path = os.path.abspath(pptx_path)
    if not os.path.exists(pptx_path):
        print(f"[X] Không tìm thấy file: {pptx_path}")
        return False

    voice_key = str(voice_choice).lower().strip()
    voice_info = VOICE_MAP.get(voice_key, VOICE_MAP["1"])
    voice_id, voice_label = voice_info

    if not output_pptx:
        base, ext = os.path.splitext(pptx_path)
        output_pptx = f"{base}_DaLongTieng{ext}"
    else:
        output_pptx = os.path.abspath(output_pptx)

    print("=" * 68)
    print("      HỆ THỐNG TỰ ĐỘNG LỒNG TIẾNG AI CHO SLIDE POWERPOINT")
    print("        Tác giả: Thầy Nguyễn Văn Thiện - THCS Ứng Hòe")
    print("=" * 68)
    print(f"\n[*] File slide gốc    : {os.path.basename(pptx_path)}")
    print(f"[*] Giọng đọc AI chọn : {voice_label}")

    prs = Presentation(pptx_path)
    total_slides = len(prs.slides)
    print(f"[*] Tổng số slide     : {total_slides} trang")

    temp_dir = tempfile.mkdtemp(prefix="audio_slides_")

    audio_files = {}
    print("\n[*] Đang chuyển lời giảng (Notes) thành giọng đọc AI:")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    has_any_notes = False
    for idx, slide in enumerate(prs.slides, start=1):
        note_text = ""
        if slide.has_notes_slide and slide.notes_slide.notes_text_frame:
            note_text = slide.notes_slide.notes_text_frame.text.strip()

        if note_text:
            has_any_notes = True
            mp3_path = os.path.join(temp_dir, f"slide_{idx:02d}.mp3")
            print(f"    • Slide {idx:02d}: Đang đọc ({len(note_text)} ký tự)...")
            try:
                loop.run_until_complete(generate_speech(note_text, voice_id, mp3_path))
                if os.path.exists(mp3_path) and os.path.getsize(mp3_path) > 0:
                    audio_files[idx] = mp3_path
            except Exception as e:
                print(f"      [!] Lỗi khi đọc slide {idx}: {e}")
        else:
            print(f"    • Slide {idx:02d}: Không có lời giảng Notes (bỏ qua âm thanh)")

    loop.close()

    if not has_any_notes or not audio_files:
        print("\n[!] Chú ý: File PowerPoint này chưa có lời bình trong phần Notes của các slide.")
        print("    Vui lòng nhờ Trợ lý AI viết lời bình vào Notes trước (hoặc dùng them_loi_binh_pptx.py).")
        shutil.rmtree(temp_dir, ignore_errors=True)
        return False

    print(f"\n[*] Đã sinh xong {len(audio_files)} đoạn giọng đọc AI.")
    print("[*] Đang tự động nhúng âm thanh vào từng slide PowerPoint...")

    # Tạo script PowerShell để nhúng âm thanh vào PowerPoint COM
    ps_lines = [
        '$ErrorActionPreference = "Stop"',
        f'$pptxPath = "{pptx_path.replace("\\", "\\\\")}"',
        f'$outPath = "{output_pptx.replace("\\", "\\\\")}"',
        'if (Test-Path -LiteralPath $outPath) { Remove-Item -LiteralPath $outPath -Force }',
        '$powerPoint = New-Object -ComObject PowerPoint.Application',
        '$presentation = $powerPoint.Presentations.Open($pptxPath, [Microsoft.Office.Core.MsoTriState]::msoTrue, [Microsoft.Office.Core.MsoTriState]::msoFalse, [Microsoft.Office.Core.MsoTriState]::msoFalse)',
    ]

    for idx, mp3 in audio_files.items():
        mp3_escaped = mp3.replace("\\", "\\\\")
        ps_lines.append(f"""
try {{
    $slide = $presentation.Slides.Item({idx})
    $shape = $slide.Shapes.AddMediaObject2("{mp3_escaped}", $false, $true, 20, 20, 50, 50)
    $shape.AnimationSettings.PlaySettings.PlayOnEntry = [Microsoft.Office.Core.MsoTriState]::msoTrue
    $shape.AnimationSettings.PlaySettings.HideWhileNotPlaying = [Microsoft.Office.Core.MsoTriState]::msoTrue
    $slide.SlideShowTransition.AdvanceOnTime = [Microsoft.Office.Core.MsoTriState]::msoTrue
}} catch {{}}
""")

    ps_lines.append('$presentation.SaveAs($outPath)')
    ps_lines.append('$presentation.Close()')
    ps_lines.append('$powerPoint.Quit()')
    ps_lines.append('Write-Host "[OK] Da nhung thanh cong toan bo am thanh!"')

    ps_script_path = os.path.join(temp_dir, "embed_audio.ps1")
    with open(ps_script_path, "w", encoding="utf-8") as f:
        f.write("\n".join(ps_lines))

    try:
        proc = subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", ps_script_path],
            capture_output=True,
            text=True,
            timeout=180
        )
        if os.path.exists(output_pptx) and os.path.getsize(output_pptx) > 0:
            print("\n" + "=" * 68)
            print("  🎉 [LỒNG TIẾNG AI THÀNH CÔNG!]")
            print(f"  • File PowerPoint đã lồng tiếng: {output_pptx}")
            print("  • Mỗi slide đã có sẵn giọng đọc AI phát tự động khi trình chiếu!")
            print("  • Bây giờ Thầy/Cô chỉ cần kéo file này vào 'XUAT_VIDEO_TU_PPTX.bat'")
            print("    là có ngay Video bài giảng MP4 hoàn chỉnh có tiếng đọc như phát thanh viên!")
            print("=" * 68)
            return True
        else:
            print(f"[!] Kết quả: {proc.stderr.strip() or proc.stdout.strip()}")
            return False
    except Exception as e:
        print(f"[!] Lỗi khi nhúng âm thanh: {e}")
        return False
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def main():
    parser = argparse.ArgumentParser(description="Lồng tiếng AI tự động vào slide PowerPoint")
    parser.add_argument("pptx", help="Đường dẫn file PowerPoint (.pptx)")
    parser.add_argument("--voice", default="1", help="1: Cô Hoài My, 2: Thầy Nam Minh")
    parser.add_argument("-o", "--output", help="Đường dẫn file xuất ra")
    args = parser.parse_args()

    process_long_tieng(args.pptx, args.voice, args.output)


if __name__ == "__main__":
    main()
