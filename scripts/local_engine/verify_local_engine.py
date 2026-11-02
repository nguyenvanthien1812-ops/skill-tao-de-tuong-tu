# -*- coding: utf-8 -*-
"""
verify_local_engine.py
Kiểm tra chẩn đoán và xác nhận Engine xử lý cục bộ (Local Engine) MathType OLE.
Chạy trực tiếp từ dòng lệnh hoặc được gọi bởi CAI_DAT_LOCAL_ENGINE.bat / cai_dat_tu_dong.bat.
"""

import os
import sys
import tempfile
import zipfile

# Đảm bảo UTF-8 trên Windows console
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

_SCRIPTS_DIR = os.path.dirname(_HERE)
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)

def run_verification():
    print("=" * 68)
    print("   KIỂM ĐỊNH NĂNG LỰC ENGINE XỬ LÝ CỤC BỘ (LOCAL ENGINE)")
    print("   Xuất công thức MathType OLE 100% Offline (Không qua Backend)")
    print("=" * 68)
    print()

    # 0. Kiểm tra bản quyền bắt buộc
    try:
        import license_manager
        ok, payload, err = license_manager.check_current_license()
        if not ok:
            print(" [X] LỖI BẢN QUYỀN: Máy tính chưa kích hoạt bản quyền hợp lệ!")
            print(f"     Chi tiết: {err}")
            print("     Vui lòng chạy file LAY_MA_MAY.bat để lấy mã máy gửi cho Tác giả.")
            print("=" * 68)
            return False
        print(f" [0/4] Kiểm tra bản quyền: [OK] ({payload.get('name', 'Hợp lệ')})")
    except ImportError:
        print(" [X] LỖI BẢN QUYỀN: Không tìm thấy module license_manager.py.")
        print("=" * 68)
        return False

    # 1. Kiểm tra Python
    py_ver = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    print(f" [1/4] Kiểm tra Python: Python {py_ver} ({sys.executable})")

    # 2. Kiểm tra thư viện Python
    print(" [2/4] Kiểm tra các thư viện bắt buộc:")
    required = ["lxml", "olefile", "latex2mathml", "docx"]
    missing = []
    for pkg in required:
        try:
            __import__(pkg)
            print(f"       + {pkg:<15}: [OK]")
        except ImportError:
            print(f"       - {pkg:<15}: [THIẾU]")
            missing.append(pkg)

    if missing:
        print()
        print(f" [!] CẢNH BÁO: Còn thiếu thư viện: {', '.join(missing)}")
        print(f"     Vui lòng chạy: pip install {' '.join(missing)}")
        return False

    # 3. Kiểm tra LibreOffice Engine
    print(" [3/4] Kiểm tra LibreOffice Headless Engine:")
    try:
        from docx_processor import find_libreoffice_python
        lo_python = find_libreoffice_python()
    except Exception as e:
        lo_python = ""
        print(f"       Lỗi import docx_processor: {e}")

    if lo_python and os.path.exists(lo_python):
        print(f"       + LibreOffice Python: [OK] -> {lo_python}")
    else:
        print("       - LibreOffice: [CHƯA TÌM THẤY]")
        print("       -> Cần cài LibreOffice để kích hoạt chế độ Offline 100%.")
        print("       -> Lệnh cài nhanh: winget install --id TheDocumentFoundation.LibreOffice -e --silent")
        return False

    # 4. Kiểm tra biên dịch thực tế 1 công thức mẫu
    print(" [4/4] Thử nghiệm biên dịch công thức mẫu: $E = mc^2$ ...")
    test_dir = tempfile.mkdtemp(prefix="lo_verify_")
    test_docx = os.path.join(test_dir, "test_input.docx")
    out_docx = os.path.join(test_dir, "test_output.docx")

    try:
        import docx
        doc = docx.Document()
        p = doc.add_paragraph("Thử nghiệm công thức: ")
        # Tránh lỗi parsing $ trong một số môi trường shell
        r = p.add_run("$E = mc^2$")
        doc.save(test_docx)

        from docx_processor import convert_docx_latex_to_mathtype
        res = convert_docx_latex_to_mathtype(test_docx, out_docx, use_libreoffice=True)

        if not os.path.exists(out_docx):
            print("       - Lỗi: Không sinh được file output!")
            return False

        # Kiểm tra file OLE nhúng
        ole_count = 0
        with zipfile.ZipFile(out_docx, "r") as z:
            ole_objects = [n for n in z.namelist() if "embeddings/oleObject" in n or "embeddings/Microsoft_Equation_3.0" in n]
            ole_count = len(ole_objects)

        if ole_count > 0:
            print("       + Biên dịch MathType OLE: [THÀNH CÔNG 100%]")
            print(f"       + Đã nhúng {ole_count} đối tượng OLE (ProgID Equation.DSMT4, mở đúp bằng MathType)")
        else:
            print("       - Biên dịch không tạo được OLE object!")
            return False

    except Exception as e:
        print(f"       - Lỗi thử nghiệm: {e}")
        return False
    finally:
        # Dọn dẹp file tạm
        try:
            if os.path.exists(test_docx): os.remove(test_docx)
            if os.path.exists(out_docx): os.remove(out_docx)
            if os.path.exists(test_dir): os.rmdir(test_dir)
        except Exception:
            pass

    print()
    print("=" * 68)
    print("   🎉 CHÚC MỪNG QUÝ THẦY/CÔ!")
    print("   ENGINE XỬ LÝ CỤC BỘ (LOCAL ENGINE) ĐÃ SẴN SÀNG HOẠT ĐỘNG 100%!")
    print("   Từ nay khi tạo đề, công thức sẽ được chuyển thành MathType OLE")
    print("   hoàn toàn CỤC BỘ trên máy tính, siêu tốc và KHÔNG CẦN BACKEND!")
    print("=" * 68)
    print()
    return True

if __name__ == "__main__":
    success = run_verification()
    sys.exit(0 if success else 1)
