# -*- coding: utf-8 -*-
import cairosvg

W, H = 1440, 1180
F = "DejaVu Sans, Arial, sans-serif"
C = dict(bg="#f3f4f6", card="#ffffff", line="#e5e7eb", dark="#111827", gray="#4b5563", light="#9ca3af",
         purple="#7c3aed", purple2="#6d28d9", purpleL="#f5f3ff", orange="#f97316", orangeL="#fff7ed",
         green="#10b981", greenL="#ecfdf5", greenD="#047857", blue="#3b82f6", blueL="#eff6ff", star="#f59e0b", starOff="#d1d5db")
o = []
def add(s): o.append(s)
def rect(x, y, w, h, fill, stroke=None, rx=10, sw=1.5, extra=""):
    st = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
    add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}"{st} {extra}/>')
def text(x, y, s, size=15, fill=C["dark"], weight="normal", anchor="start", style="normal"):
    s = s.replace("&", "&amp;").replace("<", "&lt;")
    add(f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" font-weight="{weight}" font-style="{style}" text-anchor="{anchor}">{s}</text>')
def stars(x, y, n, size=18, total=5):
    for i in range(total):
        full = (i + 1) <= int(n)
        half = (not full) and (n - int(n) >= 0.5) and i == int(n)
        col = C["star"] if full or half else C["starOff"]
        text(x + i * (size * 1.05), y, "★", size=size, fill=col)
def chip(x, y, label, fill, color, w=None, size=13):
    w = w or int(len(label) * size * 0.6 + 22)
    rect(x, y, w, 26, fill, rx=13)
    text(x + w / 2, y + 18, label, size=size, fill=color, weight="bold", anchor="middle")
    return w
def button(x, y, w, label, fill, color, stroke=None, size=14):
    rect(x, y, w, 38, fill, stroke=stroke, rx=8)
    text(x + w / 2, y + 25, label, size=size, fill=color, weight="bold", anchor="middle")

add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{F}">')
rect(0, 0, W, H, C["bg"], rx=0)

# ---- browser chrome
rect(0, 0, W, 56, "#e5e7eb", rx=0)
for i, col in enumerate(["#ef4444", "#f59e0b", "#22c55e"]):
    add(f'<circle cx="{26 + i * 24}" cy="28" r="7" fill="{col}"/>')
rect(120, 14, 1200, 28, "#ffffff", rx=14)
text(140, 33, "🔒", size=13, fill=C["light"])
text(165, 33, "otm-prensa.example/tareas/2026-10/agua-embalse", size=14, fill=C["gray"])

# ---- site header
rect(0, 56, W, 76, C["card"], rx=0)
add(f'<line x1="0" y1="132" x2="{W}" y2="132" stroke="{C["line"]}" stroke-width="2"/>')
rect(40, 76, 36, 36, C["purple"], rx=8)
text(58, 101, "O", size=20, fill="#fff", weight="bold", anchor="middle")
text(90, 95, "OTM-Prensa", size=22, fill=C["dark"], weight="bold")
text(90, 116, "Tareas de modelamiento desde la prensa", size=12, fill=C["light"])
for i, (lab, active) in enumerate([("Explorar", True), ("Por nivel", False), ("Cómo usar", False), ("Acerca del proyecto", False)]):
    x = 440 + i * 150
    text(x, 101, lab, size=15, fill=C["purple2"] if active else C["gray"], weight="bold" if active else "normal")
    if active:
        add(f'<line x1="{x}" y1="110" x2="{x + 68}" y2="110" stroke="{C["purple"]}" stroke-width="3"/>')
rect(1130, 76, 270, 40, C["purpleL"], stroke=C["purple"], rx=20)
add(f'<circle cx="1152" cy="96" r="13" fill="{C["purple"]}"/>')
text(1152, 101, "P", size=13, fill="#fff", weight="bold", anchor="middle")
text(1174, 92, "Mi cuenta · Profesora", size=13, fill=C["dark"], weight="bold")
text(1174, 109, "3° y 4° medio · Región de Valparaíso", size=11, fill=C["gray"])

# ---- filter bar
y = 150
text(40, y + 18, "Explorar  ›  Nivel 16–18  ›  Medio ambiente", size=13, fill=C["light"])
rect(40, y + 32, 560, 40, C["card"], stroke=C["line"], rx=20)
text(62, y + 58, "🔍  Buscar por tema, contenido matemático o noticia…", size=14, fill=C["light"])
x = 620
for lab, fill, col in [("Nivel: 16–18  ✕", C["purpleL"], C["purple2"]), ("Tema: medio ambiente  ✕", C["greenL"], C["greenD"]), ("Ordenar: mejor valoradas ▾", C["card"], C["gray"])]:
    x += chip(x, y + 39, lab, fill, col, size=13) + 10

# ---- main card (left)
LX, LY, LW = 40, 250, 880
rect(LX, LY, LW, 880, C["card"], stroke=C["line"], rx=14)
x = LX + 30; y = LY + 30
x += chip(x, y, "PUBLICADA · validada por el equipo", C["greenL"], C["greenD"]) + 10
x += chip(x, y, "Semana 42 · 2026", C["bg"], C["gray"]) + 10
chip(x, y, "v2 · incorpora 4 comentarios docentes", C["orangeL"], "#c2410c")
# --- ilustración: embalse pequeño
ix, iy, iw, ih = LX + 30, LY + 66, 150, 92
add(f'<clipPath id="embalse"><rect x="{ix}" y="{iy}" width="{iw}" height="{ih}" rx="12"/></clipPath>')
add(f'<g clip-path="url(#embalse)">')
rect(ix, iy, iw, ih, "#e0f2fe", rx=12)                                    # cielo
add(f'<circle cx="{ix + 118}" cy="{iy + 22}" r="11" fill="#fde68a"/>')    # sol
add(f'<path d="M{ix} {iy + 50} Q{ix + 30} {iy + 22} {ix + 62} {iy + 48} Q{ix + 80} {iy + 36} {ix + 105} {iy + 52} L{ix + 105} {iy + ih} L{ix} {iy + ih} Z" fill="#86efac"/>')  # cerros
add(f'<path d="M{ix} {iy + 58} Q{ix + 22} {iy + 44} {ix + 48} {iy + 60} Q{ix + 70} {iy + 50} {ix + 100} {iy + 64} L{ix + 100} {iy + ih} L{ix} {iy + ih} Z" fill="#4ade80"/>')
# nivel anterior (línea punteada) y agua actual
add(f'<line x1="{ix}" y1="{iy + 56}" x2="{ix + 104}" y2="{iy + 56}" stroke="#60a5fa" stroke-width="1.5" stroke-dasharray="4,3"/>')
add(f'<path d="M{ix} {iy + 70} Q{ix + 12} {iy + 66} {ix + 24} {iy + 70} T{ix + 48} {iy + 70} T{ix + 72} {iy + 70} T{ix + 96} {iy + 70} L{ix + 104} {iy + 70} L{ix + 104} {iy + ih} L{ix} {iy + ih} Z" fill="#3b82f6"/>')
add(f'<path d="M{ix} {iy + 70} Q{ix + 12} {iy + 66} {ix + 24} {iy + 70} T{ix + 48} {iy + 70} T{ix + 72} {iy + 70} T{ix + 96} {iy + 70}" fill="none" stroke="#bfdbfe" stroke-width="2"/>')
# muro de la represa
add(f'<path d="M{ix + 104} {iy + 40} L{ix + 122} {iy + 40} L{ix + 136} {iy + ih} L{ix + 104} {iy + ih} Z" fill="#9ca3af"/>')
add(f'<path d="M{ix + 104} {iy + 40} L{ix + 122} {iy + 40} L{ix + 122} {iy + 46} L{ix + 104} {iy + 46} Z" fill="#6b7280"/>')
add(f'<path d="M{ix + 136} {iy + ih} L{ix + 150} {iy + ih} L{ix + 150} {iy + 84} L{ix + 128} {iy + 84} Z" fill="#60a5fa"/>')  # salida de agua
add(f'<text x="{ix + 6}" y="{iy + 53}" font-size="9" fill="#1d4ed8" font-weight="bold">nivel 2025</text>')
add(f'<text x="{ix + 6}" y="{iy + 86}" font-size="11" fill="#ffffff" font-weight="bold">38 %</text>')
add('</g>')
rect(ix, iy, iw, ih, "none", stroke="#bae6fd", rx=12, sw=1.5)
TX = LX + 200
text(TX, LY + 100, "¿Alcanza el agua del embalse", size=27, fill=C["dark"], weight="bold")
text(TX, LY + 132, "hasta marzo?", size=27, fill=C["dark"], weight="bold")
text(TX, LY + 156, "Nota de prensa · 12 oct 2026 · el embalse que abastece a la ciudad baja al 38 %  ↗", size=13, fill=C["gray"], style="italic")

# meta grid
my = LY + 176
rect(LX + 30, my, LW - 60, 96, C["bg"], rx=10)
cols = [("Nivel principal", "16–18 años", 0), ("Variantes", "13–15  ·  18–20", 170), ("Contenidos", "tasas de cambio · lineal vs. exponencial", 340), ("Ciclo", "1–7 · foco: validar", 640)]
cols2 = [("Tiempo", "2 sesiones de 90 min", 0), ("Puntaje rúbrica", "18 / 21", 170), ("Bloqueo más anticipado", "simplificar (fase 2) · 4 de 6 grupos", 340), ("Implementaciones", "11 reportadas", 640)]
for i, (k, v, off) in enumerate(cols):
    xx = LX + 50 + off
    text(xx, my + 26, k.upper(), size=10, fill=C["light"], weight="bold")
    text(xx, my + 44, v, size=12, fill=C["dark"], weight="bold")
for i, (k, v, off) in enumerate(cols2):
    xx = LX + 50 + off
    text(xx, my + 68, k.upper(), size=10, fill=C["light"], weight="bold")
    text(xx, my + 86, v, size=12, fill=C["dark"], weight="bold")

# rating block
ry = my + 120
text(LX + 30, ry + 44, "4,6", size=44, fill=C["dark"], weight="bold")
stars(LX + 112, ry + 40, 4.5, size=26)
text(LX + 260, ry + 24, "23 valoraciones de docentes", size=14, fill=C["dark"], weight="bold")
text(LX + 260, ry + 44, "11 reportan haberla implementado · promedio de dificultad percibida: media", size=12, fill=C["gray"])
for i, (lab, pct) in enumerate([("5★", 0.62), ("4★", 0.28), ("3★", 0.07), ("2★", 0.03), ("1★", 0.0)]):
    yy = ry + 8 + i * 13
    text(LX + 740, yy + 9, lab, size=10, fill=C["gray"], anchor="end")
    rect(LX + 748, yy + 1, 100, 8, C["line"], rx=4)
    if pct: rect(LX + 748, yy + 1, int(100 * pct), 8, C["star"], rx=4)

# buttons
by = ry + 70
button(LX + 30, by, 160, "⬇  Tarea (PDF)", C["purple"], "#fff")
button(LX + 200, by, 190, "⬇  Guía docente (PDF)", C["purple"], "#fff")
button(LX + 400, by, 200, "⬇  Escenarios (notebook)", C["card"], C["purple2"], stroke=C["purple"])
button(LX + 610, by, 170, "Ver en repositorio ↗", C["card"], C["gray"], stroke=C["line"])

# tabs
ty = by + 64
add(f'<line x1="{LX + 30}" y1="{ty + 34}" x2="{LX + LW - 30}" y2="{ty + 34}" stroke="{C["line"]}" stroke-width="2"/>')
tabs = [("Enunciado", False), ("Guía docente", False), ("Escenarios simulados", False), ("Comentarios (4)", True)]
x = LX + 30
for lab, active in tabs:
    text(x, ty + 22, lab, size=15, fill=C["purple2"] if active else C["gray"], weight="bold" if active else "normal")
    w = len(lab) * 8.6
    if active:
        add(f'<line x1="{x}" y1="{ty + 34}" x2="{x + w}" y2="{ty + 34}" stroke="{C["purple"]}" stroke-width="3"/>')
    x += w + 36

# comments
cy = ty + 56
comments = [
    ("M", "Docente · 3° medio · liceo municipal, Región Metropolitana", "hace 5 días", 5,
     ["Usé la variante 16–18 tal cual. Los grupos se trabaron justo donde decía la guía (simplificar:",
      "qué consumo asumir). El escenario 3, con el modelo lineal que falla, fue clave para la discusión final."]),
    ("A", "Docente · 1° año universitario · curso de cálculo", "hace 2 semanas", 4,
     ["Buena tarea, pero la variante 18–20 necesita datos de más meses para que el ajuste exponencial",
      "tenga sentido. Subí una propuesta de datos extendidos al repositorio (PR #41)."]),
]
for ini, who, when, n, lines in comments:
    rect(LX + 30, cy, LW - 60, 96, C["bg"], rx=10)
    add(f'<circle cx="{LX + 58}" cy="{cy + 30}" r="16" fill="{C["blue"]}"/>')
    text(LX + 58, cy + 35, ini, size=14, fill="#fff", weight="bold", anchor="middle")
    text(LX + 86, cy + 26, who, size=13, fill=C["dark"], weight="bold")
    text(LX + 86, cy + 43, when, size=11, fill=C["light"])
    stars(LX + LW - 60 - 100, cy + 30, n, size=16)
    for i, l in enumerate(lines):
        text(LX + 86, cy + 66 + i * 17, l, size=12.5, fill=C["gray"])
    cy += 108
text(LX + 30, cy + 14, "Ver los 4 comentarios  ›", size=13, fill=C["purple2"], weight="bold")

# composer
cy += 32
rect(LX + 30, cy, LW - 60, 150, C["purpleL"], stroke=C["purple"], rx=10)
text(LX + 50, cy + 28, "¿Cómo te resultó implementarla?", size=16, fill=C["dark"], weight="bold")
text(LX + 50, cy + 50, "Tu valoración:", size=13, fill=C["gray"])
stars(LX + 150, cy + 52, 0, size=22)
rect(LX + 420, cy + 32, 250, 30, C["card"], stroke=C["line"], rx=6)
text(LX + 432, cy + 52, "Nivel en que la implementaste  ▾", size=12, fill=C["gray"])
rect(LX + 50, cy + 66, LW - 100, 44, C["card"], stroke=C["line"], rx=6)
text(LX + 62, cy + 92, "Cuéntanos qué funcionó, dónde se trabaron los estudiantes y qué cambiarías…", size=13, fill=C["light"])
button(LX + 50, cy + 118 - 12, 200, "Publicar comentario", C["purple"], "#fff", size=13)
text(LX + 270, cy + 121, "Tus comentarios y datos de perfil se usan, anonimizados, con fines de investigación. Más información ↗", size=11, fill=C["gray"])

# ---- right column
RX, RW = 950, 450
# profile / anticipation card
ry = 250
rect(RX, ry, RW, 250, C["card"], stroke=C["line"], rx=14)
text(RX + 24, ry + 32, "Bloqueos anticipados por la simulación", size=15, fill=C["dark"], weight="bold")
text(RX + 24, ry + 52, "6 grupos simulados · % que se trabó en cada fase", size=11, fill=C["light"])
phases = [("1 Comprender", 0.17), ("2 Simplificar", 0.67), ("3 Matematizar", 0.33), ("4 Trabajar mat.", 0.17), ("5 Interpretar", 0.33), ("6 Validar", 0.50), ("7 Comunicar", 0.17)]
for i, (lab, p) in enumerate(phases):
    yy = ry + 72 + i * 23
    text(RX + 24, yy + 12, lab, size=11, fill=C["gray"])
    rect(RX + 150, yy + 3, 240, 12, C["line"], rx=6)
    rect(RX + 150, yy + 3, int(240 * p), 12, C["purple"] if p >= 0.5 else "#c4b5fd", rx=6)
    text(RX + 400, yy + 13, f"{int(p * 100)}%", size=11, fill=C["gray"])
text(RX + 24, ry + 240, "Detalle y preguntas de andamiaje en la guía docente  ›", size=11, fill=C["purple2"], weight="bold")

# related tasks
ry = 520
rect(RX, ry, RW, 300, C["card"], stroke=C["line"], rx=14)
text(RX + 24, ry + 32, "Tareas relacionadas", size=15, fill=C["dark"], weight="bold")
rel = [("¿Cuánto sube el pasaje si el petróleo sigue así?", "13–15 · economía", 4.2, 17),
       ("Vacunación: ¿cuándo llegamos al 90%?", "16–18 · salud", 4.8, 31),
       ("Récord de calor: ¿tendencia o azar?", "18–20 · clima · estadística", 4.0, 9),
       ("Reciclaje en el colegio: ¿cuántos contenedores?", "10–12 · medio ambiente", 4.5, 12)]
for i, (t, m, r, n) in enumerate(rel):
    yy = ry + 56 + i * 60
    rect(RX + 16, yy, RW - 32, 52, C["bg"], rx=8)
    text(RX + 28, yy + 21, t, size=12.5, fill=C["dark"], weight="bold")
    text(RX + 28, yy + 40, m, size=11, fill=C["gray"])
    stars(RX + 240, yy + 41, r, size=12)
    text(RX + 310, yy + 40, f"{r:.1f} · {n} valoraciones", size=10, fill=C["light"])

# account card
ry = 840
rect(RX, ry, RW, 170, C["blueL"], stroke=C["blue"], rx=14)
text(RX + 24, ry + 32, "Tu cuenta docente", size=15, fill="#1d4ed8", weight="bold")
for i, l in enumerate(["Perfil: nivel que enseñas, tipo de establecimiento,", "región, años de experiencia.",
                        "Con esto el proyecto estudia qué tareas funcionan", "para qué población y mejora el banco.",
                        "Puedes editar o retirar tus datos cuando quieras."]):
    text(RX + 24, ry + 58 + i * 18, l, size=12, fill=C["gray"])
text(RX + 24, ry + 156, "Editar perfil ›", size=12, fill="#1d4ed8", weight="bold")

# status card
ry = 1030
rect(RX, ry, RW, 100, C["card"], stroke=C["line"], rx=14)
text(RX + 24, ry + 30, "Trazabilidad de esta tarea", size=14, fill=C["dark"], weight="bold")
for i, l in enumerate(["Noticia → diseño → rúbrica 18/21 → revisión humana ✓", "Simulación (6 grupos) → guía → revisión humana ✓ → publicada", "Commit a3f9c1 · 14 oct 2026 · v2 tras 4 comentarios docentes"]):
    text(RX + 24, ry + 52 + i * 17, l, size=11, fill=C["gray"])

# footer
text(W / 2, H - 14, "Snapshot ilustrativo de la capa interfaz · solo visual, no funcional · Borrador v2 · 17 oct 2026 · nombres y datos ficticios", size=12, fill=C["light"], anchor="middle")
add("</svg>")

svg = "\n".join(o)
open("interfaz-otm-prensa_v2_2026-10-17.svg", "w", encoding="utf-8").write(svg)
cairosvg.svg2png(bytestring=svg.encode("utf-8"), write_to="interfaz-otm-prensa_v2_2026-10-17.png", output_width=2160)
cairosvg.svg2pdf(bytestring=svg.encode("utf-8"), write_to="interfaz-otm-prensa_v2_2026-10-17.pdf")
print("ok")
