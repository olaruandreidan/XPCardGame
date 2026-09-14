# Marriage XP - logo version 1b

A fork of version 1. In version 1 the four arms of the X came from three circles of two different sizes: one radius-128 circle supplied both left arms, a second supplied the upper right arm, and the P bowl, at radius 68, supplied the lower right one. Version 1b gives all four arms a single radius, the P circle's, and runs a straight section down the middle to give back the height the smaller arcs would otherwise lose. Every arc still meets the stem where its tangent is vertical, which is exactly where a band is one `THICKNESS` wide, so the joins stay flush. All artwork is vector; no reference image is embedded.

## Files

- `marriage-xp-v1b-black.svg`: black vector artwork, transparent openings and background.
- `marriage-xp-v1b-blue.svg`: blue display-color version.
- `marriage-xp-v1b-white.svg`: white artwork for use over a colored background.
- `marriage-xp-v1b-cmyk.pdf`: the standalone logo in process black.
- `logo-v1b-study.pdf`: the mark and its game-name pairing, a comparison with versions 1 and 2, and a sweep study.

## Select and edit

In the project's `game_config.py`, set `LOGO_VERSION = "1b"`, then run the generator as usual. This works for either card format. `1` restores the original and `2` selects the raised loop.

The `V1B_*` variables in `logo.py` control the geometry.

- `V1B_RADIUS` is the shared radius of all four arm circles, the bowl included. It is `78`, which puts the mark close to version 1's width.
- `V1B_ARC_EXTRA` is how many degrees each of the three open arcs carries on past the vertical end cap a plain quarter turn would give it. It is `25`. Zero gives bare quarter circles, which read short; the extra sweep lengthens the three arms and tilts their cut ends. The closed bowl is unaffected.
- `V1B_OVERLAP` is how far the stem runs up underneath the arms. The arms' closing edge is a horizontal line exactly the stem's width, so butting the two would leave a composited hairline where they meet; running the stem up past the junction puts that edge inside the fill instead. Above the junction the arms flare wider than the stem, so the overlap never shows.
- `V1B_TOP`, `V1B_X_HEIGHT`, `V1B_AXIS` and `V1B_STEM_BOTTOM` place the mark. `V1B_TOP_JOIN` and `V1B_MIDDLE` are derived from them, so changing the radius keeps the top edge and the height of the X where they are and only the width moves.

The mark is `3 * V1B_RADIUS + THICKNESS / 2` wide before the extra sweep, and wider by `(V1B_RADIUS + THICKNESS / 2) * sin(V1B_ARC_EXTRA)` after it. Page three of the study PDF shows four sweeps side by side.

`make_logo_v1b.py` regenerates the vector exports and the study PDF when run with the same dependency-equipped Python environment used by the card generator.
