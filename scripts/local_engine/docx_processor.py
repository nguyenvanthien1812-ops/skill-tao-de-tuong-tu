import os
import re
import uuid
import copy
import zipfile
import logging
import tempfile
import subprocess
import json
import struct
from lxml import etree
import latex2mathml.converter
import omml_converter
import omml_converter.mtef
# Monkeypatch MathType default size to 14pt (448 / 32 = 14) so that MathType on user's PC renders it at 14pt
omml_converter.mtef._size_display = lambda: b"\x09\x65\xC0\x01"

import sys
# Portable path setup: prioritize local directory & bundled packages
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

try:
    import site
    for _p in site.getsitepackages():
        if _p not in sys.path:
            sys.path.append(_p)
    _user_site = site.getusersitepackages()
    if _user_site and _user_site not in sys.path:
        sys.path.append(_user_site)
except Exception:
    pass
import olefile

import latex_to_starmath
from mathtype_ole_builder import make_mathtype_ole, make_arc_equation_ole, repatch_ole_widehat
try:
    from arc_symbol_builder import (
        extract_pure_arc_base,
        build_arc_equation_native,
        parse_arc_latex_expression,
        is_arc_containing_latex,
        split_latex_by_arcs,
    )
except Exception:
    extract_pure_arc_base = None  # type: ignore
    build_arc_equation_native = None  # type: ignore
    parse_arc_latex_expression = None  # type: ignore
    is_arc_containing_latex = None  # type: ignore
    split_latex_by_arcs = None  # type: ignore
# --- Doc3 MTEF builder (inline, không phụ thuộc file ngoài) ---
# -*- coding: utf-8 -*-
"""build_doc3_mtef.py — MTEF v5 MathType giống Doc3 (1 object, cung tmFROWN)."""

import re
import struct
from pathlib import Path
from typing import Optional

# Doc3 Equation Native — lấy 219 byte đầu (hdr+fonts+size block)
_DOC3_FULL = Path(__file__).with_name("doc3_eq_native.bin")
_FALLBACK_DOC3 = Path("/home/user/doc3_eq_native.bin")


_PREFIX219_HEX = "1c00000002007dc21c010000000000008838fa062ddf88000c003d06050100070844534d543700011357696e416c6c4261736963436f6465506167657300110554696d6573204e657720526f6d616e00110353796d626f6c001105436f7572696572204e65770011044d5420457874726100120008212f458f442f4150f4100f475f4150f21f1e4150f4150f4100f445f425f48f425f4100f4100f435f4100f48f45f42a5f48f48f4100f4100f40f48f417f48f4100f412a5f445f45f45f45f45f410f0c0100010001020202020002000101010003000100040000"


def _prefix219() -> bytes:
    return bytes.fromhex(_PREFIX219_HEX)



def _finalize(content: bytes) -> bytes:
    pref = bytearray(_prefix219())
    stream_after_hdr = bytes(pref[28:]) + content
    out = bytearray(pref[:28]) + stream_after_hdr
    # pref already includes bytes 28..218; content appends after 219
    # Fix: pref[28:] is fonts through size block (191 bytes); content is formula
    out = bytearray(28)
    out[0:28] = pref[0:28]
    rest = bytes(pref[28:219]) + content
    out += rest
    struct.pack_into("<I", out, 8, len(rest))
    return bytes(out)


def _char_code(ch: str, typeface: int) -> bytes:
    """CHAR MTEF v5: typeface|0x80 + MTCode LE 2 bytes."""
    cp = ord(ch)
    return bytes([0x02, 0x00, typeface | 0x80, cp & 0xFF, (cp >> 8) & 0xFF])


def _char_text(ch: str) -> bytes:
    return _char_code(ch, 0x01)  # Times/text


def _char_var(ch: str) -> bytes:
    return _char_code(ch, 0x03)  # variables / italic


def _char_sym(ch: str) -> bytes:
    """Ký hiệu toán: dùng typeface Text (1) + MTCode Unicode — tránh ◆? của Symbol."""
    return _char_code(ch, 0x01)


def _char_fn(ch: str) -> bytes:
    """Chữ hàm sin/cos: upright text."""
    return _char_code(ch, 0x01)


def _chars_fn(s: str) -> bytes:
    return b"".join(_char_fn(c) for c in s)


def _char_hat(ch: str) -> bytes:
    # embellished char (legacy helper; widehat uses TMPL tmHAT)
    return bytes([0x02, 0x01, 0x81, ord(ch) & 0xFF, 0x00, 0x06, 0x00, 0x09, 0x00])


def _chars_text(s: str) -> bytes:
    return b"".join(_char_text(c) for c in s)


def _chars_var(s: str) -> bytes:
    return b"".join(_char_var(c) for c in s)


def _tmpl_frac_slots(num_bytes: bytes, den_bytes: bytes) -> bytes:
    """Phân số tmFRACT (0x0B) với nội dung slot đã encode."""
    b = bytearray(bytes.fromhex("03000b00000100"))
    b += num_bytes
    b += bytes.fromhex("000100")  # END num + start den line-ish
    b += den_bytes
    b += bytes.fromhex("0000")
    return bytes(b)


def _tmpl_frac(num: str, den: str) -> bytes:
    return _tmpl_frac_slots(_chars_text(num), _chars_text(den))


def _tmpl_sqrt(content_bytes: bytes) -> bytes:
    """Căn bậc hai tmROOT (selector 0x0A): slot chính = nội dung, slot chỉ số rỗng."""
    b = bytearray(bytes.fromhex("03000a00000100"))
    b += content_bytes
    b += bytes.fromhex("0000")  # END main + empty index END
    return bytes(b)


def _tmpl_frown(base: str) -> bytes:
    b = bytearray(bytes.fromhex("03002200000100"))
    b += _chars_var(base)
    b += b"\x00"
    b += bytes.fromhex("020096222300")
    b += b"\x00\x00"
    return bytes(b)


def _tmpl_widehat(base: str) -> bytes:
    """Góc widehat — TMPL tmHAT (selector 0x21=33), mũ góc U+0302."""
    b = bytearray(bytes.fromhex("03002100000100"))  # tmHAT = 33
    b += _chars_var(base)
    b += b"\x00"
    # Glyph mũ góc MT Extra / U+0302 (LE: 02 03) — KHÔNG dùng cung U+2322
    b += bytes.fromhex("020096020300")
    b += b"\x00\x00"
    return bytes(b)


def _line_start() -> bytes:
    return bytes.fromhex("0a01000100")


def build_arc_equation_native_doc3(base_letters: str) -> bytes:
    if not (base_letters and all(c.isalnum() and c.isascii() for c in base_letters)):
        raise ValueError("base_letters ASCII alnum")
    return _finalize(_line_start() + _tmpl_frown(base_letters))


def build_widehat_equation_native_doc3(base_letters: str) -> bytes:
    """OLE Equation Native cho pure \\widehat{ABC} (MTEF v5 tmHAT)."""
    if not (base_letters and all(c.isalnum() and c.isascii() for c in base_letters)):
        raise ValueError("base_letters ASCII alnum")
    return _finalize(
        _line_start()
        + bytes.fromhex("0100")
        + _tmpl_widehat(base_letters)
        + bytes([0x00])
    )


def _strip_math_wrappers(latex: str) -> str:
    s = (latex or "").strip()
    if s.startswith("$$") and s.endswith("$$"):
        s = s[2:-2].strip()
    elif s.startswith("$") and s.endswith("$"):
        s = s[1:-1].strip()
    return s


def _parse_latex_group(s: str, i: int):
    """Parse { ... } starting at s[i]=='{'. Return (inner, index_after)."""
    if i >= len(s) or s[i] != "{":
        raise ValueError("expected '{'")
    depth = 0
    j = i
    while j < len(s):
        if s[j] == "{":
            depth += 1
        elif s[j] == "}":
            depth -= 1
            if depth == 0:
                return s[i + 1:j], j + 1
        j += 1
    raise ValueError("unbalanced '{'")


def _encode_math_expr(expr: str):
    """Encode một biểu thức LaTeX hình học (có thể chứa widehat/frac/sqrt/sin...).

    Trả bytes MTEF content hoặc None nếu gặp token ngoài scope.
    """
    if expr is None:
        return None
    s = expr.strip()
    if not s:
        return b""

    # Normalize spacing / noop
    s = s.replace(r"\,", " ").replace(r"\;", " ").replace(r"\!", "")
    s = re.sub(r"\\(?:displaystyle|textstyle|scriptstyle|limits)\b", "", s)
    s = s.replace(r"\left", "").replace(r"\right", "")
    # Unicode operators hay dính từ Word/AI → LaTeX-equivalent tokens
    s = (s.replace("⇒", r" \Rightarrow ")
           .replace("→", r" \rightarrow ")
           .replace("≈", r" \approx ")
           .replace("≤", r" \leq ")
           .replace("≥", r" \geq ")
           .replace("≠", r" \neq ")
           .replace("·", r" \cdot ")
           .replace("×", r" \times ")
           .replace("±", r" \pm ")
           .replace("∞", r" \infty ")
           .replace("⊥", r" \perp ")
           .replace("∠", r" \angle ")
           .replace("°", r"^\circ ")
           .replace("−", "-")
           .replace("–", "-")
           .replace("—", "-"))
    s = re.sub(r"\s+", " ", s).strip()

    i = 0
    n = len(s)
    out = bytearray()

    def skip_ws():
        nonlocal i
        while i < n and s[i].isspace():
            i += 1

    def append_plain_ident(ident: str):
        if not ident:
            return
        # function names already handled; mixed alnum → var letters + text digits
        if all(c.isalpha() for c in ident):
            out.extend(_chars_var(ident))
        elif all(c.isdigit() for c in ident):
            out.extend(_chars_text(ident))
        else:
            for ch in ident:
                if ch.isalpha():
                    out.extend(_char_var(ch))
                else:
                    out.extend(_char_text(ch))

    # Operators / relations — MTCode Unicode + typeface text (tránh ◆)
    op_map = [
        (r"\implies", "⇒"),
        (r"\Rightarrow", "⇒"),
        (r"\rightarrow", "→"),
        (r"\to", "→"),
        (r"\approx", "≈"),
        (r"\cdot", "·"),
        (r"\times", "×"),
        (r"\perp", "⊥"),
        (r"\leq", "≤"),
        (r"\geq", "≥"),
        (r"\le", "≤"),
        (r"\ge", "≥"),
        (r"\neq", "≠"),
        (r"\ne", "≠"),
        (r"\pm", "±"),
        (r"\mp", "∓"),
        (r"\infty", "∞"),
        (r"\angle", "∠"),
        (r"\triangle", "△"),
    ]
    # sort longer first
    op_map.sort(key=lambda x: -len(x[0]))

    fn_names = (
        "arcsin", "arccos", "arctan", "sin", "cos", "tan", "cot", "sec", "csc",
        "log", "ln", "exp", "min", "max", "det", "dim", "ker", "deg",
    )

    while True:
        skip_ws()
        if i >= n:
            break

        # \widehat{BASE}
        if s.startswith(r"\widehat", i):
            j = i + len(r"\widehat")
            while j < n and s[j].isspace():
                j += 1
            if j >= n or s[j] != "{":
                return None
            base, j = _parse_latex_group(s, j)
            base = re.sub(r"\s+", "", base)
            if not base or not all(c.isalnum() and c.isascii() for c in base):
                return None
            out.extend(_tmpl_widehat(base))
            i = j
            continue

        # \sqrt{...} or \sqrt[n]{...} — chỉ hỗ trợ \sqrt{simple}
        if s.startswith(r"\sqrt", i):
            j = i + 5
            while j < n and s[j].isspace():
                j += 1
            if j < n and s[j] == "[":
                # optional index — skip for now if present with simple content
                k = s.find("]", j)
                if k < 0:
                    return None
                j = k + 1
                while j < n and s[j].isspace():
                    j += 1
            if j >= n or s[j] != "{":
                return None
            inner, j = _parse_latex_group(s, j)
            inner_b = _encode_math_expr(inner)
            if inner_b is None:
                return None
            out.extend(_tmpl_sqrt(inner_b))
            i = j
            continue

        # \frac{num}{den} with recursive bodies
        if s.startswith(r"\frac", i) or s.startswith(r"\dfrac", i) or s.startswith(r"\tfrac", i):
            if s.startswith(r"\dfrac", i) or s.startswith(r"\tfrac", i):
                j = i + 6
            else:
                j = i + 5
            while j < n and s[j].isspace():
                j += 1
            if j >= n or s[j] != "{":
                return None
            num, j = _parse_latex_group(s, j)
            while j < n and s[j].isspace():
                j += 1
            if j >= n or s[j] != "{":
                return None
            den, j = _parse_latex_group(s, j)
            nb = _encode_math_expr(num)
            db = _encode_math_expr(den)
            if nb is None or db is None:
                return None
            out.extend(_tmpl_frac_slots(nb, db))
            i = j
            continue

        # \text{...} / \mathrm{...} / \operatorname{...}
        m_txt = re.match(r"\\(?:text|mathrm|textrm|textit|mathbf|operatorname)\s*\{", s[i:])
        if m_txt:
            j = i + m_txt.end() - 1
            body, j = _parse_latex_group(s, j)
            out.extend(_chars_text(body))
            i = j
            continue

        # functions \sin \cos ...
        fn_hit = False
        for fn in fn_names:
            tok = "\\" + fn
            if s.startswith(tok, i):
                # ensure not prefix of longer command
                endp = i + len(tok)
                if endp < n and s[endp].isalpha():
                    continue
                out.extend(_chars_fn(fn))
                i = endp
                # optional thin space before next atom
                fn_hit = True
                break
        if fn_hit:
            continue

        # subscript _ {..} or _x
        if s[i] == "_" and i + 1 < n:
            j = i + 1
            while j < n and s[j].isspace():
                j += 1
            if j < n and s[j] == "{":
                body, j = _parse_latex_group(s, j)
                sub_b = _encode_math_expr(body)
                if sub_b is None:
                    return None
            else:
                m_one = re.match(r"[A-Za-z0-9]", s[j:])
                if not m_one:
                    return None
                sub_b = _encode_math_expr(m_one.group(0))
                if sub_b is None:
                    return None
                j += 1
            # TMPL tmSUB selector 27 = 0x1B
            out.extend(bytes.fromhex("03001b00000100"))
            out.extend(sub_b)
            out.extend(bytes([0x00, 0x00]))
            i = j
            continue

        # superscript ^{...} except ^{\circ} handled below; ^digit
        if s[i] == "^" and i + 1 < n and not s.startswith(r"^\circ", i) and not s.startswith(r"^{\circ}", i):
            j = i + 1
            while j < n and s[j].isspace():
                j += 1
            if j < n and s[j] == "{":
                body, j = _parse_latex_group(s, j)
                sup_b = _encode_math_expr(body)
                if sup_b is None:
                    return None
            else:
                m_one = re.match(r"[A-Za-z0-9]", s[j:])
                if not m_one:
                    return None
                sup_b = _encode_math_expr(m_one.group(0))
                if sup_b is None:
                    return None
                j += 1
            # TMPL tmSUP selector 28 = 0x1C
            out.extend(bytes.fromhex("03001c00000100"))
            out.extend(sup_b)
            out.extend(bytes([0x00, 0x00]))
            i = j
            continue

        # degree
        _deg_tokens = (r"^\circ", r"^{\circ}", r"\circ")
        _deg_hit = False
        for _dt in _deg_tokens:
            if s.startswith(_dt, i):
                out.extend(_char_text("°"))
                i += len(_dt)
                _deg_hit = True
                break
        if _deg_hit:
            continue

        # \pi
        if s.startswith(r"\pi", i) and (i + 3 >= n or not s[i + 3].isalpha()):
            out.extend(_char_code("π", 0x03))  # variable-ish Greek
            i += 3
            continue

        # relations / ops
        hit = False
        for tok, sym in op_map:
            if s.startswith(tok, i):
                out.extend(_char_text(sym))
                i += len(tok)
                hit = True
                break
        if hit:
            continue

        # single-char ops / punctuation
        if s[i] in "=-+()[]|/,.;:":
            out.extend(_char_text(s[i]))
            i += 1
            continue

        # Nhóm {...} trần: {,} (thập phân EU) hoặc bọc đơn giản
        if s[i] == "{":
            try:
                body, j = _parse_latex_group(s, i)
            except ValueError:
                return None
            body = body.strip()
            if body == ",":
                out.extend(_char_text(","))
                i = j
                continue
            if body == "":
                i = j
                continue
            inner_b = _encode_math_expr(body)
            if inner_b is None:
                return None
            out.extend(inner_b)
            i = j
            continue

        # decimal comma already handled; plain number or identifier
        m_id = re.match(r"[A-Za-z0-9]+(?:\.[0-9]+)?", s[i:])
        if m_id:
            ident = m_id.group(0)
            if re.fullmatch(r"[0-9]+(?:\.[0-9]+)?", ident):
                out.extend(_chars_text(ident))
            else:
                append_plain_ident(ident)
            i += len(ident)
            continue

        # Bo qua chu/prose khong-ASCII (Viet) va dau cau phu — khong fail ca CT
        _prose_extra = set('"\'') | set(' :') | {chr(0x201C), chr(0x201D), chr(0x2026), chr(0x00B7), chr(0x2022)}
        if ord(s[i]) > 127 or s[i] in _prose_extra:
            while i < n and (ord(s[i]) > 127 or s[i] in _prose_extra):
                i += 1
            continue

        # unknown ASCII token
        return None
    return bytes(out)


def _strip_leading_prose_before_math(s: str) -> str:
    """Bỏ tiền tố chữ thường (vd. 'Ta có ', 'Do hai góc...: ') trước phần toán.

    Công thức hỗn hợp trong đề hay dính lời Việt ngay trong $...$; encoder
    native chỉ cần phần math (\\sin/\\widehat/số...).
    """
    if not s:
        return s
    # Cắt từ lệnh LaTeX đầu tiên, hoặc từ chữ Latin/số toán học đứng trước \widehat/\sin/...
    m = re.search(
        r"(\\(?:widehat|hat|frac|dfrac|tfrac|sqrt|sin|cos|tan|cot|sec|csc|"
        r"arcsin|arccos|arctan|approx|implies|Rightarrow|rightarrow|to|perp|"
        r"cdot|times|leq|geq|neq|ne|pm|mp|infty|angle|triangle|pi|circ|"
        r"text|mathrm|operatorname|left|right)\b|[A-Za-z0-9]=|[A-Za-z]\\|"
        r"\\widehat\s*\{)",
        s,
    )
    if m:
        return s[m.start():].lstrip(" :;-–—")
    return s


def _angle_content_from_latex(latex: str):
    """Build MTEF content cho công thức có \\widehat (và sin/frac/sqrt/perp...).

    Mixed overparen → None (caller tách). Token lạ → None (fallback LO).
    """
    s = _strip_math_wrappers(latex)
    if not s or r"\widehat" not in s:
        return None
    if re.search(r"\\(?:overparen|wideparen|overarc|overgroup)\s*\{", s):
        return None
    s = _strip_leading_prose_before_math(s)
    return _encode_math_expr(s)



# 🔒 FIX TỐI THIỂU TRÊN V1
# Chỉ công thức có ĐÚNG MỘT \widehat và cấu trúc đơn giản mới dùng native tmHAT.
# Mixed/nhiều mũ giữ nguyên LibreOffice OLE để không ◆, không thiếu phần,
# không hiện Convert Equation Editor 3.0.
def _is_simple_native_angle_latex(latex: str) -> bool:
    """Native MTEF v5 tmHAT cho góc đơn lẫn phương trình chứa góc biên dịch được qua _encode_math_expr."""
    s = _strip_math_wrappers(latex or "").strip()
    if s.endswith(".") or s.endswith(",") or s.endswith(";"):
        s = s[:-1].strip()
    if not s or r"\\widehat" not in s:
        return False
    return _encode_math_expr(s) is not None


def build_angle_formula_native(latex: str):
    """Native MTEF v5 cho góc đơn và phương trình chứa góc qua OMML parser."""
    s = _strip_math_wrappers(latex or "").strip()
    if s.endswith(".") or s.endswith(",") or s.endswith(";"):
        s = s[:-1].strip()
    try:
        from converter_xml import latex_to_omml
        from omml_to_mtef import omml_to_mtef
        omml = latex_to_omml(s)
        return omml_to_mtef(omml)
    except Exception:
        content = _encode_math_expr(s)
        if not content:
            return None
        line_wrapped = bytes([0x01, 0x00]) + content + bytes([0x00])
        return _finalize(_line_start() + line_wrapped)

def build_geometry_formula_native(latex: str) -> Optional[bytes]:
    """1 object MTEF v5 cho PURE cung, hoặc công thức góc \\widehat trong scope.

    - Pure overparen/wideparen/overarc → tmFROWN
    - Có \\widehat (không lẫn overparen) → tmHAT native (fix double-click mất mũ)
    """
    if not latex:
        return None
    s = _strip_math_wrappers(latex)
    s_nospace = re.sub(r"\s+", "", s)

    # PURE arc only
    m = re.fullmatch(r"\\(?:overparen|wideparen|overarc)\{([A-Za-z0-9]+)\}", s_nospace)
    if m:
        return build_arc_equation_native_doc3(m.group(1))

    # Angle / widehat formulas (no arc mixed here)
    if r"\widehat" in s:
        return build_angle_formula_native(s)
    return None

# aliases already defined: build_geometry_formula_native, build_arc_equation_native_doc3
try:
    from latex_preprocessor import preprocess_latex, latex_to_mathml_pandoc
    HAS_PREPROCESSOR = True
except ImportError:
    HAS_PREPROCESSOR = False

# Check if pywin32 is available for structured storage manipulation
try:
    import pythoncom
    from win32com import storagecon
    HAS_PYWIN32 = True
except ImportError:
    HAS_PYWIN32 = False

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("docx_processor")


def _maybe_repatch_ole_widehat(ole_bin, latex_formula, idx=None, logger=None):
    """KHÔNG splice OLE LO để tránh lỗi Word báo 'The program used to create this object is Equation'."""
    return ole_bin


def find_libreoffice_python() -> str:
    """Find the path to the LibreOffice python interpreter."""
    candidates = [
        r"C:\Program Files\LibreOffice\program\python.exe",
        r"C:\Program Files (x86)\LibreOffice\program\python.exe",
        os.path.expandvars(r"%ProgramFiles%\LibreOffice\program\python.exe"),
        os.path.expandvars(r"%ProgramFiles(x86)%\LibreOffice\program\python.exe"),
    ]
    for c in candidates:
        if c and os.path.exists(c):
            return c
    try:
        import winreg
        for root in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
            for subkey in (
                r"SOFTWARE\LibreOffice\UNO\InstallPath",
                r"SOFTWARE\The Document Foundation\LibreOffice",
                r"SOFTWARE\WOW6432Node\LibreOffice\UNO\InstallPath",
            ):
                try:
                    with winreg.OpenKey(root, subkey) as k:
                        val, _ = winreg.QueryValueEx(k, "")
                        py = os.path.join(val, "python.exe")
                        if os.path.exists(py):
                            return py
                except Exception:
                    pass
    except Exception:
        pass
    import shutil
    soffice = shutil.which("soffice")
    if soffice:
        py = os.path.join(os.path.dirname(soffice), "python.exe")
        if os.path.exists(py):
            return py
    return ""

def get_wmf_size_emu(wmf_path: str) -> tuple[int, int]:
    """Read a WMF file and return its dimensions in EMU from the Aldus Placeable Header."""
    import struct
    if not os.path.exists(wmf_path):
        return 914400, 457200 # Fallback 1" x 0.5"
    try:
        with open(wmf_path, "rb") as f:
            header = f.read(22)
        if len(header) < 22:
            return 914400, 457200
        key, handle, left, top, right, bottom, inch, reserved, checksum = struct.unpack("<IHhhhhHIH", header)
        if key == 0x9AC6CDD7: # Aldus placeable header
            width_units = right - left
            height_units = bottom - top
            # 1 inch = 914400 EMU. The 'inch' field specifies units per inch in the WMF.
            width_emu = int(width_units * (914400 / inch))
            height_emu = int(height_units * (914400 / inch))
            # Ensure they are positive and reasonable
            if width_emu > 0 and height_emu > 0:
                return width_emu, height_emu
    except Exception as e:
        logger.error("Error reading WMF dimensions for %s: %s", wmf_path, e)
    return 914400, 457200

def apply_formatting_times_new_roman_14(zdata: dict, doc_root: etree._Element) -> None:
    """Apply Times New Roman font and size 14 (28 half-points) to all text runs and document defaults."""
    # 1. Update all runs in document.xml
    for r in doc_root.iter(_w("r")):
        # Only modify runs that contain text or field instructions
        if r.find(_w("t")) is not None or r.find(_w("instrText")) is not None:
            rPr = r.find(_w("rPr"))
            if rPr is None:
                rPr = etree.Element(_w("rPr"))
                r.insert(0, rPr)
                
            rFonts = rPr.find(_w("rFonts"))
            if rFonts is None:
                rFonts = etree.Element(_w("rFonts"))
                rPr.append(rFonts)
            rFonts.set(_w("ascii"), "Times New Roman")
            rFonts.set(_w("hAnsi"), "Times New Roman")
            rFonts.set(_w("eastAsia"), "Times New Roman")
            rFonts.set(_w("cs"), "Times New Roman")
            
            sz = rPr.find(_w("sz"))
            if sz is None:
                sz = etree.Element(_w("sz"))
                rPr.append(sz)
            sz.set(_w("val"), "28")
            
            szCs = rPr.find(_w("szCs"))
            if szCs is None:
                szCs = etree.Element(_w("szCs"))
                rPr.append(szCs)
            szCs.set(_w("val"), "28")
            
    # 2. Update styles.xml default docDefaults if it exists
    styles_xml_path = "word/styles.xml"
    if styles_xml_path in zdata:
        try:
            styles_root = _parse_xml(zdata[styles_xml_path])
            # Check docDefaults
            docDefaults = styles_root.find(_w("docDefaults"))
            if docDefaults is None:
                docDefaults = etree.Element(_w("docDefaults"))
                styles_root.insert(0, docDefaults)
            rPrDefault = docDefaults.find(_w("rPrDefault"))
            if rPrDefault is None:
                rPrDefault = etree.Element(_w("rPrDefault"))
                docDefaults.append(rPrDefault)
            rPr = rPrDefault.find(_w("rPr"))
            if rPr is None:
                rPr = etree.Element(_w("rPr"))
                rPrDefault.append(rPr)
                
            rFonts = rPr.find(_w("rFonts"))
            if rFonts is None:
                rFonts = etree.Element(_w("rFonts"))
                rPr.append(rFonts)
            rFonts.set(_w("ascii"), "Times New Roman")
            rFonts.set(_w("hAnsi"), "Times New Roman")
            rFonts.set(_w("eastAsia"), "Times New Roman")
            rFonts.set(_w("cs"), "Times New Roman")
            
            sz = rPr.find(_w("sz"))
            if sz is None:
                sz = etree.Element(_w("sz"))
                rPr.append(sz)
            sz.set(_w("val"), "28")
            
            szCs = rPr.find(_w("szCs"))
            if szCs is None:
                szCs = etree.Element(_w("szCs"))
                rPr.append(szCs)
            szCs.set(_w("val"), "28")
            
            zdata[styles_xml_path] = _serialise_xml(styles_root)
        except Exception as e:
            logger.error("Error patching styles.xml: %s", e)

# Namespaces
_MC = "http://schemas.openxmlformats.org/markup-compatibility/2006"
_W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
_O = "urn:schemas-microsoft-com:office:office"
_V = "urn:schemas-microsoft-com:vml"
_R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
_M = "http://schemas.openxmlformats.org/officeDocument/2006/math"

_REL_OLEOBJECT = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/oleObject"
_REL_IMAGE = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image"

def _w(tag: str) -> str:
    return f"{{{_W}}}{tag}"

def _o(tag: str) -> str:
    return f"{{{_O}}}{tag}"

def _v(tag: str) -> str:
    return f"{{{_V}}}{tag}"

def _r(tag: str) -> str:
    return f"{{{_R}}}{tag}"

def find_mml2omml_xslt() -> str:
    """Find the path of the MML2OMML.XSL file in common Microsoft Office directories."""
    paths_to_check = [
        r"C:\Program Files\Microsoft Office\root\Office16\MML2OMML.XSL",
        r"C:\Program Files (x86)\Microsoft Office\root\Office16\MML2OMML.XSL",
        r"C:\Program Files\Microsoft Office 15\root\office15\MML2OMML.XSL",
        r"C:\Program Files (x86)\Microsoft Office 15\root\office15\MML2OMML.XSL",
    ]
    
    for p in paths_to_check:
        if os.path.exists(p):
            return p
            
    import glob
    matches = glob.glob(r"C:\Program Files\**\MML2OMML.XSL", recursive=True)
    if matches:
        return matches[0]
        
    matches_x86 = glob.glob(r"C:\Program Files (x86)\**\MML2OMML.XSL", recursive=True)
    if matches_x86:
        return matches_x86[0]
        
    raise FileNotFoundError("Không tìm thấy tệp MML2OMML.XSL của Microsoft Office trên hệ thống.")

def clean_proof_errors(doc_root: etree._Element) -> None:
    """Remove all spelling and grammar error tags which often split text runs."""
    etree.strip_tags(doc_root, _w("proofErr"))
    etree.strip_tags(doc_root, _w("noProof"))

def merge_adjacent_runs(p_node: etree._Element) -> None:
    """Combine adjacent text runs with identical formatting to help match LaTeX patterns."""
    children = list(p_node)
    i = 0
    while i < len(children) - 1:
        current = children[i]
        next_el = children[i + 1]
        
        # Check if both are run elements
        if current.tag == _w("r") and next_el.tag == _w("r"):
            rPr_curr = current.find(_w("rPr"))
            rPr_next = next_el.find(_w("rPr"))
            
            def is_rPr_equal(a, b) -> bool:
                if a is None and b is None:
                    return True
                if a is None or b is None:
                    return False
                return etree.tostring(a) == etree.tostring(b)
            
            if is_rPr_equal(rPr_curr, rPr_next):
                t_curr = current.find(_w("t"))
                t_next = next_el.find(_w("t"))
                
                if t_curr is not None and t_next is not None:
                    t_curr.text = (t_curr.text or "") + (t_next.text or "")
                    p_node.remove(next_el)
                    children = list(p_node)
                    continue
        i += 1

def lint_unbalanced_dollars(doc_root: etree._Element) -> list:
    """Flag paragraphs whose unescaped '$' count is odd.

    An odd count means a '$...$' formula is missing a delimiter (e.g. the
    opening '$' was dropped in the source), so the paired-'$' regex never
    matches it and the formula silently passes through as raw text instead of
    becoming MathType. Returns a list of warning strings; the caller surfaces
    them so the source error is loud instead of silent.
    """
    warnings = []
    # Count only unescaped '$' (a literal '\$' is not a delimiter).
    dollar_re = re.compile(r'(?<!\\)\$')
    for p in doc_root.iter(_w("p")):
        text = "".join(t.text or "" for t in p.iter(_w("t")))
        if not text or "$" not in text:
            continue
        n = len(dollar_re.findall(text))
        if n % 2 != 0:
            snippet = text.strip()[:80]
            warnings.append(f"odd '$' count ({n}) — a formula delimiter is missing: {snippet!r}")
    return warnings


def isolate_latex_runs(p_node: etree._Element, pattern: re.Pattern) -> list:
    """Find text runs containing LaTeX formulas and split them so the LaTeX formula is isolated in its own run."""
    children = list(p_node)
    i = 0
    matched_runs = []
    
    while i < len(children):
        child = children[i]
        if child.tag == _w("r"):
            t_node = child.find(_w("t"))
            if t_node is not None and t_node.text:
                text = t_node.text
                match = pattern.search(text)
                if match:
                    start, end = match.span()
                    prefix = text[:start]
                    latex_text = text[start:end]
                    suffix = text[end:]
                    
                    rPr = child.find(_w("rPr"))
                    
                    # Create prefix run
                    if prefix:
                        pre_run = etree.Element(child.tag)
                        if rPr is not None:
                            pre_run.append(copy.deepcopy(rPr))
                        pre_t = etree.SubElement(pre_run, _w("t"))
                        pre_t.text = prefix
                        pre_t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
                        p_node.insert(p_node.index(child), pre_run)
                        
                    # Create matching run
                    match_run = etree.Element(child.tag)
                    if rPr is not None:
                        match_run.append(copy.deepcopy(rPr))
                    match_t = etree.SubElement(match_run, _w("t"))
                    match_t.text = latex_text
                    match_t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
                    p_node.insert(p_node.index(child), match_run)
                    matched_runs.append(match_run)
                    
                    # Create suffix run
                    if suffix:
                        suf_run = etree.Element(child.tag)
                        if rPr is not None:
                            suf_run.append(copy.deepcopy(rPr))
                        suf_t = etree.SubElement(suf_run, _w("t"))
                        suf_t.text = suffix
                        suf_t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
                        p_node.insert(p_node.index(child), suf_run)
                        
                    p_node.remove(child)
                    children = list(p_node)
                    i = p_node.index(match_run) + 1
                    continue
        i += 1
    return matched_runs

def _make_ole_xml_alternate(rel_id: str, shape_id: str, obj_id: str, width_emu: int, height_emu: int, omml_fallback: etree._Element) -> etree._Element:
    """Build the mc:AlternateContent tag wrapping the MathType OLE object and OMML fallback."""
    ac = etree.Element(f"{{{_MC}}}AlternateContent", nsmap={"mc": _MC})
    
    _MTYPE_NS = "urn:mathtype:oleobject"
    choice = etree.SubElement(ac, f"{{{_MC}}}Choice", nsmap={"mtype": _MTYPE_NS})
    choice.set("Requires", "mtype")
    
    wr = etree.SubElement(choice, _w("r"))
    wobj = etree.SubElement(wr, _w("object"))
    wobj.set(_w("dxaOrig"), str(width_emu // 635))
    wobj.set(_w("dyaOrig"), str(height_emu // 635))
    
    vshape = etree.SubElement(wobj, _v("shape"))
    vshape.set("id", shape_id)
    vshape.set("type", "#_x0000_t75")
    vshape.set("style", f"width:{width_emu / 12700:.1f}pt;height:{height_emu / 12700:.1f}pt")
    vshape.set(f"{{{_O}}}ole", "")
    
    oleobj = etree.SubElement(wobj, _o("OLEObject"))
    oleobj.set("Type", "Embed")
    oleobj.set("ProgID", "Equation.DSMT4")  # MathType OLE
    oleobj.set("ShapeID", shape_id)
    oleobj.set("DrawAspect", "Content")
    oleobj.set("ObjectID", obj_id)
    oleobj.set(_r("id"), rel_id)
    
    fallback = etree.SubElement(ac, f"{{{_MC}}}Fallback")
    fallback.append(copy.deepcopy(omml_fallback))
    
    return ac

def _make_direct_ole_xml(rel_id: str, image_rel_id: str, shape_id: str, obj_id: str, width_emu: int, height_emu: int, baseline_frac: float = 0.28, position_half_pt: int | None = None) -> etree._Element:
    """Build a direct w:object tag pointing to the MathType OLE and the presentation image (WMF/EMF).

    baseline_frac: tỉ lệ chiều cao dùng tính w:position (mặc định 0.28 cho LO).
    position_half_pt: nếu set, dùng offset tuyệt đối (half-points) thay baseline_frac
      — để căn cung tròn đứng cạnh phân số trên cùng baseline chữ.
    """
    wr = etree.Element(_w("r"))
    
    # Calculate baseline offset (typically 28% of formula height, rounded to half-points)
    height_pt = height_emu / 12700.0
    # Create run properties with position offset to align shape to text baseline
    wrPr = etree.SubElement(wr, _w("rPr"))
    if position_half_pt is not None:
        if position_half_pt != 0:
            wpos = etree.SubElement(wrPr, _w("position"))
            wpos.set(_w("val"), str(int(round(position_half_pt))))
    else:
        offset_half_pt = int(round(height_pt * float(baseline_frac) * 2))
        if offset_half_pt > 0:
            wpos = etree.SubElement(wrPr, _w("position"))
            wpos.set(_w("val"), f"-{offset_half_pt}")
        
    wobj = etree.SubElement(wr, _w("object"))
    wobj.set(_w("dxaOrig"), str(width_emu // 635))
    wobj.set(_w("dyaOrig"), str(height_emu // 635))
    
    vshape = etree.SubElement(wobj, _v("shape"))
    vshape.set("id", shape_id)
    vshape.set("type", "#_x0000_t75")
    vshape.set("style", f"width:{width_emu / 12700:.1f}pt;height:{height_emu / 12700:.1f}pt")
    vshape.set(f"{{{_O}}}ole", "")
    
    vimagedata = etree.SubElement(vshape, _v("imagedata"))
    vimagedata.set(_r("id"), image_rel_id)
    vimagedata.set(f"{{{_O}}}title", "")
    
    oleobj = etree.SubElement(wobj, _o("OLEObject"))
    oleobj.set("Type", "Embed")
    oleobj.set("ProgID", "Equation.DSMT4")
    oleobj.set("ShapeID", shape_id)
    oleobj.set("DrawAspect", "Content")
    oleobj.set("ObjectID", obj_id)
    oleobj.set(_r("id"), rel_id)
    
    return wr

def make_equation_native_stream(mtef_content_bytes: bytes, template_native_stream: bytes | None = None) -> bytes:
    """Build an Equation Native stream with a MathType-like 28-byte header.

    🔒 LOCKED: KHÔNG dùng lại omml_converter.make_equation_native() (nó tạo
    header zero: cf=0 + 16 byte reserved zero) → MathType mở editor rỗng.
    Hàm này giữ header non-zero (copy từ template hoặc mẫu MathType thật) và chỉ
    patch cbObject. Kiểm bằng verify_mathtype_lock.py. Xem memory
    mathtype_empty_editor_bug.

    omml_converter.make_equation_native() uses cf=0 and 16 zero reserved bytes.
    Word can still list the OLE storage, but MathType may open an empty editor.
    Real MathType objects keep non-zero clipboard/header fields, so preserve the
    template header when available and only update cbObject.
    """
    mtef_data = omml_converter.mtef.build_mtef(mtef_content_bytes)
    if template_native_stream and len(template_native_stream) >= 28:
        header = bytearray(template_native_stream[:28])
        struct.pack_into("<H", header, 0, 28)              # cbHdr
        struct.pack_into("<I", header, 2, 0x00020000)      # version
        struct.pack_into("<I", header, 8, len(mtef_data))  # cbObject
        return bytes(header) + mtef_data

    # Fallback header copied from a real MathType 7 Equation Native stream.
    # cbObject is patched per formula below.
    header = bytearray(bytes.fromhex(
        "1c00000002002cc2da0000004b87fb0044d94f000c009d04dc7cec6f"
    ))
    struct.pack_into("<I", header, 8, len(mtef_data))
    return bytes(header) + mtef_data


def copy_storage_and_patch_mtef(template_bin_path: str, output_bin_path: str, new_mtef_bytes: bytes) -> None:
    """Copy all streams from the template OLE file to the output OLE file, patching the 'Equation Native' stream."""
    flags_read = storagecon.STGM_READ | storagecon.STGM_SHARE_EXCLUSIVE
    temp_stg = pythoncom.StgOpenStorage(template_bin_path, None, flags_read)
    
    flags_write = storagecon.STGM_READWRITE | storagecon.STGM_CREATE | storagecon.STGM_SHARE_EXCLUSIVE
    out_stg = pythoncom.StgCreateDocfile(output_bin_path, flags_write, 0)
    
    ctx = temp_stg.EnumElements(0, None, 0)
    while True:
        try:
            stat = ctx.Next(1)[0]
            name = stat[0]
            el_type = stat[1]
            
            if el_type == storagecon.STGTY_STREAM:
                stream_in = temp_stg.OpenStream(name, None, flags_read, 0)
                data = stream_in.Read(stat[2])
                
                stream_out = out_stg.CreateStream(name, flags_write, 0, 0)
                
                if name == "Equation Native":
                    new_native_stream = make_equation_native_stream(
                        new_mtef_bytes,
                        template_native_stream=data,
                    )
                    stream_out.Write(new_native_stream)
                else:
                    stream_out.Write(data)
        except Exception:
            break
            
    out_stg.Commit(storagecon.STGC_DEFAULT)

def patch_ole_bin_bytes(template_bin_bytes: bytes, new_mtef_bytes: bytes) -> bytes:
    """Patch the template OLE compound file bytes with new MTEF bytes in RAM using temporary files."""
    fd_tpl, tpl_path = tempfile.mkstemp(suffix=".bin")
    try:
        os.write(fd_tpl, template_bin_bytes)
    finally:
        os.close(fd_tpl)
        
    fd_out, out_path = tempfile.mkstemp(suffix=".bin")
    os.close(fd_out)
    
    try:
        copy_storage_and_patch_mtef(tpl_path, out_path, new_mtef_bytes)
        with open(out_path, "rb") as f:
            patched_data = f.read()
        return patched_data
    finally:
        if os.path.exists(tpl_path):
            os.remove(tpl_path)
        if os.path.exists(out_path):
            os.remove(out_path)

def _parse_xml(data: bytes) -> etree._Element:
    parser = etree.XMLParser(remove_blank_text=False)
    return etree.fromstring(data, parser)

def _serialise_xml(root: etree._Element) -> bytes:
    return etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)

def _add_relationship(rels_root: etree._Element, rel_id: str, rel_type: str, target: str) -> None:
    ns = "http://schemas.openxmlformats.org/package/2006/relationships"
    etree.SubElement(rels_root, f"{{{ns}}}Relationship", {"Id": rel_id, "Type": rel_type, "Target": target})

def _ensure_content_type(ct_root: etree._Element, part_name: str, content_type: str) -> None:
    ns = "http://schemas.openxmlformats.org/package/2006/content-types"
    for child in ct_root:
        if child.get("PartName") == part_name:
            return
    etree.SubElement(ct_root, f"{{{ns}}}Override", {"PartName": part_name, "ContentType": content_type})

def make_placeable_blank_wmf() -> bytes:
    """Generate a minimal valid 1x1 blank placeable WMF file in memory."""
    import struct
    key = 0x9AC6CDD7
    handle = 0
    left, top, right, bottom = 0, 0, 1000, 1000
    inch = 1440
    reserved = 0
    
    words = [
        key & 0xFFFF,
        (key >> 16) & 0xFFFF,
        handle,
        left & 0xFFFF,
        top & 0xFFFF,
        right & 0xFFFF,
        bottom & 0xFFFF,
        inch,
        reserved & 0xFFFF,
        (reserved >> 16) & 0xFFFF
    ]
    checksum = 0
    for w in words:
        checksum ^= w
        
    aldus_header = struct.pack("<IHHHHHHIH", key, handle, left, top, right, bottom, inch, reserved, checksum)
    wmf_header = struct.pack("<HHHHIHI", 1, 9, 0x0300, 12, 0, 3, 0)
    eof = struct.pack("<IH", 3, 0)
    return aldus_header + wmf_header + eof

def enhance_sqrt_png_preview(png_bytes: bytes) -> bytes:
    """Vẽ bù nét ngang (vinculum) cho công thức có căn (sqrt/nroot) nếu nét
    phía trên bị mảnh/mất. Các ngưỡng TỰ CO GIÃN theo kích thước ảnh nên hoạt
    động đúng cả với PNG nhỏ (~96 DPI cũ) lẫn PNG phóng to (shape ×8)."""
    try:
        from PIL import Image, ImageDraw
        import io, numpy as np

        im = Image.open(io.BytesIO(png_bytes)).convert("RGBA")
        arr = np.array(im.convert("L"))
        h, w = arr.shape
        dark_y, dark_x = np.where(arr < 200)
        if len(dark_y) == 0:
            return png_bytes

        min_y = int(dark_y.min())

        # Ngưỡng theo tỉ lệ ảnh (không hard-code cho ảnh nhỏ nữa):
        band = max(4, h // 12)          # dải quét từ đỉnh xuống để tìm cột nét căn
        min_seg_w = max(8, w // 12)     # bề rộng tối thiểu để coi là 1 dấu căn
        top_tol = max(2, h // 40)       # dung sai "chạm đỉnh"
        line_w = max(2, h // 60)        # bề dày nét vẽ bù

        # Cột nào có điểm tối trong dải đỉnh
        col_has_dark = np.any(arr[min_y:min_y + band, :] < 200, axis=0)

        segments = []
        in_seg = False
        seg_start = 0
        for x in range(len(col_has_dark)):
            if col_has_dark[x] and not in_seg:
                in_seg = True
                seg_start = x
            elif not col_has_dark[x] and in_seg:
                in_seg = False
                segments.append((seg_start, x - 1))
        if in_seg:
            segments.append((seg_start, len(col_has_dark) - 1))

        draw = ImageDraw.Draw(im)
        for seg_x1, seg_x2 in segments:
            # Đoạn này có bắt đầu bằng nét chạm đỉnh (dấu căn) và đủ rộng không?
            col_top = dark_y[dark_x == seg_x1]
            if len(col_top) and col_top.min() <= min_y + top_tol and seg_x2 - seg_x1 > min_seg_w:
                for dy in range(line_w):
                    draw.line([(seg_x1, min_y + dy), (seg_x2, min_y + dy)],
                              fill=(0, 0, 0, 255), width=1)

        out = io.BytesIO()
        im.save(out, format="PNG")
        return out.getvalue()
    except Exception as e:
        logger.error("Error enhancing radical PNG preview: %s", e)
    return png_bytes



def render_arc_preview_png(base_letters: str, font_pt: float = 14.0, scale: int = 8):
    """Vẽ PNG cung tròn giống MathType Doc2 + trả baseline_frac để căn hàng.

    Returns
    -------
    png_bytes, width_px, height_px, width_emu, height_emu, baseline_frac

    baseline_frac: tỉ lệ w:position sao cho ĐÁY CHỮ (không phải đáy cung)
    nằm trên baseline dòng — khớp phân số / chữ phía trước khi tách OLE.
    """
    import io
    import math
    from PIL import Image, ImageDraw, ImageFont

    base = "".join(c for c in (base_letters or "") if c.isalnum()) or "A"

    px_per_pt = 96.0 / 72.0
    font_px = max(16, int(round(font_pt * px_per_pt * scale)))

    def _load_font(size):
        candidates = [
            r"C:\Windows\Fonts\timesi.ttf",
            r"C:\Windows\Fonts\timesbi.ttf",
            r"C:\Windows\Fonts\Timesi.ttf",
            r"C:\Windows\Fonts\times.ttf",
            r"C:\Windows\Fonts\Times New Roman Italic.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]
        for fp in candidates:
            try:
                return ImageFont.truetype(fp, size), fp
            except Exception:
                continue
        return ImageFont.load_default(), ""

    font, font_path = _load_font(font_px)
    need_shear = (
        "timesi" not in font_path.lower()
        and "italic" not in font_path.lower()
        and "oblique" not in font_path.lower()
    )

    tmp = Image.new("RGBA", (4, 4), (0, 0, 0, 0))
    td = ImageDraw.Draw(tmp)
    bb = td.textbbox((0, 0), base, font=font)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]

    shear = 0.22 if need_shear else 0.0
    tw_s = int(math.ceil(tw + abs(shear) * th)) if shear else tw

    side = max(int(font_px * 0.08), 2)
    arc_overhang = max(int(tw_s * 0.06), int(font_px * 0.06))
    pad_x = side + arc_overhang
    # Chỗ cung phía trên; đáy ảnh = đáy chữ (0 pad dưới) để căn hàng với "sd"
    arc_room = max(int(th * 0.34), int(font_px * 0.17))
    pad_top = arc_room + max(2, int(font_px * 0.02))
    pad_bot = 0

    W = tw_s + pad_x * 2
    H = th + pad_top + pad_bot

    text_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    tdraw = ImageDraw.Draw(text_layer)
    tx = pad_x - bb[0]
    ty = pad_top - bb[1]
    tdraw.text((tx, ty), base, font=font, fill=(0, 0, 0, 255))
    if shear:
        cy = pad_top + th / 2.0
        a, b, c = 1.0, shear, -shear * cy
        d, e, f = 0.0, 1.0, 0.0
        text_layer = text_layer.transform(
            (W, H), Image.AFFINE, (a, b, c, d, e, f),
            resample=Image.BICUBIC, fillcolor=(0, 0, 0, 0),
        )

    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    im.alpha_composite(text_layer)
    dr = ImageDraw.Draw(im)

    alpha = im.split()[-1]
    ink = alpha.getbbox() or (pad_x, pad_top, pad_x + tw_s, pad_top + th)
    ink_l, ink_t, ink_r, ink_b = ink
    ink_w = max(1, ink_r - ink_l)

    x0 = ink_l - int(ink_w * 0.04)
    x1 = ink_r + int(ink_w * 0.04)
    y_end = ink_t + max(1, int(th * 0.02))
    y_peak = max(1, ink_t - int(arc_room * 0.78))

    p0 = (float(x0), float(y_end))
    p1 = (float(x1), float(y_end))
    c1 = (float(x0) + (x1 - x0) * 0.22, float(y_peak))
    c2 = (float(x0) + (x1 - x0) * 0.78, float(y_peak))

    def _cubic(t, a, b, c, d):
        u = 1.0 - t
        return (
            u*u*u*a[0] + 3*u*u*t*b[0] + 3*u*t*t*c[0] + t*t*t*d[0],
            u*u*u*a[1] + 3*u*u*t*b[1] + 3*u*t*t*c[1] + t*t*t*d[1],
        )

    n = 96
    pts = [_cubic(i / n, p0, c1, c2, p1) for i in range(n + 1)]
    stroke = max(2, int(round(font_px * 0.065)))
    for ox, oy in ((0, 0), (0, 0.6), (0.6, 0)):
        shifted = [(x + ox, y + oy) for x, y in pts]
        dr.line(shifted, fill=(0, 0, 0, 255), width=stroke, joint="curve")

    final_bb = im.split()[-1].getbbox()
    # Theo dõi: phần cung trên TOP chữ (ink_top_from_crop) sau crop
    ink_top_from_crop = float(arc_room)  # mặc định = arc_room trước crop
    if final_bb:
        l, t, r, b = final_bb
        pad = max(2, int(font_px * 0.03))
        l = max(0, l - pad)
        t = max(0, t - pad)
        r = min(W, r + pad)
        b = min(H, max(b, int(ink_b) + 1))
        # pad_top = vị trí TOP CHỮ trong ảnh gốc
        # t = vị trí crop từ ảnh gốc (cắt bỏ khoảng trắng trên đỉnh cung)
        # ink_top_from_crop = phần cung còn lại bên trên chữ sau crop
        ink_top_from_crop = max(0.0, float(pad_top) - float(t))
        im = im.crop((l, t, r, b))
        W, H = im.size

    # Flatten lên nền trắng
    if im.mode == "RGBA":
        bg = Image.new("RGB", im.size, (255, 255, 255))
        bg.paste(im, mask=im.split()[-1])
        im_out = bg
    else:
        im_out = im.convert("RGB")
    buf = io.BytesIO()
    im_out.save(buf, format="PNG")
    png = buf.getvalue()

    css_w = W / float(scale)
    css_h = H / float(scale)
    w_emu = max(1, int(round(css_w * 9525)))
    h_emu = max(1, int(round(css_h * 9525)))

    # Trong Word OOXML, inline OLE được đặt với ĐÁY OLE = baseline text (mặc định).
    # Chữ "AB" (in hoa, không có descender) nên letter bottom = OLE bottom = baseline.
    # => Chữ AB tự động ngang hàng với "sd" mà KHÔNG cần offset dọc.
    # position_half_pt = 0: không hạ/nâng OLE, đáy chữ AB = baseline ✓
    # (Giá trị dương sẽ NÂNG OLE lên; âm sẽ HẠ OLE xuống — đều sai cho trường hợp này)
    position_half_pt = 0

    # baseline_frac: tỉ lệ dự phòng (không dùng khi position_half_pt = 0)
    baseline_frac = 0.0

    return png, W, H, w_emu, h_emu, baseline_frac, position_half_pt






def render_geometry_formula_preview_png(latex: str, font_pt: float = 14.0, scale: int = 8):
    """Vẽ preview 1 ảnh cho công thức có overparen — PIL + bezier arc.

    Hỗ trợ: hat, widehat, frac, sqrt, overline, vec, text, =, +, -, ...
    Dùng render_arc_preview_png cho arc (bezier đẹp), PIL text cho phần còn lại.
    """
    import io
    import re as _re
    from PIL import Image, ImageDraw, ImageFont

    s = (latex or "").strip()
    if s.startswith("$$") and s.endswith("$$"):
        s = s[2:-2].strip()
    elif s.startswith("$") and s.endswith("$"):
        s = s[1:-1].strip()
    s = _re.sub(r"\s+", "", s)

    # Find all arcs
    arc_bases = []
    remaining = s
    while True:
        m = _re.search(r"\\(?:overparen|wideparen|overarc)\{([A-Za-z0-9]+)\}", remaining)
        if not m:
            break
        arc_bases.append((m.start(), m.end(), m.group(1)))
        remaining = remaining[:m.start()] + "{" + m.group(1) + "}" + remaining[m.end():]

    if not arc_bases:
        return None

    px_per_pt = 96.0 / 72.0
    font_px = max(16, int(round(font_pt * px_per_pt * scale)))

    def _font(size, italic=False):
        cands = []
        if italic:
            cands += [
                "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
            ]
        cands += [
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]
        for fp in cands:
            try:
                return ImageFont.truetype(fp, size)
            except Exception:
                continue
        return ImageFont.load_default()

    font = _font(font_px, italic=True)
    font_rm = _font(font_px, italic=False)
    font_script = _font(max(10, int(font_px * 0.72)), italic=False)

    tmp = Image.new("RGBA", (8, 8), (0, 0, 0, 0))
    td = ImageDraw.Draw(tmp)

    def text_size(t, f):
        bb = td.textbbox((0, 0), t, font=f)
        return bb[2] - bb[0], bb[3] - bb[1], bb

    # Tokenize remaining (arcs replaced with {base})
    def tokenize_math(text):
        tokens = []
        i = 0
        while i < len(text):
            c = text[i]
            if c == '{':
                j = text.index('}', i) if '}' in text[i:] else len(text)
                inner = text[i+1:j]
                tokens.append(("group", inner))
                i = j + 1
            elif c == '\\':
                j = i + 1
                while j < len(text) and text[j].isalpha():
                    j += 1
                cmd = text[i+1:j]
                if cmd in ('widehat',):
                    # Find next group
                    k = j
                    while k < len(text) and text[k] != '{':
                        k += 1
                    if k < len(text):
                        depth = 1
                        l = k + 1
                        while l < len(text) and depth > 0:
                            if text[l] == '{': depth += 1
                            elif text[l] == '}': depth -= 1
                            l += 1
                        inner = text[k+1:l-1]
                        tokens.append(("widehat", inner))
                        i = l
                    else:
                        i = j
                elif cmd in ('hat', 'vec', 'bar', 'tilde'):
                    k = j
                    while k < len(text) and text[k] != '{':
                        k += 1
                    if k < len(text):
                        depth = 1
                        l = k + 1
                        while l < len(text) and depth > 0:
                            if text[l] == '{': depth += 1
                            elif text[l] == '}': depth -= 1
                            l += 1
                        inner = text[k+1:l-1]
                        tokens.append(("accent", cmd, inner))
                        i = l
                    else:
                        i = j
                elif cmd in ('frac', 'dfrac', 'tfrac'):
                    args = []
                    k = j
                    for _ in range(2):
                        while k < len(text) and text[k] != '{':
                            k += 1
                        if k < len(text):
                            depth = 1
                            l = k + 1
                            while l < len(text) and depth > 0:
                                if text[l] == '{': depth += 1
                                elif text[l] == '}': depth -= 1
                                l += 1
                            args.append(text[k+1:l-1])
                            k = l
                    if len(args) == 2:
                        tokens.append(("frac", args[0], args[1]))
                        i = k
                    else:
                        i = j
                elif cmd in ('sqrt',):
                    k = j
                    while k < len(text) and text[k] != '{':
                        k += 1
                    if k < len(text):
                        depth = 1
                        l = k + 1
                        while l < len(text) and depth > 0:
                            if text[l] == '{': depth += 1
                            elif text[l] == '}': depth -= 1
                            l += 1
                        inner = text[k+1:l-1]
                        tokens.append(("sqrt", inner))
                        i = l
                    else:
                        i = j
                elif cmd in ('overline', 'underline'):
                    k = j
                    while k < len(text) and text[k] != '{':
                        k += 1
                    if k < len(text):
                        depth = 1
                        l = k + 1
                        while l < len(text) and depth > 0:
                            if text[l] == '{': depth += 1
                            elif text[l] == '}': depth -= 1
                            l += 1
                        inner = text[k+1:l-1]
                        tokens.append(("overline", inner))
                        i = l
                    else:
                        i = j
                elif cmd in ('mathrm', 'text', 'mathbf'):
                    k = j
                    while k < len(text) and text[k] != '{':
                        k += 1
                    if k < len(text):
                        depth = 1
                        l = k + 1
                        while l < len(text) and depth > 0:
                            if text[l] == '{': depth += 1
                            elif text[l] == '}': depth -= 1
                            l += 1
                        inner = text[k+1:l-1]
                        tokens.append(("text", inner))
                        i = l
                    else:
                        i = j
                else:
                    i = j
            elif c in '=+-':
                tokens.append(("op", c))
                i += 1
            elif c in '()[]|,':
                i += 1
            elif c == '^':
                # superscript
                if i + 1 < len(text) and text[i+1] == '{':
                    depth = 1
                    j = i + 2
                    while j < len(text) and depth > 0:
                        if text[j] == '{': depth += 1
                        elif text[j] == '}': depth -= 1
                        j += 1
                    tokens.append(("sup", text[i+2:j-1]))
                    i = j
                elif i + 1 < len(text):
                    tokens.append(("sup", text[i+1]))
                    i += 2
                else:
                    i += 1
            elif c == '_':
                if i + 1 < len(text) and text[i+1] == '{':
                    depth = 1
                    j = i + 2
                    while j < len(text) and depth > 0:
                        if text[j] == '{': depth += 1
                        elif text[j] == '}': depth -= 1
                        j += 1
                    tokens.append(("sub", text[i+2:j-1]))
                    i = j
                elif i + 1 < len(text):
                    tokens.append(("sub", text[i+1]))
                    i += 2
                else:
                    i += 1
            elif c.isalnum():
                tokens.append(("char", c))
                i += 1
            else:
                i += 1
        return tokens

    def render_math_tokens(tokens, is_script=False):
        """Render math tokens to PIL image. Returns (im, baseline_from_bottom)."""
        parts = []
        for tok in tokens:
            ttype = tok[0]
            if ttype == "char":
                ch = tok[1]
                f = font_script if is_script else font
                tw, th, bb = text_size(ch, f)
                pad = max(1, int(font_px * 0.04))
                im = Image.new("RGBA", (tw + pad*2, th + pad*2), (0, 0, 0, 0))
                dr = ImageDraw.Draw(im)
                dr.text((pad - bb[0], pad - bb[1]), ch, font=f, fill=(0, 0, 0, 255))
                parts.append((im, max(1, int(th * 0.12))))
            elif ttype == "op":
                ch = tok[1]
                f = font_rm
                tw, th, bb = text_size(ch, f)
                pad = max(1, int(font_px * 0.04))
                im = Image.new("RGBA", (tw + pad*2, th + pad*2), (0, 0, 0, 0))
                dr = ImageDraw.Draw(im)
                dr.text((pad - bb[0], pad - bb[1]), ch, font=f, fill=(0, 0, 0, 255))
                parts.append((im, max(1, int(th * 0.12))))
            elif ttype == "text":
                txt = tok[1]
                f = font_rm
                tw, th, bb = text_size(txt, f)
                pad = max(1, int(font_px * 0.04))
                im = Image.new("RGBA", (tw + pad*2, th + pad*2), (0, 0, 0, 0))
                dr = ImageDraw.Draw(im)
                dr.text((pad - bb[0], pad - bb[1]), txt, font=f, fill=(0, 0, 0, 255))
                parts.append((im, max(1, int(th * 0.12))))
            elif ttype == "group":
                inner = render_math_tokens(tok[1], is_script)
                if inner:
                    parts.append(inner)
            elif ttype == "widehat":
                inner = render_math_tokens([("char", c) for c in tok[1]])
                if inner:
                    im, bl = inner
                    # Add hat
                    w, h = im.size
                    hat_h = max(4, int(font_px * 0.15))
                    new_im = Image.new("RGBA", (w, h + hat_h), (0, 0, 0, 0))
                    new_im.alpha_composite(im, (0, hat_h))
                    dr = ImageDraw.Draw(new_im)
                    ink = new_im.split()[-1].getbbox()
                    if ink:
                        x0, x1 = max(0, ink[0]-2), min(w, ink[2]+2)
                        y_top = max(0, hat_h - int(font_px * 0.06))
                        y_peak = max(0, y_top - int(font_px * 0.10))
                        pts = []
                        n = 24
                        for i in range(n + 1):
                            tt = i / n
                            x = x0 + (x1 - x0) * tt
                            yy = y_peak + (y_top - y_peak) * (2*tt - 1)**2
                            pts.append((x, yy))
                        dr.line(pts, fill=(0, 0, 0, 255), width=max(2, int(font_px * 0.05)), joint="curve")
                    parts.append((new_im, bl + hat_h))
            elif ttype == "accent":
                cmd, inner = tok[1], tok[2]
                inner_tokens = [("char", c) for c in inner]
                inner_im, bl = render_math_tokens(inner_tokens)
                if inner_im:
                    w, h = inner_im.size
                    accent_h = max(4, int(font_px * 0.12))
                    new_im = Image.new("RGBA", (w, h + accent_h), (0, 0, 0, 0))
                    new_im.alpha_composite(inner_im, (0, accent_h))
                    parts.append((new_im, bl + accent_h))
            elif ttype == "frac":
                num_tokens = [("char", c) for c in tok[1]]
                den_tokens = [("char", c) for c in tok[2]]
                num_im, num_bl = render_math_tokens(num_tokens, is_script=True)
                den_im, den_bl = render_math_tokens(den_tokens, is_script=True)
                if num_im and den_im:
                    gap = max(2, int(font_px * 0.06))
                    bar_w = max(num_im.size[0], den_im.size[0]) + int(font_px * 0.15)
                    pad_x = max(2, int(font_px * 0.05))
                    W = bar_w + pad_x * 2
                    above = num_im.size[1] + gap
                    below = den_im.size[1] + gap
                    H = above + below + 2
                    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                    dr = ImageDraw.Draw(im)
                    nx = pad_x + (bar_w - num_im.size[0]) // 2
                    im.alpha_composite(num_im, (nx, above - num_im.size[1]))
                    yb = above
                    dr.line([(pad_x, yb), (pad_x + bar_w, yb)], fill=(0, 0, 0, 255), width=max(2, int(font_px * 0.06)))
                    dx = pad_x + (bar_w - den_im.size[0]) // 2
                    im.alpha_composite(den_im, (dx, yb + gap))
                    # FIX baseline: neo đáy phân số vào baseline CHỮ (theo font_px),
                    # KHÔNG theo % mẫu số -> nhất quán với chữ thường, không lệch cao/thấp.
                    axis = int(font_px * 0.30)          # thanh phân số cao hơn baseline chữ
                    bar_from_bottom = below + 2
                    frac_bl = max(int(font_px * 0.06), bar_from_bottom - axis)
                    parts.append((im, frac_bl))
            elif ttype == "sqrt":
                inner_tokens = [("char", c) for c in tok[1]]
                inner_im, bl = render_math_tokens(inner_tokens)
                if inner_im:
                    w, h = inner_im.size
                    pad = max(2, int(font_px * 0.04))
                    tick = max(3, int(font_px * 0.10))
                    W = w + tick + pad * 2
                    H = h + pad * 2
                    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                    im.alpha_composite(inner_im, (tick + pad, pad))
                    dr = ImageDraw.Draw(im)
                    # Draw sqrt symbol
                    y0 = pad + h
                    y1 = pad
                    x0 = tick + pad
                    x1 = 0
                    dr.line([(x0, y0), (x1, y0 - int(h * 0.3)), (max(1, x1+2), y1)], fill=(0, 0, 0, 255), width=max(2, int(font_px * 0.05)))
                    # Overline
                    dr.line([(tick + pad, pad), (tick + pad + w, pad)], fill=(0, 0, 0, 255), width=max(2, int(font_px * 0.04)))
                    parts.append((im, bl + pad))
            elif ttype == "overline":
                inner_tokens = [("char", c) for c in tok[1]]
                inner_im, bl = render_math_tokens(inner_tokens)
                if inner_im:
                    w, h = inner_im.size
                    bar_h = max(2, int(font_px * 0.04))
                    new_im = Image.new("RGBA", (w, h + bar_h + 2), (0, 0, 0, 0))
                    new_im.alpha_composite(inner_im, (0, bar_h + 2))
                    dr = ImageDraw.Draw(new_im)
                    dr.line([(0, 0), (w, 0)], fill=(0, 0, 0, 255), width=max(2, int(font_px * 0.04)))
                    parts.append((new_im, bl + bar_h + 2))
            elif ttype == "sup":
                inner_tokens = [("char", c) for c in tok[1]]
                inner_im, bl = render_math_tokens(inner_tokens, is_script=True)
                if inner_im:
                    parts.append((inner_im, bl))
            elif ttype == "sub":
                inner_tokens = [("char", c) for c in tok[1]]
                inner_im, bl = render_math_tokens(inner_tokens, is_script=True)
                if inner_im:
                    parts.append((inner_im, bl))

        if not parts:
            return None

        gap = max(int(font_px * 0.06), 2)
        bls = [b for _, b in parts]
        max_above = max(im.size[1] - b for (im, _), b in zip(parts, bls))
        max_below = max(bls)
        H = max_above + max_below + 2
        W = sum(im.size[0] for (im, _) in parts) + gap * (len(parts) - 1)
        canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        x = 0
        base_y = max_above
        for (im, _), b in zip(parts, bls):
            y = base_y - (im.size[1] - b)
            canvas.alpha_composite(im, (x, max(0, y)))
            x += im.size[0] + gap
        return canvas, max_below

    # Render math part (with arc bases replaced by {base})
    math_text = s
    for start, end, base in reversed(arc_bases):
        math_text = math_text[:start] + "{" + base + "}" + math_text[end:]

    math_tokens = tokenize_math(math_text)
    math_result = render_math_tokens(math_tokens)

    # Render arcs
    arc_ims = []
    for _, _, base in arc_bases:
        try:
            arc_png, aw, ah, awe, ahe, abf = render_arc_preview_png(base, font_pt=font_pt, scale=scale)[:6]
            aim = Image.open(io.BytesIO(arc_png)).convert("RGBA")
            arc_ims.append(aim)
        except Exception:
            pass

    if not arc_ims:
        return None

    # Composite: math parts + arc(s)
    parts_list = []
    if math_result:
        math_im, math_bl = math_result
        parts_list.append((math_im, math_bl))
    for aim in arc_ims:
        parts_list.append((aim, max(1, int(aim.size[1] * 0.08))))

    gap = max(int(font_px * 0.08), 3)
    bls = [b for _, b in parts_list]
    max_above = max(im.size[1] - b for (im, _), b in zip(parts_list, bls))
    max_below = max(bls)
    H = max_above + max_below + 2
    W = sum(im.size[0] for (im, _) in parts_list) + gap * (len(parts_list) - 1)
    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    x = 0
    base_y = max_above
    for (im, _), b in zip(parts_list, bls):
        y = base_y - (im.size[1] - b)
        canvas.alpha_composite(im, (x, max(0, y)))
        x += im.size[0] + gap

    bb = canvas.split()[-1].getbbox()
    if bb:
        pad = max(2, int(scale * 0.4))
        l, t, r, btm = bb
        canvas = canvas.crop((max(0, l - pad), max(0, t - pad), min(W, r + pad), min(H, btm + pad)))
        base_y_c = base_y - max(0, t - pad)
        Hc = canvas.size[1]
        below = max(0.0, Hc - float(base_y_c))
        bf = max(0.0, min(0.9, below / max(1.0, float(Hc))))
    else:
        bf = 0.22

    Wc, Hc = canvas.size
    if canvas.mode == "RGBA":
        bg = Image.new("RGB", canvas.size, (255, 255, 255))
        bg.paste(canvas, mask=canvas.split()[-1])
        out_im = bg
    else:
        out_im = canvas.convert("RGB")
    buf = io.BytesIO()
    out_im.save(buf, format="PNG")
    png = buf.getvalue()
    css_w = Wc / float(scale)
    css_h = Hc / float(scale)
    w_emu = max(1, int(round(css_w * 9525)))
    h_emu = max(1, int(round(css_h * 9525)))
    return png, Wc, Hc, w_emu, h_emu, bf


def render_arc_expression_png(latex: str, font_pt: float = 14.0, scale: int = 8):
    """Vẽ PNG cho công thức có 1 hoặc nhiều cung: overparen{A}+overparen{B}.

    Ghép ngang các cung MathType-like + toán tử (+, =, ...).
    Returns (png_bytes, w_px, h_px, w_emu, h_emu) hoặc None nếu không parse được.
    """
    import io
    from PIL import Image, ImageDraw, ImageFont

    if parse_arc_latex_expression is None:
        return None
    tokens = parse_arc_latex_expression(latex)
    if not tokens:
        return None

    # Một cung thuần → render_arc_preview_png
    if len(tokens) == 1 and tokens[0][0] == "arc":
        return render_arc_preview_png(tokens[0][1], font_pt=font_pt, scale=scale)  # 6-tuple

    parts = []  # list of RGBA images
    for kind, val in tokens:
        if kind == "arc":
            png, w, h, we, he, _bf = render_arc_preview_png(val, font_pt=font_pt, scale=scale)[:6]
            from PIL import Image as _Im
            import io as _io
            parts.append(_Im.open(_io.BytesIO(png)).convert("RGBA"))
        else:
            # operator / text
            op = (val or "").strip()
            if not op:
                continue
            # font size for op ~ same as letters
            px_per_pt = 96.0 / 72.0
            font_px = max(16, int(round(font_pt * px_per_pt * scale)))
            font = None
            for fp in (
                r"C:\Windows\Fonts\times.ttf",
                r"C:\Windows\Fonts\timesi.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            ):
                try:
                    font = ImageFont.truetype(fp, font_px)
                    break
                except Exception:
                    continue
            if font is None:
                font = ImageFont.load_default()
            tmp = Image.new("RGBA", (8, 8), (0, 0, 0, 0))
            td = ImageDraw.Draw(tmp)
            bb = td.textbbox((0, 0), op, font=font)
            tw, th = bb[2] - bb[0], bb[3] - bb[1]
            pad_x = max(int(font_px * 0.18), 4)
            pad_y = max(int(font_px * 0.08), 2)
            op_im = Image.new("RGBA", (tw + pad_x * 2, th + pad_y * 2), (0, 0, 0, 0))
            ImageDraw.Draw(op_im).text((pad_x - bb[0], pad_y - bb[1]), op, font=font, fill=(0, 0, 0, 255))
            parts.append(op_im)

    if not parts:
        return None

    # Align baselines: bottom-align all parts (letters sit on same baseline)
    gap = max(int(scale * 2), 4)
    max_h = max(p.size[1] for p in parts)
    total_w = sum(p.size[0] for p in parts) + gap * (len(parts) - 1)
    canvas = Image.new("RGBA", (total_w, max_h), (0, 0, 0, 0))
    x = 0
    for p in parts:
        y = max_h - p.size[1]  # bottom align
        # operators: raise slightly to optical center of letters
        canvas.alpha_composite(p, (x, y))
        x += p.size[0] + gap

    # Crop
    bb = canvas.split()[-1].getbbox()
    if bb:
        pad = max(2, int(scale * 0.5))
        l, t, r, b = bb
        l = max(0, l - pad); t = max(0, t - pad)
        r = min(canvas.size[0], r + pad); b = min(canvas.size[1], b + pad)
        canvas = canvas.crop((l, t, r, b))

    W, H = canvas.size
    buf = io.BytesIO()
    canvas.save(buf, format="PNG")
    png = buf.getvalue()
    css_w = W / float(scale)
    css_h = H / float(scale)
    w_emu = max(1, int(round(css_w * 9525)))
    h_emu = max(1, int(round(css_h * 9525)))
    return png, W, H, w_emu, h_emu, 0.10, 0.10




def render_mixed_formula_preview_png(
    math_png_bytes: bytes,
    arc_bases: list,
    font_pt: float = 14.0,
    scale: int = 8,
    math_size_emu: tuple | None = None,
):
    """Ghép PNG math (LO) + cung (Doc2-like) trên CÙNG baseline chữ.

    Dùng làm preview 1 OLE cho công thức lồng (frac/mũ + overparen), trông như
    MathType Doc3 (không lệch dòng như khi tách 2 OLE).

    math_size_emu: (w_emu, h_emu) của PNG/WMF math LO — dùng để scale EMU
    canvas ghép cho khớp kích thước thật trong Word.
    """
    import io
    from PIL import Image

    if not math_png_bytes:
        return None
    try:
        math_im = Image.open(io.BytesIO(math_png_bytes)).convert("RGBA")
    except Exception:
        return None

    # Ước lượng chiều cao "chữ thường" trong PNG math LO (ink height * ~0.45
    # cho công thức có phân số; floor theo font 14pt).
    m_bb = math_im.split()[-1].getbbox()
    if not m_bb:
        return None
    m_ink_h = max(1, m_bb[3] - m_bb[1])
    # Phân số LO: chữ cái ~ 40–55% ink height; công thức phẳng ~ 70–85%
    target_letter_h = max(int(14 * 96 / 72 * scale * 0.85), int(m_ink_h * 0.42))
    target_letter_h = min(target_letter_h, int(m_ink_h * 0.70))

    arc_ims = []
    for base in arc_bases or []:
        try:
            # Render cung ở scale cao rồi resize cho khớp letter height math
            png, w, h, we, he, bf = render_arc_preview_png(base, font_pt=font_pt, scale=max(scale, 8))[:6]
            aim = Image.open(io.BytesIO(png)).convert("RGBA")
            # Trong PNG cung, chữ chiếm ~ (H - arc_room); letter ~ 55–70% H
            a_bb = aim.split()[-1].getbbox() or (0, 0, aim.size[0], aim.size[1])
            a_h = max(1, a_bb[3] - a_bb[1])
            # letter height ≈ 0.62 * ink (phần dưới cung)
            a_letter = max(1, int(a_h * 0.62))
            ratio = float(target_letter_h) / float(a_letter)
            # Giới hạn scale hợp lý
            ratio = max(0.45, min(2.2, ratio))
            nw = max(1, int(round(aim.size[0] * ratio)))
            nh = max(1, int(round(aim.size[1] * ratio)))
            if (nw, nh) != aim.size:
                aim = aim.resize((nw, nh), Image.Resampling.LANCZOS)
            arc_ims.append(aim)
        except Exception:
            return None
    if not arc_ims:
        return None

    # Baseline: math LO ~ 28% từ đáy; cung ~ 6–10% từ đáy (chữ sát đáy)
    gap = max(int(target_letter_h * 0.12), 4)
    parts = [math_im] + arc_ims

    def _bl_from_bottom(im, is_arc=False):
        W, H = im.size
        if is_arc:
            return max(1, int(H * 0.08))
        return max(1, int(H * 0.28))

    bls = [_bl_from_bottom(parts[0], False)] + [_bl_from_bottom(p, True) for p in parts[1:]]
    max_above = max(p.size[1] - b for p, b in zip(parts, bls))
    max_below = max(bls)
    total_h = max_above + max_below + 2
    total_w = sum(p.size[0] for p in parts) + gap * (len(parts) - 1)
    canvas = Image.new("RGBA", (total_w, total_h), (0, 0, 0, 0))
    x = 0
    base_y = max_above
    for p, b in zip(parts, bls):
        y = base_y - (p.size[1] - b)
        canvas.alpha_composite(p, (x, max(0, y)))
        x += p.size[0] + gap

    bb = canvas.split()[-1].getbbox()
    if bb:
        pad = max(2, int(scale * 0.4))
        l, t, r, btm = bb
        l = max(0, l - pad); t = max(0, t - pad)
        r = min(canvas.size[0], r + pad); btm = min(canvas.size[1], btm + pad)
        canvas = canvas.crop((l, t, r, btm))
        base_y_c = base_y - t
        H = canvas.size[1]
        below = max(0.0, H - float(base_y_c))
        bf = max(0.0, min(0.9, below / max(1.0, float(H))))
    else:
        bf = 0.28

    W, H = canvas.size
    buf = io.BytesIO()
    canvas.save(buf, format="PNG")
    png = buf.getvalue()

    # EMU: scale theo kích thước math LO thật (tránh lệch pt khi LO PNG hi-res)
    if math_size_emu and math_im.size[1] > 0:
        mw_emu, mh_emu = math_size_emu
        px_per_emu_h = float(math_im.size[1]) / max(1.0, float(mh_emu))
        # canvas px → EMU cùng mật độ với math LO
        h_emu = max(1, int(round(H / max(px_per_emu_h, 1e-9))))
        w_emu = max(1, int(round(W / max(px_per_emu_h, 1e-9))))
    else:
        css_w = W / float(scale)
        css_h = H / float(scale)
        w_emu = max(1, int(round(css_w * 9525)))
        h_emu = max(1, int(round(css_h * 9525)))
    return png, W, H, w_emu, h_emu, bf



def enhance_arc_png_preview(png_bytes: bytes):
    """Crop lề thừa PNG LO (fallback). Prefer render_arc_preview_png cho pure arc.

    Returns (png_bytes, width_px, height_px).
    """
    try:
        import io
        from PIL import Image
        im = Image.open(io.BytesIO(png_bytes))
        rgba = im.convert("RGBA")
        alpha = rgba.split()[-1]
        bbox = alpha.getbbox()
        if not bbox:
            gray = rgba.convert("L")
            mask = gray.point(lambda p: 255 if p < 250 else 0)
            bbox = mask.getbbox()
        if not bbox:
            return png_bytes, 0, 0
        left, top, right, bottom = bbox
        w, h = rgba.size
        content_h = max(1, bottom - top)
        content_w = max(1, right - left)
        pad_top = max(1, int(content_h * 0.18))
        pad_bottom = max(1, int(content_h * 0.10))
        pad_x = max(1, int(content_w * 0.08))
        top2 = max(0, top - pad_top)
        bottom2 = min(h, bottom + pad_bottom)
        left2 = max(0, left - pad_x)
        right2 = min(w, right + pad_x)
        cropped = rgba.crop((left2, top2, right2, bottom2))
        buf = io.BytesIO()
        cropped.save(buf, format="PNG")
        cw, ch = cropped.size
        return buf.getvalue(), cw, ch
    except Exception:
        return png_bytes, 0, 0

def _m(tag: str) -> str:
    return f"{{{_M}}}{tag}"

def unwrap_math_paras(doc_root: etree._Element) -> None:
    """Unwrap <m:oMathPara>/<m:oMath> shells that only carry plain $latex$ runs.

    A prior reverse-conversion pass (MathType OLE -> $latex$ text) can leave the
    math shell in place while replacing its contents with a w:r holding "$...$".
    Those runs sit under m:oMathPara / m:oMath instead of directly under w:p, so
    the LaTeX isolator never sees them. Lift the runs up to the paragraph and drop
    the empty math shell so they convert like any other formula.
    """
    for math_el in list(doc_root.iter(_m("oMathPara"))) + list(doc_root.iter(_m("oMath"))):
        parent = math_el.getparent()
        if parent is None:
            continue
        # Only unwrap when there is no real OMML math left inside (no m:t nodes),
        # i.e. the shell just wraps plain w:r/w:t runs.
        if math_el.find(f".//{_m('t')}") is not None:
            continue
        runs = math_el.findall(_w("r"))
        if not runs:
            continue
        insert_at = list(parent).index(math_el)
        for r in runs:
            parent.insert(insert_at, r)
            insert_at += 1
        parent.remove(math_el)

_MATH_TOKEN_RE = re.compile(r'(?<!\\)\$\$(.*?)(?<!\\)\$\$|(?<!\\)\$(.*?)(?<!\\)\$', re.DOTALL)

def strip_empty_math(doc_root: etree._Element) -> None:
    """Remove empty '$$ $$' / '$ $' placeholders left by blank equation cells.

    Parses $...$ / $$...$$ tokens left-to-right (same alternation as the LaTeX
    isolator) and drops only tokens whose inner content is blank. This avoids
    matching the boundary between two adjacent formulas ('$$A$$ $$B$$'), which a
    naive '\\$\\$\\s*\\$\\$' regex would eat and thereby merge the two formulas.
    """
    def _repl(m: re.Match) -> str:
        content = m.group(1) if m.group(1) is not None else m.group(2)
        return "" if (content is None or not content.strip()) else m.group(0)

    for t in doc_root.iter(_w("t")):
        if t.text and "$" in t.text:
            new = _MATH_TOKEN_RE.sub(_repl, t.text)
            if new != t.text:
                t.text = new

def merge_cross_paragraph_math(doc_root: etree._Element) -> None:
    """Gộp nội dung $$...$$ bị AI tách ra nhiều <w:p> thành 1 run duy nhất.

    AI (Gemini, GPT...) hay sinh dạng:
        <w:p>$$</w:p>
        <w:p>\\begin{cases}...\\end{cases}</w:p>
        <w:p>$$</w:p>
    Hoặc:
        <w:p>$$\\begin{cases}</w:p>
        <w:p>...\\end{cases}$$</w:p>

    Kết quả: từng <w:p> chỉ chứa 1 nửa công thức → regex $$...$$ không match
    dù có re.DOTALL (vì text nằm ở các node XML khác nhau, không phải 1 chuỗi).
    Hàm này gom text của các paragraph liên tiếp cho đến khi số $$ cân bằng.
    Chỉ gộp khi phát hiện $$ lẻ — không đụng vào paragraph bình thường.
    """
    # Tìm phần tử cha chứa các <w:p> (thường là <w:body>)
    body = doc_root.find('.//' + _w('body'))
    if body is None:
        body = doc_root

    i = 0
    while i < len(body):
        p = body[i]
        if p.tag != _w('p'):
            i += 1
            continue

        # Lấy toàn bộ text trong paragraph này
        text = ''.join(t.text or '' for t in p.iter(_w('t')))
        if '$$' not in text:
            i += 1
            continue

        # Đếm $$ — nếu lẻ thì công thức đang bị mở chưa đóng
        if text.count('$$') % 2 == 0:
            i += 1
            continue

        # Tìm các paragraph tiếp theo để gộp cho đến khi $$ cân bằng
        combined_text = text
        paragraphs_to_remove = []
        j = i + 1
        while j < len(body):
            next_p = body[j]
            if next_p.tag != _w('p'):
                j += 1
                continue
            next_text = ''.join(t.text or '' for t in next_p.iter(_w('t')))
            combined_text = combined_text + ' ' + next_text
            paragraphs_to_remove.append(next_p)
            j += 1
            if combined_text.count('$$') % 2 == 0:
                break  # đã cân bằng

        if not paragraphs_to_remove:
            i += 1
            continue

        # Xoá toàn bộ text cũ trong các <w:t> của p
        for t in p.iter(_w('t')):
            t.text = ''

        # Ghi combined_text vào run đầu tiên (hoặc tạo run mới nếu không có)
        runs = p.findall(_w('r'))
        if runs:
            t_node = runs[0].find(_w('t'))
            if t_node is None:
                t_node = etree.SubElement(runs[0], _w('t'))
            t_node.text = combined_text
            t_node.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
        else:
            new_run = etree.SubElement(p, _w('r'))
            t_node = etree.SubElement(new_run, _w('t'))
            t_node.text = combined_text
            t_node.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')

        # Xoá các paragraph đã được gộp vào p
        for rp in paragraphs_to_remove:
            try:
                body.remove(rp)
            except Exception:
                pass

        # Không tăng i vì body đã co lại sau khi xoá
        # (paragraph hiện tại đã được xử lý xong, tiếp tục từ i+1)
        i += 1


def _is_plain_op_gap(s: str) -> bool:
    """True nếu đoạn latex giữa các cung chỉ là toán tử/khoảng trắng (chèn text, không OLE)."""
    if s is None:
        return True
    t = s.strip()
    if not t:
        return True
    # +, -, =, dấu câu, sd? no - sd is text letters need math or text
    return bool(re.fullmatch(r"[\s+\-*/=(),.;:\\]+", t))


def _make_text_run(text_value: str):
    """Run văn bản thường (Times 14) để chèn +, = giữa các OLE."""
    wr = etree.Element(_w("r"))
    rPr = etree.SubElement(wr, _w("rPr"))
    rFonts = etree.SubElement(rPr, _w("rFonts"))
    rFonts.set(_w("ascii"), "Times New Roman")
    rFonts.set(_w("hAnsi"), "Times New Roman")
    sz = etree.SubElement(rPr, _w("sz"))
    sz.set(_w("val"), "28")  # 14pt
    szCs = etree.SubElement(rPr, _w("szCs"))
    szCs.set(_w("val"), "28")
    t = etree.SubElement(wr, _w("t"))
    t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    plain = text_value or ""
    plain = plain.replace(r"\,", " ").replace(r"\;", " ").replace(r"\ ", " ")
    plain = plain.replace(r"\times", "\u00d7").replace(r"\cdot", "\u00b7")
    plain = re.sub(r"\\([=+\-*/(),.;:])", r"\1", plain)
    t.text = plain
    return wr


def _require_local_engine_license():
    """Kiểm tra bản quyền bắt buộc trước khi thực thi Local Engine MathType."""
    try:
        cur_dir = os.path.dirname(os.path.abspath(__file__))
        scripts_dir = os.path.dirname(cur_dir)
        if scripts_dir not in sys.path:
            sys.path.insert(0, scripts_dir)
        import license_manager
        ok, payload, err = license_manager.check_current_license()
        if not ok:
            print("\n" + "=" * 65)
            print("  ⛔  LỖI BẢN QUYỀN - LOCAL ENGINE MATHTYPE")
            print("=" * 65)
            print(f"  Lý do: {err}")
            print("  Vui lòng liên hệ Tác giả hoặc chạy LAY_MA_MAY.bat để nhận bản quyền.")
            print("=" * 65 + "\n")
            raise PermissionError(f"Local Engine MathType chưa kích hoạt bản quyền hợp lệ: {err}")
        return payload
    except ImportError:
        raise PermissionError("LỖI BẢN QUYỀN: Không tìm thấy module xác minh license_manager.py. Không được tách lẻ Local Engine.")


def convert_docx_latex_to_mathtype(input_path: str, output_path: str, template_path: str = None, use_libreoffice: bool = True, progress_callback=None) -> dict:
    """Process a docx file, convert LaTeX math formulas to MathType OLE and save a new file."""
    _require_local_engine_license()
    # Find XSLT converter (needed for MathML->OMML fallback parsing if ever used, but we default to direct OLE)
    xslt_file = find_mml2omml_xslt()
    xslt_tree = etree.parse(xslt_file)
    transform_mml_to_omml = etree.XSLT(xslt_tree)
    
    # Check if we should use template assets
    use_template = False
    template_bin_data = None
    template_wmf_data = None
    template_wmf_ext = ".wmf"
    
    if template_path and os.path.exists(template_path) and HAS_PYWIN32:
        try:
            with zipfile.ZipFile(template_path, "r") as ztemp:
                # Find the baseline bin
                ole_names = [n for n in ztemp.namelist() if "embeddings/oleObject" in n and n.endswith(".bin")]
                if ole_names:
                    template_bin_data = ztemp.read(ole_names[0])
                # Find the baseline wmf/emf image
                img_names = [n for n in ztemp.namelist() if "media/image" in n and (n.endswith(".wmf") or n.endswith(".emf"))]
                if img_names:
                    template_wmf_data = ztemp.read(img_names[0])
                    template_wmf_ext = os.path.splitext(img_names[0])[1]
                    
            if template_bin_data is not None and template_wmf_data is not None:
                use_template = True
                logger.info("Using template assets for MathType OLE binary patching.")
            else:
                logger.warning("Could not extract MathType assets from template. Falling back to auto-generated blank WMF.")
        except Exception as e:
            logger.error("Error reading template file: %s. Falling back to auto-generated blank WMF.", e)
            
    # Generate blank WMF if not using template
    if not use_template:
        template_wmf_data = make_placeable_blank_wmf()
        template_wmf_ext = ".wmf"
        logger.info("Using dynamically generated blank WMF presentation image.")
        
    # Read DOCX
    with zipfile.ZipFile(input_path, "r") as zin:
        names = set(zin.namelist())
        zdata = {n: zin.read(n) for n in names}
        
    doc_xml_path = "word/document.xml"
    rels_path = "word/_rels/document.xml.rels"
    ct_path = "[Content_Types].xml"
    
    doc_root = _parse_xml(zdata[doc_xml_path])
    rels_root = _parse_xml(zdata.get(rels_path, b'<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"/>'))
    ct_root = _parse_xml(zdata[ct_path])
    
    # Remove spell check markers and merge formatting runs
    clean_proof_errors(doc_root)
    # Lift $latex$ runs out of leftover math shells before merging/isolating
    unwrap_math_paras(doc_root)
    strip_empty_math(doc_root)
    # Gộp $$...$$ bị AI tách ra nhiều <w:p> (phải chạy trước merge_adjacent_runs)
    merge_cross_paragraph_math(doc_root)
    for p in doc_root.iter(_w("p")):
        merge_adjacent_runs(p)

    # Lint: warn about paragraphs with an odd number of unescaped '$' — those
    # hide a formula that will never be picked up by the paired-'$' regex below.
    dollar_warnings = lint_unbalanced_dollars(doc_root)
    for w in dollar_warnings:
        logger.warning("Unbalanced $ in source: %s", w)

    latex_pattern = re.compile(r'(?<!\\)\$\$(.*?)(?<!\\)\$\$|(?<!\\)\$(.*?)(?<!\\)\$', re.DOTALL)

    # Collect all paragraph nodes
    paragraphs = list(doc_root.iter(_w("p")))
    
    # Find all LaTeX runs
    latex_runs_data = []
    for p in paragraphs:
        matched_runs = isolate_latex_runs(p, latex_pattern)
        for run in matched_runs:
            latex_runs_data.append((p, run))
            
    total_formulas = len(latex_runs_data)
    logger.info("Found %d LaTeX formula(s) to convert", total_formulas)

    if HAS_PREPROCESSOR and total_formulas > 0:
        logger.info("Preprocessing %d LaTeX formula(s)...", total_formulas)
        for idx, (p, run) in enumerate(latex_runs_data, 1):
            t_node = run.find(_w("t"))
            if t_node is not None and t_node.text:
                full_text = t_node.text.strip()
                is_double = full_text.startswith("$$") and full_text.endswith("$$")
                is_single = full_text.startswith("$") and full_text.endswith("$")
                if is_double:
                    latex_formula = full_text[2:-2].strip()
                elif is_single:
                    latex_formula = full_text[1:-1].strip()
                else:
                    latex_formula = full_text.strip()
                try:
                    preprocessed = preprocess_latex(latex_formula)
                    if is_double:
                        t_node.text = f"$${preprocessed}$$"
                    elif is_single:
                        t_node.text = f"${preprocessed}$"
                    else:
                        t_node.text = preprocessed
                except Exception as e:
                    logger.error("Failed to preprocess LaTeX formula %d: %s", idx, e)
    
    # Try using LibreOffice to batch-render formulas to WMF
    lo_python = find_libreoffice_python()
    use_lo_render = False
    lo_wmf_images = {} # index -> bytes  (full formula, part_idx=None)
    lo_wmf_sizes = {} # index -> (width_emu, height_emu)
    lo_png_images = {} # index -> PNG preview bytes (Word displays this, not the OLE)
    lo_ole_binaries = {} # index -> bytes
    # Mixed-arc parts: (formula_idx, part_idx) -> data
    lo_part_wmf_images = {}
    lo_part_wmf_sizes = {}
    lo_part_png_images = {}
    lo_part_ole_binaries = {}
    temp_dir = None
    lo_part_keys = []  # parallel to formulas_to_render: (formula_idx, part_idx|None)
    
    if use_libreoffice and lo_python:
        logger.info("LibreOffice Python interpreter found at %s. Attempting to render formula WMF images.", lo_python)
        formulas_to_render = []
        formula_mapping = [] # maps render index to run index (1-based)
        
        for idx, (p, run) in enumerate(latex_runs_data, 1):
            t_node = run.find(_w("t"))
            if t_node is None or not t_node.text:
                continue
                
            full_text = t_node.text.strip()
            if full_text.startswith("$$") and full_text.endswith("$$"):
                latex_formula = full_text[2:-2].strip()
            elif full_text.startswith("$") and full_text.endswith("$"):
                latex_formula = full_text[1:-1].strip()
            else:
                latex_formula = full_text.strip()
                
            if not latex_formula:
                continue
                
            try:
                # Pure arc / multi pure arcs: skip LO (Doc3/MTEF riêng).
                # Mixed overparen: VẪN render LO để có fallback nếu Doc3 fail.
                if extract_pure_arc_base is not None:
                    try:
                        if extract_pure_arc_base(latex_formula):
                            continue
                    except Exception:
                        pass
                if parse_arc_latex_expression is not None:
                    try:
                        _tok = parse_arc_latex_expression(latex_formula)
                        if (
                            _tok
                            and any(k == "arc" for k, _ in _tok)
                            and all(
                                k == "arc" or (k == "op" and _is_plain_op_gap(v))
                                for k, v in _tok
                            )
                        ):
                            continue
                    except Exception:
                        pass

                # Mixed: 1 OLE full (overline+LRM → tvFROWN) + PNG math-only để ghép preview
                # (preview ghép cung Doc2-like → cùng baseline như Doc3, không tách OLE)
                _parts = None
                if split_latex_by_arcs is not None and is_arc_containing_latex is not None:
                    try:
                        if is_arc_containing_latex(latex_formula):
                            _parts = split_latex_by_arcs(latex_formula)
                    except Exception:
                        _parts = None

                # Full formula luôn render (OLE + fallback preview)
                # [PATCH] Inline normalization — đảm bảo sửa lỗi ngay cả khi
                # latex_to_starmath.py chưa được cập nhật đúng.
                starmath = latex_to_starmath.convert(latex_formula)
                formulas_to_render.append(starmath)
                # DEBUG: log StarMath for formulas with known problem symbols
                if any(k in latex_formula for k in ('textdegree', 'perp', 'lvert', 'rvert', 'left|', 'right|')):
                    logger.info("DEBUG StarMath F%d: %s", idx, starmath[:200])
                formula_mapping.append(idx)
                lo_part_keys.append((idx, None))

                # Thêm math-only (không overparen) để ghép PNG cung đẹp
                if _parts and any(k == "arc" for k, _ in _parts) and any(k == "math" for k, _ in _parts):
                    for p_i, (kind, val) in enumerate(_parts):
                        if kind != "math":
                            continue
                        math_tex = (val or "").strip()
                        if not math_tex or _is_plain_op_gap(math_tex):
                            continue
                        try:
                            sm_part = latex_to_starmath.convert(math_tex)
                        except Exception as e:
                            logger.error(
                                "StarMath failed for mixed part %d.%d: %s", idx, p_i, e
                            )
                            continue
                        formulas_to_render.append(sm_part)
                        formula_mapping.append(idx)
                        lo_part_keys.append((idx, p_i))
            except Exception as e:
                logger.error("Failed to convert LaTeX to StarMath for formula %d: %s", idx, e)
        if formulas_to_render:
            try:
                temp_dir = tempfile.mkdtemp(prefix="lo_render_")
                config = {
                    "formulas": formulas_to_render,
                    "output_dir": temp_dir,
                    "host": "localhost",
                    "port": 2002
                }
                config_path = os.path.join(temp_dir, "config.json")
                with open(config_path, "w", encoding="utf-8") as f:
                    json.dump(config, f, ensure_ascii=False)
                    
                # Run the helper renderer
                renderer_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "libreoffice_renderer.py")
                logger.info("Launching LibreOffice batch renderer helper script...")
                res_proc = subprocess.run(
                    [lo_python, "-u", renderer_script, config_path],
                    capture_output=True, text=True
                )
                
                # Check results
                result_path = os.path.join(temp_dir, "results.json")
                if os.path.exists(result_path):
                    with open(result_path, "r", encoding="utf-8") as f:
                        results_data = json.load(f)
                        
                    for r in results_data:
                        r_idx = r.get("index")
                        orig_idx = formula_mapping[r_idx]
                        part_key = lo_part_keys[r_idx] if r_idx < len(lo_part_keys) else (orig_idx, None)
                        part_idx = part_key[1] if isinstance(part_key, tuple) else None
                        if r.get("success"):
                            if "wmf_path" in r:
                                wmf_path = r["wmf_path"]
                                if os.path.exists(wmf_path):
                                    with open(wmf_path, "rb") as f:
                                        _wmf_b = f.read()
                                    w_emu, h_emu = get_wmf_size_emu(wmf_path)
                                    if part_idx is None:
                                        lo_wmf_images[orig_idx] = _wmf_b
                                        lo_wmf_sizes[orig_idx] = (w_emu, h_emu)
                                    else:
                                        lo_part_wmf_images[(orig_idx, part_idx)] = _wmf_b
                                        lo_part_wmf_sizes[(orig_idx, part_idx)] = (w_emu, h_emu)
                                    logger.info(
                                        "Successfully rendered WMF for formula %d part %s: %d x %d EMU",
                                        orig_idx, part_idx, w_emu, h_emu,
                                    )
                            if "png_path" in r:
                                png_path = r["png_path"]
                                if os.path.exists(png_path):
                                    with open(png_path, "rb") as f:
                                        _png_b = f.read()
                                    if part_idx is None:
                                        lo_png_images[orig_idx] = _png_b
                                    else:
                                        lo_part_png_images[(orig_idx, part_idx)] = _png_b
                            if "bin_path" in r:
                                bin_path = r["bin_path"]
                                if os.path.exists(bin_path):
                                    with open(bin_path, "rb") as f:
                                        _bin_b = f.read()
                                    if part_idx is None:
                                        lo_ole_binaries[orig_idx] = _bin_b
                                    else:
                                        lo_part_ole_binaries[(orig_idx, part_idx)] = _bin_b
                                    logger.info(
                                        "Successfully extracted OLE binary for formula %d part %s",
                                        orig_idx, part_idx,
                                    )
                    use_lo_render = True
                else:
                    logger.error("LibreOffice renderer failed to output results.json. Stderr: %s", res_proc.stderr)
            except Exception as e:
                logger.error("Error during LibreOffice batch rendering: %s", e)
                
    converted = 0
    errors = 0
    
    # Track existing rIds to prevent collision
    existing_ids = {child.get("Id") for child in rels_root if child.get("Id")}
    
    def _new_rel_id() -> str:
        i = 1
        while f"rIdOle{i}" in existing_ids:
            i += 1
        rid = f"rIdOle{i}"
        existing_ids.add(rid)
        return rid
        
    ole_index = 1
    while f"word/embeddings/oleObject{ole_index}.bin" in names:
        ole_index += 1
        
    image_index = 1
    image_exts = (".wmf", ".emf", ".png", ".jpeg", ".jpg", ".gif")
    while any(f"word/media/image{image_index}{ext}" in names for ext in image_exts):
        image_index += 1
        
    for idx, (p, run) in enumerate(latex_runs_data, 1):
        t_node = run.find(_w("t"))
        if t_node is None or not t_node.text:
            continue
            
        full_text = t_node.text.strip()
        if full_text.startswith("$$") and full_text.endswith("$$"):
            latex_formula = full_text[2:-2].strip()
        elif full_text.startswith("$") and full_text.endswith("$"):
            latex_formula = full_text[1:-1].strip()
        else:
            latex_formula = full_text.strip()
            
        if not latex_formula:
            continue
            
        try:
            # 0. Chuẩn hoá cú pháp AI hay sinh nhưng latex2mathml không hiểu:
            #    \vert{} → \vert  (AI dùng {} rỗng để tách token, không phải argument)
            latex_formula = re.sub(
                r'\\(vert|lvert|rvert|Vert|lVert|rVert)\{\}',
                r'\\\1', latex_formula
            )

            # ═══ Doc3 FIRST: overparen → 1 OLE MTEF v5 (giống Doc3) ═══
            # QUAN TRỌNG: chỉ remove run SAU KHI new_run đã dựng xong.
            # Fail → _doc3_done=False, đi pipeline thường (KHÔNG xóa công thức).
            _doc3_done = False
            _has_arc = False
            # Góc (\widehat) ≠ cung (\overparen)
            _has_angle_hat = bool(re.search(r'\\widehat\s*\{', latex_formula or ''))
            try:
                if extract_pure_arc_base is not None and extract_pure_arc_base(latex_formula):
                    _has_arc = True
                elif is_arc_containing_latex is not None and is_arc_containing_latex(latex_formula):
                    _has_arc = True
                elif re.search(r'\\(?:overparen|wideparen|overarc|overgroup)\s*\{', latex_formula or ''):
                    _has_arc = True
            except Exception:
                _has_arc = bool(re.search(r'\\(?:overparen|wideparen|overarc)', latex_formula or ''))

            # Arc pure HOẶC góc \widehat trong scope → MTEF MathType native (Doc3-like)
            if (_has_arc or _has_angle_hat):
                try:
                    if idx in lo_ole_binaries:
                        _doc3_native = lo_ole_binaries[idx]
                    elif build_geometry_formula_native is not None:
                        _doc3_native = build_geometry_formula_native(latex_formula)
                    else:
                        raise RuntimeError("No LO bin and no builder available")
                        
                    if not _doc3_native:
                        raise RuntimeError("builder returned None for this latex")

                    ole_bin = make_mathtype_ole(_doc3_native)
                    if not ole_bin or len(ole_bin) < 512:
                        raise RuntimeError("OLE bin too small/invalid")

                    prev = None
                    _png = None
                    _we = _he = None
                    bf = 0.22
                    _pos_hp_preview = None
                    try:
                        # 1) Góc \widehat: ưu tiên preview LO (PNG/WMF) — đủ cỡ, không bị placeholder nhỏ
                        if _has_angle_hat and not _has_arc:
                            if idx in lo_png_images:
                                _png = lo_png_images[idx]
                                _we, _he = lo_wmf_sizes.get(idx, (0, 0))
                                if (not _we or not _he) and idx in lo_wmf_images:
                                    _we, _he = lo_wmf_sizes.get(idx, (0, 0))
                            elif idx in lo_wmf_images:
                                _png = lo_wmf_images[idx]
                                _we, _he = lo_wmf_sizes.get(idx, (0, 0))
                            if _png and _we and _he and _we >= 1000 and _he >= 1000:
                                prev = "lo"
                        # 2) Pure arc: PNG bezier
                        if prev is None:
                            _pb = extract_pure_arc_base(latex_formula) if extract_pure_arc_base else None
                            if _pb:
                                prev = render_arc_preview_png(_pb, font_pt=14.0, scale=8)
                        # 3) Geometry PIL (mixed arc formulas)
                        if prev is None or prev == "lo" and _png is None:
                            if prev != "lo":
                                prev = render_geometry_formula_preview_png(
                                    latex_formula, font_pt=14.0, scale=8
                                )
                    except Exception as _pe:
                        logger.warning("Doc3 preview error: %s", _pe)
                        if prev != "lo":
                            prev = None

                    if prev == "lo":
                        # already have _png/_we/_he from LO
                        pass
                    elif prev is not None:
                        _png = prev[0]
                        _we = int(prev[3])
                        _he = int(prev[4])
                        bf = float(prev[5]) if len(prev) > 5 and prev[5] is not None else 0.22
                        _pos_hp_preview = int(prev[6]) if len(prev) > 6 and prev[6] is not None else None
                    else:
                        # Fallback cuối: pure widehat vẽ PIL cỡ chữ 14pt (không còn 240x48 nhỏ xíu)
                        from PIL import Image as _PILImage, ImageDraw as _PILDraw, ImageFont as _PILFont
                        import io as _io
                        _mhat = re.search(r'\\widehat\s*\{([A-Za-z0-9]+)\}', latex_formula or '')
                        _label = _mhat.group(1) if _mhat else (latex_formula or '?')[:12]
                        _fp = 112  # ~14pt * 8 scale
                        try:
                            _fnt = _PILFont.truetype(
                                r"C:\Windows\Fonts\timesi.ttf", _fp
                            )
                        except Exception:
                            try:
                                _fnt = _PILFont.truetype(
                                    "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", _fp
                                )
                            except Exception:
                                _fnt = _PILFont.load_default()
                        _tmp = _PILImage.new("RGB", (8, 8), (255, 255, 255))
                        _td = _PILDraw.Draw(_tmp)
                        _bb = _td.textbbox((0, 0), _label, font=_fnt)
                        _tw, _th = _bb[2] - _bb[0], _bb[3] - _bb[1]
                        _hat_h = max(8, _fp // 5)
                        _pad = max(8, _fp // 8)
                        _W = _tw + 2 * _pad
                        _H = _th + _hat_h + 2 * _pad
                        _img = _PILImage.new("RGB", (_W, _H), (255, 255, 255))
                        _dr = _PILDraw.Draw(_img)
                        _dr.text((_pad - _bb[0], _pad + _hat_h - _bb[1]), _label, font=_fnt, fill=(0, 0, 0))
                        # mũ góc ^ đơn giản trên chữ
                        _x0, _x1 = _pad, _pad + _tw
                        _y_top = _pad + max(2, _hat_h // 4)
                        _y_peak = _pad
                        _pts = []
                        for _ii in range(25):
                            _tt = _ii / 24.0
                            _xx = _x0 + (_x1 - _x0) * _tt
                            _yy = _y_peak + (_y_top - _y_peak) * (2 * _tt - 1) ** 2
                            _pts.append((_xx, _yy))
                        _dr.line(_pts, fill=(0, 0, 0), width=max(2, _fp // 28))
                        _buf = _io.BytesIO()
                        _img.save(_buf, format="PNG")
                        _png = _buf.getvalue()
                        # px -> EMU (96dpi)
                        _we = int(_W * 914400 / 96)
                        _he = int(_H * 914400 / 96)
                        bf = 0.22
                        prev = "pil-hat"

                    if not _png or not _we or not _he or _we < 1000 or _he < 1000:
                        raise RuntimeError(f"preview size invalid: {_we}x{_he}")

                    # Chuẩn bị toàn bộ artifact TRƯỚC khi đụng XML run
                    _next_ole = ole_index
                    _next_img = image_index
                    while any(
                        f"word/media/image{_next_img}{ext}" in zdata
                        for ext in (".png", ".wmf", ".emf", ".jpg", ".jpeg")
                    ):
                        _next_img += 1
                    bin_name = f"word/embeddings/oleObject{_next_ole}.bin"
                    img_name = f"word/media/image{_next_img}.png"
                    rel_id = _new_rel_id()
                    img_rel_id = _new_rel_id()
                    shape_id = f"_x0000_i{1024 + idx}"
                    obj_id = "{" + str(uuid.uuid4()).upper() + "}"
                    if isinstance(prev, (tuple, list)) and len(prev) > 6 and prev[6] is not None:
                        _pos_hp = int(prev[6])
                    else:
                        _pos_hp = None
                        # Góc/frac: hạ baseline giống normal path
                        _tex_l = (latex_formula or "").lower()
                        if any(k in _tex_l for k in (r"\frac", r"\dfrac", r"\tfrac")):
                            _pos_hp = -24
                        elif r"\widehat" in (latex_formula or "") or r"\hat" in _tex_l:
                            _pos_hp = -8
                    new_run = _make_direct_ole_xml(
                        rel_id=rel_id,
                        image_rel_id=img_rel_id,
                        shape_id=shape_id,
                        obj_id=obj_id,
                        width_emu=_we,
                        height_emu=_he,
                        baseline_frac=bf,
                        position_half_pt=_pos_hp,
                    )
                    parent = run.getparent()
                    if parent is None:
                        raise RuntimeError("run has no parent")
                    run_idx = list(parent).index(run)

                    # Commit: ghi file + quan hệ + thay run (atomic về mặt logic)
                    zdata[bin_name] = ole_bin
                    zdata[img_name] = _png
                    _add_relationship(
                        rels_root, rel_id, _REL_OLEOBJECT,
                        f"embeddings/oleObject{_next_ole}.bin",
                    )
                    _ensure_content_type(
                        ct_root, f"/{bin_name}",
                        "application/vnd.openxmlformats-officedocument.oleObject",
                    )
                    _add_relationship(
                        rels_root, img_rel_id, _REL_IMAGE,
                        f"media/image{_next_img}.png",
                    )
                    _ensure_content_type(ct_root, f"/{img_name}", "image/png")
                    parent.remove(run)
                    parent.insert(run_idx, new_run)
                    ole_index = _next_ole + 1
                    image_index = _next_img + 1
                    converted += 1
                    _doc3_done = True
                    logger.info(
                        "Formula %d: Doc3 FIRST OK (%s, %d bytes): %s",
                        idx,
                        "angle-hat" if _has_angle_hat and not _has_arc else ("arc" if _has_arc else "geometry"),
                        len(_doc3_native),
                        latex_formula[:60],
                    )
                except Exception as _e:
                    # KHÔNG xóa run, KHÔNG skip pipeline — để fallback LO/omml
                    logger.warning(
                        "Doc3 FIRST failed, fallback normal path: %s | %s",
                        latex_formula[:60], _e,
                    )
                    _doc3_done = False

            if _doc3_done:
                if progress_callback:
                    progress_callback(idx, total_formulas, latex_formula)
                continue

            # 1. Convert LaTeX to MathML
            # Chỉ bỏ qua MathML full khi PURE arc (sẽ build MTEF MathType riêng).
            # Mixed formula: vẫn thử MathML (fallback); LO bin ưu tiên hơn.
            _early_pure_arc = False
            if extract_pure_arc_base is not None:
                try:
                    _early_pure_arc = extract_pure_arc_base(latex_formula) is not None
                except Exception:
                    _early_pure_arc = False

            mtef_bytes = None
            mathml_el = None
            if not _early_pure_arc:
                try:
                    # latex2mathml không hiểu \overparen → map tạm sang \overline
                    _mml_latex = re.sub(
                        r'\\(?:overparen|wideparen|overarc)\s*\{([^{}]*)\}',
                        r'\\overline{\1}',
                        latex_formula,
                    )
                    mathml_str = latex2mathml.converter.convert(_mml_latex)
                except Exception as e:
                    if HAS_PREPROCESSOR:
                        logger.info("latex2mathml failed for formula %d, trying Pandoc fallback...", idx)
                        mathml_str = latex_to_mathml_pandoc(latex_formula)
                        if not mathml_str:
                            raise e
                    else:
                        raise e
                # Post-process: latex2mathml maps \setminus to U+29F5 → U+2216
                mathml_str = mathml_str.replace('\u29F5', '\u2216')
                mathml_str = mathml_str.replace('&#x029F5;', '&#x02216;')
                parser = etree.XMLParser(remove_blank_text=True)
                mathml_el = etree.fromstring(mathml_str, parser)
                mtef_bytes = omml_converter.mathml_to_mtef_bytes(mathml_el)
            
            # 3. Generate OLE bin bytes
            #
            # ┌──────────────────────────────────────────────────────────────┐
            # │ 🔒 LOCKED — KHÔNG ĐẢO NGƯỢC THỨ TỰ ƯU TIÊN NÀY                │
            # │                                                                │
            # │ Đã xác nhận (user kích đúp 111_fixC5.docx): MTEF do            │
            # │ omml_converter TỰ ENCODE từ MathML mở ra TRẮNG trong MathType. │
            # │ Bin do LibreOffice trích là Equation Native SINH TỪ CHÍNH      │
            # │ ENGINE Equation thật (StarMath -> đối tượng Equation) và       │
            # │ MathType đọc ĐÚNG.                                             │
            # │                                                                │
            # │ BẤT BIẾN: object SỬA phải ƯU TIÊN bin LibreOffice; omml v5     │
            # │ CHỈ là fallback khi KHÔNG có bin LibreOffice. Đảo lại =        │
            # │ tái phát lỗi "mở MathType ra rỗng". Xem verify_mathtype_lock.py │
            # │ và memory mathtype_empty_editor_bug.                           │
            # └──────────────────────────────────────────────────────────────┘
            ole_bin = None
            # Pure arc / multi pure arcs: bỏ qua block locked (build MTEF MathType riêng).
            # Mixed: GIỮ full LO bin (1 OLE như Doc3) + preview ghép cung.
            _skip_locked_ole = False
            if extract_pure_arc_base is not None:
                try:
                    _skip_locked_ole = extract_pure_arc_base(latex_formula) is not None
                except Exception:
                    pass
            if (not _skip_locked_ole) and parse_arc_latex_expression is not None:
                try:
                    _tok = parse_arc_latex_expression(latex_formula)
                    if (
                        _tok
                        and any(k == "arc" for k, _ in _tok)
                        and all(
                            k == "arc" or (k == "op" and _is_plain_op_gap(v))
                            for k, v in _tok
                        )
                    ):
                        _skip_locked_ole = True
                except Exception:
                    pass

            if not _skip_locked_ole:
                try:
                    from omml_to_mtef import latex_to_mathtype_ole_offline
                    ole_bin = latex_to_mathtype_ole_offline(latex_formula)
                except Exception:
                    if idx in lo_ole_binaries:
                        _lo_b = lo_ole_binaries[idx]
                        ole_bin = _lo_b if _lo_b.startswith(b'\xd0\xcf\x11\xe0') else make_mathtype_ole(_lo_b)
                    else:
                        native_stream = make_equation_native_stream(mtef_bytes)
                        ole_bin = make_mathtype_ole(native_stream)
            # 🔒 END LOCKED (priority: LibreOffice bin trước, omml fallback sau)

            # ── Cung tròn v10 ──────────────────────────────────────────────
            # Pure arc: MTEF MathType thật + PNG Doc2-like (1 OLE).
            # Mixed (widehat/frac + overparen): 1 OLE full như Doc3
            #   - OLE = LO full (overline+LRM → patch tvFROWN) — MathType mở được
            #   - Preview = ghép PNG math-only + cung Doc2-like (cùng baseline)
            #   → không lệch dòng như khi tách 2 OLE
            _pure = None
            if extract_pure_arc_base is not None:
                try:
                    _pure = extract_pure_arc_base(latex_formula)
                except Exception:
                    _pure = None

            # multi pure arcs only: A+B
            _multi_pure = None
            if _pure is None and parse_arc_latex_expression is not None:
                try:
                    _tok = parse_arc_latex_expression(latex_formula)
                    if _tok and any(k == "arc" for k, _ in _tok):
                        if all(k == "arc" or (k == "op" and _is_plain_op_gap(v)) for k, v in _tok):
                            _multi_pure = _tok
                except Exception:
                    _multi_pure = None

            # Mixed: math + arc(s) xen kẽ
            _mixed_parts = None
            if (
                _pure is None
                and _multi_pure is None
                and split_latex_by_arcs is not None
                and is_arc_containing_latex is not None
            ):
                try:
                    if is_arc_containing_latex(latex_formula):
                        _sp = split_latex_by_arcs(latex_formula)
                        if (
                            _sp
                            and any(k == "arc" for k, _ in _sp)
                            and any(k == "math" for k, _ in _sp)
                        ):
                            _mixed_parts = _sp
                except Exception:
                    _mixed_parts = None

            def _emit_ole_run(ole_bytes, img_bytes, img_ext, w_e, h_e, bf=0.28, pos_hp=None, shape_suffix=0):
                """Ghi OLE+preview vào docx, trả về w:r element."""
                nonlocal ole_index, image_index
                bin_name = f"word/embeddings/oleObject{ole_index}.bin"
                zdata[bin_name] = ole_bytes
                this_ole = ole_index
                ole_index += 1
                rel_id = _new_rel_id()
                _add_relationship(
                    rels_root, rel_id, _REL_OLEOBJECT, f"embeddings/oleObject{this_ole}.bin"
                )
                _ensure_content_type(
                    ct_root, f"/{bin_name}",
                    "application/vnd.openxmlformats-officedocument.oleObject",
                )

                saved_img_index = image_index
                while any(
                    f"word/media/image{saved_img_index}{ext}" in zdata
                    for ext in (".png", ".wmf", ".emf", ".jpg", ".jpeg")
                ):
                    saved_img_index += 1
                image_index = saved_img_index + 1
                img_name = f"word/media/image{saved_img_index}{img_ext}"
                zdata[img_name] = img_bytes
                img_rel_id = _new_rel_id()
                _add_relationship(
                    rels_root, img_rel_id, _REL_IMAGE,
                    f"media/image{saved_img_index}{img_ext}",
                )
                _img_ct = {".wmf": "image/x-wmf", ".emf": "image/x-emf", ".png": "image/png"}
                _ensure_content_type(ct_root, f"/{img_name}", _img_ct.get(img_ext, "image/x-wmf"))

                shape_id = f"_x0000_i{1024 + idx * 20 + shape_suffix}"
                obj_id = "{" + str(uuid.uuid4()).upper() + "}"
                return _make_direct_ole_xml(
                    rel_id=rel_id,
                    image_rel_id=img_rel_id,
                    shape_id=shape_id,
                    obj_id=obj_id,
                    width_emu=w_e,
                    height_emu=h_e,
                    baseline_frac=bf,
                    position_half_pt=pos_hp,
                )

            def _calc_math_bf(math_tex: str, height_emu: int = 0) -> float:
                h_pt = height_emu / 12700.0 if height_emu > 0 else 15.6
                tex = (math_tex or "").lower()
                has_frac = any(k in tex for k in ("\\frac", "\\dfrac", "\\cfrac"))
                has_hat = any(k in tex for k in ("\\widehat", "\\hat", "\\overbrace", "\\vec", "\\overline"))
                has_sub_sup = ("_" in tex or "^" in tex)

                if has_frac or has_hat:
                    target_offset_pt = 5.5  # 11 half-pt lowering
                elif has_sub_sup:
                    target_offset_pt = 5.0  # 10 half-pt lowering
                else:
                    target_offset_pt = 4.5  # 9 half-pt lowering

                bf = target_offset_pt / max(1.0, h_pt)
                return max(0.15, min(0.45, bf))

            # Alignment profile v6 — tất cả giá trị là half-point.
            # QUAN TRỌNG: phân số đã được người dùng duyệt, tuyệt đối không thay đổi.
            _ALIGN_FRACTION_LOCKED = -24
            _ALIGN_LARGE_OPERATOR = -22
            _ALIGN_ACCENT = -8
            _ALIGN_ROOT = -7
            _ALIGN_SCRIPT = -7
            _ALIGN_PLAIN = -5

            def _baseline_offset_by_structure(math_tex: str, height_emu: int = 0) -> tuple[str, int]:
                """Chọn mốc căn theo cấu trúc LaTex, không phụ thuộc crop preview."""
                tex = (math_tex or '').lower().replace(' ', '')
                frac_cmds = (r'\frac', r'\dfrac', r'\tfrac', r'\cfrac')
                accent_cmds = (
                    r'\vec', r'\overline', r'\underline', r'\hat',
                    r'\widehat', r'\tilde', r'\widetilde', r'\bar',
                    r'\overparen', r'\wideparen', r'\overarc', r'\overset',
                )
                root_cmds = (r'\sqrt', r'\nroot')
                large_ops = (r'\int', r'\iint', r'\iiint', r'\oint',
                             r'\sum', r'\prod', r'\lim')

                # 1. PHÂN SỐ — khóa ở -24: thanh ngang là chuẩn căn dòng.
                if any(cmd in tex for cmd in frac_cmds):
                    return 'fraction_locked', _ALIGN_FRACTION_LOCKED
                # 2. TÍCH PHÂN/TỔNG/LIMIT: tách thành hai trường hợp theo chiều cao
                # thật của OLE. Tích phân gọn một dòng (Câu 1 B/D) không thể dùng
                # cùng offset với tích phân cận cao (Câu 2, Câu 16).
                if any(cmd in tex for cmd in large_ops):
                    height_pt = (height_emu / 12700.0) if height_emu else 0.0
                    if height_pt and height_pt < 27.0:
                        return 'compact_large_operator', -8
                    return 'tall_large_operator', _ALIGN_LARGE_OPERATOR
                # 3. DẤU TRÊN ĐẦU — overline/vector/cung/mũ phải căn theo đáy chữ cơ sở.
                if any(cmd in tex for cmd in accent_cmds):
                    return 'accent', _ALIGN_ACCENT
                # 4. CĂN — căn theo phần chữ dưới dấu căn.
                if any(cmd in tex for cmd in root_cmds):
                    return 'root', _ALIGN_ROOT
                # 5. MŨ/CHỈ SỐ — căn theo ký tự cơ sở.
                if '^' in tex or '_' in tex or 'rsup' in tex or 'rsub' in tex:
                    return 'script', _ALIGN_SCRIPT
                # 6. CHỮ/SỐ/HÀM THƯỜNG.
                return 'plain', _ALIGN_PLAIN

            def _anchor_position_from_preview(img_bytes, img_ext, math_tex, height_emu):
                """Tính w:position theo MỐC BÊN TRONG preview, không theo chiều cao ảnh.

                - Công thức có chữ/ký hiệu đầu tiên: lấy đáy mực của vùng đầu công thức
                  (vd. AĈB, S, l, x, =...) làm baseline.
                - Công thức BẮT ĐẦU bằng \\frac: lấy thanh ngang phân số làm mốc.
                Trả None nếu không đọc được PNG, để caller dùng fallback an toàn.
                """
                if (img_ext or '').lower() != '.png' or not img_bytes or height_emu <= 0:
                    return None
                try:
                    from PIL import Image
                    import io as _anchor_io
                    im = Image.open(_anchor_io.BytesIO(img_bytes)).convert('L')
                    W, H = im.size
                    if W < 8 or H < 8:
                        return None
                    px = im.load()
                    # Binarize: preview MathType/LibreOffice là nền trắng, mực đen.
                    ink = [[px[x, y] < 160 for x in range(W)] for y in range(H)]

                    def _first_glyph_bottom(x_start: int = 0, x_stop: int | None = None):
                        """Đáy thành phần nét mực đầu tiên, bỏ hẳn mũ/chỉ số rời."""
                        x_stop = min(W, x_stop if x_stop is not None else W)
                        # Quét theo cột để lấy glyph đầu tiên, rồi flood-fill 8 hướng.
                        seed = None
                        for xx in range(max(0, x_start), x_stop):
                            for yy in range(H):
                                if ink[yy][xx]:
                                    seed = (xx, yy)
                                    break
                            if seed is not None:
                                break
                        if seed is None:
                            return None
                        stack = [seed]
                        seen = {seed}
                        bottom = seed[1]
                        area = 0
                        while stack:
                            x, y = stack.pop()
                            area += 1
                            bottom = max(bottom, y)
                            for dy in (-1, 0, 1):
                                for dx in (-1, 0, 1):
                                    if dx == 0 and dy == 0:
                                        continue
                                    nx, ny = x + dx, y + dy
                                    if (0 <= nx < W and 0 <= ny < H and ink[ny][nx]
                                            and (nx, ny) not in seen):
                                        seen.add((nx, ny))
                                        stack.append((nx, ny))
                        return bottom if area >= 4 else None

                    tex = (math_tex or '').strip().strip('$').strip()
                    # QUY TẮC CĂN DÒNG CHUNG:
                    # - Hễ công thức CÓ phân số, lấy thanh ngang của phân số đầu tiên làm mốc.
                    #   Không chỉ áp dụng khi \frac đứng đầu: ví dụ ``d: (x-3)/2 = ...``
                    #   vẫn phải căn thanh phân số với dòng văn bản để cả cụm không bị đội lên.
                    # - Nếu không có phân số, lấy đáy mực của ký tự/ký hiệu đầu tiên làm mốc.
                    # Bỏ các lệnh style đầu công thức trước khi nhận diện.
                    for _style in ('\\displaystyle', '\\textstyle', '\\small'):
                        if tex.startswith(_style):
                            tex = tex[len(_style):].lstrip()
                    # Phân số đã được duyệt riêng bằng thanh ngang, nên không đo lại ở đây.
                    # Với các công thức khác, dùng baseline của phần nội dung thực tế.
                    has_frac = any(cmd in tex for cmd in ('\\frac', '\\dfrac', '\\tfrac', '\\cfrac'))
                    if has_frac:
                        return None

                    starts_integral = tex.startswith((
                        '\\int', '\\iint', '\\iiint', '\\oint'
                    ))
                    if starts_integral:
                        # Bắt đầu bằng ∫: bỏ dấu ∫ và cận; lấy glyph đầu thân f(x)/af(x).
                        anchor_y = _first_glyph_bottom(max(1, int(W * 0.18)), int(W * 0.78))
                    else:
                        # Bắt đầu bằng chữ/ký hiệu: lấy duy nhất glyph đầu (I trong I_4,
                        # f trong f(x), P trong P(A)); chỉ số/mũ rời không còn làm lệch.
                        anchor_y = _first_glyph_bottom(0, int(W * 0.35))

                    if anchor_y is None:
                        return None
                    # VML inline mặc định đặt ĐÁY ảnh đúng baseline dòng. Muốn mốc y
                    # nằm ở baseline thì hạ ảnh xuống: position = -(H - y) quy đổi pt.
                    height_pt = height_emu / 12700.0
                    pos_hp = -int(round((H - anchor_y) * height_pt / float(H) * 2.0))
                    # Biên an toàn: không nâng lên, không hạ quá 2 lần chiều cao chữ 14pt.
                    return max(-56, min(0, pos_hp))
                except Exception as _anchor_err:
                    logger.debug('Preview anchor measure failed: %s', _anchor_err)
                    return None

            def _math_part_ole(math_tex, part_idx=None, shape_suffix=0):
                """Build OLE+preview for a math fragment (no overparen)."""
                ole_b = None
                img_b = template_wmf_data
                img_e = template_wmf_ext
                we, he = 914400, 457200

                key = (idx, part_idx) if part_idx is not None else None

                # Ưu tiên MTEF native tmHAT cho part có \widehat (preview vẫn lấy LO/PNG)
                # → Word đẹp + double-click MathType còn mũ góc. Không đụng part không có widehat.
                _native_angle = None
                if math_tex and (r"\widehat" in math_tex) and build_angle_formula_native is not None:
                    try:
                        _native_angle = build_angle_formula_native(math_tex)
                    except Exception as _nae:
                        logger.debug("native angle part failed %r: %s", math_tex[:40], _nae)
                        _native_angle = None
                if _native_angle:
                    try:
                        ole_b = make_mathtype_ole(_native_angle)
                        logger.info(
                            "Formula %d part %s: native angle-hat OLE (%d bytes): %s",
                            idx, part_idx, len(_native_angle), (math_tex or "")[:50],
                        )
                    except Exception as _noe:
                        logger.warning("native angle OLE wrap failed: %s", _noe)
                        ole_b = None
                        _native_angle = None

                if key is not None and key in lo_part_ole_binaries:
                    if ole_b is None:
                        ole_b = lo_part_ole_binaries[key]
                        ole_b = _maybe_repatch_ole_widehat(ole_b, math_tex or latex_formula, idx, logger)
                    if key in lo_part_png_images:
                        img_b = lo_part_png_images[key]
                        img_e = ".png"
                        if key in lo_part_wmf_sizes:
                            we, he = lo_part_wmf_sizes[key]
                    elif key in lo_part_wmf_images:
                        img_b = lo_part_wmf_images[key]
                        img_e = ".wmf"
                        we, he = lo_part_wmf_sizes.get(key, (we, he))
                elif part_idx is None and idx in lo_ole_binaries:
                    if ole_b is None:
                        ole_b = lo_ole_binaries[idx]
                        ole_b = _maybe_repatch_ole_widehat(ole_b, latex_formula, idx, logger)
                    if idx in lo_png_images:
                        img_b = lo_png_images[idx]
                        img_e = ".png"
                        if "sqrt" in (math_tex or "").lower() or "nroot" in (math_tex or "").lower():
                            img_b = enhance_sqrt_png_preview(img_b)
                        if idx in lo_wmf_sizes:
                            we, he = lo_wmf_sizes[idx]
                    elif idx in lo_wmf_images:
                        img_b = lo_wmf_images[idx]
                        img_e = ".wmf"
                        we, he = lo_wmf_sizes.get(idx, (we, he))
                else:
                    # omml fallback for this fragment
                    _mml_latex = re.sub(
                        r'\\(?:overparen|wideparen|overarc)\s*\{([^{}]*)\}',
                        r'\\overline{\1}',
                        math_tex or "",
                    )
                    try:
                        mathml_str = latex2mathml.converter.convert(_mml_latex)
                        mathml_str = mathml_str.replace('\u29F5', '\u2216')
                        mathml_str = mathml_str.replace('&#x029F5;', '&#x02216;')
                        parser = etree.XMLParser(remove_blank_text=True)
                        mathml_el = etree.fromstring(mathml_str, parser)
                        _mtef = omml_converter.mathml_to_mtef_bytes(mathml_el)
                        if use_template:
                            ole_b = patch_ole_bin_bytes(template_bin_data, _mtef)
                        else:
                            ole_b = make_mathtype_ole(make_equation_native_stream(_mtef))
                    except Exception as _fe:
                        logger.warning("math part fallback failed %r: %s", math_tex, _fe)
                        raise

                if ole_b is None:
                    raise RuntimeError(f"no OLE for math part {math_tex!r}")

                # CĂN THEO NHÓM CẤU TRÚC, không quy đổi từ crop PNG sang WMF/EMF.
                # Cách quy đổi cũ là nguyên nhân cùng một công thức bị cao/thấp khác nhau
                # giữa các tệp Word.
                align_kind, pos_hp = _baseline_offset_by_structure(math_tex, he)
                # Phân số khóa theo thanh ngang. Các nhóm khác ưu tiên baseline đo
                # trực tiếp từ preview: chữ đầu hoặc f(x) sau dấu tích phân.
                if align_kind != 'fraction_locked':
                    measured_pos = _anchor_position_from_preview(img_b, img_e, math_tex, he)
                    if measured_pos is not None:
                        pos_hp = measured_pos
                        align_kind += '_measured'
                logger.info('Formula %d part %s alignment=%s position=%s: %s',
                            idx, part_idx, align_kind, pos_hp, (math_tex or '')[:50])

                return _emit_ole_run(ole_b, img_b, img_e, we, he, bf=0.28, pos_hp=pos_hp, shape_suffix=shape_suffix)

            def _arc_part_ole(base_letters, shape_suffix=0, align_with_math=False):
                """OLE MathType thật + PNG cung cong; căn baseline với math nếu cần."""
                ole_b = make_arc_equation_ole(base_letters)
                _arc_r = render_arc_preview_png(base_letters, font_pt=14.0, scale=8)
                _png, _cw, _ch, _we, _he = _arc_r[:5]
                _pos_hp = _arc_r[6] if len(_arc_r) > 6 else None
                return _emit_ole_run(
                    ole_b, _png, ".png", _we, _he,
                    bf=0.28, pos_hp=_pos_hp, shape_suffix=shape_suffix,
                )

            runs_to_insert = []  # list of w:r elements
            handled = False

            if _pure:
                try:
                    if build_arc_equation_native_doc3 is not None:
                        ole_b = make_mathtype_ole(build_arc_equation_native_doc3(_pure))
                        _arc_r = render_arc_preview_png(_pure, font_pt=14.0, scale=8)
                        _png, _cw, _ch, _we, _he = _arc_r[:5]
                        _pos_hp = _arc_r[6] if len(_arc_r) > 6 else None
                        runs_to_insert.append(
                            _emit_ole_run(ole_b, _png, ".png", _we, _he, bf=0.28,
                                         pos_hp=_pos_hp, shape_suffix=0)
                        )
                    else:
                        runs_to_insert.append(
                            _arc_part_ole(_pure, shape_suffix=0, align_with_math=False)
                        )
                    handled = True
                    logger.info("Formula %d: pure arc %r → MathType MTEF v5 Doc3", idx, _pure)
                except Exception as _e:
                    logger.warning("pure arc failed %s: %s", _pure, _e)

            if not handled and _multi_pure is not None:
                try:
                    # Mỗi cung = 1 OLE MathType thật; +/= = text run
                    sfx = 0
                    for kind, val in _multi_pure:
                        if kind == "arc":
                            runs_to_insert.append(
                                _arc_part_ole(val, shape_suffix=sfx, align_with_math=False)
                            )
                            sfx += 1
                        else:
                            op = (val or "").strip()
                            if op:
                                runs_to_insert.append(_make_text_run(f" {op} " if len(op) <= 3 else op))
                    handled = bool(runs_to_insert)
                    logger.info("Formula %d: multi pure arcs → %d runs", idx, len(runs_to_insert))
                except Exception as _e:
                    logger.warning("multi pure arc failed: %s", _e)
                    runs_to_insert = []
                    handled = False

            if not handled and _mixed_parts is not None:
                # Tách mixed formula → mỗi cung 1 OLE MTEF v5 riêng, math → OLE MathType
                # Không gộp 1 OLE (vì build_geometry_formula_native không handle mixed).
                try:
                    sfx = 0
                    for p_i, (kind, val) in enumerate(_mixed_parts):
                        if kind == "arc":
                            # Arc → arc_symbol_builder → MTEF v5 thật + PNG bezier
                            if build_arc_equation_native_doc3 is not None:
                                ole_b = make_mathtype_ole(build_arc_equation_native_doc3(val))
                                _arc_render = render_arc_preview_png(
                                    val, font_pt=14.0, scale=8
                                )
                                _png, _cw, _ch, _we, _he = _arc_render[:5]
                                _pos_hp = _arc_render[6] if len(_arc_render) > 6 else None
                                runs_to_insert.append(
                                    _emit_ole_run(ole_b, _png, ".png", _we, _he,
                                                  bf=0.28, pos_hp=_pos_hp, shape_suffix=sfx)
                                )
                                sfx += 1
                        else:
                            # Math part → OLE MathType (dùng LO pre-rendered hoặc fallback OMML)
                            math_tex = (val or "").strip()
                            if math_tex and not _is_plain_op_gap(math_tex):
                                try:
                                    runs_to_insert.append(
                                        _math_part_ole(math_tex, part_idx=p_i, shape_suffix=sfx)
                                    )
                                    sfx += 1
                                except Exception as _me:
                                    # Fallback: chỉ in text thô nếu OLE thất bại hoàn toàn
                                    logger.warning(
                                        "Formula %d part %d math OLE failed, using text run: %s",
                                        idx, p_i, _me
                                    )
                                    runs_to_insert.append(_make_text_run(f" {math_tex} "))
                            elif math_tex:
                                # Toán tử/khoảng trống đơn giản (=, +, ...) → text run
                                runs_to_insert.append(_make_text_run(f" {math_tex} "))
                    handled = bool(runs_to_insert)
                    if handled:
                        logger.info(
                            "Formula %d: mixed → %d runs (arcs as MTEF v5)",
                            idx, len(runs_to_insert),
                        )
                except Exception as _e:
                    logger.warning("Mixed parts failed: %s", _e)
                    runs_to_insert = []
                    handled = False

            if not handled:
                # Normal / fallback: 1 OLE full formula (LO ưu tiên)
                ole_bin = None
                wmf_data = template_wmf_data
                wmf_ext = template_wmf_ext
                w_emu, h_emu = 914400, 457200
                _bf = _calc_math_bf(latex_formula, h_emu)

                try:
                    from omml_to_mtef import latex_to_mathtype_ole_offline
                    ole_bin = latex_to_mathtype_ole_offline(latex_formula)
                except Exception:
                    if idx in lo_ole_binaries:
                        _lo_b = lo_ole_binaries[idx]
                        ole_bin = _lo_b if _lo_b.startswith(b'\xd0\xcf\x11\xe0') else make_mathtype_ole(_lo_b)
                    else:
                        if mtef_bytes is None:
                            raise RuntimeError("no LO bin and no mtef_bytes")
                        ole_bin = make_mathtype_ole(make_equation_native_stream(mtef_bytes))

                if idx in lo_png_images:
                    wmf_data = lo_png_images[idx]
                    wmf_ext = ".png"
                    if "sqrt" in latex_formula.lower() or "nroot" in latex_formula.lower():
                        wmf_data = enhance_sqrt_png_preview(wmf_data)
                    if idx in lo_wmf_sizes:
                        w_emu, h_emu = lo_wmf_sizes[idx]
                elif idx in lo_wmf_images:
                    wmf_data = lo_wmf_images[idx]
                    wmf_ext = ".wmf"
                    w_emu, h_emu = lo_wmf_sizes.get(idx, (w_emu, h_emu))

                # NHÁNH CÔNG THỨC THÔNG THƯỜNG: phân loại theo cấu trúc thay vì
                # dùng cùng một độ hạ cho mọi công thức không phân số.
                _align_kind, _pos_hp = _baseline_offset_by_structure(latex_formula, h_emu)
                # Phân số giữ offset đã khóa; mọi công thức khác đo mốc thật từ preview.
                if _align_kind != 'fraction_locked':
                    _measured_pos = _anchor_position_from_preview(
                        wmf_data, wmf_ext, latex_formula, h_emu
                    )
                    if _measured_pos is not None:
                        _pos_hp = _measured_pos
                        _align_kind += '_measured'
                logger.info(
                    'Formula %d normal alignment=%s position=%s: %s',
                    idx, _align_kind, _pos_hp, (latex_formula or '')[:60],
                )
                runs_to_insert.append(
                    _emit_ole_run(
                        ole_bin, wmf_data, wmf_ext, w_emu, h_emu,
                        bf=_bf, pos_hp=_pos_hp, shape_suffix=0,
                    )
                )

            # Chèn 1 hoặc nhiều run thay cho run LaTeX gốc
            parent = run.getparent()
            if parent is not None and runs_to_insert:
                run_idx = list(parent).index(run)
                parent.remove(run)
                for j, el in enumerate(runs_to_insert):
                    parent.insert(run_idx + j, el)

            converted += 1
            logger.info("Converted formula %d: %s", idx, latex_formula[:60])
            
        except Exception as e:
            errors += 1
            logger.error("Failed to convert formula %d (%s): %s", idx, latex_formula, e)
            
        if progress_callback:
            progress_callback(idx, total_formulas, latex_formula)
            
    # Clean up temporary directory if created
    if temp_dir and os.path.exists(temp_dir):
        import shutil
        try:
            shutil.rmtree(temp_dir)
        except Exception as e:
            logger.error("Failed to clean up temp dir %s: %s", temp_dir, e)
            
    # Apply Times New Roman 14 formatting to document runs and stylesheet defaults
    apply_formatting_times_new_roman_14(zdata, doc_root)
    
    # Serialize XMLs back
    zdata[doc_xml_path] = _serialise_xml(doc_root)
    zdata[rels_path] = _serialise_xml(rels_root)
    zdata[ct_path] = _serialise_xml(ct_root)
    
    # Save output docx
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zout:
        for name, data in zdata.items():
            zout.writestr(name, data)
            
    logger.info("Conversion finished: converted=%d, errors=%d", converted, errors)
    return {"total": total_formulas, "converted": converted, "errors": errors,
            "dollar_warnings": dollar_warnings}


def convert_docx_latex_to_omml(input_path: str, output_path: str, progress_callback=None) -> dict:
    """Process a docx file, convert LaTeX math formulas directly to native Word OMML (<m:oMath>) and save."""
    xslt_file = find_mml2omml_xslt()
    xslt_tree = etree.parse(xslt_file)
    transform_mml_to_omml = etree.XSLT(xslt_tree)
    
    # Read DOCX
    with zipfile.ZipFile(input_path, "r") as zin:
        names = set(zin.namelist())
        zdata = {n: zin.read(n) for n in names}
        
    doc_xml_path = "word/document.xml"
    doc_root = _parse_xml(zdata[doc_xml_path])
    
    # Remove spell check markers and merge formatting runs
    clean_proof_errors(doc_root)
    unwrap_math_paras(doc_root)
    for p in doc_root.iter(_w("p")):
        merge_adjacent_runs(p)

    latex_pattern = re.compile(r'(?<!\\)\$\$(.*?)(?<!\\)\$\$|(?<!\\)\$(.*?)(?<!\\)\$', re.DOTALL)

    paragraphs = list(doc_root.iter(_w("p")))
    latex_runs_data = []
    for p in paragraphs:
        matched_runs = isolate_latex_runs(p, latex_pattern)
        for run in matched_runs:
            latex_runs_data.append((p, run))
            
    total_formulas = len(latex_runs_data)
    logger.info("Found %d LaTeX formula(s) to convert to native OMML", total_formulas)
    
    converted = 0
    errors = 0
    
    for idx, (p, run) in enumerate(latex_runs_data, 1):
        t_node = run.find(_w("t"))
        if t_node is None or not t_node.text:
            continue
            
        full_text = t_node.text.strip()
        if full_text.startswith("$$") and full_text.endswith("$$"):
            latex_formula = full_text[2:-2].strip()
        elif full_text.startswith("$") and full_text.endswith("$"):
            latex_formula = full_text[1:-1].strip()
        else:
            latex_formula = full_text
            
        if not latex_formula:
            continue
            
        # Automatically add backslashes to standard trigonometric/logarithmic functions if they are missing
        latex_formula = re.sub(r"(?<!\\)\b(cos|sin|tan|cot|ln|log)\b", r"\\\1", latex_formula)
            
        try:
            # 0. Chuẩn hoá cú pháp AI hay sinh nhưng latex2mathml không hiểu:
            #    \vert{} → \vert  (AI dùng {} rỗng để tách token, không phải argument)
            latex_formula = re.sub(
                r'\\(vert|lvert|rvert|Vert|lVert|rVert)\{\}',
                r'\\\1', latex_formula
            )
            # 1. Convert LaTeX to MathML
            mathml_str = latex2mathml.converter.convert(latex_formula)
            parser = etree.XMLParser(remove_blank_text=True)
            mathml_el = etree.fromstring(mathml_str, parser)
            
            # 2. MathML -> OMML
            omml_el = transform_mml_to_omml(mathml_el)
            omml_root = omml_el.getroot()
            
            # 3. Replace run with OMML element
            parent = run.getparent()
            if parent is not None:
                run_idx = list(parent).index(run)
                parent.remove(run)
                parent.insert(run_idx, omml_root)
                
            converted += 1
            logger.info("Converted formula %d to native OMML: %s", idx, latex_formula)
        except Exception as e:
            errors += 1
            logger.error("Failed to convert formula %d to native OMML (%s): %s", idx, latex_formula, e)
            
        if progress_callback:
            progress_callback(idx, total_formulas, latex_formula)
            
    # Apply Times New Roman 14 formatting to document runs and stylesheet defaults
    apply_formatting_times_new_roman_14(zdata, doc_root)
    
    # Serialize XMLs back
    zdata[doc_xml_path] = _serialise_xml(doc_root)

    # Save output docx
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zout:
        for name, data in zdata.items():
            zout.writestr(name, data)

    logger.info("Conversion finished: converted=%d, errors=%d", converted, errors)
    return {"total": total_formulas, "converted": converted, "errors": errors}


if __name__ == "__main__":
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    _require_local_engine_license()

    if len(sys.argv) < 3:
        print("Sử dụng: python docx_processor.py <src.docx> <out.docx>")
        sys.exit(1)

    src, out = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])

    def _progress(idx, total, latex):
        if idx % 10 == 0 or idx == total:
            print(f"Đang xử lý: {idx}/{total} công thức...", flush=True)

    print(f"Đang mở file: {os.path.basename(src)}", flush=True)
    try:
        res = convert_docx_latex_to_mathtype(
            src, out, use_libreoffice=True, progress_callback=_progress)
    except Exception as e:
        print(f"Lỗi: {e}", flush=True)
        sys.exit(1)

    print(
        f"Hoàn tất! {res['converted']}/{res['total']} công thức "
        f"({res['errors']} lỗi) → {os.path.basename(out)}",
        flush=True)

    warns = res.get("dollar_warnings") or []
    if warns:
        print(f"\n⚠ CẢNH BÁO: {len(warns)} đoạn có số dấu '$' lẻ — "
              f"công thức thiếu dấu mở/đóng sẽ KHÔNG được chuyển thành MathType:",
              flush=True)
        for w in warns:
            print(f"  - {w}", flush=True)
    sys.exit(0)
