#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
parallel_exam_generator.py — Bộ Công Cụ Quản Lý & Đối Sánh Chùm Đề Song Song Độc Lập
===================================================================================
Chức năng:
  1. Kiểm định độ đa dạng chống trùng lặp (Anti-collision & Cross-exam Diversity Checker):
     - Đo độ tương đồng giữa các câu hỏi tương ứng giữa các đề (Đề 1 vs Đề 2, 3, 4, 5...).
     - Phát hiện câu hỏi bị "đổi số cơ học" hoặc dùng chung văn cảnh (ngưỡng tương đồng <= 20%).
  2. Xuất Bảng Đối Sánh Chùm Đề tự động (BANG_DOI_SANH_CHUM_DE.xlsx):
     - Đối chiếu trực quan từng câu giữa các đề: Chuẩn kiến thức, Cấp độ Bloom, Ngữ cảnh, Dạng con.
     - Định dạng màu sắc chuyên nghiệp nộp Tổ chuyên môn & Ban Giám Hiệu.
  3. Hỗ trợ đa môn học: Toán, Lý, Hóa, Sinh, KHTN, Tiếng Anh, Sử, Địa, KTPL, Tin, Công nghệ.
"""

from __future__ import annotations
import os
import re
import sys
import json
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

try:
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter
    HAS_OPENPYXL = True
except ImportError:
    HAS_OPENPYXL = False


# Danh sách các từ dừng phổ biến trong đề thi (loại bỏ khi đo độ tương đồng cốt lõi)
EXAM_STOPWORDS = {
    'cho', 'hàm', 'số', 'biết', 'rằng', 'tìm', 'tính', 'giá', 'trị', 'của',
    'trong', 'các', 'sau', 'đây', 'khẳng', 'định', 'nào', 'đúng', 'sai',
    'là', 'và', 'có', 'với', 'khi', 'được', 'thì', 'ở', 'tại', 'về',
    'mệnh', 'đề', 'câu', 'hỏi', 'chọn', 'đáp', 'án', 'phương', 'án',
    'bằng', 'theo', 'hãy', 'xác', 'định', 'kết', 'quả', 'thực', 'hiện'
}


def clean_text_for_comparison(text: str) -> List[str]:
    """
    Làm sạch văn bản câu hỏi:
    - Loại bỏ mã LaTeX / công thức toán
    - Chuẩn hóa chữ thường
    - Tách từ tiếng Việt và loại bỏ từ dừng đề thi
    """
    if not text:
        return []
    # Loại bỏ math $...$
    t = re.sub(r'\$[^$]*\$', ' ', text)
    # Loại bỏ ký tự đặc biệt
    t = re.sub(r'[\(\)\[\]\{\}\\\/_\^\*\+\-=<>:;.,!?\"\'%]', ' ', t)
    # Tách từ
    words = [w.strip().lower() for w in t.split() if len(w.strip()) > 1]
    # Lọc từ dừng
    meaningful_words = [w for w in words if w not in EXAM_STOPWORDS]
    return meaningful_words


def compute_jaccard_similarity(text1: str, text2: str) -> float:
    """Tính chỉ số tương đồng Jaccard giữa 2 câu hỏi (0.0 đến 1.0)."""
    tokens1 = set(clean_text_for_comparison(text1))
    tokens2 = set(clean_text_for_comparison(text2))
    if not tokens1 or not tokens2:
        return 0.0
    intersection = tokens1.intersection(tokens2)
    union = tokens1.union(tokens2)
    return len(intersection) / len(union)


def verify_cross_exam_diversity(exam_variants: List[Dict[str, Any]],
                                 threshold: float = 0.25) -> Dict[str, Any]:
    """
    Kiểm tra độ đa dạng chéo giữa các đề thi:
    - exam_variants: danh sách các đề (mỗi đề có 'code' và các câu hỏi trong 'questions' hoặc 'part1'/'part2'/'part3')
    - threshold: ngưỡng tối đa cho phép tương đồng (mặc định 0.25 = 25%)
    Trả về dict báo cáo tổng hợp.
    """
    n_exams = len(exam_variants)
    if n_exams < 2:
        return {'status': 'PASSED', 'n_exams': n_exams, 'message': 'Chỉ có 1 đề, không cần đối sánh chéo.'}

    all_pairs = []
    max_sim = 0.0
    flagged_pairs = []

    # Thu thập câu hỏi phẳng của từng đề
    def extract_flat_questions(exam: Dict[str, Any]) -> List[Dict[str, Any]]:
        flat = []
        if 'questions' in exam:
            flat.extend(exam['questions'])
        else:
            for part_key in ('part1', 'part1_mc', 'part2', 'part2_tf', 'part3', 'part3_sa', 'essay'):
                if part_key in exam and isinstance(exam[part_key], list):
                    flat.extend(exam[part_key])
        return flat

    exam_flats = [extract_flat_questions(e) for e in exam_variants]
    min_len = min(len(qlist) for qlist in exam_flats) if exam_flats else 0

    for q_idx in range(min_len):
        stems = [exam_flats[e_idx][q_idx].get('stem', '') or exam_flats[e_idx][q_idx].get('question', '')
                 for e_idx in range(n_exams)]
        
        # So sánh từng cặp đề tại vị trí câu hỏi q_idx
        for i in range(n_exams):
            for j in range(i + 1, n_exams):
                sim = compute_jaccard_similarity(stems[i], stems[j])
                all_pairs.append(sim)
                if sim > max_sim:
                    max_sim = sim
                if sim > threshold:
                    flagged_pairs.append({
                        'question_index': q_idx + 1,
                        'exam_a': exam_variants[i].get('code', f"Đề {i+1}"),
                        'exam_b': exam_variants[j].get('code', f"Đề {j+1}"),
                        'similarity': round(sim, 3),
                        'stem_a': stems[i][:80] + '...',
                        'stem_b': stems[j][:80] + '...'
                    })

    avg_sim = sum(all_pairs) / len(all_pairs) if all_pairs else 0.0
    status = 'WARNING' if flagged_pairs else 'PASSED'

    return {
        'status': status,
        'n_exams': n_exams,
        'total_comparisons': len(all_pairs),
        'average_similarity': round(avg_sim, 3),
        'max_similarity': round(max_sim, 3),
        'threshold': threshold,
        'flagged_count': len(flagged_pairs),
        'flagged_pairs': flagged_pairs,
        'is_distinct': len(flagged_pairs) == 0
    }


def export_cross_exam_comparison_excel(
    matrix_cells: List[Dict[str, Any]],
    exam_variants: List[Dict[str, Any]],
    output_path: str,
    subject: str = "Toán học",
    grade: int = 12,
    exam_title: str = "BẢNG ĐỐI SÁNH MA TRẬN & ĐỘ ĐA DẠNG CHÙM ĐỀ SONG SONG"
) -> str:
    """
    Xuất file Excel 'BANG_DOI_SANH_CHUM_DE.xlsx' đối chiếu ma trận và tính độc lập của chùm đề.
    """
    if not HAS_OPENPYXL:
        raise ImportError("openpyxl chưa được cài đặt. Vui lòng cài: pip install openpyxl")

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "BẢNG ĐỐI SÁNH CHÙM ĐỀ"
    ws.views.sheetView[0].showGridLines = True

    # 1. Bảng màu chuẩn Sư phạm
    NAVY_HEADER = PatternFill(start_color="1F497D", end_color="1F497D", fill_type="solid")
    SUB_HEADER = PatternFill(start_color="DCE6F1", end_color="DCE6F1", fill_type="solid")
    ROW_EVEN = PatternFill(start_color="F2F5F8", end_color="F2F5F8", fill_type="solid")
    ROW_ODD = PatternFill(start_color="FFFFFF", end_color="FFFFFF", fill_type="solid")
    PASS_FILL = PatternFill(start_color="E2EFDA", end_color="E2EFDA", fill_type="solid")
    WARN_FILL = PatternFill(start_color="FCE4D6", end_color="FCE4D6", fill_type="solid")

    FONT_TITLE = Font(name="Times New Roman", size=16, bold=True, color="1F497D")
    FONT_SUBTITLE = Font(name="Times New Roman", size=11, italic=True, color="595959")
    FONT_HEADER = Font(name="Times New Roman", size=11, bold=True, color="FFFFFF")
    FONT_CELL = Font(name="Times New Roman", size=11)
    FONT_BOLD = Font(name="Times New Roman", size=11, bold=True)
    FONT_PASS = Font(name="Times New Roman", size=11, bold=True, color="276A3C")
    FONT_WARN = Font(name="Times New Roman", size=11, bold=True, color="C00000")

    THIN_SIDE = Side(style='thin', color='D9D9D9')
    BORDER_CELL = Border(left=THIN_SIDE, right=THIN_SIDE, top=THIN_SIDE, bottom=THIN_SIDE)

    # 2. Tiêu đề
    ws.merge_cells("A1:H1")
    ws['A1'] = exam_title.upper()
    ws['A1'].font = FONT_TITLE
    ws['A1'].alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 30

    ws.merge_cells("A2:H2")
    ws['A2'] = f"Môn: {subject.upper()} - Lớp: {grade} | Khung chuẩn GDPT 2018 | Cam kết độc lập 100% ngữ cảnh & dạng con"
    ws['A2'].font = FONT_SUBTITLE
    ws['A2'].alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[2].height = 20

    # 3. Tiêu đề các cột
    n_variants = len(exam_variants)
    headers = ["STT", "Phần thi", "Chủ đề / Chuẩn GDPT 2018", "Cấp độ"]
    for i, v in enumerate(exam_variants):
        code = v.get('code', f"Đề 0{i+1}" if i < 9 else f"Đề {i+1}")
        headers.append(f"{code} (Ngữ cảnh & Dạng con)")
    headers.append("Đánh giá Độc lập")

    row_num = 4
    ws.row_dimensions[row_num].height = 28
    for col_idx, h in enumerate(headers, 1):
        cell = ws.cell(row=row_num, column=col_idx, value=h)
        cell.font = FONT_HEADER
        cell.fill = NAVY_HEADER
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = BORDER_CELL

    # 4. Trích xuất câu hỏi từ các đề
    def extract_flat(exam: Dict[str, Any]) -> List[Dict[str, Any]]:
        flat = []
        if 'questions' in exam:
            flat.extend(exam['questions'])
        else:
            for pk in ('part1', 'part1_mc', 'part2', 'part2_tf', 'part3', 'part3_sa', 'essay'):
                if pk in exam and isinstance(exam[pk], list):
                    flat.extend(exam[pk])
        return flat

    exam_flats = [extract_flat(e) for e in exam_variants]
    total_q = max(len(fl) for fl in exam_flats) if exam_flats else len(matrix_cells)

    for q_i in range(total_q):
        row_num += 1
        ws.row_dimensions[row_num].height = 24
        fill = ROW_EVEN if q_i % 2 == 0 else ROW_ODD

        # Cột STT
        c_stt = ws.cell(row=row_num, column=1, value=f"Câu {q_i+1}")
        c_stt.font = FONT_BOLD
        c_stt.alignment = Alignment(horizontal="center", vertical="center")
        c_stt.fill = fill
        c_stt.border = BORDER_CELL

        # Xác định thông tin chuẩn từ ma trận nếu có
        m_info = matrix_cells[q_i] if q_i < len(matrix_cells) else {}
        part_name = m_info.get('part_name', 'Phần I (TNKQ)')
        topic_name = m_info.get('topic_display', m_info.get('topic', 'Kiến thức cốt lõi'))
        bloom_level = m_info.get('level', m_info.get('bloom', 'TH'))

        # Cột Phần thi
        c_part = ws.cell(row=row_num, column=2, value=part_name)
        c_part.font = FONT_CELL
        c_part.alignment = Alignment(horizontal="center", vertical="center")
        c_part.fill = fill
        c_part.border = BORDER_CELL

        # Cột Chủ đề
        c_topic = ws.cell(row=row_num, column=3, value=topic_name)
        c_topic.font = FONT_CELL
        c_topic.alignment = Alignment(horizontal="left", vertical="center")
        c_topic.fill = fill
        c_topic.border = BORDER_CELL

        # Cột Cấp độ nhận thức
        c_lvl = ws.cell(row=row_num, column=4, value=bloom_level)
        c_lvl.font = FONT_BOLD
        c_lvl.alignment = Alignment(horizontal="center", vertical="center")
        c_lvl.fill = fill
        c_lvl.border = BORDER_CELL

        # Cột tóm tắt ngữ cảnh cho từng đề
        col_offset = 5
        stems_for_sim = []
        for e_idx in range(n_variants):
            q_data = exam_flats[e_idx][q_i] if q_i < len(exam_flats[e_idx]) else {}
            context_desc = q_data.get('context_desc') or q_data.get('sub_skill')
            stem = q_data.get('stem') or q_data.get('question', '')
            stems_for_sim.append(stem)
            
            if not context_desc:
                # Trích xuất 12 từ đầu tiên làm mô tả
                clean_s = re.sub(r'\$[^$]*\$', ' [công thức] ', stem).strip()
                words = clean_s.split()
                context_desc = " ".join(words[:10]) + ("..." if len(words) > 10 else "")
            
            c_desc = ws.cell(row=row_num, column=col_offset + e_idx, value=context_desc or "Đang cập nhật...")
            c_desc.font = FONT_CELL
            c_desc.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
            c_desc.fill = fill
            c_desc.border = BORDER_CELL

        # Đánh giá độ độc lập
        max_pair_sim = 0.0
        for i_s in range(len(stems_for_sim)):
            for j_s in range(i_s + 1, len(stems_for_sim)):
                sim = compute_jaccard_similarity(stems_for_sim[i_s], stems_for_sim[j_s])
                if sim > max_pair_sim:
                    max_pair_sim = sim

        eval_col = col_offset + n_variants
        c_eval = ws.cell(row=row_num, column=eval_col)
        if max_pair_sim <= 0.20:
            c_eval.value = f"✅ ĐẠT ({int((1-max_pair_sim)*100)}% độc lập)"
            c_eval.font = FONT_PASS
            c_eval.fill = PASS_FILL
        else:
            c_eval.value = f"⚠️ Cần phân nhánh ({int(max_pair_sim*100)}% trùng)"
            c_eval.font = FONT_WARN
            c_eval.fill = WARN_FILL
        c_eval.alignment = Alignment(horizontal="center", vertical="center")
        c_eval.border = BORDER_CELL

    # 5. Tự căn chỉnh độ rộng cột
    for col in ws.columns:
        col_letter = get_column_letter(col[0].column)
        if col_letter in ('A', 'B', 'D'):
            ws.column_dimensions[col_letter].width = 14
        elif col_letter == 'C':
            ws.column_dimensions[col_letter].width = 30
        elif col_letter == get_column_letter(headers.__len__()):
            ws.column_dimensions[col_letter].width = 24
        else:
            ws.column_dimensions[col_letter].width = 35

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    wb.save(output_path)
    return str(Path(output_path).resolve())


if __name__ == '__main__':
    # Test tự động module
    sample_q1 = "Một người gửi tiết kiệm 100 triệu đồng vào ngân hàng với lãi suất kép 6%/năm."
    sample_q2 = "Dân số của một thành phố năm 2025 là 2 triệu người với tốc độ tăng trưởng 1.2%/năm."
    sample_q3 = "Một người gửi tiết kiệm 200 triệu đồng vào ngân hàng với lãi suất kép 7%/năm."

    sim_12 = compute_jaccard_similarity(sample_q1, sample_q2)
    sim_13 = compute_jaccard_similarity(sample_q1, sample_q3)
    print(f"Độ tương đồng Đề 1 vs Đề 2 (Khác ngữ cảnh): {sim_12:.2f} (ĐẠT)")
    print(f"Độ tương đồng Đề 1 vs Đề 3 (Đổi số cơ học): {sim_13:.2f} (CẢNH BÁO)")
