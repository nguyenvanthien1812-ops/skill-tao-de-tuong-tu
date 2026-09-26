import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import CubicHermiteSpline
import os

plt.rcParams['font.family'] = 'Times New Roman'

def setup_axes(ax, xlim, ylim):
    """Thiết lập hệ trục tọa độ Oxy chuẩn SGK Việt Nam: Nét đậm, x và y sát mũi tên"""
    dx = xlim[1] - xlim[0]
    dy = ylim[1] - ylim[0]
    
    # Trục Ox và Oy nét đậm rõ ràng
    ax.axhline(0, color='black', linewidth=1.2)
    ax.axvline(0, color='black', linewidth=1.2)
    
    # Mũi tên trục x
    ax.annotate('', xy=(xlim[1], 0), xytext=(xlim[1] - 0.09*dx, 0),
                arrowprops=dict(arrowstyle='->', color='black', lw=1.3))
    # Nhãn x in nghiêng đặt sát đầu mũi tên
    ax.text(xlim[1] - 0.03*dx, -0.07*dy, 'x', fontsize=13, fontstyle='italic', ha='center', va='top')
    
    # Mũi tên trục y
    ax.annotate('', xy=(0, ylim[1]), xytext=(0, ylim[1] - 0.09*dy),
                arrowprops=dict(arrowstyle='->', color='black', lw=1.3))
    # Nhãn y in nghiêng đặt sát đầu mũi tên
    ax.text(-0.06*dx, ylim[1] - 0.03*dy, 'y', fontsize=13, fontstyle='italic', ha='right', va='center')
    
    # Gốc tọa độ O
    ax.text(-0.05*dx, -0.06*dy, 'O', fontsize=12, fontstyle='italic')
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    ax.axis('off')

def draw_point_with_projection(ax, x, y, x_label=None, y_label=None, marker='ko', ms=4.5):
    """Vẽ điểm và đường gióng nét đứt vuông góc tới 2 trục tọa độ đậm rõ"""
    ax.plot([x, x, 0], [0, y, y], 'k--', lw=1.1, alpha=0.85)
    ax.plot(x, y, marker, markersize=ms)
    if x_label is not None:
        ax.text(x, -0.4, str(x_label), fontsize=11, ha='center', fontweight='bold')
    if y_label is not None:
        ax.text(0.15, y, str(y_label), fontsize=11, va='center', fontweight='bold')

def plot_cubic_function(a, b, c, d, xlim, ylim, filename, marked_points=None):
    """Vẽ đồ thị hàm số bậc ba y = ax^3 + bx^2 + cx + d nét đậm siêu rõ"""
    fig, ax = plt.subplots(figsize=(4.0, 3.8), dpi=300)
    x = np.linspace(xlim[0]*0.95, xlim[1]*0.95, 400)
    y = a*x**3 + b*x**2 + c*x + d
    ax.plot(x, y, color='#1A365D', lw=2.3)
    
    if marked_points:
        for p in marked_points:
            px, py = p['x'], p['y']
            draw_point_with_projection(ax, px, py, p.get('xl'), p.get('yl'))
            
    setup_axes(ax, xlim, ylim)
    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()

def plot_rational_1_1(a, b, c, d, xlim, ylim, filename, marked_points=None):
    """Vẽ đồ thị hàm phân thức bậc 1 / bậc 1: y = (ax + b) / (cx + d)"""
    fig, ax = plt.subplots(figsize=(4.0, 3.8), dpi=300)
    x_asymp = -d / c
    y_asymp = a / c
    
    # Hai nhánh
    eps = 0.2
    x1 = np.linspace(xlim[0], x_asymp - eps, 300)
    y1 = (a*x1 + b) / (c*x1 + d)
    ax.plot(x1, y1, color='#1A365D', lw=1.6)
    
    x2 = np.linspace(x_asymp + eps, xlim[1], 300)
    y2 = (a*x2 + b) / (c*x2 + d)
    ax.plot(x2, y2, color='#1A365D', lw=1.6)
    
    # Tiệm cận đứng và ngang
    ax.axvline(x_asymp, color='gray', linestyle='--', lw=1)
    ax.axhline(y_asymp, color='gray', linestyle='--', lw=1)
    ax.text(x_asymp + 0.1, ylim[0] + 0.5, f'{x_asymp:.0f}' if x_asymp.is_integer() else f'{x_asymp:.1f}', fontsize=9)
    ax.text(0.12, y_asymp + 0.1, f'{y_asymp:.0f}' if y_asymp.is_integer() else f'{y_asymp:.1f}', fontsize=9)
    
    if marked_points:
        for p in marked_points:
            px, py = p['x'], p['y']
            ax.plot(px, py, 'ko', markersize=3.5)
            if 'xl' in p:
                ax.text(px - 0.2, 0.25, str(p['xl']), fontsize=9)
            if 'yl' in p:
                ax.text(0.12, py - 0.2, str(p['yl']), fontsize=9)
                
    setup_axes(ax, xlim, ylim)
    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()

def plot_bounded_spline(x_knots, y_knots, d_knots, xlim, ylim, filename, annotations=None):
    """Vẽ đường cong chuẩn xác trên đoạn kín [a; b] có cực trị xác định (dùng Hermite Spline)"""
    fig, ax = plt.subplots(figsize=(4.2, 3.5), dpi=300)
    spline = CubicHermiteSpline(x_knots, y_knots, d_knots)
    xs = np.linspace(x_knots[0], x_knots[-1], 400)
    ys = spline(xs)
    ax.plot(xs, ys, color='#C53030', lw=1.8)
    
    if annotations:
        for item in annotations:
            draw_point_with_projection(ax, item['x'], item['y'], item.get('xl'), item.get('yl'))
            
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


