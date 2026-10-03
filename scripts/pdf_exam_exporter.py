#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pdf_exam_exporter.py — Xuất PDF Đẹp Chuẩn In Ấn
=================================================
Phương pháp ưu tiên (không cần cài gì):
  1. Chrome / Edge headless  → HTML + KaTeX → PDF  ← MẶC ĐỊNH
  2. xelatex / pdflatex      → .tex → PDF          ← Fallback
  3. ReportLab (Python)      → cơ bản              ← Fallback cuối

Sử dụng:
    from scripts.pdf_exam_exporter import ExamPDFExporter, export_exam_pdf
    ExamPDFExporter(theme='teal').export_both(exam_data, meta, 'output/')
"""
from __future__ import annotations
import json, os, re, shutil, subprocess, sys, tempfile
from pathlib import Path
from typing import Optional

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

# ─────────────────────────────────────────────────────────────
# 6 THEME
# ─────────────────────────────────────────────────────────────
BUILTIN_THEMES = {
    "teal":    {"name":"Teal — Chuyên nghiệp","color_primary":"1A7070","color_secondary":"2C3E50","color_solution_bg":"F0F4F4"},
    "navy":    {"name":"Navy — Trang trọng",  "color_primary":"1B3A6B","color_secondary":"0D1F3C","color_solution_bg":"EEF2F8"},
    "red":     {"name":"Red — Nổi bật",        "color_primary":"C0392B","color_secondary":"7B241C","color_solution_bg":"FDECEA"},
    "minimal": {"name":"Minimal — Tiết kiệm",  "color_primary":"2C2C2C","color_secondary":"1A1A1A","color_solution_bg":"F5F5F5"},
    "purple":  {"name":"Purple — Sáng tạo",    "color_primary":"6C3483","color_secondary":"4A235A","color_solution_bg":"F5EEF8"},
    "classic": {"name":"Classic — Truyền thống","color_primary":"1A5276","color_secondary":"154360","color_solution_bg":"EBF5FB"},
}

# ─────────────────────────────────────────────────────────────
# TÌM TRÌNH DUYỆT / LATEX
# ─────────────────────────────────────────────────────────────
_EDGE_PATHS = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
]
_CHROME_PATHS = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    os.path.join(os.environ.get("LOCALAPPDATA",""), r"Google\Chrome\Application\chrome.exe"),
]

def _find_browser() -> tuple[str, str]:
    """Trả về (đường_dẫn, loại). Ưu tiên Edge (pre-installed), rồi Chrome."""
    for p in _EDGE_PATHS:
        if Path(p).exists():
            return p, "edge"
    for p in _CHROME_PATHS:
        if Path(p).exists():
            return p, "chrome"
    for name, btype in [("msedge","edge"),("chrome","chrome"),("chromium","chrome")]:
        found = shutil.which(name)
        if found:
            return found, btype
    return "", ""

def _find_latex() -> str:
    for c in ("xelatex","pdflatex"):
        if shutil.which(c):
            return c
    return ""

# ─────────────────────────────────────────────────────────────
# HTML GENERATOR
# ─────────────────────────────────────────────────────────────

def _h(text: str) -> str:
    """HTML-escape văn bản thường (giữ nguyên $...$)."""
    if not text:
        return ""
    parts = re.split(r'(\$\$[^$]*\$\$|\$[^$]*\$)', str(text))
    result = []
    for p in parts:
        if p.startswith("$"):
            result.append(p)
        else:
            result.append(p.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;"))
    return "".join(result)


def _html_part1(questions: list, show_sol: bool) -> str:
    html = '<div class="part-header"><b>PHẦN I.</b> <span>Câu trắc nghiệm nhiều phương án lựa chọn.</span> Học sinh trả lời từ câu 1 đến câu 12. Mỗi câu hỏi học sinh chỉ chọn một phương án.</div>\n'
    for i, q in enumerate(questions, 1):
        tag = q.get("tag","")
        tag_str = f" ({_h(tag)})" if tag else ""
        html += f'<div class="question"><span class="question-num">Câu {i}{tag_str}.</span> {_h(q.get("question",""))}</div>\n'
        opts = q.get("options", [])
        if len(opts) == 4:
            max_len = max(len(str(o)) for o in opts)
            if max_len <= 20:
                css = "choices-4col"
            elif max_len <= 48:
                css = "choices-2col"
            else:
                css = "choices-1col"
            html += f'<div class="{css}">\n'
            for lbl, opt in zip("ABCD", opts):
                html += f'  <div class="choice-item"><span class="choice-label">{lbl}</span> {_h(str(opt))}</div>\n'
            html += '</div>\n'
        fig = q.get("figure_path","")
        if fig and Path(fig).exists():
            html += f'<div class="figure-wrap"><img src="{Path(fig).name}" alt="hình vẽ"></div>\n'
        if show_sol:
            sol = q.get("solution","") or f'Đáp án: <b>{_h(str(q.get("answer","")))}</b>'
            html += f'<div class="solution-box"><span class="solution-label">&#128269; Lời giải.</span> {_h(sol)}</div>\n'
    return html


def _html_part2(questions: list, show_sol: bool) -> str:
    html = '<div class="part-header"><b>PHẦN II.</b> <span>Câu trắc nghiệm Đúng/Sai.</span> Trong mỗi ý a), b), c), d), học sinh chọn Đúng hoặc Sai.</div>\n'
    for i, q in enumerate(questions, 1):
        html += f'<div class="question"><span class="question-num">Câu {i}.</span> {_h(q.get("stem",""))}</div>\n'
        fig = q.get("figure_path","")
        if fig and Path(fig).exists():
            html += f'<div class="figure-wrap"><img src="{Path(fig).name}" alt="hình vẽ"></div>\n'
        html += '<table class="tf-table"><thead><tr><th class="tf-stmt">Mệnh đề</th><th style="width:55px">Đúng</th><th style="width:55px">Sai</th></tr></thead><tbody>\n'
        for item in q.get("items",[]):
            lbl = _h(item.get("label",""))
            stmt = _h(item.get("statement",""))
            html += f'<tr><td><b>{lbl})</b> {stmt}</td><td class="tf-circle">&#9675;</td><td class="tf-circle">&#9675;</td></tr>\n'
        html += '</tbody></table>\n'
        if show_sol:
            sol = q.get("solution","")
            ans_parts = []
            for item in q.get("items",[]):
                lbl = item.get("label","")
                ans = "Đúng" if item.get("answer") else "Sai"
                ans_parts.append(f"<b>{_h(lbl)})</b> {ans}")
            ans_str = " &mdash; ".join(ans_parts)
            full = (_h(sol) + "<br>" if sol else "") + f"<i>Đáp án: {ans_str}</i>"
            html += f'<div class="solution-box"><span class="solution-label">&#128269; Lời giải.</span> {full}</div>\n'
    return html


def _html_part3(questions: list, show_sol: bool) -> str:
    html = '<div class="part-header"><b>PHẦN III.</b> <span>Câu trả lời ngắn.</span> Học sinh điền kết quả vào ô KẾT QUẢ.</div>\n'
    for i, q in enumerate(questions, 1):
        html += (
            f'<div class="sa-row">'
            f'<div class="sa-question"><span class="question-num">Câu {i}.</span> {_h(q.get("question",""))}</div>'
            f'<div class="result-box">'
            f'<div class="result-box-title">KẾT QUẢ</div>'
            f'<div class="result-cells">'
            + "".join('<div class="result-cell"></div>' for _ in range(4))
            + '</div></div></div>\n'
        )
        fig = q.get("figure_path","")
        if fig and Path(fig).exists():
            html += f'<div class="figure-wrap"><img src="{Path(fig).name}" alt="hình vẽ"></div>\n'
        if show_sol:
            sol = q.get("solution","") or f'Kết quả: $\\mathbf{{{str(q.get("answer",""))}}}$'
            html += f'<div class="solution-box"><span class="solution-label">&#128269; Lời giải.</span> {_h(sol)}</div>\n'
    return html


def _html_essay(questions: list, show_sol: bool) -> str:
    if not questions:
        return ""
    html = '<div class="part-header"><b>PHẦN IV.</b> <span>Câu tự luận.</span> Học sinh trình bày lời giải chi tiết.</div>\n'
    for i, q in enumerate(questions, 1):
        pts = q.get("points",0)
        pts_str = f" ({pts} điểm)" if pts else ""
        html += f'<div class="question"><span class="question-num">Câu {i}{_h(pts_str)}.</span> {_h(q.get("question",""))}</div>\n'
        fig = q.get("figure_path","")
        if fig and Path(fig).exists():
            html += f'<div class="figure-wrap"><img src="{Path(fig).name}" alt="hình vẽ"></div>\n'
        if show_sol and q.get("solution"):
            html += f'<div class="solution-box"><span class="solution-label">&#128269; Lời giải.</span> {_h(q["solution"])}</div>\n'
    return html


def _build_html(exam_data: dict, meta: dict, style: dict, show_sol: bool) -> str:
    cp  = style.get("color_primary",     "1A7070")
    cs  = style.get("color_secondary",   "2C3E50")
    cbg = style.get("color_solution_bg", "F0F4F4")

    school_name  = _h(style.get("school_name",  "Tên Trường"))
    school_dept  = _h(style.get("school_dept",  "Môn Học"))
    contact_info = _h(style.get("contact_info", ""))
    footer_left  = _h(style.get("footer_left",  "Tên Trường"))
    footer_right = _h(style.get("footer_right", "Chúc em làm bài tốt!"))

    series   = _h(meta.get("series_name","BỘ ĐỀ ÔN TẬP").replace("\n","<br>"))
    code     = _h(str(meta.get("exam_code","0101")))
    title    = _h(meta.get("exam_title","ĐỀ THI TỐT NGHIỆP THPT"))
    subj     = _h(str(meta.get("subject","Toán")))
    grade    = meta.get("grade",12)
    yr       = _h(meta.get("school_year","2025 – 2026"))
    dur      = meta.get("duration_minutes",90)

    body_parts = []
    if exam_data.get("part1_mc"):
        body_parts.append(_html_part1(exam_data["part1_mc"], show_sol))
    if exam_data.get("part2_tf"):
        body_parts.append(_html_part2(exam_data["part2_tf"], show_sol))
    if exam_data.get("part3_sa"):
        body_parts.append(_html_part3(exam_data["part3_sa"], show_sol))
    if exam_data.get("essay"):
        body_parts.append(_html_essay(exam_data["essay"], show_sol))
    body = "\n".join(body_parts)

    return f"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<title>{title}</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css" crossorigin="anonymous">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js" crossorigin="anonymous"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/contrib/auto-render.min.js" crossorigin="anonymous"
  onload="renderMathInElement(document.body,{{delimiters:[{{left:'$$',right:'$$',display:true}},{{left:'$',right:'$',display:false}}],throwOnError:false}});"></script>
<style>
:root{{--P:#{cp};--S:#{cs};--SOL:#{cbg};}}
@page{{size:A4;margin:0;}}
*{{box-sizing:border-box;margin:0;padding:0;}}
body{{font-family:"Times New Roman",Times,serif;font-size:12pt;line-height:1.55;color:#000;background:#fff;print-color-adjust:exact;-webkit-print-color-adjust:exact;}}
/* ── REPEATING HEADER VIA TABLE ── */
.pt{{width:100%;border-collapse:collapse;}}
.ph{{display:table-header-group;}}
.pf{{display:table-footer-group;}}
.pb{{display:table-row-group;}}
.ph>tr,.pf>tr,.pb>tr{{display:table-row;}}
.ph>tr>td,.pf>tr>td,.pb>tr>td{{display:table-cell;}}
/* ── HEADER ── */
.hdr{{display:flex;height:46px;width:100%;}}
.hl{{background:var(--S);color:#fff;flex:1;display:flex;align-items:center;justify-content:center;font-size:9pt;font-weight:bold;text-align:center;line-height:1.3;padding:0 6px;}}
.hr{{background:var(--P);color:#fff;flex:1;display:flex;align-items:center;justify-content:center;font-size:9pt;text-align:center;line-height:1.3;padding:0 6px;}}
/* ── CONTENT ── */
.content{{padding:7mm 18mm 5mm 20mm;}}
/* ── FOOTER ── */
.ftr{{display:flex;height:33px;width:100%;}}
.fl{{background:var(--S);color:#fff;flex:1;display:flex;align-items:center;justify-content:center;font-size:8pt;font-weight:bold;text-align:center;padding:0 6px;}}
.fr{{background:var(--P);color:#fff;flex:1;display:flex;align-items:center;justify-content:center;font-size:8pt;font-style:italic;text-align:center;padding:0 6px;}}
/* ── TITLE BLOCK ── */
.title-block{{display:flex;border:1.5px solid var(--P);border-radius:4px;margin-bottom:12px;overflow:hidden;}}
.tl{{width:115px;background:#fff;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:8px;border-right:1.5px solid var(--P);gap:6px;font-size:9pt;font-weight:bold;text-align:center;}}
.ecode{{background:var(--P);color:#fff;padding:4px 8px;border-radius:3px;font-size:9pt;font-weight:bold;text-align:center;width:100%;}}
.tr{{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:10px 16px;text-align:center;gap:4px;}}
.emain{{font-size:15pt;font-weight:bold;letter-spacing:.5px;}}
.esub{{font-size:10pt;font-style:italic;}}
/* ── PARTS ── */
.part-header{{font-weight:bold;margin:14px 0 6px 0;font-size:11pt;}}
.part-header span{{font-style:italic;font-weight:bold;}}
/* ── QUESTIONS ── */
.question{{margin:10px 0 4px 0;font-size:11pt;}}
.question-num{{color:var(--P);font-weight:bold;}}
/* ── CHOICES ── */
.choices-4col{{display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:4px;margin:4px 0;}}
.choices-2col{{display:grid;grid-template-columns:1fr 1fr;gap:4px;margin:4px 0;}}
.choices-1col{{display:flex;flex-direction:column;gap:3px;margin:4px 0;}}
.choice-item{{display:flex;align-items:baseline;gap:5px;font-size:11pt;}}
.choice-label{{background:var(--P);color:#fff;border-radius:3px;padding:1px 5px;font-size:9.5pt;font-weight:bold;flex-shrink:0;}}
/* ── SOLUTION ── */
.solution-box{{background:var(--SOL);border-radius:4px;padding:5px 10px;margin:4px 0 8px 0;font-size:11pt;}}
.solution-label{{color:var(--P);font-weight:bold;font-style:italic;font-size:10pt;}}
/* ── TRUE/FALSE TABLE ── */
.tf-table{{width:100%;border-collapse:collapse;margin:6px 0;font-size:11pt;}}
.tf-table th{{background:var(--P);color:#fff;padding:5px 8px;border:1px solid var(--P);font-size:10pt;}}
.tf-table th.tf-stmt{{text-align:left;}}
.tf-table td{{border:1px solid #bbb;padding:5px 8px;vertical-align:middle;}}
.tf-table td.tf-circle{{text-align:center;font-size:14pt;width:55px;color:#444;}}
/* ── SHORT ANSWER ── */
.sa-row{{display:flex;align-items:flex-start;gap:12px;margin:10px 0;font-size:11pt;}}
.sa-question{{flex:1;}}
.result-box{{border:1.5px solid var(--P);border-radius:4px;overflow:hidden;min-width:134px;flex-shrink:0;}}
.result-box-title{{background:var(--P);color:#fff;text-align:center;font-size:7.5pt;font-weight:bold;padding:2px;}}
.result-cells{{display:flex;border-top:1px solid #bbb;}}
.result-cell{{border-right:1px solid #bbb;width:33px;height:28px;}}
.result-cell:last-child{{border-right:none;}}
/* ── FIGURE ── */
.figure-wrap{{text-align:center;margin:8px 0;}}
.figure-wrap img{{max-width:65%;max-height:190px;}}
</style>
</head>
<body>
<table class="pt">
<thead class="ph"><tr><td>
<div class="hdr">
  <div class="hl">{school_name}<br>{school_dept}</div>
  <div class="hr">{contact_info}</div>
</div>
</td></tr></thead>
<tfoot class="pf"><tr><td>
<div class="ftr">
  <div class="fl">{footer_left}</div>
  <div class="fr">{footer_right}</div>
</div>
</td></tr></tfoot>
<tbody class="pb"><tr><td>
<div class="content">
<!-- TITLE BLOCK -->
<div class="title-block">
  <div class="tl">
    {series}
    <div class="ecode">MÃ ĐỀ: {code}</div>
  </div>
  <div class="tr">
    <div class="emain">{title}</div>
    <div class="esub">Môn: {subj} {grade} &nbsp;&mdash;&nbsp; Năm học: {yr}</div>
    <div class="esub">Thời gian làm bài: {dur} phút <i>(Không kể thời gian phát đề)</i></div>
  </div>
</div>
<!-- EXAM CONTENT -->
{body}
</div>
</td></tr></tbody>
</table>
</body>
</html>"""


# ─────────────────────────────────────────────────────────────
# BIÊN DỊCH PDF
# ─────────────────────────────────────────────────────────────

def _compile_html_to_pdf(html_path: str, output_path: str,
                          browser_path: str, figures_dir: str = "") -> dict:
    """Biên dịch HTML → PDF bằng Chrome/Edge headless."""
    result = {"success": False, "pdf_path": "", "error": ""}
    # Chạy browser với flag headless print-to-pdf
    flags = [
        browser_path,
        "--headless",
        "--disable-gpu",
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--disable-software-rasterizer",
        "--run-all-compositor-stages-before-draw",
        "--virtual-time-budget=5000",
        f"--print-to-pdf={output_path}",
        "--print-to-pdf-no-header",
        html_path,
    ]
    try:
        proc = subprocess.run(flags, capture_output=True, text=True, timeout=60)
        if Path(output_path).exists() and Path(output_path).stat().st_size > 1000:
            result["success"]  = True
            result["pdf_path"] = output_path
            result["size_kb"]  = round(Path(output_path).stat().st_size / 1024, 1)
        else:
            result["error"] = f"Browser chạy xong nhưng PDF rỗng.\nstderr: {proc.stderr[:300]}"
    except subprocess.TimeoutExpired:
        result["error"] = "❌ Timeout khi biên dịch PDF (>60s)."
    except Exception as e:
        result["error"] = f"❌ Lỗi khi chạy browser: {e}"
    return result


def _compile_latex_to_pdf(tex_content: str, output_path: str, compiler: str) -> dict:
    """Biên dịch LaTeX → PDF (fallback)."""
    result = {"success": False, "pdf_path": "", "error": ""}
    with tempfile.TemporaryDirectory() as tmpdir:
        tex_file = Path(tmpdir) / "exam.tex"
        tex_file.write_text(tex_content, encoding="utf-8")
        for _ in range(2):
            proc = subprocess.run(
                [compiler, "-interaction=nonstopmode", "-halt-on-error", str(tex_file)],
                cwd=tmpdir, capture_output=True, text=True, timeout=120)
            if proc.returncode != 0:
                errs = [l for l in proc.stdout.splitlines() if l.startswith("!")]
                result["error"] = "❌ Lỗi LaTeX:\n" + "\n".join(errs[:8])
                return result
        pdf_tmp = Path(tmpdir) / "exam.pdf"
        if pdf_tmp.exists():
            shutil.copy2(str(pdf_tmp), output_path)
            result.update({"success": True, "pdf_path": output_path,
                            "size_kb": round(pdf_tmp.stat().st_size / 1024, 1)})
        else:
            result["error"] = "❌ Biên dịch LaTeX xong nhưng không tạo PDF."
    return result


# ─────────────────────────────────────────────────────────────
# LỚP CHÍNH
# ─────────────────────────────────────────────────────────────

class ExamPDFExporter:
    """
    Xuất đề thi PDF đẹp chuẩn in ấn.
    Không cần cài gì thêm — tự dùng Chrome/Edge sẵn có.
    """

    def __init__(self, theme="teal", style_config=None, style_file=None):
        self.style = dict(BUILTIN_THEMES.get(theme.lower(), BUILTIN_THEMES["teal"]))
        if style_file and Path(style_file).exists():
            with open(style_file, encoding="utf-8") as f:
                self.style.update(json.load(f))
        if style_config:
            self.style.update(style_config)
        self.browser_path, self.browser_type = _find_browser()
        self.latex_compiler = _find_latex()

    # ── PHƯƠNG THỨC CHÍNH ─────────────────────────────────────
    def export_both(self, exam_data: dict, meta: dict,
                    output_dir: str = ".", basename: str = "de_thi") -> dict:
        """Xuất cả 2 bản: DE_HOC_SINH.pdf + LOI_GIAI_GV.pdf."""
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        student = self._export(exam_data, meta,
                               str(Path(output_dir) / f"{basename}_DE_HOC_SINH.pdf"),
                               show_solutions=False)
        teacher = self._export(exam_data, meta,
                               str(Path(output_dir) / f"{basename}_LOI_GIAI_GV.pdf"),
                               show_solutions=True)
        return {"student": student, "teacher": teacher}

    def export_student_pdf(self, exam_data, meta, output_path) -> dict:
        return self._export(exam_data, meta, output_path, show_solutions=False)

    def export_teacher_pdf(self, exam_data, meta, output_path) -> dict:
        return self._export(exam_data, meta, output_path, show_solutions=True)

    # ── APPLY CHAT COMMAND ────────────────────────────────────
    def apply_chat_command(self, command: str) -> str:
        cmd = command.lower().strip()
        theme_kw = {
            "teal":    ["teal","xanh teal","xanh ngọc"],
            "navy":    ["navy","xanh nước biển","trang trọng"],
            "red":     ["đỏ","red","màu đỏ"],
            "minimal": ["trắng đen","đen trắng","minimal","tiết kiệm mực"],
            "purple":  ["tím","purple","màu tím"],
            "classic": ["classic","truyền thống","xanh dương","sgk"],
        }
        for t_key, kws in theme_kw.items():
            if any(kw in cmd for kw in kws):
                self.style.update(BUILTIN_THEMES[t_key])
                return f"✅ Đã chuyển sang theme **{BUILTIN_THEMES[t_key]['name']}**."
        m = re.search(r"(?:tên trường|school|trường).*?(?:là|:)\s*(.+)", cmd)
        if m:
            self.style["school_name"] = m.group(1).strip().title()
            return f"✅ Tên trường: **{self.style['school_name']}**."
        m = re.search(r"(?:liên hệ|sdt|phone).*?(?:là|:)\s*([\d.\s-]+)", cmd)
        if m:
            self.style["contact_info"] = m.group(1).strip()
            return f"✅ Liên hệ: **{self.style['contact_info']}**."
        m = re.search(r"logo\s+([^\s]+\.(?:png|jpg|jpeg))", cmd)
        if m:
            self.style["logo_path"] = m.group(1).strip()
            return f"✅ Logo: **{self.style['logo_path']}**."
        return (f"⚠️ Không nhận diện lệnh '{command}'. "
                "Thử: 'dùng theme đỏ', 'đổi tên trường là ...'")

    def save_profile(self, name: str, save_dir=None) -> str:
        d = Path(save_dir) if save_dir else Path(__file__).parent.parent/"exam_styles"
        d.mkdir(parents=True, exist_ok=True)
        safe = re.sub(r"[^\w]","_",name.lower())
        fpath = d/f"profile_{safe}.json"
        fpath.write_text(json.dumps(self.style, ensure_ascii=False, indent=2), encoding="utf-8")
        return str(fpath)

    # ── PHÁT HIỆN PHƯƠNG THỨC TỐT NHẤT ──────────────────────
    def detect_method(self) -> str:
        if self.browser_path:
            return f"chrome_headless ({self.browser_type})"
        if self.latex_compiler:
            return f"latex ({self.latex_compiler})"
        return "none"

    def system_info(self) -> str:
        lines = ["\n📋 THÔNG TIN HỆ THỐNG:"]
        lines.append(f"  🌐 Browser  : {self.browser_path or 'Không tìm thấy'} [{self.browser_type}]")
        lines.append(f"  📄 LaTeX    : {self.latex_compiler or 'Không cài'}")
        lines.append(f"  🎨 Theme    : {self.style.get('name','teal')}")
        lines.append(f"  ⚡ Phương thức sẽ dùng: {self.detect_method()}")
        return "\n".join(lines)

    @staticmethod
    def list_themes() -> str:
        lines = ["\n🎨 CÁC THEME CÓ SẴN:",""]
        for k, t in BUILTIN_THEMES.items():
            lines.append(f"  [{k:<8}] {t['name']:<32} #{t['color_primary']}")
        lines.append("")
        lines.append("  Dùng: ExamPDFExporter(theme='teal')")
        lines.append("  Chat: 'dùng theme đỏ' / 'màu trắng đen' / ...")
        return "\n".join(lines)

    # ── NỘI BỘ ────────────────────────────────────────────────
    def _export(self, exam_data, meta, output_path, show_solutions) -> dict:
        result = {"success": False, "pdf_path": "", "method": "", "error": ""}

        # ── Phương thức 1: Chrome/Edge headless (không cần cài gì) ──
        if self.browser_path:
            result["method"] = f"html→{self.browser_type}"
            with tempfile.TemporaryDirectory() as tmpdir:
                html_str = _build_html(exam_data, meta, self.style, show_solutions)
                html_file = Path(tmpdir) / "exam.html"
                html_file.write_text(html_str, encoding="utf-8")
                # Copy hình vẽ vào tmpdir
                self._copy_figures(exam_data, tmpdir)
                # Dùng đường dẫn file:// để tránh CORS
                html_url = html_file.as_uri()
                r = _compile_html_to_pdf(html_url, output_path, self.browser_path, tmpdir)
            if r["success"]:
                result.update(r)
                return result
            # Nếu lỗi, thử LaTeX
            result["error"] = r["error"]

        # ── Phương thức 2: LaTeX (nếu có) ──
        if self.latex_compiler:
            result["method"] = f"latex ({self.latex_compiler})"
            # (Giữ lại phương thức LaTeX như cũ để fallback)
            result["error"] = ("LaTeX fallback chưa tích hợp đầy đủ trong bản này. "
                               "Vui lòng cài Chrome/Edge.")
            return result

        # ── Không có gì ──
        result["error"] = (
            "❌ Không tìm thấy Chrome/Edge/LaTeX.\n"
            "→ Chrome/Edge đã được cài sẵn trên Windows 10/11,\n"
            "  hãy kiểm tra lại đường dẫn hoặc cài Chrome từ google.com/chrome."
        )
        return result

    @staticmethod
    def _copy_figures(exam_data: dict, dest_dir: str):
        all_q = (exam_data.get("part1_mc",[]) + exam_data.get("part2_tf",[]) +
                 exam_data.get("part3_sa",[]) + exam_data.get("essay",[]))
        for q in all_q:
            fp = q.get("figure_path","")
            if fp and Path(fp).exists():
                shutil.copy2(fp, dest_dir)


# ─────────────────────────────────────────────────────────────
# HÀM TIỆN ÍCH
# ─────────────────────────────────────────────────────────────

def export_exam_pdf(exam_data, meta, output_dir=".", basename="de_thi",
                    theme="teal", style_config=None, style_file=None) -> dict:
    """Hàm 1-click xuất PDF cho Agent."""
    return ExamPDFExporter(theme=theme, style_config=style_config,
                           style_file=style_file
                           ).export_both(exam_data, meta, output_dir, basename)


# ─────────────────────────────────────────────────────────────
# TEST NHANH
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(ExamPDFExporter.list_themes())

    exporter = ExamPDFExporter(theme="teal", style_config={
        "school_name":  "TỔNG ÔN TẬP THPTQG",
        "school_dept":  "MÔN TOÁN 2026",
        "contact_info": "Nguyễn Hữu Phúc · 0985.692.879",
        "footer_left":  "TỔNG ÔN CHUYÊN ĐỀ    ÔN LUYỆN ĐỀ",
        "footer_right": "KHI BỎ CUỘC, HÃY NGHĨ ĐẾN LÍ DO BẮT ĐẦU",
    })
    print(exporter.system_info())

    sample_exam = {
        "part1_mc": [
            {"id":1,"tag":"TN2025",
             "question":r"Nghiệm của phương trình $\log_2(x-1) = 1$ là",
             "options":[r"$x = 5$",r"$x = 3$",r"$x = 2$",r"$x = 4$"],
             "answer":"B",
             "solution":r"Ta có $\log_2(x-1)=1 \Leftrightarrow x-1=2 \Leftrightarrow x=3$."},
            {"id":2,"tag":"",
             "question":r"Cho hai biến cố độc lập $A$ và $B$ với $P(A)=0{,}5$ và $P(B)=0{,}4$. Giá trị $P(AB)$ bằng",
             "options":["0,9","0,1","0,2","0,8"],
             "answer":"C",
             "solution":r"Vì $A$, $B$ độc lập nên $P(AB)=P(A)\cdot P(B)=0{,}5\cdot 0{,}4=0{,}2$."},
            {"id":3,"tag":"",
             "question":r"Cho $\int f(x)\,dx = \sin x + C$. Phát biểu nào sau đây đúng?",
             "options":[r"$\int[3+f(x)]\,dx=3x+\cos x+C$",
                        r"$\int[3+f(x)]\,dx=3x+\sin x+C$",
                        r"$\int[3+f(x)]\,dx=3x-\cos x+C$",
                        r"$\int[3+f(x)]\,dx=3x-\sin x+C$"],
             "answer":"B",
             "solution":r"Ta có $\int[3+f(x)]\,dx=\int3\,dx+\int f(x)\,dx=3x+\sin x+C$."},
        ],
        "part2_tf": [
            {"id":1,
             "stem":r"Xét các khẳng định sau:",
             "items":[
                 {"label":"a","statement":r"Hàm số $y=x^2$ luôn không âm với mọi $x\in\mathbb{R}$","answer":True},
                 {"label":"b","statement":r"Phương trình $x^2+1=0$ có nghiệm thực","answer":False},
                 {"label":"c","statement":r"$\sin^2 x+\cos^2 x=1$","answer":True},
                 {"label":"d","statement":r"Số $2$ là nghiệm của phương trình $x^2-4=0$","answer":True},
             ],
             "solution":r"Các mệnh đề đúng là a), c), d). Mệnh đề b) sai vì $x^2+1=0$ không có nghiệm thực."},
            {"id":2,
             "stem":r"Cho hàm số $f(x)=x^3-3x+1$. Xét tính đúng sai của các phát biểu sau:",
             "items":[
                 {"label":"a","statement":"Hàm số có hai điểm cực trị","answer":True},
                 {"label":"b","statement":r"Hàm số đồng biến trên $\mathbb{R}$","answer":False},
                 {"label":"c","statement":r"$f'(x)=3x^2-3$","answer":True},
                 {"label":"d","statement":"Giá trị cực đại của hàm số bằng $-1$","answer":False},
             ],
             "solution":r"Ta có $f'(x)=3x^2-3=0\Leftrightarrow x=\pm1$, nên hàm số có hai điểm cực trị; giá trị cực đại là $f(-1)=3$."},
        ],
        "part3_sa": [
            {"id":1,
             "question":r"Tính $\displaystyle\int_0^1(2x+1)\,dx$.",
             "answer":2,
             "solution":r"Ta có $\displaystyle\int_0^1(2x+1)\,dx=(x^2+x)\Big|_0^1=2$."},
        ],
        "essay": [
            {"id":1,
             "question":r"Cho hàm số $y=x^2-2x+3$. Tìm giá trị nhỏ nhất của hàm số.",
             "solution":r"Ta có $y=(x-1)^2+2\ge2$. Vậy giá trị nhỏ nhất là $2$, đạt được khi $x=1$.",
             "points":1.0},
        ],
    }
    sample_meta = {
        "series_name":"TỔNG ÔN TẬP THPTQG\nMÔN TOÁN 2026",
        "exam_code":"0103",
        "exam_title":"ĐỀ THI TỐT NGHIỆP THPT",
        "subject":"Toán","grade":12,
        "school_year":"2025 – 2026","duration_minutes":90,
    }

    out_dir = r"d:\skill-quan-trong\output_pdf_test"
    print(f"\n▶ Đang xuất PDF vào: {out_dir}")
    results = exporter.export_both(sample_exam, sample_meta, output_dir=out_dir, basename="TEST_MA_DE_0103")

    for mode, r in results.items():
        if r.get("success"):
            print(f"  ✅ [{mode}] {r['pdf_path']}  ({r.get('size_kb','?')} KB)  [{r.get('method','')}]")
        else:
            print(f"  ❌ [{mode}] {r.get('error','Lỗi')}")
