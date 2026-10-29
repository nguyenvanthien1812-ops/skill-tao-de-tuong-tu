# -*- coding: utf-8 -*-
"""
=============================================================================
MODULE: interactive_video_builder.py
HỆ THỐNG TỰ ĐỘNG TẠO VIDEO TƯƠNG TÁC E-LEARNING (CHUẨN GDPT 2018)
- Chống tua nhanh 100% (Anti-Skip System)
- Nhúng trạm câu hỏi tương tác điểm dừng vàng (Golden Timestamps)
- Phản hồi tức thì 1-chạm & Thang điểm sư phạm chống đoán mò
- Tiêu chuẩn hoàn thành bài học (Mastery Threshold >= 80%)
- Tự động bảo lưu tiến độ khi rớt mạng (Smart Auto-Resume)
- Tối ưu hóa di động tràn màn hình (Mobile Viewport Take-over)
- Đổi tên & lớp học sinh 1-chạm
- Chế độ Thầy Cô kiểm duyệt (Teacher Preview Mode - Mật mã 123456)
- Đồng bộ Google Sheets tự động tách tab từng lớp (Apps Script V4)
=============================================================================
"""

import os
import sys
import json
import re

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
    output_html_path: str = None
) -> str:
    """
    Sinh file HTML Video Tương Tác E-Learning hoàn chỉnh dựa trên Master Template.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    skill_dir = os.path.dirname(script_dir)
    template_path = os.path.join(skill_dir, "templates", "video_tuong_tac_template.html")

    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Không tìm thấy template tại: {template_path}")

    with open(template_path, "r", encoding="utf-8") as f:
        html = f.read()

    # 1. Thay thế Title & Header
    full_title = f"{lesson_title} - {subject_grade}"
    html = re.sub(r'<title>.*?</title>', f'<title>Video Tương Tác: {full_title}</title>', html)
    html = re.sub(r'<h1>📚.*?</h1>', f'<h1>📚 {lesson_title.upper()} - {subject_grade.upper()}</h1>', html)
    html = re.sub(r'<p>SGK Kết Nối Tri Thức.*?• GV:.*?</p>', f'<p>Chương trình GDPT 2018 • GV: {teacher_name}</p>', html)

    # 2. Thay thế Constants
    html = re.sub(
        r"const SCRIPT_WEB_APP_URL = '.*?';",
        f"const SCRIPT_WEB_APP_URL = '{apps_script_url}';",
        html
    )
    html = re.sub(
        r"const YOUTUBE_VIDEO_ID = '.*?';",
        f"const YOUTUBE_VIDEO_ID = '{youtube_id}';",
        html
    )
    html = re.sub(
        r"const LOCAL_VIDEO_PATH = '.*?';",
        f"const LOCAL_VIDEO_PATH = '{local_video_path}';",
        html
    )
    html = re.sub(
        r"const TEACHER_PASSWORD = '.*?';",
        f"const TEACHER_PASSWORD = '{teacher_password}';",
        html
    )
    html = re.sub(
        r"const PASSING_THRESHOLD_PCT = \d+;",
        f"const PASSING_THRESHOLD_PCT = {passing_threshold_pct};",
        html
    )

    # 3. Thay thế Mảng checkpoints
    cp_json = json.dumps(checkpoints, ensure_ascii=False, indent=6)
    pattern_cp = r"const checkpoints = \[.*?\];"
    replacement_cp = f"const checkpoints = {cp_json};"
    html = re.sub(pattern_cp, replacement_cp, html, flags=re.DOTALL)

    # 4. Ghi ra file nếu có chỉ định output_html_path
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


if __name__ == "__main__":
    print("Module interactive_video_builder ready.")
