##TODO  
Add to run local for debug note  
Add where log is output to for debug  
Route python service to log file  
setup logrotate on log file  

## To update  
if this repo is updated:  
cd /home/pi/python/NAS_front_display  
git pull  
sudo reboot  

## To install  
cd into /home/pi/python (if python doesn't exist, make it)  
git clone this repo  

#SETUP PYTHON VENV  
python -m venv /home/pi/python/venvs/venv_front_io/  
source /home/pi/python/venvs/venv_front_io/bin/activate  
pip install -r /home/pi/python/NAS_front_display/requirements.txt  

#SETUP SERVICE:  
#Move .service file to correct location  
sudo mv /home/pi/python/NAS_front_display/front_io.service /etc/systemd/system/  

#Enable service at boot  
sudo systemctl daemon-reload && sudo systemctl enable front_io && sudo systemctl start front_io  

#Create logrotate limit on log file  
sudo nano /etc/logrotate.d/front_io  
into the file put:  
/var/log/front_io.log  
{  
    weekly  
    minsize 1M  
    maxsize 10M  
    rotate 4  
    missingok  
    notifempty  
}  
 
