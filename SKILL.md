---
name: tao-de-toan-tuong-tu
description: >-
  Tạo đề thi/kiểm tra Toán, Vật lý, Hóa học, KHTN, Sinh học, Tiếng Anh, Địa lý, KTPL, Công nghệ... lớp 6-12 chuẩn GDPT 2018 và xuất Word MathType OLE (Equation.DSMT4) + Word Equation OMML + File nghe MP3 Tiếng Anh chuẩn khảo thí:
  tạo đề tương tự (song song) từ đề gốc PDF/Word/ảnh; lập Ma trận & Bản đặc tả; ra đề theo ma trận có sẵn; tạo đề Tiếng Anh & xuất file nghe MP3 (Edge Neural TTS đa giọng đọc bản xứ, nhạc hiệu phòng thi, phát 2 lần, đồng bộ 100% câu hỏi); vẽ hình kỹ thuật 300-450 DPI (Matplotlib/TikZ: đồ thị, hình không gian, mạch điện, thí nghiệm hóa, bảng biến thiên);
  chuyển PDF sang Word không lỗi công thức; chuẩn hóa công thức file Word; trộn bộ 4 mã đề + phiếu tô trắc nghiệm + Excel đáp án; dịch đề sang tiếng Anh/song ngữ; xuất PDF in ấn; chấm bài tự luận bằng AI; OCR ảnh đề thi; đọc file MathType OLE cũ; thẩm định & rà soát đề thi theo 44 tiêu chí chuẩn GDPT 2018 (xuất biên bản Word & Dashboard Excel + Auto-fix lỗi tự động); cài đặt môi trường 1-click; soạn Kế hoạch bài dạy / giáo án chuẩn Công văn 5512 (THCS, THPT) và Công văn 2345 (Tiểu học) tích hợp Năng lực số (Thông tư 02/2025/TT-BGDĐT), Năng lực AI (Quyết định 3439/QĐ-BGDĐT & QĐ 2422), HSKT, Tiếng Anh chuyên ngành bảo toàn 100% MathType OLE; soạn slide PowerPoint (PPTX 16:9) bài giảng dạy học chuẩn mực sư phạm từ Giáo án/SGK Native DrawingML không đè chữ; tạo kịch bản & prompt Veo 3 video khởi động bài học 60-80s đồng nhất nhân vật; 
  Kích hoạt khi người dùng nói: "tôi muốn làm pptx", "tôi muốn tạo pptx", "tôi muốn làm slide", "tôi muốn tạo slide", "làm pptx", "tạo pptx", "làm slide", "tạo slide", "soạn slide", "tạo slide bài giảng", "làm pptx từ giáo án", "soạn bài giảng powerpoint", "slide toán omml", "thêm lời bình cho slide", "viết lời bình pptx", "tôi muốn làm video", "tạo video bài học", "làm video khởi động", "viết prompt veo 3", "tạo kịch bản video", "tạo file nghe mp3", "làm file nghe tiếng anh", "tạo audio listening", "tạo đề tiếng anh", "cập nhật tính năng mới", "cập nhật tiện ích", "cập nhật skill", "update skill", "soạn giáo án", "soạn giáo án tích hợp năng lực số", "soạn giáo án tích hợp ai", "soạn giáo án 5512", "soạn giáo án 2345", "chèn năng lực số", "chèn nls", "chèn ai vào giáo án", "tích hợp năng lực số", "kế hoạch bài dạy nls", "chèn nls vào word", "tạo đề tương tự", "nhân bản đề thi", "tạo đề toán/lý/hóa/KHTN", "tạo ma trận đặc tả", "tạo đề từ ma trận", "chưa có ma trận đặc tả", "trích xuất ma trận", "chuyển pdf sang word", "chuẩn hóa công thức word", "xuất word mathtype", "tạo bộ 4 mã đề", "trộn đề", "tạo phiếu trả lời", "dịch đề sang tiếng anh", "đề song ngữ", "xuất pdf đẹp", "chấm bài tự luận", "vẽ hình", "vẽ đồ thị", "render tikz", "ocr ảnh đề thi", "đọc file docx mathtype", "thẩm định đề thi", "rà soát đề thi", "kiểm tra đề thi", "thẩm định ma trận", "rà soát lời giải", "biên bản thẩm định", "đánh giá chất lượng đề", "thí nghiệm ảo", "mô phỏng 3d", "cài đặt môi trường", "hướng dẫn tạo đề".
  (Video khởi động bài học / prompt Veo 3 → dùng skill riêng `tao-video-khoi-dong-bai-hoc`.)
---


# Quy Trình Tạo Đề Toán, Vật Lý & Hóa Học Tương Tự Chuẩn Bộ GD&ĐT (Tích Hợp Backend MathType OLE & Cài Đặt 1-Click)

Skill này tự động hóa toàn bộ quy trình biên soạn đề kiểm tra / đề thi môn **TOÁN**, **VẬT LÝ** và **HÓA HỌC** (cấp THCS lớp 6, 7, 8, 9 và THPT lớp 10, 11, 12 theo định dạng mới GDPT 2018), bảo đảm **4 tiêu chuẩn vàng**:
1. **Khoa học chuẩn xác 100%**: Nghiệm đẹp, tham số logic, tuân thủ đúng định luật vật lý, hóa học (bảo toàn khối lượng, nguyên tố, điện tích, electron) và toán học (không bị hiện tượng vô lý), 4 phương án trắc nghiệm chỉ có duy nhất 1 phương án đúng, lời giải chi tiết từng bước.
2. **Hình vẽ kỹ thuật & Thí nghiệm 300 DPI chuẩn mực**: Vẽ bằng code Python Matplotlib:
   - **Môn Toán**: Đồ thị hàm số (bậc 3, bậc 4, phân thức bậc 1/1 và bậc 2/1 tiệm cận xiên), miền nghiệm hệ bất phương trình bậc nhất 2 ẩn (quy hoạch tuyến tính), sơ đồ cây xác suất (Bayes), bảng biến thiên full khung viền, phác họa đồ thị từ BBT, hình học không gian 3D ($S.ABCD$, lăng trụ, nón, trụ, cầu), hệ trục giải tích $Oxyz$.
   - **Môn Vật lý**: Đường truyền tia sáng & thấu kính, đồ thị dao động điều hòa/sóng cơ ($x-t, v-t, u-t$), sơ đồ mạch điện ($R, L, C$), giản đồ vectơ Fresnel, phân tích vectơ lực trên mặt phẳng nghiêng, đồ thị biến thiên nhiệt/khí lý tưởng $(p-V, p-T)$.
   - **Môn Hóa học**: Sơ đồ dụng cụ thí nghiệm điều chế và thu khí (dời chỗ nước/không khí), sơ đồ bình điện phân, giản đồ năng lượng phản ứng ($\Delta_r H, E_a$), đường cong chuẩn độ pH axit - bazơ.
3. **Công thức chuẩn MathType OLE (14pt) & Word Equation**:
   - Sử dụng **Backend Converter API** (`https://latex2mathtypeweb.onrender.com/api/convert-docx`) để biên dịch 100% công thức Toán, Lý (vectơ, chỉ số, đơn vị, hạt nhân), Hóa (công thức phân tử, ion, phức chất, mũi tên điều kiện $\xrightarrow{t^\circ, \text{xt}}$, mũi tên thuận nghịch $\rightleftharpoons$, kết tủa $\downarrow$, bay hơi $\uparrow$, font IUPAC thẳng chuẩn $\mathrm{Fe, Al, Cu}$) thành **MathType OLE (`Equation.DSMT4`)** nhúng nhị phân MTEF `.bin` + vector `.wmf` trực tiếp vào file Word. Giáo viên click đúp vào bất kỳ công thức nào là mở cửa sổ MathType truyền thống ngay lập tức!
   - Kèm cơ chế **Smart Fallback**: Luôn sinh thêm bản **Word Equation (OMML)** để mở được mượt mà trên mọi máy tính kể cả khi không cài MathType.
4. **Bảng Biểu Nguyên Bản (Table Grid 100%)**:
   - Tự động dựng thành bảng Word thật (`Table Grid`) có viền đầy đủ, căn lề giữa cả ngang và dọc cho các bảng thống kê Toán, bảng số liệu thực nghiệm đo đạc Vật lý, và bảng nhận biết thuốc thử Hóa học. Tuyệt đối không dùng ảnh chụp bảng, giáo viên chỉnh sửa số liệu tùy ý.

## ⭐ 6 CHÚ Ý BẮT BUỘC KHI LẬP MA TRẬN, BẢN ĐẶC TẢ & RA ĐỀ THEO MA TRẬN (TOÁN, LÝ, HÓA, KHTN, CÔNG NGHỆ...)

- **Chú ý 1 — Bản đặc tả tách mỗi mức độ nhận thức thành 1 dòng riêng & gióng thẳng hàng câu hỏi**: Bắt buộc tách riêng cột **`Mức độ đánh giá`** và cột **`Yêu cầu cần đạt`**. Mỗi mức độ nhận thức (`Nhận biết`, `Thông hiểu`, `Vận dụng`, `Vận dụng cao`) của từng bài học phải nằm trên **1 dòng (row) riêng biệt**; số lượng câu/ý và mã câu hỏi (`C1, C2, C17a...`) tương ứng với mức độ nhận thức nào **bắt buộc phải đặt nằm trên cùng dòng đó** (các cột `TT`, `Chủ đề`, `Nội dung/Đơn vị kiến thức` gộp dọc `vMerge` theo các dòng của bài học).
- **Chú ý 2 — Tuyệt đối không được thiếu các dòng Tổng kết cuối bảng**: Cả **Bảng 1 (Khung Ma trận)** và **Bảng 2 (Bản đặc tả)** bắt buộc phải có đầy đủ bộ dòng tổng kết ở cuối bảng: **`TỔNG (Ý)`**, **`TỔNG SỐ CÂU / LỆNH HỎI`**, **`TỔNG ĐIỂM (10,0 ĐIỂM)`**, và **`TỈ LỆ % (100%)`**.
- **Chú ý 3 — Vẽ bảng Word liền nét 100%, không bao giờ mất nét ở ô gộp**: Mọi bảng Ma trận và Bản đặc tả khi xuất ra `.docx` bắt buộc phải gọi hàm `enforce_perfect_table_borders(table, header_rows=3)` (trong `scripts/matrix_to_docx.py`) để gắn `<w:tblBorders>` cấp toàn bảng + quét trực tiếp toàn bộ thẻ XML `<w:tc>` (kể cả các ô ẩn `<w:vMerge/>` ở dòng 2, dòng 3 của tiêu đề hoặc cột gộp dọc) nhằm đóng khung đủ 4 cạnh, kế thừa màu nền `<w:shd>` và chống đứt dòng ngang trang (`<w:cantSplit/>`).
- **Chú ý 4 — Kiểm tra sát phạm vi bài học thực tế đã dạy (Lý thuyết vs. Thực hành)**: Nếu bài học cuối kỳ/giữa kỳ mới học 1 phần (ví dụ mới học phần lý thuyết cơ bản, chưa học phần thực hành), khi ra câu hỏi tự luận hoặc vận dụng/vận dụng cao ở bài đó **bắt buộc chỉ hỏi xoay quanh kiến thức lý thuyết đã học** (khái niệm, ưu điểm, phân loại, liên hệ thực tế đơn giản), tuyệt đối không hỏi quy trình thao tác thực hành chưa học.
- **Chú ý 5 — Khi tạo thêm Đề số 2, Đề số 3... từ cùng Ma trận & Bản đặc tả**: Phải giữ nguyên 100% ma trận phân bổ từng câu (`C1` đến câu cuối), đúng bài học, đúng mức độ nhận thức (`Nhận biết`, `Thông hiểu`, `Vận dụng`, `Vận dụng cao`) và đúng thang điểm như Đề số 1, nhưng đổi ngữ cảnh và câu hỏi mới hoàn toàn không trùng lặp.
- **Chú ý 6 — Cung cấp Câu lệnh gợi ý (Prompt mẫu) chặt chẽ cho giáo viên**: Luôn kèm theo mẫu câu lệnh tường minh (nêu rõ yêu cầu tách dòng mức độ nhận thức, đặt câu hỏi cùng dòng, đủ dòng tổng kết cuối bảng, kẻ bảng không mất nét) để giáo viên tái sử dụng dễ dàng.

---

## 🗺️ BẢN ĐỒ TÀI LIỆU — ĐỌC FILE NÀO KHI LÀM VIỆC GÌ

> [!IMPORTANT]
> `SKILL.md` chỉ giữ **quy tắc cốt lõi bắt buộc**. Khi bắt đầu một nhóm việc dưới đây, Agent **PHẢI mở và đọc file tham chiếu tương ứng trong `references/` TRƯỚC KHI làm** (đường dẫn tính từ thư mục skill).

| Việc đang làm | Đọc trước (bắt buộc) |
|:--|:--|
| Lập Ma trận / Bản đặc tả / ra đề theo ma trận | [`references/ma_tran_dac_ta.md`](./references/ma_tran_dac_ta.md) |
| Giáo viên nói câu ngắn, chưa có file; cần kịch bản phản hồi / hướng dẫn lấy đường dẫn | [`references/onboarding_prompts.md`](./references/onboarding_prompts.md) |
| Đọc đề gốc (PDF/DOCX/ảnh), chuyển PDF→Word, chuẩn hóa công thức Word | [`references/doc_de_goc_chuyen_pdf_chuan_hoa.md`](./references/doc_de_goc_chuyen_pdf_chuan_hoa.md) |
| Tạo đề tương tự: chỉnh độ khó, kiểm định GDPT 2018 (Bước 2/2bis) | [`references/thiet_ke_va_kiem_dinh.md`](./references/thiet_ke_va_kiem_dinh.md) |
| Vẽ hình / đồ thị / mạch điện / thí nghiệm | [`references/ve_hinh_ky_thuat.md`](./references/ve_hinh_ky_thuat.md), [`references/tikz_engine.md`](./references/tikz_engine.md), mẫu: [`references/tikz_templates.md`](./references/tikz_templates.md) |
| Môn Hóa học (ký hiệu, phương trình, IUPAC) | [`references/quy_chuan_hoa_hoc.md`](./references/quy_chuan_hoa_hoc.md) |
| Xuất PDF in ấn | [`references/xuat_pdf_latex.md`](./references/xuat_pdf_latex.md) |
| Dịch đề tiếng Anh / song ngữ | [`references/dich_tieng_anh.md`](./references/dich_tieng_anh.md) |
| Tạo đề Tiếng Anh & Xuất file nghe MP3 chuẩn phòng thi (khớp 100% câu hỏi) | [`references/tao_file_nghe_mp3_tieng_anh.md`](./references/tao_file_nghe_mp3_tieng_anh.md) |
| Chấm bài tự luận bằng AI | [`references/cham_bai_tu_luan.md`](./references/cham_bai_tu_luan.md) |
| "Trợ giúp", lần đầu dùng, menu sau khi tạo đề | [`references/ux_chu_dong.md`](./references/ux_chu_dong.md) |
| Chuẩn GDPT 2018, quy chuẩn đề 2025 | [`references/gdpt2018_methods.md`](./references/gdpt2018_methods.md), [`references/quy_chuan_de_thi_2025.md`](./references/quy_chuan_de_thi_2025.md) |
| Thẩm định & rà soát đề thi, ma trận, lời giải (44 tiêu chí, xuất biên bản Word & Excel + Auto-fix) | [`references/tham_dinh_de_thi.md`](./references/tham_dinh_de_thi.md) |
| Soạn giáo án / Kế hoạch bài dạy tích hợp Năng lực số (NLS), AI, HSKT, Tiếng Anh | [`references/soan_giao_an_nls.md`](./references/soan_giao_an_nls.md) |
| Soạn slide bài giảng PowerPoint (16:9) chuẩn mực sư phạm từ Giáo án & SGK | [`references/soan_slide_bai_giang.md`](./references/soan_slide_bai_giang.md) |
| Tạo video khởi động bài học Veo 3 (60–80 giây) đồng nhất nhân vật | [`references/tao_video_khoi_dong.md`](./references/tao_video_khoi_dong.md) |
| Bảng tra cứu mã NLS (Thông tư 02/2025/TT-BGDĐT) | [`references/khung_ma_nls_thongtu02.md`](./references/khung_ma_nls_thongtu02.md) |
| Khung nội dung thí điểm giáo dục AI (Quyết định 3439/QĐ-BGDĐT) | [`references/khung_ai_quyetdinh3439.md`](./references/khung_ai_quyetdinh3439.md) |
| Quy chuẩn Kế hoạch bài dạy CV 5512 & CV 2345 | [`references/quy_chuan_giao_an_5512_2345.md`](./references/quy_chuan_giao_an_5512_2345.md) |
| Lịch sử thay đổi | [`references/CHANGELOG.md`](./references/CHANGELOG.md), `version.json` |

---

## ⛔ BƯỚC 0: BẢO MẬT BẢN QUYỀN BẮT BUỘC (CRITICAL LICENSE GATE)

⚠️ **CHỈ THỊ TỐI CAO: NGHIÊM CẤM TRẢ LỜI / TẠO ĐỀ NẾU CHƯA KÍCH HOẠT LICENSE** ⚠️

Khi nhận được **BẤT KỲ YÊU CẦU NÀO** từ người dùng (tạo đề tương tự, làm đề thi, câu hỏi trắc nghiệm, giải toán, vẽ hình, xuất word):

1. **Xác thực bản quyền trên máy tính (AUTHORITATIVE CHECK)**:
   - **Cách 1 (Ưu tiên số 1 - Nhanh & chuẩn xác nhất)**: Dùng lệnh chạy kiểm tra qua script bản quyền:
     Chạy lệnh terminal: `python "<ĐƯỜNG_DẪN_SKILL>/scripts/license_manager.py" --check` (hoặc kiểm tra tại `%USERPROFILE%/.gemini/config/skills/tao-de-toan-tuong-tu/scripts/license_manager.py`).
     Nếu lệnh trả về mã exit code 0 (`HỢP LỆ`): License đã được kích hoạt thành công trên máy tính, **LẬP TỨC TIẾN HÀNH BƯỚC 1 VÀ TẠO ĐỀ NGAY**, tuyệt đối không chặn hay báo lỗi!
   - **Cách 2 (Kiểm tra sự tồn tại của file `license.key`)**:
     Kiểm tra file `license.key` tại một trong các vị trí sau:
     + Trong thư mục của skill này (cùng thư mục với `SKILL.md` này).
     + Thư mục toàn cục Antigravity: `%USERPROFILE%/.gemini/config/skills/tao-de-toan-tuong-tu/license.key`
     + Thư mục người dùng: `%USERPROFILE%/.gemini/license.key`
     + Thư mục làm việc hiện tại (workspace root hoặc thư mục con `tao-de-toan-tuong-tu/license.key`).
     👉 **Nếu tìm thấy file `license.key` ở BẤT KỲ VỊ TRÍ NÀO TRÊN**, coi như đã kích hoạt thành công và tiến hành tạo đề ngay!
   - **Cách 3 (Nếu người dùng dán trực tiếp mã License Key vào khung chat)**:
     + Kích hoạt ngay bằng lệnh: `python "<ĐƯỜNG_DẪN_SKILL>/scripts/license_manager.py" --activate "<MÃ_KEY>"`
     + Hoặc tạo file `license.key` với nội dung chuỗi key đó tại cả thư mục skill và thư mục `%USERPROFILE%/.gemini/config/skills/tao-de-toan-tuong-tu/license.key`.
     + Sau đó tiến hành tạo đề ngay cho người dùng!

2. **Nếu và chỉ nếu TẤT CẢ các bước kiểm tra trên đều thất bại (hoàn toàn không có file `license.key` và lệnh --check báo lỗi):**
   - **TUYỆT ĐỐI NGHIÊM CẤM:** Không được sinh bất kỳ câu hỏi nào ra khung chat, không được soạn đề thi, không được giải toán, không được viết code, không được xuất file Word hay vẽ hình.
   - **CHỈ ĐƯỢC PHÉP TRẢ LỜI DUY NHẤT thông báo sau:**
     > "⛔ **SKILL CHƯA ĐƯỢC KÍCH HOẠT BẢN QUYỀN TRÊN MÁY TÍNH NÀY!**  
     >   
     > Để sử dụng phần mềm tạo đề thi, thầy/cô vui lòng:  
     > 1. Nhấp đúp vào file **`LAY_MA_MAY.bat`** trong thư mục phần mềm để lấy Mã máy (Machine ID).  
     > 2. Gửi Mã máy cho tác giả để nhận License Key bản quyền.  
     > 3. Nhấp đúp vào file **`KICH_HOAT_BAN_QUYEN.bat`** để dán Key kích hoạt và sử dụng vĩnh viễn (hoặc gửi trực tiếp mã License Key vào khung chat này để em kích hoạt giúp thầy/cô)."
   - **DỪNG TIẾN TRÌNH NGAY LẬP TỨC!** Không trả lời thêm bất kỳ nội dung đề thi nào.

3. **Kiểm tra Phân Quyền Theo Từng Tiện Ích Mua Lẻ (`MODULAR FEATURE GATE` - Bắt buộc kiểm tra khi `--check` hợp lệ):**
   - Khi chạy `python "<ĐƯỜNG_DẪN_SKILL>/scripts/license_manager.py" --check`, đọc dòng `UNLOCKED_FEATURES : ...` trong kết quả:
     + Nếu `UNLOCKED_FEATURES : ALL` $\rightarrow$ Giáo viên sở hữu gói **FULL VIP (Trọn bộ 8 tiện ích)**, được phép thực hiện mọi yêu cầu.
     + Nếu `UNLOCKED_FEATURES` chỉ liệt kê một số mã tiện ích cụ thể (mua lẻ từng tiện ích), đối chiếu yêu cầu hiện tại của giáo viên với bảng 8 mã tiện ích sau:
       * `pdf_to_word`: Chuyển đổi đề thi PDF sang Word MathType OLE
       * `clone_exam`: Tạo đề thi tương tự (song song) & Vẽ hình tự động
       * `standardize_mathtype`: Chuẩn hóa công thức file Word sang MathType OLE 14pt
       * `shuffle_exam`: Trộn bộ 4 mã đề hoán vị & Tạo phiếu tô trắc nghiệm A4
       * `translate_exam`: Dịch đề thi sang Tiếng Anh học thuật & Song ngữ Anh - Việt
       * `matrix_exam`: Thiết lập Ma trận đặc tả, Trích xuất ma trận & Tạo đề từ ma trận
       * `grade_essay`: Chấm bài tự luận học sinh bằng AI Vision & Xuất báo cáo điểm
       * `ocr_exam`: Nhận diện ảnh chụp đề thi (OCR) & Đọc công thức MathType cũ
     + **Nếu tiện ích giáo viên yêu cầu KHÔNG nằm trong `UNLOCKED_FEATURES`**:
       * **TUYỆT ĐỐI NGHIÊM CẤM** thực thi tiện ích chưa mua đó (kể cả khi giáo viên yêu cầu qua hướng dẫn câu lệnh).
       * **DỪNG NGAY LẬP TỨC** và chỉ trả lời thông báo lịch sự sau:
         > "🔒 **TIỆN ÍCH NÀY CHƯA NẰM TRONG GÓI BẢN QUYỀN HIỆN TẠI CỦA THẦY/CÔ!**  
         >   
         > • **Tiện ích Thầy/Cô đang yêu cầu:** `<Tên tiện ích đang gọi>`  
         > • **Gói bản quyền hiện tại trên máy đang mở khóa:** `<Tên các tiện ích trong Gói mở khóa>`  
         >   
         > 💡 **Cách mở khóa thêm tiện ích (không cần cài đặt lại phần mềm):**  
         > 1. Thầy/Cô vui lòng liên hệ Tác giả để đăng ký mở khóa thêm tiện ích này (hoặc nâng cấp lên gói **FULL VIP Trọn bộ 8 tiện ích**).  
         > 2. Sau khi nhận Mã License Key mới từ Tác giả, Thầy/Cô chỉ cần dán trực tiếp mã đó vào khung chat này (hoặc chạy `KICH_HOAT_BAN_QUYEN.bat`) là mở khóa sử dụng được ngay!"

> Chỉ khi nào license hợp lệ VÀ tiện ích nằm trong gói được phép sử dụng thì mới được tiếp tục thực hiện các bước bên dưới!

---

## 🧭 BƯỚC 0.1: ĐIỀU HƯỚNG THÔNG MINH CHO GIÁO VIÊN (RÚT GỌN)

### ⚠️ QUY TẮC BẮT BUỘC KHI NHẬN CÂU LỆNH ĐƠN GIẢN HOẶC CHƯA CÓ FILE ĐẦU VÀO:

Khi giáo viên đưa ra các câu lệnh ngắn, đơn giản hoặc mới chỉ nêu ý định tổng quát:
- *"tôi muốn chuyển pdf sang word"*, *"chuyển đề pdf sang word"*, *"convert pdf to word"*, *"chuyển file pdf này sang docx"*
- *"tôi muốn tạo đề tương tự"*, *"tạo đề tương tự"*, *"tạo đề song song"*, *"nhân bản đề thi"*
- *"chuẩn hóa công thức word"*, *"sửa lỗi công thức file word"*, *"chuyển equation sang mathtype"*, *"chuẩn hóa mathtype"*
- *"trộn đề thi"*, *"tạo 4 mã đề"*, *"tạo phiếu tô trắc nghiệm"*, *"đảo đề thi"*
- *"dịch đề sang tiếng anh"*, *"tạo đề song ngữ"*, *"chuyển đề sang tiếng anh"*, *"đề tiếng anh"*
- *"tạo ma trận đặc tả"*, *"tạo ma trận đề kiểm tra"*, *"tôi muốn tạo đề từ ma trận có sẵn"*, *"tạo đề khi chưa có ma trận"*, *"chưa có ma trận đặc tả"*, *"chuẩn bị gì để tạo ma trận"*, *"làm ma trận"*, *"cấu trúc ma trận"*, *"tạo đề từ ma trận"*
- *"trích xuất ma trận"*, *"phân tích ma trận đề thi"*, *"lập ma trận từ đề này"*
- *"nhận diện ảnh đề thi"*, *"chụp ảnh đề thi tạo đề mới"*, *"ocr ảnh đề"*
- *"thẩm định đề thi"*, *"rà soát đề thi"*, *"kiểm tra đề thi và lời giải"*, *"đánh giá đề thi"*, *"thẩm định ma trận đặc tả"*
**MÀ TRONG NGỮ CẢNH CHƯA CÓ FILE ĐÍNH KÈM HOẶC CHƯA CÓ ĐƯỜNG DẪN TỆP CỤ THỂ**:

1. **TUYỆT ĐỐI NGHIÊM CẤM:**
   - ❌ Không được trả lời cộc lốc hoặc máy móc: *"Bạn hãy gửi file đi"*, *"Tôi cần file để xử lý"*.
   - ❌ Không được tự ý bịa đặt nội dung đề thi, không tự bịa tên file ngẫu nhiên để làm bừa khi chưa có file nguồn.
   - ❌ Không được dừng phản hồi lửng lơ khiến giáo viên bối rối không biết thao tác tiếp theo.

2. **CHỈ THỊ TỐI CAO DÀNH CHO AGENT:**
   - **Thao tác 1 (Nhận diện thư mục làm việc thực tế)**: Agent phải xác định chính xác đường dẫn thư mục làm việc hiện tại (`Current Working Directory` / Workspace Path — ví dụ: `d:\skill-quan-trong` hoặc thư mục workspace đang mở) và **điền trực tiếp đường dẫn này** vào câu trả lời gửi giáo viên, tuyệt đối không viết chung chung là "thư mục làm việc".
   - **Thao tác 2 (Xuất bản hướng dẫn tận tâm & chuyên nghiệp)**: Trả lời giáo viên bằng văn phong sư phạm ân cần, lịch sự, cung cấp chi tiết **2 CÁCH ĐƯA FILE VÀO** kèm theo **MẪU CÂU LỆNH (PROMPT) CHUẨN VÀNG** đã soạn sẵn đầy đủ bộ tiêu chí "3 KHÔNG LỖI" để giáo viên chỉ việc Copy - Paste.

---

> 👉 Hướng dẫn lấy đường dẫn file trên Windows (3 cách) và kịch bản phản hồi mẫu theo từng chức năng: xem [`references/onboarding_prompts.md`](./references/onboarding_prompts.md).

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
[Đề gốc PDF / DOCX / Ảnh chụp]
        │
        ▼ (Phân tích ma trận dạng toán & OCR trích xuất)
[Thiết kế số liệu đề mới nghiệm đẹp & Lập trình vẽ hình 450 DPI]
        │
        ▼ (Đóng gói DOCX nền chứa tag $LaTeX$ + Hình ảnh sắc nét)
[_temp_raw_latex.docx]
        │
        ├─────────────────────────────────┬──────────────────────────────┐
        ▼ (POST qua Backend API)          ▼ (Chuyển đổi Client-side)    ▼ (Sinh LaTeX)
[latex2mathtypeweb.onrender.com]   [MML2OMML.XSL Word Engine]   [pdf_exam_exporter.py]
        │                                 │                              │
        ▼                                 ▼                              ▼ (xelatex/pdflatex ×2)
[MA_DE_MATHTYPE_OLE.docx]      [MA_DE_WORD_EQUATION.docx]    [MA_DE_DE_HOC_SINH.pdf]
(Công thức MathType OLE xịn,   (Mở trên mọi máy, không        [MA_DE_LOI_GIAI_GV.pdf]
 click đúp mở MathType 6/7)     cần cài MathType)             (Đẹp như sách, chuẩn in ấn,
                                                                6 theme màu, tùy chỉnh)
```

---

---

## Các Bước Thực Hiện Chi Tiết

### 🆕 Bước 0.5: Ma Trận & Bản Đặc Tả — Lập mới / Ra đề từ Ma trận / Dùng kho chuẩn

**3 nhánh:** (1) *Chưa có ma trận* → lập từ 5 tư liệu gốc (SGK, PPCT, cấu trúc ra đề, GDPT 2018, đề mẫu); (2) *Đã có ma trận* → ra đề bám sát 100% từng dòng; (3) *Chỉ nói tên môn* → dùng kho 8 ma trận chuẩn `references/default_matrices.json`.

**Quy tắc cốt lõi (chi tiết + ví dụ bảng + hàm viền: [`references/ma_tran_dac_ta.md`](./references/ma_tran_dac_ta.md) — BẮT BUỘC đọc):**
- Bản đặc tả: cột `Mức độ đánh giá` ≠ cột `Yêu cầu cần đạt`; **mỗi mức độ nhận thức 1 dòng**, số câu + mã câu (`C1, C17a…`) **cùng dòng** (xem Chú ý 1).
- Cả 2 bảng **đủ dòng tổng kết cuối** `TỔNG (Ý)` / `TỔNG SỐ CÂU` / `TỔNG ĐIỂM` / `TỈ LỆ %` (Chú ý 2).
- Xuất Word bằng `scripts/matrix_to_docx.py` → luôn qua `enforce_perfect_table_borders()` (Chú ý 3).
- Tỉ lệ nhận thức & phạm vi bài: bám cấu trúc ra đề của trường / PPCT; bài mới học một phần (chưa học thực hành) chỉ hỏi lý thuyết (Chú ý 4).
- Công cụ: `scripts/exam_from_matrix.py` (`MatrixParser`, `ExamGenerator`, `ReviewInterface`), `scripts/matrix_to_docx.py`, kiểm định `scripts/gdpt2018_validator.py`.

#### Mẫu Câu Lệnh Chuẩn Cho Giáo Viên (đưa vào onboarding)


```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📌 TỔNG HỢP CÁC CÂU LỆNH MẪU CHẶT CHẼ ĐỂ TẠO MA TRẬN, ĐẶC TẢ & RA ĐỀ THI

📁 NHÓM 1: CHƯA CÓ MA TRẬN ĐẶC TẢ SẴN (Lập từ 5 tư liệu gốc cho mọi môn):
   - Tạo thư mục "DU_LIEU_RA_DE" chứa: (1) SGK điện tử, (2) Kế hoạch dạy học/PPCT,
     (3) Cấu trúc ra đề, (4) Đề mẫu nếu có, (5) Chương trình GDPT 2018 môn học (PDF).
   - Câu lệnh chuẩn:
     "Em hãy đọc các tài liệu trong thư mục [đường dẫn DU_LIEU_RA_DE], đối chiếu PPCT, SGK và Chương trình
      GDPT 2018 để lập bảng Khung Ma trận và Bản đặc tả đề kiểm tra môn [Toán/Lý/Hóa/KHTN/Công nghệ...]
      lớp [...] học kỳ [...] ra file Word khổ ngang A4.
      Yêu cầu bắt buộc:
      1. Trong Bản đặc tả: Tách riêng cột Mức độ đánh giá và cột Yêu cầu cần đạt; mỗi mức độ nhận thức
         (Nhận biết, Thông hiểu, Vận dụng, Vận dụng cao) của từng bài học phải nằm trên 1 dòng riêng biệt;
         số lượng câu hỏi và mã câu hỏi tương ứng (C1, C2, C17a...) phải đặt ở cùng dòng với mức độ đó.
      2. Cả bảng Khung Ma trận và Bản đặc tả bắt buộc phải có đầy đủ các dòng tổng kết ở cuối bảng:
         Tổng (Ý), Tổng số câu, Tổng điểm (10,0 điểm) và Tỉ lệ % (100%), tuyệt đối không thiếu dòng cuối.
      3. Vẽ bảng Word khung viền liền nét 100% (áp dụng đầy đủ tblBorders và tcBorders cho cả các ô gộp),
         tuyệt đối không bị mất nét kẻ dọc hay ngang."

📝 NHÓM 2: ĐÃ CÓ SẴN FILE MA TRẬN ĐẶC TẢ (Ra đề hoàn chỉnh chuẩn 3 tiêu chuẩn vàng):
   - Đính kèm file Word/Excel/PDF ma trận hoặc dán bảng vào chat.
   - Câu lệnh chuẩn:
     "Dựa vào file Ma trận & Bản đặc tả tại: [đường dẫn file], em hãy tạo giúp tôi [1 đề / 2 đề song song]
      môn [...] lớp [...] bám sát 100% từng dòng mức độ nhận thức và yêu cầu cần đạt của Bản đặc tả
      (số liệu mới nghiệm đẹp, vẽ hình 300 DPI, đầy đủ bảng đáp án và hướng dẫn chấm chi tiết từng 0,25đ,
      xuất file Word chuẩn MathType OLE 13pt-14pt, bảng biểu liền nét 100% không mất nét)."

⚡ NHÓM 3: SỬ DỤNG KHO MA TRẬN CHUẨN GDPT 2018 CÓ SẴN TRONG HỆ THỐNG:
   - "Tạo đề Toán 12, 90 phút theo ma trận chuẩn GDPT 2018 có sẵn"
   - "Xuất bảng ma trận và bản đặc tả Hóa 11 ra file Word (mỗi mức độ nhận thức 1 dòng riêng kèm mã câu hỏi cùng dòng, đủ 4 dòng tổng kết cuối bảng, khung viền liền nét không mất nét)"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Bước 1: Tiếp nhận và phân tích đề gốc

**Sử dụng thư viện [docx_reader.py](./scripts/docx_reader.py) để đọc mọi định dạng đề gốc:**

| Loại file | Hàm gọi | Engine |
|-----------|---------|--------|
| PDF (text) | `read_exam_pdf(path)` | PyMuPDF (offline) |
| DOCX thường | `read_exam_docx(path)` | python-docx (offline) |
| **DOCX có MathType OLE** | `extract_latex_from_mathtype_docx(path)` | `mathtype-latex-api.onrender.com` → MTEF-py |
| **Ảnh chụp đề thi (PNG/JPG)** | `ocr_image_to_latex([path])` | `mathtype-latex-api.onrender.com` → Mistral AI Vision |
| Tự động | `read_exam_source(path)` | Tự nhận diện theo đuôi file |

> 👉 Ví dụ code đọc từng loại file, **Bước 1.2 Chuyển PDF→Word (Hybrid Render v2)** và **Bước 1.3 Chuẩn hóa công thức Word → MathType OLE**: [`references/doc_de_goc_chuyen_pdf_chuan_hoa.md`](./references/doc_de_goc_chuyen_pdf_chuan_hoa.md).

### Bước 2: Thiết kế bài toán tương đương & Kiểm định

> **QUY TẮC VÀNG**: Dạng bài / kiểu bài PHẢI GIỐNG ĐỀ GỐC 100%. Chỉ được thay đổi số liệu và độ phức tạp tính toán. KHÔNG được đổi dạng.

- Xác định `difficulty_level` (`equivalent` mặc định | `easier` | `harder`) từ lời người dùng; điều chỉnh số liệu **và** phân phối NB/TH/VD/VDC toàn đề; chọn số liệu nghiệm đẹp; lập bảng kiểm định (đạo hàm, cực trị, tiệm cận…) để đáp án không trùng/vô nghiệm.
- **Bước 2bis (BẮT BUỘC trước khi xuất đề):** chạy checklist GDPT 2018 / `scripts/gdpt2018_validator.py`; mục nào KHÔNG ĐẠT phải sửa trước khi xuất Word. Bảng điều chỉnh số liệu, tỷ lệ, checklist đầy đủ và bảng "Cũ vs Mới": [`references/thiet_ke_va_kiem_dinh.md`](./references/thiet_ke_va_kiem_dinh.md).

### Bước 3: Lập trình vẽ hình kỹ thuật chuẩn xác (300–450 DPI)

- Lưu hình vào `hinh_ve_<ma_de>/` (PNG ≥ 300 DPI, mặc định 450); dùng `scripts/render_math_figures.py` (Matplotlib) hoặc `scripts/tikz_renderer.py` (TikZ).
- Số liệu/góc màu ĐEN đậm, có khung đệm trắng; BBT dùng `draw_bbt_sgk()`; vectơ dùng `\overrightarrow{AB}` (KHÔNG `\vec{AB}`) / `draw_vector_label()`.
- Hình phải KHỚP tuyệt đối đề bài (miền xác định, giao điểm nguyên, tiệm cận). Bảng chọn công cụ theo dạng bài + 4 quy tắc khớp hình–đề: [`references/ve_hinh_ky_thuat.md`](./references/ve_hinh_ky_thuat.md).

#### Quy tắc cạnh thấy / khuất (TUYỆT ĐỐI KHÔNG vi phạm):
- **Cạnh thấy** (có thể nhìn thấy từ vị trí quan sát): `draw[thick]` hoặc `k-` nét liền, `lw=1.8`
- **Cạnh khuất** (bị che khuất): `draw[dashed, thin]` hoặc `k--` nét đứt, `lw=1.2`
- **Điểm đặc biệt** (giao điểm, đầu mút, cực trị): chấm tròn đen `\fill` hoặc `ko markersize=5`

#### Quy tắc trình bày Chữ số, Ký hiệu Toán học & Véc-tơ (CHUẨN SGK XUẤT BẢN):
1. **Tuyệt đối KHÔNG đè chữ hay số lên nét vẽ**:
   - Mọi nhãn chữ cái ($A, B, C, D, S, O$), số đo góc ($60^\circ$), số đo độ dài cạnh ($8, 12...$), và biểu thức véc-tơ ($\vec{AS}, \vec{BC}, \vec{AD}$) phải được định vị tại vùng trống (whitespace), lệch hẳn ra ngoài các cạnh và trục tọa độ.
   - Tuyệt đối không để text hoặc hộp viền trắng (`bbox`) cắt đứt các nét vẽ liền hay nét đứt của hình học.
2. **Ký hiệu véc-tơ chuẩn SGK**:
   - Mũi tên véc-tơ phải dài bao phủ trọn vẹn bề ngang các chữ cái ($\vec{AS}, \vec{BC}, \vec{AD...}$).
   - Mũi tên phải được **nâng cao khoảng cách an toàn** (`arrow_y = p1[1] + 0.18*h`) để tách biệt hoàn toàn, **không bao giờ dính sát hay tì đè vào đỉnh chữ cái**.
3. **Độ sắc nét của ký hiệu Đạo hàm & Tích phân** (BẮT BUỘC dùng hàm chuẩn):
   - **Đạo hàm** ($y'$, $f'(x)$, $y''$): Luôn dùng `fmt_derivative('y', order=1)` → `$\boldsymbol{y'}$` hoặc `fmt_derivative('f(x)', order=2)` → `$\boldsymbol{f''(x)}$`. Dấu phẩy đạo hàm to, đậm **không bao giờ** bị mảnh như sợi chỉ.
   - **Tích phân**: Luôn dùng `fmt_integral(lower, upper, integrand, differential)` → `$\displaystyle\int_a^b f(x)\,dx$`. Ký hiệu $\displaystyle$ đảm bảo tích phân luôn to, không bị thu nhỏ.
   - **Ký hiệu góc**: Luôn dùng `fmt_angle('B', 'A', 'C')` → `$\widehat{BAC}$` (KHÔNG dùng `$\hat{A}$` vì quá ngắn). Số đo góc dùng `add_degree_label(ax, x, y, 60)` → `$\mathbf{60}^{\circ}$` đen tuyền, đậm, không xám mờ.
   - **Trong TikZ**: Ký hiệu góc dùng `\widehat{BAC}` hoặc `\angle BAC`. Đạo hàm dùng `$y^{\prime}$` hoặc `$f^{\prime}(x)$`. Tích phân dùng `$\displaystyle\int_a^b$`. Véc-tơ BẮT BUỘC `\overrightarrow{AB}` (KHÔNG `\vec{AB}`).

### Bước 4: Quy Chuẩn Xuất Bản File Word MathType OLE 100% (Bắt Buộc Cho Toàn Bộ Skill)

> [!IMPORTANT]
> **CHỈ THỊ XUẤT FILE WORD BẮT BUỘC TRÊN TOÀN BỘ HỆ THỐNG:**
> Bất kỳ yêu cầu nào liên quan đến xuất file Word (tạo đề tương tự Toán/Lý/Hóa, xuất đề thi, giải bài toán, xuất lời giải chi tiết, chuyển PDF sang Word, nhân bản bộ 4 mã đề, xuất bản tiếng Anh/song ngữ) **ĐỀU BẮT BUỘC PHẢI ÁP DỤNG 100% QUY TRÌNH NÀY**.
> Tuyệt đối không bao giờ để xuất hiện chuỗi LaTeX thô (`$ ... $`) hoặc công thức gãy nát trong file Word bàn giao cho giáo viên. Mọi công thức phải là đối tượng **MathType OLE nguyên bản (`Equation.DSMT4`)** mở nhấp đúp chuột sửa được ngay, đồng thời luôn có bản **Word Equation (OMML)** dự phòng.

#### ⚡ QUY TẮC VÀNG CÚ PHÁP LATEX CHUẨN MATHTYPE (ANTI-CORRUPTION RULES):
Để công thức hiển thị hoàn mỹ 100% trong MathType OLE mà không bao giờ bị mất ký hiệu hay dính dòng:
1. ❌ **TUYỆT ĐỐI KHÔNG DÙNG `\implies`** $\rightarrow$ ✅ **BẮT BUỘC DÙNG `\Rightarrow`**: Bộ dịch TeX của MathType không nhận diện `\implies` và sẽ nuốt mất mũi tên suy ra, làm biểu thức bị dính liền (ví dụ `$A \implies B$` biến thành `$AB$`). Luôn dùng `\Rightarrow` hoặc viết chữ "Suy ra:".
2. ❌ **TUYỆT ĐỐI KHÔNG DÙNG `\iff`** $\rightarrow$ ✅ **BẮT BUỘC DÙNG `\Leftrightarrow`**: MathType không nhận diện `\iff`.
3. ❌ **TUYỆT ĐỐI KHÔNG GỘP NHIỀU DÒNG VÀO 1 PARAGRAPH BẰNG `\n`** $\rightarrow$ ✅ Mỗi bước biến đổi toán học hoặc mỗi câu phải là một đoạn văn riêng biệt (`doc.add_paragraph()`). Nhét `\n` vào một text run sẽ làm xô lệch các đối tượng OLE và đè chữ lên nhau.
4. ❌ **TUYỆT ĐỐI KHÔNG ĐỂ CÔNG THỨC Ở TIÊU ĐỀ HOẶC BẢNG BIỂU DƯỚI DẠNG TEXT THÔ** $\rightarrow$ ✅ Mọi ký hiệu toán học ở Tiêu đề câu (ví dụ `$AK = AB\sqrt{2}$`, `$\widehat{HEF} = \widehat{HCB}$`) và trong Bảng Barem điểm BẮT BUỘC PHẢI ĐƯỢC BỌC TRONG CẶP `$ ... $` để biên dịch sang MathType OLE 100%.
5. ⚠️ **KÝ HIỆU ĐỒNG DẠNG TAM GIÁC**: MathType TeX bỏ qua `\sim`. Trong lời giải hình học, viết rõ: "$\Delta ABC$ đồng dạng với $\Delta DEF$ (g - g)" kèm tỷ số đồng dạng $\Rightarrow \frac{AB}{DE} = \frac{AC}{DF}$.
6. ✅ **KÝ HIỆU SONG SONG VÀ VUÔNG GÓC CHUẨN SGK VIỆT NAM**:
   - Theo chuẩn SGK GDPT 2018 (cả cấp 2 và cấp 3), ký hiệu song song chính thức là **hai gạch xiên song song** (`//` hoặc `⫽`), còn LaTeX quốc tế thường dùng `\parallel` (hai gạch đứng $\parallel$).
   - Hệ thống tự động chuẩn hóa cả hai dạng:
     + Khi giáo viên/AI viết `$AB // CD$` hay `$(P) // (Q)$`: Tự động chuẩn hóa thành `\text{ // }` có khoảng đệm toán học đối xứng, chống dính sát chữ và chống nhận nhầm thành phép chia trong MathType OLE / Word Equation.
     + Khi viết `\parallel`: Tự động chuyển thành `\text{ // }` (chuẩn SGK Việt Nam), chống dính sát vào tên đoạn thẳng và không bị ô vuông `□` hoặc `?` trong MathType OLE.
     + Khi viết `\perp`: Tự động thêm khoảng đệm đối xứng `\ \perp \ ` (ví dụ `$AB \ \perp \ CD$`).
7. ✅ **DẤU GIÁ TRỊ TUYỆT ĐỐI CHUẨN TEMPLATE FENCE MATHTYPE**:
   - Tự động chuẩn hóa mọi cặp dấu `|...|` hoặc `\lvert ... \rvert` sang `\left| ... \right|` (chuẩn template `tmFENCE` của MathType).
   - Ngăn chặn triệt để hiện tượng giáo viên nhấp đúp chuột mở MathType bị nuốt mất 2 vạch gạch đứng giá trị tuyệt đối.
8. ❌ **TUYỆT ĐỐI KHÔNG DÙNG `\wideparen` CHO CUNG TRÒN**:
   - Bộ dịch TeX của MathType không hỗ trợ lệnh `\wideparen{AB}` và sẽ in ra nguyên bản chuỗi text thô `\wideparen{AB}`.
   - Hệ thống tự động chuyển hóa thành `\text{cung } AB` hoặc viết lời giải bằng tiếng Việt: `cung $AB$` chuẩn sư phạm SGK Việt Nam.
9. ⚠️ **CÁCH GHI HỆ SỐ TRƯỚC GÓC `\widehat`**:
   - Tránh viết dính liền `$2\widehat{ABC}$` vì bộ phân tích MathType đôi khi gom số 2 vào trong mũ góc. Tự động chuẩn hóa thành `$2 \cdot \widehat{ABC}$`.
10. ⚠️ **TÁCH BIỆT CÔNG THỨC DISPLAY MATH TRÊN DÒNG ĐỘC LẬP**:
   - Khi hiển thị công thức trọng tâm hoặc biến đổi dài, tuyệt đối không chèn `$$ ... $$` lẫn trong đoạn văn bản thông thường. Mỗi công thức display math phải được đưa vào một paragraph riêng căn giữa `doc.add_paragraph()` với định dạng `$ ... $` (`add_math_content()` gọi trên paragraph riêng).
11. 🛡️ **CƠ CHẾ TỰ ĐỘNG CHỐNG XUNG ĐỘT KHÓA FILE WORD (PERMISSIONERROR)**:
   - Khi giáo viên đang mở xem file Word trên máy tính, hệ điều hành Windows sẽ khóa quyền ghi đè (`PermissionError: [Errno 13] Permission denied`).
   - Bộ xuất file tự động bắt ngoại lệ, không bao giờ báo lỗi hay nuốt kết quả, mà sẽ tự động lưu ra file mới `<tên_file>_moi.docx` và thông báo rõ ràng cho giáo viên.

Sử dụng thư viện cốt lõi [docx_math_builder.py](./scripts/docx_math_builder.py):

#### 1. Bộ Tiêu Chuẩn Thể Thức Sư Phạm & Typography Vàng:
- **Font chữ chuẩn**: **Times New Roman 14pt** xuyên suốt toàn bộ văn bản (câu hỏi, phương án, bài giải). Tiêu đề đề thi 16pt In đậm căn giữa; bảng biểu và đầu trang 10.5–11pt.
- **Căn lề chuẩn văn bản giáo dục**: Lề trái $2.2\text{ cm}$ (để đóng gáy tập), lề phải $2.0\text{ cm}$, lề trên $2.0\text{ cm}$, lề dưới $2.0\text{ cm}$.
- **Khoảng cách đoạn & dãn dòng**: Line spacing $1.15 - 1.2$, `space_after = 3-4pt`, `space_before = 0pt` giúp trang in thoáng đãng, sang trọng, không bị dính chữ.
- **Khung tiêu đề 2 cột đối xứng**: Cột trái thông tin Sở/Trường, cột phải thông tin Kỳ thi/Thời gian, đường chỉ kẻ phân cách màu sắc thanh lịch.
- **Căn chỉnh 4 phương án A/B/C/D**: Tự động chia cột trên bảng ẩn không viền (`add_aligned_choices`):
  - Phương án ngắn ($\le 22$ ký tự): 1 hàng 4 cột.
  - Phương án vừa ($\le 52$ ký tự): 2 hàng 2 cột.
  - Phương án dài: 4 dòng riêng biệt thụt lề $0.5\text{ cm}$.
- **Bố cục 2 cột thông minh tiết kiệm giấy in (Smart Side-by-Side Layout)**:
  - Cột trái ($4.5$ inches): Dẫn đề + phương án lựa chọn.
  - Cột phải ($2.3$ inches): Hình vẽ kỹ thuật hoặc đồ thị căn giữa dọc.
  - Tiết kiệm $35\% - 45\%$ diện tích trang in A4 cho nhà trường.
- **Bảng biểu Table Grid nguyên bản**:
  - Dòng tiêu đề đổ nền màu đậm (`#1B4F72`), chữ trắng in đậm căn giữa.
  - Các dòng dữ liệu xen kẽ nền trắng và xám nhẹ (`#F4F6F7`), có padding lề ô $100-140\text{ dxa}$, viền sắc nét, hỗ trợ công thức toán MathType OLE bên trong ô bảng.

#### 2. Quy Trình Thực Thi 5 Bước Khép Kín:
```text
[Dữ liệu Đề / Bài giải]
        │
        ▼ (Bước 4.1: Tạo DOCX nền chuẩn định dạng chứa tag $LaTeX$)
[_temp_raw_exam.docx]
        │
        ├───────────────────────────────────────────────────────┐
        ▼ (Bước 4.2: POST qua Backend API kèm License)          ▼ (Bước 4.4: OMML Local Engine)
[https://latex2mathtypeweb.onrender.com/api/convert-docx]     [MML2OMML.XSL Microsoft Office]
        │                                                        │
        ▼ (Bước 4.3: Nhận DOCX & Kiểm định Integrity Audit)      ▼
[<TEN>_MATHTYPE_OLE.docx]                                    [<TEN>_WORD_EQ.docx]
(100% Equation.DSMT4, 0 residual $,                          (Word Equation chuẩn SGK,
click đúp sửa ngay bằng MathType 6/7)                         mở trên mọi máy tính)
```

1. **Bước 4.1: Xây dựng DOCX nền chứa tag `$LaTeX$`**:
   Gọi `_build_student_docx` hoặc `_build_teacher_docx` với `mode='tex'`. Toàn bộ công thức toán, lý, hóa được bao bọc trong cặp `$ ... $`.
2. **Bước 4.2: Gửi Backend API chuyển đổi MathType OLE**:
   Gọi hàm `convert_to_mathtype_ole_via_backend(raw_path, ole_path)`. Hàm tự động đóng gói License Key và Machine ID để gửi tới Backend Server.
3. **Bước 4.3: Kiểm định tính toàn vẹn bắt buộc (Integrity Audit Gate)**:
   Hàm tự động gọi `audit_word_ole_file(ole_path)` để kiểm tra cấu trúc OpenXML:
   - Đếm số lượng đối tượng OLE thực sự (`embeddings/oleObject*.bin`).
   - Quét từng đoạn văn (`paragraphs`) và từng ô bảng (`tables`) để bảo đảm số lượng ký tự `$` sót lại bằng đúng 0 (`residual_count == 0`).
   - Nếu phát hiện lỗi hoặc không có OLE, hệ thống cảnh báo và kích hoạt cơ chế khắc phục ngay lập tức.
4. **Bước 4.4: Tạo bản Word Equation (OMML) song song**:
   Đồng thời sinh tệp `<TEN>_WORD_EQ.docx` qua `MML2OMML.XSL` để giáo viên xem được ngay trên điện thoại hoặc máy tính chưa cài MathType.
5. **Bước 4.5: Tự động dọn dẹp file nháp tạm**:
   Xóa sạch các tệp trung gian `_temp_*.docx`, chỉ giữ lại các tệp ấn phẩm chính thức sạch đẹp.

#### 3. Tích Hợp Hoàn Hảo Vào Bộ 4 Mã Đề (`exam_shuffler.py`):
Khi giáo viên yêu cầu tạo bộ đề hoán vị, hàm `generate_exam_set` tự động xuất trọn gói cho mỗi mã đề:
- `<MA_DE>_DE_HOC_SINH_MATHTYPE_OLE.docx`: Bản phát cho học sinh (MathType OLE).
- `<MA_DE>_LOI_GIAI_GV_MATHTYPE_OLE.docx`: Bản lời giải chi tiết và barem chấm cho giáo viên (MathType OLE).
- `<MA_DE>_WORD_EQ.docx`: Bản dự phòng Word Equation.
- `phieu_hoc_sinh_<MA_DE>.png`: Phiếu trả lời bong bóng chuẩn A4.
- `dap_an_giao_vien_<MA_DE>.png`: Phiếu đáp án đã tô đen để chấm thi.
- `DAP_AN_TONG_HOP_4_MA_DE.xlsx`: Bảng ma trận tổng hợp đáp án toàn bộ mã đề.

### Bước 5: Bàn giao và đối chiếu
1. Cung cấp đường link trực tiếp tới cả 2 tệp `.docx` đã tạo:
   - `<MA_DE>_MATHTYPE_OLE.docx` (MathType OLE nguyên bản - khuyên dùng)
   - `<MA_DE>_WORD_EQUATION.docx` (Word Equation OMML)
2. **Hiển thị Cảnh báo & Hướng dẫn 1-Click đồng bộ cỡ công thức MathType (Format Equations)**:
   Khi bàn giao file `_MATHTYPE_OLE.docx`, luôn kèm theo thông báo hướng dẫn giáo viên cách dùng tab **MathType** $\rightarrow$ **Format Equations** với file `Times_14pt_Chuan_BGD.eqp` (được tự động sinh sẵn trên Desktop/thư mục kết quả) để phòng trường hợp giáo viên đổi cỡ chữ văn bản hoặc muốn phóng to phân số tăm tắp theo ý muốn.
3. Hiển thị đề thi trực quan trên màn hình trò chuyện kèm hình ảnh minh họa.
4. Trình bày bảng đáp án trắc nghiệm Phần I, II, III và barem chấm chi tiết phần Tự luận.
5. Lập bảng đối chiếu chứng minh tính chuẩn xác về mặt toán học giữa đề mới và hình vẽ.

---

---

### Bước 5bis: Xuất PDF đẹp chuẩn in ấn (TÙY CHỌN — KHUYÊN DÙNG)
Sau khi tạo đề, **chủ động gợi ý** PDF. Gọi `scripts/pdf_exam_exporter.py` (`export_exam_pdf(...)`, 6 theme: teal/navy/red/minimal/purple/classic). Chi tiết lệnh, theme, tùy chỉnh qua chat, yêu cầu kỹ thuật: [`references/xuat_pdf_latex.md`](./references/xuat_pdf_latex.md).

## 🤖 UX Chủ Động (Proactive UX) — BẮT BUỘC ÁP DỤNG

> [!IMPORTANT]
> Agent PHẢI chủ động gợi ý tính năng và hiển thị menu sau mỗi task. Giáo viên KHÔNG cần biết lệnh. Khi giáo viên gõ *"trợ giúp"*, *"?"*, *"help"* hoặc lần đầu dùng → xem menu Help/Onboarding trong [`references/ux_chu_dong.md`](./references/ux_chu_dong.md).

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

---

## 🎓 Bước 7: Chấm bài tự luận bằng AI
Học sinh nộp ảnh → OCR → chấm theo rubric GDPT 2018 (`scripts/essay_grader.py`, `scripts/grading_report.py`, `references/rubric_templates.json`). **AI chỉ GỢI Ý điểm — giáo viên quyết định cuối cùng; Agent PHẢI hỏi GV xác nhận trước khi lưu điểm.** Quy trình, giao diện kết quả, danh sách rubric: [`references/cham_bai_tu_luan.md`](./references/cham_bai_tu_luan.md).

## ⚗️ Môn Hóa học — Quy chuẩn bắt buộc (GDPT 2018 & IUPAC)
- Nguyên tố/hợp chất dùng font thẳng `\mathrm{...}`; điện tích ion ghi số trước dấu sau (`\mathrm{SO_4^{2-}}`); danh pháp IUPAC.
- Phương trình có điều kiện: BẮT BUỘC `\xrightarrow[dưới]{trên}` / `\xrightleftharpoons`, KHÔNG dùng `\overset{}{\underset{}{\rightleftharpoons}}`.
- Lập sơ đồ bảo toàn (khối lượng, nguyên tố, electron, điện tích) trước khi tính; tính hiệu suất. Đầy đủ: [`references/quy_chuan_hoa_hoc.md`](./references/quy_chuan_hoa_hoc.md).

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

---

## 🎨 Render TikZ & LaTeX 300 DPI
`scripts/tikz_renderer.py` — `render_tikz(code, out.png, dpi=300)`; Local Engine (MiKTeX/TeX Live) + Cloud fallback; hỗ trợ `tkz-tab`, `tkz-euclide`, `pgfplots`, `circuitikz`, `chemfig`. Chi tiết & CLI: [`references/tikz_engine.md`](./references/tikz_engine.md); 80 mẫu: [`references/tikz_templates.md`](./references/tikz_templates.md).

## 🌐 BƯỚC 6: Dịch đề sang tiếng Anh học thuật & đề song ngữ
Dùng `scripts/exam_translator.py`; 2 chế độ: **English-only** (`<TEN>_ENGLISH_MATHTYPE_OLE.docx`) và **Bilingual** (Anh–Việt). Vẫn áp dụng đầy đủ quy trình Bước 4 (MathType OLE). Chi tiết: [`references/dich_tieng_anh.md`](./references/dich_tieng_anh.md).

## 🎧 BƯỚC 6bis: Tạo Đề Tiếng Anh & Xuất File Nghe MP3 Chuẩn Phòng Thi (Khớp 100% Câu Hỏi)
Dùng `scripts/english_listening_mp3_builder.py` thực thi **Kế hoạch Đồng bộ hóa Ngược 5 Bước** (`Anchor-Point Mapping [Q1..Qn]` $\rightarrow$ `Strict Linear Order` $\rightarrow$ `Spoken-Text Normalization` $\rightarrow$ `Cross-Audit QA Gate` $\rightarrow$ `Multi-Voice Studio Mixing`). Tự động xuất cả **File Master MP3 toàn bài** (lời dẫn, chuông báo, khoảng lặng đọc đề, nghe 2 lần) và **các File MP3 lẻ từng Part**. Chi tiết bắt buộc đọc: [`references/tao_file_nghe_mp3_tieng_anh.md`](./references/tao_file_nghe_mp3_tieng_anh.md).

## 📝 Phiên bản & Video khởi động bài học
- Phiên bản hiện hành & lịch sử thay đổi: `version.json`, [`references/CHANGELOG.md`](./references/CHANGELOG.md).
- Tạo kịch bản / prompt **Veo 3** cho video khởi động bài học: dùng skill riêng **`tao-video-khoi-dong-bai-hoc`** (không lặp lại ở đây).

