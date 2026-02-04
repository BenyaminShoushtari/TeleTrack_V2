# 📡 Mazaneh Monitor --- Real-Time Telegram Price Stream

Real-time Telegram channel monitor that extracts price data, stores it
in SQLite (with Gregorian + Shamsi timestamps), and streams updates via
WebSocket.

------------------------------------------------------------------------

## ✨ Features

-   📥 Real-time Telegram message monitoring\
-   🧠 Smart Persian text price extraction\
-   🗄 SQLite storage with:
    -   Gregorian timestamp
    -   Shamsi timestamp\
-   📏 Automatic DB size control (500MB max + auto cleanup)\
-   🌐 WebSocket real-time price broadcast\
-   🔄 Production-ready async architecture\
-   🧾 Logging system

------------------------------------------------------------------------

## 📦 Requirements

-   Python **3.9+**
-   Linux server (recommended)
-   Telegram API credentials

------------------------------------------------------------------------

# 🚀 Installation Guide

------------------------------------------------------------------------

## 1️⃣ Clone Repository

``` bash
git clone https://github.com/BenyaminShoushtari/TeleTrack_V2.git
cd mazaneh-monitor
```

------------------------------------------------------------------------

## 2️⃣ Create Python Virtual Environment

### Create venv

``` bash
python3 -m venv venv
```

### Activate venv

Linux / Server:

``` bash
source venv/bin/activate
```

------------------------------------------------------------------------

## 3️⃣ Install Dependencies

``` bash
pip install --upgrade pip
pip install telethon websockets python-dotenv aiosqlite jdatetime
```

------------------------------------------------------------------------

# ⚙️ Configuration

Create `.env` file:

``` env
TELEGRAM_API_ID=YOUR_API_ID
TELEGRAM_API_HASH=YOUR_API_HASH

TELEGRAM_CHANNEL=channel_username
SESSION_NAME=mazaneh_session

WS_HOST=0.0.0.0
WS_PORT=8765

LOG_LEVEL=INFO
```

------------------------------------------------------------------------

# ▶️ Run Project

``` bash
python telegramscrap.py
```

------------------------------------------------------------------------

# 📂 Generated Files

    mazaneh.db
    mazaneh_monitor.log

------------------------------------------------------------------------

# 🌐 WebSocket Connection

Connect clients to:

    ws://SERVER_IP:8765

------------------------------------------------------------------------

# 🗄 Database Behavior

### Size Limit

-   Max DB size: **500MB**
-   If exceeded → oldest **20% records deleted automatically**

------------------------------------------------------------------------

### Stored Data

  Field                  Description
  ---------------------- ------------------
  price                  Extracted price
  created_at_gregorian   ISO datetime
  created_at_shamsi      Persian datetime

------------------------------------------------------------------------

# 🔧 Run as Linux Service (systemd)

## 1️⃣ Create Service File

``` bash
sudo nano /etc/systemd/system/mazaneh.service
```

## 2️⃣ Service Config

``` ini
[Unit]
Description=Mazaneh Monitor Service
After=network.target

[Service]
User=root
WorkingDirectory=/root/mazaneh
ExecStart=/root/mazaneh/venv/bin/python telegramscrap.py
Restart=always

[Install]
WantedBy=multi-user.target
```

------------------------------------------------------------------------

## 3️⃣ Reload systemd

``` bash
sudo systemctl daemon-reload
```

------------------------------------------------------------------------

## 4️⃣ Enable Auto Start

``` bash
sudo systemctl enable mazaneh
```

------------------------------------------------------------------------

## 5️⃣ Start Service

``` bash
sudo systemctl start mazaneh
```

------------------------------------------------------------------------

## 6️⃣ Check Status

``` bash
sudo systemctl status mazaneh
```

------------------------------------------------------------------------

## 7️⃣ View Logs

``` bash
journalctl -u mazaneh -f
```

------------------------------------------------------------------------

# 🔐 Security Notes

-   Never commit `.env`
-   Never share API HASH
-   Use firewall for WebSocket port

------------------------------------------------------------------------

# 📜 License

MIT
