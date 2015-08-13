
/////////////////////////////////////////
/////////////////////////////////////////

/*
  HomeEasy software
  by Vicente Abarca
*/

/////////////////////////////////////////
/////////////////////////////////////////

#define MAX_BUFFER_SIZE   1405
#define INPUT_PIN         2
#define OUTPUT_PIN        3
#define OUTPUT_PIN_DEBUG  4
#define LED_PIN           13

#define END_MSG           255
#define TEMP_10000_US     254
#define TEMP_5000_US      253

byte inputFirstState = LOW;
unsigned char outputStreamTime[MAX_BUFFER_SIZE];
unsigned int outputStreamIndex = 0;
unsigned long prevMicrosTime = 0;
unsigned long currentMicrosTime = 0;
unsigned int iIterations = 0;

// Tres valores especiales que duran mas de 2550 us
//  y por lo tanto no se pueden codificar en un byte:
// - 5000 us - codificado como TEMP_5000_US
// - 10000 us - codificado como TEMP_10000_US
// - Final de trama - codificado como END_MSG

/////////////////////////////////////////
/////////////////////////////////////////

void toggleLed()
{
  digitalWrite(LED_PIN, !digitalRead(LED_PIN));
}

/////////////////////////////////////////

void int0Func()
{

  iIterations++;  

  if(outputStreamIndex == 0)
  {
    prevMicrosTime = micros();
    inputFirstState = digitalRead(INPUT_PIN);
  }
  else  
  { 
    currentMicrosTime = micros();
    int iRsl = (currentMicrosTime - prevMicrosTime)/10;
    if (iRsl > 400 && iRsl < 600)
      outputStreamTime[outputStreamIndex-1] = TEMP_5000_US;
    else if (iRsl >= 600)
      outputStreamTime[outputStreamIndex-1] = TEMP_10000_US;
    else
      outputStreamTime[outputStreamIndex-1] = (unsigned char)iRsl;   
    
    prevMicrosTime = currentMicrosTime;
  }

  outputStreamIndex++;

  toggleLed();
}

/////////////////////////////////////////
/////////////////////////////////////////

void blinkingLed()
{
  toggleLed();
  delay(50);               // wait for a 0.05 second
  toggleLed();
  delay(50);               // wait for a 0.05 second
}

/////////////////////////////////////////

void readBufferASCII()
{
  if(outputStreamIndex == 0)
    return;

  byte inputFirstStateTemp (inputFirstState);

  for(int i = 0; i < outputStreamIndex-1 ; i++)
  {
    Serial.print(inputFirstStateTemp);
    Serial.print(",");
    Serial.print(outputStreamTime[i]);
    Serial.print("\n");

    inputFirstStateTemp = !inputFirstStateTemp;
  }

  Serial.print(inputFirstStateTemp);
  Serial.print(",");
  Serial.print(END_MSG);
  Serial.print("\n");
}

/////////////////////////////////////////

void readBuffer()
{

  if(outputStreamIndex == 0)
    return;

  byte inputFirstStateTemp (inputFirstState);
  
  for(int i = 0; i < outputStreamIndex-1 ; i++)
  {
    Serial.print("P: ");
    Serial.print(i);
    Serial.print(" - V: ");
    Serial.print(inputFirstStateTemp);
    Serial.print(" - T: ");
    Serial.print(outputStreamTime[i]);
    Serial.print("\n");

    inputFirstStateTemp = !inputFirstStateTemp;
  }

  Serial.print(" - Iterations: ");
  Serial.print(iIterations);
  Serial.print("\n");

  Serial.print("P: ");
  Serial.print(outputStreamIndex-1);
  Serial.print(" - V: ");
  Serial.print(inputFirstStateTemp);
  Serial.print(" - T: ");
  Serial.print(END_MSG);
  Serial.print("\n");
  
}

/////////////////////////////////////////

void runLogger()
{
  for(int i = 0; i < MAX_BUFFER_SIZE ; i++)
    outputStreamTime[i] = 0;

  inputFirstState = LOW;
  outputStreamIndex = 0;
  iIterations = 0;

  attachInterrupt(0, int0Func, CHANGE );
}

/////////////////////////////////////////

void prompt()
{
  /*Serial.print("Print: 'a' to attach interrupt, 'v' verbose output or 'l' ascii output ---");
  Serial.println(" ");
  */
}

/////////////////////////////////////////

void txSeq()
{
  if(outputStreamIndex == 0)
    return;

  digitalWrite(OUTPUT_PIN, inputFirstState);
  digitalWrite(OUTPUT_PIN_DEBUG, digitalRead(OUTPUT_PIN));

  for(int i = 0; i < outputStreamIndex ; i++)
  {
    if(outputStreamTime[i] == TEMP_10000_US)
    {
      delayMicroseconds(10000);
    }
    else if (outputStreamTime[i] == TEMP_5000_US)
    {
      delayMicroseconds(5000);
    }
    else
    {
      delayMicroseconds(((int)outputStreamTime[i])*10);
    }
    digitalWrite(OUTPUT_PIN, !digitalRead(OUTPUT_PIN));
    digitalWrite(OUTPUT_PIN_DEBUG, digitalRead(OUTPUT_PIN));
  }

  digitalWrite(OUTPUT_PIN, LOW);
  digitalWrite(OUTPUT_PIN_DEBUG, digitalRead(OUTPUT_PIN));
}

/////////////////////////////////////////

void setup() 
{
  pinMode(LED_PIN, OUTPUT);

  pinMode(INPUT_PIN, INPUT);
  digitalWrite(INPUT_PIN,HIGH);
  //pinMode(2, INPUT_PULLUP);

  pinMode(OUTPUT_PIN, OUTPUT);
  digitalWrite(OUTPUT_PIN,LOW);
  pinMode(OUTPUT_PIN_DEBUG, OUTPUT);
  digitalWrite(OUTPUT_PIN_DEBUG,LOW);

  Serial.begin(57600);
  prompt();

  for(byte i = 0; i< 3 ;i++)
    blinkingLed();
}

/////////////////////////////////////////

void loop() 
{
  //blinkingLed();

  if(Serial.available() > 0)
  {
    detachInterrupt(0);
    switch (Serial.read()) 
    {
        case 'a':runLogger();                                         break;
        case 'v':readBuffer();                                        break;
        case 'l':readBufferASCII();                                   break;
        case 't':txSeq();                                             break;
        default: detachInterrupt(0);                                  break;
    }
  }
}

/////////////////////////////////////////
/////////////////////////////////////////
