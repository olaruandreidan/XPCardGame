"""Export version 3 and a study PDF using the project's PDF runtime."""
from pathlib import Path
from reportlab.pdfgen.canvas import Canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import mm
import logo
from logo import draw_mark, export_svg
from generate import load_config, resolve

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "output/logo/v3"


def build():
    OUT.mkdir(parents=True, exist_ok=True)
    cfg = load_config(ROOT / "game_config.py")
    pdfmetrics.registerFont(TTFont("LogoProof", str(resolve(cfg, cfg.FONT_PATH))))
    for name, fill in [("black", "#000000"), ("blue", "#3555AB"), ("white", "#FFFFFF")]:
        export_svg(OUT/f"marriage-xp-v3-{name}.svg", fill, version=3)

    def label(c, text, x, y, size, color=(0,0,0,1)):
        c.setFillColorCMYK(*color)
        c.setFont("LogoProof", size)
        c.drawString(x,y,text)

    c = Canvas(str(OUT/"logo-v3-study.pdf"), pagesize=(840,600), invariant=1,
               enforceColorSpace="CMYK", initialFontName="LogoProof")
    c.setTitle("Marriage XP - logo 3")
    c.setFillColorCMYK(0,0,.025,.025)
    c.rect(0,0,840,600,stroke=0,fill=1)
    label(c,"MARRIAGE XP / LOGO 03",36,558,10)
    label(c,"Equal arms. Crisp inner corners.",36,518,28)
    c.setFillColorCMYK(0,0,0,1)
    draw_mark(c,56,103,250,348,tight=True,version=3)
    c.setFillColorCMYK(*[v/100 for v in cfg.BOX_BACKGROUND_CMYK])
    c.roundRect(426,83,378,390,10,stroke=0,fill=1)
    c.setFillColorCMYK(*[v/100 for v in cfg.BOX_TEXT_CMYK])
    draw_mark(c,485,157,260,287,tight=True,version=3)
    size=min(33,320/pdfmetrics.stringWidth(cfg.GAME_NAME,"LogoProof",1))
    width=pdfmetrics.stringWidth(cfg.GAME_NAME,"LogoProof",size)
    label(c,cfg.GAME_NAME,615-width/2,110,size,tuple(v/100 for v in cfg.BOX_TEXT_CMYK))
    label(c,"P over X / matching arm lengths / rounded ends",56,65,11)
    label(c,"Based on your third sketch. Editable vector geometry; no embedded image.",36,26,10)
    c.showPage()

    c.setFillColorCMYK(0,0,.025,.025)
    c.rect(0,0,840,600,stroke=0,fill=1)
    label(c,"MARRIAGE XP / COMPARE",36,558,10)
    label(c,"Four versions, one family.",36,518,28)
    for x,version,name in [(46,1,"01 / Original"),(246,"1b","01b / Matched radii"),
                           (446,2,"02 / Raised loop"),(646,3,"03 / P over X")]:
        c.setFillColorCMYK(0,0,0,1)
        draw_mark(c,x,149,160,304,tight=True,version=version)
        label(c,name,x,110,13)
    label(c,"Set LOGO_VERSION in game_config.py to 1, \"1b\", 2, or 3.",36,52,12)
    c.showPage()

    c.setFillColorCMYK(0,0,.025,.025)
    c.rect(0,0,840,600,stroke=0,fill=1)
    label(c,"MARRIAGE XP / LOGO 03 - CONSTRUCTION",36,558,10)
    label(c,"Two letters. A shared diagonal.",36,518,28)
    components = logo.v3_paths(combined=False)
    vx,vy,vw,vh = logo.mark_bounds(3,True)
    for x,parts,caption in [(44,[components[0]],"Outlined X diagonal"),
                            (316,[components[1]],"Solid capital P"),
                            (588,logo.geometry_v3(),"Combined monogram")]:
        c.setFillColorCMYK(0,0,0,1)
        scale=min(205/vw,270/vh)
        c.saveState()
        c.translate(x+(205-vw*scale)/2,185+(270+vh*scale)/2)
        c.scale(scale,-scale)
        c.translate(-vx,-vy)
        for contour in parts:
            path=c.beginPath()
            for op,*values in contour:
                {"M":path.moveTo,"L":path.lineTo,"C":path.curveTo,"Z":path.close}[op](*values)
            c.drawPath(path,stroke=0,fill=1,fillMode=1)
        c.restoreState()
        label(c,caption,x,148,14)
    label(c,"The P's stem forms one arm of the X. Its bowl and counter turn with the stem.",36,88,12)
    label(c,"All four arms share one length. Rounded ends; sharp inward corners at the crossing.",36,62,12)
    c.showPage()
    c.save()

    c = Canvas(str(OUT/"marriage-xp-v3-cmyk.pdf"),pagesize=(100*mm,130*mm),invariant=1,
               enforceColorSpace="CMYK",initialFontName="LogoProof")
    c.setTitle("Marriage XP - logo version 3 - process black")
    c.setFillColorCMYK(0,0,0,1)
    draw_mark(c,8*mm,8*mm,84*mm,114*mm,tight=True,version=3)
    c.showPage()
    c.save()
    print(f"Version 3 logo assets written to {OUT}")


if __name__ == "__main__":
    build()
