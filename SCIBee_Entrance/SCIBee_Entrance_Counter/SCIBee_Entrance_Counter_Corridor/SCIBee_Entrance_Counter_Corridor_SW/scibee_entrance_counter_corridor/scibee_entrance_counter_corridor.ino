#include <Wire.h>

// --- I2C SLAVE ADDRESS CONFIGURATION ---
// RANGE FOR 31 BOARDS: 40 to 70 
const int I2C_ADDRESS = 68; 

// --- HARDWARE MAPPING (ATtiny404 Physical Pins) ---
const int LED_PINS[] = {PIN_PA1, PIN_PA2, PIN_PB2, PIN_PB3};
const int NUM_LEDS = 4;
const int IR_PINS[] = {PIN_PA4, PIN_PA5, PIN_PA6, PIN_PA7};
const int NUM_IRS = 4;

// --- I2C Command Bases ---
const byte CMD_LED_ON_BASE = 0x10;  
const byte CMD_LED_OFF_BASE = 0x20; 
const byte CMD_IR_READ_BASE = 0x30; 

/*
 * I2C COMMAND TABLE (12 Commands Total)
 * Master sends 1 byte command to the slave.
 * ----------------------------------------------------------------------
 * | Function | Target | Pin | Command (HEX) | Command (DEC) |
 * ----------------------------------------------------------------------
 * | LED ON   | D1     |  PIN_PA1 | 0x10          | 16            |
 * | LED ON   | D2     |  PIN_PA2 | 0x11          | 17            |
 * | LED ON   | D3     |  PIN_PB2  | 0x12          | 18            |
 * | LED ON   | D4     |  PIN_PB3  | 0x13          | 19            |
 * ----------------------------------------------------------------------
 * | LED OFF  | D1     |  PIN_PA1 | 0x20          | 32            |
 * | LED OFF  | D2     |  PIN_PA2 | 0x21          | 33            |
 * | LED OFF  | D3     |  PIN_PB2  | 0x22          | 34            |
 * | LED OFF  | D4     |  PIN_PB3  | 0x23          | 35            |
 * ----------------------------------------------------------------------
 * | IR READ* | Q0     |  PIN_PA4  | 0x30          | 48            |
 * | IR READ* | Q1     |  PIN_PA5  | 0x31          | 49            |
 * | IR READ* | Q2     |  PIN_PA6  | 0x32          | 50            |
 * | IR READ* | Q3     |  PIN_PA7  | 0x33          | 51            |
 * ----------------------------------------------------------------------
 * *Note: IR READ commands only *prepare* the slave. The Master must then
 * immediately request 1 byte (0-255) to get the scaled analog value.
 */

// Volatile state variable to hold the requested sensor index (0-3) for the read event.
volatile int currentReadChannel = -1; 

// ====================================================================
// SETUP
// ====================================================================

void setup() {
  // Initialize LED pins as outputs (default LOW) and IR pins as analog inputs.
  for (int i = 0; i < NUM_LEDS; i++) {
    pinMode(LED_PINS[i], OUTPUT);
    digitalWrite(LED_PINS[i], LOW);
  }
  for (int i = 0; i < NUM_IRS; i++) {
    pinMode(IR_PINS[i], INPUT);
  }

  // Initialize I2C/TWI as a slave and register handlers.
  Wire.begin(I2C_ADDRESS);
  Wire.onReceive(receiveEvent);
  Wire.onRequest(requestEvent);
}

// ====================================================================
// I2C Event Handlers
// ====================================================================

void receiveEvent(int howMany) {
  if (howMany > 0) {
    byte command = Wire.read();
    int index = -1; 

    // LED ON Commands (0x10-0x13)
    if (command >= CMD_LED_ON_BASE && command < (CMD_LED_ON_BASE + NUM_LEDS)) {
      index = command - CMD_LED_ON_BASE;
      if (index >= 0 && index < NUM_LEDS) {
        digitalWrite(LED_PINS[index], HIGH);
      }
    }
    // LED OFF Commands (0x20-0x23)
    else if (command >= CMD_LED_OFF_BASE && command < (CMD_LED_OFF_BASE + NUM_LEDS)) {
      index = command - CMD_LED_OFF_BASE;
      if (index >= 0 && index < NUM_LEDS) {
        digitalWrite(LED_PINS[index], LOW);
      }
    }
    // IR Read Preparation Commands (0x30-0x33)
    else if (command >= CMD_IR_READ_BASE && command < (CMD_IR_READ_BASE + NUM_IRS)) {
      index = command - CMD_IR_READ_BASE;
      if (index >= 0 && index < NUM_IRS) {
        currentReadChannel = index; 
      }
    }
  }

  // Clear buffer if more bytes were sent than expected (safety check).
  while(Wire.available()) { 
    Wire.read();
  }
}

void requestEvent() {
  if (currentReadChannel >= 0 && currentReadChannel < NUM_IRS) {
    // Read 10-bit value (0-1023)
    int analogValue = analogRead(IR_PINS[currentReadChannel]);
    
    // Scale to 8-bit (0-255) by dividing by 4 (shifting right by 2)
    byte responseByte = (byte)(analogValue >> 2); 

    Wire.write(responseByte);
    
    // Reset the channel marker after successful read.
    currentReadChannel = -1; 
  } else {
    // Return 0x00 if no sensor was prepared for reading.
    Wire.write(0x00);
  }
}

void loop() {
}
