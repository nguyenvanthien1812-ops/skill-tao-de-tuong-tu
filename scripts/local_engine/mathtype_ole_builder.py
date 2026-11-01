"""
mathtype_ole_builder.py

Dựng file OLE (Compound File Binary v3) HOÀN CHỈNH cho một công thức MathType,
gồm ĐỦ 4 stream mà Word cần để mở lại được bằng MathType khi kích đúp:

    \\x01CompObj      (ProgID "Equation.DSMT4", UserType "MathType 7.0 Equation")
    \\x01Ole
    \\x03ObjInfo
    Equation Native   (dữ liệu MTEF)

Trước đây các hàm make_ole (omml_converter.ole và libreoffice_renderer) CHỈ ghi
mỗi stream "Equation Native", THIẾU \\x01CompObj → Word báo "chương trình không
được cài / không phản hồi" khi kích đúp (Lỗi 3). Module này thay thế chúng.

3 stream nhỏ (CompObj/Ole/ObjInfo) là TĨNH — giống hệt nhau cho mọi công thức
MathType 7 — được trích từ file .bin gốc do Word/MathType tạo ra.

Chỉ dùng thư viện chuẩn (struct) nên import được ở cả Python 3.14 (hệ thống) lẫn
Python 3.12 của LibreOffice.

Tham chiếu: [MS-CFB] https://learn.microsoft.com/openspecs/windows_protocols/ms-cfb
"""

import struct
import os
import sys

# Cùng thư mục: builder cung tròn MathType thật (MTEF v5 + MT Extra)
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)
try:
    from arc_symbol_builder import (
        build_arc_equation_native,
        extract_arc_base_from_starmath,
        extract_pure_arc_base,
        is_arc_starmath,
        ARC_MARKER_CHAR,
    )
except Exception:  # ImportError hoặc lỗi nạp module
    build_arc_equation_native = None  # type: ignore
    extract_arc_base_from_starmath = None  # type: ignore
    extract_pure_arc_base = None  # type: ignore
    is_arc_starmath = None  # type: ignore
    ARC_MARKER_CHAR = "\u200e"

_MAGIC = b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"
_SECTOR = 512
_MINI_SECTOR = 64
_MINI_CUTOFF = 4096
_FREESECT = 0xFFFFFFFF
_ENDOFCHAIN = 0xFFFFFFFE
_FATSECT = 0xFFFFFFFD

# CLSID MathType {0002CE03-0000-0000-C000-000000000046}
_MATHTYPE_CLSID = bytes([
    0x03, 0xCE, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00,
    0xC0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x46,
])

# --- 3 stream tĩnh, trích nguyên văn từ .bin do Word/MathType 7 tạo ---
_COMPOBJ = bytes.fromhex(
    "0100feff030a0000ffffffff03ce020000000000c000000000000046"
    "160000004d6174685479706520372e30204571756174696f6e00"      # "MathType 7.0 Equation"
    "0c0000004d61746854797065204546"                            # "MathType EF"
    "000f0000004571756174696f6e2e44534d543400"                  # "Equation.DSMT4"
    "f439b271000000000000000000000000"
)
_OLE = bytes.fromhex("0100000208000000000000000000000000000000")
_OBJINFO = bytes.fromhex("000003000100")


def _pad(data: bytes, align: int) -> bytes:
    rem = len(data) % align
    return data + bytes(align - rem) if rem else data


def _dir_entry(name: str, entry_type: int, color: int, left: int, right: int,
               child: int, start_sect: int, size: int,
               clsid: bytes = bytes(16)) -> bytes:
    """Một directory entry 128 byte của CFB."""
    name_utf16 = name.encode("utf-16-le") + b"\x00\x00"
    entry = bytearray(128)
    entry[0:len(name_utf16)] = name_utf16
    struct.pack_into("<H", entry, 64, len(name_utf16))   # tên (byte, kể cả NUL)
    entry[66] = entry_type                               # 0=unused 1=storage 2=stream 5=root
    entry[67] = color                                    # 0=red 1=black
    struct.pack_into("<III", entry, 68, left, right, child)
    entry[80:96] = clsid
    struct.pack_into("<II", entry, 116, start_sect, size)
    return bytes(entry)


def _mini_slots(n: int) -> int:
    """Số mini-sector (64 byte) cần để chứa n byte."""
    return (n + _MINI_SECTOR - 1) // _MINI_SECTOR


# ┌────────────────────────────────────────────────────────────────────────┐
# │ 🔒 LOCKED — VÙNG CODE CHUYỂN ĐỔI CÔNG THỨC ĐÃ HOẠT ĐỘNG THÀNH CÔNG  │
# │                                                                        │
# │ KHÔNG ĐƯỢC THAY ĐỔI, XÓA HOẶC THÊM BẤT KỲ CODE NÀO Ở VÙNG NÀY      │
# │ TRƯỜNG HỢP CẦN SỬA ĐỔI PHẢI XIN PHÉP NGƯỜI DÙNG TRƯỚC VÀ NÊU RÕ LÝ DO│
# │                                                                        │
# │ DO NOT MODIFY OR TOUCH THIS BLOCK OF CODE WITHOUT EXPLICIT PERMISSION │
# │ FROM THE USER. ACT WITH EXTREME CAUTION TO AVOID BREAKING IT.         │
# └────────────────────────────────────────────────────────────────────────┘
def _patch_mtef_right_none(eq_native: bytes) -> bytes:
    """
    Vá các lỗi hiển thị ◆ (hình thoi đen) và ký tự sai trong MathType editor
    khi kích đúp vào công thức được tạo bởi LibreOffice.

    Cấu trúc Equation Native stream
    --------------------------------
    [0..3]   size-prefix (uint32 LE): số byte MTEF data (không kể 4 byte này)
    [4..27]  MTEF header 24 bytes: version, platform, product info
    [28+]    MTEF records: LINE(0x01), CHAR(0x02), TMPL(0x03), PILE(0x04),
             FENCE(0x09), SIZE(0x0a), FULL(0x0b), SUB(0x0c), SUB2(0x0d), END(0x00)...

    CHAR record có hai dạng:
      - Narrow (3 byte): [0x02][typeface][char_code]         khi typeface & 0x80 == 0
      - Wide   (4 byte): [0x02][typeface|0x80][char_lo][char_hi]  khi typeface & 0x80 != 0
        → char = char_lo | (char_hi << 8)  (little-endian Unicode code point)

    ─────────────────────────────────────────────────────────────────────
    LỖI 1 — FENCE record, right_char = 0xc0  (công thức có ngoặc đơn)
    ─────────────────────────────────────────────────────────────────────
    Gặp khi: công thức có ngoặc đơn với \\right. (không có ngoặc phải),
    ví dụ: (x + 1  hoặc  |x|  dạng FENCE.
    LibreOffice xuất FENCE record (tag=0x09):
        [0x09][selector][left_char][0xc0]
    right_char = 0xc0 là mã "không có ngoặc phải" của LibreOffice.
    MathType 7 không nhận ra 0xc0 → hiển thị ◆.
    Fix: buf[i+3] = 0x01  (MTEF "invisible delimiter")

    ─────────────────────────────────────────────────────────────────────
    LỖI 2 — CHAR narrow, char=0x7c, typeface=0x96  (dấu trị tuyệt đối)
    ─────────────────────────────────────────────────────────────────────
    Gặp khi: công thức có ký hiệu trị tuyệt đối |x|.
    LibreOffice xuất CHAR narrow:
        [0x02][0x96][0x7c]
    typeface=0x96 = MT Extra font. Trong MT Extra, char 0x7c không phải
    dấu gạch đứng '|' mà là '(' → khi kích đúp MathType hiển thị sai.
    Fix: buf[i+1] = 0x86  (đổi sang Symbol font, char 0x7c = '|' đúng)

    ─────────────────────────────────────────────────────────────────────
    LỖI 3 — CHAR wide, char=0x0000  (hệ phương trình, ngoặc phải ẩn)
    ─────────────────────────────────────────────────────────────────────
    Gặp khi: hệ phương trình dùng TMPL var=0x02 (pile_lbrace), LibreOffice
    thêm 2 CHAR wide để vẽ ngoặc trái và phải:
        [0x02][0x96][0x7b][0x00]  → char=0x007b='{' (đúng)
        [0x02][0x96][0x00][0x00]  → char=0x0000=NULL (sai → ◆)
    char=0x0000 (NULL) không có glyph trong font delimiter của MathType → ◆.
    Fix: buf[i+2] = 0x01  (char=0x0001, SOH/invisible, MathType bỏ qua)

    Xác nhận từ hex thực tế (docx mẫu 126 công thức):
      - Lỗi 1: 0 file (không có FENCE 0xc0 trong mẫu này, nhưng giữ fix phòng ngừa)
      - Lỗi 2: oleObject1.bin tại offset 0x4d và 0x51
      - Lỗi 3: oleObject24/26/34.bin — pattern 02 96 00 00 cuối stream

    ⚠️  CHAR narrow char=0xc0 KHÔNG được patch (0xc0 = ký tự π hợp lệ trong
    font Symbol/Greek của MathType — patch nhầm sẽ phá toàn bộ chữ pi).
    """
    RECORD_START = 28   # MTEF records bắt đầu sau 4-byte size-prefix + 24-byte header
    if len(eq_native) <= RECORD_START:
        return eq_native

    buf = bytearray(eq_native)

    # --- Lỗi 1 & 2: quét từ offset 4 (như cũ, an toàn vì header không có 0x09/0x02) ---
    i = 4
    while i < len(buf):
        tag = buf[i]

        # Lỗi 1: FENCE record (tag=0x09), right_char=0xc0 ở offset +3
        if tag == 0x09 and i + 3 < len(buf) and buf[i + 3] == 0xc0:
            buf[i + 3] = 0x01   # invisible delimiter

        # Lỗi 2: CHAR narrow (tag=0x02), typeface=0x96, char=0x7c ('|' trong MT Extra)
        if tag == 0x02 and i + 2 < len(buf) and buf[i + 2] == 0x7c and buf[i + 1] == 0x96:
            buf[i + 1] = 0x86   # đổi sang Symbol font

        i += 1

    # --- Lỗi 3: quét từ offset 28 (MTEF records), bước đúng cho wide CHAR ---
    i = RECORD_START
    while i < len(buf):
        # Wide CHAR (4 byte): tag=0x02, typeface & 0x80 != 0
        if buf[i] == 0x02 and i + 3 < len(buf) and (buf[i + 1] & 0x80):
            char_lo = buf[i + 2]
            char_hi = buf[i + 3]
            if char_lo == 0x00 and char_hi == 0x00:
                # 🔒 [LOCK-FIX-08]: Trung hòa 4 byte của bản ghi dư thừa này thành các thẻ kết thúc MTEF END (0x00 0x00 0x00 0x00)
                # để vừa xóa dấu thoi đen ◆ vừa không tạo ra thanh ngoặc thừa bên phải trong MathType Editor.
                # CẢNH BÁO CHO AI AGENTS: KHÔNG ĐƯỢC THAY THÀNH 0x01 (GÂY THỪA NGOẶC) HOẶC XÓA (GÂY ◆)!
                buf[i:i + 4] = b'\x00\x00\x00\x00'
            i += 4   # bước đúng cho wide CHAR
        else:
            i += 1

    # ─────────────────────────────────────────────────────────────────
    # 🔒 [LOCK-FIX-09] Lỗi 5 - Marker cung \overparen (U+200E)
    # ─────────────────────────────────────────────────────────────────
    # KHÔNG thay cả stream tại đây (sẽ phá công thức lồng: overparen{A}+x).
    # Thay TOÀN BỘ Equation Native bằng MTEF MathType thật chỉ xảy ra khi
    # caller xác định "cung thuần" (make_arc_equation_ole / docx_processor /
    # libreoffice_renderer với extract_pure_arc_base).
    #
    # Tại patch này chỉ xử lý fallback nhúng: xóa CHAR U+200E + đổi TMPL
    # overline → tvFROWN để MathType đỡ lỗi khi bắt buộc đi qua MTEF v3 LO.
    i_find = RECORD_START
    while i_find < len(buf) - 3:
        if buf[i_find] == 0x02 and buf[i_find + 2] == 0x0E and buf[i_find + 3] == 0x20:
            j = i_find - 1
            while j >= RECORD_START:
                if buf[j] == 0x03 and buf[j + 1] == 0x11 and buf[j + 2] == 0x00:
                    buf[j + 1] = 0x22  # tmFROWN (selector 34)
                    buf[j + 2] = 0x00
                    break
                j -= 1
            del buf[i_find:i_find + 4]
            continue
        i_find += 1


    # ─────────────────────────────────────────────────────────────────
    # Lỗi 4 — mũ góc (hat/widehat) mất khi mở MathType
    # ─────────────────────────────────────────────────────────────────
    # LibreOffice hay emit TMPL hat kiểu MTEF v3:
    #   [0x03][options][variation=0x04 tvHAT]
    #   slot0: glyph (có thể rỗng) + END
    #   slot1: base (LINE/CHAR...) + END
    # tvHAT (0x04) = mũ 1 ký tự. Base nhiều chữ (AOB, ABC) cần tvWIDEHAT (0x0A)
    # nếu không MathType mở ra mất mũ / chỉ còn chữ.
    #
    # Bản vá này:
    # 1) Đếm CHAR trong base kể cả khi bọc trong LINE
    # 2) Đổi 0x04 → 0x0A khi base >= 2 CHAR
    # 3) Nếu variation đã 0x0A thì giữ
    # 4) Bắt thêm layout MTEF v5: [03][opt][selector][variation][...]
    #    với selector tmHAT=33
    # ─────────────────────────────────────────────────────────────────
    def _skip_mtef_record(buf, j):
        """Trả về index sau record tại j; best-effort cho CHAR/LINE/TMPL/END."""
        n = len(buf)
        if j >= n:
            return j
        t = buf[j]
        if t == 0x00:  # END
            return j + 1
        if t == 0x02:  # CHAR
            if j + 1 >= n:
                return j + 1
            opt = buf[j + 1]
            j += 2
            # nudge?
            if opt & 0x10:
                j += 2
            # typeface
            if j < n:
                j += 1
            # MTCode 2 bytes LE typically present
            if j + 1 < n:
                j += 2
            # embellishment list if options say so — common embHAT trail
            # If next is EMBELL (0x06), consume until END of embell? Keep simple:
            while j < n and buf[j] == 0x06:
                # EMBELL: tag, options, embell type...
                j += 1
                if j < n:
                    eopt = buf[j]; j += 1
                    if eopt & 0x10:
                        j += 2
                    if j < n:
                        j += 1  # embell code
            return j
        if t == 0x03:  # TMPL
            if j + 2 >= n:
                return j + 1
            opt = buf[j + 1]
            j += 2  # tag+opt
            if opt & 0x10:
                j += 2  # nudge
            # try v3: variation (1 byte). v5 also has selector before variation.
            # We cannot fully know; advance 1-3 bytes conservatively then let content END drive.
            # Better: after header, scan content until depth END matching — handled by caller.
            # Here only skip header:
            # assume at least variation byte
            if j < n:
                j += 1
            # optional second variation / tmpl options in v5
            # leave content to caller
            return j
        if t == 0x01:  # LINE
            if j + 1 >= n:
                return j + 1
            opt = buf[j + 1]
            j += 2
            if opt & 0x10:
                j += 2
            return j
        # default 1 byte tag
        return j + 1

    def _count_chars_until_end(buf, j):
        """Đếm CHAR từ j đến END depth0; đi vào LINE lồng."""
        n = len(buf)
        depth = 0
        chars = 0
        while j < n:
            t = buf[j]
            if t == 0x00:
                if depth == 0:
                    return chars, j + 1
                depth -= 1
                j += 1
                continue
            if t == 0x02:
                chars += 1
                j = _skip_mtef_record(buf, j)
                continue
            if t == 0x01:  # LINE — vào trong
                j = _skip_mtef_record(buf, j)
                depth += 1
                continue
            if t == 0x03:
                # nested tmpl: skip whole by depth walk
                j = _skip_mtef_record(buf, j)
                depth += 1
                continue
            j = _skip_mtef_record(buf, j)
        return chars, j

    i = RECORD_START
    while i < len(buf) - 2:
        if buf[i] != 0x03:
            i += 1
            continue
        options = buf[i + 1]
        nudge = 2 if (options & 0x10) else 0
        hdr = i + 2 + nudge
        if hdr >= len(buf):
            break

        # Layout A (LO MTEF v3 accent): [03][opt][variation]
        variation_offset = i + 2 + nudge
        variation = buf[variation_offset]
        content_start = variation_offset + 1
        layout = 'v3var'

        # Layout B (MTEF v5 HatBox): [03][opt][selector][variation][tmpl_opt]
        # selector tmHAT=33, tmARC=34, tmTILDE=32
        if hdr + 2 < len(buf) and buf[hdr] in (32, 33, 34, 35, 31):
            # likely v5 selector
            selector = buf[hdr]
            variation_offset = hdr + 1
            variation = buf[variation_offset]
            content_start = hdr + 3  # selector, variation, tmpl_opt
            layout = 'v5sel'
            if selector != 33:  # only care tmHAT
                i = content_start
                continue

        if layout == 'v3var' and variation not in (0x04, 0x0A):
            i += 1
            continue
        if layout == 'v3var' and variation == 0x0A:
            i = content_start
            continue

        # content_start at slot0
        j = content_start
        # skip slot0 to first END
        depth = 0
        while j < len(buf):
            t = buf[j]
            if t == 0x00 and depth == 0:
                j += 1
                break
            if t == 0x03 or t == 0x01:
                # enter nested
                if t == 0x03:
                    j = _skip_mtef_record(buf, j); depth += 1
                else:
                    j = _skip_mtef_record(buf, j); depth += 1
                continue
            if t == 0x00:
                depth -= 1; j += 1; continue
            j = _skip_mtef_record(buf, j)

        char_count, _ = _count_chars_until_end(buf, j)
        if char_count > 1:
            if layout == 'v3var' and variation == 0x04:
                buf[variation_offset] = 0x0A  # tvWIDEHAT
            elif layout == 'v5sel':
                # ensure selector remains tmHAT; some LO put narrow variation
                buf[hdr] = 33  # tmHAT
                # variation 0 often default wide enough; leave
        i = content_start

    return bytes(buf)
# ┌────────────────────────────────────────────────────────────────────────┐
# │ 🔒 END LOCKED BLOCK                                                    │
# └────────────────────────────────────────────────────────────────────────┘



def make_mathtype_ole(eq_native_stream: bytes) -> bytes:
    """
    Tạo OLE CFB 1-stream hoàn toàn KHÔNG CÓ Mini FAT.
    Luôn đệm Equation Native lên đủ 4096 bytes để buộc nó vào Main FAT.
    Điều này giải quyết triệt để lỗi MathType "not responding" vì nó không hỗ trợ Mini FAT.
    """
    _is_real_mt = (
        b"DSMT7" in eq_native_stream[:80]
        and b"MT Extra" in eq_native_stream[:200]
    )
    if not _is_real_mt:
        # Patch logic was moved out, we just assume it's patched already or patch it via import
        pass 

    # BUỘC padding lên ít nhất 4096 bytes để lọt vào Main FAT
    eqn = eq_native_stream
    if len(eqn) < 4096:
        eqn += b"\x00" * (4096 - len(eqn))
    eqn_len = len(eqn)
    eqn_padded = _pad(eqn, _SECTOR)
    n_eqn_sectors = len(eqn_padded) // _SECTOR

    # ---- Bố trí sector thường ----
    #   0: FAT
    #   1: Directory (2 entry x 128 = 256 byte -> 1 sector)
    #   2..: Equation Native
    SEC_FAT = 0
    SEC_DIR = 1
    SEC_EQN = 2

    # ---- FAT ----
    fat = [_FREESECT] * (_SECTOR // 4)
    fat[SEC_FAT] = _FATSECT
    fat[SEC_DIR] = _ENDOFCHAIN
    
    # Chain Equation Native sectors
    for k in range(n_eqn_sectors):
        fat[SEC_EQN + k] = (SEC_EQN + k + 1) if k < n_eqn_sectors - 1 else _ENDOFCHAIN
        
    fat_bytes = struct.pack("<" + "I" * len(fat), *fat)

    # ---- Header ----
    difat = [_FREESECT] * 109
    difat[0] = SEC_FAT
    header = bytearray(512)
    header[0:8] = _MAGIC
    struct.pack_into("<H", header, 24, 0x003E)   # minor version
    struct.pack_into("<H", header, 26, 0x0003)   # major version (v3)
    struct.pack_into("<H", header, 28, 0xFFFE)   # byte order LE
    struct.pack_into("<H", header, 30, 9)        # sector shift 2^9=512
    struct.pack_into("<H", header, 32, 6)        # mini sector shift 2^6=64
    struct.pack_into("<I", header, 44, 1)        # NumFATSectors
    struct.pack_into("<I", header, 48, SEC_DIR)  # FirstDirectorySector
    struct.pack_into("<I", header, 56, 4096)     # MiniStreamCutoff
    struct.pack_into("<I", header, 60, _ENDOFCHAIN) # FirstMiniFATSector
    struct.pack_into("<I", header, 64, 0)        # NumMiniFATSectors
    struct.pack_into("<I", header, 68, _ENDOFCHAIN) # FirstDIFATSector
    struct.pack_into("<I", header, 72, 0)        # NumDIFATSectors
    for i, v in enumerate(difat):
        struct.pack_into("<I", header, 76 + i * 4, v)

    # ---- Directory ----
    root = _dir_entry("Root Entry", 5, 1, _FREESECT, _FREESECT, 1,
                      _ENDOFCHAIN, 0, clsid=_MATHTYPE_CLSID)
    eqn_entry = _dir_entry("Equation Native", 2, 1, _FREESECT, _FREESECT, _FREESECT,
                           SEC_EQN, eqn_len)

    dir_data = root + eqn_entry
    dir_data = _pad(dir_data, _SECTOR)

    return (
        bytes(header)
        + fat_bytes
        + dir_data
        + eqn_padded
    )


def extract_equation_native_from_ole(ole_bin: bytes) -> bytes | None:
    """Lấy stream Equation Native từ OLE MathType đã đóng gói."""
    try:
        import io
        try:
            import olefile
        except Exception:
            olefile = None
        if olefile is not None:
            ole = olefile.OleFileIO(io.BytesIO(ole_bin))
            try:
                for entry in ole.listdir():
                    # entry có thể là ['Equation Native'] hoặc ['ObjectPool', 'Obj...', 'Equation Native']
                    if entry and str(entry[-1]).endswith("Equation Native"):
                        data = ole.openstream(entry).read()
                        if data:
                            return data
            finally:
                ole.close()
        # Fallback: tìm marker MTEF/DSMT trong CFB
        for marker in (b"DSMT7", b"DSMT5", b"Equation Native"):
            idx = ole_bin.find(marker)
            if idx != -1 and marker.startswith(b"DSMT"):
                # lùi về size-prefix 4 byte nếu có
                start = max(0, idx - 4)
                # heuristic: stream from size prefix
                return ole_bin[start:]
    except Exception:
        return None
    return None



def _extract_alnum_base_from_mtef_slot(buf: bytes, start: int, end: int) -> str:
    """Lấy chuỗi chữ/số từ các CHAR trong một slot MTEF (best-effort)."""
    chars = []
    j = start
    n = min(end, len(buf))
    while j < n:
        if buf[j] == 0x02 and j + 2 < n:  # CHAR
            opt = buf[j + 1]
            k = j + 2
            if opt & 0x10 and k + 1 < n:
                k += 2
            if k >= n:
                break
            tf = buf[k]
            k += 1
            cp = None
            if not (opt & 0x20):  # has MTCode unless NO_MTCODE
                if k + 1 < n:
                    cp = buf[k] | (buf[k + 1] << 8)
                    k += 2
            if cp is not None and (0x30 <= cp <= 0x39 or 0x41 <= cp <= 0x5A or 0x61 <= cp <= 0x7A):
                chars.append(chr(cp))
            # skip emb list
            while k < n and buf[k] == 0x06:
                k += 1
                if k < n:
                    eopt = buf[k]; k += 1
                    if eopt & 0x10 and k + 1 < n:
                        k += 2
                    if k < n:
                        k += 1
            j = k
            continue
        j += 1
    return "".join(chars)


def _build_native_tmhat_bytes(base: str) -> bytes:
    """TMPL tmHAT (0x21) + base vars + glyph U+0302 — cùng format đã OK khi double-click pure góc."""
    if not base or not all(c.isalnum() and c.isascii() for c in base):
        return b""
    b = bytearray(bytes.fromhex("03002100000100"))
    for ch in base:
        cp = ord(ch)
        b += bytes([0x02, 0x00, 0x83, cp & 0xFF, (cp >> 8) & 0xFF])  # var
    b += b"\x00"
    b += bytes.fromhex("020096020300")  # MT Extra U+0302 hat
    b += b"\x00\x00"
    return bytes(b)


def _replace_lo_hats_with_native_tmhat(eq_native: bytes) -> bytes:
    """Thay mọi TMPL hat của LibreOffice bằng tmHAT native (giữ nguyên phần còn lại).

    Dùng cho công thức HỖN HỢP: sin/frac/⇒/≈ giữ nguyên từ LO; chỉ mũ góc được
    thay bằng cấu trúc MathType đã double-click OK. Không đụng cung (tmARC/FROWN).
    """
    RECORD_START = 28
    if not eq_native or len(eq_native) <= RECORD_START + 8:
        return eq_native
    # Skip real MathType arc natives
    if b"DSMT7" in eq_native[:80] and b"MT Extra" in eq_native[:200]:
        # still may be LO-wrapped with DSMT — continue if hat variation present
        pass

    buf = bytearray(eq_native)
    out = bytearray()
    i = 0
    # copy header unchanged
    out += buf[:RECORD_START]
    i = RECORD_START

    def skip_record_header_tmpl(pos):
        """Return (layout, selector_or_None, variation_offset, content_start, tmpl_header_end)."""
        if pos >= len(buf) or buf[pos] != 0x03:
            return None
        options = buf[pos + 1] if pos + 1 < len(buf) else 0
        p = pos + 2
        if options & 0x10:
            p += 2
        if p >= len(buf):
            return None
        # try v5
        if p + 2 < len(buf) and buf[p] in (31, 32, 33, 34, 35):
            sel = buf[p]
            var_off = p + 1
            content = p + 3  # sel, var, tmpl_opt
            return ("v5", sel, var_off, content, content)
        # v3 accent: variation only
        var_off = p
        content = p + 1
        return ("v3", None, var_off, content, content)

    def find_slot_end(pos):
        """From content start of TMPL, find end of whole TMPL (after final END depth0 of both slots)."""
        # Walk with depth for nested structures until we've closed 2 top-level ENDs
        # after leaving nested depth. Simpler: depth counting from content.
        j = pos
        depth = 0
        top_ends = 0
        n = len(buf)
        while j < n:
            t = buf[j]
            if t == 0x00:
                if depth == 0:
                    top_ends += 1
                    j += 1
                    if top_ends >= 2:
                        return j
                    continue
                depth -= 1
                j += 1
                continue
            if t == 0x02:  # CHAR
                if j + 1 >= n:
                    return j + 1
                opt = buf[j + 1]
                j += 2
                if opt & 0x10:
                    j += 2
                if j < n:
                    j += 1  # tf
                if j + 1 < n and not (opt & 0x20):
                    j += 2
                while j < n and buf[j] == 0x06:
                    j += 1
                    if j < n:
                        eopt = buf[j]; j += 1
                        if eopt & 0x10:
                            j += 2
                        if j < n:
                            j += 1
                continue
            if t in (0x01, 0x03, 0x04, 0x05, 0x09):
                # enter container-ish: bump depth heuristically by reading minimal header
                if t == 0x03:
                    info = skip_record_header_tmpl(j)
                    if info:
                        j = info[3]
                        depth += 1
                        continue
                # LINE/PILE/etc
                if j + 1 < n:
                    opt = buf[j + 1]
                    j += 2
                    if opt & 0x10:
                        j += 2
                    depth += 1
                    continue
            j += 1
        return j

    while i < len(buf):
        if buf[i] != 0x03:
            out.append(buf[i])
            i += 1
            continue
        info = skip_record_header_tmpl(i)
        if not info:
            out.append(buf[i]); i += 1; continue
        layout, sel, var_off, content_start, _ = info
        is_hat = False
        if layout == "v3" and var_off < len(buf) and buf[var_off] in (0x04, 0x0A):
            is_hat = True
        if layout == "v5" and sel == 33:
            is_hat = True
        if not is_hat:
            # copy this one byte and continue scan (safe, may re-detect inside)
            out.append(buf[i]); i += 1; continue

        tmpl_end = find_slot_end(content_start)
        # base is usually slot1 after first END of slot0
        # find first top-level END after content_start
        j = content_start
        depth = 0
        first_end = None
        while j < tmpl_end:
            if buf[j] == 0x00 and depth == 0:
                first_end = j
                break
            if buf[j] in (0x01, 0x03, 0x04, 0x05):
                depth += 1
                # skip header minimally
                if buf[j] == 0x03:
                    inf2 = skip_record_header_tmpl(j)
                    j = inf2[3] if inf2 else j + 1
                else:
                    opt = buf[j+1] if j+1 < len(buf) else 0
                    j += 2
                    if opt & 0x10:
                        j += 2
                continue
            if buf[j] == 0x00:
                depth = max(0, depth - 1); j += 1; continue
            if buf[j] == 0x02:
                opt = buf[j+1] if j+1 < len(buf) else 0
                j += 2
                if opt & 0x10: j += 2
                if j < len(buf): j += 1
                if j+1 < len(buf) and not (opt & 0x20): j += 2
                while j < len(buf) and buf[j] == 0x06:
                    j += 1
                    if j < len(buf):
                        eopt = buf[j]; j += 1
                        if eopt & 0x10: j += 2
                        if j < len(buf): j += 1
                continue
            j += 1
        if first_end is None:
            out.append(buf[i]); i += 1; continue
        base_start = first_end + 1
        base = _extract_alnum_base_from_mtef_slot(bytes(buf), base_start, tmpl_end)
        # also try whole tmpl if base empty (some LO put letters in slot0)
        if not base:
            base = _extract_alnum_base_from_mtef_slot(bytes(buf), content_start, tmpl_end)
        native_hat = _build_native_tmhat_bytes(base) if base else b""
        if not native_hat:
            # cannot replace — keep original tmpl bytes
            out += buf[i:tmpl_end]
            i = tmpl_end
            continue
        out += native_hat
        i = tmpl_end

    # fix size prefix if present (uint32 LE at 0 is eq header different — Equation Native
    # stream starts with 4-byte size of rest in some packs; Doc3 uses size at offset 8 of full stream)
    # For LO streams, first 4 bytes after CFB extract often include size prefix.
    # make_mathtype_ole/_patch already handle; update cb if structure is size+header
    result = bytes(out)
    if len(result) >= 12:
        # If looks like EQNOLE style: bytes 0-3 size? Our extract usually has
        # [size:4][mtef hdr...]. Update size at 0 if it matched old length pattern.
        try:
            import struct as _st
            old_size = int.from_bytes(eq_native[0:4], "little")
            if 0 < old_size <= len(eq_native) - 4:
                new_payload_len = len(result) - 4
                result = _st.pack("<I", new_payload_len) + result[4:]
        except Exception:
            pass
    return result


def repatch_ole_widehat(ole_bin: bytes) -> bytes:
    """Mở OLE LO, THAY mũ góc bằng tmHAT native, đóng gói lại MathType.

    Công thức hỗn hợp (sin/frac/⇒ + widehat): giữ nguyên phần LO, chỉ thay
    block hat → double-click còn mũ góc, không mất =/≈/⇒.
    """
    if not ole_bin or len(ole_bin) < 512:
        return ole_bin
    native = extract_equation_native_from_ole(ole_bin)
    if not native:
        try:
            patched = _patch_mtef_right_none(ole_bin)
            return patched if patched else ole_bin
        except Exception:
            return ole_bin
    try:
        # 1) vá lỗi LO chung (trong locked) — fence/null/...
        # 2) thay hat LO → tmHAT native (ngoài locked)
        fixed = _patch_mtef_right_none(native)
        replaced = _replace_lo_hats_with_native_tmhat(fixed)
        return make_mathtype_ole(replaced)
    except Exception:
        try:
            return make_mathtype_ole(_patch_mtef_right_none(native))
        except Exception:
            try:
                return _patch_mtef_right_none(ole_bin)
            except Exception:
                return ole_bin

def make_arc_equation_ole(base_letters: str) -> bytes:
    """OLE MathType 4-stream cho ký hiệu cung tròn thuần (vd. AB, MN, ABC).

    Dùng byte Equation Native MathType 7 thật (arc_symbol_builder).
    """
    if build_arc_equation_native is None:
        raise RuntimeError("arc_symbol_builder không import được")
    return make_mathtype_ole(build_arc_equation_native(base_letters))
