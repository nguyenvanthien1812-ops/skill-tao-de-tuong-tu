#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔐 License Manager – Kiểm Tra & Kích Hoạt License Key
Tích hợp vào Skill Tạo Đề Toán Tương Tự

Cách dùng (giáo viên):
  python scripts/license_manager.py --machine-id     → Lấy Machine ID để gửi tác giả
  python scripts/license_manager.py --activate <KEY> → Kích hoạt license
  python scripts/license_manager.py --check          → Kiểm tra trạng thái license
"""

import sys, os, json, base64, hashlib, socket, platform, uuid
from datetime import datetime, timezone
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

try:
    from cryptography.hazmat.primitives.asymmetric import padding
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.backends import default_backend
    HAS_CRYPTO = True
except ImportError:
    try:
        print("[*] Dang tu dong cai dat thu vien bao mat cryptography...")
        import subprocess
        subprocess.run([sys.executable, "-m", "pip", "install", "cryptography", "-q"], check=True)
        from cryptography.hazmat.primitives.asymmetric import padding
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.backends import default_backend
        HAS_CRYPTO = True
        print("[OK] Da cai dat xong cryptography!")
    except Exception:
        HAS_CRYPTO = False

# ─── CẤU HÌNH ────────────────────────────────────────────────────────────────
SKILL_DIR    = Path(__file__).resolve().parent.parent  # Thư mục gốc của skill
SKILL_NAME   = "tao-de-toan-tuong-tu"

def get_all_license_paths() -> list[Path]:
    """
    Trả về danh sách tất cả các vị trí có thể lưu hoặc kiểm tra license.key:
    1. Thư mục cục bộ của skill (nơi chứa script này)
    2. Thư mục global Google Antigravity config (%USERPROFILE%/.gemini/config/skills/tao-de-toan-tuong-tu)
    3. Thư mục global Antigravity builtin (%USERPROFILE%/.gemini/antigravity/skills/tao-de-toan-tuong-tu)
    4. Thư mục người dùng toàn cục (%USERPROFILE%/.gemini/license.key)
    5. Thư mục làm việc hiện tại (cwd) và các cấp thư mục cha/con
    """
    paths = []
    
    # 1. Thư mục skill hiện tại
    paths.append(SKILL_DIR / "license.key")
    
    # 2. Thư mục người dùng toàn cục trên Windows/macOS/Linux
    try:
        user_home = Path.home()
        paths.append(user_home / ".gemini" / "config" / "skills" / SKILL_NAME / "license.key")
        paths.append(user_home / ".gemini" / "antigravity" / "skills" / SKILL_NAME / "license.key")
        paths.append(user_home / ".gemini" / "license.key")
    except Exception:
        pass
        
    # 3. Thư mục làm việc hiện tại (cwd) và thư mục cha
    try:
        cwd = Path.cwd().resolve()
        paths.append(cwd / "license.key")
        paths.append(cwd / SKILL_NAME / "license.key")
        paths.append(cwd / ".agents" / "skills" / SKILL_NAME / "license.key")
        if cwd != cwd.parent:
            paths.append(cwd.parent / "license.key")
            paths.append(cwd.parent / SKILL_NAME / "license.key")
    except Exception:
        pass
        
    # Khử trùng lặp
    unique_paths = []
    seen = set()
    for p in paths:
        try:
            resolved = p.resolve()
            if resolved not in seen:
                seen.add(resolved)
                unique_paths.append(p)
        except Exception:
            if p not in unique_paths:
                unique_paths.append(p)
                
    return unique_paths

LICENSE_FILE = SKILL_DIR / "license.key"     # Vị trí mặc định

# ⚠️  PUBLIC KEY được nhúng vào đây (Tác giả paste public_key.pem vào đây)
# Giáo viên KHÔNG THỂ dùng public key này để TẠO license, chỉ để XÁC MINH.
PUBLIC_KEY_PEM = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAsykVJf8gHugg+wgotDfK
zUlDcpW09tl/medCzkzfI/1l19nwEqbiJoNBgbroCtu2fU38Jw+saRMusXbMys3a
aCPrHKkg0ui/59jTQx82T5a3VX+fPLe+aiMwe13b/oLGur/pPU6dqr2eoYeNUt3T
9hw+jl2XHYdDgytPeRmGUE8fN/q0VQLaCuKZcXgxugc9JnGZrkZyvoiz2cmNp2mt
Sq+mLFWvPxhbx9gTlHxX7AZCIRjTSJeq9bOL7sHiuSNClRXHAQiYUppoWiumPOV7
fjegRJweRxtBVRmC/zxxL+xz6/Hgazwivog1pRE6tr4gE0xyqjGFgyOca+dW+33H
EQIDAQAB
-----END PUBLIC KEY-----"""

# URL danh sách license bị thu hồi (tác giả cập nhật trên GitHub khi cần)
REVOCATION_URL = "https://raw.githubusercontent.com/nguyenvanthien1812-ops/skill-tao-de-tuong-tu/main/revoked.json"


# ─── LẤY MACHINE ID ──────────────────────────────────────────────────────────

def get_machine_id() -> str:
    """
    Tạo Machine ID duy nhất cho máy tính này.
    Kết hợp nhiều thông tin phần cứng để tránh giả mạo.
    """
    parts = []

    # MAC address của card mạng đầu tiên
    mac = uuid.UUID(int=uuid.getnode()).hex[-12:]
    parts.append(mac)

    # Hostname
    parts.append(socket.gethostname().lower())

    # Windows Machine GUID (nếu có)
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                             r"SOFTWARE\Microsoft\Cryptography")
        guid, _ = winreg.QueryValueEx(key, "MachineGuid")
        parts.append(guid)
    except Exception:
        parts.append(platform.node())

    raw = "|".join(parts)
    return hashlib.sha256(raw.encode()).hexdigest()[:32]


# ─── XÁC MINH LICENSE ────────────────────────────────────────────────────────

def verify_license_key(license_key: str) -> tuple[bool, dict, str]:
    """
    Xác minh license key bằng RSA Public Key.
    Trả về (is_valid, payload_dict, error_message)
    """
    if not HAS_CRYPTO:
        return False, {}, "Cần cài: pip install cryptography"

    if "PASTE_PUBLIC_KEY_HERE" in PUBLIC_KEY_PEM:
        return False, {}, "Public key chưa được cấu hình trong license_manager.py"

    try:
        parts = license_key.strip().split(".")
        if len(parts) != 2:
            return False, {}, "Định dạng license key không hợp lệ"

        payload_bytes = base64.urlsafe_b64decode(parts[0] + "==")
        signature     = base64.urlsafe_b64decode(parts[1] + "==")
        payload       = json.loads(payload_bytes.decode("utf-8"))

        # Xác minh chữ ký RSA
        public_key = serialization.load_pem_public_key(
            PUBLIC_KEY_PEM.strip().encode(), backend=default_backend()
        )
        public_key.verify(
            signature, payload_bytes,
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256()
        )

        # Kiểm tra skill đúng
        if payload.get("skill") != SKILL_NAME:
            return False, payload, "License key không dành cho skill này"

        # Kiểm tra machine_id
        machine_id = payload.get("machine_id", "ANY")
        if machine_id != "ANY":
            current_mid = get_machine_id()
            if current_mid != machine_id:
                return False, payload, (
                    f"License key này được cấp cho máy khác!\n"
                    f"  Machine ID của máy bạn : {current_mid}\n"
                    f"  Machine ID trong key    : {machine_id}\n"
                    f"  → Liên hệ tác giả để được cấp key mới cho máy này."
                )

        # Kiểm tra hạn sử dụng
        expiry = datetime.strptime(payload["expiry"], "%Y-%m-%d").replace(tzinfo=timezone.utc)
        if datetime.now(timezone.utc) > expiry:
            days_overdue = (datetime.now(timezone.utc) - expiry).days
            return False, payload, (
                f"License key đã hết hạn {days_overdue} ngày (hết hạn: {payload['expiry']}).\n"
                f"  → Liên hệ tác giả để gia hạn."
            )

        return True, payload, ""

    except Exception as e:
        return False, {}, f"Lỗi xác minh: {e}"


def check_revocation(license_id: str) -> bool:
    """Kiểm tra online xem license có bị thu hồi không. Bỏ qua nếu offline hoặc mạng chậm."""
    try:
        import urllib.request
        import time
        cache_buster = f"?t={int(time.time())}"
        url = REVOCATION_URL + cache_buster
        req = urllib.request.Request(url, headers={"User-Agent": "license-checker/2.0"})
        with urllib.request.urlopen(req, timeout=2.5) as resp:
            revoked_list = json.loads(resp.read().decode("utf-8"))
        return license_id in revoked_list
    except Exception:
        return False  # Offline hoặc timeout → bỏ qua kiểm tra thu hồi


def get_license_token() -> str:
    """Lấy chuỗi license key raw từ bất kỳ vị trí hợp lệ nào."""
    for p in get_all_license_paths():
        if p.exists():
            try:
                t = p.read_text(encoding="utf-8").strip()
                if t:
                    return t
            except Exception:
                continue
    return ""


def sync_skill_to_antigravity(license_content: str = None):
    """Tự động đồng bộ toàn bộ file skill vào Antigravity global config."""
    try:
        import shutil
        target_dir = Path.home() / ".gemini" / "config" / "skills" / SKILL_NAME
        target_dir.mkdir(parents=True, exist_ok=True)
        
        # Nếu đang chạy từ chính target_dir thì không cần copy lại code
        if SKILL_DIR.resolve() != target_dir.resolve():
            for item in SKILL_DIR.iterdir():
                if item.name.startswith(".") or item.name in {"__pycache__", "test_output_figures", "dist"}:
                    continue
                dest = target_dir / item.name
                try:
                    if item.is_dir():
                        shutil.copytree(item, dest, dirs_exist_ok=True)
                    else:
                        shutil.copy2(item, dest)
                except Exception:
                    pass
                    
        # Đồng bộ license.key
        if license_content:
            try:
                (target_dir / "license.key").write_text(license_content.strip(), encoding="utf-8")
                (Path.home() / ".gemini" / "license.key").write_text(license_content.strip(), encoding="utf-8")
            except Exception:
                pass
    except Exception:
        pass


# ─── KÍCH HOẠT LICENSE ───────────────────────────────────────────────────────

def activate(license_key: str) -> bool:
    """Xác minh và lưu license key vào máy ở tất cả các vị trí cần thiết."""
    print("[*] Đang xác minh license key ...")
    is_valid, payload, error = verify_license_key(license_key)

    if not is_valid:
        print(f"[✗] License key KHÔNG HỢP LỆ:\n    {error}")
        return False

    # Kiểm tra thu hồi online
    lid = payload.get("license_id", "")
    if lid and check_revocation(lid):
        print(f"[✗] License key đã bị TÁC GIẢ THU HỒI.\n    → Liên hệ tác giả để được hỗ trợ.")
        return False

    clean_key = license_key.strip()
    
    # Lưu license vào TẤT CẢ các vị trí khả dụng
    saved_count = 0
    for p in get_all_license_paths():
        try:
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(clean_key, encoding="utf-8")
            saved_count += 1
        except Exception:
            pass

    # Tự động nạp vào Google Antigravity
    sync_skill_to_antigravity(clean_key)

    days_left = (datetime.strptime(payload["expiry"], "%Y-%m-%d").replace(tzinfo=timezone.utc)
                 - datetime.now(timezone.utc)).days

    print(f"\n[✓] KÍCH HOẠT THÀNH CÔNG!")
    print(f"    Chào mừng: {payload.get('name', '')} ({payload.get('email', '')})")
    print(f"    Hạn sử dụng: {payload['expiry']} (còn {days_left} ngày)")
    print(f"    Đã tự động nạp và đồng bộ vào Google Antigravity!")
    print(f"    Skill đã sẵn sàng sử dụng 100%!")
    return True


def check_current_license() -> tuple[bool, dict, str]:
    """Đọc và kiểm tra license đã kích hoạt trên máy tính này (quét đa đường dẫn)."""
    found_key = None
    found_payload = {}
    found_path = None

    for p in get_all_license_paths():
        if p.exists():
            try:
                content = p.read_text(encoding="utf-8").strip()
                if content:
                    is_valid, payload, err = verify_license_key(content)
                    if is_valid:
                        # Kiểm tra thu hồi online
                        lid = payload.get("license_id", "")
                        if lid and check_revocation(lid):
                            for p_del in get_all_license_paths():
                                try:
                                    if p_del.exists():
                                        p_del.unlink(missing_ok=True)
                                except Exception:
                                    pass
                            return False, payload, "License key đã bị tác giả thu hồi. Vui lòng liên hệ tác giả để được hỗ trợ."
                        found_key = content
                        found_payload = payload
                        found_path = p
                        break
            except Exception:
                continue

    if not found_key:
        return False, {}, "Chưa kích hoạt license. Vui lòng chạy KICH_HOAT_BAN_QUYEN.bat hoặc dán mã bản quyền."

    # TỰ ĐỘNG ĐỒNG BỘ: Ghi bản quyền sang tất cả các vị trí chưa có
    for p in get_all_license_paths():
        try:
            if not p.exists() or p.read_text(encoding="utf-8").strip() != found_key:
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(found_key, encoding="utf-8")
        except Exception:
            pass

    return True, found_payload, ""


def require_valid_license() -> dict:
    """
    Hàm gọi từ các script khác để bắt buộc có license hợp lệ.
    Nếu không hợp lệ → in thông báo rõ ràng và exit.
    """
    is_valid, payload, error = check_current_license()
    if not is_valid:
        print("=" * 60)
        print("  ⛔  CẦN KÍCH HOẠT LICENSE ĐỂ SỬ DỤNG SKILL NÀY")
        print("=" * 60)
        print(f"\n  {error}")
        print()
        print("  📋 Để được cấp license, liên hệ tác giả:")
        print(f"     1. Chạy lệnh để lấy Machine ID của máy bạn:")
        print(f"        python scripts/license_manager.py --machine-id")
        print(f"     2. Gửi Machine ID cho tác giả để nhận license key.")
        print(f"     3. Kích hoạt: python scripts/license_manager.py --activate <KEY>")
        print("=" * 60)
        sys.exit(1)
    return payload


def copy_to_clipboard(text: str):
    """Copy text vào Clipboard trên Windows."""
    try:
        import subprocess
        cmd = f'powershell -Command "Set-Clipboard -Value \'{text}\'"'
        subprocess.run(cmd, shell=True, check=True)
        return True
    except Exception:
        try:
            import subprocess
            p = subprocess.Popen(['clip'], stdin=subprocess.PIPE, shell=True)
            p.communicate(text.encode('utf-8'))
            return True
        except Exception:
            return False

# ─── MAIN (CLI) ───────────────────────────────────────────────────────────────

def main():
    import argparse
    p = argparse.ArgumentParser(description="License Manager – Skill Tạo Đề Toán Tương Tự")
    g = p.add_mutually_exclusive_group(required=False)
    g.add_argument("--machine-id", action="store_true", help="Lấy Machine ID của máy này")
    g.add_argument("--activate",   nargs="?", const="PROMPT", metavar="LICENSE_KEY", help="Kích hoạt license key")
    g.add_argument("--check",      action="store_true",   help="Kiểm tra trạng thái license")
    args = p.parse_args()

    # Mặc định nếu không truyền tham số: kiểm tra license
    if not (args.machine_id or args.activate or args.check):
        args.check = True

    if args.machine_id:
        mid = get_machine_id()
        copied = copy_to_clipboard(mid)
        print("=" * 60)
        print("         MÃ ĐỊNH DANH MÁY TÍNH (MACHINE ID)")
        print("=" * 60)
        print(f"\n   Mã máy của bạn:  {mid}\n")
        print("-" * 60)
        if copied:
            print("📋 [ĐÃ TỰ ĐỘNG COPY VÀO BỘ NHỚ TẠM / CLIPBOARD!]")
            print("👉 Bạn chỉ cần mở tin nhắn Zalo gửi cho Tác giả và bấm Ctrl + V.")
        else:
            print("👉 Vui lòng bôi đen dòng mã máy ở trên rồi bấm Ctrl + C để gửi.")
        print("=" * 60)

    elif args.activate:
        key = args.activate
        if key == "PROMPT":
            print("=" * 60)
            print("           KÍCH HOẠT BẢN QUYỀN SKILL TẠO ĐỀ TOÁN")
            print("=" * 60)
            key = input("\n👉 Dán mã License Key bạn nhận được (Ctrl + V hoặc nhấp chuột phải) rồi Enter:\n\n> ").strip()
        
        if not key:
            print("[!] Mã License Key không được để trống!")
            sys.exit(1)
        
        ok = activate(key)
        sys.exit(0 if ok else 1)

    elif args.check:
        is_valid, payload, error = check_current_license()
        print("\n" + "=" * 50)
        if is_valid:
            days_left = (datetime.strptime(payload["expiry"], "%Y-%m-%d").replace(tzinfo=timezone.utc)
                         - datetime.now(timezone.utc)).days
            status = "✅ HỢP LỆ" if days_left > 7 else f"⚠️  CÒN {days_left} NGÀY"
            print(f"  Trạng thái  : {status}")
            print(f"  Tên         : {payload.get('name', '')}")
            print(f"  Email/SĐT   : {payload.get('email', '')}")
            print(f"  Hết hạn     : {payload['expiry']} (còn {days_left} ngày)")
            print(f"  Khóa máy    : {'Khóa theo máy này' if payload.get('machine_id') != 'ANY' else 'Không giới hạn máy'}")
            print("=" * 50)
            sys.exit(0)
        else:
            print(f"  Trạng thái  : ❌ CHƯA HỢP LỆ")
            print(f"  Chi tiết    : {error}")
            print("=" * 50)
            sys.exit(1)
        print("=" * 50)


if __name__ == "__main__":
    main()
