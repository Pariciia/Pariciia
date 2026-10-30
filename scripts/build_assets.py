#!/usr/bin/env python3
"""Profil README'sindeki tüm SVG'leri üretir: python3 scripts/build_assets.py

Tema: osiloskop + devre kartı. Hepsi kendi kendine yeten SVG (dış font/JS yok),
animasyonlar SMIL ile — GitHub <img> içinde çalışır.
"""
import math
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).resolve().parent.parent / "assets"
W = 840

BG = "#0b0d14"
PANEL = "#121621"
LINE = "#232838"
TEXT = "#e8eaf0"
MUTED = "#8a92a6"
DIM = "#4b5268"
AMBER = "#f97316"
GOLD = "#fcd34d"
VIOLET = "#a78bfa"
GREEN = "#4ade80"

SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace"


def defs_common():
    return f"""
    <linearGradient id="acc" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="{AMBER}"/>
      <stop offset=".5" stop-color="{GOLD}"/>
      <stop offset="1" stop-color="{VIOLET}"/>
    </linearGradient>
    <filter id="glow" x="-20%" y="-50%" width="140%" height="200%">
      <feGaussianBlur stdDeviation="3.2" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>"""


def card(h, body, extra_defs="", label=""):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}" role="img" aria-label="{escape(label)}">
  <defs>{defs_common()}{extra_defs}
    <clipPath id="frame"><rect width="{W}" height="{h}" rx="16"/></clipPath>
  </defs>
  <g clip-path="url(#frame)">
    <rect width="{W}" height="{h}" fill="{BG}"/>
{body}
  </g>
  <rect x=".5" y=".5" width="{W-1}" height="{h-1}" rx="15.5" fill="none" stroke="{LINE}"/>
</svg>
"""


def fade_in(begin, dur=0.5):
    return f'<animate attributeName="opacity" from="0" to="1" begin="{begin:.2f}s" dur="{dur}s" fill="freeze"/>'


# ---------------------------------------------------------------- header

def waveform(base=236):
    """Analog → nabız → dijital → sönüm; 2 px aralıklarla örneklenmiş iz."""
    pts = []
    for x in range(0, W + 1, 2):
        if x < 110:
            y = 1.5 * math.sin(x / 7)
        elif x < 330:
            t = (x - 110) / 220
            y = (8 + 22 * t) * math.sin((x - 110) / 15)
        elif x < 430:
            u = x - 330
            if 18 <= u < 30:
                y = -6 * math.sin((u - 18) / 12 * math.pi)
            elif 40 <= u < 44:
                y = 8 * (u - 40) / 4
            elif 44 <= u < 50:
                y = 8 - 50 * (u - 44) / 6
            elif 50 <= u < 56:
                y = -42 + 56 * (u - 50) / 6
            elif 56 <= u < 60:
                y = 14 - 14 * (u - 56) / 4
            elif 72 <= u < 92:
                y = -10 * math.sin((u - 72) / 20 * math.pi)
            else:
                y = 0
        elif x < 640:
            u = x - 430
            period = 42
            y = -24 if (u % period) < period / 2 else 18
            if u < 4:
                y = 0
        else:
            u = x - 640
            y = 24 * math.exp(-u / 70) * math.sin(u / 9)
        pts.append((x, base + y))
    d = "M" + " L".join(f"{x},{y:.1f}" for x, y in pts)
    return d


def header():
    h = 310
    grid = []
    for x in range(0, W + 1, 42):
        grid.append(f'<line x1="{x}" y1="0" x2="{x}" y2="{h}"/>')
    for y in range(8, h + 1, 42):
        grid.append(f'<line x1="0" y1="{y}" x2="{W}" y2="{y}"/>')
    ticks = "".join(f'<line x1="{x}" y1="233" x2="{x}" y2="239"/>' for x in range(0, W, 8))

    wave = waveform()
    # Entegre devre (DIP) görünümlü çipler: üst/alt bacaklar, pin-1 çentiği, sırayla yanan LED
    chips = [("macOS", AMBER), ("iOS", GOLD), ("Python", GREEN), ("Swift", VIOLET)]
    chip_svg = []
    cx = W - 36
    cy, ch = 102, 30
    for i, (c, col) in enumerate(reversed(chips)):
        w = round(len(c) * 7.6 + 42)
        cx -= w
        n_pins = max(2, (w - 16) // 12)
        step = (w - 16) / (n_pins - 1)
        pins = "".join(
            f'<rect x="{cx + 8 + k * step - 1.5:.1f}" y="{cy - 5}" width="3" height="5" rx=".8"/>'
            f'<rect x="{cx + 8 + k * step - 1.5:.1f}" y="{cy + ch}" width="3" height="5" rx=".8"/>'
            for k in range(n_pins)
        )
        idx = len(chips) - 1 - i  # soldan sağa sıra → LED zinciri soldan akar
        chip_svg.append(
            f'<g opacity="0">{fade_in(0.9 + idx * 0.12)}'
            f'<g fill="{DIM}">{pins}</g>'
            f'<rect x="{cx}" y="{cy}" width="{w}" height="{ch}" rx="5" fill="{PANEL}" stroke="{col}" stroke-opacity=".45"/>'
            f'<path d="M{cx} {cy + ch / 2 - 5} a5 5 0 0 1 0 10" fill="{BG}" stroke="{col}" stroke-opacity=".45"/>'
            f'<circle cx="{cx + 16}" cy="{cy + ch / 2}" r="3.2" fill="{col}" filter="url(#glow)">'
            f'<animate attributeName="opacity" values=".35;1;.35;.35" keyTimes="0;.12;.3;1" dur="2.4s" begin="{idx * 0.3:.1f}s" repeatCount="indefinite"/></circle>'
            f'<text x="{cx + 27}" y="{cy + 19.5}" font-family="{MONO}" font-size="12.5" font-weight="600" letter-spacing=".4" fill="{TEXT}">{c}</text></g>'
        )
        cx -= 10
    chip_svg.insert(0, f'<text x="{W - 36}" y="86" text-anchor="end" font-family="{MONO}" font-size="10" letter-spacing="2.5" fill="{DIM}">// CORE STACK</text>')

    labels = [(220, "∿ analog"), (380, "♥ pulse"), (535, "⎍ digital"), (740, "◌ decay")]
    label_svg = "".join(
        f'<text x="{x}" y="292" text-anchor="middle">{escape(t)}</text>' for x, t in labels
    )

    extra = f"""
    <radialGradient id="g1" cx="0.88" cy="0.05" r="0.55">
      <stop offset="0" stop-color="{VIOLET}" stop-opacity=".22"/>
      <stop offset="1" stop-color="{VIOLET}" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="g2" cx="0.05" cy="1" r="0.6">
      <stop offset="0" stop-color="{AMBER}" stop-opacity=".18"/>
      <stop offset="1" stop-color="{AMBER}" stop-opacity="0"/>
    </radialGradient>
    <path id="trace" d="{wave}"/>"""

    body = f"""    <rect width="{W}" height="{h}" fill="url(#g1)"/>
    <rect width="{W}" height="{h}" fill="url(#g2)"/>
    <g stroke="#ffffff" stroke-opacity=".045">{"".join(grid)}</g>
    <g stroke="#ffffff" stroke-opacity=".12">{ticks}</g>

    <g font-family="{MONO}" font-size="11" fill="{MUTED}" letter-spacing="1">
      <text x="32" y="36"><tspan fill="{AMBER}">●</tspan> CH1  2.40 GHz</text>
      <text x="170" y="36">TRIG ▲ AUTO</text>
      <text x="290" y="36">200 µs/div</text>
      <text x="{W - 32}" y="36" text-anchor="end">NEVŞEHİR · TR   <tspan fill="{GREEN}">● LIVE<animate attributeName="opacity" values="1;.25;1" dur="1.6s" repeatCount="indefinite"/></tspan></text>
    </g>

    <g opacity="0">{fade_in(0.1, 0.8)}
      <text x="44" y="128" font-family="{SANS}" font-size="58" font-weight="800" letter-spacing="-1.5" fill="url(#acc)">Aybüke Aksöz</text>
      <text x="47" y="164" font-family="{MONO}" font-size="13.5" letter-spacing="4" fill="{MUTED}">SOFTWARE  ◆  HARDWARE  ◆  SIGNAL</text>
    </g>
    {"".join(chip_svg)}

    <use href="#trace" fill="none" stroke="#ffffff" stroke-opacity=".08" stroke-width="1.4"/>
    <use href="#trace" fill="none" stroke="url(#acc)" stroke-opacity=".35" stroke-width="1.6"/>
    <path d="{wave}" pathLength="1000" fill="none" stroke="url(#acc)" stroke-width="2.6"
          stroke-linecap="round" stroke-linejoin="round" filter="url(#glow)"
          stroke-dasharray="190 1200" stroke-dashoffset="190">
      <animate attributeName="stroke-dashoffset" from="190" to="-1000" dur="4.2s" repeatCount="indefinite"/>
    </path>
    <circle r="4.5" fill="#fff" filter="url(#glow)">
      <animateMotion dur="4.2s" repeatCount="indefinite" keyPoints="0;1;1" keyTimes="0;.84;1" calcMode="linear">
        <mpath href="#trace"/>
      </animateMotion>
      <animate attributeName="opacity" values="1;1;0;0" keyTimes="0;.82;.85;1" dur="4.2s" repeatCount="indefinite"/>
    </circle>

    <g font-family="{MONO}" font-size="10.5" fill="{DIM}" letter-spacing="1">{label_svg}</g>"""
    return card(h, body, extra, "Aybüke Aksöz — software, hardware, signal")


# ---------------------------------------------------------------- terminal

ABOUT = {
    "tr": [
        ("whoami", ["Aybüke Aksöz — yazılım geliştirici & tasarımcı"]),
        ("cat odak.txt", ["macOS / iOS uygulamaları · gerçek zamanlı 3B görselleştirme",
                          "Bluetooth & IoT · sinyal işleme · arayüz tasarımı"]),
        ("ls ~/tezgah", ["esp32/  kicad/  swiftui/  3d-baski/  sensörler/"]),
        ("./simdi.sh", ["kendi devre kartımı çiziyorum → toner transfer ile basıyorum"]),
    ],
    "en": [
        ("whoami", ["Aybüke Aksöz — software developer & designer"]),
        ("cat focus.txt", ["macOS / iOS apps · real-time 3D visualization",
                           "Bluetooth & IoT · signal processing · UI design"]),
        ("ls ~/workbench", ["esp32/  kicad/  swiftui/  3d-print/  sensors/"]),
        ("./now.sh", ["designing my own PCB → etching it at home with toner transfer"]),
    ],
}


def terminal(lang):
    fs, lh, cw = 14, 25, 8.6
    rows = sum(1 + len(o) for _, o in ABOUT[lang]) + 1
    h = 58 + rows * lh + 34
    title = "aybuke@nevsehir: ~"
    parts, clips = [], []
    y, t = 92, 0.6
    for i, (cmd, outs) in enumerate(ABOUT[lang]):
        n = len(cmd)
        vals = ";".join(f"{k * cw:.1f}" for k in range(n + 1)) + ";800"
        dur = (n + 1) * 0.05
        clips.append(
            f'<clipPath id="c{i}"><rect x="72" y="{y - 18}" height="26" width="0">'
            f'<animate attributeName="width" values="{vals}" calcMode="discrete" begin="{t:.2f}s" dur="{dur:.2f}s" fill="freeze"/>'
            f"</rect></clipPath>"
        )
        parts.append(
            f'<g opacity="0">{fade_in(t - 0.15, 0.15)}<text x="40" y="{y}" fill="{AMBER}">❯</text>'
            f'<text x="58" y="{y}" fill="{VIOLET}">~</text></g>'
            f'<text x="76" y="{y}" fill="{TEXT}" clip-path="url(#c{i})">{escape(cmd)}</text>'
        )
        t += dur + 0.25
        for o in outs:
            y += lh
            parts.append(
                f'<g opacity="0">{fade_in(t, 0.35)}<text x="58" y="{y}" fill="{MUTED}">{escape(o)}</text></g>'
            )
            t += 0.15
        y += lh
        t += 0.45
    parts.append(
        f'<g opacity="0">{fade_in(t - 0.2, 0.2)}<text x="40" y="{y}" fill="{AMBER}">❯</text>'
        f'<text x="58" y="{y}" fill="{VIOLET}">~</text>'
        f'<rect x="76" y="{y - 14}" width="9" height="17" fill="{GOLD}">'
        f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;.5;.5;1" dur="1.1s" repeatCount="indefinite"/></rect></g>'
    )
    body = f"""    <rect width="{W}" height="44" fill="{PANEL}"/>
    <line x1="0" y1="44" x2="{W}" y2="44" stroke="{LINE}"/>
    <circle cx="26" cy="22" r="6" fill="#ff5f57"/><circle cx="46" cy="22" r="6" fill="#febc2e"/><circle cx="66" cy="22" r="6" fill="#28c840"/>
    <text x="{W / 2}" y="27" text-anchor="middle" font-family="{MONO}" font-size="12" fill="{DIM}">{title}</text>
    <g font-family="{MONO}" font-size="{fs}" xml:space="preserve">
      {"".join(parts)}
    </g>"""
    return card(h, body, "".join(clips), "about — terminal")


# ---------------------------------------------------------------- stack

STACK = [
    ("L1", "LANGUAGES", [("Python", "#FFD43B"), ("Swift", "#F05138"), ("C++", "#659AD2"), ("JavaScript", "#F7DF1E")]),
    ("L2", "FRAMEWORKS", [("SwiftUI", "#2396F3"), ("RealityKit", "#B48CF2"), ("Kivy", "#E8734A"), ("OpenGL", "#7FB3D5"), ("NumPy", "#4DABCF")]),
    ("L3", "HARDWARE", [("ESP32", "#E7352C"), ("BLE", "#3C9BFF"), ("CoreBluetooth", "#147EFB"), ("Arduino", "#00979D"), ("KiCad", "#7C8FF0")]),
    ("L4", "TOOLING", [("Xcode", "#1575F9"), ("Git", "#F05032"), ("VS Code", "#3EA6FF"), ("PyInstaller", "#24A84C")]),
]


def stack():
    row_h, top = 66, 70
    h = top + len(STACK) * row_h + 18
    out = [
        f'<text x="32" y="42" font-family="{MONO}" font-size="12" letter-spacing="3" fill="{MUTED}">'
        f'<tspan fill="{AMBER}">//</tspan> LAYER STACK</text>',
        f'<text x="{W - 32}" y="42" text-anchor="end" font-family="{MONO}" font-size="11" fill="{DIM}">4-layer · 1.6 mm · FR4</text>',
    ]
    k = 0
    for r, (lay, name, items) in enumerate(STACK):
        cy = top + r * row_h + row_h / 2
        out.append(
            f'<text x="32" y="{cy - 2}" font-family="{MONO}" font-size="20" font-weight="700" fill="url(#acc)">{lay}</text>'
            f'<text x="32" y="{cy + 16}" font-family="{MONO}" font-size="9.5" letter-spacing="2" fill="{DIM}">{name}</text>'
        )
        x = 170
        out.append(f'<line x1="78" y1="{cy}" x2="{W - 32}" y2="{cy}" stroke="{LINE}" stroke-width="2"/>')
        out.append(
            f'<circle r="2.5" fill="{GOLD}" opacity=".9"><animateMotion path="M78,{cy} L{W - 32},{cy}" '
            f'dur="{3.2 + r * 0.5}s" begin="{r * 0.7}s" repeatCount="indefinite"/></circle>'
        )
        out.append(f'<circle cx="150" cy="{cy}" r="5" fill="{BG}" stroke="{DIM}" stroke-width="2"/>')
        for label, color in items:
            w = len(label) * 7.6 + 40
            out.append(
                f'<g opacity="0">{fade_in(0.2 + k * 0.07, 0.4)}'
                f'<rect x="{x}" y="{cy - 17}" width="{w:.0f}" height="34" rx="9" fill="{PANEL}" stroke="{LINE}"/>'
                f'<circle cx="{x + 17}" cy="{cy}" r="4.5" fill="{color}"/>'
                f'<text x="{x + 29}" y="{cy + 4.5}" font-family="{SANS}" font-size="13.5" fill="{TEXT}">{label}</text></g>'
            )
            x += w + 12
            k += 1
    return card(h, "    " + "\n    ".join(out), "", "tech stack")


# ---------------------------------------------------------------- lab

ICONS = {
    "sphere": '<circle cx="0" cy="0" r="12"/><ellipse cx="0" cy="0" rx="12" ry="4.5"/><ellipse cx="0" cy="0" rx="4.5" ry="12"/>',
    "scan": '<path d="M-12,-6 V-12 H-6 M6,-12 H12 V-6 M12,6 V12 H6 M-6,12 H-12 V6"/><path d="M-4,-7 Q-2,0 -4,7 M4,-7 Q2,0 4,7"/>',
    "bt": '<path d="M-6,-6 L6,6 L0,12 V-12 L6,-6 L-6,6"/>',
    "bot": '<rect x="-11" y="-9" width="22" height="16" rx="5"/><circle cx="-4.5" cy="-1" r="1.6" fill="currentColor"/><circle cx="4.5" cy="-1" r="1.6" fill="currentColor"/><path d="M0,-9 V-13 M-6,7 V12 M6,7 V12"/>',
}

LAB = {
    "tr": ("lab/", "üzerinde çalıştıklarım", [
        ("sphere", "TEPE GÖZ", ["Sensör verisini gerçek zamanlı 3B küre", "üzerinde görselleştiren tarama yazılımı."], ["Python", "OpenGL", "Kivy"], "aktif"),
        ("scan", "Uzuv3D", ["Kamerayla uzvu tarayıp baskıya hazır", "STL üreten iOS uygulaması."], ["SwiftUI", "RealityKit"], "geliştiriliyor"),
        ("bt", "BT Köprüsü", ["Bluetooth Classic cihazı BLE + UART'a", "çeviren ESP32 firmware'i."], ["C++", "ESP32", "BLE"], "aktif"),
        ("bot", "Masa Robotu", ["Kendi çizdiğim PCB üzerinde, pan-tilt", "kafalı ESP32 masa robotu."], ["KiCad", "ESP32-S3", "3D"], "geliştiriliyor"),
    ]),
    "en": ("lab/", "things I'm building", [
        ("sphere", "TEPE GÖZ", ["Scanning software that renders sensor", "data on a real-time 3D sphere."], ["Python", "OpenGL", "Kivy"], "active"),
        ("scan", "Uzuv3D", ["iOS app that scans a limb with the", "camera and exports a print-ready STL."], ["SwiftUI", "RealityKit"], "in progress"),
        ("bt", "BT Bridge", ["ESP32 firmware that turns a Bluetooth", "Classic device into BLE + UART."], ["C++", "ESP32", "BLE"], "active"),
        ("bot", "Desk Robot", ["Pan-tilt ESP32 desk robot built on a", "PCB I designed myself."], ["KiCad", "ESP32-S3", "3D"], "in progress"),
    ]),
}


def lab(lang):
    head, sub, items = LAB[lang]
    cw, ch, gap, top = 376, 168, 24, 66
    h = top + 2 * ch + gap + 32
    out = [
        f'<text x="32" y="42" font-family="{MONO}" font-size="12" letter-spacing="3" fill="{MUTED}">'
        f'<tspan fill="{AMBER}">//</tspan> {head.upper()}  <tspan fill="{DIM}" letter-spacing="1">— {escape(sub)}</tspan></text>'
    ]
    for i, (icon, title, desc, tags, status) in enumerate(items):
        x = 32 + (i % 2) * (cw + gap)
        y = top + (i // 2) * (ch + gap)
        active = status in ("aktif", "active")
        dot = GREEN if active else GOLD
        g = [
            f'<rect x="{x}" y="{y}" width="{cw}" height="{ch}" rx="12" fill="{PANEL}" stroke="{LINE}"/>',
            f'<rect x="{x}" y="{y}" width="3" height="{ch}" rx="1.5" fill="url(#acc)" opacity=".8"/>',
            f'<rect x="{x + 22}" y="{y + 22}" width="44" height="44" rx="11" fill="{BG}" stroke="url(#acc)"/>',
            f'<g transform="translate({x + 44},{y + 44})" fill="none" stroke="{GOLD}" stroke-width="1.7" '
            f'stroke-linecap="round" stroke-linejoin="round" color="{GOLD}">{ICONS[icon]}</g>',
            f'<text x="{x + 80}" y="{y + 50}" font-family="{SANS}" font-size="18" font-weight="700" fill="{TEXT}">{escape(title)}</text>',
            f'<text x="{x + cw - 20}" y="{y + 36}" text-anchor="end" font-family="{MONO}" font-size="10.5" fill="{MUTED}">'
            f'<tspan fill="{dot}">●</tspan> {escape(status)}</text>',
        ]
        for j, line in enumerate(desc):
            g.append(f'<text x="{x + 22}" y="{y + 94 + j * 19}" font-family="{SANS}" font-size="13.5" fill="{MUTED}">{escape(line)}</text>')
        tx = x + 22
        for tag in tags:
            tw = len(tag) * 6.9 + 18
            g.append(
                f'<rect x="{tx}" y="{y + ch - 38}" width="{tw:.0f}" height="22" rx="6" fill="{BG}" stroke="{LINE}"/>'
                f'<text x="{tx + tw / 2:.1f}" y="{y + ch - 23}" text-anchor="middle" font-family="{MONO}" font-size="11" fill="{TEXT}">{escape(tag)}</text>'
            )
            tx += tw + 8
        out.append(f'<g opacity="0">{fade_in(0.15 + i * 0.15, 0.5)}{"".join(g)}</g>')
    return card(h, "    " + "\n    ".join(out), "", "projects")


# ---------------------------------------------------------------- footer

def footer():
    h = 90
    pts = []
    for x in range(0, W + 1, 3):
        env = math.sin(math.pi * x / W) ** 2
        y = 45 + 16 * env * math.sin(x / 11) * math.cos(x / 53)
        pts.append(f"{x},{y:.1f}")
    d = "M" + " L".join(pts)
    body = f"""    <path d="{d}" fill="none" stroke="url(#acc)" stroke-width="1.8" opacity=".55"/>
    <path d="{d}" pathLength="1000" fill="none" stroke="url(#acc)" stroke-width="2.4" filter="url(#glow)"
          stroke-dasharray="120 1200" stroke-dashoffset="120">
      <animate attributeName="stroke-dashoffset" from="120" to="-1000" dur="5s" repeatCount="indefinite"/>
    </path>
    <text x="{W / 2}" y="80" text-anchor="middle" font-family="{MONO}" font-size="10.5" letter-spacing="3" fill="{DIM}">END OF TRANSMISSION</text>"""
    svg = card(h, body, "", "signal divider")
    # footer çerçevesiz, arka plansız: sadece iz
    return svg.replace(f'<rect width="{W}" height="{h}" fill="{BG}"/>', "").replace(
        f'<rect x=".5" y=".5" width="{W-1}" height="{h-1}" rx="15.5" fill="none" stroke="{LINE}"/>', ""
    )


# ---------------------------------------------------------------- iletişim butonları

BUTTON_ICONS = {
    "email": '<rect x="-10" y="-7" width="20" height="14" rx="3"/><path d="M-9,-5.5 L0,1 L9,-5.5"/>',
    "linkedin": '<rect x="-10" y="-10" width="20" height="20" rx="4"/><path d="M-5,-1 V5 M-5,-4.5 V-4.4 M-1,5 V-1 M-1,1.5 Q-1,-1 2,-1 Q5,-1 5,2 V5"/>',
    "github": '<circle cx="-5" cy="-6" r="2.4"/><circle cx="-5" cy="7" r="2.4"/><circle cx="6" cy="-2" r="2.4"/><path d="M-5,-3.6 V4.6 M6,0.4 Q6,4 -3,5.6"/>',
}


def button(icon, label):
    bw, bh = 196, 52
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{bw}" height="{bh}" viewBox="0 0 {bw} {bh}" role="img" aria-label="{label}">
  <defs>{defs_common()}</defs>
  <rect x=".5" y=".5" width="{bw - 1}" height="{bh - 1}" rx="12" fill="{PANEL}" stroke="{LINE}"/>
  <g transform="translate(30,26)" fill="none" stroke="url(#acc)" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">{BUTTON_ICONS[icon]}</g>
  <text x="54" y="31" font-family="{MONO}" font-size="12.5" letter-spacing="2.5" fill="{TEXT}">{label}</text>
  <text x="{bw - 20}" y="31" text-anchor="end" font-family="{SANS}" font-size="14" fill="{DIM}">↗</text>
</svg>
"""


def main():
    OUT.mkdir(exist_ok=True)
    files = {
        "btn-email.svg": button("email", "EMAIL"),
        "btn-linkedin.svg": button("linkedin", "LINKEDIN"),
        "btn-github.svg": button("github", "GITHUB"),
        "header.svg": header(),
        "about-tr.svg": terminal("tr"),
        "about-en.svg": terminal("en"),
        "stack.svg": stack(),
        "lab-tr.svg": lab("tr"),
        "lab-en.svg": lab("en"),
        "footer.svg": footer(),
    }
    for name, svg in files.items():
        (OUT / name).write_text(svg, encoding="utf-8")
        print(f"assets/{name}  {len(svg) // 1024} KB")


if __name__ == "__main__":
    main()
