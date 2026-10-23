# Bước 7 — Chấm bài tự luận bằng AI

> Đọc khi giáo viên gửi ảnh bài làm / yêu cầu chấm bài, tạo rubric.
> *(Tài liệu tham chiếu của skill `tao-de-toan-tuong-tu` — được tách ra từ `SKILL.md` để SKILL.md gọn; nội dung quy tắc giữ nguyên.)*

---

## 🎓 Bước 7: Chấm Bài Tự Luận Bằng AI

> [!TIP]
> **Khi nào dùng:** Học sinh nộp bài chụp ảnh → AI đọc → chấm theo rubric GDPT 2018 → GV xác nhận điểm cuối cùng. Đặc biệt mạnh cho **Văn, Địa, KTPL, Sinh học**.

**Kích hoạt khi giáo viên nói:**
- *"chấm bài này"* + gửi ảnh → Tự động OCR + chấm
- *"chấm cả lớp"* + nhiều ảnh → Chấm hàng loạt + xuất Excel
- *"tạo rubric cho câu 3"* → Tự động tạo rubric từ đáp án

**Quy trình:**

```python
from scripts.essay_grader import EssayOCR, RubricEngine, AIGrader
from scripts.grading_report import GradingReport

api_key = os.getenv("GEMINI_API_KEY")   # Lấy từ env var

# 1. OCR ảnh bài làm học sinh
ocr = EssayOCR(api_key=api_key)
result = ocr.ocr_image("bai_lam_hs.jpg")
student_text = result["text"]

# 2. Lấy rubric (hoặc tự tạo từ đáp án)
rubric_engine = RubricEngine(subject="math")
rubric = rubric_engine.get_rubric("math", "tinh_toan_thuc_te", total_points=5.0)
# Hoặc tự tạo: rubric = rubric_engine.create_auto_rubric(model_answer, 5.0, "math")

# 3. Chấm điểm
grader = AIGrader(api_key=api_key)
grading = grader.grade_essay(
    student_answer=student_text,
    model_answer="[đáp án chuẩn]",
    rubric=rubric,
    subject="math"
)

# 4. Hiển thị kết quả cho GV xem + xác nhận
report = GradingReport([grading], subject="math")
print(report.to_chat_summary("Học sinh A"))

# 5. Xuất báo cáo (sau khi GV xác nhận điểm)
report.to_word_feedback("Học sinh A", "feedback_hs_a.docx")
report.to_excel([grading1, grading2, ...], "bang_diem_lop_10a.xlsx")
```

**Giao diện kết quả chấm trong chat:**

```
📊 KẾT QUẢ CHẤM — Câu 3 (5 điểm) — Học sinh: Nguyễn Văn A

✅ Lập mô hình toán học:     0.5/0.5  — Đặt biến x = số SP, lập đúng P(x)
⚠️  Giải toán học:            1.2/1.5  — Sai dấu bước tính f'(x) = 3x² - 3
✅ Kiểm tra điều kiện:        0.5/0.5  — Loại nghiệm âm, đúng miền
❌ Kết luận thực tiễn:        0.0/0.5  — Thiếu phiên giải ý nghĩa thực tế

🎯 Tổng AI gợi ý: 2.2/3.0 (73.3%) — Xếp loại: Đạt

💬 Điểm mạnh: Tính toán chính xác, trình bày rõ ràng
⚠️  Cần cải thiện: Bổ sung bước kết luận thực tiễn (bắt buộc GDPT 2018)

GV xác nhận điểm này không? [Enter] Đồng ý 2.2đ | [n] Nhập điểm khác
```

**Rubric có sẵn** (file `references/rubric_templates.json`):

| Môn | Loại câu tự luận |
|:----|:----------------|
| Toán | `tinh_toan_thuc_te`, `chung_minh` |
| Văn | `nghi_luan_xa_hoi`, `nghi_luan_van_hoc`, `doc_hieu` |
| Địa | `nhan_xet_bieu_do`, `giai_thich_hien_tuong` |
| KTPL | `tinh_huong_phap_luat`, `phan_tich_kinh_te` |
| Lý | `thi_nghiem`, `tinh_toan` |
| Hóa | `bao_toan`, `thi_nghiem_mo_ta` |
| Sinh | `lai_sinh_hoc`, `giai_thich_hien_tuong` |
| KHTN | `tich_hop_lien_mon` |

> [!IMPORTANT]
> **AI chỉ GỢI Ý điểm — GV quyết định cuối cùng.** Agent PHẢI hỏi GV xác nhận trước khi lưu điểm chính thức.
