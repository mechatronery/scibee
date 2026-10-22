# SCIBee Entrance System

## Description

The SCIBee Entrance System monitors bee traffic at a beehive entrance, helping beekeepers assess colony activity and identify potential health issues. Seventeen entrance tunnels monitor bee movement, while a motorized mechanism adjusts the entrance opening.

A central Beetle ESP32-C3 controller collects bee movement measurements and records them in a daily CSV file with UTC timestamps. Each file is named using the UTC date.

The middle corridor is equipped with an ESP32-S3-EYE camera module. An AI model running on the ESP32-S3-EYE detects bee presence and determines when to capture images. Captured images are appended throughout the day to a TAR archive stored on a microSD card. A new archive is created each day and named using the UTC date. The images can subsequently be analyzed to identify potential parasites, particularly Varroa mites.

Both ESP32 boards host their own Wi-Fi web interfaces, providing access to monitoring data and manual control through locally hosted web pages. The interfaces also support programmatic access by other applications.

## System Overview

- **Bee movement monitoring:** Infrared sensors detect bee movement through 17 entrance tunnels.
- **Data acquisition:** ATtiny414-based corridor PCBs communicate with the ESP32-C3 controller over I²C.
- **Data logging:** Bee movement measurements are recorded every minute with UTC timestamps in daily CSV files.
- **Image capture:** The ESP32-S3-EYE runs AI inference to detect bee presence and trigger image capture in the middle corridor.
- **Image storage:** Captured images are stored in a daily TAR archive on a microSD card.
- **Connectivity:** The ESP32-C3 and ESP32-S3-EYE each provide a Wi-Fi web interface.
- **Entrance control:** Two DC geared motors actuate the adjustable entrance doors.
- **Power supply:** A 12 V lead-acid battery supplies the system. An SY8205 step-down regulator provides a 5 V supply.
- **Mechanical design:** The enclosure is 3D-printed in PETG and assembled using steel fasteners, M3 threaded inserts, and silicone components. A transparent protective foil protects the camera.
- **Design files:** The mechanical assembly is designed in FreeCAD, and the electronics are designed in KiCad.
- **Overall dimensions:** Approximately 400 × 140 × 70 mm.

## System Architecture

The diagram shows the main subsystems and their communication links.

```mermaid
graph TD
    MAIN["Main Control System (Beetle ESP32-C3)"]
    CAM["Camera System (ESP32-S3-EYE)"]

    AP["Wi-Fi Access Point"]
    AP <-->|Wi-Fi| MAIN
    AP <-->|Wi-Fi| CAM

    MAIN -->|I²C| COR["17-Tunnel Corridor Array"]
    MAIN --> DOOR["Automated Entrance Doors"]

    classDef control fill:#e3f2fd,stroke:#1565c0,color:#0d47a1,stroke-width:2px;
    classDef camera fill:#f3e5f5,stroke:#7b1fa2,color:#4a148c,stroke-width:2px;
    classDef subsystem fill:#fff8e1,stroke:#f57f17,color:#e65100,stroke-width:2px;
    classDef network fill:#e0f7fa,stroke:#00838f,color:#006064,stroke-width:2px;

    class MAIN control;
    class CAM camera;
    class COR,DOOR subsystem;
    class AP network;
```

## Electrical Overview

The diagram summarizes the power distribution, controller connections, storage interface, and motor control paths.

```mermaid
graph TD
    %% Color palette
    classDef power fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#b71c1c;
    classDef logic fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#0d47a1;
    classDef output fill:#fff8e1,stroke:#f57f17,stroke-width:2px,color:#e65100;
    classDef external fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#1b5e20;

    %% Power supply
    BAT["12 V Battery"]:::power
    REG["SY8205 Buck Regulator"]:::power
    USB["5 V Output / USB"]:::power

    %% Main controller and peripherals
    ESP32["Beetle ESP32-C3"]:::logic
    DRV1["DRV8871 Motor Driver L"]:::logic
    DRV2["DRV8871 Motor Driver R"]:::logic
    SD["microSD SPI Breakout"]:::logic
    I2C["I²C Connection"]:::logic

    %% Outputs
    MOT1["DC Geared Motor L"]:::output
    MOT2["DC Geared Motor R"]:::output

    %% External modules
    CARD["microSD Card"]:::external
    EYE["ESP32-S3-EYE Camera"]:::external
    SENSOR["17-Tunnel Entrance Array<br/>ATtiny414 Sensor PCBs"]:::external

    %% Power distribution
    BAT ==>|12 V| REG
    BAT ==>|Motor supply| DRV1
    BAT ==>|Motor supply| DRV2
    REG ==>|5 V| ESP32
    REG ==>|5 V| SD
    REG ==>|5 V| USB
    USB ==>|5 V| EYE

    %% Control and data
    ESP32 -->|Motor control| DRV1
    ESP32 -->|Motor control| DRV2
    ESP32 <-->|SPI| SD
    ESP32 <-->|I²C| I2C
    I2C <-->|I²C| SENSOR
    SD <-->|Storage| CARD

    %% Motor outputs
    DRV1 ==>|Motor output| MOT1
    DRV2 ==>|Motor output| MOT2
```

## Bill of Materials (BOM)

### 1. Main Structure

| Index | Name                              | Qty | 3D printed |
| ----- | --------------------------------- | ---:|:----------:|
| 1.1   | Main (printed in 2 parts)         | 1   | ✓          |
| 1.2   | Top (printed in 2 parts)          | 1   | ✓          |
| 1.3   | Bottom (Bot) (printed in 2 parts) | 1   | ✓          |
| 1.4   | Top buttons                       | 4   | ✓          |

### 2. Main Control Electronics

| Index | Name                               | Qty | 3D printed |
| ----- | ---------------------------------- | ---:|:----------:|
| 2.1   | Beetle ESP32-C3                    | 1   | ✗          |
| 2.2   | microSD SPI breakout               | 1   | ✗          |
| 2.3   | microSD card                       | 1   | ✗          |
| 2.4   | SY8205 step-down voltage regulator | 1   | ✗          |
| 2.5   | DRV8871 DC motor controller        | 2   | ✗          |
| 2.6   | Main control base foil             | 1   | ✗          |
| 2.7   | Main water wall                    | 1   | ✓          |
| 2.8   | Wire anchor                        | 1   | ✗          |

### 3. Door System

| Index | Name                        | Qty | 3D printed |
| ----- | --------------------------- | ---:|:----------:|
| 3.1   | Door (printed in 2 parts)   | 1   | ✓          |
| 3.2   | Slider (printed in 2 parts) | 1   | ✓          |
| 3.3   | PZ22GR9120R DC geared motor | 2   | ✗          |
| 3.4   | Gear 1                      | 1   | ✓          |
| 3.5   | Gear 2                      | 1   | ✓          |
| 3.6   | Motor cap 1                 | 1   | ✓          |
| 3.7   | Motor cap 2                 | 1   | ✓          |

### 4. Camera and Image Capture System

| Index | Name                               | Qty | 3D printed |
| ----- | ---------------------------------- | ---:|:----------:|
| 4.1   | ESP32-S3-EYE camera module         | 1   | ✗          |
| 4.2   | Black camera cone                  | 1   | ✓          |
| 4.3   | Bottom cap                         | 1   | ✓          |
| 4.4   | Circular LED array                 | 1   | ✗          |
| 4.5   | Bottom grille                      | 1   | ✓          |
| 4.6   | Transparent camera protective foil | 1   | ✗          |

### 5. Corridor Array

The system contains 17 assembled entrance tunnels built around 18 corridor PCBs. Each tunnel's operation is based on two sequential PCBs, with adjacent tunnels sharing a PCB.

| Index | Name                               | Qty | 3D printed |
| ----- | ---------------------------------- | ---:|:----------:|
| 5.1   | Corridor PCBs (complete boards)    | 18  | ✗          |
| 5.2   | Big side                           | 16  | ✓          |
| 5.3   | Small side                         | 16  | ✓          |
| 5.4   | Big white side                     | 1   | ✓          |
| 5.5   | Small white side                   | 1   | ✓          |
| 5.6   | Glass window                       | 1   | ✗          |
| 5.7   | SSQ-106-03-L-S corridor connectors | 18  | ✗          |

### 6. Fasteners and Inserts

| Index | Name                  | Qty |
| ----- | --------------------- | ---:|
| 6.1   | M3 × 8 screws         | 20  |
| 6.2   | M3 × 16 screws        | 2   |
| 6.3   | M3 washers            | 18  |
| 6.4   | M3 nuts               | 4   |
| 6.5   | M3 × 30 threaded rods | 11  |
| 6.6   | M3 threaded inserts   | 14  |
| 6.7   | M4 × 30 screws        | 2   |
| 6.8   | M4 washers            | 2   |
