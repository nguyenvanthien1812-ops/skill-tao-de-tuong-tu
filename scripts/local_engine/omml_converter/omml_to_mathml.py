"""
Pure-Python OMML (Office Open XML Math) → MathML converter.

Handles the most common OMML elements based on the OOXML spec (Ecma-376 Part 3).
Returns an lxml Element tree rooted at <math>.
"""

from lxml import etree

_M = "http://schemas.openxmlformats.org/officeDocument/2006/math"
_W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
_MATHML_NS = "http://www.w3.org/1998/Math/MathML"

_OPS = set("+-=<>*/÷×·±∓∞∂∇∑∏∫√∧∨∩∪≤≥≠≈≡←→↑↓↔⟨⟩(),.:;!?|∣∥⫽⊥⟂")

# Common operator aliases encoded in OMML text
_OP_ALIASES = {
    "⋅": "·",  # dot operator
    "−": "−",  # minus sign
    "×": "×",
    "÷": "÷",
    "≤": "≤",
    "≥": "≥",
    "≠": "≠",
    "≈": "≈",
    "≡": "≡",
    "//": "⫽", # Slanted parallel
}


def _m(tag):
    return f"{{{_M}}}{tag}"


def _m_val(node, child_tag: str, default=None):
    """Read the m:val attribute from a child element like <m:sty m:val="p"/>."""
    child = node.find(_m(child_tag))
    if child is None:
        return default
    return child.get(_m("val"), default)


def _math_el(tag, *children, **attribs):
    el = etree.Element(f"{{{_MATHML_NS}}}{tag}", **attribs)
    for ch in children:
        if ch is not None:
            el.append(ch)
    return el


def _text_el(tag, text):
    el = etree.Element(f"{{{_MATHML_NS}}}{tag}")
    el.text = text or ""
    return el


def _is_number(s: str) -> bool:
    try:
        float(s.replace(",", "."))
        return True
    except (ValueError, AttributeError):
        return False


def _is_operator(s: str) -> bool:
    return bool(s) and (s in ("//", "⫽") or all(c in _OPS or c in _OP_ALIASES for c in s))


def _text_node(text: str):
    """Return <mi>, <mn>, or <mo> (or list of elements) for a text string."""
    t = (text or "").strip()
    if not t:
        return None
    if _is_number(t):
        return _text_el("mn", t)
    if _is_operator(t):
        return _text_el("mo", _OP_ALIASES.get(t, t))
    # Tự động tách nếu chuỗi chứa toán tử xen lẫn chữ cái (như BK∥CH, BK // CH, CH ⊥ AB)
    import re
    op_chars = ''.join(re.escape(c) for c in _OPS if c not in ('(', ')', '[', ']', '{', '}'))
    pattern = rf'(//|[{op_chars}]|\d+(?:[.,]\d+)?|[a-zA-Z]+|\s+|.)'
    tokens = [m.group() for m in re.finditer(pattern, t) if m.group().strip()]
    if len(tokens) > 1:
        res = []
        for tok in tokens:
            node = _text_node(tok)
            if node is not None:
                if isinstance(node, list):
                    res.extend(node)
                else:
                    res.append(node)
        return res
    return _text_el("mi", t)


def _get_text(node) -> str:
    """Extract all text from an OMML element and its m:t children."""
    parts = []
    for t in node.iter(_m("t")):
        if t.text:
            parts.append(t.text)
    return "".join(parts)


def _children_to_mrow(node, converter):
    """Convert all math children of node and wrap in <mrow>."""
    mrow = etree.Element(f"{{{_MATHML_NS}}}mrow")
    for child in node:
        result = converter(child)
        if result is not None:
            if isinstance(result, list):
                for r in result:
                    mrow.append(r)
            else:
                mrow.append(result)
    return mrow


def _unwrap_mrow(el):
    """If mrow has exactly one child, return that child; otherwise return mrow."""
    children = list(el)
    if len(children) == 1:
        return children[0]
    return el


class OmmlConverter:
    def convert(self, omml_root) -> etree._Element:
        """Convert an m:oMath element to a <math> MathML element."""
        math = etree.Element(f"{{{_MATHML_NS}}}math")
        mrow = etree.SubElement(math, f"{{{_MATHML_NS}}}mrow")
        for child in omml_root:
            result = self._dispatch(child)
            if result is not None:
                if isinstance(result, list):
                    for r in result:
                        mrow.append(r)
                else:
                    mrow.append(result)
        return math

    def _dispatch(self, node):
        tag = etree.QName(node).localname
        handler = getattr(self, f"_handle_{tag}", self._handle_unknown)
        return handler(node)

    # ── Ignored / pass-through containers ──────────────────────────────────

    def _handle_unknown(self, node):
        return None

    def _handle_oMath(self, node):
        return _children_to_mrow(node, self._dispatch)

    def _handle_oMathPara(self, node):
        return _children_to_mrow(node, self._dispatch)

    # ── Run: m:r → m:t ────────────────────────────────────────────────────

    def _handle_r(self, node):
        text = _get_text(node)
        if not text:
            return None
        rPr = node.find(_m("rPr"))
        sty = _m_val(rPr, "sty") if rPr is not None else None
        if sty == "p":
            return _text_el("mtext", text)
        el = _text_node(text)
        if el is None:
            el = _text_el("mi", text)
        if sty in ("b", "bi"):
            el.set("mathvariant", "bold")
        return el

    def _handle_t(self, node):
        return _text_node(node.text or "")

    # ── Fraction: m:f ─────────────────────────────────────────────────────

    def _handle_f(self, node):
        num_node = node.find(_m("num"))
        den_node = node.find(_m("den"))
        num = (
            _children_to_mrow(num_node, self._dispatch)
            if num_node is not None
            else etree.Element(f"{{{_MATHML_NS}}}mrow")
        )
        den = (
            _children_to_mrow(den_node, self._dispatch)
            if den_node is not None
            else etree.Element(f"{{{_MATHML_NS}}}mrow")
        )
        fPr = node.find(_m("fPr"))
        ftype = _m_val(fPr, "type") if fPr is not None else None
        if ftype == "lin":
            mrow = etree.Element(f"{{{_MATHML_NS}}}mrow")
            mrow.append(_unwrap_mrow(num))
            mrow.append(_text_el("mo", "/"))
            mrow.append(_unwrap_mrow(den))
            return mrow
        if ftype in ("noBar", "skw"):
            mfrac = _math_el("mfrac", _unwrap_mrow(num), _unwrap_mrow(den))
            mfrac.set("linethickness", "0")
            return mfrac
        return _math_el("mfrac", _unwrap_mrow(num), _unwrap_mrow(den))

    # ── Radical: m:rad ────────────────────────────────────────────────────

    def _handle_rad(self, node):
        deg_node = node.find(_m("deg"))
        e_node = node.find(_m("e"))
        rad = (
            _children_to_mrow(e_node, self._dispatch)
            if e_node is not None
            else etree.Element(f"{{{_MATHML_NS}}}mrow")
        )
        if deg_node is not None and len(deg_node) > 0:
            deg = _children_to_mrow(deg_node, self._dispatch)
            return _math_el("mroot", _unwrap_mrow(rad), _unwrap_mrow(deg))
        return _math_el("msqrt", _unwrap_mrow(rad))

    # ── Scripts ────────────────────────────────────────────────────────────

    def _handle_sSub(self, node):
        base = self._get_e(node)
        sub = self._get_sub(node)
        return _math_el("msub", base, sub)

    def _handle_sSup(self, node):
        base = self._get_e(node)
        sup = self._get_sup(node)
        return _math_el("msup", base, sup)

    def _handle_sSubSup(self, node):
        base = self._get_e(node)
        sub = self._get_sub(node)
        sup = self._get_sup(node)
        return _math_el("msubsup", base, sub, sup)

    def _handle_limLow(self, node):
        e = self._get_e(node)
        lim = (
            _children_to_mrow(node.find(_m("lim")), self._dispatch)
            if node.find(_m("lim")) is not None
            else etree.Element(f"{{{_MATHML_NS}}}mrow")
        )
        return _math_el("munder", e, _unwrap_mrow(lim))

    def _handle_limUpp(self, node):
        e = self._get_e(node)
        lim = (
            _children_to_mrow(node.find(_m("lim")), self._dispatch)
            if node.find(_m("lim")) is not None
            else etree.Element(f"{{{_MATHML_NS}}}mrow")
        )
        return _math_el("mover", e, _unwrap_mrow(lim))

    # ── Delimiter: m:d ────────────────────────────────────────────────────

    def _handle_d(self, node):
        dPr = node.find(_m("dPr"))
        beg = _m_val(dPr, "begChr", "(") if dPr is not None else "("
        end = _m_val(dPr, "endChr", ")") if dPr is not None else ")"
        sep = _m_val(dPr, "sepChr", "") if dPr is not None else ""
        mrow = etree.Element(f"{{{_MATHML_NS}}}mrow")
        if beg:
            mrow.append(_text_el("mo", beg))
        first = True
        for e_node in node.findall(_m("e")):
            if not first and sep:
                mrow.append(_text_el("mo", sep))
            first = False
            inner = _children_to_mrow(e_node, self._dispatch)
            for ch in list(inner):
                mrow.append(ch)
        if end:
            mrow.append(_text_el("mo", end))
        return mrow

    # ── Function: m:func ──────────────────────────────────────────────────

    def _handle_func(self, node):
        fname = node.find(_m("fName"))
        e_node = node.find(_m("e"))
        mrow = etree.Element(f"{{{_MATHML_NS}}}mrow")
        if fname is not None:
            inner = _children_to_mrow(fname, self._dispatch)
            for ch in list(inner):
                mrow.append(ch)
        mrow.append(_text_el("mo", "⁡"))  # invisible function application
        if e_node is not None:
            inner = _children_to_mrow(e_node, self._dispatch)
            mrow.append(_unwrap_mrow(inner))
        return mrow

    # ── N-ary operator: m:nary ────────────────────────────────────────────

    def _handle_nary(self, node):
        nPr = node.find(_m("naryPr"))
        op_char = _m_val(nPr, "chr", "∑") if nPr is not None else "∑"
        sub_node = node.find(_m("sub"))
        sup_node = node.find(_m("sup"))
        e_node = node.find(_m("e"))
        op_el = _text_el("mo", op_char)
        base = (
            _children_to_mrow(e_node, self._dispatch)
            if e_node is not None
            else etree.Element(f"{{{_MATHML_NS}}}mrow")
        )
        if sub_node is not None and sup_node is not None:
            lo = _children_to_mrow(sub_node, self._dispatch)
            hi = _children_to_mrow(sup_node, self._dispatch)
            op_with_limits = _math_el("munderover", op_el, _unwrap_mrow(lo), _unwrap_mrow(hi))
        elif sub_node is not None:
            lo = _children_to_mrow(sub_node, self._dispatch)
            op_with_limits = _math_el("munder", op_el, _unwrap_mrow(lo))
        elif sup_node is not None:
            hi = _children_to_mrow(sup_node, self._dispatch)
            op_with_limits = _math_el("mover", op_el, _unwrap_mrow(hi))
        else:
            op_with_limits = op_el
        mrow = etree.Element(f"{{{_MATHML_NS}}}mrow")
        mrow.append(op_with_limits)
        for ch in list(base):
            mrow.append(ch)
        return mrow

    # ── Accent: m:acc ─────────────────────────────────────────────────────

    def _handle_acc(self, node):
        accPr = node.find(_m("accPr"))
        acc_char = _m_val(accPr, "chr", "^") if accPr is not None else "^"
        e_node = node.find(_m("e"))
        base = (
            _children_to_mrow(e_node, self._dispatch)
            if e_node is not None
            else etree.Element(f"{{{_MATHML_NS}}}mrow")
        )
        return _math_el("mover", _unwrap_mrow(base), _text_el("mo", acc_char))

    # ── Bar: m:bar ────────────────────────────────────────────────────────

    def _handle_bar(self, node):
        barPr = node.find(_m("barPr"))
        pos = _m_val(barPr, "pos", "top") if barPr is not None else "top"
        e_node = node.find(_m("e"))
        base = (
            _children_to_mrow(e_node, self._dispatch)
            if e_node is not None
            else etree.Element(f"{{{_MATHML_NS}}}mrow")
        )
        bar = _text_el("mo", "¯")  # macron
        if pos == "bot":
            return _math_el("munder", _unwrap_mrow(base), bar)
        return _math_el("mover", _unwrap_mrow(base), bar)

    # ── Group char: m:groupChr ────────────────────────────────────────────

    def _handle_groupChr(self, node):
        gPr = node.find(_m("groupChrPr"))
        chr_text = _m_val(gPr, "chr", "⏟") if gPr is not None else "⏟"
        pos = _m_val(gPr, "pos", "bot") if gPr is not None else "bot"
        e_node = node.find(_m("e"))
        base = (
            _children_to_mrow(e_node, self._dispatch)
            if e_node is not None
            else etree.Element(f"{{{_MATHML_NS}}}mrow")
        )
        gch = _text_el("mo", chr_text or "⏟")
        if pos == "top":
            return _math_el("mover", _unwrap_mrow(base), gch)
        return _math_el("munder", _unwrap_mrow(base), gch)

    # ── Matrix: m:m ───────────────────────────────────────────────────────

    def _handle_m(self, node):
        mtable = etree.Element(f"{{{_MATHML_NS}}}mtable")
        for mr in node.findall(_m("mr")):
            mtr = etree.SubElement(mtable, f"{{{_MATHML_NS}}}mtr")
            for mc in mr.findall(_m("mc")):
                e_node = mc.find(_m("e"))
                mtd = etree.SubElement(mtr, f"{{{_MATHML_NS}}}mtd")
                if e_node is not None:
                    inner = _children_to_mrow(e_node, self._dispatch)
                    for ch in list(inner):
                        mtd.append(ch)
        return mtable

    # ── Equation array: m:eqArr ───────────────────────────────────────────

    def _handle_eqArr(self, node):
        mtable = etree.Element(f"{{{_MATHML_NS}}}mtable")
        for e_node in node.findall(_m("e")):
            mtr = etree.SubElement(mtable, f"{{{_MATHML_NS}}}mtr")
            mtd = etree.SubElement(mtr, f"{{{_MATHML_NS}}}mtd")
            inner = _children_to_mrow(e_node, self._dispatch)
            for ch in list(inner):
                mtd.append(ch)
        return mtable

    # ── Phantom: m:phant ──────────────────────────────────────────────────

    def _handle_phant(self, node):
        e_node = node.find(_m("e"))
        if e_node is None:
            return None
        inner = _children_to_mrow(e_node, self._dispatch)
        return _math_el("mphantom", _unwrap_mrow(inner))

    # ── Box / border box ──────────────────────────────────────────────────

    def _handle_box(self, node):
        e_node = node.find(_m("e"))
        return _children_to_mrow(e_node, self._dispatch) if e_node is not None else None

    def _handle_borderBox(self, node):
        e_node = node.find(_m("e"))
        return _children_to_mrow(e_node, self._dispatch) if e_node is not None else None

    # ── Helpers ───────────────────────────────────────────────────────────

    def _get_e(self, node) -> etree._Element:
        e = node.find(_m("e"))
        if e is None:
            return etree.Element(f"{{{_MATHML_NS}}}mrow")
        inner = _children_to_mrow(e, self._dispatch)
        return _unwrap_mrow(inner)

    def _get_sub(self, node) -> etree._Element:
        s = node.find(_m("sub"))
        if s is None:
            return etree.Element(f"{{{_MATHML_NS}}}mrow")
        inner = _children_to_mrow(s, self._dispatch)
        return _unwrap_mrow(inner)

    def _get_sup(self, node) -> etree._Element:
        s = node.find(_m("sup"))
        if s is None:
            return etree.Element(f"{{{_MATHML_NS}}}mrow")
        inner = _children_to_mrow(s, self._dispatch)
        return _unwrap_mrow(inner)


def omml_to_mathml(omml_element) -> etree._Element:
    """
    Convert an m:oMath lxml element to a MathML <math> element.
    """
    return OmmlConverter().convert(omml_element)
