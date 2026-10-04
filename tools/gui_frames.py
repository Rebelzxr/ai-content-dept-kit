"""Render IG / LinkedIn carousel slides (1080x1350), with GUI screenshots built from REAL text.

Usage (from the kit folder):
  python3 tools/gui_frames.py examples/slides.sample.json [OUT_DIR]
Output: OUT_DIR/NN.png plus OUT_DIR/carousel*.pdf. Without OUT_DIR: <spec folder>/<spec stem>/NN.png and the PDF
next to the spec (slides.json -> slides/ + carousel.pdf, slides_en.json -> slides_en/ + carousel_en.pdf).
Chinese text is the default; add "lang": "en" to the spec for English slides (Inter first, Noto Sans SC fallback).
Optional spec keys: "brand" (footer left, default "DAINER.AI · dainer-ai.biz"), "footer" (footer right).
Needs: Python 3.9+, Pillow, numpy, Google Chrome (set CHROME_PATH if it is not in the default macOS location).

Spec: {"id", "kicker", "slides": [ {type, ...}, ... ]}. Slide types:
  cover  {art, hook, sub}                          RISO art (art/<art>-RISO.png) + headline
  text   {title, items[], note?, spot?}            numbered takeaways; spot = art/spots/<name>.png illustration
  window {title, sub?, win, device?}               a terminal/editor window; with device ("laptop"|"phone"|"monitor")
                                                   it is pasted onto the green screen of art/devices/<device>.png
  image  {title, sub?, src, note?}                 a real image (path relative to the spec), e.g. a video frame
  end    {title, items[], cta, spot?}
win = {"kind": "terminal"|"editor", "title": str, "lines": [[style, text], ...]}
  styles: cmd (prompt line), out, dim, ok, bad, hl (highlighted), code (editor line)
Only paste commands and outputs that really ran; the note on each slide says when and with which version.
Safety: win_top must be a whole number 0-1350 and spot_size 80-600; art/spot ids use only letters, digits, _ and -;
device is one of laptop/phone/monitor; src must stay inside the spec's folder or the kit's art/ (symlinks included).
"""
import html, json, os, pathlib, re, subprocess, sys, tempfile
from PIL import Image
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ART = HERE.parent / "art"  # kit/art: <id>-RISO.png covers, spots/<name>_cut.png, devices/<device>.png
# Fonts load from Google Fonts (needs internet). Offline: install the same families locally (see tools/README.md).
CHROME = os.environ.get("CHROME_PATH", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
W, H = 1080, 1350
FONTS = ('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
         'family=Noto+Sans+SC:wght@500;700;900&family=Inter:wght@500;700;900&family=JetBrains+Mono:wght@500;700&family=IBM+Plex+Mono:wght@600&display=swap">')
# Every page: no scripts, frames or connections; images only from local files; styles/fonts only from Google Fonts.
CSP = ('<meta http-equiv="Content-Security-Policy" content="default-src \'none\'; img-src file: data:; '
       'style-src \'unsafe-inline\' https://fonts.googleapis.com; font-src https://fonts.gstatic.com">')
PAPER, INK, BLUE, ORANGE, MUTED = "#F3EDE0", "#14171C", "#2D4E8C", "#D9622B", "#5B606A"
DEVICES = ("laptop", "phone", "monitor")
e = html.escape


def bounded_int(s, key, default, lo, hi):
    v = s.get(key, default)
    if type(v) is not int or not lo <= v <= hi:
        raise SystemExit(f"{key} must be a whole number from {lo} to {hi}, got {v!r}")
    return v


def safe_id(value, key):
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9_-]+", value):
        raise SystemExit(f"{key} may use only letters, digits, _ and -, got {value!r}")
    return value


def inside(path, *roots):
    """Resolve path (following symlinks) and require it to stay inside one of roots."""
    p = path.resolve()
    if not any(p.is_relative_to(r.resolve()) for r in roots):
        raise SystemExit(f"path is outside the allowed folders ({', '.join(str(r) for r in roots)}): {path}")
    return p


def render(page, png, w, h):
    with tempfile.TemporaryDirectory() as tmp:  # the HTML never touches the output folder
        src = pathlib.Path(tmp) / "page.html"
        src.write_text(f'<!doctype html><meta charset="utf-8">{CSP}{FONTS}{page}')
        cmd = [CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", f"--window-size={w},{h}",
               "--virtual-time-budget=6000", f"--screenshot={png}", src.as_uri()]
        try:
            subprocess.run(cmd, check=True, capture_output=True, timeout=90)
        except subprocess.TimeoutExpired:  # headless Chrome occasionally hangs; one retry
            subprocess.run(cmd, check=True, capture_output=True, timeout=90)


def window_html(win, width, height=None):
    term = win["kind"] == "terminal"
    bg, fg = ("#1B1E24", "#E8E6DF") if term else ("#FFFFFF", INK)
    colors = {"cmd": "#F5C46B" if term else BLUE, "out": fg, "dim": "#8A909B", "ok": "#7FD69B" if term else "#1F6B52",
              "bad": "#FF8A7A" if term else "#B23A2E", "hl": fg, "code": fg}
    rows = []
    for style, text in win["lines"]:
        t = e(text) if text else "&nbsp;"
        if style == "cmd":
            t = f'<span style="color:#8A909B">$ </span>{t}' if term else t
        extra = "background:rgba(217,98,43,.22);border-radius:4px;" if style == "hl" else ""
        rows.append(f'<div class="ln" style="color:{colors.get(style, fg)};{extra}">{t}</div>')
    hcss = f"height:{height}px;" if height else ""
    return f"""<div class="win" style="width:{width}px;{hcss}background:{bg};">
<div class="bar"><i style="background:#FF5F57"></i><i style="background:#FEBC2E"></i><i style="background:#28C840"></i><span>{e(win['title'])}</span></div>
<div class="body" style="color:{fg}">{''.join(rows)}</div></div>"""


WIN_CSS = """.win{border-radius:14px;overflow:hidden;box-shadow:0 18px 40px rgba(20,23,28,.28);border:1px solid rgba(0,0,0,.12)}
.bar{height:44px;display:flex;align-items:center;gap:9px;padding:0 16px;background:rgba(127,127,127,.16)}
.bar i{width:13px;height:13px;border-radius:50%;display:block}
.bar span{margin-left:10px;font:600 17px 'IBM Plex Mono',monospace;color:#8A909B}
.body{padding:20px 24px;font:500 22px/1.55 'JetBrains Mono','Noto Sans SC',monospace;white-space:pre-wrap;word-break:break-word}
.ln{padding:0 4px}"""


def screen_png(win, out, w, h, zoom=2):
    """The window alone, filling a w x h screen (used inside device art); rendered at zoom x for sharp text."""
    page = (f"<style>*{{margin:0}}html{{zoom:{zoom}}}body{{width:{w}px;height:{h}px;background:#1B1E24}}{WIN_CSS}"
            f".win{{border-radius:0;box-shadow:none;border:0}}.body{{font-size:19px;padding:14px 16px}}.bar{{height:34px}}</style>{window_html(win, w, h)}")
    render(page, out, w * zoom, h * zoom)


def green_box(img):
    a = np.asarray(img.convert("RGB")).astype(int)
    mask = (a[:, :, 1] > 200) & (a[:, :, 0] < 90) & (a[:, :, 2] < 90)
    ys, xs = np.where(mask)
    if len(xs) < 1000:
        raise SystemExit("no green screen found in device art")
    return xs.min(), ys.min(), xs.max(), ys.max()


def device_png(device, win, out, target_w):
    """Crop the device art close around its green screen, scale to target_w, then paste the real window on the screen."""
    if device not in DEVICES:
        raise SystemExit(f"device must be one of {', '.join(DEVICES)}, got {device!r}")
    art = Image.open(inside(ART / "devices" / f"{device}.png", ART)).convert("RGB")
    x0, y0, x1, y1 = green_box(art)
    gw, gh = x1 - x0, y1 - y0
    cx0, cy0 = max(0, x0 - int(gw * .16)), max(0, y0 - int(gh * .12))
    cx1, cy1 = min(art.width, x1 + int(gw * .16)), min(art.height, y1 + int(gh * .30))
    crop = art.crop((cx0, cy0, cx1, cy1))
    k = target_w / crop.width
    crop = crop.resize((target_w, int(crop.height * k)), Image.LANCZOS)
    pad = 3  # cover the anti-aliased green fringe
    sx0, sy0 = int((x0 - cx0) * k) - pad, int((y0 - cy0) * k) - pad
    sw, sh = int(gw * k) + 2 * pad, int(gh * k) + 2 * pad
    tmp = out.with_name(out.stem + "_screen.png")
    screen_png(win, tmp, sw, sh)
    crop.paste(Image.open(tmp).convert("RGB").resize((sw, sh), Image.LANCZOS), (sx0, sy0))
    tmp.unlink()
    crop.save(out)


BASE = f"""<style>*{{margin:0;box-sizing:border-box}}
body{{width:{W}px;height:{H}px;background:{PAPER};font-family:'Noto Sans SC',sans-serif;color:{INK};position:relative;overflow:hidden}}
.k{{position:absolute;left:72px;top:64px;font:600 22px 'IBM Plex Mono',monospace;letter-spacing:.08em;color:{BLUE}}}
.pg{{position:absolute;right:72px;top:64px;font:600 22px 'IBM Plex Mono',monospace;color:{MUTED}}}
.ft{{position:absolute;left:72px;right:72px;bottom:52px;display:flex;justify-content:space-between;font:500 22px 'Noto Sans SC';color:{MUTED}}}
.ft b{{color:{INK}}}
h1{{font-weight:900;letter-spacing:-.01em;text-wrap:balance}}
.note{{font:500 24px/1.45 'Noto Sans SC';color:{MUTED}}}
{WIN_CSS}</style>"""


def frame(spec, n, total, inner, footer=True):
    brand, _, site = spec.get("brand", "DAINER.AI · dainer-ai.biz").partition(" · ")
    left = f"<b>{e(brand)}</b>" + (f" · {e(site)}" if site else "")
    ft = (f'<div class="ft"><span>{left}</span><span>{e(spec.get("footer", "完整版在 X 长文"))}</span></div>' if footer else "")
    return BASE + f'<div class="k">{e(spec["kicker"])}</div><div class="pg">{n}/{total}</div>{inner}{ft}'


def slide(spec, s, n, total, out, workdir, spec_dir=None):
    t = s["type"]
    if t == "cover":
        art = inside(ART / f"{safe_id(s['art'], 'art')}-RISO.png", ART)
        inner = (f'<div style="position:absolute;inset:0;background:url({art.as_uri()}) center bottom/cover"></div>'
                 f'<div style="position:absolute;left:72px;right:72px;top:130px"><h1 style="font-size:76px;line-height:1.16">{e(s["hook"])}</h1>'
                 f'<div style="margin-top:22px;font:700 32px/1.4 \'Noto Sans SC\';color:{ORANGE}">{e(s["sub"])}</div></div>')
    elif t == "text":
        items = "".join(f'<div style="display:flex;gap:22px;align-items:baseline;padding:{max(26, 150 // len(s["items"]))}px 0;border-top:2px solid rgba(20,23,28,.12)">'
                        f'<span style="font:700 30px \'IBM Plex Mono\';color:{ORANGE};min-width:44px">{i + 1:02d}</span>'
                        f'<span style="font:700 46px/1.35 \'Noto Sans SC\'">{e(x)}</span></div>' for i, x in enumerate(s["items"]))
        note = f'<div class="note" style="margin-top:26px">{e(s["note"])}</div>' if s.get("note") else ""
        inner = (f'<div style="position:absolute;left:72px;right:72px;top:150px"><h1 style="font-size:64px;line-height:1.2;margin-bottom:40px">{e(s["title"])}</h1>'
                 f'{items}{note}</div>')
    elif t == "window":
        head = (f'<div style="position:absolute;left:72px;right:72px;top:130px"><h1 style="font-size:52px;line-height:1.22">{e(s["title"])}</h1>'
                + (f'<div style="margin-top:14px;font:500 30px/1.45 \'Noto Sans SC\';color:{MUTED}">{e(s["sub"])}</div>' if s.get("sub") else "") + "</div>")
        note = f'<div class="note" style="position:absolute;left:72px;right:72px;bottom:110px">{e(s["note"])}</div>' if s.get("note") else ""
        if s.get("device"):
            dev = workdir / f"_dev_{n:02d}.png"
            device_png(s["device"], s["win"], dev, 936)
            inner = head + f'<div style="position:absolute;left:72px;right:72px;top:300px;bottom:160px;display:flex;align-items:center"><img src="{dev.as_uri()}" style="width:936px;max-height:100%;object-fit:contain"></div>' + note
        else:
            inner = (head + '<style>.big .body{font-size:32px;line-height:1.6;padding:28px 30px}.big .bar{height:52px}.big .bar span{font-size:20px}</style>'
                     f'<div class="big" style="position:absolute;left:72px;right:72px;top:{bounded_int(s, "win_top", 330, 0, H)}px;bottom:170px;display:flex;align-items:center">{window_html(s["win"], 936)}</div>' + note)
    elif t == "image":  # a real image (screenshot, video frame) from the evidence folder, path relative to the spec
        src = inside(spec_dir / s["src"], spec_dir, ART)
        head = (f'<div style="position:absolute;left:72px;right:72px;top:130px"><h1 style="font-size:52px;line-height:1.22">{e(s["title"])}</h1>'
                + (f'<div style="margin-top:14px;font:500 30px/1.45 \'Noto Sans SC\';color:{MUTED}">{e(s["sub"])}</div>' if s.get("sub") else "") + "</div>")
        note = f'<div class="note" style="position:absolute;left:72px;right:72px;bottom:110px">{e(s["note"])}</div>' if s.get("note") else ""
        inner = head + (f'<div style="position:absolute;left:72px;right:72px;top:330px;bottom:170px;display:flex;align-items:center;justify-content:center">'
                        f'<img src="{src.as_uri()}" style="max-width:100%;max-height:100%;object-fit:contain;border-radius:10px;box-shadow:0 18px 40px rgba(20,23,28,.25)"></div>') + note
    elif t == "end":
        items = "".join(f'<div style="font:500 40px/1.5 \'Noto Sans SC\';padding:18px 0"><b style="color:{ORANGE};font-family:\'IBM Plex Mono\'">{i + 1}.</b> {e(x)}</div>'
                        for i, x in enumerate(s["items"]))
        inner = (f'<div style="position:absolute;left:72px;right:72px;top:150px"><h1 style="font-size:58px;line-height:1.22;margin-bottom:30px">{e(s["title"])}</h1>{items}'
                 f'<div style="margin-top:44px;display:inline-block;background:{INK};color:{PAPER};font:700 32px \'Noto Sans SC\';padding:18px 28px;border-radius:8px">{e(s["cta"])}</div></div>')
    else:
        raise SystemExit(f"unknown slide type {t}")
    if s.get("spot"):  # RISO spot illustration (art/spots/<name>.png), multiplied onto the paper
        size = bounded_int(s, "spot_size", 400, 80, 600)
        spot = inside(ART / "spots" / (safe_id(s["spot"], "spot") + "_cut.png"), ART)
        inner += (f'<img src="{spot.as_uri()}" style="position:absolute;right:48px;bottom:96px;'
                  f'width:{size}px;height:{size}px">')
    page = frame(spec, n, total, inner, footer=t != "cover")
    if spec.get("lang") == "en":  # English slides: Inter for Latin text, Noto Sans SC kept as fallback
        page = page.replace("'Noto Sans SC'", "'Inter','Noto Sans SC'")
    render(page, out, W, H)


def main(spec_path, out_dir=None):
    spec_path = pathlib.Path(spec_path).resolve()
    spec = json.loads(spec_path.read_text())
    # default: slides.json -> slides/, slides_en.json -> slides_en/
    pdf_dir = pathlib.Path(out_dir).resolve() if out_dir else spec_path.parent
    out_dir = pathlib.Path(out_dir).resolve() if out_dir else spec_path.parent / spec_path.stem
    out_dir.mkdir(parents=True, exist_ok=True)
    total = len(spec["slides"])
    pngs = []
    with tempfile.TemporaryDirectory() as tmp:  # device composites live here and vanish with it
        for n, s in enumerate(spec["slides"], 1):
            png = out_dir / f"{n:02d}.png"
            slide(spec, s, n, total, png, pathlib.Path(tmp), spec_path.parent)
            pngs.append(png)
            print(png.name, s["type"])
    ims = [Image.open(p).convert("RGB") for p in pngs]
    pdf = "carousel.pdf" if spec_path.stem == "slides" else f"carousel{spec_path.stem[len('slides'):]}.pdf"
    ims[0].save(pdf_dir / pdf, save_all=True, append_images=ims[1:])
    print("pdf ok")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
