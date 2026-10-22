# SCIBee Cloud — Server Setup

## Overview

This document describes the setup of the SCIBee cloud VM, Docker, a local Qwen3 inference server using `llama.cpp`, and Tailscale for remote access.

## 1. Virtual Machine

### Connect to the server

Connect to the server's network and identify the VM's IP address:

```bash
nmap -sn 192.168.1.1-254
```

Connect using SSH:

```bash
ssh <username>@<vm-ip>
```

Replace the placeholders with the username and IP address provided by the server administrator.

### Inspect the system

```bash
cat /etc/debian_version
cat /etc/os-release
df -h
```

Check the Debian version, operating system details, and available disk space.

### Update the system

```bash
sudo apt update
apt list --upgradable
sudo apt full-upgrade
sudo apt autoremove
sudo apt clean
```

Review proposed package changes before confirming the upgrade.

## 2. Docker

Install and enable Docker:

```bash
sudo apt install docker.io
sudo systemctl enable --now docker
sudo systemctl status docker
```

Verify the installation:

```bash
sudo docker run --rm hello-world
sudo systemctl is-active docker
```

Docker should report an active service, and the test container should run successfully.

Check whether the Compose plugin is installed:

```bash
docker compose version
```

## 3. Local AI Inference Server

The Qwen3-4B model runs locally through `llama.cpp`, exposing an OpenAI-compatible API on port `8090`.

The server listens on `127.0.0.1` only. Native applications on the Debian VM can access it through localhost.

### Install dependencies

```bash
sudo apt install git cmake build-essential libssl-dev curl

git --version
cmake --version
g++ --version
```

### Build llama.cpp

Create the project directories:

```bash
mkdir -p ~/cloud/ai/qwen/models
cd ~/cloud/ai/qwen
```

Clone and build `llama.cpp`:

```bash
git clone https://github.com/ggml-org/llama.cpp.git
cd llama.cpp

cmake -B build -DLLAMA_OPENSSL=ON
cmake --build build -j"$(nproc)" --target llama-cli llama-server

ls -lh build/bin/llama-cli build/bin/llama-server
```

### Download the model

Download the Qwen3-4B GGUF model in Q4_K_M quantization:

```bash
cd ~/cloud/ai/qwen/models

../llama.cpp/build/bin/llama-cli \
  -hf Qwen/Qwen3-4B-GGUF:Q4_K_M
```

Inspect the Hugging Face cache:

```bash
ls -lh ~/.cache/huggingface/hub/models--Qwen--Qwen3-4B-GGUF/blobs/
```

Copy the actual downloaded GGUF model file into the project directory. The following source path is a placeholder and must be replaced with the location of the identified model file:

```bash
cp /path/to/downloaded-model.gguf \
  ~/cloud/ai/qwen/models/Qwen3-4B-Q4_K_M.gguf
```

Confirm that the destination file exists and has a plausible size:

```bash
ls -lh ~/cloud/ai/qwen/models/Qwen3-4B-Q4_K_M.gguf
```

Ensure the copied file is the intended Q4_K_M model, not an unrelated cache file.

### Test the inference server

Start the server manually:

```bash
cd ~/cloud/ai/qwen/llama.cpp

./build/bin/llama-server \
  -m ../models/Qwen3-4B-Q4_K_M.gguf \
  --host 127.0.0.1 \
  --port 8090 \
  -t 4 \
  -c 4096 \
  -b 128 \
  --temp 0.3 \
  --top-p 0.9
```

The server listens on localhost only.

In another terminal, check its health:

```bash
curl http://127.0.0.1:8090/health
```

Stop the manually started server with `Ctrl+C` before configuring automatic startup.

### Configure automatic startup

The systemd service below assumes the Linux account is named `scibee` and that the model and executable are located in `/home/scibee`. If your account or installation path differs, update the configuration accordingly.

Create the service file:

```bash
sudo nano /etc/systemd/system/llama-qwen.service
```

Add the following configuration:

```ini
[Unit]
Description=SCIBee Qwen3-4B llama.cpp Server
After=network.target

[Service]
Type=simple
User=scibee
WorkingDirectory=/home/scibee/cloud/ai/qwen/llama.cpp
ExecStart=/home/scibee/cloud/ai/qwen/llama.cpp/build/bin/llama-server -m /home/scibee/cloud/ai/qwen/models/Qwen3-4B-Q4_K_M.gguf --host 127.0.0.1 --port 8090 -t 4 -c 4096 -b 128 --temp 0.3 --top-p 0.9
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

Check logs if the service fails:

```bash
sudo journalctl -u llama-qwen.service -n 100 --no-pager
```

Verify the API:

```bash
curl http://127.0.0.1:8090/health
```

The service should start automatically after a reboot.

**CPU resources:** The configured `-t 4` uses four CPU threads. Adjust this value according to the VM's available CPU resources.

### Verify local API access

Check that the server is listening on the loopback interface:

```bash
ss -ltnp | grep ':8090'
```

The listener should be bound to `127.0.0.1:8090`, not `0.0.0.0:8090`.

Applications running directly on the Debian VM can access the API at:

```text
http://127.0.0.1:8090/v1/chat/completions
```

No Docker port mapping or `extra_hosts` entry is required because Docker services do not need to access the AI server.

## 4. Tailscale Remote Access

Tailscale provides private network connectivity for remote administration and access to services, subject to the network and access-control configuration.

Install Tailscale using the [official Linux installation instructions](https://tailscale.com/docs/install/linux).

```bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
```

Complete the authentication flow and authorize the server in the appropriate Tailscale network.

Check the connection:

```bash
tailscale ip
tailscale status
systemctl is-enabled tailscaled
systemctl is-active tailscaled
```
## 5. Deploy Aggregator and Evaluator

Deploy the Aggregator and Evaluator using the same procedure as for the Base Controller (in SCIBee Cloud — Raspberry Pi Gateway Setup). Adjust the service names and installation paths as needed.

## 6. Deploy OpenAgri Services and Synchroniser

For cloud-mode deployment, configure the services in `compose.yml` and create a `.env` file containing the required environment variables.

Follow the official [OpenAgri Bootstrap Deployment Guide](https://github.com/agstack/OpenAgri-Bootstrap-Deployment) for configuration and deployment instructions.
