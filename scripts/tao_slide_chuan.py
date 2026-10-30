#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bộ Khung Chuẩn Tạo File PowerPoint (.pptx) Sư Phạm 16:9 Bằng python-pptx
Tác giả: Thầy Nguyễn Văn Thiện - THCS Ứng Hòe
- Tỉ lệ màn chiếu: 16:9 (13.333 x 7.5 inches)
- Font chữ chuẩn mực: Times New Roman 100% (tự động vá cả Theme XML +mn-lt / +mj-lt)
- Ghi lời bình (Speaker Notes) tin cậy 100% cho mọi slide mới tạo (phục vụ Lồng tiếng AI)
- Tự động co giãn ảnh giữ nguyên tỷ lệ gốc (không bị méo/bẹt hình SGK)
- Hỗ trợ trọn bộ 7 Style bảng màu sư phạm & các bố cục trực quan GDPT 2018
"""

import os
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

try:
    from pptx import Presentation
    from pptx.util import Inches, Pt
    from pptx.dml.color import RGBColor
    from pptx.enum.text import PP_ALIGN
    from pptx.enum.shapes import MSO_SHAPE
except ImportError:
    import subprocess
    print("[*] Đang tự động cài đặt thư viện python-pptx...")
    subprocess.run([sys.executable, "-m", "pip", "install", "python-pptx", "--quiet"])
    from pptx import Presentation
    from pptx.util import Inches, Pt
    from pptx.dml.color import RGBColor
    from pptx.enum.text import PP_ALIGN
    from pptx.enum.shapes import MSO_SHAPE


# ─── BẢNG MÀU CHỦ ĐỀ CHUẨN MỰC (ĐẦY ĐỦ 7 THEME STYLES) ────────────────────────
THEMES = {
    "stem_navy": {
        "name": "Style 1: STEM Modern Navy & Gold (Toán, Lí, Tin, STEM)",
        "primary": RGBColor(0x1B, 0x3A, 0x6B),
        "accent": RGBColor(0xE8, 0x94, 0x1A),
        "bg": RGBColor(0xF0, 0xF5, 0xFB),
        "card_bg": RGBColor(0xFF, 0xFF, 0xFF),
        "text_dark": RGBColor(0x1E, 0x29, 0x3B),
        "box_q_bg": RGBColor(0xFF, 0xF3, 0xDB),
        "box_q_border": RGBColor(0xE8, 0x94, 0x1A),
        "box_note_bg": RGBColor(0xE8, 0xEF, 0xF8),
        "box_note_border": RGBColor(0x1B, 0x3A, 0x6B),
        "grid_colors": [
            (RGBColor(0xC0, 0x39, 0x2B), RGBColor(0xFD, 0xED, 0xEC)),
            (RGBColor(0xE8, 0x94, 0x1A), RGBColor(0xFF, 0xF3, 0xDB)),
            (RGBColor(0x16, 0xA0, 0x85), RGBColor(0xE8, 0xF8, 0xF5)),
            (RGBColor(0x1B, 0x3A, 0x6B), RGBColor(0xE8, 0xEF, 0xF8)),
        ],
    },
    "bio_emerald": {
        "name": "Style 2: Bio-Nature Emerald (Sinh học, KHTN, Môi trường)",
        "primary": RGBColor(0x0F, 0x51, 0x32),
        "accent": RGBColor(0xF5, 0x9E, 0x0B),
        "bg": RGBColor(0xF2, 0xF9, 0xF6),
        "card_bg": RGBColor(0xFF, 0xFF, 0xFF),
        "text_dark": RGBColor(0x1E, 0x29, 0x3B),
        "box_q_bg": RGBColor(0xFE, 0xF3, 0xC7),
        "box_q_border": RGBColor(0xD9, 0x77, 0x06),
        "box_note_bg": RGBColor(0xE8, 0xF5, 0xE9),
        "box_note_border": RGBColor(0x0F, 0x51, 0x32),
        "grid_colors": [
            (RGBColor(0x19, 0x87, 0x54), RGBColor(0xE8, 0xF5, 0xE9)),
            (RGBColor(0xD9, 0x77, 0x06), RGBColor(0xFE, 0xF3, 0xC7)),
            (RGBColor(0x02, 0x84, 0xC7), RGBColor(0xE0, 0xF2, 0xFE)),
            (RGBColor(0x7C, 0x3A, 0xED), RGBColor(0xF3, 0xE8, 0xFF)),
        ],
    },
    "chem_purple": {
        "name": "Style 3: Chem-Lab Royal Purple (Hóa học, Nguyên tử)",
        "primary": RGBColor(0x3B, 0x07, 0x64),
        "accent": RGBColor(0x06, 0xB6, 0xD4),
        "bg": RGBColor(0xF5, 0xF3, 0xFF),
        "card_bg": RGBColor(0xFF, 0xFF, 0xFF),
        "text_dark": RGBColor(0x1E, 0x29, 0x3B),
        "box_q_bg": RGBColor(0xCF, 0xFA, 0xFE),
        "box_q_border": RGBColor(0x08, 0x91, 0xB2),
        "box_note_bg": RGBColor(0xED, 0xE9, 0xFE),
        "box_note_border": RGBColor(0x6D, 0x28, 0xD9),
        "grid_colors": [
            (RGBColor(0x6D, 0x28, 0xD9), RGBColor(0xED, 0xE9, 0xFE)),
            (RGBColor(0x08, 0x91, 0xB2), RGBColor(0xCF, 0xFA, 0xFE)),
            (RGBColor(0xBE, 0x18, 0x5D), RGBColor(0xFC, 0xE7, 0xF3)),
            (RGBColor(0xEA, 0x58, 0x0C), RGBColor(0xFF, 0xED, 0xD5)),
        ],
    },
    "academic_pastel": {
        "name": "Style 4: Academic Contest Pastel (SKKN, Thi GVDG, Hội nghị)",
        "primary": RGBColor(0x1F, 0x4E, 0x79),
        "accent": RGBColor(0xB5, 0xC1, 0x15),
        "bg": RGBColor(0xF8, 0xFA, 0xFC),
        "card_bg": RGBColor(0xFF, 0xFF, 0xFF),
        "text_dark": RGBColor(0x1E, 0x29, 0x3B),
        "box_q_bg": RGBColor(0xF7, 0xF8, 0xE8),
        "box_q_border": RGBColor(0x8D, 0x99, 0x00),
        "box_note_bg": RGBColor(0xEF, 0xF6, 0xFF),
        "box_note_border": RGBColor(0x1F, 0x4E, 0x79),
        "grid_colors": [
            (RGBColor(0x29, 0x87, 0x71), RGBColor(0xE6, 0xF4, 0xF1)),
            (RGBColor(0x1F, 0x4E, 0x79), RGBColor(0xEF, 0xF6, 0xFF)),
            (RGBColor(0x8D, 0x99, 0x00), RGBColor(0xF7, 0xF8, 0xE8)),
            (RGBColor(0x8C, 0x21, 0x3E), RGBColor(0xFD, 0xE8, 0xEE)),
        ],
    },
    "gameshow_neon": {
        "name": "Style 5: Interactive Game Show (Rung chuông vàng, Khởi động)",
        "primary": RGBColor(0x0F, 0x29, 0x52),
        "accent": RGBColor(0xF5, 0x9E, 0x0B),
        "bg": RGBColor(0xEC, 0xFE, 0xFF),
        "card_bg": RGBColor(0xFF, 0xFF, 0xFF),
        "text_dark": RGBColor(0x0F, 0x17, 0x2A),
        "box_q_bg": RGBColor(0xFE, 0xF9, 0xC3),
        "box_q_border": RGBColor(0xD9, 0x77, 0x06),
        "box_note_bg": RGBColor(0xE0, 0xF2, 0xFE),
        "box_note_border": RGBColor(0x03, 0x69, 0xA1),
        "grid_colors": [
            (RGBColor(0x03, 0x69, 0xA1), RGBColor(0xE0, 0xF2, 0xFE)),
            (RGBColor(0xD9, 0x77, 0x06), RGBColor(0xFE, 0xF9, 0xC3)),
            (RGBColor(0x05, 0x96, 0x69), RGBColor(0xD1, 0xFA, 0xE5)),
            (RGBColor(0x7C, 0x3A, 0xED), RGBColor(0xED, 0xE9, 0xFE)),
        ],
    },
    "congress_red": {
        "name": "Style 6: Party Congress Red-Gold (Báo cáo chuyên đề, Lịch sử)",
        "primary": RGBColor(0x99, 0x00, 0x00),
        "accent": RGBColor(0xD9, 0x77, 0x06),
        "bg": RGBColor(0xFF, 0xFD, 0xF9),
        "card_bg": RGBColor(0xFF, 0xFF, 0xFF),
        "text_dark": RGBColor(0x1E, 0x29, 0x3B),
        "box_q_bg": RGBColor(0xFE, 0xF3, 0xC7),
        "box_q_border": RGBColor(0xD9, 0x77, 0x06),
        "box_note_bg": RGBColor(0xFD, 0xED, 0xEC),
        "box_note_border": RGBColor(0x99, 0x00, 0x00),
        "grid_colors": [
            (RGBColor(0x99, 0x00, 0x00), RGBColor(0xFD, 0xED, 0xEC)),
            (RGBColor(0xD9, 0x77, 0x06), RGBColor(0xFE, 0xF3, 0xC7)),
            (RGBColor(0x1B, 0x3A, 0x6B), RGBColor(0xE8, 0xEF, 0xF8)),
            (RGBColor(0x0F, 0x51, 0x32), RGBColor(0xE8, 0xF5, 0xE9)),
        ],
    },
    "hall_of_fame": {
        "name": "Style 7: Hall of Fame Gold (Tổng kết, Vinh danh)",
        "primary": RGBColor(0x1B, 0x26, 0x3B),
        "accent": RGBColor(0xC5, 0x9B, 0x27),
        "bg": RGBColor(0xF8, 0xF9, 0xFA),
        "card_bg": RGBColor(0xFF, 0xFF, 0xFF),
        "text_dark": RGBColor(0x1E, 0x29, 0x3B),
        "box_q_bg": RGBColor(0xFD, 0xF8, 0xE6),
        "box_q_border": RGBColor(0xC5, 0x9B, 0x27),
        "box_note_bg": RGBColor(0xEA, 0xEE, 0xF3),
        "box_note_border": RGBColor(0x1B, 0x26, 0x3B),
        "grid_colors": [
            (RGBColor(0x1B, 0x26, 0x3B), RGBColor(0xEA, 0xEE, 0xF3)),
            (RGBColor(0xC5, 0x9B, 0x27), RGBColor(0xFD, 0xF8, 0xE6)),
            (RGBColor(0x0F, 0x51, 0x32), RGBColor(0xE8, 0xF5, 0xE9)),
            (RGBColor(0x6D, 0x28, 0xD9), RGBColor(0xED, 0xE9, 0xFE)),
        ],
    },
}


class SlideBuilder:
    """Công cụ dựng slide bài giảng chuẩn mực sư phạm 16:9"""

    def __init__(self, theme_key="stem_navy", school="THCS Ứng Hòe", teacher="Thầy Nguyễn Văn Thiện"):
        self.prs = Presentation()
        self.prs.slide_width = Inches(13.333)
        self.prs.slide_height = Inches(7.5)
        self.blank_layout = self.prs.slide_layouts[6]
        self.theme = THEMES.get(theme_key, THEMES["stem_navy"])
        self.school = school
        self.teacher = teacher
        self.font_name = "Times New Roman"

    @staticmethod
    def _set_notes(slide, notes_text: str):
        """
        Ghi lời bình vào Speaker Notes của slide.
        LƯU Ý QUAN TRỌNG: Trong python-pptx, slide mới tạo có slide.has_notes_slide == False
        cho đến khi truy cập slide.notes_slide! Phải gọi thẳng slide.notes_slide để tự khởi tạo.
        """
        if notes_text and str(notes_text).strip():
            notes_slide = slide.notes_slide
            notes_slide.notes_text_frame.text = str(notes_text).strip()

    @staticmethod
    def _add_picture_contain(slide, image_path: str, box_left, box_top, box_w, box_h):
        """Chèn ảnh giữ nguyên tỷ lệ khung hình gốc (không làm méo hình SGK) và căn giữa trong khung."""
        try:
            from PIL import Image
            with Image.open(image_path) as im:
                iw, ih = im.size
            if iw > 0 and ih > 0:
                scale = min(float(box_w) / iw, float(box_h) / ih)
                new_w = int(iw * scale)
                new_h = int(ih * scale)
                left = int(box_left + (box_w - new_w) / 2)
                top = int(box_top + (box_h - new_h) / 2)
                return slide.shapes.add_picture(image_path, left, top, width=new_w, height=new_h)
        except Exception:
            pass
        return slide.shapes.add_picture(image_path, box_left, box_top, width=box_w, height=box_h)

    def _set_bg(self, slide):
        bg_shape = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5)
        )
        bg_shape.fill.solid()
        bg_shape.fill.fore_color.rgb = self.theme["bg"]
        bg_shape.line.color.rgb = self.theme["bg"]

    def _add_header_footer(self, slide, title_text, tag_text="BÀI HỌC", page_num=1, total_pages=10):
        header = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(1.1))
        header.fill.solid()
        header.fill.fore_color.rgb = self.theme["primary"]
        header.line.color.rgb = self.theme["primary"]

        accent_line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, Inches(1.1), Inches(13.333), Inches(0.06))
        accent_line.fill.solid()
        accent_line.fill.fore_color.rgb = self.theme["accent"]
        accent_line.line.color.rgb = self.theme["accent"]

        tag_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.4), Inches(0.12), Inches(3.4), Inches(0.3))
        tag_box.fill.solid()
        tag_box.fill.fore_color.rgb = self.theme["accent"]
        tag_box.line.color.rgb = self.theme["accent"]
        tf_tag = tag_box.text_frame
        tf_tag.word_wrap = True
        p_tag = tf_tag.paragraphs[0]
        p_tag.text = tag_text
        p_tag.font.name = self.font_name
        p_tag.font.size = Pt(13)
        p_tag.font.bold = True
        p_tag.font.color.rgb = RGBColor(255, 255, 255)
        p_tag.alignment = PP_ALIGN.CENTER

        title_box = slide.shapes.add_textbox(Inches(0.4), Inches(0.42), Inches(11.4), Inches(0.6))
        tf_title = title_box.text_frame
        tf_title.word_wrap = True
        p_title = tf_title.paragraphs[0]
        p_title.text = title_text
        p_title.font.name = self.font_name
        p_title.font.size = Pt(24)
        p_title.font.bold = True
        p_title.font.color.rgb = RGBColor(255, 255, 255)

        page_box = slide.shapes.add_textbox(Inches(11.8), Inches(0.42), Inches(1.2), Inches(0.6))
        tf_page = page_box.text_frame
        p_page = tf_page.paragraphs[0]
        p_page.text = f"{page_num:02d} / {total_pages:02d}"
        p_page.font.name = self.font_name
        p_page.font.size = Pt(14)
        p_page.font.bold = True
        p_page.font.color.rgb = RGBColor(220, 230, 242)
        p_page.alignment = PP_ALIGN.RIGHT

        footer = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, Inches(7.15), Inches(13.333), Inches(0.35))
        footer.fill.solid()
        footer.fill.fore_color.rgb = self.theme["primary"]
        footer.line.color.rgb = self.theme["primary"]

        ft_box = slide.shapes.add_textbox(Inches(0.4), Inches(7.15), Inches(12.5), Inches(0.35))
        tf_ft = ft_box.text_frame
        p_ft = tf_ft.paragraphs[0]
        p_ft.text = f"{self.school} • GV: {self.teacher}"
        p_ft.font.name = self.font_name
        p_ft.font.size = Pt(12)
        p_ft.font.color.rgb = RGBColor(255, 255, 255)

    def add_title_slide(self, lesson_name, subject="KHOA HỌC TỰ NHIÊN", grade="LỚP 6", unit="BÀI 1", notes_text=""):
        """Tạo Slide Trang Bìa bài giảng trang trọng"""
        slide = self.prs.slides.add_slide(self.blank_layout)
        self._set_bg(slide)

        cover_card = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), Inches(0.8), Inches(11.333), Inches(5.9)
        )
        cover_card.fill.solid()
        cover_card.fill.fore_color.rgb = RGBColor(255, 255, 255)
        cover_card.line.color.rgb = self.theme["primary"]
        cover_card.line.width = Pt(2.5)

        strip = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE, Inches(1.0), Inches(0.8), Inches(11.333), Inches(0.25)
        )
        strip.fill.solid()
        strip.fill.fore_color.rgb = self.theme["accent"]
        strip.line.color.rgb = self.theme["accent"]

        sch_box = slide.shapes.add_textbox(Inches(1.5), Inches(1.3), Inches(10.333), Inches(0.5))
        p = sch_box.text_frame.paragraphs[0]
        p.text = self.school.upper()
        p.font.name = self.font_name
        p.font.size = Pt(16)
        p.font.bold = True
        p.font.color.rgb = self.theme["primary"]
        p.alignment = PP_ALIGN.CENTER

        sub_box = slide.shapes.add_textbox(Inches(1.5), Inches(1.8), Inches(10.333), Inches(0.5))
        p = sub_box.text_frame.paragraphs[0]
        p.text = f"{subject} {grade}".upper()
        p.font.name = self.font_name
        p.font.size = Pt(20)
        p.font.bold = True
        p.font.color.rgb = self.theme["accent"]
        p.alignment = PP_ALIGN.CENTER

        title_box = slide.shapes.add_textbox(Inches(1.5), Inches(2.55), Inches(10.333), Inches(1.6))
        title_box.text_frame.word_wrap = True
        p = title_box.text_frame.paragraphs[0]
        p.text = f"{unit}\n{lesson_name}".upper()
        p.font.name = self.font_name
        p.font.size = Pt(32)
        p.font.bold = True
        p.font.color.rgb = self.theme["primary"]
        p.alignment = PP_ALIGN.CENTER

        gv_box = slide.shapes.add_textbox(Inches(1.5), Inches(4.8), Inches(10.333), Inches(0.8))
        p = gv_box.text_frame.paragraphs[0]
        p.text = f"Giáo viên thực hiện: {self.teacher}\nNăm học: 2026 - 2027"
        p.font.name = self.font_name
        p.font.size = Pt(16)
        p.font.color.rgb = self.theme["text_dark"]
        p.alignment = PP_ALIGN.CENTER

        self._set_notes(slide, notes_text)
        return slide

    def add_pedagogy_3step_slide(
        self,
        title_text,
        tag_text,
        image_path=None,
        image_caption="",
        question_title="CÂU HỎI THẢO LUẬN",
        questions=None,
        takeaway_title="EM CẦN GHI NHỚ",
        takeaways=None,
        page_num=2,
        total_pages=10,
        notes_text="",
    ):
        """Tạo Slide Trục Sư Phạm 3 Bước (Hình ảnh trực quan trái -> Thảo luận & Em cần ghi nhớ phải)"""
        slide = self.prs.slides.add_slide(self.blank_layout)
        self._set_bg(slide)
        self._add_header_footer(slide, title_text, tag_text, page_num, total_pages)

        img_box = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.4), Inches(1.3), Inches(5.8), Inches(5.6)
        )
        img_box.fill.solid()
        img_box.fill.fore_color.rgb = RGBColor(255, 255, 255)
        img_box.line.color.rgb = RGBColor(203, 213, 225)
        img_box.line.width = Pt(1.5)

        pic_added = False
        if image_path and os.path.exists(image_path):
            try:
                self._add_picture_contain(
                    slide, image_path, Inches(0.55), Inches(1.45), Inches(5.5), Inches(4.8)
                )
                pic_added = True
            except Exception as e:
                print(f"[!] Không thể chèn ảnh '{image_path}': {e}")

        if not pic_added:
            placeholder = slide.shapes.add_textbox(Inches(0.55), Inches(2.8), Inches(5.5), Inches(1.5))
            placeholder.text_frame.word_wrap = True
            p = placeholder.text_frame.paragraphs[0]
            p.text = f"🖼️ QUAN SÁT HÌNH ẢNH / VÍ DỤ\n{image_caption or title_text}"
            p.font.name = self.font_name
            p.font.size = Pt(18)
            p.font.bold = True
            p.font.color.rgb = RGBColor(100, 116, 139)
            p.alignment = PP_ALIGN.CENTER

        if image_caption:
            cap_box = slide.shapes.add_textbox(Inches(0.5), Inches(6.35), Inches(5.6), Inches(0.5))
            cap_box.text_frame.word_wrap = True
            p = cap_box.text_frame.paragraphs[0]
            p.text = image_caption
            p.font.name = self.font_name
            p.font.size = Pt(13)
            p.font.italic = True
            p.font.color.rgb = RGBColor(100, 116, 139)
            p.alignment = PP_ALIGN.CENTER

        # Cột phải trên: Câu hỏi thảo luận
        q_card = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.4), Inches(1.3), Inches(6.5), Inches(2.6)
        )
        q_card.fill.solid()
        q_card.fill.fore_color.rgb = self.theme["box_q_bg"]
        q_card.line.color.rgb = self.theme["box_q_border"]
        q_card.line.width = Pt(1.5)

        q_hdr = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE, Inches(6.4), Inches(1.3), Inches(6.5), Inches(0.45)
        )
        q_hdr.fill.solid()
        q_hdr.fill.fore_color.rgb = self.theme["box_q_border"]
        q_hdr.line.color.rgb = self.theme["box_q_border"]
        p_qhdr = q_hdr.text_frame.paragraphs[0]
        p_qhdr.text = f"❓ {question_title}"
        p_qhdr.font.name = self.font_name
        p_qhdr.font.size = Pt(15)
        p_qhdr.font.bold = True
        p_qhdr.font.color.rgb = RGBColor(255, 255, 255)

        q_body = slide.shapes.add_textbox(Inches(6.55), Inches(1.85), Inches(6.2), Inches(1.9))
        tf_q = q_body.text_frame
        tf_q.word_wrap = True
        questions = questions or ["Quan sát hình ảnh và nêu nhận xét của em?"]
        for idx, q_txt in enumerate(questions):
            p = tf_q.paragraphs[0] if idx == 0 else tf_q.add_paragraph()
            p.text = f"▸ {q_txt}"
            p.font.name = self.font_name
            p.font.size = Pt(16)
            p.font.color.rgb = self.theme["text_dark"]
            p.space_after = Pt(6)

        # Cột phải dưới: Em cần ghi nhớ (Ngôn ngữ lớp học chuẩn mực, không ghi từ lý luận)
        note_card = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.4), Inches(4.1), Inches(6.5), Inches(2.8)
        )
        note_card.fill.solid()
        note_card.fill.fore_color.rgb = self.theme["box_note_bg"]
        note_card.line.color.rgb = self.theme["box_note_border"]
        note_card.line.width = Pt(1.5)

        note_hdr = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE, Inches(6.4), Inches(4.1), Inches(6.5), Inches(0.45)
        )
        note_hdr.fill.solid()
        note_hdr.fill.fore_color.rgb = self.theme["box_note_border"]
        note_hdr.line.color.rgb = self.theme["box_note_border"]
        p_nhdr = note_hdr.text_frame.paragraphs[0]
        p_nhdr.text = f"💡 {takeaway_title}"
        p_nhdr.font.name = self.font_name
        p_nhdr.font.size = Pt(15)
        p_nhdr.font.bold = True
        p_nhdr.font.color.rgb = RGBColor(255, 255, 255)

        note_body = slide.shapes.add_textbox(Inches(6.55), Inches(4.65), Inches(6.2), Inches(2.1))
        tf_note = note_body.text_frame
        tf_note.word_wrap = True
        takeaways = takeaways or ["Khái niệm cốt lõi cần ghi nhớ.", "Quy tắc và công thức áp dụng."]
        for idx, n_txt in enumerate(takeaways):
            p = tf_note.paragraphs[0] if idx == 0 else tf_note.add_paragraph()
            p.text = f"▸ {n_txt}"
            p.font.name = self.font_name
            p.font.size = Pt(16)
            p.font.bold = (idx == 0)
            p.font.color.rgb = self.theme["primary"]
            p.space_after = Pt(6)

        self._set_notes(slide, notes_text)
        return slide

    def add_grid_2x2_slide(self, title_text, tag_text, items, page_num=3, total_pages=10, notes_text=""):
        """Tạo Slide Lưới 4 Ô Màu Sắc Phân Nhóm (Layout 2)"""
        slide = self.prs.slides.add_slide(self.blank_layout)
        self._set_bg(slide)
        self._add_header_footer(slide, title_text, tag_text, page_num, total_pages)

        coords = [
            (Inches(0.6), Inches(1.35)),
            (Inches(6.8), Inches(1.35)),
            (Inches(0.6), Inches(4.25)),
            (Inches(6.8), Inches(4.25)),
        ]
        grid_colors = self.theme.get(
            "grid_colors",
            [
                (self.theme["primary"], self.theme["bg"]),
                (self.theme["accent"], self.theme["box_q_bg"]),
                (self.theme["primary"], self.theme["bg"]),
                (self.theme["accent"], self.theme["box_q_bg"]),
            ],
        )

        for idx, (x, y) in enumerate(coords):
            if idx >= len(items):
                break
            item = items[idx]
            border_c, fill_c = grid_colors[idx % len(grid_colors)]

            card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, Inches(5.9), Inches(2.65))
            card.fill.solid()
            card.fill.fore_color.rgb = fill_c
            card.line.color.rgb = border_c
            card.line.width = Pt(1.5)

            hdr = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, Inches(5.9), Inches(0.45))
            hdr.fill.solid()
            hdr.fill.fore_color.rgb = border_c
            hdr.line.color.rgb = border_c
            p_hdr = hdr.text_frame.paragraphs[0]
            p_hdr.text = f"{idx + 1}. {item.get('title', '')}"
            p_hdr.font.name = self.font_name
            p_hdr.font.size = Pt(15)
            p_hdr.font.bold = True
            p_hdr.font.color.rgb = RGBColor(255, 255, 255)

            tb = slide.shapes.add_textbox(x + Inches(0.15), y + Inches(0.55), Inches(5.6), Inches(1.95))
            tf = tb.text_frame
            tf.word_wrap = True
            points = item.get("points", [])
            for p_idx, pt in enumerate(points):
                p = tf.paragraphs[0] if p_idx == 0 else tf.add_paragraph()
                p.text = f"▸ {pt}"
                p.font.name = self.font_name
                p.font.size = Pt(15)
                p.font.color.rgb = self.theme["text_dark"]
                p.space_after = Pt(4)

        self._set_notes(slide, notes_text)
        return slide

    def add_cards_3row_slide(self, title_text, tag_text, cards_data, page_num=4, total_pages=10, notes_text=""):
        """Tạo Slide 3 Dải Thẻ Ngang Đánh Số Lớn (Layout 3)"""
        slide = self.prs.slides.add_slide(self.blank_layout)
        self._set_bg(slide)
        self._add_header_footer(slide, title_text, tag_text, page_num, total_pages)

        y_positions = [Inches(1.35), Inches(3.25), Inches(5.15)]
        for idx, y in enumerate(y_positions):
            if idx >= len(cards_data):
                break
            c_info = cards_data[idx]

            card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.6), y, Inches(12.133), Inches(1.65))
            card.fill.solid()
            card.fill.fore_color.rgb = RGBColor(255, 255, 255)
            card.line.color.rgb = self.theme["primary"]
            card.line.width = Pt(1.5)

            num_box = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.6), y, Inches(1.2), Inches(1.65))
            num_box.fill.solid()
            num_box.fill.fore_color.rgb = self.theme["primary"]
            num_box.line.color.rgb = self.theme["primary"]
            p_num = num_box.text_frame.paragraphs[0]
            p_num.text = f"{idx + 1:02d}"
            p_num.font.name = self.font_name
            p_num.font.size = Pt(32)
            p_num.font.bold = True
            p_num.font.color.rgb = RGBColor(255, 255, 255)
            p_num.alignment = PP_ALIGN.CENTER

            tb = slide.shapes.add_textbox(Inches(2.0), y + Inches(0.1), Inches(10.5), Inches(1.45))
            tf = tb.text_frame
            tf.word_wrap = True
            p_t = tf.paragraphs[0]
            p_t.text = c_info.get("title", "")
            p_t.font.name = self.font_name
            p_t.font.size = Pt(18)
            p_t.font.bold = True
            p_t.font.color.rgb = self.theme["accent"]

            p_desc = tf.add_paragraph()
            p_desc.text = c_info.get("desc", "")
            p_desc.font.name = self.font_name
            p_desc.font.size = Pt(15)
            p_desc.font.color.rgb = self.theme["text_dark"]

        self._set_notes(slide, notes_text)
        return slide

    def add_process_flow_slide(self, title_text, tag_text, steps_data, page_num=5, total_pages=10, notes_text=""):
        """Tạo Slide Sơ Đồ Chuỗi Quy Trình Ngang (Layout 4)"""
        slide = self.prs.slides.add_slide(self.blank_layout)
        self._set_bg(slide)
        self._add_header_footer(slide, title_text, tag_text, page_num, total_pages)

        n = min(max(len(steps_data), 1), 4)
        total_w = 12.133
        gap = 0.35
        card_w = (total_w - gap * (n - 1)) / n

        for idx in range(n):
            st = steps_data[idx]
            x = Inches(0.6 + idx * (card_w + gap))
            y = Inches(1.65)

            card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, Inches(card_w), Inches(4.9))
            card.fill.solid()
            card.fill.fore_color.rgb = RGBColor(255, 255, 255)
            card.line.color.rgb = self.theme["primary"]
            card.line.width = Pt(1.75)

            badge = slide.shapes.add_shape(MSO_SHAPE.OVAL, x + Inches(card_w / 2 - 0.45), Inches(1.25), Inches(0.9), Inches(0.9))
            badge.fill.solid()
            badge.fill.fore_color.rgb = self.theme["accent"]
            badge.line.color.rgb = RGBColor(255, 255, 255)
            badge.line.width = Pt(2)
            pb = badge.text_frame.paragraphs[0]
            pb.text = str(idx + 1)
            pb.font.name = self.font_name
            pb.font.size = Pt(20)
            pb.font.bold = True
            pb.font.color.rgb = RGBColor(255, 255, 255)
            pb.alignment = PP_ALIGN.CENTER

            tb = slide.shapes.add_textbox(x + Inches(0.15), Inches(2.25), Inches(card_w - 0.3), Inches(4.1))
            tf = tb.text_frame
            tf.word_wrap = True
            pt = tf.paragraphs[0]
            pt.text = st.get("title", f"Bước {idx + 1}")
            pt.font.name = self.font_name
            pt.font.size = Pt(17)
            pt.font.bold = True
            pt.font.color.rgb = self.theme["primary"]
            pt.alignment = PP_ALIGN.CENTER
            pt.space_after = Pt(10)

            pd = tf.add_paragraph()
            pd.text = st.get("desc", "")
            pd.font.name = self.font_name
            pd.font.size = Pt(15)
            pd.font.color.rgb = self.theme["text_dark"]

        self._set_notes(slide, notes_text)
        return slide

    def add_quiz_slide(
        self,
        title_text,
        tag_text,
        question_text,
        options,
        correct_key="A",
        explanation="",
        reveal_answer=False,
        page_num=6,
        total_pages=10,
        notes_text="",
    ):
        """
        Tạo Slide Câu Hỏi Trắc Nghiệm / Luyện Tập 4 Đáp Án (Layout 8).
        Mặc định reveal_answer=False để chiếu trên lớp không lộ sẵn đáp án trước khi học sinh suy nghĩ!
        """
        slide = self.prs.slides.add_slide(self.blank_layout)
        self._set_bg(slide)
        self._add_header_footer(slide, title_text, tag_text, page_num, total_pages)

        q_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.6), Inches(1.35), Inches(12.133), Inches(1.8))
        q_box.fill.solid()
        q_box.fill.fore_color.rgb = RGBColor(255, 255, 255)
        q_box.line.color.rgb = self.theme["primary"]
        q_box.line.width = Pt(2.0)

        tf_q = q_box.text_frame
        tf_q.word_wrap = True
        p_q = tf_q.paragraphs[0]
        p_q.text = f"❓ CÂU HỎI: {question_text}"
        p_q.font.name = self.font_name
        p_q.font.size = Pt(19)
        p_q.font.bold = True
        p_q.font.color.rgb = self.theme["primary"]

        opt_coords = [
            ("A", Inches(0.6), Inches(3.35)),
            ("B", Inches(6.8), Inches(3.35)),
            ("C", Inches(0.6), Inches(4.75)),
            ("D", Inches(6.8), Inches(4.75)),
        ]

        for key, x, y in opt_coords:
            opt_text = options.get(key, "") if isinstance(options, dict) else ""
            is_correct = reveal_answer and (key == str(correct_key).upper())

            opt_card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, Inches(5.9), Inches(1.2))
            opt_card.fill.solid()
            opt_card.fill.fore_color.rgb = RGBColor(240, 253, 244) if is_correct else RGBColor(255, 255, 255)
            opt_card.line.color.rgb = RGBColor(34, 197, 94) if is_correct else RGBColor(203, 213, 225)
            opt_card.line.width = Pt(2.2 if is_correct else 1.2)

            badge = slide.shapes.add_shape(MSO_SHAPE.OVAL, x + Inches(0.15), y + Inches(0.2), Inches(0.8), Inches(0.8))
            badge.fill.solid()
            badge.fill.fore_color.rgb = RGBColor(22, 163, 74) if is_correct else self.theme["accent"]
            badge.line.color.rgb = RGBColor(22, 163, 74) if is_correct else self.theme["accent"]
            p_b = badge.text_frame.paragraphs[0]
            p_b.text = key
            p_b.font.name = self.font_name
            p_b.font.size = Pt(18)
            p_b.font.bold = True
            p_b.font.color.rgb = RGBColor(255, 255, 255)
            p_b.alignment = PP_ALIGN.CENTER

            tb = slide.shapes.add_textbox(x + Inches(1.05), y + Inches(0.15), Inches(4.7), Inches(0.9))
            tf = tb.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            p.text = opt_text
            p.font.name = self.font_name
            p.font.size = Pt(16)
            p.font.color.rgb = self.theme["text_dark"]

        if reveal_answer and explanation:
            exp_box = slide.shapes.add_textbox(Inches(0.6), Inches(6.15), Inches(12.133), Inches(0.85))
            tf_exp = exp_box.text_frame
            tf_exp.word_wrap = True
            p_exp = tf_exp.paragraphs[0]
            p_exp.text = f"💡 ĐÁP ÁN ĐÚNG: [{correct_key}] — {explanation}"
            p_exp.font.name = self.font_name
            p_exp.font.size = Pt(15)
            p_exp.font.bold = True
            p_exp.font.color.rgb = RGBColor(22, 163, 74)

        self._set_notes(slide, notes_text)
        return slide

    def save(self, output_path):
        """Lưu file PowerPoint hoàn chỉnh & tự động đồng bộ Theme Font về Times New Roman 100%"""
        out_p = Path(output_path).resolve()
        out_p.parent.mkdir(parents=True, exist_ok=True)
        self.prs.save(str(out_p))
        try:
            from patch_fonts import patch_pptx
            patch_pptx(str(out_p), quiet=True)
        except Exception:
            pass
        print(f"[OK] Đã xuất file PowerPoint chuẩn mực sư phạm tại: {out_p}")
        return str(out_p)
