import psutil
import subprocess
import time
import os
from pathlib import Path
from PIL import ImageFont
from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306
from luma.core.render import canvas

# SCREEN 1 (system info):
#    CPU %
#    CPU Temp
#    RAM %
#    SD
# SCREEN 2 (HDDs):
#    NAS1: OK/NOT OK usage
#    NAS2: OK/NOT OK usage
# SCREEN 3 (Local Services): 
#    Button
#    Plex
# SCREEN 4 (Network services):
#    AudioPi

#Information interigators:

def get_cpu_temp():
    return str(round(psutil.sensors_temperatures()['cpu_thermal'][0].current,1)) + '°C'
def get_cpu_per():
    return str(psutil.cpu_percent()) + '%'
def get_mem_usage():
    return str(psutil.virtual_memory().percent)+ '%'
def get_HDD_usage(path_to_hdd):
    disk = psutil.disk_usage(path_to_hdd)
    disk_tot = round(disk.total/1024.0/1024.0/1024.0,1) # Bytes to GB
    return str(disk.percent) + '%' + ' of ' + str(disk_tot) + 'GB'
def get_service_status(service):
    return subprocess.run(['systemctl', 'is-active', f'{service}.service'], capture_output=True, text=True).stdout.strip().capitalize()
def is_mounted(path_to_mount):
    return os.path.ismount(path_to_mount)


#Run Screen and Main File:
font_path = str(Path(__file__).resolve().parent.joinpath('RobotoMono-Regular.ttf'))
font_s1 = ImageFont.truetype(font_path, 10)
font_s2 = ImageFont.truetype(font_path, 10)
font_s3 = ImageFont.truetype(font_path, 10)
font_s4 = ImageFont.truetype(font_path, 10)

def screen_info(device, screen=1):
    info = ''
    if screen == 1:
        font2 = font_s1
        info += f'{"CPU %": <8}{get_cpu_per()}\n'
        info += f'{"Temp": <8}{get_cpu_temp()}\n'
        info += f'{"RAM": <8}{get_mem_usage()}\n'
        info += f'{"SD": <8}{get_HDD_usage('/')}\n'

    elif screen == 2:
        font2 = font_s2
        for HDD in ["NAS1", "NAS2"]:
            if is_mounted(f'/mnt/{HDD}'):
                info += f'{HDD:<5}{get_HDD_usage}\n'
            else:
                info += f'{HDD:<5}Not Mounted!\n'
    
    elif screen == 3:
        font2 = font_s3
        info += f'{"Button": <11}{get_service_status("pi_button_shutdown")}'

    elif screen == 4:
        font2 = font_s4

    with canvas(device, dither=True) as draw:
        draw.text((1, 1), info, font=font2, fill='white')

def main(device):
    # use custom font
    refresh_time = 0.5
    screen_time = 5
    
    while True:
        for screen in (1,2):
            for _ in range(int(screen_time/refresh_time)):
                screen_info(device, screen)
                time.sleep(refresh_time)            

if __name__ == "__main__":
    try:
        device = ssd1306(i2c(port=1, address=0x3c), width=128, height=64, rotate=0)
        device.contrast(1)
        main(device)
    except KeyboardInterrupt:
        pass
    finally:
        device.clear()

