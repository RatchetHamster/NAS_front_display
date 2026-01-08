import psutil
from subprocess import check_output

print(check_output(['hostname', '-I']))

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

print("CPU:     ", cpu_info)
print("RAM:     ", mem_info)
print("SD Card: ", disk_info)
