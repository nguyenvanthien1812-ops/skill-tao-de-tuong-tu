# -*- coding: utf-8 -*-
"""
omml_to_mtef.py

Module chuyển đổi OMML XML (Office Math Markup Language) sang MTEF v5 (MathType 7) bytes
và đóng gói thành OLE Compound Binary Streams để nhúng trực tiếp vào tệp Word (.docx).

Chạy thuần Python 100%, KHÔNG phụ thuộc MS Word hay MathType software.

Cover 100% cấu trúc OMML:
  - Text, Numbers, Operators, Variables, Greek letters, Symbols
  - <m:f>       Fractions (phân số)
  - <m:rad>     Radicals (căn bậc 2, căn bậc n)
  - <m:sSub>    Subscripts
  - <m:sSup>    Superscripts
  - <m:sSubSup> SubSuperscripts
  - <m:sPre>    Pre-sub-superscripts
  - <m:nary>    n-ary operators (Sum, Integral, Product, Union, Inter, etc.)
  - <m:d>       Delimiters / Brackets / Cases / Bra-ket
  - <m:acc>     Accents (widehat, frown/arc, vec, tilde, bar, dot, etc.)
  - <m:bar>     Overbar / Underbar
  - <m:m>       Matrices (Ma trận)
  - <m:eqArr>   Equation Arrays / Piles (Hệ phương trình / Căn lề nhiều dòng)
  - <m:limLow>  Lower Limits
  - <m:limUpp>  Upper Limits
  - <m:func>    Functions (sin, cos, log, lim, etc.)
  - <m:groupChr> Group Characters (underbrace, overbrace)
  - <m:borderBox>, <m:box>, <m:phant> Boxes & Phantoms
"""

import struct
from lxml import etree
from mtef_encoder import (

    _DOC3_PREFIX, TF_TEXT, TF_VAR, TF_MTEXTRA,
    _line_start, _char, _chars, _end,
    EMBELL_VEC, EMBELL_HAT, EMBELL_TILDE, EMBELL_DOT, EMBELL_DDOT, EMBELL_BAR
)
from mathtype_ole_builder import make_mathtype_ole

def _require_local_engine_license():
    """Kiem tra ban quyen bat buoc truoc khi thuc thi Local Engine MathType."""
    try:
        import os as _os, sys as _sys
        _cur_dir = _os.path.dirname(_os.path.abspath(__file__))
        _scripts_dir = _os.path.dirname(_cur_dir)
        if _scripts_dir not in _sys.path:
            _sys.path.insert(0, _scripts_dir)
        import license_manager
        ok, payload, err = license_manager.check_current_license()
        if not ok:
            raise PermissionError(f"Local Engine MathType chua kich hoat ban quyen hop le: {err}")
        return payload
    except ImportError:
        raise PermissionError("LOI BAN QUYEN: Khong tim thay module xac minh license_manager.py. Khong duoc tach le Local Engine.")

_require_local_engine_license()

# OMML XML Namespace
OMML_NS = "{http://schemas.openxmlformats.org/officeDocument/2006/math}"
W_NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

def _tmpl_header(tmpl_type: int, slot_count: int = 1, variation: int = 0, options: int = 0) -> bytes:
    """Xây dựng MTEF TMPL record header hỗ trợ variation đầy đủ."""
    var_lo = variation & 0xFF
    var_hi = (variation >> 8) & 0xFF
    return bytes([0x03, options, tmpl_type, var_lo, var_hi, slot_count, 0x00])

# ──────────────────────────────────────────────
# Special Symbol & Character Code Mappings
# ──────────────────────────────────────────────

UNICODE_SYMBOL_MAP = {
    # Operators & Relations (Symbol font 0x83)
    '=': (TF_VAR, ord('=')),
    '+': (TF_VAR, ord('+')),
    '-': (TF_VAR, ord('-')),
    '*': (TF_VAR, 0xD7),        # \times
    '×': (TF_VAR, 0xD7),
    '÷': (TF_VAR, 0xF7),
    '±': (TF_VAR, 0xB1),
    '∓': (TF_VAR, 0xBF),
    '≤': (TF_VAR, 0xA3),
    '≥': (TF_VAR, 0xB3),
    '≠': (TF_VAR, 0xB9),
    '≈': (TF_VAR, 0xBB),
    '≡': (TF_VAR, 0xBA),
    '∈': (TF_VAR, 0xCE),
    '∉': (TF_VAR, 0xCF),
    '⊂': (TF_VAR, 0xCC),
    '⊃': (TF_VAR, 0xC9),
    '∪': (TF_VAR, 0xC8),
    '∩': (TF_VAR, 0xC7),
    '⋅': (TF_VAR, 0xD7),
    '·': (TF_VAR, 0xD7),
    '→': (TF_VAR, 0xAE),
    '←': (TF_VAR, 0xAC),
    '⇒': (TF_VAR, 0xDE),
    '⇐': (TF_VAR, 0xDC),
    '⇔': (TF_VAR, 0xDB),
    '↔': (TF_VAR, 0xAB),
    '∞': (TF_VAR, 0xA5),
    '∂': (TF_VAR, 0xB6),
    '∇': (TF_VAR, 0xD1),
    '∃': (TF_VAR, 0x24),
    '∀': (TF_VAR, 0x22),
    '∅': (TF_VAR, 0xE6),
    '∠': (TF_VAR, 0xD0),
    '⊥': (TF_VAR, 0x5E),
    '∥': (TF_VAR, 0xBD),
    '∝': (TF_VAR, 0x5E),
    '°': (TF_VAR, 0xB0),
    '′': (TF_VAR, 0xA2),
    '″': (TF_VAR, 0xA2),
    '…': (TF_VAR, 0x2E),
    '⋯': (TF_VAR, 0xB7),

    # Greek lowercase (Symbol font)
    'α': (TF_VAR, 0x61), 'β': (TF_VAR, 0x62), 'γ': (TF_VAR, 0x67), 'δ': (TF_VAR, 0x64),
    'ε': (TF_VAR, 0x65), 'ζ': (TF_VAR, 0x7A), 'η': (TF_VAR, 0x68), 'θ': (TF_VAR, 0x71),
    'ι': (TF_VAR, 0x69), 'κ': (TF_VAR, 0x6B), 'λ': (TF_VAR, 0x6C), 'μ': (TF_VAR, 0x6D),
    'ν': (TF_VAR, 0x6E), 'ξ': (TF_VAR, 0x78), 'ο': (TF_VAR, 0x6F), 'π': (TF_VAR, 0x70),
    'ρ': (TF_VAR, 0x72), 'σ': (TF_VAR, 0x73), 'τ': (TF_VAR, 0x74), 'υ': (TF_VAR, 0x75),
    'φ': (TF_VAR, 0x66), 'χ': (TF_VAR, 0x63), 'ψ': (TF_VAR, 0x79), 'ω': (TF_VAR, 0x77),
    'ϕ': (TF_VAR, 0x6A), 'ϖ': (TF_VAR, 0x76), 'ϑ': (TF_VAR, 0x4A),

    # Greek uppercase (Symbol font)
    'Γ': (TF_VAR, 0x47), 'Δ': (TF_VAR, 0x44), 'Θ': (TF_VAR, 0x51), 'Λ': (TF_VAR, 0x4C),
    'Ξ': (TF_VAR, 0x58), 'Π': (TF_VAR, 0x50), 'Σ': (TF_VAR, 0x53), 'Φ': (TF_VAR, 0x46),
    'Ψ': (TF_VAR, 0x59), 'Ω': (TF_VAR, 0x57),

    # MT Extra glyphs
    '⏜': (TF_MTEXTRA, 0x2322),   # Arc frown U+2322
    '⌢': (TF_MTEXTRA, 0x2322),
    '⏠': (TF_MTEXTRA, 0x2322),
}

# Selectors (from record.py)
T_ANGLE    = 0
T_PAREN    = 1
T_BRACE    = 2
T_BRACK    = 3
T_BAR      = 4
T_DBAR     = 5
T_FLOOR    = 6
T_CEILING  = 7
T_OBRACK   = 8
T_INTERVAL = 9
T_ROOT     = 10
T_FRAC     = 11
T_UBAR     = 12
T_OBAR     = 13
T_ARROW    = 14
T_INTEGRAL = 15
T_SUM      = 16
T_PROD     = 17
T_COPROD   = 18
T_UNION    = 19
T_INTER    = 20
T_LIM      = 23
T_HBRACE   = 24
T_HBRACK   = 25
T_SUB      = 27
T_SUP      = 28
T_SUBSUP   = 29
T_DIRAC    = 30
T_VEC      = 31
T_TILDE    = 32
T_HAT      = 33
T_ARC      = 34
T_STRIKE   = 36
T_BOX      = 37

def _build_fence_template(beg_chr: str, end_chr: str, body_records: bytes) -> bytes:
    """Xây dựng MTEF template bọc ngoặc (Fence) dựa trên begChr và endChr."""
    sel = T_PAREN
    var = 0x0003  # Left and right fence present (tvFENCE_L | tvFENCE_R)
    
    if not beg_chr and not end_chr:
        sel = T_PAREN
        var = 0x0000
    elif beg_chr == '{' and not end_chr:
        sel = T_BRACE
        var = 0x0001  # tvFENCE_L only
    elif not beg_chr and end_chr == '}':
        sel = T_BRACE
        var = 0x0002  # tvFENCE_R only
    elif beg_chr == '(' and end_chr == ')':
        sel = T_PAREN
    elif beg_chr == '[' and end_chr == ']':
        sel = T_BRACK
    elif beg_chr == '{' and end_chr == '}':
        sel = T_BRACE
    elif beg_chr == '|' and end_chr == '|':
        sel = T_BAR
    elif (beg_chr in ('||', '‖') and end_chr in ('||', '‖')):
        sel = T_DBAR
    elif beg_chr in ('⟨', '<') and end_chr in ('⟩', '>'):
        sel = T_ANGLE
    elif beg_chr == '⌊' and end_chr == '⌋':
        sel = T_FLOOR
    elif beg_chr == '⌈' and end_chr == '⌉':
        sel = T_CEILING
    else:
        sel = T_PAREN

    return _tmpl_header(sel, 1, var) + body_records + _end() + _end()

def _build_matrix_records(rows: list) -> bytes:
    """Xây dựng MTEF MATRIX record (tag 5) từ danh sách các hàng [ [cell1_records, cell2_records], ... ]"""
    num_rows = len(rows)
    if num_rows == 0:
        return _end()
    num_cols = max(len(row) for row in rows) if rows else 0
    if num_cols == 0:
        return _end()

    hdr = bytes([0x05, 0x00, 0x01, 0x01, 0x01, num_rows, num_cols])

    cell_bytes = bytearray()
    for r in range(num_rows):
        row = rows[r]
        for c in range(num_cols):
            cell = row[c] if c < len(row) else b''
            cell_bytes += _line_start() + cell + _end()

    return hdr + cell_bytes + _end()

def _build_pile_records(lines: list, halign: int = 1, valign: int = 1) -> bytes:
    """Xây dựng MTEF PILE record (tag 4) cho hệ phương trình hoặc căn lề nhiều dòng."""
    if not lines:
        return _end()
    
    hdr = bytes([0x04, 0x00, halign, valign])
    line_bytes = bytearray()
    for line in lines:
        line_bytes += _line_start() + line + _end()
        
    return hdr + line_bytes + _end()


# ──────────────────────────────────────────────
# OMML Recursive Parser → MTEF Bytes
# ──────────────────────────────────────────────

def omml_to_mtef_records(element: etree.Element) -> bytes:
    """Parse một OMML XML element và trả về chuỗi MTEF records tương ứng."""
    if element is None:
        return b''

    tag = element.tag
    if tag.startswith('{'):
        tag_name = tag.split('}')[-1]
    else:
        tag_name = tag

    if tag_name in ('oMath', 'oMathPara', 'e', 'num', 'den', 'sub', 'sup', 'deg', 'lim', 'fName', 'base'):
        res = bytearray()
        for child in element:
            res += omml_to_mtef_records(child)
        return bytes(res)
    elif tag_name == 'r':
        return _parse_omml_run(element)
    elif tag_name == 'f':
        return _parse_omml_fraction(element)
    elif tag_name == 'rad':
        return _parse_omml_radical(element)
    elif tag_name in ('sSub', 'sSup', 'sSubSup', 'sPre'):
        return _parse_omml_scripts(element, tag_name)
    elif tag_name == 'nary':
        return _parse_omml_nary(element)
    elif tag_name == 'd':
        return _parse_omml_delimiter(element)
    elif tag_name == 'acc':
        return _parse_omml_accent(element)
    elif tag_name == 'bar':
        return _parse_omml_bar(element)
    elif tag_name == 'm':
        return _parse_omml_matrix(element)
    elif tag_name == 'eqArr':
        return _parse_omml_eq_arr(element)
    elif tag_name in ('limLow', 'limUpp'):
        return _parse_omml_limit(element, tag_name)
    elif tag_name == 'func':
        return _parse_omml_func(element)
    elif tag_name == 'groupChr':
        return _parse_omml_group_chr(element)
    elif tag_name in ('borderBox', 'box', 'phant'):
        e = element.find(f"{OMML_NS}e")
        if e is not None:
            return omml_to_mtef_records(e)
        res = bytearray()
        for child in element:
            res += omml_to_mtef_records(child)
        return bytes(res)
    else:
        res = bytearray()
        for child in element:
            res += omml_to_mtef_records(child)
        return bytes(res)


# ──────────────────────────────────────────────
# Detailed OMML Element Parsers
# ──────────────────────────────────────────────

def _parse_omml_run(r_elem: etree.Element) -> bytes:
    """Parse <m:r> text run."""
    t_elem = r_elem.find(f"{OMML_NS}t")
    if t_elem is None or not t_elem.text:
        t_elem = r_elem.find(f"{W_NS}t")
        if t_elem is None or not t_elem.text:
            return b''

    text = t_elem.text
    rPr = r_elem.find(f"{OMML_NS}rPr")
    is_normal = False
    if rPr is not None:
        if rPr.find(f"{OMML_NS}nor") is not None or rPr.find(f"{OMML_NS}scr") is not None:
            is_normal = True
        sty = rPr.find(f"{OMML_NS}sty")
        if sty is not None and sty.attrib.get(f"{OMML_NS}val") in ('p', 'plain'):
            is_normal = True

    res = bytearray()
    for ch in text:
        if ch in UNICODE_SYMBOL_MAP:
            tf, code = UNICODE_SYMBOL_MAP[ch]
            res += _char(chr(code), tf)
        elif ch.isdigit():
            res += _char(ch, TF_TEXT)
        elif ch.isalpha():
            tf = TF_TEXT if is_normal else TF_VAR
            res += _char(ch, tf)
        else:
            tf = TF_TEXT
            res += _char(ch, tf)

    return bytes(res)

def _parse_omml_fraction(f_elem: etree.Element) -> bytes:
    """Parse <m:f> fraction."""
    num_e = f_elem.find(f"{OMML_NS}num")
    den_e = f_elem.find(f"{OMML_NS}den")

    num_bytes = omml_to_mtef_records(num_e) if num_e is not None else b''
    den_bytes = omml_to_mtef_records(den_e) if den_e is not None else b''

    fPr = f_elem.find(f"{OMML_NS}fPr")
    var = 0x0000
    if fPr is not None:
        type_elem = fPr.find(f"{OMML_NS}type")
        if type_elem is not None:
            val = type_elem.attrib.get(f"{OMML_NS}val", "")
            if val == 'noBar':
                return _tmpl_header(T_FRAC, 2, 0x0000) + num_bytes + _end() + den_bytes + _end() + _end()
            elif val == 'skw':
                var = 0x0002

    return _tmpl_header(T_FRAC, 2, var) + num_bytes + _end() + den_bytes + _end() + _end()

def _parse_omml_radical(rad_elem: etree.Element) -> bytes:
    """Parse <m:rad> radical."""
    e_elem = rad_elem.find(f"{OMML_NS}e")
    deg_elem = rad_elem.find(f"{OMML_NS}deg")

    base_bytes = omml_to_mtef_records(e_elem) if e_elem is not None else b''

    radPr = rad_elem.find(f"{OMML_NS}radPr")
    deg_hide = False
    if radPr is not None:
        dh = radPr.find(f"{OMML_NS}degHide")
        if dh is not None and dh.attrib.get(f"{OMML_NS}val") in ('1', 'on', 'true'):
            deg_hide = True

    if deg_elem is not None and not deg_hide and len(deg_elem) > 0:
        deg_bytes = omml_to_mtef_records(deg_elem)
        if deg_bytes.strip():
            return _tmpl_header(T_ROOT, 2, 1) + deg_bytes + _end() + base_bytes + _end() + _end()

    return _tmpl_header(T_ROOT, 1, 0) + base_bytes + _end() + _end()

def _parse_omml_scripts(elem: etree.Element, tag_name: str) -> bytes:
    """Parse subscripts and superscripts (<m:sSub>, <m:sSup>, <m:sSubSup>, <m:sPre>)."""
    base_e = elem.find(f"{OMML_NS}e")
    sub_e = elem.find(f"{OMML_NS}sub")
    sup_e = elem.find(f"{OMML_NS}sup")

    base_bytes = omml_to_mtef_records(base_e) if base_e is not None else b''
    sub_bytes = omml_to_mtef_records(sub_e) if sub_e is not None else b''
    sup_bytes = omml_to_mtef_records(sup_e) if sup_e is not None else b''

    if tag_name == 'sSub':
        return base_bytes + _tmpl_header(T_SUB, 1) + sub_bytes + _end() + _end()
    elif tag_name == 'sSup':
        return base_bytes + _tmpl_header(T_SUP, 1) + sup_bytes + _end() + _end()
    elif tag_name == 'sSubSup':
        return base_bytes + _tmpl_header(T_SUBSUP, 2) + sub_bytes + _end() + sup_bytes + _end() + _end()
    elif tag_name == 'sPre':
        return _tmpl_header(T_SUBSUP, 2, 0x0001) + sub_bytes + _end() + sup_bytes + _end() + _end() + base_bytes
    return base_bytes

def _parse_omml_nary(nary_elem: etree.Element) -> bytes:
    """Parse n-ary operator (<m:nary>)."""
    naryPr = nary_elem.find(f"{OMML_NS}naryPr")
    chr_val = "∫"
    if naryPr is not None:
        chr_elem = naryPr.find(f"{OMML_NS}chr")
        if chr_elem is not None:
            chr_val = chr_elem.attrib.get(f"{OMML_NS}val", "∫")

    sub_e = nary_elem.find(f"{OMML_NS}sub")
    sup_e = nary_elem.find(f"{OMML_NS}sup")
    e_elem = nary_elem.find(f"{OMML_NS}e")

    sub_bytes = omml_to_mtef_records(sub_e) if sub_e is not None else b''
    sup_bytes = omml_to_mtef_records(sup_e) if sup_e is not None else b''
    base_bytes = omml_to_mtef_records(e_elem) if e_elem is not None else b''

    if chr_val in ('∫', '∬', '∭', '∮'):
        sel = T_INTEGRAL
        var = 0x0001
        if chr_val == '∬': var = 0x0002
        elif chr_val == '∭': var = 0x0003
        elif chr_val == '∮': var = 0x0004
    elif chr_val == '∑':
        sel = T_SUM
        var = 0x0000
    elif chr_val == '∏':
        sel = T_PROD
        var = 0x0000
    elif chr_val == '∐':
        sel = T_COPROD
        var = 0x0000
    elif chr_val == '⋃':
        sel = T_UNION
        var = 0x0000
    elif chr_val == '⋂':
        sel = T_INTER
        var = 0x0000
    else:
        sel = T_SUM
        var = 0x0000

    slots = []
    slots.append(sub_bytes if sub_bytes else _end())
    slots.append(_end())
    slots.append(sup_bytes if sup_bytes else _end())
    slots.append(_end())
    slots.append(base_bytes)
    slots.append(_end())

    return _tmpl_header(sel, 3, var) + b''.join(slots) + _end()

def _parse_omml_delimiter(d_elem: etree.Element) -> bytes:
    """Parse delimiter / brackets / cases (<m:d>)."""
    dPr = d_elem.find(f"{OMML_NS}dPr")
    beg_chr = "("
    end_chr = ")"
    if dPr is not None:
        bc = dPr.find(f"{OMML_NS}begChr")
        if bc is not None:
            beg_chr = bc.attrib.get(f"{OMML_NS}val", "")
        ec = dPr.find(f"{OMML_NS}endChr")
        if ec is not None:
            end_chr = ec.attrib.get(f"{OMML_NS}val", "")

    e_list = d_elem.findall(f"{OMML_NS}e")
    if not e_list:
        return b''

    if len(e_list) == 1:
        first_e = e_list[0]
        matrix_child = first_e.find(f"{OMML_NS}m")
        if matrix_child is not None:
            body_bytes = omml_to_mtef_records(first_e)
            return _build_fence_template(beg_chr, end_chr, body_bytes)

    body_bytes = bytearray()
    for idx, e in enumerate(e_list):
        body_bytes += omml_to_mtef_records(e)
        if idx < len(e_list) - 1:
            body_bytes += _char(',', TF_TEXT)

    return _build_fence_template(beg_chr, end_chr, bytes(body_bytes))

def _parse_omml_accent(acc_elem: etree.Element) -> bytes:
    """Parse accent (<m:acc>)."""
    accPr = acc_elem.find(f"{OMML_NS}accPr")
    chr_val = "̂"
    if accPr is not None:
        chr_e = accPr.find(f"{OMML_NS}chr")
        if chr_e is not None:
            chr_val = chr_e.attrib.get(f"{OMML_NS}val", "̂")

    e_elem = acc_elem.find(f"{OMML_NS}e")
    base_bytes = omml_to_mtef_records(e_elem) if e_elem is not None else b''

    if chr_val in ('̂', 'ˆ', '^'):
        return _tmpl_header(T_HAT, 1) + base_bytes + _end() + _end()
    elif chr_val in ('⏜', '⌢', '⏠'):
        return _tmpl_header(T_ARC, 1) + base_bytes + _end() + _char('\u2322', TF_MTEXTRA) + _end() + _end()
    elif chr_val in ('̃', '˜', '~'):
        return _tmpl_header(T_TILDE, 1) + base_bytes + _end() + _end()
    elif chr_val in ('⃗', '→'):
        return _tmpl_header(T_VEC, 1) + base_bytes + _end() + _end()
    elif chr_val in ('¯', '̅', '-'):
        return _tmpl_header(T_OBAR, 1) + base_bytes + _end() + _end()
    else:
        return _tmpl_header(T_HAT, 1) + base_bytes + _end() + _end()

def _parse_omml_bar(bar_elem: etree.Element) -> bytes:
    """Parse overbar / underbar (<m:bar>)."""
    barPr = bar_elem.find(f"{OMML_NS}barPr")
    pos = "top"
    if barPr is not None:
        pos_e = barPr.find(f"{OMML_NS}pos")
        if pos_e is not None:
            pos = pos_e.attrib.get(f"{OMML_NS}val", "top")

    e_elem = bar_elem.find(f"{OMML_NS}e")
    base_bytes = omml_to_mtef_records(e_elem) if e_elem is not None else b''

    sel = T_OBAR if pos == 'top' else T_UBAR
    return _tmpl_header(sel, 1) + base_bytes + _end() + _end()

def _parse_omml_matrix(m_elem: etree.Element) -> bytes:
    """Parse matrix (<m:m>)."""
    mr_list = m_elem.findall(f"{OMML_NS}mr")
    rows = []
    for mr in mr_list:
        row_cells = []
        for cell_e in mr.findall(f"{OMML_NS}e"):
            row_cells.append(omml_to_mtef_records(cell_e))
        rows.append(row_cells)

    return _build_matrix_records(rows)

def _parse_omml_eq_arr(eq_elem: etree.Element) -> bytes:
    """Parse equation array / pile (<m:eqArr>)."""
    lines = []
    for e in eq_elem.findall(f"{OMML_NS}e"):
        lines.append(omml_to_mtef_records(e))

    return _build_pile_records(lines)

def _parse_omml_limit(lim_elem: etree.Element, tag_name: str) -> bytes:
    """Parse limit lower / upper (<m:limLow>, <m:limUpp>)."""
    e_elem = lim_elem.find(f"{OMML_NS}e")
    lim_e = lim_elem.find(f"{OMML_NS}lim")

    base_bytes = omml_to_mtef_records(e_elem) if e_elem is not None else b''
    lim_bytes = omml_to_mtef_records(lim_e) if lim_e is not None else b''

    return _tmpl_header(T_LIM, 2) + lim_bytes + _end() + base_bytes + _end() + _end()

def _parse_omml_func(func_elem: etree.Element) -> bytes:
    """Parse function (<m:func>)."""
    fname_e = func_elem.find(f"{OMML_NS}fName")
    e_e = func_elem.find(f"{OMML_NS}e")

    fname_bytes = omml_to_mtef_records(fname_e) if fname_e is not None else b''
    base_bytes = omml_to_mtef_records(e_e) if e_e is not None else b''

    return fname_bytes + base_bytes

def _parse_omml_group_chr(group_elem: etree.Element) -> bytes:
    """Parse group character / overbrace / underbrace (<m:groupChr>)."""
    groupChrPr = group_elem.find(f"{OMML_NS}groupChrPr")
    pos = "top"
    if groupChrPr is not None:
        pos_e = groupChrPr.find(f"{OMML_NS}pos")
        if pos_e is not None:
            pos = pos_e.attrib.get(f"{OMML_NS}val", "top")

    e_elem = group_elem.find(f"{OMML_NS}e")
    base_bytes = omml_to_mtef_records(e_elem) if e_elem is not None else b''

    var = 0x0001 if pos == 'top' else 0x0000
    return _tmpl_header(T_HBRACE, 1, var) + base_bytes + _end() + _end()


# ──────────────────────────────────────────────
# Main API Functions
# ──────────────────────────────────────────────

def omml_to_mtef(omml_element: etree.Element) -> bytes:
    """
    Chuyển đổi một OMML XML element (lxml Element) thành chuỗi MTEF v5 bytes.
    """
    body_records = omml_to_mtef_records(omml_element)
    formula_records = _line_start() + body_records + _end()

    prefix = _DOC3_PREFIX
    payload = prefix[28:] + formula_records
    new_len = len(payload)

    header = bytearray(prefix[:28])
    struct.pack_into('<I', header, 8, new_len)

    return bytes(header) + payload


def omml_to_mathtype_ole(omml_element: etree.Element) -> bytes:
    """
    Chuyển đổi một OMML XML element thành OLE Compound File Binary (4 streams:
    \\x01CompObj, \\x01Ole, \\x03ObjInfo, Equation Native) sẵn sàng nhúng vào Word.
    """
    mtef_bytes = omml_to_mtef(omml_element)
    return make_mathtype_ole(mtef_bytes)


def latex_to_mathtype_ole_offline(latex_str: str) -> bytes:
    """
    Chuyển trực tiếp từ chuỗi LaTeX sang OLE MathType 7 mà KHÔNG CẦN MS WORD / MATHTYPE.
    """
    from converter_xml import latex_to_omml
    omml_elem = latex_to_omml(latex_str)
    return omml_to_mathtype_ole(omml_elem)


if __name__ == "__main__":
    print("=== Testing omml_to_mtef module ===")
    from converter_xml import latex_to_omml

    test_cases = [
        r"\frac{a}{b} + \sqrt[3]{x}",
        r"\widehat{ACB} = \frac{1}{2}sd\overparen{AB}",
        r"\int_0^1 f(x) dx + \sum_{i=1}^n x_i",
        r"\begin{cases} x + y = 1 \\ 2x - y = 3 \end{cases}",
        r"\begin{matrix} a & b \\ c & d \end{matrix}",
        r"\lim_{x \to 0} \frac{\sin x}{x} = 1",
    ]

    for idx, latex in enumerate(test_cases, 1):
        try:
            omml = latex_to_omml(latex)
            ole_bytes = omml_to_mathtype_ole(omml)
            print(f"Test {idx}: {latex[:35]}... -> OLE OK ({len(ole_bytes)} bytes)")
        except Exception as e:
            print(f"Test {idx} FAILED: {latex} -> {e}")
            import traceback
            traceback.print_exc()

    print("=== All tests finished ===")