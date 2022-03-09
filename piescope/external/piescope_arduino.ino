#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "math.h"

using namespace std;

//DIGITAL PINS USABLE FOR INTERRUPTS
//Mega, Mega2560, MegaADK:           2, 3, 18, 19, 20, 21
//Micro, Leonardo, other 32u4-based: 0, 1, 2, 3, 7

// Pin assignments
const int LASER_640 = 15;
const int LASER_561 = 4;
const int LASER_488 = 5;
const int LASER_405 = 11;

const int LASER_640_INTERRUPT = 18;
const int LASER_561_INTERRUPT = 19;
const int LASER_488_INTERRUPT = 20;
const int LASER_405_INTERRUPT = 21;

const int camera = 17;
const int camera_done = 9;
const int stage_interruptPin = 2;
const int slice_interruptPin = 3;

// Laser variables
int LASERS[] = {LASER_640, LASER_561, LASER_488, LASER_405};
long int exposure_405;
long int exposure_488;
long int exposure_561;
long int exposure_640;

// state for checking interrupts
volatile byte state = LOW;

// counter for the 9 sets of images to be taken per slice
const int n_sets = 9;
volatile int set_counter = 0;

// flag for starting a new set of images (1 means ready for new slice)
volatile bool ready_to_slice = 1;
volatile bool waiting_on_objective = 0;
volatile bool objective_ready = 1;

// Serial communication variables
int N = 0;
String input = "";
String numbers[12];
String temp = "";

// counter for timeout on stage not moving
unsigned long finish_time = 0;
unsigned long elapsed_time = 0;

//*****************************************************************************************************
void setup() {
  Serial.begin(115200); // use the same baud-rate as the python side

  // Pin Modes
  pinMode(camera, OUTPUT);
  pinMode(camera_done, OUTPUT);
  pinMode(LASER_640, OUTPUT);
  pinMode(LASER_561, OUTPUT);
  pinMode(LASER_488, OUTPUT);
  pinMode(LASER_405, OUTPUT);

  digitalWrite(LASER_640, LOW);
  digitalWrite(LASER_561, LOW);
  digitalWrite(LASER_488, LOW);
  digitalWrite(LASER_405, LOW);
  // Interrupts
  pinMode(LASER_640_INTERRUPT, INPUT_PULLUP);
  pinMode(LASER_561_INTERRUPT, INPUT_PULLUP);
  pinMode(LASER_488_INTERRUPT, INPUT_PULLUP);
  pinMode(LASER_405_INTERRUPT, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(LASER_640_INTERRUPT), ChangeState640, CHANGE);
  attachInterrupt(digitalPinToInterrupt(LASER_561_INTERRUPT), ChangeState561, CHANGE);
  attachInterrupt(digitalPinToInterrupt(LASER_488_INTERRUPT), ChangeState488, CHANGE);
  attachInterrupt(digitalPinToInterrupt(LASER_405_INTERRUPT), ChangeState405, CHANGE);

  pinMode(stage_interruptPin, INPUT_PULLUP);
  pinMode(slice_interruptPin, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(stage_interruptPin), StageComplete, FALLING);
  attachInterrupt(digitalPinToInterrupt(slice_interruptPin), ObjectiveReady, RISING);
}
//*****************************************************************************************************

// Main loop for reading serial comms
void loop() {

//  digitalWrite(1, LOW);
//}
  // wait for objective if imaging is complete
  if (waiting_on_objective) {
    finish_time = millis();
    while (!objective_ready) {
      elapsed_time = millis() - finish_time;
      if (elapsed_time > 5000)
      {
        waiting_on_objective = 0;
        Serial.println("TIMED OUT WAITING FOR OBJECTIVE");
        break;
      }
    }
    if (objective_ready){
      TakeSliceImages();
    }
  }

  // if not waiting on objective, wait for serial
  while (Serial.available()) {
    delay(2);
    if (Serial.available() > 0) {
      char c = Serial.read();
      input += c;
    }
  }

  if (input.length() > 0 && input[0] == 'E') {
    N = 0;
    // print incoming serial comm
    Serial.print("Received ");
    Serial.println(input);

    // go through each character
    for (int ii = 1; ii <= input.length(); ++ii) {
      // if the char is a digit, append it to an array
      if (isdigit(input[ii]) ) {
        temp += input[ii];
      }

      //this 0 is not an integer, is null string
      else if (input[ii] == ' ' || input[ii] == 0) {
        numbers[N] = temp;
        temp = "";
        if (input[ii] == ' ') N++;
      }
    }
    N++;

    exposure_405 = stringToInt(numbers[3]);
    exposure_488 = stringToInt(numbers[2]);
    exposure_561 = stringToInt(numbers[1]);
    exposure_640 = stringToInt(numbers[0]);

    // reset slice variables
    ready_to_slice = 1;
    set_counter = 0;
    Serial.println("running TakeSliceImages");
    TakeSliceImages();
    Serial.print("Waiting on objective flag: ");
    Serial.println(waiting_on_objective);
    Serial.println("finished TakeSliceImages");
    

    for (int jj = 0; jj < N; jj++)
      numbers[jj] = "";
  }

  input = "";
  Serial.flush();
}

//*****************************************************************************************************
void TakeSliceImages() {
  waiting_on_objective = 0;
  objective_ready = 0;
  set_counter = 0;
  while (set_counter < n_sets) {
    if (ready_to_slice) {
      // reset ready_to_slice
      ready_to_slice = 0;

      // increment set_counter
      set_counter++;
      TakeImages();

      // Prints 'Image set X taken.'
      Serial.print("Image set ");
      Serial.print(set_counter);
      Serial.print(" / ");
      Serial.print(n_sets);
      Serial.println(" taken.");
    }
  }
  
  waiting_on_objective = 1;
}


void TakeImages() {
  long int exposures[] = {exposure_640, exposure_561, exposure_488, exposure_405};
  Serial.println("Taking image set ");
  for (int index = 0; index <= 3; index++) {
    if (exposures[index] != 0) {
      // camera and laser on
      digitalWrite(camera, HIGH);
      digitalWrite(LASERS[index], HIGH);

      // wait for exposure time
      delay(exposures[index]);
      Serial.print("Exposing for ");
      Serial.print(exposures[index]);
      Serial.println(" ms.");

      // camera and laser off
      digitalWrite(camera, LOW);
      digitalWrite(LASERS[index], LOW);

      delay(125); // Required for falling edge to trigger on camera
    }
  }
  digitalWrite(camera_done, HIGH);
  delay(100);
  digitalWrite(camera_done, LOW);
}

void StageComplete() {
  Serial.println("Stage finished moving");
  Serial.println("setting ready_to_slice to 1");
  ready_to_slice = 1;
}

void ObjectiveReady() {
  Serial.println("Objective ready for next slice");
  Serial.println("setting objective_ready to 1");
  objective_ready = 1;
}

//*****************************************************************************************************
void ChangeState640() {
  state = digitalRead(LASER_640_INTERRUPT);

    Serial.println("Laser: 640");
    Serial.print("State: ");
    Serial.println(state);

  digitalWrite(LASER_640, state);
  digitalWrite(camera, state);
}
void ChangeState561() {
  state = digitalRead(LASER_561_INTERRUPT);

    Serial.println("Laser: 561");
    Serial.print("State: ");
    Serial.println(state);

  digitalWrite(LASER_561, state);
  digitalWrite(camera, state);
}
void ChangeState488() {
  state = digitalRead(LASER_488_INTERRUPT);

  //  Serial.println("Laser: 488");
  //  Serial.print("State: ");
  //  Serial.println(state);

  digitalWrite(LASER_488, state);
  digitalWrite(camera, state);
}
void ChangeState405() {
  state = digitalRead(LASER_405_INTERRUPT);

  //  Serial.println("Laser: 405");
  //  Serial.print("State: ");
  //  Serial.println(state);

  digitalWrite(LASER_405, state);
  digitalWrite(camera, state);
}
//*****************************************************************************************************
unsigned long stringToInt(String num) {
  int len;
  unsigned long dec = 0;
  len = num.length();
  for (int i = 0; i < len; i++) {
    dec = dec * 10 + ( num[i] - '0' );
  }
  return dec;
}
//*****************************************************************************************************
