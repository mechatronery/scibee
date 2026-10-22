/*

*/
#ifndef SCIBee_h
#define SCIBee_h

#include <Arduino.h>
#include <Wire.h>
// pin mapping
#define LEDr 22
#define LEDy 26
#define LEDg 27
#define MOT_AF 13
#define MOT_AR 12
#define MOT_BF 11
#define MOT_BR 10
#define LCpwrEN 8
#define pumpPIN 14
#define I2C_A0 4
#define I2C_A1 5
#define ANin A2
#define Dio 19

// value definition
#define RXbytes 2	// number of bytes in command/request from controller (master)
	/*
	===== byte 0: command
	0-9		: ----- system commands
		0-/
		1-reset

		4-red LED ON
		5-red LED OFF
		6-yellow LED ON
		7-yellow LED OFF
		8-green LED ON
		9-green LED OFF
	10-19	: ----- H-bridge drive
		10-brake OFF (drive disable) all
		11-brake A ON
		12-drive A forward
		13-drive A in reverse
		14-brake B ON
		15-drive B forward
		16-drive B in reverse
	20-29	: ----- pump drive controll
		20-disable pump
		21-turn pump ON
	30-39	: ----- Load cell
		30-disable Load cell power
		31-enable Load cell power & set channel to 1
		32-enable Load cell power & set channel to 2
		33-read value of load cell
	40-49	: ----- RTC
		40-read date (return: year in range of 2000-2255, month in range 1-12, day in month 1-31)
		41-read time (return: hour in range 0-23, minute in range 0-59, second in range 0-59)
		44-transfer year value
		45-transfer month value
		46-transfer day value
		47-transfer hour value
		48-transfer minute value
		49-set RTC (set RTC with values set by commands 46-48)
	50-59	: ----- qwiic enviromental sensor
		50-read temperature in °C
		51-read relative humidity in %
		52-read pressure in Pa
		53-read altitude in m
	60-69	: ----- qwiic energy meter
		60-read power in mW
		61-read energy in J
		62-read bus voltage in mV
		63-read current in mA
		64-read shunt voltage in mV
		68-read charge in C
		69-read IC temperature in °C
	70-255	: ----- un-alocated
	===== byte 1: value
	8 bit value relating to coresponding command (PWM value for H-bridge controll, date & tiem value for RTC,...)
	*/
#define TXbytes 3	// number of bytes in response to request from controller
	/*
		8 bit value
	*/



class SCIBee
{
	private:
		
	public:
		uint8_t init(uint8_t addr);
		void PUMP_mode(String mode);
		void LEDstate(char led, bool state, int Delay);
		void LoadCell_power(String mode);
		void Bridge_brake(char bridge, String state);
		void Bridge_state(char bridge, int speed);
};


#endif
