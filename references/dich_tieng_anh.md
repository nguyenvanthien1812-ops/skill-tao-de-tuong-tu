# Bước 6 — Biên dịch đề sang tiếng Anh học thuật & đề song ngữ

> Đọc khi giáo viên yêu cầu dịch đề / đề song ngữ.
> *(Tài liệu tham chiếu của skill `tao-de-toan-tuong-tu` — được tách ra từ `SKILL.md` để SKILL.md gọn; nội dung quy tắc giữ nguyên.)*

---

## 🌐 BƯỚC 6: CHUYỂN ĐỔI & BIÊN DỊCH ĐỀ THI SANG TIẾNG ANH HỌC THUẬT CHUẨN QUỐC TẾ (ACADEMIC ENGLISH & BILINGUAL EXAM CONVERTER)

Khi người dùng yêu cầu: *"chuyển đề sang tiếng anh"*, *"dịch đề sang tiếng anh"*, *"tạo đề song ngữ"*, *"xuất bản tiếng anh"*, *"translate exam to English"*, *"bilingual exam"*, *"dịch file sang tiếng anh"*:
Agent kích hoạt hệ thống biên dịch chuyên sâu [exam_translator.py](./scripts/exam_translator.py) với 2 chế độ xuất bản:

### 1. Hai Chế Độ Xuất Bản Quốc Tế:
- **Chế độ 1: Bản Tiếng Anh 100% (English-Only Exam)**:
  - Tên file: `<TEN_DE>_ENGLISH_MATHTYPE_OLE.docx` (kèm `<TEN_DE>_ENGLISH_WORD_EQ.docx`).
  - Phù hợp: Trường quốc tế, trường song ngữ, lớp chuyên Anh, ôn thi các kỳ thi quốc tế (AMC, Kangaroo, SASMO, ASMO, SAT Math, AP Calculus/Physics/Chemistry, IB, Cambridge IGCSE / A-Level).
- **Chế độ 2: Bản Song Ngữ Anh - Việt (Bilingual Exam)**:
  - Tên file: `<TEN_DE>_BILINGUAL_MATHTYPE_OLE.docx` (kèm `<TEN_DE>_BILINGUAL_WORD_EQ.docx`).
  - Cấu trúc: Câu hỏi tiếng Việt phía trên, câu hỏi tiếng Anh in nghiêng thanh lịch ngay bên dưới; hoặc bố cục 2 cột song ngữ đối xứng.

### 2. Tiêu Chuẩn Biên Dịch Ngữ Nghĩa Học Thuật:
- **Không dịch word-by-word máy móc**: Sử dụng chuẩn câu mệnh lệnh sư phạm quốc tế:
  * *"Cho tam giác ABC có ba góc nhọn nội tiếp (O; R)..."* $\rightarrow$ *"Let $\Delta ABC$ be an acute-angled triangle inscribed in $(O; R)$..."*
  * *"Chứng minh: Tứ giác AEHF nội tiếp và suy ra..."* $\rightarrow$ *"Prove that: Quadrilateral $AEHF$ is cyclic, and deduce that $\widehat{HEF} = \widehat{HCB}$."*
  * *"Tính độ dài CH theo R"* $\rightarrow$ *"Calculate the length of $CH$ in terms of $R$."*
  * *"Tìm giá trị lớn nhất / nhỏ nhất của..."* $\rightarrow$ *"Find the maximum / minimum value of..."*
  * *"Kẻ đường kính AK của (O)..."* $\rightarrow$ *"Draw the diameter $AK$ of $(O)$..."*
  * *"Tia KH cắt BC tại M và cắt (O) tại điểm thứ hai là N..."* $\rightarrow$ *"The ray $KH$ intersects $BC$ at $M$ and intersects $(O)$ at a second point $N$ ($N \neq K$)..."*
  * *"đpcm (điều phải chứng minh)"* $\rightarrow$ *"(Q.E.D.)"*
  * *"Bước 1 / Bước 2 / Bước 3"* $\rightarrow$ *"Step 1 / Step 2 / Step 3"*
  * *"Cách 1 / Cách 2"* $\rightarrow$ *"Method 1 / Method 2"*
  * *"Barem chấm điểm"* $\rightarrow$ *"Marking Scheme / Grading Rubric"*
- **Bảo toàn 100% công thức MathType OLE**: Toàn bộ công thức toán trong `$ ... $` được giữ nguyên vẹn và tự động làm sạch qua `sanitize_latex_for_mathtype` (luôn dùng `\Rightarrow`, `\Leftrightarrow`).
- **Bảo toàn 100% hình vẽ kỹ thuật**: Giữ nguyên hình vẽ 450 DPI có các nhãn điểm hình học quốc tế ($A, B, C, D, E, F, H, K, M, N, O$).

---
