# NAS_front_display
Connect up 3.3v, ground, SDA, SCL pins. 

TO RUN AT START UP AS SERVICE:

sudo nano /etc/systemd/system/front_io.service

"""

[Unit]

Description=System info display

After=multi-user.target

[Service]

ExecStart=/usr/bin/python3 /home/pi/python/NAS_front_display/main.py

Restart=always

User=root

[Install]

WantedBy=multi-user.target

"""

ENABLE SERVICE AT STARTUP:

sudo systemctl daemon-reload

sudo systemctl enable front_io

sudo systemctl start front_io
