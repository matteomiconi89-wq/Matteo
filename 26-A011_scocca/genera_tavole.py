#!/usr/bin/env python3
# Genera le tavole SVG quotate della scocca 26A011 (misure reali in mm dai DXF).
import math

FMT = lambda v: str(int(round(v)))

class Sheet:
    def __init__(self, vw, vh, sx, sy, ox, oy, flipy=False):
        self.vw, self.vh = vw, vh
        self.sx, self.sy, self.ox, self.oy = sx, sy, ox, oy
        self.flipy = flipy
        self.parts = []

    def X(self, mm): return self.ox + mm * self.sx
    def Y(self, mm):
        return self.oy - mm * self.sy if self.flipy else self.oy + mm * self.sy

    def raw(self, s): self.parts.append(s)

    def line(self, x1, y1, x2, y2, cls):
        self.raw(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" class="{cls}"/>')

    def mline(self, mx1, my1, mx2, my2, cls):
        self.line(self.X(mx1), self.Y(my1), self.X(mx2), self.Y(my2), cls)

    def rect(self, mx, my, mw, mh, cls, rx=0):
        x = self.X(mx); y = self.Y(my + mh) if self.flipy else self.Y(my)
        w = mw * self.sx; h = mh * self.sy
        r = f' rx="{rx}"' if rx else ''
        self.raw(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" class="{cls}"{r}/>')

    def prect(self, x, y, w, h, cls):
        self.raw(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" class="{cls}"/>')

    def circle(self, mx, my, rmm, cls):
        self.raw(f'<circle cx="{self.X(mx):.1f}" cy="{self.Y(my):.1f}" r="{rmm*self.sx:.1f}" class="{cls}"/>')

    def poly(self, pts_mm, cls, close=True):
        p = " ".join(f"{self.X(a):.1f},{self.Y(b):.1f}" for a, b in pts_mm)
        tag = "polygon" if close else "polyline"
        self.raw(f'<{tag} points="{p}" class="{cls}"/>')

    def text(self, x, y, s, cls, anchor="middle", rot=None):
        t = f' transform="rotate({rot} {x:.1f} {y:.1f})"' if rot is not None else ''
        self.raw(f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" class="{cls}"{t}>{s}</text>')

    def tick(self, x, y):
        self.line(x - 4.5, y + 4.5, x + 4.5, y - 4.5, "dim")

    def dimh(self, m1, m2, ypx, ext_to=None, label=None, cls_t="dimt", above=True):
        x1, x2 = self.X(m1), self.X(m2)
        if ext_to is not None:
            e1, e2 = ext_to
            self.line(x1, self.Y(e1) + (0), x1, ypx + (5 if above else -5), "ext")
            self.line(x2, self.Y(e2) + (0), x2, ypx + (5 if above else -5), "ext")
        self.line(x1 - 5, ypx, x2 + 5, ypx, "dim")
        self.tick(x1, ypx); self.tick(x2, ypx)
        lab = label if label is not None else FMT(abs(m2 - m1))
        ty = ypx - 5 if above else ypx + 15
        self.text((x1 + x2) / 2, ty, lab, cls_t)

    def dimv(self, m1, m2, xpx, ext_to=None, label=None, side="left"):
        y1, y2 = self.Y(m1), self.Y(m2)
        if ext_to is not None:
            e1, e2 = ext_to
            self.line(self.X(e1), y1, xpx + (5 if side == "left" else -5), y1, "ext")
            self.line(self.X(e2), y2, xpx + (5 if side == "left" else -5), y2, "ext")
        self.line(xpx, min(y1, y2) - 5, xpx, max(y1, y2) + 5, "dim")
        self.tick(xpx, y1); self.tick(xpx, y2)
        lab = label if label is not None else FMT(abs(m2 - m1))
        tx = xpx - 6 if side == "left" else xpx + 6
        rot = -90
        self.text(tx, (y1 + y2) / 2, lab, "dimt", rot=rot)

    def svg(self, title):
        body = "\n".join(self.parts)
        return (f'<svg viewBox="0 0 {self.vw} {self.vh}" role="img" aria-label="{title}" '
                f'preserveAspectRatio="xMidYMid meet">\n{body}\n</svg>')


# ============================================================ TAV.02 PIANTA APERTA
def pianta_aperta():
    s = 1 / 11.0
    ox, oy = 108, 132          # top-left of drawing area; plan Y grows downward from cucina(top)
    # plan: X mm -> right; Y mm (0..4840) with cucina (4840) at TOP -> py = oy + (4840-y)*s
    sh = Sheet(1512, 760, s, s, ox, oy + 4840 * s, flipy=True)  # Y(mm) measured from bottom
    Yb = sh.Y  # y in mm plan coords (0=ingresso side)

    # zone tints (before lines)
    sh.rect(919, 1213, 10199 - 919, 2390, "tintA")
    sh.rect(10279, 1213, 11184 - 10279, 2390, "tintB")
    sh.rect(11265, 1213, 13928 - 11265, 2390, "tintC")
    sh.rect(977, 61, 3835 - 977, 1150 - 61, "tintI")   # baia ingresso mod. anteriore
    sh.rect(4382, 61, 13510 - 4382, 1150 - 61, "tintI")
    sh.rect(977, 3690, 3835 - 977, 4779 - 3690, "tintK")
    sh.rect(4382, 3690, 13510 - 4382, 4779 - 3690, "tintK")

    # wheels (below floor) dashed
    for cx in (9536, 11236):
        for cy in (1494, 3475):
            sh.rect(cx - 475, cy - 220, 950, 440, "ghost")

    # fixed body (cassone)
    sh.rect(0, 1150, 897, 2540, "s0")                       # front block
    for x0, x1 in ((3915, 4302), (13590, 13928)):           # pillars
        sh.rect(x0, 1150, x1 - x0, 63, "s0")
        sh.rect(x0, 3603, x1 - x0, 87, "s0")
    sh.rect(13928, 1150, 61, 2540, "s0")                    # rear wall
    # body edge projection (rails above/below) dashed
    for y in (1150, 1213, 3603, 3690):
        sh.mline(897, y, 3915, y, "dash")
        sh.mline(4302, y, 13590, y, "dash")

    # slide-out INGRESSO (bottom, wall at y 0-61)
    for x0, x1 in ((917, 3895), (4322, 13570)):
        sh.rect(x0, 0, x1 - x0, 61, "s1")
    for x0 in (917, 3835, 4322, 13510):                     # end walls
        sh.rect(x0, 61, 60, 1150 - 61, "s1")
    sh.rect(9634, 10, 11204 - 9634, 42, "gl")               # window band glass
    sh.rect(943, 705, 10, 420, "gl")                        # glass insert in front end wall
    # slide-out CUCINA (top, wall at y 4779-4840)
    for x0, x1 in ((917, 3895), (4322, 13570)):
        sh.rect(x0, 4779, x1 - x0, 61, "s1")
    for x0 in (917, 3835, 4322, 13510):
        sh.rect(x0, 3690, 60, 4779 - 3690, "s1")
    for x0, x1 in ((2659, 3529), (5679, 7949), (9059, 9779), (10799, 11769)):
        sh.rect(x0, 4789, x1 - x0, 42, "gl")
    sh.rect(943, 3715, 10, 420, "gl")

    # partitions (divisori)
    sh.rect(8303, 3603, 40, 1176, "dv")
    sh.rect(9401, 61, 40, 1152, "dv")
    sh.rect(9836, 3603, 11811 - 9836, 40, "dv")
    sh.rect(10199, 1213, 80, 2390, "dv")
    sh.rect(10503, 3603, 40, 1176, "dv")
    sh.rect(11184, 1213, 81, 2390, "dv")
    sh.rect(11329, 61, 58, 1152, "dv")
    sh.rect(8327, 3603, 9002 - 8327, 40, "dvh")             # upper panel (da +715 dal pav.)

    # rear glass enclosure
    sh.rect(11816, 3701, 18, 537, "gl")
    sh.rect(12648, 3633, 18, 605, "gl")
    sh.rect(12668, 3604, 13457 - 12668, 10, "gl")

    # skylights + clima dashed
    for x0, x1, y0, y1 in ((1318,1968,2120,2720),(4921,5701,2120,2720),(6303,7595,2095,2745),(8287,9027,2120,2720),(12302,12992,2120,2720)):
        sh.rect(x0, y0, x1 - x0, y1 - y0, "ghostb")
    for x0 in (1651, 9392):
        sh.rect(x0, 1698, 900, 3270 - 1698, "ghost")

    # ---- labels
    def lab(mx, my, t, cls="lbl"):
        sh.text(sh.X(mx), sh.Y(my), t, cls)
    lab(5550, 2500, "ZONA A", "zl"); lab(5550, 2190, "9.280 × 2.390 · h 2.251", "lbl")
    lab(10730, 2620, "ZONA B", "zl2"); lab(10730, 2330, "905 × 2.390", "lbl")
    lab(12600, 2500, "ZONA C", "zl"); lab(12600, 2190, "2.663 × 2.390", "lbl")
    lab(2400, 530, "BAIA INGRESSO · MOD. ANTERIORE", "lbls"); lab(2400, 300, "2.858 × 1.089", "lbl")
    lab(6900, 530, "BAIA INGRESSO · profondità utile 1.152", "lbls")
    lab(2400, 4310, "BAIA CUCINA · MOD. ANTERIORE", "lbls"); lab(2400, 4060, "2.858 × 1.089", "lbl")
    lab(6300, 4310, "BAIA CUCINA · profondità utile 1.176", "lbls")
    lab(448, 2420, "VANO", "lblw"); lab(448, 2180, "TECNICO", "lblw")
    sh.text(sh.X(6303 + 646), sh.Y(2420) - 4, "oblò ×5", "lblg")
    sh.text(sh.X(2101), sh.Y(2484), "clima", "lblg")
    sh.text(sh.X(9842), sh.Y(2484), "clima", "lblg")
    sh.text(sh.X(13060), sh.Y(3980), "vetrata", "lblg")
    sh.text(sh.X(10419), sh.Y(180), "vetrina", "lblg")
    sh.text(sh.X(9214), sh.Y(4990) + 0, "vetrine", "lblg")

    # ---- dimensions (top: cucina side)  ypx above drawing
    ytop = Yb(4840)
    sh.dimh(0, 13989, ytop - 96, ext_to=(4840, 4840) if False else None)
    sh.line(sh.X(0), Yb(3690), sh.X(0), ytop - 101, "ext")
    sh.line(sh.X(13989), Yb(3690), sh.X(13989), ytop - 101, "ext")
    row2 = ytop - 62
    for a, b in ((0, 917), (917, 3895), (3895, 4322), (4322, 13570), (13570, 13989)):
        sh.dimh(a, b, row2)
    for x in (0, 917, 3895, 4322, 13570, 13989):
        sh.line(sh.X(x), ytop - 12, sh.X(x), row2 + 5, "ext")
    row3 = ytop - 28
    for a, b in ((4322 + 60, 8303), (8343, 10503), (10543, 13570 - 60)):
        sh.dimh(a, b, row3)
    for x in (4382, 8303, 8343, 10503, 10543, 13510):
        sh.line(sh.X(x), ytop - 12, sh.X(x), row3 + 5, "ext")

    # bottom dims (ingresso side)
    ybot = Yb(0)
    rowb1 = ybot + 34
    for a, b in ((4382, 9401), (9441, 11329), (11387, 13510)):
        sh.dimh(a, b, rowb1, above=False)
    for x in (4382, 9401, 9441, 11329, 11387, 13510):
        sh.line(sh.X(x), ybot + 12, sh.X(x), rowb1 - 5, "ext")
    rowb2 = ybot + 70
    for a, b in ((919, 10199), (10279, 11184), (11265, 13928)):
        sh.dimh(a, b, rowb2, above=False)
    for x in (919, 10199, 10279, 11184, 11265, 13928):
        sh.line(sh.X(x), ybot + 12, sh.X(x), rowb2 - 5, "ext")

    # left vertical dims
    xl = sh.X(0) - 34
    sh.dimv(0, 1150, xl); sh.dimv(1150, 3690, xl); sh.dimv(3690, 4840, xl)
    for y in (0, 1150, 3690, 4840):
        sh.line(sh.X(0) - 8, Yb(y), xl - 5, Yb(y), "ext")
    xl2 = xl - 36
    sh.dimv(0, 4840, xl2)
    sh.line(sh.X(0) - 8, Yb(0), xl2 - 5, Yb(0), "ext")
    sh.line(sh.X(0) - 8, Yb(4840), xl2 - 5, Yb(4840), "ext")
    # right vertical dims (interior)
    xr = sh.X(13989) + 40
    sh.dimv(61, 1213, xr, side="right"); sh.dimv(1213, 3603, xr, side="right"); sh.dimv(3603, 4779, xr, side="right")
    for y in (61, 1213, 3603, 4779):
        sh.line(sh.X(13570 if y in (61, 4779) else 13989) + 6, Yb(y), xr + 5, Yb(y), "ext")

    # side captions + scale bar + axes
    sh.text(sh.X(6995), ytop - 116, "LATO CUCINA — estrattore aperto (+1.150)", "cap")
    sh.text(sh.X(6995), ybot + 100, "LATO INGRESSO — estrattore aperto (+1.150)", "cap")
    sh.text(sh.X(-680), Yb(2420), "FRONTE", "cap", rot=-90);
    sh.text(sh.X(14620), Yb(2420), "RETRO", "cap", rot=90)
    # scale bar 2 m
    bx, by = sh.X(0), 740
    for i in range(4):
        sh.prect(bx + i * (500 * s), by - 8, 500 * s, 8, "sb0" if i % 2 == 0 else "sb1")
    sh.text(bx, by + 14, "0", "dimt", anchor="middle"); sh.text(bx + 2000 * s, by + 14, "2 m", "dimt")
    return sh.svg("Pianta configurazione aperta")


# ============================================================ TAV.03 SEZIONE TRASVERSALE
def sezione():
    s = 1 / 7.2
    sh = Sheet(950, 700, s, s, 118, 640, flipy=True)  # X: y-plan mm (0..4840) ; Y: z mm
    Xm, Ym = sh.X, sh.Y

    # ground
    sh.line(Xm(-500), Ym(0), Xm(5340), Ym(0), "s0l")
    for gx in range(-450, 5301, 150):
        sh.line(Xm(gx), Ym(0), Xm(gx - 90), Ym(0) + 9, "hair")

    # wheels behind (section at X=7000 -> wheels are proj.)
    for cy in (1494, 3475):
        sh.circle(cy, 475, 475, "ghostc")

    # chassis beams
    for y0 in (1835, 3005):
        sh.rect(y0, 830, 90, 120, "s0")
    # floor package + finished floor
    sh.rect(1151, 950, 2538, 393, "s1")
    sh.rect(0, 1343, 4840, 52, "wood")
    # fixed body rails
    sh.rect(1213, 950, 63, 393, "s0"); sh.rect(3527, 950, 63, 393, "s0")
    sh.rect(1150, 3646, 63, 39, "s0"); sh.rect(3603, 3646, 87, 39, "s0")
    # controsoffitto + roof
    sh.rect(1213, 3646, 2390, 39, "s2")
    sh.rect(1150, 3685, 2540, 315, "s1")
    # skylight (section passes through oblò 6303-7595)
    sh.rect(2095, 3644, 650, 358, "gl")
    # slide-out ingresso (left, y 0-61) — solid band at this X
    sh.rect(0, 1092, 61, 251, "s1")
    sh.rect(0, 1343, 61, 1052, "s1")
    sh.rect(0, 2395, 61, 647, "s1")
    sh.rect(0, 3042, 61, 568, "s1")
    # slide-out cucina (right, y 4779-4840) — glass band at this X
    sh.rect(4779, 1092, 61, 251, "s1")
    sh.rect(4779, 1343, 61, 1052, "s1")
    sh.rect(4800, 2395, 20, 647, "gl")
    sh.rect(4779, 3042, 61, 568, "s1")
    # inclined roofs (real profile)
    sh.poly([(61, 3498), (1301, 3546), (1301, 3624), (61, 3576)], "s1")
    sh.poly([(4779, 3498), (3539, 3546), (3539, 3624), (4779, 3576)], "s1")

    # human figure (1750) inside central zone
    hx, hz = 2900, 1395
    sh.circle(hx, hz + 1630, 115, "man")
    sh.poly([(hx - 150, hz), (hx - 60, hz), (hx - 55, hz + 780), (hx + 55, hz + 780), (hx + 60, hz), (hx + 150, hz),
             (hx + 165, hz + 900), (hx + 245, hz + 1180), (hx + 170, hz + 1440), (hx - 170, hz + 1440), (hx - 245, hz + 1180), (hx - 165, hz + 900)], "man")
    sh.text(Xm(hx), Ym(hz + 1750) - 26, "1.750", "dimt")

    # interior height dims
    sh.dimv(1395, 3646, Xm(2420), side="left", label="2.251")
    sh.dimv(1395, 3498, Xm(340), side="left", label="2.103")
    sh.dimv(1395, 3546, Xm(1120), side="left", label="2.151")
    sh.dimv(1395, 2395, Xm(4560), side="left", label="1.000")
    sh.dimv(2395, 3042, Xm(4560), side="left", label="647")
    for z in (2395, 3042):
        sh.line(Xm(4779), Ym(z), Xm(4560) - 5, Ym(z), "ext")
    # exterior dims right
    xr = Xm(5120)
    sh.dimv(0, 950, xr, side="right"); sh.dimv(950, 1395, xr, side="right", label="445")
    sh.dimv(1395, 4000, xr, side="right", label="2.605")
    xr2 = Xm(5330)
    sh.dimv(0, 4000, xr2, side="right", label="4.000")
    for z in (0, 950, 1395, 4000):
        sh.line(Xm(4850), Ym(z), xr + 5, Ym(z), "ext")
    sh.line(Xm(4850), Ym(4000), xr2 + 5, Ym(4000), "ext")
    sh.line(Xm(4850), Ym(0), xr2 + 5, Ym(0), "ext")
    # width dims top
    yt = Ym(4002) - 46
    sh.dimh(0, 4840, yt, label="4.840")
    sh.line(Xm(0), Ym(3610), Xm(0), yt + 5, "ext"); sh.line(Xm(4840), Ym(3610), Xm(4840), yt + 5, "ext")
    yt2 = Ym(4002) - 18
    sh.dimh(1150, 3690, yt2, label="2.540")
    sh.line(Xm(1150), Ym(4000), Xm(1150), yt2 + 5, "ext"); sh.line(Xm(3690), Ym(4000), Xm(3690), yt2 + 5, "ext")
    sh.dimh(0, 1150, yt2, label="1.150"); sh.dimh(3690, 4840, yt2, label="1.150")
    # floor height left
    sh.dimv(0, 1395, Xm(-320), side="left", label="1.395")
    sh.line(Xm(0), Ym(0), Xm(-320) - 5, Ym(0), "ext"); sh.line(Xm(0), Ym(1395), Xm(-320) - 5, Ym(1395), "ext")

    sh.text(Xm(610), Ym(700), "BAIA INGRESSO", "lbls")
    sh.text(Xm(4230), Ym(700), "BAIA CUCINA", "lbls")
    sh.text(Xm(610)+0, Ym(430), "sez. estrattore", "lblg")
    sh.text(Xm(4230), Ym(430), "sez. estrattore", "lblg")
    sh.text(Xm(2420), Ym(240), "carrello · Ø ruote 950", "lblg")
    sh.text(Xm(2420), Ym(4160), "oblò", "lblg")
    sh.text(Xm(4810) - 0, Ym(2718), "", "lblg")
    return sh.svg("Sezione trasversale, configurazione aperta")


# ============================================================ TAV.04 PROSPETTO LATERALE
def prospetto():
    s = 1 / 11.0
    sh = Sheet(1512, 560, s, s, 108, 480, flipy=True)
    Xm, Ym = sh.X, sh.Y
    # ground
    sh.line(Xm(-700), Ym(0), Xm(14900), Ym(0), "s0l")
    for gx in range(-650, 14851, 260):
        sh.line(Xm(gx), Ym(0), Xm(gx - 140), Ym(0) + 9, "hair")
    # roof + front/rear fixed body above slide-out
    sh.rect(0, 3685, 13989, 315, "s1")
    sh.rect(0, 141, 897, 3544, "s0")
    sh.rect(13928, 1080, 61, 2605, "s0")
    sh.rect(13590, 1395, 338, 2290, "s0")
    sh.rect(3915, 1395, 387, 2290, "s0")
    # chassis line
    sh.rect(654, 830, 13335, 120, "s0")
    # slide-out cucina face (open): skirt+wall bands, X 917-3895 / 4322-13570
    for x0, x1 in ((917, 3895), (4322, 13570)):
        sh.rect(x0, 1092, x1 - x0, 251, "s1")
        sh.rect(x0, 1343, x1 - x0, 1052, "s1")
        sh.rect(x0, 3042, x1 - x0, 568, "s1")
        sh.poly([(x0, 3498), (x1, 3498), (x1, 3576), (x0, 3576)], "s1")  # inclined roof edge
    # window band: wall vs glass
    sh.rect(917, 2395, 3895 - 917, 647, "s1")
    for a, b in ((3529, 3895), (4322, 5679), (7949, 9059), (9779, 10799), (11769, 13570)):
        sh.rect(a, 2395, b - a, 647, "s1")
    for a, b in ((2659, 3529), (5679, 7949), (9059, 9779), (10799, 11769)):
        sh.rect(a, 2395, b - a, 647, "gl")
    # clima on roof
    sh.rect(1651, 3685, 900, 275, "s2")
    sh.rect(9392, 3685, 900, 275, "s2")
    sh.text(Xm(2101), Ym(3810), "clima", "lblg"); sh.text(Xm(9842), Ym(3810), "clima", "lblg")
    # wheels
    for cx in (9536, 11236):
        sh.circle(cx, 475, 475, "wheel")
        sh.circle(cx, 475, 260, "wheelh")
    # floor line dashed
    sh.mline(654, 1395, 13928, 1395, "dashr")
    sh.text(Xm(1900), Ym(1395) + 16, "piano pavimento +1.395", "lblg", anchor="start")
    # human on ground
    hx = -430
    sh.circle(hx, 1630, 115, "man")
    sh.poly([(hx - 150, 0), (hx - 60, 0), (hx - 55, 780), (hx + 55, 780), (hx + 60, 0), (hx + 150, 0),
             (hx + 165, 900), (hx + 245, 1180), (hx + 170, 1440), (hx - 170, 1440), (hx - 245, 1180), (hx - 165, 900)], "man")
    # dims
    yt = Ym(4002) - 40
    sh.dimh(0, 13989, yt, label="13.989")
    sh.line(Xm(0), Ym(4000), Xm(0), yt + 5, "ext"); sh.line(Xm(13989), Ym(3685), Xm(13989), yt + 5, "ext")
    yb = Ym(0) + 40
    for a, b, lab in ((0, 9536, "9.536"), (9536, 11236, "1.700"), (11236, 13989, "2.753")):
        sh.dimh(a, b, yb, above=False, label=lab)
    for x in (0, 9536, 11236, 13989):
        sh.line(Xm(x), Ym(0) + 12, Xm(x), yb - 5, "ext")
    xr = Xm(14420)
    sh.dimv(0, 4000, xr, side="right", label="4.000")
    sh.line(Xm(13989), Ym(4000), xr + 5, Ym(4000), "ext"); sh.line(Xm(14280), Ym(0), xr + 5, Ym(0), "ext")
    sh.dimv(2395, 3042, Xm(14140), side="right", label="647")
    sh.line(Xm(13989), Ym(2395), Xm(14140) + 5, Ym(2395), "ext"); sh.line(Xm(13989), Ym(3042), Xm(14140) + 5, Ym(3042), "ext")
    sh.text(Xm(6995), 30, "VISTA LATO CUCINA — configurazione aperta", "cap")
    sh.text(Xm(450), Ym(2000), "vano tecnico", "lblg", rot=-90)
    return sh.svg("Prospetto laterale, lato cucina")


# ============================================================ TAV.05 PIANTA CHIUSA
def pianta_chiusa():
    s = 1 / 11.0
    sh = Sheet(1512, 420, s, s, 108, 96 + 2540 * s, flipy=True)
    Yb = sh.Y
    # translate: plan y (1150..3690) -> shift to 0..2540
    def R(mx, my, mw, mh, cls): sh.rect(mx, my - 1150, mw, mh, cls)
    R(0, 1150, 897, 2540, "s0")
    for x0, x1 in ((3915, 4302), (13590, 13928)):
        R(x0, 1150, x1 - x0, 63, "s0"); R(x0, 3603, x1 - x0, 87, "s0")
    R(13928, 1150, 61, 2540, "s0")
    for y in (1150, 3690):
        sh.mline(897, y - 1150, 3915, y - 1150, "hair"); sh.mline(4302, y - 1150, 13590, y - 1150, "hair")
    # tucked slide-outs
    for x0, x1 in ((917, 3895), (4322, 13570)):
        R(x0, 1150, x1 - x0, 61, "s1"); R(x0, 3629, x1 - x0, 61, "s1")
    for x0 in (917, 3835, 4322, 13510):
        R(x0, 1211, 60, 1089, "s1"); R(x0, 2540, 60, 1089, "s1")
    for a, b in ((2659, 3529), (5679, 7949), (9059, 9779), (10799, 11769)):
        R(a, 3650, b - a, 20, "gl")
    R(9634, 1170, 11204 - 9634, 20, "gl")
    R(10199, 1213, 80, 2390, "dv"); R(11184, 1213, 81, 2390, "dv")
    sh.text(sh.X(6950), Yb(2540 - 1150 - 1270) - 6, "estrattori rientrati — corridoio residuo 240 mm", "lblg")
    # dims
    yt = Yb(2540) - 34
    sh.dimh(0, 13989, yt, label="13.989")
    sh.line(sh.X(0), Yb(2540), sh.X(0), yt + 5, "ext"); sh.line(sh.X(13989), Yb(2540), sh.X(13989), yt + 5, "ext")
    xl = sh.X(0) - 36
    sh.dimv(0, 2540, xl, label="2.540")
    sh.line(sh.X(0) - 8, Yb(0), xl - 5, Yb(0), "ext"); sh.line(sh.X(0) - 8, Yb(2540), xl - 5, Yb(2540), "ext")
    yb2 = Yb(0) + 38
    sh.dimh(9536 - 475, 11236 + 475, yb2, above=False, label="carrello 2 assi · interasse 1.700")
    sh.text(sh.X(6995), Yb(0) + 84, "CONFIGURAZIONE DI MARCIA — sagoma stradale 13.989 × 2.540 × h 4.000", "cap")
    return sh.svg("Pianta configurazione chiusa")


if __name__ == "__main__":
    import pathlib
    base = pathlib.Path(__file__).parent
    for name, fn in (("pianta_aperta", pianta_aperta), ("sezione", sezione),
                     ("prospetto", prospetto), ("pianta_chiusa", pianta_chiusa)):
        out = fn()
        (base / f"tav_{name}.svg").write_text(out)
        print(name, len(out), "bytes")
