# -*- coding: utf-8 -*-
"""
=============================================================================
MODULE: interactive_video_builder.py (v6.4.0 / v2.1.0 - Complete 10-Type GDPT 2018 Suite)
HỆ THỐNG TỰ ĐỘNG TẠO VIDEO TƯƠNG TÁC E-LEARNING (CHUẨN GDPT 2018)
- Bộ kiểm định chất lượng sư phạm tự động (Checkpoint QA Validator cho trọn bộ 10 dạng câu hỏi:
  mcq, tf, fill, drag, tf_group, multi, match, order, cloze, classify)
- Khóa chống tua nhanh 100% (Anti-Skip System) & Chặn YouTube phát ngầm khi mở câu hỏi
- Khung câu hỏi tràn màn hình di động (100dvh), chống mất chữ khi điền số
- Cơ chế Vượt trạm đến khi Đúng (Mastery Gate): Sai KHÔNG hiện giải thích, KHÔNG lộ đáp án từng ý nhỏ
  (kèm nút Xem lại 30s & 3s suy ngẫm ở Đúng/Sai); ĐÚNG 100% mới hiện Giải thích + cộng trọn +1 điểm + nút Tiếp tục (6s)
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


def _parse_strict_bool(val, context_msg: str) -> bool:
    if isinstance(val, bool):
        return val
    if val is None:
        raise ValueError(f"{context_msg}: Thiếu giá trị Đúng/Sai (correct)!")
    s = str(val).strip().lower()
    if s in ("true", "đúng", "dung", "1", "t", "yes"):
        return True
    if s in ("false", "sai", "0", "f", "no"):
        return False
    raise ValueError(f"{context_msg}: Giá trị Đúng/Sai '{val}' không hợp lệ (chỉ nhận true/false)!")


def _normalize_token_for_match(val: str) -> str:
    s = str(val or "").strip()
    s = re.sub(r"[\u2212\u2013\u2014]", "-", s)
    s = re.sub(r"\s+", " ", s).lower()
    s = s.strip("$").strip()
    return s


def _heal_cloze_math_boundaries(template: str) -> str:
    """
    Nếu người soạn vô tình đặt placeholder {{1}} bên trong cặp dấu $...$ của KaTeX
    (ví dụ: "$a^m \\cdot a^n = {{1}}$"), tự động tách công thức thành các đoạn $...$ riêng
    nằm hai bên ô trống (ví dụ: "$a^m \\cdot a^n =$ {{1}}") để KaTeX luôn render chuẩn, không vỡ công thức.
    Bỏ qua \\$ (dấu $ thường) và $$ (công thức display).
    """
    if not re.search(r"\{\{\d+\}\}", template):
        return template

    # Tokenize: '$' đơn, placeholder, hoặc văn bản thường
    tokens = []
    pattern = re.compile(r"(\\\$|\$\$|\$|\{\{\d+\}\})")
    pos = 0
    for m in pattern.finditer(template):
        if m.start() > pos:
            tokens.append(("TXT", template[pos:m.start()]))
        tok = m.group(0)
        if tok == "$":
            tokens.append(("DOLLAR", tok))
        elif tok.startswith("{{"):
            tokens.append(("PH", tok))
        else:
            tokens.append(("TXT", tok))  # \$ hoặc $$ giữ nguyên như văn bản
        pos = m.end()
    if pos < len(template):
        tokens.append(("TXT", template[pos:]))

    def _wrap_math(chunk: str) -> str:
        if not chunk.strip():
            return chunk
        lead = chunk[:len(chunk) - len(chunk.lstrip())]
        trail = chunk[len(chunk.rstrip()):]
        return f"{lead}${chunk.strip()}${trail}"

    out = []
    i = 0
    n = len(tokens)
    while i < n:
        kind, val = tokens[i]
        if kind != "DOLLAR":
            out.append(val)
            i += 1
            continue
        # Tìm dấu $ đóng tương ứng
        j = i + 1
        while j < n and tokens[j][0] != "DOLLAR":
            j += 1
        if j >= n:
            # Không có $ đóng -> giữ nguyên phần còn lại
            out.extend(t[1] for t in tokens[i:])
            break
        inner = tokens[i + 1:j]
        if not any(t[0] == "PH" for t in inner):
            out.append("$" + "".join(t[1] for t in inner) + "$")
        else:
            buf = ""
            for t_kind, t_val in inner:
                if t_kind == "PH":
                    out.append(_wrap_math(buf))
                    buf = ""
                    if out and out[-1] and not out[-1][-1:].isspace():
                        out.append(" ")
                    out.append(t_val)
                else:
                    buf += t_val
            out.append((" " + _wrap_math(buf.strip())) if buf.strip() else "")
        i = j + 1

    healed = "".join(out)
    healed = re.sub(r"[ \t]{2,}", " ", healed)
    return healed


def validate_checkpoints(checkpoints: list, video_duration: int = 900) -> list:
    """
    BỘ KIỂM ĐỊNH CHẤT LƯỢNG SƯ PHẠM (QA GATE - HỖ TRỢ TRỌN BỘ 10 DẠNG CÂU HỎI GDPT 2018):
    1. Chuẩn hóa ID tăng dần (1, 2, 3...)
    2. Sắp xếp mốc thời gian tăng dần tuyến tính
    3. Kiểm tra chặt chẽ cấu trúc dữ liệu của cả 10 dạng:
       mcq, tf, fill, drag, tf_group, multi, match, order, cloze, classify
    4. Cảnh báo nhịp độ sư phạm (Pacing: 2.5 - 3.5 phút/câu)
    """
    if not checkpoints or not isinstance(checkpoints, list):
        raise ValueError("Danh sách checkpoints không được để trống!")

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

        # 1. MCQ: Trắc nghiệm 1 lựa chọn đúng (GIỮ NGUYÊN 100% logic gốc v6.3.x)
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

        # 2. TF: Đúng / Sai đơn (GIỮ NGUYÊN 100% logic gốc v6.3.x)
        elif cp_type in ("tf", "true_false"):
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

        # 3. FILL: Điền đáp án ngắn / Điền số (GIỮ NGUYÊN 100% logic gốc v6.3.x)
        elif cp_type in ("fill", "numeric_fill"):
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

        # 4. DRAG: Chạm / Ghép thẻ vào 1 ô kết quả (GIỮ NGUYÊN 100% logic gốc v6.3.x)
        elif cp_type in ("drag", "tap_to_place"):
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

        # 5. TF_GROUP: Đúng / Sai Đa Mệnh Đề (a, b, c, d chuẩn Phần II Bộ GD&ĐT)
        elif cp_type in ("tf_group", "true_false_group", "tf4", "tf_multi"):
            raw_stmts = cp.get("statements") if cp.get("statements") is not None else cp.get("items", [])
            if not isinstance(raw_stmts, list) or not (2 <= len(raw_stmts) <= 6):
                raise ValueError(f"Trạm {cp_id} (Đúng/Sai đa mệnh đề): Danh sách statements phải có từ 2 đến 6 mệnh đề!")
            clean_stmts = []
            for s_idx, st in enumerate(raw_stmts):
                if not isinstance(st, dict):
                    raise ValueError(f"Trạm {cp_id} (tf_group): Mệnh đề thứ {s_idx + 1} phải là object {{label, text, correct}}!")
                st_text = str(st.get("text") if st.get("text") is not None else st.get("statement", "")).strip()
                if not st_text:
                    raise ValueError(f"Trạm {cp_id} (tf_group): Nội dung mệnh đề thứ {s_idx + 1} không được để trống!")
                st_label = str(st.get("label", "")).strip() or f"{chr(ord('a') + s_idx)})"
                st_corr = _parse_strict_bool(st.get("correct"), f"Trạm {cp_id} (tf_group - ý {st_label})")
                clean_stmts.append({
                    "label": st_label,
                    "text": st_text,
                    "correct": st_corr
                })
            valid_item = {
                "id": cp_id,
                "time": cp_time,
                "type": "tf_group",
                "question": cp_q,
                "statements": clean_stmts,
                "explanation": cp_exp
            }

        # 6. MULTI: Trắc nghiệm Nhiều Đáp Án Đúng (Checkbox)
        elif cp_type in ("multi", "mcq_multi", "checkbox", "multiple_response"):
            opts = [str(o).strip() for o in (cp.get("options") or []) if str(o).strip()]
            if len(opts) < 3:
                raise ValueError(f"Trạm {cp_id} (Chọn nhiều đáp án): Phải có ít nhất 3 phương án (options)!")
            raw_corr = cp.get("correct")
            if not isinstance(raw_corr, (list, tuple)) or len(raw_corr) == 0:
                raise ValueError(f"Trạm {cp_id} (Chọn nhiều đáp án): Trường 'correct' phải là danh sách chỉ số đáp án đúng (ví dụ [0, 2])!")
            clean_corr = sorted({int(i) for i in raw_corr})
            for c_idx in clean_corr:
                if c_idx < 0 or c_idx >= len(opts):
                    raise ValueError(f"Trạm {cp_id} (multi): Chỉ số đáp án đúng ({c_idx}) nằm ngoài phạm vi options (0..{len(opts)-1})!")
            valid_item = {
                "id": cp_id,
                "time": cp_time,
                "type": "multi",
                "question": cp_q,
                "options": opts,
                "correct": clean_corr,
                "explanation": cp_exp
            }

        # 7. MATCH: Nối Cặp Tương Ứng 2 Cột (Cột A <-> Cột B)
        elif cp_type in ("match", "matching", "pair_match"):
            raw_pairs = cp.get("pairs", [])
            if not isinstance(raw_pairs, list) or not (2 <= len(raw_pairs) <= 6):
                raise ValueError(f"Trạm {cp_id} (Nối cặp): Danh sách 'pairs' phải có từ 2 đến 6 cặp!")
            clean_pairs = []
            for p_idx, pair in enumerate(raw_pairs):
                if not isinstance(pair, dict):
                    raise ValueError(f"Trạm {cp_id} (match): Cặp thứ {p_idx + 1} phải là object {{left, right}}!")
                left_s = str(pair.get("left", "")).strip()
                right_s = str(pair.get("right", "")).strip()
                if not left_s or not right_s:
                    raise ValueError(f"Trạm {cp_id} (match): Cặp thứ {p_idx + 1} thiếu nội dung 'left' hoặc 'right'!")
                clean_pairs.append({"left": left_s, "right": right_s})
            distractors = [str(d).strip() for d in (cp.get("distractors") or []) if str(d).strip()]
            if len(distractors) > 4:
                distractors = distractors[:4]
            valid_item = {
                "id": cp_id,
                "time": cp_time,
                "type": "match",
                "question": cp_q,
                "pairs": clean_pairs,
                "distractors": distractors,
                "explanation": cp_exp
            }

        # 8. ORDER: Sắp Xếp Thứ Tự Quy Trình / Dãy Số
        elif cp_type in ("order", "sequence", "sort", "ordering"):
            raw_items = [str(it).strip() for it in (cp.get("items") or []) if str(it).strip()]
            if not (2 <= len(raw_items) <= 8):
                raise ValueError(f"Trạm {cp_id} (Sắp xếp thứ tự): Danh sách 'items' phải có từ 2 đến 8 bước/phần tử!")
            if isinstance(cp.get("correct"), (list, tuple)) and len(cp["correct"]) == len(raw_items):
                perm = [int(i) for i in cp["correct"]]
                if sorted(perm) != list(range(len(raw_items))):
                    raise ValueError(f"Trạm {cp_id} (order): Thứ tự 'correct' không phải là hoán vị hợp lệ của 0..{len(raw_items)-1}!")
                raw_items = [raw_items[i] for i in perm]
            valid_item = {
                "id": cp_id,
                "time": cp_time,
                "type": "order",
                "question": cp_q,
                "items": raw_items,
                "explanation": cp_exp
            }

        # 9. CLOZE: Điền Khuyết Nhiều Chỗ Trống {{1}}, {{2}}
        elif cp_type in ("cloze", "fill_blanks", "multi_fill"):
            raw_tpl = str(cp.get("template") or cp.get("passage") or cp.get("text") or "").strip()
            raw_blanks = cp.get("blanks") if cp.get("blanks") is not None else cp.get("answers")
            if raw_blanks is None and isinstance(cp.get("correct"), list):
                raw_blanks = cp.get("correct")
            if not raw_tpl:
                raise ValueError(f"Trạm {cp_id} (Điền khuyết): Thiếu đoạn văn mẫu 'template' chứa các vị trí {{{{1}}}}, {{{{2}}}}!")
            if not isinstance(raw_blanks, list) or not (1 <= len(raw_blanks) <= 6):
                raise ValueError(f"Trạm {cp_id} (Điền khuyết): Danh sách 'blanks' phải có từ 1 đến 6 đáp án!")
            clean_blanks = [str(b).strip() for b in raw_blanks if str(b).strip()]
            if len(clean_blanks) != len(raw_blanks):
                raise ValueError(f"Trạm {cp_id} (Điền khuyết): Đáp án trong 'blanks' không được để trống!")

            # Nếu người soạn dùng ___ (3+ gạch dưới) thay vì {{1}}, {{2}} -> tự động đánh số {{1}}, {{2}}...
            if "{{1}}" not in raw_tpl and re.search(r"_{3,}", raw_tpl):
                counter = [0]
                def _repl_underscore(_m):
                    counter[0] += 1
                    return f"{{{{{counter[0]}}}}}"
                raw_tpl = re.sub(r"_{3,}", _repl_underscore, raw_tpl)

            for b_i in range(1, len(clean_blanks) + 1):
                token = f"{{{{{b_i}}}}}"
                if token not in raw_tpl:
                    raise ValueError(
                        f"Trạm {cp_id} (Điền khuyết): Có {len(clean_blanks)} đáp án trong 'blanks' nhưng không tìm thấy vị trí '{token}' trong 'template'!"
                    )

            extra_nums = sorted({int(x) for x in re.findall(r"\{\{(\d+)\}\}", raw_tpl) if int(x) < 1 or int(x) > len(clean_blanks)})
            if extra_nums:
                raise ValueError(
                    f"Trạm {cp_id} (Điền khuyết): 'template' có vị trí {extra_nums} vượt quá số đáp án trong 'blanks' ({len(clean_blanks)})!"
                )

            healed_tpl = _heal_cloze_math_boundaries(raw_tpl)

            raw_bank = cp.get("wordBank") if cp.get("wordBank") is not None else (cp.get("word_bank") or cp.get("tiles") or [])
            clean_bank = [str(w).strip() for w in raw_bank if str(w).strip()] if isinstance(raw_bank, list) else []
            if clean_bank:
                # Đảm bảo 100% mỗi ô trống đều có đáp án khớp trong wordBank để học sinh luôn giải được
                bank_norms = [_normalize_token_for_match(w) for w in clean_bank]
                for b_spec in clean_blanks:
                    accepted_norms = [_normalize_token_for_match(x) for x in b_spec.split("|") if x.strip()]
                    if not any(an in bank_norms for an in accepted_norms):
                        primary_ans = b_spec.split("|")[0].strip()
                        clean_bank.append(primary_ans)
                        bank_norms.append(_normalize_token_for_match(primary_ans))

            valid_item = {
                "id": cp_id,
                "time": cp_time,
                "type": "cloze",
                "question": cp_q,
                "template": healed_tpl,
                "blanks": clean_blanks,
                "wordBank": clean_bank,
                "explanation": cp_exp
            }

        # 10. CLASSIFY: Phân Loại Thẻ Vào 2-4 Nhóm Kiến Thức
        elif cp_type in ("classify", "categorize", "group_sort", "classification"):
            raw_cats = cp.get("categories") if cp.get("categories") is not None else cp.get("groups", [])
            clean_cats = [str(c).strip() for c in (raw_cats or []) if str(c).strip()]
            if not (2 <= len(clean_cats) <= 4):
                raise ValueError(f"Trạm {cp_id} (Phân loại nhóm): Danh sách 'categories' phải có từ 2 đến 4 nhóm!")
            cat_lookup = {c.lower(): i for i, c in enumerate(clean_cats)}

            raw_items = cp.get("items", [])
            if not isinstance(raw_items, list) or not (2 <= len(raw_items) <= 12):
                raise ValueError(f"Trạm {cp_id} (Phân loại nhóm): Danh sách 'items' phải có từ 2 đến 12 thẻ dữ kiện!")
            clean_items = []
            for it_idx, it in enumerate(raw_items):
                if not isinstance(it, dict):
                    raise ValueError(f"Trạm {cp_id} (classify): Thẻ thứ {it_idx + 1} phải là object {{text, category}}!")
                it_text = str(it.get("text", "")).strip()
                if not it_text:
                    raise ValueError(f"Trạm {cp_id} (classify): Thẻ thứ {it_idx + 1} không được để trống 'text'!")
                raw_cat = it.get("category") if it.get("category") is not None else it.get("group")
                if isinstance(raw_cat, int) or (isinstance(raw_cat, str) and raw_cat.strip().isdigit()):
                    cat_idx = int(raw_cat)
                elif isinstance(raw_cat, str) and raw_cat.strip().lower() in cat_lookup:
                    cat_idx = cat_lookup[raw_cat.strip().lower()]
                else:
                    raise ValueError(
                        f"Trạm {cp_id} (classify): Nhóm '{raw_cat}' của thẻ '{it_text}' không hợp lệ (chỉ nhận chỉ số 0..{len(clean_cats)-1} hoặc tên nhóm)!"
                    )
                if cat_idx < 0 or cat_idx >= len(clean_cats):
                    raise ValueError(
                        f"Trạm {cp_id} (classify): Chỉ số nhóm ({cat_idx}) của thẻ '{it_text}' vượt quá số nhóm ({len(clean_cats)})!"
                    )
                clean_items.append({"text": it_text, "category": cat_idx})

            valid_item = {
                "id": cp_id,
                "time": cp_time,
                "type": "classify",
                "question": cp_q,
                "categories": clean_cats,
                "items": clean_items,
                "explanation": cp_exp
            }

        else:
            raise ValueError(
                f"Trạm {cp_id}: Định dạng câu hỏi '{cp_type}' không được hỗ trợ "
                f"(hỗ trợ 10 dạng: mcq, tf, fill, drag, tf_group, multi, match, order, cloze, classify)!"
            )

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
    Sinh file HTML Video Tương Tác E-Learning hoàn chỉnh dựa trên Master Template đã qua kiểm định QA (10 dạng câu hỏi).
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
    html = re.sub(r'<title>.*?</title>', lambda _: f'<title>Video Tương Tác: {lesson_title} - {subject_grade}</title>', html)
    html = re.sub(r'<h1>📚.*?</h1>', lambda _: f'<h1>📚 {subject_grade.upper()} - {lesson_title.upper()}</h1>', html)
    html = re.sub(r'<p>SGK Kết Nối Tri Thức.*?• GV:.*?</p>', lambda _: f'<p>Chương trình GDPT 2018 • GV: {teacher_name}</p>', html)
    html = re.sub(
        r'<strong id="registerLessonTitle">.*?</strong>',
        lambda _: f'<strong id="registerLessonTitle">{subject_grade} - {lesson_title}</strong>',
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
    # Dùng lambda để re.sub KHÔNG thông dịch các chuỗi LaTeX như \cdot, \frac, \mathbb trong cp_json!
    html = re.sub(pattern_cp, lambda _: replacement_cp, html, flags=re.DOTALL)

    if output_html_path:
        os.makedirs(os.path.dirname(os.path.abspath(output_html_path)), exist_ok=True)
        with open(output_html_path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"✅ Đã tạo file Video Tương Tác: {output_html_path} ({len(html)} bytes)")

    return html


def print_netlify_next_steps(folder_path: str, is_update: bool = False):
    """
    In hướng dẫn bước tiếp theo đưa lên Netlify (hiển thị tự động sau mọi lệnh tạo mới hoặc đổi mật khẩu).
    """
    abs_folder = os.path.abspath(folder_path)
    print("\n" + "=" * 72)
    if not is_update:
        print("🌐 BƯỚC TIẾP THEO ĐỂ ĐƯA BÀI GIẢNG LÊN WEB NETLIFY (CHỈ MẤT 30 GIÂY):")
        print(f"   📁 Thư mục cần kéo thả: {abs_folder}")
        print("   ⚠️ LƯU Ý SỐNG CÒN: Kéo CẢ THƯ MỤC trên (TUYỆT ĐỐI KHÔNG kéo lẻ file index.html để tránh lỗi 404)!")
        print("   1. Mở trình duyệt vào https://app.netlify.com (đăng nhập miễn phí bằng Google/Gmail).")
        print("   2. Ở cột trái bấm 'Projects' (hoặc 'Sites') -> bấm 'Add new project' ('Add new site') -> chọn 'Deploy manually'.")
        print(f"   3. Cầm CẢ THƯ MỤC '{os.path.basename(abs_folder)}' kéo thả vào ô nét đứt -> chờ 3 giây hiện 'Published'!")
        print("   4. Đổi tên link đẹp: Vào 'Project configuration' ('Site configuration') -> 'Change project name' -> đặt tên không dấu (vd: toan6-bai6) -> Save.")
        print("   5. Mở link -> bấm '⚙️ Thầy Cô: TẮT' nhập mật khẩu kiểm tra nhanh câu hỏi -> tắt Chế độ Thầy Cô rồi gửi link vào Zalo lớp!")
    else:
        print("🌐 BƯỚC TIẾP THEO ĐỂ CẬP NHẬT LÊN WEB NETLIFY (GIỮ NGUYÊN 100% LINK CŨ):")
        print(f"   📁 Thư mục vừa cập nhật: {abs_folder}")
        print("   ⚠️ LƯU Ý: KHÔNG bấm 'Add new project' để không bị đổi đường link đã gửi cho học sinh!")
        print("   1. Mở https://app.netlify.com -> trong mục 'Projects' ('Sites'), bấm trực tiếp vào TÊN BÀI GIẢNG CŨ cần cập nhật.")
        print("   2. Bấm vào tab 'Deploys' trên thanh menu ngang.")
        print(f"   3. Cầm CẢ THƯ MỤC '{os.path.basename(abs_folder)}' kéo thả vào khung nét đứt cập nhật ở giữa trang.")
        print("   4. Chờ 3 giây hiện 'Published' -> mở lại link bài giảng bấm Ctrl + F5 (link Zalo học sinh giữ nguyên 100%, mật khẩu/nội dung mới có hiệu lực ngay!).")
    print("=" * 72 + "\n")


def package_netlify_folder(html_content: str, folder_path: str):
    """
    Đóng gói thư mục chuẩn index.html để giáo viên kéo thả vào Netlify Drop.
    """
    os.makedirs(folder_path, exist_ok=True)
    index_file = os.path.join(folder_path, "index.html")
    with open(index_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"📦 Đã đóng gói thư mục Netlify: {folder_path} (chứa index.html)")
    print_netlify_next_steps(folder_path, is_update=False)
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
    print_netlify_next_steps(os.path.dirname(html_file), is_update=True)
    return html_file


if __name__ == "__main__":
    import argparse
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    parser = argparse.ArgumentParser(description="Công cụ tạo & quản trị Video Tương Tác E-Learning (10 dạng câu hỏi GDPT 2018)")
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
        print("Module interactive_video_builder (v6.4.0 / v2.1.0) with 10-Type QA Gate, Teacher Password Manager & Netlify Handoff ready.")
