📡 Mazaneh Monitor — Real-Time Telegram Price Stream

Real-time Telegram channel monitor that extracts price data, stores it in SQLite (with Gregorian + Shamsi timestamps), and streams updates via WebSocket.

✨ Features

📥 Real-time Telegram message monitoring

🧠 Smart Persian text price extraction

🗄 SQLite storage with:

Gregorian timestamp

Shamsi timestamp

📏 Automatic DB size control (500MB max + auto cleanup)

🌐 WebSocket real-time price broadcast

🔄 Production-ready async architecture

🧾 Logging system

📦 Requirements

Python 3.9+

Linux server (recommended)

Telegram API credentials

🚀 Installation Guide
1️⃣ Clone Repository
git clone https://github.com/YOUR_USERNAME/TeleTrack_V2.git
cd mazaneh-monitor

2️⃣ Create Python Virtual Environment
Create venv
python3 -m venv venv

Activate venv

Linux / Server:

source venv/bin/activate


If activated successfully you should see:

(venv)

3️⃣ Install Dependencies
pip install --upgrade pip
pip install telethon websockets python-dotenv aiosqlite jdatetime

⚙️ Configuration

Create .env file:

TELEGRAM_API_ID=YOUR_API_ID
TELEGRAM_API_HASH=YOUR_API_HASH

TELEGRAM_CHANNEL=channel_username
SESSION_NAME=mazaneh_session

WS_HOST=0.0.0.0
WS_PORT=8765

LOG_LEVEL=INFO

▶️ Run Project
python telegramscrap.py


If successful:

Telegram Connected
WS running → ws://0.0.0.0:8765

📂 Generated Files
mazaneh.db
mazaneh_monitor.log

🌐 WebSocket Connection

Connect clients to:

ws://SERVER_IP:8765

🗄 Database Behavior
Size Limit

Max DB size: 500MB

If exceeded → oldest 20% records deleted automatically

Stored Data
Field	Description
price	Extracted price
created_at_gregorian	ISO datetime
created_at_shamsi	Persian datetime
🧪 Testing Database
sqlite3 mazaneh.db


Example queries:

SELECT * FROM mazaneh_prices LIMIT 10;

SELECT AVG(price) FROM mazaneh_prices;

🔧 Run as Linux Service (systemd)
1️⃣ Create Service File
sudo nano /etc/systemd/system/mazaneh.service

2️⃣ Paste Service Config

⚠ Replace paths with your server path

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

3️⃣ Reload systemd
sudo systemctl daemon-reload

4️⃣ Enable Auto Start
sudo systemctl enable mazaneh

5️⃣ Start Service
sudo systemctl start mazaneh

6️⃣ Check Status
sudo systemctl status mazaneh

7️⃣ View Logs
journalctl -u mazaneh -f

🛑 Stop Service
sudo systemctl stop mazaneh

🔄 Restart Service
sudo systemctl restart mazaneh

🧯 Troubleshooting
Virtual Environment Not Activating

Install full python:

apt install python3-full python3-venv

Port Not Accessible

Open firewall:

ufw allow 8765/tcp

Telegram Login Issues

Delete session file and restart.

🔐 Security Notes

Never commit .env

Never share API HASH

Use firewall for WebSocket port

📈 Future Roadmap

REST API

Dashboard UI

Chart Visualization

Multi Channel Support

Backup System

Alert Engine
