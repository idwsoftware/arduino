#!/usr/bin/env python3
"""
Genera las animaciones (GIF) e imagenes de conexiones (PNG) de la carpeta "animaciones/".

Son ILUSTRACIONES dibujadas con Pillow (no capturas reales de PICSimLab):
  - 00_flujo_paso_a_paso.gif     : pasos Arduino IDE -> PICSimLab -> Save Workspace
  - 0N_preguntaN_simulacion.gif  : comportamiento esperado de cada programa
  - 0N_preguntaN_conexiones.png  : tabla de pines tal como se eligen en "Properties"

Los nombres de menus y pines son los de PICSimLab 0.9.x.
Las simulaciones reproducen la logica y los tiempos de los .ino.

Uso: python3 herramientas/generar_animaciones.py
"""
import math
import os

from PIL import Image, ImageDraw, ImageFont

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SALIDA = os.path.join(RAIZ, "animaciones")
FUENTES = "/usr/share/fonts/truetype/dejavu/"

W, H = 960, 560

# Colores estilo PICSimLab
BG = (50, 50, 50)
PANEL = (49, 61, 99)
PANEL_BORDE = (25, 30, 55)
TXT = (235, 235, 235)
GRIS = (155, 155, 155)
LED_OFF = (70, 0, 0)
LED_ON = (255, 30, 30)
WIN_BG = (240, 240, 240)
WIN_TIT = (60, 90, 150)
MENU_BG = (225, 225, 225)
SEL = (51, 153, 255)
AMARILLO = (255, 210, 60)
VERDE_LCD = (120, 200, 60)
AGUA = (60, 140, 230)

_fcache = {}


def F(size, bold=False, mono=False):
    key = (size, bold, mono)
    if key not in _fcache:
        if mono:
            name = "DejaVuSansMono-Bold.ttf" if bold else "DejaVuSansMono.ttf"
        else:
            name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
        _fcache[key] = ImageFont.truetype(FUENTES + name, size)
    return _fcache[key]


def nuevo():
    im = Image.new("RGB", (W, H), BG)
    return im, ImageDraw.Draw(im)


def caption(d, paso, texto, sub=None):
    d.rectangle([0, H - 78, W, H], fill=(20, 20, 30))
    if paso:
        d.rounded_rectangle([14, H - 66, 120, H - 30], radius=8, fill=SEL)
        d.text((67, H - 48), paso, font=F(18, True), fill="white", anchor="mm")
        x = 136
    else:
        x = 16
    tam = 19
    while tam > 13 and d.textlength(texto, font=F(tam, True)) > W - x - 12:
        tam -= 1
    d.text((x, H - 60), texto, font=F(tam, True), fill="white")
    if sub:
        tam = 15
        while tam > 10 and d.textlength(sub, font=F(tam)) > W - x - 12:
            tam -= 1
        d.text((x, H - 32), sub, font=F(tam), fill=(200, 200, 200))


def titulo(d, texto):
    d.text((W // 2, 20), texto, font=F(20, True), fill=TXT, anchor="mm")


def cursor(d, x, y):
    pts = [(x, y), (x, y + 22), (x + 6, y + 17), (x + 10, y + 26), (x + 14, y + 24), (x + 10, y + 15), (x + 17, y + 15)]
    d.polygon(pts, fill="white", outline="black")


# ---------------------------------------------------------------------------
#  Ventanas y menus de ejemplo
# ---------------------------------------------------------------------------
def ventana(d, x, y, w, h, tit, menus, color=WIN_TIT):
    d.rectangle([x + 4, y + 4, x + w + 4, y + h + 4], fill=(25, 25, 25))
    d.rectangle([x, y, x + w, y + h], fill=WIN_BG, outline=(30, 30, 30))
    d.rectangle([x, y, x + w, y + 28], fill=color)
    d.text((x + 10, y + 14), tit, font=F(14, True), fill="white", anchor="lm")
    for i, c in enumerate([(230, 80, 80), (230, 190, 60), (90, 190, 90)]):
        cx = x + w - 18 - i * 20
        d.ellipse([cx - 6, y + 8, cx + 6, y + 20], fill=c)
    d.rectangle([x, y + 28, x + w, y + 52], fill=MENU_BG)
    pos = {}
    mx = x + 8
    for m in menus:
        tw = d.textlength(m, font=F(14))
        pos[m] = (mx, y + 28, mx + tw + 16, y + 52)
        mx += tw + 16
    return pos


def menu_activo(d, rect):
    d.rectangle(rect, fill=SEL)


def dibujar_menus(d, pos, activo=None):
    for m, r in pos.items():
        if m == activo:
            menu_activo(d, r)
        d.text((r[0] + 8, (r[1] + r[3]) // 2), m, font=F(14), fill="white" if m == activo else "black", anchor="lm")


def desplegable(d, x, y, items, sel=None, ancho=None):
    ancho = ancho or int(max(d.textlength(i, font=F(14)) for i in items) + 40)
    alto = 26 * len(items) + 6
    d.rectangle([x + 3, y + 3, x + ancho + 3, y + alto + 3], fill=(90, 90, 90))
    d.rectangle([x, y, x + ancho, y + alto], fill="white", outline=(120, 120, 120))
    centros = {}
    for i, it in enumerate(items):
        ty = y + 4 + i * 26
        if it == "-":
            d.line([x + 6, ty + 13, x + ancho - 6, ty + 13], fill=(190, 190, 190))
            continue
        if it == sel:
            d.rectangle([x + 2, ty, x + ancho - 2, ty + 24], fill=SEL)
        d.text((x + 14, ty + 12), it, font=F(14), fill="white" if it == sel else "black", anchor="lm")
        centros[it] = (x + 40, ty + 12)
    return centros


def placa_uno(d, x, y, esc=1.0):
    """Dibujo simple de un Arduino Uno."""
    w, h = int(330 * esc), int(230 * esc)
    d.rounded_rectangle([x, y, x + w, y + h], radius=10, fill=(0, 120, 140), outline=(0, 70, 90), width=2)
    d.rectangle([x - 14, y + 30, x + 40, y + 80], fill=(170, 170, 170))       # USB
    d.rectangle([x - 8, y + 150, x + 36, y + 196], fill=(30, 30, 30))         # jack
    d.rectangle([x + 120, y + 100, x + 280, y + 136], fill=(30, 30, 30))      # chip
    d.text((x + 200, y + 118), "ATMEGA328P", font=F(11, True), fill=(200, 200, 200), anchor="mm")
    for i in range(14):
        px = x + 130 + i * 13
        d.rectangle([px, y + 8, px + 9, y + 20], fill=(20, 20, 20))
    for i in range(6):
        px = x + 210 + i * 13
        d.rectangle([px, y + h - 20, px + 9, y + h - 8], fill=(20, 20, 20))
    d.text((x + 180, y + 40), "UNO", font=F(int(28 * esc), True), fill="white")
    d.text((x + 110, y + 26), "DIGITAL (PWM~)", font=F(10), fill="white")
    d.text((x + 225, y + h - 34), "ANALOG IN", font=F(10), fill="white")


# ---------------------------------------------------------------------------
#  Partes (LEDs, botones, potenciometro, etc.) estilo "Spare parts"
# ---------------------------------------------------------------------------
def panel_leds(d, x, y, estados, etiquetas=None):
    n = len(estados)
    w = 40 + n * 66
    d.rounded_rectangle([x, y, x + w, y + 100], radius=6, fill=PANEL, outline=PANEL_BORDE, width=2)
    for i, on in enumerate(estados):
        cx = x + 44 + i * 66
        # resistencia
        d.rectangle([cx - 30, y + 26, cx - 24, y + 46], fill=(210, 190, 140))
        for k in range(3):
            d.line([cx - 30, y + 30 + k * 5, cx - 24, y + 30 + k * 5], fill=(150, 80, 40))
        if on:
            d.ellipse([cx - 22, y + 14, cx + 22, y + 58], fill=(255, 80, 80))
        d.ellipse([cx - 17, y + 19, cx + 17, y + 53], fill=LED_ON if on else LED_OFF, outline=(10, 10, 10), width=2)
        lab = etiquetas[i] if etiquetas else "D%d" % (i + 2)
        d.text((cx, y + 80), lab, font=F(12), fill=GRIS, anchor="mm")
    return w


def panel_botones(d, x, y, nombres, presionado=None, sep=90):
    n = len(nombres)
    w = 40 + n * sep
    d.rounded_rectangle([x, y, x + w, y + 92], radius=6, fill=PANEL, outline=PANEL_BORDE, width=2)
    for i, nm in enumerate(nombres):
        cx = x + 64 + i * sep
        p = presionado == i
        d.rectangle([cx - 20, y + 16, cx + 20, y + 56], fill=(30, 30, 30))
        r = 11 if p else 14
        d.ellipse([cx - r, y + 36 - r, cx + r, y + 36 + r], fill=(90, 90, 90) if p else (160, 160, 160), outline="black")
        d.text((cx, y + 74), nm, font=F(12, True), fill=AMARILLO if p else GRIS, anchor="mm")
    return w


def flecha_mano(d, x, y):
    """Mano/indicador de clic."""
    cursor(d, x, y)
    d.ellipse([x - 12, y - 12, x + 12, y + 12], outline=AMARILLO, width=3)


# ---------------------------------------------------------------------------
#  Utilidades GIF
# ---------------------------------------------------------------------------
class Pelicula:
    def __init__(self):
        self.frames = []
        self.dur = []

    def add(self, im, ms):
        if self.frames and self.frames[-1].tobytes() == im.tobytes():
            self.dur[-1] += ms
        else:
            self.frames.append(im)
            self.dur.append(ms)

    def save(self, nombre):
        ruta = os.path.join(SALIDA, nombre)
        pal = [f.convert("P", palette=Image.ADAPTIVE, colors=128) for f in self.frames]
        pal[0].save(ruta, save_all=True, append_images=pal[1:], duration=self.dur, loop=0, optimize=True)
        print("Generado", os.path.relpath(ruta, RAIZ), "(%d cuadros)" % len(pal))


def mover(p, escena, x0, y0, x1, y1, pasos=8, ms=60):
    for i in range(pasos + 1):
        t = i / pasos
        t = t * t * (3 - 2 * t)
        im, d = escena()
        cursor(d, int(x0 + (x1 - x0) * t), int(y0 + (y1 - y0) * t))
        p.add(im, ms)


# ===========================================================================
#  00 - Flujo general paso a paso
# ===========================================================================
MENUS_PSL = ["File", "Board", "Microcontroller", "Modules", "Tools", "Code", "Help"]
MENUS_SP = ["File", "Edit", "Inputs", "Outputs", "Others", "Virtual", "Help"]


def escena_ide(drop=False, sel=None):
    im, d = nuevo()
    titulo(d, "Paso 1 - Arduino IDE")
    pos = ventana(d, 60, 44, 840, 410, "Pregunta1_Secuencias_LEDs | Arduino IDE",
                  ["Archivo", "Editar", "Programa", "Herramientas", "Ayuda"], color=(0, 110, 120))
    dibujar_menus(d, pos, "Programa" if drop else None)
    codigo = ["const int primerPin = 2;", "const int ultimoPin = 9;", "", "void setup() {",
              "  for(int i = primerPin; i <= ultimoPin; i++) {", "    pinMode(i, OUTPUT);", "  }", "  ..."]
    for i, l in enumerate(codigo):
        d.text((90, 110 + i * 22), l, font=F(15, mono=True), fill=(40, 40, 40))
    r = pos["Programa"]
    c = {}
    if drop:
        c = desplegable(d, r[0], r[3], ["Verificar/Compilar      Ctrl+R", "Subir                   Ctrl+U", "-",
                                         "Exportar binario compilado  Ctrl+Alt+S", "Mostrar carpeta del programa"],
                        sel=sel)
    caption(d, "PASO 1", "Arduino IDE: Programa > Exportar binario compilado",
            "Herramientas > Placa: Arduino Uno. Se crea el .hex en la carpeta del sketch (usa el que NO dice with_bootloader)")
    return im, d, pos, c


def escena_psl(activo=None, items=None, sel=None, paso="", texto="", sub=None, extra=None, tit="PICSimLab"):
    im, d = nuevo()
    titulo(d, tit)
    pos = ventana(d, 40, 44, 560, 410, "PICSimLab - Arduino Uno - atmega328p", MENUS_PSL)
    placa_uno(d, 150, 160, 1.0)
    d.text((60, 425), "Clk(MHz) 16    Spd: 1.00x", font=F(12), fill=(60, 60, 60))
    if extra:
        extra(d)
    dibujar_menus(d, pos, activo)
    c = {}
    if activo:
        r = pos[activo]
        c = desplegable(d, r[0], r[3], items, sel=sel)
    caption(d, paso, texto, sub)
    return im, d, pos, c


def flujo():
    p = Pelicula()

    # ---- Paso 1: Arduino IDE
    im, d, pos, _ = escena_ide()
    cursor(d, 480, 300)
    p.add(im, 1200)
    r = pos["Programa"]
    mover(p, lambda: escena_ide()[:2], 480, 300, r[0] + 20, r[1] + 12)
    _, _, _, c = escena_ide(True)
    tx, ty = c["Exportar binario compilado  Ctrl+Alt+S"]
    mover(p, lambda: escena_ide(True)[:2], r[0] + 20, r[1] + 12, tx, ty)
    im, d, _, _ = escena_ide(True, "Exportar binario compilado  Ctrl+Alt+S")
    flecha_mano(d, tx, ty)
    p.add(im, 3500)

    # ---- Pasos PICSimLab (menu principal)
    pasos = [
        ("Board", ["Arduino Uno", "Arduino Mega", "Arduino Nano", "Breadboard", "PICGenios", "Blue Pill", "..."],
         "Arduino Uno", "PASO 2", "PICSimLab: Board > Arduino Uno", "Elige la placa que se va a simular"),
        ("Microcontroller", ["atmega328p"], "atmega328p", "PASO 3", "Microcontroller > atmega328p",
         "Es el microcontrolador del Arduino Uno (reloj 16 MHz)"),
        ("File", ["Load Hex", "Reload Last", "Save Hex", "-", "Configure", "-", "Save Workspace", "Load Workspace",
                  "Load Board Demo", "-", "Exit"], "Load Hex", "PASO 4", "File > Load Hex",
         "Selecciona el .hex exportado (p. ej. Pregunta1_Secuencias_LEDs.ino.hex). La simulacion arranca sola"),
        ("Modules", ["Oscilloscope", "Spare parts"], "Spare parts", "PASO 5", "Modules > Spare parts",
         "Se abre la ventana de componentes externos (LEDs, botones, LCD, sensores...)"),
    ]
    cx, cy = 300, 300
    for menu, items, sel, paso, texto, sub in pasos:
        mk = lambda menu=menu, items=items, paso=paso, texto=texto, sub=sub: escena_psl(None, None, None, paso, texto, sub)[:2]
        im, d = mk()
        cursor(d, cx, cy)
        p.add(im, 700)
        r = escena_psl()[2][menu]
        mover(p, mk, cx, cy, r[0] + 20, r[1] + 12)
        _, _, _, c = escena_psl(menu, items, None, paso, texto, sub)
        tx, ty = c[sel]
        mover(p, lambda menu=menu, items=items, paso=paso, texto=texto, sub=sub:
              escena_psl(menu, items, None, paso, texto, sub)[:2], r[0] + 20, r[1] + 12, tx, ty, pasos=6)
        im, d, _, _ = escena_psl(menu, items, sel, paso, texto, sub)
        flecha_mano(d, tx, ty)
        p.add(im, 3200)
        cx, cy = tx, ty

    # ---- Paso 4b: dialogo de archivo
    def dialogo(d):
        d.rectangle([150, 120, 590, 360], fill="white", outline=(80, 80, 80), width=2)
        d.rectangle([150, 120, 590, 146], fill=WIN_TIT)
        d.text((160, 133), "Load Hex", font=F(13, True), fill="white", anchor="lm")
        archivos = ["Pregunta1_Secuencias_LEDs.ino", "Pregunta1_Secuencias_LEDs.ino.hex",
                    "Pregunta1_Secuencias_LEDs.ino.with_bootloader.hex"]
        for i, a in enumerate(archivos):
            yy = 160 + i * 28
            if i == 1:
                d.rectangle([156, yy - 2, 584, yy + 22], fill=SEL)
            d.text((166, yy + 10), a, font=F(13), fill="white" if i == 1 else "black", anchor="lm")
        d.rounded_rectangle([490, 320, 580, 350], radius=4, fill=SEL)
        d.text((535, 335), "Open", font=F(13, True), fill="white", anchor="mm")
    im, d, _, _ = escena_psl(None, None, None, "PASO 4", "File > Load Hex: abre el .hex (sin bootloader)",
                             "El programa queda cargado en el Arduino simulado", extra=dialogo)
    flecha_mano(d, 535, 335)
    p.add(im, 3000)

    # ---- Paso 6: ventana Spare parts > Outputs > LEDs
    def escena_sp(activo=None, sel=None, popup=False, psel=None, leds=False, paso="PASO 6",
                  texto="Spare parts: Outputs > LEDs  (o Inputs > Push Buttons, etc.)",
                  sub="Inputs: Push Buttons, Potentiometers, LDR, Ultrasonic HC-SR04 | Outputs: LEDs, LCD hd44780, Buzzer, Servo Motor"):
        im, d = nuevo()
        titulo(d, "Ventana Spare parts")
        pos = ventana(d, 40, 44, 880, 410, "PICSimLab - Spare parts", MENUS_SP)
        d.rectangle([41, 97, 919, 453], fill=BG)
        if leds:
            panel_leds(d, 90, 120, [False] * 8)
        dibujar_menus(d, pos, activo)
        c = {}
        if activo:
            r = pos[activo]
            c = desplegable(d, r[0], r[3], ["7 Segments Display", "Buzzer", "DC Motor", "LCD hd44780", "LEDs",
                                            "RGB LED", "Servo Motor", "Step Motor", "..."], sel=sel)
        if popup:
            c = desplegable(d, 330, 200, ["Properties", "Move", "Rotate", "Delete", "Help", "About"], sel=psel,
                            ancho=150)
        caption(d, paso, texto, sub)
        return im, d, pos, c

    im, d, pos, _ = escena_sp()
    cursor(d, 480, 300)
    p.add(im, 900)
    r = pos["Outputs"]
    mover(p, lambda: escena_sp()[:2], 480, 300, r[0] + 20, r[1] + 12)
    _, _, _, c = escena_sp("Outputs")
    tx, ty = c["LEDs"]
    mover(p, lambda: escena_sp("Outputs")[:2], r[0] + 20, r[1] + 12, tx, ty, pasos=6)
    im, d, _, _ = escena_sp("Outputs", "LEDs")
    flecha_mano(d, tx, ty)
    p.add(im, 3000)
    im, d, _, _ = escena_sp(leds=True)
    cursor(d, 300, 170)
    p.add(im, 1500)

    # ---- Paso 7: clic derecho > Properties
    t7 = dict(paso="PASO 7", texto="Clic derecho sobre el componente > Properties",
              sub="Ahi se elige a que pin del Arduino va conectada cada patita")
    im, d, _, c = escena_sp(popup=True, leds=True, **t7)
    tx, ty = c["Properties"]
    cursor(d, 330, 200)
    p.add(im, 1200)
    im, d, _, _ = escena_sp(popup=True, psel="Properties", leds=True, **t7)
    flecha_mano(d, tx, ty)
    p.add(im, 2800)

    # ---- Paso 8: dialogo de propiedades
    def props(n_sel):
        im, d = nuevo()
        titulo(d, "Ventana Properties (LEDs)")
        d.rectangle([250, 50, 710, 470], fill=WIN_BG, outline=(30, 30, 30))
        d.rectangle([250, 50, 710, 78], fill=WIN_TIT)
        d.text((262, 64), "LEDs - Properties", font=F(14, True), fill="white", anchor="lm")
        pines = ["4  PD2/2", "5  PD3/~3", "6  PD4/4", "11  PD5/~5", "12  PD6/~6", "13  PD7/7", "14  PB0/8", "15  PB1/~9"]
        for i in range(8):
            yy = 92 + i * 38
            d.text((272, yy + 14), "%d-D%d" % (i + 1, i + 1), font=F(14), fill="black", anchor="lm")
            txt = pines[i] if i < n_sel else "0  NC"
            d.rectangle([360, yy, 600, yy + 28], fill="white", outline=(150, 150, 150))
            d.text((370, yy + 14), txt, font=F(14), fill=(0, 0, 0) if i < n_sel else (150, 150, 150), anchor="lm")
            d.polygon([(582, yy + 10), (592, yy + 10), (587, yy + 18)], fill="black")
            if i == n_sel - 1:
                d.rectangle([358, yy - 2, 602, yy + 30], outline=SEL, width=3)
        yy = 92 + 8 * 38
        d.text((272, yy + 14), "Active", font=F(14), fill="black", anchor="lm")
        d.rectangle([360, yy, 600, yy + 28], fill="white", outline=(150, 150, 150))
        d.text((370, yy + 14), "HIGH", font=F(14), fill="black", anchor="lm")
        d.rounded_rectangle([610, 426, 696, 458], radius=4, fill=SEL)
        d.text((653, 442), "OK", font=F(14, True), fill="white", anchor="mm")
        caption(d, "PASO 8", "Asigna cada pin: LED1 = 4 PD2/2 (pin D2) ... LED8 = 15 PB1/~9 (pin D9)",
                "Los numeros son las patitas del chip; despues de la '/' esta el pin del Arduino. Luego OK")
        return im, d

    for n in range(0, 9):
        im, d = props(n)
        if n:
            cursor(d, 590, 92 + (n - 1) * 38 + 14)
        p.add(im, 450 if n < 8 else 2500)
    im, d = props(8)
    flecha_mano(d, 653, 442)
    p.add(im, 1500)

    # ---- Paso 9: Save Workspace
    items = ["Load Hex", "Reload Last", "Save Hex", "-", "Configure", "-", "Save Workspace", "Load Workspace",
             "Load Board Demo", "-", "Exit"]

    def leds_al_lado(d):
        panel_leds(d, 620, 160, [True, False, False, False], ["D2", "D3", "D4", "D5"])
        d.text((760, 140), "Spare parts", font=F(13), fill=GRIS, anchor="mm")

    t9 = ("PASO 9", "File > Save Workspace  ->  Pregunta1.pzw",
          "El .pzw guarda placa + programa + componentes. Para abrirlo: File > Load Workspace")
    im, d, pos, _ = escena_psl(None, None, None, *t9, extra=leds_al_lado)
    cursor(d, 400, 300)
    p.add(im, 800)
    r = pos["File"]
    mover(p, lambda: escena_psl(None, None, None, *t9, extra=leds_al_lado)[:2], 400, 300, r[0] + 20, r[1] + 12)
    _, _, _, c = escena_psl("File", items, None, *t9, extra=leds_al_lado)
    tx, ty = c["Save Workspace"]
    mover(p, lambda: escena_psl("File", items, None, *t9, extra=leds_al_lado)[:2], r[0] + 20, r[1] + 12, tx, ty,
          pasos=6)
    im, d, _, _ = escena_psl("File", items, "Save Workspace", *t9, extra=leds_al_lado)
    flecha_mano(d, tx, ty)
    p.add(im, 4000)

    # ---- Final
    im, d = nuevo()
    titulo(d, "Atajo: usar los .pzw ya preparados")
    lineas = ["1. Abre PICSimLab", "2. File > Load Workspace",
              "3. Elige PreguntaN_xxx.pzw (carpeta de cada pregunta)",
              "4. Se cargan solos: placa Arduino Uno, programa y componentes",
              "5. Si algo cambia, vuelve a guardar con File > Save Workspace"]
    for i, l in enumerate(lineas):
        d.text((120, 110 + i * 56), l, font=F(24, i == 1), fill=TXT)
    caption(d, "", "Si no abre en tu version de PICSimLab, arma el circuito con las tablas de conexiones (PNG)")
    p.add(im, 5000)

    p.save("00_flujo_paso_a_paso.gif")


# ===========================================================================
#  Imagenes de conexiones
# ===========================================================================
NOMBRE_PIN = {2: "4  PD2/2", 3: "5  PD3/~3", 4: "6  PD4/4", 5: "11  PD5/~5", 6: "12  PD6/~6", 7: "13  PD7/7",
              8: "14  PB0/8", 9: "15  PB1/~9", 10: "16  PB2/~10", 11: "17  PB3/~11", 12: "18  PB4/12",
              13: "19  PB5/13", "A0": "23  PC0/A0", "A1": "24  PC1/A1"}


def tabla_conexiones(nombre, tit, filas, nota):
    alto = 130 + 34 * len(filas) + 60
    im = Image.new("RGB", (W, alto), BG)
    d = ImageDraw.Draw(im)
    d.text((W // 2, 30), tit, font=F(22, True), fill=TXT, anchor="mm")
    cols = [(30, "Menu Spare parts"), (290, "Componente / propiedad"), (590, "Pin en Properties"), (790, "Arduino")]
    y = 70
    d.rectangle([20, y, W - 20, y + 34], fill=SEL)
    for x, t in cols:
        d.text((x, y + 17), t, font=F(15, True), fill="white", anchor="lm")
    y += 34
    for i, (menu, comp, pin) in enumerate(filas):
        d.rectangle([20, y, W - 20, y + 34], fill=(62, 62, 70) if i % 2 else (55, 55, 62))
        d.text((30, y + 17), menu, font=F(14), fill=GRIS, anchor="lm")
        d.text((290, y + 17), comp, font=F(14), fill=TXT, anchor="lm")
        if isinstance(pin, str) and pin in NOMBRE_PIN or isinstance(pin, int):
            d.text((590, y + 17), NOMBRE_PIN[pin], font=F(14, mono=True), fill=AMARILLO, anchor="lm")
            d.text((790, y + 17), pin if isinstance(pin, str) else "D%d" % pin, font=F(14, True), fill=TXT, anchor="lm")
        else:
            d.text((590, y + 17), str(pin), font=F(14, mono=True), fill=AMARILLO, anchor="lm")
        y += 34
    d.text((30, y + 24), nota, font=F(14), fill=(200, 200, 200), anchor="lm")
    ruta = os.path.join(SALIDA, nombre)
    im.save(ruta)
    print("Generado", os.path.relpath(ruta, RAIZ))


def conexiones():
    leds = [("Outputs > LEDs", "LEDs  %d-D%d" % (i + 1, i + 1), i + 2) for i in range(8)]
    tabla_conexiones("01_pregunta1_conexiones.png", "Pregunta 1 - Conexiones (Board: Arduino Uno / atmega328p)",
                     leds + [("", "LEDs  Active", "HIGH")] +
                     [("Inputs > Push Buttons", "Push Buttons  %d -Out %d" % (i + 2, i + 1), 10 + i) for i in range(4)] +
                     [("", "Push Buttons  Active", "LOW"), ("", "Push Buttons  Size", "4")],
                     "Botones en Active = LOW porque el codigo usa INPUT_PULLUP (presionado = LOW).")
    tabla_conexiones("02_pregunta2_conexiones.png", "Pregunta 2 - Conexiones (Board: Arduino Uno / atmega328p)",
                     leds + [("Inputs > Push Buttons", "Push Buttons  2 -Out 1  (DERECHA)", 10),
                             ("", "Push Buttons  3 -Out 2  (IZQUIERDA)", 11),
                             ("", "Push Buttons  Active", "LOW"),
                             ("Inputs > Potentiometers", "Potentiometers  2-POT 1  (timon)", "A0"),
                             ("Inputs > LDR", "LDR  3 - A0  (salida analogica)", "A1"),
                             ("", "LDR  2 - D0", "0  NC")],
                     "Timon: potenciometro a la mitad = centro. LDR: slider abajo = poca luz (modo nocturno).")
    tabla_conexiones("03_pregunta3_conexiones.png", "Pregunta 3 - Conexiones (Board: Arduino Uno / atmega328p)",
                     [("Outputs > LCD hd44780", "LCD  4-RS", 12), ("", "LCD  6-EN", 11),
                      ("", "LCD  5-RW", "0  NC"), ("", "LCD  7..10-D0..D3", "0  NC"),
                      ("", "LCD  11-D4", 5), ("", "LCD  12-D5", 4), ("", "LCD  13-D6", 3), ("", "LCD  14-D7", 2),
                      ("", "LCD  Model", "16x2"),
                      ("Inputs > Ultrasonic HC-SR04", "HC-SR04  2 - TRIG", 7), ("", "HC-SR04  3 - ECHO", 8),
                      ("Outputs > Buzzer", "Buzzer  Pin 1   (Type: Tone)", 6),
                      ("Outputs > LEDs", "LEDs  1-D1  (LED de alarma, Size 1)", 13),
                      ("Outputs > Servo Motor", "Servo  Pin 1  (valvula)", 9)],
                     "HC-SR04: el slider va de 0 a 400 cm. <= 30 cm => 90 % (alarma).  >= 45 cm => 85 % (se apaga).")


# ===========================================================================
#  Pregunta 1 - simulacion
# ===========================================================================
def p1_frame(estados, sec, boton=None, nota=""):
    im, d = nuevo()
    titulo(d, "Pregunta 1 - Secuencias de LEDs (comportamiento esperado)")
    panel_leds(d, 120, 90, estados)
    panel_botones(d, 120, 240, ["B1 (D10)", "B2 (D11)", "B3 (D12)", "B4 (D13)"], boton)
    nombres = {0: "Ninguna secuencia (sec = 0)", 1: "secx1(): corrimiento 2 -> 9",
               2: "secx2(): ida y vuelta (auto fantastico)", 3: "secx3(): parpadeo de todos (300 ms)",
               4: "secx4(): gusano de 4 LEDs"}
    d.text((120, 370), "Secuencia activa:", font=F(18), fill=GRIS)
    d.text((300, 370), nombres[sec], font=F(18, True), fill=AMARILLO)
    if nota:
        d.text((120, 410), nota, font=F(15), fill=(200, 200, 200))
    caption(d, "", "Mantener presionado el boton hasta que termine el ciclo actual",
            "Los botones se leen solo entre ciclos porque las secuencias usan delay()")
    return im


def p1():
    p = Pelicula()
    N = 8
    off = [False] * N
    p.add(p1_frame(off, 0, nota="Al iniciar no se enciende nada"), 1500)
    T = 150

    def secx1():
        for i in range(N):
            e = off[:]
            e[i] = True
            yield e, T

    def secx2():
        yield from secx1()
        for i in range(N - 1, 0, -1):
            e = off[:]
            e[i] = True
            yield e, T

    def secx3():
        yield [True] * N, 300
        yield off, 300

    def secx4():
        for i in range(N):
            e = off[:]
            for k in range(4):
                if i - k >= 0:
                    e[i - k] = True
            yield e, T

    for sec, gen, ciclos in [(1, secx1, 2), (2, secx2, 2), (3, secx3, 4), (4, secx4, 2)]:
        p.add(p1_frame(off, sec, sec - 1, "Boton presionado: limpiarLeds() + delay(200)"), 200)
        for c in range(ciclos):
            for e, ms in gen():
                p.add(p1_frame(e, sec, None, "Ciclo %d" % (c + 1)), ms)
    p.save("01_pregunta1_simulacion.gif")


# ===========================================================================
#  Pregunta 2 - simulacion (replica la logica del .ino con pasos de 40 ms)
# ===========================================================================
def dibujar_timon(d, cx, cy, valor):
    ang = (valor - 512) / 512.0 * 60.0
    d.text((cx, cy - 92), "Timon (POT en A0) = %d" % valor, font=F(14), fill=TXT, anchor="mm")
    d.arc([cx - 70, cy - 70, cx + 70, cy + 70], 200, 340, fill=(90, 90, 90), width=6)
    d.arc([cx - 70, cy - 70, cx + 70, cy + 70], 262, 278, fill=(80, 200, 80), width=6)
    a = math.radians(-90 + ang)
    hx, hy = cx + 80 * math.cos(a + math.pi / 2), cy + 80 * math.sin(a + math.pi / 2)
    gx, gy = cx - 80 * math.cos(a + math.pi / 2), cy - 80 * math.sin(a + math.pi / 2)
    d.line([gx, gy, hx, hy], fill=(200, 200, 200), width=10)
    d.ellipse([gx - 9, gy - 9, gx + 9, gy + 9], fill=(40, 40, 40))
    d.ellipse([hx - 9, hy - 9, hx + 9, hy + 9], fill=(40, 40, 40))
    d.ellipse([cx - 10, cy - 10, cx + 10, cy + 10], fill=(120, 120, 120))
    d.line([cx, cy, cx + 50 * math.cos(a), cy + 50 * math.sin(a)], fill=AMARILLO, width=3)
    txt = "CENTRO" if abs(valor - 512) < 80 else ("DERECHA" if valor > 512 else "IZQUIERDA")
    d.text((cx, cy + 40), txt, font=F(13, True), fill=AMARILLO, anchor="mm")


def dibujar_ldr(d, cx, cy, oscuro, lectura):
    d.text((cx, cy - 92), "LDR en A1 = %d" % lectura, font=F(14), fill=TXT, anchor="mm")
    if oscuro:
        d.ellipse([cx - 40, cy - 50, cx + 40, cy + 30], fill=(230, 230, 180))
        d.ellipse([cx - 20, cy - 62, cx + 60, cy + 18], fill=BG)
        d.text((cx, cy + 50), "NOCHE", font=F(14, True), fill=(160, 160, 255), anchor="mm")
    else:
        d.ellipse([cx - 30, cy - 40, cx + 30, cy + 20], fill=AMARILLO)
        for k in range(8):
            a = k * math.pi / 4
            d.line([cx + 38 * math.cos(a), cy - 10 + 38 * math.sin(a), cx + 52 * math.cos(a),
                    cy - 10 + 52 * math.sin(a)], fill=AMARILLO, width=4)
        d.text((cx, cy + 50), "DIA", font=F(14, True), fill=AMARILLO, anchor="mm")


def p2():
    p = Pelicula()
    TICK = 40
    N = 8
    # guion: (hasta_ms, timon, ldr, boton, texto)
    guion = [
        (1500, 512, 50, None, "De dia y sin direccional: LEDs apagados"),
        (1700, 512, 50, 0, "Se pulsa DERECHA"),
        (4500, 512, 50, None, "Flecha hacia la derecha (luz que corre de D2 a D9)"),
        (6000, "->850", 50, None, "Se gira el timon a la derecha (la direccional sigue)"),
        (7000, 850, 50, None, "Se gira el timon a la derecha (la direccional sigue)"),
        (8200, "->512", 50, None, "El timon regresa al centro -> se apaga sola"),
        (9500, 512, 50, None, "El timon regresa al centro -> se apaga sola"),
        (9700, 512, 50, 1, "Se pulsa IZQUIERDA"),
        (12000, 512, 50, None, "Flecha hacia la izquierda (D9 a D2)"),
        (13200, "->170", 50, None, "Giro a la izquierda..."),
        (14000, 170, 50, None, "Giro a la izquierda..."),
        (15200, "->512", 50, None, "...y vuelta al centro -> se apaga"),
        (16000, 512, 50, None, "...y vuelta al centro -> se apaga"),
        (16600, 512, "->900", None, "Oscurece (LDR > 600)"),
        (20000, 512, 900, None, "De noche: todos los LEDs intermitentes (400 ms)"),
        (20200, 512, 900, 0, "De noche se pulsa DERECHA"),
        (23500, 512, 900, None, "Flecha con 'cola' de 2 LEDs para verse mejor"),
        (24500, "->850", 900, None, "Giro y regreso al centro..."),
        (25500, "->512", 900, None, "Giro y regreso al centro..."),
        (28000, 512, 900, None, "...vuelve el parpadeo nocturno"),
    ]

    estado = "APAGADO"
    timon_giro = False
    oscuro = False
    paso = 0
    encendido = False
    t_ant = 0
    leds = [False] * N
    t = 0
    tim_val, ldr_val = 512, 50
    seg_ini = 0
    tim_ini, ldr_ini = 512, 50

    def interp(spec, ini, prog):
        if isinstance(spec, str):
            obj = int(spec[2:])
            return int(ini + (obj - ini) * prog)
        return spec

    for hasta, tim, ldr, boton, texto in guion:
        tim_ini, ldr_ini = tim_val, ldr_val
        seg_ini = t
        while t < hasta:
            prog = (t - seg_ini) / max(1, hasta - seg_ini)
            tim_val = interp(tim, tim_ini, prog)
            ldr_val = interp(ldr, ldr_ini, prog)
            # leerBotones / activar
            if boton is not None:
                nuevo_e = "DERECHA" if boton == 0 else "IZQUIERDA"
                if estado != nuevo_e:
                    estado, timon_giro, paso, t_ant = nuevo_e, False, 0, -10 ** 9
                    leds = [False] * N
            # vigilarTimon
            if estado != "APAGADO":
                desv = tim_val - 512
                if abs(desv) > 200:
                    timon_giro = True
                if timon_giro and abs(desv) < 80:
                    estado = "APAGADO"
                    leds = [False] * N
                    t_ant = -10 ** 9
            # leerLuz
            if not oscuro and ldr_val > 600:
                oscuro = True
            elif oscuro and ldr_val < 550:
                oscuro = False
            # salidas
            if estado in ("DERECHA", "IZQUIERDA"):
                if t - t_ant >= 120:
                    t_ant = t
                    leds = [False] * N
                    if paso < N:
                        idx = paso if estado == "DERECHA" else N - 1 - paso
                        leds[idx] = True
                        if oscuro and paso > 0:
                            leds[idx - 1 if estado == "DERECHA" else idx + 1] = True
                    paso = (paso + 1) % (N + 1)
            else:
                if oscuro:
                    if t - t_ant >= 400:
                        t_ant = t
                        encendido = not encendido
                        leds = [encendido] * N
                else:
                    leds = [False] * N

            im, d = nuevo()
            titulo(d, "Pregunta 2 - Direccional de bicicleta (comportamiento esperado)")
            panel_leds(d, 40, 50, leds)
            panel_botones(d, 40, 175, ["DERECHA (D10)", "IZQUIERDA (D11)"], boton, sep=150)
            dibujar_timon(d, 520, 330, tim_val)
            dibujar_ldr(d, 790, 330, oscuro, ldr_val)
            col = {"APAGADO": GRIS, "DERECHA": AMARILLO, "IZQUIERDA": AMARILLO}[estado]
            d.text((40, 300), "Estado:", font=F(18), fill=GRIS)
            d.text((120, 300), estado, font=F(18, True), fill=col)
            if estado != "APAGADO":
                d.text((40, 330), "timon ya giro: %s" % ("si" if timon_giro else "no"), font=F(15),
                       fill=(200, 200, 200))
            d.text((40, 355), "oscuro: %s" % ("si" if oscuro else "no"), font=F(15), fill=(200, 200, 200))
            caption(d, "", texto)
            p.add(im, TICK)
            t += TICK
    p.save("02_pregunta2_simulacion.gif")


# ===========================================================================
#  Pregunta 3 - simulacion
# ===========================================================================
H_TANQUE = 3.0
R_TANQUE = 1.5
AREA = math.pi * R_TANQUE ** 2
VTOT = AREA * H_TANQUE


def fmt(v, dig):
    """Equivalente a lcd.print(valor, digitos) de Arduino (redondea)."""
    return "%.*f" % (dig, v)


def lcd_texto(nivel, alarma):
    vol = AREA * nivel
    pc = vol * 100 / VTOT
    l1 = ("V=" + fmt(vol, 2) + "m3 " + str(int(pc + 0.5)) + "%    ")[:16].ljust(16)
    l2 = ("h=" + fmt(nivel, 2) + "m " + ("ALARMA " if alarma else "Normal "))[:16].ljust(16)
    return l1, l2, vol, pc


def p3():
    p = Pelicula()
    # guion de nivel (m): sube hasta 90 %, se abre la valvula, baja hasta 85 %, se cierra, vuelve a subir
    puntos = []
    nivel = 2.2
    alarma = False
    fase = False
    t = 0
    while t < 26000:
        # dinamica: entra agua siempre; si la valvula esta abierta sale mas de lo que entra
        nivel += (0.012 if not alarma else -0.010)
        nivel = max(0.0, min(H_TANQUE, nivel))
        d_cm = (H_TANQUE - nivel) * 100
        vol = AREA * nivel
        pc = vol * 100 / VTOT
        if not alarma and pc >= 90:
            alarma = True
        elif alarma and pc <= 85:
            alarma = False
        if alarma:
            fase = not fase
        puntos.append((nivel, d_cm, alarma, fase))
        t += 250

    for nivel, d_cm, alarma, fase in puntos:
        im, d = nuevo()
        titulo(d, "Pregunta 3 - Nivel de tanque (comportamiento esperado)")
        # tanque
        tx, ty, tw, th = 70, 80, 220, 340
        esc = th / H_TANQUE
        d.rectangle([tx, ty, tx + tw, ty + th], outline=(200, 200, 200), width=3)
        agua = ty + th - nivel * esc
        d.rectangle([tx + 3, agua, tx + tw - 3, ty + th - 3], fill=AGUA)
        for pc_m, col, lab in [(0.90, (255, 90, 90), "90 % (2.70 m)"), (0.85, (255, 200, 60), "85 % (2.55 m)")]:
            yy = ty + th - pc_m * H_TANQUE * esc
            for xx in range(tx, tx + tw, 12):
                d.line([xx, yy, xx + 6, yy], fill=col, width=2)
            d.text((tx + tw + 8, yy), lab, font=F(12), fill=col, anchor="lm")
        d.text((tx + tw // 2, ty + th + 14), "H = 3 m   r = 1,5 m", font=F(13), fill=GRIS, anchor="mm")
        # sensor
        d.rectangle([tx + 70, ty - 26, tx + 150, ty - 4], fill=(30, 110, 200))
        d.ellipse([tx + 76, ty - 24, tx + 96, ty - 6], fill=(200, 200, 200))
        d.ellipse([tx + 124, ty - 24, tx + 144, ty - 6], fill=(200, 200, 200))
        d.text((tx + 110, ty - 38), "HC-SR04", font=F(12, True), fill=TXT, anchor="mm")
        for yy in range(int(ty), int(agua), 10):
            d.line([tx + 110, yy, tx + 110, min(yy + 5, agua)], fill=AMARILLO, width=2)
        d.text((tx + 118, (ty + agua) / 2), "d = %d cm" % round(d_cm), font=F(13, True), fill=AMARILLO, anchor="lm")
        # desague + servo
        vx, vy = tx + tw, ty + th - 50
        d.rectangle([vx, vy - 8, vx + 90, vy + 8], fill=(150, 150, 150))
        ang = 90 if alarma else 0
        d.ellipse([vx + 30, vy - 18, vx + 66, vy + 18], fill=(80, 80, 80))
        a = math.radians(ang)
        d.line([vx + 48 - 18 * math.cos(a), vy - 18 * math.sin(a), vx + 48 + 18 * math.cos(a), vy + 18 * math.sin(a)],
               fill=AMARILLO, width=5)
        if alarma:
            for k in range(4):
                d.line([vx + 92 + k * 3, vy + 4 + k * 14, vx + 92 + k * 3, vy + 14 + k * 14], fill=AGUA, width=4)
        d.text((vx + 48, vy + 34), "Servo %d°" % ang, font=F(13, True), fill=TXT, anchor="mm")
        d.text((vx + 48, vy + 52), "ABIERTA" if alarma else "cerrada", font=F(12), fill=AMARILLO if alarma else GRIS,
               anchor="mm")
        # LCD
        l1, l2, vol, pc = lcd_texto(nivel, alarma)
        lx, ly = 520, 90
        d.rounded_rectangle([lx, ly, lx + 400, ly + 130], radius=8, fill=(20, 80, 30), outline=(10, 40, 15), width=3)
        d.rectangle([lx + 18, ly + 22, lx + 382, ly + 108], fill=VERDE_LCD)
        d.text((lx + 28, ly + 30), l1, font=F(25, mono=True), fill=(20, 40, 20))
        d.text((lx + 28, ly + 68), l2, font=F(25, mono=True), fill=(20, 40, 20))
        d.text((lx + 200, ly - 14), "LCD 16x2", font=F(13), fill=GRIS, anchor="mm")
        # LED alarma y buzzer
        on = alarma and fase
        d.text((560, 260), "LED alarma (D13)", font=F(14), fill=TXT)
        d.ellipse([600, 290, 650, 340], fill=LED_ON if on else LED_OFF, outline="black", width=2)
        d.text((760, 260), "Buzzer (D6)", font=F(14), fill=TXT)
        d.polygon([(770, 300), (790, 300), (810, 285), (810, 345), (790, 330), (770, 330)], fill=(200, 200, 200))
        if alarma:
            for k in range(3):
                d.arc([800 + k * 12 - 20, 295 - k * 12, 840 + k * 12, 335 + k * 12], -45, 45, fill=AMARILLO, width=3)
            d.text((860, 360), "%d Hz" % (2000 if fase else 1000), font=F(13, True), fill=AMARILLO, anchor="mm")
        # barra de porcentaje
        d.rectangle([520, 400, 920, 430], outline=GRIS, width=2)
        d.rectangle([522, 402, 522 + 396 * min(pc, 100) / 100, 428], fill=(255, 90, 90) if alarma else AGUA)
        d.text((720, 445), "%.1f %% de %.2f m3" % (pc, VTOT), font=F(14), fill=TXT, anchor="mm")
        if alarma:
            txt = "ALARMA: >= 90 %. Buzzer + LED + valvula abierta hasta bajar a 85 %"
        elif nivel > 2.5:
            txt = "Normal: la alarma se activa al llegar a 90 % (19,09 m3)"
        else:
            txt = "Normal: el tanque se esta llenando"
        caption(d, "", txt, "V = pi * r^2 * h   (h = 3 m - distancia medida por el HC-SR04)")
        p.add(im, 250)
    p.save("03_pregunta3_simulacion.gif")


if __name__ == "__main__":
    os.makedirs(SALIDA, exist_ok=True)
    conexiones()
    flujo()
    p1()
    p2()
    p3()
