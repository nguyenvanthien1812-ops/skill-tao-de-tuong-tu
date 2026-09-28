import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import CubicHermiteSpline
import os

plt.rcParams['font.family'] = 'Times New Roman'

w_box = dict(boxstyle='square,pad=0.12', fc='white', ec='none')

def setup_axes(ax, xlim, ylim):
    """
    Thiết lập hệ trục tọa độ Oxy chuẩn SGK Việt Nam & Đề thi Quốc Gia:
    - Trục Ox và Oy nét đậm 1.3pt
    - Đầu mũi tên nhọn đẹp: arrowstyle='-|> ', mutation_scale=12
    - Nhãn 'x' và 'y' in đậm nghiêng, đặt sát ngay đầu mũi tên
    - Gốc tọa độ 'O' thoáng đãng, không bị đè bởi đường gióng
    """
    dx = xlim[1] - xlim[0]
    dy = ylim[1] - ylim[0]
    
    # Trục Ox và Oy nét đậm rõ ràng
    ax.axhline(0, color='black', linewidth=1.3)
    ax.axvline(0, color='black', linewidth=1.3)
    
    # Mũi tên trục x & nhãn x sát đầu mũi tên
    ax.annotate('', xy=(xlim[1], 0), xytext=(xlim[1] - 0.08*dx, 0),
                arrowprops=dict(arrowstyle='-|> ', color='black', lw=1.3, mutation_scale=12))
    ax.text(xlim[1] - 0.03*dx, -0.07*dy, 'x', fontsize=13, fontweight='bold', fontstyle='italic')
    
    # Mũi tên trục y & nhãn y sát đầu mũi tên
    ax.annotate('', xy=(0, ylim[1]), xytext=(0, ylim[1] - 0.08*dy),
                arrowprops=dict(arrowstyle='-|> ', color='black', lw=1.3, mutation_scale=12))
    ax.text(0.04*dx, ylim[1] - 0.04*dy, 'y', fontsize=13, fontweight='bold', fontstyle='italic')
    
    # Gốc tọa độ O
    ax.text(-0.06*dx, -0.07*dy, 'O', fontsize=12, fontstyle='italic')
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    ax.axis('off')

def draw_point_with_projection(ax, x, y, x_label=None, y_label=None, marker='ko', ms=5.2, use_box=True):
    """
    Vẽ điểm và đường gióng nét đứt vuông góc tới 2 trục tọa độ đậm rõ:
    - Áp dụng 'Quy tắc gióng nhãn trục đối xứng' để không bao giờ bị đường nét đứt cắt ngang chữ số
    - Sử dụng white bounding box (w_box) khi cần thiết
    """
    ax.plot([x, x, 0], [0, y, y], 'k--', lw=1.1)
    ax.plot(x, y, marker, markersize=ms)
    
    # Gióng nhãn x
    if x_label is not None:
        y_pos = 0.25 if y < 0 else -0.42
        va = 'bottom' if y < 0 else 'top'
        ax.text(x, y_pos, str(x_label), fontsize=12, ha='center', va=va, fontweight='bold',
                bbox=w_box if use_box else None)
        
    # Gióng nhãn y
    if y_label is not None:
        x_pos = 0.18 if x < 0 else -0.42
        ha = 'left' if x < 0 else 'right'
        ax.text(x_pos, y, str(y_label), fontsize=12, ha=ha, va='center', fontweight='bold',
                bbox=w_box if use_box else None)

def plot_cubic_function(a, b, c, d, xlim, ylim, filename, marked_points=None):
    """Vẽ đồ thị hàm số bậc ba y = ax^3 + bx^2 + cx + d nét đậm siêu rõ (lw=2.3)"""
    fig, ax = plt.subplots(figsize=(4.2, 3.8), dpi=300)
    x = np.linspace(xlim[0]*0.96, xlim[1]*0.96, 400)
    y = a*x**3 + b*x**2 + c*x + d
    ax.plot(x, y, color='#000000', lw=2.3)
    
    if marked_points:
        for p in marked_points:
            px, py = p['x'], p['y']
            draw_point_with_projection(ax, px, py, p.get('xl'), p.get('yl'))
            
    setup_axes(ax, xlim, ylim)
    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()

def plot_rational_1_1(a, b, c, d, xlim, ylim, filename, marked_points=None):
    """Vẽ đồ thị hàm phân thức bậc 1 / bậc 1: y = (ax + b) / (cx + d) nét đậm siêu rõ"""
    fig, ax = plt.subplots(figsize=(4.3, 3.8), dpi=300)
    x_asymp = -d / c
    y_asymp = a / c
    
    # Hai nhánh đồ thị
    eps = 0.22
    x1 = np.linspace(xlim[0]*0.96, x_asymp - eps, 300)
    y1 = (a*x1 + b) / (c*x1 + d)
    ax.plot(x1, y1, color='#000000', lw=2.3)
    
    x2 = np.linspace(x_asymp + eps, xlim[1]*0.96, 300)
    y2 = (a*x2 + b) / (c*x2 + d)
    ax.plot(x2, y2, color='#000000', lw=2.3)
    
    # Tiệm cận đứng và ngang có white bbox chống đè chữ
    ax.axvline(x_asymp, color='black', linestyle='--', lw=1.2)
    ax.axhline(y_asymp, color='black', linestyle='--', lw=1.2)
    
    lbl_x = f'{x_asymp:.0f}' if float(x_asymp).is_integer() else f'{x_asymp:.1f}'
    lbl_y = f'{y_asymp:.0f}' if float(y_asymp).is_integer() else f'{y_asymp:.1f}'
    ax.text(x_asymp, -0.45, lbl_x, fontsize=12, fontweight='bold', ha='center', bbox=w_box)
    ax.text(-0.45, y_asymp, lbl_y, fontsize=12, fontweight='bold', va='center', bbox=w_box)
    
    if marked_points:
        for p in marked_points:
            px, py = p['x'], p['y']
            ax.plot(px, py, 'ko', markersize=5.2)
            if 'xl' in p:
                ax.text(px, 0.25 if py < 0 else -0.42, str(p['xl']), fontsize=12, fontweight='bold', ha='center')
            if 'yl' in p:
                ax.text(0.18 if px < 0 else -0.42, py, str(p['yl']), fontsize=12, fontweight='bold', va='center')
                
    setup_axes(ax, xlim, ylim)
    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()

def plot_bounded_interval_extrema(xs_knots, ys_knots, ds_knots, xlim, ylim, filename,
                                  endpoints=None, extrema=None):
    """
    Vẽ đồ thị hàm số chuẩn xác trên đoạn kín [a; b] có giá trị lớn nhất M và nhỏ nhất m:
    - Đường cong chỉ vẽ chính xác trong [a; b]
    - 2 đầu mút và các điểm cực trị có chấm tròn to (ms=5.5) và đường gióng nét đứt chuẩn xác
    - Nhãn tọa độ tuân thủ 100% 'Quy tắc gióng nhãn trục đối xứng'
    """
    fig, ax = plt.subplots(figsize=(4.5, 3.8), dpi=300)
    spline = CubicHermiteSpline(xs_knots, ys_knots, ds_knots)
    xs = np.linspace(xs_knots[0], xs_knots[-1], 400)
    ax.plot(xs, spline(xs), color='#1A365D', lw=2.4)

    # Vẽ các điểm mấu chốt (đầu mút + cực trị)
    all_points = (endpoints or []) + (extrema or [])
    for pt in all_points:
        px, py = pt['x'], pt['y']
        xl, yl = pt.get('xl'), pt.get('yl')
        ax.plot([px, px, 0], [0, py, py], 'k--', lw=1.1)
        ax.plot(px, py, 'ko', markersize=5.5)
        if xl is not None:
            y_pos = 0.25 if py < 0 else -0.42
            ax.text(px, y_pos, str(xl), fontsize=12, fontweight='bold', ha='center')
        if yl is not None:
            # Nhãn y đặt phía đối xứng so với vị trí điểm x để tránh cắt vào đường nét đứt
            x_pos = 0.18 if px < 0 else -0.42
            ax.text(x_pos, py, str(yl), fontsize=12, fontweight='bold', va='center', bbox=w_box)

    setup_axes(ax, xlim, ylim)
    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()


# ─── MÔN VẬT LÝ (LỚP 6 - 12) ─────────────────────────────────────────────────

def plot_harmonic_oscillation(A, T, phi, t_max, filename, x_label='t (s)', y_label='x (cm)'):
    """
    Vẽ đồ thị dao động điều hòa li độ - thời gian: x(t) = A * cos(omega * t + phi)
    Chuẩn SGK Vật lý 11 & 12
    """
    fig, ax = plt.subplots(figsize=(6.2, 3.2), dpi=300)
    omega = 2 * np.pi / T
    t = np.linspace(0, t_max, 500)
    x = A * np.cos(omega * t + phi)

    ax.axhline(0, color='black', lw=0.9)
    ax.axvline(0, color='black', lw=0.9)

    ax.grid(True, linestyle=':', alpha=0.55, color='gray')
    ax.plot(t, x, color='#C0392B', lw=1.8)

    ax.annotate('', xy=(t_max * 1.03, 0), xytext=(t_max * 0.96, 0),
                arrowprops=dict(arrowstyle='->', color='black', lw=1))
    ax.text(t_max * 0.98, -0.18 * A, x_label, fontsize=10, fontstyle='italic')

    ax.annotate('', xy=(0, A * 1.22), xytext=(0, A * 1.1),
                arrowprops=dict(arrowstyle='->', color='black', lw=1))
    ax.text(-0.06 * t_max, A * 1.15, y_label, fontsize=10, fontstyle='italic')
    ax.text(-0.03 * t_max, -0.15 * A, 'O', fontsize=9, fontstyle='italic')

    ax.set_xlim(-0.05 * t_max, t_max * 1.05)
    ax.set_ylim(-A * 1.3, A * 1.3)
    for sp in ['top', 'right', 'left', 'bottom']:
        ax.spines[sp].set_visible(False)

    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()


def plot_thin_lens_optics(f, d, h, filename, lens_type='convex'):
    """
    Vẽ đường truyền tia sáng & dựng ảnh qua thấu kính mỏng:
    - lens_type: 'convex' (hội tụ) hoặc 'concave' (phân kỳ)
    - f: tiêu cự
    - d: khoảng cách vật
    - h: chiều cao vật sáng AB
    """
    fig, ax = plt.subplots(figsize=(7.2, 3.5), dpi=300)
    ax.axhline(0, color='black', lw=1.0)

    f_val = abs(f) if lens_type == 'convex' else -abs(f)
    d_prime = (d * f_val) / (d - f_val) if d != f_val else 100
    h_prime = - (d_prime / d) * h

    h_lens = max(abs(h), abs(h_prime), 2.5) * 1.3
    ax.plot([0, 0], [-h_lens, h_lens], color='#1A365D', lw=1.8)
    if lens_type == 'convex':
        ax.annotate('', xy=(0, h_lens+0.2), xytext=(0, h_lens-0.2), arrowprops=dict(arrowstyle='->', color='#1A365D', lw=1.5))
        ax.annotate('', xy=(0, -h_lens-0.2), xytext=(0, -h_lens+0.2), arrowprops=dict(arrowstyle='->', color='#1A365D', lw=1.5))
    else:
        ax.annotate('', xy=(0, h_lens-0.2), xytext=(0, h_lens+0.2), arrowprops=dict(arrowstyle='->', color='#1A365D', lw=1.5))
        ax.annotate('', xy=(0, -h_lens+0.2), xytext=(0, -h_lens-0.2), arrowprops=dict(arrowstyle='->', color='#1A365D', lw=1.5))

    abs_f = abs(f)
    ax.plot([-abs_f, abs_f, 0], [0, 0, 0], 'ko', markersize=3.5)
    ax.text(-abs_f, -0.38, 'F', fontsize=11, ha='center', fontstyle='italic')
    ax.text(abs_f, -0.38, "F'", fontsize=11, ha='center', fontstyle='italic')
    ax.text(-0.25, -0.38, 'O', fontsize=11, ha='center', fontstyle='italic')

    # Vật sáng AB
    ax.annotate('', xy=(-d, h), xytext=(-d, 0), arrowprops=dict(arrowstyle='->', color='#0D47A1', lw=2.2))
    ax.text(-d, -0.38, 'A', fontsize=11, ha='center', fontweight='bold')
    ax.text(-d, h + 0.2, 'B', fontsize=11, ha='center', fontweight='bold')

    # Ảnh A'B'
    is_real = d_prime > 0
    img_color = '#B71C1C' if is_real else '#7B1FA2'
    ax.annotate('', xy=(d_prime, h_prime), xytext=(d_prime, 0),
                arrowprops=dict(arrowstyle='->', color=img_color, lw=2.2,
                                linestyle='solid' if is_real else 'dashed'))
    ax.text(d_prime, 0.2 if h_prime < 0 else -0.38, "A'", fontsize=11, ha='center', fontweight='bold')
    ax.text(d_prime, h_prime + (0.2 if h_prime > 0 else -0.4), "B'", fontsize=11, ha='center', fontweight='bold')

    # Tia sáng 1
    ax.plot([-d, 0], [h, h], color='#E65100', lw=1.3)
    ax.annotate('', xy=(-d/2, h), xytext=(-d/2 - 0.2, h), arrowprops=dict(arrowstyle='->', color='#E65100', lw=1.3))
    if lens_type == 'convex':
        ax.plot([0, d_prime], [h, h_prime], color='#E65100', lw=1.3)
    
    # Tia sáng 2
    ax.plot([-d, d_prime], [h, h_prime], color='#2E7D32', lw=1.3)

    ax.axis('off')
    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()


def draw_full_border_bbt(x_labels, yprime_data, y_data, arrows, filename, W=10.0, H=4.2):
    """
    Vẽ Bảng biến thiên (BBT) đóng khung full viền 100% chuẩn SGK & đề quốc gia (300 DPI)
    - x_labels: list of tuples (x_pos, text)
    - yprime_data: list of tuples (x_pos, text)
    - y_data: list of tuples (x_pos, y_pos, text)
    - arrows: list of tuples (start_x, start_y, end_x, end_y)
    """
    fig, ax = plt.subplots(figsize=(6.2, 2.5), dpi=300)
    ax.set_xlim(0, W)
    ax.set_ylim(0, H)
    ax.axis('off')

    # Khung viền chữ nhật bao quanh toàn bộ bảng
    ax.plot([0, W, W, 0, 0], [0, 0, H, H, 0], 'k-', lw=1.4)
    # Đường kẻ ngang dưới dòng x
    ax.plot([0, W], [3.1, 3.1], 'k-', lw=1.2)
    # Đường kẻ ngang dưới dòng y'
    ax.plot([0, W], [2.1, 2.1], 'k-', lw=1.2)
    # Đường kẻ dọc ngăn cột tiêu đề
    col_w = 1.4
    ax.plot([col_w, col_w], [0, H], 'k-', lw=1.2)

    # Tiêu đề hàng
    ax.text(col_w/2, 3.65, 'x', fontsize=13, fontweight='bold', fontstyle='italic', ha='center', va='center')
    ax.text(col_w/2, 2.6, "y '", fontsize=13, fontweight='bold', fontstyle='italic', ha='center', va='center')
    ax.text(col_w/2, 1.05, 'y', fontsize=13, fontweight='bold', fontstyle='italic', ha='center', va='center')

    for xp, text in x_labels:
        ax.text(xp, 3.65, text, fontsize=12 if '∞' in text else 13, fontweight='bold', ha='center', va='center')

    for xp, text in yprime_data:
        ax.text(xp, 2.6, text, fontsize=14 if text in ('+', '-') else 13, fontweight='bold', ha='center', va='center')

    for xp, yp, text in y_data:
        ax.text(xp, yp, text, fontsize=12 if '∞' in text else 13, fontweight='bold', ha='center', va='center')

    arrow_style = dict(arrowstyle='-|> ', color='black', lw=1.3, mutation_scale=10)
    for sx, sy, ex, ey in arrows:
        ax.annotate('', xy=(ex, ey), xytext=(sx, sy), arrowprops=arrow_style)

    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()


# ─── MÔN HÓA HỌC (LỚP 10 - 12 & KHTN) ────────────────────────────────────────

def plot_chemistry_energy_diagram(reactants_lbl, products_lbl, delta_h_val, ea_val, filename, is_exothermic=True):
    """
    Vẽ giản đồ năng lượng phản ứng hóa học (Enthalpy profile diagram):
    - Phản ứng tỏa nhiệt (is_exothermic=True): delta_h < 0
    - Phản ứng thu nhiệt (is_exothermic=False): delta_h > 0
    - Năng lượng hoạt hóa Ea và biến thiên enthalpy Delta_r H chuẩn 300 DPI
    """
    fig, ax = plt.subplots(figsize=(5.5, 3.8), dpi=300)
    
    # Trục tọa độ
    ax.annotate('', xy=(0, 5.2), xytext=(0, 0), arrowprops=dict(arrowstyle='-|> ', color='black', lw=1.3))
    ax.annotate('', xy=(5.2, 0), xytext=(0, 0), arrowprops=dict(arrowstyle='-|> ', color='black', lw=1.3))
    ax.text(0.08, 5.0, 'Năng lượng E (kJ)', fontsize=11, fontweight='bold')
    ax.text(3.5, -0.4, 'Tiến trình phản ứng', fontsize=11, fontweight='bold')
    
    # Mức năng lượng chất phản ứng và sản phẩm
    if is_exothermic:
        e_reac = 2.2
        e_prod = 1.0
        e_trans = e_reac + 2.0
    else:
        e_reac = 1.2
        e_prod = 2.6
        e_trans = e_prod + 1.8

    # Đường cong phản ứng (spline mượt)
    x_pts = [0.8, 1.4, 2.5, 3.6, 4.4]
    y_pts = [e_reac, e_reac, e_trans, e_prod, e_prod]
    from scipy.interpolate import pchip
    pch = pchip(x_pts, y_pts)
    xs = np.linspace(0.8, 4.4, 300)
    ax.plot(xs, pch(xs), color='#C53030', lw=2.2)
    
    # Vạch mức năng lượng ngang
    ax.hlines(e_reac, 0.4, 1.6, colors='black', linestyles='--', lw=1.0)
    ax.hlines(e_prod, 3.4, 4.8, colors='black', linestyles='--', lw=1.0)
    ax.hlines(e_trans, 1.8, 3.2, colors='gray', linestyles=':', lw=0.9)
    
    ax.text(1.1, e_reac + 0.15, reactants_lbl, fontsize=12, fontweight='bold', ha='center')
    ax.text(4.0, e_prod + 0.15, products_lbl, fontsize=12, fontweight='bold', ha='center')
    
    # Mũi tên Ea
    ax.annotate('', xy=(2.0, e_trans), xytext=(2.0, e_reac),
                arrowprops=dict(arrowstyle='<->', color='#1A365D', lw=1.2))
    ax.text(2.1, (e_trans + e_reac)/2, f'Ea = {ea_val} kJ', fontsize=10, fontweight='bold', color='#1A365D', va='center')
    
    # Mũi tên Delta H
    x_dh = 3.6
    ax.annotate('', xy=(x_dh, e_prod), xytext=(x_dh, e_reac),
                arrowprops=dict(arrowstyle='<->', color='#2B6CB0', lw=1.2))
    dh_text = f'Δr H = {delta_h_val} kJ'
    ax.text(x_dh + 0.1, (e_reac + e_prod)/2, dh_text, fontsize=10, fontweight='bold', color='#2B6CB0', va='center')

    ax.set_xlim(-0.2, 5.4)
    ax.set_ylim(-0.6, 5.5)
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()


def plot_ph_titration_curve(v_eq, ph_init, ph_eq, ph_end, filename, title="Đường cong chuẩn độ pH"):
    """
    Vẽ đồ thị chuẩn độ axit - bazơ (pH titration curve) chuẩn SGK Hóa học 11
    """
    fig, ax = plt.subplots(figsize=(5.5, 3.8), dpi=300)
    
    # Hệ trục tọa độ
    ax.axhline(0, color='black', lw=1.2)
    ax.axvline(0, color='black', lw=1.2)
    ax.annotate('', xy=(v_eq * 2.1, 0), xytext=(v_eq * 2.0, 0), arrowprops=dict(arrowstyle='-|> ', color='black', lw=1.2))
    ax.annotate('', xy=(0, 14.8), xytext=(0, 14.0), arrowprops=dict(arrowstyle='-|> ', color='black', lw=1.2))
    
    ax.text(v_eq * 1.9, -1.2, 'V (mL)', fontsize=11, fontweight='bold', fontstyle='italic')
    ax.text(-v_eq * 0.15, 14.3, 'pH', fontsize=11, fontweight='bold', fontstyle='italic')
    
    # Hàm sigmoid mô phỏng bước nhảy pH
    vs = np.linspace(0, v_eq * 2.0, 400)
    k = 1.8 / (v_eq * 0.08)
    phs = ph_init + (ph_end - ph_init) / (1 + np.exp(-k * (vs - v_eq)))
    ax.plot(vs, phs, color='#2B6CB0', lw=2.2)
    
    # Điểm tương đương
    ax.plot([v_eq, v_eq, 0], [0, ph_eq, ph_eq], 'k--', lw=1.1)
    ax.plot(v_eq, ph_eq, 'ko', markersize=5.2)
    ax.text(v_eq, -1.1, f'{v_eq:.0f}', fontsize=11, fontweight='bold', ha='center')
    ax.text(-v_eq * 0.08, ph_eq, f'{ph_eq:.1f}', fontsize=11, fontweight='bold', va='center', ha='right')
    ax.text(v_eq + 0.1*v_eq, ph_eq - 0.6, 'Điểm tương đương', fontsize=9, fontstyle='italic', color='#742A2A')
    
    ax.set_xlim(-v_eq * 0.15, v_eq * 2.15)
    ax.set_ylim(-1.5, 15.0)
    ax.grid(True, linestyle=':', alpha=0.45)
    for sp in ['top', 'right']:
        ax.spines[sp].set_visible(False)
        
    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()


# ─── HÌNH HỌC KHÔNG GIAN 3D (MÔN TOÁN) ───────────────────────────────────────

def plot_pyramid_s_abcd(filename, h_ratio=1.6):
    """
    Vẽ hình chóp S.ABCD đáy hình bình hành / chữ nhật chuẩn mực sư phạm:
    - Cạnh thấy vẽ nét liền (lw=1.8), cạnh khuất vẽ nét đứt (lw=1.4)
    - Các đỉnh S, A, B, C, D được định vị cân đối, chống đè chữ
    """
    fig, ax = plt.subplots(figsize=(4.5, 4.0), dpi=300)
    
    # Tọa độ các đỉnh đáy
    A = np.array([1.2, 1.2])
    B = np.array([0.4, 0.4])
    C = np.array([3.4, 0.4])
    D = np.array([4.2, 1.2])
    
    # Đỉnh S
    S = np.array([1.2, 1.2 + h_ratio * 1.8])
    
    # Cạnh khuất (nét đứt)
    ax.plot([A[0], D[0]], [A[1], D[1]], 'k--', lw=1.4)
    ax.plot([A[0], B[0]], [A[1], B[1]], 'k--', lw=1.4)
    ax.plot([S[0], A[0]], [S[1], A[1]], 'k--', lw=1.4)
    
    # Cạnh thấy (nét liền)
    ax.plot([B[0], C[0]], [B[1], C[1]], 'k-', lw=1.8)
    ax.plot([C[0], D[0]], [C[1], D[1]], 'k-', lw=1.8)
    ax.plot([S[0], B[0]], [S[1], B[1]], 'k-', lw=1.8)
    ax.plot([S[0], C[0]], [S[1], C[1]], 'k-', lw=1.8)
    ax.plot([S[0], D[0]], [S[1], D[1]], 'k-', lw=1.8)
    
    # Chấm các đỉnh
    pts = [('S', S, 'above'), ('A', A, 'top-left'), ('B', B, 'below-left'),
           ('C', C, 'below-right'), ('D', D, 'right')]
    for name, p, pos in pts:
        ax.plot(p[0], p[1], 'ko', markersize=3.8)
        if pos == 'above':
            ax.text(p[0], p[1] + 0.12, name, fontsize=12, fontweight='bold', ha='center')
        elif pos == 'top-left':
            ax.text(p[0] - 0.22, p[1] + 0.08, name, fontsize=12, fontweight='bold', ha='right')
        elif pos == 'below-left':
            ax.text(p[0] - 0.18, p[1] - 0.18, name, fontsize=12, fontweight='bold', ha='right')
        elif pos == 'below-right':
            ax.text(p[0] + 0.12, p[1] - 0.18, name, fontsize=12, fontweight='bold', ha='left')
        elif pos == 'right':
            ax.text(p[0] + 0.18, p[1] + 0.05, name, fontsize=12, fontweight='bold', ha='left')

    ax.set_xlim(-0.2, 4.8)
    ax.set_ylim(-0.2, 4.6)
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()



