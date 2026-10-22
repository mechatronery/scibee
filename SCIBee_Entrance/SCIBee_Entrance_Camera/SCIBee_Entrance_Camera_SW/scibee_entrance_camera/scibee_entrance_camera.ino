//-----Beehive-----------------
#define BEEHIVE_SSID "SCIBee_D"
#define BEEHIVE_ID "D1"
#define BEEHIVE_IP 111
#define BEEHIVE_SUBNET 4

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
#include "SD_MMC.h"
#include "microtar.h"
#include <unistd.h>
#include "freertos/semphr.h"

//-----WIFI-----------------
const char *ssid = BEEHIVE_SSID;
const char *password = "XXXXXXXX";
const uint16_t server_port = 80;
IPAddress local_ip(192, 168, BEEHIVE_SUBNET, BEEHIVE_IP);
IPAddress gateway(192, 168, BEEHIVE_SUBNET, 1);
IPAddress subnet(255, 255, 255, 0);

AsyncWebServer *server;
void handleSetTime(AsyncWebServerRequest *request);
void handleGetTime(AsyncWebServerRequest *request);
void handleGetFile(AsyncWebServerRequest *request);
void handleGetImage(AsyncWebServerRequest *request);
void handleStart(AsyncWebServerRequest *request);
void handleStop(AsyncWebServerRequest *request);
void handleReset(AsyncWebServerRequest *request);
void handleGetState(AsyncWebServerRequest *request);
void handleGetFileList(AsyncWebServerRequest *request);

unsigned long long wifi_check_interval_ms = 60*1000;
unsigned long long last_wifi_check_ms = 0;
//--------------------------

//-----Camera-----------------
#define EI_TENSOR_ARENA_LOCATION ".psram"
// dont forget to install varroa inferencing library via Sketch -> add ZIP library
// Nujno moras v src/edge-impulse-sdk/classifier/ei_classifier_config.h postavis EI_CLASSIFIER_TFLITE_ENABLE_ESP_NN flag na 0
#include <varroa_inferencing.h>
#include "edge-impulse-sdk/dsp/image/image.hpp"

#if !defined(EI_CLASSIFIER_SENSOR) || EI_CLASSIFIER_SENSOR != EI_CLASSIFIER_SENSOR_CAMERA
#error "This Edge Impulse model is not configured for a camera sensor"
#endif
#define CONFIDENCE_THRESHOLD 0.5f

#include "esp_camera.h"
#define CAMERA_MODEL_ESP32S3_EYE
#include "camera_pins.h"
// LED ring
#define LED_PWM 150 //200
#define LED_PIN 48

#define EI_CAMERA_RAW_FRAME_BUFFER_COLS 640
#define EI_CAMERA_RAW_FRAME_BUFFER_ROWS 480
#define EI_CAMERA_FRAME_BYTE_SIZE 3

#define CROP_Y_SHIFT 0
#define CROP_SIZE 270
#define CROP_X0 ((EI_CAMERA_RAW_FRAME_BUFFER_COLS - CROP_SIZE) / 2)
#define CROP_Y0 (((EI_CAMERA_RAW_FRAME_BUFFER_ROWS - CROP_SIZE) / 2) + CROP_Y_SHIFT)

static bool debug_nn = false;
static uint8_t *snapshot_buf = nullptr;
static uint8_t *crop_buf = nullptr;
volatile int object_X = -1;
volatile int object_Y = -1;

// Operational loop timing / debounce
SemaphoreHandle_t camera_mutex;
unsigned long last_infer_ms = 0;
const unsigned long infer_interval_ms = 200;  // run inference every 200 ms (5 fps)
bool was_centered = false;                    // edge-trigger save when bee enters center zone

void cameraSetup();
void captureAndGETSendImage(AsyncWebServerRequest *request);
bool run_fomo_on_jpeg_frame(camera_fb_t *fb);
static int ei_camera_get_data(size_t offset, size_t length, float *out_ptr);
static void crop_rgb888(const uint8_t *src, uint8_t *dst, int src_w, int src_h, int x0, int y0, int crop_w, int crop_h);
static bool bee_is_centered(int tol_px);
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
Time real_time;
unsigned long long real_time_epoch = 0;
unsigned long long base_time = 0;
Time current_time;
int last_check_hour = 0;
int previous_day_hour = 22;
int current_day_hour = 23;
SemaphoreHandle_t time_mutex;

unsigned long long get_epoch(const Time &t);
String get_iso_time(const Time &t);
void updateMillisTime();
void updateCurrentTime();
//--------------------------

//-----Files----------------
int max_tar_file_count = 56;
int tar_file_count = 0;
String oldest_tar_file_name = "";
String current_tar_file_name = "";
bool have_current_tar_file = false;
mtar_t tar;

void manageTarFiles();
void updateTarFileStats();
void deleteTarFile(String file_name);
void createTarFile();
void openTarFile(String arg_file_name);
void closeTarFile();
void writeImageToTarFile(camera_fb_t *fb);
void finalizeAllTarFiles();
void finalizeTarFile(String arg_file_name);
void unfinalizeTarFile(String arg_file_name);
bool isTarFileFinalized(String arg_file_name);
//--------------------------

//-----Process--------------
bool operational = false;
bool system_reset = false;
// -------------------------

void setup() {
  time_mutex = xSemaphoreCreateMutex();

  //-----UART-----------------
  Serial.begin(115200);
  delay(1000);
  Serial.print("Entrance SETUP: ");
  Serial.print(BEEHIVE_ID);
  Serial.println("\n");
  //--------------------------

  //-----PSRAM-----------------
  if (psramFound()) {
    Serial.println("PSRAM OK");
  } else {
    Serial.println("PSRAM FAIL");
  }
  //--------------------------

  //-----Onboard LED OFF------
  pinMode(3, OUTPUT);
  digitalWrite(3, LOW);
  //--------------------------

  //-----Camera LED ring------
  ledc_timer_config_t timer = {
    .speed_mode = LEDC_LOW_SPEED_MODE,
    .duty_resolution = LEDC_TIMER_10_BIT,  // 0-1024
    .timer_num = LEDC_TIMER_1,
    .freq_hz = 5000,  // 5 kHz pwm
    .clk_cfg = LEDC_AUTO_CLK
  };
  ledc_timer_config(&timer);

  ledc_channel_config_t channel = {
    .gpio_num = LED_PIN,
    .speed_mode = LEDC_LOW_SPEED_MODE,
    .channel = LEDC_CHANNEL_1,
    .intr_type = LEDC_INTR_DISABLE,
    .timer_sel = LEDC_TIMER_1,
    .duty = 0,  // start off
    .hpoint = 0
  };
  ledc_channel_config(&channel);
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
  server->on("/getSnapshot", HTTP_GET, handleGetImage);
  server->on("/start", HTTP_GET, handleStart);
  server->on("/stop", HTTP_GET, handleStop);
  server->on("/reset", HTTP_GET, handleReset);
  server->on("/getState", HTTP_GET, handleGetState);
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
  SD_MMC.setPins(39, 38, 40);
  if (!SD_MMC.begin("/sdcard", true, false, 5000000, 5)) {
    Serial.println("Failed to mount SD_MMC");
    while (1) {}
  }
  //--------------------------

  //-----Camera---------------
  // dont forget to set tools -> PartitionOPI SRAM
  cameraSetup();

  //----- FOMO buffers (Edge Impulse) -----
  size_t snapshot_buf_size = (size_t)EI_CAMERA_RAW_FRAME_BUFFER_COLS * (size_t)EI_CAMERA_RAW_FRAME_BUFFER_ROWS * (size_t)EI_CAMERA_FRAME_BYTE_SIZE;
  snapshot_buf = (uint8_t *)ps_malloc(snapshot_buf_size);
  if (!snapshot_buf) snapshot_buf = (uint8_t *)malloc(snapshot_buf_size);
  if (!snapshot_buf) {
    Serial.println("ERR: Failed to allocate snapshot_buf for EI");
    while (true) delay(1000);
  }

  size_t crop_buf_size = (size_t)CROP_SIZE * (size_t)CROP_SIZE * 3;
  crop_buf = (uint8_t *)ps_malloc(crop_buf_size);
  if (!crop_buf) crop_buf = (uint8_t *)malloc(crop_buf_size);
  if (!crop_buf) {
    Serial.println("ERR: Failed to allocate crop_buf for EI");
    while (true) delay(1000);
  }
  //--------------------------------------

  delay(300);
  Serial.println("READY");
  Serial.println("Time not set yet. Use /setTime.");
}

void loop() {
  if (system_reset) {
    ESP.restart();
  }

#if OTA_ENABLE
  ArduinoOTA.handle();
#endif

  if((millis() - last_wifi_check_ms) > wifi_check_interval_ms){
    if (WiFi.status() != WL_CONNECTED) {
      Serial.println("WiFi lost, reconnecting...");
      WiFi.disconnect();
      WiFi.begin(ssid, password);
    }
    last_wifi_check_ms = millis();
  }

  if (have_real_time) {  // Wait until real time is set
    updateCurrentTime();
    if (!have_current_tar_file) {
      manageTarFiles();
      Serial.println("Current TAR file is set!");
    } else {
      if (current_time.hour == current_day_hour && last_check_hour == previous_day_hour) {
        Serial.println("Congratulations! You survived another day.");
        finalizeTarFile(current_tar_file_name);
        have_current_tar_file = false;
        manageTarFiles();
      }
      last_check_hour = current_time.hour;

      if (operational && have_current_tar_file) {
        if (millis() - last_infer_ms < infer_interval_ms) {
          ledc_set_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_1, LED_PWM);
          ledc_update_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_1);
          return;
        }
        last_infer_ms = millis();

        ledc_set_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_1, LED_PWM);
        ledc_update_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_1);

        if (xSemaphoreTake(camera_mutex, 500 / portTICK_PERIOD_MS) != pdTRUE) {
          Serial.println("Camera busy (mutex timeout)");
          return;
        }

        camera_fb_t *fb = esp_camera_fb_get();
        if (!fb) {
          Serial.println("Failed to capture frame");
          xSemaphoreGive(camera_mutex);
          return;
        }

        bool ok = run_fomo_on_jpeg_frame(fb);
        bool centered = ok && bee_is_centered(80);
        // //320 ± 30 → [290, 350]
        // //240 ± 30 → [210, 270]
        // //idealno 320,240?
        // Save only when entering center zone
        if (centered && !was_centered) {
          Serial.println("Bee centered -> saving JPEG into TAR");
          writeImageToTarFile(fb);
        }
        was_centered = centered;

        esp_camera_fb_return(fb);
        xSemaphoreGive(camera_mutex);

      } else {
        was_centered = false;
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

// ============================================================================
// Web server functions
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
  resp["year"] = current_time.year;
  resp["month"] = current_time.month;
  resp["day"] = current_time.day;
  resp["hour"] = current_time.hour;
  resp["minute"] = current_time.minute;
  resp["second"] = current_time.second;
  resp["millis"] = current_time.millis;
  xSemaphoreGive(time_mutex);

  String response;
  serializeJson(resp, response);
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

  File root = SD_MMC.open("/");
  if (!root || !root.isDirectory()) {
    request->send(500, "text/plain", "System failed to access SD card.");
    return;
  }

  AsyncResponseStream *response = request->beginResponseStream("application/json");
  response->print("[");

  bool first = true;
  File file = root.openNextFile();

  while (file) {
    if (!file.isDirectory()) {
      String name = file.name();
      if (name.startsWith("/")) {
        name = name.substring(1);
      }

      if (name.endsWith(".tar")) {
        if (!first) {
          response->print(",");
        }
        response->print("\"");
        response->print(name);
        response->print("\"");
        first = false;
      }
    }

    file.close();
    file = root.openNextFile();
  }

  root.close();
  response->print("]");
  request->send(response);
}

void handleGetFile(AsyncWebServerRequest *request) {
  if (operational) {
    request->send(403, "text/plain", "System is RUNNING. Cannot send file. Optionally STOP the system and try again.");
    return;
  }

  if (!request->hasParam("file_name")) {
    request->send(400, "text/plain", "Missing file name.");
    return;
  }

  String file_name = request->getParam("file_name")->value();

  if (!file_name.endsWith(".tar") || file_name.indexOf("..") != -1 || file_name.indexOf('/') != -1) {
    request->send(400, "text/plain", "Invalid file name.");
    return;
  }

  bool file_found = false;

  File root = SD_MMC.open("/");
  if (!root) {
    request->send(500, "text/plain", "Failed to access SD card.");
    return;
  }

  File file = root.openNextFile();
  while (file) {
    if (!file.isDirectory()) {
      String name = file.name();
      if (name.startsWith("/")) name = name.substring(1);

      if (name == file_name) {
        file_found = true;
      }
    }
    file = root.openNextFile();
  }
  root.close();


  if (!file_found) {
    request->send(404, "text/plain", "File on SD card not found.");
    return;
  }

  if (current_tar_file_name == file_name) {
    finalizeTarFile(current_tar_file_name);
  }

  AsyncWebServerResponse *response = request->beginResponse(SD_MMC, "/" + file_name, "application/x-tar");
  response->addHeader("Content-Disposition", "attachment; filename=\"" + file_name + "\"");
  response->addHeader("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0");
  response->addHeader("Pragma", "no-cache");
  response->addHeader("Expires", "0");

  request->send(response);

  if (current_tar_file_name == file_name) {
    unfinalizeTarFile(current_tar_file_name);
  }
}

void handleGetImage(AsyncWebServerRequest *request) {
  if (!operational) {
    captureAndGETSendImage(request);
  } else {
    request->send(403, "text/plain", "System is RUNNING. Cannot capture snapshot. Optionally STOP the system and try again.");
  }
}

void handleStart(AsyncWebServerRequest *request) {
  operational = true;
  was_centered = false;

  DynamicJsonDocument resp(256);
  resp["status"] = "ok";
  String response;
  serializeJson(resp, response);
  request->send(200, "application/json", response);
}

void handleStop(AsyncWebServerRequest *request) {
  operational = false;
  was_centered = false;

  ledc_set_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_1, 0);
  ledc_update_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_1);

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

// ============================================================================
// SD / TAR functions
// ============================================================================

void manageTarFiles() {
  updateTarFileStats();
  finalizeAllTarFiles();
  if (!have_current_tar_file) {
    createTarFile();
    tar_file_count++;
  } else if (isTarFileFinalized(current_tar_file_name)) {
    unfinalizeTarFile(current_tar_file_name);
  }
  while (tar_file_count > max_tar_file_count) {
    deleteTarFile(oldest_tar_file_name);
    updateTarFileStats();
  }
}

void updateTarFileStats() {
  tar_file_count = 0;
  oldest_tar_file_name = "";
  current_tar_file_name = "";
  have_current_tar_file = false;

  File root = SD_MMC.open("/");
  if (!root) {
    Serial.println("Failed to access SD card.");
    return;
  }

  char file_name[128];
  xSemaphoreTake(time_mutex, portMAX_DELAY);
  snprintf(file_name, sizeof(file_name), "%s_VVD_%04d_%02d_%02d.tar", BEEHIVE_ID, current_time.year, current_time.month, current_time.day);
  xSemaphoreGive(time_mutex);

  File file = root.openNextFile();
  while (file) {
    if (!file.isDirectory()) {
      String name = file.name();
      if (name.startsWith("/")) {
        name = name.substring(1);
      }

      if (name.endsWith(".tar")) {
        tar_file_count++;

        if (oldest_tar_file_name.isEmpty() || name < oldest_tar_file_name) {
          oldest_tar_file_name = name;
        }

        if ((name == file_name) && (!have_current_tar_file)) {
          have_current_tar_file = true;
          current_tar_file_name = name;
        }
      }
    }
    file = root.openNextFile();
  }
  root.close();
}

void finalizeAllTarFiles() {
  File root = SD_MMC.open("/");
  if (!root) {
    Serial.println("Failed to access SD card.");
    return;
  }

  char file_name[128];
  File file = root.openNextFile();
  while (file) {
    if (!file.isDirectory()) {
      String name = file.name();
      if (name.startsWith("/")) {
        name = name.substring(1);
      }

      if (name.endsWith(".tar") && !isTarFileFinalized(name) && (current_tar_file_name != name)) {
        finalizeTarFile(name);
      }
    }
    file = root.openNextFile();
  }
  root.close();
}

void deleteTarFile(String arg_file_name) {
  String path = "/" + arg_file_name;
  if (SD_MMC.remove(path.c_str())) {
    Serial.println("Deleted: " + path);
  } else {
    Serial.println("Failed to delete: " + path);
  }
}

void createTarFile() {
  xSemaphoreTake(time_mutex, portMAX_DELAY);
  current_tar_file_name = String(BEEHIVE_ID) + "_VVD_" + get_date_prefix(current_time) + ".tar";
  String name = "info.txt";
  String content = "Created on: " + get_iso_time(current_time) + "\n";
  xSemaphoreGive(time_mutex);

  String path = "/sdcard/" + current_tar_file_name;
  if (mtar_open(&tar, path.c_str(), "w") != MTAR_ESUCCESS) {
    Serial.println("Failed to create TAR file.");
    have_current_tar_file = false;
    return;
  }
  size_t content_length = content.length();
  mtar_write_file_header(&tar, name.c_str(), content_length);
  mtar_write_data(&tar, content.c_str(), content_length);

  mtar_close(&tar);
  have_current_tar_file = true;

  Serial.print("Created new TAR: ");
  Serial.println(current_tar_file_name);
}

void openTarFile(String arg_file_name) {
  String path = "/sdcard/" + arg_file_name;
  if (mtar_open(&tar, path.c_str(), "a") != MTAR_ESUCCESS) {
    Serial.println("Failed to open TAR file.");
    return;
  }
}

void closeTarFile() {
  if (mtar_close(&tar) != MTAR_ESUCCESS) {
    Serial.println("Failed to close TAR file.");
  }
}

void finalizeTarFile(String arg_file_name) {
  if (isTarFileFinalized(arg_file_name)) {
    Serial.println("TAR already finalized.");
    return;
  }
  openTarFile(arg_file_name);
  if (mtar_finalize(&tar) != MTAR_ESUCCESS) {
    Serial.println("Failed to finalize TAR file.");
  }
  closeTarFile();
  Serial.println("TAR finalized.");
}



void unfinalizeTarFile(String arg_file_name) {
  if (!isTarFileFinalized(arg_file_name)) {
    Serial.println("TAR already unfinalized.");
    return;
  }

  String path = "/" + arg_file_name;
  File f = SD_MMC.open(path.c_str(), FILE_READ);
  if (!f) {
    Serial.println("Failed to open TAR file.");
    return;
  }

  size_t size = f.size();
  f.close();

  if (size < 1024) {
    Serial.println("File too small to unfinalize.");
    return;
  }

  path = "/sdcard/" + arg_file_name;
  if (truncate(path.c_str(), size - 1024) != 0) {
    Serial.println("truncate() failed!");
    return;
  }

  Serial.println("TAR unfinalized.");
}

bool isTarFileFinalized(String arg_file_name) {
  String path = "/" + arg_file_name;
  File f = SD_MMC.open(path.c_str(), FILE_READ);
  if (!f) {
    Serial.println("Failed to open TAR file.");
    return false;
  }

  size_t size = f.size();

  if (size < 1024) {
    f.close();
    return false;
  }

  f.seek(size - 1024);

  for (int i = 0; i < 1024; i++) {
    if (f.read() != 0) {
      f.close();
      return false;
    }
  }

  f.close();
  return true;
}

void writeImageToTarFile(camera_fb_t *fb) {
  if (!have_current_tar_file) {
    Serial.println("Missing TAR file.");
    return;
  };

  openTarFile(current_tar_file_name);

  xSemaphoreTake(time_mutex, portMAX_DELAY);
  String image_name = String(BEEHIVE_ID) + "_VVD_" + get_iso_time(current_time) + ".jpg";
  xSemaphoreGive(time_mutex);

  if (mtar_write_file_header(&tar, image_name.c_str(), fb->len) != MTAR_ESUCCESS) {
    Serial.println("Failed to write image header.");
  } else if (mtar_write_data(&tar, fb->buf, fb->len) != MTAR_ESUCCESS) {
    Serial.println("Failed to write image data.");
  } else {
    Serial.println("Image written to TAR.");
  }

  closeTarFile();
}

// ============================================================================
// Camera functions
// ============================================================================

void cameraSetup() {
  camera_mutex = xSemaphoreCreateMutex();
  if (camera_mutex == NULL) {
    Serial.println("Failed to create camera mutex.");
  }

  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sscb_sda = SIOD_GPIO_NUM;
  config.pin_sscb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;

  config.xclk_freq_hz = 10000000;
  config.pixel_format = PIXFORMAT_JPEG;

  // Force VGA for FOMO detection
  config.frame_size = FRAMESIZE_VGA;
  config.jpeg_quality = psramFound() ? 4 : 12;
  //config.fb_count = psramFound() ? 2 : 1;

  config.fb_count = 2;
  config.grab_mode = CAMERA_GRAB_LATEST;

  if (esp_camera_init(&config) != ESP_OK) {
    Serial.println("Camera init failed");
    return;
  }
  Serial.println("Camera initialized");

  sensor_t *s = esp_camera_sensor_get();
  s->set_whitebal(s, 0);
  s->set_gain_ctrl(s, 0);
  s->set_exposure_ctrl(s, 0);
  s->set_aec_value(s, 100);
  s->set_agc_gain(s, 1);
  s->set_wb_mode(s, 1);
  s->set_saturation(s, 2);
  s->set_brightness(s, -2);
  s->set_contrast(s, 0);
  s->set_sharpness(s, 0);
}


void captureAndGETSendImage(AsyncWebServerRequest *request) {
  ledc_set_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_1, LED_PWM);
  ledc_update_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_1);
  delay(200);

  if (xSemaphoreTake(camera_mutex, 100 / portTICK_PERIOD_MS) != pdTRUE) {
    ledc_set_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_1, 0);
    ledc_update_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_1);
    request->send(503, "text/plain", "Camera busy");
    return;
  }

  camera_fb_t *fb = esp_camera_fb_get();
  if (!fb) {
    xSemaphoreGive(camera_mutex);
    ledc_set_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_1, 0);
    ledc_update_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_1);
    Serial.println("Failed to capture image.");
    request->send(500, "text/plain", "System failed to capture image.");
    return;
  }

  const size_t jpg_len = fb->len;

  uint8_t *jpg_copy = (uint8_t *)ps_malloc(jpg_len);
  if (!jpg_copy) {
    jpg_copy = (uint8_t *)malloc(jpg_len);
  }

  if (!jpg_copy) {
    esp_camera_fb_return(fb);
    xSemaphoreGive(camera_mutex);
    ledc_set_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_1, 0);
    ledc_update_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_1);
    Serial.println("Failed to allocate JPEG copy buffer.");
    request->send(500, "text/plain", "System out of memory.");
    return;
  }

  memcpy(jpg_copy, fb->buf, jpg_len);

  esp_camera_fb_return(fb);
  xSemaphoreGive(camera_mutex);

  ledc_set_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_1, 0);
  ledc_update_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_1);

  AsyncWebServerResponse *response = request->beginResponse(
    "image/jpeg",
    jpg_len,
    [jpg_copy, jpg_len](uint8_t *buffer, size_t maxLen, size_t index) mutable -> size_t {
      if (index >= jpg_len) {
        if (jpg_copy) {
          free(jpg_copy);
          jpg_copy = nullptr;
        }
        return 0;
      }

      size_t to_copy = jpg_len - index;
      if (to_copy > maxLen) {
        to_copy = maxLen;
      }

      memcpy(buffer, jpg_copy + index, to_copy);

      if (index + to_copy >= jpg_len) {
        free(jpg_copy);
        jpg_copy = nullptr;
      }

      return to_copy;
    });

  response->addHeader("Content-Disposition", "inline; filename=capture.jpg");
  response->addHeader("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0");
  response->addHeader("Pragma", "no-cache");
  response->addHeader("Expires", "0");

  request->send(response);
}


// ============================================================================
// FOMO / Edge Impulse functions
// ============================================================================

static bool bee_is_centered(int tol_px) {
  if (object_X < 0 || object_Y < 0) return false;

  const int roi_cx = CROP_X0 + (CROP_SIZE / 2);
  const int roi_cy = CROP_Y0 + (CROP_SIZE / 2);

  return (abs(object_X - roi_cx) <= tol_px) && (abs(object_Y - roi_cy) <= tol_px + 10);
}

// Provide RGB888 data to Edge Impulse
static int ei_camera_get_data(size_t offset, size_t length, float *out_ptr) {
  size_t pixel_ix = offset * 3;
  size_t pixels_left = length;
  size_t out_ptr_ix = 0;

  while (pixels_left--) {
    uint32_t r = snapshot_buf[pixel_ix + 0];
    uint32_t g = snapshot_buf[pixel_ix + 1];
    uint32_t b = snapshot_buf[pixel_ix + 2];
    out_ptr[out_ptr_ix++] = (float)((r << 16) | (g << 8) | b);
    pixel_ix += 3;
  }
  return 0;
}

static void crop_rgb888(const uint8_t *src, uint8_t *dst,
                        int src_w, int src_h,
                        int x0, int y0,
                        int crop_w, int crop_h) {
  (void)src_h;
  for (int y = 0; y < crop_h; y++) {
    const uint8_t *src_row = src + ((y + y0) * src_w + x0) * 3;
    uint8_t *dst_row = dst + (y * crop_w * 3);
    memcpy(dst_row, src_row, crop_w * 3);
  }
}

bool run_fomo_on_jpeg_frame(camera_fb_t *fb) {
  if (!fb || !snapshot_buf || !crop_buf) return false;


  if (fb->width != EI_CAMERA_RAW_FRAME_BUFFER_COLS || fb->height != EI_CAMERA_RAW_FRAME_BUFFER_ROWS) {
    Serial.printf("ERR: Unexpected frame size %dx%d (expected %dx%d)\n",
                  fb->width, fb->height,
                  EI_CAMERA_RAW_FRAME_BUFFER_COLS, EI_CAMERA_RAW_FRAME_BUFFER_ROWS);
    object_X = -1;
    object_Y = -1;
    return false;
  }


  bool converted = fmt2rgb888(fb->buf, fb->len, PIXFORMAT_JPEG, snapshot_buf);
  if (!converted) {
    Serial.println("Conversion to RGB888 failed");
    object_X = -1;
    object_Y = -1;
    return false;
  }

  // Crop ROI then resize to model input
  bool do_resize =
    (EI_CLASSIFIER_INPUT_WIDTH != EI_CAMERA_RAW_FRAME_BUFFER_COLS) || (EI_CLASSIFIER_INPUT_HEIGHT != EI_CAMERA_RAW_FRAME_BUFFER_ROWS);

  if (do_resize) {
    crop_rgb888(snapshot_buf, crop_buf,
                EI_CAMERA_RAW_FRAME_BUFFER_COLS,
                EI_CAMERA_RAW_FRAME_BUFFER_ROWS,
                CROP_X0, CROP_Y0,
                CROP_SIZE, CROP_SIZE);

    ei::image::processing::resize_image(
      crop_buf,
      CROP_SIZE, CROP_SIZE,
      snapshot_buf,
      EI_CLASSIFIER_INPUT_WIDTH,
      EI_CLASSIFIER_INPUT_HEIGHT,
      3);
  }

  ei::signal_t signal;
  signal.total_length = EI_CLASSIFIER_DSP_INPUT_FRAME_SIZE;
  signal.get_data = &ei_camera_get_data;

  ei_impulse_result_t result = { 0 };
  EI_IMPULSE_ERROR err = run_classifier(&signal, &result, debug_nn);
  if (err != EI_IMPULSE_OK) {
    Serial.printf("ERR: Failed to run classifier (%d)\n", err);
    object_X = -1;
    object_Y = -1;
    return false;
  }

#if EI_CLASSIFIER_OBJECT_DETECTION == 1
  bool bb_found = false;
  ei_impulse_result_bounding_box_t *best_bb = nullptr;
  float best_value = 0.0f;

  for (size_t ix = 0; ix < result.bounding_boxes_count; ix++) {
    auto &bb = result.bounding_boxes[ix];
    //if (bb.value == 0) continue;
    if (bb.value < CONFIDENCE_THRESHOLD) continue;
    if (!bb_found || bb.value > best_value) {
      best_bb = &bb;
      best_value = bb.value;
      bb_found = true;
    }
  }

  if (bb_found && best_bb != nullptr) {
    int cx_model = best_bb->x + best_bb->width / 2;
    int cy_model = best_bb->y + best_bb->height / 2;

    int x_crop = cx_model * CROP_SIZE / EI_CLASSIFIER_INPUT_WIDTH;
    int y_crop = cy_model * CROP_SIZE / EI_CLASSIFIER_INPUT_HEIGHT;

    object_X = x_crop + CROP_X0;
    object_Y = y_crop + CROP_Y0;

    Serial.printf("FOMO: %s (%.2f) center=(%d,%d)\n",
                  best_bb->label, best_bb->value, object_X, object_Y);
  } else {
    object_X = -1;
    object_Y = -1;
  }
  return true;
#else
  object_X = -1;
  object_Y = -1;
  return true;
#endif
}
