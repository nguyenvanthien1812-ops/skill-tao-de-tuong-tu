# Bước 5bis — Xuất PDF đẹp chuẩn in ấn (6 theme, tùy chỉnh)

> Đọc khi giáo viên muốn xuất PDF / in đẹp.
> *(Tài liệu tham chiếu của skill `tao-de-toan-tuong-tu` — được tách ra từ `SKILL.md` để SKILL.md gọn; nội dung quy tắc giữ nguyên.)*

---

## 🖨️ Bước 5: Xuất PDF Đẹp Chuẩn In Ấn Qua LaTeX (TÙY CHỌN — KHUYÊN DÙNG)

> [!TIP]
> **KHI NÀO DÙNG:** Giáo viên muốn in ấn hoàn hảo, không bao giờ lệch font. PDF từ LaTeX đẹp như sách giáo khoa, chuẩn vector 600 DPI, in trên bất kỳ máy nào đều giống nhau.

### 5.1 Cách Kích Hoạt (Giáo Viên Không Cần Biết Lệnh)

Agent **TỰ ĐỘNG GỢI Ý** sau khi tạo đề xong. Giáo viên cũng có thể nói:
- *"xuất pdf"*, *"in ra"*, *"tạo pdf"*, *"in đẹp"*, *"pdf như sách"*
- *"cả word và pdf"*, *"xuất cả hai"*

### 5.2 Cú Pháp Gọi Script

```python
from scripts.pdf_exam_exporter import ExamPDFExporter, export_exam_pdf

# Cách 1 — 1-click, cả 2 bản
results = export_exam_pdf(
    exam_data=exam_data,   # Dict chuẩn (tương thích gdpt2018_validator.py)
    meta={
        "series_name":    "TỔNG ÔN TẬP THPTQG\nMÔN TOÁN 2026",
        "exam_code":      "0103",
        "exam_title":     "ĐỀ THI TỐT NGHIỆP THPT",
        "subject":        "Toán",
        "grade":          12,
        "school_year":    "2025 -- 2026",
        "duration_minutes": 90,
    },
    output_dir="output/",
    basename="MA_DE_0103",
    theme="teal",           # Hoặc: navy / red / minimal / purple / classic
    style_config={          # Tùy chỉnh thêm (nếu có)
        "school_name":  "Tên Trường",
        "contact_info": "📞 0912.345.678",
        "footer_right": "Chúc em làm bài tốt!",
    },
)
# Kết quả:
# output/MA_DE_0103_DE_HOC_SINH.pdf  ← Phát cho học sinh
# output/MA_DE_0103_LOI_GIAI_GV.pdf  ← Giáo viên có lời giải

# Cách 2 — Tùy chỉnh từ chat
exporter = ExamPDFExporter(theme='teal')
exporter.apply_chat_command("đổi tên trường là THPT Chu Văn An")
exporter.apply_chat_command("thêm logo logo_truong.png")
exporter.apply_chat_command("dùng theme đỏ")
exporter.save_profile("co_lan_thpt_chu_van_an")  # Lưu để dùng lại
results = exporter.export_both(exam_data, meta, output_dir="output/")
```

### 5.3 Hệ Thống 6 Theme Màu Sắc

| Theme | Màu chính | Phù hợp |
|:------|:---------|:--------|
| `teal` | 🟢 Xanh teal #1A7070 | Mặc định — chuyên nghiệp (như ảnh mẫu) |
| `navy` | 🔵 Xanh navy #1B3A6B | Thi học kỳ, tốt nghiệp — trang trọng |
| `red` | 🔴 Đỏ #C0392B | Ôn luyện cường độ cao — nổi bật |
| `minimal` | ⚫ Trắng đen #2C2C2C | In số lượng lớn — tiết kiệm mực |
| `purple` | 🟣 Tím #6C3483 | Trường THCS, chuyên — sáng tạo |
| `classic` | 🔷 Xanh dương #1A5276 | Chuẩn SGK truyền thống Việt Nam |

### 5.4 Tùy Chỉnh Qua Chat Tự Nhiên

Agent nhận diện và áp dụng ngay các lệnh:

| Giáo viên nói | Agent làm |
|:-------------|:---------|
| *"dùng theme đỏ"* | Chuyển sang theme `red` |
| *"đổi tên trường là Nguyễn Trãi"* | Cập nhật header |
| *"thêm logo logo.png"* | Chèn logo vào header |
| *"bỏ lời giải đi, chỉ in đề thôi"* | Xuất bản học sinh (no solution) |
| *"in 2 cột"* | Layout 2 cột tiết kiệm giấy |
| *"thêm watermark bản nháp"* | Chèn "BẢN NHÁP" chìm mờ |
| *"lưu style này lại"* | `save_profile(teacher_name)` |
| *"dùng style hôm trước"* | `load_teacher_profile(name)` |

### 5.5 Yêu Cầu Kỹ Thuật

- **LaTeX cần cài**: MikTeX (Windows) hoặc TeX Live (Linux/Mac)
- **Trình biên dịch**: xelatex (ưu tiên) hoặc pdflatex (fallback)
- **Cài MikTeX**: https://miktex.org/download (miễn phí, 1-click)
- **Script kiểm tra**: `python scripts/check_and_setup_env.py` — tự kiểm tra và hướng dẫn cài

---
