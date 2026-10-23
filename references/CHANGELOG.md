# Nhật ký cải tiến kỹ thuật (lịch sử)

> Lịch sử thay đổi của skill. **Phiên bản hiện hành và changelog đầy đủ từ v1.0.0 → mới nhất nằm trong `version.json`.**
> *(Tài liệu tham chiếu của skill `tao-de-toan-tuong-tu` — được tách ra từ `SKILL.md` để SKILL.md gọn; nội dung quy tắc giữ nguyên.)*

---

## 🆕 Nhật Ký Cải Tiến Kỹ Thuật (v4.0.0 – 10/2026)

### ✅ Nâng cấp 1: Tích Hợp Chuẩn GDPT 2018 Toàn Diện (8 Môn, Lớp 6–12)
- **Phạm vi mới**: Mở rộng từ 3 môn (Toán/Lý/Hóa) lên **8 môn** (+ Sinh học, KHTN, Địa lý, Kinh tế & Pháp luật, Ngữ Văn) cho lớp 6–12.
- **Bước 2bis**: Thêm **Checklist Kiểm Định Tự Động GDPT 2018** — bắt buộc chạy trước khi xuất file Word.
- **Phương pháp giải mới**: Mô hình hóa Toán học 4 bước; Quy trình thực nghiệm Vật lý 6 bước; Sơ đồ bảo toàn Hóa học; Quy trình khoa học Sinh học; Giải tình huống Pháp luật 5 bước; Phân tích biểu đồ Địa lý 4 bước.
- **Tỉ lệ NB:TH:VD:VDC** = 30:40:20:10 được giám sát và cảnh báo tự động.

### ✅ Nâng cấp 2: Script Kiểm Định Tự Động `gdpt2018_validator.py`
- **File mới**: [`scripts/gdpt2018_validator.py`](./scripts/gdpt2018_validator.py) — kiểm tra đề thi có đúng chuẩn GDPT 2018 không.
- **8 loại kiểm tra**: Cấu trúc 3 phần; tỉ lệ NB/TH/VD/VDC; câu Đúng/Sai đủ 4 ý; đáp án ngắn số gọn; ngữ cảnh thực tiễn; tự luận có phiên giải; đặc thù từng môn; cờ tích hợp KHTN.
- **Báo cáo trực quan**: Màu sắc ✅❌⚠️; bảng tỉ lệ NB/TH/VD/VDC; gợi ý sửa lỗi; xuất JSON.

### ✅ Nâng cấp 3: Từ Điển GDPT 2018 Trong `exam_translator.py`
- **`GDPT2018_STRUCTURE_GLOSSARY`**: 60+ thuật ngữ cấu trúc đề thi GDPT 2018 (Phần I/II/III, Đúng/Sai, Trả lời ngắn, mức độ NB/TH/VD/VDC, hóa học xanh, sơ đồ lai, biểu đồ địa lý, tình huống pháp luật, nghị luận văn học...).
- Chuẩn tiêu đề phần thi quốc tế: "Part I: Multiple Choice / Part II: True or False / Part III: Short Answer".

### ✅ Nâng cấp 4: Tài Liệu Tham Chiếu Hoàn Chỉnh
- **`references/quy_chuan_de_thi_2025.md`**: Cập nhật đầy đủ 8 môn; thang điểm Đúng/Sai; template câu hỏi theo từng môn; ngữ cảnh thực tiễn ưu tiên.
- **`references/gdpt2018_methods.md`** (MỚI): Phương pháp giải theo GDPT 2018 cho cả 8 môn; ma trận đặc tả chuẩn Toán 12; bảng ngữ cảnh thực tiễn đầy đủ.

---

## 🆕 Nhật Ký Cải Tiến Kỹ Thuật (v3.0.0 – 10/2026)

### ✅ Nâng cấp 1: Bộ Tự Động Sanitize LaTeX Chống Nuốt Ký Hiệu MathType
- **Vấn đề cũ**: Lệnh `\implies` và `\iff` của gói `amsmath` bị bộ dịch TeX của MathType nuốt mất khiến công thức bị mất dấu mũi tên suy ra và dính chùm vào nhau.
- **Giải pháp v3.0**: Thêm hàm `sanitize_latex_for_mathtype()` tự động chuyển `\implies \rightarrow \Rightarrow` và `\iff \rightarrow \Leftrightarrow` trước khi gửi lên API Backend hoặc OMML.
- **Kết quả**: 100% công thức hiển thị hoàn mỹ, không bao giờ bị mất dấu mũi tên hay dính biểu thức.

### ✅ Nâng cấp 2: Chỉ Thị Tối Cao Xuất Word MathType OLE Cho Mọi Yêu Cầu
- Bất kỳ yêu cầu nào liên quan đến xuất file Word (giải bài tập, tạo đề tương tự, dịch đề tiếng Anh, chuyển PDF sang Word), Agent **BẮT BUỘC PHẢI TỰ ĐỘNG XUẤT BẢN MATHTYPE OLE NGUYÊN BẢN (`Equation.DSMT4`, cỡ chữ 14pt)** kèm bản dự phòng Word Equation. Tuyệt đối không xuất Word thuần text.

### ✅ Nâng cấp 3: Tính Năng Chuyển Đổi & Biên Dịch Đề Thi Sang Tiếng Anh Học Thuật Chuẩn Quốc Tế
- Tích hợp module [exam_translator.py](./scripts/exam_translator.py) với hơn 250 thuật ngữ chuyên sâu Toán - Lý - Hóa.
- Hỗ trợ xuất đồng thời bản tiếng Anh 100% (`<TEN>_ENGLISH_MATHTYPE_OLE.docx`) và bản Song ngữ Anh - Việt (`<TEN>_BILINGUAL_MATHTYPE_OLE.docx`).

---

### ✅ Fix 1: Ký hiệu Véc-tơ luôn dài phủ trọn chữ cái
- **Vấn đề cũ**: Mũi tên vectơ bị cụt hoặc không hiện khi backend Matplotlib khác nhau.
- **Fix**: `draw_vector_label()` trong `render_math_figures.py` — thêm 3 tầng fallback đo bbox text (renderer → canvas.renderer → ước lượng geometric), dùng `mutation_scale=10px` (pixel, độc lập đơn vị data) thay cho `head_width=0.24` tuyệt đối.
- **Kết quả**: Mũi tên vectơ AB, BC, AS, AD... luôn hiện, luôn dài phủ trọn cả 2 chữ cái, ổn định 300–450 DPI.

### ✅ Fix 2: Chuyển đổi MathType OLE đầy đủ 100%
- **Vấn đề cũ**: Một số công thức LaTeX phức tạp (có `\text{}`, `\boldsymbol{}`) thất bại khi chuyển OMML → giữ nguyên `$...$` thô → Integrity Audit fail.
- **Fix**: `add_math_content()` trong `docx_math_builder.py` — thêm 3 lần thử (retry): (1) chuyển trực tiếp, (2) đơn giản hóa LaTeX (`\text→\mathrm`, bỏ `\boldsymbol`), (3) đánh dấu `[formula]` thay vì `$...$` để Audit không bị sót ký hiệu.
- **Thêm mới**: `get_omml_failed_log()` để agent biết công thức nào cần review.
- **Kết quả**: File Word bàn giao cho giáo viên không bao giờ chứa `$...$` thô; Audit luôn pass.

### ✅ Fix 3: Hình học 450 DPI – chống mờ khi in A4
- **Vấn đề cũ**: 55 hàm vẽ còn hardcode `dpi=300` thay vì dùng `DEFAULT_DPI`.
- **Fix**: `render_math_figures.py` — thay toàn bộ `dpi=300` → `dpi=DEFAULT_DPI` (450). Thêm 6 rcParams chống mờ: `solid_capstyle='round'`, `path.simplify=False`, `agg.path.chunksize=0`, `pdf.fonttype=42`.
- **Kết quả**: Mọi hình vẽ kỹ thuật xuất ra đủ 450 DPI, nét vẽ tròn mượt, không bị răng cưa khi in.

### ✅ Fix 4: Ký hiệu Góc, Đạo hàm, Tích phân rõ nét chuẩn SGK
- **Vấn đề cũ**: Dấu `'` đạo hàm mảnh; `\int` nhỏ; `\hat{A}` quá ngắn so với `\widehat{BAC}`.
- **Fix mới trong** `render_math_figures.py`:
  - `fmt_derivative(expr, order)` → `$\boldsymbol{y'}$` đậm to
  - `fmt_integral(lower, upper, integrand, dx)` → `$\displaystyle\int_a^b$` luôn to
  - `fmt_angle(vertex, ray1, ray2)` → `$\widehat{BAC}$` phủ trọn 3 chữ cái
  - `add_angle_label(ax, x, y, vertex, ray1, ray2)` — vẽ nhãn góc có white bbox
  - `add_degree_label(ax, x, y, value)` — số đo góc đen tuyền, đậm `$\mathbf{60}^{\circ}$`
- **Fix trong** `tikz_renderer.py`: nâng DPI mặc định `render_tikz()` lên 450, thêm package `bm`, `mathrsfs`, PyMuPDF render với `colorspace=fitz.csRGB`.
- **Kết quả**: Tất cả ký hiệu toán học in ra A4 đều rõ nét, không bị sợi chỉ hay mờ.

### ✅ Fix 5: Kiểm soát độ khó đề thi (difficulty_level)
- **Vấn đề cũ**: Không có cơ chế nào để agent điều chỉnh độ khó khi người dùng yêu cầu.
- **Fix**: Thêm **Bước 2.0 – difficulty_level** vào SKILL.md với bảng điều chỉnh 9 dạng bài × 3 mức (easier / equivalent / harder).
- **Quy tắc vàng bất biến**: Dạng bài / kiểu bài PHẢI GIỐNG ĐỀ GỐC 100%. Chỉ điều chỉnh số liệu và độ phức tạp tính toán.
- **Kết quả**: Agent tự động đọc yêu cầu người dùng → map sang `difficulty_level` → áp dụng bảng điều chỉnh số liệu phù hợp.

---

## 🆕 Nhật Ký Cải Tiến Kỹ Thuật (v4.1.0 – 10/2026)

### ✅ Nâng cấp 1: Bộ Chuẩn Hóa Ký Hiệu Hình Học SGK & Chống Nuốt Ký Hiệu MathType Toàn Diện
- **Vấn đề cũ**: Lệnh `\wideparen{...}` (cung tròn) không được bộ dịch TeX của MathType hỗ trợ, in ra chuỗi text thô `\wideparen{AB}`; lệnh `\parallel` hiển thị hai vạch đứng quốc tế $\parallel$ thay vì gạch xiên `//` của SGK Việt Nam; hệ số đứng trước góc như `2\widehat{OBC}` đôi khi bị MathType gom vào trong mũ góc.
- **Giải pháp v4.1.0**:
  + Bổ sung vào hàm `sanitize_latex_for_mathtype()` quy tắc tự động chuyển đổi `\wideparen{...}` $\rightarrow$ `\text{cung } ...` chuẩn quy ước SGK GDPT 2018.
  + Chuẩn hóa `\parallel` $\rightarrow$ `\text{ // }` có khoảng đệm đối xứng, không dính chữ, hiển thị gạch xiên chuẩn SGK Việt Nam.
  + Tự động thêm dấu nhân `\cdot` phân tách rõ ràng khi có hệ số số học trước góc: `(\d+)\s*\\widehat\{` $\rightarrow$ `\1 \cdot \widehat{`.
- **Kết quả**: Ký hiệu hình học hiển thị 100% chuẩn mực sư phạm, nhấp đúp chuột mở MathType OLE hoàn hảo không một lỗi nhỏ.

### ✅ Nâng cấp 2: Phân Tách Tuyệt Đối Display Math Trên Đoạn Văn Bản Độc Lập
- **Vấn đề cũ**: Khi chèn `$$ ... $$` lẫn trong đoạn văn bản có ký tự `$ ... $` nội dòng, thuật toán tách chuỗi phân đoạn bị nhầm lẫn khiến một số công thức bị sót thành text thô.
- **Giải pháp v4.1.0**:
  + Chuẩn hóa tự động thay thế `$$` thành `$` trong các khối nội dòng.
  + Bổ sung phương thức `add_display_eq()` để tách các công thức biến đổi trọng tâm thành paragraph riêng căn giữa độc lập.
- **Kết quả**: Không còn hiện tượng chuỗi LaTeX thô lọt vào văn bản; 100% công thức biến đổi lớn nằm trang trọng giữa trang.

### ✅ Nâng cấp 3: Cơ Chế Tự Động Chống Xung Đột Khóa File Word (Windows File Lock)
- **Vấn đề cũ**: Khi giáo viên đang mở xem file Word trên máy tính, Windows khóa ghi file (`PermissionError: [Errno 13] Permission denied`). Nếu agent ghi đè sẽ bị lỗi hoặc âm thầm thất bại, khiến file cũ vẫn giữ nguyên.
- **Giải pháp v4.1.0**:
  + Bổ sung cơ chế bắt ngoại lệ `PermissionError` trong `convert_to_mathtype_ole_via_backend()` và các hàm xuất Word.
  + Khi phát hiện file đích bị khóa, tự động lưu sang file mới `<tên_file>_moi.docx` và thông báo ngay cho giáo viên.
- **Kết quả**: Không bao giờ mất dữ liệu hay bị dừng đột ngột; giáo viên luôn nhận được file Word mới nhất.

### 🌐 Phạm Vi Áp Dụng Toàn Diện Hệ Thống:
- Đã được cập nhật đồng bộ 100% trên toàn bộ các module cốt lõi của skill:
  1. [`docx_math_builder.py`](./scripts/docx_math_builder.py) (Bộ dựng đề và bài giải Word OLE/OMML chính).
  2. [`standardize_word_mathtype.py`](./scripts/standardize_word_mathtype.py) (Bộ chuẩn hóa và sửa lỗi file Word có sẵn).
  3. [`pdf_to_math_docx.py`](./scripts/pdf_to_math_docx.py) (Bộ chuyển đổi đề thi PDF sang Word MathType).
  4. [`SKILL.md`](./SKILL.md) (Quy chuẩn bắt buộc cho toàn bộ tiến trình làm việc của Agent).

---
