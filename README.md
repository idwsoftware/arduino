# Examen Unidad II – Arquitectura de Computadoras (2026-II)

Resolución de las 3 preguntas con Arduino Uno, para simular en **PICSimLab**.
Cada carpeta tiene:
- el sketch `.ino` (se abre en el IDE de Arduino),
- el `.hex` ya compilado (en PICSimLab: *File → Load Hex*),
- el workspace `.pzw` de PICSimLab con la placa, el programa y los componentes ya conectados
  (en PICSimLab: *File → Load Workspace*).

📘 **Guía paso a paso con animaciones:** [GUIA_PICSIMLAB.md](GUIA_PICSIMLAB.md)

| Carpeta | Pregunta |
|---|---|
| `Pregunta1_Secuencias_LEDs/` | 1. 4 secuencias de LEDs que se eligen con pulsadores |
| `Pregunta2_Direccional_Bicicleta/` | 2. Direccional de bicicleta con cancelación automática y modo nocturno |
| `Pregunta3_Nivel_Tanque/` | 3. Nivel de un tanque con HC-SR04, LCD, buzzer, LED y servo |

> **Sobre los `.pzw`:** se generaron con `herramientas/generar_workspaces.py`, siguiendo el formato del
> código fuente de PICSimLab 0.9.x. No se abrieron en PICSimLab. Si tu versión no los abre bien,
> arma el circuito con las tablas de abajo y guárdalo con *File → Save Workspace*.

Configuración común en PICSimLab: *Board* = **Arduino Uno**, *Microcontroller* = **atmega328p**,
luego *Modules → Spare parts* para agregar los componentes.

---

## Pregunta 1 – Funcionamiento del código

**Pines**
- LEDs en los pines digitales **2 a 9** (`primerPin`..`ultimoPin`), salidas.
- Pulsadores `b1..b4` en los pines **10, 11, 12, 13** con `INPUT_PULLUP`: el pin está en HIGH por la
  resistencia interna y pasa a **LOW al presionar** (el botón conecta el pin a GND).

**`setup()`** configura los 8 LEDs como salida y los 4 botones como entrada con pull-up.

**`loop()`**
1. Lee cada botón. Si alguno está en LOW, guarda en `sec` el número de la secuencia (1–4), apaga todos
   los LEDs con `limpiarLeds()` y espera 200 ms (antirrebote sencillo).
2. Con `switch(sec)` ejecuta **un ciclo completo** de la secuencia elegida. Como `sec` se queda guardado,
   la secuencia se repite hasta que se pulse otro botón. Al inicio `sec = 0`, así que no pasa nada.
3. Los botones solo se leen **entre** ciclos, porque las secuencias usan `delay()`. Por eso hay que mantener
   el botón presionado hasta que termine el ciclo en curso (hasta unos 2,25 s en `secx2`).

**Secuencias** (`tiempo` = 150 ms)
| Botón | Función | Efecto |
|---|---|---|
| b1 (pin 10) | `secx1` | Un solo LED encendido que avanza del 2 al 9 (izquierda → derecha). 8 × 150 ms = 1,2 s |
| b2 (pin 11) | `secx2` | "Auto fantástico": va del 2 al 9 y vuelve del 9 al 3 (el 2 no se repite, para que el bucle sea continuo). 15 × 150 ms |
| b3 (pin 12) | `secx3` | Todos los LEDs parpadean juntos: 300 ms encendidos y 300 ms apagados |
| b4 (pin 13) | `secx4` | "Gusano": un bloque de hasta 4 LEDs (`longitud`) avanza. En el paso `i` se encienden `i, i-1, i-2, i-3` (solo los que son ≥ 2), espera 150 ms y los apaga. El bloque va creciendo al entrar (1, 2, 3, 4 LEDs) y luego se desplaza |

**Circuito en PICSimLab**
- *LEDs* (8 LEDs): LED1..LED8 → pines **2..9**
- *Push buttons* (4 botones, modo activo en bajo): B1..B4 → pines **10..13**

> Nota para una placa real: el pin 13 tiene el LED "L" integrado, que puede debilitar el pull-up interno.
> En el simulador funciona sin problema.

---

## Pregunta 2 – Direccional para bicicleta

**Conexiones**
| Componente (Spare parts) | Pin |
|---|---|
| *LEDs* (8) LED1..LED8 | 2..9 (2 = extremo izquierdo, 9 = extremo derecho) |
| *Push buttons* – botón DERECHA | 10 (activo en bajo, `INPUT_PULLUP`) |
| *Push buttons* – botón IZQUIERDA | 11 (activo en bajo, `INPUT_PULLUP`) |
| *Potentiometers* – posición del timón | A0 (centro ≈ 512) |
| *LDR* (salida `3 - A0` del módulo) | A1 (valor **alto** = oscuro) |

**Lógica**
- Al pulsar **DERECHA** se enciende una luz que corre de izquierda a derecha (flecha →), como en las imágenes
  del enunciado. **IZQUIERDA** hace lo mismo en sentido contrario.
- **Cancelación automática:** el potenciómetro representa el timón. Después de activar la direccional,
  el programa espera a que el timón **gire** (se aleje más de 200 del centro) y luego **vuelva al centro**
  (±80). En ese momento la direccional se apaga sola, como en un auto.
- **Oscuridad:** si el LDR marca oscuro (> 600, con histéresis) y no hay direccional activa, los 8 LEDs
  **parpadean** cada 400 ms. Si hay una direccional activa de noche, la flecha se muestra con "cola"
  (2 LEDs) para que se vea mejor.
- Todo usa `millis()` (sin `delay`), así los botones y el timón se leen siempre.

---

## Pregunta 3 – Medidor de nivel del tanque

**Datos:** cilindro de altura **H = 3 m** y radio **r = 1,5 m**
- Área de la base = π·r² = π·2,25 = **7,069 m²**
- Volumen total = π·r²·H = **21,206 m³**
- 90 % = **19,085 m³** → se activa la alarma (nivel 2,70 m)
- 85 % = **18,025 m³** → se apaga la alarma (nivel 2,55 m)

**Principio:** el HC-SR04 está en la tapa, mirando hacia abajo.
`distancia = tiempo_eco · 0,0343 / 2` (cm) → `nivel h = H − distancia` → `V = π·r²·h`.
Entre 85 % y 90 % hay **histéresis**: la alarma se activa al llegar al 90 % y sigue activa (con la válvula
abierta desaguando) hasta que el volumen baja al 85 %.

**Al activarse la alarma:** el buzzer suena alternando entre 2 kHz y 1 kHz, el LED de alarma parpadea y el
servo gira a 90° (válvula de desagüe abierta). Al llegar al 85 % se apaga todo y el servo vuelve a 0°.

**LCD 16x2:**
```
V=19.30m3 91%
h=2.73m ALARMA
```

**Conexiones**
| Componente | Pin |
|---|---|
| *LCD hd44780* 16x2 | RS=12, EN=11, D4=5, D5=4, D6=3, D7=2 |
| *Ultrasonic HC-SR04* | TRIG=7, ECHO=8 |
| *Buzzer* (Type: **Tone**, porque se usa `tone()`) | 6 |
| *LEDs* (LED de alarma) | 13 |
| *Servo motor* | 9 |

En PICSimLab, mueve la distancia del HC-SR04: **30 cm o menos** (nivel ≥ 2,70 m) activa la alarma;
**45 cm o más** (nivel ≤ 2,55 m) la apaga.

---

## Otras carpetas

| Carpeta | Contenido |
|---|---|
| `animaciones/` | GIF del flujo paso a paso, simulaciones del comportamiento esperado y tablas de conexiones (PNG) |
| `herramientas/` | Scripts de Python que generan los `.pzw` y las animaciones |

## Compilación

Los sketches se compilaron para `arduino:avr:uno` con el núcleo Arduino AVR y las librerías
`LiquidCrystal` y `Servo`, que ya vienen incluidas en el IDE de Arduino.
