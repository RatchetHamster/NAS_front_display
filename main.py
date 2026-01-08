import psutil
import subprocess
import docker

# Network
ip = subprocess.check_output("ifconfig " + "wlan0" + " | awk '/inet / {print $2}'", shell=True)
ip = str(ip).strip()[2:-3]

# CPU Stats (% and temp)
cpu_per = str(psutil.cpu_percent()) + '%'
cpu_temp = str(psutil.sensors_temperatures()['cpu_thermal'][0].current)
cpu_info = cpu_per + ' at ' + cpu_temp + '°C'

# Calculate memory information
memory = psutil.virtual_memory()
mem_tot = round(memory.total/1024.0/1024.0/1024.0,1) # Bytes to GB
mem_info = str(memory.percent) + '%' + ' of ' + str(mem_tot) + 'GB'

# Calculate disk information
disk = psutil.disk_usage('/')
disk_tot = round(disk.total/1024.0/1024.0/1024.0,1) # Bytes to GB
disk_info = str(disk.percent) + '%' + ' of ' + str(disk_tot) + 'GB'

print("IP:      ", ip)
print("CPU:     ", cpu_info)
print("RAM:     ", mem_info)
print("SD Card: ", disk_info)

### Docker ###

DOCKER_CLIENT = docker.DockerClient(base_url='unix://var/run/docker.sock')

def get_state(container_name):
    container = DOCKER_CLIENT.containers.get(container_name)
    return container.attrs['State']['Status']

containers = ["portainer", "Plex", "Samba"]
for container in containers:
  print(f'{container.capitalize()+':': <10}{get_state(container).capitalize()}')

# Services

button_status = subprocess.call("systemctl is-active pi_button_shutdown.service", capture_output=True, text=True)
print(button_status)
#print(f'Button:   {button_status.capitalize()}')

