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

CARD_FORMAT = "poker"  # "poker", "square", or "tarot"; square is 2.5 × 2.5 inches.
CARD_FORMATS_MM = {
    "poker": (63.5, 88.9),
    "square": (63.5, 63.5),
    "tarot": (70, 120),
}
CARD_WIDTH_MM, CARD_HEIGHT_MM = CARD_FORMATS_MM[CARD_FORMAT]
# Edit the dimensions above to customize a format. All other settings are shared.
BLEED_MM = 3
SAFE_MARGIN_MM = 7
FONT_SIZE_PT = 26
# The floor for auto-shrinking. The rule cards below carry their own sizes;
# longer topic cards may also shrink to fit, especially in square format.
MIN_FONT_SIZE_PT = 8
LINE_HEIGHT = 1.08
TEXT_VERTICAL_ALIGN = "center"  # "top", "center", or "bottom"; always left aligned.
AUTO_SHRINK_TEXT = True  # Shrinks only when needed; refuses to go below the minimum.
# Share of a QR card's usable height given to the code's panel; the caption
# takes the rest. Only cards carrying a "qr" key are affected.
CARD_QR_HEIGHT_SHARE = 0.62
CARD_COLORS_CMYK = {
    # Standard device-CMYK conversions of the requested screen hex colors.
    "category_1": (0, 68.71, 45.58, 42.35),     # #932E50
    "category_2": (0, 29.06, 84.62, 8.24),      # #EAA624
    "category_3": (4.07, 0, 53.66, 51.76),      # #767B39
    "category_4": (90, 70, 0, 0),               # Original box blue.
    "rules": (0, 0, 0, 85),  # Charcoal: keeps the rule cards out of the topic draw.
}
DEFAULT_CARD_COLOR = "category_1"  # Used for plain strings and cards without a color.
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
    # Category 1: Living together (#C85555).
    {"text": "What does our ideal weekday morning look like, for both of us?",
     "color": "category_1"},
    {"text": "How do we want to spend the last twenty minutes before sleep?",
     "color": "category_1"},
    {"text": "How do we want to handle the laundry, cooking, and errands split "
             "as our lives get busier?",
     "color": "category_1"},
    {"text": "How do we want to handle differing sleep schedules or night-owl "
             "versus early-riser habits?",
     "color": "category_1"},
    {"text": "What's our rule of thumb for big versus small purchases: who "
             "decides, and at what price does it become a “we” decision?",
     "color": "category_1"},
    {"text": "How do we recover, practically, after a short-tempered moment at home?",
     "color": "category_1"},
    {"text": "How do we want to use a “day off from each other” without it "
             "turning into avoidance?",
     "color": "category_1"},
    {"text": "What's our rule for screens, gaming, or scrolling once we're both "
             "home for the evening?",
     "color": "category_1"},
    {"text": "What should we do when one of us brings home a mood the other "
             "didn’t sign up for?",
     "color": "category_1"},
    {"text": "What differences in our temperaments have quietly turned out to be "
             "good for us rather than a problem to fix?",
     "color": "category_1"},
    {"text": "A household runs on a lot of invisible work, such as noticing the "
             "empty fridge, the overdue bill, remembering the friend who needs "
             "checking on, planning the weekend. How do we want to build that "
             "noticing together, rather than leaving the invisible burden mostly "
             "in one person’s head?",
     "color": "category_1"},
    {"text": "What did money mean in the household you grew up in and how does "
             "that history quietly shape how you two talk about money now?",
     "color": "category_1"},
    {"text": "Who and how decides the priorities in the work that you need to get "
             "done together, if fixing the door creek is more important than "
             "going out or doing groceries, if cleaning the oven and not selecting "
             "the vacation destination is how we spend the afternoon?",
     "color": "category_1"},
    {"text": "Who and how decides the level of quality that needs to be reached "
             "for work you do together, be it laundry policy, how clean the fridge "
             "should be or how to select a present for common friends?",
     "color": "category_1"},
    {"text": "How do we deal with a situation in which the other does something "
             "that we do not like, especially if we are in a social setting or "
             "under time pressure?",
     "color": "category_1"},

    # Category 2: Life plans (#EAA624).
    {"text": "Children, such a scary, yet playful concept. How are we aligned on "
             "this topic, do we want children, how many, and how would we raise them?",
     "color": "category_2"},
    {"text": "How do we want our children raised in what we believe and value, "
             "practically?",
     "color": "category_2"},
    {"text": "How do we want to care for our parents as they age?",
     "color": "category_2"},
    {"text": "How do you want to make big career or life decisions together going "
             "forward? If one of us gets a call toward a specific vocation or "
             "work, how far are we willing to bend our plans to support it?",
     "color": "category_2"},
    {"text": "Where do we actually want to be living in ten years?",
     "color": "category_2"},
    {"text": "What does retirement look like for us, and do we picture it the same way?",
     "color": "category_2"},
    {"text": "How do we want to handle it if our incomes end up very unequal?",
     "color": "category_2"},
    {"text": "What’s the legacy (not financial, the actual character or values) "
             "we want to leave behind?",
     "color": "category_2"},
    {"text": "What does a “good failure” look like for us, a risk we’d respect "
             "each other for taking even if it didn’t work out?",
     "color": "category_2"},
    {"text": "How do we want to keep choosing each other on purpose, decade after "
             "decade, rather than by default?",
     "color": "category_2"},
    {"text": "If one of us can access an opportunity, cushion, or resource the "
             "other can’t, how can we use that difference in a way that feels "
             "good to both of us, rather than something either of us feels guilty "
             "or resentful about?",
     "color": "category_2"},
    {"text": "When our families’ expectations for us don’t match, which parts do "
             "we want to keep from each, which do we want to let go of, and what "
             "do we want to invent together that’s entirely ours?",
     "color": "category_2"},
    {"text": "If we believe the other one is pouring effort into a goal that we do "
             "not agree with, how do we communicate that and resolve that issue?",
     "color": "category_2"},

    # Category 3: Relationship growth—for good (#767B39).
    {"text": "Where is one of us stronger than the other, and how do we let that "
             "carry us both instead of becoming a source of resentment?",
     "color": "category_3"},
    {"text": "What does love as sacrifice actually cost each of us this season, "
             "concretely?",
     "color": "category_3"},
    {"text": "What’s a compliment or form of affection you wish I gave more often?",
     "color": "category_3"},
    {"text": "How has the other person changed you for the better this year?",
     "color": "category_3"},
    {"text": "What’s a small daily habit of ours that’s quietly good for the "
             "marriage, and that we should protect?",
     "color": "category_3"},
    {"text": "What does being fully present with each other actually require us "
             "to put down?",
     "color": "category_3"},
    {"text": "What’s something you’re proud of that you don’t think I’ve said out "
             "loud recently?",
     "color": "category_3"},
    {"text": "What does taking up something hard “together,” rather than each "
             "alone, look like for us right now?",
     "color": "category_3"},
    {"text": "What’s one thing about how you love that I should learn to receive better?",
     "color": "category_3"},
    {"text": "What’s a version of “I love you”, not the words, but an action, that "
             "actually means the most to you?",
     "color": "category_3"},
    {"text": "Love can either use people up or genuinely empower them; what makes "
             "the difference is mutuality. Describe a recent moment that felt like "
             "real, mutual, empowering love. What specifically made it feel that "
             "way, and how could we create more moments like it?",
     "color": "category_3"},
    {"text": "Real closeness doesn’t come from becoming the same person; it comes "
             "from staying different and choosing, again and again, to understand "
             "each other across that difference. What’s a difference between us "
             "that you’d rather protect and get curious about than smooth away?",
     "color": "category_3"},
    {"text": "If physical intimacy is something we’re always learning together, "
             "what’s one thing we’d want to get better at as a team?",
     "color": "category_3"},
    {"text": "What skills does each one of us want to build in order to be a "
             "better partner and how do you plan on empowering each other in this process?",
     "color": "category_3"},

    # Category 4: Relationship growth—for worse (original box blue).
    {"text": "How do we actually want to apologize to each other? What makes an "
             "apology land instead of just ending the argument?",
     "color": "category_4"},
    {"text": "What does patience actually look like for us, in practice, on a bad day?",
     "color": "category_4"},
    {"text": "What’s a grudge either of us might still be quietly carrying, and "
             "what would it take to actually let it go?",
     "color": "category_4"},
    {"text": "What’s something I do that you’ve never told me actually hurts?",
     "color": "category_4"},
    {"text": "How do we want to handle it when we’re both right and both hurt?",
     "color": "category_4"},
    {"text": "How do we make sure the sun doesn’t go down on an unresolved fight?",
     "color": "category_4"},
    {"text": "How do we want to handle criticism from each other without it "
             "turning into defense?",
     "color": "category_4"},
    {"text": "How do we want to handle it when one of us needs comfort and the "
             "other jumps straight to fixing the problem?",
     "color": "category_4"},
    {"text": "If the exact situation that caused our worst fight happened again "
             "tomorrow, what would each of us actually do differently now?",
     "color": "category_4"},
    {"text": "Think about our last real disagreement. What helped us find the "
             "words for what was actually wrong? How could we practice that "
             "together next time, on purpose?",
     "color": "category_4"},
    {"text": "Philosopher Ellie Anderson calls the work of figuring out what "
             "you’re feeling, and helping your partner do the same, hermeneutic "
             "labor. Where does that kind of work already flow easily between us? "
             "Where would you like to build more of it, on purpose, together?",
     "color": "category_4"},
    {"text": "What often gets called someone’s “intuition” in a relationship is "
             "really years of unacknowledged interpretive work, such as noticing, "
             "translating, and making sense. Is there a kind of understanding one "
             "of us seems to have “naturally”? What would it look like to treat "
             "that as a skill we’re both building, rather than a trait only one "
             "of us has?",
     "color": "category_4"},
    {"text": "Describe a moment that felt more one-sided or draining than "
             "empowering. Without assigning blame, what would need to shift in "
             "either of us, or in how we relate, for a moment like that to feel "
             "mutual instead?",
     "color": "category_4"},
    {"text": "What’s one script about how love or partnership is “supposed” to "
             "work, something you inherited rather than chose, that you’ve had to "
             "unlearn together?",
     "color": "category_4"},
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
BOX_BACKGROUND_CMYK = (0, 43.65, 31.75, 1.18)  # #FC8EAC; independent of card colors.
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
