import sys, os, json
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as patches

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

# Ensure fonts support Vietnamese
plt.rcParams['font.sans-serif'] = ['Segoe UI', 'Arial', 'DejaVu Sans', 'Tahoma']
plt.rcParams['axes.unicode_minus'] = False

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "references" / "default_matrices.json"
OUT_DIR = BASE_DIR / "references" / "matrix_previews"
OUT_DIR.mkdir(parents=True, exist_ok=True)

if not DB_PATH.exists():
    print(f"Không tìm thấy: {DB_PATH}")
    sys.exit(1)

matrices = json.loads(DB_PATH.read_text(encoding='utf-8'))

SUBJECT_COLORS = {
    "math": {"primary": "#1A5276", "accent": "#2980B9", "bg": "#EBF5FB", "badge": "#D4E6F1"},
    "physics": {"primary": "#7D3C98", "accent": "#8E44AD", "bg": "#F4ECF7", "badge": "#E8DAEF"},
    "chemistry": {"primary": "#117864", "accent": "#16A085", "bg": "#E8F8F5", "badge": "#D1F2EB"},
    "biology": {"primary": "#196F3D", "accent": "#27AE60", "bg": "#EAF2F8", "badge": "#D5F5E3"},
    "khtn": {"primary": "#B7950B", "accent": "#D4AC0D", "bg": "#FEF9E7", "badge": "#FCF3CF"},
    "geography": {"primary": "#A04000", "accent": "#BA4A00", "bg": "#FBEEE6", "badge": "#F6DDCC"},
    "literature": {"primary": "#922B21", "accent": "#C0392B", "bg": "#FDEDEC", "badge": "#FADBD8"}
}

def render_matrix_card(key, data):
    subj = data.get("subject", "math")
    color = SUBJECT_COLORS.get(subj, SUBJECT_COLORS["math"])
    title = data.get("display_name", key)
    duration = data.get("duration_minutes", 90)
    cells = data.get("cells", [])
    
    # Calculate stats
    total_nb = sum(c.get("nb", 0) for c in cells)
    total_th = sum(c.get("th", 0) for c in cells)
    total_vd = sum(c.get("vd", 0) for c in cells)
    total_vdc = sum(c.get("vdc", 0) for c in cells)
    total_q = total_nb + total_th + total_vd + total_vdc
    
    fig = plt.figure(figsize=(10, 6.2), dpi=200)
    ax = fig.add_subplot(111)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')
    
    # Card Background
    card_bg = patches.FancyBboxPatch((1, 1), 98, 98, boxstyle="round,pad=1,rounding_size=3",
                                     facecolor="#FFFFFF", edgecolor=color["primary"], linewidth=2.5)
    ax.add_patch(card_bg)
    
    # Header Banner
    header = patches.FancyBboxPatch((1.5, 84), 97, 14.5, boxstyle="round,pad=0.5,rounding_size=2",
                                    facecolor=color["primary"], edgecolor="none")
    ax.add_patch(header)
    
    # Header text
    ax.text(50, 93, f"MA TRẬN ĐẶC TẢ ĐỀ KIỂM TRA CHUẨN GDPT 2018", 
            ha='center', va='center', fontsize=12.5, fontweight='bold', color="#FFFFFF")
    ax.text(50, 87.5, f"-  {title.upper()}  -  THỜI GIAN: {duration} PHÚT", 
            ha='center', va='center', fontsize=11, fontweight='bold', color="#F9E79F")
    
    # Top Stats Boxes (4 levels: NB, TH, VD, VDC)
    stats_data = [
        ("NHẬN BIẾT", total_nb, "30-40%", "#2E86C1"),
        ("THÔNG HIỂU", total_th, "30-40%", "#28B463"),
        ("VẬN DỤNG", total_vd, "20%", "#D35400"),
        ("VẬN DỤNG CAO", total_vdc, "10%", "#C0392B")
    ]
    
    box_w = 21.5
    for i, (lvl_name, cnt, pct, c_lvl) in enumerate(stats_data):
        bx = 4 + i * 23.5
        box = patches.FancyBboxPatch((bx, 71), box_w, 10.5, boxstyle="round,pad=0.5,rounding_size=1.5",
                                     facecolor="#F8F9F9", edgecolor=c_lvl, linewidth=1.5)
        ax.add_patch(box)
        ax.text(bx + box_w/2, 78.5, lvl_name, ha='center', va='center', fontsize=8.5, fontweight='bold', color=c_lvl)
        ax.text(bx + box_w/2, 74, f"{cnt} ý/câu ({pct})", ha='center', va='center', fontsize=9, fontweight='bold', color="#2C3E50")
        
    # Content Breakdown Table Header
    th_bg = patches.Rectangle((4, 63.5), 92, 5.5, facecolor=color["accent"], edgecolor="none")
    ax.add_patch(th_bg)
    ax.text(6, 66.2, "TT", ha='left', va='center', fontsize=8.5, fontweight='bold', color="#FFFFFF")
    ax.text(12, 66.2, "CHỦ ĐỀ KIẾN THỨC", ha='left', va='center', fontsize=8.5, fontweight='bold', color="#FFFFFF")
    ax.text(58, 66.2, "DẠNG THỨC ĐỀ", ha='left', va='center', fontsize=8.5, fontweight='bold', color="#FFFFFF")
    ax.text(78, 66.2, "NB - TH - VD - VDC", ha='center', va='center', fontsize=8.5, fontweight='bold', color="#FFFFFF")
    ax.text(91.5, 66.2, "TỔNG", ha='center', va='center', fontsize=8.5, fontweight='bold', color="#FFFFFF")
    
    # Render Rows (max 8 rows displayed, summary at bottom)
    disp_cells = cells[:8]
    y_start = 58
    row_h = 5.2
    
    for idx, cell in enumerate(disp_cells):
        y = y_start - idx * row_h
        row_bg_color = color["bg"] if idx % 2 == 0 else "#FFFFFF"
        row_box = patches.Rectangle((4, y - row_h/2), 92, row_h, facecolor=row_bg_color, edgecolor="#BDC3C7", linewidth=0.5)
        ax.add_patch(row_box)
        
        c_nb = cell.get("nb", 0)
        c_th = cell.get("th", 0)
        c_vd = cell.get("vd", 0)
        c_vdc = cell.get("vdc", 0)
        c_tot = c_nb + c_th + c_vd + c_vdc
        part_name = cell.get("part", "")
        if part_name == "part1_mc":
            part_str = "Phần I (Trắc nghiệm 4 LC)"
        elif part_name == "part2_tf":
            part_str = "Phần II (Đúng / Sai 4 ý)"
        elif part_name == "part3_sa":
            part_str = "Phần III (Trả lời ngắn)"
        elif part_name == "essay":
            part_str = "Tự luận chuyên sâu"
        else:
            part_str = "Đặc tả tổng hợp"
            
        topic_disp = cell.get("topic_display", cell.get("topic", ""))
        
        ax.text(6, y, f"{idx+1}", ha='left', va='center', fontsize=8, color="#2C3E50")
        ax.text(12, y, topic_disp[:26], ha='left', va='center', fontsize=8, fontweight='bold', color="#2C3E50")
        ax.text(58, y, part_str, ha='left', va='center', fontsize=7.5, color="#566573")
        ax.text(78, y, f"{c_nb}  -  {c_th}  -  {c_vd}  -  {c_vdc}", ha='center', va='center', fontsize=8, color="#2C3E50")
        ax.text(91.5, y, f"{c_tot}", ha='center', va='center', fontsize=8.5, fontweight='bold', color=color["primary"])
        
    # Footer Notice
    footer_y = 11
    rem_cells = len(cells) - len(disp_cells)
    if rem_cells > 0:
        ax.text(50, footer_y + 3.5, f"... Và {rem_cells} chủ đề đặc tả chi tiết khác bám sát chương trình SGK mới", 
                ha='center', va='center', fontsize=8, fontstyle='italic', color="#7F8C8D")
        
    bot_box = patches.FancyBboxPatch((4, 3.5), 92, 6.5, boxstyle="round,pad=0.5,rounding_size=1",
                                     facecolor=color["badge"], edgecolor=color["accent"], linewidth=1)
    ax.add_patch(bot_box)
    ax.text(50, 6.7, f"[OK] Chuẩn hóa 100% Bộ GD&ĐT 2025-2026 | Tự động xuất Word MathType OLE 14pt click đúp sửa ngay", 
            ha='center', va='center', fontsize=8.5, fontweight='bold', color=color["primary"])
            
    out_file = OUT_DIR / f"{key}.png"
    plt.tight_layout()
    plt.savefig(out_file, dpi=200, bbox_inches='tight')
    plt.close(fig)
    print(f"[OK] Đã tạo ảnh: {out_file.name}")
    return out_file

def render_catalog_poster():
    """Tạo 1 Poster Tổng Quan hiển thị cả 8 Ma Trận để GV nhìn vào là chọn được ngay."""
    fig = plt.figure(figsize=(14, 9.5), dpi=200)
    ax = fig.add_subplot(111)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')
    
    # Outer Background
    bg = patches.Rectangle((0, 0), 100, 100, facecolor="#F4F6F7", edgecolor="none")
    ax.add_patch(bg)
    
    # Big Header Banner
    h_box = patches.FancyBboxPatch((2, 87), 96, 11, boxstyle="round,pad=0.5,rounding_size=2",
                                   facecolor="#1B2631", edgecolor="#F39C12", linewidth=2)
    ax.add_patch(h_box)
    ax.text(50, 94.5, "DANH MỤC 8 BỘ MA TRẬN ĐỀ KIỂM TRA CHUẨN BỘ GD&ĐT", 
            ha='center', va='center', fontsize=16, fontweight='bold', color="#FFFFFF")
    ax.text(50, 89.8, "Tích hợp sẵn trong Phần mềm Tạo Đề – Định dạng GDPT 2018 (Phần I, II, III chuẩn mực)", 
            ha='center', va='center', fontsize=11, color="#FAD7A0")
            
    # 8 Cards arranged in 2 columns x 4 rows
    col_w = 46.5
    row_h = 17.5
    keys = [k for k in matrices.keys() if not k.startswith('_')]
    
    for i, k in enumerate(keys[:8]):
        data = matrices[k]
        subj = data.get("subject", "math")
        col_idx = i % 2
        row_idx = i // 2
        
        x0 = 2.5 + col_idx * 48.5
        y0 = 68 - row_idx * 19.5
        
        c = SUBJECT_COLORS.get(subj, SUBJECT_COLORS["math"])
        
        # Mini Card
        c_box = patches.FancyBboxPatch((x0, y0), col_w, row_h, boxstyle="round,pad=0.5,rounding_size=2",
                                       facecolor="#FFFFFF", edgecolor=c["primary"], linewidth=1.8)
        ax.add_patch(c_box)
        
        # Mini Card Header
        ch_box = patches.FancyBboxPatch((x0 + 0.3, y0 + row_h - 4.5), col_w - 0.6, 4.3, 
                                        boxstyle="round,pad=0.2,rounding_size=1.5",
                                        facecolor=c["primary"], edgecolor="none")
        ax.add_patch(ch_box)
        
        ax.text(x0 + 2, y0 + row_h - 2.3, f"#{i+1}. {data.get('display_name', k)}", 
                ha='left', va='center', fontsize=10.5, fontweight='bold', color="#FFFFFF")
                
        # Card Body details
        cells = data.get("cells", [])
        total_q = sum(c.get("nb", 0) + c.get("th", 0) + c.get("vd", 0) + c.get("vdc", 0) for c in cells)
        
        ax.text(x0 + 2.5, y0 + 10, f"• Cấu trúc: 3 Phần chuẩn (TN 4 lựa chọn, Đúng/Sai, Trả lời ngắn)", 
                ha='left', va='center', fontsize=8, color="#2C3E50")
        ax.text(x0 + 2.5, y0 + 7, f"• Thời gian: {data.get('duration_minutes', 90)} phút | Số câu hỏi/ý đặc tả: {total_q}", 
                ha='left', va='center', fontsize=8, color="#2C3E50")
        ax.text(x0 + 2.5, y0 + 4, f"• Tỉ lệ điểm: 30% Nhận biết – 40% Thông hiểu – 20% VD – 10% VDC", 
                ha='left', va='center', fontsize=8, color="#566573")
        
        # Badge
        badge = patches.FancyBboxPatch((x0 + col_w - 14, y0 + 1.2), 12.5, 2.5, boxstyle="round,pad=0.2,rounding_size=0.8",
                                       facecolor=c["badge"], edgecolor=c["accent"], linewidth=0.8)
        ax.add_patch(badge)
        ax.text(x0 + col_w - 7.7, y0 + 2.45, "Sẵn sàng tạo đề", 
                ha='center', va='center', fontsize=7, fontweight='bold', color=c["primary"])

    # Bottom notice
    bot_b = patches.FancyBboxPatch((2, 1.5), 96, 4.5, boxstyle="round,pad=0.3,rounding_size=1",
                                   facecolor="#EAEDED", edgecolor="#BDC3C7", linewidth=1)
    ax.add_patch(bot_b)
    ax.text(50, 3.7, "👉 Thầy/Cô chỉ cần gõ: \"Tạo đề [Tên môn] [Lớp] theo ma trận\" là phần mềm tự động xuất đề chuẩn 100%!", 
            ha='center', va='center', fontsize=9.5, fontweight='bold', color="#1B2631")

    poster_file = OUT_DIR / "DANH_MUC_8_MA_TRAN_CHUAN.png"
    plt.tight_layout()
    plt.savefig(poster_file, dpi=200, bbox_inches='tight')
    plt.close(fig)
    print(f"[OK] Đã tạo Poster Danh mục: {poster_file.name}")
    return poster_file

if __name__ == "__main__":
    print("[*] Đang kết xuất hình ảnh ma trận đặc tả...")
    for k, v in matrices.items():
        if not k.startswith("_"):
            render_matrix_card(k, v)
    render_catalog_poster()
    print("🎉 Hoàn tất kết xuất toàn bộ hình ảnh ma trận!")
