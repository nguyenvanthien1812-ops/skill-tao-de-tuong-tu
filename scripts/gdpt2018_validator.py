"""
gdpt2018_validator.py — Trình Kiểm Định Chuẩn GDPT 2018
==========================================================
Tự động kiểm tra đề thi vừa tạo có đáp ứng chuẩn GDPT 2018 không.
Hỗ trợ 8 môn: Toán, Vật Lý, Hóa Học, Sinh Học, KHTN, Địa Lý, KTPL, Văn Học.
Lớp 6–12.

Sử dụng:
    from scripts.gdpt2018_validator import validate_exam_gdpt2018, print_validation_report

    result = validate_exam_gdpt2018(exam_data, subject="math", level="thpt")
    print_validation_report(result)
"""

from __future__ import annotations
import sys
import json
from dataclasses import dataclass, field
from typing import Optional

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

# ─────────────────────────────────────────────────────────────────────
# Cấu hình chuẩn GDPT 2018 theo môn và cấp học
# ─────────────────────────────────────────────────────────────────────

GDPT2018_CONFIG = {
    # Môn THPT (10–12)
    "math": {
        "thpt": {
            "part1_mc": {"count": 12, "points": 0.25, "desc": "Trắc nghiệm nhiều phương án"},
            "part2_tf": {"count": 4,  "points": 1.0,  "desc": "Đúng / Sai (4 ý a,b,c,d)"},
            "part3_sa": {"count": 6,  "points": 0.5,  "desc": "Trả lời ngắn"},
            "total_points": 10.0,
            "support_essay": True,   # Đề kiểm tra học kỳ có tự luận
            "nbtd_ratio": (30, 40, 20, 10),  # NB:TH:VD:VDC
        },
        "thcs": {
            "part1_mc": {"count": 12, "points": 0.25, "desc": "Trắc nghiệm nhiều phương án"},
            "part2_tf": {"count": 2,  "points": 1.0,  "desc": "Đúng / Sai"},
            "part3_sa": {"count": 4,  "points": 0.5,  "desc": "Trả lời ngắn / Tự luận ngắn"},
            "total_points": 10.0,
            "support_essay": True,
            "nbtd_ratio": (35, 40, 15, 10),
        },
    },
    "physics": {
        "thpt": {
            "part1_mc": {"count": 12, "points": 0.25},
            "part2_tf": {"count": 4,  "points": 1.0},
            "part3_sa": {"count": 6,  "points": 0.5},
            "total_points": 10.0,
            "support_essay": True,
            "nbtd_ratio": (30, 40, 20, 10),
            "requires_unit_si": True,       # Bắt buộc ghi đơn vị SI
            "requires_error_analysis": True, # Câu thực nghiệm phải có phân tích sai số
        },
    },
    "chemistry": {
        "thpt": {
            "part1_mc": {"count": 12, "points": 0.25},
            "part2_tf": {"count": 4,  "points": 1.0},
            "part3_sa": {"count": 6,  "points": 0.5},
            "total_points": 10.0,
            "support_essay": True,
            "nbtd_ratio": (30, 40, 20, 10),
            "requires_iupac_font": True,    # Bắt buộc font IUPAC \mathrm{}
            "requires_conservation": True,  # Phải có sơ đồ bảo toàn
        },
    },
    "biology": {
        "thpt": {
            "part1_mc": {"count": 12, "points": 0.25},
            "part2_tf": {"count": 4,  "points": 1.0},
            "part3_sa": {"count": 6,  "points": 0.5},
            "total_points": 10.0,
            "support_essay": True,
            "nbtd_ratio": (30, 40, 20, 10),
        },
    },
    "khtn": {
        "thcs": {
            "part1_mc": {"count": 16, "points": 0.25},
            "part2_tf": {"count": 2,  "points": 1.0},
            "part3_sa": {"count": 4,  "points": 0.5},
            "total_points": 10.0,
            "support_essay": True,
            "nbtd_ratio": (35, 40, 15, 10),
            "requires_integration": True,  # Phải có câu tích hợp liên môn
        },
    },
    "geography": {
        "thpt": {
            "part1_mc": {"count": 8,  "points": 0.25},
            "part2_tf": {"count": 2,  "points": 1.0},
            "part3_sa": {"count": 0,  "points": 0.0},
            "essay":    {"count": 3,  "desc": "Bản đồ, biểu đồ, giải thích hiện tượng địa lý"},
            "total_points": 10.0,
            "support_essay": True,
            "nbtd_ratio": (25, 35, 25, 15),
        },
    },
    "economics_law": {
        "thpt": {
            "part1_mc": {"count": 8,  "points": 0.25},
            "part2_tf": {"count": 2,  "points": 1.0},
            "part3_sa": {"count": 0,  "points": 0.0},
            "essay":    {"count": 2,  "desc": "Tình huống pháp luật / Phân tích kinh tế"},
            "total_points": 10.0,
            "support_essay": True,
            "nbtd_ratio": (25, 35, 25, 15),
        },
    },
    "literature": {
        "thpt": {
            "part1_reading": {"count": 1, "desc": "Đọc hiểu văn bản (4–6 câu hỏi)"},
            "part2_writing": {"count": 2, "desc": "Nghị luận xã hội + Nghị luận văn học"},
            "total_points": 10.0,
            "support_essay": True,
            "nbtd_ratio": (20, 30, 30, 20),
            "no_mc": True,   # Văn không có trắc nghiệm A/B/C/D
        },
    },
}

# Ánh xạ tên môn viết tắt/tên đầy đủ/tiếng Anh
SUBJECT_ALIASES = {
    # Toán
    "toan": "math", "toán": "math", "math": "math", "mathematics": "math",
    # Vật lý
    "ly": "physics", "lý": "physics", "vatly": "physics", "vật lý": "physics", "physics": "physics",
    # Hóa học
    "hoa": "chemistry", "hóa": "chemistry", "hoahoc": "chemistry",
    "hóa học": "chemistry", "chemistry": "chemistry",
    # Sinh học
    "sinh": "biology", "sinhhoc": "biology", "sinh học": "biology", "biology": "biology",
    # KHTN
    "khtn": "khtn", "khoahoctunhien": "khtn",
    "khoa học tự nhiên": "khtn", "natural science": "khtn",
    # Địa lý
    "dia": "geography", "địa": "geography", "dialy": "geography",
    "địa lý": "geography", "geography": "geography",
    # KTPL
    "ktpl": "economics_law", "kinh te phap luat": "economics_law",
    "kinh tế pháp luật": "economics_law", "economics": "economics_law",
    # Văn học
    "van": "literature", "văn": "literature", "nguvan": "literature",
    "ngữ văn": "literature", "literature": "literature", "vietnamese": "literature",
}

# ─────────────────────────────────────────────────────────────────────
# Data classes
# ─────────────────────────────────────────────────────────────────────

@dataclass
class ValidationIssue:
    """Một lỗi hoặc cảnh báo trong quá trình kiểm định."""
    severity: str      # "error" | "warning" | "info"
    code: str          # Mã lỗi dạng GDPT-XXX
    message: str       # Mô tả lỗi bằng tiếng Việt
    location: str = ""  # Vị trí lỗi ("Phần II, Câu 3, ý d")
    suggestion: str = ""  # Gợi ý sửa


@dataclass
class ValidationResult:
    """Kết quả kiểm định tổng hợp."""
    valid: bool
    subject: str
    level: str
    total_questions: int
    issues: list[ValidationIssue] = field(default_factory=list)
    scores: dict = field(default_factory=dict)         # Điểm từng phần
    nbtd_actual: dict = field(default_factory=dict)    # Tỉ lệ NB/TH/VD/VDC thực tế
    nbtd_expected: dict = field(default_factory=dict)  # Tỉ lệ NB/TH/VD/VDC chuẩn
    summary: str = ""  # Tóm tắt kết quả
    stats: dict = field(default_factory=dict)          # Thống kê bổ sung


# ─────────────────────────────────────────────────────────────────────
# Hàm kiểm định chính
# ─────────────────────────────────────────────────────────────────────

def resolve_subject(subject_input: str) -> str:
    """Chuyển đổi tên môn học sang mã chuẩn nội bộ."""
    key = subject_input.lower().strip()
    return SUBJECT_ALIASES.get(key, key)


def validate_exam_gdpt2018(
    exam_data: dict,
    subject: str = "math",
    level: str = "thpt",
) -> ValidationResult:
    """
    Kiểm định đề thi theo chuẩn GDPT 2018.

    Parameters
    ----------
    exam_data : dict
        Dữ liệu đề thi với cấu trúc:
        {
            "title": str,
            "subject": str,
            "grade": int,            # Lớp (6–12)
            "part1_mc": [            # Phần I: Trắc nghiệm A/B/C/D
                {
                    "id": int,
                    "question": str,
                    "options": ["A...", "B...", "C...", "D..."],
                    "answer": str,    # "A" | "B" | "C" | "D"
                    "level": str,     # "NB" | "TH" | "VD" | "VDC"
                    "has_context": bool,  # Có ngữ cảnh thực tiễn?
                }, ...
            ],
            "part2_tf": [            # Phần II: Đúng/Sai
                {
                    "id": int,
                    "stem": str,      # Đoạn dẫn
                    "items": [
                        {"label": "a", "statement": str, "answer": bool, "level": str},
                        {"label": "b", "statement": str, "answer": bool, "level": str},
                        {"label": "c", "statement": str, "answer": bool, "level": str},
                        {"label": "d", "statement": str, "answer": bool, "level": str},
                    ],
                    "has_context": bool,
                }, ...
            ],
            "part3_sa": [            # Phần III: Trả lời ngắn
                {
                    "id": int,
                    "question": str,
                    "answer": str | float | int,
                    "level": str,
                    "has_context": bool,
                }, ...
            ],
            "essay": [               # Tự luận (nếu có)
                {
                    "id": int,
                    "question": str,
                    "solution": str,
                    "points": float,
                    "has_real_world_conclusion": bool,  # Có bước phiên giải thực tiễn?
                }, ...
            ],
        }
    subject : str
        Tên môn học (Toán / Vật Lý / Hóa Học / ...).
    level : str
        Cấp học: "thpt" (10–12) hoặc "thcs" (6–9).

    Returns
    -------
    ValidationResult
    """
    subject_key = resolve_subject(subject)
    issues: list[ValidationIssue] = []
    scores: dict = {}

    # Lấy cấu hình chuẩn
    subject_cfg = GDPT2018_CONFIG.get(subject_key, {})
    level_cfg = subject_cfg.get(level, {})
    if not level_cfg:
        issues.append(ValidationIssue(
            severity="warning",
            code="GDPT-000",
            message=f"Chưa có cấu hình chuẩn GDPT 2018 cho môn '{subject}' cấp '{level}'. Kiểm định cơ bản.",
        ))

    # ── 1. Kiểm tra cấu trúc 3 phần ──────────────────────────────────
    _check_structure(exam_data, level_cfg, subject_key, issues, scores)

    # ── 2. Kiểm tra tỉ lệ NB/TH/VD/VDC ─────────────────────────────
    nbtd_actual, nbtd_expected = _check_nbtd_ratio(exam_data, level_cfg, issues)

    # ── 3. Kiểm tra câu Đúng/Sai ────────────────────────────────────
    _check_true_false_questions(exam_data, issues)

    # ── 4. Kiểm tra câu trả lời ngắn ────────────────────────────────
    _check_short_answer(exam_data, issues)

    # ── 5. Kiểm tra ngữ cảnh thực tiễn ──────────────────────────────
    _check_real_world_context(exam_data, issues)

    # ── 6. Kiểm tra phần tự luận ─────────────────────────────────────
    _check_essay(exam_data, subject_key, issues)

    # ── 7. Kiểm tra đặc thù theo môn ────────────────────────────────
    _check_subject_specific(exam_data, subject_key, level_cfg, issues)

    # ── 7bis. Kiểm định phương pháp giải chuẩn GDPT 2018 ───────────
    _check_solution_methodology(exam_data, subject_key, issues)

    # ── 8. Tổng kết ──────────────────────────────────────────────────
    error_count   = sum(1 for i in issues if i.severity == "error")
    warning_count = sum(1 for i in issues if i.severity == "warning")
    total_questions = (
        len(exam_data.get("part1_mc", []))
        + len(exam_data.get("part2_tf", []))
        + len(exam_data.get("part3_sa", []))
        + len(exam_data.get("essay", []))
    )

    valid = error_count == 0
    summary_parts = []
    if valid:
        summary_parts.append("✅ Đề thi đạt chuẩn GDPT 2018")
    else:
        summary_parts.append(f"❌ Đề thi CÓ {error_count} LỖI cần sửa")
    if warning_count:
        summary_parts.append(f"⚠️ {warning_count} cảnh báo cần chú ý")

    return ValidationResult(
        valid=valid,
        subject=subject_key,
        level=level,
        total_questions=total_questions,
        issues=issues,
        scores=scores,
        nbtd_actual=nbtd_actual,
        nbtd_expected=nbtd_expected,
        summary=" — ".join(summary_parts),
        stats={
            "error_count": error_count,
            "warning_count": warning_count,
            "part1_count": len(exam_data.get("part1_mc", [])),
            "part2_count": len(exam_data.get("part2_tf", [])),
            "part3_count": len(exam_data.get("part3_sa", [])),
            "essay_count": len(exam_data.get("essay", [])),
        },
    )


# ─────────────────────────────────────────────────────────────────────
# Các hàm kiểm tra con (helper functions)
# ─────────────────────────────────────────────────────────────────────

def _check_structure(
    exam_data: dict,
    level_cfg: dict,
    subject_key: str,
    issues: list,
    scores: dict,
) -> None:
    """Kiểm tra cấu trúc tổng quát của đề thi."""

    # Môn Văn không có trắc nghiệm
    if level_cfg.get("no_mc"):
        if "part1_mc" in exam_data and len(exam_data["part1_mc"]) > 0:
            issues.append(ValidationIssue(
                severity="error",
                code="GDPT-101",
                message="Môn Ngữ Văn không có phần Trắc nghiệm A/B/C/D theo GDPT 2018.",
                suggestion="Xóa phần 'part1_mc' và chỉ giữ phần Đọc hiểu + Viết.",
            ))
        return

    # Phần I: Trắc nghiệm nhiều phương án
    p1 = exam_data.get("part1_mc", [])
    expected_p1 = level_cfg.get("part1_mc", {}).get("count", 12)
    if not p1:
        issues.append(ValidationIssue(
            severity="error", code="GDPT-101",
            message=f"Thiếu Phần I (Trắc nghiệm nhiều phương án). Cần {expected_p1} câu.",
            suggestion="Bổ sung key 'part1_mc' vào exam_data.",
        ))
    elif len(p1) != expected_p1:
        issues.append(ValidationIssue(
            severity="error", code="GDPT-102",
            message=f"Phần I có {len(p1)} câu, chuẩn GDPT 2018 cần đúng {expected_p1} câu.",
            suggestion=f"Thêm hoặc bỏ bớt để đủ {expected_p1} câu.",
        ))
    else:
        pt = expected_p1 * level_cfg.get("part1_mc", {}).get("points", 0.25)
        scores["part1"] = pt

    # Phần II: Đúng/Sai
    p2 = exam_data.get("part2_tf", [])
    expected_p2 = level_cfg.get("part2_tf", {}).get("count", 4)
    if not p2:
        issues.append(ValidationIssue(
            severity="error", code="GDPT-111",
            message=f"Thiếu Phần II (Đúng/Sai). Cần {expected_p2} câu theo chuẩn GDPT 2018.",
            suggestion="Đây là dạng câu HOÀN TOÀN MỚI — bắt buộc có.",
        ))
    elif len(p2) != expected_p2:
        issues.append(ValidationIssue(
            severity="warning", code="GDPT-112",
            message=f"Phần II có {len(p2)} câu Đúng/Sai, chuẩn GDPT 2018 khuyến nghị {expected_p2} câu.",
        ))
    else:
        pt = expected_p2 * level_cfg.get("part2_tf", {}).get("points", 1.0)
        scores["part2"] = pt

    # Phần III: Trả lời ngắn
    p3 = exam_data.get("part3_sa", [])
    expected_p3 = level_cfg.get("part3_sa", {}).get("count", 6)
    if not p3 and expected_p3 > 0:
        issues.append(ValidationIssue(
            severity="error", code="GDPT-121",
            message=f"Thiếu Phần III (Trả lời ngắn). Cần {expected_p3} câu.",
        ))
    elif p3 and len(p3) != expected_p3:
        issues.append(ValidationIssue(
            severity="warning", code="GDPT-122",
            message=f"Phần III có {len(p3)} câu, chuẩn GDPT 2018 khuyến nghị {expected_p3} câu.",
        ))
    else:
        pt = (len(p3) if p3 else 0) * level_cfg.get("part3_sa", {}).get("points", 0.5)
        scores["part3"] = pt

    # Kiểm tra tổng điểm
    total = sum(scores.values())
    if abs(total - 10.0) > 0.01 and level_cfg.get("total_points", 10.0) == 10.0:
        scores["total"] = total
        issues.append(ValidationIssue(
            severity="warning", code="GDPT-130",
            message=f"Tổng điểm 3 phần trắc nghiệm = {total:.2f}đ (kỳ vọng = 10,0đ).",
            suggestion="Kiểm tra lại số câu hoặc thang điểm từng phần.",
        ))
    else:
        scores["total"] = total


def _check_nbtd_ratio(
    exam_data: dict,
    level_cfg: dict,
    issues: list,
) -> tuple[dict, dict]:
    """Kiểm tra tỉ lệ NB/TH/VD/VDC trên toàn đề."""
    counter = {"NB": 0, "TH": 0, "VD": 0, "VDC": 0}

    all_questions = []
    for q in exam_data.get("part1_mc", []):
        all_questions.append(q.get("level", ""))
    for q in exam_data.get("part2_tf", []):
        for item in q.get("items", []):
            all_questions.append(item.get("level", ""))
    for q in exam_data.get("part3_sa", []):
        all_questions.append(q.get("level", ""))

    for lv in all_questions:
        lv = lv.upper().strip()
        if lv in counter:
            counter[lv] += 1

    total_labeled = sum(counter.values())
    actual_pct = {}
    if total_labeled > 0:
        for lv, cnt in counter.items():
            actual_pct[lv] = round(cnt / total_labeled * 100, 1)

    # So sánh với chuẩn
    expected_ratio = level_cfg.get("nbtd_ratio", (30, 40, 20, 10))
    expected_pct = {
        "NB": expected_ratio[0],
        "TH": expected_ratio[1],
        "VD": expected_ratio[2],
        "VDC": expected_ratio[3],
    }

    if total_labeled == 0:
        issues.append(ValidationIssue(
            severity="warning", code="GDPT-201",
            message="Không có câu hỏi nào được gán mức độ tư duy NB/TH/VD/VDC.",
            suggestion="Gán key 'level' cho từng câu hỏi (giá trị: 'NB', 'TH', 'VD', 'VDC').",
        ))
    else:
        for lv, exp in expected_pct.items():
            act = actual_pct.get(lv, 0)
            diff = abs(act - exp)
            if diff > 15:
                issues.append(ValidationIssue(
                    severity="warning", code="GDPT-202",
                    message=(
                        f"Tỉ lệ mức {lv}: thực tế {act:.1f}%, chuẩn GDPT 2018 ≈ {exp}%. "
                        f"Lệch {diff:.1f}%."
                    ),
                    suggestion=f"Điều chỉnh số câu mức {lv} để gần hơn với {exp}%.",
                ))

    return actual_pct, expected_pct


def _check_true_false_questions(exam_data: dict, issues: list) -> None:
    """Kiểm tra câu Đúng/Sai có đủ 4 ý a/b/c/d không."""
    for q in exam_data.get("part2_tf", []):
        qid = q.get("id", "?")
        items = q.get("items", [])

        if len(items) != 4:
            issues.append(ValidationIssue(
                severity="error", code="GDPT-301",
                message=f"Phần II, Câu {qid}: có {len(items)} ý, chuẩn GDPT 2018 cần đúng 4 ý (a, b, c, d).",
                suggestion="Bổ sung hoặc bỏ bớt ý cho đủ 4.",
                location=f"Phần II, Câu {qid}",
            ))

        labels = [item.get("label", "").lower() for item in items]
        expected_labels = ["a", "b", "c", "d"]
        for exp_lbl in expected_labels:
            if exp_lbl not in labels:
                issues.append(ValidationIssue(
                    severity="error", code="GDPT-302",
                    message=f"Phần II, Câu {qid}: thiếu ý '{exp_lbl}'.",
                    location=f"Phần II, Câu {qid}",
                ))

        # Kiểm tra mức độ tư duy của 4 ý
        levels_in_q = [item.get("level", "").upper() for item in items]
        if len(set(levels_in_q)) < 2 and all(l for l in levels_in_q):
            issues.append(ValidationIssue(
                severity="warning", code="GDPT-303",
                message=(
                    f"Phần II, Câu {qid}: 4 ý có cùng mức độ tư duy '{levels_in_q[0]}'. "
                    "Nên đa dạng: ý a = NB, ý b = TH, ý c = VD, ý d = VDC."
                ),
                location=f"Phần II, Câu {qid}",
            ))

        # Kiểm tra không phải tất cả 4 ý đều ĐÚNG hoặc đều SAI
        answers = [item.get("answer") for item in items if "answer" in item]
        if answers:
            if all(a is True for a in answers):
                issues.append(ValidationIssue(
                    severity="warning", code="GDPT-304",
                    message=f"Phần II, Câu {qid}: cả 4 ý đều ĐÚNG — không nên thiết kế như vậy.",
                    location=f"Phần II, Câu {qid}",
                    suggestion="Đặt ít nhất 1 ý SAI.",
                ))
            elif all(a is False for a in answers):
                issues.append(ValidationIssue(
                    severity="warning", code="GDPT-305",
                    message=f"Phần II, Câu {qid}: cả 4 ý đều SAI — không nên thiết kế như vậy.",
                    location=f"Phần II, Câu {qid}",
                    suggestion="Đặt ít nhất 1 ý ĐÚNG.",
                ))


def _check_short_answer(exam_data: dict, issues: list) -> None:
    """Kiểm tra câu trả lời ngắn — kết quả phải là số gọn."""
    for q in exam_data.get("part3_sa", []):
        qid = q.get("id", "?")
        answer = q.get("answer")
        if answer is None:
            continue
        try:
            val = float(str(answer).replace(",", "."))
            # Kiểm tra số thập phân ≤ 2 chữ số
            str_val = f"{val:.10f}".rstrip("0").rstrip(".")
            decimal_part = str_val.split(".")[-1] if "." in str_val else ""
            if len(decimal_part) > 2:
                issues.append(ValidationIssue(
                    severity="warning", code="GDPT-401",
                    message=(
                        f"Phần III, Câu {qid}: đáp án '{answer}' có quá nhiều chữ số thập phân. "
                        "Chuẩn GDPT 2018: kết quả phải là số nguyên hoặc thập phân ≤ 2 chữ số."
                    ),
                    location=f"Phần III, Câu {qid}",
                    suggestion="Chọn lại số liệu bài toán để kết quả gọn hơn.",
                ))
        except (ValueError, TypeError):
            # Đáp án dạng text (Văn, Địa, KTPL) — không kiểm tra số
            pass


def _check_real_world_context(exam_data: dict, issues: list) -> None:
    """Kiểm tra có ít nhất 1 câu mang ngữ cảnh thực tiễn không."""
    all_q = (
        exam_data.get("part1_mc", [])
        + exam_data.get("part2_tf", [])
        + exam_data.get("part3_sa", [])
    )
    context_count = sum(1 for q in all_q if q.get("has_context", False))
    total = len(all_q)

    if total > 0 and context_count == 0:
        issues.append(ValidationIssue(
            severity="error", code="GDPT-501",
            message=(
                "Không có câu hỏi nào mang ngữ cảnh thực tiễn. "
                "GDPT 2018 yêu cầu ít nhất 1–2 câu gắn với đời sống thực tế."
            ),
            suggestion=(
                "Thêm bài toán thực tế: tối ưu kinh tế, thí nghiệm vật lý thực, "
                "ứng dụng hóa học trong cuộc sống..."
            ),
        ))
    elif total > 0:
        pct = context_count / total * 100
        if pct < 10:
            issues.append(ValidationIssue(
                severity="warning", code="GDPT-502",
                message=f"Chỉ có {context_count}/{total} câu ({pct:.1f}%) có ngữ cảnh thực tiễn. Nên tăng lên ≥ 15%.",
            ))


def _check_essay(exam_data: dict, subject_key: str, issues: list) -> None:
    """Kiểm tra phần tự luận — bắt buộc có bước phiên giải thực tiễn."""
    essay_qs = exam_data.get("essay", [])
    if not essay_qs:
        return

    for q in essay_qs:
        qid = q.get("id", "?")

        # Bài toán thực tế phải có bước phiên giải
        if subject_key in ("math", "physics", "chemistry", "biology"):
            if not q.get("has_real_world_conclusion", False):
                issues.append(ValidationIssue(
                    severity="warning", code="GDPT-601",
                    message=(
                        f"Tự luận, Câu {qid}: chưa có bước phiên giải kết quả về thực tiễn. "
                        "GDPT 2018 yêu cầu: 'Vậy trong thực tế, [ý nghĩa kết quả]'."
                    ),
                    location=f"Tự luận, Câu {qid}",
                    suggestion="Thêm câu kết luận liên hệ thực tế vào cuối lời giải.",
                ))

        # Kiểm tra điểm tự luận
        points = q.get("points", 0)
        if points <= 0:
            issues.append(ValidationIssue(
                severity="error", code="GDPT-602",
                message=f"Tự luận, Câu {qid}: chưa gán điểm (points = 0).",
                location=f"Tự luận, Câu {qid}",
            ))


def _check_subject_specific(
    exam_data: dict,
    subject_key: str,
    level_cfg: dict,
    issues: list,
) -> None:
    """Kiểm tra đặc thù riêng từng môn."""

    if subject_key == "physics" and level_cfg.get("requires_error_analysis"):
        # Kiểm tra câu Đúng/Sai Vật lý có ý về sai số không
        has_error_q = False
        for q in exam_data.get("part2_tf", []):
            stem = q.get("stem", "").lower()
            if any(kw in stem for kw in ["sai số", "đo đạc", "thực nghiệm", "bảng số liệu", "thí nghiệm"]):
                has_error_q = True
                break
        if not has_error_q:
            issues.append(ValidationIssue(
                severity="warning", code="GDPT-701",
                message="Môn Vật Lý GDPT 2018: nên có ít nhất 1 câu Đúng/Sai liên quan đến thực nghiệm hoặc phân tích sai số.",
                suggestion="Thiết kế câu Đúng/Sai dựa trên bảng số liệu đo đạc thực nghiệm.",
            ))

    if subject_key == "chemistry":
        # Kiểm tra có bài toán bảo toàn electron/nguyên tố không
        all_text = " ".join([
            q.get("question", "") for q in exam_data.get("part1_mc", [])
        ] + [
            q.get("stem", "") for q in exam_data.get("part2_tf", [])
        ]).lower()
        if "bảo toàn" not in all_text and "conservation" not in all_text:
            issues.append(ValidationIssue(
                severity="warning", code="GDPT-711",
                message="Môn Hóa Học: chưa thấy câu hỏi sử dụng phương pháp bảo toàn (khối lượng/electron/nguyên tố).",
                suggestion="Bổ sung ít nhất 1 câu áp dụng định luật bảo toàn theo chuẩn GDPT 2018.",
            ))

    if subject_key == "khtn" and level_cfg.get("requires_integration"):
        # Kiểm tra có câu tích hợp không
        integrated_count = sum(
            1 for q in exam_data.get("part2_tf", [])
            if q.get("integrated", False)
        )
        if integrated_count == 0:
            issues.append(ValidationIssue(
                severity="warning", code="GDPT-721",
                message="KHTN: chưa có câu Đúng/Sai tích hợp liên môn (Lý+Hóa / Hóa+Sinh / Lý+Sinh).",
                suggestion="Thiết kế ít nhất 1 câu kết hợp 2 phân môn trong KHTN.",
            ))

    if subject_key == "literature":
        # Môn Văn: phải có phần Đọc hiểu và phần Viết
        reading_ok = len(exam_data.get("part1_reading", [])) > 0 or "reading_passage" in exam_data
        writing_ok = len(exam_data.get("essay", [])) >= 2  # NL xã hội + NL văn học
        if not reading_ok:
            issues.append(ValidationIssue(
                severity="error", code="GDPT-731",
                message="Môn Ngữ Văn: thiếu Phần Đọc hiểu văn bản.",
                suggestion="Thêm key 'reading_passage' hoặc 'part1_reading' vào exam_data.",
            ))
        if not writing_ok:
            issues.append(ValidationIssue(
                severity="error", code="GDPT-732",
                message=(
                    f"Môn Ngữ Văn: Phần Viết có {len(exam_data.get('essay', []))} bài "
                    "— cần 2 bài (Nghị luận xã hội + Nghị luận văn học)."
                ),
            ))

def _check_solution_methodology(
    exam_data: dict,
    subject_key: str,
    issues: list,
) -> None:
    """
    Kiểm định phương pháp giải theo chuẩn GDPT 2018 (Solution Methodology Audit).
    Ngăn chặn việc giáo viên/AI sử dụng phương pháp giải cũ (chương trình 2006).
    """
    all_items = []
    for q in exam_data.get("part1_mc", []):
        all_items.append(("part1", q.get("id", "?"), q))
    for q in exam_data.get("part2_tf", []):
        all_items.append(("part2", q.get("id", "?"), q))
    for q in exam_data.get("part3_sa", []):
        all_items.append(("part3", q.get("id", "?"), q))
    for q in exam_data.get("essay", []):
        all_items.append(("essay", q.get("id", "?"), q))

    # 1. TOÁN (Math)
    if subject_key == "math":
        for part, qid, q in all_items:
            sol = q.get("solution", "")
            has_ctx = q.get("has_context", False) or part == "essay" or q.get("level") in ("VD", "VDC")
            if has_ctx and sol:
                sol_lower = sol.lower()
                real_keywords = [
                    "trong thực tế", "thực tiễn", "vậy để", "kết luận",
                    "cần sản xuất", "chi phí nhỏ nhất là", "thể tích cần",
                    "diện tích cần", "vậy sau", "vậy thời gian"
                ]
                if not any(kw in sol_lower for kw in real_keywords):
                    issues.append(ValidationIssue(
                        severity="warning",
                        code="GDPT-SOL-M01",
                        message=f"{part.upper()}, Câu {qid}: Bài toán thực tế/ứng dụng chưa có câu kết luận phiên giải thực tiễn ('Vậy trong thực tế, ...').",
                        location=f"{part.upper()}, Câu {qid}",
                        suggestion="Bổ sung bước 4: 'Vậy trong thực tế, để... cần...'.",
                    ))

    # 2. VẬT LÝ (Physics)
    elif subject_key == "physics":
        has_direction_stated = False
        has_si_units = False
        for part, qid, q in all_items:
            sol = q.get("solution", "").lower()
            if any(kw in sol for kw in ["chiều dương", "gốc thời gian", "gốc toạ độ", "chiều dòng điện", "chọn chiều"]):
                has_direction_stated = True
            if any(u in sol for u in ["m/s", "km/h", "kg", "rad/s", "n", "j", "w", "hz", "v", "a", "pa", "t"]):
                has_si_units = True

        if not has_direction_stated and len(all_items) > 0:
            issues.append(ValidationIssue(
                severity="warning",
                code="GDPT-SOL-P01",
                message="Môn Vật Lý: Lời giải các bài toán chuyển động/lực nên nêu rõ quy ước ('Chọn chiều dương là...').",
                suggestion="Ghi rõ quy ước chiều dương và mốc thời gian ở đầu lời giải.",
            ))

    # 3. HÓA HỌC (Chemistry)
    elif subject_key == "chemistry":
        has_conservation = False
        for part, qid, q in all_items:
            sol = q.get("solution", "").lower()
            if any(kw in sol for kw in ["bảo toàn", "btkl", "bte", "btnt", "bảo toàn khối lượng", "bảo toàn electron", "bảo toàn nguyên tố"]):
                has_conservation = True

        if not has_conservation and len(all_items) > 0:
            issues.append(ValidationIssue(
                severity="warning",
                code="GDPT-SOL-C01",
                message="Môn Hóa Học: Bài toán tính toán hỗn hợp cần lập sơ đồ bảo toàn (khối lượng/nguyên tố/electron) theo chuẩn GDPT 2018 thay vì tính truyền thống.",
                suggestion="Lập sơ đồ bảo toàn trước khi tính toán số mol hoặc khối lượng.",
            ))

    # 4. ĐỊA LÝ (Geography)
    elif subject_key == "geography":
        for part, qid, q in all_items:
            if part == "essay":
                sol = q.get("solution", "").lower()
                if not any(kw in sol for kw in ["giải pháp", "đề xuất", "định hướng", "chính sách", "phát triển bền vững"]):
                    issues.append(ValidationIssue(
                        severity="warning",
                        code="GDPT-SOL-G01",
                        message=f"Tự luận Địa lý, Câu {qid}: Thiếu Bước 4 (Đề xuất giải pháp / định hướng phát triển bền vững).",
                        location=f"Tự luận, Câu {qid}",
                        suggestion="Bổ sung bước đề xuất giải pháp phát triển bền vững ở cuối lời giải.",
                    ))

    # 5. KINH TẾ & PHÁP LUẬT (Economics & Law)
    elif subject_key == "economics_law":
        for part, qid, q in all_items:
            if part == "essay":
                sol = q.get("solution", "").lower()
                if not any(kw in sol for kw in ["quy định", "căn cứ", "theo luật", "hành vi", "hậu quả", "bảo vệ quyền lợi"]):
                    issues.append(ValidationIssue(
                        severity="warning",
                        code="GDPT-SOL-E01",
                        message=f"Tình huống KTPL, Câu {qid}: Cần nêu rõ căn cứ quy phạm pháp luật và giải pháp bảo vệ quyền lợi.",
                        location=f"Tự luận, Câu {qid}",
                        suggestion="Áp dụng quy trình 5 bước giải quyết tình huống pháp luật GDPT 2018.",
                    ))


# ─────────────────────────────────────────────────────────────────────
# Hàm xuất báo cáo đẹp ra console
# ─────────────────────────────────────────────────────────────────────

def print_validation_report(result: ValidationResult, verbose: bool = True) -> None:
    """In báo cáo kiểm định ra console với định dạng dễ đọc."""
    SUBJECT_NAMES = {
        "math": "Toán", "physics": "Vật Lý", "chemistry": "Hóa Học",
        "biology": "Sinh Học", "khtn": "KHTN", "geography": "Địa Lý",
        "economics_law": "Kinh Tế & Pháp Luật", "literature": "Ngữ Văn",
    }
    subject_name = SUBJECT_NAMES.get(result.subject, result.subject.title())
    level_name = "THPT" if result.level == "thpt" else "THCS"

    print("\n" + "=" * 60)
    print(f"  KIỂM ĐỊNH CHUẨN GDPT 2018 — Môn {subject_name} ({level_name})")
    print("=" * 60)
    print(f"  {result.summary}")
    print(f"  Tổng câu hỏi: {result.total_questions} câu")
    print(f"  Phân bố: P.I={result.stats.get('part1_count',0)} | "
          f"P.II={result.stats.get('part2_count',0)} | "
          f"P.III={result.stats.get('part3_count',0)} | "
          f"TL={result.stats.get('essay_count',0)}")

    if result.scores:
        print(f"  Điểm: " + " + ".join(
            f"P{k[-1]}={v:.2f}đ" if k.startswith("part") else f"Tổng={v:.2f}đ"
            for k, v in result.scores.items()
        ))

    # Tỉ lệ NB/TH/VD/VDC
    if result.nbtd_actual:
        print("\n  TỈ LỆ MỨC ĐỘ TƯ DUY:")
        print(f"  {'Mức':<8} {'Thực tế':>12} {'Chuẩn GDPT':>12} {'Đánh giá':>10}")
        print("  " + "-" * 44)
        for lv in ["NB", "TH", "VD", "VDC"]:
            act = result.nbtd_actual.get(lv, 0)
            exp = result.nbtd_expected.get(lv, 0)
            diff = abs(act - exp)
            rating = "✅ OK" if diff <= 15 else "⚠️ Lệch"
            print(f"  {lv:<8} {act:>10.1f}% {exp:>10.0f}% {rating:>10}")

    # Danh sách lỗi và cảnh báo
    errors   = [i for i in result.issues if i.severity == "error"]
    warnings = [i for i in result.issues if i.severity == "warning"]
    infos    = [i for i in result.issues if i.severity == "info"]

    if errors:
        print(f"\n  ❌ LỖI ({len(errors)} lỗi — BẮT BUỘC SỬA):")
        for i, issue in enumerate(errors, 1):
            print(f"   {i}. [{issue.code}] {issue.message}")
            if issue.location:
                print(f"      📍 Vị trí: {issue.location}")
            if verbose and issue.suggestion:
                print(f"      💡 Gợi ý: {issue.suggestion}")

    if warnings:
        print(f"\n  ⚠️  CẢNH BÁO ({len(warnings)} cảnh báo — nên xem xét):")
        for i, issue in enumerate(warnings, 1):
            print(f"   {i}. [{issue.code}] {issue.message}")
            if issue.location:
                print(f"      📍 Vị trí: {issue.location}")
            if verbose and issue.suggestion:
                print(f"      💡 Gợi ý: {issue.suggestion}")

    if infos:
        print(f"\n  ℹ️  THÔNG TIN ({len(infos)}):")
        for i, issue in enumerate(infos, 1):
            print(f"   {i}. [{issue.code}] {issue.message}")

    if not result.issues:
        print("\n  🎉 Không có lỗi hay cảnh báo nào. Đề thi hoàn toàn đạt chuẩn GDPT 2018!")

    print("=" * 60 + "\n")


def validation_to_dict(result: ValidationResult) -> dict:
    """Chuyển ValidationResult thành dict để serialize JSON."""
    return {
        "valid": result.valid,
        "subject": result.subject,
        "level": result.level,
        "total_questions": result.total_questions,
        "summary": result.summary,
        "stats": result.stats,
        "scores": result.scores,
        "nbtd_actual": result.nbtd_actual,
        "nbtd_expected": result.nbtd_expected,
        "issues": [
            {
                "severity": i.severity,
                "code": i.code,
                "message": i.message,
                "location": i.location,
                "suggestion": i.suggestion,
            }
            for i in result.issues
        ],
    }


# ─────────────────────────────────────────────────────────────────────
# CLI tự test nhanh
# ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Ví dụ đề Toán THPT mẫu để test
    sample_exam = {
        "title": "Đề kiểm tra Toán 12 học kỳ I — Mẫu",
        "subject": "Toán",
        "grade": 12,
        "part1_mc": [
            {"id": i, "question": f"Câu {i}", "options": ["A", "B", "C", "D"],
             "answer": "A", "level": ["NB", "NB", "NB", "TH", "TH", "TH",
                                       "TH", "TH", "VD", "VD", "VDC", "VDC"][i-1],
             "has_context": i in (9, 12)}
            for i in range(1, 13)
        ],
        "part2_tf": [
            {
                "id": i, "stem": f"Cho hàm số... (câu {i})",
                "has_context": i == 2,
                "items": [
                    {"label": "a", "statement": "Hàm số đồng biến...", "answer": True,  "level": "NB"},
                    {"label": "b", "statement": "Hàm số có CĐ tại...", "answer": False, "level": "TH"},
                    {"label": "c", "statement": "Giá trị CT bằng...", "answer": True,  "level": "VD"},
                    {"label": "d", "statement": "Đồ thị cắt y = 2 tại...", "answer": False, "level": "VDC"},
                ],
            }
            for i in range(1, 5)
        ],
        "part3_sa": [
            {"id": i, "question": f"Tính...", "answer": i * 3,
             "level": ["TH", "TH", "VD", "VD", "VDC", "VDC"][i-1],
             "has_context": i == 5}
            for i in range(1, 7)
        ],
        "essay": [
            {"id": 1, "question": "Khảo sát hàm số...", "solution": "...",
             "points": 1.0, "has_real_world_conclusion": False},
        ],
    }

    result = validate_exam_gdpt2018(sample_exam, subject="Toán", level="thpt")
    print_validation_report(result)
    print("JSON output:")
    print(json.dumps(validation_to_dict(result), ensure_ascii=False, indent=2))
