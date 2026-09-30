# Thư Viện Mẫu Code TikZ — Hình Vẽ Đề Thi Lớp 6-12

> **Phiên bản:** 1.0 | **Cập nhật:** 2026-09  
> **Mục đích:** File tài liệu tham khảo — AI COPY snippet rồi điều chỉnh tham số cho phù hợp đề thi.

---

## Cách sử dụng

AI gọi `tikz_renderer.py` để biên dịch snippet thành ảnh PNG:

```python
# Trong script tạo đề, gọi:
result = subprocess.run(
    ["python", TIKZ_RENDERER_PATH, "--code", tikz_snippet, "--output", output_png],
    capture_output=True, text=True
)
```

`tikz_renderer.py` tự động wrap snippet vào document đầy đủ với preamble:
```latex
\documentclass[tikz,border=4pt]{standalone}
\usepackage{tikz,pgfplots,tkz-euclide,circuitikz,chemfig}
\usepackage[vietnamese]{babel}
\usepackage{amsmath,amssymb}
\usetikzlibrary{arrows.meta,angles,quotes,calc,3d,patterns,decorations.pathmorphing}
\tkzSetUpPoint[size=4,color=black,fill=black]
```

**Quy ước trong file này:**
- Mỗi mẫu có: tên, lớp áp dụng, code snippet, tham số có thể thay đổi
- Code là **SNIPPET** — không có `\documentclass`, không có `\begin{document}`
- Nét thấy: `line width=0.9pt`; Nét khuất: `dashed, line width=0.6pt`
- Nhãn tiếng Việt dùng khi phù hợp (babel/vietnam đã load)

---

## MÔN TOÁN

### Lớp 6–8: Hình Học Phẳng Cơ Bản

---

#### Mẫu T01 — Tam giác ABC bất kỳ với đường cao, trung điểm

**Lớp áp dụng:** 6–9  
**Kết quả:** Tam giác ABC, đường cao AH từ A xuống BC, trung điểm M của AC được đánh dấu.

```latex
% ===== T01: Tam giác ABC bất kỳ =====
% Tham số có thể thay đổi:
%   A=(0,3), B=(0,0), C=(4,0)  — tọa độ 3 đỉnh
%   Nhãn A, B, C — có thể đổi thành P, Q, R...
\begin{tikzpicture}[line width=0.9pt, font=\small]
  % --- Tọa độ đỉnh ---
  \coordinate (A) at (0,3);
  \coordinate (B) at (0,0);
  \coordinate (C) at (4,0);

  % --- Vẽ tam giác ---
  \draw (A) -- (B) -- (C) -- cycle;

  % --- Đường cao từ A xuống BC ---
  % H là chân đường cao (chiếu A lên BC)
  \tkzDefPointBy[projection=onto B--C](A) \tkzGetPoint{H}
  \draw[dashed, line width=0.6pt] (A) -- (H);
  % Ký hiệu góc vuông tại H
  \tkzMarkRightAngle[size=0.2](A,H,C)

  % --- Trung điểm M của AC ---
  \coordinate (M) at ($(A)!0.5!(C)$);
  \draw[fill=black] (M) circle (1.5pt);
  % Ký hiệu trung điểm (2 gạch nhỏ)
  \tkzMarkSegment[mark=||,size=3pt](A,M)
  \tkzMarkSegment[mark=||,size=3pt](M,C)

  % --- Nhãn đỉnh ---
  \node[above]       at (A) {$A$};
  \node[below left]  at (B) {$B$};
  \node[below right] at (C) {$C$};
  \node[below]       at (H) {$H$};
  \node[right]       at (M) {$M$};

  % --- Điểm đỉnh ---
  \fill (A) circle (1.5pt);
  \fill (B) circle (1.5pt);
  \fill (C) circle (1.5pt);
\end{tikzpicture}
```

---

#### Mẫu T02 — Tam giác vuông tại A với ký hiệu góc vuông

**Lớp áp dụng:** 6–9  
**Kết quả:** Tam giác vuông tại A, ký hiệu vuông, nhãn góc nhọn α và β tại B, C.

```latex
% ===== T02: Tam giác vuông tại A =====
% Tham số: B=(0,0), C=(4,0), A=(0,3) — thay đổi để có tỉ lệ phù hợp
% Góc alpha tại B, beta tại C
\begin{tikzpicture}[line width=0.9pt, font=\small]
  \coordinate (A) at (0,3);   % đỉnh góc vuông
  \coordinate (B) at (0,0);
  \coordinate (C) at (4,0);

  % Vẽ tam giác
  \draw (A) -- (B) -- (C) -- cycle;

  % Ký hiệu góc vuông tại A
  \draw (0,0.25) -- (0.25,0.25) -- (0.25,0);  % vuông tại A=(0,0) tương đối
  % (Nếu A không ở gốc, dùng tkzMarkRightAngle)
  \tkzMarkRightAngle[size=0.25](B,A,C)

  % Nhãn góc nhọn
  \tkzMarkAngle[size=0.7, arc=l](C,B,A)
  \node at (0.55,0.22) {$\alpha$};

  \tkzMarkAngle[size=0.7, arc=l](A,C,B)
  \node at (3.35,0.22) {$\beta$};

  % Nhãn cạnh (tuỳ chọn)
  \node[left]  at ($(A)!0.5!(B)$) {$b$};
  \node[below] at ($(B)!0.5!(C)$) {$a$};
  \node[right, xshift=3pt] at ($(A)!0.5!(C)$) {$c$};

  % Nhãn đỉnh
  \node[left]        at (A) {$A$};
  \node[below left]  at (B) {$B$};
  \node[below right] at (C) {$C$};

  \fill (A) circle (1.5pt);
  \fill (B) circle (1.5pt);
  \fill (C) circle (1.5pt);
\end{tikzpicture}
```

---

#### Mẫu T03 — Tam giác cân với đường phân giác/trung trực

**Lớp áp dụng:** 6–8  
**Kết quả:** Tam giác cân ABC (AB=AC), đường phân giác từ A cũng là đường cao, trung trực của BC.

```latex
% ===== T03: Tam giác cân ABC (AB=AC) =====
% Tham số: thay đổi tọa độ để có góc ở đỉnh A khác nhau
\begin{tikzpicture}[line width=0.9pt, font=\small]
  \coordinate (A) at (2,3.5);   % đỉnh
  \coordinate (B) at (0,0);
  \coordinate (C) at (4,0);
  \coordinate (M) at (2,0);     % trung điểm BC = chân đường cao

  % Vẽ tam giác
  \draw (A) -- (B) -- (C) -- cycle;

  % Đường phân giác / đường cao / trung trực từ A
  \draw[dashed, line width=0.6pt] (A) -- (M);
  \tkzMarkRightAngle[size=0.22](A,M,C)

  % Ký hiệu cạnh bằng nhau
  \tkzMarkSegment[mark=|, size=4pt](A,B)
  \tkzMarkSegment[mark=|, size=4pt](A,C)
  \tkzMarkSegment[mark=||,size=3pt](B,M)
  \tkzMarkSegment[mark=||,size=3pt](M,C)

  % Nhãn
  \node[above]       at (A) {$A$};
  \node[below left]  at (B) {$B$};
  \node[below right] at (C) {$C$};
  \node[below]       at (M) {$M$};

  \fill (A) circle (1.5pt);
  \fill (B) circle (1.5pt);
  \fill (C) circle (1.5pt);
  \fill (M) circle (1.5pt);
\end{tikzpicture}
```

---

#### Mẫu T04 — Tứ giác ABCD bất kỳ

**Lớp áp dụng:** 6–8  
**Kết quả:** Tứ giác lồi ABCD với 4 đỉnh và nhãn.

```latex
% ===== T04: Tứ giác ABCD bất kỳ =====
% Tham số: thay đổi 4 tọa độ đỉnh
\begin{tikzpicture}[line width=0.9pt, font=\small]
  \coordinate (A) at (0,2);
  \coordinate (B) at (1,0);
  \coordinate (C) at (4,0.5);
  \coordinate (D) at (3.5,3);

  \draw (A) -- (B) -- (C) -- (D) -- cycle;

  % Đường chéo (tuỳ chọn — bỏ comment nếu cần)
  % \draw[dashed, line width=0.6pt] (A)--(C);
  % \draw[dashed, line width=0.6pt] (B)--(D);

  \node[left]        at (A) {$A$};
  \node[below left]  at (B) {$B$};
  \node[below right] at (C) {$C$};
  \node[above right] at (D) {$D$};

  \fill (A) circle (1.5pt);
  \fill (B) circle (1.5pt);
  \fill (C) circle (1.5pt);
  \fill (D) circle (1.5pt);
\end{tikzpicture}
```

---

#### Mẫu T05 — Hình bình hành ABCD với đường chéo

**Lớp áp dụng:** 6–9  
**Kết quả:** Hình bình hành ABCD, hai đường chéo AC và BD cắt nhau tại O (trung điểm).

```latex
% ===== T05: Hình bình hành ABCD =====
% Tham số: (ax,ay) tọa độ A; (bx,by) tọa độ B; vec=(dx,dy) vectơ AD
\begin{tikzpicture}[line width=0.9pt, font=\small]
  \coordinate (A) at (0,0);
  \coordinate (B) at (3,0);
  \coordinate (C) at (4,2);
  \coordinate (D) at (1,2);   % D = A + (C - B) đảm bảo song song

  % Giao điểm đường chéo
  \coordinate (O) at ($(A)!0.5!(C)$);

  % Vẽ hình bình hành
  \draw (A) -- (B) -- (C) -- (D) -- cycle;

  % Đường chéo
  \draw[dashed, line width=0.6pt] (A) -- (C);
  \draw[dashed, line width=0.6pt] (B) -- (D);

  % Ký hiệu trung điểm đường chéo
  \tkzMarkSegment[mark=|, size=3pt](A,O)
  \tkzMarkSegment[mark=|, size=3pt](O,C)
  \tkzMarkSegment[mark=||,size=3pt](B,O)
  \tkzMarkSegment[mark=||,size=3pt](O,D)

  % Ký hiệu cạnh song song bằng nhau
  \tkzMarkSegment[mark=>, size=5pt](A,B)
  \tkzMarkSegment[mark=>, size=5pt](D,C)
  \tkzMarkSegment[mark=>>, size=5pt](A,D)
  \tkzMarkSegment[mark=>>, size=5pt](B,C)

  \node[below left]  at (A) {$A$};
  \node[below right] at (B) {$B$};
  \node[above right] at (C) {$C$};
  \node[above left]  at (D) {$D$};
  \node[right, xshift=3pt] at (O) {$O$};

  \fill (A) circle (1.5pt); \fill (B) circle (1.5pt);
  \fill (C) circle (1.5pt); \fill (D) circle (1.5pt);
  \fill (O) circle (1.5pt);
\end{tikzpicture}
```

---

#### Mẫu T06 — Hình thang ABCD (AB // CD)

**Lớp áp dụng:** 6–9  
**Kết quả:** Hình thang với AB // CD, ký hiệu song song, đường cao từ D xuống AB.

```latex
% ===== T06: Hình thang ABCD (AB // CD) =====
% Tham số: AB=4 (đáy lớn), CD=2 (đáy nhỏ), h=2.5 (chiều cao)
\begin{tikzpicture}[line width=0.9pt, font=\small]
  \coordinate (A) at (0,0);
  \coordinate (B) at (4,0);
  \coordinate (C) at (3.2,2.5);
  \coordinate (D) at (1.2,2.5);

  % Chân đường cao từ D
  \coordinate (H) at (1.2,0);

  \draw (A) -- (B) -- (C) -- (D) -- cycle;
  \draw[dashed, line width=0.6pt] (D) -- (H);
  \tkzMarkRightAngle[size=0.22](D,H,B)

  % Ký hiệu song song
  \tkzMarkSegment[mark=>, size=5pt](A,B)
  \tkzMarkSegment[mark=>, size=5pt](D,C)

  % Nhãn chiều cao (tuỳ chọn)
  \node[left, xshift=-3pt] at ($(D)!0.5!(H)$) {$h$};

  \node[below left]  at (A) {$A$};
  \node[below right] at (B) {$B$};
  \node[above right] at (C) {$C$};
  \node[above left]  at (D) {$D$};
  \node[below]       at (H) {$H$};

  \fill (A) circle (1.5pt); \fill (B) circle (1.5pt);
  \fill (C) circle (1.5pt); \fill (D) circle (1.5pt);
\end{tikzpicture}
```

---

### Lớp 9: Đường Tròn

---

#### Mẫu T07 — Đường tròn (O;R) với tiếp tuyến, dây cung, cung

**Lớp áp dụng:** 9  
**Kết quả:** Đường tròn tâm O bán kính R, tiếp tuyến tại A, dây cung BC, cung BC tô màu.

```latex
% ===== T07: Đường tròn với tiếp tuyến và dây cung =====
% Tham số: R=2 (bán kính), góc đặt điểm A, B, C trên đường tròn
\begin{tikzpicture}[line width=0.9pt, font=\small]
  \coordinate (O) at (0,0);
  \def\R{2}

  % Vẽ đường tròn
  \draw (O) circle (\R);

  % Điểm A trên đường tròn (tiếp điểm) tại góc 90°
  \coordinate (A) at (0,\R);
  % Tiếp tuyến tại A (nằm ngang)
  \draw (-2.5,\R) -- (2.5,\R);
  % Bán kính OA vuông góc tiếp tuyến
  \draw[line width=0.7pt] (O) -- (A);
  \tkzMarkRightAngle[size=0.22](O,A,{(2.5,\R)})

  % Dây cung BC
  \coordinate (B) at ({2*cos(210)},{2*sin(210)});
  \coordinate (C) at ({2*cos(330)},{2*sin(330)});
  \draw[line width=1pt, blue] (B) -- (C);

  % Tô màu cung BC (cung nhỏ)
  \draw[red, line width=1.5pt] ({2*cos(210)}:{2}) arc (210:330:\R);

  % Bán kính OB, OC
  \draw[dashed, line width=0.6pt] (O) -- (B);
  \draw[dashed, line width=0.6pt] (O) -- (C);

  % Nhãn
  \node[right, xshift=4pt] at (O) {$O$};
  \node[above] at (A) {$A$};
  \node[below left]  at (B) {$B$};
  \node[below right] at (C) {$C$};
  \node[right, xshift=5pt] at ({2*cos(270)},{2*sin(270)}) {\textcolor{red}{cung $BC$}};

  \fill (O) circle (1.5pt);
  \fill (A) circle (1.5pt);
  \fill (B) circle (1.5pt);
  \fill (C) circle (1.5pt);
\end{tikzpicture}
```

---

#### Mẫu T08 — Đường tròn nội tiếp và ngoại tiếp tam giác

**Lớp áp dụng:** 9  
**Kết quả:** Tam giác ABC với đường tròn ngoại tiếp (O) và nội tiếp (I).

```latex
% ===== T08: Đường tròn nội tiếp / ngoại tiếp tam giác =====
\begin{tikzpicture}[line width=0.9pt, font=\small]
  % Đặt tam giác với tọa độ cụ thể
  \coordinate (A) at (0,3.2);
  \coordinate (B) at (-2,0);
  \coordinate (C) at (2.5,0);

  % Vẽ tam giác
  \draw (A) -- (B) -- (C) -- cycle;

  % Đường tròn ngoại tiếp (dùng tkz-euclide)
  \tkzCircumCenter(A,B,C) \tkzGetPoint{O}
  \tkzDrawCircle[line width=0.8pt, blue](O,A)

  % Đường tròn nội tiếp
  \tkzInCenter(A,B,C) \tkzGetPoint{I}
  \tkzDrawCircle[in, line width=0.8pt, red](I,A)   % vẽ vòng nội tiếp

  % Nhãn tâm
  \node[right, xshift=3pt, blue]  at (O) {$O$};
  \node[right, xshift=3pt, red]   at (I) {$I$};

  \node[above]       at (A) {$A$};
  \node[below left]  at (B) {$B$};
  \node[below right] at (C) {$C$};

  \fill (O) circle (1.5pt);
  \fill (I) circle (1.5pt);
  \fill (A) circle (1.5pt);
  \fill (B) circle (1.5pt);
  \fill (C) circle (1.5pt);
\end{tikzpicture}
```

---

#### Mẫu T09 — Hai đường tròn cắt nhau tại A và B

**Lớp áp dụng:** 9  
**Kết quả:** Hai đường tròn (O;R1) và (O';R2) cắt nhau tại A và B, đoạn nối tâm OO'.

```latex
% ===== T09: Hai đường tròn cắt nhau =====
% Tham số: tâm O1, O2; bán kính R1, R2
\begin{tikzpicture}[line width=0.9pt, font=\small]
  \coordinate (O1) at (-1,0);
  \coordinate (O2) at (1.2,0);
  \def\Ra{2}
  \def\Rb{1.8}

  \draw (O1) circle (\Ra);
  \draw (O2) circle (\Rb);

  % Đường nối tâm
  \draw[dashed, line width=0.6pt] (O1) -- (O2);

  % Giao điểm A, B (tính thủ công hoặc dùng tkz-euclide)
  \tkzInterCC(O1,\Ra)(O2,\Rb) \tkzGetPoints{A}{B}
  % Dây chung AB
  \draw[blue, line width=1pt] (A) -- (B);

  \node[left]  at (O1) {$O$};
  \node[right] at (O2) {$O'$};
  \node[above, yshift=2pt] at (A) {$A$};
  \node[below, yshift=-2pt] at (B) {$B$};

  \fill (O1) circle (1.5pt); \fill (O2) circle (1.5pt);
  \fill (A)  circle (1.5pt); \fill (B)  circle (1.5pt);
\end{tikzpicture}
```

---

#### Mẫu T10 — Góc nội tiếp, góc tâm, góc tiếp tuyến-dây

**Lớp áp dụng:** 9  
**Kết quả:** Đường tròn tâm O, cung BC, góc nội tiếp BAC, góc tâm BOC.

```latex
% ===== T10: Góc nội tiếp và góc tâm =====
\begin{tikzpicture}[line width=0.9pt, font=\small]
  \coordinate (O) at (0,0);
  \def\R{2.2}
  \draw (O) circle (\R);

  % B, C trên đường tròn
  \coordinate (B) at ({2.2*cos(200)},{2.2*sin(200)});
  \coordinate (C) at ({2.2*cos(340)},{2.2*sin(340)});
  % A trên cung lớn (phía trên)
  \coordinate (A) at ({2.2*cos(90)},{2.2*sin(90)});

  % Các cạnh
  \draw[blue] (A) -- (B) -- (C) -- (A);   % góc nội tiếp BAC
  \draw[red]  (O) -- (B);
  \draw[red]  (O) -- (C);                  % góc tâm BOC

  % Tô cung BC nhỏ
  \draw[orange, line width=1.5pt] ({2.2*cos(200)}:{2.2}) arc (200:340:\R);

  % Đánh dấu góc
  \tkzMarkAngle[size=0.6, blue](B,A,C)
  \node[blue, below, yshift=-3pt] at (A) {$\widehat{BAC}$};
  \tkzMarkAngle[size=0.5, red](B,O,C)
  \node[red, above, yshift=3pt] at (O) {$\widehat{BOC}$};

  \node[above]       at (A) {$A$};
  \node[below left]  at (B) {$B$};
  \node[below right] at (C) {$C$};
  \node[right, xshift=3pt] at (O) {$O$};

  \fill (O) circle (1.5pt);
  \fill (A) circle (1.5pt); \fill (B) circle (1.5pt); \fill (C) circle (1.5pt);
\end{tikzpicture}
```

---

### Lớp 10: Vectơ & Hệ Tọa Độ

---

#### Mẫu T11 — Hệ trục Oxy với vectơ

**Lớp áp dụng:** 10  
**Kết quả:** Hệ trục Oxy có mũi tên, vectơ $\vec{u}$ từ gốc tọa độ, tọa độ điểm A(3;2).

```latex
% ===== T11: Hệ trục Oxy với vectơ =====
% Tham số: xmax=5, ymax=4; điểm A=(3,2); vectơ u=(2,1.5)
\begin{tikzpicture}[line width=0.9pt, font=\small,
    >=Stealth]
  % Trục tọa độ
  \draw[->] (-0.5,0) -- (5.2,0) node[right] {$x$};
  \draw[->] (0,-0.5) -- (0,4.2) node[above] {$y$};
  \node[below left] at (0,0) {$O$};

  % Lưới nhẹ (tuỳ chọn)
  \draw[gray!30, thin] (0,0) grid (5,4);

  % Vectơ u từ O
  \draw[->, thick, blue] (0,0) -- (2,1.5)
        node[above right] {$\vec{u}(2;\,1{,}5)$};

  % Điểm A(3;2)
  \fill[red] (3,2) circle (2pt) node[above right] {$A(3;\,2)$};
  % Đường chiếu xuống trục (tuỳ chọn)
  \draw[dashed, line width=0.6pt, red] (3,0) -- (3,2) -- (0,2);
  \node[below] at (3,0) {$3$};
  \node[left]  at (0,2) {$2$};

  % Đơn vị trục
  \foreach \x in {1,2,3,4,5} \node[below] at (\x,0) {\tiny\x};
  \foreach \y in {1,2,3,4}   \node[left]  at (0,\y) {\tiny\y};
\end{tikzpicture}
```

---

#### Mẫu T12 — Phép cộng vectơ (quy tắc hình bình hành)

**Lớp áp dụng:** 10  
**Kết quả:** Quy tắc hình bình hành: $\vec{a} + \vec{b} = \vec{c}$, hình bình hành OABC.

```latex
% ===== T12: Cộng vectơ — quy tắc hình bình hành =====
% Tham số: vec_a=(3,0.5), vec_b=(1,2.5) — thay đổi 2 vectơ cộng
\begin{tikzpicture}[line width=0.9pt, font=\small, >=Stealth]
  \coordinate (O) at (0,0);
  \coordinate (A) at (3,0.5);    % đầu mút vectơ a
  \coordinate (B) at (1,2.5);    % đầu mút vectơ b
  \coordinate (C) at (4,3);      % C = A + B

  % Vectơ a (xanh lam)
  \draw[->, thick, blue]  (O) -- (A) node[midway, below] {$\vec{a}$};
  % Vectơ b (đỏ)
  \draw[->, thick, red]   (O) -- (B) node[midway, left]  {$\vec{b}$};
  % Vectơ tổng (đen)
  \draw[->, very thick]   (O) -- (C) node[midway, above left] {$\vec{a}+\vec{b}$};

  % Hoàn chỉnh hình bình hành
  \draw[dashed, line width=0.6pt, blue] (B) -- (C);
  \draw[dashed, line width=0.6pt, red]  (A) -- (C);

  % Nhãn đỉnh
  \node[below left]  at (O) {$O$};
  \node[below right] at (A) {$A$};
  \node[above left]  at (B) {$B$};
  \node[above right] at (C) {$C$};

  \fill (O) circle (1.5pt); \fill (A) circle (1.5pt);
  \fill (B) circle (1.5pt); \fill (C) circle (1.5pt);
\end{tikzpicture}
```

---

#### Mẫu T13 — Đường thẳng và điểm trong mặt phẳng Oxy

**Lớp áp dụng:** 10  
**Kết quả:** Hệ trục Oxy, đường thẳng $d: 2x - y + 1 = 0$, điểm A(1;2) và B(-1;-1).

```latex
% ===== T13: Đường thẳng trong Oxy =====
% Tham số: phương trình đường thẳng d: ax + by + c = 0
%   Ở đây: 2x - y + 1 = 0  =>  y = 2x + 1
\begin{tikzpicture}[line width=0.9pt, font=\small, >=Stealth]
  \draw[->] (-2.5,0) -- (3.5,0) node[right] {$x$};
  \draw[->] (0,-2.5) -- (0,4.5) node[above] {$y$};
  \node[below left] at (0,0) {\small $O$};

  % Đường thẳng d: y = 2x + 1 (x từ -1.5 đến 1.5)
  \draw[blue, thick] (-1.5, {2*(-1.5)+1}) -- (1.7, {2*1.7+1})
        node[right] {$d$};

  % Điểm A(1;2)
  \fill[red] (1,2) circle (2pt) node[right] {$A(1;\,2)$};
  % Điểm B(-1;-1) — nằm trên đường thẳng
  \fill[blue] (-1,-1) circle (2pt) node[left] {$B(-1;\,-1)$};

  % Giao với trục y (tung độ gốc = 1)
  \fill (0,1) circle (1.5pt) node[right, xshift=2pt] {\small$(0;1)$};

  % Giao với trục x (hoành độ gốc x=-0.5)
  \fill (-0.5,0) circle (1.5pt) node[below] {\small$(-\frac{1}{2};0)$};

  % Vạch đơn vị
  \foreach \x in {-2,-1,1,2,3} \node[below] at (\x,0) {\tiny\x};
  \foreach \y in {-2,-1,1,2,3,4} \node[left]  at (0,\y) {\tiny\y};
\end{tikzpicture}
```

---

#### Mẫu T14 — Góc giữa hai đường thẳng

**Lớp áp dụng:** 10–11  
**Kết quả:** Hai đường thẳng $d_1$, $d_2$ cắt nhau, đánh dấu góc nhọn $\varphi$ giữa chúng.

```latex
% ===== T14: Góc giữa hai đường thẳng =====
\begin{tikzpicture}[line width=0.9pt, font=\small, >=Stealth]
  % Gốc giao nhau
  \coordinate (O) at (0,0);

  % d1: hướng 30°, d2: hướng 80°
  % Tham số: thay đổi góc 30 và 80 theo đường thẳng cụ thể
  \coordinate (P1) at ({3*cos(30)}, {3*sin(30)});
  \coordinate (Q1) at ({-2*cos(30)},{-2*sin(30)});
  \coordinate (P2) at ({2.5*cos(80)},{2.5*sin(80)});
  \coordinate (Q2) at ({-1.5*cos(80)},{-1.5*sin(80)});

  \draw[blue]  (Q1) -- (P1) node[right] {$d_1$};
  \draw[red]   (Q2) -- (P2) node[above] {$d_2$};

  % Đánh dấu góc nhọn giữa d1 và d2
  \tkzMarkAngle[size=0.8, arc=l, mark=none](P1,O,P2)
  % Nhãn góc phi
  \node at ({0.9*cos(55)},{0.9*sin(55)}) {$\varphi$};

  % Điểm giao
  \fill (O) circle (1.5pt) node[below left] {$O$};
\end{tikzpicture}
```

---

#### Mẫu T15 — Khoảng cách từ điểm M đến đường thẳng d

**Lớp áp dụng:** 10  
**Kết quả:** Đường thẳng d, điểm M ngoài d, đường vuông góc từ M xuống d (khoảng cách h).

```latex
% ===== T15: Khoảng cách từ điểm đến đường thẳng =====
\begin{tikzpicture}[line width=0.9pt, font=\small, >=Stealth]
  % Đường thẳng d nằm ngang
  \draw[blue] (-1,0) -- (5,0) node[right] {$d$};

  % Điểm M trên cao
  \coordinate (M) at (2,2.5);
  \fill[red] (M) circle (2pt) node[above] {$M$};

  % Chân vuông góc H
  \coordinate (H) at (2,0);
  \draw[red, dashed, line width=0.7pt] (M) -- (H);
  \tkzMarkRightAngle[size=0.22, red](M,H,{(5,0)})
  \fill (H) circle (1.5pt) node[below] {$H$};

  % Nhãn khoảng cách
  \node[right, xshift=3pt, red] at ($(M)!0.5!(H)$) {$h = d(M,d)$};
\end{tikzpicture}
```

---

### Lớp 10–12: Hàm Số & Đồ Thị (pgfplots)

---

#### Mẫu T16 — Đồ thị hàm số bậc hai (parabol)

**Lớp áp dụng:** 10–12  
**Kết quả:** Parabol $y = ax^2 + bx + c$, đỉnh, giao trục.

```latex
% ===== T16: Đồ thị parabol y = x^2 - 2x - 3 =====
% Tham số: thay đổi hàm số \f{x}
\begin{tikzpicture}[font=\small]
\begin{axis}[
  width=7cm, height=6cm,
  axis lines=center,
  xlabel={$x$}, ylabel={$y$},
  xlabel style={right},
  ylabel style={above},
  xmin=-2, xmax=5, ymin=-5, ymax=6,
  xtick={-1,0,1,2,3,4},
  ytick={-4,-2,0,2,4},
  tick label style={font=\tiny},
  grid=both, grid style={gray!20},
  samples=80,
]
  % Hàm số: y = x^2 - 2x - 3
  \addplot[blue, thick, domain=-1.5:3.7] {x^2 - 2*x - 3};

  % Đỉnh parabol tại (1, -4)
  \addplot[mark=*, red, mark size=2pt] coordinates {(1,-4)};
  \node[red, right] at (axis cs:1,-4) {$I(1;\,-4)$};

  % Giao trục Ox: x=-1 và x=3
  \addplot[mark=*, black, mark size=2pt] coordinates {(-1,0) (3,0)};
  \node[above] at (axis cs:-1,0) {\small$-1$};
  \node[above] at (axis cs:3,0)  {\small$3$};

  % Giao trục Oy: y=-3
  \addplot[mark=*, black, mark size=2pt] coordinates {(0,-3)};
  \node[right] at (axis cs:0,-3) {\small$-3$};

  \node[blue, right] at (axis cs:3.5,5) {$y=x^2-2x-3$};
\end{axis}
\end{tikzpicture}
```

---

#### Mẫu T17 — Đồ thị hàm lượng giác sin/cos

**Lớp áp dụng:** 11  
**Kết quả:** Đồ thị $y = \sin x$ và $y = \cos x$ trên $[-\pi, 2\pi]$.

```latex
% ===== T17: Đồ thị sin và cos =====
\begin{tikzpicture}[font=\small]
\begin{axis}[
  width=10cm, height=5cm,
  axis lines=center,
  xlabel={$x$}, ylabel={$y$},
  xmin=-3.5, xmax=7,
  ymin=-1.5, ymax=1.8,
  xtick={-3.14159, -1.5708, 0, 1.5708, 3.14159, 4.7124, 6.2832},
  xticklabels={$-\pi$, $-\dfrac{\pi}{2}$, $0$,
               $\dfrac{\pi}{2}$, $\pi$,
               $\dfrac{3\pi}{2}$, $2\pi$},
  ytick={-1,0,1},
  tick label style={font=\small},
  samples=200,
  grid=both, grid style={gray!15},
]
  \addplot[blue, thick, domain=-3.5:7] {sin(deg(x))}
           node[right, pos=0.97] {$\sin x$};
  \addplot[red, thick, domain=-3.5:7, dashed] {cos(deg(x))}
           node[above, pos=0.6] {$\cos x$};
\end{axis}
\end{tikzpicture}
```

---

#### Mẫu T18 — Bảng biến thiên (tkz-tab)

**Lớp áp dụng:** 10–12  
**Kết quả:** Bảng biến thiên hàm $f(x) = x^3 - 3x$ với cực trị tại $x = \pm1$.

```latex
% ===== T18: Bảng biến thiên hàm f(x)=x^3-3x =====
% Tham số: thay đổi điểm đặc biệt và giá trị cực trị
\begin{tikzpicture}
\tkzTabInit[lgt=2, espcl=2.5]{
  $x$     / 1,
  $f'(x)$ / 1,
  $f(x)$  / 2.2
}{$-\infty$, $-1$, $1$, $+\infty$}

\tkzTabLine{, +, z, -, z, +, }

\tkzTabVar{
  -/ $-\infty$,
  +/ $2$,
  -/ $-2$,
  +/ $+\infty$
}
\end{tikzpicture}
```

---

### Lớp 11–12: Hình Không Gian

---

#### Mẫu T19 — Hình chóp S.ABC (đáy tam giác)

**Lớp áp dụng:** 11–12  
**Kết quả:** Hình chóp S.ABC, nét khuất dashed, đường cao SO.

```latex
% ===== T19: Hình chóp S.ABC =====
% Tham số: tọa độ A,B,C,S — điều chỉnh để được góc nhìn đẹp
\begin{tikzpicture}[line width=0.9pt, font=\small,
    x={(0.9cm,0cm)}, y={(0.4cm,0.5cm)}, z={(0cm,1cm)}]
  % Tọa độ đỉnh
  \coordinate (A) at (0,0,0);
  \coordinate (B) at (3,0,0);
  \coordinate (C) at (1.5,2.5,0);
  \coordinate (S) at (1.5,0.8,3);

  % Đáy ABC
  \draw (A) -- (B) -- (C) -- cycle;
  % Cạnh bên (nét thấy)
  \draw (S) -- (A);
  \draw (S) -- (B);
  \draw (S) -- (C);

  % Trung điểm đáy (tuỳ chọn: vẽ đường cao)
  \coordinate (O) at ($(A)!0.333!(B) + (0,0.833,0)$);
  % Gốc đường cao — tính bằng trọng tâm
  \coordinate (G) at ({(0+3+1.5)/3},{(0+0+2.5)/3},0);
  \draw[dashed, line width=0.6pt] (S) -- (G);
  \draw[dashed, line width=0.6pt] (G) -- (A);
  \draw[dashed, line width=0.6pt] (G) -- (B);
  \draw[dashed, line width=0.6pt] (G) -- (C);

  % Nhãn
  \node[below left]  at (A) {$A$};
  \node[below right] at (B) {$B$};
  \node[right]       at (C) {$C$};
  \node[above]       at (S) {$S$};

  \fill (A) circle (1.5pt); \fill (B) circle (1.5pt);
  \fill (C) circle (1.5pt); \fill (S) circle (1.5pt);
\end{tikzpicture}
```

---

#### Mẫu T20 — Hình chóp S.ABCD (đáy tứ giác)

**Lớp áp dụng:** 11–12  
**Kết quả:** Hình chóp S.ABCD đáy hình vuông, nét khuất dashed (SA, SD, AB nét khuất).

```latex
% ===== T20: Hình chóp S.ABCD đáy hình vuông =====
\begin{tikzpicture}[line width=0.9pt, font=\small,
    x={(1cm,0cm)}, y={(0.35cm,0.4cm)}, z={(0cm,1cm)}]
  \coordinate (A) at (0,0,0);
  \coordinate (B) at (3,0,0);
  \coordinate (C) at (3,3,0);
  \coordinate (D) at (0,3,0);
  \coordinate (S) at (1.5,1.5,3.5);

  % Đáy: DA, AB nét khuất; BC, CD nét thường
  \draw[dashed, line width=0.6pt] (D) -- (A) -- (B);
  \draw (B) -- (C) -- (D);

  % Cạnh bên
  \draw[dashed, line width=0.6pt] (S) -- (A);  % SA khuất
  \draw[dashed, line width=0.6pt] (S) -- (D);  % SD khuất
  \draw (S) -- (B);
  \draw (S) -- (C);

  \node[below left]  at (A) {$A$};
  \node[below right] at (B) {$B$};
  \node[right]       at (C) {$C$};
  \node[left]        at (D) {$D$};
  \node[above]       at (S) {$S$};

  \fill (A) circle (1.5pt); \fill (B) circle (1.5pt);
  \fill (C) circle (1.5pt); \fill (D) circle (1.5pt);
  \fill (S) circle (1.5pt);
\end{tikzpicture}
```

---

#### Mẫu T21 — Lăng trụ tam giác đứng ABC.A'B'C'

**Lớp áp dụng:** 11–12  
**Kết quả:** Lăng trụ đứng tam giác, 2 đáy ABC và A'B'C', các cạnh bên thẳng đứng.

```latex
% ===== T21: Lăng trụ đứng tam giác ABC.A'B'C' =====
\begin{tikzpicture}[line width=0.9pt, font=\small,
    x={(1cm,0cm)}, y={(0.35cm,0.4cm)}, z={(0cm,1cm)}]
  % Đáy dưới
  \coordinate (A) at (0,0,0);
  \coordinate (B) at (3,0,0);
  \coordinate (C) at (1.5,2.5,0);
  % Đáy trên (tịnh tiến theo z)
  \coordinate (A1) at (0,0,3);
  \coordinate (B1) at (3,0,3);
  \coordinate (C1) at (1.5,2.5,3);

  % Đáy dưới: AB khuất
  \draw[dashed, line width=0.6pt] (A) -- (B);
  \draw (B) -- (C); \draw (C) -- (A);

  % Cạnh bên: AA' khuất
  \draw[dashed, line width=0.6pt] (A) -- (A1);
  \draw (B) -- (B1); \draw (C) -- (C1);

  % Đáy trên
  \draw (A1) -- (B1) -- (C1) -- cycle;

  \node[below left]  at (A)  {$A$};
  \node[below right] at (B)  {$B$};
  \node[right]       at (C)  {$C$};
  \node[above left]  at (A1) {$A'$};
  \node[above right] at (B1) {$B'$};
  \node[right]       at (C1) {$C'$};

  \fill (A) circle (1.5pt); \fill (B) circle (1.5pt); \fill (C) circle (1.5pt);
  \fill (A1) circle (1.5pt); \fill (B1) circle (1.5pt); \fill (C1) circle (1.5pt);
\end{tikzpicture}
```

---

#### Mẫu T22 — Lăng trụ tứ giác đứng ABCD.A'B'C'D'

**Lớp áp dụng:** 11–12  
**Kết quả:** Lăng trụ tứ giác đứng, đáy hình chữ nhật.

```latex
% ===== T22: Lăng trụ tứ giác đứng ABCD.A'B'C'D' =====
\begin{tikzpicture}[line width=0.9pt, font=\small,
    x={(1cm,0cm)}, y={(0.4cm,0.35cm)}, z={(0cm,1cm)}]
  \coordinate (A) at (0,0,0); \coordinate (B) at (3,0,0);
  \coordinate (C) at (3,2,0); \coordinate (D) at (0,2,0);
  \coordinate (A1) at (0,0,2.5); \coordinate (B1) at (3,0,2.5);
  \coordinate (C1) at (3,2,2.5); \coordinate (D1) at (0,2,2.5);

  % Đáy dưới (A,D khuất)
  \draw[dashed, line width=0.6pt] (D) -- (A);
  \draw[dashed, line width=0.6pt] (A) -- (B);
  \draw (B) -- (C) -- (D);
  % Cạnh bên (AA', DD' khuất)
  \draw[dashed, line width=0.6pt] (A) -- (A1);
  \draw[dashed, line width=0.6pt] (D) -- (D1);
  \draw (B) -- (B1); \draw (C) -- (C1);
  % Đáy trên
  \draw (A1) -- (B1) -- (C1) -- (D1) -- cycle;

  \node[left]        at (A)  {$A$}; \node[right] at (B)  {$B$};
  \node[right]       at (C)  {$C$}; \node[left]  at (D)  {$D$};
  \node[above left]  at (A1) {$A'$};\node[above right] at (B1) {$B'$};
  \node[right]       at (C1) {$C'$};\node[above left]  at (D1) {$D'$};

  \fill (A) circle (1.5pt); \fill (B) circle (1.5pt);
  \fill (C) circle (1.5pt); \fill (D) circle (1.5pt);
  \fill (A1) circle (1.5pt); \fill (B1) circle (1.5pt);
  \fill (C1) circle (1.5pt); \fill (D1) circle (1.5pt);
\end{tikzpicture}
```

---

#### Mẫu T23 — Hình lập phương ABCD.A'B'C'D'

**Lớp áp dụng:** 11–12  
**Kết quả:** Hình lập phương cạnh $a$, 3 mặt nhìn thấy, 3 mặt khuất dashed.

```latex
% ===== T23: Hình lập phương ABCD.A'B'C'D' =====
% Tham số: \a = cạnh hình lập phương (đổi số đo)
\begin{tikzpicture}[line width=0.9pt, font=\small,
    x={(1cm,0cm)}, y={(0.4cm,0.4cm)}, z={(0cm,1cm)}]
  \def\a{2.5}
  \coordinate (A) at (0,0,0);   \coordinate (B) at (\a,0,0);
  \coordinate (C) at (\a,\a,0); \coordinate (D) at (0,\a,0);
  \coordinate (A1) at (0,0,\a);  \coordinate (B1) at (\a,0,\a);
  \coordinate (C1) at (\a,\a,\a);\coordinate (D1) at (0,\a,\a);

  % Nét khuất: AB, AD, AA'
  \draw[dashed, line width=0.6pt] (A)--(B) (A)--(D) (A)--(A1);
  % Nét thấy đáy dưới
  \draw (B)--(C)--(D);
  % Cạnh bên thấy
  \draw (B)--(B1); \draw (C)--(C1); \draw (D)--(D1);
  % Đáy trên
  \draw (A1)--(B1)--(C1)--(D1)--cycle;
  % Mặt trước thấy
  \draw (B1)--(B);

  \node[left]        at (A)  {$A$}; \node[right] at (B)  {$B$};
  \node[right]       at (C)  {$C$}; \node[left]  at (D)  {$D$};
  \node[above left]  at (A1) {$A'$};\node[above right] at (B1) {$B'$};
  \node[right]       at (C1) {$C'$};\node[above left]  at (D1) {$D'$};

  \fill (B) circle (1.5pt); \fill (C) circle (1.5pt);
  \fill (D) circle (1.5pt); \fill (A1) circle (1.5pt);
  \fill (B1) circle (1.5pt); \fill (C1) circle (1.5pt); \fill (D1) circle (1.5pt);
\end{tikzpicture}
```

---

## MÔN VẬT LÝ

### Lớp 6–8: Lực & Cơ Học Cơ Bản

---

#### Mẫu V01 — Vật trên mặt phẳng nghiêng với các lực

**Lớp áp dụng:** 10  
**Kết quả:** Khối hộp trên mặt phẳng nghiêng góc α, phân tích lực: $P$, $N$, $F_{ms}$, thành phần song song và vuông góc.

```latex
% ===== V01: Vật trên mặt phẳng nghiêng =====
% Tham số: \ang = góc nghiêng (30, 37, 45...), thay \ang
\begin{tikzpicture}[line width=0.9pt, font=\small, >=Stealth]
  \def\ang{30}   % góc nghiêng (độ)

  % Mặt phẳng nghiêng
  \draw[very thick] (0,0) -- ({5*cos(\ang)},{5*sin(\ang)}) -- (5,0) -- cycle;
  % Nét đáy
  \draw[very thick] (-0.3,0) -- (5.3,0);

  % Góc nghiêng
  \draw ({0.7*cos(0)}:{0.7}) arc (0:\ang:0.7);
  \node at ({0.9*cos(\ang/2)},{0.9*sin(\ang/2)}) {$\alpha$};

  % Vị trí vật (khối hộp nhỏ)
  \def\vx{2.5} \def\vy{1.45}   % chỉnh theo góc
  % Vẽ khối hộp (hình chữ nhật nghiêng theo mặt phẳng)
  \begin{scope}[rotate=\ang, shift={({2.2},0)}]
    \fill[gray!30] (0,0) rectangle (0.8,0.6);
    \draw (0,0) rectangle (0.8,0.6);
    \coordinate (CM) at (0.4,0.3);  % tâm khối hộp
  \end{scope}

  % Vị trí gần đúng tâm khối hộp
  \coordinate (CM) at ({2.2*cos(\ang)+0.4*cos(\ang)-0.3*sin(\ang)},
                        {2.2*sin(\ang)+0.4*sin(\ang)+0.3*cos(\ang)});

  % Lực trọng trường P (xuống)
  \draw[->, thick, blue]   (CM) -- ++(0,-2)   node[below] {$\vec{P}$};
  % Lực pháp tuyến N (vuông góc mặt phẳng)
  \draw[->, thick, red]    (CM) -- ++({-sin(\ang)},{cos(\ang)}) node[above] {$\vec{N}$};
  % Lực ma sát (song song mặt phẳng, hướng lên)
  \draw[->, thick, orange] (CM) -- ++({cos(\ang+180)},{sin(\ang+180)}) node[left] {$\vec{F}_{ms}$};
\end{tikzpicture}
```

---

#### Mẫu V02 — Đòn bẩy với điểm tựa O và hai lực

**Lớp áp dụng:** 6–8  
**Kết quả:** Thanh đòn bẩy, điểm tựa O hình tam giác, lực $F_1$ và $F_2$, tay đòn $l_1$, $l_2$.

```latex
% ===== V02: Đòn bẩy =====
% Tham số: vị trí điểm tựa O (thay 2.5 => chia tỉ lệ khác nhau)
\begin{tikzpicture}[line width=0.9pt, font=\small, >=Stealth]
  % Thanh đòn bẩy (nằm ngang)
  \draw[very thick] (-3,0) -- (4,0);

  % Điểm tựa O (tam giác)
  \coordinate (O) at (0.5,0);
  \draw[fill=gray!40] (O) -- ++(-0.35,-0.7) -- ++(0.7,0) -- cycle;
  \node[above, yshift=3pt] at (O) {$O$};

  % Lực F1 (tác dụng bên trái, hướng xuống)
  \coordinate (A) at (-2.5,0);
  \draw[->, thick, blue] (A) -- ++(0,-1.8) node[below] {$\vec{F}_1$};
  \fill (A) circle (2pt) node[above] {$A$};

  % Lực F2 (tác dụng bên phải, hướng xuống)
  \coordinate (B) at (3.2,0);
  \draw[->, thick, red] (B) -- ++(0,-1.2) node[below] {$\vec{F}_2$};
  \fill (B) circle (2pt) node[above] {$B$};

  % Tay đòn l1 và l2
  \draw[<->, gray] (-2.5,-0.5) -- (0.5,-0.5) node[midway,below] {$l_1$};
  \draw[<->, gray] (0.5,-0.5)  -- (3.2,-0.5) node[midway,below] {$l_2$};

  % Mặt đất
  \draw[very thick, gray] (-3.5,-0.7) -- (4.5,-0.7);
  \fill[pattern=north east lines, pattern color=gray]
    (-3.5,-1) rectangle (4.5,-0.7);
\end{tikzpicture}
```

---

#### Mẫu V03 — Ròng rọc cố định và ròng rọc động

**Lớp áp dụng:** 6–8  
**Kết quả:** Hai loại ròng rọc, dây kéo, lực F và trọng vật P.

```latex
% ===== V03: Ròng rọc cố định và ròng rọc động =====
\begin{tikzpicture}[line width=0.9pt, font=\small, >=Stealth]
%% --- Ròng rọc cố định (bên trái) ---
\begin{scope}[xshift=0cm]
  \node[above, font=\footnotesize\bfseries] at (1,4.5) {Ròng rọc cố định};
  % Trần nhà
  \fill[pattern=north east lines, pattern color=gray] (0,4) rectangle (2,4.3);
  \draw[very thick] (0,4) -- (2,4);
  % Ròng rọc
  \draw[fill=gray!20] (1,3.7) circle (0.35);
  \fill (1,3.7) circle (2pt);
  % Trục gắn vào trần
  \draw[very thick] (1,4) -- (1,4.05);
  % Dây (qua ròng rọc)
  \draw[very thick] (0.65,3.7) -- (0.65,1.5);  % nhánh trái (vật treo)
  \draw[very thick] (1.35,3.7) -- (1.35,1.8);  % nhánh phải (kéo)
  % Vật P
  \fill[gray!40] (0.2,1.1) rectangle (1.1,1.5);
  \draw (0.2,1.1) rectangle (1.1,1.5);
  \node at (0.65,1.3) {$P$};
  % Lực kéo F
  \draw[->, thick, red] (1.35,1.8) -- ++(0,-1) node[below] {$\vec{F}$};
\end{scope}

%% --- Ròng rọc động (bên phải) ---
\begin{scope}[xshift=3.5cm]
  \node[above, font=\footnotesize\bfseries] at (1,4.5) {Ròng rọc động};
  % Trần
  \fill[pattern=north east lines, pattern color=gray] (0,4) rectangle (2,4.3);
  \draw[very thick] (0,4) -- (2,4);
  % Hai nhánh dây lên trần
  \draw[very thick] (0.5,4) -- (0.5,2.5);
  \draw[very thick] (1.5,4) -- (1.5,2.15);
  % Ròng rọc động (treo theo vật)
  \draw[fill=gray!20] (1,2.5) circle (0.35);
  \fill (1,2.5) circle (2pt);
  % Dây bên phải kéo xuống
  \draw[very thick] (1.35,2.5) -- (1.35,1.8);
  \draw[->, thick, red] (1.35,1.8) -- ++(0,-0.9) node[below] {$\vec{F}$};
  % Vật P gắn vào tâm ròng rọc
  \fill[gray!40] (0.6,1.5) rectangle (1.4,2.1);
  \draw (0.6,1.5) rectangle (1.4,2.1);
  \node at (1,1.8) {$P$};
  \draw[very thick] (1,2.1) -- (1,2.15);
\end{scope}
\end{tikzpicture}
```

---

#### Mẫu V04 — Lò xo treo vật (gắn tường)

**Lớp áp dụng:** 6–10  
**Kết quả:** Lò xo lắp vào tường/trần, treo vật khối lượng m, mũi tên lực đàn hồi và trọng lực.

```latex
% ===== V04: Lò xo treo vật =====
% Tham số: chiều dài lò xo, kích thước vật
\begin{tikzpicture}[line width=0.9pt, font=\small, >=Stealth,
    decoration={coil, aspect=0.4, segment length=6pt, amplitude=5pt}]
  % Trần nhà
  \fill[pattern=north east lines, pattern color=gray] (-1,4.5) rectangle (1,4.8);
  \draw[very thick] (-1,4.5) -- (1,4.5);

  % Điểm gắn lò xo
  \draw[very thick] (0,4.5) -- (0,4.2);

  % Lò xo (dùng decoration coil)
  \draw[decorate, thick] (0,4.2) -- (0,2);

  % Vật treo (khối hộp)
  \fill[gray!30] (-0.5,1.3) rectangle (0.5,2);
  \draw (-0.5,1.3) rectangle (0.5,2);
  \node at (0,1.65) {$m$};

  % Lực trọng trường
  \draw[->, thick, blue] (0,1.3) -- ++(0,-1.2) node[below] {$\vec{P}=m\vec{g}$};
  % Lực đàn hồi lò xo
  \draw[->, thick, red]  (0,2)   -- ++(0, 1)   node[above] {$\vec{F}_{đh}$};

  % Độ giãn lò xo
  \draw[<->, gray, dashed] (0.8,4.2) -- (0.8,2) node[midway,right] {$\Delta l$};
\end{tikzpicture}
```

---

### Lớp 9–12: Điện Học (circuitikz)

---

#### Mẫu V05 — Mạch điện nối tiếp R1-R2-R3

**Lớp áp dụng:** 9  
**Kết quả:** Mạch kín với nguồn điện và ba điện trở mắc nối tiếp.

```latex
% ===== V05: Mạch nối tiếp R1-R2-R3 =====
% Tham số: thay giá trị R bằng số cụ thể trong node
\begin{tikzpicture}[line width=0.9pt, font=\small,
    circuit ee IEC, set resistor graphic=var resistor IEC graphic]
  % Nguồn điện — phía trái
  \draw (0,0) to[battery1, l=$\mathcal{E}$] (0,3);
  % Nối tiếp qua 3 điện trở
  \draw (0,3) -- (1.5,3)
        to[resistor, l=$R_1$] (3,3)
        to[resistor, l=$R_2$] (5,3)
        to[resistor, l=$R_3$] (6.5,3)
        -- (6.5,0) -- (0,0);
\end{tikzpicture}
```

---

#### Mẫu V06 — Mạch song song R1 // R2

**Lớp áp dụng:** 9  
**Kết quả:** Nguồn điện và hai điện trở mắc song song.

```latex
% ===== V06: Mạch song song R1 // R2 =====
\begin{tikzpicture}[line width=0.9pt, font=\small,
    circuit ee IEC, set resistor graphic=var resistor IEC graphic]
  % Đường dây chính
  \draw (0,0) to[battery1, l=$U$] (0,3) -- (2,3);
  \draw (2,0) -- (0,0);

  % Nhánh song song 1: R1
  \draw (2,3) to[resistor, l=$R_1$] (2,0);

  % Nhánh song song 2: R2
  \draw (2,3) -- (4,3) to[resistor, l=$R_2$] (4,0) -- (2,0);
\end{tikzpicture}
```

---

#### Mẫu V07 — Mạch hỗn hợp R1 nối tiếp (R2 // R3)

**Lớp áp dụng:** 9  
**Kết quả:** R1 nối tiếp với cụm song song (R2//R3), có nguồn điện.

```latex
% ===== V07: Mạch hỗn hợp R1 nt (R2//R3) =====
\begin{tikzpicture}[line width=0.9pt, font=\small,
    circuit ee IEC, set resistor graphic=var resistor IEC graphic]
  % Nguồn
  \draw (0,0) to[battery1, l=$U$] (0,3) -- (1.5,3);

  % R1 nối tiếp
  \draw (1.5,3) to[resistor, l=$R_1$] (3.5,3);

  % Điểm nút M và N
  \node[above] at (3.5,3) {$M$};
  \node[below] at (3.5,0) {$N$};

  % R2 nhánh trên
  \draw (3.5,3) to[resistor, l=$R_2$] (5.5,3) -- (5.5,0);
  % R3 nhánh dưới
  \draw (3.5,3) -- (3.5,1.5) to[resistor, l=$R_3$] (5.5,1.5) -- (5.5,0);

  \draw (5.5,0) -- (0,0);
  \fill (3.5,3) circle (2pt);
  \fill (5.5,0) circle (2pt);
\end{tikzpicture}
```

---

#### Mẫu V08 — Mạch RLC nối tiếp với nguồn xoay chiều

**Lớp áp dụng:** 12  
**Kết quả:** Mạch R-L-C nối tiếp với nguồn xoay chiều $u = U_0\cos\omega t$.

```latex
% ===== V08: Mạch RLC nối tiếp =====
\begin{tikzpicture}[line width=0.9pt, font=\small,
    circuit ee IEC, set resistor graphic=var resistor IEC graphic]
  % Nguồn xoay chiều
  \draw (0,0) to[sV, l=$u$] (0,3) -- (1,3)
        to[resistor, l=$R$] (3,3)
        to[inductor,  l=$L$] (5,3)
        to[capacitor, l=$C$] (7,3)
        -- (7,0) -- (0,0);
  % Nhãn nguồn
  \node[left, xshift=-4pt] at (0,1.5) {$u=U_0\cos\omega t$};
\end{tikzpicture}
```

---

#### Mẫu V09 — Mạch có ampe kế và vôn kế

**Lớp áp dụng:** 9–11  
**Kết quả:** Mạch với nguồn, R, ampe kế nối tiếp đo dòng, vôn kế song song đo điện áp.

```latex
% ===== V09: Mạch có ampe kế và vôn kế =====
\begin{tikzpicture}[line width=0.9pt, font=\small,
    circuit ee IEC, set resistor graphic=var resistor IEC graphic]
  % Mạch chính
  \draw (0,0) to[battery1, l=$U$] (0,3)
        to[ammeter] (2,3)         % Ampe kế nối tiếp
        to[resistor, l=$R$] (5,3)
        -- (5,0) -- (0,0);

  % Vôn kế song song với R
  \draw (2,3) -- (2,4.5) to[voltmeter] (5,4.5) -- (5,3);

  % Nhãn
  \node[above] at (1,3) {\small A};
  \node[above] at (3.5,4.5) {\small V};
\end{tikzpicture}
```

---

#### Mẫu V10 — Mạch có tụ điện và cuộn cảm

**Lớp áp dụng:** 11–12  
**Kết quả:** Mạch LC dao động hoặc mạch với tụ và cuộn cảm riêng biệt.

```latex
% ===== V10: Mạch LC dao động =====
\begin{tikzpicture}[line width=0.9pt, font=\small,
    circuit ee IEC]
  % Cuộn cảm L ở trên
  \draw (0,0) to[capacitor, l=$C$] (0,3)
              to[inductor,  l=$L$] (3,3)
              -- (3,0) -- (0,0);
  % Nhãn dòng điện (tuỳ chọn)
  \draw[->, red] (1.5,3.3) -- ++(0.7,0) node[right] {$i$};
\end{tikzpicture}
```

---

### Lớp 11–12: Quang Học

---

#### Mẫu V11 — Thấu kính hội tụ: tia tới, ảnh thật

**Lớp áp dụng:** 11  
**Kết quả:** Thấu kính hội tụ, vật AB ở ngoài tiêu cự, 3 tia đặc biệt, ảnh thật ngược chiều A'B'.

```latex
% ===== V11: Thấu kính hội tụ — ảnh thật =====
% Tham số: f=2 (tiêu cự), d=3.5 (khoảng cách vật)
% Công thức: 1/d' = 1/f - 1/d
\begin{tikzpicture}[line width=0.9pt, font=\small, >=Stealth]
  \def\f{2}    % tiêu cự
  \def\d{3.5}  % khoảng vật
  % d' = d*f/(d-f)
  \pgfmathsetmacro{\dp}{\d*\f/(\d-\f)}

  % Trục chính
  \draw[->] (-5,0) -- (5.5,0) node[right] {trục chính};
  % Thấu kính (đường thẳng đứng + mũi tên hai chiều)
  \draw[very thick, <->] (0,-2.3) -- (0,2.3);
  \node[above right] at (0,2.3) {$L$};

  % Tiêu điểm F và F'
  \fill[blue] (\f,0) circle (2pt) node[below] {$F'$};
  \fill[blue] (-\f,0) circle (2pt) node[below] {$F$};

  % Vật AB (mũi tên hướng lên)
  \draw[->, very thick, green!60!black] (-\d,0) -- (-\d,1.5);
  \node[left] at (-\d,0.75) {$A$};
  \node[above left] at (-\d,1.5) {$B$};

  % Ảnh A'B' (ngược chiều — mũi tên hướng xuống)
  \draw[->, very thick, red] (\dp,0) -- (\dp,{-1.5*\dp/(\d-\dp)*(\d-\f)/\f});
  \node[right] at (\dp,-0.5) {$B'$};

  % Tia 1: song song trục → qua F'
  \draw[orange] (-\d,1.5) -- (0,1.5) -- (\f,0);
  % Tia 2: qua quang tâm O → thẳng
  \draw[orange] (-\d,1.5) -- (\dp,{-1.5*\dp/(\d-\dp)*(\d-\f)/\f});
  % Tia 3: qua F → song song trục
  \draw[orange] (-\d,1.5) -- (-\f,0) -- (0,{1.5*\f/\d}) -- (\dp,{1.5*\f/\d});

  \node at (0,-3) {\small $f=\f$cm,\; $d=\d$cm,\; $d'=\pgfmathprintnumber[fixed,precision=1]{\dp}$cm};
\end{tikzpicture}
```

---

#### Mẫu V12 — Thấu kính phân kỳ: ảnh ảo

**Lớp áp dụng:** 11  
**Kết quả:** Thấu kính phân kỳ, 3 tia đặc biệt, ảnh ảo cùng chiều nhỏ hơn vật.

```latex
% ===== V12: Thấu kính phân kỳ — ảnh ảo =====
% Tham số: f=-2 (tiêu cự âm), d=3 (khoảng vật)
\begin{tikzpicture}[line width=0.9pt, font=\small, >=Stealth]
  \def\f{2}    % |f| = 2, thấu kính phân kỳ f = -2
  \def\d{3}

  % Trục chính
  \draw[->] (-4.5,0) -- (4,0) node[right] {trục chính};

  % Thấu kính phân kỳ (mũi tên ngược vào trong)
  \draw[very thick] (0,-2) -- (0,2);
  \draw[{<[scale=1.5]}-{>[scale=1.5]}, very thick] (0,-2.1) -- (0,2.1)
      node[above right] {$L$};

  % Tiêu điểm (phân kỳ: F ở cùng phía vật)
  \fill[blue] (-\f,0) circle (2pt) node[below] {$F'$};  % ảo, cùng phía vật
  \fill[blue] (\f,0)  circle (2pt) node[below] {$F$};

  % Vật AB
  \draw[->, very thick, green!60!black] (-\d,0) -- (-\d,1.4);
  \node[above left] at (-\d,1.4) {$B$};

  % d' = d*f/(d+f)  [f âm, công thức phân kỳ]
  \pgfmathsetmacro{\dp}{\d*\f/(\d+\f)}  % d' dương nhưng ảnh ảo bên vật

  % Ảnh A'B' (cùng chiều, nhỏ hơn, cùng phía với vật — bên trái)
  \draw[->, very thick, red] (-\dp,0) -- (-\dp,{1.4*\dp/\d});
  \node[right] at (-\dp,{0.7*\dp/\d}) {$B'$};

  % Tia 1: song song trục → như xuất phát từ F'
  \draw[orange]        (-\d,1.4) -- (0,1.4);
  \draw[orange,dashed] (0,1.4) -- (2,{1.4-2*(1.4+\f)/\f*0.3}); % kéo dài
  \draw[orange]        (0,1.4) -- (-\f,0);   % nối về F'

  % Tia 2: qua O (thẳng)
  \draw[orange] (-\d,1.4) -- (2,{-1.4/\d*2});

  \node at (0,-2.8) {\small Thấu kính phân kỳ: ảnh ảo, cùng chiều, nhỏ hơn vật};
\end{tikzpicture}
```

---

#### Mẫu V13 — Gương cầu lõm: tiêu điểm F và tâm C

**Lớp áp dụng:** 11  
**Kết quả:** Gương cầu lõm, tiêu điểm F, tâm cầu C, vật AB, tia phản xạ, ảnh.

```latex
% ===== V13: Gương cầu lõm =====
\begin{tikzpicture}[line width=0.9pt, font=\small, >=Stealth]
  \def\R{3}   % bán kính cong (cm)

  % Trục chính
  \draw[->] (-0.5,0) -- (6,0) node[right] {trục chính};

  % Gương cầu lõm (vẽ cung tròn)
  \draw[very thick] ({3+\R*cos(160)}:{0}) arc (160:200:\R)
       [shift={(\R,0)}];
  % Đơn giản hơn: vẽ thẳng
  \draw[very thick, line width=2pt] (5.5,-2) arc (200:160:3) ;

  % Tiêu điểm F và tâm cầu C
  \pgfmathsetmacro{\FC}{\R/2}
  \fill[blue] (\FC,0) circle (2pt) node[below] {$F$};
  \fill[red]  (\R,0)  circle (2pt) node[below] {$C$};

  % Đỉnh gương I
  \fill (0,0) circle (2pt) node[below left] {$I$};

  % Vật AB (ngoài C)
  \draw[->, very thick, green!60!black] (4.2,0) -- (4.2,1.5) node[above] {$B$};
  \node[below] at (4.2,0) {$A$};

  \node at (3,-2.5) {\small Gương cầu lõm: $F=\R/2$cm, $C=\R$cm};
\end{tikzpicture}
```

---

#### Mẫu V14 — Lăng kính với tia sáng tán sắc

**Lớp áp dụng:** 11  
**Kết quả:** Lăng kính tam giác, tia trắng vào, tán sắc thành đỏ-tím ở mặt ra.

```latex
% ===== V14: Lăng kính tán sắc ánh sáng =====
\begin{tikzpicture}[line width=0.9pt, font=\small, >=Stealth]
  % Lăng kính (tam giác)
  \coordinate (A) at (2,3.5);
  \coordinate (B) at (0,0);
  \coordinate (C) at (4,0);
  \fill[cyan!10] (A) -- (B) -- (C) -- cycle;
  \draw[very thick] (A) -- (B) -- (C) -- cycle;
  \node[above] at (A) {$A$};

  % Tia tới (từ bên trái, chiếu vào mặt AB)
  \draw[->, thick, white!50!gray] (-1.5,1.8) -- (0.8,1.2)
        node[above, pos=0.5] {\small tia trắng};

  % Điểm vào mặt AB (tia khúc xạ vào trong)
  \coordinate (I) at (0.8,1.2);
  \draw[thick, gray] (I) -- (2.8,0.5);  % tia trong lăng kính

  % Điểm ra mặt BC — tia tán sắc
  \coordinate (J) at (2.8,0.5);
  % Tia đỏ (lệch ít hơn)
  \draw[->, thick, red]    (J) -- ++(1.5,-0.3) node[right] {\small đỏ};
  % Tia cam
  \draw[->, thick, orange] (J) -- ++(1.5,-0.5);
  % Tia vàng
  \draw[->, thick, yellow!80!black] (J) -- ++(1.5,-0.7);
  % Tia xanh lục
  \draw[->, thick, green!70!black] (J) -- ++(1.5,-0.9);
  % Tia tím (lệch nhiều nhất)
  \draw[->, thick, violet]  (J) -- ++(1.5,-1.1) node[right] {\small tím};

  % Pháp tuyến tại I và J (dashed)
  \draw[dashed, line width=0.6pt] ($(I)+(-0.5,1)$) -- ($(I)+(0.5,-1)$);
  \draw[dashed, line width=0.6pt] ($(J)+(-0.5,1)$) -- ($(J)+(0.5,-1)$);
\end{tikzpicture}
```

---

#### Mẫu V15 — Đồ thị dao động điều hòa x = A·cos(ωt + φ)

**Lớp áp dụng:** 12  
**Kết quả:** Đồ thị $x(t) = A\cos(\omega t)$ theo thời gian, biên độ A, chu kỳ T.

```latex
% ===== V15: Đồ thị dao động điều hòa =====
% Tham số: A=2 (biên độ), T=4 (chu kỳ), đổi hàm sin/cos
\begin{tikzpicture}[font=\small]
\begin{axis}[
  width=10cm, height=5cm,
  axis lines=center,
  xlabel={$t$ (s)}, ylabel={$x$ (cm)},
  xlabel style={right},
  ylabel style={above},
  xmin=-0.3, xmax=5,
  ymin=-2.8, ymax=2.8,
  xtick={0,1,2,3,4},
  xticklabels={$0$,$\frac{T}{4}$,$\frac{T}{2}$,$\frac{3T}{4}$,$T$},
  ytick={-2,0,2},
  yticklabels={$-A$,$0$,$A$},
  tick label style={font=\small},
  samples=200,
]
  % x = 2*cos(2*pi/4 * t) = 2*cos(pi/2 * t)  với T=4
  \addplot[blue, thick, domain=0:5] {2*cos(deg(3.14159/2*x))};
  \node[blue] at (axis cs:4.5,2.2) {$x=A\cos\omega t$};

  % Đường biên độ
  \draw[red, dashed, line width=0.7pt] (axis cs:0,2)  -- (axis cs:5,2);
  \draw[red, dashed, line width=0.7pt] (axis cs:0,-2) -- (axis cs:5,-2);
\end{axis}
\end{tikzpicture}
```

---

#### Mẫu V16 — Đồ thị phân tích lực trên mặt phẳng nghiêng (vectơ)

**Lớp áp dụng:** 10  
**Kết quả:** Vật trên mặt phẳng nghiêng góc α, phân tích $\vec{P}$ thành $P_x \parallel$ mặt và $P_y \perp$ mặt.

```latex
% ===== V16: Phân tích trọng lực trên mặt phẳng nghiêng =====
\begin{tikzpicture}[line width=0.9pt, font=\small, >=Stealth]
  \def\ang{37}

  % Mặt phẳng nghiêng
  \draw[very thick] (0,0) -- ({5*cos(\ang)},{5*sin(\ang)});
  \draw[very thick] (0,0) -- (5,0);
  \draw ({0.8*cos(0)}:0.8) arc (0:\ang:0.8);
  \node at ({1*cos(\ang/2)},{1*sin(\ang/2)}) {$\alpha$};

  % Vật (hình chữ nhật nghiêng)
  \begin{scope}[rotate=\ang, shift={(2.2,0)}]
    \fill[gray!25] (0,0) rectangle (0.9,0.65);
    \draw (0,0) rectangle (0.9,0.65);
  \end{scope}

  % Điểm đặt (tâm vật)
  \coordinate (G) at ({2.2*cos(\ang)+0.45*cos(\ang)-0.325*sin(\ang)},
                       {2.2*sin(\ang)+0.45*sin(\ang)+0.325*cos(\ang)});

  % Vectơ P (thẳng đứng xuống)
  \draw[->, very thick, blue]   (G) -- ++(0,-2.2) node[below] {$\vec{P}$};

  % Thành phần Px (song song mặt, hướng xuống dốc)
  \draw[->, thick, red]  (G) -- ++({-1.4*cos(\ang)},{-1.4*sin(\ang)})
        node[left, pos=1] {$P_x{=}P\sin\alpha$};

  % Thành phần Py (vuông góc mặt, hướng vào mặt phẳng)
  \draw[->, thick, orange] (G) -- ++({1.75*sin(\ang)},{-1.75*cos(\ang)})
        node[right, pos=1] {$P_y{=}P\cos\alpha$};

  % Đường kẻ phụ (dashed)
  \draw[dashed, line width=0.6pt] (G) -- ++(0,-1.75);
  \draw[dashed, line width=0.6pt] (G) -- ++({-1.4*cos(\ang)},{-1.4*sin(\ang)});
\end{tikzpicture}
```

---

## MÔN HÓA HỌC

### Công Thức Cấu Tạo (chemfig)

---

#### Mẫu H01 — Axit acetic CH3COOH

**Lớp áp dụng:** 9–11  
**Kết quả:** Công thức cấu tạo axit acetic (axit axetic) dạng khai triển.

```latex
% ===== H01: Axit acetic CH3COOH =====
\begin{tikzpicture}
  \chemfig{
    H-[2]C(-[4]H)(-[6]H)-C(=[2]O)-[0]O-H
  }
\end{tikzpicture}
```

---

#### Mẫu H02 — Benzene C6H6 (vòng thơm)

**Lớp áp dụng:** 11–12  
**Kết quả:** Vòng benzene với liên kết đôi xen kẽ (Kekulé) hoặc vòng tròn bên trong.

```latex
% ===== H02: Benzene — cấu tạo Kekulé =====
\begin{tikzpicture}
  % Dạng Kekulé (liên kết đôi xen kẽ)
  \chemfig{*6(-=-=-=)}
\end{tikzpicture}
```

```latex
% ===== H02b: Benzene — dạng vòng tròn (delocalized) =====
\begin{tikzpicture}
  \chemfig{**6(------)}
\end{tikzpicture}
```

---

#### Mẫu H03 — Glucose C6H12O6 (mạch thẳng Fischer)

**Lớp áp dụng:** 12  
**Kết quả:** Công thức cấu tạo glucose dạng mạch hở Fischer.

```latex
% ===== H03: Glucose mạch hở (rút gọn) =====
\begin{tikzpicture}
  \chemfig{
    CH_2OH-[2]CHOH-[2]CHOH-[2]CHOH-[2]CHOH-[2]CHO
  }
\end{tikzpicture}
```

---

#### Mẫu H04 — Ethanol C2H5OH

**Lớp áp dụng:** 9–11  
**Kết quả:** Công thức cấu tạo ethanol khai triển đầy đủ.

```latex
% ===== H04: Ethanol C2H5OH =====
\begin{tikzpicture}
  \chemfig{
    H-C(-[2]H)(-[6]H)-C(-[2]H)(-[6]H)-O-H
  }
\end{tikzpicture}
```

---

#### Mẫu H05 — Axit sulfuric H2SO4

**Lớp áp dụng:** 10–11  
**Kết quả:** Công thức cấu tạo H2SO4 với liên kết đôi S=O và S-OH.

```latex
% ===== H05: Axit sulfuric H2SO4 =====
\begin{tikzpicture}
  \chemfig{
    HO-S(=[2]O)(=[6]O)-OH
  }
\end{tikzpicture}
```

---

#### Mẫu H06 — Methane CH4

**Lớp áp dụng:** 9  
**Kết quả:** Công thức cấu tạo methane (4 liên kết C-H).

```latex
% ===== H06: Methane CH4 =====
\begin{tikzpicture}
  \chemfig{
    H-C(-[2]H)(-[4]H)-[6]H
  }
\end{tikzpicture}
```

---

#### Mẫu H07 — Ethylene (Ethene) CH2=CH2

**Lớp áp dụng:** 11  
**Kết quả:** Công thức cấu tạo ethylene với liên kết đôi C=C.

```latex
% ===== H07: Ethylene CH2=CH2 =====
\begin{tikzpicture}
  \chemfig{
    H-[2]C(-[4]H)=C(-[0]H)-[6]H
  }
\end{tikzpicture}
```

---

#### Mẫu H08 — Acetylene (Ethyne) CH≡CH

**Lớp áp dụng:** 11  
**Kết quả:** Liên kết ba C≡C.

```latex
% ===== H08: Acetylene CH≡CH =====
\begin{tikzpicture}
  \chemfig{
    H-C~C-H
  }
\end{tikzpicture}
```

---

### Sơ Đồ Thí Nghiệm Hóa Học

---

#### Mẫu H09 — Điều chế khí CO2 (HCl + CaCO3)

**Lớp áp dụng:** 9  
**Kết quả:** Bình tam giác chứa CaCO3 + HCl, ống dẫn khí CO2 sang bình nước vôi trong.

```latex
% ===== H09: Điều chế CO2 từ CaCO3 + HCl =====
\begin{tikzpicture}[line width=0.9pt, font=\small]
  %% --- Bình phát sinh (erlenmeyer) ---
  \begin{scope}[xshift=0cm]
    % Thân bình (hình thang ngược + cổ)
    \draw[fill=cyan!10]
      (0.3,2.2) -- (0.3,2.7) -- (0.7,2.7) -- (0.7,2.2)  % cổ bình
      -- (1.5,0.2) -- (-0.5,0.2) -- (0.3,2.2);            % thân
    \draw (0.2,2.2) -- (0.2,2.7) -- (0.8,2.7) -- (0.8,2.2);
    % Nút cao su (hình chữ nhật tối)
    \fill[gray!60] (0.2,2.65) rectangle (0.8,2.95);
    \node at (0.5,1.2) {\small $CaCO_3$};
    \node at (0.5,0.7) {\small $+HCl$};
    % Bong bóng khí
    \fill[cyan!30] (0.4,1.8) circle (0.12);
    \fill[cyan!30] (0.7,1.6) circle (0.09);
  \end{scope}

  %% --- Ống dẫn khí ---
  \draw[very thick] (0.5,2.95) -- (0.5,3.5) -- (3.5,3.5) -- (3.5,2.3);

  %% --- Bình thu khí / nước vôi trong ---
  \begin{scope}[xshift=3cm]
    \draw[fill=yellow!10]
      (0.2,2.2) -- (0.2,2.7) -- (0.8,2.7) -- (0.8,2.2)
      -- (1.5,0.2) -- (-0.5,0.2) -- (0.2,2.2);
    \fill[gray!60] (0.2,2.65) rectangle (0.8,2.95);
    % Nước vôi trong (màu trắng đục một phần)
    \fill[gray!20] (-0.3,0.2) rectangle (1.3,1.0);
    \node at (0.5,0.6) {\small $Ca(OH)_2$};
    \node at (0.5,1.4) {\small $CO_2$};
  \end{scope}

  % Nhãn
  \node[below] at (0.5,0.1) {\small Bình phát sinh};
  \node[below] at (3.5,0.1) {\small Bình thu};
\end{tikzpicture}
```

---

#### Mẫu H10 — Bình điện phân dung dịch NaCl

**Lớp áp dụng:** 12  
**Kết quả:** Bình điện phân với catot (-) và anot (+), dung dịch NaCl, điện cực nhúng chìm, bong bóng khí.

```latex
% ===== H10: Bình điện phân NaCl =====
\begin{tikzpicture}[line width=0.9pt, font=\small, >=Stealth]
  % Bình điện phân (hình chữ nhật)
  \draw[very thick, fill=blue!5] (-2,-1.5) rectangle (2,2);

  % Dung dịch NaCl (màu nhạt)
  \fill[blue!15] (-2,-1.5) rectangle (2,0.5);
  \node at (0,-0.5) {Dung dịch $NaCl$};

  % Catot (cực âm, bên trái) — thép không gỉ
  \fill[gray!60] (-1,-1.3) rectangle (-0.7,1.5);
  \draw (-1,-1.3) rectangle (-0.7,1.5);
  \node[above] at (-0.85,1.5) {\small Catot (−)};
  % Bong bóng H2 ở catot
  \fill[cyan!40] (-0.85,0.7) circle (0.12);
  \fill[cyan!40] (-0.85,0.3) circle (0.09);
  \node[left, xshift=-5pt] at (-1,0.5) {\small $H_2\uparrow$};

  % Anot (cực dương, bên phải) — than graphite
  \fill[black!50] (0.7,-1.3) rectangle (1,1.5);
  \draw (0.7,-1.3) rectangle (1,1.5);
  \node[above] at (0.85,1.5) {\small Anot (+)};
  % Bong bóng Cl2 ở anot
  \fill[yellow!60] (0.85,0.7) circle (0.12);
  \fill[yellow!60] (0.85,0.3) circle (0.09);
  \node[right, xshift=3pt] at (1,0.5) {\small $Cl_2\uparrow$};

  % Dây dẫn và nguồn điện
  \draw[very thick] (-0.85,1.5) -- (-0.85,2.8) -- (-1.5,2.8);
  \draw[very thick] (0.85,1.5)  -- (0.85,2.8)  -- (1.5,2.8);
  % Nguồn (pin)
  \draw[very thick] (-1.5,2.5) -- (-1.5,3.1);
  \draw[very thick, line width=3pt] (-1.8,2.7) -- (-1.2,2.7);  % cực dài (-)
  \draw[very thick, line width=5pt] (-1.8,2.9) -- (-1.2,2.9);  % cực ngắn (+)
  \draw[very thick] (1.5,2.5) -- (1.5,3.1);
  \node[above] at (0,3.0) {Nguồn điện một chiều};
\end{tikzpicture}
```

---

#### Mẫu H11 — Sơ đồ chưng cất (chưng cất rượu)

**Lớp áp dụng:** 9  
**Kết quả:** Bình chưng cất, ống sinh hàn, bình hứng.

```latex
% ===== H11: Chưng cất đơn giản =====
\begin{tikzpicture}[line width=0.9pt, font=\small,
    decoration={coil, amplitude=3pt, segment length=5pt}]
  %% Bình chưng cất (bình tròn)
  \draw[fill=orange!10] (0,0) circle (1);
  \draw[fill=orange!20] (-0.7,-0.8) arc(200:340:1) -- cycle;  % dung dịch
  \node at (0,-0.3) {\small hỗn hợp};

  % Cổ bình
  \draw[fill=gray!20] (-0.15,0.95) -- (-0.15,2) -- (0.15,2) -- (0.15,0.95);

  % Nhiệt kế
  \draw[very thick, red] (0,1.5) -- (0,2.8);
  \fill[red] (0,2.8) circle (3pt);
  \node[right] at (0.1,2.5) {\small nhiệt kế};

  % Ống nghiêng
  \draw[thick] (0.15,1.8) -- (3,1);
  \draw[thick] (0.15,2.0) -- (3,1.2);

  % Ống sinh hàn (cuộn xoắn trong vỏ nước)
  \draw[fill=cyan!20] (2.8,0.2) rectangle (4.5,1.4);
  \draw[decorate, thick] (2.9,1.2) -- (4.4,0.4);
  \node at (3.65,0.85) {\tiny nước làm lạnh};

  % Ống ra
  \draw[thick] (4.4,0.5) -- (5,0.2);
  \draw[thick] (4.4,0.7) -- (5,0.4);

  % Bình hứng
  \draw[fill=cyan!10] (4.8,-0.5) -- (4.8,0.3) -- (5.4,0.3) -- (5.4,-0.5) -- cycle;
  \node at (5.1,-0.1) {\small rượu};

  % Đèn cồn
  \fill[yellow!60] (-0.3,-1.5) -- (0.3,-1.5) -- (0.2,-1.2) -- (-0.2,-1.2) -- cycle;
  \draw (-0.4,-1.7) rectangle (0.4,-1.5);
  \node[below] at (0,-1.7) {\small đèn cồn};
\end{tikzpicture}
```

---

#### Mẫu H12 — Nhận biết khí SO2 qua nước brom

**Lớp áp dụng:** 10–11  
**Kết quả:** Khí SO2 sục qua dung dịch nước brom, làm mất màu.

```latex
% ===== H12: Nhận biết SO2 (mất màu nước brom) =====
\begin{tikzpicture}[line width=0.9pt, font=\small]
  %% Bình phát sinh SO2
  \draw[fill=gray!10] (-3.5,-1) rectangle (-1.5,1.5);
  \fill[yellow!20] (-3.5,-1) rectangle (-1.5,0.3);
  \node at (-2.5,-0.3) {\small $Na_2SO_3$+$H_2SO_4$};
  \node[above] at (-2.5,1.5) {\small Bình phát sinh};
  % Nút cao su + ống
  \fill[gray!50] (-2.7,1.4) rectangle (-2.3,1.7);
  \draw[thick] (-2.5,1.7) -- (-2.5,2.2) -- (0,2.2);

  %% Bình nước brom
  \draw[fill=orange!5] (-0.5,-1) rectangle (1.5,1.5);
  \fill[orange!30] (-0.5,-1) rectangle (1.5,0.2);
  \node at (0.5,-0.4) {\small nước brom};
  \node[above] at (0.5,1.5) {\small (vàng cam)};
  \fill[gray!50] (-0.2,1.4) rectangle (0.2,1.7);
  \draw[thick] (0,1.7) -- (0,2.2);
  \draw[thick] (0,2.2) -- (0,-0.8);  % ống sục vào dung dịch

  % Mũi tên khí
  \draw[->, thick, yellow!60!black] (-2.5,2.2) -- (0,2.2);
  \node[above] at (-1.2,2.2) {\small $SO_2$};

  % Kết quả
  \node[below, text=orange!80!black] at (0.5,-1.1) {\small mất màu};
\end{tikzpicture}
```

---

## PHỤ LỤC — Mẫu Bổ Sung

---

#### Mẫu P01 — Đồ thị hàm bậc ba (lớp 12)

**Lớp áp dụng:** 12  
**Kết quả:** Đồ thị $y = x^3 - 3x + 2$ với cực đại, cực tiểu.

```latex
% ===== P01: Đồ thị hàm bậc ba y=x^3-3x+2 =====
\begin{tikzpicture}[font=\small]
\begin{axis}[
  width=7cm, height=6cm,
  axis lines=center,
  xlabel={$x$}, ylabel={$y$},
  xmin=-2.5, xmax=3,
  ymin=-2, ymax=5,
  samples=100,
  grid=both, grid style={gray!15},
]
  \addplot[blue, thick, domain=-2.2:2.5] {x^3 - 3*x + 2};

  % Cực đại tại x=-1, y=4
  \addplot[mark=*, red, mark size=2pt] coordinates {(-1,4)};
  \node[red, left] at (axis cs:-1,4) {CĐ$(-1;\,4)$};

  % Cực tiểu tại x=1, y=0
  \addplot[mark=*, orange, mark size=2pt] coordinates {(1,0)};
  \node[orange, right] at (axis cs:1,0) {CT$(1;\,0)$};

  \node[blue, right] at (axis cs:2,4) {$y=x^3-3x+2$};
\end{axis}
\end{tikzpicture}
```

---

#### Mẫu P02 — Đồ thị hàm logarithm (lớp 12)

**Lớp áp dụng:** 12  
**Kết quả:** Đồ thị $y = \log_2 x$ và $y = \log_{0.5} x$ so sánh.

```latex
% ===== P02: Đồ thị hàm logarithm =====
\begin{tikzpicture}[font=\small]
\begin{axis}[
  width=7cm, height=6cm,
  axis lines=center,
  xlabel={$x$}, ylabel={$y$},
  xmin=-0.3, xmax=5,
  ymin=-3, ymax=3,
  samples=100,
]
  % log base 2: ln(x)/ln(2)
  \addplot[blue, thick, domain=0.05:5] {ln(x)/ln(2)};
  \node[blue, right] at (axis cs:4,2) {$y=\log_2 x$};

  % log base 0.5: ln(x)/ln(0.5)
  \addplot[red, thick, dashed, domain=0.05:5] {ln(x)/ln(0.5)};
  \node[red, right] at (axis cs:4,-2) {$y=\log_{0.5} x$};

  % Giao trục: x=1, y=0
  \addplot[mark=*, black, mark size=2pt] coordinates {(1,0)};
\end{axis}
\end{tikzpicture}
```

---

#### Mẫu P03 — Bảng biến thiên hàm phân thức (lớp 12)

**Lớp áp dụng:** 12  
**Kết quả:** Bảng biến thiên cho $f(x) = \dfrac{x+1}{x-1}$ (hàm nhất biến).

```latex
% ===== P03: Bảng biến thiên hàm phân thức y=(x+1)/(x-1) =====
\begin{tikzpicture}
\tkzTabInit[lgt=2.5, espcl=3]{
  $x$     / 1,
  $f'(x)$ / 1,
  $f(x)$  / 2.2
}{$-\infty$, $1$, $+\infty$}

\tkzTabLine{, -, d, -, }

\tkzTabVar{
  +/ $+\infty$,
  +D-/ $+\infty$ / $-\infty$,
  +/ $+\infty$
}
\end{tikzpicture}
```

---

#### Mẫu P04 — Lực Coulomb (hai điện tích điểm)

**Lớp áp dụng:** 11  
**Kết quả:** Hai điện tích q1(+) và q2(-) cách nhau r, lực hút Coulomb.

```latex
% ===== P04: Lực Coulomb giữa hai điện tích =====
\begin{tikzpicture}[line width=0.9pt, font=\small, >=Stealth]
  % Điện tích q1 (+)
  \fill[red!20] (0,0) circle (0.35);
  \draw[red, thick] (0,0) circle (0.35);
  \node at (0,0) {$+q_1$};

  % Điện tích q2 (-)
  \fill[blue!20] (4,0) circle (0.35);
  \draw[blue, thick] (4,0) circle (0.35);
  \node at (4,0) {$-q_2$};

  % Khoảng cách r
  \draw[<->, gray] (0,-0.7) -- (4,-0.7) node[midway, below] {$r$};

  % Lực hút (hướng vào nhau)
  \draw[->, thick, red]  (0.35,0.3)  -- (1.5,0.3)  node[above, midway] {$\vec{F}_{12}$};
  \draw[->, thick, blue] (3.65,0.3) -- (2.5,0.3)  node[above, midway] {$\vec{F}_{21}$};

  % Công thức
  \node[below] at (2,-1.2) {$F = k\dfrac{|q_1||q_2|}{r^2}$};
\end{tikzpicture}
```

---

#### Mẫu P05 — Sóng ngang biểu diễn tại t=0

**Lớp áp dụng:** 12  
**Kết quả:** Hình vẽ sóng cơ học tại thời điểm $t=0$: bước sóng λ, biên độ A.

```latex
% ===== P05: Sóng ngang (snapshot tại t=0) =====
\begin{tikzpicture}[font=\small]
\begin{axis}[
  width=10cm, height=5cm,
  axis lines=center,
  xlabel={$x$ (m)}, ylabel={$u$ (cm)},
  xmin=-0.3, xmax=5.5,
  ymin=-2.8, ymax=3.2,
  xtick={0,1,2,3,4,5},
  ytick={-2,0,2},
  yticklabels={$-A$,$0$,$A$},
  samples=200,
]
  % Hình sin: bước sóng lambda = 2 (m)
  \addplot[blue, thick, domain=0:5.2] {2*sin(deg(3.14159*x))};

  % Đánh dấu bước sóng lambda
  \draw[<->, red, thick] (axis cs:0,2.5) -- (axis cs:2,2.5)
        node[midway, above] {$\lambda$};

  % Mũi tên hướng lan truyền
  \draw[->, thick, green!60!black] (axis cs:4.5,2) -- (axis cs:5.3,2)
        node[right] {$v$};
\end{axis}
\end{tikzpicture}
```

---

#### Mẫu P06 — Gương phẳng: tia phản xạ (định luật phản xạ)

**Lớp áp dụng:** 7–11  
**Kết quả:** Gương phẳng, pháp tuyến N, tia tới, tia phản xạ, góc tới $i$ = góc phản xạ $i'$.

```latex
% ===== P06: Định luật phản xạ gương phẳng =====
\begin{tikzpicture}[line width=0.9pt, font=\small, >=Stealth]
  % Gương phẳng (nằm ngang)
  \draw[very thick] (-3,0) -- (3,0);
  \fill[pattern=north east lines, pattern color=gray] (-3,-0.3) rectangle (3,0);

  % Pháp tuyến
  \draw[dashed, line width=0.7pt] (0,-1) -- (0,3) node[above] {$N$};

  % Tia tới (từ trên trái, hướng xuống)
  \draw[->, thick, blue] (-2.5,2.5) -- (0,0) node[midway, above right] {\small tia tới};

  % Tia phản xạ (đối xứng qua pháp tuyến)
  \draw[->, thick, red] (0,0) -- (2.5,2.5) node[midway, above left] {\small tia phản xạ};

  % Góc tới i và góc phản xạ i'
  \draw[blue]  ({0.8*cos(135)}:{0.8}) arc (135:90:0.8);
  \node[blue, above left]  at ({0.6*cos(112)},{0.6*sin(112)}) {$i$};

  \draw[red]   ({0.8*cos(90)}:{0.8}) arc (90:45:0.8);
  \node[red, above right]  at ({0.6*cos(68)},{0.6*sin(68)}) {$i'$};

  \node[below] at (0,-0.5) {\small $i = i'$ (Định luật phản xạ)};
\end{tikzpicture}
```

---

#### Mẫu P07 — Chu kỳ tuần hoàn (đồng hồ / chu kỳ dao động)

**Lớp áp dụng:** 12  
**Kết quả:** Đồng hồ con lắc đơn với dây treo, vị trí cân bằng và biên.

```latex
% ===== P07: Con lắc đơn =====
% Tham số: \L = chiều dài dây, \ang = góc biên
\begin{tikzpicture}[line width=0.9pt, font=\small, >=Stealth]
  \def\L{3}
  \def\angMax{25}   % góc biên (độ)

  % Trần nhà (gắn con lắc)
  \fill[pattern=north east lines, pattern color=gray] (-1.5,0.3) rectangle (1.5,0.6);
  \draw[very thick] (-1.5,0.3) -- (1.5,0.3);

  % Điểm treo
  \fill (0,0.3) circle (2pt);

  % Vị trí cân bằng (thẳng đứng)
  \draw[dashed, line width=0.6pt, gray] (0,0.3) -- (0,{0.3-\L-0.4});

  % Con lắc ở vị trí biên phải
  \coordinate (ball) at ({(\L)*sin(\angMax)},{0.3-(\L)*cos(\angMax)});
  \draw[thick] (0,0.3) -- (ball);
  \fill[red!60] (ball) circle (0.3);
  \node[right, xshift=5pt] at (ball) {$m$};

  % Con lắc ở vị trí biên trái (dashed)
  \coordinate (ballL) at ({-(\L)*sin(\angMax)},{0.3-(\L)*cos(\angMax)});
  \draw[dashed, line width=0.7pt] (0,0.3) -- (ballL);
  \fill[red!20] (ballL) circle (0.3);

  % Cung dao động
  \draw[<->, blue] (ballL) arc ({180+\angMax}:{-\angMax}:\L)
                            [shift={(0,0.3)}];

  % Góc alpha
  \draw[orange] ({0.8*sin(\angMax/2)},{0.3-0.8*cos(\angMax/2)}) arc
       ({270-\angMax/2}:{270+0}:0.8) [shift={(0,0.3)}];
  \node[orange, right] at ({0.5*sin(\angMax/2)},{0.3-0.9}) {$\alpha_0$};

  % Nhãn chiều dài dây
  \node[right, xshift=3pt] at ({0.5*(\L)*sin(\angMax)},{0.3-0.5*(\L)*cos(\angMax)})
       {$l$};
\end{tikzpicture}
```

---

#### Mẫu P08 — Khúc xạ ánh sáng tại mặt phân cách

**Lớp áp dụng:** 11  
**Kết quả:** Tia sáng qua mặt phân cách hai môi trường, góc tới $i$ và góc khúc xạ $r$, pháp tuyến.

```latex
% ===== P08: Khúc xạ ánh sáng =====
\begin{tikzpicture}[line width=0.9pt, font=\small, >=Stealth]
  % Mặt phân cách
  \draw[very thick] (-3,0) -- (3,0);

  % Môi trường 1 (trên) và môi trường 2 (dưới)
  \fill[cyan!5]  (-3,0) rectangle (3,3);
  \fill[blue!8]  (-3,-2.5) rectangle (3,0);
  \node[right] at (2.5,2)  {Môi trường 1 ($n_1$)};
  \node[right] at (2.5,-2) {Môi trường 2 ($n_2>n_1$)};

  % Pháp tuyến
  \draw[dashed, line width=0.7pt] (0,-2.5) -- (0,3) node[above] {$N$};

  % Tia tới (từ trên)
  \draw[->, thick, blue] (-2.5,2.5) -- (0,0);
  \node[blue, above] at (-1.8,2) {\small tia tới};

  % Góc tới i
  \draw[blue] (0,0.9) arc (90:135:0.9);
  \node[blue, above left] at (-0.3,0.7) {$i$};

  % Tia khúc xạ (lệch về pháp tuyến vì n2>n1)
  \draw[->, thick, red] (0,0) -- (1.5,-2.5);
  \node[red, right] at (1,-2) {\small tia khúc xạ};

  % Góc khúc xạ r (nhỏ hơn i)
  \draw[red] (0,-0.9) arc (270:300:0.9);
  \node[red, below right] at (0.3,-0.7) {$r$};

  % Tia phản xạ (đối xứng tia tới)
  \draw[->, thick, gray, dashed] (0,0) -- (2.5,2.5);
  \node[gray] at (2,1.5) {\small tia p.xạ};

  % Định luật Snell
  \node[below] at (0,-3) {\small $n_1\sin i = n_2\sin r$ (Snell)};
\end{tikzpicture}
```

---

#### Mẫu P09 — Đồ thị U-I (đặc tính V-A) điện trở

**Lớp áp dụng:** 9–11  
**Kết quả:** Đồ thị $U = f(I)$ tuyến tính (đường thẳng qua gốc), dốc = $R$.

```latex
% ===== P09: Đồ thị U-I đặc tính V-A =====
\begin{tikzpicture}[font=\small]
\begin{axis}[
  width=7cm, height=6cm,
  axis lines=left,
  xlabel={$I$ (A)}, ylabel={$U$ (V)},
  xmin=0, xmax=3.5, ymin=0, ymax=12,
  xtick={0,0.5,1,1.5,2,2.5,3},
  ytick={0,2,4,6,8,10},
  grid=both, grid style={gray!20},
]
  % U = R*I = 3*I (R=3 Ohm) — thay đổi hệ số góc
  \addplot[blue, thick, domain=0:3.3] {3*x};

  % Đánh dấu điểm (2A, 6V)
  \addplot[mark=*, red, mark size=2.5pt] coordinates {(2,6)};
  \draw[dashed, red, line width=0.7pt]
       (axis cs:2,0) -- (axis cs:2,6) -- (axis cs:0,6);
  \node[red, right] at (axis cs:2,6) {\small$(2;\,6)$};

  % Nhãn độ dốc R
  \node[blue, rotate=54] at (axis cs:1.5,6.5) {\small $\tan\alpha = R = 3\,\Omega$};
\end{axis}
\end{tikzpicture}
```

---

#### Mẫu P10 — Hình hộp chữ nhật (lớp 8-11)

**Lớp áp dụng:** 8–12  
**Kết quả:** Hình hộp chữ nhật ABCD.A'B'C'D' với kích thước a, b, c.

```latex
% ===== P10: Hình hộp chữ nhật =====
% Tham số: \a=chiều dài, \b=chiều rộng, \c=chiều cao
\begin{tikzpicture}[line width=0.9pt, font=\small,
    x={(1cm,0cm)}, y={(0.4cm,0.35cm)}, z={(0cm,1cm)}]
  \def\a{3} \def\b{2} \def\c{2}

  \coordinate (A) at (0,0,0);   \coordinate (B) at (\a,0,0);
  \coordinate (C) at (\a,\b,0); \coordinate (D) at (0,\b,0);
  \coordinate (A1) at (0,0,\c);  \coordinate (B1) at (\a,0,\c);
  \coordinate (C1) at (\a,\b,\c);\coordinate (D1) at (0,\b,\c);

  % Kích thước a (đáy)
  \draw[<->, gray, thin] (0,-0.5,0) -- (\a,-0.5,0) node[midway, below] {$a$};
  \draw[<->, gray, thin] (\a+0.5,0,0) -- (\a+0.5,\b,0) node[midway, right] {$b$};
  \draw[<->, gray, thin] (\a+0.5,\b,0) -- (\a+0.5,\b,\c) node[midway, right] {$c$};

  % Nét khuất
  \draw[dashed, line width=0.6pt] (A)--(B) (A)--(D) (A)--(A1);
  % Nét thấy
  \draw (B)--(C)--(D); \draw (B)--(B1); \draw (C)--(C1); \draw (D)--(D1);
  \draw (A1)--(B1)--(C1)--(D1)--cycle;

  \node[left]        at (A)  {$A$}; \node[below] at (B)  {$B$};
  \node[right]       at (C)  {$C$}; \node[left]  at (D)  {$D$};
  \node[above left]  at (A1) {$A'$};\node[above] at (B1) {$B'$};
  \node[right]       at (C1) {$C'$};\node[above left] at (D1) {$D'$};
\end{tikzpicture}
```

---

## BẢNG TRA CỨU NHANH

| Mã   | Tên mẫu                            | Môn    | Lớp   | Package chính     |
|------|------------------------------------|--------|-------|-------------------|
| T01  | Tam giác ABC bất kỳ + đường cao    | Toán   | 6–9   | tkz-euclide       |
| T02  | Tam giác vuông tại A               | Toán   | 6–9   | tkz-euclide       |
| T03  | Tam giác cân + trung trực          | Toán   | 6–8   | tkz-euclide       |
| T04  | Tứ giác ABCD bất kỳ               | Toán   | 6–8   | tikz              |
| T05  | Hình bình hành + đường chéo        | Toán   | 6–9   | tkz-euclide       |
| T06  | Hình thang AB//CD                  | Toán   | 6–9   | tikz              |
| T07  | Đường tròn + tiếp tuyến + dây cung | Toán   | 9     | tikz              |
| T08  | Đường tròn nội/ngoại tiếp △        | Toán   | 9     | tkz-euclide       |
| T09  | Hai đường tròn cắt nhau            | Toán   | 9     | tkz-euclide       |
| T10  | Góc nội tiếp – góc tâm             | Toán   | 9     | tikz              |
| T11  | Hệ trục Oxy + vectơ               | Toán   | 10    | tikz              |
| T12  | Cộng vectơ (hình bình hành)        | Toán   | 10    | tikz              |
| T13  | Đường thẳng trong Oxy              | Toán   | 10    | tikz              |
| T14  | Góc giữa 2 đường thẳng             | Toán   | 10–11 | tikz              |
| T15  | Khoảng cách điểm – đường thẳng     | Toán   | 10    | tikz              |
| T16  | Đồ thị parabol y=ax²+bx+c          | Toán   | 10–12 | pgfplots          |
| T17  | Đồ thị sin và cos                  | Toán   | 11    | pgfplots          |
| T18  | Bảng biến thiên (tkz-tab)          | Toán   | 10–12 | tkz-tab           |
| T19  | Hình chóp S.ABC                    | Toán   | 11–12 | tikz 3d           |
| T20  | Hình chóp S.ABCD                   | Toán   | 11–12 | tikz 3d           |
| T21  | Lăng trụ tam giác ABC.A'B'C'       | Toán   | 11–12 | tikz 3d           |
| T22  | Lăng trụ tứ giác ABCD.A'B'C'D'    | Toán   | 11–12 | tikz 3d           |
| T23  | Hình lập phương ABCD.A'B'C'D'      | Toán   | 11–12 | tikz 3d           |
| V01  | Vật trên mặt phẳng nghiêng + lực   | Lý     | 10    | tikz              |
| V02  | Đòn bẩy + tay đòn                  | Lý     | 6–8   | tikz              |
| V03  | Ròng rọc cố định + động            | Lý     | 6–8   | tikz              |
| V04  | Lò xo treo vật                     | Lý     | 6–10  | tikz              |
| V05  | Mạch nối tiếp R1-R2-R3             | Lý     | 9     | circuitikz        |
| V06  | Mạch song song R1//R2              | Lý     | 9     | circuitikz        |
| V07  | Mạch hỗn hợp R1 nt (R2//R3)       | Lý     | 9     | circuitikz        |
| V08  | Mạch RLC nối tiếp                  | Lý     | 12    | circuitikz        |
| V09  | Mạch ampe kế + vôn kế              | Lý     | 9–11  | circuitikz        |
| V10  | Mạch LC dao động                   | Lý     | 11–12 | circuitikz        |
| V11  | Thấu kính hội tụ + ảnh thật        | Lý     | 11    | tikz              |
| V12  | Thấu kính phân kỳ + ảnh ảo         | Lý     | 11    | tikz              |
| V13  | Gương cầu lõm + tiêu điểm          | Lý     | 11    | tikz              |
| V14  | Lăng kính tán sắc ánh sáng         | Lý     | 11    | tikz              |
| V15  | Đồ thị dao động điều hòa x(t)      | Lý     | 12    | pgfplots          |
| V16  | Phân tích lực mặt phẳng nghiêng    | Lý     | 10    | tikz              |
| H01  | Axit acetic CH3COOH                | Hóa    | 9–11  | chemfig           |
| H02  | Benzene C6H6 (Kekulé)              | Hóa    | 11–12 | chemfig           |
| H03  | Glucose (mạch thẳng Fischer)       | Hóa    | 12    | chemfig           |
| H04  | Ethanol C2H5OH                     | Hóa    | 9–11  | chemfig           |
| H05  | Axit sulfuric H2SO4                | Hóa    | 10–11 | chemfig           |
| H06  | Methane CH4                        | Hóa    | 9     | chemfig           |
| H07  | Ethylene CH2=CH2                   | Hóa    | 11    | chemfig           |
| H08  | Acetylene CH≡CH                    | Hóa    | 11    | chemfig           |
| H09  | Điều chế CO2 (HCl+CaCO3)          | Hóa    | 9     | tikz              |
| H10  | Điện phân NaCl                     | Hóa    | 12    | tikz              |
| H11  | Chưng cất rượu                     | Hóa    | 9     | tikz              |
| H12  | Nhận biết SO2 (nước brom)          | Hóa    | 10–11 | tikz              |
| P01  | Đồ thị hàm bậc ba y=x³-3x+2       | Toán   | 12    | pgfplots          |
| P02  | Đồ thị logarithm                   | Toán   | 12    | pgfplots          |
| P03  | Bảng biến thiên hàm phân thức      | Toán   | 12    | tkz-tab           |
| P04  | Lực Coulomb 2 điện tích             | Lý     | 11    | tikz              |
| P05  | Sóng ngang (snapshot t=0)           | Lý     | 12    | pgfplots          |
| P06  | Gương phẳng – định luật phản xạ    | Lý     | 7–11  | tikz              |
| P07  | Con lắc đơn                        | Lý     | 12    | tikz              |
| P08  | Khúc xạ ánh sáng (Snell)           | Lý     | 11    | tikz              |
| P09  | Đồ thị U-I đặc tính V-A            | Lý     | 9–11  | pgfplots          |
| P10  | Hình hộp chữ nhật a×b×c            | Toán   | 8–12  | tikz 3d           |

---

## PHỤ LỤC — Mẫu Bổ Sung (T21–T28)

---

#### Mẫu T21 — Hai đường thẳng song song bị cắt bởi cát tuyến (Góc so le, đồng vị)

**Lớp áp dụng:** 7–8  
**Kết quả:** Hai đường thẳng a∥b bị cắt bởi cát tuyến c; tô màu 1 cặp góc so le trong (xanh) và 1 cặp góc đồng vị (cam); nhãn α tại mỗi cặp; ghi chú a∥b.

```latex
% ===== T21: Hai đường thẳng song song – cát tuyến =====
% Tham số có thể thay đổi:
%   yA=1, yB=3  — khoảng cách 2 đường thẳng
%   angle=60    — góc nghiêng của cát tuyến (độ)
%   xspan=4     — chiều dài đường thẳng a, b
\begin{tikzpicture}[line width=0.9pt, font=\small]
  % --- Hai đường thẳng song song a và b ---
  \def\yA{1}   % y của đường a
  \def\yB{3}   % y của đường b
  \draw (-0.5,\yA) -- (5.5,\yA)  node[right] {$a$};
  \draw (-0.5,\yB) -- (5.5,\yB)  node[right] {$b$};

  % --- Cát tuyến c (góc ~60° so với đường ngang) ---
  % Giao với a tại P, giao với b tại Q
  % tan(60°)≈1.732, dx = (yB-yA)/tan60 ≈ 1.155
  \coordinate (P) at (2.5, \yA);   % giao với a
  \coordinate (Q) at (1.345, \yB); % giao với b  (2.5 - (3-1)/tan60)
  % Kéo dài cát tuyến ra ngoài hai phía
  \coordinate (Cbot) at ($(P)!1.5!(Q)$);  % kéo xuống qua P
  \coordinate (Ctop) at ($(Q)!1.5!(P)$);  % kéo lên qua Q — sai chiều, sửa:
  % Hướng từ P lên Q: vector (Q-P)
  \coordinate (Ctop) at ($(Q) + 1.2*($(Q)-(P)$)$);
  \coordinate (Cbot) at ($(P) + 1.2*($(P)-(Q)$)$);
  \draw (Cbot) -- (Ctop) node[above right] {$c$};

  % --- Tô màu GÓC SO LE TRONG (cùng màu xanh dương) ---
  % Góc so le trong: góc bên phải-dưới tại Q (trên đường b)
  %   và góc bên trái-trên tại P (trên đường a)
  % Dùng fill polygon đơn giản bằng tọa độ tuyệt đối
  % Tại P: góc bên trái-trên (giữa cát tuyến hướng lên và đường a hướng trái)
  \fill[blue!30, opacity=0.6]
      (P)
      -- ++(180:0.7)          % sang trái 0.7 trên đường a
      -- ++(60:0.5)           % đi theo hướng cát tuyến lên 0.5
      -- cycle;
  % Tại Q: góc bên phải-dưới (giữa cát tuyến hướng xuống và đường b hướng phải)
  \fill[blue!30, opacity=0.6]
      (Q)
      -- ++(0:0.7)            % sang phải 0.7 trên đường b
      -- ++(240:0.5)          % đi ngược chiều cát tuyến
      -- cycle;

  % --- Tô màu GÓC ĐỒNG VỊ (cùng màu cam) ---
  % Góc đồng vị: góc bên phải-trên tại P và góc bên phải-trên tại Q
  % Tại P: bên phải-trên
  \fill[orange!40, opacity=0.6]
      (P)
      -- ++(0:0.7)
      -- ++(60:0.5)
      -- cycle;
  % Tại Q: bên phải-trên
  \fill[orange!40, opacity=0.6]
      (Q)
      -- ++(0:0.7)
      -- ++(60:0.5)
      -- cycle;

  % --- Nhãn góc ---
  \node[blue!70!black] at ($(P)+(-0.45, 0.18)$) {$\alpha$};  % so le tại P
  \node[blue!70!black] at ($(Q)+(0.42, -0.18)$) {$\alpha$};  % so le tại Q
  \node[orange!80!black] at ($(P)+(0.42, 0.18)$) {$\beta$};  % đồng vị tại P
  \node[orange!80!black] at ($(Q)+(0.42, 0.18)$) {$\beta$};  % đồng vị tại Q

  % --- Giao điểm ---
  \fill (P) circle (2pt);
  \fill (Q) circle (2pt);

  % --- Chú thích song song ---
  \node[draw, rounded corners=2pt, fill=yellow!20, font=\footnotesize,
        inner sep=3pt] at (4.2, 2) {$a \parallel b$};
\end{tikzpicture}
```

---

#### Mẫu T22 — Hai tam giác đồng dạng (AA)

**Lớp áp dụng:** 8–9  
**Kết quả:** Tam giác ABC (lớn) và DEF (nhỏ ~60%) vẽ cạnh nhau; đánh dấu góc bằng nhau; tỉ lệ cạnh ghi bên dưới.

```latex
% ===== T22: Hai tam giác đồng dạng AA =====
% Tham số có thể thay đổi:
%   Tọa độ ABC (tam giác lớn), DEF (tam giác nhỏ ~60% kích thước)
%   Nhãn góc: alpha tại A/D, beta tại B/E
\begin{tikzpicture}[line width=0.9pt, font=\small]
  % --- Tam giác ABC (lớn) ---
  \coordinate (A) at (0, 3);
  \coordinate (B) at (0, 0);
  \coordinate (C) at (3.5, 0);
  \draw (A) -- (B) -- (C) -- cycle;
  \fill (A) circle (2pt); \fill (B) circle (2pt); \fill (C) circle (2pt);
  \node[above]      at (A) {$A$};
  \node[below left] at (B) {$B$};
  \node[below right]at (C) {$C$};

  % --- Tam giác DEF (nhỏ, ~60% — dịch sang phải) ---
  \coordinate (D) at (5.0, 1.8);   % tương ứng A
  \coordinate (E) at (5.0, 0);     % tương ứng B
  \coordinate (F) at (7.1, 0);     % tương ứng C
  \draw (D) -- (E) -- (F) -- cycle;
  \fill (D) circle (2pt); \fill (E) circle (2pt); \fill (F) circle (2pt);
  \node[above]      at (D) {$D$};
  \node[below left] at (E) {$E$};
  \node[below right]at (F) {$F$};

  % --- Đánh dấu góc bằng nhau ---
  % Góc A = Góc D (cung đơn)
  \tkzMarkAngle[size=0.55, arc=l, color=blue!70!black](C,A,B)
  \tkzMarkAngle[size=0.55, arc=l, color=blue!70!black](F,D,E)
  % Góc B = Góc E (cung đôi)
  \tkzMarkAngle[size=0.55, arc=ll, color=red!70!black](A,B,C)
  \tkzMarkAngle[size=0.55, arc=ll, color=red!70!black](D,E,F)

  % Nhãn góc
  \node[blue!70!black, right, xshift=2pt] at ($(A)+(0.3,-0.5)$)   {$\hat{A}$};
  \node[blue!70!black, right, xshift=2pt] at ($(D)+(0.25,-0.4)$)  {$\hat{D}$};
  \node[red!70!black,  above, yshift=2pt] at ($(B)+(0.4, 0.35)$)  {$\hat{B}$};
  \node[red!70!black,  above, yshift=2pt] at ($(E)+(0.35,0.3)$)   {$\hat{E}$};

  % --- Tỉ lệ đồng dạng ---
  \node[font=\footnotesize, align=center] at (3.55, -0.65)
    {$\dfrac{AB}{DE} = \dfrac{BC}{EF} = \dfrac{AC}{DF}$};
  \node[font=\footnotesize, below=2pt] at (3.55, -1.1)
    {$\triangle ABC \sim \triangle DEF$ (g.g)};
\end{tikzpicture}
```

---

#### Mẫu T23 — Hình thoi ABCD với đường chéo vuông góc nhau

**Lớp áp dụng:** 8  
**Kết quả:** Hình thoi dạng quả trám; 2 đường chéo AC⊥BD cắt tại O có ký hiệu vuông; các cạnh đánh dấu tick; nhãn đầy đủ.

```latex
% ===== T23: Hình thoi ABCD – đường chéo vuông góc =====
% Tham số có thể thay đổi:
%   d1=2.5 (nửa đường chéo dài AC), d2=1.5 (nửa đường chéo ngắn BD)
\begin{tikzpicture}[line width=0.9pt, font=\small]
  \def\da{2.5}   % nửa đường chéo AC (dọc)
  \def\db{1.6}   % nửa đường chéo BD (ngang)

  % --- Tọa độ 4 đỉnh và tâm ---
  \coordinate (A) at (0, \da);    % trên
  \coordinate (B) at (\db, 0);    % phải
  \coordinate (C) at (0, -\da);   % dưới
  \coordinate (D) at (-\db, 0);   % trái
  \coordinate (O) at (0, 0);      % tâm

  % --- Hình thoi ---
  \draw (A) -- (B) -- (C) -- (D) -- cycle;

  % --- Hai đường chéo ---
  \draw[dashed, line width=0.7pt] (A) -- (C);
  \draw[dashed, line width=0.7pt] (B) -- (D);

  % --- Ký hiệu góc vuông tại O ---
  \draw[line width=0.7pt]
      (0.2, 0) -- (0.2, 0.2) -- (0, 0.2);

  % --- Tick marks trên 4 cạnh (bằng nhau) ---
  \tkzMarkSegment[mark=|, size=4pt](A,B)
  \tkzMarkSegment[mark=|, size=4pt](B,C)
  \tkzMarkSegment[mark=|, size=4pt](C,D)
  \tkzMarkSegment[mark=|, size=4pt](D,A)

  % --- Điểm ---
  \fill (A) circle (2pt); \fill (B) circle (2pt);
  \fill (C) circle (2pt); \fill (D) circle (2pt);
  \fill (O) circle (2pt);

  % --- Nhãn đỉnh ---
  \node[above]       at (A) {$A$};
  \node[right]       at (B) {$B$};
  \node[below]       at (C) {$C$};
  \node[left]        at (D) {$D$};
  \node[below right] at (O) {$O$};

  % --- Ghi chú tính chất ---
  \node[font=\footnotesize, right=8pt] at (B)
    {$AC \perp BD$};
  \node[font=\footnotesize, right=8pt] at ($(B)-(0,0.4)$)
    {$OA=OC,\ OB=OD$};
\end{tikzpicture}
```

---

#### Mẫu T24 — Góc nội tiếp và góc tâm (Đường tròn lớp 9)

**Lớp áp dụng:** 9  
**Kết quả:** Đường tròn (O;R); điểm A,B,C trên đường tròn; góc nội tiếp BAC (cung đơn) và góc tâm BOC (cung đôi); chú thích ∠BOC=2·∠BAC.

```latex
% ===== T24: Góc nội tiếp và góc tâm =====
% Tham số có thể thay đổi:
%   R=2.5 — bán kính đường tròn
%   Góc A=210°, B=50°, C=130° (vị trí trên đường tròn, tính từ trục Ox)
\begin{tikzpicture}[line width=0.9pt, font=\small]
  \def\R{2.5}
  \coordinate (O) at (0,0);

  % --- Đường tròn ---
  \draw (O) circle (\R);
  \fill (O) circle (2pt);
  \node[below right, yshift=-2pt] at (O) {$O$};

  % --- Ba điểm trên đường tròn ---
  % A ở dưới, B trái-trên, C phải-trên
  \coordinate (A) at ({-\R*sin(30)}, {-\R*cos(30)});   % 210° ~ góc dưới
  \coordinate (B) at ({-\R*cos(20)}, { \R*sin(20)});   % ~110°
  \coordinate (C) at ({ \R*cos(20)}, { \R*sin(20)});   % ~70°

  % --- Vẽ tam giác ABC (góc nội tiếp) ---
  \draw (A) -- (B) -- (C) -- (A);

  % --- Đoạn OB và OC (tạo góc tâm) ---
  \draw[line width=0.8pt] (O) -- (B);
  \draw[line width=0.8pt] (O) -- (C);

  % --- Đánh dấu góc ---
  % Góc nội tiếp BAC (cung đơn, màu xanh)
  \tkzMarkAngle[size=0.65, arc=l, color=blue!70!black](B,A,C)
  % Góc tâm BOC (cung đôi, màu đỏ)
  \tkzMarkAngle[size=0.7, arc=ll, color=red!70!black](B,O,C)

  % Nhãn góc
  \node[blue!70!black, above, yshift=2pt] at ($(A)+(0,0.65)$)
    {$\angle BAC$};
  \node[red!70!black,  below, yshift=-2pt] at ($(O)+(0,-0.75)$)
    {$\angle BOC$};

  % --- Điểm ---
  \fill (A) circle (2pt); \fill (B) circle (2pt); \fill (C) circle (2pt);
  \node[below]      at (A) {$A$};
  \node[left]       at (B) {$B$};
  \node[right]      at (C) {$C$};

  % --- Bán kính R ---
  \draw[<->, >=stealth, gray, line width=0.7pt]
      (O) -- node[above, sloped, font=\footnotesize]{$R$} (C);

  % --- Chú thích chính ---
  \node[draw, rounded corners=2pt, fill=yellow!20, font=\footnotesize,
        inner sep=4pt, align=center] at (0, -3.3)
    {$\angle BOC = 2 \cdot \angle BAC$};
\end{tikzpicture}
```

---

#### Mẫu T25 — Hình chóp S.ABCD có thiết diện song song đáy

**Lớp áp dụng:** 11–12  
**Kết quả:** Hình chóp S.ABCD phối cảnh; mặt phẳng cắt song song đáy tạo thiết diện MNPQ tô màu xanh nhạt; cạnh khuất nét đứt; nhãn đầy đủ.

```latex
% ===== T25: Hình chóp S.ABCD – thiết diện song song đáy =====
% Tham số có thể thay đổi:
%   t=0.55 — tỉ số vị trí mặt cắt (0<t<1, t=0.5 là giữa)
%   Tọa độ đáy ABCD và đỉnh S
\begin{tikzpicture}[line width=0.9pt, font=\small,
    x={(1cm,0cm)}, y={(0.4cm,0.3cm)}, z={(0cm,1cm)}]

  % Tỉ số vị trí thiết diện (từ S)
  \def\t{0.55}

  % --- Tọa độ đáy ABCD (trong mp Oxy) ---
  \coordinate (A) at (0,0,0);
  \coordinate (B) at (3,0,0);
  \coordinate (C) at (3,2,0);
  \coordinate (D) at (0,2,0);
  % --- Đỉnh chóp S ---
  \coordinate (S) at (1.5,1,4);

  % --- Điểm thiết diện trên các cạnh bên ---
  % M trên SA: M = S + t*(A-S) = (1-t)*S + t*A
  \coordinate (M) at ($(S)!\t!(A)$);
  \coordinate (N) at ($(S)!\t!(B)$);
  \coordinate (P) at ($(S)!\t!(C)$);
  \coordinate (Q) at ($(S)!\t!(D)$);

  % --- Đáy ABCD ---
  % Cạnh thấy: BC, CD, SB, SC, SD
  \draw (B) -- (C) -- (D);
  % Cạnh khuất: AB, AD, SA
  \draw[dashed, line width=0.6pt] (A) -- (B);
  \draw[dashed, line width=0.6pt] (A) -- (D);
  \draw[dashed, line width=0.6pt] (S) -- (A);

  % --- Cạnh bên thấy ---
  \draw (S) -- (B);
  \draw (S) -- (C);
  \draw (S) -- (D);

  % --- Thiết diện MNPQ (tô màu) ---
  \fill[blue!15, opacity=0.8] (M) -- (N) -- (P) -- (Q) -- cycle;
  \draw[blue!70!black, line width=1.2pt] (M) -- (N) -- (P) -- (Q) -- cycle;

  % M trên SA (khuất) — đường từ S đến M nét đứt đã có
  % MQ song song AD (khuất một phần)
  \draw[dashed, blue!50, line width=0.8pt] (M) -- (Q);

  % --- Nhãn đỉnh ---
  \node[above]       at (S) {$S$};
  \node[below left]  at (A) {$A$};
  \node[below right] at (B) {$B$};
  \node[right]       at (C) {$C$};
  \node[left]        at (D) {$D$};
  % Nhãn thiết diện
  \node[left,  blue!70!black, font=\footnotesize] at (M) {$M$};
  \node[right, blue!70!black, font=\footnotesize] at (N) {$N$};
  \node[right, blue!70!black, font=\footnotesize] at (P) {$P$};
  \node[left,  blue!70!black, font=\footnotesize] at (Q) {$Q$};

  % --- Điểm ---
  \fill (S) circle (2pt); \fill (B) circle (2pt);
  \fill (C) circle (2pt); \fill (D) circle (2pt);
  \fill (M) circle (2pt); \fill (N) circle (2pt);
  \fill (P) circle (2pt); \fill (Q) circle (2pt);
\end{tikzpicture}
```

---

#### Mẫu T26 — Hình lăng trụ đứng ABC.A'B'C' có đường chéo

**Lớp áp dụng:** 11–12  
**Kết quả:** Lăng trụ đứng tam giác; đường chéo BC' màu đỏ; cạnh khuất nét đứt; chiều cao h đánh dấu; nhãn đầy đủ.

```latex
% ===== T26: Lăng trụ đứng tam giác ABC.A'B'C' =====
% Tham số có thể thay đổi:
%   h=3.5 — chiều cao lăng trụ
%   Tọa độ đáy A, B, C
\begin{tikzpicture}[line width=0.9pt, font=\small,
    x={(1cm,0cm)}, y={(0.38cm,0.28cm)}, z={(0cm,1cm)}]

  \def\h{3.5}  % chiều cao

  % --- Đáy dưới ABC ---
  \coordinate (A) at (0,0,0);
  \coordinate (B) at (3,0,0);
  \coordinate (C) at (1.5,2,0);

  % --- Đáy trên A'B'C' ---
  \coordinate (Ap) at (0,0,\h);
  \coordinate (Bp) at (3,0,\h);
  \coordinate (Cp) at (1.5,2,\h);

  % --- Cạnh đáy dưới: BC thấy, AB và AC khuất ---
  \draw (B) -- (C);
  \draw[dashed, line width=0.6pt] (A) -- (B);
  \draw[dashed, line width=0.6pt] (A) -- (C);

  % --- Cạnh đáy trên: A'B'C' đều thấy ---
  \draw (Ap) -- (Bp) -- (Cp) -- cycle;

  % --- Cạnh bên: BB' và CC' thấy, AA' khuất ---
  \draw (B) -- (Bp);
  \draw (C) -- (Cp);
  \draw[dashed, line width=0.6pt] (A) -- (Ap);

  % --- Đường chéo BC' (màu đỏ đậm) ---
  \draw[color={rgb,255:red,197;green,48;blue,48}, line width=1.2pt]
      (B) -- (Cp)  node[midway, right, font=\footnotesize,
                        color={rgb,255:red,197;green,48;blue,48}] {$BC'$};

  % --- Chiều cao h (mũi tên nét đứt bên phải) ---
  \draw[<->, >=stealth, dashed, gray, line width=0.7pt]
      ($(B)+(0.6,0,0)$) -- node[right, font=\footnotesize]{$h$}
      ($(Bp)+(0.6,0,0)$);

  % --- Nhãn đỉnh ---
  \node[below left]  at (A)  {$A$};
  \node[below right] at (B)  {$B$};
  \node[right]       at (C)  {$C$};
  \node[above left]  at (Ap) {$A'$};
  \node[above right] at (Bp) {$B'$};
  \node[right]       at (Cp) {$C'$};

  % --- Điểm ---
  \fill (B)  circle (2pt); \fill (C)  circle (2pt);
  \fill (Ap) circle (2pt); \fill (Bp) circle (2pt); \fill (Cp) circle (2pt);
\end{tikzpicture}
```

---

#### Mẫu T27 — Hệ ròng rọc (Cơ học lớp 6–8)

**Lớp áp dụng:** 6–8  
**Kết quả:** Ròng rọc cố định trên xà + ròng rọc động treo vật; dây vắt qua cả hai; lực F↑ và trọng lực P↓; nhãn F=P/2.

```latex
% ===== T27: Hệ ròng rọc cố định + ròng rọc động =====
% Tham số có thể thay đổi:
%   r1=0.4 — bán kính ròng rọc cố định
%   r2=0.35 — bán kính ròng rọc động
%   Vị trí ròng rọc: cố định tại (1.2,5), động tại (2.8,2.5)
\begin{tikzpicture}[line width=0.9pt, font=\small,
    >=stealth]

  % === XÀ + TƯỜNG (trên cùng) ===
  \fill[gray!40] (-0.3, 5.8) rectangle (5.5, 6.1);
  \draw[line width=1pt] (-0.3, 5.8) -- (5.5, 5.8);
  % Gạch chéo (pattern)
  \foreach \x in {0,0.4,...,5.2}
    \draw[gray!60, line width=0.5pt] (\x, 5.8) -- ++(0.3, 0.3);

  % === RÒNG RỌC CỐ ĐỊNH (gắn xà, tại (1.5, 5.0)) ===
  \def\rfx{1.5} \def\rfy{5.0} \def\rone{0.42}
  \draw (\rfx, \rfy) circle (\rone);
  \fill[gray!20] (\rfx, \rfy) circle (\rone);
  \draw (\rfx, \rfy) circle (\rone);
  \fill (\rfx, \rfy) circle (2.5pt);
  % Thanh gắn lên xà
  \draw[line width=1.2pt] (\rfx, \rfy+\rone) -- (\rfx, 5.8);
  \node[font=\footnotesize, left] at (\rfx-\rone, \rfy) {Cố định};

  % === RÒNG RỌC ĐỘNG (tại (3.0, 2.8)) ===
  \def\rdx{3.0} \def\rdy{2.8} \def\rtwo{0.4}
  \draw (\rdx, \rdy) circle (\rtwo);
  \fill[gray!20] (\rdx, \rdy) circle (\rtwo);
  \draw (\rdx, \rdy) circle (\rtwo);
  \fill (\rdx, \rdy) circle (2.5pt);
  \node[font=\footnotesize, right=4pt] at (\rdx+\rtwo, \rdy) {Động};

  % === VẬT TREO (hình chữ nhật bên dưới ròng rọc động) ===
  \draw[fill=gray!30] (\rdx-0.4, \rdy-\rtwo-0.15)
      rectangle (\rdx+0.4, \rdy-\rtwo-0.85);
  \node[font=\footnotesize] at (\rdx, \rdy-\rtwo-0.5) {Vật};

  % === DÂY VẮT QUA HAI RÒNG RỌC ===
  % Dây từ điểm neo (trái ròng rọc động) lên ròng rọc cố định, xuống tay kéo
  % Đoạn 1: từ điểm neo (\rdx-\rtwo, \rdy) lên gắn xà bên trái
  \draw[line width=1.1pt] (\rdx-\rtwo, \rdy) -- (\rfx-0.05, \rfy-\rone);
  % Đoạn 2: vòng qua ròng rọc cố định (xấp xỉ)
  \draw[line width=1.1pt] (\rfx+0.05, \rfy-\rone) -- (\rdx+\rtwo, \rdy);
  % Nối hai điểm tiếp tuyến qua cung tròn (đơn giản bằng arc)
  \draw[line width=1.1pt]
      (\rfx-0.05, \rfy-\rone) arc(270:90:0.42) ;
  % Đoạn dây từ ròng rọc cố định lên, tay kéo
  \draw[line width=1.1pt] (\rfx-\rone-0.02, \rfy)
      -- (\rfx-\rone-0.02, 5.8);  % neo đầu dây lên xà (đầu kia cố định)

  % Đoạn dây tay kéo đi xuống từ ròng rọc cố định
  \draw[line width=1.1pt] (\rfx+\rone+0.0, \rfy)
      -- (\rfx+\rone, 5.8);

  % === MŨI TÊN LỰC KÉO F (người kéo đoạn dây bên phải xuống/lên) ===
  \draw[->, line width=1.2pt, blue!70!black]
      (\rfx+\rone+0.6, \rfy-1.0)
      -- node[right, font=\footnotesize]{$F$}
      (\rfx+\rone+0.6, \rfy-1.0+1.4);

  % === MŨI TÊN TRỌNG LỰC P (vật) ===
  \draw[->, line width=1.2pt, red!70!black]
      (\rdx, \rdy-\rtwo-0.85)
      -- node[right, font=\footnotesize]{$P$}
      (\rdx, \rdy-\rtwo-0.85-1.0);

  % === CHÚ THÍCH ===
  \node[draw, rounded corners=2pt, fill=yellow!20, font=\footnotesize,
        inner sep=3pt] at (0.9, 1.2)
    {$F = \dfrac{P}{2}$};
\end{tikzpicture}
```

---

#### Mẫu T28 — Đồ thị U-I (Đặc tính V-A) điện trở thuần

**Lớp áp dụng:** 9  
**Kết quả:** Hệ tọa độ I(A)–U(V); 2 đường thẳng qua gốc O (R1 xanh dốc cao, R2 đỏ dốc thấp); điểm làm việc có đường gióng nét đứt; nhãn R1, R2; ghi tan α = R.

```latex
% ===== T28: Đồ thị U-I đặc tính V-A điện trở thuần =====
% Tham số có thể thay đổi:
%   R1=4 (Ω), R2=2 (Ω) — độ dốc 2 đường thẳng
%   Điểm làm việc: I1=1.0A, I2=1.5A
%   Phạm vi trục: I từ 0→2 A, U từ 0→8 V
\begin{tikzpicture}[line width=0.9pt, font=\small,
    >=stealth, scale=1.0]

  % === Tham số ===
  \def\Ra{4}   % R1 = 4 Ω (dốc cao)
  \def\Rb{2}   % R2 = 2 Ω (dốc thấp)
  \def\Imax{2.2}
  \def\Umax{9.0}
  \def\scaleI{2.8}  % 1A = 2.8cm trên trục I
  \def\scaleU{0.7}  % 1V = 0.7cm trên trục U

  % Điểm làm việc trên R1 (I=1.0A, U=4V)
  \def\Ia{1.0}  \def\Ua{4.0}
  % Điểm làm việc trên R2 (I=1.5A, U=3V)
  \def\Ib{1.5}  \def\Ub{3.0}

  % === Trục tọa độ ===
  \draw[->, line width=0.9pt] (0,0) -- ({\Imax*\scaleI+0.5}, 0)
      node[right] {$I$ (A)};
  \draw[->, line width=0.9pt] (0,0) -- (0, {\Umax*\scaleU+0.5})
      node[above] {$U$ (V)};
  \node[below left] at (0,0) {$O$};

  % Vạch chia trục I
  \foreach \i in {0.5, 1.0, 1.5, 2.0}{
    \draw ({\i*\scaleI}, 0.06) -- ({\i*\scaleI}, -0.06);
    \node[below, font=\footnotesize] at ({\i*\scaleI}, 0) {\i};
  }
  % Vạch chia trục U
  \foreach \u in {2, 4, 6, 8}{
    \draw (0.06, {\u*\scaleU}) -- (-0.06, {\u*\scaleU});
    \node[left, font=\footnotesize] at (0, {\u*\scaleU}) {\u};
  }

  % === Đường thẳng R1 (màu xanh, dốc cao) ===
  % U = R1 * I => điểm cuối: I=2, U=8
  \draw[blue!70!black, line width=1.2pt]
      (0,0) -- ({2.0*\scaleI}, {2.0*\Ra*\scaleU})
      node[right, blue!70!black] {$R_1$};

  % === Đường thẳng R2 (màu đỏ, dốc thấp) ===
  \draw[red!70!black, line width=1.2pt]
      (0,0) -- ({2.0*\scaleI}, {2.0*\Rb*\scaleU})
      node[right, red!70!black] {$R_2$};

  % === Điểm làm việc trên R1 (I1=1.0, U1=4) ===
  \fill[blue!70!black] ({\Ia*\scaleI}, {\Ua*\scaleU}) circle (2.5pt);
  % Đường gióng nét đứt
  \draw[dashed, gray, line width=0.6pt]
      ({\Ia*\scaleI}, 0) -- ({\Ia*\scaleI}, {\Ua*\scaleU})
      -- (0, {\Ua*\scaleU});
  \node[above right, blue!70!black, font=\footnotesize]
      at ({\Ia*\scaleI}, {\Ua*\scaleU}) {$(I_1, U_1)$};

  % === Điểm làm việc trên R2 (I2=1.5, U2=3) ===
  \fill[red!70!black] ({\Ib*\scaleI}, {\Ub*\scaleU}) circle (2.5pt);
  \draw[dashed, gray, line width=0.6pt]
      ({\Ib*\scaleI}, 0) -- ({\Ib*\scaleI}, {\Ub*\scaleU})
      -- (0, {\Ub*\scaleU});
  \node[below right, red!70!black, font=\footnotesize]
      at ({\Ib*\scaleI}, {\Ub*\scaleU}) {$(I_2, U_2)$};

  % === Ghi chú độ dốc ===
  \node[blue!70!black, font=\footnotesize, rotate=55]
      at ({0.9*\scaleI}, {0.9*\Ra*\scaleU+0.3})
      {$\tan\alpha_1 = R_1 = \dfrac{U_1}{I_1}$};
  \node[red!70!black, font=\footnotesize, rotate=30]
      at ({1.3*\scaleI}, {1.3*\Rb*\scaleU+0.3})
      {$\tan\alpha_2 = R_2$};
\end{tikzpicture}
```

---

#### Mẫu T29 — Định lý Thales: đường thẳng MN // BC trong tam giác ABC

**Lớp áp dụng:** 8–9  
**Kết quả:** Tam giác ABC với MN // BC, tick marks tỉ lệ, ghi chú tỉ lệ đoạn thẳng

```latex
% ===== T29: Định lý Thales — MN // BC trong tam giác ABC =====
% Tham số: toạ độ A, B, C; tỉ số t (M = A + t*(B-A), N = A + t*(C-A))
\begin{tikzpicture}[line width=0.9pt, font=\small]
  \usetikzlibrary{calc}
  \tkzInit
  % --- Định nghĩa đỉnh ---
  \coordinate (A) at (2, 4);
  \coordinate (B) at (0, 0);
  \coordinate (C) at (4, 0);
  % --- M trên AB, N trên AC (t = 0.55) ---
  \coordinate (M) at ($(A)!0.55!(B)$);
  \coordinate (N) at ($(A)!0.55!(C)$);

  % --- Vẽ tam giác ---
  \draw (B) -- (C) -- (A) -- cycle;
  % --- Vẽ MN ---
  \draw[blue, line width=1pt] (M) -- (N);

  % --- Tick marks: AM (1 gạch), MB (2 gạch) ---
  \tkzMarkSegment[mark=|,  size=4pt](A,M)
  \tkzMarkSegment[mark=|,  size=4pt](A,N)
  \tkzMarkSegment[mark=||, size=4pt](M,B)
  \tkzMarkSegment[mark=||, size=4pt](N,C)

  % --- Nhãn đỉnh ---
  \tkzLabelPoint[above](A){$A$}
  \tkzLabelPoint[below left](B){$B$}
  \tkzLabelPoint[below right](C){$C$}
  \tkzLabelPoint[left](M){$M$}
  \tkzLabelPoint[right](N){$N$}

  % --- Ký hiệu song song ---
  \draw[blue, ->, >=stealth, shorten >=2pt]
      ($(M)!0.5!(N)+(0,0.18)$) -- +(0.35,0)
      node[right, blue, font=\footnotesize]{};
  \node[blue, font=\footnotesize] at ($(M)!0.5!(N)+(0,0.32)$)
      {$MN \parallel BC$};

  % --- Ghi chú tỉ lệ ---
  \node[draw, rounded corners=3pt, fill=yellow!15,
        font=\small, inner sep=4pt] at (5.2, 2)
      {$\dfrac{AM}{MB} = \dfrac{AN}{NC}$};
\end{tikzpicture}
```

---

#### Mẫu T30 — Bình điện phân (Hóa 12)

**Lớp áp dụng:** 12  
**Kết quả:** Sơ đồ bình điện phân với catot, anot, dòng điện, ion di chuyển

```latex
% ===== T30: Bình điện phân — catot (-) anot (+) =====
% Tham số: kích thước bình, nhãn ion (thay Na+/Cl- tuỳ bài)
\begin{tikzpicture}[line width=0.9pt, font=\small,
    >=Stealth, arr/.style={->, thick, shorten >=2pt}]
  \usetikzlibrary{arrows.meta, calc, patterns}

  % --- Bình điện phân (hình chữ nhật) ---
  \draw[line width=1.2pt] (0,0) rectangle (6,3.5);
  % Dung dịch (fill nhạt)
  \fill[cyan!10] (0.05,0.05) rectangle (5.95,2.6);
  \draw[cyan!40, line width=0.5pt] (0.05,2.6) -- (5.95,2.6);
  \node[gray, font=\footnotesize] at (3, 1.3) {Dung dịch NaCl};

  % --- Catot bên trái (thanh điện cực) ---
  \fill[gray!60] (0.8, 0.05) rectangle (1.1, 2.6);
  \node[font=\small\bfseries] at (0.95, 2.9) {Catot};
  \node[font=\small] at (0.95, 3.2) {$(-)$};

  % --- Anot bên phải ---
  \fill[gray!60] (4.9, 0.05) rectangle (5.2, 2.6);
  \node[font=\small\bfseries] at (5.05, 2.9) {Anot};
  \node[font=\small] at (5.05, 3.2) {$(+)$};

  % --- Dây nối nguồn DC (bên trên) ---
  \draw[line width=1.2pt] (0.95, 3.5) -- (0.95, 4.2) -- (5.05, 4.2) -- (5.05, 3.5);
  % Nguồn DC
  \draw[line width=1.2pt] (2.6, 4.2) -- (2.6, 4.7);
  \draw[line width=1.2pt] (3.4, 4.2) -- (3.4, 4.7);
  \draw[line width=2.5pt] (2.4, 4.7) -- (2.8, 4.7); % cực dài (-)? (+ là dài)
  \draw[line width=1pt]   (3.2, 4.7) -- (3.6, 4.7); % cực ngắn
  \draw[line width=2.5pt] (2.4, 4.9) -- (2.8, 4.9);
  \draw[line width=1pt]   (3.2, 4.9) -- (3.6, 4.9);
  \node[font=\footnotesize] at (3, 5.15) {Nguồn DC};

  % --- Mũi tên dòng điện ngoài I (từ + ra, qua dây tới catot) ---
  \draw[arr, red] (5.05, 4.2) -- (4.0, 4.2)
      node[midway, above, red, font=\footnotesize]{$I$};

  % --- Mũi tên ion trong dung dịch ---
  % Cation Na+ → catot (trái)
  \draw[arr, blue!70] (3.5, 1.8) -- (1.4, 1.8)
      node[midway, above, blue!70, font=\footnotesize]{$\text{Na}^+$};
  % Anion Cl- → anot (phải)
  \draw[arr, orange!80!red] (2.5, 0.9) -- (4.6, 0.9)
      node[midway, below, orange!80!red, font=\footnotesize]{$\text{Cl}^-$};
\end{tikzpicture}
```

---

#### Mẫu T31 — Chuỗi phản ứng hóa học (flowchart mũi tên)

**Lớp áp dụng:** 11–12  
**Kết quả:** Sơ đồ chuỗi 5 hợp chất với mũi tên điều kiện phản ứng

```latex
% ===== T31: Chuỗi phản ứng — CH4 → C2H2 → C2H4 → C2H5OH → CH3COOH =====
% Tham số: node text, điều kiện trên/dưới mũi tên
\begin{tikzpicture}[
    node distance=2.4cm,
    box/.style={rectangle, draw, rounded corners=3pt,
                fill=blue!8, inner sep=5pt, font=\small,
                minimum height=1cm, minimum width=1.7cm},
    arr/.style={-latex, thick},
    cond/.style={font=\scriptsize, inner sep=1pt},
    >=latex, line width=0.9pt]
  \usetikzlibrary{positioning, arrows.meta}

  % --- Các node hợp chất ---
  \node[box] (A) {$\text{CH}_4$};
  \node[box, right=of A] (B) {$\text{C}_2\text{H}_2$};
  \node[box, right=of B] (C) {$\text{C}_2\text{H}_4$};
  \node[box, right=of C] (D) {$\text{C}_2\text{H}_5\text{OH}$};
  \node[box, right=of D] (E) {$\text{CH}_3\text{COOH}$};

  % --- Mũi tên + điều kiện ---
  % CH4 → C2H2
  \draw[arr] (A) -- (B)
      node[cond, above, midway]{$1500^\circ\text{C}$}
      node[cond, below, midway]{làm lạnh nhanh};

  % C2H2 → C2H4
  \draw[arr] (B) -- (C)
      node[cond, above, midway]{$\text{H}_2$, xt}
      node[cond, below, midway]{$t^\circ$};

  % C2H4 → C2H5OH
  \draw[arr] (C) -- (D)
      node[cond, above, midway]{$\text{H}_2\text{O}$}
      node[cond, below, midway]{$\text{H}^+$, $t^\circ$};

  % C2H5OH → CH3COOH
  \draw[arr] (D) -- (E)
      node[cond, above, midway]{men giấm}
      node[cond, below, midway]{$30\text{--}35^\circ\text{C}$};
\end{tikzpicture}
```

---

#### Mẫu T32 — Đường phân giác trong tam giác (tính chất)

**Lớp áp dụng:** 9  
**Kết quả:** Tam giác ABC với phân giác AD, đánh dấu 2 góc bằng nhau, ghi chú tỉ lệ

```latex
% ===== T32: Đường phân giác trong tam giác ABC =====
% Tham số: toạ độ A, B, C; D chia BC theo tỉ AB:AC
\begin{tikzpicture}[line width=0.9pt, font=\small]
  \usetikzlibrary{calc}
  \tkzInit

  % --- Đỉnh ---
  \coordinate (A) at (2.5, 4.2);
  \coordinate (B) at (0, 0);
  \coordinate (C) at (5, 0);

  % AB ≈ 4.72, AC ≈ 3.35 → D chia BC: BD/DC = AB/AC ≈ 4.72/3.35
  % D = B + (AB/(AB+AC)) * (C-B)
  % Tính gần đúng: AB = sqrt(2.5²+4.2²) ≈ 4.89, AC = sqrt(2.5²+4.2²) tương tự
  % Dùng AB = 4.89, AC = 3.91 (sẽ định nghĩa D trực tiếp)
  \coordinate (D) at ($(B)!0.556!(C)$); % BD/BC ≈ AB/(AB+AC)

  % --- Vẽ tam giác ---
  \draw (B) -- (C) -- (A) -- cycle;

  % --- Vẽ phân giác AD ---
  \draw[blue, line width=1pt] (A) -- (D);

  % --- Đánh dấu 2 góc BAD = DAC ---
  \tkzMarkAngle[arc=l, size=0.6, color=red!70!black](B,A,D)
  \tkzMarkAngle[arc=l, size=0.9, color=red!70!black](D,A,C)

  % --- Nhãn ---
  \tkzLabelPoint[above](A){$A$}
  \tkzLabelPoint[below left](B){$B$}
  \tkzLabelPoint[below right](C){$C$}
  \tkzLabelPoint[below](D){$D$}

  % --- Ghi chú ---
  \node[draw, rounded corners=3pt, fill=yellow!15,
        font=\small, inner sep=4pt] at (6.2, 2.1)
      {$\dfrac{BD}{DC} = \dfrac{AB}{AC}$};
\end{tikzpicture}
```

---

#### Mẫu T33 — Đồ thị hypebol $y = k/x$ với tiệm cận

**Lớp áp dụng:** 10–12  
**Kết quả:** Hai nhánh hypebol, tiệm cận nét đứt, điểm mẫu có đường gióng, nhãn hàm số

```latex
% ===== T33: Đồ thị hypebol y = k/x (k > 0) =====
% Tham số: k (hệ số), xmin/xmax domain
\begin{tikzpicture}[line width=0.9pt, font=\small]
  \usetikzlibrary{calc}
  \begin{axis}[
    axis lines=center,
    xlabel={$x$}, ylabel={$y$},
    xlabel style={right},
    ylabel style={above},
    xmin=-4.5, xmax=4.5,
    ymin=-4.5, ymax=4.5,
    xtick={-4,-3,...,4}, ytick={-4,-3,...,4},
    tick label style={font=\scriptsize},
    width=7cm, height=7cm,
    clip=false,
    every axis plot/.append style={smooth, thick, blue!70!black}
  ]
    \pgfmathsetmacro{\k}{2} % k = 2

    % Nhánh x > 0
    \addplot[domain=0.45:4.3, samples=80, blue!70!black, thick]
        {\k/x};
    % Nhánh x < 0
    \addplot[domain=-4.3:-0.45, samples=80, blue!70!black, thick]
        {\k/x};

    % Tiệm cận x = 0 (trục y) — đã là trục, thêm nét đứt riêng
    \draw[dashed, gray, line width=0.7pt] (axis cs:0,-4.5) -- (axis cs:0,4.5);
    % Tiệm cận y = 0 (trục x)
    \draw[dashed, gray, line width=0.7pt] (axis cs:-4.5,0) -- (axis cs:4.5,0);

    % Điểm mẫu P(1, k) với đường gióng
    \addplot[mark=*, mark size=2pt, red] coordinates {(1,\k)};
    \draw[dashed, red, line width=0.6pt]
        (axis cs:1,0) -- (axis cs:1,\k) -- (axis cs:0,\k);
    \node[red, font=\scriptsize, right] at (axis cs:1,\k) {$(1;\ k)$};

    % Nhãn hàm số ở đầu nhánh trên
    \node[blue!70!black, font=\small] at (axis cs:3.5, 1.0)
        {$y = \dfrac{k}{x}$};
  \end{axis}
\end{tikzpicture}
```

---

#### Mẫu T34 — Hệ trục Oxyz 3D phối cảnh (Toán 12)

**Lớp áp dụng:** 12  
**Kết quả:** Hệ trục Oxyz dạng oblique 2D, điểm A(2;3;4) với đường chiếu nét đứt xuống 3 mặt phẳng

```latex
% ===== T34: Hệ trục Oxyz 3D phối cảnh oblique (không dùng tdplot) =====
% Tham số: toạ độ điểm A (ax, ay, az); góc oblique cho Oy
\begin{tikzpicture}[line width=0.9pt, font=\small, >=Stealth]
  \usetikzlibrary{arrows.meta, calc}

  % --- Hệ số phối cảnh oblique: Oy góc -30°, tỉ lệ 0.5 ---
  \def\ax{2}  \def\ay{3}  \def\az{4}   % toạ độ điểm A
  \def\sc{0.9}                          % scale chung

  % Chuyển (x,y,z) → (X,Y) oblique:
  %   X = x*\sc + y*cos(210°)*\sc*0.5 = x*\sc - y*0.433*\sc
  %   Y = z*\sc + y*sin(210°)*\sc*0.5 = z*\sc - y*0.25*\sc
  % Macro đặt sẵn các điểm:
  \pgfmathsetmacro{\Ax}{\ax*\sc + \ay*cos(210)*0.5*\sc}
  \pgfmathsetmacro{\Ay}{\az*\sc + \ay*sin(210)*0.5*\sc}

  % O là gốc
  \coordinate (O)  at (0,0);
  \coordinate (A3) at (\Ax, \Ay);  % điểm A trong mặt phẳng vẽ

  % --- Trục Ox (sang phải) ---
  \draw[->, line width=1pt] (O) -- (4.5*\sc, 0) node[right]{$x$};
  % --- Trục Oz (thẳng lên) ---
  \draw[->, line width=1pt] (O) -- (0, 4.2*\sc) node[above]{$z$};
  % --- Trục Oy (oblique, xuống-phải góc 210°) ---
  \draw[->, line width=1pt] (O) --
      ({3.5*\sc*cos(210)}, {3.5*\sc*sin(210)}) node[below left]{$y$};

  % --- Nhãn O ---
  \node[below left, font=\small] at (O) {$O$};

  % Toạ độ hình chiếu của A lên 3 trục / mặt phẳng (oblique):
  % Hình chiếu lên mặt Oxy (z=0): (ax, ay, 0)
  \pgfmathsetmacro{\Axy_x}{\ax*\sc + \ay*cos(210)*0.5*\sc}
  \pgfmathsetmacro{\Axy_y}{0 + \ay*sin(210)*0.5*\sc}
  \coordinate (Axy) at (\Axy_x, \Axy_y);

  % Hình chiếu lên trục Ox: (ax, 0, 0)
  \coordinate (Ax_) at (\ax*\sc, 0);
  % Hình chiếu lên trục Oz: (0, 0, az)
  \coordinate (Az_) at (0, \az*\sc);
  % Hình chiếu lên mặt Oxz (y=0): (ax,0,az)
  \coordinate (Axz) at (\ax*\sc, \az*\sc);

  % --- Đường gióng nét đứt từ A xuống mặt Oxy ---
  \draw[dashed, line width=0.6pt, gray]
      (A3) -- (Axy);
  % Từ Axy xuống Ox
  \draw[dashed, line width=0.6pt, gray]
      (Axy) -- (Ax_);
  % Từ A lên mặt Oxz
  \draw[dashed, line width=0.6pt, gray]
      (A3) -- (Axz);
  \draw[dashed, line width=0.6pt, gray]
      (Axz) -- (Az_);
  \draw[dashed, line width=0.6pt, gray]
      (Axz) -- (Ax_);

  % --- Điểm A ---
  \fill[red] (A3) circle (2.2pt);
  \node[above right, red, font=\small]
      at (A3) {$A(\ax;\ay;\az)$};

  % --- Nhãn hình chiếu ---
  \fill[blue!60] (Axy) circle (1.5pt);
  \node[below right, blue!60, font=\scriptsize]
      at (Axy) {$A'$};
  \fill[blue!60] (Axz) circle (1.5pt);
  \node[right, blue!60, font=\scriptsize]
      at (Axz) {$A''$};
\end{tikzpicture}
```

---

#### Mẫu T35 — Mạch cầu Wheatstone cân bằng và đo điện trở

**Lớp áp dụng:** 11  
**Kết quả:** Sơ đồ mạch cầu điện trở hình thoi ABCD với 4 điện trở $R_1, R_2, R_3, R_x$ trên 4 nhánh; nhánh chéo giữa nối điện kế $G$; hai đỉnh còn lại nối nguồn điện $\mathcal{E}$; chú thích điều kiện cân bằng cầu.

```latex
% ===== T35: Mạch cầu Wheatstone cân bằng và đo điện trở =====
% Tham số có thể thay đổi:
%   Tọa độ các nút hình thoi A, B, C, D
%   Nhãn các điện trở R1, R2, R3, Rx
%   Nguồn điện E, điện kế G, công thức điều kiện cân bằng
\begin{tikzpicture}[line width=0.9pt, font=\small]
  % Định vị các đỉnh của hình thoi ABCD
  \coordinate (A) at (0, 0);       % Cực trái A
  \coordinate (B) at (3, 2.2);     % Cực trên B
  \coordinate (C) at (6, 0);       % Cực phải C
  \coordinate (D) at (3, -2.2);    % Cực dưới D

  % Vẽ 4 nhánh cầu Wheatstone với các điện trở R1, R2, R3, Rx
  \draw (A) to[R, l=$R_1$] (B)
        to[R, l=$R_2$] (C)
        to[R, l_=$R_x$] (D)
        to[R, l_=$R_3$] (A);

  % Nhánh chéo giữa B và D: Điện kế G
  \draw (B) -- (3, 0.45);
  \draw (3, -0.45) -- (D);
  \draw[fill=white, draw=black, line width=0.9pt] (3, 0) circle (0.45cm);
  \node[font=\bfseries\normalsize] at (3, 0) {G};
  \draw[->, >=Stealth, thin] (2.75, -0.15) -- (3.25, 0.2);

  % Đánh dấu các nút A, B, C, D
  \fill (A) circle (2pt) node[left=3pt] {$A$};
  \fill (B) circle (2pt) node[above=3pt] {$B$};
  \fill (C) circle (2pt) node[right=3pt] {$C$};
  \fill (D) circle (2pt) node[below=3pt] {$D$};

  % Mạch ngoài nối nguồn điện E (suất điện động E) giữa A và C
  \draw (A) -- (-1.2, 0) -- (-1.2, -3.2)
        to[battery, l=$\mathcal{E}$] (7.2, -3.2)
        -- (7.2, 0) -- (C);

  % Chú thích điều kiện cân bằng cầu Wheatstone
  \node[draw, rounded corners=3pt, fill=blue!5, font=\small, inner sep=4pt]
        at (3, -4.1) {Điều kiện cân bằng khi $I_G = 0$: $\dfrac{R_1}{R_2} = \dfrac{R_3}{R_x} \implies R_x = \dfrac{R_2 R_3}{R_1}$};
\end{tikzpicture}
```

---

#### Mẫu T36 — Sơ đồ tạo ảnh qua kính hiển vi (Quang học 11)

**Lớp áp dụng:** 11  
**Kết quả:** Hệ 2 thấu kính đồng trục: Vật kính $O_1$ ($f_1$ ngắn) và Thị kính $O_2$ ($f_2$ dài hơn). Vật $AB$ đặt trước $O_1$ cho ảnh thật trung gian $A_1B_1$, $A_1B_1$ nằm trong tiêu cự của $O_2$ cho ảnh ảo sau cùng $A_2B_2$ rất lớn; đường tia sáng chính xác kèm mắt quan sát.

```latex
% ===== T36: Sơ đồ tạo ảnh qua kính hiển vi =====
% Tham số có thể thay đổi:
%   Tiêu cự f1, f2 của vật kính O1 và thị kính O2
%   Vị trí và độ cao vật sáng AB
%   Ảnh trung gian A1B1 và ảnh ảo sau cùng A2B2
\begin{tikzpicture}[line width=0.9pt, font=\small, >=Stealth]
  % --- Trục chính ---
  \draw[->, line width=0.8pt] (-0.2, 0) -- (10.5, 0) node[right]{$\Delta$};

  % --- Thấu kính 1: Vật kính O1 (tiêu cự ngắn f1 = 1.0) ---
  \coordinate (O1) at (2.5, 0);
  \draw[<->, line width=1.2pt, blue!80!black] (2.5, -2.5) -- (2.5, 2.5)
        node[above, font=\footnotesize] {Vật kính ($O_1$)};
  \node[below right=1pt, font=\footnotesize] at (O1) {$O_1$};
  \coordinate (F1)  at (1.5, 0);
  \coordinate (F1p) at (3.5, 0);
  \fill (F1) circle (1.5pt) node[below=2pt, font=\scriptsize] {$F_1$};
  \fill (F1p) circle (1.5pt) node[above=2pt, font=\scriptsize] {$F'_1$};

  % --- Thấu kính 2: Thị kính O2 (tiêu cự f2 = 1.6 > f1) ---
  \coordinate (O2) at (6.8, 0);
  \draw[<->, line width=1.2pt, blue!80!black] (6.8, -3.5) -- (6.8, 2.5)
        node[above, font=\footnotesize] {Thị kính ($O_2$)};
  \node[below right=1pt, font=\footnotesize] at (O2) {$O_2$};
  \coordinate (F2)  at (5.2, 0);
  \coordinate (F2p) at (8.4, 0);
  \fill (F2) circle (1.5pt) node[below=2pt, font=\scriptsize] {$F_2$};
  \fill (F2p) circle (1.5pt) node[below=2pt, font=\scriptsize] {$F'_2$};

  % --- Vật sáng AB (d1 = 1.5 > f1 = 1.0) ---
  \coordinate (A) at (1.0, 0);
  \coordinate (B) at (1.0, 0.45);
  \draw[->, line width=1.2pt, red] (A) -- (B) node[above, font=\footnotesize] {$B$};
  \node[below=2pt, font=\scriptsize] at (A) {$A$};

  % --- Ảnh trung gian A1B1 (thật, ngược chiều, d1' = 3.0) ---
  \coordinate (A1) at (5.5, 0);
  \coordinate (B1) at (5.5, -0.9);
  \draw[->, line width=1.2pt, red!80!black] (A1) -- (B1) node[below=2pt, font=\footnotesize] {$B_1$};
  \node[above=2pt, font=\scriptsize] at (A1) {$A_1$};

  % --- Ảnh sau cùng A2B2 (ảo, rất lớn, d2' = -4.5) ---
  \coordinate (A2) at (2.0, 0);
  \coordinate (B2) at (2.0, -3.3);
  \draw[->, dashed, line width=1.2pt, purple] (A2) -- (B2) node[below left=2pt, font=\footnotesize] {$B_2$};
  \node[above left=2pt, font=\scriptsize] at (A2) {$A_2$};

  % --- Đường truyền tia sáng từ B qua O1 ---
  % Tia 1: Từ B song song trục chính tới O1 tại (2.5, 0.45)
  \draw[line width=0.7pt, orange!80!black] (B) -- (2.5, 0.45);
  \draw[->, line width=0.7pt, orange!80!black] (1.75, 0.45) -- (1.8, 0.45);
  % Sau O1 qua F'1 tới B1 và đi tiếp tới O2
  \draw[line width=0.7pt, orange!80!black] (2.5, 0.45) -- (5.5, -0.9);
  \draw[->, line width=0.7pt, orange!80!black] (3.0, 0.225) -- (3.05, 0.202);

  % Tia 2: Từ B qua quang tâm O1 đi thẳng tới B1
  \draw[line width=0.7pt, green!60!black] (B) -- (5.5, -0.9);
  \draw[->, line width=0.7pt, green!60!black] (2.0, 0.15) -- (2.05, 0.135);

  % --- Đường truyền tia sáng từ B1 qua O2 ---
  % Tia qua quang tâm O2: từ B1 qua O2(6.8, 0)
  \draw[line width=0.7pt, red!80!black] (5.5, -0.9) -- (6.8, 0) -- (9.0, 1.523);
  \draw[->, line width=0.7pt, red!80!black] (7.9, 0.76) -- (7.95, 0.795);
  % Nét đứt kéo dài về B2
  \draw[dashed, line width=0.6pt, red!80!black] (6.8, 0) -- (B2);

  % Tia song song trục chính từ B1 tới O2 tại (6.8, -0.9)
  \draw[line width=0.7pt, cyan!70!black] (5.5, -0.9) -- (6.8, -0.9);
  % Sau O2 khúc xạ qua F'2(8.4, 0)
  \draw[line width=0.7pt, cyan!70!black] (6.8, -0.9) -- (9.2, 0.45);
  \draw[->, line width=0.7pt, cyan!70!black] (7.6, -0.45) -- (7.65, -0.42);
  % Nét đứt kéo dài về B2
  \draw[dashed, line width=0.6pt, cyan!70!black] (6.8, -0.9) -- (B2);

  % --- Mắt quan sát đặt sau thị kính ---
  \draw[line width=0.8pt] (9.6, 0.8) arc[start angle=150, end angle=210, radius=1.0];
  \fill (9.6, 0.3) circle (2pt);
  \node[right, font=\scriptsize] at (9.7, 0.3) {Mắt};

  % --- Hộp chú thích ---
  \node[draw, rounded corners=3pt, fill=yellow!15, font=\scriptsize, inner sep=3pt]
        at (5.5, 2.0) {$d'_1 > 0 \text{ (ảnh thật } A_1B_1 \text{)} \quad \longrightarrow \quad d_2 < f_2 \implies d'_2 < 0 \text{ (ảnh ảo } A_2B_2 \text{ rất lớn)}$};
\end{tikzpicture}
```

---

#### Mẫu T37 — Mô hình nguyên tử Bohr và các mức năng lượng quang phổ

**Lớp áp dụng:** 12  
**Kết quả:** Sơ đồ mức năng lượng nguyên tử Hydro với hạt nhân ở tâm, các quỹ đạo dừng tròn đồng tâm $n=1 (K), n=2 (L), n=3 (M), n=4 (N)$; mũi tên sóng photon phát xạ khi electron chuyển mức ($H_\alpha$, Lyman $\alpha$); nhãn mức $n$ và công thức năng lượng $E_n = -\dfrac{13{,}6}{n^2}\text{ eV}$.

```latex
% ===== T37: Mô hình nguyên tử Bohr và các mức năng lượng quang phổ =====
% Tham số có thể thay đổi:
%   Bán kính các quỹ đạo dừng rK, rL, rM, rN
%   Mức chuyển trạng thái electron (n=3 -> n=2, n=2 -> n=1...)
%   Tên loại sóng photon phát xạ (H_alpha, Lyman...)
\begin{tikzpicture}[line width=0.9pt, font=\small, >=Stealth]
  \usetikzlibrary{decorations.pathmorphing}

  % --- Hạt nhân ở tâm ---
  \fill[red!80!black] (0,0) circle (5pt);
  \node[white, font=\bfseries\scriptsize] at (0,0) {$+$};
  \node[below=7pt, font=\scriptsize] at (0,0) {Hạt nhân ($+e$)};

  % --- Bán kính các quỹ đạo dừng ---
  \def\rK{1.2}
  \def\rL{2.2}
  \def\rM{3.2}
  \def\rN{4.2}

  % --- Các quỹ đạo dừng tròn đồng tâm ---
  \draw[dashed, blue!50!black, line width=0.7pt] (0,0) circle (\rK);
  \draw[dashed, blue!50!black, line width=0.7pt] (0,0) circle (\rL);
  \draw[dashed, blue!50!black, line width=0.7pt] (0,0) circle (\rM);
  \draw[dashed, blue!50!black, line width=0.7pt] (0,0) circle (\rN);

  % --- Nhãn các quỹ đạo dừng (lớp và năng lượng) ---
  \node[above, font=\footnotesize, blue!80!black] at (0, \rK)
        {$n=1\ (K)\colon -13{,}6\text{ eV}$};
  \node[above, font=\footnotesize, blue!80!black] at (0, \rL)
        {$n=2\ (L)\colon -3{,}4\text{ eV}$};
  \node[above, font=\footnotesize, blue!80!black] at (0, \rM)
        {$n=3\ (M)\colon -1{,}51\text{ eV}$};
  \node[above, font=\footnotesize, blue!80!black] at (0, \rN)
        {$n=4\ (N)\colon -0{,}85\text{ eV}$};

  % --- Electron trên quỹ đạo n = 3 nhảy xuống n = 2 ---
  \coordinate (eM) at ({3.2*cos(35)}, {3.2*sin(35)});
  \coordinate (eL) at ({2.2*cos(35)}, {2.2*sin(35)});

  % Vị trí ban đầu electron (n=3)
  \fill[cyan!80!black] (eM) circle (3pt);
  \node[above right=1pt, cyan!80!black, font=\scriptsize] at (eM) {$e^-$};

  % Mũi tên chuyển mức electron từ n=3 xuống n=2
  \draw[->, line width=1.2pt, red!80!black]
        (eM) -- (eL)
        node[midway, right=2pt, font=\scriptsize, text=red!80!black] {Chuyển mức};

  % Vị trí đích electron (n=2)
  \draw[cyan!80!black, fill=white, line width=1pt] (eL) circle (3pt);

  % Photon phát xạ (sóng dạng snake) phát ra từ điểm chuyển mức
  \draw[->, line width=1.1pt, red, decorate, decoration={snake, amplitude=2pt, segment length=6pt}]
        (eL) -- ++(2.2, -0.6)
        node[right=2pt, font=\footnotesize] {Photon $H_\alpha$ ($\lambda = 656\text{ nm}$)};

  % --- Chuyển mức n=2 xuống n=1 (Dãy Lyman - phát photon UV) ---
  \coordinate (eL2) at ({-2.2*cos(40)}, {-2.2*sin(40)});
  \coordinate (eK2) at ({-1.2*cos(40)}, {-1.2*sin(40)});
  \draw[->, line width=1.1pt, violet] (eL2) -- (eK2);
  \draw[->, line width=1pt, violet, decorate, decoration={snake, amplitude=1.8pt, segment length=5pt}]
        (eK2) -- ++(-1.8, -0.8)
        node[below left=1pt, font=\footnotesize] {Lyman $\alpha$ (UV)};

  % --- Hộp công thức định luật Bohr ---
  \node[draw, rounded corners=3pt, fill=blue!5, font=\small, inner sep=4pt]
        at (0, -4.9) {Công thức mức năng lượng: $E_n = -\dfrac{13{,}6}{n^2}\text{ eV} \qquad hf = E_m - E_n$};
\end{tikzpicture}
```

---

#### Mẫu T38 — Minh họa hình học Định lý Pythagore (3 hình vuông trên tam giác vuông)

**Lớp áp dụng:** 8  
**Kết quả:** Tam giác vuông $ABC$ tại $A$. Trên 3 cạnh $BC, CA, AB$ dựng ra ngoài 3 hình vuông tương ứng có diện tích $a^2, b^2, c^2$ được tô 3 màu nhạt khác nhau (xanh lá, cam, xanh dương); ký hiệu góc vuông và công thức $a^2 = b^2 + c^2$.

```latex
% ===== T38: Minh họa hình học Định lý Pythagore =====
% Tham số có thể thay đổi:
%   Độ dài cạnh b (AC) và c (AB)
%   Màu sắc tô 3 hình vuông
%   Tên các đỉnh tam giác và nhãn diện tích S1, S2, S3
\begin{tikzpicture}[line width=0.9pt, font=\small, scale=0.85]
  % --- Tọa độ các đỉnh của tam giác vuông ABC ---
  % Tam giác vuông tại A, cạnh b = AC = 4, cạnh c = AB = 3, cạnh huyền a = BC = 5
  \coordinate (A) at (0, 0);
  \coordinate (B) at (0, 3);
  \coordinate (C) at (4, 0);

  % --- Tọa độ các đỉnh 3 hình vuông dựng ra ngoài ---
  % Hình vuông trên cạnh AB (c = 3)
  \coordinate (B1) at (-3, 3);
  \coordinate (A1) at (-3, 0);

  % Hình vuông trên cạnh AC (b = 4)
  \coordinate (C1) at (4, -4);
  \coordinate (A2) at (0, -4);

  % Hình vuông trên cạnh huyền BC (a = 5)
  \coordinate (B2) at (3, 7);
  \coordinate (C2) at (7, 4);

  % --- Vẽ & tô màu 3 hình vuông ---
  % 1. Hình vuông trên cạnh AB (xanh lá nhạt)
  \filldraw[fill=green!20, draw=green!60!black, line width=0.9pt]
        (A) -- (B) -- (B1) -- (A1) -- cycle;
  \node[font=\bfseries, text=green!60!black] at (-1.5, 1.5) {$S_2 = c^2$};

  % 2. Hình vuông trên cạnh AC (cam nhạt)
  \filldraw[fill=orange!20, draw=orange!70!black, line width=0.9pt]
        (A) -- (C) -- (C1) -- (A2) -- cycle;
  \node[font=\bfseries, text=orange!70!black] at (2, -2) {$S_1 = b^2$};

  % 3. Hình vuông trên cạnh huyền BC (xanh dương nhạt)
  \filldraw[fill=blue!15, draw=blue!70!black, line width=0.9pt]
        (B) -- (C) -- (C2) -- (B2) -- cycle;
  \node[font=\bfseries, text=blue!70!black] at (3.5, 3.5) {$S_3 = a^2$};

  % --- Vẽ tam giác ABC nổi bật ---
  \filldraw[fill=gray!15, draw=black, line width=1.2pt]
        (A) -- (B) -- (C) -- cycle;

  % --- Ký hiệu góc vuông tại A ---
  \draw[line width=0.8pt] (0, 0.35) -- (0.35, 0.35) -- (0.35, 0);

  % --- Nhãn các đỉnh & độ dài các cạnh ---
  \node[below left=2pt] at (A) {$A$};
  \node[above left=2pt] at (B) {$B$};
  \node[below right=2pt] at (C) {$C$};

  \node[right=2pt] at (0, 1.5) {$c$};
  \node[above=2pt] at (2, 0) {$b$};
  \node[below left=2pt] at (2, 1.5) {$a$};

  % --- Hộp chú thích định lý ---
  \node[draw, rounded corners=3pt, fill=yellow!20, font=\small, inner sep=4pt]
        at (2, -5.2) {Định lý Pythagore: $a^2 = b^2 + c^2 \iff S_3 = S_1 + S_2$};
\end{tikzpicture}
```

---

#### Mẫu T39 — Thiết diện hình chóp cắt bởi mặt phẳng qua 3 điểm

**Lớp áp dụng:** 11  
**Kết quả:** Hình chóp tứ giác $S.ABCD$. Ba điểm $M \in SA, N \in SB, P \in SC$. Dựng giao điểm $Q = (MNP) \cap SD$ qua giao tuyến phụ với mặt phẳng trung gian $(SBD)$ và tâm đáy $O$; thiết diện $MNPQ$ được tô màu nổi bật; nét thấy liền 0.9pt, nét khuất đứt 0.6pt, đường dựng nét đứt mỏng.

```latex
% ===== T39: Thiết diện hình chóp cắt bởi mặt phẳng qua 3 điểm =====
% Tham số có thể thay đổi:
%   Tọa độ các đỉnh hình chóp S.ABCD
%   Tỉ lệ vị trí các điểm M trên SA, N trên SB, P trên SC
%   Màu sắc tô thiết diện MNPQ
\begin{tikzpicture}[line width=0.9pt, font=\small, scale=1.1]
  \usetikzlibrary{calc}

  % --- Tọa độ các đỉnh của hình chóp S.ABCD ---
  \coordinate (A) at (1.2, 1.2);   % Đỉnh góc trong (khuất)
  \coordinate (B) at (0, -0.6);    % Đỉnh trước trái
  \coordinate (C) at (4.5, -0.6);  % Đỉnh trước phải
  \coordinate (D) at (5.5, 1.2);   % Đỉnh sau phải
  \coordinate (S) at (2.4, 4.6);   % Đỉnh chóp S

  % --- Giao điểm 2 đường chéo đáy O = AC \cap BD ---
  \coordinate (O) at (intersection of A--C and B--D);

  % --- Các điểm M \in SA, N \in SB, P \in SC ---
  \coordinate (M) at ($(S)!0.55!(A)$);
  \coordinate (N) at ($(S)!0.65!(B)$);
  \coordinate (P) at ($(S)!0.45!(C)$);

  % --- Dựng điểm phụ I = MP \cap SO ---
  \coordinate (I) at (intersection of M--P and S--O);

  % --- Dựng giao điểm Q = NI \cap SD (đỉnh thứ 4 của thiết diện) ---
  \coordinate (Q) at (intersection of N--I and S--D);

  % --- Tô màu thiết diện MNPQ ---
  \fill[cyan!25, opacity=0.7] (M) -- (N) -- (P) -- (Q) -- cycle;

  % --- Các cạnh đáy ---
  \draw[dashed, line width=0.6pt] (A) -- (B);
  \draw[dashed, line width=0.6pt] (A) -- (D);
  \draw[line width=0.9pt] (B) -- (C) -- (D);

  % --- Đường chéo đáy & đường phụ SO (nét đứt mỏng) ---
  \draw[dashed, gray!80, line width=0.5pt] (A) -- (C);
  \draw[dashed, gray!80, line width=0.5pt] (B) -- (D);
  \draw[dashed, gray!80, line width=0.5pt] (S) -- (O);

  % --- Đường dựng phụ tìm I và Q (nét đứt) ---
  \draw[dashed, orange!80!black, line width=0.6pt] (M) -- (P);
  \draw[dashed, orange!80!black, line width=0.6pt] (N) -- (Q);

  % --- Các cạnh bên hình chóp ---
  \draw[dashed, line width=0.6pt] (S) -- (A);  % SA khuất
  \draw[line width=0.9pt] (S) -- (B);          % SB thấy
  \draw[line width=0.9pt] (S) -- (C);          % SC thấy
  \draw[line width=0.9pt] (S) -- (D);          % SD thấy

  % --- Các cạnh của thiết diện MNPQ ---
  \draw[dashed, teal!80!black, line width=1.1pt] (M) -- (Q);  % Cạnh khuất
  \draw[dashed, teal!80!black, line width=1.1pt] (M) -- (N);  % Cạnh mặt sau
  \draw[line width=1.1pt, teal!80!black] (N) -- (P);          % Cạnh thấy mặt SBC
  \draw[line width=1.1pt, teal!80!black] (P) -- (Q);          % Cạnh thấy mặt SCD

  % --- Đánh dấu các điểm ---
  \foreach \p/\pos in {S/above, A/above left, B/below left, C/below right, D/right, O/below, I/right, M/left, N/left, P/right, Q/right} {
    \fill (\p) circle (1.5pt);
    \node[\pos=2pt, font=\scriptsize] at (\p) {$\p$};
  }

  % Điểm Q nổi bật (kết quả tìm kiếm)
  \fill[red] (Q) circle (2pt);
  \node[right=2pt, red, font=\footnotesize\bfseries] at (Q) {$Q$};

  % --- Hộp chú thích thuật toán tìm thiết diện ---
  \node[draw, rounded corners=3pt, fill=blue!5, font=\scriptsize, inner sep=3pt]
        at (2.7, -1.4) {Dựng: $O = AC \cap BD \;\to\; I = MP \cap SO \;\to\; Q = NI \cap SD \;\implies\; \text{Thiết diện là } MNPQ$};
\end{tikzpicture}
```

---

#### Mẫu T40 — Đồ thị trên thang bán logarithm (Semi-log plot)

**Lớp áp dụng:** 12 nâng cao / chuyên  
**Kết quả:** Hệ tọa độ bán logarit (semi-log) với trục $x$ tuyến tính, trục $y$ theo thang $\log_{10}$ ($1, 10, 100, 1000$); đường biểu diễn hàm số mũ $y = y_0 \cdot 10^{kt}$ thẳng hàng đặc trưng; lưới logarit với vạch chia co cụm chuẩn khoa học.

```latex
% ===== T40: Đồ thị trên thang bán logarithm (Semi-log plot) =====
% Tham số có thể thay đổi:
%   Hàm số mũ (tăng trưởng hoặc phân rã/suy giảm)
%   Miền giá trị xmin, xmax, ymin, ymax
%   Nhãn trục đại lượng (thời gian, nồng độ, số hạt...)
\begin{tikzpicture}[line width=0.9pt, font=\small]
  \begin{semilogyaxis}[
    width=8.5cm, height=7cm,
    grid=both,
    grid style={line width=0.3pt, draw=gray!30},
    major grid style={line width=0.6pt, draw=gray!60},
    minor y tick num=8,
    xlabel={Thời gian $t$ (giờ)},
    ylabel={Số lượng vi khuẩn $N(t)$},
    xlabel style={font=\small, at={(axis description cs:0.5,-0.08)}, anchor=north},
    ylabel style={font=\small, at={(axis description cs:-0.12,0.5)}, anchor=south},
    xmin=0, xmax=6,
    ymin=1, ymax=1000,
    xtick={0, 1, 2, 3, 4, 5, 6},
    ytick={1, 10, 100, 1000},
    yticklabels={$1$, $10$, $100$, $1000$},
    tick label style={font=\footnotesize},
    legend pos=north west,
    legend cell align=left,
    legend style={font=\scriptsize, fill=white, fill opacity=0.9, draw=gray!50}
  ]
    % --- Đường biểu diễn tăng trưởng mũ (thẳng trên thang semi-log) ---
    % N(t) = 2 * 10^(0.45 * t)
    \addplot[domain=0:5.8, samples=50, red!80!black, line width=1.3pt]
        { 2 * 10^(0.45 * x) };
    \addlegendentry{Tăng trưởng: $N_1(t) = 2 \cdot 10^{0{,}45 t}$}

    % --- Đường biểu diễn suy giảm mũ (phóng xạ / thuốc giảm nồng độ) ---
    % N(t) = 800 * 10^(-0.4 * t)
    \addplot[domain=0:5.8, samples=50, blue!80!black, line width=1.3pt, dashed]
        { 800 * 10^(-0.42 * x) };
    \addlegendentry{Phân rã: $N_2(t) = 800 \cdot 10^{-0{,}42 t}$}

    % --- Đánh dấu điểm mốc trên đường tăng trưởng ---
    \addplot[mark=*, mark size=2pt, red!80!black] coordinates {(0, 2) (2, 15.85) (4, 126)};
    \node[above left, font=\scriptsize, red!80!black] at (axis cs:0, 2) {$(0; 2)$};
    \node[below right, font=\scriptsize, red!80!black] at (axis cs:4, 126) {$(4; 126)$};

    % --- Chú thích bản chất hàm số mũ trên thang log ---
    \node[draw, rounded corners=2pt, fill=yellow!15, font=\scriptsize, inner sep=3pt]
        at (axis cs:3.2, 15) {$\log_{10} y = \log_{10} y_0 + kt$ (tuyến tính)};
  \end{semilogyaxis}
\end{tikzpicture}
```

---

*Tổng cộng: **80 mẫu TikZ** (39 Toán + 22 Vật lý + 13 Hóa học + 3 phụ lục Toán + 3 phụ lục khác)*  
*File được tạo tự động bởi Antigravity AI — phiên bản 1.3 (cập nhật 2026-09)*
