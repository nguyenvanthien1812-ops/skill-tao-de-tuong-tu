import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import CubicHermiteSpline
import os
import sys

try:
    from .tikz_renderer import render_tikz, is_latex_available
except ImportError:
    try:
        from tikz_renderer import render_tikz, is_latex_available
    except ImportError:
        render_tikz = None
        is_latex_available = lambda: False

# ─── LỚP A: HARD-LOCK LICENSE (chạy ngay khi import module) ─────────────────
def _check_license_on_import():
    try:
        _scripts_dir = os.path.dirname(os.path.abspath(__file__))
        if _scripts_dir not in sys.path:
            sys.path.insert(0, _scripts_dir)
        from license_manager import check_current_license
        ok, payload, err = check_current_license()
        if not ok:
            raise PermissionError(
                "\n╔══════════════════════════════════════════════════════════╗\n"
                "║     ⛔  SKILL CHƯA ĐƯỢC KÍCH HOẠT BẢN QUYỀN!           ║\n"
                "╠══════════════════════════════════════════════════════════╣\n"
                f"║  Lý do: {err[:50]:<50} ║\n"
                "╠══════════════════════════════════════════════════════════╣\n"
                "║  Chạy KICH_HOAT_BAN_QUYEN.bat để kích hoạt license.    ║\n"
                "╚══════════════════════════════════════════════════════════╝"
            )
    except Exception as e:
        if isinstance(e, PermissionError):
            raise e
        raise PermissionError(
            f"\n╔══════════════════════════════════════════════════════════╗\n"
            f"║     ⛔  SKILL CHƯA ĐƯỢC KÍCH HOẠT BẢN QUYỀN!           ║\n"
            f"╠══════════════════════════════════════════════════════════╣\n"
            f"║  Lý do: Lỗi xác minh license ({str(e)[:30]})           ║\n"
            f"╠══════════════════════════════════════════════════════════╣\n"
            f"║  Chạy KICH_HOAT_BAN_QUYEN.bat để kích hoạt license.    ║\n"
            f"╚══════════════════════════════════════════════════════════╝"
        )
_check_license_on_import()
# ─────────────────────────────────────────────────────────────────────────────


DEFAULT_DPI = 450

def apply_sgk_style():
    """Thiết lập cấu hình font Times New Roman + STIX Math chuẩn SGK & 450 DPI in ấn siêu nét"""
    plt.rcParams.update({
        'font.family': 'serif',
        'font.serif': ['Times New Roman', 'DejaVu Serif'],
        'mathtext.fontset': 'stix',
        'mathtext.rm': 'Times New Roman',
        'mathtext.it': 'Times New Roman:italic',
        'mathtext.bf': 'Times New Roman:bold',
        'lines.antialiased': True,
        'patch.antialiased': True,
        'text.antialiased': True,
        'figure.dpi': DEFAULT_DPI,
        'savefig.dpi': DEFAULT_DPI,
        'savefig.bbox': 'tight',
        'savefig.pad_inches': 0.03,
        'savefig.facecolor': 'white',
        'savefig.transparent': False,
        # Chong mo khi in: tang do sac net (sharpness) va anti-aliasing cho net ve
        'agg.path.chunksize': 0,          # 0 = chia nho tu dong (chong artifact)
        'path.simplify': False,            # Tat simplify de giu nen tron ven
        'path.simplify_threshold': 0.0,    # Giu tat ca diem Bezier
        'lines.solid_capstyle': 'round',   # Dau net ve tron, khong bi gay
        'lines.dash_capstyle': 'round',    # Dau net dut tron
        'lines.solid_joinstyle': 'round',  # Goc liet tron (chong rang cua)
        'pdf.fonttype': 42,                # Font TrueType trong PDF (in net hon Type 3)
        'ps.fonttype': 42,                 # Font TrueType trong PS
    })

apply_sgk_style()

def to_math_label(val, italic=False):
    """
    Chuẩn hóa nhãn (số, dấu, chữ cái đỉnh) sang TeX STIX chuẩn SGK Việt Nam:
    - Ký hiệu vô cực: '-inf' -> r'$-\\infty$', '+inf' -> r'$+\\infty$'
    - Dấu trong BBT: '+' -> r'$\\mathbf{+}$', '-' -> r'$\\mathbf{-}$' (dấu trừ toán học U+2212)
    - Số âm/dương: -1 -> r'$-1$', 2 -> r'$2$', 0 -> r'$0$'
    - Tên đỉnh hình học: 'A' -> r'$A$', 'S' -> r'$S$', "A'" -> r"$A'$"
    """
    if val is None:
        return ""
    txt = str(val).strip()
    if txt in ('-inf', '-oo', r'-\infty'):
        return r'$-\infty$'
    if txt in ('+inf', '+oo', 'inf', r'+\infty'):
        return r'$+\infty$'
    if txt == '+':
        return r'$\mathbf{+}$'
    if txt == '-':
        return r'$\mathbf{-}$'
    if txt.startswith('$') and txt.endswith('$'):
        return txt
    # Ký hiệu chứa dấu phẩy đạo hàm hoặc đỉnh có phẩy (A', B', y', f'(x), y'')
    if "'" in txt or r'\prime' in txt:
        clean = txt.replace('$', '')
        return rf'$\boldsymbol{{{clean}}}$'
    # Tên đỉnh hình học (S, A, B, C, D, B1...)
    if italic or (len(txt) <= 3 and txt[0].isalpha() and (len(txt) == 1 or txt[1] in ('1', '2', '3', '0'))):
        return f'${txt}$'
    # Số nguyên hoặc số thực (kể cả số âm)
    try:
        float(txt)
        return f'${txt}$'
    except ValueError:
        pass
    return txt

w_box = dict(boxstyle='square,pad=0.10', fc='white', ec='none')

def setup_axes(ax, xlim, ylim):
    """
    Thiết lập hệ trục tọa độ Oxy chuẩn SGK Việt Nam & Đề thi Quốc Gia:
    - Trục Ox và Oy nét đậm 1.3pt
    - Đầu mũi tên nhọn đặc: arrowstyle='-|>', mutation_scale=12
    - Nhãn '$x$' và '$y$' in nghiêng đậm bằng font STIX đồng bộ Times New Roman, đặt sát đầu mũi tên
    - Gốc tọa độ '$O$' đặt tại góc phần tư thứ III
    - Nền trắng 100%, không vẽ ticks li ti (chuẩn SGK Việt Nam)
    """
    dx = xlim[1] - xlim[0]
    dy = ylim[1] - ylim[0]
    
    # Trục Ox và Oy nét đậm 1.3pt
    ax.axhline(0, color='black', linewidth=1.3)
    ax.axvline(0, color='black', linewidth=1.3)
    
    # Mũi tên trục x & nhãn x sát đầu mũi tên
    arrow_axis = dict(arrowstyle='-|>', color='black', lw=1.3, mutation_scale=12)
    ax.annotate('', xy=(xlim[1], 0), xytext=(xlim[1] - 0.08*dx, 0), arrowprops=arrow_axis)
    ax.text(xlim[1] - 0.03*dx, -0.08*dy, r'$x$', fontsize=13, fontweight='bold', fontstyle='italic')
    
    # Mũi tên trục y & nhãn y sát đầu mũi tên
    ax.annotate('', xy=(0, ylim[1]), xytext=(0, ylim[1] - 0.08*dy), arrowprops=arrow_axis)
    ax.text(0.05*dx, ylim[1] - 0.05*dy, r'$y$', fontsize=13, fontweight='bold', fontstyle='italic')
    
    # Gốc tọa độ O (góc phần tư thứ III)
    ax.text(-0.07*dx, -0.08*dy, r'$O$', fontsize=12.5, fontweight='bold', fontstyle='italic')
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    ax.axis('off')

def draw_vector_label(ax, x, y, letters, fontsize=13.5, color='black', fontweight='bold', ha='center', va='center', bbox=None):
    """
    Ve nhan vec-to chuan SGK v2.1 - 3 tang fallback do bbox, mui ten phu tron chu cai.
    Sua loi: mui ten cam, qua ngan, khong hien khi backend Agg headless.
    mutation_scale=10px (pixel) doc lap don vi data -> on dinh 300-450 DPI.
    """
    clean_txt = str(letters).replace('$', '').replace('\\vec{', '').replace('}', '').strip()

    # Neu la 1 ky tu don (u, v, a...): dung \vec binh thuong
    if len(clean_txt) <= 1 or clean_txt.startswith('\\'):
        return ax.text(x, y, f'$\\vec{{{clean_txt}}}$', fontsize=fontsize, fontweight=fontweight,
                       color=color, ha=ha, va=va, bbox=bbox)

    # Ve chu cai truoc (2+ ky tu: AB, BC, AS, AD...)
    t = ax.text(x, y, f'${clean_txt}$', fontsize=fontsize, fontweight=fontweight,
                color=color, ha=ha, va=va, bbox=bbox)

    # ---- Do bbox qua 3 tang fallback -----------------------------------
    bbox_data = None
    fig = ax.get_figure()

    # Tang 1: get_renderer() - hoat dong voi hau het backend
    try:
        fig.canvas.draw()
        renderer = fig.canvas.get_renderer()
        bb = t.get_window_extent(renderer=renderer)
        inv = ax.transData.inverted()
        p0 = inv.transform((bb.x0, bb.y0))
        p1 = inv.transform((bb.x1, bb.y1))
        if abs(p1[0] - p0[0]) > 1e-9:
            bbox_data = (p0, p1)
    except Exception:
        pass

    # Tang 2: canvas.renderer (thuoc tinh thay the - Agg headless)
    if bbox_data is None:
        try:
            renderer2 = fig.canvas.renderer
            bb2 = t.get_window_extent(renderer=renderer2)
            inv2 = ax.transData.inverted()
            p0 = inv2.transform((bb2.x0, bb2.y0))
            p1 = inv2.transform((bb2.x1, bb2.y1))
            if abs(p1[0] - p0[0]) > 1e-9:
                bbox_data = (p0, p1)
        except Exception:
            pass

    # Tang 3: uoc luong hinh hoc theo fontsize + xlim (luon thanh cong)
    if bbox_data is None:
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        dx_data = abs(xlim[1] - xlim[0])
        dy_data = abs(ylim[1] - ylim[0])
        n_chars = max(len(clean_txt), 1)
        char_w = 0.022 * dx_data * (fontsize / 13.0)
        char_h = 0.045 * dy_data * (fontsize / 13.0)
        half_w = n_chars * char_w / 2.0
        p0 = np.array([x - half_w, y])
        p1 = np.array([x + half_w, y + char_h])
        bbox_data = (p0, p1)

    # ---- Ve mui ten phu tron chu cai -----------------------------------
    p0, p1 = bbox_data
    w = p1[0] - p0[0]
    h = abs(p1[1] - p0[1])

    # Nang mui ten 0.22*h phia tren dinh chu (khong bao gio dinh net)
    arrow_y = p1[1] + 0.22 * h
    # Keo dai 6% moi ben de phu vuot qua 2 chu cai bien
    x_start = p0[0] - 0.06 * w
    x_end   = p1[0] + 0.06 * w

    # mutation_scale=10px (pixel, doc lap don vi data) -> on dinh 300-450 DPI
    ax.annotate(
        '',
        xy=(x_end, arrow_y),
        xytext=(x_start, arrow_y),
        arrowprops=dict(
            arrowstyle='->,head_width=0.20,head_length=0.22',
            color=color,
            lw=1.4,
            mutation_scale=10,
            shrinkA=0,
            shrinkB=0,
        ),
        annotation_clip=False,
    )
    return t

# ─── KY HIEU DAO HAM & TICH PHAN CHUAN SGK (v2.1 – Ro net khi in A4) ─────

def fmt_derivative(expr, order=1):
    """
    Dinh dang ky hieu dao ham chuan SGK, to dam ro rang khi in.
    - order=1: y' hoac f'(x) -> dung \\boldsymbol{y'} size 15.5pt
    - order=2: y'' hoac f''(x) -> \\boldsymbol{y''}
    Dau phay dao ham to, dam, KHONG bi manh nhu soi chi.
    """
    primes = "'" * order
    clean = str(expr).replace('$', '').strip()
    return rf'$\boldsymbol{{{clean}{primes}}}$'


def fmt_integral(lower='a', upper='b', integrand='f(x)', differential='x'):
    """
    Dinh dang ky hieu tich phan chuan SGK ro net khi in A4.
    Su dung \\displaystyle de tich phan luon hien to, khong bi thu nho.
    Vi du: fmt_integral('0','1','x^2','x') -> $\\displaystyle\\int_0^1 x^2\\,dx$
    """
    return rf'$\displaystyle\int_{{{lower}}}^{{{upper}}} {integrand}\,d{differential}$'


def fmt_angle(vertex, ray1=None, ray2=None):
    """
    Dinh dang ky hieu goc chuan SGK (dung \\widehat de phủ tron 3 dinh).
    - fmt_angle('B','A','C') -> $\\widehat{BAC}$ (goc BAC)
    - fmt_angle('A')        -> $\\widehat{A}$ (goc dinh A don gian)
    """
    if ray1 and ray2:
        return rf'$\widehat{{{ray1}{vertex}{ray2}}}$'
    return rf'$\widehat{{{vertex}}}$'


def add_angle_label(ax, x, y, vertex, ray1=None, ray2=None,
                    fontsize=13, color='black', fontweight='bold',
                    ha='center', va='center'):
    """
    Ve nhan goc tai vi tri (x, y) su dung ky hieu widehat chuan SGK.
    Dung thay cho ax.text(x, y, r'$\hat{A}$') vi hat{A} qua ngan.
    """
    label = fmt_angle(vertex, ray1, ray2)
    return ax.text(x, y, label, fontsize=fontsize, fontweight=fontweight,
                   color=color, ha=ha, va=va,
                   bbox=dict(boxstyle='square,pad=0.08', fc='white', ec='none'))


def add_degree_label(ax, x, y, value, fontsize=12.5, color='black', ha='center', va='center'):
    """
    Ve so do goc (vi du: 60 do) voi ky hieu do trong ro, dam, den tuyen.
    Dung thay cho ax.text voi color='gray' vi xam mo khi in.
    Vi du: add_degree_label(ax, 1.5, 0.5, 60) -> hien thi '60^{\circ}' ro net.
    """
    label = rf'$\mathbf{{{value}}}^{{\circ}}$'
    return ax.text(x, y, label, fontsize=fontsize, fontweight='bold',
                   color=color, ha=ha, va=va,
                   bbox=dict(boxstyle='square,pad=0.08', fc='white', ec='none'))


def draw_point_with_projection(ax, x, y, x_label=None, y_label=None, marker='ko', ms=5.2, use_box=True):
    """
    Vẽ điểm và đường gióng nét đứt vuông góc tới 2 trục tọa độ đậm rõ:
    - Áp dụng 'Quy tắc gióng nhãn trục đối xứng' để không bao giờ bị đường nét đứt cắt ngang chữ số
    - Tự động định dạng số âm / số thực qua to_math_label để nét chữ chuẩn toán học STIX
    - Sử dụng white bounding box (w_box) khi cần thiết
    """
    ax.plot([x, x, 0], [0, y, y], 'k--', lw=1.1)
    ax.plot(x, y, marker, markersize=ms)
    
    # Gióng nhãn x
    if x_label is not None:
        y_pos = 0.25 if y < 0 else -0.42
        va = 'bottom' if y < 0 else 'top'
        lbl_x = to_math_label(x_label)
        ax.text(x, y_pos, lbl_x, fontsize=12.5, ha='center', va=va, fontweight='bold',
                bbox=w_box if use_box else None)
        
    # Gióng nhãn y
    if y_label is not None:
        x_pos = 0.18 if x < 0 else -0.42
        ha = 'left' if x < 0 else 'right'
        lbl_y = to_math_label(y_label)
        ax.text(x_pos, y, lbl_y, fontsize=12.5, ha=ha, va='center', fontweight='bold',
                bbox=w_box if use_box else None)

def plot_cubic_function(a, b, c, d, xlim, ylim, filename, marked_points=None):
    """Vẽ đồ thị hàm số bậc ba y = ax^3 + bx^2 + cx + d nét đậm siêu rõ (lw=2.3)"""
    fig, ax = plt.subplots(figsize=(4.2, 3.8), dpi=DEFAULT_DPI)
    x = np.linspace(xlim[0]*0.96, xlim[1]*0.96, 400)
    y = a*x**3 + b*x**2 + c*x + d
    ax.plot(x, y, color='#000000', lw=2.3)
    
    if marked_points:
        for p in marked_points:
            if isinstance(p, (tuple, list)):
                px, py = p[0], p[1]
                xl = str(px) if len(p) < 3 else str(p[2])
                yl = str(py) if len(p) < 4 else str(p[3])
            else:
                px, py = p['x'], p['y']
                xl = p.get('xl')
                yl = p.get('yl')
            draw_point_with_projection(ax, px, py, xl, yl)
            
    setup_axes(ax, xlim, ylim)
    plt.tight_layout()
    plt.savefig(filename, dpi=DEFAULT_DPI, bbox_inches='tight')
    plt.close()

def plot_rational_1_1(a, b, c, d, xlim, ylim, filename, marked_points=None):
    """Vẽ đồ thị hàm phân thức bậc 1 / bậc 1: y = (ax + b) / (cx + d) nét đậm siêu rõ"""
    if c == 0:
        raise ValueError("Hàm phân thức bậc 1/ bậc 1 yêu cầu c != 0 (mẫu số cx + d).")
    fig, ax = plt.subplots(figsize=(4.3, 3.8), dpi=DEFAULT_DPI)
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
            if isinstance(p, (tuple, list)):
                px, py = p[0], p[1]
                xl = str(px) if len(p) < 3 else str(p[2])
                yl = str(py) if len(p) < 4 else str(p[3])
            else:
                px, py = p['x'], p['y']
                xl = p.get('xl')
                yl = p.get('yl')
            ax.plot(px, py, 'ko', markersize=5.2)
            if xl is not None:
                ax.text(px, 0.25 if py < 0 else -0.42, str(xl), fontsize=12, fontweight='bold', ha='center')
            if yl is not None:
                ax.text(0.18 if px < 0 else -0.42, py, str(yl), fontsize=12, fontweight='bold', va='center')
                
    setup_axes(ax, xlim, ylim)
    plt.tight_layout()
    plt.savefig(filename, dpi=DEFAULT_DPI, bbox_inches='tight')
    plt.close()


def plot_rational_2_1(a, b, c, d, e, xlim, ylim, filename, marked_points=None, show_asymptotes=True):
    """
    Vẽ đồ thị hàm phân thức bậc 2 / bậc 1: y = (ax^2 + bx + c) / (dx + e) (Toán 12 GDPT 2018).
    - Tiệm cận đứng: x = -e / d
    - Tiệm cận xiên: y = mx + n với m = a/d, n = (b - m*e) / d
    - Tự động lấy mẫu 2 nhánh mượt mà, vẽ đường tiệm cận nét đứt chuẩn SGK
    """
    if d == 0:
        raise ValueError("Mẫu số dx + e yêu cầu d != 0.")
    if a == 0:
        return plot_rational_1_1(b, c, d, e, xlim, ylim, filename, marked_points)

    fig, ax = plt.subplots(figsize=(4.5, 4.0), dpi=DEFAULT_DPI)
    x_asymp = -e / d
    m = a / d
    n = (b - m * e) / d

    def f(x):
        return (a * x**2 + b * x + c) / (d * x + e)

    x_min, x_max = xlim[0] * 0.96, xlim[1] * 0.96
    y_min, y_max = ylim[0], ylim[1]
    H = y_max - y_min

    # Nhánh trái
    if x_min < x_asymp:
        xs1 = np.linspace(x_min, x_asymp - 0.04, 400)
        ys1 = f(xs1)
        mask1 = (ys1 >= y_min - 0.35 * H) & (ys1 <= y_max + 0.35 * H)
        if np.any(mask1):
            ax.plot(xs1[mask1], ys1[mask1], color='#000000', lw=2.3)

    # Nhánh phải
    if x_max > x_asymp:
        xs2 = np.linspace(x_asymp + 0.04, x_max, 400)
        ys2 = f(xs2)
        mask2 = (ys2 >= y_min - 0.35 * H) & (ys2 <= y_max + 0.35 * H)
        if np.any(mask2):
            ax.plot(xs2[mask2], ys2[mask2], color='#000000', lw=2.3)

    # Đường tiệm cận
    if show_asymptotes:
        # Tiệm cận đứng
        if xlim[0] <= x_asymp <= xlim[1]:
            ax.axvline(x_asymp, color='black', linestyle='--', lw=1.2)
            lbl_x = f'{x_asymp:.0f}' if float(x_asymp).is_integer() else f'{x_asymp:.1f}'
            ax.text(x_asymp, -0.45, lbl_x, fontsize=12, fontweight='bold', ha='center', bbox=w_box)

        # Tiệm cận xiên y = mx + n
        xs_slant = np.array([xlim[0], xlim[1]])
        ys_slant = m * xs_slant + n
        ax.plot(xs_slant, ys_slant, color='black', linestyle='--', lw=1.2)

    if marked_points:
        for p in marked_points:
            if isinstance(p, (tuple, list)):
                px, py = p[0], p[1]
                xl = str(px) if len(p) < 3 else str(p[2])
                yl = str(py) if len(p) < 4 else str(p[3])
            else:
                px, py = p['x'], p['y']
                xl = p.get('xl')
                yl = p.get('yl')
            ax.plot(px, py, 'ko', markersize=5.2)
            if xl is not None:
                ax.text(px, 0.25 if py < 0 else -0.42, str(xl), fontsize=12, fontweight='bold', ha='center')
            if yl is not None:
                ax.text(0.18 if px < 0 else -0.42, py, str(yl), fontsize=12, fontweight='bold', va='center')

    setup_axes(ax, xlim, ylim)
    plt.tight_layout()
    plt.savefig(filename, dpi=DEFAULT_DPI, bbox_inches='tight')
    plt.close()


def plot_bounded_interval_extrema(xs_knots, ys_knots, ds_knots, xlim, ylim, filename,
                                  endpoints=None, extrema=None):
    """
    Vẽ đồ thị hàm số chuẩn xác trên đoạn kín [a; b] có giá trị lớn nhất M và nhỏ nhất m:
    - Đường cong chỉ vẽ chính xác trong [a; b]
    - 2 đầu mút và các điểm cực trị có chấm tròn to (ms=5.5) và đường gióng nét đứt chuẩn xác
    - Nhãn tọa độ tuân thủ 100% 'Quy tắc gióng nhãn trục đối xứng'
    """
    fig, ax = plt.subplots(figsize=(4.5, 3.8), dpi=DEFAULT_DPI)
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
    plt.savefig(filename, dpi=DEFAULT_DPI, bbox_inches='tight')
    plt.close()


# ─── MÔN VẬT LÝ (LỚP 6 - 12) ─────────────────────────────────────────────────

def plot_harmonic_oscillation(A, T, phi, t_max, filename, x_label='t (s)', y_label='x (cm)'):
    """
    Vẽ đồ thị dao động điều hòa li độ - thời gian: x(t) = A * cos(omega * t + phi)
    Chuẩn SGK Vật lý 11 & 12
    """
    fig, ax = plt.subplots(figsize=(6.2, 3.2), dpi=DEFAULT_DPI)
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
    plt.savefig(filename, dpi=DEFAULT_DPI, bbox_inches='tight', facecolor='white')
    plt.close()


def plot_thin_lens_optics(f, d, h, filename, lens_type='convex'):
    """
    Vẽ đường truyền tia sáng & dựng ảnh qua thấu kính mỏng:
    - lens_type: 'convex' (hội tụ) hoặc 'concave' (phân kỳ)
    - f: tiêu cự
    - d: khoảng cách vật
    - h: chiều cao vật sáng AB
    """
    fig, ax = plt.subplots(figsize=(7.2, 3.5), dpi=DEFAULT_DPI)
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
    plt.savefig(filename, dpi=DEFAULT_DPI, bbox_inches='tight', facecolor='white')
    plt.close()


def draw_full_border_bbt(x_labels, yprime_data, y_data, arrows, filename, W=10.0, H=4.2):
    """
    Vẽ Bảng biến thiên (BBT) đóng khung full viền 100% chuẩn SGK & đề quốc gia (300 DPI)
    - x_labels: list of tuples (x_pos, text)
    - yprime_data: list of tuples (x_pos, text)
    - y_data: list of tuples (x_pos, y_pos, text)
    - arrows: list of tuples (start_x, start_y, end_x, end_y)
    """
    fig, ax = plt.subplots(figsize=(6.2, 2.5), dpi=DEFAULT_DPI)
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
    ax.text(col_w/2, 3.65, '$x$', fontsize=13.5, fontweight='bold', fontstyle='italic', ha='center', va='center')
    ax.text(col_w/2, 2.6, r"$\boldsymbol{y'}$", fontsize=16, fontweight='bold', ha='center', va='center')
    ax.text(col_w/2, 1.05, '$y$', fontsize=13.5, fontweight='bold', fontstyle='italic', ha='center', va='center')

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
    plt.savefig(filename, dpi=DEFAULT_DPI, bbox_inches='tight', facecolor='white')
    plt.close()


def draw_bbt_sgk(x_cols, interval_signs, y_data, filename, critical_zeros=None, asymptotes=None, title_labels=None):
    """
    Vẽ Bảng Biến Thiên chuẩn 100% Sách Giáo Khoa Toán Việt Nam (300 DPI):
    - x_cols: danh sách mốc x, ví dụ ['-inf', 0, 1, 2, '+inf']
    - interval_signs: danh sách dấu từng khoảng: ['+', '-', '-', '+']
    - critical_zeros: danh sách index mốc x có y'=0: [1, 3] (tại x=0 và x=2)
    - asymptotes: danh sách index mốc x là tiệm cận đứng có dấu 2 gạch song song ||: [2] (tại x=1)
    - y_data: danh sách giá trị y tại từng mốc:
      + Mốc thường: (val, 'high'|'low'|'mid')
      + Mốc tiệm cận (trong asymptotes): {'left': (val_left, 'low'), 'right': (val_right, 'high')}
    - title_labels: tên các hàng (mặc định: x, y', y hoặc x, f'(x), f(x))
    """
    if title_labels is None:
        title_labels = ('x', "y'", 'y')
    critical_zeros = critical_zeros or []
    asymptotes = asymptotes or []
    n = len(x_cols)
    W = max(9.5, 2.0 + (n - 1) * 2.0)
    H = 4.2
    fig, ax = plt.subplots(figsize=(W * 0.52, H * 0.52), dpi=DEFAULT_DPI)
    ax.set_xlim(0, W)
    ax.set_ylim(0, H)
    ax.axis('off')

    col_w = 1.4
    # Khung viền ngoài (1.4pt) & kẻ ngang phân cách hàng (1.2pt)
    ax.plot([0, W, W, 0, 0], [0, 0, H, H, 0], 'k-', lw=1.4)
    ax.plot([0, W], [3.1, 3.1], 'k-', lw=1.2)
    ax.plot([0, W], [2.1, 2.1], 'k-', lw=1.2)
    ax.plot([col_w, col_w], [0, H], 'k-', lw=1.2)

    # Tiêu đề hàng (In đậm, rõ nét chuẩn SGK)
    ax.text(col_w/2, 3.65, f'${title_labels[0]}$', fontsize=13.5, fontweight='bold', ha='center', va='center')
    
    # Hàng đạo hàm (y', f'(x), y''): làm đậm rõ nét dấu phẩy đạo hàm
    lbl_deriv = str(title_labels[1]).strip().strip('$')
    if "'" in lbl_deriv or r'\prime' in lbl_deriv:
        lbl_deriv_formatted = rf'$\boldsymbol{{{lbl_deriv}}}$'
        deriv_fsize = 16
    else:
        lbl_deriv_formatted = f'${lbl_deriv}$'
        deriv_fsize = 13.5
    ax.text(col_w/2, 2.60, lbl_deriv_formatted, fontsize=deriv_fsize, fontweight='bold', ha='center', va='center')
    ax.text(col_w/2, 1.05, f'${title_labels[2]}$', fontsize=13.5, fontweight='bold', ha='center', va='center')

    # Phân bố đều các mốc x
    step = (W - col_w - 0.8) / (n - 1)
    xs = [col_w + 0.4 + i * step for i in range(n)]

    def fmt_inf(val):
        return to_math_label(val)

    # 1. DÒNG x
    for i, x_val in enumerate(x_cols):
        ax.text(xs[i], 3.65, fmt_inf(x_val), fontsize=12 if 'infty' in fmt_inf(x_val) else 13, fontweight='bold', ha='center', va='center')

    # Dấu 2 gạch song song || tại các cột tiệm cận (khoảng cách 0.08, nét 1.1pt)
    gap = 0.08
    for asymp_idx in asymptotes:
        ax_pos = xs[asymp_idx]
        ax.plot([ax_pos - gap, ax_pos - gap], [0, 3.1], 'k-', lw=1.1)
        ax.plot([ax_pos + gap, ax_pos + gap], [0, 3.1], 'k-', lw=1.1)

    # 2. DÒNG y' (Dấu toán học in đậm rõ chuẩn SGK)
    for i, sign in enumerate(interval_signs):
        pos_x = (xs[i] + xs[i+1]) / 2
        s_clean = str(sign).strip()
        if s_clean == '-':
            s_lbl = r'$\mathbf{-}$'
            fsize = 18
        elif s_clean == '+':
            s_lbl = r'$\mathbf{+}$'
            fsize = 17
        else:
            s_lbl = s_clean
            fsize = 15
        ax.text(pos_x, 2.60, s_lbl, fontsize=fsize, fontweight='bold', ha='center', va='center')

    for idx in critical_zeros:
        if idx not in asymptotes and 0 < idx < n - 1:
            ax.text(xs[idx], 2.60, r'$0$', fontsize=13, fontweight='bold', ha='center', va='center')

    # 3. DÒNG y & MŨI TÊN BIẾN THIÊN
    arrow_bbt = dict(arrowstyle='-|>', color='black', lw=1.3, mutation_scale=10)
    segments = []
    current_segment = []

    for i, item in enumerate(y_data):
        if i in asymptotes:
            if isinstance(item, dict):
                l_val, l_lvl = item.get('left', ('', 'low'))
                r_val, r_lvl = item.get('right', ('', 'high'))
                
                pos_x_l = xs[i] - 0.40
                pos_y_l = 1.65 if l_lvl == 'high' else (0.45 if l_lvl == 'low' else 1.05)
                ax.text(pos_x_l, pos_y_l, fmt_inf(l_val), fontsize=12 if 'infty' in fmt_inf(l_val) else 13, fontweight='bold', ha='center', va='center')
                current_segment.append((pos_x_l, pos_y_l))
                segments.append(current_segment)
                current_segment = []
                
                pos_x_r = xs[i] + 0.40
                pos_y_r = 1.65 if r_lvl == 'high' else (0.45 if r_lvl == 'low' else 1.05)
                ax.text(pos_x_r, pos_y_r, fmt_inf(r_val), fontsize=12 if 'infty' in fmt_inf(r_val) else 13, fontweight='bold', ha='center', va='center')
                current_segment.append((pos_x_r, pos_y_r))
        else:
            if isinstance(item, (tuple, list)):
                val, level = item[0], item[1]
            else:
                val, level = item, 'mid'
            pos_y = 1.65 if level == 'high' else (0.45 if level == 'low' else 1.05)
            pos_x = xs[i]
            txt = fmt_inf(val)
            ax.text(pos_x, pos_y, txt, fontsize=12 if 'infty' in txt else 13, fontweight='bold', ha='center', va='center')
            current_segment.append((pos_x, pos_y))

    if current_segment:
        segments.append(current_segment)

    for seg in segments:
        for k in range(len(seg) - 1):
            x1, y1 = seg[k]
            x2, y2 = seg[k+1]
            dy = y2 - y1
            sx = x1 + 0.32
            ex = x2 - 0.32
            sy = y1 + (0.12 if dy > 0 else -0.12)
            ey = y2 + (-0.12 if dy > 0 else 0.12)
            ax.annotate('', xy=(ex, ey), xytext=(sx, sy), arrowprops=arrow_bbt)

    plt.tight_layout()
    plt.savefig(filename, dpi=DEFAULT_DPI, bbox_inches='tight', pad_inches=0.03, facecolor='white')
    plt.close()


# ─── BỔ SUNG TỪ CHĐ MATH STUDIO (Giai đoạn 1-3) ──────────────────────────────
#  Nguồn tham chiếu thuật toán: CHĐ Math Studio by Chân Đức
#  (D:\skill-quan-trong\chd-math-studio-main\chd-math-studio-main)
#  Port thuật toán JS/Typst → Python/Matplotlib 450 DPI

import math as _math
from itertools import combinations as _combinations


# ──────────────────────────────────────────────────────────────────────────────
# GIAI ĐOẠN 1: Miền Nghiệm Hệ Bất Phương Trình Bậc Nhất 2 Ẩn
# Dạng bài: Toán 10 GDPT 2018 — Quy hoạch tuyến tính, Max/Min F(x,y)=ax+by
# ──────────────────────────────────────────────────────────────────────────────

def _parse_linear_ineq(expr_str):
    """
    Parser BPT bậc nhất 2 ẩn an toàn — không dùng eval().
    Nhận: "2*x + y <= 4", "x/2 + y >= 1", "x > -2*y + 3", "−x ≥ 1"
    Trả về: dict {'a': float, 'b': float, 'c': float, 'strict': bool}
    đại diện cho ax + by ≤ c (đã chuẩn hóa vector pháp tuyến)
    """
    try:
        import sympy as _sp
    except ImportError:
        raise ImportError("Cần cài sympy: pip install sympy")

    # Chuẩn hóa ký tự unicode
    s = str(expr_str).strip()
    s = s.replace('≤', '<=').replace('≥', '>=').replace('−', '-')
    s = s.replace('×', '*').replace('·', '*')

    # Tách tại dấu so sánh (thứ tự quan trọng: <= trước <)
    strict = False
    sign_mul = 1  # +1 nếu ≤, -1 nếu ≥
    for op in ('<=', '>=', '<', '>'):
        if op in s:
            parts = s.split(op, 1)
            if len(parts) == 2:
                strict = (op in ('<', '>'))
                sign_mul = -1 if op.startswith('>') else 1
                lhs_str, rhs_str = parts[0].strip(), parts[1].strip()
                break
    else:
        raise ValueError(f"Không tìm thấy dấu so sánh trong: '{expr_str}'")

    x, y = _sp.symbols('x y')
    try:
        lhs = _sp.sympify(lhs_str, locals={'x': x, 'y': y})
        rhs = _sp.sympify(rhs_str, locals={'x': x, 'y': y})
    except Exception as e:
        raise ValueError(f"Biểu thức không hợp lệ: {e}")

    # Kiểm tra chỉ bậc nhất
    diff = _sp.expand(lhs - rhs)
    for sym in diff.free_symbols:
        if sym not in (x, y):
            raise ValueError(f"Chỉ chấp nhận biến x và y, tìm thấy: {sym}")
    poly = _sp.Poly(diff, x, y)
    if poly.total_degree() > 1:
        raise ValueError("Chỉ nhận biểu thức bậc nhất theo x, y")

    # Rút gọn về ax + by ≤ c
    coeffs = poly.as_dict()
    a = float(coeffs.get((1, 0), 0)) * sign_mul
    b = float(coeffs.get((0, 1), 0)) * sign_mul
    c = -float(coeffs.get((0, 0), 0)) * sign_mul

    norm = _math.hypot(a, b)
    if norm < 1e-12:
        raise ValueError("Sau rút gọn, biểu thức không phụ thuộc x hoặc y")

    return {
        'a': a / norm, 'b': b / norm, 'c': c / norm,
        'strict': strict,
        'source': expr_str.strip()
    }


def _clip_segment_bpt(start, end, planes):
    """
    Thuật toán Liang-Barsky: cắt đoạn [start, end] theo danh sách nửa mặt phẳng ax+by≤c.
    Trả về [(x1,y1), (x2,y2)] hoặc None nếu đoạn bị loại hoàn toàn.
    """
    lo, hi = 0.0, 1.0
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    for p in planes:
        a, b, c = p['a'], p['b'], p['c']
        q = c - a * start[0] - b * start[1]
        d = a * dx + b * dy
        if abs(d) < 1e-12:
            if q < -1e-9:
                return None
        else:
            t = q / d
            if d > 0:
                hi = min(hi, t)
            else:
                lo = max(lo, t)
        if lo > hi:
            return None
    if hi - lo < 1e-10:
        return None
    return [
        (start[0] + lo * dx, start[1] + lo * dy),
        (start[0] + hi * dx, start[1] + hi * dy)
    ]


def _lighten_hex(hex_color, factor=0.42):
    """Pha nhạt màu hex: factor=0 → giữ nguyên, factor=1 → trắng hoàn toàn."""
    hex_color = hex_color.lstrip('#')
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    r2 = int(r * (1 - factor) + 255 * factor)
    g2 = int(g * (1 - factor) + 255 * factor)
    b2 = int(b * (1 - factor) + 255 * factor)
    return f'#{r2:02x}{g2:02x}{b2:02x}'


def _find_boundary_intersections(planes, xmin, xmax, ymin, ymax):
    """
    Tìm tất cả giao điểm giữa các đường biên của hệ BPT (và cả 4 cạnh khung).
    Trả về list các dict {'x', 'y'} nằm trong khung nhìn.
    """
    bounds_planes = [
        {'a': -1, 'b': 0, 'c': -xmin},  # x >= xmin
        {'a':  1, 'b': 0, 'c':  xmax},  # x <= xmax
        {'a':  0, 'b': -1, 'c': -ymin}, # y >= ymin
        {'a':  0, 'b':  1, 'c':  ymax}, # y <= ymax
    ]
    all_planes = planes + bounds_planes
    result = []
    for i, j in _combinations(range(len(all_planes)), 2):
        pi, pj = all_planes[i], all_planes[j]
        det = pi['a'] * pj['b'] - pj['a'] * pi['b']
        if abs(det) < 1e-12:
            continue
        ix = (pi['c'] * pj['b'] - pj['c'] * pi['b']) / det
        iy = (pi['a'] * pj['c'] - pj['a'] * pi['c']) / det
        if not (_math.isfinite(ix) and _math.isfinite(iy)):
            continue
        # Chỉ giữ điểm trong khung nhìn
        if xmin - 1e-8 <= ix <= xmax + 1e-8 and ymin - 1e-8 <= iy <= ymax + 1e-8:
            # Kiểm tra không trùng điểm đã có
            if not any(_math.hypot(p['x'] - ix, p['y'] - iy) < 1e-7 for p in result):
                result.append({'x': ix, 'y': iy})
    return result


def plot_linear_inequalities(
    inequalities,
    xlim=(-1, 6),
    ylim=(-1, 6),
    filename='mien_nghiem.png',
    reverse=False,
    show_intersections=True,
    title='',
    figsize=(5.0, 4.8),
):
    """
    Vẽ miền nghiệm hệ bất phương trình bậc nhất 2 ẩn (Toán 10 GDPT 2018).
    Thuật toán Liang-Barsky Half-Plane Clipping — dịch từ CHĐ Math Studio.

    Tham số:
        inequalities: list of dict hoặc list of str
            Dạng dict: {'expr': '2*x + y <= 4', 'color': '#2755df', 'enabled': True}
            Dạng str:  '2*x + y <= 4'  (dùng màu mặc định theo thứ tự)
        xlim, ylim: tuple (min, max) của khung nhìn
        reverse: False = gạch vùng LOẠI (chuẩn SGK), True = gạch vùng NGHIỆM
        show_intersections: True = hiển thị tọa độ đỉnh đa giác miền nghiệm
        title: tiêu đề hình (để trống nếu không cần)

    Ví dụ:
        plot_linear_inequalities([
            {'expr': 'x >= 0',       'color': '#2755df'},
            {'expr': 'y >= 0',       'color': '#188779'},
            {'expr': 'x + y <= 4',   'color': '#d06b38'},
        ], xlim=(-0.5, 5), ylim=(-0.5, 5), filename='mien_nghiem.png')
    """
    # Bảng màu mặc định nếu không chỉ định màu
    _default_colors = ['#2755df', '#188779', '#d06b38', '#9333ea',
                       '#dc2626', '#0891b2', '#65a30d', '#c026d3']

    xmin, xmax = xlim
    ymin, ymax = ylim

    # Chuẩn hóa input
    normalized = []
    for idx, item in enumerate(inequalities):
        if isinstance(item, str):
            normalized.append({'expr': item, 'color': _default_colors[idx % len(_default_colors)], 'enabled': True})
        elif isinstance(item, dict):
            normalized.append({
                'expr': item.get('expr', item.get('formula', '')),
                'color': item.get('color', _default_colors[idx % len(_default_colors)]),
                'enabled': item.get('enabled', True),
            })

    # Parse các BPT đang bật
    active = []
    for item in normalized:
        if not item['enabled']:
            continue
        parsed = _parse_linear_ineq(item['expr'])
        parsed['color'] = item['color']
        active.append(parsed)

    # Tạo figure
    fig, ax = plt.subplots(figsize=figsize, dpi=DEFAULT_DPI)
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    ax.set_aspect('equal', adjustable='box')
    ax.axis('off')

    W = xmax - xmin
    H = ymax - ymin

    # ── Lưới nền nhạt & Ticks trục ──
    tick_step_x = max(1, int(W / 8))
    tick_step_y = max(1, int(H / 8))
    x_ticks = [x for x in np.arange(_math.ceil(xmin), xmax + 0.01, tick_step_x) if xmin < x < xmax - 0.06 * W]
    y_ticks = [y for y in np.arange(_math.ceil(ymin), ymax + 0.01, tick_step_y) if ymin < y < ymax - 0.06 * H]
    for xt in x_ticks:
        ax.plot([xt, xt], [ymin, ymax], color='#e9edf4', lw=0.7, zorder=0)
    for yt in y_ticks:
        ax.plot([xmin, xmax], [yt, yt], color='#e9edf4', lw=0.7, zorder=0)

    # ── Trục tọa độ ──
    setup_axes(ax, (xmin, xmax), (ymin, ymax))

    # Nhãn số trên trục
    ox = max(xmin, min(xmax, 0))
    oy = max(ymin, min(ymax, 0))
    for xt in x_ticks:
        if abs(xt) > 1e-9:
            ax.text(xt, oy - 0.06 * H, f'${int(xt) if xt == int(xt) else xt}$',
                    fontsize=10, ha='center', va='top', color='#778397', fontweight='bold')
    for yt in y_ticks:
        if abs(yt) > 1e-9:
            ax.text(ox - 0.04 * W, yt, f'${int(yt) if yt == int(yt) else yt}$',
                    fontsize=10, ha='right', va='center', color='#778397', fontweight='bold')

    # ── Bounds planes cho clipping ──
    bounds_planes = [
        {'a': -1, 'b': 0, 'c': -xmin},
        {'a':  1, 'b': 0, 'c':  xmax},
        {'a':  0, 'b': -1, 'c': -ymin},
        {'a':  0, 'b':  1, 'c':  ymax},
    ]

    # ── Hatch (gạch chéo) ──
    hatch_spacing = max(10, int(_math.hypot(W, H) * 8))  # ~13px tại 600px
    hatch_step = (xmax - xmin) / hatch_spacing

    for idx, ineq in enumerate(active):
        # Nửa mặt phẳng bị loại: đảo dấu pháp tuyến
        excluded_plane = [{'a': -ineq['a'], 'b': -ineq['b'], 'c': -ineq['c']}]
        slope = -1 if idx % 2 == 0 else 1
        color_pale = _lighten_hex(ineq['color'], factor=0.55)

        clip_planes = bounds_planes + (excluded_plane if not reverse else [])

        for k in range(-hatch_spacing, hatch_spacing * 2):
            offset = k * hatch_step
            x1, y1 = xmin, ymax + offset
            x2, y2 = xmax, ymax + offset + slope * W

            if reverse:
                # Gạch miền nghiệm chung: cắt theo TẤT CẢ nửa mặt phẳng thỏa mãn
                clip_all = bounds_planes + [{'a': p['a'], 'b': p['b'], 'c': p['c']} for p in active]
                seg = _clip_segment_bpt((x1, y1), (x2, y2), clip_all)
                if seg:
                    ax.plot([seg[0][0], seg[1][0]], [seg[0][1], seg[1][1]],
                            color=color_pale, lw=0.85, zorder=1)
                break  # chỉ cần vẽ 1 lần cho reverse
            else:
                seg = _clip_segment_bpt((x1, y1), (x2, y2), clip_planes)
                if seg:
                    ax.plot([seg[0][0], seg[1][0]], [seg[0][1], seg[1][1]],
                            color=color_pale, lw=0.85, zorder=1)

    # Nếu reverse: vẽ hatch chung một lần
    if reverse and active:
        color_pale = _lighten_hex(active[0]['color'], factor=0.55)
        clip_all = bounds_planes + [{'a': p['a'], 'b': p['b'], 'c': p['c']} for p in active]
        for k in range(-hatch_spacing * 2, hatch_spacing * 2):
            offset = k * hatch_step
            x1, y1 = xmin, ymax + offset
            x2, y2 = xmax, ymax + offset - W  # slope -1
            seg = _clip_segment_bpt((x1, y1), (x2, y2), clip_all)
            if seg:
                ax.plot([seg[0][0], seg[1][0]], [seg[0][1], seg[1][1]],
                        color=color_pale, lw=0.85, zorder=1)

    # ── Vẽ đường biên ──
    xmid = (xmin + xmax) / 2
    ymid = (ymin + ymax) / 2
    span = 2 * _math.hypot(W, H)

    for ineq in active:
        a, b, c = ineq['a'], ineq['b'], ineq['c']
        norm2 = a * a + b * b
        d = (c - a * xmid - b * ymid) / norm2
        cx = xmid + a * d
        cy = ymid + b * d
        p1 = (cx - b * span, cy + a * span)
        p2 = (cx + b * span, cy - a * span)
        seg = _clip_segment_bpt(p1, p2, bounds_planes)
        if seg:
            ls = '--' if ineq['strict'] else '-'
            ax.plot([seg[0][0], seg[1][0]], [seg[0][1], seg[1][1]],
                    color=ineq['color'], lw=2.0, ls=ls, zorder=3)

    # ── Giao điểm đỉnh miền nghiệm ──
    if show_intersections and active:
        intersections = _find_boundary_intersections(
            [{'a': p['a'], 'b': p['b'], 'c': p['c']} for p in active],
            xmin, xmax, ymin, ymax
        )
        # Lọc những điểm thỏa mãn TẤT CẢ BPT (nằm trong/trên miền nghiệm)
        vertex_pts = []
        for pt in intersections:
            px, py = pt['x'], pt['y']
            in_region = all(
                p['a'] * px + p['b'] * py <= p['c'] + 1e-7
                for p in active
            )
            if in_region:
                vertex_pts.append((px, py))

        used_boxes = []
        for px, py in vertex_pts:
            # Format tọa độ
            def _fmt(v):
                if abs(v - round(v)) < 1e-6:
                    return str(int(round(v)))
                return f'{v:.2f}'.rstrip('0').rstrip('.')
            label = f'$({_fmt(px)};\\ {_fmt(py)})$'
            w_est = len(label) * 0.07 * (xmax - xmin)
            h_est = 0.07 * (ymax - ymin)

            # Chống đè: thử 4 vị trí
            candidates = [
                (px + 0.05 * W, py + 0.06 * H),
                (px + 0.05 * W, py - 0.10 * H),
                (px - 0.22 * W, py + 0.06 * H),
                (px - 0.22 * W, py - 0.10 * H),
            ]
            lx, ly = candidates[0]
            for cx2, cy2 in candidates:
                overlap = any(
                    abs(cx2 - bx) < w_est and abs(cy2 - by) < h_est
                    for bx, by in used_boxes
                )
                if not overlap:
                    lx, ly = cx2, cy2
                    break
            used_boxes.append((lx, ly))

            # Chấm tím tại đỉnh
            ax.plot(px, py, 'o', color='#6d28d9', ms=4.5, zorder=5)
            # Hộp nhãn tọa độ
            ax.text(lx, ly, label, fontsize=9.5, color='#4c1d95',
                    ha='left', va='center', zorder=6,
                    bbox=dict(boxstyle='round,pad=0.25', fc='white', ec='#e4dcf8', lw=0.8))

    # ── Chú thích danh sách BPT (góc trên phải, tránh đè nhãn góc trái dưới) ──
    legend_x_start = xmax - 0.03 * W
    legend_y_start = ymax - 0.06 * H
    line_h = 0.065 * H
    for idx, ineq in enumerate(active):
        ly = legend_y_start - idx * line_h
        ls = '--' if ineq['strict'] else '-'
        ax.plot([legend_x_start - 0.10 * W, legend_x_start - 0.03 * W], [ly, ly],
                color=ineq['color'], lw=2.0, ls=ls, zorder=4)
        # Chuẩn hóa ký hiệu hiển thị: thay >= bằng ≥, <= bằng ≤
        display_src = (ineq['source']
                       .replace('>=', '≥').replace('<=', '≤')
                       .replace('> ', '> ').replace('< ', '< '))
        ax.text(legend_x_start - 0.12 * W, ly, display_src,
                fontsize=8.5, color=ineq['color'], va='center', ha='right',
                fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.12', fc='white', ec='none', alpha=0.85))

    # ── Chú thích miền trắng / miền gạch ──
    note = ('Vùng gạch: miền nghiệm chung' if reverse
            else 'Vùng trắng: miền nghiệm chung')
    ax.text((xmin + xmax) / 2, ymax - 0.04 * H, note,
            fontsize=9.5, ha='center', va='top', color='#24334b',
            style='italic')

    # ── Tiêu đề ──
    if title and title.strip():
        ax.set_title(title, fontsize=13, fontweight='bold', color='#24334b', pad=8)

    plt.tight_layout(pad=0.4)
    plt.savefig(filename, dpi=DEFAULT_DPI, bbox_inches='tight',
                pad_inches=0.05, facecolor='white')
    plt.close()


# ──────────────────────────────────────────────────────────────────────────────
# GIAI ĐOẠN 2: Sơ Đồ Cây Xác Suất Tự Động
# Dạng bài: Toán 11-12 — Xác suất có điều kiện, Bayes, Tổng-Nhân
# ──────────────────────────────────────────────────────────────────────────────

def _parse_probability_tree(tree_text):
    """
    Parse cú pháp thụt lề thành cấu trúc cây nút.
    Mỗi dòng: [indent]tên_nút | xác_suất_nhánh
    Nút gốc không có '|'.
    """
    lines = [l for l in tree_text.split('\n') if l.strip()]
    if not lines:
        raise ValueError("Nội dung sơ đồ cây trống.")
    if len(lines) > 40:
        raise ValueError("Sơ đồ cây tối đa 40 nút.")

    nodes = []
    stack = []  # [(depth, node_dict)]

    for i, raw in enumerate(lines):
        # Đếm độ thụt lề (2 dấu cách = 1 cấp)
        stripped = raw.lstrip(' ')
        spaces = len(raw) - len(stripped)
        depth = spaces // 2

        if i == 0 and depth != 0:
            raise ValueError("Nút gốc phải ở cột 0 (không thụt lề).")

        parts = stripped.split('|', 1)
        label = parts[0].strip()
        edge_label = parts[1].strip() if len(parts) > 1 else ''

        if not label:
            raise ValueError(f"Dòng {i+1}: tên nút trống.")

        node = {
            'label': label,
            'edge': edge_label,
            'depth': depth,
            'children': [],
            'x': 0.0, 'y': 0.0,
        }

        # Gắn vào cha
        while stack and stack[-1][0] >= depth:
            stack.pop()
        if stack:
            stack[-1][1]['children'].append(node)
        nodes.append(node)
        stack.append((depth, node))

    return nodes[0], nodes  # root, all_nodes


def plot_probability_tree(
    tree_text,
    filename='so_do_cay.png',
    title='Sơ đồ cây',
    root_color='#2755df',
    node_fill='#f0f4ff',
    node_border='#dbe3f3',
    edge_color='#9aaccb',
    label_color='#24334b',
    prob_color='#778397',
    figsize=None,
):
    """
    Vẽ sơ đồ cây xác suất tự động từ cú pháp thụt lề (Toán 11-12 GDPT 2018).
    Thuật toán layout dịch từ CHĐ Math Studio.

    Tham số:
        tree_text: chuỗi thụt lề, mỗi cấp 2 dấu cách, nhãn nhánh sau '|'
        filename: đường dẫn file xuất (PNG)
        title: tiêu đề hình

    Ví dụ:
        plot_probability_tree(
            '''Phép thử
  A | 0.6
    B | 0.7
    B̄ | 0.3
  Ā | 0.4
    B | 0.2
    B̄ | 0.8''',
            filename='cay_xac_suat.png'
        )
    """
    root, all_nodes = _parse_probability_tree(tree_text)

    leaves = [n for n in all_nodes if not n['children']]
    n_leaves = max(len(leaves), 1)
    max_depth = max(n['depth'] for n in all_nodes)

    # Kích thước canvas tự động (tăng chiều ngang để không bị cấn lề phải)
    fig_h = max(3.6, n_leaves * 0.72 + 1.1)
    fig_w = max(5.8, (max_depth + 1) * 2.3)
    if figsize:
        fig_w, fig_h = figsize

    fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=DEFAULT_DPI)
    ax.set_xlim(0, fig_w)
    ax.set_ylim(0, fig_h)
    ax.axis('off')

    # ── Thuật toán gán tọa độ Y (từ CHĐ Math Studio) ──
    leaf_counter = [0]

    def assign_y(node):
        if not node['children']:
            leaf_counter[0] += 1
            node['y'] = 0.65 + (leaf_counter[0] - 0.5) * (fig_h - 1.2) / n_leaves
        else:
            for child in node['children']:
                assign_y(child)
            node['y'] = sum(c['y'] for c in node['children']) / len(node['children'])

    assign_y(root)

    # ── Kích thước box & Căn lề an toàn chống cắt mép ──
    box_w = min(1.35, (fig_w - 1.6) / (max_depth + 1) * 0.75)
    box_h = min(0.42, (fig_h - 1.2) / n_leaves * 0.60)
    x_margin_l = box_w / 2 + 0.45
    x_margin_r = box_w / 2 + 0.45
    x_span = fig_w - x_margin_l - x_margin_r

    for node in all_nodes:
        node['x'] = x_margin_l + node['depth'] * x_span / max(max_depth, 1)

    label_fs = max(8.0, min(12, box_w * 7.5))
    edge_fs = max(7.5, min(11, box_w * 7.0))

    def _fmt_tree_lbl(lbl):
        s = str(lbl).strip()
        if s.endswith('_bar'):
            return rf'$\overline{{{s[:-4]}}}$'
        if len(s) == 2 and s[1] == '\u0304':
            return rf'$\overline{{{s[0]}}}$'
        if len(s) == 1 and s in ('A', 'B', 'C', 'D', 'M', 'N'):
            return rf'${s}$'
        if s in ('Ā', 'B̄', 'C̄', 'D̄', 'M̄', 'N̄'):
            return rf'$\overline{{{s[0]}}}$'
        return s

    def _fmt_edge_lbl(lbl):
        s = str(lbl).strip()
        if not s:
            return ''
        if '/' in s and not s.startswith('$'):
            p = s.split('/')
            if len(p) == 2 and p[0].strip().isdigit() and p[1].strip().isdigit():
                return rf'$\frac{{{p[0].strip()}}}{{{p[1].strip()}}}$'
        try:
            float(s)
            return rf'${s}$'
        except ValueError:
            pass
        return s

    # ── Vẽ cạnh (edges) ──
    for node in all_nodes:
        for child in node['children']:
            x1 = node['x'] + box_w / 2
            x2 = child['x'] - box_w / 2
            y1, y2 = node['y'], child['y']
            ax.plot([x1, x2], [y1, y2], color=edge_color, lw=1.5, zorder=1)

            # Nhãn xác suất giữa cạnh (lùi xuống để không đè đường nối)
            if child['edge']:
                mx = (x1 + x2) / 2
                my = (y1 + y2) / 2
                offset = -0.12 * (fig_h / 5)
                edge_text = _fmt_edge_lbl(child['edge'])
                ax.text(mx, my + offset, edge_text,
                        fontsize=edge_fs, color=prob_color, ha='center', va='top',
                        fontweight='bold',
                        bbox=dict(boxstyle='round,pad=0.15', fc='white', ec='none'))

    # ── Vẽ các nút ──
    from matplotlib.patches import FancyBboxPatch as _FBP

    for node in all_nodes:
        cx, cy = node['x'], node['y']
        is_root = (node is root)
        fill = root_color if is_root else node_fill
        border = root_color if is_root else node_border
        text_col = 'white' if is_root else label_color

        rect = _FBP(
            (cx - box_w / 2, cy - box_h / 2),
            box_w, box_h,
            boxstyle='round,pad=0.08',
            facecolor=fill, edgecolor=border, linewidth=1.1, zorder=2
        )
        ax.add_patch(rect)

        formatted_lbl = _fmt_tree_lbl(node['label'])
        ax.text(cx, cy, formatted_lbl,
                fontsize=label_fs, color=text_col,
                ha='center', va='center', fontweight='bold', zorder=3)

    # ── Tiêu đề ──
    if title and title.strip():
        ax.text(fig_w / 2, fig_h - 0.28, title,
                fontsize=13, fontweight='bold', color='#24334b',
                ha='center', va='top')

    plt.tight_layout(pad=0.3)
    plt.savefig(filename, dpi=DEFAULT_DPI, bbox_inches='tight',
                pad_inches=0.08, facecolor='white')
    plt.close()


# ──────────────────────────────────────────────────────────────────────────────
# GIAI ĐOẠN 3: Phác Họa Đồ Thị Từ Bảng Biến Thiên (Smoothstep Hermite)
# Dạng bài: Câu nhận diện đồ thị từ BBT — phổ biến trong đề TN THPT
# ──────────────────────────────────────────────────────────────────────────────

def _parse_bbt_value(val_str):
    """Chuyển nhãn BBT ('−∞', '+∞', '3', '1/2', 'sqrt(2)'...) thành float."""
    s = str(val_str).strip().replace('−', '-').replace('–', '-')
    if s in ('+∞', '+inf', 'inf', '+oo'):
        return float('inf')
    if s in ('-∞', '-inf', '-oo'):
        return float('-inf')
    if s in ('', '||'):
        return float('nan')
    try:
        import sympy as _sp
        return float(_sp.sympify(s))
    except Exception:
        try:
            return float(eval(s.replace('^', '**')))
        except Exception:
            return float('nan')


def _bbt_interpolate(x, xs_finite, left_vals, right_vals, signs, scale_x, scale_y):
    """
    Nội suy đường cong từ bảng biến thiên dùng Smoothstep Hermite.
    Dịch từ src/drawing.js — hàm illustration() của CHĐ Math Studio.
    """
    n = len(xs_finite)
    if n < 2:
        return float('nan')

    # Tìm khoảng chứa x
    idx = -1
    for i in range(n - 1):
        xa, xb = xs_finite[i], xs_finite[i + 1]
        in_left = (xa == -float('inf') or x > xa)
        in_right = (xb == float('inf') or x < xb)
        if in_left and in_right:
            idx = i
            break
    if idx < 0:
        return float('nan')

    if signs[idx] == '||':
        return float('nan')

    a, b = xs_finite[idx], xs_finite[idx + 1]
    rawA = right_vals[idx]
    rawB = left_vals[idx + 1]

    if _math.isnan(rawA) or _math.isnan(rawB):
        return float('nan')

    # Tính tham số u ∈ (0, 1)
    if not _math.isfinite(a) and not _math.isfinite(b):
        u = 0.5 + _math.atan(x / max(scale_x, 1e-9)) / _math.pi
    elif not _math.isfinite(a):
        u = scale_x / (b - x + scale_x) if (b - x + scale_x) > 1e-12 else 0.99
    elif not _math.isfinite(b):
        u = (x - a) / (x - a + scale_x) if (x - a + scale_x) > 1e-12 else 0.99
    else:
        denom = b - a
        u = (x - a) / denom if abs(denom) > 1e-12 else 0.5

    u = max(1e-6, min(1 - 1e-6, u))  # Kẹp trong (0,1) để tránh log(0)

    # Nội suy
    if not _math.isfinite(rawA) and not _math.isfinite(rawB):
        try:
            return _math.copysign(1, rawB) * scale_y * _math.log(u / (1 - u))
        except (ValueError, ZeroDivisionError):
            return float('nan')
    elif not _math.isfinite(rawA):
        denom = u
        return rawB + _math.copysign(1, rawA) * scale_y * (1 - u) ** 2 / max(denom, 1e-9)
    elif not _math.isfinite(rawB):
        denom = 1 - u
        return rawA + _math.copysign(1, rawB) * scale_y * u ** 2 / max(denom, 1e-9)
    else:
        # Smoothstep cubic: H(u) = 3u² - 2u³  →  đảm bảo f'=0 tại 2 đầu mốc
        return rawA + (rawB - rawA) * (3 * u ** 2 - 2 * u ** 3)


def plot_graph_from_bbt(
    points,
    signs,
    filename='phachinh_bbt.png',
    xlim=None,
    ylim=None,
    color='#2755df',
    title='Phác họa đồ thị từ bảng biến thiên',
    show_asymptotes=True,
    n_samples=800,
):
    """
    Phác họa đường cong đồ thị hàm số từ bảng biến thiên (Toán 12 GDPT 2018).
    Dùng Smoothstep Hermite để đảm bảo tiếp tuyến nằm ngang tại cực trị.
    Dịch từ CHĐ Math Studio — src/drawing.js hàm illustration().

    Tham số:
        points: list[dict], mỗi phần tử:
            {'x': '-inf', 'y': '+inf', 'mark': ''}        ← đầu mút
            {'x': '-1',   'y': '3',    'mark': '0'}       ← cực trị
            {'x': '1',    'y': '-1',   'mark': '0'}       ← cực trị
            {'x': '+inf', 'y': '+inf', 'mark': ''}        ← đầu mút
            {'x': '1',    'y': '+inf', 'right': '-inf', 'mark': '||'} ← tiệm cận
        signs: list[str] — '+', '-', '0', '||' cho từng khoảng
        filename: đường dẫn PNG xuất
        xlim, ylim: tuple (min, max) — tự động ước lượng nếu None
        color: màu đường đồ thị
        title: tiêu đề (None = không vẽ tiêu đề)

    Ví dụ (hàm bậc 3 y = x³ - 3x + 1):
        plot_graph_from_bbt(
            points=[
                {'x': '-inf', 'y': '-inf', 'mark': ''},
                {'x': '-1',   'y': '3',    'mark': '0'},
                {'x': '1',    'y': '-1',   'mark': '0'},
                {'x': '+inf', 'y': '+inf', 'mark': ''},
            ],
            signs=['+', '-', '+'],
            filename='do_thi_bac3.png'
        )
    """
    if len(points) < 2:
        raise ValueError("Bảng biến thiên cần ít nhất 2 mốc.")
    if len(signs) != len(points) - 1:
        raise ValueError("Số dấu phải bằng số mốc trừ 1.")

    # Chuyển đổi giá trị
    xs_raw = [_parse_bbt_value(p.get('x', '')) for p in points]
    left_vals = [_parse_bbt_value(p.get('y', '')) for p in points]
    right_vals = [
        _parse_bbt_value(p.get('right', p.get('y', ''))) for p in points
    ]
    marks = [p.get('mark', '') for p in points]

    # Tính scale
    finite_xs = [v for v in xs_raw if _math.isfinite(v)]
    finite_ys = [v for v in left_vals + right_vals if _math.isfinite(v)]

    if not finite_xs:
        scale_x = 3.0
    else:
        scale_x = max(1.0, max(finite_xs) - min(finite_xs))
    if not finite_ys:
        scale_y = 3.0
    else:
        scale_y = max(1.0, max(finite_ys) - min(finite_ys))

    # Tự động khung nhìn
    if xlim is None:
        if finite_xs:
            x_lo = min(finite_xs) - 0.4 * scale_x
            x_hi = max(finite_xs) + 0.4 * scale_x
        else:
            x_lo, x_hi = -4.0, 4.0
        xlim = (x_lo, x_hi)

    if ylim is None:
        if finite_ys:
            y_lo = min(finite_ys) - 0.35 * scale_y
            y_hi = max(finite_ys) + 0.35 * scale_y
        else:
            y_lo, y_hi = -4.0, 4.0
        ylim = (y_lo, y_hi)

    xmin, xmax = xlim
    ymin, ymax = ylim
    W, H = xmax - xmin, ymax - ymin

    # Chỉ dùng các mốc hữu hạn làm anchor nội suy
    # (vô cực được xử lý bởi công thức đặc biệt)

    # Vẽ
    fig, ax = plt.subplots(figsize=(4.5, 3.8), dpi=DEFAULT_DPI)

    # Lưới nhạt
    ax.axhline(0, color='#e9edf4', lw=0.8)
    ax.axvline(0, color='#e9edf4', lw=0.8)

    # Trục tọa độ
    setup_axes(ax, (xmin, xmax), (ymin, ymax))

    # ── Tiệm cận đứng (tại mốc có mark='||') ──
    if show_asymptotes:
        for p in points:
            if p.get('mark', '') == '||':
                xv = _parse_bbt_value(p.get('x', ''))
                if _math.isfinite(xv) and xmin <= xv <= xmax:
                    ax.axvline(xv, color='#d19055', lw=1.3, ls='--', zorder=1)

    # ── Sinh các nhánh đường cong ──
    # Tách theo tiệm cận/gián đoạn
    break_xs = set()
    for i, p in enumerate(points):
        if p.get('mark', '') == '||' or signs[i - 1] == '||' if i > 0 else False:
            xv = _parse_bbt_value(p.get('x', ''))
            if _math.isfinite(xv):
                break_xs.add(xv)

    xs_sample = np.linspace(xmin, xmax, n_samples)
    segments = []
    current = []

    for xi in xs_sample:
        # Kiểm tra qua break point
        if any(prev < bx <= xi for bx in break_xs
               for prev in ([current[-1][0]] if current else [])):
            if current:
                segments.append(current)
                current = []

        yi = _bbt_interpolate(xi, xs_raw, left_vals, right_vals, signs, scale_x, scale_y)

        if not _math.isfinite(yi) or yi < ymin - H * 0.5 or yi > ymax + H * 0.5:
            if current:
                segments.append(current)
                current = []
            continue

        # Midpoint test: phát hiện gián đoạn (từ CHĐ Math Studio)
        if current:
            prev_x, prev_y = current[-1]
            if abs(yi - prev_y) > H * 1.5:
                mid_xi = (prev_x + xi) / 2
                mid_yi = _bbt_interpolate(mid_xi, xs_raw, left_vals, right_vals, signs, scale_x, scale_y)
                expected = (prev_y + yi) / 2
                if not _math.isfinite(mid_yi) or abs(mid_yi - expected) > H * 0.15:
                    segments.append(current)
                    current = []

        current.append((xi, max(ymin - H * 0.1, min(ymax + H * 0.1, yi))))

    if current:
        segments.append(current)

    # Vẽ các nhánh (Ramer-Douglas-Peucker simplify giảm điểm)
    for seg in segments:
        if len(seg) < 2:
            continue
        xs_seg, ys_seg = zip(*seg)
        ax.plot(xs_seg, ys_seg, color=color, lw=2.3,
                solid_capstyle='round', solid_joinstyle='round', zorder=3)

    # ── Chấm cực trị (mark='0') ──
    for p in points:
        if p.get('mark', '') == '0':
            px = _parse_bbt_value(p.get('x', ''))
            py = _parse_bbt_value(p.get('y', ''))
            if _math.isfinite(px) and _math.isfinite(py):
                if xmin <= px <= xmax and ymin <= py <= ymax:
                    ax.plot(px, py, 'o', color=color, ms=4.5, zorder=5)
                    # Đường gióng nét đứt
                    ax.plot([px, px, xmin], [ymin, py, py],
                            '--', color='#a6b7e9', lw=1.0, zorder=2)
                    ax.text(px, ymin - 0.05 * H, f'${_parse_bbt_value(p["x"]):.4g}$',
                            fontsize=10, ha='center', va='top', color='#778397', fontweight='bold')
                    ax.text(xmin - 0.04 * W, py, f'${py:.4g}$',
                            fontsize=10, ha='right', va='center', color='#778397', fontweight='bold')

    # ── Cảnh báo "minh họa" ──
    ax.text((xmin + xmax) / 2, ymin + 0.03 * H,
            'Phác họa minh họa — không xác định duy nhất đồ thị',
            fontsize=7.5, ha='center', va='bottom', color='#9ca3af', style='italic')

    if title and title.strip():
        ax.set_title(title, fontsize=11.5, fontweight='bold', color='#24334b', pad=6)

    plt.tight_layout(pad=0.3)
    plt.savefig(filename, dpi=DEFAULT_DPI, bbox_inches='tight',
                pad_inches=0.05, facecolor='white')
    plt.close()


# ─── MÔN HÓA HỌC (LỚP 10 - 12 & KHTN) ────────────────────────────────────────

def plot_chemistry_energy_diagram(reactants_lbl, products_lbl, delta_h_val, ea_val, filename, is_exothermic=True):
    """
    Vẽ giản đồ năng lượng phản ứng hóa học (Enthalpy profile diagram):
    - Phản ứng tỏa nhiệt (is_exothermic=True): delta_h < 0
    - Phản ứng thu nhiệt (is_exothermic=False): delta_h > 0
    - Năng lượng hoạt hóa Ea và biến thiên enthalpy Delta_r H chuẩn 300 DPI
    """
    fig, ax = plt.subplots(figsize=(5.5, 3.8), dpi=DEFAULT_DPI)
    
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
    plt.savefig(filename, dpi=DEFAULT_DPI, bbox_inches='tight', facecolor='white')
    plt.close()


def plot_ph_titration_curve(v_eq, ph_init, ph_eq, ph_end, filename, title="Đường cong chuẩn độ pH"):
    """
    Vẽ đồ thị chuẩn độ axit - bazơ (pH titration curve) chuẩn SGK Hóa học 11
    """
    fig, ax = plt.subplots(figsize=(5.5, 3.8), dpi=DEFAULT_DPI)
    
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
    plt.savefig(filename, dpi=DEFAULT_DPI, bbox_inches='tight', facecolor='white')
    plt.close()


# ─── HÌNH HỌC KHÔNG GIAN 3D (MÔN TOÁN) ───────────────────────────────────────

def plot_pyramid_s_abcd(filename, h_ratio=1.6):
    """
    Vẽ hình chóp S.ABCD đáy hình bình hành / chữ nhật chuẩn mực sư phạm:
    - Cạnh thấy vẽ nét liền (lw=1.8), cạnh khuất vẽ nét đứt (lw=1.4)
    - Các đỉnh S, A, B, C, D được định vị cân đối, chống đè chữ
    """
    fig, ax = plt.subplots(figsize=(4.5, 4.0), dpi=DEFAULT_DPI)
    
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
    
    # Chấm các đỉnh (nhãn in nghiêng chuẩn SGK Việt Nam)
    pts = [('S', S, 'above'), ('A', A, 'top-left'), ('B', B, 'below-left'),
           ('C', C, 'below-right'), ('D', D, 'right')]
    for name, p, pos in pts:
        ax.plot(p[0], p[1], 'ko', markersize=3.8)
        lbl = to_math_label(name, italic=True)
        if pos == 'above':
            ax.text(p[0], p[1] + 0.12, lbl, fontsize=13, fontweight='bold', ha='center')
        elif pos == 'top-left':
            ax.text(p[0] - 0.22, p[1] + 0.08, lbl, fontsize=13, fontweight='bold', ha='right')
        elif pos == 'below-left':
            ax.text(p[0] - 0.18, p[1] - 0.18, lbl, fontsize=13, fontweight='bold', ha='right')
        elif pos == 'below-right':
            ax.text(p[0] + 0.12, p[1] - 0.18, lbl, fontsize=13, fontweight='bold', ha='left')
        elif pos == 'right':
            ax.text(p[0] + 0.18, p[1] + 0.05, lbl, fontsize=13, fontweight='bold', ha='left')

    ax.set_xlim(-0.2, 4.8)
    ax.set_ylim(-0.2, 4.6)
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig(filename, dpi=DEFAULT_DPI, bbox_inches='tight', facecolor='white')
    plt.close()


# ═══════════════════════════════════════════════════════════════════════════════
# NHÓM 1 — TOÁN (Matplotlib)
# ═══════════════════════════════════════════════════════════════════════════════

# ── 1a. Hàm lượng giác ────────────────────────────────────────────────────────
def plot_trig_function(func_type, a, b, c, d, xlim, ylim, filename, marked_points=None):
    """
    Vẽ đồ thị hàm lượng giác y = a*sin(bx + c) + d hoặc y = a*cos(bx + c) + d
    - func_type : 'sin' hoặc 'cos'
    - Trục x ghi nhãn bội số của π/4, π/2, π chuẩn SGK
    - Đánh dấu điểm cực đại, cực tiểu, giao Ox
    """
    fig, ax = plt.subplots(figsize=(8, 4), dpi=DEFAULT_DPI)

    # Phông chữ Times New Roman
    apply_sgk_style()

    x = np.linspace(xlim[0], xlim[1], 2000)
    if func_type == 'sin':
        y = a * np.sin(b * x + c) + d
    else:
        y = a * np.cos(b * x + c) + d

    ax.plot(x, y, color='#1A365D', lw=2.0)

    # Trục toạ độ
    ax.axhline(0, color='black', lw=1.0)
    ax.axvline(0, color='black', lw=1.0)
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)

    # Nhãn trục x bội số π
    x_left, x_right = xlim
    pi = np.pi
    # Tạo danh sách tick x theo bội π/2 nằm trong xlim
    tick_step = pi / 2
    tick_vals = []
    n_start = int(np.floor(x_left / tick_step))
    n_end = int(np.ceil(x_right / tick_step))
    for n in range(n_start, n_end + 1):
        v = n * tick_step
        if xlim[0] <= v <= xlim[1]:
            tick_vals.append(v)

    def _pi_label(val):
        val_over_pi = val / pi
        # Xấp xỉ phân số đơn giản
        from fractions import Fraction
        frac = Fraction(val_over_pi).limit_denominator(8)
        num, den = frac.numerator, frac.denominator
        if num == 0:
            return '$0$'
        elif den == 1:
            if num == 1:
                return r'$\pi$'
            elif num == -1:
                return r'$-\pi$'
            else:
                return r'$%d\pi$' % num
        else:
            if num == 1:
                return r'$\dfrac{\pi}{%d}$' % den
            elif num == -1:
                return r'$-\dfrac{\pi}{%d}$' % den
            else:
                sign = '-' if num < 0 else ''
                return r'$%s\dfrac{%d\pi}{%d}$' % (sign, abs(num), den)

    ax.set_xticks(tick_vals)
    ax.set_xticklabels([_pi_label(v) for v in tick_vals], fontsize=9)

    # Đánh dấu điểm cực đại / cực tiểu / giao Ox
    # Tìm cực trị: chỗ đạo hàm đổi dấu
    dy = np.diff(y)
    for i in range(len(dy) - 1):
        xi = x[i + 1]
        yi = y[i + 1]
        # Cực đại
        if dy[i] > 0 and dy[i + 1] < 0:
            ax.plot(xi, yi, 'o', color='#C0392B', ms=5, zorder=5)
            ax.annotate(f'({xi/pi:.3g}π; {yi:.3g})', (xi, yi),
                        textcoords='offset points', xytext=(6, 6),
                        fontsize=7.5, color='#C0392B',
                        bbox=dict(boxstyle='square,pad=0.12', fc='white', ec='none'))
        # Cực tiểu
        elif dy[i] < 0 and dy[i + 1] > 0:
            ax.plot(xi, yi, 'o', color='#27AE60', ms=5, zorder=5)
            ax.annotate(f'({xi/pi:.3g}π; {yi:.3g})', (xi, yi),
                        textcoords='offset points', xytext=(6, -14),
                        fontsize=7.5, color='#27AE60',
                        bbox=dict(boxstyle='square,pad=0.12', fc='white', ec='none'))
    # Giao Ox
    for i in range(len(y) - 1):
        if y[i] * y[i + 1] <= 0 and abs(y[i] - y[i + 1]) < 1:
            xi = x[i] - y[i] * (x[i + 1] - x[i]) / (y[i + 1] - y[i])
            ax.plot(xi, 0, 's', color='#555555', ms=4, zorder=5)

    # Điểm đánh dấu tùy chỉnh
    if marked_points:
        for pt in marked_points:
            ax.plot(pt[0], pt[1], 'o', color='#E67E22', ms=5, zorder=6)

    ax.spines[['top', 'right']].set_visible(False)
    ax.set_xlabel('x', fontsize=11, loc='right')
    ax.set_ylabel('y', fontsize=11, loc='top', rotation=0)
    ax.tick_params(labelsize=9)
    plt.tight_layout()
    plt.savefig(filename, dpi=DEFAULT_DPI, bbox_inches='tight', facecolor='white')
    plt.close()


# ── 1b. Parabol y = ax² + bx + c ─────────────────────────────────────────────
def plot_parabola(a, b, c, xlim, ylim, filename, vertex_label=True, roots_label=True):
    """
    Vẽ parabol chuẩn SGK lớp 10:
    - Đỉnh V đánh dấu và ghi tọa độ
    - Giao với trục Ox đánh dấu và ghi tọa độ (nếu có)
    - Giao với trục Oy đánh dấu
    - Trục đối xứng nét đứt
    """
    apply_sgk_style()
    fig, ax = plt.subplots(figsize=(6, 5), dpi=DEFAULT_DPI)

    x = np.linspace(xlim[0], xlim[1], 1000)
    y = a * x**2 + b * x + c

    ax.plot(x, y, color='#1A365D', lw=2.0)

    # Trục toạ độ
    ax.axhline(0, color='black', lw=1.0)
    ax.axvline(0, color='black', lw=1.0)

    # Đỉnh
    xv = -b / (2 * a)
    yv = a * xv**2 + b * xv + c
    ax.plot(xv, yv, 'o', color='#C0392B', ms=6, zorder=5)
    if vertex_label:
        label_txt = f'V({xv:.3g}; {yv:.3g})'
        offset = (8, -14) if a > 0 else (8, 6)
        ax.annotate(label_txt, (xv, yv),
                    textcoords='offset points', xytext=offset,
                    fontsize=9, color='#C0392B',
                    bbox=dict(boxstyle='square,pad=0.12', fc='white', ec='none'))

    # Trục đối xứng
    ax.axvline(xv, color='#888888', lw=1.2, ls='--')
    ax.text(xv, ylim[0] + (ylim[1] - ylim[0]) * 0.03,
            f'x = {xv:.3g}', fontsize=8, color='#888888', ha='center',
            bbox=dict(boxstyle='square,pad=0.1', fc='white', ec='none'))

    # Nghiệm (giao Ox)
    disc = b**2 - 4 * a * c
    if disc >= 0:
        x1 = (-b - np.sqrt(disc)) / (2 * a)
        x2 = (-b + np.sqrt(disc)) / (2 * a)
        roots = sorted(set([round(x1, 8), round(x2, 8)]))
        if roots_label:
            for xr in roots:
                ax.plot(xr, 0, 'o', color='#27AE60', ms=6, zorder=5)
                ax.annotate(f'({xr:.3g}; 0)', (xr, 0),
                            textcoords='offset points', xytext=(4, -14),
                            fontsize=8.5, color='#27AE60',
                            bbox=dict(boxstyle='square,pad=0.12', fc='white', ec='none'))

    # Giao Oy (x=0)
    yoy = c
    ax.plot(0, yoy, 'o', color='#2980B9', ms=5, zorder=5)
    ax.annotate(f'(0; {yoy:.3g})', (0, yoy),
                textcoords='offset points', xytext=(6, 4),
                fontsize=8.5, color='#2980B9',
                bbox=dict(boxstyle='square,pad=0.12', fc='white', ec='none'))

    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    ax.spines[['top', 'right']].set_visible(False)
    ax.set_xlabel('x', fontsize=11, loc='right')
    ax.set_ylabel('y', fontsize=11, loc='top', rotation=0)
    ax.tick_params(labelsize=9)
    plt.tight_layout()
    plt.savefig(filename, dpi=DEFAULT_DPI, bbox_inches='tight', facecolor='white')
    plt.close()


# ── 1c. Hình học không gian 3D ────────────────────────────────────────────────

def plot_prism_abc_a1b1c1(filename):
    """
    Vẽ lăng trụ đứng ABC.A'B'C' (lăng trụ tam giác):
    - Cạnh thấy nét liền, cạnh khuất nét đứt
    - Nhãn đỉnh đúng vị trí
    """
    apply_sgk_style()
    fig, ax = plt.subplots(figsize=(5, 6), dpi=DEFAULT_DPI)
    ax.set_aspect('equal')
    ax.axis('off')

    # Toạ độ 2D giả phối cảnh
    # Đáy dưới ABC
    A  = np.array([0.0, 0.0])
    B  = np.array([3.0, 0.0])
    C  = np.array([1.0, 1.2])   # chếch vào giữa (góc nhìn)
    # Đáy trên A'B'C' (dịch lên)
    h = 3.5
    A1 = A + np.array([0.0, h])
    B1 = B + np.array([0.0, h])
    C1 = C + np.array([0.0, h])

    kw_solid  = dict(color='black', lw=1.8)
    kw_hidden = dict(color='black', lw=1.2, ls='--')

    def seg(p, q, **kw):
        ax.plot([p[0], q[0]], [p[1], q[1]], **kw)

    # Đáy dưới: AB thấy, BC thấy, CA khuất
    seg(A, B, **kw_solid)
    seg(B, C, **kw_solid)
    seg(C, A, **kw_hidden)

    # Đáy trên: A'B'C' toàn thấy
    seg(A1, B1, **kw_solid)
    seg(B1, C1, **kw_solid)
    seg(C1, A1, **kw_solid)

    # Cạnh bên: AA', BB' thấy; CC' khuất
    seg(A, A1, **kw_solid)
    seg(B, B1, **kw_solid)
    seg(C, C1, **kw_hidden)

    # Nhãn đỉnh in nghiêng chuẩn SGK Việt Nam
    offsets = {
        'A': (-0.25, -0.20), 'B': (0.12, -0.20), 'C': (0.10, -0.15),
        "A'": (-0.30, 0.12), "B'": (0.12, 0.12), "C'": (0.10, 0.12),
    }
    pts = {'A': A, 'B': B, 'C': C, "A'": A1, "B'": B1, "C'": C1}
    for name, pt in pts.items():
        ox, oy = offsets[name]
        lbl = to_math_label(name, italic=True)
        ax.text(pt[0] + ox, pt[1] + oy, lbl, fontsize=13, fontweight='bold',
                ha='center', va='center',
                bbox=dict(boxstyle='square,pad=0.10', fc='white', ec='none'))

    ax.set_xlim(-0.6, 3.8)
    ax.set_ylim(-0.5, 5.3)
    plt.tight_layout()
    plt.savefig(filename, dpi=DEFAULT_DPI, bbox_inches='tight', facecolor='white')
    plt.close()


def plot_cylinder(filename, show_height=True, show_radius=True):
    """
    Vẽ hình trụ đứng:
    - Đáy dưới elip nét liền
    - Đáy trên nửa trước nét liền, nửa sau nét đứt
    - Nhãn r và h
    """
    apply_sgk_style()
    fig, ax = plt.subplots(figsize=(4, 5), dpi=DEFAULT_DPI)
    ax.set_aspect('equal')
    ax.axis('off')

    cx, cy_bot, cy_top = 0.0, 0.0, 3.0
    rx, ry = 1.5, 0.45   # bán kính elip x, y

    theta = np.linspace(0, 2 * np.pi, 300)

    # Đáy dưới — nét liền hoàn toàn
    ax.plot(cx + rx * np.cos(theta), cy_bot + ry * np.sin(theta),
            'k-', lw=1.8)

    # Đáy trên — nửa trước (0→π) liền, nửa sau (π→2π) đứt
    theta_front = np.linspace(0, np.pi, 150)
    theta_back  = np.linspace(np.pi, 2 * np.pi, 150)
    ax.plot(cx + rx * np.cos(theta_front), cy_top + ry * np.sin(theta_front),
            'k-', lw=1.8)
    ax.plot(cx + rx * np.cos(theta_back),  cy_top + ry * np.sin(theta_back),
            'k--', lw=1.2)

    # Hai đường sinh thấy (trái, phải)
    ax.plot([-rx, -rx], [cy_bot, cy_top], 'k-', lw=1.8)
    ax.plot([ rx,  rx], [cy_bot, cy_top], 'k-', lw=1.8)

    # Nhãn r
    if show_radius:
        ax.plot([cx, rx], [cy_top, cy_top], 'k-', lw=1.2)
        ax.text(rx / 2, cy_top + 0.18, '$r$', fontsize=12, ha='center',
                bbox=dict(boxstyle='square,pad=0.10', fc='white', ec='none'))

    # Nhãn h
    if show_height:
        ax.annotate('', xy=(rx + 0.35, cy_top), xytext=(rx + 0.35, cy_bot),
                    arrowprops=dict(arrowstyle='<->', color='black', lw=1.2))
        ax.text(rx + 0.65, (cy_bot + cy_top) / 2, '$h$', fontsize=12, va='center',
                bbox=dict(boxstyle='square,pad=0.10', fc='white', ec='none'))

    ax.set_xlim(-2.3, 2.8)
    ax.set_ylim(-0.7, 3.7)
    plt.tight_layout()
    plt.savefig(filename, dpi=DEFAULT_DPI, bbox_inches='tight', facecolor='white')
    plt.close()


def plot_cone(filename, show_height=True, show_radius=True, show_slant=False):
    """
    Vẽ hình nón:
    - Đáy elip (nửa trước liền, nửa sau đứt)
    - 2 đường sinh thấy, 1 đường sinh khuất (nét đứt)
    - Nhãn r, h, l
    """
    apply_sgk_style()
    fig, ax = plt.subplots(figsize=(4, 5), dpi=DEFAULT_DPI)
    ax.set_aspect('equal')
    ax.axis('off')

    cx, cy_base = 0.0, 0.0
    rx, ry = 1.5, 0.40
    apex = np.array([cx, 3.2])

    theta_front = np.linspace(0, np.pi, 150)
    theta_back  = np.linspace(np.pi, 2 * np.pi, 150)

    # Đáy
    ax.plot(cx + rx * np.cos(theta_front), cy_base + ry * np.sin(theta_front),
            'k-', lw=1.8)
    ax.plot(cx + rx * np.cos(theta_back),  cy_base + ry * np.sin(theta_back),
            'k--', lw=1.2)

    # Đường sinh thấy (trái & phải)
    ax.plot([cx - rx, apex[0]], [cy_base, apex[1]], 'k-', lw=1.8)
    ax.plot([cx + rx, apex[0]], [cy_base, apex[1]], 'k-', lw=1.8)

    # Đường sinh khuất phía sau (điểm trên đỉnh elip đáy sau)
    ax.plot([cx, apex[0]], [cy_base + ry, apex[1]], 'k--', lw=1.2)

    # Đỉnh
    ax.plot(*apex, 'ko', ms=4)

    # Nhãn r
    if show_radius:
        ax.plot([cx, cx + rx], [cy_base, cy_base], 'k-', lw=1.2)
        ax.text(cx + rx / 2, cy_base - 0.25, '$r$', fontsize=12, ha='center',
                bbox=dict(boxstyle='square,pad=0.10', fc='white', ec='none'))

    # Nhãn h
    if show_height:
        ax.plot([cx, cx], [cy_base, apex[1]], 'k--', lw=1.0)
        ax.text(cx + 0.18, apex[1] / 2, '$h$', fontsize=12, va='center',
                bbox=dict(boxstyle='square,pad=0.10', fc='white', ec='none'))

    # Nhãn l (đường sinh)
    if show_slant:
        l_val = np.hypot(rx, apex[1])
        ax.text((cx + rx + apex[0]) / 2 + 0.1, (cy_base + apex[1]) / 2,
                '$l$', fontsize=12,
                bbox=dict(boxstyle='square,pad=0.10', fc='white', ec='none'))

    ax.set_xlim(-2.2, 2.5)
    ax.set_ylim(-0.8, 3.9)
    plt.tight_layout()
    plt.savefig(filename, dpi=DEFAULT_DPI, bbox_inches='tight', facecolor='white')
    plt.close()


def plot_sphere(filename, show_cross_section=True):
    """
    Vẽ hình cầu:
    - Đường tròn lớn nét liền
    - Đường kính ngang (elip nửa sau nét đứt)
    - Tâm O, bán kính R
    """
    apply_sgk_style()
    fig, ax = plt.subplots(figsize=(4.5, 4.5), dpi=DEFAULT_DPI)
    ax.set_aspect('equal')
    ax.axis('off')

    cx, cy, R = 0.0, 0.0, 2.0
    rx_eq, ry_eq = R, R * 0.32   # elip xích đạo

    theta = np.linspace(0, 2 * np.pi, 600)
    # Đường tròn lớn (mặt phẳng đứng)
    ax.plot(cx + R * np.cos(theta), cy + R * np.sin(theta), 'k-', lw=2.0)

    if show_cross_section:
        # Nửa trước elip xích đạo (nét liền)
        t_front = np.linspace(0, np.pi, 200)
        t_back  = np.linspace(np.pi, 2 * np.pi, 200)
        ax.plot(cx + rx_eq * np.cos(t_front), cy + ry_eq * np.sin(t_front),
                'k-', lw=1.6)
        ax.plot(cx + rx_eq * np.cos(t_back),  cy + ry_eq * np.sin(t_back),
                'k--', lw=1.1)

    # Tâm O
    ax.plot(cx, cy, 'ko', ms=3)
    ax.text(cx - 0.18, cy - 0.18, '$O$', fontsize=12)

    # Bán kính R
    ax.plot([cx, cx + R], [cy, cy + 0], 'k-', lw=1.2)
    ax.text(cx + R / 2, cy + 0.15, '$R$', fontsize=12, ha='center',
            bbox=dict(boxstyle='square,pad=0.10', fc='white', ec='none'))

    ax.set_xlim(-2.8, 2.8)
    ax.set_ylim(-2.8, 2.8)
    plt.tight_layout()
    plt.savefig(filename, dpi=DEFAULT_DPI, bbox_inches='tight', facecolor='white')
    plt.close()


def plot_rectangular_box(a, b, c, filename):
    """
    Vẽ hình hộp chữ nhật ABCD.A'B'C'D' với 3 kích thước a, b, c.
    Cạnh thấy nét liền, cạnh khuất nét đứt.
    Ghi nhãn a, b, c trên các cạnh.
    """
    apply_sgk_style()
    fig, ax = plt.subplots(figsize=(6, 5), dpi=DEFAULT_DPI)
    ax.set_aspect('equal')
    ax.axis('off')

    # Phối cảnh chiều sâu theo hướng xiên 30°, tỉ lệ 0.5
    depth_angle = np.radians(30)
    dx = b * np.cos(depth_angle) * 0.5
    dy = b * np.sin(depth_angle) * 0.5

    # 8 đỉnh: A B C D (đáy trước) → A' B' C' D' (đáy sau)
    # Mặt trước ABCD: hình chữ nhật a × c
    A = np.array([0.0,  0.0])
    B = np.array([a,    0.0])
    C = np.array([a,    c])
    D = np.array([0.0,  c])

    A1 = A + np.array([dx, dy])
    B1 = B + np.array([dx, dy])
    C1 = C + np.array([dx, dy])
    D1 = D + np.array([dx, dy])

    kw_s = dict(color='black', lw=1.8)
    kw_h = dict(color='black', lw=1.2, ls='--')

    def seg(p, q, **kw):
        ax.plot([p[0], q[0]], [p[1], q[1]], **kw)

    # Mặt trước (thấy)
    seg(A, B, **kw_s); seg(B, C, **kw_s)
    seg(C, D, **kw_s); seg(D, A, **kw_s)
    # Mặt sau (khuất)
    seg(A1, B1, **kw_h); seg(B1, C1, **kw_h)
    seg(C1, D1, **kw_h); seg(D1, A1, **kw_h)
    # Cạnh nối: AB→A'B' thấy; AD→A'D' khuất; BC→B'C' thấy
    seg(A, A1, **kw_h)    # cạnh khuất AA'
    seg(B, B1, **kw_s)    # cạnh thấy BB'
    seg(C, C1, **kw_s)    # cạnh thấy CC'
    seg(D, D1, **kw_s)    # cạnh thấy DD'

    # Nhãn đỉnh in nghiêng chuẩn SGK Việt Nam
    labels = {
        'A': A, 'B': B, 'C': C, 'D': D,
        "A'": A1, "B'": B1, "C'": C1, "D'": D1
    }
    offsets_lbl = {
        'A': (-0.22, -0.22), 'B': (0.12, -0.22),
        'C': (0.12,  0.12),  'D': (-0.22,  0.12),
        "A'": (-0.22, -0.22), "B'": (0.12, -0.15),
        "C'": (0.12,  0.12),  "D'": (-0.26,  0.12),
    }
    for name, pt in labels.items():
        ox, oy = offsets_lbl[name]
        lbl = to_math_label(name, italic=True)
        ax.text(pt[0] + ox, pt[1] + oy, lbl, fontsize=13, fontweight='bold', ha='center', va='center',
                bbox=dict(boxstyle='square,pad=0.08', fc='white', ec='none'))

    # Nhãn kích thước
    # a: cạnh AB (đáy dưới trước)
    ax.text((A[0] + B[0]) / 2, A[1] - 0.30, f'$a$', fontsize=13, fontweight='bold', ha='center',
            bbox=dict(boxstyle='square,pad=0.10', fc='white', ec='none'))
    # c: cạnh BC (cạnh bên đứng)
    ax.text(B[0] + 0.30, (B[1] + C[1]) / 2, f'$c$', fontsize=13, fontweight='bold', ha='left', va='center',
            bbox=dict(boxstyle='square,pad=0.10', fc='white', ec='none'))
    # b: cạnh BB' (chiều sâu)
    mid_bb1 = (B + B1) / 2
    ax.text(mid_bb1[0] + 0.18, mid_bb1[1], f'$b$', fontsize=13, fontweight='bold', ha='left', va='center',
            bbox=dict(boxstyle='square,pad=0.10', fc='white', ec='none'))

    margin = 0.6
    all_pts = [A, B, C, D, A1, B1, C1, D1]
    xs = [p[0] for p in all_pts]
    ys = [p[1] for p in all_pts]
    ax.set_xlim(min(xs) - margin, max(xs) + margin)
    ax.set_ylim(min(ys) - margin, max(ys) + margin)
    plt.tight_layout()
    plt.savefig(filename, dpi=DEFAULT_DPI, bbox_inches='tight', facecolor='white')
    plt.close()


# ═══════════════════════════════════════════════════════════════════════════════
# NHÓM 2 — VẬT LÝ (Matplotlib)
# ═══════════════════════════════════════════════════════════════════════════════

# ── 2a. Đồ thị động học ───────────────────────────────────────────────────────
def plot_kinematics(t_values, s_values, filename,
                    xlabel='t (s)', ylabel='s (m)',
                    title='Đồ thị s - t', color='#1A365D'):
    """
    Vẽ đồ thị chuyển động s-t / v-t / a-t tổng quát.
    - t_values: array hoặc list of arrays
    - s_values: array hoặc list of arrays (tương ứng)
    - Nếu truyền list of arrays thì vẽ nhiều đường với màu tự động
    """
    apply_sgk_style()
    fig, ax = plt.subplots(figsize=(7, 4), dpi=DEFAULT_DPI)

    colors_cycle = ['#1A365D', '#C0392B', '#27AE60', '#8E44AD', '#D35400']

    # Chuẩn hóa đầu vào: cho phép array lẫn list of arrays
    if isinstance(t_values, np.ndarray) and t_values.ndim == 1:
        t_list = [t_values]
        s_list = [s_values]
    elif isinstance(t_values, list) and len(t_values) > 0 and isinstance(t_values[0], (int, float)):
        t_list = [np.array(t_values)]
        s_list = [np.array(s_values)]
    else:
        t_list = [np.array(t) for t in t_values]
        s_list = [np.array(s) for s in s_values]

    for idx, (t, s) in enumerate(zip(t_list, s_list)):
        clr = colors_cycle[idx % len(colors_cycle)]
        ax.plot(t, s, color=clr, lw=2.0,
                label=f'Vật {idx + 1}' if len(t_list) > 1 else None)

        # Đánh dấu các điểm đặc biệt (t=0 và t cuối)
        ax.plot(t[0],  s[0],  'o', color=clr, ms=5, zorder=5)
        ax.plot(t[-1], s[-1], 'o', color=clr, ms=5, zorder=5)

    ax.axhline(0, color='black', lw=0.8)
    ax.axvline(0, color='black', lw=0.8)
    ax.set_xlabel(xlabel, fontsize=11)
    ax.set_ylabel(ylabel, fontsize=11)
    if title:
        ax.set_title(title, fontsize=12, pad=6)
    if len(t_list) > 1:
        ax.legend(fontsize=9)
    ax.spines[['top', 'right']].set_visible(False)
    ax.tick_params(labelsize=9)
    plt.tight_layout()
    plt.savefig(filename, dpi=DEFAULT_DPI, bbox_inches='tight', facecolor='white')
    plt.close()


def plot_velocity_time(segments, filename):
    """
    Vẽ đồ thị v-t theo từng đoạn chuyển động.
    segments: list of dict với keys:
        t_start, t_end, v_start, v_end, label (optional), fill (optional bool)
    """
    apply_sgk_style()
    fig, ax = plt.subplots(figsize=(7, 4), dpi=DEFAULT_DPI)

    colors_seg = ['#1A365D', '#C0392B', '#27AE60', '#8E44AD']

    for idx, seg in enumerate(segments):
        t0, t1 = seg['t_start'], seg['t_end']
        v0, v1 = seg['v_start'], seg['v_end']
        clr = colors_seg[idx % len(colors_seg)]
        ts = np.linspace(t0, t1, 200)
        vs = np.linspace(v0, v1, 200)
        ax.plot(ts, vs, color='#1A365D', lw=2.0)
        ax.plot(t0, v0, 'o', color='#1A365D', ms=5, zorder=5)

        # Nhãn đoạn
        if seg.get('label'):
            ax.text((t0 + t1) / 2, max(v0, v1) + 0.5, seg['label'],
                    fontsize=8.5, ha='center', color='#444444',
                    bbox=dict(boxstyle='square,pad=0.10', fc='white', ec='none'))

        # Tô màu diện tích (tùy chọn)
        if seg.get('fill', False):
            ax.fill_between(ts, vs, 0, alpha=0.12, color=clr)

        # Nét đứt dóng xuống trục t
        for tv, vv in [(t0, v0), (t1, v1)]:
            if vv != 0:
                ax.plot([tv, tv], [0, vv], 'k--', lw=0.8)
                ax.plot([0, tv],  [vv, vv], 'k--', lw=0.8)

    # Điểm cuối của đoạn cuối
    last = segments[-1]
    ax.plot(last['t_end'], last['v_end'], 'o', color='#1A365D', ms=5, zorder=5)

    ax.axhline(0, color='black', lw=1.0)
    ax.axvline(0, color='black', lw=1.0)
    ax.set_xlabel('t (s)', fontsize=11)
    ax.set_ylabel('v (m/s)', fontsize=11)
    ax.set_title('Đồ thị v - t', fontsize=12, pad=6)
    ax.spines[['top', 'right']].set_visible(False)
    ax.tick_params(labelsize=9)
    plt.tight_layout()
    plt.savefig(filename, dpi=DEFAULT_DPI, bbox_inches='tight', facecolor='white')
    plt.close()


# ── 2b. Nhiệt động học / Khí lý tưởng ────────────────────────────────────────
def plot_ideal_gas_pV(T_values, V_ranges, filename):
    """
    Vẽ đường đẳng nhiệt pV = nRT trên hệ trục (V, p).
    - T_values : list các nhiệt độ [T1, T2, T3, ...]
    - V_ranges : list 2-tuple (V_min, V_max) tương ứng mỗi T
    Giả định n=1, R=8.314 (đơn vị tùy ý, hiển thị tỉ lệ)
    """
    apply_sgk_style()
    fig, ax = plt.subplots(figsize=(6, 5), dpi=DEFAULT_DPI)

    colors_T = ['#C0392B', '#E67E22', '#27AE60', '#2980B9', '#8E44AD']
    nR = 8.314  # n*R, có thể chuẩn hoá

    for idx, (T, (Vmin, Vmax)) in enumerate(zip(T_values, V_ranges)):
        V = np.linspace(Vmin, Vmax, 500)
        p = nR * T / V
        clr = colors_T[idx % len(colors_T)]
        ax.plot(V, p, color=clr, lw=2.0,
                label=f'$T_{idx + 1}$ = {T} K')
        # Nhãn cuối đường
        ax.text(V[-1] * 1.01, p[-1], f'$T_{idx + 1}$', fontsize=10,
                color=clr, va='center',
                bbox=dict(boxstyle='square,pad=0.08', fc='white', ec='none'))

    ax.axhline(0, color='black', lw=0.8)
    ax.axvline(0, color='black', lw=0.8)
    ax.set_xlabel('$V$ (m³)', fontsize=11)
    ax.set_ylabel('$p$ (Pa)', fontsize=11)
    ax.set_title('Đồ thị $p$–$V$ (đẳng nhiệt)', fontsize=12, pad=6)
    ax.spines[['top', 'right']].set_visible(False)
    ax.tick_params(labelsize=9)
    # Chú thích T tăng dần
    if len(T_values) >= 2:
        note = f'$T_1 < T_2$' + (f' < T_3$' if len(T_values) >= 3 else '')
        ax.text(0.98, 0.96, note, transform=ax.transAxes,
                fontsize=9, ha='right', va='top',
                bbox=dict(boxstyle='round,pad=0.3', fc='#FAFAFA', ec='#BBBBBB'))
    plt.tight_layout()
    plt.savefig(filename, dpi=DEFAULT_DPI, bbox_inches='tight', facecolor='white')
    plt.close()


def plot_ideal_gas_pT(V_values, T_ranges, filename):
    """
    Vẽ đường đẳng tích p/T = const trên hệ (T, p).
    - V_values : list thể tích [V1, V2, ...]
    - T_ranges : list 2-tuple (T_min, T_max) tương ứng mỗi V
    """
    apply_sgk_style()
    fig, ax = plt.subplots(figsize=(6, 5), dpi=DEFAULT_DPI)

    colors_V = ['#C0392B', '#E67E22', '#27AE60', '#2980B9', '#8E44AD']
    nR = 8.314

    for idx, (V, (Tmin, Tmax)) in enumerate(zip(V_values, T_ranges)):
        T = np.linspace(Tmin, Tmax, 500)
        p = nR * T / V
        clr = colors_V[idx % len(colors_V)]
        ax.plot(T, p, color=clr, lw=2.0,
                label=f'$V_{idx + 1}$ = {V} m³')
        # Nhãn cuối đường
        ax.text(T[-1] * 1.01, p[-1], f'$V_{idx + 1}$', fontsize=10,
                color=clr, va='center',
                bbox=dict(boxstyle='square,pad=0.08', fc='white', ec='none'))
        # Nét đứt kéo về T=0
        ax.plot([0, T[0]], [0, p[0]], color=clr, lw=1.0, ls='--', alpha=0.5)

    ax.axhline(0, color='black', lw=0.8)
    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)
    ax.set_xlabel('$T$ (K)', fontsize=11)
    ax.set_ylabel('$p$ (Pa)', fontsize=11)
    ax.set_title('Đồ thị $p$–$T$ (đẳng tích)', fontsize=12, pad=6)
    ax.spines[['top', 'right']].set_visible(False)
    ax.tick_params(labelsize=9)
    plt.tight_layout()
    plt.savefig(filename, dpi=DEFAULT_DPI, bbox_inches='tight', facecolor='white')
    plt.close()


# ── 2c. Giản đồ vectơ Fresnel (RLC) ──────────────────────────────────────────
def plot_fresnel_diagram(U_R, U_L, U_C, filename):
    """
    Vẽ giản đồ vectơ Fresnel cho mạch RLC nối tiếp:
    - U_R nằm ngang (cùng pha với I)
    - U_L thẳng đứng lên
    - U_C thẳng đứng xuống
    - Vectơ U_L - U_C (kết hợp)
    - Vectơ U tổng
    - Góc φ
    """
    apply_sgk_style()
    fig, ax = plt.subplots(figsize=(5, 5.5), dpi=DEFAULT_DPI)
    ax.set_aspect('equal')

    arrow_kw = dict(length_includes_head=True, head_width=0.06, head_length=0.08, lw=1.8)

    # Vectơ U_R (nằm ngang)
    ax.arrow(0, 0, U_R, 0, color='#27AE60', **arrow_kw)
    ax.text(U_R / 2, -0.25, r'$U_R$', fontsize=12, ha='center', color='#27AE60',
            bbox=dict(boxstyle='square,pad=0.10', fc='white', ec='none'))

    # Vectơ U_L (thẳng đứng lên, gốc tại đầu U_R)
    ax.arrow(U_R, 0, 0, U_L, color='#C0392B', **arrow_kw)
    ax.text(U_R + 0.20, U_L / 2, r'$U_L$', fontsize=12, va='center', color='#C0392B',
            bbox=dict(boxstyle='square,pad=0.10', fc='white', ec='none'))

    # Vectơ U_C (thẳng đứng xuống, gốc tại đầu U_R)
    ax.arrow(U_R, 0, 0, -U_C, color='#2980B9', **arrow_kw)
    ax.text(U_R + 0.20, -U_C / 2, r'$U_C$', fontsize=12, va='center', color='#2980B9',
            bbox=dict(boxstyle='square,pad=0.10', fc='white', ec='none'))

    # Vectơ tổng U (từ gốc O đến điểm cuối)
    U_net_y = U_L - U_C
    U_total = np.hypot(U_R, U_net_y)
    ax.arrow(0, 0, U_R, U_net_y, color='#8E44AD', lw=2.2,
             length_includes_head=True, head_width=0.07, head_length=0.09)
    ax.text(U_R / 2 - 0.30, U_net_y / 2 + 0.10,
            f'$U = {U_total:.2g}$', fontsize=11, color='#8E44AD',
            bbox=dict(boxstyle='square,pad=0.10', fc='white', ec='none'))

    # Đường nét đứt U_L - U_C từ O lên
    ax.plot([U_R, U_R], [0, U_net_y], 'k--', lw=1.0)

    # Góc φ
    phi = np.degrees(np.arctan2(U_net_y, U_R))
    phi_rad = np.radians(phi)
    arc_r = min(U_total * 0.35, 0.9)
    arc_theta = np.linspace(0, phi_rad, 80)
    ax.plot(arc_r * np.cos(arc_theta), arc_r * np.sin(arc_theta), 'k-', lw=1.0)
    ax.text(arc_r * 1.08 * np.cos(phi_rad / 2),
            arc_r * 1.08 * np.sin(phi_rad / 2),
            r'$\varphi$', fontsize=11,
            bbox=dict(boxstyle='square,pad=0.08', fc='white', ec='none'))

    ax.axhline(0, color='black', lw=0.8)
    ax.axvline(0, color='black', lw=0.8)
    ax.text(0, -0.18, '$O$', fontsize=11, ha='center')

    # Padding
    pad = 0.5
    ax.set_xlim(-pad, U_R + pad + 0.8)
    y_span = max(U_L, U_C, abs(U_net_y))
    ax.set_ylim(-U_C - pad, U_L + pad)

    ax.spines[['top', 'right']].set_visible(False)
    ax.set_xlabel('(đồng pha với $I$)', fontsize=9, color='#555555')
    ax.tick_params(labelsize=8)
    ax.set_title('Giản đồ Fresnel mạch RLC nối tiếp', fontsize=11, pad=6)
    plt.tight_layout()
    plt.savefig(filename, dpi=DEFAULT_DPI, bbox_inches='tight', facecolor='white')
    plt.close()


# =============================================================================
# HÀM 1: plot_exponential_log
# =============================================================================

def plot_exponential_log(a, xlim, ylim, filename,
                         show_inverse=True,
                         show_ref_line=True,
                         marked_points=None):
    """
    Vẽ đồ thị hàm số mũ y = a^x và logarithm y = log_a(x)
    chuẩn SGK Toán 12.
    - a: cơ số (a > 0, a != 1). Thường là 2, 3, 0.5, 1/3
    - show_inverse: True → vẽ cả y=log_a(x) đối xứng qua y=x
    - show_ref_line: True → vẽ đường y=x nét đứt làm trục đối xứng
    - marked_points: list of dict {x, y, xl, yl} để đánh dấu điểm đặc biệt
    Yêu cầu:
    - y=a^x: đường màu '#1A365D', nhãn '$y=a^x$' đặt ở đầu đường
    - y=log_a(x): đường màu '#C53030', nhãn '$y=\\log_a x$'
    - Điểm giao (1,0) và (0,1) đánh dấu chấm tròn đen
    - Tiệm cận ngang y=0 (cho a^x) và tiệm cận đứng x=0 (cho log) ghi nét đứt mờ
    - Giao với trục Oy: (0; 1) đánh dấu
    - Giao log với trục Ox: (1; 0) đánh dấu
    """
    import numpy as np
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(7, 6), facecolor='white')

    x_min, x_max = xlim
    y_min, y_max = ylim

    # --- Vẽ y = a^x ---
    x_exp = np.linspace(x_min, x_max, 800)
    y_exp = np.power(float(a), x_exp)
    # Chỉ vẽ trong ylim
    mask_exp = (y_exp >= y_min) & (y_exp <= y_max)
    ax.plot(x_exp[mask_exp], y_exp[mask_exp],
            color='#1A365D', lw=2.2, zorder=3, label=r'$y = a^x$')

    # Nhãn đặt ở đầu đường (phía phải nếu a>1, phía trái nếu a<1)
    if a > 1:
        x_label_exp = x_exp[mask_exp][-1] if mask_exp.any() else x_max
    else:
        x_label_exp = x_exp[mask_exp][0] if mask_exp.any() else x_min
    y_label_exp = float(a) ** float(x_label_exp)
    ax.text(x_label_exp - 0.15, y_label_exp + 0.15,
            r'$y=a^x$', fontsize=12, fontweight='bold',
            color='#1A365D', fontfamily='DejaVu Serif',
            ha='right', va='bottom',
            bbox=dict(boxstyle='square,pad=0.12', fc='white', ec='none'))

    # --- Vẽ y = log_a(x) ---
    if show_inverse:
        x_log = np.linspace(max(1e-3, x_min if x_min > 0 else 1e-3), x_max, 800)
        y_log = np.log(x_log) / np.log(float(a))
        mask_log = (y_log >= y_min) & (y_log <= y_max)
        ax.plot(x_log[mask_log], y_log[mask_log],
                color='#C53030', lw=2.2, zorder=3, label=r'$y = \log_a x$')

        # Nhãn log
        if mask_log.any():
            xl_last = x_log[mask_log][-1]
            yl_last = y_log[mask_log][-1]
            ax.text(xl_last + 0.1, yl_last - 0.25,
                    r'$y=\log_a x$', fontsize=12, fontweight='bold',
                    color='#C53030', fontfamily='DejaVu Serif',
                    ha='left', va='top',
                    bbox=dict(boxstyle='square,pad=0.12', fc='white', ec='none'))

    # --- Đường y = x (trục đối xứng) ---
    if show_ref_line:
        xy_line = np.linspace(max(x_min, y_min), min(x_max, y_max), 400)
        ax.plot(xy_line, xy_line,
                color='gray', lw=1.2, ls='--', alpha=0.65, zorder=2,
                label=r'$y = x$')
        ax.text(xy_line[-1] + 0.05, xy_line[-1],
                r'$y=x$', fontsize=10, color='gray',
                ha='left', va='center',
                bbox=dict(boxstyle='square,pad=0.12', fc='white', ec='none'))

    # --- Tiệm cận ---
    ax.axhline(0, color='black', lw=1.0, zorder=1)
    if show_inverse:
        ax.axvline(0, color='black', lw=1.0, zorder=1)

    # --- Điểm giao đặc biệt ---
    ax.plot(0, 1, 'ko', ms=6, zorder=5)
    ax.annotate('$(0,\\ 1)$', xy=(0, 1), xytext=(-0.35, 1.2),
                fontsize=11, fontfamily='DejaVu Serif',
                arrowprops=None)
    if show_inverse:
        ax.plot(1, 0, 'ko', ms=6, zorder=5)
        ax.annotate('$(1,\\ 0)$', xy=(1, 0), xytext=(1.2, -0.35),
                    fontsize=11, fontfamily='DejaVu Serif',
                    arrowprops=None)

    # --- Điểm đặc biệt bổ sung ---
    if marked_points:
        for pt in marked_points:
            ax.plot(pt['x'], pt['y'], 'ko', ms=6, zorder=5)
            ax.annotate(f"$({pt.get('xl', pt['x'])},\\ {pt.get('yl', pt['y'])})$",
                        xy=(pt['x'], pt['y']),
                        xytext=(pt['x'] + 0.15, pt['y'] + 0.15),
                        fontsize=10, fontfamily='DejaVu Serif')

    # --- Trục toạ độ có mũi tên ---
    ax.spines[['top', 'right']].set_visible(False)
    ax.spines['left'].set_position('zero')
    ax.spines['bottom'].set_position('zero')
    ax.spines['left'].set_linewidth(1.1)
    ax.spines['bottom'].set_linewidth(1.1)

    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)
    ax.set_xlabel('$x$', fontsize=13, fontweight='bold',
                  fontfamily='DejaVu Serif', loc='right')
    ax.set_ylabel('$y$', fontsize=13, fontweight='bold',
                  fontfamily='DejaVu Serif', loc='top', rotation=0)

    ax.plot(x_max, 0, '>k', ms=5, clip_on=False)
    ax.plot(0, y_max, '^k', ms=5, clip_on=False)

    ax.tick_params(labelsize=10)
    ax.set_xticks([t for t in ax.get_xticks() if t != 0])
    ax.set_yticks([t for t in ax.get_yticks() if t != 0])

    plt.tight_layout()
    plt.savefig(filename, dpi=DEFAULT_DPI, bbox_inches='tight', facecolor='white')
    plt.close()


# =============================================================================
# HÀM 2: plot_absolute_value_transform
# =============================================================================

def plot_absolute_value_transform(coeffs, transform_type, xlim, ylim, filename,
                                   func_type='cubic',
                                   show_original=True):
    """
    Vẽ đồ thị y=|f(x)| hoặc y=f(|x|) từ hàm f(x) gốc.
    - coeffs: tuple hệ số của f(x).
        func_type='cubic'   : (a, b, c, d) → ax^3 + bx^2 + cx + d
        func_type='rational': (a, b, c, d) → (ax + b) / (cx + d)
    - transform_type: 'abs_y' → y=|f(x)|,  'abs_x' → y=f(|x|)
    - show_original: True → vẽ f(x) nét đứt xám để so sánh
    Yêu cầu:
    - Đồ thị gốc f(x): nét đứt '#888888', lw=1.4
    - Đồ thị biến đổi: nét liền '#1A365D', lw=2.2
    - Với y=|f(x)|: phần âm được 'lật' lên, đánh dấu điểm gãy trên Ox bằng chấm tròn
    - Với y=f(|x|): phần x<0 là gương của x>0 qua trục Oy
    - Điểm gãy: chấm tròn đen ms=5
    """
    import numpy as np
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(7, 6), facecolor='white')
    x_min, x_max = xlim
    y_min, y_max = ylim

    x_full = np.linspace(x_min, x_max, 2000)

    def _f(x_arr):
        if func_type == 'cubic':
            a, b, c, d = coeffs
            return a * x_arr**3 + b * x_arr**2 + c * x_arr + d
        elif func_type == 'rational':
            a, b, c, d = coeffs
            denom = c * x_arr + d
            with np.errstate(divide='ignore', invalid='ignore'):
                result = np.where(np.abs(denom) > 1e-9,
                                  (a * x_arr + b) / denom,
                                  np.nan)
            return result
        else:
            raise ValueError(f"func_type khong hop le: {func_type}")

    y_orig = _f(x_full)

    def _clip(y):
        return np.where((y >= y_min) & (y <= y_max), y, np.nan)

    # --- Vẽ đồ thị gốc ---
    if show_original:
        ax.plot(x_full, _clip(y_orig),
                color='#888888', lw=1.4, ls='--', alpha=0.7,
                zorder=2, label='$f(x)$ goc')

    # --- Tính đồ thị biến đổi ---
    if transform_type == 'abs_y':
        y_trans = np.abs(y_orig)
        trans_label = r'$y = |f(x)|$'
        sign_changes = np.where(np.diff(np.sign(y_orig)))[0]
        break_xs = []
        for idx in sign_changes:
            if not (np.isnan(y_orig[idx]) or np.isnan(y_orig[idx + 1])):
                x0, x1 = x_full[idx], x_full[idx + 1]
                y0, y1 = y_orig[idx], y_orig[idx + 1]
                if abs(y1 - y0) > 1e-12:
                    xc = x0 - y0 * (x1 - x0) / (y1 - y0)
                    break_xs.append(xc)

    elif transform_type == 'abs_x':
        y_trans = _f(np.abs(x_full))
        trans_label = r'$y = f(|x|)$'
        break_xs = [0.0]
    else:
        raise ValueError(f"transform_type khong hop le: {transform_type}")

    ax.plot(x_full, _clip(y_trans),
            color='#1A365D', lw=2.2, zorder=3, label=trans_label)

    # Nhãn đồ thị biến đổi
    y_trans_clipped = _clip(y_trans)
    y_max_val = float(np.nanmax(y_trans_clipped)) if not np.all(np.isnan(y_trans_clipped)) else y_max
    mid_idx = len(x_full) // 2
    ax.text(x_full[mid_idx], y_max_val * 0.85,
            trans_label, fontsize=12, fontweight='bold',
            color='#1A365D', fontfamily='DejaVu Serif',
            ha='center', va='center',
            bbox=dict(boxstyle='square,pad=0.12', fc='white', ec='none'))

    # Đánh dấu điểm gãy
    for bx in break_xs:
        if transform_type == 'abs_y':
            by = float(np.abs(_f(np.array([bx]))[0]))
        else:
            by = float(_f(np.array([abs(bx)]))[0])
        if y_min <= by <= y_max:
            ax.plot(bx, by, 'ko', ms=5, zorder=5)

    # --- Trục toạ độ ---
    ax.spines[['top', 'right']].set_visible(False)
    ax.spines['left'].set_position('zero')
    ax.spines['bottom'].set_position('zero')
    ax.spines['left'].set_linewidth(1.1)
    ax.spines['bottom'].set_linewidth(1.1)
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)
    ax.set_xlabel('$x$', fontsize=13, fontweight='bold',
                  fontfamily='DejaVu Serif', loc='right')
    ax.set_ylabel('$y$', fontsize=13, fontweight='bold',
                  fontfamily='DejaVu Serif', loc='top', rotation=0)
    ax.plot(x_max, 0, '>k', ms=5, clip_on=False)
    ax.plot(0, y_max, '^k', ms=5, clip_on=False)
    ax.tick_params(labelsize=10)

    if show_original:
        ax.legend(fontsize=10, loc='best',
                  prop={'family': 'DejaVu Serif', 'size': 10})

    plt.tight_layout()
    plt.savefig(filename, dpi=DEFAULT_DPI, bbox_inches='tight', facecolor='white')
    plt.close()


# =============================================================================
# HÀM 3: plot_statistics_bar
# =============================================================================

def plot_statistics_bar(categories, values, filename,
                         bar_type='frequency',
                         show_polygon=False,
                         ylabel_override=None,
                         title=None,
                         color='#2B6CB0'):
    """
    Vẽ biểu đồ cột tần số / tần suất chuẩn SGK Toán 10 và KHTN.
    - categories : list nhãn trục Ox (VD: ['[10;15)', '[15;20)', '[20;25)'])
    - values     : list giá trị chiều cao cột tương ứng
    - bar_type   : 'frequency' (tần số n_i), 'relative' (tần suất f_i %), 'density' (mật độ)
    - show_polygon: True → vẽ đường gãy khúc (đa giác tần số/tần suất) màu đỏ
    - Mỗi cột ghi giá trị ở trên đỉnh (fontsize=11, ha='center')
    - Cột có viền đen mỏng (edgecolor='black', lw=0.8)
    """
    import numpy as np
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(max(6, len(categories) * 1.1), 5),
                           facecolor='white')

    n = len(categories)
    x_pos = np.arange(n)
    bar_width = 0.72

    bars = ax.bar(x_pos, values, width=bar_width,
                  color=color, edgecolor='black', linewidth=0.8,
                  zorder=3)

    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.015 * max(values),
                str(val), fontsize=11, fontweight='bold',
                ha='center', va='bottom',
                fontfamily='DejaVu Serif')

    if show_polygon:
        poly_x = np.concatenate([
            [x_pos[0] - bar_width / 2],
            x_pos,
            [x_pos[-1] + bar_width / 2]
        ])
        poly_y = np.concatenate([[0], values, [0]])
        ax.plot(poly_x, poly_y,
                color='#C53030', lw=2.0, marker='o', ms=5,
                zorder=4, label='Da giac tan so/tan suat')
        ax.legend(fontsize=10, prop={'family': 'DejaVu Serif', 'size': 10})

    ax.set_xticks(x_pos)
    ax.set_xticklabels(categories, fontsize=11,
                       fontfamily='DejaVu Serif', rotation=0)

    if ylabel_override:
        ylabel_str = ylabel_override
    elif bar_type == 'frequency':
        ylabel_str = 'Tan so ($n_i$)'
    elif bar_type == 'relative':
        ylabel_str = 'Tan suat (%)'
    else:
        ylabel_str = 'Mat do tan so'

    ax.set_ylabel(ylabel_str, fontsize=12, fontweight='bold',
                  fontfamily='DejaVu Serif')
    ax.set_xlabel('Gia tri / Lop', fontsize=12, fontweight='bold',
                  fontfamily='DejaVu Serif')

    if title:
        ax.set_title(title, fontsize=13, fontweight='bold',
                     fontfamily='DejaVu Serif', pad=8)

    ax.set_xlim(-0.5, n - 0.5)
    ax.set_ylim(0, max(values) * 1.18)
    ax.yaxis.grid(True, lw=0.6, alpha=0.5, zorder=0)
    ax.set_axisbelow(True)
    ax.spines[['top', 'right']].set_visible(False)
    ax.tick_params(axis='y', labelsize=10)

    plt.tight_layout()
    plt.savefig(filename, dpi=DEFAULT_DPI, bbox_inches='tight', facecolor='white')
    plt.close()


# =============================================================================
# HÀM 4: plot_pie_chart
# =============================================================================

def plot_pie_chart(labels, values, filename,
                   show_percent=True,
                   show_label=True,
                   explode=None,
                   title=None):
    """
    Vẽ biểu đồ hình quạt (pie chart) chuẩn SGK KHTN lớp 7, Toán 10.
    - labels      : list tên các phần (VD: ['Lua', 'Ngo', 'Khoai', 'Khac'])
    - values      : list giá trị (không cần tổng = 100, hàm tự tính %)
    - show_percent: True → hiện % trên mỗi múi
    - show_label  : True → hiện tên bên cạnh múi
    - explode     : list độ tách (VD: [0.05, 0, 0, 0]) hoặc None
    - Màu sắc xen kẽ rõ ràng, kèm hatch để in đen trắng
    """
    import matplotlib.pyplot as plt

    COLORS = ['#1A365D', '#4A90D9', '#C53030', '#F6AD55', '#68D391',
              '#B794F4', '#2D3748', '#9AE6B4', '#FEB2B2', '#BEE3F8']
    HATCHES = ['/', '\\\\', 'x', '.', 'o', '+', '-', '*', '//', '||']

    n = len(labels)
    colors_used = [COLORS[i % len(COLORS)] for i in range(n)]
    hatches_used = [HATCHES[i % len(HATCHES)] for i in range(n)]

    if explode is None:
        explode = [0] * n

    def _autopct(pct):
        return f'{pct:.1f}%' if show_percent else ''

    fig, ax = plt.subplots(figsize=(7, 6), facecolor='white')

    wedges, texts, autotexts = ax.pie(
        values,
        labels=labels if show_label else None,
        autopct=_autopct,
        explode=explode,
        colors=colors_used,
        startangle=90,
        pctdistance=0.68,
        labeldistance=1.12,
        wedgeprops=dict(linewidth=1.0, edgecolor='white')
    )

    for wedge, hatch in zip(wedges, hatches_used):
        wedge.set_hatch(hatch)

    for text in texts:
        text.set_fontsize(11)
        text.set_fontfamily('DejaVu Serif')
        text.set_fontweight('bold')
    for autotext in autotexts:
        autotext.set_fontsize(11)
        autotext.set_fontfamily('DejaVu Serif')
        autotext.set_fontweight('bold')
        autotext.set_color('white')

    if title:
        ax.set_title(title, fontsize=13, fontweight='bold',
                     fontfamily='DejaVu Serif', pad=10)

    ax.axis('equal')
    plt.tight_layout()
    plt.savefig(filename, dpi=DEFAULT_DPI, bbox_inches='tight', facecolor='white')
    plt.close()


# =============================================================================
# HÀM 5: plot_number_line_intervals
# =============================================================================

def plot_number_line_intervals(intervals, xlim, filename,
                                key_points=None,
                                labels=None,
                                title=None):
    """
    Vẽ trục số biểu diễn nghiệm bất phương trình / tập xác định
    chuẩn SGK lớp 8–12.
    - intervals : list of tuples (a, b, left_closed, right_closed)
      Dùng float('inf') / float('-inf') cho vô cực.
    - key_points: list giá trị đặc biệt bổ sung cần đánh dấu
    - labels    : list nhãn bổ sung tương ứng với các endpoint
    Yêu cầu:
    - Đoạn thuộc tập nghiệm: tô đậm nét dày (lw=3.5, màu '#1A365D')
    - Đầu mút đóng: chấm đặc tròn đen (ms=9)
    - Đầu mút mở: chấm rỗng (markerfacecolor='white', ms=9)
    - Mũi tên hai đầu trục số, nhãn +inf/-inf
    """
    import numpy as np
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(9, 2.2), facecolor='white')
    ax.set_aspect('auto')
    ax.axis('off')

    x_min, x_max = xlim
    margin = (x_max - x_min) * 0.06
    ax_x0 = x_min - margin
    ax_x1 = x_max + margin

    Y = 0.5

    ax.annotate('', xy=(ax_x1, Y), xytext=(ax_x0, Y),
                arrowprops=dict(arrowstyle='->', color='black',
                                lw=1.2, mutation_scale=14))

    ax.text(ax_x0 - margin * 0.3, Y, '$-\\infty$',
            fontsize=12, va='center', ha='right',
            fontfamily='DejaVu Serif')
    ax.text(ax_x1 + margin * 0.1, Y, '$+\\infty$',
            fontsize=12, va='center', ha='left',
            fontfamily='DejaVu Serif')

    all_endpoints = {}

    for (a, b, left_closed, right_closed) in intervals:
        a_draw = max(a, ax_x0) if not np.isinf(a) else ax_x0
        b_draw = min(b, ax_x1) if not np.isinf(b) else ax_x1

        ax.plot([a_draw, b_draw], [Y, Y],
                color='#1A365D', lw=3.5, solid_capstyle='butt', zorder=3)

        if not np.isinf(a):
            if left_closed:
                ax.plot(a, Y, 'ko', ms=9, zorder=5)
            else:
                ax.plot(a, Y, 'o', ms=9, zorder=5,
                        markerfacecolor='white',
                        markeredgecolor='black', markeredgewidth=1.5)
            all_endpoints[a] = left_closed

        if not np.isinf(b):
            if right_closed:
                ax.plot(b, Y, 'ko', ms=9, zorder=5)
            else:
                ax.plot(b, Y, 'o', ms=9, zorder=5,
                        markerfacecolor='white',
                        markeredgecolor='black', markeredgewidth=1.5)
            all_endpoints[b] = right_closed

    if key_points:
        for kp in key_points:
            ax.plot(kp, Y, 'o', ms=8, zorder=4,
                    markerfacecolor='white',
                    markeredgecolor='black', markeredgewidth=1.4)
            all_endpoints[kp] = False

    for val in sorted(all_endpoints.keys()):
        try:
            label_str = str(int(val)) if float(val) == int(val) else str(round(val, 4))
        except (ValueError, OverflowError):
            label_str = str(val)
        ax.text(val, Y - 0.28, label_str,
                fontsize=12, ha='center', va='top',
                fontfamily='DejaVu Serif', fontweight='bold')

    if labels:
        for i, val in enumerate(sorted(all_endpoints.keys())):
            if i < len(labels) and labels[i]:
                ax.text(val, Y + 0.32, labels[i],
                        fontsize=10, ha='center', va='bottom',
                        fontfamily='DejaVu Serif', color='#C53030')

    if title:
        ax.set_title(title, fontsize=12, fontweight='bold',
                     fontfamily='DejaVu Serif', pad=4)

    ax.set_xlim(ax_x0 - margin * 1.5, ax_x1 + margin * 1.5)
    ax.set_ylim(0, 1)

    plt.tight_layout()
    plt.savefig(filename, dpi=DEFAULT_DPI, bbox_inches='tight', facecolor='white')
    plt.close()


# =============================================================================
# HÀM 6: plot_2d_vectors
# =============================================================================

def plot_2d_vectors(vectors, filename,
                    xlim=None, ylim=None,
                    show_components=False,
                    show_resultant=False,
                    show_angle=False,
                    grid=False):
    """
    Vẽ hệ vectơ trong mặt phẳng Oxy — dùng cho bài tổng hợp lực,
    phân tích vectơ, phép cộng vectơ (lớp 10 Toán & Vật lý).
    - vectors: list of dict:
        {'origin': (ox, oy), 'dx': float, 'dy': float,
         'label': str, 'color': str, 'style': '-' or '--'}
    - show_components: True → vẽ thêm thành phần ngang/đứng nét đứt
    - show_resultant : True → vẽ vectơ tổng hợp (màu tím '#8E44AD')
    - show_angle     : True → vẽ cung góc giữa các vectơ và ghi số độ
    - Mũi tên vectơ: ax.annotate với arrowprops=dict(arrowstyle='->', lw=1.8)
    - Nhãn vectơ đặt ở đầu mũi tên, có bbox trắng chống đè
    """
    import numpy as np
    import matplotlib.pyplot as plt
    from matplotlib.patches import Arc

    fig, ax = plt.subplots(figsize=(7, 6), facecolor='white')

    all_x = []
    all_y = []
    for v in vectors:
        ox, oy = v.get('origin', (0, 0))
        dx, dy = v.get('dx', 0.0), v.get('dy', 0.0)
        all_x += [ox, ox + dx]
        all_y += [oy, oy + dy]

    x_span = max(all_x) - min(all_x)
    y_span = max(all_y) - min(all_y)
    pad = max(x_span * 0.25, y_span * 0.25, 0.5)

    if xlim is None:
        xlim = (min(all_x) - pad, max(all_x) + pad)
    if ylim is None:
        ylim = (min(all_y) - pad, max(all_y) + pad)

    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)

    ax.spines[['top', 'right']].set_visible(False)
    ax.spines['left'].set_position('zero')
    ax.spines['bottom'].set_position('zero')
    ax.spines['left'].set_linewidth(1.1)
    ax.spines['bottom'].set_linewidth(1.1)
    ax.set_xlabel('$x$', fontsize=13, fontweight='bold',
                  fontfamily='DejaVu Serif', loc='right')
    ax.set_ylabel('$y$', fontsize=13, fontweight='bold',
                  fontfamily='DejaVu Serif', loc='top', rotation=0)
    ax.plot(xlim[1], 0, '>k', ms=5, clip_on=False)
    ax.plot(0, ylim[1], '^k', ms=5, clip_on=False)

    if grid:
        ax.grid(True, lw=0.5, alpha=0.4, zorder=0)
    ax.tick_params(labelsize=10)
    ax.set_xticks([t for t in ax.get_xticks() if t != 0])
    ax.set_yticks([t for t in ax.get_yticks() if t != 0])

    default_colors = ['#1A365D', '#C53030', '#276749', '#744210', '#2C7A7B']
    for i, v in enumerate(vectors):
        ox, oy = v.get('origin', (0, 0))
        dx, dy = v.get('dx', 0.0), v.get('dy', 0.0)
        color = v.get('color', default_colors[i % len(default_colors)])
        style = v.get('style', '-')
        label = v.get('label', f'$\\vec{{v}}_{{{i+1}}}$')

        ax.annotate('',
                    xy=(ox + dx, oy + dy),
                    xytext=(ox, oy),
                    arrowprops=dict(
                        arrowstyle='->',
                        color=color,
                        lw=1.8,
                        linestyle=style,
                        mutation_scale=16
                    ),
                    zorder=4)

        ax.text(ox + dx + 0.05 * (xlim[1] - xlim[0]),
                oy + dy + 0.03 * (ylim[1] - ylim[0]),
                label,
                fontsize=12, fontweight='bold', color=color,
                fontfamily='DejaVu Serif',
                ha='left', va='bottom',
                bbox=dict(boxstyle='square,pad=0.12', fc='white', ec='none'))

        if show_components:
            ax.annotate('',
                        xy=(ox + dx, oy),
                        xytext=(ox, oy),
                        arrowprops=dict(arrowstyle='->', color=color,
                                        lw=1.0, linestyle='--',
                                        mutation_scale=10),
                        zorder=3)
            ax.annotate('',
                        xy=(ox + dx, oy + dy),
                        xytext=(ox + dx, oy),
                        arrowprops=dict(arrowstyle='->', color=color,
                                        lw=1.0, linestyle='--',
                                        mutation_scale=10),
                        zorder=3)
            ax.plot([ox + dx, ox + dx], [oy, oy + dy],
                    color=color, lw=0.9, ls=':', alpha=0.6)
            ax.plot([ox, ox + dx], [oy, oy],
                    color=color, lw=0.9, ls=':', alpha=0.6)

    if show_resultant and len(vectors) >= 2:
        ox_r = vectors[0].get('origin', (0, 0))[0]
        oy_r = vectors[0].get('origin', (0, 0))[1]
        sum_dx = sum(v.get('dx', 0) for v in vectors)
        sum_dy = sum(v.get('dy', 0) for v in vectors)

        ax.annotate('',
                    xy=(ox_r + sum_dx, oy_r + sum_dy),
                    xytext=(ox_r, oy_r),
                    arrowprops=dict(arrowstyle='->', color='#8E44AD',
                                    lw=2.2, mutation_scale=18),
                    zorder=5)
        ax.text(ox_r + sum_dx + 0.05 * (xlim[1] - xlim[0]),
                oy_r + sum_dy,
                r'$\vec{R}$ (tong hop)',
                fontsize=12, fontweight='bold', color='#8E44AD',
                fontfamily='DejaVu Serif',
                ha='left', va='center',
                bbox=dict(boxstyle='square,pad=0.12', fc='white', ec='none'))

    if show_angle and len(vectors) >= 2:
        for i in range(len(vectors) - 1):
            v1 = vectors[i]
            v2 = vectors[i + 1]
            ox, oy = v1.get('origin', (0, 0))
            dx1, dy1 = v1.get('dx', 1.0), v1.get('dy', 0.0)
            dx2, dy2 = v2.get('dx', 1.0), v2.get('dy', 0.0)

            ang1 = float(np.degrees(np.arctan2(dy1, dx1))) % 360
            ang2 = float(np.degrees(np.arctan2(dy2, dx2))) % 360

            ang_diff = abs(ang2 - ang1)
            if ang_diff > 180:
                ang_diff = 360 - ang_diff

            arc_r = min(abs(xlim[1] - xlim[0]), abs(ylim[1] - ylim[0])) * 0.12
            arc = Arc((ox, oy), 2 * arc_r, 2 * arc_r,
                      angle=0,
                      theta1=min(ang1, ang2),
                      theta2=max(ang1, ang2),
                      color='#555555', lw=1.2)
            ax.add_patch(arc)

            mid_ang = np.radians((ang1 + ang2) / 2)
            ax.text(ox + arc_r * 1.3 * np.cos(mid_ang),
                    oy + arc_r * 1.3 * np.sin(mid_ang),
                    f'${ang_diff:.0f}°$',
                    fontsize=10, color='#555555',
                    fontfamily='DejaVu Serif',
                    ha='center', va='center',
                    bbox=dict(boxstyle='square,pad=0.12', fc='white', ec='none'))

    plt.tight_layout()
    plt.savefig(filename, dpi=DEFAULT_DPI, bbox_inches='tight', facecolor='white')
    plt.close()


# ---------------------------------------------------------------------------
# HÀM 1: plot_function_comparison
# ---------------------------------------------------------------------------
def plot_function_comparison(f1_coeffs, f2_coeffs, xlim, ylim, filename,
                              shade_between=True, shade_color='#FED7D7',
                              intersection_pts=None,
                              labels=('$f(x)$', '$g(x)$')):
    """Vẽ 2 hàm số đa thức bậc <= 3 trên cùng hệ trục Oxy.

    Parameters
    ----------
    f1_coeffs, f2_coeffs : list
        Hệ số [a, b, c, d] tương ứng với a*x^3 + b*x^2 + c*x + d.
        Có thể truyền ít phần tử hơn (sẽ zero-pad bên trái).
    xlim, ylim : tuple (min, max)
    filename : str
    shade_between : bool
        Tô vùng kẹp giữa 2 đường.
    shade_color : str
    intersection_pts : list of (x, y) or None
    labels : tuple of 2 str
        Nhãn f1 và f2.
    """
    import numpy as np
    import matplotlib.pyplot as plt

    def _poly(coeffs, x):
        # Zero-pad về 4 phần tử [a, b, c, d]
        c = [0.0] * (4 - len(coeffs)) + list(coeffs)
        a, b, cc, d = c
        return a * x**3 + b * x**2 + cc * x + d

    fig, ax = plt.subplots(figsize=(6, 5))
    setup_axes(ax, xlim, ylim)

    x = np.linspace(xlim[0], xlim[1], 600)
    y1 = _poly(f1_coeffs, x)
    y2 = _poly(f2_coeffs, x)

    # Clip to ylim for clean display
    y1c = np.clip(y1, ylim[0] - 1, ylim[1] + 1)
    y2c = np.clip(y2, ylim[0] - 1, ylim[1] + 1)

    # Tô vùng
    if shade_between:
        ax.fill_between(x, y1c, y2c, color=shade_color, alpha=0.35)

    # Đường cong
    l1, = ax.plot(x, y1c, color='#1A365D', lw=2.2, label=labels[0])
    l2, = ax.plot(x, y2c, color='#C53030', lw=2.2, label=labels[1])

    # Nhãn đặt ở đầu đường
    bbox_style = dict(boxstyle='round,pad=0.2', fc='white', ec='none', alpha=0.85)
    for line, label in [(l1, labels[0]), (l2, labels[1])]:
        xd, yd = line.get_xdata(), line.get_ydata()
        # Tìm điểm cuối còn nằm trong ylim
        mask = (yd >= ylim[0]) & (yd <= ylim[1])
        if mask.any():
            idx = np.where(mask)[0][-1]
            ax.text(xd[idx], yd[idx], '  ' + label,
                    fontsize=12, fontweight='bold',
                    fontfamily='DejaVu Serif', color=line.get_color(),
                    va='center', bbox=bbox_style)

    # Giao điểm
    if intersection_pts:
        for (px, py) in intersection_pts:
            ax.plot(px, py, 'ko', ms=6, zorder=5)
            ax.annotate(f'({px:.4g}; {py:.4g})',
                        xy=(px, py), xytext=(6, 6), textcoords='offset points',
                        fontsize=10, fontfamily='DejaVu Serif', fontweight='bold')

    plt.tight_layout()
    plt.savefig(filename, dpi=DEFAULT_DPI, bbox_inches='tight', facecolor='white')
    plt.close()


# ---------------------------------------------------------------------------
# HÀM 2: plot_wave_superposition
# ---------------------------------------------------------------------------
def plot_wave_superposition(A1, A2, T, phi_diff, t_max, filename, show_labels=True):
    """Vẽ 2 dao động điều hòa thành phần và dao động tổng hợp.

    Parameters
    ----------
    A1, A2 : float  Biên độ thành phần (cm)
    T : float       Chu kỳ (s)
    phi_diff : float  Độ lệch pha u2 so với u1 (rad)
    t_max : float   Thời gian hiển thị (s)
    filename : str
    show_labels : bool
    """
    import numpy as np
    import matplotlib.pyplot as plt

    t = np.linspace(0, t_max, 2000)
    omega = 2 * np.pi / T
    u1 = A1 * np.cos(omega * t)
    u2 = A2 * np.cos(omega * t + phi_diff)
    u  = u1 + u2

    # Biên độ tổng hợp
    A_total = np.sqrt(A1**2 + A2**2 + 2 * A1 * A2 * np.cos(phi_diff))

    fig, ax = plt.subplots(figsize=(8, 3.5))

    ax.axhline(0, color='#AAAAAA', lw=0.8)
    ax.plot(t, u1, color='#1A365D', lw=1.6, ls='--', label=f'$u_1$ ($A_1={A1}$ cm)')
    ax.plot(t, u2, color='#C53030', lw=1.6, ls='--', label=f'$u_2$ ($A_2={A2}$ cm)')
    ax.plot(t, u,  color='#276749', lw=2.4, ls='-',  label='$u = u_1+u_2$')

    if show_labels:
        # Đánh dấu biên độ tổng hợp trên trục y
        ax.axhline( A_total, color='#276749', lw=0.8, ls=':')
        ax.axhline(-A_total, color='#276749', lw=0.8, ls=':')
        ax.text(-t_max * 0.01, A_total,
                f'$A={A_total:.3g}$ cm',
                fontsize=11, fontweight='bold', fontfamily='DejaVu Serif',
                color='#276749', ha='right', va='center',
                bbox=dict(boxstyle='round,pad=0.15', fc='white', ec='none'))

    ax.set_xlabel('$t$ (s)', fontsize=12, fontweight='bold', fontfamily='DejaVu Serif')
    ax.set_ylabel('$u$ (cm)', fontsize=12, fontweight='bold', fontfamily='DejaVu Serif')
    ax.legend(fontsize=10, loc='upper right',
              prop={'family': 'DejaVu Serif', 'size': 10})
    ax.spines[['top', 'right']].set_visible(False)
    ax.tick_params(labelsize=10)

    plt.tight_layout()
    plt.savefig(filename, dpi=DEFAULT_DPI, bbox_inches='tight', facecolor='white')
    plt.close()


# ---------------------------------------------------------------------------
# HÀM 3: plot_nuclear_decay
# ---------------------------------------------------------------------------
def plot_nuclear_decay(N0, half_life, t_max, filename,
                       show_halflife_marks=True, y_label='N(t)'):
    """Vẽ đồ thị phân rã hạt nhân N(t) = N0 * (1/2)^(t/T_half).

    Parameters
    ----------
    N0 : float          Số hạt nhân ban đầu
    half_life : float   Chu kỳ bán rã (cùng đơn vị t_max)
    t_max : float       Thời gian tối đa hiển thị
    filename : str
    show_halflife_marks : bool
        Vẽ đường gióng tại T_half, 2T_half, 3T_half, 4T_half
    y_label : str
    """
    import numpy as np
    import matplotlib.pyplot as plt

    t = np.linspace(0, t_max, 1000)
    N = N0 * (0.5) ** (t / half_life)

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(t, N, color='#1A365D', lw=2.4)

    # Đường gióng tại bội số của T_half
    marks_t  = [half_life * k for k in range(1, 5) if half_life * k <= t_max]
    marks_N  = [N0 * (0.5) ** k for k in range(1, 5) if half_life * k <= t_max]
    t_labels = ['0']
    t_ticks  = [0]
    N_ticks  = [N0]
    N_labels_str = ['$N_0$']

    denom_map = {1: '$N_0/2$', 2: '$N_0/4$', 3: '$N_0/8$', 4: '$N_0/16$'}
    t_sym_map = {1: '$T_{1/2}$', 2: '$2T_{1/2}$',
                  3: '$3T_{1/2}$', 4: '$4T_{1/2}$'}

    for k, (tk, Nk) in enumerate(zip(marks_t, marks_N), start=1):
        t_ticks.append(tk)
        t_labels.append(t_sym_map[k])
        N_ticks.append(Nk)
        N_labels_str.append(denom_map[k])
        if show_halflife_marks:
            ax.plot([tk, tk], [0, Nk], color='#888888', lw=1.0, ls='--')
            ax.plot([0, tk], [Nk, Nk], color='#888888', lw=1.0, ls='--')
            ax.plot(tk, Nk, 'o', color='#C53030', ms=5, zorder=5)

    ax.set_xticks(t_ticks)
    ax.set_xticklabels(t_labels, fontsize=11, fontfamily='DejaVu Serif')
    ax.set_yticks(N_ticks)
    ax.set_yticklabels(N_labels_str, fontsize=11, fontfamily='DejaVu Serif')

    ax.set_xlabel('$t$', fontsize=13, fontweight='bold', fontfamily='DejaVu Serif')
    ax.set_ylabel(y_label, fontsize=13, fontweight='bold', fontfamily='DejaVu Serif')
    ax.spines[['top', 'right']].set_visible(False)
    ax.set_xlim(0, t_max)
    ax.set_ylim(0, N0 * 1.05)

    plt.tight_layout()
    plt.savefig(filename, dpi=DEFAULT_DPI, bbox_inches='tight', facecolor='white')
    plt.close()


# ---------------------------------------------------------------------------
# HÀM 4: plot_conic_section
# ---------------------------------------------------------------------------
def plot_conic_section(conic_type, a, b, xlim, ylim, filename,
                       show_foci=True, show_asymptotes=True, show_vertices=True):
    """Vẽ elip hoặc hyperbol trên hệ trục Oxy.

    Parameters
    ----------
    conic_type : 'ellipse' | 'hyperbola'
    a, b : float  Bán trục (a theo x, b theo y)
    xlim, ylim : tuple (min, max)
    filename : str
    show_foci : bool
    show_asymptotes : bool  (chỉ áp dụng cho hyperbol)
    show_vertices : bool
    """
    import numpy as np
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(5.5, 4.5))
    setup_axes(ax, xlim, ylim)

    theta = np.linspace(0, 2 * np.pi, 800)

    if conic_type == 'ellipse':
        c = np.sqrt(abs(a**2 - b**2))
        xe = a * np.cos(theta)
        ye = b * np.sin(theta)
        ax.plot(xe, ye, color='#1A365D', lw=2.2)

        # Tiêu điểm
        if show_foci and c > 1e-9:
            foci_x = [-c, c] if a > b else [0, 0]
            foci_y = [0, 0]  if a > b else [-c, c]
            ax.plot(foci_x, foci_y, 'r.', ms=8, zorder=5)
            for fx, fy, lbl in zip(foci_x, foci_y,
                                    ['$F_1$', '$F_2$']):
                ax.annotate(lbl, (fx, fy), xytext=(5, 6),
                            textcoords='offset points',
                            fontsize=11, fontweight='bold',
                            fontfamily='DejaVu Serif', color='#C53030')

        # Đỉnh
        if show_vertices:
            vx = [-a, a, 0, 0]
            vy = [0, 0, -b, b]
            ax.plot(vx, vy, 'k.', ms=5, zorder=4)
            for vxi, vyi, lbl in zip(vx, vy,
                                      [f'$-{a:.4g}$', f'${a:.4g}$',
                                       f'$-{b:.4g}$', f'${b:.4g}$']):
                ax.annotate(lbl, (vxi, vyi), xytext=(-14, -14),
                            textcoords='offset points', fontsize=10,
                            fontfamily='DejaVu Serif')

    elif conic_type == 'hyperbola':
        c = np.sqrt(a**2 + b**2)
        # Nhánh phải và trái qua tham số hóa an toàn
        tt = np.linspace(-np.pi / 2 + 0.05, np.pi / 2 - 0.05, 500)
        xr = a / np.cos(tt)
        yr = b * np.tan(tt)
        xl = -xr

        # Clip
        mask_r = (yr >= ylim[0]) & (yr <= ylim[1]) & (xr >= xlim[0]) & (xr <= xlim[1])
        mask_l = (yr >= ylim[0]) & (yr <= ylim[1]) & (xl >= xlim[0]) & (xl <= xlim[1])

        if mask_r.any():
            ax.plot(xr[mask_r], yr[mask_r], color='#1A365D', lw=2.2)
        if mask_l.any():
            ax.plot(xl[mask_l], yr[mask_l], color='#1A365D', lw=2.2)

        # Tiệm cận
        if show_asymptotes:
            xas = np.array(xlim)
            ax.plot(xas,  (b / a) * xas, color='#888888', lw=1.2, ls='--',
                    label=f'$y=\\pm\\frac{{{b:.4g}}}{{{a:.4g}}}x$')
            ax.plot(xas, -(b / a) * xas, color='#888888', lw=1.2, ls='--')
            ax.legend(fontsize=10, loc='upper left',
                      prop={'family': 'DejaVu Serif', 'size': 10})

        # Tiêu điểm
        if show_foci:
            ax.plot([-c, c], [0, 0], 'r.', ms=8, zorder=5)
            for fx, lbl in [(-c, '$F_1$'), (c, '$F_2$')]:
                ax.annotate(lbl, (fx, 0), xytext=(5, 6),
                            textcoords='offset points',
                            fontsize=11, fontweight='bold',
                            fontfamily='DejaVu Serif', color='#C53030')

        # Đỉnh
        if show_vertices:
            ax.plot([-a, a], [0, 0], 'k.', ms=5, zorder=4)
            for vx, lbl in [(-a, f'$-{a:.4g}$'), (a, f'${a:.4g}$')]:
                ax.annotate(lbl, (vx, 0), xytext=(-14, -14),
                            textcoords='offset points', fontsize=10,
                            fontfamily='DejaVu Serif')

    plt.tight_layout()
    plt.savefig(filename, dpi=DEFAULT_DPI, bbox_inches='tight', facecolor='white')
    plt.close()


# ---------------------------------------------------------------------------
# HÀM 5: plot_projectile_motion
# ---------------------------------------------------------------------------
def plot_projectile_motion(v0, angle_deg, filename, g=10.0,
                           show_components=True, show_peak=True,
                           show_range=True):
    """Vẽ quỹ đạo ném xiên (vật lý phổ thông).

    Parameters
    ----------
    v0 : float          Tốc độ ban đầu (m/s)
    angle_deg : float   Góc ném so với phương ngang (độ)
    filename : str
    g : float           Gia tốc trọng trường (m/s^2)
    show_components : bool
        Vẽ v0x, v0y và cung góc alpha.
    show_peak : bool
        Đánh dấu đỉnh quỹ đạo + nhãn H.
    show_range : bool
        Nhãn tầm xa L dưới trục Ox.
    """
    import numpy as np
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches

    alpha = np.deg2rad(angle_deg)
    v0x = v0 * np.cos(alpha)
    v0y = v0 * np.sin(alpha)

    # Thời gian bay, tầm xa, độ cao cực đại
    t_flight = 2 * v0y / g
    L = v0x * t_flight
    H = v0y**2 / (2 * g)

    t = np.linspace(0, t_flight, 600)
    x = v0x * t
    y = v0y * t - 0.5 * g * t**2

    fig, ax = plt.subplots(figsize=(7.5, 4))

    # Quỹ đạo
    ax.plot(x, y, color='#1A365D', lw=2.2, zorder=3)

    # Vectơ v0
    scale = min(L, H * 2) * 0.25 if H > 0 else L * 0.15
    ax.annotate('', xy=(v0x / v0 * scale, v0y / v0 * scale),
                xytext=(0, 0),
                arrowprops=dict(arrowstyle='->', color='#C53030',
                                lw=2.0, mutation_scale=14))
    ax.text(v0x / v0 * scale * 1.05, v0y / v0 * scale * 1.05,
            r'$\vec{v}_0$', fontsize=12, fontweight='bold',
            fontfamily='DejaVu Serif', color='#C53030')

    if show_components:
        # v0x (ngang, nét đứt xanh lá)
        ax.annotate('', xy=(v0x / v0 * scale, 0),
                    xytext=(0, 0),
                    arrowprops=dict(arrowstyle='->', color='#27AE60',
                                    lw=1.6, linestyle='dashed',
                                    mutation_scale=12))
        ax.text(v0x / v0 * scale / 2, -H * 0.08,
                '$v_{0x}$', fontsize=11, fontweight='bold',
                fontfamily='DejaVu Serif', color='#27AE60', ha='center')
        # v0y (đứng, nét đứt vàng cam)
        ax.annotate('', xy=(0, v0y / v0 * scale),
                    xytext=(0, 0),
                    arrowprops=dict(arrowstyle='->', color='#F39C12',
                                    lw=1.6, linestyle='dashed',
                                    mutation_scale=12))
        ax.text(-L * 0.03, v0y / v0 * scale / 2,
                '$v_{0y}$', fontsize=11, fontweight='bold',
                fontfamily='DejaVu Serif', color='#F39C12', ha='right')

        # Cung góc alpha
        arc_r = scale * 0.55
        arc = mpatches.Arc((0, 0), arc_r, arc_r,
                            angle=0, theta1=0, theta2=angle_deg,
                            color='#555555', lw=1.2)
        ax.add_patch(arc)
        ax.text(arc_r * 0.55, arc_r * 0.12,
                f'$\\alpha={angle_deg:.4g}°$',
                fontsize=10, fontfamily='DejaVu Serif', color='#555555')

    # Đỉnh quỹ đạo
    t_peak = v0y / g
    x_peak = v0x * t_peak
    if show_peak:
        ax.plot(x_peak, H, 'ko', ms=5, zorder=5)
        ax.annotate(f'$H = {H:.4g}$ m',
                    xy=(x_peak, H), xytext=(6, 6),
                    textcoords='offset points',
                    fontsize=11, fontweight='bold', fontfamily='DejaVu Serif',
                    bbox=dict(boxstyle='round,pad=0.2', fc='white', ec='none'))

    # Tầm xa
    if show_range:
        ax.annotate('', xy=(L, 0), xytext=(0, 0),
                    arrowprops=dict(arrowstyle='<->', color='#555555', lw=1.0))
        ax.text(L / 2, -H * 0.15,
                f'$L = {L:.4g}$ m',
                fontsize=11, fontweight='bold', fontfamily='DejaVu Serif',
                ha='center', va='top',
                bbox=dict(boxstyle='round,pad=0.2', fc='white', ec='none'))

    ax.set_xlim(-L * 0.05, L * 1.1)
    ax.set_ylim(-H * 0.25, H * 1.3)
    ax.axhline(0, color='#333333', lw=1.0)
    ax.axvline(0, color='#333333', lw=1.0)
    ax.set_xlabel('$x$ (m)', fontsize=12, fontweight='bold', fontfamily='DejaVu Serif')
    ax.set_ylabel('$y$ (m)', fontsize=12, fontweight='bold', fontfamily='DejaVu Serif')
    ax.spines[['top', 'right']].set_visible(False)

    plt.tight_layout()
    plt.savefig(filename, dpi=DEFAULT_DPI, bbox_inches='tight', facecolor='white')
    plt.close()


# ═══════════════════════════════════════════════════════════════════════════════
# NHÓM BỔ SUNG — HÌNH HỌC NÂNG CAO, TÍCH PHÂN RIEMANN & VẬT LÝ NÂNG CAO
# ═══════════════════════════════════════════════════════════════════════════════

def plot_integral_riemann_sum(func_type, coeffs, a, b, n_rects, filename, riemann_type='left', xlim=None, ylim=None):
    """
    Minh họa định nghĩa tích phân bằng tổng Riemann (các hình chữ nhật xấp xỉ diện tích dưới đường cong - SGK Toán 12 mới).
    - func_type: 'poly' (đa thức đa hệ số)
    - a, b: cận tích phân
    - n_rects: số hình chữ nhật (VD: 5, 8, 10)
    - riemann_type: 'left' (mép trái), 'right' (mép phải), hoặc 'mid' (trung điểm)
    - Đường cong f(x): màu '#1A365D', lw=2.3
    - Cột chữ nhật: màu '#BEE3F8', viền '#2B6CB0', lw=1.2, alpha=0.65
    - Ghi nhãn tích phân xấp xỉ S và đánh dấu mốc chia x_0, ..., x_n
    """
    apply_sgk_style()
    fig, ax = plt.subplots(figsize=(7.5, 4.8), dpi=DEFAULT_DPI)

    # Hàm số f(x)
    if callable(func_type):
        f = func_type
    elif callable(coeffs):
        f = coeffs
    elif func_type == 'poly':
        f = lambda x: np.polyval(coeffs, x)
    else:
        f = lambda x: np.polyval(coeffs, x)

    # Tính toán các hình chữ nhật Riemann
    dx = (b - a) / float(n_rects)
    x_edges = np.linspace(a, b, n_rects + 1)
    
    rect_x = []
    rect_h = []
    for i in range(n_rects):
        x_left = x_edges[i]
        if riemann_type == 'left':
            x_sample = x_left
        elif riemann_type == 'right':
            x_sample = x_edges[i + 1]
        elif riemann_type in ('mid', 'midpoint'):
            x_sample = x_left + 0.5 * dx
        else:
            x_sample = x_left
        h = float(f(x_sample))
        rect_x.append(x_left)
        rect_h.append(h)

    # Vẽ các cột hình chữ nhật
    for x_l, h in zip(rect_x, rect_h):
        ax.bar(x_l, h, width=dx, align='edge',
               facecolor='#BEE3F8', edgecolor='#2B6CB0',
               linewidth=1.2, alpha=0.65, zorder=2)

    # Tính tổng Riemann S
    S_approx = sum(h * dx for h in rect_h)

    # Trục xlim, ylim
    pad_x = max(0.6, abs(b - a) * 0.25)
    if xlim is None:
        xlim = (a - pad_x, b + pad_x)

    x_dense = np.linspace(xlim[0], xlim[1], 400)
    y_dense = f(x_dense)

    y_min_val = min(0.0, float(np.min(y_dense)), min(rect_h))
    y_max_val = max(0.0, float(np.max(y_dense)), max(rect_h))
    pad_y = max(1.0, (y_max_val - y_min_val) * 0.25)
    if ylim is None:
        ylim = (y_min_val - pad_y * 0.4, y_max_val + pad_y)

    # Vẽ đường cong f(x)
    ax.plot(x_dense, y_dense, color='#1A365D', lw=2.3, zorder=4, label='$y = f(x)$')

    # Trục tọa độ Oxy
    ax.axhline(0, color='black', lw=1.3, zorder=3)
    ax.axvline(0, color='black', lw=1.3, zorder=3)

    # Mũi tên Ox, Oy
    dx_axis = xlim[1] - xlim[0]
    dy_axis = ylim[1] - ylim[0]
    ax.annotate('', xy=(xlim[1], 0), xytext=(xlim[1] - 0.04 * dx_axis, 0),
                arrowprops=dict(arrowstyle='-|> ', color='black', lw=1.3, mutation_scale=12), zorder=5)
    ax.text(xlim[1] - 0.02 * dx_axis, -0.06 * dy_axis, '$x$',
            fontsize=13, fontweight='bold', fontstyle='italic', ha='left', va='top')

    ax.annotate('', xy=(0, ylim[1]), xytext=(0, ylim[1] - 0.04 * dy_axis),
                arrowprops=dict(arrowstyle='-|> ', color='black', lw=1.3, mutation_scale=12), zorder=5)
    ax.text(0.02 * dx_axis, ylim[1] - 0.02 * dy_axis, '$y$',
            fontsize=13, fontweight='bold', fontstyle='italic', ha='left', va='center')
    ax.text(-0.03 * dx_axis, -0.05 * dy_axis, '$O$',
            fontsize=12, fontweight='bold', fontstyle='italic', ha='right', va='top')

    # Đánh dấu các mốc chia x_0, x_1, ..., x_n trên trục hoành
    w_box = dict(boxstyle='square,pad=0.10', fc='white', ec='none')
    tick_len = 0.02 * dy_axis
    for i, x_i in enumerate(x_edges):
        ax.plot([x_i, x_i], [-tick_len, tick_len], color='black', lw=1.2, zorder=5)
        if i == 0:
            lbl = f'$x_0=a$'
        elif i == n_rects:
            lbl = f'$x_{{{n_rects}}}=b$'
        else:
            lbl = f'$x_{{{i}}}$'
        y_offset = -0.07 * dy_axis if (i % 2 == 0 or n_rects <= 5) else -0.13 * dy_axis
        # Nếu mốc x_0 trùng sát gốc tọa độ thì dịch xuống để không đè vào chữ O
        if abs(x_i) < 0.08 * dx_axis and i == 0:
            y_offset = -0.12 * dy_axis
        ax.text(x_i, y_offset, lbl, fontsize=12, fontweight='bold',
                ha='center', va='top', bbox=w_box, zorder=6)

    # Ghi nhãn diện tích tích phân đậm rõ nét: \mathbf{\int}_a^b f(x)dx \approx S
    riemann_type_str = {
        'left': 'trái (Left-sum)',
        'right': 'phải (Right-sum)',
        'mid': 'trung điểm (Midpoint-sum)'
    }.get(riemann_type, riemann_type)

    label_box = (
        rf'$\mathbf{{\int}}_{{{a:g}}}^{{{b:g}}} f(x)\,dx \approx S \approx {S_approx:.3f}$' + '\n' +
        f'($n={n_rects}$, tổng {riemann_type_str})'
    )
    ax.text(0.04, 0.94, label_box, transform=ax.transAxes,
            fontsize=13, fontweight='bold',
            ha='left', va='top',
            bbox=dict(boxstyle='round,pad=0.4', fc='white', ec='#2B6CB0', lw=1.4),
            zorder=7)

    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    ax.axis('off')

    plt.tight_layout()
    plt.savefig(filename, dpi=DEFAULT_DPI, bbox_inches='tight', facecolor='white')
    plt.close()


def plot_electric_field_lines(q1_pos, q1_val, q2_pos, q2_val, filename, grid_size=4.0):
    """
    Vẽ đường sức điện trường của 2 điện tích điểm (cùng dấu hoặc trái dấu) trong không gian phẳng 2D (Vật lý 11).
    - q1_val, q2_val: giá trị điện tích (dương > 0, âm < 0)
    - q1_pos, q2_pos: vị trí tọa độ tuple (x, y)
    - Dùng streamplot vẽ đường sức mượt mà lw=1.3, color='#2B6CB0'
    - Điện tích dương tô đỏ '#E53E3E', có dấu '+'; âm tô xanh '#3182CE', có dấu '-'
    - Bán kính điện tích = 0.25, viền đen
    """
    apply_sgk_style()
    fig, ax = plt.subplots(figsize=(6.0, 5.8), dpi=DEFAULT_DPI)

    # Lưới tọa độ tính điện trường
    res = 220
    x = np.linspace(-grid_size, grid_size, res)
    y = np.linspace(-grid_size, grid_size, res)
    X, Y = np.meshgrid(x, y)

    # Điện trường E do 2 điện tích điểm
    x1, y1 = q1_pos
    x2, y2 = q2_pos

    dx1 = X - x1
    dy1 = Y - y1
    r1 = np.hypot(dx1, dy1)
    # Tránh chia cho 0 bên trong lõi hạt
    r1_reg = np.maximum(r1, 0.12)
    Ex1 = q1_val * dx1 / (r1_reg ** 3)
    Ey1 = q1_val * dy1 / (r1_reg ** 3)

    dx2 = X - x2
    dy2 = Y - y2
    r2 = np.hypot(dx2, dy2)
    r2_reg = np.maximum(r2, 0.12)
    Ex2 = q2_val * dx2 / (r2_reg ** 3)
    Ey2 = q2_val * dy2 / (r2_reg ** 3)

    Ex = Ex1 + Ex2
    Ey = Ey1 + Ey2

    # Vẽ đường sức điện trường bằng streamplot
    ax.streamplot(X, Y, Ex, Ey, color='#2B6CB0', linewidth=1.3,
                  density=1.3, arrowsize=1.2, arrowstyle='->', zorder=2)

    # Vẽ các điện tích tròn
    w_box = dict(boxstyle='square,pad=0.12', fc='white', ec='none')
    charges = [
        (q1_pos, q1_val, '$q_1$'),
        (q2_pos, q2_val, '$q_2$')
    ]
    for pos, val, name in charges:
        fc = '#E53E3E' if val > 0 else '#3182CE'
        sign = '+' if val > 0 else '-'
        circle = plt.Circle(pos, radius=0.25, facecolor=fc, edgecolor='black', lw=1.5, zorder=5)
        ax.add_patch(circle)
        ax.text(pos[0], pos[1], sign, color='white', fontsize=14,
                fontweight='bold', fontfamily='DejaVu Serif',
                ha='center', va='center', zorder=6)
        # Nhãn điện tích
        val_str = f'{val:+g}'
        ax.text(pos[0], pos[1] - 0.45, f'{name} ({val_str})',
                fontsize=11, fontweight='bold', fontfamily='DejaVu Serif',
                ha='center', va='top', bbox=w_box, zorder=6)

    ax.set_xlim(-grid_size, grid_size)
    ax.set_ylim(-grid_size, grid_size)
    ax.set_aspect('equal')
    ax.set_xlabel('$x$ (m)', fontsize=12, fontweight='bold', fontfamily='DejaVu Serif')
    ax.set_ylabel('$y$ (m)', fontsize=12, fontweight='bold', fontfamily='DejaVu Serif')
    ax.set_title('Đường sức điện trường của hai điện tích điểm',
                 fontsize=12, fontweight='bold', fontfamily='DejaVu Serif', pad=12)
    ax.grid(True, linestyle=':', alpha=0.35, color='#718096')

    plt.tight_layout()
    plt.savefig(filename, dpi=DEFAULT_DPI, bbox_inches='tight', facecolor='white')
    plt.close()


def plot_magnetic_lorentz_force(filename, v_dir='right', b_dir='into_page', charge_type='positive'):
    """
    Minh họa quy tắc bàn tay trái xác định lực Lorentz tác dụng lên điện tích chuyển động trong từ trường (Vật lý 11).
    - b_dir: 'into_page' (otimes), 'out_of_page' (odot), hoặc 'up'
    - v_dir: 'right', 'left', 'up', 'down'
    - charge_type: 'positive' (q > 0) hoặc 'negative' (q < 0)
    - Lưới từ trường B làm nền
    - Hạt mang điện: đỏ (+) hoặc xanh (-)
    - Vectơ v: '#27AE60', mũi tên đậm, nhãn v
    - Vectơ f: '#C53030', mũi tên đậm, vuông góc với v, nhãn f
    - Ký hiệu góc vuông giữa v và f
    """
    apply_sgk_style()
    fig, ax = plt.subplots(figsize=(6.0, 5.2), dpi=DEFAULT_DPI)
    w_box = dict(boxstyle='square,pad=0.12', fc='white', ec='none')

    is_positive = charge_type in ('positive', '+', 'pos')
    q_sign = 1 if is_positive else -1

    # Nền từ trường B
    if b_dir in ('into_page', 'out_of_page'):
        symbol = r'$\otimes$' if b_dir == 'into_page' else r'$\odot$'
        xs = np.linspace(-2.4, 2.4, 7)
        ys = np.linspace(-2.0, 2.0, 6)
        for gx in xs:
            for gy in ys:
                if np.hypot(gx, gy) > 0.45:
                    ax.text(gx, gy, symbol, color='#A0AEC0', fontsize=17,
                            ha='center', va='center', zorder=1)
        b_label = r'$\vec{B} \otimes$' if b_dir == 'into_page' else r'$\vec{B} \odot$'
        b_desc = 'hướng vào trong' if b_dir == 'into_page' else 'hướng ra ngoài'
        ax.text(2.3, 2.2, f'{b_label} ({b_desc})',
                fontsize=11, fontweight='bold', fontfamily='DejaVu Serif', color='#2B6CB0',
                ha='right', va='center',
                bbox=dict(boxstyle='round,pad=0.3', fc='white', ec='#2B6CB0', lw=1.2),
                zorder=7)
    elif b_dir == 'up':
        for gx in np.linspace(-2.4, 2.4, 7):
            ax.annotate('', xy=(gx, 2.2), xytext=(gx, -2.2),
                        arrowprops=dict(arrowstyle='-|>', color='#CBD5E0', lw=1.3, mutation_scale=12),
                        zorder=1)
        ax.text(2.3, 2.2, r'$\vec{B}$ (hướng lên)',
                fontsize=11, fontweight='bold', fontfamily='DejaVu Serif', color='#2B6CB0',
                ha='right', va='center',
                bbox=dict(boxstyle='round,pad=0.3', fc='white', ec='#2B6CB0', lw=1.2),
                zorder=7)

    # Xác định vectơ vận tốc v
    v_len = 1.8
    if v_dir == 'right':
        uv = np.array([1.0, 0.0])
    elif v_dir == 'left':
        uv = np.array([-1.0, 0.0])
    elif v_dir == 'up':
        uv = np.array([0.0, 1.0])
    elif v_dir == 'down':
        uv = np.array([0.0, -1.0])
    else:
        uv = np.array([1.0, 0.0])

    vec_v = uv * v_len

    # Xác định vectơ lực Lorentz f: f = q * (v x B)
    if b_dir == 'into_page':
        uf_geom = np.array([-uv[1], uv[0]])
        uf = q_sign * uf_geom
    elif b_dir == 'out_of_page':
        uf_geom = np.array([uv[1], -uv[0]])
        uf = q_sign * uf_geom
    else:  # b_dir == 'up'
        uf = np.array([-uv[1], uv[0]]) * q_sign

    f_len = 1.8
    vec_f = uf * f_len

    # Vẽ vectơ v (màu xanh lá)
    ax.annotate('', xy=(vec_v[0], vec_v[1]), xytext=(0, 0),
                arrowprops=dict(arrowstyle='-|>', color='#27AE60', lw=2.4, mutation_scale=16),
                zorder=4)
    v_text_pos = vec_v + 0.28 * uv
    ax.text(v_text_pos[0], v_text_pos[1], r'$\vec{v}$',
            fontsize=13, fontweight='bold', fontfamily='DejaVu Serif', color='#27AE60',
            ha='center', va='center', bbox=w_box, zorder=6)

    # Vẽ vectơ f (màu đỏ)
    ax.annotate('', xy=(vec_f[0], vec_f[1]), xytext=(0, 0),
                arrowprops=dict(arrowstyle='-|>', color='#C53030', lw=2.4, mutation_scale=16),
                zorder=4)
    f_text_pos = vec_f + 0.28 * uf
    ax.text(f_text_pos[0], f_text_pos[1], r'$\vec{f}$',
            fontsize=13, fontweight='bold', fontfamily='DejaVu Serif', color='#C53030',
            ha='center', va='center', bbox=w_box, zorder=6)

    # Ký hiệu góc vuông giữa v và f
    sq_size = 0.28
    corner = sq_size * (uv + uf)
    pt1 = sq_size * uv
    pt2 = sq_size * uf
    ax.plot([pt1[0], corner[0], pt2[0]], [pt1[1], corner[1], pt2[1]],
            color='black', lw=1.3, zorder=4)
    center_sq = 0.5 * corner
    ax.plot(center_sq[0], center_sq[1], 'ko', markersize=2.2, zorder=4)

    # Vẽ hạt mang điện ở gốc (0, 0)
    charge_color = '#E53E3E' if is_positive else '#3182CE'
    circle = plt.Circle((0, 0), radius=0.25, facecolor=charge_color, edgecolor='black', lw=1.6, zorder=5)
    ax.add_patch(circle)
    sign_text = '+' if is_positive else '-'
    ax.text(0, 0, sign_text, color='white', fontsize=16, fontweight='bold',
            ha='center', va='center', zorder=6)

    # Nhãn điện tích q
    q_label = r'$q > 0$' if is_positive else r'$q < 0$'
    uq = -0.5 * (uv + uf)
    if np.linalg.norm(uq) > 1e-4:
        uq = uq / np.linalg.norm(uq)
    else:
        uq = np.array([-1.0, -1.0]) / np.sqrt(2)
    q_pos = 0.55 * uq
    ax.text(q_pos[0], q_pos[1], q_label,
            fontsize=11, fontweight='bold', fontfamily='DejaVu Serif',
            ha='center', va='center', bbox=w_box, zorder=6)

    ax.set_xlim(-2.8, 2.8)
    ax.set_ylim(-2.5, 2.5)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title(r'Lực Lorentz tác dụng lên điện tích: $\vec{f} = q(\vec{v} \times \vec{B})$',
                 fontsize=12, fontweight='bold', fontfamily='DejaVu Serif', pad=12)

    plt.tight_layout()
    plt.savefig(filename, dpi=DEFAULT_DPI, bbox_inches='tight', facecolor='white')
    plt.close()


def plot_polar_graph(curve_type, a, filename, title=None):
    """
    Vẽ đồ thị tọa độ cực r = f(theta) (Toán nâng cao / hình học giải tích).
    - curve_type: 'circle' (r = a), 'rose_4' (r = a*cos(2*theta)), 'cardioid' (r = a*(1 + cos(theta)))
    - Subplot với projection='polar'
    - Đường cong màu '#1A365D', lw=2.2
    - Lưới cực r, theta rõ ràng, các góc chia nhãn 0, pi/4, pi/2, ...
    - Tiêu đề hình vẽ rõ ràng
    """
    apply_sgk_style()
    fig, ax = plt.subplots(figsize=(6.0, 6.0), subplot_kw=dict(projection='polar'), dpi=DEFAULT_DPI)

    theta = np.linspace(0, 2 * np.pi, 1000)

    if curve_type == 'circle':
        r = np.full_like(theta, float(a))
        formula = f'$r = {a:g}$'
        default_title = f'Đồ thị tọa độ cực: Đường tròn $r = {a:g}$'
    elif curve_type == 'rose_4':
        r = a * np.cos(2 * theta)
        formula = rf'$r = {a:g}\cos(2\theta)$'
        default_title = rf'Đồ thị cực: Hoa bốn cánh $r = {a:g}\cos(2\theta)$'
    elif curve_type == 'cardioid':
        r = a * (1 + np.cos(theta))
        formula = rf'$r = {a:g}(1 + \cos\theta)$'
        default_title = rf'Đồ thị cực: Hình tim (Cardioid) $r = {a:g}(1 + \cos\theta)$'
    else:
        r = np.full_like(theta, float(a))
        formula = f'$r = {a:g}$'
        default_title = f'Đồ thị tọa độ cực $r = {a:g}$'

    # Vẽ đường cong tọa độ cực
    ax.plot(theta, r, color='#1A365D', lw=2.2, label=formula, zorder=3)
    ax.fill(theta, np.maximum(r, 0), color='#BEE3F8', alpha=0.3, zorder=2)

    # Chia nhãn các góc chuẩn pi/4, pi/2, ...
    angles = np.linspace(0, 2 * np.pi, 8, endpoint=False)
    angle_labels = ['0', r'$\frac{\pi}{4}$', r'$\frac{\pi}{2}$', r'$\frac{3\pi}{4}$',
                    r'$\pi$', r'$\frac{5\pi}{4}$', r'$\frac{3\pi}{2}$', r'$\frac{7\pi}{4}$']
    ax.set_xticks(angles)
    ax.set_xticklabels(angle_labels, fontsize=11, fontweight='bold', fontfamily='DejaVu Serif')

    # Lưới cực
    ax.grid(True, linestyle='--', color='#CBD5E0', alpha=0.8)
    ax.tick_params(axis='y', labelsize=10)

    fig_title = title if title is not None else default_title
    ax.set_title(fig_title, fontsize=12, fontweight='bold', fontfamily='DejaVu Serif', pad=18)
    ax.legend(loc='upper right', bbox_to_anchor=(1.18, 1.12), fontsize=11)

    plt.tight_layout()
    plt.savefig(filename, dpi=DEFAULT_DPI, bbox_inches='tight', facecolor='white')
    plt.close()


def plot_3d_cross_section_pyramid(filename, cut_ratio=0.5):
    """
    Vẽ hình chóp có mặt phẳng cắt tạo thiết diện (SGK Toán 11 Hình học không gian).
    - Đáy chóp: tứ giác ABCD. Đỉnh S.
    - Mặt phẳng cắt song song đáy ở độ cao tỉ lệ cut_ratio (0.5 = ở giữa), tạo thiết diện MNPQ.
    - Tô màu thiết diện MNPQ bằng màu xanh cyan/blue với độ mờ alpha=0.35.
    - Cạnh thấy nét liền lw=1.6, cạnh khuất (đáy và đường cao) vẽ nét đứt lw=1.2.
    - Đỉnh S, A, B, C, D, M, N, P, Q có nhãn chữ rõ ràng với bbox trắng.
    """
    apply_sgk_style()
    fig, ax = plt.subplots(figsize=(5.2, 5.6), dpi=DEFAULT_DPI)
    w_box = dict(boxstyle='square,pad=0.12', fc='white', ec='none')

    # Tọa độ các đỉnh đáy ABCD (hình bình hành trong phép chiếu song song)
    A = np.array([1.2, 1.4])
    B = np.array([0.4, 0.4])
    C = np.array([3.6, 0.4])
    D = np.array([4.4, 1.4])

    # Đỉnh S (đường cao SA vuông góc với đáy)
    S = np.array([1.2, 4.4])

    # Thiết diện MNPQ song song với đáy ở độ cao tỉ lệ k = cut_ratio
    k = float(cut_ratio)
    k = max(0.05, min(0.95, k))
    M = (1.0 - k) * A + k * S
    N = (1.0 - k) * B + k * S
    P = (1.0 - k) * C + k * S
    Q = (1.0 - k) * D + k * S

    # Tô màu thiết diện MNPQ
    sec_poly = plt.Polygon([M, N, P, Q], facecolor='#63B3ED', edgecolor='none', alpha=0.35, zorder=2)
    ax.add_patch(sec_poly)

    # Cạnh khuất của hình chóp (đáy AB, AD và đường cao SA) - nét đứt lw=1.2
    ax.plot([A[0], B[0]], [A[1], B[1]], 'k--', lw=1.2, zorder=3)
    ax.plot([A[0], D[0]], [A[1], D[1]], 'k--', lw=1.2, zorder=3)
    ax.plot([S[0], A[0]], [S[1], A[1]], 'k--', lw=1.2, zorder=3)

    # Cạnh thấy của hình chóp - nét liền lw=1.6
    ax.plot([B[0], C[0]], [B[1], C[1]], 'k-', lw=1.6, zorder=3)
    ax.plot([C[0], D[0]], [C[1], D[1]], 'k-', lw=1.6, zorder=3)
    ax.plot([S[0], B[0]], [S[1], B[1]], 'k-', lw=1.6, zorder=3)
    ax.plot([S[0], C[0]], [S[1], C[1]], 'k-', lw=1.6, zorder=3)
    ax.plot([S[0], D[0]], [S[1], D[1]], 'k-', lw=1.6, zorder=3)

    # Viền thiết diện MNPQ:
    # NP, PQ nằm trên các mặt thấy (SBC, SCD) -> nét liền
    # MN, MQ nằm trên các mặt khuất (SAB, SAD) -> nét đứt
    ax.plot([N[0], P[0]], [N[1], P[1]], color='#2B6CB0', linestyle='-', lw=1.6, zorder=4)
    ax.plot([P[0], Q[0]], [P[1], Q[1]], color='#2B6CB0', linestyle='-', lw=1.6, zorder=4)
    ax.plot([M[0], N[0]], [M[1], N[1]], color='#2B6CB0', linestyle='--', lw=1.2, zorder=4)
    ax.plot([M[0], Q[0]], [M[1], Q[1]], color='#2B6CB0', linestyle='--', lw=1.2, zorder=4)

    # Đánh dấu và ghi nhãn các đỉnh
    vertices = [
        ('S', S, (0, 10)),
        ('A', A, (-14, 4)),
        ('B', B, (-14, -8)),
        ('C', C, (8, -8)),
        ('D', D, (10, 4)),
        ('M', M, (-14, 4)),
        ('N', N, (-14, -4)),
        ('P', P, (10, -4)),
        ('Q', Q, (10, 4))
    ]
    for name, pt, offset in vertices:
        ax.plot(pt[0], pt[1], 'ko', markersize=3.8, zorder=5)
        ax.annotate(name, xy=pt, xytext=offset, textcoords='offset points',
                    fontsize=12, fontweight='bold', fontfamily='DejaVu Serif',
                    bbox=w_box, zorder=6)

    ax.set_xlim(-0.3, 5.0)
    ax.set_ylim(-0.3, 4.9)
    ax.set_aspect('equal')
    ax.axis('off')

    plt.tight_layout()
    plt.savefig(filename, dpi=DEFAULT_DPI, bbox_inches='tight', facecolor='white')
    plt.close()
