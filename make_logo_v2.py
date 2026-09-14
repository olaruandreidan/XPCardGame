"""Export the second logo and a comparison PDF using the project's PDF runtime."""
from pathlib import Path
from reportlab.pdfgen.canvas import Canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import mm
from logo import draw_mark, export_svg
from generate import load_config, resolve

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "output/logo/v2"


def build():
    OUT.mkdir(parents=True, exist_ok=True)
    cfg = load_config(ROOT / "game_config.py")
    pdfmetrics.registerFont(TTFont("LogoProof", str(resolve(cfg, cfg.FONT_PATH))))
    for name, fill in [("black", "#000000"), ("blue", "#3555AB"), ("white", "#FFFFFF")]:
        export_svg(OUT/f"marriage-xp-v2-{name}.svg", fill, version=2)

    def label(c, text, x, y, size, color=(0,0,0,1)):
        c.setFillColorCMYK(*color)
        c.setFont("LogoProof", size)
        c.drawString(x,y,text)

    c = Canvas(str(OUT/"logo-v2-study.pdf"), pagesize=(840,600), invariant=1,
               enforceColorSpace="CMYK", initialFontName="LogoProof")
    c.setTitle("Marriage XP - second logo direction")
    c.setFillColorCMYK(0,0,.025,.025)
    c.rect(0,0,840,600,stroke=0,fill=1)
    label(c,"MARRIAGE XP / LOGO 02",36,558,10)
    label(c,"A raised loop. An open stem.",36,518,28)
    c.setFillColorCMYK(0,0,0,1)
    draw_mark(c,56,103,270,348,tight=True,version=2)
    c.setFillColorCMYK(*[v/100 for v in cfg.BOX_BACKGROUND_CMYK])
    c.roundRect(426,83,378,390,10,stroke=0,fill=1)
    c.setFillColorCMYK(*[v/100 for v in cfg.BOX_TEXT_CMYK])
    draw_mark(c,485,157,260,287,tight=True,version=2)
    size=min(33,320/pdfmetrics.stringWidth(cfg.GAME_NAME,"LogoProof",1))
    width=pdfmetrics.stringWidth(cfg.GAME_NAME,"LogoProof",size)
    label(c,cfg.GAME_NAME,615-width/2,110,size,tuple(v/100 for v in cfg.BOX_TEXT_CMYK))
    label(c,"One width: both rings, the stem outline and the openings between them",56,65,11)
    label(c,"Based on your second sketch. Editable vector geometry; no embedded image.",36,26,10)
    c.showPage()

    c.setFillColorCMYK(0,0,.025,.025)
    c.rect(0,0,840,600,stroke=0,fill=1)
    label(c,"MARRIAGE XP / COMPARE",36,558,10)
    label(c,"Two versions, one family.",36,518,28)
    for x,version,name in [(86,1,"01 / Original"),(467,2,"02 / Raised loop + open stem")]:
        c.setFillColorCMYK(0,0,0,1)
        draw_mark(c,x,149,270,304,tight=True,version=version)
        label(c,name,x,110,16)
    label(c,"Both versions remain available. Change LOGO_VERSION in game_config.py.",36,52,12)
    c.showPage()
    c.save()

    c = Canvas(str(OUT/"marriage-xp-v2-cmyk.pdf"),pagesize=(100*mm,130*mm),invariant=1,
               enforceColorSpace="CMYK",initialFontName="LogoProof")
    c.setTitle("Marriage XP - logo version 2 - process black")
    c.setFillColorCMYK(0,0,0,1)
    draw_mark(c,8*mm,8*mm,84*mm,114*mm,tight=True,version=2)
    c.showPage()
    c.save()
    print(f"Version 2 logo assets written to {OUT}")


if __name__ == "__main__":
    build()
