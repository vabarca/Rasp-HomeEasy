
/////////////////////////////////////////
/////////////////////////////////////////

/*
  HomeEasyTx software
  by Vicente Abarca
*/

/////////////////////////////////////////
/////////////////////////////////////////

#define MAX_BUFFER_SIZE   1405
#define INPUT_PIN         2
#define OUTPUT_PIN        3
//#define OUTPUT_PIN_DEBUG  4
#define LED_PIN           13

#define END_MSG           255
#define TEMP_10000_US     254
#define TEMP_5000_US      253

unsigned char ouputFirstState = 0;
unsigned char outputStreamTime[MAX_BUFFER_SIZE];
unsigned int outputStreamTimeLenght = 0;

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
/////////////////////////////////////////

void blinkingLed()
{
  toggleLed();
  delay(50);               // wait for a 0.05 second
  toggleLed();
  delay(50);               // wait for a 0.05 second
}

/////////////////////////////////////////

void txSeq()
{
  if(outputStreamTimeLenght == 0)
    return;

  digitalWrite(OUTPUT_PIN, ouputFirstState);
  digitalWrite(LED_PIN, digitalRead(OUTPUT_PIN));

  for(int i = 0; i < outputStreamTimeLenght ; i++)
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
    digitalWrite(LED_PIN, digitalRead(OUTPUT_PIN));
  }

  digitalWrite(OUTPUT_PIN, LOW);
  digitalWrite(LED_PIN, digitalRead(OUTPUT_PIN));
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
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN,LOW);

  Serial.begin(57600);

  for(byte i = 0; i< 4 ;i++)
    blinkingLed();
}

/////////////////////////////////////////

void loop() 
{
  static unsigned int stcbyPayload_counter(0);
  static byte stcbyHOST_step(0);

  byte data;  
  while (Serial.available() > 0)  // Process bytes received
  {
    data = Serial.read();
    switch(stcbyHOST_step)    //Normally we start from zero. This is a state machine
    {
      case 0: 
        if(data == 'W') 
        {
          stcbyPayload_counter=0;
          stcbyHOST_step++; //First byte of data packet header is correct, so jump to the next step
        }
        break; 
      case 1: 
        if(data == 'H') stcbyHOST_step++; //Second byte of data packet header is correct
        else stcbyHOST_step=0;    //Second byte is not correct so restart to step zero and try again.  
        break;
      case 2: 
        if(data == 'D') stcbyHOST_step++; //Third byte of data packet header is correct
        else stcbyHOST_step=0;    //Third byte is not correct so restart to step zero and try again.
        break;
      case 3: 
        if(data == 'O') stcbyHOST_step++; //Fourth byte of data packet header is correct, Header complete
        else stcbyHOST_step=0;    //Fourth byte is not correct so restart to step zero and try again.
        break;
      case 4:
        outputStreamTimeLenght = (int)data;
        outputStreamTimeLenght = ( outputStreamTimeLenght << 8) & 0xFF00; //primer byte del data length (no incluye el byte de estado de inico)
        stcbyHOST_step++;
        break;
      case 5:
        outputStreamTimeLenght += (int)data; 
        stcbyHOST_step++;
        if (outputStreamTimeLenght > MAX_BUFFER_SIZE)
          stcbyHOST_step=0; //Bad data, so restart to step zero and try again.     
        break;
      case 6:
        //El primer dato es el estado de inicio
        ouputFirstState = data;
        stcbyHOST_step++;
        break;      
      case 7: 
        // Payload data read...
        // We stay in this state until we reach the payload_length
        outputStreamTime[stcbyPayload_counter++] = data;
        if (stcbyPayload_counter >= outputStreamTimeLenght) 
          stcbyHOST_step++; 
        break;
      case 8:
        if(data == 'M') stcbyHOST_step++; 
        else stcbyHOST_step=0;        
        break; 
      case 9:
        if(data == 'S') stcbyHOST_step++;
        else stcbyHOST_step=0;
        break;
      case 10:
        if(data == 'L') stcbyHOST_step++;
        else stcbyHOST_step=0;
        break;
      case 11:
        if(data == 'P') 
        {
          txSeq();
          blinkingLed();
          delay(50);
          blinkingLed();
          delay(50);
          Serial.print("ok");
        }

      default:
        stcbyHOST_step=0;         //reiniciamos la maquina de estados;
    }
  }// while (_serialPort->available() > 0)
}

/////////////////////////////////////////
/////////////////////////////////////////
