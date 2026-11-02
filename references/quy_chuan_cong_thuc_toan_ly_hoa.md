# Quy Chuẩn Soạn Thảo Công Thức Toán, Vật Lý & Hóa Học (Lớp 6–12) Chuẩn MathType OLE (GDPT 2018)

> **Tài liệu tham chiếu bắt buộc của skill `tao-de-toan-tuong-tu`**
> Áp dụng xuyên suốt khi: Tạo đề thi mới, Chuyển PDF sang Word, Chuẩn hóa công thức Word, Giải bài chi tiết, Soạn giáo án & Slide bài giảng.

---

## 🌟 4 LỜI KHUYÊN VÀNG CHO GIÁO VIÊN & AGENT (BẢO ĐẢM 100% MATHTYPE OLE ĐẸP CHUẨN)

Khi soạn thảo bất kỳ công thức Toán, Lý, Hóa nào (ở dạng mã LaTeX trong dấu `$...$` hoặc `$$...$$`), Agent và Thầy/Cô **BẮT BUỘC** tuân thủ 4 nguyên tắc sau để Local Engine biên dịch thành MathType OLE nguyên bản (`Equation.DSMT4`, Times New Roman 14pt) không bao giờ bị lỗi:

### 1. Luôn bao ngoặc nhọn `{ }` đầy đủ cho số mũ, chỉ số và biểu thức phức hợp
- **Quy tắc**: Mọi chỉ số dưới (`_`), số mũ (`^`), hoặc biểu thức con bắt buộc phải bọc trong `{ }`.
- **Đúng**: `x_{12}`, `a^{2n+1}`, `C_n^k`, `v_0`, `\Delta_r H_{298}^\circ`, `^{238}_{\;92}\mathrm{U}`.
- ❌ **Sai**: `x_12` (sẽ thành $x_1$ cạnh số 2), `a^2n+1` (thành $a^2$ nhân $n+1$).

### 2. Tiếng Việt & Chú thích chữ trong công thức BẮT BUỘC bọc trong `\text{...}`
- **Quy tắc**: Tuyệt đối không gõ tiếng Việt có dấu trần trụi trực tiếp vào giữa công thức toán học.
- **Đúng**: 
  * Toán: $S_{\text{tam giác}} = \frac{1}{2}ah$, $V_{\text{khối nón}} = \frac{1}{3}\pi R^2 h$.
  * Lý: $\vec{F}_{\text{hl}} = m \vec{a}$, $W_{\text{đ}} = \frac{1}{2}mv^2$, $F_{\text{ms}} = \mu N$.
  * Hóa: $\Delta_r H_{298}^\circ = \sum E_b(\text{cđ}) - \sum E_b(\text{sp})$, $C\% = \frac{m_{\text{ct}}}{m_{\text{dd}}} \times 100\%$.
- ❌ **Sai**: $S_{tam giác}$, $W_đ$, $m_{chất tan}$ (gây lỗi phân tích từ vựng LaTeX và làm méo dạng chữ).

### 3. Hệ phương trình & Hệ điều kiện: Dùng môi trường `\begin{cases} ... \end{cases}`
- **Quy tắc**: Phân tách các dòng bằng hai dấu gạch chéo ngược `\\`. Không dùng các ký tự ngoặc nhọn vẽ tay lẻ loi.
- **Đúng**:
  $$\begin{cases} 2x + 3y = 7 \\ 4x - y = 5 \end{cases}$$
- Local Engine tự động chuyển sang cấu trúc StarMath `left lbrace stack{...} right none`, tạo dấu ngoặc nhọn lớn co dãn ôm khít các dòng và căn lề trái đều tăm tắp.

### 4. Ký hiệu Hình học đặc thù: Dùng chuẩn `\widehat{...}` (Góc) và `\wideparen{...}` (Cung)
- **Quy tắc**:
  * Góc: Dùng `\widehat{ABC}` hoặc `\widehat{A}` (mũ rộng trùm lên cả 3 đỉnh).
  * Cung tròn: Dùng `\wideparen{AB}` hoặc `\wideparen{CD}` (dấu cung cong trùm trên đầu).
  * Vectơ: Dùng `\vec{a}`, `\vec{AB}`, `\vec{v_0}`.
- Hệ thống đã tích hợp `arc_symbol_builder.py` để dựng nhị phân MTEF Frown Overstrike chuẩn xác của MathType, không bao giờ bị đè chữ hay biến thành ô vuông.

---

## 📐 I. QUY CHUẨN CÔNG THỨC TOÁN HỌC (LỚP 6 – 12)

| Khối lớp | Chủ đề trọng tâm | Quy cách LaTeX chuẩn |
| :--- | :--- | :--- |
| **Lớp 6–7** | Phân số, hỗn số, lũy thừa, tỉ lệ thức | `\frac{a}{b}`, `\frac{a}{b} = \frac{c}{d} \Rightarrow ad = bc`, `2^{10} = 1024` |
| **Lớp 7–9** | Căn thức, Vi-ét, Pythagoras, PT bậc 2 | `x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}`, `x_1 + x_2 = -\frac{b}{a}` |
| **Lớp 9–10** | Hệ phương trình, BĐT Cauchy | `\begin{cases} ax + by = c \\ dx + ey = f \end{cases}`, `\frac{a+b}{2} \geq \sqrt{ab}` |
| **Lớp 10** | Lượng giác, Vectơ, Tổ hợp, Nhị thức | `\sin^2 x + \cos^2 x = 1`, `\vec{a}\cdot\vec{b} = |\vec{a}||\vec{b}|\cos\theta`, `(a+b)^n = \sum_{k=0}^{n} C_n^k a^{n-k}b^k` |
| **Lớp 11** | Giới hạn, Đạo hàm, Cấp số, Số phức | `\lim_{x \to 0}\frac{\sin x}{x}=1`, `\left(\frac{u}{v}\right)' = \frac{u'v-uv'}{v^2}`, `z = a + bi` |
| **Lớp 12** | Tích phân, Logarit, Oxyz, Ma trận | `\int_a^b f(x)\,dx`, `d(M,(P)) = \frac{|Ax_0+By_0+Cz_0+D|}{\sqrt{A^2+B^2+C^2}}`, `\det\begin{pmatrix}a&b\\c&d\end{pmatrix}` |

---

## ⚡ II. QUY CHUẨN CÔNG THỨC VẬT LÝ & KHTN (LỚP 6 – 12)

### 1. Đại lượng vectơ & Chuyển động (Vật lý 10)
- Vectơ gia tốc, vận tốc, động lượng, lực: Luôn dùng `\vec{...}`.
  * Đúng: `\vec{F}_{\text{hl}} = m \vec{a}`, `\Delta \vec{p} = \vec{F}\Delta t`, `\vec{v} = \vec{v_0} + \vec{a}t`.
- Hệ thức độc lập & rơi tự do: `v^2 - v_0^2 = 2as`, `s = v_0 t + \frac{1}{2}at^2`.

### 2. Dao động điều hòa & Sóng (Vật lý 11)
- Phương trình li độ, vận tốc: `x = A \cos(\omega t + \varphi)`, `v = -\omega A \sin(\omega t + \varphi)`.
- Chu kỳ, bước sóng: `T = 2\pi\sqrt{\frac{l}{g}} = 2\pi\sqrt{\frac{m}{k}}`, `\lambda = v \cdot T = \frac{v}{f}`.
- Điện trường & Coulomb: `F = k \frac{|q_1 q_2|}{\varepsilon r^2}`, `E = \frac{F}{|q|}`.
- Từ thông & Suất điện động cảm ứng: `\Phi = B S \cos\alpha`, `e_c = -\frac{\Delta\Phi}{\Delta t}`.

### 3. Nhiệt học, Khí lý tưởng & Vật lý Hạt nhân (Vật lý 12 GDPT 2018)
- Nhiệt lượng & Chuyển thể: `Q = mc\Delta T`, `Q = \lambda m`, `Q = Lm`.
- Phương trình khí lý tưởng: `pV = nRT = \frac{m}{M}RT`, `\Delta U = A + Q`.
- **Ký hiệu hạt nhân & Phản ứng hạt nhân (BẮT BUỘC CÓ DẤU CÁCH HOẶC CANH CHUẨN TRÊN/DƯỚI)**:
  * Ký hiệu đồng vị hạt nhân: Dùng `^{A}_{Z}\mathrm{X}` hoặc `^{A}_{\;Z}\mathrm{X}` để số khối $A$ và nguyên tử số $Z$ nằm thẳng đứng ở bên trái tên nguyên tố thẳng đứng `\mathrm{X}`.
  * Ví dụ phân rã Alpha: `^{238}_{\;92}\mathrm{U} \rightarrow ^{234}_{\;90}\mathrm{Th} + ^{4}_{2}\mathrm{He}`.
  * Phản ứng phân hạch: `^{235}_{\;92}\mathrm{U} + ^{1}_{0}n \rightarrow ^{144}_{\;56}\mathrm{Ba} + ^{89}_{\;36}\mathrm{Kr} + 3\,^{1}_{0}n`.
  * Độ hụt khối & Năng lượng liên kết:
    $$E_{\text{lk}} = \Delta m \cdot c^2 = \left[Z m_p + (A-Z)m_n - m_X\right]c^2$$
  * Định luật phóng xạ: `N(t) = N_0 \cdot 2^{-\frac{t}{T}} = N_0 \cdot e^{-\lambda t}` (với `\lambda = \frac{\ln 2}{T}`).

### 4. Đơn vị đo lường (SI):
- Luôn đặt đơn vị trong `\text{...}` hoặc cách một dấu phẩy mỏng:
  * Ví dụ: `v = 20\text{ m/s}`, `a = 9{,}8\text{ m/s}^2`, `R = 50\,\Omega`, `C = 10\,\mu\text{F}`.

---

## ⚗️ III. QUY CHUẨN CÔNG THỨC HÓA HỌC & KHTN (LỚP 6 – 12)

### 1. Font chữ IUPAC & Điện tích ion
- **Font thẳng đứng**: Nguyên tố, phân tử và ion **bắt buộc** dùng `\mathrm{...}`.
  * Đúng: `\mathrm{Fe, Al, Cu, H_2O, CaCO_3, H_2SO_4}`.
- **Điện tích ion (Quy ước mới GDPT 2018)**: Ghi **Số trước, Dấu sau**.
  * Đúng: `\mathrm{Al^{3+}}`, `\mathrm{Fe^{2+}}`, `\mathrm{SO_4^{2-}}`, `\mathrm{Cl^-}`.
  * ❌ Sai: `Al^{+3}`, `SO_4^{-2}`.

### 2. Mũi tên phản ứng & Điều kiện
- **Mũi tên có điều kiện kéo dài**: Bắt buộc dùng `\xrightarrow[dưới]{trên}` hoặc `\xrightleftharpoons[dưới]{trên}` để mũi tên co dãn theo độ dài văn bản điều kiện.
  * Phản ứng este hóa:
    $$\mathrm{CH_3COOH + C_2H_5OH \xrightleftharpoons[t^\circ]{\mathrm{H_2SO_4\ \text{đặc}}} CH_3COOC_2H_5 + H_2O}$$
  * Phản ứng nhiệt phân: `\mathrm{CaCO_3 \xrightarrow{t^\circ} CaO + CO_2\uparrow}`.
- **Kết tủa & Bay hơi**: Dùng `\downarrow` (kết tủa) và `\uparrow` (bay hơi).
- **Trạng thái chất**: Ghi rõ `(s)` rắn, `(l)` lỏng, `(g)` khí, `(aq)` dung dịch.

### 3. Nhiệt hóa học & Tốc độ phản ứng (Hóa học 10–12)
- Biến thiên Enthalpy: `\Delta_r H_{298}^\circ`, `\Delta_f H_{298}^\circ`.
- Hằng số cân bằng & pH: `K_C = \frac{[\mathrm{NH_3}]^2}{[\mathrm{N_2}][\mathrm{H_2}]^3}`, `\mathrm{pH} = -\log[\mathrm{H^+}]`.
- Pin điện & Điện cực: `\mathrm{Zn(s) \mid Zn^{2+}(aq) \parallel Cu^{2+}(aq) \mid Cu(s)}`.
- Phức chất: `[\mathrm{Cu(NH_3)_4}]^{2+}`, `[\mathrm{Ag(NH_3)_2}]^+`.

---

## 🛡️ TÓM TẮT: QUY TẮC BẤT DI BẤT DỊCH CHO AGENT KHI TẠO ĐỀ & GIẢI BÀI

1. Khi sinh công thức Toán/Lý/Hóa, **phải bọc 100% trong cặp dấu `$...$` (công thức cùng dòng) hoặc `$$...$$` (công thức đứng riêng dòng)**.
2. Kiểm tra kỹ không bỏ sót dấu đóng ngoặc `{}`.
3. Không gõ tiếng Việt không dấu trong toán (dùng `\text{...}`).
4. Gọi `scripts/docx_math_builder.py` hoặc `scripts/local_engine/docx_processor.py` để xuất MathType OLE `Equation.DSMT4` cục bộ 100% offline.
