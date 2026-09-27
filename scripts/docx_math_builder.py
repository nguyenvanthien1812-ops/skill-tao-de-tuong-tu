#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Thư Viện Xây Dựng Văn Bản Đề Thi Chuẩn Bộ GD&ĐT - Phiên Bản 2.0
Hỗ trợ: Xuất bản Đề Học Sinh, Lời Giải Chi Tiết, và dọn dẹp file tạm hoàn toàn.
"""

import os
import uuid
import tempfile
import urllib.request
import docx
from docx import Document
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


def add_math_content(paragraph, text, mode='omml', bold=False, font_size=None):
    """Thêm văn bản xen kẽ công thức $...$ vào paragraph Word."""
    parts = text.split('$')
    for i, part in enumerate(parts):
        if not part:
            continue
        if i % 2 == 0:
            run = paragraph.add_run(part)
            if bold:
                run.bold = True
            if font_size:
                run.font.size = Pt(font_size)
        else:
            if mode == 'omml':
                try:
                    omml_xml = latex_to_omml(part)
                    omml_el = parse_xml(omml_xml)
                    paragraph._p.append(omml_el)
                except Exception:
                    run = paragraph.add_run('$' + part + '$')
            else:
                run = paragraph.add_run('$' + part + '$')


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


# ─── BACKEND CONVERTER ───────────────────────────────────────────────────────

def convert_to_mathtype_ole_via_backend(base_tex_docx_path, output_ole_docx_path,
                                         api_url=BACKEND_API_URL, timeout=120):
    """
    Gửi DOCX chứa $LaTeX$ lên backend → nhận về MathType OLE nguyên bản.
    Trả về True nếu thành công, False nếu thất bại.
    """
    boundary = uuid.uuid4().hex
    headers = {'Content-Type': f'multipart/form-data; boundary={boundary}'}
    with open(base_tex_docx_path, 'rb') as f:
        file_bytes = f.read()

    body = bytearray()
    body.extend(f'--{boundary}\r\n'.encode())
    body.extend(f'Content-Disposition: form-data; name="file"; filename="{os.path.basename(base_tex_docx_path)}"\r\n'.encode())
    body.extend(b'Content-Type: application/vnd.openxmlformats-officedocument.wordprocessingml.document\r\n\r\n')
    body.extend(file_bytes)
    body.extend(f'\r\n--{boundary}--\r\n'.encode())

    req = urllib.request.Request(api_url, data=bytes(body), headers=headers, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if resp.status == 200:
                with open(output_ole_docx_path, 'wb') as f:
                    f.write(resp.read())
                return True
    except Exception as e:
        print(f"[Backend OLE] Lỗi kết nối: {e}")
    return False


# ─── PIPELINE XUẤT 3 ẤN PHẨM ────────────────────────────────────────────────

def build_and_export(exam_data, output_dir, exam_code,
                     school_info="SỞ GD&ĐT ....................\nTRƯỜNG THPT ....................",
                     exam_title="ĐỀ KIỂM TRA GIỮA HỌC KỲ I – NĂM HỌC 2024–2025\nMÔN: TOÁN 12",
                     duration="90 phút", logo_path=None,
                     build_teacher_version=True):
    """
    Pipeline xuất trọn bộ ấn phẩm từ dữ liệu đề thi:
      1. [code]_DE_HOC_SINH_OLE.docx  – Bản phát cho học sinh
      2. [code]_LOI_GIAI_GV_OLE.docx  – Bản lời giải chi tiết cho giáo viên
      3. [code]_WORD_EQ.docx          – Dự phòng Word Equation
    Tự động dọn dẹp file tạm trung gian.
    """
    os.makedirs(output_dir, exist_ok=True)
    results = {}

    # Build bản đề học sinh (TeX nền → Backend OLE)
    tmp_student = os.path.join(tempfile.gettempdir(), f'_tmp_student_{exam_code}_{uuid.uuid4().hex[:8]}.docx')
    try:
        _build_student_docx(tmp_student, exam_data, exam_code, school_info, exam_title, duration, logo_path, mode='tex')
        out_student = os.path.join(output_dir, f'{exam_code}_DE_HOC_SINH_OLE.docx')
        ok = convert_to_mathtype_ole_via_backend(tmp_student, out_student)
        if ok:
            print(f"[OK] Đã xuất: {out_student}")
            results['student_ole'] = out_student
        else:
            print(f"[FALLBACK] Dùng Word Equation cho bản học sinh.")
    finally:
        if os.path.exists(tmp_student):
            os.remove(tmp_student)

    # Build bản lời giải giáo viên
    if build_teacher_version:
        tmp_teacher = os.path.join(tempfile.gettempdir(), f'_tmp_teacher_{exam_code}_{uuid.uuid4().hex[:8]}.docx')
        try:
            _build_teacher_docx(tmp_teacher, exam_data, exam_code, school_info, exam_title, duration, logo_path, mode='tex')
            out_teacher = os.path.join(output_dir, f'{exam_code}_LOI_GIAI_GV_OLE.docx')
            ok = convert_to_mathtype_ole_via_backend(tmp_teacher, out_teacher)
            if ok:
                print(f"[OK] Đã xuất: {out_teacher}")
                results['teacher_ole'] = out_teacher
        finally:
            if os.path.exists(tmp_teacher):
                os.remove(tmp_teacher)

    # Build bản Word Equation dự phòng (dùng OMML local)
    out_eq = os.path.join(output_dir, f'{exam_code}_WORD_EQ.docx')
    _build_student_docx(out_eq, exam_data, exam_code, school_info, exam_title, duration, logo_path, mode='omml')
    print(f"[OK] Đã xuất bản dự phòng: {out_eq}")
    results['omml_fallback'] = out_eq

    return results


def _build_student_docx(path, exam_data, code, school_info, exam_title, duration, logo_path, mode):
    """Nội bộ: tạo file DOCX bản học sinh (không có đáp án)."""
    doc = init_exam_doc()
    add_exam_header(doc, school_info=school_info, exam_title=exam_title,
                    exam_code=code, duration=duration, logo_path=logo_path)
    _write_exam_body(doc, exam_data, mode=mode, show_answers=False, show_solutions=False)
    doc.save(path)


def _build_teacher_docx(path, exam_data, code, school_info, exam_title, duration, logo_path, mode):
    """Nội bộ: tạo file DOCX bản lời giải giáo viên (có đáp án + barem)."""
    doc = init_exam_doc()
    # Thêm dòng nhận diện "TÀI LIỆU GIÁO VIÊN"
    p_gv = doc.add_paragraph()
    p_gv.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_gv = p_gv.add_run("📌  TÀI LIỆU DÀNH RIÊNG CHO GIÁO VIÊN – KHÔNG PHÁT CHO HỌC SINH")
    r_gv.bold = True
    r_gv.font.color.rgb = RGBColor(192, 0, 0)
    r_gv.font.size = Pt(11)
    p_gv.paragraph_format.space_after = Pt(4)

    add_exam_header(doc, school_info=school_info, exam_title=exam_title,
                    exam_code=code, duration=duration, logo_path=logo_path)

    # Bảng đáp án nhanh trước khi vào nội dung
    if 'part1_answers' in exam_data:
        add_answer_key_grid(doc, exam_data['part1_answers'], exam_data.get('part3_answers'))

    doc.add_paragraph()
    _write_exam_body(doc, exam_data, mode=mode, show_answers=True, show_solutions=True)
    doc.save(path)


def _write_exam_body(doc, exam_data, mode='tex', show_answers=False, show_solutions=False):
    """Viết nội dung toàn bộ đề thi vào doc (dùng chung cho cả 2 bản)."""
    # Hàm này sẽ được AI agent tùy biến khi sinh script tạo đề cụ thể.
    # Ở đây chỉ định nghĩa interface và placeholder.
    pass
