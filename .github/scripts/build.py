"""Build the profile README artwork (dark + light SVGs) from one data source.

Usage: python .github/scripts/build.py            # use versions in versions.json
       python .github/scripts/build.py --fetch    # refresh versions first
"""
import json
import os
import sys
import urllib.request
from xml.sax.saxutils import escape

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "assets")
VERSIONS = os.path.join(ROOT, ".github", "versions.json")

SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Inter, Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, monospace"

THEMES = {
    "dark": dict(
        bg="#0A0A0C", surface="#121216", surface2="#18181E", border="#24242C", border2="#2E2E38",
        text="#F5F5F7", muted="#8C8C99", faint="#55555F", dot="#1E1E25",
        accent="#FF6B1A", accent_soft="#FF6B1A22", accent_line="#FF6B1A55", green="#3DDC84",
    ),
    "light": dict(
        bg="#FBFBF9", surface="#FFFFFF", surface2="#F3F3EF", border="#E6E6E0", border2="#D9D9D2",
        text="#111114", muted="#66666F", faint="#A3A3AB", dot="#E4E4DE",
        accent="#F05A0A", accent_soft="#F05A0A18", accent_line="#F05A0A44", green="#16A34A",
    ),
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


def cards(v):
    return [
        dict(slug="breakui-pro", kind="PREMIUM PLUGIN", title="BreakUI Pro",
             lines=["Add-on elements for Breakdance: Smart Video,", "Contact Hub, Audio Player, PDF Viewer, Ask Buddy."],
             pill=f"v{v['breakui-pro']}", tags=["Breakdance", "PHP", "JS"], icon="layers"),
        dict(slug="preview-pass", kind="FREE · WORDPRESS.ORG", title="BreakUI Preview Pass",
             lines=["Send clients a private preview link to a draft.", "No login, no staging site. Every feature free."],
             pill=f"v{v['breakui-preview-pass']}", tags=["WordPress", "Open source"], icon="link"),
        dict(slug="breakui", kind="MARKETPLACE", title="BreakUI",
             lines=["Ready-made Breakdance templates and sections", "for agencies and freelancers."],
             pill="Live", tags=["Templates", "Breakdance"], icon="grid"),
        dict(slug="wpbuilderpros", kind="STUDIO", title="WPBuilderPros",
             lines=["WordPress build studio: new sites, redesigns,", "WooCommerce, speed, SEO and fixes."],
             pill="Live", tags=["WooCommerce", "Speed", "SEO"], icon="brick"),
        dict(slug="typeset", kind="FREE TOOL", title="Typeset",
             lines=["Fluid typography generator. Build a type", "scale and copy the CSS clamp() values."],
             pill="Live", tags=["CSS", "clamp()"], icon="type"),
        dict(slug="hire", kind="AVAILABLE NOW", title="Your project next",
             lines=["Need a WordPress or Breakdance site built,", "fixed or made faster? Let's talk."],
             pill="moniir.dev", tags=["Hire me"], icon="arrow", cta=True),
    ]


# ---------------------------------------------------------------- helpers

def svg(w, h, body, title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-label="{escape(title)}" fill="none">\n<title>{escape(title)}</title>\n{body}\n</svg>\n')


def dots(t, w, h, pid):
    return (f'<defs><pattern id="{pid}" width="22" height="22" patternUnits="userSpaceOnUse">'
            f'<circle cx="1" cy="1" r="1" fill="{t["dot"]}"/></pattern></defs>'
            f'<rect width="{w}" height="{h}" fill="url(#{pid})"/>')


def text(x, y, s, size, fill, weight=400, font=SANS, anchor="start", ls=0, extra=""):
    return (f'<text x="{x}" y="{y}" font-family="{font}" font-size="{size}" font-weight="{weight}" '
            f'fill="{fill}" text-anchor="{anchor}" letter-spacing="{ls}" {extra}>{escape(s)}</text>')


def mono_w(s, size):
    return len(s) * size * 0.61


def sans_w(s, size, weight=400):
    return len(s) * size * (0.56 if weight >= 600 else 0.52)


# ---------------------------------------------------------------- hero

def hero(t):
    W, H = 1000, 440
    rows = [("Smart Video", "BETA"), ("Contact Hub", ""), ("Audio Player", ""),
            ("PDF Viewer", ""), ("Website Preview", "BETA"), ("Ask Buddy", "BETA")]
    px, py, pw = 618, 92, 330
    b = []
    b.append(f'''<style>
  .pulse {{ animation: pulse 2.4s ease-in-out infinite; transform-origin: 63px 133px; }}
  @keyframes pulse {{ 0%,100% {{ opacity:.35; transform: scale(1); }} 50% {{ opacity:0; transform: scale(2.4); }} }}
  .caret {{ animation: blink 1.1s steps(1) infinite; }}
  @keyframes blink {{ 50% {{ opacity:0; }} }}
  .sel {{ animation: sel 9s cubic-bezier(.65,0,.35,1) infinite; }}
  @keyframes sel {{
    0%,14% {{ transform: translateY(0px); }} 18%,30% {{ transform: translateY(38px); }}
    34%,46% {{ transform: translateY(76px); }} 50%,62% {{ transform: translateY(114px); }}
    66%,78% {{ transform: translateY(152px); }} 82%,96% {{ transform: translateY(190px); }} 100% {{ transform: translateY(0px); }}
  }}
  .cur {{ animation: cur 9s cubic-bezier(.65,0,.35,1) infinite; }}
  @keyframes cur {{
    0%,14% {{ transform: translate(0px,0px); }} 18%,30% {{ transform: translate(-14px,38px); }}
    34%,46% {{ transform: translate(6px,76px); }} 50%,62% {{ transform: translate(-20px,114px); }}
    66%,78% {{ transform: translate(2px,152px); }} 82%,96% {{ transform: translate(-10px,190px); }} 100% {{ transform: translate(0px,0px); }}
  }}
  @media (prefers-reduced-motion: reduce) {{ .pulse,.caret,.sel,.cur {{ animation: none; }} }}
</style>''')
    b.append(f'<defs><radialGradient id="glow" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" '
             f'gradientTransform="translate(120 40) rotate(30) scale(520 300)">'
             f'<stop stop-color="{t["accent"]}" stop-opacity=".16"/><stop offset="1" stop-color="{t["accent"]}" stop-opacity="0"/></radialGradient>'
             f'<clipPath id="frame"><rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="20"/></clipPath></defs>')
    b.append(f'<g clip-path="url(#frame)"><rect width="{W}" height="{H}" fill="{t["bg"]}"/>')
    b.append(dots(t, W, H, "d").replace("<defs>", "<defs>", 1))
    b.append(f'<rect width="{W}" height="{H}" fill="url(#glow)"/>')
    # window bar
    b.append(f'<rect width="{W}" height="44" fill="{t["surface"]}"/><path d="M0 44.5H{W}" stroke="{t["border"]}"/>')
    for i, c in enumerate(["#FF5F57", "#FEBC2E", "#28C840"]):
        b.append(f'<circle cx="{26 + i*20}" cy="22" r="6" fill="{c}"/>')
    b.append(text(W/2, 27, "moniir.dev  —  ~/developermonir", 12.5, t["muted"], font=MONO, anchor="middle"))
    # status pill
    pill = "Available for new projects"
    pwid = 40 + mono_w(pill, 12.5)
    b.append(f'<rect x="48" y="118" width="{pwid}" height="30" rx="15" fill="{t["surface"]}" stroke="{t["border2"]}"/>')
    b.append(f'<circle class="pulse" cx="63" cy="133" r="4" fill="{t["green"]}"/><circle cx="63" cy="133" r="4" fill="{t["green"]}"/>')
    b.append(text(76, 137.5, pill, 12.5, t["text"], font=MONO))
    # name + role
    b.append(text(46, 212, "Moniruzzaman Monir", 54, t["text"], 700, ls=-1.6))
    b.append(text(48, 256, "WordPress & Breakdance developer.", 23, t["text"], 500, ls=-0.3))
    b.append(text(48, 288, "I build plugins, templates and fast websites", 19, t["muted"], ls=-0.2))
    b.append(f'<text x="48" y="314" font-family="{SANS}" font-size="19" fill="{t["muted"]}" letter-spacing="-0.2">'
             f'for agencies and businesses worldwide<tspan class="caret" fill="{t["accent"]}" font-weight="300" dx="3">|</tspan></text>')
    # metrics
    parts = []
    for i, (num, lab) in enumerate([("7+", "years"), ("700+", "websites"), ("120+", "clients")]):
        parts.append(f'<tspan dx="{0 if i == 0 else 28}" font-family="{SANS}" font-size="20" font-weight="700" fill="{t["text"]}" letter-spacing="-0.4">{num}</tspan>'
                     f'<tspan dx="7" font-family="{MONO}" font-size="13" fill="{t["muted"]}">{lab}</tspan>')
    b.append(f'<text x="48" y="376">{"".join(parts)}</text>')
    # layers panel
    ph = 38 * len(rows) + 62
    b.append(f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="14" fill="{t["surface"]}" stroke="{t["border2"]}"/>')
    b.append(text(px + 18, py + 28, "ELEMENTS", 11, t["muted"], 600, MONO, ls=1.2))
    b.append(text(px + pw - 18, py + 28, "BreakUI Pro", 11, t["accent"], 600, MONO, anchor="end"))
    b.append(f'<path d="M{px} {py+44.5}H{px+pw}" stroke="{t["border"]}"/>')
    ry0 = py + 52
    b.append(f'<g class="sel"><rect x="{px+8}" y="{ry0}" width="{pw-16}" height="32" rx="8" fill="{t["accent_soft"]}" stroke="{t["accent_line"]}"/></g>')
    for i, (name, tag) in enumerate(rows):
        ry = ry0 + i * 38
        b.append(f'<rect x="{px+20}" y="{ry+8}" width="16" height="16" rx="4" stroke="{t["faint"]}" stroke-width="1.4"/>')
        b.append(f'<path d="M{px+24} {ry+16}h8" stroke="{t["faint"]}" stroke-width="1.4" stroke-linecap="round"/>')
        b.append(text(px + 48, ry + 21, name, 14, t["text"], 500))
        if tag:
            b.append(f'<rect x="{px+pw-62}" y="{ry+8}" width="42" height="17" rx="8.5" stroke="{t["border2"]}"/>')
            b.append(text(px + pw - 41, ry + 20, tag, 9.5, t["muted"], 600, MONO, anchor="middle", ls=0.6))
    # cursor
    cx, cy = px + 200, ry0 + 20
    b.append(f'<g class="cur"><path transform="translate({cx} {cy})" d="M0 0 L0 17 L4.6 12.8 L7.8 19.6 L10.6 18.4 L7.4 11.6 L13.2 11.4 Z" '
             f'fill="{t["text"]}" stroke="{t["bg"]}" stroke-width="1.2" stroke-linejoin="round"/></g>')
    b.append('</g>')
    b.append(f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="20" stroke="{t["border"]}"/>')
    return svg(W, H, "\n".join(b), "Moniruzzaman Monir — WordPress & Breakdance developer")


# ---------------------------------------------------------------- stats

def stats(t):
    W, H = 1000, 128
    items = [("7+", "Years in WordPress"), ("700+", "Websites shipped"),
             ("120+", "Clients worldwide"), ("350+", "Fiverr projects")]
    b = [f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="16" fill="{t["surface"]}" stroke="{t["border"]}"/>']
    cw = W / len(items)
    for i, (n, l) in enumerate(items):
        cx = cw * i + cw / 2
        if i:
            b.append(f'<path d="M{cw*i} 28V{H-28}" stroke="{t["border"]}"/>')
        b.append(text(cx, 66, n, 34, t["text"], 700, anchor="middle", ls=-1))
        b.append(text(cx, 94, l.upper(), 11, t["muted"], 500, MONO, anchor="middle", ls=1))
    return svg(W, H, "\n".join(b), "7+ years, 700+ websites, 120+ clients, 350+ Fiverr projects")


# ---------------------------------------------------------------- cards

ICONS = {
    "layers": 'M0 10 L18 0 L36 10 L18 20 Z M0 18 L18 28 L36 18 M0 26 L18 36 L36 26',
    "link": 'M15 21 a7 7 0 0 1 0-10 l5-5 a7 7 0 0 1 10 10 l-3 3 M21 15 a7 7 0 0 1 0 10 l-5 5 a7 7 0 0 1-10-10 l3-3',
    "grid": 'M2 2h14v14H2z M20 2h14v14H20z M2 20h14v14H2z M20 20h14v14H20z',
    "brick": 'M1 3h34v9H1z M1 14h16v9H1z M19 14h16v9H19z M1 25h34v9H1z',
    "type": 'M3 6V2h24v4 M15 2v32 M10 34h10 M24 16h10 M29 16v18',
    "arrow": 'M4 32 L32 4 M12 4 H32 V24',
}


def card(t, c):
    W, H = 490, 236
    cta = c.get("cta")
    b = []
    fill = t["accent_soft"] if cta else t["surface"]
    stroke = t["accent_line"] if cta else t["border"]
    b.append(f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="16" fill="{t["bg"]}"/>')
    b.append(f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="16" fill="{fill}" stroke="{stroke}"/>')
    b.append(text(28, 42, c["kind"], 11, t["accent"], 600, MONO, ls=1.2))
    b.append(f'<g transform="translate({W-64} 26)"><path d="{ICONS[c["icon"]]}" stroke="{t["accent"] if cta else t["faint"]}" '
             f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></g>')
    b.append(text(26, 86, c["title"], 27, t["text"], 700, ls=-0.7))
    for i, ln in enumerate(c["lines"]):
        b.append(text(28, 120 + i * 23, ln, 15, t["muted"]))
    # footer
    b.append(f'<path d="M0 {H-58.5}H{W}" stroke="{t["border"]}"/>')
    x = 28
    pw = mono_w(c["pill"], 12) + 22
    pfill = t["accent"] if cta else t["surface2"]
    pcol = "#FFFFFF" if cta else t["text"]
    b.append(f'<rect x="{x}" y="{H-42}" width="{pw}" height="26" rx="13" fill="{pfill}" stroke="{t["border2"] if not cta else pfill}"/>')
    b.append(text(x + pw / 2, H - 24.5, c["pill"], 12, pcol, 600, MONO, anchor="middle"))
    x += pw + 10
    for tag in c["tags"]:
        tw = mono_w(tag, 11.5) + 18
        b.append(f'<rect x="{x}" y="{H-42}" width="{tw}" height="26" rx="13" stroke="{t["border2"]}"/>')
        b.append(text(x + tw / 2, H - 24.5, tag, 11.5, t["muted"], 500, MONO, anchor="middle"))
        x += tw + 8
    b.append(f'<path d="M{W-46} {H-20} L{W-30} {H-36} M{W-42} {H-36} H{W-30} V{H-24}" stroke="{t["text"]}" '
             f'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>')
    return svg(W, H, "\n".join(b), f'{c["title"]} — {" ".join(c["lines"])}')


# ---------------------------------------------------------------- stack

STACK = [
    ("Build", ["WordPress", "Breakdance", "WooCommerce", "Divi", "Gutenberg"]),
    ("Code", ["PHP", "JavaScript", "TypeScript", "Twig", "CSS", "MySQL"]),
    ("Ship", ["Figma", "Git", "Hostinger", "Cloudflare", "WP Engine", "PageSpeed"]),
]


def stack(t):
    W, H = 1000, 196
    b = [f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="16" fill="{t["surface"]}" stroke="{t["border"]}"/>']
    for r, (label, items) in enumerate(STACK):
        y = 38 + r * 52
        if r:
            b.append(f'<path d="M28 {y-14.5}H{W-28}" stroke="{t["border"]}" stroke-dasharray="2 5"/>')
        b.append(text(28, y + 19, label.upper(), 11, t["accent"], 600, MONO, ls=1.4))
        x = 120
        for it in items:
            w = len(it) * 14 * 0.56 + 30
            b.append(f'<rect x="{x}" y="{y}" width="{w}" height="30" rx="8" fill="{t["surface2"]}" stroke="{t["border2"]}"/>')
            b.append(text(x + w / 2, y + 20, it, 14, t["text"], 500, anchor="middle"))
            x += w + 10
    return svg(W, H, "\n".join(b), "Stack: " + ", ".join(i for _, its in STACK for i in its))


# ---------------------------------------------------------------- section label

def label(t, num, name):
    W, H = 1000, 40
    b = [text(0, 26, num, 12, t["accent"], 600, MONO, ls=1),
         text(34, 26, name.upper(), 12, t["text"], 600, MONO, ls=2)]
    x = 34 + mono_w(name.upper(), 12) + len(name) * 2 + 18
    b.append(f'<path d="M{x} 21.5H{W}" stroke="{t["border"]}"/>')
    return svg(W, H, "\n".join(b), name)


# ---------------------------------------------------------------- footer

def footer(t):
    W, H = 1000, 150
    b = [f'<defs><linearGradient id="g" x1="0" y1="0" x2="{W}" y2="0" gradientUnits="userSpaceOnUse">'
         f'<stop stop-color="{t["accent"]}" stop-opacity=".14"/><stop offset=".6" stop-color="{t["accent"]}" stop-opacity="0"/></linearGradient></defs>',
         f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="16" fill="{t["surface"]}"/>',
         f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="16" fill="url(#g)" stroke="{t["border"]}"/>',
         text(36, 66, "Have a WordPress project in mind?", 28, t["text"], 700, ls=-0.7),
         text(38, 100, "Breakdance builds, WooCommerce stores, redesigns, speed and fixes.", 15, t["muted"])]
    bw = 210
    bx = W - bw - 36
    b.append(f'<rect x="{bx}" y="52" width="{bw}" height="48" rx="24" fill="{t["accent"]}"/>')
    b.append(text(bx + bw / 2 - 8, 81.5, "moniir.dev", 16, "#FFFFFF", 700, anchor="middle"))
    b.append(f'<path d="M{bx+bw-44} 82 L{bx+bw-32} 70 M{bx+bw-41} 70 H{bx+bw-32} V79" stroke="#FFFFFF" stroke-width="2" '
             f'stroke-linecap="round" stroke-linejoin="round"/>')
    return svg(W, H, "\n".join(b), "Have a WordPress project in mind? moniir.dev")


# ---------------------------------------------------------------- write

def main():
    v = load_versions()
    if "--fetch" in sys.argv:
        v = fetch_versions(v)
    os.makedirs(OUT, exist_ok=True)
    for name, t in THEMES.items():
        files = {
            f"hero-{name}.svg": hero(t),
            f"stats-{name}.svg": stats(t),
            f"stack-{name}.svg": stack(t),
            f"footer-{name}.svg": footer(t),
            f"label-work-{name}.svg": label(t, "01", "Selected work"),
            f"label-stack-{name}.svg": label(t, "02", "Toolkit"),
            f"label-contact-{name}.svg": label(t, "03", "Work with me"),
        }
        for c in cards(v):
            files[f"card-{c['slug']}-{name}.svg"] = card(t, c)
        for fn, s in files.items():
            open(os.path.join(OUT, fn), "w", encoding="utf-8").write(s)
    print("Built with versions:", v)


if __name__ == "__main__":
    main()
