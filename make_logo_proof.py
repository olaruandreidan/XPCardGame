"""Generate vector SVGs and a CMYK logo/font study. Run with the PDF runtime."""
from pathlib import Path
from reportlab.pdfgen.canvas import Canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import mm
from logo import draw_mark, export_svg, LEFT_CENTER, ARM_RADIUS, BOWL_RADIUS, BOWL_CENTER_Y

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "output/logo"
OUT.mkdir(parents=True, exist_ok=True)
for name, path in [("Manrope", "manrope/Manrope-Bold.ttf"),
                   ("ManropeExtra", "manrope/Manrope-ExtraBold.ttf"),
                   ("Outfit", "Outfit-Bold.ttf")]:
    pdfmetrics.registerFont(TTFont(name, str(ROOT / "assets/fonts" / path)))


def ink(c, name):
    c.setFillColorCMYK(*{"blue":(.90,.70,0,0), "black":(0,0,0,1),
                         "muted":(0,0,0,.55), "paper":(0,0,.025,.025),
                         "white":(0,0,0,0)}[name])


def label(c, text, x, y, size=9, font="Manrope", shade="black"):
    ink(c,shade)
    c.setFont(font,size)
    c.drawString(x,y,text)


def background(c, shade):
    ink(c,shade)
    c.rect(0,0,840,600,stroke=0,fill=1)


def top(c, kicker, title):
    label(c,kicker,36,559,9,shade="muted")
    label(c,title,36,521,25)


def build():
    for name, fill in [("marriage-xp-black", "#000000"),
                       ("marriage-xp-blue", "#3555AB"),
                       ("marriage-xp-white", "#FFFFFF")]:
        export_svg(OUT / (name+".svg"), fill)

    c=Canvas(str(OUT/"logo-study.pdf"),pagesize=(840,600),enforceColorSpace="CMYK",
             invariant=1,initialFontName="Manrope")
    c.setTitle("Marriage XP - geometric logo study 01")
    background(c,"paper")
    top(c,"MARRIAGE XP / IDENTITY STUDY 01", "One shared stem. Two connected forms.")
    ink(c,"black")
    draw_mark(c,56,100,260,355)
    ink(c,"blue")
    c.roundRect(399,106,405,350,12,stroke=0,fill=1)
    ink(c,"white")
    draw_mark(c,424,194,118,176)
    label(c,"Marriage",566,300,34,"ManropeExtra","white")
    label(c,"XP",566,257,34,"ManropeExtra","white")
    label(c,"Conversations for a life together.",426,138,12,"Manrope","white")
    label(c,"GEOMETRIC MONOGRAM",56,69,9,shade="muted")
    label(c,"MANROPE EXTRABOLD + BOLD",399,69,9,shade="muted")
    label(c,"First direction from your sketch. Circular curves, even weight, flat terminals.",36,27,10)
    c.showPage()

    background(c,"paper")
    top(c,"CONSTRUCTION / 01", "A small set of repeatable rules.")
    x,y,w,h=110,130,210,325
    ink(c,"black")
    draw_mark(c,x,y,w,h)
    scale=min(w/338,h/468)
    c.saveState()
    c.translate(x+(w-338*scale)/2,y+(h+468*scale)/2)
    c.scale(scale,-scale)
    c.setStrokeColorCMYK(1,.2,0,0)
    c.setLineWidth(.7/scale)
    c.setDash(3/scale,3/scale)
    cx,cy=LEFT_CENTER
    for xx,yy,r in [(cx,cy,ARM_RADIUS),(cx+2*ARM_RADIUS,cy,ARM_RADIUS),
                    (cx+ARM_RADIUS+BOWL_RADIUS,BOWL_CENTER_Y,BOWL_RADIUS)]:
        c.circle(xx,yy,r,stroke=1,fill=0)
        c.line(xx-7,yy,xx+7,yy)
        c.line(xx,yy-7,xx,yy+7)
    c.line(cx+ARM_RADIUS,15,cx+ARM_RADIUS,450)
    c.restoreState()
    for yy,heading,body in [(417,"01 / Matched arms", "Both upper arms follow a radius of 128 units."),
                            (332,"02 / Circular loop", "A 68-unit radius keeps the right counter open."),
                            (247,"03 / One weight", "44-unit bands, a straight stem, and square ends.")]:
        label(c,heading,410,yy,17)
        label(c,body,410,yy-25,11)
    label(c,"SMALL-SIZE CHECK / ACTUAL MARK HEIGHT",410,158,9,shade="muted")
    for xx,size in [(414,12),(503,18),(610,25)]:
        ink(c,"black")
        # Visible ink spans 424 of the viewBox's 468 units.
        draw_mark(c,xx,58,size*mm*338/424,size*mm*468/424)
        label(c,f"{size} mm",xx,41,9,shade="muted")
    label(c,"Filled vector outlines. SVG uses display color; PDF uses process CMYK.",36,18,9)
    c.showPage()

    background(c,"paper")
    top(c,"TYPE / 02", "A font with the same circular rhythm.")
    for yy,font,cardfont,heading in [(306,"ManropeExtra","Manrope","MANROPE / RECOMMENDED"),
                                    (95,"Outfit","Outfit","OUTFIT / EXISTING ALTERNATIVE")]:
        label(c,heading,36,yy+155,9,shade="muted")
        ink(c,"black")
        draw_mark(c,36,yy,85,132)
        label(c,"Marriage",147,yy+81,37,font)
        label(c,"XP",147,yy+34,37,font)
        ink(c,"blue")
        c.rect(465,yy-10,339,160,stroke=0,fill=1)
        for i,line in enumerate(["How will we govern", "our finances?"]):
            label(c,line,487,yy+89-i*32,24,cardfont,"white")
    label(c,"Manrope: a quieter, more even texture. Outfit: rounder and more playful.",36,29,10)
    c.showPage()
    c.save()

    c=Canvas(str(OUT/"marriage-xp-mark-cmyk.pdf"),pagesize=(100*mm,140*mm),
             enforceColorSpace="CMYK",invariant=1,initialFontName="Manrope")
    c.setTitle("Marriage XP - vector mark - process black")
    ink(c,"black")
    draw_mark(c,5*mm,5*mm,90*mm,130*mm)
    c.showPage()
    c.save()
    print(f"Logo assets and proof written to {OUT}")


if __name__ == "__main__":
    build()
