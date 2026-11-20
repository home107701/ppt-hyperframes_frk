# -*- coding: utf-8 -*-
"""Roteiro de producao em .docx: um bloco por slide."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from docx import Document
from docx.shared import Pt, RGBColor

import content as C

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "R001_roteiro-de-producao.docx")
INK = RGBColor(0x11, 0x11, 0x11)
GREY = RGBColor(0x66, 0x6B, 0x73)


def copy_lines(d):
    out = ["Título: " + d["title"].replace("\n", " ")]
    for k in ("support", "lead", "body", "foot", "tab"):
        if d.get(k):
            out.append(k.capitalize() + ": " + d[k])
    for k in ("left", "right"):
        if d.get(k):
            out.append(("Painel %s: " % k) + d[k][0] + " — " + " · ".join(d[k][1]))
    if d.get("steps"):
        out.append("Passos: " + " · ".join(s if isinstance(s, str) else "%s %s" % s for s in d["steps"]))
    if d.get("items"):
        out.append("Itens: " + " · ".join(i if isinstance(i, str) else "%s — %s" % i for i in d["items"]))
    if d.get("cols"):
        out.append("Colunas: " + " · ".join("%s — %s" % (c[0], "; ".join(c[1])) for c in d["cols"]))
    if d.get("rows"):
        out.append("Linhas: " + " · ".join(" | ".join(r) for r in d["rows"]))
    if d.get("marks"):
        out.append("Marcos: " + " · ".join("%s — %s" % m for m in d["marks"]))
    return out


def build():
    doc = Document()
    st = doc.styles["Normal"]
    st.font.name = "Roboto"
    st.font.size = Pt(10)
    st.font.color.rgb = GREY
    for s in doc.sections:
        s.left_margin = s.right_margin = Pt(64)

    p = doc.add_paragraph()
    r = p.add_run("R001 — MÓDULO 1: EXODONTIA DE TERCEIROS MOLARES")
    r.font.size = Pt(9)
    r.font.bold = True
    r.font.color.rgb = INK

    p = doc.add_paragraph()
    r = p.add_run("Da panorâmica à TCFC — 20 slides")
    r.font.size = Pt(22)
    r.font.bold = True
    r.font.color.rgb = INK

    p = doc.add_paragraph()
    r = p.add_run("Tema: física clínica, limites da imagem 2D, parâmetros de TCFC e sinais "
                  "radiográficos de Rood & Shehab  |  Público: cirurgiões-dentistas e alunos de "
                  "cirurgia oral menor  |  Objetivo: converter achado de imagem em decisão "
                  "registrada  |  Slides: 20  |  Tom: didático e clínico  |  Idioma: pt-BR  |  16:9")
    r.font.size = Pt(9)

    p = doc.add_paragraph()
    r = p.add_run("Design system: Minimal Editorial Mono — fundo #FFFFFF, títulos #111111, corpo "
                  "#666B73, divisores #D8DCE3, acentos #1A1A1A/#2B2B2E em cards, tabs e regras "
                  "(5–12% da área). Roboto Bold nos títulos (30–48 pt nesta versão 16:9), Roboto "
                  "Regular no corpo (9–13 pt, entrelinha 1,35–1,55), Roboto Medium em labels de "
                  "caixa alta (8,2–8,6 pt). Margens laterais de 6%, topo e base de 10%, grade de 12 "
                  "colunas invisível, 35–45% de área livre. Fotografia editorial colorida, luz "
                  "difusa, sem texto, logos ou filtros; nunca em tela cheia. Ícones monoline em "
                  "grafite. Proibidos: mascotes, emojis, neon, gradientes coloridos, glassmorphism, "
                  "sombras pesadas, fundo escuro integral.")
    r.font.size = Pt(9)

    doc.add_paragraph()
    for d in C.SLIDES:
        h = doc.add_paragraph()
        r = h.add_run("SLIDE %02d · %s" % (d["n"], d["title"].replace("\n", " ")))
        r.font.size = Pt(12.5)
        r.font.bold = True
        r.font.color.rgb = INK

        rows = [
            ("Objetivo", d["notes"]["objetivo"]),
            ("Mensagem-chave", d["notes"]["mensagem"]),
            ("Copy final visível", "  ||  ".join(copy_lines(d))),
            ("Layout", "%s — %s" % (d["layout"], d["notes"]["posicionamento"])),
            ("Prompt de imagem", d["notes"]["imagem"]),
            ("Ícones e gráficos", d["notes"]["icones"]),
            ("Acessibilidade", d["notes"]["acessibilidade"]),
            ("Fontes", d["notes"]["fontes"]),
        ]
        for lbl, txt in rows:
            p = doc.add_paragraph()
            p.paragraph_format.space_after = Pt(2)
            r = p.add_run(lbl + ": ")
            r.font.bold = True
            r.font.size = Pt(9)
            r.font.color.rgb = INK
            r2 = p.add_run(txt)
            r2.font.size = Pt(9)

    doc.save(OUT)
    return OUT


if __name__ == "__main__":
    print(build())
