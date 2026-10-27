# -*- coding: utf-8 -*-
"""
report_generator.py
───────────────────
Xuất Báo cáo Thẩm định ra file Word (chuẩn biên bản Hội đồng bộ môn)
và file Excel (dashboard tiêu chí).

Bao gồm:
  - generate_word_report(rpt, data, out_path) → DOCX
  - generate_excel_report(rpt, data, out_path) → XLSX
  - generate_correction_plan(rpt, data)        → str (hiển thị trong chat)
"""
from __future__ import annotations
import os
import sys
from datetime import date

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tham_dinh.exam_validator import ValidationReport, FindingItem, SEVERITY_ERROR, SEVERITY_WARNING
from tham_dinh.exam_extractor  import ExamData

try:
    import docx
    from docx import Document
    from docx.shared import Pt, Cm, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False

try:
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    HAS_XLSX = True
except ImportError:
    HAS_XLSX = False


# ──────────────────────────────────────────────────────────────────────────────
# HELPER: tạo ô bảng Word có background
# ──────────────────────────────────────────────────────────────────────────────

def _set_cell_bg(cell, hex_color: str):
    from docx.oxml.ns import qn
    from docx.oxml import parse_xml
    shd = parse_xml(
        f'<w:shd xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
        f'w:val="clear" w:color="auto" w:fill="{hex_color}"/>'
    )
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    for old in tcPr.findall(qn('w:shd')):
        tcPr.remove(old)
    tcPr.append(shd)


def _add_cell_text(cell, text, bold=False, size=11, color_hex=None, align=None):
    p = cell.paragraphs[0]
    p.clear()
    if align == 'center':
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(text)
    run.bold = bold
    run.font.name = 'Times New Roman'
    run.font.size = Pt(size)
    if color_hex:
        r, g, b = int(color_hex[:2], 16), int(color_hex[2:4], 16), int(color_hex[4:], 16)
        run.font.color.rgb = RGBColor(r, g, b)


# ──────────────────────────────────────────────────────────────────────────────
# WORD REPORT
# ──────────────────────────────────────────────────────────────────────────────

def generate_word_report(
    rpt: ValidationReport,
    data: ExamData,
    out_path: str,
    school_name: str = "",
    teacher_name: str = "",
    exam_subject: str = "Toán",
    exam_grade: str = ""
) -> str:
    """Xuất biên bản thẩm định ra file Word."""
    if not HAS_DOCX:
        return ""

    doc = Document()

    # Cài lề trang
    for section in doc.sections:
        section.top_margin    = Cm(2.0)
        section.bottom_margin = Cm(2.0)
        section.left_margin   = Cm(2.5)
        section.right_margin  = Cm(2.0)

    # ── Tiêu đề ──────────────────────────────────────────────────────────────
    # Bảng 2 cột: trường bên trái, CHXHCNVN bên phải
    header_tbl = doc.add_table(rows=1, cols=2)
    header_tbl.style = 'Table Grid'
    lc = header_tbl.cell(0, 0)
    rc = header_tbl.cell(0, 1)
    lc.text = f"TRƯỜNG THCS {school_name.upper() if school_name else '.....................'}\nTỔ TOÁN – TIN"
    rc.text = "CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM\nĐộc Lập – Tự Do – Hạnh Phúc\n─────────────────────"
    for cell in [lc, rc]:
        for p in cell.paragraphs:
            for run in p.runs:
                run.font.name = 'Times New Roman'
                run.font.size = Pt(11)
                run.bold = True

    doc.add_paragraph()

    # Tiêu đề biên bản
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p_title.add_run("THÔNG BÁO\nKẾT QUẢ THẨM ĐỊNH ĐỀ KIỂM TRA GIỮA HỌC KỲ I")
    r.bold = True
    r.font.name = 'Times New Roman'
    r.font.size = Pt(14)

    # Thông tin đề
    info_lines = [
        f"1. Giáo viên ra đề: {teacher_name if teacher_name else '................................................................'}",
        f"2. Môn / Lớp: {exam_subject} {exam_grade} – Mã đề: {data.exam_code or '...'}",
        f"3. Ngày thẩm định: {date.today().strftime('%d/%m/%Y')}",
    ]
    for line in info_lines:
        p = doc.add_paragraph()
        r = p.add_run(line)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(12)

    doc.add_paragraph()

    # ── Kết luận tổng hợp ────────────────────────────────────────────────────
    p_kl = doc.add_paragraph()
    r_kl = p_kl.add_run(f"Kết luận: {rpt.summary}")
    r_kl.bold = True
    r_kl.font.name = 'Times New Roman'
    r_kl.font.size = Pt(12.5)
    if rpt.overall_pass:
        r_kl.font.color.rgb = RGBColor(0x1E, 0x87, 0x49)   # xanh lá
    else:
        r_kl.font.color.rgb = RGBColor(0xC0, 0x39, 0x2B)   # đỏ

    doc.add_paragraph()

    # ── Bảng chi tiết ────────────────────────────────────────────────────────
    p_h = doc.add_paragraph()
    r_h = p_h.add_run("BẢNG CHI TIẾT TỪNG HẠNG MỤC KIỂM TRA:")
    r_h.bold = True
    r_h.font.name = 'Times New Roman'
    r_h.font.size = Pt(12)

    tbl = doc.add_table(rows=1, cols=4)
    tbl.style = 'Table Grid'
    # Header
    headers = ["Nhóm / Mã", "Tiêu chí kiểm tra", "Kết quả phát hiện", "Đề nghị sửa"]
    header_bg = "1B4F72"
    for i, h in enumerate(headers):
        cell = tbl.cell(0, i)
        _set_cell_bg(cell, header_bg)
        _add_cell_text(cell, h, bold=True, size=11, color_hex="FFFFFF", align='center')

    # Set column widths
    from docx.oxml.ns import qn
    from docx.oxml  import parse_xml

    col_widths_cm = [2.0, 4.5, 5.5, 4.5]

    failures = [f for f in rpt.findings if f.status != "PASS"]
    passes   = [f for f in rpt.findings if f.status == "PASS"]

    # Chỉ ghi các mục LỖI/CẢNH BÁO (PASS không cần in ra)
    for item in sorted(failures, key=lambda x: x.code):
        row = tbl.add_row()
        bg = "FADBD8" if item.severity == SEVERITY_ERROR else "FEF9E7"
        icon = "❌" if item.severity == SEVERITY_ERROR else "⚠️"
        _set_cell_bg(row.cells[0], bg)
        _add_cell_text(row.cells[0], f"{icon} {item.code}\n({item.group})", size=10)
        _add_cell_text(row.cells[1], item.criterion, size=10)
        _add_cell_text(row.cells[2], item.result, size=10,
                       color_hex="C0392B" if item.severity == SEVERITY_ERROR else "7D6608")
        _add_cell_text(row.cells[3], item.suggestion, size=10)

    # Nếu không có lỗi
    if not failures:
        row = tbl.add_row()
        _set_cell_bg(row.cells[0], "D5F5E3")
        _add_cell_text(row.cells[0], "✅ TẤT CẢ", bold=True, size=11)
        row.cells[1].merge(row.cells[2]).merge(row.cells[3])
        _add_cell_text(row.cells[1], f"Đạt toàn bộ {rpt.total} tiêu chí — Đề đạt chuẩn xuất sắc.",
                       bold=True, size=11, color_hex="1E8749")

    doc.add_paragraph()

    # Thống kê
    p_stat = doc.add_paragraph()
    p_stat.add_run(
        f"Tổng tiêu chí kiểm tra: {rpt.total}  |  "
        f"✅ Đạt: {rpt.passed}  |  "
        f"❌ Lỗi bắt buộc: {rpt.failed_critical}  |  "
        f"⚠️ Cảnh báo: {rpt.failed_warning}"
    ).font.size = Pt(11)

    # Phần ký duyệt
    doc.add_paragraph()
    sign_tbl = doc.add_table(rows=3, cols=3)
    sign_tbl.style = 'Table Grid'
    sign_headers = ["HIỆU TRƯỞNG / BGH DUYỆT", "TỔ TRƯỞNG CHUYÊN MÔN", "NGƯỜI THẨM ĐỊNH"]
    for i, sh in enumerate(sign_headers):
        _add_cell_text(sign_tbl.cell(0, i), sh, bold=True, size=11, align='center')
    for i in range(3):
        _add_cell_text(sign_tbl.cell(1, i), "(Ký, đóng dấu)", size=10, align='center')
        _add_cell_text(sign_tbl.cell(2, i), "\n\n\n", size=11)   # khoảng ký

    doc.save(out_path)
    print(f"[Report] ✓ Đã xuất biên bản Word: {out_path}")
    return out_path


# ──────────────────────────────────────────────────────────────────────────────
# EXCEL DASHBOARD
# ──────────────────────────────────────────────────────────────────────────────

def generate_excel_report(
    rpt: ValidationReport,
    data: ExamData,
    out_path: str
) -> str:
    """Xuất dashboard tiêu chí ra file Excel."""
    if not HAS_XLSX:
        return ""

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Kết quả thẩm định"

    # Style
    hdr_font  = Font(name='Times New Roman', bold=True, color="FFFFFF", size=11)
    hdr_fill  = PatternFill("solid", fgColor="1B4F72")
    err_fill  = PatternFill("solid", fgColor="FADBD8")
    warn_fill = PatternFill("solid", fgColor="FEF9E7")
    pass_fill = PatternFill("solid", fgColor="D5F5E3")
    center    = Alignment(horizontal='center', vertical='center', wrap_text=True)
    left      = Alignment(horizontal='left',   vertical='center', wrap_text=True)
    thin_border = Border(
        left=Side(style='thin'), right=Side(style='thin'),
        top=Side(style='thin'),  bottom=Side(style='thin')
    )

    # Header
    headers = ["Mã", "Nhóm", "Tiêu chí kiểm tra", "Kết quả phát hiện",
               "Trạng thái", "Mức độ", "Có thể Auto-fix", "Đề nghị sửa"]
    ws.append(headers)
    for col_idx, _ in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_idx)
        cell.font  = hdr_font
        cell.fill  = hdr_fill
        cell.alignment = center
        cell.border = thin_border

    ws.column_dimensions['A'].width = 8
    ws.column_dimensions['B'].width = 18
    ws.column_dimensions['C'].width = 32
    ws.column_dimensions['D'].width = 36
    ws.column_dimensions['E'].width = 12
    ws.column_dimensions['F'].width = 18
    ws.column_dimensions['G'].width = 14
    ws.column_dimensions['H'].width = 36

    for r_idx, item in enumerate(rpt.findings, 2):
        row_data = [
            item.code,
            item.group,
            item.criterion,
            item.result,
            "✅ ĐẠT"  if item.status == "PASS"
                else ("❌ LỖI" if item.severity == SEVERITY_ERROR else "⚠️ CẢNH BÁO"),
            item.severity,
            "✅ Có" if item.fixable else "—",
            item.suggestion
        ]
        ws.append(row_data)

        fill = pass_fill if item.status == "PASS" else (err_fill if item.severity == SEVERITY_ERROR else warn_fill)
        for col_idx in range(1, len(row_data) + 1):
            cell = ws.cell(row=r_idx, column=col_idx)
            cell.fill   = fill
            cell.border = thin_border
            cell.alignment = center if col_idx in (1, 5, 6, 7) else left
            cell.font   = Font(name='Times New Roman', size=10)

    # Summary row
    ws.append([])
    ws.append(["TỔNG KẾT", "", "",
                f"✅ Đạt: {rpt.passed}/{rpt.total}  |  "
                f"❌ Lỗi bắt buộc: {rpt.failed_critical}  |  "
                f"⚠️ Cảnh báo: {rpt.failed_warning}",
                "XUẤT SẮC" if rpt.overall_pass and rpt.failed_warning == 0
                    else ("ĐẠT" if rpt.overall_pass else "CHƯA ĐẠT"),
                "", "", rpt.summary])

    wb.save(out_path)
    print(f"[Report] ✓ Đã xuất dashboard Excel: {out_path}")
    return out_path


# ──────────────────────────────────────────────────────────────────────────────
# CORRECTION PLAN (hiển thị trong chat cho GV duyệt)
# ──────────────────────────────────────────────────────────────────────────────

def generate_correction_plan(rpt: ValidationReport, data: ExamData) -> str:
    """
    Tạo kế hoạch sửa chữa dạng văn bản để hiển thị cho giáo viên duyệt trước khi auto-fix.
    Trả về chuỗi markdown đẹp.
    """
    failures = rpt.get_failures()
    if not failures:
        return (
            f"## ✅ ĐỀ KIỂM TRA ĐẠT CHUẨN HOÀN TOÀN\n\n"
            f"Toàn bộ **{rpt.total} tiêu chí** đều đạt yêu cầu. "
            f"Đề thi sẵn sàng in ấn và sử dụng ngay.\n\n"
            f"> **Tổng kết:** {rpt.summary}"
        )

    lines = [
        f"## 📋 KẾ HOẠCH SỬA CHỮA ĐỀ KIỂM TRA (MÃ ĐỀ {data.exam_code or '???'})",
        "",
        f"> **Kết quả tổng hợp:** {rpt.summary}",
        f"> **Tiêu chí đạt:** {rpt.passed}/{rpt.total}  |  "
        f"**Lỗi bắt buộc:** {rpt.failed_critical}  |  "
        f"**Cảnh báo:** {rpt.failed_warning}",
        "",
    ]

    # Phân loại
    critical = [f for f in failures if f.severity == SEVERITY_ERROR]
    warnings = [f for f in failures if f.severity != SEVERITY_ERROR]
    fixable  = rpt.get_fixable()

    if critical:
        lines.append("### ❌ CÁC LỖI BẮT BUỘC PHẢI SỬA TRƯỚC KHI NỘP TỔ CHUYÊN MÔN")
        lines.append("")
        for i, item in enumerate(critical, 1):
            auto = " *(Có thể Auto-fix)*" if item.fixable else ""
            lines.append(f"**{i}. [{item.code}]** {item.criterion}{auto}")
            lines.append(f"   - 🔍 Phát hiện: {item.result}")
            lines.append(f"   - 💊 Cách sửa: {item.suggestion}")
            lines.append("")

    if warnings:
        lines.append("### ⚠️ CÁC CẢNH BÁO CẦN LƯU Ý (Khuyên sửa để hoàn thiện hơn)")
        lines.append("")
        for i, item in enumerate(warnings, 1):
            auto = " *(Có thể Auto-fix)*" if item.fixable else ""
            lines.append(f"**{i}. [{item.code}]** {item.criterion}{auto}")
            lines.append(f"   - 🔍 Phát hiện: {item.result}")
            lines.append(f"   - 💊 Cách sửa: {item.suggestion}")
            lines.append("")

    if fixable:
        lines.append("---")
        lines.append(f"### 🤖 AUTO-FIX KHẢ DỤNG ({len(fixable)} hạng mục có thể sửa tự động)")
        lines.append("")
        lines.append("Hệ thống có thể tự động sửa các lỗi sau **ngay sau khi Thầy/Cô xác nhận**:")
        lines.append("")
        for i, item in enumerate(fixable, 1):
            lines.append(f"- **Fix {i} [{item.code}]:** {item.fix_action}")
        lines.append("")
        lines.append(f"> 👉 **Thầy/Cô trả lời `OK` hoặc `Đồng ý` để em tự động sửa toàn bộ {len(fixable)} hạng mục trên.**")
        lines.append("> Hoặc Thầy/Cô có thể gõ số thứ tự các hạng mục muốn bỏ qua (ví dụ: `Bỏ qua 2, 3`).")
    else:
        lines.append("---")
        lines.append("### 🛠️ CÁC LỖI CẦN SỬA THỦ CÔNG")
        lines.append("")
        lines.append("Các lỗi trên đây cần Thầy/Cô sửa trực tiếp trong file Word. "
                     "Sau khi sửa xong, gửi lại file để em thẩm định lần 2.")

    return "\n".join(lines)


# ──────────────────────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────────────────────

def run_full_report(
    rpt: ValidationReport,
    data: ExamData,
    output_dir: str,
    school_name: str = "",
    teacher_name: str = "",
    exam_grade: str = "8"
) -> dict:
    os.makedirs(output_dir, exist_ok=True)
    code = data.exam_code or "XXX"

    word_path  = os.path.join(output_dir, f"Bien_ban_tham_dinh_Toan{exam_grade}_Ma{code}.docx")
    excel_path = os.path.join(output_dir, f"Dashboard_tham_dinh_Toan{exam_grade}_Ma{code}.xlsx")

    generate_word_report(rpt, data, word_path, school_name, teacher_name, "Toán", exam_grade)
    generate_excel_report(rpt, data, excel_path)
    correction_md = generate_correction_plan(rpt, data)

    return {
        "word_path":     word_path,
        "excel_path":    excel_path,
        "correction_md": correction_md,
        "rpt":           rpt
    }
