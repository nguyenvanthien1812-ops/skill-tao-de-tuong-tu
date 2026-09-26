#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module Trộn Đề & Hoán Vị Mã Đề - Phiên Bản 2.0
Chức năng:
  - Hoán vị thứ tự câu hỏi và vị trí đáp án A/B/C/D theo mã đề.
  - Giữ nguyên mapping đáp án đúng (luôn biết đáp án nào là đúng sau khi hoán vị).
  - Xuất file phiếu trả lời dạng bong bóng (bubble sheet) có thể in ra và chụp ảnh chấm thi.
  - Xuất file Excel tổng hợp đáp án 4 mã đề.
"""

import sys
import copy
import random
import os
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Circle, FancyBboxPatch
import numpy as np

try:
    import openpyxl
    from openpyxl.styles import PatternFill, Alignment, Font, Border, Side
    HAS_OPENPYXL = True
except ImportError:
    HAS_OPENPYXL = False


# ─── HOÁN VỊ ĐÁP ÁN VÀ CÂU HỎI ─────────────────────────────────────────────

def shuffle_choices(question, seed):
    """
    Hoán vị 4 đáp án A/B/C/D của 1 câu hỏi.
    Input : question = {'stem': '...', 'choices': [A, B, C, D], 'correct_idx': 0}
    Output: question mới với choices đã được xáo trộn, correct_idx cập nhật đúng.
    """
    q = copy.deepcopy(question)
    rng = random.Random(seed)
    indices = list(range(4))
    rng.shuffle(indices)
    old_correct = q['correct_idx']
    q['choices'] = [q['choices'][i] for i in indices]
    q['correct_idx'] = indices.index(old_correct)
    return q


def shuffle_questions(questions, seed, keep_first=0):
    """
    Hoán vị thứ tự câu hỏi trong một phần.
    - keep_first: số câu đầu KHÔNG hoán vị (giữ nguyên thứ tự).
    Trả về list câu hỏi đã hoán vị kèm ánh xạ vị trí mới.
    """
    rng = random.Random(seed)
    fixed = questions[:keep_first]
    to_shuffle = questions[keep_first:]
    shuffled = copy.deepcopy(to_shuffle)
    rng.shuffle(shuffled)
    return fixed + shuffled


def generate_exam_variant(base_exam, variant_code, base_seed=42):
    """
    Tạo 1 mã đề mới từ đề gốc.
    - base_exam: dict chứa 'part1', 'part2', 'part3' (các phần câu hỏi)
    - variant_code: chuỗi mã đề (vd: '202')
    - base_seed: seed gốc, mỗi mã đề dùng seed khác nhau để hoán vị khác nhau
    """
    seed = base_seed + sum(ord(c) for c in str(variant_code))
    variant = {'code': variant_code}

    # Phần I: hoán vị cả câu và đáp án
    if 'part1' in base_exam:
        part1_shuffled = shuffle_questions(base_exam['part1'], seed=seed)
        variant['part1'] = [shuffle_choices(q, seed=seed + i)
                            for i, q in enumerate(part1_shuffled)]

    # Phần II: KHÔNG hoán vị câu (vì các ý a, b, c, d liên kết nhau)
    if 'part2' in base_exam:
        variant['part2'] = copy.deepcopy(base_exam['part2'])

    # Phần III: hoán vị thứ tự câu (các câu độc lập)
    if 'part3' in base_exam:
        variant['part3'] = shuffle_questions(base_exam['part3'], seed=seed + 100)

    # Phần IV (Tự luận): KHÔNG hoán vị
    if 'part4' in base_exam:
        variant['part4'] = copy.deepcopy(base_exam['part4'])

    return variant


def generate_all_variants(base_exam, base_code, n=4):
    """
    Tạo bộ n mã đề từ 1 đề gốc.
    base_code: mã đề gốc (vd: 201), sinh thêm 202, 203, 204, ...
    Trả về list các variant dicts.
    """
    variants = []
    for i in range(n):
        code = str(int(base_code) + i)
        variant = generate_exam_variant(base_exam, variant_code=code, base_seed=int(base_code))
        variants.append(variant)
    return variants


def extract_answer_key(variant):
    """Trích xuất bảng đáp án từ 1 variant."""
    key = {'code': variant['code'], 'part1': [], 'part2': {}, 'part3': []}
    labels = ['A', 'B', 'C', 'D']
    if 'part1' in variant:
        for i, q in enumerate(variant['part1']):
            key['part1'].append((i + 1, labels[q['correct_idx']]))
    if 'part2' in variant:
        for i, q in enumerate(variant['part2']):
            key['part2'][i + 1] = q.get('answers', {})  # {'a': True, 'b': False, ...}
    if 'part3' in variant:
        for i, q in enumerate(variant['part3']):
            key['part3'].append((i + 1, q.get('answer', '')))
    return key


# ─── PHIẾU TRẢ LỜI BONG BÓNG (BUBBLE SHEET) ─────────────────────────────────

def generate_bubble_sheet(variant_code, part1_answers, part2_info=None, part3_answers=None,
                          answer_key=None, output_path=None, school_name="TRƯỜNG THPT ......................"):
    """
    Tạo phiếu trả lời trắc nghiệm dạng bong bóng (bubble sheet) chuẩn A4.
    - variant_code: mã đề (vd: '201')
    - part1_answers: danh sách 12 câu (để biết số câu)
    - answer_key: nếu truyền vào → tô đen đáp án đúng (bản đáp án giáo viên)
    - output_path: đường dẫn file PNG đầu ra
    """
    IS_ANSWER_KEY = answer_key is not None
    n_part1 = len(part1_answers)  # thường 12
    n_part3 = len(part3_answers) if part3_answers else 4

    fig, ax = plt.subplots(figsize=(8.27, 11.69), dpi=150)  # A4 ở 150 DPI
    ax.set_xlim(0, 21)
    ax.set_ylim(0, 29.7)
    ax.axis('off')
    ax.set_facecolor('white')
    fig.patch.set_facecolor('white')
    ax.invert_yaxis()  # Top-to-bottom

    # ── Header ──
    ax.text(10.5, 0.7, school_name, ha='center', va='center',
            fontsize=10, fontweight='bold', fontfamily='DejaVu Sans')

    title = "PHIẾU TRẢ LỜI TRẮC NGHIỆM" if not IS_ANSWER_KEY else "ĐÁP ÁN CHÍNH THỨC (BẢN GIÁO VIÊN)"
    color = 'black' if not IS_ANSWER_KEY else '#C0392B'
    ax.text(10.5, 1.45, title, ha='center', va='center',
            fontsize=12, fontweight='bold', color=color, fontfamily='DejaVu Sans')
    ax.text(10.5, 2.1, f"Mã đề: {variant_code}   |   Môn: TOÁN 12",
            ha='center', va='center', fontsize=10, fontfamily='DejaVu Sans')

    # ── Khung thông tin thí sinh ──
    if not IS_ANSWER_KEY:
        box = FancyBboxPatch((0.5, 2.5), 20, 2.2, boxstyle="round,pad=0.1",
                             linewidth=1, edgecolor='black', facecolor='#F0F8FF')
        ax.add_patch(box)
        ax.text(1.0, 3.1, "Họ và tên: ________________________________________________",
                va='center', fontsize=9, fontfamily='DejaVu Sans')
        ax.text(1.0, 3.75, "Lớp: ______________    SBD: ________________    Ngày thi: _______________",
                va='center', fontsize=9, fontfamily='DejaVu Sans')
        ax.text(1.0, 4.4, "Chữ ký GT: ______________________    Số phách: ________________",
                va='center', fontsize=9, fontfamily='DejaVu Sans')
    else:
        ax.add_patch(FancyBboxPatch((0.5, 2.5), 20, 0.8, boxstyle="round,pad=0.05",
                                    linewidth=1, edgecolor='#C0392B', facecolor='#FFF0F0'))
        ax.text(10.5, 2.92, "Đáp án đúng được tô đen ●  |  Giữ bản này để chấm thi",
                ha='center', va='center', fontsize=9, color='#C0392B', fontfamily='DejaVu Sans')

    # ── Phần I: Bong bóng ABCD cho 12 câu ──
    start_y = 5.0 if not IS_ANSWER_KEY else 3.8
    section_box_y = start_y - 0.4
    ax.add_patch(FancyBboxPatch((0.5, section_box_y), 20, 0.45, boxstyle="round,pad=0.05",
                                linewidth=0.5, edgecolor='#2471A3', facecolor='#D6EAF8'))
    ax.text(10.5, section_box_y + 0.23, "PHẦN I  –  Trắc nghiệm nhiều phương án  (12 câu × 0,25 điểm = 3,0 điểm)",
            ha='center', va='center', fontsize=8.5, fontweight='bold', color='#1A5276',
            fontfamily='DejaVu Sans')

    labels_abcd = ['A', 'B', 'C', 'D']
    # Header cột ABCD
    col_x_start = 1.0
    cell_w = 4.6  # width per group of 4 bubbles
    q_per_col = 6
    ax.text(col_x_start + 0.7, start_y + 0.1, 'A', ha='center', fontsize=7.5,
            fontweight='bold', color='#2471A3', fontfamily='DejaVu Sans')
    ax.text(col_x_start + 1.1, start_y + 0.1, 'B', ha='center', fontsize=7.5,
            fontweight='bold', color='#2471A3', fontfamily='DejaVu Sans')
    ax.text(col_x_start + 1.5, start_y + 0.1, 'C', ha='center', fontsize=7.5,
            fontweight='bold', color='#2471A3', fontfamily='DejaVu Sans')
    ax.text(col_x_start + 1.9, start_y + 0.1, 'D', ha='center', fontsize=7.5,
            fontweight='bold', color='#2471A3', fontfamily='DejaVu Sans')
    ax.text(col_x_start + cell_w + 0.7, start_y + 0.1, 'A', ha='center', fontsize=7.5,
            fontweight='bold', color='#2471A3', fontfamily='DejaVu Sans')
    ax.text(col_x_start + cell_w + 1.1, start_y + 0.1, 'B', ha='center', fontsize=7.5,
            fontweight='bold', color='#2471A3', fontfamily='DejaVu Sans')
    ax.text(col_x_start + cell_w + 1.5, start_y + 0.1, 'C', ha='center', fontsize=7.5,
            fontweight='bold', color='#2471A3', fontfamily='DejaVu Sans')
    ax.text(col_x_start + cell_w + 1.9, start_y + 0.1, 'D', ha='center', fontsize=7.5,
            fontweight='bold', color='#2471A3', fontfamily='DejaVu Sans')

    row_h = 0.52
    for q_idx in range(n_part1):
        col = q_idx // q_per_col
        row = q_idx % q_per_col
        x_base = col_x_start + col * cell_w
        y_pos = start_y + 0.35 + row * row_h

        # Số câu
        ax.text(x_base + 0.2, y_pos, f"Câu {q_idx + 1}:", fontsize=8,
                va='center', fontfamily='DejaVu Sans')

        # Bong bóng A, B, C, D
        correct_label = None
        if IS_ANSWER_KEY and answer_key:
            p1_key = {k: v for k, v in answer_key.get('part1', [])}
            correct_label = p1_key.get(q_idx + 1)

        for opt_idx, lbl in enumerate(labels_abcd):
            cx = x_base + 0.7 + opt_idx * 0.4
            is_correct = IS_ANSWER_KEY and (lbl == correct_label)
            bubble_color = '#1A5276' if is_correct else 'white'
            edge_color = '#1A5276' if is_correct else '#555555'
            circle = Circle((cx, y_pos), 0.13, color=bubble_color,
                             ec=edge_color, linewidth=0.8, zorder=5)
            ax.add_patch(circle)
            txt_color = 'white' if is_correct else '#333333'
            ax.text(cx, y_pos, lbl, ha='center', va='center',
                    fontsize=6, color=txt_color, fontweight='bold',
                    fontfamily='DejaVu Sans', zorder=6)

    # ── Phần II: Đúng/Sai ──
    p2_start = start_y + 0.35 + q_per_col * row_h + 0.5
    ax.add_patch(FancyBboxPatch((0.5, p2_start - 0.35), 20, 0.4, boxstyle="round,pad=0.05",
                                linewidth=0.5, edgecolor='#1E8449', facecolor='#D5F5E3'))
    ax.text(10.5, p2_start - 0.15, "PHẦN II  –  Trắc nghiệm đúng/sai  (2 câu, mỗi câu 4 ý = 1,0 điểm)",
            ha='center', va='center', fontsize=8.5, fontweight='bold', color='#145A32',
            fontfamily='DejaVu Sans')

    for q_ii in range(2):
        yy = p2_start + 0.15 + q_ii * 0.95
        ax.text(col_x_start, yy, f"Câu {q_ii + 1}:", fontsize=8, va='center',
                fontfamily='DejaVu Sans')
        for sub_idx, sub_lbl in enumerate(['a', 'b', 'c', 'd']):
            xb = col_x_start + 0.7 + sub_idx * 2.0
            for td_idx, td_lbl in enumerate(['Đ', 'S']):
                cx2 = xb + td_idx * 0.55
                ax.text(cx2 - 0.22, yy - 0.28, td_lbl, fontsize=6.5, ha='center',
                        va='center', color='#1E8449', fontfamily='DejaVu Sans')
                circle2 = Circle((cx2, yy), 0.13, color='white', ec='#1E8449',
                                  linewidth=0.8, zorder=5)
                ax.add_patch(circle2)
            ax.text(xb + 0.15, yy + 0.25, f'ý {sub_lbl})', fontsize=6.5, ha='center',
                    va='center', fontfamily='DejaVu Sans')

    # ── Phần III: Trả lời ngắn ──
    p3_start = p2_start + 0.15 + 2 * 0.95 + 0.6
    ax.add_patch(FancyBboxPatch((0.5, p3_start - 0.35), 20, 0.4, boxstyle="round,pad=0.05",
                                linewidth=0.5, edgecolor='#7D3C98', facecolor='#F4ECF7'))
    ax.text(10.5, p3_start - 0.15,
            "PHẦN III  –  Trả lời ngắn  (4 câu × 0,5 điểm = 2,0 điểm)",
            ha='center', va='center', fontsize=8.5, fontweight='bold', color='#4A235A',
            fontfamily='DejaVu Sans')

    for q3_idx in range(n_part3):
        yy3 = p3_start + 0.2 + q3_idx * 0.7
        ax.text(col_x_start, yy3, f"Câu III.{q3_idx + 1}:", fontsize=8, va='center',
                fontfamily='DejaVu Sans')
        if IS_ANSWER_KEY and part3_answers and q3_idx < len(part3_answers):
            ans_val = str(part3_answers[q3_idx][1])
            ax.add_patch(FancyBboxPatch((col_x_start + 1.4, yy3 - 0.17), 3.0, 0.35,
                                        boxstyle="round,pad=0.05",
                                        linewidth=1, edgecolor='#7D3C98', facecolor='#EBD9F7'))
            ax.text(col_x_start + 2.9, yy3, ans_val, ha='center', va='center',
                    fontsize=10, fontweight='bold', color='#4A235A',
                    fontfamily='DejaVu Sans')
        else:
            ax.add_patch(FancyBboxPatch((col_x_start + 1.4, yy3 - 0.15), 5.0, 0.32,
                                        boxstyle="round,pad=0.05",
                                        linewidth=0.8, edgecolor='#7D3C98', facecolor='white'))

    # ── Góc cắt (alignment corners) để nhận dạng khi chụp ảnh ──
    for cx, cy in [(0.15, 0.15), (20.85, 0.15), (0.15, 29.55), (20.85, 29.55)]:
        ax.add_patch(Circle((cx, cy), 0.22, color='black', zorder=10))

    # ── Barcode QR/mã đề nho nhỏ góc phải dưới ──
    ax.text(19.5, 29.3, f"#{variant_code}", ha='right', va='bottom', fontsize=7,
            color='gray', fontfamily='DejaVu Sans')

    plt.tight_layout(pad=0)
    if output_path is None:
        output_path = f'phieu_tra_loi_{variant_code}.png'
    fig.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f"[OK] Phiếu trả lời: {output_path}")
    return output_path


# ─── XUẤT FILE EXCEL TỔNG HỢP ĐÁP ÁN ────────────────────────────────────────

def export_answer_key_excel(all_keys, output_path):
    """
    Xuất file Excel tổng hợp đáp án tất cả mã đề.
    all_keys: list of dict từ extract_answer_key()
    """
    if not HAS_OPENPYXL:
        print("[!] Cần cài openpyxl: pip install openpyxl")
        return False

    wb = openpyxl.Workbook()
    wb.remove(wb.active)

    color_map = {'A': 'DDEEFF', 'B': 'DDFFD6', 'C': 'FFF3CC', 'D': 'FFE0E0'}
    header_fill = PatternFill("solid", fgColor="1A5276")
    header_font = Font(color="FFFFFF", bold=True, size=11)
    center = Alignment(horizontal='center', vertical='center')
    thin = Side(style='thin', color="CCCCCC")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)

    for key in all_keys:
        ws = wb.create_sheet(title=f"Mã đề {key['code']}")
        ws.row_dimensions[1].height = 22
        ws.column_dimensions['A'].width = 12

        # Header hàng 1: Số câu
        ws.cell(row=1, column=1, value=f"Mã đề {key['code']}").font = Font(bold=True, size=13)
        ws.merge_cells('A1:N1')
        ws['A1'].alignment = center
        ws['A1'].fill = header_fill
        ws['A1'].font = header_font

        # Header hàng 2
        ws.cell(row=2, column=1, value="Câu").fill = header_fill
        ws.cell(row=2, column=1).font = header_font
        ws.cell(row=2, column=1).alignment = center
        ws.cell(row=3, column=1, value="Đáp án").fill = header_fill
        ws.cell(row=3, column=1).font = header_font
        ws.cell(row=3, column=1).alignment = center

        for i, (q_num, ans) in enumerate(key['part1'], start=2):
            ws.cell(row=2, column=i, value=f"Câu {q_num}").alignment = center
            ws.cell(row=2, column=i).border = border
            cell = ws.cell(row=3, column=i, value=ans)
            cell.alignment = center
            cell.font = Font(bold=True, size=13, color="C0392B")
            cell.fill = PatternFill("solid", fgColor=color_map.get(ans, 'FFFFFF'))
            cell.border = border
            ws.column_dimensions[cell.column_letter].width = 7

        # Phần III
        if key['part3']:
            row_offset = 5
            ws.cell(row=row_offset, column=1, value="Phần III").font = Font(bold=True)
            for i, (q_num, ans) in enumerate(key['part3'], start=2):
                ws.cell(row=row_offset, column=i, value=f"III.{q_num}").alignment = center
                ws.cell(row=row_offset, column=i).border = border
                cell = ws.cell(row=row_offset + 1, column=i, value=str(ans))
                cell.alignment = center
                cell.font = Font(bold=True, size=12, color="1A6B3A")
                cell.fill = PatternFill("solid", fgColor="EAF7EA")
                cell.border = border

    wb.save(output_path)
    print(f"[OK] File đáp án Excel: {output_path}")
    return True


# ─── PIPELINE CHÍNH: TẠO BỘ 4 MÃ ĐỀ ─────────────────────────────────────────

def generate_exam_set(base_exam, output_dir, base_code="201", n_variants=4,
                      school_name="TRƯỜNG THPT ......................"):
    """
    Tạo trọn bộ n mã đề với đầy đủ:
      - Phiếu trả lời học sinh (PNG)
      - Phiếu đáp án giáo viên (PNG, bong bóng tô đen)
      - File Excel tổng hợp đáp án tất cả mã đề
    Trả về dict kết quả.
    """
    os.makedirs(output_dir, exist_ok=True)
    variants = generate_all_variants(base_exam, base_code=base_code, n=n_variants)
    all_keys = []
    results = {}

    for v in variants:
        code = v['code']
        key = extract_answer_key(v)
        all_keys.append(key)

        # Phiếu học sinh
        sheet_student = os.path.join(output_dir, f'phieu_hoc_sinh_{code}.png')
        generate_bubble_sheet(
            variant_code=code,
            part1_answers=key['part1'],
            part3_answers=key['part3'],
            answer_key=None,
            output_path=sheet_student,
            school_name=school_name
        )

        # Phiếu đáp án giáo viên
        sheet_key = os.path.join(output_dir, f'dap_an_giao_vien_{code}.png')
        generate_bubble_sheet(
            variant_code=code,
            part1_answers=key['part1'],
            part3_answers=key['part3'],
            answer_key=key,
            output_path=sheet_key,
            school_name=school_name
        )

        results[code] = {
            'variant': v,
            'key': key,
            'phieu_hoc_sinh': sheet_student,
            'phieu_dap_an_gv': sheet_key
        }

    # Excel tổng hợp
    excel_path = os.path.join(output_dir, f'DAP_AN_TONG_HOP_{n_variants}_MA_DE.xlsx')
    export_answer_key_excel(all_keys, excel_path)
    results['excel'] = excel_path

    return results
