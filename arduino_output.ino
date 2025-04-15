#include <Servo.h>
const int ledPin = 13;  // Onboard LED on Arduino Leonardo
Servo servo;

void setup() {
  Serial.begin(9600);
  pinMode(ledPin, OUTPUT);
}

void blinkLED(int times, int delayTime) {
  for (int i = 0; i < times; i++) {
    digitalWrite(ledPin, HIGH);
    delay(delayTime);
    digitalWrite(ledPin, LOW);
    delay(delayTime);
  }
}

void loop() {
  if (Serial.available() > 0) {
    char incomingByte = Serial.read();
    int frustrationValue = incomingByte - '0';  // Convert ASCII digit to integer

    // Reset the LED state before showing the new pattern
    digitalWrite(ledPin, LOW);

    // Choose a blink pattern based on the frustration level
    switch (frustrationValue) {
      case 0:
        // Not Very Frustrated: blink once slowly
        servo.attach(4);
        servo.write(0);
        delay(2000);
        servo.detach();
        break;
      case 1:
        // Medium Frustrated: blink twice at a medium pace
        servo.attach(6);
        servo.write(0);
        delay(2000);
        servo.detach();
        break;
      case 2:
        // Very Frustrated: blink three times quickly
        servo.attach(8);
        servo.write(0);
        delay(2000);
        servo.detach();
        break;
      default:
        // For any unexpected value, do nothing or add error handling
        break;
    }
  }
}
