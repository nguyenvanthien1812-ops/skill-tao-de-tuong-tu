r"""
latex_to_starmath.py
Chuyển một biểu thức LaTeX sang cú pháp StarMath (ngôn ngữ công thức LibreOffice Math).
Đây là bước trung gian: StarMath -> (LibreOffice Math) -> OLE MathType (MTEF) thật.

Phạm vi hỗ trợ (đủ dùng cho phần lớn công thức phổ thông/đại học):
  - \frac, \dfrac, \tfrac, \cfrac, \sqrt, \sqrt[n]{}, ^ và _ (kể cả không có {})
  - Các phép toán/quan hệ thường gặp: \pm \mp \times \div \cdot \leq \geq \neq
    \approx \equiv \in \subset \cup \cap \mid \iff \implies \impliedby ...
  - Chữ Hy Lạp: \alpha ... \omega, \Gamma ... \Omega
  - \sum \int \iint \prod \lim với cận trên/dưới (_{}^{})
  - Các hàm số chuẩn: sin cos tan log ln exp lim max min det ...
  - \left ... \right và \big \Big \bigg \Bigg (cùng biến thể l/r) với các dấu
    ngoặc ( ) [ ] \{ \} | .
  - \text{}, \mathrm{}, \mathbf{}, \vec{}, \hat{}, \overline{}, \underline{},
    \boxed{}, \pmod{}, \bmod
  - \overset{top}{base}: nhận diện các "top" phổ biến (\rightarrow, \hat,
    \tilde, \bar...) và ánh xạ sang đúng lệnh accent StarMath tương ứng
    (vd \overset{\rightarrow}{OD} -> vector OD có mũi tên, không còn lộ
    chữ "overset" ra ngoài như bản cũ)
  - Hệ phương trình / hệ điều kiện dạng \left\{\begin{array}{l} ... \end{array}\right.
  - \begin{cases}, \begin{matrix}, \begin{pmatrix}/\begin{bmatrix}/\begin{vmatrix}

KHÔNG hỗ trợ đầy đủ: môi trường align nhiều dòng có căn chỉnh theo cột (&),
macro tự định nghĩa, tikz, một số ký hiệu hiếm. Với các trường hợp đó, hãy
kiểm tra lại bằng mắt (pipeline có sẵn bước render ra ảnh để xem trước).
Với lệnh LaTeX không nằm trong danh sách trên, script sẽ giữ nguyên TÊN LỆNH
dưới dạng chữ thô trong công thức xuất ra (để người dùng dễ phát hiện và tự
bổ sung) — nếu thấy chữ tiếng Anh lạ (không phải biến số) lẫn trong công thức
đã build, đó là dấu hiệu cần bổ sung lệnh đó vào script này.
"""

import re
import unicodedata

GREEK_LOWER = [
    "alpha", "beta", "gamma", "delta", "epsilon", "varepsilon", "zeta", "eta",
    "theta", "vartheta", "iota", "kappa", "lambda", "mu", "nu", "xi",
    "omicron", "pi", "varpi", "rho", "varrho", "sigma", "varsigma", "tau",
    "upsilon", "phi", "varphi", "chi", "psi", "omega",
]
GREEK_UPPER = [
    "Gamma", "Delta", "Theta", "Lambda", "Xi", "Pi", "Sigma", "Upsilon",
    "Phi", "Psi", "Omega",
]

SYMBOL_MAP = {
    "pm": "+-", "mp": "-+", "times": "times", "div": "div", "cdot": ".",
    "ast": "*", "circ": "circ", "oplus": "oplus", "otimes": "otimes",
    "leq": "<=", "le": "<=", "geq": ">=", "ge": ">=", "neq": "<>", "ne": "<>",
    "approx": "approx", "equiv": "equiv", "sim": "sim", "simeq": "simeq",
    "cong": "cong", "propto": "prop",
    "in": "in", "notin": "notin",
    "subset": "subset", "subseteq": "subseteq",
    "supset": "supset", "supseteq": "supseteq",
    "cup": "union", "cap": "intersection", "setminus": "setminus",
    "emptyset": "emptyset", "varnothing": "emptyset",
    "forall": "forall", "exists": "exists",
    "nabla": "nabla", "partial": "partial", "infty": "infinity",
    "rightarrow": "rightarrow", "to": "rightarrow", "leftarrow": "leftarrow",
    "gets": "leftarrow", "leftrightarrow": "leftrightarrow",
    "Rightarrow": "drarrow", "Leftarrow": "dlarrow",
    "Leftrightarrow": "dlrarrow",
    "cdots": "dotsaxis", "ldots": "dotslow", "dots": "dotslow",
    "vdots": "dotsvert", "ddots": "dotsdiag",
    "Re": "Re", "Im": "Im", "wedge": "and", "vee": "or", "neg": "neg",
    "perp": "ortho", "bot": "ortho", "parallel": "parallel", "angle": "angle",
    "degree": "degree", "prime": "\"'\"",
}

FUNC_NAMES = {
    "sin", "cos", "tan", "cot", "sec", "csc", "sinh", "cosh", "tanh", "coth",
    "arcsin", "arccos", "arctan", "ln", "log", "exp", "det", "dim", "gcd",
    "max", "min", "sup", "inf",
}

# Từ khoá StarMath: khi một cụm CHỮ THÔ (không phải lệnh LaTeX) trùng nguyên
# vẹn một từ khoá này, StarMath render thành KÝ HIỆU thay vì các chữ cái.
# Ví dụ nhãn đoạn thẳng "IM" -> ℑ (phần ảo), "IN" -> ∈, "RE" -> ℜ, "OR" -> ∨.
# StarMath tra nguyên cụm chữ (khớp đúng cả cụm, không khớp tiền tố), nên chỉ
# cần tách cụm trùng thành từng chữ ("IM" -> "I M") là hết va chạm mà hiển thị
# vẫn y hệt. So khớp KHÔNG phân biệt hoa/thường (StarMath cũng vậy).
# Không đưa tên hàm (sin, cos, ln, log, exp...) vào đây: chúng vốn nên được
# StarMath nhận là hàm.
STARMATH_RESERVED = {
    "im", "re", "or", "and", "not", "in", "notin", "def", "div", "mod",
    "abs", "sqrt", "sum", "prod", "int", "lim", "nabla", "circ", "dot",
    "bar", "vec", "hat", "tilde", "grave", "acute", "check", "breve",
    "overline", "underline", "widevec", "widehat", "widetilde", "widebar",
    "func", "left", "right", "over", "wideslash", "widebslash",
    "times", "cdot", "oplus", "otimes", "ominus", "odivide", "odot",
    "union", "intersection", "setminus", "aleph", "emptyset", "exists",
    "forall", "partial", "infinity", "infty", "ortho", "parallel", "angle",
    "prop", "approx", "equiv", "sim", "simeq", "cong", "subset", "supset",
    "toward", "transl", "transr", "dlarrow", "drarrow", "dlrarrow",
    "boper", "uoper", "oper", "none", "lbrace", "rbrace", "lline", "rline",
    "ldline", "rdline", "langle", "rangle", "lceil", "rceil", "lfloor",
    "rfloor", "stack", "binom", "matrix", "phantom", "bold", "ital",
    "italic", "nitalic", "nbold", "size", "color", "font", "alignl",
    "alignr", "alignc", "newline", "from", "to", "csub", "csup", "sub", "sup",
}

for g in GREEK_LOWER:
    SYMBOL_MAP[g] = "%" + g
for g in GREEK_UPPER:
    SYMBOL_MAP[g] = "%" + g.upper()

BRACKET_MAP = {"(": "(", ")": ")", "[": "[", "]": "]", "\\{": "lbrace",
               "\\}": "rbrace", "|": "lline", ".": "none", "\\|": "ldline",
               # \vert = "|" đơn, \Vert = "‖" đôi. \lvert/\rvert (đơn) và
               # \lVert/\rVert (đôi) là bản có hướng rõ ràng của LaTeX. Với
               # \left, tất cả đều là mép TRÁI nên map về lline/ldline.
               "\\vert": "lline", "\\lvert": "lline", "\\rvert": "lline",
               "\\Vert": "ldline", "\\lVert": "ldline", "\\rVert": "ldline",
               "\\langle": "langle", "\\rangle": "rangle"}

# BRACKET_MAP dùng chung cho cả \left và \right, nhưng dấu gạch dọc phải đổi
# hướng: \right| là "rline" (không phải "lline"), \right\| là "rdline". Nếu
# không, "\left|...\right|" (giá trị tuyệt đối / chuẩn) sinh ra
# "left lline ... right lline" — StarMath không khớp cặp, hiển thị sai.
# Các biến thể \vert/\Vert cũng phải đổi hướng theo cùng lý do.
RIGHT_DELIM_OVERRIDE = {"|": "rline", "\\|": "rdline",
                        "\\vert": "rline", "\\lvert": "rline",
                        "\\rvert": "rline", "\\Vert": "rdline",
                        "\\lVert": "rdline", "\\rVert": "rdline",
                        "\\langle": "langle", "\\rangle": "rangle"}

# Toán tử Unicode gõ THẲNG bằng ký tự thật (∫, ∑...) thay vì lệnh LaTeX (\int,
# \sum). Đề gốc (vd Câu 5 phần tích phân) rất hay dán trực tiếp ký tự ∫ kèm
# cận "_{0}^{2}". Nếu không nhận diện, ∫ rơi vào nhánh catch-all (giữ nguyên ký
# tự) còn "_{0}^{2}" thành chỉ số dưới/trên rời rạc — StarMath KHÔNG hiểu đó là
# cận tích phân nên mất bound. Ánh xạ về đúng toán tử StarMath có from/to.
UNICODE_OPERATORS = {
    "∫": "int", "∬": "iint", "∭": "iiint", "∮": "iint",
    "∑": "sum", "∏": "prod", "⋃": "union", "⋂": "intersection",
}

# Các toán tử lớn có CẬN (giới hạn) đặt trên/dưới trong StarMath qua from/to.
# Khi rsub/rsup đứng ngay sau token này thì đó là cận (∫_a^b, ∑_i, lim...),
# phải đổi rsub->from, rsup->to; nếu để rsub/rsup thì bị vẽ thành chỉ số cạnh.
_LIMIT_OPERATORS = {"int", "iint", "iiint", "oint", "sum", "prod",
                    "union", "intersection", "lim"}


def _preceded_by_limit_operator(out):
    """True nếu, bỏ qua các cụm 'from {..}'/'to {..}' đã xuất, token liền trước
    là một toán tử lớn (int/sum/lim...). Dùng để biến rsub/rsup thành cận."""
    text = "".join(out).rstrip()
    while True:
        # Bỏ nhóm ngoặc "{...}" ở cuối (cận đã xuất trước đó).
        if text.endswith("}"):
            depth = 0
            j = len(text) - 1
            while j >= 0:
                if text[j] == "}":
                    depth += 1
                elif text[j] == "{":
                    depth -= 1
                    if depth == 0:
                        break
                j -= 1
            if j < 0:
                return False
            text = text[:j].rstrip()
            # Sau nhóm phải là từ khóa from/to thì mới bỏ tiếp, ngược lại dừng.
            if text.endswith("from"):
                text = text[:-4].rstrip()
            elif text.endswith("to"):
                text = text[:-2].rstrip()
            else:
                return False
            continue
        break
    last = text.split()
    return bool(last) and last[-1] in _LIMIT_OPERATORS


def _find_matching_brace(s, open_idx):
    """s[open_idx] == '{' ; trả về index của '}' tương ứng."""
    depth = 0
    for i in range(open_idx, len(s)):
        if s[i] == "{":
            depth += 1
        elif s[i] == "}":
            depth -= 1
            if depth == 0:
                return i
    raise ValueError("Dấu { không đóng trong: " + s)


def _read_arg(s, i):
    """Đọc 1 tham số LaTeX bắt đầu từ vị trí i (bỏ qua khoảng trắng).
    Trả về (nội_dung, vị_trí_kế_tiếp)."""
    while i < len(s) and s[i] == " ":
        i += 1
    if i >= len(s):
        return "", i
    if s[i] == "{":
        j = _find_matching_brace(s, i)
        return s[i + 1:j], j + 1
    # 1 ký tự đơn (vd ^2, _n, \vec x)
    if s[i] == "\\":
        m = re.match(r"\\[a-zA-Z]+", s[i:])
        if m:
            return m.group(0), i + len(m.group(0))
    return s[i], i + 1


def _strip_wrappers(s):
    s = s.strip()
    for a, b in [("$$", "$$"), ("$", "$"), ("\\[", "\\]"), ("\\(", "\\)")]:
        if s.startswith(a) and s.endswith(b) and len(s) >= len(a) + len(b):
            return s[len(a):len(s) - len(b)].strip()
    return s


_LONG_FUNC_NAMES = ("arcsin", "arccos", "arctan", "sinh", "cosh", "tanh", "coth")
_SHORT_FUNC_NAMES = ("cos", "sin", "tan", "cot", "log", "ln")
# Biến số hay đứng dính ngay sau hàm lượng giác/log mà không có dấu cách,
# kiểu "cosx", "sinx", "logt" (rất hay gặp trong đề nguyên hàm/đạo hàm).
_TRAILING_VARS = "xyzt"

# Các lệnh "gia tố" (accent) StarMath hỗ trợ trực tiếp, nhưng trong file nguồn
# lại bị gõ THIẾU dấu \\ ở đầu (lỗi hay gặp khi công thức có sẵn cú pháp
# StarMath lẫn vào ô LaTeX), kiểu "widevec{n}", "acute{B}", "overline{B}".
# Nếu không sửa, chữ "widevec"/"acute"/"overline" sẽ lộ ra thành text thô thay
# vì trở thành đúng dấu mũi tên/dấu phẩy/gạch ngang phía trên.
_BARE_ACCENT_CMDS = ("widevec", "acute", "overline", "underline", "grave",
                     "check", "breve")

# Các lệnh accent hay bị gõ "hậu tố" (đặt SAU chữ cái thay vì bao quanh trước),
# kiểu "u\vec" hay "n\vec_{1}" thay vì đúng chuẩn LaTeX "\vec{u}"/"\vec{n}_{1}".
# Đây là lỗi gõ rất phổ biến trong đề gốc do người soạn dùng công cụ gõ tắt
# đặt ký hiệu mũi tên/dấu ngay sau biến thay vì bọc biến vào trong lệnh.
_POSTFIX_ACCENT_CMDS = ("vec", "hat", "bar", "tilde", "dot", "ddot", "check",
                        "grave", "breve", "acute")
_POSTFIX_ACCENT_RE = re.compile(
    r"\b([A-Za-z]{1,2})\s*\\(" + "|".join(_POSTFIX_ACCENT_CMDS) +
    r")\b(?!\s*\{)(\s*_\s*(?:\{[^{}]*\}|[A-Za-z0-9]))?"
)


def _fix_postfix_accents(s: str) -> str:
    """Sửa lỗi accent đặt hậu tố: "n \\vec _{1}" -> "\\vec{n}_{1}".
    Chỉ áp dụng khi lệnh KHÔNG được theo ngay bởi "{" (tức không phải dạng
    chuẩn \\vec{...} vốn đã đúng và không cần đụng tới)."""
    def repl(m):
        base, cmd, sub = m.group(1), m.group(2), m.group(3) or ""
        return "\\" + cmd + "{" + base + "}" + sub
    return _POSTFIX_ACCENT_RE.sub(repl, s)


def _fix_bare_accent_commands(s: str) -> str:
    """Thêm dấu \\ còn thiếu trước các lệnh accent StarMath bị gõ trần (không
    có \\) nhưng vẫn có dạng {arg} theo ngay sau, kiểu "widevec{n}" -> "\\widevec{n}"."""
    return re.sub(r"(?<!\\)\b(" + "|".join(_BARE_ACCENT_CMDS) + r")(?=\{)",
                  r"\\\1", s)


def _autofix_missing_backslash(s: str) -> str:
    """Tự động thêm dấu \\ còn thiếu trước tên hàm lượng giác/log, xử lý các kiểu
    lỗi gõ LaTeX hay gặp trong đề gốc:
      1) Hàm đứng riêng một từ, không có \\:                 "sin x"   -> "\\sin x"
      2) Hàm dính liền ngay sau hệ số/biến, không cách:       "Acos("   -> "A\\cos("
         (mẫu vật lý x(t)=Acos(...) rất hay gặp; kể cả khi theo sau không phải
         dấu "(" trực tiếp mà là "\\left(", "Acos\\left(...)" vẫn phải nhận ra)
      3) Hàm dính liền một biến số quen thuộc phía SAU, không cách, không \\:
         "cosx" -> "\\cos x", "sinx" -> "\\sin x" (rất hay gặp trong nguyên hàm).
      4) Kết hợp cả 2 lỗi cùng lúc: "bcosx" (= b*cos(x)) -> "b\\cos x".
    Không đụng vào các hàm dài đã đúng dạng như "arccos"/"cosh" (tránh cắt vụn
    thành "arc" + "\\cos"), và bỏ qua phần đã có \\ phía trước.
    """
    # (1) Tên hàm dài, đứng nguyên 1 từ.
    s = re.sub(r"(?<!\\)\b(" + "|".join(_LONG_FUNC_NAMES) + r")\b", r"\\\1", s)
    # (2a) Tên hàm ngắn, đứng nguyên 1 từ (vd " sin x", đứng đầu chuỗi, sau dấu +...).
    s = re.sub(r"(?<!\\)\b(" + "|".join(_SHORT_FUNC_NAMES) + r")\b", r"\\\1", s)
    # (2b) Tên hàm ngắn dính liền ngay sau 1 chữ cái/số (không có \\, không cách),
    # và theo sau không phải là 1 chữ cái khác (tức đã hết "từ hàm") — bắt được cả
    # "Acos(" lẫn "Acos\left(...)" (đề gốc rất hay dùng \left ngay sau hàm dính).
    # Loại trừ hậu tố của "arc..." để không phá "arccos".
    s = re.sub(r"(?<=[A-Za-z0-9])(?<!\\)(?<!arc)(" +
               "|".join(_SHORT_FUNC_NAMES) + r")(?![A-Za-z])", r"\\\1", s)
    # (2c) Tên hàm ngắn đứng đầu từ (có ranh giới trái) nhưng dính liền theo sau
    # bởi ĐÚNG 1 biến số quen thuộc, không cách: "cosx" -> "\cos x".
    s = re.sub(r"(?<!\\)\b(" + "|".join(_SHORT_FUNC_NAMES) +
               r")(?=[" + _TRAILING_VARS + r"]\b)", r"\\\1 ", s)
    # (2d) Kết hợp cả 2 lỗi cùng lúc: hệ số dính trước LẪN biến dính sau, kiểu
    # "bcosx" (= b*cos(x)) hay gặp trong nguyên hàm/đạo hàm.
    s = re.sub(r"(?<=[A-Za-z0-9])(?<!\\)(?<!arc)(" +
               "|".join(_SHORT_FUNC_NAMES) + r")(?=[" + _TRAILING_VARS +
               r"]\b)", r"\\\1 ", s)
    return s


def _script_body(arg):
    """Dịch thân của chỉ số trên/dưới (^{..}/_{..}).

    Nếu thân CHỈ gồm toán tử dấu trần (+, -, *, /, =, <, >, ±...) mà không có
    toán hạng, StarMath vẽ ra glyph lỗi '¿' (vd '-1^{+}' cho giới hạn một phía
    lim_{x→-1⁺}). Bọc chuỗi đó thành string literal StarMath ("+") để hiển thị
    đúng ký tự thay vì hiểu là phép toán thiếu vế.
    """
    body = _process(arg)
    stripped = body.strip()
    if not stripped:
        return body
    if all(ch in '+-*/=<>±∓' for ch in stripped):
        return ' "' + stripped + '" '

    # Nếu bắt đầu bằng toán tử 2 vế (như =S, +2...) thì chèn thêm nhóm rỗng {} ở đầu làm vế trái
    # để tránh LibreOffice Math báo lỗi thiếu vế trái sinh ra glyph '¿'.
    _RELOP = re.compile(r'^(?:<=|>=|<>|=|<|>)')
    _WORDOP = re.compile(r'^(?:approx|equiv|simeq|sim|cong|dlrarrow|drarrow|dlarrow|rightarrow|pointer|leftarrow|notin|in|subseteq|subset|supseteq|supset|union|intersection)(?:\s+|$)')
    _SIGNOP = re.compile(r'^[-+*/](?:\s+|$)')

    if _RELOP.match(stripped) or _WORDOP.match(stripped) or _SIGNOP.match(stripped):
        return '{} ' + body
    return body


def _safe_text_for_starmath(text: str) -> str:
    """Chuyển chuỗi tuỳ ý (kể cả có chữ tiếng Việt/Unicode) thành chuỗi an toàn
    để dùng trong StarMath string literal "...".

    Vấn đề gốc
    ----------
    StarMath string literal được LibreOffice Math truyền vào MTEF stream theo
    encoding Windows-1252 (Latin-1). Các ký tự tiếng Việt (ố, ề, ạ...) là
    Unicode đa byte, KHÔNG có trong Windows-1252 → LibreOffice xuất byte rác
    (0xC0 hoặc placeholder) → MathType hiển thị ◆ (hình thoi đen).

    Chiến lược
    ----------
    1. Với ký tự ASCII (ord < 128): giữ nguyên.
    2. Với ký tự Latin có dấu (ví dụ ố, ề, ạ, đ...):
       - NFD decompose → tách base character + combining marks
       - Giữ lại base character (Latin ASCII), bỏ combining marks
       - Riêng "đ/Đ" (d với stroke, KHÔNG decompose ra 'd') → map thủ công → 'd'/'D'
    3. Với ký tự hoàn toàn ngoài Latin (CJK, Hy Lạp gõ thẳng...):
       - Giữ nguyên nếu nằm trong Windows-1252 (ord 128-255 theo cp1252)
       - Thay bằng '?' nếu không map được

    Kết quả: "đối" → "doi", "kề" → "ke", "góc" → "goc" — không còn ◆.
    Hiển thị trong MathType mất dấu nhưng ĐÚNG ký tự, không lỗi.
    """
    # Map thủ công các ký tự không NFD-decompose ra base Latin
    _MANUAL = {
        'đ': 'd', 'Đ': 'D',
        'ł': 'l', 'Ł': 'L',
        'ø': 'o', 'Ø': 'O',
        'ß': 'ss',
        'æ': 'ae', 'Æ': 'AE',
        'œ': 'oe', 'Œ': 'OE',
    }

    result = []
    for ch in text:
        if ord(ch) < 128:
            result.append(ch)
            continue
        if ch in _MANUAL:
            result.append(_MANUAL[ch])
            continue
        # Thử NFD decompose: lấy base character (không phải combining mark)
        nfd = unicodedata.normalize('NFD', ch)
        base = ''.join(c for c in nfd if unicodedata.category(c) != 'Mn')
        if base and ord(base[0]) < 128:
            result.append(base)
            continue
        # Kiểm tra có encode được cp1252 không
        try:
            ch.encode('cp1252')
            result.append(ch)
        except (UnicodeEncodeError, LookupError):
            result.append('?')
    return ''.join(result)


def _preprocess_bare_abs(s: str) -> str:
    """Chuyển cặp | ... | trần (giá trị tuyệt đối) thành \\left|...\\right|.

    Mục đích
    --------
    Dấu | trần trong _process() bị emit là "mline" (gạch dọc giữa). "mline"
    không tạo FENCE record trong MTEF mà tạo CHAR(0x7C). Điều đó ổn với
    P(B|A) hay {x | x>0}, nhưng với giá trị tuyệt đối |A| thì LibreOffice
    đôi khi xuất sai cấu trúc → MathType hiển thị dấu ( thừa (quan sát ảnh 1).
    Chuyển |...| thành \\left|...\\right| → nhánh \\left/\\right đã xử lý
    đúng → tạo FENCE record chuẩn → MathType render '|A|' không lỗi.

    Quy tắc phân biệt
    -----------------
    - Cặp | ... | không chứa | bên trong, không đứng trong \\{...\\}:
      → giá trị tuyệt đối → bọc \\left|...\\right|
    - | đơn trong P(B|A): chỉ có 1 dấu | → không phải cặp → không đụng
    - | trong \\{x | x>0\\}: được bảo vệ qua bước thay placeholder \\{/\\}

    Không đụng đến
    --------------
    - Cặp đã có \\left|...\\right| (regex dùng negative lookbehind (?<!\\left))
    - Cặp |...|_a^b (đã được xử lý riêng trong convert() bằng regex trước đó)
    - \\vert, \\lvert, \\rvert (đã xử lý đúng trong _process())
    """
    _PH_L = '\x00LB\x00'   # placeholder cho \{
    _PH_R = '\x00RB\x00'   # placeholder cho \}

    # Bước 1: bảo vệ \{...\} — | bên trong là điều kiện tập hợp, không phải abs
    work = s.replace(r'\{', _PH_L).replace(r'\}', _PH_R)

    # Bước 2: khớp cặp |...| không chứa | bên trong
    # Negative lookbehind (?<!\\left): không đụng \left| đã đúng rồi
    # Negative lookahead (?!\s*[_^]): không đụng |...|_a^b (đã có regex riêng)
    pattern = re.compile(r'(?<!\\left)\|([^|\\]+?)\|(?!\s*[_^])')

    res = pattern.sub(lambda m: r'\left|' + m.group(1) + r'\right|', work)

    # Bước 3: khôi phục \{ \}
    return res.replace(_PH_L, r'\{').replace(_PH_R, r'\}')


def _fix_bare_cancel(s: str) -> str:
    """🔒 [LOCK-FIX-10]: Thêm backslash còn thiếu trước 'cancel' bị gõ trần (không có \\).

    Hai dạng lỗi gõ hay gặp trong đề gốc:
      1) cancel{D}   → \\cancel{D}   (có {} bao argument)
      2) cancel X    → \\cancel{X}   (khoảng trắng + đúng 1 ký tự đơn)

    Không đụng vào \\cancel (đã có dấu \\) và không bọc thêm khi không cần.
    """
    # Dạng 1: cancel ngay trước { → thêm \ phía trước
    s = re.sub(r'(?<!\\)\bcancel\b(?=\s*\{)', r'\\cancel', s)
    # Dạng 2: cancel + khoảng trắng + 1 ký tự chữ cái đơn → \cancel{X}
    # Chỉ bọc đúng 1 ký tự (dạng ký pháp Feynman: cancel D, cancel p...)
    s = re.sub(r'(?<!\\)\bcancel\b\s+([A-Za-z])(?![A-Za-z])', r'\\cancel{\1}', s)
    return s


def _preprocess_bare_abs_safe(s: str) -> str:
    """🔒 [LOCK-FIX-09]: Bọc các cặp |...| chứa lệnh LaTeX (có dấu \\) thành \\left|...\\right| một cách an toàn.

    Quy trình:
      1. Bảo vệ \\{ và \\} bằng placeholder.
      2. Bảo vệ \\left| và \\right| đã đúng sẵn.
      3. Bảo vệ \\| (phép chuẩn norm) bằng placeholder.
      4. Áp dụng regex tìm các cặp |...| không chứa | bên trong và bọc chúng.
      5. Khôi phục lại các thực thể đã bảo vệ.
    """
    _PH_L = '\x00LB\x00'
    _PH_R = '\x00RB\x00'
    work = s.replace(r'\{', _PH_L).replace(r'\}', _PH_R)

    _PH_B2_L = '\x02LFTPIPE\x02'
    _PH_B2_R = '\x02RGTPIPE\x02'
    work = work.replace(r'\left|', _PH_B2_L).replace(r'\right|', _PH_B2_R)

    _PH_NORM = '\x03NORM\x03'
    work = work.replace(r'\|', _PH_NORM)

    # Cho phép chứa dấu gạch chéo ngược \\ bên trong
    pattern = re.compile(r'(?<!\\left)\|([^|]+?)\|(?!\s*[_^])')
    work = pattern.sub(lambda m: r'\left|' + m.group(1) + r'\right|', work)

    work = work.replace(_PH_NORM, r'\|')
    work = work.replace(_PH_B2_L, r'\left|').replace(_PH_B2_R, r'\right|')
    work = work.replace(_PH_L, r'\{').replace(_PH_R, r'\}')
    return work


def _preprocess_quantum_braket(s: str) -> str:
    """🔒 [LOCK-FIX-12]: Tự động bọc và chuẩn hoá các ký pháp Bra-Ket an toàn, tránh bọc nhầm qua dấu `=`.

    1. Bra-ket: \\langle A | B \\rangle -> \\left\\langle A \\right| \\left. B \\right\\rangle
    2. Ket (tránh đụng \\left| và \\right|): | A \\rangle -> \\left| A \\right\\rangle
    3. Bra (tránh đụng \\left\\langle): \\langle A | -> \\left\\langle A \\right|
    """
    # 1. Bra-ket: \langle A | B \rangle -> \left\langle A \right| \left. B \right\rangle
    s = re.sub(r'\\langle([^|]+?)\|([^|]+?)\\rangle', r'\\left\\langle \1 \\right| \\left. \2 \\right\\rangle', s)
    # 2. Ket: | A \rangle -> \left| A \right\rangle (bảo vệ \left/\right đã có)
    s = re.sub(r'(?<!\\left)(?<!\\right)\|([^|]+?)\\rangle', r'\\left| \1 \\right\\rangle', s)
    # 3. Bra: \langle A | -> \left\langle A \right| (bảo vệ \left)
    s = re.sub(r'(?<!\\left)\\langle([^|]+?)\|', r'\\left\\langle \1 \\right|', s)
    return s


def convert(latex: str) -> str:
    """Chuyển 1 công thức LaTeX sang chuỗi StarMath."""
    # ----------------------------------------------------------------
    # Tiền xử lý \overparen{...} -> \overline{ \u200e ... }
    # Đánh dấu bằng ký tự tàng hình Left-To-Right Mark (U+200E) để mathtype_ole_builder.py
    # nhận diện và chuyển thành arc cung tròn (tvFROWN) thay vì overbar,
    # đồng thời không hiển thị rác trong Word WMF preview.
    latex = latex.replace(r'\overparen{', '\\overline{ \u200e ').replace(
                           r'\overparen {', '\\overline{ \u200e ')
    # ----------------------------------------------------------------
    s = _strip_wrappers(latex)
    # 🔒 [LOCK-FIX-14]: Sửa lỗi empty group {} đứng trước dấu _ hoặc ^ (thường gặp trong {}_2F_1)
    # hoặc công thức bắt đầu trực tiếp bằng dấu _ hoặc ^ (thiếu base → gây lỗi cú pháp StarMath -> ¿)
    s = re.sub(r'\{\}(?=\s*[_^])', r'""', s)
    if s.startswith(('_', '^')):
        s = '""' + s
    # ----------------------------------------------------------------
    # B1: Dọn ký tự Unicode vô hình / khoảng trắng Unicode không chuẩn.
    # Nhiều trình soạn đề dán U+2061 (FUNCTION APPLICATION) giữa tên hàm và
    # đối số, hoặc U+200A (HAIR SPACE) giữa ký hiệu tích phân và biến số.
    # Những ký tự này đi qua nguyên vẹn vào StarMath, LibreOffice không map
    # được sang MTEF → hiển thị ◆ (hộp lỗi) trong MathType.
    # Cách sửa: xóa hết ký tự vô hình, đổi khoảng trắng Unicode về ASCII.
    # ----------------------------------------------------------------
    # Ký tự vô hình / đặt chỗ (zero-width): xóa hết
    _INVISIBLE = (
        '\u2061'  # FUNCTION APPLICATION   (sin⁡x)
        '\u2062'  # INVISIBLE TIMES        (ab)
        '\u2063'  # INVISIBLE SEPARATOR    (i,j)
        '\u2064'  # INVISIBLE PLUS         (3⁤¼)
        '\u2060'  # WORD JOINER
        '\u200B'  # ZERO-WIDTH SPACE
        '\u200C'  # ZERO-WIDTH NON-JOINER
        '\u200D'  # ZERO-WIDTH JOINER
        '\uFEFF'  # BOM / ZERO-WIDTH NO-BREAK SPACE
        '\u00AD'  # SOFT HYPHEN
    )
    s = s.translate(str.maketrans('', '', _INVISIBLE))
    # Sau khi xóa ký tự vô hình, tên hàm có thể dính liền vào số/biến
    # vd "sin⁡3x" → "sin3x". Chỉ thêm space khi TÊN HÀM cụ thể dính
    # vào chữ số hoặc chữ cái — KHÔNG thêm vào các cặp như "6x", "2x".
    _FUNC_BOUNDARY = re.compile(
        r'\b(sin|cos|tan|cot|log|ln|arcsin|arccos|arctan|sinh|cosh|tanh|coth|exp|lim(?!its)|det|max|min)([0-9A-Za-z])'
    )
    s = _FUNC_BOUNDARY.sub(r'\1 \2', s)
    # Khoảng trắng Unicode không chuẩn → dấu cách ASCII thường
    _UNICODE_SPACES = {
        ord(c): ' ' for c in (
            '\u00A0'  # NO-BREAK SPACE
            '\u2000\u2001\u2002\u2003\u2004\u2005'  # EN/EM/FIGURE... SPACE
            '\u2006\u2007\u2008\u2009\u200A'        # HAIR SPACE etc.
            '\u202F'  # NARROW NO-BREAK SPACE
            '\u205F'  # MEDIUM MATHEMATICAL SPACE
            '\u3000'  # IDEOGRAPHIC SPACE
        )
    }
    s = s.translate(_UNICODE_SPACES)
    # ----------------------------------------------------------------
    # template còn khuyết đối số (vd cận tích phân đã có nhưng ô thân hàm bị
    # bỏ trống). Nếu giữ nguyên, StarMath hiểu "<" ">" là toán tử so sánh và
    # "?" là chữ thô -> lộ ra "< ? >" giữa công thức. Xoá sạch trước khi dịch.
    s = re.sub(r"<\s*\?\s*>", " ", s)
    # ----------------------------------------------------------------
    # B2: Thanh cận tích phân viết bằng pipe thường "|F(x)|_a^b".
    # "|" trần -> "mline" (dấu gạch giữa, KHÔNG ghép cặp). Khi có chỉ số
    # _a^b ngay sau dấu "|" ĐÓNG, chỉ số gắn vào từ khóa "mline" -> StarMath
    # không attach script vào "mline" -> MathType hiển thị ◆ (Câu 9 C/D).
    # Cách sửa: đổi "|...|" (không chứa "|" bên trong) đứng NGAY TRƯỚC _ hoặc
    # ^ thành "\left|...\right|" để đi theo nhánh đã chạy đúng (bọc {..} +
    # csup/csub). Giá trị tuyệt đối thường (|a|, \ln|x|, |f(x)|dx) không có
    # chỉ số _/^ theo sau nên KHÔNG bị đụng.
    # Bug fix: bảo vệ \left| và \right| đã có sẵn trước khi áp regex,
    # tránh bọc kép (\left|\int\right|^2 → \left\left|...\right\right|^2).
    # ----------------------------------------------------------------
    _PH_B2_L = '\x02LFTPIPE\x02'
    _PH_B2_R = '\x02RGTPIPE\x02'
    s = s.replace(r'\left|', _PH_B2_L).replace(r'\right|', _PH_B2_R)
    s = re.sub(r"\|([^|]+)\|(?=\s*[_^])", r"\\left|\1\\right|", s)
    s = s.replace(_PH_B2_L, r'\left|').replace(_PH_B2_R, r'\right|')
    s = _preprocess_quantum_braket(s)  # Chuẩn hoá ký pháp cơ học lượng tử Bra-Ket: \langle A | B \rangle -> \left\langle A\right| ...
    s = _preprocess_bare_abs_safe(s)  # "|\\vec{\\theta}|" -> "\\left|\\vec{\\theta}\\right|" (trị tuyệt đối chứa lệnh LaTeX)
    s = _preprocess_bare_abs(s)        # "|A|" -> "\left|A\right|" (abs trần → FENCE)
    s = _fix_bare_accent_commands(s)   # "widevec{n}" -> "\widevec{n}"
    s = _fix_bare_cancel(s)            # "cancel{D}", "cancel D" -> "\cancel{D}"
    s = _fix_postfix_accents(s)        # "n \vec _{1}" -> "\vec{n}_{1}"
    s = _autofix_missing_backslash(s)  # "Acos(", "cosx", "bcosx" -> "\cos"...
    # 🔒 [LOCK-FIX-01]: Chuẩn hóa khoảng trắng sau \left và \right để tránh bị nhận diện nhầm
    # bởi _auto_wrap_raw_brackets gây lỗi bọc kép \left\left và glyph lỗi ¿¿¿¿ ở các Câu 9, 10, 11
    # CẢNH BÁO CHO AI AGENTS: KHÔNG ĐƯỢC XÓA HOẶC SỬA 2 DÒNG REGEX NÀY!
    s = re.sub(r'\\left\s+', r'\\left', s)
    s = re.sub(r'\\right\s+', r'\\right', s)
    s = _auto_wrap_raw_brackets(s)     # "[-3; 3)" -> "\left[ -3; 3 \right)"
    res = _process(s).strip()
    # ----------------------------------------------------------------
    # B3: Xử lý công thức bắt đầu bằng toán tử 2 vế (=, +, -, \Leftrightarrow...).
    # Trong StarMath, toán tử 2 vế đứng ở đầu mà không có vế trái sẽ bị coi là
    # lỗi cú pháp (thiếu vế) và LibreOffice xuất ra glyph báo lỗi '¿'.
    # Chèn nhóm rỗng '{}' ở đầu để tạo vế trái hợp lệ, loại bỏ triệt để dấu '¿'.
    # ----------------------------------------------------------------
    # Toán tử quan hệ/đẳng thức KHÔNG bao giờ mang nghĩa đơn nguyên → luôn cần
    # vế trái, kể cả khi dính liền toán hạng ('=2' → '{} =2'). Đây chính là gốc
    # của lỗi '=' hiển thị thành '¿': trước đây yêu cầu có dấu cách sau toán tử
    # nên '=2 log...' không được chèn '{}'. Thứ tự '<=|>=|<>' trước '<|>' để khớp
    # đúng toán tử 2 ký tự.
    _RELOP_START = re.compile(r'^(?:<=|>=|<>|=|<|>)')
    # Toán tử từ khóa (chữ) PHẢI có ranh giới từ phía sau, nếu không 'intersection'
    # sẽ khớp nhầm 'in', 'supseteq' khớp nhầm 'supset'... (đặt biến thể dài trước).
    _WORDOP_START = re.compile(
        r'^(?:approx|equiv|simeq|sim|cong|dlrarrow|drarrow|dlarrow|rightarrow|leftarrow|notin|in|subseteq|subset|supseteq|supset|union|intersection)(?=\s|$)'
    )
    # '+ - * /' chỉ chèn vế trái khi CÓ dấu cách phía sau ('- 3'); nếu dính liền
    # ('-3', '+3') coi là số âm/dương hợp lệ, giữ nguyên.
    _SIGNOP_START = re.compile(r'^[-+*/](?:\s+|$)')
    if _RELOP_START.match(res) or _WORDOP_START.match(res) or _SIGNOP_START.match(res):
        res = '{} ' + res
    return res


def _auto_wrap_raw_brackets(latex_str: str) -> str:
    """Tự động bọc \\left và \\right cho các cặp ngoặc trần chứa dấu chấm phẩy/phẩy
    (như khoảng/nửa khoảng toán học [-3; 3), (0; 5], (a, b) hoặc tọa độ điểm A(1; 0; 0)).
    StarMath coi ngoặc trần lệch nhau là lỗi cú pháp → hiển thị ¿ trong ảnh preview.
    Khi bọc \\left và \\right, StarMath render thành cặp left...right chuẩn không lỗi.

    🔒 BẢO VỆ ngoặc đứng ngay sau \\right. (chú thích điều kiện như "(t∈ℝ; t>0)").
    Trước đây regex bọc nhầm → StarMath emit thêm " left ( " → MathType hiển thị
    dấu ( thừa ở cuối công thức khi mở editor (kích đúp).

    Kỹ thuật: thay \\right. bằng placeholder \\x00RDOT\\x00 trước khi áp regex.
    Hàm _replace() kiểm tra ký tự ngay trước vị trí khớp: nếu là \\x00
    (ký tự cuối placeholder) thì giữ nguyên, không bọc. Sau đó khôi phục \\right.
    """
    _PH = '\x00RDOT\x00'   # ký tự \x00 không bao giờ xuất hiện trong LaTeX hợp lệ

    # Bước 1: bảo vệ \right. → placeholder
    work = latex_str.replace(r'\right.', _PH)

    pattern = re.compile(
        r'(?<!\\left)([\[\(])\s*([^\[\]\(\)]*?[;,][^\[\]\(\)]*?)\s*([\]\)])'
    )

    def _make_replace(src: str):
        """Tạo hàm replace với closure trên chuỗi nguồn để kiểm tra vị trí."""
        def _replace(m):
            # Nếu ký tự ngay trước ( là \x00 (ký tự cuối _PH) → ngoặc này
            # đứng ngay sau \right. → KHÔNG bọc, trả nguyên văn.
            if m.start() > 0 and src[m.start() - 1] == '\x00':
                return m.group(0)
            return rf'\left{m.group(1)} {m.group(2)} \right{m.group(3)}'
        return _replace

    # Áp 2 lần để bắt cặp ngoặc lồng nhau (giống code cũ)
    res  = pattern.sub(_make_replace(work), work)
    res2 = pattern.sub(_make_replace(res),  res)

    # Bước 3: khôi phục \right.
    return res2.replace(_PH, r'\right.')



def _find_matching_end(s, start, name):
    """Tìm vị trí \\end{name} khớp với \\begin{name} bắt đầu tại start
    (không xử lý lồng cùng tên, đủ dùng cho đề phổ thông)."""
    end_tag = "\\end{" + name + "}"
    idx = s.find(end_tag, start)
    if idx == -1:
        raise ValueError("Thiếu \\end{%s} khớp với \\begin{%s}" % (name, name))
    return idx, idx + len(end_tag)


def _process_environment(name, content):
    rows = [r for r in content.split("\\\\")]
    row_strs = []
    for row in rows:
        row = row.strip()
        if row == "":
            continue
        cells = [c.strip() for c in row.split("&")]
        cells_out = [_process(c) for c in cells]
        row_strs.append(" ~~ ".join(cells_out))
    rows_aligned = [" alignl { " + r + " } " for r in row_strs]
    body = "stack{" + " # ".join(rows_aligned) + "}" if len(row_strs) > 1 \
        else (row_strs[0] if row_strs else "")
    # Nếu mỗi hàng có nhiều cột thật sự (ma trận), dùng cú pháp matrix thay stack
    multi_col = any(("&" in r) for r in rows if r.strip())
    if multi_col:
        matrix_rows = []
        for row in rows:
            row = row.strip()
            if row == "":
                continue
            cells = [_process(c.strip()) for c in row.split("&")]
            matrix_rows.append(" # ".join(cells))
        body = "matrix{" + " ## ".join(matrix_rows) + "}"

    if name == "cases":
        return " left lbrace " + body + " right none "
    if name in ("matrix",):
        return "matrix{" + " ## ".join(
            " # ".join(_process(c.strip()) for c in row.split("&"))
            for row in rows if row.strip()) + "}"
    if name == "pmatrix":
        inner = "matrix{" + " ## ".join(
            " # ".join(_process(c.strip()) for c in row.split("&"))
            for row in rows if row.strip()) + "}"
        return "left ( " + inner + " right )"
    if name == "bmatrix":
        inner = "matrix{" + " ## ".join(
            " # ".join(_process(c.strip()) for c in row.split("&"))
            for row in rows if row.strip()) + "}"
        return "left [ " + inner + " right ]"
    if name == "vmatrix":
        inner = "matrix{" + " ## ".join(
            " # ".join(_process(c.strip()) for c in row.split("&"))
            for row in rows if row.strip()) + "}"
        return "left lline " + inner + " right rline"
    if name == "array":
        return body
    return body


def _process(s: str) -> str:
    out = []
    i = 0
    n = len(s)
    # Đếm \vert / \Vert TRẦN để ghép cặp: lần lẻ = mép TRÁI (mở), lần chẵn =
    # mép PHẢI (đóng). \vert...\vert là giá trị tuyệt đối, \Vert...\Vert là
    # chuẩn — luôn đi theo cặp. Trước đây dùng "mline" cho cả hai, MathType
    # render "mline" thành "¿" (Câu 9: D=∫|x²−x|dx). lline/rline khớp cặp đúng.
    vert_count = 0
    dvert_count = 0
    # Stack lưu vị trí ký tự trong out tại thời điểm mỗi \left được emit.
    # Dùng để \right tìm đúng \left tương ứng (không nhầm với \left lồng bên trong).
    left_stack = []  # mỗi phần tử = len("".join(out)) lúc emit " left ..."
    while i < n:
        c = s[i]

        if s[i:i + 7] == "\\begin{":
            j = s.index("}", i)
            name = s[i + 7:j]
            k = j + 1
            if name == "array" and k < n and s[k] == "{":
                k = _find_matching_brace(s, k) + 1  # bỏ qua {cols}
            end_start, end_stop = _find_matching_end(s, k, name)
            content = s[k:end_start]
            out.append(" " + _process_environment(name, content) + " ")
            i = end_stop
            continue

        if c == "\\":
            m = re.match(r"\\([a-zA-Z]+)", s[i:])
            if not m:
                # \{  \}  \|  \,  \;  \!  \(space)  \\  ...
                m2 = re.match(r"\\(.)", s[i:])
                if m2 is None:
                    # Dấu \ ở cuối chuỗi hoặc trước ký tự không hợp lệ — bỏ qua
                    i += 1
                    continue
                ch = m2.group(1)
                if ch in ("{", "}"):
                    out.append(" lbrace " if ch == "{" else " rbrace ")
                elif ch in (",", ";", "!", " "):
                    # \, thin space, \; thick space, \! neg space, \ space
                    # → all removed: StarMath manages inter-token spacing automatically
                    pass
                elif ch == "\\":
                    out.append(" newline ")
                elif ch == "%":
                    # StarMath dùng % làm tiền tố ký hiệu (%pi, %alpha...);
                    # một dấu % trần sẽ bị hiểu nhầm/lỗi cú pháp, nên phải
                    # bọc thành text literal để hiển thị đúng dấu %.
                    out.append(' "%" ')
                elif ch == "|":
                    # Đây là \| trần. LaTeX dùng \| cho double vertical bar,
                    # nhưng trong các tài liệu toán VN, người soạn đề rất hay
                    # dùng \| để biểu diễn dấu gạch dọc trong xác suất P(A|B)
                    # hoặc tập hợp. Nếu map sang '|', StarMath hiểu là OR (∨).
                    # 🔒 [LOCK-FIX-13]: Thay vì "mline" (gây lỗi ¿), dùng string literal "|"
                    out.append(' "|" ')
                else:
                    out.append(ch)
                i += m2.end()
                continue

            cmd = m.group(1)
            i += m.end()

            if cmd in ("frac", "dfrac", "tfrac", "cfrac"):
                a, i = _read_arg(s, i)
                b, i = _read_arg(s, i)
                # Bọc CẢ phân số trong một nhóm { } ngoài cùng. StarMath cho
                # "int"/"sum"... bám vào toán hạng NGAY SAU, còn "over" áp sau;
                # nếu để "int ... {x} over {..}" thì thành (int x)/(..) — dấu ∫
                # lọt vào tử số (Câu 7: B=∫ x/√(x²+1)). Bọc {{x} over {..}} giữ
                # nguyên phân số là một khối dưới dấu tích phân.
                out.append("{{" + _process(a) + "} over {" + _process(b) + "}}")
            elif cmd == "sqrt":
                if i < n and s[i] == "[":
                    j = s.index("]", i)
                    root = s[i + 1:j].strip()
                    i = j + 1
                    arg, i = _read_arg(s, i)
                    if root == "":
                        out.append(" sqrt{" + _process(arg) + "} ")
                    else:
                        out.append(" nroot{" + _process(root) + "}{" + _process(arg) + "} ")
                else:
                    arg, i = _read_arg(s, i)
                    out.append(" sqrt{" + _process(arg) + "} ")
            elif cmd in ("binom", "dbinom"):
                a, i = _read_arg(s, i)
                b, i = _read_arg(s, i)
                out.append(" binom{" + _process(a) + "}{" + _process(b) + "} ")
            elif cmd == "boxed":
                arg, i = _read_arg(s, i)
                out.append(" boxed {" + _process(arg) + "} ")
            elif cmd == "pmod":
                arg, i = _read_arg(s, i)
                out.append(" ( mod " + _process(arg) + " ) ")
            elif cmd == "bmod":
                out.append(" mod ")
            elif cmd in ("text", "mathrm", "operatorname"):
                arg, i = _read_arg(s, i)
                # _safe_text_for_starmath: chuyển chữ Việt/Unicode về Latin ASCII
                # trước khi đưa vào StarMath string literal. LibreOffice Math mã
                # hóa string literal theo Windows-1252 khi xuất MTEF; ký tự ngoài
                # bảng mã đó (ố, ề, đ...) bị xuất thành byte rác → MathType ◆.
                out.append(' "' + _safe_text_for_starmath(arg) + '" ')
            elif cmd == "mathbb":
                arg, i = _read_arg(s, i)
                blackboard = {"Z": "\u2124", "R": "\u211D", "N": "\u2115",
                              "Q": "\u211A", "C": "\u2102"}
                out.append(" " + blackboard.get(arg.strip(), arg) + " ")
            elif cmd in ("mathbf", "boldsymbol"):
                arg, i = _read_arg(s, i)
                out.append(" bold {" + _process(arg) + "} ")
            elif cmd == "mathit":
                arg, i = _read_arg(s, i)
                out.append(" ital {" + _process(arg) + "} ")
            elif cmd in ("rm", "bf", "it", "sf", "tt", "cal", "sl", "sc",
                         "mathsf", "mathtt", "mathcal", "mathnormal",
                         "rmfamily", "bffamily", "itshape", "upshape",
                         "normalfont"):
                # Lệnh khai báo font kiểu cũ (\rm \bf \it ...) và họ font LaTeX2e.
                # StarMath không có khái niệm tương đương chung; quan trọng là
                # KHÔNG để tên lệnh ("rm", "bf"...) lọt ra thành chữ thô. Nếu có
                # {arg} theo ngay sau (vd "\rm{ d }") thì lấy nội dung, còn dạng
                # khai báo trần ("\rm x") thì chỉ đơn giản bỏ lệnh, giữ phần sau.
                while i < n and s[i] == " ":
                    i += 1
                if i < n and s[i] == "{":
                    arg, i = _read_arg(s, i)
                    out.append(" " + _process(arg) + " ")
            elif cmd == "overset":
                # \overset{top}{base}: nhiều đề (đặc biệt vector: \overset{\rightarrow}{OD})
                # dùng cú pháp này thay vì \vec{}/\overrightarrow{}. StarMath không có lệnh
                # "overset" chung, nên phải nhận diện phần "top" và ánh xạ sang lệnh accent
                # StarMath tương ứng (vec/widevec/hat/tilde/overline...). Nếu không, trước đây
                # code rơi vào nhánh "lệnh lạ -> giữ nguyên tên", làm chữ "overset" bị lộ ra
                # thành văn bản thô thay vì hiển thị mũi tên/dấu phía trên chữ.
                top, i = _read_arg(s, i)
                base, i = _read_arg(s, i)
                top_key = top.strip().lstrip("\\")
                accent = {
                    "rightarrow": "widevec", "to": "widevec",
                    "leftarrow": "widevec", "gets": "widevec",
                    "leftrightarrow": "widevec", "rightharpoonup": "widevec",
                    "hat": "hat", "widehat": "widehat",
                    "tilde": "tilde", "widetilde": "widetilde", "sim": "tilde",
                    "bar": "overline", "overline": "overline",
                    "vee": "check", "wedge": "hat",
                    "dot": "dot", "ddot": "ddot",
                }.get(top_key)
                if accent:
                    out.append(" " + accent + " {" + _process(base) + "} ")
                else:
                    # Không nhận diện được ký hiệu phía trên: dùng "csup" của StarMath để
                    # đặt "top" ngay phía trên "base" (không đẹp bằng accent thật, nhưng
                    # không làm lộ chữ "overset" ra ngoài như lỗi cũ).
                    processed_base = _process(base)
                    stripped_base = processed_base.strip()
                    if stripped_base in ('=', '<', '>', '+', '-', '*', '/') or stripped_base in (
                        'approx', 'equiv', 'simeq', 'sim', 'cong', 'notin', 'in', 'subseteq', 'subset', 'supseteq', 'supset', 'rightarrow', 'leftarrow'
                    ):
                        out.append(" {{} " + stripped_base + " {}} csup {" + _process(top) + "} ")
                    else:
                        out.append(" {" + processed_base + "} csup {" + _process(top) + "} ")
            elif cmd in ("vec", "hat", "dot", "ddot", "bar", "tilde",
                         "overline", "underline", "widehat", "widetilde",
                         "overrightarrow", "overleftarrow", "widevec",
                         "acute", "grave", "check", "breve"):
                key = {"widetilde": "widetilde",
                       "overline": "overline", "bar": "overline",
                       "overrightarrow": "widevec",
                       "overleftarrow": "widevec",
                       "widehat": "widehat",
                       }.get(cmd, cmd)
                arg, i = _read_arg(s, i)
                # \vec với argument nhiều ký tự (AB, AC, IM...) phải dùng
                # "widevec" để mũi tên trải dài hết base; "vec" chỉ vẽ mũi
                # tên ngắn bằng 1 ký tự — không đủ phủ cả cụm.
                if key == "vec" and len(arg.strip()) > 1:
                    key = "widevec"
                elif key in ("tilde", "widetilde") and len(arg.strip()) > 1:
                    key = "widetilde"
                out.append(" " + key + " {" + _process(arg) + "} ")
            elif cmd == "left":
                d, i = _read_delim(s, i)
                # Ghi nhớ vị trí byte trong out tại thời điểm emit " left "
                left_stack.append(len("".join(out)))
                out.append(" left " + BRACKET_MAP.get(d, d) + " ")
            elif cmd == "right":
                d, i = _read_delim(s, i)
                delim = RIGHT_DELIM_OVERRIDE.get(d) or BRACKET_MAP.get(d, d)
                # ----------------------------------------------------------------
                # Fix "evaluation bar" notation: \left. F(x) \right|_a^b
                # StarMath không hỗ trợ subscript/superscript đặt trực tiếp sau
                # "right rline" (block left...right) — sinh ra ký hiệu lỗi ◆.
                # Giải pháp: nếu ngay sau \right| có _{}^{}, gom toàn bộ
                # cụm left...right vào { } rồi gắn csub/csup để tạo bảng
                # cán đến giá trị tích phân đúng cú pháp.
                # ----------------------------------------------------------------
                # Tìm xem có sub/sup theo sau ngay không (bỏ qua khoảng trắng
                # và các nhóm rỗng "{}" — nguồn hay viết \right\vert{}_{a}^{b}
                # với "{}" chèn giữa để tách token, làm _/^ không nằm sát \right).
                j = i
                while j < len(s):
                    if s[j] == ' ':
                        j += 1
                    elif s[j] == '{' and j + 1 < len(s) and s[j+1] == '}':
                        j += 2
                    else:
                        break
                sub_arg = sup_arg = None
                # Đọc sub (_) và sup (^) bất kỳ thứ tự
                k = j
                while k < len(s) and s[k] in ('_', '^'):
                    sym = s[k]
                    k += 1
                    arg_val, k = _read_arg(s, k)
                    while k < len(s) and s[k] == ' ':
                        k += 1
                    if sym == '_':
                        sub_arg = arg_val
                    else:
                        sup_arg = arg_val
                    # có thể có cả _ lẫn ^ sau
                    if k < len(s) and s[k] in ('_', '^'):
                        continue
                    break

                if (sub_arg is not None or sup_arg is not None) and delim in ('rline', 'rdline', 'none'):
                    # Lấy vị trí của \left ĐÚNG tương ứng từ stack.
                    # Nếu stack rỗng (left bị emit từ context khác), fallback rfind.
                    joined = "".join(out)
                    if left_stack:
                        left_pos = left_stack.pop()
                    else:
                        # Fallback: tìm " left " cuối cùng chưa khớp bằng depth scan
                        left_pos = -1
                        depth = 0
                        # Dò ngược các token " left " và " right " trong joined
                        tok_pat = re.compile(r' (left|right) ')
                        tokens = [(m.start(), m.group(1)) for m in tok_pat.finditer(joined)]
                        for tidx in reversed(range(len(tokens))):
                            tpos, tname = tokens[tidx]
                            if tname == 'right':
                                depth += 1
                            else:  # left
                                if depth == 0:
                                    left_pos = tpos
                                    break
                                depth -= 1
                    if left_pos != -1:
                        before = joined[:left_pos]
                        inner  = joined[left_pos:]  # " left ... "
                        # ------------------------------------------------------
                        # Ngoặc trái vô hình "\left." sinh " left none ...".
                        # LibreOffice export "left none" thành ký tự null (mtcode
                        # 0x0000) làm dấu ngoặc trái của template → MathType editor
                        # hiển thị ◆? (ảnh preview thì vô hình nên nhìn vẫn đẹp).
                        # Với thanh cận |F(x)|_a^b (\left. ... \right|), bỏ hẳn
                        # "left none" và emit thanh bar đơn (rline/rdline) → không
                        # còn null char, render y hệt. Giá trị tuyệt đối có cận
                        # (\left|...\right|_a^b) bắt đầu bằng "left lline" nên KHÔNG
                        # khớp nhánh này, giữ nguyên cặp left...right.
                        # ------------------------------------------------------
                        m_none = re.match(r'\s*left\s+none\s+', inner)
                        if m_none and delim in ('rline', 'rdline'):
                            content = inner[m_none.end():]
                            piece = "{" + content + " " + delim + " }"
                        else:
                            # Xây dựng: { left ... right rline } csup {b} csub {a}
                            piece = "{" + inner + " right " + delim + " }"
                        if sup_arg is not None:
                            piece += " csup {" + _script_body(sup_arg) + "}"
                        if sub_arg is not None:
                            piece += " csub {" + _script_body(sub_arg) + "}"
                        # Reset out và điền lại
                        out.clear()
                        out.append(before)
                        out.append(piece)
                        i = k
                        continue
                # Trường hợp thường: emit right rồi tiếp tục.
                # Cần pop left_stack để stack không bị lệch với left/right thường.
                if left_stack:
                    left_stack.pop()
                # Luôn emit "right none" thay vì bỏ qua. Trước đây code bỏ
                # qua hoàn toàn khi delim=='none' (điều kiện 'if delim != "none"')
                # khiến \left\{...\right. tạo ra StarMath thiếu "right none":
                #   "left lbrace stack{...}"  ← sai
                #   "left lbrace stack{...} right none"  ← đúng
                # LibreOffice Math cần "right none" để tạo FENCE record đúng
                # trong MTEF; thiếu nó LO có thể auto-close theo cách không chuẩn
                # hoặc không tạo FENCE record → render khác với \begin{cases}.
                # mathtype_ole_builder._patch_mtef_right_none() sau đó patch
                # right_char 0xc0→0x01 trong FENCE record đó.
                out.append(" right " + delim + " ")

            elif cmd in ("sum", "int", "iint", "iiint", "oint", "prod",
                         "bigcup", "bigcap", "lim"):
                word = {"int": "int", "iint": "iint", "iiint": "iiint",
                        "oint": "iint", "sum": "sum", "prod": "prod",
                        "bigcup": "union", "bigcap": "intersection",
                        "lim": "lim"}[cmd]
                lo, hi, i = _read_limits(s, i)
                piece = " " + word
                if lo is not None:
                    piece += " from {" + _process(lo) + "}"
                if hi is not None:
                    piece += " to {" + _process(hi) + "}"
                out.append(piece + " ")
            elif cmd in FUNC_NAMES:
                out.append(" " + cmd + " ")
            elif cmd == "mathop":
                arg, i = _read_arg(s, i)
                out.append(" " + _process(arg) + " ")
            elif cmd == "limits":
                lo, hi, i = _read_limits(s, i)
                if lo is not None:
                    out.append(" from {" + _process(lo) + "}")
                if hi is not None:
                    out.append(" to {" + _process(hi) + "}")
            elif cmd in ("displaystyle", "textstyle", "nolimits",
                         "strut", "hfill", "allowbreak", "notag"):
                pass  # Bỏ qua các lệnh layout chỉ dùng trong LaTeX
            elif cmd in SYMBOL_MAP:
                out.append(" " + SYMBOL_MAP[cmd] + " ")
            elif cmd in ("quad", "qquad"):
                out.append("~~")
            elif cmd in ("cdotp",):
                out.append(" . ")
            elif cmd == "mid":
                out.append(" divides ")
            elif cmd in ("lvert", "rvert", "Vert", "vert", "lVert", "rVert"):
                # Biến thể \vert đứng TRẦN (không đi sau \left/\right). Bản có
                # hướng (\lvert/\rvert, \lVert/\rVert) ghép cặp được nên map
                # thẳng sang lline/rline (đơn) hay ldline/rdline (đôi). Bản
                # KHÔNG hướng (\vert, \Vert) ghép cặp bằng bộ đếm luân phiên:
                # lần lẻ = mở (lline/ldline), lần chẵn = đóng (rline/rdline).
                if cmd == "vert":
                    vert_count += 1
                    out.append(" lline " if vert_count % 2 == 1 else " rline ")
                elif cmd == "Vert":
                    dvert_count += 1
                    out.append(" ldline " if dvert_count % 2 == 1 else " rdline ")
                else:
                    out.append({"lvert": " lline ", "rvert": " rline ",
                                "lVert": " ldline ", "rVert": " rdline "}[cmd])
            elif cmd == "colon":
                out.append(" : ")
            elif cmd == "iff":
                out.append(" dlrarrow ")
            elif cmd == "implies":
                out.append(" drarrow ")
            elif cmd == "impliedby":
                out.append(" dlarrow ")
            elif cmd in ("big", "Big", "bigg", "Bigg", "bigl", "bigr",
                         "Bigl", "Bigr", "biggl", "biggr", "Biggl", "Biggr"):
                # Các biến thể cỡ dấu ngoặc (\big( \Big( ...) không bắt buộc đi theo
                # cặp \left \right; StarMath không phân biệt cỡ nên chỉ cần lấy
                # đúng ký tự ngoặc, bỏ qua phần chỉ định cỡ.
                d, i = _read_delim(s, i)
                out.append(" " + BRACKET_MAP.get(d, d) + " ")
            elif cmd == "underbrace":
                # \underbrace{X}_{label} → {X} csub { "⏟" label }
                # Thay vì dùng từ khóa underbrace bị lỗi OLE trong Word, ta dùng ký tự Unicode móc dưới U+23DF (⏟)
                # làm text literal bên trong csub. Giải pháp này giúp vẽ móc dưới đẹp mắt, giữ đầy đủ ký tự
                # trong MathType Editor và tương thích 100%.
                arg, i = _read_arg(s, i)
                # Đọc label chỉ số dưới nếu có _{...}
                j = i
                while j < n and s[j] == ' ':
                    j += 1
                if j < n and s[j] == '_':
                    j += 1
                    label, j = _read_arg(s, j)
                    out.append(" {" + _process(arg) + "} csub { \"\u23DF\" {" + _script_body(label) + "} } ")
                    i = j
                else:
                    out.append(" {" + _process(arg) + "} csub { \"\u23DF\" } ")
            elif cmd == "overbrace":
                # \overbrace{X}^{label} → {X} csup { "⏞" label }
                # Sử dụng ký tự Unicode móc trên U+23DE (⏞) làm text literal bên trong csup.
                arg, i = _read_arg(s, i)
                # Đọc label chỉ số trên nếu có ^{...}
                j = i
                while j < n and s[j] == ' ':
                    j += 1
                if j < n and s[j] == '^':
                    j += 1
                    label, j = _read_arg(s, j)
                    out.append(" {" + _process(arg) + "} csup { \"\u23DE\" {" + _script_body(label) + "} } ")
                    i = j
                else:
                    out.append(" {" + _process(arg) + "} csup { \"\u23DE\" } ")
            elif cmd == "cancel":
                # \cancel{X} → overstrike{X}
                # Phục hồi overstrike để LibreOffice Math sinh OLE MTEF chuẩn, kích đúp MathType không bị rỗng.
                arg, i = _read_arg(s, i)
                out.append(" overstrike {" + _process(arg) + "} ")
            elif cmd in ("not", "slashed"):
                # 🔒 [LOCK-FIX-11]: \not{X} / \not\partial → overstrike{X}: ký pháp gạch chéo Feynman.
                # _read_arg đọc được cả {arg} lẫn \cmd đơn (vd \not\partial).
                arg, i = _read_arg(s, i)
                out.append(" overstrike {" + _process(arg) + "} ")
            elif cmd in ("xrightarrow", "xLeftrightarrow", "xRightarrow"):
                # \xrightarrow{label} → mũi tên phải có nhãn phía trên
                # Đọc optional bracket [...] nếu có (nhãn phía dưới), bỏ qua
                if i < n and s[i] == '[':
                    j = s.index(']', i)
                    i = j + 1
                label, i = _read_arg(s, i)
                out.append(" {rightarrow} csup {" + _process(label) + "} ")
            elif cmd in ("xleftarrow", "xLeftarrow"):
                # \xleftarrow{label} → mũi tên trái có nhãn phía trên
                if i < n and s[i] == '[':
                    j = s.index(']', i)
                    i = j + 1
                label, i = _read_arg(s, i)
                out.append(" {leftarrow} csup {" + _process(label) + "} ")
            elif cmd == "stackrel":
                # \stackrel{top}{base} → {"base"} csup {top}
                # Nếu base là toán tử quan hệ đứng độc lập, bọc trong dấu nháy kép để tránh lỗi ¿.
                top, i = _read_arg(s, i)
                base, i = _read_arg(s, i)
                processed_base = _process(base)
                stripped_base = processed_base.strip()
                if stripped_base in ('=', '<', '>', '+', '-', '*', '/') or stripped_base in (
                    'approx', 'equiv', 'simeq', 'sim', 'cong', 'notin', 'in', 'subseteq', 'subset', 'supseteq', 'supset', 'rightarrow', 'leftarrow'
                ):
                    out.append(" {\"" + stripped_base + "\"} csup {" + _process(top) + "} ")
                else:
                    out.append(" {" + processed_base + "} csup {" + _process(top) + "} ")
            else:
                # Không rõ lệnh: giữ tên (để người dùng tự soát lại)
                out.append(" " + cmd + " ")
            continue

        # "rsub{..}" / "rsup{..}" trần (không \\) đứng ngay sau 1 biểu thức —
        # đây thực chất là cú pháp StarMath postfix có sẵn ĐÚNG trong nguồn
        # (kiểu "{∫}rsub{a}rsup{b}..."), không phải lệnh LaTeX. Nếu không nhận
        # diện, "rsub"/"rsup" sẽ lộ ra thành chữ thô dính liền vào biểu thức
        # trước đó thay vì trở thành chỉ số dưới/trên đúng nghĩa.
        if s[i:i + 4] in ("rsub", "rsup") and (i == 0 or not s[i - 1].isalnum()):
            j = i + 4
            while j < n and s[j] == " ":
                j += 1
            if j < n and s[j] == "{":
                arg, k = _read_arg(s, j)
                word = s[i:i + 4]
                # Nếu rsub/rsup đứng ngay sau MỘT TOÁN TỬ LỚN (int, sum, prod,
                # lim...) thì đó là CẬN của toán tử, không phải chỉ số dưới/trên
                # bên phải. Ví dụ nguồn "{∫}rsub{a}rsup{b}": ∫ đã thành "int",
                # rsub{a}/rsup{b} phải là "from {a}"/"to {b}", nếu để nguyên
                # "int rsub {a} rsup {b}" StarMath vẽ a,b thành chỉ số cạnh ∫
                # (mất cận). Dò NGƯỢC qua các nhóm from/to đã xuất (vd rsup đến
                # sau khi rsub đã thành "from {a}") để tìm toán tử gốc.
                if _preceded_by_limit_operator(out):
                    word = {"rsub": "from", "rsup": "to"}[word]
                out.append(" " + word + " {" + _process(arg) + "} ")
                i = k
                continue

        if c in "{}":
            i += 1
            continue  # nhóm trần {..} không có lệnh phía trước: bỏ ngoặc, giữ nội dung
        if c == "^":
            arg, j = _read_arg(s, i + 1)
            out.append("^{" + _script_body(arg) + "}")
            i = j
            continue
        if c == "_":
            arg, j = _read_arg(s, i + 1)
            out.append("_{" + _script_body(arg) + "}")
            i = j
            continue

        if c in UNICODE_OPERATORS:
            # Toán tử gõ bằng ký tự Unicode thật (∫, ∑, ∏...) — xử lý y hệt lệnh
            # \int/\sum: đọc luôn cận _{}^{} (hoặc from/to) đi kèm để không mất
            # bound. Ví dụ đề Câu 5: "∫ _{0}^{2} (x^2-x) dx".
            word = UNICODE_OPERATORS[c]
            i += 1
            lo, hi, i = _read_limits(s, i)
            piece = " " + word
            if lo is not None:
                piece += " from {" + _process(lo) + "}"
            if hi is not None:
                piece += " to {" + _process(hi) + "}"
            out.append(piece + " ")
            continue

        if c == "|":
            # Dấu gạch dọc ĐỨNG GIỮA biểu thức (không thuộc cặp \left|...\right|),
            # điển hình là xác suất có điều kiện P(B|A) hay tập hợp {x | x>0}.
            # StarMath hiểu "|" trần là toán tử OR (∨) -> render sai thành P(B∨A).
            # Thay vì "mline" (gây lỗi ¿), dùng string literal "|"
            out.append(' "|" ')
            i += 1
            continue

        if c == "%":
            # % trần trong công thức (vd $2%$) — không phải lệnh LaTeX, chỉ là
            # ký tự phần trăm thật. Phải bọc literal, nếu không StarMath sẽ
            # hiểu % là tiền tố ký hiệu (%pi, %alpha...) và báo lỗi cú pháp.
            out.append(' "%" ')
            i += 1
            continue

        if c == ";":
            # Dấu chấm phẩy trong công thức (vd khoảng [-3; 3) của toán VN).
            # StarMath dùng ";" làm ký tự phân tách tham số trong một số cấu
            # trúc — nếu gặp ";" ở vị trí không mong đợi, sẽ hiển thị ¿
            # (glyph lỗi). Bọc thành chuỗi literal ";" để giữ nguyên ký tự.
            out.append(' ";" ')
            i += 1
            continue

        if c.isascii() and c.isalpha():
            # Gom trọn cụm chữ cái ASCII liền nhau. StarMath tra CẢ CỤM trong
            # bảng từ khoá: nếu trùng (không phân biệt hoa/thường) nó vẽ KÝ HIỆU
            # thay vì các chữ. Nhãn hình học 2 chữ hay va phải: "IM"->ℑ, "IN"->∈,
            # "RE"->ℜ, "OR"->∨. Chèn khoảng trắng giữa các chữ để StarMath tách
            # thành từng token đơn (không còn là từ khoá) — hiển thị vẫn y hệt.
            j = i
            while j < n and s[j].isascii() and s[j].isalpha():
                j += 1
            run = s[i:j]
            if run.lower() in STARMATH_RESERVED:
                out.append(" ".join(run))
            else:
                out.append(run)
            i = j
            continue

        out.append(c)
        i += 1

    text = "".join(out)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def _read_delim(s, i):
    while i < len(s) and s[i] == " ":
        i += 1
    if s[i:i + 1] == "\\":
        m = re.match(r"\\[a-zA-Z]+|\\.", s[i:])
        tok = m.group(0)
        return tok, i + len(tok)
    return s[i], i + 1


def _read_limits(s, i):
    """Đọc _{...}^{...} hoặc ^{...}_{...} ngay sau 1 lệnh (\\sum, \\int, ...).
    Cũng nhận diện luôn cú pháp cận trên/dưới kiểu StarMath postfix lẫn trong
    nguồn: "from{a}" (cận dưới) và "to{b}"/"\\to{b}" (cận trên), kiểu
    "\\int from{a}\\to{b}..." — nếu không nhận diện, "from"/"to" sẽ lộ ra
    thành chữ thô dính liền thay vì trở thành đúng cận trên/dưới của tích phân."""
    lo = hi = None
    while i < len(s) and s[i] == " ":
        i += 1
    for _ in range(2):
        if i < len(s) and s[i] == "_":
            lo, i = _read_arg(s, i + 1)
        elif i < len(s) and s[i] == "^":
            hi, i = _read_arg(s, i + 1)
        elif s[i:i + 4] == "from" and _next_nonspace_is_brace(s, i + 4):
            j = i + 4
            while j < len(s) and s[j] == " ":
                j += 1
            lo, i = _read_arg(s, j)
        elif s[i:i + 3] == "\\to" and _next_nonspace_is_brace(s, i + 3):
            j = i + 3
            while j < len(s) and s[j] == " ":
                j += 1
            hi, i = _read_arg(s, j)
        elif s[i:i + 2] == "to" and _next_nonspace_is_brace(s, i + 2):
            j = i + 2
            while j < len(s) and s[j] == " ":
                j += 1
            hi, i = _read_arg(s, j)
        else:
            break
        while i < len(s) and s[i] == " ":
            i += 1
    return lo, hi, i


def _next_nonspace_is_brace(s, i):
    while i < len(s) and s[i] == " ":
        i += 1
    return i < len(s) and s[i] == "{"


if __name__ == "__main__":
    tests = [
        r"\frac{-b \pm \sqrt{b^2 - 4ac}}{2a}",
        r"\sum_{i=1}^{n} i = \frac{n(n+1)}{2}",
        r"\int_{a}^{b} f(x)\,dx = F(b) - F(a)",
        r"\lim_{x \to 0} \frac{\sin x}{x} = 1",
        r"\sqrt[3]{x^2+y^2}",
        r"e^{i\pi} + 1 = 0",
        # --- các trường hợp lấy từ đề DE44 / anle (kiểm tra hồi quy) ---
        r"\overset{\rightarrow}{n_{1}}=\left(0\,;\,-4\,;\,3\right)",
        r"\left(\overset{\rightarrow}{OD},\overset{\rightarrow}{OB}\right)",
        r"\overrightarrow{AB} + \overrightarrow{BC}",
        r"\left\{\begin{array}{l} x=-300+80t \\ y=-1000+100t \\ z=100\sqrt[]{11}\end{array}\right.(t\in\mathbb{R})",
        r"A\cos(\omega t+\varphi)",
        r"x(t)=Acos(\omega t+\varphi)",
        r"\frac{a\sqrt[]{6}}{2}",
        # --- các lệnh mới bổ sung ---
        r"\dfrac{a}{b} + \tfrac{1}{2}",
        r"\boxed{x=1}",
        r"12 \equiv 2 \pmod{5}",
        r"a \bmod b",
        r"\{x \mid x>0\}",
        r"p \implies q \iff r",
        r"\big( x+1 \big) \cdot \Big[ y-2 \Big]",
        # --- các lệnh mới bổ sung (đợt sửa lỗi từ file anle / 1783746580495_DE44 / đề Kết nối tri thức) ---
        r"x(t)=Acos\left(\omega t+\varphi\right)",       # hàm dính liền + theo sau là \left( chứ không phải (
        r"F(x)=ae^{x}+bcosx+C",                            # hệ số dính trước LẪN biến dính sau, không \
        r"y=3e^{x}+sinx",                                   # hàm dính liền biến số phía sau, không \
        r" u \vec =\left ( { 5;-4;-7 } \right ) ",          # \vec đặt hậu tố (sau biến) thay vì \vec{u}
        r" n \vec _{ 4 }  =\left ( { 2;-1;5 } \right ). ",  # \vec hậu tố + có chỉ số dưới đi kèm
        r"\overset{\rightarrow}{OD}",                       # \vec chuẩn (\overset) vẫn phải chạy đúng như cũ
        r"widevec{n}=\left( 1 ; 3 ; 1\right)",              # lệnh accent StarMath bị gõ thiếu dấu \
        r"P\left( acute{B}\right)",                          # "acute{B}" thiếu dấu \ (B ngang/phẩy)
        r"widevec{{n}rsub{P}}=\left[ widevec{AB} \right]", # widevec lồng rsub lồng nhau
        r"{∫}rsub{a}rsup{b}f\left( x\right) d x = F\left( b\right) - F\left( a\right)",  # rsub/rsup trần
        r"I ={∫}rsub{0}rsup{\frac{π}{3}}\cos x d x",        # rsup có nội dung lồng dấu ngoặc {}
        r"V =\int from{a}\to{b}{S\left( x \right)}dx .",    # cận tích phân kiểu StarMath postfix from{}\to{}
        r"V = π\int from{a}\to{b}{f}^{2}\left( x\right) dx", # tương tự, có thêm số mũ
        # --- các biến thể \vert / \Vert (giá trị tuyệt đối, chuẩn) ---
        r"\left| x-2 \right|",                              # abs kiểu "|" thường (đã chạy trước đó)
        r"\left\vert x-2 \right\vert",                       # \vert thay cho "|" trong cặp \left \right
        r"\lvert a \rvert + \lVert v \rVert",                # \lvert/\rvert (đơn) và \lVert/\rVert (đôi) TRẦN
        r"\left\Vert \vec{u} \right\Vert = 1",              # \Vert (chuẩn) trong cặp \left \right
        r"f(x)=\vert x \vert",                                # \vert TRẦN không đi cặp
        # --- tích phân đề thật (gemini2): phân số dưới ∫ và |..| trong ∫ ---
        r"B = \int_{0}^{\sqrt{3}} \frac{x}{\sqrt{x^2 + 1}} dx",  # Câu 7: cả \frac phải nằm dưới ∫, không lọt ∫ vào tử
        r"D = \int_{0}^{2} \vert{}x^2 - x\vert{} dx",            # Câu 9: cặp \vert{} = |..| (lline/rline), không phải mline(¿)
    ]
    for t in tests:
        print(t, " -> ", convert(t))
