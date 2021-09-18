/**
 * Author Teemu Mäntykallio
 * Initializes the library and turns the motor in alternating directions.
 * Modified by Charles DeLorey for master's thesis project, Hamlyn Centre ICL 2020-2021
*/

// make sure under Tools > Board it's Board: Arduino Due (Programming Port)


#define TRIGGER_PIN 22   // pin for activating EIT system
#define CAM_PIN     26   // pin for syncing webcam footage


int trigger_freq = 40; // Hz
int iters        = 0;
int loopcount    = 0;
int curr_steps   = 0;
#include <DueTimer.h>

void setup() {
  Serial.begin(115200);
  while(!Serial);
  
  pinMode(TRIGGER_PIN, OUTPUT);
  pinMode(CAM_PIN, OUTPUT);
  Timer3.attachInterrupt(triggerReading).setFrequency(trigger_freq);
  Timer3.start();
  Serial.println("Start!");
  digitalWrite(CAM_PIN, HIGH);
}


void loop() {

  if (iters == 1) {
    Timer3.stop();
    Serial.println("Stop");
    digitalWrite(CAM_PIN, LOW);
    iters++; //only run it once
  }

  if (iters < 1) {
    delay(2000);
    iters++;
  }

}


void triggerReading(){
  digitalWrite(TRIGGER_PIN, HIGH);
  Serial.println(curr_steps/2);    // sending step val to pyserial
  digitalWrite(TRIGGER_PIN, LOW);
}



//* could use another arduino pin to measure/signal the movement/motion of the stepper
//  could setup other program on daq to record voltage on direction pin
//  or record digital pin direction pin
//  do loop multiple times and then calculate functional loop speed

// oneFlex : params: 
// - steps is the number of stepper steps the motor will turn
// - rate is the trigger rate for the DAQ sampling
//void oneFlex(int steps, int dly) { //can drop this speed of data collection to make sure it's definitely synchronised with the data collection
//  driver.shaft_dir(0);
//  for (int i=0; i < steps * microstps; i++) {
//    curr_steps++;
//    digitalWrite(STEP_PIN, HIGH);
//    delayMicroseconds(dly);
//    digitalWrite(STEP_PIN, LOW);
//    delayMicroseconds(dly); 
//  }
//}

// oneRelax : params: 
// - steps is the number of stepper steps the motor will turn
// - rate is the trigger rate for the DAQ sampling
//void oneRelax(int steps, int dly) {
//  driver.shaft_dir(1);
//  for (int i=0; i < steps * microstps; i++) {
//    curr_steps--;
//    digitalWrite(STEP_PIN, HIGH);
//    delayMicroseconds(dly);
//    digitalWrite(STEP_PIN, LOW);
//    delayMicroseconds(dly); 
//  }
//}
