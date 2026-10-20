# -*- coding: utf-8 -*-
import cairosvg

W, H = 1440, 1210
F = "DejaVu Sans, Arial, sans-serif"
C = dict(bg="#f3f4f6", card="#ffffff", line="#e5e7eb", dark="#111827", gray="#4b5563", light="#9ca3af",
         purple="#7c3aed", purple2="#6d28d9", purpleL="#f5f3ff", orange="#f97316", orangeL="#fff7ed",
         green="#10b981", greenL="#ecfdf5", greenD="#047857", blue="#3b82f6", blueL="#eff6ff", star="#f59e0b", starOff="#d1d5db")
LEVEL = {"10–12": ("#fef3c7", "#b45309"), "13–15": ("#dcfce7", "#15803d"), "16–18": ("#ede9fe", "#6d28d9"), "18–20": ("#dbeafe", "#1d4ed8")}
o = []
def add(s): o.append(s)
def rect(x, y, w, h, fill, stroke=None, rx=10, sw=1.5, extra=""):
    st = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
    add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}"{st} {extra}/>')
def text(x, y, s, size=15, fill=C["dark"], weight="normal", anchor="start", style="normal"):
    s = s.replace("&", "&amp;").replace("<", "&lt;")
    add(f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" font-weight="{weight}" font-style="{style}" text-anchor="{anchor}">{s}</text>')
def stars(x, y, n, size=12, total=5):
    for i in range(total):
        full = (i + 1) <= int(n)
        half = (not full) and (n - int(n) >= 0.5) and i == int(n)
        col = C["star"] if full or half else C["starOff"]
        text(x + i * (size * 1.05), y, "★", size=size, fill=col)
def chip(x, y, label, fill, color, size=11, h=22):
    w = int(len(label) * size * 0.62 + 16)
    rect(x, y, w, h, fill, rx=h / 2)
    text(x + w / 2, y + h * 0.7, label, size=size, fill=color, weight="bold", anchor="middle")
    return w

# ---------- flat icons (drawn inside a w×h box at x,y) ----------
def icon_embalse(x, y, w, h):
    rect(x, y, w, h, "#e0f2fe", rx=0)
    add(f'<circle cx="{x + w*0.8}" cy="{y + h*0.22}" r="{h*0.1}" fill="#fde68a"/>')
    add(f'<path d="M{x} {y+h*0.55} Q{x+w*0.2} {y+h*0.25} {x+w*0.42} {y+h*0.52} Q{x+w*0.55} {y+h*0.4} {x+w*0.7} {y+h*0.56} L{x+w*0.7} {y+h} L{x} {y+h} Z" fill="#86efac"/>')
    add(f'<path d="M{x} {y+h*0.75} Q{x+w*0.1} {y+h*0.7} {x+w*0.2} {y+h*0.75} T{x+w*0.4} {y+h*0.75} T{x+w*0.6} {y+h*0.75} L{x+w*0.7} {y+h*0.75} L{x+w*0.7} {y+h} L{x} {y+h} Z" fill="#3b82f6"/>')
    add(f'<path d="M{x+w*0.7} {y+h*0.42} L{x+w*0.82} {y+h*0.42} L{x+w*0.92} {y+h} L{x+w*0.7} {y+h} Z" fill="#9ca3af"/>')
def icon_bus(x, y, w, h):
    rect(x, y, w, h, "#fef3c7", rx=0)
    rect(x, y + h*0.78, w, h*0.22, "#d1d5db", rx=0)
    rect(x + w*0.15, y + h*0.3, w*0.6, h*0.42, "#f97316", rx=8)
    for i in range(3):
        rect(x + w*0.2 + i*w*0.18, y + h*0.37, w*0.13, h*0.16, "#bfdbfe", rx=3)
    add(f'<circle cx="{x+w*0.3}" cy="{y+h*0.76}" r="{h*0.07}" fill="#374151"/><circle cx="{x+w*0.62}" cy="{y+h*0.76}" r="{h*0.07}" fill="#374151"/>')
    text(x + w*0.86, y + h*0.6, "$", size=h*0.3, fill="#b45309", weight="bold", anchor="middle")
def icon_vacuna(x, y, w, h):
    rect(x, y, w, h, "#dcfce7", rx=0)
    add(f'<path d="M{x+w*0.1} {y+h*0.9} L{x+w*0.1} {y+h*0.5} L{x+w*0.3} {y+h*0.5} L{x+w*0.3} {y+h*0.3} L{x+w*0.5} {y+h*0.3} L{x+w*0.5} {y+h*0.6} L{x+w*0.7} {y+h*0.6} L{x+w*0.7} {y+h*0.2} L{x+w*0.9} {y+h*0.2} L{x+w*0.9} {y+h*0.9} Z" fill="#86efac"/>')
    add(f'<path d="M{x+w*0.1} {y+h*0.55} L{x+w*0.3} {y+h*0.45} L{x+w*0.5} {y+h*0.4} L{x+w*0.7} {y+h*0.3} L{x+w*0.9} {y+h*0.18}" fill="none" stroke="#15803d" stroke-width="3"/>')
    text(x + w*0.06, y + h*0.95, "meta 90 %", size=h*0.14, fill="#15803d", weight="bold")
def icon_calor(x, y, w, h):
    rect(x, y, w, h, "#fee2e2", rx=0)
    add(f'<circle cx="{x+w*0.72}" cy="{y+h*0.35}" r="{h*0.2}" fill="#f97316"/>')
    rect(x + w*0.22, y + h*0.15, w*0.1, h*0.6, "#ffffff", stroke="#9ca3af", rx=8)
    rect(x + w*0.24, y + h*0.35, w*0.06, h*0.4, "#ef4444", rx=4)
    add(f'<circle cx="{x+w*0.27}" cy="{y+h*0.8}" r="{h*0.09}" fill="#ef4444"/>')
def icon_reciclaje(x, y, w, h):
    rect(x, y, w, h, "#ecfdf5", rx=0)
    for i, col in enumerate(["#10b981", "#3b82f6", "#f59e0b"]):
        rect(x + w*0.12 + i*w*0.27, y + h*0.4, w*0.2, h*0.45, col, rx=4)
        rect(x + w*0.1 + i*w*0.27, y + h*0.34, w*0.24, h*0.08, col, rx=3)
    text(x + w*0.5, y + h*0.27, "♻", size=h*0.22, fill="#047857", anchor="middle")
def icon_estadio(x, y, w, h):
    rect(x, y, w, h, "#e0e7ff", rx=0)
    add(f'<ellipse cx="{x+w*0.5}" cy="{y+h*0.55}" rx="{w*0.4}" ry="{h*0.32}" fill="#6366f1"/>')
    add(f'<ellipse cx="{x+w*0.5}" cy="{y+h*0.55}" rx="{w*0.27}" ry="{h*0.2}" fill="#4ade80"/>')
    rect(x + w*0.42, y + h*0.45, w*0.16, h*0.2, "none", stroke="#ffffff", rx=0, sw=1.5)
def icon_metro(x, y, w, h):
    rect(x, y, w, h, "#f3e8ff", rx=0)
    rect(x, y + h*0.75, w, h*0.06, "#9ca3af", rx=0)
    rect(x + w*0.1, y + h*0.3, w*0.8, h*0.42, "#7c3aed", rx=10)
    for i in range(4):
        rect(x + w*0.16 + i*w*0.18, y + h*0.37, w*0.13, h*0.15, "#ddd6fe", rx=3)
    add(f'<circle cx="{x+w*0.5}" cy="{y+h*0.18}" r="{h*0.07}" fill="#fde68a"/>')
def icon_encuesta(x, y, w, h):
    rect(x, y, w, h, "#dbeafe", rx=0)
    for i, (hh, col) in enumerate([(0.3, "#3b82f6"), (0.55, "#1d4ed8"), (0.42, "#60a5fa"), (0.2, "#93c5fd")]):
        rect(x + w*0.14 + i*w*0.2, y + h*(0.85 - hh), w*0.14, h*hh, col, rx=3)
    add(f'<line x1="{x+w*0.1}" y1="{y+h*0.85}" x2="{x+w*0.9}" y2="{y+h*0.85}" stroke="#1e3a8a" stroke-width="2"/>')
def icon_sismo(x, y, w, h):
    rect(x, y, w, h, "#fff7ed", rx=0)
    add(f'<polyline points="{x+w*0.05},{y+h*0.55} {x+w*0.25},{y+h*0.55} {x+w*0.33},{y+h*0.2} {x+w*0.42},{y+h*0.85} {x+w*0.5},{y+h*0.3} {x+w*0.58},{y+h*0.7} {x+w*0.66},{y+h*0.5} {x+w*0.95},{y+h*0.5}" fill="none" stroke="#ea580c" stroke-width="3"/>')
def icon_pan(x, y, w, h):
    rect(x, y, w, h, "#fef9c3", rx=0)
    add(f'<ellipse cx="{x+w*0.45}" cy="{y+h*0.6}" rx="{w*0.3}" ry="{h*0.2}" fill="#d97706"/>')
    add(f'<ellipse cx="{x+w*0.45}" cy="{y+h*0.52}" rx="{w*0.3}" ry="{h*0.18}" fill="#f59e0b"/>')
    add(f'<path d="M{x+w*0.65} {y+h*0.75} L{x+w*0.72} {y+h*0.35} L{x+w*0.8} {y+h*0.55} L{x+w*0.9} {y+h*0.2}" fill="none" stroke="#b45309" stroke-width="3"/>')
    text(x + w*0.9, y + h*0.9, "↑", size=h*0.25, fill="#b45309", weight="bold", anchor="end")

ICONS = dict(embalse=icon_embalse, bus=icon_bus, vacuna=icon_vacuna, calor=icon_calor, reciclaje=icon_reciclaje,
             estadio=icon_estadio, metro=icon_metro, encuesta=icon_encuesta, sismo=icon_sismo, pan=icon_pan)

TASKS = {
 "embalse": ("¿Alcanza el agua del embalse hasta marzo?", "16–18", 4.6, 23, "medio ambiente"),
 "bus":     ("¿Cuánto sube el pasaje si el petróleo sigue así?", "13–15", 4.2, 17, "economía"),
 "vacuna":  ("Vacunación: ¿cuándo llegamos al 90%?", "16–18", 4.8, 31, "salud"),
 "calor":   ("Récord de calor: ¿tendencia o azar?", "18–20", 4.0, 9, "clima"),
 "reciclaje": ("Reciclaje en el colegio: ¿cuántos contenedores?", "10–12", 4.5, 12, "medio ambiente"),
 "estadio": ("Evacuar el estadio en 8 minutos: ¿se puede?", "13–15", 4.3, 14, "deporte"),
 "metro":   ("Nueva línea de metro: ¿cuántos trenes hacen falta?", "18–20", 4.4, 8, "transporte"),
 "encuesta": ("La encuesta dice 48%: ¿cuánto hay que creerle?", "16–18", 4.7, 20, "sociedad"),
 "sismo":   ("Sismo 6,2: ¿cuánta energía es eso?", "13–15", 4.1, 6, "ciencia"),
 "pan":     ("El pan subió 14%: ¿y el sueldo?", "10–12", 4.4, 11, "economía"),
}

add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{F}">')
rect(0, 0, W, H, C["bg"], rx=0)

# browser chrome
rect(0, 0, W, 56, "#e5e7eb", rx=0)
for i, col in enumerate(["#ef4444", "#f59e0b", "#22c55e"]):
    add(f'<circle cx="{26 + i * 24}" cy="28" r="7" fill="{col}"/>')
rect(120, 14, 1200, 28, "#ffffff", rx=14)
text(165, 33, "otm-prensa.example", size=14, fill=C["gray"])

# site header
rect(0, 56, W, 76, C["card"], rx=0)
add(f'<line x1="0" y1="132" x2="{W}" y2="132" stroke="{C["line"]}" stroke-width="2"/>')
rect(40, 76, 36, 36, C["purple"], rx=8)
text(58, 101, "O", size=20, fill="#fff", weight="bold", anchor="middle")
text(90, 95, "OTM-Prensa", size=22, fill=C["dark"], weight="bold")
text(90, 116, "Tareas de modelamiento desde la prensa", size=12, fill=C["light"])
for i, (lab, active) in enumerate([("Inicio", True), ("Explorar", False), ("Por nivel", False), ("Cómo usar", False), ("Acerca del proyecto", False)]):
    x = 400 + i * 128
    text(x, 101, lab, size=15, fill=C["purple2"] if active else C["gray"], weight="bold" if active else "normal")
    if active:
        add(f'<line x1="{x}" y1="110" x2="{x + 44}" y2="110" stroke="{C["purple"]}" stroke-width="3"/>')
rect(1130, 76, 270, 40, C["purpleL"], stroke=C["purple"], rx=20)
add(f'<circle cx="1152" cy="96" r="13" fill="{C["purple"]}"/>')
text(1152, 101, "P", size=13, fill="#fff", weight="bold", anchor="middle")
text(1174, 92, "Mi cuenta · Profesora", size=13, fill=C["dark"], weight="bold")
text(1174, 109, "3° y 4° medio · Región de Valparaíso", size=11, fill=C["gray"])

# ---------- hero
hx, hy, hw, hh = 40, 156, W - 80, 230
add('<defs><linearGradient id="hero" x1="0" x2="1"><stop offset="0" stop-color="#4c1d95"/><stop offset="1" stop-color="#7c3aed"/></linearGradient>'
    '<clipPath id="heroclip"><rect x="%d" y="%d" width="%d" height="%d" rx="16"/></clipPath></defs>' % (hx, hy, hw, hh))
add('<g clip-path="url(#heroclip)">')
rect(hx, hy, hw, hh, "url(#hero)", rx=16)
# big illustration on the right, framed
icon_embalse(hx + hw - 420, hy, 420, hh)
add(f'<rect x="{hx + hw - 420}" y="{hy}" width="120" height="{hh}" fill="url(#hero)" opacity="0.0"/>')
add(f'<linearGradient id="fade" x1="0" x2="1"><stop offset="0" stop-color="#5b21b6" stop-opacity="1"/><stop offset="1" stop-color="#5b21b6" stop-opacity="0"/></linearGradient>')
add(f'<rect x="{hx + hw - 420}" y="{hy}" width="140" height="{hh}" fill="url(#fade)"/>')
add('</g>')
x = hx + 36
x += chip(x, hy + 28, "TAREA DE LA SEMANA", "#fde68a", "#92400e", size=11, h=24) + 10
x += chip(x, hy + 28, "NUEVO", C["orange"], "#fff", size=11, h=24) + 10
chip(x, hy + 28, "Semana 42 · 2026", "#ede9fe", "#4c1d95", size=11, h=24)
text(hx + 36, hy + 92, "¿Alcanza el agua del embalse hasta marzo?", size=32, fill="#ffffff", weight="bold")
text(hx + 36, hy + 122, "A partir de la noticia de esta semana sobre la baja del nivel del embalse que abastece a la ciudad.", size=15, fill="#ede9fe")
text(hx + 36, hy + 144, "Nivel 16–18 (variantes 13–15 y 18–20) · tasas de cambio · lineal vs. exponencial · 2 sesiones", size=13, fill="#c4b5fd")
rect(hx + 36, hy + 168, 150, 38, "#ffffff", rx=8)
text(hx + 111, hy + 193, "Ver la tarea", size=14, fill=C["purple2"], weight="bold", anchor="middle")
rect(hx + 198, hy + 168, 190, 38, "none", stroke="#ffffff", rx=8)
text(hx + 293, hy + 193, "⬇  Guía docente", size=14, fill="#ffffff", weight="bold", anchor="middle")
stars(hx + 410, hy + 194, 4.5, size=16)
text(hx + 500, hy + 193, "4,6 · 23 valoraciones", size=13, fill="#ede9fe")

# ---------- rows of thumbnails
CW, CH, GAP = 256, 200, 20
def card(x, y, key, new=False):
    title, lvl, r, n, tema = TASKS[key]
    rect(x, y, CW, CH, C["card"], stroke=C["line"], rx=12)
    add(f'<clipPath id="c{key}{int(x)}{int(y)}"><rect x="{x}" y="{y}" width="{CW}" height="{CH*0.56}" rx="12"/></clipPath>')
    add(f'<g clip-path="url(#c{key}{int(x)}{int(y)})">')
    ICONS[key](x, y, CW, CH * 0.56 + 12)
    add('</g>')
    if new:
        rect(x + 10, y + 10, 64, 22, C["orange"], rx=6)
        text(x + 42, y + 26, "NUEVO", size=11, fill="#fff", weight="bold", anchor="middle")
    f, c = LEVEL[lvl]
    chip(x + CW - 68, y + 10, lvl, f, c, size=11, h=22)
    ty = y + CH * 0.56 + 10
    t1 = title if len(title) <= 29 else title[:title.rfind(" ", 0, 29)]
    t2 = "" if t1 == title else title[len(t1) + 1:]
    text(x + 12, ty + 18, t1, size=13, fill=C["dark"], weight="bold")
    if t2: text(x + 12, ty + 35, t2, size=13, fill=C["dark"], weight="bold")
    text(x + 12, ty + 56, tema, size=11, fill=C["light"])
    stars(x + 12, ty + 76, r, size=12)
    text(x + 82, ty + 76, f"{r:.1f} · {n}", size=11, fill=C["gray"])

def row(y, title, keys, new_keys=()):
    text(40, y, title, size=19, fill=C["dark"], weight="bold")
    text(W - 40, y, "Ver todas ›", size=13, fill=C["purple2"], weight="bold", anchor="end")
    for i, k in enumerate(keys):
        card(40 + i * (CW + GAP), y + 14, k, new=(k in new_keys))
    # hint of a 6th card cut off at the right edge
    rect(40 + 5 * (CW + GAP), y + 14, 60, CH, C["card"], stroke=C["line"], rx=12)

row(430, "Nuevas esta semana", ["embalse", "metro", "sismo", "pan", "encuesta"], new_keys={"embalse", "metro", "sismo"})
row(680, "Mejor valoradas por docentes", ["vacuna", "encuesta", "embalse", "reciclaje", "metro"])
row(930, "Para tu nivel: 16–18 años", ["embalse", "vacuna", "encuesta", "calor", "estadio"], new_keys={"embalse"})

# footer
text(W / 2, H - 14, "Snapshot ilustrativo de la pantalla de inicio · solo visual, no funcional · Borrador v1 · 17 oct 2026 · tareas y datos ficticios", size=12, fill=C["light"], anchor="middle")
add("</svg>")

svg = "\n".join(o)
open("home-otm-prensa_v1_2026-10-17.svg", "w", encoding="utf-8").write(svg)
cairosvg.svg2png(bytestring=svg.encode("utf-8"), write_to="home-otm-prensa_v1_2026-10-17.png", output_width=2160)
cairosvg.svg2pdf(bytestring=svg.encode("utf-8"), write_to="home-otm-prensa_v1_2026-10-17.pdf")
print("ok")
