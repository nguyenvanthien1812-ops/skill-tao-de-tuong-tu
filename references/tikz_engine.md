# Bộ máy render TikZ & LaTeX 300 DPI

> Đọc khi cần render mã TikZ/LaTeX ra PNG/PDF hoặc biên dịch đề nhiều trang.
> *(Tài liệu tham chiếu của skill `tao-de-toan-tuong-tu` — được tách ra từ `SKILL.md` để SKILL.md gọn; nội dung quy tắc giữ nguyên.)*

---

## 🎨 Bộ Máy Render Mã TikZ & LaTeX 300 DPI (TikZ Engine Tích Hợp Sẵn)

Nhằm tối ưu hóa việc tái sử dụng các kho tài nguyên đề thi LaTeX/TikZ khổng lồ của giáo viên, Skill tích hợp sẵn **Bộ máy Render TikZ Engine (`scripts/tikz_renderer.py`)** với cơ chế hoạt động kép:

1. **Local Engine (MikTeX / TeX Live Offline)**:
   - Tự động nhận diện trình biên dịch `pdflatex`, `xelatex`, `lualatex` trên máy tính.
   - Kết hợp thư viện đồ họa vector `PyMuPDF (fitz)` biên dịch và xuất trực tiếp ảnh PNG độ phân giải cao **300 - 600 DPI** trong vòng 1-2 giây.
   - Tự động cắt sạch phần viền trắng dư thừa (`trim_whitespace`) giúp hình ảnh vừa vặn tuyệt đối khi chèn vào văn bản Word.

2. **Cloud Fallback Engine (Không Lo Thiếu Môi Trường)**:
   - Nếu máy tính của giáo viên chưa cài đặt TeX engine (hoặc cài thiếu gói), hệ thống tự động định tuyến sang API đám mây render ngầm trả về ảnh PNG chuẩn 100%, bảo đảm không bao giờ báo lỗi hay gián đoạn trải nghiệm của giáo viên.

3. **Hỗ Trợ Toàn Diện Các Gói Chuyên Ngành Giáo Dục**:
   - `tkz-tab`: Dựng bảng biến thiên, bảng xét dấu có mũi tên cong, tiệm cận đôi $\parallel$, cực trị chuẩn 100% định dạng đề thi THPT Quốc gia.
   - `tkz-euclide`: Dựng hình học phẳng, tam giác, đường tròn, góc vuông, trung điểm, phân giác sắc nét.
   - `pgfplots`: Vẽ đồ thị hàm số giải tích ($Oxy$), mặt cong 3D, hệ tọa độ có lưới ô vuông.
   - `circuitikz`: Sơ đồ mạch điện xoay chiều/1 chiều ($R, L, C$, nguồn điện, vôn kế, ampe kế) cho môn Vật lý.
   - `chemfig`: Công thức cấu tạo mạch hở, mạch vòng benzen, este, amino acid cho môn Hóa học.
   - `vietnam`: Hiển thị tiếng Việt có dấu chuẩn đẹp ngay bên trong hình vẽ (nhãn trục, chú thích).

4. **Cách Sử Dụng Linh Hoạt**:
   - **Cách 1: Giao tiếp tự nhiên trong chat**:
     > *"Render cho tôi đoạn mã TikZ này thành ảnh: `\\begin{tikzpicture}...\\end{tikzpicture}`"*
     > *"Câu này hãy vẽ hình bằng TikZ rồi chèn vào file Word nhé!"*
   - **Cách 2: Gọi trong code Python biên soạn đề**:
     ```python
     from scripts.tikz_renderer import render_tikz
     
     tikz_code = r'''
     \begin{tikzpicture}
       \tkzTabInit{$x$ / 1 , $f'(x)$ / 1 , $f(x)$ / 2}{$-\infty$, $-1$, $1$, $+\infty$}
       \tkzTabLine{,+,0,-,0,+,}
       \tkzTabVar{-/ $-\infty$, +/ $4$, -/ $0$, +/ $+\infty$}
     \end{tikzpicture}
     '''
     render_tikz(tikz_code, 'hinh_ve_de/cau_1_bbt.png', dpi=300)
     ```
   - **Cách 3: Chạy dòng lệnh CLI độc lập**:
     ```bash
     # Xuất ảnh PNG 300 DPI
     python scripts/tikz_renderer.py -i hinh_goc.tex -o hinh_xuat.png --dpi 300

     # Xuất file PDF vector khít viền (standalone)
     python scripts/tikz_renderer.py -i hinh_goc.tex -o hinh_xuat.pdf

     # Xuất file PDF căn giữa trang A4
     python scripts/tikz_renderer.py -i hinh_goc.tex -o hinh_xuat.pdf --mode a4
     ```

5. **Biên Dịch Trọn Vẹn Cả Đề Thi & Tài Liệu Nhiều Trang Sang PDF Chuẩn TeX**:
   - Tự động nhận diện cấu trúc tài liệu hoàn chỉnh (`\documentclass[...]{article/exam}`).
   - Cơ chế **Biên dịch 2 lượt (Two-Pass Compilation)**: Tự động chạy lần 2 nếu tài liệu có mục lục (`\tableofcontents`), tham chiếu chéo (`\ref`, `\label`) hoặc số trang tổng thể (`Trang \thepage / \pageref{LastPage}`).
   - Cho phép Thầy/Cô xuất đồng thời 2 bản ấn phẩm:
     * **Bản Word (.docx)**: Chứa MathType OLE nguyên bản để dễ chỉnh sửa, thêm bớt nội dung.
     * **Bản PDF TeX (.pdf)**: Đẹp tuyệt mỹ, chuẩn vector in ấn nhà xuất bản, không bao giờ bị nhảy trang, lệch dòng trên mọi máy in và thiết bị di động.

---
