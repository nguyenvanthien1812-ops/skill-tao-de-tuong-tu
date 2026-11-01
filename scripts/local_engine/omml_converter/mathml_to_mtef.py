"""
Walk a MathML lxml element tree and produce MTEF binary equation content.

These bytes are the 'inner' equation records (CHAR, TMPL, etc.) that
mtef.build_mtef() wraps in the full MTEF stream header.
"""

from lxml import etree

from .mtef import (
    _GREEK,
    TF_FUNCTION,
    TF_LCGREEK,
    TF_NUMBER,
    TF_SYMBOL,
    TF_TEXT,
    TF_UCGREEK,
    TF_VARIABLE,
    _char,
    fraction,
    nroot_radical,
    sqrt_radical,
    subscript,
    subsuperscript,
    superscript,
)

_MML = "http://www.w3.org/1998/Math/MathML"

_GREEK_BY_CODEPOINT = {v: k for k, v in _GREEK.items()}

# Operator string → unicode codepoint (for common math symbols typed as text)
_OP_MAP = {
    "<=": 0x2264,  # ≤
    ">=": 0x2265,  # ≥
    "!=": 0x2260,  # ≠
    "->": 0x2192,  # →
    "<-": 0x2190,  # ←
    "...": 0x2026,  # …
    "∥": 0x2225,   # Parallel to (song song hai vạch đứng)
    "//": 0x2AFD,  # Slanted parallel (song song hai vạch xiên chuẩn SGK Việt Nam)
    "⫽": 0x2AFD,   # Double solidus operator
    "⊥": 0x22A5,   # Perpendicular (vuông góc)
    "⟂": 0x22A5,   # Perpendicular
    "|": 0x007C,   # ASCII vertical bar - renders as | in MathType Symbol font (0x7C is safe in all fonts)
    "∣": 0x007C,   # U+2223 divides → mapped to ASCII 0x007C for MathType compatibility
}


def _mml(tag):
    return f"{{{_MML}}}{tag}"


class MathmlEncoder:
    def encode(self, math_el) -> bytes:
        """Encode the content of a <math> element."""
        return self._encode_children(math_el)

    def _encode_children(self, node) -> bytes:
        out = b""
        for child in node:
            out += self._dispatch(child)
        return out

    def _dispatch(self, node) -> bytes:
        tag = etree.QName(node).localname
        handler = getattr(self, f"_enc_{tag}", self._enc_unknown)
        return handler(node)

    def _enc_unknown(self, node) -> bytes:
        return self._encode_children(node)

    # ── Leaf nodes ────────────────────────────────────────────────────────

    def _enc_mi(self, node) -> bytes:
        text = (node.text or "").strip()
        if not text:
            return b""
        # Check for Greek letters by Unicode codepoint
        if len(text) == 1 and ord(text) in _GREEK_BY_CODEPOINT:
            cp = ord(text)
            if 0x03B1 <= cp <= 0x03C9:  # lowercase Greek
                return _char(TF_LCGREEK, cp)
            if 0x0391 <= cp <= 0x03A9:  # uppercase Greek
                return _char(TF_UCGREEK, cp)
        # Multi-char mi = function name (hoặc đoạn thẳng hình học nếu viết hoa toàn bộ)
        if len(text) > 1:
            if text.isupper() and len(text) <= 4:
                # Đoạn thẳng hình học (AB, CD, BK, CH,...) -> mỗi ký tự là biến toán in nghiêng
                out = b""
                for ch in text:
                    out += _char(TF_VARIABLE, ord(ch))
                return out
            out = b""
            for ch in text:
                out += _char(TF_FUNCTION, ord(ch))
            return out
        return _char(TF_VARIABLE, ord(text))

    def _enc_mn(self, node) -> bytes:
        text = (node.text or "").strip()
        out = b""
        for ch in text:
            if ch.isdigit():
                out += _char(TF_NUMBER, ord(ch))
            elif ch in (".", ","):
                out += _char(TF_SYMBOL, ord(ch))
            else:
                out += _char(TF_VARIABLE, ord(ch))
        return out

    def _enc_mo(self, node) -> bytes:
        text = (node.text or "").strip()
        if not text:
            return b""
        if text in _OP_MAP:
            return _char(TF_SYMBOL, _OP_MAP[text])
        if text == "⁡":  # invisible function application
            return b""
        # Encode each character as a symbol
        out = b""
        for ch in text:
            out += _char(TF_SYMBOL, ord(ch))
        return out

    def _enc_mtext(self, node) -> bytes:
        text = (node.text or "").strip()
        out = b""
        for ch in text:
            out += _char(TF_TEXT, ord(ch))
        return out

    # ── Structural nodes ──────────────────────────────────────────────────

    def _enc_mrow(self, node) -> bytes:
        return self._encode_children(node)

    def _enc_math(self, node) -> bytes:
        return self._encode_children(node)

    def _enc_mfrac(self, node) -> bytes:
        children = list(node)
        num = self._dispatch(children[0]) if len(children) > 0 else b""
        den = self._dispatch(children[1]) if len(children) > 1 else b""
        return fraction(num, den)

    def _enc_msqrt(self, node) -> bytes:
        inner = self._encode_children(node)
        return sqrt_radical(inner)

    def _enc_mroot(self, node) -> bytes:
        children = list(node)
        rad = self._dispatch(children[0]) if len(children) > 0 else b""
        deg = self._dispatch(children[1]) if len(children) > 1 else b""
        return nroot_radical(deg, rad)

    def _enc_msub(self, node) -> bytes:
        children = list(node)
        base = self._dispatch(children[0]) if len(children) > 0 else b""
        sub = self._dispatch(children[1]) if len(children) > 1 else b""
        return base + subscript(sub)

    def _enc_msup(self, node) -> bytes:
        children = list(node)
        base = self._dispatch(children[0]) if len(children) > 0 else b""
        sup = self._dispatch(children[1]) if len(children) > 1 else b""
        return base + superscript(sup)

    def _enc_msubsup(self, node) -> bytes:
        children = list(node)
        base = self._dispatch(children[0]) if len(children) > 0 else b""
        sub = self._dispatch(children[1]) if len(children) > 1 else b""
        sup = self._dispatch(children[2]) if len(children) > 2 else b""
        return base + subsuperscript(sub, sup)

    def _enc_munder(self, node) -> bytes:
        children = list(node)
        base = self._dispatch(children[0]) if len(children) > 0 else b""
        under = self._dispatch(children[1]) if len(children) > 1 else b""
        # Represent as subscript-style limit
        return base + subscript(under)

    def _enc_mover(self, node) -> bytes:
        children = list(node)
        base = self._dispatch(children[0]) if len(children) > 0 else b""
        over = self._dispatch(children[1]) if len(children) > 1 else b""
        return base + superscript(over)

    def _enc_munderover(self, node) -> bytes:
        children = list(node)
        base = self._dispatch(children[0]) if len(children) > 0 else b""
        under = self._dispatch(children[1]) if len(children) > 1 else b""
        over = self._dispatch(children[2]) if len(children) > 2 else b""
        return base + subsuperscript(under, over)

    def _enc_mphantom(self, node) -> bytes:
        return b""  # phantom = invisible, skip

    # ── Table / matrix ────────────────────────────────────────────────────

    def _enc_mtable(self, node) -> bytes:
        # Flatten matrix to row-by-row, comma/semicolon separated
        out = b""
        rows = list(node)
        for i, mtr in enumerate(rows):
            if i > 0:
                out += _char(TF_SYMBOL, ord(";"))  # row separator
            cells = list(mtr)
            for j, mtd in enumerate(cells):
                if j > 0:
                    out += _char(TF_SYMBOL, ord(","))
                out += self._encode_children(mtd)
        return out

    def _enc_mtr(self, node) -> bytes:
        return self._encode_children(node)

    def _enc_mtd(self, node) -> bytes:
        return self._encode_children(node)


def mathml_to_mtef_bytes(math_el) -> bytes:
    """Convert a MathML <math> element to MTEF equation content bytes."""
    return MathmlEncoder().encode(math_el)
