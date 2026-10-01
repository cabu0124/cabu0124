#!/usr/bin/env python3
"""Generates the Solo Leveling style "System" SVGs used by the profile README.

Run from anywhere:  python3 assets/source/build.py   (needs Pillow)
Edit the content constants below and re-run to refresh every asset.
Stack icons are cached in assets/source/icons (skillicons.dev + Simple Icons).
"""
import base64
import math
import random
import re
from datetime import date
from pathlib import Path
from xml.sax.saxutils import escape

from PIL import Image

HERE = Path(__file__).resolve().parent
OUT = HERE.parent
TODAY = date.today()
VERSION = "v3"  # bump on visual changes: new file names bust GitHub/VS Code image caches

# ================================================================ content

PLAYER_ID = "cabu0124"
NAME = "Carlos Andres Castano"
ROLE = "Software Engineer & Technical Leader"
CAREER_START = date(2015, 8, 1)  # level = full years since this date

STATUS = [
    ("guild:", "Teleperformance · remote"),
    ("base:", "Vancouver, BC, Canada"),
    ("lang:", "Spanish (native) · English (C1)"),
]
SKILLS = [
    ("backend/", ".NET · C# · ASP.NET · REST APIs · Microservices"),
    ("frontend/", "Angular · React · TypeScript"),
    ("data/", "SQL Server · PostgreSQL · Cosmos DB · MongoDB"),
    ("cloud/", "Azure · Kubernetes · Docker"),
    ("devops/", "CI/CD pipelines · Git · GitHub · Azure DevOps"),
    ("ai/", "Claude Code · Copilot · Ollama · coding agents"),
    ("practices/", "SDD · architecture · code review · mentoring"),
]
OPEN_TO = "open to: architecture · leadership · AI-assisted dev"

# 0-100, clockwise from the top
STATS = [
    ("BACKEND", 90),
    ("CLOUD", 82),
    ("DEVOPS & CI/CD", 85),
    ("LEADERSHIP", 90),
    ("AI-ASSISTED", 86),
    ("FRONTEND", 78),
]

QUESTS = [
    ("Lead SDD adoption across the team", "ONGOING"),
    ("Mentor 8+ developers", "ONGOING"),
    ("Agentic dev with Claude Code & Copilot", "ONGOING"),
    ("PG Diploma, IT Project Mgmt @ VCC", "ONGOING"),
    ("Music-learning game (Unity / Godot)", "ONGOING"),
    ("Release the SDD spec + project templates", "CLEARED"),
    ("M.S. in Software Engineering", "CLEARED"),
]
QUEST_NOTE = ("NOTICE: LinkedIn is the fastest way to reach the player.",
              "Messages there usually get a reply within a day.")

# (category, [(label, icon)]); icon "skill:<id>" comes from skillicons, anything else is a local tile.
# The first category is rendered as the highlighted "legendary" row.
INVENTORY = [
    ("ai/", [("Claude Code", "claude"), ("Copilot", "copilot"), ("Ollama", "ollama")]),
    ("backend/", [("C#", "skill:cs"), (".NET", "skill:dotnet"), ("Node.js", "skill:nodejs"), ("Python", "skill:py")]),
    ("frontend/", [("Angular", "skill:angular"), ("React", "skill:react"), ("TypeScript", "skill:ts")]),
    ("cloud-devops/", [("Azure", "skill:azure"), ("Azure DevOps", "azuredevops"), ("Kubernetes", "skill:kubernetes"),
                       ("Docker", "skill:docker"), ("Git", "skill:git"), ("GitHub", "skill:github")]),
    ("data/", [("SQL Server", "sqlserver"), ("PostgreSQL", "skill:postgres"), ("Cosmos DB", "cosmosdb"),
               ("MongoDB", "skill:mongodb"), ("Firebase", "skill:firebase")]),
    ("tools/", [("Jira", "jira"), ("Postman", "skill:postman"), ("Visual Studio", "skill:visualstudio"),
                ("VS Code", "skill:vscode"), ("LaTeX", "skill:latex")]),
    ("gamedev-design/", [("Unity", "skill:unity"), ("Godot", "skill:godot"), ("Figma", "skill:figma"),
                         ("Photoshop", "skill:ps")]),
]
AI_PERKS = ["coding agents", "agentic workflows", "local LLMs", "spec → code with AI"]

REPOS = {
    "quest-spec": {
        "name": "sdd-spec-template",
        "sub": "The Spec Repository · WHAT & WHY",
        "objective": ["Keep one technology-agnostic spec per product",
                      "story as the single source of truth."],
        "rewards": ["One spec feeds many dev repositories",
                    "Status and decisions live in one place",
                    "Works with any coding agent"],
        "flow": ["spec.md", "/sdd-sync", "web · api · infra"],
    },
    "quest-project": {
        "name": "sdd-project-template",
        "sub": "The development repository · HOW",
        "objective": ["Turn approved specs into a plan, tasks and",
                      "code, one feature at a time."],
        "rewards": ["Rule 1: no code without an approved spec",
                    "Same layout for web, API, infra, mobile",
                    "Works with any coding agent"],
        "flow": ["/sdd-plan", "/sdd-tasks", "/sdd-implement"],
    },
}

KPIS = [("10+", "YEARS IN THE FIELD"), ("5", "GATES CLEARED"), ("8+", "DEVS MENTORED"),
        ("3", "GDS INTEGRATED"), ("2", "OSS TEMPLATES")]

# rank, role, guild, start, end (None = now), loot
CAREER = [
    ("A", "Software Specialist & Tech Lead", "Teleperformance", (2022, 2), None,
     "SDD rollout · 8+ devs mentored · Jira↔GitHub flow · AI agents"),
    ("B", "Software Specialist", "Teleperformance", (2021, 3), (2022, 1),
     "Amadeus · Sabre · Navitaire GDS integrations"),
    ("C", "Software Developer Analyst", "Juniper", (2018, 5), (2021, 2),
     "Payment gateways on an internal Hub API"),
    ("D", "Front-End Developer", "Juniper", (2016, 9), (2018, 4),
     "Client websites · .NET · SCSS · Handlebars"),
    ("E", "Junior Developer", "VOV Solutions", (2015, 8), (2016, 8),
     "Full PBX system · Android apps · Node.js"),
]
# badge, program, school, start, end (None = in progress), tag
TRAINING = [
    ("PG", "Postgraduate Diploma, IT Project Management", "Vancouver Community College", (2026, 1), None, "IN PROGRESS"),
    ("EN", "General English", "Bayswater Vancouver", (2024, 1), (2025, 12), ""),
    ("M.S.", "M.S. in Software Engineering", "Universidad Javeriana Cali", (2022, 1), (2024, 12), "THESIS"),
    ("PG", "Postgraduate Diploma, Software Engineering", "Universidad Javeriana Cali", (2022, 1), (2023, 12), ""),
    ("B.S.", "B.S. in Electronic Engineering", "Universidad de San Buenaventura Cali", (2009, 1), (2015, 12), "THESIS"),
]

# ================================================================ style

C = {
    "bg": "#0b0e1a", "panel": "#10142a", "panel2": "#151a33", "line": "#262c4a", "edge1": "#a78bfa",
    "edge2": "#38bdf8", "border": "#8b7bf0", "cyan": "#67e8f9", "ice": "#e0f2fe", "text": "#c9d4ea",
    "muted": "#7d86a8", "violet": "#a78bfa", "purple": "#7c3aed", "gold": "#fcd34d", "pink": "#f472b6",
    "green": "#4ade80",
}
RANK = {"E": C["muted"], "D": C["green"], "C": C["cyan"], "B": C["violet"], "A": C["gold"]}
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"
CW = 0.6  # monospace advance per font-size unit

DEFS = f"""<defs>
<linearGradient id="edge" x1="0" x2="1" y1="0" y2="1">
  <stop stop-color="{C['edge1']}"/><stop offset="1" stop-color="{C['edge2']}"/>
</linearGradient>
<linearGradient id="bar" x1="0" x2="1"><stop stop-color="{C['purple']}"/><stop offset="1" stop-color="{C['cyan']}"/></linearGradient>
<radialGradient id="aura"><stop stop-color="{C['purple']}" stop-opacity=".45"/>
  <stop offset=".6" stop-color="{C['purple']}" stop-opacity=".12"/><stop offset="1" stop-color="{C['purple']}" stop-opacity="0"/></radialGradient>
<filter id="glow" x="-20%" y="-30%" width="140%" height="160%">
  <feGaussianBlur stdDeviation="2.2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
</filter>
</defs>"""

STYLE = f"""
text{{font-family:{MONO};fill:{C['text']}}}
.blink{{animation:blink 1.4s steps(1) infinite}}
.pulse{{animation:pulse 2s ease-in-out infinite}}
@keyframes blink{{50%{{opacity:0}}}}
@keyframes pulse{{50%{{opacity:.35}}}}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}}}
"""


def svg(w, h, title, body):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img">'
        f"<title>{escape(title)}</title><style>{STYLE}</style>{DEFS}{body}</svg>\n"
    )


def t(x, y, s, size=16, fill=None, anchor="start", weight=400, extra=""):
    a = f'x="{x:g}" y="{y:g}" font-size="{size}"'
    if fill:
        a += f' style="fill:{fill}"'
    if weight != 400:
        a += f' font-weight="{weight}"'
    if anchor != "start":
        a += f' text-anchor="{anchor}"'
    return f"<text {a}{extra}>{escape(s)}</text>"


def shell(w, h, title, right=""):
    """Outer card in the style of the reference `whoami` window."""
    o = [
        f'<rect width="{w}" height="{h}" rx="18" fill="{C["bg"]}"/>',
        f'<rect x="9" y="9" width="{w - 18}" height="{h - 18}" rx="13" fill="none" stroke="url(#edge)" stroke-width="2"/>',
        t(32, 41, "◆", 15, C["cyan"], extra=' filter="url(#glow)"'),
        t(54, 41, title, 15, C["muted"]),
        f'<path d="M29 58H{w - 29}" stroke="{C["line"]}"/>',
    ]
    if right:
        o.append(t(w - 32, 41, right, 13, C["muted"], anchor="end"))
    return "".join(o)


def panel(x, y, w, h, stroke=None, fill=None):
    return (f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" rx="9" fill="{fill or C["panel"]}" '
            f'stroke="{stroke or C["border"]}" stroke-width="1.5"/>')


def chip(x, y, label, color, size=11, fill_opacity=.14):
    w = len(label) * size * CW + 16
    return (f'<rect x="{x:g}" y="{y - size - 3:g}" width="{w:g}" height="{size + 9}" rx="4" fill="{color}" '
            f'fill-opacity="{fill_opacity}" stroke="{color}" stroke-opacity=".7"/>'
            + t(x + w / 2, y + 1, label, size, color, anchor="middle", weight=700)), w


def prompt(x, y, cmd, size=20):
    return t(x, y, f"❯ {cmd}", size, C["cyan"], weight=700)


# ================================================================ portrait

CYCLE, FADE, SCAN_END = 18.5, 1.3, 2.6
PORTRAIT_OUT, PORTRAIT_IN = 2.9, 16.8
# silhouette (assets/source/silhouettes/<name>.png), caption, fade-in start, fade-out start
FORMS = [
    ("dotnet", "SKILL: .NET", 4.2, 7.0),
    ("kubernetes", "SKILL: KUBERNETES", 8.4, 11.2),
    ("claude", "SKILL: CLAUDE CODE", 12.6, 15.4),
]


def key_times(*secs):
    return ";".join(f"{v / CYCLE:.4f}" for v in (0, *secs)) + ";1"


def stipple_portrait(cols):
    """Sparse 1-bit Floyd-Steinberg stipple of the portrait; returns dot list and size."""
    src = Image.open(HERE / "portrait.png").convert("RGBA")
    rows = round(cols * src.height / src.width)
    img = src.resize((cols, rows), Image.LANCZOS)
    alpha, lum = img.getchannel("A"), img.convert("L")

    # brighter skin = denser dots; the last rows dissolve instead of ending on a hard edge
    lo, hi, fade_from = 25, 235, 0.82
    tone = Image.new("L", (cols, rows))
    for y in range(rows):
        fade = min(1, (1 - y / rows) / (1 - fade_from))
        for x in range(cols):
            a = alpha.getpixel((x, y)) / 255
            v = (min(max(lum.getpixel((x, y)), lo), hi) - lo) / (hi - lo)
            tone.putpixel((x, y), round(255 * a * fade * (0.05 + 0.36 * v ** 1.3)))
    bits = tone.convert("1")
    return [(x, y) for y in range(rows) for x in range(cols) if bits.getpixel((x, y))], cols, rows


def stipple_silhouette(name, w, h, rng, density=.2):
    """Random stipple inside a logo mask, centered in a w×h box."""
    mask = Image.open(HERE / "silhouettes" / f"{name}.png").getchannel("A")
    ox, oy = (w - mask.width) // 2, (h - mask.height) // 2 - 12
    return [(x + ox, y + oy) for y in range(mask.height) for x in range(mask.width)
            if mask.getpixel((x, y)) > 128 and rng.random() < density]


def particles(dots, w, h, rng, show, hide, starts_visible, tile=10):
    """Group dots in jittered clusters that drift in/out and fade, like a particle dissolve."""
    clusters = {}
    for x, y in dots:
        key = (int(x + rng.uniform(-3, 3)) // tile, int(y + rng.uniform(-3, 3)) // tile)
        clusters.setdefault(key, []).append(f"M{x} {y}h1")

    out = []
    for (tx, ty), d in clusters.items():
        ang = math.atan2(ty * tile - h * .45, tx * tile - w / 2) + rng.uniform(-.6, .6)

        def drift(a):
            dist = rng.uniform(5, 16)
            return f"{dist * math.cos(a):.1f} {dist * math.sin(a) - rng.uniform(2, 7):.1f}"

        a, b = drift(ang), drift(ang + rng.uniform(-1.2, 1.2))
        begin = rng.uniform(0, .6) + (ty * tile / h) * .5  # top goes first
        if starts_visible:  # fade out, stay hidden, come back
            kt, tr, op, base = key_times(hide, hide + FADE, show, show + FADE), f"0 0;0 0;{a};{a};0 0;0 0", "1;1;0;0;1;1", ""
        else:  # assemble, hold, scatter
            kt, tr, op, base = key_times(show, show + FADE, hide, hide + FADE), f"{a};{a};0 0;0 0;{b};{b}", "0;0;1;1;0;0", ' opacity="0"'
        common = f'begin="{begin:.2f}s" dur="{CYCLE}s" repeatCount="indefinite" keyTimes="{kt}"'
        out.append(f'<path{base} d="{"".join(d)}">'
                   f'<animateTransform attributeName="transform" type="translate" {common} values="{tr}"/>'
                   f'<animate attributeName="opacity" {common} values="{op}"/></path>')
    return "".join(out)


def caption(x, y, label, show, hide, starts_visible):
    if starts_visible:
        kt, op, base = key_times(hide, hide + .5, show + .8, show + FADE), "1;1;0;0;1;1", ""
    else:
        kt, op, base = key_times(show + .8, show + FADE, hide, hide + .5), "0;0;1;1;0;0", ' opacity="0"'
    return (f'<text x="{x}" y="{y}" font-size="12" font-weight="700" text-anchor="middle" letter-spacing="2" '
            f'style="fill:{C["cyan"]}"{base}>{escape(label)}'
            f'<animate attributeName="opacity" dur="{CYCLE}s" repeatCount="indefinite" keyTimes="{kt}" values="{op}"/></text>')


# ================================================================ profile banner


def level_and_exp(today):
    years = today.year - CAREER_START.year - ((today.month, today.day) < (CAREER_START.month, CAREER_START.day))
    last = CAREER_START.replace(year=CAREER_START.year + years)
    nxt = CAREER_START.replace(year=CAREER_START.year + years + 1)
    return years, (today - last).days / (nxt - last).days


def profile():
    W, H = 1180, 620
    lvl, exp = level_and_exp(TODAY)
    o = [shell(W, H, f"{PLAYER_ID} · system · player profile")]
    o.append(f'<circle cx="{W - 98}" cy="36" r="5" fill="{C["cyan"]}" class="blink"/>')
    o.append(t(W - 32, 41, "online", 13, C["muted"], anchor="end"))

    # left: scan panel
    px, py, pw, ph = 29, 78, 420, 512
    o.append(panel(px, py, pw, ph))
    rng = random.Random(124)
    dots, dw, dh = stipple_portrait(cols=380)
    n = len(dots)
    layers = particles(dots, dw, dh, rng, PORTRAIT_IN, PORTRAIT_OUT, True)
    for name, _, show, hide in FORMS:
        layers += particles(stipple_silhouette(name, dw, dh, rng), dw, dh, rng, show, hide, False)
    o.append(t(px + 20, py + 30, "PLAYER.SCAN", 14, C["violet"], weight=700))
    o.append(t(px + pw - 20, py + 30, f"{dw}×{dh} / 1-BIT", 11, C["muted"], anchor="end"))
    o.append(f'<path d="M{px} {py + 46}H{px + pw}" stroke="{C["line"]}"/>')
    ox, oy = px + (pw - dw) // 2, py + 62
    o.append(f'<clipPath id="pc"><rect x="{px + 2}" y="{py + 48}" width="{pw - 4}" height="{ph - 96}"/></clipPath>')
    o.append(f'<ellipse cx="{ox + dw / 2}" cy="{oy + dh * .5}" rx="{dw * .55:.0f}" ry="{dh * .55:.0f}" fill="url(#aura)"/>')
    o.append(f'<linearGradient id="ink" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="0" y2="{dh}">'
             f'<stop offset=".15" stop-color="{C["ice"]}"/><stop offset=".55" stop-color="{C["cyan"]}"/>'
             f'<stop offset="1" stop-color="{C["violet"]}"/></linearGradient>')
    o.append(f'<g clip-path="url(#pc)"><g transform="translate({ox} {oy + .5})" stroke="url(#ink)" '
             f'shape-rendering="crispEdges">{layers}</g></g>')

    # scan line sweeps once per cycle, right before the portrait dissolves
    kt = f"0;{SCAN_END / CYCLE:.4f};{(SCAN_END + .01) / CYCLE:.4f};1"
    o.append(f'<rect x="{px + 1}" y="{oy}" width="{pw - 2}" height="2" fill="{C["cyan"]}" filter="url(#glow)" opacity="0">'
             f'<animateTransform attributeName="transform" type="translate" dur="{CYCLE}s" repeatCount="indefinite" '
             f'keyTimes="{kt}" values="0 0;0 {dh};0 {dh};0 {dh}"/>'
             f'<animate attributeName="opacity" dur="{CYCLE}s" repeatCount="indefinite" keyTimes="{kt}" values=".9;.9;0;0"/>'
             f'</rect>')
    k, x0, y0, x1, y1 = 12, px + 14, oy - 4, px + pw - 14, oy + dh + 4
    o.append(f'<path d="M{x0} {y0}h{k}M{x0} {y0}v{k}M{x1} {y0}h-{k}M{x1} {y0}v{k}M{x0} {y1}h{k}M{x0} {y1}v-{k}'
             f'M{x1} {y1}h-{k}M{x1} {y1}v-{k}" fill="none" stroke="{C["violet"]}" opacity=".6"/>')
    cap_x, cap_y = px + pw / 2, py + ph - 52
    o.append(caption(cap_x, cap_y, f"PLAYER: {PLAYER_ID.upper()}", PORTRAIT_IN, PORTRAIT_OUT, True))
    for _, label, show, hide in FORMS:
        o.append(caption(cap_x, cap_y, label, show, hide, False))
    o.append(t(px + 20, py + ph - 18, f"PTS {n:,} · FS/DITHER", 11, C["muted"]))
    o.append(t(px + pw - 20, py + ph - 18, "ARISE", 13, C["violet"], anchor="end", weight=700,
               extra=' letter-spacing="4" filter="url(#glow)"'))

    # right: status
    sx, sy, sw, sh = 469, 78, 682, 512
    L = sx + 21
    o.append(panel(sx, sy, sw, sh))
    o.append(prompt(L, sy + 33, "status"))
    handle = NAME.lower().replace(" ", "_")
    o.append(t(L, sy + 65, handle, 17, C["text"]))
    dash_x = L + len(handle) * 17 * CW + 12
    o.append(t(dash_x, sy + 65, "—", 17, C["muted"]))
    o.append(t(dash_x + 26, sy + 65, ROLE, 17, C["gold"]))
    o.append(f'<path d="M{L} {sy + 88}H{sx + sw - 21}" stroke="{C["line"]}"/>')

    V = L + 100
    y = sy + 118
    o.append(t(L, y, "level:", 16, C["muted"]))
    o.append(t(V, y, str(lvl), 16, C["ice"], weight=700))
    bx, bw = V + 40, 300
    o.append(f'<rect x="{bx}" y="{y - 10}" width="{bw}" height="8" rx="4" fill="{C["line"]}"/>')
    o.append(f'<rect x="{bx}" y="{y - 10}" width="{bw * exp:.0f}" height="8" rx="4" fill="url(#bar)" filter="url(#glow)"/>')
    o.append(t(bx + bw + 14, y, f"exp {exp:.0%} → lv {lvl + 1}", 13, C["muted"]))
    for label, value in STATUS:
        y += 29
        o.append(t(L, y, label, 16, C["muted"]))
        o.append(t(V, y, value, 16, C["violet"]))

    y += 50
    o.append(prompt(L, y, "ls skills/"))
    y += 8
    for label, value in SKILLS:
        y += 25
        o.append(t(L, y, label, 15, C["pink"]))
        o.append(t(L + 130, y, value, 15, C["text"]))

    by = sy + sh - 44
    o.append(f'<path d="M{sx} {by}H{sx + sw}" stroke="{C["line"]}"/>')
    o.append(f'<rect x="{L - 6}" y="{by + 11}" width="78" height="22" rx="3" fill="{C["cyan"]}"/>')
    o.append(t(L + 33, by + 26, "ONLINE", 11, C["bg"], anchor="middle", weight=700))
    o.append(t(L + 86, by + 27, "player.status", 12, C["text"], weight=600))
    o.append(t(sx + sw - 21, by + 27, OPEN_TO, 11, C["muted"], anchor="end"))

    return svg(W, H, f"System status window for {NAME}, level {lvl} {ROLE}", "".join(o))


# ================================================================ stats hexagon


def stats():
    W, H = 560, 500
    cx, cy, r = W / 2, 282, 120
    o = [shell(W, H, f"{PLAYER_ID} · stats", "self-assessed · 0–100")]

    for rad, dash, op in [(56, "60 26", .55), (104, "110 40 18 40", .35), (164, "190 60 30 60", .22)]:
        o.append(f'<circle cx="{cx}" cy="{cy}" r="{rad}" fill="none" stroke="{C["cyan"]}" '
                 f'stroke-opacity="{op}" stroke-dasharray="{dash}"/>')

    n = len(STATS)
    pts, vals = [], []
    for i, (_, val) in enumerate(STATS):
        a = math.radians(-90 + i * 360 / n)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
        vals.append((cx + r * val / 100 * math.cos(a), cy + r * val / 100 * math.sin(a)))
    poly = lambda ps: " ".join(f"{x:.1f},{y:.1f}" for x, y in ps)
    o.append(f'<polygon points="{poly(pts)}" fill="none" stroke="{C["line"]}" stroke-width="1.5"/>')
    o.append(f'<polygon points="{poly(vals)}" fill="{C["violet"]}" fill-opacity=".16" stroke="{C["violet"]}" '
             f'stroke-width="1.6" filter="url(#glow)"/>')

    for (name, val), (nx, ny) in zip(STATS, pts):
        o.append(f'<circle cx="{nx:.1f}" cy="{ny:.1f}" r="8" fill="{C["bg"]}" stroke="{C["cyan"]}" stroke-width="1.5"/>'
                 f'<circle cx="{nx:.1f}" cy="{ny:.1f}" r="3" fill="{C["cyan"]}"/>')
        if abs(nx - cx) < 1:  # top / bottom: stack label above or below
            ny1, ny2 = (ny - 38, ny - 16) if ny < cy else (ny + 30, ny + 52)
            o.append(t(nx, ny1, name, 14, C["text"], anchor="middle", weight=700))
            o.append(t(nx, ny2, str(val), 20, C["ice"], anchor="middle", weight=700))
        else:  # sides: label outside the node
            side, anchor = (1, "start") if nx > cx else (-1, "end")
            o.append(t(nx + 18 * side, ny - 4, name, 14, C["text"], anchor=anchor, weight=700))
            o.append(t(nx + 18 * side, ny + 18, str(val), 20, C["ice"], anchor=anchor, weight=700))

    hexa = poly([(cx + 26 * math.cos(math.radians(30 + k * 60)), cy - 8 + 26 * math.sin(math.radians(30 + k * 60)))
                 for k in range(6)])
    o.append(f'<polygon points="{hexa}" fill="{C["ice"]}"/>')
    o.append(f'<path d="M{cx} {cy - 20}V{cy + 4}M{cx - 9} {cy - 11}L{cx} {cy - 20}L{cx + 9} {cy - 11}" fill="none" '
             f'stroke="{C["bg"]}" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/>')
    o.append(f'<rect x="{cx - 22}" y="{cy + 26}" width="44" height="20" rx="10" fill="{C["bg"]}" stroke="{C["line"]}"/>')
    o.append(t(cx, cy + 41, "0", 13, C["gold"], anchor="middle", weight=700))
    summary = ", ".join(f"{s.title()} {v}" for s, v in STATS)
    return svg(W, H, f"Stats: {summary}", "".join(o))


# ================================================================ daily quest


def quest():
    W, H = 560, 500
    cx = W / 2
    o = [shell(W, H, f"{PLAYER_ID} · quest --daily")]
    o.append(panel(cx - 130, 80, 260, 44, C["cyan"]))
    o.append(f'<rect x="{cx - 116}" y="90" width="24" height="24" rx="3" fill="none" stroke="{C["ice"]}" stroke-width="1.5"/>')
    o.append(t(cx - 104, 108, "!", 16, C["ice"], anchor="middle", weight=700))
    o.append(t(cx + 16, 108, "QUEST INFO", 17, C["ice"], anchor="middle", weight=700, extra=' letter-spacing="4"'))
    o.append(t(cx, 156, "[Daily Quest: Growth Training has arrived.]", 13, C["cyan"], anchor="middle"))
    o.append(t(cx, 190, "GOALS", 15, C["text"], anchor="middle", weight=700, extra=' letter-spacing="3"'))
    o.append(f'<path d="M{cx - 30} 198H{cx + 30}" stroke="{C["text"]}"/>')

    y = 232
    for label, status in QUESTS:
        done = status == "CLEARED"
        color = C["gold"] if done else C["cyan"]
        o.append(t(32, y, label, 13, C["text"]))
        o.append(f'<rect x="{W - 128}" y="{y - 11}" width="13" height="13" rx="2" fill="none" stroke="{color}"/>')
        if done:
            o.append(f'<path d="M{W - 125} {y - 5}l3 3l5 -8" fill="none" stroke="{color}" stroke-width="2"/>')
        o.append(t(W - 30, y, f"[{status}]", 12, color, anchor="end", weight=700))
        y += 30

    o.append(f'<path d="M29 {y - 8}H{W - 29}" stroke="{C["line"]}"/>')
    o.append(t(cx, y + 16, QUEST_NOTE[0], 12, C["pink"], anchor="middle", weight=700))
    o.append(t(cx, y + 36, QUEST_NOTE[1], 12, C["muted"], anchor="middle"))
    return svg(W, H, "Daily quest: " + "; ".join(f"{q} ({s.lower()})" for q, s in QUESTS), "".join(o))


# ================================================================ icons


def tile(body, title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 256 256" role="img">'
            f'<title>{title}</title><rect width="256" height="256" rx="60" fill="#242938"/>{body}</svg>\n')


def brand_tile(name, title, color):
    """Wrap a Simple Icons glyph (assets/source/icons) in a skillicons-style tile."""
    d = re.search(r'<path d="([^"]+)"', (HERE / "icons" / f"{name}.svg").read_text()).group(1)
    return tile(f'<path transform="translate(48 48) scale(6.667)" fill="{color}" d="{d}"/>', title)


TILES = {
    "sqlserver": tile(
        '<g fill="#cc2927"><ellipse cx="128" cy="76" rx="72" ry="26"/>'
        '<path d="M56 76v104c0 14 32 26 72 26s72-12 72-26V76c0 14-32 26-72 26s-72-12-72-26z"/></g>'
        '<ellipse cx="128" cy="76" rx="56" ry="16" fill="#ef5350"/>'
        '<path d="M56 112c0 14 32 26 72 26s72-12 72-26M56 146c0 14 32 26 72 26s72-12 72-26" '
        'fill="none" stroke="#8e1b1a" stroke-width="6"/>', "SQL Server"),
    "azuredevops": tile(
        '<path d="M196 72v104l-44 36-68-24v24l-38-50 112 8V76z" fill="#0078d7"/>'
        '<path d="M196 72l-48-32-78 32v66l-24 6 0-50z" fill="#3fa1f0"/>', "Azure DevOps"),
    "claude": brand_tile("claude", "Claude Code", "#d97757"),
    "copilot": brand_tile("githubcopilot", "GitHub Copilot", "#ffffff"),
    "jira": brand_tile("jira", "Jira", "#2684ff"),
    "ollama": brand_tile("ollama", "Ollama", "#ffffff"),
    "cosmosdb": tile(
        '<circle cx="128" cy="128" r="58" fill="#2f7fd6"/><circle cx="110" cy="108" r="20" fill="#59b4ff" opacity=".7"/>'
        '<ellipse cx="128" cy="128" rx="100" ry="34" fill="none" stroke="#9fd8ff" stroke-width="10" '
        'transform="rotate(-24 128 128)"/>'
        '<path d="M196 52l5 12 12 5-12 5-5 12-5-12-12-5 12-5zM56 186l4 9 9 4-9 4-4 9-4-9-9-4 9-4z" fill="#e0f2fe"/>',
        "Azure Cosmos DB"),
}


def icon_uri(ref):
    raw = (HERE / "icons" / f"skill-{ref[6:]}.svg").read_text() if ref.startswith("skill:") else TILES[ref]
    return "data:image/svg+xml;base64," + base64.b64encode(raw.encode()).decode()


# ================================================================ inventory


def inventory():
    W = 1000
    slot_w, slot_h, gap, row_h = 82, 92, 8, 112
    H = 92 + row_h * len(INVENTORY) + 20
    total = sum(len(items) for _, items in INVENTORY)
    o = [shell(W, H, f"{PLAYER_ID} · inventory", f"{total} items equipped")]
    y = 78
    for i, (cat, items) in enumerate(INVENTORY):
        legendary = i == 0
        accent = C["gold"] if legendary else C["violet"]
        if legendary:
            o.append(f'<rect x="29" y="{y}" width="{W - 58}" height="{row_h - 12}" rx="9" fill="{C["gold"]}" '
                     f'fill-opacity=".05" stroke="{C["gold"]}" stroke-width="1.5" filter="url(#glow)" class="pulse"/>')
        else:
            o.append(panel(29, y, W - 58, row_h - 12, C["line"]))
        o.append(t(49, y + 42, f"❯ {cat}", 15, C["gold"] if legendary else C["pink"], weight=700))
        sub = f"{len(items)} item{'s' * (len(items) > 1)}" + (" · LEGENDARY" if legendary else "")
        o.append(t(49, y + 64, sub, 12, C["gold"] if legendary else C["muted"], weight=700 if legendary else 400))
        x = 214
        sy = y + (row_h - 12 - slot_h) / 2
        for label, ref in items:
            o.append(f'<rect x="{x}" y="{sy:g}" width="{slot_w}" height="{slot_h}" rx="7" fill="{C["panel2"]}" '
                     f'stroke="{accent}" stroke-opacity="{.9 if legendary else .45}"/>')
            o.append(f'<image x="{x + (slot_w - 44) / 2:g}" y="{sy + 10:g}" width="44" height="44" href="{icon_uri(ref)}"/>')
            o.append(t(x + slot_w / 2, sy + 76, label, 10.5 if len(label) < 12 else 9.5, C["text"], anchor="middle"))
            x += slot_w + gap
        if legendary:  # perks next to the AI slots
            px0, px1, py0 = x + 16, W - 49, sy + 40
            o.append(t(px0, sy + 12, "PERKS", 11, C["muted"], weight=700, extra=' letter-spacing="2"'))
            cx, cy = px0, py0
            for perk in AI_PERKS:
                w = len(perk) * 12 * CW + 16
                if cx + w > px1:
                    cx, cy = px0, cy + 30
                c, _ = chip(cx, cy, perk, C["gold"] if perk.startswith("spec") else C["cyan"], 12)
                o.append(c)
                cx += w + 8
        y += row_h
    names = "; ".join(f"{c.strip('/')}: " + ", ".join(lbl for lbl, _ in items) for c, items in INVENTORY)
    return svg(W, H, f"Inventory. {names}. AI perks: {', '.join(AI_PERKS)}", "".join(o))


# ================================================================ quest cards (featured repos)


def quest_card(repo):
    W, H = 560, 360
    o = [shell(W, H, f"{PLAYER_ID} · quest board")]
    badge, bw = chip(W - 32 - 74, 41, "S-RANK", C["gold"])
    o.append(badge.replace(f'x="{W - 32 - 74:g}"', f'x="{W - 32 - bw:g}"', 1)
             .replace(f'x="{W - 32 - 74 + bw / 2:g}"', f'x="{W - 32 - bw / 2:g}"', 1))
    o.append(t(32, 96, "[QUEST]", 13, C["cyan"], weight=700))
    o.append(t(104, 96, repo["name"], 21, C["ice"], weight=700))
    o.append(t(32, 122, repo["sub"], 13, C["violet"]))

    o.append(t(32, 158, "OBJECTIVE", 11, C["muted"], weight=700, extra=' letter-spacing="2"'))
    for i, line in enumerate(repo["objective"]):
        o.append(t(32, 178 + i * 18, line, 13, C["text"]))

    o.append(t(32, 232, "REWARDS", 11, C["muted"], weight=700, extra=' letter-spacing="2"'))
    for i, line in enumerate(repo["rewards"]):
        o.append(t(32, 252 + i * 18, "◆", 10, C["gold"]))
        o.append(t(48, 252 + i * 18, line, 13, C["text"]))

    # flow chips, then the call to action
    fx, fy = 32, H - 30
    for i, step in enumerate(repo["flow"]):
        c, w = chip(fx, fy, step, C["cyan"] if i % 2 == 0 else C["violet"])
        o.append(c)
        fx += w + 6
        if i < len(repo["flow"]) - 1:
            o.append(t(fx + 4, fy, "▶", 10, C["muted"]))
            fx += 22
    o.append(t(W - 32, fy, "ACCEPT ▸", 12, C["gold"], anchor="end", weight=700, extra=' class="blink"'))
    return svg(W, H, f"Quest {repo['name']}: {repo['sub']}", "".join(o))


# ================================================================ dungeon log (career + training)


def frac(ym):
    if ym is None:
        return TODAY.year + (TODAY.month - 1) / 12
    return ym[0] + (ym[1] - 1) / 12


def dungeon_log():
    W = 1180
    y0, x_from, x_to, yr0, yr1 = 78, 760, 1130, 2009, 2027
    xs = lambda yr: x_from + (yr - yr0) / (yr1 - yr0) * (x_to - x_from)
    row = 46
    H = 200 + row * (len(CAREER) + len(TRAINING)) + 92
    o = [shell(W, H, f"{PLAYER_ID} · dungeon log", f"since {yr0}")]

    # KPI strip
    n, gap = len(KPIS), 14
    kw = (W - 58 - gap * (n - 1)) / n
    for i, (num, label) in enumerate(KPIS):
        kx = 29 + i * (kw + gap)
        o.append(panel(kx, y0, kw, 70, C["line"]))
        o.append(t(kx + 18, y0 + 38, num, 26, C["gold"] if i == 0 else C["cyan"], weight=700))
        o.append(t(kx + 18, y0 + 58, label, 10.5, C["muted"], weight=700, extra=' letter-spacing="1"'))

    def axis(y_top, y_bottom):
        out = []
        for yr in range(yr0, yr1 + 1, 3):
            x = xs(yr)
            out.append(f'<path d="M{x:.1f} {y_top + 8}V{y_bottom}" stroke="{C["line"]}" stroke-dasharray="2 4"/>')
            out.append(t(x, y_top, str(yr), 10.5, C["muted"], anchor="middle"))
        return "".join(out)

    def bar(y, start, end, color, active):
        x1, x2 = xs(frac(start)), xs(frac(end))
        dash = ' stroke-dasharray="3 3"' if active and color == C["violet"] else ""
        s = (f'<rect x="{x1:.1f}" y="{y - 6}" width="{max(x2 - x1, 4):.1f}" height="10" rx="5" fill="{color}" '
             f'fill-opacity="{.9 if active else .55}" stroke="{color}"{dash}/>')
        if active:
            s += f'<circle cx="{x2:.1f}" cy="{y - 1}" r="5" fill="{color}" class="pulse" filter="url(#glow)"/>'
        return s

    # career
    y = y0 + 116
    o.append(prompt(49, y, "gates cleared", 18))
    top = y + 18
    o.append(axis(y, top + row * len(CAREER)))
    y = top
    for rank, role, guild, start, end, loot in CAREER:
        color = RANK[rank]
        o.append(f'<rect x="49" y="{y + 4}" width="30" height="30" rx="5" fill="{color}" fill-opacity=".14" stroke="{color}"/>')
        o.append(t(64, y + 25, rank, 15, color, anchor="middle", weight=700))
        o.append(t(94, y + 17, role, 14, C["ice"], weight=700))
        o.append(t(94 + len(role) * 14 * CW + 10, y + 17, f"· {guild}", 13, C["muted"]))
        o.append(t(94, y + 36, loot, 12, C["violet"]))
        o.append(bar(y + 20, start, end, color if rank != "E" else C["text"], end is None))
        if end is None:
            c, _ = chip(94 + (len(role) + len(guild) + 3) * 13.6 * CW + 18, y + 17, "ACTIVE", C["gold"], 10)
            o.append(c)
        y += row

    # training
    y += 34
    o.append(prompt(49, y, "training", 18))
    top = y + 18
    o.append(axis(y, top + row * len(TRAINING)))
    y = top
    for badge, program, school, start, end, tag in TRAINING:
        bw = 34
        o.append(f'<rect x="49" y="{y + 4}" width="{bw}" height="30" rx="5" fill="{C["violet"]}" fill-opacity=".14" '
                 f'stroke="{C["violet"]}"/>')
        o.append(t(49 + bw / 2, y + 24, badge, 10 if len(badge) > 2 else 11.5, C["violet"], anchor="middle", weight=700))
        tx = 94
        o.append(t(tx, y + 17, program, 14, C["ice"], weight=700))
        o.append(t(tx, y + 36, school, 12, C["muted"]))
        if tag:
            c, _ = chip(tx + len(program) * 14 * CW + 12, y + 17, tag, C["cyan"] if end is None else C["gold"], 10)
            o.append(c)
        o.append(bar(y + 20, start, end, C["violet"], end is None))
        y += row

    title = ("Dungeon log. " + " ".join(f"{k} {v.lower()}." for k, v in KPIS) + " Career: "
             + "; ".join(f"{r} at {g}, {s[0]}–{e[0] if e else 'present'}" for _, r, g, s, e, _ in CAREER)
             + ". Training: " + "; ".join(f"{p}, {sc}, {s[0]}–{e[0] if e else 'present'}" for _, p, sc, s, e, _ in TRAINING))
    return svg(W, H, title, "".join(o))


def main():
    pages = {
        "system-profile": profile(),
        "stats": stats(),
        "daily-quest": quest(),
        "inventory": inventory(),
        "dungeon-log": dungeon_log(),
        **{name: quest_card(repo) for name, repo in REPOS.items()},
    }
    written = set()
    for stem, content in pages.items():
        name = f"{stem}.{VERSION}.svg"
        (OUT / name).write_text(content)
        written.add(name)
    for old in OUT.glob("*.svg"):
        if old.name not in written:
            old.unlink()
    print(f"{len(written)} assets ({VERSION}) written to", OUT)


if __name__ == "__main__":
    main()
