/*
 * EXAMEN UNIDAD II - ARQUITECTURA DE COMPUTADORAS - Pregunta 2
 * Control direccional para bicicleta.
 *
 * Hardware (PICSimLab - Arduino Uno + Spare parts):
 *   - 8 LEDs (parte "LEDs")          -> pines 2..9  (2 = extremo izquierdo, 9 = extremo derecho)
 *   - Pulsador DERECHA               -> pin 10 (INPUT_PULLUP, activo en LOW)
 *   - Pulsador IZQUIERDA             -> pin 11 (INPUT_PULLUP, activo en LOW)
 *   - Potenciometro (timon)          -> A0  (centro ~512)
 *   - LDR (modulo sensor de luz)     -> A1  (valor ALTO = oscuro: la
 *                                          resistencia del LDR sube con poca luz)
 *
 * Funcionamiento:
 *   - Al pulsar DERECHA se activa la secuencia de flecha hacia la derecha
 *     (luz que corre de izquierda a derecha). Igual para IZQUIERDA.
 *   - La direccional se desactiva sola cuando el timon (potenciometro)
 *     gira y luego REGRESA a la posicion central (como un auto).
 *   - Si esta oscuro (LDR) y no hay direccional activa, todos los LEDs
 *     parpadean de forma intermitente (luz de posicion/seguridad).
 *   - Todo es no bloqueante (millis), asi los botones responden siempre.
 */

const int primerPin = 2;
const int ultimoPin = 9;
const int NUM_LEDS  = ultimoPin - primerPin + 1;

const int btnDer   = 10;
const int btnIzq   = 11;
const int pinTimon = A0;
const int pinLDR   = A1;

// Umbrales
const int CENTRO        = 512;  // lectura del potenciometro en el centro
const int ZONA_CENTRO   = 80;   // +- banda considerada "centro"
const int GIRO_MIN      = 200;  // desviacion para considerar que el timon giro
const int UMBRAL_OSCURO = 600;  // LDR por encima de esto = oscuro (~15 lux)
const int HISTERESIS    = 40;   // evita parpadeos en el limite luz/oscuridad

const unsigned long T_PASO      = 120;  // ms por paso de la flecha
const unsigned long T_INTERMIT  = 400;  // ms de parpadeo nocturno

enum Estado { APAGADO, DERECHA, IZQUIERDA };
Estado estado = APAGADO;

bool timonGiro = false;          // el timon ya salio del centro tras activar
bool oscuro    = false;
int  paso      = 0;
bool encendido = false;
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

  switch (estado) {
    case DERECHA:
    case IZQUIERDA:
      if (ahora - tAnterior >= T_PASO) {
        tAnterior = ahora;
        flecha(estado == DERECHA);
      }
      break;

    case APAGADO:
      if (oscuro) {
        if (ahora - tAnterior >= T_INTERMIT) {
          tAnterior = ahora;
          encendido = !encendido;
          todos(encendido);
        }
      } else {
        todos(false);
      }
      break;
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
    tAnterior = 0;
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
    tAnterior = 0;
    Serial.println("Timon al centro: direccional desactivada");
  }
}

void leerLuz() {
  int luz = analogRead(pinLDR);
  if (!oscuro && luz > UMBRAL_OSCURO) oscuro = true;
  else if (oscuro && luz < UMBRAL_OSCURO - HISTERESIS) oscuro = false;
}

// Flecha: la luz corre hacia el lado indicado; tras llegar al extremo
// se apagan todos un paso y se repite (efecto ">>>" o "<<<").
void flecha(bool haciaDerecha) {
  todos(false);
  if (paso < NUM_LEDS) {
    int led = haciaDerecha ? (primerPin + paso) : (ultimoPin - paso);
    digitalWrite(led, HIGH);
    // en la oscuridad se agrega "cola" para mayor visibilidad
    if (oscuro && paso > 0) {
      int cola = haciaDerecha ? led - 1 : led + 1;
      digitalWrite(cola, HIGH);
    }
  }
  paso = (paso + 1) % (NUM_LEDS + 1);
}

void todos(bool valor) {
  for (int i = primerPin; i <= ultimoPin; i++) digitalWrite(i, valor ? HIGH : LOW);
}
