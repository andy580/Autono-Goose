// Define stepper motor connections:
#define sDirPin 6
#define sStepPin 7

// Input command
char command;
bool recieved = false;
 
// Declare stepper motor variables
// Delay in microseconds
int delayStep = 500;
int delayCommand = 50;
int stepsPerRevolution = 200;

void setup() {
//Start serial communication
  Serial.begin(9600);

// Declare stepper motor pins as output:
  pinMode(sStepPin, OUTPUT);
  pinMode(sDirPin, OUTPUT);  
}

void loop(){
  getCommand();
  if (recieved == true){
    if (command == 'r'){
      digitalWrite(sDirPin, HIGH);
      turnOnce();
      recieved = false;
    } else if (command == 'l') {
      digitalWrite(sDirPin, LOW);
      turnOnce();
      recieved = false;
    }
    recieved = false;
  }
  delay(delayCommand);
}

void getCommand() {
  command = Serial.read();
//  Serial.println(command);
  if ( (command == 'r') || (command == 'l') ) {
    recieved = true;
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
