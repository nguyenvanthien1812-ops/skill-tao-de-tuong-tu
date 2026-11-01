"""
OMML → MathType conversion pipeline.

Finds every ``m:oMath`` equation in a ``.docx``, converts each to a MathType
OLE object (``Equation.DSMT6``), and writes a new ``.docx`` with those objects
embedded in place of the original OMML equations. The original OMML is kept as
a fallback so the equations stay visible in every Word environment.
"""

from __future__ import annotations

import copy
import logging
import uuid
import zipfile
from dataclasses import dataclass

from lxml import etree

from .mathml_to_mtef import mathml_to_mtef_bytes
from .mtef import make_equation_native
from .ole import make_ole
from .omml_to_mathml import omml_to_mathml

logger = logging.getLogger(__name__)

# ── Namespaces ────────────────────────────────────────────────────────────────

_NS = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "m": "http://schemas.openxmlformats.org/officeDocument/2006/math",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "v": "urn:schemas-microsoft-com:vml",
    "o": "urn:schemas-microsoft-com:office:office",
    "mc": "http://schemas.openxmlformats.org/markup-compatibility/2006",
    "wp": "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing",
}

_W = _NS["w"]
_M = _NS["m"]
_R = _NS["r"]
_V = _NS["v"]
_O = _NS["o"]
_MC = _NS["mc"]

_REL_OLEOBJECT = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/oleObject"

NSMAP_W = dict(_NS)


def _w(tag: str) -> str:
    return f"{{{_W}}}{tag}"


def _m(tag: str) -> str:
    return f"{{{_M}}}{tag}"


def _r(tag: str) -> str:
    return f"{{{_R}}}{tag}"


def _v(tag: str) -> str:
    return f"{{{_V}}}{tag}"


def _o(tag: str) -> str:
    return f"{{{_O}}}{tag}"


@dataclass
class ConversionSummary:
    """Outcome of a :func:`convert` run."""

    found: int = 0
    converted: int = 0
    skipped: int = 0
    errors: int = 0


# ── OLE object XML builder ────────────────────────────────────────────────────


def _make_ole_xml(
    rel_id: str,
    shape_id: str,
    obj_id: str,
    width_emu: int,
    height_emu: int,
    omml_fallback: etree._Element,
) -> etree._Element:
    """
    Build an mc:AlternateContent element that offers:

      • mc:Choice  — MathType OLE object (used when Word can call MathType)
      • mc:Fallback — original OMML equation (used when MathType is absent,
                       keeps the equation visible in all environments)

    Structure:
      <mc:AlternateContent>
        <mc:Choice Requires="v">
          <w:r>
            <w:object ...>
              <v:shape ... o:ole=""/>
              <o:OLEObject ProgID="Equation.DSMT6" ... r:id="..."/>
            </w:object>
          </w:r>
        </mc:Choice>
        <mc:Fallback>
          <m:oMath> ... original equation ... </m:oMath>
        </mc:Fallback>
      </mc:AlternateContent>
    """
    # Convert EMU to twips (1 inch = 914400 EMU = 1440 twips)
    dxa_w = max(100, width_emu * 1440 // 914400)
    dxa_h = max(100, height_emu * 1440 // 914400)

    ac = etree.Element(f"{{{_MC}}}AlternateContent")

    # ── Primary: MathType OLE ──────────────────────────────────────────────
    # Requires="mtype" references a custom namespace that no standard Word
    # build recognises. Per ECMA-376 MCE rules, unknown Requires → Fallback.
    # This means Word always renders the OMML Fallback (equations stay visible),
    # while MathType (which scans raw XML for Equation.DSMT* OLE objects) still
    # finds and uses the embedded binary.
    # Declare the custom namespace via nsmap so the XML is valid.
    _MTYPE_NS = "urn:mathtype:oleobject"
    choice = etree.SubElement(ac, f"{{{_MC}}}Choice", nsmap={"mtype": _MTYPE_NS})
    choice.set("Requires", "mtype")

    wr = etree.SubElement(choice, _w("r"))
    wobj = etree.SubElement(wr, _w("object"))
    wobj.set(_w("dxaOrig"), str(dxa_w))
    wobj.set(_w("dyaOrig"), str(dxa_h))

    vshape = etree.SubElement(wobj, _v("shape"))
    vshape.set("id", shape_id)
    vshape.set("type", "#_x0000_t75")
    vshape.set("style", f"width:{dxa_w / 20:.1f}pt;height:{dxa_h / 20:.1f}pt")
    vshape.set(f"{{{_O}}}ole", "")

    oleobj = etree.SubElement(wobj, _o("OLEObject"))
    oleobj.set("Type", "Embed")
    oleobj.set("ProgID", "Equation.DSMT6")
    oleobj.set("ShapeID", shape_id)
    oleobj.set("DrawAspect", "Content")
    oleobj.set("ObjectID", obj_id)
    oleobj.set(_r("id"), rel_id)

    # ── Fallback: original OMML (always visible) ───────────────────────────
    fallback = etree.SubElement(ac, f"{{{_MC}}}Fallback")
    fallback.append(copy.deepcopy(omml_fallback))

    return ac


# ── docx ZIP manipulation ─────────────────────────────────────────────────────


def _parse_xml(data: bytes) -> etree._Element:
    parser = etree.XMLParser(remove_blank_text=False)
    return etree.fromstring(data, parser)


def _serialise_xml(root: etree._Element) -> bytes:
    return etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)


def _add_relationship(rels_root: etree._Element, rel_id: str, rel_type: str, target: str) -> None:
    ns = "http://schemas.openxmlformats.org/package/2006/relationships"
    etree.SubElement(
        rels_root,
        f"{{{ns}}}Relationship",
        {
            "Id": rel_id,
            "Type": rel_type,
            "Target": target,
        },
    )


def _ensure_content_type(ct_root: etree._Element, part_name: str, content_type: str) -> None:
    ns = "http://schemas.openxmlformats.org/package/2006/content-types"
    for child in ct_root:
        if child.get("PartName") == part_name:
            return
    etree.SubElement(
        ct_root,
        f"{{{ns}}}Override",
        {
            "PartName": part_name,
            "ContentType": content_type,
        },
    )


# ── Main conversion pipeline ──────────────────────────────────────────────────


def convert(input_path: str, output_path: str) -> ConversionSummary:
    """Convert every OMML equation in ``input_path`` and write ``output_path``.

    Returns a :class:`ConversionSummary` describing how many equations were
    found, converted, skipped (empty content) and failed. The output ``.docx``
    is always written, even when some equations fail to convert (failed
    equations are left as their original OMML).
    """
    with zipfile.ZipFile(input_path, "r") as zin:
        names = set(zin.namelist())
        zdata = {n: zin.read(n) for n in names}

    doc_xml_path = "word/document.xml"
    rels_path = "word/_rels/document.xml.rels"
    ct_path = "[Content_Types].xml"

    doc_root = _parse_xml(zdata[doc_xml_path])
    rels_root = _parse_xml(
        zdata.get(
            rels_path,
            b'<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"/>',
        )
    )
    ct_root = _parse_xml(zdata[ct_path])

    # Collect all m:oMath elements (deferred to avoid mutating tree during iter)
    omath_list = list(doc_root.iter(_m("oMath")))
    summary = ConversionSummary(found=len(omath_list))
    logger.info("Found %d equation(s)", summary.found)

    # Track which rIds are already used
    existing_ids = {child.get("Id") for child in rels_root if child.get("Id")}

    def _new_rel_id() -> str:
        i = 1
        while f"rIdOle{i}" in existing_ids:
            i += 1
        rid = f"rIdOle{i}"
        existing_ids.add(rid)
        return rid

    ole_index = 1
    # Scan existing embeddings to avoid collision
    while f"word/embeddings/oleObject{ole_index}.bin" in names:
        ole_index += 1

    for eq_num, omath in enumerate(omath_list, 1):
        try:
            # 1. OMML → MathML
            mathml_el = omml_to_mathml(omath)

            # 2. MathML → MTEF binary
            eq_bytes = mathml_to_mtef_bytes(mathml_el)
            if not eq_bytes:
                summary.skipped += 1
                logger.warning("Equation %d: empty content, skipping", eq_num)
                continue

            # 3. MTEF → Equation Native stream
            native_stream = make_equation_native(eq_bytes)

            # 4. Equation Native stream → OLE compound file
            ole_bin = make_ole(native_stream)

            # 5. Store .bin in docx embeddings
            bin_name = f"word/embeddings/oleObject{ole_index}.bin"
            zdata[bin_name] = ole_bin
            ole_index += 1

            # 6. Add relationship
            rel_id = _new_rel_id()
            _add_relationship(
                rels_root, rel_id, _REL_OLEOBJECT, f"embeddings/oleObject{ole_index - 1}.bin"
            )

            # 7. Add content type for .bin
            _ensure_content_type(
                ct_root,
                f"/{bin_name}",
                "application/vnd.openxmlformats-officedocument.oleObject",
            )

            # 8. Replace the equation node in the document tree.
            #    m:oMath may live directly in w:p, or be wrapped by m:oMathPara.
            #    In either case we replace the outermost equation container so
            #    we don't leave an empty orphan oMathPara behind.
            #
            #    The replacement is mc:AlternateContent with:
            #      Choice  → MathType OLE object (rendered by MathType)
            #      Fallback → original OMML     (rendered natively by Word)
            shape_id = f"_x0000_i{1024 + eq_num}"
            obj_id = "{" + str(uuid.uuid4()).upper() + "}"

            # Determine the node to replace
            replace_node = omath
            parent = omath.getparent()
            if parent is not None and etree.QName(parent).localname == "oMathPara":
                replace_node = parent
                parent = parent.getparent()

            alt = _make_ole_xml(
                rel_id,
                shape_id,
                obj_id,
                width_emu=914400,  # 1 inch wide  — default display size
                height_emu=457200,  # 0.5 inch tall
                omml_fallback=omath,  # original equation kept as visible fallback
            )

            if parent is not None:
                idx = list(parent).index(replace_node)
                parent.remove(replace_node)
                parent.insert(idx, alt)

            summary.converted += 1
            logger.info("Equation %d: converted → %s", eq_num, bin_name)

        except Exception as exc:  # noqa: BLE001 — keep going; report per-equation
            summary.errors += 1
            logger.error("Equation %d: %s", eq_num, exc)

    # Serialise modified XML back
    zdata[doc_xml_path] = _serialise_xml(doc_root)
    zdata[rels_path] = _serialise_xml(rels_root)
    zdata[ct_path] = _serialise_xml(ct_root)

    # Write output docx
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zout:
        for name, data in zdata.items():
            zout.writestr(name, data)

    logger.info("Saved → %s", output_path)
    return summary
