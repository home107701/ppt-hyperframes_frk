# -*- coding: utf-8 -*-
"""PDF vetorial 960x540 a partir das mesmas primitivas do engine."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

import content as C
import engine as R
import render as L

PAGE_W, PAGE_H = R.W, R.H
OUT = os.path.join(R.ROOT, "aula.pdf")

FONTS = {400: "Roboto", 500: "Roboto-Medium", 700: "Roboto-Bold"}
REG = False


def register():
    global REG
    if REG:
        return
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    for wt, name in FONTS.items():
        pdfmetrics.registerFont(TTFont(name, os.path.join(R.FONT_DIR, R.FPATH[wt])))
    REG = True


def col(c):
    return (c[0] / 255.0, c[1] / 255.0, c[2] / 255.0)


def build():
    register()
    c = canvas.Canvas(OUT, pagesize=(PAGE_W, PAGE_H))
    c.setTitle("R001 — Radiologia e TCFC na exodontia de terceiros molares"
               if hasattr(c, "setTitle") else "")
    for d in C.SLIDES:
        s = L.render_one(d["n"], "pdf")
        for p in s.pts:
            kind = p[0]
            if kind == "rect":
                _, x, y, w, h, fill, stroke, lw, radius = p
                if fill:
                    c.setFillColor(col(fill))
                    c.rect(x, PAGE_H - y - h, w, h, stroke=0, fill=1)
                if stroke:
                    c.setStrokeColor(col(stroke))
                    c.setLineWidth(lw)
                    c.rect(x, PAGE_H - y - h, w, h, stroke=1, fill=0)
            elif kind == "line":
                _, x1, y1, x2, y2, cc, lw = p
                c.setStrokeColor(col(cc))
                c.setLineWidth(lw)
                c.line(x1, PAGE_H - y1, x2, PAGE_H - y2)
            elif kind == "image":
                _, key, x, y, w, h, alt, dpi = p
                path = R.cropped(key, w, h, dpi)
                c.drawImage(ImageReader(path), x, PAGE_H - y - h, w, h, mask=None)
            elif kind == "text":
                _, x, y, txt, wt, pt, cc, trk = p
                if not txt:
                    continue
                c.setFillColor(col(cc))
                c.setFont(FONTS[wt], pt)
                if abs(trk) < 1e-6:
                    c.drawString(x, PAGE_H - y, txt)
                else:
                    cx = x
                    for ch in txt:
                        c.drawString(cx, PAGE_H - y, ch)
                        cx += R.measure(ch, wt, pt, 0.0) + trk
        c.showPage()
    c.save()
    return OUT


if __name__ == "__main__":
    print(build())
