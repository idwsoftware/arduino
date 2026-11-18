/*
 * EXAMEN UNIDAD II - ARQUITECTURA DE COMPUTADORAS - Pregunta 3
 * Medidor de nivel de un tanque cilindrico con HC-SR04.
 *
 * Tanque: altura H = 3.0 m, radio r = 1.5 m
 *   Volumen total = pi * r^2 * H = pi * 2.25 * 3 = 21.206 m3
 *   90 % = 19.085 m3  -> ALARMA ON (buzzer + LED + abre valvula/servo)
 *   85 % = 18.025 m3  -> ALARMA OFF (cierra valvula)  [histeresis]
 *
 * El sensor esta en la tapa del tanque mirando hacia abajo:
 *   nivel h = H - distancia
 *   volumen = pi * r^2 * h
 *
 * Conexiones (Arduino Uno):
 *   LCD 16x2 (HD44780): RS=12, E=11, D4=5, D5=4, D6=3, D7=2 (RW a GND)
 *   HC-SR04: TRIG=7, ECHO=8
 *   Buzzer: pin 6
 *   LED alarma: pin 13
 *   Servo (valvula de desague): pin 9
 */

#include <LiquidCrystal.h>
#include <Servo.h>

LiquidCrystal lcd(12, 11, 5, 4, 3, 2);
Servo valvula;

const int PIN_TRIG   = 7;
const int PIN_ECHO   = 8;
const int PIN_BUZZER = 6;
const int PIN_LED    = 13;
const int PIN_SERVO  = 9;

const float ALTURA = 3.0;   // m
const float RADIO  = 1.5;   // m
const float AREA   = PI * RADIO * RADIO;  // m2
const float VOL_TOTAL = AREA * ALTURA;    // m3

const float PORC_ALARMA_ON  = 90.0;
const float PORC_ALARMA_OFF = 85.0;

const int SERVO_CERRADO = 0;
const int SERVO_ABIERTO = 90;

bool alarma = false;

void setup() {
  pinMode(PIN_TRIG, OUTPUT);
  pinMode(PIN_ECHO, INPUT);
  pinMode(PIN_BUZZER, OUTPUT);
  pinMode(PIN_LED, OUTPUT);

  valvula.attach(PIN_SERVO);
  valvula.write(SERVO_CERRADO);

  lcd.begin(16, 2);
  lcd.print("Nivel de Tanque");
  lcd.setCursor(0, 1);
  lcd.print("Vmax=");
  lcd.print(VOL_TOTAL, 2);
  lcd.print(" m3");
  Serial.begin(9600);
  delay(1500);
  lcd.clear();
}

// Devuelve la distancia en metros (o -1 si no hay eco)
float medirDistancia() {
  digitalWrite(PIN_TRIG, LOW);
  delayMicroseconds(2);
  digitalWrite(PIN_TRIG, HIGH);
  delayMicroseconds(10);
  digitalWrite(PIN_TRIG, LOW);

  unsigned long dur = pulseIn(PIN_ECHO, HIGH, 30000UL); // max ~5 m
  if (dur == 0) return -1.0;
  return (dur * 0.0343 / 2.0) / 100.0;  // cm -> m
}

void loop() {
  float d = medirDistancia();
  if (d < 0) {
    lcd.setCursor(0, 0);
    lcd.print("Error sensor    ");
    delay(200);
    return;
  }

  float nivel = ALTURA - d;
  nivel = constrain(nivel, 0.0, ALTURA);
  float volumen    = AREA * nivel;
  float porcentaje = volumen * 100.0 / VOL_TOTAL;

  // Control con histeresis 90 % / 85 %
  if (!alarma && porcentaje >= PORC_ALARMA_ON) {
    alarma = true;
    valvula.write(SERVO_ABIERTO);
  } else if (alarma && porcentaje <= PORC_ALARMA_OFF) {
    alarma = false;
    valvula.write(SERVO_CERRADO);
    noTone(PIN_BUZZER);
    digitalWrite(PIN_LED, LOW);
  }

  if (alarma) {
    // sonido y LED intermitentes de alarma
    static bool fase = false;
    fase = !fase;
    digitalWrite(PIN_LED, fase ? HIGH : LOW);
    if (fase) tone(PIN_BUZZER, 2000);
    else      tone(PIN_BUZZER, 1000);
  }

  // Pantalla
  lcd.setCursor(0, 0);
  lcd.print("V=");
  lcd.print(volumen, 2);
  lcd.print("m3 ");
  lcd.print(porcentaje, 0);
  lcd.print("%    ");

  lcd.setCursor(0, 1);
  lcd.print("h=");
  lcd.print(nivel, 2);
  lcd.print("m ");
  lcd.print(alarma ? "ALARMA " : "Normal ");

  Serial.print("d="); Serial.print(d, 2);
  Serial.print(" h="); Serial.print(nivel, 2);
  Serial.print(" V="); Serial.print(volumen, 3);
  Serial.print(" %="); Serial.println(porcentaje, 1);

  delay(250);
}
