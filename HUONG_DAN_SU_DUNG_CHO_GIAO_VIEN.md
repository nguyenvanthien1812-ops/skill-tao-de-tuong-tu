# 📘 HƯỚNG DẪN SỬ DỤNG SKILL TẠO ĐỀ TOÁN TƯƠNG TỰ v2.0
### Dành cho Quý Thầy/Cô Giáo Viên Bộ Môn Toán – Sử Dụng Trên Google Antigravity

---

## I. TỔNG QUAN – SKILL NÀY LÀM ĐƯỢC GÌ?

Skill **Tạo Đề Toán Tương Tự** là một trợ lý AI sư phạm tự động hóa toàn bộ quy trình biên soạn đề thi Toán từ A→Z. Giáo viên chỉ cần **1 câu nói**, hệ thống sẽ tự động:

| Công việc | Thời gian AI xử lý |
| :--- | :---: |
| Phân tích cấu trúc đề gốc (ma trận, dạng toán, mức độ) | ~5 giây |
| Thiết kế bộ số liệu mới có nghiệm đẹp (nguyên, không lẻ thập phân) | ~10 giây |
| Lập trình vẽ toàn bộ hình vẽ kỹ thuật 300 DPI (đồ thị, BBT, hình không gian) | ~15 giây |
| Xuất bản **Đề Học Sinh** + **Lời Giải Giáo Viên** (MathType OLE + Word Equation) | ~30–60 giây |
| Tạo bộ **4 mã đề hoán vị** + phiếu trả lời bong bóng (in ra chụp ảnh chấm ngay) | ~60 giây |

---

## II. YÊU CẦU HỆ THỐNG

| Phần mềm | Phiên bản tối thiểu | Ghi chú |
| :--- | :--- | :--- |
| **Google Antigravity** | Phiên bản mới nhất | Bắt buộc |
| **Microsoft Word** | Word 2016 / Office 365 | Để mở và in file kết quả |
| **Python** | Python 3.10 trở lên | Bắt buộc; cài đặt 1 lần duy nhất |
| **MathType** | Phiên bản 6.x hoặc 7.x | Không bắt buộc; chỉ cần nếu muốn click đúp sửa công thức |
| Kết nối Internet | Tốc độ thông thường | Để AI giao tiếp với máy chủ chuyển đổi MathType Cloud |

---

## III. CÀI ĐẶT – CHỈ LÀM 1 LẦN DUY NHẤT (MẤT ~2 PHÚT)

### Bước 1: Cài Python (nếu chưa có)

1. Truy cập: **https://www.python.org/downloads/**
2. Tải phiên bản Python mới nhất và cài đặt.
3. ⚠️ **Quan trọng:** Khi màn hình cài đặt hiện ra, hãy **tích vào ô `☑ Add python.exe to PATH`** trước khi nhấn Install.

> [!TIP]
> Để kiểm tra Python đã cài chưa: nhấn `Win + R`, gõ `cmd`, Enter, rồi gõ `python --version`. Nếu thấy `Python 3.x.x` là đã cài thành công.

---

### Bước 2: Cài các thư viện hỗ trợ – 1 Click

Trong thư mục dự án (hoặc thư mục Skill), Thầy/Cô sẽ thấy file:
```
📁 tao-de-toan-tuong-tu/
│
└── 🖱️  cai_dat_tu_dong.bat   ← NHẤP ĐÚP VÀO ĐÂY!
```

**Nhấp đúp chuột (Double Click)** vào `cai_dat_tu_dong.bat`. Màn hình đen sẽ tự động:
- Kiểm tra Python.
- Tải và cài 8 thư viện: `matplotlib`, `scipy`, `python-docx`, `lxml`, `latex2mathml`, `requests`, `pillow`, `openpyxl`.
- Kiểm tra Microsoft Word và MathType trên máy.
- Kiểm tra kết nối với Máy chủ MathType Cloud.
- Hiển thị `[HOÀN TẤT] MÔI TRƯỜNG ĐÃ SẴN SÀNG 100%` → Nhấn phím bất kỳ để đóng.

---

### Bước 3: Cài Skill vào Antigravity

Sao chép thư mục `tao-de-toan-tuong-tu` vào **một trong hai** vị trí sau:

**Dùng cho tất cả dự án (Khuyên dùng):**
```
C:\Users\<Tên_Người_Dùng>\.gemini\config\skills\tao-de-toan-tuong-tu
```

**Dùng riêng cho một thư mục đề thi cụ thể:**
```
<Thư_Mục_Đề_Thi>\.agents\skills\tao-de-toan-tuong-tu
```

---

## IV. CÁCH SỬ DỤNG – CÁC LỆNH THƯỜNG GẶP

Sau khi cài đặt xong, Thầy/Cô **mở thư mục đề thi bằng Antigravity** và nhắn tin trong khung chat. Không cần học lệnh phức tạp – chỉ cần nói chuyện tự nhiên!

---

### 🔵 NHÓM 1: Tạo đề tương tự (1 mã đề đơn)

```
"Tạo cho tôi một đề tương tự từ Đề 301"
"Tạo đề mới tương tự với file PDF này"
"Nhân bản đề thi Toán 12 từ đề gốc có hình vẽ và công thức chuẩn"
```

**Kết quả AI xuất ra:**
```
📁 <Thư_Mục_Đề_Thi>/
├── 📄 [MÃ]_DE_HOC_SINH_OLE.docx      ← Bản phát cho học sinh làm bài
├── 📄 [MÃ]_LOI_GIAI_GV_OLE.docx      ← Bản lời giải chi tiết cho giáo viên
├── 📄 [MÃ]_WORD_EQ.docx              ← Dự phòng Word Equation (máy không có MathType)
└── 📁 hinh_ve_[MÃ]/                  ← 12 hình vẽ kỹ thuật 300 DPI
    ├── fig_cau_1.png
    ├── fig_cau_6.png
    └── ...
```

---

### 🟠 NHÓM 2: Tạo bộ 4 mã đề cho phòng thi

```
"Tạo bộ 4 mã đề phòng thi (mã 201, 202, 203, 204) từ Đề 301"
"Tạo 4 mã đề hoán vị từ đề này, kèm phiếu trả lời để in"
"Tạo bộ đề phòng thi có thể chụp ảnh chấm thi"
```

**Kết quả AI xuất ra:**
```
📁 BO_DE_PHONG_THI/
├── 📁 MA_DE_201/
│   ├── 201_DE_HOC_SINH_OLE.docx
│   ├── 201_LOI_GIAI_GV_OLE.docx
│   ├── 🖼️  phieu_hoc_sinh_201.png      ← In ra phát cho học sinh tô bong bóng
│   └── 🖼️  dap_an_giao_vien_201.png    ← Bản đáp án GV (bong bóng tô đen ●)
├── 📁 MA_DE_202/  ...
├── 📁 MA_DE_203/  ...
├── 📁 MA_DE_204/  ...
├── 📊 DAP_AN_TONG_HOP_4_MA_DE.xlsx    ← Excel 4 sheet, mỗi mã đề 1 sheet màu sắc
└── 🗜️  BO_4_MA_DE_PHONG_THI.zip       ← Nén sẵn sàng gửi Zalo/GDrive
```

---

### 🟢 NHÓM 3: Chỉ tạo phiếu trả lời

```
"Tạo phiếu trả lời bong bóng cho mã đề 304"
"In phiếu trả lời cho học sinh mã đề 201 đến 204"
```

---

---

### 🟣 NHÓM 5: Tạo Ma Trận & Bản Đặc Tả Đề Kiểm Tra (Chuẩn GDPT 2018 - Áp Dụng Mọi Môn Học)

Khi Thầy/Cô cần lập Ma Trận và Bản Đặc Tả để nộp Tổ chuyên môn, Ban Giám Hiệu duyệt hoặc muốn ra đề theo ma trận:

```text
"Tôi muốn làm ma trận đặc tả đề kiểm tra"
"Tạo ma trận đặc tả đề kiểm tra môn [Toán/Lý/Hóa/KHTN/Sử/Địa/Văn] lớp [8/10/11/12]"
"Tạo đề từ ma trận có sẵn"
```

Hệ thống phân luồng cực kỳ thông minh theo 2 trường hợp:
- **Trường hợp 1 (Chưa có ma trận):** Thầy/Cô gom các tài liệu (SGK PDF, Phân phối chương trình, Cấu trúc đề, Chương trình 2018) vào 1 thư mục `DU_LIEU_RA_DE`. AI sẽ tự động phân tích và xuất file Word Ma Trận & Bản Đặc Tả chi tiết có kẻ bảng Table Grid chuẩn quy định của Bộ GD&ĐT.
- **Trường hợp 2 (Đã có ma trận):** Thầy/Cô gửi đường dẫn file Ma trận (Word/Excel/PDF), AI sẽ lập tức biên soạn 2 file Word Đề Học Sinh & Lời Giải Chi Tiết chuẩn MathType OLE 14pt và vẽ hình 300 DPI.
- **Lựa chọn nhanh:** Sử dụng sẵn kho 8 ma trận chuẩn GDPT 2018 của Bộ GD&ĐT tích hợp sẵn trong phần mềm.

---

---

### 🧪 NHÓM 6: Tạo Thí Nghiệm Ảo & Mô Phỏng 3D Tương Tác (Chụp Ảnh SGK)

Biến các hình vẽ tĩnh, sơ đồ thí nghiệm trong SGK thành phòng thí nghiệm ảo tương tác 60 FPS, xuất file HTML chạy Offline 100% không cần mạng:

```text
"Tôi muốn làm thí nghiệm ảo"
"Tạo mô phỏng 3D từ ảnh SGK này"
"Làm thí nghiệm ảo Hóa học / Vật lý"
```

- **Cách tốt nhất:** Thầy/Cô dùng điện thoại chụp lại trang SGK có hình thí nghiệm rồi kéo thả ảnh vào khung chat. AI sẽ tự động đọc dụng cụ, hóa chất, các bước tiến hành và lập trình ra phòng thí nghiệm ảo hoàn chỉnh.
- **File kết quả:** 1 file HTML độc lập (ví dụ `Thi_Nghiem_Ao.html`) mở bằng Chrome/Edge/Cốc Cốc, trình chiếu lên TV hoặc bảng tương tác mà không cần mạng Internet.

---

### 🔧 NHÓM 4: Kiểm tra và cài đặt môi trường

```
"Kiểm tra môi trường máy tính"
"Cài đặt các thư viện cần thiết giúp tôi"
"Setup máy để tạo đề"
```

---

## V. MÔ TẢ CHI TIẾT CÁC FILE KẾT QUẢ

### 1. `[MÃ]_DE_HOC_SINH_OLE.docx` – Bản Đề Thi Học Sinh
- ✅ Chứa toàn bộ câu hỏi, hình vẽ kỹ thuật sắc nét (300 DPI).
- ✅ **Không có đáp án**, không có lời giải.
- ✅ Công thức toán là **MathType OLE nguyên bản** → click đúp mở MathType sửa ngay.
- ✅ Ô trống cho học sinh điền kết quả Phần III (Trả lời ngắn).
- 🖨️ **In ngay bằng Ctrl + P** mà không cần chỉnh sửa gì thêm.

### 2. `[MÃ]_LOI_GIAI_GV_OLE.docx` – Bản Lời Giải Giáo Viên
- ✅ Có dòng cảnh báo màu đỏ "**TÀI LIỆU DÀNH RIÊNG CHO GIÁO VIÊN – KHÔNG PHÁT CHO HỌC SINH**" ngay đầu trang.
- ✅ Bảng đáp án nhanh màu sắc (xanh nền cho số câu, đỏ đậm cho đáp án đúng).
- ✅ Lời giải chi tiết từng bước, đủ barem điểm.
- ✅ Công thức MathType OLE.

### 3. `[MÃ]_WORD_EQ.docx` – Bản Dự Phòng Word Equation
- ✅ Dành cho máy tính chưa cài MathType.
- ✅ Công thức Word Equation gốc (OMML) – chỉnh sửa bằng phím `Alt + =` chuẩn SGK.
- ✅ Hiển thị và in ấn chuẩn 100% trên mọi máy có Word 2016+.

### 4. `phieu_hoc_sinh_[MÃ].png` – Phiếu Trả Lời Học Sinh (Bubble Sheet)
- ✅ Chuẩn khổ A4, in trực tiếp từ Windows Print.
- ✅ 4 góc tròn đen (alignment markers) để định vị khi chụp ảnh.
- ✅ Bong bóng ABCD Phần I, ô Đ/S Phần II, ô điền kết quả Phần III.

### 5. `dap_an_giao_vien_[MÃ].png` – Phiếu Đáp Án Giáo Viên
- ✅ Bong bóng đáp án đúng tô đen ●, dễ đối chiếu khi chấm tay.
- ✅ Phần III hiển thị số đáp án nổi bật màu tím.

### 6. `DAP_AN_TONG_HOP_4_MA_DE.xlsx` – Excel Tổng Hợp
- ✅ Mỗi mã đề một sheet riêng.
- ✅ Ô đáp án được tô màu (A: xanh, B: xanh lá, C: vàng, D: hồng).
- ✅ Có thể import vào app chấm thi hỗ trợ file CSV/Excel.

---

## VI. CÁCH CHẤM THI BẰNG PHIẾU BUBBLE SHEET

1. **Trước khi thi:** In `phieu_hoc_sinh_[MÃ].png` cho học sinh (1 tờ A4/học sinh). In `dap_an_giao_vien_[MÃ].png` giữ lại cho giáo viên.
2. **Sau khi thi:** Thu phiếu trả lời từ học sinh.
3. **Chấm thi:**
   - **Cách 1 (Nhanh nhất):** Đặt phiếu đáp án GV cạnh phiếu học sinh, nhìn bong bóng đen khớp là đúng.
   - **Cách 2 (Tự động):** Chụp ảnh phiếu học sinh bằng điện thoại → dùng app nhận dạng OMR (như **CamScanner, Appy Pie OMR, GradeCam**) đọc bong bóng tự động.
4. **Tổng hợp điểm:** Dùng file Excel `DAP_AN_TONG_HOP_4_MA_DE.xlsx` làm bảng tra cứu đáp án nhanh.

---

## VII. FAQ – CÂU HỎI THƯỜNG GẶP

### ❓ "Tại sao công thức chỗ to chỗ nhỏ, hoặc phân số bị nhỏ hơn chữ thường? Làm sao để đồng bộ 100%?"
**→ Do cỡ chữ MathType OLE chưa đồng bộ với cỡ chữ văn bản Word hoặc MathType tự co nhỏ phân số:**  
Trong Word, khi Thầy/Cô đổi cỡ chữ văn bản (ví dụ từ 14pt xuống 12pt hoặc 10.5pt), Word **chỉ đổi chữ viết (text)**, hoàn toàn không đổi được cỡ của đối tượng MathType OLE. Đồng thời mặc định MathType tự động thu nhỏ tử số và mẫu số của phân số xuống chỉ còn 58% cỡ chuẩn.

#### 🎯 CÁCH CHUẨN HÓA 1-CLICK CỰC NHANH TRONG WORD (CHỈ MẤT 3 GIÂY):

**Bước 1:** Trên thanh công cụ Word, chọn tab **MathType** $\rightarrow$ Bấm nút **Format Equations** (hoặc phím tắt `Ctrl + Alt + Q`).  
- Tích chọn mục **MathType preference file:** (dòng thứ 4 từ trên xuống).  
- Bấm vào nút **Browse...** ngay bên cạnh.  
![Bước 1: Hộp thoại Format Equations](CAU_HINH_MATHTYPE_CHUAN/huong_dan_buoc1_format_equations.png)

**Bước 2:** Chọn file cấu hình chuẩn 14pt (Thầy/Cô chọn **1 trong 2 cách**):  
- **🌟 Cách 1 (Dễ nhất — Chuột click Desktop):** Ở cột bên trái cửa sổ chọn tệp, nhấp vào **Desktop** (Màn hình chính) $\rightarrow$ Nhấp đúp vào file **`Times_14pt_Chuan_BGD.eqp`** (đã được tự động để sẵn trên Desktop) $\rightarrow$ Bấm **Open**.  
- **⚡ Cách 2 (Siêu nhanh — Dán đường dẫn):** Tại ô **`File name:`** ở dưới cùng (nơi con trỏ chuột nhấp nháy), dán trực tiếp dòng này vào:  
  ```text
  C:\Users\admin\Desktop\Times_14pt_Chuan_BGD.eqp
  ```  
  rồi bấm nút **Open**.  
![Bước 2: Chọn file cấu hình EQP](CAU_HINH_MATHTYPE_CHUAN/huong_dan_buoc2_chon_file_cau_hinh.png)

**Bước 3:** Tích chọn **Whole document** (Toàn bộ tài liệu) $\rightarrow$ Bấm nút **OK**.  
👉 **Kết quả:** Toàn bộ công thức trong toàn bài sẽ đồng loạt nhảy về chuẩn **14 pt**, các phân số được tự động phóng to rõ ràng, cân đối tuyệt đối chỉ trong 3 giây!  
*(Nếu Thầy/Cô dùng đề cỡ 12pt hoặc 13pt thì chọn tương ứng file `Times_12pt_Chuan_BGD.eqp` hoặc `Times_13pt_Chuan_BGD.eqp` ngay trên Desktop).*  
*(Hoặc Thầy/Cô có thể mở ngay file song hành `[MÃ]_WORD_EQ.docx` đi kèm: bản này dùng Word Equation nên khi bôi đen đổi cỡ chữ, toàn bộ công thức và phân số sẽ tự động co giãn theo 100%!).*

---

### ❓ "Tôi mở file Word lên nhưng công thức vẫn là mã chữ `$y = f(x)$`"
**→ Bạn đang mở nhầm file tạm trung gian.** Hãy đóng lại và mở đúng file:
- Bản học sinh: `[MÃ]_DE_HOC_SINH_OLE.docx`
- Bản lời giải: `[MÃ]_LOI_GIAI_GV_OLE.docx`

File đúng **không bao giờ** có chữ `TEX` hoặc `TEMP` trong tên.

---

### ❓ "Công thức hiện ra nhưng không click đúp mở MathType được"
**→ Máy tính chưa cài MathType.** Công thức vẫn hiển thị đẹp dưới dạng ảnh vector WMF sắc nét – bạn có thể in ấn bình thường. Nếu cần sửa công thức, hãy mở bản `[MÃ]_WORD_EQ.docx` và dùng `Alt + =`.

---

### ❓ "AI báo lỗi hoặc script chạy không xong"
**→ Nhắn vào khung chat:** *"Kiểm tra môi trường và cài đặt lại các thư viện cần thiết"*. AI sẽ tự chẩn đoán và sửa mà không cần bạn làm gì thêm.

---

### ❓ "Tôi muốn thay đổi tên trường hoặc năm học trên đề thi"
**→ Nhắn thêm thông tin khi ra lệnh:**
> *"Tạo đề tương tự từ Đề 301, tên trường là THPT Nguyễn Trãi, năm học 2025–2026"*

---

### ❓ "Có thể tạo đề cho lớp 10 hoặc 11 không?"
**→ Có.** Skill hoạt động với bất kỳ cấp lớp nào. Chỉ cần nói rõ khi ra lệnh:
> *"Tạo đề tương tự lớp 11 từ đề này"*

---

## VIII. CẤU TRÚC THƯ MỤC SKILL (Để Tham Khảo)

```
tao-de-toan-tuong-tu/
│
├── 📋 SKILL.md                        ← Hướng dẫn quy trình cho AI
├── 🖱️  cai_dat_tu_dong.bat             ← Nút bấm 1-click cài đặt môi trường
│
├── 📁 scripts/
│   ├── check_and_setup_env.py         ← Tự động chẩn đoán & cài thư viện
│   ├── render_math_figures.py         ← Vẽ hình kỹ thuật 300 DPI
│   ├── docx_math_builder.py           ← Tạo file Word (Bản HS + Bản GV)
│   └── exam_shuffler.py               ← Trộn mã đề + tạo phiếu bubble sheet
│
└── 📁 references/
    └── quy_chuan_de_thi_2025.md       ← Chuẩn ma trận đề thi GDPT 2018
```

---

## IX. CHIA SẺ CHO ĐỒNG NGHIỆP

Để tặng bộ công cụ này cho đồng nghiệp:

1. Gửi file **[SKILL_TAO_DE_TOAN_TUONG_TU.zip](file:///c:/Users/admin/Downloads/tao-de/SKILL_TAO_DE_TOAN_TUONG_TU.zip)** qua Zalo / Google Drive / Email.
2. Đồng nghiệp:
   - Giải nén file `.zip`.
   - **Nhấp đúp vào `cai_dat_tu_dong.bat`** → tự động cài trong 30 giây.
   - Copy thư mục `tao-de-toan-tuong-tu` vào `C:\Users\..\.gemini\config\skills\`.
   - Mở thư mục đề thi bằng Antigravity và bắt đầu tạo đề!

---

> [!NOTE]
> Skill được phát triển và duy trì bởi **Google Antigravity (AGY)**. Mọi thắc mắc kỹ thuật, vui lòng nhắn trực tiếp vào khung chat Antigravity.
