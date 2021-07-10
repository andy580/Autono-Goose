// Define stepper motor connections:
#define sDirPin 6
#define sStepPin 7

#define stopRightBtnPin 9
#define stopLeftBtnPin 10

#define steerRightBtnPin 11
#define steerLeftBtnPin 12

#define ledPin 13
#define limStopPin 2 

char command = ' '; 
bool recieved = false;
bool brakeEngaged = true;

int rightBtnState =0;
int leftBtnState =0;


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
  pinMode(sStepPin, OUTPUT);
  pinMode(sDirPin, OUTPUT); 

  setupBrake();
}

void loop(){

rightBtnState = digitalRead(stopRightBtnPin);
leftBtnState = digitalRead(stopLeftBtnPin);
  
//Buttons on breadboard send controls
  if (leftBtnState == HIGH){
    command = 'G';
  }
  if (rightBtnState == HIGH){
    command = 'S';
  }
  
  getCommand(command, recieved);
  execCommand(command, recieved, brakeEngaged);

  command = ' ';
//  delay(delayCommand);

//  if(digitalRead(limStopPin) == LOW) {
//    Serial.println("on");
//  }
  
}


// ////////////////////Helper Functions/////////////////// // 
void setupBrake(){
  digitalWrite(sDirPin, LOW);
  
  while(digitalRead(limStopPin) == HIGH){
//      Serial.println(limStopPin);
      digitalWrite(sStepPin, HIGH);
      delayMicroseconds(delayStep);
      digitalWrite(sStepPin, LOW);
      delayMicroseconds(delayStep);
    if(digitalRead(limStopPin) == LOW) { break; }
  }
  digitalWrite(sDirPin, HIGH);
//  Engange Brake
  for (int i=0; i<setupBrakeTurns; i++){
    turnOnce();
  }
  delayStep = 600;
}


void getCommand(char &command, bool &recieved) {
  if (command == ' '){ command = Serial.read(); }
  if ( (command == 's') || (command == 'g') || (command == 'S') || (command == 'G') ) {
    recieved = true;
  }
}

void execCommand(char &command, bool &recieved, bool &brakeEngaged) {
  if (recieved == true){
    if (command == 's' && brakeEngaged == true) { recieved = false;  }
    if (command == 'g' && brakeEngaged == false) { recieved = false;  }
    
    if (command == 's' && recieved == true){
      Serial.println("Executing Stop");
      digitalWrite(sDirPin, HIGH);
      for (int i=0; i<StopGoTurns; i++) {turnOnce();}
      recieved = false;
      brakeEngaged=true;
    } else if (command == 'g' && recieved == true) {
//      Serial.println("Executing Go");
      digitalWrite(sDirPin, LOW);
      for (int i=0; i<StopGoTurns; i++) {turnOnce();}
      recieved = false;
      brakeEngaged=false;
    }

    else if (command =='S' && recieved == true){
      digitalWrite(sDirPin, HIGH);
      for (int i=0; i<1; i++) {turnOnce();}
      recieved = false;
    }
    else if (command == 'G' && recieved == true) {
//      Serial.println("Executing Go");
      digitalWrite(sDirPin, LOW);
      for (int i=0; i<1; i++) {turnOnce();}
      recieved = false;
    }
    
    Serial.println(brakeEngaged);
    recieved = false;
  }
}

void turnOnce(){
    for (int i = 0; i < stepsPerRevolution; i++) {
    digitalWrite(sStepPin, HIGH);
    delayMicroseconds(delayStep);
    digitalWrite(sStepPin, LOW);
    delayMicroseconds(delayStep);
  }
  
}
