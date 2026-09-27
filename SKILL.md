---
name: tao-de-toan-tuong-tu
description: >-
  Tạo đề thi hoặc đề kiểm tra môn TOÁN và môn VẬT LÝ (KHTN lớp 6-12) tương tự (song song, cùng ma trận đặc tả) từ một đề gốc cho trước.
  Tự động phân tích đề gốc (từ file PDF, Word DOCX hoặc ảnh chụp), thiết kế bộ số liệu mới nghiệm đẹp & chuẩn xác định luật vật lý/toán học,
  lập trình vẽ 100% hình vẽ kỹ thuật (đồ thị hàm số, bảng biến thiên, hình không gian, sơ đồ mạch điện, thấu kính quang học, đồ thị dao động/sóng, phân tích vectơ lực)
  chuẩn xác tuyệt đối bằng Python Matplotlib (300 DPI), và tự động kết nối Backend Converter API (https://latex2mathtypeweb.onrender.com/api/convert-docx)
  để xuất trực tiếp file Word (.docx) chứa đối tượng MathType OLE nguyên bản (Equation.DSMT4) mở click đúp sửa ngay,
  kèm cơ chế Smart Fallback sang bản Word Equation (OMML) chuẩn SGK.
  Tích hợp sẵn tính năng tự động chẩn đoán và cài đặt môi trường 1-click cho giáo viên.
  Hỗ trợ xuất đồng thời bản Đề Học Sinh và bản Lời Giải Chi Tiết riêng biệt.
  Tự động tạo bộ 4 mã đề hoán vị kèm phiếu trả lời bong bóng (bubble sheet) chuẩn A4 chụp ảnh chấm thi và file Excel tổng hợp đáp án.
  Kích hoạt khi người dùng yêu cầu: "tạo đề tương tự", "tạo đề tương tự từ đề gốc", "nhân bản đề thi Toán", "tạo đề vật lý tương tự",
  "tạo đề thi môn lý", "nhân bản đề thi vật lý", "tạo đề KHTN", "tạo mã đề song song có hình vẽ và công thức chuẩn",
  "xuất đề thi mathtype ole", "cài đặt môi trường", "cài đặt thư viện", "setup máy tạo đề", "kiểm tra môi trường", "tạo bộ 4 mã đề", "tạo phiếu trả lời".
---

# Quy Trình Tạo Đề Toán & Vật Lý Tương Tự Chuẩn Bộ GD&ĐT (Tích Hợp Backend MathType OLE & Cài Đặt 1-Click)

Skill này tự động hóa toàn bộ quy trình biên soạn đề kiểm tra / đề thi môn **TOÁN** và môn **VẬT LÝ** (cấp THCS lớp 6, 7, 8, 9 và THPT lớp 10, 11, 12 theo định dạng mới GDPT 2018), bảo đảm **3 tiêu chuẩn vàng**:
1. **Khoa học chuẩn xác 100%**: Nghiệm đẹp, tham số logic, tuân thủ đúng định luật vật lý và toán học (không bị hiện tượng vô lý), 4 phương án trắc nghiệm chỉ có duy nhất 1 phương án đúng, lời giải chi tiết từng bước.
2. **Hình vẽ kỹ thuật 300 DPI chuẩn mực**: Vẽ bằng code Python Matplotlib:
   - **Môn Toán**: Đồ thị hàm số, bảng biến thiên, hình học không gian.
   - **Môn Vật lý**: Đường truyền tia sáng & thấu kính, đồ thị dao động điều hòa/sóng cơ ($x-t, v-t, u-t$), sơ đồ mạch điện, giản đồ vectơ Fresnel, phân tích vectơ lực trên mặt phẳng nghiêng, đồ thị biến thiên nhiệt/khí lý tưởng $(p-V, p-T)$.
3. **Công thức chuẩn MathType OLE & Word Equation**:
   - Sử dụng **Backend Converter API** (`https://latex2mathtypeweb.onrender.com/api/convert-docx`) để biên dịch 100% công thức thành **MathType OLE (`Equation.DSMT4`)** nhúng nhị phân MTEF `.bin` + vector `.wmf` trực tiếp vào file Word. Giáo viên click đúp vào bất kỳ công thức nào là mở cửa sổ MathType truyền thống ngay lập tức!
   - Kèm cơ chế **Smart Fallback**: Luôn sinh thêm bản **Word Equation (OMML)** để mở được mượt mà trên mọi máy tính kể cả khi không cài MathType.

---

## 🔐 Bước 0: Kiểm Tra License (BẮT BUỘC – Làm Trước Mọi Thứ)

**Agent PHẢI chạy lệnh này đầu tiên, trước khi thực hiện bất kỳ yêu cầu tạo đề nào:**

```bash
python scripts/license_manager.py --check
```

- Nếu kết quả là `✅ HỢP LỆ` → tiếp tục bình thường.
- Nếu kết quả là `❌ KHÔNG HỢP LỆ` hoặc `Chưa kích hoạt` → **DỪNG HOÀN TOÀN**, không làm gì thêm, và hướng dẫn người dùng:
  1. Chạy `python scripts/license_manager.py --machine-id` để lấy Machine ID.
  2. Gửi Machine ID cho tác giả để được cấp license key.
  3. Kích hoạt: `python scripts/license_manager.py --activate <KEY>`.

> Nếu người dùng hỏi "Kiểm tra license", "Kích hoạt license", "Lấy Machine ID" → thực thi lệnh tương ứng ngay.

---

## 🛠️ Chế Độ Tự Phục Hồi & Cài Đặt Môi Trường Cho Giáo Viên

Để đảm bảo giáo viên không cần có kiến thức kỹ thuật về lập trình hay terminal:

1. **Nút Bấm 1-Click (`cai_dat_tu_dong.bat`)**:
   - File batch được đóng gói sẵn trong thư mục skill và thư mục dự án.
   - Giáo viên chỉ cần **nhấp đúp chuột (Double Click)** vào tệp `cai_dat_tu_dong.bat`: Hệ thống sẽ tự động nhận diện Python, cập nhật pip, tải toàn bộ thư viện cần thiết (`matplotlib`, `scipy`, `python-docx`, `lxml`, `latex2mathml`, `requests`, `pillow`) và kiểm tra kết nối với Microsoft Word/MathType.

2. **Cơ chế Tự Động Sửa Lỗi Ngầm (Self-Healing)**:
   - Khi thực hiện lệnh tạo đề, nếu hệ thống phát hiện bất kỳ thư viện nào chưa được cài đặt (`ImportError` hoặc `ModuleNotFoundError`), Agent **tuyệt đối không yêu cầu người dùng mở terminal gõ lệnh**.
   - Agent sẽ **tự động thực thi lệnh chạy ngầm** script `scripts/check_and_setup_env.py` để tự cài đặt ngay lập tức các gói còn thiếu, sau đó tiếp tục tiến trình tạo đề một cách mượt mà.

3. **Lệnh yêu cầu hỗ trợ cài đặt**:
   - Khi người dùng hỏi: *"Cài đặt môi trường"*, *"Cài đặt các thư viện cần thiết"*, *"Kiểm tra máy"*: Agent sẽ chủ động chạy `python scripts/check_and_setup_env.py` và xuất bảng báo cáo trạng thái chi tiết, dễ hiểu.

---

## Kiến Trúc Pipeline Xử Lý

```text
[Đề gốc PDF / DOCX]
        │
        ▼ (Phân tích ma trận dạng toán & OCR trích xuất)
[Thiết kế số liệu đề mới nghiệm đẹp & Lập trình vẽ hình 300 DPI]
        │
        ▼ (Đóng gói DOCX nền chứa tag $LaTeX$ + Hình ảnh sắc nét)
[_temp_raw_latex.docx]
        │
        ├───────────────────────────────────────────────────────┐
        ▼ (POST qua Backend API)                                 ▼ (Chuyển đổi Client-side)
[https://latex2mathtypeweb.onrender.com/api/convert-docx]     [MML2OMML.XSL Word Engine]
        │                                                        │
        ▼ (200 OK)                                               ▼
[<MA_DE>_MATHTYPE_OLE.docx]                              [<MA_DE>_WORD_EQUATION.docx]
(Công thức MathType OLE xịn 100%,                        (Công thức Word Equation chuẩn SGK,
click đúp mở MathType 6.x/7.x)                           mở trên mọi máy tính không cần MathType)
```

---

## Các Bước Thực Hiện Chi Tiết

### Bước 1: Tiếp nhận và phân tích đề gốc
1. Xác định tệp đề gốc (PDF, DOCX hoặc ảnh chụp trong thư mục dự án hoặc do người dùng tải lên).
2. Dùng Python (`pymupdf`/`fitz` hoặc `docx`) trích xuất toàn bộ câu hỏi và danh sách các câu có hình vẽ:
   - Phần I: Trắc nghiệm 4 lựa chọn (12 câu).
   - Phần II: Trắc nghiệm Đúng/Sai (2 hoặc 4 câu, mỗi câu 4 ý a, b, c, d).
   - Phần III: Trắc nghiệm trả lời ngắn (4 hoặc 6 câu).
   - Phần Tự luận: Khảo sát hàm số, bài toán thực tế, tối ưu hóa.

### Bước 2: Thiết kế bài toán tương đương & Kiểm định toán học
Với mỗi câu hỏi trong đề gốc:
1. **Giữ nguyên dạng toán & phương pháp giải**: Đổi số liệu, tham số nhưng giữ nguyên mức độ nhận biết / thông hiểu / vận dụng.
2. **Chọn số liệu nghiệm đẹp**:
   - Hàm bậc ba / phân thức: Chọn nghiệm đạo hàm nguyên (ví dụ $x = 0, x = 2$ hoặc $x = \pm 1$), tung độ cực trị nguyên.
   - Bài toán thực tế / tối ưu hóa: Đảm bảo điểm dừng $x_0$ rơi vào khoảng thực tế và cho kết quả nguyên hoặc số thập phân gọn.
3. **Lập bảng kiểm định**: Tính toán đạo hàm, cực trị, giới hạn tiệm cận để đảm bảo đáp án trắc nghiệm không bị trùng hoặc vô nghiệm.

### Bước 3: Lập trình vẽ hình kỹ thuật chuẩn xác (300 DPI) & Đậm Nét Siêu Rõ
Lưu toàn bộ hình ảnh vào thư mục `hinh_ve_<ma_de>/` với định dạng PNG độ phân giải 300 DPI:
1. Sử dụng thư viện trợ giúp: [render_math_figures.py](./scripts/render_math_figures.py).
2. **Quy chuẩn đồ thị siêu nét khi in ấn**:
   - Đường cong đồ thị vẽ đậm rõ (`color='#1A365D'` hoặc `#C53030`, `lw=2.2 - 2.4`).
   - Trục tọa độ $Ox, Oy$ có mũi tên rõ nét (`lw=1.2 - 1.5`).
   - Nhãn $x$ và $y$ in nghiêng (`fontsize=13`), **bắt buộc đặt sát đầu mũi tên trục** (không để cách xa).
   - Gốc $O$ đặt tại góc phần tư thứ III gần giao điểm. Font chữ các số tọa độ rõ ràng (`fontsize=12 - 13`).
   - Đường gióng nét đứt màu xám đen (`k--`, `lw=1.0 - 1.2`) nối từ điểm cực trị, điểm cắt tới các trục.
   - Đồ thị trên đoạn $[a; b]$: Sử dụng `CubicHermiteSpline` để khóa cứng giá trị lớn nhất $M$ và giá trị nhỏ nhất $m$, chống hiện tượng đường cong bị võng lẹm sai lệch.
3. **Quy chuẩn bảng biến thiên & hình không gian**:
   - **Bảng biến thiên (BBT)**: Kẻ đầy đủ khung viền bao quanh (full bordered) 100% giống đề thi quốc gia; đủ hàng $x$, $y'$, $y$, vạch đôi $\parallel$, mũi tên $\nearrow \searrow$, font chữ đậm nét 13pt.
   - **Hình học không gian**: Cạnh thấy nét liền (`k-`, `lw=1.8`), cạnh khuất nét đứt (`k--`, `lw=1.5`).

4. **4 Quy Tắc Vàng Khớp Tuyệt Đối Giữa Hình Vẽ & Đề Bài (Visual & Mathematical Consistency Protocol)**:
   - **Quy tắc Miền xác định và 2 đầu mút đoạn kín $[a; b]$**: Khi đề bài khảo sát trên đoạn kín $[a; b]$, đồ thị **bắt buộc phải chấm dứt chính xác tại $x = a$ và $x = b$** (dùng `np.linspace(a, b, 400)`), không kéo dài vô tận sang 2 phía. Luôn đánh dấu chấm tròn nổi bật (`ko`, `ms=5.5`) tại 2 đầu mút $(a; f(a))$, $(b; f(b))$ và kẻ đường gióng nét đứt tới cả 2 trục.
   - **Quy tắc Gióng nhãn trục đối xứng (Opposite Semi-Axis Projection Rule)**:
     * Điểm có $x < 0 \implies$ nhãn tung độ gióng sang phía $x > 0$ của trục $Oy$.
     * Điểm có $x > 0 \implies$ nhãn tung độ gióng sang phía $x < 0$ của trục $Oy$.
     * Điểm có $y < 0 \implies$ nhãn hoành độ gióng lên phía $y > 0$ của trục $Ox$.
     * Điểm có $y > 0 \implies$ nhãn hoành độ gióng xuống phía $y < 0$ của trục $Ox$.
     * Nhãn trên đường gióng nét đứt hoặc tiệm cận: Bắt buộc dùng `bbox=dict(boxstyle='square,pad=0.12', fc='white', ec='none')` tạo cửa sổ trắng sạch, chống đường nét cắt ngang thân chữ số.
   - **Quy tắc Giao điểm & Tọa độ nguyên sạch**: Khi câu hỏi yêu cầu xác định "Giao điểm với trục hoành Ox" hoặc "Giao điểm với trục tung Oy", hàm số hoặc spline phải đi qua chính xác các tọa độ nguyên đó (ví dụ $(3; 0)$, $(0; 2)$). Nhãn số của giao điểm đặt lệch theo hướng ngược chiều độ dốc tiếp tuyến để đường cong không cắt qua chữ.
   - **Quy tắc Tiệm cận và Tâm đối xứng**: Tiệm cận đứng $x = x_0$ và ngang $y = y_0$ kẻ nét đứt `lw=1.2`. Giao điểm với các trục phải cách xa gốc $O$ tối thiểu $|x| \ge 1.0$ hoặc $|y| \ge 1.0$ để nhãn không va chạm với chữ $O$.

### Bước 4: Đóng gói Word chuẩn cỡ chữ 14pt và kết nối Backend MathType OLE
Sử dụng thư viện [docx_math_builder.py](./scripts/docx_math_builder.py):

1. **Chuẩn định dạng cỡ chữ 14pt**:
   - Toàn bộ văn bản câu hỏi, phương án A, B, C, D, lời giải và công thức MathType OLE đều được thiết lập chuẩn **cỡ chữ 14pt (font Times New Roman)**, line spacing 1.15.
2. **Sinh file nền tạm thời (`_temp_raw_latex.docx`)**:
   - Chứa toàn bộ nội dung đề, đáp án, hình vẽ sắc nét, các công thức nằm trong `$ ... $`.
   - Lưu ý: Không dùng tên file chứa chữ `MATHTYPE` để tránh người dùng click nhầm vào file nháp.
3. **Gửi tới Backend API chuyển đổi MathType OLE**:
   - Gọi hàm `convert_to_mathtype_ole_via_backend(base_tex, output_ole)` để gửi file DOCX nền tới `https://latex2mathtypeweb.onrender.com/api/convert-docx`.
   - Nhận lại và lưu thành **`<MA_DE>_DE_HOC_SINH_OLE.docx`** và **`<MA_DE>_LOI_GIAI_GV_OLE.docx`**.
4. **Sinh file dự phòng Word Equation (`<MA_DE>_WORD_EQ.docx`)**:
   - Chuyển toàn bộ công thức sang OMML bằng `MML2OMML.XSL` để người dùng không có MathType vẫn xem và in ấn chuẩn 100%.
5. **Dọn dẹp file nháp tạm**: Tự động xóa file `_temp_raw_latex.docx` sau khi hoàn tất.

### Bước 5: Bàn giao và đối chiếu
1. Cung cấp đường link trực tiếp tới cả 2 tệp `.docx` đã tạo:
   - `<MA_DE>_MATHTYPE_OLE.docx` (MathType OLE nguyên bản - khuyên dùng)
   - `<MA_DE>_WORD_EQUATION.docx` (Word Equation OMML)
2. Hiển thị đề thi trực quan trên màn hình trò chuyện kèm hình ảnh minh họa.
3. Trình bày bảng đáp án trắc nghiệm Phần I, II, III và barem chấm chi tiết phần Tự luận.
4. Lập bảng đối chiếu chứng minh tính chuẩn xác về mặt toán học giữa đề mới và hình vẽ.
