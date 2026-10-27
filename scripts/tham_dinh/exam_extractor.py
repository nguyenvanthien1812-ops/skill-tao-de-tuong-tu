# -*- coding: utf-8 -*-
"""
exam_extractor.py
─────────────────
Module trích xuất dữ liệu từ 3 file: Ma trận/Bản đặc tả, Đề thi, Hướng dẫn chấm.
Trả về ExamData chuẩn hoá để các validator dùng chung.

Lưu ý cấu trúc thực tế đề Toán THCS/THPT:
  - Phương án A/B/C/D thường nằm trong TABLE 1 hàng × 4 cột (hoặc 2×2)
    với OLE objects (công thức MathType) → python-docx không đọc được text
  - Bảng ma trận có merged cells → dùng XML để đọc đúng số ô thực
  - Ô TN trong ma trận có dạng "4(1đ)" → số câu = 4, điểm = 1đ
  - Dòng Tổng trong ma trận có dạng "29(10đ)" → số câu = 29, điểm thật = 10đ
"""
from __future__ import annotations
import re
import os
from dataclasses import dataclass, field
from typing import Optional

import docx
from docx import Document

# ──────────────────────────────────────────────────────────────────────────────
# DATA MODELS
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class MatrixEntry:
    """Một dòng trong Ma trận / Bản đặc tả."""
    tt: str = ""
    chu_de: str = ""
    noi_dung: str = ""
    muc_do: str = ""          # Nhận biết / Thông hiểu / Vận dụng / Vận dụng cao
    tn_nb: int = 0
    tl_nb: float = 0.0
    tn_th: int = 0
    tl_th: float = 0.0
    tn_vd: int = 0
    tl_vd: float = 0.0
    tn_vdc: int = 0
    tl_vdc: float = 0.0
    tong_cau: int = 0
    tong_diem: float = 0.0
    ma_cau: str = ""          # "C1, C2, C17a..."


@dataclass
class TNQuestion:
    """Một câu trắc nghiệm trong đề thi."""
    num: int = 0
    stem: str = ""
    choices: list = field(default_factory=list)   # [A, B, C, D]
    answer: str = ""          # Đáp án đúng (từ HDC)
    solution: str = ""
    topic: str = ""           # Chủ đề/bài học
    level: str = ""           # NB / TH / VD / VDC
    has_image: bool = False


@dataclass
class EssayQuestion:
    """Một bài tự luận."""
    num: int = 0
    title: str = ""
    points_total: float = 0.0
    intro: str = ""
    sub_items: list = field(default_factory=list)  # list of EssaySubItem
    has_image: bool = False


@dataclass
class EssaySubItem:
    label: str = ""           # "a)", "b)", ...
    stem: str = ""
    points: float = 0.0
    level: str = ""           # NB / TH / VD / VDC
    solution_steps: list = field(default_factory=list)  # [(step_text, points), ...]


@dataclass
class ExamData:
    """Container tất cả dữ liệu trích xuất từ 3 file."""
    # Ma trận
    matrix_entries: list = field(default_factory=list)   # [MatrixEntry]
    matrix_total_tn: int = 0
    matrix_total_tl_items: int = 0
    matrix_total_score: float = 0.0
    matrix_tn_score: float = 0.0
    matrix_tl_score: float = 0.0
    matrix_ratio: dict = field(default_factory=dict)     # {NB:%, TH:%, VD:%, VDC:%}
    matrix_has_summary_rows: bool = False
    matrix_table_count: int = 0

    # Đề thi
    exam_code: str = ""
    exam_title: str = ""
    exam_duration: str = ""
    tn_questions: list = field(default_factory=list)     # [TNQuestion]
    essay_questions: list = field(default_factory=list)  # [EssayQuestion]
    exam_tn_score: float = 0.0
    exam_tl_score: float = 0.0
    exam_has_end_marker: bool = False
    exam_image_refs: list = field(default_factory=list)

    # Hướng dẫn chấm
    rubric_code: str = ""
    rubric_answers: dict = field(default_factory=dict)   # {câu_num: "A"/"B"/"C"/"D"}
    rubric_solutions: list = field(default_factory=list)
    rubric_has_note: bool = False
    rubric_total_score: float = 0.0

    # OLE/Format
    exam_ole_count: int = 0
    exam_residual_dollar: int = 0
    rubric_ole_count: int = 0
    rubric_residual_dollar: int = 0

    # E03/E04 — Cỡ chữ & phân số OLE (danh sách chiều cao EMU của từng OLE object)
    exam_ole_heights: list = field(default_factory=list)   # [int, ...] chiều cao EMU mỗi OLE
    exam_small_fractions: int = 0    # Số OLE nghi là phân số bị co nhỏ
    rubric_ole_heights: list = field(default_factory=list)
    rubric_small_fractions: int = 0

    # Raw text (để fallback)
    matrix_raw: str = ""
    exam_raw: str = ""
    rubric_raw: str = ""


# ──────────────────────────────────────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────────────────────────────────────

def _safe_float(s: str) -> float:
    """Chuyển chuỗi số kiểu '2,25' hoặc '(1đ)' thành float."""
    if not s:
        return 0.0
    s = str(s).replace(',', '.').replace('đ', '').replace('(', '').replace(')', '').strip()
    m = re.search(r'[\d]+\.?[\d]*', s)
    return float(m.group()) if m else 0.0


def _safe_int(s: str) -> int:
    """Lấy số nguyên đầu tiên trong chuỗi."""
    m = re.search(r'\d+', str(s))
    return int(m.group()) if m else 0


def _extract_text(doc: Document) -> str:
    """Trích xuất toàn bộ text từ Document (kể cả bảng)."""
    parts = []
    for p in doc.paragraphs:
        parts.append(p.text)
    for tbl in doc.tables:
        for row in tbl.rows:
            for cell in row.cells:
                parts.append(cell.text)
    return "\n".join(parts)


def _tc_text(tc_elem) -> str:
    """Lấy text từ một <w:tc> element (tránh OLE làm mất text)."""
    ns = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
    texts = [t.text for t in tc_elem.iter(f'{ns}t') if t.text]
    return ''.join(texts).strip()


def _tc_has_ole(tc_elem) -> bool:
    """Kiểm tra cell có chứa OLE object không."""
    from lxml import etree
    xml_str = etree.tostring(tc_elem, encoding='unicode')
    return 'w:object' in xml_str or 'OLEObject' in xml_str


def _row_real_cells(row) -> list:
    """
    Đọc danh sách (text, has_ole) cho từng ô thực của row (bỏ merged duplicates).
    Word API row.cells() trả về ô bị lặp khi merge → phải dùng XML.
    """
    ns = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
    tc_list = row._tr.findall(f'.//{ns}tc')
    result = []
    for tc in tc_list:
        result.append((_tc_text(tc), _tc_has_ole(tc)))
    return result


def _count_ole_objects(docx_path: str) -> dict:
    """Đếm số OLE object và $ sót trong file DOCX."""
    try:
        import zipfile
        ole_count = 0
        residual = 0
        with zipfile.ZipFile(docx_path, 'r') as z:
            ole_count = sum(1 for n in z.namelist()
                            if 'oleObject' in n and n.endswith('.bin'))
            if 'word/document.xml' in z.namelist():
                xml = z.read('word/document.xml').decode('utf-8', errors='ignore')
                wt_texts = re.findall(r'<w:t[^>]*>(.*?)</w:t>', xml)
                for txt in wt_texts:
                    residual += txt.count('$')
        return {'ole_count': ole_count, 'residual_count': residual,
                'ok': ole_count > 0 and residual == 0}
    except Exception as e:
        return {'ole_count': 0, 'residual_count': -1, 'ok': False, 'error': str(e)}


def _analyze_ole_sizes(docx_path: str) -> dict:
    r"""
    Phân tích cỡ chữ và phân số co nhỏ trong các OLE MathType.

    Phương pháp:
    - Đọc kích thước của từng <w:object> trong document.xml:
      + Kiểu 1: <wp:extent cx="..." cy="..."/>
      + Kiểu 2: <v:shape ... style="...width:...;height:..."/> (Word MathType truyền thống)
      + Kiểu 3: <w:object w:dxaOrig="..." w:dyaOrig="...">
    - Đơn vị quy đổi: pt hoặc EMU (1 pt = 12700 EMU = 20 dxa).
    - Cỡ chữ chuẩn 13pt–14pt → chiều cao chữ ≈ 10–18 pt.
    - Phân số inline co nhỏ (E04): chiều cao 12–20 pt nhưng bề rộng >= 25 pt
      (công thức phân số dạng \frac bị ép dòng inline thay vì \dfrac display).
    - Cỡ chữ lệch chuẩn (E03): các công thức chữ thường lệch > 40% so với median.

    Trả về:
        {
            'heights': [int, ...],      # danh sách cy EMU của từng OLE
            'widths':  [int, ...],      # danh sách cx EMU
            'small_fractions': int,     # số OLE nghi phân số co nhỏ
            'outlier_count': int,       # số OLE cỡ chữ lệch chuẩn
            'ok': bool
        }
    """
    try:
        import zipfile
        import statistics

        heights = []
        widths  = []

        with zipfile.ZipFile(docx_path, 'r') as z:
            if 'word/document.xml' not in z.namelist():
                return {'heights': [], 'widths': [], 'small_fractions': 0,
                        'outlier_count': 0, 'ok': False}
            xml = z.read('word/document.xml').decode('utf-8', errors='ignore')

        # Tách từng khối <w:object ... </w:object>
        obj_blocks = re.findall(
            r'<w:object\b[^>]*>.*?</w:object>',
            xml, flags=re.DOTALL
        )

        for blk in obj_blocks:
            # 1. wp:extent (EMU trực tiếp)
            m_wp = re.search(r'<wp:extent\s+cx="(\d+)"\s+cy="(\d+)"', blk)
            if m_wp:
                cx, cy = int(m_wp.group(1)), int(m_wp.group(2))
                if cx > 50_000 and cy > 50_000:
                    heights.append(cy)
                    widths.append(cx)
                    continue

            # 2. v:shape style="width:Xpt;height:Ypt" (MathType OLE phổ biến)
            m_v = re.search(r'<v:shape[^>]+style=["\']([^"\']+)["\']', blk)
            if m_v:
                style = m_v.group(1)
                mw = re.search(r'width:([0-9.]+)pt', style)
                mh = re.search(r'height:([0-9.]+)pt', style)
                if mw and mh:
                    cx = int(float(mw.group(1)) * 12700)
                    cy = int(float(mh.group(1)) * 12700)
                    if cx > 50_000 and cy > 50_000:
                        heights.append(cy)
                        widths.append(cx)
                        continue

            # 3. w:dxaOrig / w:dyaOrig (1 dxa = 635 EMU)
            m_dxa = re.search(r'w:dxaOrig="(\d+)"\s+w:dyaOrig="(\d+)"', blk)
            if m_dxa:
                cx = int(m_dxa.group(1)) * 635
                cy = int(m_dxa.group(2)) * 635
                if cx > 50_000 and cy > 50_000:
                    heights.append(cy)
                    widths.append(cx)
                    continue

        # Fallback toàn văn nếu không match qua w:object
        if not heights:
            for s in re.findall(r'<v:shape[^>]+style=["\']([^"\']+)["\']', xml):
                mw = re.search(r'width:([0-9.]+)pt', s)
                mh = re.search(r'height:([0-9.]+)pt', s)
                if mw and mh:
                    cx = int(float(mw.group(1)) * 12700)
                    cy = int(float(mh.group(1)) * 12700)
                    if cx > 50_000 and cy > 50_000:
                        heights.append(cy)
                        widths.append(cx)

        if not heights:
            return {'heights': [], 'widths': [], 'small_fractions': 0,
                    'outlier_count': 0, 'ok': True}

        # Đổi ra đơn vị pt để tính toán trực quan
        heights_pt = [h / 12700 for h in heights]
        widths_pt  = [w / 12700 for w in widths]

        # ── Phát hiện phân số co nhỏ (E04) ──────────────────────────────────
        # Phân số inline: chiều cao nằm trong mức văn bản (12–20pt) nhưng chiều rộng lớn (>= 25pt)
        small_fractions = sum(
            1 for h, w in zip(heights_pt, widths_pt)
            if 12.0 <= h <= 20.0 and w >= 25.0
        )

        # ── Phát hiện cỡ chữ không đồng bộ (E03) ────────────────────────────
        # Lấy median của các công thức dòng thông thường (h < 22pt)
        regular = [h for h in heights_pt if h < 22.0]
        outlier_count = 0
        if len(regular) >= 5:
            med = statistics.median(regular)
            if med > 0:
                # Lệch > 40% so với median kích thước chuẩn
                outlier_count = sum(
                    1 for h in regular
                    if abs(h - med) / med > 0.40
                )

        return {
            'heights': heights,
            'widths':  widths,
            'small_fractions': small_fractions,
            'outlier_count': outlier_count,
            'ok': True
        }

    except Exception as e:
        return {'heights': [], 'widths': [], 'small_fractions': 0,
                'outlier_count': 0, 'ok': False, 'error': str(e)}


# ──────────────────────────────────────────────────────────────────────────────
# MATRIX EXTRACTOR
# ──────────────────────────────────────────────────────────────────────────────

def _parse_matrix_cell(val: str):
    """
    Parse ô ma trận dạng '4(1đ)' hoặc '4(1,0đ)' → (so_cau=4, diem=1.0).
    Nếu chỉ có số như '4' → (4, 0.0).
    Nếu rỗng → (0, 0.0).
    """
    if not val:
        return 0, 0.0
    # Dạng "N(Xđ)" hoặc "N(X,Yđ)"
    m = re.match(r'(\d+)\s*\(([^)]+)\)', val)
    if m:
        return int(m.group(1)), _safe_float(m.group(2))
    # Chỉ là số
    v = _safe_float(val)
    return _safe_int(val), v


def _extract_matrix(doc: Document, data: ExamData):
    """
    Trích xuất Ma trận & Bản đặc tả từ document.

    Cấu trúc bảng ma trận chuẩn GDPT 2018 (12 cột thực):
      Col 0: TT
      Col 1: Chương/Chủ đề
      Col 2: Nội dung/Đơn vị kiến thức
      Col 3: TN_NB  (dạng "4(1đ)")
      Col 4: TL_NB  (dạng "1(0,5đ)")
      Col 5: TN_TH
      Col 6: TL_TH
      Col 7: TN_VD
      Col 8: TL_VD
      Col 9: TN_VDC
      Col 10: TL_VDC
      Col 11: Tổng điểm (dạng "7(2,25đ)22,5%")
    """
    data.matrix_table_count = len(doc.tables)
    data.matrix_raw = _extract_text(doc)

    ns = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'

    # Từ khoá header — bỏ qua các dòng này
    HEADER_KW = [
        'mức độ đánh giá', 'tnkq', 'nhận biết', 'thông hiểu',
        'vận dụng', 'nội dung/đơn vị', 'chương/ chủ đề',
        'tt (1)', 'tt(1)', 'chương/chủ đề'
    ]

    total_score_found = 0.0
    has_tong_row = False
    has_ti_le_row = False

    for tbl in doc.tables:
        if len(tbl.rows) < 4:
            continue

        entries = []

        for r_idx, row in enumerate(tbl.rows):
            cells_raw = _row_real_cells(row)      # [(text, has_ole), ...]
            cells     = [c[0] for c in cells_raw] # chỉ text
            row_text  = ' '.join(cells).lower()

            # Bỏ qua dòng header (chỉ xét 3 hàng đầu của bảng)
            if r_idx < 3 and any(kw in row_text for kw in HEADER_KW):
                continue

            # Dòng Tổng: "Tổng" ở cột 0
            if cells and 'tổng' in cells[0].lower():
                has_tong_row = True
                # Ô cuối: "29(10đ)" → lấy số trong ngoặc = điểm thật
                last = cells[-1]
                m_br = re.search(r'\((\d+[\.,]?\d*)\s*đ?\)', last)
                if m_br:
                    total_score_found = _safe_float(m_br.group(1))
                else:
                    # Thử tìm số ≤ 15 ở cuối
                    nums = re.findall(r'\d+[\.,]?\d*', last)
                    for n in reversed(nums):
                        v = _safe_float(n)
                        if 0 < v <= 15:
                            total_score_found = v
                            break
                continue

            # Dòng Tỉ lệ
            if cells and ('tỉ lệ' in cells[0].lower() or 'tỉ lệ' in row_text[:20]):
                has_ti_le_row = True
                continue

            # Bỏ dòng quá ít ô hoặc rỗng
            non_empty = [c for c in cells if c.strip()]
            if len(non_empty) < 3 or len(cells) < 8:
                continue

            # Dòng dữ liệu
            entry = MatrixEntry()
            entry.tt       = cells[0]
            entry.chu_de   = cells[1] if len(cells) > 1 else ''
            entry.noi_dung = cells[2] if len(cells) > 2 else ''

            if len(cells) >= 12:
                entry.tn_nb,  entry.tl_nb  = _parse_matrix_cell(cells[3])
                _,            tl_nb_d       = _parse_matrix_cell(cells[4])
                if entry.tl_nb == 0:
                    entry.tl_nb = tl_nb_d
                entry.tn_th,  _             = _parse_matrix_cell(cells[5])
                _,            tl_th_d       = _parse_matrix_cell(cells[6])
                entry.tl_th                 = tl_th_d
                entry.tn_vd,  _             = _parse_matrix_cell(cells[7])
                _,            tl_vd_d       = _parse_matrix_cell(cells[8])
                entry.tl_vd                 = tl_vd_d
                entry.tn_vdc, _             = _parse_matrix_cell(cells[9])
                _,            tl_vdc_d      = _parse_matrix_cell(cells[10])
                entry.tl_vdc                = tl_vdc_d
                # Ô tổng điểm — ưu tiên số trong ngoặc
                cau_tong, diem_tong         = _parse_matrix_cell(cells[11])
                entry.tong_cau              = cau_tong
                entry.tong_diem             = diem_tong if diem_tong > 0 else _safe_float(cells[11])
            elif len(cells) >= 8:
                entry.tn_nb, _ = _parse_matrix_cell(cells[3])
                entry.tn_th, _ = _parse_matrix_cell(cells[5])
                _, diem_tong   = _parse_matrix_cell(cells[-1])
                entry.tong_diem = diem_tong if diem_tong > 0 else _safe_float(cells[-1])

            total_q = entry.tn_nb + entry.tn_th + entry.tn_vd + entry.tn_vdc
            if entry.noi_dung or entry.chu_de or total_q > 0:
                entries.append(entry)

        if entries:
            data.matrix_entries = entries
            data.matrix_total_tn = sum(
                e.tn_nb + e.tn_th + e.tn_vd + e.tn_vdc for e in entries
            )
            # Ưu tiên dòng Tổng (đáng tin nhất)
            if total_score_found > 0:
                data.matrix_total_score = total_score_found
            else:
                data.matrix_total_score = round(
                    sum(e.tong_diem for e in entries if 0 < e.tong_diem <= 15), 2
                )
            data.matrix_has_summary_rows = has_tong_row and has_ti_le_row
            break


# ──────────────────────────────────────────────────────────────────────────────
# EXAM EXTRACTOR (Đề thi học sinh)
# ──────────────────────────────────────────────────────────────────────────────

def _elem_text(elem) -> str:
    """Lấy text từ XML element (paragraph hoặc table cell)."""
    ns = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
    texts = [t.text for t in elem.iter(f'{ns}t') if t.text]
    return ''.join(texts).strip()


def _elem_has_ole(elem) -> bool:
    """Kiểm tra element có chứa OLE object."""
    from lxml import etree
    xml_str = etree.tostring(elem, encoding='unicode')
    return 'w:object' in xml_str or 'OLEObject' in xml_str


def _extract_exam(doc: Document, data: ExamData):
    """
    Trích xuất đề thi: mã đề, câu TN, bài TL.

    Lưu ý: phương án A/B/C/D trong đề Toán MathType nằm trong TABLE
    (1 hàng × 4 cột, hoặc 2 hàng × 2 cột). Mỗi ô có OLE object (công thức).
    Cần duyệt body XML để xử lý đúng thứ tự paragraph & table.
    """
    raw = _extract_text(doc)
    data.exam_raw = raw

    # Mã đề
    m_code = re.search(r'[Mm]ã\s*đề[:\s]*(\d+)', raw)
    if m_code:
        data.exam_code = m_code.group(1)

    # Thời gian
    m_time = re.search(r'(\d+)\s*phút', raw)
    if m_time:
        data.exam_duration = m_time.group(1) + ' phút'

    # Đánh dấu HẾT
    data.exam_has_end_marker = bool(
        re.search(r'[-─]+\s*hết\s*[-─]+', raw, re.IGNORECASE)
        or 'hết' in raw.lower()
    )

    ns   = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
    body = doc.element.body

    tn_pattern    = re.compile(r'^Câu\s+(\d+)[.\s]', re.IGNORECASE)
    essay_pattern = re.compile(r'^Bài\s+(\d+)[.\s(]', re.IGNORECASE)

    tn_questions    = []
    essay_questions = []
    current_tn      = None
    current_essay   = None

    def flush_tn():
        if current_tn:
            tn_questions.append(current_tn)

    def flush_essay():
        if current_essay:
            essay_questions.append(current_essay)

    for elem in body:
        tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag

        # ── PARAGRAPH ──
        if tag == 'p':
            p_text   = _elem_text(elem)
            has_ole  = _elem_has_ole(elem)

            if not p_text and not has_ole:
                continue

            # Bỏ heading Phần I / Phần II
            if re.search(r'PHẦN\s+I{1,2}\b', p_text, re.IGNORECASE):
                continue

            # Câu trắc nghiệm
            m_tn = tn_pattern.match(p_text)
            if m_tn:
                flush_tn()
                flush_essay()
                current_tn    = TNQuestion(num=int(m_tn.group(1)), stem=p_text)
                current_essay = None
                continue

            # Bài tự luận
            m_es = essay_pattern.match(p_text)
            if m_es:
                flush_tn()
                flush_essay()
                current_tn    = None
                current_essay = None
                pts_m = re.search(r'\([\s]*([\d,\.]+)\s*điểm\)', p_text)
                pts   = _safe_float(pts_m.group(1)) if pts_m else 0.0
                current_essay = EssayQuestion(
                    num=int(m_es.group(1)), title=p_text, points_total=pts
                )
                continue

            # Phương án A/B/C/D trong paragraph thường (không OLE)
            if current_tn and re.match(r'^[A-D][.\s]', p_text):
                current_tn.choices.append(p_text)
                continue

            # Phương án A/B/C/D trong paragraph chỉ có "A." + OLE
            if current_tn and has_ole and re.match(r'^[A-D]\.?\s*$', p_text):
                label = p_text.rstrip('. ') or chr(65 + len(current_tn.choices))
                current_tn.choices.append(f"{label}.[OLE]")
                continue

            # Sub-item tự luận: a), b), ...
            if current_essay and re.match(r'^[a-e]\)', p_text):
                pts_m = re.search(r'\([\s]*([\d,\.]+)\s*điểm\)', p_text)
                pts   = _safe_float(pts_m.group(1)) if pts_m else 0.0
                sub   = EssaySubItem(label=p_text[:2], stem=p_text, points=pts)
                current_essay.sub_items.append(sub)
                continue

        # ── TABLE (phương án A/B/C/D nằm trong table) ──
        elif tag == 'tbl':
            tr_list = elem.findall(f'.//{ns}tr')

            # TABLE phương án: nhỏ (1–2 hàng, 2–4 cột), chứa A/B/C/D
            if current_tn and len(tr_list) <= 2:
                choices_found = []
                for tr in tr_list:
                    tc_list = tr.findall(f'.//{ns}tc')
                    for tc in tc_list:
                        cell_text = _tc_text(tc)
                        cell_ole  = _tc_has_ole(tc)
                        if re.match(r'^[A-D][.\s]?', cell_text) or cell_ole:
                            if cell_ole and not re.match(r'^[A-D]', cell_text):
                                # Ô chỉ có OLE — gán nhãn tự động
                                label = chr(65 + len(choices_found))
                                choices_found.append(f"{label}.[OLE]")
                            else:
                                choices_found.append(cell_text if cell_text else f"{chr(65+len(choices_found))}.[OLE]")
                if choices_found:
                    current_tn.choices.extend(choices_found)
            # TABLE tự luận (hình vẽ…) — bỏ qua, không cần parse

    flush_tn()
    flush_essay()

    data.tn_questions    = tn_questions
    data.essay_questions = essay_questions
    data.exam_tn_score   = round(len(tn_questions) * 0.25, 2)
    data.exam_tl_score   = round(sum(e.points_total for e in essay_questions), 2)


# ──────────────────────────────────────────────────────────────────────────────
# RUBRIC EXTRACTOR (Hướng dẫn chấm)
# ──────────────────────────────────────────────────────────────────────────────

def _extract_rubric(doc: Document, data: ExamData):
    """Trích xuất Hướng dẫn chấm: đáp án TN + barem TL."""
    raw = _extract_text(doc)
    data.rubric_raw = raw

    # Mã đề trong HDC
    m_code = re.search(r'[Mm]ã\s*đề[:\s]*(\d+)', raw)
    if m_code:
        data.rubric_code = m_code.group(1)

    data.rubric_has_note = any(kw in raw.lower() for kw in [
        'lưu ý khi chấm', 'lưu ý:', 'lưu ý chung', 'học sinh làm cách khác', 'thí sinh làm theo cách giải khác'
    ])

    # Trích đáp án từ bảng — bảng đáp án có header dạng "Câu 1", "Câu 2", ...
    answers = {}
    for tbl in doc.tables:
        if len(tbl.rows) < 2:
            continue
        # Dùng XML để đọc header đúng
        header_cells = _row_real_cells(tbl.rows[0])
        header_texts = [c[0] for c in header_cells]
        if any('câu' in h.lower() for h in header_texts):
            # Dòng thứ 2 là đáp án
            ans_cells = _row_real_cells(tbl.rows[1])
            ans_texts  = [c[0] for c in ans_cells]
            for h, a in zip(header_texts, ans_texts):
                m = re.search(r'\d+', h)
                if m and a.strip() in ('A', 'B', 'C', 'D'):
                    answers[int(m.group())] = a.strip()

    data.rubric_answers = answers

    # Tổng điểm barem TL
    tl_score = 0.0
    for tbl in doc.tables:
        if len(tbl.rows) < 2 or len(tbl.columns) < 2:
            continue
        last_header = tbl.rows[0].cells[-1].text.strip().lower()
        if 'điểm' in last_header:
            for row in tbl.rows[1:]:
                tl_score += _safe_float(row.cells[-1].text)
    data.rubric_total_score = round(tl_score, 2)


# ──────────────────────────────────────────────────────────────────────────────
# MAIN ENTRY POINT
# ──────────────────────────────────────────────────────────────────────────────

def extract_exam_data(
    matrix_path: str,
    exam_path: str,
    rubric_path: str
) -> ExamData:
    """
    Trích xuất toàn bộ dữ liệu từ 3 file.
    Trả về ExamData chuẩn hoá để các validator sử dụng.
    """
    data = ExamData()

    print(f"[Extractor] Đọc Ma trận: {os.path.basename(matrix_path)}")
    doc_matrix = Document(matrix_path)
    _extract_matrix(doc_matrix, data)

    print(f"[Extractor] Đọc Đề thi: {os.path.basename(exam_path)}")
    doc_exam = Document(exam_path)
    _extract_exam(doc_exam, data)

    print(f"[Extractor] Đọc Hướng dẫn chấm: {os.path.basename(rubric_path)}")
    doc_rubric = Document(rubric_path)
    _extract_rubric(doc_rubric, data)

    print(f"[Extractor] Kiểm định OLE: {os.path.basename(exam_path)}")
    ole_exam   = _count_ole_objects(exam_path)
    ole_rubric = _count_ole_objects(rubric_path)
    data.exam_ole_count         = ole_exam['ole_count']
    data.exam_residual_dollar   = ole_exam['residual_count']
    data.rubric_ole_count       = ole_rubric['ole_count']
    data.rubric_residual_dollar = ole_rubric['residual_count']

    print(f"[Extractor] Phân tích cỡ chữ & phân số OLE: {os.path.basename(exam_path)}")
    size_exam   = _analyze_ole_sizes(exam_path)
    size_rubric = _analyze_ole_sizes(rubric_path)
    data.exam_ole_heights       = size_exam.get('heights', [])
    data.exam_small_fractions   = size_exam.get('small_fractions', 0)
    data.rubric_ole_heights     = size_rubric.get('heights', [])
    data.rubric_small_fractions = size_rubric.get('small_fractions', 0)
    # outlier_count lưu tạm để validator dùng (không cần đưa vào dataclass)
    data.__dict__['_exam_ole_outliers']   = size_exam.get('outlier_count', 0)
    data.__dict__['_rubric_ole_outliers'] = size_rubric.get('outlier_count', 0)

    print(f"[Extractor] ✓ Hoàn tất. TN={len(data.tn_questions)} câu, "
          f"TL={len(data.essay_questions)} bài, "
          f"Ma trận={len(data.matrix_entries)} dòng.")
    return data


if __name__ == '__main__':
    import sys
    if len(sys.argv) == 4:
        d = extract_exam_data(sys.argv[1], sys.argv[2], sys.argv[3])
        print(f"Matrix score: {d.matrix_total_score}")
        print(f"Matrix TN: {d.matrix_total_tn}")
        print(f"Exam TN: {len(d.tn_questions)} câu / {d.exam_tn_score}đ")
        print(f"Rubric answers: {d.rubric_answers}")
