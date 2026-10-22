/*

*/
#include "scibee_base_control_board_library.h"


uint8_t SCIBee::init(uint8_t addr)
{
		// initialization log value. Each bit represents individual initialization segments (1=sucesfull, 0=unsucesfull).
		uint8_t init_log=1+2;

	// serial initialize
	pinMode(I2C_A0, INPUT);
	pinMode(I2C_A1, INPUT);

		Wire.setSDA(20);
		Wire.setSCL(21);
		uint8_t address=100;
		if(addr == 0)
		{
			if(digitalRead(I2C_A0)) address+=1;
			if(digitalRead(I2C_A1)) address+=2;
		}
		else address=addr;
	Wire.begin(address);
			init_log+=128;	// I2C0 initialized

		Wire1.setSDA(2);
		Wire1.setSCL(3);
	Wire1.begin();
			init_log+=64;	// I2C1 initialized
	
	// LED initialize
	pinMode(LEDr, OUTPUT);
		digitalWrite(LEDr,LOW);
	pinMode(LEDy, OUTPUT);
		digitalWrite(LEDy,LOW);
	pinMode(LEDg, OUTPUT);
		digitalWrite(LEDg,LOW);
			init_log+=32;	// LED indicators initialized
	
	// piezo pump initialize
	pinMode(pumpPIN, OUTPUT);
		PUMP_mode("STOP");
			init_log+=16;	// piezo pump initialized
	
	// load cell initialize
	pinMode(LCpwrEN, OUTPUT);
		digitalWrite(LCpwrEN,LOW);
			init_log+=8;	// Load cell power control initialized
	
	// H-bridge initialize
	pinMode(MOT_AF, OUTPUT);
		digitalWrite(MOT_AF,LOW);
	pinMode(MOT_AR, OUTPUT);
		digitalWrite(MOT_AR,LOW);
	pinMode(MOT_BF, OUTPUT);
		digitalWrite(MOT_BF,LOW);
	pinMode(MOT_BR, OUTPUT);
		digitalWrite(MOT_BR,LOW);
			init_log+=4;	// H-bridge drives initialized
	
	return init_log;
}

// ***** ***** Piezo pump
void SCIBee::PUMP_mode(String mode)
{
  if(mode == "RUN") digitalWrite(pumpPIN,HIGH);
  else digitalWrite(pumpPIN,LOW);
}

// ***** ***** LEDs
void SCIBee::LEDstate(char led, bool state, int Delay)
{
	switch (led)
	{
		case 'R': case 'r':
		{
			digitalWrite(LEDr,state);
			break;
		}
		case 'Y': case 'y':
		{
			digitalWrite(LEDy,state);
			break;
		}
		case 'G': case 'g':
		{
			digitalWrite(LEDg,state);
			break;
		}
		default:
			break;
	}
	delay(Delay);
}

// ***** ***** Load cells
void SCIBee::LoadCell_power(String mode)
{
  if(mode == "ON") digitalWrite(LCpwrEN,HIGH);
  else digitalWrite(LCpwrEN,LOW);
}

// ***** ***** H-bridges
void SCIBee::Bridge_brake(char bridge, String state)
{
	switch (bridge)
	{
		case 'A':
			if(state == "ON")
			{
				digitalWrite(MOT_AF,HIGH);
				digitalWrite(MOT_AR,HIGH);
			}
			else
			{
				digitalWrite(MOT_AF,LOW);
				digitalWrite(MOT_AR,LOW);
			}
			break;
			
		case 'B':
			if(state == "ON")
			{
				digitalWrite(MOT_BF,HIGH);
				digitalWrite(MOT_BR,HIGH);
			}
			else
			{
				digitalWrite(MOT_BF,LOW);
				digitalWrite(MOT_BR,LOW);
			}
			break;
		default:
			break;
	}
}

void SCIBee::Bridge_state(char bridge, int speed)
{
	switch (bridge)
	{
		case 'A':
			if(speed > 0)
			{
				analogWrite(MOT_AF,abs(speed));
				digitalWrite(MOT_AR,LOW);
			}
			else
			{
				analogWrite(MOT_AR,abs(speed));
				digitalWrite(MOT_AF,LOW);
			}
			break;
			
		case 'B':
			if(speed > 0)
			{
				analogWrite(MOT_BF,abs(speed));
				digitalWrite(MOT_BR,LOW);
			}
			else
			{
				analogWrite(MOT_BR,abs(speed));
				digitalWrite(MOT_BF,LOW);
			}
			break;
		default:
			break;
	}
}
