#!/usr/bin/env python3
"""Generate Marriage XP's CMYK cards, reverse-tuck carton and proof PDFs."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import io
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time


def ensure_pdf_runtime():
    """Let a plain python3 command reuse an already-equipped local interpreter."""
    if all(importlib.util.find_spec(name) is not None for name in ("reportlab", "pypdf")):
        return
    root = Path(__file__).resolve().parent
    candidates = [
        root / ".venv" / "bin" / "python3",
        root / ".venv" / "Scripts" / "python.exe",
        Path.home() / ".cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3",
    ]
    for python in candidates:
        if not python.is_file() or python.resolve() == Path(sys.executable).resolve():
            continue
        try:
            probe = subprocess.run([str(python), "-c", "import reportlab, pypdf"],
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                   timeout=10)
        except (OSError, subprocess.TimeoutExpired):
            continue
        if probe.returncode == 0:
            print("Using the available PDF tools from " + str(python), flush=True)
            os.execv(str(python), [str(python), str(Path(__file__).resolve()), *sys.argv[1:]])
    print("PDF dependencies are missing. From this project folder, run:\n\n"
          "  python3 -m venv .venv\n"
          "  .venv/bin/python3 -m pip install -r requirements.txt\n\n"
          "Then retry: python3 generate.py --watch\n"
          "On Windows, use .venv\\Scripts\\python.exe instead of .venv/bin/python3.",
          file=sys.stderr)
    raise SystemExit(1)


if __name__ == "__main__":
    ensure_pdf_runtime()

from reportlab.lib.colors import CMYKColor, CMYKColorSep
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas
from reportlab.graphics.barcode import qr as qrcodes
from pypdf import PdfReader, PdfWriter
from pypdf.generic import (ArrayObject, DecodedStreamObject, DictionaryObject,
                          NameObject, NumberObject, RectangleObject, TextStringObject)

from logo import draw_logo, draw_mark

ROOT = Path(__file__).resolve().parent
FONT = "GameFont"


def color(value):
    if len(value) != 4 or any(not isinstance(v, (int, float)) or not math.isfinite(v)
                              or not 0 <= v <= 100 for v in value):
        raise ValueError(f"CMYK must have four channels in 0..100: {value!r}")
    return CMYKColor(*(v / 100 for v in value))


def card_background(cfg, card):
    name = card.get("color", cfg.DEFAULT_CARD_COLOR)
    if not isinstance(name, str) or name not in cfg.CARD_COLORS_CMYK:
        raise ValueError(f"Unknown card color {name!r}. Choose from {', '.join(cfg.CARD_COLORS_CMYK)}.")
    return card.get("background_cmyk", cfg.CARD_COLORS_CMYK[name])


def load_config(path):
    spec = importlib.util.spec_from_file_location("card_game_config", path)
    cfg = importlib.util.module_from_spec(spec)
    # Compile the source directly, so fast successive edits never use stale bytecode.
    exec(compile(path.read_text(encoding="utf-8"), str(path), "exec"), cfg.__dict__)
    cfg.BASE = path.parent
    return cfg


def resolve(cfg, path):
    return (cfg.BASE / Path(path).expanduser()).resolve()


def positive(value, name, zero=False):
    if (not isinstance(value, (int, float)) or isinstance(value, bool)
            or not math.isfinite(value) or value < 0 or (not zero and value == 0)):
        raise ValueError(f"{name} must be {'non-negative' if zero else 'positive'} and finite.")


def validate(cfg):
    global FONT
    for name in ("CARD_WIDTH_MM", "CARD_HEIGHT_MM", "SAFE_MARGIN_MM", "FONT_SIZE_PT",
                 "MIN_FONT_SIZE_PT", "LINE_HEIGHT", "CARD_THICKNESS_MM",
                 "BOX_BOARD_THICKNESS_MM", "BOX_MIN_INTERNAL_DEPTH_MM",
                 "BOX_GLUE_TAB_MM", "BOX_TUCK_TAB_MM", "BOX_MARGIN_MM",
                 "BOX_FRONT_FONT_SIZE_PT", "BOX_BACK_FONT_SIZE_PT"):
        positive(getattr(cfg, name), name)
    for name in ("BLEED_MM", "BOX_WIDTH_CLEARANCE_MM", "BOX_HEIGHT_CLEARANCE_MM",
                 "BOX_DEPTH_CLEARANCE_MM"):
        positive(getattr(cfg, name), name, zero=True)
    if cfg.LINE_HEIGHT < 1:
        raise ValueError("LINE_HEIGHT must be at least 1 to avoid overlapping lines.")
    if 2 * cfg.SAFE_MARGIN_MM >= min(cfg.CARD_WIDTH_MM, cfg.CARD_HEIGHT_MM):
        raise ValueError("SAFE_MARGIN_MM leaves no room for card text.")
    if cfg.BOX_MARGIN_MM < cfg.BLEED_MM:
        raise ValueError("BOX_MARGIN_MM must be at least BLEED_MM.")
    if cfg.MIN_FONT_SIZE_PT > cfg.FONT_SIZE_PT:
        raise ValueError("MIN_FONT_SIZE_PT must not exceed FONT_SIZE_PT.")
    if cfg.TEXT_VERTICAL_ALIGN not in ("top", "center", "bottom"):
        raise ValueError("TEXT_VERTICAL_ALIGN must be top, center, or bottom.")
    for name in ("TEXT_CMYK", "BOX_BACKGROUND_CMYK", "BOX_TEXT_CMYK"):
        color(getattr(cfg, name))
    color(getattr(cfg, "CARD_BACK_LOGO_CMYK", cfg.TEXT_CMYK))
    back_scale = getattr(cfg, "CARD_BACK_LOGO_SCALE", 0.7)
    positive(back_scale, "CARD_BACK_LOGO_SCALE")
    if back_scale > 1:
        raise ValueError("CARD_BACK_LOGO_SCALE must be at most 1.")
    if not isinstance(cfg.CARD_COLORS_CMYK, dict) or not cfg.CARD_COLORS_CMYK:
        raise ValueError("CARD_COLORS_CMYK must contain at least one named color.")
    for name, channels in cfg.CARD_COLORS_CMYK.items():
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Card color names must be non-empty strings.")
        color(channels)
    card_background(cfg, {})  # Validate the default even when every card overrides it.
    if not cfg.CARDS:
        raise ValueError("Add at least one phrase to CARDS.")
    if not isinstance(cfg.GAME_NAME, str) or not cfg.GAME_NAME.strip():
        raise ValueError("GAME_NAME must be a non-empty string.")
    cards = []
    for index, entry in enumerate(cfg.CARDS, 1):
        card = {"text": entry} if isinstance(entry, str) else dict(entry)
        unknown = set(card) - {"text", "color", "copies", "background_cmyk", "text_cmyk",
                               "font_size_pt", "qr"}
        if unknown:
            raise ValueError(f"Card {index}: unknown settings {sorted(unknown)}")
        if not isinstance(card.get("text"), str) or not card["text"].strip():
            raise ValueError(f"Card {index}: text must be a non-empty string.")
        if "qr" in card and (not isinstance(card["qr"], str) or not card["qr"].strip()):
            raise ValueError(f"Card {index}: qr must be a non-empty URL string.")
        copies = card.get("copies", 1)
        if type(copies) is not int or copies < 1:
            raise ValueError(f"Card {index}: copies must be a positive integer.")
        for key in ("background_cmyk", "text_cmyk"):
            if key in card:
                color(card[key])
        positive(card.get("font_size_pt", cfg.FONT_SIZE_PT), f"Card {index} font size")
        color(card_background(cfg, card))
        cards.extend([card] * copies)
    font_path = resolve(cfg, cfg.FONT_PATH)
    if not font_path.is_file():
        raise ValueError(f"Font not found: {font_path}")
    # ReportLab keeps the first font registered under an alias. Give each font
    # its own alias so repeated builds in one Python process can change fonts.
    identity = f"{font_path}:{cfg.FONT_COLLECTION_INDEX}"
    FONT = "GameFont_" + hashlib.sha256(identity.encode()).hexdigest()[:16]
    pdfmetrics.registerFont(TTFont(FONT, str(font_path), subfontIndex=cfg.FONT_COLLECTION_INDEX))
    all_text = "".join(c["text"] for c in cards) + cfg.GAME_NAME + cfg.BOX_BACK_TEXT
    cmap = pdfmetrics.getFont(FONT).face.charToGlyph
    missing = sorted({ch for ch in all_text if not ch.isspace() and ord(ch) not in cmap})
    if missing:
        raise ValueError(f"The selected font lacks these characters: {''.join(missing)!r}")
    return cards


def wrap(text, size, width):
    lines = []
    for paragraph in text.split("\n"):
        current = ""
        for word in paragraph.split():
            if pdfmetrics.stringWidth(word, FONT, size) > width:
                return None
            candidate = f"{current} {word}" if current else word
            if pdfmetrics.stringWidth(candidate, FONT, size) <= width:
                current = candidate
            else:
                lines.append(current)
                current = word
        lines.append(current)
    return lines


def fit(text, width, height, requested, minimum, leading, shrink=True):
    size = requested
    minimum = min(minimum, requested)
    while size >= minimum - 0.001:
        lines = wrap(text, size, width)
        ascent, descent = pdfmetrics.getAscentDescent(FONT, size)
        total = (len(lines) - 1) * size * leading + ascent - descent if lines else math.inf
        if total <= height + 0.001:
            return lines, size, total, ascent
        if not shrink or size <= minimum:
            break
        size = max(minimum, round(size - 0.25, 3))
    raise ValueError(f"Text cannot fit at {minimum:g} pt: {text!r}. Reduce size/margins or edit the phrase.")


def qr_modules(url, level="M"):
    """The QR matrix, as rows of booleans. ReportLab encodes it; we draw it."""
    widget = qrcodes.QrCodeWidget(url, barLevel=level)
    widget.getBounds()  # The encoding happens here.
    modules = widget.qr.modules
    if not modules:
        raise ValueError(f"Could not encode a QR code for {url!r}.")
    return [[bool(cell) for cell in row] for row in modules]


def draw_qr(c, url, x, y, side, quiet=4, level="M"):
    """Fill a QR code into a square, in the canvas's current color.

    Every dark module goes into one path, with each row's neighbours merged
    into a single rectangle. One path means one fill, so the rasterizer
    resolves the whole union at once and shared module edges cannot show a
    seam the way separately drawn shapes can.
    """
    modules = qr_modules(url, level)
    count = len(modules)+2*quiet
    step = side/count
    path = c.beginPath()
    for row, cells in enumerate(modules):
        col = 0
        while col < len(cells):
            if not cells[col]:
                col += 1
                continue
            end = col
            while end < len(cells) and cells[end]:
                end += 1
            left = x+(quiet+col)*step
            top = y+side-(quiet+row)*step
            path.moveTo(left, top)
            path.lineTo(left+(end-col)*step, top)
            path.lineTo(left+(end-col)*step, top-step)
            path.lineTo(left, top-step)
            path.close()
            col = end
    c.drawPath(path, stroke=0, fill=1)
    return step


def text_block(c, text, x, y, width, height, size, minimum, leading=1.1,
               align="top", shrink=True):
    lines, actual, total, ascent = fit(text, width, height, size, minimum, leading, shrink)
    top = y + height
    if align == "center":
        top -= (height - total) / 2
    elif align == "bottom":
        top = y + total
    c.setFont(FONT, actual)
    for i, line in enumerate(lines):
        c.drawString(x, top - ascent - i * actual * leading, line)
    return actual


def canvas_for(buffer, size, title, separation=False):
    c = Canvas(buffer, pagesize=size, pageCompression=1, invariant=1,
               pdfVersion=(1, 4), enforceColorSpace="SEP_CMYK" if separation else "CMYK",
               initialFontName=FONT)
    c.setTitle(title)
    c.setAuthor("Marriage XP card generator")
    c.setCreator("Marriage XP / ReportLab")
    return c


def embed_profile(writer, cfg):
    if not cfg.ICC_PROFILE_PATH:
        return
    data = resolve(cfg, cfg.ICC_PROFILE_PATH).read_bytes()
    if (len(data) < 128 or data[36:40] != b"acsp" or data[16:20] != b"CMYK"
            or int.from_bytes(data[:4], "big") != len(data)):
        raise ValueError("ICC_PROFILE_PATH must point to a valid CMYK ICC profile.")
    profile = DecodedStreamObject()
    profile.set_data(data)
    profile[NameObject("/N")] = NumberObject(4)
    intent = DictionaryObject({
        NameObject("/Type"): NameObject("/OutputIntent"),
        NameObject("/S"): NameObject("/GTS_PDFX"),
        NameObject("/OutputConditionIdentifier"): TextStringObject(cfg.ICC_OUTPUT_CONDITION),
        NameObject("/Info"): TextStringObject(cfg.ICC_OUTPUT_CONDITION),
        NameObject("/DestOutputProfile"): writer._add_object(profile),
    })
    writer._root_object[NameObject("/OutputIntents")] = ArrayObject([writer._add_object(intent)])


def save_pdf(buffer, target, cfg, trim=None, bleed=None):
    reader = PdfReader(buffer)
    writer = PdfWriter()
    writer.append(reader)
    if reader.metadata:
        writer.add_metadata(dict(reader.metadata))
    for page in writer.pages:
        for name, bounds in (("trimbox", trim), ("bleedbox", bleed)):
            if bounds:
                # ReportLab rounds MediaBox coordinates. Reuse those exact
                # values when a requested box is the full page (e.g. no bleed).
                if all(abs(float(a)-float(b)) < 0.001 for a, b in zip(bounds, page.mediabox)):
                    bounds = page.mediabox
                setattr(page, name, RectangleObject(bounds))
    embed_profile(writer, cfg)
    with target.open("wb") as f:
        writer.write(f)


def make_cards(cfg, cards, target, bleed_mm=None):
    bleed_mm = cfg.BLEED_MM if bleed_mm is None else bleed_mm
    w, h, b, m = (v * mm for v in (cfg.CARD_WIDTH_MM, cfg.CARD_HEIGHT_MM,
                                  bleed_mm, cfg.SAFE_MARGIN_MM))
    buffer = io.BytesIO()
    title = cfg.GAME_NAME + (" - cards (no bleed)" if b == 0 else " - cards")
    c = canvas_for(buffer, (w + 2*b, h + 2*b), title)
    sizes = []
    for i, card in enumerate(cards, 1):
        c.setFillColor(color(card_background(cfg, card)))
        c.rect(0, 0, w + 2*b, h + 2*b, stroke=0, fill=1)
        text_height = h-2*m
        if card.get("qr"):
            # A QR needs a light field and a quiet zone to scan, so it sits on
            # a panel in the card's text color with the modules in the card's
            # background color: the card inverted, rather than a foreign white.
            share = getattr(cfg, "CARD_QR_HEIGHT_SHARE", 0.62)
            side = min(w-2*m, (h-2*m)*share)
            gap = min(4*mm, max(0.0, (h-2*m-side)/3))
            panel_x, panel_y = b+m+(w-2*m-side)/2, b+m+(h-2*m)-side
            c.setFillColor(color(card.get("text_cmyk", cfg.TEXT_CMYK)))
            # The corner radius stays inside the four-module quiet zone.
            c.roundRect(panel_x, panel_y, side, side, side*0.06, stroke=0, fill=1)
            c.setFillColor(color(card_background(cfg, card)))
            draw_qr(c, card["qr"], panel_x, panel_y, side)
            text_height = panel_y-(b+m)-gap
            if text_height <= 0:
                raise ValueError(f"Card page {i}: the QR panel leaves no room for text. "
                                 "Lower CARD_QR_HEIGHT_SHARE.")
        c.setFillColor(color(card.get("text_cmyk", cfg.TEXT_CMYK)))
        try:
            sizes.append(text_block(c, card["text"], b+m, b+m, w-2*m, text_height,
                                    card.get("font_size_pt", cfg.FONT_SIZE_PT),
                                    cfg.MIN_FONT_SIZE_PT, cfg.LINE_HEIGHT,
                                    cfg.TEXT_VERTICAL_ALIGN, cfg.AUTO_SHRINK_TEXT))
        except ValueError as exc:
            raise ValueError(f"Card page {i}: {exc}") from exc
        c.showPage()
    c.save()
    save_pdf(buffer, target, cfg, (b, b, b+w, b+h), (0, 0, w+2*b, h+2*b))
    return sizes


def card_back_designs(cfg, cards):
    """Palette order, then extra custom inks; record matching front page numbers."""
    backs = [dict(color=name, background_cmyk=list(ink), front_pages=[])
             for name, ink in cfg.CARD_COLORS_CMYK.items()]
    named = {back["color"]: back for back in backs}
    for page, card in enumerate(cards, 1):
        ink = list(card_background(cfg, card))
        back = named[card.get("color", cfg.DEFAULT_CARD_COLOR)]
        if back["background_cmyk"] != ink:
            back = next((item for item in backs if item["background_cmyk"] == ink), None)
            if back is None:
                back = dict(color=None, background_cmyk=ink, front_pages=[])
                backs.append(back)
        back["front_pages"].append(page)
    for page, back in enumerate(backs, 1):
        back["page"] = page
    return backs


def make_card_backs(cfg, backs, target, bleed_mm=None):
    bleed_mm = cfg.BLEED_MM if bleed_mm is None else bleed_mm
    w, h, b, m = (v * mm for v in (cfg.CARD_WIDTH_MM, cfg.CARD_HEIGHT_MM,
                                  bleed_mm, cfg.SAFE_MARGIN_MM))
    scale = getattr(cfg, "CARD_BACK_LOGO_SCALE", 0.7)
    logo_w, logo_h = min(w*scale, w-2*m), min(h*scale, h-2*m)
    buffer = io.BytesIO()
    title = cfg.GAME_NAME + " - card backs" + (" (no bleed)" if b == 0 else "")
    c = canvas_for(buffer, (w+2*b, h+2*b), title)
    for back in backs:
        c.setFillColor(color(back["background_cmyk"]))
        c.rect(0, 0, w+2*b, h+2*b, stroke=0, fill=1)
        c.setFillColor(color(getattr(cfg, "CARD_BACK_LOGO_CMYK", cfg.TEXT_CMYK)))
        # Version 3 centers on the X crossing; other marks use visible bounds.
        draw_mark(c, b+(w-logo_w)/2, b+(h-logo_h)/2, logo_w, logo_h,
                  tight=True, version=getattr(cfg, "LOGO_VERSION", 1))
        c.showPage()
    c.save()
    save_pdf(buffer, target, cfg, (b, b, b+w, b+h), (0, 0, w+2*b, h+2*b))


def box_geometry(cfg, count):
    required = count * cfg.CARD_THICKNESS_MM + cfg.BOX_DEPTH_CLEARANCE_MM
    depth = max(required, cfg.BOX_MIN_INTERNAL_DEPTH_MM)
    if cfg.BOX_INTERNAL_DEPTH_MM is not None:
        positive(cfg.BOX_INTERNAL_DEPTH_MM, "BOX_INTERNAL_DEPTH_MM")
        depth = cfg.BOX_INTERNAL_DEPTH_MM
        if depth < required:
            raise ValueError(f"Box internal depth must be at least {required:.2f} mm for this deck.")
    # A single board caliper between score centerlines approximates inside dimensions.
    # Printer tooling/stock can require different allowances: always make a prototype.
    board = cfg.BOX_BOARD_THICKNESS_MM
    W = cfg.CARD_WIDTH_MM + cfg.BOX_WIDTH_CLEARANCE_MM + board
    H = cfg.CARD_HEIGHT_MM + cfg.BOX_HEIGHT_CLEARANCE_MM + board
    D = depth + board
    G, T = cfg.BOX_GLUE_TAB_MM, cfg.BOX_TUCK_TAB_MM
    if G >= W or T >= H or D >= W:
        raise ValueError("Tuck-box geometry requires glue tab < width, tuck tab < height, and depth < width.")
    x = [G, G+W, G+W+D, G+2*W+D, G+2*W+2*D]
    cut, fold = [], []
    def segments(points, dest):
        dest.extend(zip(points, points[1:]))
    bevel = min(3, H/8, G/3)
    segments([(G, 0), (0, bevel), (0, H-bevel), (G, H)], cut)
    cut.append(((x[-1], 0), (x[-1], H)))
    fold.extend([((xx, 0), (xx, H)) for xx in x[:-1]])
    # Back / side / front / side. Top tuck on front; bottom tuck on back.
    for top in (False, True):
        y, sign = (H, 1) if top else (0, -1)
        for panel in range(4):
            a, z = x[panel], x[panel+1]
            if panel == (2 if top else 0):
                inset = min(2, W/10)
                segments([(a, y), (a, y+sign*D), (a+inset, y+sign*(D+T)),
                          (z-inset, y+sign*(D+T)), (z, y+sign*D), (z, y)], cut)
                fold.extend([((a, y), (z, y)), ((a, y+sign*D), (z, y+sign*D))])
            elif panel in (1, 3):
                length = min(W*0.45, D*1.4)
                inset = min(2, D/5)
                segments([(a, y), (a+inset, y+sign*length),
                          (z-inset, y+sign*length), (z, y)], cut)
                fold.append(((a, y), (z, y)))
            else:
                cut.append(((a, y), (z, y)))
    extension = max(D+T, min(W*0.45, D*1.4))
    return dict(W=W, H=H, D=D, G=G, T=T, x=x, cut=cut, fold=fold,
                extension=extension, depth=depth, required=required,
                net_width=x[-1], net_height=H+2*extension)


def box_art(c, cfg, g):
    W, H, D, G, T = (g[k]*mm for k in ("W", "H", "D", "G", "T"))
    b = cfg.BLEED_MM*mm
    e = g["extension"]*mm
    # Flood the entire bounding rectangle: all cut edges, including flap slits,
    # have at least the configured bleed. The surplus is outside the cut outline.
    c.setFillColor(color(cfg.BOX_BACKGROUND_CMYK))
    c.rect(-b, -e-b, g["net_width"]*mm+2*b, H+2*e+2*b, fill=1, stroke=0)
    # Keep the usable central glue area unprinted; taper ends remain sacrificial.
    c.setFillColorCMYK(0, 0, 0, 0)
    gap = min(2*mm, G/4, H/8)
    c.rect(gap, 3*gap, G-2*gap, H-6*gap, fill=1, stroke=0)
    c.setFillColor(color(cfg.BOX_TEXT_CMYK))
    margin = min(7*mm, W*0.14, H*0.1)
    front = g["x"][2]*mm
    # Reserve only the actual name height at the bottom; give the mark all
    # remaining safe space, preserving its aspect ratio and visible bounds.
    front_margin = min(3*mm, W*0.08, H*0.05)
    usable = W-2*front_margin
    lines, title_size, title_height, ascent = fit(
        cfg.GAME_NAME, usable, H*0.20, cfg.BOX_FRONT_FONT_SIZE_PT, 12, 1.05)
    c.setFont(FONT, title_size)
    for i, line in enumerate(lines):
        line_width = pdfmetrics.stringWidth(line, FONT, title_size)
        c.drawString(front+(W-line_width)/2,
                     front_margin+title_height-ascent-i*title_size*1.05, line)
    logo_bottom = front_margin+title_height+front_margin
    logo_height = H-front_margin-logo_bottom
    # Equal padding above the title and below the top edge centers v3's X
    # crossing in that remaining space, independently of the title's height.
    c.saveState()
    draw_logo(c, front+front_margin, logo_bottom, usable,
              logo_height, cfg)
    c.restoreState()
    if cfg.BOX_BACK_TEXT:
        text_block(c, cfg.BOX_BACK_TEXT, G+margin, margin, W-2*margin, H-2*margin,
                   cfg.BOX_BACK_FONT_SIZE_PT, 8, 1.2, "center")


def box_lines(c, g):
    c.saveState()
    c.setStrokeOverprint(True)
    c.setLineWidth(0.3)
    for key, ink, dash in (("cut", CMYKColorSep(0, 1, 0, 0, spotName="CutContour"), []),
                           ("fold", CMYKColorSep(1, 0, 0, 0, spotName="Crease"), [3, 2])):
        c.setStrokeColor(ink)
        c.setDash(dash)
        for p, q in g[key]:
            c.line(p[0]*mm, p[1]*mm, q[0]*mm, q[1]*mm)
    c.restoreState()


def make_box(cfg, g, target, artwork, guides):
    m, e, b = cfg.BOX_MARGIN_MM*mm, g["extension"]*mm, cfg.BLEED_MM*mm
    size = (g["net_width"]*mm+2*m, g["net_height"]*mm+2*m)
    buffer = io.BytesIO()
    c = canvas_for(buffer, size, cfg.GAME_NAME + " - " + target.stem, guides)
    c.translate(m, m+e)
    if artwork:
        box_art(c, cfg, g)
    if guides:
        box_lines(c, g)
    c.showPage()
    c.save()
    # Box TrimBox is the dieline bounding rectangle, not the cut contour itself.
    save_pdf(buffer, target, cfg, (m, m, size[0]-m, size[1]-m),
             (m-b, m-b, size[0]-m+b, size[1]-m+b))
    return [round(v/mm, 3) for v in size]


def combine(cfg, paths, target):
    writer = PdfWriter()
    for path in paths:
        writer.append(path)
    writer.add_metadata({"/Title": cfg.GAME_NAME + " - cards and box proof"})
    embed_profile(writer, cfg)
    with target.open("wb") as stream:
        writer.write(stream)


def build(cfg):
    cards = validate(cfg)
    backs = card_back_designs(cfg, cards)
    g = box_geometry(cfg, len(cards))
    output = resolve(cfg, cfg.OUTPUT_DIR)
    output.mkdir(parents=True, exist_ok=True)
    # Stage every output so invalid edits cannot replace the last successful set.
    with tempfile.TemporaryDirectory(prefix=".build-", dir=output) as scratch:
        stage = Path(scratch)
        if os.name == "nt":
            # Windows temporary directories have private ACLs. Inherit the
            # output folder's permissions before creating files, so moving
            # them into output does not lock out the desktop user's viewer.
            subprocess.run(["icacls", str(stage), "/reset"], check=True,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                           text=True)
        sizes = make_cards(cfg, cards, stage / "cards.pdf")
        make_cards(cfg, cards, stage / "cards-no-bleed.pdf", bleed_mm=0)
        make_card_backs(cfg, backs, stage / "card-backs.pdf")
        # One no-bleed file per back color, named by palette key or a custom
        # index; card_back_designs() already merges duplicate custom inks, so
        # each back here is a visually distinct color.
        custom_backs = 0
        for back in backs:
            if back["color"]:
                slug = back["color"]
            else:
                custom_backs += 1
                slug = f"custom-{custom_backs}"
            filename = f"card-backs-no-bleed-{slug}.pdf"
            make_card_backs(cfg, [back], stage / filename, bleed_mm=0)
            back["no_bleed_file"] = filename
        page_size = make_box(cfg, g, stage / "box-artwork.pdf", True, False)
        make_box(cfg, g, stage / "box-dieline.pdf", False, True)
        make_box(cfg, g, stage / "box-proof.pdf", True, True)
        combine(cfg, [stage / "cards.pdf", stage / "box-proof.pdf"], stage / "game.pdf")
        report = dict(game=cfg.GAME_NAME, card_count=len(cards),
                      card_format=getattr(cfg, "CARD_FORMAT", "custom"),
                      card_backgrounds_cmyk=[card_background(cfg, card) for card in cards],
                      card_backs=backs,
                      card_back_logo_cmyk=getattr(cfg, "CARD_BACK_LOGO_CMYK", cfg.TEXT_CMYK),
                      card_back_logo_scale=getattr(cfg, "CARD_BACK_LOGO_SCALE", 0.7),
                      box_background_cmyk=cfg.BOX_BACKGROUND_CMYK,
                      vector_logo_enabled=getattr(cfg, "USE_VECTOR_LOGO", False),
                      logo_version=getattr(cfg, "LOGO_VERSION", 1),
                      card_trim_mm=[cfg.CARD_WIDTH_MM, cfg.CARD_HEIGHT_MM],
                      bleed_mm=cfg.BLEED_MM, card_font_sizes_pt=sizes,
                      no_bleed_card_page_mm=[cfg.CARD_WIDTH_MM, cfg.CARD_HEIGHT_MM],
                      estimated_box_internal_mm=[g["W"]-cfg.BOX_BOARD_THICKNESS_MM,
                                                g["H"]-cfg.BOX_BOARD_THICKNESS_MM, g["depth"]],
                      box_score_panel_mm=[g["W"], g["H"], g["D"]],
                      box_page_mm=page_size, icc_profile=cfg.ICC_PROFILE_PATH,
                      notes=["Card fronts and color-matched backs are separate PDFs; no duplex pairing or sheet imposition.",
                             "card-backs.pdf has one page per back, in the card_backs page order; each back's no_bleed_file is its own single-page PDF instead.",
                             "cards-no-bleed.pdf has exact finished-size pages, without bleed or cut marks, for printer imposition.",
                             "game.pdf ends with box-proof.pdf, including visible cut/fold guides.",
                             "Send separate box artwork and dieline for production; guides are spot separations.",
                             "CMYK PDF, not certified PDF/X. Confirm profile and dieline with the printer.",
                             "Make a 100% scale physical prototype using your actual card and box stock."])
        (stage / "build-report.json").write_text(json.dumps(report, indent=2)+"\n", encoding="utf-8")
        for path in stage.iterdir():
            path.replace(output / path.name)
        stale = output / "card-backs-no-bleed.pdf"
        if stale.exists():
            stale.unlink()
    print(f"Built {len(cards)} cards ({cfg.CARD_WIDTH_MM:g} x {cfg.CARD_HEIGHT_MM:g} mm).")
    print(f"Estimated box inside: {g['W']-cfg.BOX_BOARD_THICKNESS_MM:g} x "
          f"{g['H']-cfg.BOX_BOARD_THICKNESS_MM:g} x {g['depth']:g} mm.")
    print(f"PDFs saved to {output}")
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "game_config.py")
    parser.add_argument("--watch", action="store_true", help="Rebuild when config, logo, or font changes.")
    parser.add_argument("--format", choices=("poker", "square", "tarot"),
                        help="Override the card format; write to OUTPUT_DIR/<format>/ for comparison.")
    args = parser.parse_args()
    path = args.config.resolve()
    signature = None
    while True:
        try:
            cfg = load_config(path)
            if args.format:
                cfg.CARD_FORMAT = args.format
                cfg.CARD_WIDTH_MM, cfg.CARD_HEIGHT_MM = cfg.CARD_FORMATS_MM[args.format]
                cfg.OUTPUT_DIR = str(Path(cfg.OUTPUT_DIR) / args.format)
            watched = [path, ROOT / "logo.py", resolve(cfg, cfg.FONT_PATH), Path(__file__)]
            if cfg.ICC_PROFILE_PATH:
                watched.append(resolve(cfg, cfg.ICC_PROFILE_PATH))
            current = tuple((p.stat().st_mtime_ns, p.stat().st_size) for p in watched)
            if current != signature:
                # A child process also reloads generator/logo code on every rebuild.
                signature = current
                if args.watch:
                    command = [sys.executable, str(Path(__file__).resolve()), "--config", str(path)]
                    if args.format:
                        command.extend(["--format", args.format])
                    subprocess.run(command, check=False)
                else:
                    build(cfg)
        except (ValueError, OSError, SyntaxError, TypeError, AttributeError) as exc:
            message = f"Build failed: {exc}"
            if not args.watch:
                print(message, file=sys.stderr)
                return 1
            if signature != message:
                print(message, file=sys.stderr)
                signature = message
        if not args.watch:
            return 0
        time.sleep(0.5)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nStopped watching.")
