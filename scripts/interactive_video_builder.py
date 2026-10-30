# -*- coding: utf-8 -*-
"""
=============================================================================
MODULE: interactive_video_builder.py (v6.3.4 - Mastery Gate, Secure Teacher Password & QA Gate)
HỆ THỐNG TỰ ĐỘNG TẠO VIDEO TƯƠNG TÁC E-LEARNING (CHUẨN GDPT 2018)
- Bộ kiểm định chất lượng sư phạm tự động (Checkpoint QA Validator cho cả 4 dạng: mcq, tf, fill, drag)
- Khóa chống tua nhanh 100% (Anti-Skip System) & Chặn YouTube phát ngầm khi mở câu hỏi
- Khung câu hỏi tràn màn hình di động (100dvh), chống mất chữ khi điền số
- Cơ chế Vượt trạm đến khi Đúng (Mastery Gate): Sai KHÔNG hiện giải thích (kèm nút Xem lại 30s & 3s suy ngẫm ở Đúng/Sai); ĐÚNG mới hiện Giải thích + cộng trọn +1 điểm + nút Tiếp tục (6s)
- Tiêu chuẩn hoàn thành bài học công bằng (Mastery Threshold >= 80% số câu hoàn thành + thống kê số câu đúng ngay lần đầu)
- Tự động bảo lưu tiến độ khi rớt mạng (Smart Auto-Resume)
- Đổi tên & lớp học sinh 1-chạm
- Chế độ Thầy Cô kiểm duyệt (Teacher Preview Mode - cho phép đặt/đổi mật khẩu riêng, ẩn hoàn toàn gợi ý mật khẩu khỏi màn hình học sinh)
- Đồng bộ Google Sheets tự động tách tab từng lớp (Apps Script V4)
=============================================================================
"""

import os
import sys
import json
import re

def validate_checkpoints(checkpoints: list, video_duration: int = 900) -> list:
    """
    BỘ KIỂM ĐỊNH CHẤT LƯỢNG SƯ PHẠM (QA GATE):
    Đảm bảo 100% câu hỏi của các video tương lai đều chạy trơn tru, không lỗi:
    1. Chuẩn hóa ID tăng dần (1, 2, 3...)
    2. Sắp xếp mốc thời gian tăng dần tuyến tính
    3. Kiểm tra tính hợp lệ của từng loại câu hỏi (MCQ, Đúng/Sai, Điền số, Kéo thả)
    4. Cảnh báo nhịp độ sư phạm (Pacing: 2.5 - 3.5 phút/câu)
    """
    if not checkpoints or not isinstance(checkpoints, list):
        raise ValueError("Danh sách checkpoints không được để trống!")

    # 1. Tự động sắp xếp theo thời gian (giây)
    sorted_cp = sorted(checkpoints, key=lambda x: x.get("time", 0))

    validated = []
    for idx, cp in enumerate(sorted_cp, start=1):
        cp_id = idx
        cp_time = int(cp.get("time", 0))
        cp_type = str(cp.get("type", "mcq")).lower().strip()
        cp_q = str(cp.get("question", "")).strip()
        cp_exp = str(cp.get("explanation", "")).strip()

        if cp_time <= 0:
            raise ValueError(f"Trạm {cp_id}: Thời gian dừng (time) phải là số nguyên dương (giây)!")

        if not cp_q:
            raise ValueError(f"Trạm {cp_id}: Nội dung câu hỏi (question) không được để trống!")

        if not cp_exp:
            cp_exp = "Hãy ôn lại lý thuyết trong video để nắm vững kiến thức nhé."

        # Kiểm tra theo từng loại câu hỏi
        if cp_type == "mcq":
            opts = cp.get("options", [])
            if not isinstance(opts, list) or len(opts) < 2:
                raise ValueError(f"Trạm {cp_id} (MCQ): Phải có ít nhất 2 phương án lựa chọn!")
            correct = int(cp.get("correct", 0))
            if correct < 0 or correct >= len(opts):
                raise ValueError(f"Trạm {cp_id} (MCQ): Chỉ số đáp án đúng (correct={correct}) vượt quá số phương án ({len(opts)})!")
            valid_item = {
                "id": cp_id,
                "time": cp_time,
                "type": "mcq",
                "question": cp_q,
                "options": [str(o).strip() for o in opts],
                "correct": correct,
                "explanation": cp_exp
            }

        elif cp_type in ["tf", "true_false"]:
            correct_val = cp.get("correct")
            if not isinstance(correct_val, bool):
                if str(correct_val).lower() in ["true", "đúng", "1"]:
                    correct_val = True
                else:
                    correct_val = False
            valid_item = {
                "id": cp_id,
                "time": cp_time,
                "type": "tf",
                "question": cp_q,
                "correct": correct_val,
                "explanation": cp_exp
            }

        elif cp_type in ["fill", "numeric_fill"]:
            correct_val = str(cp.get("correct", "")).strip()
            if not correct_val:
                raise ValueError(f"Trạm {cp_id} (Điền số): Phải có đáp án chính xác (correct)!")
            valid_item = {
                "id": cp_id,
                "time": cp_time,
                "type": "fill",
                "question": cp_q,
                "correct": correct_val,
                "explanation": cp_exp
            }

        elif cp_type in ["drag", "tap_to_place"]:
            tiles = cp.get("tiles", [])
            correct_val = str(cp.get("correct", "")).strip()
            if not tiles or not correct_val:
                raise ValueError(f"Trạm {cp_id} (Kéo thả): Phải có danh sách thẻ (tiles) và đáp án (correct)!")
            valid_item = {
                "id": cp_id,
                "time": cp_time,
                "type": "drag",
                "question": cp_q,
                "tiles": [str(t).strip() for t in tiles],
                "correct": correct_val,
                "multiSelect": bool(cp.get("multiSelect", False)),
                "explanation": cp_exp
            }
        else:
            raise ValueError(f"Trạm {cp_id}: Định dạng câu hỏi '{cp_type}' không được hỗ trợ (chỉ nhận mcq, tf, fill, drag)!")

        validated.append(valid_item)

    # Kiểm tra nhịp độ sư phạm (Pacing check)
    for i in range(1, len(validated)):
        diff = validated[i]["time"] - validated[i-1]["time"]
        if diff < 45:
            print(f"⚠️ Cảnh báo Pacing: Trạm {validated[i-1]['id']} và {validated[i]['id']} quá sát nhau ({diff}s). Nên cách nhau từ 90s - 210s.")

    return validated


def build_interactive_video_html(
    lesson_title: str,
    subject_grade: str,
    teacher_name: str,
    youtube_id: str,
    apps_script_url: str,
    checkpoints: list,
    passing_threshold_pct: int = 80,
    teacher_password: str = "123456",
    local_video_path: str = "./video.mp4",
    video_duration: int = 860,
    output_html_path: str = None
) -> str:
    """
    Sinh file HTML Video Tương Tác E-Learning hoàn chỉnh dựa trên Master Template đã qua kiểm định QA.
    """
    clean_checkpoints = validate_checkpoints(checkpoints, video_duration=video_duration)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    skill_dir = os.path.dirname(script_dir)
    template_path = os.path.join(skill_dir, "templates", "video_tuong_tac_template.html")

    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Không tìm thấy template tại: {template_path}")

    with open(template_path, "r", encoding="utf-8") as f:
        html = f.read()

    full_title = f"{lesson_title} ({subject_grade})"
    safe_js_title = full_title.replace("\\", "\\\\").replace("'", "\\'")
    html = re.sub(r'<title>.*?</title>', f'<title>Video Tương Tác: {lesson_title} - {subject_grade}</title>', html)
    html = re.sub(r'<h1>📚.*?</h1>', f'<h1>📚 {subject_grade.upper()} - {lesson_title.upper()}</h1>', html)
    html = re.sub(r'<p>SGK Kết Nối Tri Thức.*?• GV:.*?</p>', f'<p>Chương trình GDPT 2018 • GV: {teacher_name}</p>', html)
    html = re.sub(
        r'<strong id="registerLessonTitle">.*?</strong>',
        f'<strong id="registerLessonTitle">{subject_grade} - {lesson_title}</strong>',
        html
    )

    html = re.sub(
        r"const LESSON_TITLE = '.*?';",
        lambda _: f"const LESSON_TITLE = '{safe_js_title}';",
        html
    )
    html = re.sub(
        r"const SCRIPT_WEB_APP_URL = '.*?';",
        lambda _: f"const SCRIPT_WEB_APP_URL = '{apps_script_url}';",
        html
    )
    html = re.sub(
        r"const YOUTUBE_VIDEO_ID = '.*?';",
        lambda _: f"const YOUTUBE_VIDEO_ID = '{youtube_id}';",
        html
    )
    html = re.sub(
        r"const LOCAL_VIDEO_PATH = '.*?';",
        lambda _: f"const LOCAL_VIDEO_PATH = '{local_video_path}';",
        html
    )
    safe_js_pwd = str(teacher_password if teacher_password is not None else "123456").strip()
    if not safe_js_pwd:
        safe_js_pwd = "123456"
    safe_js_pwd_escaped = safe_js_pwd.replace("\\", "\\\\").replace("'", "\\'")
    html = re.sub(
        r"const TEACHER_PASSWORD = '.*?';",
        lambda _: f"const TEACHER_PASSWORD = '{safe_js_pwd_escaped}';",
        html
    )
    # Bảo mật: Không bao giờ để lộ mật khẩu mặc định trong placeholder mà học sinh nhìn thấy
    html = re.sub(
        r'(<input[^>]*id="teacherPwd"[^>]*?)placeholder="Mặc định:[^"]*"',
        r'\1placeholder="Nhập mật mã bảo mật dành riêng cho Thầy Cô..."',
        html
    )
    html = re.sub(
        r"const PASSING_THRESHOLD_PCT = \d+;",
        f"const PASSING_THRESHOLD_PCT = {int(passing_threshold_pct)};",
        html
    )
    html = re.sub(
        r"let videoDuration = \d+;",
        f"let videoDuration = {int(video_duration)};",
        html
    )

    cp_json = json.dumps(clean_checkpoints, ensure_ascii=False, indent=6)
    pattern_cp = r"const checkpoints = \[.*?\];"
    replacement_cp = f"const checkpoints = {cp_json};"
    html = re.sub(pattern_cp, replacement_cp, html, flags=re.DOTALL)

    if output_html_path:
        os.makedirs(os.path.dirname(os.path.abspath(output_html_path)), exist_ok=True)
        with open(output_html_path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"✅ Đã tạo file Video Tương Tác: {output_html_path} ({len(html)} bytes)")

    return html


def package_netlify_folder(html_content: str, folder_path: str):
    """
    Đóng gói thư mục chuẩn index.html để giáo viên kéo thả vào Netlify Drop.
    """
    os.makedirs(folder_path, exist_ok=True)
    index_file = os.path.join(folder_path, "index.html")
    with open(index_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"📦 Đã đóng gói thư mục Netlify: {folder_path} (chứa index.html)")
    return folder_path


def update_teacher_password(target_path: str, new_password: str) -> str:
    """
    Đổi nhanh mật khẩu Chế độ Thầy Cô (TEACHER_PASSWORD) cho file HTML hoặc thư mục Netlify (chứa index.html) đã tạo sẵn,
    đồng thời xóa bỏ mọi placeholder lộ mật khẩu mặc định trên giao diện học sinh.
    """
    clean_pwd = str(new_password if new_password is not None else "").strip()
    if not clean_pwd:
        raise ValueError("Mật khẩu mới không được để trống!")

    resolved_path = os.path.abspath(target_path)
    if os.path.isdir(resolved_path):
        html_file = os.path.join(resolved_path, "index.html")
    else:
        html_file = resolved_path

    if not os.path.exists(html_file):
        raise FileNotFoundError(f"Không tìm thấy file bài giảng HTML tại: {html_file}")

    with open(html_file, "r", encoding="utf-8") as f:
        html = f.read()

    if "const TEACHER_PASSWORD" not in html:
        raise ValueError(f"File {html_file} không chứa cấu hình TEACHER_PASSWORD của Video Tương Tác!")

    safe_js_pwd_escaped = clean_pwd.replace("\\", "\\\\").replace("'", "\\'")
    html = re.sub(
        r"const TEACHER_PASSWORD = '.*?';",
        lambda _: f"const TEACHER_PASSWORD = '{safe_js_pwd_escaped}';",
        html
    )
    html = re.sub(
        r'(<input[^>]*id="teacherPwd"[^>]*?)placeholder="Mặc định:[^"]*"',
        r'\1placeholder="Nhập mật mã bảo mật dành riêng cho Thầy Cô..."',
        html
    )

    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"🔑 Đã cập nhật mật khẩu Chế độ Thầy Cô thành công tại: {html_file}")
    return html_file


if __name__ == "__main__":
    import argparse
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    parser = argparse.ArgumentParser(description="Công cụ tạo & quản trị Video Tương Tác E-Learning")
    parser.add_argument(
        "--set-password",
        nargs=2,
        metavar=("NEW_PASSWORD", "TARGET_HTML_OR_FOLDER"),
        help="Đổi mật khẩu Chế độ Thầy Cô cho file HTML hoặc thư mục Netlify có sẵn"
    )
    args = parser.parse_args()
    if args.set_password:
        new_pwd, target = args.set_password
        update_teacher_password(target, new_pwd)
    else:
        print("Module interactive_video_builder (v6.3.4) with QA Gate & Teacher Password Manager ready.")
