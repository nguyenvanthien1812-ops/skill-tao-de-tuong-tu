import os
import re
import shutil
import zipfile
import sys

def patch_pptx(pptx_path):
    print(f"Patching fonts in {pptx_path}...")
    temp_dir = pptx_path + "_temp_unpack"
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)

    with zipfile.ZipFile(pptx_path, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)

    # 1. Update theme XMLs
    theme_dir = os.path.join(temp_dir, 'ppt', 'theme')
    if os.path.exists(theme_dir):
        for f in os.listdir(theme_dir):
            if f.endswith('.xml'):
                fpath = os.path.join(theme_dir, f)
                with open(fpath, 'r', encoding='utf-8') as tf:
                    content = tf.read()
                content = re.sub(r'<a:latin typeface="[^"]*"', '<a:latin typeface="Times New Roman"', content)
                content = re.sub(r'<a:ea typeface="[^"]*"', '<a:ea typeface="Times New Roman"', content)
                content = re.sub(r'<a:cs typeface="[^"]*"', '<a:cs typeface="Times New Roman"', content)
                with open(fpath, 'w', encoding='utf-8') as tf:
                    tf.write(content)
                print(f"Patched theme: {f}")

    # 2. Update slide XMLs, layout XMLs, master XMLs
    slide_dirs = [
        os.path.join(temp_dir, 'ppt', 'slides'),
        os.path.join(temp_dir, 'ppt', 'slideLayouts'),
        os.path.join(temp_dir, 'ppt', 'slideMasters'),
        os.path.join(temp_dir, 'ppt', 'notesSlides'),
    ]
    
    count_patched = 0
    for sdir in slide_dirs:
        if not os.path.exists(sdir):
            continue
        for f in os.listdir(sdir):
            if f.endswith('.xml'):
                fpath = os.path.join(sdir, f)
                with open(fpath, 'r', encoding='utf-8') as sf:
                    content = sf.read()
                
                orig = content
                # Replace theme token references
                content = content.replace('typeface="+mn-lt"', 'typeface="Times New Roman"')
                content = content.replace('typeface="+mj-lt"', 'typeface="Times New Roman"')
                
                # Also ensure any <a:rPr> that has font attributes gets Times New Roman
                # In DrawingML, <a:rPr sz="1800" ...><a:latin typeface="Times New Roman"/></a:rPr>
                if content != orig:
                    with open(fpath, 'w', encoding='utf-8') as sf:
                        sf.write(content)
                    count_patched += 1

    print(f"Patched {count_patched} slide/layout/master XML files.")

    # 3. Re-pack pptx
    temp_zip = pptx_path + ".new"
    with zipfile.ZipFile(temp_zip, 'w', zipfile.ZIP_DEFLATED) as zip_out:
        for root, dirs, files in os.walk(temp_dir):
            for f in files:
                full_path = os.path.join(root, f)
                rel_path = os.path.relpath(full_path, temp_dir)
                zip_out.write(full_path, rel_path)

    shutil.rmtree(temp_dir)
    os.replace(temp_zip, pptx_path)
    print("Done! PPTX re-packed successfully.")

if __name__ == '__main__':
    target = sys.argv[1] if len(sys.argv) > 1 else 'projects/khtn6_bai11_oxygen_ppt169_20261010/exports/khtn6_bai11_oxygen_20261010_162611.pptx'
    patch_pptx(target)
