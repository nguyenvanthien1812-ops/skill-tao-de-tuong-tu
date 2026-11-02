import os
import re
import copy
from lxml import etree
import latex2mathml.converter
from docx import Document
from docx.text.run import Run
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

def _require_local_engine_license():
    """Kiem tra ban quyen bat buoc truoc khi thuc thi Local Engine MathType."""
    try:
        import os as _os, sys as _sys
        _cur_dir = _os.path.dirname(_os.path.abspath(__file__))
        _scripts_dir = _os.path.dirname(_cur_dir)
        if _scripts_dir not in _sys.path:
            _sys.path.insert(0, _scripts_dir)
        import license_manager
        ok, payload, err = license_manager.check_current_license()
        if not ok:
            raise PermissionError(f"Local Engine MathType chua kich hoat ban quyen hop le: {err}")
        return payload
    except ImportError:
        raise PermissionError("LOI BAN QUYEN: Khong tim thay module xac minh license_manager.py. Khong duoc tach le Local Engine.")

_require_local_engine_license()


# Load XSLT stylesheet for MathML to OMML conversion
# We try to load from the resources folder, which is packaged with the app
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
XSLT_PATH = os.path.join(CURRENT_DIR, "resources", "MML2OMML.XSL")

# Cache the compiled XSLT transform
_transform = None

def get_xslt_transform():
    global _transform
    if _transform is None:
        if not os.path.exists(XSLT_PATH):
            raise FileNotFoundError(f"Không tìm thấy tệp MML2OMML.XSL tại {XSLT_PATH}. Vui lòng chạy locate_resources.py.")
        xslt_doc = etree.parse(XSLT_PATH)
        _transform = etree.XSLT(xslt_doc)
    return _transform

def latex_to_omml(latex_str):
    """
    Converts a LaTeX string to an OMML XML element.
    """
    # 1. LaTeX to MathML
    mathml_str = latex2mathml.converter.convert(latex_str)
    
    # 2. Parse MathML
    mathml_xml = etree.fromstring(mathml_str)
    
    ns = {"m": "http://www.w3.org/1998/Math/MathML"}
    
    # Pre-process 1: add accent="true" to all <mover> elements to map accents correctly in OMML
    for mover in mathml_xml.xpath("//m:mover", namespaces=ns):
        mover.set("accent", "true")
        
    # Pre-process 2: convert ring operator (\u2218) to standard degree symbol (\u00B0)
    for mo in mathml_xml.xpath("//m:mo", namespaces=ns):
        if mo.text == "\u2218":
            mo.text = "\u00B0"
            
    # Pre-process 3: detect subscripts/superscripts enclosed in parentheses (like Q_{(O, 72^\circ)})
    # and wrap them in <mfenced> to produce exactly one <m:d> delimiter in OMML,
    # preventing double parentheses and semicolon/regional settings bugs.
    targets = mathml_xml.xpath("//m:msub/m:*[2] | //m:msup/m:*[2] | //m:msubsup/m:*[2] | //m:msubsup/m:*[3]", namespaces=ns)
    for sub in targets:
        container = sub
        children = list(container)
        if len(children) >= 2:
            first = children[0]
            last = children[-1]
            first_text = "".join(first.itertext()).strip()
            last_text = "".join(last.itertext()).strip()
            is_first_paren = first.tag.endswith("mo") and (first_text == "(" or first_text == "\u0028")
            is_last_paren = last.tag.endswith("mo") and (last_text == ")" or last_text == "\u0029")
            if is_first_paren and is_last_paren:
                mfenced = etree.Element("{http://www.w3.org/1998/Math/MathML}mfenced", attrib={"open": "(", "close": ")"})
                mrow = etree.SubElement(mfenced, "{http://www.w3.org/1998/Math/MathML}mrow")
                for child in children[1:-1]:
                    container.remove(child)
                    mrow.append(child)
                container.remove(first)
                container.remove(last)
                container.append(mfenced)
                
                # Convert mo inside mfenced's mrow to mtext to prevent separator splitting
                for mo in mrow.xpath(".//m:mo", namespaces=ns):
                    mo.tag = "{http://www.w3.org/1998/Math/MathML}mtext"
                    for attr in ["fence", "stretchy", "form", "separator"]:
                        if attr in mo.attrib:
                            del mo.attrib[attr]
                            
    # For any remaining mo inside subscripts/superscripts that were not parenthesized (like standard separators),
    # convert them to mtext to prevent XSLT from wrapping them in complex delimiter <m:d> objects
    for sub in mathml_xml.xpath("//m:msub/m:*[2] | //m:msup/m:*[2] | //m:msubsup/m:*[2] | //m:msubsup/m:*[3]", namespaces=ns):
        for mo in sub.xpath(".//m:mo", namespaces=ns):
            mo.tag = "{http://www.w3.org/1998/Math/MathML}mtext"
            for attr in ["fence", "stretchy", "form", "separator"]:
                if attr in mo.attrib:
                    del mo.attrib[attr]
        
    # 3. Transform MathML to OMML
    transform = get_xslt_transform()
    omml_xml = transform(mathml_xml)
    
    # Return the root element of the transformed XML
    return omml_xml.getroot()

def parse_math_match(raw_match):
    """
    Parses a regex match of LaTeX to return its clean math content and type (inline vs display).
    """
    # Standard display delimiters
    if raw_match.startswith('$$') and raw_match.endswith('$$'):
        return raw_match[2:-2], True
    elif raw_match.startswith(r'\[') and raw_match.endswith(r'\]'):
        return raw_match[2:-2], True
    elif raw_match.startswith('[latex]') and raw_match.endswith('[/latex]'):
        return raw_match[7:-8], False
    # Standard inline delimiters
    elif raw_match.startswith('$') and raw_match.endswith('$'):
        return raw_match[1:-1], False
    elif raw_match.startswith(r'\(') and raw_match.endswith(r'\)'):
        return raw_match[2:-2], False
    
    # Custom fallback
    return raw_match, False

def split_match_runs(paragraph, start_run, start_offset, end_run, end_offset):
    """
    Splits start_run and end_run at boundary offsets to isolate the LaTeX text.
    Returns (latex_start_elem, latex_end_elem) representing the XML nodes to replace.
    """
    text_a = start_run.text
    text_b = end_run.text
    
    # 1. Split end_run at end_offset + 1 (isolate text after the match)
    if end_offset + 1 < len(text_b):
        next_r_elem = copy.deepcopy(end_run._r)
        end_run.text = text_b[:end_offset + 1]
        
        # Clear text inside deepcopy and insert new text
        for t in next_r_elem.xpath('w:t'):
            t.getparent().remove(t)
        t_elem = etree.SubElement(next_r_elem, '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t')
        text_next = text_b[end_offset + 1:]
        if text_next.startswith(' ') or text_next.endswith(' '):
            t_elem.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
        t_elem.text = text_next
        
        end_run._r.addnext(next_r_elem)
        
    # 2. Split start_run at start_offset (isolate text before the match)
    # Note: if start_run and end_run were the same, start_run's text has changed to text_b[:end_offset + 1]!
    text_a_current = start_run.text
    if start_offset > 0:
        next_r_elem = copy.deepcopy(start_run._r)
        start_run.text = text_a_current[:start_offset]
        
        for t in next_r_elem.xpath('w:t'):
            t.getparent().remove(t)
        t_elem = etree.SubElement(next_r_elem, '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t')
        text_next = text_a_current[start_offset:]
        if text_next.startswith(' ') or text_next.endswith(' '):
            t_elem.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
        t_elem.text = text_next
        
        start_run._r.addnext(next_r_elem)
        latex_start_elem = next_r_elem
    else:
        latex_start_elem = start_run._r
        
    # Determine the end XML element of the isolated LaTeX run sequence
    if start_run == end_run:
        latex_end_elem = latex_start_elem
    else:
        latex_end_elem = end_run._r
        
    return latex_start_elem, latex_end_elem

def process_paragraph(paragraph, regex, stats, log_callback=None, skip_cases=False):
    """
    Scans a paragraph for LaTeX formulas and replaces them with OMML XML elements.
    """
    runs = paragraph.runs
    if not runs:
        return
        
    # Build a full string of the runs text to match against regex
    run_text_full = "".join(run.text for run in runs)
    
    matches = list(regex.finditer(run_text_full))
    if not matches:
        return
        
    # Map each character in run_text_full to (run_object, char_offset_within_run)
    char_map = []
    for run in runs:
        run_text = run.text
        for char_offset in range(len(run_text)):
            char_map.append((run, char_offset))
            
    # Process matches in reverse (right-to-left) to avoid offset shifting issues
    for match in reversed(matches):
        start, end = match.span()
        raw_match = match.group(0)
        
        math_content, is_display = parse_math_match(raw_match)
        if not math_content.strip():
            continue
            
        # Check if we should skip cases or subscripts containing parentheses (for direct MathType translation)
        if skip_cases:
            if any(term in math_content for term in ["cases", "array", "matrix", "align"]):
                continue
            if re.search(r'_[{][^{}]*[\(\)][^{}]*[}]', math_content) or re.search(r'\^[{][^{}]*[\(\)][^{}]*[}]', math_content):
                continue
            
        try:
            # 1. Convert to OMML
            omml_elem = latex_to_omml(math_content)
            
            # 2. Identify start and end runs
            start_run, start_offset = char_map[start]
            end_run, end_offset = char_map[end - 1]
            
            # 3. Split runs to isolate LaTeX text
            latex_start_elem, latex_end_elem = split_match_runs(
                paragraph, start_run, start_offset, end_run, end_offset
            )
            
            # 4. Remove LaTeX elements from parent and insert OMML
            parent = latex_start_elem.getparent()
            children = list(parent)
            
            start_xml_idx = children.index(latex_start_elem)
            end_xml_idx = children.index(latex_end_elem)
            
            for idx in range(start_xml_idx, end_xml_idx + 1):
                parent.remove(children[idx])
                
            # If it's a display equation and represents a whole paragraph, we can wrap it appropriately,
            # but wrapping as basic OMML is fine inside a paragraph.
            parent.insert(start_xml_idx, omml_elem)
            
            stats['converted'] += 1
            if log_callback:
                log_callback(f"Đã chuyển đổi thành công: {math_content[:30]}...")
                
        except Exception as e:
            stats['errors'] += 1
            if log_callback:
                log_callback(f"Lỗi khi chuyển đổi công thức '{math_content[:30]}...': {str(e)}")

def process_container(container, regex, stats, log_callback=None, skip_cases=False):
    """
    Recursively scans a container (like Document, Section, Cell) for paragraphs and tables.
    """
    for paragraph in container.paragraphs:
        process_paragraph(paragraph, regex, stats, log_callback, skip_cases)
        
    for table in container.tables:
        for row in table.rows:
            for cell in row.cells:
                process_container(cell, regex, stats, log_callback, skip_cases)

def build_latex_regex(delimiters_config):
    """
    Builds a regex pattern based on user-selected LaTeX delimiters.
    """
    patterns = []
    
    # Priority: match longer delimiters first to prevent sub-matching issues
    if delimiters_config.get('display_double_dollar', True):
        patterns.append(r'\$\$(.*?)\$\$')
    if delimiters_config.get('display_bracket', True):
        patterns.append(r'\\\[(.*?)\\\]')
    if delimiters_config.get('custom_tags', True):
        patterns.append(r'\[latex\](.*?)\[/latex\]')
    if delimiters_config.get('inline_dollar', True):
        # Match $...$ but restrict it from matching empty or spans containing newlines
        patterns.append(r'\$([^\$\n]+?)\$')
    if delimiters_config.get('inline_parenthesis', True):
        patterns.append(r'\\\((.*?)\\\)')
        
    if not patterns:
        return None
        
    combined_pattern = '|'.join(f'({p})' for p in patterns)
    return re.compile(combined_pattern, re.DOTALL)

def apply_standard_formatting(doc, log_callback=None):
    """
    Standardizes formatting to Times New Roman, size 14, justified, 1.3 line spacing, 6pt space after,
    and standard margins (Top 2.0cm, Bottom 2.0cm, Left 3.0cm, Right 2.0cm).
    Also formats tables to be premium looking (centered, styled margins/shading, 12pt centered font).
    """
    if log_callback:
        log_callback("Đang căn chỉnh lề và định dạng phông chữ Times New Roman 14 chuẩn...")

    # 1. Set global Normal style
    if 'Normal' in doc.styles:
        style = doc.styles['Normal']
        style.font.name = 'Times New Roman'
        style.font.size = Pt(14)
        
        # Set XML level font mappings to enforce it for all Unicode scripts
        try:
            rPr = style.element.get_or_add_rPr()
            rFonts = rPr.get_or_add_rFonts()
            rFonts.set(qn('w:ascii'), 'Times New Roman')
            rFonts.set(qn('w:hAnsi'), 'Times New Roman')
            rFonts.set(qn('w:cs'), 'Times New Roman')
        except Exception:
            pass

        style.paragraph_format.line_spacing = 1.3
        style.paragraph_format.space_after = Pt(6)
        style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    # 2. Set margins
    for section in doc.sections:
        section.top_margin = Cm(2.0)
        section.bottom_margin = Cm(2.0)
        section.left_margin = Cm(3.0)
        section.right_margin = Cm(2.0)

    # 3. Format all existing paragraphs and runs
    for p in doc.paragraphs:
        p.paragraph_format.line_spacing = 1.3
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        
        # Remove redundant bullet points (• A. -> A.)
        text_stripped = p.text.strip()
        if re.match(r'^[A-D]\.(\s|$)', text_stripped):
            pPr = p._p.get_or_add_pPr()
            numPr = pPr.find('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}numPr')
            if numPr is not None:
                pPr.remove(numPr)
                
        for run in p.runs:
            run.font.name = 'Times New Roman'
            run.font.size = Pt(14)

    # Helper functions for table margins (padding) and shading
    def set_table_margins(table, top=120, bottom=120, left=160, right=160):
        tblPr = table._tbl.tblPr
        # Remove existing cell margins if any
        for old in tblPr.xpath('w:tblCellMar'):
            tblPr.remove(old)
        tblCellMar = OxmlElement('w:tblCellMar')
        for side, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
            node = OxmlElement(f'w:{side}')
            node.set(qn('w:w'), str(val))
            node.set(qn('w:type'), 'dxa')
            tblCellMar.append(node)
        tblPr.append(tblCellMar)

    def set_cell_shading(cell, color_hex):
        tcPr = cell._tc.get_or_add_tcPr()
        for old in tcPr.xpath('w:shd'):
            tcPr.remove(old)
        shd = OxmlElement('w:shd')
        shd.set(qn('w:val'), 'clear')
        shd.set(qn('w:color'), 'auto')
        shd.set(qn('w:fill'), color_hex)
        tcPr.append(shd)

    # 4. Format all existing tables with premium styling
    for table in doc.tables:
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        
        # Set clean light gray borders
        tblPr = table._tbl.tblPr
        for old in tblPr.xpath('w:tblBorders'):
            tblPr.remove(old)
        tblBorders = OxmlElement('w:tblBorders')
        for border_name in ['top', 'left', 'bottom', 'right', 'insideH', 'insideV']:
            border = OxmlElement(f'w:{border_name}')
            border.set(qn('w:val'), 'single')
            border.set(qn('w:sz'), '4') # 1/2 pt
            border.set(qn('w:space'), '0')
            border.set(qn('w:color'), 'D3D3D3') # light gray
            tblBorders.append(border)
        tblPr.append(tblBorders)
        
        # Set cell padding (6pt top/bottom, 8pt left/right)
        set_table_margins(table, top=120, bottom=120, left=160, right=160)
        
        for row_idx, row in enumerate(table.rows):
            for col_idx, cell in enumerate(row.cells):
                cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
                
                # Apply shading: Row 0 -> F2F2F2, Col 0 -> FAFAFA
                if row_idx == 0:
                    set_cell_shading(cell, "F2F2F2")
                elif col_idx == 0:
                    set_cell_shading(cell, "FAFAFA")
                
                for p in cell.paragraphs:
                    p.paragraph_format.line_spacing = 1.15
                    p.paragraph_format.space_after = Pt(2)
                    p.paragraph_format.space_before = Pt(2)
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    
                    for run in p.runs:
                        run.font.name = 'Times New Roman'
                        run.font.size = Pt(12) # 12pt for tables to prevent overflow
                        if row_idx == 0 or col_idx == 0:
                            run.font.bold = True

def convert_docx_offline(input_path, output_path, delimiters_config, standardize_formatting=False, log_callback=None, skip_cases=False):
    """
    Converts a .docx file containing LaTeX formulas into a new .docx with native Word equations.
    """
    stats = {'converted': 0, 'errors': 0}
    if log_callback:
        log_callback(f"Đang mở tệp tin: {os.path.basename(input_path)}")
        
    doc = Document(input_path)
    
    # Build regular expression for delimiters
    regex = build_latex_regex(delimiters_config)
    if regex is None:
        raise ValueError("Chưa chọn bất kỳ ký hiệu bao quanh LaTeX nào!")
        
    # Process document body
    process_container(doc, regex, stats, log_callback, skip_cases)
    
    # Process headers and footers in all sections
    for section in doc.sections:
        if section.header and not section.header.is_linked_to_previous:
            process_container(section.header, regex, stats, log_callback, skip_cases)
        if section.footer and not section.footer.is_linked_to_previous:
            process_container(section.footer, regex, stats, log_callback, skip_cases)
            
    # Apply standard formatting if requested
    if standardize_formatting:
        apply_standard_formatting(doc, log_callback)
            
    doc.save(output_path)
    if log_callback:
        log_callback(f"Đã hoàn thành! Chuyển đổi thành công {stats['converted']} công thức, {stats['errors']} lỗi.")
        
    return stats

def convert_text_to_docx(input_path, output_path, delimiters_config, standardize_formatting=True, log_callback=None):
    """
    Converts a plain text file (.txt, .md, .tex) containing LaTeX to a .docx with formatted equations.
    """
    stats = {'converted': 0, 'errors': 0}
    if log_callback:
        log_callback(f"Đang đọc tệp văn bản: {os.path.basename(input_path)}")
        
    # Read text file
    with open(input_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    doc = Document()
    regex = build_latex_regex(delimiters_config)
    
    for line in lines:
        stripped = line.strip('\n')
        p = doc.add_paragraph()
        if stripped:
            p.add_run(stripped)
            if regex:
                process_paragraph(p, regex, stats, log_callback)
                
    # Apply standard formatting (defaults to True for plain text to make it look professional)
    if standardize_formatting:
        apply_standard_formatting(doc, log_callback)
        
    doc.save(output_path)
    if log_callback:
        log_callback(f"Đã hoàn thành! Đã tạo file Word và chuyển đổi {stats['converted']} công thức, {stats['errors']} lỗi.")
        
    return stats


def validate_latex_in_file(file_path, delimiters_config, log_callback=None, output_dir=None):
    """
    Scans a .docx, .doc, or .txt/.md/.tex file for LaTeX formulas and validates their syntax.
    If warnings exist:
      - For .docx/.doc: highlights formulas in bold red, appends red bold warnings after,
        and saves as <name>_kiem_tra_loi.docx.
      - For text files: inserts inline warning markers <<< LỖI LATEX: ... >>>
        and saves as <name>_kiem_tra_loi.<ext>.
    Returns a dictionary with validation stats: {'formulas_found': X, 'warnings': Y}
    """
    import re
    from docx import Document
    from docx.shared import RGBColor
    from docx.text.run import Run
    
    stats = {'formulas_found': 0, 'warnings': 0}
    
    # 1. Build regex
    regex = build_latex_regex(delimiters_config)
    if regex is None:
        if log_callback:
            log_callback("Lỗi: Chưa chọn bất kỳ ký hiệu bao quanh LaTeX nào!")
        return stats
        
    original_base_name = os.path.splitext(os.path.basename(file_path))[0]
    ext = os.path.splitext(file_path)[1].lower()
    
    temp_docx_path = None
    try:
        # Convert legacy .doc to .docx dynamically on Windows
        if ext == '.doc':
            if log_callback:
                log_callback("Phát hiện tệp Word cũ (.doc). Đang tự động chuyển đổi sang .docx để quét lỗi...")
            
            import win32com.client
            word_app = None
            opened_doc = None
            temp_docx_path = file_path + "x_temp" # e.g. path.docx_temp
            try:
                try:
                    word_app = win32com.client.GetActiveObject("Word.Application")
                except Exception:
                    word_app = win32com.client.Dispatch("Word.Application")
                word_app.Visible = False
                opened_doc = word_app.Documents.Open(os.path.abspath(file_path))
                opened_doc.SaveAs2(os.path.abspath(temp_docx_path), FileFormat=12)
            except Exception as e:
                if log_callback:
                    log_callback(f"Lỗi khi chuyển đổi file .doc sang .docx: {str(e)}")
                return stats
            finally:
                if opened_doc:
                    opened_doc.Close(SaveChanges=False)
            
            file_path = temp_docx_path
            ext = '.docx'
            
        # Define common valid LaTeX commands whitelist to find OCR typos
        valid_commands = {
            'frac', 'sqrt', 'sum', 'int', 'lim', 'begin', 'end', 'pmatrix', 'cases', 'array', 'matrix', 'align',
            'alpha', 'beta', 'gamma', 'delta', 'epsilon', 'theta', 'lambda', 'pi', 'sigma', 'omega',
            'Delta', 'Sigma', 'Omega', 'sin', 'cos', 'tan', 'cot', 'log', 'ln', 'to', 'infty',
            'pm', 'mp', 'times', 'div', 'neq', 'le', 'ge', 'approx', 'sim', 'equiv',
            'subset', 'supset', 'cap', 'cup', 'vee', 'wedge', 'neg', 'partial', 'nabla',
            'vec', 'bar', 'hat', 'tilde', 'widehat', 'overparen', 'overarc', 'degree', 'circ',
            'cdot', 'ldots', 'cdots', 'quad', 'qquad', 'left', 'right', 'over', 'choose',
            'limits', 'in', 'ni', 'notin', 'forall', 'exists', 'mathrm', 'mathbf', 'mathit',
            'mathsf', 'mathtt', 'mathcal', 'mathbb', 'text', 'mbox', 'sub', 'sup', 'parallel',
            'perp', 'angle', 'triangle', 'varnothing'
        }
    
        if ext == '.docx':
            doc = Document(file_path)
            
            def validate_paragraph_and_highlight(paragraph, location_prefix):
                runs = paragraph.runs
                if not runs:
                    return
                    
                run_text_full = "".join(run.text for run in runs)
                matches = list(regex.finditer(run_text_full))
                if not matches:
                    return
                    
                # Map character index to (run, offset)
                char_map = []
                for run in runs:
                    run_text = run.text
                    for char_offset in range(len(run_text)):
                        char_map.append((run, char_offset))
                        
                # Process matches in reverse to prevent offset shift when splitting runs
                for match in reversed(matches):
                    start, end = match.span()
                    raw_match = match.group(0)
                    math_content, is_display = parse_math_match(raw_match)
                    if not math_content.strip():
                        continue
                        
                    stats['formulas_found'] += 1
                    
                    warnings = []
                    # Check 1: Balanced braces { }
                    brace_count = 0
                    mismatched_braces = False
                    for char in math_content:
                        if char == '{':
                            brace_count += 1
                        elif char == '}':
                            brace_count -= 1
                            if brace_count < 0:
                                mismatched_braces = True
                    if brace_count != 0 or mismatched_braces:
                        warnings.append("Không khớp dấu ngoặc nhọn { } (có thể thiếu ngoặc đóng/mở)")
                        
                    # Check 2: Raw $
                    unescaped_dollar_matches = re.findall(r'(?<!\\)\$', math_content)
                    if unescaped_dollar_matches:
                        warnings.append("Chứa ký hiệu $ bên trong công thức (có thể gõ lỗi hoặc OCR gộp sai)")
                        
                    # Check 3: Unrecognized LaTeX commands
                    commands_found = re.findall(r'\\([a-zA-Z]+)', math_content)
                    for cmd in commands_found:
                        if cmd not in valid_commands:
                            if cmd.lower() in valid_commands:
                                warnings.append(f"Lệnh \\{cmd} có thể viết sai cỡ chữ (nhãn chuẩn là \\{cmd.lower()})")
                            else:
                                warnings.append(f"Không nhận diện được lệnh \\{cmd} (có thể là lỗi quét ảnh OCR)")
                                
                    # Check 4: Look for OCR typos with numbers
                    mixed_commands = re.findall(r'\\([a-zA-Z0-9]+)', math_content)
                    for cmd in mixed_commands:
                        if any(char.isdigit() for char in cmd):
                            warnings.append(f"Lệnh \\{cmd} chứa số (khả năng cao là lỗi quét OCR, ví dụ \\frac bị quét thành \\f1ac)")
                            
                    if warnings:
                        stats['warnings'] += len(warnings)
                        if log_callback:
                            formula_disp = math_content.replace('\n', ' ')
                            if len(formula_disp) > 40:
                                formula_disp = formula_disp[:37] + "..."
                            log_callback(f"[CẢNH BÁO] Tại {location_prefix} | Công thức: {formula_disp}")
                            for warn in warnings:
                                log_callback(f"  -> {warn}")
                                
                        # Isolate math run
                        start_run, start_offset = char_map[start]
                        end_run, end_offset = char_map[end - 1]
                        
                        latex_start_elem, latex_end_elem = split_match_runs(
                            paragraph, start_run, start_offset, end_run, end_offset
                        )
                        
                        # Style matching runs to bold red
                        parent = latex_start_elem.getparent()
                        children = list(parent)
                        s_idx = children.index(latex_start_elem)
                        e_idx = children.index(latex_end_elem)
                        
                        for idx in range(s_idx, e_idx + 1):
                            child = children[idx]
                            if child.tag.endswith('r'):
                                r_obj = Run(child, paragraph)
                                r_obj.font.color.rgb = RGBColor(255, 0, 0)
                                r_obj.bold = True
                                
                        # Append warning right after formula
                        warn_text = f" [LỖI LATEX: {'; '.join(warnings)}] "
                        warn_run = paragraph.add_run(warn_text)
                        warn_run.font.color.rgb = RGBColor(255, 0, 0)
                        warn_run.bold = True
                        
                        latex_end_elem.addnext(warn_run._r)
                        
            def process_container_validation(container, container_name):
                for idx, paragraph in enumerate(container.paragraphs, 1):
                    validate_paragraph_and_highlight(paragraph, f"{container_name}, Đoạn {idx}")
                    
                for t_idx, table in enumerate(container.tables, 1):
                    for r_idx, row in enumerate(table.rows, 1):
                        for c_idx, cell in enumerate(row.cells, 1):
                            cell_name = f"{container_name}, Bảng {t_idx}, Hàng {r_idx}, Cột {c_idx}"
                            process_container_validation(cell, cell_name)
                            
            # Run traversal
            process_container_validation(doc, "Phần thân")
            for s_idx, section in enumerate(doc.sections, 1):
                if section.header and not section.header.is_linked_to_previous:
                    process_container_validation(section.header, f"Header Phần {s_idx}")
                if section.footer and not section.footer.is_linked_to_previous:
                    process_container_validation(section.footer, f"Footer Phần {s_idx}")
                    
            if stats['warnings'] > 0:
                file_dir = os.path.dirname(file_path)
                target_dir = output_dir if output_dir else file_dir
                output_file_name = f"{original_base_name}_kiem_tra_loi.docx"
                output_file_path = os.path.join(target_dir, output_file_name)
                doc.save(output_file_path)
                if log_callback:
                    log_callback(f"Đã lưu tệp quét lỗi tại: {output_file_path}")
                    
        elif ext in ('.txt', '.md', '.tex'):
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                
            new_lines = []
            file_has_warnings = False
            
            for line_idx, line in enumerate(lines, 1):
                matches = list(regex.finditer(line))
                if not matches:
                    new_lines.append(line)
                    continue
                    
                current_line = line
                for match in reversed(matches):
                    start, end = match.span()
                    raw_match = match.group(0)
                    math_content, is_display = parse_math_match(raw_match)
                    if not math_content.strip():
                        continue
                        
                    stats['formulas_found'] += 1
                    
                    warnings = []
                    # Check 1: Balanced braces { }
                    brace_count = 0
                    mismatched_braces = False
                    for char in math_content:
                        if char == '{':
                            brace_count += 1
                        elif char == '}':
                            brace_count -= 1
                            if brace_count < 0:
                                mismatched_braces = True
                    if brace_count != 0 or mismatched_braces:
                        warnings.append("Không khớp dấu ngoặc nhọn { } (có thể thiếu ngoặc đóng/mở)")
                        
                    # Check 2: Raw $
                    unescaped_dollar_matches = re.findall(r'(?<!\\)\$', math_content)
                    if unescaped_dollar_matches:
                        warnings.append("Chứa ký hiệu $ bên trong công thức (có thể gõ lỗi hoặc OCR gộp sai)")
                        
                    # Check 3: Unrecognized LaTeX commands
                    commands_found = re.findall(r'\\([a-zA-Z]+)', math_content)
                    for cmd in commands_found:
                        if cmd not in valid_commands:
                            if cmd.lower() in valid_commands:
                                warnings.append(f"Lệnh \\{cmd} có thể viết sai cỡ chữ (nhãn chuẩn là \\{cmd.lower()})")
                            else:
                                warnings.append(f"Không nhận diện được lệnh \\{cmd} (có thể là lỗi quét ảnh OCR)")
                                
                    # Check 4: Look for OCR typos with numbers
                    mixed_commands = re.findall(r'\\([a-zA-Z0-9]+)', math_content)
                    for cmd in mixed_commands:
                        if any(char.isdigit() for char in cmd):
                            warnings.append(f"Lệnh \\{cmd} chứa số (khả năng cao là lỗi quét OCR, ví dụ \\frac bị quét thành \\f1ac)")
                            
                    if warnings:
                        stats['warnings'] += len(warnings)
                        file_has_warnings = True
                        if log_callback:
                            formula_disp = math_content.replace('\n', ' ')
                            if len(formula_disp) > 40:
                                formula_disp = formula_disp[:37] + "..."
                            log_callback(f"[CẢNH BÁO] Tại Dòng {line_idx} | Công thức: {formula_disp}")
                            for warn in warnings:
                                log_callback(f"  -> {warn}")
                                
                        # Insert inline warning marker
                        warn_text = f" <<< LỖI LATEX: {'; '.join(warnings)} >>> "
                        current_line = current_line[:end] + warn_text + current_line[end:]
                        
                new_lines.append(current_line)
                
            if file_has_warnings:
                file_dir = os.path.dirname(file_path)
                target_dir = output_dir if output_dir else file_dir
                output_file_name = f"{original_base_name}_kiem_tra_loi{ext}"
                output_file_path = os.path.join(target_dir, output_file_name)
                with open(output_file_path, 'w', encoding='utf-8') as f:
                    f.writelines(new_lines)
                if log_callback:
                    log_callback(f"Đã lưu tệp quét lỗi tại: {output_file_path}")
        else:
            if log_callback:
                log_callback(f"Lỗi: Định dạng tệp {ext} không được hỗ trợ để quét lỗi!")
    except Exception as e:
        if log_callback:
            log_callback(f"Lỗi khi quét tệp {os.path.basename(file_path)}: {str(e)}")
    finally:
        if temp_docx_path and os.path.exists(temp_docx_path):
            try:
                os.remove(temp_docx_path)
            except Exception:
                pass
                    
    return stats
