# -*- coding: utf-8 -*-
"""Layout do deck Minimal Editorial Mono, 16:9 (960x540 pt), Roboto.

Cada slide e composto em pontos (960x540) e renderizado a 2x. As medidas usam
as metricas reais da Roboto; todos os blocos sao verificados contra sua area e
contra a base segura antes de serem desenhados.
"""
import math
import os

from PIL import Image, ImageDraw, ImageFont

import content as C

S = 2  # escala de render -> 1920x1080
W, H = 960, 540

INK = (17, 17, 17)
BODY = (102, 107, 115)
RULE = (216, 220, 227)
GRAPHITE = (26, 26, 26)
WHITE = (255, 255, 255)
PAPER = (243, 244, 246)
ON_DARK = (208, 212, 219)

M = 58.0            # margem lateral (6%)
TOP = 54.0          # margem superior (10%)
SAFE_BOTTOM = 470.0
FOOT_Y = 494.0
CONTENT_W = W - 2 * M

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_FILES = {400: "Roboto-400.ttf", 500: "Roboto-500.ttf", 700: "Roboto-700.ttf"}
SUPERSAMPLE = 8

_cache = {}
FONT_NAME = {400: "Roboto-Regular", 500: "Roboto-Medium", 700: "Roboto-Bold"}
_fonts_ready = False


def register_fonts():
    """Deixa as fontes disponiveis para o backend vetorial (PDF)."""
    global _fonts_ready
    if _fonts_ready:
        return
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    for w, name in FONT_NAME.items():
        pdfmetrics.registerFont(TTFont(name, os.path.join(HERE, "fonts", FONT_FILES[w])))
    _fonts_ready = True


def _font(weight, pt):
    key = ("d", weight, round(pt, 2))
    if key not in _cache:
        _cache[key] = ImageFont.truetype(
            os.path.join(HERE, "fonts", FONT_FILES[weight]), max(1, int(round(pt * S)))
        )
    return _cache[key]


def _mfont(weight, pt):
    key = ("m", weight, round(pt, 2))
    if key not in _cache:
        _cache[key] = ImageFont.truetype(
            os.path.join(HERE, "fonts", FONT_FILES[weight]),
            max(1, int(round(pt * S * SUPERSAMPLE))),
        )
    return _cache[key]


def measure(text, weight, pt):
    return _mfont(weight, pt).getlength(text) / (S * SUPERSAMPLE)


def wrap(text, weight, pt, max_w):
    out = []
    for para in text.split("\n"):
        line = ""
        for wd in para.split(" "):
            probe = wd if not line else line + " " + wd
            if measure(probe, weight, pt) <= max_w or not line:
                line = probe
            else:
                out.append(line)
                line = wd
        out.append(line)
    return out


def block_h(text, weight, pt, max_w, lh):
    lines = wrap(text, weight, pt, max_w) if max_w else text.split("\n")
    return (len(lines) - 1) * pt * lh


def fit_pt(text, weight, sizes, max_w, lh):
    """Maior tamanho da lista em que `text` cabe em max_w sem quebra feia."""
    for pt in sizes:
        if max(measure(l, weight, pt) for l in text.split("\n")) <= max_w:
            return pt
    return sizes[-1]


class Slide:
    def __init__(self, backend="pil"):
        self.backend = backend
        self.warn = []
        self.pts = {}          # elementos vetoriais acumulados (PDF)
        self.images = []       # (key, x, y, w, h)
        self.img = Image.new("RGB", (int(W * S), int(H * S)), WHITE)
        self.d = ImageDraw.Draw(self.img)

    # --- primitivas de desenho: PIL agora, PDF no pos-processamento
    def draw_text(self, x, y, txt, weight, pt, color):
        if self.backend == "pil":
            self.d.text(self._xy(x, y), txt, font=_font(weight, pt), fill=color, anchor="ls")
        else:
            self.pts.setdefault("text", []).append((x, y, txt, weight, pt, color))

    def draw_run(self, x, y, txt, weight, pt, color, tracking):
        if self.backend == "pil":
            f = _font(weight, pt)
            cx = x
            for ch in txt:
                self.d.text(self._xy(cx, y), ch, font=f, fill=color, anchor="ls")
                cx += measure(ch, weight, pt) + tracking
        else:
            self.pts.setdefault("run", []).append((x, y, txt, weight, pt, color, tracking))

    def draw_rect(self, x, y, w, h, color):
        if self.backend == "pil":
            self.d.rectangle([x * S, y * S, (x + w) * S, (y + h) * S], fill=color)
        else:
            self.pts.setdefault("rect", []).append((x, y, w, h, color))

    def draw_line(self, x1, y1, x2, y2, color, weight):
        if self.backend == "pil":
            self.d.line([self._xy(x1, y1), self._xy(x2, y2)], fill=color, width=max(1, int(weight * S)))
        else:
            self.pts.setdefault("line", []).append((x1, y1, x2, y2, color, max(0.4, weight)))

    def draw_dot(self, x, y, r, color):
        if self.backend == "pil":
            self.d.ellipse([(x - r) * S, (y - r) * S, (x + r) * S, (y + r) * S], fill=color)
        else:
            self.pts.setdefault("dot", []).append((x, y, r, color))

    def draw_arc(self, x1, y1, x2, y2, start, end, color, weight):
        if self.backend != "pil":
            cx, cy = (x1 + x2) / 2.0, (y1 + y2) / 2.0
            rx, ry = (x2 - x1) / 2.0, (y2 - y1) / 2.0
            n = 72
            prev = None
            for i in range(n + 1):
                a = math.radians(start + (end - start) * i / n)
                cur = (cx + rx * math.cos(a), cy + ry * math.sin(a))
                if prev:
                    self.draw_line(prev[0], prev[1], cur[0], cur[1], color, weight)
                prev = cur
            return
        if self.backend == "pil":
            self.d.arc([x1 * S, y1 * S, x2 * S, y2 * S], start, end, fill=color, width=max(1, int(weight * S)))
        else:
            self.pts.setdefault("arc", []).append((x1, y1, x2, y2, start, end, color, weight))

    def _xy(self, x, y):
        return (x * S, y * S)

    def text(self, x, y, text, pt, weight=400, color=BODY, max_w=None, lh=1.45,
             tracking=0.0, align="left", name="", limit=SAFE_BOTTOM):
        """y = baseline da primeira linha. Devolve a baseline da ultima linha."""
        lines = wrap(text, weight, pt, max_w) if max_w else text.split("\n")
        f = _font(weight, pt)
        for i, ln in enumerate(lines):
            by = y + i * pt * lh
            wpx = measure(ln, weight, pt)
            if max_w and wpx > max_w + 0.8:
                self.warn.append("X %s %.1f>%.1f '%s'" % (name, wpx, max_w, ln))
            xx = x
            if align == "center":
                xx = x - wpx / 2.0
            elif align == "right":
                xx = x - wpx
            if tracking:
                self.draw_run(xx, by, ln, weight, pt, color, tracking)
            else:
                self.draw_text(xx, by, ln, weight, pt, color)
        last = y + (len(lines) - 1) * pt * lh
        if last > limit + 0.5:
            self.warn.append("Y %s %.1f>%.1f" % (name, last, limit))
        return last

    def rect(self, x, y, w, h, color):
        self.draw_rect(x, y, w, h, color)

    def hline(self, x, y, w, color=RULE, weight=0.75):
        self.draw_rect(x, y, w, weight, color)

    def vline(self, x, y, h, color=RULE, weight=0.75):
        self.draw_rect(x, y, weight, h, color)

    def dot(self, x, y, r=2.6, color=INK):
        self.draw_dot(x, y, r, color)

    def arrow(self, x1, y1, x2, y2, color=INK, weight=1.2):
        self.draw_line(x1, y1, x2, y2, color, weight)
        ang = math.atan2(y2 - y1, x2 - x1)
        for sig in (0.5, -0.5):
            self.draw_line(x2, y2, x2 - 6 * math.cos(ang + sig), y2 - 6 * math.sin(ang + sig),
                           color, weight)

    def image(self, key, x, y, w, h):
        self.images.append((key, x, y, w, h))
        path, _alt, _kind = C.IMG[key]
        im = Image.open(os.path.join(HERE, path)).convert("RGB")
        scale = max(w * S / im.width, h * S / im.height)
        nw, nh = int(im.width * scale + 0.5), int(im.height * scale + 0.5)
        im = im.resize((nw, nh), Image.LANCZOS)
        left = (nw - int(w * S)) // 2
        top = (nh - int(h * S)) // 2
        self.img.paste(im.crop((left, top, left + int(w * S), top + int(h * S))),
                       (int(x * S), int(y * S)))

    def label(self, x, y, text, color=INK, pt=8.6):
        return self.text(x, y, text.upper(), pt, 500, color, tracking=1.15, name="label")

    def rule_short(self, x, y, w=44, color=GRAPHITE):
        self.hline(x, y, w, color, 1.6)

    def footer(self, n):
        self.hline(M, FOOT_Y, 40, RULE, 1.4)
        self.text(M, FOOT_Y + 13, "RADIOLOGIA E TOMOGRAFIA · TERCEIROS MOLARES", 7.2, 500, BODY,
                  tracking=0.9, name="foot-l", limit=530)
        self.text(W - M, FOOT_Y + 13, "%02d / 40" % n, 7.2, 500, BODY, align="right",
                  name="foot-r", limit=530)


# --------------------------------------------------------------------- blocos
def head(s, d, tpt=None, tw=620, bottom=SAFE_BOTTOM, y=None):
    """Label + titulo + regra curta. Devolve a baseline da regra."""
    s.label(M, TOP + 6, d["label"])
    pt = tpt or fit_pt(d["title"], 700, [38, 36, 34, 32], tw, 1.12)
    y0 = y if y is not None else 118
    last = s.text(M, y0, d["title"], pt, 700, INK, max_w=tw, lh=1.12, tracking=-pt * 0.021,
                  name="title", limit=bottom)
    s.rule_short(M, last + 24)
    return last + 24


def bullets(s, x, y, items, w, pt=12.5, gap=24, color=BODY, marker=True, lh=1.4):
    for it in items:
        if marker:
            s.rect(x, y - 6.4, 5, 4.8, GRAPHITE)
        y = s.text(x + (15 if marker else 0), y, it, pt, 400, color, max_w=w - (15 if marker else 0),
                   lh=lh, name="li") + gap
    return y - gap


# -------------------------------------------------------------------- layouts
def cover(s, d):
    s.label(M, TOP + 6, d["label"])
    pt = fit_pt(d["title"], 700, [54, 52, 50, 48, 46, 44], 476, 1.06)
    last = s.text(M, 214, d["title"], pt, 700, INK, max_w=476, lh=1.06, tracking=-pt * 0.022,
                  name="title", limit=372)
    s.rule_short(M, last + 24)
    s.text(M, last + 58, d["support"], 13.5, 400, BODY, max_w=462, lh=1.45, name="support", limit=420)
    cy = 400
    s.rect(M, cy, 340, 66, GRAPHITE)
    s.text(M + 20, cy + 22, d["card_label"].upper(), 7.6, 500, ON_DARK, tracking=1.1, name="cl")
    s.text(M + 20, cy + 42, d["card_text"], 11.0, 400, WHITE, max_w=300, lh=1.26, name="ct",
           limit=cy + 60)
    s.image(d["img"], 566, 0, 394, 540)


def closing(s, d):
    s.label(M, TOP + 6, d["label"])
    pt = fit_pt(d["title"], 700, [60, 58, 56], 430, 1.04)
    last = s.text(M, 206, d["title"], pt, 700, INK, max_w=430, lh=1.04, tracking=-pt * 0.022,
                  name="title", limit=330)
    s.rule_short(M, last + 24)
    s.text(M, last + 58, d["support"], 13.5, 400, BODY, max_w=400, lh=1.5, name="support", limit=396)
    y = 404
    for it in d["items"]:
        s.text(M, y, it.upper(), 8.4, 500, INK, tracking=0.95, name="item")
        y += 22
    s.image(d["img"], 566, 0, 394, 540)


def divider(s, d):
    s.label(M, TOP + 6, d["label"])
    s.text(730, 300, d["big"], 104, 700, PAPER, tracking=-5, name="bignum")
    s.hline(732, 318, 130, RULE, 0.75)
    s.text(732, 356, "BLOCO", 8.0, 500, BODY, tracking=1.2, name="cap")
    pt = fit_pt(d["title"], 700, [46, 44, 42, 40], 600, 1.1)
    last = s.text(M, 268, d["title"], pt, 700, INK, max_w=600, lh=1.1, tracking=-pt * 0.022,
                  name="title", limit=400)
    s.rule_short(M, last + 26)
    s.text(M, last + 62, d["support"], 14, 400, BODY, max_w=470, lh=1.5, name="support", limit=SAFE_BOTTOM)


def split_photo(s, d, side="left", style="items"):
    pw = 400 if side == "left" else 392
    ph = 378
    px = M if side == "left" else W - M - pw
    py = 82
    s.image(d["img"], px, py, pw, ph)
    tx = px + pw + 46 if side == "left" else M
    tw = CONTENT_W - pw - 46
    s.label(tx, TOP + 6, d["label"])
    pt = fit_pt(d["title"], 700, [40, 38, 36, 34, 32], tw, 1.12)
    last = s.text(tx, 132, d["title"], pt, 700, INK, max_w=tw, lh=1.12, tracking=-pt * 0.02,
                  name="title", limit=250)
    s.rule_short(tx, last + 22)
    sup_b = s.text(tx, last + 56, d["support"], 13, 400, BODY, max_w=tw, lh=1.5,
                   name="support", limit=340)
    y = sup_b + (38 if d.get("flow") else 42)
    for i, it in enumerate(d.get("items", [])):
        if style == "check":
            s.rect(tx, y - 6.4, 4.4, 4.4, GRAPHITE)
            s.text(tx + 15, y, it, 12, 400, INK, max_w=tw - 15, lh=1.35, name="item", limit=SAFE_BOTTOM)
            y += 29
        else:
            s.text(tx, y - 8, "%02d" % (i + 1), 8.2, 500, BODY, name="num")
            s.text(tx + 20, y, it, 12, 400, INK, max_w=tw - 20, lh=1.35, name="item", limit=474)
            y += 29
    if d.get("flow"):
        fy = max(y + 12, 436)
        s.hline(tx, fy, tw, RULE, 0.75)
        s.text(tx, fy + 18, d["flow"].upper(), 7.2, 500, BODY, max_w=tw + 40, tracking=0.7,
               name="flow", limit=fy + 26)


def two_questions(s, d):
    s.label(M, TOP + 6, d["label"])
    s.text(W - M, 168, "01", 9.0, 500, BODY, align="right", name="a")
    s.text(W - M, 300, "02", 9.0, 500, BODY, align="right", name="b")
    last1 = s.text(M, 186, d["q1"], 34, 700, INK, max_w=680, lh=1.16, tracking=-0.7, name="q1", limit=270)
    s.hline(M, last1 + 30, 90, GRAPHITE, 1.6)
    last2 = s.text(M, 336, d["q2"], 34, 700, INK, max_w=680, lh=1.16, tracking=-0.7, name="q2", limit=412)
    s.text(M, 452, d["support"], 12.5, 400, BODY, max_w=620, lh=1.4, name="support")


def cascade(s, d):
    s.label(M, TOP + 6, d["label"])
    x = M
    y = 210
    for i, word in enumerate(d["chain"]):
        s.text(x, y, word, 42, 700, INK, tracking=-0.9, name="chain")
        x += measure(word, 700, 42) + 16
        if i < len(d["chain"]) - 1:
            s.text(x, y, "\u2260", 32, 400, BODY, name="neq")
            x += 36
    s.hline(M, 246, 440, RULE, 0.75)
    s.rule_short(M, 300, 44)
    s.text(M, 352, d["support"], 20, 400, INK, max_w=650, lh=1.45, name="support", limit=440)
    s.text(M, 462, "SINAL \u2192 RISCO \u2192 CONDUTA", 7.8, 500, BODY, tracking=1.0, name="tag")


def columns(s, d, kind):
    rule = head(s, d, tw=720)
    top = rule + 44
    if kind == "three_cols":
        cw = (CONTENT_W - 2 * 26) / 3.0
        for i, col in enumerate(d["cols"]):
            x = M + i * (cw + 26)
            s.hline(x, top - 16, cw, RULE, 0.75)
            s.text(x, top + 8, col[0], 14.5, 700, INK, max_w=cw, lh=1.25, name="h")
            bullets(s, x, top + 40, col[1], cw, pt=11.5, gap=20)
    elif kind == "three_options":
        cw = (CONTENT_W - 2 * 26) / 3.0
        for i, (nm, desc) in enumerate(d["options"]):
            x = M + i * (cw + 26)
            if i == 0:
                s.rect(x - 14, top - 18, cw + 14, 166, GRAPHITE)
                s.text(x, top + 12, "OPÇÃO 0%d" % (i + 1), 8.2, 500, ON_DARK, tracking=1.0,
                       name="on")
                s.text(x, top + 52, nm, 15, 700, WHITE, max_w=cw - 24, lh=1.25, name="h")
                s.text(x, top + 94, desc, 11.2, 400, ON_DARK, max_w=cw - 28, lh=1.42, name="d",
                       limit=top + 138)
                continue
            s.hline(x, top - 16, cw, RULE, 0.75)
            s.text(x, top + 12, "OPÇÃO 0%d" % (i + 1), 8.2, 500, BODY, tracking=1.0, name="on")
            s.text(x, top + 52, nm, 15, 700, INK, max_w=cw, lh=1.25, name="h")
            s.text(x, top + 94, desc, 11.2, 400, BODY, max_w=cw - 4, lh=1.42, name="d",
                   limit=top + 138)
        if d.get("footnote"):
            s.hline(M, 392, CONTENT_W, RULE, 0.75)
            s.text(M, 414, d["footnote"], 11, 400, BODY, max_w=CONTENT_W - 30, name="fn")
    elif kind == "two_panels":
        cw = (CONTENT_W - 40) / 2.0
        for i, col in enumerate([d["left"], d["right"]]):
            x = M + i * (cw + 40)
            if i:
                s.vline(x - 40, top - 10, 262, RULE, 0.75)
            s.text(x, top + 10, col[0], 17, 700, INK, max_w=cw, lh=1.25, name="h")
            bullets(s, x, top + 46, col[1], cw, pt=12, gap=24)
        if d.get("footnote"):
            s.hline(M, 440, CONTENT_W, RULE, 0.75)
            s.text(M, 460, d["footnote"], 11, 400, BODY, max_w=CONTENT_W - 30, name="fn")
    elif kind == "three_plans":
        rw = 366
        for i, (nm, txt) in enumerate(d["plans"]):
            y = top + 10 + i * 76
            s.hline(M, y - 18, rw, RULE, 0.6)
            s.text(M, y + 2, nm, 16, 700, INK, name="h")
            s.text(M + 92, y + 2, txt, 11, 400, BODY, max_w=rw - 96, lh=1.38, name="d", limit=y + 40)
        if d.get("img"):
            s.image(d["img"], 474, 116, 428, 300)
            s.vline(474, 116, 300, WHITE, 1.0)
    elif kind == "flow_choice":
        cw = (CONTENT_W - 4) / 2.0
        s.hline(M, top - 6, CONTENT_W, GRAPHITE, 1.0)
        for i, col in enumerate([d["left"], d["right"]]):
            x = M + i * (cw + 4)
            if i:
                s.vline(x - 2, top - 6, min(250, 428 - (top - 6)), RULE, 0.75)
            s.text(x, top + 26, "CAMINHO %s" % ("A" if i == 0 else "B"), 8.4, 500, BODY,
                   tracking=1.0, name="h")
            s.text(x, top + 58, col[0], 19, 700, INK, max_w=cw - 24, lh=1.2, name="h2")
            bullets(s, x, top + 96, col[1], cw - 20, pt=12, gap=22)
        s.hline(M, 440, CONTENT_W, RULE, 0.75)
        s.text(M, 460, d["footnote"], 11, 400, BODY, max_w=CONTENT_W - 30, name="fn")


def table(s, d):
    s.label(M, TOP + 6, d["label"])
    pt = fit_pt(d["title"], 700, [40, 38, 36, 34], 740, 1.12)
    last = s.text(M, 122, d["title"], pt, 700, INK, max_w=740, lh=1.12, tracking=-pt * 0.021,
                  name="title", limit=214)
    if d.get("support"):
        last = s.text(M, last + 30, d["support"], 12.5, 400, BODY, max_w=700, lh=1.4,
                      name="support", limit=246)
    top = last + 34
    rows = d["rows"]
    rh = 44 if len(rows) <= 4 else 37
    body_pt = 12 if len(rows) <= 4 else 11.4
    widths = [0.30, 0.35, 0.35]
    xs = [M, M + widths[0] * CONTENT_W, M + (widths[0] + widths[1]) * CONTENT_W]
    s.hline(M, top, CONTENT_W, GRAPHITE, 1.1)
    for i, hd in enumerate(d["head"]):
        s.text(xs[i], top + 16, hd.upper(), 7.8, 500, BODY, tracking=0.95, name="th")
    y = top + 34
    for r in rows:
        s.hline(M, y, CONTENT_W, RULE, 0.6)
        s.text(xs[0], y + 20, r[0], body_pt, 500, INK, max_w=widths[0] * CONTENT_W - 14, lh=1.3, name="c1")
        s.text(xs[1], y + 20, r[1], body_pt, 400, BODY, max_w=widths[1] * CONTENT_W - 20, lh=1.32, name="c2")
        s.text(xs[2], y + 20, r[2], body_pt, 400, BODY, max_w=widths[2] * CONTENT_W - 8, lh=1.32, name="c3")
        y += rh
    s.hline(M, y, CONTENT_W, RULE, 0.6)
    if d.get("footnote"):
        s.text(M, min(y + 30, 462), d["footnote"], 11, 400, BODY, max_w=CONTENT_W - 30, name="fn")


def numbered(s, d):
    rule = head(s, d, tw=760, bottom=222)
    top = rule + (28 if d["layout"] == "flow_four" else 42)
    kind = d["layout"]
    if kind == "flow_four":
        for i, (num, q, sub) in enumerate(d["steps"]):
            y = top + i * 60
            s.hline(M, y - 12, CONTENT_W, RULE, 0.6)
            s.text(M, y + 2, num, 8.4, 500, BODY, name="num")
            s.text(M + 32, y + 4, q, 17, 700, INK, max_w=620, lh=1.2, name="q")
            s.text(M + 32, y + 25, sub, 10.8, 400, BODY, max_w=620, lh=1.3, name="s")
        s.hline(M, top + 4 * 60 - 12, CONTENT_W, RULE, 0.6)
        s.text(M, top + 4 * 60 + 12, d["support"], 11.0, 400, BODY, max_w=CONTENT_W - 40,
               name="support", limit=470)
    elif kind == "quiz_five":
        for i, (num, q) in enumerate(d["items"]):
            y = top + i * 46
            s.hline(M, y - 12, CONTENT_W, RULE, 0.6)
            s.text(M, y + 2, num, 8.4, 500, BODY, name="num")
            s.text(M + 32, y + 4, q, 15.5, 700, INK, max_w=700, lh=1.2, name="q")
        s.hline(M, top + 5 * 46 - 12, CONTENT_W, RULE, 0.6)
        s.text(M, top + 5 * 46 + 12, d["support"], 10.6, 400, BODY, max_w=CONTENT_W - 40,
               name="support", limit=474)
    elif kind == "rows_three":
        for i, (lab, txt) in enumerate(d["rows"]):
            y = top + 24 + i * 84
            s.text(M, y, lab.upper(), 8.2, 500, BODY, tracking=1.0, name="lab")
            s.hline(M, y + 10, 96, GRAPHITE, 1.2)
            s.text(M + 128, y, txt, 17, 700, INK, max_w=CONTENT_W - 132, lh=1.25, name="txt", limit=y + 30)
        if d.get("footnote"):
            s.hline(M, 440, CONTENT_W, RULE, 0.75)
            s.text(M, 460, d["footnote"], 11, 400, BODY, max_w=CONTENT_W - 30, name="fn")
    elif kind == "steps_five":
        cw = (CONTENT_W - 4 * 16) / 5.0
        s.hline(M, top - 8, CONTENT_W, GRAPHITE, 1.0)
        for i, (num, txt) in enumerate(d["steps"]):
            x = M + i * (cw + 16)
            s.text(x, top + 26, num, 20, 700, INK, name="num")
            s.text(x, top + 62, txt, 11, 400, BODY, max_w=cw - 4, lh=1.4, name="nm", limit=top + 120)
        s.text(M, top + 160, d["support"], 14, 400, BODY, max_w=600, lh=1.45, name="support")
    elif kind == "grid_six":
        cw = (CONTENT_W - 2 * 30) / 3.0
        for i, (num, txt) in enumerate(d["items"]):
            r, c = divmod(i, 3)
            x = M + c * (cw + 30)
            y = top + r * 92
            s.hline(x, y - 10, cw, RULE, 0.75)
            s.text(x, y + 18, num, 8.2, 500, BODY, name="num")
            s.text(x, y + 46, txt, 19, 700, INK, max_w=cw, lh=1.2, name="nm")
        s.text(M, top + 2 * 92 + 20, d["support"], 12.5, 400, BODY, max_w=620, lh=1.45, name="support")


def agenda(s, d):
    s.label(M, TOP + 6, d["label"])
    pt = fit_pt(d["title"], 700, [40, 38, 36], 520, 1.12)
    last = s.text(M, 122, d["title"], pt, 700, INK, max_w=520, lh=1.12, tracking=-pt * 0.021,
                  name="title", limit=220)
    top = last + 40
    for i, (num, name, desc) in enumerate(d["items"]):
        y = top + i * 56
        s.hline(M, y - 14, 510, RULE, 0.6)
        s.text(M, y + 6, num, 9.2, 500, BODY, name="num")
        s.text(M + 30, y + 8, name, 16, 700, INK, name="nm")
        s.text(M + 30, y + 28, desc, 10.5, 400, BODY, max_w=460, name="d")
    s.image(d["img"], 596, 104, 306, 316)


def editorial_photo(s, d):
    s.label(M, TOP + 6, d["label"])
    pt = fit_pt(d["title"], 700, [42, 40, 38, 36], 600, 1.08)
    last = s.text(M, 120, d["title"], pt, 700, INK, max_w=600, lh=1.08, tracking=-pt * 0.021,
                  name="title", limit=210)
    s.rule_short(M, last + 22)
    s.text(M, last + 52, d["support"], 13, 400, BODY, max_w=545, lh=1.45, name="support", limit=280)
    y = 330
    for i, it in enumerate(d.get("items", [])):
        yy = y + i * 34
        s.text(M, yy - 2, "%02d" % (i + 1), 8.0, 500, BODY, name="num")
        s.text(M + 24, yy, it, 11.5, 400, BODY, max_w=290, lh=1.3, name="item", limit=yy + 16)
    s.image(d["img"], 452, 292, 450, 178)


def metric(s, d):
    s.label(M, TOP + 6, d["label"])
    pt = fit_pt(d["title"], 700, [40, 38, 36, 34], 560, 1.1)
    last = s.text(M, 122, d["title"], pt, 700, INK, max_w=560, lh=1.1, tracking=-pt * 0.021,
                  name="title", limit=230)
    top = last + 34
    kind = d["layout"]
    if kind == "metric_case":
        s.text(M, top + 2, d["metric_label"].upper(), 7.6, 500, BODY, tracking=1.0, name="ml")
        s.hline(M, top + 14, 40, RULE, 1.2)
        s.text(M, top + 86, d["metric"], 92, 700, INK, tracking=-3.2, name="metric")
        bullets(s, M, top + 128, d["items"], 400, pt=11.5, gap=22)
        s.image(d["img"], 512, 104, 390, 330)
        s.vline(482, 104, 330, RULE, 0.75)
    elif kind == "evidence":
        s.text(M, top + 46, d["metric"], 58, 700, INK, tracking=-2.0, name="metric")
        s.text(M, top + 66, d["metric_note"], 10, 400, BODY, max_w=470, name="mn")
        y = top + 108
        for it in d["items"]:
            s.hline(M, y - 16, 480, RULE, 0.6)
            y = s.text(M, y, it, 12, 400, BODY, max_w=480, lh=1.4, name="li") + 24
    elif kind == "case_metric":
        s.text(M, top + 34, d["metric"], 64, 700, INK, name="metric")
        s.text(M + 34, top + 6, d["metric_label"].upper(), 7.6, 500, BODY, tracking=1.0, name="ml")
        s.text(M, top + 62, d["support"], 12.5, 400, BODY, max_w=386, lh=1.45, name="support", limit=top + 132)
        bullets(s, M, top + 146, d["items"], 390, pt=11.5, gap=20)
        s.image(d["img"], 500, 82, 402, 378)
        s.vline(478, 82, 378, RULE, 0.75)


def timeline(s, d):
    s.label(M, TOP + 6, d["label"])
    pt = fit_pt(d["title"], 700, [40, 38, 36], 400, 1.1)
    last = s.text(M, 118, d["title"], pt, 700, INK, max_w=400, lh=1.1, tracking=-pt * 0.021,
                  name="title", limit=230)
    s.text(M, last + 34, d["support"], 12.5, 400, BODY, max_w=360, lh=1.45, name="support", limit=330)
    cx, cy, r = 706.0, 396.0, 158.0
    s.draw_arc(cx - r, cy - r, cx + r, cy + r, 180, 360, RULE, 1.0)
    s.hline(cx - r, cy, 2 * r, GRAPHITE, 1.0)
    for i, (dt, txt) in enumerate(d["marks"]):
        ang = math.pi + (i + 0.5) * math.pi / len(d["marks"])
        mx, my = cx + r * math.cos(ang), cy + r * math.sin(ang)
        s.dot(mx, my, 3.0)
        lx = min(max(cx + (r + 44) * math.cos(ang), 350), 858)
        ly = cy + (r + 40) * math.sin(ang) - 26
        s.text(lx, ly, dt, 10, 700, INK, align="center", name="dt")
        s.text(lx, ly + 14, txt, 7.4, 400, BODY, max_w=124, lh=1.3, align="center", name="tx",
               limit=ly + 44)


def diagram(s, d):
    rule = head(s, d, tw=520, bottom=250)
    if d["layout"] == "diagram_angulation":
        s.text(M, rule + 52, d["support"], 12.5, 400, BODY, max_w=430, lh=1.45, name="support", limit=330)
        y = rule + 112
        for it in d["items"]:
            s.text(M, y, it, 11.5, 400, BODY, max_w=420, lh=1.35, name="item")
            y += 26
        bx, by = 596, 340
        angles = (-20, 26, 0, 72)
        for i, ang in enumerate(angles):
            x = bx + i * 78
            s.hline(x - 26, by, 52, RULE, 1.0)
            rad = math.radians(ang)
            s.draw_line(x, by, x + 48 * math.sin(rad), by - 56 * math.cos(rad), INK, 1.5)
            s.text(x, by + 26, ["-20\u00b0", "+26\u00b0", "0\u00b0", "+72\u00b0"][i], 7.4, 500, BODY,
                   align="center", name="ang")
        s.text(bx - 26, by + 60, "ESQUEMA DID\u00c1TICO \u00b7 WINTER", 7.4, 500, BODY, tracking=0.9,
               name="cap")
    else:
        s.text(M, rule + 50, d["support"], 12.5, 400, BODY, max_w=660, lh=1.45, name="support", limit=320)
        top = rule + 106
        pw = 292
        s.rect(M, top, pw, 158, GRAPHITE)
        s.text(M + 20, top + 44, d["panels"][0][0], 32, 700, WHITE, tracking=-1.0, name="p1")
        s.text(M + 20, top + 76, d["panels"][0][1], 10.0, 400, ON_DARK, max_w=pw - 40, lh=1.42,
               name="p1t", limit=top + 148)
        x2 = M + pw + 44
        s.text(x2, top + 44, d["panels"][1][0], 32, 700, INK, tracking=-1.0, name="p2")
        s.text(x2, top + 76, d["panels"][1][1], 10.0, 400, BODY, max_w=CONTENT_W - pw - 70, lh=1.42,
               name="p2t", limit=top + 120)
        s.hline(x2, top + 20, 110, RULE, 0.75)
        if d.get("footnote"):
            s.text(M, 460, d["footnote"], 10.5, 400, BODY, max_w=CONTENT_W - 30, name="fn")


PLAIN = {
    "cover": cover,
    "closing": closing,
    "divider": divider,
    "agenda": agenda,
    "editorial_photo_bottom": editorial_photo,
    "timeline": timeline,
    "rows_table": table,
    "two_questions": two_questions,
    "cascade": cascade,
    "flow_four": numbered,
    "quiz_five": numbered,
    "rows_three": numbered,
    "steps_five": numbered,
    "grid_six": numbered,
    "metric_case": metric,
    "evidence": metric,
    "case_metric": metric,
    "diagram_angulation": diagram,
    "grid_pell": diagram,
}


def render_one(d, s=None):
    s = s or Slide()
    lay = d["layout"]
    if lay in ("split_photo_left", "split_photo_right", "list_photo", "checklist_photo"):
        split_photo(s, d,
                    side="right" if lay == "split_photo_right" else "left",
                    style="check" if lay == "checklist_photo" else "items")
    elif lay in ("three_cols", "three_options", "two_panels", "three_plans", "flow_choice"):
        columns(s, d, lay)
    else:
        PLAIN[lay](s, d)
    s.footer(d["n"])
    return s


if __name__ == "__main__":
    out = os.path.join(HERE, "render")
    os.makedirs(out, exist_ok=True)
    problems = []
    for d in C.SLIDES:
        s = render_one(d)
        s.img.save(os.path.join(out, "s%02d.png" % d["n"]))
        problems += [(d["n"], w) for w in s.warn]
    print("slides:", len(C.SLIDES))
    for p in problems:
        print("PROBLEMA", p)
    print("ok" if not problems else "%d problemas" % len(problems))
