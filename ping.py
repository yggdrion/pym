import threading
from ping3 import ping
import time
import yaml
from src import influx

def ping_ip(ip, name):

    try:
        response_time = ping(ip, timeout=0.2)
    except Exception as e:
        print("Error: Ping")
        print(e)
        response_time = 0.2

    response_time = float(response_time)
    measurement = 'ping' 
    tags = {'name': name}
    fields = {'response_time': response_time}

    influx.write(measurement, tags, fields)

with open('ping.yml', 'r') as file:
    yaml_data = yaml.safe_load(file)

devices = yaml_data['devices']

while True:
    
    print("Ping: Thread")
    threads = []
    for device in devices:
        name = device['name']
        ip = device['ip']
        thread = threading.Thread(target=ping_ip, args=(ip, name))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()
        
    time.sleep(3)
