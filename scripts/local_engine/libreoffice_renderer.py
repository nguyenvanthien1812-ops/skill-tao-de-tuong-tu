import os
import sys
import json
import subprocess
import time
import struct

# Builder dựng OLE đủ 4 stream (kể cả \x01CompObj) để Word kích đúp mở lại
# được bằng MathType. Cùng thư mục với script này.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mathtype_ole_builder import make_mathtype_ole, make_arc_equation_ole
try:
    from arc_symbol_builder import (
        extract_arc_base_from_starmath,
        is_arc_starmath,
        build_arc_equation_native,
    )
except Exception:
    extract_arc_base_from_starmath = None
    is_arc_starmath = None
    build_arc_equation_native = None

def _connect(host, port, launch=True, tries=15):
    """Resolve a UNO context, launching a headless soffice if needed.

    Returns the resolved component context, or None if it could not connect.
    Used both for the initial connect and to RECONNECT in Phase 2 after a
    heavy Phase-1 render loop crashes soffice ('Binary URP bridge already
    disposed'), which otherwise loses every v3 OLE bin.
    """
    import uno

    def _try_resolve():
        local_ctx = uno.getComponentContext()
        resolver = local_ctx.ServiceManager.createInstanceWithContext(
            "com.sun.star.bridge.UnoUrlResolver", local_ctx)
        return resolver.resolve(
            f"uno:socket,host={host},port={port};urp;StarOffice.ComponentContext")

    try:
        return _try_resolve()
    except Exception:
        if not launch:
            return None
        soffice_candidates = [
            r"C:\Program Files\LibreOffice\program\soffice.exe",
            r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
            os.path.expandvars(r"%ProgramFiles%\LibreOffice\program\soffice.exe"),
        ]
        soffice_path = "soffice"
        for sc in soffice_candidates:
            if sc and os.path.exists(sc):
                soffice_path = sc
                break
        if not os.path.exists(soffice_path):
            soffice_path = "soffice"  # fallback to PATH
        subprocess.Popen([
            soffice_path,
            "--headless", "--invisible", "--nocrashreport", "--nodefault",
            "--norestore", "--nologo", "--nofirststartwizard",
            f"--accept=socket,host={host},port={port};urp;"
        ])
        for _ in range(tries):
            time.sleep(1)
            try:
                return _try_resolve()
            except Exception:
                pass
        return None


def main():
    if len(sys.argv) < 2:
        print("Usage: python libreoffice_renderer.py <config_json_path>")
        sys.exit(1)
        
    config_path = sys.argv[1]
    if not os.path.exists(config_path):
        print(f"Error: Config file not found at {config_path}")
        sys.exit(1)
        
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
        
    formulas = config.get("formulas", [])
    output_dir = config.get("output_dir", "")
    host = config.get("host", "localhost")
    port = config.get("port", 2002)
    
    if not output_dir:
        print("Error: output_dir is required in config")
        sys.exit(1)
        
    os.makedirs(output_dir, exist_ok=True)
    
    # Connect to LibreOffice (and self-start if needed)
    import uno
    from com.sun.star.beans import PropertyValue
    from com.sun.star.awt import Size, Point
    
    def _prop(name, value):
        p = PropertyValue()
        p.Name = name
        p.Value = value
        return p
        
    try:
        local_ctx = uno.getComponentContext()
        resolver = local_ctx.ServiceManager.createInstanceWithContext(
            "com.sun.star.bridge.UnoUrlResolver", local_ctx)
        ctx = resolver.resolve(f"uno:socket,host={host},port={port};urp;StarOffice.ComponentContext")
    except Exception:
        ctx = _connect(host, port, launch=True)
        if ctx is None:
            print("Error: Could not connect to or start LibreOffice.")
            sys.exit(1)

    smgr = ctx.ServiceManager
    desktop = smgr.createInstanceWithContext("com.sun.star.frame.Desktop", ctx)

    # Create empty Draw document
    doc = desktop.loadComponentFromURL("private:factory/sdraw", "_blank", 0, (_prop("Hidden", True),))
    draw_page = doc.getDrawPages().getByIndex(0)

    results = []

    # ── Phase 1: render mỗi công thức ra WMF (ảnh xem trước + kích thước) ──
    # Vẫn phải làm từng công thức vì mỗi ảnh có kích thước riêng.
    for idx, formula in enumerate(formulas):

        res = {"index": idx, "formula": formula, "success": False, "error": None}
        try:
            # Create OLE2Shape for Math
            ole_shape = doc.createInstance("com.sun.star.drawing.OLE2Shape")
            ole_shape.CLSID = "078B7ABA-54FC-457F-8551-6147e776a997"

            # Set default large size (20cm x 10cm)
            ole_shape.setSize(Size(20000, 10000))
            ole_shape.setPosition(Point(0, 0))

            # Add shape to page
            draw_page.add(ole_shape)

            # Set formula string
            embedded = ole_shape.EmbeddedObject
            embedded.changeState(1) # EmbedStates.RUNNING
            component = embedded.getComponent()

            # Set formula string first (as setting Formula resets properties)
            component.Formula = formula

            # Configure formula font (Times New Roman, 14pt) AFTER setting formula
            try:
                component.BaseFontHeight = 14
                component.FontNameVariables = "Times New Roman"
                component.FontNameFunctions = "Times New Roman"
                component.FontNameNumbers = "Times New Roman"
                component.FontNameText = "Times New Roman"
            except Exception as fe:
                pass

            # Force update embedded object visual presentation
            try:
                embedded.update()
            except Exception as ue:
                pass

            # Query actual formula visual size and resize shape before export
            try:
                formula_size = embedded.getVisualAreaSize(1)
                if formula_size.Width > 0 and formula_size.Height > 0:
                    # Convert from Twips (1/1440 inch) to 1/100th mm (1/2540 inch)
                    w_mm100 = int(formula_size.Width * 2540 / 1440)
                    h_mm100 = int(formula_size.Height * 2540 / 1440)
                    ole_shape.setSize(Size(w_mm100, h_mm100))
            except Exception as sz_err:
                pass

            # Export to WMF (kept for physical size metadata: WMF carries the
            # true formula dimensions in EMU used to size the Word shape).
            gef = smgr.createInstanceWithContext("com.sun.star.drawing.GraphicExportFilter", ctx)
            gef.setSourceDocument(ole_shape)

            wmf_filename = f"formula_{idx}.wmf"
            wmf_path = os.path.join(output_dir, wmf_filename)
            url_wmf = "file:///" + os.path.abspath(wmf_path).replace("\\", "/")

            args = (
                _prop("URL", url_wmf),
                _prop("MimeType", "image/x-wmf"),
            )
            gef.filter(args)

            # Export to PNG (raster) — this is the preview Word actually displays.
            # WMF previews embed LibreOffice's OpenSymbol font, which Word lacks and
            # substitutes, spreading digits/shrinking variables. A raster PNG renders
            # the exact pixels LibreOffice drew, so Word shows the correct appearance.
            png_path = os.path.join(output_dir, f"formula_{idx}.png")
            try:
                true_sz = ole_shape.getSize()  # 1/100 mm, kích thước thật
                # LỖI 1 (căn thiếu nét): FilterData PixelWidth/PixelHeight KHÔNG
                # có tác dụng với OLE shape → PNG luôn ~96 DPI, nét vinculum √ chỉ
                # ~1px nên biến mất khi Word thu nhỏ ảnh về kích thước vật lý.
                # Cách chắc chắn: PHÓNG TO SHAPE THẬT lên SCALE lần trước khi
                # export PNG → PNG có nhiều pixel thật, nét mảnh được giữ lại khi
                # Word co ảnh về kích thước vật lý (nét được khử răng cưa, không
                # mất). WMF đã export ở kích thước thật phía trên nên metadata
                # kích thước Word shape KHÔNG bị ảnh hưởng.
                SCALE = 8
                ole_shape.setSize(Size(true_sz.Width * SCALE,
                                       true_sz.Height * SCALE))
                gef.setSourceDocument(ole_shape)
                url_png = "file:///" + os.path.abspath(png_path).replace("\\", "/")
                gef.filter((
                    _prop("URL", url_png),
                    _prop("MimeType", "image/png"),
                ))
                # Khôi phục kích thước thật (phòng trường hợp shape được dùng lại)
                ole_shape.setSize(true_sz)
            except Exception:
                png_path = None

            # Remove and dispose shape to free memory
            draw_page.remove(ole_shape)
            try:
                ole_shape.dispose()
            except:
                pass

            if os.path.exists(wmf_path) and os.path.getsize(wmf_path) > 0:
                res["success"] = True
                res["wmf_path"] = wmf_path
                if png_path and os.path.exists(png_path) and os.path.getsize(png_path) > 0:
                    res["png_path"] = png_path
            else:
                res["error"] = "WMF file was not created or empty"
        except Exception as e:
            res["error"] = str(e)

        results.append(res)

    try:
        doc.close(False)
    except Exception as e:
        pass

    # ── Phase 2: trích .bin theo LÔ (1 lần lưu + mở, thay vì N lần) ──
    # Đây là chỗ tăng tốc chính: bản cũ tạo/lưu/mở lại 1 file .doc cho MỖI
    # công thức (~250ms/công thức). Giờ chèn TẤT CẢ công thức vào 1 tài liệu
    # swriter, lưu 1 lần, mở lại 1 lần, rồi trích mọi stream "Equation Native".
    # LibreOffice đặt tên object đếm LÙI từ 2147483647, nên sort tên GIẢM DẦN
    # sẽ khôi phục đúng thứ tự chèn (đã kiểm chứng).
    _extract_bins_batch(desktop, smgr, formulas, results, output_dir,
                         host=host, port=port)

    # Write results back to a JSON file
    result_path = os.path.join(output_dir, "results.json")
    with open(result_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"Render completed. Results saved to {result_path}")


def _extract_bins_batch(desktop, smgr, formulas, results, output_dir,
                        chunk_size=20, host="localhost", port=2002):
    """Trích 'Equation Native' (MTEF v3) cho mọi công thức, ghi formula_{idx}.bin
    và gắn 'bin_path' vào results theo đúng thứ tự.

    Chia thành từng LÔ nhỏ (chunk_size công thức/lô). Chèn TẤT CẢ công thức vào
    một tài liệu swriter rồi lưu một lần sẽ làm sập cầu UNO ('Binary URP bridge
    already disposed') khi số lượng lớn (~133) → 0 bin sinh ra → docx_processor
    rơi về đường dự phòng MTEF v5 (MathType mở ra rỗng). Lưu từng lô nhỏ giữ mỗi
    lần lưu đủ nhẹ; ngoài ra nếu cầu UNO đã chết sau vòng render Phase 1 nặng,
    ta KẾT NỐI LẠI (khởi động lại soffice) trước mỗi lô để lô vẫn chạy được.
    """
    import re as _re
    import uno
    from com.sun.star.beans import PropertyValue

    def _prop(name, value):
        p = PropertyValue()
        p.Name = name
        p.Value = value
        return p

    _HERE = os.path.dirname(os.path.abspath(__file__))
    if _HERE not in sys.path:
        sys.path.insert(0, _HERE)
    try:
        import site
        for _p in site.getsitepackages():
            if _p not in sys.path:
                sys.path.append(_p)
        _user_site = site.getusersitepackages()
        if _user_site and _user_site not in sys.path:
            sys.path.append(_user_site)
    except Exception:
        pass
    import olefile

    # Giữ desktop hiện tại; nếu cầu chết sẽ thay bằng desktop mới.
    state = {"desktop": desktop}

    def _live_desktop(force_reconnect=False):
        """Trả về desktop còn sống, kết nối lại nếu cần. None nếu thất bại."""
        d = state["desktop"]
        if not force_reconnect:
            try:
                if d is not None:
                    d.getComponents()  # chạm thử để phát hiện cầu chết
                    return d
            except Exception:
                pass
        # Kết nối lại (khởi động lại soffice nếu đã tắt)
        state["desktop"] = None
        ctx = _connect(host, port, launch=True)
        if ctx is None:
            return None
        new_desktop = ctx.ServiceManager.createInstanceWithContext(
            "com.sun.star.frame.Desktop", ctx)
        state["desktop"] = new_desktop
        return new_desktop

    def _extract_one_chunk(chunk_formulas, base_idx, _retried=False):
        """Chèn chunk_formulas vào 1 doc, lưu, trích bin, gắn vào results tại
        vị trí base_idx + i. Trả về số bin trích được."""
        d = _live_desktop()
        if d is None:
            print(f"Chunk at {base_idx}: no live LibreOffice bridge — skipping")
            return 0

        batch_doc_path = os.path.join(output_dir, f"_batch_ole_{base_idx}.doc")
        n_extracted = 0
        try:
            w_doc = d.loadComponentFromURL(
                "private:factory/swriter", "_blank", 0, (_prop("Hidden", True),))
            w_text = w_doc.getText()
            w_cursor = w_text.createTextCursor()

            for formula in chunk_formulas:
                w_ole_obj = w_doc.createInstance("com.sun.star.text.TextEmbeddedObject")
                w_ole_obj.CLSID = "078B7ABA-54FC-457F-8551-6147e776a997"
                w_text.insertTextContent(w_cursor, w_ole_obj, False)
                w_embedded = w_ole_obj.EmbeddedObject
                w_embedded.changeState(1)
                w_component = w_embedded.getComponent()
                w_component.Formula = formula
                try:
                    w_component.BaseFontHeight = 14
                    w_component.FontNameVariables = "Times New Roman"
                    w_component.FontNameFunctions = "Times New Roman"
                    w_component.FontNameNumbers = "Times New Roman"
                    w_component.FontNameText = "Times New Roman"
                except Exception:
                    pass
                w_text.insertControlCharacter(
                    w_cursor,
                    uno.getConstantByName(
                        "com.sun.star.text.ControlCharacter.PARAGRAPH_BREAK"),
                    False)

            w_doc.storeToURL(uno.systemPathToFileUrl(batch_doc_path),
                             (_prop("FilterName", "MS Word 97"),))
            w_doc.close(False)

            ole = olefile.OleFileIO(batch_doc_path)
            names = [n[1] for n in ole.listdir()
                     if len(n) == 3 and n[0] == "ObjectPool" and n[2] == "Equation Native"]

            def _key(n):
                m = _re.search(r"(\d+)", n)
                return int(m.group(1)) if m else 0
            # Tên object đếm LÙI → sort GIẢM DẦN = đúng thứ tự chèn công thức.
            names.sort(key=_key, reverse=True)

            # Nếu số stream khác số công thức trong lô thì thứ tự không còn tin
            # cậy → bỏ qua cả lô (các công thức đó rơi về ảnh WMF + dự phòng).
            if len(names) != len(chunk_formulas):
                print(f"Chunk at {base_idx}: expected {len(chunk_formulas)} "
                      f"Equation Native streams, found {len(names)} "
                      f"— retrying one-by-one")
                ole.close()
                # Thay vì bỏ cả chunk, thử lại từng công thức riêng lẻ
                # để chỉ công thức lỗi bị mất, không kéo theo cả lô.
                # Guard _retried=True tránh đệ quy vô hạn.
                if len(chunk_formulas) > 1 and not _retried:
                    for _fi, _formula in enumerate(chunk_formulas):
                        n_extracted += _extract_one_chunk(
                            [_formula], base_idx + _fi, _retried=True
                        )
                return n_extracted

            for i, name in enumerate(names):
                gidx = base_idx + i
                if gidx >= len(results):
                    break
                try:
                    eq_native_bytes = ole.openstream(
                        ["ObjectPool", name, "Equation Native"]).read()

                    # DEBUG: lưu raw MTEF để phân tích (lưu vào thư mục gốc)
                    # Chi bat khi LOCAL_ENGINE_DEBUG=1 (tranh ghi rac vao thu muc skill
                    # va tranh loi quyen ghi lam mat OLE tren may giao vien).
                    if os.environ.get("LOCAL_ENGINE_DEBUG") == "1":
                        try:
                            import tempfile as _tf
                            with open(os.path.join(_tf.gettempdir(), f"raw_{gidx}.bin"), "wb") as _dbg:
                                _dbg.write(eq_native_bytes)
                        except Exception:
                            pass

                    # Cung tròn thuần: thay Equation Native LO bằng MTEF MathType THẬT
                    # Preview Phase 1: csup ⌢ sát chữ (không còn stack khe rộng).
                    sm = None
                    try:
                        sm = results[gidx].get("formula") or (
                            formulas[gidx] if gidx < len(formulas) else None
                        )
                    except Exception:
                        sm = None
                    if sm and build_arc_equation_native is not None:
                        import re as _re_arc
                        _pure = _re_arc.fullmatch(
                            r"\s*\{\s*([A-Za-z0-9]+)\s*\}\s*csup(?:\s+size\*[0-9.]+)?\s*\{[^{}]*\u200e[^{}]*\}\s*",
                            sm,
                        )
                        if not _pure:
                            _pure = _re_arc.fullmatch(
                                r"\s*stack\s*\{\s*[^#]*\u200e\s*#\s*([A-Za-z0-9]+)\s*\}\s*",
                                sm,
                            )
                        if _pure:
                            base = _pure.group(1)
                            try:
                                eq_native_bytes = build_arc_equation_native(base)
                                results[gidx]["arc_base"] = base
                            except Exception as _arc_e:
                                results[gidx]["arc_error"] = str(_arc_e)

                    ole_bin = make_mathtype_ole(eq_native_bytes)
                    bin_path = os.path.join(output_dir, f"formula_{gidx}.bin")
                    with open(bin_path, "wb") as bf:
                        bf.write(ole_bin)
                    results[gidx]["bin_path"] = bin_path
                    n_extracted += 1
                except Exception as e:
                    results[gidx].setdefault("error", None)
                    results[gidx]["error"] = f"bin extract failed: {e}"
            ole.close()
        except Exception as e:
            # Cầu chết giữa chừng (thường xảy ra với lô ĐẦU vì desktop kế thừa từ
            # Phase 1 đã hỏng). Kết nối lại và thử lại lô này MỘT lần trước khi bỏ.
            print(f"Chunk bin extraction failed at {base_idx}: {e}")
            state["desktop"] = None
            if os.path.exists(batch_doc_path):
                try:
                    os.remove(batch_doc_path)
                except Exception:
                    pass
            if not _retried:
                if _live_desktop(force_reconnect=True) is not None:
                    print(f"Chunk at {base_idx}: reconnected, retrying once")
                    return _extract_one_chunk(chunk_formulas, base_idx, _retried=True)
            return n_extracted
        finally:
            if os.path.exists(batch_doc_path):
                try:
                    os.remove(batch_doc_path)
                except Exception:
                    pass
        return n_extracted

    total_extracted = 0
    for base in range(0, len(formulas), chunk_size):
        chunk = formulas[base:base + chunk_size]
        total_extracted += _extract_one_chunk(chunk, base)
    print(f"Batch bin extraction: {total_extracted}/{len(formulas)} bins produced")

if __name__ == "__main__":
    main()
