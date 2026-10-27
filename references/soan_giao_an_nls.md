# SOẠN GIÁO ÁN & KẾ HOẠCH BÀI DẠY TÍCH HỢP NĂNG LỰC SỐ (NLS) & AI

Tài liệu hướng dẫn quy chuẩn sư phạm và kỹ thuật chèn Năng lực số (NLS), AI, HSKT và Tiếng Anh vào Kế hoạch bài dạy theo GDPT 2018.

---

## 1. HAI LUỒNG XỬ LÝ CHÍNH
* **Luồng 1 (Chèn vào giáo án có sẵn - Word DOCX)**:
  - Áp dụng công nghệ **XML Injection** (`scripts/inject_nls_docx.py`).
  - Giữ nguyên 100% bố cục, căn lề, bảng 2 cột và các đối tượng nhúng MathType OLE (`Equation.DSMT4`).
* **Luồng 2 (Soạn mới từ đầu theo SGK)**:
  - Tiểu học (Lớp 1-5): Soạn theo khung **Công văn 2345/BGDĐT-GDTH**.
  - THCS & THPT (Lớp 6-12): Soạn theo khung **Công văn 5512/BGDĐT-GDTrH** (Bảng 2 cột).

---

## 2. BẢNG PHÂN TẦNG MÃ NĂNG LỰC SỐ (THÔNG TƯ 02/2025/TT-BGDĐT)
* **Tiểu học (Lớp 1-3)**: Mức `CB1` (ví dụ: `1.1.CB1a`, `2.1.CB1a`...).
* **Tiểu học (Lớp 4-5)**: Mức `CB2` (ví dụ: `1.1.CB2b`, `2.2.CB2a`...).
* **THCS (Lớp 6-7)**: Mức `TC1` (ví dụ: `1.1.TC1a`, `2.4.TC1a`, `3.1.TC1a`, `5.2.TC1a`, `5.3.TC1a`, `6.2.TC1a`...).
* **THCS (Lớp 8-9)**: Mức `TC2` (ví dụ: `1.1.TC2b`, `2.4.TC2a`, `3.1.TC2b`, `5.3.TC2a`...).
* **THPT (Lớp 10-12)**: Mức `NC1 / NC2` (ví dụ: `1.1.NC1a`, `3.1.NC1a`, `NLc.C2`, `NLd.D1`...).

---

## 3. KHUNG NĂNG LỰC AI (QUYẾT ĐỊNH 3439/QĐ-BGDĐT & QĐ 2422)
* `NLa`: Tư duy lấy con người làm trung tâm.
* `NLb`: Đạo đức AI & bảo mật dữ liệu.
* `NLc`: Kĩ thuật & Ứng dụng AI (`NLc.C1`: nhận biết AI; `NLc.C2`: ra lệnh và sử dụng AI tra cứu, đối chiếu).
* `NLd`: Thiết kế hệ thống AI.
* **Nguyên tắc bắt buộc**: Phải có cụm từ *"dưới sự định hướng của GV"* và *"đối chiếu với SGK/tài liệu chuẩn trước khi báo cáo"*.

---

## 4. QUY TẮC SƯ PHẠM ĐPQ (ĐỌC – PHÂN TÍCH – QUYẾT ĐỊNH)
* **Chống bịa công cụ**: Hoạt động học sinh đọc sách, nghe giảng, trả lời miệng $\to$ **CẤM CHÈN NLS/AI**.
* **Chỉ chèn vào `d) Tổ chức thực hiện`**:
  * Trọng tâm ở **Bước 2 (Thực hiện nhiệm vụ)** và **Bước 3 (Báo cáo)** khi HS trực tiếp thao tác công nghệ số.
  * Tuyệt đối không chèn vào Mục tiêu, Nội dung, Sản phẩm của từng hoạt động.

---

## 5. MÃ MÀU CHUẨN XUẤT WORD
* 🔵 Năng lực số: `<w:color w:val="0055D4"/>` (Xanh dương, in đậm).
* 🟣 Năng lực AI: `<w:color w:val="7030A0"/>` (Tím, in đậm).
* 🟢 Hòa nhập HSKT: `<w:color w:val="008000"/>` (Xanh lá, in nghiêng + đậm).
* 🟠 Tiếng Anh: `<w:color w:val="B45309"/>` (Cam đất, in nghiêng + đậm).

---

## 6. QUY CHUẨN XỬ LÝ PHỤ LỤC III / PHÂN PHỐI CHƯƠNG TRÌNH (PPCT)
Nhà trường và tổ chuyên môn đầu năm học đều ban hành **Kế hoạch giáo dục của tổ chuyên môn (Phụ lục III)** kèm bảng Phân phối chương trình phân công cụ thể từng bài dạy, số tiết, Yêu cầu cần đạt, thiết bị dạy học và mã Năng lực số/AI đã được phê duyệt.

Khi giáo viên yêu cầu tích hợp NLS/AI vào giáo án:
1. **Trường hợp có Phụ lục III / PPCT**:
   - AI **BẮT BUỘC** trích xuất đúng dòng tương ứng với tên bài và phân phối tiết của bài dạy.
   - Bốc chính xác các mã chỉ báo Năng lực số (ví dụ: `1.1.TC1a`, `2.4.TC1a`) và nội dung AI (ví dụ: `NLc.C2`) mà tổ chuyên môn đã phân công.
   - **Tuyệt đối không tự ý thay đổi hoặc tự bịa mã khác** làm lệch hồ sơ chuyên môn của tổ khi đoàn kiểm tra, thanh tra đối chiếu.
2. **Trường hợp giáo viên copy 1 dòng từ PPCT vào chat**:
   - AI sử dụng ngay thông tin đó để đưa vào mục Mục tiêu và Tiến trình dạy học mà không cần hỏi lại.
3. **Trường hợp trường chưa phân công mã trong Phụ lục III**:
   - AI tự động đối chiếu Khung năng lực số (Thông tư 02/2025/TT-BGDĐT) và Khung AI (Quyết định 3439/QĐ-BGDĐT) theo đúng cấp học để đề xuất 1-2 mã phù hợp nhất với hoạt động thực tế của bài học.
