/*
 * EXAMEN UNIDAD II (version B) - ARQUITECTURA DE COMPUTADORAS - Pregunta 2
 * Control direccional para bicicleta.
 *
 * Hardware (PICSimLab - Arduino Uno + Spare parts):
 *   - 8 LEDs (parte "LEDs")          -> pines 2..9  (2 = extremo izquierdo, 9 = extremo derecho)
 *   - Pulsador DERECHA               -> pin 10 (INPUT_PULLUP, activo en LOW)
 *   - Pulsador IZQUIERDA             -> pin 11 (INPUT_PULLUP, activo en LOW)
 *   - Potenciometro (timon)          -> A0  (centro ~512)
 *   - LDR (modulo sensor de luz)     -> A1  (valor ALTO = oscuro)
 *
 * Funcionamiento:
 *   - Al pulsar DERECHA se activa la flecha hacia la derecha: un bloque de
 *     2 LEDs encendidos que avanza de izquierda a derecha (como en la figura).
 *     IZQUIERDA hace lo mismo en sentido contrario.
 *   - La direccional se desactiva sola cuando el timon (potenciometro) gira
 *     y luego REGRESA a la posicion central.
 *   - De noche (LDR oscuro) y sin direccional activa: secuencia de todos los
 *     LEDs, intermitentes entre PARES e IMPARES (D2,D4,D6,D8 <-> D3,D5,D7,D9).
 *     Si se activa una direccional de noche, la flecha tiene prioridad.
 *   - Todo es no bloqueante (millis), asi los botones responden siempre.
 */

const int primerPin = 2;
const int ultimoPin = 9;
const int NUM_LEDS  = ultimoPin - primerPin + 1;
const int LARGO_FLECHA = 2;      // LEDs encendidos a la vez en la flecha

const int btnDer   = 10;
const int btnIzq   = 11;
const int pinTimon = A0;
const int pinLDR   = A1;

// Umbrales
const int CENTRO        = 512;  // lectura del potenciometro en el centro
const int ZONA_CENTRO   = 80;   // +- banda considerada "centro"
const int GIRO_MIN      = 200;  // desviacion para considerar que el timon giro
const int UMBRAL_OSCURO = 600;  // LDR por encima de esto = oscuro
const int HISTERESIS    = 50;   // evita parpadeos en el limite luz/oscuridad

const unsigned long T_PASO     = 150;  // ms por paso de la flecha
const unsigned long T_INTERMIT = 400;  // ms de alternancia pares/impares

enum Estado { APAGADO, DERECHA, IZQUIERDA };
Estado estado = APAGADO;

bool timonGiro = false;   // el timon ya salio del centro tras activar
bool oscuro    = false;
bool fasePar   = false;
int  paso      = 0;
unsigned long tAnterior = 0;

void setup() {
  for (int i = primerPin; i <= ultimoPin; i++) pinMode(i, OUTPUT);
  pinMode(btnDer, INPUT_PULLUP);
  pinMode(btnIzq, INPUT_PULLUP);
  Serial.begin(9600);
}

void loop() {
  leerBotones();
  vigilarTimon();
  leerLuz();

  unsigned long ahora = millis();

  if (estado != APAGADO) {
    if (ahora - tAnterior >= T_PASO) {
      tAnterior = ahora;
      flecha(estado == DERECHA);
    }
  } else if (oscuro) {
    if (ahora - tAnterior >= T_INTERMIT) {
      tAnterior = ahora;
      fasePar = !fasePar;
      paresImpares(fasePar);
    }
  } else {
    todos(false);
  }
}

// ---------------------------------------------------------------
void leerBotones() {
  if (digitalRead(btnDer) == LOW) activar(DERECHA);
  if (digitalRead(btnIzq) == LOW) activar(IZQUIERDA);
}

void activar(Estado nuevo) {
  if (estado != nuevo) {
    estado    = nuevo;
    timonGiro = false;
    paso      = 0;
    tAnterior = millis() - T_PASO;   // dibuja el primer paso de inmediato
    todos(false);
    Serial.println(nuevo == DERECHA ? "Direccional DERECHA" : "Direccional IZQUIERDA");
  }
}

// Cancelacion automatica: el timon debe girar y luego volver al centro
void vigilarTimon() {
  if (estado == APAGADO) return;
  int desv = analogRead(pinTimon) - CENTRO;

  if (abs(desv) > GIRO_MIN) timonGiro = true;

  if (timonGiro && abs(desv) < ZONA_CENTRO) {
    estado = APAGADO;
    todos(false);
    tAnterior = millis() - T_INTERMIT;
    Serial.println("Timon al centro: direccional desactivada");
  }
}

void leerLuz() {
  int luz = analogRead(pinLDR);
  bool antes = oscuro;
  if (!oscuro && luz > UMBRAL_OSCURO) oscuro = true;
  else if (oscuro && luz < UMBRAL_OSCURO - HISTERESIS) oscuro = false;
  if (oscuro != antes) Serial.println(oscuro ? "Modo NOCHE" : "Modo DIA");
}

// Flecha: un bloque de LARGO_FLECHA LEDs avanza hacia el lado indicado.
// Pasos: entra por el borde, recorre la tira, sale, y un paso apagado.
void flecha(bool haciaDerecha) {
  todos(false);
  int totalPasos = NUM_LEDS + LARGO_FLECHA;   // incluye entrada, salida y pausa
  for (int k = 0; k < LARGO_FLECHA; k++) {
    int pos = paso - k;                        // posicion 0..NUM_LEDS-1
    if (pos >= 0 && pos < NUM_LEDS) {
      int led = haciaDerecha ? (primerPin + pos) : (ultimoPin - pos);
      digitalWrite(led, HIGH);
    }
  }
  paso = (paso + 1) % totalPasos;
}

// Intermitencia nocturna: pares o impares encendidos
void paresImpares(bool pares) {
  for (int i = primerPin; i <= ultimoPin; i++) {
    bool esPar = (i % 2 == 0);
    digitalWrite(i, (esPar == pares) ? HIGH : LOW);
  }
}

void todos(bool valor) {
  for (int i = primerPin; i <= ultimoPin; i++) digitalWrite(i, valor ? HIGH : LOW);
}
