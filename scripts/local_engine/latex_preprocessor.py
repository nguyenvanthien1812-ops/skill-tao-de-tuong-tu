import sys
import types
import io

# ─────────────────────────────────────────────────────────────────────
# 🔒 [LOCK-FIX-PYTHON314-TYPING]
# Monkeypatch typing.io on Python 3.14 where it was removed.
# This prevents antlr4-python3-runtime from raising ModuleNotFoundError.
# ─────────────────────────────────────────────────────────────────────
if "typing.io" not in sys.modules:
    import typing
    typing_io = types.ModuleType("typing.io")
    typing_io.TextIO = typing.TextIO if hasattr(typing, "TextIO") else io.TextIOBase
    typing_io.BinaryIO = typing.BinaryIO if hasattr(typing, "BinaryIO") else io.BufferedIOBase
    sys.modules["typing.io"] = typing_io

import re

# ─────────────────────────────────────────────────────────────────────────────
# Bảng tra ký tự Unicode số mũ và chỉ số dưới → LaTeX toán học
# Lý do: pylatexenc map ² → \texttwosuperior (text mode), ³ → \textthreesuperior,
# còn các ký tự ⁴–⁹ bị giữ nguyên Unicode — không dùng được trong StarMath.
# Phải chặn trước pylatexenc bằng bảng tra thủ công này.
# ─────────────────────────────────────────────────────────────────────────────
_SUPERSCRIPT_UNICODE: dict[str, str] = {
    '\u2070': '0',  # ⁰
    '\u00b9': '1',  # ¹
    '\u00b2': '2',  # ²
    '\u00b3': '3',  # ³
    '\u2074': '4',  # ⁴
    '\u2075': '5',  # ⁵
    '\u2076': '6',  # ⁶
    '\u2077': '7',  # ⁷
    '\u2078': '8',  # ⁸
    '\u2079': '9',  # ⁹
    '\u2071': 'i',  # ⁱ
    '\u207f': 'n',  # ⁿ
}
_SUBSCRIPT_UNICODE: dict[str, str] = {
    '\u2080': '0',  # ₀
    '\u2081': '1',  # ₁
    '\u2082': '2',  # ₂
    '\u2083': '3',  # ₃
    '\u2084': '4',  # ₄
    '\u2085': '5',  # ₅
    '\u2086': '6',  # ₆
    '\u2087': '7',  # ₇
    '\u2088': '8',  # ₈
    '\u2089': '9',  # ₉
}


def _fix_unicode_super_sub(s: str) -> str:
    """Chuyển ký tự Unicode số mũ/chỉ số về dạng LaTeX chuẩn TRƯỚC khi pylatexenc xử lý.

    Ví dụ: 'x²' → 'x^{2}',  'a₁' → 'a_{1}'
    Cần chạy trước clean_unicode_chars() vì pylatexenc map ² → \\texttwosuperior
    (text mode) thay vì ^{2}, gây lỗi khi convert sang StarMath.
    """
    for ch, digit in _SUPERSCRIPT_UNICODE.items():
        s = s.replace(ch, f'^{{{digit}}}')
    for ch, digit in _SUBSCRIPT_UNICODE.items():
        s = s.replace(ch, f'_{{{digit}}}')
    return s

# Try to import optional packages
try:
    from pylatexenc.latexencode import unicode_to_latex
    HAS_PYLATEXENC = True
except ImportError:
    HAS_PYLATEXENC = False

try:
    from sympy.parsing.latex import parse_latex
    from sympy import latex
    HAS_SYMPY = True
except ImportError:
    HAS_SYMPY = False


def is_vietnamese_latin_char(ch: str) -> bool:
    """Nhận diện các chữ cái Tiếng Việt và Latin (bao gồm cả các chữ có dấu)."""
    if ch in ('đ', 'Đ'):
        return True
    import unicodedata
    nfd = unicodedata.normalize('NFD', ch)
    base = ''.join(c for c in nfd if unicodedata.category(c) != 'Mn')
    if base and len(base) == 1 and ('a' <= base.lower() <= 'z'):
        return True
    return False


def clean_unicode_chars(latex_str: str) -> str:
    """
    Sử dụng pylatexenc để chuyển đổi các ký tự Unicode toán học lạ (α, β, ≤, ≥, →...)
    về dạng lệnh LaTeX tương ứng trước khi đưa vào pipeline chính.
    """
    if not HAS_PYLATEXENC:
        return latex_str
 
    res = []
    for char in latex_str:
        if ord(char) > 127:
            if is_vietnamese_latin_char(char):
                res.append(char)
                continue
            try:
                lat = unicode_to_latex(char)
                # Dọn các wrapper mà unicode_to_latex sinh ra
                if lat.startswith(r'\ensure_math{') and lat.endswith('}'):
                    lat = lat[13:-1]
                if lat.startswith(r'\ensure_math{') and lat.endswith('}'):
                    lat = lat[13:-1]
                if lat.startswith(r'\ensuremath{') and lat.endswith('}'):
                    lat = lat[12:-1]
                if lat.startswith('{') and lat.endswith('}'):
                    lat = lat[1:-1]
                if lat.startswith(r'\text'):
                    # Map các lệnh text sang math tương ứng
                    mapping = {
                        r'\textrightarrow': r'\rightarrow',
                        r'\textleftarrow': r'\leftarrow',
                        r'\texttimes': r'\times',
                        r'\textdiv': r'\div',
                        r'\textpm': r'\pm',
                        r'\textleq': r'\leq',
                        r'\textgeq': r'\geq',
                        r'\textneq': r'\neq',
                    }
                    lat = mapping.get(lat, lat)
                res.append(lat)
            except Exception:
                res.append(char)
        else:
            res.append(char)
    return "".join(res)


def check_latex_balanced(latex_str: str) -> tuple[bool, str]:
    """
    Kiểm tra ngoặc đóng mở của LaTeX có khớp hay không.
    Trả về (is_balanced, error_message).
    """
    # Đếm số lượng ngoặc nhọn
    open_braces = latex_str.count('{') - latex_str.count('\\{')
    close_braces = latex_str.count('}') - latex_str.count('\\}')
    if open_braces != close_braces:
        return False, f"Mất cân bằng dấu ngoặc nhọn: {open_braces} mở, {close_braces} đóng"

    # Đếm số lượng \left và \right
    left_count = len(re.findall(r'\\left\b', latex_str))
    right_count = len(re.findall(r'\\right\b', latex_str))
    if left_count != right_count:
        return False, f"Mất cân bằng \\left và \\right: {left_count} left, {right_count} right"

    return True, ""


def normalize_with_sympy(latex_str: str) -> str:
    """
    Sử dụng SymPy để chuẩn hóa các biểu thức toán học thuần túy.
    Bỏ qua nếu chứa các cấu trúc hình học, vector, text hoặc môi trường.
    """
    if not HAS_SYMPY:
        return latex_str

    # Các từ khóa loại trừ: nếu chứa thì tuyệt đối không chạy qua SymPy
    # vì SymPy sẽ làm mất cấu trúc hình học/vector hoặc tách biến (AB -> A B)
    exclude_patterns = [
        r'\\vec', r'\\overrightarrow', r'\\overleftarrow',
        r'\\widehat', r'\\overline', r'\\underline',
        r'\\angle', r'\\begin', r'\\end', r'\\text',
        r'\\mathrm', r'\\mathbf', r'\\stackrel', r'\\overparen', r'\\frown',
        # Tránh biến ghép nhiều chữ cái viết liền (nhãn điểm AB, CD...) bị tách thành A * B
        r'[A-Za-z]{2,}'
    ]
    
    for pattern in exclude_patterns:
        if re.search(pattern, latex_str):
            return latex_str

    try:
        expr = parse_latex(latex_str)
        normalized = latex(expr)
        # Nếu normalized không chứa khoảng trắng lạ phân tách biến ghép thì trả về
        return normalized
    except Exception:
        return latex_str


def preprocess_latex(latex_str: str) -> str:
    """
    Hàm tiền xử lý LaTeX chính. Chạy qua các bước dọn dẹp và chuẩn hóa an toàn.
    """
    if not latex_str or not latex_str.strip():
        return latex_str

    # Bước 0: Sửa ký tự Unicode số mũ/chỉ số TRƯỚC pylatexenc
    # (pylatexenc map ² → \texttwosuperior thay vì ^{2} → lỗi StarMath)
    processed = _fix_unicode_super_sub(latex_str)

    # Bước 1: Dọn dẹp ký tự Unicode lạ sang lệnh LaTeX tương ứng
    processed = clean_unicode_chars(processed)

    # Bước 2: Chuẩn hóa bằng SymPy nếu là biểu thức toán thuần và an toàn
    processed = normalize_with_sympy(processed)

    return processed


def latex_to_mathml_pandoc(latex_str: str) -> str or None:
    """
    Fallback engine: Sử dụng Pandoc chuyển đổi LaTeX sang MathML khi engine chính lỗi.
    Yêu cầu máy phải cài đặt Pandoc.
    """
    import subprocess
    try:
        # Bọc $$...$$ để pandoc nhận diện là math block
        input_tex = f"$${latex_str}$$"
        result = subprocess.run(
            ["pandoc", "-f", "latex", "-t", "mathml", "--mathml"],
            input=input_tex,
            capture_output=True,
            text=True,
            encoding="utf-8"
        )
        if result.returncode == 0:
            return result.stdout
    except Exception:
        pass
    return None
