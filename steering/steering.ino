// Define stepper motor connections:
#define steerDirPin 4
#define steerStepPin 5

#define stopDirPin 6
#define stopStepPin 7

#define stopRightBtnPin 9
#define stopLeftBtnPin 10

#define steerRightBtnPin 11
#define steerLeftBtnPin 12

#define ledPin 13
#define limStopPin 2 

char command = ' '; 
char steeringPosn = 'n';

bool recieved = false;
bool brakeEngaged = true;

int stopRightBtnState =0;
int stopLeftBtnState =0;

int steerRightBtnState =0;
int steerLeftBtnState =0;

int StopGoTurns = 6;
int setupBrakeTurns = 15;
 
// Declare stepper motor variables
// Delay in microseconds
//Nema 17
// 150 rpm == 1000 us delayStep
//int delayStep = 1000;

//Nema 23
// usually 500 us delay will lead to ~70-80 RPM = 2000 pps
int delayStep = 750;
int delayCommand = 100;
int stepsPerRevolution = 200;


// /////////////////Main/////////////// // 

void setup() {
// Start serial communication
  Serial.begin(9600);

// LED indicator
  pinMode(ledPin, OUTPUT);
  digitalWrite(ledPin, LOW);

// Buttons
  pinMode(stopRightBtnPin, INPUT);
  pinMode(stopLeftBtnPin, INPUT);

// Limit Switch
  pinMode(limStopPin, INPUT);

// Declare stepper motor pins as output:
  pinMode(stopStepPin, OUTPUT);
  pinMode(stopDirPin, OUTPUT); 

  pinMode(steerStepPin, OUTPUT);
  pinMode(steerDirPin, OUTPUT);

  setupBrake();
}

void loop(){

stopRightBtnState = digitalRead(stopRightBtnPin);
stopLeftBtnState = digitalRead(stopLeftBtnPin);
steerRightBtnState = digitalRead(steerRightBtnPin);
steerLeftBtnState = digitalRead(steerLeftBtnPin);
  
//Buttons on breadboard send controls
  if (stopLeftBtnState == HIGH){
    command = 'G';
  }
  if (stopRightBtnState == HIGH){
    command = 'S';
  }
  if (steerLeftBtnState == HIGH){
    command = 'L';
    Serial.println("Left Button Pressed");
  }
  if (steerRightBtnState == HIGH){
    command = 'R';
    Serial.println("Right Button Pressed");
  }
  
  getCommand(command, recieved);
  execCommand(command, recieved, brakeEngaged, steeringPosn);

  command = ' ';
//  delay(delayCommand);

//  if(digitalRead(limStopPin) == LOW) {
//    Serial.println("on");
//  }
  
}


// ////////////////////Helper Functions/////////////////// // 
void setupBrake(){
  digitalWrite(stopDirPin, LOW);
  
  while(digitalRead(limStopPin) == HIGH){
//      Serial.println(limStopPin);
      digitalWrite(stopStepPin, HIGH);
      delayMicroseconds(delayStep);
      digitalWrite(stopStepPin, LOW);
      delayMicroseconds(delayStep);
    if(digitalRead(limStopPin) == LOW) { break; }
  }
  digitalWrite(stopDirPin, HIGH);
//  Engange Brake
  for (int i=0; i<setupBrakeTurns; i++){
    turnOnce(stopStepPin);
  }
  delayStep = 600;
}


void getCommand(char &command, bool &recieved) {
  if (command == ' '){ command = Serial.read(); }
  if ( (command == 's') || (command == 'g') || (command == 'S') || (command == 'G') || (command == 'l') || (command == 'r') || (command == 'L') || (command == 'R') ) {
    recieved = true;
  }
}

void execCommand(char &command, bool &recieved, bool &brakeEngaged, char &steeringPosn) {
  if (recieved == true){
    if (command == 's' && brakeEngaged == true) { recieved = false;  }
    if (command == 'g' && brakeEngaged == false) { recieved = false;  }
    if (command == steeringPosn) { recieved = false; }
    
    if (command == 's' && recieved == true){
      Serial.println("Executing Stop");
      digitalWrite(stopDirPin, HIGH);
      for (int i=0; i<StopGoTurns; i++) {turnOnce(stopStepPin);}
      recieved = false;
      brakeEngaged=true;
    } else if (command == 'g' && recieved == true) {
//      Serial.println("Executing Go");
      digitalWrite(stopDirPin, LOW);
      for (int i=0; i<StopGoTurns; i++) {turnOnce(stopStepPin);}
      recieved = false;
      brakeEngaged=false;
    }
    else if (command =='S' && recieved == true){
      digitalWrite(stopDirPin, HIGH);
      for (int i=0; i<1; i++) {turnOnce(stopStepPin);}
      recieved = false;
    }
    else if (command == 'G' && recieved == true) {
//      Serial.println("Executing Go");
      digitalWrite(stopDirPin, LOW);
      for (int i=0; i<1; i++) {turnOnce(stopStepPin);}
      recieved = false;
    }
    else if (command == 'l' && recieved == true) {
      Serial.println("Executing Left");
      digitalWrite(steerDirPin, LOW);
      for (int i=0; i< 15; i++) {turnOnce(steerStepPin);}
      steeringPosn = 'l';
      recieved = false;
    }
    else if (command == 'r' && recieved == true) {
      Serial.println("Executing Right");
      digitalWrite(steerDirPin, HIGH);
      for (int i=0; i< 15; i++) {turnOnce(steerStepPin);}
      steeringPosn = 'r';
      recieved = false;
    }
    else if (command == 'n' && recieved == true) {
      Serial.println("Executing Neutral");
      if (steeringPosn == 'r') {digitalWrite(steerDirPin, LOW);}
      else if (steeringPosn == 'l') {digitalWrite(steerDirPin, HIGH);}
      for (int i=0; i<15; i++) {turnOnce(steerStepPin);}
      recieved = false;
    }
    else if (command =='L' && recieved == true){
      digitalWrite(steerDirPin, LOW);
      for (int i=0; i<1; i++) {turnOnce(steerDirPin);}
      recieved = false;
    }
    else if (command =='R' && recieved == true){
      digitalWrite(steerDirPin, HIGH);
      for (int i=0; i<1; i++) {turnOnce(steerDirPin);}
      recieved = false;
    }
    
    Serial.println(brakeEngaged);
    recieved = false;
  }
}

void turnOnce(const int &motorPin){
    for (int i = 0; i < stepsPerRevolution; i++) {
    digitalWrite(motorPin, HIGH);
    delayMicroseconds(delayStep);
    digitalWrite(motorPin, LOW);
    delayMicroseconds(delayStep);
  }
  
}
