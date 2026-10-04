"""Security checks for the renderers. Run from the kit folder:  python3 tools/test_security.py -v

(a) a malicious win_top / spot_size is rejected before any page is rendered
(b) paths that leave the spec folder or art/ (../, absolute, escaping symlink, bad ids/devices) are rejected
(c) the sample spec still renders: 7 slides + PDF, CSP on every page, no script, existing files left alone
Test (c) needs Chrome (CHROME_PATH) and is skipped without it.
"""
import os, pathlib, subprocess, sys, tempfile, unittest, urllib.parse, urllib.request
from unittest import mock

sys.dont_write_bytecode = True  # keep the kit folder free of __pycache__
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import article_cover  # noqa: E402
import gui_frames  # noqa: E402

KIT = pathlib.Path(__file__).resolve().parent.parent
SPEC = {"id": "T", "kicker": "K", "slides": []}
WIN = {"kind": "terminal", "title": "t", "lines": [["out", "hi"]]}
PAYLOAD = '0px"></div><script>globalThis.auditProbe=1</script><div style="top:0'


class Base(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self._tmp.name)
        self.spec_dir = self.root / "spec"
        self.spec_dir.mkdir()

    def tearDown(self):
        self._tmp.cleanup()

    def rejected(self, s, word):
        with mock.patch.object(gui_frames, "render") as render, self.assertRaises(SystemExit) as cm:
            gui_frames.slide(SPEC, s, 1, 1, self.root / "01.png", self.root, self.spec_dir)
        self.assertIn(word, str(cm.exception))
        render.assert_not_called()


class A_NumericFields(Base):
    def test_malicious_win_top_rejected(self):
        for bad in (PAYLOAD, "400", 400.0, True, -1, 5000, None):
            with self.subTest(win_top=bad):
                self.rejected({"type": "window", "title": "t", "win": WIN, "win_top": bad}, "win_top")

    def test_malicious_spot_size_rejected(self):
        for bad in ('280px;background:url(https://example.com/x)', "280", 79, 601):
            with self.subTest(spot_size=bad):
                self.rejected({"type": "text", "title": "t", "items": ["a"], "spot": "stamp", "spot_size": bad}, "spot_size")

    def test_valid_numbers_still_accepted(self):
        with mock.patch.object(gui_frames, "render") as render:
            gui_frames.slide(SPEC, {"type": "window", "title": "t", "win": WIN, "win_top": 400,
                                    "spot": "stamp", "spot_size": 280}, 1, 1, self.root / "01.png", self.root, self.spec_dir)
        page = render.call_args[0][0]
        self.assertIn("top:400px", page)
        self.assertIn("width:280px;height:280px", page)


class B_Paths(Base):
    def test_src_outside_spec_folder_rejected(self):
        outside = self.root / "outside.png"
        outside.write_bytes(b"private")
        (self.spec_dir / "link.png").symlink_to(outside)
        for bad in ("../outside.png", str(outside), "link.png", "sub/../../outside.png"):
            with self.subTest(src=bad):
                self.rejected({"type": "image", "title": "t", "src": bad}, "outside the allowed folders")

    def test_src_inside_spec_folder_accepted(self):
        (self.spec_dir / "ok.png").write_bytes(b"x")
        with mock.patch.object(gui_frames, "render") as render:
            gui_frames.slide(SPEC, {"type": "image", "title": "t", "src": "ok.png"}, 1, 1,
                             self.root / "01.png", self.root, self.spec_dir)
        self.assertIn((self.spec_dir / "ok.png").resolve().as_uri(), render.call_args[0][0])

    def test_bad_ids_and_devices_rejected(self):
        self.rejected({"type": "cover", "art": "../G02", "hook": "h", "sub": "s"}, "art")
        self.rejected({"type": "cover", "art": "/etc/passwd", "hook": "h", "sub": "s"}, "art")
        self.rejected({"type": "text", "title": "t", "items": ["a"], "spot": "../../x"}, "spot")
        for bad in ("../devices/laptop", "tablet"):
            with self.subTest(device=bad):
                self.rejected({"type": "window", "title": "t", "win": WIN, "device": bad}, "device")

    def test_article_cover_bad_art_id_rejected(self):
        for bad in ("../G02", "G02/../../x", "/tmp/x"):
            with self.subTest(art_id=bad), self.assertRaises(SystemExit):
                article_cover.cover(bad, self.root, "k", "t1", "t2", "s", self.root)


@unittest.skipUnless(os.path.exists(gui_frames.CHROME), "Chrome not found; set CHROME_PATH")
class C_SampleRenders(Base):
    def test_sample_spec_renders(self):
        out = self.root / "out"
        out.mkdir()
        decoys = {out / "_dev_04.png": b"keep", out / "01.html": b"keep"}  # old code deleted/overwrote these
        for p, data in decoys.items():
            p.write_bytes(data)
        pages, real_run = [], subprocess.run

        def spy(cmd, **kw):  # read the exact HTML Chrome is about to load
            pages.append(pathlib.Path(urllib.request.url2pathname(urllib.parse.urlparse(cmd[-1]).path)).read_text())
            return real_run(cmd, **kw)

        with mock.patch.object(gui_frames.subprocess, "run", side_effect=spy):
            gui_frames.main(KIT / "examples" / "slides.sample.json", out)

        for n in range(1, 8):
            with gui_frames.Image.open(out / f"{n:02d}.png") as im:
                self.assertEqual(im.size, (1080, 1350))
        self.assertTrue((out / "carousel.sample.pdf").stat().st_size > 0)
        for p, data in decoys.items():
            self.assertEqual(p.read_bytes(), data, f"{p.name} was touched")
        leftovers = {p.name for p in out.iterdir()} - {f"{n:02d}.png" for n in range(1, 8)} - {"carousel.sample.pdf"}
        self.assertEqual(leftovers, {p.name for p in decoys})
        self.assertEqual(len(pages), 8)  # 7 slides + 1 device screen
        for page in pages:
            self.assertIn(gui_frames.CSP, page)
            self.assertNotIn("<script", page.lower())


if __name__ == "__main__":
    unittest.main()
