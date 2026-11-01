"""
Minimal OLE Compound File Binary (CFB v3, 512-byte sectors) writer.

Creates a single-stream compound document containing one stream named
'Equation Native'.  Used to wrap MTEF data into a MathType OLE object
that can be embedded in a Word (.docx) file.

References:
  [MS-CFB] https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-cfb
"""

import struct

_MAGIC = b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"
_SECTOR = 512
_FREESECT = 0xFFFFFFFF
_ENDOFCHAIN = 0xFFFFFFFE
_FATSECT = 0xFFFFFFFD
_DIFSECT = 0xFFFFFFFC


def _pad(data: bytes, align: int) -> bytes:
    rem = len(data) % align
    return data + bytes(align - rem) if rem else data


def _utf16le(s: str) -> bytes:
    return s.encode("utf-16-le")


def _dir_entry(
    name: str,
    entry_type: int,  # 0=unused, 1=storage, 2=stream, 5=root
    color: int,  # 0=red, 1=black
    child: int,
    left: int,
    right: int,
    start_sect: int,
    size: int,
    clsid: bytes = bytes(16),
) -> bytes:
    name_utf16 = _utf16le(name) + b"\x00\x00"
    name_len = len(name_utf16)
    entry = bytearray(128)
    entry[0 : len(name_utf16)] = name_utf16
    struct.pack_into("<H", entry, 64, name_len)
    entry[66] = entry_type
    entry[67] = color
    struct.pack_into("<III", entry, 68, left, right, child)  # left, right, child
    entry[80:96] = clsid
    struct.pack_into("<II", entry, 116, start_sect, size)
    return bytes(entry)


_MINI_CUTOFF = 4096  # streams < this go to mini-stream; we avoid that by padding


def make_ole(stream_data: bytes) -> bytes:
    """
    Return bytes of a minimal OLE CFB containing one stream called
    'Equation Native' with the given content.
    """
    # Ensure stream is >= mini-stream cutoff so it uses regular sectors.
    # Extra zero bytes are harmless: the EQNOLEFILEHDR inside stream_data
    # already encodes the real data length so parsers stop at the right place.
    if len(stream_data) < _MINI_CUTOFF:
        stream_data = stream_data + bytes(_MINI_CUTOFF - len(stream_data))
    # Pad stream to sector boundary
    padded = _pad(stream_data, _SECTOR)
    n_data_sectors = len(padded) // _SECTOR

    # Sector layout:
    #   sector 0  → FAT
    #   sector 1  → Directory
    #   sectors 2 … (2 + n_data - 1) → stream data

    # ── FAT sector ───────────────────────────────────────────────────────────
    fat = [_FREESECT] * (_SECTOR // 4)
    fat[0] = _FATSECT  # sector 0 is FAT itself
    fat[1] = _ENDOFCHAIN  # sector 1 = directory (single sector)
    for i in range(n_data_sectors):
        if i < n_data_sectors - 1:
            fat[2 + i] = 2 + i + 1  # chain to next data sector
        else:
            fat[2 + i] = _ENDOFCHAIN  # last data sector
    fat_bytes = struct.pack("<" + "I" * len(fat), *fat)

    # ── DIFAT in header: first 109 FAT sector locations ─────────────────────
    difat = [_FREESECT] * 109
    difat[0] = 0  # sector 0 is the only FAT sector

    # ── CFB header (512 bytes) ────────────────────────────────────────────────
    header = bytearray(512)
    header[0:8] = _MAGIC
    # CLSID: zeros
    struct.pack_into("<H", header, 24, 0x003E)  # minor version
    struct.pack_into("<H", header, 26, 0x0003)  # major version (v3)
    struct.pack_into("<H", header, 28, 0xFFFE)  # byte order LE
    struct.pack_into("<H", header, 30, 9)  # sector size shift (2^9=512)
    struct.pack_into("<H", header, 32, 6)  # mini sector size shift (2^6=64)
    # [MS-CFB] header field offsets (v3):
    #  40: NumDirectorySectors  (0 for v3 — pre-zeroed)
    #  44: NumFATSectors
    #  48: FirstDirectorySectorLocation
    #  52: TransactionSignatureNumber   (0 — pre-zeroed)
    #  56: MiniStreamCutoffSize
    #  60: FirstMiniFATSectorLocation
    #  64: NumMiniFATSectors
    #  68: FirstDIFATSectorLocation
    #  72: NumDIFATSectors
    #  76: DIFAT array (109 × 4 bytes = 436 bytes → total 512)
    struct.pack_into("<I", header, 44, 1)  # NumFATSectors = 1
    struct.pack_into("<I", header, 48, 1)  # FirstDirectorySector = 1
    struct.pack_into("<I", header, 56, 0x1000)  # MiniStreamCutoffSize = 4096
    struct.pack_into("<I", header, 60, _ENDOFCHAIN)  # FirstMiniFATSector = none
    struct.pack_into("<I", header, 64, 0)  # NumMiniFATSectors = 0
    struct.pack_into("<I", header, 68, _ENDOFCHAIN)  # FirstDIFATSector = none
    struct.pack_into("<I", header, 72, 0)  # NumDIFATSectors = 0
    for i, v in enumerate(difat):
        struct.pack_into("<I", header, 76 + i * 4, v)  # DIFAT array at offset 76

    # ── Directory sector (sector 1) ───────────────────────────────────────────
    # MathType CLSID for root entry: {0002CE02-0000-0000-C000-000000000046}
    mathtype_clsid = bytes(
        [
            0x02,
            0xCE,
            0x02,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0xC0,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x46,
        ]
    )
    root_entry = _dir_entry(
        "Root Entry",
        entry_type=5,
        color=1,
        child=1,
        left=_FREESECT,
        right=_FREESECT,
        start_sect=_ENDOFCHAIN,
        size=0,
        clsid=mathtype_clsid,
    )
    stream_entry = _dir_entry(
        "Equation Native",
        entry_type=2,
        color=1,
        child=_FREESECT,
        left=_FREESECT,
        right=_FREESECT,
        start_sect=2,
        size=len(stream_data),  # padded size so CFB skips mini stream
    )
    unused = bytes(128)
    dir_sector = root_entry + stream_entry + unused + unused
    assert len(dir_sector) == _SECTOR

    return bytes(header) + fat_bytes + dir_sector + padded
