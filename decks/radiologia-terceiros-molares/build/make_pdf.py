# -*- coding: utf-8 -*-
"""Gera o PDF vetorial do deck a partir do mesmo layout do preview.

Texto em contorno de fonte (nitido em qualquer zoom) e imagens JPEG embutidas.
O PDF tem 960x540 pt (16:9) e e usado como fonte visual da apresentacao.
"""
import os

from reportlab.lib.colors import Color
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen import canvas

import content as C
import render as R

OUT = os.path.join(R.HERE, "deck.pdf")
PAGE_W, PAGE_H = R.W, R.H


def col(rgb):
    return Color(rgb[0] / 255.0, rgb[1] / 255.0, rgb[2] / 255.0)


IMG_CACHE = os.path.join(R.HERE, "render", "_crop")


def cropped(key, w, h, dpi=200):
    """Recorta no mesmo enquadramento (cover, centralizado) do preview."""
    from PIL import Image
    path = os.path.join(R.HERE, C.IMG[key][0])
    im = Image.open(path).convert("RGB")
    tw, th = max(1, int(round(w / 72.0 * dpi))), max(1, int(round(h / 72.0 * dpi)))
    scale = max(tw / im.width, th / im.height)
    nw, nh = int(im.width * scale + 0.5), int(im.height * scale + 0.5)
    im = im.resize((nw, nh), Image.LANCZOS)
    left, top = (nw - tw) // 2, (nh - th) // 2
    im = im.crop((left, top, left + tw, top + th))
    os.makedirs(IMG_CACHE, exist_ok=True)
    dst = os.path.join(IMG_CACHE, "%s_%dx%d.jpg" % (key, tw, th))
    if not os.path.exists(dst):
        im.save(dst, quality=94, subsampling=0)
    return dst


def build():
    R.register_fonts()
    c = canvas.Canvas(OUT, pagesize=(PAGE_W, PAGE_H))
    c.setTitle("Radiologia e tomografia na prática clínica de terceiros molares")
    c.setAuthor("Aula — Cirurgia oral menor")
    c.setSubject("40 slides · Minimal Editorial Mono")
    for d in C.SLIDES:
        s = R.render_one(d, SlideOverride(d))
        # ordem de pintura: fundo, retangulos, linhas, imagens, textos
        c.setFillColor(col(R.WHITE))
        c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
        for (x, y, w, h, cc) in s.pts.get("rect", []):
            c.setFillColor(col(cc))
            c.rect(x, PAGE_H - y - h, w, h, stroke=0, fill=1)
        for (x1, y1, x2, y2, cc, wt) in s.pts.get("line", []):
            c.setStrokeColor(col(cc))
            c.setLineWidth(wt)
            c.line(x1, PAGE_H - y1, x2, PAGE_H - y2)
        for (x, y, r, cc) in s.pts.get("dot", []):
            c.setFillColor(col(cc))
            c.circle(x, PAGE_H - y, r, stroke=0, fill=1)
        for (x1, y1, x2, y2, st, en, cc, wt) in s.pts.get("arc", []):
            c.setStrokeColor(col(cc))
            c.setLineWidth(wt)
            c.arc(x1, PAGE_H - y2, x2, PAGE_H - y1, startAng=-en, extent=en - st)
        for key, x, y, w, h in s.images:
            c.drawImage(ImageReader(cropped(key, w, h)), x, PAGE_H - y - h, w, h,
                        mask=None, preserveAspectRatio=False)
        for (x, y, txt, wt, pt, cc) in s.pts.get("text", []):
            c.setFillColor(col(cc))
            c.setFont(R.FONT_NAME[wt], pt)
            c.drawString(x, PAGE_H - y, txt)
        for (x, y, txt, wt, pt, cc, tracking) in s.pts.get("run", []):
            c.setFillColor(col(cc))
            c.setFont(R.FONT_NAME[wt], pt)
            tc = "%.4f Tc" % (tracking + 0.28)   # repoe o avanco removido do espaco
            cx = x
            for ch in txt:
                c.drawString(cx, PAGE_H - y, ch)
                cx += R.measure(ch, wt, pt) + tracking
        for w in s.warn:
            raise SystemExit("layout invalido no slide %d: %s" % (d["n"], w))
        c.showPage()
    c.save()
    return OUT


class SlideOverride(R.Slide):
    def __init__(self, d):
        super().__init__(backend="pdf")


if __name__ == "__main__":
    print(build())
