#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script Kiểm Tra Chất Lượng Hình Vẽ — render_math_figures.py
Chạy toàn bộ hàm vẽ với tham số mẫu → xuất ảnh PNG vào thư mục test_output/
Dùng để xác minh hình vẽ chuẩn xác trước khi tích hợp vào đề thi.

Chạy: python test_figures.py
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

import numpy as np
from pathlib import Path

OUT = Path(__file__).parent / "test_output_figures"
OUT.mkdir(exist_ok=True)

PASS = []
FAIL = []

def test(name, fn):
    try:
        fn()
        size = (OUT / f"{name}.png").stat().st_size
        print(f"  [PASS] {name} ({size//1024} KB)")
        PASS.append(name)
    except Exception as e:
        print(f"  [FAIL] {name}: {e}")
        FAIL.append(name)

try:
    from render_math_figures import (
        plot_cubic_function, plot_rational_1_1,
        plot_bounded_interval_extrema, draw_full_border_bbt,
        draw_bbt_sgk,
        plot_harmonic_oscillation, plot_thin_lens_optics,
        plot_pyramid_s_abcd, plot_chemistry_energy_diagram,
        plot_ph_titration_curve,
    )
except ImportError as e:
    print(f"[Lỗi] Không import được render_math_figures: {e}")
    sys.exit(1)


print("\n" + "="*60)
print("KIỂM TRA HÀM VẼ MATPLOTLIB — render_math_figures.py")
print("="*60)

# ── TOÁN ──────────────────────────────────────────────────────────────────────

print("\n[TOÁN — Hàm số]")

test("ham_bac_3_basic",
    lambda: plot_cubic_function(1, 0, -3, 0, (-2.5, 2.5), (-5, 5),
                                str(OUT / "ham_bac_3_basic.png"),
                                marked_points=[(1, -2, '1', '-2'), (-1, 2, '-1', '2')]))

test("ham_phan_thuc",
    lambda: plot_rational_1_1(2, 1, 1, -1, (-4, 6), (-6, 8),
                              str(OUT / "ham_phan_thuc.png"),
                              marked_points=[(0, -1, '0', '-1')]))

test("ham_tren_doan_kin",
    lambda: plot_bounded_interval_extrema(
        [0, 1, 2, 3], [0, 2, 1, 4], [3, 0, 0, 3],
        (0, 3), (-0.5, 5),
        str(OUT / "ham_tren_doan_kin.png"),
        endpoints=[{'x': 0, 'y': 0, 'xl': '0', 'yl': '0'},
                   {'x': 3, 'y': 4, 'xl': '3', 'yl': '4'}],
        extrema=[{'x': 1, 'y': 2, 'xl': '1', 'yl': '2'},
                 {'x': 2, 'y': 1, 'xl': '2', 'yl': '1'}]
    ))

print("\n[TOÁN — Bảng biến thiên]")

test("bang_bien_thien",
    lambda: draw_full_border_bbt(
        x_labels=[(2.2, r'$-\infty$'), (4.2, '-1'), (6.2, '0'), (8.2, '2'), (9.5, r'$+\infty$')],
        yprime_data=[(3.2, '-'), (4.2, '0'), (5.2, '+'), (6.2, '0'), (7.2, '-'), (8.2, '0'), (9.0, '+')],
        y_data=[(2.2, 1.8, r'$-\infty$'), (4.2, 0.4, '-2'), (6.2, 1.8, '3'), (8.2, 0.4, '-1'), (9.5, 1.8, r'$+\infty$')],
        arrows=[(2.6, 1.6, 3.8, 0.6), (4.6, 0.6, 5.8, 1.6), (6.6, 1.6, 7.8, 0.6), (8.6, 0.6, 9.2, 1.6)],
        filename=str(OUT / "bang_bien_thien.png")
    ))

test("bbt_sgk_bac_3",
    lambda: draw_bbt_sgk(
        x_cols=['-inf', -1, 1, '+inf'],
        interval_signs=['+', '-', '+'],
        critical_zeros=[1, 2],
        y_data=[('-inf', 'low'), (2, 'high'), (-2, 'low'), ('+inf', 'high')],
        filename=str(OUT / "bbt_sgk_bac_3.png")
    ))

test("bbt_sgk_phan_thuc",
    lambda: draw_bbt_sgk(
        x_cols=['-inf', 1, '+inf'],
        interval_signs=['-', '-'],
        critical_zeros=[],
        asymptotes=[1],
        y_data=[
            (2, 'high'),
            {'left': ('-inf', 'low'), 'right': ('+inf', 'high')},
            (2, 'low')
        ],
        filename=str(OUT / "bbt_sgk_phan_thuc.png")
    ))



print("\n[TOÁN — Hình học không gian]")

test("hinh_chop_s_abcd",
    lambda: plot_pyramid_s_abcd(str(OUT / "hinh_chop_s_abcd.png"), h_ratio=1.6))

print("\n[VẬT LÝ]")

test("dao_dong_dieu_hoa",
    lambda: plot_harmonic_oscillation(5, 0.4, 0, 1.2,
                                      str(OUT / "dao_dong_dieu_hoa.png"),
                                      x_label='t (s)', y_label='x (cm)'))

test("thau_kinh_hoi_tu",
    lambda: plot_thin_lens_optics(15, 30, 2,
                                  str(OUT / "thau_kinh_hoi_tu.png"),
                                  lens_type='convex'))

test("thau_kinh_phan_ky",
    lambda: plot_thin_lens_optics(-20, 10, 2,
                                  str(OUT / "thau_kinh_phan_ky.png"),
                                  lens_type='concave'))

print("\n[HÓA HỌC]")

test("gian_do_nang_luong",
    lambda: plot_chemistry_energy_diagram(
        'CH₄ + 2O₂', 'CO₂ + 2H₂O',
        -890, 150,
        str(OUT / "gian_do_nang_luong.png"),
        is_exothermic=True
    ))

test("duong_cong_chuan_do_ph",
    lambda: plot_ph_titration_curve(25, 1.0, 7.0, 13.0,
                                    str(OUT / "duong_cong_chuan_do_ph.png")))

# ── CÁC HÀM MỚI (nếu đã thêm) ─────────────────────────────────────────────────

print("\n[KIỂM TRA HÀM MỚI]")

try:
    from render_math_figures import plot_trig_function
    test("ham_luong_giac_sin",
        lambda: plot_trig_function('sin', 2, 1, 0, 0, (-2*np.pi, 2*np.pi), (-3, 3),
                                   str(OUT / "ham_luong_giac_sin.png")))
    test("ham_luong_giac_cos",
        lambda: plot_trig_function('cos', 1, 2, 0, 1, (0, 2*np.pi), (-1, 3),
                                   str(OUT / "ham_luong_giac_cos.png")))
except ImportError:
    print("  [SKIP] plot_trig_function chưa được thêm")

try:
    from render_math_figures import plot_parabola
    test("parabol_mo_len",
        lambda: plot_parabola(1, -2, -3, (-3, 5), (-5, 5),
                              str(OUT / "parabol_mo_len.png")))
    test("parabol_mo_xuong",
        lambda: plot_parabola(-1, 4, 3, (-2, 6), (-5, 8),
                              str(OUT / "parabol_mo_xuong.png")))
except ImportError:
    print("  [SKIP] plot_parabola chưa được thêm")

try:
    from render_math_figures import plot_prism_abc_a1b1c1
    test("lang_tru_abc",
        lambda: plot_prism_abc_a1b1c1(str(OUT / "lang_tru_abc.png")))
except ImportError:
    print("  [SKIP] plot_prism_abc_a1b1c1 chưa được thêm")

try:
    from render_math_figures import plot_cylinder, plot_cone, plot_sphere
    test("hinh_tru",
        lambda: plot_cylinder(str(OUT / "hinh_tru.png")))
    test("hinh_non",
        lambda: plot_cone(str(OUT / "hinh_non.png")))
    test("hinh_cau",
        lambda: plot_sphere(str(OUT / "hinh_cau.png")))
except ImportError:
    print("  [SKIP] plot_cylinder/cone/sphere chưa được thêm")

try:
    from render_math_figures import plot_kinematics
    test("do_thi_s_t",
        lambda: plot_kinematics(
            [np.array([0, 1, 2, 3, 4])],
            [np.array([0, 20, 40, 40, 60])],
            str(OUT / "do_thi_s_t.png"),
            xlabel='t (s)', ylabel='s (m)'
        ))
except ImportError:
    print("  [SKIP] plot_kinematics chưa được thêm")

try:
    from render_math_figures import plot_fresnel_diagram
    test("gian_do_fresnel",
        lambda: plot_fresnel_diagram(60, 100, 20,
                                     str(OUT / "gian_do_fresnel.png")))
except ImportError:
    print("  [SKIP] plot_fresnel_diagram chưa được thêm")

try:
    from render_math_figures import plot_velocity_time
    test("do_thi_v_t",
        lambda: plot_velocity_time(
            [
                {'t_start': 0, 't_end': 2, 'v_start': 0, 'v_end': 10, 'label': 'Tăng tốc'},
                {'t_start': 2, 't_end': 4, 'v_start': 10, 'v_end': 10, 'label': 'Đều'},
                {'t_start': 4, 't_end': 6, 'v_start': 10, 'v_end': 0, 'label': 'Giảm tốc'},
            ],
            str(OUT / "do_thi_v_t.png")
        ))
except ImportError:
    print("  [SKIP] plot_velocity_time chưa được thêm")

# ── GIAI ĐOẠN 1 — HÀM MỚI ─────────────────────────────────────────────────────

print("\n[GIAI ĐOẠN 1 — Hàm mới bổ sung]")

try:
    from render_math_figures import plot_exponential_log
    test("ham_mu_log_a2",
        lambda: plot_exponential_log(2, (-3, 4), (-0.5, 8), str(OUT / "ham_mu_log_a2.png"),
                                     show_inverse=True, show_ref_line=True))
    test("ham_mu_log_half",
        lambda: plot_exponential_log(0.5, (-3, 3), (-0.5, 6), str(OUT / "ham_mu_log_half.png"),
                                     show_inverse=True))
except ImportError:
    print("  [SKIP] plot_exponential_log chưa được thêm")

try:
    from render_math_figures import plot_absolute_value_transform
    test("abs_y_of_cubic",
        lambda: plot_absolute_value_transform(
            (1, 0, -3, 0), 'abs_y', (-2.5, 2.5), (-1, 6),
            str(OUT / "abs_y_of_cubic.png"), func_type='cubic', show_original=True))
    test("abs_x_of_cubic",
        lambda: plot_absolute_value_transform(
            (1, 0, -3, 0), 'abs_x', (-2.5, 2.5), (-5, 3),
            str(OUT / "abs_x_of_cubic.png"), func_type='cubic', show_original=True))
except ImportError:
    print("  [SKIP] plot_absolute_value_transform chưa được thêm")

try:
    from render_math_figures import plot_statistics_bar
    test("bieu_do_tan_so",
        lambda: plot_statistics_bar(
            ['[140;145)', '[145;150)', '[150;155)', '[155;160)', '[160;165)'],
            [3, 7, 12, 8, 5],
            str(OUT / "bieu_do_tan_so.png"),
            bar_type='frequency', show_polygon=True, title='Biểu đồ tần số chiều cao học sinh'))
    test("bieu_do_tan_suat",
        lambda: plot_statistics_bar(
            ['[140;145)', '[145;150)', '[150;155)', '[155;160)', '[160;165)'],
            [8.57, 20.0, 34.29, 22.86, 14.28],
            str(OUT / "bieu_do_tan_suat.png"),
            bar_type='relative', show_polygon=False, title='Biểu đồ tần suất (%)'))
except ImportError:
    print("  [SKIP] plot_statistics_bar chưa được thêm")

try:
    from render_math_figures import plot_pie_chart
    test("bieu_do_hinh_quat",
        lambda: plot_pie_chart(
            ['Lúa', 'Ngô', 'Khoai', 'Khác'],
            [45, 25, 18, 12],
            str(OUT / "bieu_do_hinh_quat.png"),
            show_percent=True, title='Cơ cấu sản xuất nông nghiệp'))
except ImportError:
    print("  [SKIP] plot_pie_chart chưa được thêm")

try:
    from render_math_figures import plot_number_line_intervals
    test("truc_so_nghiem_bpt",
        lambda: plot_number_line_intervals(
            [(float('-inf'), 2, False, True), (3, float('inf'), True, False)],
            (-4, 6),
            str(OUT / "truc_so_nghiem_bpt.png"),
            key_points=[2, 3],
            title='Tập nghiệm bất phương trình'))
    test("truc_so_tap_xd",
        lambda: plot_number_line_intervals(
            [(-3, 5, True, False)],
            (-5, 7),
            str(OUT / "truc_so_tap_xd.png"),
            title='Tập xác định [-3; 5)'))
except ImportError:
    print("  [SKIP] plot_number_line_intervals chưa được thêm")

try:
    from render_math_figures import plot_2d_vectors
    test("vec_to_tong_hop",
        lambda: plot_2d_vectors(
            [
                {'origin': (0, 0), 'dx': 3, 'dy': 0, 'label': r'$\vec{F_1}$', 'color': '#1A365D', 'style': '-'},
                {'origin': (0, 0), 'dx': 0, 'dy': 2, 'label': r'$\vec{F_2}$', 'color': '#C53030', 'style': '-'},
            ],
            str(OUT / "vec_to_tong_hop.png"),
            show_resultant=True, show_angle=True))
    test("vec_to_phan_tich_luc",
        lambda: plot_2d_vectors(
            [
                {'origin': (0, 0), 'dx': 4, 'dy': 2, 'label': r'$\vec{P}$', 'color': '#1A365D', 'style': '-'},
                {'origin': (0, 0), 'dx': 4, 'dy': 0, 'label': r'$P_x$', 'color': '#C53030', 'style': '--'},
                {'origin': (0, 0), 'dx': 0, 'dy': 2, 'label': r'$P_y$', 'color': '#27AE60', 'style': '--'},
            ],
            str(OUT / "vec_to_phan_tich_luc.png"),
            show_components=False, show_resultant=False))
except ImportError:
    print("  [SKIP] plot_2d_vectors chưa được thêm")

# ── GIAI ĐOẠN 2 — HÀM MỚI ─────────────────────────────────────────────────────

print("\n[GIAI ĐOẠN 2 — Hàm nâng cao]")

try:
    from render_math_figures import plot_function_comparison
    test("so_sanh_2_ham",
        lambda: plot_function_comparison(
            (1, 0, -3, 0), (0, 0, -1, 0),
            (-2.5, 2.5), (-6, 4),
            str(OUT / "so_sanh_2_ham.png"),
            shade_between=True,
            intersection_pts=[(-1.41, 1.41), (1.41, -1.41)],
            labels=(r'$f(x)=x^3-3x$', r'$g(x)=-x$')
        ))
except ImportError:
    print("  [SKIP] plot_function_comparison chưa được thêm")

try:
    from render_math_figures import plot_wave_superposition
    test("giao_thoa_song_cung_pha",
        lambda: plot_wave_superposition(3, 4, 0.4, 0, 1.2,
                                        str(OUT / "giao_thoa_song_cung_pha.png")))
    test("giao_thoa_song_vuong_pha",
        lambda: plot_wave_superposition(3, 4, 0.4, 3.14159/2, 1.2,
                                        str(OUT / "giao_thoa_song_vuong_pha.png")))
    test("giao_thoa_song_nguoc_pha",
        lambda: plot_wave_superposition(5, 3, 0.4, 3.14159, 1.2,
                                        str(OUT / "giao_thoa_song_nguoc_pha.png")))
except ImportError:
    print("  [SKIP] plot_wave_superposition chưa được thêm")

try:
    from render_math_figures import plot_nuclear_decay
    test("phan_ra_hat_nhan",
        lambda: plot_nuclear_decay(1.0, 1620, 4*1620,
                                   str(OUT / "phan_ra_hat_nhan.png"),
                                   show_halflife_marks=True,
                                   y_label='m(t)/m₀'))
except ImportError:
    print("  [SKIP] plot_nuclear_decay chưa được thêm")

try:
    from render_math_figures import plot_conic_section
    test("duong_ellipse",
        lambda: plot_conic_section('ellipse', 5, 3, (-6, 6), (-4, 4),
                                   str(OUT / "duong_ellipse.png"),
                                   show_foci=True, show_vertices=True))
    test("duong_hypebol",
        lambda: plot_conic_section('hyperbola', 3, 2, (-6, 6), (-5, 5),
                                   str(OUT / "duong_hypebol.png"),
                                   show_foci=True, show_asymptotes=True, show_vertices=True))
except ImportError:
    print("  [SKIP] plot_conic_section chưa được thêm")

try:
    from render_math_figures import plot_projectile_motion
    test("nem_xien_45_do",
        lambda: plot_projectile_motion(20, 45,
                                       str(OUT / "nem_xien_45_do.png"),
                                       show_components=True, show_peak=True, show_range=True))
    test("nem_xien_30_do",
        lambda: plot_projectile_motion(20, 30,
                                       str(OUT / "nem_xien_30_do.png"),
                                       show_components=True, show_peak=True, show_range=True))
except ImportError:
    print("  [SKIP] plot_projectile_motion chưa được thêm")

# ── GIAI ĐOẠN 3 — HÀM CHUYÊN BIỆT HOÀN THIỆN ─────────────────────────────────

print("\n[GIAI ĐOẠN 3 — Hàm chuyên sâu hoàn thiện]")

try:
    from render_math_figures import plot_integral_riemann_sum
    test("tich_phan_riemann",
        lambda: plot_integral_riemann_sum(
            'poly', (-0.25, 0, 4), 0, 3, 6,
            str(OUT / "tich_phan_riemann.png"),
            riemann_type='mid'
        ))
except ImportError:
    print("  [SKIP] plot_integral_riemann_sum chưa được thêm")

try:
    from render_math_figures import plot_electric_field_lines
    test("duong_suc_dien_trai_dau",
        lambda: plot_electric_field_lines((-1.5, 0), 1, (1.5, 0), -1,
                                          str(OUT / "duong_suc_dien_trai_dau.png")))
    test("duong_suc_dien_cung_dau",
        lambda: plot_electric_field_lines((-1.5, 0), 1, (1.5, 0), 1,
                                          str(OUT / "duong_suc_dien_cung_dau.png")))
except ImportError:
    print("  [SKIP] plot_electric_field_lines chưa được thêm")

try:
    from render_math_figures import plot_magnetic_lorentz_force
    test("luc_lorentz",
        lambda: plot_magnetic_lorentz_force(str(OUT / "luc_lorentz.png")))
except ImportError:
    print("  [SKIP] plot_magnetic_lorentz_force chưa được thêm")

try:
    from render_math_figures import plot_polar_graph
    test("do_thi_cuc_hoa_4_canh",
        lambda: plot_polar_graph('rose_4', 3, str(OUT / "do_thi_cuc_hoa_4_canh.png"),
                                 title=r"$r = 3\cos(2\theta)$"))
    test("do_thi_cuc_cardioid",
        lambda: plot_polar_graph('cardioid', 2, str(OUT / "do_thi_cuc_cardioid.png"),
                                 title=r"$r = 2(1+\cos\theta)$"))
except ImportError:
    print("  [SKIP] plot_polar_graph chưa được thêm")

try:
    from render_math_figures import plot_3d_cross_section_pyramid
    test("thiet_dien_chop_3d",
        lambda: plot_3d_cross_section_pyramid(str(OUT / "thiet_dien_chop_3d.png"),
                                              cut_ratio=0.55))
except ImportError:
    print("  [SKIP] plot_3d_cross_section_pyramid chưa được thêm")


print("\n[TikZ ENGINE — tikz_renderer.py]")


try:
    from tikz_renderer import render_tikz, is_latex_available

    if not is_latex_available():
        print("  [SKIP] Không có LaTeX compiler — dùng cloud fallback")

    tikz_tests = [
        ("tikz_tam_giac", r"""
\begin{tikzpicture}
\coordinate (A) at (0,0);
\coordinate (B) at (4,0);
\coordinate (C) at (2,3);
\draw[thick] (A) -- (B) -- (C) -- cycle;
\node[below left] at (A) {$A$};
\node[below right] at (B) {$B$};
\node[above] at (C) {$C$};
\end{tikzpicture}
"""),
        ("tikz_duong_tron", r"""
\begin{tikzpicture}
\draw[thick] (0,0) circle (2cm);
\fill (0,0) circle (2pt) node[below] {$O$};
\draw[dashed] (0,0) -- (2,0) node[midway, above] {$R$};
\end{tikzpicture}
"""),
        ("tikz_mach_dien_R1R2", r"""
\begin{circuitikz}[scale=0.9]
\draw (0,2) to[battery, l=$\mathcal{E}$] (0,0)
      (0,0) -- (3,0)
      (3,0) to[R, l=$R_1$] (3,2)
      (3,2) to[R, l=$R_2$] (0,2);
\end{circuitikz}
"""),
        ("tikz_bbt_tkztab", r"""
\begin{tikzpicture}
\tkzTabInit
  {$x$ / 1, $f'(x)$ / 0.8, $f(x)$ / 2}
  {$-\infty$, $-1$, $2$, $+\infty$}
\tkzTabLine{, -, z, +, z, - ,}
\tkzTabVar{+/$+\infty$, -/$-2$, +/$5$, -/$-\infty$}
\end{tikzpicture}
"""),
    ]

    for name, code in tikz_tests:
        out_path = str(OUT / f"{name}.png")
        try:
            ok = render_tikz(code, out_path, dpi=200, engine='auto')
            if ok and os.path.getsize(out_path) > 1000:
                size = os.path.getsize(out_path) // 1024
                print(f"  [PASS] {name} ({size} KB)")
                PASS.append(name)
            else:
                print(f"  [FAIL] {name}: file trống hoặc quá nhỏ")
                FAIL.append(name)
        except Exception as e:
            print(f"  [FAIL] {name}: {e}")
            FAIL.append(name)

except ImportError as e:
    print(f"  [SKIP] tikz_renderer không load được: {e}")


# ── KẾT QUẢ ─────────────────────────────────────────────────────────────────

print("\n" + "="*60)
print(f"KẾT QUẢ: {len(PASS)} PASS / {len(FAIL)} FAIL / {len(PASS)+len(FAIL)} TỔNG")
print(f"Hình vẽ đã xuất: {OUT}")
if FAIL:
    print(f"\nCần xem xét lại:")
    for f in FAIL:
        print(f"  ✗ {f}")
print("="*60)
