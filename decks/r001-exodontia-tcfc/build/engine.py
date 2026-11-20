# -*- coding: utf-8 -*-
"""Motor de layout unico: registra primitivas e desenha em PIL, PDF ou PPTX.

Coordenadas em pontos sobre canvas 960x540 (16:9). Espelhar em tres backends
garante que a previa PNG, o PDF e o PPTX tenham a mesma geometria.
"""
import os
import warnings

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
IMG_DIR = os.path.join(ROOT, "img")
FONT_DIR = os.path.join(ROOT, "fonts")
CACHE = os.path.join(HERE, "_crop")

W, H = 960.0, 540.0
S = 2
M = 58.0
TOP = 54.0
BOT = 468.0
FOOT = 494.0
CW = W - 2 * M

INK = (17, 17, 17)
BODY = (102, 107, 115)
RULE = (216, 220, 227)
GRAPH = (26, 26, 26)
ONDARK = (208, 212, 219)
WHITE = (255, 255, 255)

FPATH = {400: "Roboto-400.ttf", 500: "Roboto-500.ttf", 700: "Roboto-700.ttf"}
_fcache = {}


def _pilfont(wt, pt):
    key = (wt, round(pt, 2))
    if key not in _fcache:
        _fcache[key] = ImageFont.truetype(os.path.join(FONT_DIR, FPATH[wt]), int(round(pt * S)))
    return _fcache[key]


def measure(txt, wt, pt, tracking=0.0):
    if not txt:
        return 0.0
    f = _pilfont(wt, pt)
    base = f.getlength(txt) / S
    return base + tracking * (len(txt) - 1)


def wrap(txt, wt, pt, maxw, tracking=0.0):
    out = []
    for para in str(txt).split("\n"):
        words = para.split()
        line = ""
        for wd in words:
            probe = (line + " " + wd).strip()
            if measure(probe, wt, pt, tracking) <= maxw or not line:
                line = probe
            else:
                out.append(line)
                line = wd
        out.append(line)
    return out


def cropped(key, w, h, dpi=200):
    os.makedirs(CACHE, exist_ok=True)
    out = os.path.join(CACHE, "%s_%dx%d.jpg" % (key, int(w), int(h)))
    src = os.path.join(IMG_DIR, key + ".jpg")
    im = Image.open(src).convert("RGB")
    iw, ih = im.size
    r = w / float(h)
    if iw / float(ih) > r:
        nw = int(ih * r)
        x0 = (iw - nw) // 2
        im = im.crop((x0, 0, x0 + nw, ih))
    else:
        nh = int(iw / r)
        y0 = (ih - nh) // 3
        im = im.crop((0, y0, iw, y0 + nh))
    im = im.resize((max(2, int(w / 72.0 * dpi)), max(2, int(h / 72.0 * dpi))), Image.LANCZOS)
    im.save(out, quality=90)
    return out


class Slide:
    def __init__(self, backend="pil"):
        self.b = backend
        self.pts = []
        self.images = []
        self.warn = []
        if backend == "pil":
            self.im = Image.new("RGB", (int(W * S), int(H * S)), (255, 255, 255))
            self.d = ImageDraw.Draw(self.im)

    # ---------------------------------------------------------------- primitivas
    def rect(self, x, y, w, h, fill=None, color=None, lw=0.8, radius=0):
        self.pts.append(("rect", x, y, w, h, fill, color, lw, radius))
        if self.b == "pil":
            if fill:
                self.d.rectangle([x * S, y * S, (x + w) * S - 1, (y + h) * S - 1], fill=fill)
            if color:
                self.d.rectangle([x * S, y * S, (x + w) * S - 1, (y + h) * S - 1], outline=color, width=max(1, int(round(lw * S))))

    def line(self, x1, y1, x2, y2, color=RULE, lw=0.8):
        self.pts.append(("line", x1, y1, x2, y2, color, lw))
        if self.b == "pil":
            self.d.line([x1 * S, y1 * S, x2 * S, y2 * S], fill=color, width=max(1, int(round(lw * S))))

    def hline(self, x, y, w, color=RULE, lw=0.8):
        self.line(x, y, x + w, y, color, lw)

    def vline(self, x, y, h, color=RULE, lw=0.8):
        self.line(x, y, x, y + h, color, lw)

    def text(self, x, y, txt, pt=12, wt=400, color=BODY, max_w=None, lh=1.42,
             tracking=0.0, name="txt", align="left", limit=None, check=True):
        """y = linha de base da primeira linha. Devolve a base da ultima linha."""
        if max_w is None:
            max_w = CW
        lines = wrap(txt, wt, pt, max_w, tracking)
        if limit is not None and len(lines) > limit:
            self.warn.append("%s: %d linhas > limite %d" % (name, len(lines), limit))
        lead = pt * lh
        last = y + lead * (len(lines) - 1)
        if check and last > BOT + 6:
            self.warn.append("%s: base %.1f abaixo de %.0f" % (name, last, BOT))
        for i, ln in enumerate(lines):
            yy = y + lead * i
            lw_ = measure(ln, wt, pt, tracking)
            if lw_ > max_w + 0.6:
                self.warn.append("%s: linha excede %.0f (%.1f)" % (name, max_w, lw_))
            xx = x
            if align == "right":
                xx = x + max_w - lw_
            self._line(xx, yy, ln, pt, wt, color, tracking)
        return last

    def _line(self, x, y, txt, pt, wt, color, tracking):
        self.pts.append(("text", x, y, txt, wt, pt, color, tracking))
        if self.b != "pil":
            return
        if not txt:
            return
        if abs(tracking) < 1e-6:
            self.d.text((x * S, y * S), txt, font=_pilfont(wt, pt), fill=color, anchor="ls")
        else:
            cx = x
            for ch in txt:
                self.d.text((cx * S, y * S), ch, font=_pilfont(wt, pt), fill=color, anchor="ls")
                cx += measure(ch, wt, pt) + tracking

    def image(self, key, x, y, w, h, alt="", dpi=200):
        self.images.append({"key": key, "x": x, "y": y, "w": w, "h": h, "alt": alt})
        self.pts.append(("image", key, x, y, w, h, alt, dpi))
        if self.b == "pil":
            im = Image.open(cropped(key, w, h, dpi)).resize((int(w * S), int(h * S)), Image.LANCZOS)
            self.im.paste(im, (int(x * S), int(y * S)))

    # ---------------------------------------------------------------- conteudo
    def header(self, kicker, n, total):
        self.text(M, TOP, kicker.upper(), 8.6, 500, BODY, tracking=1.15, name="kicker")
        self.hline(M, FOOT - 16, 40, RULE, 1.2)
        self.text(M, FOOT, "RADIOLOGIA · TERCEIROS MOLARES", 7.8, 500, BODY, tracking=1.1, name="foot")
        self.text(W - M - 60, FOOT, "%02d / %02d" % (n, total), 8.2, 500, BODY, tracking=0.6,
                  max_w=60, align="right", name="page")

    def title(self, s, maxw, top=None, sizes=(48, 44, 40, 36), maxlines=3):
        top = 96 if top is None else top
        chosen = sizes[-1]
        lines = wrap(s, 700, chosen, maxw, -chosen * 0.021)
        for sz in sizes:
            ls = wrap(s, 700, sz, maxw, -sz * 0.021)
            if len(ls) <= maxlines:
                chosen, lines = sz, ls
                break
        else:
            self.warn.append("titulo: %d linhas" % len(lines))
        lead = chosen * 1.14
        for i, ln in enumerate(lines):
            self._line(M, top + lead * i, ln, chosen, 700, INK, -chosen * 0.021)
        return top + lead * (len(lines) - 1), chosen, len(lines)

    def bullets(self, x, y, items, pt=12, gap=None, wt=400, color=BODY, maxw=380, lh=1.4):
        gap = gap if gap else pt * 1.62
        yy = y
        for it in items:
            self.rect(x, yy - pt * 0.50, 3.4, 3.4, fill=INK)
            last = self.text(x + 12, yy, it, pt, wt, color, maxw - 12, lh=lh, name="bullet")
            yy = max(last, yy) + gap
        return yy
