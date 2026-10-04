"""X Article header (5:2, 1500x600) with Chinese title typeset over text-free RISO art, plus an optional code card.

Usage (from the kit folder):
  python3 tools/article_cover.py <ART_ID> <OUT_DIR> "<kicker>" "<title line 1>" "<title line 2>" "<series>" [code_file]
ART_ID picks art/<ART_ID>-RISO.png (e.g. G02). Output: <OUT_DIR>/cover.png and, when code_file is given,
<OUT_DIR>/code.png (1200 wide) as a fallback image in case the X Article editor does not keep the code block formatting.
The code card label defaults to ".claude/settings.json"; set CODE_LABEL to change it. Brand text: KIT_BRAND (default DAINER.AI).
Needs: Python 3.9+, Pillow, Google Chrome (set CHROME_PATH if it is not in the default macOS location).
Safety: ART_ID may use only letters, digits, _ and -, and the art file must stay inside the kit's art/ (symlinks included).
"""
import html, os, pathlib, re, subprocess, sys, tempfile
from PIL import Image

HERE = pathlib.Path(__file__).resolve().parent
ART = HERE.parent / "art"  # kit/art
CHROME = os.environ.get("CHROME_PATH", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
BRAND = os.environ.get("KIT_BRAND", "DAINER.AI")
CODE_LABEL = os.environ.get("CODE_LABEL", ".claude/settings.json")
FONTS = ('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
         'family=Noto+Sans+SC:wght@500;700;900&family=IBM+Plex+Mono:wght@500;600&display=swap">')
# Every page: no scripts, frames or connections; images only from local files; styles/fonts only from Google Fonts.
CSP = ('<meta http-equiv="Content-Security-Policy" content="default-src \'none\'; img-src file: data:; '
       'style-src \'unsafe-inline\' https://fonts.googleapis.com; font-src https://fonts.gstatic.com">')
PAPER, INK, ACCENT = "#F3EDE0", "#14171C", "#2D4E8C"


def render(html_text, png_path, w, h):
    with tempfile.TemporaryDirectory() as tmp:  # the HTML never touches the output folder
        src = pathlib.Path(tmp) / "page.html"
        src.write_text(html_text)
        subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                        f"--window-size={w},{h}", "--virtual-time-budget=6000",
                        f"--screenshot={png_path}", src.as_uri()],
                       check=True, capture_output=True, timeout=90)


def cover(art_id, out, kicker, t1, t2, series, workdir):
    if not re.fullmatch(r"[A-Za-z0-9_-]+", art_id):
        raise SystemExit(f"ART_ID may use only letters, digits, _ and -, got {art_id!r}")
    art = (ART / f"{art_id}-RISO.png").resolve()
    if not art.is_relative_to(ART.resolve()):
        raise SystemExit(f"art file is outside {ART}: {art}")
    im = Image.open(art)
    w, h = im.size
    # the art keeps its subject in the lower ~60%; crop that band at the panel's 860:600 ratio
    ch = int(w * 600 / 860)
    top = min(h - ch, int(h * 0.42))
    crop = workdir / "art_crop.png"
    im.crop((0, top, w, top + ch)).save(crop)
    e = html.escape
    page = f"""<!doctype html><meta charset="utf-8">{CSP}{FONTS}<style>
*{{margin:0;box-sizing:border-box}} body{{width:1500px;height:600px;background:{PAPER};display:flex;font-family:'Noto Sans SC',sans-serif;color:{INK}}}
.txt{{width:640px;padding:64px 40px 56px 72px;display:flex;flex-direction:column}}
.k{{font:600 22px 'IBM Plex Mono',monospace;letter-spacing:.08em;color:{ACCENT};margin-bottom:28px}}
h1{{font-weight:900;font-size:62px;line-height:1.18;letter-spacing:-.01em}}
.s{{margin-top:auto;font-weight:500;font-size:22px;color:#4A4F57}}
.s b{{color:{INK}}}
.art{{width:860px;height:600px;background:url('{crop.as_uri()}') center/cover}}
</style><div class="txt"><div class="k">{e(kicker)}</div><h1>{e(t1)}<br>{e(t2)}</h1>
<div class="s"><b>{e(BRAND)}</b> · {e(series)}</div></div><div class="art"></div>"""
    render(page, out / "cover.png", 1500, 600)


def code_card(code_file, out):
    code = html.escape(pathlib.Path(code_file).read_text().rstrip())
    lines = code.count("\n") + 1
    h = 120 + lines * 44
    page = f"""<!doctype html><meta charset="utf-8">{CSP}{FONTS}<style>
*{{margin:0}} body{{width:1200px;height:{h}px;background:{PAPER};padding:40px 56px;box-sizing:border-box}}
.f{{font:600 20px 'IBM Plex Mono',monospace;color:{ACCENT};margin-bottom:16px}}
pre{{font:500 30px/44px 'IBM Plex Mono',monospace;color:{INK}}}
</style><div class="f">{html.escape(CODE_LABEL)}</div><pre>{code}</pre>"""
    render(page, out / "code.png", 1200, h)


if __name__ == "__main__":
    if len(sys.argv) < 7:
        raise SystemExit(__doc__)
    art_id, out_dir, kicker, t1, t2, series = sys.argv[1:7]
    out = pathlib.Path(out_dir).resolve()
    out.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:  # the art crop lives here and vanishes with it
        cover(art_id, out, kicker, t1, t2, series, pathlib.Path(tmp))
    if len(sys.argv) > 7:
        code_card(sys.argv[7], out)
    print("ok", out)
