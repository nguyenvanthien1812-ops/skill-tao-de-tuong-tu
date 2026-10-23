# Bước 0.5 — Lập Ma trận, Bản đặc tả & Ra đề từ Ma trận (chi tiết đầy đủ)

> BẮT BUỘC đọc trước khi lập Bảng Ma trận / Bản đặc tả hoặc ra đề theo ma trận. Chứa: 3 nhánh xử lý, quy tắc 1 mức độ = 1 dòng, dòng tổng kết, hàm `enforce_perfect_table_borders`, API `MatrixParser/ExamGenerator`.
> *(Tài liệu tham chiếu của skill `tao-de-toan-tuong-tu` — được tách ra từ `SKILL.md` để SKILL.md gọn; nội dung quy tắc giữ nguyên.)*

---

### 🆕 Bước 0.5: Thiết Lập Ma Trận & Tạo Đề Từ Ma Trận Đặc Tả

> [!TIP]
> **Khi nào dùng:** 
> 1. Giáo viên muốn lập Bảng Ma trận & Bản đặc tả chuẩn GDPT 2018 từ các tài liệu gốc (khi chưa có ma trận).
> 2. Giáo viên đã có sẵn file Ma trận đặc tả và muốn tạo đề thi mới hoàn toàn bám sát 100% ma trận này.
> 3. Giáo viên muốn dùng nhanh kho 8 ma trận chuẩn GDPT 2018 tích hợp sẵn trong hệ thống.

**Kích hoạt khi giáo viên nói:**
- *"chưa có ma trận đặc tả"*, *"tạo đề khi chưa có ma trận"*, *"hướng dẫn chuẩn bị ma trận"* → Kích hoạt **Nhánh 1: Lập Ma trận từ 5 tư liệu gốc**.
- *"tôi muốn tạo đề từ ma trận có sẵn"*, *"tạo đề theo ma trận này"* (kèm file Word/Excel/ảnh hoặc bảng chat) → Kích hoạt **Nhánh 2: Ra đề từ ma trận có sẵn**.
- *"tạo đề Toán 12, 90 phút"*, *"xuất ma trận Hóa 11"* → Kích hoạt **Nhánh 3: Dùng kho ma trận chuẩn GDPT 2018 mặc định**.

---

#### 📌 Nhánh 1: Khi Giáo Viên Chưa Có Ma Trận (Lập Ma Trận & Bản Đặc Tả Từ Thư Mục Tư Liệu)
1. **Đọc và đối chiếu toàn bộ tài liệu trong thư mục do giáo viên cung cấp:**
   - Đọc file **Kế hoạch dạy học / Phân phối chương trình (PPCT)** để đếm chính xác số tiết đã dạy đến thời điểm kiểm tra, xác định danh sách các bài học nằm trong phạm vi ra đề (nếu giáo viên lưu ý phần thực hành của bài cuối chưa học thì chỉ ra đề phần lý thuyết đã học).
   - Đọc file **Sách giáo khoa điện tử (PDF)** để nắm chính xác tên Chương / Chủ đề, các dạng bài tập, thuật ngữ, ký hiệu và ngữ cảnh đặc trưng của bộ sách đang dạy.
   - Đọc file **Cấu trúc ra đề** để xác định hình thức (TN 4 lựa chọn, TN Đúng/Sai, Trả lời ngắn, Tự luận), thời gian làm bài, tổng điểm và tỷ lệ mức độ nhận thức (chuẩn 40% Nhận biết – 30% Thông hiểu – 20% Vận dụng – 10% Vận dụng cao).
   - Đọc file **Chương trình GDPT 2018 môn học (PDF)** để trích xuất nguyên văn chuẩn xác 100% cột **"Yêu cầu cần đạt" (YCCĐ)** tương ứng với từng bài học và từng mức độ nhận thức.
   - Tham khảo file **Đề mẫu / Đề minh họa (nếu có)** để căn chỉnh độ dài câu hỏi và văn phong ra đề quen thuộc của trường/Sở.

2. **Quy tắc thiết lập Bảng Ma trận đề kiểm tra (Bảng 1 - Khung Ma trận):**
   - **Tên Chủ đề / Mạch kiến thức (Cột 1):** Lấy chuẩn xác 100% theo tên Chương / Chủ đề trong **Sách giáo khoa (SGK)** đang dùng (kèm tổng số tiết và tỉ lệ % thời lượng).
   - **Tên Nội dung / Đơn vị kiến thức (Cột 2):** Lấy chuẩn xác 100% theo tên bài trong **Kế hoạch dạy học / Phân phối chương trình (PPCT)** (kèm số tiết dạy của bài). Tuyệt đối không tự ý cắt xén, không để trống và không lặp lại sai lệch tên bài.
   - **Phân bổ số câu, số điểm:** Tỉ lệ thuận với số tiết dạy của từng bài học; phân bổ đúng các phần (Phần I: TN nhiều lựa chọn; Phần II: Đúng/Sai; Phần III: Trả lời ngắn [nếu có]; Phần Tự luận).
   - **⛔ BẮT BUỘC PHẢI CÓ ĐẦY ĐỦ 4 HÀNG TỔNG KẾT Ở CUỐI BẢNG MA TRẬN (TUYỆT ĐỐI KHÔNG ĐƯỢC THIẾU DÒNG CUỐI CÙNG CỦA BẢNG):**
     1. `TỔNG (Ý)`: Thống kê chi tiết số ý/lệnh hỏi theo từng cột B, H, VD, VDC của từng phần và tổng số lệnh hỏi (ví dụ: 31 ý hoặc 32 ý).
     2. `TỔNG SỐ CÂU`: Thống kê số câu của từng phần (ví dụ: Phần I: 16 câu | Phần II: 2 câu (8 ý) | Phần III: 4 câu | Phần IV: 3 câu | Tổng: 25 câu (31 ý)).
     3. `TỔNG ĐIỂM`: Điểm từng phần và tổng điểm theo 4 mức độ nhận thức (4,0 đ Biết | 3,0 đ Hiểu | 2,0 đ Vận dụng | 1,0 đ Vận dụng cao | Tổng: 10,0 đ).
     4. `TỈ LỆ %`: 40% Biết | 30% Hiểu | 20% Vận dụng | 10% Vận dụng cao | Tổng: 100%.

3. **QUY TẮC VÀNG THIẾT LẬP BẢN ĐẶC TẢ ĐỀ KIỂM TRA (Bảng 2 - Bản đặc tả chi tiết):**
   > [!IMPORTANT]
   > **1️⃣ QUY TẮC MỖI TỈ LỆ / MỨC ĐỘ NHẬN THỨC 1 DÒNG & CÂU HỎI TƯƠNG ỨNG Ở CÙNG DÒNG ĐÓ:**
   > - **Tách riêng cột `Mức độ đánh giá` và cột `Yêu cầu cần đạt`** thành 2 cột độc lập (tuyệt đối không gộp chung 2 cột này thành 1 cột).
   > - Tuyệt đối **KHÔNG gộp chung** các mức độ (`Nhận biết`, `Thông hiểu`, `Vận dụng`, `Vận dụng cao`) của cùng một bài học vào 1 hàng (row) hay 1 ô.
   > - **Mỗi mức độ nhận thức xuất hiện trong bài học đó bắt buộc phải chiếm 1 DÒNG ĐỘC LẬP (ROW RIÊNG)** trong bảng. Các cột `TT`, `Chủ đề / Mạch kiến thức` và `Nội dung / Đơn vị kiến thức (Tên bài học)` được gộp ô dọc (`vMerge`) qua các dòng mức độ nhận thức của bài học đó:
   >   + **Cột 1 (`TT`) & Cột 2 (`Chủ đề / Mạch kiến thức`):** Gộp dọc theo toàn bộ các dòng thuộc cùng một Chương / Chủ đề.
   >   + **Cột 3 (`Nội dung / Đơn vị kiến thức`):** Gộp dọc theo các dòng mức độ nhận thức thuộc cùng một Bài học (ví dụ: `Bài 2. Nguyên tử (5 tiết)` gộp dọc qua 3 dòng: `Nhận biết`, `Thông hiểu`, `Vận dụng`).
   >   + **Cột 4 (`Mức độ đánh giá`):** Mỗi dòng ghi đúng 1 mức độ: `Nhận biết` (in đậm, màu xanh `#005A9E`), `Thông hiểu` (in đậm, màu xanh `#005A9E`), `Vận dụng` (in đậm, màu cam đậm `#C55A11`), hoặc `Vận dụng cao` (in đậm, màu đỏ nâu `#9E1B1B`).
   >   + **Cột 5 (`Yêu cầu cần đạt`):** Trích xuất chuẩn xác YCCĐ từ Chương trình GDPT 2018 tương ứng đúng với mức độ nhận thức của dòng đó (dòng `Nhận biết` chỉ ghi YCCĐ Nhận biết; dòng `Thông hiểu` chỉ ghi YCCĐ Thông hiểu; dòng `Vận dụng` chỉ ghi YCCĐ Vận dụng).
   >   + **Các cột Số câu ở từng phần (`Phần I: B, H, VD`, `Phần II: B, H, VD`, `Phần III: B, H, VD`, `Tự luận: B, H, VD, VDC`):** Điền số lượng câu hỏi / lệnh hỏi vào **ĐÚNG DÒNG CỦA MỨC ĐỘ NHẬN THỨC ĐÓ**.
   >   + **Cột cuối cùng (`Câu hỏi trong đề`):** Ghi rõ mã định danh câu hỏi cụ thể trong đề thi tương ứng với mức độ nhận thức đó **Ở CÙNG DÒNG ĐÓ** (ví dụ: dòng `Nhận biết` ghi `C4, C5, C17a`; dòng `Thông hiểu` ghi `C20`; dòng `Vận dụng` ghi `C24a`).
   >
   > 📊 **Minh họa cấu trúc dòng chuẩn bắt buộc của Bản đặc tả:**
   > | TT | Chủ đề / Mạch kiến thức | Nội dung / Đơn vị kiến thức | Mức độ đánh giá | Yêu cầu cần đạt | Phần I (B) | Phần I (H) | Phần II (B) | Phần II (H) | Tự luận (VD) | Câu hỏi trong đề |
   > |:--:|:---|:---|:---:|:---|:--:|:--:|:--:|:--:|:--:|:--:|
   > | **2** *(gộp dọc)* | **Chất và sự biến đổi của chất** *(gộp dọc)* | **Bài 2. Nguyên tử (5 tiết)** *(gộp dọc 3 dòng)* | **Nhận biết** | - Nêu được mô hình nguyên tử...<br>- Xác định được các loại hạt... | 2 | | 1 | | | **C4, C5, C17a** |
   > | ↑ | ↑ | ↑ | **Thông hiểu** | - Tính được khối lượng xấp xỉ...<br>- Xác định được số hạt p, e, n... | | | | 1 | | **C20** |
   > | ↑ | ↑ | ↑ | **Vận dụng** | - Tính được số lượng từng loại hạt p, e, n trong nguyên tử... | | | | | 0.5* | **C24a** |
   > | ↑ | ↑ | **Bài 3. Nguyên tố hóa học (3 tiết)** *(gộp dọc 2 dòng)* | **Nhận biết** | - Phát biểu được khái niệm nguyên tố hóa học... | 1 | | 1 | | | **C6, C17b** |
   > | ↑ | ↑ | ↑ | **Thông hiểu** | - Viết đúng kí hiệu hóa học và gọi tên các nguyên tố... | | 1 | | | | **C7** |
   >
   > **2️⃣ ĐẦY ĐỦ CÁC HÀNG TỔNG KẾT BẮT BUỘC Ở CUỐI BẢN ĐẶC TẢ (TUYỆT ĐỐI KHÔNG ĐƯỢC THIẾU DÒNG CUỐI CÙNG):**
   >   1. `TỔNG (Ý)` / `TỔNG SỐ CÂU / LỆNH HỎI`: Điền số lượng câu/ý theo từng cột và tổng (ví dụ: 25 câu, 31 ý).
   >   2. `TỔNG ĐIỂM (10,0 ĐIỂM)`: 4,0 đ | 2,0 đ | 1,0 đ | 3,0 đ | 10,0 đ.
   >   3. `TỈ LỆ %`: 40% | 20% | 10% | 30% | 100%.
   >
   > **3️⃣ BẢNG CHỮ KÝ PHÊ DUYỆT (Bảng 3):** Đặt ngay dưới Bản đặc tả gồm 3 cột phân định thẩm quyền:
   >   * Cột 1: *HIỆU TRƯỞNG / BGH DUYỆT* (Ký, đóng dấu và phê duyệt).
   >   * Cột 2: *TỔ TRƯỞNG CHUYÊN MÔN* (Ký và ghi rõ họ tên).
   >   * Cột 3: *NGƯỜI LẬP MA TRẬN & ĐẶC TẢ* (Ký và ghi rõ họ tên kèm ngày tháng năm).

4. **QUY TẮC KỸ THUẬT BẮT BUỘC: VẼ BẢNG WORD CHỐNG MẤT NÉT VIỀN 100% (`enforce_perfect_table_borders`):**
   > [!WARNING]
   > **NGUYÊN NHÂN LỖI MẤT NÉT KẺ BẢNG TRONG `python-docx` VÀ CÁCH KHẮC PHỤC TRIỆT ĐỂ:**
   > - Trong `python-docx`, khi gộp ô dọc bằng `cell_top.merge(cell_bottom)`, lệnh truy cập `table.rows[r].cells[c]` ở các dòng bị gộp (`Row 1, Row 2` của tiêu đề hoặc các dòng gộp của `TT`, `Chủ đề`, `Bài học`) sẽ **trả về ô gốc phía trên (`vMerge="restart"`)** chứ KHÔNG trả về phần tử XML `<w:tc>` thực sự tại dòng đó (`<w:vMerge/>`).
   > - Do đó, nếu chỉ lặp `for row in table.rows: for cell in row.cells:` để gắn `<w:tcBorders>` và màu nền `<w:shd>`, các phần tử `<w:tc>` có `<w:vMerge/>` sẽ bị **bỏ trống hoàn toàn `<w:tcBorders>` và `<w:shd>`**, dẫn đến khi mở trong Microsoft Word sẽ bị **mất đường kẻ dọc, mất đường kẻ ngang và mất màu nền ở giữa các ô gộp tiêu đề**!
   > - Ngoài ra, nếu không gắn `<w:cantSplit/>` cho từng dòng `<w:tr>`, khi bảng tràn sang trang mới giữa chừng một dòng, Word sẽ cắt đôi dòng và làm mất nét kẻ ngang cuối trang.
   >
   > **✅ GIẢI PHÁP BẮT BUỘC (Agent phải gọi hàm `enforce_perfect_table_borders(table, header_rows=3)` sau khi hoàn tất `.merge()` trên mọi bảng Ma trận & Bản đặc tả):**
   ```python
   from docx.oxml import parse_xml, OxmlElement
   from docx.oxml.ns import qn

   def enforce_perfect_table_borders(table, header_rows=3, border_color="000000", border_sz="4"):
       """
       Đảm bảo 100% bảng Word (kể cả mọi ô gộp dọc vMerge và gộp ngang gridSpan)
       có đầy đủ đường kẻ viền 4 cạnh sắc nét, đồng bộ màu nền ô gộp,
       không bị cắt đứt dòng khi qua trang (cantSplit) và lặp lại tiêu đề bảng (tblHeader).
       """
       tblPr = table._tbl.tblPr
       # 1. Thiết lập tblBorders ở cấp toàn bảng
       old_borders = tblPr.find(qn('w:tblBorders'))
       if old_borders is not None:
           tblPr.remove(old_borders)
       tblPr.append(parse_xml(
           f'<w:tblBorders xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
           f'<w:top w:val="single" w:sz="{border_sz}" w:space="0" w:color="{border_color}"/>'
           f'<w:left w:val="single" w:sz="{border_sz}" w:space="0" w:color="{border_color}"/>'
           f'<w:bottom w:val="single" w:sz="{border_sz}" w:space="0" w:color="{border_color}"/>'
           f'<w:right w:val="single" w:sz="{border_sz}" w:space="0" w:color="{border_color}"/>'
           f'<w:insideH w:val="single" w:sz="{border_sz}" w:space="0" w:color="{border_color}"/>'
           f'<w:insideV w:val="single" w:sz="{border_sz}" w:space="0" w:color="{border_color}"/>'
           f'</w:tblBorders>'
       ))

       # 2. Duyệt trực tiếp qua mọi phần tử XML <w:tr> và <w:tc> (bao gồm cả các ô vMerge bị ẩn)
       col_active_fill = {}
       for r_idx, tr in enumerate(table._tbl.tr_lst):
           trPr = tr.get_or_add_trPr()
           # Chống cắt đôi dòng khi ngắt trang
           if trPr.find(qn('w:cantSplit')) is None:
               trPr.append(OxmlElement('w:cantSplit'))
           # Lặp lại tiêu đề bảng khi sang trang mới
           if r_idx < header_rows and trPr.find(qn('w:tblHeader')) is None:
               trPr.append(OxmlElement('w:tblHeader'))

           grid_col = 0
           for tc in tr.tc_lst:
               tcPr = tc.get_or_add_tcPr()
               gridSpan_el = tcPr.find(qn('w:gridSpan'))
               span = int(gridSpan_el.get(qn('w:val'))) if gridSpan_el is not None else 1

               # Gắn tcBorders đủ 4 cạnh cho TẤT CẢ các <w:tc> (kể cả ô vMerge continue)
               for old_b in tcPr.findall(qn('w:tcBorders')):
                   tcPr.remove(old_b)
               tcPr.append(parse_xml(
                   f'<w:tcBorders xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
                   f'<w:top w:val="single" w:sz="{border_sz}" w:space="0" w:color="{border_color}"/>'
                   f'<w:left w:val="single" w:sz="{border_sz}" w:space="0" w:color="{border_color}"/>'
                   f'<w:bottom w:val="single" w:sz="{border_sz}" w:space="0" w:color="{border_color}"/>'
                   f'<w:right w:val="single" w:sz="{border_sz}" w:space="0" w:color="{border_color}"/>'
                   f'</w:tcBorders>'
               ))

               # Đồng bộ màu nền <w:shd> từ ô vMerge="restart" xuống các ô vMerge bên dưới
               vMerge_el = tcPr.find(qn('w:vMerge'))
               shd_el = tcPr.find(qn('w:shd'))
               if vMerge_el is not None:
                   vm_val = vMerge_el.get(qn('w:val'))
                   if vm_val == 'restart':
                       fill_color = shd_el.get(qn('w:fill')) if shd_el is not None else None
                       for c_i in range(grid_col, grid_col + span):
                           col_active_fill[c_i] = fill_color
                   else:
                       inherit_fill = col_active_fill.get(grid_col)
                       if inherit_fill and shd_el is None:
                           tcPr.append(parse_xml(
                               f'<w:shd xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
                               f'w:val="clear" w:color="auto" w:fill="{inherit_fill}"/>'
                           ))
               else:
                   for c_i in range(grid_col, grid_col + span):
                       col_active_fill.pop(c_i, None)

               grid_col += span
   ```

5. **Thể thức xuất file Word (.docx) nộp tổ chuyên môn & Quy trình tạo Bộ hồ sơ kiểm tra hoàn chỉnh:**
   - **Khổ giấy Landscape (ngang A4):** Bắt buộc dùng khổ ngang để bảng 18-21 cột hiển thị thông thoáng, không co ép chữ hay tràn lề.
   - **Căn lề văn bản hành chính:** Trên 1.5–2cm, Dưới 1.5–2cm, Phải 1.5–2cm, Trái 2–2.5cm. Font chữ `Times New Roman` đồng nhất.
   - **Khi tạo cả Đề thi từ ma trận vừa lập:** Tự động đối chiếu chéo 4 chiều (`Khung Ma trận` <-> `Bản đặc tả` <-> `Đề kiểm tra` <-> `Hướng dẫn chấm`) để đảm bảo khớp 100% số câu, mã câu, mức độ nhận thức và thang điểm.

---

#### 📌 Nhánh 2: Khi Giáo Viên Đã Có Sẵn Ma Trận (Ra Đề Thi Hoàn Chỉnh Bám Sát Ma Trận)
1. **Parse ma trận đặc tả (tự động nhận diện định dạng):**

```python
from scripts.exam_from_matrix import MatrixParser, ExamGenerator, ReviewInterface

# 1. Parse ma trận (tự động nhận diện định dạng)
parser = MatrixParser()

# Từ bảng trong chat (Markdown)
matrix = parser.from_text(user_message)

# Từ file Excel/Word đính kèm
matrix = parser.from_excel("ma_tran.xlsx")   # hoặc from_docx("ma_tran.docx")

# Chỉ nói tên môn → dùng ma trận mặc định
matrix = parser.get_default(subject="math", grade=12, duration_minutes=90)
matrix = parser.from_natural_language("tạo đề Toán 12, 90 phút, khó hơn một chút")

# 2. Sinh câu hỏi theo từng ô ma trận
generator = ExamGenerator(subject=matrix["subject"], grade=matrix["grade"])

# Sinh + review từng câu (GV xem và quyết định giữ/sinh lại/bỏ)
exam_data = generator.generate_full_exam(matrix, review_mode=True)

# 3. Kiểm định chuẩn GDPT 2018
from scripts.gdpt2018_validator import validate_exam_gdpt2018
result = validate_exam_gdpt2018(exam_data, subject=matrix["subject"])
```

**Giao diện Review Từng Câu (GV không cần biết lệnh — Agent xử lý):**

```
🔄 Đang sinh câu 1/12 — Hàm số bậc ba [VD] ...

📝 CÂU 1 [VD — Hàm số & đồ thị]:
   Cho hàm số $y = x^3 - 3x + 2$. Mệnh đề nào sau đây ĐÚNG?
   A. Hàm số đồng biến trên $(-1; 1)$
   B. Hàm số có giá trị cực đại bằng 4         ← Đáp án đúng
   C. Hàm số không có điểm cực trị
   D. Hàm số luôn đồng biến trên $\mathbb{R}$
   ✅ Ngữ cảnh thực tiễn: Không | Mức: VD

👉 [Enter] Giữ lại  |  [r] Sinh lại câu này  |  [e] Sửa thủ công  |  [s] Bỏ qua
```

**Ma trận mặc định có sẵn** (file `references/default_matrices.json`):

| Khóa | Môn | Lớp | Thời gian |
|:-----|:----|:----|:---------|
| `math_12_thpt_90min` | Toán | 12 | 90 phút |
| `physics_12_thpt_90min` | Vật Lý | 12 | 90 phút |
| `chemistry_11_thpt_90min` | Hóa Học | 11 | 90 phút |
| `chemistry_12_thpt_90min` | Hóa Học | 12 | 90 phút |
| `biology_12_thpt_90min` | Sinh Học | 12 | 90 phút |
| `khtn_8_thcs_45min` | KHTN | 8 | 45 phút |
| `geography_12_thpt_90min` | Địa Lý | 12 | 90 phút |
| `literature_12_thpt_90min` | Ngữ Văn | 12 | 90 phút |

🖼️ **Bộ ảnh trực quan hiển thị ma trận (cho GV xem và chọn ngay):**
- [Xem Poster Tổng Mục 8 Ma Trận](file:///d:/skill-quan-trong/.agents/skills/tao-de-toan-tuong-tu/references/matrix_previews/DANH_MUC_8_MA_TRAN_CHUAN.png)
- [Chi tiết Ma Trận Toán 12](file:///d:/skill-quan-trong/.agents/skills/tao-de-toan-tuong-tu/references/matrix_previews/math_12_thpt_90min.png)
- [Chi tiết Ma Trận Vật Lý 12](file:///d:/skill-quan-trong/.agents/skills/tao-de-toan-tuong-tu/references/matrix_previews/physics_12_thpt_90min.png)
- [Chi tiết Ma Trận Hóa Học 12](file:///d:/skill-quan-trong/.agents/skills/tao-de-toan-tuong-tu/references/matrix_previews/chemistry_12_thpt_90min.png)
- [Chi tiết Ma Trận Hóa Học 11](file:///d:/skill-quan-trong/.agents/skills/tao-de-toan-tuong-tu/references/matrix_previews/chemistry_11_thpt_90min.png)
- [Chi tiết Ma Trận Sinh Học 12](file:///d:/skill-quan-trong/.agents/skills/tao-de-toan-tuong-tu/references/matrix_previews/biology_12_thpt_90min.png)
- [Chi tiết Ma Trận KHTN 8](file:///d:/skill-quan-trong/.agents/skills/tao-de-toan-tuong-tu/references/matrix_previews/khtn_8_thcs_45min.png)
- [Chi tiết Ma Trận Địa Lý 12](file:///d:/skill-quan-trong/.agents/skills/tao-de-toan-tuong-tu/references/matrix_previews/geography_12_thpt_90min.png)
- [Chi tiết Ma Trận Ngữ Văn 12](file:///d:/skill-quan-trong/.agents/skills/tao-de-toan-tuong-tu/references/matrix_previews/literature_12_thpt_90min.png)

---


> **Lưu ý tỉ lệ nhận thức:** tỉ lệ 40% NB – 30% TH – 20% VD – 10% VDC là khung ma trận đề học kỳ THCS theo *cấu trúc ra đề của nhà trường*. Bảng `difficulty_level` ở `thiet_ke_va_kiem_dinh.md` (equivalent ≈ 30/40/20/10) chỉ áp dụng khi *tạo đề tương tự từ đề gốc*; khi ra đề theo Ma trận thì **luôn bám tỉ lệ trong Ma trận**.
