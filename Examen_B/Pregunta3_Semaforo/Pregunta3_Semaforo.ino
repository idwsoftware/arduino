/*
 * EXAMEN UNIDAD II (version B) - ARQUITECTURA DE COMPUTADORAS - Pregunta 3
 * Semaforo para una interseccion de 2 vias (Principal y Secundaria).
 *
 * Conexiones (Arduino Uno / PICSimLab):
 *   Via Principal  : ROJO = D2, AMBAR = D3, VERDE = D4
 *   Via Secundaria : ROJO = D5, AMBAR = D6, VERDE = D7
 *   Pulsador HORA PUNTA : D8 (INPUT_PULLUP, activo en LOW) -> cada pulsacion
 *                         activa / desactiva el modo hora punta
 *   LDR (hora del dia)  : A0 (valor ALTO = oscuro)
 *   Display 7 segmentos (catodo comun, activo en HIGH):
 *        a = D9, b = D10, c = D11, d = D12, e = D13, f = A1, g = A2
 *   Terminal virtual (IO Virtual Term): RX/TX del Arduino (D0/D1) a 9600 baudios
 *
 * Modos:
 *   DIURNO     : verde 25 s, ambar 3 s. Mientras una via esta en verde+ambar,
 *                la otra esta en rojo.
 *   HORA PUNTA : el verde aumenta 50 % (37,5 s). Se aplica desde el siguiente verde.
 *   NOCTURNO   : con casi total oscuridad se cancela el ciclo y el ambar de
 *                ambos semaforos parpadea cada 0,5 s hasta que vuelva la luz.
 *   El display muestra solo 4, 3, 2, 1 en los ultimos 4 segundos de cada estado.
 */

// ---------------- Pines ----------------
const int P_ROJO = 2, P_AMBAR = 3, P_VERDE = 4;
const int S_ROJO = 5, S_AMBAR = 6, S_VERDE = 7;
const int BTN_PUNTA = 8;
const int PIN_LDR = A0;
const int SEG[7] = {9, 10, 11, 12, 13, A1, A2};   // a, b, c, d, e, f, g

// ---------------- Tiempos (ms) ----------------
const unsigned long T_VERDE       = 25000UL;
const unsigned long T_VERDE_PUNTA = 37500UL;   // 25 s + 50 %
const unsigned long T_AMBAR       = 3000UL;
const unsigned long T_PARPADEO    = 500UL;

// ---------------- Umbrales LDR ----------------
const int UMBRAL_NOCHE = 900;   // casi total oscuridad
const int UMBRAL_DIA   = 800;   // histeresis para volver a dia

// Segmentos a..g para los digitos 0..9 (bit0 = a ... bit6 = g)
const byte DIGITOS[10] = {
  0b0111111, 0b0000110, 0b1011011, 0b1001111, 0b1100110,
  0b1101101, 0b1111101, 0b0000111, 0b1111111, 0b1101111
};

enum Fase { P_VERDE_FASE, P_AMBAR_FASE, S_VERDE_FASE, S_AMBAR_FASE };
enum Modo { DIURNO, HORA_PUNTA, NOCTURNO };

Fase fase = P_VERDE_FASE;
unsigned long inicioFase = 0;
unsigned long duracionFase = T_VERDE;

bool horaPunta = false;
bool noche = false;
Modo modoImpreso = NOCTURNO;     // fuerza la primera impresion
bool primeraVez = true;

bool btnAnterior = HIGH;
unsigned long tBoton = 0;

bool ambarEncendido = false;
unsigned long tParpadeo = 0;

void setup() {
  int salidas[] = {P_ROJO, P_AMBAR, P_VERDE, S_ROJO, S_AMBAR, S_VERDE};
  for (int i = 0; i < 6; i++) pinMode(salidas[i], OUTPUT);
  for (int i = 0; i < 7; i++) pinMode(SEG[i], OUTPUT);
  pinMode(BTN_PUNTA, INPUT_PULLUP);

  Serial.begin(9600);
  Serial.println("Semaforo 2 vias - inicio");
  iniciarFase(P_VERDE_FASE);
}

void loop() {
  leerBoton();
  leerLuz();
  imprimirModo();

  if (noche) {
    modoNocturno();
  } else {
    cicloNormal();
  }
}

// ======================= Entradas =======================
void leerBoton() {
  bool lectura = digitalRead(BTN_PUNTA);
  if (lectura != btnAnterior && millis() - tBoton > 50) {   // antirrebote
    tBoton = millis();
    btnAnterior = lectura;
    if (lectura == LOW) {               // flanco de bajada = pulsacion
      horaPunta = !horaPunta;
    }
  }
}

void leerLuz() {
  int luz = analogRead(PIN_LDR);
  if (!noche && luz > UMBRAL_NOCHE) {
    noche = true;
    tParpadeo = millis() - T_PARPADEO;
    ambarEncendido = false;
  } else if (noche && luz < UMBRAL_DIA) {
    noche = false;
    iniciarFase(P_VERDE_FASE);          // al volver el dia se reinicia el ciclo
  }
}

Modo modoActual() {
  if (noche) return NOCTURNO;
  return horaPunta ? HORA_PUNTA : DIURNO;
}

const char* nombreModo(Modo m) {
  switch (m) {
    case HORA_PUNTA: return "HORA PUNTA";
    case NOCTURNO:   return "NOCTURNO";
    default:         return "DIURNO";
  }
}

// Imprime el modo en la terminal virtual cada vez que cambia
void imprimirModo() {
  Modo m = modoActual();
  if (m != modoImpreso || primeraVez) {
    modoImpreso = m;
    primeraVez = false;
    Serial.print("MODO: ");
    Serial.println(nombreModo(m));
  }
}

// ======================= Ciclo normal =======================
void iniciarFase(Fase f) {
  fase = f;
  inicioFase = millis();
  if (f == P_VERDE_FASE || f == S_VERDE_FASE) {
    duracionFase = horaPunta ? T_VERDE_PUNTA : T_VERDE;
  } else {
    duracionFase = T_AMBAR;
  }

  // Luces de cada fase
  apagarLuces();
  switch (f) {
    case P_VERDE_FASE: digitalWrite(P_VERDE, HIGH); digitalWrite(S_ROJO, HIGH); break;
    case P_AMBAR_FASE: digitalWrite(P_AMBAR, HIGH); digitalWrite(S_ROJO, HIGH); break;
    case S_VERDE_FASE: digitalWrite(P_ROJO, HIGH);  digitalWrite(S_VERDE, HIGH); break;
    case S_AMBAR_FASE: digitalWrite(P_ROJO, HIGH);  digitalWrite(S_AMBAR, HIGH); break;
  }

  const char* textos[] = {"Principal VERDE / Secundaria ROJO", "Principal AMBAR / Secundaria ROJO",
                          "Principal ROJO / Secundaria VERDE", "Principal ROJO / Secundaria AMBAR"};
  Serial.print(nombreModo(modoActual()));
  Serial.print(" -> ");
  Serial.print(textos[f]);
  Serial.print(" (");
  Serial.print(duracionFase / 1000.0, 1);
  Serial.println(" s)");
}

void cicloNormal() {
  unsigned long transcurrido = millis() - inicioFase;

  if (transcurrido >= duracionFase) {
    iniciarFase((Fase)((fase + 1) % 4));
    transcurrido = 0;
  }

  // Cuenta regresiva: solo los 4 ultimos segundos
  unsigned long restante = duracionFase - transcurrido;
  int segundos = (restante + 999) / 1000;        // redondeo hacia arriba
  if (segundos >= 1 && segundos <= 4) mostrarDigito(segundos);
  else apagarDisplay();
}

// ======================= Modo nocturno =======================
void modoNocturno() {
  if (millis() - tParpadeo >= T_PARPADEO) {
    tParpadeo = millis();
    ambarEncendido = !ambarEncendido;
    apagarLuces();
    digitalWrite(P_AMBAR, ambarEncendido ? HIGH : LOW);
    digitalWrite(S_AMBAR, ambarEncendido ? HIGH : LOW);
    apagarDisplay();
  }
}

// ======================= Salidas =======================
void apagarLuces() {
  digitalWrite(P_ROJO, LOW);  digitalWrite(P_AMBAR, LOW); digitalWrite(P_VERDE, LOW);
  digitalWrite(S_ROJO, LOW);  digitalWrite(S_AMBAR, LOW); digitalWrite(S_VERDE, LOW);
}

void mostrarDigito(int n) {
  for (int i = 0; i < 7; i++) digitalWrite(SEG[i], bitRead(DIGITOS[n], i) ? HIGH : LOW);
}

void apagarDisplay() {
  for (int i = 0; i < 7; i++) digitalWrite(SEG[i], LOW);
}
