//-----Beehive-----------------
#define BEEHIVE_ID "C1"
#define BEEHIVE_IP 101
#define BEEHIVE_SUBNET 3
#define OTA_ENABLE 0
//-----------------------------

#include <WiFi.h>
#if OTA_ENABLE
#include <ArduinoOTA.h>
#endif
#include <AsyncTCP.h>
#include <ESPAsyncWebServer.h>
#include <LittleFS.h>
#include <ArduinoJson.h>
#include <time.h>
#include <SdFat.h>
#include <SPI.h>
#include <Wire.h>

int loop_num = 0;

//-----WIFI-----------------
const char *ssid = "SCIBee_C";
const char *password = "XXXXXXXX";
const uint16_t server_port = 80;
IPAddress local_ip(192, 168, BEEHIVE_SUBNET, BEEHIVE_IP);
IPAddress gateway(192, 168, BEEHIVE_SUBNET, 1);
IPAddress subnet(255, 255, 255, 0);

AsyncWebServer *server;
// Prototypes
void handleSetTime(AsyncWebServerRequest *request);
void handleGetTime(AsyncWebServerRequest *request);
void handleGetFile(AsyncWebServerRequest *request);
void handleGetSnapshot(AsyncWebServerRequest *request);
void handleGetEntranceSize(AsyncWebServerRequest *request);
void handleSetEntranceSize(AsyncWebServerRequest *request);
void handleLoadDoor(AsyncWebServerRequest *request);
void handleUnloadDoor(AsyncWebServerRequest *request);
void handleStart(AsyncWebServerRequest *request);
void handleStop(AsyncWebServerRequest *request);
void handleReset(AsyncWebServerRequest *request);
void handleGetState(AsyncWebServerRequest *request);
void handleGetCounterThreshold(AsyncWebServerRequest *request);
void handleGetDoorThreshold(AsyncWebServerRequest *request);
void handleSetCounterThreshold(AsyncWebServerRequest *request);
void handleSetDoorThreshold(AsyncWebServerRequest *request);
void handleGetFileList(AsyncWebServerRequest *request);

unsigned long long wifi_check_interval_ms = 60 * 1000;
unsigned long long last_wifi_check_ms = 0;
//--------------------------

//-----Time-----------------
typedef struct {
  int year;
  int month;
  int day;
  int hour;
  int minute;
  int second;
  int millis;
} Time;

unsigned long millis_last = 0;
unsigned long long millis_time = 0;
bool have_real_time = false;
Time real_time;  // received time
unsigned long long real_time_epoch = 0;
unsigned long long base_time = 0;
Time current_time;
int last_check_hour = 0;
int previous_day_hour = 22;
int current_day_hour = 23;
SemaphoreHandle_t time_mutex;

// Prototypes
unsigned long long get_epoch(const Time &t);
String get_iso_time(const Time &t);
void updateMillisTime();
void updateCurrentTime();
unsigned long long getCurrentTimeMs();
//--------------------------

//-----SD card--------------
#define SD_CS 7
#define SD_MOSI 6
#define SD_MISO 5
#define SD_SCK 4
SdFat SD;
SdFile dataFile;
SPIClass spi(FSPI);
//--------------------------

//-----Files----------------
int max_csv_file_count = 56;
int csv_file_count = 0;
String oldest_csv_file_name = "";
String current_csv_file_name = "";
bool have_current_csv_file = false;
//--------------------------

//-----CSV------------------
const unsigned long csv_write_interval_ms = 60000;
unsigned long last_csv_write_ms = 0;
// Prototypes
void manageCsvFiles();
void updateCsvFileStats();
void deleteCsvFile(String fileName);
void createCsvFile();
void openCsvFile();
void closeCsvFile();
void writeDataToCsvFile();
String buildCsvFileName(const Time &t);
//--------------------------

//-----Door control---------
#define I2C_SDA_PIN 8
#define I2C_SCL_PIN 9
#define I2C_FREQUENCY 400000

const byte CMD_LED_ON_BASE = 0x10;
const byte CMD_LED_OFF_BASE = 0x20;
const byte CMD_IR_READ_BASE = 0x30;

#define DOOR_SENSOR_INDEX 3
int door_threshold = 127;

#define MOTOR_TIMEOUT_RIGHT 1500
#define MOTOR_TIMEOUT_LEFT 1500

const byte SLAVE_ADDRESSES_LEFT[] = { 40, 41, 42, 43, 44, 45, 46, 47, 48, 49 };
const byte SLAVE_ADDRESSES_RIGHT[] = { 57, 56, 55, 54, 53, 52, 51, 50, 49 };

const int RIGHT_ADDR_COUNT = sizeof(SLAVE_ADDRESSES_RIGHT) / sizeof(SLAVE_ADDRESSES_RIGHT[0]);
const int LEFT_ADDR_COUNT = sizeof(SLAVE_ADDRESSES_LEFT) / sizeof(SLAVE_ADDRESSES_LEFT[0]);

const int RIGHT_POS_MAX = 9;
const int LEFT_POS_MAX = 10;

const int RIGHT_MOTOR_PIN_1 = 3;
const int RIGHT_MOTOR_PIN_2 = 10;

const int LEFT_MOTOR_PIN_1 = 0;
const int LEFT_MOTOR_PIN_2 = 1;

const int PWM_FREQUENCY = 1000;
const int PWM_RESOLUTION = 8;

const int MOTOR_SPEED_RIGHT = 150;
const int MOTOR_SPEED_LEFT = 150;
const int MOTOR_SPEED = 150;

int last_requested_entrance_size = -1;

enum DoorSelection {
  DOOR_RIGHT,
  DOOR_LEFT,
  DOOR_BOTH
};

enum MotorDirection {
  MOTOR_1,
  MOTOR_2
};

// Prototypes
int setLedState(byte addr, byte idx, bool state);
int readIrSensor(byte addr, byte idx);
bool isSensorBlocked(int sensorNum, MotorDirection direction);
int getPositionDoor(MotorDirection direction);
bool setPosition(int targetSensor, MotorDirection direction);
bool computeTargets(int numberOfGates, int &leftTarget, int &rightTarget);
bool getCurrentEntranceSize(int &entranceSize, int &leftPos, int &rightPos);
void motorForward(int speed, MotorDirection direction);
void motorReverse(int speed, MotorDirection direction);
void motorStop(MotorDirection direction);
void pulseClose(MotorDirection direction);
void pulseOpen(MotorDirection direction);
bool loadDoor(MotorDirection direction);
void unloadDoor(MotorDirection direction);
bool parseDoorSelection(AsyncWebServerRequest *request, DoorSelection &selection);
int readDoorSensorRaw(byte gate_index);
//--------------------------

//-----Counter logic--------
const byte COUNTER_SLAVE_ADDRESSES[] = {
  40, 41, 42, 43, 44, 45, 46, 47, 48, 49,
  50, 51, 52, 53, 54, 55, 56, 57
};

const int COUNTER_NUM_SLAVES = sizeof(COUNTER_SLAVE_ADDRESSES) / sizeof(COUNTER_SLAVE_ADDRESSES[0]);
const int COUNTER_NUM_GATES = COUNTER_NUM_SLAVES - 1;
const int COUNTER_NUM_SENSORS = 3;
const int COUNTER_MAX_SEQ = 5;
int counter_threshold = 127;

struct CounterGateState {
  bool s[COUNTER_NUM_SENSORS];
  int raw[COUNTER_NUM_SENSORS];
};

struct CounterGateTracker {
  char history[COUNTER_MAX_SEQ];
  int len;
  char last_state;
  int entrance_count;
  int exit_count;
};

CounterGateTracker counterTrackers[COUNTER_NUM_GATES];

int counter_total_in = 0;
int counter_total_out = 0;

// Prototypes
bool parseStrictInt(const String &text, int &value);
void counterSetup();
void counterReset();
CounterGateState getSingleCounterGateState(byte gate_index);
char classifyCounterGate(const CounterGateState &gate);
bool counterEndsWith(const char *buf, int len, const char *pattern);
void updateCounterTracker(int gate, char label);
void updateCounterTotals();
void updateCounterLogic();
void runCounterScan(int readings[COUNTER_NUM_SENSORS][COUNTER_NUM_GATES]);
//--------------------------

//-----Process--------------
void entranceSetup();
bool operational = false;
bool system_reset = false;
//--------------------------

void setup() {
  time_mutex = xSemaphoreCreateMutex();

  //-----UART-----------------
  Serial.begin(115200);
  delay(1000);
  Serial.print("Entrance SETUP: ");
  Serial.print(BEEHIVE_ID);
  Serial.println("\n");
  //--------------------------

  //----WIFI------------------
  WiFi.mode(WIFI_STA);
  WiFi.setAutoReconnect(true);
  WiFi.persistent(true);
  if (!WiFi.config(local_ip, gateway, subnet)) {
    Serial.println("wifi_config_failed");
  }
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    Serial.print(".");
    delay(500);
  }
  Serial.println("");
  Serial.print("IP: ");
  Serial.println(WiFi.localIP());
  //--------------------------

  //-----Web Server-----------
  if (!LittleFS.begin()) {
    Serial.println("Failed to mount LittleFS");
    while (1) {
    }
  }
  server = new AsyncWebServer(server_port);
  server->on("/setTime", HTTP_GET, handleSetTime);
  server->on("/getTime", HTTP_GET, handleGetTime);
  server->on("/getFile", HTTP_GET, handleGetFile);
  server->on("/getSnapshot", HTTP_GET, handleGetSnapshot);
  server->on("/load", HTTP_GET, handleLoadDoor);
  server->on("/unload", HTTP_GET, handleUnloadDoor);
  server->on("/start", HTTP_GET, handleStart);
  server->on("/stop", HTTP_GET, handleStop);
  server->on("/reset", HTTP_GET, handleReset);
  server->on("/getEntranceSize", HTTP_GET, handleGetEntranceSize);
  server->on("/setEntranceSize", HTTP_GET, handleSetEntranceSize);
  server->on("/getState", HTTP_GET, handleGetState);
  server->on("/getCounterThreshold", HTTP_GET, handleGetCounterThreshold);
  server->on("/getDoorThreshold", HTTP_GET, handleGetDoorThreshold);
  server->on("/setCounterThreshold", HTTP_GET, handleSetCounterThreshold);
  server->on("/setDoorThreshold", HTTP_GET, handleSetDoorThreshold);
  server->on("/getFileList", HTTP_GET, handleGetFileList);
  server->serveStatic("/", LittleFS, "/www/").setDefaultFile("index.html");

  server->begin();
  //--------------------------

  //-----OTA-----------
#if OTA_ENABLE
  ArduinoOTA.setHostname(BEEHIVE_ID);
  ArduinoOTA.setPort(3232);
  ArduinoOTA.setPassword("XXXXXXXX");
  // OTA debug callbacks
  ArduinoOTA.onStart([]() {
    Serial.println("OTA Start");
    if (ArduinoOTA.getCommand() != U_FLASH) {
      Serial.println("Unmounting LittleFS for filesystem OTA...");
      LittleFS.end();
    } else {
      Serial.println("Firmware OTA...");
    }
  });

  ArduinoOTA.onEnd([]() {
    Serial.println("\nOTA End");
  });

  ArduinoOTA.onProgress([](unsigned int progress, unsigned int total) {
    //Serial.printf("Progress: %u%%\r\n",(progress * 100) / total);
    Serial.printf(
      "Progress: %u%%  Temp=%.1f C  "
      "WiFiStatus=%d  RSSI=%d  "
      "Heap=%u MinHeap=%u\r\n",
      (progress * 100) / total,
      temperatureRead(),
      WiFi.status(),
      WiFi.RSSI(),
      ESP.getFreeHeap(),
      ESP.getMinFreeHeap());
  });

  ArduinoOTA.onError([](ota_error_t error) {
    //Serial.printf("Error[%u]: ", error);
    Serial.printf(
      "Error[%u]: WiFiStatus=%d RSSI=%d FreeHeap=%u MinFreeHeap=%u\r\n",
      error,
      WiFi.status(),
      WiFi.RSSI(),
      ESP.getFreeHeap(),
      ESP.getMinFreeHeap());
    if (error == OTA_AUTH_ERROR) {
      Serial.println("OTA Auth Failed");
    } else if (error == OTA_BEGIN_ERROR) {
      Serial.println("OTA Begin Failed");
    } else if (error == OTA_CONNECT_ERROR) {
      Serial.println("OTA Connect Failed");
    } else if (error == OTA_RECEIVE_ERROR) {
      Serial.println("OTA Receive Failed");
    } else if (error == OTA_END_ERROR) {
      Serial.println("OTA End Failed");
    }
  });

  ArduinoOTA.begin();
#endif
  //--------------------------

  //-----SD Card--------------
  Serial.println("Initializing SD card...");
  if (!spi.begin(SD_SCK, SD_MISO, SD_MOSI, SD_CS)) {
    Serial.println("SPI initialization failed!");
    return;
  }
  SdSpiConfig spiConfig(SD_CS, DEDICATED_SPI, SD_SCK_MHZ(10), &spi);
  if (!SD.begin(spiConfig)) {
    Serial.println("SD initialization failed!");
    return;
  }
  Serial.println("SD initialization done.");
  //--------------------------

  //-----Entrance---------------
  entranceSetup();
  //--------------------------

  //-----Counter---------------
  counterSetup();
  //--------------------------

  delay(300);
  Serial.println("READY");
  Serial.println("Time not set yet. Use /setTime.");
}

void loop() {
  //loop_num++;

  if (system_reset) {
    ESP.restart();
  }

#if OTA_ENABLE
  ArduinoOTA.handle();
#endif

  if ((millis() - last_wifi_check_ms) > wifi_check_interval_ms) {
    if (WiFi.status() != WL_CONNECTED) {
      Serial.println("WiFi lost, reconnecting...");
      WiFi.disconnect();
      WiFi.begin(ssid, password);
    }
    last_wifi_check_ms = millis();
  }

  if (have_real_time) {  // Wait until real time is set
    updateCurrentTime();
    if (!have_current_csv_file) {
      manageCsvFiles();
      Serial.println("Current CSV file is set!");
    } else {
      if (current_time.hour == current_day_hour && last_check_hour == previous_day_hour) {
        Serial.println("Congratulations! You survived another day.");
        have_current_csv_file = false;
        manageCsvFiles();
        counterReset();
      }
      last_check_hour = current_time.hour;

      if (operational && have_current_csv_file) {
        updateCounterLogic();
        if (millis() - last_csv_write_ms >= csv_write_interval_ms) {
          last_csv_write_ms = millis();
          writeDataToCsvFile();
          //Serial.println(loop_num);
          //loop_num = 0;
        }
      }
    }
  } else {
    delay(10);
  }
}

// ============================================================================
// Time functions
// ============================================================================
void updateMillisTime() {
  unsigned long millis_current = millis();
  millis_time = millis_time + (unsigned long long)(millis_current - millis_last);
  millis_last = millis_current;
}

void updateCurrentTime() {
  xSemaphoreTake(time_mutex, portMAX_DELAY);
  updateMillisTime();
  unsigned long long dt = millis_time - base_time;
  unsigned long long epoch_new = real_time_epoch + (dt / 1000);
  int ms = dt % 1000;
  struct tm t;
  gmtime_r((time_t *)&epoch_new, &t);
  current_time.year = t.tm_year + 1900;
  current_time.month = t.tm_mon + 1;
  current_time.day = t.tm_mday;
  current_time.hour = t.tm_hour;
  current_time.minute = t.tm_min;
  current_time.second = t.tm_sec;
  current_time.millis = ms;
  xSemaphoreGive(time_mutex);
}

unsigned long long get_epoch(const Time &t) {
  struct tm tm_time = { 0 };
  tm_time.tm_year = t.year - 1900;
  tm_time.tm_mon = t.month - 1;
  tm_time.tm_mday = t.day;
  tm_time.tm_hour = t.hour;
  tm_time.tm_min = t.minute;
  tm_time.tm_sec = t.second;
  setenv("TZ", "UTC0", 1);
  tzset();
  return (unsigned long long)mktime(&tm_time);
}

String get_iso_time(const Time &t) {
  char buf[64];
  snprintf(buf, sizeof(buf), "%04d_%02d_%02dT%02d_%02d_%02d_%03dZ",
           t.year, t.month, t.day, t.hour, t.minute, t.second, t.millis);
  return String(buf);
}

String get_date_prefix(const Time &t) {
  char buf[32];
  snprintf(buf, sizeof(buf), "%04d_%02d_%02d", t.year, t.month, t.day);
  return String(buf);
}

unsigned long long getCurrentTimeMs() {
  xSemaphoreTake(time_mutex, portMAX_DELAY);
  unsigned long long t = get_epoch(current_time) * 1000ULL + (unsigned long long)current_time.millis;
  xSemaphoreGive(time_mutex);
  return t;
}
// ============================================================================
// Web server handlers
// ============================================================================
void handleSetTime(AsyncWebServerRequest *request) {
  xSemaphoreTake(time_mutex, portMAX_DELAY);
  updateMillisTime();
  base_time = millis_time;
  if (request->hasParam("year")) real_time.year = request->getParam("year")->value().toInt();
  if (request->hasParam("month")) real_time.month = request->getParam("month")->value().toInt();
  if (request->hasParam("day")) real_time.day = request->getParam("day")->value().toInt();
  if (request->hasParam("hour")) real_time.hour = request->getParam("hour")->value().toInt();
  if (request->hasParam("minute")) real_time.minute = request->getParam("minute")->value().toInt();
  String second_String = request->getParam("second")->value();
  float second_float = second_String.toFloat();
  real_time.second = (int)second_float;
  real_time.millis = (int)((second_float - real_time.second) * 1000);
  real_time_epoch = get_epoch(real_time);
  have_real_time = true;
  xSemaphoreGive(time_mutex);

  DynamicJsonDocument resp(256);
  resp["status"] = "ok";
  String response;
  serializeJson(resp, response);
  request->send(200, "application/json", response);
}

void handleGetTime(AsyncWebServerRequest *request) {
  DynamicJsonDocument resp(256);

  xSemaphoreTake(time_mutex, portMAX_DELAY);
  resp["status"] = "ok";
  resp["year"] = String(current_time.year);
  resp["month"] = String(current_time.month);
  resp["day"] = String(current_time.day);
  resp["hour"] = String(current_time.hour);
  resp["minute"] = String(current_time.minute);
  resp["second"] = String(current_time.second);
  resp["millis"] = String(current_time.millis);
  xSemaphoreGive(time_mutex);

  String response;
  serializeJson(resp, response);
  request->send(200, "application/json", response);
}

void handleGetFile(AsyncWebServerRequest *request) {
  updateCsvFileStats();
  String file_name = current_csv_file_name;
  if (request->hasParam("file_name")) {
    file_name = request->getParam("file_name")->value();
  }
  if (file_name.isEmpty()) {
    request->send(404, "text/plain", "No CSV file available");
    return;
  }
  if (file_name.indexOf("..") != -1 || file_name.indexOf('/') != -1 || !file_name.endsWith(".csv")) {
    request->send(400, "text/plain", "Invalid filename");
    return;
  }
  SdFile *downloadFile = new SdFile();
  if (!downloadFile->open(file_name.c_str(), O_RDONLY)) {
    delete downloadFile;
    request->send(404, "text/plain", "File not found");
    return;
  }
  const size_t totalSize = (size_t)downloadFile->fileSize();
  AsyncWebServerResponse *response = request->beginResponse(
    "text/csv",
    totalSize,
    [downloadFile, totalSize](uint8_t *buffer, size_t maxLen, size_t index) mutable -> size_t {
      int bytesRead = downloadFile->read(buffer, maxLen);

      if (bytesRead <= 0) {
        downloadFile->close();
        delete downloadFile;
        return 0;
      }

      if (index + (size_t)bytesRead >= totalSize) {
        downloadFile->close();
        delete downloadFile;
      }

      return (size_t)bytesRead;
    });
  response->addHeader("Content-Disposition", "attachment; filename=\"" + file_name + "\"");
  request->send(response);
}

void handleStart(AsyncWebServerRequest *request) {
  operational = true;

  DynamicJsonDocument resp(256);
  resp["status"] = "ok";
  String response;
  serializeJson(resp, response);
  request->send(200, "application/json", response);
}

void handleStop(AsyncWebServerRequest *request) {
  operational = false;

  DynamicJsonDocument resp(256);
  resp["status"] = "ok";
  String response;
  serializeJson(resp, response);
  request->send(200, "application/json", response);
}

void handleReset(AsyncWebServerRequest *request) {
  system_reset = true;

  DynamicJsonDocument resp(256);
  resp["status"] = "ok";
  String resp_str;
  serializeJson(resp, resp_str);
  request->send(200, "application/json", resp_str);
}

void handleLoadDoor(AsyncWebServerRequest *request) {
  DoorSelection selection;
  if (!parseDoorSelection(request, selection)) {
    DynamicJsonDocument resp(256);
    resp["status"] = "error";
    resp["message"] = "Invalid side. Use right, left, or both";

    String response;
    serializeJson(resp, response);
    request->send(400, "application/json", response);
    return;
  }

  bool rightOk = true;
  bool leftOk = true;

  if (selection == DOOR_RIGHT || selection == DOOR_BOTH) {
    rightOk = loadDoor(MOTOR_1);
  }

  if (selection == DOOR_LEFT || selection == DOOR_BOTH) {
    leftOk = loadDoor(MOTOR_2);
  }

  DynamicJsonDocument resp(256);
  resp["status"] = (rightOk && leftOk) ? "ok" : "error";
  resp["rightLoaded"] = rightOk;
  resp["leftLoaded"] = leftOk;

  if (selection == DOOR_RIGHT) resp["side"] = "right";
  else if (selection == DOOR_LEFT) resp["side"] = "left";
  else resp["side"] = "both";

  String response;
  serializeJson(resp, response);
  request->send((rightOk && leftOk) ? 200 : 500, "application/json", response);
}

void handleUnloadDoor(AsyncWebServerRequest *request) {
  DoorSelection selection;
  if (!parseDoorSelection(request, selection)) {
    DynamicJsonDocument resp(256);
    resp["status"] = "error";
    resp["message"] = "Invalid side. Use right, left, or both";

    String response;
    serializeJson(resp, response);
    request->send(400, "application/json", response);
    return;
  }

  if (selection == DOOR_RIGHT || selection == DOOR_BOTH) {
    unloadDoor(MOTOR_1);
  }

  if (selection == DOOR_LEFT || selection == DOOR_BOTH) {
    unloadDoor(MOTOR_2);
  }

  DynamicJsonDocument resp(256);
  resp["status"] = "ok";

  if (selection == DOOR_RIGHT) resp["side"] = "right";
  else if (selection == DOOR_LEFT) resp["side"] = "left";
  else resp["side"] = "both";

  String response;
  serializeJson(resp, response);
  request->send(200, "application/json", response);
}

void handleGetEntranceSize(AsyncWebServerRequest *request) {
  DynamicJsonDocument resp(256);

  int entranceSize = -1;
  int leftPos = 0;
  int rightPos = 0;

  bool ok = getCurrentEntranceSize(entranceSize, leftPos, rightPos);

  resp["status"] = ok ? "ok" : "unknown_position";
  resp["entranceSize"] = entranceSize;
  resp["leftPosition"] = leftPos;
  resp["rightPosition"] = rightPos;
  resp["lastRequestedEntranceSize"] = last_requested_entrance_size;

  String response;
  serializeJson(resp, response);

  request->send(ok ? 200 : 409, "application/json", response);
}

void handleSetEntranceSize(AsyncWebServerRequest *request) {
  String rawValue;

  if (request->hasParam("size")) {
    rawValue = request->getParam("size")->value();
  } else if (request->hasParam("value")) {
    rawValue = request->getParam("value")->value();
  } else if (request->hasParam("entranceSize")) {
    rawValue = request->getParam("entranceSize")->value();
  } else if (request->hasParam("numberOfGates")) {
    rawValue = request->getParam("numberOfGates")->value();
  } else {
    DynamicJsonDocument resp(256);
    resp["status"] = "error";
    resp["message"] = "Missing parameter: use value, entranceSize, or numberOfGates";

    String response;
    serializeJson(resp, response);
    request->send(400, "application/json", response);
    return;
  }

  int requestedValue = 0;
  if (!parseStrictInt(rawValue, requestedValue)) {
    DynamicJsonDocument resp(256);
    resp["status"] = "error";
    resp["message"] = "Parameter must be an integer";

    String response;
    serializeJson(resp, response);
    request->send(400, "application/json", response);
    return;
  }

  int constrainedValue = constrain(requestedValue, 0, 18);
  last_requested_entrance_size = constrainedValue;

  if (constrainedValue == 16 || constrainedValue == 17 || constrainedValue == 18) {
    openFull(MOTOR_1);
    openFull(MOTOR_2);
  } else if (constrainedValue == 1 || ((constrainedValue % 2 == 0) && (constrainedValue != 0))) {
    getCommand(constrainedValue + 2);
  } else {
    getCommand(constrainedValue + 1);
  }
  getCommand(constrainedValue);

  int actualEntranceSize = -1;
  int leftPos = 0;
  int rightPos = 0;
  bool actualKnown = getCurrentEntranceSize(actualEntranceSize, leftPos, rightPos);

  DynamicJsonDocument resp(256);
  resp["status"] = "ok";
  resp["requestedValue"] = requestedValue;
  resp["appliedEntranceSize"] = constrainedValue;
  resp["actualEntranceSize"] = actualEntranceSize;
  resp["actualKnown"] = actualKnown;
  resp["leftPosition"] = leftPos;
  resp["rightPosition"] = rightPos;

  String response;
  serializeJson(resp, response);
  request->send(200, "application/json", response);
}

void handleGetState(AsyncWebServerRequest *request) {
  DynamicJsonDocument resp(256);

  resp["status"] = "ok";

  if (!have_real_time) {
    resp["state"] = "waiting for time";
  } else if (operational) {
    resp["state"] = "running";
  } else {
    resp["state"] = "stopped";
  }

  String response;
  serializeJson(resp, response);
  request->send(200, "application/json", response);
}

void handleGetCounterThreshold(AsyncWebServerRequest *request) {
  DynamicJsonDocument resp(256);

  resp["status"] = "ok";
  resp["counter_threshold"] = counter_threshold;

  String response;
  serializeJson(resp, response);
  request->send(200, "application/json", response);
}

void handleGetDoorThreshold(AsyncWebServerRequest *request) {
  DynamicJsonDocument resp(256);

  resp["status"] = "ok";
  resp["door_threshold"] = door_threshold;

  String response;
  serializeJson(resp, response);
  request->send(200, "application/json", response);
}

void handleSetCounterThreshold(AsyncWebServerRequest *request) {
  if (request->hasParam("threshold")) counter_threshold = request->getParam("threshold")->value().toInt();

  DynamicJsonDocument resp(256);
  resp["status"] = "ok";
  String response;
  serializeJson(resp, response);
  request->send(200, "application/json", response);
}

void handleSetDoorThreshold(AsyncWebServerRequest *request) {
  if (request->hasParam("threshold")) door_threshold = request->getParam("threshold")->value().toInt();

  DynamicJsonDocument resp(256);
  resp["status"] = "ok";
  String response;
  serializeJson(resp, response);
  request->send(200, "application/json", response);
}

void handleGetSnapshot(AsyncWebServerRequest *request) {
  int readings[COUNTER_NUM_SENSORS][COUNTER_NUM_GATES];
  runCounterScan(readings);

  DynamicJsonDocument doc(8192);
  JsonArray root = doc.to<JsonArray>();

  for (int gate = 0; gate < COUNTER_NUM_GATES; gate++) {
    JsonArray gateArr = root.createNestedArray();
    // sensors 1–3
    for (int s = 0; s < COUNTER_NUM_SENSORS; s++) {
      gateArr.add(readings[s][gate]);
    }
    // sensor 4 (raw)
    int s4 = readDoorSensorRaw(gate);
    gateArr.add(s4);
  }
  String response;
  serializeJson(doc, response);
  request->send(200, "application/json", response);
}

void handleGetFileList(AsyncWebServerRequest *request) {
  if (operational) {
    request->send(403, "text/plain", "System is RUNNING. Cannot list files. Optionally STOP the system and try again.");
    return;
  }
  if (!have_real_time) {
    request->send(403, "text/plain", "System is WAITING FOR TIME. Cannot list files. SET system time and try again.");
    return;
  }

  SdFile root;
  if (!root.open("/")) {
    request->send(500, "text/plain", "System failed to access SD card.");
    return;
  }

  AsyncResponseStream *response = request->beginResponseStream("application/json");
  response->print("[");

  bool first = true;

  SdFile file;
  while (file.openNext(&root, O_RDONLY)) {
    if (!file.isDir()) {
      char name[64];
      file.getName(name, sizeof(name));

      String fname = String(name);

      if (fname.endsWith(".csv")) {
        if (!first) {
          response->print(",");
        }
        response->print("\"");
        response->print(fname);
        response->print("\"");
        first = false;
      }
    }
    file.close();
  }

  root.close();

  response->print("]");
  request->send(response);
}

bool parseDoorSelection(AsyncWebServerRequest *request, DoorSelection &selection) {
  if (!request->hasParam("side")) {
    selection = DOOR_BOTH;
    return true;
  }

  String side = request->getParam("side")->value();
  side.toLowerCase();

  if (side == "right") {
    selection = DOOR_RIGHT;
    return true;
  }

  if (side == "left") {
    selection = DOOR_LEFT;
    return true;
  }

  if (side == "both") {
    selection = DOOR_BOTH;
    return true;
  }

  return false;
}

// ============================================================================
// Counter functions
// ============================================================================
bool parseStrictInt(const String &text, int &value) {
  if (text.length() == 0) return false;

  char *endPtr = nullptr;
  long parsed = strtol(text.c_str(), &endPtr, 10);

  if (endPtr == text.c_str() || *endPtr != '\0') {
    return false;
  }

  value = (int)parsed;
  return true;
}

void counterSetup() {
  for (int i = 0; i < COUNTER_NUM_GATES; i++) {
    counterTrackers[i].len = 1;
    counterTrackers[i].history[0] = 'R';
    counterTrackers[i].last_state = 'R';
    counterTrackers[i].entrance_count = 0;
    counterTrackers[i].exit_count = 0;
  }

  counter_total_in = 0;
  counter_total_out = 0;

  Serial.println("Counter logic ready");
}

void counterReset() {
  for (int i = 0; i < COUNTER_NUM_GATES; i++) {
    counterTrackers[i].entrance_count = 0;
    counterTrackers[i].exit_count = 0;
  }

  counter_total_in = 0;
  counter_total_out = 0;

  Serial.println("Counter reset");
}

CounterGateState getSingleCounterGateState(byte gate_index) {
  CounterGateState result;

  for (int i = 0; i < COUNTER_NUM_SENSORS; i++) {
    result.s[i] = false;
    result.raw[i] = 0;
  }

  if (gate_index >= COUNTER_NUM_GATES) return result;

  byte emitter = COUNTER_SLAVE_ADDRESSES[gate_index + 1];
  byte receiver = COUNTER_SLAVE_ADDRESSES[gate_index];

  for (int sensor = 0; sensor < COUNTER_NUM_SENSORS; sensor++) {
    if (setLedState(emitter, sensor, true) != 0) continue;
    //delayMicroseconds(50);
    int reading = readIrSensor(receiver, sensor);
    setLedState(emitter, sensor, false);
    if (reading < 0) continue;
    result.raw[sensor] = reading;
    result.s[sensor] = (reading >= counter_threshold);
  }

  return result;
}

char classifyCounterGate(const CounterGateState &gate) {
  bool S1 = gate.s[0];
  bool S2 = gate.s[1];
  bool S3 = gate.s[2];

  byte pattern = (S3 << 2) | (S2 << 1) | S1;

  const char table[8] = {
    'R', 'R', 'x', 'B',
    'R', 'R', 'A', 'x'
  };

  return table[pattern];
}

bool counterEndsWith(const char *buf, int len, const char *pattern) {
  int plen = strlen(pattern);
  if (len < plen) return false;

  for (int i = 0; i < plen; i++) {
    if (buf[len - plen + i] != pattern[i]) return false;
  }

  return true;
}

void updateCounterTracker(int gate, char label) {
  if (label != 'R' && label != 'A' && label != 'B') return;

  CounterGateTracker &t = counterTrackers[gate];

  if (label == t.last_state) return;

  t.last_state = label;

  if (t.len < COUNTER_MAX_SEQ) {
    t.history[t.len++] = label;
  } else {
    for (int i = 0; i < COUNTER_MAX_SEQ - 1; i++) {
      t.history[i] = t.history[i + 1];
    }
    t.history[COUNTER_MAX_SEQ - 1] = label;
  }

  // Entrance
  if ((t.len >= 5 && counterEndsWith(t.history, t.len, "RBABR")) || (t.len >= 4 && counterEndsWith(t.history, t.len, "RABR"))) {
    t.entrance_count++;
    t.len = 1;
    t.history[0] = 'R';
    //Serial.print(gate);
    //Serial.println("+");
    return;
  }

  // Exit
  if ((t.len >= 4 && counterEndsWith(t.history, t.len, "RBAR")) || (t.len >= 5 && counterEndsWith(t.history, t.len, "RABAR"))) {
    t.exit_count++;
    t.len = 1;
    t.history[0] = 'R';
    //Serial.print(gate);
    //Serial.println("-");
    return;
  }
}

void updateCounterTotals() {
  counter_total_in = 0;
  counter_total_out = 0;

  for (int d = 0; d < COUNTER_NUM_GATES; d++) {
    counter_total_in += counterTrackers[d].entrance_count;
    counter_total_out += counterTrackers[d].exit_count;
  }
}

void updateCounterLogic() {
  for (int d = 0; d < COUNTER_NUM_GATES; d++) {
    CounterGateState gate = getSingleCounterGateState(d);
    char label = classifyCounterGate(gate);
    updateCounterTracker(d, label);
  }

  updateCounterTotals();
}

void runCounterScan(int readings[COUNTER_NUM_SENSORS][COUNTER_NUM_GATES]) {
  for (int sensor = 0; sensor < COUNTER_NUM_SENSORS; sensor++) {
    for (int gate = 0; gate < COUNTER_NUM_GATES; gate++) {
      byte emitter = COUNTER_SLAVE_ADDRESSES[gate + 1];
      byte receiver = COUNTER_SLAVE_ADDRESSES[gate];
      setLedState(emitter, sensor, true);
      //delayMicroseconds(50);
      int reading = readIrSensor(receiver, sensor);
      setLedState(emitter, sensor, false);
      readings[sensor][gate] = reading;
    }
  }
}

// ============================================================================
// Motor functions
// ============================================================================
void motorForward(int speed, MotorDirection direction) {
  if (direction == MOTOR_1) {
    ledcWrite(RIGHT_MOTOR_PIN_1, speed);
    ledcWrite(RIGHT_MOTOR_PIN_2, 0);
  } else if (direction == MOTOR_2) {
    ledcWrite(LEFT_MOTOR_PIN_1, 0);
    ledcWrite(LEFT_MOTOR_PIN_2, speed);
  }
}

void motorReverse(int speed, MotorDirection direction) {
  if (direction == MOTOR_1) {
    ledcWrite(RIGHT_MOTOR_PIN_1, 0);
    ledcWrite(RIGHT_MOTOR_PIN_2, speed);
  } else if (direction == MOTOR_2) {
    ledcWrite(LEFT_MOTOR_PIN_1, speed);
    ledcWrite(LEFT_MOTOR_PIN_2, 0);
  }
}

void motorStop(MotorDirection direction) {
  if (direction == MOTOR_1) {
    ledcWrite(RIGHT_MOTOR_PIN_1, 0);
    ledcWrite(RIGHT_MOTOR_PIN_2, 0);
  } else if (direction == MOTOR_2) {
    ledcWrite(LEFT_MOTOR_PIN_1, 0);
    ledcWrite(LEFT_MOTOR_PIN_2, 0);
  }
}

void pulseClose(MotorDirection direction) {
  if (direction == MOTOR_1) {
    motorForward(255, MOTOR_1);
    delay(25);
    motorStop(MOTOR_1);
  } else if (direction == MOTOR_2) {
    motorReverse(255, MOTOR_2);
    delay(10);
    motorStop(MOTOR_2);
  }
}

void pulseOpen(MotorDirection direction) {
  if (direction == MOTOR_1) {
    motorReverse(255, MOTOR_1);
    delay(10);
    motorStop(MOTOR_1);
  } else if (direction == MOTOR_2) {
    motorForward(255, MOTOR_2);
    delay(10);
    motorStop(MOTOR_2);
  }
}

bool loadDoor(MotorDirection direction) {
  const char *doorName = (direction == MOTOR_1) ? "right" : "left";
  unsigned long timeoutMs = (direction == MOTOR_1) ? MOTOR_TIMEOUT_RIGHT : MOTOR_TIMEOUT_LEFT;
  int speed = (direction == MOTOR_1) ? MOTOR_SPEED_RIGHT : MOTOR_SPEED_LEFT;

  Serial.print("Loading ");
  Serial.print(doorName);
  Serial.println(" door (closing to sensor 1)...");

  unsigned long startTime = millis();

  while (!isSensorBlocked(1, direction)) {
    if (millis() - startTime > timeoutMs) {
      motorStop(direction);
      Serial.print("ERROR: ");
      Serial.print(doorName);
      Serial.println(" loadDoor timeout!");
      return false;
    }
    motorForward(speed, direction);
    delay(30);
  }

  motorStop(direction);

  Serial.print(doorName);
  Serial.println(" door loaded at sensor 1.");
  return true;
}

void unloadDoor(MotorDirection direction) {
  const char *doorName = (direction == MOTOR_1) ? "right" : "left";
  int speed = (direction == MOTOR_1) ? MOTOR_SPEED_RIGHT : MOTOR_SPEED_LEFT;

  Serial.print("Unloading ");
  Serial.print(doorName);
  Serial.println(" door (ejecting)...");

  motorReverse(speed, direction);
  delay(2000);
  motorStop(direction);
}

// ============================================================================
// Sensor functions
// ============================================================================
int setLedState(byte addr, byte idx, bool state) {
  byte cmd = (state ? CMD_LED_ON_BASE : CMD_LED_OFF_BASE) + idx;
  Wire.beginTransmission(addr);
  Wire.write(cmd);
  return Wire.endTransmission();
}

int readIrSensor(byte addr, byte idx) {
  byte cmd = CMD_IR_READ_BASE + idx;
  Wire.beginTransmission(addr);
  Wire.write(cmd);
  if (Wire.endTransmission() != 0) return -1;
  if (Wire.requestFrom(addr, (uint8_t)1) == 1) return Wire.read();
  return -1;
}

bool readDoorSensor(byte addr) {
  setLedState(addr, DOOR_SENSOR_INDEX, true);
  int v = readIrSensor(addr, DOOR_SENSOR_INDEX);
  setLedState(addr, DOOR_SENSOR_INDEX, false);
  if (v < 0) return false;
  return (v > door_threshold);
}

int readDoorSensorRaw(byte gate_index) {
  if (gate_index >= COUNTER_NUM_GATES) return -1;
  byte addr = COUNTER_SLAVE_ADDRESSES[gate_index];
  if (setLedState(addr, 3, true) != 0) return -1;
  //delayMicroseconds(50);
  int reading = readIrSensor(addr, 3);
  setLedState(addr, 3, false);
  return reading;  // raw value
}

bool isSensorBlocked(int sensorNum, MotorDirection direction = MOTOR_1) {
  if (direction == MOTOR_1) {
    if (sensorNum < 1 || sensorNum > RIGHT_ADDR_COUNT) return false;
    byte addr = SLAVE_ADDRESSES_RIGHT[sensorNum - 1];
    return readDoorSensor(addr);
  } else if (direction == MOTOR_2) {
    if (sensorNum < 1 || sensorNum > LEFT_ADDR_COUNT) return false;
    byte addr = SLAVE_ADDRESSES_LEFT[sensorNum - 1];
    return readDoorSensor(addr);
  }

  return false;
}

// ============================================================================
// Door functions
// ============================================================================
int getPositionDoor(MotorDirection direction = MOTOR_1) {
  if (direction == MOTOR_1) {
    for (int i = RIGHT_POS_MAX; i >= 1; i--) {
      if (isSensorBlocked(i, MOTOR_1)) return i;
    }
    return 0;
  }
  if (direction == MOTOR_2) {
    for (int i = LEFT_POS_MAX; i >= 1; i--) {
      if (isSensorBlocked(i, MOTOR_2)) return i;
    }
    return 0;
  }
  return 0;
}

bool setPosition(int targetSensor, MotorDirection direction = MOTOR_1) {
  if (direction == MOTOR_1) {
    if (targetSensor < 1 || targetSensor > RIGHT_POS_MAX) {
      Serial.println("Right: Invalid target sensor!");
      return false;
    }

    int startPos = getPositionDoor(MOTOR_1);
    int overshoot = targetSensor + 1;
    if (overshoot > RIGHT_ADDR_COUNT) overshoot = targetSensor;

    unsigned long startTime = millis();

    if (startPos < targetSensor) {
      while (true) {
        if (millis() - startTime > MOTOR_TIMEOUT_RIGHT) {
          motorStop(MOTOR_1);
          Serial.println("Right: ERROR closing timeout!");
          return false;
        }

        if (isSensorBlocked(overshoot, MOTOR_1)) {
          pulseOpen(MOTOR_1);
          break;
        }
        motorForward(MOTOR_SPEED_RIGHT, MOTOR_1);
      }

      startTime = millis();

      while (true) {
        if (millis() - startTime > MOTOR_TIMEOUT_RIGHT) {
          motorStop(MOTOR_1);
          Serial.println("Right: ERROR opening-back timeout!");
          return false;
        }

        if (!isSensorBlocked(targetSensor, MOTOR_1)) {
          pulseClose(MOTOR_1);
          return true;
        }
        motorReverse(MOTOR_SPEED_RIGHT, MOTOR_1);
      }
    } else if (startPos > targetSensor) {
      while (true) {
        if (millis() - startTime > MOTOR_TIMEOUT_RIGHT) {
          motorStop(MOTOR_1);
          Serial.println("Right: ERROR opening timeout!");
          return false;
        }

        if (!isSensorBlocked(targetSensor, MOTOR_1)) {
          pulseClose(MOTOR_1);
          return true;
        }
        motorReverse(MOTOR_SPEED_RIGHT, MOTOR_1);
      }
    }

    Serial.println("Right: Already at target.");
    return true;
  }

  if (direction == MOTOR_2) {
    if (targetSensor < 1 || targetSensor > LEFT_POS_MAX) {
      Serial.println("Left: Invalid target sensor!");
      return false;
    }

    int startPos = getPositionDoor(MOTOR_2);
    unsigned long startTime = millis();

    if (startPos < targetSensor) {
      while (true) {
        if (millis() - startTime > MOTOR_TIMEOUT_LEFT) {
          motorStop(MOTOR_2);
          Serial.println("Left: ERROR closing timeout!");
          return false;
        }

        if (isSensorBlocked(targetSensor, MOTOR_2)) {
          pulseClose(MOTOR_2);
          return true;
        }
        motorForward(MOTOR_SPEED, MOTOR_2);
      }
    } else if (startPos > targetSensor) {
      while (true) {
        if (millis() - startTime > MOTOR_TIMEOUT_LEFT) {
          motorStop(MOTOR_2);
          Serial.println("Left: ERROR opening timeout!");
          return false;
        }

        if (!isSensorBlocked(targetSensor, MOTOR_2)) {
          pulseOpen(MOTOR_2);
          break;
        }
        motorReverse(MOTOR_SPEED, MOTOR_2);
      }

      startTime = millis();

      while (true) {
        if (millis() - startTime > MOTOR_TIMEOUT_LEFT) {
          motorStop(MOTOR_2);
          Serial.println("Left: ERROR closing-back timeout!");
          return false;
        }

        if (isSensorBlocked(targetSensor, MOTOR_2)) {
          pulseClose(MOTOR_2);
          return true;
        }
        motorForward(MOTOR_SPEED, MOTOR_2);
      }
    }

    Serial.println("Left: Already at target.");
    return true;
  }

  return false;
}

bool computeTargets(int numberOfGates, int &leftTarget, int &rightTarget) {
  if (numberOfGates < 0 || numberOfGates > 18)
    return false;

  leftTarget = 9 - (numberOfGates / 2);
  rightTarget = 9 - ((numberOfGates - 1) / 2);

  if (leftTarget < 1) leftTarget = 1;
  if (leftTarget > LEFT_POS_MAX) leftTarget = LEFT_POS_MAX;
  if (rightTarget < 1) rightTarget = 1;
  if (rightTarget > RIGHT_POS_MAX) rightTarget = RIGHT_POS_MAX;

  return true;
}

void getCommand(int numberOfGates) {
  if (numberOfGates > 0) {
    int leftTarget, rightTarget;

    if (!computeTargets(numberOfGates, leftTarget, rightTarget)) {
      Serial.println("Invalid numberOfGates (allowed 1..17).");
      return;
    }

    Serial.print("Command: open gates = ");
    Serial.println(numberOfGates);

    if (!setPosition(rightTarget, MOTOR_1)) {
      Serial.println("Right move failed. Stopping right motor.");
      motorStop(MOTOR_1);
      return;
    }

    if (!setPosition(leftTarget, MOTOR_2)) {
      Serial.println("Left move failed. Stopping left motor.");
      motorStop(MOTOR_2);
      return;
    }

    Serial.println("Gate command done.");
  } else if (numberOfGates == 0) {
    getCommand(1);

    while (true) {
      if (!isSensorBlocked(1, MOTOR_1)) {
        //Serial.println("test_1");
        pulseClose(MOTOR_1);
        break;
      }
      //Serial.println("test_2");
      motorForward(MOTOR_SPEED_RIGHT, MOTOR_1);
    }
  }
}

bool getCurrentEntranceSize(int &entranceSize, int &leftPos, int &rightPos) {
  leftPos = getPositionDoor(MOTOR_2);
  rightPos = getPositionDoor(MOTOR_1);

  // Special case for fully closed entrance size 0 from your sketch logic
  if (leftPos == LEFT_POS_MAX && rightPos == 0) {
    entranceSize = 0;
    return true;
  }

  for (int gates = 1; gates <= 18; gates++) {
    int leftTarget, rightTarget;
    if (!computeTargets(gates, leftTarget, rightTarget)) continue;

    if (leftPos == leftTarget && rightPos == rightTarget) {
      entranceSize = gates;
      return true;
    }
  }

  entranceSize = -1;
  return false;
}

bool openFull(MotorDirection direction) {
  if (direction == MOTOR_1) {
    Serial.println("Opening door fully...");
    unsigned long startTime = millis();
    while (isSensorBlocked(1, MOTOR_1)) {
      if (millis() - startTime > MOTOR_TIMEOUT_RIGHT) {
        motorStop(MOTOR_1);
        Serial.println("ERROR: openFull timeout!");
        return false;
      }
      motorReverse(MOTOR_SPEED_RIGHT, MOTOR_1);
    }
    motorStop(MOTOR_1);
    motorForward(255, MOTOR_1);
    motorForward(50, MOTOR_1);
    motorForward(0, MOTOR_1);
    Serial.println("Door fully opened (sensor 1).");
    return true;
  } else if (direction == MOTOR_2) {
    Serial.println("Opening door fully...");
    unsigned long startTime = millis();
    while (isSensorBlocked(1, MOTOR_2)) {
      if (millis() - startTime > MOTOR_TIMEOUT_LEFT) {
        motorStop(MOTOR_2);
        Serial.println("ERROR: openFull timeout!");
        return false;
      }
      motorReverse(MOTOR_SPEED, MOTOR_2);
    }
    pulseOpen(MOTOR_2);
    Serial.println("Door fully opened (sensor 1).");
    return true;
  }
}

void entranceSetup() {
  digitalWrite(RIGHT_MOTOR_PIN_1, LOW);
  digitalWrite(RIGHT_MOTOR_PIN_2, LOW);

  Wire.begin(I2C_SDA_PIN, I2C_SCL_PIN, I2C_FREQUENCY);

  ledcAttach(RIGHT_MOTOR_PIN_1, PWM_FREQUENCY, PWM_RESOLUTION);
  ledcAttach(RIGHT_MOTOR_PIN_2, PWM_FREQUENCY, PWM_RESOLUTION);
  ledcAttach(LEFT_MOTOR_PIN_1, PWM_FREQUENCY, PWM_RESOLUTION);
  ledcAttach(LEFT_MOTOR_PIN_2, PWM_FREQUENCY, PWM_RESOLUTION);

  Serial.println("Door Control Ready");
}

// ============================================================================
// CSV Functions
// ============================================================================
String buildCsvFileName(const Time &t) {
  xSemaphoreTake(time_mutex, portMAX_DELAY);
  String name = String(BEEHIVE_ID) + "_BEC_" + get_date_prefix(t) + ".csv";
  xSemaphoreGive(time_mutex);

  return name;
}

void closeCsvFile() {
  if (dataFile.isOpen()) {
    dataFile.close();
  }
}

void updateCsvFileStats() {
  csv_file_count = 0;
  oldest_csv_file_name = "";
  current_csv_file_name = "";
  have_current_csv_file = false;

  SdFile dir;
  if (!dir.open("/")) {
    Serial.println("CSV stats: failed to open root directory");
    return;
  }

  char datePrefix[24];
  xSemaphoreTake(time_mutex, portMAX_DELAY);
  snprintf(
    datePrefix,
    sizeof(datePrefix),
    "%s_BEC_%04d_%02d_%02d",
    BEEHIVE_ID,
    current_time.year,
    current_time.month,
    current_time.day);
  xSemaphoreGive(time_mutex);

  SdFile entry;
  while (entry.openNext(&dir, O_RDONLY)) {
    if (!entry.isDir()) {
      char nameBuf[128] = { 0 };
      entry.getName(nameBuf, sizeof(nameBuf));
      String name = String(nameBuf);

      if (name.endsWith(".csv")) {
        csv_file_count++;

        if (oldest_csv_file_name.isEmpty() || name < oldest_csv_file_name) {
          oldest_csv_file_name = name;
        }

        if (name.startsWith(datePrefix)) {
          if (!have_current_csv_file || name > current_csv_file_name) {
            have_current_csv_file = true;
            current_csv_file_name = name;
          }
        }
      }
    }
    entry.close();
  }

  dir.close();
}

void deleteCsvFile(String fileName) {
  if (fileName.isEmpty()) return;

  if (SD.exists(fileName.c_str())) {
    if (SD.remove(fileName.c_str())) {
      Serial.print("Deleted CSV file: ");
      Serial.println(fileName);
    } else {
      Serial.print("Failed to delete CSV file: ");
      Serial.println(fileName);
    }
  }

  if (fileName == current_csv_file_name) {
    current_csv_file_name = "";
    have_current_csv_file = false;
  }
}

void createCsvFile() {
  closeCsvFile();
  String newFileName = buildCsvFileName(current_time);

  SdFile newFile;
  if (!newFile.open(newFileName.c_str(), O_CREAT | O_TRUNC | O_WRONLY)) {
    Serial.print("Failed to create CSV file: ");
    Serial.println(newFileName);
    have_current_csv_file = false;
    current_csv_file_name = "";
    return;
  }

  newFile.print("Epoch_time_ms,");
  for (int i = 1; i < COUNTER_NUM_GATES + 1; i++) {
    newFile.printf("In_%d,", i);
  }
  newFile.print("In_sum,");
  for (int i = 1; i < COUNTER_NUM_GATES + 1; i++) {
    newFile.printf("Out_%d,", i);
  }
  newFile.println("Out_sum");
  newFile.close();

  current_csv_file_name = newFileName;
  have_current_csv_file = true;

  Serial.print("Created CSV file: ");
  Serial.println(current_csv_file_name);
}

void manageCsvFiles() {
  updateCsvFileStats();
  if (!have_current_csv_file) {
    createCsvFile();
    csv_file_count++;
  }
  while (csv_file_count > max_csv_file_count) {
    deleteCsvFile(oldest_csv_file_name);
    updateCsvFileStats();
  }
}

void openCsvFile() {
  if (current_csv_file_name.isEmpty()) return;
  closeCsvFile();
  if (!dataFile.open(current_csv_file_name.c_str(), O_WRONLY | O_APPEND)) {
    Serial.print("Failed to open CSV file: ");
    Serial.println(current_csv_file_name);
    have_current_csv_file = false;
  }
}

void writeDataToCsvFile() {
  openCsvFile();
  if (!dataFile.isOpen()) {
    Serial.println("CSV write error: file not open");
    return;
  }

  dataFile.printf("%llu,", getCurrentTimeMs());
  for (int i = 0; i < COUNTER_NUM_GATES; i++) {
    dataFile.printf("%d,", counterTrackers[i].entrance_count);
  }
  dataFile.printf("%d,", counter_total_in);
  for (int i = 0; i < COUNTER_NUM_GATES; i++) {
    dataFile.printf("%d,", counterTrackers[i].exit_count);
  }
  dataFile.println(counter_total_out);

  if (dataFile.sync()) {
    Serial.println("CSV data saved.");
  } else {
    Serial.println("CSV data NOT saved.");
  }
  closeCsvFile();
}
