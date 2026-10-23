# Bước 1 — Đọc đề gốc, chuyển PDF→Word không lỗi & chuẩn hóa công thức Word

> Đọc khi cần đọc PDF/DOCX/ảnh đề gốc, chuyển PDF sang Word (Hybrid Render v2), hoặc chuẩn hóa công thức file Word sang MathType OLE.
> *(Tài liệu tham chiếu của skill `tao-de-toan-tuong-tu` — được tách ra từ `SKILL.md` để SKILL.md gọn; nội dung quy tắc giữ nguyên.)*

---

> **Lưu ý quan trọng**:
> - DOCX do giáo viên soạn bằng MathType cũ → dùng `extract_latex_from_mathtype_docx()` để chuyển OLE về LaTeX trước khi phân tích.
> - Ảnh chụp đề thi bằng điện thoại (PNG/JPG) → dùng `ocr_image_to_latex()` để nhận diện công thức bằng Mistral AI Vision.

**Ví dụ sử dụng:**
```python
from scripts.docx_reader import read_exam_source, extract_latex_from_mathtype_docx, ocr_image_to_latex

# 1. Đọc file PDF đề thi
content = read_exam_source("de_toan_12.pdf")

# 2. Đọc DOCX có MathType OLE → lấy LaTeX
content = extract_latex_from_mathtype_docx("de_cu_mathtype.docx")

# 3. OCR ảnh chụp đề thi bằng Mistral AI
result = ocr_image_to_latex(["de_thi_scan.jpg", "de_thi_scan_2.jpg"])

# 4. Tự động nhận diện
content = read_exam_source("de_goc.docx", is_mathtype_docx=True)
```

---

### 🔄 Bước 1.2: Chuyển Đổi PDF Sang Word Không Lỗi (Hybrid Render v2 — Chống Xô Lệch Bảng Biểu & Hình Ảnh)

> [!TIP]
> **Khi nào dùng:** Giáo viên gửi file PDF đề thi, kế hoạch bài dạy (KHBD), tài liệu chuyên môn và yêu cầu:
> *"chuyển pdf sang word"*, *"convert pdf to word mathtype"*, *"chuyển pdf sang word không lỗi bảng biểu"*, *"chuyển đề thi pdf sang word mathtype ole"*, *"chuyển kế hoạch bài dạy sang word"*.

#### Chiến lược Hybrid Render v2:
1. **Bảng biểu (Table Grid) chống xô lệch 100%**: Thay vì trích xuất text bảng làm mất viền, xô lệch hàng cột hay tràn lề, hệ thống tự động render vùng bảng thành ảnh **300 DPI** sắc nét từ chính file PDF gốc. Bảng giữ nguyên 100% bố cục, màu sắc, viền kẻ, không bao giờ lệch trang.
2. **Hình ảnh kỹ thuật & thí nghiệm**: Tự động crop trực tiếp từ trang PDF render 300 DPI tại đúng tọa độ `bbox`, bảo toàn 100% độ sắc nét khi in ấn.
3. **Văn bản & Tiêu đề**: Trích xuất text theo thứ tự đọc tự nhiên từ trên xuống dưới (sort theo tọa độ $y_0$), tự động phân tầng tiêu đề Heading 1 (14pt bold), Heading 2 (12pt bold) và nội dung (Times New Roman 12pt).
4. **Công thức Toán / Ký hiệu Hóa**: Bọc mã LaTeX và tự động gửi Backend Converter API (`https://latex2mathtypeweb.onrender.com/api/convert-docx`) để xuất đối tượng **MathType OLE (`Equation.DSMT4`)** nhấp đúp mở sửa ngay trong Word, kèm bản Word Equation (`_WORD_EQ.docx`) dự phòng.

#### Lệnh thực thi nhanh:
```python
from scripts.pdf_to_word_v2 import convert_pdf_to_word

# Chuyển đổi 1-click
result = convert_pdf_to_word(
    pdf_path="D:/duong_dan/de_thi.pdf",
    out_dir="D:/duong_dan/thu_muc_xuat",
    table_as_image=True  # Giữ bảng 300 DPI chống xô lệch
)

# File xuất ra:
# 📄 <tên_file>_MATHTYPE_OLE.docx (Công thức MathType OLE xịn)
# 📄 <tên_file>_WORD_EQ.docx     (Bản dự phòng Word Equation)
# 🖼️ <tên_file>_imgs/            (Thư mục chứa toàn bộ hình ảnh)
```

Hoặc chạy dòng lệnh terminal:
```powershell
python scripts/pdf_to_word_v2.py "D:\duong_dan\de_thi.pdf" "D:\duong_dan\xuat"
```

---

### 📐 Bước 1.3: Chuẩn Hóa Công Thức File Word Sang MathType OLE 100% (Bảo Toàn Tuyệt Đối Bố Cục & Hình Thức)

> [!TIP]
> **Khi nào dùng:** Giáo viên đã có một file Word được căn chỉnh lề, định dạng font, kẻ bảng biểu, chèn hình ảnh rất đẹp mắt nhưng:
> - Công thức toán học bị lỗi, bị nhảy dòng, hoặc lẫn lộn giữa **Word Equation (OMML)** và **LaTeX**.
> - Giáo viên muốn toàn bộ công thức trong bài trở thành **MathType OLE (`Equation.DSMT4` / `DSMT6`) 14pt** để nhấp đúp (double-click) mở cửa sổ MathType 6/7 chỉnh sửa trực tiếp.
> - **YÊU CẦU SỐNG CÒN**: Giữ nguyên 100% bố cục, hình ảnh, bảng biểu (gộp ô, màu sắc, viền kẻ), header/footer, khoảng cách dòng của file Word gốc.

#### Cơ chế Dual-Pass Engine (Bảo toàn 100% cấu trúc OOXML):
1. **Tiền xử lý thông minh**: Quét trực tiếp `word/document.xml`, chuẩn hóa các cú pháp LaTeX (`\[...\]` → `$$...$$`, `\(...\)` → `$...$`, thay `\implies` bằng `\Rightarrow`, `\iff` bằng `\Leftrightarrow`). Giữ nguyên 100% các thẻ định dạng `<w:pPr>`, `<w:rPr>`, bảng `<w:tbl>`, hình ảnh `<w:drawing>`.
2. **Pass 1 — LaTeX sang MathType OLE**: Gửi file DOCX lên Backend Converter Server (`https://latex2mathtypeweb.onrender.com/api/convert-docx`) để biên dịch toàn bộ các công thức LaTeX `$LaTeX$` thành đối tượng MathType OLE (`Equation.DSMT4`, cỡ 14pt chuẩn SGK).
3. **Pass 2 — Word Equation (OMML) sang MathType OLE**: Tự động kích hoạt module `omml_converter` quét toàn bộ các công thức `<m:oMath>` / `<m:oMathPara>` còn sót lại trong tài liệu và chuyển đổi trực tiếp thành MathType OLE (`Equation.DSMT6`). Hệ thống tự động kiểm tra và đánh số tránh xung đột tệp nhúng (`word/embeddings/oleObjectN.bin`).
4. **Kiểm định tính toàn vẹn (Integrity Audit)**: Kiểm tra số lượng OLE object sau khi xuất bản để báo cáo chính xác cho giáo viên.

#### Lệnh thực thi 1-Click (Python & CLI):
```python
from scripts.standardize_word_mathtype import standardize_doc_to_mathtype

# Chuẩn hóa 1-click giữ nguyên 100% bố cục
result = standardize_doc_to_mathtype(
    input_path="C:/duong_dan/de_thi_da_chinh_dep.docx",
    output_path="C:/duong_dan/de_thi_da_chinh_dep_MATHTYPE_OLE.docx"  # (Tùy chọn, mặc định tự tạo hậu tố)
)
print(f"Đã chuẩn hóa {result['ole_count']} công thức MathType OLE thành công!")
```

Hoặc chạy dòng lệnh PowerShell:
```powershell
python scripts/standardize_word_mathtype.py "C:\duong_dan\de_thi_da_chinh_dep.docx"
```

#### 💡 Mẹo Thao Tác Trực Tiếp Trong Microsoft Word (3 Cú Click):
Nếu giáo viên muốn chuyển đổi trực tiếp ngay trên máy tính đã cài đặt Word và MathType:
1. Mở file Word cần chuẩn hóa.
2. Trên thanh công cụ (Ribbon), chọn thẻ **MathType**.
3. Bấm vào nút **Convert Equations** (Chuyển đổi công thức).
4. Tại hộp thoại hiện ra, tích chọn cả 2 mục:
   - ✅ **Microsoft Word 2007 and later (OMML) equations**
   - ✅ **TeX code** (với delimiter `$...$` hoặc `$$...$$`)
5. Bấm nút **Convert**. Toàn bộ công thức trong tài liệu sẽ tự động chuyển thành MathType OLE trong vài giây mà không xê dịch một milimet bố cục nào!

---

2. Sau khi có nội dung đề gốc, trích xuất toàn bộ câu hỏi theo **cấu trúc GDPT 2018** (áp dụng cho tất cả 8 môn, lớp 6–12):


   **Các phần trắc nghiệm (Toán / Vật Lý / Hóa Học / Sinh Học / KHTN / Địa Lý / KTPL):**
   - **Phần I**: Trắc nghiệm 4 lựa chọn A/B/C/D (12 câu THPT; 16–20 câu THCS/KHTN).
   - **Phần II**: Trắc nghiệm **Đúng/Sai** (4 câu THPT; 2–4 câu THCS) — mỗi câu gồm **4 ý a, b, c, d** theo thứ tự mức độ NB→TH→VD→VDC. Thang điểm: đúng 1 ý = 0,25đ; 2 ý = 0,5đ; 3 ý = 0,75đ; 4 ý = 1,0đ.
   - **Phần III**: Trắc nghiệm trả lời ngắn — điền số (6 câu THPT; 4–6 câu THCS). **Đáp án bắt buộc là số nguyên hoặc thập phân ≤ 2 chữ số**.
   - **Phần Tự luận** (đề kiểm tra học kỳ): bài toán thực tiễn, khảo sát hàm số, tình huống pháp luật, phân tích địa lý, bài nghị luận văn học. **Bắt buộc có bước phiên giải kết quả về thực tiễn**.

   **Môn Ngữ Văn (cấu trúc riêng — không có trắc nghiệm A/B/C/D):**
   - **Phần I — Đọc hiểu**: 1 ngữ liệu (văn bản văn học / nhật dụng), 4–6 câu hỏi theo 4 mức NB/TH/VD/VDC.
   - **Phần II — Viết**: 1 bài nghị luận xã hội + 1 bài nghị luận văn học.

   **Phân loại mức độ tư duy bắt buộc (GDPT 2018):**
   - **NB** (Nhận biết): ~30% tổng câu
   - **TH** (Thông hiểu): ~40% tổng câu
   - **VD** (Vận dụng): ~20% tổng câu
   - **VDC** (Vận dụng cao): ~10% tổng câu



---

## 📄 Tính Năng Chuyển Đổi PDF Đề Thi Sang Word Chuẩn Toán Học & Sư Phạm (Không Lỗi Công Thức, Hình Vẽ, Bảng Biểu)

Khi người dùng cung cấp một file đề thi định dạng **PDF** (kể cả file PDF scan hoặc ảnh chụp) và yêu cầu **chuyển sang Word**, Agent kích hoạt quy trình chuyển đổi chuyên dụng bảo đảm **100% không bị các lỗi kinh điển của công cụ thông thường**:

1. **Khắc phục lỗi công thức toán (MathType OLE 14pt)**:
   - Các công cụ thông thường (Adobe, SmallPDF, pdf2docx) biến công thức thành chuỗi text gãy nát, mất phân số, hỏng căn thức, vỡ ký hiệu tích phân/vectơ.
   - **Quy trình chuẩn**: Nhận diện ngữ nghĩa toán học đầy đủ sang cú pháp chuẩn LaTeX `$ ... $`, sau đó biên dịch qua Backend API thành **MathType OLE (`Equation.DSMT4`) nguyên bản**. Giáo viên mở file Word là click đúp sửa công thức mượt mà.
2. **Khắc phục lỗi hình vẽ minh họa**:
   - Trích xuất trực tiếp từ các trang PDF ở độ phân giải **300 DPI**, khử sạch viền thừa (`trim_whitespace`).
   - Tự động áp dụng **Bố cục 2 cột thông minh (Smart Side-by-Side)** cho các câu có đồ thị hàm số hoặc hình 3D đứng, giúp trang Word cực kỳ thoáng và tiết kiệm 35-45% giấy in.
3. **Khắc phục lỗi bảng biểu (Tables & Frequency Grids)**:
   - Bảng mẫu số liệu ghép nhóm thống kê, bảng phân bố tần số được chuyển thành **bảng Word chuẩn (`Table Grid`)**, có viền đầy đủ, căn giữa, số liệu các cột cân đối, không bao giờ bị vỡ khung hay biến dạng.
4. **Trọn bộ ấn phẩm xuất ra**:
   - `<TEN_DE>_MATHTYPE_OLE.docx`: Bản đề học sinh MathType OLE nguyên bản.
   - `<TEN_DE>_LOI_GIAI_OLE.docx`: Bản giáo viên có lời giải & đáp án chính thức từ Sở GD&ĐT.
   - `<TEN_DE>_WORD_EQ.docx`: Bản dự phòng Word Equation (OMML).

---
