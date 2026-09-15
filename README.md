# Marriage XP

A small Python generator for solid-color, borderless cards and a matching reverse-tuck box. All artwork is vector; the supplied Fredoka font is embedded. The defaults are 63.5 × 88.9 mm poker cards, 3 mm bleed, four category backgrounds, charcoal instruction cards, and white left-aligned text. A large mathematical logo fills most of the independently colored box front, with the game name centered at the bottom and no subtitle.

## Quick start

On this Mac, double-click **Generate PDFs.command**, or run `python3 generate.py` / `python3 generate.py --watch`. If your current Python lacks the PDF dependencies, the script automatically checks the project's `.venv` and then the bundled Codex Python runtime. It reuses an environment with both dependencies installed and preserves your command-line options.

Edit **game_config.py**, save, then run the launcher again. The default deck has 9 instruction/QR cards followed by 56 categorized question cards. Generated files live in **output/pdf/**.

**Switch fonts in one line:** set `FONT_NAME` to any option below. All fonts are bundled; no font installation is needed. `fredoka` remains an alias for `fredoka-bold`.

| `FONT_NAME` | Font weight |
| --- | --- |
| `fredoka-light` | Fredoka Light (300) |
| `fredoka-regular` | Fredoka Regular (400) |
| `fredoka-medium` | Fredoka Medium (500) |
| `fredoka-semibold` | Fredoka SemiBold (600) |
| `fredoka-bold` | Fredoka Bold (700), current default |
| `manrope` | Manrope Bold, previous design |
| `outfit` | Outfit Bold, original design |

For any other machine with Python 3.10 or newer:

```sh
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 generate.py
```

On Windows, activate with `.venv\Scripts\activate` instead. After setup, the generator works offline.

To regenerate whenever you save the settings, font, or logo:

```sh
python3 generate.py --watch
```

The launcher also accepts `--watch` from a terminal. Stop watching with Ctrl+C. A failed configuration keeps the last successful PDFs intact. Watch mode reports the failure and resumes when you fix the file.

## What to edit

**Square mode:** run `python3 generate.py --format square` for 2.5 × 2.5 inch (63.5 × 63.5 mm) cards and a matching box. Its eight PDFs go in `output/pdf/square/`, so you can compare them with the existing poker version. Add `--watch` to keep that version up to date:

```sh
python3 generate.py --format square --watch
```

Use `--format poker` to generate a poker comparison in `output/pdf/poker/`. Alternatively, change `CARD_FORMAT = "square"` in `game_config.py` to make square the normal mode for the launcher and plain `python3 generate.py`; without a command-line override, files go directly into `OUTPUT_DIR`. Set it back to `"poker"` to restore the previous size. Formats share phrases, fonts, colors, and margins. Text may shrink to fit, respecting `MIN_FONT_SIZE_PT`, and the box resizes automatically. Square pages with the default 3 mm bleed measure 69.5 × 69.5 mm; no-bleed pages measure exactly 63.5 × 63.5 mm.

**Tarot mode:** run `python3 generate.py --format tarot` for 70 × 120 mm cards, the standard tarot trim size used by most print shops, and a matching box. Its eight PDFs go in `output/pdf/tarot/`. Add `--watch` to keep that version up to date:

```sh
python3 generate.py --format tarot --watch
```

Or set `CARD_FORMAT = "tarot"` in `game_config.py` to make it the normal mode. Tarot pages with the default 3 mm bleed measure 76 × 126 mm; no-bleed pages measure exactly 70 × 120 mm. The extra height and width give text more room than poker or square, so fewer (if any) cards need auto-shrinking.

| Setting | Meaning |
| --- | --- |
| `CARDS` | Phrases in page order; strings or dictionaries with per-card overrides |
| `CARD_FORMAT` | `poker` or `square` for normal runs |
| `CARD_FORMATS_MM` | Editable width/height pairs in mm; the selected pair sets `CARD_WIDTH_MM` and `CARD_HEIGHT_MM` |
| `FONT_NAME` | Any font selector from the table above |
| `FONT_PATH` | An embeddable TrueType font; `.ttc` collections also use `FONT_COLLECTION_INDEX` |
| `FONT_SIZE_PT`, `MIN_FONT_SIZE_PT` | Preferred size and lower limit for automatic shrinking |
| `SAFE_MARGIN_MM`, `LINE_HEIGHT` | Inner text spacing and line spacing multiplier |
| `TEXT_VERTICAL_ALIGN` | `top`, `center`, or `bottom`; horizontal alignment stays left |
| `CARD_COLORS_CMYK` | Named colors for categories 1–4 and instruction cards; add or edit any CMYK tuple |
| `DEFAULT_CARD_COLOR` | Color name used by plain strings or cards without a `color` field |
| `TEXT_CMYK` | Default card text color; four ink percentages, each from 0 through 100 |
| `CARD_BACK_LOGO_CMYK` | Independent logo color for card backs; white by default |
| `CARD_BACK_LOGO_SCALE` | Maximum fraction of card width and height occupied by the centered logo (0 to 1, excluding 0); also respects the safe margin |
| `BOX_BACKGROUND_CMYK`, `BOX_TEXT_CMYK` | Independent box background and text/logo colors |
| `USE_VECTOR_LOGO` | `True` by default; draws the large mathematical logo above the bottom game name |
| `CARD_QR_HEIGHT_SHARE` | Share of a QR card's usable height given to the code panel; the caption takes the rest |
| `LOGO_VERSION` | `1` for the original solid mark; `"1b"` for version 1 with all four arm radii matched; `2` for the raised loop with a crescent and hollow stem; `3` for a solid capital P over an outlined X |
| `CARD_THICKNESS_MM` | Measured thickness of one finished card, including any coating |
| `BOX_BOARD_THICKNESS_MM` | Thickness of the box material |
| `BOX_*_CLEARANCE_MM` | Total additional room in each dimension |
| `BOX_INTERNAL_DEPTH_MM` | Optional explicit internal depth; otherwise calculated |
| `GAME_NAME`, `BOX_BACK_TEXT` | Bottom name on the front and description on the back |
| `ICC_PROFILE_PATH` | Optional CMYK ICC profile from your printer |

For example:

```python
CARDS = [
    {"text": "What does our ideal morning look like?", "color": "category_1"},
    {"text": "Where do we want to live?", "color": "category_2", "copies": 2,
     "font_size_pt": 25},
    {"text": "Make your own cards.", "color": "rules",
     "qr": "https://github.com/olaruandreidan/XPCardGame"},
]
BOX_BACKGROUND_CMYK = (85, 10, 75, 10)  # Green box, independent of card colors.
```

This produces four card pages and sizes the box for four cards. A `background_cmyk` tuple on an individual card overrides its named palette color. Changing the card palette never changes the box colors. Every card has exactly one solid background and one phrase. There are no printed borders, numbers, or trim marks on cards. Text wraps at spaces, preserves explicit newlines, and may shrink in quarter-point increments. A word that is too wide or text that cannot fit at the minimum size stops the build with a useful error. Missing font characters and unknown color names also stop the build.

### QR cards

A `qr` URL turns a card into a QR card. The code is generated from the URL and drawn as vector paths, like the logo; no image is embedded and no extra dependency is needed. It sits on a rounded panel in the card's text color with the modules in the card's background color, so the code is the card inverted rather than a foreign white block, and a scanner still gets the light field and four-module quiet zone it needs. The caption goes underneath and is sized by the usual auto-fit rules. `CARD_QR_HEIGHT_SHARE` sets how much of the card's usable height the panel takes, with the caption getting the rest; at the default `0.62` a poker card gives 1.13 mm modules and a square card 0.75 mm, both comfortably above what a phone camera needs. A long URL is one unbreakable word, so put line breaks in the caption yourself if you want the address printed as well.

## Files generated

| File | Use |
| --- | --- |
| `game.pdf` | Requested combined document: each card on a page, followed by the unfolded box with visible cut/fold guides |
| `cards.pdf` | Production card faces, one per page, with bleed and explicit TrimBox/BleedBox |
| `cards-no-bleed.pdf` | Exact finished-size card pages without bleed or cut marks, for the printer to arrange on a larger sheet |
| `card-backs.pdf` | One back per palette color, plus additional custom card backgrounds; centered vector logo, with bleed |
| `card-backs-no-bleed.pdf` | Same back pages at exact finished size, without bleed or cut marks |
| `box-artwork.pdf` | Clean box artwork, without manufacturing lines |
| `box-dieline.pdf` | Matching vector cut and score paths on a separate page |
| `box-proof.pdf` | Box artwork plus visible manufacturing guides for assembly and review |
| `build-report.json` | Card count, actual font sizes, dimensions, and production notes |

The three box PDFs share identical page size and coordinates. The combined PDF intentionally has mixed page sizes. Box TrimBox is the **bounding rectangle of the net**; the dieline defines the actual irregular cut shape. Color extends beyond every cut edge, including into discarded areas. The central glue area is unprinted.

## Printing and assembly

Print at **100% / actual size**, with any “fit to page” option disabled. The sample card page measures 69.5 × 94.9 mm including bleed, with a 63.5 × 88.9 mm TrimBox. The sample box page is approximately 183.6 × 155.6 mm.

For a shop arranging many cards on one large sheet, use **cards-no-bleed.pdf**. Each page is exactly the configured finished card size (63.5 × 88.9 mm at the default settings), with the background extending to every edge and no bleed area, borders, or cut marks. Text size and position relative to the finished card are identical to `cards.pdf`. Page MediaBox, TrimBox, and BleedBox all match the finished size. This file is generated automatically on every run, including watch mode; it remains one card per page so the shop can choose its own sheet size and arrangement. The shop can group same-color cards and extend their matching CMYK background across the sheet. Individual card colors remain intact. Use the color values in `game_config.py` or `build-report.json` for matching the sheet background.

Artwork uses explicit process CMYK. The dieline uses named spot colors: **CutContour** (solid magenta preview) and **Crease** (dashed cyan preview), with stroke overprint. These are manufacturing guides and must not become printed decoration. Send the printer `cards.pdf`, `box-artwork.pdf`, and `box-dieline.pdf`; confirm their required spot names, score convention, bleed, and color profile. `game.pdf` and `box-proof.pdf` visibly include the guides.

These files are **not certified PDF/X**. An optional ICC profile declares an output intent but does not convert the ink percentages or perform PDF/X validation. CMYK appearance on a display is approximate; use your printer's proof to judge final color. No printer profile is assumed or bundled.

Box sizing starts with:

```text
inside width  = card width  + width clearance
inside height = card height + height clearance
inside depth  = max(card count × card thickness + depth clearance, minimum depth)
score-to-score panel dimensions = inside dimensions + one box-board thickness
```

The default 65-card deck uses its calculated stack depth. Smaller decks use a minimum 12 mm inside depth. For sleeved cards, use their outside dimensions and measured stack thickness. The net is intended for folding carton stock, not thick rigid board. Extreme dimensions that make the box wider in depth than its face are rejected.

Make a physical prototype with your actual stock before ordering a print run. This is a parametric prototype dieline; commercial tooling may need adjusted score allowances and closure geometry.

1. Cut all solid magenta paths, including the slits between flaps.
2. Score and pre-fold the dashed cyan paths. Keep the artwork outside.
3. Form the four panels into a tube. Glue the unprinted tab underneath the far-right side panel's free edge and let it set.
4. At the bottom, fold the two small side flaps inward. Fold the large closure across the opening, bend its tongue at the second score, and tuck it inside the opposite wall.
5. Insert the cards and close the top the same way. Its closure attaches to the opposite broad panel.

Card backs are generated on every run, including watch mode and both card formats. Their backgrounds use exactly the same CMYK values as the fronts. Each has only the selected `LOGO_VERSION`, with proportions preserved. Version 3 centers the X's crossing on the card; on the box it centers horizontally on the front panel and vertically in the space between the title and the top edge; other versions center by their visible bounds. Scaling accounts for the P bowl's extra reach so it stays inside the available space, clear of the box name. `CARD_BACK_LOGO_SCALE` controls its size and `CARD_BACK_LOGO_CMYK` its ink, independently of the box. Backs always display the logo; `USE_VECTOR_LOGO` controls the box only.

Back pages follow `CARD_COLORS_CMYK` order, including unused palette entries. Additional distinct `background_cmyk` overrides follow in first-use order. The `card_backs` list in `build-report.json` gives each back's one-based page number, ink values, and matching front page numbers, including copies. Back designs do not increase the deck count or box depth. Give the printer `card-backs.pdf` with `cards.pdf`, or both no-bleed files. The printer repeats each back for its matching fronts and handles sheet arrangement and duplex orientation. `game.pdf` remains the fronts followed by the box proof; no sheet imposition or rounded-corner tooling is generated.

## Logo study

`logo.py` now contains a parametric vector monogram derived from your sketch. `output/logo/` contains SVG exports and a three-page study with a recommended open-source Manrope font pairing. Run `python3 make_logo_proof.py` to regenerate it. See `output/logo/README.md` for the geometry settings and font details.

The second sketch is available as **version 2** in `output/logo/v2/`, including SVGs and a comparison PDF. It is the current default: `LOGO_VERSION = 2` in `game_config.py` uses it in the normal generator (both poker and square modes). Set it back to `1` for the original. Version 2 raises the circular loop to the arm height, opens a transparent crescent along its right side, and uses an outlined, upright descending stem. One width, a third of the arm weight, governs both rings, the stem outline, and the openings between them. Both versions are mathematical filled paths; the openings reveal the configured background color.

`USE_VECTOR_LOGO = True` is enabled in `game_config.py`. Each normal generator run fits the logo as large as possible above the game name, preserving its proportions. The name stays centered at the bottom; there is no front subtitle. Set the option to `False` to show the bottom name alone. The generator supplies a saved canvas state and the configured box text color. The SVGs use filled vector paths; PDF drawing uses the same mathematical geometry. The cards retain their simple phrase-only design. The separate logo study PDF records the earlier Manrope comparison.

## Verification and sources

Run `python3 -m unittest discover -s tests -v` after changing generator behavior. Tests check card dimensions and counts, font embedding, color operators, cut-contour closure, spot names, alternate dimensions, overflow, and retention of previous outputs on failure.

- [Fredoka font](https://github.com/google/fonts/tree/main/ofl/fredoka), with its license in `assets/fonts/fredoka/OFL.txt`.
- [Manrope open-source font edition](https://github.com/google/fonts/tree/main/ofl/manrope), with its license in `assets/fonts/manrope/OFL.txt`.
- [Outfit alternative font](https://github.com/Outfitio/Outfit-Fonts), with its license in `assets/fonts/OFL.txt`.
- [ReportLab graphics and CMYK documentation](https://docs.reportlab.com/reportlab/userguide/ch2_graphics/).

Only ReportLab and pypdf are needed to generate PDFs. Poppler is optional for rendering previews during development.
