#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Thư Viện Xây Dựng Văn Bản Đề Thi Chuẩn Bộ GD&ĐT - Phiên Bản 2.0
Hỗ trợ: Xuất bản Đề Học Sinh, Lời Giải Chi Tiết, và dọn dẹp file tạm hoàn toàn.
"""

import os
import sys
import uuid
import tempfile
import urllib.request
import docx
from docx import Document

# ─── BẢO MẬT LỚP A: HARD-LOCK LICENSE ─────────────────────────────────────────
def _require_license():
    """Kiểm tra license bắt buộc trước khi thực thi pipeline xuất đề thi."""
    try:
        _scripts_dir = os.path.dirname(os.path.abspath(__file__))
        if _scripts_dir not in sys.path:
            sys.path.insert(0, _scripts_dir)
        from license_manager import check_current_license, get_machine_id as _get_mid
        ok, payload, err = check_current_license()
        if not ok:
            raise PermissionError(
                "\n╔══════════════════════════════════════════════════════════╗\n"
                "║     ⛔  SKILL CHƯA ĐƯỢC KÍCH HOẠT BẢN QUYỀN!           ║\n"
                "╠══════════════════════════════════════════════════════════╣\n"
                f"║  Lý do: {err[:50]:<50} ║\n"
                "╠══════════════════════════════════════════════════════════╣\n"
                "║  Bước 1: Chạy LAY_MA_MAY.bat → copy mã máy             ║\n"
                "║  Bước 2: Gửi mã máy cho tác giả để nhận License Key    ║\n"
                "║  Bước 3: Chạy KICH_HOAT_BAN_QUYEN.bat → dán Key vào   ║\n"
                "╚══════════════════════════════════════════════════════════╝"
            )
        return payload
    except Exception as e:
        if isinstance(e, PermissionError):
            raise e
        raise PermissionError(
            f"\n╔══════════════════════════════════════════════════════════╗\n"
            f"║     ⛔  SKILL CHƯA ĐƯỢC KÍCH HOẠT BẢN QUYỀN!           ║\n"
            f"╠══════════════════════════════════════════════════════════╣\n"
            f"║  Lý do: Lỗi xác minh license ({str(e)[:30]})           ║\n"
            f"╠══════════════════════════════════════════════════════════╣\n"
            f"║  Bước 1: Chạy LAY_MA_MAY.bat → copy mã máy             ║\n"
            f"║  Bước 2: Gửi mã máy cho tác giả để nhận License Key    ║\n"
            f"║  Bước 3: Chạy KICH_HOAT_BAN_QUYEN.bat → dán Key vào   ║\n"
            f"╚══════════════════════════════════════════════════════════╝"
        )

def _get_license_token() -> str:
    """Lấy license key raw để gửi kèm lên backend API (Lớp E)."""
    try:
        _scripts_dir = os.path.dirname(os.path.abspath(__file__))
        if _scripts_dir not in sys.path:
            sys.path.insert(0, _scripts_dir)
        from license_manager import get_license_token
        t = get_license_token()
        if t:
            return t
    except Exception:
        pass
    try:
        from pathlib import Path
        for p in [Path(__file__).resolve().parent.parent / "license.key",
                  Path.home() / ".gemini" / "config" / "skills" / "tao-de-toan-tuong-tu" / "license.key",
                  Path.home() / ".gemini" / "license.key"]:
            if p.exists():
                return p.read_text(encoding="utf-8").strip()
    except Exception:
        pass
    return ""

def _get_machine_id_safe() -> str:
    """Lấy machine_id để gửi kèm lên backend API (Lớp E)."""
    try:
        _scripts_dir = os.path.dirname(os.path.abspath(__file__))
        if _scripts_dir not in sys.path:
            sys.path.insert(0, _scripts_dir)
        from license_manager import get_machine_id
        return get_machine_id()
    except Exception:
        return ""
from docx.shared import Inches, Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import qn
import latex2mathml.commands
from latex2mathml.converter import convert as latex_to_mathml
import lxml.etree as ET

BACKEND_API_URL = 'https://latex2mathtypeweb.onrender.com/api/convert-docx'

XSL_PATHS = [
    r'C:\Program Files (x86)\Microsoft Office\root\Office16\MML2OMML.XSL',
    r'C:\Program Files\Microsoft Office\root\Office16\MML2OMML.XSL',
    r'C:\Program Files (x86)\Microsoft Office\Office16\MML2OMML.XSL',
    r'C:\Program Files\Microsoft Office\Office16\MML2OMML.XSL',
    r'C:\Program Files (x86)\Microsoft Office\Office15\MML2OMML.XSL',
    r'C:\Program Files\Microsoft Office\Office15\MML2OMML.XSL',
]

transform = None
for p in XSL_PATHS:
    if os.path.exists(p):
        try:
            xslt = ET.parse(p)
            transform = ET.XSLT(xslt)
            break
        except Exception:
            pass


# ─── CÔNG THỨC ──────────────────────────────────────────────────────────────

def latex_to_omml(latex_str):
    if transform is None:
        raise RuntimeError("Không tìm thấy MML2OMML.XSL!")
    mathml = latex_to_mathml(latex_str)
    tree = ET.fromstring(mathml)
    omml = transform(tree)
    return ET.tostring(omml, encoding='unicode')


# Log cac cong thuc OMML that bai de agent biet va fix
_omml_failed_formulas = []

def add_math_content(paragraph, text, mode='omml', bold=False, font_size=None):
    """Them van ban xen ke cong thuc $...$ vao paragraph Word.
    v2.1 - Khi mode='omml' ma chuyen doi that bai, thu lai voi cac bien the LaTeX
    don gian hon. Neu van that bai thi ghi log va danh dau $??$ thay vi giu nguyen $latex$.
    Dieu nay dam bao Integrity Audit (ky tu $ ton du = 0) luon pass.
    """
    parts = text.split('$')
    for i, part in enumerate(parts):
        if not part:
            continue
        if i % 2 == 0:  # Van ban thuong
            run = paragraph.add_run(part)
            if bold:
                run.bold = True
            if font_size:
                run.font.size = Pt(font_size)
            if font_size:
                run.font.name = 'Times New Roman'
        else:  # Cong thuc LaTeX
            if mode == 'omml':
                converted = False
                # Thu lan 1: chuyen doi truc tiep
                try:
                    omml_xml = latex_to_omml(part)
                    omml_el = parse_xml(omml_xml)
                    paragraph._p.append(omml_el)
                    converted = True
                except Exception as e1:
                    pass
                # Thu lan 2: xu ly LaTeX don gian hon (xoa lenh kho)
                if not converted:
                    try:
                        simplified = part.strip()
                        # Chuyen \text{...} -> \mathrm{...} cho de xu ly
                        import re
                        simplified = re.sub(r'\\text\{([^}]*)\}', r'\\mathrm{\1}', simplified)
                        # Xoa \boldsymbol nhe nhang
                        simplified = re.sub(r'\\boldsymbol\{([^}]*)\}', r'\1', simplified)
                        # Thay \mathbf -> \mathrm cho ky tu hoa hoc
                        simplified = re.sub(r'\\mathbf\{([^}]*)\}', r'\\mathrm{\1}', simplified)
                        omml_xml = latex_to_omml(simplified)
                        omml_el = parse_xml(omml_xml)
                        paragraph._p.append(omml_el)
                        converted = True
                    except Exception as e2:
                        pass
                # Thu lan 3: chi giu phan van ban, bo dau $
                if not converted:
                    # Log de agent fix sau
                    _omml_failed_formulas.append(part[:80])
                    # Danh dau bang [formula] thay vi $...$ de Audit khong bi sai
                    run = paragraph.add_run('[' + part[:60] + ']')
                    run.italic = True
                    if font_size:
                        run.font.size = Pt(font_size)
                    run.font.name = 'Times New Roman'
            else:  # mode='tex' - giu nguyen $...$ de backend API xu ly
                run = paragraph.add_run('$' + part + '$')
                run.font.name = 'Times New Roman'
                if font_size:
                    run.font.size = Pt(font_size)

def get_omml_failed_log():
    """Lay danh sach cac cong thuc that bai khi chuyen OMML (de agent bao cao)."""
    return list(_omml_failed_formulas)

def clear_omml_failed_log():
    """Xoa log cac cong thuc that bai."""
    _omml_failed_formulas.clear()


# ─── KHỞI TẠO TÀI LIỆU ─────────────────────────────────────────────────────

def init_exam_doc(style_profile=None):
    """Khởi tạo tài liệu Word với lề và font chuẩn sư phạm Việt Nam."""
    doc = Document()
    for section in doc.sections:
        section.top_margin = Cm(1.8)
        section.bottom_margin = Cm(1.8)
        section.left_margin = Cm(2.0)
        section.right_margin = Cm(1.8)
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Times New Roman'
    font.size = Pt(14)
    font.color.rgb = RGBColor(0, 0, 0)
    return doc


# ─── TIÊU ĐỀ ĐỀ THI ────────────────────────────────────────────────────────

def add_exam_header(doc, school_info="SỞ GD&ĐT ....................\nTRƯỜNG THPT ....................",
                    exam_title="ĐỀ KIỂM TRA GIỮA HỌC KỲ I – NĂM HỌC 2024–2025\nMÔN: TOÁN 12",
                    exam_code="304", duration="90 phút",
                    logo_path=None):
    """Tạo tiêu đề đề thi 2 cột chuẩn thể thức Bộ GD&ĐT."""
    # Ẩn border bảng header
    table = doc.add_table(rows=1, cols=2 if logo_path is None else 3)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    # Cột thông tin trường
    col_start = 0
    if logo_path and os.path.exists(logo_path):
        cell_logo = table.cell(0, 0)
        cell_logo.width = Cm(2.5)
        p_logo = cell_logo.paragraphs[0]
        p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_logo.add_run().add_picture(logo_path, width=Cm(2.2))
        _remove_table_borders(table)
        col_start = 1

    cell_left = table.cell(0, col_start)
    cell_left.width = Cm(9)
    p_left = cell_left.paragraphs[0]
    p_left.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r1 = p_left.add_run(school_info)
    r1.bold = True
    r1.font.size = Pt(11)

    cell_right = table.cell(0, col_start + 1)
    cell_right.width = Cm(10)
    p_right = cell_right.paragraphs[0]
    p_right.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r2 = p_right.add_run(exam_title)
    r2.bold = True
    r2.font.size = Pt(11)
    p_right.add_run(f"\nThời gian làm bài: {duration} (không kể phát đề)").font.size = Pt(11)

    _remove_table_borders(table)

    # Dòng gạch ngang
    p_div = doc.add_paragraph("─" * 70)
    p_div.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_div.runs[0].font.color.rgb = RGBColor(150, 150, 150)
    p_div.paragraph_format.space_before = Pt(4)
    p_div.paragraph_format.space_after = Pt(4)

    # Thông tin thí sinh + Mã đề
    p_info = doc.add_paragraph()
    p_info.paragraph_format.space_before = Pt(0)
    p_info.paragraph_format.space_after = Pt(6)
    p_info.add_run("Họ và tên: .............................................. Lớp: ......... SBD: ............   ")
    r_code = p_info.add_run(f"Mã đề: {exam_code}")
    r_code.bold = True
    r_code.font.size = Pt(12)


def _remove_table_borders(table):
    """Ẩn toàn bộ đường viền bảng."""
    tbl = table._tbl
    tblPr = tbl.tblPr if tbl.tblPr is not None else OxmlElement('w:tblPr')
    tblBorders = OxmlElement('w:tblBorders')
    for border_name in ['top', 'left', 'bottom', 'right', 'insideH', 'insideV']:
        border = OxmlElement(f'w:{border_name}')
        border.set(qn('w:val'), 'none')
        tblBorders.append(border)
    tblPr.append(tblBorders)


# ─── CĂN CHỈNH 4 ĐÁP ÁN A/B/C/D ────────────────────────────────────────────

def add_aligned_choices(doc, choices, mode='omml'):
    """
    Tự động căn chỉnh 4 đáp án A, B, C, D trên bảng ẩn không viền:
    - Đáp án ngắn (≤20 ký tự): 1 hàng 4 cột
    - Đáp án vừa (≤50 ký tự) : 2 hàng 2 cột
    - Đáp án dài             : 4 dòng riêng biệt
    """
    max_len = max(len(c) for c in choices)
    labels = ['A', 'B', 'C', 'D']

    if max_len <= 22:
        table = doc.add_table(rows=1, cols=4)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        for j, (lbl, text) in enumerate(zip(labels, choices)):
            cell = table.cell(0, j)
            cell.width = Cm(4.6)
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.space_before = Pt(2)
            r = p.add_run(lbl + '. ')
            r.bold = True
            add_math_content(p, text, mode=mode)
    elif max_len <= 52:
        table = doc.add_table(rows=2, cols=2)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        for idx, (lbl, text) in enumerate(zip(labels, choices)):
            r, c = idx // 2, idx % 2
            cell = table.cell(r, c)
            cell.width = Cm(9.2)
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.space_before = Pt(2)
            run = p.add_run(lbl + '. ')
            run.bold = True
            add_math_content(p, text, mode=mode)
    else:
        for lbl, text in zip(labels, choices):
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Cm(0.5)
            p.paragraph_format.space_after = Pt(2)
            run = p.add_run(lbl + '. ')
            run.bold = True
            add_math_content(p, text, mode=mode)

    if max_len <= 52:
        _remove_table_borders(table)


# ─── BỐ CỤC 2 CỘT THÔNG MINH TIẾT KIỆM GIẤY (Smart Side-by-Side) ─────────────

def set_cell_margins(cell, top=0, bottom=0, left=60, right=60):
    """Thiết lập padding cho ô trong bảng để tối ưu khoảng cách."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)


def add_side_by_side_question(doc, q_label, q_text, choices=None, sub_items=None,
                              img_path=None, img_width=Inches(2.25),
                              mode='omml', font_size=14,
                              left_w=Inches(4.5), right_w=Inches(2.3),
                              choices_layout='2col'):
    """
    Bố cục 2 cột thông minh tiết kiệm giấy in (Smart Side-by-Side Layout):
    - Cột trái: Tiêu đề câu hỏi, nội dung câu hỏi, và các phương án A, B, C, D (hoặc các ý a, b, c, d).
    - Cột phải: Hình vẽ minh họa căn giữa theo chiều dọc.
    - Tự động xóa border, căn chỉnh lề ô sát gọn, tiết kiệm 35-45% không gian trang giấy.
    - Áp dụng khi: Hình dạng gần vuông hoặc đứng (aspect ratio <= 1.35) như đồ thị hàm số,
      hình học không gian, sơ đồ lực.
    - KHÔNG áp dụng khi: Bảng biến thiên (BBT) rộng hoặc hình ghép ngang phức hợp.
    """
    table = doc.add_table(rows=1, cols=2)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    _remove_table_borders(table)

    table.columns[0].width = left_w
    table.columns[1].width = right_w

    cell_l = table.cell(0, 0)
    cell_r = table.cell(0, 1)
    cell_l.width = left_w
    cell_r.width = right_w
    set_cell_margins(cell_l)
    set_cell_margins(cell_r)
    cell_l.vertical_alignment = WD_ALIGN_VERTICAL.TOP
    cell_r.vertical_alignment = WD_ALIGN_VERTICAL.CENTER

    # 1. Câu hỏi & dẫn đề
    p0 = cell_l.paragraphs[0]
    p0.paragraph_format.space_before = Pt(4)
    p0.paragraph_format.space_after = Pt(3)
    if q_label:
        r_lbl = p0.add_run(q_label)
        r_lbl.bold = True
        r_lbl.font.size = Pt(font_size)
    add_math_content(p0, q_text, mode=mode, font_size=font_size)

    # 2. Các ý phụ (Phần II: a, b, c, d)
    if sub_items:
        for item in sub_items:
            p_item = cell_l.add_paragraph()
            p_item.paragraph_format.space_before = Pt(0)
            p_item.paragraph_format.space_after = Pt(2)
            add_math_content(p_item, item, mode=mode, font_size=font_size)

    # 3. Các đáp án trắc nghiệm A, B, C, D
    if choices:
        if choices_layout == '2col' and len(choices) == 4:
            p_c1 = cell_l.add_paragraph()
            p_c1.paragraph_format.space_before = Pt(2)
            p_c1.paragraph_format.space_after = Pt(2)
            add_math_content(p_c1, choices[0] + '          ' + choices[1], mode=mode, font_size=font_size)

            p_c2 = cell_l.add_paragraph()
            p_c2.paragraph_format.space_before = Pt(0)
            p_c2.paragraph_format.space_after = Pt(2)
            add_math_content(p_c2, choices[2] + '          ' + choices[3], mode=mode, font_size=font_size)
        else:
            for c in choices:
                p_c = cell_l.add_paragraph()
                p_c.paragraph_format.space_before = Pt(0)
                p_c.paragraph_format.space_after = Pt(2)
                add_math_content(p_c, c, mode=mode, font_size=font_size)

    # 4. Hình vẽ minh họa cột phải
    if img_path and os.path.exists(img_path):
        p_img = cell_r.paragraphs[0]
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(0)
        p_img.paragraph_format.space_after = Pt(0)
        p_img.add_run().add_picture(img_path, width=img_width)

    return table



# ─── Ô GHI KẾT QUẢ HỌC SINH (Phần III) ─────────────────────────────────────

def add_short_answer_box(doc, question_num):
    """Chèn ô trống nhỏ cho học sinh điền kết quả phần Trả lời ngắn."""
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(3)
    p.add_run(f"  Kết quả câu {question_num}: ")
    box = p.add_run("____________")
    box.underline = True
    return p


# ─── BẢNG ĐÁP ÁN NHANH (cuối file lời giải) ─────────────────────────────────

def add_answer_key_grid(doc, part1_answers, part3_answers=None):
    """Tạo bảng ma trận đáp án trắc nghiệm nhanh chuẩn mực."""
    h = doc.add_paragraph()
    h.paragraph_format.space_before = Pt(16)
    r = h.add_run("BẢNG ĐÁP ÁN TRẮC NGHIỆM – MÃ ĐỀ")
    r.bold = True
    r.font.size = Pt(12)
    r.underline = True

    # Phần I
    p_head1 = doc.add_paragraph()
    p_head1.add_run("Phần I:").bold = True
    t1 = doc.add_table(rows=2, cols=len(part1_answers))
    t1.alignment = WD_TABLE_ALIGNMENT.CENTER
    t1.style = 'Table Grid'
    labels_row = t1.row_cells(0)
    ans_row = t1.row_cells(1)
    for i, (q_num, ans) in enumerate(part1_answers):
        _set_cell_center_bold(labels_row[i], str(q_num), bg_color="D6E4F0")
        _set_cell_center_bold(ans_row[i], str(ans), bg_color="FFFFFF", text_color="C0392B")

    # Phần III (nếu có)
    if part3_answers:
        p_head3 = doc.add_paragraph()
        p_head3.paragraph_format.space_before = Pt(8)
        p_head3.add_run("Phần III:").bold = True
        t3 = doc.add_table(rows=2, cols=len(part3_answers))
        t3.alignment = WD_TABLE_ALIGNMENT.CENTER
        t3.style = 'Table Grid'
        for i, (q_num, ans) in enumerate(part3_answers):
            _set_cell_center_bold(t3.row_cells(0)[i], f"III.{q_num}", bg_color="EAF7EA")
            _set_cell_center_bold(t3.row_cells(1)[i], str(ans), bg_color="FFFFFF", text_color="1A6B3A")


def _set_cell_center_bold(cell, text, bg_color=None, text_color=None):
    """Căn giữa, in đậm và tô màu nền cho ô bảng."""
    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(text)
    run.bold = True
    run.font.size = Pt(10.5)
    if text_color:
        r, g, b = int(text_color[:2], 16), int(text_color[2:4], 16), int(text_color[4:], 16)
        run.font.color.rgb = RGBColor(r, g, b)
    if bg_color:
        tcPr = cell._tc.get_or_add_tcPr()
        shd = OxmlElement('w:shd')
        shd.set(qn('w:val'), 'clear')
        shd.set(qn('w:color'), 'auto')
        shd.set(qn('w:fill'), bg_color)
        tcPr.append(shd)


# ─── KIỂM ĐỊNH TÍNH TOÀN VẸN OLE (INTEGRITY AUDIT) ───────────────────────────

def audit_word_ole_file(docx_path):
    """
    Kiểm định tính toàn vẹn của tệp Word MathType OLE:
    - Đếm số lượng đối tượng OLE thực sự (word/embeddings/oleObject*.bin).
    - Quét toàn bộ văn bản (paragraphs và tables) để phát hiện ký tự '$' chưa chuyển đổi.
    Trả về dict: {
        'ok': bool,
        'ole_count': int,
        'residual_count': int,
        'residuals': list,
        'file_size': int
    }
    """
    if not os.path.exists(docx_path):
        return {'ok': False, 'ole_count': 0, 'residual_count': 0, 'residuals': [], 'file_size': 0, 'error': 'File not found'}

    file_size = os.path.getsize(docx_path)
    ole_count = 0
    try:
        import zipfile
        with zipfile.ZipFile(docx_path, 'r') as zf:
            ole_objects = [n for n in zf.namelist() if 'embeddings/oleObject' in n]
            ole_count = len(ole_objects)
    except Exception as e:
        return {'ok': False, 'ole_count': 0, 'residual_count': 0, 'residuals': [], 'file_size': file_size, 'error': str(e)}

    residuals = []
    try:
        doc = Document(docx_path)
        for i, p in enumerate(doc.paragraphs):
            if '$' in p.text:
                residuals.append(f"p_{i}: {p.text[:60]}")
        for t_idx, tbl in enumerate(doc.tables):
            for r_idx, row in enumerate(tbl.rows):
                for c_idx, cell in enumerate(row.cells):
                    if '$' in cell.text:
                        residuals.append(f"tbl_{t_idx}_r{r_idx}_c{c_idx}: {cell.text[:60]}")
    except Exception as e:
        residuals.append(f"Lỗi đọc văn bản docx: {e}")

    ok = (ole_count > 0 and len(residuals) == 0)
    return {
        'ok': ok,
        'ole_count': ole_count,
        'residual_count': len(residuals),
        'residuals': residuals,
        'file_size': file_size
    }


# ─── TIỆN ÍCH BẢNG BIỂU & HÌNH ẢNH SƯ PHẠM ──────────────────────────────────

def add_heading_section(doc, text, level=1):
    """Thêm tiêu đề phân đoạn chuẩn thể thức sư phạm Việt Nam."""
    p = doc.add_paragraph()
    p.paragraph_format.keep_with_next = True
    p.paragraph_format.line_spacing = 1.15
    if level == 1:
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(6)
        r = p.add_run(text)
        r.bold = True
        r.font.name = 'Times New Roman'
        r.font.size = Pt(14.5)
        r.font.color.rgb = RGBColor(192, 57, 43)  # Đỏ đô Bộ GD&ĐT
    else:
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(4)
        r = p.add_run(text)
        r.bold = True
        r.font.name = 'Times New Roman'
        r.font.size = Pt(13.5)
        r.font.color.rgb = RGBColor(26, 82, 118)  # Xanh lam đậm
    return p


def add_styled_table(doc, headers, rows_data, col_widths=None, header_bg="1B4F72", mode='tex'):
    """
    Dựng bảng chuẩn Table Grid sư phạm:
    - Tiêu đề nổi bật với nền màu header_bg và chữ trắng đậm.
    - Dữ liệu xen kẽ nền trắng và xám nhẹ (#F4F6F7).
    - Căn lề và khoảng đệm (padding) chuẩn mực.
    - Hỗ trợ công thức $...$ trong ô bảng (chuyển đổi chuẩn MathType OLE hoặc OMML).
    """
    tbl = doc.add_table(rows=len(rows_data) + 1, cols=len(headers))
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.style = 'Table Grid'
    tbl.autofit = False

    # Header row
    hdr_cells = tbl.rows[0].cells
    for j, h_text in enumerate(headers):
        if col_widths and j < len(col_widths):
            hdr_cells[j].width = col_widths[j]
        tcPr = hdr_cells[j]._tc.get_or_add_tcPr()
        shd = parse_xml(f'<w:shd {docx.oxml.ns.nsdecls("w")} w:fill="{header_bg}"/>')
        tcPr.append(shd)
        set_cell_margins(hdr_cells[j], top=140, bottom=140, left=150, right=150)
        p = hdr_cells[j].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(2)
        r = p.add_run(h_text)
        r.bold = True
        r.font.name = 'Times New Roman'
        r.font.size = Pt(11)
        r.font.color.rgb = RGBColor(255, 255, 255)

    # Data rows
    for i, row in enumerate(rows_data):
        row_cells = tbl.rows[i + 1].cells
        bg = "F4F6F7" if i % 2 == 1 else "FFFFFF"
        for j, val in enumerate(row):
            if col_widths and j < len(col_widths):
                row_cells[j].width = col_widths[j]
            tcPr = row_cells[j]._tc.get_or_add_tcPr()
            shd = parse_xml(f'<w:shd {docx.oxml.ns.nsdecls("w")} w:fill="{bg}"/>')
            tcPr.append(shd)
            set_cell_margins(row_cells[j], top=100, bottom=100, left=140, right=140)
            p = row_cells[j].paragraphs[0]
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.line_spacing = 1.15

            val_str = str(val)
            if j == 0 and len(val_str) > 15:
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            elif any(c in val_str for c in ['=', '<', '>', '$', '(', ')']):
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT

            add_math_content(p, val_str, mode=mode, font_size=10.5)
    return tbl


def add_centered_image(doc, img_path, width=Inches(4.5), caption=None, mode='tex'):
    """Chèn hình ảnh kỹ thuật/thí nghiệm căn giữa kèm chú thích chuẩn SGK."""
    if not img_path or not os.path.exists(img_path):
        return None
    p_img = doc.add_paragraph()
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_img.paragraph_format.space_before = Pt(8)
    p_img.paragraph_format.space_after = Pt(3)
    p_img.paragraph_format.keep_with_next = True
    p_img.add_run().add_picture(img_path, width=width)

    if caption:
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_before = Pt(0)
        p_cap.paragraph_format.space_after = Pt(10)
        p_cap.paragraph_format.line_spacing = 1.15
        r_c = p_cap.add_run(caption)
        r_c.font.name = 'Times New Roman'
        r_c.bold = True
        r_c.italic = True
        r_c.font.size = Pt(11)
        r_c.font.color.rgb = RGBColor(44, 62, 80)
    return p_img


# ─── BACKEND CONVERTER ───────────────────────────────────────────────────────

def convert_to_mathtype_ole_via_backend(base_tex_docx_path, output_ole_docx_path,
                                         api_url=BACKEND_API_URL, timeout=120):
    """
    Gửi DOCX chứa $LaTeX$ lên backend → nhận về MathType OLE nguyên bản.
    [Lớp E] Gửi kèm license_key + machine_id để server xác thực bản quyền.
    Sau khi tải về, tự động chạy kiểm định tính toàn vẹn (Integrity Audit).
    Trả về True nếu thành công và hợp lệ, False nếu thất bại.
    """
    boundary = uuid.uuid4().hex
    headers = {'Content-Type': f'multipart/form-data; boundary={boundary}'}
    with open(base_tex_docx_path, 'rb') as f:
        file_bytes = f.read()

    # ─── LỚP E: Đính kèm thông tin license vào request ─────────────────────
    license_token = _get_license_token()
    machine_id    = _get_machine_id_safe()
    # ────────────────────────────────────────────────────────────────────────

    body = bytearray()
    body.extend(f'--{boundary}\r\n'.encode('utf-8'))
    body.extend(f'Content-Disposition: form-data; name="file"; filename="{os.path.basename(base_tex_docx_path)}"\r\n'.encode('utf-8'))
    body.extend(b'Content-Type: application/vnd.openxmlformats-officedocument.wordprocessingml.document\r\n\r\n')
    body.extend(file_bytes)

    if license_token:
        body.extend(f'\r\n--{boundary}\r\n'.encode('utf-8'))
        body.extend(b'Content-Disposition: form-data; name="license_key"\r\n\r\n')
        body.extend(license_token.encode('utf-8'))
    if machine_id:
        body.extend(f'\r\n--{boundary}\r\n'.encode('utf-8'))
        body.extend(b'Content-Disposition: form-data; name="machine_id"\r\n\r\n')
        body.extend(machine_id.encode('utf-8'))

    body.extend(f'\r\n--{boundary}--\r\n'.encode('utf-8'))

    req = urllib.request.Request(api_url, data=bytes(body), headers=headers, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if resp.status == 200:
                with open(output_ole_docx_path, 'wb') as f:
                    f.write(resp.read())

                # Tự động chạy kiểm định tính toàn vẹn
                audit = audit_word_ole_file(output_ole_docx_path)
                if audit['ok']:
                    print(f"[Backend OLE] ✓ THÀNH CÔNG: {audit['ole_count']} công thức MathType OLE nguyên bản (0 lỗi ký hiệu)")
                else:
                    if audit.get('residuals'):
                    for r in audit['residuals'][:5]:
                        print(f'  !! Con sot $: {r}')
                print(f"[Backend OLE] Canh bao kiem dinh: ole_count={audit['ole_count']}, residual_$= {audit['residual_count']}")
                return True
            else:
                print(f"[Backend OLE] Server trả về mã HTTP {resp.status}")
    except Exception as e:
        print(f"[Backend OLE] Lỗi kết nối API: {e}")
    return False


# ─── NỘI DUNG ĐỀ THI & CHUYÊN ĐỀ CHUẨN GDPT 2018 ───────────────────────────

def _write_exam_body(doc, exam_data, mode='tex', show_answers=False, show_solutions=False):
    """
    Viết nội dung toàn bộ đề thi / chuyên đề vào doc chuẩn cấu trúc GDPT 2018:
    - Phần I: Trắc nghiệm 4 lựa chọn (A, B, C, D)
    - Phần II: Trắc nghiệm Đúng / Sai (a, b, c, d)
    - Phần III: Trả lời ngắn (ô điền kết quả)
    - Phần IV: Tự luận / Bài toán mô hình hóa thực tế
    - Kèm hình vẽ kỹ thuật (standalone hoặc smart side-by-side) và bảng biểu số liệu (Table Grid).
    """
    labels = ['A', 'B', 'C', 'D']

    # 1. TIÊU ĐỀ BÀI HOẶC CHUYÊN ĐỀ (NẾU CÓ)
    if 'title' in exam_data:
        p_title = doc.add_paragraph()
        p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_title.paragraph_format.space_before = Pt(6)
        p_title.paragraph_format.space_after = Pt(4)
        r = p_title.add_run(exam_data['title'])
        r.bold = True
        r.font.name = 'Times New Roman'
        r.font.size = Pt(16)
        r.font.color.rgb = RGBColor(11, 60, 93)

    if 'subtitle' in exam_data:
        p_sub = doc.add_paragraph()
        p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_sub.paragraph_format.space_before = Pt(0)
        p_sub.paragraph_format.space_after = Pt(10)
        r = p_sub.add_run(exam_data['subtitle'])
        r.italic = True
        r.font.name = 'Times New Roman'
        r.font.size = Pt(12)
        r.font.color.rgb = RGBColor(90, 90, 90)

    # 2. PHẦN I: TRẮC NGHIỆM 4 PHƯƠNG ÁN
    part1 = exam_data.get('part1', [])
    if part1:
        add_heading_section(doc, f"PHẦN I. Thí sinh trả lời từ câu 1 đến câu {len(part1)}. Mỗi câu hỏi thí sinh chỉ chọn một phương án.", level=1)
        for i, q in enumerate(part1):
            q_num = i + 1
            stem = q.get('stem', '')
            choices = q.get('choices', [])
            img = q.get('image') or q.get('image_path')
            correct_idx = q.get('correct_idx')
            sol = q.get('solution')
            is_sbs = q.get('is_side_by_side', False)

            if img and os.path.exists(img) and is_sbs and len(choices) == 4:
                add_side_by_side_question(
                    doc=doc,
                    q_label=f"Câu {q_num}: ",
                    q_text=stem,
                    choices=choices,
                    img_path=img,
                    mode=mode,
                    font_size=14
                )
            else:
                p_q = doc.add_paragraph()
                p_q.paragraph_format.space_before = Pt(6)
                p_q.paragraph_format.space_after = Pt(3)
                p_q.paragraph_format.line_spacing = 1.15
                r_num = p_q.add_run(f"Câu {q_num}: ")
                r_num.bold = True
                r_num.font.name = 'Times New Roman'
                r_num.font.size = Pt(14)
                add_math_content(p_q, stem, mode=mode, font_size=14)

                if img and os.path.exists(img):
                    add_centered_image(doc, img, width=Inches(3.8), caption=q.get('image_caption'))

                if choices:
                    add_aligned_choices(doc, choices, mode=mode)

            # Hiển thị đáp án cho bản giáo viên
            if show_answers and correct_idx is not None and 0 <= correct_idx < len(labels):
                p_ans = doc.add_paragraph()
                p_ans.paragraph_format.space_before = Pt(2)
                p_ans.paragraph_format.space_after = Pt(2)
                r_a = p_ans.add_run(f"➤ Chọn đáp án {labels[correct_idx]}")
                r_a.bold = True
                r_a.font.name = 'Times New Roman'
                r_a.font.size = Pt(13)
                r_a.font.color.rgb = RGBColor(192, 57, 43)

            # Hiển thị lời giải cho bản giáo viên
            if show_solutions and sol:
                p_sol = doc.add_paragraph()
                p_sol.paragraph_format.space_before = Pt(2)
                p_sol.paragraph_format.space_after = Pt(6)
                p_sol.paragraph_format.line_spacing = 1.15
                r_s = p_sol.add_run("Lời giải: ")
                r_s.bold = True
                r_s.italic = True
                r_s.font.name = 'Times New Roman'
                r_s.font.size = Pt(13)
                r_s.font.color.rgb = RGBColor(26, 82, 118)
                add_math_content(p_sol, sol, mode=mode, font_size=13.5)

    # 3. PHẦN II: TRẮC NGHIỆM ĐÚNG/SAI
    part2 = exam_data.get('part2', [])
    if part2:
        add_heading_section(doc, f"PHẦN II. Thí sinh trả lời từ câu 1 đến câu {len(part2)}. Trong mỗi ý a), b), c), d) ở mỗi câu, thí sinh chọn đúng hoặc sai.", level=1)
        for i, q in enumerate(part2):
            q_num = i + 1
            stem = q.get('stem', '')
            items = q.get('items', [])
            img = q.get('image') or q.get('image_path')
            sol = q.get('solution')

            p_q = doc.add_paragraph()
            p_q.paragraph_format.space_before = Pt(6)
            p_q.paragraph_format.space_after = Pt(3)
            p_q.paragraph_format.line_spacing = 1.15
            r_num = p_q.add_run(f"Câu {q_num}: ")
            r_num.bold = True
            r_num.font.name = 'Times New Roman'
            r_num.font.size = Pt(14)
            add_math_content(p_q, stem, mode=mode, font_size=14)

            if img and os.path.exists(img):
                add_centered_image(doc, img, width=Inches(3.8), caption=q.get('image_caption'))

            for item in items:
                p_item = doc.add_paragraph()
                p_item.paragraph_format.left_indent = Cm(0.5)
                p_item.paragraph_format.space_before = Pt(1)
                p_item.paragraph_format.space_after = Pt(2)
                p_item.paragraph_format.line_spacing = 1.15

                lbl = item.get('label', 'a') if isinstance(item, dict) else 'a'
                txt = item.get('text', str(item)) if isinstance(item, dict) else str(item)
                is_true = item.get('is_true', None) if isinstance(item, dict) else None

                r_l = p_item.add_run(f"{lbl}) ")
                r_l.bold = True
                r_l.font.name = 'Times New Roman'
                r_l.font.size = Pt(14)
                add_math_content(p_item, txt, mode=mode, font_size=14)

                if show_answers and is_true is not None:
                    tag = " [Đúng]" if is_true else " [Sai]"
                    color = RGBColor(26, 130, 60) if is_true else RGBColor(192, 57, 43)
                    r_t = p_item.add_run(tag)
                    r_t.bold = True
                    r_t.font.name = 'Times New Roman'
                    r_t.font.size = Pt(13)
                    r_t.font.color.rgb = color

            if show_solutions and sol:
                p_sol = doc.add_paragraph()
                p_sol.paragraph_format.space_before = Pt(2)
                p_sol.paragraph_format.space_after = Pt(6)
                p_sol.paragraph_format.line_spacing = 1.15
                r_s = p_sol.add_run("Lời giải chi tiết: ")
                r_s.bold = True
                r_s.italic = True
                r_s.font.name = 'Times New Roman'
                r_s.font.size = Pt(13)
                r_s.font.color.rgb = RGBColor(26, 82, 118)
                add_math_content(p_sol, sol, mode=mode, font_size=13.5)

    # 4. PHẦN III: TRẢ LỜI NGẮN
    part3 = exam_data.get('part3', [])
    if part3:
        add_heading_section(doc, f"PHẦN III. Thí sinh trả lời từ câu 1 đến câu {len(part3)}. Điền kết quả vào ô tương ứng.", level=1)
        for i, q in enumerate(part3):
            q_num = i + 1
            stem = q.get('stem', '')
            ans = q.get('answer', '')
            img = q.get('image') or q.get('image_path')
            sol = q.get('solution')

            p_q = doc.add_paragraph()
            p_q.paragraph_format.space_before = Pt(6)
            p_q.paragraph_format.space_after = Pt(3)
            p_q.paragraph_format.line_spacing = 1.15
            r_num = p_q.add_run(f"Câu {q_num}: ")
            r_num.bold = True
            r_num.font.name = 'Times New Roman'
            r_num.font.size = Pt(14)
            add_math_content(p_q, stem, mode=mode, font_size=14)

            if img and os.path.exists(img):
                add_centered_image(doc, img, width=Inches(3.8), caption=q.get('image_caption'))

            if not show_answers:
                add_short_answer_box(doc, q_num)
            else:
                p_ans = doc.add_paragraph()
                p_ans.paragraph_format.space_before = Pt(2)
                p_ans.paragraph_format.space_after = Pt(2)
                r_a = p_ans.add_run(f"➤ Đáp số: {ans}")
                r_a.bold = True
                r_a.font.name = 'Times New Roman'
                r_a.font.size = Pt(13)
                r_a.font.color.rgb = RGBColor(26, 130, 60)

            if show_solutions and sol:
                p_sol = doc.add_paragraph()
                p_sol.paragraph_format.space_before = Pt(2)
                p_sol.paragraph_format.space_after = Pt(6)
                p_sol.paragraph_format.line_spacing = 1.15
                r_s = p_sol.add_run("Lời giải chi tiết: ")
                r_s.bold = True
                r_s.italic = True
                r_s.font.name = 'Times New Roman'
                r_s.font.size = Pt(13)
                r_s.font.color.rgb = RGBColor(26, 82, 118)
                add_math_content(p_sol, sol, mode=mode, font_size=13.5)

    # 5. PHẦN IV / TỰ LUẬN / BÀI TOÁN THỰC TẾ
    part4 = exam_data.get('part4', []) or exam_data.get('essay', [])
    if part4:
        add_heading_section(doc, "PHẦN IV. TỰ LUẬN VÀ BÀI TOÁN THỰC TẾ", level=1)
        for i, q in enumerate(part4):
            q_num = i + 1
            title = q.get('title', f"Bài toán {q_num}")
            stem = q.get('stem', '') or q.get('text', '')
            sub_qs = q.get('questions', [])
            sol = q.get('solution')
            img = q.get('image') or q.get('image_path')
            tbl_data = q.get('table')

            add_heading_section(doc, f"{q_num}. {title}", level=2)
            if stem:
                p_stem = doc.add_paragraph()
                p_stem.paragraph_format.space_before = Pt(3)
                p_stem.paragraph_format.space_after = Pt(4)
                p_stem.paragraph_format.line_spacing = 1.2
                add_math_content(p_stem, stem, mode=mode, font_size=14)

            if img and os.path.exists(img):
                add_centered_image(doc, img, width=Inches(5.0), caption=q.get('image_caption'))

            if tbl_data:
                add_styled_table(doc, tbl_data.get('headers', []), tbl_data.get('rows', []),
                                 col_widths=tbl_data.get('widths'), mode=mode)

            for sub_q in sub_qs:
                p_sq = doc.add_paragraph()
                p_sq.paragraph_format.left_indent = Cm(0.4)
                p_sq.paragraph_format.space_before = Pt(2)
                p_sq.paragraph_format.space_after = Pt(3)
                p_sq.paragraph_format.line_spacing = 1.15
                add_math_content(p_sq, sub_q, mode=mode, font_size=14)

            if show_solutions and sol:
                add_heading_section(doc, "Lời giải chi tiết và Hướng dẫn chấm:", level=2)
                p_sol = doc.add_paragraph()
                p_sol.paragraph_format.space_before = Pt(2)
                p_sol.paragraph_format.space_after = Pt(6)
                p_sol.paragraph_format.line_spacing = 1.2
                add_math_content(p_sol, sol, mode=mode, font_size=13.5)


# ─── PIPELINE XUẤT 3 ẤN PHẨM ────────────────────────────────────────────────

def _build_student_docx(path, exam_data, code, school_info, exam_title, duration, logo_path, mode):
    """Nội bộ: tạo file DOCX bản học sinh (không có đáp án/lời giải)."""
    doc = init_exam_doc()
    add_exam_header(doc, school_info=school_info, exam_title=exam_title,
                    exam_code=code, duration=duration, logo_path=logo_path)
    _write_exam_body(doc, exam_data, mode=mode, show_answers=False, show_solutions=False)
    doc.save(path)


def _build_teacher_docx(path, exam_data, code, school_info, exam_title, duration, logo_path, mode):
    """Nội bộ: tạo file DOCX bản lời giải giáo viên (có đáp án + barem chi tiết)."""
    doc = init_exam_doc()
    p_gv = doc.add_paragraph()
    p_gv.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_gv = p_gv.add_run("📌  TÀI LIỆU DÀNH RIÊNG CHO GIÁO VIÊN – KHÔNG PHÁT CHO HỌC SINH")
    r_gv.bold = True
    r_gv.font.name = 'Times New Roman'
    r_gv.font.color.rgb = RGBColor(192, 0, 0)
    r_gv.font.size = Pt(11)
    p_gv.paragraph_format.space_after = Pt(4)

    add_exam_header(doc, school_info=school_info, exam_title=exam_title,
                    exam_code=code, duration=duration, logo_path=logo_path)

    # Bảng ma trận đáp án nhanh
    if 'part1_answers' in exam_data:
        add_answer_key_grid(doc, exam_data['part1_answers'], exam_data.get('part3_answers'))

    doc.add_paragraph()
    _write_exam_body(doc, exam_data, mode=mode, show_answers=True, show_solutions=True)
    doc.save(path)


def build_and_export(exam_data, output_dir, exam_code,
                     school_info="SỞ GD&ĐT ....................\nTRƯỜNG THPT ....................",
                     exam_title="ĐỀ KIỂM TRA GIỮA HỌC KỲ I – NĂM HỌC 2024–2025\nMÔN: TOÁN 12",
                     duration="90 phút", logo_path=None,
                     build_teacher_version=True):
    """
    Pipeline xuất trọn bộ ấn phẩm chuẩn từ dữ liệu đề thi:
      1. [code]_DE_HOC_SINH_MATHTYPE_OLE.docx  – Bản phát cho học sinh (MathType OLE)
      2. [code]_LOI_GIAI_GV_MATHTYPE_OLE.docx  – Bản lời giải chi tiết cho giáo viên (MathType OLE)
      3. [code]_WORD_EQ.docx                   – Dự phòng Word Equation (OMML)
    Tự động dọn dẹp file tạm trung gian và chạy kiểm định tính toàn vẹn.
    """
    _require_license()
    os.makedirs(output_dir, exist_ok=True)
    results = {}

    # 1. Build bản đề học sinh (TeX nền → Backend OLE)
    tmp_student = os.path.join(tempfile.gettempdir(), f'_tmp_student_{exam_code}_{uuid.uuid4().hex[:8]}.docx')
    try:
        _build_student_docx(tmp_student, exam_data, exam_code, school_info, exam_title, duration, logo_path, mode='tex')
        out_student = os.path.join(output_dir, f'{exam_code}_DE_HOC_SINH_MATHTYPE_OLE.docx')
        ok = convert_to_mathtype_ole_via_backend(tmp_student, out_student)
        if ok and os.path.exists(out_student):
            audit = audit_word_ole_file(out_student)
            print(f"[OK] Đã xuất bản học sinh MathType OLE: {out_student} ({audit['ole_count']} OLE objects)")
            results['student_ole'] = out_student
            results['student_audit'] = audit
        else:
            print(f"[FALLBACK] Chuyển đổi OLE học sinh không khả dụng, dùng Word Equation.")
    finally:
        if os.path.exists(tmp_student):
            os.remove(tmp_student)

    # 2. Build bản lời giải giáo viên (TeX nền → Backend OLE)
    if build_teacher_version:
        tmp_teacher = os.path.join(tempfile.gettempdir(), f'_tmp_teacher_{exam_code}_{uuid.uuid4().hex[:8]}.docx')
        try:
            _build_teacher_docx(tmp_teacher, exam_data, exam_code, school_info, exam_title, duration, logo_path, mode='tex')
            out_teacher = os.path.join(output_dir, f'{exam_code}_LOI_GIAI_GV_MATHTYPE_OLE.docx')
            ok = convert_to_mathtype_ole_via_backend(tmp_teacher, out_teacher)
            if ok and os.path.exists(out_teacher):
                audit = audit_word_ole_file(out_teacher)
                print(f"[OK] Đã xuất bản lời giải giáo viên MathType OLE: {out_teacher} ({audit['ole_count']} OLE objects)")
                results['teacher_ole'] = out_teacher
                results['teacher_audit'] = audit
        finally:
            if os.path.exists(tmp_teacher):
                os.remove(tmp_teacher)

    # 3. Build bản Word Equation dự phòng (dùng OMML local)
    out_eq = os.path.join(output_dir, f'{exam_code}_WORD_EQ.docx')
    try:
        _build_student_docx(out_eq, exam_data, exam_code, school_info, exam_title, duration, logo_path, mode='omml')
        print(f"[OK] Đã xuất bản dự phòng Word Equation: {out_eq}")
        results['omml_fallback'] = out_eq
    except Exception as e:
        print(f"[Cảnh báo] Không thể tạo bản OMML: {e}")

    return results


def export_exam_to_word_mathtype(exam_data, output_dir, exam_code="101",
                                  school_info="SỞ GD&ĐT ....................\nTRƯỜNG THPT ....................",
                                  exam_title="ĐỀ KIỂM TRA ĐỊNH KỲ – MÔN: TOÁN 12",
                                  duration="90 phút", logo_path=None,
                                  build_teacher_version=True):
    """
    Hàm giao diện cấp cao (Public API) xuất bản trọn bộ tài liệu Word MathType OLE cho toàn bộ skill.
    """
    return build_and_export(
        exam_data=exam_data,
        output_dir=output_dir,
        exam_code=exam_code,
        school_info=school_info,
        exam_title=exam_title,
        duration=duration,
        logo_path=logo_path,
        build_teacher_version=build_teacher_version
    )

