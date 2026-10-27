#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
inject_nls_docx.py
Tool tự động chèn Năng lực số (NLS), AI, HSKT và Tiếng Anh vào file giáo án Word (.docx)
Bảo toàn 100% MathType OLE, bảng biểu 2 cột và bố cục file gốc.
"""

import os
import sys
import json
import argparse
import docx
from docx.shared import Pt, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

# Bảng mã màu chuẩn nhận diện
COLOR_MAP = {
    'blue': RGBColor(0x00, 0x55, 0xD4),    # NLS: Xanh dương (#0055D4)
    'purple': RGBColor(0x70, 0x30, 0xA0),  # AI: Tím (#7030A0)
    'green': RGBColor(0x00, 0x80, 0x00),   # HSKT: Xanh lá (#008000)
    'orange': RGBColor(0xB4, 0x53, 0x09),  # Tiếng Anh: Cam đất (#B45309)
}

def set_run_font(run, font_name="Times New Roman", size_pt=13, color_rgb=None, bold=False, italic=False):
    """Thiết lập định dạng font chuẩn xác cho Run"""
    run.font.name = font_name
    # Đặt XML rFonts cho cả tiếng Việt có dấu
    rPr = run._r.get_or_add_rPr()
    rFonts = OxmlElement('w:rFonts')
    rFonts.set(qn('w:ascii'), font_name)
    rFonts.set(qn('w:hAnsi'), font_name)
    rFonts.set(qn('w:cs'), font_name)
    rPr.append(rFonts)
    
    if size_pt:
        run.font.size = Pt(size_pt)
    if color_rgb:
        run.font.color.rgb = color_rgb
    run.font.bold = bold
    run.font.italic = italic

def insert_paragraph_after(target_para, text="", bold=False, italic=False, color_rgb=None, size_pt=13):
    """Chèn một đoạn văn mới ngay sau đoạn văn chỉ định"""
    new_p = OxmlElement('w:p')
    target_para._p.addnext(new_p)
    new_para = docx.text.paragraph.Paragraph(new_p, target_para._parent)
    if text:
        run = new_para.add_run(text)
        set_run_font(run, size_pt=size_pt, color_rgb=color_rgb, bold=bold, italic=italic)
    return new_para

def inject_nls(input_path, output_path, data):
    """
    Tiêm dữ liệu NLS / AI vào file Word docx
    data dict cấu trúc:
    {
        "muc_tieu_nls": [
            {"type": "blue", "text": "2.3. Năng lực số và ứng dụng AI:", "bold": True},
            {"type": "blue", "text": "- Khai thác dữ liệu và thông tin (1.1.TC1a): ...", "bold": False},
            {"type": "purple", "text": "- Sử dụng trí tuệ nhân tạo (6.2.TC1a / NLc.C2): ...", "bold": False}
        ],
        "thiet_bi_nls": [
            {"type": "blue", "text": "+ Ứng dụng số: Quizizz/Azota, phần mềm mô phỏng GeoGebra/PhET, công cụ AI minh họa.", "bold": False}
        ],
        "hoat_dong": {
            "1": [
                {"type": "blue", "step": "thuc_hien", "text": "[★NLS] HS tương tác với video mô phỏng / câu hỏi khởi động trên TV số. (Mã: 2.1.TC1a)"}
            ],
            "2": [
                {"type": "blue", "step": "thuc_hien", "text": "[★NLS] HS thao tác trên phần mềm số / tra cứu học liệu số theo hướng dẫn. (Mã: 1.1.TC1a, 5.3.TC1a)"}
            ],
            "3": [
                {"type": "blue", "step": "thuc_hien", "text": "[★NLS] HS sử dụng máy tính cầm tay để kiểm tra kết quả bài giải. (Mã: 5.2.TC1a)"}
            ],
            "4": [
                {"type": "blue", "step": "thuc_hien", "text": "[★NLS] HS sử dụng Canva thiết kế sơ đồ tư duy hoặc poster tuyên truyền. (Mã: 3.1.TC1a)"},
                {"type": "purple", "step": "thuc_hien", "text": "[★AI] HS sử dụng công cụ AI gợi ý ý tưởng thông điệp, đối chiếu với SGK trước khi báo cáo. (Mã: NLc.C2)"}
            ]
        }
    }
    """
    doc = docx.Document(input_path)
    
    # 1. CHÈN VÀO MỤC I. MỤC TIÊU -> Cuối phần 2. Năng lực (trước 3. Phẩm chất)
    muc_tieu_items = data.get("muc_tieu_nls", [])
    if muc_tieu_items:
        # Tìm vị trí chèn: Tìm đoạn có chữ "3. Phẩm chất" hoặc "Phẩm chất"
        target_idx = None
        for i, p in enumerate(doc.paragraphs):
            t = p.text.strip().lower()
            if t.startswith("3. phẩm chất") or t.startswith("iii. phẩm chất") or "phẩm chất:" in t:
                target_idx = i - 1
                break
        
        # Nếu không thấy Phẩm chất, tìm sau đoạn "2. Năng lực"
        if target_idx is None:
            for i, p in enumerate(doc.paragraphs):
                t = p.text.strip().lower()
                if "2. năng lực" in t or "năng lực đặc thù" in t:
                    target_idx = i
        
        if target_idx is not None and target_idx >= 0:
            curr_p = doc.paragraphs[target_idx]
            for item in muc_tieu_items:
                c_rgb = COLOR_MAP.get(item.get("type", "blue"))
                curr_p = insert_paragraph_after(
                    curr_p, 
                    text=item.get("text", ""), 
                    bold=item.get("bold", False),
                    italic=item.get("italic", False),
                    color_rgb=c_rgb,
                    size_pt=item.get("size", 13)
                )

    # 2. CHÈN VÀO MỤC II. THIẾT BỊ DẠY HỌC
    thiet_bi_items = data.get("thiet_bi_nls", [])
    if thiet_bi_items:
        tb_idx = None
        for i, p in enumerate(doc.paragraphs):
            t = p.text.strip().lower()
            if "1. giáo viên:" in t or "1. đối với giáo viên:" in t or "đối với giáo viên" in t:
                tb_idx = i
                break
        if tb_idx is not None:
            curr_p = doc.paragraphs[tb_idx]
            for item in thiet_bi_items:
                c_rgb = COLOR_MAP.get(item.get("type", "blue"))
                curr_p = insert_paragraph_after(
                    curr_p,
                    text=item.get("text", ""),
                    bold=item.get("bold", False),
                    italic=item.get("italic", False),
                    color_rgb=c_rgb,
                    size_pt=13
                )

    # 3. CHÈN VÀO MỤC III. TIẾN TRÌNH DẠY HỌC (Trong các bảng 2 cột hoặc đoạn văn)
    hoat_dong_data = data.get("hoat_dong", {})
    if hoat_dong_data:
        # Quét qua tất cả các bảng trong document (bảng CV 5512)
        for tbl in doc.tables:
            for row in tbl.rows:
                for cell in row.cells:
                    cell_text_lower = cell.text.lower()
                    # Kiểm tra ô này có phải là ô tổ chức thực hiện chứa các bước không
                    for hd_key, items in hoat_dong_data.items():
                        # Kiểm tra xem cell này thuộc Hoạt động nào hoặc bước nào
                        for item in items:
                            step_kw = "thực hiện" if item.get("step") == "thuc_hien" else "báo cáo"
                            if step_kw in cell_text_lower:
                                # Tìm paragraph cụ thể chứa bước này trong cell
                                for p in cell.paragraphs:
                                    p_txt = p.text.lower()
                                    if ("* thực hiện" in p_txt or "- thực hiện" in p_txt or "thực hiện nhiệm vụ" in p_txt) and item.get("step") == "thuc_hien":
                                        # Thêm dòng vào cuối paragraph này
                                        p.add_run("\n")
                                        r = p.add_run(item.get("text", ""))
                                        c_rgb = COLOR_MAP.get(item.get("type", "blue"))
                                        set_run_font(r, color_rgb=c_rgb, bold=True, italic=False)
                                        # Đánh dấu đã chèn để không chèn lặp lại
                                        item["_inserted"] = True
                                        break
                                    elif ("* báo cáo" in p_txt or "- báo cáo" in p_txt or "báo cáo, thảo luận" in p_txt) and item.get("step") == "bao_cao":
                                        p.add_run("\n")
                                        r = p.add_run(item.get("text", ""))
                                        c_rgb = COLOR_MAP.get(item.get("type", "blue"))
                                        set_run_font(r, color_rgb=c_rgb, bold=True, italic=False)
                                        item["_inserted"] = True
                                        break

    # Lưu file
    doc.save(output_path)
    print(f"[THÀNH CÔNG] Đã tiêm NLS/AI và lưu file tại: {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Inject NLS/AI into docx lesson plan")
    parser.add_argument("--input", "-i", required=True, help="Path to input docx file")
    parser.add_argument("--output", "-o", required=True, help="Path to output docx file")
    parser.add_argument("--data", "-d", help="Path to JSON data file")
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"[LỖI] Không tìm thấy file đầu vào: {args.input}")
        sys.exit(1)

    data = {}
    if args.data and os.path.exists(args.data):
        with open(args.data, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        # Dữ liệu mặc định mẫu thử nghiệm
        data = {
            "muc_tieu_nls": [
                {"type": "blue", "text": "2.3. Năng lực số và ứng dụng Trí tuệ nhân tạo (AI):", "bold": True},
                {"type": "blue", "text": "- Khai thác dữ liệu và thông tin (1.1.TC1a): HS biết tìm kiếm, chọn lọc và khai thác thông tin, hình ảnh học tập trên Internet/kho học liệu số.", "bold": False},
                {"type": "purple", "text": "- Sử dụng trí tuệ nhân tạo (6.2.TC1a): HS biết sử dụng công cụ AI hỗ trợ gợi ý ý tưởng và đối chiếu với SGK trước khi báo cáo.", "bold": False}
            ]
        }

    inject_nls(args.input, args.output, data)

if __name__ == "__main__":
    main()
