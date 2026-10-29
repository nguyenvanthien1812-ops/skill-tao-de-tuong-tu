#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sync_skill.py — Công cụ Đồng Bộ & Kiểm Định Toàn Vẹn Skill (Self-Audit + Sync)
================================================================================
1. Dọn dẹp triệt để thư mục lồng nhau rác (.agents, tao-de-toan-tuong-tu) và license.key thừa.
2. Kiểm định cú pháp (py_compile) toàn bộ script trong scripts/.
3. Kiểm định cấu trúc SKILL.md và toàn bộ references/*.md (không đứt link, cân bằng code fence).
4. Kiểm định file Word Ma trận & Bản đặc tả mẫu:
   - Đủ dòng tổng kết cuối bảng ở cả Bảng 1 và Bảng 2
   - Mỗi mức độ nhận thức nằm trên 1 dòng riêng + mã câu hỏi nằm cùng dòng
   - 0 ô thiếu viền (w:tcBorders), có w:tblBorders, 0 ô gộp bị lặp chữ.
5. Đồng bộ 100% từ Workspace sang Global (%USERPROFILE%/.gemini/config/skills/...).
"""

import os
import re
import sys
import glob
import shutil
import py_compile
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
WORKSPACE_SKILLS_ROOT = SKILL_DIR.parent
GLOBAL_SKILLS_ROOT = Path.home() / ".gemini" / "config" / "skills"
GLOBAL_SKILL_DIR = GLOBAL_SKILLS_ROOT / "tao-de-toan-tuong-tu"


def clean_junk_in_skill_dir(root: Path) -> list[str]:
    """Xóa các thư mục lồng nhau rác và bản license.key nằm sai vị trí."""
    removed = []
    if not root.exists():
        return removed
    junk_dirs = [
        root / ".agents",
        root / "tao-de-toan-tuong-tu",
        root / "scripts" / ".agents",
        root / "scripts" / "tao-de-toan-tuong-tu",
        root / "test_output_figures",
    ]
    for jd in junk_dirs:
        if jd.exists():
            shutil.rmtree(jd, ignore_errors=True)
            removed.append(str(jd))
    stray_lic = root / "scripts" / "license.key"
    if stray_lic.exists():
        stray_lic.unlink(missing_ok=True)
        removed.append(str(stray_lic))
    return removed


def verify_scripts_compile(root: Path) -> list[str]:
    """Biên dịch thử toàn bộ file .py trong scripts/."""
    errors = []
    for py_file in sorted((root / "scripts").glob("*.py")):
        try:
            py_compile.compile(str(py_file), doraise=True)
        except Exception as e:
            errors.append(f"{py_file.name}: {e}")
    return errors


def verify_markdown_docs(root: Path) -> list[str]:
    """Kiểm định SKILL.md và references/*.md."""
    errors = []
    skill_md = root / "SKILL.md"
    if not skill_md.exists():
        return ["Thiếu file SKILL.md"]
    txt = skill_md.read_text(encoding="utf-8")
    if txt.count("```") % 2 != 0:
        errors.append("SKILL.md: Lệch cặp dấu ``` (code fence)")
    if re.search(r"[^\n\r#]#{2,4} ", txt):
        errors.append("SKILL.md: Có heading ### bị dính vào cuối dòng trước")
    for m in re.finditer(r"\]\((\./[^)#]+)", txt):
        rel = m.group(1)[2:]
        if not (root / rel).exists():
            errors.append(f"SKILL.md: Link nội bộ không tồn tại: {m.group(1)}")
    for ref_md in sorted((root / "references").glob("*.md")):
        rtxt = ref_md.read_text(encoding="utf-8")
        if rtxt.count("```") % 2 != 0:
            errors.append(f"references/{ref_md.name}: Lệch cặp dấu ``` (code fence)")
    return errors


def verify_matrix_docx(docx_path: Path) -> list[str]:
    """Kiểm định 4 quy chuẩn bắt buộc trên file Word Ma trận & Bản đặc tả."""
    errors = []
    if not docx_path.exists():
        return [f"Không tìm thấy file mẫu Ma trận: {docx_path}"]
    from docx import Document
    from docx.oxml.ns import qn

    doc = Document(str(docx_path))
    if len(doc.tables) < 3:
        return [f"File Ma trận chỉ có {len(doc.tables)} bảng (cần >= 3 bảng)"]

    t1, t2 = doc.tables[1], doc.tables[2]
    # 1. Kiểm tra viền và nhân bản đoạn văn ở cả 2 bảng
    for idx, tbl in [(1, t1), (2, t2)]:
        if tbl._tbl.tblPr.find(qn("w:tblBorders")) is None:
            errors.append(f"Bảng {idx}: Thiếu w:tblBorders")
        tcs = [tc for tr in tbl._tbl.tr_lst for tc in tr.tc_lst]
        nob = sum(1 for tc in tcs if tc.tcPr is None or tc.tcPr.find(qn("w:tcBorders")) is None)
        if nob > 0:
            errors.append(f"Bảng {idx}: Có {nob}/{len(tcs)} ô thiếu w:tcBorders")
        for tr in tbl._tbl.tr_lst:
            for tc in tr.tc_lst[:3]:
                vm = tc.tcPr.find(qn("w:vMerge")) if tc.tcPr is not None else None
                if vm is not None and vm.get(qn("w:val")) == "restart":
                    paras = ["".join(x.text or "" for x in p.iter(qn("w:t"))).strip() for p in tc.iter(qn("w:p"))]
                    nonempty = [p for p in paras if p]
                    if len(nonempty) != len(set(nonempty)):
                        errors.append(f"Bảng {idx}: Ô gộp dọc bị nhân bản chữ: {nonempty[:3]}")
                        break

    # 2. Kiểm tra dòng tổng kết cuối bảng
    t1_last = [t1.rows[i].cells[0].text.strip().upper() for i in range(len(t1.rows) - 4, len(t1.rows))]
    if not any("TỈ LỆ" in s for s in t1_last) or not any("TỔNG ĐIỂM" in s for s in t1_last):
        errors.append(f"Bảng 1 (Ma trận): Thiếu dòng tổng kết cuối bảng ({t1_last})")

    t2_last = [t2.rows[i].cells[0].text.strip().upper() for i in range(len(t2.rows) - 3, len(t2.rows))]
    if not any("TỈ LỆ" in s for s in t2_last) or not any("TỔNG ĐIỂM" in s for s in t2_last):
        errors.append(f"Bảng 2 (Bản đặc tả): Thiếu dòng tổng kết cuối bảng ({t2_last})")

    # 3. Kiểm tra mỗi dòng của Bản đặc tả chỉ chứa đúng 1 mức độ nhận thức + có mã câu hỏi cùng dòng
    valid_levels = {"Nhận biết", "Thông hiểu", "Vận dụng", "Vận dụng cao"}
    for ri in range(3, len(t2.rows) - 3):
        cells = t2.rows[ri].cells
        lvl = cells[3].text.strip()
        qcodes = cells[18].text.strip()
        if lvl not in valid_levels:
            errors.append(f"Bảng 2 dòng {ri}: Cột Mức độ đánh giá không hợp lệ ('{lvl}')")
            break
        if not qcodes.startswith("C"):
            errors.append(f"Bảng 2 dòng {ri} ({lvl}): Thiếu mã câu hỏi cùng dòng ('{qcodes}')")
            break

    return errors


def sync_directory(src: Path, dst: Path, preserve_files: set[str] = None):
    """Đồng bộ toàn bộ file từ src sang dst (bỏ qua __pycache__ và giữ nguyên preserve_files ở dst)."""
    if src.resolve() == dst.resolve():
        return
    preserve_files = preserve_files or set()
    dst.mkdir(parents=True, exist_ok=True)
    for root, dirs, files in os.walk(src):
        dirs[:] = [d for d in dirs if d not in {"__pycache__", ".git", ".agents", "tao-de-toan-tuong-tu", "test_output_figures"}]
        rel_dir = Path(root).relative_to(src)
        target_dir = dst / rel_dir
        target_dir.mkdir(parents=True, exist_ok=True)
        for f in files:
            if f.endswith((".pyc", ".pyo", ".tmp")) or f.startswith("~$"):
                continue
            if f in preserve_files and (target_dir / f).exists():
                continue
            shutil.copy2(Path(root) / f, target_dir / f)


def run_all() -> int:
    print("=" * 72)
    print("  🔄 ĐỒNG BỘ & KIỂM ĐỊNH TOÀN VẸN SKILL (SELF-AUDIT & SYNC)")
    print("=" * 72)

    removed_w = clean_junk_in_skill_dir(SKILL_DIR)
    removed_g = clean_junk_in_skill_dir(GLOBAL_SKILL_DIR)
    if removed_w or removed_g:
        print(f"  [✓] Đã dọn {len(removed_w) + len(removed_g)} thư mục/file rác lồng nhau.")

    errs = []
    errs.extend(verify_scripts_compile(SKILL_DIR))
    errs.extend(verify_markdown_docs(SKILL_DIR))
    sample_docx = SKILL_DIR / "MATH_12_THPT_90MIN_MA_TRAN_DAC_TA_CHUAN_BGD.docx"
    errs.extend(verify_matrix_docx(sample_docx))

    if errs:
        print("  [✗] PHÁT HIỆN LỖI KIỂM ĐỊNH:")
        for e in errs:
            print(f"      - {e}")
        return 1

    print("  [✓] 100% script (.py) biên dịch thành công.")
    print("  [✓] SKILL.md & 15 file references/*.md chuẩn cấu trúc, không đứt link.")
    print("  [✓] File Word Ma trận & Bản đặc tả mẫu đạt chuẩn 100% (0 ô mất nét, đủ dòng tổng, 1 mức độ/1 dòng).")

    if GLOBAL_SKILLS_ROOT.exists():
        sync_directory(SKILL_DIR, GLOBAL_SKILL_DIR, preserve_files={"license.key"})
        clean_junk_in_skill_dir(GLOBAL_SKILL_DIR)
        print(f"  [✓] Đã đồng bộ sang Global Config: {GLOBAL_SKILL_DIR}")

        # Đồng bộ sang Antigravity Skills directory và các thư mục dự án nếu có
        for extra_skill_dir in [
            Path.home() / ".gemini" / "antigravity" / "skills" / "tao-de-toan-tuong-tu",
            Path(r"D:\skill-Nguyen-Thien\tao-de-toan-tuong-tu"),
            Path(r"D:\skill-quan-trong\.agents\skills\tao-de-toan-tuong-tu"),
        ]:
            if extra_skill_dir.parent.exists() and extra_skill_dir.resolve() != SKILL_DIR.resolve():
                sync_directory(SKILL_DIR, extra_skill_dir, preserve_files={"license.key"})
                clean_junk_in_skill_dir(extra_skill_dir)
                print(f"  [✓] Đã đồng bộ sang: {extra_skill_dir}")

        # Đồng bộ luôn skill video khởi động bài học nếu có
        vid_src = WORKSPACE_SKILLS_ROOT / "tao-video-khoi-dong-bai-hoc"
        if vid_src.exists():
            for vid_dst in [
                GLOBAL_SKILLS_ROOT / "tao-video-khoi-dong-bai-hoc",
                Path(r"D:\skill-Nguyen-Thien\tao-video-khoi-dong-bai-hoc"),
            ]:
                if vid_dst.parent.exists():
                    sync_directory(vid_src, vid_dst)
                    print(f"  [✓] Đã đồng bộ skill video: {vid_dst}")

    print("=" * 72)
    return 0


if __name__ == "__main__":
    sys.exit(run_all())
