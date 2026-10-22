#include <scibee_base_control_board_library.h>
#include <SparkFun_Qwiic_Scale_NAU7802_Arduino_Library.h>
#include "SparkFunBME280.h"
#include <RTC_PCF85063.h>
#include <Adafruit_INA228.h>


// ===== Device Constructors
SCIBee SCIBee;
uint8_t adress=0;            // setting adress to 0 will automatically set-up the adress based on logic state on pins I2C_A0 & I2C_A1. Setting anything else but 0, will set the adress of the device to set value.
NAU7802 Scale;
BME280 Enviromental;
RTC_PCF85063 RTC;
  uint8_t RTCyear,RTCmonth,RTCday,RTChour,RTCminute,RTCsecond;
Adafruit_INA228 EnergyMeter = Adafruit_INA228();

// ===== Variables
int i=0;                                      // multipurpuse incrementing variable
int32_t currentReading=0, currentReading_=0;  // value storing variable and its temporary counterpart
byte recieve[RXbytes];                        // I2C receive buffer
byte transmit[TXbytes];                       // I2C transmit buffer
bool readCycle=false;                         // loop cycle condition flag
bool transmitDONE=false;                      // flag set if I2C transmit happened (for runing debug/monitoring code)

// ===== Device flags (to know if devices are present or not)
bool scale_F, rtc_F, envS_F, enrgM_F;


// ===== Setup
void setup()
{
  Serial.begin(9600);
  delay(5000);

  // ----- Board initialization
  uint8_t log1=SCIBee.init(adress);
  if (log1 < 255)
  {
      Serial.print("Board initialization unsecesfull. Error log: ");
      Serial.print(log1);
      Serial.println(". Freezing...");
      while(1);
  }
  else
  {
    Serial.print("Board initialization sucesfull.");
    
      uint8_t adress_;
		if(adress == 0)
		{
      adress_=100;
			if(digitalRead(I2C_A0)) adress_+=1;
			if(digitalRead(I2C_A1)) adress_+=2;
		}
		else adress_=adress;
    Serial.print(" Board adress | ");
    Serial.print(adress_);
    Serial.println(" |.");
  }

  SCIBee.LEDstate('Y', HIGH, 0);   // initialization in progres indicator

  // ----- Paripheral comunication setup
  Wire.onReceive(I2C_RxHandler);
  Wire.onRequest(I2C_TxHandler);

  // ----- Scale initialization
  if (Scale.begin(Wire1, false) == false)
  {
      Serial.println("Scale not detected.");
      scale_F=false;
  }
  else
  {
      uint8_t log2=1;
    Serial.print("Scale detected, setting up... ");

    if(Scale.reset()) log2+=128;
    if(Scale.powerUp()) log2+=64;
    if(Scale.setGain(NAU7802_GAIN_128)) log2+=32;  //Set gain to 128
    if(Scale.setSampleRate(NAU7802_SPS_10)) log2+=16; //Set samples per second to 10
    //Turn off CLK_CHP. From 9.1 power on sequencing.
    uint8_t adc = Scale.getRegister(NAU7802_ADC);
    adc |= 0x30;
    if(Scale.setRegister(NAU7802_ADC, adc)) log2+=8;
    if(Scale.clearBit(NAU7802_PGA_LDOMODE, NAU7802_PGA)) log2+=4; //Ensure LDOMODE bit is clear - improved accuracy and higher DC gain, with ESR < 1 ohm
    delay(250); //Wait for LDO to stabilize - takes about 200ms
    Scale.getWeight(true, 10); //Flush
    if(Scale.calibrateAFE()) log2+=2; //Re-cal analog front end when we change gain, sample rate, or channel

    if(log2 < 255) while(1)
    {
        SCIBee.LEDstate('R', HIGH, 0);   // setup error indicator
      Serial.print("Scale setup unsucesfull. Error log: ");
      Serial.print(log2);
      Serial.println(".");
      delay(1000);
    }
    else
    {
      Serial.println("Scale setup complete.");
      scale_F=true;
    }
  }

  // ----- RTC initialization
  RTC.begin(Wire1);
    RTC.cap_sel(CAP_SEL_12_5PF);    // CAP_SEL bit setting 12.5pF
    RTC.calibratBySeconds(0, -0.000041);
    // checking if device is present: stopping timer, reading timer value#1, reading timer value#2, starting timer and reading timer value#3. value#1=value#2 && value#3 > value#1
    RTC.getTime();
    uint8_t time1=RTC.second;
    delay(1500);
    RTC.getTime();
    uint8_t time2=RTC.second;
    if((time2 > time1) && (time2 < (time1+3)))
    {
      Serial.println("RTC detected.");
      rtc_F=true;
    }
    else
    {
      Serial.println("No RTC detected.");
      rtc_F=false;
    }

  // ----- Enviromental sensor on qwiic
  if (Enviromental.beginI2C(Wire1) == false)
  {
    Serial.println("No enviromental sensor detected.");
    envS_F=false;
  }
  else
  {
    Serial.println("Enviromental sensor detected.");
    envS_F=true;
  }

  // ----- Power sensor on qwiic
  if (EnergyMeter.begin(INA228_I2CADDR_DEFAULT,&Wire1,false) == false)
  {
    Serial.println("No Energy meter detected.");
    enrgM_F=false;
  }
  else
  {
    Serial.print("Energy meter detected. Setting up... ");
    EnergyMeter.setShunt(0.015, 10.0);
    EnergyMeter.setAveragingCount(INA228_COUNT_16); // 1,4,16,64,128,256,512,1024
      Serial.print("| Averaging counts: ");
      Serial.print(EnergyMeter.getAveragingCount());
    EnergyMeter.setVoltageConversionTime(INA228_TIME_150_us);
      Serial.print(". Voltage conversion time: ");
      Serial.print(EnergyMeter.getVoltageConversionTime());
    EnergyMeter.setCurrentConversionTime(INA228_TIME_280_us);
      Serial.print(". Current conversion time: ");
      Serial.print(EnergyMeter.getCurrentConversionTime());
      Serial.println(".");
    enrgM_F=true;
  }


  // initialization complete semafor sequence
  SCIBee.LEDstate('Y', LOW, 0);
  SCIBee.LEDstate('G', LOW, 0);
  SCIBee.LEDstate('R', HIGH, 500);
  SCIBee.LEDstate('Y', HIGH, 500);
  SCIBee.LEDstate('G', HIGH, 1000);
  SCIBee.LEDstate('Y', LOW, 0);
  SCIBee.LEDstate('R', LOW, 200);
  SCIBee.LEDstate('G', LOW, 200);
  SCIBee.LEDstate('G', HIGH, 200);
  SCIBee.LEDstate('G', LOW, 0);
}

// ===== Main
void loop()
{
  if(recieve[0] != 0)
  {
    Serial.print("Received from controller; ");
    Serial.print(recieve[0]);
    Serial.print(":");
    Serial.println(recieve[1]);

    switch (recieve[0])
    {
      case 1:           // system reset
      {

        break;
      }
      case 4:          // red LED ON
      {
          SCIBee.LEDstate('R',HIGH,0);
        break;
      }
      case 5:          // red LED OFF
      {
          SCIBee.LEDstate('r',LOW,0);
        break;
      }
      case 6:          // yellow LED ON
      {
          SCIBee.LEDstate('Y',HIGH,0);
        break;
      }
      case 7:          // yellow LED OFF
      {
          SCIBee.LEDstate('y',LOW,0);
        break;
      }
      case 8:          // green LED ON
      {
          SCIBee.LEDstate('G',HIGH,0);
        break;
      }
      case 9:          // green LED OFF
      {
          SCIBee.LEDstate('G',LOW,0);
        break;
      }
      case 10:          // H-bridge brake OFF
      {
          commandExecution_start();

        SCIBee.Bridge_brake('A',"OFF");
        SCIBee.Bridge_brake('B',"OFF");
        
          commandExecution_complete();
        break;
      }
      case 11:          // H-bridge A brake ON
      {
          commandExecution_start();

        SCIBee.Bridge_brake('A',"ON");
        
          commandExecution_complete();
        break;
      }
      case 12:          // H-bridge A drive forward
      {
          commandExecution_start();

        SCIBee.Bridge_state('A', recieve[1]);
        
          commandExecution_complete();
        break;
      }
      case 13:          // H-bridge A drive reverse
      {
          commandExecution_start();

        SCIBee.Bridge_state('A', -recieve[1]);
        
          commandExecution_complete();
        break;
      }
      case 14:          // H-bridge B brake ON
      {
          commandExecution_start();

        SCIBee.Bridge_brake('B',"ON");
        
          commandExecution_complete();
        break;
      }
      case 15:          // H-bridge B drive forward
      {
          commandExecution_start();

        SCIBee.Bridge_state('B', recieve[1]);
        
          commandExecution_complete();
        break;
      }
      case 16:          // H-bridge B drive reverse
      {
          commandExecution_start();

        SCIBee.Bridge_state('B', -recieve[1]);
        
          commandExecution_complete();
        break;
      }
      case 20:          // piezo pump stop
      {
          commandExecution_start();

        SCIBee.PUMP_mode("STOP");
        
          commandExecution_complete();
        break;
      }
      case 21:          // piezo pump run
      {
          commandExecution_start();

        SCIBee.PUMP_mode("RUN");
        
          commandExecution_complete();
        break;
      }
      case 30:          // load cell power OFF
      {
          commandExecution_start();

        SCIBee.LoadCell_power("OFF");
        
          commandExecution_complete();
        break;
      }
      case 31:          // enable Load cell power & set channel to 1
      {
        if(scale_F)
        {
              commandExecution_start();

            SCIBee.LoadCell_power("ON");
              //Serial.println("Load cell power ON.");
            delay(1000);
            Scale.setChannel(NAU7802_CHANNEL_1);
            delay(100);
            Scale.calibrateAFE(); //Re-calibrate analog front end when we change gain, sample rate, or channel
            
              commandExecution_complete();
        }
        else noDevice_error();
        break;
      }
      case 32:          // enable Load cell power & set channel to 2
      {
        if(scale_F)
        {
            commandExecution_start();

          SCIBee.LoadCell_power("ON");
            //Serial.println("Load cell power ON.");
          delay(1000);
          Scale.setChannel(NAU7802_CHANNEL_2);
          delay(100);
          Scale.calibrateAFE(); //Re-calibrate analog front end when we change gain, sample rate, or channel
          
            commandExecution_complete();
          }
          else noDevice_error();
        break;
      }
      case 33:          // read value of load cell
      {
        if(scale_F)
        {
            commandExecution_start();

            readCycle=true;
          while(readCycle)
          {
            if(Scale.available() == true)
            {
              currentReading += Scale.getReading();
              i++;
              
              packageTo3Bytes(abs(currentReading)/i); // execute 24bit averaging and value segmenting for transmision
            }
          }
          
            commandExecution_complete();
        }
        else noDevice_error();
        break;
      }
      case 40:          // read RTC date
      {
        if(rtc_F)
        {
          commandExecution_start();

          RTC.getTime();
            transmit[0]=RTC.year;
            transmit[1]=RTC.month;
            transmit[2]=RTC.dayOfMonth;
        
          commandExecution_complete();
        }
        else noDevice_error();
        break;
      }
      case 41:          // read RTC time
      {
        if(rtc_F)
        {
            commandExecution_start();

          RTC.getTime();
            transmit[0]=RTC.hour;
            transmit[1]=RTC.minute;
            transmit[2]=RTC.second;
          
            commandExecution_complete();
        }
        else noDevice_error();
        break;
      }
      case 44:          // set RTC year
      {
        if(rtc_F)
        {
            commandExecution_start();

          RTCyear=recieve[1];
          
            commandExecution_complete();
        }
        else noDevice_error();
        break;
      }
      case 45:          // set RTC month
      {
        if(rtc_F)
        {
            commandExecution_start();

          RTCmonth=recieve[1];
          
            commandExecution_complete();
        }
        else noDevice_error();
        break;
      }
      case 46:          // set RTC day
      {
        if(rtc_F)
        {
            commandExecution_start();

          RTCday=recieve[1];
          
            commandExecution_complete();
        }
        else noDevice_error();
        break;
      }
      case 47:          // set RTC hour
      {
        if(rtc_F)
        {
            commandExecution_start();

          RTChour=recieve[1];
          
            commandExecution_complete();
        }
        else noDevice_error();
        break;
      }
      case 48:          // set RTC minute
      {
        if(rtc_F)
        {
            commandExecution_start();

          RTCminute=recieve[1];
          
            commandExecution_complete();
        }
        else noDevice_error();
        break;
      }
      case 49:          // set RTC time
      {
        if(rtc_F)
        {
            commandExecution_start();

            RTC.stopClock();
          RTC.fillByYMD(2000+RTCyear,RTCmonth,RTCday);
          RTC.fillByHMS(RTChour,RTCminute,0);
          RTC.setTime();          //write time to the RTC chip
            RTC.startClock();

            commandExecution_complete();
        }
        else noDevice_error();
        break;
      }
      case 50:          // read temperature in °C/10 offset by +128
      {
        if(envS_F)
        {
            commandExecution_start();

          packageTo3Bytes(int(Enviromental.readTempC()*10+1280));
          
            commandExecution_complete();
        }
        else noDevice_error();
        break;
      }
      case 51:          // read relative humidity in %
      {
        if(envS_F)
        {
            commandExecution_start();

          packageTo3Bytes(int(Enviromental.readFloatHumidity()));
          
            commandExecution_complete();
        }
        else noDevice_error();
        break;
      }
      case 52:          // read pressure in Pa
      {
        if(envS_F)
        {
            commandExecution_start();

          packageTo3Bytes(int(Enviromental.readFloatPressure()));
          
            commandExecution_complete();
        }
        else noDevice_error();
        break;
      }
      case 53:          // read altitude in m
      {
        if(envS_F)
        {
            commandExecution_start();

          packageTo3Bytes(int(Enviromental.readFloatAltitudeMeters()));
          
            commandExecution_complete();
        }
        else noDevice_error();
        break;
      }
      case 60:          // read power in mW
      {
        if(enrgM_F)
        {
            commandExecution_start();

          packageTo3Bytes(int(EnergyMeter.getPower_mW()));
          
            commandExecution_complete();
        }
        else noDevice_error();
        break;
      }
      case 61:          // read energy in J
      {
        if(enrgM_F)
        {
            commandExecution_start();

          packageTo3Bytes(int(EnergyMeter.readEnergy()));
          
            commandExecution_complete();
        }
        else noDevice_error();
        break;
      }
      case 62:          // read bus voltage in mV
      {
        if(enrgM_F)
        {
            commandExecution_start();

          packageTo3Bytes(int(EnergyMeter.getBusVoltage_V()*1000));
          
            commandExecution_complete();
        }
        else noDevice_error();
        break;
      }
      case 63:          // read current in 1/10 of mA
      {
        if(enrgM_F)
        {
            commandExecution_start();

          packageTo3Bytes(int(EnergyMeter.getCurrent_mA()*10));
          
            commandExecution_complete();
        }
        else noDevice_error();
        break;
      }
      case 64:          // read shunt voltage in 1/100 of mV
      {
        if(enrgM_F)
        {
            commandExecution_start();

          packageTo3Bytes(int(EnergyMeter.getShuntVoltage_mV()*100));
          
            commandExecution_complete();
        }
        else noDevice_error();
        break;
      }
      case 68:          // read charge in C
      {
        if(enrgM_F)
        {
            commandExecution_start();

          packageTo3Bytes(int(EnergyMeter.readCharge()));
          
            commandExecution_complete();
        }
        else noDevice_error();
        break;
      }
      case 69:          // read IC temperature in °C
      {
        if(enrgM_F)
        {
            commandExecution_start();

          packageTo3Bytes(int(EnergyMeter.readDieTemp()));
          
            commandExecution_complete();
        }
        else noDevice_error();
        break;
      }
      default:
      {
        noDevice_error();
        break;
      }
    }

    currentReading=0;
    currentReading_=0;
    i=0;
    recieve[0]=0;   // reset command ID to indicate command has been executed
  }

  if(transmitDONE)
  {
    Serial.print("Sent: ");
    Serial.print(transmit[0]);
    Serial.print(":");
    Serial.print(transmit[1]);
    Serial.print(":");
    Serial.println(transmit[2]);

    transmitDONE=false;
  }
}


// ================================================================================================================

// ===== Functions
void packageTo3Bytes(int value)
{
  transmit[0]=byte(value);
  transmit[1]=byte(value >>8);
  transmit[2]=byte(value >>16);
}

void I2C_RxHandler(int numBytes)
{
  I2Chandeler_start();
    int k=0;
  while(k<RXbytes)
  {
    while(Wire.available())
    {
      recieve[k] = Wire.read(); // Read Any Received Data
      k++;
    }
  }
  I2Chandeler_complete();
}

void I2C_TxHandler(void)
{
  I2Chandeler_start();
    readCycle=false;
  
  Wire.write(transmit,TXbytes);
    transmitDONE=true;
  
  I2Chandeler_complete();
}

void I2Chandeler_start()
{
  SCIBee.LEDstate('Y',HIGH,0);
}
void I2Chandeler_complete()
{
  SCIBee.LEDstate('Y',LOW,0);
}

void noDevice_error()
{
    transmit[0]=0xff;
    transmit[1]=0xff;
    transmit[2]=0xff;
  SCIBee.LEDstate('R',HIGH,2000);
  SCIBee.LEDstate('R',LOW,0);
}

void commandExecution_start()
{
  SCIBee.LEDstate('G',HIGH,0);
}
void commandExecution_complete()
{
  SCIBee.LEDstate('G',LOW,0);
}
