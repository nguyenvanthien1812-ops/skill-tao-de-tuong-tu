#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
essay_grader.py — Chấm Bài Tự Luận Bằng AI (Gemini Vision)
=============================================================
Quy trình: Ảnh bài làm HS → OCR (Gemini Vision) → RubricEngine → AIGrader → Báo cáo
Hỗ trợ 8 môn GDPT 2018. AI gợi ý điểm, GV quyết định cuối cùng.
Ảnh bài làm được gửi lên Gemini Vision API (Google Cloud).

Sử dụng:
    from scripts.essay_grader import EssayOCR, RubricEngine, AIGrader
    ocr = EssayOCR(api_key)
    text = ocr.ocr_image('bai_lam.jpg')
    grader = AIGrader(api_key)
    result = grader.grade_essay(text, model_answer, rubric)
"""
import os
import sys
import json
import base64
import requests

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

import time
import re

class EssayOCR:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get('GEMINI_API_KEY')
        self.is_mock = not bool(self.api_key)
        self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.api_key}"
        
    def _encode_image(self, path: str) -> tuple[str, str]:
        ext = os.path.splitext(path)[1].lower()
        if ext in ['.jpg', '.jpeg']:
            mime = 'image/jpeg'
        elif ext == '.png':
            mime = 'image/png'
        elif ext == '.pdf':
            mime = 'application/pdf'
        else:
            mime = 'image/jpeg'
            
        with open(path, 'rb') as f:
            encoded = base64.b64encode(f.read()).decode('utf-8')
        return encoded, mime

    def _mock_ocr(self) -> dict:
        return {
            "text": "Gọi x là số sản phẩm. Ta có điều kiện x > 0.\nHàm chi phí là $C(x) = 100x + 5000$.\nDoanh thu là $R(x) = 200x$.\nLợi nhuận là $P(x) = R(x) - C(x) = 100x - 5000$.\nĐể hòa vốn thì P(x) = 0 suy ra x = 50.\nVậy cần sản xuất 50 sản phẩm.",
            "confidence": 0.95,
            "has_math": True,
            "error": None
        }

    def ocr_image(self, image_path: str) -> dict:
        if self.is_mock:
            return self._mock_ocr()
            
        try:
            encoded, mime = self._encode_image(image_path)
            payload = {
                "contents": [{
                    "parts": [
                        {"text": "Hãy đọc và ghi lại toàn bộ nội dung chữ viết trong ảnh này. Đây là bài làm môn học của học sinh. Giữ nguyên cấu trúc, công thức toán học (viết dạng LaTeX $...$), và bảng biểu. Không thêm nhận xét."},
                        {"inline_data": {"mime_type": mime, "data": encoded}}
                    ]
                }]
            }
            
            headers = {"Content-Type": "application/json"}
            resp = requests.post(self.api_url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            
            text = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
            has_math = "$" in text or "\\" in text
            return {
                "text": text,
                "confidence": 0.9,
                "has_math": has_math,
                "error": None
            }
        except Exception as e:
            return {"text": "", "confidence": 0.0, "has_math": False, "error": str(e)}

    def ocr_batch(self, image_paths: list) -> list:
        results = []
        for path in image_paths:
            results.append(self.ocr_image(path))
        return results

class RubricEngine:
    def __init__(self, subject='math'):
        self.subject = subject
        self.templates = self._load_templates()

    def _load_templates(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        rubric_path = os.path.join(base_dir, 'references', 'rubric_templates.json')
        if os.path.exists(rubric_path):
            with open(rubric_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def get_rubric(self, subject: str, question_type: str, total_points: float) -> dict:
        subject_rubrics = self.templates.get(subject, {})
        rubric = subject_rubrics.get(question_type)
        if not rubric:
            return {}
            
        scaled_rubric = dict(rubric)
        scaled_criteria = []
        for c in rubric.get("criteria", []):
            sc = dict(c)
            sc["max_score"] = round(c.get("weight", 0) * total_points, 2)
            scaled_criteria.append(sc)
            
        scaled_rubric["criteria"] = scaled_criteria
        scaled_rubric["total_points"] = total_points
        return scaled_rubric

    def load_custom_rubric(self, path_or_text: str) -> dict:
        try:
            if os.path.exists(path_or_text):
                with open(path_or_text, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return json.loads(path_or_text)
        except:
            return {}

    def create_auto_rubric(self, model_answer: str, total_points: float, subject: str) -> dict:
        return {
            "display": "Auto Generated Rubric",
            "criteria": [
                {"id": "auto_1", "name": "Nội dung chính", "max_score": total_points, "indicators": ["Đầy đủ ý"]}
            ],
            "total_points": total_points
        }

    def format_rubric_display(self, rubric: dict) -> str:
        if not rubric:
            return "Không có rubric."
        res = f"### Rubric: {rubric.get('display', 'Chưa rõ')}\n"
        res += f"**Tổng điểm:** {rubric.get('total_points', 0)}\n\n"
        for c in rubric.get('criteria', []):
            res += f"- **{c.get('name')}** ({c.get('max_score')}đ)\n"
            for ind in c.get('indicators', []):
                res += f"  - {ind}\n"
        return res

class AIGrader:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get('GEMINI_API_KEY')
        self.is_mock = not bool(self.api_key)
        self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key={self.api_key}"

    def _call_gemini(self, prompt: str) -> str:
        if self.is_mock:
            return json.dumps({
                "total_score": 3.5,
                "max_score": 5.0,
                "percentage": 70.0,
                "grade_suggestion": "Đạt",
                "breakdown": [
                  {
                    "criterion": "Lập mô hình toán học",
                    "score": 0.5, "max_score": 0.5,
                    "status": "full",
                    "comment": "Đặt biến và lập hàm mục tiêu đúng",
                    "detail": "Học sinh đặt x = số sản phẩm, lập đúng hàm P(x)..."
                  }
                ],
                "common_errors": ["Thiếu bước kiểm tra điều kiện", "Chưa phiên giải thực tiễn"],
                "strengths": ["Tính toán chính xác", "Trình bày rõ ràng"],
                "overall_comment": "Bài làm nắm vững phương pháp...",
                "improvement_suggestions": ["Cần bổ sung bước kết luận thực tiễn"],
                "gdpt2018_compliance": {
                  "has_real_world_conclusion": False,
                  "follows_4step_method": True,
                  "has_unit_check": True
                }
            })
            
        for attempt in range(3):
            try:
                payload = {
                    "contents": [{"parts": [{"text": prompt}]}]
                }
                headers = {"Content-Type": "application/json"}
                resp = requests.post(self.api_url, headers=headers, json=payload)
                resp.raise_for_status()
                data = resp.json()
                return data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
            except Exception as e:
                if attempt == 2:
                    return "{}"
                time.sleep(2)
        return "{}"

    def _parse_grading_json(self, raw: str) -> dict:
        try:
            match = re.search(r'```json\n(.*?)\n```', raw, re.DOTALL)
            if match:
                raw = match.group(1)
            return json.loads(raw)
        except:
            return {}

    def grade_essay(self, student_answer: str, model_answer: str, rubric: dict, subject: str = 'math') -> dict:
        prompt = f"""
Bạn là một giáo viên chuyên môn {subject} theo chuẩn GDPT 2018. Hãy chấm điểm bài làm của học sinh.

### Đáp án mẫu:
{model_answer}

### Rubric chấm điểm:
{json.dumps(rubric, ensure_ascii=False, indent=2)}

### Bài làm học sinh:
{student_answer}

### Yêu cầu:
Trả về KẾT QUẢ DƯỚI DẠNG JSON duy nhất như sau (không thêm text khác):
{{
  "total_score": float,
  "max_score": float,
  "percentage": float,
  "grade_suggestion": "str",
  "breakdown": [
    {{
      "criterion": "str",
      "score": float,
      "max_score": float,
      "status": "full/partial/none",
      "comment": "str",
      "detail": "str"
    }}
  ],
  "common_errors": ["str"],
  "strengths": ["str"],
  "overall_comment": "str",
  "improvement_suggestions": ["str"],
  "gdpt2018_compliance": {{
    "has_real_world_conclusion": bool,
    "follows_4step_method": bool,
    "has_unit_check": bool
  }}
}}
"""
        raw = self._call_gemini(prompt)
        return self._parse_grading_json(raw)

    def grade_batch(self, student_answers: list, model_answer: str, rubric: dict) -> list:
        return [self.grade_essay(ans, model_answer, rubric) for ans in student_answers]

    def generate_teacher_feedback(self, result: dict) -> str:
        res = "=== NHẬN XÉT CỦA GIÁO VIÊN ===\n"
        res += f"Điểm: {result.get('total_score')}/{result.get('max_score')}\n"
        res += f"Nhận xét chung: {result.get('overall_comment')}\n"
        res += "Điểm mạnh:\n" + "\n".join(f"- {s}" for s in result.get('strengths', [])) + "\n"
        res += "Lỗi thường gặp:\n" + "\n".join(f"- {e}" for e in result.get('common_errors', [])) + "\n"
        res += "Gợi ý cải thiện:\n" + "\n".join(f"- {i}" for i in result.get('improvement_suggestions', [])) + "\n"
        return res

if __name__ == '__main__':
    print("Testing EssayOCR Mock...")
    ocr = EssayOCR()
    print(ocr.ocr_image("dummy.jpg"))
    
    print("\nTesting RubricEngine...")
    engine = RubricEngine()
    print(engine.get_rubric("math", "tinh_toan_thuc_te", 5.0))
    
    print("\nTesting AIGrader Mock...")
    grader = AIGrader()
    res = grader.grade_essay("student_text", "model_text", {})
    print(json.dumps(res, indent=2, ensure_ascii=False))
