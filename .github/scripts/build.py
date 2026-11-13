"""Build the profile README artwork (the cover poster).

Fonts are subset and embedded in each SVG, because GitHub shows SVGs as <img>
and an <img> cannot load web fonts.

Usage: python .github/scripts/build.py
Requires: pip install fonttools brotli
"""
import base64
import io
import os
from xml.sax.saxutils import escape

from fontTools import subset
from fontTools.ttLib import TTFont

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "assets")
FONT_DIR = os.path.join(ROOT, ".github", "fonts")

FONTS = {  # key: (file, css family, css style, fallback stack)
    "ts": ("TenorSans-Regular.ttf", "Tenor Sans", "normal", "'Tenor Sans', Optima, 'Gill Sans', sans-serif"),
    "nr": ("Newsreader-Regular.ttf", "Newsreader", "normal", "Newsreader, Georgia, serif"),
    "ni": ("Newsreader-Italic.ttf", "Newsreader", "italic", "Newsreader, Georgia, serif"),
}
_tt = {k: TTFont(os.path.join(FONT_DIR, v[0])) for k, v in FONTS.items()}

THEMES = {
    "dark": dict(bg="#11100E", line="#2C2A26", line2="#3A3732", text="#ECE6DB",
                 muted="#9A9388", faint="#5F5A53", accent="#C9A27A"),
    "light": dict(bg="#F5F1EA", line="#DCD5C9", line2="#CBC3B5", text="#1B1916",
                  muted="#6B645A", faint="#A79F93", accent="#94653A"),
}


# ---------------------------------------------------------------- drawing kit

class Canvas:
    def __init__(self, w, h, title):
        self.w, self.h, self.title = w, h, title
        self.parts, self.used = [], {k: set() for k in FONTS}

    def add(self, s):
        self.parts.append(s)

    def width(self, s, font, size, ls=0.0):
        f = _tt[font]
        cmap, hmtx, upm = f.getBestCmap(), f["hmtx"], f["head"].unitsPerEm
        adv = sum(hmtx[cmap.get(ord(c), cmap.get(32))][0] for c in s)
        return adv * size / upm + ls * len(s)

    def text(self, x, y, s, font, size, fill, anchor="start", ls=0.0, upper=False):
        s = s.upper() if upper else s
        self.used[font].update(s)
        style, stack = FONTS[font][2], FONTS[font][3]
        self.add(f'<text x="{x:.1f}" y="{y:.1f}" font-family="{stack}" font-style="{style}" font-size="{size}" '
                 f'fill="{fill}" text-anchor="{anchor}" letter-spacing="{ls}">{escape(s)}</text>')
        return self.width(s, font, size, ls)

    def line(self, x1, y1, x2, y2, color, w=1):
        self.add(f'<path d="M{x1} {y1}L{x2} {y2}" stroke="{color}" stroke-width="{w}"/>')

    def arrow(self, x, y, color, s=11):
        self.add(f'<path d="M{x} {y+s} L{x+s} {y} M{x+3} {y} H{x+s} V{y+s-3}" stroke="{color}" '
                 f'stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round" fill="none"/>')

    def fontface(self):
        css = []
        for k, chars in self.used.items():
            if not chars:
                continue
            opts = subset.Options()
            opts.flavor = "woff2"
            opts.layout_features = ["kern", "liga"]
            f = TTFont(os.path.join(FONT_DIR, FONTS[k][0]))
            sub = subset.Subsetter(opts)
            sub.populate(text="".join(sorted(chars)) + " ")
            sub.subset(f)
            buf = io.BytesIO()
            f.flavor = "woff2"
            f.save(buf)
            b64 = base64.b64encode(buf.getvalue()).decode()
            css.append(f"@font-face{{font-family:'{FONTS[k][1]}';font-style:{FONTS[k][2]};font-weight:400;"
                       f"src:url(data:font/woff2;base64,{b64}) format('woff2');}}")
        return "".join(css)

    def render(self):
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" '
                f'viewBox="0 0 {self.w} {self.h}" role="img" aria-label="{escape(self.title)}" fill="none">\n'
                f'<title>{escape(self.title)}</title>\n<style>{self.fontface()}</style>\n'
                + "\n".join(self.parts) + "\n</svg>\n")


# ---------------------------------------------------------------- poster

def poster():
    t = THEMES["dark"]
    W, H = 1500, 500
    c = Canvas(W, H, "Moniruzzaman Monir — WordPress & Breakdance developer. BreakUI, BreakUI Pro, WPBuilderPros. moniir.dev")
    photo = base64.b64encode(open(os.path.join(ROOT, ".github", "img", "photo.jpg"), "rb").read()).decode()
    c.add(f'<defs><clipPath id="ph"><circle cx="1190" cy="250" r="168"/></clipPath>'
          f'<radialGradient id="warm" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" gradientTransform="translate(1190 250) scale(420)">'
          f'<stop stop-color="{t["accent"]}" stop-opacity=".13"/><stop offset="1" stop-color="{t["accent"]}" stop-opacity="0"/></radialGradient></defs>')
    c.add(f'<rect width="{W}" height="{H}" fill="{t["bg"]}"/>')
    c.add(f'<rect width="{W}" height="{H}" fill="url(#warm)"/>')
    c.add(f'<rect x="28.5" y="28.5" width="{W-57}" height="{H-57}" stroke="{t["line"]}"/>')
    # masthead
    c.text(72, 82, "WordPress · Breakdance", "ts", 15, t["muted"], ls=3.4, upper=True)
    c.line(72, 102.5, 900, 102.5, t["line2"])
    # name
    c.text(66, 212, "Moniruzzaman", "ts", 104, t["text"], ls=-3)
    c.text(66, 322, "Monir", "ts", 104, t["text"], ls=-3)
    c.text(398, 280, "builds WordPress websites,", "ni", 30, t["muted"], ls=-0.2)
    c.text(398, 318, "Breakdance plugins & templates.", "ni", 30, t["accent"], ls=-0.2)
    # brands
    c.line(72, 380.5, 900, 380.5, t["line2"])
    x = 72
    for i, b in enumerate(["BreakUI", "BreakUI Pro", "WPBuilderPros", "moniir.dev"]):
        if i:
            x += c.text(x, 424, "·", "ts", 15, t["faint"], ls=3.4) + 10
        x += c.text(x, 424, b, "ts", 15, t["text"] if i < 3 else t["accent"], ls=3.4, upper=True) + 10
    # photo
    c.add(f'<circle cx="1190" cy="250" r="196" stroke="{t["line2"]}"/>')
    c.add(f'<circle cx="1190" cy="250" r="178" stroke="{t["accent"]}" stroke-opacity=".7"/>')
    c.add(f'<image href="data:image/jpeg;base64,{photo}" x="1022" y="82" width="336" height="336" '
          f'clip-path="url(#ph)" preserveAspectRatio="xMidYMid slice"/>')
    # figures on the ring
    c.text(900, 82, "7+ yrs · 700+ sites · 120+ clients", "ts", 15, t["muted"], anchor="end", ls=3.4, upper=True)
    return c.render()


# ---------------------------------------------------------------- write

def main():
    os.makedirs(OUT, exist_ok=True)
    for f in os.listdir(OUT):
        if f.endswith(".svg"):
            os.remove(os.path.join(OUT, f))
    open(os.path.join(OUT, "poster.svg"), "w", encoding="utf-8").write(poster())
    print("Built assets/poster.svg")


if __name__ == "__main__":
    main()
