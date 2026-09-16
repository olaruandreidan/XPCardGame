import contextlib
import io
import json
import re
from pathlib import Path
import tempfile
import unittest

from pypdf import PdfReader
from pypdf.generic import ContentStream
from reportlab.lib.units import mm

import generate as app


class GeneratorTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.cfg = app.load_config(app.ROOT / "game_config.py")
        self.cfg.OUTPUT_DIR = self.tmp.name

    def build(self):
        with contextlib.redirect_stdout(io.StringIO()):
            return app.build(self.cfg)

    def test_pdf_dimensions_color_fonts_and_combined_pages(self):
        out = self.build()
        cards = PdfReader(out / "cards.pdf")
        self.assertEqual(len(cards.pages), len(self.cfg.CARDS))
        for page in cards.pages:
            self.assertAlmostEqual(float(page.trimbox.width) / mm, 63.5, places=4)
            self.assertAlmostEqual(float(page.trimbox.height) / mm, 88.9, places=4)
            self.assertAlmostEqual(float(page.mediabox.width) / mm, 69.5, places=4)
            self.assertAlmostEqual(float(page.bleedbox.height) / mm, 94.9, places=4)
            ops = {op for _, op in ContentStream(page.get_contents(), cards).operations}
            self.assertIn(b"k", ops)
            self.assertFalse(ops & {b"rg", b"RG", b"g", b"G"})
            fonts = page["/Resources"]["/Font"].get_object()
            self.assertTrue(fonts)
            for ref in fonts.values():
                font = ref.get_object()
                desc = font.get("/FontDescriptor")
                self.assertIsNotNone(desc)
                self.assertIn("/FontFile2", desc.get_object())
        # Collapse whitespace on both sides: a card may carry intentional \n
        # line breaks, which extraction reports as ordinary spacing.
        first = " ".join(cards.pages[0].extract_text().split())
        self.assertEqual(first, " ".join(self.cfg.CARDS[0]["text"].split()))
        combined = PdfReader(out / "game.pdf")
        self.assertEqual(len(combined.pages), len(cards.pages)+1)
        self.assertEqual(combined.pages[-1].mediabox, PdfReader(out / "box-proof.pdf").pages[0].mediabox)
        die = PdfReader(out / "box-dieline.pdf").pages[0]
        spaces = die["/Resources"]["/ColorSpace"].get_object().values()
        self.assertEqual({str(v.get_object()[1]) for v in spaces}, {"/CutContour", "/Crease"})
        for name in ("box-artwork.pdf", "box-proof.pdf"):
            self.assertEqual(PdfReader(out / name).pages[0].mediabox, die.mediabox)

    def test_copies_resize_deck_and_box(self):
        self.cfg.CARDS = [{"text": "A question?", "copies": 80}]
        cards = app.validate(self.cfg)
        g = app.box_geometry(self.cfg, len(cards))
        self.assertEqual(len(cards), 80)
        self.assertAlmostEqual(g["depth"], 80*0.32+2)

    def test_no_bleed_pdf_preserves_finished_artwork(self):
        self.cfg.CARD_WIDTH_MM = 70
        self.cfg.CARD_HEIGHT_MM = 95
        self.cfg.BLEED_MM = 4
        self.cfg.CARDS = [
            {"text": "Category 1 question?", "color": "category_1", "copies": 2},
            {"text": "Category 3 question?", "color": "category_3"},
        ]
        out = self.build()
        normal = PdfReader(out / "cards.pdf")
        trimmed = PdfReader(out / "cards-no-bleed.pdf")
        self.assertEqual(len(trimmed.pages), 3)
        for full, tight in zip(normal.pages, trimmed.pages):
            self.assertAlmostEqual(float(tight.mediabox.width)/mm, 70, places=4)
            self.assertAlmostEqual(float(tight.mediabox.height)/mm, 95, places=4)
            self.assertEqual(list(tight.mediabox.lower_left), [0, 0])
            self.assertEqual(tight.mediabox, tight.trimbox)
            self.assertEqual(tight.mediabox, tight.bleedbox)
            self.assertEqual(full.extract_text(), tight.extract_text())
            full_ops = ContentStream(full.get_contents(), normal).operations
            tight_ops = ContentStream(tight.get_contents(), trimmed).operations
            self.assertEqual([v for v, op in full_ops if op in (b"k", b"Tf")],
                             [v for v, op in tight_ops if op in (b"k", b"Tf")])
            self.assertFalse({op for _, op in tight_ops} & {b"S", b"s", b"B", b"B*", b"b", b"b*"})
            full_text = [v for v, op in full_ops if op == b"Tm"]
            tight_text = [v for v, op in tight_ops if op == b"Tm"]
            self.assertEqual(len(full_text), len(tight_text))
            for a, b in zip(full_text, tight_text):
                self.assertAlmostEqual(float(a[4]-b[4])/mm, 4, places=3)
                self.assertAlmostEqual(float(a[5]-b[5])/mm, 4, places=3)

    def test_alternate_card_dimensions(self):
        self.cfg.CARD_WIDTH_MM = 70
        self.cfg.CARD_HEIGHT_MM = 100
        self.cfg.CARDS = ["What next?"]
        out = self.build()
        page = PdfReader(out / "cards.pdf").pages[0]
        self.assertAlmostEqual(float(page.trimbox.width)/mm, 70, places=4)
        self.assertAlmostEqual(float(page.trimbox.height)/mm, 100, places=4)

    def test_backs_match_palette_custom_inks_and_front_copies(self):
        self.cfg.CARDS = [
            {"text": "Category 1", "color": "category_1", "copies": 2},
            {"text": "Custom", "background_cmyk": (1, 2, 3, 4), "copies": 2},
            {"text": "Also custom", "background_cmyk": (1, 2, 3, 4)},
        ]
        out = self.build()
        report = json.loads((out / "build-report.json").read_text())
        designs = report["card_backs"]
        self.assertEqual(len(designs), len(self.cfg.CARD_COLORS_CMYK)+1)
        self.assertEqual(designs[0]["front_pages"], [1, 2])
        self.assertEqual(designs[-1]["front_pages"], [3, 4, 5])
        self.assertEqual(report["card_count"], 5)
        full = PdfReader(out / "card-backs.pdf")
        self.assertEqual(len(full.pages), len(designs))
        custom_count = 0
        for design in designs:
            if design["color"]:
                expected_file = f"card-backs-no-bleed-{design['color']}.pdf"
            else:
                custom_count += 1
                expected_file = f"card-backs-no-bleed-custom-{custom_count}.pdf"
            self.assertEqual(design["no_bleed_file"], expected_file)
        for index, page in enumerate(full.pages):
            tight = PdfReader(out / designs[index]["no_bleed_file"])
            self.assertEqual(len(tight.pages), 1)
            trimmed = tight.pages[0]
            self.assertEqual(page.trimbox, PdfReader(out / "cards.pdf").pages[0].trimbox)
            self.assertEqual(trimmed.mediabox, trimmed.trimbox)
            self.assertEqual(trimmed.mediabox, trimmed.bleedbox)
            for item, reader in ((page, full), (trimmed, tight)):
                ops = ContentStream(item.get_contents(), reader).operations
                fills = [tuple(float(n) for n in values) for values, op in ops if op == b"k"]
                expected_fills = [tuple(v/100 for v in designs[index]["background_cmyk"]),
                                  tuple(v/100 for v in self.cfg.CARD_BACK_LOGO_CMYK)]
                self.assertEqual(len(fills), len(expected_fills))
                for actual, expected in zip(fills, expected_fills):
                    for actual_channel, expected_channel in zip(actual, expected):
                        self.assertAlmostEqual(actual_channel, expected_channel, places=4)
                self.assertEqual(item.extract_text(), "")
                operators = {op for _, op in ops}
                self.assertIn(b"c", operators)  # Vector logo, no image or printed guides.
                self.assertFalse(operators & {b"Do", b"rg", b"RG", b"S", b"s"})

    def test_square_back_logo_is_centered_and_resizes(self):
        import logo
        self.cfg.CARD_WIDTH_MM = self.cfg.CARD_HEIGHT_MM = 63.5
        self.cfg.LOGO_VERSION = 3
        self.cfg.CARD_BACK_LOGO_SCALE = 0.5
        self.cfg.CARD_BACK_LOGO_CMYK = (0, 0, 0, 100)
        out = self.build()
        report = json.loads((out / "build-report.json").read_text())
        pdf = PdfReader(out / report["card_backs"][0]["no_bleed_file"])
        page = pdf.pages[0]
        self.assertAlmostEqual(float(page.mediabox.width), 180, places=3)
        self.assertAlmostEqual(float(page.mediabox.height), 180, places=3)
        # ReportLab combines the logo's translate/scale operations into one matrix.
        ops = ContentStream(page.get_contents(), pdf).operations
        matrices = [list(map(float, v)) for v, op in ops if op == b"cm"]
        a, b, c, d, e, f = matrices[-1]
        x, y, w, h = logo.mark_bounds(self.cfg.LOGO_VERSION, tight=True)
        cx, cy = logo.V3_CROSSING
        self.assertAlmostEqual(a*cx+c*cy+e, 90, places=3)
        self.assertAlmostEqual(b*cx+d*cy+f, 90, places=3)
        reach = max(abs(a*(x-cx)), abs(a*(x+w-cx)),
                    abs(d*(y-cy)), abs(d*(y+h-cy)))
        self.assertAlmostEqual(reach, 45, places=3)
        self.cfg.CARD_BACK_LOGO_SCALE = 1.1
        with self.assertRaisesRegex(ValueError, "CARD_BACK_LOGO_SCALE"):
            self.build()

    def test_v3_x_crossing_is_centered_above_box_title(self):
        import logo
        self.cfg.LOGO_VERSION = 3
        for width, height in self.cfg.CARD_FORMATS_MM.values():
            self.cfg.CARD_WIDTH_MM, self.cfg.CARD_HEIGHT_MM = width, height
            out = self.build()
            pdf = PdfReader(out / "box-artwork.pdf")
            ops = ContentStream(pdf.pages[0].get_contents(), pdf).operations
            a, b, c, d, e, f = [list(map(float, v)) for v, op in ops if op == b"cm"][-1]
            g = app.box_geometry(self.cfg, len(app.validate(self.cfg)))
            cx, cy = logo.V3_CROSSING
            self.assertAlmostEqual(a*cx+c*cy+e, (g["x"][2]+g["W"]/2)*mm, places=3)
            # Locate the title's first line in the PDF; its top defines the
            # lower boundary of the space being centered, even if it wraps.
            for values, op in ops:
                if op == b"Tf":
                    title_size = float(values[1])
                elif op == b"Tm":
                    baseline = float(values[5])
                elif op == b"Tj":
                    break
            title_top = baseline + app.pdfmetrics.getAscentDescent(app.FONT, title_size)[0]
            self.assertAlmostEqual(b*cx+d*cy+f, (g["H"]*mm+title_top)/2, places=3)

    def test_square_format_exports_exact_size_and_matching_box(self):
        self.cfg.CARD_FORMAT = "square"
        self.cfg.CARD_WIDTH_MM, self.cfg.CARD_HEIGHT_MM = self.cfg.CARD_FORMATS_MM["square"]
        out = self.build()
        full = PdfReader(out / "cards.pdf")
        tight = PdfReader(out / "cards-no-bleed.pdf")
        self.assertEqual(len(full.pages), len(self.cfg.CARDS))
        for page in full.pages:
            self.assertAlmostEqual(float(page.trimbox.width), 180, places=3)
            self.assertAlmostEqual(float(page.trimbox.height), 180, places=3)
            self.assertAlmostEqual(float(page.mediabox.width)/mm, 69.5, places=3)
            self.assertAlmostEqual(float(page.mediabox.height)/mm, 69.5, places=3)
        for page in tight.pages:
            self.assertAlmostEqual(float(page.mediabox.width), 180, places=3)
            self.assertAlmostEqual(float(page.mediabox.height), 180, places=3)
        box = app.box_geometry(self.cfg, len(full.pages))
        self.assertAlmostEqual(box["W"], 65.4)
        self.assertAlmostEqual(box["H"], 65.4)
        combined = PdfReader(out / "game.pdf")
        self.assertEqual(len(combined.pages), len(full.pages)+1)
        self.assertEqual(combined.pages[-1].mediabox, PdfReader(out / "box-proof.pdf").pages[0].mediabox)

    def test_cut_outline_is_one_closed_loop_without_fold_edges(self):
        for count in (1, 12, 52, 100):
            g = app.box_geometry(self.cfg, count)
            neighbors = {}
            for p, q in g["cut"]:
                neighbors.setdefault(p, []).append(q)
                neighbors.setdefault(q, []).append(p)
            self.assertTrue(all(len(v) == 2 for v in neighbors.values()))
            seen, pending = set(), [next(iter(neighbors))]
            while pending:
                p = pending.pop()
                if p not in seen:
                    seen.add(p)
                    pending.extend(neighbors[p])
            self.assertEqual(seen, set(neighbors))
            cuts = {frozenset(edge) for edge in g["cut"]}
            self.assertFalse(cuts & {frozenset(edge) for edge in g["fold"]})

    def test_bad_text_does_not_overwrite_successful_output(self):
        out = self.build()
        old = (out / "cards.pdf").read_bytes()
        self.cfg.CARDS = ["Unbreakable"*100]
        with self.assertRaisesRegex(ValueError, "cannot fit"):
            self.build()
        self.assertEqual(old, (out / "cards.pdf").read_bytes())

    def test_invalid_inputs_and_missing_glyph(self):
        self.cfg.CARD_COLORS_CMYK["category_1"] = (101, 0, 0, 0)
        with self.assertRaisesRegex(ValueError, "CMYK"):
            app.validate(self.cfg)
        self.cfg.CARD_COLORS_CMYK["category_1"] = (0, 0, 0, 0)
        self.cfg.CARDS = ["Unsupported \U0001f984"]
        with self.assertRaisesRegex(ValueError, "lacks"):
            app.validate(self.cfg)
        self.cfg.BOX_INTERNAL_DEPTH_MM = 1
        with self.assertRaisesRegex(ValueError, "at least"):
            app.box_geometry(self.cfg, 52)

    def test_named_colors_overrides_and_box_are_independent_in_pdf(self):
        self.cfg.CARDS = [
            {"text": "Category 1", "color": "category_1"},
            {"text": "Category 2", "color": "category_2"},
            {"text": "Category 3", "color": "category_3"},
            {"text": "Category 4", "color": "category_4"},
            "Default",
            {"text": "Custom", "color": "category_1", "background_cmyk": (1, 2, 3, 4)},
        ]
        self.cfg.BOX_BACKGROUND_CMYK = (20, 30, 40, 50)
        out = self.build()
        def first_fill(page, reader):
            return next(tuple(float(n) for n in values) for values, op in
                        ContentStream(page.get_contents(), reader).operations if op == b"k")
        cards = PdfReader(out / "cards.pdf")
        expected = [(0,.6871,.4558,.4235),(0,.2906,.8462,.0824),
                    (.0407,0,.5366,.5176),(.9,.7,0,0),
                    (0,.6871,.4558,.4235),(.01,.02,.03,.04)]
        self.assertEqual([first_fill(page, cards) for page in cards.pages], expected)
        box = PdfReader(out / "box-artwork.pdf")
        self.assertEqual(first_fill(box.pages[0], box), (.2,.3,.4,.5))

    def test_unknown_color_is_rejected(self):
        self.cfg.CARDS = [{"text": "Question", "color": "blu"}]
        with self.assertRaisesRegex(ValueError, "Unknown card color"):
            self.build()

    def test_logo_is_vector_and_keeps_game_name(self):
        out = self.build()
        box = PdfReader(out / "box-artwork.pdf")
        page = box.pages[0]
        ops = [op for _, op in ContentStream(page.get_contents(), box).operations]
        self.assertGreaterEqual(ops.count(b"c"), 8)
        self.assertNotIn(b"Do", ops)
        self.assertIn(self.cfg.GAME_NAME, " ".join(page.extract_text().split()))
        self.assertNotIn("Conversations for a life together", page.extract_text())
        self.cfg.USE_VECTOR_LOGO = False
        out = self.build()
        plain = PdfReader(out / "box-artwork.pdf")
        self.assertNotIn(b"c", [op for _, op in ContentStream(plain.pages[0].get_contents(), plain).operations])

    def test_font_can_switch_back_to_manrope(self):
        source = (app.ROOT / "game_config.py").read_text(encoding="utf-8")
        path = Path(self.tmp.name) / "alternate_config.py"
        path.write_text(re.sub(r'^FONT_NAME\s*=.*$', 'FONT_NAME = "manrope"',
                               source, count=1, flags=re.MULTILINE), encoding="utf-8")
        self.cfg = app.load_config(path)
        self.cfg.BASE = app.ROOT
        self.cfg.OUTPUT_DIR = self.tmp.name
        self.assertEqual(self.cfg.FONT_PATH, "assets/fonts/manrope/Manrope-Bold.ttf")
        out = self.build()
        pdf = PdfReader(out / "cards.pdf")
        fonts = pdf.pages[0]["/Resources"]["/Font"].get_object().values()
        self.assertTrue(all("Manrope" in str(ref.get_object()["/BaseFont"]) for ref in fonts))


if __name__ == "__main__":
    unittest.main()
