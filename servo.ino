#include<Servo.h>

Servo servo;

void setup() {
    servo.attach(6);
}

void loop() {
    servo.detach();
    delay(2000);
    servo.attach(6);
    servo.write(180);
    delay(2000);
    servo.detach();
    delay(2000);
    servo.attach(6);
    servo.write(0);
    delay(2000);
}