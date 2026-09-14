"""Export version 1b and a study PDF using the project's PDF runtime."""
from pathlib import Path
from reportlab.pdfgen.canvas import Canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import mm
import logo
from logo import draw_mark, export_svg
from generate import load_config, resolve

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "output/logo/v1b"


def build():
    OUT.mkdir(parents=True, exist_ok=True)
    cfg = load_config(ROOT / "game_config.py")
    pdfmetrics.registerFont(TTFont("LogoProof", str(resolve(cfg, cfg.FONT_PATH))))
    for name, fill in [("black", "#000000"), ("blue", "#3555AB"), ("white", "#FFFFFF")]:
        export_svg(OUT/f"marriage-xp-v1b-{name}.svg", fill, version="1b")

    def label(c, text, x, y, size, color=(0,0,0,1)):
        c.setFillColorCMYK(*color)
        c.setFont("LogoProof", size)
        c.drawString(x,y,text)

    c = Canvas(str(OUT/"logo-v1b-study.pdf"), pagesize=(840,600), invariant=1,
               enforceColorSpace="CMYK", initialFontName="LogoProof")
    c.setTitle("Marriage XP - logo 1b")
    c.setFillColorCMYK(0,0,.025,.025)
    c.rect(0,0,840,600,stroke=0,fill=1)
    label(c,"MARRIAGE XP / LOGO 01b",36,558,10)
    label(c,"One radius for all four arms.",36,518,28)
    c.setFillColorCMYK(0,0,0,1)
    draw_mark(c,56,103,250,348,tight=True,version="1b")
    c.setFillColorCMYK(*[v/100 for v in cfg.BOX_BACKGROUND_CMYK])
    c.roundRect(426,83,378,390,10,stroke=0,fill=1)
    c.setFillColorCMYK(*[v/100 for v in cfg.BOX_TEXT_CMYK])
    draw_mark(c,485,157,260,287,tight=True,version="1b")
    size=min(33,320/pdfmetrics.stringWidth(cfg.GAME_NAME,"LogoProof",1))
    width=pdfmetrics.stringWidth(cfg.GAME_NAME,"LogoProof",size)
    label(c,cfg.GAME_NAME,615-width/2,110,size,tuple(v/100 for v in cfg.BOX_TEXT_CMYK))
    label(c,"Four circles of one radius, joined by a straight middle section",56,65,11)
    label(c,"Forked from version 1. Editable vector geometry; no embedded image.",36,26,10)
    c.showPage()

    c.setFillColorCMYK(0,0,.025,.025)
    c.rect(0,0,840,600,stroke=0,fill=1)
    label(c,"MARRIAGE XP / COMPARE",36,558,10)
    label(c,"Three versions, one family.",36,518,28)
    for x,version,name in [(66,1,"01 / Original"),(346,"1b","01b / Matched radii"),
                           (606,2,"02 / Raised loop")]:
        c.setFillColorCMYK(0,0,0,1)
        draw_mark(c,x,149,210,304,tight=True,version=version)
        label(c,name,x,110,14)
    label(c,"Set LOGO_VERSION in game_config.py to 1, \"1b\", or 2.",36,52,12)
    c.showPage()

    # Sweep study. The page sets V1B_ARC_EXTRA, draws, and puts it back;
    # nothing outside this function sees the change.
    keep = logo.V1B_ARC_EXTRA
    c.setFillColorCMYK(0,0,.025,.025)
    c.rect(0,0,840,600,stroke=0,fill=1)
    label(c,"MARRIAGE XP / LOGO 01b - SWEEP",36,558,10)
    label(c,"How far past the quarter turn?",36,518,28)
    for x,extra in [(56,0),(256,15),(456,25),(656,35)]:
        logo.V1B_ARC_EXTRA = float(extra)
        c.setFillColorCMYK(0,0,0,1)
        draw_mark(c,x,149,150,304,tight=True,version="1b")
        label(c,f"V1B_ARC_EXTRA = {extra}",x,110,13)
        label(c,f"mark {logo.mark_bounds('1b', True)[2]:.0f} wide",x,90,10)
    logo.V1B_ARC_EXTRA = keep
    label(c,"Version 1 is 286 wide. The extra sweep lengthens the three open arms "
             "and tilts their cut ends.",36,52,12)
    c.showPage()
    c.save()

    c = Canvas(str(OUT/"marriage-xp-v1b-cmyk.pdf"),pagesize=(100*mm,130*mm),invariant=1,
               enforceColorSpace="CMYK",initialFontName="LogoProof")
    c.setTitle("Marriage XP - logo version 1b - process black")
    c.setFillColorCMYK(0,0,0,1)
    draw_mark(c,8*mm,8*mm,84*mm,114*mm,tight=True,version="1b")
    c.showPage()
    c.save()
    print(f"Version 1b logo assets written to {OUT}")


if __name__ == "__main__":
    build()
