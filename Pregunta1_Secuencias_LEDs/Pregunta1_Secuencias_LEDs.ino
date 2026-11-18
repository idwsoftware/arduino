/*
 * EXAMEN UNIDAD II - ARQUITECTURA DE COMPUTADORAS - Pregunta 1
 * 8 LEDs (pines 2..9) y 4 pulsadores (pines 10..13, INPUT_PULLUP).
 * Cada pulsador selecciona una de 4 secuencias de luces.
 *   b1 -> secx1: corrimiento izquierda->derecha (un LED a la vez)
 *   b2 -> secx2: "auto fantastico" ida y vuelta
 *   b3 -> secx3: parpadeo de todos los LEDs (300 ms ON / 300 ms OFF)
 *   b4 -> secx4: "gusano" de 4 LEDs que avanza
 */

const int primerPin = 2;   // primer LED
const int ultimoPin = 9;   // ultimo LED

const int b1 = 10;         // pulsadores (activos en LOW)
const int b2 = 11;
const int b3 = 12;
const int b4 = 13;

int tiempo = 150;          // retardo entre pasos (ms)
byte sec = 0;              // secuencia activa (0 = ninguna)

void setup() {
  for (int i = primerPin; i <= ultimoPin; i++) {
    pinMode(i, OUTPUT);
  }

  pinMode(b1, INPUT_PULLUP);
  pinMode(b2, INPUT_PULLUP);
  pinMode(b3, INPUT_PULLUP);
  pinMode(b4, INPUT_PULLUP);
}

void loop() {
  // Lectura de pulsadores: al presionar se elige la secuencia,
  // se apagan los LEDs y se espera 200 ms (antirrebote simple)
  if (digitalRead(b1) == LOW) { sec = 1; limpiarLeds(); delay(200); }
  if (digitalRead(b2) == LOW) { sec = 2; limpiarLeds(); delay(200); }
  if (digitalRead(b3) == LOW) { sec = 3; limpiarLeds(); delay(200); }
  if (digitalRead(b4) == LOW) { sec = 4; limpiarLeds(); delay(200); }

  // Ejecuta un ciclo completo de la secuencia seleccionada
  switch (sec) {
    case 1: secx1(); break;
    case 2: secx2(); break;
    case 3: secx3(); break;
    case 4: secx4(); break;
  }
}

// Apaga todos los LEDs
void limpiarLeds() {
  for (int i = primerPin; i <= ultimoPin; i++) {
    digitalWrite(i, LOW);
  }
}

// Secuencia 1: un LED recorre de 2 a 9
void secx1() {
  for (int i = primerPin; i <= ultimoPin; i++) {
    digitalWrite(i, HIGH);
    delay(tiempo);
    digitalWrite(i, LOW);
  }
}

// Secuencia 2: ida (2->9) y vuelta (9->3)
void secx2() {
  for (int i = primerPin; i <= ultimoPin; i++) {
    digitalWrite(i, HIGH);
    delay(tiempo);
    digitalWrite(i, LOW);
  }
  for (int i = ultimoPin; i > primerPin; i--) {
    digitalWrite(i, HIGH);
    delay(tiempo);
    digitalWrite(i, LOW);
  }
}

// Secuencia 3: todos encienden y apagan a la vez
void secx3() {
  for (int i = primerPin; i <= ultimoPin; i++) digitalWrite(i, HIGH);
  delay(300);
  for (int i = primerPin; i <= ultimoPin; i++) digitalWrite(i, LOW);
  delay(300);
}

// Secuencia 4: bloque ("gusano") de hasta 4 LEDs que avanza
void secx4() {
  int longitud = 4;
  for (int i = primerPin; i <= ultimoPin; i++) {
    for (int e = 0; e < longitud; e++) {
      if (i - e >= primerPin) digitalWrite(i - e, HIGH);
    }
    delay(tiempo);
    for (int e = 0; e < longitud; e++) {
      if (i - e >= primerPin) digitalWrite(i - e, LOW);
    }
  }
}
