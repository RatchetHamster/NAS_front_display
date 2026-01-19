import psutil
import subprocess
import time
import os
import logging
from threading import Thread
from pathlib import Path
from PIL import ImageFont, Image
from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306
from luma.core.render import canvas

#Logger:
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s') #Change level of logging output here

# Load Logo: 
logo = Image.open("logo.bmp")
logo = logo.convert("1")
print("mode:", logo.mode)
print("size:", logo.size)
print("device:", device.width, device.height)


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
#def get_screen_info_1():
#    return "SHOW LOGO"
    
def get_screen_info_1():
    info = f'{"SD": <6}{get_HDD_usage('/')}\n'
    for HDD in ["NAS1", "NAS2"]:
            if is_mounted(f'/mnt/{HDD}'):
                info += f'{HDD:<6}{get_HDD_usage(f"/mnt/{HDD}")}\n'
            else:
                info += f'{HDD:<6}Not Mounted!\n'
    return info

def get_screen_info_2():
    info = f'{"Button": <11}{get_service_status("pi_button_shutdown")}\n'
    info += f'{"Plex": <11}{get_service_status("plexmediaserver")}\n'
    info += f'{"Samba": <11}{get_service_status("smbd")}\n'
    return info

def get_screen_info_3():
    host1 = '192.168.0.82'
    status1 = is_pi_online(host1)
    info = f'{"AudioPi": <11}{status1}\n'
    if status1 == "Online":
        info += f'{" - MP3": <11}{check_service(host1, "pirate-mp3")}\n'
        info += f'{" - Samba": <11}{check_service(host1, "smbd")}\n'
    return info
    
def draw_frame(device, info, font1):
    #Footer Info:
    foot = f'{"C:"+get_cpu_per():<6}'
    foot += f'{get_cpu_temp():^6}'
    foot += f'{"R:"+get_mem_usage():>6}'#18tot chars

    with canvas(device, dither=True) as draw:
        if info == "SHOW LOGO":
            print("mode:", logo.mode)
            print("size:", logo.size)
            print("device:", device.width, device.height)
            draw.bitmap((0,0),logo, fill=1)
        else:
            draw.rectangle((1, 48, 127, 63), outline="white")
            draw.text((11, 49), foot, font=font1, fill='white')
            draw.text((1, 1), info, font=font1, fill='white')
    return foot

class CustomThread(Thread):
    def __init__(self, group=None, target=None, name=None, args=(), kwargs={}, verbose=None):
        # Initializing the Thread class
        super().__init__(group, target, name, args, kwargs)
        self._return = None

    # Overriding the Thread.run function
    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args, **self._kwargs)

    def join(self):
        super().join()
        return self._return

def main(device):
    font_path = str(Path(__file__).resolve().parent.joinpath('RobotoMono-Regular.ttf'))
    font1 = ImageFont.truetype(font_path, 10)
    frame_rate = 0.5
    screen_time = 5
    screen_fun= {1:get_screen_info_1, 2:get_screen_info_2, 3:get_screen_info_3}
    next_screen_info = get_screen_info_1()
    
    while True:    
        for screen in range(1,len(screen_fun)+1):
            start_t = time.time()
            curr_screen_info = next_screen_info
            next_screen = screen+1
            if next_screen>len(screen_fun):
                next_screen=1
            next_thread = CustomThread(target=screen_fun[next_screen])
            next_thread.start()
            
            while time.time() - start_t <= screen_time:    
                foot = draw_frame(device, curr_screen_info, font1)
                time.sleep(frame_rate)
                
            logging.debug(f'Screen displaying {screen}:\n{curr_screen_info+foot}\n')
            next_screen_info = next_thread.join()


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
