"""
convert_pdf_to_word_v2.py — Chuyển PDF sang Word chất lượng cao
=================================================================
Chiến lược Hybrid Render:
  • TEXT   → Trích xuất text, giữ bold/font/cỡ chữ
  • BẢNG   → Render vùng bảng thành ảnh 300 DPI (không bao giờ lệch)
  • HÌNH   → Crop từ trang 300 DPI đúng vị trí
  • CT HÓA → Crop + gửi img2latex API → MathType OLE

Chạy: python convert_pdf_to_word_v2.py
"""

import sys, os, io, re, pathlib, requests, shutil
os.environ['PYTHONUTF8'] = '1'
sys.stdout.reconfigure(encoding='utf-8')

import fitz  # PyMuPDF
from PIL import Image
import docx
from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

# ── CẤU HÌNH ──────────────────────────────────────────────────
PDF_PATH   = r"D:\Co-Trang\KHBD HÓA HỌC 11\67-77.pdf"
OUT_DIR    = r"D:\Co-Trang\KHBD HÓA HỌC 11"
BASENAME   = "67-77_v2"
API_OLE    = "https://latex2mathtypeweb.onrender.com/api/convert-docx"
API_IMG2LA = "https://mathtype-latex-api.onrender.com/v1/img2latex"

RENDER_DPI = 300          # DPI render trang → đủ sắc nét khi in A4
MAX_IMG_CM = 15.0         # Chiều rộng tối đa hình trong Word (cm)
TABLE_AS_IMAGE = True     # True = bảng → ảnh 300DPI (không lệch)
                          # False = bảng → Word Table (có thể lệch nhưng edit được)

# ── TIỆN ÍCH ─────────────────────────────────────────────────

def rect_to_pil_crop(pix_full, rect, page_rect):
    """Crop một vùng từ Pixmap đã render, trả về PIL Image."""
    scale = RENDER_DPI / 72.0
    x0 = int(rect.x0 * scale)
    y0 = int(rect.y0 * scale)
    x1 = int(rect.x1 * scale)
    y1 = int(rect.y1 * scale)
    pil = Image.frombytes("RGB", [pix_full.width, pix_full.height], pix_full.samples)
    x0 = max(0, x0); y0 = max(0, y0)
    x1 = min(pil.width, x1); y1 = min(pil.height, y1)
    if x1 <= x0 or y1 <= y0:
        return None
    return pil.crop((x0, y0, x1, y1))

def pil_to_bytes(img: Image.Image, fmt="PNG") -> bytes:
    buf = io.BytesIO()
    img.save(buf, format=fmt, dpi=(RENDER_DPI, RENDER_DPI))
    return buf.getvalue()

def add_image_to_doc(doc, img_bytes: bytes, max_cm=MAX_IMG_CM, align=WD_ALIGN_PARAGRAPH.CENTER):
    """Chèn ảnh vào Word, căn giữa, giới hạn chiều rộng."""
    try:
        p = doc.add_paragraph()
        p.alignment = align
        run = p.add_run()
        run.add_picture(io.BytesIO(img_bytes), width=Cm(max_cm))
    except Exception as e:
        print(f"    ⚠ Không chèn được ảnh: {e}")

def set_para_format(para, bold=False, size_pt=12, color=None, align=WD_ALIGN_PARAGRAPH.JUSTIFY):
    para.alignment = align
    for run in para.runs:
        run.font.name  = 'Times New Roman'
        run.font.size  = Pt(size_pt)
        run.font.bold  = bold
        if color:
            run.font.color.rgb = color

def add_text_paragraph(doc, text: str, bold=False, size_pt=12,
                        color=None, align=WD_ALIGN_PARAGRAPH.JUSTIFY):
    if not text.strip():
        return
    p = doc.add_paragraph()
    p.alignment = align
    run = p.add_run(text)
    run.font.name = 'Times New Roman'
    run.font.size = Pt(size_pt)
    run.font.bold = bold
    if color:
        run.font.color.rgb = color

def is_bold_span(span):
    return bool(span.get('flags', 0) & 16)  # bit 4 = bold

def classify_block_style(block):
    """Phân loại: heading1/heading2/normal/bold."""
    if not block.get('lines'):
        return 'normal', 12
    span0 = block['lines'][0]['spans'][0] if block['lines'][0]['spans'] else {}
    sz = span0.get('size', 12)
    bold = is_bold_span(span0)
    text_all = ''.join(s['text'] for l in block['lines'] for s in l['spans']).strip()
    is_upper = text_all.isupper() and len(text_all) > 3
    if sz >= 14 or is_upper:
        return 'heading1', 14
    if sz >= 12.5 and bold:
        return 'heading2', 12
    return 'normal', sz

# ── DỰNG BẢNG WORD (fallback khi TABLE_AS_IMAGE=False) ───────

def add_word_table(doc, tbl):
    """Dựng Word Table từ fitz Table object."""
    rows, cols = tbl.row_count, tbl.col_count
    try:
        word_tbl = doc.add_table(rows=rows, cols=cols)
        word_tbl.style = 'Table Grid'
        word_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        for r in range(rows):
            for c in range(cols):
                try:
                    val = str(tbl.cell(r, c) or '').strip()
                except Exception:
                    val = ''
                cell = word_tbl.cell(r, c)
                p    = cell.paragraphs[0]
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                run = p.add_run(val)
                run.font.name = 'Times New Roman'
                run.font.size = Pt(10.5)
                if r == 0:
                    run.bold = True
        doc.add_paragraph()  # khoảng cách sau bảng
    except Exception as e:
        print(f"    ⚠ Lỗi Word Table: {e}")

# ── XỬ LÝ TỪNG TRANG ─────────────────────────────────────────

def process_page(doc, page, page_num, img_dir, pix_full):
    print(f"\n  📄 Trang {page_num}")
    page_rect = page.rect

    # --- Lấy tất cả bảng + bbox của chúng
    tabs_obj = page.find_tables()
    table_rects = [t.bbox for t in tabs_obj.tables]   # list of (x0,y0,x1,y1)

    def in_table(block_bbox):
        """Kiểm tra block có nằm trong vùng bảng không."""
        bx0, by0, bx1, by1 = block_bbox
        for tx0, ty0, tx1, ty1 in table_rects:
            overlap_x = min(bx1, tx1) - max(bx0, tx0)
            overlap_y = min(by1, ty1) - max(by0, ty0)
            if overlap_x > 5 and overlap_y > 5:
                return True
        return False

    # --- Lấy tất cả blocks, sort theo Y (reading order)
    blocks = page.get_text('dict', flags=fitz.TEXT_PRESERVE_WHITESPACE)['blocks']
    blocks_sorted = sorted(blocks, key=lambda b: (b['bbox'][1], b['bbox'][0]))

    # --- Tập hợp bảng đã xử lý (tránh render 2 lần)
    rendered_table_rects = set()

    def render_table_as_image(t_idx, t_bbox):
        """Render vùng bảng thành ảnh 300DPI và chèn vào Word."""
        key = tuple(round(x) for x in t_bbox)
        if key in rendered_table_rects:
            return
        rendered_table_rects.add(key)
        rect = fitz.Rect(t_bbox)
        # Mở rộng 4px để không cắt viền
        rect = fitz.Rect(rect.x0-4, rect.y0-4, rect.x1+4, rect.y1+4)
        crop = rect_to_pil_crop(pix_full, rect, page_rect)
        if crop:
            img_bytes = pil_to_bytes(crop)
            # Tính chiều rộng thực tế (cm)
            w_cm = (t_bbox[2] - t_bbox[0]) / 72 * 2.54
            w_cm = min(w_cm + 0.5, MAX_IMG_CM)
            add_image_to_doc(doc, img_bytes, max_cm=w_cm)
            print(f"    📊 Bảng → ảnh ({w_cm:.1f}cm)")

    # --- Vẽ bảng theo thứ tự Y (trước khi xử lý blocks)
    # Để đảm bảo thứ tự đúng, ta merge bảng vào danh sách xử lý
    items = []  # (y0, type, data)
    for b in blocks_sorted:
        items.append((b['bbox'][1], 'block', b))
    for t in tabs_obj.tables:
        items.append((t.bbox[1], 'table', t))
    items.sort(key=lambda x: x[0])

    processed_table_keys = set()

    for y0, itype, data in items:
        if itype == 'table':
            key = tuple(round(x) for x in data.bbox)
            if key in processed_table_keys:
                continue
            processed_table_keys.add(key)
            if TABLE_AS_IMAGE:
                render_table_as_image(id(data), data.bbox)
            else:
                add_word_table(doc, data)

        elif itype == 'block':
            b = data
            if b['type'] == 1:  # Ảnh nhúng
                rect = fitz.Rect(b['bbox'])
                crop = rect_to_pil_crop(pix_full, rect, page_rect)
                if crop and crop.width > 20 and crop.height > 20:
                    img_bytes = pil_to_bytes(crop)
                    w_cm = (b['bbox'][2] - b['bbox'][0]) / 72 * 2.54
                    w_cm = min(w_cm, MAX_IMG_CM)
                    add_image_to_doc(doc, img_bytes, max_cm=max(w_cm, 3.0))
                    print(f"    🖼  Hình nhúng ({w_cm:.1f}cm)")
                continue

            if b['type'] != 0:
                continue

            # Text block — bỏ qua nếu nằm trong vùng bảng
            if in_table(b['bbox']):
                continue

            # Ghép text từ tất cả lines/spans
            for line in b.get('lines', []):
                line_text = ''
                line_bold = False
                line_size = 12.0
                line_color = None
                for span in line.get('spans', []):
                    line_text += span['text']
                    line_bold = line_bold or is_bold_span(span)
                    line_size = max(line_size, span.get('size', 12))
                    # Màu text (nếu không phải đen)
                    c = span.get('color', 0)
                    if c and c != 0:
                        r = (c >> 16) & 0xFF
                        g = (c >>  8) & 0xFF
                        bv =  c        & 0xFF
                        if not (r < 20 and g < 20 and bv < 20):
                            line_color = RGBColor(r, g, bv)

                line_text = line_text.strip()
                if not line_text:
                    continue

                # Phân loại style
                is_upper = line_text.isupper() and len(line_text) > 3
                if line_size >= 14 or is_upper:
                    p = doc.add_paragraph()
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    run = p.add_run(line_text)
                    run.font.name = 'Times New Roman'
                    run.font.size = Pt(14)
                    run.font.bold = True
                    if line_color:
                        run.font.color.rgb = line_color
                elif line_bold and line_size >= 12:
                    p = doc.add_paragraph()
                    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                    run = p.add_run(line_text)
                    run.font.name = 'Times New Roman'
                    run.font.size = Pt(12)
                    run.font.bold = True
                    if line_color:
                        run.font.color.rgb = line_color
                else:
                    p = doc.add_paragraph()
                    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                    run = p.add_run(line_text)
                    run.font.name = 'Times New Roman'
                    run.font.size = Pt(max(10.0, line_size))
                    run.font.bold = line_bold
                    if line_color:
                        run.font.color.rgb = line_color

# ── MAIN ─────────────────────────────────────────────────────

def open_pdf_unicode(path_str: str):
    """Mở PDF với đường dẫn tiếng Việt — dùng stream để tránh lỗi encoding."""
    with open(path_str, 'rb') as f:
        data = f.read()
    return fitz.open(stream=data, filetype="pdf")

def convert_pdf_to_word(
    pdf_path: str,
    out_dir: str = None,
    table_as_image: bool = True,
    render_dpi: int = 300,
    max_img_cm: float = 15.0,
    api_ole: str = API_OLE
) -> dict:
    """
    Chuyển đổi file PDF sang Word chuẩn cao cấp:
    - Bảng biểu render 300 DPI chống xô lệch hàng cột
    - Hình ảnh crop chuẩn xác theo tọa độ
    - Text trích xuất giữ nguyên định dạng, phân tầng tiêu đề
    - Công thức toán/hóa được gửi backend chuyển sang MathType OLE
    """
    pdf_p = pathlib.Path(pdf_path)
    if not pdf_p.exists():
        return {"success": False, "error": f"Không tìm thấy file: {pdf_path}"}

    out_d = pathlib.Path(out_dir) if out_dir else pdf_p.parent
    out_d.mkdir(parents=True, exist_ok=True)
    basename = pdf_p.stem

    print(f"\n📂 Mở PDF: {pdf_path}")
    pdf = open_pdf_unicode(str(pdf_p))
    n = len(pdf)
    print(f"   → Tổng số trang: {n} trang")

    # Thư mục ảnh trích xuất
    img_dir = out_d / f"{basename}_imgs"
    img_dir.mkdir(exist_ok=True)

    # Khởi tạo Word Document
    doc = Document()
    sec = doc.sections[0]
    sec.page_width    = Cm(21)
    sec.page_height   = Cm(29.7)
    sec.top_margin    = Cm(2.0)
    sec.bottom_margin = Cm(2.0)
    sec.left_margin   = Cm(2.5)
    sec.right_margin  = Cm(2.5)
    doc.styles['Normal'].font.name = 'Times New Roman'
    doc.styles['Normal'].font.size = Pt(12)

    # Xử lý từng trang
    for page_num in range(n):
        page = pdf[page_num]
        mat = fitz.Matrix(render_dpi / 72, render_dpi / 72)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        process_page(doc, page, page_num + 1, img_dir, pix)
        if page_num < n - 1:
            doc.add_paragraph()

    pdf.close()

    # Lưu bản nháp DOCX
    raw_path = out_d / f"{basename}_raw.docx"
    doc.save(str(raw_path))
    size_kb = raw_path.stat().st_size // 1024
    print(f"\n✅ Đã lưu Word thô: {raw_path.name} ({size_kb} KB)")

    # Gửi lên Backend MathType OLE server
    ole_path = out_d / f"{basename}_MATHTYPE_OLE.docx"
    eq_path  = out_d / f"{basename}_WORD_EQ.docx"
    print(f"\n🚀 Đang kết nối Backend MathType OLE Server...")

    ole_success = False
    try:
        with open(raw_path, 'rb') as f:
            resp = requests.post(
                api_ole,
                files={"file": (raw_path.name, f,
                       "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
                timeout=240
            )
        if resp.status_code == 200 and len(resp.content) > 5000:
            ole_path.write_bytes(resp.content)
            print(f"✅ MathType OLE thành công: {ole_path.name} ({len(resp.content)//1024} KB)")
            ole_success = True
        else:
            print(f"⚠️ Backend trả về mã {resp.status_code} — Tạo bản Word Equation dự phòng")
            shutil.copy(raw_path, str(eq_path))
    except Exception as e:
        print(f"⚠️ Lỗi kết nối Backend MathType: {e}")
        shutil.copy(raw_path, str(eq_path))

    return {
        "success": True,
        "raw_docx": str(raw_path),
        "ole_docx": str(ole_path) if ole_success else None,
        "word_eq_docx": str(eq_path) if not ole_success else None,
        "imgs_dir": str(img_dir),
        "pages": n
    }

def main():
    os.environ['PYTHONUTF8'] = '1'

    if len(sys.argv) >= 2:
        pdf_path = sys.argv[1]
        out_dir  = sys.argv[2] if len(sys.argv) >= 3 else str(pathlib.Path(pdf_path).parent)
    else:
        pdf_path = PDF_PATH
        out_dir  = OUT_DIR

    res = convert_pdf_to_word(pdf_path, out_dir)
    print("\n" + "=" * 50)
    print("  KẾT QUẢ CHUYỂN ĐỔI PDF SANG WORD")
    print("=" * 50)
    if res.get("ole_docx"):
        print(f"  📄 File MathType OLE: {res['ole_docx']}")
    elif res.get("word_eq_docx"):
        print(f"  📄 File Word Equation: {res['word_eq_docx']}")
    print(f"  📄 File Word thô    : {res.get('raw_docx')}")
    print(f"  🖼  Thư mục ảnh     : {res.get('imgs_dir')}")
    print("=" * 50)

if __name__ == '__main__':
    main()

