#SETUP PYTHON VENV
python -m venv_front_io /home/pi/python/venvs/
source /home/pi/python/venvs/venv_front_io/bin/activate
pip install -r /home/pi/python/NAS_front_display/requirements.txt

#SETUP SERVICE:
#Move .service file to correct location
sudo mv /home/pi/python/NAS_front_display/front_io.service /etc/systemd/system/

#Enable service at boot
sudo systemctl daemon-reload
sudo systemctl enable front_io
sudo systemctl start front_io
