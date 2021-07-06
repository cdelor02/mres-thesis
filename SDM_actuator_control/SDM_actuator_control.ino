/**
 * Author Teemu Mäntykallio
 * Initializes the library and turns the motor in alternating directions.
 * Modified by Charles DeLorey for master's thesis project, Hamlyn Centre ICL 2020-2021
*/

// make sure under Tools > Board it's Board: Arduino Due (Programming Port)

#define EN_PIN      4    // Nano v3:	16 Mega:	38	//enable (CFG6)
#define DIR_PIN     6    //			19			55	//direction
#define STEP_PIN    5    //			18			54	//step
#define CS_PIN      7    //			17			64	//chip select
#define TRIGGER_PIN 22   // pin for activating EIT system

const int stepsPerRevolution = 200;  // change this to fit 
// the number of steps per revolution for your motor

bool dir             = true;
int incomingb        = 0;
int receivedVal      = 0;
boolean newData      = false;
int num              = 0;
double spool_diam    = 31.4159;
double steps_per_1mm = 1 / (spool_diam / stepsPerRevolution);
int microstps        = 2;
int iters            = 0;
unsigned long starttime;
unsigned long endtime;
double cable_len_val = 0;
unsigned long curr_steps    = 0;

#include <DueTimer.h>
#include <TMC2130Stepper.h>
TMC2130Stepper driver = TMC2130Stepper(EN_PIN, DIR_PIN, STEP_PIN, CS_PIN);

void setup() {
	Serial.begin(9600);
	while(!Serial);
	Serial.println("Start...");
	SPI.begin();
	pinMode(MISO, INPUT_PULLUP);
	driver.begin(); 			    // Initiate pins and registeries
	driver.rms_current(600); 	// Set stepper current to 600mA. The command is the same as command TMC2130.setCurrent(600, 0.11, 0.5);
	driver.stealthChop(1); 	  // Enable extremely quiet stepping
	
	digitalWrite(EN_PIN, LOW);
  driver.microsteps(microstps);
  Serial.print("Microsteps: "); Serial.println(driver.microsteps());
  pinMode(TRIGGER_PIN, OUTPUT);
  Timer3.attachInterrupt(triggerReading).setFrequency(10);
  Serial.print("Curr steps start: "); Serial.println(curr_steps);
}


void loop() {   // DON'T FORGET TO SET SHAFT_DIR

// ** I think the stepper works better at 256 microsteps
// oneFlex() and oneRelax() only for when microsteps != 0
  recvOneVal();
  if (newData == true) {
    Serial.print("# iterations: "); Serial.println(receivedVal);
    Timer3.start();
    while (iters < receivedVal) {
      Serial.print("Iteration: "); Serial.println(iters+1);
//      actuateInStages(true, 2, 134, 2000, 40);
//      delay(2000);
//      actuateInStages(false, 2, 134, 2000, 40);
//      delay(2000);      
      //delayWithSampling(2000, 40);

      oneFlex(100, 40);
      Serial.print("curr_steps after Flex: "); Serial.println(curr_steps);
      delay(4000);
//      oneFlex(67, 40);
//      delay(4000);
      oneRelax(100, 40);
            Serial.print("curr_steps after relax: "); Serial.println(curr_steps);

      delay(4000);
//      oneRelax(67, 40);
//      delay(4000);

    iters++;
    }
    newData = false;
    Timer3.stop();
    if (iters == receivedVal) {
      Timer3.stop();
    }
  }
}


void triggerReading(){
  digitalWrite(TRIGGER_PIN, HIGH);
  digitalWrite(TRIGGER_PIN, LOW);
  Serial.print("curr steps: "); Serial.println(curr_steps);
}

void recvOneVal() {
  if (Serial.available() > 0) {
    receivedVal = Serial.parseInt();
    newData = true;
  }
}


void delayWithSampling(int duration, int rate) {
  starttime = millis();
  //endtime = starttime;
  while ((millis() - starttime) <= duration) {

  // sample data at specified rate
  if (starttime % rate == 0) {
      digitalWrite(TRIGGER_PIN, HIGH);
      digitalWrite(TRIGGER_PIN, LOW);      
  }  
  
  //endtime = millis();
  }
}

//* could use another arduino pin to measure/signal the movement/motion of the stepper
//  could setup other program on daq to record voltage on direction pin
//  or record digital pin direction pin
//  do loop multiple times and then calculate functional loop speed

// oneFlex : params: 
// - steps is the number of stepper steps the motor will turn
// - rate is the trigger rate for the DAQ sampling
void oneFlex(int steps, int rate) { //can drop this speed of data collection to make sure it's definitely synchronised with the data collection
  driver.shaft_dir(0);

  for (int i=0; i < steps * microstps; i++) {
    curr_steps++;
//    if (i % rate == 0) {
//      digitalWrite(TRIGGER_PIN, HIGH);
//    }
    digitalWrite(STEP_PIN, HIGH);
    delayMicroseconds(1000);
    digitalWrite(STEP_PIN, LOW);
    delayMicroseconds(1000); 
//    if (i % rate == 0) {
//      digitalWrite(TRIGGER_PIN, LOW);
//    }  
  }
}

// oneRelax : params: 
// - steps is the number of stepper steps the motor will turn
// - rate is the trigger rate for the DAQ sampling
void oneRelax(int steps, int rate) {
  driver.shaft_dir(1);
  
  for (int i=0; i < steps * microstps; i++) {
    curr_steps--;
//    if (i % rate == 0) {
//      digitalWrite(TRIGGER_PIN, HIGH);
//    }
    digitalWrite(STEP_PIN, HIGH);
    delayMicroseconds(1000);
    digitalWrite(STEP_PIN, LOW);
    delayMicroseconds(1000); 
//    if (i % rate == 0) {
//      digitalWrite(TRIGGER_PIN, LOW);
//    }  
  }
}

// **the number of stages must be a divisor of steps
void actuateInStages(bool flex, int stages, int steps, int dly, int rate) {
  if (flex) {
    for (int i=0; i < stages; i++) {
      oneFlex(steps/stages, rate);
      delay(dly);
    }
  } else {
    for (int i=0; i < stages; i++) {
      oneRelax(steps/stages, rate);
      delay(dly);      
    }
  }
}

double stepToDist(int steps) {
  Serial.println("stepToDist");
  Serial.print(steps); Serial.print(" "); Serial.println(steps_per_1mm);
  return steps / steps_per_1mm;
}

int distToStep(int dist) {
  // Takes distance in mm and converts it to the
  // corresponding number of steps given the spool diameter
  return dist * steps_per_1mm;
}
