# Bước 3 — Vẽ hình kỹ thuật 300–450 DPI & Bảng chọn công cụ (38 hàm, 80 mẫu TikZ)

> Đọc khi cần vẽ đồ thị / hình không gian / mạch điện / thí nghiệm hóa.
> *(Tài liệu tham chiếu của skill `tao-de-toan-tuong-tu` — được tách ra từ `SKILL.md` để SKILL.md gọn; nội dung quy tắc giữ nguyên.)*

---

### Bước 3: Lập trình vẽ hình kỹ thuật chuẩn xác (300 DPI) & Đậm Nét Siêu Rõ
Lưu toàn bộ hình ảnh vào thư mục `hinh_ve_<ma_de>/` với định dạng PNG độ phân giải 300 DPI:
1. Sử dụng thư viện trợ giúp: [render_math_figures.py](./scripts/render_math_figures.py).
2. **Quy chuẩn đồ thị siêu nét khi in ấn**:
   - Đường cong đồ thị vẽ đậm rõ (`color='#1A365D'` hoặc `#C53030`, `lw=2.2 - 2.4`).
   - Trục tọa độ $Ox, Oy$ có mũi tên rõ nét (`lw=1.2 - 1.5`).
   - Nhãn $x$ và $y$ in nghiêng (`fontsize=13`), **bắt buộc đặt sát đầu mũi tên trục** (không để cách xa).
   - Gốc $O$ đặt tại góc phần tư thứ III gần giao điểm. Font chữ các số tọa độ rõ ràng (`fontsize=12 - 13`).
   - Đường gióng nét đứt màu xám đen (`k--`, `lw=1.0 - 1.2`) nối từ điểm cực trị, điểm cắt tới các trục.
   - Đồ thị trên đoạn $[a; b]$: Sử dụng `CubicHermiteSpline` để khóa cứng giá trị lớn nhất $M$ và giá trị nhỏ nhất $m$, chống hiện tượng đường cong bị võng lẹm sai lệch.
3. **Quy chuẩn bảng biến thiên & hình không gian chuẩn SGK**:
   - **Bảng biến thiên (BBT)**: Ưu tiên sử dụng hàm `draw_bbt_sgk()` (hoặc `draw_full_border_bbt()`) tự động đóng khung kín 1.4pt chuẩn 100% SGK; tự động phân bố cột mốc $x$, dấu $+$ / $-$ to rõ (15-16pt), số $0$ tại điểm cực trị, phân tầng cao độ dòng $y$ (cực đại ở trên, cực tiểu ở dưới, $-\infty$ ở đáy, $+\infty$ ở đỉnh), mũi tên biến thiên vectơ 2D sắc nét có khoảng đệm chống chạm số, vạch đôi $\parallel$ song song chạy suốt hàng $y'$ và $y$ tại điểm gián đoạn / tiệm cận đứng.
   - **Hình học không gian**: Cạnh thấy nét liền (`k-`, `lw=1.8 - 2.0`), cạnh khuất nét đứt (`k--`, `lw=1.3 - 1.5`). Các đỉnh $S, A, B, C, D, O...$ dùng Times New Roman bold italic (`$S$, $A$, $B$...`).
   - **Quy chuẩn Ký hiệu Véc-tơ chuẩn SGK (Mũi tên phủ trọn chữ)**:
     * Trong **TikZ**: BẮT BUỘC dùng `\overrightarrow{AB}`, `\overrightarrow{AS}`, `\overrightarrow{BC}`, TUYỆT ĐỐI KHÔNG dùng `\vec{AB}` (vì `\vec` chỉ phủ 1 chữ cái đầu).
     * Trong **Matplotlib**: BẮT BUỘC dùng hàm `draw_vector_label(ax, x, y, 'AB')` từ `scripts/render_math_figures.py` để mũi tên véc-tơ dài bao phủ trọn vẹn toàn bộ 2 chữ cái.
   - **Quy chuẩn Độ rõ nét của Số liệu & Góc khi in (Contrast & Sharpness Protocol)**:
     * **Màu sắc số liệu**: 100% màu ĐEN TUYỀN (`color='black'` hoặc `#000000`), TUYỆT ĐỐI KHÔNG dùng màu xám mờ (`#777777`, `#888888`) hay màu tím/xanh nhạt cho số liệu độ dài (như số $8$) và số đo góc (như $60^\circ$).
     * **Kích thước & độ đậm**: Số liệu và độ dài cạnh, góc phải dùng `fontsize=12.5 - 13.5`, `fontweight='bold'`.
     * **Khung đệm trắng (White Bounding Box)**: Mọi số liệu và góc nằm gần đường nét đứt / nét liền đều BẮT BUỘC có `bbox=dict(boxstyle='square,pad=0.10', fc='white', ec='none')` (hoặc `fill=white, inner sep=1.5pt` trong TikZ) để số không bao giờ bị chìm hoặc bị nét vẽ cắt ngang.
     * **Độ phân giải xuất ảnh**: Mặc định **`450 DPI`** (hoặc `600 DPI` đối với hình in chi tiết cao).

4. **4 Quy Tắc Vàng Khớp Tuyệt Đối Giữa Hình Vẽ & Đề Bài (Visual & Mathematical Consistency Protocol)**:
   - **Quy tắc Miền xác định và 2 đầu mút đoạn kín $[a; b]$**: Khi đề bài khảo sát trên đoạn kín $[a; b]$, đồ thị **bắt buộc phải chấm dứt chính xác tại $x = a$ và $x = b$** (dùng `np.linspace(a, b, 400)`), không kéo dài vô tận sang 2 phía. Luôn đánh dấu chấm tròn nổi bật (`ko`, `ms=5.5`) tại 2 đầu mút $(a; f(a))$, $(b; f(b))$ và kẻ đường gióng nét đứt tới cả 2 trục.
   - **Quy tắc Gióng nhãn trục đối xứng (Opposite Semi-Axis Projection Rule)**:
     * Điểm có $x < 0 \implies$ nhãn tung độ gióng sang phía $x > 0$ của trục $Oy$.
     * Điểm có $x > 0 \implies$ nhãn tung độ gióng sang phía $x < 0$ của trục $Oy$.
     * Điểm có $y < 0 \implies$ nhãn hoành độ gióng lên phía $y > 0$ của trục $Ox$.
     * Điểm có $y > 0 \implies$ nhãn hoành độ gióng xuống phía $y < 0$ của trục $Ox$.
     * Nhãn trên đường gióng nét đứt hoặc tiệm cận: Bắt buộc dùng `bbox=dict(boxstyle='square,pad=0.10', fc='white', ec='none')` tạo cửa sổ trắng sạch, chống đường nét cắt ngang thân chữ số.
   - **Quy tắc Giao điểm & Tọa độ nguyên sạch**: Khi câu hỏi yêu cầu xác định "Giao điểm với trục hoành Ox" hoặc "Giao điểm với trục tung Oy", hàm số hoặc spline phải đi qua chính xác các tọa độ nguyên đó (ví dụ $(3; 0)$, $(0; 2)$). Nhãn số của giao điểm đặt lệch theo hướng ngược chiều độ dốc tiếp tuyến để đường cong không cắt qua chữ.
   - **Quy tắc Tiệm cận và Tâm đối xứng**: Tiệm cận đứng $x = x_0$ và ngang $y = y_0$ kẻ nét đứt `lw=1.2`. Giao điểm với các trục phải cách xa gốc $O$ tối thiểu $|x| \ge 1.0$ hoặc $|y| \ge 1.0$ để nhãn không va chạm với chữ $O$.

### 🎯 Bảng Chọn Công Cụ Vẽ Hình Chính Xác Theo Dạng Bài (Tool Selection Matrix — 38 Hàm & 80 Mẫu TikZ)

Agent PHẢI chọn đúng công cụ theo bảng dưới để đảm bảo độ chuẩn xác 100% về mặt toán học/vật lý và mỹ thuật vector 300 DPI:

| Dạng hình bài toán | Công cụ | Hàm Matplotlib / Mẫu TikZ | Lớp |
|-------------------|---------|---------------------------|-----|
| **Đồ thị hàm bậc 3** $y = ax^3+bx^2+cx+d$ | Matplotlib | `plot_cubic_function()` | 11–12 |
| **Đồ thị phân thức** $y = \frac{ax+b}{cx+d}$ | Matplotlib | `plot_rational_1_1()` | 11–12 |
| **Đồ thị trên đoạn kín** $[a;b]$ (Hermite Spline) | Matplotlib | `plot_bounded_interval_extrema()` | 11–12 |
| **Parabol** $y = ax^2+bx+c$ (đỉnh, trục đối xứng) | Matplotlib | `plot_parabola()` | 10 |
| **Hàm lượng giác** $y = a\sin(bx+c)+d$, cos | Matplotlib | `plot_trig_function()` (nhãn bội số $\pi$) | 10–12 |
| **Hàm mũ & log** $y = a^x$, $y = \log_a x$ | Matplotlib | `plot_exponential_log()` (trục đối xứng $y=x$) | 12 |
| **Đồ thị biến đổi** $y = |f(x)|$, $y = f(|x|)$ | Matplotlib | `plot_absolute_value_transform()` | 12 |
| **So sánh 2 hàm & Diện tích tích phân** | Matplotlib | `plot_function_comparison()` (tô màu diện tích) | 12 |
| **Định nghĩa tích phân (Tổng Riemann)** | Matplotlib | `plot_integral_riemann_sum()` (cột diện tích) | 12 |
| **Đường Elip & Hypebol** (tiêu điểm, tiệm cận) | Matplotlib | `plot_conic_section()` / TikZ `Mẫu T33` | 10–12 |
| **Trục số biểu diễn nghiệm BPT / Tập xác định** | Matplotlib | `plot_number_line_intervals()` (đầu đóng/mở) | 8–12 |
| **Biểu đồ thống kê** (cột tần số/tần suất, quạt) | Matplotlib | `plot_statistics_bar()`, `plot_pie_chart()` | 7, 10, 12 |
| **Hệ tọa độ cực** $r = f(\theta)$ (hoa 4 cánh, tim) | Matplotlib | `plot_polar_graph()` | Nâng cao |
| **Bảng biến thiên chuẩn SGK (tự động)** | Matplotlib | `draw_bbt_sgk()` (tự động 100% chuẩn SGK) / `draw_full_border_bbt()` | 11–12 |
| **Hình không gian 3D** (chóp, lăng trụ, hộp, nón, trụ, cầu) | Matplotlib / TikZ | `plot_pyramid_*()`, `plot_prism_*()`, `plot_cylinder()`, `plot_cone()`, `plot_sphere()` | 11–12 |
| **Thiết diện 3D hình chóp** | Matplotlib / TikZ | `plot_3d_cross_section_pyramid()` hoặc TikZ `Mẫu T25, T39` | 11 |
| **Hệ trục Oxyz 3D** | TikZ | `Mẫu T34` (isometric/oblique) | 12 |
| **Hình học phẳng** (Thales, Pythagore, phân giác, góc so le, đồng vị, đường tròn) | **TikZ** `tkz-euclide` | Xem `references/tikz_templates.md` (`Mẫu T01-T10, T21-T24, T29, T32, T38`) | 6–9 |
| **Dao động điều hòa** $x(t) = A\cos(\omega t + \varphi)$ | Matplotlib | `plot_harmonic_oscillation()` | 11–12 |
| **Giao thoa sóng** (2 nguồn, cùng/ngược/vuông pha) | Matplotlib | `plot_wave_superposition()` | 12 |
| **Phân rã hạt nhân** $N(t) = N_0 \cdot 2^{-t/T}$ | Matplotlib | `plot_nuclear_decay()` (chu kỳ bán rã) | 12 |
| **Động học s-t, v-t, a-t** | Matplotlib | `plot_kinematics()`, `plot_velocity_time()` | 10 |
| **Chuyển động ném xiên parabol** | Matplotlib | `plot_projectile_motion()` ($v_0, \alpha, H, L$) | 10 |
| **Đường sức điện trường** 2 điện tích điểm | Matplotlib | `plot_electric_field_lines()` (streamplot) | 11 |
| **Lực Lorentz & Từ trường** (bàn tay trái) | Matplotlib | `plot_magnetic_lorentz_force()` ($\vec{v} \perp \vec{f}$) | 11 |
| **Giản đồ vectơ Fresnel mạch RLC** | Matplotlib | `plot_fresnel_diagram()` ($\vec{U}_R, \vec{U}_L, \vec{U}_C$) | 12 |
| **Hệ vectơ Oxy & Tổng hợp lực** | Matplotlib / TikZ | `plot_2d_vectors()` / TikZ `Mẫu T11, T12` | 10 |
| **Quang học** (thấu kính, kính hiển vi, gương, lăng kính) | Matplotlib / TikZ | `plot_thin_lens_optics()` / TikZ `Mẫu V11-V14, T36` | 11 |
| **Mạch điện** (nối tiếp, song song, Wheatstone, RLC) | **TikZ** `circuitikz` | Xem `references/tikz_templates.md` (`Mẫu V05-V10, T28, T35`) | 9–12 |
| **Nhiệt động học** (p-V, p-T khí lý tưởng) | Matplotlib | `plot_ideal_gas_pV()`, `plot_ideal_gas_pT()` | 10 |
| **Nguyên tử Bohr & Quang phổ Hydro** | TikZ | `Mẫu T37` | 12 |
| **Cơ học** (ròng rọc, đòn bẩy, mặt phẳng nghiêng) | TikZ | `Mẫu V01-V04, T27` | 6–10 |
| **Hóa học** (cấu tạo chemfig, chuỗi phản ứng, điện phân) | **TikZ** `chemfig` | `Mẫu H01-H12, T30, T31` | 10–12 |
| **Giản đồ năng lượng & pH chuẩn độ Hóa** | Matplotlib | `plot_chemistry_energy_diagram()`, `plot_ph_titration_curve()` | 10–12 |

> 📖 **Thư viện mẫu TikZ**: [`references/tikz_templates.md`](./references/tikz_templates.md)
> Chứa **80 đoạn code TikZ chuẩn hóa** sẵn có, bao quát 100% chương trình từ lớp 6 đến lớp 12. Chỉ cần copy snippet và điều chỉnh tham số số liệu theo đề mới.
>
> **Quy trình gọi TikZ Engine:**
> ```python
> from scripts.tikz_renderer import render_tikz
> tikz_code = r"""
> % Copy mẫu từ tikz_templates.md và điều chỉnh tham số
> \begin{tikzpicture}
>   ...
> \end{tikzpicture}
> """
> ok = render_tikz(tikz_code, "hinh_ve.png", dpi=300, mode="standalone")
> ```
