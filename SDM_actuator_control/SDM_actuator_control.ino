/**
 * Author Teemu Mäntykallio
 * Initializes the library and turns the motor in alternating directions.
 * Modified by Charles DeLorey for master's thesis project
*/

// make sure under Tools > Board it's Board: Arduino Due (Programming Port)

#define EN_PIN    4  // Nano v3:	16 Mega:	38	//enable (CFG6)
#define DIR_PIN   6  //			19			55	//direction
#define STEP_PIN  5  //			18			54	//step
#define CS_PIN    7  //			17			64	//chip select
#define TRIGGER_PIN 22 // pin for activating EIT system

const int stepsPerRevolution = 200;  // change this to fit the number of steps per revolution
// for your motor

bool dir = true;
int incomingb = 0;
int receivedVal = 0;
boolean newData = false;
int num = 0;

#include <TMC2130Stepper.h>
TMC2130Stepper driver = TMC2130Stepper(EN_PIN, DIR_PIN, STEP_PIN, CS_PIN);

void setup() {
	Serial.begin(9600);
	while(!Serial);
	Serial.println("Start...");
	SPI.begin();
	pinMode(MISO, INPUT_PULLUP);
	driver.begin(); 			// Initiate pins and registeries
	driver.rms_current(600); 	// Set stepper current to 600mA. The command is the same as command TMC2130.setCurrent(600, 0.11, 0.5);
	driver.stealthChop(1); 	// Enable extremely quiet stepping
	
	digitalWrite(EN_PIN, LOW);
  //driver.microsteps(0);
  Serial.print("Microsteps: "); Serial.println(driver.microsteps());
  pinMode(TRIGGER_PIN, OUTPUT);
}

void loop() { // DON'T FORGET TO SET SHAFT_DIR
  //recvOneVal(); // if driver microsteps == 0, then use vals in the high 10s 
  //driver.shaft_dir(1); // 0 is anticlockwise, 1 is clockwise

// ** I think the stepper works better at 256 microsteps
// oneFlex() and oneRelax() only for when microsteps != 0
  oneFlex();
  delay(4000);
  oneRelax();
  delay(4000);

//  if (newData == true) {
//    digitalWrite(TRIGGER_PIN, HIGH); //activate DAQ
//    for (int i=0; i < receivedVal; i++) {
//      //Serial.print(i); Serial.print(" ");
//      digitalWrite(STEP_PIN, HIGH);
//      delayMicroseconds(10);
//      digitalWrite(STEP_PIN, LOW);
//      delayMicroseconds(10);
//    }
//    Serial.println("end.");
//    newData = false;
//    digitalWrite(TRIGGER_PIN, LOW); //stop DAQ
//  }
}
  

  
  
//  delay(4000);
//  if (newData == true) {
//    Serial.print("input: ");
//    Serial.println(receivedVal);
//    // use input to change direction
//  driver.shaft_dir(0);
    //turnSteps(receivedInt, 1, 10);
//    if (receivedVal == '0') {
//      driver.shaft_dir(0);
//    } else if (receivedVal == '1') {
//      driver.shaft_dir(1);    
//    }
//    newData = false;
//}


void recvOneVal() {
  if (Serial.available() > 0) {
    receivedVal = Serial.parseInt();
    newData = true;
  }
}

// for when microsteps != 0
void oneFlex() {
  driver.shaft_dir(0);
  digitalWrite(TRIGGER_PIN, HIGH);
  for (int i=0; i < 29000; i++) {
    digitalWrite(STEP_PIN, HIGH);
    delayMicroseconds(10);
    digitalWrite(STEP_PIN, LOW);
    delayMicroseconds(10);
  }
  //digitalWrite(TRIGGER_PIN, LOW);  
}

// for when microsteps != 0
void oneRelax() {
  driver.shaft_dir(1);
//  digitalWrite(TRIGGER_PIN, HIGH);
  for (int i=0; i < 29000; i++) {
    digitalWrite(STEP_PIN, HIGH);
    delayMicroseconds(10);
    digitalWrite(STEP_PIN, LOW);
    delayMicroseconds(10);
  }
  digitalWrite(TRIGGER_PIN, LOW);
}


void stepOne(int dly) {
  delayMicroseconds(dly);
  digitalWrite(STEP_PIN, HIGH);
  delayMicroseconds(dly);
  digitalWrite(STEP_PIN, LOW);
  delayMicroseconds(dly);
}

void stepN(int dly, int steps) {
  for (int i = 0; i < steps; i++) {
    stepOne(dly);
  }
}

int distToStep(int dist) {
  // according to some ridiculous calculations,
  // 0.0872 mm == 1 degree = 0.55 steps
  return dist / 0.55;
}

void turnSteps(int steps, int dir, int dly) {
  driver.shaft_dir(dir);
  if (dir == 0) {
    Serial.print("Turning left by ");
    Serial.println(steps);
  } else {
    Serial.print("Turning right by ");
    Serial.println(steps);
  }
  for (int i=0; i < steps; i++) {
    delayMicroseconds(dly);
    digitalWrite(STEP_PIN, HIGH);
    delayMicroseconds(dly);
    digitalWrite(STEP_PIN, LOW);
    delayMicroseconds(dly);
  }
  delay(10);
}
