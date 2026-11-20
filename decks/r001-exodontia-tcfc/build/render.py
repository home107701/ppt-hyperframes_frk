# -*- coding: utf-8 -*-
"""Layouts dos 20 slides + previa PNG / aba de contato."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import content as C
from engine import (BOT, BODY, CW, FOOT, GRAPH, H, INK, M, ONDARK, RULE, TOP, W,
                    WHITE, Slide, cropped, measure, wrap)

TOTAL = len(C.SLIDES)
E = {}          # render de cada slide, por numero


def reg(fn):
    E[fn.__name__[2:]] = fn
    return fn


def kicker(s, d):
    s.text(M, TOP, d["kicker"].upper(), 8.6, 500, BODY, tracking=1.15, name="kicker")


def foot(s, d):
    s.hline(M, FOOT - 16, 40, RULE, 1.2)
    s.text(M, FOOT, "RADIOLOGIA · TERCEIROS MOLARES", 7.8, 500, BODY, tracking=1.1, name="foot", check=False)
    s.text(W - M - 60, FOOT, "%02d / %02d" % (d["n"], TOTAL), 8.2, 500, BODY, tracking=0.6,
           max_w=60, align="right", name="page", check=False)


def support(s, y, txt, w=440):
    return s.text(M, y, txt, 13, 400, BODY, w, lh=1.5, name="support")


# ------------------------------------------------------------------ 01 capa
@reg
def s_cover(s, d):
    kicker(s, d)
    y, sz, nl = s.title(d["title"], 500, top=126, sizes=(44, 40, 36), maxlines=2)
    sy = y + 34
    last = s.text(M, sy, d["support"], 13, 400, BODY, 428, lh=1.5, name="support")
    ty = last + 40
    s.rect(M, ty, 244, 42, fill=GRAPH)
    s.text(M + 16, ty + 26, d["tab"], 8.4, 500, ONDARK, 212, tracking=1.4, name="tab")
    s.image(d["img"], 606, 54, 354, 372, alt=C.IMG[d["img"]][1])
    s.hline(M, FOOT - 16, 40, RULE, 1.2)
    s.text(M, FOOT, "RADIOLOGIA · TERCEIROS MOLARES", 7.8, 500, BODY, tracking=1.1, name="foot", check=False)
    s.text(W - M - 60, FOOT, "%02d / %02d" % (d["n"], TOTAL), 8.2, 500, BODY, tracking=0.6,
           max_w=60, align="right", name="page", check=False)


# ------------------------------------------------------------------ 02 dois blocos
@reg
def s_two_probes(s, d):
    kicker(s, d)
    y, sz, nl = s.title(d["title"], 700, top=132, sizes=(42, 38, 34))
    top = 282
    cols = [(M, d["left"]), (M + 428, d["right"])]
    for i, (x, (lab, items)) in enumerate(cols):
        if i:
            s.vline(x - 22, top - 24, 150, RULE, 0.75)
        s.text(x, top, lab.upper(), 8.6, 500, BODY, 380, tracking=1.1, name="plab")
        s.hline(x, top + 11, 44, GRAPH, 1.4)
        s.bullets(x, top + 56, items, pt=11.5, gap=20, maxw=380)
    s.text(M, 424, d["foot"], 11.5, 400, BODY, 700, lh=1.45, name="foot_note")
    foot(s, d)


# ------------------------------------------------------------------ 03 passos + nota
@reg
def s_steps_note(s, d):
    kicker(s, d)
    s.title(d["title"], 640, top=112, sizes=(40, 36, 32))
    y = 244
    for i, (lab, txt) in enumerate(d["steps"]):
        s.text(M, y, "%02d" % (i + 1), 8.6, 500, BODY, 26, tracking=0.8, name="num")
        s.text(M + 34, y, lab, 11.5, 700, INK, 520, name="step")
        s.text(M + 34, y + 16, txt, 10.5, 400, BODY, 520, lh=1.4, name="stepd")
        if i:
            s.hline(M, y - 26, 560, RULE, 0.7)
        y += 44
    nx = M + 620
    s.text(nx, 244, d["note"][0], 8.6, 500, BODY, 200, tracking=1.1, name="nlab")
    s.hline(nx, 255, 40, GRAPH, 1.4)
    s.text(nx, 284, d["note"][1], 10.5, 400, BODY, 210, lh=1.5, name="note")
    foot(s, d)


# ------------------------------------------------------------------ 04 tabela 3 col
def table(s, x, y, cols, rows, widths, rh=46, head=9, body=11.2, foot_rule=True):
    s.text(x, y, cols[0].upper(), 8.6, 500, BODY, widths[0], tracking=1.0, name="th0")
    cx = x
    for i, c in enumerate(cols):
        s.text(cx, y, c.upper(), 8.6, 500, BODY, widths[i], tracking=1.0, name="th%d" % i)
        cx += widths[i]
    s.hline(x, y + 12, sum(widths), GRAPH, 1.2)
    yy = y + 40
    for r, row in enumerate(rows):
        cx = x
        for i, cell in enumerate(row):
            s.text(cx, yy, cell, body, 400 if i else 500, INK if i == 0 else BODY,
                   widths[i] - 14, lh=1.35, name="td")
            cx += widths[i]
        if r < len(rows) - 1:
            s.hline(x, yy + 18, sum(widths), RULE, 0.7)
        yy += rh
    if foot_rule:
        s.hline(x, yy - 14, sum(widths), RULE, 0.7)
    return yy


@reg
def s_table_three(s, d):
    kicker(s, d)
    s.title(d["title"], 700, top=132, sizes=(42, 38, 34))
    table(s, M, 268, d["cols"], d["rows"], [232, 236, 376], rh=42, body=11)
    s.text(M, 448, d["foot"], 9, 400, BODY, 780, lh=1.4, name="tnote")
    foot(s, d)


# ------------------------------------------------------------------ 05 metrica + foto
@reg
def s_metric_photo(s, d):
    kicker(s, d)
    s.title(d["title"], 470, top=96, sizes=(42, 38, 34))
    s.image(d["img"], 596, 96, 306, 300, alt=C.IMG[d["img"]][1])
    s.text(M, 284, d["metric_label"].upper(), 8.2, 500, BODY, 300, tracking=1.0, name="mlab")
    s.hline(M, 296, 40, GRAPH, 1.4)
    s.text(M, 344, d["metric"], 46, 700, INK, 420, tracking=-0.9, name="metric")
    s.bullets(M, 384, d["items"], pt=11.5, gap=20, maxw=470)
    foot(s, d)


# ------------------------------------------------------------------ 06 lista + foto esquerda
@reg
def s_list_photo(s, d):
    kicker(s, d)
    s.image(d["img"], M, 96, 388, 268, alt=C.IMG[d["img"]][1])
    x = 494
    s.title(d["title"], 408, top=96, sizes=(40, 36, 32))
    y = 236
    for i, (lab, txt) in enumerate(d["items"]):
        s.text(x, y, lab, 12.5, 500, INK, 408, name="item")
        s.text(x, y + 17, txt, 10.8, 400, BODY, 400, lh=1.4, name="itemd")
        s.hline(x, y + 40, 408, RULE, 0.7)
        y += 62
    foot(s, d)


# ------------------------------------------------------------------ 07 camada focal
@reg
def s_focal_arc(s, d):
    kicker(s, d)
    s.title(d["title"], 560, top=112, sizes=(40, 36, 32))
    cx, cy, r = 480, 380, 190
    seg = 48
    prev = None
    import math
    for i in range(seg + 1):
        a = math.pi * (1 - i / float(seg))
        px, py = cx + r * math.cos(a), cy - r * 0.62 * math.sin(a)
        if prev:
            s.line(prev[0], prev[1], px, py, (43, 43, 46), 1.0)
        prev = (px, py)
    labels = [("Lingual à camada", "Alargado e borrado", 0.16, "left"),
              ("Na camada focal", "Proporção preservada", 0.5, "center"),
              ("Vestibular à camada", "Estreitado e sem nitidez", 0.84, "right")]
    for lab, sub, t, side in labels:
        a = math.pi * (1 - t)
        px, py = cx + r * math.cos(a), cy - r * 0.62 * math.sin(a)
        s.line(px, py - 12, px, py - 4, GRAPH, 1.0)
        s.rect(px - 2, py - 2, 4, 4, fill=INK)
        if side == "left":
            lx = px - 176
            s.text(lx, py - 24, lab.upper(), 8.2, 500, BODY, 160, tracking=1.0, name="flab", align="right")
            s.text(lx, py - 8, sub, 10.2, 400, BODY, 160, lh=1.3, name="fsub", align="right")
        elif side == "right":
            lx = px + 16
            s.text(lx, py - 24, lab.upper(), 8.2, 500, BODY, 170, tracking=1.0, name="flab")
            s.text(lx, py - 8, sub, 10.2, 400, BODY, 170, lh=1.3, name="fsub")
        else:
            s.text(px - 80, py - 44, lab.upper(), 8.2, 500, BODY, 160, tracking=1.0, name="flab", align="center")
            s.text(px - 80, py - 28, sub, 10.2, 400, BODY, 160, lh=1.3, name="fsub", align="center")
    s.text(M, 400, d["foot"], 11, 400, BODY, 250, lh=1.5, name="foot_note")
    foot(s, d)


# ------------------------------------------------------------------ 08 tres colunas
@reg
def s_three_cols(s, d):
    kicker(s, d)
    s.title(d["title"], 700, top=112, sizes=(40, 36, 32))
    top = 268
    for i, (lab, items) in enumerate(d["cols"]):
        x = M + i * 288
        s.text(x, top, lab.upper(), 8.4, 500, BODY, 250, tracking=1.0, name="clab")
        s.hline(x, top + 12, 40, GRAPH, 1.4)
        s.bullets(x, top + 56, items, pt=10.6, gap=16, maxw=250)
    foot(s, d)


# ------------------------------------------------------------------ 09 duas linhas + card
@reg
def s_rows_two(s, d):
    kicker(s, d)
    s.title(d["title"], 520, top=112, sizes=(40, 36, 32))
    y = 262
    for lab, txt in d["rows"]:
        s.text(M, y, lab.upper(), 8.6, 500, BODY, 380, tracking=1.0, name="rlab")
        s.text(M, y + 26, txt, 11.2, 400, BODY, 400, lh=1.45, name="rbody")
        y += 94
    s.rect(596, 262, 306, 146, fill=GRAPH)
    s.text(614, 292, d["note"][0], 8.4, 500, ONDARK, 270, tracking=1.2, name="nlab")
    s.text(614, 320, d["note"][1], 10.6, 400, ONDARK, 268, lh=1.45, name="note")
    foot(s, d)


# ------------------------------------------------------------------ 10 metrica + bullets
@reg
def s_metric_bullets(s, d):
    kicker(s, d)
    s.title(d["title"], 460, top=112, sizes=(40, 36, 32))
    s.text(M, 268, d["metric_label"].upper(), 8.2, 500, BODY, 300, tracking=1.0, name="mlab")
    s.hline(M, 280, 40, GRAPH, 1.4)
    s.text(M, 312, "Um voxel que contém osso e tecido mole recebe uma densidade média: a cortical fina deixa de existir na imagem, mesmo estando íntegra no paciente.",
           11.4, 400, BODY, 420, lh=1.53, name="body")
    x = 560
    s.hline(x, 190, 342, RULE, 0.75)
    s.bullets(x, 226, d["items"], pt=11.5, gap=24, maxw=342)
    foot(s, d)


# ------------------------------------------------------------------ 11 split com regra escura
@reg
def s_split_flow(s, d):
    kicker(s, d)
    s.title(d["title"], 420, top=112, sizes=(40, 36, 32))
    s.hline(M, 246, 52, GRAPH, 1.8)
    s.text(M, 292, d["foot"], 11, 400, BODY, 380, lh=1.5, name="foot_note")
    x = 520
    y = 208
    for num, txt in d["steps"]:
        s.text(x, y, num, 8.6, 500, BODY, 20, name="num")
        s.text(x + 30, y, txt, 11.8, 400, INK, 330, lh=1.35, name="step")
        s.hline(x, y + 26, 370, RULE, 0.7)
        y += 60
    foot(s, d)


# ------------------------------------------------------------------ 12 dois paineis
@reg
def s_two_panels(s, d):
    kicker(s, d)
    s.title(d["title"], 700, top=112, sizes=(40, 36, 32))
    top = 262
    for i, (lab, items) in enumerate((d["left"], d["right"])):
        x = M + i * 436
        if i:
            s.vline(x - 20, top - 24, 190, RULE, 0.75)
        s.text(x, top, lab.upper(), 8.4, 500, BODY, 380, tracking=1.0, name="plab")
        s.hline(x, top + 12, 40, GRAPH, 1.4)
        s.bullets(x, top + 54, items, pt=10.8, gap=16, maxw=380)
    s.text(M, 412, d["foot"], 11.2, 400, INK, 760, lh=1.4, name="foot_note")
    foot(s, d)


# ------------------------------------------------------------------ 13 metrica + 3 colunas
@reg
def s_metric_cols(s, d):
    kicker(s, d)
    s.title(d["title"], 470, top=112, sizes=(40, 36, 32))
    s.text(M + 560, 124, d["metric"], 44, 700, INK, 240, tracking=-0.9, name="metric")
    s.text(M + 560, 152, d["metric_label"], 8.6, 500, BODY, 250, lh=1.4, name="mlab")
    top = 300
    for i, (lab, txt) in enumerate(d["cols"]):
        x = M + i * 288
        s.text(x, top, lab.upper(), 8.4, 500, BODY, 250, tracking=1.0, name="clab")
        s.hline(x, top + 12, 40, GRAPH, 1.4)
        s.text(x, top + 48, txt, 10.8, 400, BODY, 250, lh=1.45, name="cbody")
    s.text(M, 424, d["foot"], 10.6, 400, BODY, 780, lh=1.4, name="foot_note")
    foot(s, d)


# ------------------------------------------------------------------ 14 split foto direita
@reg
def s_split_photo_right(s, d):
    kicker(s, d)
    s.title(d["title"], 470, top=112, sizes=(40, 36, 32))
    s.vline(556, 96, 300, RULE, 0.75)
    s.image(d["img"], 596, 96, 306, 268, alt=C.IMG[d["img"]][1])
    s.bullets(M, 296, d["items"], pt=11.4, gap=26, maxw=470)
    foot(s, d)


# ------------------------------------------------------------------ 15 tres planos
@reg
def s_three_planes(s, d):
    kicker(s, d)
    s.title(d["title"], 700, top=112, sizes=(40, 36, 32))
    top = 268
    import math
    for i, (lab, items) in enumerate(d["cols"]):
        x = M + i * 288
        s.text(x, top, lab.upper(), 8.4, 500, BODY, 250, tracking=1.0, name="clab")
        s.hline(x, top + 12, 40, GRAPH, 1.4)
        s.bullets(x, top + 56, items, pt=10.6, gap=16, maxw=250)
    s.text(M, 424, d["foot"], 10.8, 400, INK, 760, lh=1.4, name="foot_note")
    foot(s, d)


# ------------------------------------------------------------------ 16 cortes
@reg
def s_cuts(s, d):
    kicker(s, d)
    s.title(d["title"], 420, top=112, sizes=(40, 36, 32))
    s.text(M, 250, d["body"], 10.8, 400, BODY, 386, lh=1.5, name="body")
    s.bullets(M, 348, d["items"], pt=10.6, gap=16, maxw=386)
    # diagrama: arco em U com cortes perpendiculares
    import math
    cx, cy = 700, 250
    r = 132
    pts = []
    for i in range(37):
        a = math.pi * (i / 36.0)
        pts.append((cx + r * math.cos(a), cy + r * 0.55 * math.sin(a)))
    for i in range(len(pts) - 1):
        s.line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], (43, 43, 46), 1.1)
    s.line(cx, cy, cx, cy + 82, (120, 124, 130), 0.8)
    for k in range(5):
        a = math.pi * (0.22 + 0.14 * k)
        px, py = cx + r * math.cos(a), cy + r * 0.55 * math.sin(a)
        nx, ny = math.cos(a) * 26, math.sin(a) * 26 / 0.55
        s.line(px - nx * 0.55, py - ny * 0.55, px + nx * 0.55, py + ny * 0.55, GRAPH, 0.9)
        s.text(px, py - 10, str(k + 1), 8.0, 500, BODY, 12, name="cnum")
    s.text(596, 424, "CORTES ORTORRADIAIS · 1 mm", 8.2, 500, BODY, 300, tracking=1.0, name="clab")
    foot(s, d)


# ------------------------------------------------------------------ 17 passos + foto
@reg
def s_steps_photo(s, d):
    kicker(s, d)
    s.title(d["title"], 520, top=104, sizes=(38, 34, 30))
    y = 240
    for i, txt in enumerate(d["steps"]):
        s.text(M, y, "%02d" % (i + 1), 8.4, 500, BODY, 24, tracking=0.8, name="num")
        s.hline(M, y - 16, 500, RULE, 0.7)
        s.text(M + 32, y, txt, 10.6, 400, INK, 470, lh=1.35, name="step")
        y += 42
    s.image(d["img"], 640, 316, 262, 152, alt=C.IMG[d["img"]][1])
    foot(s, d)


# ------------------------------------------------------------------ 18 linha do tempo
@reg
def s_timeline(s, d):
    import math
    kicker(s, d)
    s.title(d["title"], 470, top=112, sizes=(38, 34, 30))
    s.text(M, 262, "Quatro publicações, uma mudança de critério.", 11, 400, BODY, 400, lh=1.45, name="lead")
    cx, cy, r = 712, 408, 176
    seg = 72
    prev = None
    for i in range(seg + 1):
        a = math.pi * (1 - i / float(seg))
        px, py = cx + r * math.cos(a), cy - r * math.sin(a)
        if prev:
            s.line(prev[0], prev[1], px, py, RULE, 1.0)
        prev = (px, py)
    s.hline(cx - r, cy, 2 * r, RULE, 1.0)
    t_pos = [0.06, 0.34, 0.64, 0.93]
    for (year, txt), t in zip(d["marks"], t_pos):
        a = math.pi * (1 - t)
        px, py = cx + r * math.cos(a), cy - r * math.sin(a)
        s.rect(px - 2.6, py - 2.6, 5.2, 5.2, fill=GRAPH)
        lx = min(max(px - 60, 468), 858 - 120)
        ly = py - 52
        s.text(lx, ly, year, 14, 700, INK, 120, name="year")
        s.text(lx, ly + 18, txt, 9.0, 400, BODY, 120, lh=1.35, name="mark")
    foot(s, d)


# ------------------------------------------------------------------ 19 tabela 3 col, 4 linhas
@reg
def s_table_four(s, d):  # noqa: D401
    kicker(s, d)
    s.title(d["title"], 700, top=104, sizes=(38, 34, 30))
    table(s, M, 246, d["cols"], d["rows"], [220, 250, 374], rh=44, body=10.4, foot_rule=False)
    s.text(M, 438, d["foot"], 10.4, 400, INK, 780, lh=1.4, name="foot_note")
    foot(s, d)


# ------------------------------------------------------------------ 20 fechamento
@reg
def s_closing(s, d):
    kicker(s, d)
    y, sz, nl = s.title(d["title"], 470, top=112, sizes=(40, 36, 32))
    s.bullets(M, y + 52, d["items"], pt=11.4, gap=24, maxw=440)
    s.rect(M, 400, 250, 40, fill=GRAPH)
    s.text(M + 16, 425, d["tab"], 8.4, 500, ONDARK, 218, tracking=1.4, name="tab")
    s.image(d["img"], 596, 96, 306, 300, alt=C.IMG[d["img"]][1])
    foot(s, d)


# ------------------------------------------------------------------ driver
def render_one(n, backend="pil"):
    d = C.SLIDES[n - 1]
    s = Slide(backend)
    E[d["layout"]](s, d)
    return s


def render_all(outdir=None):
    out = []
    for d in C.SLIDES:
        s = render_one(d["n"])
        if s.warn:
            out.extend(["s%02d %s" % (d["n"], w) for w in s.warn])
        if outdir:
            s.im.resize((int(W * 1.4), int(H * 1.4))).save(os.path.join(outdir, "s%02d.png" % d["n"]))
    return out


if __name__ == "__main__":
    os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), "_preview"), exist_ok=True)
    P = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_preview")
    warns = render_all(P)
    print("slides:", len(C.SLIDES))
    for w in warns:
        print("  !", w)
    print("ok" if not warns else "warn")
