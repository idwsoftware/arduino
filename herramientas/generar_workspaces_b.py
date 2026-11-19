#!/usr/bin/env python3
"""
Genera los Workspace de PICSimLab (.pzw) del Examen version B (carpeta Examen_B/).
Reutiliza el formato y las funciones de generar_workspaces.py.

Uso: python3 herramientas/generar_workspaces_b.py <carpeta_build_opcional>
"""
import os
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from generar_workspaces import PIN, NC, leds, botones, potenciometros, ldr, pcf, ini  # noqa: E402

RAIZ = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Examen_B")

ROJO, VERDE, AMARILLO = 0, 1, 3


def leds_color(pines, colores, x, y):
    """LEDs con color por LED (0=Red, 1=Green, 2=Blue, 3=Yellow, 4=White)."""
    p = [PIN[n] for n in pines] + [NC] * (8 - len(pines))
    c = list(colores) + [0] * (8 - len(colores))
    return "LEDs,%d,%d,0:%s,1,%s,%d" % (x, y, ",".join(map(str, p)), ",".join(map(str, c)), len(pines))


def display_7s(segmentos, x, y):
    """7 Segments Display tipo Single: a..g, punto, D1..D4, active(1=HIGH), tipo(1=Single)."""
    p = [PIN[n] for n in segmentos] + [NC]          # punto sin conectar
    return "7 Segments Display,%d,%d,0:%s,0,0,0,0,1,1" % (x, y, ",".join(map(str, p)))


def terminal_virtual(x, y):
    """IO Virtual Term: RX = pin 3 (PD1/TX del Arduino), TX = pin 2 (PD0/RX), 9600 baudios, visible."""
    return "IO Virtual Term,%d,%d,0:3,2,1,9600,1,620,120,420,360,0,*" % (x, y)


PREGUNTAS = {
    "Pregunta1_Secuencias_LEDs": (
        [leds([2, 3, 4, 5, 6, 7, 8, 9], 20, 20), botones([10, 11, 12, 13], 20, 170)],
        640, 340,
    ),
    "Pregunta2_Direccional_Bicicleta": (
        [
            leds([2, 3, 4, 5, 6, 7, 8, 9], 20, 20),
            botones([10, 11], 20, 170),
            potenciometros(["A0"], [100], 20, 310),   # timon al centro
            ldr("A1", 330, 310, 0),                    # de dia al iniciar
        ],
        640, 600,
    ),
    "Pregunta3_Semaforo": (
        [
            leds_color([2, 3, 4], [ROJO, AMARILLO, VERDE], 20, 20),     # Via Principal
            leds_color([5, 6, 7], [ROJO, AMARILLO, VERDE], 20, 150),    # Via Secundaria
            botones([8], 20, 280),                                       # HORA PUNTA
            ldr("A0", 300, 20, 0),                                       # de dia al iniciar
            display_7s([9, 10, 11, 12, 13, "A1", "A2"], 500, 20),
            terminal_virtual(300, 300),
        ],
        820, 520,
    ),
}


def main():
    build = sys.argv[1] if len(sys.argv) > 1 else None
    for nombre, (partes, w, h) in PREGUNTAS.items():
        carpeta = os.path.join(RAIZ, nombre)
        if build:
            hexf = os.path.join(build, nombre, nombre + ".ino.with_bootloader.hex")
        else:
            hexf = os.path.join(carpeta, nombre + ".ino.hex")
        with open(hexf) as f:
            hexdata = f.read()
        salida = os.path.join(carpeta, nombre + ".pzw")
        with zipfile.ZipFile(salida, "w", zipfile.ZIP_DEFLATED) as z:
            z.writestr("picsimlab_workspace/", "")
            z.writestr("picsimlab_workspace/picsimlab.ini", ini())
            z.writestr("picsimlab_workspace/parts_Arduino_Uno.pcf", pcf(partes, w, h))
            z.writestr("picsimlab_workspace/mdump_Arduino_Uno_atmega328p.hex", hexdata)
        print("Generado", os.path.relpath(salida, os.path.dirname(RAIZ)))


if __name__ == "__main__":
    main()
