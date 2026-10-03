#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pdf_exam_exporter.py — Xuất PDF Đẹp Chuẩn In Ấn Qua LaTeX
=======================================================
Tự động sinh mã LaTeX → biên dịch PDF đẹp như sách giáo khoa.
Hỗ trợ 6 theme màu sắc + tùy chỉnh qua JSON config + chat tự nhiên.
Tương thích hoàn toàn với exam_data dict của gdpt2018_validator.py.

Sử dụng:
    from scripts.pdf_exam_exporter import ExamPDFExporter, export_exam_pdf
    exporter = ExamPDFExporter(theme='teal')
    exporter.export_both(exam_data, meta, output_dir='output/')
"""

from __future__ import annotations
import os
import sys
import re
import json
import shutil
import tempfile
import subprocess
from pathlib import Path
from typing import Optional

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

# ─────────────────────────────────────────────────────────────────────
# 6 THEME MÀU SẮC CÓ SẴN
# ─────────────────────────────────────────────────────────────────────

BUILTIN_THEMES = {
    "teal": {
        "name": "Teal — Chuyên nghiệp (Mặc định)",
        "color_primary": "1A7070",
        "color_secondary": "2C3E50",
        "color_solution_bg": "F0F4F4",
        "description": "Xanh teal chuyên nghiệp như ảnh mẫu.",
    },
    "navy": {
        "name": "Navy — Trang trọng",
        "color_primary": "1B3A6B",
        "color_secondary": "0D1F3C",
        "color_solution_bg": "EEF2F8",
        "description": "Xanh nước biển trang trọng. Phù hợp đề thi học kỳ.",
    },
    "red": {
        "name": "Red — Nổi bật",
        "color_primary": "C0392B",
        "color_secondary": "7B241C",
        "color_solution_bg": "FDECEA",
        "description": "Màu đỏ nổi bật. Phù hợp đề ôn luyện cường độ cao.",
    },
    "minimal": {
        "name": "Minimal — Tiết kiệm mực",
        "color_primary": "2C2C2C",
        "color_secondary": "1A1A1A",
        "color_solution_bg": "F5F5F5",
        "description": "Trắng đen tối giản. Tiết kiệm mực in tối đa.",
    },
    "purple": {
        "name": "Purple — Sáng tạo",
        "color_primary": "6C3483",
        "color_secondary": "4A235A",
        "color_solution_bg": "F5EEF8",
        "description": "Màu tím sáng tạo. Phù hợp THCS, trường chuyên.",
    },
    "classic": {
        "name": "Classic — Truyền thống",
        "color_primary": "1A5276",
        "color_secondary": "154360",
        "color_solution_bg": "EBF5FB",
        "description": "Xanh dương truyền thống chuẩn SGK Việt Nam.",
    },
}

# ─────────────────────────────────────────────────────────────────────
# HÀM TRỢ GIÚP
# ─────────────────────────────────────────────────────────────────────

_LATEX_ESCAPE = {
    '&': r'\&', '%': r'\%', '$': r'\$', '#': r'\#',
    '_': r'\_', '{': r'\{', '}': r'\}',
    '~': r'\textasciitilde{}', '^': r'\textasciicircum{}',
}


def escape_latex(text: str) -> str:
    """Escape ký tự đặc biệt LaTeX nhưng BẢO TOÀN công thức $...$."""
    if not text:
        return ""
    parts = re.split(r'(\$\$[^$]*\$\$|\$[^$]*\$)', text)
    result = []
    for part in parts:
        if part.startswith('$'):
            result.append(part)
        else:
            s = part.replace('\\', r'\textbackslash{}')
            for ch, repl in _LATEX_ESCAPE.items():
                s = s.replace(ch, repl)
            result.append(s)
    return ''.join(result)


def _detect_compiler() -> str:
    for c in ('xelatex', 'pdflatex'):
        if shutil.which(c):
            return c
    return ''


# ─────────────────────────────────────────────────────────────────────
# SINH MÃ LATEX CHO TỪNG PHẦN
# ─────────────────────────────────────────────────────────────────────

def _gen_part1(questions: list, show_solutions: bool) -> str:
    lines = [
        r'\exampart{I}{Câu trắc nghiệm nhiều phương án lựa chọn.}'
        r'{Học sinh trả lời từ câu 1 đến câu 12.'
        r' Mỗi câu hỏi học sinh chỉ chọn một phương án.}',
    ]
    for i, q in enumerate(questions, 1):
        tag = q.get('tag', '')
        tag_str = f" ({escape_latex(tag)})" if tag else ''
        qtext = escape_latex(q.get('question', ''))
        lines.append(rf'\examquestion{{{i}}}{{{tag_str}}}{{{qtext}}}')
        opts = q.get('options', [])
        if len(opts) == 4:
            a, b, c, d = [escape_latex(str(o)) for o in opts]
            max_len = max(len(str(o)) for o in opts)
            if max_len <= 22:
                lines.append(rf'\choicesFour{{{a}}}{{{b}}}{{{c}}}{{{d}}}')
            elif max_len <= 50:
                lines.append(rf'\choicesTwo{{{a}}}{{{b}}}{{{c}}}{{{d}}}')
            else:
                lines.append(rf'\choicesOne{{{a}}}{{{b}}}{{{c}}}{{{d}}}')
        fig = q.get('figure_path', '')
        if fig and Path(fig).exists():
            lines.append(rf'\examfigure{{{Path(fig).name}}}')
        if show_solutions:
            sol = q.get('solution', '')
            ans = q.get('answer', '')
            sol_text = escape_latex(sol) if sol else \
                rf'\textit{{Đáp án: \textbf{{{escape_latex(str(ans))}}}}}'
            lines.append(rf'\begin{{solutionbox}}{sol_text}\end{{solutionbox}}')
    return '\n'.join(lines)


def _gen_part2(questions: list, show_solutions: bool) -> str:
    lines = [
        r'\exampart{II}{Câu trắc nghiệm Đúng/Sai.}'
        r'{Trong mỗi ý a), b), c), d), học sinh chọn Đúng hoặc Sai.}',
    ]
    for i, q in enumerate(questions, 1):
        stem = escape_latex(q.get('stem', ''))
        lines.append(rf'\examquestion{{{i}}}{{}}{{{stem}}}')
        fig = q.get('figure_path', '')
        if fig and Path(fig).exists():
            lines.append(rf'\examfigure{{{Path(fig).name}}}')
        items = q.get('items', [])
        lines.append(r'\begin{truefalsetable}')
        for item in items:
            label = escape_latex(item.get('label', ''))
            stmt = escape_latex(item.get('statement', ''))
            lines.append(rf'\truefalserow{{{label}}}{{{stmt}}}')
        lines.append(r'\end{truefalsetable}')
        if show_solutions:
            sol = q.get('solution', '')
            ans_parts = []
            for item in items:
                lbl = item.get('label', '')
                ans = 'Đúng' if item.get('answer') else 'Sai'
                ans_parts.append(rf'\textbf{{{lbl}}}) {ans}')
            ans_str = r' --- '.join(ans_parts)
            full_sol = (escape_latex(sol) + '\n\n' if sol else '') + \
                       rf'\textit{{Đáp án: {ans_str}}}'
            lines.append(rf'\begin{{solutionbox}}{full_sol}\end{{solutionbox}}')
    return '\n'.join(lines)


def _gen_part3(questions: list, show_solutions: bool) -> str:
    lines = [
        r'\exampart{III}{Câu trả lời ngắn.}'
        r'{Học sinh điền kết quả vào ô KẾT QUẢ.}',
    ]
    for i, q in enumerate(questions, 1):
        qtext = escape_latex(q.get('question', ''))
        lines.append(rf'\shortanswerquestion{{{i}}}{{{qtext}}}')
        fig = q.get('figure_path', '')
        if fig and Path(fig).exists():
            lines.append(rf'\examfigure{{{Path(fig).name}}}')
        if show_solutions:
            ans = q.get('answer', '')
            sol = q.get('solution', '')
            sol_text = escape_latex(sol) if sol else \
                rf'Kết quả: $\mathbf{{{escape_latex(str(ans))}}}$'
            lines.append(rf'\begin{{solutionbox}}{sol_text}\end{{solutionbox}}')
    return '\n'.join(lines)


def _gen_essay(questions: list, show_solutions: bool) -> str:
    if not questions:
        return ''
    lines = [
        r'\exampart{Tự luận}{Câu tự luận.}'
        r'{Học sinh trình bày lời giải chi tiết.}',
    ]
    for i, q in enumerate(questions, 1):
        qtext = escape_latex(q.get('question', ''))
        pts = q.get('points', 0)
        pts_str = f" ({pts} điểm)" if pts else ''
        lines.append(rf'\examquestion{{{i}}}{{{escape_latex(pts_str)}}}{{{qtext}}}')
        fig = q.get('figure_path', '')
        if fig and Path(fig).exists():
            lines.append(rf'\examfigure{{{Path(fig).name}}}')
        if show_solutions:
            sol = q.get('solution', '')
            if sol:
                lines.append(
                    rf'\begin{{solutionbox}}{escape_latex(sol)}\end{{solutionbox}}'
                )
    return '\n'.join(lines)


# ─────────────────────────────────────────────────────────────────────
# SINH PREAMBLE LATEX
# ─────────────────────────────────────────────────────────────────────

def _build_preamble(style: dict, compiler: str) -> str:
    cp  = style.get('color_primary',     '1A7070')
    cs  = style.get('color_secondary',   '2C3E50')
    cbg = style.get('color_solution_bg', 'F0F4F4')
    school_name  = style.get('school_name',  'Tên Trường')
    school_dept  = style.get('school_dept',  'Môn Học')
    contact_info = style.get('contact_info', '')
    footer_left  = style.get('footer_left',  'Tên Trường')
    footer_right = style.get('footer_right', 'Chúc em làm bài tốt!')
    logo_path    = style.get('logo_path',    '')
    watermark    = style.get('watermark',    False)

    if compiler == 'xelatex':
        font_pkg = r"""
\usepackage{fontspec}
\setmainfont{Times New Roman}
\setsansfont{Arial}"""
    else:
        font_pkg = r"""
\usepackage[utf8]{inputenc}
\usepackage[T5]{fontenc}
\usepackage{times}"""

    logo_cmd = ''
    if logo_path and Path(logo_path).exists():
        logo_cmd = rf'\includegraphics[height=0.9cm]{{{Path(logo_path).name}}}'

    wm_pkg = ''
    if watermark:
        wm_pkg = (r'\usepackage{draftwatermark}' + '\n' +
                  r'\SetWatermarkText{BAN NHAP}' + '\n' +
                  r'\SetWatermarkScale{3}' + '\n' +
                  r'\SetWatermarkColor[gray]{0.90}')

    en  = escape_latex
    return rf"""%!TEX program = {compiler}
\documentclass[12pt,a4paper]{{article}}
{font_pkg}
\usepackage[vietnamese]{{babel}}
\usepackage{{amsmath,amssymb,amsfonts,mathtools}}
\usepackage{{xcolor}}
\usepackage[a4paper,top=2.2cm,bottom=2.2cm,left=2.0cm,right=1.8cm,headheight=1.6cm]{{geometry}}
\usepackage{{fancyhdr}}
\usepackage[most,breakable]{{tcolorbox}}
\usepackage{{tabularx}}
\usepackage{{multicol}}
\usepackage{{graphicx}}
\usepackage[export]{{adjustbox}}
\usepackage{{tikz}}
\usepackage{{enumitem}}
\usepackage{{array}}
\usepackage{{colortbl}}
\usepackage{{booktabs}}
{wm_pkg}

\definecolor{{PrimaryColor}}{{HTML}}{{{cp}}}
\definecolor{{SecondaryColor}}{{HTML}}{{{cs}}}
\definecolor{{SolutionBg}}{{HTML}}{{{cbg}}}

\pagestyle{{fancy}}
\fancyhf{{}}
\renewcommand{{\headrulewidth}}{{0pt}}
\fancyhead[L]{{%
  \colorbox{{SecondaryColor}}{{%
    \parbox[c][1.1cm][c]{{0.44\textwidth}}{{%
      \centering\color{{white}}\small\bfseries
      {en(school_name)}\\{en(school_dept)}%
    }}%
  }}%
}}
\fancyhead[R]{{%
  \colorbox{{PrimaryColor}}{{%
    \parbox[c][1.1cm][c]{{0.44\textwidth}}{{%
      \centering\color{{white}}\small
      {en(contact_info)}\\{logo_cmd}%
    }}%
  }}%
}}
\fancyhead[C]{{\colorbox{{white}}{{\textbf{{\thepage}}}}}}
\fancyfoot[L]{{%
  \colorbox{{SecondaryColor}}{{%
    \parbox[c][0.7cm][c]{{0.46\textwidth}}{{%
      \centering\color{{white}}\small\bfseries {en(footer_left)}%
    }}%
  }}%
}}
\fancyfoot[R]{{%
  \colorbox{{PrimaryColor}}{{%
    \parbox[c][0.7cm][c]{{0.46\textwidth}}{{%
      \centering\color{{white}}\small\itshape {en(footer_right)}%
    }}%
  }}%
}}

\newcommand{{\exampart}}[3]{{%
  \vspace{{8pt}}%
  \noindent\textbf{{PHẦN \MakeUppercase{{#1}}.}} \textit{{\textbf{{#2}}}} #3%
  \vspace{{4pt}}%
}}
\newcommand{{\examquestion}}[3]{{%
  \vspace{{6pt}}%
  \noindent{{\textcolor{{PrimaryColor}}{{\textbf{{Câu~#1#2.}}}}}}~#3%
  \vspace{{2pt}}%
}}
\newcommand{{\shortanswerquestion}}[2]{{%
  \vspace{{6pt}}%
  \begin{{minipage}}[t]{{0.70\textwidth}}%
    \noindent{{\textcolor{{PrimaryColor}}{{\textbf{{Câu~#1.}}}}}}~#2%
  \end{{minipage}}%
  \hfill%
  \begin{{minipage}}[t]{{0.26\textwidth}}%
    \begin{{tcolorbox}}[colback=white,colframe=PrimaryColor,%
      colbacktitle=PrimaryColor,%
      title={{\centering\tiny\bfseries\color{{white}} KẾT QUẢ}},%
      halign=center,left=1pt,right=1pt,top=2pt,bottom=4pt]%
    \begin{{tabular}}{{|c|c|c|c|}}%
      \hline%
      \rule{{0pt}}{{14pt}}\phantom{{W}}&\phantom{{W}}&\phantom{{W}}&\phantom{{W}}\\%
      \hline%
    \end{{tabular}}%
    \end{{tcolorbox}}%
  \end{{minipage}}%
  \vspace{{2pt}}%
}}
\newcommand{{\choiceitem}}[2]{{%
  \tikz[baseline=(N.base)]{{\node[fill=PrimaryColor,text=white,rounded corners=3pt,%
    inner xsep=4pt,inner ysep=2pt,font=\small\bfseries](N){{#1}};}}%
  \;#2%
}}
\newcommand{{\choicesFour}}[4]{{%
  \vspace{{2pt}}%
  \begin{{tabularx}}{{\textwidth}}{{XXXX}}%
    \choiceitem{{A}}{{#1}}&\choiceitem{{B}}{{#2}}&%
    \choiceitem{{C}}{{#3}}&\choiceitem{{D}}{{#4}}%
  \end{{tabularx}}%
  \vspace{{2pt}}%
}}
\newcommand{{\choicesTwo}}[4]{{%
  \vspace{{2pt}}%
  \begin{{tabularx}}{{\textwidth}}{{XX}}%
    \choiceitem{{A}}{{#1}}&\choiceitem{{B}}{{#2}}\\%
    \choiceitem{{C}}{{#3}}&\choiceitem{{D}}{{#4}}%
  \end{{tabularx}}%
  \vspace{{2pt}}%
}}
\newcommand{{\choicesOne}}[4]{{%
  \vspace{{2pt}}%
  \begin{{itemize}}[leftmargin=1.2cm,label={{}},itemsep=1pt]%
    \item\choiceitem{{A}}{{#1}}%
    \item\choiceitem{{B}}{{#2}}%
    \item\choiceitem{{C}}{{#3}}%
    \item\choiceitem{{D}}{{#4}}%
  \end{{itemize}}%
  \vspace{{2pt}}%
}}
\newcommand{{\examfigure}}[1]{{%
  \begin{{center}}%
    \includegraphics[max width=0.72\textwidth,max height=8cm]{{#1}}%
  \end{{center}}%
}}
\newtcolorbox{{solutionbox}}[1][]{{%
  breakable,enhanced,%
  colback=SolutionBg,colframe=SolutionBg,%
  boxrule=0pt,arc=4pt,%
  left=8pt,right=8pt,top=4pt,bottom=4pt,%
  before upper={{\textcolor{{PrimaryColor}}{{\textbf{{\textit{{\small$\mathcal{{Q}}$\,Lời giải.}}}}}}\;}},%
  #1%
}}
\newenvironment{{truefalsetable}}{{%
  \vspace{{4pt}}%
  \begin{{tabularx}}{{\textwidth}}{{|X|c|c|}}%
  \hline%
  \rowcolor{{PrimaryColor}}%
  \color{{white}}\bfseries Mệnh đề &%
  \color{{white}}\bfseries Đúng &%
  \color{{white}}\bfseries Sai\\%
  \hline%
}}{{%
  \hline%
  \end{{tabularx}}%
  \vspace{{4pt}}%
}}
\newcommand{{\truefalserow}}[2]{{%
  \textbf{{#1)}}~#2&$\bigcirc$&$\bigcirc$\\\hline%
}}
\setlength{{\parindent}}{{0pt}}
\setlength{{\parskip}}{{3pt}}
\setlength{{\tabcolsep}}{{6pt}}

\begin{{document}}
"""


def _build_title(meta: dict) -> str:
    series = escape_latex(meta.get('series_name', 'BỘ ĐỀ ÔN TẬP').replace('\n', r'\\'))
    code   = escape_latex(str(meta.get('exam_code', '0101')))
    title  = escape_latex(meta.get('exam_title', 'ĐỀ THI TỐT NGHIỆP THPT'))
    subj   = escape_latex(str(meta.get('subject', 'Toán')))
    grade  = meta.get('grade', 12)
    yr     = escape_latex(meta.get('school_year', '2025 -- 2026'))
    dur    = meta.get('duration_minutes', 90)
    return rf"""
\vspace{{6pt}}
\noindent
\begin{{tcolorbox}}[enhanced,boxrule=1pt,arc=3pt,
  colframe=PrimaryColor,colback=white,
  sidebyside,sidebyside align=top,lefthand width=3.6cm]
  \centering
  {{\small\bfseries {series}}}\\
  \vspace{{4pt}}
  \begin{{tcolorbox}}[colback=PrimaryColor,colframe=PrimaryColor,arc=3pt,
    fontupper=\color{{white}}\bfseries\small,halign=center]
    MÃ ĐỀ: {code}
  \end{{tcolorbox}}
\tcblower
  \centering
  {{\large\bfseries {title}}}\\[4pt]
  \textit{{Môn: {subj}~{grade} \quad---\quad Năm học: {yr}}}\\[2pt]
  \textit{{Thời gian làm bài: {dur} phút (Không kể thời gian phát đề)}}
\end{{tcolorbox}}
\vspace{{6pt}}
"""


def _build_document(meta, exam_data, show_solutions, style, compiler):
    preamble = _build_preamble(style, compiler)
    title    = _build_title(meta)
    parts    = [preamble, title]
    if exam_data.get('part1_mc'):
        parts.append(_gen_part1(exam_data['part1_mc'], show_solutions))
    if exam_data.get('part2_tf'):
        parts.append(_gen_part2(exam_data['part2_tf'], show_solutions))
    if exam_data.get('part3_sa'):
        parts.append(_gen_part3(exam_data['part3_sa'], show_solutions))
    if exam_data.get('essay'):
        parts.append(_gen_essay(exam_data['essay'], show_solutions))
    parts.append(r'\end{document}')
    return '\n\n'.join(parts)


# ─────────────────────────────────────────────────────────────────────
# LỚP ExamPDFExporter
# ─────────────────────────────────────────────────────────────────────

class ExamPDFExporter:
    """Xuất đề thi PDF đẹp chuẩn in ấn từ dữ liệu exam_data."""

    def __init__(self, theme='teal', style_config=None, style_file=None):
        self.style = dict(BUILTIN_THEMES.get(theme.lower(), BUILTIN_THEMES['teal']))
        if style_file and Path(style_file).exists():
            with open(style_file, encoding='utf-8') as f:
                self.style.update(json.load(f))
        if style_config:
            self.style.update(style_config)
        self.compiler = _detect_compiler()

    def apply_chat_command(self, command: str) -> str:
        """Xử lý lệnh tùy chỉnh tự nhiên từ chat."""
        cmd = command.lower().strip()
        theme_kw = {
            'teal':    ['teal', 'xanh teal', 'xanh ngọc'],
            'navy':    ['navy', 'xanh nước biển', 'trang trọng'],
            'red':     ['đỏ', 'red', 'màu đỏ'],
            'minimal': ['trắng đen', 'đen trắng', 'minimal', 'tiết kiệm mực'],
            'purple':  ['tím', 'purple', 'màu tím'],
            'classic': ['classic', 'truyền thống', 'xanh dương', 'sgk'],
        }
        for t_key, kws in theme_kw.items():
            if any(kw in cmd for kw in kws):
                self.style.update(BUILTIN_THEMES[t_key])
                return f"✅ Đã chuyển sang theme **{BUILTIN_THEMES[t_key]['name']}**."
        m = re.search(r'(?:tên trường|school|trường).*?(?:là|:)\s*(.+)', cmd)
        if m:
            self.style['school_name'] = m.group(1).strip().title()
            return f"✅ Tên trường: **{self.style['school_name']}**."
        m = re.search(r'(?:liên hệ|sdt|phone|số điện thoại).*?(?:là|:)\s*([\d.\s-]+)', cmd)
        if m:
            self.style['contact_info'] = m.group(1).strip()
            return f"✅ Liên hệ: **{self.style['contact_info']}**."
        m = re.search(r'logo\s+([^\s]+\.(?:png|jpg|jpeg|pdf))', cmd)
        if m:
            self.style['logo_path'] = m.group(1).strip()
            return f"✅ Logo: **{self.style['logo_path']}**."
        m = re.search(r'(?:footer|chân trang).*?(?:là|:)\s*(.+)', cmd)
        if m:
            self.style['footer_right'] = m.group(1).strip()
            return f"✅ Footer: **{self.style['footer_right']}**."
        if any(kw in cmd for kw in ('watermark', 'bản nháp', 'draft')):
            self.style['watermark'] = True
            return "✅ Đã bật watermark **BẢN NHÁP**."
        return (f"⚠️ Không nhận diện lệnh '{command}'. "
                "Thử: 'dùng theme đỏ', 'đổi tên trường là ...', 'thêm logo logo.png'.")

    def save_profile(self, profile_name: str, save_dir=None) -> str:
        _dir = Path(save_dir) if save_dir else Path(__file__).parent.parent / 'exam_styles'
        _dir.mkdir(parents=True, exist_ok=True)
        safe = re.sub(r'[^\w]', '_', profile_name.lower())
        fpath = _dir / f'profile_{safe}.json'
        with open(fpath, 'w', encoding='utf-8') as f:
            json.dump(self.style, f, ensure_ascii=False, indent=2)
        return str(fpath)

    def export_student_pdf(self, exam_data, meta, output_path) -> dict:
        return self._export(exam_data, meta, output_path, show_solutions=False)

    def export_teacher_pdf(self, exam_data, meta, output_path) -> dict:
        return self._export(exam_data, meta, output_path, show_solutions=True)

    def export_both(self, exam_data, meta, output_dir='.', basename='de_thi') -> dict:
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        student = self._export(
            exam_data, meta,
            str(Path(output_dir) / f'{basename}_DE_HOC_SINH.pdf'),
            show_solutions=False)
        teacher = self._export(
            exam_data, meta,
            str(Path(output_dir) / f'{basename}_LOI_GIAI_GV.pdf'),
            show_solutions=True)
        return {'student': student, 'teacher': teacher}

    def _export(self, exam_data, meta, output_path, show_solutions) -> dict:
        result = {'success': False, 'pdf_path': '', 'compiler': self.compiler, 'error': ''}
        if not self.compiler:
            result['error'] = (
                '❌ Không tìm thấy LaTeX.\n'
                'Cài MikTeX: https://miktex.org/download\n'
                'hoặc: python scripts/check_and_setup_env.py')
            return result
        latex_doc = _build_document(meta, exam_data, show_solutions, self.style, self.compiler)
        with tempfile.TemporaryDirectory() as tmpdir:
            tex_file = Path(tmpdir) / 'exam.tex'
            tex_file.write_text(latex_doc, encoding='utf-8')
            self._copy_figures(exam_data, tmpdir)
            logo = self.style.get('logo_path', '')
            if logo and Path(logo).exists():
                shutil.copy2(logo, tmpdir)
            for pass_num in range(1, 3):
                proc = subprocess.run(
                    [self.compiler, '-interaction=nonstopmode', '-halt-on-error', str(tex_file)],
                    cwd=tmpdir, capture_output=True, text=True, timeout=120)
                if proc.returncode != 0:
                    errs = [l for l in proc.stdout.splitlines() if l.startswith('!')]
                    result['error'] = f'❌ Lỗi biên dịch LaTeX (lượt {pass_num}):\n' + '\n'.join(errs[:8])
                    return result
            pdf_tmp = Path(tmpdir) / 'exam.pdf'
            if pdf_tmp.exists():
                shutil.copy2(str(pdf_tmp), output_path)
                result.update({'success': True, 'pdf_path': output_path,
                                'size_kb': round(pdf_tmp.stat().st_size / 1024, 1)})
            else:
                result['error'] = '❌ Biên dịch xong nhưng không tạo được PDF.'
        return result

    @staticmethod
    def _copy_figures(exam_data, dest_dir):
        for q in (exam_data.get('part1_mc', []) + exam_data.get('part2_tf', []) +
                  exam_data.get('part3_sa', []) + exam_data.get('essay', [])):
            fp = q.get('figure_path', '')
            if fp and Path(fp).exists():
                shutil.copy2(fp, dest_dir)

    @staticmethod
    def list_themes() -> str:
        lines = ['\n🎨 CÁC THEME CÓ SẴN:\n',
                 f"  {'Key':<10} {'Mô tả':<45} {'Màu chính'}",
                 '  ' + '-' * 68]
        for key, t in BUILTIN_THEMES.items():
            lines.append(f"  {key:<10} {t['description']:<45} #{t['color_primary']}")
        lines.append('\n  Dùng: ExamPDFExporter(theme="teal")')
        lines.append('  Hoặc nói: "dùng theme đỏ" / "màu trắng đen" / ...')
        return '\n'.join(lines)


# ─────────────────────────────────────────────────────────────────────
# HÀM TIỆN ÍCH
# ─────────────────────────────────────────────────────────────────────

def export_exam_pdf(exam_data, meta, output_dir='.', basename='de_thi',
                    theme='teal', style_config=None, style_file=None) -> dict:
    """Hàm 1-click xuất cả 2 bản PDF cho Agent sử dụng."""
    return ExamPDFExporter(theme=theme, style_config=style_config,
                           style_file=style_file).export_both(
        exam_data, meta, output_dir, basename)


# ─────────────────────────────────────────────────────────────────────
# CLI TEST NHANH
# ─────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    print(ExamPDFExporter.list_themes())
    sample_exam = {
        'part1_mc': [
            {'id': 1, 'tag': 'TN2025',
             'question': r'Nghiệm của phương trình $\log_2(x-1) = 1$ là',
             'options': [r'$x = 5$', r'$x = 3$', r'$x = 2$', r'$x = 4$'],
             'answer': 'B',
             'solution': r'Ta có $\log_2(x-1)=1 \Leftrightarrow x-1=2 \Leftrightarrow x=3$.'},
        ],
        'part2_tf': [
            {'id': 1, 'stem': r'Cho hàm số $f(x) = x^3 - 3x + 1$. Xét các khẳng định:',
             'items': [
                 {'label': 'a', 'statement': 'Hàm số có hai điểm cực trị', 'answer': True},
                 {'label': 'b', 'statement': r'Hàm số đồng biến trên $\mathbb{R}$', 'answer': False},
                 {'label': 'c', 'statement': r"$f'(x) = 3x^2 - 3$", 'answer': True},
                 {'label': 'd', 'statement': 'Giá trị cực đại bằng $-1$', 'answer': False},
             ], 'solution': r"Ta có $f'(x)=3x^2-3=0 \Leftrightarrow x=\pm1$."},
        ],
        'part3_sa': [
            {'id': 1, 'question': r'Tính $\displaystyle\int_0^1 (2x+1)\,dx$.',
             'answer': 2, 'solution': r'Ta có $\int_0^1(2x+1)\,dx=(x^2+x)\Big|_0^1=2$.'},
        ],
    }
    sample_meta = {
        'series_name': 'TỔNG ÔN TẬP THPTQG\nMÔN TOÁN 2026', 'exam_code': '0103',
        'exam_title': 'ĐỀ THI TỐT NGHIỆP THPT', 'subject': 'Toán',
        'grade': 12, 'school_year': '2025 -- 2026', 'duration_minutes': 90,
    }
    style_override = {
        'school_name': 'TỔNG ÔN TẬP THPTQG', 'school_dept': 'MÔN TOÁN 2026',
        'contact_info': 'Nguyễn Hữu Phúc · 0985.692.879',
        'footer_left': 'TỔNG ÔN CHUYÊN ĐỀ    ÔN LUYỆN ĐỀ',
        'footer_right': 'KHI BỎ CUỘC, HÃY NGHĨ ĐẾN LÍ DO BẮT ĐẦU',
    }
    exporter = ExamPDFExporter(theme='teal', style_config=style_override)
    print("\nĐang biên dịch PDF (cần cài LaTeX)...")
    results = exporter.export_both(sample_exam, sample_meta, output_dir='.', basename='test_pdf')
    for mode, r in results.items():
        status = f"✅ {r['pdf_path']} ({r.get('size_kb', '?')} KB)" if r.get('success') \
            else f"❌ {r.get('error', 'Lỗi')}"
        print(f"  [{mode}] {status}")
