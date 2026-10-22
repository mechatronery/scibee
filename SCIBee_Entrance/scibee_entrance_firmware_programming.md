# SCIBee Entrance and Camera — Firmware Programming

## Overview

This document describes how to configure Arduino IDE 2 and upload firmware to the ESP32-based SCIBee devices.

Two firmware targets are supported:

- **Entrance counter:** Beetle ESP32-C3, using `scibee_entrance_counter.ino`.
- **Camera:** ESP32-S3-EYE, using `scibee_entrance_camera.ino` and an Edge Impulse inference library.

Both devices use Wi-Fi for network communication and LittleFS to store web interface resources.

## Development Environment

### Arduino IDE

Install **Arduino IDE 2** and configure the ESP32 development environment:

1. Open **Tools → Board → Boards Manager**.
2. Install **esp32 by Espressif Systems**.

### Required Libraries

Install the following libraries through **Sketch → Include Library → Manage Libraries**:

| Library             | Author          |
| ------------------- | --------------- |
| Arduino_ESP32_OTA   | Arduino         |
| Async TCP           | ESP32Async      |
| ESP Async WebServer | ESP32Async      |
| ArduinoJson         | Benoit Blanchon |
| SdFat               | Bill Greiman    |

The camera additionally requires the Edge Impulse inference library described in the camera section.

### LittleFS Upload Plugin

Install the [Arduino LittleFS Upload plugin](https://github.com/earlephilhower/arduino-littlefs-upload):

1. Download the plugin's VSIX file.

2. Copy it into the Arduino IDE plugins directory:
   
   - **macOS/Linux:** `~/.arduinoIDE/plugins/`
   
   - **Windows:** `C:\Users\<username>\.arduinoIDE\plugins\`

3. Create the directory if it does not exist.

4. Restart Arduino IDE.

The plugin uploads web interface resources from the firmware project's `data` directory to LittleFS.

## Camera — ESP32-S3-EYE

**Program:** `scibee_entrance_camera.ino`

### AI Inference Library

Install the Edge Impulse inference library:

1. Select **Sketch → Include Library → Add .ZIP Library...**.
2. Select `ei-varroa-arduino-1.0.4.zip`.
3. Open `src/edge-impulse-sdk/classifier/ei_classifier_config.h` in the installed library.
4. Set the following flag to `0`:

```cpp
#define EI_CLASSIFIER_TFLITE_ENABLE_ESP_NN 0
```

### Board Configuration

Open `scibee_entrance_camera.ino` and configure the following options under **Tools**:

| Setting                              | Value                                    |
| ------------------------------------ | ---------------------------------------- |
| Board                                | `ESP32S3 Dev Module`                     |
| USB CDC On Boot                      | `Enabled`                                |
| CPU Frequency                        | `160MHz`                                 |
| Erase All Flash Before Sketch Upload | `Disabled`                               |
| Partition Scheme                     | `8M with spiffs`                         |
| Flash Size                           | `8M`, if available as a separate setting |
| PSRAM                                | `OPI PSRAM`                              |

Select **Sketch → Verify/Compile** and install any additional missing libraries reported by the compiler.

### Firmware Upload

1. Update the beehive ID, IP address, subnet, Wi-Fi SSID, and password in `scibee_entrance_camera.ino`.

2. Connect the ESP32-S3-EYE to the computer using a USB cable.

3. Select **Sketch → Upload** and wait for completion.

4. Upload the web interface resources:
   
   - Open the command palette using `Ctrl + Shift + P` (Windows/Linux) or `Cmd + Shift + P` (macOS).
   
   - Select **Upload LittleFS to Pico/ESP8266/ESP32**.
   
   - Wait for the filesystem upload to complete.

## Entrance Counter — Beetle ESP32-C3

**Program:** `scibee_entrance_counter.ino`

### Board Configuration

Open `scibee_entrance_counter.ino` and configure the following options under **Tools**:

| Setting                              | Value                |
| ------------------------------------ | -------------------- |
| Board                                | `ESP32C3 Dev Module` |
| USB CDC On Boot                      | `Enabled`            |
| CPU Frequency                        | `160MHz`             |
| Erase All Flash Before Sketch Upload | `Disabled`           |

Select **Sketch → Verify/Compile** and install any additional missing libraries reported by the compiler.

### Firmware Upload

1. Update the beehive ID, IP address, subnet, Wi-Fi SSID, and password in `scibee_entrance_counter.ino`.

2. Connect the Beetle ESP32-C3 to the computer using a USB cable.

3. Select **Sketch → Upload** and wait for completion.

4. Upload the web interface resources:
   
   - Open the command palette using `Ctrl + Shift + P` (Windows/Linux) or `Cmd + Shift + P` (macOS).
   
   - Select **Upload LittleFS to Pico/ESP8266/ESP32**.
   
   - Wait for the filesystem upload to complete.

## Network Configuration

Before compiling each device's firmware, verify the device-specific configuration:

| Parameter      | Description                                  |
| -------------- | -------------------------------------------- |
| Beehive ID     | Identifier assigned to the device or beehive |
| IP address     | Static IP address assigned to the device     |
| Subnet         | Network subnet configuration                 |
| Wi-Fi SSID     | Name of the Wi-Fi network                    |
| Wi-Fi password | Password for the Wi-Fi network               |

Ensure that the configured IP address is unique and compatible with the installation network. Use the correct Wi-Fi credentials for the deployment location.

## Programming Checklist

Before deploying a device, verify the following:

- Correct firmware sketch selected.
- Correct ESP32 board and board settings selected.
- Beehive ID and network settings updated.
- LittleFS web interface resources uploaded successfully.
- Device connectivity and web interface verified.

**Important:** Firmware and LittleFS resources are uploaded separately. Upload both whenever deploying an updated firmware and its corresponding web interface.
