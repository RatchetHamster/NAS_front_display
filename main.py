import psutil
import subprocess
import docker
import time
from pathlib import Path
from PIL import ImageFont
from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306
from luma.core.render import canvas

#Information interigators:
def get_ip():
    return str(subprocess.check_output("ifconfig " + "wlan0" + " | awk '/inet / {print $2}'", shell=True)).strip()[2:-3]
    
def get_cpu_perc_temp():
    cpu_per = str(psutil.cpu_percent()) + '%'
    cpu_temp = str(round(psutil.sensors_temperatures()['cpu_thermal'][0].current,1))
    return cpu_per + ' at ' + cpu_temp + '°C'
    
def get_mem_usage():
    memory = psutil.virtual_memory()
    mem_tot = round(memory.total/1024.0/1024.0/1024.0,1) # Bytes to GB
    return str(memory.percent) + '%' + ' of ' + str(mem_tot) + 'GB'
    
def get_sd_usage():
    disk = psutil.disk_usage('/')
    disk_tot = round(disk.total/1024.0/1024.0/1024.0,1) # Bytes to GB
    return str(disk.percent) + '%' + ' of ' + str(disk_tot) + 'GB'
    
DOCKER_CLIENT = docker.DockerClient(base_url='unix://var/run/docker.sock')
def get_container_state(container_name):
    container = DOCKER_CLIENT.containers.get(container_name)
    return container.attrs['State']['Status'].capitalize()
    
def get_button_status():
    return subprocess.run(['systemctl', 'is-active', 'pi_button_shutdown.service'], capture_output=True, text=True).stdout.strip().capitalize()


#Run Screen and Main File:
font_path = str(Path(__file__).resolve().parent.joinpath('RobotoMono-Regular.ttf'))
font_s1 = ImageFont.truetype(font_path, 10)
font_s2 = ImageFont.truetype(font_path, 10)

def get_info(screen=1):
    info = ''
    if screen == 1:
        info += f'{"IP": <6}{get_ip()}\n'
        info += f'{"CPU": <6}{get_cpu_perc_temp()}\n'
        info += f'{"RAM": <6}{get_mem_usage()}\n'
        info += f'{"HD": <6}{get_sd_usage()}\n'
    elif screen == 2:
        for container in ["portainer", "Plex", "Samba"]:
            info += f'{container.capitalize(): <11}{get_container_state(container)}\n'
        info += f'{"Button": <11}{get_button_status()}'
    return info       

def disp_info(device, info, font2, screen=1):    
    with canvas(device, dither=True) as draw:
        draw.text((1, 1), info, font=font2, fill='white')

def main(device):
    # use custom font
    refresh_time = 0.5
    screen_time = 5
    
    while True:
        for screen in (1,2):
            for _ in range(int(screen_time/refresh_time)):
                if screen==1:
                    disp_info(device, get_info(screen), font_s1, screen)
                elif screen==2:
                    disp_info(device, get_info(screen), font_s2, screen)
                time.sleep(refresh_time)
            for i in range(int(device.width/2)):
                info1 = get_info(1)
                info2 = get_info(2)
                with canvas(device, dither=True) as draw:
                    draw.text((1-i*2, 1), info1, font=font_s1, fill='white')
                    draw.text((device_width+1-i*2, 1), info2, font=font_s2, fill='white')
                    time.sleep(0.1)
            

if __name__ == "__main__":
    try:
        device = ssd1306(i2c(port=1, address=0x3c), width=128, height=64, rotate=0)
        device.contrast(1)
        main(device)
    except KeyboardInterrupt:
        pass
    finally:
        device.clear()

