# Quy Chuẩn Soạn Đề Thi Môn Toán Chuẩn Bộ GD&ĐT (Chương Trình GDPT 2018)

## 1. Cấu Trúc Đề Thi Chuẩn Định Dạng 2025
* **Phần I: Câu hỏi trắc nghiệm nhiều phương án lựa chọn**
  - Gồm 12 câu hỏi (từ Câu 1 đến Câu 12).
  - Mỗi câu có 4 phương án $A, B, C, D$, chỉ có duy nhất 1 phương án đúng.
  - Điểm: 0,25 điểm / câu (Tổng: 3,0 điểm).
* **Phần II: Câu hỏi trắc nghiệm Đúng / Sai**
  - Gồm 2 đến 4 câu hỏi. Mỗi câu có 4 lệnh hỏi $a), b), c), d)$.
  - Thí sinh phải chọn ĐÚNG hoặc SAI cho từng ý.
* **Phần III: Câu hỏi trắc nghiệm trả lời ngắn**
  - Gồm 4 đến 6 câu hỏi. Thí sinh chỉ điền kết quả số (số nguyên, phân số hoặc số thập phân làm tròn).
* **Phần Tự luận (đối với đề kiểm tra định kỳ)**
  - Thường gồm 2 đến 3 câu bài tập vận dụng, khảo sát hàm số, bài toán tối ưu hóa kinh tế / vật lý thực tế.

## 2. Quy Chuẩn Công Thức Toán Học
1. **Tuyệt đối không dùng văn bản thô Unicode**: Không viết `y = (2x+1)/(x-2)` hay `x³ - 3x² + 2`.
2. **Xuất 2 định dạng Word**:
   - `_WORD_EQUATION.docx`: Dùng chuẩn OMML (nhúng qua thẻ `<m:oMath>`). Mở file là hiển thị công thức phân số thẳng đứng, căn thức chuẩn Cambria Math / Times New Roman.
   - `_MATHTYPE_TEX.docx`: Toàn bộ công thức nằm trong cặp dấu `$ ... $`. Người dùng chỉ cần nhấn `Ctrl + A` rồi bấm **Toggle TeX** (`Alt + \`) trên thanh công cụ MathType là chuyển sang MathType OLE 100%.

## 3. Quy Chuẩn Hình Vẽ Đồ Thị & Kỹ Thuật
1. **Độ phân giải**: Tối thiểu 300 DPI, hình nền trắng (`bbox_inches='tight'`).
2. **Hệ trục tọa độ $Oxy$**:
   - Trục hoành có mũi tên sang phải, nhãn $x$ in nghiêng.
   - Trục tung có mũi tên hướng lên, nhãn $y$ in nghiêng.
   - Gốc tọa độ $O$ in nghiêng.
3. **Đường gióng**: Nét đứt màu đen hoặc xám (`linestyle='--'`, `lw=0.8`) vuông góc từ điểm cực trị, điểm uốn tới trục tọa độ.
4. **Đồ thị trên đoạn $[a; b]$**: Phải dùng nội suy Hermite Spline để đảm bảo cực trị trên đoạn đúng tuyệt đối với số liệu câu hỏi, không bị lẹm võng ngoài ý muốn.
5. **Hình học không gian**: Các cạnh nhìn thấy vẽ nét liền (`k-`), các cạnh khuất vẽ nét đứt (`k--`).
