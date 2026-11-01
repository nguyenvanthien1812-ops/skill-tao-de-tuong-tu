"""
MTEF 5.0 binary encoder.

Binary format verified by reverse-engineering fixture files from
https://github.com/jure/mathtype (MTEF parser Ruby gem).

Record sizes:
  END  (0x00): 1 byte  (no options byte)
  LINE (0x01): 2 bytes  type + options
  CHAR (0x02): 5 bytes  type + options + typeface_encoded + MTCode_lo + MTCode_hi
  TMPL (0x03): 5 bytes header  type + options + selector + variation + tmpl_opts
  SIZE (0x09): 4 bytes  type + 0x65(101) + size_lo + size_hi
  FULL (0x0a): 1 byte  (no options)
  SUB  (0x0b): 1 byte  (no options)
  SUB2 (0x0c): 1 byte  (no options)

TMPL selectors:
  0x0a = tmROOT  (radical/root)
  0x0b = tmFRACT (fraction)
  0x1b = tmSUB   (subscript; base precedes TMPL in parent LINE)
  0x1c = tmSUP   (superscript; base precedes TMPL in parent LINE)
  0x1d = tmSUBSUP (sub+sup; base precedes TMPL)

Typeface encoding: byte = actual_typeface + 128
  typeface 3 (variable/italic) → 0x83
  typeface 8 (numbers)         → 0x88
  typeface 6 (symbols/ops)     → 0x86
  typeface 4 (Greek lowercase)  → 0x84
  typeface 5 (Greek uppercase)  → 0x85
  typeface 2 (function names)   → 0x82
  typeface 1 (text, Arial)      → 0x81
"""

import struct

# ── Primitive records ──────────────────────────────────────────────────────────

END = b"\x00"
FULL = b"\x0a"
SUB = b"\x0b"
SUB2 = b"\x0c"


def _line(null: bool = False) -> bytes:
    return bytes([0x01, 0x01 if null else 0x00])


def _end_line() -> bytes:
    return END


def _char(typeface: int, unicode_val: int) -> bytes:
    return bytes([0x02, 0x00, typeface + 128, unicode_val & 0xFF, (unicode_val >> 8) & 0xFF])


def _size_display() -> bytes:
    """Explicit display point size (stored value 320 = display size -320 in spec)."""
    return bytes([0x09, 0x65, 0x40, 0x01])


def _tmpl_header(selector: int, variation: int = 0, tmpl_opts: int = 0) -> bytes:
    return bytes([0x03, 0x00, selector, variation, tmpl_opts])


# ── Typeface constants ─────────────────────────────────────────────────────────

TF_FUNCTION = 2  # sin, cos, log …
TF_VARIABLE = 3  # italic math variables
TF_LCGREEK = 4  # α β γ …
TF_UCGREEK = 5  # Α Β Γ …
TF_SYMBOL = 6  # +  −  =  ×  …
TF_VECTOR = 7  # bold
TF_NUMBER = 8  # 0–9
TF_TEXT = 1  # regular text (Arial in preamble)

# Greek letter name → Unicode codepoint
_GREEK = {
    "alpha": 0x03B1,
    "beta": 0x03B2,
    "gamma": 0x03B3,
    "delta": 0x03B4,
    "epsilon": 0x03B5,
    "zeta": 0x03B6,
    "eta": 0x03B7,
    "theta": 0x03B8,
    "iota": 0x03B9,
    "kappa": 0x03BA,
    "lambda": 0x03BB,
    "mu": 0x03BC,
    "nu": 0x03BD,
    "xi": 0x03BE,
    "pi": 0x03C0,
    "rho": 0x03C1,
    "sigma": 0x03C3,
    "tau": 0x03C4,
    "upsilon": 0x03C5,
    "phi": 0x03C6,
    "chi": 0x03C7,
    "psi": 0x03C8,
    "omega": 0x03C9,
    "Alpha": 0x0391,
    "Beta": 0x0392,
    "Gamma": 0x0393,
    "Delta": 0x0394,
    "Epsilon": 0x0395,
    "Zeta": 0x0396,
    "Eta": 0x0397,
    "Theta": 0x0398,
    "Lambda": 0x039B,
    "Mu": 0x039C,
    "Nu": 0x039D,
    "Xi": 0x039E,
    "Pi": 0x03A0,
    "Rho": 0x03A1,
    "Sigma": 0x03A3,
    "Tau": 0x03A4,
    "Phi": 0x03A6,
    "Chi": 0x03A7,
    "Psi": 0x03A8,
    "Omega": 0x03A9,
}

# Operators that should use the symbol typeface
_OPERATORS = set("+-=<>*/÷×·±∓∞∂∇∑∏∫√∧∨∩∪≤≥≠≈≡←→↑↓↔⟨⟩")


def _classify_char(text: str) -> tuple[int, int]:
    """Return (typeface, unicode_val) for a single character."""
    if not text:
        return TF_VARIABLE, 0x20
    ch = text[0]
    if ch.isdigit():
        return TF_NUMBER, ord(ch)
    if ch in _OPERATORS or ord(ch) > 0x2000:
        return TF_SYMBOL, ord(ch)
    if "a" <= ch <= "z" or "A" <= ch <= "Z":
        return TF_VARIABLE, ord(ch)
    return TF_SYMBOL, ord(ch)


def chars_from_text(text: str) -> bytes:
    """Encode a string as a sequence of CHAR records."""
    out = b""
    for ch in text:
        if ch == " ":
            continue
        tf, val = _classify_char(ch)
        out += _char(tf, val)
    return out


# ── Structural helpers ─────────────────────────────────────────────────────────


def fraction(num_bytes: bytes, den_bytes: bytes) -> bytes:
    """tmFRACT template: two slots (numerator / denominator)."""
    return (
        _tmpl_header(0x0B)  # tmFRACT
        + _line()
        + num_bytes
        + END  # slot 1: numerator
        + FULL  # reset size between slots
        + _line()
        + den_bytes
        + END  # slot 2: denominator
        + END  # end TMPL
    )


def sqrt_radical(rad_bytes: bytes) -> bytes:
    """tmROOT with variation 0 (square root, one slot)."""
    return (
        _tmpl_header(0x0A, variation=0)  # tmROOT, tvROOT_SQ
        + _line()
        + rad_bytes
        + END  # radicand slot
        + END  # end TMPL
    )


def nroot_radical(deg_bytes: bytes, rad_bytes: bytes) -> bytes:
    """tmROOT with variation 1 (nth root, two slots: degree + radicand)."""
    return (
        _tmpl_header(0x0A, variation=1)
        + _line()
        + deg_bytes
        + END
        + _line()
        + rad_bytes
        + END
        + END
    )


def subscript(sub_bytes: bytes) -> bytes:
    """tmSUB: base precedes this TMPL in parent LINE; one content slot + null slot."""
    return (
        FULL
        + _tmpl_header(0x1B)  # tmSUB
        + SUB  # size change inside
        + _line()
        + sub_bytes
        + END  # slot 1: subscript
        + _line(null=True)  # slot 2: null (superscript placeholder)
        + END  # end TMPL
    )


def superscript(sup_bytes: bytes) -> bytes:
    """tmSUP: base precedes this TMPL in parent LINE."""
    return (
        FULL
        + _tmpl_header(0x1C)  # tmSUP
        + SUB
        + _line()
        + sup_bytes
        + END
        + _line(null=True)
        + END
    )


def subsuperscript(sub_bytes: bytes, sup_bytes: bytes) -> bytes:
    """tmSUBSUP: base precedes this TMPL in parent LINE."""
    return (
        FULL
        + _tmpl_header(0x1D)
        + SUB
        + _line()
        + sub_bytes
        + END
        + _line()
        + sup_bytes
        + END
        + _line(null=True)
        + END
    )


# ── MTEF preamble ─────────────────────────────────────────────────────────────

# Fixed preamble bytes (body only, after the 12-byte MTEF header).
# Sourced from a verified MathType 5 Windows fixture (frac_sub.bin from
# https://github.com/jure/mathtype/tree/master/spec/fixtures/input/mathtype5).
# Contains: ENCODING_DEF, FONT_DEFs (Arial, Times New Roman, Symbol, MT Extra),
# EQN_PREFS, and colour/spacing tables.
_PREAMBLE_BODY = (
    b"\x13WinAllBasicCode"
    b"Pages\x00\x11\x05Arial\x00\x11\x05"
    b"Times New Roman\x00"
    b"\x11\x03Symbol\x00\x11\x04MT Ex"
    b"tra\x00\x12\x00\x08!\x0f(\xf2\x7fAP\xf4\x10"
    b"\x0fG_AP\xf2\x1f\x1eAP\xf4\x15\x0fA\x00\xf4"
    b"E\xf4%\xf4\x8fB_A\x00\xf4\x10\x0fC_A\x00"
    b"\xf4\x8fE\xf4*_H\xf4\x8fA\x00\xf4\x10\x0f@\xf4"
    b"\x8fA\x7fH\xf4\x10\x0fA*_D_E\xf4_E"
    b"\xf4_A\x0f\x0c\x01\x00\x01\x00\x02\x02\x03\x02\x03\x00\x03"
    b"\x00\x01\x01\x01\x00\x02\x00\x02\x00\x04\x00\x00"
)


def build_mtef(equation_bytes: bytes) -> bytes:
    """
    Wrap equation content bytes in a complete MTEF 5.0 stream.

    equation_bytes: output of the encode_* functions below (CHAR/TMPL records).
    Returns bytes ready to be placed in the 'Equation Native' OLE stream
    (after the 28-byte EQNOLEFILEHDR prefix).
    """
    header = bytes(
        [
            0x05,  # MTEF version 5
            0x01,  # platform: 1 = Windows
            0x00,  # product: 0 = MathType
            0x06,  # product version 6
            0x00,  # product subversion 0
            0x44,
            0x53,
            0x4D,
            0x54,
            0x36,
            0x00,  # app key "DSMT6\0"
            0x00,  # equation options: 0 = display/block
        ]
    )
    main_line = FULL + _line() + _size_display() + equation_bytes + END
    return header + _PREAMBLE_BODY + main_line


def make_equation_native(equation_bytes: bytes) -> bytes:
    """
    Build the complete 'Equation Native' OLE stream bytes:
    EQNOLEFILEHDR (28 bytes) + MTEF data.
    """
    mtef_data = build_mtef(equation_bytes)
    # EQNOLEFILEHDR: cbHdr(WORD) + version(DWORD) + cf(WORD) + cbObject(LONG) + reserved(16 bytes)
    header = struct.pack("<HIHI", 28, 0x00020000, 0, len(mtef_data)) + bytes(16)
    return header + mtef_data
