#include <Servo.h>

Servo servoClaws;
Servo servoLeft;
Servo servoRight;
Servo servoBase;


const int infraPin = 5;
const int echoPin = 6;
const int trigPin = 7;

const int clawsPin = 8;
const int leftPin = 9;
const int rightPin = 10;
const int basePin = 11;

float duration, distance;

void setup() {
  // Beginning Serial Communication 
  Serial.begin(9600);

  // Infrared sensor
  pinMode(7, INPUT);  

  // Ultrasonic sensor
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);

  // Attaching servos to respective pin number
  servoLeft.attach(leftPin);
  servoRight.attach(rightPin);
  servoBase.attach(basePin);
  servoClaws.attach(clawsPin);

  // Assigning inital servo angle 
  servoLeft.write(120); 
  servoRight.write(90); 
  servoBase.write(0);
  servoClaws.write(0);
}

void loop() {

  checkDistanceAndObject();
  delay(1000);

  // If we received data from Python script
  if (Serial.available() > 0) {
    
    // Read the data send - (Bin id)
    String data = Serial.readString();
    // Activate the robot and passing the data as argument
    activateRobot(data);
  }
}

// Function to activate the robot
void activateRobot(String data) {
  if(data == "1"){
    // Metal
    fetchObject();
    disposeObject(90);
  }else if(data == "2"){
    // Organic
    fetchObject();
    disposeObject(120);
  }else if(data == "3"){
    // Paper
    fetchObject();
    disposeObject(60);
  }else if(data == "4"){
    // Plastic
    fetchObject();
    disposeObject(30);
  }else if(data == "5"){
    // Other
    fetchObject();
    disposeObject(145);
  }
}

// Function to detect object's presence through IR sensor
bool detectObject() {
  bool found = false;
  int sensorStatus = digitalRead(infraPin);

  if (sensorStatus == 0) {
    found = true;
  }

  // Will return 1 if true or 0 if false
  return found;
}

// Function that checks object's presence and distance
void checkDistanceAndObject(){

  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  duration = pulseIn(echoPin, HIGH);
  distance = (duration*.0343)/2;

  bool hasDetect = detectObject();

  String data = String(hasDetect) + " " + String(distance);

  Serial.println(data);
}

// Function to open and close the claws
void activateClaws(){
  int initPos = 0;
  int finalPos = 35;

  for (int pos = initPos; pos <= finalPos; pos += 1) {
    servoClaws.write(pos); 
    delay(15);                
  }

  delay(2000);

  for (int pos = finalPos; pos >= initPos+5; pos -= 1) {
    servoClaws.write(pos);
    delay(15);                 
  }
}

// Function to move robotic arm forward
void moveArmForward(){
  int pos = 0;
  // Move robotic arm forward
  for(pos = 120; pos >= 90; pos -= 1){
    servoLeft.write(pos); // < 90 forward > 90 backward
    delay(15);
  }
}

// Function to move robotic arm backward
void moveArmBackward(){
  int pos = 0;
  for(pos = 90; pos <= 120; pos += 1){
    servoLeft.write(pos); // < 90 forward > 90 backward
    delay(15);
  }
}

void rotateBase(int angle){
  for(int pos = 0; pos <= angle; pos += 1){
    servoBase.write(pos);
    delay(15);
  }
}

void rotateBaseBack(int angle){
  for(int pos = angle; pos >= 0; pos -= 1){
    servoBase.write(pos);
    delay(15);
  }
}

void fetchObject(){
  
  // Move arm forward
  moveArmForward();

  delay(500);

  // Opening and Clsoing the Claws
  activateClaws();

  delay(500);

  // Move robotic arm back
  moveArmBackward();

}

void disposeObject(int angle){
  // Rotate Base
  rotateBase(angle);
  delay(500);
  // Move arm forward 
  moveArmForward();
  delay(500);
  // Opening Closing Claws
  activateClaws();
  delay(500);
  // Move arm back
  moveArmBackward();
  delay(500);
  // Return base to init position
  rotateBaseBack(angle);
  delay(500);
}
