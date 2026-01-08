import psutil

cpu = str(psutil.cpu_percent()) + '%'

# Calculate memory information
memory = psutil.virtual_memory()
# Convert Bytes to GB (Bytes -> KB -> MB -> GB)
mem_tot = round(memory.total/1024.0/1024.0/1024.0,1)
mem_info = str(memory.percent) + '%' + ' of ' + str(mem_tot) + 'GB'

# Calculate disk information
disk = psutil.disk_usage('/')
# Convert Bytes to GB (Bytes -> KB -> MB -> GB)
disk_tot = round(disk.total/1024.0/1024.0/1024.0,1)
disk_used = round(disk_tot - disk.free/1024.0/1024.0/1024.0,1)
disk_info = str(disk.percent) + '%' + ' of ' + str(disk_tot) + 'GB'

print("CPU:     ", cpu)
print("RAM:     ", mem_info)
print("SD Card: ", disk_info)
