// Define stepper motor connections:
#define sDirPin 6
#define sStepPin 7

#define rightBtnPin 2
#define leftBtnPin 3

#define ledPin 13

char command = ' '; 
bool recieved = false;

int rightBtnState =0;
int leftBtnState =0;
 
// Declare stepper motor variables
// Delay in microseconds
//Nema 17
// 150 rpm == 1000 us delayStep
//int delayStep = 1000;

//Nema 23
// usually 500 us delay will lead to ~70-80 RPM = 2000 pps
int delayStep = 1000;
int delayCommand = 100;
int stepsPerRevolution = 850;


// /////////////////Main/////////////// // 

void setup() {
// Start serial communication
  Serial.begin(9600);

// LED indicator
  pinMode(ledPin, OUTPUT);
  digitalWrite(ledPin, LOW);

// Buttons
  pinMode(rightBtnPin, INPUT);
  pinMode(leftBtnPin, INPUT);

// Declare stepper motor pins as output:
  pinMode(sStepPin, OUTPUT);
  pinMode(sDirPin, OUTPUT); 
}

void loop(){

rightBtnState = digitalRead(rightBtnPin);
leftBtnState = digitalRead(leftBtnPin);
  
//Buttons on breadboard send controls
  if (leftBtnState == HIGH){
    command = 'l';
  }
  if (rightBtnState == HIGH){
    command = 'r';
  }
  
  getCommand(command, recieved);
  execCommand(command, recieved);

  command = ' ';
  delay(delayCommand);
  
}


// ////////////////////Helper Functions/////////////////// // 
void turn(int number){
  digitalWrite(sDirPin, HIGH);
  for (int i=0; i<number; i++){
    turnOnce();
  }
  delay(delayCommand);
  
  digitalWrite(sDirPin, LOW);
  for (int i=0; i<number; i++){
    turnOnce();
  }
  delay(delayCommand);
}


void getCommand(char &command, bool &recieved) {
//  command = Serial.read();
  if ( (command == 'r') || (command == 'l') ) {
    recieved = true;
  }
}

void execCommand(char &command, bool &recieved) {
  if (recieved == true){
    if (command == 'r'){
      Serial.println("Executing right");
      digitalWrite(ledPin, HIGH);
      digitalWrite(sDirPin, HIGH);
      turnOnce();
      recieved = false;
      digitalWrite(ledPin, LOW);
    } else if (command == 'l') {
      Serial.println("Executing left");
      digitalWrite(ledPin, HIGH);
      digitalWrite(sDirPin, LOW);
      turnOnce();
      recieved = false;
      digitalWrite(ledPin, LOW);
    }
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