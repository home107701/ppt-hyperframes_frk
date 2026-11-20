# -*- coding: utf-8 -*-
"""PPTX nativo: um textbox por linha medida, imagens recortadas, notas de producao."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Emu, Pt

import content as C
import engine as R
import render as L

EMU = 12700            # 1 pt em EMU
OUT = os.path.join(R.ROOT, "aula.pptx")
ASC = 0.905            # ascender do Roboto Bold/Medium


def rgb(c):
    return RGBColor(c[0], c[1], c[2])


def notes_text(d):
    n = d["notes"]
    lines = [
        "• S%02d — %s" % (d["n"], d["title"].replace("\n", " ")),
        "Objetivo: %s" % n["objetivo"],
        "Mensagem-chave: %s" % n["mensagem"],
        "Layout: %s" % d["layout"],
        "Notas de posicionamento: %s" % n["posicionamento"],
        "Prompt de imagem: %s" % n["imagem"],
        "Ícones/gráficos: %s" % n["icones"],
        "Acessibilidade: %s" % n["acessibilidade"],
        "Fontes: %s" % n["fontes"],
    ]
    return "\n".join(lines)


def build():
    prs = Presentation()
    prs.slide_width = Emu(int(R.W * EMU))
    prs.slide_height = Emu(int(R.H * EMU))
    blank = prs.slide_layouts[6]

    for d in C.SLIDES:
        s = L.render_one(d["n"], "pptx")
        sl = prs.slides.add_slide(blank)

        for p in s.pts:
            kind = p[0]
            if kind == "image":
                _, key, x, y, w, h, alt, dpi = p
                path = R.cropped(key, w, h, dpi)
                sl.shapes.add_picture(path, Emu(int(x * EMU)), Emu(int(y * EMU)),
                                      Emu(int(w * EMU)), Emu(int(h * EMU)))
            elif kind == "rect":
                _, x, y, w, h, fill, stroke, lw, radius = p
                if fill and not stroke:
                    sh = sl.shapes.add_shape(1, Emu(int(x * EMU)), Emu(int(y * EMU)),
                                             Emu(int(w * EMU)), Emu(int(h * EMU)))
                    sh.fill.solid()
                    sh.fill.fore_color.rgb = rgb(fill)
                    sh.line.fill.background()
                    sh.shadow.inherit = False
                    if sh.has_text_frame:
                        sh.text_frame.text = ""
            elif kind == "line":
                _, x1, y1, x2, y2, cc, lw = p
                from pptx.enum.shapes import MSO_CONNECTOR
                cn = sl.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Emu(int(x1 * EMU)),
                                             Emu(int(y1 * EMU)), Emu(int(x2 * EMU)), Emu(int(y2 * EMU)))
                cn.line.color.rgb = rgb(cc)
                cn.line.width = Pt(max(0.5, lw))
                cn.shadow.inherit = False
            elif kind == "text":
                _, x, y, txt, wt, pt, cc, trk = p
                if not txt.strip():
                    continue
                wid = R.measure(txt, wt, pt, trk) * 1.22 + 10
                left = x - 2
                top = y - pt * ASC
                tb = sl.shapes.add_textbox(Emu(int(left * EMU)), Emu(int(top * EMU)),
                                           Emu(int(wid * EMU)), Emu(int(pt * 1.5 * EMU)))
                tf = tb.text_frame
                tf.word_wrap = False
                tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
                tf.vertical_anchor = MSO_ANCHOR.TOP
                tf.auto_size = None
                para = tf.paragraphs[0]
                para.alignment = PP_ALIGN.LEFT
                run = para.add_run()
                run.text = txt
                f = run.font
                f.name = "Roboto"
                f.size = Pt(round(pt, 1))
                f.bold = wt == 700
                f.color.rgb = rgb(cc)
                if abs(trk) > 1e-6:
                    run.font._rPr.set("spc", str(int(round(trk * 100))))

        sl.notes_slide.notes_text_frame.text = notes_text(d)

    prs.save(OUT)
    return OUT


if __name__ == "__main__":
    print(build())
