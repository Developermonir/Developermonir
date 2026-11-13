"""Build the profile README artwork (dark + light SVGs) from one data source.

Fonts are subset and embedded in each SVG, because GitHub shows SVGs as <img>
and an <img> cannot load web fonts.

Usage: python .github/scripts/build.py            # use versions in versions.json
       python .github/scripts/build.py --fetch    # refresh versions first
Requires: pip install fonttools brotli
"""
import base64
import io
import json
import os
import sys
import urllib.request
from xml.sax.saxutils import escape

from fontTools import subset
from fontTools.ttLib import TTFont

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "assets")
FONT_DIR = os.path.join(ROOT, ".github", "fonts")
VERSIONS = os.path.join(ROOT, ".github", "versions.json")

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


# ---------------------------------------------------------------- data

def load_versions():
    try:
        return json.load(open(VERSIONS))
    except Exception:
        return {"breakui-pro": "2.0.22", "breakui-preview-pass": "1.3.0"}


def fetch_versions(v):
    def get(url):
        req = urllib.request.Request(url, headers={"User-Agent": "profile-readme"})
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.load(r)

    try:
        v["breakui-pro"] = get("https://pro.breakui.com/wp-json/bu-pro/v1/update")["version"] or v["breakui-pro"]
    except Exception as e:
        print("BreakUI Pro version fetch failed:", e)
    try:
        v["breakui-preview-pass"] = get(
            "https://api.wordpress.org/plugins/info/1.2/?action=plugin_information&request%5Bslug%5D=breakui-preview-pass"
        )["version"] or v["breakui-preview-pass"]
    except Exception as e:
        print("Preview Pass version fetch failed:", e)
    json.dump(v, open(VERSIONS, "w"), indent=2)
    return v


def work(v):
    return [
        dict(slug="breakui-pro", kind="Premium plugin", title="BreakUI Pro",
             lines=["Add-on elements for the Breakdance builder:", "Smart Video, Contact Hub, PDF Viewer, Ask Buddy."],
             meta=f"v{v['breakui-pro']}"),
        dict(slug="preview-pass", kind="Free · WordPress.org", title="Preview Pass",
             lines=["Private preview links for client drafts.", "No login, no staging site, nothing to unlock."],
             meta=f"v{v['breakui-preview-pass']}"),
        dict(slug="breakui", kind="Marketplace", title="BreakUI",
             lines=["Breakdance templates and sections", "for agencies and freelancers."], meta="Live"),
        dict(slug="wpbuilderpros", kind="Studio", title="WPBuilderPros",
             lines=["WordPress builds, redesigns, WooCommerce,", "speed, SEO and fixes."], meta="Live"),
        dict(slug="typeset", kind="Free tool", title="Typeset",
             lines=["A fluid type scale generator that writes", "the CSS clamp() values for you."], meta="Live"),
    ]


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


# ---------------------------------------------------------------- hero

def hero(t):
    W, H = 1000, 520
    c = Canvas(W, H, "Moniruzzaman Monir — WordPress & Breakdance developer. 7+ years, 700+ websites, 120+ clients.")
    c.text(0, 22, "Moniruzzaman Monir", "ts", 11, t["muted"], ls=2.6, upper=True)
    c.text(W / 2, 22, "Developer · Plugin author", "ts", 11, t["muted"], anchor="middle", ls=2.6, upper=True)
    c.text(W, 22, "Tangail, Bangladesh", "ts", 11, t["muted"], anchor="end", ls=2.6, upper=True)
    c.line(0, 40.5, W, 40.5, t["line2"])
    c.text(-4, 160, "Moniruzzaman", "ts", 92, t["text"], ls=-2.5)
    c.text(-4, 262, "Monir", "ts", 92, t["text"], ls=-2.5)
    sx = 330
    c.text(sx, 205, "builds WordPress websites,", "ni", 27, t["muted"], ls=-0.2)
    c.text(sx, 241, "Breakdance plugins and templates —", "ni", 27, t["muted"], ls=-0.2)
    c.text(sx, 277, "carefully, and fast.", "ni", 27, t["accent"], ls=-0.2)
    c.line(0, 352.5, W, 352.5, t["line"])
    figs = [("7+", "Years in WordPress"), ("700+", "Websites shipped"),
            ("120+", "Clients worldwide"), ("350+", "Projects on Fiverr")]
    cw = W / 4
    for i, (n, lab) in enumerate(figs):
        x = cw * i + (0 if i == 0 else 24)
        if i:
            c.line(cw * i, 372, cw * i, 470, t["line"])
        c.text(x, 425, n, "ts", 48, t["text"], ls=-1)
        c.text(x + 2, 458, lab, "ts", 10.5, t["muted"], ls=2.2, upper=True)
    c.line(0, 490.5, W, 490.5, t["line"])
    c.text(0, 514, "Available for new projects", "ni", 15, t["accent"])
    c.text(W, 514, "moniir.dev", "ts", 11, t["muted"], anchor="end", ls=2.6, upper=True)
    return c.render()


# ---------------------------------------------------------------- section header

def section(t, num, name, note):
    W, H = 1000, 74
    c = Canvas(W, H, name)
    c.text(0, 40, num, "ts", 12, t["accent"], ls=2)
    c.text(44, 44, name, "ts", 34, t["text"], ls=-0.6)
    c.text(W, 42, note, "ni", 17, t["muted"], anchor="end")
    c.line(0, 72.5, W, 72.5, t["line2"])
    return c.render()


# ---------------------------------------------------------------- work row

def row(t, i, w, last):
    W, H = 1000, 116
    c = Canvas(W, H, f'{w["title"]} — {w["kind"]}. {" ".join(w["lines"])} {w["meta"]}')
    c.text(0, 50, f"{i:02d}", "ts", 12, t["accent"], ls=2)
    c.text(44, 58, w["title"], "ts", 38, t["text"], ls=-0.8)
    c.text(46, 86, w["kind"], "ts", 10.5, t["muted"], ls=2.2, upper=True)
    c.text(500, 50, w["lines"][0], "nr", 17, t["muted"])
    c.text(500, 74, w["lines"][1], "nr", 17, t["muted"])
    c.text(W - 26, 50, w["meta"], "ts", 12, t["text"], anchor="end", ls=1.2)
    c.arrow(W - 12, 40, t["text"])
    c.line(0, 115.5, W, 115.5, t["line2"] if last else t["line"])
    return c.render()


# ---------------------------------------------------------------- toolkit

STACK = [
    ("Build with", ["WordPress", "Breakdance", "WooCommerce", "Divi", "Gutenberg"]),
    ("Write in", ["PHP", "JavaScript", "TypeScript", "Twig", "CSS", "SQL"]),
    ("Ship on", ["Figma", "Git", "Hostinger", "Cloudflare", "WP Engine"]),
]


def toolkit(t):
    W, H = 1000, 196
    c = Canvas(W, H, "Toolkit: " + ", ".join(i for _, its in STACK for i in its))
    for r, (label, items) in enumerate(STACK):
        y = 50 + r * 62
        c.text(0, y, label, "ts", 10.5, t["accent"], ls=2.2, upper=True)
        x = 180
        for j, it in enumerate(items):
            x += c.text(x, y + 3, it, "nr", 22, t["text"])
            if j < len(items) - 1:
                x += 12
                x += c.text(x, y + 3, "/", "nr", 22, t["faint"])
                x += 12
        c.line(0, y + 25.5, W, y + 25.5, t["line"])
    return c.render()


# ---------------------------------------------------------------- footer

def footer(t):
    W, H = 1000, 250
    c = Canvas(W, H, "Have a project in mind? Write to contact@moniir.dev or visit moniir.dev")
    c.text(-3, 92, "Have a project", "ts", 64, t["text"], ls=-1.6)
    w = c.text(-3, 166, "in mind?", "ts", 64, t["text"], ls=-1.6)
    c.text(w + 22, 164, "Let’s talk.", "ni", 40, t["accent"], ls=-0.4)
    c.text(W, 124, "contact@moniir.dev", "nr", 20, t["text"], anchor="end")
    c.line(W - c.width("contact@moniir.dev", "nr", 20), 133.5, W, 133.5, t["line2"])
    c.text(W - 20, 164, "moniir.dev", "nr", 20, t["text"], anchor="end")
    c.arrow(W - 11, 151, t["text"])
    c.line(0, 210.5, W, 210.5, t["line2"])
    c.text(0, 238, "WordPress · Breakdance · WooCommerce", "ts", 10.5, t["muted"], ls=2.2, upper=True)
    c.text(W, 238, "Since 2019", "ts", 10.5, t["muted"], anchor="end", ls=2.2, upper=True)
    return c.render()


# ---------------------------------------------------------------- write

def main():
    v = load_versions()
    if "--fetch" in sys.argv:
        v = fetch_versions(v)
    os.makedirs(OUT, exist_ok=True)
    for f in os.listdir(OUT):
        if f.endswith(".svg"):
            os.remove(os.path.join(OUT, f))
    items = work(v)
    for name, t in THEMES.items():
        files = {
            f"hero-{name}.svg": hero(t),
            f"section-work-{name}.svg": section(t, "I", "Selected work", "Plugins, products and tools"),
            f"section-toolkit-{name}.svg": section(t, "II", "Toolkit", "What I reach for"),
            f"section-contact-{name}.svg": section(t, "III", "Contact", "Open to new projects"),
            f"toolkit-{name}.svg": toolkit(t),
            f"footer-{name}.svg": footer(t),
        }
        for i, w in enumerate(items, 1):
            files[f"work-{w['slug']}-{name}.svg"] = row(t, i, w, i == len(items))
        for fn, s in files.items():
            open(os.path.join(OUT, fn), "w", encoding="utf-8").write(s)
    print("Built with versions:", v)


if __name__ == "__main__":
    main()
