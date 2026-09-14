# Marriage XP - logo version 3

Redrawn from `logo3sketch.jpeg` as a **capital P over an X**. The P is a complete letter with a continuous stem and a D-shaped bowl and counter. It tilts clockwise, and its stem also forms one diagonal of the X. An outlined diagonal crosses behind it. All artwork is vector; no reference image is embedded.

## Files

- `marriage-xp-v3-black.svg`: black vector artwork, transparent openings and background.
- `marriage-xp-v3-blue.svg`: blue display-color version.
- `marriage-xp-v3-white.svg`: white artwork for use over a colored background.
- `marriage-xp-v3-cmyk.pdf`: the standalone logo in process black.
- `logo-v3-study.pdf`: the mark and its game-name pairing, a comparison with the other versions, and a construction page separating the P and X components.
- `logo-v3-preview.png`: screen preview of the revised version; use SVG or PDF for production.

## How it is put together

The P and X are combined into one filled silhouette with three true transparent openings. The P is constructed upright, with a rounded D-shaped counter and circular right-hand bowl, then rotated as one shape. This keeps the bowl attached to the stem and preserves the reading of the letter. The stem and bowl share a 56-unit weight; the X outline is 14 units. The angles are mirrored at 32 degrees from vertical.

**All four arms measure 200 design units from the crossing along their centre lines.** A shared `V3_ARM_LENGTH` controls the two upper arms and both lower arms. Circular fillets round the tips, the P's shoulder and counter, and both X slots. The four inward corners at the X's crossing stay sharp. Short edges locally limit the fillet radius so curves cannot overlap.

## Select and edit

In the project's `game_config.py`, set `LOGO_VERSION = 3`, then run the generator as usual. This works for either card format.

The `V3_*` variables in `logo.py` control the geometry.

- `V3_THICKNESS`: P stem and bowl weight, also the full outlined-diagonal width.
- `V3_OUTLINE`: outlined-diagonal wall width.
- `V3_TILT`: rotation of the P and the mirrored angle of the other diagonal.
- `V3_CROSSING`: location of the intersection.
- `V3_ARM_LENGTH`: shared centre-to-tip length for all four arms. The upper-arm, lower-arm and upper-stem values are derived from it.
- `V3_CORNER_RADIUS`: rounding at the P corners and arm ends. X tip and slot radii account for the outline width; its four crossing corners remain sharp.
- `V3_BOWL_RADIUS`: outside radius of the bowl; inner radius is derived by subtracting the shared stroke weight.
- `V3_BOWL_STRAIGHT`: straight portion from the left edge of the P to the curved bowl.

Bounds are derived from the actual cubic-curve extrema. PDF placement centers version 3 on `V3_CROSSING`, the center of the X, with symmetric fitting space that accommodates the P bowl without clipping. On card backs the crossing aligns with the center of the card. On box fronts it aligns horizontally with the panel center and vertically with the midpoint between the top of the title and the top edge of the panel. Versions 1, 1b, and 2 retain their own geometry and alignment.

`make_logo_v3.py` regenerates the vector exports and the study PDF when run with the same dependency-equipped Python environment used by the card generator.
