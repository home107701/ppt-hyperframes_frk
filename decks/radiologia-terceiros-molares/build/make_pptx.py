# -*- coding: utf-8 -*-
"""Gera o PPTX 16:9 (40 slides) a partir do mesmo layout, com notas do apresentador.

O PPTX e o arquivo enviado ao Google Drive/Slides, para que a conversao preserve
geometria, fontes, imagens e notas.
"""
import os

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import MSO_ANCHOR, MSO_AUTO_SIZE
from pptx.util import Emu, Pt

import content as C
import render as R

EMU_PT = 12700          # 1 pt = 12700 EMU
HERE = R.HERE
OUT = os.path.join(HERE, "deck.pptx")


def rgb(c):
    return RGBColor(c[0], c[1], c[2])


def emu(pt):
    return Emu(int(round(pt * EMU_PT)))


def notes_text(d):
    n = d["notes"]
    linhas = [
        ("N%d — %s" % (d["n"], d["label"]), True),
        ("Objetivo: %s" % n["objetivo"], False),
        ("Mensagem-chave: %s" % n["mensagem"], False),
        ("Layout: %s" % d["layout"], False),
        ("Notas de posicionamento: %s" % n["posicionamento"], False),
        ("Prompt de imagem: %s" % n["imagem"], False),
        ("Ícones/gráficos: %s" % n["icones"], False),
        ("Acessibilidade: %s" % n["acessibilidade"], False),
        ("Fontes: %s" % n["fontes"], False),
    ]
    return "\n".join(("• " if bold else "") + t for t, bold in linhas)


def build():
    prs = Presentation()
    prs.slide_width = emu(R.W)
    prs.slide_height = emu(R.H)
    blank = prs.slide_layouts[6]

    for d in C.SLIDES:
        s = R.render_one(d, R.Slide(backend="pptx"))
        page = prs.slides.add_slide(blank)
        bg = page.background.fill
        bg.solid()
        bg.fore_color.rgb = rgb(R.WHITE)

        # retangulos (regras e cards)
        for (x, y, w, h, cc) in s.pts.get("rect", []):
            from pptx.enum.shapes import MSO_SHAPE
            shp = page.shapes.add_shape(MSO_SHAPE.RECTANGLE, emu(x), emu(y), emu(max(w, 0.4)), emu(max(h, 0.4)))
            shp.fill.solid()
            shp.fill.fore_color.rgb = rgb(cc)
            shp.line.fill.background()
            shp.shadow.inherit = False

        # linhas do diagrama e do arco
        for (x1, y1, x2, y2, cc, wt) in s.pts.get("line", []):
            from pptx.enum.shapes import MSO_CONNECTOR
            ln = page.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, emu(x1), emu(y1), emu(x2), emu(y2))
            ln.line.color.rgb = rgb(cc)
            ln.line.width = Pt(max(wt, 0.4))

        # pontos do arco da linha do tempo
        for (x, y, r, cc) in s.pts.get("dot", []):
            from pptx.enum.shapes import MSO_SHAPE
            shp = page.shapes.add_shape(MSO_SHAPE.OVAL, emu(x - r), emu(y - r), emu(2 * r), emu(2 * r))
            shp.fill.solid()
            shp.fill.fore_color.rgb = rgb(cc)
            shp.line.fill.background()
            shp.shadow.inherit = False

        # imagens: inseridas ja recortadas no enquadramento do preview
        for key, x, y, w, h in s.images:
            path = R_cropped(key, w, h)
            page.shapes.add_picture(path, emu(x), emu(y), emu(w), emu(h))

        # textos: um textbox por linha, sem margem interna
        for (x, y, txt, wt, pt, cc, tracking) in s.pts.get("run", []):
            add_text(page, x, y, txt, wt, pt, cc, tracking)
        for (x, y, txt, wt, pt, cc) in s.pts.get("text", []):
            add_text(page, x, y, txt, wt, pt, cc, 0.0)

        page.notes_slide.notes_text_frame.text = notes_text(d)

    prs.save(OUT)
    return OUT


_crop_cache = {}


def R_cropped(key, w, h):
    import make_pdf
    return make_pdf.cropped(key, w, h, dpi=220)


def add_text(page, x, baseline, txt, wt, pt, cc, tracking):
    asc = pt * 0.905           # ascender tipico da Roboto (1854/2048)
    box_h = pt * (0.905 + 0.271)
    top = baseline - asc
    # largura generosa: o renderizador do Slides mede diferente da Roboto local
    need = R.measure(txt, wt, pt) + abs(tracking) * len(txt)
    tb = page.shapes.add_textbox(emu(x), emu(top), emu(max(need * 1.22 + 10, 6)), emu(box_h))
    tf = tb.text_frame
    tf.word_wrap = False
    tf.auto_size = MSO_AUTO_SIZE.NONE
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = MSO_ANCHOR.TOP
    p = tf.paragraphs[0]
    from pptx.enum.text import PP_ALIGN
    p.alignment = PP_ALIGN.LEFT
    run = p.add_run()
    run.text = txt
    f = run.font
    f.name = "Roboto"
    f.size = Pt(pt)
    f.bold = (wt == 700)
    f.color.rgb = rgb(cc)
    rPr = run._r.get_or_add_rPr()
    rPr.set("dirty", "0")
    if tracking:
        rPr.set("spc", str(int(round(tracking * 100))))

    bodyPr = tf._txBody.find('{http://schemas.openxmlformats.org/drawingml/2006/main}bodyPr')
    if bodyPr is not None:
        bodyPr.set("wrap", "none")
        bodyPr.set("lIns", "0")
        bodyPr.set("tIns", "0")
        bodyPr.set("rIns", "0")
        bodyPr.set("bIns", "0")


if __name__ == "__main__":
    print(build())
