# -*- coding: utf-8 -*-
r"""
arc_symbol_builder.py

Xây dựng ký hiệu "cung tròn" (arc, vd cung AB) dạng MathType
Equation Native (MTEF) THẬT, dùng nguyên byte trích từ MathType 7.0 có sẵn
(không đi qua LibreOffice), đảm bảo:
  - Hiển thị đúng hình cung cong (không phải gạch thẳng, không phải chữ "frown").
  - Kích đúp mở được bằng MathType bình thường (không bị lỗi hình thoi đen "?").

BỐI CẢNH / LỊCH SỬ DEBUG (xem HANDOFF.md để biết đầy đủ quá trình):
  1) ``\overparen{AB}`` ban đầu bị đổi thành ``\overline{...}`` (StarMath) -> ra
     GẠCH NGANG THẲNG, không phải cung cong. Đã sửa trong latex_to_starmath.py.
  2) Thử dùng ký tự Unicode cung tròn (U+2312 ARC hoặc U+2322 FROWN) qua
     StarMath "stack { <ký_tự> # AB }" -> LibreOffice VẼ ĐÚNG (PNG đẹp), nhưng
     khi xuất MTEF v3 và mở bằng MathType THẬT trên Windows -> LỖI HÌNH THOI
     ĐEN "?" (ký tự không có trong font mà LibreOffice gán cho nó).
  3) Ép font qua StarMath / typeface index -> LibreOffice MTEF v3 KHÔNG có
     FONT_DEF "MT Extra".
  5) Người dùng tự chèn cung tròn qua nút Geometry trong MathType
     -> trích Doc1.doc (ABC) / Doc2.doc (AB) = byte MTEF v5 THẬT.
  6) Ký tự cung tròn THẬT: U+2322 FROWN + font "MT Extra" trong MTEF v5.

=> Giải pháp DUY NHẤT đã kiểm chứng: TÁI SỬ DỤNG nguyên byte thực từ
   MathType (build_arc_equation_native), chỉ thay CHAR record của nhãn.

ĐÃ KIỂM CHỨNG:
  - build_arc_equation_native("AB")  == byte thực Doc2.doc  (100% khớp)
  - build_arc_equation_native("ABC") khớp Doc1.doc (lệch timestamp nội bộ)
  - "MN","PQ","CD","XY" -> hiển thị + kích đúp OK trên MathType thật.
"""

from __future__ import annotations

import re
import struct
from typing import Optional

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

# ---------------------------------------------------------------------------
# CHAR record cho ký hiệu cung tròn: tag(02) + opts(00) + typeface(96) +
# charcode LE (22 23 = U+2322 FROWN) + embell(00).
# Typeface 0x96 lấy TỪ CHÍNH byte thực của MathType, tham chiếu font "MT Extra".
# ---------------------------------------------------------------------------
_ARC_CHAR_RECORD = bytes.fromhex("020096222300")

# Marker mở đầu phần "thân công thức" (LINE record), giữ nguyên từ byte thực.
_LINE_OPEN_MARKER = bytes.fromhex("0a01000300220000")
_NESTED_LINE_MARKER = bytes.fromhex("0100")

# Prefix đầy đủ (28-byte EQNOLEFILEHDR + header MTEF v5 + bảng tên font
# "DSMT7"/"WinAllBasicCodePages"/"Times New Roman"/"Symbol"/"Courier New"/
# "MT Extra" + bảng kích thước style + block size/record dẫn vào LINE)
# -- TRÍCH NGUYÊN VĂN từ Doc2.doc (công thức "cung AB").
#
# LƯU Ý: bản trước cắt prefix ngay sau "...410f0c" và bỏ mất 23 byte
# size/index block ngay trước LINE → selftest lệch 23 byte. Đã ghép đủ.
_PREFIX_HEX = (
    "1c0000000200c6c1dc00000000000000d855ba062ddf88000c003d06"
    "050100070844534d543700001357696e416c6c4261736963436f6465"
    "506167657300110554696d6573204e657720526f6d616e0011035379"
    "6d626f6c001105436f7572696572204e65770011044d542045787472"
    "6100120008212f458f442f4150f4100f475f4150f21f1e4150f4150f"
    "4100f445f425f48f425f4100f4100f435f4100f48f45f42a5f48f48f"
    "4100f4100f40f48f417f48f4100f412a5f445f45f45f45f45f410f0c"
    # 23-byte size/index block (có trong Doc2.doc, nằm ngay trước LINE)
    "0100010001020202020002000101010003000100040000"
)
_PREFIX = bytes.fromhex(_PREFIX_HEX)

# Marker tàng hình Left-to-Right Mark dùng trong StarMath để nhận diện overparen.
# latex_to_starmath chèn U+200E vào nội dung overline/stack tương ứng.
ARC_MARKER_CHAR = "\u200e"  # LRM
ARC_MARKER = ARC_MARKER_CHAR


def build_arc_equation_native(base_letters: str) -> bytes:
    """Trả về bytes của 1 "Equation Native" stream (MTEF v5 THẬT) cho ký hiệu
    cung tròn trên base_letters, vd build_arc_equation_native("AB").

    - base_letters: chỉ hỗ trợ ký tự ASCII chữ/số (A-Z, a-z, 0-9).
    - Kết quả: dùng ĐỂ THAY thế trực tiếp vào stream "Equation Native" của
      1 object MathType (Equation.DSMT4) trong file .doc/.docx embedding.
    """
    if not (base_letters and all(c.isalnum() and c.isascii() for c in base_letters)):
        raise ValueError(
            "base_letters chỉ hỗ trợ ký tự ASCII chữ/số, vd 'AB', 'MN', 'ABC'"
        )

    tail = bytearray()
    tail += _LINE_OPEN_MARKER
    tail += _NESTED_LINE_MARKER
    for ch in base_letters:
        # CHAR record: tag(02) opts(00) typeface(83 = "variable")
        # charcode(1 byte ASCII) embell(00).
        tail += bytes([0x02, 0x00, 0x83, ord(ch), 0x00])
    tail += bytes([0x00])  # end-of-row (dòng chữ cái nhãn)
    tail += _ARC_CHAR_RECORD  # ký tự cung tròn (FROWN, font MT Extra)
    tail += bytes([0x00, 0x00])  # 2 marker đóng (PILE + biểu thức)

    payload = _PREFIX[28:] + bytes(tail)  # mọi thứ SAU 28-byte EQNOLEFILEHDR
    new_len = len(payload)

    header = bytearray(_PREFIX[:28])
    header[8:12] = struct.pack("<I", new_len)  # cập nhật trường độ dài payload

    return bytes(header) + payload


# Các lệnh LaTeX được coi là "cung tròn"
_OVERPAREN_CMDS = (
    r"overparen",
    r"wideparen",
    r"overarc",
    r"arc",
)


def extract_pure_arc_base(latex: str) -> Optional[str]:
    """Nếu latex CHỈ là một lệnh cung tròn bọc nhãn ASCII, trả về nhãn.

    Ví dụ chấp nhận:
      overparen{AB}   \\overparen{MN}   \\wideparen{ABC}
      $\\overparen{PQ}$  (đã strip $ ở ngoài)

    Trả về None nếu không phải cung thuần (có thêm toán khác) hoặc nhãn không hợp lệ.
    """
    if not latex:
        return None
    s = latex.strip()
    # bỏ $ bọc ngoài nếu còn
    if s.startswith("$$") and s.endswith("$$"):
        s = s[2:-2].strip()
    elif s.startswith("$") and s.endswith("$"):
        s = s[1:-1].strip()

    # bỏ \displaystyle / \textstyle thừa ở ngoài
    s = re.sub(r"^\\(?:displaystyle|textstyle|scriptstyle)\s*", "", s)

    cmd_alt = "|".join(_OVERPAREN_CMDS)
    # \cmd{BASE} hoặc \cmd {BASE}
    m = re.fullmatch(
        rf"\\?({cmd_alt})\s*\{{([A-Za-z0-9]+)\}}",
        s,
    )
    if not m:
        # cho phép thêm khoảng trắng cuối
        m = re.fullmatch(
            rf"\\?({cmd_alt})\s*\{{([A-Za-z0-9]+)\}}\s*",
            s,
        )
    if not m:
        return None
    base = m.group(2)
    if not base or not all(c.isalnum() and c.isascii() for c in base):
        return None
    return base



_OVERPAREN_RE = re.compile(
    r"\\(?:overparen|wideparen|overarc)\s*\{([A-Za-z0-9]+)\}"
)

def parse_arc_latex_expression(latex: str):
    """Tách latex có một/nhiều cung thành token để vẽ preview.

    Ví dụ:
      \\overparen{AB}              -> [('arc','AB')]
      \\overparen{A}+\\overparen{B} -> [('arc','A'), ('op','+'), ('arc','B')]
      \\overparen{A}+\\overparen{B}=1 -> [('arc','A'), ('op','+'), ('arc','B'), ('op','='), ('text','1')]  (text thô)

    Trả None nếu không có overparen nào.
    """
    if not latex:
        return None
    s = latex.strip()
    if s.startswith("$$") and s.endswith("$$"):
        s = s[2:-2].strip()
    elif s.startswith("$") and s.endswith("$"):
        s = s[1:-1].strip()
    s = re.sub(r"^\\(?:displaystyle|textstyle|scriptstyle)\s*", "", s)

    if not _OVERPAREN_RE.search(s):
        return None

    tokens = []
    pos = 0
    for m in _OVERPAREN_RE.finditer(s):
        gap = s[pos:m.start()]
        # tách operator/text trong gap
        if gap.strip():
            # giữ nguyên các ký tự toán phổ biến, bỏ khoảng trắng thừa
            g = gap.strip()
            # có thể là + - = , ; ( ) ...
            tokens.append(("op", g))
        tokens.append(("arc", m.group(1)))
        pos = m.end()
    tail = s[pos:].strip()
    if tail:
        tokens.append(("op", tail))

    # phải có ít nhất 1 arc
    if not any(t[0] == "arc" for t in tokens):
        return None
    return tokens



def split_latex_by_arcs(latex: str):
    """Tách 1 công thức LaTeX thành các phần arc / math xen kẽ.

    Mục tiêu: công thức LỒNG như
      \\widehat{ACB}=\\frac{1}{2}sd\\overparen{AB}
    → [
        ("math", "\\widehat{ACB}=\\frac{1}{2}sd"),
        ("arc",  "AB"),
      ]

    Pure arc \\overparen{AB} → [("arc","AB")]
    Không có arc → [("math", latex)] (1 phần)

    Mỗi phần "arc" sẽ thành OLE MathType MTEF thật + PNG đẹp.
    Mỗi phần "math" đi pipeline LibreOffice bình thường (không dính U+2322/LRM).
    """
    if not latex:
        return []
    s = latex.strip()
    if s.startswith("$$") and s.endswith("$$"):
        s = s[2:-2].strip()
    elif s.startswith("$") and s.endswith("$"):
        s = s[1:-1].strip()
    s = re.sub(r"^\\(?:displaystyle|textstyle|scriptstyle)\s*", "", s)

    parts = []
    pos = 0
    for m in _OVERPAREN_RE.finditer(s):
        gap = s[pos:m.start()]
        if gap.strip():
            # giữ gap (kể cả khoảng trắng biên tối thiểu)
            parts.append(("math", gap))
        parts.append(("arc", m.group(1)))
        pos = m.end()
    tail = s[pos:]
    if tail.strip():
        parts.append(("math", tail))
    if not parts:
        parts = [("math", s)]
    # Gộp math rỗng
    cleaned = []
    for kind, val in parts:
        if kind == "math" and not val.strip():
            continue
        cleaned.append((kind, val))
    return cleaned or [("math", s)]


def is_arc_containing_latex(latex: str) -> bool:
    """True nếu latex chứa ít nhất một \\overparen/\\wideparen/\\overarc."""
    if not latex:
        return False
    return bool(_OVERPAREN_RE.search(latex))


def extract_arc_base_from_starmath(starmath: str) -> Optional[str]:
    """Nhận diện StarMath đã được đánh dấu cung (có U+200E) và lấy nhãn ASCII.

    Các dạng latex_to_starmath sinh ra:
      - {AB} csup size*0.9 {⌢ LRM}   (ưu tiên — cung sát chữ)
      - stack{⌒ # AB} / stack{⌢ # AB}
      - overline{ LRM AB }
    """
    if not starmath or ARC_MARKER_CHAR not in starmath:
        return None
    s = starmath.replace(ARC_MARKER_CHAR, "")
    # {BASE} csup ...
    m = re.search(
        r"\{\s*([A-Za-z0-9]+)\s*\}\s*csup\b",
        s,
    )
    if m:
        return m.group(1)
    # BASE csup (không ngoặc, 1 token)
    m = re.search(
        r"\b([A-Za-z0-9]+)\s+csup\b",
        s,
    )
    if m:
        return m.group(1)
    # stack{ <symbol> # BASE }
    m = re.search(
        r"stack\s*\{\s*[^#]*#\s*([A-Za-z0-9]+)\s*\}",
        s,
    )
    if m:
        return m.group(1)
    # overline{ BASE } / widebar{ BASE }
    m = re.search(
        r"(?:overline|widebar|bar)\s*\{\s*([A-Za-z0-9]+)\s*\}",
        s,
    )
    if m:
        return m.group(1)
    m = re.search(r"\b([A-Za-z0-9]{1,8})\b", s)
    if m:
        return m.group(1)
    return None


def is_pure_arc_starmath(starmath: str) -> bool:
    """True nếu StarMath chỉ là MỘT cung tròn thuần (không + x, không 2 cung)."""
    if not starmath or ARC_MARKER_CHAR not in starmath:
        return False
    s = starmath.strip()
    # {AB} csup size*0.9 {⌢ LRM}
    if re.fullmatch(
        r"\{\s*[A-Za-z0-9]+\s*\}\s*csup(?:\s+size\*[0-9.]+)?\s*\{[^}]*\u200e[^}]*\}",
        s,
    ):
        return True
    # stack form (bản cũ)
    if re.fullmatch(
        r"stack\s*\{\s*[^#]*\u200e?\s*#\s*[A-Za-z0-9]+\s*\}",
        s,
    ):
        return True
    return False


def is_arc_starmath(starmath: str) -> bool:
    """True nếu StarMath mang marker cung tròn."""
    return bool(starmath) and ARC_MARKER_CHAR in starmath


def selftest() -> None:
    """Kiểm chứng với byte thực đã trích từ Doc2.doc (AB)."""
    real_ab_hex = (
        "1c0000000200c6c1dc00000000000000d855ba062ddf88000c003d06050100"
        "070844534d543700001357696e416c6c4261736963436f6465506167657300"
        "110554696d6573204e657720526f6d616e00110353796d626f6c001105436f"
        "7572696572204e65770011044d5420457874726100120008212f458f442f41"
        "50f4100f475f4150f21f1e4150f4150f4100f445f425f48f425f4100f4100f"
        "435f4100f48f45f42a5f48f48f4100f4100f40f48f417f48f4100f412a5f44"
        "5f45f45f45f45f410f0c01000100010202020200020001010100030001000"
        "400000a01000300220000010002008341000200834200000200962223000000"
    )
    real_ab = bytes.fromhex(real_ab_hex)
    built_ab = build_arc_equation_native("AB")
    assert built_ab == real_ab, (
        f"MISMATCH với byte thực AB đã trích xuất! "
        f"built={len(built_ab)} real={len(real_ab)}"
    )
    print("OK: build_arc_equation_native('AB') khớp 100% với byte MathType thực.")

    built_mn = build_arc_equation_native("MN")
    assert len(built_mn) == len(real_ab)
    print("OK: build_arc_equation_native('MN') sinh đúng độ dài.")

    built_abc = build_arc_equation_native("ABC")
    # ABC = AB + 1 CHAR record (5 byte)
    assert len(built_abc) == len(real_ab) + 5
    print(
        "OK: build_arc_equation_native('ABC') độ dài =",
        len(built_abc),
        "(AB + 1 CHAR).",
    )

    assert extract_pure_arc_base(r"\overparen{AB}") == "AB"
    assert extract_pure_arc_base(r"\wideparen{MN}") == "MN"
    assert extract_pure_arc_base(r"\overparen{AB} + 1") is None
    assert extract_arc_base_from_starmath("stack{⌒ \u200e # XY}") == "XY"
    assert extract_arc_base_from_starmath("{XY} csup size*0.9 {⌢\u200e}") == "XY"
    assert parse_arc_latex_expression(r"\overparen{A}+\overparen{B}") == [
        ("arc", "A"), ("op", "+"), ("arc", "B")
    ]
    assert is_pure_arc_starmath("{AB} csup size*0.9 {⌢\u200e}")
    assert not is_pure_arc_starmath("{A} csup size*0.9 {⌢\u200e} + {B} csup size*0.9 {⌢\u200e}")
    assert split_latex_by_arcs(r"\overparen{AB}") == [("arc", "AB")]
    sp = split_latex_by_arcs(r"\widehat{ACB}=\frac{1}{2}sd\overparen{AB}")
    assert sp[-1] == ("arc", "AB") and sp[0][0] == "math"
    print("OK: extract_pure_arc_base / extract_arc_base_from_starmath / split.")


if __name__ == "__main__":
    selftest()