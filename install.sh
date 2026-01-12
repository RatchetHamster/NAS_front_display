#SETUP PYTHON VENV
sudo apt update  
sudo apt upgrade -y  
sudo apt install python3-pip -y
python -m venv /home/pi/python/
source /home/pi/python/venv/bin/activate
pip install -r /home/pi/python/NAS_front_display/requirements.txt

#SETUP SERVICE:
#Move .service file to correct location
sudo mv /home/pi/python/NAS_front_display/front_io.service /etc/systemd/system/

#Enable service at boot
sudo systemctl daemon-reload
sudo systemctl enable front_io
sudo systemctl start front_io
