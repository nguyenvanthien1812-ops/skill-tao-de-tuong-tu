# Bước 2 — Thiết kế số liệu theo độ khó & Kiểm định chuẩn GDPT 2018 (checklist đầy đủ)

> Đọc khi thiết kế đề tương tự (bảng điều chỉnh số liệu, tỷ lệ NB/TH/VD/VDC) và trước khi xuất đề (Bước 2bis — bắt buộc).
> *(Tài liệu tham chiếu của skill `tao-de-toan-tuong-tu` — được tách ra từ `SKILL.md` để SKILL.md gọn; nội dung quy tắc giữ nguyên.)*

---

### Bước 2: Thiết kế bài toán tương đương & Kiểm định toán học

#### 🎯 Bước 2.0 – Xác định mức độ khó (MANDATORY – BẮT BUỘC ĐẦU TIÊN)

> **QUY TẮC VÀNG**: Dạng bài / kiểu bài PHẢI GIỐNG ĐỀ GỐC 100%. Chỉ được thay đổi số liệu và độ phức tạp tính toán. KHÔNG được đổi dạng.

Trước khi thiết kế số liệu, Agent PHẢI xác định `difficulty_level` từ yêu cầu người dùng:

| Người dùng nói | `difficulty_level` | Hướng dẫn thiết kế số liệu |
|---------------|---------------------|-----------------------------|
| (Không nói gì / mặc định) | `equivalent` | Cùng mức độ phức tạp tính toán như đề gốc |
| "tương đương", "cùng mức", "như vậy" | `equivalent` | Cùng mức độ phức tạp tính toán như đề gốc |
| "dễ hơn", "đơn giản hơn", "ít khó hơn" | `easier` | Giảm độ phức tạp tính toán |
| "khó hơn", "nâng cao hơn", "thử thách hơn" | `harder` | Tăng độ phức tạp tính toán |

**Bảng điều chỉnh số liệu theo `difficulty_level`:**

| Dạng bài | `easier` | `equivalent` | `harder` |
|----------|----------|--------------|----------|
| **Hàm bậc ba** $ax^3+bx^2+cx+d$ | $a=1$, nghiệm đạo hàm nguyên đơn giản ($x=0,\pm1$) | $a=1$, nghiệm đạo hàm nguyên đẹp | $a\in\{1,-1,2\}$, tham số có phân số gọn |
| **Phân thức bậc 1/bậc 1** | Tiệm cận nguyên đơn giản, nghiệm = 0 | Tiệm cận nguyên, nghiệm nguyên | Tiệm cận phân số, cực trị phức tạp hơn |
| **Tích phân định thức** | Cận $[0;1]$, $f(x)$ đơn thức | Cận $[a;b]$ nguyên, đa thức bậc ≤3 | Cận có căn thức, tích phân từng phần |
| **Hàm lượng giác** | Biên độ 1, chu kỳ $2\pi$ | Biên độ nguyên, pha ban đầu đẹp | Pha ban đầu $\pi/6$, $\pi/4$; phép dịch |
| **Hình học không gian** | Hộp chữ nhật, tỉ số đơn | Chóp có cạnh nguyên gọn | Chóp cụt, thiết diện chéo phức tạp |
| **Phương trình / BPT** | Nghiệm nguyên, bậc 2 đơn | Nghiệm nguyên hoặc phân số gọn | Nghiệm vô tỉ $\sqrt{\cdot}$, ẩn phức hợp |
| **Bài toán thực tế** | Hàm mục tiêu bậc 2, điểm dừng $x_0$ nguyên | Hàm bậc 3, điểm dừng nguyên | Hàm bậc 4 hoặc hỗn hợp, ràng buộc thực tế |
| **Hóa học – Phản ứng** | Phân tử đơn giản, cân bằng hệ số nhỏ | Phương trình cân bằng chuẩn | Phản ứng nhiều bước, tính hiệu suất |
| **Vật lý – Dao động / Điện** | Biên độ nguyên, tần số đẹp | Biên độ nguyên, pha ban đầu $0$ hoặc $\pi/2$ | Pha ban đầu $\pi/6$, mạch RLC phức hợp |

**Bảng điều chỉnh tỷ lệ NB / TH / VD / VDC theo `difficulty_level`:**

> [!IMPORTANT]
> Agent PHẢI điều chỉnh phân phối mức độ tư duy **toàn đề** theo bảng này. Không chỉ thay số liệu — phải thực sự phân bổ lại số câu hỏi theo từng mức.

| Mức độ | NB (Nhận biết) | TH (Thông hiểu) | VD (Vận dụng) | VDC (Vận dụng cao) | Ghi chú |
|--------|---------------|-----------------|---------------|---------------------|---------|
| `easier` | ~40% | ~40% | ~15% | ~5% | Ưu tiên câu tính tay được, không cần máy tính; bỏ câu tích hợp liên chủ đề |
| `equivalent` | ~30% | ~40% | ~20% | ~10% | Giữ nguyên phân phối chuẩn GDPT 2018 như đề gốc |
| `harder` | ~20% | ~30% | ~25% | ~25% | Thêm câu tích hợp liên chủ đề; phương án mồi bẫy sai tinh vi hơn |

**Ví dụ áp dụng — Đề Toán 45 câu, 90 phút:**

| | `easier` | `equivalent` | `harder` |
|-|----------|--------------|----------|
| NB | 18 câu | 14 câu | 9 câu |
| TH | 18 câu | 18 câu | 14 câu |
| VD | 7 câu | 9 câu | 11 câu |
| VDC | 2 câu | 4 câu | 11 câu |
| **Tổng** | **45 câu** | **45 câu** | **45 câu** |

**Ví dụ áp dụng — thay đổi số liệu câu cụ thể:**
- Đề gốc có câu: *"Hàm $y = x^3 - 3x + 2$ có bao nhiêu cực trị?"*
  - `easier`: $y = x^3 - 3x$ (bỏ hằng số, nghiệm đơn hơn)
  - `equivalent`: $y = x^3 - 3x^2 + 4$ (cùng bậc, cùng số cực trị)
  - `harder`: $y = x^3 - 3x^2 + 4x - 2$ (thêm tham số, đòi hỏi tính toán hơn)

Với mỗi câu hỏi trong đề gốc:
1. **Điều chỉnh phân phối NB/TH/VD/VDC toàn đề**: Áp dụng bảng tỷ lệ bên trên theo `difficulty_level`. Nếu `easier` → chuyển một số câu VD/VDC thành câu TH/NB cùng dạng bài nhưng đơn giản hơn. Nếu `harder` → nâng độ tư duy của một số câu NB/TH lên VD/VDC.
2. **Giữ nguyên dạng toán & phương pháp giải**: Đổi số liệu, tham số theo bảng điều chỉnh số liệu bên trên.
3. **Chọn số liệu nghiệm đẹp** (áp dụng bảng trên theo `difficulty_level`):
   - Hàm bậc ba / phân thức: Chọn nghiệm đạo hàm nguyên (ví dụ $x = 0, x = 2$ hoặc $x = \pm 1$), tung độ cực trị nguyên.
   - Bài toán thực tế / tối ưu hóa: Đảm bảo điểm dừng $x_0$ rơi vào khoảng thực tế và cho kết quả nguyên hoặc số thập phân gọn.
4. **Lập bảng kiểm định**: Tính toán đạo hàm, cực trị, giới hạn tiệm cận để đảm bảo đáp án trắc nghiệm không bị trùng hoặc vô nghiệm.

---


### ✅ Bước 2bis: Kiểm Định Chuẩn GDPT 2018 (BẮT BUỘC TRƯỚC KHI XUẤT ĐỀ)

> [!IMPORTANT]
> **CHỈ THỊ BẮT BUỘC:** Sau khi thiết kế xong toàn bộ câu hỏi, Agent PHẢI tự kiểm tra checklist dưới đây. Nếu bất kỳ mục nào KHÔNG ĐẠT, phải sửa trước khi xuất file Word.

#### Checklist Kiểm Định Tự Động (8 môn, lớp 6–12):

```
✅ CHECKLIST GDPT 2018
══════════════════════════════════════════════════════════════════════

□ [CẤU TRÚC] Đề có đủ 3 phần theo chuẩn GDPT 2018?
  - Môn KHTN/Toán/Lý/Hóa/Sinh/Địa/KTPL: Phần I + II + III (+ Tự luận nếu là đề học kỳ)
  - Môn Ngữ Văn: Đọc hiểu + Viết (KHÔNG có trắc nghiệm A/B/C/D)

□ [ĐÚNG/SAI] Mỗi câu Phần II có ĐÚNG 4 ý a/b/c/d không?
  - Ý a: mức NB | Ý b: mức TH | Ý c: mức VD | Ý d: mức VDC
  - Không được tất cả 4 ý đều ĐÚNG hoặc đều SAI

□ [TỈ LỆ NB/TH/VD/VDC] Tổng tỉ lệ trên toàn đề xấp xỉ 30:40:20:10 (%)?

□ [TRẢ LỜI NGẮN] Tất cả đáp án Phần III là số nguyên hoặc thập phân ≤ 2 chữ số?

□ [THỰC TIỄN] Có ít nhất 1–2 câu mang ngữ cảnh đời sống thực tế?

□ [TỰ LUẬN] Lời giải tự luận có bước "phiên giải kết quả về thực tiễn"?

□ [PHƯƠNG PHÁP GIẢI GDPT 2018] Lời giải TUYỆT ĐỐI không dùng phương pháp cũ (2006):
  - Toán: Đủ 4 bước mô hình hóa + câu kết luận phiên giải thực tế ("Vậy trong thực tế, ...")
  - Vật Lý: Quy ước chiều dương + mốc thời gian + đơn vị SI + nhận xét ý nghĩa vật lý
  - Hóa Học: Lập sơ đồ bảo toàn (KL/NT/e/ĐT) trước khi tính + trạng thái chất + điều kiện phản ứng
  - Địa Lý: Đủ 4 bước phân tích (nhận xét chung → chi tiết → nguyên nhân → giải pháp phát triển bền vững)
  - KTPL: Đủ 5 bước giải quyết tình huống pháp luật

□ [VALIDATOR BẮT BUỘC] Chạy script kiểm định tự động trước khi xuất đề:
  python scripts/gdpt2018_validator.py (hoặc gọi validate_exam_gdpt2018(exam_data))
  Validator tự động kiểm tra cả cấu trúc đề VÀ phương pháp giải của từng câu!

══════════════════════════════════════════════════════════════════════
```

#### Phương Pháp Giải Chuẩn GDPT 2018 Theo Từng Môn:

**🔵 Môn Toán — Bắt buộc áp dụng Mô hình hóa toán học (4 bước):**
```
Bước 1 — Thực tiễn → Toán học: Đặt biến, lập hàm số mô tả tình huống
Bước 2 — Giải toán học: Tính đạo hàm, tìm cực trị, giải PT/BPT
Bước 3 — Kiểm tra điều kiện thực tế: Nghiệm > 0, trong miền thực tế
Bước 4 — Phiên giải: "Vậy trong thực tế, [kết luận có ý nghĩa]."
```
- **Thống kê & Xác suất** (lớp 6+): Phân phối nhị thức $B(n,p)$, chuẩn $N(\mu,\sigma^2)$, kết quả phải là phân số gọn hoặc thập phân ≤ 2 chữ số.
- **Hình học không gian**: Luôn gắn với ứng dụng thực tế (tính vật liệu, chi phí, thể tích bồn chứa).

**🔴 Môn Vật Lý — Quy trình thực nghiệm 6 bước:**
```
1. Xác định vấn đề → 2. Giả thuyết → 3. Thiết kế thí nghiệm
4. Đo đạc (≥3 lần) → 5. Xử lý sai số → 6. Kết luận
```
- **Bắt buộc ghi**: Quy ước chiều dương; giả thuyết bỏ qua (ma sát, lực cản...); phân tích lực bằng hình vẽ; đơn vị SI chuẩn $\mathrm{m/s, kg, N, Pa, J, W}$.
- **Phân tích sai số**: $\bar{X} = \frac{1}{n}\sum x_i$; $\Delta X = \frac{1}{n}\sum|x_i - \bar{X}|$; $\delta X = \frac{\Delta X}{\bar{X}} \times 100\%$.
- **Câu Đúng/Sai thực nghiệm**: Ít nhất 1 câu dựa trên bảng số liệu đo đạc thực.

**🟢 Môn Hóa Học — Sơ đồ bảo toàn bắt buộc:**
```
🔵 Bảo toàn khối lượng: Σm(đầu vào) = Σm(sản phẩm)
🔴 Bảo toàn nguyên tố: n(X) = const qua phản ứng
🟡 Bảo toàn electron: Σe(nhường) = Σe(nhận)
🟢 Bảo toàn điện tích: Σ(ion+) = Σ(ion−) trong dung dịch
```
- **Font IUPAC**: $\mathrm{Fe, Al, Cu, H_2O, Fe_2O_3}$ — KHÔNG in nghiêng.
- **Điều kiện phản ứng**: $\xrightarrow{t^\circ, \text{xt}}$, $\xrightarrow{\text{ánh sáng}}$, trạng thái $(s)(l)(g)(aq)$, ký hiệu $\downarrow\uparrow$.
- **Hóa học xanh**: Tính hiệu suất phản ứng $H\% = \frac{m_{SP}}{m_{LT}} \times 100\%$; liên hệ ứng dụng môi trường.

**🟣 Môn Sinh Học — Quy trình khoa học 6 bước:**
```
Quan sát → Đặt câu hỏi → Giả thuyết → Thí nghiệm (có nhóm đối chứng)
→ Phân tích số liệu → Kết luận & Phổ biến
```
- **Di truyền**: Sơ đồ lai đầy đủ P→F1→F2; tỉ lệ kiểu gen/kiểu hình; liên hệ bệnh di truyền người.
- **Ứng dụng**: Vaccine, GMO, tế bào gốc, xử lý ô nhiễm vi sinh — phải nêu ý nghĩa thực tiễn.

**🌍 Môn KHTN lớp 6–9 — Tích hợp liên môn:**
- Mỗi câu Đúng/Sai nên kết hợp ≥ 2 phân môn (Lý+Hóa / Hóa+Sinh / Lý+Sinh).
- Quy trình khoa học: Quan sát → Giả thuyết → Thực nghiệm → Kết luận.
- Ngữ cảnh: Bảo vệ môi trường, tiết kiệm năng lượng, an toàn thực phẩm, sức khỏe cộng đồng.

**🗺️ Môn Địa Lý — Kỹ năng phân tích biểu đồ/bản đồ chuẩn GDPT 2018:**
```
Bước 1: Nhận xét chung (tổng quan toàn biểu đồ)
Bước 2: Nhận xét chi tiết (từng thành phần, giai đoạn; max/min; xu hướng tăng/giảm)
Bước 3: Giải thích nguyên nhân
Bước 4: Kết luận và liên hệ thực tiễn Việt Nam / Thế giới
```
- Câu Tự luận Địa lý: PHẢI có đề xuất giải pháp phát triển bền vững.

**⚖️ Môn Kinh Tế & Pháp Luật — Giải tình huống pháp luật 5 bước:**
```
1. Xác định chủ thể (ai? vai trò?)
2. Xác định quan hệ pháp lý (hợp đồng? vi phạm? tranh chấp?)
3. Tìm quy phạm pháp luật áp dụng
4. Áp dụng vào tình huống cụ thể
5. Kết luận: Hành vi đúng/sai? Hậu quả pháp lý? Giải pháp bảo vệ quyền lợi?
```

**📖 Môn Ngữ Văn — Đọc hiểu và Viết theo GDPT 2018:**
- **Đọc hiểu**: Câu hỏi theo 4 mức NB→TH→VD→VDC; phát hiện biện pháp tu từ, phân tích tác dụng, liên hệ thực tiễn.
- **Nghị luận XH**: Giải thích → Thực trạng → Nguyên nhân/Hậu quả → Giải pháp → Liên hệ bản thân.
- **Nghị luận VH**: Giới thiệu tác giả/tác phẩm → Phân tích luận điểm (dẫn chứng + bình) → Đánh giá nghệ thuật → Liên hệ mở rộng.

---

> [!IMPORTANT]
> ### ⛔ CHECKLIST BẮT BUỘC KIỂM TRA LỜI GIẢI TRƯỚC KHI XUẤT (GDPT 2018)
>
> Agent PHẢI tự rà soát từng mục dưới đây. **Nếu bất kỳ mục nào CHƯA ĐẠT → phải sửa ngay, KHÔNG được xuất file.**
>
> #### 🔵 Toán — Lời Giải Tự Luận / Phần III:
> ```
> □ Có đặt biến rõ ràng + điều kiện biến (x > 0, n ∈ ℕ*, ...)?
> □ Lập hàm số/phương trình mô tả đúng bài toán?
> □ Giải toán học đầy đủ (tính f'(x), tìm nghiệm, xét dấu...)?
> □ Kiểm tra nghiệm trong miền thực tế?
> □ CÓ câu kết luận "Vậy trong thực tế, [ý nghĩa kết quả]."? ← THIẾU NHIỀU NHẤT
> □ Kết quả Phần III là số nguyên hoặc thập phân ≤ 2 chữ số?
> ```
>
> #### 🔴 Vật Lý — Lời Giải:
> ```
> □ Ghi "Chọn chiều dương là..." ở đầu lời giải?   ← THIẾU NHIỀU NHẤT
> □ Ghi "Bỏ qua [ma sát/lực cản/...]" nếu bài không cho số liệu đó?
> □ Có sơ đồ/hình phân tích lực (kể cả mô tả bằng text)?
> □ Đơn vị kết quả ghi đúng hệ SI (m/s, kg, N, Pa, J, W, Hz, T)?
> □ Có câu nhận xét ý nghĩa vật lý: "Dấu âm có nghĩa... / Kết quả này cho thấy..."?
> □ Câu thực nghiệm: Có bảng số liệu + phân tích sai số (ΔX, δX%)?
> ```
>
> #### 🟢 Hóa Học — Lời Giải:
> ```
> □ Bài hỗn hợp: ĐÃ lập sơ đồ bảo toàn trước khi tính?  ← THIẾU NHIỀU NHẤT
>   (bảo toàn khối lượng / nguyên tố / electron / điện tích)
> □ Phương trình hóa học CÓ điều kiện phản ứng (t°, xt, as, p)?
> □ Phương trình CÓ trạng thái chất (s)(l)(g)(aq)?
> □ Phương trình CÓ ký hiệu ↓ (kết tủa), ↑ (khí)?
> □ Font IUPAC: tên nguyên tố THẲNG ĐỨNG \mathrm{Fe, Al, Cu} — KHÔNG in nghiêng?
> □ Có nhắc đến ứng dụng / ý nghĩa thực tế của phản ứng (Hóa học xanh)?
> □ Nếu có hiệu suất: ghi rõ H=...% áp dụng cho chất nào?
> ```
>
> #### 🟣 Sinh Học — Lời Giải:
> ```
> □ Sơ đồ lai đầy đủ: P (kiểu gen) → Giao tử P → F1 (kiểu gen + kiểu hình)?
> □ Tỉ lệ kiểu gen + kiểu hình ghi dạng phân số (1:2:1, 3:1, 9:3:3:1)?
> □ Có liên hệ ứng dụng thực tiễn (y học, nông nghiệp, môi trường)?
> □ Bài thực nghiệm: có nhóm đối chứng + nhóm thực nghiệm?
> ```
>
> #### 🗺️ Địa Lý — Lời Giải Tự Luận:
> ```
> □ Bước 1: Nhận xét CHUNG trước (xu hướng tổng quan)?
> □ Bước 2: Nhận xét CHI TIẾT (max/min/tăng/giảm từng thành phần)?
> □ Bước 3: Giải thích NGUYÊN NHÂN?
> □ Bước 4: Kết luận + ĐỀ XUẤT GIẢI PHÁP phát triển bền vững?  ← THIẾU NHIỀU NHẤT
> ```
>
> #### ⚖️ KTPL — Lời Giải Tình Huống:
> ```
> □ Bước 1: Xác định đủ các CHỦ THỂ trong tình huống (tên, vai trò)?
> □ Bước 2: Xác định LOẠI QUAN HỆ PHÁP LÝ (hợp đồng/vi phạm/tranh chấp)?
> □ Bước 3: Chỉ ra QUY PHẠM PHÁP LUẬT áp dụng (điều, khoản luật cụ thể)?
> □ Bước 4: ÁP DỤNG quy phạm vào tình huống?
> □ Bước 5: KẾT LUẬN hành vi đúng/sai + hậu quả pháp lý + giải pháp?  ← THIẾU NHIỀU NHẤT
> ```
>
> #### 📝 Câu Đúng/Sai (Tất cả môn) — Bắt buộc đúng thứ tự:
> ```
> □ Ý a = mức NB (nhận biết thuần túy từ lý thuyết)
> □ Ý b = mức TH (suy luận, so sánh)
> □ Ý c = mức VD (tính toán, áp dụng công thức)
> □ Ý d = mức VDC (kết luận mở, tình huống mới, phản biện)
> □ Không được: tất cả 4 ý đều ĐÚNG hoặc đều SAI
> □ Đáp án mỗi ý phải CÓ LỜI GIẢI giải thích tại sao Đúng/Sai
> ```

---

### 📋 Bảng So Sánh "Cũ vs Mới" — Những Lỗi Phổ Biến Nhất

> [!WARNING]
> Các mẫu lời giải CŨ dưới đây **nghiêm cấm** xuất hiện trong đề/lời giải của skill.

#### ❌ Toán — Lời Giải Cũ vs ✅ Mới:

| ❌ **Cách cũ (CHƯƠNG TRÌNH 2006)** | ✅ **Cách mới (GDPT 2018)** |
|:----------------------------------|:--------------------------|
| Tính ra x = 500, kết luận "Vậy x = 500." | **"Vậy trong thực tế, để chi phí nhỏ nhất là 120 triệu đồng, doanh nghiệp cần sản xuất đúng 500 sản phẩm/ngày."** |
| Giải xác suất bằng liệt kê toàn bộ | Dùng phân phối nhị thức $X \sim B(n, p)$, tính $P(X=k) = \binom{n}{k}p^k(1-p)^{n-k}$ |
| Hình học không gian chỉ tính V, S | Gắn ngữ cảnh: "Một bể nước có hình chóp... cần bao nhiêu vật liệu để sản xuất?" |

#### ❌ Vật Lý — Lời Giải Cũ vs ✅ Mới:

| ❌ **Cách cũ** | ✅ **Cách mới** |
|:-------------|:--------------|
| Áp dụng công thức F = ma, tính ra F = 10 N. | **"Chọn chiều dương là chiều chuyển động. Bỏ qua ma sát. Theo định luật II Newton: F = ma = 2×5 = 10 N. Dấu dương cho thấy lực cùng chiều chuyển động."** |
| Cho bảng số liệu, tính trung bình cộng. | Tính đủ: $\bar{X}$, $\Delta X$, $\delta X\%$, viết kết quả $X = \bar{X} \pm \Delta X$ (đơn vị). |
| Bài tập điện xoay chiều không nhắc ứng dụng. | Liên hệ: "Đây là nguyên lý hoạt động của máy phát điện / động cơ điện trong công nghiệp." |

#### ❌ Hóa Học — Lời Giải Cũ vs ✅ Mới:

| ❌ **Cách cũ** | ✅ **Cách mới** |
|:-------------|:--------------|
| Viết PT: `Fe + HCl → FeCl2 + H2↑` | **`$\mathrm{Fe_{(s)} + 2HCl_{(aq)} \rightarrow FeCl_2{(aq)} + H_2\uparrow_{(g)}}$`** (font thẳng, trạng thái, ký hiệu khí) |
| Tính trực tiếp n(Fe) = 0.1 mol, m = 5.6g. | **Lập sơ đồ bảo toàn nguyên tố Fe trước:** $n_{\mathrm{Fe}}(\text{đầu}) = n_{\mathrm{Fe}}(\text{sản phẩm})$, sau đó tính. |
| Kết luận: "Vậy m = 5.6g." | **"Vậy m = 5.6g. Phản ứng này ứng dụng trong xử lý nước thải axit công nghiệp."** |
| Phương trình không ghi điều kiện. | Bắt buộc: `$\xrightarrow{t^\circ, \text{xt}}$` hoặc `$\xrightarrow{\text{ánh sáng}}$` |

#### ❌ Địa Lý — Lời Giải Cũ vs ✅ Mới:

| ❌ **Cách cũ** | ✅ **Cách mới** |
|:-------------|:--------------|
| "GDP năm 2020 là X tỉ USD, năm 2023 là Y tỉ USD, tăng Z%." | **B1 Chung:** "Nhìn chung GDP tăng liên tục giai đoạn 2020-2023." → **B2 Chi tiết:** "Tốc độ tăng nhanh nhất năm... Thấp nhất năm... do..." → **B3 Nguyên nhân** → **B4: Đề xuất chính sách thu hút đầu tư / phát triển bền vững."** |
| Nhận xét biểu đồ không có đề xuất giải pháp. | Câu tự luận Địa lý PHẢI có Bước 4: Đề xuất giải pháp. |
