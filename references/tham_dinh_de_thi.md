# Quy Trình Thẩm Định & Rà Soát Đề Thi, Lời Giải Chuẩn GDPT 2018 (Toán THCS & THPT)

> File này quy định toàn bộ tiêu chí, quy trình kỹ thuật và cơ chế tương tác tự động hóa của Bộ công cụ **Thẩm định & Rà soát Đề kiểm tra** tích hợp trong skill `tao-de-toan-tuong-tu`.

---

## 🎯 Mục Tiêu & Phạm Vi Ứng Dụng

Khi giáo viên yêu cầu:
- *"thẩm định đề thi"*, *"rà soát đề thi"*, *"kiểm tra đề thi và lời giải"*
- *"xem đề đã bám sát ma trận chưa"*, *"kiểm tra xem có vượt chương trình không"*
- *"bộ công cụ kiểm tra rà soát đề"*

Bộ công cụ sẽ thực hiện:
1. **Đọc tự động 3 file đầu vào**:
   - File 1: Khung Ma trận & Bản đặc tả (`.docx`)
   - File 2: Đề kiểm tra học sinh (`.docx`)
   - File 3: Hướng dẫn chấm & Thang điểm (`.docx`)
2. **Kiểm tra 42 tiêu chí chất lượng** chia làm 7 nhóm nghiêm ngặt (dựa trên mẫu Thông báo kết quả thẩm định đề của Hội đồng thẩm định chuyên môn).
3. **Xuất 2 tài liệu báo cáo chuyên nghiệp**:
   - `Bien_ban_tham_dinh_ToanX_MaYYY.docx`: Biên bản thẩm định Word hoàn chỉnh, có bảng biểu liền nét, chữ ký Hội đồng.
   - `Dashboard_tham_dinh_ToanX_MaYYY.xlsx`: Bảng tính Excel thống kê trực quan mức độ đạt/chưa đạt.
4. **Trình Kế hoạch sửa chữa (Correction Plan)** lên khung chat terminal / conversation:
   - Liệt kê lỗi bắt buộc sửa (Critical) và cảnh báo sư phạm (Warning).
   - Liệt kê các lỗi có thể sửa tự động (Auto-fixable).
5. **Chờ giáo viên duyệt ("OK" / "Đồng ý")**:
   - Nếu giáo viên đồng ý $\rightarrow$ chạy module `auto_fixer` để sửa trực tiếp file Word và xuất ra file có hậu tố `_FIXED.docx`, giữ nguyên 100% file gốc.

---

## 📊 Hệ Thống 42 Tiêu Chí Thẩm Định (7 Nhóm)

### Nhóm A: Ma Trận & Bản Đặc Tả (A01 – A06)
- **A01**: Tổng điểm toàn ma trận bắt buộc $= 10,0$ điểm.
- **A02**: Tỉ lệ điểm giữa các mức độ nhận thức (NB : TH : VD : VDC) tuân thủ đúng chuẩn GDPT 2018 (ví dụ 4:3:2:1 hoặc 5:3:1.5:0.5).
- **A03**: Có đầy đủ các dòng tổng kết bắt buộc cuối bảng (`TỔNG`, `TỈ LỆ %`, `TỈ LỆ CHUNG`).
- **A04**: Số lượng câu hỏi trắc nghiệm trong ma trận khớp chính xác với số câu trong đề thi.
- **A05**: Số lượng ý hỏi tự luận trong bản đặc tả khớp chính xác với đề thi.
- **A06**: Mỗi mức độ nhận thức của từng bài học được tách thành dòng riêng và mã câu hỏi nằm trên cùng dòng tương ứng.

### Nhóm B: Phần Trắc Nghiệm Khách Quan (B01 – B05)
- **B01**: Đúng thang điểm quy định (mỗi câu 0,25 điểm hoặc theo ma trận).
- **B02**: Mỗi câu trắc nghiệm có đầy đủ 4 phương án $A, B, C, D$.
- **B03**: Phân bổ đáp án đúng cân bằng giữa $A, B, C, D$ (không thiên lệch quá 60% về 1 phương án).
- **B04**: Duy nhất 1 đáp án đúng; các phương án nhiễu có tính sư phạm, bẫy lỗi sai học sinh thường gặp.
- **B05**: Không bị lỗi lặp đáp án hoặc các phương án phủ định/mâu thuẫn hiển nhiên.

### Nhóm C: Phần Tự Luận (C01 – C05)
- **C01**: Tổng điểm phần tự luận khớp chính xác với ma trận (thường từ 5,0 đến 7,0 điểm).
- **C02**: Mỗi bài/ý tự luận đều ghi rõ số điểm tương ứng (ví dụ: `a) (0,5 điểm)`).
- **C03**: Các bài hình học hoặc ứng dụng thực tế có hình vẽ kỹ thuật sắc nét, minh họa rõ ràng.
- **C04**: Cuối đề thi có dấu ngắt trang và dòng kết thúc chuẩn mực: `--------------------- HẾT ----------------------`.
- **C05**: Không vượt quá giới hạn kiến thức chương trình tại thời điểm kiểm tra.

### Nhóm D: Hướng Dẫn Chấm & Biểu Điểm (D01 – D04)
- **D01**: Mã đề trong Hướng dẫn chấm khớp 100% với Mã đề trên đề thi.
- **D02**: Bảng đáp án trắc nghiệm đầy đủ, rõ ràng từng câu.
- **D03**: Lời giải tự luận chia nhỏ barem điểm đến từng $0,25$ điểm (hoặc $0,1$ điểm).
- **D04**: Có khung quy định "Lưu ý khi chấm" (học sinh làm cách khác đúng vẫn cho điểm tối đa, làm đúng đến đâu cho điểm đến đó).

### Nhóm E: Định Dạng & Kỹ Thuật Soạn Thảo (E01 – E05)
- **E01**: Bản Đề thi 100% công thức toán ở định dạng MathType OLE (`Equation.DSMT4`), 0% ký hiệu `$` sót lại.
- **E02**: Bản HDC 100% công thức toán ở định dạng MathType OLE, 0% ký hiệu `$` sót lại.
- **E03**: Đồng bộ cỡ chữ công thức MathType (chuẩn 13pt–14pt toàn bài, phát hiện lệch cỡ to/nhỏ do sao chép từ nhiều nguồn khác nhau). *(Có Auto-fix)*
- **E04**: Phân số và biểu thức tầng hiển thị chuẩn, không bị co nhỏ dạng inline `\frac` (chuyển sang Full-size display `\dfrac`). *(Có Auto-fix)*
- **E05**: Toàn bộ bảng biểu trong đề và HDC kẻ khung viền liền nét 100% (`Table Grid`), không mất nét viền ở các ô gộp.

### Nhóm F: Đối Chiếu Chéo 3 File (Cross-Check F01 – F03)
- **F01**: Từng câu hỏi trên đề khớp 100% với yêu cầu cần đạt và mức độ nhận thức trong Bản đặc tả.
- **F02**: Tổng điểm nhất quán tuyệt đối giữa Ma trận $\leftrightarrow$ Đề thi $\leftrightarrow$ Hướng dẫn chấm.
- **F03**: Số lượng câu TN và bài TL nhất quán giữa 3 file.

### Nhóm G: Tính Sư Phạm & Phân Hóa (G01 – G03)
- **G01**: Ngữ cảnh bài toán thực tế chuẩn mực, số liệu thực tiễn logic.
- **G02**: Câu vận dụng cao (VDC) có tính phân hóa rõ nét để chọn lọc học sinh giỏi, không đánh đố mẹo mực.
- **G03**: Diễn đạt đề thi trong sáng, không dùng từ địa phương, không gây hiểu lầm đa nghĩa.

---

## 🔍 Quy Chuẩn Rà Soát Từng Công Thức & Kế Hoạch Sửa Chữa Chi Tiết (Formula-Level Audit Protocol)

> [!IMPORTANT]
> Khi thẩm định đề thi, Agent và Thẩm định viên **BẮT BUỘC rà soát tỉ mỉ từng công thức toán học** (từ câu đầu đến câu cuối trong cả Đề thi và Hướng dẫn chấm), tuyệt đối không chỉ kiểm tra hình thức bên ngoài.

### 1. Quy Trình Rà Soát Công Thức 3 Lớp:
1. **Lớp 1 — Tính đúng đắn toán học & logic nghiệm**:
   - Giải soát lại từng bước biến đổi đại số, giải phương trình/hệ phương trình/bất phương trình.
   - Kiểm tra điều kiện xác định (ĐKXĐ), tập xác định, điều kiện có nghĩa của căn thức, phân thức.
   - Kiểm tra tính toán số học, quy đồng mẫu số, nhân chia dấu âm/dương, khai triển hằng đẳng thức.
   - Đảm bảo 4 phương án trắc nghiệm chỉ có duy nhất 1 đáp án đúng, các phương án nhiễu phản ánh đúng bẫy sai lầm của học sinh.
2. **Lớp 2 — Chuẩn mực ký hiệu & sư phạm GDPT 2018**:
   - Ký hiệu toán học chuẩn mực: dấu suy ra $\Rightarrow$ vs tương đương $\Leftrightarrow$, ký hiệu góc $\widehat{ABC}$, độ dài đoạn thẳng, vectơ $\vec{u}$, tập hợp $\in, \subset$.
   - Ký hiệu đơn vị chuẩn quốc tế: $\mathrm{cm, m^2, km/h}$, viết thẳng đứng không nghiêng; tên điểm hình học in hoa thẳng đứng.
3. **Lớp 3 — Chuẩn kỹ thuật & định dạng file**:
   - 100% công thức nhúng chuẩn MathType OLE (`Equation.DSMT4`), $0\%$ ký hiệu `$` thô sót lại.
   - Đồng bộ cỡ chữ 13pt–14pt toàn bài, không lệch to nhỏ.
   - Phân số hiển thị đủ chiều cao (`\dfrac`), không bị co nhỏ dạng inline fractions.

### 2. Định Dạng Kế Hoạch Sửa Chữa Chi Tiết Từng Công Thức (Bắt Buộc Trình Bày Trong Báo Cáo):
Khi phát hiện công thức có vấn đề, Agent bắt buộc xuất bảng Kế hoạch sửa chữa theo cấu trúc:
| STT | Vị trí (File & Câu) | Công thức hiện tại | Vấn đề / Lỗi sai | Công thức sửa chuẩn | Hướng xử lý |
|:---:|:---|:---|:---|:---|:---|
| 1 | Đề thi - Câu 5 | $x^2 - 4x + 4 = 0 \Leftrightarrow x = -2$ | Sai dấu nghiệm phương trình bậc 2 | $x^2 - 4x + 4 = 0 \Leftrightarrow (x - 2)^2 = 0 \Leftrightarrow x = 2$ | Thủ công |
| 2 | HDC - Bài 2b | $\frac{2x+1}{x-3}$ (inline nhỏ) | Phân số bị co nhỏ, khó đọc | $\dfrac{2x+1}{x-3}$ (Full-size) | Auto-fix |
| 3 | Đề thi - Câu 12 | `$(d): y = 2x + 1$` | Sót ký hiệu $ thô chưa qua MathType | Đối tượng MathType OLE chuẩn | Auto-fix |

---

## 💻 Hướng Dẫn Sử Dụng Bộ Công Cụ

### Cách 1: Chạy 1-Click qua file BAT (Dành cho Giáo viên)
Giáo viên nhấp đúp chuột vào file:
```text
THAM_DINH_DE_THI.bat
```
*(Nằm tại thư mục gốc của phần mềm)*.
Cửa sổ tương tác mở ra, Thầy/Cô chỉ cần kéo thả 3 file `.docx` vào và nhấn Enter.

### Cách 2: Chạy qua Dòng lệnh CLI (Dành cho Lập trình viên / Agent)
```bash
python .agents/skills/tao-de-toan-tuong-tu/scripts/tham_dinh/exam_reviewer_cli.py \
  --matrix  "đường_dẫn_ma_tran.docx" \
  --exam    "đường_dẫn_de_thi.docx" \
  --rubric  "đường_dẫn_huong_dan_cham.docx" \
  --output  "thư_mục_lưu_kết_quả" \
  --grade   8 \
  --school  "THCS Chu Văn An" \
  --teacher "Nguyễn Thị Mai"
```

### Cách 3: Agent Tự Động Thực Thi Trong Hội Thoại
Khi người dùng cung cấp đường dẫn hoặc file trong chat:
1. Agent gọi script `exam_reviewer_cli.py` với cờ `--no-fix` để chạy thẩm định và sinh báo cáo.
2. Trình bảng tóm tắt kết quả và Kế hoạch sửa chữa (Correction Plan) cho người dùng xem.
3. Hỏi người dùng: *"Thầy/Cô có đồng ý để em tự động sửa các mục có thể Auto-fix (như bổ sung dấu HẾT, sửa mã đề HDC, thêm lưu ý chấm...) không ạ?"*
4. Khi người dùng xác nhận **"OK" / "Đồng ý"** $\rightarrow$ Agent gọi module `auto_fixer` để sửa và cung cấp đường dẫn file `_FIXED.docx` hoàn thiện.
