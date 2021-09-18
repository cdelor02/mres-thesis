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
#define CAM_PIN     26   // pin for syncing webcam footage

const int stepsPerRevolution = 200;  // change this to fit 
// the number of steps per revolution for your stepper

int receivedVal         = 0;
boolean newData         = false;
double spool_diam       = 31.4159;
double steps_per_1mm    = 1 / (spool_diam / stepsPerRevolution);
int microstps           = 2;
int iters               = 0;
unsigned int curr_steps = 0;
int trigger_freq        = 40; // Hz

String shakeInput       = "";
char* shakeKey          = "S";
bool shakeFlag          = false;
float timeAtStep        = 0;
String flushInputBuffer = "";
char* data              = "";
int   randStep          = 0;

int loopcount=0;

#include <DueTimer.h>
#include <TMC2130Stepper.h>
TMC2130Stepper driver = TMC2130Stepper(EN_PIN, DIR_PIN, STEP_PIN, CS_PIN);

void setup() {
	Serial.begin(115200);
	while(!Serial);
	SPI.begin();
	pinMode(MISO, INPUT_PULLUP);
	driver.begin(); 			    // Initiate pins and registeries
	driver.rms_current(600); 	// Set stepper current to 600mA. The command is the same as command TMC2130.setCurrent(600, 0.11, 0.5);
	driver.stealthChop(1); 	  // Enable extremely quiet stepping
	
	digitalWrite(EN_PIN, LOW);
  driver.microsteps(microstps);
//  Serial.print("Microsteps: "); Serial.println(driver.microsteps());
  pinMode(TRIGGER_PIN, OUTPUT);
  pinMode(CAM_PIN, OUTPUT);
  Timer3.attachInterrupt(triggerReading).setFrequency(trigger_freq);
//  Serial.print("Trigger freq: "); Serial.print(trigger_freq); Serial.println(" Hz");
//  Serial.print("Curr steps: "); Serial.println(curr_steps);
//  Serial.print("Available bytes: "); Serial.println(Serial.availableForWrite());

  Timer3.start();
  digitalWrite(CAM_PIN, HIGH);
}


void loop() {   // DON'T FORGET SHAFT_DIR

// ** the stepper works better at 256 microsteps
// oneFlex() and oneRelax() only for when microsteps != 0

//  recvOneVal();
//  if(newData == true) {
//    if(receivedVal == -1) {
//      digitalWrite(CAM_PIN, HIGH);
//      delay(2 * 1000);
//      digitalWrite(CAM_PIN, LOW);
//      Serial.println(receivedVal);
//      newData = false;
//      Serial.flush();
//    }
//  } 

//  randStep = random(20, 101);

  if (iters == 10) {
    digitalWrite(CAM_PIN, LOW);
    Timer3.stop();
    loopcount=0;
    Serial.println(-1);
    iters++; //only run it once
  }

  if (iters < 10) {
    delay(2000);
    oneFlex(100,  4000);
    delay(2000);
    oneRelax(100, 4000);
    //delay(1000);
    iters++;
  }


  //recvOneVal();
//  receivedVal = 100;
//  newData = true;

//  if (newData == true) {
    //Serial.print("# iterations: "); Serial.println(receivedVal);
//    Timer3.start();
//    while (true) {
//      Serial.print("Iteration: "); Serial.println(iters+1);
//      actuateInStages(true, 2, 134, 2000, 40);
//      delay(2000);
//      actuateInStages(false, 2, 134, 2000, 40);
//      delay(2000);      
      //delayWithSampling(2000, 40);

//      delay(4000);
//      oneFlex(receivedVal, 1000);
      //Serial.print("ACTUAL curr_steps after Flex: "); Serial.println(curr_steps/2);
//      delay(4000);
//      oneFlex(67, 40);
//      delay(4000);
//      oneRelax(receivedVal, 1000);
    //Serial.print("ACTUAL curr_steps after relax: "); Serial.println(curr_steps/2);

//      oneRelax(67, 40);
//      delay(4000);

//    iters++;
//    }
//    newData = false;
//    Timer3.stop();
//    if (iters == receivedVal) {
//      Timer3.stop();
//    }
//  }
}


void triggerReading(){
  digitalWrite(TRIGGER_PIN, HIGH);
  //loopcount++;

  //if (loopcount % 10 == 0)
  //{
    //Serial.print(loopcount);
    //Serial.print(",");
  Serial.println(curr_steps/2);    // sending step val to pyserial
  //}
  digitalWrite(TRIGGER_PIN, LOW);
}

void recvOneVal() {
  if (Serial.available() > 0) {
    receivedVal = Serial.parseInt();
    newData = true;
  }
}


//* could use another arduino pin to measure/signal the movement/motion of the stepper
//  could setup other program on daq to record voltage on direction pin
//  or record digital pin direction pin
//  do loop multiple times and then calculate functional loop speed

// oneFlex : params: 
// - steps is the number of stepper steps the motor will turn
// - rate is the trigger rate for the DAQ sampling
void oneFlex(int steps, int dly) { //can drop this speed of data collection to make sure it's definitely synchronised with the data collection
  driver.shaft_dir(0);
  for (int i=0; i < steps * microstps; i++) {
    curr_steps++;
    digitalWrite(STEP_PIN, HIGH);
    delayMicroseconds(dly);
    digitalWrite(STEP_PIN, LOW);
    delayMicroseconds(dly); 
  }
}

// oneRelax : params: 
// - steps is the number of stepper steps the motor will turn
// - rate is the trigger rate for the DAQ sampling
void oneRelax(int steps, int dly) {
  driver.shaft_dir(1);
  for (int i=0; i < steps * microstps; i++) {
    curr_steps--;
    digitalWrite(STEP_PIN, HIGH);
    delayMicroseconds(dly);
    digitalWrite(STEP_PIN, LOW);
    delayMicroseconds(dly); 
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
  // Takes distance in steps and converts it to the
  // corresponding millimeter change given the spool diameter
  return steps / steps_per_1mm;
}

int distToStep(int dist) {
  // Takes distance in mm and converts it to the
  // corresponding number of steps given the spool diameter
  return dist * steps_per_1mm;
}


void handShake() {
  while (Serial.available() > 0) {
    shakeInput = Serial.readStringUntil('\n');
    if (shakeInput != ""){
//      sprintf(data, "%s\n", shakeKey);
      Serial.println(shakeInput);
      Serial.flush();
//        shakeFlag = true;
        // Enable the motor after handshaking
//        digitalWrite(TRIGGER_PIN, HIGH);
//        shakeInput = "";
        // Initialise the time variables
//        timeAtStep = micros();
//        flushInputBuffer = Serial.readStringUntil('\n');
    }
  }
}
