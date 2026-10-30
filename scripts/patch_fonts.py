#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Công cụ đồng bộ 100% Font chữ trong file PowerPoint (.pptx) về chuẩn Times New Roman
(Bao gồm cả Theme XML +mn-lt / +mj-lt, Slide Master, Slide Layout, Slides và Notes)
"""

import os
import re
import shutil
import zipfile
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def patch_pptx(pptx_path, quiet=False):
    pptx_path = os.path.abspath(pptx_path)
    if not quiet:
        print(f"[*] Đang chuẩn hóa font Times New Roman cho: {pptx_path}...")
    temp_dir = pptx_path + "_temp_unpack"
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)

    with zipfile.ZipFile(pptx_path, "r") as zip_ref:
        zip_ref.extractall(temp_dir)

    theme_dir = os.path.join(temp_dir, "ppt", "theme")
    if os.path.exists(theme_dir):
        for f in os.listdir(theme_dir):
            if f.endswith(".xml"):
                fpath = os.path.join(theme_dir, f)
                with open(fpath, "r", encoding="utf-8") as tf:
                    content = tf.read()
                content = re.sub(r'<a:latin typeface="[^"]*"', '<a:latin typeface="Times New Roman"', content)
                content = re.sub(r'<a:ea typeface="[^"]*"', '<a:ea typeface="Times New Roman"', content)
                content = re.sub(r'<a:cs typeface="[^"]*"', '<a:cs typeface="Times New Roman"', content)
                with open(fpath, "w", encoding="utf-8") as tf:
                    tf.write(content)

    slide_dirs = [
        os.path.join(temp_dir, "ppt", "slides"),
        os.path.join(temp_dir, "ppt", "slideLayouts"),
        os.path.join(temp_dir, "ppt", "slideMasters"),
        os.path.join(temp_dir, "ppt", "notesSlides"),
    ]

    count_patched = 0
    for sdir in slide_dirs:
        if not os.path.exists(sdir):
            continue
        for f in os.listdir(sdir):
            if f.endswith(".xml"):
                fpath = os.path.join(sdir, f)
                with open(fpath, "r", encoding="utf-8") as sf:
                    content = sf.read()

                orig = content
                content = content.replace('typeface="+mn-lt"', 'typeface="Times New Roman"')
                content = content.replace('typeface="+mj-lt"', 'typeface="Times New Roman"')
                content = content.replace('typeface="+mn-ea"', 'typeface="Times New Roman"')
                content = content.replace('typeface="+mj-ea"', 'typeface="Times New Roman"')

                if content != orig:
                    with open(fpath, "w", encoding="utf-8") as sf:
                        sf.write(content)
                    count_patched += 1

    temp_zip = pptx_path + ".new"
    with zipfile.ZipFile(temp_zip, "w", zipfile.ZIP_DEFLATED) as zip_out:
        for root, _, files in os.walk(temp_dir):
            for f in files:
                full_path = os.path.join(root, f)
                rel_path = os.path.relpath(full_path, temp_dir)
                zip_out.write(full_path, rel_path)

    shutil.rmtree(temp_dir, ignore_errors=True)
    os.replace(temp_zip, pptx_path)
    if not quiet:
        print(f"[OK] Đã đồng bộ font Times New Roman cho {count_patched} tệp XML trong PPTX.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Cách dùng: python patch_fonts.py <duong_dan_file.pptx>")
        sys.exit(1)
    patch_pptx(sys.argv[1])
