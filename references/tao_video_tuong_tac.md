# 🎬 HƯỚNG DẪN TẠO VIDEO TƯƠNG TÁC E-LEARNING (CHỐNG TUA NHANH + CÂU HỎI NHÚNG + GOOGLE SHEETS SYNC)

---

## 📌 GIỚI THIỆU TÍNH NĂNG

**Video Tương Tác E-Learning** là một file HTML độc lập (single-file, không cần server riêng) cho phép giáo viên:

| Tính năng | Mô tả |
|-----------|-------|
| 🔒 **Chống tua nhanh** | Học sinh không thể skip — video tự snap back khi cố tua |
| ❓ **Câu hỏi nhúng** | Video tự dừng tại các mốc định sẵn, hiện câu hỏi tương tác |
| ✅ **Phản hồi 1-chạm** | Bấm vào đáp án → ngay lập tức đổi màu + âm thanh (không cần nút Submit) |
| 📊 **Google Sheets Sync** | Điểm và trạng thái học sinh ghi vào Sheets thời gian thực |
| 🌐 **Deploy miễn phí** | Đưa lên Netlify (miễn phí, không cần hosting trả phí) |
| 📱 **Responsive** | Hoạt động trên điện thoại, máy tính bảng, laptop |

---

## 🔑 TỪ KHÓA KÍCH HOẠT

Khi giáo viên nói một trong các câu sau, agent hiểu cần thực hiện tính năng này:

- *"tôi muốn tạo video tương tác"*
- *"làm video có câu hỏi tương tác"*
- *"video chống tua nhanh cho học sinh"*
- *"tạo video e-learning"*
- *"video tích hợp câu hỏi"*
- *"làm video học sinh không tua được"*
- *"tạo interactive video"*
- *"video dừng hỏi câu hỏi"*
- *"video ghi điểm vào google sheet"*

---

## 📋 CÁC CÂU LỆNH MẪU CHO GIÁO VIÊN (COPY-PASTE NGAY)

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📌 CÂU LỆNH MẪU TẠO VIDEO TƯƠNG TÁC E-LEARNING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🟢 CÂU LỆNH 1 — Tạo nhanh từ video YouTube có sẵn:
   "Em hãy tạo video tương tác e-learning cho Bài [tên bài], [môn] lớp [X].
    Link YouTube: [https://youtu.be/VIDEO_ID]
    Link Google Sheets: [https://docs.google.com/spreadsheets/d/SHEET_ID/edit]
    Bài có [N] câu hỏi tương tác, học sinh không tua nhanh được.
    Kết quả học sinh tự động ghi vào Google Sheets của thầy/cô."

🟢 CÂU LỆNH 2 — Tạo với danh sách câu hỏi cụ thể:
   "Em hãy tạo video tương tác cho video YouTube [VIDEO_ID].
    Các câu hỏi như sau (thầy/cô sẽ ghi rõ từng câu):
    - Câu 1 (tại phút 3:10): [nội dung câu hỏi trắc nghiệm A/B/C/D]
    - Câu 2 (tại phút 5:00): [câu hỏi đúng/sai]
    - Câu 3 (tại phút 7:25): [điền số, đáp án = 7]
    Đồng bộ Google Sheets: [link sheets] và đưa lên Netlify giúp thầy/cô."

🟢 CÂU LỆNH 3 — Cập nhật bài đã có, thêm câu hỏi mới:
   "Em hãy thêm 2 câu hỏi mới vào video tương tác [tên bài] đã làm:
    - Câu mới 1 (tại phút 8:00): Câu trắc nghiệm — [nội dung]
    - Câu mới 2 (tại phút 9:30): Câu điền số — đáp án = [N]"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## ⚙️ LUỒNG LÀM VIỆC (WORKFLOW) — 5 BƯỚC

### Bước 0: Thu thập thông tin từ giáo viên

Agent hỏi GV (nếu chưa có) những thông tin sau:

| Thông tin cần | Ví dụ |
|---------------|-------|
| Tên bài học | Bài 6: Lũy thừa với số mũ tự nhiên |
| Môn + Lớp | Toán 6, SGK Kết nối tri thức |
| Link YouTube | `https://youtu.be/EaYtq5u1Wzw` → VIDEO_ID = `EaYtq5u1Wzw` |
| Link Google Sheets | `https://docs.google.com/spreadsheets/d/1ZYZ.../edit` → SHEET_ID = `1ZYZ...` |
| Số câu hỏi & thời điểm | 7 câu, tại các phút: 3:10, 4:15, 7:25, 8:50, 10:00, 11:35, 13:15 |
| Nội dung từng câu hỏi | GV cung cấp, hoặc agent đề xuất dựa trên nội dung bài |

---

### Bước 1: GV tạo Google Apps Script → lấy Web App URL

**Agent hướng dẫn GV từng bước:**

1. Mở Google Sheets → `Tiện ích mở rộng` → `Apps Script`
2. Xóa code mặc định, dán đoạn code Apps Script sau:

```javascript
// ============================================================
// APPS SCRIPT V4 — PHÂN LỚP TỰ ĐỘNG + THỐNG KÊ TỪNG LỚP
// ✅ Lớp mới → tự tạo tab  ✅ 1 HS = 1 dòng  ✅ Thống kê tự cập nhật
// ============================================================

const SUMMARY_SHEET = '📊 Tổng hợp';
const CLASS_PREFIX  = '';          // '' → tab "6A" | 'Lớp ' → tab "Lớp 6A"
const STAT_ROW      = 1;           // Dòng thống kê (dòng 1)
const STAT_ROW2     = 2;           // Dòng thống kê phụ (dòng 2)
const HEADER_ROW    = 3;           // Dòng header bắt đầu từ dòng 3
const DATA_START    = 4;           // Dữ liệu HS từ dòng 4

const CLASS_COLORS = [
  '#1B4F72','#145A32','#6E2F8C','#784212',
  '#1A5276','#0E6655','#922B21','#154360',
  '#4A235A','#1B2631'
];

// ── Hàm chính nhận POST từ video tương tác ──────────────────
function doPost(e) {
  const lock = LockService.getScriptLock();
  try { lock.waitLock(10000); }
  catch (err) { return ok({status:'busy'}); }

  try {
    const d     = JSON.parse(e.postData.contents);
    const name  = String(d.studentName  || '').trim();
    const cls   = String(d.studentClass || '').trim().toUpperCase();
    if (!name || !cls) return ok({status:'skip'});

    const score  = Number(d.score)          || 0;
    const total  = Number(d.totalQuestions) || 7;
    const pct    = total > 0 ? Math.round(score/total*100) : 0;
    const ts     = d.timestamp || new Date().toLocaleString('vi-VN');
    const status = d.status   || '🟡 Đang học';
    const detail = d.details  || '';

    // 1. Cập nhật sheet lớp
    const classSheet = getOrMakeClassSheet_(CLASS_PREFIX + cls);
    upsertStudent_(classSheet, name, [ts, name, score, total, pct+'%', status, detail], false);
    updateClassStats_(classSheet, cls, total);

    // 2. Cập nhật sheet Tổng hợp
    const sumSheet = getOrMakeSummarySheet_();
    upsertStudent_(sumSheet, name+'§'+cls, [ts, name, cls, score, total, pct+'%', status, detail], true);
    updateSummaryStats_(sumSheet, total);

    return ok({status:'success', class: CLASS_PREFIX+cls});
  } catch(err) {
    return ok({status:'error', msg: err.toString()});
  } finally {
    lock.releaseLock();
  }
}

// ── Upsert 1 học sinh (1 dòng duy nhất) ─────────────────────
function upsertStudent_(sheet, uniqueKey, rowValues, isSummary) {
  const lastRow = sheet.getLastRow();
  const keyColIdx = isSummary ? 10 : 9;

  let foundRow = -1;
  if (lastRow >= DATA_START) {
    const keys = sheet.getRange(DATA_START, keyColIdx, lastRow - DATA_START + 1, 1).getValues();
    for (let i = keys.length - 1; i >= 0; i--) {
      if (String(keys[i][0]).trim() === uniqueKey) {
        foundRow = i + DATA_START; break;
      }
    }
  }

  const stt = foundRow > 0
    ? sheet.getRange(foundRow, 1).getValue()
    : Math.max(0, lastRow - HEADER_ROW) + 1;

  const fullRow = [stt].concat(rowValues).concat([uniqueKey]);

  if (foundRow > 0) {
    sheet.getRange(foundRow, 1, 1, fullRow.length).setValues([fullRow]);
    colorRowByStatus_(sheet, foundRow, rowValues[5]);
  } else {
    sheet.appendRow(fullRow);
    const newRow = sheet.getLastRow();
    colorRowByStatus_(sheet, newRow, rowValues[5]);
    hideKeyColumn_(sheet, isSummary);
  }
}

function colorRowByStatus_(sheet, rowNum, status) {
  const col = sheet.getLastColumn();
  const rng = sheet.getRange(rowNum, 1, 1, col - 1);
  if (String(status).includes('HOÀN THÀNH')) {
    rng.setBackground('#D5F5E3');
  } else if (String(status).includes('Đang học')) {
    rng.setBackground('#FEF9E7');
  } else {
    rng.setBackground('#FFFFFF');
  }
}

function updateClassStats_(sheet, className, total) {
  const lastRow = sheet.getLastRow();
  if (lastRow < DATA_START) {
    writeStatPlaceholder_(sheet, className);
    return;
  }

  const numStudents  = lastRow - HEADER_ROW;
  const dataRange    = sheet.getRange(DATA_START, 1, numStudents, 8);
  const data         = dataRange.getValues();

  let sumScore = 0, countDone = 0, countInProgress = 0;
  data.forEach(row => {
    const score  = Number(row[3]) || 0;
    const status = String(row[6] || '');
    sumScore += score;
    if (status.includes('HOÀN THÀNH')) countDone++;
    else if (status.includes('Đang học') || status.includes('Vừa vào')) countInProgress++;
  });

  const avgScore = numStudents > 0 ? (sumScore / numStudents).toFixed(1) : 0;
  const avgPct   = total > 0 ? Math.round(sumScore / numStudents / total * 100) : 0;

  const statCell1 = sheet.getRange(STAT_ROW, 1, 1, 8);
  statCell1.merge();
  statCell1.setValue(`📊 THỐNG KÊ LỚP ${className}  —  Cập nhật: ${new Date().toLocaleTimeString('vi-VN')}`);
  statCell1.setBackground('#1B4F72');
  statCell1.setFontColor('#FFFFFF');
  statCell1.setFontWeight('bold');
  statCell1.setFontSize(11);
  statCell1.setHorizontalAlignment('center');

  const statCell2 = sheet.getRange(STAT_ROW2, 1, 1, 8);
  statCell2.merge();
  statCell2.setValue(
    `👥 Sĩ số đã vào học: ${numStudents}  |  ` +
    `✅ Hoàn thành: ${countDone} (${numStudents>0?Math.round(countDone/numStudents*100):0}%)  |  ` +
    `🟡 Đang học: ${countInProgress}  |  ` +
    `⭐ Điểm TB: ${avgScore}/${total} (${avgPct}%)`
  );
  statCell2.setBackground('#D6EAF8');
  statCell2.setFontColor('#1A5276');
  statCell2.setFontWeight('bold');
  statCell2.setFontSize(10);
  statCell2.setHorizontalAlignment('center');
}

function updateSummaryStats_(sheet, total) {
  const lastRow = sheet.getLastRow();
  if (lastRow < DATA_START) return;

  const numStudents = lastRow - HEADER_ROW;
  const data        = sheet.getRange(DATA_START, 1, numStudents, 9).getValues();

  const classStat = {};
  let totalDone = 0;
  data.forEach(row => {
    const cls    = String(row[3] || '');
    const status = String(row[7] || '');
    if (!classStat[cls]) classStat[cls] = { count:0, done:0 };
    classStat[cls].count++;
    if (status.includes('HOÀN THÀNH')) { classStat[cls].done++; totalDone++; }
  });

  const clsList = Object.entries(classStat)
    .sort((a,b) => a[0].localeCompare(b[0]))
    .map(([cls, s]) => `${cls}: ${s.count} HS (${s.done} xong)`)
    .join('   |   ');

  const statCell1 = sheet.getRange(STAT_ROW, 1, 1, 10);
  statCell1.merge();
  statCell1.setValue(`📊 TỔNG HỢP TẤT CẢ LỚP  —  Cập nhật: ${new Date().toLocaleTimeString('vi-VN')}`);
  statCell1.setBackground('#784212');
  statCell1.setFontColor('#FFFFFF');
  statCell1.setFontWeight('bold');
  statCell1.setFontSize(11);
  statCell1.setHorizontalAlignment('center');

  const statCell2 = sheet.getRange(STAT_ROW2, 1, 1, 10);
  statCell2.merge();
  statCell2.setValue(`👥 Tổng: ${numStudents} HS  |  ✅ Hoàn thành: ${totalDone}  |  ${clsList}`);
  statCell2.setBackground('#FDEBD0');
  statCell2.setFontColor('#784212');
  statCell2.setFontWeight('bold');
  statCell2.setFontSize(10);
  statCell2.setHorizontalAlignment('center');
}

function writeStatPlaceholder_(sheet, className) {
  const r1 = sheet.getRange(STAT_ROW, 1, 1, 8);
  r1.merge();
  r1.setValue(`📊 THỐNG KÊ LỚP ${className} — Chưa có học sinh`);
  r1.setBackground('#1B4F72'); r1.setFontColor('#FFFFFF'); r1.setFontWeight('bold');
  r1.setHorizontalAlignment('center');
}

function getOrMakeClassSheet_(sheetName) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let sh   = ss.getSheetByName(sheetName);
  if (sh) return sh;

  sh = ss.insertSheet(sheetName);
  const idx   = ss.getSheets().length - 1;
  const color = CLASS_COLORS[idx % CLASS_COLORS.length];
  sh.setTabColor(color);

  sh.getRange(STAT_ROW,  1, 1, 8).merge();
  sh.getRange(STAT_ROW2, 1, 1, 8).merge();

  sh.getRange(HEADER_ROW, 1, 1, 9).setValues([[
    'STT','Thời gian','Họ và tên','Điểm','Tổng câu','%','Trạng thái','Chi tiết','_key'
  ]]);
  const hdr = sh.getRange(HEADER_ROW, 1, 1, 9);
  hdr.setBackground(color); hdr.setFontColor('#FFF'); hdr.setFontWeight('bold');
  hdr.setHorizontalAlignment('center');
  sh.setFrozenRows(HEADER_ROW);

  [45,135,160,55,65,60,170,200].forEach((w,i) => sh.setColumnWidth(i+1, w));
  sh.hideColumns(9);
  return sh;
}

function getOrMakeSummarySheet_() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let sh   = ss.getSheetByName(SUMMARY_SHEET);
  if (sh) return sh;

  sh = ss.insertSheet(SUMMARY_SHEET, 0);
  sh.setTabColor('#F39C12');
  sh.getRange(STAT_ROW,  1, 1, 10).merge();
  sh.getRange(STAT_ROW2, 1, 1, 10).merge();
  sh.getRange(HEADER_ROW, 1, 1, 10).setValues([[
    'STT','Thời gian','Họ và tên','Lớp','Điểm','Tổng câu','%','Trạng thái','Chi tiết','_key'
  ]]);
  const hdr = sh.getRange(HEADER_ROW, 1, 1, 10);
  hdr.setBackground('#784212'); hdr.setFontColor('#FFF'); hdr.setFontWeight('bold');
  hdr.setHorizontalAlignment('center');
  sh.setFrozenRows(HEADER_ROW);
  [45,135,165,60,55,65,60,170,200].forEach((w,i) => sh.setColumnWidth(i+1, w));
  sh.hideColumns(10);
  return sh;
}

function hideKeyColumn_(sheet, isSummary) {
  try { sheet.hideColumns(isSummary ? 10 : 9); } catch(e) {}
}

function ok(obj) {
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}

function doGet() {
  return ok({status:'ok', version:'V4-ClassStats'});
}
```

3. Nhấn **Triển khai** → **Triển khai mới** → **Ứng dụng web**
   - Ai có quyền truy cập: **Mọi người** (Anyone)
   - Nhấn **Triển khai** → Copy URL Web App
4. Gửi URL Web App cho agent (dạng: `https://script.google.com/macros/s/AKfycbw.../exec`)

> **Lưu ý quan trọng:** Mỗi lần sửa code Apps Script, phải tạo **phiên bản mới** (`Triển khai` → `Quản lý triển khai` → Chỉnh sửa → Phiên bản mới) thì thay đổi mới có hiệu lực!

---

### Bước 2: Agent tạo file HTML hoàn chỉnh

Agent dựa vào template bên dưới, thay thế các placeholder:

| Placeholder | Giá trị cần thay |
|-------------|-----------------|
| `YOUTUBE_VIDEO_ID` | ID video YouTube (ví dụ: `EaYtq5u1Wzw`) |
| `SCRIPT_WEB_APP_URL` | URL Apps Script Web App |
| `TÊN BÀI HỌC` | Tên bài đầy đủ (ví dụ: `Lũy Thừa Với Số Mũ Tự Nhiên - Toán 6`) |
| `TÊN GIÁO VIÊN` | Tên GV (ví dụ: `GV: Nguyễn Thiện (THCS Ứng Hòe)`) |
| `checkpoints[]` | Mảng câu hỏi theo cú pháp quy định (xem bên dưới) |
| `TỔNG_SỐ_CÂU` | Số nguyên (ví dụ: `7`) |
| `localStorage_KEY` | Key lưu local (ví dụ: `nls_toan6`) |

---

### Bước 3: Deploy lên Netlify

**⚠️ LỖI HAY GẶP:** Netlify KHÔNG nhận file lẻ — phải drag **THƯ MỤC** chứa file `index.html`.

**Cách đúng:**
1. Tạo thư mục mới (ví dụ: `Video_Toan6_Bai6`)
2. Đặt file HTML vào thư mục, **đổi tên thành `index.html`**
3. Truy cập [app.netlify.com](https://app.netlify.com) → `Sites` → `Add new site` → `Deploy manually`
4. Kéo thả **CẢ THƯ MỤC** `Video_Toan6_Bai6` vào ô deploy
5. Netlify tự tạo link dạng: `https://ten-ngau-nhien.netlify.app`
6. Tùy chỉnh tên: `Site configuration` → `Change site name` (ví dụ: `toan-6-luy-thua`)

> 💡 **Mẹo:** Lần cập nhật sau, kéo thả lại thư mục vào site cũ để **overwrite** (không mất link cũ).

---

## 🗂️ CẤU TRÚC `checkpoints[]` — CÚ PHÁP KHAI BÁO CÂU HỎI

### Dạng 1: Trắc nghiệm MCQ (Multiple Choice)

```javascript
{
  id: 1,
  time: 190,          // Thời điểm dừng (giây). Ví dụ: 3 phút 10 giây = 190
  type: 'mcq',
  question: 'Nội dung câu hỏi...',
  options: [
    'A. Phương án A',
    'B. Phương án B',
    'C. Phương án C',
    'D. Phương án D'
  ],
  correct: 1,          // Index đáp án đúng (0=A, 1=B, 2=C, 3=D)
  explanation: 'Giải thích chi tiết tại sao đáp án đúng...'
}
```

### Dạng 2: Đúng/Sai (True/False)

```javascript
{
  id: 4,
  time: 530,
  type: 'tf',
  question: 'Khẳng định sau ĐÚNG hay SAI: "..."',
  correct: false,      // true = ĐÚNG, false = SAI
  explanation: 'Giải thích...'
}
```

### Dạng 3: Điền số (Fill-in-the-Blank)

```javascript
{
  id: 3,
  time: 445,
  type: 'fill',
  question: 'Nội dung câu hỏi... Em hãy điền kết quả vào ô dưới đây:',
  correct: '7',        // Đáp án là chuỗi string (so sánh sau khi trim)
  explanation: 'Giải thích...'
}
```

> **Lưu ý:** `inputmode="numeric"` được tự động thêm vào ô nhập — bàn phím số tự bật trên điện thoại.
> Học sinh nhấn **Enter** hoặc bấm nút **"Kiểm tra →"** để nộp.

### Dạng 4 (Dành cho bài tiếp theo): Kéo thả / Chạm thẻ số

**Thiết kế dự kiến** (chưa implement trong bài này — dành cho bài tiếp theo):

```javascript
{
  id: 3,
  time: 445,
  type: 'drag',        // Dạng kéo thả
  question: 'Kéo thẻ số vào ô trống: 2³ × 2⁴ = 2[__]',
  tiles: ['5', '6', '7', '8', '12'],  // Các thẻ số hiện ra
  correct: '7',
  explanation: 'Giải thích...'
}
```

*Khi implement: Dùng HTML5 Drag & Drop API + touch events cho mobile (touchstart/touchmove/touchend), highlight vùng drop khi kéo qua, âm thanh snap khi thả đúng.*

---

## 🎯 CÁC TÍNH NĂNG KỸ THUẬT QUAN TRỌNG

### F. Chế Độ Thầy Cô (Teacher Preview Mode)

- Mặc định: Học sinh bị khóa tua nhanh 100%.
- Thầy/Cô bấm vào nút **"⚙️ Cài đặt Thầy Cô"** trên góc phải $\to$ Nhập mật khẩu bí mật (mặc định: `123456`).
- Khi mở khóa thành công:
  - Thanh tiến độ mở khóa hoàn toàn: Thầy Cô có thể click hoặc kéo tua đến bất kỳ giây nào.
  - Xuất hiện danh sách các nút **[Trạm 1: 03:10] [Trạm 2: 04:15]...** để bấm vào là video nhảy ngay đến đúng trạm và bật câu hỏi kiểm tra lập tức!
  - Bấm nút **"🔒 Tắt Chế độ Thầy Cô"** để khóa lại như học sinh.

### G. Tự Động Bảo Lưu Tiến Độ (Smart Auto-Resume)

- Tự động ghi nhớ tiến độ học sinh vào `localStorage` (`nls_toan6_saved_progress`) theo thời gian thực (vị trí giây xem, trạm đã giải, điểm số).
- Nếu học sinh vô tình bị rớt mạng, hết pin, reload trang hoặc tắt trình duyệt:
  - Khi mở lại, hệ thống hiển thị bảng thông báo: *"Chào em [Tên], em có muốn tiếp tục học từ vị trí [mm:ss] không?"*
  - Bấm **"TIẾP TỤC HỌC ▶️"**: Nhảy ngay đến vị trí đang học dở, giữ nguyên điểm số và các trạm đã giải.
  - Bấm **"Học lại từ đầu 🔄"**: Bắt đầu lại từ đầu bài.


### A. Chống tua nhanh 100% (Anti-Skip System)

```javascript
// Theo dõi thời gian xem tối đa hợp lệ
let maxWatchedTime = 0;
const SKIP_TOLERANCE = 3; // Cho phép seek tối đa 3 giây phía trước

setInterval(() => {
  const current = PlayerEngine.getCurrentTime();
  if (current > maxWatchedTime + SKIP_TOLERANCE) {
    // Học sinh cố tua — snap back
    PlayerEngine.seekTo(maxWatchedTime);
    AudioFX.playWarning();
    // Hiện cảnh báo...
  }
  if (!activeCheckpoint) {
    maxWatchedTime = Math.max(maxWatchedTime, current);
  }
}, 250); // Poll mỗi 250ms
```

**Lớp bảo vệ bổ sung:**
- YouTube `controls: 0` + `disablekb: 1` — ẩn toàn bộ controls YouTube
- CSS overlay `pointer-events: none` bao phủ vùng video — chặn click vào progress bar
- `user-select: none` toàn trang — chặn inspect/copy

### B. Dual-Engine (File:// + HTTPS)

**Vấn đề:** YouTube Embed lỗi 153 khi mở từ `file://` protocol (thiếu HTTP Referer).

**Giải pháp — Dual-Engine:**
```javascript
const isFileProtocol = window.location.protocol === 'file:';

const PlayerEngine = {
  init() {
    if (isFileProtocol) {
      // Dùng video MP4 local
      setupLocalVideoPlayer();
    } else {
      // Dùng YouTube IFrame API
      setupYouTubePlayer();
    }
  }
};
```

→ Khi GV mở từ máy tính (file://): dùng MP4 local.  
→ Khi HS mở từ Netlify (https://): dùng YouTube.

### C. Audio FX (Web Audio API — không cần file âm thanh)

```javascript
const AudioFX = {
  // Âm chúc mừng (đúng)
  playSuccess() { /* Chord C→E→G bằng oscillator */ },
  // Âm sai (tiếng rè giảm dần)
  playWrong() { /* Sawtooth 220Hz→140Hz */ },
  // Âm cảnh báo (tua nhanh)
  playWarning() { /* Square wave 350→280Hz */ }
};
```

### D. Phản hồi 1-Chạm (Instant Feedback — không cần Submit)

**Luồng MCQ/TF:**
1. HS bấm vào phương án → `handleInstantChoice(optionIndex)` gọi ngay
2. So sánh với `checkpoint.correct`
3. **Nếu đúng:** Đổi màu xanh lá (#10b981) + âm chuông + confetti mini + đếm ngược 4s tự tiếp tục
4. **Nếu sai:** Đổi màu đỏ (#ef4444) + shake animation + âm rè + hiện giải thích + nút "Xem lại 30 giây trước"

**Luồng Fill:**
1. HS nhập số → nhấn Enter hoặc bấm nút
2. So sánh sau khi trim
3. Phản hồi tương tự MCQ

### E. Google Sheets Sync

**Sync xảy ra tại 3 thời điểm:**
- Khi HS điền tên + lớp và bắt đầu (ghi trạng thái "Vừa vào lớp")
- Sau mỗi câu trả lời đúng (cập nhật điểm + trạng thái)
- Khi HS hoàn thành tất cả câu hỏi (ghi "ĐÃ HOÀN THÀNH")

**Payload gửi lên Apps Script:**
```javascript
{
  timestamp: "29/10/2026, 14:30:00",
  studentName: "Nguyễn Văn An",
  studentClass: "6C",
  score: 3,
  totalQuestions: 7,
  status: "🟡 Đang học (Đã hoàn thành Trạm 3/7)",
  lesson: "Bài 6: Lũy thừa với số mũ tự nhiên (Toán 6)",
  details: "{\"1\":{\"correct\":true,...}}"
}
```

**Dùng `mode: 'no-cors'`** — không cần CORS header phía Apps Script, nhưng không đọc được response body (dùng `.then()` riêng cho màn hình hoàn thành).

---

## 🐛 BẢNG LỖI & CÁCH SỬA

| Lỗi | Nguyên nhân | Cách sửa |
|-----|-------------|----------|
| **YouTube Error 153** | Mở từ `file://` protocol, thiếu HTTP Referer | Dùng Dual-Engine: local MP4 nếu `file://`, YouTube nếu `https://` |
| **Netlify 404 Not Found** | Upload file lẻ (tên không phải `index.html`) | Tạo thư mục + đặt file là `index.html` → kéo cả thư mục vào Netlify |
| **File HTML tiếng Việt bị lỗi** | Ghi file không đúng encoding UTF-8 | Dùng Python: `open(path, 'w', encoding='utf-8')` |
| **Apps Script không cập nhật** | Code mới chưa tạo phiên bản mới | `Triển khai → Quản lý triển khai → Sửa → Phiên bản mới → Triển khai` |
| **Học sinh tua được video** | Controls YouTube hiện ra | Kiểm tra `controls: 0, disablekb: 1` trong `playerVars` |
| **Không ghi vào Sheets** | Sai SCRIPT_WEB_APP_URL hoặc quyền truy cập Apps Script | Kiểm tra URL; đảm bảo deploy với "Mọi người" có quyền truy cập |
| **Âm thanh không phát** | Browser block autoplay audio | Bình thường — âm thanh chỉ phát sau khi HS tương tác lần đầu (Web Audio API constraint) |

---

## 📐 TEMPLATE HTML CỐT LÕI — PHẦN CẤU HÌNH (THAY THẾ)

```html
<!-- === THAY ĐỔI 3 HẰNG SỐ NÀY ============================= -->
<script>
  const SCRIPT_WEB_APP_URL = 'PASTE_URL_APPS_SCRIPT_WEB_APP_O_DAY';
  // Ví dụ: 'https://script.google.com/macros/s/AKfycbw.../exec'

  const YOUTUBE_VIDEO_ID = 'VIDEO_ID_YOUTUBE';
  // Ví dụ: 'EaYtq5u1Wzw' (lấy từ youtu.be/EaYtq5u1Wzw)

  const LOCAL_VIDEO_PATH = './ten_file_video.mp4';
  // File MP4 đặt cùng thư mục với index.html (dùng khi mở file://)

  // === THAY ĐỔI MẢng checkpoints[] ===========================
  const checkpoints = [
    // Câu 1 — Trắc nghiệm MCQ
    {
      id: 1, time: 190, type: 'mcq',
      question: 'Câu hỏi trắc nghiệm...',
      options: ['A. ...', 'B. ...', 'C. ...', 'D. ...'],
      correct: 1,  // 0=A, 1=B, 2=C, 3=D
      explanation: 'Giải thích...'
    },
    // Câu 2 — Đúng/Sai
    {
      id: 2, time: 320, type: 'tf',
      question: 'Khẳng định ĐÚNG hay SAI: "..."',
      correct: false,  // true=ĐÚNG, false=SAI
      explanation: 'Giải thích...'
    },
    // Câu 3 — Điền số
    {
      id: 3, time: 445, type: 'fill',
      question: 'Điền kết quả vào ô:',
      correct: '7',  // String, so sánh sau khi trim()
      explanation: 'Giải thích...'
    },
    // Thêm các câu tiếp theo tương tự...
  ];

  const TOTAL_QUESTIONS = checkpoints.length; // Tự động tính
  const LESSON_NAME = 'Tên bài học đầy đủ';   // Hiện trong báo cáo Sheets
  const LOCAL_STORAGE_KEY = 'nls_mon_lop';     // Key lưu tên HS (duy nhất mỗi bài)
</script>
<!-- === KẾT THÚC PHẦN CẤU HÌNH =============================== -->
```

> **📁 File HTML đầy đủ mẫu** (đã hoạt động thực tế với Toán 6 Bài 6):  
> Xem tại: `C:\Users\admin\Downloads\Video_Tuong_Tac_Toan6_YouTube_GoogleSheets.html`  
> Hoặc artifact: `Video_Tuong_Tac_Toan6_YouTube_GoogleSheets.html` trong conversation hiện tại.

---

## 📊 XEM KẾT QUẢ HỌC SINH TRÊN GOOGLE SHEETS

Giáo viên mở Google Sheets đã cung cấp → Tab `Dữ liệu học sinh`:

| Cột | Nội dung |
|-----|----------|
| A | Thời gian vào học (tự động) |
| B | Họ và tên học sinh |
| C | Lớp |
| D | Điểm (số câu đúng) |
| E | Tổng số câu |
| F | Trạng thái (`🟡 Đang học` / `🟢 ĐÃ HOÀN THÀNH`) |
| G | Tên bài học |
| H | Chi tiết từng câu (JSON) |

> 💡 **Mẹo:** Dùng **Google Sheets Filter** cột F để lọc HS đã hoàn thành vs. chưa hoàn thành.  
> Dùng **Conditional Formatting** để tô màu ô điểm (xanh = cao, đỏ = thấp).

---

## 🔗 TÀI NGUYÊN & THÔNG TIN KỸ THUẬT

- **CDN KaTeX** (render công thức toán trong câu hỏi): `https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.js`
- **CDN Canvas-Confetti** (hiệu ứng pháo bông khi đúng): `https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js`
- **YouTube IFrame API**: `https://www.youtube.com/iframe_api`
- **Netlify Drop** (deploy miễn phí): `https://app.netlify.com`
- **Google Apps Script**: Trong Google Sheets → `Tiện ích mở rộng` → `Apps Script`

---

*Tính năng này được tổng hợp từ thực tế sản phẩm Video Tương Tác Toán 6 Bài 6 — Lũy thừa với số mũ tự nhiên, do GV Nguyễn Thiện (THCS Ứng Hòe) triển khai thực tế ngày 29/10/2026.*


### H. Tối Ưu Hóa Trải Nghiệm Trên Điện Thoại (Mobile First)

- **Chiếm trọn màn hình khi hiện câu hỏi (Viewport Take-over):** Trên điện thoại di động (chiều ngang hẹp), khung câu hỏi tự động phóng to toàn màn hình (`position: fixed; width: 100vw; height: 100vh`), không bị bó hẹp trong khung video 200px.
- **Vùng chạm chuẩn Touch Target:** Các nút đáp án có chiều cao tối thiểu 48px, padding rộng rãi, chống bấm nhầm ngón tay.
- **Chống phóng to màn hình iOS Safari:** Cỡ chữ trong ô nhập số tự động gán `16px` để bàn phím bật lên không làm co giật trang web.

### I. Đổi Tên & Lớp Học Sinh Trực Tiếp (Switch / Change Student)

- Nút tên học sinh trên thanh tiêu đề: `👤 Tên (Lớp) ✏️ Đổi`.
- Bấm vào bất kỳ lúc nào để:
  1. **Sửa lại tên/lớp:** Khi học sinh gõ nhầm (ví dụ từ `6A` sang `6B`) $\to$ Dữ liệu Google Sheets tự động chuyển học sinh sang tab lớp mới!
  2. **Đổi sang học sinh khác:** Khi anh/chị/em trong nhà dùng chung 1 chiếc điện thoại $\to$ Chọn *"Đây là học sinh khác"* để bắt đầu lượt học mới từ đầu (điểm số và trạm giải reset về 0 cho học sinh mới).


### J. Tiêu Chuẩn Hoàn Thành Bài Học (Mastery Threshold ≥ 80%)

- **Quy tắc tính điểm chống đoán mò / spam click:**
  - **Đúng ngay lần đầu (Lần 1):** Được trọn vẹn **+1.0 điểm**.
  - **Đúng ở lần 2 (tự sửa lỗi sau gợi ý):** Được **+0.5 điểm**.
  - **Sai từ 2 lần trở lên:** Hệ thống hiển thị đáp án đúng + lời giải chi tiết, tính **0 điểm** cho câu đó, và tự động mở khóa cho học sinh tiếp tục xem video (tránh học sinh bị kẹt mãi ở 1 câu).
- **Phân loại kết quả cuối bài:**
  - **Đạt từ 80% trở lên (tối thiểu 6/7 câu đúng):**
    - Giao diện: Vòng tròn điểm xanh lá, bắn pháo hoa Confetti, công nhận hoàn thành bài.
    - Sổ điểm Google Sheets: `🟢 ĐÃ HOÀN THÀNH (ĐẠT: X/7 - Y%)` $\to$ Tính vào mục hoàn thành của lớp.
  - **Dưới 80% (< 5.6 điểm, tức dưới 6 câu):**
    - Giao diện: Vòng tròn điểm màu cam/đỏ, cảnh báo *"⚠️ CHƯA ĐẠT TIÊU CHUẨN HOÀN THÀNH BÀI (Yêu cầu ≥ 80%)"*, không bắn pháo hoa.
    - Nút hành động: Nổi bật nút *"🔄 Học lại bài giảng để đạt chuẩn ≥ 80%"*.
    - Sổ điểm Google Sheets: `🔴 CHƯA ĐẠT (Cần học lại: X/7 - Y%)` $\to$ Thầy Cô nhìn vào là biết ngay học sinh cần ôn tập lại.


### K. Công Cụ Sinh Tự Động Bằng Python: `scripts/interactive_video_builder.py`

Hệ thống cung cấp sẵn script Python để tự động ráp template và xuất file HTML / thư mục Netlify chỉ với 1 hàm gọi:

```python
from scripts.interactive_video_builder import build_interactive_video_html, package_netlify_folder

# 1. Cấu hình bài học
checkpoints = [
    {
        "id": 1, "time": 190, "type": "mcq",
        "question": "Cho lũy thừa 7⁴. Cơ số và số mũ là?",
        "options": ["A. 4 và 7", "B. 7 và 4", "C. 7 và 28", "D. 28 và 7"],
        "correct": 1,
        "explanation": "Trong aⁿ, a là cơ số và n là số mũ."
    },
    # ... các trạm tiếp theo
]

# 2. Sinh file HTML và đóng gói thư mục Netlify
html = build_interactive_video_html(
    lesson_title="Bài 6: Lũy thừa với số mũ tự nhiên",
    subject_grade="Toán 6",
    teacher_name="Nguyễn Thiện (THCS Ứng Hòe)",
    youtube_id="EaYtq5u1Wzw",
    apps_script_url="https://script.google.com/macros/s/.../exec",
    checkpoints=checkpoints,
    passing_threshold_pct=80,      # Tiêu chuẩn hoàn thành >= 80%
    teacher_password="123456",     # Mật mã mở khóa duyệt bài Thầy Cô
    output_html_path="dist/index.html"
)

# 3. Kéo thả thư mục 'dist' vào app.netlify.com là xong!
```


### L. Bộ Kiểm Định Chất Lượng Tự Động (Future-Proof QA Gate): `validate_checkpoints()`

Để bảo đảm **100% các video bài giảng tạo mới trong tương lai** đều chạy mượt mà, học sinh trả lời trôi chảy, không bao giờ gặp lỗi kẹt video hay lỗi biến mất chữ, hệ thống tích hợp sẵn cổng kiểm định chất lượng tự động:

1. **Tự động sắp xếp tuyến tính:** Tự động sắp xếp lại các trạm theo thứ tự thời gian tăng dần, đánh số `Trạm 1, Trạm 2, Trạm 3...` chuẩn xác kể cả khi người dùng nhập lộn xộn.
2. **Kiểm tra tính hợp lệ của từng dạng câu hỏi:**
   - **MCQ:** Bắt buộc số phương án $\ge 2$, chỉ số `correct` phải nằm trong khoảng hợp lệ ($0 \le 	ext{correct} < 	ext{len}(	ext{options})$).
   - **Đúng / Sai:** Tự động chuyển đổi các giá trị linh hoạt (`true`, `đúng`, `1`) thành Boolean chuẩn.
   - **Điền số:** Bắt buộc có chuỗi đáp án chuẩn, tự động bật `autocomplete="off"` và tạm dừng vòng lặp quét 250ms để học sinh gõ số thoải mái không bao giờ bị mất chữ.
   - **Kéo thả / Chạm thẻ số:** Kiểm tra danh sách thẻ `tiles` và vị trí rơi hợp lệ.
3. **Cảnh báo nhịp độ sư phạm (Pacing Check):** Cảnh báo nếu 2 câu hỏi quá sát nhau ($< 45	ext{s}$) gây ức chế ngắt quãng, hoặc quá thưa ($> 300	ext{s}$) khiến học sinh xem thụ động.
4. **Kế thừa Master Template:** Mọi bài giảng mới đều được sinh từ [`templates/video_tuong_tac_template.html`](../templates/video_tuong_tac_template.html) đã được kiểm thử thực tế và tích hợp trọn vẹn toàn bộ các bản vá lỗi (chống tua, tự nhớ tiến độ, đổi tên học sinh, chuẩn đạt 80%, di động tràn màn hình).

---

## 🐛 M. Lỗi Đã Biết & Đã Vá (Bug Tracker)

> Ghi lại để tránh tái phát khi tạo video mới. **Master Template đã được vá toàn bộ**.

| # | Dạng câu hỏi / Tính năng | Triệu chứng | Nguyên nhân gốc | Trạng thái |
|---|---|---|---|---|
| 1 | **Điền số (`fill`)** | Chữ học sinh gõ biến mất ngay khi nhập | `startMonitoring()` chạy 250ms gọi `pauseAndOpenQuiz()` → re-render `cArea.innerHTML` xóa text đang gõ | ✅ Đã vá: thêm guard `isQuizCurrentlyOpen()` ở đầu monitoring loop + tự động nhận diện `inputmode` (`numeric`/`decimal`/`text`) hỗ trợ số âm `-5` và thập phân `3,5 = 3.5` |
| 2 | **Đúng/Sai (`tf`)** | Sau khi chọn đáp án: phát âm thanh nhưng video kẹt cứng, không hiện nút Tiếp tục | (1) ID button bị lệch: HTML tạo `id="tf-true"/"tf-false"` nhưng JS tìm `id="tf-btn-true"/"tf-btn-false"` → `null` → JS crash ngay sau âm thanh; (2) Chấm 1-chạm dứt điểm cho câu 2 lựa chọn để luôn hiện nút `Tiếp tục bài học ▶️` ngay lập tức (dù chọn Đúng hay Sai) | ✅ Đã vá: đồng bộ `tf-btn-true` / `tf-btn-false` + `tf-badge-*`, chấm 1-chạm luôn hiện nút Tiếp tục & tự phát tiếp |
| 3 | **Trắc nghiệm (`mcq`)** | Chạm đúp trên điện thoại làm mất oan lượt 2; bất đẳng thức `<a` làm vỡ HTML | Nút chọn sai lần 1 chưa bị khóa `disabled`; chuỗi phương án chưa escape `<` `>` trước khi gán `innerHTML` | ✅ Đã vá: khóa nút vừa chọn sai lần 1 + `escapeHtml()` + tự động render công thức Toán KaTeX |
| 4 | **Chạm / Ghép thẻ (`drag`)** | Video mới dùng dạng `drag` bị treo khung câu hỏi | `validate_checkpoints()` cho phép `drag` nhưng HTML template thiếu nhánh render & `handleInstantDrag()` | ✅ Đã vá: tích hợp đầy đủ UI chạm/ghép thẻ trên điện thoại & máy tính + chấm 2 lượt + tự phát tiếp |
| 5 | **Đổi tên/lớp & Auto-Resume** | Bấm "Lưu thông tin mới" không đóng modal; tự lưu tiến độ lỗi ngầm | `saveStudentProgressLocally()` gọi `PlayerEngine.getCurrentTime()` (chỉ có `getTime()`) gây `TypeError` | ✅ Đã vá: bổ sung alias `getCurrentTime()`, bọc `safeStorage*` chống lỗi Safari ẩn danh/Zalo WebView, tách key lưu tiến độ riêng theo từng `YOUTUBE_VIDEO_ID` |
| 6 | **YouTube chạy ngầm & Di động** | YouTube tự chạy ngầm sau khi mở câu hỏi; nút Tiếp tục bị che bởi thanh điều hướng di động | `ytPlayer.seekTo()` sau `pauseVideo()` kích hoạt buffer & auto-play; CSS mobile dùng sai tên class cũ và thiếu `100dvh` | ✅ Đã vá: chặn tuyệt đối phát ngầm trong `onStateChange` khi quiz đang mở; chuẩn hóa CSS `100dvh`/`92dvh` ghim cố định nút Tiếp tục |
| 7 | **Học lại khi < 80%** | Học sinh chưa đạt 80% bấm Học lại nhưng không hiện lại câu hỏi để nâng điểm | `restartLesson()` cũ chỉ `seekTo(0)` mà không xóa `attempts` các câu sai | ✅ Đã vá: thêm nút **🎯 Ôn & làm lại câu chưa đạt (Nâng điểm)** (`retryFailedQuestions()`) xóa riêng các câu `< 1đ` và nhảy tới trước câu sai 25s, kèm nút **🔄 Học lại toàn bộ từ đầu** |
| 8 | **Google Sheets** | Nhiều hàng trùng tên học sinh; tổng số câu bị cố định `/7` cho bài khác | Race condition khi POST song song; hằng số `/7` & tên bài bị hardcode | ✅ Đã vá: thêm `LockService` trong Apps Script V4 + tự động hóa 100% theo `checkpoints.length` và `LESSON_TITLE` |

### ⚠️ Quy tắc bắt buộc khi tạo HTML câu hỏi Đúng/Sai:

```html
<!-- ĐÚNG ✅ — ID phải khớp với handleInstantTF() -->
<button class="tf-btn" id="tf-btn-true"  onclick="handleInstantTF(true)">✅ ĐÚNG</button>
<button class="tf-btn" id="tf-btn-false" onclick="handleInstantTF(false)">❌ SAI</button>

<!-- SAI ❌ — id="tf-true" sẽ gây crash JS -->
<button class="tf-btn" id="tf-true"  onclick="handleInstantTF(true)">✅ ĐÚNG</button>
<button class="tf-btn" id="tf-false" onclick="handleInstantTF(false)">❌ SAI</button>
```

### ✅ Checklist kiểm tra sau khi tạo video mới:

- [ ] Câu MCQ: Bấm đúng → màu xanh + âm thanh + đếm ngược 4s + video tiếp tục
- [ ] Câu MCQ: Bấm sai lần 1 → rung + banner đỏ + hiện giải thích + nút "Xem lại 30s"
- [ ] Câu MCQ: Bấm sai lần 2 → hiện đáp án đúng màu xanh + 0 điểm + đếm ngược tiếp tục
- [ ] Câu Đúng/Sai: Bấm đúng → màu xanh + âm thanh + **hiện nút Tiếp tục** + đếm ngược 4s
- [ ] Câu Đúng/Sai: Bấm sai → rung + banner đỏ + xem lại
- [ ] Câu Điền số: Gõ số → chữ **KHÔNG biến mất** khi đang gõ
- [ ] Câu Điền số: Bấm Kiểm tra (hoặc Enter) → phản hồi ngay
- [ ] Đổi tên/lớp: Bấm nút "Đổi" → hiện modal → nhập tên mới → lưu được
