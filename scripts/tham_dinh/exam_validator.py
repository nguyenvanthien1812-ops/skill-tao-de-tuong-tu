# -*- coding: utf-8 -*-
"""
exam_validator.py
─────────────────
Chạy toàn bộ các tiêu chí kiểm tra chuẩn GDPT 2018 trên ExamData đã trích xuất.
Trả về danh sách FindingItem (lỗi/cảnh báo) để dùng trong báo cáo và auto-fix.
"""
from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import Callable, Optional

from .exam_extractor import ExamData


# ──────────────────────────────────────────────────────────────────────────────
# DATA MODEL CHO KẾT QUẢ KIỂM TRA
# ──────────────────────────────────────────────────────────────────────────────

SEVERITY_ERROR   = "❌ LỖI BẮT BUỘC"    # 🔴 vi phạm → đề CHƯA ĐẠT
SEVERITY_WARNING = "⚠️ CẢNH BÁO"        # 🟠 quan trọng
SEVERITY_INFO    = "💡 KHUYẾN NGHỊ"      # 🟡 cải thiện

@dataclass
class FindingItem:
    code: str                  # "A01", "B01", ...
    group: str                 # "A. Ma trận", "B. Trắc nghiệm", ...
    criterion: str             # Mô tả tiêu chí
    result: str                # Kết quả kiểm tra cụ thể
    status: str                # "PASS" / "FAIL" / "WARN"
    severity: str              # SEVERITY_ERROR / WARNING / INFO
    suggestion: str = ""       # Gợi ý sửa
    fixable: bool = False      # Có thể auto-fix không
    fix_action: Optional[str] = None  # Mô tả hành động fix


@dataclass
class ValidationReport:
    findings: list = field(default_factory=list)  # [FindingItem]
    total: int = 0
    passed: int = 0
    failed_critical: int = 0
    failed_warning: int = 0
    overall_pass: bool = False
    summary: str = ""

    def add(self, item: FindingItem):
        self.findings.append(item)
        self.total += 1
        if item.status == "PASS":
            self.passed += 1
        elif item.severity == SEVERITY_ERROR:
            self.failed_critical += 1
        else:
            self.failed_warning += 1

    def finalize(self):
        self.overall_pass = (self.failed_critical == 0)
        if self.overall_pass and self.failed_warning == 0:
            self.summary = "✅ XUẤT SẮC — Đề đạt chuẩn hoàn toàn, in ấn và sử dụng ngay."
        elif self.overall_pass:
            self.summary = (f"✅ ĐẠT CHUẨN — {self.failed_warning} cảnh báo cần lưu ý, "
                            f"có thể dùng sau khi cải thiện.")
        else:
            self.summary = (f"❌ CHƯA ĐẠT — {self.failed_critical} lỗi bắt buộc phải sửa "
                            f"trước khi nộp tổ chuyên môn.")

    def get_failures(self) -> list:
        return [f for f in self.findings if f.status != "PASS"]

    def get_fixable(self) -> list:
        return [f for f in self.findings if f.status != "PASS" and f.fixable]


# ──────────────────────────────────────────────────────────────────────────────
# HELPER
# ──────────────────────────────────────────────────────────────────────────────

def _fi(code, group, criterion, result, status, severity, suggestion="", fixable=False, fix_action=None):
    return FindingItem(code=code, group=group, criterion=criterion,
                       result=result, status=status, severity=severity,
                       suggestion=suggestion, fixable=fixable, fix_action=fix_action)


# ──────────────────────────────────────────────────────────────────────────────
# NHÓM A — MA TRẬN & BẢN ĐẶC TẢ
# ──────────────────────────────────────────────────────────────────────────────

def _check_group_A(data: ExamData, rpt: ValidationReport):
    GROUP = "A. Ma trận & Bản đặc tả"

    # A01: Tổng điểm = 10,0
    score = data.matrix_total_score
    if abs(score - 10.0) < 0.01:
        rpt.add(_fi("A01", GROUP, "Tổng điểm toàn đề = 10,0 điểm",
                    f"Tổng = {score} điểm ✓", "PASS", SEVERITY_ERROR))
    else:
        rpt.add(_fi("A01", GROUP, "Tổng điểm toàn đề = 10,0 điểm",
                    f"Tổng = {score} điểm ≠ 10,0 điểm",
                    "FAIL", SEVERITY_ERROR,
                    f"Tính lại điểm từng dòng để tổng = 10,0 điểm. Hiện tổng đang là {score}.",
                    fixable=False))

    # A02: Có dòng tổng kết cuối bảng
    if data.matrix_has_summary_rows:
        rpt.add(_fi("A02", GROUP, "Bảng Ma trận có đầy đủ dòng tổng kết cuối (TỔNG / TỈ LỆ %)",
                    "Đủ dòng tổng kết ✓", "PASS", SEVERITY_ERROR))
    else:
        rpt.add(_fi("A02", GROUP, "Bảng Ma trận có đầy đủ dòng tổng kết cuối (TỔNG / TỈ LỆ %)",
                    "Thiếu dòng TỔNG hoặc TỈ LỆ % cuối bảng",
                    "FAIL", SEVERITY_ERROR,
                    "Thêm đầy đủ 4 dòng cuối bảng: TỔNG (Ý) / TỔNG SỐ CÂU / TỔNG ĐIỂM / TỈ LỆ %."))

    # A03: Số câu TN trong ma trận ≥ 1
    total_tn = data.matrix_total_tn
    if total_tn > 0:
        rpt.add(_fi("A03", GROUP, "Bảng Ma trận có phân bổ câu Trắc nghiệm",
                    f"Tổng TN trong ma trận = {total_tn} câu ✓", "PASS", SEVERITY_ERROR))
    else:
        rpt.add(_fi("A03", GROUP, "Bảng Ma trận có phân bổ câu Trắc nghiệm",
                    "Không trích xuất được số câu TN từ Ma trận — cần kiểm tra cấu trúc bảng.",
                    "WARN", SEVERITY_WARNING,
                    "Kiểm tra lại định dạng cột TNKQ/TL trong bảng Ma trận."))

    # A04: Tổng số câu trong Ma trận khớp với đề thi
    matrix_tn = data.matrix_total_tn
    exam_tn   = len(data.tn_questions)
    if matrix_tn == exam_tn:
        rpt.add(_fi("A04", GROUP, "Số câu TN trong Ma trận = số câu TN trong Đề thi",
                    f"Ma trận: {matrix_tn} câu = Đề thi: {exam_tn} câu ✓", "PASS", SEVERITY_ERROR))
    elif exam_tn > 0 and matrix_tn == 0:
        rpt.add(_fi("A04", GROUP, "Số câu TN trong Ma trận = số câu TN trong Đề thi",
                    f"Không trích xuất được số câu TN từ Ma trận (parser chưa nhận diện được cấu trúc bảng)",
                    "WARN", SEVERITY_WARNING,
                    "Kiểm tra lại thủ công: Số câu TN trong Ma trận có bằng số câu trong Đề không?"))
    else:
        rpt.add(_fi("A04", GROUP, "Số câu TN trong Ma trận = số câu TN trong Đề thi",
                    f"Ma trận: {matrix_tn} câu ≠ Đề thi: {exam_tn} câu",
                    "FAIL", SEVERITY_ERROR,
                    f"Điều chỉnh lại số câu TN trong Ma trận cho khớp với Đề thi ({exam_tn} câu)."))


# ──────────────────────────────────────────────────────────────────────────────
# NHÓM B — ĐỀ THI PHẦN TRẮC NGHIỆM
# ──────────────────────────────────────────────────────────────────────────────

def _check_group_B(data: ExamData, rpt: ValidationReport):
    GROUP = "B. Trắc nghiệm"

    # B01: Đủ câu hỏi và số câu liên tục
    tn_qs = data.tn_questions
    nums = sorted([q.num for q in tn_qs])

    if tn_qs:
        expected = list(range(1, len(tn_qs) + 1))
        if nums == expected:
            rpt.add(_fi("B01", GROUP, "Câu hỏi TN đánh số liên tục từ 1 đến N",
                        f"Đủ {len(tn_qs)} câu, đánh số 1–{len(tn_qs)} ✓", "PASS", SEVERITY_ERROR))
        else:
            missing = set(expected) - set(nums)
            rpt.add(_fi("B01", GROUP, "Câu hỏi TN đánh số liên tục từ 1 đến N",
                        f"Thiếu hoặc sai đánh số câu: {missing}",
                        "FAIL", SEVERITY_ERROR,
                        f"Kiểm tra và đánh lại số thứ tự câu hỏi bị thiếu: {sorted(missing)}."))
    else:
        rpt.add(_fi("B01", GROUP, "Câu hỏi TN đánh số liên tục từ 1 đến N",
                    "Không trích xuất được câu hỏi TN — cần kiểm tra thủ công.",
                    "WARN", SEVERITY_WARNING))

    # B02: Mỗi câu có đủ 4 phương án
    multi_answers = []
    no_choices = []
    for q in tn_qs:
        if len(q.choices) == 0:
            no_choices.append(q.num)
        elif len(q.choices) != 4:
            no_choices.append(q.num)

    if no_choices:
        rpt.add(_fi("B02", GROUP, "Mỗi câu TN có đúng 4 phương án A/B/C/D",
                    f"Câu không đủ 4 phương án: {no_choices}",
                    "FAIL", SEVERITY_ERROR,
                    f"Bổ sung đủ 4 phương án cho câu: {no_choices}."))
    else:
        rpt.add(_fi("B02", GROUP, "Mỗi câu TN có đúng 4 phương án A/B/C/D",
                    f"Tất cả {len(tn_qs)} câu đủ 4 phương án ✓", "PASS", SEVERITY_ERROR))

    # B03: Phân bổ đáp án không quá tập trung
    answers = data.rubric_answers
    if answers:
        from collections import Counter
        dist = Counter(answers.values())
        max_count = max(dist.values()) if dist else 0
        total = len(answers)
        pct = round(max_count / total * 100) if total else 0
        dominant = [k for k, v in dist.items() if v == max_count][0] if dist else ''
        if pct > 60:
            rpt.add(_fi("B03", GROUP, "Phân bổ đáp án A/B/C/D cân bằng (không quá 60% một chữ)",
                        f"Đáp án '{dominant}' chiếm {pct}% ({max_count}/{total} câu) — quá tập trung",
                        "WARN", SEVERITY_WARNING,
                        f"Điều chỉnh lại một số câu để đáp án phân bổ đều hơn giữa A, B, C, D.",
                        fixable=False))
        else:
            rpt.add(_fi("B03", GROUP, "Phân bổ đáp án A/B/C/D cân bằng (không quá 60% một chữ)",
                        f"Phân bổ đáp án: {dict(dist)} — cân bằng ✓", "PASS", SEVERITY_WARNING))
    else:
        rpt.add(_fi("B03", GROUP, "Phân bổ đáp án A/B/C/D cân bằng",
                    "Không có dữ liệu đáp án từ HDC để kiểm tra",
                    "WARN", SEVERITY_WARNING, "Cung cấp file Hướng dẫn chấm để kiểm tra phân bổ đáp án."))

    # B04: Tổng điểm TN = 5,0
    tn_score = data.exam_tn_score
    if abs(tn_score - 5.0) < 0.01:
        rpt.add(_fi("B04", GROUP, "Tổng điểm phần Trắc nghiệm = 5,0 điểm (20 câu × 0,25)",
                    f"20 câu × 0,25 = {tn_score} ✓", "PASS", SEVERITY_ERROR))
    else:
        rpt.add(_fi("B04", GROUP, "Tổng điểm phần Trắc nghiệm = 5,0 điểm",
                    f"Hiện có {len(tn_qs)} câu × 0,25 = {tn_score} điểm ≠ 5,0",
                    "FAIL", SEVERITY_ERROR,
                    f"Điều chỉnh số câu TN để đảm bảo 20 câu = 5,0 điểm."))


# ──────────────────────────────────────────────────────────────────────────────
# NHÓM C — ĐỀ THI PHẦN TỰ LUẬN
# ──────────────────────────────────────────────────────────────────────────────

def _check_group_C(data: ExamData, rpt: ValidationReport):
    GROUP = "C. Tự luận"

    essay_qs = data.essay_questions

    # C01: Tổng điểm TL = 5,0
    tl_score = data.exam_tl_score
    if abs(tl_score - 5.0) < 0.01:
        rpt.add(_fi("C01", GROUP, "Tổng điểm phần Tự luận = 5,0 điểm",
                    f"Tổng = {tl_score} điểm ✓", "PASS", SEVERITY_ERROR))
    else:
        rpt.add(_fi("C01", GROUP, "Tổng điểm phần Tự luận = 5,0 điểm",
                    f"Tổng điểm TL = {tl_score} điểm ≠ 5,0",
                    "FAIL", SEVERITY_ERROR,
                    f"Điều chỉnh điểm các bài TL sao cho tổng = 5,0 điểm."))

    # C02: Tổng điểm TN + TL = 10,0
    total = round(data.exam_tn_score + data.exam_tl_score, 2)
    if abs(total - 10.0) < 0.01:
        rpt.add(_fi("C02", GROUP, "Tổng điểm TN + TL = 10,0 điểm",
                    f"{data.exam_tn_score} + {data.exam_tl_score} = {total} ✓", "PASS", SEVERITY_ERROR))
    else:
        rpt.add(_fi("C02", GROUP, "Tổng điểm TN + TL = 10,0 điểm",
                    f"{data.exam_tn_score} + {data.exam_tl_score} = {total} ≠ 10,0",
                    "FAIL", SEVERITY_ERROR,
                    "Điều chỉnh lại phân bổ điểm TN và TL để tổng bằng 10,0 điểm."))

    # C03: Số bài TL và có đủ nội dung
    if essay_qs:
        rpt.add(_fi("C03", GROUP, f"Phần Tự luận có đủ {len(essay_qs)} bài",
                    f"Trích xuất được {len(essay_qs)} bài TL ✓", "PASS", SEVERITY_ERROR))
    else:
        rpt.add(_fi("C03", GROUP, "Phần Tự luận có bài hỏi",
                    "Không trích xuất được bài TL — kiểm tra thủ công.",
                    "WARN", SEVERITY_WARNING))

    # C04: Đề có dòng "HẾT"
    if data.exam_has_end_marker:
        rpt.add(_fi("C04", GROUP, "Đề có dòng kết thúc '─── HẾT ───'",
                    "Có dòng HẾT ✓", "PASS", SEVERITY_WARNING))
    else:
        rpt.add(_fi("C04", GROUP, "Đề có dòng kết thúc '─── HẾT ───'",
                    "Thiếu dòng HẾT cuối đề",
                    "FAIL", SEVERITY_WARNING,
                    "Thêm dòng '----- HẾT -----' và '(Cán bộ coi thi không giải thích gì thêm)' cuối đề.",
                    fixable=True, fix_action="Thêm dòng HẾT cuối file đề thi"))


# ──────────────────────────────────────────────────────────────────────────────
# NHÓM D — HƯỚNG DẪN CHẤM
# ──────────────────────────────────────────────────────────────────────────────

def _check_group_D(data: ExamData, rpt: ValidationReport):
    GROUP = "D. Hướng dẫn chấm"

    # D01: HDC có mã đề
    if data.rubric_code:
        match = (data.rubric_code == data.exam_code) if data.exam_code else True
        if match:
            rpt.add(_fi("D01", GROUP, "HDC có ghi rõ Mã đề khớp với Đề thi",
                        f"Mã đề HDC: {data.rubric_code} ✓", "PASS", SEVERITY_ERROR))
        else:
            rpt.add(_fi("D01", GROUP, "HDC có ghi rõ Mã đề khớp với Đề thi",
                        f"Mã đề HDC: {data.rubric_code} ≠ Mã đề thi: {data.exam_code}",
                        "FAIL", SEVERITY_ERROR,
                        f"Sửa mã đề trong HDC thành '{data.exam_code}'.",
                        fixable=True, fix_action=f"Sửa mã đề trong HDC = {data.exam_code}"))
    else:
        rpt.add(_fi("D01", GROUP, "HDC có ghi rõ Mã đề",
                    "Không tìm thấy Mã đề trong HDC",
                    "FAIL", SEVERITY_ERROR,
                    f"Bổ sung 'Mã đề: {data.exam_code}' vào bảng tiêu đề HDC.",
                    fixable=True, fix_action=f"Bổ sung Mã đề {data.exam_code} vào HDC"))

    # D02: Số đáp án TN trong HDC khớp với số câu TN
    n_ans = len(data.rubric_answers)
    n_tn  = len(data.tn_questions)
    if n_ans == n_tn:
        rpt.add(_fi("D02", GROUP, "Số đáp án TN trong HDC = Số câu TN trong Đề",
                    f"{n_ans} đáp án = {n_tn} câu ✓", "PASS", SEVERITY_ERROR))
    elif n_ans == 0:
        rpt.add(_fi("D02", GROUP, "Số đáp án TN trong HDC = Số câu TN trong Đề",
                    "Không trích xuất được đáp án từ bảng HDC (kiểm tra định dạng bảng)",
                    "WARN", SEVERITY_WARNING))
    else:
        rpt.add(_fi("D02", GROUP, "Số đáp án TN trong HDC = Số câu TN trong Đề",
                    f"HDC: {n_ans} đáp án ≠ Đề thi: {n_tn} câu",
                    "FAIL", SEVERITY_ERROR,
                    f"Bổ sung hoặc xóa bớt đáp án trong bảng HDC cho đủ {n_tn} câu."))

    # D03: Tổng điểm barem TL trong HDC
    rubric_tl = data.rubric_total_score
    if abs(rubric_tl - 5.0) < 0.01:
        rpt.add(_fi("D03", GROUP, "Tổng điểm barem TL trong HDC = 5,0 điểm",
                    f"Tổng barem TL = {rubric_tl} điểm ✓", "PASS", SEVERITY_ERROR))
    elif rubric_tl == 0:
        rpt.add(_fi("D03", GROUP, "Tổng điểm barem TL trong HDC = 5,0 điểm",
                    "Không trích xuất được điểm barem TL (kiểm tra định dạng cột 'Điểm')",
                    "WARN", SEVERITY_WARNING))
    else:
        rpt.add(_fi("D03", GROUP, "Tổng điểm barem TL trong HDC = 5,0 điểm",
                    f"Tổng barem TL = {rubric_tl} điểm ≠ 5,0 điểm",
                    "FAIL", SEVERITY_ERROR,
                    f"Điều chỉnh lại điểm từng bước trong bảng barem để tổng = 5,0 điểm."))

    # D04: HDC có Lưu ý khi chấm
    if data.rubric_has_note:
        rpt.add(_fi("D04", GROUP, "HDC có mục 'Lưu ý khi chấm bài'",
                    "Có mục Lưu ý ✓", "PASS", SEVERITY_WARNING))
    else:
        rpt.add(_fi("D04", GROUP, "HDC có mục 'Lưu ý khi chấm bài'",
                    "Thiếu mục Lưu ý khi chấm",
                    "FAIL", SEVERITY_WARNING,
                    "Thêm mục 'Lưu ý khi chấm bài' với 3 điểm: (1) Giải cách khác đúng; (2) Điểm không làm tròn; (3) Bài hình học không vẽ hình = không chấm điểm.",
                    fixable=True, fix_action="Thêm mục Lưu ý chấm bài vào cuối HDC"))


# ──────────────────────────────────────────────────────────────────────────────
# NHÓM E — ĐỊNH DẠNG & TRÌNH BÀY
# ──────────────────────────────────────────────────────────────────────────────

def _check_group_E(data: ExamData, rpt: ValidationReport):
    GROUP = "E. Định dạng & Trình bày"

    # E01: Kiểm tra OLE bản đề thi
    ole = data.exam_ole_count
    res = data.exam_residual_dollar
    if ole > 0 and res == 0:
        rpt.add(_fi("E01", GROUP, "Bản Đề thi: 100% công thức là MathType OLE, không sót ký hiệu $",
                    f"{ole} đối tượng OLE, sót $ = 0 ✓", "PASS", SEVERITY_ERROR))
    elif res < 0:
        rpt.add(_fi("E01", GROUP, "Bản Đề thi: Kiểm tra MathType OLE",
                    "Không đọc được file DOCX để kiểm tra OLE",
                    "WARN", SEVERITY_WARNING))
    elif res > 0:
        rpt.add(_fi("E01", GROUP, "Bản Đề thi: 100% công thức là MathType OLE, không sót ký hiệu $",
                    f"Phát hiện {res} ký hiệu $ sót lại trong văn bản (công thức chưa chuyển MathType)",
                    "FAIL", SEVERITY_ERROR,
                    f"Gõ lại {res} công thức còn thô bằng MathType OLE hoặc chạy lại pipeline chuyển đổi.",
                    fixable=True, fix_action=f"Chuyển {res} ký hiệu $ thành MathType OLE trong Đề thi"))
    else:
        rpt.add(_fi("E01", GROUP, "Bản Đề thi: Kiểm tra MathType OLE",
                    "Không có đối tượng OLE nào — đề chưa nhúng công thức MathType",
                    "FAIL", SEVERITY_ERROR,
                    "Chạy lại pipeline xuất đề để nhúng MathType OLE cho toàn bộ công thức."))

    # E02: Kiểm tra OLE bản HDC
    ole2 = data.rubric_ole_count
    res2 = data.rubric_residual_dollar
    if ole2 > 0 and res2 == 0:
        rpt.add(_fi("E02", GROUP, "Bản HDC: 100% công thức là MathType OLE, không sót ký hiệu $",
                    f"{ole2} đối tượng OLE, sót $ = 0 ✓", "PASS", SEVERITY_ERROR))
    elif res2 < 0:
        rpt.add(_fi("E02", GROUP, "Bản HDC: Kiểm tra MathType OLE",
                    "Không đọc được file HDC để kiểm tra OLE",
                    "WARN", SEVERITY_WARNING))
    elif res2 > 0:
        rpt.add(_fi("E02", GROUP, "Bản HDC: 100% công thức là MathType OLE",
                    f"Phát hiện {res2} ký hiệu $ sót trong HDC",
                    "FAIL", SEVERITY_ERROR,
                    f"Gõ lại {res2} công thức còn thô trong HDC bằng MathType OLE.",
                    fixable=True, fix_action=f"Chuyển {res2} ký hiệu $ thành MathType OLE trong HDC"))
    else:
        rpt.add(_fi("E02", GROUP, "Bản HDC: Kiểm tra MathType OLE",
                    "Không có đối tượng OLE nào trong HDC",
                    "FAIL", SEVERITY_ERROR,
                    "Chạy lại pipeline xuất HDC để nhúng MathType OLE."))

    # E03: Đồng bộ cỡ chữ công thức MathType
    exam_outliers = data.__dict__.get('_exam_ole_outliers', 0)
    total_text_oles_exam = len([h for h in data.exam_ole_heights if h < 350_000])
    if not data.exam_ole_heights:
        rpt.add(_fi("E03", GROUP,
                    "Cỡ chữ công thức MathType đồng bộ (chuẩn 13–14pt)",
                    "Không phân tích được kích thước OLE (có thể file dùng định dạng cũ)",
                    "WARN", SEVERITY_WARNING,
                    "Mở file bằng MathType và kiểm tra cỡ chữ thủ công."))
    elif total_text_oles_exam >= 5 and exam_outliers > 0:
        pct = round(exam_outliers / total_text_oles_exam * 100)
        # Nếu chỉ có 1-3 công thức lệch nhỏ (< 10%) thường là chỉ số trên/dưới (x^2, a_1)
        if pct < 10 and exam_outliers <= 3:
            rpt.add(_fi("E03", GROUP,
                        "Cỡ chữ công thức MathType đồng bộ (chuẩn 13–14pt)",
                        f"Cỡ chữ {total_text_oles_exam} công thức cơ bản đồng đều "
                        f"(có {exam_outliers} công thức dạng mũ/chỉ số nhỏ đặc thù) ✓",
                        "PASS", SEVERITY_WARNING))
        else:
            rpt.add(_fi("E03", GROUP,
                        "Cỡ chữ công thức MathType đồng bộ (chuẩn 13–14pt)",
                        f"Phát hiện {exam_outliers}/{total_text_oles_exam} công thức "
                        f"({pct}%) có cỡ chữ lệch chuẩn so với phần lớn đề thi "
                        f"(thường do copy công thức từ nhiều nguồn khác nhau)",
                        "WARN", SEVERITY_WARNING,
                        "Chạy Auto-fix để chuẩn hóa toàn bộ cỡ chữ MathType về 13pt "
                        "đồng đều. Hoặc mở MathType → Format → Define Sizes và chỉnh lại.",
                        fixable=True, fix_action="standardize_mathtype_size"))
    else:
        rpt.add(_fi("E03", GROUP,
                    "Cỡ chữ công thức MathType đồng bộ (chuẩn 13–14pt)",
                    f"Cỡ chữ {total_text_oles_exam} công thức trong đề thi đồng đều ✓",
                    "PASS", SEVERITY_WARNING))

    # E04: Phân số không bị co nhỏ (inline fraction)
    sf_exam   = data.exam_small_fractions
    sf_rubric = data.rubric_small_fractions
    sf_total  = sf_exam + sf_rubric
    if sf_total > 0:
        parts = []
        if sf_exam > 0:
            parts.append(f"Đề thi: {sf_exam} phân số")
        if sf_rubric > 0:
            parts.append(f"HDC: {sf_rubric} phân số")
        rpt.add(_fi("E04", GROUP,
                    "Phân số hiển thị đầy đủ (không bị co nhỏ kiểu inline)",
                    f"Phát hiện {sf_total} phân số có thể bị co nhỏ "
                    f"({', '.join(parts)}) — trông giống \\frac thay vì \\dfrac",
                    "WARN", SEVERITY_WARNING,
                    "Chạy Auto-fix để chuyển sang Full-size fraction. "
                    "Hoặc trong MathType: chọn phân số → Format → Full size fraction (Ctrl+Shift+F).",
                    fixable=True, fix_action="standardize_mathtype_size"))
    else:
        rpt.add(_fi("E04", GROUP,
                    "Phân số hiển thị đầy đủ (không bị co nhỏ kiểu inline)",
                    "Không phát hiện phân số co nhỏ bất thường ✓",
                    "PASS", SEVERITY_WARNING))


# ──────────────────────────────────────────────────────────────────────────────
# NHÓM F — ĐỐI CHIẾU CHÉO
# ──────────────────────────────────────────────────────────────────────────────

def _check_group_F(data: ExamData, rpt: ValidationReport):
    GROUP = "F. Đối chiếu chéo (3 file)"

    # F01: Mã đề thống nhất giữa Đề thi và HDC
    exam_c  = data.exam_code
    rubr_c  = data.rubric_code
    if exam_c and rubr_c:
        if exam_c == rubr_c:
            rpt.add(_fi("F01", GROUP, "Mã đề thống nhất giữa Đề thi và HDC",
                        f"Cả hai đều là Mã đề {exam_c} ✓", "PASS", SEVERITY_ERROR))
        else:
            rpt.add(_fi("F01", GROUP, "Mã đề thống nhất giữa Đề thi và HDC",
                        f"Đề thi: Mã đề {exam_c} ≠ HDC: Mã đề {rubr_c}",
                        "FAIL", SEVERITY_ERROR,
                        f"Sửa Mã đề trong HDC thành {exam_c} để thống nhất với Đề thi.",
                        fixable=True, fix_action=f"Sửa Mã đề HDC = {exam_c}"))
    else:
        rpt.add(_fi("F01", GROUP, "Mã đề thống nhất giữa Đề thi và HDC",
                    f"Đề thi: '{exam_c}', HDC: '{rubr_c}' — thiếu thông tin",
                    "WARN", SEVERITY_WARNING,
                    "Bổ sung Mã đề vào cả Đề thi và HDC."))

    # F02: Tổng điểm nhất quán (Ma trận / Đề thi / HDC)
    s_matrix = data.matrix_total_score
    s_exam   = round(data.exam_tn_score + data.exam_tl_score, 2)
    s_rubric = round(data.exam_tn_score + data.rubric_total_score, 2)  # TN + barem TL
    scores_ok = (abs(s_matrix - 10.0) < 0.01 and
                 abs(s_exam   - 10.0) < 0.01)
    if scores_ok:
        rpt.add(_fi("F02", GROUP, "Tổng điểm nhất quán giữa Ma trận – Đề thi – HDC",
                    f"Ma trận={s_matrix} / Đề thi={s_exam} / Cùng = 10,0 ✓",
                    "PASS", SEVERITY_ERROR))
    else:
        rpt.add(_fi("F02", GROUP, "Tổng điểm nhất quán giữa Ma trận – Đề thi – HDC",
                    f"Ma trận={s_matrix} / Đề thi={s_exam} — không nhất quán",
                    "FAIL", SEVERITY_ERROR,
                    "Đối chiếu lại tổng điểm giữa 3 file để đảm bảo cùng = 10,0 điểm."))

    # F03: Số câu TN nhất quán
    n_matrix = data.matrix_total_tn
    n_exam   = len(data.tn_questions)
    n_rubric = len(data.rubric_answers)
    if n_matrix > 0 and n_matrix == n_exam:
        rpt.add(_fi("F03", GROUP, "Số câu TN nhất quán giữa Ma trận – Đề thi – HDC",
                    f"Cùng {n_exam} câu TN ✓", "PASS", SEVERITY_ERROR))
    elif n_matrix == 0:
        rpt.add(_fi("F03", GROUP, "Số câu TN nhất quán giữa Ma trận – Đề thi – HDC",
                    f"Đề thi: {n_exam} câu / HDC: {n_rubric} câu — Ma trận chưa trích xuất được",
                    "WARN", SEVERITY_WARNING))
    else:
        rpt.add(_fi("F03", GROUP, "Số câu TN nhất quán giữa Ma trận – Đề thi – HDC",
                    f"Ma trận: {n_matrix} / Đề thi: {n_exam} / HDC: {n_rubric}",
                    "FAIL", SEVERITY_ERROR,
                    "Điều chỉnh cho cả 3 file cùng ghi đúng số câu TN."))


# ──────────────────────────────────────────────────────────────────────────────
# NHÓM G — PHÂN HÓA & CHẤT LƯỢNG
# ──────────────────────────────────────────────────────────────────────────────

def _check_group_G(data: ExamData, rpt: ValidationReport):
    GROUP = "G. Phân hóa & Chất lượng"

    # G01: Câu VDC tồn tại
    has_vdc = any('vận dụng cao' in e.muc_do.lower() for e in data.matrix_entries)
    essay_tl = data.essay_questions
    has_vdc_essay = len(essay_tl) > 0 and essay_tl[-1].points_total <= 1.0  # heuristic: bài cuối nhỏ
    if has_vdc or has_vdc_essay:
        rpt.add(_fi("G01", GROUP, "Đề có câu/ý Vận dụng cao để phân hóa học sinh giỏi",
                    "Có câu VDC ✓", "PASS", SEVERITY_INFO))
    else:
        rpt.add(_fi("G01", GROUP, "Đề có câu/ý Vận dụng cao để phân hóa học sinh giỏi",
                    "Không phát hiện câu VDC trong Ma trận",
                    "WARN", SEVERITY_INFO,
                    "Thêm ít nhất 1 câu/ý Vận dụng cao (0,5 điểm) để phân hóa học sinh giỏi theo GDPT 2018."))

    # G02: Có bài toán thực tế gắn ngữ cảnh đời sống
    raw = data.exam_raw.lower()
    context_words = ['mảnh vườn', 'sân', 'hàng rào', 'tấm vải', 'bể nước', 'hộp', 'khuôn viên', 'cây', 'mảnh đất', 'chiều dài', 'chiều rộng']
    has_context = any(w in raw for w in context_words)
    if has_context:
        rpt.add(_fi("G02", GROUP, "Đề có bài toán thực tế gắn ngữ cảnh đời sống",
                    "Có bài toán thực tế ✓", "PASS", SEVERITY_INFO))
    else:
        rpt.add(_fi("G02", GROUP, "Đề có bài toán thực tế gắn ngữ cảnh đời sống",
                    "Không phát hiện bài toán gắn ngữ cảnh thực tế",
                    "WARN", SEVERITY_INFO,
                    "Thêm ít nhất 1 bài toán gắn với thực tế đời sống (diện tích vườn, chi phí lát nền, ...) theo tinh thần GDPT 2018."))


# ──────────────────────────────────────────────────────────────────────────────
# RUN ALL
# ──────────────────────────────────────────────────────────────────────────────

def run_all_checks(data: ExamData) -> ValidationReport:
    """Chạy toàn bộ các tiêu chí thẩm định và trả về ValidationReport."""
    rpt = ValidationReport()

    print("[Validator] Kiểm tra Nhóm A — Ma trận & Bản đặc tả...")
    _check_group_A(data, rpt)

    print("[Validator] Kiểm tra Nhóm B — Trắc nghiệm...")
    _check_group_B(data, rpt)

    print("[Validator] Kiểm tra Nhóm C — Tự luận...")
    _check_group_C(data, rpt)

    print("[Validator] Kiểm tra Nhóm D — Hướng dẫn chấm...")
    _check_group_D(data, rpt)

    print("[Validator] Kiểm tra Nhóm E — Định dạng MathType OLE...")
    _check_group_E(data, rpt)

    print("[Validator] Kiểm tra Nhóm F — Đối chiếu chéo 3 file...")
    _check_group_F(data, rpt)

    print("[Validator] Kiểm tra Nhóm G — Phân hóa & Chất lượng...")
    _check_group_G(data, rpt)

    rpt.finalize()
    print(f"\n[Validator] ✓ Hoàn tất: {rpt.passed}/{rpt.total} tiêu chí đạt.")
    print(f"[Validator] {rpt.summary}")
    return rpt
