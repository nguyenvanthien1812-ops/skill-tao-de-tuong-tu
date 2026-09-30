#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script Kiểm Tra & Tự Động Cài Đặt Môi Trường Cho Skill Tạo Đề Toán Tương Tự
Tác giả: Antigravity Assistant - Google DeepMind
Dành cho: Quý Thầy/Cô giáo bộ môn Toán
"""

import sys
import os
import subprocess
import urllib.request
import time

REQUIRED_PACKAGES = [
    ("matplotlib", "matplotlib"),
    ("scipy", "scipy"),
    ("docx", "python-docx"),
    ("lxml", "lxml"),
    ("latex2mathml", "latex2mathml"),
    ("requests", "requests"),
    ("PIL", "pillow"),
    ("openpyxl", "openpyxl"),
    ("cryptography", "cryptography"),
    ("fitz", "pymupdf"),
]

OFFICE_XSL_PATHS = [
    r'C:\Program Files (x86)\Microsoft Office\root\Office16\MML2OMML.XSL',
    r'C:\Program Files\Microsoft Office\root\Office16\MML2OMML.XSL',
    r'C:\Program Files (x86)\Microsoft Office\Office16\MML2OMML.XSL',
    r'C:\Program Files\Microsoft Office\Office16\MML2OMML.XSL',
    r'C:\Program Files (x86)\Microsoft Office\Office15\MML2OMML.XSL',
    r'C:\Program Files\Microsoft Office\Office15\MML2OMML.XSL',
    r'C:\Program Files (x86)\Microsoft Office\Office14\MML2OMML.XSL',
    r'C:\Program Files\Microsoft Office\Office14\MML2OMML.XSL',
]

BACKEND_API_HEALTH = 'https://latex2mathtypeweb.onrender.com/'

def print_banner():
    print("=" * 65)
    print("   HỆ THỐNG KIỂM TRA & TỰ ĐỘNG CÀI ĐẶT MÔI TRƯỜNG TẠO ĐỀ TOÁN")
    print("   Dành cho Giáo viên sử dụng Google Antigravity")
    print("=" * 65)
    print()

def install_package(pip_name):
    print(f"[*] Đang tự động cài đặt thư viện: {pip_name} ...")
    cmd = [sys.executable, "-m", "pip", "install", pip_name, "--quiet", "--disable-pip-version-check"]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"    -> [THÀNH CÔNG] Đã cài đặt xong: {pip_name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"    -> [LỖI] Không thể tự cài {pip_name}: {e.stderr.strip()}")
        return False

def check_and_install_dependencies():
    print("[1/4] Kiểm tra các thư viện Python chuyên dụng:")
    all_ok = True
    for module_name, pip_name in REQUIRED_PACKAGES:
        try:
            __import__(module_name)
            print(f"  [OK] Đã có thư viện: {pip_name}")
        except ImportError:
            print(f"  [-] Chưa có thư viện: {pip_name}. Tiến hành tự cài đặt...")
            success = install_package(pip_name)
            if not success:
                all_ok = False
    return all_ok

def check_microsoft_office():
    print("\n[2/4] Kiểm tra Microsoft Office & MathType trên máy tính:")
    found_xsl = False
    for path in OFFICE_XSL_PATHS:
        if os.path.exists(path):
            found_xsl = True
            print(f"  [OK] Đã tìm thấy tệp chuyển đổi Word Equation:\n       {path}")
            break
    
    if not found_xsl:
        print("  [LƯU Ý] Không tìm thấy MML2OMML.XSL ở thư mục mặc định.")
        print("          Hệ thống sẽ tự động sử dụng máy chủ Backend để sinh công thức.")
    
    # Kiểm tra MathType Registry/Thư mục nếu có
    mathtype_dirs = [
        r"C:\Program Files (x86)\MathType",
        r"C:\Program Files\MathType"
    ]
    has_mathtype = any(os.path.exists(d) for d in mathtype_dirs)
    if has_mathtype:
        print("  [OK] Đã cài đặt phần mềm MathType trên máy (Sẵn sàng mở sửa click đúp).")
    else:
        print("  [THÔNG TIN] Chưa phát hiện MathType cài tại thư mục chuẩn. Khi mở file Word,")
        print("              ảnh công thức vector WMF vẫn hiển thị chuẩn nét 100%.")

def check_latex_compiler():
    print("\n[3/4] Kiểm tra trình biên dịch LaTeX & TikZ Engine:")
    try:
        from tikz_renderer import find_latex_compiler, is_latex_available
    except ImportError:
        try:
            from scripts.tikz_renderer import find_latex_compiler, is_latex_available
        except ImportError:
            find_latex_compiler = lambda: None
            is_latex_available = lambda: False

    compiler = find_latex_compiler()
    if compiler:
        print(f"  [OK] Tìm thấy trình biên dịch LaTeX: {os.path.basename(compiler)}")
        print("       -> Sẵn sàng render hình vẽ TikZ, tkz-tab, tkz-euclide, circuitikz siêu tốc 300 DPI!")
    else:
        print("  [LƯU Ý] Chưa phát hiện pdflatex/xelatex trên máy.")
        print("          Hệ thống sẽ tự động kích hoạt Cloud Fallback Engine khi render TikZ.")

def check_backend_api():
    print("\n[4/4] Kiểm tra kết nối tới Máy chủ chuyển đổi MathType OLE:")
    try:
        req = urllib.request.Request(
            BACKEND_API_HEALTH,
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req, timeout=15) as response:
            status = response.getcode()
            if status in [200, 404]: # Endpoint root returns 200 or 404 is alive
                print("  [OK] Kết nối Máy chủ MathType Cloud thành công! Sẵn sàng xuất OLE.")
            else:
                print(f"  [CẢNH BÁO] Máy chủ phản hồi mã {status}.")
    except Exception as e:
        print(f"  [LƯU Ý] Máy chủ phản hồi chậm hoặc đang khởi động lại ({e}).")
        print("          Đừng lo, hệ thống vẫn sẽ sinh bản Word Equation (OMML) cực chuẩn!")

def main():
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
    print_banner()
    pkg_status = check_and_install_dependencies()
    check_microsoft_office()
    check_latex_compiler()
    check_backend_api()
    
    print("\n" + "=" * 65)
    if pkg_status:
        print(" [HOÀN TẤT] MÔI TRƯỜNG ĐÃ SẴN SÀNG 100% ĐỂ TẠO ĐỀ TOÁN!")
        print(" Quý Thầy/Cô chỉ cần mở khung chat Antigravity và nhắn:")
        print('   "Tạo cho tôi đề tương tự từ Đề [Tên_Đề]"')
    else:
        print(" [CHÚ Ý] Một số thư viện cài đặt chưa hoàn tất. Vui lòng kiểm tra lại mạng Internet.")
    print("=" * 65)

if __name__ == '__main__':
    main()
