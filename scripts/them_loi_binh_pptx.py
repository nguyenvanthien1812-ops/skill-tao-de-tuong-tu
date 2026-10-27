#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Công Cụ Đọc Nội Dung Slide & Ghi Lời Bình Vào Phần Notes Của PowerPoint
Tác giả: Thầy Nguyễn Văn Thiện - THCS Ứng Hòe
- Đọc tiêu đề, nội dung chữ của từng slide trong file PPTX có sẵn
- Tự động ghi lời giảng/lời bình của giáo viên vào mục Notes dưới chân slide
- Phục vụ việc trình chiếu và xuất video bài giảng
"""

import sys
import os
import json
import argparse

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



def extract_slide_content(pptx_path):
    """Trích xuất toàn bộ văn bản của từng slide để AI phân tích viết lời bình"""
    pptx_path = os.path.abspath(pptx_path)
    if not os.path.exists(pptx_path):
        print(f"[X] Không tìm thấy file: {pptx_path}")
        return None

    prs = Presentation(pptx_path)
    slides_data = []

    for idx, slide in enumerate(prs.slides, start=1):
        texts = []
        for shape in slide.shapes:
            if shape.has_text_frame:
                for paragraph in shape.text_frame.paragraphs:
                    t = paragraph.text.strip()
                    if t:
                        texts.append(t)
        
        # Đọc notes hiện tại nếu có
        existing_notes = ""
        if slide.has_notes_slide and slide.notes_slide.notes_text_frame:
            existing_notes = slide.notes_slide.notes_text_frame.text.strip()

        slides_data.append({
            "slide_index": idx,
            "title": texts[0] if texts else f"Slide {idx}",
            "content": texts,
            "existing_notes": existing_notes
        })

    return slides_data


def inject_notes_to_pptx(pptx_path, notes_dict, output_path=None):
    """
    Ghi danh sách lời bình vào mục Notes của từng slide.
    notes_dict: dict {slide_index (int): "nội dung lời bình (str)"}
    """
    pptx_path = os.path.abspath(pptx_path)
    if not os.path.exists(pptx_path):
        print(f"[X] Không tìm thấy file: {pptx_path}")
        return False

    if not output_path:
        base, ext = os.path.splitext(pptx_path)
        output_path = f"{base}_CoLoiBinh{ext}"
    else:
        output_path = os.path.abspath(output_path)

    prs = Presentation(pptx_path)

    for idx, slide in enumerate(prs.slides, start=1):
        str_key = str(idx)
        script_text = notes_dict.get(idx) or notes_dict.get(str_key)
        if script_text:
            notes_slide = slide.notes_slide
            text_frame = notes_slide.notes_text_frame
            text_frame.text = script_text

    prs.save(output_path)
    print(f"[✓] Đã ghi thành công lời bình vào phần Notes của {len(notes_dict)} slide!")
    print(f"[✓] File mới đã lưu tại: {output_path}")
    return output_path


def main():
    parser = argparse.ArgumentParser(description="Trích xuất nội dung hoặc ghi lời bình vào PowerPoint Notes")
    parser.add_argument("pptx", help="Đường dẫn file PowerPoint (.pptx)")
    parser.add_argument("--extract", action="store_true", help="Trích xuất nội dung các slide dạng JSON ra màn hình")
    parser.add_argument("--inject-json", type=str, help="Đường dẫn file JSON chứa lời bình để ghi vào Notes")
    parser.add_argument("-o", "--output", help="Đường dẫn file PPTX lưu ra")
    args = parser.parse_args()

    if args.extract:
        data = extract_slide_content(args.pptx)
        if data:
            print(json.dumps(data, ensure_ascii=False, indent=2))
        return

    if args.inject_json:
        if not os.path.exists(args.inject_json):
            print(f"[X] Không tìm thấy file JSON: {args.inject_json}")
            sys.exit(1)
        with open(args.inject_json, "r", encoding="utf-8") as f:
            notes_data = json.load(f)
        inject_notes_to_pptx(args.pptx, notes_data, args.output)
        return

    print("Vui lòng chọn cờ --extract để đọc nội dung slide, hoặc --inject-json để ghi lời bình.")


if __name__ == "__main__":
    main()
