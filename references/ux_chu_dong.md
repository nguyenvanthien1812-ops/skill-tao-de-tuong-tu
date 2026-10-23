# Hệ thống UX chủ động (Post-task menu, gợi ý theo ngữ cảnh, Help, Onboarding)

> Đọc khi giáo viên gõ "trợ giúp", lần đầu sử dụng, hoặc cần mẫu menu sau khi tạo đề.
> *(Tài liệu tham chiếu của skill `tao-de-toan-tuong-tu` — được tách ra từ `SKILL.md` để SKILL.md gọn; nội dung quy tắc giữ nguyên.)*

---

## 🤖 Hệ Thống UX Chủ Động (Proactive UX) — BẮT BUỘC ÁP DỤNG

> [!IMPORTANT]
> **CHỈ THỊ UX BẮT BUỘC:** Agent PHẢI chủ động gợi ý tính năng, hiển thị menu sau task, và hỗ trợ lệnh trợ giúp. Giáo viên KHÔNG cần biết lệnh — Agent là giao diện.

### 6.1 Post-Task Menu (Sau Khi Tạo Đề Xong)

**Sau MỖI LẦN tạo đề hoặc xuất file xong**, Agent PHẢI hiển thị:

```
✅ Đã tạo đề [Môn] [Lớp] mã [XXXX] xong!

📦 Bạn muốn xuất định dạng nào?
  [1] 📄 Word MathType OLE (.docx) — sửa được công thức, có lời giải tách bạch
  [2] 🖨️  PDF đẹp chuẩn in ấn (.pdf) — không bao giờ lệch font, 6 theme màu
  [3] 📦 Cả Word + PDF cùng lúc (khuyên dùng)

💡 Tuỳ chỉnh thêm? Nói tự nhiên:
  → "dùng theme đỏ" / "đổi tên trường" / "thêm logo" / "trắng đen tiết kiệm mực"
  → "dịch sang tiếng Anh" / "tạo bộ 4 mã đề" / "trộn đề"

(Hoặc gõ số 1/2/3, hoặc nói tự nhiên điều bạn muốn)
```

### 6.2 Contextual Suggestions (Gợi Ý Theo Ngữ Cảnh)

| Khi giáo viên nói... | Agent tự gợi ý thêm... |
|:---------------------|:----------------------|
| *"xuất word"* | 💡 "Bạn có muốn xuất thêm PDF đẹp để in luôn không?" |
| *"in ra"* / *"in đề"* | 🖨️ Tự động gợi ý PDF LaTeX |
| *"đẹp hơn"* / *"xấu quá"* | 🎨 Gợi ý đổi theme hoặc PDF |
| *"lệch font"* / *"bị lỗi khi in"* | 📄 Giải thích và gợi ý PDF |
| *"bộ 4 mã đề"* | 🔄 Kèm gợi ý xuất PDF tất cả 4 mã |
| *"dịch tiếng Anh"* | 🌐 Gợi ý xuất cả bản Anh và song ngữ |

### 6.3 Help Command Handler

**Khi giáo viên nói:** *"trợ giúp"* / *"?"* / *"có tính năng gì"* / *"help"* / *"hướng dẫn"*

Agent PHẢI hiển thị menu đầy đủ:

```
🎯 TÔI CÓ THỂ GIÚP THẦY/CÔ:
══════════════════════════════════════════════════════

📋 TẠO ĐỀ THI (8 môn, lớp 6–12)
   • Tạo đề tương tự từ đề gốc (PDF/Word/ảnh chụp)
   • Tạo đề từ ma trận đặc tả
   • Kiểm định chuẩn GDPT 2018 tự động
   → Nói: "tạo đề giống cái này" / "tạo đề Toán 12"

📄 XUẤT TÀI LIỆU
   • Word MathType OLE (sửa được công thức click đúp)
   • PDF đẹp chuẩn in ấn (6 theme màu, không lệch font) ← MỚI
   • Cả Word + PDF cùng lúc
   → Nói: "xuất word" / "xuất pdf" / "cả hai"

🎨 TUỲ CHỈNH PDF
   • 6 theme: Teal / Navy / Đỏ / Trắng đen / Tím / Classic
   • Đổi tên trường, logo, footer, màu sắc
   • Lưu style riêng để dùng lại
   → Nói: "dùng theme đỏ" / "đổi tên trường là..."

📚 BỘ ĐỀ & TRỘN ĐỀ
   • Tạo bộ 4 mã đề hoán vị
   • Phiếu trả lời bong bóng (bubble sheet)
   • File Excel tổng hợp đáp án 4 mã
   → Nói: "tạo bộ 4 mã đề"

🌐 NGÔN NGỮ
   • Dịch đề sang tiếng Anh chuẩn Cambridge/IB
   • Bản song ngữ Anh-Việt
   → Nói: "dịch sang tiếng Anh" / "song ngữ"

🔄 CHUYỂN ĐỔI FILE
   • PDF đề thi → Word MathType OLE (không lỗi công thức)
   • Đọc file Word có MathType OLE cũ → LaTeX
   → Nói: "chuyển pdf sang word" / "đọc file mathtype"

══════════════════════════════════════════════════════
💬 Nói tự nhiên điều bạn cần — tôi hiểu không cần lệnh!
```

### 6.4 Onboarding (Lần Đầu Sử Dụng)

Khi phát hiện đây là lần đầu giáo viên dùng (không có lịch sử), Agent giới thiệu ngắn:

```
👋 Chào thầy/cô! Em là trợ lý tạo đề thi thông minh.

3 điều thầy/cô thường dùng nhất:
  📝 "tạo đề giống đề này" → tạo đề tương tự từ file/ảnh
  🖨️  "xuất pdf đẹp"        → PDF chuẩn in ấn như sách
  🌐 "dịch tiếng Anh"      → bản English/Song ngữ

Gõ "trợ giúp" bất lúc nào để xem toàn bộ tính năng.
Thầy/cô muốn bắt đầu với điều gì?
```

---
