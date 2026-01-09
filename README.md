# NAS_front_display
Connect up 3.3v, ground, SDA, SCL pins. 

setup venv and install requirements.txt

TO RUN AT START UP AS SERVICE:

sudo nano /etc/systemd/system/front_io.service

"""

[Unit]

Description=System info display

After=multi-user.target

[Service]

ExecStart=/home/pi/python/venv/bin/python /home/pi/python/NAS_front_display/main.py

Restart=always

User=root

[Install]

WantedBy=multi-user.target

"""

ENABLE SERVICE AT STARTUP:

sudo systemctl daemon-reload

sudo systemctl enable front_io

sudo systemctl start front_io
