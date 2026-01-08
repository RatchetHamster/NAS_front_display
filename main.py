import psutil
import subprocess
import docker

def get_ip():
    return str(subprocess.check_output("ifconfig " + "wlan0" + " | awk '/inet / {print $2}'", shell=True)).strip()[2:-3]

def get_cpu_perc_temp():
    cpu_per = str(psutil.cpu_percent()) + '%'
    cpu_temp = str(psutil.sensors_temperatures()['cpu_thermal'][0].current)
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



print(f'{"IP:": <10}{get_ip()}')
print(f'{"CPU:": <10}{get_cpu_perc_temp()}')
print(f'{"RAM:": <10}{get_mem_usage()}')
print(f'{"SD Card:": <10}{get_sd_usage()}')
print(f'{"Button:": <10}{get_button_status()}')
for container in ["portainer", "Plex", "Samba"]:
  print(f'{container.capitalize()+':': <10}{get_container_state(container)}')

