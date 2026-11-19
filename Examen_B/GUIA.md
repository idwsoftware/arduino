# Examen Unidad II (versión B) – Guía de solución y de PICSimLab

Cada carpeta trae:
- **`.ino`**: el programa, para abrir en el Arduino IDE.
- **`.hex`**: el programa compilado (en PICSimLab: *File → Load Hex*).
- **`.pzw`**: el workspace de PICSimLab con la placa, el programa y los componentes ya conectados
  (en PICSimLab: *File → Load Workspace*).

| Carpeta | Pregunta | Cambios respecto al examen anterior |
|---|---|---|
| `Pregunta1_Secuencias_LEDs/` | 1. Secuencias de LEDs | Ninguno: mismo código |
| `Pregunta2_Direccional_Bicicleta/` | 2. Direccional de bicicleta | Flecha de **2 LEDs** y de noche **pares/impares** intermitentes |
| `Pregunta3_Semaforo/` | 3. Semáforo de 2 vías | Pregunta nueva |

> **Sobre los `.pzw`:** se generaron siguiendo el formato del código fuente de PICSimLab 0.9.x, pero
> **no se abrieron en PICSimLab**. Si tu versión no los abre bien, arma el circuito con las tablas de esta
> guía y guárdalo con *File → Save Workspace*.

---

## Pasos generales en PICSimLab

### Opción rápida
1. **File → Load Workspace**.
2. Elige el `.pzw` de la pregunta. Listo.

### Opción manual
1. En el Arduino IDE: **Herramientas → Placa → Arduino Uno**, luego **Programa → Exportar binario compilado**.
   Usa el `.hex` que **no** dice `with_bootloader`. Ya viene incluido en cada carpeta.
2. En PICSimLab: **Board → Arduino Uno** y **Microcontroller → atmega328p**.
3. **File → Load Hex** y elige el `.hex`.
4. **Modules → Spare parts** para abrir la ventana de componentes.
5. Agrega cada componente:
   - **Inputs:** Push Buttons, Potentiometers, LDR.
   - **Outputs:** LEDs, 7 Segments Display.
   - **Virtual:** IO Virtual Term.
6. **Clic derecho sobre el componente → Properties** y elige los pines según las tablas.
7. **File → Save Workspace** para crear tu `.pzw`.

En *Properties*, cada pin aparece como `número  nombre`:

| Arduino | En PICSimLab | | Arduino | En PICSimLab |
|---|---|---|---|---|
| D0 (RX) | `2  PD0/0` | | D8 | `14  PB0/8` |
| D1 (TX) | `3  PD1/1` | | D9 | `15  PB1/~9` |
| D2 | `4  PD2/2` | | D10 | `16  PB2/~10` |
| D3 | `5  PD3/~3` | | D11 | `17  PB3/~11` |
| D4 | `6  PD4/4` | | D12 | `18  PB4/12` |
| D5 | `11  PD5/~5` | | D13 | `19  PB5/13` |
| D6 | `12  PD6/~6` | | A0 | `23  PC0/A0` |
| D7 | `13  PD7/7` | | A1 / A2 | `24  PC1/A1` / `25  PC2/A2` |

---

## Pregunta 1 – Secuencias de LEDs (igual al examen anterior)

**Funcionamiento del código**
- LEDs en D2..D9 (salidas). Pulsadores `b1..b4` en D10..D13 con `INPUT_PULLUP`: al presionar, el pin pasa a LOW.
- `loop()` lee los botones. Si uno está presionado:
  1. guarda la secuencia en `sec`;
  2. apaga los LEDs (`limpiarLeds()`);
  3. espera 200 ms (antirrebote).
- Luego ejecuta **un ciclo completo** de la secuencia guardada y repite. Como las secuencias usan `delay()`,
  los botones solo se leen entre ciclos: hay que mantenerlos presionados un momento.
- Las secuencias:
  - `secx1`: un LED que avanza de D2 a D9 (150 ms por paso).
  - `secx2`: ida de D2 a D9 y vuelta de D9 a D3, estilo "auto fantástico".
  - `secx3`: todos encendidos 300 ms y apagados 300 ms.
  - `secx4`: un "gusano" de hasta 4 LEDs que avanza.

| Spare parts | Propiedad | Pin |
|---|---|---|
| Outputs → LEDs | 1-D1 … 8-D8 | D2 … D9 |
| Inputs → Push Buttons | 2 -Out 1 … 5 -Out 4 | D10 … D13 |
| Inputs → Push Buttons | Active | **LOW** |

---

## Pregunta 2 – Direccional de bicicleta (versión B)

**Qué hace**
- **DERECHA (D10):** un bloque de **2 LEDs encendidos** avanza de izquierda a derecha, como en la figura del examen.
  - Entra por el borde, recorre la tira, sale y hace una pausa (150 ms por paso).
  - **IZQUIERDA (D11):** lo mismo en sentido contrario.
- **Se apaga sola:** el potenciómetro en A0 es el timón. Cuando el timón **gira** (más de 200 desde el centro)
  y luego **vuelve al centro** (±80), la direccional se desactiva.
- **De noche** (LDR oscuro) y sin direccional: los LEDs **pares e impares se alternan** cada 400 ms
  (D2, D4, D6, D8 ↔ D3, D5, D7, D9).
  - Si de noche se pulsa una direccional, la flecha tiene prioridad.
  - Cuando se cancela, vuelve la intermitencia.
- Usa `millis()` (sin `delay`), así los botones responden en todo momento.

**Conexiones**

| Spare parts | Propiedad | Pin |
|---|---|---|
| Outputs → LEDs | 1-D1 … 8-D8 | D2 … D9 (D2 = izquierda) |
| Inputs → Push Buttons | 2 -Out 1 (DERECHA) | D10 |
| Inputs → Push Buttons | 3 -Out 2 (IZQUIERDA) | D11 |
| Inputs → Push Buttons | Active | **LOW** |
| Inputs → Potentiometers | 2-POT 1 (timón) | A0 |
| Inputs → LDR | 3 - A0 (salida analógica del módulo) | A1 |

**Cómo probar**
1. Pulsa DERECHA y aparece la flecha de 2 LEDs →.
2. Mueve el potenciómetro hacia un extremo y regrésalo a la mitad: se apaga.
3. Baja el slider del LDR (poca luz): pares e impares se alternan.
   - En el LDR de PICSimLab, **poca luz = voltaje alto**. El código toma oscuro cuando la lectura es mayor a 600.

---

## Pregunta 3 – Semáforo de 2 vías (nueva)

**Funcionamiento**

| Fase | Vía Principal | Vía Secundaria | Diurno | Hora punta |
|---|---|---|---|---|
| 1 | **VERDE** | ROJO | 25 s | 37,5 s (+50 %) |
| 2 | **ÁMBAR** | ROJO | 3 s | 3 s |
| 3 | ROJO | **VERDE** | 25 s | 37,5 s (+50 %) |
| 4 | ROJO | **ÁMBAR** | 3 s | 3 s |

- **Diurno:** verde 25 s y ámbar 3 s en cada vía.
  - El rojo de una vía dura lo mismo que el verde + ámbar de la otra (28 s). Así las dos vías nunca están en verde a la vez.
  - El enunciado pide rojo de 25 s, pero eso no cuadra con verde de 25 s más ámbar de 3 s.
- **Hora punta:** cada pulsación del botón (D8) **activa o desactiva** el modo.
  - El verde sube a 37,5 s (+50 %) y se aplica desde el siguiente verde.
- **Nocturno:** si el LDR detecta casi total oscuridad (lectura > 900):
  - se cancela el ciclo;
  - el **ámbar de los dos semáforos parpadea cada 0,5 s**;
  - cuando vuelve la luz (lectura < 800), el ciclo se reinicia desde la fase 1.
- **Terminal virtual:** imprime `MODO: DIURNO`, `MODO: HORA PUNTA` o `MODO: NOCTURNO` cada vez que cambia el modo.
  También imprime cada cambio de fase, por ejemplo `DIURNO -> Principal VERDE / Secundaria ROJO (25.0 s)`.
- **Display de 7 segmentos:** muestra solo **4, 3, 2, 1** en los últimos 4 segundos de cada fase; el resto del tiempo está apagado.
  - El ámbar dura 3 s, así que ahí se ve 3, 2, 1.
  - En modo nocturno el display está apagado.

**Conexiones**

| Spare parts | Propiedad | Pin |
|---|---|---|
| Outputs → LEDs (Size 3) – **Vía Principal** | 1-D1 rojo / 2-D2 amarillo / 3-D3 verde | D2 / D3 / D4 |
| Outputs → LEDs (Size 3) – **Vía Secundaria** | 1-D1 rojo / 2-D2 amarillo / 3-D3 verde | D5 / D6 / D7 |
| Inputs → Push Buttons (Size 1) | 2 -Out 1 (HORA PUNTA), Active **LOW** | D8 |
| Inputs → LDR | 3 - A0 (salida analógica) | A0 |
| Outputs → 7 Segments Display | Seg a, b, c, d, e | D9, D10, D11, D12, D13 |
| Outputs → 7 Segments Display | Seg f, g | A1, A2 |
| Outputs → 7 Segments Display | Point, D1..D4 / Active / Type | NC / **HIGH** / **Single** |
| Virtual → IO Virtual Term | P2 - RX / P3 - TX / Speed | `3  PD1/1` / `2  PD0/0` / 9600 |

En las propiedades de cada LED elige el color: **Red**, **Yellow** y **Green**.

**Cómo probar**
1. Al iniciar: Principal en verde y Secundaria en rojo. En la terminal aparece `MODO: DIURNO`.
2. Espera: a falta de 4 s el display muestra 4, 3, 2, 1, y pasa a ámbar (3, 2, 1).
3. Pulsa el botón: aparece `MODO: HORA PUNTA` y el siguiente verde dura 37,5 s.
4. Baja el slider del LDR **hasta el fondo**: aparece `MODO: NOCTURNO` y los dos ámbar parpadean.
   Súbelo y el ciclo vuelve a empezar.

> Si no ves la terminal: **clic derecho sobre IO Virtual Term → Properties** y revisa que RX sea `3  PD1/1`,
> TX sea `2  PD0/0` y la velocidad 9600.
