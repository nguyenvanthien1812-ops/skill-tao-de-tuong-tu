#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Công Cụ Tự Động Bóc Tách Văn Bản & Hình Ảnh Từ File Giáo Án Word (DOCX), SGK (PDF) & Ảnh Chụp
Tác giả: Thầy Nguyễn Văn Thiện - THCS Ứng Hòe
- Bóc tách toàn bộ hình ảnh phân giải gốc từ file Word (.docx) hoặc Sách giáo khoa (.pdf)
- Tự động lọc bỏ ảnh rác/icon siêu nhỏ (< 3KB) và tự động chụp trang PDF nét cao (200 DPI)
  nếu file PDF SGK là bản scan hoặc hình vẽ vector (giúp luôn có hình ảnh chèn vào Slide!)
- Hỗ trợ nhận trực tiếp file ảnh chụp trang SGK (.png, .jpg, .jpeg, .webp)
"""

import os
import sys
import shutil
import zipfile
import argparse
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def extract_docx(docx_path, out_dir):
    """Bóc tách ảnh và văn bản từ file Word (.docx)"""
    docx_path = Path(docx_path).resolve()
    out_dir = Path(out_dir).resolve()
    images_dir = out_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    extracted_images = []
    text_content = []

    try:
        with zipfile.ZipFile(docx_path, "r") as z:
            media_files = sorted([f for f in z.namelist() if f.startswith("word/media/")])
            idx = 1
            for mf in media_files:
                ext = Path(mf).suffix.lower()
                raw_bytes = z.read(mf)
                # Bỏ qua các chấm/đường kẻ trang trí quá nhỏ (< 1.5 KB) hoặc file vector WMF/EMF không chèn trực tiếp được
                if len(raw_bytes) < 1500:
                    continue
                if ext in {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff", ".webp"}:
                    out_name = f"image_{idx:02d}{ext}"
                    out_path = images_dir / out_name
                    out_path.write_bytes(raw_bytes)
                    extracted_images.append(
                        {
                            "name": out_name,
                            "path": str(out_path),
                            "size_bytes": len(raw_bytes),
                        }
                    )
                    idx += 1
    except Exception as e:
        print(f"[!] Cảnh báo khi trích xuất ảnh từ DOCX: {e}")

    try:
        import docx
        doc = docx.Document(str(docx_path))
        for p in doc.paragraphs:
            t = p.text.strip()
            if t:
                text_content.append(t)
        for tbl in doc.tables:
            for row in tbl.rows:
                row_texts = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                if row_texts:
                    text_content.append(" | ".join(row_texts))
    except ImportError:
        try:
            import xml.etree.ElementTree as ET
            with zipfile.ZipFile(docx_path, "r") as z:
                xml_data = z.read("word/document.xml")
                root = ET.fromstring(xml_data)
                for elem in root.iter():
                    if elem.tag.endswith("}t") and elem.text:
                        text_content.append(elem.text.strip())
        except Exception as e:
            print(f"[!] Không thể đọc văn bản DOCX: {e}")

    txt_path = out_dir / "content.txt"
    txt_path.write_text("\n\n".join(text_content), encoding="utf-8")

    return {
        "source": str(docx_path),
        "total_paragraphs": len(text_content),
        "total_images": len(extracted_images),
        "images": extracted_images,
        "content_txt": str(txt_path),
    }


def extract_pdf(pdf_path, out_dir, max_snapshot_pages=15):
    """Bóc tách ảnh và văn bản từ file Sách giáo khoa PDF (kèm cơ chế chụp trang 200 DPI dự phòng)"""
    pdf_path = Path(pdf_path).resolve()
    out_dir = Path(out_dir).resolve()
    images_dir = out_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    extracted_images = []
    text_content = []

    try:
        import fitz  # PyMuPDF
        doc = fitz.open(str(pdf_path))
        img_idx = 1
        seen_xrefs = set()

        for page_idx in range(len(doc)):
            page = doc[page_idx]
            text = page.get_text()
            if text.strip():
                text_content.append(f"--- TRANG {page_idx + 1} ---\n" + text.strip())

            page_extracted_count = 0
            for img_info in page.get_images(full=True):
                xref = img_info[0]
                if xref in seen_xrefs:
                    continue
                seen_xrefs.add(xref)
                try:
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    w = base_image.get("width", 999)
                    h = base_image.get("height", 999)
                    # Lọc bỏ icon nhỏ hoặc đường viền trang SGK
                    if len(image_bytes) < 3500 or w < 70 or h < 70:
                        continue
                    image_ext = base_image["ext"]
                    out_name = f"page{page_idx + 1:02d}_img{img_idx:02d}.{image_ext}"
                    out_path = images_dir / out_name
                    out_path.write_bytes(image_bytes)
                    extracted_images.append(
                        {
                            "name": out_name,
                            "path": str(out_path),
                            "page": page_idx + 1,
                            "size_bytes": len(image_bytes),
                        }
                    )
                    img_idx += 1
                    page_extracted_count += 1
                except Exception:
                    pass

            # Nếu trang PDF là hình vẽ vector hoặc bản scan chưa tách ảnh lẻ -> chụp trang 200 DPI sắc nét
            if page_extracted_count == 0 and page_idx < max_snapshot_pages:
                try:
                    pix = page.get_pixmap(dpi=200)
                    out_name = f"page{page_idx + 1:02d}_full.png"
                    out_path = images_dir / out_name
                    pix.save(str(out_path))
                    extracted_images.append(
                        {
                            "name": out_name,
                            "path": str(out_path),
                            "page": page_idx + 1,
                            "size_bytes": out_path.stat().st_size,
                        }
                    )
                except Exception:
                    pass

        doc.close()
    except ImportError:
        try:
            import pypdf
            reader = pypdf.PdfReader(str(pdf_path))
            img_idx = 1
            for p_idx, page in enumerate(reader.pages):
                text = page.extract_text()
                if text:
                    text_content.append(f"--- TRANG {p_idx + 1} ---\n" + text.strip())
                for image_file_object in page.images:
                    if len(image_file_object.data) < 3500:
                        continue
                    out_name = f"page{p_idx + 1:02d}_img{img_idx:02d}_{image_file_object.name}"
                    out_path = images_dir / out_name
                    out_path.write_bytes(image_file_object.data)
                    extracted_images.append(
                        {
                            "name": out_name,
                            "path": str(out_path),
                            "page": p_idx + 1,
                            "size_bytes": len(image_file_object.data),
                        }
                    )
                    img_idx += 1
        except Exception as e:
            print(f"[!] Lỗi khi đọc PDF: {e}")

    txt_path = out_dir / "content.txt"
    txt_path.write_text("\n\n".join(text_content), encoding="utf-8")

    return {
        "source": str(pdf_path),
        "total_paragraphs": len(text_content),
        "total_images": len(extracted_images),
        "images": extracted_images,
        "content_txt": str(txt_path),
    }


def extract_single_image(img_path, out_dir):
    """Sao chép trực tiếp ảnh chụp trang SGK vào thư mục tài nguyên bài giảng"""
    img_path = Path(img_path).resolve()
    out_dir = Path(out_dir).resolve()
    images_dir = out_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    out_name = f"sgk_photo_01{img_path.suffix.lower()}"
    out_path = images_dir / out_name
    shutil.copy2(img_path, out_path)
    txt_path = out_dir / "content.txt"
    txt_path.write_text(f"[Ảnh chụp trang SGK]: {out_path}", encoding="utf-8")
    return {
        "source": str(img_path),
        "total_paragraphs": 1,
        "total_images": 1,
        "images": [{"name": out_name, "path": str(out_path), "size_bytes": out_path.stat().st_size}],
        "content_txt": str(txt_path),
    }


def main():
    parser = argparse.ArgumentParser(description="Công cụ bóc tách tài liệu Word, PDF & Ảnh chụp SGK")
    parser.add_argument("input_file", help="Đường dẫn đến file DOCX, PDF hoặc Ảnh chụp")
    parser.add_argument("-o", "--output", default="extracted_assets", help="Thư mục lưu kết quả")
    args = parser.parse_args()

    in_file = Path(args.input_file)
    if not in_file.exists():
        print(f"[X] Không tìm thấy file: {in_file}")
        sys.exit(1)

    suffix = in_file.suffix.lower()
    if suffix == ".docx":
        res = extract_docx(in_file, args.output)
    elif suffix == ".pdf":
        res = extract_pdf(in_file, args.output)
    elif suffix in {".png", ".jpg", ".jpeg", ".webp", ".bmp"}:
        res = extract_single_image(in_file, args.output)
    else:
        print(f"[X] Định dạng file chưa hỗ trợ trực tiếp: {suffix}. Hỗ trợ .docx, .pdf, .png, .jpg")
        sys.exit(1)

    print("=" * 65)
    print("      🎉 BÓC TÁCH NỘI DUNG TÀI LIỆU THÀNH CÔNG!")
    print("=" * 65)
    print(f"[*] File nguồn          : {res['source']}")
    print(f"[*] Số đoạn văn bản     : {res['total_paragraphs']}")
    print(f"[*] Số hình ảnh sẵn sàng: {res['total_images']}")
    print(f"[*] Thư mục lưu ảnh     : {Path(args.output).resolve() / 'images'}")
    print(f"[*] File text trích xuất: {res['content_txt']}")
    print("=" * 65)


if __name__ == "__main__":
    main()
