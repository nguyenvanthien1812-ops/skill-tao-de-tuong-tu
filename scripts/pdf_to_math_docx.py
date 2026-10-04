#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module Chuyển Đổi Đề Thi PDF Sang Word Chuẩn Toán Học & Sư Phạm
(High-Fidelity PDF to MathType Word Converter)

Tính năng:
1. Chuyển đổi PDF (kể cả PDF scan hoặc ảnh) sang Word không lỗi công thức.
2. Công thức toán được nhận diện LaTeX và chuyển sang MathType OLE (Equation.DSMT4) 14pt.
3. Hình vẽ được trích xuất ở độ phân giải 300 DPI, căn chỉnh tự động theo Bố cục 2 cột (Smart Side-by-Side).
4. Bảng biểu thống kê (mẫu ghép nhóm, bảng phân bố tần số) được dựng bằng bảng Word chuẩn (Table Grid).
5. Tự động sinh cả 3 ấn phẩm: Bản đề học sinh OLE, Bản lời giải chi tiết OLE, và Bản Word Equation OMML.
"""

import os
import sys
import uuid
import argparse
import urllib.request
from pathlib import Path
import fitz  # PyMuPDF
from PIL import Image, ImageChops
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import qn

# Import các tiện ích từ docx_math_builder nếu có
try:
    from .docx_math_builder import (
        BACKEND_API_URL, latex_to_omml, add_math_content,
        _remove_table_borders, set_cell_margins, add_side_by_side_question,
        _get_license_token, _get_machine_id_safe,
        convert_to_mathtype_ole_via_backend, audit_word_ole_file
    )
except ImportError:
    try:
        from docx_math_builder import (
            BACKEND_API_URL, latex_to_omml, add_math_content,
            _remove_table_borders, set_cell_margins, add_side_by_side_question,
            _get_license_token, _get_machine_id_safe,
            convert_to_mathtype_ole_via_backend, audit_word_ole_file
        )
    except ImportError:
        # Nếu chạy standalone script
        BACKEND_API_URL = 'https://latex2mathtypeweb.onrender.com/api/convert-docx'
        def convert_to_mathtype_ole_via_backend(*args, **kwargs):
            return False
        def audit_word_ole_file(*args, **kwargs):
            return {'ok': False, 'ole_count': 0}
    def _get_license_token():
        try:
            _d = os.path.dirname(os.path.abspath(__file__))
            if _d not in sys.path:
                sys.path.insert(0, _d)
            from license_manager import get_license_token
            t = get_license_token()
            if t:
                return t
        except Exception:
            pass
        try:
            for p in [Path(__file__).resolve().parent.parent / "license.key",
                      Path.home() / ".gemini" / "config" / "skills" / "tao-de-toan-tuong-tu" / "license.key",
                      Path.home() / ".gemini" / "license.key"]:
                if p.exists():
                    return p.read_text(encoding="utf-8").strip()
        except Exception:
            pass
        return ""
    def _get_machine_id_safe():
        try:
            _d = os.path.dirname(os.path.abspath(__file__))
            if _d not in sys.path:
                sys.path.insert(0, _d)
            from license_manager import get_machine_id
            return get_machine_id()
        except Exception:
            return ""

# ─── LỚP A: HARD-LOCK LICENSE ────────────────────────────────────────────────
def _require_license():
    try:
        _d = os.path.dirname(os.path.abspath(__file__))
        if _d not in sys.path:
            sys.path.insert(0, _d)
        from license_manager import check_current_license
        ok, payload, err = check_current_license()
        if not ok:
            raise PermissionError(
                "\n╔══════════════════════════════════════════════════════════╗\n"
                "║     ⛔  SKILL CHƯA ĐƯỢC KÍCH HOẠT BẢN QUYỀN!           ║\n"
                "╠══════════════════════════════════════════════════════════╣\n"
                f"║  Lý do: {err[:50]:<50} ║\n"
                "╠══════════════════════════════════════════════════════════╣\n"
                "║  Chạy KICH_HOAT_BAN_QUYEN.bat để kích hoạt license.    ║\n"
                "╚══════════════════════════════════════════════════════════╝"
            )
        return payload
    except ImportError:
        return {}
# ─────────────────────────────────────────────────────────────────────────────



def trim_whitespace(im, bg_color=(255, 255, 255), pad=15):
    """Cắt bỏ viền trắng thừa xung quanh hình vẽ minh họa."""
    im = im.convert('RGB')
    bg = Image.new('RGB', im.size, bg_color)
    diff = ImageChops.difference(im, bg)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    bbox = diff.getbbox()
    if bbox:
        w, h = im.size
        bbox = (max(0, bbox[0]-pad), max(0, bbox[1]-pad), min(w, bbox[2]+pad), min(h, bbox[3]+pad))
        return im.crop(bbox)
    return im

def extract_pages_at_300dpi(pdf_path, output_dir):
    """Kết xuất tất cả các trang của PDF thành ảnh 300 DPI sắc nét."""
    os.makedirs(output_dir, exist_ok=True)
    doc = fitz.open(pdf_path)
    page_paths = []
    print(f"[*] Đang kết xuất {len(doc)} trang PDF ở độ phân giải 300 DPI...")
    for i, page in enumerate(doc):
        pix = page.get_pixmap(dpi=300)
        p_path = os.path.join(output_dir, f"page_{i+1}_300dpi.png")
        pix.save(p_path)
        page_paths.append(p_path)
        print(f"    + Trang {i+1}: {pix.width}x{pix.height} px")
    return page_paths

def convert_to_mathtype_ole(in_path, out_path, api_url=BACKEND_API_URL, timeout=120):
    """
    Chuyển đổi file DOCX nền chứa $LaTeX$ sang Word MathType OLE nguyên bản.
    [Lớp A] Yêu cầu license hợp lệ.
    [Lớp E] Gửi kèm license_key + machine_id lên backend để xác thực.
    Tự động kiểm định tính toàn vẹn (Integrity Audit) sau khi xuất.
    """
    _require_license()
    print(f"[*] Đang gửi {os.path.basename(in_path)} tới Backend MathType Server...")
    return convert_to_mathtype_ole_via_backend(in_path, out_path, api_url=api_url, timeout=timeout)



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Chuyển đổi đề thi PDF sang Word chuẩn MathType OLE và Word Equation")
    parser.add_argument("--pdf", required=True, help="Đường dẫn tới file PDF cần chuyển đổi")
    parser.add_argument("--out", default=".", help="Thư mục xuất file Word")
    args = parser.parse_args()

    pdf_file = args.pdf
    if not os.path.exists(pdf_file):
        print(f"[Lỗi] Không tìm thấy file: {pdf_file}")
        sys.exit(1)

    print(f"[*] Bắt đầu xử lý file PDF: {pdf_file}")
    try:
        from pdf_to_word_v2 import convert_pdf_to_word
    except ImportError:
        try:
            from .pdf_to_word_v2 import convert_pdf_to_word
        except ImportError:
            import sys
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            from pdf_to_word_v2 import convert_pdf_to_word

    res = convert_pdf_to_word(pdf_file, args.out)
    if res.get("ole_docx"):
        print(f"[OK] File MathType OLE đã sẵn sàng: {res['ole_docx']}")
    elif res.get("word_eq_docx"):
        print(f"[OK] File Word Equation đã sẵn sàng: {res['word_eq_docx']}")
    else:
        print(f"[OK] Đã xuất file: {res.get('raw_docx')}")

