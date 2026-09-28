---
name: tao-de-toan-tuong-tu
description: >-
  Tạo đề thi hoặc đề kiểm tra môn TOÁN, VẬT LÝ, HÓA HỌC (và KHTN lớp 6-12) tương tự (song song, cùng ma trận đặc tả) từ một đề gốc cho trước.
  Tự động phân tích đề gốc (từ file PDF, Word DOCX hoặc ảnh chụp), thiết kế bộ số liệu mới nghiệm đẹp & chuẩn xác định luật tự nhiên (bảo toàn khối lượng/nguyên tố/electron, định luật vật lý/toán học),
  lập trình vẽ 100% hình vẽ kỹ thuật & thí nghiệm (đồ thị hàm số, bảng biến thiên, hình không gian 3D, sơ đồ mạch điện, thấu kính quang học, đồ thị dao động/sóng, phân tích vectơ lực, sơ đồ thí nghiệm hóa học, giản đồ năng lượng, đồ thị pH chuẩn độ)
  chuẩn xác tuyệt đối bằng Python Matplotlib (300 DPI), dựng bảng số liệu nguyên bản (Table Grid), và tự động kết nối Backend Converter API (https://latex2mathtypeweb.onrender.com/api/convert-docx)
  để xuất trực tiếp file Word (.docx) chứa đối tượng MathType OLE nguyên bản (Equation.DSMT4) mở click đúp sửa ngay,
  kèm cơ chế Smart Fallback sang bản Word Equation (OMML) chuẩn SGK.
  Tích hợp sẵn tính năng tự động chẩn đoán và cài đặt môi trường 1-click cho giáo viên.
  Hỗ trợ xuất đồng thời bản Đề Học Sinh và bản Lời Giải Chi Tiết riêng biệt.
  Tự động tạo bộ 4 mã đề hoán vị kèm phiếu trả lời bong bóng (bubble sheet) chuẩn A4 chụp ảnh chấm thi và file Excel tổng hợp đáp án.
  Đặc biệt: Tích hợp công nghệ chuyển đổi tệp đề thi PDF (kể cả PDF scan hoặc ảnh) sang Word không lỗi công thức khoa học (Toán, Lý, Hóa), không lỗi hình vẽ và bảng biểu, xuất trực tiếp MathType OLE 14pt.
  Kích hoạt khi người dùng yêu cầu: "tạo đề tương tự", "tạo đề tương tự từ đề gốc", "nhân bản đề thi Toán", "tạo đề vật lý tương tự",
  "tạo đề thi môn lý", "nhân bản đề thi vật lý", "tạo đề hóa học tương tự", "tạo đề thi môn hóa", "nhân bản đề hóa học", "tạo đề KHTN",
  "tạo mã đề song song có hình vẽ và công thức chuẩn", "xuất đề thi mathtype ole", "cài đặt môi trường", "cài đặt thư viện", "setup máy tạo đề",
  "kiểm tra môi trường", "tạo bộ 4 mã đề", "tạo phiếu trả lời", "chuyển pdf sang word", "chuyển pdf sang word không lỗi",
  "chuyển đề thi pdf sang word mathtype", "convert pdf to word mathtype", "chuyển pdf sang word công thức toán không lỗi",
  "chuyển đề thi hóa sang word mathtype", "chuyển đề thi lý sang word mathtype", "vẽ hình thí nghiệm hóa học", "vẽ hình học không gian 3d", "dựng bảng biểu word mathtype".
---

# Quy Trình Tạo Đề Toán, Vật Lý & Hóa Học Tương Tự Chuẩn Bộ GD&ĐT (Tích Hợp Backend MathType OLE & Cài Đặt 1-Click)

Skill này tự động hóa toàn bộ quy trình biên soạn đề kiểm tra / đề thi môn **TOÁN**, **VẬT LÝ** và **HÓA HỌC** (cấp THCS lớp 6, 7, 8, 9 và THPT lớp 10, 11, 12 theo định dạng mới GDPT 2018), bảo đảm **3 tiêu chuẩn vàng**:
1. **Khoa học chuẩn xác 100%**: Nghiệm đẹp, tham số logic, tuân thủ đúng định luật vật lý, hóa học (bảo toàn khối lượng, nguyên tố, điện tích, electron) và toán học (không bị hiện tượng vô lý), 4 phương án trắc nghiệm chỉ có duy nhất 1 phương án đúng, lời giải chi tiết từng bước.
2. **Hình vẽ kỹ thuật & Thí nghiệm 300 DPI chuẩn mực**: Vẽ bằng code Python Matplotlib:
   - **Môn Toán**: Đồ thị hàm số, bảng biến thiên full khung viền, hình học không gian 3D ($S.ABCD$, lăng trụ, nón, trụ, cầu), hệ trục giải tích $Oxyz$.
   - **Môn Vật lý**: Đường truyền tia sáng & thấu kính, đồ thị dao động điều hòa/sóng cơ ($x-t, v-t, u-t$), sơ đồ mạch điện ($R, L, C$), giản đồ vectơ Fresnel, phân tích vectơ lực trên mặt phẳng nghiêng, đồ thị biến thiên nhiệt/khí lý tưởng $(p-V, p-T)$.
   - **Môn Hóa học**: Sơ đồ dụng cụ thí nghiệm điều chế và thu khí (dời chỗ nước/không khí), sơ đồ bình điện phân, giản đồ năng lượng phản ứng ($\Delta_r H, E_a$), đường cong chuẩn độ pH axit - bazơ.
3. **Công thức chuẩn MathType OLE (14pt) & Word Equation**:
   - Sử dụng **Backend Converter API** (`https://latex2mathtypeweb.onrender.com/api/convert-docx`) để biên dịch 100% công thức Toán, Lý (vectơ, chỉ số, đơn vị, hạt nhân), Hóa (công thức phân tử, ion, phức chất, mũi tên điều kiện $\xrightarrow{t^\circ, \text{xt}}$, mũi tên thuận nghịch $\rightleftharpoons$, kết tủa $\downarrow$, bay hơi $\uparrow$, font IUPAC thẳng chuẩn $\mathrm{Fe, Al, Cu}$) thành **MathType OLE (`Equation.DSMT4`)** nhúng nhị phân MTEF `.bin` + vector `.wmf` trực tiếp vào file Word. Giáo viên click đúp vào bất kỳ công thức nào là mở cửa sổ MathType truyền thống ngay lập tức!
   - Kèm cơ chế **Smart Fallback**: Luôn sinh thêm bản **Word Equation (OMML)** để mở được mượt mà trên mọi máy tính kể cả khi không cài MathType.
4. **Bảng Biểu Nguyên Bản (Table Grid 100%)**:
   - Tự động dựng thành bảng Word thật (`Table Grid`) có viền đầy đủ, căn lề giữa cả ngang và dọc cho các bảng thống kê Toán, bảng số liệu thực nghiệm đo đạc Vật lý, và bảng nhận biết thuốc thử Hóa học. Tuyệt đối không dùng ảnh chụp bảng, giáo viên chỉnh sửa số liệu tùy ý.

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

6. **Bố Cục 2 Cột Thông Minh Tiết Kiệm Giấy In (Smart Side-by-Side Layout Protocol)**:
   - **Mục tiêu sư phạm**: Khi in đề thi trên khổ giấy A4, đặt hình vẽ ngay phía dưới câu hỏi (full-width stacked) làm mất tới 10-12 cm chiều cao trang cho mỗi câu, khiến đề thi bị phình to tốn kém giấy in. Bằng cách xếp **câu hỏi + đáp án bên trái** và **hình vẽ bên phải** trong một bảng ẩn không viền, diện tích chiều cao trang in được **tiết kiệm từ 35% đến 45%**!
   - **Bộ Tiêu Chí Xét Tính Phù Hợp (Suitability Decision Matrix)**:
     * ✅ **PHÙ HỢP BỐ CỤC 2 CỘT (`is_side_by_side = True`)**:
       - Hình dạng gần vuông hoặc đứng (tỉ lệ $W/H \le 1.35$, chiều rộng hiển thị $2.0 - 2.4$ inches): Đồ thị hàm số trên hệ tọa độ $Oxy$ (bậc ba, phân thức hữu tỉ, bậc bốn, đồ thị trên đoạn kín), hình học không gian dạng đứng, sơ đồ lực vật lý.
       - Nội dung bên trái (dẫn đề + các đáp án A, B, C, D hoặc các ý a, b, c, d) có từ 3 đến 6 dòng chữ, vừa khít và cân xứng hoàn hảo với chiều cao của hình vẽ bên phải.
       - Áp dụng mẫu: Câu 1, Câu 2, Câu 4, Câu 8, Câu 10 (Phần I); Câu 1 (Phần II); Câu 2, Câu 3 (Phần III).
     * ⛔ **KHÔNG PHÙ HỢP – BẮT BUỘC ĐỂ TOÀN DÒNG (Full-Width Stacked)**:
       - **Bảng biến thiên (BBT)**: Cần chiều ngang tối thiểu $4.0 - 4.5$ inches để hiển thị đầy đủ các cột $-\infty, x_1, x_2, +\infty$, vạch đôi $\parallel$ và mũi tên biến thiên không bị co rúm méo mó. Nếu ép BBT vào cột hẹp $2.2$ inches sẽ vi phạm nghiêm trọng chuẩn mực sư phạm. (Ví dụ: Câu 11, Câu 12 Phần I; Câu 1 Phần III).
       - **Hình vẽ ghép ngang phức hợp (Landscape Multi-diagrams)**: Các hình gồm 2 hình con đặt ngang nhau (như sơ đồ tấm tôn phẳng $60\text{ cm}$ và hình hộp 3D bên cạnh, chiều ngang thực tế $> 4.0$ inches). Bắt buộc phải để toàn dòng để học sinh dễ quan sát. (Ví dụ: Câu 3 Tự luận).
   - **Quy cách kỹ thuật Word DOCX**:
     * Bảng ẩn `rows=1, cols=2`, xóa 100% đường viền (`_remove_table_borders(table)`).
     * Cột trái: Chiều rộng $4.5$ inches ($11.4\text{ cm}$), căn lề trên `WD_ALIGN_VERTICAL.TOP`.
     * Cột phải: Chiều rộng $2.3$ inches ($5.8\text{ cm}$), hình ảnh căn giữa theo chiều dọc `WD_ALIGN_VERTICAL.CENTER`.
     * Bản Giáo Viên: Lời giải chi tiết được trình bày trải rộng toàn dòng ngay phía dưới bảng để thuận tiện đọc và chấm thi.


### Bước 5: Bàn giao và đối chiếu
1. Cung cấp đường link trực tiếp tới cả 2 tệp `.docx` đã tạo:
   - `<MA_DE>_MATHTYPE_OLE.docx` (MathType OLE nguyên bản - khuyên dùng)
   - `<MA_DE>_WORD_EQUATION.docx` (Word Equation OMML)
2. Hiển thị đề thi trực quan trên màn hình trò chuyện kèm hình ảnh minh họa.
3. Trình bày bảng đáp án trắc nghiệm Phần I, II, III và barem chấm chi tiết phần Tự luận.
4. Lập bảng đối chiếu chứng minh tính chuẩn xác về mặt toán học giữa đề mới và hình vẽ.

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

## 🧪 Quy Chuẩn Biên Soạn Môn HÓA HỌC (Lớp 10, 11, 12 & KHTN)

1. **Công thức & Phương trình Hóa học MathType OLE (14pt)**:
   - **Tên nguyên tố chuẩn IUPAC GDPT 2018**: Dùng font chữ đứng chuẩn (`\mathrm{...}` hoặc `\text{...}`), tuyệt đối không để in nghiêng như ẩn số toán học (Ví dụ: $\mathrm{Fe, Al, Cu, O_2, H_2O}$, không dùng $Fe, Al, Cu$).
   - **Phương trình 1 chiều có điều kiện**: Sử dụng `\xrightarrow{t^\circ, \text{xt}}` (ví dụ: $2\text{Al} + \text{Fe}_2\text{O}_3 \xrightarrow{t^\circ} \text{Al}_2\text{O}_3 + 2\text{Fe}$).
   - **Phương trình thuận nghịch**: Dùng `\rightleftharpoons` cho phản ứng cân bằng hóa học (ví dụ: $\text{N}_2(g) + 3\text{H}_2(g) \rightleftharpoons 2\text{NH}_3(g)$).
   - **Trạng thái & Hiện tượng**: Ký hiệu kết tủa $\downarrow$, khí thoát $\uparrow$, trạng thái $(s), (l), (g), (aq)$.
   - **Nhiệt hóa học**: Enthalpy chuẩn $\Delta_r H_{298}^\circ = -92,2\text{ kJ/mol}$, $\Delta_f H_{298}^\circ$.
   - **Hóa học hữu cơ & phức chất**: Công thức cấu tạo mạch $\text{CH}_3-\text{CH}_2-\text{OH}$, este $\text{CH}_3\text{COOC}_2\text{H}_5$, ion phức $[\text{Cu}(\text{NH}_3)_4]^{2+}$.
2. **Hình vẽ thí nghiệm & Đồ thị Hóa học 300 DPI**:
   - Dụng cụ điều chế thu khí (dời nước, dời không khí), bình điện phân, giản đồ năng lượng phản ứng ($\Delta_r H, E_a$), đường cong chuẩn độ pH (điểm tương đương, bước nhảy pH).

---

## 📊 Quy Chuẩn Bảng Biểu Đa Môn (Table Grid Nguyên Bản)

1. **Môn Toán**:
   - Bảng biến thiên (BBT): Khung viền kép hoặc full border đầy đủ, căn lề giữa, vạch đôi $\parallel$, mũi tên biến thiên $\nearrow \searrow$.
   - Bảng mẫu số liệu ghép nhóm thống kê: Cột nhóm giá trị, tần số, tần suất, độ lệch chuẩn.
2. **Môn Vật lý**:
   - Bảng số liệu thực nghiệm đo đạc: Lần đo $1, 2, 3$, giá trị trung bình $\bar{X}$, sai số tuyệt đối $\Delta X$.
   - Bảng thông số kỹ thuật thiết bị điện: Điện áp định mức $U_{đm}$, công suất $P_{đm}$, hiệu suất.
3. **Môn Hóa học**:
   - Bảng nhận biết & thuốc thử: Cột Mẫu thử, Thuốc thử, Hiện tượng quan sát, Phương trình ion thu gọn.
   - Bảng nhiệt động học & hằng số: Enthalpy tạo thành $\Delta_f H_{298}^\circ$, entropy $S_{298}^\circ$, thế điện cực chuẩn $E^\circ$.
4. **Quy cách Word DOCX**:
   - Luôn dùng `doc.add_table(style='Table Grid')`. Căn giữa ngang `WD_TABLE_ALIGNMENT.CENTER` và căn giữa dọc `WD_ALIGN_VERTICAL.CENTER`. Khung viền sắc nét, giáo viên nhấp chuột sửa trực tiếp mọi số liệu.


