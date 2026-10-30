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

---

### 🎬 NHÓM 7: Tạo Video Tương Tác E-Learning (Từ Link YouTube, Giáo Án Word Hoặc Sách Giáo Khoa)

> 💡 **Mẹo nhanh cho người mới:** Thầy/Cô chỉ cần gõ ngắn gọn **`"tôi muốn tạo video tương tác"`** (hoặc **`"tôi muốn thay đổi mật khẩu chế độ thầy cô"`**), AI sẽ lập tức hiện bảng hướng dẫn cầm tay chỉ việc từng bước từ đầu!

#### 1️⃣ Quy trình 4 bước từ đầu cho Giáo viên mới làm lần đầu:
1. **Bước 1 — Chuẩn bị nguồn bài giảng:**
   - *Nếu đã có video trên YouTube:* Copy đường link YouTube bài giảng (có thể đính kèm thêm file **Giáo án Word `.docx`** hoặc **file/ảnh Sách giáo khoa SGK** để câu hỏi khớp 100% tiết dạy trên lớp).
   - *Nếu CHƯA CÓ VIDEO (chỉ mới có Giáo án Word hoặc SGK):* Kéo thả file Giáo án Word (`.docx`) hoặc file PDF / ảnh chụp trang SGK vào khung chat — AI sẽ tự tạo Slide 16:9 $\to$ viết lời giảng $\to$ lồng tiếng AI (**Cô Hoài My** / **Thầy Nam Minh**) $\to$ kết xuất **Video MP4 Full HD 1080p** $\to$ nhúng câu hỏi tương tác đúng từng giây!
2. **Bước 2 — Kết nối Sổ điểm Google Sheets tự chia lớp:** Nếu chưa biết tạo link Web App (`/exec`), Thầy/Cô chỉ cần ghi trong câu lệnh: **`"Hướng dẫn tôi tạo Sổ điểm Google Sheets"`** (AI sẽ cấp sẵn đoạn mã copy-paste 30 giây là xong).
3. **Bước 3 — Gửi 1 trong các Mẫu Câu Lệnh rõ ràng bên dưới** để AI xuất sẵn thư mục `Web_Video_Tuong_Tac_...` ra ngoài **Desktop**.
4. **Bước 4 — Đưa lên Web miễn phí 3 giây:** Mở [app.netlify.com](https://app.netlify.com) $\to$ kéo thả thư mục ngoài Desktop vào khung Deploys là có ngay đường link HTTPS gửi Zalo cho học sinh!

#### 🎯 Bảng Menu 10 Dạng Câu Hỏi Tương Tác Chuẩn GDPT 2018 (Thầy/Cô Tùy Chọn):
*(Thầy/Cô không cần nhớ mã kỹ thuật — chỉ cần gọi tên tiếng Việt hoặc ghi `"Tự phối hợp đa dạng trong 10 dạng"`)*
1. **Trắc nghiệm 1 lựa chọn (`A, B, C, D`)** — Chạm 1 lần chấm ngay, khóa nút sai chống chạm đúp.
2. **Đúng / Sai đơn (1 nhận định)** — Chọn `✅ ĐÚNG` hoặc `❌ SAI` (sai khóa 3 giây suy ngẫm).
3. **Đúng / Sai đa mệnh đề (`4 ý a, b, c, d` chuẩn Phần II Bộ GD&ĐT)** — Mỗi dòng có nút `[Đúng] / [Sai]`; làm sai chỉ báo tổng số ý đúng (*"Đúng 2/4 mệnh đề"*), không lộ ý sai.
4. **Trắc nghiệm nhiều đáp án đúng (`Checkbox ☐`)** — Tích chọn tất cả các khẳng định đúng.
5. **Điền đáp án ngắn / Điền số** — Gõ số nguyên, số âm, thập phân (`3,5 = 3.5`) hoặc từ ngắn.
6. **Điền khuyết nhiều chỗ trống `(1), (2), (3)`** — Hỗ trợ cả chạm từ gợi ý trong ngân hàng từ hoặc gõ trực tiếp.
7. **Chạm / Ghép thẻ vào 1 ô kết quả** — Chạm chọn 1 thẻ hoặc ghép chuỗi nhiều thẻ.
8. **Nối cặp tương ứng 2 cột (`Cột A ↔ Cột B`)** — Chạm 1 ô Cột A + chạm 1 ô Cột B gắn nhãn màu (`Cặp 1`, `Cặp 2`...).
9. **Sắp xếp thứ tự quy trình / dãy số** — Dùng nút `▲ / ▼` hoặc chạm 2 thẻ để đổi chỗ.
10. **Phân loại thẻ vào `2–4` nhóm kiến thức** — Chạm thẻ rồi chạm vào Rổ/Nhóm tương ứng.

#### 2️⃣ Các mẫu câu lệnh chi tiết (Copy – Điền thông tin – Gửi ngay):

* **🟢 Mẫu A — Đã có Link YouTube (có thể kèm Giáo án Word / SGK để AI tự soạn câu hỏi chuẩn bài dạy):**
```text
Em hãy tạo giúp tôi 1 trang Web Video Tương Tác E-Learning hoàn chỉnh:
- Môn & Lớp: [Ví dụ: Toán 6 - Kết nối tri thức]
- Tên bài học: [Ví dụ: Bài 6 - Lũy thừa với số mũ tự nhiên]
- Giáo viên & Trường: [Ví dụ: GV Nguyễn Thiện - THCS Ứng Hòe]
- Link video YouTube: [Dán link YouTube] (Thời lượng: [Ví dụ: 14 phút 20 giây])
- Tài liệu bám sát (nếu có): [Kéo thả file Giáo án Word .docx hoặc PDF/ảnh SGK vào chat, hoặc bỏ qua]
- Link Web App Google Sheets: [Dán link .../exec HOẶC ghi "Hướng dẫn tôi tạo Sổ điểm Google Sheets"]
- Mật khẩu Chế độ Thầy Cô: [Nhập mật khẩu riêng, ví dụ: Thien2026 - để trống mặc định là 123456]
- Các dạng câu hỏi muốn dùng: [Ghi "Tự phối hợp đa dạng trong 10 dạng" HOẶC ghi tên các dạng muốn có: (1) Trắc nghiệm 1 đáp án, (2) Đúng/Sai đơn, (3) Đúng/Sai 4 ý a-b-c-d, (4) Chọn nhiều đáp án, (5) Điền số/chữ, (6) Điền khuyết nhiều chỗ trống, (7) Ghép thẻ, (8) Nối cặp 2 cột A-B, (9) Sắp xếp thứ tự, (10) Phân loại nhóm]
- Yêu cầu: Thiết kế [5 - 7] trạm câu hỏi tương tác rải đều theo bài giảng; chống tua nhanh 100%; trả lời ĐÚNG mới hiện giải thích; đóng gói thư mục chuẩn ra ngoài Desktop để kéo thả lên Netlify.
```

* **🟣 Mẫu B — CHƯA CÓ VIDEO: Làm mới trọn gói từ File Giáo án Word (`.docx`) hoặc Sách giáo khoa (`.pdf` / ảnh chụp):**
```text
Hiện tại tôi chưa có video bài giảng, mới chỉ có file Giáo án / Sách giáo khoa tại: "[Kéo thả file vào chat HOẶC giữ Shift + Chuột phải vào file chọn Copy as path rồi dán vào đây]".
Em hãy làm trọn gói từ đầu giúp tôi ra cả Video bài giảng MP4 lẫn Trang Web Video Tương Tác:
- Môn & Lớp: [...] - Tên bài học: [...] - Giáo viên & Trường: [...]
- Giọng đọc AI lồng tiếng: [Cô Hoài My (Nữ miền Bắc) / hoặc Thầy Nam Minh (Nam miền Bắc)]
- Hình thức sử dụng: [Online qua YouTube + Netlify / hoặc Offline dạy trực tiếp trên TV lớp học]
- Link Web App Google Sheets: [Dán link .../exec HOẶC ghi "Hướng dẫn tôi tạo Sổ điểm Google Sheets"]
- Mật khẩu Chế độ Thầy Cô: [Nhập mật khẩu riêng, ví dụ: Thien2026]
- Các dạng câu hỏi muốn dùng: [Ghi "Tự phối hợp đa dạng trong 10 dạng" HOẶC ghi tên các dạng muốn có]
- Yêu cầu: (1) Bóc tách nội dung & ảnh gốc từ Giáo án/SGK, lập kịch bản Slide + danh sách câu hỏi gửi tôi duyệt; (2) Tạo Slide PowerPoint 16:9 chuẩn sư phạm, viết lời giảng vào Notes, lồng tiếng AI và xuất Video MP4 Full HD 1080p; (3) Căn đúng mốc giây kết thúc từng mục kiến thức trong video vừa xuất để đóng gói Trang Web Video Tương Tác ra ngoài Desktop.
```
*(Lưu ý khi làm từ Giáo án/SGK: Sau khi AI xuất xong file `.mp4`, nếu muốn gửi link Online cho học sinh học ở nhà trên điện thoại, Thầy/Cô chỉ cần tải file `.mp4` đó lên YouTube ở chế độ **Không công khai / Unlisted** mất 1 phút rồi gửi link YouTube cho AI gắn vào gói Netlify; nếu chỉ dạy trên máy chiếu/TV lớp học thì chạy Offline trực tiếp file `.mp4` ngay trong thư mục mà không cần đăng YouTube!).*

* **🟠 Mẫu C — Đã có Video YouTube + Thầy/Cô tự soạn sẵn câu hỏi (Dùng dạng nào giữ dòng đó, xóa dòng không dùng):**
```text
Em hãy tạo trang Web Video Tương Tác E-Learning theo đúng danh sách câu hỏi và mốc thời gian tôi đã chuẩn bị sẵn:
- Môn & Lớp: [...] - Tên bài học: [...] - Giáo viên & Trường: [...]
- Link video YouTube: [Dán link YouTube] (Thời lượng: [Ví dụ: 14 phút 20 giây])
- Link Web App Google Sheets: [Dán link .../exec HOẶC ghi "Hướng dẫn tôi tạo Sổ điểm Google Sheets"]
- Mật khẩu Chế độ Thầy Cô: [Nhập mật khẩu riêng, ví dụ: 246810]
- Danh sách các trạm câu hỏi (giữ lại các dạng muốn dùng):
  + Trạm 1 (phút 02:30 - Trắc nghiệm 1 đáp án): [Câu hỏi | A... B... C... D... | Đáp án đúng | Giải thích]
  + Trạm 2 (phút 04:00 - Đúng/Sai đơn): [Nhận định | Đáp án: Đúng hoặc Sai | Giải thích]
  + Trạm 3 (phút 05:30 - Đúng/Sai 4 ý a,b,c,d): [Đề dẫn | a) ... (Đúng/Sai); b) ... (Đúng/Sai); c) ... (Đúng/Sai); d) ... (Đúng/Sai) | Giải thích]
  + Trạm 4 (phút 07:00 - Chọn nhiều đáp án đúng): [Câu hỏi | Các phương án | Các đáp án đúng | Giải thích]
  + Trạm 5 (phút 08:20 - Điền đáp án ngắn/số): [Câu hỏi | Đáp án đúng | Giải thích]
  + Trạm 6 (phút 09:40 - Điền khuyết nhiều chỗ trống): [Đoạn văn có (1), (2), (3) | Đáp án (1), (2), (3) | Các từ gợi ý (nếu có) | Giải thích]
  + Trạm 7 (phút 11:00 - Ghép thẻ): [Câu hỏi | Các thẻ lựa chọn | Thẻ đúng | Giải thích]
  + Trạm 8 (phút 12:10 - Nối cặp 2 cột A-B): [Câu hỏi | Cặp 1: A1 - B1; Cặp 2: A2 - B2; Cặp 3: A3 - B3 | Giải thích]
  + Trạm 9 (phút 13:15 - Sắp xếp thứ tự): [Câu hỏi | Thứ tự đúng: Bước 1 -> Bước 2 -> Bước 3 | Giải thích]
  + Trạm 10 (phút 14:00 - Phân loại nhóm): [Câu hỏi | Nhóm 1: (các thẻ...); Nhóm 2: (các thẻ...) | Giải thích]
```

#### 3️⃣ Bộ tính năng sư phạm đỉnh cao tích hợp sẵn:
* 🔒 **Chống tua nhanh 100%:** Giám sát 250ms, giật lại vị trí hợp lệ khi học sinh cố tình tua vượt bài giảng.
* 🎯 **Vượt trạm đến khi Đúng & Chuẩn đạt $\ge$ 80%:** Học sinh bắt buộc tự trả lời **ĐÚNG** mới vượt qua được từng trạm câu hỏi và được ghi nhận trọn `+1 điểm` (1 câu hoàn thành). Mọi học sinh kiên trì học hết video đều đạt chuẩn Hoàn thành (`🟢 ĐÃ HOÀN THÀNH`), đồng thời Sổ điểm vẫn thống kê riêng số câu đúng ngay từ lần thử đầu tiên.
* 🛡️ **Giấu giải thích khi sai — Chỉ mở giải thích khi ĐÚNG:** Khi trả lời sai, hệ thống **tuyệt đối không lộ đáp án hay lời giải thích**, chỉ nhắc suy nghĩ lại kèm nút `⏪ Xem lại 30s bài giảng` (câu Đúng/Sai có 3 giây suy ngẫm chống bấm bừa 2 nút liên tiếp). Chỉ khi trả lời **ĐÚNG** mới mở hộp `💡 Hướng dẫn & Giải thích`.
* 📱 **Tối ưu di động tràn màn hình + Đổi tên/lớp 1-chạm + Tự động nhớ tiến độ** khi rớt mạng hay hết pin.
* 📊 **Google Sheets tự động tách tab từng lớp (`6A`, `6B`...)** kèm bảng thống kê Sĩ số, Hoàn thành, Điểm TB thời gian thực.
* ⚙️ **Chế độ Thầy Cô bảo mật tuyệt đối:** Mở khóa tua tự do & nhảy nhanh tới từng trạm câu hỏi để duyệt bài; ô nhập mật mã ẩn hoàn toàn gợi ý mật khẩu trên màn hình học sinh.

#### 4️⃣ 🔑 Hướng dẫn chi tiết 4 tình huống thay đổi mật khẩu Chế độ Thầy Cô:
1. **Tình huống 1 — Đặt mật khẩu riêng ngay từ đầu khi tạo bài mới *(Khuyên dùng)*:** Ghi dòng `- Mật khẩu Chế độ Thầy Cô: [Mật khẩu riêng, ví dụ: Thien2026]` ngay trong câu lệnh tạo video.
2. **Tình huống 2 — Bài giảng đã tạo sẵn trên máy, nhờ AI đổi tự động *(3 giây)*:** Giữ `Shift + Chuột phải` vào thư mục bài giảng chọn `Copy as path` rồi nhắn vào khung chat:
   > *"Em hãy đổi mật khẩu Chế độ Thầy Cô của bài giảng tại đường dẫn: `[Dán đường dẫn thư mục]` thành mật khẩu mới là: `Toan6@2026` giúp tôi."*
3. **Tình huống 3 — Tự đổi thủ công bằng Notepad trên máy tính *(10 giây, không cần mở AI)*:**
   - Mở thư mục bài giảng ngoài Desktop $\to$ Chuột phải vào file **`index.html`** $\to$ chọn **Open with $\to$ Notepad**.
   - Nhấn **`Ctrl + F`**, gõ `TEACHER_PASSWORD` $\to$ sửa `'123456'` thành mật khẩu mới bên trong cặp dấu nháy đơn (ví dụ: `const TEACHER_PASSWORD = '246810';`) $\to$ nhấn **`Ctrl + S`** lưu lại.
4. **Tình huống 4 — Cập nhật mật khẩu mới lên Web Netlify mà KHÔNG BỊ ĐỔI LINK đã gửi học sinh *(3 giây)*:**
   - Mở [app.netlify.com](https://app.netlify.com) $\to$ bấm chọn **tên bài giảng** $\to$ vào tab **`Deploys`** $\to$ **kéo thả lại thư mục bài giảng** vừa đổi mật khẩu vào khung cập nhật. Chờ 3 giây hiện *Published* rồi bấm `Ctrl + F5`: **đường link cũ trên Zalo học sinh giữ nguyên 100%**, mật khẩu mới có hiệu lực ngay!

#### 5️⃣ 🌐 Hướng dẫn bước tiếp theo đưa bài giảng lên Web Netlify miễn phí (Sau khi tạo mới hoặc cập nhật):
> ⚠️ **Quy tắc vàng chống lỗi `404 Not Found`:** Thầy/Cô phải cầm chuột **kéo CẢ THƯ MỤC VÀNG ngoài Desktop** (ví dụ `Web_Video_Tuong_Tac_...`) thả vào Netlify — **tuyệt đối không** mở thư mục ra kéo lẻ file `index.html`!

* **🆕 Khi đưa bài giảng MỚI lên Web lần đầu tiên (30 giây):**
  1. Mở **[app.netlify.com](https://app.netlify.com)** $\to$ đăng nhập miễn phí 1 lần bằng tài khoản **Google (Gmail)**.
  2. Ở cột trái bấm **`Projects`** *(hoặc `Sites`)* $\to$ góc phải bấm **`Add new project`** *(hoặc `Add new site`)* $\to$ chọn **`Deploy manually`**.
  3. Cầm **cả thư mục bài giảng ngoài Desktop** kéo thả vào vòng tròn nét đứt $\to$ chờ 3 giây hiện **`Published`** màu xanh lá!
  4. **Đổi tên đường link đẹp:** Vào **`Project configuration`** *(hoặc `Site configuration`)* $\to$ **`Change project name`** *(hoặc `Change site name`)* $\to$ đặt tên bài không dấu nối bằng gạch ngang (ví dụ: `toan6-bai6-thcs-unghoe`) $\to$ bấm **`Save`**.
  5. Mở link vừa tạo $\to$ bấm **`⚙️ Thầy Cô: TẮT`** nhập mật khẩu duyệt thử các câu hỏi $\to$ tắt Chế độ Thầy Cô rồi gửi link vào nhóm Zalo lớp!
* **🔄 Khi CẬP NHẬT lại bài đã có (sau khi Đổi mật khẩu / Sửa câu hỏi — Giữ nguyên 100% link cũ):**
  1. Mở **[app.netlify.com](https://app.netlify.com)** $\to$ nhấp trực tiếp vào **tên bài giảng cũ** trong danh sách *(không bấm Add new project)*.
  2. Bấm vào tab **`Deploys`** $\to$ kéo thả **cả thư mục vừa cập nhật ngoài Desktop** vào khung nét đứt giữa trang $\to$ chờ 3 giây hiện **`Published`** $\to$ bấm **`Ctrl + F5`** làm mới trang web!

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
