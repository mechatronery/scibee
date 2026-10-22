# SCIBee Cloud — Raspberry Pi Gateway Setup

## Overview

This document describes how to configure a Raspberry Pi Zero 2 W as a SCIBee gateway. The gateway provides a Wi-Fi access point for local devices, LTE connectivity, remote access through Tailscale, I²C support, and a systemd-managed base controller service.

**Note:** Replace placeholders with deployment-specific values.

## 1. Raspberry Pi OS Installation

1. Download the Raspberry Pi Imager AppImage from the [official GitHub releases](https://github.com/raspberrypi/rpi-imager/releases). Version 2.0.8 was tested.

2. Make the AppImage executable and launch it:
   
   ```bash
   chmod +x rpi-imager-*.AppImage
   ./rpi-imager-*.AppImage
   ```

3. Select the appropriate Raspberry Pi model and SD card.

4. Choose **Raspberry Pi OS (other) → Raspberry Pi OS Lite (64-bit)**.

5. Configure the hostname, locale, username, password, Wi-Fi credentials, and SSH access in OS customisation.

6. Write the image to the SD card.

## 2. Initial Access

Boot the Pi and connect the administration PC to the same network.

Discover the Pi's IP address:

```bash
nmap -sn 192.168.4.1-254
```

Connect using the discovered address:

```bash
ssh scibee@<pi-ip>
```

Replace `<pi-ip>` with the actual address assigned by the router.

## 3. Wi-Fi Access Point

The gateway can expose a dedicated Wi-Fi network for nearby SCIBee devices. The following example uses `SCIBee_A` and subnet `192.168.1.0/24`.

Create the NetworkManager connection:

```bash
sudo nmcli con add con-name hotspot ifname wlan0 \
  type wifi ssid "SCIBee_A" autoconnect no

sudo nmcli con modify hotspot \
  wifi-sec.key-mgmt wpa-psk \
  wifi-sec.psk "<WIFI_PASSWORD>"

sudo nmcli con modify hotspot \
  802-11-wireless.mode ap \
  802-11-wireless.band bg \
  ipv4.method shared \
  ipv4.addresses 192.168.1.1/24 \
  ipv4.shared-dhcp-range 192.168.1.2,192.168.1.99
```

**Subnet convention:** Assign a distinct subnet to each gateway, for example:

- `SCIBee_A`: `192.168.1.0/24`
- `SCIBee_B`: `192.168.2.0/24`

Update the IP addresses, DHCP range, and Tailscale routes consistently when changing subnets.

Bring up the access point:

```bash
sudo nmcli con up hotspot
```

Connect the PC to the access point and SSH into the gateway:

```bash
ssh scibee@192.168.1.1
```

To recover the normal router connection without rebooting, schedule a delayed activation in a separate terminal:

```bash
sudo sh -c 'sleep 300 && nmcli con up netplan-wlan0-SCIBee'
```

Replace `netplan-wlan0-SCIBee` with the actual router connection profile. This is a one-time recovery command, not a persistent fallback service.

### ESP32 compatibility

For the ESP32 Wi-Fi compatible implementation, configure WPA2/CCMP security:

```bash
sudo nmcli connection modify hotspot \
  802-11-wireless-security.key-mgmt wpa-psk \
  802-11-wireless-security.proto rsn \
  802-11-wireless-security.pairwise ccmp \
  802-11-wireless-security.group ccmp \
  802-11-wireless-security.pmf disable
```

Restart the access point to apply changes:

```bash
sudo nmcli connection down hotspot
sudo nmcli connection up hotspot
```

Inspect connected Wi-Fi clients:

```bash
sudo iw dev wlan0 station dump
```

## 4. LTE Connectivity

Assemble the supported cellular modem and antenna, install the SIM, and connect the Pi to the internet temporarily through its normal router connection.

Verify modem device nodes:

```bash
ls /dev/ttyUSB*
```

Install ModemManager and inspect the modem:

```bash
sudo apt update
sudo apt install modemmanager
sudo reboot
```

After reboot:

```bash
mmcli -L
mmcli -m 0
```

The modem index may differ. Use the index reported by `mmcli -L`.

### Configure the mobile connection

Create a GSM connection using the APN and authentication settings supplied by the mobile operator:

```bash
sudo nmcli con add con-name lte ifname "*" type gsm \
  apn "<APN>"
```

If the SIM requires a PIN, configure it locally:

```bash
sudo nmcli con modify lte gsm.pin "<SIM_PIN>"
```

Activate and test the connection:

```bash
sudo nmcli con up lte

ping -c 4 1.1.1.1
ping -c 4 google.com
```

A successful IP-address ping tests connectivity; a successful domain-name ping also tests DNS resolution.

### Connection priorities

Configure the normal router connection to have the highest priority, with LTE and the access point as fallbacks:

```bash
sudo nmcli con modify netplan-wlan0-SCIBee \
  connection.autoconnect yes \
  connection.autoconnect-priority 100

sudo nmcli con modify lte \
  connection.autoconnect yes \
  connection.autoconnect-priority 0

sudo nmcli con modify hotspot \
  connection.autoconnect yes \
  connection.autoconnect-priority 10
```

Replace the router profile name if necessary.

## 5. Tailscale Remote Access

Install Tailscale using the [official Linux instructions](https://tailscale.com/docs/install/linux).

```bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
```

Complete authentication, then verify connectivity:

```bash
tailscale ip
tailscale status
systemctl is-enabled tailscaled
systemctl is-active tailscaled
```

Enable IP forwarding for subnet routing:

```bash
echo 'net.ipv4.ip_forward = 1' | \
  sudo tee /etc/sysctl.d/99-tailscale.conf

sudo sysctl -p /etc/sysctl.d/99-tailscale.conf
```

Advertise the gateway's Wi-Fi subnet:

```bash
sudo tailscale set --advertise-routes=192.168.1.0/24
```

Approve the advertised route in the [Tailscale admin console](https://login.tailscale.com/admin/machines). Enable route acceptance on remote clients when needed:

```bash
sudo tailscale set --accept-routes=true
```

To enable Tailscale SSH, if permitted by the tailnet's access policies:

```bash
sudo tailscale set --ssh
```

For example, access the gateway through its Tailscale IP:

```bash
ssh scibee@<TAILSCALE_IP>
```

Access a device connected to the gateway's Wi-Fi network using its LAN address:

```bash
ssh <DEVICE_USER>@192.168.1.20
```

### Forward Tailscale traffic to the Wi-Fi subnet

Add a dispatcher script to permit forwarding from Tailscale to the access-point subnet.

Create the script:

```bash
sudo nano /etc/NetworkManager/dispatcher.d/90-tailscale-hotspot
```

Add:

```bash
#!/bin/sh

# Apply only when the Wi-Fi interface becomes active.
IFACE="$1"
ACTION="$2"

[ "$IFACE" = "wlan0" ] || exit 0
[ "$ACTION" = "up" ] || exit 0

TABLE="nm-shared-wlan0"
CHAIN="filter_forward"
SUBNET="192.168.1.0/24"

# Wait briefly for NetworkManager to create its forwarding chain.
for i in 1 2 3 4 5; do
    nft list chain ip "$TABLE" "$CHAIN" >/dev/null 2>&1 && break
    sleep 1
done

# Avoid adding the same forwarding rule more than once.
if ! nft list chain ip "$TABLE" "$CHAIN" 2>/dev/null |
    grep -Fq "iifname \"tailscale0\" oifname \"wlan0\" ip daddr $SUBNET accept"
then
    nft insert rule ip "$TABLE" "$CHAIN" \
        iifname "tailscale0" \
        oifname "wlan0" \
        ip daddr "$SUBNET" \
        accept
fi

exit 0
```

Set ownership and permissions:

```bash
sudo chown root:root \
  /etc/NetworkManager/dispatcher.d/90-tailscale-hotspot

sudo chmod 755 \
  /etc/NetworkManager/dispatcher.d/90-tailscale-hotspot
```

Test the script and inspect the forwarding chain:

```bash
sudo /etc/NetworkManager/dispatcher.d/90-tailscale-hotspot wlan0 up

sudo nft -a list chain ip nm-shared-wlan0 filter_forward
```

From a remote Tailscale client, test a device on the gateway subnet:

```bash
ping -c 3 192.168.1.20
```

Repeat after restarting the access point to confirm that the rule is restored.

## 6. Enable I²C

Enable I²C using the Raspberry Pi configuration utility:

```bash
sudo raspi-config
```

Select **Interface Options → I2C → Enable**, then reboot.

Install tools and verify the interface:

```bash
sudo apt update
sudo apt install -y i2c-tools python3-smbus2

ls /dev/i2c-*
lsmod | grep i2c
sudo i2cdetect -y 1
```

Use the correct I²C bus and ensure that connected devices are powered and wired correctly.

## 7. Allow Controlled System Time Updates

If the controller must set the operating system time, grant the `scibee` account passwordless permission to execute only `/usr/bin/date` as root.

Confirm the executable path:

```bash
which date
```

Create a sudoers drop-in:

```bash
sudo visudo -f /etc/sudoers.d/scibee-time
```

Add:

```sudoers
scibee ALL=(root) NOPASSWD: /usr/bin/date
```

Set secure permissions and validate the configuration:

```bash
sudo chown root:root /etc/sudoers.d/scibee-time
sudo chmod 0440 /etc/sudoers.d/scibee-time
sudo visudo -c
```

Test with an appropriate UTC timestamp:

```bash
sudo -u scibee sudo -n /usr/bin/date -u -s "YYYY-MM-DD HH:MM:SS"
date -u '+UTC: %Y-%m-%d %H:%M:%S UTC'
```

Replace the timestamp placeholder with a valid date and time.

## 8. Deploy the Base Controller

Install the Python dependencies:

```bash
sudo apt update
sudo apt install -y python3-flask python3-smbus2 gunicorn

python3 -c "import flask, smbus2; print('Dependencies OK')"
which gunicorn
```

From the PC, run the following command in the directory containing `base_controller/`:

```bash
rsync -avz -e ssh base_controller/ \
  scibee@<PI_IP>:/home/scibee/base_controller/
```

Replace `<PI_IP>` with the gateway's reachable address.

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

Inspect logs and restart the service when necessary:

```bash
sudo journalctl -u base-controller.service -n 30 --no-pager
sudo journalctl -u base-controller.service -f

sudo systemctl restart base-controller.service
```

Verify that the controller starts automatically after reboot:

```bash
sudo reboot
```

After reconnecting:

```bash
sudo systemctl status base-controller.service --no-pager
```
