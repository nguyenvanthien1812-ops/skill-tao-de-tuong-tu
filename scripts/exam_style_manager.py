#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
exam_style_manager.py — Quản lý Theme và Profile Cá Nhân
========================================================
Load/save theme màu sắc và thông tin trường cho ExamPDFExporter.

Sử dụng:
    from scripts.exam_style_manager import ExamStyleManager
    style = ExamStyleManager.load_theme('teal')
    ExamStyleManager.save_teacher_profile('co_lan', style)
    style2 = ExamStyleManager.load_teacher_profile('co_lan')
"""

from __future__ import annotations
import json
import re
from pathlib import Path
from typing import Optional

# Thư mục lưu profile cá nhân giáo viên (trong thư mục skill)
_SKILL_ROOT = Path(__file__).parent.parent
_STYLES_DIR = _SKILL_ROOT / 'exam_styles'


class ExamStyleManager:
    """Quản lý theme màu sắc và profile cá nhân của giáo viên."""

    @staticmethod
    def load_theme(theme_name: str) -> dict:
        """
        Load theme có sẵn theo tên.
        Nếu không tìm thấy, trả về theme 'teal' mặc định.
        """
        name = theme_name.lower().strip()
        fpath = _STYLES_DIR / f'theme_{name}.json'
        if fpath.exists():
            with open(fpath, encoding='utf-8') as f:
                return json.load(f)
        # Fallback về teal
        teal = _STYLES_DIR / 'theme_teal.json'
        if teal.exists():
            with open(teal, encoding='utf-8') as f:
                return json.load(f)
        # Hardcode fallback cuối cùng
        return {
            'color_primary': '1A7070',
            'color_secondary': '2C3E50',
            'color_solution_bg': 'F0F4F4',
        }

    @staticmethod
    def load_from_file(path: str) -> dict:
        """Load style từ file JSON tùy chỉnh."""
        with open(path, encoding='utf-8') as f:
            return json.load(f)

    @staticmethod
    def save_teacher_profile(teacher_name: str, style: dict,
                              save_dir: Optional[str] = None) -> str:
        """
        Lưu profile cá nhân của giáo viên.
        Lần sau chỉ cần gọi load_teacher_profile(teacher_name).
        """
        out_dir = Path(save_dir) if save_dir else _STYLES_DIR
        out_dir.mkdir(parents=True, exist_ok=True)
        safe_name = re.sub(r'[^\w]', '_', teacher_name.lower())
        fpath = out_dir / f'profile_{safe_name}.json'
        with open(fpath, 'w', encoding='utf-8') as f:
            json.dump(style, f, ensure_ascii=False, indent=2)
        return str(fpath)

    @staticmethod
    def load_teacher_profile(teacher_name: str,
                              profiles_dir: Optional[str] = None) -> Optional[dict]:
        """
        Load profile cá nhân của giáo viên.
        Trả về None nếu chưa có profile nào.
        """
        out_dir = Path(profiles_dir) if profiles_dir else _STYLES_DIR
        safe_name = re.sub(r'[^\w]', '_', teacher_name.lower())
        fpath = out_dir / f'profile_{safe_name}.json'
        if fpath.exists():
            with open(fpath, encoding='utf-8') as f:
                return json.load(f)
        return None

    @staticmethod
    def list_profiles() -> list[dict]:
        """Liệt kê tất cả profile đã lưu."""
        profiles = []
        for fp in sorted(_STYLES_DIR.glob('profile_*.json')):
            with open(fp, encoding='utf-8') as f:
                data = json.load(f)
            profiles.append({
                'file': fp.name,
                'school_name': data.get('school_name', ''),
                'theme': data.get('theme', ''),
            })
        return profiles

    @staticmethod
    def list_themes() -> list[dict]:
        """Liệt kê 6 theme có sẵn."""
        themes = []
        for fp in sorted(_STYLES_DIR.glob('theme_*.json')):
            with open(fp, encoding='utf-8') as f:
                data = json.load(f)
            themes.append({
                'key': data.get('theme', fp.stem.replace('theme_', '')),
                'name': data.get('name', ''),
                'description': data.get('description', ''),
                'color': '#' + data.get('color_primary', '000000'),
            })
        return themes

    @staticmethod
    def resolve_theme_from_chat(user_message: str) -> Optional[str]:
        """
        Nhận diện yêu cầu theme từ tin nhắn tự nhiên.
        Trả về tên theme ('teal', 'navy', ...) hoặc None.

        Ví dụ:
            'theme xanh teal' → 'teal'
            'dùng màu đỏ' → 'red'
            'style trắng đen' → 'minimal'
        """
        msg = user_message.lower()
        mapping = [
            ('teal', ['teal', 'xanh ngọc', 'xanh lá mạ']),
            ('navy', ['navy', 'navy blue', 'xanh nước biển', 'trang trọng', 'biển']),
            ('red',  ['red', 'đỏ', 'red color', 'nổi bật', 'màu đỏ']),
            ('minimal', ['minimal', 'trắng đen', 'đen trắng', 'tiết kiệm mực', 'đơn giản']),
            ('purple', ['purple', 'tím', 'màu tím', 'sáng tạo']),
            ('classic', ['classic', 'truyền thống', 'sgk', 'xanh dương']),
        ]
        for theme_key, keywords in mapping:
            for kw in keywords:
                if kw in msg:
                    return theme_key
        return None

    @staticmethod
    def merge_styles(*styles: dict) -> dict:
        """
        Trộn nhiều style lại (sau ghi đè trước).
        Ví dụ: merge_styles(theme_teal, custom_config) → kết hợp
        """
        result: dict = {}
        for s in styles:
            result.update(s)
        return result


if __name__ == '__main__':
    print('Các theme có sẵn:')
    for t in ExamStyleManager.list_themes():
        print(f"  [{t['key']}] {t['name']} {t['color']}")
    print('\nCác profile đã lưu:')
    profiles = ExamStyleManager.list_profiles()
    if profiles:
        for p in profiles:
            print(f"  {p['file']} — {p['school_name']}")
    else:
        print('  (chưa có profile nào)')
