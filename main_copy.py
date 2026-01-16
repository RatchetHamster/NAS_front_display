import psutil
import subprocess
import time
import os
import logging
from pathlib import Path
from PIL import ImageFont
from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306
from luma.core.render import canvas

#Logger:
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s') #Change level of logging output here

# SCREEN 1 (system info):
# SCREEN 2 (HDDs):
# SCREEN 3 (Local Services): 
# SCREEN 4 (Network services):
#    AudioPi

#region ----- Get Infos -----
def get_cpu_temp():
    try:
        return str(int(psutil.sensors_temperatures()['cpu_thermal'][0].current)) + '°C'
    except:
        logging.error('Something went wrong getting CPU Temp')
        return 'ERR'
        
def get_cpu_per():
    try:
        return str(int(psutil.cpu_percent())) + '%'
    except:
        logging.error('Something went wrong getting CPU %')
        return 'ERR'
        
def get_mem_usage():
    try:
        return str(int(psutil.virtual_memory().percent))+ '%'
    except:
        logging.error('Something went wrong getting mem usage')
        return 'ERR'

def is_mounted(path_to_mount):
    try:
        return os.path.ismount(path_to_mount)
    except:
        logging.error(f'Something went wrong polling mounted HDD: {path_to_mount}')
        return 'ERR'

def get_HDD_usage(path_to_hdd):
    try:
        disk = psutil.disk_usage(path_to_hdd)
        disk_tot = int(disk.total/1024.0/1024.0/1024.0) # Bytes to GB
        return str(int(disk.percent)) + '%' + ' of ' + str(disk_tot) + ' GB'
    except:
        logging.error(f'Something went wrong getting HDD usage: {path_to_hdd}')
        return 'ERR'
        
def get_service_status(service):
    try:
        return subprocess.run(['systemctl', 'is-active', f'{service}.service'], capture_output=True, text=True).stdout.strip().capitalize()
    except:
        logging.error(f'Something went wrong getting service status: {service}')
        return 'ERR'

def is_pi_online(host_ip):
    try:
        result = subprocess.run(["ping", "-c", "1", "-W", str(2), host_ip], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,)
        if result.returncode == 0: 
            return "Online"
        else:
            return "Offline"
    except Exception:
        return "Offline"

def check_service(host_ip, service):
    command = ["ssh", f"pi@{host_ip}", f"systemctl is-active {service}"]
    try:
        status = subprocess.run(command, capture_output=True, text=True, timeout=2).stdout.strip().capitalize()
        return status
    except:
        return "ERR"

#endregion


#Run Screen and Main File:
font_path = str(Path(__file__).resolve().parent.joinpath('RobotoMono-Regular.ttf'))
num_screens = 1
font_s1 = ImageFont.truetype(font_path, 10)
font_s2 = ImageFont.truetype(font_path, 10)
font_s3 = ImageFont.truetype(font_path, 10)
font_s4 = ImageFont.truetype(font_path, 10)

def screen_info(device, screen=1):
    info = ''
    if screen == 1:
        font2 = font_s1
        info += f'C: {get_cpu_per()}'
        info += f'   {get_cpu_temp()}   '
        info += f'R:{get_mem_usage()}'




            

    else:
        logging.error("Screen not defined")

    with canvas(device, dither=True) as draw:
        draw.rectangle((1, 45, 127, 63), outline="white")
        draw.text((1, 45), info, font=font2, fill='white')
    return info

def main(device):
    # use custom font
    refresh_time = 0.5
    screen_time = 5
    while True:
        for screen in range(1,num_screens+1):
            start_t = time.time()
            while time.time() - start_t <= screen_time:
                info = screen_info(device, screen)
                time.sleep(refresh_time)
            logging.debug(f'Screen displaying {screen}:\n{info}\n')


if __name__ == "__main__":
    logging.info("Service Initiated")
    try:
        try:
            device = ssd1306(i2c(port=1, address=0x3c), width=128, height=64, rotate=0)
            device.contrast(1)
        except:
            logging.critical("Something went wrong with the screen mount.")
        main(device)
    except KeyboardInterrupt:
        pass
    finally:
        device.clear()
