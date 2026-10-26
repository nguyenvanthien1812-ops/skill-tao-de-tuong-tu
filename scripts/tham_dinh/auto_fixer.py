# -*- coding: utf-8 -*-
"""
auto_fixer.py
─────────────
Tự động sửa các lỗi fixable trong file Word đề thi và HDC
dựa trên kế hoạch sửa đã được Giáo viên phê duyệt.

Luồng:
  1. Nhận list FindingItem (fixable=True) đã được GV duyệt
  2. Áp dụng fix lên file Word (exam_path, rubric_path)
  3. Lưu file mới ra output_dir
  4. Trả về dict kết quả
"""
from __future__ import annotations
import os
import re
import shutil
from typing import Optional

from tham_dinh.exam_extractor import ExamData
from tham_dinh.exam_validator import FindingItem


# ──────────────────────────────────────────────────────────────────────────────
# INDIVIDUAL FIXERS
# ──────────────────────────────────────────────────────────────────────────────

def _fix_add_end_marker(exam_path: str, exam_out: str) -> str:
    """Thêm dòng HẾT cuối đề thi nếu chưa có."""
    try:
        import docx
        doc = docx.Document(exam_path)
        full_text = " ".join(p.text for p in doc.paragraphs).lower()
        if 'hết' not in full_text:
            from docx.shared import Pt
            from docx.enum.text import WD_ALIGN_PARAGRAPH
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(12)
            r = p.add_run("--------------------- HẾT ----------------------\n"
                          "(Cán bộ coi thi không giải thích gì thêm)")
            r.italic = True
            r.font.name = 'Times New Roman'
            r.font.size = Pt(12)
            doc.save(exam_out)
            return f"✅ Đã thêm dòng HẾT vào cuối Đề thi → {os.path.basename(exam_out)}"
        else:
            shutil.copy2(exam_path, exam_out)
            return "ℹ️ Đề thi đã có dòng HẾT, không cần sửa."
    except Exception as e:
        return f"❌ Lỗi khi thêm dòng HẾT: {e}"


def _fix_add_rubric_note(rubric_path: str, rubric_out: str) -> str:
    """Thêm mục Lưu ý khi chấm bài vào cuối HDC nếu chưa có."""
    try:
        import docx
        from docx.shared import Pt, RGBColor
        doc = docx.Document(rubric_path)
        full_text = " ".join(p.text for p in doc.paragraphs).lower()
        if 'lưu ý khi chấm' not in full_text and 'lưu ý:' not in full_text:
            p_h = doc.add_paragraph()
            p_h.paragraph_format.space_before = Pt(10)
            r_h = p_h.add_run("Lưu ý khi chấm bài:")
            r_h.bold = True
            r_h.font.name = 'Times New Roman'
            r_h.font.size = Pt(13)

            notes = [
                "1. Thí sinh làm theo cách khác đúng vẫn cho điểm tối đa theo từng phần tương ứng.",
                "2. Điểm toàn bài là tổng điểm các câu không làm tròn, thang điểm 10,0 điểm.",
                "3. Ở bài hình học, nếu học sinh không vẽ hình hoặc vẽ sai hình cơ bản thì không chấm điểm phần đó."
            ]
            for note in notes:
                pn = doc.add_paragraph()
                pn.paragraph_format.left_indent = docx.shared.Cm(0.4)
                pn.paragraph_format.space_before = Pt(1)
                pn.paragraph_format.space_after  = Pt(2)
                rn = pn.add_run(note)
                rn.font.name = 'Times New Roman'
                rn.font.size = Pt(12)

            doc.save(rubric_out)
            return f"✅ Đã thêm mục 'Lưu ý khi chấm bài' vào cuối HDC → {os.path.basename(rubric_out)}"
        else:
            shutil.copy2(rubric_path, rubric_out)
            return "ℹ️ HDC đã có mục Lưu ý, không cần sửa."
    except Exception as e:
        return f"❌ Lỗi khi thêm Lưu ý: {e}"


def _fix_rubric_exam_code(rubric_path: str, rubric_out: str, correct_code: str) -> str:
    """Sửa Mã đề trong HDC thành đúng mã đề của Đề thi."""
    try:
        import docx
        doc = docx.Document(rubric_path)

        # Tìm và sửa trong các đoạn văn
        changed = 0
        code_pattern = re.compile(r'[Mm]ã\s*đề\s*[:\s]*\d+')
        for para in doc.paragraphs:
            if code_pattern.search(para.text):
                for run in para.runs:
                    if re.search(r'\d+', run.text) and 'đề' in para.text.lower():
                        new_text = code_pattern.sub(f'Mã đề: {correct_code}', run.text)
                        if new_text != run.text:
                            run.text = new_text
                            changed += 1

        # Tìm trong bảng
        for tbl in doc.tables:
            for row in tbl.rows:
                for cell in row.cells:
                    for para in cell.paragraphs:
                        if code_pattern.search(para.text):
                            for run in para.runs:
                                new_text = code_pattern.sub(f'Mã đề: {correct_code}', run.text)
                                if new_text != run.text:
                                    run.text = new_text
                                    changed += 1

        doc.save(rubric_out)
        return (f"✅ Đã sửa Mã đề trong HDC thành '{correct_code}' "
                f"({changed} vị trí) → {os.path.basename(rubric_out)}")
    except Exception as e:
        return f"❌ Lỗi khi sửa Mã đề HDC: {e}"


# ──────────────────────────────────────────────────────────────────────────────
# MAIN AUTO-FIX RUNNER
# ──────────────────────────────────────────────────────────────────────────────

def run_auto_fix(
    approved_items: list,       # [FindingItem] đã được GV phê duyệt
    data: ExamData,
    exam_path: str,
    rubric_path: str,
    output_dir: str
) -> dict:
    """
    Thực thi auto-fix cho các FindingItem được phê duyệt.
    Lưu file đã sửa vào output_dir với hậu tố _FIXED.
    """
    os.makedirs(output_dir, exist_ok=True)
    results = []

    exam_base   = os.path.splitext(os.path.basename(exam_path))[0]
    rubric_base = os.path.splitext(os.path.basename(rubric_path))[0]
    exam_out    = os.path.join(output_dir, exam_base   + "_FIXED.docx")
    rubric_out  = os.path.join(output_dir, rubric_base + "_FIXED.docx")

    # Copy file gốc làm nền để sửa
    shutil.copy2(exam_path,   exam_out)
    shutil.copy2(rubric_path, rubric_out)

    for item in approved_items:
        code = item.code
        print(f"[AutoFix] Áp dụng fix {code}: {item.fix_action}")

        if code == "C04":   # Thêm dòng HẾT
            res = _fix_add_end_marker(exam_out, exam_out)
            results.append(f"**[{code}]** {res}")

        elif code == "D01":   # Sửa/bổ sung Mã đề trong HDC
            res = _fix_rubric_exam_code(rubric_out, rubric_out, data.exam_code or "")
            results.append(f"**[{code}]** {res}")

        elif code == "D04":   # Thêm Lưu ý chấm bài
            res = _fix_add_rubric_note(rubric_out, rubric_out)
            results.append(f"**[{code}]** {res}")

        else:
            results.append(f"**[{code}]** ℹ️ Lỗi này cần sửa thủ công — em đã ghi rõ hướng dẫn trong báo cáo.")

    return {
        "exam_fixed":   exam_out,
        "rubric_fixed": rubric_out,
        "results":      results,
        "summary":      f"Đã xử lý {len(approved_items)} hạng mục auto-fix. "
                        f"File đã sửa lưu tại: {output_dir}"
    }


def parse_approved_items(
    user_input: str,
    fixable_items: list
) -> list:
    """
    Phân tích câu trả lời của GV để xác định item nào được phê duyệt.
    GV có thể: OK / Đồng ý (tất cả), Bỏ qua 2,3 (bỏ qua số 2 và 3), Fix 1,4 (chỉ fix 1 và 4)
    """
    inp = user_input.strip().lower()

    # Đồng ý tất cả
    if any(kw in inp for kw in ['ok', 'đồng ý', 'sửa hết', 'sửa tất cả', 'yes', 'được']):
        skip_nums = set()
        # Kiểm tra có "bỏ qua" không
        m_skip = re.search(r'bỏ\s*qua\s*([\d,\s]+)', inp)
        if m_skip:
            skip_nums = set(int(n.strip()) for n in re.findall(r'\d+', m_skip.group(1)))
        return [item for i, item in enumerate(fixable_items, 1) if i not in skip_nums]

    # Chỉ fix một số item
    m_fix = re.search(r'fix\s*([\d,\s]+)', inp)
    if m_fix:
        fix_nums = set(int(n.strip()) for n in re.findall(r'\d+', m_fix.group(1)))
        return [item for i, item in enumerate(fixable_items, 1) if i in fix_nums]

    # Không nhận ra lệnh
    return []
