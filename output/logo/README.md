# Marriage XP - logo study 01

This first vector direction follows the supplied hand-drawn reference: two curved upper arms, a curved lower-left arm, a descending common stem, and a circular right-hand loop. The sketch is a reference only; no photograph is embedded or traced.

## Deliverables

- `marriage-xp-black.svg`: editable filled vector paths, transparent background.
- `marriage-xp-blue.svg`: the same geometry in a display approximation of the game's cobalt blue.
- `marriage-xp-white.svg`: white geometry on a transparent background.
- `marriage-xp-mark-cmyk.pdf`: vector mark in process black, 100 × 140 mm page.
- `logo-study.pdf`: three pages showing the mark, a name pairing, construction, small-size checks, and Manrope/Outfit comparisons.
- `logo-preview.png`: screen preview of the first study page. Use the SVG/PDF for vector artwork.

SVG colors are for display. The PDFs use process CMYK. The stand-alone logo has no full-bleed page background, so it requires no print bleed. The study is for design review, not a box dieline.

## Construction and iteration

The master is `../../logo.py`. The main variables are `ARM_RADIUS`, `BOWL_RADIUS`, `THICKNESS`, `BOWL_CENTER_Y`, and `STEM_BOTTOM`. Two 128-unit arm radii meet the same stem. The loop has a 68-unit radius. The bands and stem are 44 units thick. Curves use cubic Bezier approximations of circles. All elements are filled paths, without live strokes, images, or font dependencies.

Run `python3 make_logo_proof.py` from the project directory using the same Python environment as the card generator. This regenerates all SVGs and both PDFs. To refresh the optional PNG preview, run `pdftoppm -f 1 -singlefile -scale-to 1600 -png output/logo/logo-study.pdf output/logo/logo-preview`.

The logo is integrated into the normal generator: `USE_VECTOR_LOGO = True` in `game_config.py` draws it large above the bottom game name on the box, without a subtitle. The current deck uses Fredoka Bold; set `FONT_NAME = "manrope"` to restore the previous font. Regenerate the game with `python3 generate.py`; no separate logo export step is needed. The study PDF remains the original design comparison.

## Recommended font

The historical study compares **Manrope ExtraBold (800)** for the game name and **Manrope Bold (700)** for questions with the more playful Outfit Bold alternative. The normal game generator now uses the user-selected Fredoka Bold for all text.

The bundled files come specifically from the **open-source Google Fonts edition of Manrope**, not a newer commercial edition. Its SIL Open Font License is included in `../../assets/fonts/manrope/OFL.txt`.

- Source: https://github.com/google/fonts/tree/main/ofl/manrope
- License: https://github.com/google/fonts/blob/main/ofl/manrope/OFL.txt
- Bundled original: `../../assets/fonts/manrope/Manrope-Variable.ttf`
- Static instances: `Manrope-Bold.ttf` and `Manrope-ExtraBold.ttf` in that same folder.

The static fonts were produced from the variable font at weights 700 and 800 with FontTools. They are embedded in the study PDF. No additional font installation or internet access is needed to regenerate the proof.

The `FONT_NAME` selector in `game_config.py` switches between the bundled Fredoka, Manrope, and Outfit fonts.
