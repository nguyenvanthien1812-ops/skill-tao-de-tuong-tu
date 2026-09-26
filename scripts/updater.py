#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script Tự Động Cập Nhật Skill từ GitHub
- Kiểm tra phiên bản mới nhất trên GitHub
- Tải và thay thế các file đã thay đổi
- BẢO VỆ TUYỆT ĐỐI file license.key và config.json của giáo viên
- Hoạt động an toàn, tự phục hồi nếu mất kết nối mạng

Cách dùng:
  python updater.py                  # Kiểm tra + cập nhật tự động
  python updater.py --check-only     # Chỉ kiểm tra, không cập nhật
  python updater.py --force          # Buộc cập nhật dù đang là phiên bản mới nhất
"""

import sys
import os
import json
import urllib.request
import urllib.error
import shutil
import tempfile
import zipfile
import argparse

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

# ─── CẤU HÌNH ĐƯỜNG DẪN ──────────────────────────────────────────────────────
SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR   = os.path.dirname(SCRIPT_DIR)
LOCAL_VER   = os.path.join(SKILL_DIR, "version.json")
CONFIG_FILE = os.path.join(SKILL_DIR, "github_config.json")

# Các file TUYỆT ĐỐI KHÔNG được ghi đè khi cập nhật (bản quyền và cấu hình riêng)
PROTECTED_FILES = {
    "config.json",
    "license.key",
    "machine_id.txt",
    "MA_MAY_CUA_BAN.txt",
    "github_config.json"
}

# Cấu hình mặc định
GITHUB_USER = "PLACEHOLDER"           # Ví dụ: "nguyenvanA"
GITHUB_REPO = "tao-de-toan-tuong-tu"  # Tên repo trên GitHub

# Đọc cấu hình từ github_config.json nếu có
if os.path.exists(CONFIG_FILE):
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            cfg = json.load(f)
            GITHUB_USER = cfg.get("github_user", GITHUB_USER)
            GITHUB_REPO = cfg.get("github_repo", GITHUB_REPO)
    except Exception:
        pass


def get_github_urls():
    api_base   = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}"
    raw_base   = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/main"
    zip_url    = f"https://github.com/{GITHUB_USER}/{GITHUB_REPO}/archive/refs/heads/main.zip"
    version_url= f"{raw_base}/version.json"
    return api_base, raw_base, zip_url, version_url


# ─── HÀM TIỆN ÍCH ────────────────────────────────────────────────────────────

def fetch_json(url, timeout=10):
    req = urllib.request.Request(url, headers={"User-Agent": "tao-de-updater/2.2"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def read_local_version():
    if not os.path.exists(LOCAL_VER):
        return "0.0.0", {}
    try:
        with open(LOCAL_VER, encoding="utf-8") as f:
            data = json.load(f)
        return data.get("version", "0.0.0"), data
    except Exception:
        return "0.0.0", {}


def compare_versions(v1, v2):
    """Trả về True nếu v2 > v1"""
    def parse(v):
        parts = []
        for x in v.split("."):
            try:
                parts.append(int(x))
            except ValueError:
                parts.append(0)
        return tuple(parts)
    return parse(v2) > parse(v1)


def download_zip_and_update(zip_url, dest_dir):
    """Tải toàn bộ repo dưới dạng ZIP và giải nén, bỏ qua PROTECTED_FILES."""
    print(f"[*] Đang tải gói cập nhật mới nhất từ GitHub...")
    tmp_zip = tempfile.mktemp(suffix=".zip")
    try:
        req = urllib.request.Request(zip_url, headers={"User-Agent": "tao-de-updater/2.2"})
        with urllib.request.urlopen(req, timeout=60) as resp, open(tmp_zip, "wb") as f:
            f.write(resp.read())
        print(f"[*] Tải về thành công! Đang tự động giải nén và cập nhật...")

        with zipfile.ZipFile(tmp_zip, "r") as z:
            # Tìm prefix thư mục trong ZIP (thường là "repo-main/" hoặc tương tự)
            namelist = z.namelist()
            prefix = ""
            for n in namelist:
                if n.endswith("/") and n.count("/") == 1:
                    prefix = n
                    break

            updated = []
            skipped = []
            for member in namelist:
                if member == prefix:
                    continue
                rel_path = member[len(prefix):] if prefix and member.startswith(prefix) else member
                if not rel_path:
                    continue

                basename = os.path.basename(rel_path)
                if basename in PROTECTED_FILES:
                    skipped.append(rel_path)
                    continue

                target = os.path.join(dest_dir, rel_path)
                if member.endswith("/"):
                    os.makedirs(target, exist_ok=True)
                else:
                    os.makedirs(os.path.dirname(target), exist_ok=True)
                    with z.open(member) as src, open(target, "wb") as dst:
                        dst.write(src.read())
                    updated.append(rel_path)
        return updated, skipped
    finally:
        if os.path.exists(tmp_zip):
            try:
                os.remove(tmp_zip)
            except Exception:
                pass


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    global GITHUB_USER, GITHUB_REPO

    parser = argparse.ArgumentParser(description="Cập nhật Skill Tạo Đề Toán & Vật Lý từ GitHub")
    parser.add_argument("--check-only", action="store_true", help="Chỉ kiểm tra phiên bản, không cập nhật")
    parser.add_argument("--force",      action="store_true", help="Buộc cập nhật dù đang là phiên bản mới nhất")
    parser.add_argument("--user",       type=str, default=None, help="Tài khoản GitHub")
    args = parser.parse_args()

    if args.user:
        GITHUB_USER = args.user

    print("=" * 66)
    print("   HỆ THỐNG CẬP NHẬT TỰ ĐỘNG – SKILL TẠO ĐỀ TOÁN & VẬT LÝ")
    print("=" * 66)

    # Đọc phiên bản cục bộ
    local_ver, local_data = read_local_version()
    print(f"\n[i] Phiên bản máy tính đang dùng : v{local_ver}")

    # Kiểm tra cấu hình GitHub
    if GITHUB_USER == "PLACEHOLDER":
        print("\n" + "-" * 66)
        print("  [!] CHƯA THIẾT LẬP TÀI KHOẢN GITHUB CỦA TÁC GIẢ")
        print("-" * 66)
        print("  Để hệ thống tự động tải bản mới từ GitHub, Thầy/Cô chỉ cần")
        print("  nhập tên tài khoản GitHub (Username) dưới đây:")
        print("  (Ví dụ nếu link repo là https://github.com/thaynguyen/tao-de-toan-tuong-tu")
        print("   thì username là: thaynguyen)")
        print()
        val = input("👉 Nhập Username GitHub của Thầy/Cô (hoặc nhấn Enter để bỏ qua): ").strip()
        if val:
            GITHUB_USER = val
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump({"github_user": GITHUB_USER, "github_repo": GITHUB_REPO}, f, indent=2, ensure_ascii=False)
            print(f"[OK] Đã lưu thiết lập: {GITHUB_USER}/{GITHUB_REPO}")
        else:
            print("\n[i] Chưa có thông tin tài khoản GitHub. Bỏ qua kiểm tra cập nhật.")
            return

    api_base, raw_base, zip_url, version_url = get_github_urls()

    try:
        print(f"[*] Đang kết nối GitHub ({GITHUB_USER}/{GITHUB_REPO}) để kiểm tra...")
        remote_data = fetch_json(version_url, timeout=10)
        remote_ver  = remote_data.get("version", "0.0.0")
        print(f"[i] Phiên bản mới nhất trên GitHub: v{remote_ver}")
    except (urllib.error.URLError, Exception) as e:
        print(f"\n[OFFLINE] Không thể kết nối với GitHub: {e}")
        print("          • Kiểm tra kết nối mạng Internet.")
        print("          • Hoặc kiểm tra xem tài khoản/repo GitHub đã được tạo công khai (Public) chưa.")
        print("          • Skill hiện tại vẫn tiếp tục hoạt động bình thường trên máy tính của bạn.")
        return

    is_newer = compare_versions(local_ver, remote_ver)

    if not is_newer and not args.force:
        print(f"\n[✓] Tuyệt vời! Bạn đang sử dụng PHIÊN BẢN MỚI NHẤT (v{local_ver}).")
        print("    Không cần cập nhật thêm.")
        changelog = remote_data.get("changelog", {}).get(remote_ver, [])
        if changelog:
            print(f"\n  Các tính năng trong v{remote_ver}:")
            for item in changelog:
                print(f"    • {item}")
        return

    if args.check_only:
        print(f"\n[!] Đã có phiên bản mới: v{remote_ver} (phiên bản hiện tại: v{local_ver})")
        changelog = remote_data.get("changelog", {}).get(remote_ver, [])
        print("  Tính năng mới:")
        for item in changelog:
            print(f"    • {item}")
        print("\n  → Nhấp đúp vào cap_nhat_tu_dong.bat để tiến hành cập nhật.")
        return

    # Hiển thị thông báo bản mới
    print(f"\n" + "=" * 66)
    print(f"  🔔 PHÁT HIỆN BẢN NÂNG CẤP MỚI: v{local_ver} ──▶ v{remote_ver}")
    print("=" * 66)
    changelog = remote_data.get("changelog", {}).get(remote_ver, [])
    if changelog:
        print("  Các cải tiến & tính năng mới:")
        for item in changelog:
            print(f"    ⭐ {item}")

    confirm = input("\n  Cập nhật ngay bây giờ? [Y/n] (Nhấn Enter để đồng ý): ").strip().upper()
    if confirm and confirm not in ("Y", "YES"):
        print("  Đã hủy tiến trình cập nhật.")
        return

    # Thực hiện cập nhật
    updated_files, skipped_files = download_zip_and_update(zip_url, SKILL_DIR)
    print(f"\n[✓] Đã cập nhật thành công {len(updated_files)} tệp mã nguồn và tài liệu.")
    
    if skipped_files:
        print(f"[i] Bảo toàn an toàn {len(skipped_files)} tệp dữ liệu cá nhân & bản quyền:")
        for f in skipped_files:
            print(f"    🛡️  {f} (giữ nguyên không bị ghi đè)")

    print(f"\n" + "=" * 66)
    print(f"  🎉 [HOÀN TẤT] BẠN ĐÃ CẬP NHẬT LÊN PHIÊN BẢN v{remote_ver} THÀNH CÔNG!")
    print("  Toàn bộ tính năng mới đã sẵn sàng cho lần tạo đề tiếp theo.")
    print("=" * 66)


if __name__ == "__main__":
    main()
