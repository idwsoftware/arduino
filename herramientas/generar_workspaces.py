#!/usr/bin/env python3
"""
Genera los Workspace de PICSimLab (.pzw) de las 3 preguntas.

Un .pzw es un ZIP con la carpeta "picsimlab_workspace/" que contiene:
  - picsimlab.ini                         -> placa, micro y reloj
  - parts_Arduino_Uno.pcf                 -> componentes de "Spare parts" y sus pines
  - mdump_Arduino_Uno_atmega328p.hex      -> programa cargado en la flash

Formato tomado del codigo fuente de PICSimLab 0.9.x (github.com/lcgamboa/picsimlab).
Los pines usan la numeracion fisica del ATmega328P DIP-28 que muestra PICSimLab:
  D2=4 (PD2/2) ... D7=13, D8=14 ... D13=19, A0=23, A1=24 ; 0 = NC (sin conectar)

Uso:  python3 herramientas/generar_workspaces.py <carpeta_build_con_hex_with_bootloader opcional>
Si no se indica carpeta, usa el .ino.hex de cada pregunta.
"""
import os
import sys
import time
import zipfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Pin Arduino -> pin del ATmega328P DIP-28 (como lo numera PICSimLab)
PIN = {2: 4, 3: 5, 4: 6, 5: 11, 6: 12, 7: 13, 8: 14, 9: 15, 10: 16, 11: 17, 12: 18, 13: 19,
       "A0": 23, "A1": 24, "A2": 25, "A3": 26, "A4": 27, "A5": 28}
NC = 0


def leds(pines, x, y):
    """LEDs: 8 pines, active(1=HIGH), 8 colores (0=rojo), tamano."""
    p = [PIN[n] for n in pines] + [NC] * (8 - len(pines))
    return "LEDs,%d,%d,0:%s,1,%s,%d" % (x, y, ",".join(map(str, p)), ",".join(["0"] * 8), len(pines))


def botones(pines, x, y):
    """Push Buttons: 8 pines, active(0=LOW), mode(0=normal), tamano."""
    p = [PIN[n] for n in pines] + [NC] * (8 - len(pines))
    return "Push Buttons,%d,%d,0:%s,0,0,%d" % (x, y, ",".join(map(str, p)), len(pines))


def potenciometros(pines, valores, x, y):
    """Potentiometers: 4 pines, 4 valores (0..200 => 0..5 V), tamano."""
    p = [PIN[n] for n in pines] + [NC] * (4 - len(pines))
    v = list(valores) + [0] * (4 - len(valores))
    return "Potentiometers,%d,%d,0:%s,%s,%d" % (x, y, ",".join(map(str, p)), ",".join(map(str, v)), len(pines))


def ldr(pin_analog, x, y, valor=0):
    """LDR: pin D0 (digital), pin A0 (analogico), valor slider (0=mucha luz, 200=oscuro), Vth."""
    return "LDR,%d,%d,0:%d,%d,%d,2.500000" % (x, y, NC, PIN[pin_analog], valor)


def lcd(rs, en, d4, d5, d6, d7, x, y):
    """LCD hd44780: RS, EN, D0..D7, RW, modelo (1 = 16x2)."""
    p = [PIN[rs], PIN[en], NC, NC, NC, NC, PIN[d4], PIN[d5], PIN[d6], PIN[d7], NC, 1]
    return "LCD hd44780,%d,%d,0:%s" % (x, y, ",".join(map(str, p)))


def hcsr04(trig, echo, distancia_cm, x, y):
    """Ultrasonic HC-SR04: TRIG, ECHO, valor slider (distancia = 400*(200-valor)/200 cm)."""
    valor = int(round(200 - distancia_cm / 2.0))
    return "Ultrasonic HC-SR04,%d,%d,0:%d,%d,%d" % (x, y, PIN[trig], PIN[echo], valor)


def buzzer(pin, x, y):
    """Buzzer: pin, tipo (0=Active, 1=Passive, 2=Tone), active(1=HIGH). Tone sirve para tone()."""
    return "Buzzer,%d,%d,0:%d,2,1" % (x, y, PIN[pin])


def servo(pin, x, y):
    return "Servo Motor,%d,%d,0:%d" % (x, y, PIN[pin])


def pcf(partes, ancho, alto):
    cab = [
        "version,0,0,0:0.9.0",
        "scale,0,0,0:1.000000",
        "position,600,40,%d:%d" % (ancho, alto),
        "boardp,40,40,573:308",
        "spare_on,0,0,0:1",
        "osc_on,0,0,0:0",
        "useAlias,0,0,0:0",
        "debug,0,1,0:",
        "bgcolor,0,0,0:#323232",
    ]
    return "\n".join(cab + partes) + "\n"


def ini():
    fecha = time.strftime("%a %b %d %H:%M:%S %Y")
    filas = [
        ("picsimlab_version", "0.9.0"),
        ("picsimlab_lab", "Arduino_Uno"),
        ("picsimlab_debug", "0"),
        ("picsimlab_debugt", "1"),
        ("picsimlab_debugp", "1234"),
        ("picsimlab_position", "40,40"),
        ("picsimlab_scale", "0.900000"),
        ("osc_on", "0"),
        ("spare_on", "1"),
        ("picsimlab_lfile", " "),
        ("pzw_creation_date", fecha),
        ("pzw_modify_date", fecha),
        ("Arduino_Uno_proc", "atmega328p"),
        ("Arduino_Uno_clock", "16.0"),
    ]
    return "".join('%s\t= "%s"\n' % f for f in filas)


PREGUNTAS = {
    "Pregunta1_Secuencias_LEDs": (
        [
            leds([2, 3, 4, 5, 6, 7, 8, 9], 20, 20),
            botones([10, 11, 12, 13], 20, 170),
        ],
        640, 340,
    ),
    "Pregunta2_Direccional_Bicicleta": (
        [
            leds([2, 3, 4, 5, 6, 7, 8, 9], 20, 20),
            botones([10, 11], 20, 170),
            potenciometros(["A0"], [100], 20, 310),   # timon al centro (2,5 V)
            ldr("A1", 330, 310, 0),                    # mucha luz al iniciar
        ],
        640, 600,
    ),
    "Pregunta3_Nivel_Tanque": (
        [
            lcd(12, 11, 5, 4, 3, 2, 20, 20),
            hcsr04(7, 8, 100, 530, 20),                # 100 cm -> nivel 2 m (66 %)
            servo(9, 530, 290),
            buzzer(6, 330, 410),
            leds([13], 20, 410),
        ],
        880, 600,
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
        print("Generado", os.path.relpath(salida, RAIZ))


if __name__ == "__main__":
    main()
