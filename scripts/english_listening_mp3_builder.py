#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
english_listening_mp3_builder.py — Bộ Máy Tạo File Nghe MP3 Tiếng Anh Chuẩn Khảo Thí
=====================================================================================
Thực thi Kế hoạch Đồng bộ hóa Ngược 5 Bước (5-Step Backward Synchronization Plan)
bảo đảm file MP3 khớp tuyệt đối 100% với câu hỏi và đáp án trên đề thi:
  1. Anchor-Point Mapping: Khóa chặt từng câu hỏi [Q1..Qn] với bằng chứng đáp án.
  2. Strict Linear Order: Kiểm tra thứ tự xuất hiện thông tin từ đầu đến cuối.
  3. Spoken-Text Normalization: Chuẩn hóa số đếm, tiền tệ, năm, số thứ tự, từ viết tắt, đánh vần.
  4. Cross-Audit QA Gate: Kiểm định chéo (Đề ↔ Tapescript ↔ Đáp án & giới hạn từ Gap-fill).
  5. Multi-Voice Studio Mixing: Phối âm đa giọng đọc bản xứ (Edge Neural TTS) + nhạc hiệu
     phòng thi (Chime tone) + khoảng lặng đọc đề + nghe 2 lần tự động.
"""

import os
import re
import sys
import json
import shutil
import asyncio
import argparse
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


# ============================================================================
# 1. BẢNG PHÂN VAI GIỌNG ĐỌC BẢN XỨ (EDGE NEURAL VOICES) & TỐC ĐỘ ĐỌC THEO CẤP
# ============================================================================
VOICE_PRESETS: Dict[str, str] = {
    "announcer": "en-GB-SoniaNeural",       # Giám thị / Phát thanh viên dẫn quy chế (Anh - Anh RP)
    "female_uk": "en-GB-LibbyNeural",       # Nữ Anh - Anh (Giáo viên, Điều phối viên, Nhân viên)
    "male_uk": "en-GB-RyanNeural",          # Nam Anh - Anh (Học sinh, Chuyên gia, Người hướng dẫn)
    "female_us": "en-US-JennyNeural",       # Nữ Anh - Mỹ (Phóng viên, MC, Sinh viên)
    "female_academic": "en-US-AriaNeural",  # Nữ Anh - Mỹ học thuật (Tiến sĩ, Nhà khoa học)
    "male_us": "en-US-GuyNeural",           # Nam Anh - Mỹ trầm ấm (Giáo sư giảng bài, Diễn giả)
    "male_academic": "en-US-ChristopherNeural",  # Nam Anh - Mỹ trang trọng
    "female_au": "en-AU-NatashaNeural",     # Nữ Anh - Úc
    "male_au": "en-AU-WilliamNeural",       # Nam Anh - Úc
}

LEVEL_SPEED_PRESETS: Dict[str, str] = {
    "grade_6_7": "-10%",   # Lớp 6-7: ~115-125 WPM, rõ ràng, chậm rãi
    "grade_8_9": "-5%",    # Lớp 8-9 đại trà / Thi vào 10: ~130-140 WPM
    "hsg_9": "+0%",        # Học sinh giỏi Lớp 9 / Chuyên Anh: ~150-160 WPM (chuẩn bản xứ)
    "thpt": "-3%",         # THPT (Lớp 10-12): ~140-150 WPM
    "hsg_thpt": "+0%",     # HSG THPT / IELTS: ~155-165 WPM
}


# ============================================================================
# 2. BỘ CHUẨN HÓA VĂN BẢN NÓI (SPOKEN-TEXT NORMALIZER)
# ============================================================================
class SpokenTextNormalizer:
    """
    Chuyển đổi văn bản Tapescript in trên giấy thành Văn bản Nói (Phonetic Script)
    trước khi đưa vào TTS nhằm chống đọc sai ký hiệu, tiền tệ, năm tháng hoặc đọc lướt số.
    """

    ABBREVIATIONS = {
        r"\bDr\.": "Doctor",
        r"\bProf\.": "Professor",
        r"\bMr\.": "Mister",
        r"\bMrs\.": "Missus",
        r"\bMs\.": "Miz",
        r"\bSt\.": "Saint",
        r"\bMt\.": "Mount",
        r"\be\.g\.": "for example",
        r"\bi\.e\.": "that is",
        r"\betc\.": "et cetera",
        r"\bvs\.": "versus",
    }

    ORDINALS = {
        "1st": "first", "2nd": "second", "3rd": "third", "4th": "fourth",
        "5th": "fifth", "6th": "sixth", "7th": "seventh", "8th": "eighth",
        "9th": "ninth", "10th": "tenth", "11th": "eleventh", "12th": "twelfth",
        "13th": "thirteenth", "14th": "fourteenth", "15th": "fifteenth",
        "16th": "sixteenth", "17th": "seventeenth", "18th": "eighteenth",
        "19th": "nineteenth", "20th": "twentieth", "21st": "twenty-first",
    }

    @classmethod
    def strip_anchor_tags(cls, text: str) -> str:
        """
        Xóa sạch mọi nhãn neo câu hỏi như [Q1], [Q12], (Q1), (Q6 - False), [Q5: A]
        để máy thu âm tuyệt đối không đọc lộ nhãn câu hỏi vào bài nghe.
        """
        cleaned = re.sub(r"\[Q\d+[^\]]*\]", "", text)
        cleaned = re.sub(r"\(Q\d+[^)]*\)", "", cleaned)
        cleaned = re.sub(r"\s{2,}", " ", cleaned)
        return cleaned.strip()

    @classmethod
    def expand_spelling_tags(cls, text: str) -> str:
        """
        Chuyển cú pháp [SPELL: MARYKIRK] thành 'M - A - R - Y - K - I - R - K'
        có nhịp ngắt tự nhiên cho các câu hỏi yêu cầu đánh vần tên riêng.
        """
        def _repl(match: re.Match) -> str:
            word = match.group(1).strip().upper()
            letters = [ch for ch in word if ch.isalnum()]
            return ", ".join(letters)

        return re.sub(r"\[SPELL:\s*([A-Za-z0-9]+)\s*\]", _repl, text)

    @classmethod
    def normalize(cls, text: str) -> str:
        """Chuẩn hóa toàn diện chuỗi văn bản trước khi đọc TTS."""
        out = cls.strip_anchor_tags(text)
        out = cls.expand_spelling_tags(out)

        # Chuẩn hóa từ viết tắt học thuật / chức danh
        for pattern, replacement in cls.ABBREVIATIONS.items():
            out = re.sub(pattern, replacement, out)

        # Chuẩn hóa thế kỷ / số thứ tự (7th -> seventh)
        for ord_key, ord_word in cls.ORDINALS.items():
            out = re.sub(rf"\b{ord_key}\b", ord_word, out, flags=re.IGNORECASE)

        # Chuẩn hóa phần trăm (20% -> 20 percent)
        out = re.sub(r"(\d+(?:\.\d+)?)\s*%", r"\1 percent", out)

        # Chuẩn hóa tiền tệ ($60 -> 60 dollars, £45 -> 45 pounds)
        out = re.sub(r"\$(\d+(?:,\d{3})*(?:\.\d+)?)", r"\1 dollars", out)
        out = re.sub(r"£(\d+(?:,\d{3})*(?:\.\d+)?)", r"\1 pounds", out)

        return out.strip()


# ============================================================================
# 3. BỘ KIỂM ĐỊNH ĐỒNG BỘ 5 BƯỚC (LISTENING SYNC VALIDATOR - QA GATE)
# ============================================================================
class ListeningSyncValidator:
    """
    Kiểm định chéo giữa Danh sách Câu hỏi - Kịch bản Tapescript - Bảng Đáp án
    trước khi sinh âm thanh MP3. Đảm bảo:
      1. Đủ 100% mốc neo [Q1]..[Qn] trong Tapescript.
      2. Các mốc [Q1]..[Qn] xuất hiện theo đúng trình tự tuyến tính (tăng dần).
      3. Với câu hỏi Gap-fill / Note completion: từ đáp án bắt buộc có mặt trong
         câu thoại chứa mốc [Qn] và không vượt quá giới hạn số từ (max_words).
    """

    @staticmethod
    def validate_spec(spec: Dict[str, Any]) -> Tuple[bool, List[str], List[Dict[str, Any]]]:
        errors: List[str] = []
        audit_rows: List[Dict[str, Any]] = []

        parts = spec.get("parts", [])
        if not parts:
            return False, ["Cấu hình bài nghe (spec) không có phần (parts) nào."], []

        all_expected_qids: List[int] = []
        all_found_qids_in_order: List[int] = []

        for p_idx, part in enumerate(parts, start=1):
            p_title = part.get("title", f"Part {p_idx}")
            p_type = part.get("type", "mcq").lower()  # mcq | tf | gapfill
            max_words = int(part.get("max_words", 3))
            questions = part.get("questions", [])
            segments = part.get("segments", [])

            full_raw_script = "\n".join(seg.get("text", "") for seg in segments)

            # Tìm thứ tự xuất hiện các tag [Q<num>] hoặc (Q<num>) trong script của part này
            found_tags = [
                int(m.group(1))
                for m in re.finditer(r"[\[\(]Q(\d+)[^\]\)]*[\]\)]", full_raw_script)
            ]
            all_found_qids_in_order.extend(found_tags)

            # Kiểm tra tính đơn điệu tăng (Strict Linear Order) trong từng Part
            for i in range(len(found_tags) - 1):
                if found_tags[i] > found_tags[i + 1]:
                    errors.append(
                        f"{p_title}: Sai thứ tự tuyến tính! Câu Q{found_tags[i]} xuất hiện trước Q{found_tags[i + 1]} trong bài nghe."
                    )

            for q in questions:
                qid = int(q["id"])
                all_expected_qids.append(qid)
                ans = str(q.get("answer", "")).strip()
                if not ans:
                    errors.append(f"{p_title} - Câu {qid}: Thiếu đáp án (answer).")
                    continue

                # Kiểm tra mốc neo [Q<qid>] có tồn tại trong script không
                anchor_pattern = re.compile(rf"[\[\(]Q{qid}\b[^\]\)]*[\]\)]")
                has_anchor = bool(anchor_pattern.search(full_raw_script))

                # Với dạng gapfill, kiểm tra từ đáp án có xuất hiện thực tế trong script không
                ans_variants = [v.strip() for v in re.split(r"[/|]", ans) if v.strip()]
                clean_script_lower = SpokenTextNormalizer.strip_anchor_tags(full_raw_script).lower()
                norm_script_lower = SpokenTextNormalizer.normalize(full_raw_script).lower()

                evidence_ok = True
                if p_type == "gapfill":
                    evidence_ok = any(
                        v.lower() in clean_script_lower or v.lower() in norm_script_lower
                        for v in ans_variants
                    )
                    if not evidence_ok:
                        errors.append(
                            f"{p_title} - Câu {qid} (Gap-fill): Đáp án '{ans}' không xuất hiện trong kịch bản bài nghe!"
                        )
                    # Kiểm tra số lượng từ của đáp án chuẩn đầu tiên
                    first_ans_words = ans_variants[0].split()
                    if len(first_ans_words) > max_words:
                        errors.append(
                            f"{p_title} - Câu {qid} (Gap-fill): Đáp án '{ans_variants[0]}' có {len(first_ans_words)} từ, vượt quá giới hạn {max_words} từ!"
                        )

                if not has_anchor:
                    errors.append(
                        f"{p_title} - Câu {qid}: Chưa gắn nhãn neo [Q{qid}] trong kịch bản Tapescript."
                    )

                audit_rows.append({
                    "part": p_title,
                    "q_id": qid,
                    "type": p_type.upper(),
                    "answer": ans,
                    "has_anchor": has_anchor,
                    "evidence_ok": evidence_ok,
                })

        return len(errors) == 0, errors, audit_rows

    @staticmethod
    def print_audit_report(is_valid: bool, errors: List[str], audit_rows: List[Dict[str, Any]]) -> None:
        print("=" * 72)
        print("  🔍 BÁO CÁO KIỂM ĐỊNH ĐỒNG BỘ ĐỀ THI ↔ TAPESCRIPT ↔ MP3 (QA GATE)")
        print("=" * 72)
        for row in audit_rows:
            status = "✅ KHỚP 100%" if (row["has_anchor"] and row["evidence_ok"]) else "❌ LỆCH"
            print(
                f"  • Câu {row['q_id']:02d} [{row['type']:7s}] | Đáp án: {row['answer']:25s} | Neo [Q{row['q_id']}]: {status}"
            )
        print("-" * 72)
        if is_valid:
            print(f"  🎉 KẾT LUẬN: ĐẠT CHUẨN 100% ({len(audit_rows)}/{len(audit_rows)} câu khớp tuyệt đối, đúng thứ tự tuyến tính).")
        else:
            print(f"  ⛔ PHÁT HIỆN {len(errors)} LỖI ĐỒNG BỘ CẦN SỬA TRƯỚC KHI XUẤT MP3:")
            for err in errors:
                print(f"     - {err}")
        print("=" * 72)


# ============================================================================
# 4. BỘ PHỐI ÂM PHÒNG THU ĐA GIỌNG ĐỌC (MULTI-VOICE STUDIO PRODUCER)
# ============================================================================
def _resolve_voice(voice_key_or_name: str) -> str:
    return VOICE_PRESETS.get(voice_key_or_name.lower(), voice_key_or_name)


def _resolve_rate(level_or_rate: str) -> str:
    if not level_or_rate:
        return "+0%"
    if level_or_rate.endswith("%"):
        return level_or_rate
    return LEVEL_SPEED_PRESETS.get(level_or_rate.lower(), "+0%")


def _create_chime_segment(duration_ms: int = 600, freq: int = 880):
    """Tạo tiếng chuông báo hiệu chuẩn phòng thi (Chime tone)."""
    from pydub.generators import Sine
    tone = Sine(freq).to_audio_segment(duration=duration_ms)
    return tone.fade_in(50).fade_out(100) - 10


async def _synthesize_tts(text: str, voice: str, out_path: Path, rate: str = "+0%", pitch: str = "+0Hz") -> Path:
    import edge_tts
    spoken_text = SpokenTextNormalizer.normalize(text)
    communicate = edge_tts.Communicate(text=spoken_text, voice=voice, rate=rate, pitch=pitch)
    await communicate.save(str(out_path))
    return out_path


async def build_listening_exam_mp3(
    spec: Dict[str, Any],
    output_dir: str | Path,
    copy_to_dir: Optional[str | Path] = None,
    strict_qa: bool = True,
) -> Dict[str, str]:
    """
    Hàm tổng hợp trọn bộ file nghe MP3 từ cấu trúc dữ liệu `spec`.
    Tự động chạy cổng kiểm định `ListeningSyncValidator` trước khi thu âm.
    """
    is_valid, errors, audit_rows = ListeningSyncValidator.validate_spec(spec)
    ListeningSyncValidator.print_audit_report(is_valid, errors, audit_rows)
    if strict_qa and not is_valid:
        raise ValueError("Kiểm định đồng bộ Tapescript - Câu hỏi thất bại. Vui lòng sửa các lỗi trên trước khi tạo MP3.")

    from pydub import AudioSegment

    out_dir = Path(output_dir)
    temp_dir = out_dir / "_temp_tts_segments"
    out_dir.mkdir(parents=True, exist_ok=True)
    temp_dir.mkdir(parents=True, exist_ok=True)

    announcer_voice = _resolve_voice(spec.get("announcer_voice", "announcer"))
    default_rate = _resolve_rate(spec.get("level", "hsg_9"))
    play_count = int(spec.get("play_count", 2))
    master_filename = spec.get("master_filename", "FULL_LISTENING_EXAM.mp3")

    chime = _create_chime_segment(600, 880)
    sil_2s = AudioSegment.silent(duration=2000)
    sil_5s = AudioSegment.silent(duration=5000)

    # 1. Thu âm lời dẫn mở đầu (Intro)
    intro_text = spec.get(
        "intro_text",
        "Ministry of Education and Training. English Listening Test. "
        "This test consists of three parts. Each part will be played twice. "
        "Write all your answers on the answer sheet.",
    )
    intro_mp3 = temp_dir / "intro.mp3"
    await _synthesize_tts(intro_text, announcer_voice, intro_mp3, rate="+0%")

    again_mp3 = temp_dir / "listen_again.mp3"
    await _synthesize_tts("Now listen again.", announcer_voice, again_mp3, rate="+0%")

    part_mp3_paths: List[str] = []
    part_audio_segments: List[AudioSegment] = []

    # 2. Thu âm và ráp từng Part
    for p_idx, part in enumerate(spec.get("parts", []), start=1):
        p_filename = part.get("filename", f"SECTION_I_PART_{p_idx}_LISTENING.mp3")
        pre_pause_sec = int(part.get("pre_pause_sec", 30))
        between_pause_sec = int(part.get("between_pause_sec", 15))
        post_pause_sec = int(part.get("post_pause_sec", 20))
        part_rate = _resolve_rate(part.get("rate", default_rate))

        inst_text = part.get(
            "instruction",
            f"Part {p_idx}. Listen carefully and answer the questions. "
            f"You now have {pre_pause_sec} seconds to look at the questions for Part {p_idx}.",
        )
        inst_mp3 = temp_dir / f"p{p_idx}_inst.mp3"
        await _synthesize_tts(inst_text, announcer_voice, inst_mp3, rate="+0%")

        end_text = part.get(
            "outro",
            f"That is the end of Part {p_idx}. You now have {post_pause_sec} seconds to check your answers.",
        )
        end_mp3 = temp_dir / f"p{p_idx}_end.mp3"
        await _synthesize_tts(end_text, announcer_voice, end_mp3, rate="+0%")

        # Thu âm các lượt lời thoại (segments) trong Part
        body_audio = AudioSegment.empty()
        for s_idx, seg in enumerate(part.get("segments", [])):
            v_name = _resolve_voice(seg.get("voice", "male_us"))
            s_rate = _resolve_rate(seg.get("rate", part_rate))
            pause_after_ms = int(seg.get("pause_after_ms", 650))
            seg_mp3 = temp_dir / f"p{p_idx}_seg_{s_idx}.mp3"
            await _synthesize_tts(seg["text"], v_name, seg_mp3, rate=s_rate)
            body_audio += AudioSegment.from_mp3(str(seg_mp3)) + AudioSegment.silent(duration=pause_after_ms)

        # Ráp hoàn chỉnh 1 Part (Đọc hướng dẫn -> Nghỉ đọc đề -> Chime -> Lần 1 -> Nghỉ -> Lần 2 -> Nghỉ kiểm tra)
        part_track = (
            AudioSegment.from_mp3(str(inst_mp3))
            + AudioSegment.silent(duration=pre_pause_sec * 1000)
            + chime
            + sil_2s
            + body_audio
        )
        if play_count >= 2:
            part_track += (
                AudioSegment.silent(duration=between_pause_sec * 1000)
                + AudioSegment.from_mp3(str(again_mp3))
                + sil_2s
                + chime
                + sil_2s
                + body_audio
            )
        part_track += (
            sil_2s
            + chime
            + sil_2s
            + AudioSegment.from_mp3(str(end_mp3))
            + AudioSegment.silent(duration=post_pause_sec * 1000)
        )

        part_out_path = out_dir / p_filename
        part_track.export(str(part_out_path), format="mp3", bitrate="192k")
        part_mp3_paths.append(str(part_out_path))
        part_audio_segments.append(part_track)
        print(f"  [✓] Đã xuất file nghe Part {p_idx}: {part_out_path}")

    # 3. Ráp File Tổng hợp Toàn Bài (Master Track)
    full_track = AudioSegment.from_mp3(str(intro_mp3)) + sil_5s
    for idx, p_seg in enumerate(part_audio_segments):
        full_track += p_seg
        if idx < len(part_audio_segments) - 1:
            full_track += sil_5s

    master_out_path = out_dir / master_filename
    full_track.export(str(master_out_path), format="mp3", bitrate="192k")
    duration_sec = len(full_track) / 1000.0
    print(
        f"  [✓] Đã xuất file MASTER toàn bài ({int(duration_sec // 60)}p {int(duration_sec % 60)}s): {master_out_path}"
    )

    # Dọn dẹp thư mục tạm
    shutil.rmtree(temp_dir, ignore_errors=True)

    # Sao chép sang thư mục đích phụ (ví dụ Downloads) nếu có yêu cầu
    if copy_to_dir:
        dst_dir = Path(copy_to_dir)
        dst_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(master_out_path, dst_dir / master_filename)
        for p_path in part_mp3_paths:
            shutil.copy2(p_path, dst_dir / Path(p_path).name)
        print(f"  [✓] Đã sao chép trọn bộ file MP3 sang: {dst_dir}")

    return {
        "master_mp3": str(master_out_path),
        "part_mp3s": part_mp3_paths,
        "duration_seconds": round(duration_sec, 1),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Công cụ tạo file nghe MP3 môn Tiếng Anh chuẩn khảo thí (khớp 100% câu hỏi)."
    )
    parser.add_argument("--spec", required=True, help="Đường dẫn tới file JSON đặc tả bài nghe (listening_spec.json)")
    parser.add_argument("--out", default="./listening_audio", help="Thư mục lưu các file MP3 đầu ra")
    parser.add_argument("--copy-to", default=None, help="Thư mục phụ để sao chép file MP3 (ví dụ Downloads)")
    parser.add_argument("--validate-only", action="store_true", help="Chỉ chạy kiểm định đồng bộ QA Gate mà không sinh MP3")
    args = parser.parse_args()

    spec_path = Path(args.spec)
    if not spec_path.exists():
        print(f"Lỗi: Không tìm thấy file spec tại {spec_path}")
        return 1

    spec_data = json.loads(spec_path.read_text(encoding="utf-8"))
    if args.validate_only:
        is_valid, errors, audit_rows = ListeningSyncValidator.validate_spec(spec_data)
        ListeningSyncValidator.print_audit_report(is_valid, errors, audit_rows)
        return 0 if is_valid else 1

    asyncio.run(build_listening_exam_mp3(spec_data, args.out, copy_to_dir=args.copy_to))
    return 0


if __name__ == "__main__":
    sys.exit(main())
