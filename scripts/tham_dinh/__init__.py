# -*- coding: utf-8 -*-
"""
Bộ công cụ Thẩm định Đề thi Toán THCS/THPT
============================================
Gồm 5 module chính:
  - exam_extractor   : Đọc file Đề + HDC + Ma trận → ExamData
  - exam_validator   : Kiểm tra 42 tiêu chí → ValidationReport
  - report_generator : Xuất Word biên bản + Excel dashboard + kế hoạch sửa
  - auto_fixer       : Thực hiện sửa tự động các lỗi được duyệt
  - exam_reviewer_cli: CLI entry point – pipeline hoàn chỉnh
"""

__version__ = "1.0.0"
__author__  = "Bộ công cụ Thẩm định Đề thi"
