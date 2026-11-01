# -*- coding: utf-8 -*-
"""build_doc3_mtef.py — MTEF v5 MathType giống Doc3 (1 object, cung tmFROWN)."""
from __future__ import annotations

import re
import struct
from pathlib import Path
from typing import Optional

# Doc3 Equation Native — lấy 219 byte đầu (hdr+fonts+size block)
_DOC3_FULL = Path(__file__).with_name("doc3_eq_native.bin")
_FALLBACK_DOC3 = Path("/home/user/doc3_eq_native.bin")


_PREFIX219_HEX = "1c0000000200c6c11c010000000000008838fa062ddf88000c003d06050100070844534d543700011357696e416c6c4261736963436f6465506167657300110554696d6573204e657720526f6d616e00110353796d626f6c001105436f7572696572204e65770011044d5420457874726100120008212f458f442f4150f4100f475f4150f21f1e4150f4150f4100f445f425f48f425f4100f4100f435f4100f48f45f42a5f48f48f4100f4100f40f48f417f48f4100f412a5f445f45f45f45f45f410f0c0100010001020202020002000101010003000100040000"


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


def _char_text(ch: str) -> bytes:
    return bytes([0x02, 0x00, 0x81, ord(ch), 0x00])


def _char_var(ch: str) -> bytes:
    return bytes([0x02, 0x00, 0x83, ord(ch), 0x00])


def _char_hat(ch: str) -> bytes:
    return bytes([0x02, 0x01, 0x81, ord(ch), 0x00, 0x06, 0x00, 0x09, 0x00])


def _chars_text(s: str) -> bytes:
    return b"".join(_char_text(c) for c in s)


def _chars_var(s: str) -> bytes:
    return b"".join(_char_var(c) for c in s)


def _tmpl_frac(num: str, den: str) -> bytes:
    b = bytearray(bytes.fromhex("03000b00000100"))
    b += _chars_text(num)
    b += bytes.fromhex("000100")
    b += _chars_text(den)
    b += bytes.fromhex("0000")
    return bytes(b)


def _tmpl_frown(base: str) -> bytes:
    b = bytearray(bytes.fromhex("03002200000100"))
    b += _chars_var(base)
    b += b"\x00"
    b += bytes.fromhex("020096222300")
    b += b"\x00\x00"
    return bytes(b)


def _tmpl_widehat(base: str) -> bytes:
    """Widehat — TMPL 0x0A, base = biến."""
    b = bytearray(bytes.fromhex("03000a00000100"))
    b += _chars_var(base)
    b += b"\x00\x00"
    return bytes(b)


def _line_start() -> bytes:
    return bytes.fromhex("0a01000100")


def build_arc_equation_native_doc3(base_letters: str) -> bytes:
    if not (base_letters and all(c.isalnum() and c.isascii() for c in base_letters)):
        raise ValueError("base_letters ASCII alnum")
    return _finalize(_line_start() + _tmpl_frown(base_letters))


def build_geometry_formula_native(latex: str) -> Optional[bytes]:
    """1 object MTEF v5 cho pure/mixed geometry có overparen (kiểu Doc3)."""
    if not latex:
        return None
    s = latex.strip()
    if s.startswith("$$") and s.endswith("$$"):
        s = s[2:-2].strip()
    elif s.startswith("$") and s.endswith("$"):
        s = s[1:-1].strip()
    s = re.sub(r"^\\(?:displaystyle|textstyle)\\s*", "", s)
    # keep spaces out for parsing
    s_nospace = re.sub(r"\s+", "", s)

    m = re.fullmatch(r"\\(?:overparen|wideparen|overarc)\{([A-Za-z0-9]+)\}", s_nospace)
    if m:
        return build_arc_equation_native_doc3(m.group(1))

    m_arc = re.search(r"\\(?:overparen|wideparen|overarc)\{([A-Za-z0-9]+)\}", s_nospace)
    if not m_arc:
        return None
    arc_base = m_arc.group(1)
    head = s_nospace[: m_arc.start()]
    if s_nospace[m_arc.end():]:
        return None

    rec = bytearray(_line_start())
    rest = head

    wh = re.match(r"\\widehat\{([A-Za-z0-9]+)\}(.*)$", rest)
    h1 = re.match(r"\\hat\{([A-Za-z0-9])\}(.*)$", rest)
    if wh:
        base, rest = wh.group(1), wh.group(2)
        if len(base) == 1:
            rec += _char_hat(base)
        else:
            rec += _tmpl_widehat(base)
    elif h1:
        rec += _char_hat(h1.group(1))
        rest = h1.group(2)
    else:
        while rest:
            h = re.match(r"\\hat\{([A-Za-z0-9])\}(.*)$", rest)
            if h:
                rec += _char_hat(h.group(1))
                rest = h.group(2)
                continue
            if rest[0] == "=" or rest.startswith("\\"):
                break
            if rest[0].isalnum():
                rec += _char_text(rest[0])
                rest = rest[1:]
                continue
            break

    if rest.startswith("="):
        rec += _char_var("=")
        rest = rest[1:]

    fr = re.match(r"\\frac\{([^{}]*)\}\{([^{}]*)\}(.*)$", rest)
    if fr:
        num, den, rest = fr.group(1), fr.group(2), fr.group(3)
        if not (re.fullmatch(r"[A-Za-z0-9]+", num) and re.fullmatch(r"[A-Za-z0-9]+", den)):
            return None
        rec += _tmpl_frac(num, den)

    if rest:
        if not re.fullmatch(r"[A-Za-z0-9]+", rest):
            return None
        rec += _chars_text(rest)

    rec += b"\x00"
    rec += _tmpl_frown(arc_base)
    return _finalize(bytes(rec))


def selftest():
    doc3 = Path("/home/user/doc3_extract/ObjectPool__1846005202_Equation Native").read_bytes()
    content = bytearray()
    content += _line_start()
    content += _char_text("B")
    content += _char_hat("A")
    content += _char_text("x")
    content += _char_var("=")
    content += _tmpl_frac("1", "2")
    content += _chars_text("sd")
    content += b"\x00"
    content += _tmpl_frown("ABC")
    got = _finalize(bytes(content))
    assert got[219:] == doc3[219:], "content mismatch"
    # cbObject may differ if prefix length same — full match preferred
    assert b"MT Extra" in got and b"DSMT7" in got
    print("OK Doc3 rebuild content, len", len(got), "doc3", len(doc3))
    # Note: full bytes may differ only in cbObject field if same
    if got != doc3:
        for i, (a, b) in enumerate(zip(got, doc3)):
            if a != b:
                print(f" first full diff @{i}: {a:02x} vs {b:02x}")
                break
        print(" lens", len(got), len(doc3))
    else:
        print("OK full Doc3 byte match")

    for s in [
        r"\overparen{AB}",
        r"\widehat{AOB}=sd\overparen{AB}",
        r"\widehat{ACB}=\frac{1}{2}sd\overparen{AB}",
        r"\widehat{BAx}=\frac{1}{2}sd\overparen{AB}",
    ]:
        b = build_geometry_formula_native(s)
        assert b and b"MT Extra" in b, s
        print("OK", s, len(b))


if __name__ == "__main__":
    selftest()
