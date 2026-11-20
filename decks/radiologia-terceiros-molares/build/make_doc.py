# -*- coding: utf-8 -*-
"""Gera o roteiro de direcao de arte em .docx: um bloco por slide."""
import os

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt, RGBColor

import content as C

OUT = os.path.join(C.__file__.rsplit("/", 2)[0], "roteiro-diretoria-de-arte.docx")
INK = RGBColor(0x11, 0x11, 0x11)
GREY = RGBColor(0x66, 0x6B, 0x73)


def copy_final(d):
    partes = ["Título: %s" % d.get("title", "").replace("\n", " ")]
    for k, lbl in (("support", "Apoio"), ("q1", "Pergunta 1"), ("q2", "Pergunta 2"),
                   ("card_text", "Card"), ("metric_note", "Intervalo"), ("footnote", "Rodapé")):
        if d.get(k):
            partes.append("%s: %s" % (lbl, d[k]))
    if d.get("items"):
        itens = [i if isinstance(i, str) else " / ".join(i) for i in d["items"]]
        partes.append("Bullets: " + " · ".join(itens))
    if d.get("steps"):
        partes.append("Passos: " + " · ".join(" ".join(t) for t in d["steps"]))
    if d.get("rows"):
        partes.append("Linhas: " + " · ".join(" | ".join(r) for r in d["rows"]))
    if d.get("cols"):
        partes.append("Colunas: " + " · ".join("%s (%s)" % (c[0], "; ".join(c[1])) for c in d["cols"]))
    if d.get("options"):
        partes.append("Opções: " + " · ".join("%s — %s" % o for o in d["options"]))
    if d.get("plans"):
        partes.append("Planos: " + " · ".join("%s — %s" % p for p in d["plans"]))
    if d.get("panels"):
        partes.append("Painéis: " + " · ".join("%s — %s" % p for p in d["panels"]))
    if d.get("left"):
        partes.append("Painel A: %s (%s)" % (d["left"][0], "; ".join(d["left"][1])))
        partes.append("Painel B: %s (%s)" % (d["right"][0], "; ".join(d["right"][1])))
    if d.get("marks"):
        partes.append("Marcos: " + " · ".join("%s — %s" % m for m in d["marks"]))
    if d.get("chain"):
        partes.append("Cadeia: " + " ≠ ".join(d["chain"]))
    if d.get("flow"):
        partes.append("Fluxo: " + d["flow"])
    return partes


def build():
    doc = Document()
    st = doc.styles["Normal"]
    st.font.name = "Roboto"
    st.font.size = Pt(10)
    st.font.color.rgb = GREY
    for s in doc.sections:
        s.left_margin = s.right_margin = Pt(64)

    h = doc.add_paragraph()
    r = h.add_run("RADIOLOGIA E TOMOGRAFIA NA PRÁTICA CLÍNICA DE EXODONTIA DE TERCEIROS MOLARES")
    r.font.size = Pt(9)
    r.font.color.rgb = INK
    r.font.bold = True

    t = doc.add_paragraph()
    r = t.add_run("Roteiro de direção de arte — 40 slides")
    r.font.size = Pt(24)
    r.font.bold = True
    r.font.color.rgb = INK

    meta = doc.add_paragraph()
    r = meta.add_run("Público: cirurgiões-dentistas e alunos de cirurgia oral menor  |  "
                     "Objetivo: converter achado de imagem em conduta registrada  |  "
                     "Slides: 40  |  Tom: didático e clínico  |  Idioma: pt-BR  |  Formato: 16:9")
    r.font.size = Pt(9)

    ds = doc.add_paragraph()
    r = ds.add_run("Design system: Minimal Editorial Mono — fundo #FFFFFF, títulos #111111, corpo #666B73, "
                   "divisores #D8DCE3, acentos #1A1A1A/#2B2B2E em cards, tabs e regras. Roboto Bold nos títulos "
                   "(34–58 pt nesta versão 16:9, tracking negativo), Roboto Regular no corpo (11–17 pt, entrelinha "
                   "1,3–1,5), Roboto Medium em labels caixa alta (7,2–8,6 pt). Margens laterais de 6% e vertical de "
                   "10%, grade de 12 colunas invisível, 35–45% de área livre. Fotografia editorial natural, colorida "
                   "e difusa, sem texto, logos ou filtros; nada em tela cheia. Ícones monoline pretos. "
                   "Proibidos: mascotes, emojis, neon, gradientes coloridos, glassmorphism, sombras pesadas.")
    r.font.size = Pt(9)

    doc.add_paragraph()
    for d in C.SLIDES:
        cab = doc.add_paragraph()
        r = cab.add_run("SLIDE %02d  ·  %s" % (d["n"], d["title"].replace("\n", " ")))
        r.font.size = Pt(13)
        r.font.bold = True
        r.font.color.rgb = INK

        linhas = [
            ("Objetivo", d["notes"]["objetivo"]),
            ("Mensagem-chave", d["notes"]["mensagem"]),
            ("Copy final visível", "  ||  ".join(copy_final(d))),
            ("Layout", "%s — %s" % (d["layout"], d["notes"]["posicionamento"])),
            ("Prompt de imagem", d["notes"]["imagem"] +
             (("  Foto: " + C.IMG[d["img"]][0] + ". Texto alternativo: " + C.IMG[d["img"]][1] + ".")
              if d.get("img") else "  Sem fotografia neste slide.")),
            ("Ícones e gráficos", d["notes"]["icones"]),
            ("Acessibilidade", d["notes"]["acessibilidade"]),
            ("Fontes do conteúdo", d["notes"]["fontes"]),
        ]
        for lbl, txt in linhas:
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
