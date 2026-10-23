import sys, os, json
from pathlib import Path
from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import qn

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "references" / "default_matrices.json"


def _set_cell_style(cell, text, bold=False, font_size=10, align=WD_ALIGN_PARAGRAPH.CENTER,
                    bg_color=None, italic=False, text_color=None):
    cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
    cell.text = ""
    p = cell.paragraphs[0]
    p.alignment = align
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.15
    run = p.add_run(str(text))
    run.font.name = 'Times New Roman'
    run.font.size = Pt(font_size)
    run.bold = bold
    run.italic = italic
    if text_color:
        run.font.color.rgb = RGBColor(*text_color)

    tcPr = cell._tc.get_or_add_tcPr()
    if bg_color:
        for old_shd in tcPr.findall(qn('w:shd')):
            tcPr.remove(old_shd)
        shd = OxmlElement('w:shd')
        shd.set(qn('w:val'), 'clear')
        shd.set(qn('w:color'), 'auto')
        shd.set(qn('w:fill'), bg_color)
        tcPr.append(shd)


# Thứ tự phần tử con chuẩn theo schema OOXML (Word có thể báo lỗi / bỏ viền nếu sai thứ tự)
_TCPR_ORDER = ['cnfStyle', 'tcW', 'gridSpan', 'hMerge', 'vMerge', 'tcBorders', 'shd', 'noWrap',
               'tcMar', 'textDirection', 'tcFitText', 'vAlign', 'hideMark']
_TBLPR_ORDER = ['tblStyle', 'tblpPr', 'tblOverlap', 'bidiVisual', 'tblStyleRowBandSize',
                'tblStyleColBandSize', 'tblW', 'jc', 'tblCellSpacing', 'tblInd', 'tblBorders',
                'shd', 'tblLayout', 'tblCellMar', 'tblLook', 'tblCaption', 'tblDescription']


def _reorder_children(el, order):
    """Sắp xếp lại phần tử con của el theo `order` (phần tử lạ giữ nguyên ở cuối)."""
    def key(child):
        tag = child.tag.split('}')[-1]
        return order.index(tag) if tag in order else len(order)
    children = list(el)
    ordered = sorted(children, key=key)  # sorted ổn định
    if ordered != children:
        for c in children:
            el.remove(c)
        for c in ordered:
            el.append(c)


def _dedupe_merged_cell_paragraphs(table):
    """
    python-docx cộng dồn đoạn văn của các ô khi gộp (merge): ô TT/Chủ đề/Bài học gộp dọc N dòng
    sẽ hiện lặp lại N lần ("1 1 1 1"), ô gộp ngang có thêm đoạn trống làm cao dòng.
    Giữ lại mỗi đoạn có chữ đúng 1 lần (theo thứ tự), bỏ đoạn trống/lặp (luôn giữ >= 1 đoạn).
    """
    W = qn('w:p')
    for tr in table._tbl.tr_lst:
        for tc in tr.tc_lst:
            tcPr = tc.tcPr
            if tcPr is None:
                continue
            vm = tcPr.find(qn('w:vMerge'))
            is_merged = tcPr.find(qn('w:gridSpan')) is not None or (vm is not None and vm.get(qn('w:val')) == 'restart')
            if not is_merged:
                continue
            paras = tc.findall(W)
            if len(paras) <= 1:
                continue
            seen, keep = set(), []
            for para in paras:
                txt = ''.join(x.text or '' for x in para.iter(qn('w:t')))
                has_break = para.find('.//' + qn('w:br')) is not None
                if not txt.strip() and not has_break:
                    continue
                if txt in seen:
                    continue
                seen.add(txt)
                keep.append(para)
            if not keep:
                keep = [paras[0]]
            for para in paras:
                if para not in keep and len(tc.findall(W)) > 1:
                    tc.remove(para)


def enforce_perfect_table_borders(table, header_rows=3, border_color="000000", border_sz="4"):
    """
    Đảm bảo 100% bảng Word (kể cả mọi ô gộp dọc vMerge và gộp ngang gridSpan)
    có đầy đủ đường kẻ viền 4 cạnh sắc nét, đồng bộ màu nền ô gộp,
    không bị cắt đứt dòng khi qua trang (cantSplit) và lặp lại tiêu đề bảng (tblHeader).
    """
    _dedupe_merged_cell_paragraphs(table)
    tblPr = table._tbl.tblPr
    old_borders = tblPr.find(qn('w:tblBorders'))
    if old_borders is not None:
        tblPr.remove(old_borders)
    tblPr.append(parse_xml(
        f'<w:tblBorders xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        f'<w:top w:val="single" w:sz="{border_sz}" w:space="0" w:color="{border_color}"/>'
        f'<w:left w:val="single" w:sz="{border_sz}" w:space="0" w:color="{border_color}"/>'
        f'<w:bottom w:val="single" w:sz="{border_sz}" w:space="0" w:color="{border_color}"/>'
        f'<w:right w:val="single" w:sz="{border_sz}" w:space="0" w:color="{border_color}"/>'
        f'<w:insideH w:val="single" w:sz="{border_sz}" w:space="0" w:color="{border_color}"/>'
        f'<w:insideV w:val="single" w:sz="{border_sz}" w:space="0" w:color="{border_color}"/>'
        f'</w:tblBorders>'
    ))

    col_active_fill = {}
    for r_idx, tr in enumerate(table._tbl.tr_lst):
        trPr = tr.get_or_add_trPr()
        if trPr.find(qn('w:cantSplit')) is None:
            trPr.append(OxmlElement('w:cantSplit'))
        if r_idx < header_rows and trPr.find(qn('w:tblHeader')) is None:
            trPr.append(OxmlElement('w:tblHeader'))

        grid_col = 0
        for tc in tr.tc_lst:
            tcPr = tc.get_or_add_tcPr()
            gridSpan_el = tcPr.find(qn('w:gridSpan'))
            span = int(gridSpan_el.get(qn('w:val'))) if gridSpan_el is not None else 1

            for old_b in tcPr.findall(qn('w:tcBorders')):
                tcPr.remove(old_b)
            tcPr.append(parse_xml(
                f'<w:tcBorders xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
                f'<w:top w:val="single" w:sz="{border_sz}" w:space="0" w:color="{border_color}"/>'
                f'<w:left w:val="single" w:sz="{border_sz}" w:space="0" w:color="{border_color}"/>'
                f'<w:bottom w:val="single" w:sz="{border_sz}" w:space="0" w:color="{border_color}"/>'
                f'<w:right w:val="single" w:sz="{border_sz}" w:space="0" w:color="{border_color}"/>'
                f'</w:tcBorders>'
            ))

            vMerge_el = tcPr.find(qn('w:vMerge'))
            shd_el = tcPr.find(qn('w:shd'))
            if vMerge_el is not None:
                vm_val = vMerge_el.get(qn('w:val'))
                if vm_val == 'restart':
                    fill_color = shd_el.get(qn('w:fill')) if shd_el is not None else None
                    for c_i in range(grid_col, grid_col + span):
                        col_active_fill[c_i] = fill_color
                else:
                    inherit_fill = col_active_fill.get(grid_col)
                    if inherit_fill and shd_el is None:
                        tcPr.append(parse_xml(
                            f'<w:shd xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
                            f'w:val="clear" w:color="auto" w:fill="{inherit_fill}"/>'
                        ))
            else:
                for c_i in range(grid_col, grid_col + span):
                    col_active_fill.pop(c_i, None)

            _reorder_children(tcPr, _TCPR_ORDER)
            grid_col += span

    _reorder_children(tblPr, _TBLPR_ORDER)


def _set_table_borders(table, color="000000", sz="4", val="single"):
    enforce_perfect_table_borders(table, header_rows=1, border_color=color, border_sz=sz)


def export_matrix_to_docx(matrix_key, output_path=None):
    """Xuất Word Ma trận + Bản đặc tả từ một khóa trong references/default_matrices.json."""
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Không tìm thấy: {DB_PATH}")
    data = json.loads(DB_PATH.read_text(encoding='utf-8'))
    if matrix_key not in data:
        raise KeyError(f"Không tìm thấy ma trận: {matrix_key}")
    return export_matrix_dict_to_docx(data[matrix_key], output_path, matrix_key=matrix_key)


def export_matrix_dict_to_docx(m, output_path=None, matrix_key="matrix"):
    """
    Xuất Word Ma trận + Bản đặc tả từ DICT ma trận (cùng schema với default_matrices.json /
    MatrixParser._normalize). Đây là ĐƯỜNG DUY NHẤT dựng bảng -> mọi ma trận (kho chuẩn hay do
    giáo viên cung cấp) đều tự động đúng chuẩn: 1 mức độ/1 dòng, đủ dòng tổng kết, viền liền nét.
    """
    try:
        _d = os.path.dirname(os.path.abspath(__file__))
        if _d not in sys.path:
            sys.path.insert(0, _d)
        from license_manager import require_valid_license
        require_valid_license("matrix_exam")
    except ImportError:
        pass

    subj = str(m.get("subject", "Môn học")).capitalize()
    grade = m.get("grade", 12)
    duration = m.get("duration_minutes", 90)
    cells = m.get("cells", [])

    doc = Document()

    # Page Setup: A4 Landscape
    section = doc.sections[0]
    section.orientation = 1  # Landscape
    section.page_width = Cm(29.7)
    section.page_height = Cm(21.0)
    section.top_margin = Cm(1.5)
    section.bottom_margin = Cm(1.5)
    section.left_margin = Cm(2.0)
    section.right_margin = Cm(1.5)

    # Header School/Department
    t_head = doc.add_table(rows=1, cols=2)
    t_head.alignment = WD_TABLE_ALIGNMENT.CENTER
    _set_cell_style(
        t_head.rows[0].cells[0],
        "SỞ GD&ĐT / PHÒNG GD&ĐT ........................\nTRƯỜNG ........................................................",
        bold=True, font_size=11, align=WD_ALIGN_PARAGRAPH.CENTER
    )
    _set_cell_style(
        t_head.rows[0].cells[1],
        "CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM\nĐộc lập - Tự do - Hạnh phúc",
        bold=True, font_size=11, align=WD_ALIGN_PARAGRAPH.CENTER
    )

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(6)
    p_title.paragraph_format.space_after = Pt(4)
    r_t = p_title.add_run("KHUNG MA TRẬN VÀ BẢN ĐẶC TẢ ĐỀ KIỂM TRA ĐỊNH KỲ\n")
    r_t.font.name = 'Times New Roman'
    r_t.font.size = Pt(13)
    r_t.bold = True

    r_sub = p_title.add_run(f"MÔN: {subj.upper()} {grade} — THỜI GIAN LÀM BÀI: {duration} PHÚT (CHUẨN GDPT 2018)")
    r_sub.font.name = 'Times New Roman'
    r_sub.font.size = Pt(11.5)
    r_sub.bold = True

    # Group cells by topic_display / unit
    # 21 columns for Table 1:
    # 0: TT | 1: Chủ đề | 2: Nội dung/Đơn vị KT |
    # 3,4,5: Phần I (B, H, VD) | 6,7,8: Phần II (B, H, VD) | 9,10,11: Phần III (B, H, VD) | 12,13,14,15: Phần IV (B, H, VD, VDC) |
    # 16,17,18,19: Tổng số câu/ý (B, H, VD, VDC) | 20: Tỉ lệ % điểm
    p_sec1 = doc.add_paragraph()
    p_sec1.paragraph_format.space_before = Pt(6)
    p_sec1.paragraph_format.space_after = Pt(4)
    r_s1 = p_sec1.add_run(f"1. KHUNG MA TRẬN ĐỀ KIỂM TRA ĐỊNH KÌ ({duration} PHÚT - 10,0 ĐIỂM)")
    r_s1.font.name = 'Times New Roman'
    r_s1.font.size = Pt(12)
    r_s1.bold = True

    t1 = doc.add_table(rows=3, cols=21)
    t1.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr_bg = "EBF1F5"

    # Row 0 headers
    _set_cell_style(t1.cell(0, 0), "TT", bold=True, font_size=10, bg_color=hdr_bg)
    _set_cell_style(t1.cell(0, 1), "Chủ đề / Mạch kiến thức", bold=True, font_size=10, bg_color=hdr_bg)
    _set_cell_style(t1.cell(0, 2), "Nội dung / Đơn vị kiến thức", bold=True, font_size=10, bg_color=hdr_bg)
    _set_cell_style(t1.cell(0, 3), "MỨC ĐỘ ĐÁNH GIÁ (SỐ CÂU / LỆNH HỎI)", bold=True, font_size=10, bg_color=hdr_bg)
    _set_cell_style(t1.cell(0, 16), "Tổng số câu / ý", bold=True, font_size=10, bg_color=hdr_bg)
    _set_cell_style(t1.cell(0, 20), "Tỉ lệ %\nđiểm", bold=True, font_size=10, bg_color=hdr_bg)

    # Row 1 headers
    _set_cell_style(t1.cell(1, 3), "Phần I. Nhiều lựa chọn", bold=True, font_size=9.5, bg_color=hdr_bg)
    _set_cell_style(t1.cell(1, 6), "Phần II. Đúng/Sai", bold=True, font_size=9.5, bg_color=hdr_bg)
    _set_cell_style(t1.cell(1, 9), "Phần III. Trả lời ngắn", bold=True, font_size=9.5, bg_color=hdr_bg)
    _set_cell_style(t1.cell(1, 12), "Phần IV. Tự luận", bold=True, font_size=9.5, bg_color=hdr_bg)
    for idx_c, lbl in enumerate(["B", "H", "VD", "VDC"], start=16):
        _set_cell_style(t1.cell(1, idx_c), lbl, bold=True, font_size=9.5, bg_color=hdr_bg)

    # Row 2 headers
    sub_lbls = ["B", "H", "VD", "B", "H", "VD", "B", "H", "VD", "B", "H", "VD", "VDC"]
    for offset, lbl in enumerate(sub_lbls, start=3):
        _set_cell_style(t1.cell(2, offset), lbl, bold=True, font_size=9.5, bg_color=hdr_bg)

    # Merge header cells
    t1.cell(0, 0).merge(t1.cell(2, 0))
    t1.cell(0, 1).merge(t1.cell(2, 1))
    t1.cell(0, 2).merge(t1.cell(2, 2))
    t1.cell(0, 3).merge(t1.cell(0, 15))
    t1.cell(1, 3).merge(t1.cell(1, 5))
    t1.cell(1, 6).merge(t1.cell(1, 8))
    t1.cell(1, 9).merge(t1.cell(1, 11))
    t1.cell(1, 12).merge(t1.cell(1, 15))
    t1.cell(0, 16).merge(t1.cell(0, 19))
    for idx_c in range(16, 20):
        t1.cell(1, idx_c).merge(t1.cell(2, idx_c))
    t1.cell(0, 20).merge(t1.cell(2, 20))

    col_totals = [0] * 13  # cols 3..15
    tot_b = tot_h = tot_vd = tot_vdc = 0

    for idx, cell_data in enumerate(cells, 1):
        r = t1.add_row().cells
        part = cell_data.get("part", "part1_mc")
        nb = cell_data.get("nb", 0)
        th = cell_data.get("th", 0)
        vd = cell_data.get("vd", 0)
        vdc = cell_data.get("vdc", 0)

        _set_cell_style(r[0], str(idx), font_size=10)
        _set_cell_style(r[1], cell_data.get("topic_display", ""), align=WD_ALIGN_PARAGRAPH.LEFT, bold=True, font_size=10)
        _set_cell_style(r[2], cell_data.get("topic_display", ""), align=WD_ALIGN_PARAGRAPH.LEFT, font_size=10)

        if part == "part1_mc":
            b_i, h_i, vd_i = 3, 4, 5
            pts = (nb + th + vd + vdc) * 0.25
        elif part == "part2_tf":
            b_i, h_i, vd_i = 6, 7, 8
            pts = 1.0
        elif part == "part3_sa":
            b_i, h_i, vd_i = 9, 10, 11
            pts = (nb + th + vd + vdc) * 0.5
        else:
            b_i, h_i, vd_i = 12, 13, 14
            pts = (nb + th + vd + vdc) * 1.0

        if nb:
            _set_cell_style(r[b_i], str(nb), font_size=10)
            col_totals[b_i - 3] += nb
        if th:
            _set_cell_style(r[h_i], str(th), font_size=10)
            col_totals[h_i - 3] += th
        if vd + (vdc if part != "essay" else 0):
            v_val = vd + (vdc if part != "essay" else 0)
            _set_cell_style(r[vd_i], str(v_val), font_size=10)
            col_totals[vd_i - 3] += v_val
        if part == "essay" and vdc:
            _set_cell_style(r[15], str(vdc), font_size=10)
            col_totals[12] += vdc

        tot_b += nb
        tot_h += th
        tot_vd += vd
        tot_vdc += vdc

        if nb: _set_cell_style(r[16], str(nb), bold=True, font_size=10)
        if th: _set_cell_style(r[17], str(th), bold=True, font_size=10)
        if vd: _set_cell_style(r[18], str(vd), bold=True, font_size=10)
        if vdc: _set_cell_style(r[19], str(vdc), bold=True, font_size=10)
        _set_cell_style(r[20], f"{pts:.2f}".rstrip('0').rstrip('.') + f" đ\n({pts*10:.0f}%)", font_size=9.5)

    # 4 MANDATORY SUMMARY ROWS AT THE BOTTOM OF TABLE 1
    sum_bg = "F2F4F4"
    # Row Sum 1: TỔNG (Ý)
    r_s1 = t1.add_row().cells
    _set_cell_style(r_s1[0], "TỔNG (Ý)", bold=True, font_size=10, bg_color=sum_bg)
    r_s1[0].merge(r_s1[2])
    for i in range(13):
        _set_cell_style(r_s1[3 + i], str(col_totals[i]) if col_totals[i] else "0", bold=True, font_size=10, bg_color=sum_bg)
    _set_cell_style(r_s1[16], str(tot_b), bold=True, font_size=10, bg_color=sum_bg)
    _set_cell_style(r_s1[17], str(tot_h), bold=True, font_size=10, bg_color=sum_bg)
    _set_cell_style(r_s1[18], str(tot_vd), bold=True, font_size=10, bg_color=sum_bg)
    _set_cell_style(r_s1[19], str(tot_vdc), bold=True, font_size=10, bg_color=sum_bg)
    tot_all_items = tot_b + tot_h + tot_vd + tot_vdc
    _set_cell_style(r_s1[20], f"{tot_all_items} ý", bold=True, font_size=10, bg_color=sum_bg)

    # Row Sum 2: TỔNG SỐ CÂU
    r_s2 = t1.add_row().cells
    _set_cell_style(r_s2[0], "TỔNG SỐ CÂU", bold=True, font_size=10, bg_color=sum_bg)
    r_s2[0].merge(r_s2[2])
    p1_c = sum(col_totals[0:3])
    p2_y = sum(col_totals[3:6])
    p3_c = sum(col_totals[6:9])
    p4_c = sum(col_totals[9:13])
    _set_cell_style(r_s2[3], f"{p1_c} câu", bold=True, font_size=10, bg_color=sum_bg)
    r_s2[3].merge(r_s2[5])
    _set_cell_style(r_s2[6], f"{p2_y // 4} câu ({p2_y} ý)" if p2_y else "0 câu", bold=True, font_size=10, bg_color=sum_bg)
    r_s2[6].merge(r_s2[8])
    _set_cell_style(r_s2[9], f"{p3_c} câu", bold=True, font_size=10, bg_color=sum_bg)
    r_s2[9].merge(r_s2[11])
    _set_cell_style(r_s2[12], f"{p4_c} câu", bold=True, font_size=10, bg_color=sum_bg)
    r_s2[12].merge(r_s2[15])
    tot_q = p1_c + (p2_y // 4) + p3_c + p4_c
    _set_cell_style(r_s2[16], f"{tot_q} câu ({tot_all_items} ý)", bold=True, font_size=10, bg_color=sum_bg)
    r_s2[16].merge(r_s2[19])
    _set_cell_style(r_s2[20], f"{tot_q} câu", bold=True, font_size=10, bg_color=sum_bg)

    # Row Sum 3: TỔNG ĐIỂM
    r_s3 = t1.add_row().cells
    _set_cell_style(r_s3[0], "TỔNG ĐIỂM", bold=True, font_size=10, bg_color=sum_bg)
    r_s3[0].merge(r_s3[2])
    _set_cell_style(r_s3[3], "3,0 điểm", bold=True, font_size=10, bg_color=sum_bg)
    r_s3[3].merge(r_s3[5])
    _set_cell_style(r_s3[6], "4,0 điểm", bold=True, font_size=10, bg_color=sum_bg)
    r_s3[6].merge(r_s3[8])
    _set_cell_style(r_s3[9], "3,0 điểm" if p3_c else "0,0 điểm", bold=True, font_size=10, bg_color=sum_bg)
    r_s3[9].merge(r_s3[11])
    _set_cell_style(r_s3[12], "3,0 điểm" if p4_c else "0,0 điểm", bold=True, font_size=10, bg_color=sum_bg)
    r_s3[12].merge(r_s3[15])
    _set_cell_style(r_s3[16], "4,0 đ", bold=True, font_size=10, bg_color=sum_bg)
    _set_cell_style(r_s3[17], "3,0 đ", bold=True, font_size=10, bg_color=sum_bg)
    _set_cell_style(r_s3[18], "2,0 đ", bold=True, font_size=10, bg_color=sum_bg)
    _set_cell_style(r_s3[19], "1,0 đ", bold=True, font_size=10, bg_color=sum_bg)
    _set_cell_style(r_s3[20], "10,0 đ", bold=True, font_size=10, bg_color=sum_bg)

    # Row Sum 4: TỈ LỆ %
    r_s4 = t1.add_row().cells
    _set_cell_style(r_s4[0], "TỈ LỆ %", bold=True, font_size=10, bg_color=sum_bg)
    r_s4[0].merge(r_s4[2])
    _set_cell_style(r_s4[3], "30%", bold=True, font_size=10, bg_color=sum_bg)
    r_s4[3].merge(r_s4[5])
    _set_cell_style(r_s4[6], "40%", bold=True, font_size=10, bg_color=sum_bg)
    r_s4[6].merge(r_s4[8])
    _set_cell_style(r_s4[9], "30%" if p3_c else "0%", bold=True, font_size=10, bg_color=sum_bg)
    r_s4[9].merge(r_s4[11])
    _set_cell_style(r_s4[12], "30%" if p4_c else "0%", bold=True, font_size=10, bg_color=sum_bg)
    r_s4[12].merge(r_s4[15])
    _set_cell_style(r_s4[16], "40%", bold=True, font_size=10, bg_color=sum_bg)
    _set_cell_style(r_s4[17], "30%", bold=True, font_size=10, bg_color=sum_bg)
    _set_cell_style(r_s4[18], "20%", bold=True, font_size=10, bg_color=sum_bg)
    _set_cell_style(r_s4[19], "10%", bold=True, font_size=10, bg_color=sum_bg)
    _set_cell_style(r_s4[20], "100%", bold=True, font_size=10, bg_color=sum_bg)

    enforce_perfect_table_borders(t1, header_rows=3)

    # -------------------------------------------------------------
    # BẢNG 2: BẢN ĐẶC TẢ CHI TIẾT (MỖI MỨC ĐỘ NHẬN THỨC 1 DÒNG RIÊNG)
    # -------------------------------------------------------------
    p_sec2 = doc.add_paragraph()
    p_sec2.paragraph_format.space_before = Pt(12)
    p_sec2.paragraph_format.space_after = Pt(4)
    r_sec2 = p_sec2.add_run("2. BẢN ĐẶC TẢ ĐỀ KIỂM TRA ĐỊNH KÌ (CHI TIẾT THEO MỨC ĐỘ NHẬN THỨC)")
    r_sec2.font.name = 'Times New Roman'
    r_sec2.font.size = Pt(12)
    r_sec2.bold = True

    # 19 columns for Table 2:
    # 0: TT | 1: Chủ đề | 2: Nội dung/Đơn vị KT | 3: Mức độ đánh giá | 4: Yêu cầu cần đạt |
    # 5,6,7: Phần I (B, H, VD) | 8,9,10: Phần II (B, H, VD) | 11,12,13: Phần III (B, H, VD) | 14,15,16,17: Phần IV (B, H, VD, VDC) |
    # 18: Câu hỏi trong đề
    t2 = doc.add_table(rows=3, cols=19)
    t2.alignment = WD_TABLE_ALIGNMENT.CENTER

    _set_cell_style(t2.cell(0, 0), "TT", bold=True, font_size=10, bg_color=hdr_bg)
    _set_cell_style(t2.cell(0, 1), "Chủ đề / Mạch kiến thức", bold=True, font_size=10, bg_color=hdr_bg)
    _set_cell_style(t2.cell(0, 2), "Nội dung / Đơn vị kiến thức", bold=True, font_size=10, bg_color=hdr_bg)
    _set_cell_style(t2.cell(0, 3), "Mức độ\nđánh giá", bold=True, font_size=10, bg_color=hdr_bg)
    _set_cell_style(t2.cell(0, 4), "Yêu cầu cần đạt\n(Trích xuất chuẩn CT GDPT 2018)", bold=True, font_size=10, bg_color=hdr_bg)
    _set_cell_style(t2.cell(0, 5), "Số câu hỏi / lệnh hỏi theo mức độ đánh giá", bold=True, font_size=10, bg_color=hdr_bg)
    _set_cell_style(t2.cell(0, 18), "Câu hỏi\ntrong đề", bold=True, font_size=10, bg_color=hdr_bg)

    _set_cell_style(t2.cell(1, 5), "Phần I. TN Nhiều lựa chọn", bold=True, font_size=9.5, bg_color=hdr_bg)
    _set_cell_style(t2.cell(1, 8), "Phần II. TN Đúng/Sai", bold=True, font_size=9.5, bg_color=hdr_bg)
    _set_cell_style(t2.cell(1, 11), "Phần III. Trả lời ngắn", bold=True, font_size=9.5, bg_color=hdr_bg)
    _set_cell_style(t2.cell(1, 14), "Phần IV. Tự luận", bold=True, font_size=9.5, bg_color=hdr_bg)

    for offset, lbl in enumerate(sub_lbls, start=5):
        _set_cell_style(t2.cell(2, offset), lbl, bold=True, font_size=9.5, bg_color=hdr_bg)

    for c_i in range(5):
        t2.cell(0, c_i).merge(t2.cell(2, c_i))
    t2.cell(0, 5).merge(t2.cell(0, 17))
    t2.cell(1, 5).merge(t2.cell(1, 7))
    t2.cell(1, 8).merge(t2.cell(1, 10))
    t2.cell(1, 11).merge(t2.cell(1, 13))
    t2.cell(1, 14).merge(t2.cell(1, 17))
    t2.cell(0, 18).merge(t2.cell(2, 18))

    q_counter = 1
    for idx, cell_data in enumerate(cells, 1):
        part = cell_data.get("part", "part1_mc")
        topic_name = cell_data.get("topic_display", "")
        level_entries = []
        for lvl_key, lvl_label, lvl_color, verb_prefix in [
            ("nb", "Nhận biết", (0, 90, 158), "- Nhận biết, nêu và xác định được kiến thức cơ bản về"),
            ("th", "Thông hiểu", (0, 90, 158), "- Hiểu, giải thích và phân tích được các tính chất/quy luật của"),
            ("vd", "Vận dụng", (197, 90, 17), "- Vận dụng kiến thức để tính toán và xử lý bài toán về"),
            ("vdc", "Vận dụng cao", (158, 27, 27), "- Vận dụng tổng hợp kiến thức để giải quyết tình huống thực tiễn về"),
        ]:
            cnt = cell_data.get(lvl_key, 0)
            if cnt > 0:
                q_codes = [f"C{q_counter + k}" for k in range(cnt)]
                q_counter += cnt
                level_entries.append((lvl_key, lvl_label, lvl_color, f"{verb_prefix} {topic_name}.", cnt, ", ".join(q_codes)))

        start_r_idx = len(t2.rows)
        for lvl_key, lvl_label, lvl_color, yccd_txt, cnt, q_code_str in level_entries:
            r2 = t2.add_row().cells
            _set_cell_style(r2[0], str(idx), font_size=10)
            _set_cell_style(r2[1], topic_name, align=WD_ALIGN_PARAGRAPH.LEFT, bold=True, font_size=10)
            _set_cell_style(r2[2], topic_name, align=WD_ALIGN_PARAGRAPH.LEFT, font_size=10)
            _set_cell_style(r2[3], lvl_label, bold=True, font_size=9.5, text_color=lvl_color)
            _set_cell_style(r2[4], yccd_txt, align=WD_ALIGN_PARAGRAPH.LEFT, font_size=9.5)

            if part == "part1_mc":
                col_map = {"nb": 5, "th": 6, "vd": 7, "vdc": 7}
            elif part == "part2_tf":
                col_map = {"nb": 8, "th": 9, "vd": 10, "vdc": 10}
            elif part == "part3_sa":
                col_map = {"nb": 11, "th": 12, "vd": 13, "vdc": 13}
            else:
                col_map = {"nb": 14, "th": 15, "vd": 16, "vdc": 17}

            _set_cell_style(r2[col_map[lvl_key]], str(cnt), font_size=10)
            _set_cell_style(r2[18], q_code_str, bold=True, font_size=9.5)

        end_r_idx = len(t2.rows) - 1
        if end_r_idx > start_r_idx:
            t2.cell(start_r_idx, 0).merge(t2.cell(end_r_idx, 0))
            t2.cell(start_r_idx, 1).merge(t2.cell(end_r_idx, 1))
            t2.cell(start_r_idx, 2).merge(t2.cell(end_r_idx, 2))

    # 3 MANDATORY SUMMARY ROWS AT THE BOTTOM OF TABLE 2
    r2_s1 = t2.add_row().cells
    _set_cell_style(r2_s1[0], "TỔNG SỐ CÂU / LỆNH HỎI", bold=True, font_size=10, bg_color=sum_bg)
    r2_s1[0].merge(r2_s1[4])
    for i in range(13):
        _set_cell_style(r2_s1[5 + i], str(col_totals[i]) if col_totals[i] else "0", bold=True, font_size=10, bg_color=sum_bg)
    _set_cell_style(r2_s1[18], f"{tot_q} câu ({tot_all_items} ý)", bold=True, font_size=10, bg_color=sum_bg)

    r2_s2 = t2.add_row().cells
    _set_cell_style(r2_s2[0], "TỔNG ĐIỂM (10,0 ĐIỂM)", bold=True, font_size=10, bg_color=sum_bg)
    r2_s2[0].merge(r2_s2[4])
    _set_cell_style(r2_s2[5], "3,0 đ", bold=True, font_size=10, bg_color=sum_bg)
    r2_s2[5].merge(r2_s2[7])
    _set_cell_style(r2_s2[8], "4,0 đ", bold=True, font_size=10, bg_color=sum_bg)
    r2_s2[8].merge(r2_s2[10])
    _set_cell_style(r2_s2[11], "3,0 đ" if p3_c else "0,0 đ", bold=True, font_size=10, bg_color=sum_bg)
    r2_s2[11].merge(r2_s2[13])
    _set_cell_style(r2_s2[14], "3,0 đ" if p4_c else "0,0 đ", bold=True, font_size=10, bg_color=sum_bg)
    r2_s2[14].merge(r2_s2[17])
    _set_cell_style(r2_s2[18], "10,0 đ", bold=True, font_size=10, bg_color=sum_bg)

    r2_s3 = t2.add_row().cells
    _set_cell_style(r2_s3[0], "TỈ LỆ %", bold=True, font_size=10, bg_color=sum_bg)
    r2_s3[0].merge(r2_s3[4])
    _set_cell_style(r2_s3[5], "30%", bold=True, font_size=10, bg_color=sum_bg)
    r2_s3[5].merge(r2_s3[7])
    _set_cell_style(r2_s3[8], "40%", bold=True, font_size=10, bg_color=sum_bg)
    r2_s3[8].merge(r2_s3[10])
    _set_cell_style(r2_s3[11], "30%" if p3_c else "0%", bold=True, font_size=10, bg_color=sum_bg)
    r2_s3[11].merge(r2_s3[13])
    _set_cell_style(r2_s3[14], "30%" if p4_c else "0%", bold=True, font_size=10, bg_color=sum_bg)
    r2_s3[14].merge(r2_s3[17])
    _set_cell_style(r2_s3[18], "100%", bold=True, font_size=10, bg_color=sum_bg)

    enforce_perfect_table_borders(t2, header_rows=3)

    # Signature Table
    doc.add_paragraph()
    t_sig = doc.add_table(rows=1, cols=3)
    t_sig.alignment = WD_TABLE_ALIGNMENT.CENTER
    _set_cell_style(t_sig.cell(0, 0), "HIỆU TRƯỞNG / BGH DUYỆT\n(Ký, đóng dấu và phê duyệt)\n\n\n\n", bold=True, font_size=10.5)
    _set_cell_style(t_sig.cell(0, 1), "TỔ TRƯỞNG CHUYÊN MÔN\n(Ký và ghi rõ họ tên)\n\n\n\n", bold=True, font_size=10.5)
    _set_cell_style(t_sig.cell(0, 2), "..., ngày ..... tháng ..... năm 2026\nNGƯỜI LẬP MA TRẬN & ĐẶC TẢ\n(Ký và ghi rõ họ tên)\n\n\n", bold=True, font_size=10.5)

    if not output_path:
        output_path = BASE_DIR / f"{matrix_key.upper()}_MA_TRAN_DAC_TA_CHUAN_BGD.docx"
    else:
        output_path = Path(output_path)

    doc.save(str(output_path))
    print(f"[OK] Đã xuất file Word Ma trận & Bản đặc tả: {output_path}")
    return output_path


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Xuất Ma trận & Bản đặc tả ra Word (chuẩn: 1 mức độ/1 dòng, đủ dòng tổng, viền liền nét).")
    ap.add_argument("key", nargs="?", default="math_12_thpt_90min", help="Khóa trong references/default_matrices.json")
    ap.add_argument("--json", help="Đường dẫn file JSON ma trận (thay cho khóa có sẵn)")
    ap.add_argument("-o", "--output", help="Đường dẫn file .docx xuất ra")
    args = ap.parse_args()
    if args.json:
        _m = json.loads(Path(args.json).read_text(encoding="utf-8"))
        export_matrix_dict_to_docx(_m, args.output, matrix_key=Path(args.json).stem)
    else:
        export_matrix_to_docx(args.key, args.output)
