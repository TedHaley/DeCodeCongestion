#include <Arduino.h>

int LIGHTPIN = 3;
String inString = "";    // string to hold input

void setup() {
  Serial.begin(9600);
  pinMode(LIGHTPIN, OUTPUT);
}

void loop() {
  // Read serial input:
  while (Serial.available() > 0) {
    int inChar = Serial.read();
    if (isDigit(inChar)) {
      // convert the incoming byte to a char and add it to the string:
      inString += (char)inChar;
    }
    // if you get a newline, print the string, then the string's value:
    if (inChar == '\n') {
      Serial.print("Value:");
      Serial.println(inString.toInt());
      Serial.print("String: ");
      Serial.println(inString);
      if (inString.length() != 0) {
        analogWrite(LIGHTPIN, inString.toInt());
      }
      // clear the string for new input:
      inString = "";

    }
  }
}