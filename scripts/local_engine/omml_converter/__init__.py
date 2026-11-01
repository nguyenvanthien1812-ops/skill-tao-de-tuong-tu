"""Convert OMML equations in ``.docx`` files to MathType OLE objects."""

from __future__ import annotations

from .converter import ConversionSummary, convert
from .mathml_to_mtef import mathml_to_mtef_bytes
from .mtef import make_equation_native
from .ole import make_ole
from .omml_to_mathml import omml_to_mathml

__version__ = "0.1.0"

__all__ = [
    "ConversionSummary",
    "__version__",
    "convert",
    "make_equation_native",
    "make_ole",
    "mathml_to_mtef_bytes",
    "omml_to_mathml",
]
