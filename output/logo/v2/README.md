# Marriage XP - logo version 2

Drawn from the second sketch, `logo2.jpeg`. The pale areas are interpreted as openings: a crescent along the right side of the loop and a hollow, upright stem. The left arms and loop align at the top and bottom. Circular bands and a parallelogram define the geometry. All artwork is vector; no reference image is embedded.

## Files

- `marriage-xp-v2-black.svg`: black vector artwork, transparent openings and background.
- `marriage-xp-v2-blue.svg`: blue display-color version.
- `marriage-xp-v2-white.svg`: white artwork for use over a colored background.
- `marriage-xp-v2-cmyk.pdf`: the standalone logo in process black.
- `logo-v2-study.pdf`: the new mark and its game-name pairing, followed by a comparison with version 1.
- `logo-v2-preview.png`: screen preview; use the SVG or PDF for print and editing.

The SVG uses filled paths with true holes, not white shapes covering black ones. The PDF uses the same path geometry, with process CMYK colors.

## Select and edit

In the project's `game_config.py`, `LOGO_VERSION = 2` is the current default, so the generator draws this mark on the box as usual. This works for either card format. `LOGO_VERSION = 1` restores the original.

The `V2_*` variables in `logo.py` control the geometry. `V2_OUTLINE` is the shared width for the inner right-hand ring, the outer ring, the stem outline, and the openings between them: the crescent gap and the stem's hollow. It is one third of `V2_THICKNESS`, the arm weight (14.667 design units). The bowl's annular zone, from the circular opening out to the silhouette, is exactly one arm weight, so that third divides it into ring, gap and ring edge to edge, and divides the stem into outline, hollow and outline. The circular opening sits flush with the arm's inner edge, keeping it one clean circle across the solid left half of the bowl and the open right half. The outside silhouette is unchanged. Stem side spacing compensates for its lean to retain that same perpendicular thickness. `make_logo_v2.py` regenerates the vector exports and comparison PDF when run with the same dependency-equipped Python environment used by the card generator.
