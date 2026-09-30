#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module Biên Dịch & Render Mã TikZ Thành Hình Ảnh 300 DPI Siêu Nét
Tích hợp trong Skill Tạo Đề Thi Chuẩn Bộ GD&ĐT.

Hỗ trợ:
1. Local Engine: Sử dụng pdflatex/xelatex/lualatex có sẵn trên máy (MikTeX, TeX Live)
   kết hợp PyMuPDF (fitz) xuất ảnh PNG 300-600 DPI, tốc độ ~1s, sắc nét tuyệt đối.
2. Cloud Fallback Engine: Tự động chuyển hướng sang API render trực tuyến (QuickLaTeX)
   nếu máy giáo viên chưa cài đặt TeX engine, đảm bảo không bao giờ bị gián đoạn.
3. Hỗ trợ đầy đủ các gói chuyên dụng cho giáo dục Việt Nam:
   - tikz, pgfplots (Đồ thị & hình học)
   - tkz-tab (Bảng biến thiên, bảng xét dấu chuẩn SGK & Đề thi Quốc Gia)
   - tkz-euclide (Hình học phẳng, góc, trung điểm, đường tròn)
   - circuitikz (Mạch điện môn Vật Lý)
   - chemfig (Công thức cấu tạo môn Hóa Học)
   - vietnam (Hiển thị tiếng Việt trong hình vẽ)
   - amsmath, amssymb, amsfonts (Ký hiệu toán học)
"""

import os
import sys
import shutil
import tempfile
import subprocess
import re
from pathlib import Path
from typing import Optional, Union

try:
    import fitz  # PyMuPDF
    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False

try:
    from PIL import Image, ImageChops
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


STANDARD_PREAMBLE_PACKAGES = [
    r"\usepackage[utf8]{vietnam}",
    r"\usepackage{amsmath,amssymb,amsfonts}",
    r"\usepackage{tikz}",
    r"\usepackage{pgfplots}",
    r"\pgfplotsset{compat=newest}",
    r"\usepackage{tkz-tab}",
    r"\usepackage{tkz-euclide}",
    r"\usepackage[siunitx]{circuitikz}",
    r"\usepackage{chemfig}",
    r"\usetikzlibrary{arrows,arrows.meta,calc,intersections,patterns,shapes,positioning,decorations.markings}",
]


def find_latex_compiler() -> Optional[str]:
    """Tìm trình biên dịch LaTeX khả dụng trên hệ thống (ưu tiên pdflatex, xelatex)."""
    compilers = ["pdflatex", "xelatex", "lualatex", "latex"]
    for c in compilers:
        found = shutil.which(c)
        if found:
            return c
    # Quét thêm thư mục phổ biến trên Windows
    win_paths = [
        r"C:\Users\admin\scoop\apps\miktex\current\miktex\bin\x64\pdflatex.exe",
        r"C:\Program Files\MiKTeX\miktex\bin\x64\pdflatex.exe",
        r"C:\Program Files (x86)\MiKTeX\miktex\bin\pdflatex.exe",
        r"C:\texlive\2026\bin\windows\pdflatex.exe",
        r"C:\texlive\2025\bin\windows\pdflatex.exe",
        r"C:\texlive\2024\bin\windows\pdflatex.exe",
    ]
    for p in win_paths:
        if os.path.isfile(p):
            return p
    return None


def is_latex_available() -> bool:
    """Kiểm tra máy tính có sẵn LaTeX compiler hay không."""
    return find_latex_compiler() is not None


def trim_whitespace(img_path: str, padding: int = 10):
    """Cắt bớt viền trắng dư thừa xung quanh ảnh PNG bằng PIL."""
    if not HAS_PIL or not os.path.exists(img_path):
        return
    try:
        im = Image.open(img_path)
        im_rgba = im.convert("RGBA")
        bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
        diff = ImageChops.difference(im_rgba, bg)
        bbox = diff.getbbox()
        if bbox:
            w, h = im.size
            crop_box = (
                max(0, bbox[0] - padding),
                max(0, bbox[1] - padding),
                min(w, bbox[2] + padding),
                min(h, bbox[3] + padding)
            )
            cropped = im.crop(crop_box)
            cropped.save(img_path)
    except Exception:
        pass


def wrap_tikz_document(tikz_code: str, custom_preamble: str = "", mode: str = "standalone") -> str:
    """
    Bọc mã TikZ snippet thành một tài liệu LaTeX hoàn chỉnh.
    - mode='standalone' (mặc định): Bo sát viền hình (tight bounding box), chuẩn vector nhúng vào tài liệu.
    - mode='a4': Căn giữa trên trang giấy A4 chuẩn, thích hợp xem và in ấn trực tiếp.
    Nếu mã đã là tài liệu hoàn chỉnh (có \\documentclass), trả về nguyên bản.
    """
    code_stripped = tikz_code.strip()
    if r"\documentclass" in code_stripped:
        return code_stripped

    # Tự động chuẩn hóa tkz-tab nếu thiếu khoảng trắng quanh dấu gạch chéo
    if r"\tkzTabInit" in code_stripped:
        code_stripped = re.sub(r'(\$\S+\$)\s*/\s*(\d+)', r'\1 / \2 ', code_stripped)

    # Nếu là chemfig độc lập, bọc trong node tikz
    if code_stripped.startswith(r"\chemfig") and r"\begin{tikzpicture}" not in code_stripped:
        tikz_content = f"\\begin{{tikzpicture}}\n  \\node {{{code_stripped}}};\n\\end{{tikzpicture}}"
    elif r"\begin{tikzpicture}" not in code_stripped:
        tikz_content = f"\\begin{{tikzpicture}}\n{code_stripped}\n\\end{{tikzpicture}}"
    else:
        tikz_content = code_stripped

    preamble_lines = "\n".join(STANDARD_PREAMBLE_PACKAGES)
    if custom_preamble:
        preamble_lines += "\n" + custom_preamble

    if mode == "a4":
        doc_class = r"\documentclass[12pt,a4paper]{article}"
        preamble_lines += "\n" + r"\usepackage[margin=2cm]{geometry}" + "\n" + r"\pagestyle{empty}"
        body = f"\\vspace*{{\\fill}}\n\\begin{{center}}\n{tikz_content}\n\\end{{center}}\n\\vspace*{{\\fill}}"
    else:
        doc_class = r"\documentclass[tikz,border=4pt]{standalone}"
        body = tikz_content

    full_tex = f"""{doc_class}
{preamble_lines}
\\begin{{document}}
{body}
\\end{{document}}
"""
    return full_tex


def render_tikz_local(tex_source: str, output_path: str, dpi: int = 300, timeout: int = 60, passes: int = 1) -> bool:
    """Biên dịch mã TeX thành PDF, SVG hoặc PNG độ phân giải cao bằng pdflatex + PyMuPDF.
    Hỗ trợ biên dịch tài liệu, đề thi nhiều trang với 2 lần chạy (two-pass) để giải quyết label/ref/số trang."""
    compiler = find_latex_compiler()
    if not compiler:
        return False

    output_dir = os.path.dirname(os.path.abspath(output_path))
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmpdir:
        tex_file = os.path.join(tmpdir, "render_fig.tex")
        with open(tex_file, "w", encoding="utf-8") as f:
            f.write(tex_source)

        try:
            # Biên dịch TeX sang PDF vector
            cmd = [compiler, "-interaction=nonstopmode", "-halt-on-error", "render_fig.tex"]
            res = subprocess.run(
                cmd,
                cwd=tmpdir,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout
            )
            pdf_file = os.path.join(tmpdir, "render_fig.pdf")

            # Nếu có tham chiếu chéo (cross-references, \pageref, \label, \tableofcontents) -> chạy thêm pass 2
            needs_second_pass = passes > 1 or any(k in tex_source for k in [r"\label", r"\pageref", r"\ref", r"\tableofcontents", "LastPage"])
            if needs_second_pass and os.path.isfile(pdf_file) and os.path.getsize(pdf_file) > 0:
                subprocess.run(
                    cmd,
                    cwd=tmpdir,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    timeout=timeout
                )

            if not os.path.isfile(pdf_file) or os.path.getsize(pdf_file) == 0:
                return False

            ext = os.path.splitext(output_path)[1].lower()

            # 1. Xuất file PDF vector nguyên bản (đề thi, tài liệu hoặc hình standalone)
            if ext == ".pdf":
                shutil.copy2(pdf_file, output_path)
                return True

            # 2. Xuất file SVG vector
            if ext == ".svg":
                if HAS_PYMUPDF:
                    doc = fitz.open(pdf_file)
                    svg_content = doc[0].get_svg_image()
                    doc.close()
                    with open(output_path, "w", encoding="utf-8") as f_svg:
                        f_svg.write(svg_content)
                    return True
                return False

            # 3. Xuất file PNG (mặc định)
            if HAS_PYMUPDF:
                doc = fitz.open(pdf_file)
                if len(doc) > 0:
                    page = doc[0]
                    zoom = dpi / 72.0
                    mat = fitz.Matrix(zoom, zoom)
                    pix = page.get_pixmap(matrix=mat, alpha=False)
                    pix.save(output_path)
                    doc.close()
                    trim_whitespace(output_path, padding=8)
                    return True
                doc.close()
        except Exception:
            return False

    return False


def render_tikz_cloud(tikz_code: str, output_path: str, timeout: int = 20) -> bool:
    """
    Fallback dự phòng: Render TikZ qua Cloud API (QuickLaTeX) khi máy chưa cài đặt LaTeX.
    Hỗ trợ giáo viên sử dụng ngay mà không cần cấu hình phức tạp.
    """
    if not HAS_REQUESTS:
        return False

    output_dir = os.path.dirname(os.path.abspath(output_path))
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    # Đảm bảo có thẻ tikzpicture
    code_stripped = tikz_code.strip()
    if r"\begin{tikzpicture}" not in code_stripped:
        code_stripped = f"\\begin{{tikzpicture}}\n{code_stripped}\n\\end{{tikzpicture}}"

    preamble = (
        r"\usepackage{amsmath,amssymb}" "\n"
        r"\usepackage{tikz}" "\n"
        r"\usepackage{pgfplots}" "\n"
        r"\pgfplotsset{compat=newest}" "\n"
        r"\usepackage{tkz-tab}" "\n"
        r"\usepackage{tkz-euclide}" "\n"
        r"\usepackage{circuitikz}" "\n"
        r"\usetikzlibrary{arrows,arrows.meta,calc}"
    )

    url = "https://quicklatex.com/latex3.f"
    payload = {
        "formula": code_stripped,
        "fsize": "20px",
        "fcolor": "000000",
        "mode": "0",
        "out": "1",
        "remhost": "quicklatex.com",
        "preamble": preamble
    }

    try:
        resp = requests.post(url, data=payload, timeout=timeout)
        if resp.status_code == 200:
            lines = resp.text.strip().split("\n")
            if lines and lines[0].strip() == "0":
                parts = lines[1].strip().split()
                img_url = parts[0]
                img_data = requests.get(img_url, timeout=timeout).content

                ext = os.path.splitext(output_path)[1].lower()
                if ext == ".pdf" and HAS_PYMUPDF:
                    img_doc = fitz.open(stream=img_data, filetype="png")
                    pdf_bytes = img_doc.convert_to_pdf()
                    img_doc.close()
                    with open(output_path, "wb") as f_pdf:
                        f_pdf.write(pdf_bytes)
                    return True

                with open(output_path, "wb") as f_out:
                    f_out.write(img_data)
                trim_whitespace(output_path, padding=8)
                return True
    except Exception:
        pass

    return False


def render_tikz(
    tikz_code: str,
    output_path: str,
    dpi: int = 300,
    custom_preamble: str = "",
    mode: str = "standalone",
    engine: str = "auto",
    timeout: int = 60
) -> bool:
    """
    Hàm tổng quát kết xuất mã TikZ thành tệp PDF (vector sắc nét), PNG (300 DPI) hoặc SVG.

    Tham số:
    - tikz_code: Chuỗi mã TikZ (snippet hoặc full LaTeX document).
    - output_path: Đường dẫn tệp ảnh xuất ra (.pdf, .png, .svg).
    - dpi: Độ phân giải in ấn (khi xuất PNG, mặc định 300 DPI).
    - custom_preamble: Khai báo thêm package LaTeX nếu cần.
    - mode: 'standalone' (viền khít vector chuẩn) hoặc 'a4' (trang giấy A4).
    - engine: 'auto' (ưu tiên local, fallback sang cloud), 'local' hoặc 'cloud'.
    - timeout: Thời gian chờ tối đa (giây).

    Trả về: True nếu xuất tệp thành công, False nếu thất bại.
    """
    # ─── LỚP A: Kiểm tra bản quyền bắt buộc ────────────────────────────────
    try:
        _scripts_dir = os.path.dirname(os.path.abspath(__file__))
        if _scripts_dir not in sys.path:
            sys.path.insert(0, _scripts_dir)
        from license_manager import check_current_license
        ok, payload, err = check_current_license()
        if not ok:
            raise PermissionError(
                "\n╔══════════════════════════════════════════════════════════╗\n"
                "║     ⛔  SKILL CHƯA ĐƯỢC KÍCH HOẠT BẢN QUYỀN!           ║\n"
                "╠══════════════════════════════════════════════════════════╣\n"
                f"║  Lý do: {err[:50]:<50} ║\n"
                "╠══════════════════════════════════════════════════════════╣\n"
                "║  Chạy KICH_HOAT_BAN_QUYEN.bat để kích hoạt license.    ║\n"
                "╚══════════════════════════════════════════════════════════╝"
            )
    except ImportError:
        pass  # Môi trường dev của tác giả, không chặn
    # ────────────────────────────────────────────────────────────────────────
    full_tex = wrap_tikz_document(tikz_code, custom_preamble, mode=mode)


    if engine in ("auto", "local"):
        if is_latex_available():
            ok = render_tikz_local(full_tex, output_path, dpi=dpi, timeout=timeout)
            if ok and os.path.isfile(output_path) and os.path.getsize(output_path) > 0:
                return True
        if engine == "local":
            return False

    # Nếu local không khả dụng hoặc lỗi, thử Cloud Engine Fallback
    if engine in ("auto", "cloud"):
        ok = render_tikz_cloud(tikz_code, output_path, timeout=timeout)
        if ok and os.path.isfile(output_path) and os.path.getsize(output_path) > 0:
            return True

    return False


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Biên dịch mã TikZ sang file PDF vector, SVG hoặc ảnh PNG 300 DPI")
    parser.add_argument("-i", "--input", help="Đường dẫn tệp mã .tex hoặc .tikz")
    parser.add_argument("-c", "--code", help="Chuỗi mã TikZ trực tiếp")
    parser.add_argument("-o", "--output", required=True, help="Đường dẫn tệp đầu ra (.pdf, .svg, .png)")
    parser.add_argument("--mode", choices=["standalone", "a4"], default="standalone", help="Chế độ trang: standalone (viền khít vector) hoặc a4 (trang A4)")
    parser.add_argument("--dpi", type=int, default=300, help="Độ phân giải DPI khi xuất PNG (mặc định: 300)")
    parser.add_argument("--engine", choices=["auto", "local", "cloud"], default="auto", help="Engine render")

    args = parser.parse_args()

    tikz_content = ""
    if args.input:
        with open(args.input, "r", encoding="utf-8") as f:
            tikz_content = f.read()
    elif args.code:
        tikz_content = args.code
    else:
        print("[LỖI] Vui lòng cung cấp mã qua --input hoặc --code!")
        sys.exit(1)

    print(f"[*] Đang biên dịch mã TikZ sang: {args.output} (Mode={args.mode}, DPI={args.dpi}, Engine={args.engine})...")
    success = render_tikz(tikz_content, args.output, dpi=args.dpi, mode=args.mode, engine=args.engine)
    if success:
        size_kb = os.path.getsize(args.output) / 1024
        print(f"[THÀNH CÔNG] Đã tạo tệp: {args.output} ({size_kb:.1f} KB)")
        sys.exit(0)
    else:
        print("[THẤT BẠI] Không thể biên dịch mã TikZ.")
        sys.exit(1)
