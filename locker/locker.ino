// import libraries and definitions
#include <Servo.h>
#include <stdlib.h>
#define TOT_DRAWERS 2
#define CLOSING_TIME 10000

typedef struct {
  Servo s;
  int pin;
} drawer;

// allocation and initialization of the drawers
drawer* d = (drawer*) malloc(TOT_DRAWERS*sizeof(drawer));

char inNum;        // input number from serial
int* cState = (int*) malloc(TOT_DRAWERS*sizeof(int));       // current states
int* futureState = (int*) malloc(TOT_DRAWERS*sizeof(int));  // future states
unsigned long* lasttime = (unsigned long*) malloc(TOT_DRAWERS*sizeof(unsigned long));
unsigned int drawer_number = 0;

// TOT_DRAWERS states (one for each drawer)
// one state can be 0: close or 1: open

void setup() {
    Serial.begin(9600);
    
    d[0].pin = 2;
    d[1].pin = 3;
    
    for(int i = 0; i < TOT_DRAWERS; i++){
      d[i].s = Servo();
      d[i].s.attach(d[i].pin);
      Serial.print("servo ");
      Serial.print(i);
      Serial.println(" -> angle 0");

      cState[i] = 0; // all initial states (closed)
      futureState[i] = 0; // all future states (closed)
    }

  // print status to the Serial Monitor
  Serial.println("Setup finished");
}



void loop() {
  // check all the interval time
  for(int i = 0; i < TOT_DRAWERS; i++){
    if((cState[i] == 1) && (millis() - lasttime[i] < CLOSING_TIME)) {
        futureState[i] = 1; // stay open
    }
    else{
      futureState[i] = 0; // close
    }
  }

  // read external inputs
  if(Serial.available() > 0){
    inNum = Serial.read();          // it should be the drawer to open (an integer)
    //drawer_number = inNum - '0';  // it should be the drawer to open (a string)
    drawer_number = inNum;
 
    if(drawer_number >= 0 && drawer_number < TOT_DRAWERS){ // check input (useless)
        Serial.print("Received ");
        Serial.println(drawer_number);
        
        // future state estimation and actions
        futureState[drawer_number] = 0;   // default (closed)
        if(cState[drawer_number] == 0){
          lasttime[drawer_number] = millis();  // start counting the opening time
          futureState[drawer_number] = 1; // open drower
        }
        if(cState[drawer_number] == 1) {
          lasttime[drawer_number] = millis();
          futureState[drawer_number] = 1; // stay open
        }
      }
    }

    Serial.println("OnEnter Actions");
        
     // onEnter Actions
     for(int i = 0; i < TOT_DRAWERS; i++){

        d[i].s.write(0 + futureState[i]*300);
        
        Serial.print("servo ");
        Serial.print(i);
        Serial.print(" -> angle ");
        Serial.println(futureState[i]*300);
     }
     
      // state transition
      for(int i = 0; i < TOT_DRAWERS; i++){
        cState[i]=futureState[i];
      }
      delay(2000);
}
