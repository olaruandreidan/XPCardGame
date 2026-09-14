"""Edit this file, then run: python3 generate.py

Dimensions are millimetres; font sizes are points. CMYK channels are 0..100.
The first card is your phrase. The remaining cards and box copy are samples.
"""

GAME_NAME = "The marriage level-up game"
FONT_NAME = "fredoka-medium"  # Choose any key below; "manrope" restores the previous font.
FONT_FILES = {
    "fredoka": "assets/fonts/fredoka/Fredoka-Bold.ttf",  # Alias for fredoka-bold.
    "fredoka-light": "assets/fonts/fredoka/Fredoka-Light.ttf",  # 300
    "fredoka-regular": "assets/fonts/fredoka/Fredoka-Regular.ttf",  # 400
    "fredoka-medium": "assets/fonts/fredoka/Fredoka-Medium.ttf",  # 500
    "fredoka-semibold": "assets/fonts/fredoka/Fredoka-SemiBold.ttf",  # 600
    "fredoka-bold": "assets/fonts/fredoka/Fredoka-Bold.ttf",  # 700
    "manrope": "assets/fonts/manrope/Manrope-Bold.ttf",
    "outfit": "assets/fonts/Outfit-Bold.ttf",
}
FONT_PATH = FONT_FILES[FONT_NAME]  # Or replace this with a custom font path.
FONT_COLLECTION_INDEX = 0  # Only needed for a .ttc font collection.
USE_VECTOR_LOGO = True  # Automatically draws the mathematical logo on the box.
LOGO_VERSION = 3  # 1 = original solid mark; "1b" = version 1 with matched arm radii;
                  # 2 = outlined loop/stem from the second sketch;
                  # 3 = straight crossed-bar X from the third sketch.

CARD_FORMAT = "poker"  # "poker" or "square"; square is 2.5 × 2.5 inches.
CARD_FORMATS_MM = {
    "poker": (63.5, 88.9),
    "square": (63.5, 63.5),
}
CARD_WIDTH_MM, CARD_HEIGHT_MM = CARD_FORMATS_MM[CARD_FORMAT]
# Edit the dimensions above to customize a format. All other settings are shared.
BLEED_MM = 3
SAFE_MARGIN_MM = 7
FONT_SIZE_PT = 26
# The floor for auto-shrinking. The rule cards below carry their own sizes,
# so this only has to stay low enough for them to reflow into the smaller
# square format; the topic cards never come near it.
MIN_FONT_SIZE_PT = 8
LINE_HEIGHT = 1.08
TEXT_VERTICAL_ALIGN = "center"  # "top", "center", or "bottom"; always left aligned.
AUTO_SHRINK_TEXT = True  # Shrinks only when needed; refuses to go below the minimum.
# Share of a QR card's usable height given to the code's panel; the caption
# takes the rest. Only cards carrying a "qr" key are affected.
CARD_QR_HEIGHT_SHARE = 0.62
CARD_COLORS_CMYK = {
    "red": (0, 90, 75, 0),
    "green": (85, 10, 75, 10),
    "blue": (90, 70, 0, 0),
    "purple": (55, 85, 0, 0),
    "rules": (0, 0, 0, 85),  # Charcoal: keeps the rule cards out of the topic draw.
}
DEFAULT_CARD_COLOR = "blue"  # Used for plain strings and cards without a color.
TEXT_CMYK = (0, 0, 0, 0)  # White paper / no ink.
CARD_BACK_LOGO_CMYK = (0, 0, 0, 0)  # Independent logo ink on every card back.
CARD_BACK_LOGO_SCALE = 0.7  # Fit within 70% of width/height, respecting SAFE_MARGIN_MM.
# Backs use LOGO_VERSION, centered, with one page per palette color (plus custom inks).

# A plain string creates one card. A dict allows per-card overrides.
# {"text": "Your phrase", "color": "red", "copies": 2,
#  "text_cmyk": (0, 0, 0, 0), "font_size_pt": 25}
# A "qr" URL turns the card into a QR card: the code is drawn as vector paths
# on a panel in the card's text color, with the caption below it.
# A "background_cmyk" tuple overrides the named color for a single card.
# Color choices below are examples, not assigned gameplay categories.
# Use \n for intentional line breaks. Copies also increase the box capacity.
CARDS = [
    # Instruction cards, from "The Marriage level up game.txt". Each carries an
    # explicit font_size_pt, chosen as the largest that fits the poker card with
    # a little room to spare. Edit the text and the size may need revisiting.
    {"text": "For Xhenis and Petru, "
             "because how they XPerience love and life with fierce beauty and "
             "tender strength inspires us all",
     "color": "rules", "font_size_pt": 18},
    {"text": "Life often hits us hard. Routine and stress and steady erosion "
             "shrink us. Love is growth as counterweight to life's evil, but how "
             "to feed it? This game is one for couples that are not too weary of "
             "a bit of playful work and wish to level up their marriage game.",
     "color": "rules", "font_size_pt": 14},
    {"text": "Rule 1\n\n"
             "Level up your marriage by talking about the topics on the cards "
             "and reaching a common answer. That's it, that is the game!",
     "color": "rules", "font_size_pt": 17},
    {"text": "Rule 2\n\n"
             "When talking about a topic, you only level-up when you reach an "
             "answer you are both happy with, and one that you both believe is "
             "useful to have articulated. You do not level up if you reach two "
             "different answers.",
     "color": "rules", "font_size_pt": 14},
    {"text": "Rule 3\n\n"
             "Every time you get to have a meaningful conversation about your "
             "relationship, congratulate yourselves. Take the card and stick it "
             "with some magnet to your fridge, as an achievement.",
     "color": "rules", "font_size_pt": 14},
    {"text": "Rule 4\n\n"
             "If you are struggling to pick topics, do it like this. Each pick a "
             "color (or the same color). Then draw 3 face-down cards each only "
             "from picked colors. Rock-paper-scissors to decide who goes first. "
             "Then the first one picks a topic from their drawn topics.",
     "color": "rules", "font_size_pt": 12.5},
    {"text": "Rule 5\n\n"
             "You only level up if you do it constantly. Every month with no new "
             "talk resets your progress. We advice you set for yourself a "
             "recurring date, like the first and third Wed of every month.",
     "color": "rules", "font_size_pt": 14.5},
    {"text": "Rule 6\n\n"
             "The cards are kinda cool and you can also use them some other way. "
             "Actually, on one of the cards you will find a QR code to a lil "
             "piece of software that lets you create more cards that you can "
             "then print by following the instructions found at the same link.",
     "color": "rules", "font_size_pt": 13},
    # Rule 6 points at this one.
    {"text": "Make your own cards.\n\n"
             "github.com/\n"
             "olaruandreidan/XPCardGame",
     "qr": "https://github.com/olaruandreidan/XPCardGame",
     "color": "rules", "font_size_pt": 11},
    # Topic cards.
    {"text": "How will we govern our finances?", "color": "blue"},
    {"text": "What makes you feel at home?", "color": "red"},
    {"text": "How do we want to spend our Sundays?", "color": "green"},
    {"text": "What does support look like to you?", "color": "purple"},
    {"text": "Which traditions will we make our own?", "color": "blue"},
    {"text": "How will we share the invisible work?", "color": "red"},
    {"text": "What helps you feel heard?", "color": "green"},
    {"text": "What are we saving for?", "color": "purple"},
    {"text": "How do we make room for ourselves?", "color": "blue"},
    {"text": "What adventure should we plan next?", "color": "red"},
    {"text": "How will we repair after an argument?", "color": "green"},
    {"text": "What do we want to keep choosing?", "color": "purple"},
]

# Measure a stack of your actual stock and divide by the number of cards.
CARD_THICKNESS_MM = 0.32
BOX_BOARD_THICKNESS_MM = 0.4
BOX_WIDTH_CLEARANCE_MM = 1.5  # Total clearance, not per side.
BOX_HEIGHT_CLEARANCE_MM = 1.5
BOX_DEPTH_CLEARANCE_MM = 2
BOX_MIN_INTERNAL_DEPTH_MM = 12  # Makes a very small sample deck's box practical.
BOX_INTERNAL_DEPTH_MM = None  # Optional override; rejected if too small for the deck.
BOX_GLUE_TAB_MM = 12
BOX_TUCK_TAB_MM = 12
BOX_MARGIN_MM = 8
BOX_BACKGROUND_CMYK = (90, 70, 0, 0)  # Independent of every card color.
BOX_TEXT_CMYK = (0, 0, 0, 0)  # Independent box text and logo color.
BOX_FRONT_FONT_SIZE_PT = 30
BOX_BACK_FONT_SIZE_PT = 12
BOX_BACK_TEXT = (
    "For Xhenis and Petru\n\n"
    "With love,\n"
    "Maria and Andrei"
)

# Optional CMYK ICC profile supplied by your printer. This embeds an output
# intent; it does not convert ink values or claim PDF/X certification.
ICC_PROFILE_PATH = None
ICC_OUTPUT_CONDITION = "Printer-supplied CMYK profile"
OUTPUT_DIR = "output/pdf"
