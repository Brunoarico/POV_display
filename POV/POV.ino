#include <Adafruit_NeoPixel.h>
#ifdef __AVR__
  #include <avr/power.h>
#endif
#include "image.h"
#define PIN 12
#define NUM_LEDS 36
#define BRIGHTNESS 5
#define ENCODER 2
#define ROT true
#define PWM  82
bool fake = false;
bool noww = false;
Adafruit_NeoPixel strip = Adafruit_NeoPixel(NUM_LEDS, PIN, NEO_GRB + NEO_KHZ800);
unsigned long int old_t = 0, new_t = 0;
float delta = 0;
bool accel = true;
int pwm_motor = 120;


void setup() {
  strip.setBrightness(BRIGHTNESS);
  strip.begin();
  strip.show();
  pinMode(ENCODER, INPUT);
  pinMode(9, OUTPUT);
  pinMode(7, OUTPUT);
  digitalWrite(7, HIGH);
  attachInterrupt(digitalPinToInterrupt(ENCODER), change_color, RISING);
  Serial.begin(9600);
  setPwmFrequency(9, 1);
  accelerate();
}

void change_color(){
  accel = false;
  if(!fake){
    new_t = millis();
    delta =  runningAverage(new_t-old_t);
    old_t = new_t;  
    noww = false;
  }
}

long runningAverage(int M) {
  #define LM_SIZE 3
  static int LM[LM_SIZE];      // LastMeasurements
  static byte index = 0;
  static long sum = 0;
  static byte count = 0;

  // keep sum updated to improve speed.
  sum -= LM[index];
  LM[index] = M;
  sum += LM[index];
  index++;
  index = index % LM_SIZE;
  if (count < LM_SIZE) count++;

  return sum / count;
}

int k = 0;

void colorWipe(int j) {
  fake = true;
  for(uint16_t i=0; i<strip.numPixels(); i++) {
    uint16_t v = pgm_read_word(&m[j][i]);
    strip.setPixelColor(i, strip.Color(((v >> 16) & 0xFF) ,((v >> 8) & 0xFF) ,((v) & 0xFF) ));     //yellow
  }
  strip.show();
  fake = false;
}

void off(){
  fake = true;
  for(uint16_t i=0; i<strip.numPixels(); i++) {
    strip.setPixelColor(i, strip.Color(0, 0, 0));
  }
  strip.show();
  fake = false;
}

void setPwmFrequency(int pin, int divisor) {
  byte mode;
  if(pin == 5 || pin == 6 || pin == 9 || pin == 10) {
    switch(divisor) {
      case 1: mode = 0x01; break;
      case 8: mode = 0x02; break;
      case 64: mode = 0x03; break;
      case 256: mode = 0x04; break;
      case 1024: mode = 0x05; break;
      default: return;
    }
    if(pin == 5 || pin == 6) {
      TCCR0B = TCCR0B & 0b11111000 | mode;
    } else {
      TCCR1B = TCCR1B & 0b11111000 | mode;
    }
  } else if(pin == 3 || pin == 11) {
    switch(divisor) {
      case 1: mode = 0x01; break;
      case 8: mode = 0x02; break;
      case 32: mode = 0x03; break;
      case 64: mode = 0x04; break;
      case 128: mode = 0x05; break;
      case 256: mode = 0x06; break;
      case 1024: mode = 0x07; break;
      default: return;
    }
    TCCR2B = TCCR2B & 0b11111000 | mode;
  }
}


void accelerate () {
  int olt = 0;
  analogWrite(9, pwm_motor);
  while(pwm_motor > PWM) {
    if(millis()-olt > 100 ) {
      olt = millis();
      pwm_motor--;
      analogWrite(9, pwm_motor);
    }
    Serial.println(String(pwm_motor) + " " + String(delta));
  }
  Serial.println("Go");
}

void loop() {
  if(!noww) {
    for(int j = k; j<LINES+k; j++){
      colorWipe(j%LINES);
      off();
    }
    noww = true;
    if(ROT){
      k++;
      k = k%LINES;
    }
  }

}
