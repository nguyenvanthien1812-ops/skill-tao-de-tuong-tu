# 📋 BỘ CÔNG CỤ THẨM ĐỊNH ĐỀ KIỂM TRA MÔN TOÁN (GDPT 2018)
**Phiên bản 1.0** | Ưu tiên Toán THCS lớp 6–9 | Có thể mở rộng cho mọi môn

---

## 🚀 Cách dùng nhanh (cho Thầy/Cô)

### Bước 1: Nhấp đúp vào file
```
THAM_DINH_DE_THI.bat
```
*(nằm tại thư mục gốc `d:\skill-quan-trong\`)*

### Bước 2: Cung cấp 3 file
Nhập đường dẫn hoặc **kéo thả file** vào cửa sổ:
1. **File Ma trận / Bản đặc tả** (`.docx`)
2. **File Đề thi** dành cho học sinh (`.docx`)
3. **File Hướng dẫn chấm** / Lời giải (`.docx`)

### Bước 3: Đọc kết quả
Hệ thống tự động xuất 2 file báo cáo ra thư mục chỉ định:
- `Bien_ban_tham_dinh_ToanX_MaYYY.docx` — Biên bản thẩm định (in được)
- `Dashboard_tham_dinh_ToanX_MaYYY.xlsx` — Dashboard tổng quan

---

## 📊 Các tiêu chí kiểm tra (42 tiêu chí, 7 nhóm)

| Nhóm | Nội dung | Số tiêu chí |
|------|----------|-------------|
| **A** | Ma trận & Bản đặc tả | 6 |
| **B** | Phần Trắc nghiệm | 5 |
| **C** | Phần Tự luận | 5 |
| **D** | Hướng dẫn chấm | 4 |
| **E** | Định dạng MathType OLE | 3 |
| **F** | Đối chiếu chéo 3 file | 3 |
| **G** | Phân hóa & Chất lượng | 3 |

---

## ⚙️ Yêu cầu hệ thống

- **Python 3.9+** (tải tại [python.org](https://python.org))
- Thư viện: `python-docx`, `openpyxl`, `lxml` *(tự động cài khi chạy BAT)*
- Windows 10/11

---

## 🧑‍💻 Dùng qua dòng lệnh (nâng cao)

```bat
cd d:\skill-quan-trong\.agents\skills\tao-de-toan-tuong-tu\scripts

python tham_dinh\exam_reviewer_cli.py ^
  --matrix  "đường_dẫn\ma_tran.docx" ^
  --exam    "đường_dẫn\de_hoc_sinh.docx" ^
  --rubric  "đường_dẫn\huong_dan_cham.docx" ^
  --output  "đường_dẫn\thu_muc_bao_cao" ^
  --grade   8 ^
  --school  "Trường THCS ABC" ^
  --teacher "Nguyễn Văn A"
```

---

## 🔄 Quy trình thẩm định

```
3 file .docx  →  Trích xuất dữ liệu  →  Kiểm tra 42 tiêu chí
     ↓
Biên bản Word + Dashboard Excel  →  Kế hoạch sửa chữa
     ↓
(Các lỗi có thể auto-fix)  →  Hỏi GV xác nhận  →  Sửa file tự động
```

---

## 📁 Cấu trúc thư mục

```
d:\skill-quan-trong\
├── THAM_DINH_DE_THI.bat              ← Launcher chính (double-click để chạy)
├── README_THAM_DINH.md               ← Hướng dẫn này
└── .agents\skills\tao-de-toan-tuong-tu\scripts\tham_dinh\
    ├── __init__.py
    ├── exam_extractor.py             ← Đọc 3 file → ExamData
    ├── exam_validator.py             ← Kiểm tra 42 tiêu chí
    ├── report_generator.py           ← Xuất biên bản Word + Excel
    ├── auto_fixer.py                 ← Sửa tự động lỗi được duyệt
    └── exam_reviewer_cli.py          ← CLI entry point
```

---

## ❓ Câu hỏi thường gặp

**Q: Tool có sửa file gốc không?**
A: Không. Tool chỉ ĐỌC file gốc, mọi sửa đổi tự động đều được lưu vào file mới có hậu tố `_FIXED.docx`.

**Q: Đề môn khác (Lý, Hóa...) có dùng được không?**
A: Phiên bản 1.0 tối ưu cho Toán. Môn khác sẽ được hỗ trợ trong phiên bản tiếp theo.

**Q: Tôi không có Python, làm sao chạy?**
A: Tải Python 3.11 tại [python.org/downloads](https://python.org/downloads), chọn "Add to PATH" khi cài. Sau đó chạy BAT như bình thường.

---

*Bộ công cụ được phát triển phục vụ công tác thẩm định đề kiểm tra theo chuẩn GDPT 2018.*
