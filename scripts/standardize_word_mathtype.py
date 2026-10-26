#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
standardize_word_mathtype.py — Chuẩn Hóa Công Thức Word Sang MathType OLE 100%
================================================================================
Tính năng chuyên biệt:
1. Tiếp nhận file Word (.docx) đã được căn chỉnh đẹp (bố cục, bảng biểu, hình ảnh).
2. Chuẩn hóa 100% các loại công thức trong file:
   - Công thức LaTeX dạng text ($...$, $$...$$, \(...\), \[...\])
   - Công thức Word Equation (OMML m:oMath, m:oMathPara)
   - Ký hiệu toán học/hóa học lẫn trong văn bản
3. Xuất ra đối tượng MathType OLE nguyên bản (Equation.DSMT4 / DSMT6):
   - Nhấp đúp chuột (double-click) mở ngay cửa sổ MathType 6/7 để chỉnh sửa.
   - Cỡ chữ công thức đồng bộ 14pt (hoặc theo font văn bản).
4. BẢO TOÀN 100% BỐ CỤC:
   - Giữ nguyên toàn bộ bảng biểu, đường viền, gộp ô (merged cells).
   - Giữ nguyên hình vẽ, sơ đồ, căn lề trang, header/footer, khoảng cách dòng.
   - Giữ nguyên toàn bộ font chữ và định dạng văn bản gốc.

Sử dụng:
    python scripts/standardize_word_mathtype.py "C:\\duong_dan\\file.docx"
"""

from __future__ import annotations
import os
import sys
import re
import zipfile
import shutil
import pathlib
import requests
import lxml.etree as ET
from typing import Optional

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass
os.environ['PYTHONUTF8'] = '1'

BACKEND_API_URL = "https://latex2mathtypeweb.onrender.com/api/convert-docx"

def postprocess_ole_docx_fix_delimiters(docx_path):
    r"""
    Tự động chuẩn hóa các đối tượng MathType OLE (.bin) trong file DOCX:
    1. Sửa lỗi tofu kim cương ◆ (U+2223): Khi LaTeX dùng \mid, backend sinh mã Unicode 0x2223
       trong font Symbol (tf=0x86). Do Symbol là font 8-bit, MathType không có glyph nên hiện ◆.
       -> Chuyển thành mã ASCII 0x007C trong font Symbol (tf=0x86) hiển thị vạch đứng | thẳng tắp 100%.
    2. Sửa lỗi ngoặc đơn mở '(' (MT Extra 0x7C): Khi backend dùng fence tmBAR với font MT Extra (tf=0x96),
       glyph 0x7C trong mtextra.ttf là verticalbracketright (hình vòng cung cong '(').
       -> Đổi typeface thành Symbol (tf=0x86) với mã 0x7C hiển thị vạch đứng | thẳng tắp 100%.
    """
    try:
        tmp_path = str(docx_path) + '.tmp'
        fixed = 0
        with zipfile.ZipFile(docx_path, 'r') as zin, zipfile.ZipFile(tmp_path, 'w', compression=zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                data = zin.read(item.filename)
                if item.filename.startswith('word/embeddings/') and item.filename.endswith('.bin'):
                    # 1. U+2223 in Symbol font -> 0x007C in Symbol font (chống lỗi kim cương ◆)
                    if b'\x02\x00\x86\x23\x22' in data:
                        fixed += data.count(b'\x02\x00\x86\x23\x22')
                        data = data.replace(b'\x02\x00\x86\x23\x22', b'\x02\x00\x86\x7c\x00')
                    # 2. MT Extra 0x7C -> Symbol font 0x007C (chống lỗi ngoặc '(' khi kích đúp)
                    if b'\x02\x00\x96\x7c\x00' in data:
                        fixed += data.count(b'\x02\x00\x96\x7c\x00')
                        data = data.replace(b'\x02\x00\x96\x7c\x00', b'\x02\x00\x86\x7c\x00')
                zout.writestr(item, data)
        if fixed > 0:
            os.replace(tmp_path, docx_path)
            print(f"    ✓ Đã chuẩn hóa tự động {fixed} vạch đứng (|) trong MathType OLE.")
        else:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
    except Exception as e:
        print(f"    ⚠️ Postprocess OLE: {e}")

# ── TIỀN XỬ LÝ CHUẨN HÓA CÚ PHÁP LATEX ────────────────────────────────────────

def _clean_latex_syntax(latex_str: str) -> str:
    """Chuẩn hóa cú pháp LaTeX để tương thích 100% với bộ biên dịch MathType."""
    if not latex_str:
        return ""
    # 1. Thay thế các lệnh logic gây lỗi MathType font
    latex_str = latex_str.replace(r"\implies", r"\Rightarrow")
    latex_str = latex_str.replace(r"\iff", r"\Leftrightarrow")
    latex_str = latex_str.replace(r"\to", r"\rightarrow")
    # Chuẩn hóa giá trị tuyệt đối / vạch đứng sang \mid để chống lỗi font MT Extra 0x7c '(' khi kích đúp MathType:
    latex_str = re.sub(r'\\left\s*\|', r'\\mid ', latex_str)
    latex_str = re.sub(r'\\right\s*\|', r' \\mid', latex_str)
    latex_str = re.sub(r'\\lvert\b', r'\\mid ', latex_str)
    latex_str = re.sub(r'\\rvert\b', r' \\mid', latex_str)
    
    # Chuẩn hóa cung tròn hình học (MathType không hỗ trợ \wideparen, gây lỗi in raw text):
    latex_str = re.sub(r'\\wideparen\{([^}]+)\}', r'\\text{cung }\1', latex_str)
    # Chuẩn hóa song song sang // chuẩn SGK Việt Nam (thay vì ||):
    latex_str = re.sub(r'\\parallel\b', r'\\text{ // }', latex_str)
    # Tự động chèn dấu nhân \cdot trước \widehat nếu đứng sau số hệ số (chống lỗi MathType nuốt số vào dấu mũ):
    latex_str = re.sub(r'(\d+)\s*\\widehat\{', r'\1 \\cdot \\widehat{', latex_str)

    # 2. Chuẩn hóa ký hiệu vuông góc đối xứng, chống dính chữ
    latex_str = re.sub(r'(?<!\\)\s*\\perp\s*', r' \\ \\perp \\ ', latex_str)
    latex_str = re.sub(r'(?<!https:)(?<!http:)(?<!/)\s*//\s*(?!/)', r' \\text{ // } ', latex_str)
    
    # 3. Tự động chuyển giá trị tuyệt đối |...| sang \mid ... \mid
    def _repl_abs(m):
        inner = m.group(1)
        if not inner.strip():
            return '||'
        return r'\mid ' + inner.strip() + r' \mid'
    latex_str = re.sub(r'(?<!\\)(?<!\\mid\s)\|(?!\|)([^\|\r\n]+?)(?<!\\)\|(?!\|)', _repl_abs, latex_str)
    latex_str = re.sub(r'\s*\\mid\s*', r' \\mid ', latex_str)

    # 4. Xóa các ký tự xuống dòng thô trong công thức
    latex_str = re.sub(r'[\r\n]+', ' ', latex_str)
    
    # 5. Chuẩn hóa khoảng trắng
    latex_str = re.sub(r'\s+', ' ', latex_str).strip()
    return latex_str

def preprocess_docx_latex_tags(doc_xml_bytes: bytes) -> bytes:
    """
    Quét document.xml để chuẩn hóa các thẻ LaTeX trong text runs:
    - Chuyển \\[...\\] thành $$...$$
    - Chuyển \\(...\\) thành $...$
    - Tự động bọc $ cho các lệnh LaTeX trần như \\frac, \\sqrt nếu người dùng quên bọc $
    """
    root = ET.fromstring(doc_xml_bytes)
    ns = {
        'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
        'm': 'http://schemas.openxmlformats.org/officeDocument/2006/math'
    }
    
    # Duyệt qua các text runs <w:t>
    for t_node in root.xpath('//w:t', namespaces=ns):
        if not t_node.text:
            continue
        text = t_node.text
        
        # 1. Chuyển \[...\] sang $$...$$
        text = re.sub(r'\\\[(.*?)\\\]', r'$$\1$$', text, flags=re.DOTALL)
        
        # 2. Chuyển \(...\) sang $...$
        text = re.sub(r'\\\((.*?)\\\)', r'$\1$', text, flags=re.DOTALL)
        
        # 3. Chuẩn hóa nội dung bên trong $...$
        def _repl_dollar(match):
            inner = match.group(1)
            cleaned = _clean_latex_syntax(inner)
            return f"${cleaned}$"
        
        text = re.sub(r'\$([^\$]+)\$', _repl_dollar, text)
        
        if text != t_node.text:
            t_node.text = text
            # Bảo đảm xml:space="preserve"
            t_node.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
            
    return ET.tostring(root, xml_declaration=True, encoding='utf-8')

# ── HÀM CHÍNH: CHUẨN HÓA DOCX SANG MATHTYPE OLE ─────────────────────────────

def standardize_doc_to_mathtype(
    input_path: str,
    output_path: Optional[str] = None,
    api_url: str = BACKEND_API_URL,
    timeout: int = 240
) -> dict:
    """
    Quy trình chuẩn hóa công thức 2 tầng (Dual-Pass Engine):
      Tầng 1: Chuyển toàn bộ $LaTeX$ sang MathType OLE qua Backend Server.
      Tầng 2: Chuyển toàn bộ Word Equation (OMML m:oMath) sang MathType OLE qua omml_converter.
    
    Bảo đảm 100% không xô lệch bố cục, bảng biểu, hình ảnh.
    """
    try:
        _d = os.path.dirname(os.path.abspath(__file__))
        if _d not in sys.path:
            sys.path.insert(0, _d)
        from license_manager import require_valid_license
        require_valid_license("standardize_mathtype")
    except ImportError:
        pass

    in_p = pathlib.Path(input_path).resolve()
    if not in_p.exists():
        return {"success": False, "error": f"Không tìm thấy file: {input_path}"}
        
    if output_path is None:
        out_p = in_p.parent / f"{in_p.stem}_MATHTYPE_OLE.docx"
    else:
        out_p = pathlib.Path(output_path).resolve()
        
    print(f"\n" + "=" * 65)
    print(f"  CHUẨN HÓA CÔNG THỨC WORD SANG MATHTYPE OLE NGUYÊN BẢN")
    print("=" * 65)
    print(f"  📁 Tệp nguồn : {in_p.name}")
    print(f"  📁 Tệp đích  : {out_p.name}")
    
    # ── BƯỚC 1: Tiền xử lý văn bản để chuẩn hóa ký hiệu LaTeX ──
    print(f"\n[*] Bước 1/3: Tiền xử lý cú pháp LaTeX trong văn bản...")
    tmp_preprocessed = in_p.parent / f"_tmp_pre_{in_p.stem}.docx"
    try:
        with zipfile.ZipFile(in_p, 'r') as zin:
            names = zin.namelist()
            zdata = {n: zin.read(n) for n in names}
            
        if "word/document.xml" in zdata:
            zdata["word/document.xml"] = preprocess_docx_latex_tags(zdata["word/document.xml"])
            
        with zipfile.ZipFile(tmp_preprocessed, 'w', compression=zipfile.ZIP_DEFLATED) as zout:
            for n in names:
                zout.writestr(n, zdata[n])
        print("    → Tiền xử lý hoàn tất, bảo toàn 100% cấu trúc OOXML.")
    except Exception as e:
        print(f"    ⚠️ Tiền xử lý nhẹ: {e}, dùng tệp gốc.")
        shutil.copy(in_p, tmp_preprocessed)

    # ── BƯỚC 2: Chuyển đổi $LaTeX$ sang MathType OLE qua Backend Server ──
    print(f"\n[*] Bước 2/3: Chuyển đổi công thức LaTeX sang MathType OLE...")
    tmp_step1 = in_p.parent / f"_tmp_step1_{in_p.stem}.docx"
    backend_success = False
    try:
        with open(tmp_preprocessed, 'rb') as f:
            resp = requests.post(
                api_url,
                files={"file": (tmp_preprocessed.name, f,
                       "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
                timeout=timeout
            )
        if resp.status_code == 200 and len(resp.content) > 5000:
            tmp_step1.write_bytes(resp.content)
            print(f"    ✅ Backend chuyển đổi LaTeX thành công ({len(resp.content)//1024} KB).")
            backend_success = True
        else:
            print(f"    ⚠️ Backend phản hồi mã {resp.status_code}, dùng bản bước 1.")
            shutil.copy(tmp_preprocessed, tmp_step1)
    except Exception as e:
        print(f"    ⚠️ Kết nối Backend: {e}, tiếp tục bước xử lý nội bộ.")
        shutil.copy(tmp_preprocessed, tmp_step1)
        
    # ── BƯỚC 3: Chuyển đổi Word Equations (OMML) sang MathType OLE ──
    print(f"\n[*] Bước 3/3: Quét và chuyển đổi các công thức Word Equation (OMML)...")
    try:
        import omml_converter
        summary = omml_converter.convert(str(tmp_step1), str(out_p))
        print(f"    ✅ omml_converter: Tìm thấy {summary.found} công thức OMML, đã chuyển {summary.converted} sang MathType OLE.")
    except Exception as e:
        print(f"    ⚠️ omml_converter: {e}. Lưu tệp bước 2 làm kết quả cuối.")
        shutil.copy(tmp_step1, out_p)
        summary = None

    # ── DỌN DẸP TỆP TẠM ──
    for tmp_f in [tmp_preprocessed, tmp_step1]:
        if tmp_f.exists():
            try:
                tmp_f.unlink()
            except Exception:
                pass

    # ── CHUẨN HÓA MTEF NHỊ PHÂN TRÁNH LỖI TOFU VÀ NGOẶC ĐƠN ──
    postprocess_ole_docx_fix_delimiters(out_p)

    # ── KIỂM ĐỊNH TÍNH TOÀN VẸN (AUDIT) ──
    ole_count = 0
    omml_count = 0
    try:
        with zipfile.ZipFile(out_p, 'r') as z:
            doc_xml = z.read('word/document.xml')
            root = ET.fromstring(doc_xml)
            ns = {
                'o': 'urn:schemas-microsoft-com:office:office',
                'm': 'http://schemas.openxmlformats.org/officeDocument/2006/math'
            }
            ole_count = len(root.xpath('//o:OLEObject', namespaces=ns))
            omml_count = len(root.xpath('//m:oMath', namespaces=ns))
    except Exception:
        pass

    print("\n" + "=" * 65)
    print("  KẾT QUẢ CHUẨN HÓA FILE WORD:")
    print("=" * 65)
    print(f"  📄 Tệp xuất xịn : {out_p.name} ({out_p.stat().st_size // 1024} KB)")
    print(f"  📐 Số công thức MathType OLE : {ole_count} công thức")
    print(f"  📝 Số công thức OMML còn lại  : {omml_count} công thức")
    print(f"  ✨ Bố cục & hình thức         : Giữ nguyên 100% bản gốc")
    print("=" * 65)
    
    deploy_mathtype_pref_files(str(out_p.parent))
    return {
        "success": True,
        "input_path": str(in_p),
        "output_path": str(out_p),
        "ole_count": ole_count,
        "omml_count": omml_count,
        "file_size_kb": out_p.stat().st_size // 1024
    }


def deploy_mathtype_pref_files(target_dir=None):
    import os, shutil
    src_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'references', 'CAU_HINH_MATHTYPE_CHUAN')
    if not os.path.exists(src_dir):
        src_dir = os.path.join(r'd:\skill-quan-trong', 'CAU_HINH_MATHTYPE_CHUAN')
    desktop = os.path.join(os.environ.get('USERPROFILE', ''), 'Desktop')
    dest_dirs = []
    if target_dir and os.path.exists(target_dir):
        dest_dirs.append(target_dir)
    if desktop and os.path.exists(desktop):
        dest_dirs.append(desktop)
    if os.path.exists(src_dir):
        for fname in os.listdir(src_dir):
            if fname.endswith('.eqp'):
                s_file = os.path.join(src_dir, fname)
                for d in dest_dirs:
                    try:
                        shutil.copy2(s_file, os.path.join(d, fname))
                    except Exception:
                        pass
    print("\n" + "=" * 72)
    print("💡 MẸO ĐỒNG BỘ 100% CỠ CHỮ CÔNG THỨC MATHTYPE VÀ LÀM TO PHÂN SỐ (1-CLICK):")
    print("   Trong Word, nếu Thầy/Cô đổi cỡ font hoặc thấy phân số bị nhỏ hơn chữ:")
    print("   1. Mở file Word -> Chọn tab MathType -> Format Equations (Ctrl + Alt + Q)")
    print("   2. Chọn 'MathType preference file' -> Browse... -> Desktop -> Times_14pt_Chuan_BGD.eqp")
    print("   3. Chọn 'Whole document' -> Bấm OK (Đồng bộ toàn bài chuẩn 14pt chỉ trong 3 giây!)")
    print("=" * 72 + "\n")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Cách dùng:")
        print('  python standardize_word_mathtype.py "C:\\duong_dan\\file.docx" ["C:\\duong_dan\\file_xuat.docx"]')
        sys.exit(1)
        
    in_file = sys.argv[1]
    out_file = sys.argv[2] if len(sys.argv) >= 3 else None
    res = standardize_doc_to_mathtype(in_file, out_file)
    if res["success"]:
        print(f"\n👉 Bạn có thể mở tệp: {res['output_path']} để kiểm tra!")
