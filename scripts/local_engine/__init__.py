# -*- coding: utf-8 -*-
"""
Local MathType OLE Engine (100% Offline)
Chuyển đổi công thức LaTeX trong file Word thành MathType OLE (Equation.DSMT4)
hoàn toàn cục bộ trên máy tính giáo viên mà không cần máy chủ Backend.
"""

from .docx_processor import convert_docx_latex_to_mathtype, find_libreoffice_python

__all__ = ["convert_docx_latex_to_mathtype", "find_libreoffice_python"]
