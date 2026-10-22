# SCIBee Edge — Raspberry Pi Setup

## Overview

This document describes the SCIBee edge configuration using a Raspberry Pi Zero 2 W and Raspberry Pi 5. The Zero 2 W provides local device connectivity and controller functionality, while the Pi 5 hosts the local Qwen3-4B inference server using `llama.cpp` and OpenAgri services.

The setup covers Raspberry Pi OS, Wi-Fi connectivity, Docker, local AI inference, I²C, system time permissions, and the base controller service.

**Note:** Replace example credentials and device addresses with deployment-specific values.

## 1. Raspberry Pi OS Installation

1. Download the Raspberry Pi Imager AppImage from the [official GitHub releases](https://github.com/raspberrypi/rpi-imager/releases). 

2. Make it executable and launch it:
   
   ```bash
   chmod +x rpi-imager-*.AppImage./rpi-imager-*.AppImage
   ```

3. Select the appropriate Pi model and SD card.

4. Choose **Raspberry Pi OS (other) → Raspberry Pi OS Lite (64-bit)**.

5. Configure the hostname, locale, username, password, Wi-Fi credentials, and SSH access.

6. Write the image to the SD card.

## 2. Initial Access

Boot the Pi and connect the administration PC to the same network.

Discover available devices:

```bash
nmap -sn 192.168.4.1-254
```

Connect over SSH using the address reported by the scan:

```bash
ssh scibee@<PI_IP>
```

Replace `<PI_IP>` with the actual address.

Inspect the system and available disk space:

```bash
cat /etc/debian_version
cat /etc/os-release
df -h
```

Update the operating system:

```bash
sudo apt update
apt list --upgradable
sudo apt full-upgrade
sudo apt autoremove
sudo apt clean
```

Review package changes before confirming the upgrade.

## 3. Wi-Fi Configuration

Each edge device should use the Wi-Fi network assigned to its deployment. The example below uses `SCIBee_A` and subnet `192.168.1.0/24`.

**Subnet convention:**

- `SCIBee_A`: `192.168.1.0/24`
- `SCIBee_B`: `192.168.2.0/24`

Keep each deployment's addresses, gateway, and subnet consistent.

### Raspberry Pi Zero 2 W — Configure a hotspot

The Zero 2 W can provide a local access point for ESP32 devices and other edge hardware.

Create the hotspot:

```bash
sudo nmcli connection add con-name hotspot \
  ifname wlan0 type wifi ssid "SCIBee_A" \
  autoconnect no

sudo nmcli connection modify hotspot \
  wifi-sec.key-mgmt wpa-psk \
  wifi-sec.psk "<WIFI_PASSWORD>"

sudo nmcli connection modify hotspot \
  802-11-wireless.mode ap \
  802-11-wireless.band bg \
  ipv4.method shared \
  ipv4.addresses 192.168.1.1/24 \
  ipv4.shared-dhcp-range 192.168.1.2,192.168.1.99
```

Configure connection priorities:

```bash
# Prefer the normal router connection.
sudo nmcli connection modify netplan-wlan0-SCIBee \
  connection.autoconnect yes \
  connection.autoconnect-priority 100

# Allow the hotspot to start as a fallback.
sudo nmcli connection modify hotspot \
  connection.autoconnect yes \
  connection.autoconnect-priority 10

nmcli -f NAME,AUTOCONNECT,AUTOCONNECT-PRIORITY connection show
```

Activate the hotspot:

```bash
sudo nmcli connection up hotspot
```

Connect the administration PC to `SCIBee_A` and access the Pi:

```bash
ssh scibee@192.168.1.1
```

### ESP32 Wi-Fi compatibility

For the ESP32 Wi-Fi compatible implementation, configure WPA2/CCMP security:

```bash
sudo nmcli connection modify hotspot \
  802-11-wireless-security.key-mgmt wpa-psk \
  802-11-wireless-security.proto rsn \
  802-11-wireless-security.pairwise ccmp \
  802-11-wireless-security.group ccmp \
  802-11-wireless-security.pmf disable
```

Restart the hotspot:

```bash
sudo nmcli connection down hotspot
sudo nmcli connection up hotspot
```

Inspect connected stations:

```bash
sudo iw dev wlan0 station dump
```

### Raspberry Pi 5 — Connect to the edge network

Discover the Pi 5 on the existing network:

```bash
nmap -sn 192.168.1.1-254
ssh scibee@<PI5_IP>
```

If the Pi does not boot, check its power supply and status indicators.

Check and update the EEPROM if required:

```bash
sudo rpi-eeprom-update
```

Apply an EEPROM update only when needed, following the official Raspberry Pi instructions:

```bash
sudo rpi-eeprom-update -a
sudo reboot
```

Create a NetworkManager Wi-Fi profile:

```bash
sudo nmcli connection add type wifi \
  ifname wlan0 \
  con-name "netplan-wlan0-SCIBee_A" \
  ssid "SCIBee_A"

sudo nmcli connection modify "netplan-wlan0-SCIBee_A" \
  wifi-sec.key-mgmt wpa-psk \
  wifi-sec.psk "<WIFI_PASSWORD>"
```

Configure automatic connection priorities. The example assumes the existing router profile is named `netplan-wlan0-SCIBee`.

```bash
# Prefer the existing router network.
sudo nmcli connection modify "netplan-wlan0-SCIBee" \
  connection.autoconnect yes \
  connection.autoconnect-priority 100

# Use the edge network as a lower-priority connection.
sudo nmcli connection modify "netplan-wlan0-SCIBee_A" \
  connection.autoconnect yes \
  connection.autoconnect-priority 10
```

Inspect connection profiles:

```bash
nmcli connection show
nmcli -f NAME,AUTOCONNECT,AUTOCONNECT-PRIORITY connection show
```

### Assign a static IP to the Pi 5

Use a reserved address appropriate for the network. The example assigns `192.168.1.222`:

```bash
sudo nmcli connection modify "netplan-wlan0-SCIBee_A" \
  ipv4.method manual \
  ipv4.addresses 192.168.1.222/24 \
  ipv4.gateway 192.168.1.1 \
  ipv4.dns "192.168.1.1"
```

The gateway and DNS addresses must match the actual network configuration. Ensure that the chosen static address is excluded from the DHCP pool or reserved for the Pi.

Verify the configuration:

```bash
nmcli connection show "netplan-wlan0-SCIBee_A" |
  grep -E 'ipv4.method|ipv4.addresses|ipv4.gateway|ipv4.dns'
```

Activate the profile when it is safe to change the current network connection:

```bash
sudo nmcli connection up "netplan-wlan0-SCIBee_A"
```

## 4. Docker on Raspberry Pi 5

Install and enable Docker:

```bash
sudo apt update
sudo apt install -y docker.io
sudo systemctl enable --now docker
sudo systemctl status docker --no-pager
```

Verify the installation:

```bash
sudo docker run --rm hello-world
sudo systemctl is-active docker
docker compose version
```

## 5. Raspberry Pi 5 — Local AI Inference

The Pi 5 runs Qwen3-4B locally using `llama.cpp`. The inference server exposes an OpenAI-compatible API on port `8090`, bound to localhost.

### Install dependencies

Create the project directories:

```bash
mkdir -p ~/cloud/ai/qwen/models
cd ~/cloud/ai/qwen
```

Install build dependencies:

```bash
sudo apt update
sudo apt install -y git cmake build-essential libssl-dev curl
```

Verify the tools:

```bash
git --version
cmake --version
g++ --version
```

### Build llama.cpp

Clone the repository and compile the CLI and server:

```bash
cd ~/cloud/ai/qwen

git clone https://github.com/ggml-org/llama.cpp.git
cd llama.cpp

cmake -B build -DLLAMA_OPENSSL=ON
cmake --build build -j"$(nproc)" --target llama-cli llama-server
```

Verify the binaries:

```bash
ls -lh build/bin/llama-cli build/bin/llama-server
```

### Download the model

Download the Qwen3-4B GGUF model using Q4_K_M quantization:

```bash
cd ~/cloud/ai/qwen/models

../llama.cpp/build/bin/llama-cli \
  -hf Qwen/Qwen3-4B-GGUF:Q4_K_M
```

Inspect the Hugging Face cache:

```bash
ls -lh ~/.cache/huggingface/hub/models--Qwen--Qwen3-4B-GGUF/blobs/
```

Copy the actual downloaded GGUF file into the project directory. Identify the correct model blob instead of relying on a fixed cache hash:

```bash
cp /path/to/downloaded-model.gguf \
  ~/cloud/ai/qwen/models/Qwen3-4B-Q4_K_M.gguf
```

Verify the destination:

```bash
ls -lh ~/cloud/ai/qwen/models/Qwen3-4B-Q4_K_M.gguf
```

### Test the inference server

Start the server manually:

```bash
cd ~/cloud/ai/qwen/llama.cpp

./build/bin/llama-server \
  -m ../models/Qwen3-4B-Q4_K_M.gguf \
  --host 127.0.0.1 \
  --port 8090 \
  -t 1 \
  -c 4096 \
  -b 64 \
  --temp 0.3 \
  --top-p 0.9
```

The example uses one CPU thread, a 4096-token context, and batch size 64. Adjust these settings based on memory usage, latency, and throughput.

In another terminal, check the health endpoint:

```bash
curl http://127.0.0.1:8090/health
```

Stop the manually started server with `Ctrl+C` before enabling the systemd service.

### Configure automatic startup

Create the service file:

```bash
sudo nano /etc/systemd/system/llama-qwen.service
```

Add:

```ini
[Unit]
Description=SCIBee Qwen3-4B llama.cpp Server
After=network.target

[Service]
Type=simple
User=scibee
WorkingDirectory=/home/scibee/cloud/ai/qwen/llama.cpp
ExecStart=/home/scibee/cloud/ai/qwen/llama.cpp/build/bin/llama-server -m /home/scibee/cloud/ai/qwen/models/Qwen3-4B-Q4_K_M.gguf --host 127.0.0.1 --port 8090 -t 1 -c 4096 -b 64 --temp 0.3 --top-p 0.9
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now llama-qwen.service
sudo systemctl status llama-qwen.service --no-pager
```

Check logs if startup fails:

```bash
sudo journalctl -u llama-qwen.service -n 100 --no-pager
```

Verify that the API is listening on localhost:

```bash
curl http://127.0.0.1:8090/health
ss -ltnp | grep ':8090'
```

The listener should use `127.0.0.1:8090`, not `0.0.0.0:8090`.

### Test the chat API

```bash
curl http://127.0.0.1:8090/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen3-4B-Q4_K_M",
    "messages": [
      {
        "role": "user",
        "content": "Explain beekeeping."
      }
    ],
    "temperature": 0.3
  }'
```

### Monitor resource usage

Check memory:

```bash
free -h
```

Inspect the inference process:

```bash
ps -C llama-server -o %cpu,%mem,cmd
```

Check CPU temperature:

```bash
vcgencmd measure_temp
```

Monitor temperature and memory under sustained inference workloads. Use adequate cooling and power for the Raspberry Pi 5.

## 6. I²C on Raspberry Pi Zero 2 W

Enable I²C:

```bash
sudo raspi-config
```

Select **Interface Options → I2C → Enable**, then reboot.

Install the tools and Python library:

```bash
sudo apt update
sudo apt install -y i2c-tools python3-smbus
```

Verify the interface:

```bash
ls /dev/i2c-*
lsmod | grep i2c
sudo i2cdetect -y 1
```

Install additional Python dependencies if required by the edge application:

```bash
sudo apt install -y python3-aiohttp python3-apscheduler python3-pip
```

Use the correct bus for the connected hardware. An I²C scan should be performed only when the bus and attached devices are ready.

## 7. Controlled System Time Updates

If the controller needs to update the operating system clock, grant the `scibee` account permission to execute `/usr/bin/date` as root.

Verify the executable path:

```bash
which date
```

Create a sudoers configuration:

```bash
sudo visudo -f /etc/sudoers.d/scibee-time
```

Add:

```sudoers
scibee ALL=(root) NOPASSWD: /usr/bin/date
```

Set ownership and permissions:

```bash
sudo chown root:root /etc/sudoers.d/scibee-time
sudo chmod 0440 /etc/sudoers.d/scibee-time
sudo visudo -c
```

Test with a valid UTC timestamp:

```bash
sudo -u scibee sudo -n /usr/bin/date -u -s "YYYY-MM-DD HH:MM:SS"

date '+Local: %Y-%m-%d %H:%M:%S %Z'
date -u '+UTC: %Y-%m-%d %H:%M:%S UTC'
```

Replace the timestamp placeholder before running the command.

## 8. Deploy the Base Controller

Install the required Python packages:

```bash
sudo apt update
sudo apt install -y python3-flask python3-smbus2 gunicorn

python3 -c "import flask, smbus2; print('Dependencies OK')"
which gunicorn
```

From the PC, run this command from the directory containing `base_controller/`:

```bash
rsync -avz -e ssh base_controller/ \
  scibee@<PI_IP>:/home/scibee/base_controller/
```

Replace `<PI_IP>` with the address of the target Pi.

### Configure systemd

Create the service file:

```bash
sudo nano /etc/systemd/system/base-controller.service
```

Add:

```ini
[Unit]
Description=SCIBee Base Controller
After=network.target

[Service]
Type=simple
User=scibee
Group=scibee
WorkingDirectory=/home/scibee/base_controller
ExecStart=/usr/bin/gunicorn -c /home/scibee/base_controller/gunicorn_conf.py -w 1 --threads 4 -b 0.0.0.0:8998 base_controller:app
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now base-controller.service
sudo systemctl status base-controller.service --no-pager
```

Inspect logs and restart the service:

```bash
sudo journalctl -u base-controller.service -n 30 --no-pager
sudo journalctl -u base-controller.service -f

sudo systemctl restart base-controller.service
```

Reboot to verify automatic startup:

```bash
sudo reboot
```

After reconnecting:

```bash
sudo systemctl status base-controller.service --no-pager
```

## 9. Deploy Aggregator and Evaluator

Deploy the Aggregator and Evaluatorusing the same procedure as the Base Controller. Adjust the service names and installation paths as needed.

## 10. Deploy OpenAgri Services and Synchroniser

For edge-mode deployment, configure the services in `compose.yml` and create a `.env` file containing the required environment variables.

Follow the official [OpenAgri Bootstrap Deployment Guide](https://github.com/agstack/OpenAgri-Bootstrap-Deployment) for configuration and deployment instructions.
