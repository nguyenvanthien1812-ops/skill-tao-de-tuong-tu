# -*- coding: utf-8 -*-
"""
exam_reviewer_cli.py  —  BỘ CÔNG CỤ THẨM ĐỊNH ĐỀ KIỂM TRA TOÁN
────────────────────────────────────────────────────────────────────
Điểm vào chính. Giáo viên chỉ cần cung cấp 3 đường dẫn file và chạy:

    python exam_reviewer_cli.py \
        --matrix  "đường_dẫn/ma_tran.docx" \
        --exam    "đường_dẫn/de_hoc_sinh.docx" \
        --rubric  "đường_dẫn/huong_dan_cham.docx" \
        --output  "đường_dẫn/thu_muc_bao_cao" \
        [--grade  8] \
        [--school "Trường THCS ABC"] \
        [--teacher "Nguyễn Văn A"]

Hệ thống sẽ:
  1. Đọc và phân tích 3 file
  2. Chạy toàn bộ 42 tiêu chí kiểm tra
  3. Xuất Biên bản thẩm định Word + Dashboard Excel
  4. Trình Kế hoạch sửa chữa trong terminal
  5. Hỏi GV có muốn Auto-fix không → nếu đồng ý, sửa file và lưu bản FIXED
"""
import os
import sys
import argparse

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr and hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

# Thêm thư mục cha vào path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR  = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, PARENT_DIR)

from tham_dinh.exam_extractor  import extract_exam_data
from tham_dinh.exam_validator  import run_all_checks
from tham_dinh.report_generator import run_full_report, generate_correction_plan
from tham_dinh.auto_fixer       import run_auto_fix, parse_approved_items


BANNER = """
╔══════════════════════════════════════════════════════════════════╗
║      BỘ CÔNG CỤ THẨM ĐỊNH ĐỀ KIỂM TRA MÔN TOÁN (GDPT 2018)   ║
║      Phiên bản 1.0 | Ưu tiên môn Toán THCS lớp 6–9             ║
╚══════════════════════════════════════════════════════════════════╝
"""


def main():
    parser = argparse.ArgumentParser(
        description="Thẩm định đề kiểm tra Toán chuẩn GDPT 2018"
    )
    parser.add_argument('--matrix',  required=True,  help='Đường dẫn file Ma trận & Bản đặc tả (.docx)')
    parser.add_argument('--exam',    required=True,  help='Đường dẫn file Đề thi học sinh (.docx)')
    parser.add_argument('--rubric',  required=True,  help='Đường dẫn file Hướng dẫn chấm (.docx)')
    parser.add_argument('--output',  default='',     help='Thư mục lưu báo cáo đầu ra')
    parser.add_argument('--grade',   default='8',    help='Khối lớp (6/7/8/9/10/11/12), mặc định 8')
    parser.add_argument('--school',  default='',     help='Tên trường (tuỳ chọn)')
    parser.add_argument('--teacher', default='',     help='Tên giáo viên ra đề (tuỳ chọn)')
    parser.add_argument('--no-fix',  action='store_true', help='Bỏ qua bước hỏi Auto-fix')
    args = parser.parse_args()

    print(BANNER)

    # Kiểm tra file tồn tại
    for label, path in [("Ma trận", args.matrix), ("Đề thi", args.exam), ("HDC", args.rubric)]:
        if not os.path.exists(path):
            print(f"[Lỗi] Không tìm thấy file {label}: {path}")
            sys.exit(1)

    # Xác định thư mục đầu ra
    if args.output:
        output_dir = args.output
    else:
        output_dir = os.path.join(os.path.dirname(args.exam), "BAO_CAO_THAM_DINH")

    print(f"[INFO] Thư mục báo cáo: {output_dir}")
    print()

    # ── BƯỚC 1: TRÍCH XUẤT DỮ LIỆU ───────────────────────────────────────────
    print("=" * 65)
    print("BƯỚC 1: TRÍCH XUẤT DỮ LIỆU TỪ 3 FILE")
    print("=" * 65)
    data = extract_exam_data(args.matrix, args.exam, args.rubric)

    # ── BƯỚC 2: KIỂM TRA BỘ TIÊU CHÍ THẨM ĐỊNH ─────────────────────────────
    print()
    print("=" * 65)
    print("BƯỚC 2: KIỂM TRA BỘ TIÊU CHÍ THẨM ĐỊNH (CHUẨN GDPT 2018)")
    print("=" * 65)
    rpt = run_all_checks(data)

    # ── BƯỚC 3: XUẤT BÁO CÁO ─────────────────────────────────────────────────
    print()
    print("=" * 65)
    print("BƯỚC 3: XUẤT BÁO CÁO THẨM ĐỊNH")
    print("=" * 65)
    report_result = run_full_report(
        rpt, data, output_dir,
        school_name=args.school,
        teacher_name=args.teacher,
        exam_grade=args.grade
    )
    print(f"  → Biên bản Word: {report_result['word_path']}")
    print(f"  → Dashboard Excel: {report_result['excel_path']}")

    # ── BƯỚC 4: TRÌNH KẾ HOẠCH SỬA CHỮA ─────────────────────────────────────
    print()
    print("=" * 65)
    print("BƯỚC 4: KẾ HOẠCH SỬA CHỮA")
    print("=" * 65)
    correction_md = report_result['correction_md']
    # In ra terminal (bỏ markdown)
    clean = correction_md.replace("**", "").replace("##", "").replace(">", "  ")
    print(clean)

    # ── BƯỚC 5: AUTO-FIX (nếu có lỗi fixable) ────────────────────────────────
    fixable = rpt.get_fixable()
    if fixable and not args.no_fix:
        print()
        print("=" * 65)
        print(f"BƯỚC 5: AUTO-FIX ({len(fixable)} hạng mục có thể sửa tự động)")
        print("=" * 65)
        print()
        for i, item in enumerate(fixable, 1):
            print(f"  Fix {i}. [{item.code}] {item.fix_action}")
        print()
        print("Thầy/Cô có muốn tự động sửa các lỗi trên không?")
        print("  → Gõ 'OK' hoặc 'Đồng ý' để sửa TẤT CẢ")
        print("  → Gõ 'Bỏ qua 2,3' để bỏ qua Fix 2 và Fix 3")
        print("  → Gõ 'Fix 1,4' để chỉ sửa Fix 1 và Fix 4")
        print("  → Gõ 'Không' hoặc nhấn Enter để bỏ qua")
        print()

        try:
            user_input = input("Thầy/Cô chọn: ").strip()
        except (EOFError, KeyboardInterrupt):
            user_input = ""

        if user_input:
            approved = parse_approved_items(user_input, fixable)
            if approved:
                print(f"\n[AutoFix] Bắt đầu sửa {len(approved)} hạng mục...")
                fix_result = run_auto_fix(
                    approved_items=approved,
                    data=data,
                    exam_path=args.exam,
                    rubric_path=args.rubric,
                    output_dir=output_dir
                )
                print()
                print("Kết quả Auto-fix:")
                for res in fix_result['results']:
                    clean_res = res.replace("**", "")
                    print(f"  {clean_res}")
                print()
                print(f"  → Đề thi đã sửa: {fix_result['exam_fixed']}")
                print(f"  → HDC đã sửa:    {fix_result['rubric_fixed']}")
            else:
                print("[AutoFix] Không nhận ra lệnh. Bỏ qua bước Auto-fix.")
        else:
            print("[AutoFix] Bỏ qua. Thầy/Cô có thể sửa thủ công theo hướng dẫn trong báo cáo.")
    else:
        if not fixable:
            print()
            print("ℹ️  Không có hạng mục nào cần/có thể Auto-fix.")

    # ── KẾT THÚC ─────────────────────────────────────────────────────────────
    print()
    print("=" * 65)
    print("HOÀN TẤT THẨM ĐỊNH")
    print("=" * 65)
    print(f"  Tổng kết: {rpt.summary}")
    print(f"  Báo cáo đã lưu tại: {output_dir}")
    print()

    # Return code: 0 = đạt, 1 = có lỗi
    sys.exit(0 if rpt.overall_pass else 1)


if __name__ == '__main__':
    main()
